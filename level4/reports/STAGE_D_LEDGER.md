# Stage D — claim ledger

Every Stage D statement with its evidence status. Statuses follow
`level4/src/rebaseguard_level4/ledger.py`, whose guard rejects proof vocabulary
on any non-`PROOF_STATUSES` entry.

**Decision: `STAGE-D-PARTIAL`.**

| # | Statement | Status | Evidence |
|---|---|---|---|
| D-01 | `F_1'(0) = 1 − Gamma` (score identity, `m = 1`) | `FROZEN-PROVED` | Level 2C Lean; **inherited**, not re-derived |
| D-02 | `Gamma_CUSUM ∈ [3.9243482, 27.8493821]` | `FROZEN-CERTIFIED` | Level 1–3 Arb; **inherited** |
| D-03 | unique root of `F_1(e)+e` in `[1.028724, 1.044724]`, multiplier in `[0.1081, 0.8325]` | `RIGOROUS-CERTIFIED` | Stage B; **inherited**, not extended |
| D-04 | SR ARL0-matched to CUSUM(`h=5`): `A = 520.886134` | `CONFIRMATORY-NUMERICAL` | `calibration_d1.json`; rel err `−0.00045 ± 0.00174` |
| D-05 | `Gamma_SR = 17.3198 ± 0.0280` at `m = 1`; lower bound `> 2` | `CONFIRMATORY-NUMERICAL` | `d1_gamma.json` (D1.2) |
| D-06 | SR excess over CUSUM at matched ARL0 `= +1.4746 ± 0.0400` | `CONFIRMATORY-NUMERICAL` | `d1_gamma.json` (D1.3) |
| D-07 | SR replication is **two-detector**, not detector-independence | `METHOD-DEFINITION` | scope statement; two detectors only |
| D-08 | SR symmetric period-2 root candidate `e* = 1.036719 ± 0.001496` | `CANDIDATE` | `d1_4_sr_map.json`; resolution-limited |
| D-09 | CUSUM MC root interval lies inside the Stage B enclosure | `REPRODUCED` | consistency check on the simulator only |
| D-10 | `gamma_i` decays with lag; `gamma_0 = 15.8544` | `NEW-NUMERICAL` | `d2_gamma_m.json` (D2.1, descriptive) |
| D-11 | `sum_i gamma_i = E[T_tau^2] = ARL0` (Wald), ratio `0.99960` | `REPRODUCED` | `d2_gamma_m.json` |
| D-12 | `Gamma_m` decreases in `m` and crosses 2 within `m* ∈ [50, 75]` | `CONFIRMATORY-NUMERICAL` | `d2_gamma_m.json` (D2.2); ends `+108.6` / `−14.5` SE |
| D-13 | interpolated `m* = 72.19` `[71.85, 72.53]` | `NEW-NUMERICAL` | secondary to the bracket, which is primary |
| D-14 | `Gamma_m -> Gamma_inf = E[T_tau^2/tau] = 1.4037 ± 0.0013 < 2` | `NEW-NUMERICAL` | `d2_gamma_m.json` (D2.4). **Not a theorem, not an asymptotic result** |
| D-15 | `Gamma_m = (1/m) sum_i gamma_i` under convention A (blueprint claim) | `FAILED-TO-REPRODUCE` | refuted at 152 SE, `m = 250`; pinned by a test |
| D-16 | `Gamma_m^B = (1/m) sum_i gamma_i` | `METHOD-DEFINITION` | algebraic identity of convention B, not a result |
| D-17 | Stage A's minimum dwell makes its `m > 1` map different from Stage D's | `METHOD-DEFINITION` | `CORRESPONDENCE_AUDIT.md` A1; equal at `m = 1` |
| D-18 | `F'_{rho,m}(0) = rho(1 − Gamma_m)` at `m > 1` | **`FAILED`** | D2.3: 0/8 at the primary step `h = 0.05` |
| D-19 | the D2.3 discrepancy is `O(h^2)` truncation, order `p = 1.938`; Richardson within `0.40` SE | `NEW-NUMERICAL` | **diagnosis only**; does not alter D-18 |
| D-20 | `F'(0)` matches `1 − Gamma` per detector at `m = 1` (`−16.23 ± 0.11`, `−14.91 ± 0.11`) | `NEW-NUMERICAL` | consistency check; **not** a substitute for D2.3 |
| D-21 | the `Gamma_m = 2` crossing has **no** observable operational counterpart | **`NEW-NUMERICAL` (negative result)** | D2.5: 0/4 metrics peak at `m*`, 4/4 monotone |
| D-22 | alarm alternation persists above `m*` (`−0.456` at `m = 100`, `Gamma_m = 1.776`) | `NEW-NUMERICAL` | `d2_5_bridge.json` |
| D-23 | `m*` is a local-stability boundary of the **deterministic** conditional-mean skeleton at `e = 0` | `METHOD-DEFINITION` | `rho_c = 1 <=> Gamma_m = 2`; **not** an operational transition |
| D-24 | D3 regularity assumptions written and labelled before simulation | `METHOD-DEFINITION` | `D3_REGULARITY.md` (`9eafbcd2…`) |
| D-25 | A1 (differentiation under the expectation), non-Gaussian | **`OPEN`** | UNPROVED for every non-Gaussian family |
| D-26 | A4 (square-integrability of the stopped score sum) | **`OPEN`** | check too low-powered (4 batches) to speak |
| D-27 | `E[psi^2] = E[psi']` for all six families | `NEW-NUMERICAL` | quadrature, agreement to 4 decimals |
| D-28 | `Gamma_psi` lower bound `> 2` for 6/6 ARL0-matched families | `CONFIRMATORY-NUMERICAL` | `d3_nongaussian.json` (D3.2, frozen estimand) |
| D-29 | under `Gamma_psi/E[psi']`, 5/6 families exceed 2 | `NEW-NUMERICAL` | assumption A5 |
| D-30 | **t3 interpretation** | **`AMBIGUOUS`** | `2.5980` PASS vs `1.2990` FAIL; neither estimand selected |
| D-31 | naive Gaussian-form `Gamma_T` (`99.5586` at t3 vs `2.5980`) | **`DIAGNOSTIC ONLY`** | D3.3; never evidence |
| D-32 | the Gaussian stopped-sum identity does **not** export to heavy-tailed families | `NEW-NUMERICAL` | inference **from** D-31's failure |
| D-33 | D3 establishes numerical robustness over six families | `METHOD-DEFINITION` | **not** distribution-free, **not** universal |
| D-34 | general location-family theorem | **`OPEN`** | proof obligations not closed (D-25, D-26) |
| D-35 | D4 stability map | **`BLOCKED`** | gate requires D2 to survive; D2.3 failed |
| D-36 | rigorous SR certificate | **`OPEN`** | not started; D1.4 does not substitute |
| D-37 | invariant law of the noisy recursion | **`OPEN`** | unchanged since Stage B |
| D-38 | adversarial suite 12/12; A11 failed first run, diagnosed, fixed | `NEW-NUMERICAL` | `adversarial_d.json`, `FAILURE_DIAGNOSES.md` F2 |
| D-39 | protocol hash unchanged across all campaigns | `METHOD-DEFINITION` | A12: `925adecf…` |
| D-40 | no frozen Stage A/B/C/C.1 or Level 1–3 artifact modified | `METHOD-DEFINITION` | no file outside `stage_d/` newer than the freeze |

## Forbidden wordings (none appear in Stage D artifacts)

"detector-independent" · "distribution-free" · "universal" · "robust in general"
· "first stability boundary" · "repeated SR is novel" · any Stage D result called
"certified" or "proved" · `m*` as an operational phase transition · a general
location-family theorem.
