# Parser Reliability Benchmark

A reproducible benchmark measuring how reliably the community parsers wrapped by
parse-patrol (ASE, cclib, the custom Gaussian parser, iodata) extract structured
data from **real** computational-chemistry files harvested from the
[NOMAD](https://nomad-lab.eu) repository.

Agentic molecular-science systems treat these parsers as tools they can call
blindly. This benchmark asks a simple question: *when you point them at real,
heterogeneous data, how often do they actually work?*

## Headline result

On the single file NOMAD itself designates as each entry's primary output
("mainfile"), no individual parser exceeds **~24%** success, and an *oracle*
that picks the best parser per file still solves only **45%** — on the other
55% **no parser succeeds at all**. The parsers that do succeed are largely
disjoint by domain (ASE for materials/structure codes; cclib/iodata for
molecular quantum chemistry), so a router is necessary but far from sufficient.

See [`report.md`](report.md) for the full tables.

## Method

* **Corpus.** 52 NOMAD entries spanning 16 simulation codes (VASP, Gaussian,
  ORCA, GAMESS, exciting, CASTEP, …), 1104 raw files, cached under `tests/.data`
  and frozen into [`dataset.json`](dataset.json).
* **Two denominators.**
  * *All files* — every file in the upload (the naive "point the parser at
    everything" scenario).
  * *Mainfile only* — the single primary output file NOMAD designates per entry.
    An authoritative, non-arbitrary eligible set.
* **Field-level success.** Because every parser model uses `Optional` fields, a
  parser can "succeed" (no exception) yet return a structureless shell. Success
  is therefore defined as *actually extracting an atomic structure* (atoms +
  coordinates); extracting an energy is tracked as a stricter secondary bar.
  See [`success.py`](success.py).
* **Outcomes.** `success` / `empty` (silent failure — no exception, no data) /
  `error` (exception, type recorded) / `timeout`.

The parsers are never modified: their failures are the measurement.

## Reproduce

```bash
# 1. Freeze the corpus (the ONLY networked step; needs the cached tests/.data).
uv run python -m benchmarks.dataset --data-root tests/.data --out benchmarks/dataset.json

# 2. Run every parser over every file (offline; ~a few minutes on 8 cores).
uv run python -m benchmarks.run --dataset benchmarks/dataset.json \
    --data-root tests/.data --out benchmarks/results.csv

# 3. Aggregate into the report.
uv run python -m benchmarks.report --results benchmarks/results.csv --out benchmarks/report.md
```

Step 2 is deterministic given a fixed `dataset.json` and the files on disk. Some
parsers hang inside C extensions on pathological inputs; the runner isolates each
attempt in a worker process and kills+respawns on a hard per-file timeout, so a
single bad file is recorded as `timeout` rather than stalling the run.

## Files

| File | Role |
|---|---|
| `dataset.py` | Freezes the corpus into `dataset.json` (queries NOMAD once for program/mainfile metadata). |
| `success.py` | Field-level success criteria per parser. |
| `run.py` | Manager-pool harness; produces `results.csv`. |
| `report.py` | Aggregates `results.csv` into `report.md`. |
| `dataset.json` | Frozen corpus manifest (reproducibility). |
| `results.csv` | One row per parser × file attempt. |
| `report.md` | Generated human-readable report. |
