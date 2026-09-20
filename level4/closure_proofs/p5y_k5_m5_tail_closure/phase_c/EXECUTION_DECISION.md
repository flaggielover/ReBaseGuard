# Campaign B, Phase C — execution decision: STOP under the frozen stop rule, with a costed continuation plan

Start frontier `3c1c6b9c` (`p5y-postk1-frontier`), `main` untouched at `1cb45382`, AWS SR/PS1 untouched.
Guard **DENY** throughout; **no new real scientific value was computed** in this phase and no new real address exists.
Numbers in this document are the repaired ones of review r1 (note N1); `review/REVIEW_R1.md` records what changed.

## 1. Verdict

    TAIL_TARGET              = CUSUM m = 5, cells 305, 306, 307, 308, 309
    TAIL_SELECTED_ROUTE      = T2 (theorem TC at the 5 tail cells)  -- INVALIDATED, see section 3
    TAIL_FEASIBILITY_GATE    = MARGINAL at the frozen audit's own inputs and with every supremum measured;
                               INFEASIBLE with the order-3 scale taken from adopted evidence
    CAMPAIGN_B_EXECUTION     = STOPPED before freeze, by config/FEASIBILITY_GATES_B.json `stop_rule`
    NEW_REAL_ADDRESSES       = 0        NEW_REAL_CPU_HOURS = 0
    K5                       = PARTIAL  (m = 5 open on [305, 309]; coverage map r4 unchanged, no r5)

The frozen gate file, written before any Campaign-B forecast, says:

> `selection_rule`: "highest class; among equal classes prefer zero new real addresses, then fewer new-real
> CPU-hours; **below USEFUL is never executed**"
> `stop_rule`: "if every route is MARGINAL or INFEASIBLE, **stop Campaign B execution and write a costed
> continuation plan**"

Every route scores below USEFUL. The stop rule fires. The gate was not amended, reinterpreted or re-scored after the
numbers were seen; it was applied mechanically by `code/tail_forecast_r2.py::classify`.

## 2. What was measured (Phase B0/B1, read-only and replay-only)

`evidence/measurement_r1/` — an identity-gated **replay** of the theorem-TC input fields of cells 305–309 that the
adopted K1 record does not store (`cert.norms.k/j`, `sup_S0`, `sup.{F,D,H}`, `Ĥ_r(a)`, the whole-cell W enclosures),
plus `ADOPTED_TAIL_INPUTS.json`, a manifest-checked verbatim copy of the adopted record fields the tail arithmetic
consumes. ≈ 6 740 CPU-s ≈ **1.87 CPU-h of replay** — not new-real: no order-3 candidate of F is proposed and the
gated order-3 entry points are never reached. Gates:

| gate | result |
|---|---|
| frozen producer identity gate (262 fields vs the sealed K1 record, per cell) | identical, 5/5 |
| derived identity gate (rebuild the record's `R2_interval` for every m from Ĥ_r(a), W and the record's own `eps_cell_refined`) | contained, worst normalised endpoint gap 3.63·10⁻⁸ (tolerance 10⁻⁶), 20/20 |
| adopted-state replay gate (no tail route) reproduces the sealed Campaign-A consumption `1fa8d8de…` pass ranges | PASS, all four m |
| `ADOPTED_TAIL_INPUTS.json` field-by-field against the live adopted records | PASS, all fields, 5/5 |
| two independent theorem-TC-T paths (no shared function since note N15) agree as exact rationals | 20/20 |

`norms.k/j`, `sup_S0` and the order-0 `sup.{F,D,H}` are covered by neither gate *directly*; they are covered
indirectly, because they feed the gated residual and Aux3-eps computations. That is the measurement's residual trust
surface and it is stated in `evidence/measurement_r1/MEASUREMENT_NOTE.md` rather than glossed.

The measurement overturns the candidate-supremum assumptions the frozen route comparison made:

