# Phase C — Independent adversarial review of the Phase B strategy

```text
REVIEW_VERDICT = PASS_WITH_NOTES
```

**Object.** `phase_b/STRATEGY.md`, `phase_a/OPEN_CELL_AUDIT.md`, `phase_a/OPEN_CELL_MAP.json` and `code/open_cell_map.py`
(uncommitted, in the worktree at `84299314`).

**Verdict in one paragraph.** No finding invalidates a proposed certification or the selection **E**. The mathematics
holds:
- T-EXT: the transport has the right derivative orders, the parity facts are correct, and every hull quantity is used
  on its own domain.
- K5-B-T: sound.
- Phase A: its classification reproduces, including the graded boundary at cell 40.
- The negative claims about a global shortcut and the front scalar zone survive an attempted counter-route.

The notes still matter. Four of them must be settled **before** the T-EXT freeze, because after the first evaluation
any change becomes a post-result choice:
- F1: qualification coverage at widened η;
- F2: a dominating consumption rule at zero cost;
- F3: sealing the lower-order tower bounds;
- F11: a pre-freeze guard and ledger.

The claim in §3 that anchors at a ≠ 0 cannot form multi-cell blocks is not supported (F8). One number in §8 is wrong
(F9).

## 0. Method and independence limits

**What I ran.** I ran no local_tower, r5_majorant or M5 evaluation at any η, no model solve, and no AWS access. I wrote
nothing except this file.
- **Graded zone, recomputed on rebaseguard-vultr-02, read-only.** I used the frozen `hermite6_ext.norm_table`,
  `constants_r4`, `graded_dag.resolvent_block` and the frozen venv, at 256 bits, on the clean clone
  `/root/work/k5c-base` at `84299314`. These are operator constants only. The code was passed on stdin, and no file
  was written.
- **Sealed slot-1 record.** I read it and did arithmetic on the recorded numbers only.
- **Phase A diagnostics.** I recomputed them from the convenience extract `cells_min.json`. I spot-checked records
  0 (m = 1), 50 (m = 1) and 305 (m = 5) against the host `k4_records`: identical.
- **Phase A map provenance.** `OPEN_CELL_MAP.json` sha256 is `9579f3ad…`, as stated. The worktree
  `code/open_cell_map.py` (`b50ec93b…`) is byte-identical to the host copy `/var/tmp/k5c-analysis/open_cell_map.py`.
  The per-m pass ranges equal `E6_POSITIVE_CONSUMPTION_OUTPUT.json`.
- **Contamination audit on the host.** There are uncommitted T-EXT drafts in
  `/root/work/k5c-dev/level4/closure_proofs/p5y_k5_remaining_cell_closure/transport_extension/code/`: six files dated
  2026-09-18 19:01 (`text_transport.py`, `text_consume.py`, `text_mutants.py`, `qualify_text.py`, …). There is dev
  evidence in `/var/tmp/k5c-analysis/dev/`:
  - `REPLAY_dev.json`: η = x1 replay, M5 and trace reproduced with rel 0;
  - `FIXTURES_dev.json`: synthetic fixtures only.

  I found no `evaluate` output: no `text-result.v1` JSON and no `hull_cells` file under /root, /tmp or /var/tmp. So I
  found **no evidence of a pre-freeze real evaluation at η > x1**.

**Independence limits.** I am a separate session and process of the same model (claude-opus-5). I am not a human and
not a different model family. I read the author's code and data, but I did not see the author's reasoning beyond the
documents. I relied on the convenience extract after a 3-record spot check. I did not re-run the E6 pass sets myself;
I compared them with the committed E6 output.

## 1. Findings

Each finding is labelled LOAD_BEARING only if it would invalidate a certification or the strategy selection.
**None does.** Findings F1–F3 and F11 are **pre-freeze conditions**: they cost nothing now, and they become
post-result or unfixable after the first evaluation.

**F1 — NON_LOAD_BEARING (pre-freeze condition). Widened-η qualification cannot be delivered by the existing fixture
families.**
- **The plan.** STRATEGY.md:155 promises "manufactured exact-truth fixtures at widened η".
- **Where the fixtures stop.** The R4 fixtures qualified up to η·C_e0 ≈ 1.0 (`QUALIFICATION_PROTOCOL_R4.json:180`,
  FR4_08: C_e0 ≈ 20, x1 = 1/20). The host dev widening reaches at most η·C_e0 = 1.60. At larger factors FR4_04 (≥ 4×)
  and FR4_06 (≥ 16×) refuse construction with `sup_cell ||K|| >= 1: no resolvent bound`
  (`/var/tmp/k5c-analysis/dev/FIXTURES_dev.json`, uncommitted).
