# Independent freeze review — K5 PARTIAL closeout protocol, successor R2
CLOSEOUT_FREEZE_REJECTED

## Reviewer context

* Fresh context, read-only, adversarial. I had no part in C1–C12-R2, floor r2, route audit r0/r1, the rejected
  closeout freezes 08e9acd1 / dfcd8f79, their reviews 591b4394 / 0d275038, or the R2 freeze.
* Target: worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, branch `p5y-k5-tail-c11rd-d1d2-extension`, HEAD
  9f702acba4259599db808141a271e471cd6b53ca (2026-09-28 01:33:54 +0900), tree be7d774fefcbf266daeeb327a273b199a826bbb5.
  `git status --porcelain --ignored` was empty before and after my runs.
* Frozen files read in full, with their blob ids at 9f702acb (recorded here because I01 locates the freeze commit from
  history and cannot pin its own hash, see N13):

  | file | lines | blob |
  |---|---|---|
  | `README.md` | 31 | 72e6789a32d378d1a3f1003898562c459699d6b9 |
  | `protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL_R2.md` | 448 | c3c1888a5c5efc34c1312d235729b08de220eb0b |
  | `code/closeout_checks_r2.py` | 1007 | 11b021a04c9e299559c49bf7e9747f15560d4451 |
  | `code/drift_selftest_r2.py` | 196 | 8d63296ea0ab539316885532110cd360d10257fa |
  | `config/REF_RULES_R2.json` | 36 | 0fdc80c1d73da40ddd6b8add9b2cca91761fe78a |
  | `config/WORDING_RULES_R2.json` | 30 | 9d8743322b010e2a15135f8edc81d852f7ca0795 |
  | `config/WORDING_FIXTURES_R2.json` | 72 | c3b43211a1747e4a6c84068d0ec9147f9ae544ff |
  | `config/PUBLICATION_ALLOWLIST_R2.json` | 130 | 0e45b3556ac077e578f0ea908f324d5335959d13 |
  | `evidence/REF_SNAPSHOT_R2.json` | 3790 | 4711e3c61cc18bbd0874370dc19ea629d0a3793c |
  | `evidence/PREFREEZE_CHECKS_R2.json` | 272 | 595543013db2f16a7392034645617218362246df |
  | `evidence/DRIFT_SELFTEST_R2.json` | 212 | f884ece8d705a1c4139adbcd33dd447c859dca08 |

* Both predecessor reviews read in full: `level4/closure_proofs/p5y_k5_partial_closeout/review/CLOSEOUT_FREEZE_REVIEW.md`
  (591b4394: B1, N1–N9, points 1–15) and `level4/closure_proofs/p5y_k5_partial_closeout_r1/review/CLOSEOUT_FREEZE_REVIEW_R1.md`
  (0d275038: B1, B2, N1–N11, points 1–18). Also the route-audit r1 review N4.1–N4.9 (:127–183) and route audit r1 §9
  (:578–594).
* I created, modified or deleted nothing in either repository. I wrote only into my scratch directory: this review, the
  checker outputs (`x.json`, `d.json`, `s.json`), the self-test output (`st.json`, `dw/`), two ref listings, and three
  probe scripts of my own (below).