| quantity | frozen route comparison (assumed) | measured / adopted evidence |
|---|---|---|
| s_H (order-2 candidate sup) | ≈ 5 | **0.5723 – 1.3345** (measured, 25 objects) |
| s_D, s_F | not stated (2, 1 used here to reconstruct it) | 0.2981 – 0.6952, 0.1843 – 1.0789 (measured) |
| s_G (order-3 candidate sup) | ≈ 10 | **not measurable without the governed run**; the adopted Campaign-A records give s_G / s_H = **34.8 – 80.5** at the lower front, i.e. 20 – 107 on the measured tail s_H |
| \|Ĝ(a)\| | ≤ s_G ≈ 10 | adopted ratio \|Ĝ(a)\| / s_G = **0.680 – 0.681** on all 170 adopted objects |
| δ_mid(G_r) | ≈ 10⁻³ | adopted 2.8 · 10⁻³ – 7.9 · 10⁻³ |

## 3. Why route T2 is invalidated (load-bearing, and independent of any estimate)

`evidence/forecast_r2/TAIL_FORECAST_R2.json` scores every route with the **frozen K5-B** (`k5b_check.k5b_literal`,
pin `ddd54dc4…`) on the full adopted post-Campaign-A state, not with the direct-test predicate alone, and every route
gets the same premise supply (review r1 note N4).

| route | new real addresses | NOMINAL closes | CONSERVATIVE closes | class under the frozen gates |
|---|---|---|---|---|
| **T2 at the frozen audit's own stated inputs** (s_G = \|Ĝ(a)\| = 10, s_H = 5, s_D = 2, s_F = 1, δ_G = 10⁻³) | 5 | **3/5** (305–307) | **0/5** | **MARGINAL** |
| T2, same order-3 inputs, every supremum measured | 5 | **4/5** (305–308) | **1/5** | **MARGINAL** |
| T2 with the order-3 scale taken from the adopted Campaign-A records | 5 | 0/5 | 0/5 | INFEASIBLE |
| **TCT0** (theorem TC-T, Ĝ := 0) | **0** | 1/5 (305) | 1/5 (nothing is estimated) | MARGINAL |

The frozen route comparison claimed for T2 "NOMINAL … 5/5 closed with margin 1.6× (cell 309) to 6× (cell 305)" and
"CONSERVATIVE … 3/5", hence class USEFUL. Recomputed exactly, **at that comparison's own scenario inputs**, the
numbers are 3/5 and 0/5; giving the route the benefit of every measured supremum they are 4/5 and 1/5. USEFUL needs
NOMINAL = 5/5 or CONSERVATIVE ≥ 3/5, so **no reading reaches it**. The defect does not depend on which estimate of the
unmeasured order-3 scale one prefers, and under the frozen `selection_rule` ("below USEFUL is never executed") T2 must
not be launched.

The reason the audit's arithmetic was optimistic: it charged the order-3 candidate only through Env4 and a centre
motion ρ·\|Ĝ(a)\| ≤ ρ·10, i.e. ≤ 0.54, whereas the adopted evidence puts \|Ĝ(a)\| at 0.681·s_G with s_G ≈ 20–107 on
the measured tail, giving a centre motion of 0.6–4.2 on its own — before any radius.

**The refutation has exactly one hinge, and it should be named.** With the measured suprema, s_G = 10 and
δ_G = 10⁻³, the route closes 3/5 if \|Ĝ(a)\| = s_G, 4/5 if \|Ĝ(a)\| = 0.681·s_G, and **5/5 — i.e. USEFUL — only if
\|Ĝ(a)\| = 0 exactly** (review r2 note M8). "No reading reaches USEFUL" is therefore a claim about every reading in
which the order-3 candidate does not vanish exactly at the evaluation point, and it is justified twice over: by the
frozen comparison's own "abs_G_at_a ≤ sup of the G candidate", and by the adopted ratio 0.680–0.681 measured on all
170 Campaign-A objects.

**The exact threshold.** The tail closes under T2 if and only if the tail's certified order-3 candidate supremum
satisfies s_G ≤ ratio · s_H with (`critical_sup_G_over_sup_H_ratio`, exact bisection on the frozen test):

