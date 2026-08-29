# A formal-complexity lens on parser reliability and agentic file→schema conversion

> Concept note for the parse-patrol agent study. Develops the Chomsky-hierarchy
> framing raised in discussion, positions it against existing literature, and
> states the concrete, testable predictions it adds. Draft — for the paper's
> theory/related-work sections.

## 1. The reframing

Our current labels for *why a parser succeeds or fails* are atheoretical: we bin
by **program** (Gaussian, VASP, …). That describes the data but explains nothing.
Formal language theory offers a labeling axis that *predicts*: classify each
source format by the **grammatical complexity extraction demands**, and each tool
by the **class of languages it can recognize**. A parser is then expected to fail
exactly when the format's required class exceeds the parser's power — a
falsifiable claim, which is the currency a negative-results/benchmark paper needs.

## 2. Two mappings and one hypothesis

**Tools, by parsing power (ceiling of the automata class each implements):**

| Tool | Mechanism | Power ceiling |
|---|---|---|
| custom Gaussian parser | regexes + light line-state | **regular** (Type-3) |
| cclib / ASE / iodata text readers | stateful line scanners | **regular + counters** |
| iodata/ASE grammar-backed readers (`.fchk`, `.molden`, XML, JSON) | real format grammars / combinators | **context-free** (Type-2) |
| the coding agent (writes & runs code) | arbitrary Python | **Turing-complete** — can synthesize any class |

**Sources, by the complexity extraction demands.** These are not designed
languages — they are Fortran/C `write`-statement output — so we use a pragmatic
4-level ordinal *inspired by* the hierarchy, with a documented rubric, not a
formal per-file classification:

- **L0 — grammar-defined**: properly nested/structured (XML, JSON, `.fchk`,
  `.molden`). Context-free; machine-parseable by construction.
- **L1 — line-regular**: fixed tokens per line, no counting. Regular.
- **L2 — block + count-agreement**: a header declares *N atoms*, then *N* lines
  follow; repeated "standard orientation" blocks where you must take the last
  (Gaussian, FHI-aims, ORCA). The counting/agreement dependency a pure regex
  cannot enforce → *mildly context-sensitive*.
- **L3 — cross-referential / multi-file**: values defined in one section or file
  are referenced or combined elsewhere (WIEN2k `.struct`+`.scf`, exciting's split
  files). Context-sensitive.

**The power-gap hypothesis (central, falsifiable):**

> A fixed parser fails when the source's required level exceeds the parser's power
> ceiling. The coding agent's marginal value — and its rate of *correctly* writing
> a parser from scratch — rises with that gap.

This converts "parsers fail unpredictably" into "parsers fail *where tool-power <
format-level*," and recasts the agent from *a thing that calls tools* into **the
mechanism that climbs the hierarchy when the fixed tools are under-powered.**

## 3. The agent as an automata-class escalator

Why can the agent match arbitrary format complexity where a fixed parser cannot?
Because a plain transformer is a fixed-depth, sub-Turing computation, but **with
chain-of-thought and code execution it gains serial state and becomes
Turing-complete** — a jump in automata class, not merely "more parameters." This
is exactly the escalation the power-gap hypothesis predicts the agent performs.
The connection is well-established in the theory-of-computation-meets-neural-nets
literature (§5), which we borrow rather than re-derive.

## 4. Three axes of "what makes extraction hard" (be honest about scope)

The hierarchy is one axis, not the whole story. Over-fitting it would repeat the
strawman we already corrected once. Extraction difficulty decomposes into:

