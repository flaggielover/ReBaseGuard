# Independent review of the cell-307 RLR adjudication (r1)
ADJUDICATION_ACCEPTED

## Reviewer statement
* I am a fresh, independent, read-only adjudication reviewer. I wrote, froze, qualified, reviewed, granted, ran, sealed
  and adjudicated nothing in this campaign. This file is the only file I wrote in the repository. I created no ref and
  no commit, and I modified, moved or deleted no repository file.
* I ran no driver command (no `execute`, no `seal-only`, not even `preflight`), no certifier and no consumer, on any
  cell. I recomputed nothing on cell 307. My only computation was exact `fractions.Fraction` comparison of strings
  already committed: the sealed blob (read from the object store), `RLR307_FREEZE.json` at the freeze, and C2's
  committed `C2_D5_FORECAST.json`. Scripts: `/private/tmp/rlr307_adjrev_c307/verify.py` (40/40 PASS) and
  `/private/tmp/rlr307_adjrev_c307/extra.py`, both run as `python3.14 -I -S -B`.
* Basis: worktree `/Users/suzhe/ReBaseGuard-c307`, branch `p5y-k5-cell307-rlr-r1`, HEAD = adjudication commit
  `126083216ecee764785a6c0516ec27c21d2650c6` (parent `e68f3d64`; it adds only `adjudication/RLR307_CELL307_ADJUDICATION.md`).
  Tree clean apart from this file. NS = `level4/closure_proofs/p5y_k5_cell307_rlr_r1`.

## Checks (campaign brief section 28)

**1. Frozen criterion applied verbatim: PASS.**
* `git show cd5016f1:NS/protocol/RLR307_PROTOCOL.md` §8: row 1 (TARGET_EVALUATED, Stage 1 CERTIFIED, independent checks
  equal, `pass` True, i.e. Γ(5, 307; S_RLR) < 0 in exact rationals) gives CELL307_CLOSED_UNDER_RLR; Γ ≥ 0 "including
  Γ = 0 exactly" gives NOT_CLOSED; CERTIFICATION_FAILED gives NOT_CLOSED (RLR_CERTIFICATION_FAILED); any post-marker
  failure gives CELL307_EXECUTION_INDETERMINATE; strictness, tolerance, rounding, margin, floor never change.
* The adjudication's quoted criterion and supply strings equal `RLR307_FREEZE.json` `stage2.closure_criterion` and
  `stage2.supply` at `cd5016f1` byte for byte (script). It states strict `<`, no tolerance, no rounding, no margin,
  Γ = 0 not closed, CERTIFICATION_FAILED → not closed, post-marker failure → indeterminate.
* Its line-2 token is exactly the §8 row-1 conclusion, and equals the frozen `outcome_table["TARGET_EVALUATED + pass
  True"]` looked up by my script from the record's `pass`.

**2. Correct target result used: PASS.**
* Blob of `NS/evidence/execution/RLR307_CELL307_RESULT.json` at seal `b26c64a7` = `04161112…` = blob object at
  `refs/p5y-k5-cell307-rlr-r1/pending-result` = HEAD blob = worktree `git hash-object` (and raw bytes equal in-script).
* Seal commit parent = grant `5390b06d`; it adds only the result path; no commit after the seal touches that path.
  `refs/p5y-k5-cell307-rlr-r1/target-consumed` → `5390b06d`. The self-hash `sha256` field verifies (driver `serialize`
  rule). The adjudication read the record at the seal (its table row 1): correct object.

**3. Correct sign (recomputed): PASS.**
* `target.stage2.evaluated.Gamma_exact` is `p/q` with q > 0 and p < 0; `Fraction(Γ) != 0` True; `Fraction(Γ) < 0`
  True. Recorded `pass` is True and equals (Γ < 0).
* The adjudication's sign derivation reproduces: numerator prefix, sha256 `5bb5d5ca…` of the exact string, and its
  exact bracket all check. `status` TARGET_EVALUATED; top-level and `target.decision` `mechanical_outcome` both equal
  the frozen-table output.
* Supporting layers (all exact): Stage 1 cell CERTIFIED, 10/10 blocks CERTIFIED with certified degrees (4, 6, 8),
  30 rungs (30 distinct (block, degree) keys, all `RUNG_RETURNED`, all CERTIFIED), `independent_checks` = {all_equal:
  true, rungs: 30}; `A{0,1,2}_SUPPLY_max` = max over blocks; target A0 string = control A0 string; target A1, A2 =
  min(control, cell max); provenance (I1, RLR, RLR) and supply string equal the frozen rule; `blocks_planned` = the
  Stage-1 hulls.
* Control: `C2_D5_FORECAST.json` sha256 = record pin `784f25ee…`; its cell-307 `A_exact`, `Gamma_exact`, `H_exact`,
  `M_after_exact`, `pass` (False) and `provenance` equal the control's; `field_matches` 7/7; adjudication's control
  sha256 `b732230c…` and bracket check.

