# Disposition of the three non-blocking notes the Campaign-A adjudicator left open (N1 / C7, N3, N5)

Written before any Campaign-B freeze, as required. Source: `p5y_k5_lower_front_order3/evidence/tc_r1/adjudication_r1/`
(`ADJUDICATION_R1.md` notes N1, N3, N5 and `SEQUENCING_DEFECT_NOTE.md`). The historical order-3 registry and every
adopted namespace are **not** edited by this successor; any cross-reference is owned here.

## N1 / C7 — the order-3 producer's registry says no real CUSUM cell may be evaluated by it

**Status for Campaign B as executed: NOT LOAD-BEARING. No bridge is needed, and none is issued.**

The adjudicator's note concerns `p5y_k5_cusum_order3_real_producer/config/REAL_CELL_AUTHORIZATION_REGISTRY.json`
(`FROZEN_EMPTY`, "No entry exists: no real CUSUM cell may be evaluated by this producer") versus Campaign A's
execution of that namespace's frozen `Order3Certifier` on real cells 11–44 under Campaign A's own authorization.

Campaign B, as executed, never reaches that surface:

- The selected route was abandoned before freeze (`phase_c/EXECUTION_DECISION.md`), so no authorization was requested
  and the guard never left DENY.
- The one route this successor *derived* (TCT0, theorem TC-T) takes Ĝ := 0. It proposes no order-3 candidate of F,
  calls no order-3 entry point, and records no order-3 field of F. `code/tct_inputs.py` asserts
  `order3_fields_present = false` and refuses if any `G`-family key appears in its output; all five measurement records
  carry that flag.
- `tct_inputs.py` does import the frozen chain through `tc_producer._import_chain()`, which imports `cusum_order3` for
  the Aux5 bootstrap and instantiates the *Aux3* certifier (`ReplayAux3Certifier`), exactly as Campaign A's
  qualification replay did. `certify_real_cell` and `rung3_engine.certify_order3` — the gated entry points that hold
  the registry check — are not executed, and `rung3_residual.g_residual` is not called at all.

**Obligation carried forward, unchanged and unsatisfied.** The adjudicator's *adoption* obligation on Campaign A still
stands: the registry sentence, read alone, misleads about cells 11–44, and the cross-reference must be owned by a
successor. This successor does not discharge it, because discharging it while Campaign B produced no order-3 evidence
would attach the bridge to the wrong campaign. **Any successor that evaluates a real order-3 CUSUM cell — route C2 of
the continuation plan — must issue the bridge as its own artifact**, naming
`p5y_k5_lower_front_order3/evidence/tc_r1/SEAL.json` `disclosure_C7_parallel_channel` and its own authorization, before
its freeze. Recorded here so the obligation is not lost with Campaign B's stop.

## N3 — the manufactured oracle covers r = 0 and m = 1; the r ≥ 1 source tower and the W assembly rest on cross-checks

**Status: DOES NOT BECOME LOAD-BEARING for Campaign B as executed, and is partly retired.**

The tail domain does introduce qualitatively new source-tower behaviour: the frozen J/h Leibniz tower, which was
harmless at the lower front, is the *dominant* term at the tail (σ3 = 5.9–67.2 and σ4 up to 355 from the pure tower at
cell 309, against whole-cell magnitudes of order 4). So the question the adjudicator raised is live at the tail.

Campaign B answers it without new manufactured fixtures, because it does not *trust* the tower — it **intersects the
tower with adopted, independently certified evidence for the same objects** (theorem TC-T premise (P3′)):
`auxiliary_evidence.candidate_suprema['S:r:3'] + midpoint_eps['S:r:3']` for σ3, and `['h:j:3']` for the h-tower. Those
Aux3 quantities are inside the frozen producer's 262-field identity gate, and the minimum of two valid upper bounds is
a valid upper bound. Where the two disagree they disagree by 2–18× and the adopted evidence is the tighter, so the
tower is no longer the binding premise on the tail; where only the tower exists (order 4) its contribution enters only
through ρ²·Env4/2 ≈ 0.3 of a radius ≈ 3.9, i.e. 8%.

The W assembly and the order-2 centre — the other half of the blind spot — are now covered by a **new** gate this
successor introduces, which Campaign A did not have: `tct_rule.derived_identity_gate` rebuilds the adopted record's
`R2_interval` for every m from the replayed Ĥ_r(a) and W enclosures plus the record's own `eps_cell_refined` and
requires containment in the record interval within 10⁻⁶ relative (measured worst gap 3.6·10⁻⁸, 20/20 comparisons).
A swapped W endpoint or a wrong centre moves an endpoint by O(10⁻²–1) and is caught.

**If and when a route with a real Ĝ is executed** (continuation C2), N3 returns in full: manufactured fixtures at the
tail geometry (e₀ ∈ [1.62, 2.10], ρ ∈ [0.040, 0.055], A0 ≈ 5.8–7.7, A2 ≈ 278–646) must be added, because the existing
fixture families run at e₀ ∈ [−0.2, 0.2] and ρ ≤ 0.02 and exercise neither the tail's ρ² regime nor its atom constants.
That is scoped in the continuation plan, not here.

## N5 — the four new order-3 fields have no identity gate

**Status: RETIRED for Campaign B as executed. The trust surface is not entered.**

N5 is precisely about `delta_G`, `eps_src[3]`, `sup.G` and `abs_G_at_a` — the fields with no adopted predecessor.
Route TCT0 sets three of them to zero by construction (`sup.G = 0`, `abs_G_at_a = 0`, and `delta_G` is not a producer
output but a closed-form combination `3k₁s_H + 3k₂s_D + k₃s_F + σ3` of quantities that *are* identity-gated), and the
fourth, `eps_src[3]`, is the adopted Aux3 `midpoint_order3_eps` value carried from the sealed record. So the campaign's
enclosures depend on **no un-gated order-3 quantity at all**, and the structural safeguard the adjudicator described
(order-3 enters only through a non-negative half-width, the centre staying the adopted order-2 candidate) is not merely
sufficient here — it is vacuous, because the half-width has no order-3 candidate in it.

Two further gates were added anyway, and both are reported in
`evidence/forecast_r2/TAIL_FORECAST_R2.json`:

1. the **derived identity gate** above, which closes the Ĥ_r(a) / W gap that N5's cousin left open;
2. **two independent rule paths** (`tct_rule.tail_enclosure` through the frozen `tc_rule`, and
   `tct_rule.tail_enclosure_crosscheck` re-derived from `theorem/THEOREM_TCT.md` importing no `tc_rule`) that must
   agree as exact rationals on every cell and every m; they agree 20/20.

**If and when a route with a real Ĝ is executed** (continuation C2), N5 returns unchanged and an additional
consistency gate becomes worthwhile, since the adopted records make two invariants available that Campaign A did not
check: `abs_G_at_a ≤ sup.G` (holds on all 170 adopted objects, at the near-constant ratio 0.680–0.681) and
`delta_G > 0`. Both are refusal-only — they can reject a record but never tighten an enclosure — so they are safe to
pre-register. Recorded for the successor.

## Summary

| note | load-bearing for Campaign B as executed? | disposition |
|---|---|---|
| N1 / C7 | no — no order-3 entry point reached, guard never left DENY | obligation restated and assigned to the first successor that evaluates a real order-3 cell; historical registry untouched |
| N3 | yes in substance, answered without new fixtures | tower intersected with adopted Aux3 order-3 evidence (P3′); W/centre covered by the new derived identity gate; tail fixtures scoped for C2 |
| N5 | no — the four fields are zero or adopted | retired here; two new gates added; invariants pre-registered for C2 |
