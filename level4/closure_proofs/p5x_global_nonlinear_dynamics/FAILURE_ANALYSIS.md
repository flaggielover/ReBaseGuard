# P5X failure analysis — what does not work, and what P5X will not prove

Recorded **before** any production result, so that a later negative outcome
cannot be presented as a surprise and a later positive outcome cannot be
presented as inevitable.

---

## 1. Cauchy–Schwarz through `P5-T5` is structurally dead

The cheapest imaginable route to `sup_e |R| < 2` is

```text
|R(e)| = |E[Rbar | e]| <= sqrt( E[Rbar^2 | e] ) <= sqrt(C_D) .
```

With P5's proved constants this gives `3.1e4` (CUSUM); with the *measured*
`sup_e E[tau|e] = 465` it still gives `21.6`. The final-disposition audit
already recorded this. P5X adds the sharper observation that the route cannot
work **even with a perfect constant**:

```text
E[Rbar^2 | e=0] = S(0) = 4.036 (CUSUM, m=1) > 4 ,
```

so `sqrt(E[Rbar^2|0]) > 2` exactly. Any bound of the form
`|R| <= sqrt(E[Rbar^2])` is therefore *provably* incapable of reaching `2` for
`m = 1`. Bounding `|R|` requires exploiting the cancellation inside the
expectation, i.e. actually solving for it. This is the single strongest reason
the campaign is a certified-numerics campaign and not an inequality-chasing
campaign.

## 2. There is no restoring drift, and P5X must not claim one

The brief's §5 target,
`sign(e) E[e_{j+1} - e_j | e] < -eps` outside a compact set, is satisfied — but
not because the far field is pushed back toward `0`. It is satisfied because
the far field is **erased**: for `|e|` large the alarm fires on the first
observation, `w = min(m,1) = 1`, the selection constraint becomes vacuous, and
the next state is drawn from a *fixed* law that does not remember `e` at all.
`E[e_{j+1} | e] -> 0`, not `-c e`.

Consequences that P5X respects:

* the drift inequality is a statement about **forgetting**, and the write-up
  must say so; describing it as a Lyapunov restoring force would be a
  mechanistic misstatement even though the inequality is true;
* no contraction-outside-a-compact-set argument is available, because
  `|E[e_{j+1}|e] - E[e_{j+1}|e']|` does not shrink proportionally to `|e - e'|`
  in the far field — it goes to `0` for both, which is *stronger* pointwise but
  says nothing about a contraction constant on pairs;
* monotone-drift arguments are unavailable: `|R|` is not monotone in `|e|`.
  The secondary lobe near `|e| ~ 5.5` (CUSUM) and `~ 6.5`–`7` (SR) is real and
  reproduced in both P5 seed families and in the P5X probe.

## 3. Small-noise / stochastic-bifurcation theory does not fit

A stochastic flip-bifurcation treatment would require the branch amplitude to
dominate the per-cycle noise. It does not, anywhere in the admissible range:
P5 measured `SNR <= 1.5` (`m = 1`) and `~0.01` at `rho_c` itself, with the
noise floor bounded below by `(1-rho_c)/sqrt(m) >= 0.40`. Any expansion in a
small noise parameter would be an expansion in a parameter that is `O(1)`.
P5X therefore does **not** name random dynamical systems, stochastic normal
forms, or stochastic bifurcation theory as tools. They would be technique
theatre.

## 4. The skeleton is not a model of the chain

`f_rho = rho R` is the conditional-mean map. Iterating it is a legitimate object
of study and P5 studied it. It is **not** an approximation to the stochastic
recursion at any admissible `rho`, for the reason in §3. Therefore:

* a proof of Level D (skeleton global dynamics) is not a proof about `pi`;
* the measured bimodality of `pi` (onset `4.1x`–`9.8x rho_c`) is not explained
  by the 2-cycle merely because both are "two-ness";
* P5X's gate `G12` fails the campaign if the synthesis language lets a reader
  infer otherwise.

## 5. What P5X will not attempt

| not attempted | why |
|---|---|
| proving `sup_e E[tau|e] = E[tau|0]` | a separate theorem; it would make `P5-T4`/`T5`/`T7` constants realistic, but P5X's route does not need it (the resolvent bound is obtained per `e`-interval by the monotone Bellman minorant) |
| a rigorous enclosure of the invariant density `pi` | far harder than the moment bounds and not needed for the mechanism; without it, no rigorous bimodality statement is possible |
| a rigorous bimodality / metastability theorem | requires the previous line |
| formalising the stochastic monitoring process in Lean | out of proportion; `LEAN_PLAN.md` §3 |
| any statement outside the frozen Gaussian core, convention A, `m in {1,2,3,5}` | P8/P8R territory; `FROZEN_SCOPE.md` |
| any statement about adaptive or state-dependent `rho` | `P5-T7`'s own scope restriction |
| re-running or reinterpreting P5's gates `G1`–`G20` | forbidden by the brief and by `FROZEN_GATES.md` `G10` |
| tightening the existing `Gamma` certificates | different priority; P5X imports them as-is |

## 6. Ways this campaign can legitimately fail

Named in advance, each with the verdict it forces.

| failure mode | detection | forced verdict |
|---|---|---|
| certified enclosure of `R` is wider than the `0.409` margin to `2` in the worst cell | gate `G5` | `H3b` unproved → Level C fails → `P5X = PARTIAL`, Level B may still stand |
| the per-`e`-interval resolvent bound degrades badly for `|e|` in the lobe region | gate `G5` | narrow the certified `e`-cover, extend the far-field lemma inward, or report a scoped `sup` |
| `inf_e S` cannot be certified strictly positive | gate `G4` | the high-dispersion **lower** bound fails → mechanism claim reduces to boundedness only → `P5X = PARTIAL` |
| `R'` system too expensive, so `H3a` is not discharged | gate `G5` | report `H2`+`H3b` proved, `H3a` still conditional; P5-T9 uniqueness stays conditional |
| skeleton dynamics uncertifiable except very far from `rho_c` | gate `G3`/`G5` | report the achieved `eta`; does not change the campaign verdict |
| certified constants contradict P5's measured values | gate `G9`, `G10` | **stop**: a genuine contradiction is a defect in the reduction or the certificate, not a discovery |
| the synthesis needs language stronger than the evidence | gate `G12` | rewrite the synthesis, not the evidence |

## 7. The one thing that would kill the campaign outright

If the reduction `P5X-T1` were wrong — if the pre-alarm detector state were not
a sufficient statistic, or the short-`tau` bookkeeping under convention A were
mis-stated — every certified number would be meaningless. The probe is
precisely a falsification test of that: an independent 2-D solve reproducing a
Monte Carlo map produced by a completely different method, in `2 x 4 x 10`
cells, including the non-obvious secondary lobe. It did not falsify it. Gate
`G2` and gate `G9` re-run that test at production quality, and gate `G2`
additionally requires the certified `R'(0)` to match the P3 multiplier.
