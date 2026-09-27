# Independent freeze review — K5 PARTIAL closeout protocol, successor R1
CLOSEOUT_FREEZE_REJECTED

## Reviewer context

* Fresh context, read-only, adversarial. I had no part in C1–C12-R2, floor r2, route audit r0/r1, the rejected
  closeout freeze 08e9acd1, its review 591b4394, or the R1 freeze.
* Target: worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, branch `p5y-k5-tail-c11rd-d1d2-extension`, HEAD
  dfcd8f79ee90ffbb5d04ada43eb7ffd10b44013d (2026-09-27 23:14:11 +0900). Tree clean including ignored files
  (`git status --porcelain --ignored` empty, before and after my runs).
* Frozen files read in full, with their blob ids at dfcd8f79 (recorded here because no check enforces post-freeze
  immutability, see N1):
  * `level4/closure_proofs/p5y_k5_partial_closeout_r1/protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL_R1.md` (378 lines) — def3c3f3df3af1bde531af9d20cb61f0a1ec71a1
  * `level4/closure_proofs/p5y_k5_partial_closeout_r1/code/closeout_checks_r1.py` (675 lines) — aa856b1bc985f17040bfedbb6a16982c734a10e7
  * `level4/closure_proofs/p5y_k5_partial_closeout_r1/README.md` — 0cf23687693e2edc70b05f684068cda0ad160d6a
  * `level4/closure_proofs/p5y_k5_partial_closeout_r1/evidence/PREFREEZE_CHECKS_R1.json` — af3a9719e194c6d651057ac1455ca50144ba6c0e
  * `level4/closure_proofs/p5y_k5_partial_closeout_r1/evidence/XREF_SNAPSHOT_R1.json` — e074a22a59db150b358cb42aff045072406b14fd
  * freeze tree b0142d4c674b1419885344f5f1887449170a5cb5.
* Predecessor review `level4/closure_proofs/p5y_k5_partial_closeout/review/CLOSEOUT_FREEZE_REVIEW.md` (591b4394) read
  in full (B1, N1–N9, points 1–15), and the route-audit r1 review's N4 items 1–9 (:127–185).
* I created, modified or deleted nothing in either repository. I wrote only into my scratch directory: this review,
  the two checker outputs, a list of recent ref tips, and my own wording probe script (below).
* **Code run.**
  * The frozen checker, only after reading its whole source and confirming it is administrative: imports are
    `argparse, ast, datetime, hashlib, json, pathlib, re, subprocess, sys, fractions`; subprocesses are read-only git
    (`rev-parse, symbolic-ref, merge-base, for-each-ref, config --get, show, cat-file, diff, status, ls-files, log`)
    and, in the publication phase only, the synthesis verifier; `c11rd_validate.py`, `c11rd_qualify.py` and
    `c11rd_compare.py` are `ast.parse`d from `git show`, never imported or executed; `-I` keeps the repository off
    `sys.path`; output is counts and names only.
    * `python3 -I -S -B level4/closure_proofs/p5y_k5_partial_closeout_r1/code/closeout_checks_r1.py --phase freeze --out <scratch>/freeze_checks.json`
      → **26/26 PASS**, exit 0, head dfcd8f79, L01 `files_scanned` 6, 0 original / 0 independent hits, decoys behave.
    * `python3 -I -S -B …/closeout_checks_r1.py --xref --out <scratch>/xref.json` → **pass**, exit 0,
      `observed_at` 2026-09-27T23:24:27+09:00, `refs_scanned` 126, XB1–XB6 all compatible, tips identical to the
      committed snapshot (the only new commit on any ref is the freeze itself, exempt by path).
  * My own probe (not repository code): `python3 -I -S -B <scratch>/wording_probe.py <checker path>`. It
    `ast.literal_eval`s four literals of the checker (`BANNED_ASSERTIONS`, `NEGATION_CUES`, `CLAUSE_SPLIT`,
    `WORDING_FIXTURES`) without importing it, re-implements `wording_findings` line for line (it reproduces T01
    exactly: 0 prohibited missed, 0 allowed false positives), and runs English probe sentences through it and through
    the predecessor's substring list (predecessor checker :127–132, :381). Text only.
  * `python3 -I -S -c` with `json.load` to read r5's key names and open ranges, and to summarize the two checker
    outputs. No other repository code.
