# Phase B — closure routes for the remaining CUSUM K5 cells, and the selected strategy

Written before any new scientific result. Nothing in this document was computed from a new value of R or of a
derivative of R. Every number comes from frozen artifacts, sealed records, or certified operator constants.

**Indexing.** K1 cell k (0-based, `cells.json`) is theorem cell C_{k+1}. Its right end is x_hi(k); x1 = x_hi(0) = 5083/10⁷.

## 1. Cell-0 transport audit (existing evidence as is)

The adopted slot-1 record certifies, for each m, two things:
- `R'''_m(0) ∈ [L0, U0]`;
- `M5_m ≥ sup_{[0, x1]} |R_m^(5)|`.

**Certification domain of M5.** M5 comes from `local_r5.local_tower` with `eta = x1`, the hull norms `norm_table(0, x1)`
and `sup_S0_on(n, 0, x1)`, `C = C_upper(cell 0)`, and the local-anchoring lemma with drift distance x1. Its domain is
exactly the hull [0, x1], i.e. K1 cell 0. No other certified R⁽⁵⁾, R⁽⁴⁾ or signed R''' object exists for CUSUM:
- the Aux3/4/5 order-3 objects are unsigned magnitudes (readiness audit §5);
- the GammaTilde point certificate is order ≤ 1 at e = 0.

| m | L0 | M5 on [0, x1] | MAX_CERTIFIED_E (existing) | LAST_K1_CELL_CERTIFIED | FRONT CELLS DISCHARGED |
|---|---:|---:|---|---|---:|
| 1 | 1801.43 | 1.0614e8 | x1 = 5.083e-4 | 0 | 0 |
| 2 | 1461.59 | 9.1648e7 | x1 | 0 | 0 |
| 3 | 1307.11 | 8.3673e7 | x1 | 0 | 0 |
| 5 | 1073.99 | 7.3404e7 | x1 | 0 | 0 |

`R'''(e) ≥ L0 − (e²/2)·M5` is certified only for e ≤ x1. Reusing it on cell 1 would use M5 outside its certified
domain, which is forbidden.

**A valid wider-domain bound can be constructed deterministically (strategy T-EXT, §6).**
- Every rule of the R3/R4 tower and of the local-anchoring lemma is stated for a hull [0, η] with hull norms on
  [0, η]. x1 enters only as the hull radius.
- The anchors are e = 0 objects: the candidate graded suprema and the graded point errors. The sealed record carries
  both as the exact radius-zero dyadics of the slot-1 run. Every tower rule is a valid inequality for valid inputs
  (review F4), and the dev replay reproduces M5 and the trace exactly.
- So M5_m(η) ≥ sup_{[0,η]} |R^(5)| can be recomputed for any η from sealed data, closed-form Gaussian/Hermite norms
  and certified constants, with no model solve.
- M5(η) is nondecreasing in η (every input grows).

**Ceiling of the whole transport family** (analytic, from M5(η) ≥ M5(x1)):
- Pointwise positivity L_k > 0 needs x_hi(k)² < 2·L0/M5(x1). That means cells ≤ 10 for m = 1, ≤ 9 for m = 5.
- The K5-B chain integrates R''' twice, so it can carry up to roughly x² < 10·L0/M5, i.e. about cell 23 (m = 1) or
  cell 21 (m = 5).
- These are upper bounds on the reach. The actual reach depends on how fast M5(η) grows, which is not known before
  the frozen evaluation.

## 2. Global theorem shortcut — none

Every candidate was checked against the frozen record of what is proved:

| ingredient | what it gives | why it cannot discharge a region |
|---|---|---|
| slot-1 local positivity | R'''(0) > 0; R''' > 0 on [0, x1] | local; no global sign may be inferred from a local sign |
| GammaTilde > 1 (`84aaa6a5`) | s(0+) = Γ̃ − 1 > 0 | a boundary value, no monotonicity content |
| K2 (κ ≥ κ*/m²), K3 (M₂ < ∞), K4 assembly | variance floor, finiteness, assembly | no sign information on g = R − eR' |
| real-analyticity (L5, `879792d0`) | R ∈ C^∞, holomorphic strip | qualitative only: strip width θ ≈ 1e-5..1e-6; no Cauchy bound usable on 0.1-scale intervals |
| parity | R odd ⇒ g odd, R''' even, R''''(0) = 0 | already used (transport); gives nothing at e ≠ 0 |
| K5-B identities | g' = −eR'', s' = g/e² | the theorem itself; needs R'' lower bounds |
| K1 whole-cell records | R2 enclosures | H.lo ≤ 0 on all 310 cells (Z2 never fires); no convexity certificate anywhere |
| endpoint facts | R(2) > −2 ⇒ s(2) < 1 | an endpoint value, not a derivative sign |

A convexity shortcut (R'' ≥ 0 ⇒ g decreasing ⇒ g < 0) would need a certified R'' ≥ 0, which no artifact provides.
**GLOBAL_SHORTCUT = NONE.**

## 3. Block certification

- **Order 2 (direct bound on a block B ⊇ several cells).** Γ_B uses the block midpoint and a block-wide R''
  magnitude, which is at least the largest cell magnitude, over a radius at least the cell radius. It is never
  sharper than the per-cell tests. Rejected.
- **Order 3 anchored at 0 (the block [0, x_k]).** This is T-EXT (§6): one deterministic block per prefix, zero new
  addresses.
- **Order 3 anchored at a ≠ 0 (UNFORECAST; corrected after review F8).** A new point run for R'''(a) is needed, and
  the CusumPointBackend refuses eta_mid ≠ 0 (Q03), so this means new executor code. The graded rules also stop
  existing at a > 0.0228 (§3 of the Phase A audit).
  - The 4.7e10 R3 majorant came from whole-cell errors inside the anchors, not from anchoring away from 0. It does
    not decide the question.
  - A hybrid is possible: keep T-EXT's tower anchored at 0, which is valid on [0, η] ∋ a, and transport a new point
    bound L_a to first order, `R'''(e) ≥ L_a − |e−a|·M4(η)`. That is multi-cell iff M4(η) ≲ L_a / cell width.
  - Its reach is **unknown** until T-EXT seals M4(η). The anchor counts in §4 and §7 are rough estimates, not bounds.

## 4. Sparse anchors

- **Graded zone (cells after the transport reach, up to 40).** Unforecast (see §3); roughly one anchor per cell if
  the hybrid radius stays below a cell width. Each anchor needs a new, unqualified executor mode. The point radius is also amplified by the graded determinant, which falls to
  0.05 at cell 40. Rough cost: 20–35 anchors × 0.84 CPU-h (the slot-1 cost) ≈ 17–30 CPU-h, plus a new executor
  and qualification. Informativeness at a ≠ 0 is unforecast and doubtful.
- **Scalar zone (cells 41–K_m).** No certified method of the existing architecture is informative here:
  - Order-3 scalar enclosures have radius ≥ C·3k₁·ε_H,mid ≈ 1e7 (R1 finding), against R''' ≈ 2e3.
  - Order-≤ 2 point evaluations through the K1 midpoint path have the K1 width, which already contains 0 on
    64–83 cells per m (MIDPOINT_G_INDETERMINATE). Adding points cannot fix a point enclosure that contains 0.
  - The 25–28 CURVATURE_SLACK cells per m could be closed by sub-cell points with the parent M_R2. That costs
    about 170–240 point runs per m (≈ 250 union points ≈ 83 CPU-h) and leaves 104–123 cells per m open. Rejected:
    it cannot change K5's status.

