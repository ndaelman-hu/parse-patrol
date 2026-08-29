# Related work: quantifying harness effectiveness for code-generating agents, and the frameworks for artifact hardness

Cited map for the agent-scaffold-study (does the parse-patrol harness reduce a
coding agent's workload and failure modes when it generates a parser/extraction
artifact toward a target schema, and what theory predicts *when* it helps).

**Provenance.** Built from a fan-out, adversarially-verified literature search
(23 sources → 110 candidate claims → 25 verified by 3-vote refutation panels:
**22 confirmed, 3 refuted**). Refuted claims are excluded and listed at the end so
we do not repeat them. Two arXiv-only 2025/2026 items carry `[title-to-confirm]`.

---

## Part A — Prior work that *quantifies* harness/scaffold effect on code-generating agents

### A1. Scaffold / agent-interface ablations with workload + failure metrics
- **Yang et al. 2024, "SWE-agent: Agent-Computer Interfaces Enable Automated
  Software Engineering," NeurIPS 2024** (arXiv:2405.15793). A controlled ablation
  over interface components on 300 SWE-bench issues shows *interface design drives
  performance* (a purpose-built ACI yields a large relative gain over a shell-only
  baseline with the *same* model), and edit **guardrails** (a linter that discards
  invalid edits) measurably help. *Relevance: the canonical precedent for our
  arms — the scaffold, not the model, is the manipulated variable; and guardrails
  ≈ our "content-check" against silent-empty.*
- **Liu et al. 2024, "AgentBench: Evaluating LLMs as Agents," ICLR 2024.**
  Multi-environment agent benchmark that defines an **explicit failure-mode
  taxonomy**. *Relevance: precedent for cataloguing agent failures (our wrong-tool
  / silent-empty / from-scratch taxonomy).*
- **Qin et al. 2024, "ToolLLM: Facilitating LLMs to Master 16000+ Real-world
  APIs," ICLR 2024** (ToolBench). Augmenting an LLM with a tool/API layer
  measurably improves tool-use performance. *Relevance: precedent that a tool
  harness helps, quantified.*
- **Patil et al. 2023, "Gorilla: LLM Connected with Massive APIs"**
  (arXiv:2305.15334). API-tool-use with documentation-grounded invocation. *Cited
  for the tool-augmentation setting; we do NOT use its head-to-head accuracy claim
  (that specific claim was refuted in verification — see end).*

### A2/A4. Vetted components vs. from-scratch; documentation; failure operationalization
- **Jain et al. 2024, "On Mitigating Code LLM Hallucinations with API
  Documentation," Amazon** (arXiv:2407.09726). Code LLMs hallucinate APIs at rates
  **strongly dependent on API frequency** (GPT-4o: 38.58% valid low-frequency vs
  93.66% high-frequency invocations); supplying API **documentation** mitigates it.
  Operationalizes hallucination as a checkable failure. *Relevance: direct
  precedent for our DOCS arm and hallucinated-field mode — and the frequency
  dependence mirrors our finding that failure tracks how "tail"/complex the format
  is.*
- **Gu et al. 2025, "What to Retrieve for Effective Retrieval-Augmented Code
  Generation? An Empirical Study and Beyond"** (arXiv:2503.20589). **Not all
  context helps** — retrieved *documentation/API info* helps, but retrieved
  *similar code* introduces noise that can degrade generation. *Relevance:
  precedent that a scaffold can hurt if it's the wrong kind — matters for whether
  DOCS/FULL ever add noise/tokens without benefit.*
- **Ellis et al. 2021, "DreamCoder: Bootstrapping Inductive Program Synthesis with
  Wake-Sleep Library Learning," PLDI 2021.** Reusing learned, vetted abstractions
  beats searching primitives from scratch. *Relevance: the "use tested components
  vs. write from scratch" thesis, formalized as library learning.*

### A5. Parser / wrapper / log-parsing synthesis and its evaluation
- **Fisher, Walker, Zhu & White 2008, "From Dirt to Shovels: Fully Automatic Tool
  Generation from Ad Hoc Data," POPL 2008** (PADS). Fully-automatically infers the
  format of ad-hoc data and emits an end-to-end tool suite (parser, printer, XML
  converter, analyzer), replacing hand-written format specs — i.e. it **quantifies
  effort saved** by automatic synthesis. *Relevance: the canonical theory that
  synthesizing a parser from scratch can be principled — legitimizes the agent's
  from-scratch mode when no tool fits.*
- **Zhu et al. 2019, "Tools and Benchmarks for Automated Log Parsing,"
  ICSE-SEIP 2019.** Benchmarks 13 automated log parsers over 16 real datasets;
  **no single parser is universally best**. *Relevance: precedent for our
  multi-parser benchmark and oracle — heterogeneity forces selection/combination.*