* **Code run.**
  * The frozen checker, after reading all 1007 lines: imports `argparse, ast, datetime, difflib, hashlib, json,
    pathlib, re, subprocess, sys, fractions`; subprocesses are git (`rev-parse, symbolic-ref, merge-base, for-each-ref,
    config --get, show, cat-file, diff, status, ls-files, log, ls-tree, grep, rev-list, hash-object` without `-w`) and,
    in the publication phase only, the pinned synthesis verifier. The C11RD sources are `ast.parse`d from `git show`,
    never imported. It holds the D1/D2 hash sets in process memory for L01 and prints counts only.
    * `--phase freeze --out <scratch>/x.json` at 01:39:49 +0900 → **28/28 PASS**, exit 0 (I01 ok, freeze commit
      9f702acb, 11 files; T01 41 fixtures, corpus 276, 0 violations; L01 0/0, decoys behave).
    * `--diff …/evidence/REF_SNAPSHOT_R2.json --out <scratch>/d.json` at 01:40:13 → **CONTINUE**, exit 0; one new
      commit (9f702acb), every touched file exempt; recomputed obligation table equal to the snapshot's.
    * `--snapshot --out <scratch>/s.json` at 02:01:17–02:07:25 → CONTINUE; 134 refs; obligations identical to the frozen
      snapshot; the only differences are the moved tip of this branch and the 8 R2 files that are now carriers.
  * `code/drift_selftest_r2.py --workdir <scratch>/dw --out <scratch>/st.json` (01:56:57–02:00:37), after reading all
    196 lines: every ref write (`update-ref`, `hash-object -w`, `commit-tree`) runs with `cwd=clone`; the clone is a
    `git clone --shared --no-checkout` under the workdir, asserted to have a different common dir; the checker copy
    resolves REPO to the clone. Result **pass, 10/10**, every verdict and stop-class set identical to
    `evidence/DRIFT_SELFTEST_R2.json`; clone deleted. `git for-each-ref` of the real repository before (01:38:39) and
    after (02:01:02) is byte-identical (134 refs).
  * My own probes, importing nothing from the repository: `wording_probe.py` re-implements `normalize`, tier P, tier L
    and `_licensed` from `config/WORDING_RULES_R2.json` and the two literal sets read by `ast.literal_eval` from blobs
    fb297cf2 / aa856b1b, plus the predecessor and R1 scans; `carrier_probe.py` regex-tests the frozen carrier and flag
    regexes on synthetic status text; `merge_probe.py` re-implements checker :707–723 on synthetic log text. Text only.
* No Γ, margin, factor, bisection, knockout or Λ bound computed; no arithmetic on any TCT input, registry or
  certificate. Every figure below is quoted from the line cited.
* Nothing opened under a C11R quarantine directory. For C11R I read only `adjudication/ADJUDICATION_C11R_N9.md` :144;
  for C11RD only line 2 of the N9 adjudication and its review. No D1/D2 value written or echoed. No session transcript.
  No network, AWS or Vultr.
* **Incidental exposure (disclosed, used in no computation):** committed 306–309 figures at C2 adjudication :38–48, :65,
  :474–478; C3 adjudication :347–350; C4 adjudication :286–290, :498–540; C7 README grep hits :15, :24, :112; C8
  adjudication :348, :382; C12-R2 adjudication :225, :363–370, :385–400. K1/K2-K3/K4R1 owner records and the K2/K3
  REVIEW.md (K2/K3 constants), K4R1 commit message (K4 B values).

## What I checked

* **Freeze scope.** `git diff --name-status 0d275038 9f702acb`: exactly the 11 files of §13, all `A`, 6224 insertions.
  Predecessor namespaces: `git diff --name-only 591b4394 9f702acb -- …/p5y_k5_partial_closeout` empty; the trees of
  `p5y_k5_partial_closeout` at 591b4394 and of `p5y_k5_partial_closeout_r1` at 0d275038 equal those at HEAD
  (961bd323…, 7901e06b…). No commit after 591b4394 / 0d275038 touches them.
* **Current refs, independently** (`git for-each-ref`, all object types; `--sort=-committerdate`; `git log --all
  --since=2026-09-27T12:00`): 134 refs = 47 heads, 37 remotes, 42 tags (32 annotated, all peeling to commits),
  5 `refs/codex/…` tree refs, 3 governance refs (one of them, `refs/c12r2/cell306-pending-result`, points at a blob).
  Newest tips: 9f702acb (this branch, 09-28 01:33:54), e88a2885 (`p5y-k4r1-final-closure` = origin, tag
  `p5y-k4-successor-closed`, 09-27 22:13:19), b5b4c917, bc4ba08e, dec92e09 (governance), df703837, 7d5cf02b. Nothing
  newer than e88a2885 on any other ref. 36 linked worktrees, none detached.
* **Owner records at their tips, independently:** 7d5cf02b `FINAL_ADJUDICATION.json` (`k1_successor_verdict`
  K1_SUCCESSOR_CLOSED, `residual_blockers` NONE, `sr_successor_science` PASS); df703837 `FINAL_COUNTERSIGNATURE.json`
  (countersignature K2/K3 PASS; `status` K2/K3 CLOSED, K4/K5 OPEN); e88a2885 `K4R1_FINAL_VERDICT.json` (CLOSED /
  CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN / NONE, `HISTORICAL_K4_COMMIT` bc4ba08e, `P5Y_STATE` K5 OPEN, P5Y NOT_YET_CLOSED);
  bc4ba08e `K4_EXECUTION_RESULT.json` (NOT_CLOSED (K4_INCONCLUSIVE_K1_RECORDS)); `K5_STATUS.md` :4–5, :52 (SR K5
  NOT STARTED, one blob d212f0d5 on 23 tips). The computed table in the snapshot (K1, SR K1, K2, K3, K4 CLOSED; K5
  OPEN; P5Y NOT_YET_CLOSED; SR K5 NOT STARTED; union open [[306, 309]]) matches what I read.
