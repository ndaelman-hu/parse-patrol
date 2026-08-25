"""Run every parser over every file in the frozen corpus -> ``results.csv``.

Fully offline: reads ``dataset.json`` and the raw files on disk, imports the
four parser entry points, and attempts to parse each file with each parser.
Every attempt is classified as:

* ``success``  -- no exception AND a structure was extracted (see success.py)
* ``empty``    -- no exception BUT the returned model has no structure
                  (a *silent* failure: the agent gets a near-empty object back)
* ``error``    -- the parser raised an exception (type recorded)
* ``timeout``  -- the parser exceeded the wall-clock budget (some parsers hang
                  inside C extensions, where an in-process signal cannot preempt
                  them; those are killed and respawned by the manager)

Each row also records whether the file is the NOMAD-designated ``mainfile``,
which yields the rigorous "eligible files only" denominator downstream.

A manager drives a pool of persistent worker processes, one task in flight per
worker. If a worker exceeds the hard per-task budget (e.g. a native hang), the
manager kills and respawns *only that worker* and records the single offending
file as a timeout -- so one pathological file never stalls the rest of the run.
Results are streamed to ``results.csv`` as they arrive. Parser stdout/stderr is
redirected at the fd level because some parsers log past Python's ``sys.stderr``.

Usage:
    python -m benchmarks.run --dataset benchmarks/dataset.json \
        --data-root tests/.data --out benchmarks/results.csv
"""

from __future__ import annotations

import argparse
import csv
import importlib
import json
import multiprocessing as mp
import os
import signal
import sys
import time
import warnings
from multiprocessing.connection import Connection, wait
from typing import Any, Callable, Dict, List, Optional, Tuple, cast

from benchmarks.success import Verdict, evaluate

PARSERS: Dict[str, Tuple[str, str]] = {
    "ase": ("parse_patrol.parsers.ase.utils", "ase_parse"),
    "cclib": ("parse_patrol.parsers.cclib.utils", "cclib_parse"),
    "gaussian": ("parse_patrol.parsers.gaussian.utils", "gaussian_parse"),
    "iodata": ("parse_patrol.parsers.iodata.utils", "iodata_parse"),
}

DEFAULT_SOFT_TIMEOUT_S = 20   # in-worker SIGALRM (bounds slow pure-Python parses)
DEFAULT_HARD_TIMEOUT_S = 45   # manager kills a worker stuck past this (native hangs)

FIELDNAMES = [
    "parser", "entry_id", "program", "file", "is_mainfile",
    "outcome", "exception_type", "has_structure", "has_energy",
]


def _load_parsers() -> Dict[str, Callable[[str], Any]]:
    return {
        name: getattr(importlib.import_module(mod), fn)
        for name, (mod, fn) in PARSERS.items()
    }


def _attempt(fn: Callable[[str], Any], parser: str, path: str, soft_timeout: int):
    """Return (outcome, exception_type, Verdict) for one parse attempt."""
    signal.alarm(soft_timeout)
    try:
        model = fn(path)
        verdict = evaluate(parser, model)
        return ("success" if verdict.success else "empty"), "", verdict
    except TimeoutError:
        return "timeout", "TimeoutError", Verdict(False, False)
    except BaseException as exc:  # parsers raise a wide, undocumented range
        return "error", type(exc).__name__, Verdict(False, False)
    finally:
        signal.alarm(0)