| cell | 305 | 306 | 307 | 308 | 309 |
|---|---|---|---|---|---|
| critical s_G / s_H | 64.72 | 47.99 | 32.03 | 19.20 | **10.55** |

The adopted lower-front value of that ratio is 34.8–80.5, so cell 309 needs the tail ratio to be 3.3–7.6× smaller than
anything the campaign has measured. That is possible — the tail's order-0→1 candidate growth `s_D/s_F` is 0.53–1.81
against the front's 16.9–144.4 — but it is **not evidence**, and the more nearly analogous order-1→2 growth
`s_H/s_D` is 1.11–4.46 against the front's 2.01–4.33, i.e. the two ranges *overlap*. The frozen NOMINAL scenario
("best available estimate") cannot be read as licensing the favourable end of that spread.

## 4. What is nevertheless established: cell 305 is closable with zero new real compute

Route **TCT0** (`theorem/THEOREM_TCT.md`: Lemma G atom constants, Ĝ := 0, σ₃/σ₄ from adopted Aux3 evidence) is a
**derivation, not a forecast** — every input is an adopted certified bound and nothing is estimated, so its NOMINAL
and CONSERVATIVE scenarios coincide. Frozen-K5-B result on the adopted post-Campaign-A state:

| cell | adopted M | mag 𝓗₅ (TCT0) | M after | M needed | Γ before | Γ after | margin | K5-B |
|---|---|---|---|---|---|---|---|---|
| 305 | 5.4983 | **4.257155** | 4.257155 | 4.8916 | +0.041841 | **−0.043752** | **1.149×** | **PASS** (via direct) |
| 306 | 5.4270 | 4.151682 | 4.151682 | 3.9051 | +0.117964 | +0.019116 | 0.941× | open |
| 307 | 5.3352 | 4.040057 | 4.040057 | 3.0761 | +0.199484 | +0.085118 | 0.761× | open |
| 308 | 5.2961 | 4.005124 | 4.005124 | 2.4324 | +0.288317 | +0.158343 | 0.607× | open |
| 309 | 5.2699 | 3.964274 | 3.964274 | 1.9698 | +0.374145 | +0.226117 | 0.497× | open |

No previously passing cell regresses (m = 1, 2, 3 stay complete on 0–309); no intersection is empty; `newly_passing`
= [305]. TCT0's class under the frozen gates is nevertheless **MARGINAL** (1/5), so the same `selection_rule` forbids
executing it under the *current* gate file. Closing cell 305 therefore needs a **new, separately frozen gate** owned by
the next successor — frozen, as always, before its own forecast is computed.

**Where the radius goes.** Per object at cell 309 the radii are 2.077, 3.157, 3.786, 4.498, 4.414. Decomposing
rad_r = A0·p2 + 2A1·p1 + A2·p0 into its eight terms (review r2 note M1):

| cell | r | rad | A0·ρ·f_G | A0·ρ²·Env4/2 | next largest |
|---|---|---|---|---|---|
| 309 | 3 | 4.4978 | **2.463 (55 %)** | 1.139 (25 %) | 2A1·ρ²·f_G/2 = 0.615 (14 %) |
| 309 | 4 | 4.4136 | 1.552 (35 %) | **2.049 (46 %)** | 2A1·ρ²·f_G/2 = 0.388 (9 %) |
| 305 | 3 | 4.5217 | **2.741 (61 %)** | 0.852 (19 %) | 0.685 (15 %) |
| 305 | 4 | 5.0786 | **2.535 (50 %)** | 1.546 (30 %) | 0.633 (12 %) |

The order-3 residual term A0·ρ·f_G is the largest single term everywhere except at r = 4 on cells 308 and 309, where
the (P3) remainder A0·ρ²·Env4/2 overtakes it (σ₄ reaches ≈ 235 at r = 4 through the J/h tower, for which no adopted
order-4 evidence exists). Summing every f_G-bearing term over r gives **78.7 / 77.1 / 75.0 / 73.2 / 71.6 %** of the
total radius on cells 305…309, and dropping f_G to its `eps_src[3]` floor would take the magnitude to 1.22–1.35, below
every M_needed — so an order-3 residual that cost nothing would close all five cells.

