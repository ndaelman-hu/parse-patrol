# Paper outline v2 — competence-vs-performance framing

Restructure per discussion: **emphasize failure + documentation, de-emphasize the
molecular angle** (molecular data is the *test case*, not the subject). Thesis:
*agents are assumed Turing-complete, but competence ≠ performance; we measure where
their realized parsing capability actually sits along the language-complexity
hierarchy.*

Working title (candidates):
- *Competence is not Performance: Where LLM Agents Actually Parse Along the Complexity Hierarchy*
- *The Parsing Gap: Measuring Realized vs. Expressive Capability of Coding Agents*

---

## 1. Introduction (the argument, in order)
1. **Turing complexity.** A coding agent can emit code in a Turing-complete
   language, so it is *assumed* able to solve arbitrarily complex processing tasks.
2. **Competence vs. performance.** That is an *expressivity* claim, not evidence of
   *realized* capability — the hidden assumption (Chomsky's own distinction;
   Delétang 2023 capacity≠generalization; Merrill & Sabharwal finite-precision;
   Dziri "could≠does"). We treat it as a hypothesis to *measure*, not assume.
3. **A hierarchy of language complexity.** Chomsky (regular → CF → CS → RE) refined
   by Joshi's mildly-context-sensitive band and the LCFRS fan-out ladder — the
   principled scale on which we place tasks.
4. **Parsing as the probe.** We test realized capability at the *first, most
   overlooked step of any information-processing chain*: **parsing**. Novelty —
   the field studies downstream reasoning; the grounding/parsing step is
   understudied. Novelty is **not** Chomsky-grading LLM parsing — ChomskyBench
   (Dong et al. 2026, arXiv:2604.02709) did that on *synthetic* languages and is our
   nearest baseline — but doing it on **real heterogeneous scientific output**, with
   a **harness/documentation manipulation**, measuring **competence vs. performance
   on a real code-artifact task**, plus a **failure-mode taxonomy indexed by
   grammatical class** (still unoccupied).
5. **Test case.** Processing real **ab initio / molecular output data** — a hard,
   heterogeneous, real-world instance (not the subject, the instrument).

## 2. The system: parse-patrol (MCP server)
- **Layout (brief):** dual-mode — parsers exposed as MCP tools *and* as direct
  Python imports; a documentation/scaffolding layer (per-parser docs, capability
  metadata, prompts).
- **Original goal:** built to **facilitate parser onboarding into NOMAD**, later
  extended toward **community-wide information exchange** (parsers as shared,
  discoverable, testable components).
- Why it's the right probe: it lets us vary exactly the *documentation/scaffolding*
  the agent receives, and measure the effect.

## 3. Methodology
- **Two difficulty axes:**
  - **Source complexity** — the format's **grammatical class** (regular /
    context-free / mildly context-sensitive / context-sensitive), with
    **grammar-availability** (does a designed, tested parser already exist?) as a
    *separate* factor. No ad-hoc "L" labels: a context-free XML file is
    grammatically *more* complex than a regular log yet easier to extract, precisely
    because its grammar is supplied — that separation is a result, not a footnote.
  - **Target schema complexity** — from a *bounded* target (fill a fixed JSON
    schema) up to a **Turing-complete** target (generate an executable code
    artifact, e.g. a **PySCF** script), so the *output* difficulty also spans the
    hierarchy.
- **Documentation arms (the scaffolding variable):** BARE → +DOCS → +capability-map
  → +complexity-level (what the harness tells the agent).
- **Instrumentation:** track tool-calls / turns / tokens **and the agent's
  chain-of-thought**; label a failure-mode taxonomy (wrong-tool, silent-empty,
  parser-from-scratch, hallucinated-field, unit-error, retry-loop, gave-up) and
  **index it by grammatical class × target-complexity × arm**.
- Reuses the existing instrument (`agent_study/`): arms, metrics, failure_modes,
  format-complexity rubric.

## 4. Results — overview in main text, detail in SI
- **Main text:** a single overview — realized capability vs. formal-complexity
  demand (does performance track its grammatical class?), the failure-mode distribution by class,
  and the scaffold/documentation effect by class. The competence–performance gap,
  quantified.
- **SI:** full per-run results, per-arm tables, and the **CoT transcripts**.

## 5. Discussion & outlook
- The measured competence–performance gap and where documentation closes it (peaks
  in the mildly-context-sensitive band, per the offloadability law).
- **Follow-up:** *Turing-complete parsing / information-processing chains.* Most
  real processing pipelines are Turing-complete end to end; parsing is the tractable
  first step — extending the measurement up the target-complexity axis (toward
  code-generation targets like PySCF) is the natural next study.

---

## Decisions this forces (flagged for you)
1. **Venue fit.** De-emphasizing molecular content makes this a stronger
   CS/formal-methods paper but a *weaker* fit for a molecular-ML workshop. Keeping
   molecular data as the visible test case is the hedge. (Live tension — you've set
   the emphasis; noting the trade.)
2. **New axis = new experiments.** The *target-complexity* axis (JSON → PySCF
   code-gen) is a genuinely new dimension and a strong idea, but a Turing-complete
   target means *generating and running executable code* and checking correctness —
   materially heavier than filling a JSON schema. Bigger sweep, higher cost.
3. **Two claims depend on the running deep-research:** the "parsing is understudied /
   the cross-section is vacuous" novelty hook, and any "no prior benchmark" statement.
4. **Scope/cost.** grammatical class × target-complexity × 4 arms × repeats × CoT logging is a
   substantially larger run than the 12-task pilot; needs a scale/model decision.