- **What the frozen hull family needs.** It spans η·C_e0 = 0.48 (cell 1) to 10.7 (cell 40). That includes:
  - the regime where the ee entry of the resolvent block is **capped at C** (`graded_dag.py:108`), from cell 33 on.
    The cap was never active at slot-1: ee = 469.99 < C = 1232.84.
  - off-diagonal entries up to 911 (my recomputation, §2 item 8).
- **Consequence.** No exact-truth fixture exercises these code paths at the parameter scale of cells ≈ 6–40. The code
  is frozen and the paths are generic, so this is a qualification-completeness gap, not a soundness defect.
- **Repair.** Either:
  - add a σ-fixture family with an exact (non-Neumann) resolvent certificate that reaches η·C_e0 ≥ 11, det ≈ 0.05
    and the ee cap; or
  - freeze the consumption to the η range the fixtures actually cover, and say so.

**F2 — NON_LOAD_BEARING (pre-freeze condition; the most valuable missed route). A strictly dominating transport rule
costs no new address.**
- **The frozen rule and the better one.** STRATEGY.md:145–146 uses `L_k = L0 − (x_hi(k)²/2)·M5(x_hi(k))`. But the 40
  prefix hulls give `|R⁽⁵⁾(t)| ≤ M5(x_hi(j))` for t in cell j. The exact remainder
  `R'''(e) = R'''(0) + ∫₀ᵉ (e−t)R⁽⁵⁾(t)dt` then gives, for cell k with X = x_hi(k):

  ```text
  inf_{C_k} R''' ≥ L0 − Σ_{j=0..k} M5(x_hi(j)) · [(X − x_lo(j))² − (X − x_hi(j))²] / 2
  ```

  The weights telescope to X²/2, so this is never worse than the frozen rule. For j = 0 it can use the sealed slot-1
  M5. If M5(η) grows like η^p, the penalty shrinks by 2/((p+1)(p+2)): 1/3 for p = 1, 1/10 for p = 3, 1/36 for p = 7.
  The reach then grows by about 1.4–1.6× in e, at no cost.
- **Why the gain may be large.** The dev fixture FR4_05 (parity_leak) shows M5/true jumping from 1.8e3 to 2.5e5 when
  η doubles (synthetic, allowed evidence). Growth may be steep.
- **Why it must be decided now.** Once the M5(η) values are seen, choosing this rule is a post-result choice. Adopt it,
  or record its rejection, in the freeze.

**F3 — NON_LOAD_BEARING (pre-freeze condition). Seal the lower-order tower bounds from the same evaluation.**
- **What is available.** `r5_majorant.m5(towers, order=n)` (`r5_majorant.py:103`) already returns
  `M_n(η) = Σ|c|·sup‖P_e X⁽ⁿ⁾‖` for n = 2, 3, 4. These are certified bounds on sup|R''|, sup|R'''| and sup|R''''| on
  [0, η], with the same premises as M5.
- **How much sharper they are.** At x1 the sealed tower gives |R''| ≤ 1.43 for m = 1 (`tower_nodes` F:0:2, e = 1.432).
  The K1 enclosure of cell 0 gives M_R2 = 16,670, about 10⁴× larger.
- **What they would feed later.** Each use would need its own successor preregistration:
  - (a) a K5-B successor that floors H_k.lo at −M2 and caps M_k at M2 on cells ≤ 40. This is trivially valid, but the
    extension beyond the L-reach is modest (a few cells at most).
  - (b) hybrid anchors at a ≠ 0 (F8), which need M4(η).
  - (c) any graded-zone direct test.
- **Why now.** Re-running the towers after M5(η) is known would be a second, post-result derivation. Sealing
  M2–M4 per hull now costs nothing.

**F4 — NON_LOAD_BEARING. The proof's "monotone" justification is the wrong reason. The conclusion stands.**
- **Where.** STRATEGY.md:34 and :141–142, and the host draft `anchors_from_sealed`.
- **The right reason.** Soundness does not need monotonicity. Every rule is a valid inequality for any valid
  upper-bound inputs, and a minimum of valid bounds is valid. The sealed anchors are also not merely upper bounds:
  `V`/`_up` normalize every component to a radius-zero dyadic (`graded_dag.py:74–81`), and the record serializes
  them exactly (`executor_core.py:66–67`, 570–572). The dev replay reproduces M5 and the trace with rel 0.