**ANCHOR_COUNT / REAL_ADDRESSES for the front: not finite with the existing architecture.** The scalar zone needs a
new certified method (§8). The graded-zone count is unforecast until T-EXT seals M4(η).

## 5. m = 5 tail (cells 305–309)

- **Why 149–304 pass and 305–309 do not.** In the tail, |g| decreases (−0.34 → −0.23) while the curvature penalty
  ρ·x·M_R2 grows with the cell width (ρ = 0.041 → 0.054) and with x. The two cross between cells 304 and 305.
  The midpoint enclosures are tight (width about 0.008). m = 1, 2, 3 have larger |g| there and pass.
- **Cheaper tail route (theorem K5-B-T, a successor to K5-B, not a modification):**
  1. For a cell C_k = [a, b], a partition a = y₀ < … < y_s = min(b, 2) with midpoints p_j and radii r_j is used.
  2. By the MVT for g, `hi(R(p_j) − p_j R'(p_j)) + r_j·y_j·M_R2(k) < 0` for every j gives g < 0 on [a, min(b, 2)].
     M_R2(k) bounds |R''| on all of C_k, so it is valid on every sub-cell.
  3. Restricting to (0, 2] is exactly the H3a domain, and it removes the need to pass cell 309 beyond e = 2.
  4. Each K5-B pass certifies g < 0 on its own cell unconditionally, so passes and K5-B-T sub-cells can be mixed.
     H3a then follows from g < 0 on (0, 2], the analytic continuity and s(0+) facts, and s(2) < 1.
     s(2) < 1 needs the cell-309 target gate, which the closure does not enforce and which the consumer must check
     (PB6).
