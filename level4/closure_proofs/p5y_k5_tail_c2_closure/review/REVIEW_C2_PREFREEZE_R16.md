# Campaign C2 — sixteenth independent pre-freeze review

**VERDICT: READY_TO_FREEZE_WITH_NOTES**

The science, the gate and the integrity envelope are clean for the sixteenth consecutive round, and I reproduced
all of it here rather than inheriting it: four producers re-run into scratch, three byte-for-byte and B0 with only
the expected `head` leaf; `D_PARTIAL` with closed = {305, 306} and open = {307, 308, 309}; the three gap falls;
both Γ; `BOTH_PASSES_OK` with 45/45 consumed constants and 18/18 `certified` at both precisions; 146 additions and
zero modifications or deletions since `5289b6ce`; the gate at exactly one commit; `main` untouched. I also rebuilt
the replacement ledger from the git object store over all 115 committed `evidence/` and `config/` files, taking no
list from C2 or from any prior review: **19 leaves, three files, 9 + 4 + 6**, exactly as published.

**All thirteen of the edits this commit claims landed.** I checked each one individually in the diff and again in
the file at HEAD, in both directions, because certifying an unperformed repair is this campaign's documented
failure mode and was the headline of two of the last three rounds. Thirteen for thirteen, plus the four supporting
edits (round-table row, README row, the new disposition section, the new register row).

**r15's FAIL is genuinely repaired, and every substantive replacement claim this commit wrote is true.** I
re-derived each rather than accepting it: r8 does raise the "Sixth instance" ordinal as its own Note 4 and does say
"Delete the ordinal"; r9 does record it twice, the second time as an express agreement to leave it so a later round
would not treat it as accumulating debt; `REVIEW_C2_PREFREEZE_R12.md` contains no self-disclosure of a hand-tallied
first draft (r13 and r14 each make one about themselves); "nine constitute the single scientific or decision
change" reconciles with the ledger I rebuilt; and the round-13 register row is genuinely the "none-of-one"
exception the text now names.

**I found no defect that clears the FAIL bar.** Nine self-descriptive residues survive, all listed below in full,
and I want to be plain that none of them would mislead an adjudicator about the science, the decision, the
governance state, evidence provenance or the campaign's reliability. The largest of them — the trailing clause at
`:410–411` that still attributes a count re-extraction to r12 — is the fourth-round residue of a claim that r13,
r14 and r15 each independently rated a NOTE, and its false half is now explicitly withdrawn one sentence earlier.
**The namespace is fit to freeze.**

---

## Reviewer context

I am an independent fresh-context reviewer. I wrote no part of Campaign C2 and had no involvement in rounds one
through fifteen. I reviewed `p5y-k5-tail-c2` at `36e8fa1d` in the worktree `/Users/suzhe/ReBaseGuard-k5c2`,
starting from `git diff 757db96a..36e8fa1d` as the review request directed, then sweeping the whole namespace
independently. I re-ran every producer into a scratch directory outside the repository and compared bytes, and I
rebuilt the replacement ledger from scratch. Every count in this file was extracted by script from the files, not
by eye, after the request's warning that r12, r13, r14 and r15 each hand-tallied their own verdict table wrong on
the first attempt; my verdict table below was produced by parsing the verdict column of my own checklist. I
modified no file in this namespace except this one, ran no writing git command, and did not touch AWS or any
remote host. The working tree was clean before I started and clean when I finished.

r15 asked that a sixteenth round not re-derive r14's C13–C15 or C18–C22. I re-derived them anyway where the
commit under review touched them — C13 in particular, because the disposition corpus grew again this round — and
they hold. I did not take r15's "I have left none for a sixteenth round" on trust: I swept the namespace myself and
found nine live instances, two of which r15 did not list and one of which this commit created.

---

## Checklist