- **Monotonicity also holds.** I checked it:
  - `resolvent_block` mode depends only on (C, C_e0, C_o0, k1, k2, η), never on anchors;
  - graded → scalar_fallback replaces min(val, C) by C, so no decrease;
  - d2/det, M_eo/det and d1/det are increasing in η;
  - `_minv`, `_min` and the V normalization are monotone.

  So "M5(η) nondecreasing" (L37) is right. Rewrite the proof step with the rule-wise argument.

**F5 — NON_LOAD_BEARING. P1 cites the wrong authority for the tower's regularity.**
- **The problem.** P1 (STRATEGY.md:125) cites P5X L5 for "R odd and C⁵". L5's countersignature certifies **R only**
  (`p5x_l5_independent_review/README.md:179`). It gives no numerical bounds (:181–183), and it leaves producer
  remainders to the producer (:159).
- **What M5(η) actually needs.** The e-regularity of the component objects (F_r, S_r, h_j, W_{r,j} as Banach-valued
  functions, to order 5–6) and the derivative identities used by `true_tower`. These are the R2/R3 producer premises:
  σ-parity at e = 0 (`R2_DESIGN.md` §3), and the K1 kernel-derivative norm machinery, which is valid on any window
  (`hermite6_ext.norm_table`).
- **Repair.** Both are e-uniform, so the extension to [0, η] is legitimate. It is the same basis slot-1 used on
  [0, x1]. Restate P1 accordingly: L5 for R, the R2/R3 premises for the tower.

**F6 — NON_LOAD_BEARING. The `local_tower` API does not bind x1 to base["eta"].**
- **The gap.** It checks key presence only (`local_r5.py:70–72`).
- **Why it matters.** A drift factor x1 < η with hull norms on [0, η] is unsound: lemma (a)/(b) needs drift ≥ every
  e in the hull.
- **Repair.** The T-EXT wrapper must refuse x1 ≠ eta. Make the host-draft mutants TM01 and TM05 (and TM02, TM03)
  required gates.

**F7 — NON_LOAD_BEARING. The notation L_k collides between two indexings.**
- **The collision.** §6 indexes L_k by the 0-based K1 cell. §1, §6 ("admits L₁ only") and K5-B index it by theorem
  cell.
- **The risk.** Assigning cell k−1's bound to cell k is unsound: its hull ends at x_hi(k−1) < x_hi(k). The other
  direction is merely conservative.
- **Repair.** Use distinct symbols. The host draft `text_consume.py` maps `cells[k]["L"]` with an index check, and its
  mutant CM01 is exactly the unsound direction. Keep CM01 as a required gate.

**F8 — NON_LOAD_BEARING. "Anchors at a ≠ 0 cannot form multi-cell blocks" (STRATEGY.md:72–76) is not established.**
- (i) **The cited cause is wrong.** The 4.7e10 majorant came from Strategy-A **whole-cell** errors inside the anchors
  (`R4_DESIGN.md:131–133`), not from anchoring away from 0.
- (ii) **A hybrid route was overlooked.** It keeps the exact-parity tower anchored at e = 0: T-EXT's own tower is valid
  on [0, η] ∋ a. Only R'''(a) comes from a new point run. Because R''''(a) ≠ 0, the transport is first order:
  `R'''(e) ≥ L_a − |e−a|·M4(η)`, with radius L_a/M4(η). The a = 0 radius √(2L/M5) does not apply.
- (iii) **Its reach is unknown.** The hybrid is multi-cell iff M4(η) ≲ L_a / cell width, i.e. roughly M5(η) ≲ 3e8 near
  η ≈ 0.01. That is not known before T-EXT. L_a itself may degrade at a ≠ 0 (see F9).
- **Repair.** Restate as UNFORECAST. The anchor counts in D1/C2 (§4, §7) are then estimates, not lower bounds.

**F9 — NON_LOAD_BEARING. A number and a mechanism in §8 are wrong. The FB-S conclusion survives a counter-route I
tried.**
- **The number.** STRATEGY.md:190 says residuals must be "10³× smaller near the graded boundary". Recomputed from the
  records, the needed factor w/|g| at cells 40–41 is 18–51× (m = 1: 18.8/17.6; m = 5: 50.9/47.9). 10³× is reached
  near cell 10.