* **Carrier coverage, independently:** `git log --all -G <carrier_regex> --name-only` without a pathspec (244 paths:
  the 233 in scope, the 8 R2 files, and 3 out-of-scope presentation files); a broader state-spelling search
  `K[1-5]|P5Y` + state word over `level4 docs README.md` (113 paths, 64 of them not carriers, excluding R2).
* **Every citation in §5–§11** that carries a number or verdict (table in point 16); the checker's diff, identity,
  allowlist, stale-line, wording and self-test code paths line by line.

---

## BLOCKERS

**B1. The drift classifier silently drops new status carriers from any commit that also touches a known carrier
path. When the known-path files of that commit are owner records, no STOP fires — contrary to protocol §5.2 :126
("Any other touched carrier ⇒ STOP_AMBIGUOUS_CROSS_REF_STATE").**

Mechanism (`code/closeout_checks_r2.py`):
* :707 `touched` = the `-G <carrier_regex>` pass over new commits. Without `--pickaxe-all` it lists, per commit, only
  the files whose diff matched.
* :709 `by_path` = `git log --name-only -- <233 known carrier paths>`. The pathspec limits the listed files to known
  paths.
* :712 `for c in {x["commit"]: x for x in touched + by_path}.values()`. For a commit present in both lists, the
  `by_path` entry overwrites the `touched` entry. Every new-path carrier found by `-G` in that commit disappears from
  classification.
* :716–722 then classifies only the known paths. An owner-record path gets "known owner record changed -> recompared
  below" (:719) and no stop. The recompare (:741–746) compares only the parsed obligation fields. The flag scan
  (:758–760) looks only for positive-closure spellings. For commit tips, nothing compares the inventory with
  `known_carriers`; only tree refs get that comparison (:738–740).

Evidence:
* Real git output for e88a2885, the actual K4 closure commit. The `-G` pass lists five carriers:
  `K4R1_FINAL_VERDICT.json`, `README.md`, `adjudication/FINAL_ADJUDICATION.json`, `…/FINAL_ADJUDICATION.md`,
  `…/build_final.py`. The by-path pass restricted to the owner path lists only `K4R1_FINAL_VERDICT.json`.
* `merge_probe.py`, a line-for-line re-implementation of :712 on that shape, keeps only the owner path.

Concrete silent drift, before adjudication or before publication, on any ref:
* **A new coverage map.** One commit updates `level4/closure_proofs/p5y_k5_remaining_cell_closure/K5_STATUS.md` (an
  owner record present on 23 tips) without touching its SR K5 row, and adds a coverage map at a new path.
  * The map has schema `…coverage-map.v6`, `K5_COVERAGE_COMPLETE` false, and one cell fewer open.
  * The map is dropped from classification. The recomputed table is unchanged, because r5's path is untouched. No
    positive flag fires.
  * Result: **CONTINUE**. The r6 path appears nowhere in `new_carrier_commits`; the diff file shows only an
    SRK5_OWNER compatible-drift entry. The adjudication and publication would still state "r5 remains the current
    authoritative coverage map" (§10).
  * This bundling is the repository's own pattern: a3547b9b, the only commit that ever wrote `K5_STATUS.md`, also
    wrote the carrier `code/k5_coverage_map.py`.
* **A K4R1 reversal.** One commit adds `…/p5y_k4r1_final_adjudication/review/…REVIEW.md` with text such as
  "K4R1_SUCCESSOR_VERDICT = CLOSED is not supported; K4 = NOT_CLOSED". The same commit edits a non-parsed field of
  `K4R1_FINAL_VERDICT.json`, for example appending to `non_blocking_notes`. Result: **CONTINUE**, and K4 is published
  as CLOSED.

Why this blocks:
* It breaks the one mechanism that R2 introduced to repair both predecessors' B1, stale cross-ref state not forcing a
  stop.
