# Thirteenth independent pre-freeze review — Campaign C2, D-stage successor

**VERDICT: NOT_READY**

*Thirteenth independent fresh-context pre-freeze review, 2026-09-21, worktree `/Users/suzhe/ReBaseGuard-k5c2`,
branch `p5y-k5-tail-c2`, HEAD `92bc9637`. Read-only: this file is the only file I wrote, and I ran no writing git
command. AWS was not touched.*

---

## Reviewer context — what I re-derived, and what I took on trust

I wrote none of this work and read it cold. As instructed I started from `git diff 6aa2040a..92bc9637` — three
files, 507 insertions, 22 deletions, of which 457 insertions are r12's review file committed verbatim — and then
widened to the whole namespace for the corpus sweep. Everything I call verified below I verified myself on this
machine (macOS/arm64, stdlib CPython 3, `PYTHONINTMAXSTRDIGITS=0`). I did not use the FLINT venv.

**Re-derived independently.** All three stdlib producers re-run into a scratch directory and compared with `cmp`
against their committed artifacts: `code/c2_mutations.py` → `evidence/prefreeze/C2_MUTATIONS.json`
**byte-identical**, sha256 `512180f32a5ca85355270f57bc98c5281d8bb8de7f9e32a1d10652e1e0a4ebac`;
`code/c2_d1_blocker.py` → `evidence/phase_d1/C2_D1_BLOCKER.json` **byte-identical**; `code/c2_critical_ratio.py` →
`evidence/phase_d5/C2_CRITICAL_RATIOS.json` **byte-identical**. I also re-ran `code/c2_b0_verify.py`, which returns
`ALL_PASS: true` and differs from the committed artifact in exactly one leaf, `.B1_git.head`
(`5289b6ce` → `92bc9637`), as expected and as r6 and r12 recorded. From `C2_D5_FORECAST.json` I read back
`D_STAGE_CLASS = D_PARTIAL`, `closed = [305, 306]`, `still_open = [307, 308, 309]`, gap falls
`0.46285183476411584 / 0.24593099374719365 / 0.18389841084966285`, `Gamma(305) = −0.08802906884054082`,
`Gamma(306) = −0.030469257709306738`, `gate_sha256 = 098dd7f5…`, `gate_frozen_before_forecast: true`. From
`C2_RECERTIFY_306.json` I recounted the consumed-constant checks myself against
`(C_T, tau)` on the nine block artifacts and `(D1, D2, D_lo)` on the nine cell artifacts: **45/45 `ok` at 256 bits
and 45/45 at 384 bits**, `all_ok: true` on both passes, 18/18 `certified: true`, verdict `BOTH_PASSES_OK`,
`registry_sha_pin_ok: true`.

**The ledger, rebuilt from scratch.** I took no file list from the campaign and none from r12. I enumerated every
path under `evidence/` and `config/` at HEAD and every path ever touched under those trees on any ref, wrote my
own JSON leaf-flattener, and diffed consecutive revisions with `git log --reverse --all -- <file>`. 115 files at
HEAD, 115 ever, no deletions or renames, 112 single-revision. **19 replaced leaves across three files, 9 + 4 + 6,
leaf for leaf as tabulated**, plus 114 added and 20 removed outside the ledger's stated scope. r11 FAIL 1 is
repaired and r12's rebuild is confirmed independently. Detail in § "Rebuilt replacement ledger".

**Tallies.** Every count I print about a checklist — r11's, r12's and my own — is the output of a script that
extracts the verdict column, not a hand count; my own first draft was hand-counted and wrong, and the disclosure
is in § "Verdict counts". The same script produced the sub-count sweep behind FAIL 1.

**Taken on trust.** The Arb/FLINT passes themselves and every certified constant; the mathematics the producers
implement; N10's build-log premise; anything on a remote host. I relied on r11's V1, V5, V8 and V10 and on r12's
V-list as the review request permits, after re-deriving V2, V6, V7, V11 and V12 here.

**Where I landed.** The science, the gate and the integrity envelope are clean for the thirteenth consecutive
round, and I reproduced all of it rather than inheriting it. Both of r12's FAILs are repaired, and FAIL 2 is
repaired exactly right — the README's `9 + 4 + 6 = 19` reconciles against my own rebuild. But the paragraph that
reports what this commit achieved makes a false universal claim about this very document, of precisely the shape
r12 FAIL 1 named and precisely the sentence r12 asked the campaign not to write; a second prose tally of the
campaign's own defects was left contradicting the one this commit corrected; and a bolded claim about the
campaign's self-audit record has been false for six rounds and is still there. Three FAILs, all textual, none
touching evidence.

---

## Checklist