- **The mechanism.** STRATEGY.md:183–184 says the width is set by "C_upper × residual". The K1 D half-width at cell 0
  (4.58, m = 1) is about 98% the cross term C²·k1·res0 = 1232.8 · 0.798 · 1232.8 · 3.70e-6 ≈ 4.49. Here res0 comes
  from the R half-width 4.56e-3 = C·res0.
- **The counter-route I tried.** The sealed slot-1 point run certifies R'(0) (m = 1) to ±0.0446 (`point_nodes` F:0:1,
  e = 0.0446). The GammaTilde/K1 path gives ±4.58 (`p5y_gammatilde_point_certificate/result/RUNG_256.json`). That is
  about 100× sharper. The mechanism:
  - the order-0 error is odd, and the odd block C_o0 = 5.36 carries it (F:0:0, o = 1.98e-5 = 5.36 × 3.70e-6);
  - that kills the cross term;
  - the gain needs parity-exact candidate residuals, which hold only at e = 0.
- **Why it fails.** In scalar_fallback (η ≥ 0.02338) every block entry reverts to C, so the gain vanishes and FB-S
  stands. Inside the graded zone at p ≠ 0, the even residual part returns. Using the recorded magnitudes, the R error
  is about ee·res0 ≈ 1.9e-3 at cell 20, against |g| ≈ 9.7e-4. So graded order-≤1 points are not a credible route
  either.
- **Repair.** Correct the number and the mechanism in §8.

**F10 — NON_LOAD_BEARING. Small numeric and reference errors.**
- OPEN_CELL_AUDIT.md:37 "width(D) ≈ 4.4–9.2": the recorded range over cells 1–148 is 3.74–9.08 for m = 1 and 3.49–16.9
  across m.
- OPEN_CELL_AUDIT.md:37 "dominated by e0·width(D)" is false at cell 1: w_R = 0.0091 > e0·w_D = 0.0069. It is true from
  about cell 5 on.
- STRATEGY.md:183 "C_upper (587–1233)": the scalar-zone cells 41–148 have 514–1026. 1233 belongs to cell 0.
- STRATEGY.md:73 cites "§A3 of the Phase A audit", which does not exist. It should be §3.
- STRATEGY.md:89 "leaves 105–123 cells per m open" should read 104–123.

**F11 — NON_LOAD_BEARING (pre-freeze condition). Governance hardening.**
- **No technical barrier to pre-freeze evaluation.** The host draft `text_transport.py evaluate` runs with no freeze
  record check and no ledger. T-EXT is cheap and deterministic, so an unrecorded exploratory evaluation would be easy
  and undetectable. That is exactly the class of risk the executor's guard exists for.
- **Mutation gate needs the real result.** The draft `text_mutants.py` calls `evaluate()` on the real sealed data, so
  that qualification gate can only complete **after** the result exists.
- **Required before freeze:**
  - a wrapper refusal of η > x1 unless the frozen preregistration hash is present;
  - a one-line evaluation ledger, with the output hash committed before interpretation;
  - a sign-blind qualification verdict, with a frozen VOID / no-rerun rule if a post-evaluation gate fails.

**F12 — NON_LOAD_BEARING. Tail (D3) details.**
- **K5-B-T is sound** (§2 item 7).
- **The executor reuse needs new code.** `point_core.point_cell` refuses any cell but CUSUM cell 0
  (`point_core.py:104–113`), so reuse needs a new containing-cell binding. "Additive binding + requalification" is
  right, but it is new code.
- **The consumer must check target_gate.** It must check it on cell 309 per m (PB6: margins 1.37–1.84). The E6 adapter
  does not (`consumption_adapter.py:127–151`).
- **Preregister the failure path.** A sub-cell failure must not trigger adaptive refinement.
- **The forecast holds.** At the worst sub-cell for s = 2, 2, 3, 3, the penalty / |g_centre| is 0.56, 0.69, 0.57 and
  0.71 (< 0.8). Cell 309 on [x_lo, 2] gives 0.085 against 0.227. That is 11 points.

**F13 — NON_LOAD_BEARING. T-EXT's relation to the frozen slot-1 consumption map.**
- **The map.** The slot-1 POSITIVE map fixes the closed cells "with L_1 := L1_m and L_k := −∞ otherwise"
  (`p5y_k5_cusum_first_real_probe_protocol/PROTOCOL.md` §10).
