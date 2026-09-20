# Campaign B, Phase C — execution decision: STOP under the frozen stop rule, with a costed continuation plan

Start frontier `3c1c6b9c` (`p5y-postk1-frontier`), `main` untouched at `1cb45382`, AWS SR/PS1 untouched.
Guard **DENY** throughout; **no new real scientific value was computed** in this phase and no new real address exists.

## 1. Verdict

    TAIL_TARGET              = CUSUM m = 5, cells 305, 306, 307, 308, 309
    TAIL_SELECTED_ROUTE      = T2 (theorem TC at the 5 tail cells)  -- INVALIDATED, see section 3
    TAIL_FEASIBILITY_GATE    = MARGINAL at the frozen audit's own inputs; INFEASIBLE at evidence-based inputs
    CAMPAIGN_B_EXECUTION     = STOPPED before freeze, by config/FEASIBILITY_GATES_B.json `stop_rule`
    NEW_REAL_ADDRESSES       = 0        NEW_REAL_CPU_HOURS = 0
    K5                       = PARTIAL  (m = 5 open on [305, 309]; coverage map r4 unchanged, no r5)

The frozen gate file, written before any Campaign-B forecast, says:

> `selection_rule`: "highest class; among equal classes prefer zero new real addresses, then fewer new-real
> CPU-hours; **below USEFUL is never executed**"
> `stop_rule`: "if every route is MARGINAL or INFEASIBLE, **stop Campaign B execution and write a costed
> continuation plan**"

Every route now scores below USEFUL. The stop rule fires. The gate was not amended, reinterpreted or re-scored after
the numbers were seen; it was applied mechanically by `code/tail_forecast_r2.py::classify`.

## 2. What was measured (Phase B0/B1, read-only and replay-only)

`evidence/measurement_r1/` — an identity-gated **replay** of the theorem-TC input fields of cells 305–309 that the
adopted K1 record does not store (`cert.norms.k/j`, `sup_S0`, `sup.{F,D,H}`, `Ĥ_r(a)`, the whole-cell W enclosures),
plus the adopted midpoint residuals and source errors. ≈ 6 740 CPU-s ≈ **1.87 CPU-h of replay** (not new-real: no
order-3 candidate of F is proposed, and `order3_fields_present = false` on every record). Gates:

| gate | result |
|---|---|
| frozen producer identity gate (262 fields vs the sealed K1 record, per cell) | identical, 5/5 |
| derived identity gate (rebuild the record's `R2_interval` for every m from Ĥ_r(a), W and the record's own `eps_cell_refined`) | contained, worst relative endpoint gap 3.6·10⁻⁸ (tolerance 10⁻⁶), 20/20 |
| adopted-state replay gate (no tail route) reproduces the sealed Campaign-A consumption `1fa8d8de…` pass ranges | PASS, all four m |
| two independent theorem-TCT rule paths agree as exact rationals | 20/20 |

The measurement overturns the two candidate-supremum assumptions the frozen route comparison made:

| quantity | frozen route comparison (assumed) | measured / adopted evidence |
|---|---|---|
| s_H (order-2 candidate sup) | ≈ 5 | **0.57 – 1.33** (measured, 25 objects) |
| s_D, s_F | not stated (≈ 2, ≈ 1 implied) | 0.30 – 0.70, 0.26 – 1.08 (measured) |
| s_G (order-3 candidate sup) | ≈ 10 | **not measurable without the governed run**; the adopted Campaign-A records give s_G / s_H = **34.8 – 80.5** at the lower front, i.e. 20 – 110 on the measured tail s_H |
| \|Ĝ(a)\| | ≤ s_G ≈ 10 | adopted ratio \|Ĝ(a)\| / s_G = **0.680 – 0.681** on all 170 adopted objects |
| δ_mid(G_r) | ≈ 10⁻³ | adopted 2.8 · 10⁻³ – 7.9 · 10⁻³ |

## 3. Why route T2 is invalidated (load-bearing, and independent of any estimate)

`evidence/forecast_r2/TAIL_FORECAST_R2.json` scores every route with the **frozen K5-B** (`k5b_check.k5b_literal`,
pin `ddd54dc4…`) on the full adopted post-Campaign-A state, not with the direct-test predicate alone.

