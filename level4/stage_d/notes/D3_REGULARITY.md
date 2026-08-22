# D3.1 — regularity assumptions, written before any non-Gaussian simulation

**Written 2026-08-22, BEFORE any D3 data was generated**, as
`STAGE_D_PROTOCOL.md` (`925adecf…`) D3.1 requires. Each assumption is labelled
with its actual evidential status. Unproved assumptions are marked **UNPROVED**
and stay marked in the report.

Notation: innovations `raw_t ~ p` i.i.d., `z_t = raw_t − e`, so the location
family is `p_e(z) = p(z + e)` and the score is `psi = −p'/p`, giving
`d/de log p_e(z)|_0 = −psi(z)`.

---

## A1 — Differentiation under the expectation **UNPROVED for non-Gaussian**

`d/de E_e[g] |_0 = −E_0[ g * sum_{t<=tau} psi(z_t) ]`.

Needs local domination / uniform integrability of `g * sum_t psi(z_t)` in a
neighbourhood of `e = 0`.

* **Gaussian:** the corresponding interchange is machine-checked in Lean for the
  frozen functional (Level 2C, `FROZEN-PROVED`). It is not re-derived here.
* **Every non-Gaussian family: UNPROVED.** The heavy-tailed families are exactly
  where such domination is most delicate — `t_3` has no finite fourth moment, so
  the usual `L^2`-domination argument does not transfer.
* **Consequence, committed now:** D3 can establish *numerical robustness only*.
  A rigorous general theorem may be claimed only if A1 is actually discharged,
  which this stage does not attempt. Numerical agreement is **not** a proof of
  A1, and will not be presented as one.

## A2 — Finite Fisher information `I = E[psi^2] < inf` **VERIFIED NUMERICALLY**

Checked by quadrature per family, together with the regularity identity
`E[psi^2] = E[psi']`, which holds to 4 decimals for all six families:

| family | Var | `I = E[psi^2]` | `E[psi']` |
|---|---|---|---|
| gaussian | 1.0000 | 1.0000 | 1.0000 |
| t10 | 1.0000 | 1.0577 | 1.0577 |
| t5 | 1.0000 | 1.2500 | 1.2500 |
| t3 | 1.0000 | 2.0000 | 2.0000 |
| contam0.05 | 1.4000 | 0.8833 | 0.8833 |
| contam0.1 | 1.8000 | 0.7961 | 0.7961 |

Status: `NEW-NUMERICAL`. Quadrature is not a proof, though for these closed-form
densities the values are standard.

## A3 — `E[tau] < inf` under each family **VERIFIED NUMERICALLY**

Each family's CUSUM threshold is recalibrated so `ARL0` matches the frozen
Gaussian CUSUM, which presupposes finiteness. Measured directly per family.
The Level 1–3 killing lemma (`|G_n| >= h + nk => tau <= n`) is a Gaussian
argument and is **not** transferred.

## A4 — Square-integrability of the stopped score sum **UNPROVED**

`E[(sum_{t<=tau} psi(z_t))^2] < inf` is needed for the estimator to have finite
variance. Under Wald's identities this follows from A2 and A3 for well-behaved
families, but the stopped sum is not a simple sum and the argument is not
completed here. Monitored empirically: the reported SEs are meaningless if this
fails, so per-family batch-mean and normal SEs are compared, and disagreement
between them is reported as a symptom.

## A5 — **The protocol's `Gamma_psi` is not normalised by `E[psi']`** ⚠️

This is the most important limitation in D3 and is recorded **before** seeing any
result so it cannot be presented as an afterthought.

The protocol freezes

    Gamma_psi = E[ (1/w) sum_{i<w} psi(z_{tau-i}) * sum_{t<=tau} psi(z_t) ]

If the reference is re-estimated from the stopped window by the M-estimator with
score `psi` — the natural generalisation of the Gaussian sample mean — its
influence function is `psi / E[psi']`, so the induced map obeys

    F'(0) = 1 − Gamma_psi / E[psi']

and the local-stability boundary is `Gamma_psi / E[psi'] = 2`, **not**
`Gamma_psi = 2`. The two coincide **only for the Gaussian**, where `E[psi'] = 1`.

* The D3.2 criterion is applied to `Gamma_psi` exactly as frozen. It is not
  rewritten.
* `Gamma_psi / E[psi']` is reported alongside it as the **stability-relevant**
  quantity, clearly labelled, with `E[psi']` from A2.
* Because `E[psi'] > 1` for `t10`, `t5`, `t3` and `< 1` for both contaminated
  families, the normalisation moves the two groups in **opposite** directions.
  Any conclusion that is not robust to this choice will be reported as
  ambiguous rather than resolved in the convenient direction.

## A6 — Odd symmetry `F(−e) = −F(e)` **ASSUMED, checked numerically**

All six families are symmetric about 0 and the detector is two-sided, so the
innovation-negation / arm-swap involution used in the Gaussian case should
carry over. Not re-proved for non-Gaussian; checked numerically.

## A7 — The detector is unchanged **BY CONSTRUCTION**

The frozen CUSUM *form* (`k = 1/2`, two-sided, inclusive post-update alarm) is
applied to non-Gaussian innovations. Only the threshold `h` is recalibrated, to
match `ARL0`. `k = 1/2` is **not** the likelihood-ratio-optimal drift for
non-Gaussian families, so these detectors are deliberately *not* optimal — D3
tests robustness of the frozen scheme, not optimality of a redesigned one.

---

## Vocabulary fixed in advance

D3 may produce, at most, **numerical robustness across the tested families**.
The words "distribution-free", "universal", "robust in general" and "certified"
are forbidden regardless of outcome. Six families are not a class of
distributions, and agreement among them is replication, not generality.
