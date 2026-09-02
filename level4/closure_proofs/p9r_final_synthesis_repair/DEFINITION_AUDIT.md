# P9R definition audit

Written **before** any P9R result exists. Its purpose is to fix every term the
campaign uses, so that a later result cannot quietly redefine one.

## 1. What P9R is

P9R is a **repair campaign** for Priority 9. Its mandate is bounded by the
authoritative P9 adjudication's list of defects. It is not a new grand theory
campaign, not a re-adjudication of P1-P8, and not a global Level-4 closure
audit.

Success does **not** require proving every open global claim. Narrowing a
theorem is acceptable. A negative or conditional conclusion is acceptable.
Claim inflation is not.

## 2. Authoritative inputs, verified at the anchor

| object | value | verified how |
|---|---|---|
| P9 verdict | `PARTIAL` | `p9_final_synthesis/results/independent_adjudication.json::final_p9_verdict` |
| P9 adjudication commit | `a3e3cabc30c4508b866736aeede54db17e5e1fcc` | `git log -- level4/closure_proofs/p9_final_synthesis` returns exactly this one commit |
| P8 verdict | `FAIL` | root `README.md` status table; `5411e2c` |
| P8R verdict | `CLOSED` | `p8r_temporal_integrity_repair/results/independent_adjudication.json::verdict` |
| P8R adjudication commit | `dc8516732c2c5672987a6a5a22c1ce023c77f68f` | repository `HEAD` and `origin/main` at the anchor |
| P4, P5 | `PARTIAL` | root `README.md` status table |
| P1, P2, P3, P6, P7 | `CLOSED` | root `README.md` status table |
| P9 namespace unchanged since adjudication | yes | `git diff a3e3cab HEAD -- level4/closure_proofs/p9_final_synthesis` is empty |
| no later commit repairs P9 | yes | no `p9r`/`P9R` namespace existed before this one |

## 3. Terms

**Frozen detector `D`.** Exactly one of: two-sided CUSUM with `k = 1/2`,
`h = 5`, inclusive post-update alarm; symmetric two-chart SR with
`A = 520.886133602749`, **no headstart** (`R_0 = 0`), inclusive post-update
alarm on the raw state. Nothing else is a frozen detector.

**Convention A.** No minimum dwell, `tau = inf{t >= 1 : alarm}`; reuse window
`w = min(m, tau)` with denominator `w`; `e_{j+1} = rho (e_j + zbar_w) + (1-rho) F`
with `F ~ N(0, 1/m)` drawn independently of the stopping event; detector state
reset to the no-headstart initial state at every cycle boundary. Convention B
(fixed-`m` denominator), the Stage-A minimum-dwell process for `m > 1`, and the
Track-1B random-window convention are **different objects**, not repairs.

**`A(e)`.** `E_e[tau]` for one cycle from the reset state at constant entering
reference error `e`. It depends on the detector only.

**`ARL_0`.** The stationary in-control expected cycle length of the
repeated-cycle chain, i.e. `E_pi[A]` for the chain's entering-error law `pi`.

**Nominal `A(0)`.** The single-cycle response at a *perfect* reference. It is a
different control from `rho = 0`, and P9R never conflates the two.

**Estimator convention.** The statistical unit is the **replicate**. Cycles
within one replicate are dependent and are never pooled as independent
observations. The reported ARL is the mean over replicates of the per-replicate
mean cycle length after `burn_in` cycles. `burn_in` is taken from the
authoritative P7 cell, not chosen by P9R.

**MC agreement language.** `z = (a - b) / sqrt(se_a^2 + se_b^2)`;
`MC_CONSISTENT` at `|z| <= 3`, `MC_TENSION` at `|z| <= 4`, `MC_DISAGREEMENT`
otherwise. "Exact agreement" is never used for a Monte Carlo comparison.

**`ASM-DOM`.** `A(e) <= A(0)` for `N(0,1/m)`-a.e. `e`. The single premise
separating `P9R-T2b` from an exact theorem.

**`GLOBAL_MONOTONICITY`.** One of `PROVED`, `EMPIRICALLY_SUPPORTED`,
`NOT_ESTABLISHED`, `FALSE`, decided in `RESULTS.md` from the monotonicity audit.
`EMPIRICALLY_SUPPORTED` entails "not proved" and never licenses an exact claim.

## 4. Claim classes and edge types

Frozen in `experiments/ledger_schema.py` before production. Ten claim classes,
eleven edge types, one rank table, fifteen validator rules. No class, type, rank
or rule may be added after results are seen. See `CLAIM_LANGUAGE_FIREWALL.md`
for the wording each class licenses.

Node **kinds** (`DEFINITION`, `ASSUMPTION`, `CLAIM`, `STATUS`) are a separate
axis from claim classes. A `DEFINITION` and a `STATUS` carry no claim class at
all, which is how P9R keeps a frozen convention or an adjudicated verdict from
being read as scientific evidence.

## 5. Source classification rules

A claim's class is derived from its **cited source**, not from what a downstream
document would like it to be:

* `EXACT_THEOREM` requires that every hypothesis is either part of the frozen
  model definition or discharged for the frozen model *within the cited source*.
* `CONDITIONAL_THEOREM` is required whenever at least one hypothesis is stated
  but not discharged for the frozen model.
* `FORMALLY_VERIFIED` requires kernel evidence recorded in the source
  (declarations, axiom audit, absence of `sorry`). Exact arithmetic and
  interval certificates are **not** formal verification.
* `CERTIFIED_NUMERICAL` requires an interval/enclosure certificate, and its
  statement is about a *number*, never about a bridge or a campaign.
* `EMPIRICAL_REPRODUCED` requires an independent replay; `EMPIRICAL_ONLY` is
  everything else measured.
* A claim inside a `PARTIAL` or `FAIL` priority keeps its own class but is
  usable downstream only at its adjudicated tier and scope.

Two source-derived reclassifications follow immediately and are recorded as
**downgrades**, not repairs of the source campaigns:

* `P3-X1` — `FORMALLY_VERIFIED` -> `CERTIFIED_NUMERICAL`. P3's own
  `LEAN_CORRESPONDENCE.md` states the Priority-3 Lean file "makes no numerical
  claim"; the witnesses are exact `Fraction` arithmetic plus an Arb enclosure.
* `P1-T1` — `EXACT_THEOREM` -> `CONDITIONAL_THEOREM`. P1's own
  `DEFINITION_AUDIT.md` §4 says the integrability and domination obligations are
  discharged *from an assumed* stopped exponential-moment bound. P2-T1 stays
  `EXACT_THEOREM` because `ASSUMPTION_DISCHARGE.md` proves all eight concrete
  obligations. Neither reclassification changes P1's or P3's authoritative
  `CLOSED` campaign status, and neither is load-bearing for `P9R-T2a`.

## 6. What P9R may and may not use

* It **may** use exact P1-P7 content at its adjudicated tier.
* It **may** cite P8 surviving evidence as P8 evidence, and P8R evidence as
  P8R evidence.
* It **may not** treat `P8R = CLOSED` as converting `P8 = FAIL`, nor as
  implying universal model-class transfer.
* Its core theorems `P9R-T2a`/`P9R-T2b` **do not depend on P8 or P8R at all**;
  this is asserted as gate `I12` and tested.
* It **may not** use grid evidence to discharge `ASM-DOM`.