1. **Identification / dispatch** — *which* format is this, and which reader
   applies? Our reliability benchmark's *dominant* failure was
   `UnknownFileType` / `ccopen → None` (~30–95% of a parser's errors): the parser
   never even fired. That is a routing problem, orthogonal to parsing power.
2. **Grammatical complexity** — the Chomsky axis. Owns the power-gap hypothesis.
3. **Noise / corruption robustness** — binary interleaving (`UnicodeDecodeError`),
   truncated files (`StopIteration`), whitespace/locale/version drift. A format
   can be trivially L1 and still break every parser through dirtiness — and this
   is arguably where LLMs help *most*.

Honest framing for the paper: a **three-axis model** (identify / parse / denoise),
where formal complexity supplies the *explanatory backbone* for axis 2 and we do
not claim it governs 1 or 3.

## 5. Related work — what exists, and what is new

**Formal language theory ↔ neural networks (method precedent).** Delétang et al.,
*Neural Networks and the Chomsky Hierarchy* (arXiv:2207.02098, ICLR 2023),
empirically group tasks by Chomsky class and show RNNs/Transformers fail to
generalize on non-regular tasks while only memory-augmented nets reach
context-free/-sensitive — itself a negative-results paper using our exact
methodological move, in a synthetic-task domain. The expressiveness line shows
**chain-of-thought/serial computation lifts transformers up the hierarchy toward
Turing-completeness**: *Chain of Thought Empowers Transformers to Solve Inherently
Serial Problems* (ICLR 2024, OpenReview `3EWTEy9MTM`), *The Expressive Power of
Transformers with Chain of Thought*, *Towards Revealing the Mystery behind Chain
of Thought* (arXiv:2305.15408), and the survey *What Formal Languages Can
Transformers Express?* (arXiv:2311.00208); see also *Formal Language Theory Meets
Modern NLP* (arXiv:2102.10094). We **reuse** this to justify axis-2 escalation; we
do not contribute to it.

**Log parsing (closest cousin problem).** Extracting structure from
semi-structured machine text is the subject of a mature line: LogPai/`logparser`,
Drain, and *Tools and Benchmarks for Automated Log Parsing* (arXiv:1811.03509,
ICSE-SEIP 2019), now extended by LLM-based parsers (*System Log Parsing with Large
Language Models: A Review*, arXiv:2504.04877). **Difference:** log parsing mines
*templates* (recurring static/dynamic segments) for anomaly detection; it does not
convert to a *user-defined scientific target schema*, and it does not frame
difficulty by Chomsky class or by a tool-power/format-complexity gap.

**Declarative format grammars.** Kaitai Struct and PADS (Fisher & Gruber, PLDI
2005) describe formats *as grammars* so parsers are generated, not hand-written —
precisely what scientific text outputs lack, which is *why* their parsers are
brittle. cclib 2.0 (J. Chem. Phys. 2024) itself moved to a tree-based IR and a
*parser-combinator* organization (a functional route to context-free parsers),
evidence the field is converging on more principled parser structure.

**LLMs for scientific structured extraction.** Dagdelen et al., *Structured
information extraction from scientific text with large language models* (Nature
Communications 2024, `s41467-024-45563-x`) and related schema-prompted extractors
(e.g. multi-agent composition–property pipelines) target **natural-language
prose** in papers. **Difference:** our sources are *machine-emitted, structured
but undocumented* output files — a regime with sharp grammatical structure and
hard numeric ground truth, where a formal-complexity lens is meaningful and prose
IE methods do not directly apply.

**Domain infrastructure.** NOMAD Metainfo (Ghiringhelli et al.; *Shared metadata
for data-centric materials science*, arXiv:2205.14774) is the hierarchical
**target schema** and its per-code, hand-written parsers are the **brittle tool
layer** parse-patrol wraps; the LLM-Hackathon reflections (arXiv:2411.15221) are
the origin venue.

**Novelty statement (defensible, appropriately narrow).** The
neural-nets-and-the-Chomsky-hierarchy framing is established; log parsing and LLM
prose-extraction are established. What appears **new** is their synthesis:
framing the reliability of the *tool layer* (fixed parsers vs. an LLM coding
agent) for *computational-science output-file → schema conversion* as a
**parsing-power vs. format-complexity gap**, and using that gap to (a)
**explain and predict** where fixed parsers fail and (b) **predict when the agent
should escalate the automata class** (write-from-scratch vs. call a tool). We have
found no prior work combining these.

## 6. What it operationalizes into (concrete, staged by cost)

1. **Cheap, no new agent spend — a second label + a re-cut.** Add a `format_level`
   field (L0–L3) to `tasks.json` via a short rubric, and re-cut the existing
   parser-reliability benchmark (`benchmarks/results.csv`) by level. Prediction:
   the regex Gaussian parser (regular) collapses at L2; iodata's grammar-backed
   `.fchk` path (CF) holds at L0. If the data shows tool success dropping where
   *format-level > tool-power*, that is the paper's explanatory figure.
2. **The prize — a complexity-aware 4th scaffold arm.** Beyond BARE/DOCS/FULL, give
   the agent the source's level, each tool's power ceiling, and the rule *"if the
   format's level exceeds every tool, write a stateful/recursive parser
   yourself."* Predictions: fewer wrong-parser attempts at L2–L3; *higher* correct
   `parser_from_scratch` at L3 (where it is the right move) and *lower* at L0–L1
   (where it is wasted) — a sharper, theory-grounded effect than the documentation
   scaffold.
3. **A difficulty curve.** Test whether agent effort (tool calls, lines of parser
   code written, turns) rises monotonically with `format_level` — a clean
   theory-driven result and an axis for ordering tasks.

## 7. Testable predictions (summary)

- P1: Fixed-parser success on the mainfile decreases as `format_level` exceeds the
  parser's power ceiling; near-zero when the gap is ≥ 2 classes.
- P2: The agent's `parser_from_scratch` rate increases with `format_level`, and is
  *correct* (produces valid output) far more often at L3 than at L0–L1.
- P3: The complexity-aware arm reduces wrong-parser attempts and total tool calls
  vs. BARE/DOCS/FULL, concentrated at L2–L3.
- P4: Residual failures not explained by the power gap concentrate in axes 1
  (identification) and 3 (noise) — visible as `UnknownFileType`/decode/truncation
  errors roughly independent of `format_level`.

## Sources

- Delétang et al., *Neural Networks and the Chomsky Hierarchy*, arXiv:2207.02098 (ICLR 2023) — https://arxiv.org/abs/2207.02098
- *Chain of Thought Empowers Transformers to Solve Inherently Serial Problems*, ICLR 2024 — https://openreview.net/forum?id=3EWTEy9MTM
- *Towards Revealing the Mystery behind Chain of Thought: A Theoretical Perspective*, arXiv:2305.15408 — https://arxiv.org/pdf/2305.15408
- *What Formal Languages Can Transformers Express? A Survey*, arXiv:2311.00208 — https://arxiv.org/pdf/2311.00208
- *Formal Language Theory Meets Modern NLP*, arXiv:2102.10094 — https://arxiv.org/pdf/2102.10094
- Zhu et al., *Tools and Benchmarks for Automated Log Parsing*, arXiv:1811.03509 (ICSE-SEIP 2019) — https://arxiv.org/pdf/1811.03509
- *System Log Parsing with Large Language Models: A Review*, arXiv:2504.04877 — https://arxiv.org/html/2504.04877v2
- logpai/logparser toolkit — https://github.com/logpai/logparser
- Kaitai Struct — https://kaitai.io/
- cclib — https://github.com/cclib/cclib ; *cclib 2.0*, J. Chem. Phys. 161, 042501 (2024) — https://pubs.aip.org/aip/jcp/article/161/4/042501/3304757
- Dagdelen et al., *Structured information extraction from scientific text with LLMs*, Nature Communications 2024 — https://www.nature.com/articles/s41467-024-45563-x
- *Shared metadata for data-centric materials science* (NOMAD Metainfo), arXiv:2205.14774 — https://arxiv.org/pdf/2205.14774
- *Reflections from the 2024 LLM Hackathon for Applications in Materials Science and Chemistry*, arXiv:2411.15221 — https://arxiv.org/pdf/2411.15221
