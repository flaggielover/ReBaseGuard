# Reader re-check (MBS-10): governance/USER_DECISION_BRIEF_308_SUCCESSOR.md revision r1 with section G, fresh non-holder reader readerUDB
NO_OUTCOME_EXPECTATION

## Scope and reader status

* Reader: readerUDB, the same fresh non-holder as `reviews/READER_CHECK_USER_DECISION_BRIEF_308.md`. I have still
  not seen any observation of the MB308 r1 target run beyond what this brief itself now states (see R-1, R-2).
* Read, and nothing else in the research or formal namespaces (checked 2026-09-29T21:18Z; no git commands used):
  * the brief, working-tree file (r1 plus the uncommitted §G), 268 lines, sha256
    `47e3a192c03645e20519b707655c7d78dd55374f8b9109570e95613e3e3bb3fa`;
  * `governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md`, sha256 `c170c726…ee152c` (unchanged since my first check);
  * `ledger/USER_TEXTS_SUCCESSOR_308.md`, sha256 `16f0efcc…99f3dffe` (unchanged since my first check).
* I read the whole current file, including the new text in A.1–A.4, B.6, E, F and G. I did no scientific
  computation and no git writes. The only tools I used were `sed`/`diff`, `grep` and `shasum`.

## 1. Outcome expectation: none found

The whole file contains no margin, estimate or likelihood of MB-S closing cell 308, no hint of how close anything is,
and no "worth running" argument from cell 308's structure. None of the new text states any of these.
* The A.4 table row "determinism argument (successor value = lost-run value)" is a structural statement from A1
  (review N2) and carries no value.
* "Caps change only the probability of completion, never Γ" (A.2) is unchanged from r0, gives no estimate and is
  acceptable.
* §G names categories of MB r1 observations and says that no values are reproduced. It states nothing about Γ,
  margin or closure.

Two §G phrases do carry MB r1 run content, R-1 and R-2 below. Neither states or bounds an outcome, a margin or how far
the run got, so I did not classify them as an outcome expectation. They should still be changed before the brief goes
to the user.

## 2. Verbatim sections: still byte-identical

I compared these by exact line-range `diff`; every pair is identical:

| Brief section | Brief lines | Source | Source lines |
| --- | --- | --- | --- |
| §D, O1–O5 with their reconciliations | 72–132 | A1 §1 | 21–81 |
| §E 3a (§20) | 139–163 | ledger | 885–909 |
| §E 3b (§21) | 165–183 | ledger | 911–929 |
| §E 3c (§23) | 185–203 | ledger | 931–949 |
| §E 1c (§26) | 205–226 | ledger | 31–52 |

The section boundaries are clean and there is no trailing whitespace. The new selection sentence in §E (lines 136–137)
sits outside the verbatim blocks.

## 3. Status of my r0 items

* **Applied and accepted:** N-1 (A.3 names both options), N-2 (B.6 "record your decisions"), N-3 (A.4 is now a
  parallel table) and N-8 (A.2 defines "mechanically").
* **Partly applied:**
  * N-4: A.1 now offers withholding, but the B lead-in does not (R-6).
  * N-5: the §E selection is now stated, but its description overstates what it covers (R-7).
  * N-6: §F now carries a time, but not its source, and the tense does not match (R-8).
