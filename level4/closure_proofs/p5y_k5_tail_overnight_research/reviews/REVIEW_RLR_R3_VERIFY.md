# REVIEW_RLR_R3_VERIFY — independent adversarial verification of RLR R2 repairs (C1–C5)

Verifier: independent agent (wrote none of the reviewed code). Date 2026-09-28. Time box 45 min.
Scope: repairs responding to reviews/REVIEW_RLR_R2.md §5 (C1–C5). Quarantine: preamble Q1–Q8, S1–S8, amendments 1–4 obeyed; no 305–309 quantity computed; validation-drift values not quoted.

## 0. Status
COMPLETE within the time box (started 09:15 JST, finished ~09:37 JST). Everything listed as run below was run;
NOT RUN: nothing in the priority list; out of scope and not rerun: the 27-job evidence regeneration (verified by
hashes and stored-field recomputation instead), negctl, MC, PLAIN rungs.

## 1. D13 coverage rule (priority 1) — SOUND (no reachable point excluded)

**Derivation (independent).** Frozen CUSUM (c1b_kernel.py:3–8, 31–33): K = 1/2, H = 5, x′ = ((p+z−K)⁺, (m−z−K)⁺), alarm iff
p+z−K > 5 or m−z−K > 5. If both arms of x′ are positive then p′+m′ = (p+z−K)+(m−z−K) = p+m−1 exactly. Every non-alarmed
state has p, m ≤ 5. Hence, from a state with one arm 0 (axis, p+m ≤ 5): a both-positive successor has p′+m′ ≤ 4; from a
both-positive state with p+m ≤ 4: a both-positive successor has p′+m′ ≤ 3; an axis successor has its coordinate ≤ 5.
So R = {0 ≤ p,m ≤ 5 : p = 0 or m = 0 or p+m ≤ 4} is closed under the killed chain and contains the atom (one step from
(0,0) cannot make both arms positive: z > 1/2 and z < −1/2). The bound 4 is attained: (5,0) → (2,2) with z = −5/2.
Points with p > 0, m > 0, p+m > 4 are unreachable; points with one arm 0 and p+m ∈ (4,5] ARE reachable.

**What D13 excludes (c1b_pw.py:114–120).** Only the J = 5 form (x-region t = p+m ∈ [4,5]) on 2-D boxes (rp > 0 and rm > 0).
* 2-D boxes are the base squares of `base_cover` (c1b_kernel.py:383–396: side 1/4, lower-left sum < 4, so every
  coordinate ≤ 4) and their `split_box` children (which stay inside their parent). A 2-D box therefore contains no axis
  point with p+m > 4; its only points with p+m > 4 are both-positive, i.e. outside R.
* Ownership: `region_of_point` is ceil(t) (right-closed), so the attainable boundary p+m = 4 is owned by J = 4, which
  is still checked on 2-D boxes. Axis points with t ∈ (4,5] are owned by J = 5 and lie in the 1-D axis boxes
  (c1b_kernel.py:392–395, both axes, [4,5] fully covered), where J = 5 (and J = 4) is still checked; 1-D boxes split
  into 1-D boxes.
* The squares cover the closed triangle (for p,m with p+m ≤ 4 take i = ⌈p/h⌉−1 or 0, same for j: (i+j)h < p+m ≤ 4).
Conclusion: D13 removes checks only at unreachable points. The pass decisions are rigorous-bound based (certpw.py:133
`r["lo"] >= 0`, quad_check certpw.py:160–163); the D13 `own`/`in_R` test (certpw.py:166, pw.py:144) only gates the
"pointwise violation" witness label, which is reporting, and a flagged box still fails the check.

**Independent check (SCR/review_RLR3/rv3_reach.py, exact rationals, drift-free, class SYNTHETIC_VALIDATION).**
Random + adversarial exact walks from the atom (push to p = 5 exactly, then into the both-positive window): 2505
distinct states, all in `in_R`; max p+m over both-positive states equals 4 exactly (bound attained, not exceeded);
1500 sampled reachable states all covered by a base-cover box whose `regions_of_box` contains the owning region
(0 uncovered). Negative controls: mutant rule that also drops J = 4 on 2-D boxes → 603/1500 uncovered (detected);
mutant CUSUM with K = 1/4 → both-positive states with p+m > 4 reached, 366 states outside R (detected).