- **What T-EXT does.** It re-consumes the same sealed record for cells 1–40. The protocol allows this only as "the next
  ones … each under its own new preregistration". The sealed intermediates are also declared load-bearing
  (`EXECUTOR_SPEC.md:45–53`).
- **Repair.** The T-EXT preregistration should state explicitly that it does not amend the slot-1 result or its E6
  output. It is a successor consumption.

## 2. Answers to the review questions

**1. Derivative orders.**
- **Evenness transport:** correct. R odd gives R''' even, R'''' odd and R''''(0) = 0. The first-order Taylor expansion
  of R''' with an integral R⁽⁵⁾ remainder gives weight ∫₀ᵉ(e−t)dt = e²/2 (`r5_majorant.py:4–8`).
- **K5-B:** g' = −eR'' and s' = g/e² check out. The MVT for R'' with R''' ≥ L_k needs C³
  (`K5_GLOBAL_BRIDGE.md:38–46`).
- **Tail:** |g(e) − g(p_j)| ≤ r_j·sup_{sub-cell}|t R''(t)| ≤ r_j·y_j·M_R2(k) is correct, with y_j the right end of the
  sub-cell.
- **Ceilings:** e² < 2L0/M5 and e² < 10L0/M5, from g ≤ −L0e³/3 + M e⁵/30, are right. I recomputed them: cells ≤ 10/9/9/9
  and ≤ 23/22/22/21 for m = 1/2/3/5.

**2. Parity, and every place x1 or η enters.**
- σ(p,m) = (m,p) is an e-independent isometric involution fixing x0, so the value at x0 is the even part's value. This
  is valid for all e.
- At e = 0 the parity facts are exact and hull-independent. Each place η enters is valid on [0, η] when every argument
  is taken on [0, η] and x1 ≡ η (F6):
  - `local_anchor` drift (`local_r5.py:57–61`);
  - `graded_true_sup` wrong part η·T_{n+1} (`graded_dag.py:142`);
  - `apply_op` leak η·k_{i+1} (:122);
  - `resolvent_block` a = η²k2/2, b = ηk1 (:99–100);
  - hull norms `norm_table(0, η)`;
  - S0 `sup_S0_on(n, 0, η)`;
  - C.
- The resolvent perturbation is around A0 = I − K_0, with ‖P_xΔP_x‖ ≤ η²k2/2 because K_1(0) swaps parity, and
  ‖P_xΔP_y‖ ≤ ηk1. The certified 2×2 M-matrix test (d1, d2, det > 0) is the right criterion.
- R''''(0) = 0 needs R odd only.

**3. Certification domains.**
- **Slot-1 M5.** It is certified on [0, x1] only. Its sealed hull norms have eta = x1, and the anchor drift factor is x1.
- **The T-EXT inputs are valid on [0, η]:**
  - C = C_upper(0) = 1232.836 is the maximum over cells 0..40. C_upper is nonincreasing, and each per-cell C_upper is K1
    geometry covering its cell ("drift_monotone_resolvent", `build_spec.py:91–95`).
  - The e = 0 anchors do not depend on the hull.
- **Monotonicity.** The tower is monotone (F4). No mode flip or min() choice can produce a smaller output at a larger
  input, and soundness does not need it anyway.

**4. Point versus whole cell, and indexing.**
- `L0 − (x_hi²/2)·M5(x_hi)` is a valid inf over the closed cell [x_lo, x_hi]. The bound decreases in e, and x_hi is in
  the closed hull.
- K1 cell k is theorem cell C_{k+1}, and `k5b_literal` cells[i] is C_{i+1} (`k5b_check.py:155–157`).
- Reuse per m is correct: one tower, and `m5()` gives each m its own coefficients.
- Beware the off-by-one direction (F7).

**5. Post-result selection risk.**
- The consumption rule is fixed (40 hulls, smallest prefix), and each L_k is independently valid. No selection there.
- The residual risks:
  - (i) forgoing the dominating rule (F2) and the M2–M4 exports (F3) unless decided now;
  - (ii) no code guard against pre-freeze evaluation, and a post-evaluation mutation gate (F11);
  - (iii) T-EXT outputs will inform later designs of D1/C2. That is acceptable if they are disclosed as inputs of a new
    preregistration.
- For the tail, the partition is chosen from existing K1 midpoints, which is pre-result. A no-adaptive-refinement rule
  is needed (F12).

