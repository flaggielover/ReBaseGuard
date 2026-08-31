# Priority-3 proofs

All statements are about the scalar function

```text
lambda(rho, G) = rho (1 - G),      rho in [0,1],  G real,
```

supplied by the closed Priority-1 and Priority-2 derivative theorems. The
proofs are elementary; they are written out because the campaign's whole claim
rests on getting the degenerate cases right rather than on analytic depth.

## Lemma 1 (magnitude factorisation)

For `rho >= 0`, `|lambda(rho,G)| = |rho| |1-G| = rho |1-G| = rho d(G)` with
`d(G) := |1-G|`.

*Proof.* `|xy| = |x||y|` and `|rho| = rho` for `rho >= 0`. ∎

Formalized as `Priority3Map.abs_multiplier`.

## Lemma 2 (strict monotonicity in the reuse fraction)

If `G != 1` then `rho -> |lambda(rho,G)|` is strictly increasing on `[0,∞)`.

*Proof.* `d(G) = |1-G| > 0` because `1-G != 0`. By Lemma 1 the map is
`rho -> rho d(G)`, and multiplication by a positive constant is strictly
increasing. ∎

Formalized as `Priority3Map.abs_multiplier_strictMonoOn`.

Consequence: for `G != 1` the locally attracting set is an interval containing
`0`, so a single threshold describes it completely. This is the step that
licenses drawing a boundary line rather than a region.

## Lemma 3 (exact boundary identity)

If `G > 1` and `rho_c := 1/(G-1)` then `|lambda(rho_c,G)| = 1` exactly.

*Proof.* `G > 1` gives `G-1 > 0`, hence `rho_c > 0` and `d(G) = G-1` (since
`1-G <= 0`). By Lemma 1, `|lambda(rho_c,G)| = (1/(G-1))(G-1) = 1`. ∎

Formalized as `Priority3Map.boundary_at_criticalRho`.

## Theorem 4 (attraction and repulsion criteria)

Let `rho >= 0` and `G > 1`. Then

```text
|lambda(rho,G)| < 1  <=>  rho < 1/(G-1),
|lambda(rho,G)| > 1  <=>  rho > 1/(G-1).
```

*Proof.* By Lemma 1 and `d(G)=G-1>0`, the claim is `rho(G-1) < 1` iff
`rho < 1/(G-1)`, which is division of a strict inequality by the positive
number `G-1`; likewise for the reverse inequality. ∎

Formalized as `Priority3Map.attracting_iff_lt_criticalRho` and
`Priority3Map.repelling_iff_criticalRho_lt`.

Together with the trichotomy of `|lambda|` against `1`
(`Priority3Map.trichotomy`) the three cases are exhaustive and mutually
exclusive, and the boundary case is the one on which linearization is silent.

## Theorem 5 (admissible-domain intersection)

Let `G > 1`. Then `rho_c = 1/(G-1) <= 1` if and only if `G >= 2`.

*Proof.* `G-1>0`, so `1/(G-1) <= 1` iff `1 <= G-1` iff `G >= 2`. ∎

Formalized as `Priority3Map.criticalRho_le_one_iff`.

Hence for `1 < G < 2` the algebraic boundary exists but is inaccessible on
`[0,1]`, and every admissible reuse fraction is locally attracting.

## Theorem 6 (moderate-gain endpoint audit)

If `0 <= G <= 2`, `0 <= rho` and `rho < 1`, then `|lambda(rho,G)| < 1`.

*Proof.* `0 <= G <= 2` gives `-1 <= 1-G <= 1`, hence `d(G) <= 1`. By Lemma 1,
`|lambda| = rho d(G) <= rho < 1`. ∎

Formalized as `Priority3Map.attracting_of_gain_le_two`. The neutral case
`G = 1` is separately recorded (`attracting_of_gain_eq_one`): the multiplier
vanishes identically, the whole admissible domain is attracting, and no
critical fraction exists — it is not merely inaccessible.

At full reuse the endpoints and interior must be separated. If `0 < G < 2`,
then `-1 < 1-G < 1`, hence `|lambda(1,G)|=|1-G|<1`; full reuse is still
attracting. If `G=0` or `G=2`, then `|lambda(1,G)|=1`, so full reuse is the
first-order boundary. These statements are formalized as
`full_reuse_attracting_of_gain_between_zero_two` and
`full_reuse_boundary_of_gain_eq_zero_or_two`.