**Declaration / consistency.** D13 was declared in PROGRESS.md:205–208 before the code change (PROGRESS.md:235) and pin;
it is stated in C1B_ROUTE_SUMMARY.md:43 (R) and :124–128; checker (`regions_of_box`, used by `enclose_t` and
`quad_check`) and certificate statements (S1/S2 "on R", summary:48–49) use the same R. The rule also explains the old
e = 3, d = 6 (i′) failures (flagged centres had p+m > 4 off the axes).
Note N1 (scope, pre-existing, not introduced by D13): all certified sup-norm constants are sup over R, i.e. norms of
the chain restricted to the closed set R ∋ a; any consumer must use that restricted norm (THEOREM_LR.md:9 leaves X
abstract). D13 verdict: **PASS — no soundness blocker.**
Evidence cross-check: the pre-pin e = 3 PW9 rung (logs/prepin/C1B_PW9_POINT_e3.json) records 10 failure samples, all
flagged "pointwise", all in region J = 5, 0/10 centres in R — the diagnosis at PROGRESS.md:195–199 is correct. The
regenerated rung C1B_R2_PW_POINT_e3_d6.json has 6/6 (i′) "passed" flags true. Temporal note: D13's declaration and the
code change arrive in the same commit (3d13c138), so "declared before the change" rests on PROGRESS ordering only.
(Latent fragility, not active: base_cover assumes 1/h integer; every caller uses the default h = 1/4.)

## 4. C4 provenance — MET (with notes)

`SCR/review_RLR3/rv3_prov.py` (HISTORICAL_READ) hashes the HEAD blobs (`git show HEAD:…`, HEAD = 3d13c138; LR code,
LR docs and config are identical to HEAD in the working tree) and compares them with every `validation/C1B_R2_*.json`.
* `C1B_R2_CODE_PINS.json` (revision 2): 12/12 pins equal the HEAD blobs.
* 30 output JSONs: 29 carry `provenance.code_sha256` (12 files each); the 5 load-bearing modules (gauss, kernel, pw,
  certpw, certify) match HEAD in 29/29. The only mismatch anywhere is `c1b_report.py` in outputs written before pin
  revision 2 — the declared aggregator-only fix (PROGRESS.md "[PIN r2]"); SUMMARY.json (written after) matches fully.
* Flags: TIGHT_CT and BLOCK_LIGHT recorded in every PW point/block, NEGCTL, BLOCKCTL(_DISC), TEST_COMBINED output;
  PLAIN and MC outputs record `{}`, which is accurate (c1b_certify.py / c1b_mc.py do not read either flag).
* `C1B_R2_BLOCKCTL_DISC.json` (r2_blockctl_disc.py, outside the pinned set) records `own_sha256` = HEAD blob.
Notes: N2 — `C1B_R2_PREPIN_COMPARISON.json` has no provenance block (comparison only, not certifying). N3 — at HEAD
the 12 pre-pin `validation/C1B_*.json` files (incl. the old e = 3 PW9 rung with the retracted "pointwise" failures) are
still present at their canonical paths; the working tree has them moved to `logs/prepin/`, but the deletions are not
committed (`git status`: ` D`). Report globs are R2-prefixed (c1b_report.py:38,138) so they are not ingested, but stale
evidence is left live at HEAD until the move is committed. N4 — PROGRESS.md bracketed times are not wall-clock
(e.g. "[09:20] D17c" while `C1B_R2_BLOCKCTL_DISC.json` mtime is 09:13:31 JST and this review started 09:15 JST);
ordering is consistent with file mtimes, but the stamps should not be cited as times.

## 2. C2 combined supply — MET (test is one-sided: note)