* The protocol text states the rule, but the frozen checker does not implement it.
* The frozen self-test cannot see the defect: no scenario bundles an owner-record edit with a new carrier (S2 and S6
  edit the owner record alone).
* After this review the checker cannot be changed (protocol :3–4).

**B2. "Content-based" discovery recognizes state only in the spellings of `carrier_regex_ere`. That regex misses the
repository's own prose status form. The positive-closure-flag regex runs only on carrier blobs. So a K-state
reversal or closure claim written in that form, on any ref, passes as CONTINUE.**

* The carrier regex covers JSON keys, `K[1-5] = X`, `P5Y = X`, `P5Y state`, and named tokens. It does not cover
  "K4 OPEN", "K2 CLOSED", "K1 is NOT_CLOSED", "K4 remains OPEN", "| K4 | CLOSED |" or "K4: CLOSED". `carrier_probe.py`
  returns no carrier match for each of them.
* **Repository precedent.** The actual independent review of the K2/K3 closure,
  `level4/closure_proofs/p5y_k2_k3_final_countersignature/REVIEW.md` (df703837), records "The public status is
  **K2 CLOSED, K3 CLOSED, K4 OPEN, K5 OPEN**". It is **not** a carrier, and neither is the K1 successor adjudication
  README.
  * My broader state-spelling search finds 64 in-scope paths in history that carry K/P5Y state prose and are not
    carriers.
  * One of them is `docs/research_synthesis/README.md` ("K1 is NOT_CLOSED"), the very line §14 treats as stale K1
    state.
* **The N3 repair is effective only inside files that are already carriers.** The flag regex was widened for the N3
  repair to `K5 CLOSED_BY`, `P5Y *[=:] *CLOSED` and `K5 *= *CLOSED`. But `flag_hits` (:621–631) scans only inventoried
  carrier paths.
  * "K5 CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN", "P5Y: CLOSED", "P5Y=CLOSED" and "K5=CLOSED" are flags but not carriers
    (probe). In a new file they are never scanned.
* **The scenario the R1 review named.** R1 review B1 (:123–127) named "a review or re-adjudication of the K4R1 or K1
  successor verdict" landing on another ref. Its acceptance condition (:426–428) asked for "K1/K4/K5/P5Y status
  assignments in JSON and prose forms".
  * A K4R1 or K1 review written like the K2/K3 review ("K4R1 adjudication REJECTED … K4 remains OPEN") produces no
    carrier hit on any ref. The result is **CONTINUE**.
  * The owner table then still reports K4 CLOSED. This is the predecessor-B1 failure class.
* **The design is fail-open for unrecognized text.** Every new commit outside this branch that matches neither the
  regex nor a known path is ignored, even under `level4/closure_proofs/`.

What does **not** change:
* At the freeze, the snapshot is correct. I re-derived every owner row independently, and a fresh `--snapshot` agrees.
* B1 and B2 concern the forcing mechanism between freeze and publication, not today's facts.

---

## NOTES (non-blocking)

**N1. Blob refs and tags that peel to trees or blobs are never inspected.** `enumerate_refs` classifies them
"unrelated", and the diff raises no stop for a new one.
* This repository already stores a pending scientific result as a blob ref (`refs/c12r2/cell306-pending-result`).
* G01 covers only `refs/c11rd/`, `refs/c12r2/`, `refs/c12r1/` and `refs/c12/`. A new `refs/c13/…` result ref would
  pass.

**N2. Rewinding or deleting a binding ref gives CONTINUE while the record stays live elsewhere.**
* Example: branch `p5y-k4r1-final-closure` reset to b5b4c917 while tag `p5y-k4-successor-closed` still holds
  e88a2885.
* Likewise, deleting only the owner JSON on the binding branch while the tags keep it.
* The ref move is listed in `ref_changes`, but `compatible_drift` (:757) reflects only owner-record/live-tip changes.
  §5.2 says moved refs are COMPATIBLE_DRIFT.

**N3. Owner-record edits in unparsed fields count as compatible drift.**
* `K5_STATUS.md` `P5Y_STATUS = NOT_CLOSED` → `CLOSED`, or its `| CUSUM K5 |` row set to CLOSED, changes neither the
  parsed SR K5 row nor any flag. The flag regex has no `P5Y_STATUS = CLOSED` spelling.