- **Forecast** (0.8 margin on the K1 midpoint values): equal splits s = 2, 2, 3, 3 on 305–308, plus one point on
  [x_hi(308), 2]. That is 11 new point addresses (order ≤ 1, all m per run) at about 1,180 CPU-s each (GammaTilde
  point runs), about 3.6 CPU-h, about 1 wall-h on 4 workers.
- **Executor:** `p5y_gammatilde_point_certificate/code/point_eval.py`, the frozen K1 midpoint path on a degenerate
  cell {a} with C_upper of the containing cell.
  - Classification: REQUIRES_NEW_CODE_AND_QUALIFICATION (review F12). `point_core.point_cell` is bound to cell 0, so
    a containing-cell binding is new code. The qualification is an exact replay of a K1 tail midpoint, the same
    pattern as its Q2.
- **The tail alone cannot close K5.** Every m = 1–5 front stays open. Tail compute is therefore deferred: preparing
  or authorizing it now would spend addresses that cannot change K5's status. The design goes on record here, and
  its execution packet waits until the front has a qualified route.

## 6. Strategy T-EXT (wider-hull evenness transport from sealed slot-1 data)

**Theorem T-EXT.** Fix m ∈ {1, 2, 3, 5} and η > 0 with [0, η] ⊆ K5 domain.