- **Le & Zhang 2023, "Log Parsing: How Far Can ChatGPT Go?," ASE 2023 (NIER)**
  (arXiv:2306.01590), and **the LLM-log-parsing review** (arXiv:2504.04877).
  The **scaffold/guidance given to the LLM materially changes parsing accuracy**:
  structured prompts (extraction rules, demonstrations) beat naive prompts by
  20–60%; a bare prompt barely grasps the task. *Relevance: the closest applied
  cousin — an LLM doing a parsing task where scaffolding is measured to help.*

---

## Part B — Frameworks for "how hard is the artifact the agent must generate"

### B6. Formal-language / Chomsky-hierarchy expressiveness (our leading lens)
- **Delétang et al. 2023, "Neural Networks and the Chomsky Hierarchy," ICLR 2023**
  (arXiv:2207.02098). Grouping tasks by the hierarchy predicts generalization;
  **only architectures augmented with structured memory reach context-free /
  context-sensitive** tasks. *(State carefully: the broad claim "transformers/RNNs
  fail on all non-regular tasks" did NOT survive verification — see end. The
  memory-augmentation result did.)*
- **Merrill & Sabharwal 2024, "The Expressive Power of Transformers with Chain of
  Thought," ICLR 2024** (arXiv:2310.07923). A **linear number of CoT steps lets a
  transformer recognize all regular languages** it otherwise cannot; intermediate
  generation fundamentally raises expressive power.
- **Li et al. 2024, "Chain of Thought Empowers Transformers to Solve Inherently
  Serial Problems," ICLR 2024.** Without CoT, constant-depth/precision transformers
  are bounded by AC⁰ ⊊ TC⁰; CoT lifts them to serial computation.
- **Strobl et al. 2024, "What Formal Languages Can Transformers Express? A Survey,"
  TACL 2024** (arXiv:2311.00208). Consolidates the above.
- **`[title-to-confirm]` (arXiv:2607.06155, 2026).** **Maps agentic AI
  architectures onto the Chomsky hierarchy by memory structure** — regular ≈ finite
  automaton, context-free ≈ pushdown, Turing-complete ≈ Turing machine. *Relevance:
  the Chomsky-for-agents lens is **already occupied** — we cite, not claim it.*
- **`[title-to-confirm]` (arXiv:2510.23487, 2025).** **"Tool interface structure,
  not the controller, determines expressivity gains"**: a finite-precision
  recurrent model *without* tool interaction recognizes only regular languages; the
  tool interface is what lifts it. ***This is the closest prior work to our
  power-gap thesis.*** *Relevance: the theoretical claim "the harness lifts the
  agent up the hierarchy" is **theirs** — our contribution must be the empirical
  measurement and the format-complexity-conditioned prediction, not this theorem.*

### B6b. Failure *modes* by language level (with / without CoT)
- **Liu et al. 2023, "Transformers Learn Shortcuts to Automata," ICLR 2023 (oral)**
  (arXiv:2210.10749). A low-depth transformer can represent any finite-state
  automaton via *shortcut* solutions (o(T) layers) that then **fail to
  length-generalize** — a failure *mechanism* tied to the automaton/level.
- **Dziri et al. 2023, "Faith and Fate: Limits of Transformers on
  Compositionality," NeurIPS 2023 (Spotlight)** (arXiv:2305.18654). Transformers
  reduce multi-step reasoning to *linearized subgraph matching* and **fail as graph
  width and depth grow** — a compositional/graph hardness axis. *(Doubles as the
  Axis-B graph-complexity bridge.)*
- **CoT changes the profile:** without CoT the failure is the one-shot bound
  (AC⁰/TC⁰; Li et al. 2024); with CoT the model climbs but exhibits serial-error
  modes. *No located work cross-tabulates a coding-agent **failure-mode taxonomy**
  (silent-empty / wrong-tool / retry-loop / gave-up) against **Chomsky level ×
  CoT-on/off** — see Part C.*

### B7. Program-synthesis / inductive-programming complexity
- **Polozov & Gulwani 2015, "FlashMeta: A Framework for Inductive Program
  Synthesis," OOPSLA 2015**, and **Gulwani, "Programming by Examples," 2016.**
  Synthesis hardness is controlled by **restricting the DSL** and by example-based
  specs (reasoning over concrete inputs is more tractable than over symbolic program
  states). *Relevance: an alternative "artifact hardness" axis — how big/restricted
  is the space the agent must search — complementary to format complexity.*

