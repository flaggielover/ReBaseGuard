# P5Y — K2–K5 FORWARD AUDIT (design only; K1 untouched)

**K1 was not run, not modified, not resumed, and no second K1 successor was
created.** `P5Y_K1_SUCCESSOR_PRODUCTION_RUN = NO`.

## The headline

The remaining **load-bearing** work on the P5 line is **K1 + K4 + K5**. K4 and
K5 are near-free riders on K1. K2 and K3, as named in the P5Y campaign, are
**not hypotheses of the authoritative theorem**.

## Authoritative hypotheses (`p5_nonlinear_dynamics/THEOREM.md`)

```text
(H1)  R continuous and odd                       ALREADY EXACT (P5-T3)
(H2)  R(e) < 0 for all e > 0                     open  = K4
(H3a) s(e) = -R(e)/e continuous and STRICTLY
      DECREASING on (0,2], s(0+) = GammaTilde-1
      = 1/rho_c, s(2) < 1                        open  = K5
(H3b) sup_e |R(e)| < 2                           open  = K1 = gate G3
T10 additionally requires: S continuous at 0
```
T8 is conditional on (H1,H2); T9 and T10 on (H1–H3).

## Four corrections to the brief's summaries

1. **H2 is global**, `R(e) < 0` for *all* `e > 0` — not "on a frozen positive
   near-zero interval". What is *load-bearing* is `(0,2]`, and that reduction is
   licensed by K1, not by a near-zero restriction.
2. **H3a is strict monotonicity** on `(0,2]`, not "attains each level exactly
   once". The audit records level-attainment as a legitimate *weakening*;
   adopting it as the target would substitute the theorem and needs an explicit
   pre-registered decision.
3. **K2 (`inf_e S(e) > 0`) is not a hypothesis of T8/T9/T10.** T10 consumes only
   *S continuous at 0*. And `V = rho^2 S(e) + (1-rho)^2/m >= (1-rho)^2/m > 0`
   for every `rho < 1`, so positivity of `S` can bind only at `rho = 1`, and
   there only at the branch point.
4. **K3 (`M2 < infinity`) is already closed, exactly.** `P5-T5` is an EXACT
   THEOREM giving `E[Rbar^{2p}|e] <= (2p-1)!! C_D`; at `p = 1` that *is* `M2`,
   with `C_D` explicit and finite from `P5-T4` (`C_CUSUM <= 9.8959e8`,
   `C_SR <= 1.4054e11`). What is open is only whether anything downstream needs
   a *non-vacuous* `M2`.

## Dependency DAG — the load-bearing edges

```text
K4(H2)  -> K1(H3b)   MATHEMATICAL   for e >= 2, |R| < 2 <= e already excludes a
                                    positive fixed point of f_rho = rho R, so H2
                                    only has to be certified on (0,2]
K4      -> K1 cells  CERTIFICATE    proof path = certified R on a cover of
                                    [e_0,2] + certified R' < 0 on [0,e_0]
K5(H3a) -> K4        MATHEMATICAL   s = -R/e > 0 on (0,2] requires R < 0 there
K5      -> K1 cells  CERTIFICATE    s'(e) = (R - e R')/e^2 < 0 cellwise needs
                                    BOTH R and R' enclosures
K3      -> K1        NO DEPENDENCY  P5-T5/T4 are exact and independent of H1-H3b
K2      -> theorem   GOVERNANCE     the consumed statement must be re-resolved
```

**Verified, not assumed:** the frozen K1 DAG already solves `dF_0..dF_4` (10
resolvent solves per detector), and the K1 covers are `[0, 5.5]` (CUSUM) and
`[0, 6.7555]` (SR) — both strictly containing `(0,2]`.

## The one action that must be taken before T2S

**The frozen K1 cell record does not carry the per-cell `R` and `R'`
enclosures.** It carries 21 fields — residuals, budgets, radii, P1, timings —
but not the assembled `R` and `R'` intervals that K4 and K5 consume.

```text
if K1 emits them   K4 and K5 become assembly passes          ~0 incremental CPU-h
if it does not     K4/K5 need a second full K1-scale campaign  ~620 CPU-h
```
Emitting them is a **reporting** change, not a scientific one — K1 computes
these values anyway. But the successor checkpoint is FROZEN with
`POST_FREEZE_AMENDMENT_ALLOWED = NO`, and this task forbids creating another K1
successor. **So this is a decision for the operator, not an action I may take.**

## Checkpoint readiness

| K | status | reason |
|---|---|---|
| K2 | `BLOCKED_BY_THEOREM` | `inf_e S(e) > 0` is not a hypothesis of T8/T9/T10; the consumed statement must be re-resolved before a checkpoint can be framed |
| K3 | `BLOCKED_BY_THEOREM` | finiteness already closed exactly by P5-T5/T4; whether a non-vacuous `M2` is consumed anywhere must be adjudicated before spending ~620 CPU-h |
| K4 | `BLOCKED_BY_K1` | architecture fully determined; every numerical input is a K1 production artifact and K1 is `NOT_RUN` |
| K5 | `BLOCKED_BY_K1` | same inputs, plus a dependency on K4 |

No micro-pilot was run: no K2–K5 uncertainty is resolvable by compute. K4/K5 are
blocked on artifacts, not knowledge; K2/K3 on a theorem question.

## Reuse warning

First-moment machinery does **not** automatically certify second moments. The
second-moment reduction has its own backward functions, its own resolvent and
its own cross terms. Nothing in the K1 stack certifies `E[Rbar^2]`.