**4. No result-dependent rule change: PASS.**
* `git log cd5016f1..HEAD -- NS/protocol NS/theory NS/code NS/config NS/tests` is empty; the last commit touching those
  directories is `cd5016f1`. Commits after the freeze only add qualification evidence (`978d9965`), reviews
  (`c91991c6`, `e68f3d64`), the grant, the seal, post-exec checks/ledger (`2c50f534`) and the adjudication.
* The adjudication introduces no criterion, margin, tolerance or threshold. Its verification table and liabilities
  assessment verify the frozen conditions; neither adds a condition for or against closure.

**5. Correct scope: PASS.** Record: cell 307, m 5, route RLR, scope CLOSURE_ONLY; driver `TARGET_CELL = 307`. The
adjudication's conclusion is cell 307 only, under RLR, closure only.

**6. Closure / adoption distinction: PASS.** Section "Closure is not adoption" states: not adoption in r5, not under
floor r2, not r6, not K5 closed, not P5Y closed; no floor, threshold or adoption-semantics change; any adoption needs
a separate prospective campaign; the document authorizes nothing. This matches the §8 closing paragraph.

**7. r5 unchanged, no r6: PASS.**
* `K5_COVERAGE_MAP_R5.json` blob = `f978eeb6b41188eabaf3c6d590c9178d711f1ce6` at HEAD, `cd5016f1`, `7f45e048` and in
  the worktree; its sha256 `e2197051…` = the record's `input_sha256.coverage_r5`; last commit `ae4cbc2c`.
* `git log --all --name-only` shows no coverage-map r6 path on any ref. Record `governance_state_before.r6` = absent.

**8. Other cells unchanged, nothing inferred: PASS.**
* `git diff --name-only 7f45e048 HEAD` outside NS is empty; `p5y_k5_tail_c2_closure` tree is unchanged since `7f45e048`.
* The adjudication names cells 306, 308, 309 only to say they are unchanged and nothing is inferred; it states no
  quantity of any other cell or m.

**G2 (qualification review): PASS.**
* The adjudication's first verbatim block equals `NS/review/INCIDENT_INDEPENDENCE_REVIEW.md` §4 exactly (heading
  through C6; compared as text after stripping the trailing newline). It therefore carries C1-C6 verbatim, including
  F1(a), F1(b), "4 ledgered plus 1 unledgered", "temporal and parametric independence only" and result-chasing risk
  MEDIUM.
* It names N4 and N7; each quoted note is an exact substring of `NS/review/RLR307_QUALIFICATION_REVIEW.md`.

**E5 (qualification review): PASS.**
* `cpu_seconds_workers` does not occur in the adjudication (grep). N6 is referred to by label only; no value cited.
* The only numbers placed next to cell-307 quantities are record-derived: the target Γ (sign, sha256, bracket) and
  C2's committed historical cell-307 control. No decoy, validation or qualification value appears beside them.
* The adjudication applies §8 verbatim and states the closure/adoption limits E5 lists (see checks 1 and 6).

## Blockers
None.

## Notes (non-blocking)
* **R1.** The verbatim N4 quote (required text under G2, and identical to what the grant carries) contains a
  decoy-derived digit count. It is a structural size, not a certified value, and it sits in the notes section, away
  from every cell-307 quantity. Not an E5 breach; no action.
* **R2.** Adjudication table rows 1-13 were each re-checked on committed bytes, except that for row 5 I scanned the rung
  records (case-insensitive) for traceback/refusal/quarantine/exception/error tokens and found none, rather than
  reading them. The liabilities claim that the six certifier hashes in the record appear in `C1B_R2_CODE_PINS.json`
  also checks (6/6, presence check).
* **R3.** For the grant carrying C1-C6, N4 and N7, I ran a presence check only (grant fields
  `incident_review_conditions_C1_C6_verbatim`, `qualification_review_notes_verbatim`); I did not byte-compare the grant.
  That is outside the brief-§28 checks and does not affect this review.
* **R4.** The residual limitation (protocol §6: certified inputs from one implementation; Γ from C2's frozen consumer,
  validated by exact control reproduction) is stated correctly by the adjudication. I did not re-certify or recompute
  either, as the hard rules require.
* **R5.** The adjudication's liabilities assessment (C1-C6, N4, N7 do not affect validity of the one frozen
  evaluation) is reasoned from committed facts I also confirmed: one seal, one consumed marker, 0 `RUNG_EXCEPTION`,
  frozen directories unchanged since `cd5016f1`. I agree with it.

## Conclusion
All eight brief-§28 checks, plus G2 and E5, pass on committed bytes. The adjudication applies the frozen §8 criterion
verbatim to the correct sealed record, the exact sign is negative, and scope and closure-only limits are stated
correctly. Next step under protocol §10: handover. r5 stays authoritative; no r6; K5 and P5Y are not closed.