### B8. Alternative artifact-hardness lenses
- **Vitányi & Li 2000, "Minimum Description Length Induction, Bayesianism, and
  Kolmogorov Complexity," IEEE Trans. Inf. Theory.** Artifact hardness as
  description length. *Relevance: an information-theoretic alternative to the
  automata-class view (a parser's Kolmogorov complexity vs. its Chomsky class).*
- **`[title-to-confirm]` (Frontiers in AI, 2026).** "Hybrid Intelligence Effort":
  in LLM-assisted workflows, **effort shifts from code production to oversight /
  validation / hallucination mitigation**. *Relevance: supports measuring
  *workload* (our steps/tool-calls/tokens), not just pass/fail.*
- **`[title-to-confirm]` (Frontiers in Neuroscience, 2022).** Code-complexity
  metrics (cyclomatic, cognitive complexity) **diverge from perceived difficulty**.
  *Relevance: caveat — "how hard is the artifact" is not captured by classic code
  metrics; a formal-complexity axis may predict agent effort better.*

---

## Part C — Gaps and positioning

Two things are, honestly, **already established** and must be cited rather than
claimed:
1. **"A tool harness / CoT lifts an agent up the Chomsky hierarchy"** — theoretical
   (Merrill & Sabharwal 2024; arXiv:2510.23487; arXiv:2607.06155).
2. **"Scaffolding/tools reduce coding-agent effort and failures"** — empirical
   (SWE-agent 2024; ToolLLM 2024; API-doc hallucination 2024; LLM-log-parsing
   2023–24).

The **white space is their conjunction, conditioned on format complexity, in a
scientific-parser domain.** No located work does *all* of:
(i) **empirically quantifies** a harness's reduction of a coding agent's *workload
and failure modes* for **parser/extraction code generation**, **and**
(ii) uses a **format-complexity (Chomsky / power-gap) taxonomy to predict *which
inputs* the harness helps on** (structured L0 → harness suffices; free-form/
cross-file L2–L3 → the agent must escalate), **and**
(iii) grounds it in **real, heterogeneous scientific output** with a
**domain-specific failure taxonomy** (silent-empty-accepted, wrong-parser,
parser-from-scratch, unit-error).

The nearest neighbors each occupy only one axis: arXiv:2510.23487 has the
tool-expressivity theory but **no** workload/failure measurement and **no** domain;
the LLM-log-parsing line (arXiv:2306.01590, 2504.04877) has an applied parsing task
with measured scaffold gains but **no** complexity-hierarchy prediction of *when*;
Zhu et al. 2019 benchmarks parsers but **no** agent and **no** synthesis; PADS 2008
synthesizes parsers but **pre-LLM** and without an agent-effort measurement.

**Our contribution, positioned honestly:** an *empirical* test of the harness's
effect on agent workload and a *complexity-conditioned* failure taxonomy for
scientific parser code-generation — using the established tool-expressivity theory
as the *predictive frame*, not as a claimed result. The parser-*selection* problem
specifically (choosing among wrapped parsers) remains a gap; the closest transfer
is the LLM tool-selection literature (ToolLLM, Gorilla), which we adapt.

**Two sharper white-space claims (both survive the literature check):**
1. **A failure-mode taxonomy indexed by language level.** Capability-by-level maps
   exist (Delétang 2023) and failure *mechanisms* exist (Liu 2023; Dziri 2023), but
   **no work cross-tabulates a coding-agent failure-mode taxonomy against Chomsky
   level × CoT-on/off.** Doing so for scientific parser codegen — *which* failure
   mode dominates at L0 vs L2 vs L3, with and without the harness — is a distinct
   contribution.
2. **The right formalism is two-axis.** The Chomsky/string hierarchy governs file
   *syntax* (Axis A); the *chemical* target is graph-structured, better graded by
   graph grammars (MØD, arXiv:1603.02481), designed molecular grammars (SELFIES,
   arXiv:1905.13741), and graph descriptive complexity (Courcelle/treewidth). No
   located work combines a string-syntax and a graph-structure hardness axis to
   predict extraction/harness value — see `paper/format_semantic_hierarchy.md`.

---

## Excluded — claims that did NOT survive adversarial verification (do not cite these)
- ✗ *Gorilla (LLaMA-7B) outperforms GPT-4 on API accuracy by 20.43% / Claude by
  10.75% zero-shot* (arXiv:2305.15334) — refuted 0–3. Gorilla is real; this
  head-to-head margin is not reliable.
- ✗ *In RAG code-gen, retrieving similar code degrades results by **up to 15%*** —
  refuted 1–2. The qualitative "not all context helps / similar-code adds noise"
  **did** verify (3–0); the specific 15% figure did not. Cite the qualitative form.
- ✗ *RNNs **and Transformers** empirically fail to generalize on **all** non-regular
  tasks* (Delétang) — refuted 1–2. Use the verified form: *only memory-augmented
  architectures reach context-free/context-sensitive* (2–1 confirmed).

## Provenance note
Adversarial verification ran per claim (3 independent refutation votes; a claim
died on ≥2 refutes). Titles/venues for the 2025–26 arXiv items marked
`[title-to-confirm]` should be checked against the arXiv abstract page before they
go in a submission bibliography.