**Code.** `c1b_certpw.assemble` (c1b_certpw.py:303–341) computes c1 = min(q1, A_eff·κ1C_T), c2 = min(q2, A_eff·ρ2^Dv′)
(q_j already the RLR ratio/non-ratio min), the quotient-rule assembly A1_c, A2_c with the minimised c1 in the A2 cross
term, then SUPPLY_j = min(·, G_j) with G = (C_R, κ1C_R², κ2C_R² + 2κ1²C_R³) — exactly THEOREM_LR LR-4 (THEOREM_LR.md:168–173)
and the ρ-level min endorsed in REVIEW_RLR_R2 §1.3 / THEOREM_LR.md:241. It is on the load-bearing path: every PW
record is built through it (c1b_certpw.py:299, :380) and the aggregator re-derives it (c1b_report.py:54).

**Run (SCR/review_RLR3/rv3_c2.py; imports the test module and calls `run_test`, not `main`, so nothing under NS is
written).** assemble: PASS (16 real certified PW records, 3 plants, 2000 random sets, 0 failures). Author mutants:
`mutant_no_min` CAUGHT (all 3 plants fail, 379 random failures), `mutant_no_G` CAUGHT (2 plants, 153 random).
Independent exact recomputation of D14 (PROGRESS.md:209–217) equals `assemble` on 2019/2019 input sets (real + planted +
random). On the 16 real records SUPPLY equals raw RLR exactly (16/16; consistent with C1B_ROUTE_SUMMARY.md:157).
Stored evidence: the exact A0/A1/A2_SUPPLY fields in the 16 certified C1B_R2_PW_* records (15 point + 1 block) equal
`assemble` recomputed from their stored exact inputs, 16/16 (SCR/review_RLR3/rv3_stored.py).

**Adversarial finding (note N5, not a blocker).** The test only asserts SUPPLY ≤ min(RLR, Dv′, G) and SUPPLY > 0
(c1b_test_combined.py:44–49). Two UNSOUND mutants I planted — SUPPLY halved, and Lemma G with the cubic term dropped —
both PASS the author's test (0 failures). The test therefore guards "never worse than Dv′/G" but cannot detect an
under-reported (invalid) supply. The shipped code is correct (exact D14 equality above), so C2 as worded is met, but the
test should additionally assert exact equality with its own D14 formula (or the lower side) before any freeze.
Note N6: `c1b_certify.assemble` (c1b_certify.py:292–310, PLAIN baseline path, listed load-bearing in c1b_prov.py)
is a second assembly without SUPPLY; PLAIN records carry raw RLR only and must never be the consumed output
(C1B_ROUTE_SUMMARY.md:284 says the consumed output is SUPPLY; make the PLAIN exclusion explicit).

## 5. C1 claims and C5 governance — MET (minor wording note)

**C1.** Scan of THEOREM_LR.md, C1LR_ROUTE_SUMMARY.md, cusum/C1B_ROUTE_SUMMARY.md and both PROGRESS files for
dominat / never worse / beats / provably / ≤ Dv′: no remaining unqualified "RLR never worse than Dv′" claim.
THEOREM_LR.md:223–227 (heading + correction), :246 (certified-ρ caveat), :424 ("empirical … not a consequence of LR-3");
C1LR_ROUTE_SUMMARY.md:28 and :47–48 and :125 all state: dominance is a theorem for exact ρ only; with certified ρ only
min(RLR, Dv′, G) is guaranteed. C1B_ROUTE_SUMMARY.md:70, :153, :327 attach the guarantee to SUPPLY only. The old
LR/PROGRESS.md:19, :28 plan/log lines remain as history and are explicitly corrected at LR/PROGRESS.md:98–101
(acceptable: preserved log with a correction entry). Old C1B :91 ((i′) ladder) is corrected at C1B:142–151 and old
:269 (null sets) at C1B:110–121 (piece-B images carry mass on strip lines; correctness rests on the right-closed
ownership convention — I re-derived the J ↔ strip correspondence for BW = (0,1,2,3,5) and agree).
Note N7 (wording): C1B:119 "Every box is checked with every region form it meets" is no longer literally true after
D13 (2-D boxes skip J = 5); the D13 paragraph at C1B:124–128 qualifies it, but :119 should say "every form it meets
that owns a point of R in it".

