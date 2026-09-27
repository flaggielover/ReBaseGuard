# Independent freeze review — K5 PARTIAL closeout protocol
CLOSEOUT_FREEZE_REJECTED

## Reviewer context

* Fresh context, read-only, adversarial. I had no part in C1–C12-R2, floor r2, route audit r0/r1, their reviews,
  or the closeout draft or freeze.
* Target: worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, branch `p5y-k5-tail-c11rd-d1d2-extension`, HEAD
  08e9acd176aea4351425c169d2eac723d0a2208b (the freeze commit, 2026-09-27 22:02:20 +0900). Tree clean, including
  ignored files (`git status --porcelain --ignored` is empty).
* Frozen files reviewed in full:
  * `level4/closure_proofs/p5y_k5_partial_closeout/protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL.md` (515 lines);
  * `level4/closure_proofs/p5y_k5_partial_closeout/code/closeout_checks.py` (431 lines);
  * `level4/closure_proofs/p5y_k5_partial_closeout/README.md`;
  * `level4/closure_proofs/p5y_k5_partial_closeout/evidence/PREFREEZE_CHECKS.json` and `evidence/SR_K5_REFS.json`.
* I modified, created or deleted nothing in either repository. The only files I wrote are in my scratch directory
  (this review, the two checker outputs, and three code-text extracts of the scan helpers used for a `diff`; they
  contain no value).
* **Code run.** Only the frozen checker, and only after reading its whole source and confirming it imports nothing
  but the standard library, uses only read-only git subcommands, parses (never imports or executes)
  `c11rd_validate.py`, and prints only counts and names:
  * `python3 -I -S -B …/closeout_checks.py --phase freeze --out <scratch>/freeze_checks.json` → **23/23 PASS**,
    exit 0, head 08e9acd1, `files_scanned` 6, 0 original / 0 independent hits, decoys fire correctly.
  * `python3 -I -S -B …/closeout_checks.py --sr-refs --out <scratch>/sr_refs.json` → **pass**, 126 refs scanned,
    `unexpected` empty; the listed commits are now the four in the committed evidence plus the freeze commit itself.
  * By design the checker loads the original hash set and the independent D1/D2 values into its own process memory to
    build hash sets. I saw no value; its output carries counts only.
* No other repository code run: no campaign producer, certifier, verifier, driver or module, and not the
  research-synthesis verifier.
* No Γ, margin, factor, bisection, knockout or Λ bound computed, and no arithmetic on any TCT input, registry or
  certificate. I did not recompute any percentage; every figure below is quoted from the line cited.
* I opened nothing under the C11R quarantine directory. My `git log -S/-G` searches and the checker's `C03` filename
  walk traverse the object store and the file tree internally; they print only commit subjects or file names. No
  D1/D2 value was written or echoed. No session transcript read. No network, AWS or Vultr contact.
* **Incidental exposure (disclosed, used in no computation).** Committed 306–309 numbers at: C2 adjudication
  :40–70, :462–510; C3 adjudication :340–356; C3 open-notes disposition :18–26; C4 adjudication :284–292, :498–560;
  C9 README :25–46; C12-R2 adjudication :1–6, :375–402 and grep hits; C8 adjudication grep hits (:51, :148, :348,
  :352, :382, :384, :486); C7 README grep hits; route audit r1 :194–310, :578–631.

## What I checked (files, lines, commands)

* **Freeze scope.** `git show --stat 08e9acd1` and `git diff --stat 2f36352e 08e9acd1`: exactly 5 added files, all
  in the closeout namespace, 1151 insertions, 0 deletions. The draft `PROPOSED_K5_PARTIAL_CLOSEOUT_DRAFT.md` has the
  same blob at 4a4b1392, 2f36352e and HEAD (64e985f6), i.e. unedited.
* **The r1 review** `level4/closure_proofs/p5y_k5_tail_route_audit/review/ROUTE_AUDIT_R1_REVIEW.md` in full (N1–N7,
  the N4 items 1–9, points 0–12, conditions of acceptance), the draft in full, route audit r1 §4, §9, §10.
