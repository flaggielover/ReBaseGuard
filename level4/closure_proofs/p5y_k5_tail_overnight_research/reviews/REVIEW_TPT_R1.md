# REVIEW_TPT_R1 — independent adversarial review of Theorem TPT / TPT-B (route E_assembly)

ROUTE_REVIEW: NOT_READY

Reviewer: independent, read-only (I did not author any of the route). Date 2026-09-28 (review run 2026-09-27T18:3xZ).
Scope: `streams/E_assembly/THEOREM_TPT.md`, `tpt.py` (sha256 `77c1646e…` = HEAD `ccc4ea36`), `test_tpt_guards.py`,
`validate_tpt_synthetic.py`, `validate_tptb_synthetic.py`, `v3/TPT_V3_REPORT.md`, `v3/tc_reder.py`,
`v3/tpt_v3_lower_front.py`, `validation/TPT_SYNTHETIC.json`, `TPTB_SYNTHETIC.json`, `TPT_V3_LOWER_FRONT.json`, read
against THEOREM_TC, THEOREM_TCT, K5_GLOBAL_BRIDGE, C5 (adjudication §7–§9, route search), floor r2, ROUTE_AUDIT_R1 and
the campaign graph. NS = `level4/closure_proofs/p5y_k5_tail_overnight_research`; SCR = the session scratchpad.

**Quarantine conduct of this review.** No quantity was computed for any CUSUM cell, at any drift in [1.2, 2.6], or
from any `TCT_INPUTS_30x` / `REGISTRY_C2` / target file. No historical module was imported or run. All runs are on
the exact finite-state fixtures of `code/ov_fixtures.py` (e0 ∈ {1/8, 1/4, 1/2}, declared in §R before running) and on
two hand-written synthetic profiles at e0 ∈ {1/2, 3/4}. I ran the route's code with `python3 -B` (no `.pyc` written
into NS) and with `ov_quarantine.LEDGER` redirected to `SCR/review_tpt/REVIEWER_LEDGER.jsonl`, so this review wrote
nothing into NS except this file (NS ledger: the lines added during my session are other streams' RSO runs, not
mine). I did not call `validate_*.main()` (it overwrites committed JSON) nor `ov_quarantine.scan()` (it writes under
`ledger/`). Git: `git show` / `git log` / `git diff` only.

## 0. Summary

| question | finding |
|---|---|
| 1 derivation | **Sound.** TPT, TPT-M, TPT-P, TPT-D, Lemma TC-P (under TC (P1)–(P4) and under TC-T (P1), (P2′), (P3′), Lemma G), TPT-B all hold. Wording defects: TPT-O "attained" (N1), Lemma TC-P "no inequality uses s = ρ" (N2), "already certified by TC" (N3), TPT-G sign premise (N13). No hidden assumption breaks soundness; the ones that matter for a consumer (H_K1 must be the consumed H_final, M_k = mag(H_final), empty-intersection refusal, exact types) are consumer-contract gaps (N5–N7). |
| 2 novelty | **Genuinely new** (N15): C5 adjudication §9 lists "every transport using a third certified input (a midpoint or sub-cell enclosure of R'')" as unexcluded; TPT is neither B2 nor D3. Not a relabelling. |
| 3 implementation | **Correct; not broken.** 0 unsound cases in 576 exact-truth evaluations incl. 192 with interior cap splits (§R, A3); matches the theorem on every branch I could reach; guard tests pass on r1 and fail on r0 (verified). Guard *overclaim* (N4) and missing fail-closed branches (N5, N6). |
| 4 tests | **Inadequate as committed** (B2, B3): TPT-B's B4 control is a tautology; V1's control never touches the transport; V2 was never run; the cap/split path has no truth test; "V4 independent" and V3 independence are weaker than claimed (N8). My A2 shows the transport check *can* fail — so the fix is cheap. |
| 5 leakage | **Defect** (B1): `graph/K5_TAIL_DEPENDENCY_GRAPH.md:110` combines TPT-G's 1/2 and 1/3 charges with tail-cell S̄ shares ("≈ 60 % + ≈ 20 % of S̄ historically", sourced from 306–309) — exactly the combination THEOREM_TPT.md:154-155 says "was not done". No target value was computed by the route (ledger clean). Cell 306 not addressed (N12). |
| 6 governance | Closure-only label **correct**; `fail_closed[3]` citation inapt (N10). **FREEZE_READY not justified**: no freeze design exists for extraction of per-r inputs on the TC-T/C2 path, reproduction gate, decoy qualification or exactly-once mechanics, and that path has zero validation (B4). |

