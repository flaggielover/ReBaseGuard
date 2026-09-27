# Campaign errata (records that are frozen are not edited; corrections live here)

| id | item | correction | source |
|---|---|---|---|
| E1 | `config/QUARANTINE_AMENDMENT_1.json` `written_utc` "2026-09-27T18:40Z" | The amendment was committed at 2026-09-27T17:52:48Z (02:52:48 +0900). The recorded time is a hand-entered estimate and is **later** than the commit. For temporal integrity (G7), the commit time is authoritative. | REVIEW_GLOBAL_INTEGRITY_R1 F16 |
| E2 | `config/QUARANTINE_AMENDMENT_2.json` `written_utc` "2026-09-28T20:20Z" | Committed at 2026-09-27T20:13:39Z (05:13:39 +0900). The recorded date and time are wrong. The commit time is authoritative. | F16 |
| E3 | stream B `PROGRESS.md` times | These are step labels, not clock times. Commit times are authoritative. | F16 |
| E4 | stream A historical-read run, logged with class `HISTORICAL_READ` | Under TARGET_QUARANTINE allowed[1] the class should be `HISTORICAL_DECOMPOSITION`. The run's notes already disclosed this. `log_execution` now exempts both classes from LEAK_FLAG (`HISTORICAL_CLASSES`). The arithmetic stays within each supply (sub-review A). | F15 |
| E5 | commit subject of 6d0f0615 ("strictly positive", "result-free") | The corrected wording is in the stream D documents: strict for exact sups only; DRP-0 result-free, DRP-1 outcome-adaptive. | review D; F9 |
| E6 | commit message of 48392744 names erratum TPT-E1 | The document edit landed in 4f7cfe50. | coordinator |
| E7 | `ledger/OV_AUDIT.json` committed with PASS at 9db36e13 | That was stale once incidents were recorded. It is regenerated at the final HEAD, and its FAIL verdict names the recorded incidents. | F2 |
| E8 | `README.md` layout listed `streams/F_indep/` | That directory was never used and has been removed. The independent-implementation work lives in the streams (V3, the V_A/V_B verifiers, the C11 kernel cross-checks). | F17 |
