# Campaign C1, Phase C — execution decision: STOP before freeze under the frozen stop rule, with a costed C2 plan

Start frontier `76c37de1` (`p5y-postk1-frontier`), `main` untouched at `1cb45382`, AWS SR/PS1 untouched.
Guard **DENY** throughout. **NEW_REAL_ADDRESSES = 0, NEW_REAL_CPU_HOURS = 0.**

## 1. Verdict

    C1_GATE_COMMIT   = 36d8e39bf2dde7b980853c5c8e7ecdd6cfab2a81   (gate sha256 927ecfc7..., frozen before any forecast)
    C1_CLASS         = MARGINAL
    SELECTION        = STOP_AND_WRITE_COSTED_C2_PLAN
    CERTIFIED closes = {305, 306}      DEGRADED closes = {305}
    material-improvement test = FAIL   (6.716 % fall against a 10 % threshold)
    K5 = PARTIAL, m5 open [305, 309]; coverage map r4 (a3bddd83...) unchanged, no r5

The frozen gate says: `selection_rule` — "below USEFUL is never executed"; `stop_rule` — "if C1 is MARGINAL or
INFEASIBLE, stop before freeze and write a costed C2 continuation plan". Both fire. No freeze, no qualification, no
seal, no consumption, no adjudication, no coverage map.

**C1 was one repaired line away from wrongly reporting EXECUTE.** The first evaluation recorded the
material-improvement test as a 16.1 % fall and the class as USEFUL. The independent pre-freeze review
(`review/REVIEW_C1_PREFREEZE.md`, verdict NOT_READY) found that the test was implemented on a *different quantity*
than the gate states: the gate's baseline 2.252903 is a **uniform atom-constant** reduction factor, while the code
computed `1/margin = M_after/M_needed`, a **magnitude** ratio. Recomputed on the gate's own quantity the fall is
**6.716 %**, and the class is MARGINAL. The gate text was not touched; the code was corrected to match it, which is
the only direction a gate repair may take.

## 2. What C1 certified, and what it bought

All five tail cells certified, each at the first rung of both pre-registered alpha ladders, 1232.2 CPU-s of
operator-only certification, zero new real scientific addresses.

| cell | A0 generic → C1 | A1 | A2 | mag TC-T | M needed | Γ | margin |
|---|---|---|---|---|---|---|---|
| 305 | 7.73 → 6.88 (1.123×) | 1.002× | **0.793×** | 3.947590 | 4.891579 | −0.065100 | 1.239× **PASS** |
| 306 | 7.23 → 6.41 (1.128×) | 1.009× | 0.799× | 3.831264 | 3.905056 | −0.005719 | 1.019× **PASS** |
| 307 | 6.68 → 5.99 (1.116×) | 0.984× | 0.766× | 3.774673 | 3.076148 | +0.061683 | 0.815× open |
| 308 | 6.17 → 5.59 (1.104×) | 0.961× | 0.738× | 3.785137 | 2.432398 | +0.136195 | 0.643× open |
| 309 | 5.78 → 5.21 (1.110×) | 0.971× | 0.746× | 3.723417 | 1.969828 | +0.198810 | 0.529× open |

**The scientific finding of C1 is negative and it is the useful part.** Atom deflation, which bought 2.46× on A0 at
e = 0, buys **1.10–1.13×** at the tail and makes **A2 worse by 1.25–1.36×**. Theorem AD §3 predicted exactly this:
the deflation gain lives in the cross terms where the generic stack multiplies independent copies of C, and at the
tail C_upper is already only 5.78–7.73, so there is nothing large to collapse — while Lemma Dv′ pays
d₂ = D2/D_lo = 22.8–37.1 straight into A2. **The e = 0 precedent does not transfer, and the Campaign-B continuation
note's 2.46× expectation was wrong by a factor of ≈ 2.2.** That is now measured rather than estimated.

Uniform atom-constant reduction still required after C1: 1.000 / 1.000 / **1.262** / **1.663** / **2.102** on cells
305…309, against Campaign B's 1.000 / 1.071 / 1.362 / 1.771 / 2.253. The blocker moved, but not by 10 %.

## 3. Why cells 305 and 306 are *not* adopted

Two cells do close under C1's certified constants, and the gate's `partial_adoption` clause would permit adopting a
subset — but only for a campaign whose class is USEFUL or STRONG. At MARGINAL the selection rule forbids execution
outright, so nothing is sealed, nothing is adjudicated, and coverage map r4 stands unchanged with all five tail cells
open. Cell 305's closure (margin 1.239×, survives DEGRADED) is uncontested and has now been derived twice — by
Campaign B with Lemma G constants and by C1 with Lemma Dv′ — and it remains unadopted for the same reason both times:
no gate has yet been frozen that permits adopting it.

