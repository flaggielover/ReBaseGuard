# MB308 formal campaign: build report (builder, 2026-09-29)

**What this is.** This builds the machinery of the prospective, exactly-once campaign on cell 308 (route MB), items
B1 to B8, in the formal namespace `level4/closure_proofs/p5y_k5_cell308_mb_r1/` (NSF). The research namespace
`p5y_k5_cell308_research` is abbreviated NS.

**Status: nothing is frozen, qualified, reviewed or granted.**
* Nothing was staged or committed.
* No ref exists under `refs/p5y-k5-cell308-mb-r1/` in the real repository. The markers created by the flow tests
  live only in `git clone --shared` sandboxes under the session scratchpad.
* None of `authorization/`, `adjudication/`, `evidence/`, `qualification/` or `protocol/` exists. `protocol/` is
  created by the manifest writer only at the freeze.

**Cell 308 was never evaluated.**
* The execute mode was never run against the real repository.
* Nothing was run on any object of cells 305–309 or at any drift in [6/5, 13/5]: no Stage 1, no pointwise ladder,
  no TPT-B, no supply.
* No new-route value (TPT, C5-T, TPT-B, a supply, a margin) was computed for 305–309.

**The only historical computation** is the committed-record rehearsal of cell 305: controls C-A and C-B,
reproduction only, equality booleans only.
* It was run 4 times: directly, and as QC01 in three development qualifications.
* All 4 runs are ledgered as HISTORICAL_RECONSTRUCTION, agent `builder`.
* Record sha256 (scratchpad; incident review C7(a)):
  * direct: `9d994c2f893106ef55440808da45a2ba381415d0e1c298e34e1672e440da1b6c`
  * r3: `5b07d44b92c537500881633923546b9bdd61d95ed9799ea4a7a85ac7422b0e0a`
  * QDEV_final: `3a18f49efd995ec2628f398fb5d7a769ea7608bb4b5f92a53252866cbac379c3`
  * final2 (tripwires verified armed and firing): `ceefafe84c2b33d1cf884e29d12e9c344ec1f6aa0c7433cbaaed5c89d9192b73`

**What was implemented against.**
* `NS/streams/FORMAL/MB308_DESIGN_DRAFT.md` d0/d1 and THEOREM_MB r1.
* Coordinator notes 1–5:
  * stream F2 at `a7014669`;
  * stream F3 at `0292d654`;
  * REVIEW_A0_CERTIFIER_R1 C1–C6;
  * the incident review conditions C2, C7, C8 and C9, plus the QC13 citations;
  * the vd_pl C2b verifier at `58f190dc` and the C1b d ≥ 8 rule.

## 1. What is implemented (B1–B8)