**C5.** config/QUARANTINE_AMENDMENT_4.json (stricter-only) lists streams/C_308/LR/cusum/C1B_ROUTE_SUMMARY.md, restates
the cusum logs and validation/C1B_*.json, and adds the C2B summary/tightness files and validation/C2B_VALIDATION.json.
Its line pointers ("near line 60", "near lines 97–112") refer to the pre-revision layout; the R2 revision moved all
values into Appendix V (C1B:312 onward, producer r2_tables.py), so the file-level listing still covers them.
C1B_ROUTE_SUMMARY.md carries a latent-proxy banner. CLOSURE-ONLY under floor r2 remains stated. MET.

## 3. C3 block-path controls — MET

**Design read (c1b_blockctl.py, r2_blockctl_disc.py; block [1/2, 17/32] declared in D12/D15, outside the quarantined band,
`Q.guard_drift` called).** B0 positive (certified block w_T and L1 (i′) certificate accepted); B1 w′ = (1−ε)w_T through
`check_supersolution` (exact residual′(atom, e*) < 0 asserted, :73); B2 interior-drift-only residual plant
residual − c·ψ(e)·(k_a+h1), ψ = 0 at both ends and 1 at e_c (asserted exactly, :79), exact witness asserted (:86),
accepted by the point enclosures at both ends and rejected by the block enclosure (e-direction isolated); B3 (i′)
C-conjunct (precondition C(atom) > 0 asserted, :110; witness :114); B4 discriminant at its witness (:138). N1′/N4
preconditions of REVIEW_RLR_R2's notes are now asserted (c1b_negctl.py:144, :175). Note N8: B2 is a residual-level
plant pushed through `cx.enc` (the enclosure `check_supersolution` uses), not an e-dependent w pushed through the
kernel; this is appropriate because D12 fixes an e-free candidate family, but it tests enclosure e-uniformity, not
kernel handling of e-dependent candidates.

**Committed evidence (validation/C1B_R2_BLOCKCTL.json, flags/counts only):** B0 wT_certified and L1_quad_passed true;
B1 witness_valid + rejected; B2 witness_valid, accepted by both end-point checks, rejected by the block checker;
B3 witness_valid + rejected (832 flagged centres); B4 witness_valid + rejected (2413 flagged centres — i.e. B4 alone
does not isolate the discriminant, as the author self-reported); all_block_controls true.

**D17c discriminant-only plant — algebra verified.** a′ = a + μw_T, b1′ = (1+λ)b1, b2, g0, g2 unchanged. From
`quad_check`'s definitions (c1b_certpw.py:147–149): A′ = A exactly; B′ = B + λ(b1 − K̂b1) (= `Dq`, r2_blockctl_disc.py
D17b block); C′ = C − λK^(1)b1 + μ(w_T − K̂w_T) (= `Cp`). The plant is accepted as PLANTED only inside the branch
`encCp["lo"] >= 0 and encA["lo"] > 0` — rigorous block enclosures over R × [1/2, 17/32] — so A′ > 0 and C′ ≥ 0 hold
globally (the literal `True` flags are gated by that branch); the witness is a base-cover centre with `in_R`, at
e* = 33/64 (interior), with rigorous point intervals: |B′| bounded away from 0, A_lo > 0, C′_lo ≥ 0 and
min B′² − 4·A_hi·C′_hi > 0. Hence the quadratic Aμ² + B′μ + C′ is negative at μ = −B′/2A at the witness: the
certificate is genuinely invalid, and the ONLY violated true conjunct is the discriminant. A sound box checker must
reject any box containing the witness in its owning region, so the rejection is forced by the discriminant.
Committed result: status PLANTED at λ = 1, rejected, 5/5 sampled failures carry `discriminant_violation` with A, C
centre values > 0; positive control (unmodified certificate) passes. D17 and D17b NOT_CONSTRUCTIBLE outcomes are
preserved in logs/ (S4-compliant, declared before running per PROGRESS.md:248, :270, :280).

