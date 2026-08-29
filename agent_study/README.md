# Agent Scaffold Study

Does giving a coding agent a **capability scaffold** reduce the number of steps it
takes and the errors it makes when converting a real computational-chemistry file
into a fixed target schema — and what are its failure modes?

This is a distinct artifact from the parser-reliability benchmark in
[`../benchmarks/`](../benchmarks); it *reuses* that benchmark's `results.csv` as
ground-truth tool×source capability labels and to build reference answers.

## The experiment

A coding agent (Claude Agent SDK) is given a source file and the target JSON
schema, plus the parse-patrol MCP parse tools and built-in Bash/Read/Write (so it
can also `from parse_patrol import cclib_parse`). Three arms — **only the scaffold
text in the system prompt varies, the tool set is constant**:

| Arm | Scaffold given to the agent |
|---|---|
| **BARE** | none — tools only |
| **DOCS** | + each parser's documentation (its supported formats) |
| **FULL** | + the cross-parser capability map (parser × property-group) |

We measure per run: **effort** (tool calls, code executions, turns, cost),
**errors** (tool errors, and *wrong-parser attempts* — calling a parser that
`benchmarks/results.csv` says fails on that program), and **outcome** (field-level
precision/recall + a core-field success flag against the reference). Then we label
each run with **agent failure modes** (wrong parser, silent-empty accepted,
parser-from-scratch, hallucinated field, unit error, retry loop, gave up).

## Prerequisites

* The benchmark must have been built (`benchmarks/results.csv`, `dataset.json`).
* Install the Agent SDK: `uv sync --extra agent-study` (adds `claude-agent-sdk`).
* Authenticate Claude: the SDK drives the local `claude` CLI. If you're logged
  into Claude Code, no `ANTHROPIC_API_KEY` is needed. **Agent runs cost tokens.**

## Run it

```bash
# 1. Freeze tasks (offline; reuses the benchmark). Already produces tasks.json.
uv run python -m agent_study.tasks --out agent_study/tasks.json

# 2. PILOT first (12 runs) to validate the harness before the full sweep:
uv run python -m agent_study.run --limit-tasks 4 --arms BARE,DOCS,FULL --repeats 1

# 3. Full sweep (23 tasks × 3 arms × 3 repeats = 207 runs):
uv run python -m agent_study.run --arms BARE,DOCS,FULL --repeats 3 --model claude-opus-4-8

# 4. Score + report (offline):
uv run python -m agent_study.metrics
uv run python -m agent_study.failure_modes
uv run python -m agent_study.report
```

## Files

| File | Role |
|---|---|
| `target_schema.py` | The goal format + scoring field lists + canonical units. |
| `ground_truth.py` | Parser model → target schema adapters (unit-canonicalized). |
| `tasks.py` / `tasks.json` | Solvable, program-diverse tasks + frozen reference answers. |
| `arms.py` | BARE/DOCS/FULL system-prompt builders from real scaffold assets. |
| `run.py` | Claude Agent SDK harness → per-run transcripts in `runs/`. |
| `metrics.py` | Transcripts → `metrics.csv` (steps, errors, precision/recall, success). |
| `failure_modes.py` | Transcripts → `failure_modes.csv` (labeled agent failure modes). |
| `report.py` | Aggregates → `report.md` (per-arm effort/outcome + failure distribution). |
