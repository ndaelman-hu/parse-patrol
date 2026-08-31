# Reproducing the agent-scaffold study

This reproduces the results in the ML4Molecules 2026 paper (tag
`ml4molecules-2026-submission`): the failure-mode figure, the per-arm success/failure
tables, and the scored CSVs.

## 0. Environment

```bash
uv sync                      # install the pinned environment (uv.lock)
```

## 1. Fetch the data (DVC)

Heavy artifacts are **not** in git — they are tracked by DVC and stored on a private
remote (git holds only the tiny `*.dvc` pointers).

```bash
uv run dvc pull              # fetches tests/.data (14 GB fixtures) + agent_study/runs (transcripts)
```

- `tests/.data/`  — 1,163 real simulation-output files across 16 codes (NOMAD snapshot).
- `agent_study/runs/`  — 159 agent run transcripts (+ their `.output.json`).

Requires access to the configured DVC remote (`dvc remote list`). Without it you can still
re-run the sweep from scratch (step 2), which regenerates `agent_study/runs/`.

## 2. (Optional) Re-run the agent sweep

Uses the Claude Agent SDK; drives the local `claude` CLI (no API key needed if logged in).
This is the expensive step; skip it if you pulled `agent_study/runs/` in step 1.

```bash
# all arms, 30-task matched set + NONE baseline, single run per cell
uv run python -m agent_study.run --arms NONE,BARE,DOCS,FULL,COMPLEXITY \
    --repeats 1 --model claude-opus-4-8 --runs-dir agent_study/runs
```

Excluded automatically (infrastructure limits, see paper appendix): the 3 GAMESS tasks
(parsed model exceeds the SDK message buffer) and one ~3.5 GB GPAW output (hangs).

## 3. Score the runs

```bash
uv run python -m agent_study.metrics        --runs-dir agent_study/runs --out agent_study/metrics.csv
uv run python -m agent_study.failure_modes  --runs-dir agent_study/runs --out agent_study/failure_modes.csv
```

`metrics.csv` = per-run effort + correctness; `failure_modes.csv` = per-run failure labels.
The matched-set summary is in `agent_study/results_summary.md`.

## 4. Rebuild the figure

```bash
cd paper/neurips_submission && uv run python make_fig.py   # writes fig_failuremodes.pdf (+ .png)
```

## Provenance

- **Submitted paper:** `git checkout ml4molecules-2026-submission` (clean, DVC-tracked snapshot).
- **Exact bytes at the 13:59 AOE deadline:** commit `952dac5` (tag `as-submitted-raw`, if created),
  and `paper/neurips_submission/ParsePatrol_AgenticFailureModes.pdf`.
- Follow-up experiment plan: `paper/RESEARCH_PLAN.md`.