Route states I can support: theorem + `tpt.py` on the TC (lower-front, real-Ĝ, registry-r1) input path —
**VALIDATED_NON_TARGET**; on the tail's TC-T/C2 input path — **IMPLEMENTED, unvalidated**; overall **not
FREEZE_READY**; r2 status **closure-only**. Gates: G1 **disputed** (B1), G2 PASS, G3 PASS with N1/N2/N13 wording,
G4 PASS (reproduced, §R A1), G5 PASS on TC path only (B4), G6 PARTIAL (N8), G7 PASS for the route's own runs
(ledger), G8 **FAIL at campaign level** (B1), G9 NOT YET (B4, N5–N7, N9, N11, N12), G10 **undetermined**
prospectively (N14).

## B. Blockers

### B1. An implicit tail forecast built on TPT-G is in the campaign record; THEOREM_TPT's "was not done" is false at campaign level

* THEOREM_TPT.md:154-155: *"Combining this proposition with committed per-cell radius decompositions or C8 factors
  to predict any tail cell's Γ is a target-equivalent proxy. It is forbidden in this campaign and was not done."*
* `graph/K5_TAIL_DEPENDENCY_GRAPH.md:110` (committed `4403f86f`, after TPT-G `9db36e13`): rank-1 row *"the Taylor
  remainder terms linear and quadratic in |t−e0| (≈ 60 % + ≈ 20 % of S̄ historically) are charged at their edge
  value over the whole cell. The exact profile charges ≈ 1/2 and ≈ 1/3 (TPT-G)"*, owner **TPT**.
* The 60 % / 20 % are **tail-cell** shares: `graph/sources/graph_A_consumer.md:488-491` (*"A0·ρ·f_G is 63.37 /
  61.59 / 60.04 / 58.80 % of S̄"* for 306–309) and `:512-513` (*"A0·ρ²·Env4/2 is 18.01 / 19.86 / 21.52 / 23.06 % of
  S̄"*). S̄ is the m = 5 tail radius mean (`graph_A_consumer.md:80`), and the penalty on 306–309 is
  ρ·(x_hi − ρ/2)·(|C_lo| + S̄) (`graph_A_consumer.md:126-128`). Share × charge is a direct estimator of TPT's
  tail penalty reduction, i.e. "a ratio from which such a Γ could be inferred" — load-bearing under
  ROUTE_AUDIT_R1.md:560-563. It also ranks the route by target-cell data (S1).
* Motivation provenance: the first version of §0 (`git show af4365aa:…/THEOREM_TPT.md`, line 16) said the midpoint
  radius is *"typically orders of magnitude smaller"* than rad_r(ρ). That is true at the tail
  (`graph_A_consumer.md:256-257`: A0·f_H is 0.085–0.115 % of S̄ at 306–309) and false on the only non-target real
  data (0.94–0.97, TPT_V3_REPORT.md:125-126). The erratum TPT-E1 (THEOREM_TPT.md:17-21) fixes the claim but does not
  disclose where "typically" came from. I cannot establish what the author saw; the record is consistent with a
  motivation informed by tail radius decompositions.
* Aggravating fact: on the tail every TPT input (per-r f_F…f_G, Env4, Ĥ_r(a), W, A of the supply) is already a
  committed number (e.g. Env4 per r for 306–309 at `graph_A_consumer.md:505-508`), so TPT's tail Γ is a closed-form
  function of committed data. Blindness rests entirely on nobody doing that arithmetic; the graph row does most of it.
* **Required before any freeze preparation:** (a) retract or quarantine-label the graph row (and its JSON twin,
  `K5_TAIL_DEPENDENCY_GRAPH.json` route entries citing TPT) as a target-equivalent proxy; (b) correct
  THEOREM_TPT.md:154-155 to disclose that the combination exists in the campaign record; (c) record in THEOREM_TPT §0
  what tail-derived material was read before af4365aa; (d) a user ruling (U3 context) that a TPT floor extension
  would be decided *knowing* this proxy, as ROUTE_AUDIT_R1 requires for C8-factor knowledge (§7 U3 liability).

### B2. Negative controls that cannot fail, or do not exercise the object under test (S2, S7)

* **TPT-B B4 is a tautology.** `validate_tptb_synthetic.py:77`:
  `viol_nc = sum(1 for d in devs for x in d if x > max(d) / 2)`. For any list with max > 0 the maximum element
  exceeds max/2, so this "detects" on every fixture regardless of `rad_at`, `penalty_blocked` or anything TPT-B
  computes. THEOREM_TPT.md:185 reports it as *"B4 truth-relative negative control detected | 24/24"*.
* **V1's control does not touch the transport.** `validate_tpt_synthetic.py:147-149` replaces every radius by
  max(true deviation)/2 and counts `d > r`; it exercises only the comparison operator, never `penalty_closed`,
  `lo_hi_polys` or `evaluate`. There is **no negative control for the transport soundness check**
  (`sound_transport_certified`, `:192-193`), which is the claim that matters.
* My A2 (§R) shows the committed fixture set *does* have power against a planted transport under-estimate (θ·P
  detected for θ = 0.99 on 2/12, 0.9 on 5/12, 0.5 on 11/12; implementation mutants detected on 2–6/12), so this is
  cheap to repair — but the committed evidence does not show it, and the TPT-B row presents a vacuous check as a pass.
* **Required:** replace B4 by a truth-relative plant through `penalty_blocked` / `rad_at`; add a transport-level
  plant (θ·P and at least one implementation mutant) to V1 with coverage; correct THEOREM_TPT.md:185.

### B3. Declared validation obligations V2 were never executed; claims outrun code

* THEOREM_TPT.md:217-220 declares V2: non-monotone profiles (P₊ path), H_K1 binding on part of the cell, and a planted
  invalid profile (L above the true R'') that must make the check fail. The ledger/JSON purpose string claims
  "TPT V1/V2/V4" (`validate_tpt_synthetic.py:235`).
* `grep H_K1` finds **no** use in `validate_tpt_synthetic.py` or `validate_tptb_synthetic.py`; `tpt.py` has **no** P₊
  implementation at all. The only cap exercise is `test_tpt_guards.py:68-78` (a dominance/ordering probe, no truth)
  and V3's variant B, where the cap never binds (TPT_V3_REPORT.md:157). So the split code (`tpt.py:155-206`,
  `:350-366`) — the only non-trivial branch — has no truth-relative test in the committed evidence.
