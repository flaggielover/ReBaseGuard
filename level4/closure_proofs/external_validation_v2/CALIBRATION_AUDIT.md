# Calibration and actual power audit

All values were generated after the execution checkpoint and before any
confirmatory P0/P1/P2 evaluation comparison. Calibration used the chronological
calibration block under P0 only. The task threshold is fixed for every policy.

| Task | h | Target / achieved ARL | 95% block interval | Calibration blocks | Natural week blocks | Event blocks | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| A — Household power | 5.2549566185 | 240 / 239.2079 | [176.8116, 310.0512] | 25 | 99 | 20 | PASS |
| B — Metro traffic | 5.2396056046 | 60 / 60.1818 | [43.0604, 81.5253] | 24 | 120 | 20 | PASS |
| C — Beijing PM2.5 | 4.9094082426 | 60 / 59.5119 | [47.0229, 72.7857] | 21 | 102 | 20 | PASS |

Each point error is below 1%, each target lies inside its interval, and every
endpoint class meets the unmodified 20-block floor. The backup was not
activated. Calibration residuals remain misspecified relative to iid Gaussian
theory: Metro retains ACF1 0.724 and Beijing excess kurtosis 12.87. The campaign
therefore uses empirical calibration and the frozen dependence-aware inference;
it does not claim theorem confirmation.

Canonical record: `results/gates.json`.