* Changes to non-table K1 fields (e.g. `cusum_successor_science`) are parsed but never compared.

**N4. The search scope `level4 docs README.md` is itself a path restriction.** Three out-of-scope carriers exist
(`figures/final/figure13_ps1_current_boundary.svg` and two `scripts/*.py`, 59ad9bb8, `LEVEL4_GLOBAL_CLOSURE = NO`, on
main and `codex/presentation-refresh`). A status claim under `figures/` or `scripts/` is invisible.

**N5. Commits reachable only from a linked worktree's detached HEAD** are counted by `rev-list --all` / `log --all`, but
`tip_inv` uses ref tips only. An owner-record change there is "recompared" against refs that do not contain it, giving
CONTINUE. None of the 36 worktrees is detached now.

**N6. Snapshot granularity.** Ref rows carry a carrier count and owner-record kinds, not per-ref artifact paths or
states; those are derivable from `known_carriers` and `reconstruction`. The class "unrelated" is never produced for a
commit ref, because root `README.md` is a carrier on every tip. Acceptable, since it errs toward informational.

**N7. The diff evidence does not bind which snapshot was used.** Only `snapshot_observed_at` is recorded, not the
snapshot's blob or hash. The adjudication reviewer should confirm 2026-09-28T01:23:46+09:00 / blob 4711e3c6.

**N8. Wording scan: paraphrase and markup gaps (not weakenings).** The predecessor, R1 and R2 all accept each of the
following:
* "H3a is now established for m = 1, 2, 3."
* "H3a is supported / true / verified for m = 1."
* "This proves H3a."
* "Cell 309 is therefore unclosable."
* "Cell 308 can not be closed."
* "All routes are now exhausted."
* "Every route has been exhausted."
* "306 has failed."
* "CUSUM K5 closed."
* "K5 is now closed."
* "SR K5 has completed."
* "r5 is the final map."
* "Cell 309 has been refuted."
* A banned phrase hard-wrapped inside a blockquote (`> … H3a is⏎> established`, or `> … 309 is⏎> unclosable`), because
  the `>` marker survives normalization. This namespace hard-wraps blockquotes (§7 308, §14).
* A banned phrase inside `_…_` / `__…__` emphasis.

The fresh publication-conformance check (§12 step 7) must read semantically against §14 (A)–(G).

**N9. T01's "R2 ⊇ R1" holds on the 276-sentence corpus, not universally.** R2 accepts "Unresolved cells are
not⏎evidence against H3a.", which R1 rejects. That is a correct relaxation of R1's wrapped-negation false positive (R1
review N9), but the check label reads as universal.

**N10. Stale-line provenance.** `PUBLICATION_ALLOWLIST_R2.json` says README :137 and synthesis README :160 were "last
touched by ce7fb933 (2026-09-16)".
* `git log -L` shows both lines were last changed by e47e8947 (2026-09-13, author = committer date). ce7fb933 only
  edited the adjacent bullets.
* The enforced "(as recorded 2026-09-16)" is defensible as the date the list was last re-published. The frozen
  `context` text is false.
* `correction_ok` does not enforce the ref/tip or `(CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN)`. For README :137 ("K1 and P5Y
  remain NOT CLOSED") it does not enforce that the supersession is scoped to K1, since P5Y is still not closed.

**N11. Other stale PS1/SR current-state bullets are neither listed nor editable under P02.** README :133
("CURRENTLY_GRACEFUL_DRAINING") and :136 ("PS1/SR is a **separate, ongoing** line") sit in the same list as the
corrected lines. The P-B block should name them superseded.

**N12. §7 309 attribution.** The ceiling 3.266416 and "exceeds … by 9.79 %" come from C8 adjudication :348 / :382
("floor exceeds ceiling by 9.79 %"). The cited C7 README gives 3.586306094 and a 9.7933 % clearance of the critical A0
(:15, :24, :112). The figures are consistent; only the cited source is incomplete.

**N13. I01 finds the freeze commit by `--diff-filter=A` on HEAD's history.** A rewrite of this unpushed branch (S06
forbids a remote copy) would re-anchor it. The blob ids above are the external record.

**N14. Two further blind spots.**
* An evil merge is invisible to both passes, because `git log` runs without `-m`.
* A new ref at an old, non-tip commit resurrects historical carriers with no comparison against `known_carriers`.
  Only tree refs are compared.

