"""Label each run with agent failure modes (automatic detectors).

The taxonomy is the negative-results contribution: the scaffold's value shows up
as a shift in *which* failure modes occur, not just aggregate success. Detectors
are deliberately conservative and transcript-grounded; ambiguous cases can be sent
to an LLM judge later (hook left below, off by default to avoid extra API cost).

Modes:
  wrong_parser        called a parser that cannot handle this program
  silent_empty        emitted output despite a parser that returns no structure
  parser_from_scratch wrote its own parsing code instead of using the tools
  hallucinated_field  produced a field the source/parsers do not support
  unit_error          right quantity, wrong unit (energy ~x27.21, coords ~x1.889)
  retry_loop          called the same tool on the same input >= 3 times
  gave_up             failed to produce the required core fields
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
from collections import Counter, defaultdict
from typing import Any, Dict, List

from agent_study.metrics import (
    TOOL_TO_PARSER, _tool_uses, analyze_run, _close,
)
from agent_study.target_schema import EV_PER_HARTREE, ANGSTROM_PER_BOHR, get_field

MODES = [
    "wrong_parser", "silent_empty", "parser_from_scratch",
    "unit_error", "retry_loop", "gave_up",
]

_SCRATCH_MARKERS = ("re.compile", "readlines", ".read()", "def parse", "for line in", "splitlines")


def _wrote_own_parser(record: Dict[str, Any]) -> bool:
    for m in record.get("transcript", []):
        for b in m.get("blocks", []):
            if b.get("block") != "ToolUseBlock" or b.get("name") not in ("Write", "Bash"):
                continue
            blob = json.dumps(b.get("input", "")).lower()
            uses_tool = "parse_patrol" in blob or "_parse(" in blob
            if any(mk in blob for mk in _SCRATCH_MARKERS) and not uses_tool:
                return True
    return False


def _unit_error(record: Dict[str, Any]) -> bool:
    ref, prod = record.get("reference", {}), record.get("produced") or {}
    # energy: eV vs Hartree
    r_e, p_e = get_field(ref, "energetics.scf_energy"), get_field(prod, "energetics.scf_energy")
    if isinstance(r_e, (int, float)) and isinstance(p_e, (int, float)) and r_e and not _close(r_e, p_e):
        ratio = abs(p_e / r_e) if r_e else 0
        if _close(ratio, EV_PER_HARTREE) or _close(ratio, 1 / EV_PER_HARTREE):
            return True
    # coords: Bohr vs Angstrom (compare first atom's norm)
    r_c, p_c = get_field(ref, "geometry.coords"), get_field(prod, "geometry.coords")
    if isinstance(r_c, list) and isinstance(p_c, list) and r_c and p_c and len(r_c) == len(p_c):
        try:
            rn = sum(abs(c) for c in r_c[0]) or 1e-9
            pn = sum(abs(c) for c in p_c[0])
            ratio = pn / rn
            if _close(ratio, 1 / ANGSTROM_PER_BOHR) or _close(ratio, ANGSTROM_PER_BOHR):
                return True
        except (TypeError, ValueError, IndexError):
            pass
    return False


def _retry_loop(record: Dict[str, Any]) -> bool:
    seen: Counter = Counter()
    for t in _tool_uses(record.get("transcript", [])):
        key = (t.get("name"), json.dumps(t.get("input", ""), sort_keys=True))
        seen[key] += 1
    return any(c >= 3 for c in seen.values())


def label_run(record: Dict[str, Any]) -> List[str]:
    m = analyze_run(record)
    labels: List[str] = []
    if m["n_wrong_parser"] > 0:
        labels.append("wrong_parser")
    # silent_empty: produced output while (only) a failing parser was used
    used = {TOOL_TO_PARSER[t["name"]] for t in _tool_uses(record.get("transcript", []))
            if t.get("name") in TOOL_TO_PARSER}
    ps = record.get("parser_success", {})
    if record.get("produced") and used and not any(ps.get(p) for p in used):
        labels.append("silent_empty")
    if _wrote_own_parser(record):
        labels.append("parser_from_scratch")
    if _unit_error(record):
        labels.append("unit_error")
    if _retry_loop(record):
        labels.append("retry_loop")
    if not m["success"]:
        labels.append("gave_up")
    return labels


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs-dir", default="agent_study/runs")
    ap.add_argument("--out", default="agent_study/failure_modes.csv")
    args = ap.parse_args()

    rows: List[Dict[str, Any]] = []
    per_arm: Dict[str, Counter] = defaultdict(Counter)
    for path in sorted(glob.glob(os.path.join(args.runs_dir, "*.json"))):
        if path.endswith(".output.json"):
            continue
        with open(path) as f:
            record = json.load(f)
        labels = label_run(record)
        rows.append({"run_id": record["run_id"], "arm": record["arm"],
                     "task_id": record["task_id"], "labels": ";".join(labels)})
        for lab in labels:
            per_arm[record["arm"]][lab] += 1

    if not rows:
        print(f"No run records in {args.runs_dir}")
        return
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["run_id", "arm", "task_id", "labels"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {args.out}: {len(rows)} runs labeled.")
    for arm, counts in sorted(per_arm.items()):
        print(f"  {arm}: {dict(counts)}")


if __name__ == "__main__":
    main()