| | check | verdict | evidence |
|---|---|---|---|
| 1 | **r12 FAIL 1 — the surviving compliance clause deleted** | **PASS — verified** | `grep -rn "prose does not"` over the namespace returns no occurrence in C2's own prose; `ERRATUM_C2.md:427` now reads "…where this campaign tallies its own defects. Hand-maintained counts in prose are themselves one of the recurring defects". The only remaining hits are inside quotation in disposition rows and in the review files |
| 2 | r12 FAIL 1 — the r11 FAIL 2 row rewritten to record the partial repair | **PASS — verified** | `:397` now reads "The compliance clauses are deleted. *(The first repair removed one of the two and recorded both as gone — r12 FAIL 1. The second survived verbatim for a further round and is deleted now.)*" Accurate |
| 3 | **r12 FAIL 1 — was the *same shape* avoided this round?** | **FAIL** | no. `:419–422` claims a sweep of this document that was not performed and miscounts the sweep it did perform. **Note 1 — FAIL 1** |
| 4 | **r12 FAIL 2 — README provenance paragraph reconciles** | **PASS — verified against my own rebuild** | `README.md:91–97`: nineteen leaves "divide 9 + 4 + 6"; the nine are the C_T sensitivity row on 307/308/309, the four the suite counts, the six the free text and `cpu_seconds`. 9 + 4 + 6 = 19 and each figure matches my ledger rebuild leaf for leaf |
| 5 | the nine are correctly identified as the one scientific correction | **PASS — verified** | the nine replaced leaves are exactly `.cells.{307,308,309}.sensitivity_10pct_improvement.C_T.{magnitude, delta_vs_base, relative_gain}` at `e71378a0 → 55c4cf00`. "Brought inside the Lemma Dv′ admissibility premise" matches the r2 FAIL 66 disposition |
| 6 | **the replacement ledger is still complete** | **PASS — rebuilt from scratch here** | 115 committed files under `evidence/` + `config/`; three multi-revision; **19 replaced, three files, 9 + 4 + 6**. No replaced leaf is absent from the table and no tabled leaf is absent from my rebuild. See § "Rebuilt replacement ledger" |
| 7 | **r12 S3 — the "magnitude" claim restated as a claim about values** | **PASS — verified** | `:50–52` now reads "No **value** of a certified operator constant, of Γ, of a cell magnitude, of a required reduction or of a gap fall was replaced", with the field-name collision disclosed in the parenthetical. I confirmed the substance: across all four commits of `C2_D1_BLOCKER.json` the five `.cells.*.magnitude` leaves are byte-stable, and `evidence/registry_c2/` has a single commit |
| 8 | **no transcribed per-review sub-count remains in `ERRATUM_C2.md`** | **FAIL** | `:72` still reads "79 checks — 60 PASS, 10 INFO, 3 NOT_CHECKABLE_LOCALLY, **6 FAIL**"; `:283` and `:286` carry r1's and r2's breakdowns. Eleven headers carried one at `6aa2040a`; ten were stripped. **Note 1 — FAIL 1** |
| 9 | "Only FAIL counts remain, because those reconcile against the rows below" | **FAIL (same finding)** | false on its face given row 8. **Note 1** |
| 10 | the FAIL counts that do remain reconcile against the disposition rows | **PASS — recounted mechanically** | round table sums 6+3+1+3+2+1+2+3+3+3+2+2 = **31**; disposition rows = 25 `rN FAIL k` + 6 r1-style = **31**, and the per-round split matches the table round for round (r1 6, r2 3, r3 1, r4 3, r5 2, r6 1, r7 2, r8 3, r9 3, r10 3, r11 2, r12 2). `ERRATUM_C2.md:4` and `README.md:52` hold |
| 11 | **r11's true checklist tally is 31 PASS / 1 PARTIAL / 2 NOTE / 2 FAIL against a stated 30/1/3/2** | **PASS — verified mechanically** | script extraction of r11's verdict column over its 36 numbered rows gives 31/1/2/2; r11's own verdict-counts block at `:289–296` states 36 rows, 30 PASS, 1 PARTIAL, 3 NOTE, 2 FAIL. The erratum's figures at `:421–422` are right |
| 12 | r12's own verdict counts are internally consistent | **PASS — verified mechanically** | my extraction over r12's 39 numbered rows gives 29 PASS / 1 PARTIAL / 5 NOTE / 4 FAIL, matching its stated table exactly. Its "distinct blocking defects: 2" is what the round table and README transcribe, consistent with every earlier round's convention |
| 13 | the r12 round-table and README rows are correct | **PASS — verified** | `| r12 | 6aa2040a | 2 FAIL |` — `6aa2040a` is the HEAD r12 reviewed; README row "NOT_READY — **2 FAIL**"; r12's verdict is NOT_READY |
| 14 | the r12 disposition section describes r12's ledger rebuild accurately | **PASS — verified** | "over all 115 committed files … 19 leaves / three files / 9 + 4 + 6 correct in every cell, with nothing missing" matches r12 `:34–38`, `:260–271` and my own independent rebuild |
| 15 | **the r12 disposition section describes r12's self-disclosure accurately** | **NOTE** | `:408–409` credits r12 with having "disclosed that its own first draft of its verdict table was hand-tallied and wrong". r12's committed file contains no such disclosure — only `:419`, "Counts extracted mechanically … not hand-tallied". **Note 4** |
| 16 | **"Its NOTE-level findings are acted on rather than deferred"** | **NOTE** | r12 raised seven NOTE-level findings (Notes 3–9). Three were acted on (4, 7, and 5 via the strip that FAIL 1 concerns); Notes 3, 6, 8 and 9 were not. **Note 5** |
| 17 | **the two prose tallies of C2's own false-compliance episodes agree** | **FAIL** | they do not. `:309` says "C2 has **twice** written a sentence here claiming its prose contains no counts, and **both times** the claim was false"; `:397`, rewritten by this commit, says "**three times**, and each time". Same fact, same document, 88 lines apart. **Note 2 — FAIL 2** |
| 18 | r12's S2 named two sites (`:395` and `:306`); both repaired? | **FAIL (same finding)** | `:395` was rewritten; the `:306–312` parenthetical was not touched at all, and now contradicts it. **Note 2** |
| 19 | **`ERRATUM_C2.md:481–482` — "the self-audit is now finding these faster than the reviews are"** | **FAIL** | false, and false for six rounds. The register immediately above it has 23 rows: **4 self-caught** (all in rounds 4–5, last at `ec5b08ca`) and **19 reviewer-caught**; of the 12 rows added in rounds 6–11, **zero** are self-caught. **Note 3 — FAIL 3** |
| 20 | **r12 S4 — "the one place in nine rounds" no longer carries a round count** | **NOTE** | the round bound is gone as r12 suggested, but `:366` now reads "It is **the only occasion** on which C2 has departed from a reviewer's explicit instruction" — an unbounded universal. r12's Note 7 records a second candidate (r10's declined structural recommendation), and its other half — the second register still carrying only r2 note 4 — is unactioned for a third round. **Note 6** |
| 21 | **r12 S5 — "four independent reviews (r5, r6, r7, r8)"** | **NOTE** | unchanged at `README.md:99–100` and `ERRATUM_C2.md:29`. True and non-exclusive, but r11, r12 and now this review have each run the whole-history D1 leaf diff, so the enumeration undercounts by three and will drift again. **Note 7** |
| 22 | **r12 Note 3 — `ERRATUM_C2.md:27–28` made to match the repaired README** | **NOTE** | not done. The README now says nine of nineteen leaves are the scientific correction; `:27–28` still says "one is a scientific or decision value" of the same nineteen, disambiguated only by the "nine leaves" clause two lines down. r12 asked for exactly this if FAIL 2 were repaired. **Note 5** |
| 23 | **r12 Note 6 — the ledger's replacement-only scope stated** | **NOTE** | not done. My rebuild confirms 114 added and 20 removed leaves outside the table's scope; the scope sentence at `:37` is exact and I verified it, but the section is still headed as the complete provenance accounting with no pointer to r2 FAIL 66 / r4 FAIL 1. **Note 8** |
| 24 | **did this repair introduce a new defect?** | **FAIL** | yes — Note 1 (the sweep claim, `:419–422`) and Note 2's stale half (`:309` left contradicting the `:397` this commit rewrote). Note 3 is pre-existing and undetected for six rounds |
| 25 | three producers reproduce byte-for-byte | **PASS — re-run here** | three for three `cmp` clean into scratch, plus B0 `ALL_PASS` with the one expected head leaf. Working tree `git status --porcelain` empty before and after |
| 26 | `c2_mutations.py` 43/43, 0 undetected, sha `512180f3…` | **PASS — re-run here** | `applied 43` = 35 real + 8 static, `detected 40`, 3 proven-equivalent (M19, M20, M32), `undetected: []`, `pass: true`; artifact sha256 `512180f32a5c…4ebac` |
| 27 | class `D_PARTIAL`, closed {305, 306}, open {307, 308, 309} | **PASS — verified** | read back from `C2_D5_FORECAST.json` |
| 28 | gap falls 0.46285183 / 0.24593099 / 0.18389841 | **PASS — verified** | exact to full precision on cells 307/308/309 |
| 29 | Γ(305) = −0.088029069, Γ(306) = −0.030469258 | **PASS — verified** | −0.08802906884054082 and −0.030469257709306738 |
| 30 | `C2_RECERTIFY_306.json` = `BOTH_PASSES_OK`, 45/45 at both precisions | **PASS — recounted from the artifact** | 45/45 at 256 bits and 45/45 at 384 over the five consumed constants, every field `ok`, 18/18 `certified`, `all_ok` both passes, `registry_sha_pin_ok: true` |
| 31 | gate sha `098dd7f5c3cf…b28f` at exactly one commit | **PASS — verified** | `shasum -a 256` matches byte for byte; `git log --all` on the path returns only `87309610` |
| 32 | all-additive and in-namespace since `5289b6ce` | **PASS — verified** | `git diff --name-status 5289b6ce..92bc9637` → **143 A, 0 M, 0 D**; no path outside `level4/closure_proofs/p5y_k5_tail_c2_closure/` (r12's 142 plus its own review file) |
| 33 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS — verified** | per-path history: the JSON's only commit is `5a94568a`; the producer's are `51f8844b` then `5a94568a`, and `51f8844b` is the earlier commit. Neither file is in this diff |
| 34 | `main` untouched | **PASS — verified** | `main` is `c123b9bb`, an ancestor of HEAD; no C2 commit on it |
| 35 | coverage map r4 `a3bddd83…` intact; no r5 map | **PASS — verified** | `K5_COVERAGE_MAP_R4.json` hashes to `a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35`; repo-wide `find -iname '*COVERAGE_MAP_R5*'` → nothing |
| 36 | nothing pre-empts freeze, qualification, seal, adoption or adjudication | **PASS — verified** | no lifecycle artifact anywhere in the namespace and the diff adds none; `R_STAGE_DESIGN.md:5` guard **DENY** with no authorization artifact; `CELL_306_ADOPTION.md:9–13` states adoption is a terminal governance state nothing in C2 may confer |
| 37 | all twelve prior review files committed and unedited | **PASS — verified** | each of `review/REVIEW_C2_PREFREEZE{,_R2…_R12}.md` has **exactly one** commit in `git log --all`; r12 is committed at `92bc9637` verbatim and I diffed it against nothing else because nothing else exists |
| 38 | code comments and docstrings swept for the class | **PASS — verified independently** | the only corpus universals in `code/` remain `c2_critical_ratio.py:14` (= V9) and `c2_recertify_306.py:101–102` (= V4); both sound and both unchanged in this diff. Confirms r11 row 32 and r12 row 33 |
| 39 | committed JSON string leaves swept for the class | **PASS — verified independently** | I flattened all 115 committed JSON files: 4073 string leaves, 52 flagged by the universal/superlative regex, every one a mathematical or gate-rule quantifier over a fixed object, except `host.note` (= V4) and `diagnostic_policy.why` (r10-dispositioned). No JSON changed in this diff. Confirms r12 row 34 |
| 40 | `ERRATUM_C2.md:5–6` and `:307–309` — "counts belong in the tables, not in prose" | **NOTE** | normative rather than a truth claim, so not itself false — but `:72` is a prose tally that violates it, and `:307–308`'s past-tense "every hand-maintained tally was deleted from the prose that carried it" is false as a description of the present state. **Note 9** |
| 41 | working tree clean; no stray artifact | **PASS** | `git status --porcelain` empty. The empty untracked `theorem/` directory persists (0 entries, 0 tracked); untracked, so outside the freeze. **Note 10** |

---

## Notes

### Note 1 (FAIL 1) — the paragraph reporting this commit's sweep claims a sweep of this document that was not performed, and miscounts the one it did perform

`ERRATUM_C2.md:416–422`, added by `92bc9637`:

> Its NOTE-level findings are acted on rather than deferred: … and **every transcribed per-review
> PASS/NOTE/INFO sub-count has been stripped from this document**. That last is the r5 FAIL 2 lesson finally
> applied consistently — C2 had re-introduced the habit in **six** disposition headers … **Only FAIL counts
> remain**, because those reconcile against the rows below.

Three statements, checked mechanically by regex over the file:

**(a) The universal is false.** `ERRATUM_C2.md:72`, the disposition header for the FIRST pre-freeze review, still
reads in full:

> `review/REVIEW_C2_PREFREEZE.md`, at `5a94568a`: **79 checks — 60 PASS, 10 INFO, 3 NOT_CHECKABLE_LOCALLY**, **6 FAIL**.

That is a transcribed per-review PASS/INFO sub-count, in a disposition header, in the same form as the ten that
were stripped, and it is untouched by this commit. `:283` and `:286` carry two more (r2's "62 PASS / 4 NOTE / 2
INFO" and r1's "60 PASS / 10 INFO / 3 NOT_CHECKABLE_LOCALLY"); those two sit inside the r5 FAIL 2 analysis and the
erratum has a standing reason for keeping them — `:330` calls the recount "fixed historical fact rather than a
running tally" — but the new sentence carves out nothing, and `:72` has no such defence.

**(b) "Only FAIL counts remain" is false** for the same reason.

**(c) The count of what was stripped is wrong.** At `6aa2040a`, **eleven** disposition headers carried a
PASS/NOTE/INFO sub-count — r1 through r11. This commit stripped **ten** of them. "Six" understates the work done
by four and, more importantly, is the artefact of not having run the sweep the sentence describes: a sweep that
had been run would have returned eleven and would have caught `:72`.

**Why this is a FAIL and not a NOTE.** It is the r12 FAIL 1 shape reproduced exactly — *a repair that covers all
but one of the named items, recorded as covering all of them* — one round later, in the paragraph dispositioning
the review that named that shape, and in the last sentence written before commit, which r12 identified at its
`:376–378` as the precise locus of this failure. r12 closed with "it should make only them, and it should not
write a third sentence saying that it has"; this is that third sentence, and it is wrong in three places. An
adjudicator reading `:419–422` concludes the transcription hazard is eliminated from this document. It is not, and
the surviving instance is in the disposition of round one, which is the first thing a reader of that document
reaches. That misleads about the campaign's repair record, and hence about its reliability, which is inside the
bar.

**To repair:** strip `:72` down to "**6 FAIL**" as the other ten were; then either delete the "every transcribed
… stripped" clause entirely and say nothing about the state of the document, or state the number actually swept
and the carve-out for `:283`/`:286`, with the command beside it. The campaign's own adopted rule (`:380`) is the
one that applies: *never describe a corpus you can cite; if you must describe it, run the check before committing
the sentence, and put the command in the text.*

### Note 2 (FAIL 2) — the two prose tallies of C2's own false-compliance episodes now contradict each other; only one of r12's two S2 sites was touched

r12's S2 named **two** sites, `:395` and `:306`. This commit rewrote the first and left the second byte-identical.
They now disagree about the same fact.

`:397` (rewritten by this commit):

> C2 has written a sentence claiming its prose carries no counts **three times**, and **each time** the claim was
> false while sitting beside counts.

`:309–312` (untouched, inside the r6 disposition):

> *(C2 has **twice** written a sentence here claiming its prose contains no counts, and **both times** the claim
> was false while the sentence itself sat beside counts. No such claim is made now…)*

Twice or three times: the document states both, 88 lines apart, about the identical phenomenon, and neither figure
is accompanied by a check. Nor is either obviously right — `:330` (r7 FAIL 1) records C2 "asserting **twice** that
no sentence in the namespace states a count" in the round-six repair *before* the two clauses r11 later named, so
a reader trying to reconcile them arrives at four rather than at either printed figure.

This is the same class and the same mechanism as FAIL 1: the neighbouring sentence the fix failed to carry along,
in the register that exists to record exactly that mechanism. The erratum is the instrument an adjudicator uses to
audit how often this campaign asserted compliance it did not have; when that instrument states two different
counts of those episodes, the audit cannot be completed from the document.

**To repair:** delete the count from one of the two — the `:309` parenthetical is the weaker of the pair and is
already fully covered by the r11 and r12 disposition rows — or cite the enumeration (r7 FAIL 1's two, r11 FAIL 2's
two) instead of summing it in prose.

### Note 3 (FAIL 3) — "the self-audit is now finding these faster than the reviews are" has been false for six rounds

`ERRATUM_C2.md:481–482`:

> **The self-audit is now finding these faster than the reviews are**, which is the only encouraging thing in this
> section.

Extracted mechanically from the "caught by" column of the register at `:432–456`, which sits forty lines above it:

| | |
|---|---|
| register rows | 23 |
| **self-caught** | **4** — all in rounds 4 and 5, the last corrected at `ec5b08ca` |
| reviewer-caught | 19 |
| rows added in rounds 6–11 | 12, of which **0** are self-caught |

The sentence was plausibly true when it was written, in the round-five era, where three of that round's four
entries are self-catches. It has been false since round six, it is present-tense and bolded, and it is the one
evaluative claim the section makes about the campaign's capacity to police itself.

**Why this is a FAIL and not a NOTE.** I considered NOTE, and this is the softest of my three findings: it is
rhetoric rather than arithmetic, and nothing decided by the gate turns on it. I file it as a FAIL because the
reader it is addressed to is precisely the adjudicator deciding how much of this campaign's self-reporting to
trust; because it is refuted by the table directly above it, so a reader who checks finds the document arguing
against itself; and because it is a self-descriptive claim over a mutable corpus that has been allowed to go
stale — the defect class this namespace has now spent eight rounds on, surviving undetected through seven of them.
Leaving it for a fourteenth round would be leaving exactly what the review request says not to leave.

**To repair:** delete the sentence, or state it in the past tense and bounded ("in rounds four and five the
self-audit caught four of the seven instances recorded for those rounds"), which is a fixed historical fact and
cannot go stale.

### Note 4 (NOTE) — a disclosure is attributed to r12 that r12's committed file does not contain

`ERRATUM_C2.md:408–409` says r12 "**disclosed** that its own first draft of its verdict table was hand-tallied and
wrong, which it re-extracted mechanically before finishing — the same hazard it was auditing."

r12's committed file says only, at `:419`, "Counts extracted mechanically from the verdict column of the checklist
above, not hand-tallied — for the reason given in Note 5." It does not say that a first draft existed, that it was
hand-tallied, or that it was wrong. The claim may well be true of what the reviewer reported outside the
namespace, and it is creditable of C2 to record it; but an adjudicator who checks it against the cited file will
not find it. This is a claim about the contents of a committed corpus asserted without the corpus supporting it —
the same class, at low severity, and in the same paragraph as FAIL 1. Cite where the disclosure was made, or drop
the word "disclosed" and attribute it to the handover.

### Note 5 (NOTE) — "Its NOTE-level findings are acted on rather than deferred" covers three of seven

r12 raised seven NOTE-level findings, its Notes 3–9. Acted on: Note 4 (the magnitude claim, `:50–52`), Note 7 in
part (the round count removed from `:366`), and Note 5 by way of the sub-count strip — which FAIL 1 shows was
itself incomplete. Not acted on: **Note 3** (make `ERRATUM_C2.md:27–28` match the repaired README), **Note 6**
(state the ledger's replacement-only scope), **Note 8** (the "four independent reviews" enumeration) and **Note
9** (the untracked `theorem/`). Read as introducing the three items that follow it the sentence is defensible;
read as written it is a fourth universal in the same paragraph, and the campaign's history is that this
distinction is not one it gets the benefit of. Note 3 matters most of the four: with r12 FAIL 2 repaired, the
README now says nine of nineteen leaves are the scientific correction while `:27–28` still says "one is a
scientific or decision value" of the same nineteen. That is the divergence r12 predicted in terms.

### Note 6 (NOTE) — "the only occasion on which C2 has departed from a reviewer's explicit instruction"

`:366`. The round count is gone, as r12 asked. What replaced it is an unbounded universal rather than r12's
suggested "the one place so far", and the other half of r12's Note 7 — that C2 declined r10's explicit structural
recommendation without registering it, and that the second register at `:461–463` still carries only r2 note 4 —
is unactioned for a third consecutive round (r11 Note 5, r12 Note 7, now this). I add a third candidate: r12
closed with "it should make only them, and it should not write a third sentence saying that it has", and
`92bc9637` did both. Whether any of these counts as a "departure from an explicit instruction" is arguable, which
is the point — the claim is not checkable as written, and the campaign has no register that would settle it.
Either register the declined recommendations in the second register, or drop "the only".

### Note 7 (NOTE) — "four independent reviews (r5, r6, r7, r8)"

`README.md:99–100` and `ERRATUM_C2.md:29`, unchanged. r12 verified this sound as its V1 and I did not disturb it.
But r11, r12 and this review have each now run the whole-history leaf diff of `C2_D1_BLOCKER.json` — I ran it here
across all four commits and confirm the nine — so the enumeration undercounts by three and will drift by one more
each round it survives. Citing the check rather than the cast, as r12 proposed, removes the maintenance
permanently. Carried forward unchanged, still a NOTE.

### Note 8 (NOTE) — the ledger is scoped to replacements and still does not say so

r12's Note 6, unactioned. My independent rebuild finds, besides the 19 replacements, **114 added** and **20
removed** leaves, all in `C2_D1_BLOCKER.json` and `C2_MUTATIONS.json`; the 20 removals are
`gain_per_unit_of_input_moved` struck from the four non-C_T operator rows at `92c5d199`, r4 FAIL 1's remedy. The
scope sentence at `:37` is exact and I verified it holds. The reading hazard r12 described stands: a section
headed "Replacement ledger" and introduced as the complete provenance accounting invites being read as covering
every change to committed evidence. One clause closes it. Not a defect; the sentence is true as written.

### Note 9 (NOTE) — the normative clauses are now violated in fact by `:72`

`:5–6` ("Counts belong in the tables of this document and of `README.md`, not in prose") and `:307–309` ("So every
hand-maintained tally was deleted from the prose that carried it. Counts belong in the tables…") are normative and
historical rather than present-tense compliance claims, which is why r12 passed the second of them at its row 10.
I pass them on the same reasoning. I record them because `:72` is a prose tally that violates the norm both state,
and because the past-tense "every hand-maintained tally was deleted from the prose that carried it" is, taken as a
description of the present, false. If FAIL 1 is repaired at `:72` the whole of this note goes away.

### Note 10 (INFO) — empty untracked `theorem/`

`level4/closure_proofs/p5y_k5_tail_c2_closure/theorem/` still exists on disk, is empty (0 entries) and untracked
(0 files in `git ls-files`), so it is outside the freeze. Unchanged from r11's Note 6 and r12's Note 9. Third
round carried; still not a defect.

---

## Rebuilt replacement ledger

Rebuilt independently, taking no file list from the campaign and none from r12. Method: enumerate every path under
`evidence/` and `config/` from `git ls-tree -r --name-only HEAD`, union with every path ever touched under those
trees on any ref (`git log --all --name-only --diff-filter=ACDMRT`); for each, walk `git log --reverse --all --
<file>`, parse each revision's blob as JSON, flatten to leaves keyed by full path (dict keys and list indices), and
diff consecutive revisions. A **replaced** leaf is one whose key exists in both revisions with a different value.

**Corpus.** 115 committed files under `evidence/` + `config/` at HEAD; 115 ever seen in history; **no file has
ever been deleted or renamed**. 112 are single-revision. Three have more than one:

| file | revisions | replaced | added | removed |
|---|---|---|---|---|
| `evidence/phase_d1/C2_D1_BLOCKER.json` | 4 | **9** | 58 | 20 |
| `evidence/prefreeze/C2_MUTATIONS.json` | 2 | **4** | 56 | 0 |
| `evidence/prefreeze/C2_RECERTIFY_306.json` | 3 | **6** | 0 | 0 |
| **total** | | **19** | 114 | 20 |

Leaf by leaf, the nine at `e71378a0 → 55c4cf00` are
`.cells.{307,308,309}.sensitivity_10pct_improvement.C_T.{magnitude, delta_vs_base, relative_gain}`; the four at
`5a94568a → 12585997` are `.applied`, `.detected`, `.real_mutants` and
`.mutants.M10_wrong_tail_cell.caught_by[0]`; the six are `.diagnostic_policy.why` and both
`.passes.*.cpu_seconds` at `8aee1fc5 → 55c4cf00`, and `.host.note` and both `.passes.*.cpu_seconds` at
`55c4cf00 → 5609358f`. **19 replaced leaves, three files, 9 + 4 + 6 — the campaign's ledger is correct in every
cell, and so is r12's rebuild of it.** Nothing is missing from it and nothing in it is absent from my rebuild.

**Cross-check of the stability claim.** I separately tracked the five `.cells.*.magnitude` leaves of
`C2_D1_BLOCKER.json` across all four of its commits: byte-stable throughout. Together with
`evidence/registry_c2/` having a single commit (`5a94568a`, re-derived here over the directory), that establishes
the new `:50–52` sentence: no value of a certified operator constant, of Γ, of a cell magnitude, of a required
reduction or of a gap fall has been replaced.

---

## The corpus-claim defect class — is it closed?

**No. This is the eighth consecutive round in which it survives, and this round it survives in the sentence that
reports the round's own sweep of it.**

The substance continues to improve, and that should be said plainly: the provenance accounting itself is correct
and I established that by rebuilding it rather than reading it; r12's S1, S3, S6 and S7 are genuinely closed; and
nothing in the class touches the science, the gate, the integrity envelope, evidence provenance or review
attribution. What survives is eleven sentences, three of them currently false in a way an adjudicator would act
on.

Below is **every** universal, superlative or self-descriptive claim over a mutable corpus that I found in the
namespace — Markdown prose and tables, `.py` comments and docstrings, and every one of the 4073 string leaves of
the 115 committed JSON files. I leave none for a next round.

**Surviving — currently false (4):**

| # | site | claim | why it fails |
|---|---|---|---|
| **T1** | `ERRATUM_C2.md:419` | "**every** transcribed per-review PASS/NOTE/INFO sub-count has been stripped from this document" | `:72` survives verbatim with "60 PASS, 10 INFO, 3 NOT_CHECKABLE_LOCALLY"; `:283` and `:286` carry two more. **FAIL 1 / Note 1** |
| **T2** | `ERRATUM_C2.md:422` | "**Only FAIL counts remain**, because those reconcile against the rows below" | false by T1. The FAIL counts themselves do reconcile — 31 against 31, checked. **FAIL 1 / Note 1** |
| **T3** | `ERRATUM_C2.md:420–421` | "C2 had re-introduced the habit in **six** disposition headers" | eleven headers carried one at `6aa2040a`; ten were stripped. **FAIL 1 / Note 1** |
| **T4** | `ERRATUM_C2.md:481` | "**The self-audit is now finding these faster than the reviews are**" | the register above it: 4 self-caught of 23, none since round five, 0 of the 12 added in rounds 6–11. **FAIL 3 / Note 3** |

**Surviving — two statements of one fact that cannot both be true (1):**

| # | site | claim | status |
|---|---|---|---|
| **T5** | `ERRATUM_C2.md:309` vs `:397` | "C2 has **twice** written a sentence claiming its prose contains no counts" / "…**three times**" | same fact, same document; this commit rewrote `:397` and left `:309`. `:330` suggests four. **FAIL 2 / Note 2** |

**Surviving — true now, but stale, drifting, unverifiable in-namespace, or over-general (6):**

| # | site | claim | status |
|---|---|---|---|
| **T6** | `ERRATUM_C2.md:416` | "Its NOTE-level findings **are acted on rather than deferred**" | three of r12's seven; Notes 3, 6, 8, 9 deferred. Defensible if read as introducing the list that follows. **Note 5** |
| **T7** | `ERRATUM_C2.md:408–409` | r12 "**disclosed** that its own first draft of its verdict table was hand-tallied and wrong" | r12's committed file contains no such disclosure. **Note 4** |
| **T8** | `ERRATUM_C2.md:366` | "It is **the only occasion** on which C2 has departed from a reviewer's explicit instruction" | r12 S4, half-actioned: the round count is gone, the universal is now unbounded and has at least two other candidates, neither registered. **Note 6** |
| **T9** | `README.md:99–100`, `ERRATUM_C2.md:29` | "**four** independent reviews (r5, r6, r7, r8) each confirmed this" | r12 S5, unchanged. True and non-exclusive; now an undercount by three. **Note 7** |
| **T10** | `ERRATUM_C2.md:27–28` | "Of the leaves replaced … **one is a scientific or decision value**" | r12 S3/Note 3, unactioned; now diverges from the repaired `README.md:91–92`, which says nine. Locally disambiguated two lines later. **Note 5** |
| **T11** | `ERRATUM_C2.md:307–308` | "So **every** hand-maintained tally was deleted from the prose that carried it" | past-tense about the round-six repair, which r7 and r8 showed was incomplete; false as a description of the present, given `:72`. **Note 9** |

**Closed this round, verified:** r12's **S1** (`; prose does not` deleted — no occurrence remains in C2's prose);
**S2** in part (the `:395` row rewritten accurately; its second site `:306` untouched and now inconsistent — see
T5); **S3** (restated as a claim about values, and the substance re-derived here); **S6** (the r11 header's
30/1/3/2 removed, and its true tally 31/1/2/2 confirmed mechanically); **S7** (the README now reconciles at
9 + 4 + 6 = 19, confirmed against my own rebuild).

**Corpus claims checked and found sound (12).** r11's V1, V5, V8, V10 and r12's V3, V4, V9 relied on per the
review request; the rest re-derived here. Recorded so a fourteenth round need not re-derive them.

| # | site | claim | how it was checked |
|---|---|---|---|
| V1 | `ERRATUM_C2.md:29`, `README.md:99` | r5/r6/r7/r8 each diffed every leaf of `C2_D1_BLOCKER.json`; r9 did not | r11 and r12 (see T9 for the drift caveat) |
| V2 | `ERRATUM_C2.md:62` | "`evidence/registry_c2/` has one commit in its history" | **re-derived here**: `git log --all` on the directory → `5a94568a` only |
| V3 | `ERRATUM_C2.md:385` | "no build-host record exists anywhere in C2's `evidence/` or `config/`" | r12, from a flatten of all 115 JSON files; my own string-leaf sweep found no new host record |
| V4 | `C2_RECERTIFY_306.json.host.note`, `c2_recertify_306.py:101–102`, N10 | "the registry's build host is not recorded anywhere in this repository" | r11, r12; unchanged in this diff and re-read here |
| V5 | `ERRATUM_C2.md:362` | the artifact's bytes contain no fragment of the docstring | r11, r12 |
| V6 | `ERRATUM_C2.md:4`, `README.md:52` | "dispositions every FAIL from every one of them" | **re-derived here after the r12 row**: 31 disposition rows against 31 FAILs, matching round for round |
| V7 | `README.md:3` | "Nothing outside this namespace is modified" | **re-derived here**: 143 A, 0 M, 0 D since `5289b6ce`, every path in-namespace; `main` an ancestor |
| V8 | `OPEN_NOTES…:81`, `CELL_306_ADOPTION.md:98` | "no campaign has built [a second, independently written certifier]" | r2, r7, r11 |
| V9 | `R_STAGE_DESIGN.md:60`, `c2_critical_ratio.py:14` | "the C1 column, which nothing else in the programme has ever computed" | r12; both sites unchanged in this diff |
| V10 | `CELL_306_ADOPTION.md:48` | the in-repo corroboration is "the one identified", not "the only" | r11; the narrowing is in place and I re-read it |
| **V11** | `ERRATUM_C2.md:37` — the ledger's scope sentence | "Every leaf this campaign has replaced in an already-committed evidence file" | **re-derived here from scratch over all 115 files**: true |
| **V12** | `ERRATUM_C2.md:47–52` | "19 leaves, three files … nine … four … six", and no value of a certified constant, Γ, cell magnitude, required reduction or gap fall replaced | **re-derived here**: exact leaf for leaf; the five `.cells.*.magnitude` leaves byte-stable across all four D1 commits |

**On why the class keeps surviving.** r12 diagnosed it as the last sentence written before commit — the one
describing what the commit achieved — and proposed the cure: never state, in prose, a fact about the campaign's
own text or its own evidence tree that is not the printed output of a command included beside it. This round
supplies the confirming experiment. Everything `92bc9637` did that was *cited* is right: the ledger, which I
rebuilt; the 9 + 4 + 6; the r11 tally 31/1/2/2, which I extracted mechanically and which matches; the cell-level
magnitude stability, which I re-derived. Everything it *described* is wrong: the sweep of its own document, the
count of headers it swept, the reviewer disclosure it paraphrased, the notes it said it had actioned. The
campaign does not have an accuracy problem. It has a problem with exactly one genre of sentence, and it has now
written that genre of sentence in the disposition of every one of the last four reviews to name it.

---

## What I did not check

- **The Arb/FLINT passes and every certified constant.** I did not use the FLINT venv and recomputed no certified
  value. The determinism and safe-side results are trusted on the artifact, on the leaf-stability of its three
  commits, and on twelve prior reviews. I recounted 45/45 from the artifact; I did not re-derive it.
- **The underlying K5-B / TC-T mathematics.** I verified that the committed producers reproduce their artifacts
  byte-for-byte, not that what they compute is mathematically correct.
- **Anything on a remote host.** AWS was not touched; `rebaseguard-vultr` was not contacted. N10's build-log
  premise is unverified by me, as it was by r8–r12.
- **`code/c2_refined_registry.py`** beyond confirming it is unchanged in this diff and reading its comments for the
  corpus sweep. I did not run `build` or `verify`, and did not re-derive the 105/105 registry verification.
- **`evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json`** beyond confirming it is single-revision and clean in
  my ledger rebuild.
- **`D_PRIME_OPPORTUNITY.md`'s counter-combination arithmetic (r12's N7).** Read, not recomputed. It is the finding
  the README says outranks the rest, and it has still not been independently recomputed by any round I read —
  thirteen rounds in, that is the largest unexamined surface in this namespace, and I record it as such rather than
  as a defect.
- **Reviews r1–r10 end to end.** I read r12 in full, r11's checklist and verdict block in full, and r1–r10 by
  targeted search — for the sub-count sites, the compliance-clause history, and row 37 by history rather than
  content.
- **r1's own checklist row count.** I confirmed r1's self-reported verdict table sums to its stated 79; I did not
  independently re-derive that its checklist has 79 rows, because my parser cannot cleanly separate r1's checklist
  from its data tables. Nothing in my findings turns on it — FAIL 1 concerns the presence of the transcription, not
  its accuracy.
- **Predecessor namespace contents.** I established only that no path outside the C2 namespace changed since
  `5289b6ce`, that `main` is untouched, and that the r4 coverage map is intact with no r5 anywhere in the repo.

---

## Verdict counts

| | |
|---|---|
| rows | 41 |
| PASS | 27 |
| NOTE | 7 |
| **FAIL** | **7** |
| notes | 10 (3 FAIL, 6 NOTE, 1 INFO) |

Counts extracted mechanically from the verdict column of the checklist above by script, not hand-tallied. The
seven FAIL rows are **3 distinct defects**: rows 3, 8 and 9 are the single finding of Note 1; rows 17 and 18 are
Note 2; row 19 is Note 3; row 24 ("did this repair introduce a new defect?") is a question answered FAIL that
points at Notes 1 and 2 rather than adding a defect — it is counted in the row tally and not as a fourth defect.

*Disclosure, because this review's FAIL 1 is about exactly this.* My first draft of this table read 29 PASS / 5
FAIL. I had hand-counted the FAIL rows and missed two while writing the sentence above it, which is the same
mechanism as Note 1 and as r12's Note 5. The script that produced the table as it now stands was run afterwards
and its output is what is printed: 41 rows, 27 PASS, 7 NOTE, 7 FAIL, numbering contiguous 1–41. Any count in this
file about any checklist — r11's, r12's or my own — came from that script. A reviewer who audits this file should
re-run the extraction rather than trust the table, for the reason the campaign's own `ERRATUM_C2.md:380` gives.

**Distinct blocking defects: 3.**

**VERDICT: NOT_READY.**

**The science, the gate and the integrity envelope are clean, and I re-derived them rather than inheriting them:**
three producers byte-identical plus B0 `ALL_PASS`, `D_PARTIAL` with closed {305, 306} and open {307, 308, 309},
all three gap falls and both Γ exact to full precision, `BOTH_PASSES_OK` with 45/45 consumed constants at 256 and
384 bits and 18/18 `certified`, 43/43 mutants with 0 undetected reproducing sha `512180f32a5c…`. 143 additions and
nothing else since `5289b6ce`; the gate byte-exact at `098dd7f5…` and at exactly one commit; `c2_d5_forecast.py`
and `C2_D5_FORECAST.json` unmoved since `5a94568a`; `main` untouched; coverage map r4 `a3bddd83…` intact with no
r5 anywhere; guard DENY and no lifecycle artifact pre-empting freeze, qualification, seal, adoption or
adjudication; all twelve prior reviews committed with exactly one commit each and unedited.

**Both of r12's FAILs are repaired, and FAIL 2 is repaired exactly right.** The README's `9 + 4 + 6 = 19`
reconciles against a ledger I rebuilt from the git object store over all 115 committed evidence and config files
without looking at either the campaign's table or r12's. The surviving compliance clause is gone. The r11 tally
r12 flagged is correct as restated — 31/1/2/2 against a stated 30/1/3/2, which I extracted mechanically. The
ledger's "magnitude" claim is now a claim about values and the substance of it holds. This is the best-verified
state this namespace has been in.

**The namespace is not yet fit to freeze**, for three textual reasons, none touching evidence and two of them
introduced by `92bc9637`. Freezing now would freeze (i) a sentence asserting that every transcribed per-review
sub-count has been stripped from the erratum when the disposition of round one still carries one, alongside a
count of the sweep that is wrong by five — the r12 FAIL 1 shape reproduced in the paragraph dispositioning r12;
(ii) two prose tallies of C2's own false-compliance episodes that give different numbers for the same fact, one of
them rewritten by this commit and the other left; and (iii) a bolded claim that the self-audit is outpacing the
reviews, refuted by the register forty lines above it and false for six rounds.

**On the calibration.** I think it is right and I applied it as written. I did not withhold a ready verdict to
avoid appearing lenient: seven NOTEs and an INFO are genuinely non-blocking, I say so plainly, and I have recorded
twelve corpus claims as sound and five of r12's seven S-items as closed so that a fourteenth round need not
re-derive them. Nor did I grant one to end the cycle: FAIL 1 is a completeness claim about this document that is
false and that an adjudicator would rely on when auditing the repair record; FAIL 2 leaves the defect register
unable to state how many times this campaign claimed compliance it did not have; FAIL 3 is the softest of the
three and I say so in the note, but it is a present-tense claim about the campaign's reliability refuted by its
own table, and the request was to leave nothing for a next round.

**The repairs are one header, one count, one clause and one sentence.** If the campaign makes them, the right
thing to write about having made them is nothing at all: the disposition rows below the tables already carry the
record, and every round in which this campaign described its own compliance in prose is a round in which the
description was wrong.
