# P4ZA Phases 7–9 — the 32 K3 cells, and the unbounded-score question

## 1. Why K3 fired at all

`K3` compared each configuration's measured per-path relative standard
deviation against **twice** its regime envelope, where the envelope came from
P4Z's feasibility micro-pilot.  P4Z's own Stage-0 report already recorded the
diagnosis and refused to re-tune it:

| regime | measured / predicted | verdict |
|---|---|---|
| heavy (`t1p5`) | 0.81 – 1.14 | envelope accurate |
| moderate (`t3`) | 0.76 – 1.01 | envelope accurate |
| light, symmetric | 1.58 – 2.32 | envelope **under-predicts** |
| `skewnormal4` | 2.88 – 12.39 | envelope badly wrong |

Two causes, both in the envelope and neither in the estimator: the light
envelope was fitted on **one** cell (`reduced/cusum@2/gaussian`) and applied
across two layers and two detectors, and that cell's RB-MAP leg was measured on
**four** batches.  On the very cell it was fitted to, the envelope reads 1.110
against a measured 2.293.

`K3` is therefore a *calibration* gate that failed, not a *validity* gate that
failed.  But it did fail, and P4Z reported the cells `INCONCLUSIVE` rather than
relaxing it — which is why they are still open.

## 2. Taxonomy of the 32

| category | cells | configurations |
|---|---|---|
| **A — bounded score, envelope simply weak** | 12 | `frozen/cusum@5/laplace`, `reduced/sr@20/logistic`, `reduced/cusum@2/gaussian` |
| **A′ — unbounded but at most linear score (Gaussian)** | 4 | `reduced/sr@20/gaussian` |
| **B — genuinely unbounded score, asymmetric family** | 16 | `frozen/cusum@5/skewnormal4`, `frozen/sr@520.886/skewnormal4`, `reduced/cusum@2/skewnormal4`, `reduced/sr@20/skewnormal4` |
| **C — extrapolation-only configurations** | 0 | none: every affected configuration was measured directly at Stage-0 |
| **D — carrying no unresolved scientific claim** | 0 | all 32 are theorem-supported cells inside the frozen 96-cell scope |

Category `A′` is separated from `A` because the Gaussian score `psi(z) = z` is
unbounded, so the *bounded-score* discharge lemma L3 does not cover it either —
it is covered by L4, exactly as `skewnormal4` is.  Lumping it with the bounded
families would have hidden that.

## 3. The unbounded-score question, and why it is not fatal

RB-SCORE's moment argument, as P4Z stated it in `rbscore.py`, reads:

> `|B_{n,m}| <= (m-1) c_D` and `|P_{n-1}| <= M (n-1)` **for a bounded-score
> family**, so `|h_n| <= C n` and the per-path value is bounded by `C tau^2`.

The clause "for a bounded-score family" is doing real work, and for
`skewnormal4` — and for `gaussian` — `score_bound` is `None`.

**The bounded-survival lemma removes the difficulty.**  `P_{n-1}` is a sum over
`t < n` of `psi(Z_t)` where every `Z_t` is a **surviving** residual, and the
lemma (formalised in P4Z's Lean, 12 declarations, standard axioms only) gives
`|Z_t| < c_D` for every survivor.  So only the score's values on the compact
interval `[-c_D, c_D]` ever enter, and

```text
M_eff := sup_{|z| <= c_D} |psi(z)|  <  infinity
```

serves in place of a global bound.  The argument then proceeds verbatim with
`M_eff` for `M`.  Nothing about global boundedness is needed.

The same substitution covers `J2` and `J3`, whose integrands run over the
*unbounded* alarm set: both reduce to values of `f` and `F` at the two
endpoints, `J3 = f(U) - f(L)` and `J2 = F(L) - L f(L) + U f(U) + 1 - F(U)`, and
are bounded by constants depending only on `c_D` and `sup f`.  `J1` is bounded
by `E|eps|`.

Measured effective bounds:

```text
skewnormal4, cusum@5      c_D = 5.5000   sup|psi| on survival = 29.3763
skewnormal4, sr@520.886   c_D = 6.7555   sup|psi| on survival = 37.8806
```

That also explains the *magnitude* of the K3 miss without appealing to
anything: `M_eff` for `skewnormal4` is roughly thirty times the bounded-score
families' constant, so the variance scale is genuinely far larger.  The
envelope did not model it.  The estimator was never invalid.

## 4. The score is at most linear, which is what the frozen theorem needs

`skewnormal4` has `psi(z) = sd * (y - alpha * phi(alpha y)/Phi(alpha y))` with
`y = mean + sd * z`.  By the Mills ratio, `phi(x)/Phi(x) -> |x|` as
`x -> -infinity` and `-> 0` as `x -> +infinity`, so

```text
psi(z) / z  ->  sd                  as z -> +infinity
psi(z) / z  ->  sd * (1 + alpha^2)  as z -> -infinity
```

Measured, against the prediction:

| | measured slope | predicted |
|---|---|---|
| right tail | 0.4009 → `sd` | `sd = 0.633110` |
| left tail | 6.8133 at `z = -10^4`, still rising | `sd * 17 = 10.7629` |

Growth is **exactly linear** in both tails — never super-linear.  That is
precisely hypothesis **L4** of the frozen `THEOREM.md` §8:

> **L4 (light tails, at most linear score).**  If `|psi(z)| <= M0 + M1|z|` with
> `M1 > 0` and `E[e^{a|eps|}] < infinity` for some `a > 0` …

and §8's own Coverage paragraph already states: *"L4+L1+L2 discharge Gaussian,
Laplace, logistic and the **skew-normal**."*

So the frozen theorem covers `skewnormal4` and `gaussian` by L4.  `score_bound
= None` records only that the *bounded-score* route L3 is unavailable; it never
meant the family was outside the theorem.  P4Z's `rbscore.py` docstring stated
its moment argument in terms of L3 alone, which was an incomplete statement of
a correct result rather than a defect in the estimator.

## 5. Verdict on Phase 9

```text
SKEWNORMAL4_ROUTE = RB_SCORE_EXTENDABLE_BY_INTEGRABILITY_PROOF
```

No alternative estimator is needed, no scope exclusion is invented, and RB-MAP
is not pressed into service as a substitute.  The extension is a consequence of
a lemma that was already proved and already formalised before any of these
results were seen, applied to a hypothesis (L4) the frozen theorem already
records for this family.

This disposition was reached from the analytic form of the score and from the
frozen theorem's own discharge lemmas — **not** from the numerical stability of
any experiment, which Phase 9 explicitly forbids as a justification.

## 6. What P4ZA must therefore do for the 32

Nothing about validity; everything about calibration and precision.

* Re-derive the regime envelope from `M_eff` and the frozen theorem rather than
  from a single pilot cell (Phase 8).
* Run all 8 affected configurations to the **full frozen 200 blocks** — P4Z
  only ever gave them 20, so there is no full-precision evidence for them in
  any campaign.
* Apply the unchanged frozen gate.

## 7. One formal addition, and its limit

The integrability argument in §3 needs one statement that P4Z's Lean does not
yet carry: that a continuous score restricted to the compact survival interval
attains a finite bound, and that this bound is what enters the estimator.  The
first half is elementary; the second is a statement about the estimator's
construction rather than about the theorem.

`FORMAL_ADDENDUM.md` records what is formalised and what is deliberately left
as ordinary mathematics.  No `sorry`, no new axiom.