* My A3 (§R) exercised the cap/split path against exact truth with 0 unsound cases, so I expect the code to pass;
  but the route must commit its own V2 (or delete V2 from §4 and the purpose string), and state that the P₊ branch
  is unimplemented (THEOREM_TPT.md:131 says "use P₊" for Ĝ ≠ 0 with signed data).

### B4. The tail input path (TC-T / C2 consumer) is unvalidated and has no freeze design

* V3 validates only the **TC** path: real Ĝ, registry-r1 Lemma Dv′ constants taken *as given*
  (TPT_V3_REPORT.md:41), (P3) tower. The tail uses **TC-T**: Ĝ := 0, (P2′) f_G = 3k₁s_H + 3k₂s_D + k₃s_F + σ3
  (+ eps_src[3]), (P3′) two towers with the mean-value correction, and the D4 minimum over Lemma G ∪ Lemma Dv′ r2 via
  `c2_d5_forecast` → `deflated_consume` → `tct_rule` (floor r2 `quantity_compared.adoption_quantity`).
* TC-T per-r inputs exist **only** for cells 305–309 (`p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_305..309.json`),
  all quarantined. There is therefore no non-target real cell on which the per-r extraction from the frozen
  `tct_rule` can be rehearsed against a committed whole-cell enclosure.
