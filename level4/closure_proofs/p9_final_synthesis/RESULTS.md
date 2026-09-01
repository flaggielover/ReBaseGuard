# P9 results

P9 ran **no discovery experiment**. Everything below is either a reproduction of
an existing claim, a consistency property of the assembled evidence graph, or a
theorem derived from claims that already existed at the anchor commit.

---

## 1. The finding that governs the campaign

> **The repository contains zero statements defining a Level-4 Priority 9.**

`grep` for `Priority 9`, `PRIORITY 9`, `priority_9`, `priority9` returns **0**
hits. `grep` for `\bP9\b` returns 11, and **all 11** are P5's *premise* label for
`m`-monotonicity — the same collision P8 recorded as its `U1`, but total.

P8, by contrast, had four frozen statements (`F1`–`F4`) that literally defined
it. P9 has none. So P9 is a **prompt-constituted synthesis priority over a
repository-constituted evidence base**, and every scope item is `PROMPT_DERIVED`.
This is declared in `P9_DEFINITION_AUDIT.md` §2 and repeated in
`CODEX_HANDOFF.md` so no reader can miss it.

## 2. The status correction — raised, then settled by the repository

At the anchor commit the campaign prompt asserted `P6 = CLOSED` while the last
record in the P6 namespace read `FINAL_P6_VERDICT = PARTIAL` (`G6`, `G9`, `G12`
`PARTIAL`, `CALIBRATION = LIMITED`), and P6R2b said verbatim *"`P6 = CLOSED` is
**not** declared here."* P9 flagged the conflict and carried every P6 claim at
`PARTIAL`-consistent strength rather than granting an ungranted status.

**The authoritative status table has since been updated to `P6 = CLOSED`**, in
the same pass that produced the P8 verdict. P9 follows it. The residue it still
records: no independent Gate-9 review is documented *inside* the P6 namespace,
so closure is not traceable through `p6r2b_gate9_crn_identity/` alone. Closure
is scope-bound and is **not** novelty — `P6-NOV` stays `NOT_ESTABLISHED`.

## 2b. The authoritative P8 verdict: `FAIL`

Claude's discovery reported `PARTIAL_CANDIDATE`. **It did not survive.** The
adjudicator confirmed the four scientific failures and found a fifth:

> **`G14` fails** — temporal integrity. The directory was untracked with no
> pre-result commit or externally anchored digest; the provenance record does
> not hash `THEORY.md`, `EXPERIMENT_PROTOCOL.md` or `CLOSURE_GATES.md`;
> `config.py` was modified *after* the production artifacts; and the frozen
> protocol's stated E2 sizes (250,000 / 2,048,000 cycles) contradict the
> executed 163,840 / 1,024,000. Amendment `A2` was `RESULT_DRIVEN`.

Under the frozen rule any integrity-spine failure forces `FAIL`, so
`PARTIAL_CANDIDATE` was never available. **P8 failed on preregistration
integrity, not on its science.**

P9 held **no** P8 premise, so no P9 conclusion changed — the reconciliation
removed 6 graph edges and withdrew one provisional row, nothing more. That is
what the quarantine was designed to guarantee
(`P8_TO_P9_RECONCILIATION.md`).

The adjudication's §16 *permits* P9 to use four surviving tiers. **P9 declines**,
keeping the stricter `FAIL` rule it pre-committed to in
`P8_DEPENDENCY_GATE.md` §4.

This verdict also validates a choice P9 made before knowing it:
`EXPERIMENT_PROTOCOL.md` §0 discloses that P9's own gates were written *after*
its reproductions ran, and for that reason `CLOSURE_GATES.md` contains no
post-hoc numerical threshold — only properties verifiable by inspection.

## 3. The claim ledger

`CLAIM_LEDGER.{md,json}` — **65 claims**, **64 typed edges** (58 `premise`, 5
`verifies`, 1 `diagnoses`), **0 validation findings**.

| status | claims |
|---|---:|
| `EXACT_THEOREM` | 16 |
| `CONDITIONAL_THEOREM` | 9 |
| `FORMALLY_VERIFIED` | 3 |
| `CERTIFIED_NUMERICAL` | 3 |
| `EMPIRICAL_REPRODUCED` | 9 |
| `EMPIRICAL_ONLY` | 7 |
| `NEGATIVE_RESULT` | 11 |
| `NOT_ESTABLISHED` | 5 |
| `PARTIAL_PRIORITY_RESULT` | 2 |

Eleven `NEGATIVE_RESULT` and five `NOT_ESTABLISHED` rows are carried at the same
prominence as the positive ones, per `CLAIM_LANGUAGE_POLICY.md` `R3`.

## 4. The typed-edge finding

The no-inflation validator, on its **first** run, rejected the graph:

```text
INFLATION P4-L1 (FORMALLY_VERIFIED, rank 6) exceeds weakest parent rank 5
INFLATION P4-R1 (EMPIRICAL_REPRODUCED, rank 3) exceeds weakest parent rank 1
```

Both were real modelling errors, and fixing them produced P9's one genuinely
non-obvious structural result: **a dependency graph of this project drawn with
untyped edges is unsound.** A Lean or Arb layer is a fact *about* an artifact —
it neither is bounded by, nor licenses, the science it verifies. A diagnosis of
a failed gate is not a consequence of it.

