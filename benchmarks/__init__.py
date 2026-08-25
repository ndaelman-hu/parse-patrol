"""Parse-patrol parser-reliability benchmark.

A reproducible benchmark measuring how reliably the community parsers wrapped by
parse-patrol (ASE, cclib, custom Gaussian, iodata) extract structured data from
real computational-chemistry files harvested from the NOMAD repository.

Pipeline:
    dataset.py  -> freezes the corpus into dataset.json  (single network step)
    success.py  -> field-level success verdicts per parser
    run.py      -> runs every parser over every file      (fully offline)
    report.py   -> aggregates results.csv into report.md

The benchmark is a *measurement*: parser failures are the contribution, so the
parsers themselves are never modified here.
"""
