# P4ZB Phases 1–2 — the local finite-difference structure at `frozen/cusum@5/skewnormal4`

The expansion is derived first; the observed order is then explained from it;
and the derivation is turned into **out-of-sample predictions** that the Phase-4
study tests before anything is frozen.

## 1. Regularity: does an even-power expansion exist at all?

The frozen Route-B object is the central difference of `g_m(e) = E_e[A_m]`,

```text
D(h) = -( g_m(h) - g_m(-h) ) / (2h)
```

An expansion `D(h) = Gamma + a h^2 + b h^4 + c h^6 + ...` requires `g_m` to be
sufficiently differentiable near `0`.  Four things could spoil it, and each is
checked rather than assumed.

**(i) Score growth.**  `skewnormal4` has `score_bound = None`, but its score is
at most linear (`psi/z -> sd` on the right, `-> sd(1+alpha^2)` on the left, by
the Mills ratio).  That is hypothesis **L4** of the frozen `THEOREM.md` §8, and
L4+L1+L2 discharge the skew-normal there.  Linear growth does not obstruct
smoothness of a *stopped expectation* in the location parameter.

**(ii) The alarm geometry.**  `tau` is integer valued and the alarm set is a
union of half-lines whose endpoints move with `e`.  Individual paths therefore
change their stopping time discontinuously in `e`.  But `g_m(e)` is an
*expectation* over a continuous innovation law: the discontinuity is integrated
against a density, so the boundary contributes terms that are smooth in `e`
provided the density is smooth, which the skew-normal is (`C^infinity`,
positive on `R`).  This is the same mechanism that makes `g_m` differentiable at
all — Theorem G1a — and it does not stop at first order.

**(iii) Common support.**  `(A3)` holds: the skew-normal is positive on all of
`R` and its support does not move with `e`.  The moving-support failure mode
`F1`, which genuinely destroys the identity, does not apply.

**(iv) Asymmetry.**  `skewnormal4` is the only asymmetric family in scope, so
`E_0[A_m] != 0` and `0` is not a fixed point of the reuse map.  That matters for
the *stability* reading (Theorem G4) but not for the existence of the expansion:
the central difference kills even derivatives of `g_m` regardless of whether
`g_m(0) = 0`.

**Conclusion.**  An even-power expansion is available.  `P4ZB` does **not**
assume the *effective* order is already 2 — see §3.

## 2. The expansion and the Richardson relation

```text
g_m(±h) = g_m(0) ± h g' + (h^2/2) g'' ± (h^3/6) g''' + (h^4/24) g'''' ± (h^5/120) g^(5) + ...
g_m(h) - g_m(-h) = 2h g' + (h^3/3) g''' + (h^5/60) g^(5) + ...
D(h) = Gamma + a h^2 + b h^4 + O(h^6),   a = -g'''/6,  b = -g^(5)/120
```

For a factor-2 pair, `R(2h, h) = (4 D(h) - D(2h))/3 = Gamma - 4 b h^4 + O(h^6)`.

## 3. Why the *effective* order can sit below 2 while the asymptotic order is 2

This is the heart of the matter.  Take the successive CRN-paired differences on
a triple `(2h, h, h/2)`:

```text
Delta_1 = D(2h) - D(h)   = 3 a h^2 + 15 b h^4
Delta_2 = D(h) - D(h/2)  = (3/4) a h^2 + (15/16) b h^4
```

so the ratio that defines the empirical order is

```text
Delta_1 / Delta_2 = 4 * ( a + 5 b h^2 ) / ( a + (5/4) b h^2 )
p = log2( Delta_1 / Delta_2 )
```

Read that carefully.  If `b/a > 0` the ratio exceeds 4 and `p > 2`.  If
`b/a < 0` the ratio falls **below** 4 and `p < 2` — with no failure of the
theory whatsoever.  A measured `p < 2` is therefore *not* evidence that the
expansion is invalid; it is evidence that the `h^2` and `h^4` coefficients have
**opposite signs** and that `h` is not yet small enough for the `h^2` term to
dominate.

`p -> 2` as `h -> 0` in either case.  The approach is from below when
`b/a < 0`.

## 4. Testing that against P4ZA's stored ladder

P4ZA ran three rungs, `(0.1, 0.05, 0.025)`, on this configuration with 40 blocks
of 32 268 paths.  Solving `D(h) = Gamma + a h^2 + b h^4` exactly on those three
points:

| m | `Gamma` fit | `a` | `b` | `b/a` | `b h^2/a` at `h=0.05` | `p` predicted | `p` observed |
|---|---|---|---|---|---|---|---|
| 1 | 5.37849 | 206.54 | −6023.61 | **−29.16** | −0.0729 | 1.484 | **1.484** |
| 2 | 4.28978 | 175.05 | −5039.75 | **−28.79** | −0.0720 | 1.492 | **1.492** |
| 3 | 3.84612 | 154.29 | −4492.84 | **−29.12** | −0.0728 | 1.485 | **1.485** |
| 5 | 3.47815 | 123.27 | −3846.91 | **−31.21** | −0.0780 | 1.435 | **1.435** |

