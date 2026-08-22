# Stage E — data provenance

Raw files are **not redistributed** in this repository. They are fetched into
`level4/stage_e/data/_cache/` (gitignored) by `reproduce.sh`; only checksums,
dimensions and manifests are committed. Machine-readable form:
`results/data_manifest.json`.

Retrieval date: **2026-08-22**.

---

## Task A — Electricity / Elec2

| | |
|---|---|
| Name | `electricity-normalized` (Elec2) |
| Source | OpenML dataset id **151**, file id 2419 (`https://api.openml.org/data/v1/download/2419/electricity-normalized.arff`) |
| Version | OpenML normalized ARFF, Weka `Normalize -S1.0 -T0.0` + `ReplaceMissingValues` |
| License | Public, OpenML redistribution terms; originally NSW/Australian electricity market data (Harries 1999) |
| Raw size | 3,092,013 bytes, sha256 `2d86fbc74c69a5c0…` |
| Raw dimensions | 45,312 rows × 9 attributes |
| Temporal ordering | half-hourly, 1996-05-07 → 1998-12-05 |
| Preprocessing | `day` → sin/cos; `date` dropped as a feature; 8 features retained |
| Split | train `[0, 13594)` · calibration `[13594, 22656)` · evaluation `[22656, 45312)` |
| Restrictions | not redistributed here; fetched at reproduce time |

### ⚠ Ordering anomaly — recorded because it changes the loader

The `date` column of this ARFF is **not globally monotone**. It contains **five
backward jumps**:

| row | date before → after | drop | day | period |
|---|---|---|---|---|
| 25487 | 0.500111 → 0.465112 | 0.034999 | 7→1 | 1.0→0.0 |
| 34895 | 0.884695 → 0.875979 | 0.008716 | 7→1 | 1.0→0.0 |
| 35231 | 0.902526 → 0.885049 | 0.017477 | 7→1 | 1.0→0.0 |
| 36239 | 0.995443 → 0.885978 | 0.109465 | 7→1 | 1.0→0.0 |
| 40703 | 1.000000 → 0.867307 | 0.132693 | 2→3 | 1.0→0.0 |

Every jump sits at a day boundary where `period` wraps `1.0 → 0.0`. Elec2 is a
sequential half-hourly recording, and **file row order is authoritative**;
sorting by `date` would scramble it. The loader therefore uses row order and
verifies the half-hourly cycle instead: `period` must advance `0..47` and wrap.
A first implementation asserted monotone `date` and correctly failed, which is
how this was found.

---

## Task B — UCI Air Quality

| | |
|---|---|
| Name | Air Quality |
| Source | UCI ML Repository id **360** (`https://archive.ics.uci.edu/static/public/360/air+quality.zip`) |
| Citation | De Vito et al., *Sens. Actuators B*, 2008 |
| License | CC BY 4.0 (UCI) |
| Raw size | 1,543,989 bytes zip, sha256 `d4a64013fb385288…`; `AirQualityUCI.csv` sha256 `13277ae5d858…` |
| Raw dimensions | 9,357 hourly records × 15 fields |
| Temporal ordering | hourly, 2004-03-10 18:00 → 2005-04-04 |
| Format quirks | `;` separated, `,` decimal separator, `-200` = missing |
| Exclusions | rows where any used sensor channel or the target is `-200` / unparsable → **8,991 usable** (fixed rule, outcome-independent) |
| Target | `C6H6(GT)` reference-analyser benzene |
| Features | `PT08.S1(CO)`, `PT08.S2(NMHC)`, `PT08.S3(NOx)`, `PT08.S4(NO2)`, `PT08.S5(O3)`, `T`, `RH` |
| Split | train `[0, 2697)` · calibration `[2697, 4495)` · evaluation `[4495, 8991)` |

The dataset documents **genuine metal-oxide sensor drift** over the recording
year, which is why it is used as the sensor/industrial task.

---

## Task C — UCI Bike Sharing

| | |
|---|---|
| Name | Bike Sharing Dataset (`hour.csv`) |
| Source | UCI ML Repository id **275** (`https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip`) |
| Citation | Fanaee-T & Gama, *Prog. Artif. Intell.*, 2013 |
| License | CC BY 4.0 (UCI) |
| Raw size | 279,992 bytes zip, sha256 `b70182d0d0508e9a…`; `hour.csv` sha256 `e03de4ee4ef4…` |
| Raw dimensions | 17,379 hourly records × 17 fields |
| Temporal ordering | hourly, 2011-01-01 → 2012-12-31; `instant` verified strictly increasing |
| Target | `log1p(cnt)` |
| Features | season, yr, holiday, workingday, weathersit, temp, atemp, hum, windspeed, hour sin/cos, month sin/cos |
| **Leakage exclusion** | `casual` and `registered` are **excluded**: they sum exactly to `cnt` |
| Split | train `[0, 5214)` · calibration `[5214, 8690)` · evaluation `[8690, 17379)` |

---

## Common discipline

* Splits are strictly chronological and contiguous; verified by test.
* Models and all standardisation constants are fitted on the **reference block
  only**; the detector threshold on the **calibration block only**.
* Nothing is fitted on the evaluation stream. No model or threshold is revisited
  after any monitoring outcome.
* Provenance is established for all three datasets, so all three are eligible
  for Stage E closure.
