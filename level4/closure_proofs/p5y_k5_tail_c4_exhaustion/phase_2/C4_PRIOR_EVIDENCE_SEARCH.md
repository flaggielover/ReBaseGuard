# Phase 2 — reuse first: does anything already certified bound E_a[tau] from below?

Producer: `code/c4_prior_evidence.py`. Evidence: `evidence/phase2/C4_PRIOR_EVIDENCE.json`.
Reproduce with `python3 -B code/c4_prior_evidence.py --out /tmp/x.json`.

## The answer

**No.** Every committed quantity that constrains the *level* of `E_a[tau] = tau_a / D` constrains it from above.

## How that was established, in two mechanical halves

**(a) A direction table over every certified field.** The producer enumerates every field of the C1 and C2 tail
registries and of their per-cell taboo and whole-kernel artifacts, for cells 306–309, and classifies each against a
table written out in full in the source. Fields the table does not name are reported as `UNCLASSIFIED`, not
dropped; the run that produced the committed evidence has `unclassified_fields: []`.

| direction | fields |
|---|---|
| `UPPER` — bounds the numerator or the whole ratio from above | `tau`, `C_T`, `Abar`, `sup_w_chebyshev` |
| `LOWER_D` — bounds the denominator from below, which again bounds the ratio from above | `D_lo` |
| `ENCLOSE` — two-sided | `D_mid` |
| `OTHER` — derivatives, geometry, allowances, candidate values, provenance | `D1`, `D2`, `D1_mid_abs_upper`, `margin_lower_bound`, `w_min_lower_bound`, `allowance_upper`, `candidate_at_atom`, `lambda_mid`, `lambda_cell`, `arl`, `sub_blocks` |

Two entries deserve their reasons stated rather than being left to the table.

* **`D_mid` is the only two-sided object in the corpus**, and it is on the wrong side of the fraction. Its upper end
  does give `E_a[tau] >= tau_a / D_mid_hi >= 1 / D_mid_hi`, which is a genuine certified lower bound — Phase 3
  evaluates it as route R4 and it lands near 1.04–1.08, against thresholds of 3.2 and 4.4.
* **`margin_lower_bound` is the near miss.** It is `inf_X` of the supersolution defect `w - 1 - Khat w`. Inverting
  Lemma T into a lower bound needs `sup_X` of that same defect, which the certifier computes on the way past — the
  frozen `min_max_on_reachable` returns both — and then discards. The information exists; it is not recorded.

**(b) A tree sweep, so that "we looked where we expected to find it" is not the argument.** Every `.json` and `.py`
under `level4/closure_proofs` outside this namespace is searched for `subsolution|minorant|lower bound on
…(arl|tau|stopping)|arl_lower|tau_lower|E_a[tau] >=`. The committed run records every hit with its matched text.
The hits reduce to exactly three kinds:

| matched text | count | disposition |
|---|---|---|
| `minorant` | 31 | the P5X drift-minorant family and integer-floor geometry. `drift_minorant.py`'s own docstring: it changes "the rigorous **upper** bound used for `\|\|(I - K_e)^{-1}\|\|_inf`". A minorant of the hit probability is a majorant of the ARL. Wrong direction. |
| `lower bound on hitting gives an upper bound on sup_x E_x[tau]` | 2 | `p5y_gate2e_sr_metric` and `…2f`. SR detector, not CUSUM; `binding: false`; `e = 1/4`, not a tail cell; and their own `direction_audit` records `type: UPPER`. Wrong detector, wrong drift, wrong direction. |
| a GSR/SADD passage | 1 | an external literature abstract inside `novelty_verification`. Not a certificate of anything in this programme. |

## Dependency map

The map Phase 2 was asked to build has one live chain and a set of dead ends. The dead ends are the point of the
exercise, so they are drawn too.

    D_mid (two-sided, committed)  --[ tau_a >= 1, Lemma SM(a) ]-->  E_a[tau] >= 1/D_mid_hi  ~ 1.05   DEAD (too weak)

    tau, C_T, Abar, C_upper, D_lo  --[ every one an upper bound ]-->  (no lower bound derivable)     DEAD

    margin_lower_bound = inf_X g  --[ needs sup_X g, not recorded ]-->  tau_a >= w(a)/(1 + sup g)    BLOCKED

    frozen model geometry (H, K)  --[ theorem L: ladder/Wald ]-->  E_a[tau] >= H/E[(|z|-K)^+]
        --> compare against critical A0  --> cell excluded, or not                                   LIVE

The live chain touches no registry constant, no candidate polynomial and no Arb certificate. That is not an
accident of convenience: it means the exclusion result cannot inherit a defect from any surface C2 or C3 argued
about.