**N15. §0's B1 row says the diff "inspects every commit new since the snapshot".** It inspects only commits that match
`-G` or a known path (and, per B1, not every file of those).

---

## 1. All-ref discovery actually occurs

✓.
* `for-each-ref` with no pattern (:448–455) returns all 134 refs, with annotated tags peeled.
* Tree refs are grepped (:486–489). Blob refs are enumerated but not inspected (N1).
* My independent enumeration matches the snapshot's 134 rows.

## 2. No hard-coded-only state discovery remains

**Partly.**
* No branch name is used anywhere in discovery. Refs are selected by the carrier inventory at their tips.
* The six owner-record paths are a content-type map of where each obligation's record lives. That is acceptable in
  design **only because** anything outside it is supposed to force STOP_AMBIGUOUS. It is not a disguised branch
  hard-code.
* An owner-type record at a **new** path is caught only as STOP_AMBIGUOUS, and only if:
  * its diff matches the carrier regex (B2: prose forms miss); and
  * its commit does not also touch one of the six owner paths (B1).
  Otherwise it is not caught. The owner table is never extended to it.

## 3. Frozen ref snapshot complete

✓ (N6).
* 134 refs; `commit_tips` 90; 233 carrier paths; 245 known (path, blob) carriers.
* Owner-record versions, with live tips and introducing commits, are recorded.
* The obligation table is computed; flags are empty; verdict CONTINUE.
* My fresh `--snapshot` (02:01:18) reproduces it, with the freeze commit as the only difference.

## 4. New relevant refs detected

**Not reliably (B1, B2, N1).**
* The self-test S1/S8 pass is reproduced.
* Not detected:
  * a new carrier bundled with an owner edit;
  * a new record in prose form;
  * a new blob ref.

## 5. Ambiguous refs force stop

**Partly.** STOP_AMBIGUOUS fires for unexplained carriers in new commits and in new tree refs, and all exceptions
become STOP_DISCOVERY_ERROR. B1 and B2 leave paths where ambiguity yields CONTINUE.

## 6. Moved binding refs fail-closed

**Partly.**
* S2 (moved to a K4-changing commit) stops, and S3 continues as designed.
* A rewind or partial deletion while the record is live elsewhere continues (N2).
* A move to a commit that bundles an owner edit with new carriers continues (B1).

## 7. Predecessor scan strength preserved

✓.
* Tier P = the 17 predecessor phrases read from blob fb297cf2, plus 11 additions, applied absolutely.
* No predecessor phrase contains `*` or a backtick. R2's normalization only removes those and collapses whitespace, as
  the predecessor did. So "predecessor rejects ⇒ R2 rejects" holds for every input, not only for the corpus.
* My probe found no counterexample.

## 8. Whitespace normalization catches wrapped claims

✓ for plain hard wraps: all wrapped fixtures and R1 probes are rejected. ✗ for blockquote-wrapped and `_`-emphasized
text (N8). Those are not weakenings.

## 9. Negation handling is proposition-local

✓ for tier L.
* Only the last cue counts, it must sit immediately before the match (whitespace or a fixed neutral parenthetical), and
  no `.;:!?` may intervene.
* Probes are rejected as required: "not merely …", "No one doubts that …", "It is not surprising that …",
  "Not only are …".
* Tier P is never licensed.

## 10. "all routes exhausted" restored

✓ in tier P, via the predecessor literal.

## 11. Known R1 false negatives caught

✓. All 8 R1-review probes are rejected, including "K5 is not closed, H3a is established for m = 1." (T01
`r1_probe_misses` is empty; my probe agrees).

## 12. Post-freeze identity protection exists

✓ (N13).
* I01 requires freeze blob = HEAD blob = worktree hash for all 11 files, and no commit after the freeze touching them.
  README is exempt only in the publication phase.
* It runs in the freeze, adjudication and publication phases. It passed in my run.

## 13. Stale K1 public wording handled prospectively

✓ (N10, N11).
* Four allowlisted lines are replaced in place by a frozen correction form that keeps the claim and date (P02/P03).
* The two `PS1_CURRENT_STATUS.md` lines stay byte-identical (H01) and are reported.
* Historical records are untouched.

## 14. Publication allowlist exact

