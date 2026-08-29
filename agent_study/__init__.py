"""Agent scaffold study.

Does giving a coding agent a capability scaffold reduce the number of steps it
takes and the errors it makes when converting a real computational-chemistry
source file into a fixed target schema?

Three arms (only the scaffold text in the system prompt varies; the tool set is
held constant):

    BARE  -> parse tools only, no guidance on which tool fits which format
    DOCS  -> + each parser's documentation (its supported formats)
    FULL  -> + the cross-parser capability map (parser x property-group)

Pipeline:
    target_schema.py -> the canonical goal format the agent must produce
    ground_truth.py  -> parser model -> target schema (reference answers)
    tasks.py         -> freeze solvable tasks (>=1 parser works) into tasks.json
    arms.py          -> the three system-prompt variants
    run.py           -> Claude Agent SDK harness -> per-run transcripts
    metrics.py       -> transcripts -> steps / errors / precision-recall / success
    failure_modes.py -> transcripts -> agent failure-mode labels
    report.py        -> per-arm aggregation -> report.md

Reuses the parser-reliability benchmark in ``benchmarks/`` as ground-truth
tool x source capability labels; that benchmark remains a separate artifact.
"""
