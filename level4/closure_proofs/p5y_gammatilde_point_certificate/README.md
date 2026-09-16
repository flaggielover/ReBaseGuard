# P5Y — GammaTilde point certificate (CUSUM m = 3, 5)

A governed successor to the reuse audit `p5y_gammatilde_sign_audit` (`323e2b8f`, left unchanged). Its one
scientific purpose is to certify the sign of `R_m'(0)` at **e = 0 exactly** for CUSUM `m = 3, 5`. By P1-T1,
`R_m'(0) = 1 − GammaTilde_m`, so this is the premise `GammaTilde_m > 1`. The run also produced m = 2 as a
control and m = 1 as a non-target control.

The work stays separate from the K5 order-3 work: no signed R''' object, no cells 148/305/309, no order-3
campaign, no K1 record or CUSUM composite modified, no AWS/PS1, and no origin/main.

```bash
python3 -B code/adjudicate_point.py verify           # POINT_ADJUDICATION_VERIFIED <sha256> (recompute + temporal integrity)
python3 -B qualification/test_point_core.py          # ok 12
python3 -B code/qualify_point.py --replay qualification/evidence/replay-cell0.json \
    --point-e0 qualification/evidence/point-e0.json --unit-tests-passed --out /tmp/v.json   # PASS
```

## Method

The evaluator is the frozen K1 CUSUM midpoint path, called unedited:

1. `order2.Order2Certifier(cell).prepare()` and `all_residuals()`
2. `aux_propagate.cell_dag(cert, "delta_mid")`
3. `propagate.enclosures`
4. `assembly.assemble(m, D, W[1])`

It runs on the degenerate cell `{0}` (`left = right = e0 = 0`, `rho = 0`), with `C_upper` taken from frozen cell 0.
Cell 0 is `[0, 2e0]` and its `C_evaluation` is exactly 0. Each midpoint residual is certified at `e = 0` exactly.

The method uses no whole-cell R2/R3 widening, no refine2, no auxiliary order-3 evidence, no K5-B recurrences,
no Monte Carlo and no finite differences.

The run is bound to:

- producer identity `3692d0fe`, manifest v3 `b55a2da1` and runtime contract `bc75c9ea`, verified live at the
  initial and final gates;
- wrapper and source pins in `protocol/POINT_PROTOCOL.json` (sha256 `2a761357…`);
- a clean SciPy guard;
- `rebaseguard-vultr-02` and the frozen venv.

## Timeline (temporal integrity, verified by `adjudicate_point.py verify`)

| Step | Commit | Content |
|---|---|---|
| Protocol freeze | `aca34248` | Gates, precision ladder 256→384→512, retry policy, controls, CPU ceilings, wrapper and source hashes. No run had happened. A pre-freeze dry gate check (no kernel arithmetic) passed. |
| Qualification | `e7a9fbb0` | **PASS** (see below) |
| Science rung 256 | `6c8f64bc` | Started at epoch 1789555705, after the qualification commit time. Scientific hash `a446beeb`. |
| Adjudication | this commit | `adjudication/ADJUDICATION.json` |

Qualification checks:

- **Q1:** 12 fail-closed unit tests: manufactured positive/negative/zero/near-zero derivatives, a malformed
  interval, wrong m, wrong manifest, malformed identity, protocol and wrapper tampering, geometry, the ladder,
  controls, and the premise rule.
- **Q2:** the replay of K1 cell 0 reproduced `R_interval` and `D_interval` **exactly** for m = 1, 2, 3, 5.
- **Q3:** the degenerate cell `{e0}` gave enclosures contained in the record's.
- **Q4:** identity matched and the SciPy guard was clean.
- **Q5:** 0.66 CPU-h, under the 2 CPU-h ceiling.

The gates were never changed. Only the first rung ran, because every target was already decisive there, so no
retry or escalation happened. The run wrote nothing outside this namespace.

## Result (256 bits; decimals rounded outward, exact rationals in `result/RUNG_256.json`)

| m | Role | R'(0) enclosure | GammaTilde enclosure | Margin above 1 | Status |
|---|---|---|---|---|---|
| 3 | target | [−19.322961, −2.527955] | [3.527955, 20.322961] | 2.527955 | **CERTIFIED** |
| 5 | target | [−17.442603, −0.937531] | [1.937531, 18.442603] | 0.937531 | **CERTIFIED** |
| 2 | control | [−20.789792, −3.725414] | [4.725414, 21.789792] | 3.725414 | consistent with reuse [1.766264, 24.748817] |
| 1 | non-target control | [−19.469325, −10.304405] | [11.304405, 20.469325] | 10.304405 | consistent with CORE-C1 [3.9243482, 27.8493821] |

Every `R_m(0)` enclosure contains 0, as oddness requires. No control problems were found. Science CPU was
1160.5 s (0.322 CPU-h); qualification added 0.661 CPU-h.

## Verdict

```
M3_GAMMATILDE_GT_1 = CERTIFIED
M5_GAMMATILDE_GT_1 = CERTIFIED
ALL_CUSUM_M_GAMMATILDE_GT_1 = CERTIFIED          (m=1 CORE-C1, m=2 reuse audit + this control, m=3, m=5 here)
H3A_POSITIVE_BRANCH_PREMISE_CUSUM = SATISFIED
```

## Scope

- This certifies only `GammaTilde_m > 1` for the frozen Gaussian CUSUM at m ∈ {3, 5}. Together with the m = 1
  certificate and the m = 2 reuse audit, it covers all CUSUM m ∈ {1, 2, 3, 5}.
- The `= 1/rho_c` clause of H3a now has its sign premise for CUSUM. **H3a itself (strict monotonicity of s) is not
  proved here, and K5 and P5Y are not closed.** K5-B remains sufficient-only, and B1 (the real order-3 producer)
  is unaffected. SR is outside scope.
- P1-T1's analytic obligations and P5X L5 keep their existing review status.
- The evaluator's validity rests on the frozen K1 CUSUM certifier (the Aux5 producer and its adjudications); this
  successor adds no new analytic premise.
