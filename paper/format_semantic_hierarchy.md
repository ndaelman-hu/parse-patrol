# Two hierarchies: source-format syntax vs. semantic depth — and why agents must compensate

This note grounds the power-gap thesis in two orthogonal hierarchies and the way
they interact:

- **Axis A — syntactic complexity of the *source format*** (a Chomsky-hierarchy
  ordinal L0–L3), classified per code with evidence from the actual files.
- **Axis B — structural depth of the *target semantic concept*** (S0–S3),
  grounded in the [`nomad-simulations`](https://github.com/nomad-coe/nomad-simulations)
  schema classes.

The claim: a **fixed parser** occupies a bounded automata class (regex → regular;
stateful scanner → regular+counting; grammar-backed reader → context-free). The
data it must recover lives at some (format-level ⊗ semantic-depth) coordinate. A
parser succeeds only where that coordinate sits at or below its power ceiling. The
**coding agent is Turing-complete** (it writes and runs code), so its role is to
*compensate* for the gap — and, at the top of Axis B, to **compute concepts the
source file never contained at all**, which no parser can do in principle.

---

## Recap: parsers by Chomsky class

| Tool | Mechanism | Power ceiling |
|---|---|---|
| custom Gaussian parser | regexes + light line-state | **regular** (Type-3) |
| cclib / ASE / iodata *text* readers | stateful line scanners | **regular + counting** (finite-state + counters; ad-hoc mildly-CS) |
| iodata / ASE *grammar-backed* readers (XML/JSON/`.fchk`/`.molden`) | format grammars / combinators | **context-free** (Type-2) |
| the coding agent | arbitrary Python (+ chain-of-thought) | **Turing-complete** (Type-0) |

A parser fails when the format's required class exceeds its ceiling; the agent
compensates by climbing the hierarchy.

---

## Axis A — Source-format syntactic complexity (16 codes, evidenced)

Ordinal rubric:

- **L0 — grammar-defined / structured** (properly nested; context-free): XML, JSON,
  `.fchk`, `.molden`. Also **binary containers** with a fixed grammar (HDF5/netCDF/
  pickle) — machine-parseable *if* you have the format's reader, otherwise opaque.
- **L1 — line-regular**: fixed tokens per line, no counting (regular).
- **L2 — free-form log with count-agreement**: a header declares *N* atoms, then *N*
  lines follow; repeated blocks where the last must be taken. The counting/agreement
  dependency a lone regex cannot enforce → *mildly context-sensitive*.
- **L3 — cross-referential / multi-file**: values defined in one file/section and
  combined in another (context-sensitive).

The mainfile fixes the *headline* level; full extraction often pulls an entry up to
L3 (auxiliary/binary companion files). Evidence below is the literal structural
signature of each code's primary output in the corpus.

| Code | Mainfile | Level (mainfile) | Evidence from the file | Entry-level pull |
|---|---|---|---|---|
| **VASP** | `vasprun.xml` | **L0** | XML-nested (`<modeling><calculation>…`) | OUTCAR (L2), POSCAR (L2) present |
| **GPAW** | `gs_gw_nowfs.gpw` | **L0-binary** | file is **binary** (structured container) | `.txt` log is L2; `.json` is L0 |
| **Gaussian** | `H2O.log` | **L2** | count-decl `NAtoms= 3 …`; repeated "Standard orientation" blocks (take last) | `.fchk`/`.chk` companions (L0/binary) |
| **CASTEP** | `case.castep` | **L2** | count-decl `Total number of ions in cell = 12` | `.castep_bin` (binary), `.bands`, `.cell`, `.check` → **L3/binary** |
| **Crystal** | `*.out` | **L2** | count-decl `NUMBER OF ATOMS PER SUPERCELL 18` | single-file |
| **ONETEP** | `*.out` | **L2** | count table header `Symbol Natoms Nngwfs Nprojs` | single-file |
| **FHI-aims** | `aims.out` | **L2** | free-form SCF log; self-contained | `control.in`/`geometry.in` (L1 inputs) |
| **CP2K** | `cp2k.out` | **L2** | free-form log | `.inp` input (L1) |
| **GAMESS** | `*.out` | **L2** | free-form log | `.inp` input |
| **NWChem** | `output.out` | **L2** | free-form log | `.nw` input |
| **ORCA** | `*.out` | **L2** | blocks incl. `FINAL SINGLE POINT ENERGY` (take last) | `.inp` input |
| **Octopus** | `output.out` | **L2** | free-form log | **k-resolved split files** `.k1_x/.k1_y/.k1_z` → **L3** |
| **exciting** | `INFO_GS.OUT` | **L2** | count-decl `Total number of atoms per unit cell : 8` | `input.xml` (L0) + many `.OUT`/`.dat` → **L3** |
| **LAMMPS** | `log.lammps` | **L1–L2** | thermo tables (line-regular L1); data files carry atom counts (L2). *Classical MD, not ab initio.* | `.lmp` data, job scripts |
| **WIEN2k** | `ZnSe_ZB.scf` | **L3** | needs the companion `.struct` (defines cell + atoms) which the `.scf` references/reports against | intrinsically 2-file |
| **ABINIT** | `graphene.out` | **L3** | multi-file: `.files` maps I/O units, `.in` defines the run, `.nc` (**netCDF binary**) holds arrays; cross-referential | `.psp8` pseudopotentials, `.win` |

**Distribution.** L0: VASP (+GPAW binary). L2 (the bulk): Gaussian, CASTEP, Crystal,
ONETEP, FHI-aims, CP2K, GAMESS, NWChem, ORCA, Octopus, exciting-mainfile. L1–L2:
LAMMPS. L3: WIEN2k, ABINIT — and CASTEP/Octopus/exciting once binary/split companion
files are required. This refines the coarse extension-based rubric used in the
benchmark re-cut (which lumped most codes as L2): the *evidence* is the count-agreement
declaration (L2), the XML nesting (L0), the binary container (L0-binary), or the
multi-file dependency (L3).

---

## Axis B — Semantic-concept depth (nomad-simulations schema)

The target schema is a tree: **`Simulation` → {`Program`, `ModelSystem`,
`ModelMethod`, `Outputs`}**. Below, each branch's concepts are ordered by **structural
depth S0–S3**, defined by their *footprint in a source file* (which is what governs
extraction difficulty):

- **S0 — scalar**: a single number/string on a line.
- **S1 — per-particle vector/array**: one value per atom (needs the count-agreement of Axis-A L2).
- **S2 — variable-indexed array**: a field over a grid (k-points, energies, bands, modes) — the schema models these with `variables.py`. Needs structured numeric blocks, often in binary/auxiliary files.
- **S3 — cross-referenced / graph / derived-not-printed**: assembled across sections/files, or *computed* and typically absent from the raw output.

### `ModelSystem` — the structure (`model_system.py`)

| Depth | Concept (schema class · attribute) | Note |
|---|---|---|
| S0 | `total_charge`, `total_spin_multiplicity`, `type`, `dimensionality`, `n_particles` | scalars |
| S0 | `Cell`/`Representation`: `lattice_vectors` [3×3], `periodic_boundary_conditions` [3] | small fixed arrays |
| S1 | `positions` [N×3], `velocities` [N×3]; `particle_states` → `AtomsState` (per-atom) | per-atom (L2 count-agreement) |
| S3 | `ChemicalFormula`: `hill`, `iupac`, `reduced`, `anonymous` | **computed** from species, not printed |
| S3 | `symmetry` → `GlobalCrystalSymmetry`: `space_group_number`, `wyckoff_letters`, `lattice_type`, `hall_symbol`; `LocalCrystalSymmetry`: `site_symmetries` | usually **derived via spglib**, absent from output |
| S3 | `bond_list`/connectivity; `sub_systems` tree; `AlternativeRepresentation` (primitive/conventional/`supercell_matrix`) | graph / derived |

### `ModelMethod` — the physics (`model_method.py`)

| Depth | Concept (schema class · attribute) | Note |
|---|---|---|
| S0 | `ModelMethodElectronic.is_spin_polarized`; `DFT.jacobs_ladder`, `reference_form` | scalars/flags |
| S2/S3 | `XCFunctional` → `XCComponent`: `libxc_id`, `family`, `fraction_exact_exchange`, `functional_key` | **provenance normalization**: map a code's XC label → LibXC components |
| S3 | `HubbardInteractions`: `u_interaction`, `j_hunds_coupling`, `slater_integrals`, `orbitals_ref` | matrices + references |
| S3 | `TB`/`Wannier`/`SlaterKoster`; `HF`; `PerturbationMethod` (MP); `CC`; `CI`; multireference `ActiveSpace`/`MultireferenceSCF` (CASSCF); excited-state `GW`/`BSE`/`TDDFT`/`Screening`; `DMFT` | deep method provenance scattered through free-form logs; heavy `*_ref` cross-referencing |

### `Outputs` — the results (`outputs.py` + `properties/`)

| Depth | Concept (schema file · class) | Note |
|---|---|---|
| S0 | `energies.py` (`TotalEnergy`, Fermi level); `band_gap.py` (`ElectronicBandGap` value) | a number on a line — reachable by a **regular** parser in any code |
| S1 | `forces.py` (per-atom [N×3]); atomic charges; per-atom moments | per-atom arrays (L2) |
| S2 | `electronic_eigenvalues.py`, `band_structure.py`, spectral profiles / density-of-states (`spectral_profile.py`), `permittivity.py`, `greens_function.py`, `hopping_matrix.py`, `fermi_surface.py`, `molecular_orbitals.py`; vibrational modes | arrays over `variables.py` grids (k, energy, band, mode) — frequently in **binary/auxiliary** files |
| S3 | `thermodynamics.py` (ensemble-derived), workflow-level aggregates; anything requiring joining method+system+outputs | cross-section assembly |

---

## The interaction — extraction reachability = (format level ⊗ semantic depth)

A concept is reachable by a parser of power *P* only if its **footprint** — set by
*both* the format level (Axis A) and the concept depth (Axis B) — sits at or below
*P*. Sketch of the reachability frontier:

| | S0 scalar (energy, gap) | S1 per-atom (geometry, forces) | S2 grid array (bands, DOS, ε(ω)) | S3 cross-ref / derived (symmetry, XC provenance, formula) |
|---|---|---|---|---|
| **L0/L1 format** | trivial (regular) | easy (grammar/CF) | reachable if grammar covers arrays | needs join/compute |
| **L2 format** | regular OK | **needs counting** (many parsers already fail here) | needs stateful block parsing; often binary → parser blind | needs join/compute |
| **L3 / binary format** | needs the right file | cross-file / binary decode | **binary/aux decode** (`.gpw`, `.nc`, `.castep_bin`) | full assembly |

Two lessons drop out. (1) The **same semantic concept has different extraction cost
in different codes**: `TotalEnergy` (S0) is a line in every log — a regex gets it
anywhere — whereas an `ElectronicBandStructure` (S2) is a k-indexed array that VASP
exposes in `vasprun.xml` (L0, parseable) but GPAW hides in a `.gpw` binary and Octopus
splits across `.k1_*` files (L3) — unreachable to a text scanner. (2) The frontier is
**not** a single Chomsky level; it is the *join* of format syntax and concept depth.

### The four ways an agent compensates

Because the agent is Turing-complete, it can move the frontier — and this is the
precise content of "agents compensate for lack of parser power":

1. **Climb the syntactic class.** Write a stateful/recursive parser for L2 count-
   agreement and L3 blocks, or a binary decoder for `.gpw`/`.nc`/`.castep_bin` — parsing
   a language above any fixed tool's ceiling.
2. **Cross-file join.** Assemble a concept from several files (`.struct`+`.scf`;
   `.in`+`.files`+`.nc`; `input.xml`+`INFO.OUT`) — an operation a single-file parser has
   no way to express.
3. **Semantic normalization.** Map heterogeneous code output onto the schema:
   unit conversion, energy-term bookkeeping, and XC-label → LibXC-component provenance
   (`XCFunctional`/`XCComponent`) — a *translation*, not a parse.
4. **Derive concepts absent from the file (the strongest form).** Compute S3 schema
   fields the source never printed: run spglib for `GlobalCrystalSymmetry`, canonicalize
   `ChemicalFormula` (hill/iupac/anonymous), infer `bond_list`, or compute a `band_gap`
   from eigenvalues. **A parser categorically cannot produce data that is not in its
   input; a coding agent can.**

Modes 1–2 are climbing Axis A; modes 3–4 are climbing Axis B. The benchmark's
power-gap result is Axis A alone; this note shows the second axis is where the agent's
advantage becomes *qualitative* rather than merely *more robust* — it is the argument
for why an agentic grounding layer is not just a nicer parser but a strictly more
powerful class of machine.

---

## Which formalism for which axis? Chomsky for the bytes, graph-complexity for the chemistry

The Chomsky (string) hierarchy fits **Axis A** because output *files are strings*.
It is the *wrong* tool for **Axis B**: a molecule is a graph, a crystal is a
periodic structure, a reaction is a graph rewrite — none are strings. Better-fitting
formalisms for the chemical-structure axis:

- **Graph grammars / double-pushout (DPO) graph rewriting** — the chemistry-native
  analogue of a formal grammar. Concrete instance: **MØD** (Andersen, Flamm, Merkle
  & Stadler, *A Software Package for Chemically Inspired Graph Transformation*,
  arXiv:1603.02481): molecules are labelled graphs, reactions are direct
  derivations, and graph *languages* are directed hypergraphs.
- **A designed molecular formal language: SELFIES** (Krenn, Häse, Nigam, Friederich
  & Aspuru-Guzik 2020, *Mach. Learn.: Sci. Technol.*, arXiv:1905.13741) — a formal
  grammar in which *every* string is a valid molecule, vs. SMILES (~context-free with
  ring-closure **cross-references** → mildly context-sensitive and fragile). Direct
  evidence that a *designed* formal language beats an ad-hoc one for a chemical object.
- **Graph descriptive complexity** — **Courcelle's theorem** (1990): MSO-definable
  graph properties are decidable in linear time on graphs of **bounded treewidth**.
  Treewidth / clique-width *grade* the structural hardness of a molecular or crystal
  graph in a way the string classes cannot.
- **Empirical bridge to failure**: Dziri et al. (*Faith and Fate*, NeurIPS 2023,
  arXiv:2305.18654) model compositional tasks as **computation graphs** and show
  transformers fail as **graph width and depth** grow — i.e. a *graph-structural*
  hardness axis that predicts agent failure on structured targets better than a
  string level.

**Consequence.** Our S3 concepts — molecular connectivity, `GlobalCrystalSymmetry`
(space group / Wyckoff), formula canonicalization — are *graph-reconstruction* or
*group-theoretic computations*, **not string parses**. That is exactly why they sit
in "derive/compute" (compensation mode 4). The two-axis model is therefore really
**two hierarchies under two formalisms**: Chomsky over the bytes (Axis A),
graph-complexity over the chemistry (Axis B).

## Provenance

- Axis-A levels: structural signatures extracted from the corpus mainfiles
  (`benchmarks/dataset.json`; evidence strings quoted above are literal from the files).
- Axis-B classes/attributes: `nomad-simulations` schema packages
  (`model_system.py`, `model_method.py`, `outputs.py`, `properties/*`,
  `variables.py`) — https://github.com/nomad-coe/nomad-simulations.
- Framing: `paper/complexity_framing.md`; benchmark re-cut: `agent_study/complexity_report.md`.
