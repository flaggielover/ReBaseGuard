# C8 — Operator-Information Feasibility and Route Selection

**Not a closure campaign.** C8 adopts no cell, closes nothing, and executes no route. It answers one
question: after C7, what is the **minimum additional operator information** that can materially
advance the remaining K5 CUSUM m=5 tail?

Guard **DENY**. New-real **0**, kernel evaluations **0**, operator certifications executed **0**,
remote contacts **0**, toolchain provisioned **0**.

## Authoritative state

`m=5` open is **{306, 307, 308, 309}**, reconstructed from the per-cell verdicts of
`K5_COVERAGE_MAP_R5.json` (blob `f978eeb6…`), not from its summary ranges. `m=1`, `m=2`, `m=3` are
complete at 310 cells each.

**Correction inherited from C7.** C7's prose said "m=5 open on [305,309]". That is wrong: r5 records
cell 305 as `PASS`, in `newly_passing`, and in `adopted_cells`. C8 uses the artifact.

`LOCAL_MAIN_REF` `c123b9bb…` and `REMOTE_MAIN_REF` `1cb45382…` were recorded **separately**. They
differ; local main is behind. C8 does not synchronize or modify main.

## The answer

The decision clause is `Γ_k = g_hi + ρ·x_hi·M`, pass iff `Γ_k < 0`, with the atom constants entering
**only** through `M`. C8 rebuilt it from committed evidence and validated the rebuild twice before
evaluating any counterfactual: it reproduces all **twenty** committed `(A, Γ)` supply tuples to
2e-17, and reproduces C5's own per-cell `M_used` to 2.5e-16. Its cell-309 `A0` ceiling,
`3.266415728`, independently equals C5's published `critical_A0_C5T`.

### The central structural fact

`Λ` is a **lower** bound on `E_a[τ]`; `A0` is an **upper** bound on the same quantity. `Γ` depends on
`A0` and **never on `Λ`**. By Lemma SM(d), `Λ` enters the decision only as the **floor** below which
no admissible `A0` can go.

Routes **R1** (clipping gap) and **R2** (cell uniformization) both *raise* `Λ`. Raising a floor cannot
lower `Γ`. Measured, not asserted: perfect information in either changes `Γ` by exactly **0.000000000**
at every open cell.

> **R1 and R2 have zero leverage on closure.** They are exclusion-strengthening routes — which is
> what C7 was. They cannot close a cell.

### Per-cell, under the authoritative C5-T clause

| cell | `M_used` | `M_needed_C5T` | verdict | cheapest sufficient fact |
|---|---|---|---|---|
| 306 | 3.438037494 | 3.952942541 | **ALREADY PASSES** | none — the blocker is **adoption** |
| 307 | 3.374598932 | 3.114961361 | FEASIBLE | `A0` 5.597996 → ≤ 4.996766 (**1.1203×**) |
| 308 | 3.371647050 | 2.463911270 | FEASIBLE | `A0` → floor **and** `A1` ≤ 17.632791 (1.2927×) |
| 309 | 3.319524453 | 1.995669915 | **MATHEMATICALLY REFUTED** | none within the atom-constant family |

**Cell 309.** The perfect-information oracle — `A0` at its certified floor with `A1 = A2 = 0`,
strictly better than any certification could supply — still fails. The clause tolerates
`A0 ≤ 3.266416`; the floor forces `A0 ≥ 3.586306`. The refutation already held under C4's weaker
floor 3.297250, so **C7's strengthening widened it rather than created it**, and C8 claims otherwise
nowhere. This reproduces C4's published exclusion of 309; C8's contribution is extending the same
test to 306, 307 and 308, which C4 did not decide.

**Cell 306 is the cheapest result in the tail and costs nothing.** It passes the authoritative clause
under committed certified supplies *today*. It is listed OPEN in r5 only because C2's adjudication
was `PARTIALLY_ADOPTED` and adopted 305 alone. No new science should be bought for it.

### A fourth route, recorded rather than omitted

The frozen TC-T rule accepts an `order3` argument, and committed evidence
(`C2_CRITICAL_RATIOS.json`, `Gamma_perfect_order3`) shows perfect order-3 information closes **every**
open cell including 309, at `Γ = −0.089759481`. It is the only route with leverage on 309 — and it is
**true new-real** (B1/D4), forbidden by the C8 boundary and by the gate's rule 4 while a competitive
zero-new-real route is untested.

## Selected route for C9

**`NEXT_ROUTE_OPERATOR_CERT` — R3 (E1 operator certification), targeted at cell 307 first.**

A `1.1203×` tightening of a single quantity is the smallest sufficient information requirement
anywhere in the tail, and the certified floor `3.734070` leaves ample room.

**The risk is not CPU.** C2 measured its own refinement as *non-monotone*: `D_lo` improved but `τ` got
1.90–2.24 % **worse**, and the net `A0` gain was only 4.5–4.9 %. The 1.1203× is therefore **not
guaranteed by buying more CPU**, and no host profile can make it so.

**Host profiles** (estimates extrapolated from one committed measurement, not a benchmark):

| profile | cores | RAM | scope | CPU-h | wall-h |
|---|---|---|---|---|---|
| MINIMUM | 2 | 4 GB | 307 + 308 only | 10.76 | 7.18 |
| RECOMMENDED | 8 | 16 GB | all four, deeper sweep | 43.06 | 7.18 |
| FAST | 32 | 64 GB | same scope as RECOMMENDED | 43.06 | 1.79 |

Toolchain, read from committed pins and not by querying anything: python 3.12.3, numpy 2.5.2,
python-flint 0.9.0, FLINT 3.6.0 (Arb subsumed). **No certifying host exists in scope** — the local
machine lacks all six libraries, C6 re-measured the programme's worker and found the same, and AWS is
forbidden. Host provisioning is a separately governed prerequisite requiring the user's decision.

## What C8 does not claim

No cell is closed or adopted. K5 is not complete. Broader deterministic exhaustion is **not**
established. The R-stage prerequisite is **not** satisfied. No counterfactual is evidence.

## Layout

    config/DECISION_GATE_C8.json    frozen at 55e74332 BEFORE any result artifact
    code/c8_chain.py                exact reconstruction of the downstream clause + 20-supply check
    code/c8_routes.py               phases 1-5: DAG, gap anatomy, inversion, oracles
    code/c8_decision.py             phases 8-10: C5-T inversion, toolchain, frontier, selection
    code/c8_mutations.py            phase 11: 18 planted bad decisions
    code/c8_factcheck.py            phase 14: mechanical checks + load-bearing claim ledger
    code/c8_b0_audit.py             18-check state audit, no tautologies, UNCHECKED never counts PASS
