# Architecture lessons

Design lessons for parse-patrol, distilled from the parser-reliability benchmark
(`benchmarks/`), the format/semantic complexity analysis (`paper/`), and the
harness-effectiveness study (`agent_study/`). Each lesson is grounded in a specific
finding.

**The through-line.** parse-patrol's job is *not* "have a parser for everything"
— that is impossible, and unnecessary: a coding agent is Turing-complete and can
always synthesize the missing parser itself. The harness's job is to make the
agent's climb **cheap** and its failures **visible**: tell it what's covered, tell
it when to escalate, hand it the derivations it cannot parse, normalize what it
does parse, and never let a failure be silent.

Three of these are already half-built in `agent_study/` / `benchmarks/`; the lesson
is to **promote them from the study into the harness itself.**

---

## Tier 1 — load-bearing

### 1. Return a validity signal, not just a model
**Finding.** Parsers return structureless models *without raising* on up to
1077/1104 files (`benchmarks/report.md`). **Lesson.** The harness's first job is to
make "no data extracted" explicit — a `has_structure` / `extraction_status` /
`warnings` field surfaced through every MCP tool. This converts a *silent* failure
(undetectable to the agent) into a *catchable* one. **Change.** Additive
(non-breaking) validity signal on the parser models + MCP responses. *(Issue #48.)*

### 2. Parse *and* derive — not just parse
**Finding.** Many target-schema concepts are graph/group-theoretic **computations a
parser cannot produce** — connectivity, `GlobalCrystalSymmetry`/Wyckoff, formula
canonicalization, band gap from eigenvalues (`paper/format_semantic_hierarchy.md`,
Axis B). **Lesson.** Be a **parse + derive** toolkit: expose derivation tools
(spglib for symmetry, formula canonicalizer, connectivity/graph builders) alongside
parsers, aligned to the `nomad-simulations` semantic schema. This is where the
agent's Turing-completeness is *qualitatively* needed (compensation mode 4).
**Change.** A `derive/` tool family exposed via MCP + direct import.

### 3. Own the conversion layer: canonicalize units and terms centrally
**Finding.** Parsers speak different units (cclib eV, iodata Bohr, the Gaussian
`zpve` Joules/Mol bug) → unit-error failures land on the agent. **Lesson.** The
"conversion layer" is formally an **attribute grammar**: put a normalization stage
between parser-native models and the target schema so the agent never sees raw
eV/Bohr. **Change.** Promote the canonicalizing adapters that already exist in
`agent_study/ground_truth.py` into a first-class normalization layer. *(Root cause
of issue #47.)*

---

## Tier 2 — efficiency / scaffolding

### 4. Give the agent the *map*; deliver context selectively
**Finding.** The power gap (L0 100% → L2 43% → L3 0%) says *when* a tool suffices vs.
must be escalated; but "not all context helps" and the pilot's ceiling show that
maximal scaffolding can *add* steps. **Lesson.** Expose format-level + per-tool
power ceiling as metadata so the agent selects at L0/L1 and escalates at L2–L3 —
delivered **complexity-conditioned** (surface the capability map when the format is
L2+, not unconditionally). Give the map; don't build an autonomous router.
**Change.** A complexity-metadata resource, reusing the `format_level` rubric in
`agent_study/complexity.py`.

### 5. Ground capability docs in *measured* coverage, not advertised support
**Finding.** Parser docs claim broad support the benchmark refutes (ASE "supports"
Gaussian → 0/48). **Lesson.** Feed the harness's per-parser capability metadata from
**`benchmarks/results.csv`** (measured tool×format success) and keep it current —
the benchmark becomes the harness's honesty layer. **Change.** Generate the
capability docs/resources from benchmark results rather than hand-writing them.

---

## Tier 3 — system / learning

### 6. Design the escalation ladder — and learn from successful syntheses
**Finding.** The four compensation modes form a ladder: covered parser → combine
(oracle) → agent synthesizes a parser → compute. **Lesson.** When the agent
synthesizes a *working* parser for an L2/L3 format, **capture it back into the
harness** (PADS "From Dirt to Shovels" / DreamCoder library-learning): one-off
synthesis becomes reusable coverage, exactly where fixed tools fail. **Change.** A
contribution path for agent-synthesized parsers (with the validity signal as the
acceptance test).

### 7. Sandbox agent/parser execution — Turing-complete means it can hang
**Finding.** Real parsers hung indefinitely in C extensions during the benchmark;
hard-kill timeouts were required (`benchmarks/run.py`). **Lesson.** Any path that
runs synthesized or direct-import code (the point of dual-mode) needs **resource
bounds** — the moment arbitrary code runs, non-termination (the halting problem) is
a live failure mode. **Change.** Timeout/kill wrappers around parse/derive
execution.

### 8. Make failure modes first-class telemetry
**Finding.** Failure modes (wrong-parser, silent-empty, from-scratch) are currently
reconstructed post-hoc from transcripts (`agent_study/failure_modes.py`).
**Lesson.** Instrument the harness so it records which parser was tried,
empty-vs-success, and wrong-parser attempts at the tool boundary. **Change.**
Optional telemetry hook that dogfoods the `agent_study` metrics into the product and
lets the harness self-report the failure-by-level profile.

---

## Priority

If only three are done, do **1 (validity signal)**, **3 (normalization layer)**, and
**5 (measured capability docs)** — all three already have prototypes in the study
code, all three directly cut the agent's workload and failures, and together they
turn the benchmark from a critique into the harness's own quality machinery.
