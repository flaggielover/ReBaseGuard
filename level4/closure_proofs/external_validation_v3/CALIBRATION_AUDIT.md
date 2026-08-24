# Calibration and actual-power audit

Calibration is P0-only and precedes every confirmatory policy comparison. The
chronological split, train-owned model and scale, calibration-owned threshold,
and shared evaluation stream are frozen.

| Task | h | Target / achieved ARL | Dependence-aware 95% interval | Calibration blocks | Natural blocks | Event blocks | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| MetroPT-3 compressor | 2.098640831849 | 32 / 32.163043 | [26.467120, 39.021739] | 46 | 43 | 40 | PASS |
| Online Retail II | 2.855368398518 | 24 / 23.830508 | [18.652331, 29.991737] | 59 | 52 | 40 | PASS |

Both point estimates meet the 10% tolerance, both targets lie inside their
intervals, and every closure endpoint meets the unmodified floor of 40. The
campaign uses empirical calibration and dependence-aware blocks; it does not
claim iid Gaussian residuals or theorem confirmation.