* **Still open:** N-7 (O5's line range against §4b), which is for the scanner or holder side.

## 4. Remaining sentences I would change

**R-1 (§G, lines 260–262). Fix before sending.** Current text: "no per-worker observation from the coordinator's
23:10 audit".
* Reason: "23:10" is a clock time from the MB r1 run chronology. That contradicts "No values are reproduced here"
  (line 259) and §G's own listing of "the run chronology" as held content (line 253).
* The user's ledger already records the 23:29 Force Quit. Together with that, this time puts on the clock a point at
  which the lost run was being audited.
* That concerns the run's progress, which bears on the caps decision (A.2). A1 S13 requires that decision to rest on
  decoy and qualification evidence only.
* Proposed: "no per-worker observation from a coordinator audit".

**R-2 (§G, line 255). Fix before sending.** Current text: "a qualitative pool-load continuation statement".
* Reason: the word "continuation" gives away what the statement says, not just what kind of statement it is.
  That content is a qualitative observation about the lost run's progress, which is relevant to completion and caps
  (S13).
* Proposed: "a qualitative statement about worker-pool load".

**R-3 (§C, lines 66–67; §F, line 232). Internal contradiction.**
* §C says the T6 ruling "is **pending at the time of writing**". §G reports it as ruled: T6_FIRED_MITIGATED
  (`ff2280e9`).
* Proposed for §C: "the T6 ruling … : T6_FIRED_MITIGATED (§G)".
* Proposed for §F: "Accepted (`b7e62dec`); T6 fired and mitigated, M1 pending (§G)".

**R-4 (A.4 table, line 41; §C, line 63). Neutrality.** Option (i)'s rating reads "MEDIUM–HIGH, upper end,
conditional".
* Reason: this omits §G's condition, "MEDIUM–HIGH (upper end) only under M1–M6; otherwise HIGH", and the fact that M1
  is pending. Option (i) therefore looks more settled than §G says it is.
* Proposed cell text: "MEDIUM–HIGH, upper end, only with byte-identical science and M1–M6 (M1 pending, §G);
  otherwise HIGH".
* Add the same M1–M6 qualifier to the §C rating bullet.

**R-5 (A.1, lines 17–19). Accuracy of both branches.**
* "MB-S stays a **reviewed**, unfrozen, pre-freeze build": "reviewed" conflicts with §F (the implementation review is
  pending) and with §G (M1 is pending). Proposed: "an unfrozen, target-free pre-freeze build".
* "Granting permission allows the freeze and the official qualification" overstates it. Under A1 S16 the user decision
  is only condition (c); (a), (b) and (d) must also hold.
* Proposed: "Granting permission satisfies S16(c); the freeze and official qualification also need S16(a), (b) and
  (d). It does not authorise a target step (see B)."

**R-6 (B lead-in, line 46). Neutrality: the rest of N-4.** "The ruling must expressly: 1. authorise a second consumed
evaluation …" still reads as if the S1 ruling will authorise. Withholding it is not mentioned.
* Proposed: "If you later decide to authorise a successor grant, the S1 ruling must expressly:".
* Also add a line: "Withholding the S1 ruling is equally available: no successor grant is made, and MB-S makes no
  target evaluation."

**R-7 (minor; §E, lines 136–137).** "the passages on a second execution and on successors" reads as if it covers
everything the user said about successors.
* The same ledger records further successor passages: §1a, §1b ("Return to research only through a new successor
  campaign …", which A1 §2 itself cites) and the 2026-09-29 overnight program.
* Proposed: add "The ledger also records §1a, §1b and the 2026-09-29 overnight program (§2); they are not reproduced
  here."

**R-8 (minor; §F, lines 240–243).** The reading is framed as "a reading at that time only", but it goes on in the
present tense ("Memory pressure is elevated, thermal level is 1, … is on, … exceeds").
* Proposed: past tense ("was elevated … was 1 … was on … exceeded"), and name where the reading is recorded.
* My r0 N-6 request still stands: a holder or the scanner should confirm that none of these readings repeats an MB r1
  run observation (S13). I cannot check that.

**R-9 (minor; A.3, line 32).** "The incident re-rating's recommendation is (i)." This is acceptable now that both
options are named.
* Optionally add its reference (`b7e62dec`) so it reads as an attributed input.
* r0 attributed the recommendation to "the incident review"; r1 attributes it to "the incident re-rating". I cannot
  verify which review made it, so the coordinator should make sure the attribution is right.

**Carried over, no change proposed:** N-7. O5 cites `reviews/REVIEW_EXECUTION_INTERRUPTION.md` lines 463–464, and
S13 forbids pointing to that review's §4b. §D must stay verbatim, so the scanner or holder side should confirm the
line range. §G names "the formal MB r1 postexec recovery record" without a path, which I accept.

## Summary

* No outcome expectation of any kind.
* §D and §E are still byte-identical to their sources.
* R-1 and R-2 (MB r1 run content in §G), R-3 (a contradiction between §C and §G), and R-4 to R-6 (neutrality and
  accuracy) should be fixed before the brief goes to the user. R-7 to R-9 are minor.
