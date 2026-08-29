"""Run the coding agent over each task x arm x repeat -> per-run transcripts.

Uses the Claude Agent SDK (``claude_agent_sdk``). The agent is given the
parse-patrol MCP parse tools plus the built-in Bash/Read/Write tools (so it can
also take the direct-import path ``from parse_patrol import cclib_parse``), and a
per-arm system prompt (BARE / DOCS / FULL, see arms.py). Each run's full message
stream is captured to ``agent_study/runs/<task>__<arm>__<rep>.json`` for offline
scoring by metrics.py / failure_modes.py.

Auth: the SDK drives the local ``claude`` CLI, which uses your existing Claude
login — no ANTHROPIC_API_KEY needed if ``claude`` is authenticated. Install the
SDK first (see agent_study/README.md).

Usage:
    python -m agent_study.run --tasks agent_study/tasks.json \
        --arms BARE,DOCS,FULL --repeats 3 --model claude-opus-4-8
    # pilot:
    python -m agent_study.run --limit-tasks 4 --arms BARE,DOCS,FULL --repeats 1
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from agent_study.arms import ARMS, system_prompt
from agent_study.target_schema import schema_json_hint

# MCP tool names the agent may call (mcp__<server>__<tool>).
PARSE_PATROL_TOOLS = [
    "mcp__parse_patrol__cclib_parse_file_to_model",
    "mcp__parse_patrol__gauss_parse_file_to_model",
    "mcp__parse_patrol__iodata_parse_file_to_model",
    "mcp__parse_patrol__ase_parse_file_to_model",
]
BUILTIN_TOOLS = ["Bash", "Read", "Write"]

MCP_SERVERS = {
    "parse_patrol": {
        "type": "stdio",
        "command": "uv",
        "args": ["run", "python", "-m", "parse_patrol"],
    }
}


def task_prompt(task: Dict[str, Any], out_path: str) -> str:
    """The user turn — identical across arms (the scaffold lives in the system prompt)."""
    return (
        f"Convert the computational-chemistry output file below into the target JSON "
        f"schema and write the JSON to `{out_path}`.\n\n"
        f"Source file:\n{task['source_file']}\n\n"
        f"Target JSON schema (use these canonical units: coordinates in Angstrom, "
        f"energies in Hartree, frequencies in cm^-1, IR intensities in km/mol; omit "
        f"fields not present in the source):\n{schema_json_hint()}\n\n"
        f"Extract every field the source supports. Write only the JSON object to the "
        f"output path."
    )


def _block_to_dict(block: Any) -> Dict[str, Any]:
    """Serialize a content block (best-effort across SDK versions)."""
    kind = type(block).__name__
    d: Dict[str, Any] = {"block": kind}
    for attr in ("text", "name", "input", "tool_use_id", "content", "id", "thinking"):
        if hasattr(block, attr):
            val = getattr(block, attr)
            # tool_result content can itself be blocks; stringify defensively
            try:
                json.dumps(val)
                d[attr] = val
            except (TypeError, ValueError):
                d[attr] = str(val)
    return d


def _message_to_dict(msg: Any) -> Dict[str, Any]:
    kind = type(msg).__name__
    d: Dict[str, Any] = {"message": kind}
    content = getattr(msg, "content", None)
    if isinstance(content, list):
        d["blocks"] = [_block_to_dict(b) for b in content]
    elif content is not None:
        d["content"] = content if isinstance(content, str) else str(content)
    for attr in ("total_cost_usd", "num_turns", "duration_ms", "is_error", "result", "subtype"):
        if hasattr(msg, attr):
            d[attr] = getattr(msg, attr)
    usage = getattr(msg, "usage", None)
    if usage is not None:
        d["usage"] = usage if isinstance(usage, dict) else str(getattr(usage, "__dict__", usage))
    return d


async def run_one(task: Dict[str, Any], arm: str, rep: int, model: str,
                  max_turns: int, runs_dir: str, max_budget_usd: float) -> Dict[str, Any]:
    """Execute a single agent run and persist its transcript."""
    from claude_agent_sdk import ClaudeAgentOptions, query  # type: ignore[import-not-found]

    run_id = f"{task['task_id']}__{arm}__{rep}"
    out_json = os.path.join(runs_dir, f"{run_id}.output.json")  # where the AGENT writes
    # NONE is the no-harness baseline: no parse-patrol MCP server and no parser
    # tools at all, so the agent must extract and map from scratch with code alone.
    if arm == "NONE":
        allowed_tools, mcp_servers = BUILTIN_TOOLS, {}
    else:
        allowed_tools, mcp_servers = PARSE_PATROL_TOOLS + BUILTIN_TOOLS, MCP_SERVERS
    options = ClaudeAgentOptions(
        system_prompt=system_prompt(arm, task.get("format_level")),
        allowed_tools=allowed_tools,
        mcp_servers=mcp_servers,  # type: ignore[arg-type]
        permission_mode="bypassPermissions",
        model=model,
        max_turns=max_turns,
        max_budget_usd=max_budget_usd,  # per-run spend safety cap
        setting_sources=[],             # ignore project CLAUDE.md/settings for reproducibility
        cwd=os.getcwd(),
    )

    transcript: List[Dict[str, Any]] = []
    async for message in query(prompt=task_prompt(task, out_json), options=options):
        transcript.append(_message_to_dict(message))

    produced: Optional[Any] = None
    if os.path.exists(out_json):
        try:
            with open(out_json) as f:
                produced = json.load(f)
        except (json.JSONDecodeError, OSError):
            produced = None

    record = {
        "run_id": run_id,
        "task_id": task["task_id"],
        "program": task["program"],
        "tier": task.get("tier", "easy"),
        "format_level": task.get("format_level", ""),
        "arm": arm,
        "repeat": rep,
        "model": model,
        "source_file": task["source_file"],
        "parser_success": task["parser_success"],
        "reference": task["reference"],
        "reference_parsers": task.get("reference_parsers", []),
        "produced": produced,
        "transcript": transcript,
    }
    with open(os.path.join(runs_dir, f"{run_id}.json"), "w") as f:
        json.dump(record, f, indent=2)
    return record


async def _main_async(args) -> None:
    with open(args.tasks) as f:
        tasks = json.load(f)["tasks"]
    if args.limit_tasks:
        tasks = tasks[: args.limit_tasks]
    arms = [a.strip() for a in args.arms.split(",") if a.strip() in ARMS]
    os.makedirs(args.runs_dir, exist_ok=True)

    total = len(tasks) * len(arms) * args.repeats
    done = 0
    for task in tasks:
        for arm in arms:
            for rep in range(args.repeats):
                done += 1
                print(f"[{done}/{total}] {task['task_id']} arm={arm} rep={rep}", flush=True)
                try:
                    await run_one(task, arm, rep, args.model, args.max_turns,
                                  args.runs_dir, args.max_budget_usd)
                except Exception as e:  # keep the sweep going; record the failure
                    print(f"    run failed: {type(e).__name__}: {e}", flush=True)
    print(f"Wrote {done} run records to {args.runs_dir}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks", default="agent_study/tasks.json")
    ap.add_argument("--arms", default="BARE,DOCS,FULL")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--limit-tasks", type=int, default=0, help="0 = all tasks (pilot: use e.g. 4)")
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--max-turns", type=int, default=30)
    ap.add_argument("--max-budget-usd", type=float, default=2.0, help="per-run spend cap")
    ap.add_argument("--runs-dir", default="agent_study/runs")
    args = ap.parse_args()
    asyncio.run(_main_async(args))


if __name__ == "__main__":
    main()