* **Every citation in §5–§8 and §10** at the cited lines (table in point 4).
* **Vocabulary.** `git grep` over HEAD for `K5_CLOSED`, `K5_DECLARED_CLOSED`, `K5_INCONCLUSIVE`, `H3a holds` /
  `established`; E01 :59–61, :89, :91.
* **r5.** Blob `f978eeb6…` at HEAD; key names only, then `K5_COVERAGE_COMPLETE`, `open_ranges`,
  `union_open_ranges`, `c2_adjudication_verdict`.
* **Checker.** Full source; the hashed-scan helpers diffed against blob 9a55edf1 (`c11rd_qualify.py` :1252–1303) and
  `value_patterns` against blob e536605b :282–292; the `ORIGINAL_PATTERN_SHA256` literal located in blob 22293e05417132b4 at :728; all four
  pinned blobs verified with `git ls-tree`. `verify_synthesis.py` blob at HEAD and at base = d2411ab8 (imports:
  argparse, json, re, subprocess, sys, pathlib; document checks only).
* **Cross-ref state.** `git for-each-ref --sort=-committerdate`, `git reflog show` of the K1, K2/K3, K4 and K4R1
  refs, `git show` of 7d5cf02b, df703837, bc4ba08e, b5b4c917, e88a2885, da79fe1f;
  `git log --all --since=2026-09-18 -G 'K5'`; `git log --all --since=2026-09-12 -G` for SR/PS1-near-K5 spellings;
  ancestry of every `refs/heads/*k5*` tip against HEAD.

---

## BLOCKERS

**B1. The frozen protocol states, as verified fact, a cross-ref K1 / P5Y state that was false at the freeze.
N4.4 (P5Y consequence) and N4.9 (SR K5 across all refs, stale rationale) are therefore implemented against a false
record, and the text cannot now be corrected.**

What the frozen text says:
* §10 :380–381: "The latest SR K1 artifact on another ref, da79fe1f (ref `p5y-k1-successor-final-assembly`),
  states 'READY for independent adjudication; K1 not decided'."
* §10 :382: "SR K1 records now exist, unadjudicated."
* §7 :314–319: the recorded P5Y state is `K5_STATUS.md` :45–58 (2026-09-19), "P5Y final assembly waits on SR K1, SR K5
  and CUSUM K5", and "Its P5Y dependency structure is not superseded"; :325–326 "K1, K4 and SR K5 are carried as
  last recorded."

What the repository recorded **before** the freeze (22:02:20 +0900):
* **Same ref as cited.** `refs/heads/p5y-k1-successor-final-assembly` moved da79fe1f → **7d5cf02b** at
  2026-09-27 14:25:06 +0900 (reflog "commit: level4: close P5Y K1 line by successor adjudication"), more than seven hours
  before the freeze. Also on `refs/remotes/origin/…`. Its file
  level4/closure_proofs/p5y_k1_successor_final_adjudication/evidence/FINAL_ADJUDICATION.json records at :29–31
  `"k1_successor_verdict": "K1_SUCCESSOR_CLOSED"`, `"k1_scientific_line": "CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN"`,
  `"residual_blockers": "NONE"`, and at :14 `"sr_successor_science": "PASS"`. Its README calls it "the independent
  final adjudication of the additive assembly at da79fe1f…".
* **df703837** (15:03:06, ref `p5y-k2-k3-final-closure`), level4/closure_proofs/p5y_k2_k3_final_countersignature/
  FINAL_COUNTERSIGNATURE.json :108–110: `"K4": "OPEN"`, `"K5": "OPEN"`, `"P5Y": "K2_K3_CLOSED_K4_K5_OPEN"`.
* **bc4ba08e** (15:44:32, ref `p5y-k4-frozen-execution-r1`), level4/closure_proofs/p5y_k4_frozen_execution_r1/
  README.md :65: "K1 = CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN   K2 = CLOSED   K3 = CLOSED   K4 = OPEN   K5 = OPEN
  P5Y = NOT_YET_CLOSED".
* **After** the freeze, e88a2885 (22:13:19, ref `p5y-k4r1-final-closure`, pushed to origin 22:19:54),
  level4/closure_proofs/p5y_k4r1_final_adjudication/README.md :41: "K1 CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN · K2 CLOSED
  · K3 CLOSED · K4 CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN · K5 OPEN · P5Y NOT_YET_CLOSED".

