"""Score run records: steps, errors, wrong-parser attempts, field correctness.

Reads the per-run JSON written by run.py and emits one metrics row per run.
Correctness is judged against the frozen reference answer (built from the winning
parser) with numeric tolerance and order-insensitive comparison of atom lists.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
from typing import Any, Dict, List, Optional

from agent_study.target_schema import ALL_FIELDS, CORE_FIELDS, get_field

REL_TOL = 1e-3
ABS_TOL = 1e-4

# MCP parse-tool name -> parser key (for wrong-parser detection).
TOOL_TO_PARSER = {
    "mcp__parse_patrol__cclib_parse_file_to_model": "cclib",
    "mcp__parse_patrol__gauss_parse_file_to_model": "gaussian",
    "mcp__parse_patrol__iodata_parse_file_to_model": "iodata",
    "mcp__parse_patrol__ase_parse_file_to_model": "ase",
}
# direct-import call detection inside Bash commands
_IMPORT_PARSER_RE = re.compile(r"\b(cclib|gaussian|iodata|ase)_parse\b")


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= max(REL_TOL * max(abs(a), abs(b)), ABS_TOL)


def _list_close(a: List[float], b: List[float]) -> bool:
    if not isinstance(a, list) or not isinstance(b, list) or len(a) != len(b):
        return False
    try:
        sa, sb = sorted(float(x) for x in a), sorted(float(x) for x in b)
    except (TypeError, ValueError):
        return a == b
    return all(_close(x, y) for x, y in zip(sa, sb))


def _coords_close(a: Any, b: Any) -> bool:
    if not (isinstance(a, list) and isinstance(b, list) and len(a) == len(b)):
        return False

    def key(row):
        return tuple(round(float(c), 3) for c in row)

    try:
        sa, sb = sorted(a, key=key), sorted(b, key=key)
        return all(len(r1) == len(r2) and all(_close(float(x), float(y)) for x, y in zip(r1, r2))
                   for r1, r2 in zip(sa, sb))
    except (TypeError, ValueError):
        return False


def _field_correct(field: str, ref: Any, prod: Any) -> bool:
    if prod is None:
        return False
    if field == "geometry.coords":
        return _coords_close(ref, prod)
    if field in ("geometry.elements",):
        return isinstance(prod, list) and sorted(map(str, prod)) == sorted(map(str, ref))
    if field in ("geometry.atomic_numbers",):
        return isinstance(prod, list) and sorted(prod) == sorted(ref)
    if field in ("vibrational.frequencies_cm1", "vibrational.ir_intensities", "charges.mulliken"):
        return _list_close(ref, prod)
    if field == "metadata.program":
        return str(prod).strip().lower() == str(ref).strip().lower()
    if field == "metadata.formula":
        return str(prod).strip() == str(ref).strip()
    if isinstance(ref, (int, float)) and isinstance(prod, (int, float)):
        return _close(float(ref), float(prod))
    return ref == prod


def score_fields(reference: Dict[str, Any], produced: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    produced = produced or {}
    extractable = [f for f in ALL_FIELDS if get_field(reference, f) is not None]
    correct = [f for f in extractable if _field_correct(f, get_field(reference, f), get_field(produced, f))]
    produced_fields = [f for f in ALL_FIELDS if get_field(produced, f) is not None]
    # A produced field is *verifiable* only if the (union) reference also has it.
    # Fields the reference lacks are "unverified extra" — a parser may simply have
    # missed them; without ground truth we neither credit nor penalise them (they
    # are NOT counted as hallucinations).
    verifiable = [f for f in produced_fields if f in extractable]
    extra_unverified = [f for f in produced_fields if f not in extractable]
    core_needed = [f for f in CORE_FIELDS if get_field(reference, f) is not None]
    core_ok = all(f in correct for f in core_needed)
    return {
        "n_extractable": len(extractable),
        "n_correct": len(correct),
        "recall": len(correct) / len(extractable) if extractable else 0.0,
        "precision": len(correct) / len(verifiable) if verifiable else 0.0,
        "n_extra_unverified": len(extra_unverified),
        "success": int(bool(core_needed) and core_ok),
    }


def _tool_uses(transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [b for m in transcript for b in m.get("blocks", []) if b.get("block") == "ToolUseBlock"]


def _tool_errors(transcript: List[Dict[str, Any]]) -> int:
    n = 0
    for m in transcript:
        for b in m.get("blocks", []):
            if b.get("block") == "ToolResultBlock":
                if b.get("is_error") or ("error" in str(b.get("content", "")).lower()):
                    n += 1
    return n


def analyze_run(record: Dict[str, Any]) -> Dict[str, Any]:
    transcript = record.get("transcript", [])
    tool_uses = _tool_uses(transcript)
    parser_success = record.get("parser_success", {})

    wrong_parser = 0
    parsers_used = set()
    bash_calls = 0
    for t in tool_uses:
        name = t.get("name", "")
        if name in TOOL_TO_PARSER:
            p = TOOL_TO_PARSER[name]
            parsers_used.add(p)
            if not parser_success.get(p, False):
                wrong_parser += 1
        elif name == "Bash":
            bash_calls += 1
            cmd = json.dumps(t.get("input", ""))
            for p in _IMPORT_PARSER_RE.findall(cmd):
                parsers_used.add(p)
                if not parser_success.get(p, False):
                    wrong_parser += 1

    result_msg: Dict[str, Any] = next(
        (m for m in transcript if m.get("message") == "ResultMessage"), {})
    fields = score_fields(record.get("reference", {}), record.get("produced"))

    # self-consistency: n_atoms == len(coords) == len(elements) (reference-free;
    # the main signal for hard tasks where no full reference exists)
    prod = record.get("produced") or {}
    n = get_field(prod, "metadata.n_atoms")
    coords = get_field(prod, "geometry.coords")
    elements = get_field(prod, "geometry.elements")
    lens = {len(x) for x in (coords, elements) if isinstance(x, list)}
    if isinstance(n, int):
        lens.add(n)
    self_consistent = int(bool(coords) and len(lens) == 1)

    return {
        "run_id": record["run_id"],
        "task_id": record["task_id"],
        "program": record["program"],
        "tier": record.get("tier", "easy"),
        "format_level": record.get("format_level", ""),
        "arm": record["arm"],
        "repeat": record["repeat"],
        "produced_nonempty": int(bool(prod)),
        "self_consistent": self_consistent,
        # effort
        "n_tool_calls": len(tool_uses),
        "n_parsers_tried": len(parsers_used),
        "n_bash": bash_calls,
        "n_turns": sum(1 for m in transcript if m.get("message") == "AssistantMessage"),
        "cost_usd": result_msg.get("total_cost_usd"),
        # errors
        "n_tool_errors": _tool_errors(transcript),
        "n_wrong_parser": wrong_parser,
        # outcome
        **fields,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--runs-dir", default="agent_study/runs")
    ap.add_argument("--out", default="agent_study/metrics.csv")
    args = ap.parse_args()

    rows: List[Dict[str, Any]] = []
    for path in sorted(glob.glob(os.path.join(args.runs_dir, "*.json"))):
        if path.endswith(".output.json"):
            continue
        with open(path) as f:
            rows.append(analyze_run(json.load(f)))

    if not rows:
        print(f"No run records in {args.runs_dir}")
        return
    fieldnames = list(rows[0].keys())
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {args.out}: {len(rows)} run metrics.")


if __name__ == "__main__":
    main()