`b/a` is negative on every `m`, which is exactly the condition §3 derives for
`p < 2`, and the predicted order reproduces the observed order to three decimal
places.

**This is a consistency check, not a validation.**  Three points determine three
unknowns, so the fit *must* reproduce them; the only real content is that the
sign of `b/a` came out negative as the mechanism requires.  An independent test
needs a fourth rung, which is what Phase 4 buys.

## 5. What the model says about P4ZA's `T_B`

Under the same model the residual of the frozen Richardson value is
`-4 b (0.025)^4`, and the difference between the two Richardson pairs P4ZA used
is

```text
R(0.1,0.05) - R(0.05,0.025) = -4b(0.05^4 - 0.025^4) = -4b(0.025)^4 * (16 - 1)
```

i.e. exactly **15 times** the residual it was standing in for.  Measured on the
stored blocks the ratio is `15.00` on all four `m`, to two decimals.

That is not a discovery about the data; it is the factor **P4ZA declared in
advance** in its own frozen checkpoint — *"the idealised `h^4` relation would
divide this by 15; P4ZA does NOT, which is a declared conservative factor of
15."*  The measurement confirms the declaration was quantitatively exact.

Modelled residual of the frozen Richardson value, as a fraction of it:

| m | modelled residual | as % of `R` | P4ZA `T_B` | as % of `R` | ratio |
|---|---|---|---|---|---|
| 1 | +0.009412 | 0.175 % | 0.14118 | 2.620 % | 15.00 |
| 2 | +0.007875 | 0.183 % | 0.11812 | 2.748 % | 15.00 |
| 3 | +0.007020 | 0.182 % | 0.10530 | 2.733 % | 15.00 |
| 5 | +0.006011 | 0.173 % | 0.09016 | 2.588 % | 15.00 |

**P4ZB does not act on this table.**  It is a model prediction, and a model
fitted to three points that then explains those three points has proved nothing.
The next section states what would falsify it.

## 6. Falsifiable out-of-sample predictions

The fit used only `h = 0.1, 0.05, 0.025`.  It predicts, for rungs it has never
seen:

| m | `D(0.0125)` | `D(0.00625)` | `p` on `(0.05,0.025,0.0125)` | `p` on `(0.025,0.0125,0.00625)` |
|---|---|---|---|---|
| 1 | 5.410617 | 5.386551 | 1.895 | 1.975 |
| 2 | 4.317007 | 4.296609 | 1.897 | 1.975 |
| 3 | 3.870116 | 3.852138 | 1.896 | 1.975 |
| 5 | 3.497322 | 3.482964 | 1.888 | 1.973 |

If the Phase-4 study reproduces these, the `h^4` model is validated out of
sample and the residual estimate in §5 is trustworthy.  If it does not — if the
order stalls, or `D` at the finer rungs departs from prediction by more than
Monte Carlo error allows — then the model is **wrong**, the residual estimate is
unusable, and P4ZB reports that rather than extrapolating.

## 7. The other candidate explanations, and why they are rejected

* **CRN / Monte Carlo noise.**  Rejected on block-level data: the paired
  differences carry standard errors 7 to 100 times smaller than the differences
  themselves at the coarse rungs, and the fitted `b/a` is consistent across all
  four `m` to within 8 %.  Noise does not produce a coefficient ratio that
  stable.
* **Numerical cancellation.**  Rejected at these rungs: `h = 0.025` against a
  CUSUM slack `k = 1/2` is a 5 % perturbation, and the differences are `O(1)`
  against estimates of `O(5)`.  Cancellation becomes the binding problem only at
  the finest rungs, which is precisely what the study maps.
* **Alarm-boundary non-smoothness.**  Rejected as the *dominant* effect: it
  would not produce a clean two-term `h^2 + h^4` structure whose predicted order
  matches the observed order to three decimals on four independent `m`.
* **Skewness-induced coefficient imbalance.**  This is **accepted** — it is the
  same statement as `b/a < 0`.  The asymmetric family is the only one in scope
  whose `b/a` is both negative and large enough (`≈ −30`) to hold `p` near 1.45
  at the frozen rungs.  The symmetric light families at the same detector reach
  `p ≈ 1.6–2.3`.
* **Insufficiently fine `h`.**  Also **accepted**, and it is the same mechanism:
  `|b h^2 / a| ≈ 0.073` at `h = 0.05` and `0.018` at `h = 0.025`.  The `h^4`
  term is a few per cent of the `h^2` term, which is exactly enough to move the
  measured order from 2.0 to 1.45.