**6. Hidden smoothness.** C^∞ of R is certified (L5, reviewed). The tower's component-object regularity is a producer
premise and must be cited as such (F5). No numerical use of L5 occurs.

**7. Tail logic.**
- **K5-B-T is sound.** The parent M_R2 bounds |R''| on every sub-cell, and restricting to (0, 2] matches H3a.
- **Every K5-B pass certifies g < 0 on its own cell unconditionally.** γ_{k−1} and μ_k are valid bounds whatever
  happened to earlier cells (`K5_GLOBAL_BRIDGE.md:42–44`), and the direct Γ_k is local. So mixing passes with K5-B-T
  sub-cells is valid.
- **s(2) < 1 comes from target_gate.** It needs the cell-309 target_gate per m, which the consumer must enforce (F12).

**8. Phase A.** Confirmed with frozen code (operator constants only), with C = C_upper(0) = 1232.8358:

| cell | x_hi | mode | det | ee | eo = oe | oo |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 5.083e-4 | graded | 0.99953 | 469.99 | 1.02 | 5.36 |
| 33 | 0.018572 | graded | 0.36783 | 1232.84 (cap) | 101.4 | 13.4 |
| 40 | 0.022766 | graded | 0.05018 | 1232.84 | 911.4 | 94.2 |
| 41 | 0.023376 | scalar_fallback | −0.00144 | C | C | C |

- **Graded zone:** cells 1–40.
- **Pass/open sets:** equal to E6.
- **H.lo:** H.lo ≤ 0 on every cell for every m (0 exceptions), and M_R2 ≥ max|H| everywhere.
- **Diagnostic tables** (§5 of the audit): reproduced.

**9. Negative claims.**
- **GLOBAL_SHORTCUT = NONE:** agree. There is no certified sign of R'' anywhere, and the other ingredients carry no
  sign.
- **Front scalar zone infeasible with the qualified architecture:** agree. The only candidate I found (graded
  order-≤1 points) fails for a structural reason (F9). More points cannot shrink a K1-path enclosure that contains 0,
  and the precision ladder is stagnating.
- **Anchors at a ≠ 0 cannot form multi-cell blocks:** not established (F8).
- **Missed routes:** see §3.

**10. Governance classification.**
- **I agree that T-EXT needs no external countersigned authorization.** It performs no real-input arithmetic in the
  TRUST_MODEL sense: no `CusumPointBackend`, no K1 model solve, no scientific address of the executor kind. It
  consumes sealed intermediates that were declared load-bearing.
- **I disagree with "no authorization boundary."** T-EXT produces new certified scientific values that change the pass
  sets. It therefore needs a freeze commit, a code-level refusal before the freeze, a one-shot evaluation ledger, a
  sealed result hash before interpretation, a sign-blind qualification with a frozen failure rule, and independent
  adjudication (F11).

## 3. Missed routes

These are ranked by value per new real address.

1. **Piecewise-M5 transport** (F2). Zero addresses and strictly dominating. It must be chosen before the freeze.
2. **Seal M2/M3/M4 per hull** (F3). Zero addresses. It enables a K5-B successor with the floor H'_k.lo = max(H_k.lo,
   −M2(x_hi(k))) and M'_k = min(M_R2, M2) on cells ≤ 40, which is trivially valid. The gain is modest. It also enables
   hybrid anchors.
3. **Hybrid anchors at a ≠ 0** (F8). New point runs (a new executor mode, the same class as D1), each transported with
   the 0-anchored tower's M4(η). The block size is unforecast, and they need not be single-cell.
4. **Examined and rejected:** graded order-≤1 point runs at e0 ≠ 0 (F9). The parity gain exists only for parity-exact
   residuals at e = 0.

## 4. Conditions before the T-EXT freeze

These are required even though the verdict is PASS_WITH_NOTES.

1. Decide F2 (piecewise rule) and F3 (export M2–M4): adopt, or record the rejection.
2. Specify widened-η qualification that reaches the consumed η range (F1), or restrict consumption to the qualified
   range.
3. Rewrite the proof step (F4) and premise P1 (F5).
4. Enforce x1 ≡ eta in the wrapper, with required mutants (F6). Use distinct index symbols, with CM01 as a gate (F7).
5. Add the guard, ledger and sign-blind post-evaluation qualification rule (F11). State the successor-consumption
   relation to slot-1 (F13).
6. Correct §3 (F8), and the numbers and mechanism in §8 and the audit (F9, F10), before the blocker is reported to the
   user.