**Independent rerun of the D17/D17b/D17c control (SCR/review_RLR3/rv3_disc_rerun.py = r2_blockctl_disc.py with only
the output path, the ledger path and the own-hash source path redirected to scratch; `nice python3 -B … --tight-ct
--block-light`, 421 s, class NONTARGET_DRIFT_VALIDATION, block [1/2, 17/32] only).** The output is identical to the
committed validation/C1B_R2_BLOCKCTL_DISC.json in every field except `seconds` and `provenance`; `matches_pins` true.
Reproduced: D17 NOT_CONSTRUCTIBLE, D17b NOT_CONSTRUCTIBLE, D17c PLANTED at λ = 1, global C′_lo ≥ 0 and A_lo > 0,
x* ∈ R, rejected by the pinned block `quad_check` (15648 failure records; 5/5 samples discriminant violations),
positive control passes. B0–B4 were also rerun (SCR/review_RLR3/rv3_blockctl_rerun.py = c1b_blockctl.py with output and ledger paths
redirected; 272 s): output identical to validation/C1B_R2_BLOCKCTL.json except `seconds`/`provenance`,
`matches_pins` true, all_block_controls true (B0 accepted; B1–B4 witness_valid and rejected; B2 accepted at both ends).
C3 verdict: planted-invalid supersolution, interior-drift-only, C-conjunct and discriminant-only certificates are
pushed through the block checkers with exact witnesses and all rejected; positive control accepted; block candidate
family declared (D12). **MET.**

## 6. Condition table, notes, quarantine statement

| condition | verdict | basis |
|---|---|---|
| D13 soundness (priority 1) | PASS — excludes only unreachable points | §1: derivation (both-positive ⇒ p+m ≤ 4, attained), cover geometry, exact walk check + 2 negative controls |
| C1 claims | MET | §5 |
| C2 combined supply | MET (note N5) | §2: code read, test run, author mutants caught, exact D14 equality 2019/2019 |
| C3 block controls | MET | §3: D17c algebra verified; B0–B4 and D17/D17b/D17c reruns identical to committed |
| C4 provenance | MET (notes N2–N4) | §4: 12/12 pins = HEAD; 29/29 outputs load-bearing hashes = HEAD; flags recorded |
| C5 governance | MET | §5: amendment 4 lists C1B summary; values confined to Appendix V |

Notes (none is a soundness blocker; N3 and N5 should be fixed before any freeze preparation):
N1 certified sup-norm constants are norms of the chain restricted to the closed set R ∋ a (pre-existing convention);
N2 PREPIN_COMPARISON has no provenance block; N3 12 pre-pin validation/C1B_*.json files are still live at HEAD (move
to logs/prepin/ not committed); N4 PROGRESS bracketed times are not wall-clock; N5 c1b_test_combined.py is one-sided —
unsound under-reporting mutants (halved supply; Lemma G without cubic term) pass it; add an exact-equality/lower-side
assertion; N6 PLAIN path (c1b_certify.assemble) has no SUPPLY — state that PLAIN records are never consumed;
N7 C1B:119 wording predates D13; N8 B2 is a residual-level plant (appropriate for the e-free family of D12).

Route state unchanged by this verification: VALIDATED_NON_TARGET, CLOSURE-ONLY under floor r2. This review does not
assess FREEZE_READY.

**Quarantine statement.** Drifts evaluated: none in §1/§2/§4 (drift-free exact rationals / hash reads); the declared
block [1/2, 17/32] (e* = 33/64) in the §3 reruns, via the route's own `Q.guard_drift`. No cell id, no 305–309 quantity,
no tail number read into code or placed next to any value; no validation-drift value is quoted here (flags, counts,
signs and state coordinates only). Imports: NS/code/ov_quarantine.py and this route's c1b_* modules under test only; no
historical module. `Q.LEDGER` redirected to SCR/review_RLR3/REVIEW_LEDGER.jsonl (NS ledger mtime predates this review).
No git writes (read-only `git status/log/show/ls-tree/diff` only); no remote hosts. Only file written under NS: this review.

## 7. Verdict

D13 excludes only unreachable states (both arms positive forces p+m ≤ 4; the only states with p+m > 4 are on the
axes, which remain checked with the J = 5 form on 1-D boxes), so there is no soundness blocker. C1–C5 are met.
Notes N1–N8 stand; N3 (stale pre-pin evidence at HEAD) and N5 (one-sided combined-supply test) should be
closed before any freeze preparation.

REPAIR_VERIFY: CONFIRMED_WITH_NOTES
