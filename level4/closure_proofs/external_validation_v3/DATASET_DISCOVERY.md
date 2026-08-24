# Outcome-blind dataset discovery

Audit date: 2026-08-24. Twelve new UCI candidates were recorded before
filtering. Selection used provenance, license, chronology, raw structure,
missingness, causal modeling feasibility, residual diagnostics, projected
power, runtime, and domain coverage only. All are distributed by the UCI
Machine Learning Repository under CC BY 4.0.

| UCI | Candidate | Instances | Domain | Pre-outcome decision |
|---:|---|---:|---|---|
| 791 | MetroPT-3 | 1,516,948 | industrial compressor sensors | **PRIMARY A**; long real operational stream, distinct domain, projected floor 40 passes |
| 502 | Online Retail II | 1,067,371 | retail operations/demand | **PRIMARY B**; two chronological years, distinct domain, projected floor 40 passes |
| 482 | Parking Birmingham | 35,717 | parking occupancy | excluded: cross-sectional facility rows collapse to too few chronological blocks |
| 374 | Appliances Energy Prediction | 19,735 | household energy | excluded: materially overlaps the V2 Household success domain |
| 322 | Gas sensor array under dynamic mixtures | 4,178,504 | laboratory gas sensors | excluded: segmented controlled experiments, not one operational stream |
| 608 | Traffic Flow Forecasting | 2,101 | road traffic | excluded: projected chronological effective blocks below 40 |
| 560 | Seoul Bike Sharing Demand | 8,760 | bicycle demand | excluded: limited power and duplicates the historical Stage-E mobility regime |
| 601 | AI4I 2020 Predictive Maintenance | 10,000 | synthetic maintenance | excluded: synthetic rather than real/semi-real sequential evidence |
| 851 | Steel Industry Energy Consumption | 35,040 | industrial energy | excluded: adequate length but energy-domain overlap with V2 Household |
| 447 | Hydraulic System Condition Monitoring | 2,205 cycles | hydraulic test rig | excluded: segmented within-cycle profiles and too few independent cycles |
| 357 | Occupancy Detection | 20,560 | building sensors | excluded: only a short physical span and insufficient dependence-aware blocks |
| 849 | Power Consumption of Tetouan City | 52,417 | urban energy | excluded: adequate length but energy-domain overlap with V2 Household |

## Selected raw diagnostics

### A — MetroPT-3

- Official archive SHA-256: `aab991a970e58210de853bb8078ce0e63abb4d9412fdc5c79792dae3d8e1721a`.
- 1,516,948 parseable ten-second records; no malformed selected fields.
- 16,657 eligible 15-minute bins after requiring at least 72 raw readings.
- Coverage: 2020-02-01 through 2020-09-01; 249 observation-time gaps are
  retained as gaps, never imputed from future values.
- Pilot target: 15-minute mean oil temperature; causal ridge model only.
- Pilot calibration residual ACF1 0.926; excess kurtosis 17.37.
- Pilot values are raw/model diagnostics only; no reuse policy was run.

### B — Online Retail II

- Official archive SHA-256: `572e36277c2390fbfde10664750731e0a86f55e33470d91919085f0408e67bfb`.
- 1,067,371 transaction rows across two chronological worksheets.
- 1,044,416 positive, non-return rows; 22,956 zero/negative return rows excluded
  by the frozen gross-demand definition.
- 17,718 complete clock-hour bins from 2009-12-01 through 2011-12-09; hours
  without positive sales are explicit zeros.
- Pilot target: `log1p` positive unit demand; causal lag/calendar ridge model.
- Pilot calibration residual ACF1 0.006; excess kurtosis 6.60.
- Pilot values are raw/model diagnostics only; no reuse policy was run.

No backup task is registered. A failed scientific result is never replaced.
