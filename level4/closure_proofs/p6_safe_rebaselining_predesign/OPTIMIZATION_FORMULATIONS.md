# Candidate optimisation formulations for P6

Five mathematically explicit formulations. **P6 is not locked to one.** The
choice is entry-gate item 4/5 and depends partly on the P5 verdict
(`P5_ADJUDICATION_CONTINGENCIES.md`).

Notation follows `SAFETY_OBJECTIVES.md` §1. `U` ranges over a **policy class**
`Ucal` (a parameterised family, not all measurable functions), and every
functional below is a functional of the **policy-induced** law of the chain, not
of a fixed-`rho` stationary law.

> **Standing caveat (`H7`).** Under a state-dependent `U`, `(e_j)` is no longer
> the time-homogeneous chain of `D9`, and `P1` (P5's T7) does **not** transfer
> automatically. Every formulation below is therefore written in two versions:
> a **stationary** version `E_pi_U[.]`, legitimate only in Branch A/B and only
> after `T6-B` supplies a stationary law for the closed loop, and a
> **finite-horizon** version `(1/J) sum_{j=1}^{J} E[.]`, legitimate in every
> branch. When they differ, the finite-horizon version is the one P6 runs.

---

## A. ARL-constrained minimum fresh-sample usage

*"Buy back a stated amount of in-control performance with as few fresh
observations as possible."*

```
minimise_{U in Ucal}     Fresh(U)  =  (1/J) sum_j E[ k_j 1{rho_j < 1} ]

subject to               Arl0(U)   >=  a_target
                         Coll(U)   >=  coll_floor
```

* `a_target` must be stated **relative to a named control** (`S20`, `E1`): e.g.
  `a_target = Arl0(B2*)`, the best fixed-`rho` cell in the frozen grid at the
  same `m`. An absolute target near nominal `465` is unreachable and would make
  the problem infeasible everywhere (`S4`).
* **Strength.** The cleanest economic statement, and the constraint is a closed,
  directly measured quantity.
* **Weakness.** Ignores the delay tail entirely, which `S9` says is where the
  damage is. Must never be run alone.

## B. Delay-tail-constrained maximum reuse

*"Reuse as much as possible without letting the catastrophic-delay probability
exceed a stated level."*

```
maximise_{U in Ucal}     FracReuse(U)   (equivalently: minimise Fresh(U))

subject to               Dtail(L; Delta)  <=  alpha        for each Delta in Dgrid
                         Arl0(U)          >=  a_target
```

* This is formulation A with the objective and the binding risk swapped so that
  the **tail** is the hard constraint. It is the formulation that takes `S9`
  most seriously.
* **Strength.** Directly encodes the closed failure mode.
* **Weakness.** `Dtail` is expensive to estimate (`COMPUTE_PLAN.md` §5), and the
  constraint must hold over a *grid* of `Delta` because `Delta` is unknown at
  design time as well as at decision time (`H8`). A policy tuned at one `Delta`
  and evaluated at the same `Delta` is a leakage failure (`F8`).

## C. Reference-dispersion-constrained reuse

*"Keep the reference law inside the ARL-calibrated tolerance region, then reuse
freely."*

```
maximise_{U in Ucal}     FracReuse(U)

subject to               OutCal(beta; U)  =  P( |e| > c_beta )   <=  gamma
```

with `c_beta` the calibrated radius of `SAFETY_OBJECTIVES.md` §3.1.

* **Strength.** The constraint is cheap, low-variance and, unusually for a
  surrogate, is tied to monitoring by the *exact* `S1` rather than by analogy.
  It is also the only formulation with a plausible route to a **theorem**
  (`P6_THEORY_TARGETS.md` T6-A/T6-D).
* **Weakness.** It is still a surrogate constraint. `S18` forbids concluding
  from `OutCal <= gamma` that any monitoring metric is controlled. The
  monitoring metrics must be measured anyway, which raises the question of why
  they were not the constraint in the first place. **Recommended role: the
  formulation P6 *derives theory* about, not the one it gates on.**

## D. Composite risk objective

```
minimise_{U in Ucal}   Risk(U) = w_D * Dtail_norm(U) + w_A * ArlDeficit_norm(U)
                                + w_F * Fresh_norm(U)
```

with each term normalised against the corresponding value at full reuse
(`rho = 1`), so `Risk(full reuse) = w_D + w_A + w_F` and lower is better.

* **Strength.** Single scalar, so screening and early-stopping are trivial
  (`COMPUTE_PLAN.md` §4).
* **Weakness.** The weights `w` are not derivable from anything in the ledger.
  Choosing them after seeing results is a post-hoc selection failure (`F7`).
* **Permitted role:** as a **screening** scalar only, with weights frozen before
  any screening data are seen, and with the explicit statement that no closure
  claim rests on `Risk`. It must not appear in Tier 1 or Tier 2 of
  `SAFETY_OBJECTIVES.md` §4.

## E. Pareto frontier over monitoring quality vs data reuse

```
Frontier = { U in Ucal :  no U' in Ucal with
             Dtail(U') <= Dtail(U),  Arl0(U') >= Arl0(U),
             Fresh(U') <= Fresh(U),  with at least one strict
             and all three differences resolved at the preregistered
             paired-CI level }
```

Reported as the non-dominated set in the 3-space `(Dtail, Arl0, Fresh)`, with
the baselines `B0`–`B6` and the oracle ceiling (`P6_METHOD_CANDIDATES.md` §4)
plotted on the same axes.

* **Strength.** Makes **no** arbitrary trade-off; the dominance test is
  uncertainty-aware by construction; and it is robust to the P5 verdict because
  it needs no stationary-law quantity.
* **Strength (methodological).** It removes the pressure to declare a winner,
  which is where prescriptive campaigns usually fail. "P6 produced a frontier
  and an oracle ceiling" is a complete and defensible scientific result.
* **Weakness.** Estimating a frontier with uncertainty needs care: naive
  non-dominance over noisy point estimates over-selects. The dominance test
  above must use paired CIs, and the frontier must be reported with a
  membership-uncertainty statement (`STATISTICAL_DESIGN.md` §6).

---

## Recommended pairing

| stage | formulation | why |
|---|---|---|
| screening | **D** with frozen weights | one scalar, cheap early-stop |
| shortlist | **A** and **B** run as a pair | they bracket the trade-off from both sides; disagreement between them is itself informative |
| confirmation | **B** | takes the closed failure mode `S9` as the binding constraint |
| headline scientific output | **E** | no arbitrary weights, no forced winner |
| theory | **C** | the only formulation with a tractable theorem target |

Nothing here is frozen. The gate freezes it.
