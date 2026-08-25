"""Freeze the benchmark corpus into a reproducible ``dataset.json`` manifest.

This is the *only* step that touches the network. It reads the locally-cached
NOMAD raw files (default ``tests/.data``), asks NOMAD once for the authoritative
metadata of every cached entry (program name, version, formula and, crucially,
the ``mainfile`` NOMAD itself designates as the primary parseable file), scopes
the on-disk raw files to that entry, and writes a frozen manifest.

Downstream (``run.py``) reads only ``dataset.json`` and the files on disk, so the
actual benchmark is deterministic and offline.

Usage:
    python -m benchmarks.dataset --data-root tests/.data --out benchmarks/dataset.json
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, List, Optional

import requests

NOMAD_QUERY_URL = "https://nomad-lab.eu/prod/v1/api/v1/entries/query"


def _list_entry_dirs(data_root: str) -> List[str]:
    return sorted(
        d
        for d in os.listdir(data_root)
        if os.path.isdir(os.path.join(data_root, d)) and not d.startswith(".")
    )


def fetch_nomad_metadata(entry_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """Return {entry_id: {program_name, program_version, formula, mainfile}}.

    A single batched NOMAD query. Entries NOMAD no longer serves are simply
    absent from the result (the caller records them with ``None`` metadata).
    """
    body = {
        "owner": "visible",
        "query": {"entry_id:any": entry_ids},
        "pagination": {"page_size": len(entry_ids)},
        "required": {
            "include": [
                "entry_id",
                "upload_id",
                "mainfile",
                "results.method.simulation.program_name",
                "results.method.simulation.program_version",
                "results.material.chemical_formula_reduced",
            ]
        },
    }
    resp = requests.post(NOMAD_QUERY_URL, json=body, timeout=120)
    if resp.status_code != 200:
        raise RuntimeError(f"NOMAD query failed: HTTP {resp.status_code}")

    out: Dict[str, Dict[str, Any]] = {}
    for item in resp.json().get("data", []):
        sim = (item.get("results", {}).get("method", {}) or {}).get("simulation", {}) or {}
        material = item.get("results", {}).get("material", {}) or {}
        out[item.get("entry_id", "")] = {
            "upload_id": item.get("upload_id"),
            "mainfile": item.get("mainfile"),
            "program_name": sim.get("program_name"),
            "program_version": sim.get("program_version"),
            "formula": material.get("chemical_formula_reduced"),
        }
    return out


def _scope_files(entry_dir: str, mainfile: Optional[str]) -> tuple[List[str], Optional[str]]:
    """Return (raw files relative to ``entry_dir``, on-disk mainfile path).

    On disk, NOMAD raw files are extracted under a single upload directory (a
    hash), and NOMAD's ``mainfile`` is relative to *that* directory, i.e. the
    real path is ``<upload_dir>/<mainfile>``. We therefore scope to the entry's
    top-level subdirectories only: this captures every genuine raw file while
    excluding ``manifest.json`` and any stray, agent-generated analysis
    artifacts that sit loose at the entry root.
    """
    subdirs = [
        d for d in sorted(os.listdir(entry_dir)) if os.path.isdir(os.path.join(entry_dir, d))
    ]

    files: List[str] = []
    for sub in subdirs:
        for root, _dirs, names in os.walk(os.path.join(entry_dir, sub)):
            for name in names:
                if name.endswith("_raw.zip"):
                    continue
                files.append(os.path.relpath(os.path.join(root, name), entry_dir))
    files.sort()

    mainfile_ondisk = None
    if mainfile:
        for sub in subdirs:
            candidate = os.path.join(sub, mainfile)
            if os.path.exists(os.path.join(entry_dir, candidate)):
                mainfile_ondisk = candidate
                break
    return files, mainfile_ondisk


def build_dataset(data_root: str) -> Dict[str, Any]:
    entry_ids = _list_entry_dirs(data_root)
    meta = fetch_nomad_metadata(entry_ids)

    entries: List[Dict[str, Any]] = []
    unresolved_scope: List[str] = []
    dropped_empty: List[str] = []
    for entry_id in entry_ids:
        entry_dir = os.path.join(data_root, entry_id)
        m = meta.get(entry_id, {})
        mainfile = m.get("mainfile")
        files, mainfile_ondisk = _scope_files(entry_dir, mainfile)

        # Drop entries whose raw files never downloaded (empty on disk): they
        # would otherwise inflate the program count with no data behind them.
        if not files:
            dropped_empty.append(entry_id)
            continue

        # Sanity flag: could we locate the designated mainfile on disk?
        if mainfile and mainfile_ondisk is None:
            unresolved_scope.append(entry_id)

        entries.append(
            {
                "entry_id": entry_id,
                "program_name": m.get("program_name"),
                "program_version": m.get("program_version"),
                "formula": m.get("formula"),
                "upload_id": m.get("upload_id"),
                "mainfile": mainfile,
                "mainfile_ondisk": mainfile_ondisk,
                "files": files,
            }
        )

    return {
        "data_root": data_root,
        "n_entries": len(entries),
        "n_files": sum(len(e["files"]) for e in entries),
        "n_programs": len({e["program_name"] for e in entries if e["program_name"]}),
        "unresolved_scope": unresolved_scope,
        "dropped_empty": dropped_empty,
        "entries": entries,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-root", default="tests/.data")
    ap.add_argument("--out", default="benchmarks/dataset.json")
    args = ap.parse_args()

    dataset = build_dataset(args.data_root)
    with open(args.out, "w") as f:
        json.dump(dataset, f, indent=2)

    print(
        f"Wrote {args.out}: {dataset['n_entries']} entries, "
        f"{dataset['n_files']} files, {dataset['n_programs']} programs."
    )
    if dataset["unresolved_scope"]:
        print(
            f"WARNING: mainfile not found on disk for "
            f"{len(dataset['unresolved_scope'])} entries: {dataset['unresolved_scope']}"
        )


if __name__ == "__main__":
    main()