Three edge types were introduced: `premise` (bounds strength), `verifies`
(formal/certified layer), `diagnoses`. Only `premise` enters the bound.
`P1-L1`, `CORE-C1`, `CORE-C2` and `P4-C1` were retyped for the same reason —
`P1-L1` had escaped detection only because its parent happens to be
`EXACT_THEOREM`, which is luck rather than correctness. With typed edges the
ledger validates at **0 violations** and `tests/test_dependency_graph.py`
asserts the distinction is load-bearing rather than decorative.

## 5. `P9-T2` — the separation theorem

> For each frozen detector and each `m >= 1`, at `rho = 0` the invariant law is
> exactly `N(0,1/m)`, the stationary in-control ARL equals `E[A(e)]`, and that
> is **strictly** less than `A(0)`.

`rho = 0` is strictly below `rho_c` for every supported `(D,m)` — it is where the
local map is *maximally* stable, multiplier `0`. So operational degradation is
present at the most locally stable operating point available. **Hence no
threshold in `rho` can be an operational safety boundary.**

This upgrades P7's frozen-criterion **negative empirical result** (`P7-R1`) to
an **exact** statement for the frozen model. It uses only `P5-T1`, `P5-T7` and
`P7-A`, all `EXACT_THEOREM`, and introduces no new premise. Proof in
`THEORY.md` §2.

Its empirical complement, from P6's pre-design exclusion `X1`: the measured ARL
optimum sits `1.25x`–`4.1x` **above** `rho_c`, i.e. inside the locally repelling
region. Local stability and operational quality do not merely fail to
coincide — over the measured grid they point in opposite directions.

## 6. Reproduction

Independent implementation, no P1–P8 imports, deterministic seeds.

| anchor | result |
|---|---|
| A1 P3 exact witnesses | **exact** — all 8 rational boundaries reproduce; `\|rho_c(1-Gamma)\| = 1` exactly |
| A2 P3 Gaussian `rho_c` | max abs diff **`4.882e-10`** (tol `1e-9`); SR-below-CUSUM ordering reproduced |
| A3 P5 raw-mean identity | max abs diff **`8.882e-16`** (tol `1e-12`), 18 cells |
| A4 P7 operational | fresh `78.84–162.11` vs published `79.91–162.03`; **cycle-2 collapse `5.63–8.83` vs published `5.6–9.4`** |
| A5 burn-in | new finding, §7 |
| A6 `P9-T2` mixture + `P7-A` premise | quadrature vs recursive run agree to `0.3–1.6`; **0 monotonicity violations at 3 SE over 320 comparisons** |

Two A4 cells needed investigation rather than assertion, and both were
investigated rather than adjusted: `D-12` (nominal CUSUM `A(0)`, `z = -3.09`;
a second seed gave `467.6`, and P7's own replay range `447–492` contains both)
and `D-11` (see §7).

## 7. `P9-N1` — the transient is oscillatory

Investigating an apparent `45.21` vs `48.36` disagreement with P7 produced a
finding rather than a discrepancy. Mean cycle length **by cycle index** under
full reuse:

```text
SR,    m=1, rho=1:  460.5,  5.8, 73.7, 38.2, 53.6, 46.0, 48.6, 46.4, ... -> ~48.5
CUSUM, m=1, rho=1:  467.6,  5.6, 74.4, 40.3, 54.0, 46.5, 50.5, 47.7, ... -> ~50.0
```

| convention | SR `m=1` | CUSUM `m=1` |
|---|---:|---:|
| discard cycle 1 | `46.96` | `48.34` |
| discard 10 | `48.49` | `49.97` |
| pool all cycles | `67.64` | `69.31` |

At discard-10 the SR value matches P7's `48.36` to `0.13`. The gap was
**entirely a burn-in convention difference**. Pooling all cycles inflates the
estimate by `~40%`.

Consequences: `P5-T7` proves uniform geometric ergodicity but with loose
constants, so the *rate* was not previously pinned — here it is measured, and it
is slow. `P7-E2`'s lesson sharpens: one-cycle calibration is misleading, and so
is few-cycle calibration. Any cross-priority comparison of an operational ARL
must state its burn-in convention (`DEFINITION_CROSSWALK.md` X-08).

## 8. Discrepancies

15 registered. **Twelve resolved, three left `OPEN`.**

Still `OPEN`: `D-09` (the frozen campaign is recorded `CLOSED` while `L4R-11`
remains a MANDATORY `FAIL`), `D-13` (P5-T11's map-vs-chain `ACF1` residual —
`<= 3.5%` but up to **16 chain SE**, isolated to the PCHIP plug-in, "overturned
as unresolved"), `D-15` (P3's grid preregistration cannot be authenticated).

Three were resolved **during** the campaign by events outside P9's control, and
P9 claims credit for none: `D-08` (the owner fixed the stale README), `D-10`
(the status table settled P6), `D-14` (the P8 adjudication settled transfer, in
the negative — detector transfer is **measured absent** and `G7` fails
literally). P9 claims only that it recorded each correctly while it was open,
and revised when the repository spoke.

## 9. Gates and tests

**`G1`–`G14` PASS (14/14).** The verdict rule in `CLOSURE_GATES.md` was fixed
before the P8 outcome was known and has not been adjusted since.