| | check | verdict | evidence |
|---|---|---|---|
| 1 | **edit 1 of 13 (r15 Note 1 / D1)** — "unremarked by eight reviews" withdrawn from the live r14 Note 4 row | **PASS** | `:455` now reads "Present since `fb4d688b`. **r14 reported it as unremarked; that was wrong and C2 repeated it unchecked — r8 raised it as its own note 4 … and r9 recorded it twice …**". The string survives only at `:473` (the r15 disposition row, quoting it) and `:537` (the register row). Landed |
| 2 | **edit 2 of 13 (D2)** — the credit to r12 for disclosing a hand-tallied first draft withdrawn | **PASS** | `:410` now "stated that its counts were extracted mechanically rather than hand-tallied", with an explicit parenthetical withdrawal. "disclosed that its own first draft" occurs nowhere outside `review/`. Landed. *(A residual clause in the same paragraph is Note 1)* |
| 3 | **edit 3 of 13 (D3)** — "Its NOTE-level findings were acted on" narrowed | **PASS** | `:418` now "**Three of** its NOTE-level findings were acted on rather than deferred:". The old string occurs nowhere outside `review/`. Landed |
| 4 | **edit 4 of 13 (D4)** — "the only occasion on which C2 has departed" bounded | **PASS** | `:369–370` now "It is **the one departure from a reviewer's explicit instruction that C2 has recorded**". Landed |
| 5 | **edit 5 of 13 (D5, site 1)** — `ERRATUM_C2.md:31` de-enumerated | **PASS** | `:32` now "Reviews r5, r6, r7 and r8 — **and later rounds** — each independently diffed…". Landed. *(The new wording's scope is Note 2)* |
| 6 | **edit 6 of 13 (D5, site 2)** — `README.md:101–103` de-enumerated | **PASS** | `README.md:102–104` now "reviews r5, r6, r7 and r8 each confirmed this … **and later rounds have re-derived it**". "four independent reviews (r5, r6, r7, r8)" survives only at `:400` (historical quotation in the r11 FAIL 2 finding column) and `:485` (the D5 bullet). Landed |
| 7 | **edit 7 of 13 (D6)** — "one is a scientific or decision value" reconciled | **PASS** | `:30–31` now "**nine constitute the single scientific or decision change**". Landed; consistency with the ledger is row 32 |
| 8 | **edit 8 of 13 (D7)** — "Every instance has the same shape … sound every time" corrected | **PASS** | `:546–549` now "**Most** instances have the same shape … The round-13 row is not of that shape: there the repair did not land at all and was then certified as complete (r14 Note 1)." Landed. *(Twin universal at `:580–581`: Note 3; the "the round-13 row" ambiguity: Note 4)* |
| 9 | **edit 9 of 13 (D8)** — the sibling absolute softened | **PASS** | `:556` now "The other episodes are in the register rows above and are **mostly** not re-told here." Landed |
| 10 | **edit 10 of 13 (D9, site 1)** — `:313` compliance clause rewritten as an instruction | **PASS** | `:314` now "**C2 should not make such a claim again**: where prose states a number it should simply be right, and checked before it is written." No longer a claim about the present text. Landed |
| 11 | **edit 11 of 13 (D9, site 2)** — `:399` compliance clause rewritten as an instruction | **PASS** | `:400` now "**C2 should not make such a claim again**: …". "No such claim is made" survives only at `:415`, inside the r12 FAIL 1 finding column as a quotation of the superseded row. Landed |
| 12 | **edit 12 of 13 (D10)** — "Every one of C2's repair rounds has carried an error" bounded | **PASS** | `:503` now "**through round thirteen** carried an error of its own". Landed. *(The bound understates the register the same commit grew: Note 5)* |
| 13 | **edit 13 of 13 (D11)** — N9's "no campaign has built one" narrowed | **PASS** | `OPEN_NOTES_DISPOSITION_C2.md:81` now "and **none exists in this repository**". Landed. *(Still an unverified universal over a mutable corpus: Note 6)* |
| 14 | supporting edit — the round-table row for r15 | **PASS** | `| r15 | 757db96a | 1 FAIL | § "Dispositions from the FIFTEENTH pre-freeze review" |`. `757db96a` is the HEAD r15 reviewed; the named section exists at `:465` |
| 15 | supporting edit — the README review row for r15 | **PASS** | `README.md:54` "NOT_READY — **1 FAIL**", consistent with r15's own "Distinct blocking defects: 1" |
| 16 | supporting edit — the new § FIFTEENTH disposition section | **PASS** | present at `:465–498`; one finding row plus the eleven-item sweep list. Every claim in it is checked at rows 18–34 |
| 17 | supporting edit — the new register row for round 14 | **PASS** | `| 14 | repaired r14 Note 4 | repeated r14's "unremarked by eight reviews" premise without checking it | r15 Note 1 |`. Correctly attributed: `757db96a` is the repair of r14's findings, so it is round 14, matching the register's convention |
| 18 | **r8 raised the ordinal as its own Note 4 and said "Delete the ordinal"** | **PASS — verified at source** | `REVIEW_C2_PREFREEZE_R8.md:116–119`: "**Note 4 (NOTE)** — `ERRATUM_C2.md:378` 'Sixth instance; r5 FAIL 1'. … it is an off-by-one count in prose in the section about off-by-one counts in prose, and three rounds have passed over it. **Delete the ordinal.**" Exactly as the new text says |
| 19 | **r9 mentions it twice, the second time as a deliberate decision to leave it** | **PASS — verified at source** | `R9.md:154–156` ("**NOTE, not FAIL**, and it is already disclosed in a committed review file") and `R9.md:278–283` ("I agree with leaving them, and **I am recording that agreement so a tenth round does not treat them as accumulating debt**"). Two mentions; the second is the express decision |
| 20 | the supplied check — "One `grep -rn 'Sixth instance' review/` refutes it" | **PASS — I ran it** | returns 19 lines across four files, including `R8.md:116` and `R9.md:154`. The command in the text does what the text says it does |
| 21 | "which already occupies two register rows" (the inherited-premise failure mode) | **PASS** | register rows 17 (`took r9's "one place" premise unverified` → r10 FAIL 3) and 19 (`named r9, which had not done the diff` → r10 FAIL 1). Exactly two, and both were FAILs in their round |
| 22 | **`REVIEW_C2_PREFREEZE_R12.md` contains no self-disclosure of a hand-tallied first draft** | **PASS — verified by grep** | the file's only statements on the point are `:197` ("column mechanically") and `:419` ("Counts extracted mechanically from the verdict column of the checklist above, not hand-tallied"). No first draft, no hand tally, no re-extraction. The withdrawal is correct |
| 23 | "r13 and r14 each did that about themselves" | **PASS — verified at source** | `R13.md:440` "My first draft of this table read 29 PASS / 5 FAIL"; `R14.md:439` "My own first draft of this table said 7 FAIL and 10 NOTE". Non-exclusive phrasing, so r15's own disclosure does not falsify it |
| 24 | "Flagged by r13 and carried unrepaired for three rounds" | **PASS** | `R13.md:77` / `:217` / T7 raised it; `R14.md:336` C9 re-raised it; `R15.md:343` D2 re-raised it. Three rounds |
| 25 | "r15 listed eleven live corpus claims (its D1–D11)" | **PASS — tallied mechanically** | r15's class table has exactly 11 rows, labelled D1 through D11 with no gaps |
| 26 | "five of them had been silently carried forward — raised by r13, re-raised by r14" | **PASS** | r15's D2–D6 each cite "was r14 C9 / r13 T7", "r14 C8 / r13 T6", "r14 C10 / r13 T8", "r14 C11 / r13 T9", "r14 C12 / r13 T10". Five, and each names both predecessors |
| 27 | **"All eleven are actioned here"** | **PASS** | D1 at checklist row 1; D2–D11 at rows 2–13. Thirteen edits over eleven items, D5 and D9 having two sites each. The certification is true this time |
| 28 | "at `757db96a`: **1 FAIL**" | **PASS** | r15's verdict counts section: "**Distinct blocking defects: 1**", 1 FAIL row (row 19). Matches |
| 29 | "It confirmed that **all eight** of the r14 repairs landed" | **PASS** | r15's landing table has 8 rows, all "yes". Accurately reported, and I spot-re-derived three of them (the `grep -c` withdrawal, the deleted ordinal, the restored r5 note-8 attribution) at HEAD |
| 30 | D7 bullet — "r14 had rated this claim sound; r15 moved it" | **PASS** | `R14.md` C16 rated it SOUND over 25 rows; `R15.md:344` moved it to the live list. Accurate, and a fair thing to record |
| 31 | D10 bullet — "Also rated sound by r14 and moved by r15" | **PASS** | `R14.md` C17 SOUND; `R15.md:347` D10. Accurate |
| 32 | **"nine constitute the single scientific or decision change" reconciles with the ledger** | **PASS — ledger rebuilt independently** | my rebuild over all 115 committed `evidence/`+`config/` files: `C2_D1_BLOCKER.json` `e71378a0→55c4cf00` 9 replaced (the `C_T` `magnitude`/`delta_vs_base`/`relative_gain` triple on 307/308/309); `C2_MUTATIONS.json` `5a94568a→12585997` 4; `C2_RECERTIFY_306.json` 3 + 3. **19 / three files / 9 + 4 + 6**, matching `:50` and `README.md:93–96` cell for cell |
| 33 | **the round-13 register row is genuinely the "none-of-one" exception now named** | **PASS** | register row 26 (`repaired r13 FAIL 2` / `changed the wording, left the count, and certified the count removed` / `r14 Note 1`). `:452` describes it in bold as "**not repaired at all**, and its disposition row certified that it was"; r14 Note 1 called it "none-of-one". The exception the text names is the row that refutes the old universal |
| 34 | "Three of its NOTE-level findings" matches the three the sentence then enumerates | **PASS** | `:418–421` enumerates exactly three: the `magnitude` claim (r12 Note 4), "the one place in nine rounds" (r12 Note 7), and the transcribed sub-counts (r12 Note 5). The number and the list agree |
| 35 | **the residual r12 clause at `:410–411`** | **NOTE** | "Its counts were **re-extracted** mechanically **before finishing** — the same hazard it was auditing." r12 records no re-extraction, and the clause re-implies the very narrative the parenthetical two clauses earlier withdraws. **Note 1** |
| 36 | **`:32` — "and later rounds — each independently diffed every leaf …"** | **NOTE** | read distributively this sweeps in r9 and r10, neither of which ran the whole-history D1 leaf diff; crediting r9 with it was r10 FAIL 1. `README.md:102–104` states the same fact unambiguously. **Note 2** |
| 37 | **`:580–581` — the twin of the universal repaired at `:546`** | **NOTE** | "**Every instance** was in labelling, framing, or an ornament attached to a result that kept reproducing bit-exactly under **every** independent implementation written against it" was not softened when its twin thirty lines up was. The sibling-absolute shape, a third time. **Note 3** |
| 38 | "The round-13 row is not of that shape" | **NOTE** | three register rows carry round 13 (rows 26, 27, 28); only row 26 is the exception. Disambiguated solely by the trailing "(r14 Note 1)". **Note 4** |
| 39 | `:503` "through round thirteen" against the register the same commit grew | **NOTE** | round 14 now has a register row, so the bound is narrower than the record it introduces, and the D10 bullet's "Bounded to what has been observed" is therefore slightly wrong. Conservative, not false. **Note 5** |
| 40 | `OPEN_NOTES` N9 "none exists in this repository" | **NOTE** | narrower and more honest than "no campaign has built one", but still an unverified universal over a 130-namespace mutable corpus. The class migrated rather than closed here. **Note 6** |
| 41 | `code/c2_recertify_306.py:15` and `:102` — "nothing in this repository records that" | **NOTE** | two docstring/comment universals over the repository, of the same species as N9. Long-standing (the r9 FAIL 3 repair), verified by r10 over C2's `evidence/` and `config/` but asserted over the whole repository. Not listed by r15. **Note 7** |
| 42 | `ERRATUM_C2.md:4` / `README.md:55` — "dispositions every FAIL from every one of them" | **PASS — tallied mechanically** | the round table's 15 rows sum to **39**; the document carries **39** disposition rows (r1's six — FAIL 6, 61, 62, 30, 51, 53 — plus 33 `rN FAIL/Note` rows distributed 3/1/3/2/1/2/3/3/3/2/2/3/4/1 over r2–r15), matching the table cell for cell. True, but a self-maintained universal: listed in the class section |
| 43 | `ERRATUM_C2.md:5` — "Counts belong in the tables … not in prose" against the document's own prose counts | **NOTE** | normative rather than descriptive, so not falsifiable in the way its deleted ancestors were — but the document breaks it freely, including in a sentence added this round (`:418`, "Three of its NOTE-level findings"). **Note 8** |
| 44 | `ERRATUM_C2.md:583` — "its arithmetic was never the weak part, and its prose always was" | **NOTE** | a universal self-characterisation over the campaign. Supported by sixteen rounds of reproduction, but of the class. Not listed by r15. **Note 9** |
| 45 | did the commit introduce any **other** new defect? | **PASS** | I read all 43 added `ERRATUM_C2.md` lines, the added `README.md` line and the changed `OPEN_NOTES` line individually. Notes 1 and 2 are the only ones the commit created or left; Notes 3, 4 and 5 are tensions it sharpened; Notes 6–9 predate it |
| 46 | the round table and disposition registers reconcile | **PASS — tallied mechanically** | 15 table rows, 39 FAILs, 39 disposition rows, matched per round by script |
| 47 | the instance register and its derived figures | **PASS — tallied mechanically** | **29** register rows; **4** marked `self-caught`, in rounds **4 and 5** only; rounds **6–11** contribute exactly **12** rows, **0** of them self-caught. Every figure in the r13 FAIL 3 withdrawal paragraph (`:561–563`) still holds against the larger register |
| 48 | "Every one of C2's repair rounds through round thirteen carried an error of its own" | **PASS — tallied mechanically** | rounds present in the register: 1,2,3,4,5,6,7,8,9,10,11,12,13,14 with counts 1/1/2/3/4/1/1/3/3/2/2/2/3/1. Every round 1–13 has at least one row, so the bounded claim is true |
| 49 | the replacement ledger's scope sentence, "Every leaf this campaign has replaced" | **PASS — re-derived from scratch** | over all 115 files, across every consecutive commit pair: exactly the four rows published, 19 replaced leaves, three files, nothing missing and nothing extra. The regeneration command is printed beside it |
| 50 | `c2_mutations.py` reproduces byte-for-byte | **PASS** | re-run into scratch; `cmp` clean against `evidence/prefreeze/C2_MUTATIONS.json`; `applied 43`, `real_mutants 35`, `static_assertions 8`, `detected 40`, 3 proven-equivalent, `undetected []`, `pass true`, `sha256 512180f32a5ca85355270f57bc98c5281d8bb8de7f9e32a1d10652e1e0a4ebac` matching the file's own sha |
| 51 | `c2_critical_ratio.py` reproduces byte-for-byte | **PASS** | `cmp` clean against `evidence/phase_d5/C2_CRITICAL_RATIOS.json` |
| 52 | `c2_d1_blocker.py` reproduces byte-for-byte | **PASS** | `cmp` clean against `evidence/phase_d1/C2_D1_BLOCKER.json` |
| 53 | `c2_b0_verify.py` reproduces with only the expected drift | **PASS** | leaf-by-leaf diff: exactly one differing leaf, `/B1_git/head` `5289b6ce…` → `36e8fa1d…`. `ALL_PASS true`, B1–B7 all true |
| 54 | class, closed subset, open subset | **PASS** | `C2_D5_FORECAST.json`: `D_STAGE_CLASS = D_PARTIAL`, `closed = [305, 306]`, `still_open = [307, 308, 309]` |
| 55 | the three gap falls | **PASS** | `0.46285183476411584` / `0.24593099374719365` / `0.18389841084966285` on 307 / 308 / 309 — the published figures |
| 56 | Γ(305) and Γ(306) | **PASS** | `-0.08802906884054082` and `-0.030469257709306738`, i.e. `−0.088029069` and `−0.030469258`; both negative, both cells close. 307/308/309 positive as published |
| 57 | `C2_RECERTIFY_306.json` verdict and accounting | **PASS — tallied mechanically** | `BOTH_PASSES_OK`; re-tallied from the artifact: the five consumed constants (C_T, tau, D_lo, D1, D2) **45/45 ok** in `determinism_256` **and** in `safe_side_384`; `certified: true` on 18/18 in both; `all_ok: true` both; `diagnostic_deviations {count 27, worst_relative 5.3188e-30}` |
| 58 | all changes since `5289b6ce` are additions | **PASS** | `git diff --name-status 5289b6ce..36e8fa1d` → **146** rows, all `A`, zero `M`/`D`/`R` (145 at r15's HEAD, plus the r15 review file) |
| 59 | every change is inside the C2 namespace; predecessors untouched | **PASS** | the only changed top-level closure-proof directory is `p5y_k5_tail_c2_closure`; no changed path outside it |
| 60 | `main` untouched | **PASS** | `main` = `c123b9bb`, an ancestor of `36e8fa1d` |
| 61 | frozen gate sha, at exactly one commit | **PASS** | `shasum -a 256 config/FEASIBILITY_GATES_C2.json` = `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`; `git log --all` on that path returns exactly one commit, `87309610` |
| 62 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS** | the most recent commit touching either is `5a94568a` |
| 63 | coverage map r4 intact, no r5 | **PASS** | `K5_COVERAGE_MAP_R4.json` sha256 `a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35`, matching the README's `a3bddd83…`; the only other map anywhere in `level4/` is the predecessor's R3 |
| 64 | nothing pre-empting freeze, qualification, seal or adjudication | **PASS** | no freeze, seal, qualification or adjudication artifact in the namespace; `phase_r/R_STAGE_DESIGN.md:1–6` states DESIGN ONLY, guard **DENY**, no authorization artifact, `NEW_REAL_ADDRESSES = 0`; `CELL_306_ADOPTION.md` is a disposition of the predecessor reviewer's conditions |
| 65 | all fifteen prior review files committed and unedited | **PASS** | each has exactly one commit in `git log -- <file>`; none amended |
| 66 | all fifteen prior reviews returned NOT_READY | **PASS** | extracted by script from each file's VERDICT line: 15 files, 15 `NOT_READY` |
| 67 | working tree clean before and after my re-runs | **PASS** | `git status --porcelain` empty both times; all producer output written to scratch outside the repository |
| 68 | the empty `theorem/` directory | **INFO** | present and empty, therefore not committed. r13, r14 and r15 recorded the same. Harmless; recorded so a seventeenth round does not re-discover it |

---

## Notes

### Note 1 (NOTE) — D2's repair left a residual clause that still attributes a re-extraction to r12

`ERRATUM_C2.md:410–411`, as it stands at HEAD:

> It also listed surviving instances of the corpus-claim class, and stated that its counts were extracted
> mechanically rather than hand-tallied. *(An earlier version of this sentence credited r12 with disclosing that
> its own first draft had been hand-tallied and wrong. It makes no such disclosure — r13 and r14 each did that
> about themselves. Flagged by r13 and carried unrepaired for three rounds; r15 D2.)* **Its counts were
> re-extracted mechanically before finishing — the same hazard it was auditing.**

The bolded sentence is what is left of the withdrawn claim. `REVIEW_C2_PREFREEZE_R12.md` says only *"Counts
extracted mechanically from the verdict column of the checklist above, not hand-tallied"* — one extraction, no
re-extraction, no "before finishing". The word **re-**extracted and the phrase **before finishing** presuppose a
first, non-mechanical tally that was then replaced, which is precisely the narrative the parenthetical two clauses
earlier denies. So the paragraph now asserts and denies the same thing about the same file within four lines, and
it duplicates its own first clause while doing it.

This is the all-but-one shape the campaign's own register exists to record: the named falsehood was deleted, the
clause carrying its implication was not. It is also the fourth round in which this sentence has been flagged and
the second in which a commit rewrote it without carrying the fix along (r15's own words: "it should certainly not
survive a repair that edits its sentence").

**Why this is a NOTE and not a FAIL, and I want to be explicit because it is the closest call in this review.**
r13, r14 and r15 each rated the *stronger* form — the explicit, unambiguous credit — a NOTE, on the ground that no
decision turns on which review disclosed a tally error about itself. What survives is strictly weaker: an
implication carried by a prefix and an adverbial, in a sentence whose neighbour states the correct fact in the
campaign's own voice. An adjudicator reading the paragraph is told, in bold-adjacent parenthesis, exactly what r12
does and does not contain. Nothing about the science, the decision, the governance state, evidence provenance or
the campaign's reliability is misstated by it. Escalating to FAIL now, after three reviewers rated the worse
version a NOTE, would be a change of bar rather than a finding.

**Repair, if a successor touches this file for any other reason:** delete the sentence. The clause before it
already says everything true that it was trying to say.

### Note 2 (NOTE) — `:32`'s "and later rounds" is over-inclusive on its natural reading

`ERRATUM_C2.md:31–34`:

> Reviews r5, r6, r7 and r8 — **and later rounds** — **each** independently diffed every leaf of that artifact
> across its whole history and **each** found the same nine leaves.

The two "each"es distribute over the whole subject, which includes "later rounds". Two later rounds did not do it:

- **r9** did not. Its only leaf diff was of `C2_RECERTIFY_306.json` across one commit pair (`R9.md:78`), and it
  says so itself (`R9.md:192`).
- **r10** did not either. `R10.md:134–139` is a table of *which reviews record the diff* — r5, r6, r7, r8 — read
  out of the committed files, not performed; its own leaf diff at `:215` is again of `C2_RECERTIFY_306.json`.

Crediting r9 with this exact diff was **r10 FAIL 1**, so the sentence re-opens, in vaguer form, the very hole a
FAIL closed six rounds ago. I verified who actually ran it: **r5, r6, r7, r8** (`R5.md:73`, `R6.md:64`,
`R7.md:37`, `R8.md:21`) and later **r11, r12, r13, r14, r15** — nine of fifteen, not all-later-rounds.

I record it as a NOTE rather than a FAIL for three reasons. The core proposition is true and I re-derived it
myself this round from the object store, so an adjudicator relying on it is relying on something correct. No review
is named falsely, which is what made r10 FAIL 1 a FAIL. And the same fact is stated unambiguously in the front-door
file — `README.md:102–104`, "and later rounds **have re-derived it**" — which is the form that cannot be read
distributively.

**Repair:** make `:32` match the README's wording. One clause.

### Note 3 (NOTE) — the twin of the universal repaired at `:546` was not softened

D7 softened `:546` from "Every instance has the same shape" to "Most instances have the same shape" and named the
exception. Thirty lines below, `:580–581` still reads:

> **Every instance** was in labelling, framing, or an ornament attached to a result that kept reproducing
> bit-exactly under **every** independent implementation written against it.

Both sentences generalise over the same 29-row register, one now hedged and one not. The claim is defensible —
nothing in the register touched a computed quantity, which is the paragraph's actual point, and I confirmed that
independently — but "an ornament attached to a result" is a poor description of register row 26, the repair that
was not made, and of row 20, a ledger built over the wrong corpus.

This is the third consecutive round in which a softened absolute has left an unsoftened twin elsewhere in the same
section (r14 Note 6 → r15 Note 4 → here). It is worth saying plainly that the pattern is now in the *repair
method*, not in any one sentence: the fix is applied at the site the reviewer cited and nowhere else.

**Repair:** "Almost every instance was in labelling, framing, or an ornament…", or cite the register instead of
describing it.

### Note 4 (NOTE) — "The round-13 row" names one of three

`:548`. The register carries three rows attributed to round 13 (rows 26, 27, 28). Only row 26 is the none-of-one
case. The trailing "(r14 Note 1)" resolves it for a reader who follows the citation, and no other reading is
available on inspection, so this is imprecision rather than error. **Repair:** "the first of the round-13 rows".

### Note 5 (NOTE) — `:503`'s bound is narrower than the register beneath it

`:503` now reads "Every one of C2's repair rounds **through round thirteen** carried an error of its own", and the
register immediately below it carries a **round 14** row added by the same commit. The claim is true and no longer
self-undermining, which is what D10 asked for. But the D10 bullet at `:496–497` describes the repair as "Bounded to
what has been observed", and what has been observed now extends to round fourteen. Conservative in the
non-flattering direction — the sentence understates C2's own failure rate rather than overstating it — so nothing
is concealed from an adjudicator, who sees the round-14 row three lines later.

**Repair:** "Every repair round recorded below has carried an error of its own", which was r15's suggestion and is
the form that never needs editing again.

### Note 6 (NOTE) — N9's "none exists in this repository"

`OPEN_NOTES_DISPOSITION_C2.md:80–81`. Narrower and more checkable than the "no campaign has built one" it replaces,
and used honestly — to *narrow* C2's own trust claim rather than widen it. It is nonetheless a universal over a
mutable corpus of some 130 namespaces, asserted without a cited check, and it goes stale the day a successor
builds a second certifier. The class migrated here; it did not close. No repair needed before freeze; a successor
should rescope it when it closes N9.

### Note 7 (NOTE) — two repository-wide universals in `c2_recertify_306.py`

`:15` ("nothing in this repository records that") and `:101–103` ("nothing in the repository records that"), both
about the machine that built the registry. Same species as Note 6, in committed code rather than prose. They are
the r9 FAIL 3 repair and were verified by r10 over C2's own `evidence/` and `config/` — but they are asserted over
the whole repository, which is wider than what was checked. Long-standing, honest in direction (they *withhold* a
claim rather than make one), and not listed by r15, whose row 55 judged `code/` clean. Listed here so the class
inventory is complete.

### Note 8 (NOTE) — `:5`'s rule against the document's own practice

`:5` states "Counts belong in the tables of this document and of `README.md`, **not in prose**". The document
carries prose counts throughout — `:50` "19 leaves, three files", `:562` "four were self-caught … none of the
twelve", and, added this round, `:418` "Three of its NOTE-level findings". The rule is normative, not descriptive,
so it is not falsifiable the way its deleted ancestors were (that distinction is exactly what rounds six through
thirteen bought), and `:314` states the workable version: where prose states a number it should simply be right.
The two sentences are in tension and a successor will eventually reconcile them. Non-blocking.

### Note 9 (NOTE) — "its prose always was"

`:583`, closing the pattern section: "its arithmetic was never the weak part, and its prose **always** was." A
universal self-characterisation over the campaign. Sixteen rounds of byte-exact reproduction support the first
half and the register supports the second, so it is not false; it is the last unhedged self-description in the
file. Recorded only so the class inventory is complete.

---

## Did every r15 edit land?

**Yes — all thirteen, plus four supporting edits, verified individually in the diff and again in the file at HEAD,
in both directions (new string present at `36e8fa1d` and absent at `757db96a`; old string absent from the live
text at `36e8fa1d` and present at `757db96a`).** I checked this first and separately, because this campaign has
twice certified a repair that had not happened, and because the commit message itself asserts individual
verification, which is the kind of claim that has been wrong here before.

| | claimed edit | landed? | evidence at HEAD |
|---|---|---|---|
| 1 | **D1 / r15 Note 1** — "unremarked by eight reviews" withdrawn | **yes** | `:455` now records what r8 and r9 actually did; the old clause survives only as a quotation at `:473` and in the register at `:537` |
| 2 | **D2** — the r12 hand-tally credit withdrawn | **yes** | `:410`; "disclosed that its own first draft" occurs nowhere outside `review/`. *(Residue: Note 1)* |
| 3 | **D3** — "its NOTE-level findings" narrowed | **yes** | `:418` "**Three of** its NOTE-level findings were acted on" |
| 4 | **D4** — "the only occasion" bounded | **yes** | `:369–370` "the one departure from a reviewer's explicit instruction that C2 has recorded" |
| 5 | **D5 site 1** — `ERRATUM_C2.md` de-enumerated | **yes** | `:32` "Reviews r5, r6, r7 and r8 — and later rounds —". *(Scope: Note 2)* |
| 6 | **D5 site 2** — `README.md` de-enumerated | **yes** | `README.md:102–104`; the enumerated form survives only as a quotation at `:400` and in the D5 bullet at `:485` |
| 7 | **D6** — "one is a scientific or decision value" reconciled | **yes** | `:30–31` "nine constitute the single scientific or decision change" |
| 8 | **D7** — the shape universal corrected | **yes** | `:546–549` "Most instances have the same shape … The round-13 row is not of that shape" |
| 9 | **D8** — the sibling absolute softened | **yes** | `:556` "are **mostly** not re-told here" |
| 10 | **D9 site 1** — `:313` compliance clause | **yes** | `:314` "C2 should not make such a claim again" |
| 11 | **D9 site 2** — `:399` compliance clause | **yes** | `:400` "C2 should not make such a claim again"; "No such claim is made" survives only inside the r12 FAIL 1 quotation at `:415` |
| 12 | **D10** — the repair-round universal bounded | **yes** | `:503` "through round thirteen carried an error of its own" |
| 13 | **D11** — N9 narrowed | **yes** | `OPEN_NOTES_DISPOSITION_C2.md:81` "none exists in this repository" |

**Supporting edits, all present and accurate:** the round-table row for r15 (`757db96a`, 1 FAIL, pointing at a
section that exists), the README review row (NOT_READY — 1 FAIL), the new § "Dispositions from the FIFTEENTH
pre-freeze review" with its finding row and eleven-item sweep list, and the new register row attributing the round-14
error correctly.

**Nothing in the namespace certifies more than was done.** "All eleven are actioned here" is true; "The whole live
list is swept in this commit, not only the FAIL" is true. That matters, because the last two rounds both blocked on
a disposition row that claimed a repair which had not been made. This round's did not.

---

## Is the corpus-claim class closed?

**Not closed — but it no longer contains a false claim about anything an adjudicator would decide on, and for the
first time in ten rounds the round's own new prose did not add one that does.** r15's whole live list was actioned,
not just its blocker, and the eleven instances it left have become nine, of a strictly milder kind.

Below is every instance I found in the namespace — prose, tables, code comments, docstrings and committed JSON
string leaves — that is a universal, superlative or self-descriptive claim over a mutable corpus and is currently
false, unverified, or capable of going stale. I swept all nine `.md` files outside `review/`, all seven `.py` files
in `code/`, the free-text leaves of every committed JSON under `evidence/` and `config/`, and every added line of
this commit, by script and then by hand. **None of the nine blocks a freeze, and I say so as the finding, not as a
concession.**

| | site | the claim | status |
|---|---|---|---|
| **E1** | `ERRATUM_C2.md:410–411` | r12's "counts were **re-extracted** mechanically **before finishing**" | **UNSUPPORTED — Note 1.** r12 records one mechanical extraction and no re-extraction; the clause re-implies the narrative the same paragraph withdraws. Residue of r15 D2, fourth round, in a sentence this commit rewrote. The largest of the nine |
| **E2** | `ERRATUM_C2.md:32` | "Reviews r5, r6, r7 and r8 — **and later rounds** — **each** independently diffed every leaf …" | **OVER-INCLUSIVE — Note 2.** r9 and r10 did not; crediting r9 with this diff was r10 FAIL 1. Created by this commit as the D5 repair. `README.md:102–104` states it correctly |
| **E3** | `ERRATUM_C2.md:580–581` | "**Every instance** was in labelling, framing, or an ornament … under **every** independent implementation" | **UNSOFTENED TWIN — Note 3.** Sibling of the D7 repair at `:546`, not carried along. Defensible on its actual point, loose on its wording |
| **E4** | `ERRATUM_C2.md:548` | "**The** round-13 row is not of that shape" | **AMBIGUOUS — Note 4.** Three register rows carry round 13; the citation resolves it. Introduced by this commit |
| **E5** | `ERRATUM_C2.md:503`, `:496–497` | "through round thirteen" / "Bounded to what has been observed" | **NARROWER THAN THE RECORD — Note 5.** The same commit added a round-14 row. Errs against C2's own interest; nothing concealed. Introduced by this commit |
| **E6** | `OPEN_NOTES_DISPOSITION_C2.md:81` | "a second, independently written certifier … **none exists in this repository**" | **UNVERIFIED, STALE-CAPABLE — Note 6.** The D11 repair: narrower than its predecessor, still a universal over 130 namespaces with no cited check |
| **E7** | `code/c2_recertify_306.py:15`, `:101–103` | "**nothing in this repository** records that" (×2) | **WIDER THAN WHAT WAS CHECKED — Note 7.** Verified by r10 over C2's `evidence/` and `config/`, asserted over the repository. Honest in direction. Not listed by r15 |
| **E8** | `ERRATUM_C2.md:5` | "Counts belong in the tables … **not in prose**" | **IN TENSION WITH PRACTICE — Note 8.** Normative, so not falsifiable; the document carries prose counts throughout, including one added this round |
| **E9** | `ERRATUM_C2.md:583` | "its arithmetic was **never** the weak part, and its prose **always** was" | **UNHEDGED SELF-CHARACTERISATION — Note 9.** True on the record; the last unhedged self-description in the file |

**Maintained universals I checked and found true, so a seventeenth round need not.** These are not on the list
above because they are correct at HEAD and are re-verified every round by construction, but they are
self-maintained and will need re-checking whenever the corpus grows:

- `ERRATUM_C2.md:4` / `README.md:55` — "dispositions every FAIL from every one of them": **39 table FAILs, 39
  disposition rows**, matched per round by script.
- `ERRATUM_C2.md:40` — the ledger's scope sentence, "Every leaf this campaign has replaced in an already-committed
  evidence file": **re-derived from scratch over all 115 files — true**, and the regeneration command sits beside it.
- `README.md:82` — "Every independent pre-freeze review so far has returned NOT_READY": **15 of 15**, extracted by
  script from the VERDICT lines.
- `ERRATUM_C2.md:561–563` — the r13 FAIL 3 replacement figures: **4 self-caught, rounds 4 and 5 only, 0 of the 12
  rows in rounds 6–11**, re-tallied against the 29-row register.
- `ERRATUM_C2.md:503` — every round 1–13 has at least one register row.
- `ERRATUM_C2.md:30–31`, `:49`, `README.md:93–96` — 19 = 9 + 4 + 6 across three files, all four cells correct.

**What changed in the class this round, and why I think it is now finishable.** For ten rounds the class behaved
the same way: a blocker was repaired, and the repair or its neighbourhood produced a new false claim over the
review corpus, the register or the document's own prose. This commit is the first that swept an entire live list,
and the first where the new claims about *other committed files* — what r8 said, what r9 decided, what r12 does and
does not contain, which register row is the exception — are all true; I checked every one at source rather than
accepting the citation. What is left is nine residues, of which seven are hedging or scope problems and none
asserts a falsehood about the science, the decision, the governance state, evidence provenance or the campaign's
reliability. That is a different object from what the last ten reviews were looking at, and the honest description
is that the class has been reduced to editorial residue rather than closed outright.

---

## Did this repair introduce a new defect?

**Yes — two, both NOTE-level, and I assumed there were more until I had read every changed sentence.** I extracted
all 43 added `ERRATUM_C2.md` lines, the added `README.md` line and the changed `OPEN_NOTES_DISPOSITION_C2.md` line
and checked each independently against source:

- The **round-table row**, the **README row** and the **section title** they point at: consistent, and `757db96a`
  is the commit r15 reviewed.
- The **r15 disposition section's opening paragraph**: "1 FAIL" matches r15's "Distinct blocking defects: 1"; "all
  eight of the r14 repairs landed" matches r15's landing table; "the three residual strings appear only as
  historical quotations" — I re-checked all three at HEAD and they do.
- **The r15 Note 1 row**: accurate in every clause. r8 Note 4 says "Delete the ordinal"; r9 records it twice, the
  second an express agreement to leave it; the grep refutes the old claim in one command; the register does carry
  exactly two rows for the inherited-premise failure mode.
- **The eleven-item sweep list**: each bullet checked against r15 and against the file. Two describe their own
  repair slightly loosely — D7's "Corrected to name the exception" (Note 4) and D10's "Bounded to what has been
  observed" (Note 5).
- **The rewritten r14 Note 4 row**: correct, including the ordinal's position in the register and the `fb4d688b`
  provenance.
- **The new register row**: correctly worded and correctly attributed to round 14.
- **The D2 repair**: the false credit is withdrawn; the clause after it was not carried along — **Note 1**.
- **The D5 repair**: correct in the README, over-inclusive in the erratum — **Note 2**.

Notes 3, 4 and 5 are tensions this commit sharpened rather than created: it hedged one of two twin universals, it
named one of three round-13 rows, and it bounded a claim to thirteen while adding a fourteenth row. Notes 6–9
predate it. I have counted only Notes 1 and 2 as newly created or newly left.

---

## What I did not check

- The Arb/FLINT passes themselves, every certified constant in `evidence/registry_c2/`, and the mathematics the
  producers implement. I verified that the committed producers reproduce their committed artifacts byte-for-byte,
  which establishes reproducibility, not mathematical correctness.
- `0.932851` (max D_lo × 1.1 across the tail) and `1.0674 / 0.005505 / 0.060556`. I confirmed they are present and
  unaltered but did not recompute them; I rely on r3's table, r4's independent exact verification and r14's
  recomputation from `C2_D1_BLOCKER.json`.
- N10's build-log premise, and anything on a remote host. I ran nothing on AWS or Vultr, as the review request
  requires.
- The internal correctness of the predecessor namespaces. I checked only that they are byte-untouched since
  `5289b6ce` and that the r4 coverage map's sha256 matches what the README cites.
- The fifteen prior review files end to end. I read r5, r8, r9, r10, r12, r13, r14 and r15 in the parts that bear on
  my findings, extracted every verdict line by script, and confirmed each file's commit count is one.
- r15's own verdict table. I did not re-parse r15's checklist to confirm its 45/1/10/0; I confirmed only its
  distinct-blocker count of 1, which is what the disposition row and the round table transcribe.
- Commit messages as a corpus. I read the one under review and compared its claims against the tree; I did not
  sweep the campaign's commit messages, which are immutable and outside the namespace.

---

## Verdict counts

Extracted from the checklist table above by script, not by hand:

| verdict | rows |
|---|---|
| PASS | 58 |
| FAIL | 0 |
| NOTE | 9 |
| INFO | 1 |
| **total rows** | **68** |

58 + 0 + 9 + 1 = 68, reconciling against the table; rows are numbered contiguously 1–68 with none missing.

**Distinct blocking defects: 0.**

**NOTE-level findings: 9** — Notes 1 through 9, at checklist rows 35, 36, 37, 38, 39, 40, 41, 43 and 44. Note 7
covers two sites (`c2_recertify_306.py:15` and `:101–103`) in a single row. Row 68 is the INFO.

*Method, because four consecutive rounds got this wrong by hand.* The table above was produced by a script that
reads the verdict column of the committed checklist and counts it; I re-ran it against this file after my final
edit. A seventeenth reviewer, should there be one, should re-run the extraction rather than trust the printed
table, for the reason `ERRATUM_C2.md:382–383` gives.

---

## Where I landed

The request asked me to say whether the calibration is right, and whether a residual self-descriptive imperfection
in an errata document rises to a FAIL. **I think the calibration is right, and I think nothing here clears it.**

Fifteen rounds have verified the science, the gate and the integrity envelope, and so have I, independently and
from scratch: three producers byte-for-byte, B0 with one expected leaf, the class and both Γ and all three gap
falls exact, 45/45 at both precisions, 146 additions and nothing else since `5289b6ce`, the gate at one commit,
`main` untouched, no lifecycle artifact pre-empting anything, all fifteen prior reviews committed and unedited. I
also rebuilt the replacement ledger from the object store over 115 files and got 19 / three / 9 + 4 + 6. Nothing an
adjudicator would decide on has moved since round one, and nothing in this review touches any of it.

What was left to decide was the corpus-claim class, and specifically whether this commit — which repaired a FAIL
*and* swept ten NOTEs, the first round to do both — introduced a replacement defect of the kind that has blocked
ten consecutive rounds. It introduced two, and neither is of that kind. The last five rounds each blocked on a
sentence that was **false about a committed file**: that r12 had disclosed something it had not, that eight reviews
had walked past a defect two of them had found, that a `grep -c` returned 4 when the same commit made it 7. I went
looking for that sentence and it is not there. Every claim this commit makes about another committed file — r8's
Note 4, r9's two mentions and its express decision, r12's absent disclosure, r13's and r14's own disclosures,
r15's eleven items and its five silently-carried ones, the register row that is the exception — I checked at source
and every one is true.

What survives is nine residues, and I have listed all nine rather than the one or two I would most like fixed. The
strongest, Note 1, is a subordinate clause implying a process step for a reviewer who did not record one; three
reviewers rated its unambiguous ancestor a NOTE, and its false half is now explicitly withdrawn in the same
paragraph. The next, Note 2, is an appositive that is over-inclusive on a distributive reading, in a sentence whose
front-door twin states the same fact correctly, and whose core proposition I verified myself. The other seven are
hedging, scoping and self-characterisation. None of them would cause an adjudicator to misjudge the science, the
decision, the governance state, evidence provenance or the campaign's reliability, and I do not think a seventeenth
round spent on them would find anything a sixteenth has not.

I am conscious that a reviewer in this position has an incentive to find one more thing, because sixteen rounds of
NOT_READY make a ready verdict look like fatigue. I have tried to price that in by holding myself to the bar as
written rather than to the bar the record implies: a FAIL must be a concrete defect capable of misleading an
adjudicator about one of five named things. I found none. **If a seventeenth round is run, it should be run because
someone wants Notes 1 and 2 repaired, not because this namespace is unsafe to freeze — it is not.**

**The D-stage successor may be frozen.** The nine notes are editorial and can be swept in a single commit before or
after the freeze; if they are swept before it, that commit should touch nothing else, and — on this campaign's own
record — its own new sentences should be checked before they are committed.

**VERDICT: READY_TO_FREEZE_WITH_NOTES.**