def _worker_loop(conn: Connection, soft_timeout: int) -> None:
    """Persistent worker: receive (parser, abspath), send back an outcome tuple."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 1)
    os.dup2(devnull, 2)
    warnings.simplefilter("ignore")

    def _handler(signum: int, frame: Any) -> None:
        raise TimeoutError("soft timeout")

    signal.signal(signal.SIGALRM, _handler)
    fns = _load_parsers()
    conn.send("READY")
    while True:
        msg = conn.recv()
        if msg is None:
            break
        parser, path = msg
        outcome, exc_type, verdict = _attempt(fns[parser], parser, path, soft_timeout)
        conn.send((outcome, exc_type, int(verdict.has_structure), int(verdict.has_energy)))


class _Worker:
    def __init__(self, ctx: Any, soft_timeout: int) -> None:
        self.ctx = ctx
        self.soft_timeout = soft_timeout
        self.task: Optional[dict] = None
        self.deadline = 0.0
        self._spawn()

    def _spawn(self) -> None:
        self.parent_conn, child_conn = self.ctx.Pipe()
        self.proc = self.ctx.Process(target=_worker_loop, args=(child_conn, self.soft_timeout))
        self.proc.start()
        child_conn.close()
        assert self.parent_conn.recv() == "READY"

    def assign(self, task: dict, path: str, hard_timeout: int) -> None:
        self.task = task
        self.deadline = time.monotonic() + hard_timeout
        self.parent_conn.send((task["parser"], path))

    def respawn(self) -> None:
        self.proc.kill()
        self.proc.join()
        self.parent_conn.close()
        self.task = None
        self._spawn()

    def stop(self) -> None:
        try:
            self.parent_conn.send(None)
        except (BrokenPipeError, OSError):
            pass
        self.proc.join(timeout=5)
        if self.proc.is_alive():
            self.proc.kill()
            self.proc.join()


def _build_tasks(dataset: dict) -> List[dict]:
    tasks: List[dict] = []
    for parser in PARSERS:
        for entry in dataset["entries"]:
            mainfile = entry.get("mainfile_ondisk")
            for rel in entry["files"]:
                tasks.append({
                    "parser": parser,
                    "entry_id": entry["entry_id"],
                    "program": entry["program_name"] or "unknown",
                    "file": rel,
                    "is_mainfile": int(rel == mainfile),
                })
    return tasks


def run(dataset_path: str, data_root: str, out_path: str,
        soft_timeout: int, hard_timeout: int, n_workers: int) -> None:
    with open(dataset_path) as f:
        dataset = json.load(f)
    tasks = _build_tasks(dataset)
    pending = list(reversed(tasks))  # pop() from the end

    ctx = mp.get_context("fork")
    workers = [_Worker(ctx, soft_timeout) for _ in range(n_workers)]

    out_file = open(out_path, "w", newline="")
    writer = csv.DictWriter(out_file, fieldnames=FIELDNAMES)
    writer.writeheader()

    done = 0
    total = len(tasks)
    counts: Dict[str, int] = {}

    def _emit(task: dict, outcome: str, exc_type: str, hs: int, he: int) -> None:
        nonlocal done
        writer.writerow({
            **{k: task[k] for k in ("parser", "entry_id", "program", "file", "is_mainfile")},
            "outcome": outcome, "exception_type": exc_type,
            "has_structure": hs, "has_energy": he,
        })
        out_file.flush()
        done += 1
        counts[outcome] = counts.get(outcome, 0) + 1

    def _fill_idle() -> None:
        for w in workers:
            if w.task is None and pending:
                task = pending.pop()
                path = os.path.join(data_root, task["entry_id"], task["file"])
                w.assign(task, path, hard_timeout)

    _fill_idle()
    while any(w.task is not None for w in workers):
        busy = [w for w in workers if w.task is not None]
        by_conn = {w.parent_conn: w for w in busy}
        for conn in wait(list(by_conn), timeout=1.0):
            w = by_conn[cast(Connection, conn)]
            task = w.task
            assert task is not None
            try:
                outcome, exc_type, hs, he = cast(Connection, conn).recv()
            except EOFError:  # worker died mid-task
                _emit(task, "timeout", "WorkerDied", 0, 0)
                w.respawn()
                continue
            _emit(task, outcome, exc_type, hs, he)
            w.task = None
        # hard-timeout sweep: kill+respawn workers stuck in native code
        now = time.monotonic()
        for w in workers:
            if w.task is not None and now > w.deadline:
                _emit(w.task, "timeout", "HardTimeout", 0, 0)
                w.respawn()
        _fill_idle()
        print(f"\r  {done}/{total} attempts", end="", file=sys.stderr, flush=True)

    for w in workers:
        w.stop()
    out_file.close()
    print(file=sys.stderr)

    # Per-parser success summary.
    with open(out_path) as f:
        rows = list(csv.DictReader(f))
    for parser in PARSERS:
        pr = [r for r in rows if r["parser"] == parser]
        succ = sum(r["outcome"] == "success" for r in pr)
        print(f"  {parser:9s}: {succ}/{len(pr)} success (all files)", file=sys.stderr)
    print(f"Wrote {out_path}: {len(rows)} rows. outcomes={counts}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", default="benchmarks/dataset.json")
    ap.add_argument("--data-root", default="tests/.data")
    ap.add_argument("--out", default="benchmarks/results.csv")
    ap.add_argument("--soft-timeout", type=int, default=DEFAULT_SOFT_TIMEOUT_S)
    ap.add_argument("--hard-timeout", type=int, default=DEFAULT_HARD_TIMEOUT_S)
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 4))
    args = ap.parse_args()
    run(args.dataset, args.data_root, args.out, args.soft_timeout,
        args.hard_timeout, args.workers)


if __name__ == "__main__":
    main()
