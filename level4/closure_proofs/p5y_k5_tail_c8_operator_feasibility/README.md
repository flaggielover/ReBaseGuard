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

### Per-cell, under the authoritative C5-T clause and the binding adoption floor

C2's adjudication sets a **binding prospective adoption floor**: **F1** (Γ < 0 also under a
registry-free supply) **or** **F2** (uniform-A margin ≥ 1.25). Closure alone is not adoption. The
correct unit of operator improvement is **one uniform factor on `eff`**, because Lemma Dv′ makes
`A0`, `A1` and `A2` all proportional to it.

| cell | closes now | uniform-A margin | F1 | F2 | adoptable | ×`eff` to close | ×`eff` to be **adoptable** |
|---|---|---|---|---|---|---|---|
| 306 | **yes** | 1.171431 | fail | fail | **no** | — | **1.067071** |
| 307 | no | — | fail | fail | no | 1.096007 | 1.370009 |
| 308 | no | — | fail | fail | no | 1.438423 | 1.798029 |
| 309 | no | — | fail | fail | no | 1.818354 | 2.272943 |

**Cell 306 is the cheapest target in the tail — but it is not free.** An earlier version of this
campaign called its blocker "adoption, not information". That was **wrong**: 306 fails *both* limbs
of a binding floor, and C2's adjudicator anticipated the exact number, writing that 306 reaches
"Γ = −0.036198 with a uniform-A margin of 1.1555 — still short of F2 … a D′ campaign alone will not
discharge this floor." It needs a real **1.067071×** uniform tightening.

**Cell 309 — refuted, but within a stated scope.** The perfect-information oracle for the
atom-constant family fails: the clause tolerates `A0 ≤ 3.266416` and the floor forces
`A0 ≥ 3.586306`. The refutation already held under C4's weaker floor 3.297250, so **C7 widened it
rather than created it**, and this reproduces C4's published exclusion. But it is **not
unconditional**: it holds *within the atom-constant family, at the committed sup norms*. A tightening
of the candidate sup norms voids it — **19.612136 %** against the current floor, and C5 published
**2.0561597 %** against C4's weaker floor, a figure reproduced here exactly. C7's stronger floor made
the refutation roughly 9.5× more robust against that route.

### The route set

| route | lever | leverage | class |
|---|---|---|---|
| R1 | clipping gap | **zero** | LOW_LEVERAGE |
| R2 | cell uniformization | **zero** | LOW_LEVERAGE |
| R3 | operator certification (E1) | closes 306/307/308; **not** 309 | TOOLCHAIN_BLOCKED |
| R4 | order-3 surrogate | closes all four | NEW_REAL_BLOCKED |
| R5 | source-sup norms (C6 route A1) | **voids the 309 refutation** | DATA_BLOCKED |

R5 was omitted from the first enumeration, which therefore wrongly called R4 "the only route with
leverage on 309" — a claim now **withdrawn** in the live artifacts. C5 classifies R5 **DATA-blocked,
not refuted**, and publishes **six** such levers; the cheapest, `all_four_together` at **0.6076 %**,
is cheaper than the sup-norm lever at 2.0562 % that C8 itself found. All six are carried.

Every scaled sweep is `COUNTERFACTUAL_ONLY` and inherits C5's **DIAGNOSTIC** status.

## Selected route for C9

**`NEXT_ROUTE_OPERATOR_CERT` — R3 (E1 operator certification), targeted at cell 307 first**, at a
uniform `eff` tightening > **1.096007×** (1.370009× to be adoptable), then 308 at > 1.438423×.

**Cell 306 is cheaper — 1.067071× — and C8 does not select it.** The frozen gate's rule 1 routes any
cell that passes the clause to *governance* and forbids requesting information for it. That rule
rests on a premise C2's binding floor falsifies, but a campaign does not override a frozen rule in
its own favour, least of all when the override selects the outcome it prefers. Recorded as
`ERRATUM_C8_GATE.md` E1; 306-first becomes available only if governance amends and re-freezes rule 1.
Both numbers are published so the choice can be made on the numbers.

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