* No Γ, margin, factor, bisection, knockout or Λ bound computed; no arithmetic on any TCT input, registry or
  certificate. Every figure below is quoted from the line cited.
* Nothing opened under a C11R quarantine directory (I listed C11R file names with `git ls-files | grep -v quarantine`
  and read only `adjudication/ADJUDICATION_C11R_N9.md` :144). For C11RD I read only line 2 of the N9 adjudication and
  its review. No D1/D2 value written or echoed. No session transcript read. No network, AWS or Vultr.
* **Incidental exposure (disclosed, used in no computation):** committed 306–309 figures at C2 adjudication :47–48,
  :65, :474–478; C3 adjudication :349–350; C4 adjudication :288–290, :503, :510–512, :518–537; C7 README :15; C8
  adjudication grep hits :348, :382, :486; C9 README :37, :39, :46; C12-R2 grep hits for the sealed Γ (adjudication
  :225, result JSON :129, floor application :12, :19); C1 README :24–30; Campaign B README :10, :26–39; K4R1 verdict
  JSON (K4 residual values, not 306–309).

## What I checked (files, lines, commands, ref tips)

* **Freeze scope.** `git diff --stat 591b4394 dfcd8f79`: exactly the 5 files of §13 step 1, 1489 insertions, nothing
  else. `git diff 591b4394 dfcd8f79 -- level4/closure_proofs/p5y_k5_partial_closeout` empty; since 08e9acd1 only the
  review (421 lines) was added there. No change to `README.md` or `docs/` since 08e9acd1.
* **Ref landscape, independently** (`git for-each-ref --sort=-committerdate`, 134 refs: 126 heads/remotes/tags,
  3 governance refs, 5 `refs/codex/turn-diffs/checkpoints/*` pointing at tree objects). Newest tips at 23:43 +0900:

  | tip | committer time (+0900) | ref(s) | subject / reflog |
  |---|---|---|---|
  | dfcd8f79 | 09-27 23:14:11 | `refs/heads/p5y-k5-tail-c11rd-d1d2-extension` | the R1 freeze |
  | e88a2885 | 09-27 22:13:19 | `refs/heads/p5y-k4r1-final-closure` = origin | reflog: branch created 22:12:38 from b5b4c917; commit 22:13:19 "P5Y K4 closed by later successor campaign" |
  | b5b4c917 | 09-27 21:17:46 | `refs/heads/p5y-k4r1-nearzero-successor` = origin | reflog 81f5195a 16:54:28 … 0dc949b5 20:01:57 → 93d82c87 20:45:07 → 8928b8f1 21:17:19 → b5b4c917 21:17:46 |
  | bc4ba08e | 09-27 15:44:32 | `refs/heads/p5y-k4-frozen-execution-r1` = origin | reflog: created 15:16:57 from 5289b6ce; "NOT_CLOSED, K4_INCONCLUSIVE_K1_RECORDS" |
  | df703837 | 09-27 15:03:06 | `refs/heads/p5y-k2-k3-final-closure` = origin | reflog: created 15:01:25 from origin/p5y-postk1-frontier |
  | 7d5cf02b | 09-27 14:25:06 | `refs/heads/p5y-k1-successor-final-assembly` = origin | reflog: da79fe1f fetched from a bundle 14:19:59; adjudication 14:25:06 |
  | 15e70072 | 09-25 17:12:25 Z | `refs/heads/p5y-k1-final-evidence` (+ aws, origin) | PS1 AWS-only assembly |

  No ref moved between the snapshot (23:11:55) and my last check (23:43:27) except the freeze commit.