That is exactly why the ordering C1 before C2 rests on §3 and not on this decomposition: **a real Ĝ does not remove
f_G for free.** It pays ‖Ĝ‖ through Env4 and \|Ĝ(a)\| through the centre motion, which is precisely why
`T2_EVIDENCE` closes 0/5 and why the critical ratio at cell 309 is 10.55. C1 shrinks every one of the eight terms at
once; C2 trades the largest of them for two new ones.

## 5. Costed continuation plan

Ordered by expected value. Both options need a *new* feasibility gate frozen first, because the present one is
exhausted (its universe is the 5 open pairs and its classes have been applied).

### C1 — TCT0 + an operator-only certified registry extension to the tail (recommended, zero new real addresses)

`evidence/forecast_r2/ATOM_CONSTANT_REQUIREMENT.json`: with Ĝ := 0 the tail closes as soon as the atom constants fall
by

| cell | 305 | 306 | 307 | 308 | 309 |
|---|---|---|---|---|---|
| **A0 alone** (the pessimistic bracket) | 1.000× | **1.091×** | **1.502×** | **2.206×** | **3.294×** |
| A0, A1, A2 uniformly | 1.000× | 1.071× | 1.362× | 1.771× | 2.253× |

The A0-alone series leads because Lemma Dv′ does **not** scale the three constants uniformly: A0 = Ā_eff,
A1 = Ā_eff(κ₁C + δ₁) and A2 = Ā_eff(2κ₁²C² + κ₂C + 2κ₁Cδ₁ + 2δ₁² + δ₂), where C = sup‖Ĝ_e‖ is the taboo-resolvent
bound — a different constant from C_upper, and not necessarily smaller in the same proportion. The uniform series is a
modelling convenience; the true gain lies between the two columns.

**C1 is not route T1.** The frozen route comparison classified T1 — "theorem-AD tightening at the tail (the adopted
Perron rule, domain extended)" — INFEASIBLE, and that verdict stands: T1 feeds the registry constants the
**whole-cell** residuals δ_cell = δ_mid + ρ·Env (0.05–0.09 per object at the tail), which is exactly the term theorem
TC was invented to remove, and its radius is ≈ 45 per r however good the constants are. C1 feeds the same constants
into theorem TC-T's **Taylor** residuals p₀, p₁, p₂ (at cell 309, r = 0: 1.5·10⁻⁴, 0.0076, 0.28), where the radii are
2.077–4.498 per r. The mechanism T1 was refused for is not the mechanism C1 uses; no frozen verdict is being
re-litigated.

**What C1 can be expected to deliver, honestly.** Lemma Dv′ gives A0 = Ā_eff ≥ sup_B E_a[τ]. At e = 0 the adopted
registry bought **500.409** against `cells.json` cell 0's C_upper = 1232.836, a **2.46×** reduction — enough, as a
historical precedent, to clear cells 306, 307 and 308 (1.091×, 1.502×, 2.206× on A0 alone) but not cell 309's 3.294×.
At tail drift e ≈ 1.6–2.1 with the frozen CUSUM
(h, k) = (5, ½) the mean increment is e − k ≈ 1.1–1.6, so a renewal estimate puts E_a[τ] at order h/(e − k) ≈ 3.1–4.5
against C_upper = 5.78–7.73 — a ratio near **1.7**, which clears cells 306 and 307 and is **short of the 2.21× and
3.29× that 308 and 309 need on A0 alone**. The renewal heuristic and the e = 0 precedent therefore disagree about
cell 308 (1.7× against 2.46×) and agree that cell 309 is the hard one. Gains in A1 and A2 (through C = sup‖Ĝ_e‖ and the D-derivative bounds) would
have to make up the rest. **Expected outcome: 3/5 (cells 305–307) securely; 4–5/5 only if the taboo constants are also
favourable.** That is an estimate from a renewal heuristic, not a certificate, and the next campaign must freeze its
gate before refining it.
Cost: **0 new-real CPU-h**, ≈ 2–4 CPU-h of operator certification and replay, ≈ 6–8 h of governed lifecycle. The
required certificates are the six operator-only ones of theorem AD §8 (Ā, τ, C, D_lo, D1, D2 per e-block), which that
theorem states explicitly are free of any source, candidate of F or value of R — so **no new real address and no guard
transition**. The frozen build/falsify/cross-check code of `p5y_k5_perron_deflated_resolvent` applies unchanged; the
new work is 5 tail e-blocks instead of 149, plus its own qualification and adjudication.