| item | file | content |
|---|---|---|
| B1 | `code/mb308_guard.py` | **Formal guard**, DECOY by default. It refuses the band and its mirror, and the labels CUSUM m=5 305–309. It is bound as `ov_quarantine` (C1b, C2b, tpt.py), as `c308E_quarantine` (tptb_tail), as `vd_verify.Q` / `vd_pl.Q`, and as F3's `_guard` through an adapter. **Arming** (`arm_target`) requires three things: the marker `refs/p5y-k5-cell308-mb-r1/target-consumed` names the grant commit; that commit is HEAD; and the admitted set EQUALS the 37 pairs the guard derives itself from `CELL308` by D1/D2 (11 tiles E_i, 11 hulls B_i, 11 points b_i, and the cover with its 3 points). **`reproduction(cell, cover, e0)`** admits only the cover of 305 or 308 (for 308 the cover must equal `CELL308`), for a reproduction-only control. `log_execution` always refuses. |
| B2 | `code/mb308_pinned.py` | **Pinned loader.** Every external module is executed from bytes that pass a sha256 check and a HEAD blob check. There is no filesystem import and no .pyc; a `__pycache__` next to `c308_quarantine` is refused. The groups are: C1b (6); C2b + c7 (5); `rlr307_stage1` and `rlr307_independent`; `vd_verify` + `vd_adapt` + **`vd_pl`** (C2B_PL_HOOK, wired); `tptb_tail` + `frozen_path_loader` (the loader's six frozen files are executed here and handed to its cache); `decoy_gen` (decoy only); F2 `mb_independent`; F3 `tuple_independent`; and `c308_quarantine` r2 (executed by vd_verify and the loader at import). The loader also checks identities, and checks the guard's own sha256 at every binding (REVIEW_A0 C1). |
| — | `code/mb308_a0core.py` | **Side-effect-free extraction from stream A0**: `c2bx_rung`, `sub_certify`, `c1b_w_rung`, certificate serialisation, `compose`, and `pinned_recheck`. The sources are recorded by sha256, blob and line range (committed at `646e7e18` with exactly those blobs). The certificates are **byte-identical** to the persisted A0 certificates (QC06 C1, 5/5). |
| B3 | `code/mb308_stage1.py` | **Stage-1 jobs.** Geometry follows D1/D2. The RLR ladder (4, 6, 8) runs on B_i through the pinned `certify_rung`. The pointwise ladder at b_i is C2b N (20, 40, 80) and C1b d (8, 10, 12). **D5 as amended (section 4)**: C2b uppers are verified by `vd_pl.verify_pl` inside the C2B job; C1b uppers are verified by `vd_verify` only for d ≤ 6, and d ≥ 8 is NOT_INDEPENDENTLY_VERIFIED. Budgets are fixed operation counts, with outcomes VERIFIED, REFUTED or UNDECIDED. `pointwise` implements the admission rule. `rlr_block` implements Lemma Lad against `rlr307_independent`; `envelope` implements Lemma M-U. A guard refusal or an infrastructure error in a job is an execution failure. |
| B4 | `code/mb308_supply.py` | **Supply members.** S_I1, DvM_C1 and DvM_C2 (the frozen `atom_constants_r2` with Abar' = min(Abar, Ubar_i)), D14M (the pinned `assemble` with Abar' and Lemma DM D_lo'; the A0 slot is min(Abar'_eff, C_R)), and G. S_i is the componentwise min, with provenance. Non-block inputs to D14M are refused. **F2 is enforced**: the envelope, every member, S_i and Lemma Lad must be EXACTLY equal to F2's. F2's band guard is switched off only when the guard is ARMED. |
| B5 | `code/mb308_consumer.py` | **Consumer.** The committed TC-T inputs (ported from `rlr307_driver`; pins include `TCT_INPUTS_308`). **C-A** reproduces the committed record. **C-B** runs the reproduction gates at s = ρ: G-R1, G-R2, G-R3, **G-R3b** (F3), G-R4(M), G-CF, profile at ρ, and P_frozen. It runs inside `guard.reproduction`, with **tripwires verified armed and firing**, and outputs booleans only. **`stage2`**, the target entry, runs the same gates, then G-R4(N5), C5, exact tiling, the **C6** per-piece refusal, G-R3b on every block triple, `penalty_blocked`, G-T2 (the exact side only), P_B ≤ P_frozen(S_I1), and the F2 bracket (P_lo ≤ P_B, exact). Γ_dec = g_hi + max(P_B, P_hi). Tripwires keep every other route's function unreachable. |
| B6 | `code/mb308_driver.py` | **Driver**, with modes `preflight`, `rehearse --cell 305`, `decoy --cell 297\|316 [--first-blocks K] [--dev-ladder] --out F`, `execute` and `seal-only`. The exactly-once mechanics are copied from `rlr307_driver` and re-targeted to 308, with outcomes CELL308_CLOSED_UNDER_MB, CELL308_NOT_CLOSED_UNDER_MB and CELL308_EXECUTION_INDETERMINATE. Failure kinds are INDEPENDENT_CHECK_FAILED, INCONSISTENT, C6_REFUSED, TARGET_EVALUATION_FAILED and POST_MARKER_RECORDING_FAILED. Each Stage-1 job runs in a fresh spawned worker (`max_tasks_per_child=1`) with RLIMIT_CPU equal to the declared per-job cap; the driver refuses if the effective cap differs (REVIEW_A0 C3). **Decoy 297**: Stage 1 on real blocks; Stage 2 on decoy_gen bundles with 297's geometry (3 regimes, plus the r = 0 order-3-binding variant, plus a ×1000 supply variant in which the Stage-1 members bind). |
| — | `code/mb308_manifest.py` | Writes `protocol/MB308_FREEZE.json` at the freeze, and inside the sandboxes. |
| B7 | `tests/test_mb308_flows.py` | QC10: 41 exactly-once flows, plus the QC09 sandbox arming test. |
| B7 | `tests/test_mb308_twosided.py` | QC05: the composition against F2 and the literal definitions; 10 mutants; binding plants; refusals; Lemma Lad; the admission rule (11 cases). |
| B7 | `tests/test_mb308_guard.py` | QC09, in-process: every refusal, through every pinned code path. |
| B7 | `tests/test_mb308_tptb.py` | QC07, formal part: Stage 2 on decoy bundles; rise-then-fall cases with the endpoint-only mutant; C5, C6, reproduction and tiling plants; tripwires; the r = 0 order-3 regime; the G-R3b common-mode plant. |
| B7 | `tests/test_mb308_a0.py` | QC06: REVIEW_A0 C1 (byte identity); C6 (i) FD, (ii) err-path, (iii) swaps, (iv) vertex enclosure (using the reviewer's `r_eval.py` from pinned bytes); D5 verifier controls through the formal path. |
| B8 | `code/mb308_qualify.py`, `config/QUALIFICATION_CASES.json` | QC01–QC13 and Q8, gates Q1–Q12. Modes are official, `--review`, and `--dev --only … --work DIR --out FILE`. A dev report can never pass. A missing or non-boolean `pass` fails the run. QC12 reads the patterns at run time from the pinned `NS/ledger/TAIL_FIGURE_PATTERNS.json` (C8). QC13 and Q11 cite `NS/reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308.md` and check the condition files by path. |
| — | `errata/C2B_ERRATA.md` | REVIEW_A0 C5 (= REVIEW_C2B C4): the six claim corrections. |

## 2. The target path (what `execute` would do; never run)

1. **Pre-marker checks** (as in 307):
   * interpreter flags, identity, no prior evaluation, result paths;
   * a clean tree that includes ignored files (so `__pycache__` refuses);
   * the derived grant chain;
   * every pin, with F2 and F3 present and committed;
   * lineage (through `e042c8d1` and `0292d654`), r5/r6, seal preconditions, CPU caps.
2. `load_consumer`, then `load_science`. The order matters: research import guards installed at import are inert
   for exec-loaded modules.
3. **Controls on 308.** C-A, and C-B in `guard.reproduction(308)`, with tripwires verified. On failure:
   CONTROL_FAILED, sealed, not consumed.
4. **`prepare_target`.** The geometry is cross-checked against cells.json, REGISTRY_C2 and the guard. The 37
   admitted pairs must equal the guard's frozen set.
5. **Marker by CAS, then `after_marker`**, which runs these steps in order:
   * the parent arms the guard;
   * Stage 1 runs in a spawned pool: RLR jobs, C2B jobs (each with vd_pl verification), C1B jobs (d ≤ 6 would get
     VER jobs; the frozen degrees do not);
   * Lemma Lad, checked against rlr307_independent and F2;
   * the admission rule (INCONSISTENT raises);
   * the envelope and the supply (checked against F2);
   * Stage 2;
   * the decision.

   Every failure is sealed as CELL308_EXECUTION_INDETERMINATE.

## 3. What was run (builder session; the 6-core machine was shared and heavily loaded)

| run | where | result | wall |
|---|---|---|---|
| `rehearse --cell 305` (direct) | real repo, read-only; output in the scratchpad | C-A: 7/7 fields equal. C-B: every gate equal; tripwires armed | 5.6 s |
| `preflight` | real repo, read-only | PREFLIGHT PASS | 4.3 s |
| `decoy 297 --first-blocks 1 --dev-ladder`, C1b d = 8 variant (superseded) | decoy mode | Stopped after 82 CPU-min: VER of one C1b d = 8 certificate in `vd_verify` had not finished. This is consistent with VERIFIER_REPORT D7 and led to coordinator note 5. No output | — |
| `decoy 297 --first-blocks 1 --dev-ladder` (d4) | decoy mode, 2 workers | RLR d4 311.6 s (cap declared = effective 3600 s); C2b N20 62.9 s; C1b d4 13.1 s; VER d4 20.0 s. Stage 2 on 4 bundles: every gate passes; F2 EQUAL | 314.5 s |
| `decoy 297 --first-blocks 2 --dev-ladder` (d4) | decoy mode, 3 workers | Blocks 0–1 certified. Stage 2 on 5 bundles, including the ×1000 variant, where D14M binds on blocks 0–1 (non-constant triples): every gate passes; F2 EQUAL | 242.7 s |
| `decoy 297 --first-blocks 2 --dev-ladder` (**final code**, vd_pl) | decoy mode, 2 workers | Per block: RLR d4 ≈ 211 s; C2b N20 ≈ 39 s, including **vd_pl VERIFIED in ≈ 3 s**; C1b d4 7.3 s; VER d4 VERIFIED ≈ 9.6 s. Pointwise CERTIFIED, with **admitted rung C2B:N=20** (alarm partner: the C1b Lambda_lo). Stage 2 on 5 bundles: every gate passes; tripwires verified; F2 EQUAL | 271.0 s (533 CPU-s) |
| dev qualification **final2** (`--only QC01,QC05,QC06,QC07,QC09,QC10,QC11,QC12,QC13`) | scratchpad sandbox | **all 9 PASS** (details below) | 378 s |

Details of final2:
* **QC01**: C-A and C-B equal.
* **QC05**: 1980/1980 blocks exactly equal to F2; 10/10 mutants rejected; 5/5 binding plants; refusals; Lemma Lad
  150/150; admission rule 11/11.
* **QC06**:
  * C1 byte identity 5/5.
  * FD with a rough W: 0 exceedances over 6440 cells of every kind, 400 of them with s < 1.
  * FD with a smooth W: 0 exceedances; max FD/bound 0.9985; the ×0.5 control flagged 2048 times.
  * Err-path controls in both directions: vertex-acceptable, re-check FAIL, float interior violation found.
  * Both direction swaps FAIL.
  * Vertex enclosure: 3361/3361 nodes inside; the control lands 3361/3361 outside.
  * D5 verifier controls: 9/9. vd_pl VERIFIED the valid certificate and REFUTED the ×0.97 and claim-changed
    ones. vd_verify VERIFIED the d4 certificate and REFUTED or refused the plants.
* **QC07**:
  * Stream ASSEMBLY E4: 29/29.
  * Formal cases: 168/168.
  * Rise-then-fall endpoint-only mutants: 32/32 detected.
  * P_B × (1 − 2^-40): 168/168 detected.
  * Plants C5, C6 (with F2 refusing the same input), reproduction and tiling: all caught.
  * Tripwires: correct.
  * r = 0 order-3 cases: 8/8.
  * G-R3b common-mode plant: caught by G-R3b only.
* **QC09**:
  * Every refusal holds through every pinned path.
  * Arming works with the exact set.
  * Arming is refused without the marker, with one pair dropped, with an extra band pair, and with a marker that
    does not name the grant.
* **QC10**: 41/41 flows.
* **QC11**: every static check passes, including the C2 check: no reference to the research reconstructions.
* **QC12**: 0 tail-pattern hits in 17 files; 70 patterns loaded at run time; the planted control fires. The
  record-token scan runs in official mode only.
* **QC13**:
  * The ledger lines are pre-grant classes only.
  * The incident review's verdict line and condition files check out.
  * "Committed before the freeze" is necessarily false here, because no freeze exists.

**Not run, as instructed:** the heavy cases QC02 (full decoy 297), QC03 (316, 3 blocks), QC04 (determinism,
including REVIEW_A0 C4 at drifts 3 and 11/10) and QC08 (Monte Carlo). All four are implemented.

**Record sha256 (scratchpad; incident review C7(b)).**

| record | sha256 |
|---|---|
| decoy b1_d4 | `26c636f08c0b0442e19200f71d1826eefde5f598139abaaaca08e1b3779edf07` |
| decoy b2_d4 | `43d14a9501afc152e4eac74f90c875310957664ddd1d429c98ecfdc602b2834f` |
| decoy b2_final | `c25e0c87d8fa726e1e6517e9a0043ea92f948519a140a9c1fbeb4ba179bbfcd8` |
| QDEV_final2 report | `8864c0c85000d3616341cacdcfd8f465453d67ac32feffc1133169aedbda21a0` |

The decoy outputs are latent proxies. Only runtime and status may enter the EVAL_CAP rule.

## 4. Builder decisions and amendments (each needs review before a freeze)

1. **Admission rule (D5 as amended by REVIEW_A0 C2 and coordinator notes 3 and 5).**
   * An upper rung is admitted only if it is VERIFIED and a certified lower rung of the other implementation has
     L_other ≤ U.
   * REFUTED, or L_other > U for **any** certified upper rung (verified or not), gives INCONSISTENT. The "or not" is
     the builder's stricter-only reading. After the marker, INCONSISTENT means INDETERMINATE.
   * No other-implementation lower rung gives ALARM_UNAVAILABLE. UNDECIDED means the rung is not admitted.
   * **C1b uppers with d > 6 are NOT_INDEPENDENTLY_VERIFIED and are never admitted.** So in the frozen ladder, U_i
     comes from C2b rungs only, policed by the C1b Lambda_lo. The alarm sensitivity U − L_other is recorded.
2. **Verification budgets** (operation counts, never wall clock), in `VERIFY_BUDGET`:
   * C2b PL (`vd_pl`): `max_depth` 12, `max_boxes` 10^6 per column job;
   * C1b strip (`vd_verify`): `max_boxes` 200000 per initial box, `min_width` 2^-40.

   These are the verifiers' own defaults, frozen here. They are **OPEN for review**: stream VERIFY may declare
   others.
3. **Kernel e equals cover e** (identity map). b_i ≥ 0, and the envelope runs over increasing b_i. Justified by
   evenness (THEOREM_MB N6).
4. **Arming by the rule-derived set instead of a hash-bound AUTHORIZATION.json** (the A0_C5 design).
   * The admitted set is a pure function of the guard's pinned bytes.
   * The guard's sha256 is in `HELPER_SHA256`; the grant binds the driver's sha256; every guard binding checks the
     guard's sha256.
   * No per-drift multiplicity counters exist. Exactly-once is carried by the marker.
   * REVIEW_A0 C1 asks for the design; the review must accept this equivalence or require the file.
5. **Tripwires are in-memory stubs.** Pinned bytes are unchanged and the originals are restored. They are verified
   armed and firing before any control or Stage 2 proceeds (C7(a)). QC11 checks the same property statically.
6. **In-memory re-pointing of research guards.** Pinned bytes are unchanged and identities are checked.
   * `vd_verify.Q`, `vd_pl.Q` and `c308E_quarantine` are re-pointed.
   * F3's `_guard` is re-pointed to a formal adapter; the original is kept as `_research_guard`.
   * The frozen-path loader's cache is primed.
7. **Exact comparisons only (D12).** G-T2 gates only P_lo ≤ P_B. The loose upper side is informational. The
   decision uses max(P_B, P_hi).
8. **G-R3b is mandatory.** Checked on the cell tuple, rad(S), W and the whole cell at ρ, and on the rad and lo/hi
   polynomials of every block triple.
   * In a control: a failure means CONTROL_FAILED.
   * In Stage 2: a failure means INDEPENDENT_CHECK_FAILED.
9. **CPU caps (REVIEW_A0 C3).** Each job gets a per-job RLIMIT_CPU equal to its declared cap in a fresh worker; the
   job refuses if the effective cap differs. A cap hit is an execution failure. The values are provisional (OPEN).
10. **A guard refusal inside a job is an execution failure.** A refused admitted object must never silently weaken
    a member.
11. **Decoy Stage 2.** The decoy supply plays S_I1, and members (3)/(4) come from Stage 1. The variants are the
    r = 0 order-3-binding bundle and the ×1000 supply bundle.
12. **Dev-only flags.** `--dev-ladder` (RLR 4, C2b 20, C1b 4) and `--first-blocks` are refused outside decoy mode.
    The qualification's `--dev` mode requires `--work` outside the repository.

## 5. Findings

* **The C1b strip verification at d ≥ 8 is infeasible.** One d = 8 VER job ran more than 82 CPU-min and did not
  finish. This matches VERIFIER_REPORT D7 and is now built into the rule (C1b uppers are never admitted).
* **The C2b PL verification is cheap.** It takes about 3 s at N = 20 inside the job. VERIFY quotes 14 s at N = 40
  and 100–170 s at N = 80.
* **The RLR block rungs dominate Stage-1 cost.** At d = 4 a rung takes 210–310 s under load; the 307 figures for
  d = 6 and 8 were 1326 s and 2311 s.
* **The byte-identity re-validation of the extracted A0 core passes** (REVIEW_A0 C1).
* **Composition, TPT-B, G-R3b, C6 and tripwires behave as specified** on synthetic and decoy data. No unexpected
  behaviour was found.

## 6. Open items (must be closed before a freeze)

1. **Protocol.** No `protocol/MB308_PROTOCOL.md` has been written; converting the design into a protocol is the
   coordinator's step. `theory/` is not populated either: Q1 checks the research THEOREM_MB. A decision is needed on
   whether to copy it into NSF.
2. **EVAL_CAP and `RUNG_CPU_CAP_S`.** They are provisional (12 h; per-job caps) and must be set from the QC02/QC03
   decoy costs by the 307 rule, using runtime and status only (C7(b)). The rule must include C2b verification for
   N ∈ {20, 40, 80} at every b_i (note 5), and 11 blocks × RLR (4, 6, 8). The qualify module does not yet compute
   the EVAL_CAP projection (the 307 Q12 did).
3. **Heavy qualification not run.** QC02, QC03, QC04 and QC08 are implemented but were not run. QC04 includes the
   REVIEW_A0 C4 determinism pair on the frozen driver at drifts 3 and 11/10; its non-dyadic drift runs C2b only,
   because the formal b_i are dyadic.
4. **Freeze-time re-pinning.**
   * `HELPER_SHA256` must be re-pinned after the last edit. My scratchpad utility `pin_helpers.py` did this during
     development.
   * The research-side pins are current as of research HEAD `29415a5d`: `c308_quarantine` r2, `vd_verify`, `vd_pl`,
     F2, F3, the E4 controls, and `TAIL_FIGURE_PATTERNS.json`. Any later research edit refuses fail-closed.
   * Also needed: `QUALIFIED_WORKTREE` `/Users/suzhe/ReBaseGuard-c308mb`, branch `p5y-k5-cell308-mb-r1` (design §1),
     and the lineage.
5. **A0 certificates are untracked.** The certificates used by the QC06 byte identity (`NS/streams/A0/certs/*`) are
   untracked in git (A0 review N8). The files are checked against `CERTS_MANIFEST.json` at run time, but the freeze
   must store them content-addressed or pin their sha256.
6. **Incident-review conditions.**
   * C4, the user's CLOSURE_ONLY ruling, is checked at the grant and is not implemented here.
   * C7(a): the rehearsal records exist in the scratchpad only (sha256 above). The coordinator decides whether to
     commit them.
7. **Unimplemented research-side cases.** "Stream A0 C3 controls" and "VERIFY D4/D6 controls" are not re-run
   verbatim. QC06's D5 controls cover the same classes through the formal path.
8. **Decoy selection.** A decoy member binds only in the ×1000 variant, because decoy_gen supplies are small. QC02
   could be made stronger by declaring more scaled variants.
9. **Formal ledger.** None exists in NSF. As in 307, the qualification carries its ledger entries in its report.
   Builder lines went to the NS ledger through `log_event`.

## 8. Freeze prep (coordinator note 6; edits made after the build commit `55d3719c`)

**Edits.** Nothing was executed on 305–309 apart from the committed-305 reproduction (QC01, twice more; ledgered).
1. **Caps (protocol §3.2).**
   * `EVAL_CAP_S = 8 * 3600`.
   * `RUNG_CPU_CAP_S` in seconds:

     | kind | per-rung caps |
     |---|---|
     | RLR | d4 1800, d6 4200, d8 8700 |
     | C2B | N20 1800, N40 1800, N80 2700 |
     | C1B | d8, d10, d12: 1800 |
     | VER | every rung 1800 (unused in the frozen ladder) |

   * `PRE_CAP_S` stays 1800 and `WORKERS` stays 5.
   * One addition: `C1B` d4 = 1800 s is kept. It serves only the decoy development ladder (`--dev-ladder`) and is
     unused by the frozen ladder.
2. **Q12 (`q12_caps` in `mb308_qualify`).** It re-derives the §3.2 projection from the OFFICIAL QC02 (297, all
   blocks) and QC03 (316, blocks 0–2) runtimes. The job set is 11 blocks × 9 frozen jobs = 99 jobs, scheduled
   longest-first on 5 workers.
   * It requires EVAL_CAP_S ≥ ⌈1.5 × projection⌉.
   * It requires every per-job cap ≥ 2 × the official maximum wall of its kind and rung.
   * It requires every job CERTIFIED (C2b VERIFIED and admitted), with no alarm, refutation or ALARM_UNAVAILABLE.
   * A missing job kind fails loudly. Every number is recorded, runtime and status only.
   * Gate Q12 = QC10 ∧ QC11 ∧ Q12_caps.
   * Checks: the scheduler reproduces the protocol's figures exactly (99 jobs, 65 502.8 job-s, makespan 13 110.8 s).
     A plumbing run on the timing-only record passed; its full outputs were not opened.
   * **Remark for §3.2.** In this build's records the C2B job wall ALREADY includes the in-job vd_pl verification:
     `run_job` times the whole job. The protocol table's "+ verification" column therefore double-counts. That is
     conservative and harmless. Q12 keeps the same convention: job wall + recorded verification seconds.
3. **Theory copy.**
   * `theory/THEOREM_MB.md` is byte-identical to the research THEOREM_MB r1 blob at `bfa9ad3c`
     (sha256 `f1c767dc…0d25`, blob `2ee1a41b…`).
   * Case `Q1_theory` checks the NSF copy's sha256 and blob against that pin, and the pin against `git rev-parse
     bfa9ad3c:<path>`. Gate Q1 = QC05 ∧ Q1_theory.
4. **Driver docstring fixed.** Stage 1 verifies C2b rungs with vd_pl in the job. C1b upper rungs with d > 6 are
   never admitted. C1b Lambda_lo is only the cross-implementation alarm. No other comment claimed C1b verification.
5. **Identity and lineage.**
   * Identity constants are as specified (they were already set).
   * LINEAGE now requires the research commits 33185113, bfa9ad3c, a7014669, 0292d654, e042c8d1, f42fef40, 8da57f89,
     58f190dc, 55d3719c, fc4eeeee and cc249872 (plus the 307-era anchors), each with a subject-word check.
   * All resolve as ancestors of HEAD.
6. **Q8 manifest.** It now lists, with sha256 and git blob:
   * EVERY namespace file (root files, protocol, theory, errata, evidence_prefreeze, config, code, tests), excluding
     the manifest itself and the post-freeze directories;
   * EVERY pinned external file (54: pinned modules, F2, F3, vd_pl, consumer inputs, MC, E4, the pattern file, the
     research theory, r_eval, and the 5 committed A0 certificates plus their manifest), each checked against its pin
     and its HEAD blob.

   Q8 in the qualification checks all of these, plus no unlisted or absent file, and requires the five named files
   to be listed. `FROZEN_DIRS` gains `evidence_prefreeze`. The flow sandbox now copies every NSF directory and the
   root files onto the checked-out namespace (`dirs_exist_ok`).
7. **Protocol not pinned.**
   * The protocol is not pinned in code. The manifest reads `protocol/MB308_PROTOCOL.md` at freeze time.
   * `HELPER_SHA256` was re-pinned after the last edit (driver sha256 below).
   * The C2 static check (QC11) now scans code (.py) only. The protocol's own sentence stating the history/recon
     prohibition had made the prose scan fire.

**Discrepancies for the coordinator.** I did not change these unilaterally.
* **Verdict line.** Protocol §10 step 3 says the qualification review's "line 3 exactly QUALIFICATION_ACCEPTED".
  The driver's `check_grant` (the 307 code) requires line 2 (`verdict_ok`: `lines[1]`). The QC13 incident-review
  check takes the first non-empty line after the title. One of the two texts must be aligned before the freeze.
* **§3.2 double count.** See item 2.

**Dev qualification after these edits** (`--dev --only QC01,QC05,QC06,QC07,QC09,QC10,QC11,QC12,QC13`, sandbox
under the scratchpad, 221.5 s):
* **All 10 PASS**: Q1_theory, QC01, QC05, QC06, QC07, QC09, QC10, QC11, QC12, QC13.
  * QC05: 1980/1980 exact.
  * QC06: C1 byte identity 5/5, including the committed-blob check; FD; controls; D5 9/9.
  * QC07: E4 29/29; rise-then-fall 32/32; formal 168/168.
  * QC10: 41/41.
  * QC12: 20 files, 70 patterns, 0 hits.
  * QC13: the incident review is committed before HEAD, and its condition files are present.
* Gates Q2, Q3, Q6, Q8 and Q12 stay false in dev mode by construction: heavy cases, manifest and Q12_caps are
  official-only.
* Report sha256: `e8957269c3c5ded6c83281a5c048ac550d9887feff2f31042c2b0b8f71d1ead7`.
* The QC01 records of the two runs: `712fdf10…641e` and `de7e9cd8…0bb6`.
* The read-only `preflight` passes on the real repository.

## 7. Files (sha256 of the bytes after freeze prep; this report excluded)

| file | sha256 |
|---|---|
| `code/mb308_a0core.py` | `0873604379bb5008f385ed09c7ae2f0694a402a91881b6a9d2e45649af332de6` |
| `code/mb308_consumer.py` | `c233bdb6235cd8a44bcf187be7d6686a4684f8619bed21ade9130432c5c09188` |
| `code/mb308_driver.py` | `965a2a306dd564b16614fc0bc22583e663e5bfa99464dc7afbe2bc408ac265f9` |
| `code/mb308_guard.py` | `882ce3fb86f4089081104e0fdbaf31c01b16e9a80065acd4e911f3010e6e06b1` |
| `code/mb308_manifest.py` | `fe80033d32df890b6dff187cf5ab876b46ad779e6c8eece60c138b0793b11170` |
| `code/mb308_pinned.py` | `5c221a0e70a708c580f13e1cd622556930f047f3c0b302227a8d9b18c52220a2` |
| `code/mb308_qualify.py` | `ca221cf080a0d4343971903aeea8c069ec871795d6424bf1b2558ad407c96a94` |
| `code/mb308_stage1.py` | `23296f837eb7520b36c32bba08d238d940c14a8753e8ce8cadb05f0990f2ec98` |
| `code/mb308_supply.py` | `af1a818b68459ada53773557e10153ae4ae3edc232d52e93fd19814e4da59b58` |
| `config/QUALIFICATION_CASES.json` | `2283989bdc61acfb34f3136503614db2dbc6d4ce18c450b870198f10bdd6ba5f` |
| `errata/C2B_ERRATA.md` | `91bc3e4867479d28d6dab080db59bc30767b26c888af466727137a29285185b3` |
| `evidence_prefreeze/DECOY_TIMING_PREFREEZE.json` | `0d6ded7f571753e91a11d09e3e778198b5ba3742bf6dd84e7c0fc0676e209f3f` |
| `protocol/MB308_PROTOCOL.md` | `87e75fa7396d1d9149d5d245d344c5eed8a52c3421720626dcb10bd5ec892cf8` |
| `tests/test_mb308_a0.py` | `be7ca5a7f3e73432ee1d7dd7c2a597c6bc41ef09557643234c3a7b4c1c5b98eb` |
| `tests/test_mb308_flows.py` | `5a5c70c12754ff0ea4cdca20429661e0f16827ee8b6e926e741f55b8373cbd6a` |
| `tests/test_mb308_guard.py` | `a64ac7865ec2af48eb18531b48aacac19bf0329d7d31e5ea9b0e390a588fd52f` |
| `tests/test_mb308_tptb.py` | `44ea60ac0e28222c365a78fd6c8a92b7f8f72ab2ebc0e70619dcde05e07faec9` |
| `tests/test_mb308_twosided.py` | `e71b12fa7c29261ad0b4ad561c24133a54cc60464d0fc0ca68ca56d055afc8d8` |
| `theory/THEOREM_MB.md` | `f1c767dccc0bb3738fcae350530d4dda13c8b9db482ffb25528376502f4d0d25` |