## Lemma 7 (gain-interval envelope)

If `Glo <= G <= Ghi` then `d(G) <= max(d(Glo), d(Ghi))`.

*Proof.* `d` is the composition of an affine map with the absolute value, hence
convex; on an interval a convex function attains its maximum at an endpoint.
Concretely: if `G <= 1` then `d(G) = 1-G <= 1-Glo <= |1-Glo| = d(Glo)`; if
`G >= 1` then `d(G) = G-1 <= Ghi-1 <= |1-Ghi| = d(Ghi)`. ∎

Formalized as `Priority3Map.gainDistance_le_max`.

## Theorem 8 (interval robustness)

Let `rho >= 0` and `Glo <= G <= Ghi`.

1. If `rho d(Glo) < 1` and `rho d(Ghi) < 1`, then `|lambda(rho,G)| < 1`.
2. If `1 <= Glo` and `rho d(Glo) > 1`, then `|lambda(rho,G)| > 1`.

*Proof.* (1) By Lemma 7 and Lemma 1, `rho d(G) <= rho max(d(Glo),d(Ghi)) < 1`.
(2) `1 <= Glo <= G` gives `d(G) = G-1 >= Glo-1 = d(Glo)`, so
`rho d(G) >= rho d(Glo) > 1`. ∎

Formalized as `Priority3Map.attracting_of_interval` and
`Priority3Map.repelling_of_interval`.

This is the formal content of the campaign's reporting rule: a classification
may be reported as robust only when the enclosing gain interval yields the same
verdict at both endpoints. Its contrapositive is the rule actually implemented:
if the magnitude interval contains `1`, the cell is `INCONCLUSIVE`.

## Proposition 9 (exactness of the magnitude interval)

For `rho >= 0` and `G` ranging over `[Glo, Ghi]`, the set of values `rho d(G)`
is exactly

```text
[ rho * min , rho * max ],   max = max(|1-Glo|,|1-Ghi|),
min = 0 if Glo <= 1 <= Ghi, else min(|1-Glo|,|1-Ghi|).
```

*Proof.* `d` is continuous on a connected interval, so its image is an
interval. Its maximum is at an endpoint by Lemma 7. Its minimum is `0` exactly
when `1` is in the interval (where `d` vanishes), and otherwise `d` is monotone
on the interval, so the minimum is at an endpoint. Multiplying by `rho >= 0`
preserves order. ∎

This is why the implementation does not take endpoint minima blindly: for a
gain interval straddling `1` the true minimum magnitude is `0`, which is
precisely the case where a naive endpoint rule would understate uncertainty.

## Proposition 10 (delta-method standard error)

For `G > 1`, `rho_c(G) = 1/(G-1)` has derivative `-1/(G-1)^2`, so the
first-order standard error of the plug-in estimator is

```text
SE(rho_c) = SE(G) / (G-1)^2.
```

Interval endpoints are additionally reported by the exact monotone transform
`[1/(Ghi-1), 1/(Glo-1)]` whenever `Glo > 1`; when the gain interval reaches
`1` the transformed interval is unbounded above and is reported as such rather
than truncated to a finite endpoint.

## Proposition 11 (exact witness boundaries)

For the Priority-1 finite-support witness the exact gain is `15/2` for every
`m` in the supported grid, so `rho_c = 2/13`. For the Priority-2 SR-compatible
witness the exact gain is `2 + 2/m`, so

```text
rho_c(m) = 1/(1 + 2/m) = m/(m+2),
```

giving `1/3, 1/2, 3/5, 5/7` at `m = 1,2,3,5`.

*Proof.* Both gains are finite rational sums; the values are recomputed in
exact rational arithmetic from the frozen witness files by
`src/rebaseguard_p3_map/provenance.py::exact_witness_gamma`, and the entries at
`m in {2,3,5}` reproduce the values already recorded by the two closed
certificates. The boundary values follow from Lemma 3. ∎

Because every quantity involved is rational, the boundary identity
`|lambda(rho_c)| = 1` is certified **exactly**, not by enclosure. The Arb run
at 128 bits reports an enclosure of `1` as a consistency check; an interval can
never certify an equality, and this campaign does not pretend otherwise.