* Nothing in the route specifies: (a) how per-r (f_F, f_D, f_H, f_G, Env4, Ĥ_r(a), W) are extracted from the frozen
  `tct_rule` path without re-deriving them by hand; (b) a reproduction gate that re-derives the committed 𝓗_5 (and
  C2's committed `Gamma_exact` for S_I1, floor r2 `fail_closed[2]`) exactly, inside the one sealed execution, before
  P* is computed; (c) a decoy/synthetic qualification of that extraction on manufactured TC-T-shaped inputs (Ĝ = 0,
  two towers); (d) exactly-once mechanics (consumed ref, sealed result, no re-run).
* A reproduction gate at s = ρ cannot see an error that preserves rad_r(ρ) but mis-shapes rad_r(s) (e.g. a term
  moved between the constant and the s-coefficients). The gate should therefore also check the per-r coefficient
  vector against the committed per-r values (f_*, Env4 are committed per r for the tail) — or the extraction must
  come from the frozen code path itself.
* This is exactly the work of freeze preparation, but it is also what G5/G9 require before FREEZE_READY can be
  claimed; nothing of it exists.

## N. Notes

**N1. TPT-O "attained" is false in the stated class.** THEOREM_TPT.md:86-91: the witness has R'' = L on (e0, x_hi]
and R'' = U on [x_lo, e0); R'' jumps at e0 (and wherever L, U jump), so R is not C² — the Setting (THEOREM_TPT.md:42-43)
requires C². The bound is the **supremum** over C² members (mollify), not attained. Optimality is unaffected;
C5-T's witness (constant R'') was genuinely C². Rephrase.

**N2. Lemma TC-P proof wording.** THEOREM_TPT.md:114: *"No inequality of TC uses s = ρ except the final
substitution."* Literally false: (P3) Env4 uses |t| ≤ ρ inside (THEOREM_TC.md:39-44), and TC-T's (P3′) cell tower
uses ρ in the mean-value correction (THEOREM_TCT.md:97, 100-104). Both are whole-cell constants and remain valid at
every u ∈ [e0, t] ⊂ C, so the lemma is correct. I checked each term: p0/p1/p2 are Taylor expansions at e0 with
integral remainders bounded by the whole-cell Env4 — valid; f_G (σ3, a **midpoint** premise) enters only as the
φ'''(e0) coefficient of s, which is a midpoint object — valid; σ4 enters only Env4, a **whole-cell** premise —
valid; A0/A1/A2 (Lemma G, Lemma Dv′) are uniform on C and theorem TC §4 step 3 is pointwise — valid; the centre
relaxation (t − e0)Ĝ_r(a) ∈ [−s|Ĝ_r(a)|, s|Ĝ_r(a)|] per r — valid; W enclosures are whole-cell, so constant-in-t use is
valid. Restate the sentence precisely.

**N3. "the pointwise profile that theorem TC already certifies"** (THEOREM_TPT.md:36; commit msg `af4365aa`). TC §3
certifies only the ρ-substituted enclosure. The profile is certified by the **new** Lemma TC-P; it is a small delta
of TC's proof but it is new and must be reviewed as such (this review does so, N2).

**N4. Geometry guard overclaim.** `tpt.py:13-16` and THEOREM_TPT.md:206 claim *"a target cell cannot be evaluated
through this module even under a false label"*. `rad_poly`, `lo_hi_polys` and `whole_cell_enclosure` do not depend on
e0 at all, and each side of P* is affine in e0. My B1 run shows `whole_cell_enclosure` identical and
I_right(e0+d) = I_right(e0) + d·∫(−lo) exactly under a shift of a synthetic profile from e0 = 1/2 to 3/4. So a
target's inputs under a translated geometry would be evaluated exactly. The effective barrier is the input-path
quarantine (`ov_quarantine.FORBIDDEN_PATH_PATTERNS`), which `tpt.py` does not call. No one did this; the claim must be
weakened, and a freeze must not rely on the geometry guard as a safety property.

**N5. No fail-closed on pointwise-empty intersection.** THEOREM_TC §6 / TC-T §4 consumption says "refuse if empty".
`tpt.py` checks emptiness only at s = ρ (`whole_cell_enclosure`, `tpt.py:261-269`). Since lo(s) ↓ and hi(s) ↑, the
intersection is narrowest at s = 0. My B3 run: H_K1 = [hi(0) + 1/100, hi(ρ)] gives L(e0) > U(e0), non-empty at ρ,
**accepted**, P_tpt = 0.1205 (smaller than without the inconsistent cap). Under valid inputs this cannot happen, so
it is not unsoundness — but it is exactly the signal that one input is invalid, and TPT consumes it silently. A
freeze must refuse if max(capLo, lo(0)) > min(capHi, hi(0)). (V3 computed this as a probe,
`tpt_v3_lower_front.py:200`, but it is not in `tpt.py`.)

**N6. No exact-rational contract.** My B2 run: a `float` Env4 is accepted and `P_tpt` comes back as `float`
(Fraction·float → float; no outward rounding). `tc_reder._nn` enforces `Fraction` (`tc_reder.py:59-64`); `tpt._check`
(`tpt.py:136-152`) does not. A freeze must enforce exact types for every field.

**N7. What H_K1 and M must be.** THEOREM_TPT.md:123-126 names only the K1 `R2_interval`. TPT-D's dominance over the
*consumed* clause needs L ≥ H_final.lo and U ≤ H_final.hi, where H_final is everything the adopted consumer
intersects (R2, AD/deflated, T-EXT C1/C2, TC-T). With only R2, TPT can lose to C5-T on H_final wherever another
enclosure binds. Also `penalty_frozen` uses mag(H) (`tpt.py:280-285`), equal to the consumed M_k only when
M_k = mag(H_final); a freeze must bind H_K1 := H_final and assert M_k = mag(H_final) (or intersect with [−M_k, M_k]).

**N8. Independence is weaker than stated.** (a) V4 "independent second implementation" (THEOREM_TPT.md:224) is
`penalty_riemann` in the same module, sharing `lo_hi_polys`; it checks integration only. (b) `v3/tc_reder.py` imports
nothing from `tpt.py` (verified by reading; no shared code), but V3 builds `tpt.CellProfile` *from tc_reder's terms*
(`tpt_v3_lower_front.py:115-120`), so "tpt profile polys equal independent" (`:156`) and "P_tpt = independent exact
P*" (`tc_reder.py:171-180`, the same closed-form antiderivative algorithm) share the input derivation and the
Lemma TC-P reading. The only external check is the exact s = ρ reproduction of committed H_TC (136/136), and the
A-constants are taken as given (TPT_V3_REPORT.md:41). On real data there is no ground truth for the s-profile shape
(the report says so, :156).

**N9. Provenance drift.** TPT_V3_REPORT.md:14 cites `tpt.py` sha256 `9d497ef1…` (= r0, `af4365aa`), but the committed
V3 JSON records `8a17dd1e…` (= r1, `48392744`). HEAD `tpt.py` is `77c1646e…` (append-only TPT-B addition, `ccc4ea36`,
verified by `git diff 48392744 ccc4ea36`). A freeze must pin one hash and regenerate every validation against it.

**N10. Floor r2 citation.** THEOREM_TPT.md:198 cites `fail_closed[3]`. In `K5_TAIL_ADOPTION_FLOOR_R2.json`,
`fail_closed[3]` (0-indexed) is the chosen-supply restriction, which TPT does not touch. The operative anchor for
"closure-only" is `quantity_compared.adoption_quantity` (*"computed by the frozen consumer path … with the atom
constants S substituted and every other input unchanged"*) together with `fail_closed[2]`. The conclusion
(closure-only; floor extension needed, U3) is correct. ROUTE_AUDIT_R1.md:42 uses the same inapt index.

**N11. Chain clause.** K5-B's γ_k uses Γ_k (K5_GLOBAL_BRIDGE.md:26-27). THEOREM_TPT.md:199 says the chain is "not
changed". A consumer must state whether γ_k consumes Γ_TPT; for γ_k only g(x_k) is needed, for which I_right(ρ) alone
suffices. On the tail only the direct clause is the adoption quantity (`graph_A_consumer.md:140`), but the frozen
`k5b_literal` evaluates both.

**N12. Cells 305/306 not addressed.** 306 is closed under I1's supply and not certified under I2's, with
Γ(5, 306; S_I2) = +0.005159101140006536 sealed once (ROUTE_AUDIT_R1.md:89; C12-R2). Floor r2 F1′(d) needs Γ < 0 under
EACH supply, so a consumer that lowers the penalty is foreseeably the lever that would flip exactly that clause: a TPT
evaluation at 306 would be designed knowing the adverse I2 result — the same liability ROUTE_AUDIT_R1 records for
306-e (`:319`, "designed knowing the adverse I1/I2 result"). 305 was adopted under r1 and may not be re-adjudicated
under a new rule (C10, floor r2 §2). THEOREM_TPT says nothing about either. Before any freeze the route must state
305 OUT, decide 306 IN/OUT prospectively, and if IN, carry the known old-clause results as a disclosed
result-chasing risk (HIGH for 306).

**N13. TPT-G premises.** THEOREM_TPT.md:139-152 requires "all coefficients ≥ 0", which includes c ≥ 0, i.e.
lo(0) ≤ 0 on the right (binding) side — a data-dependent sign premise, stated but easy to miss. "c collects the
centre, the W half-widths and rad(0)" is imprecise: on the right c = −W_lo − Σ_r (Ĥ_r,lo − rad_r(0))/m. The finite-ρ
ratios `(x0/2 + ρ/3)/(x0 + ρ/2)` and `(x0/3 + ρ/4)/(x0 + ρ/2)` I re-derived and confirm.

**N14. G10 is undetermined prospectively.** The only non-target real evidence gives 0.7–2.5 % of the penalty
(TPT_V3_REPORT.md:122) — cosmetic there. Any claim of material tail value goes through the B1 proxy. Say so.

**N15. Novelty (question 2).** TPT is not in C5's 14-route ledger (`p5y_k5_tail_c5_exhaustion/phase_3/C5_ROUTE_SEARCH.md:40-56`).
B2 (`:50`) needs g at sub-midpoints; TPT keeps one midpoint. D3 (`:53`) needs R'''; TPT needs none. C5_ADJUDICATION.md:178-180
and :206-208 list "a transport consuming a third certified input … a midpoint or sub-cell enclosure of R''" as
unexcluded; the TC-P profile is such an input (certified by the new Lemma TC-P from the same premises). Genuinely
new, not a relabelling. Caveat: its "third input" is a finer reading of the same certified premises, not new
certified information, so it cannot exceed what those premises imply (TPT-O, within the relaxation scope).

**N16. TPT-B.** Theorem sound (per-block constants valid on the block; pointwise use legitimate by TC §4 step 3;
quasi-convexity per piece ⇒ sup at piece ends). My B4 run with overlapping, non-monotone blocks: P*_B = 0.189725 ≥
dense lower running sup 0.189705, < cell-max TPT 0.215165. Its validation uses k_i bounded over [0, e_hi], not per
block (`validate_tptb_synthetic.py:34`), so "negligible gain" (THEOREM_TPT.md:187) is fixture-specific. At the tail its
blocks would come from REGISTRY_C2 sub-blocks (a quarantined path). Correctly not ranked.

**N17. Minor.** `_crossing` uses a fixed 60-bit bisection (`tpt.py:155-177`) — sound (non-binding side), slightly
loose; `evaluate` raises `AssertionError` on dominance failure — a freeze should turn every such branch into a
recorded refusal, not an exception that aborts a sealed run half-way. Two V3 prototype runs on cells 11/44 were logged retroactively (TPT_V3_REPORT.md:159; ledger entries at 17:59:41Z); harmless here (non-target), but an exactly-once design must make logging precede execution.

## R. Reviewer runs (exact commands and outputs)

Declared rule before running: synthetic FSM fixtures only; (A1, A2) the 12 committed V1 configs; (A3) e0 ∈ {1/8, 1/4,
1/2} × ρ/e0 ∈ {1/8, 1/4, 1/2, 3/4} × m ∈ {1, 2, 3, 5} × Ĝ ∈ {zero, real} × pert ∈ {1/1000, 1/100}, n = 4, first
buildable seed from 101 upward per combination, each in three variants (plain; a **valid** K1 cap built from a certified
truth enclosure widened to lo(ρ/2)/hi(ρ/2) so that the split path runs; a synthetic c-weighted W term w(e) with its
exact whole-cell enclosure), within a 900 s budget. Scripts: `SCR/review_tpt/rv_common.py`, `rv_attack_a.py`,
`rv_attack_b.py`, `rv_r0_test.py`; outputs `RV_ATTACK_A_*.json`, `RV_ATTACK_B.json`.

**A1 reproduction.** `cd SCR/review_tpt && nice python3 -B rv_attack_a.py a1 a2` → `A1 all match: True 12` (P_tpt and
P_c5t of all 12 committed V1 fixtures reproduced exactly from `tpt.py` HEAD).

**A2 transport-level negative controls** (same run). Detection = a TRUE lower bound of sup g (grid max, 401 points)
exceeds g_hi + P′:

    theta_0.99_detected 2 / 12     theta_0.95_detected 4 / 12
    theta_0.9_detected  5 / 12     theta_0.5_detected 11 / 12
    M1_no_centre_motion_detected_by_truth 3 / 12   (P'/P 0.764-0.972 on the 6 real-G fixtures, 1.0 on G=0)
    M2_t_sign_error_detected_by_truth     6 / 12
    M3_no_Env4_detected_by_truth          2 / 12   (P'/P 0.969-0.9997)
    M4_radius_at_half_s_detected_by_truth 4 / 12
    true_excess_lower/P range 0.338 ... 0.998

So the committed fixtures can detect ≥ 1 % transport under-estimates on some fixtures; this is the control B2 asks the
route to commit.

**A3 unsoundness search (cap / split / W).** `cd SCR/review_tpt && nohup nice python3 -B rv_attack_a.py a3 > rv_attack_a3.log 2>&1 &`
(wall 317 s) →

    evaluations 576 (192 plain, 192 cap, 192 W; m = 1,2,3,5 x 144 each; e0 in {1/8,1/4,1/2}; rho/e0 in {1/8,1/4,1/2,3/4})
    build_failures_skipped 3, evaluate_raised 0
    UNSOUND_by_truth 0            (true grid max of g never exceeds g_hi + P_tpt)
    certified_sound 576 / 576     (rigorous sup g upper bound <= g_hi + P_tpt)
    P_ge_exact_lower_bracket 576  (independent 200-bit exact bracket of P*, cap included)
    dense_running_sup_le_P 576    (running sup over e computed WITHOUT TPT-M <= P_tpt)
    cap_variants_with_split 192   (all 192 with an INTERIOR split on both sides)
    max (P_tpt - 200-bit upper bracket)/P = 2.8e-36 (the 60-bit split costs nothing measurable)
    true_excess/P max 0.989 (power), min P_tpt/P_c5t 0.262 (large gains when rho/x0 is large)

I found no input on which P_tpt < sup g − g_hi. Under valid inputs the implementation is sound on every branch I
could reach (plain, capped with interior splits on both sides, W ≠ 0, Ĝ zero and real, m up to 5).

**B probes.** `nice python3 -B rv_attack_b.py`:

    B1_translation: whole_cell_enclosure_equal_under_e0_shift true, I_right_affine_exact true, I_left_affine_exact true
    B2_float_input: accepted true, P_tpt_type float
    B3_empty_pointwise_intersection: refused false, L(e0)>U(e0) true, whole_cell_at_rho_nonempty true, P_tpt 0.1205033
    B4_tptb_nonmonotone_blocks: P_star_B 0.1897248, P_tpt_cell 0.2151646, dense_lower_running_sup 0.1897046, PB_ge_dense true
    B5_test_tpt_guards (ledger redirected): exit 0, "TPT GUARD TESTS PASS"

**r0 discrimination.** `git show af4365aa:…/tpt.py > SCR/review_tpt/r0/tpt.py; python3 -B rv_r0_test.py` →
`exit 1`, G1/G2 None, G3 rad_poly/lo_hi_polys/whole_cell_enclosure/penalty_riemann_lower unguarded,
G4 `raised: True, TPT-D dominance violated`, `TPT GUARD TESTS FAIL` — confirms THEOREM_TPT.md:204 ("passes on r1 and
fails on r0").

## X. What I could not check

* Anything at the tail (by design): whether the TC-T/C2 per-r inputs, extracted as a freeze would extract them,
  reproduce the committed 𝓗_5; whether H_final = 𝓗_5 on both ends there; whether M_k = mag(H_final) there.
* The frozen `tct_rule` / `deflated_consume` / `c2_d5_forecast` code paths (reading only; not run, not imported).
* Real-data soundness of the s-profile shape: no ground truth exists for real cells; only s = ρ is externally
  anchored (N8).
* Lemma G / Lemma Dv′ themselves, the K1 records' Arb outward rounding, and the W enclosure construction — taken as
  adopted; TPT does not change them.
* Authorship/intent behind the graph row and the original "orders of magnitude" sentence (B1): I report the record,
  not the author's knowledge.
* The P₊ branch (not implemented) and the (P3) Env4(s) refinement (not implemented).
* Concurrent sibling streams (e.g. `IDEA_ADLR_ATOM_DIRECT.md`, written during this review) were not reviewed.

## Path to ACCEPTED_FOR_FREEZE_PREPARATION

1. B1 (a)–(d). 2. B2 and B3 repaired and re-run against one pinned `tpt.py` hash (N9), with coverage stated.
3. N4–N7 turned into enforced refusals in `tpt.py` (empty pointwise intersection, exact types, H_K1 := H_final,
M_k check) with truth-relative tests. 4. A written freeze design for B4 (extraction from the frozen path,
coefficient-level plus s = ρ reproduction gate against committed values, decoy qualification on manufactured TC-T
inputs, exactly-once mechanics) and an explicit 305-out / 306 decision (N12). 5. A user instruction for a floor
extension (U3) before any of this is frozen, since the route is closure-only under r2.
