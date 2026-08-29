"""Aggregate metrics.csv + failure_modes.csv into a per-arm report.md.

Headline comparison: does more scaffold (BARE -> DOCS -> FULL) reduce steps and
errors and shift the agent's failure-mode distribution?
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import Counter, defaultdict
from statistics import mean, pstdev
from typing import Dict, List

from agent_study.arms import ARMS
from agent_study.failure_modes import MODES


def _load(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def _num(rows: List[dict], key: str) -> List[float]:
    out = []
    for r in rows:
        v = r.get(key, "")
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            pass
    return out


def _cell(vals: List[float]) -> str:
    if not vals:
        return "n/a"
    return f"{mean(vals):.2f} ± {pstdev(vals):.2f}" if len(vals) > 1 else f"{mean(vals):.2f}"


def build(metrics: List[dict], failures: List[dict]) -> str:
    arms = [a for a in ARMS if any(r["arm"] == a for r in metrics)]
    by_arm: Dict[str, List[dict]] = defaultdict(list)
    for r in metrics:
        by_arm[r["arm"]].append(r)
    fail_by_arm: Dict[str, Counter] = defaultdict(Counter)
    n_runs_arm: Counter = Counter()
    for r in failures:
        n_runs_arm[r["arm"]] += 1
        for lab in filter(None, r.get("labels", "").split(";")):
            fail_by_arm[r["arm"]][lab] += 1

    def tier_rows(a: str, tier: str) -> List[dict]:
        return [r for r in by_arm[a] if r.get("tier", "easy") == tier]

    L: List[str] = []
    add = L.append
    add("# Agent Scaffold Study — Report")
    add("")
    add("Does a capability scaffold reduce a coding agent's steps and errors when "
        "converting chemistry files into a target schema? Arms: **BARE** (tools only) "
        "→ **DOCS** (+docs) → **FULL** (+capability map) → **COMPLEXITY** (+format "
        "level, tool-power ceilings, escalation rule). Tasks split into **easy** "
        "(≥1 parser works; field-scored) and **hard** (no parser works; the "
        "discriminating regime, scored on behaviour + self-consistency).")
    add("")

    has_easy = any(tier_rows(a, "easy") for a in arms)
    has_hard = any(tier_rows(a, "hard") for a in arms)

    if has_easy:
        add("## Easy tier — field-level outcome")
        add("")
        add("| Arm | n | Success | Field recall | Field precision | Tool calls | Wrong-parser | Cost (USD) |")
        add("|---|---|---|---|---|---|---|---|")
        for a in arms:
            rows = tier_rows(a, "easy")
            if not rows:
                continue
            add(f"| {a} | {len(rows)} "
                f"| {_cell(_num(rows,'success'))} "
                f"| {_cell(_num(rows,'recall'))} "
                f"| {_cell(_num(rows,'precision'))} "
                f"| {_cell(_num(rows,'n_tool_calls'))} "
                f"| {_cell(_num(rows,'n_wrong_parser'))} "
                f"| {_cell(_num(rows,'cost_usd'))} |")
        add("")

    if has_hard:
        add("## Hard tier — behaviour (no single parser works)")
        add("")
        add("| Arm | n | Self-consistent | Wrote own parser | Wrong-parser | Tool calls | Cost (USD) |")
        add("|---|---|---|---|---|---|---|")
        for a in arms:
            rows = tier_rows(a, "hard")
            if not rows:
                continue
            add(f"| {a} | {len(rows)} "
                f"| {_cell(_num(rows,'self_consistent'))} "
                f"| {_cell(_num(rows,'n_bash'))} "
                f"| {_cell(_num(rows,'n_wrong_parser'))} "
                f"| {_cell(_num(rows,'n_tool_calls'))} "
                f"| {_cell(_num(rows,'cost_usd'))} |")
        add("")
        add("Hypothesis: on hard tasks COMPLEXITY should cut wrong-parser thrash and "
            "raise correct write-from-scratch (self-consistent output) vs BARE.")
        add("")

    add("## Agent failure modes by arm")
    add("")
    add("Share of runs exhibiting each mode (a run may show several).")
    add("")
    add("| Mode | " + " | ".join(arms) + " |")
    add("|---|" + "---|" * len(arms))
    for mode in MODES:
        cells = []
        for a in arms:
            n = n_runs_arm[a] or 1
            cells.append(f"{100*fail_by_arm[a][mode]/n:.0f}% ({fail_by_arm[a][mode]}/{n_runs_arm[a]})")
        add(f"| {mode} | " + " | ".join(cells) + " |")
    add("")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--metrics", default="agent_study/metrics.csv")
    ap.add_argument("--failures", default="agent_study/failure_modes.csv")
    ap.add_argument("--out", default="agent_study/report.md")
    args = ap.parse_args()

    metrics, failures = _load(args.metrics), _load(args.failures)
    if not metrics:
        print(f"No metrics in {args.metrics} — run metrics.py first.")
        return
    with open(args.out, "w") as f:
        f.write(build(metrics, failures))
    print(f"Wrote {args.out} from {len(metrics)} runs.")


if __name__ == "__main__":
    main()
