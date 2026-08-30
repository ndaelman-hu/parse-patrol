# Agent sweep — scored summary (matched 30-task set; Claude Opus 4.8)

Total run records: 159. Matched set excludes GAMESS(3), oversized GPAW(1), context-sensitive(1), regular(0).

## Success % (CF/grammar n=4, mildly-CS n=26, Total n=30)

| arm | CF/grammar | mildly-CS | Total |
|---|---|---|---|
| NONE | 75% (3/4) | 50% (13/26) | 53% (16/30) |
| BARE | 100% (4/4) | 54% (14/26) | 60% (18/30) |
| DOCS | 100% (4/4) | 54% (14/26) | 60% (18/30) |
| FULL | 100% (4/4) | 58% (15/26) | 63% (19/30) |
| COMPLEXITY | 100% (4/4) | 58% (15/26) | 63% (19/30) |

## Failure modes + avg tool-calls

| arm | wrong_parser | silent_empty | from_scratch | unit_error | retry_loop | gave_up | avg_tools |
|---|---|---|---|---|---|---|---|
| NONE | 0 | 0 | 12 | 1 | 0 | 14 | 5.4 |
| BARE | 21 | 11 | 0 | 1 | 0 | 12 | 6.9 |
| DOCS | 19 | 11 | 1 | 1 | 0 | 12 | 7.1 |
| FULL | 21 | 11 | 2 | 0 | 0 | 11 | 7.4 |
| COMPLEXITY | 2 | 1 | 1 | 0 | 0 | 11 | 5.9 |
