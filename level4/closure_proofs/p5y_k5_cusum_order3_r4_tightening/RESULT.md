# R4 result: QUALIFIED_FOR_GOVERNED_REAL_CELL_QUALIFICATION (non-scientific)

**Run.**
- Frozen protocol at `0a7ce2fd`, run once on rebaseguard-vultr-02 from a clean clone (0 porcelain lines),
  venv `/root/work/rbg-cusum-aux5-venv`, runner PID 221030.
- Started 2026-09-17T03:31:26Z. `RUN_COMPLETE.json` records result sha256 `3095a83d…` and 0 runner failures.
- `qualify_r4.py check` reproduces gates, counts, verdict and next step with no problems.
- Evidence: `evidence/qualification_r4/` (with `RUN_PROVENANCE.json`).
- Completion was detected from the marker files and the runner's exact `/proc/<pid>/cmdline`, not `pgrep -f`.

**Scope.** No real cell was evaluated, no `R'''` or `R⁽⁵⁾` value of any `(D,m)` was computed, no probe was run, and
the authorization registry is empty.

**This verdict qualifies infrastructure only. It authorizes nothing.** `REAL_CELL_QUALIFICATION = NOT_AUTHORIZED`.

## Gates

G01–G17 all PASS.

| suite | result |
|---|---|
| R3 wiring mutations (re-executed, R3 protocol) | **12/12**; C1 = C2/C3 = C6 = C7 = 0; payload sha256 identical to the frozen R3 evidence |
| R3 certificate-verifier mutations | **3/3** |
| R3 R⁽⁵⁾ mutations B01–B06 (verbatim) | **6/6** |
| R4 odd-certificate mutations O01–O04 | 4/4 (control rejected at margin −0.135) |
| R4 local-R⁽⁵⁾ mutations L01–L05 | 5/5 |
| first-cell soundness: 8 R4 fixtures + R3 FC1–FC5 | 0 violations |
| B01 self-test (FR4_01–03) | PASS |
| M5 independent Cauchy/acb cross-check | PASS (worst disagreement 0.0 at double precision; M5 dominates) |
| C_o0 independent cross-check X1–X4 | PASS (float margin min 0.0984 ≥ certified 0.0971; float odd norm 4.596 ≤ 5.360 ≤ 20.43) |
| evenness lemma, determinism, fail-closed (8/8), fences, runtime, R2/R3 regressions | PASS |

**B01 self-test detail.** On each tight-M5 fixture:
- correct method: 0 violations at 256 and 384 bits;
- B01: 8 violations, kinds exactly {M5, strategyB}, with no tower, anchor or point violation, identical at both
  precisions;
- sham `v.t` and sham `v.e + 0·v.o`: 0 violations.

## Certified constants

| constant | R3 | R4 | method |
|---|---:|---:|---|
| `C_o0` | 20.4322 | **5.3601** (margin ≥ 0.0971) | exact σ-odd block: positive reflected kernel on `{p ≥ m}`, polynomial supersolution (21/20, 1/2, depth 3) |
| `C_e0` | 469.7697 | 469.7697 (R3 artifact, replayed) | unchanged; float full resolvent 465.4, so this is essentially the true value (Perron 0.99782) |

- **Improvement:** 3.81×; class NEAR_NUMERICAL.
- **Float references (non-evidence):** odd-block sup resolvent 4.596; R3 coupling `E τ∧T_0` 16.56.

## Cell-0 forecast

Inputs are committed magnitudes and certified constants only; G factor 1, m = 1; `S* = 33.4066`, frozen from R3.

| quantity | value |
|---|---:|
| CERTIFIED_M5_R4 (local exact-parity anchoring, 12 iterations; trace 6.7e11 → 2.5556e9) | **2.5556e9** (R3: 4.71e10; 18.4×) |
| X1_SQUARED_OVER_2 | 25836889/200000000000000 |
| TRANSPORT_PENALTY_R4 | **330.1** (R3: 6079), transport label UNINFORMATIVE (≥ 100) |
| POINT_RADIUS_FORECAST (assumption A1) | **490.6** |
| STRATEGY_B_TOTAL_RADIUS_R4 | **820.8**: **MARGINAL** (S* < 820.8 ≤ 100 S*) |
| Strategy A cell radius with R4 C_o0 (info) | 3.85e4 |

- **Other m values:** totals are m = 2: 747.9, m = 3: 692.1, m = 5: 635.5.
- **G factors 10 and 100:** at most +5.6.

**Sensitivity grid (total radius, m = 1).** Only the starred cell is certified; all others are hypothetical.

| C_o0 \ M5 | model at this C_o0 | 1e10 | 1e9 | 1e8 | 1e7 |
|---|---:|---:|---:|---:|---:|
| certified 5.3601 (point 490.6) | **820.8\*** | 1782.5 | 619.8 | 503.5 | 491.9 |
| 10 (point 986.7) | 1577.0 | 2278.5 | 1115.9 | 999.6 | 988.0 |
| 6 (point 552.7) | 918.1 | 1844.5 | 681.9 | 565.6 | 554.0 |
| 4.68 non-certified (point 426.9) | 719.7 | 1718.7 | 556.1 | 439.8 | 428.2 |

**Dominant blocker: BOTH_COMPARABLE.** The penalty is 330.1 and the point radius 490.6, neither twice the other.
- The C_o0 lever is nearly exhausted: the certified value is 1.17× the float norm, and the point radius at 4.68 is
  still 426.9.
- The point radius is now set by `C_e0` (≈ 466, essentially its true value) and by the residual magnitudes.
- M5 below 1e8 would remove the penalty, but the total then stays ≥ 491.

## Caveats (stated, not hidden)

1. **Assumption A1 (R3).** The point radius assumes the future point run at e = 0 has residuals of the committed e0
   magnitudes. The real governed run must produce its own and must not reuse this forecast.
2. **The local M5 is not uniformly tighter.** On FR4_08 (near boundary, x₁ = 1/20) the local M5 (1.71e6) exceeds the
   R3 cell-anchored M5 (1.39e6). Both are valid, and a future run may take the minimum. The large CUSUM gain comes from
   avoiding the whole-cell drift in the anchors.
3. **Labels are not science.** MARGINAL is an enclosure-width label on the frozen scale, not a statement about the
   sign or size of `R'''`.

## Final status

- **Verdict:** QUALIFIED_FOR_GOVERNED_REAL_CELL_QUALIFICATION.
- **B1_NO_CERTIFIED_ORDER3_PRODUCER:** CLOSED_FOR_REAL_CELL_QUALIFICATION_ONLY.
- **REAL_CELL_QUALIFICATION:** NOT_AUTHORIZED.
- **Proposal:** prepared, NOT executed: `PROPOSAL_GOVERNED_FIRST_REAL_CELL.md`. The choice between option A (pure
  qualification, excluded from science) and option B (preregistered scientific probe) is left explicitly UNDECIDED.
- **NEXT_STEP (frozen rule):** PREPARE_GOVERNED_REAL_CELL_QUALIFICATION.