| route | new real addresses | NOMINAL closes | CONSERVATIVE closes | class under the frozen gates |
|---|---|---|---|---|
| **T2 at the frozen audit's own stated inputs** (s_G = 10, s_H = 5, δ_G = 10⁻³) | 5 | **3/5** (305–307) | **1/5** | **MARGINAL** |
| T2, same order-3 inputs, measured adopted suprema | 5 | 3/5 (305–307) | 1/5 | MARGINAL |
| T2 with the order-3 scale taken from the adopted Campaign-A records | 5 | 0/5 | 0/5 | INFEASIBLE |
| **TCT0** (theorem TC-T, Ĝ := 0) | **0** | 1/5 (305) | 1/5 (nothing is estimated) | MARGINAL |

The frozen route comparison claimed for T2 "NOMINAL … 5/5 closed with margin 1.6× (cell 309) to 6× (cell 305)" and
"CONSERVATIVE … 3/5", hence class USEFUL. Recomputed exactly, **at that comparison's own scenario inputs**, the
numbers are 3/5 and 1/5, hence class **MARGINAL**. Both of the two claims that made T2 USEFUL are arithmetically
wrong, so the defect does not depend on which estimate of the unmeasured order-3 scale one prefers. Under the frozen
`selection_rule` ("below USEFUL is never executed") T2 must not be launched.

The reason the audit's arithmetic was optimistic: it charged the order-3 candidate only through Env4 and a centre
motion ρ·\|Ĝ(a)\| ≤ ρ·10, i.e. ≤ 0.54, whereas the adopted evidence puts \|Ĝ(a)\| at 0.681·s_G with s_G ≈ 20–110 on
the measured tail, giving a centre motion of 0.6–4.3 on its own — before any radius.

**The exact threshold.** The tail closes under T2 if and only if the tail's certified order-3 candidate supremum
satisfies s_G ≤ ratio · s_H with (`critical_sup_G_over_sup_H_ratio`, exact bisection on the frozen test):

| cell | 305 | 306 | 307 | 308 | 309 |
|---|---|---|---|---|---|
| critical s_G / s_H | 60.18 | 43.23 | 27.13 | 14.24 | **5.47** |

The adopted lower-front value of that ratio is 34.8–80.5. Cell 309 therefore needs the tail ratio to be ~10× smaller
than anything the campaign has ever observed. That is possible — the tail's own measured per-order growth is
s_H/s_D ≈ 1.1 and s_D/s_F ≈ 0.6, nothing like the front's 2–4 and ≈ 20 — but it is **not evidence**, and the frozen
NOMINAL scenario ("best available estimate") cannot be read as licensing the favourable end of a 15-fold range.

## 4. What is nevertheless established: cell 305 is closable with zero new real compute

Route **TCT0** (`theorem/THEOREM_TCT.md`: Lemma G atom constants, Ĝ := 0, σ3/σ4 from adopted Aux3 evidence) is a
**derivation, not a forecast** — every input is an adopted certified bound and nothing is estimated, so its NOMINAL
and CONSERVATIVE scenarios coincide. Frozen-K5-B result on the adopted post-Campaign-A state:

| cell | adopted M | mag 𝓗₅ (TCT0) | M after | M needed | Γ before | Γ after | K5-B |
|---|---|---|---|---|---|---|---|
| 305 | 5.4983 | **4.2031** | 4.2031 | 4.8916 | +0.041841 | **−0.047477** | **PASS** (via direct) |
| 306 | 5.4270 | 4.0906 | 4.0906 | 3.9051 | +0.117964 | +0.014379 | open |
| 307 | 5.3352 | 3.9692 | 3.9692 | 3.0761 | +0.199484 | +0.078863 | open |
| 308 | 5.2961 | 3.9232 | 3.9232 | 2.4324 | +0.288317 | +0.150091 | open |
| 309 | 5.2699 | 3.8719 | 3.8719 | 1.9698 | +0.374145 | +0.215646 | open |

No previously passing cell regresses (m = 1, 2, 3 stay complete on 0–309); no intersection is empty; `newly_passing`
= [305]. TCT0's class under the frozen gates is nevertheless **MARGINAL** (1/5), so the same
`selection_rule` forbids executing it under the *current* gate file. Closing cell 305 therefore needs a **new,
separately frozen gate** owned by the next successor — frozen, as always, before its own forecast is computed.

## 5. Costed continuation plan

Ordered by expected value. Both options need a *new* feasibility gate frozen first, because the present one is
exhausted (its universe is the 5 open pairs and its classes have been applied).

### C1 — TCT0 + an operator-only certified registry extension to the tail (recommended, zero new real addresses)

`evidence/forecast_r2/ATOM_CONSTANT_REQUIREMENT.json`: with Ĝ := 0 the tail closes as soon as the atom constants fall,
uniformly, by