So at the freeze, da79fe1f was not the latest SR K1 artifact on its own ref; SR K1 had been adjudicated
(`K1_SUCCESSOR_CLOSED`, SR science PASS); and three committed records on other refs said K1 was closed. By the time
the adjudication runs, every P5Y obligation except K5 is recorded closed. The quote attributed to da79fe1f is literal
(its subject line), but calling it "latest" and SR K1 "unadjudicated" is false.

Why this blocks rather than being a note:
* **It is an N4 repair implemented wrongly.** The r1 review's N4.4 asked for the P5Y consequence precisely because
  "the user authorizing 'final' should see it". N4.9 asked that the SR K5 re-check span all refs and "record that the
  'needs SR K1 records' rationale may be stale". The frozen §7/§10 show the user a P5Y picture (P5Y waiting on SR K1,
  SR K5 and CUSUM K5, with SR K1 undecided) that no longer existed. The accurate picture at adjudication time is that
  K5 (SR K5 NOT STARTED, CUSUM K5 unresolved) is the only open P5Y obligation. That is the consequence of a "final"
  K5 closeout that N4.4 exists to surface, and it is materially different.
* **It is a false citation in governing text** (a category the authorization lists as blocking). §10 labels it
  "Verified before freeze". Unlike §5's reconstruction, it is not marked non-binding.
* **Nothing in the frozen chain forces a correction.** §10's STOP fires only on "a contradictory SR K5 state". A K1
  closure is not an SR K5 state. The frozen `--sr-refs` pickaxe only searches the literal text `SR K5`, so it cannot
  see it (7d5cf02b does not contain that text). The required adjudication table (§12 step 3) has no K1 or P5Y row.
  Publication (§12 step 5) is by the author from the adjudication, with no independent review. P-A's
  "evidence/provenance table" and P-B/P-C/P-D's status sections are exactly where §7/§10 would be restated. After this
  review nothing in the protocol may be edited (:6), so an ACCEPT would freeze the false statement into the governing
  record.
* **The same defect recurs in §14.** It records `p5y-k4r1-nearzero-successor` as having moved "5d33363c → 93d82c87
  (… candidate r5 … no target evaluated)". The reflog shows it moved again to 8928b8f1 (FREEZE, 21:17:19) and to
  **b5b4c917** ("exactly-once execution result", 21:17:46), both about 45 min before the freeze. The r1 review N6 had
  flagged exactly this class of stale "recorded" ref value, and the protocol's repair table claims N6 as implemented
  (§0 :48).

What does **not** change: SR K5 is still NOT STARTED on every ref (see point 11), CUSUM K5 still yields
`K5_INCONCLUSIVE` under §5, and `P5Y_STATUS` is still not closed. B1 is about the correctness of what the frozen
text tells the adjudicator and the user, not about the CUSUM verdict.

Repair (successor freeze; nothing in this round):
* Restate §7/§10 from all refs as of the new freeze. For each record give ref, commit and governance status (N4.1):
  * K1 `CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN` (7d5cf02b);
  * K2/K3 CLOSED (df703837);
  * K4 as then recorded (bc4ba08e NOT_CLOSED; e88a2885 CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN);
  * P5Y NOT_YET_CLOSED;
  * SR K5 NOT STARTED, with **both** recorded prerequisites (see N3).
* Say explicitly that K5 is then the only open P5Y obligation.
* Replace "latest SR K1 artifact" with the actual latest record.
* Refresh §14.
* Either mark every cross-ref statement non-binding and require the adjudicator to re-derive a P5Y row from all refs at
  adjudication time, or add a STOP if any obligation's recorded state differs from the frozen text.

---

## NOTES (non-blocking)