That is the honest cost of the discipline, and it should be named: **the programme has twice computed a sound closure
of cell 305 and twice declined to adopt it**, because each campaign's gate was written to demand more than one cell.
A successor that wants cell 305 adopted should freeze a gate whose universe is cell 305 alone, before computing
anything.

Cell 306 is a different matter. Its margin is **1.93 %** (Γ = −0.005719468 against a curvature penalty of 0.296955),
the frozen DEGRADED probe loses it, and it sits on the one trust surface C1 opened and could not have checked against
prior evidence — the six operator constants on a domain where no certified evidence existed before. The pre-freeze
reviewer's opinion, which this campaign accepts: do not adopt 306 without an independent re-certification of its
operator constants and a stated, pre-frozen margin floor.

## 4. Costed C2 plan

C2 must freeze a new gate before computing anything, and that gate should pre-register the levers C1 left free — the
block width above all (pre-freeze review notes 6 and 11).

### C2-a — finer taboo block partition (the cheapest untaken margin, zero new real addresses)

C1 certified one block per cell, of width 2ρ ≈ 0.081–0.108. The adopted r1 geometry uses 1/100-wide blocks and takes
the worst constants over the sub-blocks meeting a cell. A narrower block admits a tighter supersolution, so C_T and τ
fall, and **A0 = τ/D_lo is where C1's entire gain lives**. Splitting each tail cell into 9–11 sub-blocks is a
mechanical change to `c1_tail_registry` (the block list, not the certification), costs ≈ 9–11× the taboo-block CPU of
C1 (≈ 2.5–3.5 CPU-h, still operator-only) and needs no new machinery.
*Expected*: a further reduction in A0 of unknown size — C1 gives no basis to predict it, and the campaign should not
repeat the mistake of assuming one. It bears directly on cell 306's 1.93 % and on cell 307's 1.262×.
*Does not plausibly reach*: cell 309's 2.102×, on any reading of C1's numbers.

### C2-b — attack D_lo and D2 rather than Ā (zero new real addresses)

Ā is **inert**: Ā_eff = min(Ā, τ/D_lo) = τ/D_lo on all five cells, so the whole-kernel ARL supersolution — about half
C1's build cost — feeds nothing. Every future CPU-second spent on Ā is wasted. The live quantities are τ, D_lo and,
for A2, d₂ = D2/D_lo. D2 = 19.3–28.5 is the single largest contributor to C1's A2 degradation; a sharper certified
d″ bound would remove the one place C1 went backwards.
*Cost*: unknown without a probe; the `taboo_certify.cell_artifact` degree and depth are the levers.

### C2-c — accept that the tail needs the order-3 candidate after all (5 new real addresses)

C1 settles a question Campaign B could not: the operator route alone does **not** reach cells 308 and 309. With
C2-a and C2-b at their most optimistic the remaining factor at 309 is still of order 2, and nothing in the operator
machinery offers that. The remaining levers are the ones Campaign B priced:
- a real order-3 candidate at the tail (Campaign B route T2, ≈ 2.2 CPU-h new-real, 5 new real addresses, guard ALLOW
  required), whose own critical threshold is now better understood — it closes each cell iff the certified order-3
  candidate supremum satisfies s_G ≤ 10.55·s_H at 309;
- a higher-order theorem (order-4 Taylor cell), which would need order-4 source evidence that Aux3 does not provide;
- sparse positive-e certified anchors, priced as INFEASIBLE by Campaign A's route H.

**Recommended sequencing**: C2-a and C2-b first, since they are operator-only and cheap; they will either close 306
and 307 with real margin or demonstrate that they cannot, and either outcome sharpens the case for C2-c. Do not
launch C2-c before C1's successor has re-certified cell 306's constants independently.

### Not recommended

- Re-running C1 with the componentwise minimum of Lemma G and Lemma Dv′ constants. It is sound, it was computed, and
  it closes the same two cells (uniform reduction still required at 309: 2.0749, a 7.90 % fall — still short of 10 %).
- Re-running C1 with a relaxed gate. The gate is frozen and its `no_redefinition` clause is the reason C1's defect
  was caught rather than published.

## 5. Compute accounting

| item | CPU-h | kind |
|---|---|---|
| Campaign A (adopted) | 14.203 | new real |
| Campaign B replay measurement | ≈ 1.87 | replay, not new real |
| **C1 operator certification** | **0.342** | operator-only certification, not new real |
| C1 forecast / K5-B scoring / mutations | < 0.2 | arithmetic |
| **C1 new real** | **0.000** | — |

## 6. Invariants held

- `main` untouched at `1cb45382`; AWS SR/PS1 not contacted at any point.
- Every adopted predecessor namespace byte-unchanged since the start frontier (`evidence/phase_a/`, A4).
- Coverage map r4 (`a3bddd83…`) untouched; **no r5 exists**.
- The C1 gate was committed exactly once, at `36d8e39b`, and is an ancestor of every commit that reports a number.
- Both Campaign B reviews and Campaign A's adjudication are untouched.