* **Artifacts at those tips:** `git show 7d5cf02b:…/p5y_k1_successor_final_adjudication/evidence/FINAL_ADJUDICATION.json`
  (and its README), `git show df703837:…/FINAL_COUNTERSIGNATURE.json`, `git show e88a2885:…/K4R1_FINAL_VERDICT.json`
  and its README; `git grep` of P5Y-status tokens (`P5Y_STATE`, `"P5Y": "`, `P5Y = `, `P5Y_STATUS =`) over every
  heads/remotes/tags tip committed after 2026-09-19 (28 distinct commits): the only P5Y-state carriers are
  K5_STATUS.md (09-19), POSTK1_STATUS.json / DAG / PS1 correction (09-13), an SR qualification note (09-09, "P5Y =
  NOT READY"), the K4 exec result (bc4ba08e), the K2/K3 countersignature, the K4R1 verdict, and the closeout
  namespaces. Nothing newer than e88a2885 records a P5Y state.
* **SR K5 across refs, independently:** `git log --all -i -G 'SR[^|\n]{0,25}K5|K5[^|\n]{0,25}\bSR\b'` (since
  09-19 23:xx),
  `git log --all -G 'K5 CLOSED'`, a search for any SR order-3 producer since 09-11
  (`SR order-3|SR_ORDER3|AUX3_SR|…`), per-tip blobs of the two status files (via the checker), the history of
  `AUX3_SR_RECORD.json` (only 986e6173, tag `p5y-k1-sr-o9-aux3-sr-feasibility-fail`, 09-11), and the five codex tree
  refs (`git ls-tree -r`, `git grep`).
* **Every citation in §5–§11** at the cited lines (table in point 13), and the r1 route table §9 (:578–597).
* **Checker:** full source; its T01 fixtures, regexes and clause splitter (probe above); P01/P03 logic; XB1–XB6
  logic; comparison with the predecessor checker's W01 (:127–132, :381) and `sr_refs` (:398–410).

---

## BLOCKERS

**B1. The binding cross-ref re-read (the B1 repair itself) reads K1/K2-K3/K4/P5Y from three remembered branch
names. A K1, K4 or P5Y state recorded on any other ref — which is how this repository records these transitions —
is invisible to the mandated re-reads, and "ambiguous ⇒ STOP" is absent. The protocol therefore cannot force the
correction that the predecessor's B1 was rejected for lacking.**

What is frozen:
* Checker :144–155 hard-codes `K1_REF = "refs/heads/p5y-k1-successor-final-assembly"`,
  `K2K3_REF = "refs/heads/p5y-k2-k3-final-closure"`, `K4_REF = "refs/heads/p5y-k4r1-final-closure"`.
  `xref_snapshot` (:591–610) reads XB1–XB4 only at those refs. `INFORMATIONAL_REFS` (:159–165) is a fixed list, so the
  re-read file does not even show that a new ref exists.
* The only all-ref scans are XB5 (SR-K5 spellings, two status-file blobs) and XB6 (`K5_CLOSED_REGEX`,
  `P5Y_CLOSED_REGEX`, `*COVERAGE_MAP_R6*` paths). Neither looks for K1/K4 states, or for a P5Y state that differs in
  any way other than "closed".
* Protocol §5.1 :127–130: INCOMPATIBLE is "any token change, a missing ref, a missing or unparseable artifact, or any
  XB5/XB6 finding". There is no ambiguity class (no occurrence of "ambig" in the protocol or checker), and the checker
  never compares the re-read with `XREF_SNAPSHOT_R1.json` or enumerates refs that are not in its list.
* §13 step 4 :320–321 makes the adjudication's K1/K4/P5Y/SR rows "taken from the step-3 re-read"; §14 (E) :354–355
  puts "K1 and K4 as recorded at the re-read tips" into the publication.

Why this is the predecessor's failure class, and why it is realistic here:
* The authorization requires reconstruction from current ref tips, "never remembered commit ids or branch names",
  and binding re-reads where "incompatible/ambiguous -> STOP". The predecessor review's repair (591b4394 :135–136)
  asked either for a P5Y row re-derived "from all refs" at adjudication time or for a STOP "if any obligation's
  recorded state differs from the frozen text". R1 implements neither for a record on a new ref.
* Every P5Y status transition today arrived on a **newly created** ref (reflogs above): K2/K3 on
  `p5y-k2-k3-final-closure` (created 15:01:25); K4 NOT_CLOSED on `p5y-k4-frozen-execution-r1` (created 15:16:57);
  K4 CLOSED on `p5y-k4r1-final-closure` (created 22:12:38). Had a re-read been pinned at 16:00 to the then-current
  K4 ref `p5y-k4-frozen-execution-r1`, a re-read after 22:13 would have returned identical tokens (NOT_CLOSED) and been
  classed COMPATIBLE while K4's recorded state had changed on a new ref. That is exactly the e88a2885 fact the
  predecessor review cited against 08e9acd1.
* Concretely, R1 does not STOP, and records stale rows, if before adjudication or publication any of these land on a
  ref other than the three: a review or re-adjudication of the K4R1 or K1 successor verdict (e88a2885's own notes say
  "no human review"; the K5 line routinely follows adjudications with a separate adjudication review); a P5Y-level
  assembly or status record whose `P5Y_STATE` changes K1–K4 or states K5 in a non-"closed" form; a K5 coverage map
  named other than `*COVERAGE_MAP_R6*`.

What does **not** change: at the freeze, the snapshot is correct. I re-derived every row independently (points 3–5).
B1 concerns the forcing mechanism that must keep those rows true until adjudication and publication. After this
review the checker cannot be amended (protocol :4).

**B2. The repaired wording scan (W01/T01) weakens the prohibition, contrary to the authorization's explicit
"without weakening the prohibition". Positive assertions that the predecessor's W01 rejected now pass, including in
the hard-wrapped format this namespace uses.**

Mechanism (checker :324–367):
* `CLAUSE_SPLIT` splits at every newline (`[.;:!?\n]`). The predecessor collapsed whitespace first (`re.sub(r"\s+",
  " ", v)`, :381). A banned phrase that straddles a line wrap is no longer seen.
* A match is allowed if **any** negation cue occurs **anywhere earlier in the clause**. Commas split only before
  and/but/while/whereas/so, so an unrelated "no"/"not"/"nothing"/"none" earlier in the sentence licenses the assertion.
* "all routes exhausted" (a predecessor phrase) was dropped: the new regex requires "are" or "have been".

My probe (re-implementation reproduces T01 exactly; "pred" = predecessor substring list):

| probe sentence (positive assertion; must be caught) | R1 W01 | pred |
|---|---|---|
| "K5 is not closed, H3a is established for m = 1." | **passes** | caught |
| "With no certified counterexample, H3a holds for m = 1, 2, 3." | **passes** | caught |
| "Since none of the routes succeeded, cell 309 is unclosable." | **passes** | caught |
| "Nothing remains open, K5 is closed." | **passes** | caught |
| "The adjudication finds that H3a is⏎established for m = 1, 2, 3." (line wrap at ⏎) | **passes** | caught |
| "Under the current framework cell 309 is⏎unclosable." | **passes** | caught |
| "All routes exhausted." | **passes** | caught |
| "No further campaign is needed because all routes have been exhausted." | **passes** | passes |

* The first row is the protocol's own must-fail example (§12 :300, "K5 is not closed, and H3a is established")
  with "and" removed. The last row is the exhaustion claim point 18 exists to prevent; R1's regex covers "have been
  exhausted" but the leading "No" licenses it.
* All 23 fixtures are single-line, and none has a comma without a conjunction, so T01 cannot detect either hole.
* The namespace writes hard-wrapped Markdown (the R1 protocol has 146 lines of 100+ characters that end
  mid-sentence; the R1 README has 5). P-A and P-E are namespace documents, so a wrapped banned phrase is the expected
  case, not a contrivance.
* The false-positive repair also holds only on a single line: "This closeout is not a statement that⏎309 is
  unclosable." and "Unresolved cells are not⏎evidence against H3a." are still rejected (fail-closed; N9).

Why blocking: the authorization made non-weakening a condition of the N6 repair. The repair matrix (§0 N6 row) and
§12 :295–300 present the scan as the repair, and the frozen checker cannot be changed. The fresh
publication-conformance check (§13 step 7) is a useful second layer. It is not the mechanical, non-weakened scan the
authorization asked for.

---

## NOTES (non-blocking)

**N1. No mechanical post-freeze immutability.** P01 compares against BASE 591b4394 and allows the five freeze files
in every phase. H01's `HISTORICAL_PATHS` excludes the R1 namespace. An edit to the protocol, checker or snapshot
after dfcd8f79 therefore passes every check. Line 3's "its hash is recorded by the freeze review" is the only guard;
the blob ids are in the reviewer-context section above.

**N2. Drift is not classified mechanically.** The re-read never loads `XREF_SNAPSHOT_R1.json`, so
COMPATIBLE_DRIFT (§5.1) is a manual comparison of tip ids. An unparseable artifact makes `json.loads` raise (:573):
the checker crashes with no output instead of recording INCOMPATIBLE. This fails closed.

**N3. XB6 is narrow.**
* `"P5Y": *"CLOSED"` requires the exact value, so `"P5Y": "CLOSED_BY_…"` is missed (the K5 alternative has no
  closing quote).
* Prose "K5 CLOSED ·" (the K4R1 README :41 style) is excluded by design.
* `K5_COVERAGE_COMPLETE = true/YES` and `K5_STATUS (CUSUM) = CLOSED` in a new file are not covered.
* A coverage map is caught only by the literal `COVERAGE_MAP_R6` name.

These are part of the new-ref gap in B1.

**N4. "All refs" means refs/heads, refs/remotes and refs/tags** (126 of 134). The 3 governance refs are checked by
G01. The 5 `refs/codex/turn-diffs/checkpoints/*` refs point at tree objects, which `git log --all` skips. I
inspected them: none contains `K5_STATUS.md`, the readiness audit, SR-K5 text, `K5_DECLARED_CLOSED` or `P5Y_STATE`.
Tree 41e4fa3f carries a K1 `FINAL_ADJUDICATION.json` whose blob (09011923) is identical to 7d5cf02b's. The commit
message's "all 126 refs" is accurate in that sense.

**N5. Scope of "the only remaining open P5Y obligation".** The ref record supports it for the K-obligations of
`P5Y_STATE` (K1–K4 closed, K5 OPEN). The P5Y DAG also lists T8, T9/T10, G.NOV and G.L4 (`P5Y_POST_K1_DAG.md`
:74–77); T8 depends on K4 only and has no recorded state. §5 hedges ("relevant to this closeout"); §8 :241–242 does
not. Better: "the only open one of K1–K5 as recorded in `P5Y_STATE`".

**N6. Stale public text stays beside the additive update.** On this branch, `docs/research_synthesis/README.md` :160
reads "K1 is NOT_CLOSED." (and :158 PS1 "NOT_CLOSED"), and root `README.md` :134 reads "NOT_CLOSED". P02 forbids
editing those lines, so the publication (E) must say explicitly that they are superseded by the records at the
re-read tips. Otherwise the public files will contradict themselves.

**N7. XB2 binds only the countersignature tokens** (`K2`/`K3` = PASS), not the `status`/`final_status` CLOSED
fields reported in the §5 row. Those are bound indirectly by XB4.

**N8. `K5_CLOSED` "CUSUM-scoped (repository usage: C11R adjudication :144)".** Line 144 uses the token ("N9_CLOSED
would not by itself have meant K5_CLOSED") without scoping it. The CUSUM scope is the protocol's own definition, and
the text should say so. The distinction from `K5_DECLARED_CLOSED` is correct.

**N9. W01 still rejects some correct text** (fail-closed): wrapped negations (B2), and correct scoped statements such
as "308 cannot be closed by improving A1 and A2 alone at the certified A0" (C3 :350's knockout fact).

**N10. P01 lists ignored files anywhere in the worktree** (`--ignored --untracked-files=all` over the whole repo).
A stray `.DS_Store` or `__pycache__` anywhere fails the phase. This fails closed and is a nuisance only.

**N11. §11 "(i) SR K1 records — now satisfied in substance".** This is an inference, not a record. It is defensible:
the K1 successor adjudication covers SR (`sr_bridge` 6/6, `historical_sr_ps1` 369/369), and K4R1 assembled SR on
(0, 2] from K1 records. It should be worded as an inference.

---

## 1. Predecessor rejection preserved

✓.
* §0 :14–22 names 08e9acd1 as REJECTED and 591b4394 as authoritative, quoting line 2 `CLOSEOUT_FREEZE_REJECTED`.
* It states that no adjudication, publication or science occurred under the predecessor. The predecessor namespace
  holds only the 5 freeze files plus the review, and no public file changed.
* R1 is a new prospective repair in a new namespace. H01 covers the predecessor namespace (byte-identical to base,
  verified). H02 pins its verdict token.

## 2. B1 repaired

**Partly.**
* The facts are repaired: §5 is correct as of the freeze, and SR K1 is no longer "unadjudicated".
* §14 is refreshed: the K4 history row matches the reflog.
* The forcing mechanism is not: the binding re-reads are keyed to remembered branch names, with no new-ref or
  ambiguity detection. See blocker B1.

## 3. Current K1 ref tip read correctly

✓. 7d5cf02b (14:25:06), also on origin. `FINAL_ADJUDICATION.json` :29–31 records `K1_SUCCESSOR_CLOSED`,
`CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN`, `NONE`; :13–14 CUSUM/SR successor science PASS; :48–50 historical PARTIAL. SR K1
is covered by `sr_bridge` 6/6 and `historical_sr_ps1` 369/369 (:37–39). XB1 matches.

## 4. Current K4 ref tip read correctly

✓. e88a2885 (22:13:19), on a ref created at 22:12:38. `K4R1_FINAL_VERDICT.json` :37–40 records CLOSED /
CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN / NONE; :3–5 historical NOT_CLOSED at bc4ba08e is preserved. The history row
(b5b4c917 reflog; candidate 5d33363c rejected at r4, JSON :15) is correct.

## 5. P5Y obligation statement

✓, with a scoping note (N5).
* `P5Y_STATE` at :51–57 reads K1 and K4 CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN, K2/K3 CLOSED, K5 OPEN, P5Y
  NOT_YET_CLOSED. The README :41 matches.
* Nothing on any ref is newer (my `git grep` over recent tips).
* "K5 is the only remaining open P5Y obligation" holds for the K-obligations. It is not stronger than the refs if
  read that way.
* No P5Y verdict is issued (§8 :246–247).

## 6. Cross-ref drift policy

**Not sound (B1).**
* The Class A/B split and the informational/binding split are right, and comparing by state tokens is right.
* But the binding re-read covers three fixed refs, has no "ambiguous" class, and does not look at new refs.
* COMPATIBLE_DRIFT is not mechanically classified (N2).

## 7. SR K5 state correctly reconstructed

✓.
* `K5_STATUS.md` :52 NOT STARTED; one version (d212f0d5) on every carrying tip; readiness audit :13 (597c9b2d).
* XB5 (multi-spelling `-G`, which catches in-place edits; exemption by exact id or matched-file path) is clean.
* My broader `-G` found only the audit and closeout commits after 09-19.
* It is carried out of scope, not a CUSUM blocker, and not declared complete (§11 :286–288).

## 8. Missing SR order-3 prerequisite carried

✓.
* §11 :283–285 carries (ii) and cites `level4/closure_proofs/p5y_k1_sr_o9_aux3_successor/config/AUX3_SR_RECORD.json`
  (`AUX3_SR_FEASIBILITY_FAIL`, only commit 986e6173).
* H03 pins the exact K5_STATUS line.
* No SR order-3 producer appears on any ref since 09-11 (readiness :12 agrees).

## 9. PARTIAL / INCONCLUSIVE / OPEN mapping

✓. §6.1 cites the repository definitions first:
* OPEN = r5 `open_ranges` / `"K5": "OPEN"` (K4R1 JSON :56);
* PARTIAL = `K5_STATUS.md` :4–5, a coverage status;
* K5_INCONCLUSIVE = E01 :91, a CUSUM-K5 verdict.

It states their relation, keeps the levels separate, and excludes the historical P5/P5X/P5Y-K1 PARTIAL verdicts.

## 10. Wording-scan false positive repaired

**No; the prohibition is weakened (B2).**
* The single-line false positive is fixed.
* Wrapped negations are still rejected (N9).
* Positive assertions pass in three ways: after an unrelated earlier negation in the same clause, across a line
  wrap, and as "all routes exhausted".
* The fixtures cannot see any of these.

## 11. Publication allowlist enforced

✓.
* P01 checks every path changed since base (tracked, untracked and ignored, via `git diff --name-only BASE` plus
  `status --porcelain --ignored --untracked-files=all`) against an exact per-phase list that matches §13 :333–338.
* P02 enforces additive-only edits.
* P03 enforces a single pure-insertion hunk: between `## Current successor status (PS1)` (:124) and
  `## Limitations and negative results` (:141) in `README.md`, and appended at the end of the two docs files.
* Limits: N1 (the freeze files stay mutable against base) and N10.

## 12. N4.1–N4.9 retained

✓. Each is present:
* N4.1 §3;
* N4.2 §4 with L02 blob pins;
* N4.3 §6.2 :159, never applied per cell;
* N4.4 §8;
* N4.5 §7 :186, exact;
* N4.6 §7 :203–207, verbatim;
* N4.7 §9, seven rows matching r1 §9's DEFER / INSUFFICIENT_EVIDENCE rows, with R4 HIGH;
* N4.8 "current authoritative" (7×), with no "final coverage map";
* N4.9 §11.

Predecessor notes N1, N3, N4, N5, N7, N8 and N9 are repaired. N2 is repaired by XB5. N6 is repaired except for W01
(B2).

## 13. 306–309 wording correctly scoped (citation spot-checks)

| # | protocol claim | checked at | result |
|---|---|---|---|
| 1 | K5 object: CUSUM cells 0–309 meeting (0, 2] | E01 `K5_TARGET_AND_THIRD_ORDER.md` :89 | ✓ |
| 2 | rule "otherwise unresolved cells ⇒ K5_INCONCLUSIVE" | E01 :91 | ✓ verbatim |
| 3 | Γ(5, 306; S_I1) = −0.030469257709306738 | C2 adjudication :47 | ✓ |
| 4 | C2 D4 at 307: Γ positive | C2 :48 | ✓ |
| 5 | F2: ×1.25 → +0.029163293; uniform-A margin 1.1277; F2 fails for 306 | C2 :65, :476, :478 | ✓ |
| 6 | Γ(5, 306; S_I2) = +0.005159101140006536, sealed once at 276f4d41 | result JSON :129; adjudication :225; `git show --stat 276f4d41` (1 file) | ✓ |
| 7 | EXECUTION_ACCEPTED 1173670f; CELL306_NOT_ADOPTED 9c2cbf21; ADJUDICATION_ACCEPTED c5324a78 | line 2 of each file; `git log` | ✓ |
| 8 | base TRUE; F1′ (a)–(c) TRUE, (d) FALSE; F2 FALSE | C12-R2 adjudication :363–369 (HOLDS ×4, FAILS), :400 | ✓ |
| 9 | N9 CLOSED 7d67989d; ADJUDICATION_ACCEPTED fb237288 | line 2 of each; `--diff-filter=A` | ✓ |
| 10 | 307: C3 D′ mixed supply Γ positive; knockout closes, so A0 is not the blocker | C3 :349; C4 :288–290 | ✓ |
| 11 | 308: knockout A1 = A2 = 0 leaves Γ = +0.039568 | C3 :350 | ✓ |
| 12 | 308: C4 Condition 3 (4.311; 18.2×; 4.375229; "nothing licenses …") | C4 :534–537 | ✓ word for word |
| 13 | 308: "operator-level route not excluded", not "cannot be excluded"; 2,000,000 paths, ~65 SE | C4 :510–512 | ✓ |
| 14 | 308 attribution: Condition 2 bars "the honest answer is that none can" and the `E[tau] < infinity (Lemma T)` citation | C4 :527–532 | ✓ (predecessor N4 repaired) |
| 15 | 309: Condition 1 scope wording | C4 :522–523 (sentence ends :525) | ✓ |
| 16 | 309: "not a statement that 309 is unclosable" | C4 :503 | ✓ |
| 17 | Λ₃₀₉ ≥ 3.586306094; C7 ACCEPTED_WITH_CONDITIONS | C7 README :15, :144 | ✓ |
| 18 | C5-T ceiling 3.266416; 9.79 % | C8 adjudication :348, :382, :486 | ✓ |
| 19 | C9 α 1.098807×–1.137406×; EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION | C9 README :3, :37, :39; STOP_RECORD :3 | ✓ |
| 20 | C8 factors COUNTERFACTUAL_ONLY; C5-T clause | C8 README :43, :87 | ✓ |
| 21 | F1′ unavailable for 307; freeze-before-recompute | floor r2 spec :193, :202–203 | ✓ |
| 22 | limb 1 does not fire: FIRST_CELL_SUPPORTED_ALL_M, ADOPTED | first-probe RESULT.md :7–8, :14–16 | ✓ |
| 23 | C1 MARGINAL (stopped before freeze); Campaign B MARGINAL / INFEASIBLE; C11 EXECUTION_INVALID (single-e, 307) | C1 README :11, :14, :24–30; Campaign B README :16, :26–28; C11 README :3, :106–112 | ✓ |
| 24 | K5-B sufficient-only; H3a counterexample standard | `K5_GLOBAL_BRIDGE.md` :18, :61; countersignature README :236–238, :20 | ✓ |
| 25 | K5 upstream of T9/T10 and L4 | DAG :60, :75, :97–102 | ✓ (N5) |
| 26 | seven deferred directions and labels | route audit r1 §9 :580–597 | ✓ |

Scoping:
* 306 is OPEN / NOT ADOPTED with four coexisting facts, not collapsed.
* 307 is OPEN; the N4.5 sentence is exact; UNKNOWN is kept; C9/C8 are not load-bearing.
* 308 is OPEN with C4 Condition 3 verbatim; the MC evidence is reported and not authoritative.
* 309 is OPEN, refuted within Condition 1's scope only, with UNKNOWN outside that scope.
* `K5_INCONCLUSIVE` is never applied per cell.

## 14. H3a consequence

✓.
* §8 :232–240: an unresolved or failed cell is not by itself evidence against H3a, citing README :236–238 correctly.
* A counterexample is kept distinct from the inability to certify a sufficient condition.
* No support is claimed, even for m ∈ {1, 2, 3}.
* K5-B is sufficient-only.

W01 enforcement is weakened (B2).

## 15. r5 authoritative

✓. §10: blob `f978eeb6b41188eabaf3c6d590c9178d711f1ce6` at HEAD (last touched ae4cbc2c). `K5_COVERAGE_COMPLETE`
false; m = 5 open `[[306, 309]]`; m = 1, 2, 3 open `[]`; union `[[306, 309]]`. Enforced by C01/C02.

## 16. No r6

✓.
* No step writes coverage (§10 STOP; §16).
* C03 finds nothing in the worktree.
* `git log --all --diff-filter=A -- '*COVERAGE_MAP_R6*' '*coverage_map_r6*'` is empty.
* XB6 finds no r6 path.
* Path-name limit: N3.

## 17. No new science

✓.
* The freeze diff is 5 document/admin files.
* The checker is administrative (reviewer context).
* The governance refs are exactly as pinned (G01); no new `refs/c12*`, `refs/c11rd*`.
* No new result file exists.
* The Γ 306/307/308/309 = 0/0/0/0 declaration is uncontradicted.
* §2, §4 and §9 reintroduce no prospective campaign.

## 18. Future research not falsely declared exhausted

✓ in text:
* §9 marks the seven directions optional, "neither failed nor completed", and reopenable under fresh
  authorization.
* §12 :292–293 says the closeout "bars no separately authorized research".
* §14 (G) requires the same.

Mechanical enforcement of the no-exhaustion rule is weakened (B2: "No further campaign is needed because all routes
have been exhausted." and "All routes exhausted." both pass W01).

---

## What would change the verdict

**To CLOSEOUT_FREEZE_ACCEPTED (on a successor freeze R2; nothing in this round):**
* **B1.** Make the binding re-read independent of remembered branch names.
  * Enumerate every ref (`for-each-ref`, including non-commit refs, reported separately).
  * Diff the ref set and tips against the frozen snapshot.
  * For every new ref or moved tip, search the commits reachable from it but not from the snapshot's tips for
    P5Y-status carriers: `P5Y_STATE`, K1/K4/K5/P5Y status assignments in JSON and prose forms, `*FINAL_VERDICT*` /
    `*FINAL_ADJUDICATION*` / coverage-map paths.
  * Classify an unexplained hit as AMBIGUOUS ⇒ STOP, and record COMPATIBLE_DRIFT mechanically against the snapshot.
  * Alternatively, make K1/K4/P5Y rows non-binding and require the adjudicator to re-derive them from all refs with
    the ref list printed.
* **B2.** Make W01 at least as strict as the predecessor on every input.
  * Collapse whitespace before splitting.
  * Let a negation cue license a match only when it governs it: the nearest cue within a short window immediately
    before the match, with no intervening comma or subordinator.
  * Restore "all routes exhausted".
  * Add fixtures for wrapped lines, comma-without-conjunction, and every predecessor-banned phrase in a positive
    sentence, plus a monotonicity test against the predecessor list.
* Optionally address N1–N11. N1 (a post-freeze identity check of the five freeze files) and N6 (explicit
  supersession of the stale public K1 lines) are the most useful.

With those and no new defect, I would accept. The cell dispositions, vocabulary, H3a handling, r5/no-r6, SR K5
treatment and N4.1–N4.9 are sound as frozen.

**This review would be wrong if:**
* the authorization intended "never … branch names" to forbid only *inferring state from a name*, not *locating the
  record by a remembered name*, and accepted a fixed-ref re-read. The quoted "incompatible/ambiguous -> STOP" points
  the other way, and so does the predecessor review's "from all refs";
* or the authorization's "without weakening the prohibition" meant only "do not remove banned categories", not
  "do not let previously rejected positive assertions pass". My probe shows both: a dropped phrase and new passes.
