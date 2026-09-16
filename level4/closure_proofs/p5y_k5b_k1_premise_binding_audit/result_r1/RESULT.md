# K5-B → K1 CUSUM premise-binding audit: result r1

This result executes the plan published in `9d136827` (`config/AUDIT_PLAN.json`, unchanged). The audit base is
`1bf31bc8`. The audit is read-only: it computes no new scientific value, runs no probe, builds no producer and
issues no K5/H3a verdict. The machine record is `PREMISE_BINDING_RESULT.json`, and
`code/verify_premise_binding.py` recomputes every Git-checkable fact in it.

```text
PB2_REGULARITY                = BOUND
PB2_L5_GOVERNANCE             = internal human proof only; no independent review found; recorded "nothing certified depends on it"
PB2                           = BOUND_WITH_NOTE
PB3_DEFINITIONAL_BINDING      = PASS
PB3_EXTERNAL_CONSISTENCY      = PASS   (corroborative only; weak for m > 1)
PB3                           = BOUND
PB4_FUNCTION_IDENTITY         = BOUND
PB5_WHOLE_CELL_R2             = BOUND
PB6_R2_ENDPOINT_GATE          = BOUND_WITH_NOTE
CUSUM_K5B_K1_PREMISE_BINDING  = PASS_WITH_NOTES
NEW_K5_BLOCKER_CREATED        = NO
SR_PREMISE_BINDING            = UNDETERMINED_PENDING_PS1
B3_REOPENED                   = NO
B1_NO_CERTIFIED_ORDER3_PRODUCER = OPEN
```

| Item | What binds it | Note |
|---|---|---|
| PB2 C³ | P5X L5 (PROOF.md §L5) makes `R_{D,m}` holomorphic on a strip, hence real-analytic on all of ℝ. That covers `e = 0`, cell 309 beyond 2, and every K5-B MVT/integral step on `[0, 11/2]`. The proof trace found no gap. | L5 is internal P5X work (`528908ba`) with no independent review. It was recorded as non-load-bearing, and it became load-bearing only through K5-B. |
| PB3 `R'(0) = 1 − Γ̃` | `R = E[R̄\|e] = e + E_e[A_m]` (P5-T1/T2, P5X L1.7) `= F_{1,m}` (P1 §1) ⇒ `R'(0) = 1 − Γ̃_m` by P1-T1, an EXACT_THEOREM recorded as independently reviewed, with `Γ̃_m = E_0[A_m T_τ]`. There is no hidden `+e` (raw-variable `F = R`), no sign flip (`z = raw − e` everywhere), and no alternate map (convention A). | Cell-0 record: the implied Γ̃ intervals contain the estimates for every m. For m = 1 the interval `[7.08, 24.70]` lies inside the certified `[3.92, 27.85]`. |
| PB4 identity | The raw DAG is re-derived to `E_{x0}[R̄]` with W-coefficients `1/t − 1/m`, which equal the frozen table. Detector, `k = 1/2`, `h = 5`, `m`, convention A, reset state, `e`-sign, geometry and domain match term by term. The certifier `qualify5` path is bound by manifest v3: 60 files byte-identical, hash `b55a2da1`, identity `3692d0fe` = the closure's identity. | `ρ` is a name collision: the P5 reuse fraction is not the K1 cell half-width. |
| PB5 whole-cell `R''` | `R2_interval` = assembly of `Ĥ(x0) ± refine2 whole-cell ε` and `Ŵ''(x0) ± whole-cell cascade/Taylor ε`. Every rule holds for all `\|e − e0\| ≤ ρ`. It is not a midpoint value, point estimate, Taylor coefficient, sample or magnitude. | Inherited adjudications (drift-aware norms, refine2, auxiliary derivative) and the per-cell `C_upper` were traced, not re-adjudicated. |
| PB6 `R(2) > −2` | The per-m `target_gate` on the Taylor enclosure of cell 309 = `[1.9839101, 2.092283]`: PASS for m = 1, 2, 3, 5. An exact recheck from the record endpoints gives whole-cell `R ≥ −0.625443 / −0.336675 / −0.226774 / −0.161330`, margins 1.374557 / 1.663325 / 1.773226 / 1.838670. It is not the far-field splice. | The closure does **not** imply it: sealing and K4 attestation check structure only (`k4_values_evaluated = false`). It is bound by the record's frozen scientific hash and the export manifest. A K5 consumer must check it explicitly. |

**Host observations** (read-only, `rebaseguard-vultr-02`):
- export manifest `29ad1f9b` equals the committed copy;
- 326/326 record hashes match;
- 326/326 records carry identity `3692d0fe`;
- all 1304 `target_gate` and ledger statuses are PASS.

Byte copies of the records for cells 0 and 309 are in `records/`. They match the committed export manifest, and
their frozen scientific hashes recompute.

**Consumption readiness.** For CUSUM, the K5-B premises are bound to the closed K1 evidence, with two notes: L5's
governance status, and the explicit cell-309 gate check. A future certified signed-`R'''` producer may consume the
CUSUM `R_interval`, `D_interval` (midpoint), `R2_interval` and `M_R2` (whole-cell) records under identity
`3692d0fe`. It must:
1. carry those notes;
2. re-verify record bytes against export manifest `29ad1f9b`;
3. check the cell-309 `target_gate` PASS for every m itself.

This result authorizes nothing, and it does not strengthen H3a's `1/ρ_c` clause, which lies outside K5-B.

```bash
python3 -B code/verify_premise_binding.py
python3 -B tests/test_premise_binding_result.py
python3 -B tests/test_plan.py
```