| cell | 305 | 306 | 307 | 308 | 309 |
|---|---|---|---|---|---|
| uniform A0/A1/A2 reduction needed | 1.00× (already closes) | **1.053×** | **1.335×** | **1.731×** | **2.195×** |
| A0-alone reduction needed | 1.00× | 1.068× | 1.462× | 2.132× | 3.153× |

**C1 is not route T1.** The frozen route comparison classified T1 — "theorem-AD tightening at the tail (the adopted
Perron rule, domain extended)" — INFEASIBLE, and that verdict stands: T1 feeds the registry constants the **whole-cell**
residuals δ_cell = δ_mid + ρ·Env (0.05–0.09 per object at the tail), which is exactly the term theorem TC was invented
to remove, and its radius is ≈ 45 per r however good the constants are. C1 feeds the same constants into theorem
TC-T's **Taylor** residuals p0, p1, p2 (0.28, 0.008, 0.0002 at cell 309), where the radius is 2.08–4.07 per r and a
2.2× constant reduction is decisive. The mechanism T1 was refused for is not the mechanism C1 uses; no frozen verdict
is being re-litigated.

Lemma G's A0 is the non-sharp one-sided block bound C_upper = 5.78–7.73. Theorem AD's Lemma Dv′ replaces it with
Ā_eff = min(Ā, τ/D_lo) ≥ sup E_a[τ], which at e = 0 was 469.8 against C_upper = 1233 — a **2.6× reduction** — and at
drift e ≈ 1.6–2.1 the mean time to alarm is far smaller relative to the block bound than at e = 0, so a 1.05×–2.20×
reduction is the *easy* end of that mechanism. The required certificates are the six operator-only ones of theorem AD
§8 (Ā, τ, C, D_lo, D1, D2 per e-block) — no source, no candidate of F, no value of R, hence **no new real scientific
address and no guard transition**. The frozen build/falsify/cross-check code of `p5y_k5_perron_deflated_resolvent`
(`build_registry.py`, `taboo_certify.py`, `falsify_registry.py`, `xcheck_registry.py`) applies unchanged; the new work
is 5 tail e-blocks instead of 149, plus its own qualification and adjudication.
Estimated cost: **0 new-real CPU-h**, ≈ 2–4 CPU-h of operator certification and replay, ≈ 6–8 h of governed
lifecycle. Expected outcome: 5/5, with 306–308 comfortable and 309 the binding cell.
Risk: if the tail Ā_eff turns out not to beat C_upper by 2.2×, cells 308–309 stay open and C1 degrades to 3/5 — still
USEFUL under any sane gate.

### C2 — the real order-3 candidate at the tail (route T2), *after* C1

Only worth launching once C1 has fixed the atom constants, because C1 shrinks the radius multiplicatively while T2
removes the ρ·f_G term; together they close the tail with a wide margin under either order-3 outcome. Cost unchanged:
5 new real addresses, ≈ 2.2 CPU-h new-real + ≈ 0.9 CPU-h pre-registered reproduction, guard ALLOW required.
If C1 is not done first, T2's own critical threshold (section 3) makes it a coin flip on an unmeasured quantity.

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

## 6. Compute accounting

| item | CPU-h | kind |
|---|---|---|
| Campaign A (adopted) | 14.203 | new real |
| Campaign B replay measurement of cells 305–309 | ≈ 1.87 | replay of adopted values, identity-gated; **not** new real |
| Campaign B forecast / K5-B scoring | < 0.05 | arithmetic |
| **Campaign B new real** | **0.000** | — |

Remaining nominal headroom against the 40 CPU-h campaign hard cap: **25.797 CPU-h**, unchanged. The 8 CPU-h Campaign-B
hard cap was never approached and no launch decision was taken against it.

## 7. Invariants held

- `main` untouched at `1cb45382`; AWS SR/PS1 not contacted at any point (CUSUM/K5 only, Vultr worker only).
- Campaign A's namespace `p5y_k5_lower_front_order3` byte-unchanged since its freeze outside its own evidence prefix;
  every adopted predecessor namespace byte-unchanged since Campaign A's start frontier `7cb01e38`
  (`evidence/b0_r1/B0_STATE_VERIFICATION.json` G5).
- Coverage map r4 (`a3bddd83…`) untouched; **no coverage map r5 exists**, and none may until an adopted successor
  closes at least one tail cell after a *completed* independent adjudication handover.
- The frozen Campaign-B feasibility gates (`config/FEASIBILITY_GATES_B.json`, sha256 `392101dd…`, frozen at `7ee92476`) were not modified.
