"""The three experimental arms: identical base + increasing scaffold.

Only the scaffold text added to the system prompt differs across arms; the tool
set and the task prompt are held constant, so any difference in the agent's
behaviour is attributable to the scaffold *knowledge*, not to tool availability.

    NONE  no harness at all: the parse-patrol MCP server and parser tools are
          withheld (see run.py), so the agent must extract and map from scratch with
          code alone. This is the baseline that isolates the harness's value.
    BARE  base only. The agent knows the four parsers exist (their tool names are
          visible) but gets no guidance on which handles which format.
    DOCS  base + each parser's own documentation (the formats it supports).
    FULL  DOCS + the cross-parser capability map (parser x property-group), i.e.
          .pipelines/resources/{semantic,structure}-schema.md.

The scaffold content is pulled from the real parse-patrol assets so the
experiment tests the project's actual scaffolding.
"""

from __future__ import annotations

import importlib
from functools import lru_cache
from typing import Any, List

NONE_SYSTEM = """\
You are a coding agent that extracts data from a computational-chemistry output \
file and writes it into a fixed target JSON schema.

You have no specialized parsers available. Write and run your own code (you may \
write Python and install libraries) to read the file, extract the requested \
fields, convert them to the schema's canonical units, and write the resulting JSON \
to the path given in the task. Do not invent values that are not present in the \
file.\
"""

BASE_SYSTEM = """\
You are a coding agent that extracts data from a computational-chemistry output \
file and writes it into a fixed target JSON schema.

You have the parse-patrol parsers available two ways:
  - as MCP tools (cclib, ase, gaussian, iodata parse tools), and
  - as importable Python functions, so you may also write and run a script:
        from parse_patrol import cclib_parse, ase_parse, gaussian_parse, iodata_parse

Use the parsers rather than writing your own from scratch. Extract the requested \
fields, convert them to the schema's canonical units, and write the resulting \
JSON to the path given in the task. Do not invent values that are not present in \
the file.\
"""

_DOC_RESOURCES = [
    ("parse_patrol.parsers.cclib.__main__", "cclib_documentation"),
    ("parse_patrol.parsers.ase.__main__", "ase_documentation"),
    ("parse_patrol.parsers.iodata.__main__", "iodata_documentation"),
]

_CAPABILITY_MAP_FILES = [
    ".pipelines/resources/semantic-schema.md",
    ".pipelines/resources/structure-schema.md",
]


def _drive(coro: Any) -> Any:
    """Run an await-free coroutine to completion without an event loop.

    The MCP resource functions are ``async def`` but contain no real awaits (they
    just return a literal), so a single ``.send(None)`` completes them. This avoids
    a nested-event-loop error when the scaffold is built from inside the harness's
    running loop.
    """
    try:
        coro.send(None)
    except StopIteration as stop:
        return stop.value
    raise RuntimeError("resource coroutine unexpectedly awaited")


def _call_resource(mod: str, fn: str) -> str:
    func = getattr(importlib.import_module(mod), fn)
    result = func()
    return _drive(result) if hasattr(result, "send") else result


@lru_cache(maxsize=1)
def docs_text() -> str:
    parts: List[str] = []
    for mod, fn in _DOC_RESOURCES:
        parts.append(_call_resource(mod, fn).strip())
    return "\n\n---\n\n".join(parts)


@lru_cache(maxsize=1)
def capability_map_text() -> str:
    parts: List[str] = []
    for path in _CAPABILITY_MAP_FILES:
        with open(path) as f:
            parts.append(f.read().strip())
    return "\n\n".join(parts)


# Complexity-aware scaffold (the theory-grounded arm): tells the agent the
# source's format complexity, each tool's parsing-power ceiling, and the rule to
# escalate to writing its own parser when the format outranks every tool.
_LEVEL_DESC = {
    "L0": "L0 — grammar-defined/structured (XML/JSON/fchk): a well-scoped parser should read it directly.",
    "L1": "L1 — line-regular structure/input: simple, regex/line-scannable.",
    "L2": "L2 — free-form output log with block + count-agreement (N atoms then N lines; repeated blocks, take the last): needs a stateful scan, not a lone regex.",
    "L3": "L3 — cross-referential / multi-file (values defined in one file/section, used in another): needs context tracking across files.",
}
_TOOL_POWER = (
    "# Tool parsing-power ceilings\n"
    "- custom Gaussian parser: regex — regular; reliable only on Gaussian-format logs.\n"
    "- cclib / ASE / iodata (text readers): stateful line scanners — regular + counting.\n"
    "- iodata / ASE grammar-backed readers (.fchk/.molden/XML/JSON): context-free.\n"
    "- you, writing Python: Turing-complete — you can parse any level.\n\n"
    "Rule: if the source's level exceeds what an available parser handles (L3, or a "
    "structured format no parser supports), do NOT thrash calling parsers that will "
    "return empty — write your own stateful/recursive parser. Otherwise pick the "
    "parser whose power matches the format."
)


def system_prompt(arm: str, format_level: str | None = None) -> str:
    if arm == "NONE":
        return NONE_SYSTEM
    if arm == "BARE":
        return BASE_SYSTEM
    docs = f"{BASE_SYSTEM}\n\n# Parser documentation\n\n{docs_text()}"
    if arm == "DOCS":
        return docs
    full = (docs + "\n\n# Cross-parser capability map (which parser extracts which property)"
            f"\n\n{capability_map_text()}")
    if arm == "FULL":
        return full
    if arm == "COMPLEXITY":
        lvl = _LEVEL_DESC.get(format_level or "", "unknown format complexity")
        return f"{full}\n\n# Source format complexity\nThis file: {lvl}\n\n{_TOOL_POWER}"
    raise ValueError(f"unknown arm: {arm}")


ARMS = ["NONE", "BARE", "DOCS", "FULL", "COMPLEXITY"]
