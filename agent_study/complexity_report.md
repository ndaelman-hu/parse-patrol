# Benchmark re-cut by format complexity (power-gap test)

Parser success rate grouped by `format_level` (L0 structured → L3 cross-referential). Prediction: success falls as level rises, and structured L0 formats are handled far more reliably than free-form logs. Rubric: `agent_study/complexity.py`; framing: `paper/complexity_framing.md`.

## Mainfile success by level × parser

| Level | ase | cclib | gaussian | iodata | files |
|---|---|---|---|---|---|
| L0 | 100.0% (4/4) | 0.0% (0/4) | 0.0% (0/4) | 0.0% (0/4) | 4 |
| L2 | 18.2% (8/44) | 25.0% (11/44) | 9.1% (4/44) | 6.8% (3/44) | 44 |
| L3 | 0.0% (0/3) | 0.0% (0/3) | 0.0% (0/3) | 0.0% (0/3) | 3 |

## Oracle (any parser succeeds) by level — mainfiles

| Level | Solved by ≥1 parser |
|---|---|
| L0 | 100.0% (4/4) |
| L2 | 43.2% (19/44) |
| L3 | 0.0% (0/3) |

## All-files success by level × parser

| Level | ase | cclib | gaussian | iodata | files |
|---|---|---|---|---|---|
| L0 | 11.8% (4/34) | 0.0% (0/34) | 0.0% (0/34) | 0.0% (0/34) | 34 |
| L1 | 36.4% (8/22) | 0.0% (0/22) | 59.1% (13/22) | 63.6% (14/22) | 22 |
| L2 | 2.6% (26/1009) | 16.8% (170/1009) | 1.3% (13/1009) | 10.1% (102/1009) | 1009 |
| L3 | 12.8% (5/39) | 0.0% (0/39) | 0.0% (0/39) | 0.0% (0/39) | 39 |