### C2 — the real order-3 candidate at the tail (route T2), *after* C1

Only worth launching once C1 has fixed the atom constants, because C1 shrinks the whole radius multiplicatively while
T2 removes only the ρ·f_G part of it (§4). Cost unchanged: 5 new real addresses, ≈ 2.2 CPU-h new-real + ≈ 0.9 CPU-h
pre-registered reproduction, guard ALLOW required. On its own its critical threshold (§3) makes it a coin flip on an
unmeasured quantity. C2 must also discharge Campaign A's note N1 obligation and re-open notes N3 and N5 — see
`CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md`.

### C3 — measure the tail order-3 scale under a pre-registered single-cell probe

If the next campaign wants the T2 question settled on evidence rather than deferred: pre-register **one** cell
(309, the binding one), evaluate it, and publish s_G, |Ĝ(a)| and δ_mid(G_r) as the measurement that fixes the
estimate for all five. Cost ≈ 0.44 CPU-h new-real, 1 new real address, full governed lifecycle. This buys knowledge,
not coverage, and should be folded into C1's lifecycle rather than run alone.

### Not recommended

- Route T3 (11 sub-cell point addresses, a new theorem and a new executor) — strictly more expensive than C1 and
  reopens the executor governance surface (`p5y_k5_cusum_real_point_executor` X1/N1–N3/D1–D4).
- Route T4 (re-cover the tail with narrower K1 cells) — still INFEASIBLE on governance: the frozen K5-B binds the
  cover by `cells.json` `341eb5e9…`, and changing it invalidates the adopted map's cell indexing.
- Tightening f_G alone: setting σ₃ ≡ 0 outright — a gift larger than any legitimate refinement — still closes only
  3/5 (review r1 item 51). No refinement of the order-3 residual can close the tail.

## 6. Compute accounting

| item | CPU-h | kind |
|---|---|---|
| Campaign A (adopted) | 14.203 | new real |
| Campaign B replay measurement of cells 305–309 | ≈ 1.87 | replay of adopted values, identity-gated; **not** new real |
| Campaign B forecast / K5-B scoring | < 0.1 | arithmetic |
| **Campaign B new real** | **0.000** | — |

Remaining nominal headroom against the 40 CPU-h campaign hard cap: **25.797 CPU-h**, unchanged. The 8 CPU-h Campaign-B
hard cap was never approached and no launch decision was taken against it.

## 7. Invariants held

- `main` untouched at `1cb45382`; AWS SR/PS1 not contacted at any point (CUSUM/K5 only, Vultr worker only).
- Campaign A's namespace `p5y_k5_lower_front_order3` byte-unchanged since its freeze outside its own evidence prefix
  (64 files changed, all under `evidence/tc_r1/`, 0 deletions); every adopted predecessor namespace byte-unchanged
  since Campaign A's start frontier `7cb01e38` (`evidence/b0_r1/B0_STATE_VERIFICATION.json` G5, re-derived
  independently in `review/REVIEW_R1.md` items 42–43).
- Coverage map r4 (`a3bddd83…`) untouched; **no coverage map r5 exists**, and none may until an adopted successor
  closes at least one tail cell after a *completed* independent adjudication handover.
- The frozen Campaign-B feasibility gates (`config/FEASIBILITY_GATES_B.json`, sha256 `392101dd…`, frozen at
  `7ee92476`) were not modified, and neither were `phase_a/` or `phase_b/`.