**N1. The decision rule's non-E01 limbs.** E01 :91 defines only `K5_FAIL_MATHEMATICAL` (`R'''_cell.hi < 0` on a cell
containing 0) and `K5_INCONCLUSIVE`.
* Rule 1's second limb ("any other independently proved counterexample to H3a") and Rule 2's second limb ("an accepted
  adjudication has established the remaining K5-B premises") are judgment-based extensions.
* The mapping `K5_CLOSED` ↔ `K5_DECLARED_CLOSED = YES` conflates a CUSUM-only verdict with a flag the repository uses
  for K5 as a whole (for example `p5y_k5b_independent_countersignature/README.md` :20).
* Neither extension can fire here. Rule 2's first limb fails mechanically (r5 `K5_COVERAGE_COMPLETE` false), and no
  committed artifact asserts a counterexample. So the verdict still follows mechanically.
* `K5_CLOSED` is repository vocabulary (C11R adjudication :144, C11R comparison review :126–127) and is named in the
  authorization. Not a blocker.

**N2. The SR-refs method is weak, but its conclusion is right.**
* `git log --all -S 'SR K5'` counts occurrences, so an in-place status edit ("| SR K5 | NOT STARTED" → another status)
  is invisible to it.
* It matches one literal spelling. The readiness audit e8680998 speaks of "the SR half of K5" and
  `K5_SR_K1_INPUTS_EXIST` and is not listed.
* It pre-accepts every commit on this branch after c5324a78, so the closeout's own later commits are exempt from their
  own scan.
* I checked independently with `git log --all --since=2026-09-12 -G` for SR/PS1-near-K5 spellings and
  `git log --all --since=2026-09-18 -G 'K5'`. The only SR-K5-bearing commits are a3547b9b, e8680998 (an ancestor of
  HEAD, consistent with NOT STARTED), the route-audit commits and the freeze. The K4/K2-K3 records say only
  "K5 = OPEN". No ref shows SR K5 progress.

**N3. The SR K5 rationale is carried incompletely.** `K5_STATUS.md` :52 says "NOT STARTED: needs SR K1 records,
plus an SR order-3 producer (`AUX3_SR_FEASIBILITY_FAIL` on record)". §10 carries only the first clause. With SR K1
now closed, the second clause is what keeps SR K5 blocked, and it should be visible.

**N4. A misattribution inherited from r1 (§6 308, :254–255).** "C4 Condition 2 (:527–533) forbids quoting 'none can'
/ 'cannot be excluded'". Condition 2 bars "the honest answer is that none can" and the `E[tau] < infinity (Lemma T)`
sentence. "not 'cannot be excluded'" comes from C4's verdict text at :511–512. The substance (neither phrase
establishes anything) is right.

**N5. The pre-freeze reconstruction omits some negative history** that r1's dossiers list: C1 MARGINAL, Campaign B
MARGINAL/INFEASIBLE, and C11's failed corroboration for 307. Required publication wording (C) demands "negative
historical evidence visible". The adjudicator must add it (§3 allows it).

**N6. Publication controls are thin.**
* No independent review follows publication (§12 step 5).
* W01 is a phrase blocklist that paraphrase evades. For example, "H3a is supported" is not banned.
* It false-positives on a correct negated quote. §6's own 309 line ("not a statement that 309 is unclosable") contains
  the banned substring "is unclosable". This fails closed.
* P-B's placement is not checked.
* P-E, the namespace README, is not scanned by W01.
* P01 enforces "inside the namespace", not §13's exhaustive list. A new, unlisted file under the namespace would pass
  P01, and C03 catches only names containing `coverage_map_r6`.
* P01/H01 use `--exclude-standard`, so gitignored files are invisible. The tree is currently clean, including ignored
  files.

**N7. "Verbatim copies" is not byte-exact.** The helper bodies are code-identical to blob 9a55edf1, but docstrings and
one comment were stripped (my `diff`: 4 hunks, all docstring/comment/blank). `value_patterns` is code-identical to
blob e536605b except its docstring.

**N8. A wording conflict in §12.** "Every role below is a fresh, independent context, distinct from … the author" sits
against step 5, "Performed by the closeout author".

**N9. PARTIAL / INCONCLUSIVE / OPEN mapping.** The protocol never states how its CUSUM-level `K5_INCONCLUSIVE` relates
to the historical status word PARTIAL (`K5_STATUS.md` :50; a3547b9b) or to other refs' "K5 = OPEN". The
authorization's N4.3 is met, but the publication will juxtapose three vocabularies without a stated mapping.

---

## 1. N4.1–N4.9 implemented?

| item | r1-review requirement | protocol | verdict |
|---|---|---|---|
| N4.1 | licence to read any committed artifact, subject to the forbidden list | §3: any artifact on the branch at or before the freeze, plus other refs where SR K5/P5Y requires; status visible; uncertified evidence reportable only; forbidden list kept | ✓. Every `refs/heads/*k5*` tip except the stale `p5y-k5-order3-producer-design` is an ancestor of HEAD, so no K5 evidence is out of reach |
| N4.2 | resolve the P4 vs "no code" contradiction; bind the scanner | §4 separates administrative checks from forbidden science; only the frozen checker, the pinned synthesis verifier and git may run; hash-set sources pinned (L02) | ✓ |
| N4.3 | K5-level, not per-cell; name a CUSUM-level `K5_INCONCLUSIVE` if intended | §5: tokens from E01 plus `K5_CLOSED`; applied to CUSUM K5 only; per-cell use forbidden (:171–172); P5Y-wide K5 gets no verdict | ✓ (N1, N9) |
| N4.4 | P5Y consequence; countersignature failure semantics | §7: H3a rule verbatim-accurate to README :236–238; no support claimed; P5Y consequence stated | H3a part ✓. **P5Y part stated against a false cross-ref state (B1)** |
| N4.5 | "no route that closes 307 has been certified" | §6 :224, exact | ✓ |
| N4.6 | C4 Condition 3 counterpart plus the MC evidence | §6 :249–258 | ✓ (point 7) |
| N4.7 | list every DEFER/INSUFFICIENT_EVIDENCE row or state a rule; R4 carries N3 | §8: all seven directions; labels match r1 §9; R4 HIGH with the R_STAGE_DESIGN and Campaign B T2 evidence; optional, neither failed nor completed | ✓ |
| N4.8 | "current", not "final" | §11; no "final coverage map" or "final authoritative" anywhere in the namespace (grep); W01 bans the phrase | ✓ |
| N4.9 | SR K5 re-check across refs; record that the rationale may be stale | §10: pickaxe across refs; stale-rationale sentence; STOP if contradictory | SR K5 conclusion ✓ (N2). **The accompanying SR K1 fact is false at freeze (B1)**; rationale incomplete (N3) |

The other notes: N1a/N1c are carried in §8 :361–363 and :357–358, and N1b is visible in the §12 chain (a freeze plus
three reviews). N2a is at :351–352. N3 is in §8. N5 is at :353–354. N6: U2 at :355, E1 at :359–360; the K4 ref is
stale again (B1).

## 2. No prospective scientific route silently reintroduced

✓.
* §0 :27–30 fixes "no prospective K5 scientific expansion under present governance".
* Every route in §8 is DEFER or INSUFFICIENT_EVIDENCE, "reopened only under fresh, separately authorized, prospective
  protocols", with C2 Condition 1's freeze-before-recompute (:332–333).
* R-α, R-I2-alone, Floor-307 and X308 stay REJECTed as actions (:347–348).
* No step of §12 computes anything.
* §5(c) says "no currently justified prospective campaign is required before publication closeout". That is the
  governance-qualified reading the r1 review's point 12 required, not "no scientifically justified campaign remains".

## 3. No scientific computation occurred

✓.
* The freeze diff is 5 documentation/admin files, with no addition outside the namespace.
* `PREFREEZE_CHECKS.json` (head 2f36352e, phase prefreeze, 23/23) and my own freeze-phase run (head 08e9acd1, 23/23)
  agree. H01 finds historical namespaces byte-identical to 2f36352e. G01 finds the governance refs as pinned:
  `refs/c12r2/cell306-target-consumed` → dec92e09, `…pending-result` → 0ac46b3d, `refs/c11rd/r1-execution-consumed` →
  4b716d43. G02 finds the forensic objects present.
* The checker is administrative: stdlib only (`argparse, ast, hashlib, json, pathlib, re, subprocess, sys, fractions`);
  read-only git subcommands (`rev-parse, symbolic-ref, merge-base, for-each-ref, config --get, show, cat-file, diff,
  status, ls-files, log`); `ast.parse`, not import, of `c11rd_validate.py`. Fractions are used only to render
  scanned tokens for hashing. It reads no TCT input, registry or certificate into any calculation. Its only subprocess
  besides git is the synthesis verifier, in the publication phase.
* It can detect what it claims:
  * S/C/G/H/P checks are exact equality or ancestry tests;
  * L01 has working decoy controls and the 17-element original set;
  * R01 claims existence only, and checks existence only.
  * Limits are in N2 and N6.
* The freeze commit message declares Γ evaluations 306/307/308/309 = 0/0/0/0. Nothing contradicts it: no new result
  files, and no ref under `refs/c12r2/`, `refs/c11rd/`, `refs/c12r1/` or `refs/c12/` other than the pinned three.

## 4. Cell dispositions accurately scoped: citation spot checks

| # | protocol claim | checked at | result |
|---|---|---|---|
| 1 | K5 object: CUSUM cells 0–309 meeting (0, 2] | `K5_TARGET_AND_THIRD_ORDER.md` :89 | ✓ |
| 2 | E01 rule: FAIL_MATHEMATICAL / "otherwise unresolved cells ⇒ K5_INCONCLUSIVE" | same file :91 | ✓ verbatim |
| 3 | H3a non-refutation rule, "including cell 309 or the m = 5 tail" | countersignature README :236–238 | ✓ |
| 4 | Γ(5, 306; S_I1) = −0.030469257709306738 | C2 adjudication :47 | ✓ |
| 5 | C2 D4 supply: Γ positive at 307 | C2 adjudication :48 | ✓ |
| 6 | F2: Γ at ×1.25 = +0.029163293; uniform-A margin 1.1277 | C2 adjudication :65, :476, :478 | ✓ |
| 7 | Γ(5, 306; S_I2) = +0.005159101140006536, sealed once at 276f4d41 | C12-R2 result JSON :129; adjudication :225; `git show --stat 276f4d41` (1 file, the result JSON) | ✓ |
| 8 | EXECUTION_ACCEPTED (1173670f); CELL306_NOT_ADOPTED (9c2cbf21); ADJUDICATION_ACCEPTED (c5324a78) | line 2 of each file; `git log -1` of each | ✓ |
| 9 | base TRUE; F1′ (a)–(c) TRUE, (d) FALSE; F2 FALSE; control reproduces C2 | C12-R2 adjudication :381–400, :173–176, :409 | ✓ |
| 10 | N9 CLOSED (7d67989d); ADJUDICATION_ACCEPTED (fb237288) | line 2 of each file; `git show --stat` | ✓ |
| 11 | 307: C3 D′ mixed supply Γ positive; closes at A1 = A2 = 0, so A0 is not the blocker | C3 adjudication :349; C4 adjudication :288–289 | ✓ |
| 12 | 308: knockout A1 = A2 = 0 still leaves Γ = +0.039568 | C3 adjudication :350; C3-N4 at open-notes disposition :20–23 | ✓ |
| 13 | 308: C4 Condition 3 text | C4 adjudication :534–537 | ✓ (point 7) |
| 14 | 308: "operator-level route not excluded"; 2,000,000-path MC at ~65 SE | C4 adjudication :510–512 | ✓ (attribution: N4) |
| 15 | 309: Condition 1 scope wording | C4 adjudication :522–523 | ✓ verbatim |
| 16 | 309: "not a statement that … unclosable" | C4 adjudication :503 | ✓ |
| 17 | 309: Λ₃₀₉ ≥ 3.586306094; C7 ACCEPTED_WITH_CONDITIONS; ceiling 3.266416; 9.79 % | C7 README :15, :24, :112, :144; C8 adjudication :348, :382, :486 | ✓ (quoted, not recomputed) |
| 18 | 307: C9 α 1.098807–1.137406 uncertified; C9 EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION | C9 README :3, :37, :39; STOP_RECORD_C9 :3 | ✓ |
| 19 | C8 factors COUNTERFACTUAL_ONLY, C5-T clause | C8 README :43, :87 | ✓ |
| 20 | F1′ unavailable for 307; freeze-before-recompute | floor r2 spec :193, :202–203 | ✓ |
| 21 | Rule 1 does not fire: FIRST_CELL_SUPPORTED_ALL_M, ADOPTED | first-probe RESULT.md :7–8, :15, :65 | ✓ |
| 22 | Rule 2 does not fire: `K5_COVERAGE_COMPLETE` false; m = 5 open [[306, 309]] | r5 at HEAD, blob `f978eeb6…` | ✓ |
| 23 | K5-B sufficient-only | `K5_GLOBAL_BRIDGE.md` :18, :61 | ✓ |
| 24 | C8 erratum E1 "false premise"; U2 / C6 Condition 10 | `ERRATUM_C8_GATE.md` :6; open-notes disposition C6 :20 | ✓ |
| 25 | SR K5 NOT STARTED; P5Y waits; `P5Y_STATUS = NOT_CLOSED` | `K5_STATUS.md` :52, :55, :57; blob d212f0d5, last touched a3547b9b | ✓ as a 09-19 record; **stale as the current P5Y state (B1)** |
| 26 | "latest SR K1 artifact … da79fe1f … K1 not decided" | da79fe1f subject ✓; ref history ✗ | **✗ (B1)** |

Scoping: 306 is OPEN / NOT ADOPTED with four coexisting facts. 307, 308 and 309 are OPEN. 309's refutation is
confined to C4 Condition 1's scope. `K5_INCONCLUSIVE` is never applied per cell (:170–172). ✓.

## 5. 306 historical facts not rewritten

✓.
* All of these coexist in §6 :194–220 with their statuses: closure under I1 (C2, CI/EX), non-certification under I2
  ("non-certification, not disproof", :205), N9 CLOSED as a trust condition only (:210), floor r2 not met (base
  TRUE; F1′(d) FALSE; F2 FALSE from C2 §K), CELL306_NOT_ADOPTED, ADJUDICATION_ACCEPTED, EXECUTION_ACCEPTED.
* None is collapsed into a single word, and "306 failed" is banned in publication.
* H01/H02 confirm that every C12-R2, floor r2 and C11RD file is byte-identical and every pinned verdict token is
  present.
* Required wording (B) matches the C12-R2 determinations.

## 6. 307 preserves UNKNOWN space

✓.
* The N4.5 sentence is exact.
* The negative evidence is certified supplies evaluated and not closing (C2 :48, C3 :349).
* The blocker structure is (A1, A2), not A0.
* F1′ is unavailable.
* C9/C8 figures are "reported, not load-bearing".
* "UNKNOWN: every route not certified. No impossibility is claimed."
* Omitted history: N5.

## 7. 308 preserves C4 Condition 3

✓. The blockquote at §6 :250–252 reproduces C4 adjudication :534–537 word for word from "at `A0 = 4.311`" through
"nothing licenses "cell 308 is closable"". That covers the 18.2× on (A1, A2) at the MC value Λ₃₀₈ = 4.311, the
impossibility at A0 = 4.375229, and "C4-N3 stands and is binding". Only the instruction clause ("Strike 'one of them is
progress' (Phase 1 §5). Replace it with the quantified fact:") is omitted. Also carried:
* the verdict wording ("operator-level route not excluded");
* the MC evidence, explicitly "reported and NOT authoritative … not an exclusion";
* "No certified upper bound on Λ₃₀₈ exists" (consistent with C4 :511 and my grep);
* "nothing establishes '308 is not closable'".

Uncertified Monte-Carlo is never an exclusion (§3 :83–84, §6 :257–258).

## 8. 309 negative evidence not overgeneralized

✓.
* It is "refuted within scope only", in Condition 1's own words, including "the frozen measurement inputs and the
  frozen TC-T / K5-B consumer".
* C7 strengthens the in-scope margin only.
* C4 :503 is cited against generalization.
* UNKNOWN outside scope lists sup-norm, finer cover, real order-3, assembly/clause tightening, residual-specific routes
  and other theory.
* The disposition is OPEN.

## 9. H3a not rejected from failed cells; no overclaim of support

✓.
* §7 :296–305 states the rule with the countersignature citation, keeps "certified counterexample" (none in committed
  evidence) distinct from "inability to certify a sufficient condition", and cites K5-B as sufficient-only.
* §7 :307–310 asserts H3a for no (D, m), even for m ∈ {1, 2, 3} where r5 shows no open ranges, because no accepted
  artifact assembles the §10 premise list. My grep finds no committed "H3a holds for (CUSUM, m)" claim.
* W01 bans "h3a is false/refuted/proved/established/holds for" (limits: N6).

## 10. K5-level terminology

Essentially ✓.
* `K5_FAIL_MATHEMATICAL` and `K5_INCONCLUSIVE` are E01 :91 vocabulary.
* `K5_CLOSED` occurs in the repository (C11R) and is named in the authorization.
* The repository flag is `K5_DECLARED_CLOSED` (countersignature README :20; COUNTERSIGNATURE.json :28; the probe
  producer RESULT :121; the GammaTilde audit).
* No "failed" verdict is invented.
* The rule is ordered and prospective, and yields `K5_INCONCLUSIVE` mechanically on the r5 fact.
* Caveats: N1 (judgment-based extension limbs; flag conflation) and N9 (PARTIAL/OPEN mapping).

## 11. SR K5 out of scope; the all-refs check

The scope is ✓: SR K5 is carried as NOT STARTED, not adjudicated, and nothing is inferred from CUSUM (§1, §5 :174–178,
§10). There is a STOP on a contradictory SR K5 state (§10, §15).

`evidence/SR_K5_REFS.json` (122 refs; a3547b9b plus three route-audit commits; pass) is reproduced by my run (126 refs
now; the freeze commit is added, self-exempt).

The method is weak (N2). But I independently confirmed with broader `-G` searches over all refs that no ref records
SR K5 progress, so "NOT STARTED" is uncontradicted.

The check is **not** sound as a basis for the surrounding claims. §10's SR K1 statement is false at the freeze and the
rationale is incomplete (B1, N3).

## 12. Coverage mutation forbidden

✓.
* §0 :13, §9 :365–372 (STOP on any mutation), §13 ("No other file may change"), §15.
* Mechanically: C01 (r5 blob), C02 (open ranges and `K5_COVERAGE_COMPLETE` false), P01 (no change outside the
  namespace, plus three additive files in publication) and H01.
* Gap inside the namespace: N6.

## 13. r5 remains authoritative

✓. §5(d), §9 and §11 say "current authoritative coverage map". The r5 blob at HEAD is `f978eeb6b41188eabaf3c6d590c9178d711f1ce6`,
and the structural fields match r5 at the freeze.

## 14. No r6 can be generated by this protocol

✓.
* No step writes coverage.
* The only runnable code is the checker (read-only) and the synthesis verifier (document checks).
* C03 checks that no `coverage_map_r6`-named file exists, tracked or on disk.
* Any other-named coverage file inside the namespace is forbidden by §9/§13 text but not mechanically caught (N6).

## 15. Publication does not claim research exhausted; §13 constraints

✓ in text.
* §8 frames seven optional directions as neither failed nor completed.
* §11 and W01 ban "all routes exhausted", "mathematically final", "no route exists" and "final coverage map".
* §13 is an exhaustive five-artifact list, with root README and synthesis edits additive-only (P02 catches any
  deletion or modification).
* Required wording (A)–(E) is accurate.

The constraints are adequate in scope but weak in enforcement (N6). The most material publication risk is that P-A's
evidence/provenance table and the P-B/P-C/P-D status sections would restate the false §7/§10 cross-ref facts (B1),
with no reviewer after publication.

---

## What would change the verdict

**To CLOSEOUT_FREEZE_ACCEPTED (on a successor freeze):**
* §7 and §10 restated from all refs as of that freeze, with ref, commit and status for K1 (7d5cf02b), K2/K3
  (df703837), K4 (bc4ba08e, and e88a2885 if present), P5Y NOT_YET_CLOSED and SR K5 NOT STARTED (both recorded
  prerequisites, N3).
* An explicit statement that K5 is then the only open P5Y obligation.
* §14 refreshed.
* Either all cross-ref statements marked non-binding with a required re-derivation at adjudication time, or a STOP if
  any P5Y obligation's recorded state differs from the frozen text.

With that and no new defect, I would accept. N1–N9 would be welcome but not required.

**This review would be wrong if:**
* 7d5cf02b, df703837 and bc4ba08e were not in this repository at 22:02:20 +0900. The reflogs I read say they were,
  at 14:25:06, 15:03:06 and 15:44:32 respectively.
* Or the authorization explicitly defined the P5Y consequence as the 2026-09-19 `K5_STATUS.md` record, not the
  current cross-ref state. I have not seen the authorization text. The r1 review's N4.4/N4.9 language points the
  other way.