✓.
* P01 compares every changed path (tracked, untracked and ignored) against an exact per-phase list.
* P02 allows only the stale-line replacements plus one block at the frozen place.
* P03 requires no unmarked stale K1 line.
* I01 guards the frozen files.

## 15. N4.1–N4.9 retained

✓.
* N4.1 §3.
* N4.2 §4 with L02 blob pins.
* N4.3 §6.1/§6.2: CUSUM-scoped, never per cell.
* N4.4 §8: P5Y consequence and H3a semantics.
* N4.5 §7, exact.
* N4.6 §7: C4 Condition 3 verbatim and the MC evidence.
* N4.7 §9: seven rows matching r1 §9 (R-asm, R4, R5, B1, RSO, R-E1g, R-F1′). R-α, R-I2-alone, Floor-307 and X308 are
  rejected as actions.
* N4.8 "current authoritative".
* N4.9 §11 plus the SR-K5 carrier spellings.

The predecessor's N1–N9 and R1's N1–N11 are all carried in the §0 table.

## 16. Cell scoping correct: citation spot-checks

| # | claim | checked at | result |
|---|---|---|---|
| 1 | CUSUM cells 0–309 meeting (0, 2] | E01 :89 | ✓ |
| 2 | "otherwise unresolved cells ⇒ `K5_INCONCLUSIVE`" | E01 :91 | ✓ verbatim |
| 3 | Γ(5, 306; S_I1) = −0.030469257709306738 | C2 adjudication :47 | ✓ |
| 4 | 307 not closed by C2's supply | C2 :48 (Γ positive) | ✓ |
| 5 | F2: ×1.25 → +0.029163293; margin 1.1277; FAILS | C2 :65, :476, :478 | ✓ |
| 6 | Γ(5, 306; S_I2) = +0.005159101140006536, sealed at 276f4d41 | C12-R2 adjudication :225; `git show --stat 276f4d41` (1 result file) | ✓ |
| 7 | EXECUTION_ACCEPTED 1173670f; CELL306_NOT_ADOPTED 9c2cbf21; ADJUDICATION_ACCEPTED c5324a78 | line 2 of each; commit subjects | ✓ |
| 8 | base TRUE; F1′ (a)–(c) TRUE, (d) FALSE; F2 FALSE | C12-R2 adjudication :363–370, :391–400 | ✓ |
| 9 | N9 CLOSED 7d67989d; ADJUDICATION_ACCEPTED fb237288 | line 2 of each; commits | ✓ |
| 10 | 307: C3 D′ positive; knockout closes, so A0 is not the blocker | C3 :349; C4 :288–290 | ✓ |
| 11 | 308: knockout leaves Γ = +0.039568 | C3 :350 | ✓ |
| 12 | 308: C4 Condition 3 (4.311; 18.2×; 4.375229; "nothing licenses …") | C4 :534–537 | ✓ word for word |
| 13 | 308: "operator-level route not excluded"; 2,000,000 paths, ~65 SE | C4 :510–512 | ✓ |
| 14 | Condition 2 bars "the honest answer is that none can" and the Lemma T citation | C4 :527–532 | ✓ |
| 15 | 309: Condition 1 scope | C4 :522–525 | ✓ |
| 16 | 309: exclusion does not show 309 unclosable | C4 :503 | ✓ |
| 17 | Λ₃₀₉ ≥ 3.586306094; ceiling 3.266416; 9.79 % | C7 README :15, :24, :112; C8 :348, :382 | ✓ (attribution: N12) |
| 18 | F1′ only for a cell with its own two-implementation evidence | floor r2 spec :193 | ✓ |
| 19 | C1 MARGINAL; Campaign B STOPPED / INFEASIBLE; C11 EXECUTION_INVALID; C9 EXECUTION_BLOCKED; C8 COUNTERFACTUAL_ONLY | C1 README :11, :30; B README :16, :26–28; C11 README :3; C9 README :3; C8 README :87 | ✓ |
| 20 | limb 1 does not fire: FIRST_CELL_SUPPORTED_ALL_M, ADOPTED | first-probe RESULT.md :7–8, :65 | ✓ |
| 21 | r5 blob f978eeb6; `K5_COVERAGE_COMPLETE` false; m = 5 open [[306, 309]], others [] | HEAD blob; JSON | ✓ |
| 22 | `K5_CLOSED` used unscoped | C11R adjudication :144 | ✓ |
| 23 | SR K5 NOT STARTED; `AUX3_SR_FEASIBILITY_FAIL` | `K5_STATUS.md` :52; AUX3_SR_RECORD.json :2, :20 | ✓ |
| 24 | K5 upstream of T9/T10 and L4 | DAG :60, :75, :97–102 | ✓ |

