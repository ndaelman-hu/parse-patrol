# Submission checklist — ML4Molecules (NeurIPS 2026) workshop

**Deadline: 29 August 2026 (AOE)** — submit via OpenReview. Non-archival, double-blind, ≤5 content pages, ≤50 MB.

## Bundle contents (this folder)
- `main.tex` — the paper (anonymized, `[dblblindworkshop]` option set).
- `neurips_2026.sty` — official style file (from the NeurIPS 2026 template zip).
- `refs.bib` — bibliography.
- `neurips_2026.tex`, `checklist.tex` — official examples; **not needed** (the NeurIPS checklist is not required for this workshop). Safe to ignore/delete.

## Compile (pick one)
**Fastest — Overleaf:** New Project → Upload → add `main.tex`, `neurips_2026.sty`, `refs.bib` → set main document to `main.tex` → Recompile. Download PDF.

**Local (needs TeX Live):**
```
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

## Verify before upload
- [ ] **Page count ≤ 5** content pages (references + appendix don't count). Current draft is ~4 pages of text + 3 tables; if it spills over 5, trim candidates below.
- [ ] **Anonymized**: title page shows "Anonymous Author(s)". Do **NOT** add the `[final]` option (that de-anonymizes). Scanned clean — no names/affiliations/repo/tool-name/acknowledgments in `main.tex` or `refs.bib`.
- [ ] **Bibliography renders** (7 refs; author-year via natbib/`plainnat`).
- [ ] File size ≤ 50 MB (trivially true — no heavy figures).

## If over 5 pages — trim in this order
1. Shorten §1 Introduction by one paragraph.
2. Fold Table 2 (outcome breakdown) into a sentence, keeping only the "1077/1104 silent-empty" number.
3. Compress the "Relation to prior work" paragraph in §4.
4. Move the Limitations paragraph tighter / into a footnote.

## Data provenance (all numbers are real, from this repo)
- Tables 1–2 + failure taxonomy: `benchmarks/report.md` (harness `benchmarks/`).
- Table 3 (complexity re-cut): `agent_study/complexity_report.md`.
- Corpus: `benchmarks/dataset.json` (52 entries, 16 codes, 1104 files).

## Two author decisions to make before submitting
- **Reproducibility link.** The paper says data/mainfiles are "frozen for reproducibility" but includes **no URL** (safest for double-blind). If you want a link, use an anonymized mirror (e.g. anonymous.4open.science) — do **not** paste the real GitHub URL (de-anonymizes).
- **NOMAD citation.** `ghiringhelli2023metadata` (the materials-database metadata paper) is cited in the third person, which is standard and acceptable even though it is consortium-adjacent to the likely authors. Keep it unless you'd rather generalize the sentence.

## Framing note (why the paper reads science-first, not tooling)
The workshop centers molecular ML; a parser paper is one layer below. The draft is
written to fit the explicitly-solicited **"benchmarks / negative results /
evaluation of scientific agents and their components"** and **"grounding LLMs via
chemical databases"** lanes: the spine is the *scientific consequence* of silent
grounding failure, and the intellectual core is the **power-gap law**, not a bug
report. This is a legitimate but not centerpiece fit; it is a free-roll on a
non-archival venue. The genuinely science-central version (the agentic-scaffold
ablation) is future work.
