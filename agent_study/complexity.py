"""Format-complexity rubric (Chomsky-hierarchy-inspired) + benchmark re-cut.

Assigns each source file a coarse ordinal ``format_level`` (L0-L3) reflecting the
grammatical complexity extraction demands, then re-cuts the parser-reliability
benchmark (``benchmarks/results.csv``) by that level to test the *power-gap
hypothesis*: fixed-parser success should fall as format level rises, and structured
(L0) formats should be handled far more reliably than free-form logs (L2-L3).

See ``paper/complexity_framing.md`` for the full framing and the rubric rationale.
This is a coarse, documented ordinal — not a formal per-file classification.

Levels:
  L0  grammar-defined / structured (XML, JSON, .fchk, .molden, vasprun.xml) -> context-free
  L1  line-regular structure/input (.xyz, .gjf/.com, POSCAR-as-plain)       -> regular
  L2  free-form output log with block + count-agreement (.out/.log/.OUT ...) -> mildly context-sensitive
  L3  cross-referential / multi-file (WIEN2k struct+scf, exciting split)     -> context-sensitive

Usage:
    python -m agent_study.complexity --results benchmarks/results.csv \
        --out agent_study/complexity_report.md
"""

from __future__ import annotations

import argparse
import csv
import os
from collections import defaultdict
from typing import Dict, List

LEVELS = ["L0", "L1", "L2", "L3"]

_L0_EXT = {".xml", ".json", ".fchk", ".molden", ".hdf5", ".h5"}
_L1_EXT = {".xyz", ".gjf", ".com", ".cif", ".gen"}
_L1_BASENAMES = {"POSCAR", "CONTCAR"}
# programs whose primary results are split across cross-referencing files
_L3_PROGRAMS = {"WIEN2k"}


def format_level(program: str, filename: str) -> str:
    """Coarse L0-L3 level for a source file (see module docstring for the rubric)."""
    base = os.path.basename(filename)
    ext = os.path.splitext(base)[1].lower()

    if "vasprun" in base.lower() or ext in _L0_EXT:
        return "L0"
    if (program or "") in _L3_PROGRAMS:
        return "L3"
    if ext in _L1_EXT or base in _L1_BASENAMES:
        return "L1"
    # default: free-form simulation output log (count-agreement, take-last blocks)
    return "L2"


def _pct(num: int, den: int) -> str:
    return f"{100.0 * num / den:.1f}% ({num}/{den})" if den else "n/a"


def recut(results_csv: str) -> str:
    with open(results_csv) as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["level"] = format_level(r["program"], r["file"])

    parsers = sorted({r["parser"] for r in rows})

    # success rate by level x parser (mainfile only, then all files)
    def table(mainfile_only: bool) -> List[str]:
        succ: Dict[tuple, int] = defaultdict(int)
        tot: Dict[tuple, int] = defaultdict(int)
        for r in rows:
            if mainfile_only and r["is_mainfile"] != "1":
                continue
            key = (r["level"], r["parser"])
            tot[key] += 1
            succ[key] += r["outcome"] == "success"
        out = ["| Level | " + " | ".join(parsers) + " | files |",
               "|---|" + "---|" * (len(parsers) + 1)]
        for lvl in LEVELS:
            nfiles = sum(tot[(lvl, p)] for p in parsers) // max(1, len(parsers))
            cells = [_pct(succ[(lvl, p)], tot[(lvl, p)]) for p in parsers]
            if any(tot[(lvl, p)] for p in parsers):
                out.append(f"| {lvl} | " + " | ".join(cells) + f" | {nfiles} |")
        return out

    # oracle (any parser) by level
    by_file: Dict[tuple, Dict[str, str]] = defaultdict(dict)
    level_of: Dict[tuple, str] = {}
    mainfiles = set()
    for r in rows:
        k = (r["entry_id"], r["file"])
        by_file[k][r["parser"]] = r["outcome"]
        level_of[k] = r["level"]
        if r["is_mainfile"] == "1":
            mainfiles.add(k)
    orc_s: Dict[str, int] = defaultdict(int)
    orc_t: Dict[str, int] = defaultdict(int)
    for k in mainfiles:
        lvl = level_of[k]
        orc_t[lvl] += 1
        orc_s[lvl] += any(o == "success" for o in by_file[k].values())

    L: List[str] = []
    add = L.append
    add("# Benchmark re-cut by format complexity (power-gap test)")
    add("")
    add("Parser success rate grouped by `format_level` (L0 structured → L3 "
        "cross-referential). Prediction: success falls as level rises, and "
        "structured L0 formats are handled far more reliably than free-form logs. "
        "Rubric: `agent_study/complexity.py`; framing: `paper/complexity_framing.md`.")
    add("")
    add("## Mainfile success by level × parser")
    add("")
    L += table(mainfile_only=True)
    add("")
    add("## Oracle (any parser succeeds) by level — mainfiles")
    add("")
    add("| Level | Solved by ≥1 parser |")
    add("|---|---|")
    for lvl in LEVELS:
        if orc_t[lvl]:
            add(f"| {lvl} | {_pct(orc_s[lvl], orc_t[lvl])} |")
    add("")
    add("## All-files success by level × parser")
    add("")
    L += table(mainfile_only=False)
    add("")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--results", default="benchmarks/results.csv")
    ap.add_argument("--out", default="agent_study/complexity_report.md")
    args = ap.parse_args()
    report = recut(args.results)
    with open(args.out, "w") as f:
        f.write(report)
    print(f"Wrote {args.out}")
    print(report)


if __name__ == "__main__":
    main()