Scoping:
* 306 is OPEN / NOT ADOPTED with its facts coexisting.
* 307 is OPEN with the exact N4.5 sentence.
* 308 is OPEN with Condition 3 exact and MC as non-exclusion.
* 309 is OPEN, refuted only within Condition 1's scope, with UNKNOWN outside it.
* `K5_INCONCLUSIVE` is never applied per cell.

## 17. H3a treatment correct

✓.
* §8 carries README :236–238: no failed cell or `K5_INCONCLUSIVE` is evidence against H3a, and refutation needs a
  certified counterexample.
* K5-B is sufficient-only (bridge :18, :61).
* No support is claimed for any (D, m).

## 18. r5 / no-r6 correct

✓.
* §10 names r5 blob f978eeb6 as the current authoritative map.
* C01/C02/C03 enforce it.
* `git log --all --diff-filter=A` finds no `*COVERAGE_MAP_R6*` or `*coverage_map_r6*` on any ref. The only
  coverage-map carriers across refs are r1–r5 and their scripts.
* Drift detection of a new map is broken in the B1 case.

## 19. Zero science

✓.
* The freeze adds 11 administrative or document files.
* The checker and self-test are administrative; the self-test writes synthetic status text only, in a deleted clone.
* The governance refs are exactly as pinned (G01).
* The Γ 306/307/308/309 = 0/0/0/0 declaration is uncontradicted.
* I computed nothing.

---

## What would change the verdict

**To CLOSEOUT_FREEZE_ACCEPTED (on a successor freeze R3; nothing in this round):**
* **B1.** Classify files per commit as the union of both passes; never let one pass overwrite the other. Then:
  * add self-test scenarios that bundle an owner-record edit with a new carrier;
  * add one that bundles a `K5_STATUS.md` edit with a new `coverage-map.v6` file;
  * require STOP_AMBIGUOUS in both.
* **B2.** Make unrecognized status text fail closed, by either of:
  * **Broaden the carrier regex** to the repository's prose forms, for example `K[1-5]` / `P5Y` / `SR K5` followed
    within a few characters (spaces, `*`, `` ` ``, `:`, `|`, `=`, "is", "remains") by a state word (CLOSED, OPEN,
    NOT_CLOSED, NOT CLOSED, NOT_YET_CLOSED, PARTIAL, NOT STARTED, INCONCLUSIVE). Then run the positive-flag regex over
    every blob added or modified by every new commit in scope, not only over carriers.
  * **Or stop on every new commit** outside this branch that touches `level4/closure_proofs/**`, `docs/**` or
    `README.md`, unless a frozen rule marks it unrelated.

  Include a K2/K3-REVIEW-style fixture ("The public status is K4 OPEN") that must STOP.
* Optionally:
  * N1: inspect blob refs, and tags peeling to trees or blobs;
  * N2 / N3: stop on binding-ref rewinds, and on changes to unparsed status lines of owner records;
  * N7: bind the snapshot hash in the diff output;
  * N8: strip `>` blockquote markers and `_` emphasis before scanning;
  * N10 / N11: correct the provenance text and name the extra stale PS1 bullets.

With those and no new defect, I would accept. Everything else is sound as frozen:
* the obligation table as computed today;
* the wording scan's non-weakening;
* the identity guard;
* the allowlist;
* the cell dispositions, H3a handling, r5 / no-r6, SR K5 treatment and N4.1–N4.9.

**This review would be wrong if:**
* **B1:** `git log -G … --name-only` listed every file of a matching commit, or the by-path pass listed files outside
  its pathspec. It does neither: see the e88a2885 output above. Or the dict merge at :712 did not overwrite, but
  Python dict comprehension semantics are unambiguous.
* **B2:** the user's authorization accepted a carrier heuristic with known recall gaps as "content inspection", with
  fail-open treatment of unrecognized text. In that case B2 would be a note. B1 would still block, because the frozen
  checker does not implement the frozen protocol's own STOP rule.
