# Follow-up research plan — from the ML4Molecules 2026 workshop paper to a full paper

**Status:** the workshop paper (`ml4molecules-2026-submission`, non-archival) is a *first,
single-run, single-model* sweep. Findings are suggestive, not confirmed. This plan turns it
into an archival-quality study. Source of truth for experiments; narrative/lit thinking
lives in the Obsidian vault.

## Headline result to defend / sharpen
Giving a coding agent tested parsers barely improves parsing of computational-chemistry
output and *introduces* silent interface failures; what helps is telling it where the
format sits on the language-complexity hierarchy and where each tool's power ends.
Realized performance turns on **knowing** tool power, not **having** the tools. Success is
roughly flat (53→63%); the effect is on **failure composition and cost**, not success rate.

## Priorities

### P0 — Disentangle the COMPLEXITY-arm confound (the #1 experiment)
The `COMPLEXITY` arm bundles two cues: (a) the source's **grammatical class** and (b) each
**tool's power ceiling** + escalation rule. The current design cannot say which drives the
interface-failure collapse — and the CoT shows the agent sometimes just *skips* tools,
consistent with a generic "distrust parsers" nudge. Add ablation arms:
- `CLASS-ONLY` — source grammatical class, no tool ceilings.
- `CEILING-ONLY` — tool power ceilings + escalation rule, no source class.
- `DISTRUST` — a generic "the parsers may not fit; verify or write your own" nudge.
Reuse `agent_study/arms.py`. Outcome: attribute the mechanism, or show it needs both cues.

### P1 — Statistical power
≥3 runs/cell and 2–3 models (include an open-weight model) to get significance + separate
model-specific behaviour from general effects. Reuse `agent_study/run.py` (`--repeats`,
`--model`). Report variance, not just point estimates.

### P1 — Populate the hierarchy extremes
The corpus is skewed to the mildly-context-sensitive middle. Add:
- **Regular** formats (finite-state; currently 0 examples).
- **Context-sensitive = multi-file / interconnected** parsing (a quantity defined in one
  file referenced in another) — the outlook headline. Build a small balanced sub-corpus.

### P2 — Chain-of-thought analysis
Code *how* the agent integrates the complexity cue (when it decides to skip a parser,
escalate, or trust a tool). Qualitative + quantitative over the saved transcripts
(`agent_study/runs/`). This is the "why does knowledge help" thread.

### P2 — Independent ground truth
Replace the union-of-parsers reference (`agent_study/ground_truth.py`) with hand-verified
ground truth on a subset → real correctness, not field-presence.

### P2 — Fix-and-remeasure the harness (tests the thesis directly)
Act on the paper's own §5 critique: tighten the Pydantic output contract (required fields,
non-empty collections, cross-field consistency) and correct the capability metadata that
overstates coverage. Re-run: does *better tooling* substitute for *agent knowledge*, or do
the interface failures persist until the agent is told about complexity?

### P3 — Target-complexity axis
Extend the target from a fixed JSON schema to a Turing-complete artifact (e.g. a PySCF
input script). Note: Turing-complete *parsing* itself ≈ code analysis, already well studied,
so frame it as a known bound rather than the contribution.

### P3 — Quantitative positioning vs ChomskyBench / RELIC
Situate our real-data, code-artifact, harness-manipulation setup against the synthetic
formal-language benchmarks (ChomskyBench, RELIC) with comparable numbers where possible.

## Instruments to reuse (do not rebuild)
`agent_study/{arms,run,metrics,failure_modes,ground_truth,complexity}.py`;
`paper/neurips_submission/make_fig.py`; the DVC-tracked `tests/.data` + `agent_study/runs`.

## Camera-ready (if the workshop accepts)
Flip `\blindfalse` in `main_v2.tex` (restores Parse Patrol / NOMAD / hackathon cite + real
authors); swap the anon 4open.science link for the real repo (after a git-history scrub);
deposit a data snapshot to Zenodo/NOMAD for a DOI.