Premises:
- **(P1)** R = R_m is odd and C⁵ on [0, η]: P5-T3, and P5X L5 real-analyticity (independently reviewed `879792d0`).
- **(P2)** R'''(0) ≥ L0_m (sealed, adopted slot-1).
- **(P3)** M5_m(η) is the frozen `local_r5.local_tower` output (12 iterations, parity on) with:
  - anchors = the sealed candidate graded suprema and graded point errors at e = 0;
  - `x1 := η`;
  - base = { C = max C_upper over the K1 cells meeting [0, η]; C_e0, C_o0 from registry `a645a157`;
    k, j = `norm_table(0, η)`; S0 = `sup_S0_on(n, 0, η)`; eta = η }.

Conclusion: for every K1 cell C ⊆ [0, η], `inf_C R''' ≥ L0_m − (x_hi(C)²/2)·M5_m(η)`.

*Proof.*
- R''' is even and R⁽⁴⁾(0) = 0, so `R'''(e) = R'''(0) + ∫₀^e (e−t) R⁽⁵⁾(t) dt ≥ R'''(0) − (e²/2) sup_{[0,e]}|R⁽⁵⁾|`.
- M5_m(η) bounds that sup by the R4 local-anchoring lemma and the R3 graded tower. Each rule is a bound over the hull
  whose inputs are sups over the same hull. The resolvent rule needs |e| ≤ η and a certified C on the hull, which
  C_upper supplies cell by cell: it is a proved bound on ‖(I−K_e)⁻¹‖ for every e in the cell.
- The export at the σ-fixed x0 keeps only the even part.
- The sealed anchors are upper bounds of the certified e = 0 quantities, and every tower operation is monotone in its
  nonnegative inputs. ∎

**Consumption rule (frozen before evaluation).**
- For each m and each K1 cell k = 1, …, 40 (the whole graded zone, fixed by certified constants before any result),
  set `L_k := L0_m − (x_hi(k)²/2)·M5_m(x_hi(k))`, using the smallest prefix hull containing the cell.
- Cell 0 keeps the adopted sealed L1. Cells ≥ 41 keep L_k = None.
- The result is fed to the frozen `k5b_literal` through the E6 loading path. That needs an additive successor
  consumer, because the accepted E6 adapter admits L₁ only.
- All 40 hulls are always evaluated. There is no adaptive or post-result choice, and each L_k is an independent valid
  bound.

**Governance classification (corrected after review §2.10).**
- T-EXT is a deterministic re-derivation from sealed, adopted evidence and certified constants. It has no real-input
  arithmetic in the TRUST_MODEL sense, no model solve and no new real scientific address. So it needs no external
  countersigned authorization.
- It does produce new certified values, so it has its own boundary:
  - a freeze commit;
  - a code-level refusal to evaluate before the freeze;
  - an evaluation ledger;
  - a sign-blind qualification with a VOID / no-rerun rule;
  - a sealed result hash before consumption;
  - independent adjudication.

**Pre-freeze adoptions from the review:**
- the piecewise transport over the nested hulls (F2), which dominates the rule above;
- sealed M2–M4 exports and a second, M2-tightened consumption (F3);
- widened-regime fixtures, including a small-determinant family (F1).

See `../transport_extension/TEXT_SPEC.md`.

## 7. Strategy comparison

| strategy | new real probes | new real addresses | CPU-h | wall-h | new governance campaigns | engineering | scientific risk | governance risk | cells it can close |
|---|---:|---:|---:|---:|---:|---|---|---|---|
| A existing evidence as is | 0 | 0 | 0 | 0 | 0 | none | none | none | 0 |
| B global shortcut | 0 | 0 | 0 | 0 | 0 | — | — | — | none exists |
| C1 T-EXT block [0, x_k] | 0 | 0 | < 0.1 | < 0.5 | 1 (deterministic successor) | small (wrapper around frozen code) | low (replay-anchored) | low | ≤ about 9–23 per m, front start only |
| C2 hybrid blocks at e ≠ 0 | unforecast | unforecast | ≈ 0.84 per anchor | — | 2 (executor + authorization) | new executor mode | high (unforecast) | medium | ≤ cells up to 40 |
| D1 sparse anchors, graded zone | ≈ 20–35 (estimate) | ≈ 20–35 | 17–30 | 5–8 | 2 | new executor mode | high | medium | ≤ cells up to 40 |
| D2 sub-cell points, slack band | ≈ 250 | ≈ 250 | ≈ 83 | ≈ 21 | 2 | reuse point path | low | medium | 25–28 per m (upper front) |
| D3 tail sub-cell points | 11 | 11 | ≈ 3.6 | ≈ 1 | 1 (+ authorization) | reuse point path | low | medium | m = 5 tail 305–309 |
| front scalar zone, any route | — | — | — | — | — | new certified method | — | — | infeasible now |
| **E mixed = C1 now + D3 designed + front blocker** | 0 tonight | 0 tonight | < 0.1 | < 1 | 1 | small | low | low | C1's cells now; tail on authorization |

**Selection** (lexicographic: rigor, then new addresses, then governance, then wall, then CPU) = **E (mixed)**.
- Run C1 (T-EXT) tonight.
- Design D3 (tail) but do not authorize or run it, because K5 cannot close while the front is blocked.
- Report the front scalar-zone blocker as the scientific blocker.

## 8. The front blocker, stated precisely

`FB-S` (scalar zone, K1 cells 41 to 132 / 144 / 145 / 148): no certified method of the qualified architecture
resolves the sign of g there.

- The K1 point enclosure of g(e0) contains 0 on 64–83 cells per m. Its width is dominated by the resolvent cross
  term: the D half-width is about C²·k₁·res₀ (98% of it at cell 0). In the scalar zone, C_upper is 514–1026
  (review F9).
- The graded parity method does not exist beyond e = 0.0228.

A resolution needs at least one new certified capability:
- **(i)** a Perron-deflated resolvent certificate. The even-block constant C_e0 ≈ 470 is essentially the Perron mode:
  eigenvalue 0.99782, and the float deflated norm is about 0.26 per the R2 diagnostics.
- **(ii)** a producer whose enclosure widths are a few × (upper front) to 18–51× (cells 40–41, the graded boundary)
  smaller; about 10³× would be needed near cell 10.
- **(iii)** an order-3 producer at e ≠ 0 that does not rely on exact parity.

Each of these is a research-grade successor with its own theorem, certificate and qualification. None can be
honestly scheduled as an overnight real run.

`FB-G` (graded zone, cells between the T-EXT reach and 40): needs (iii), or order-3 anchors at 0 < a ≤ 0.0228 with a
new executor mode.

## 9. Reuse audit

| component | T-EXT | tail (D3) | front |
|---|---|---|---|
| R5 executor (supervisor, lifecycle, ledger, authorization interface) | NOT_APPLICABLE (no real address) | REQUIRES_NEW_QUALIFICATION if used with the point backend | NOT_APPLICABLE |
| R5 backend `CusumPointBackend` | NOT_APPLICABLE (not re-run) | NOT_APPLICABLE (e = 0 only; refuses eta_mid ≠ 0) | NOT_APPLICABLE |
| certificate stack (C_e0, C_o0 registry `a645a157`) | REUSABLE_AS_IS | NOT_APPLICABLE | — |
| R5 majorants (`local_r5`, `r5_majorant`, `graded_dag`, `hermite6_ext`) | REUSABLE_WITH_ADDITIVE_BINDING (hull parameter η) | NOT_APPLICABLE | NOT_APPLICABLE beyond cell 40 |
| K1 loader (`k5_minimality`) | REUSABLE_AS_IS | REUSABLE_AS_IS | — |
| K5-B literal checker (`k5b_literal`) | REUSABLE_AS_IS (per-cell L already supported) | REUSABLE_AS_IS | — |
| E6 adapter | read path REUSABLE_AS_IS; L₁-only channel insufficient, so an additive successor consumer | successor consumer | — |
| GammaTilde point path (`point_eval`) | NOT_APPLICABLE | REQUIRES_NEW_CODE_AND_QUALIFICATION (cell-0 binding) | NOT_APPLICABLE (K1 width) |

No R6 executor is created. T-EXT changes no executor code.
