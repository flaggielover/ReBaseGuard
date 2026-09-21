# Campaign C2 — fifteenth independent pre-freeze review

**VERDICT: NOT_READY**

The science, the gate and the integrity envelope are clean for the fifteenth consecutive round, and I reproduced
all of it here rather than inheriting it: four producers re-run into scratch, three byte-for-byte and B0 with only
the expected `head` leaf; `D_PARTIAL` with closed = {305, 306} and open = {307, 308, 309}; the three gap falls;
both Γ; `BOTH_PASSES_OK` with 45/45 consumed constants and 18/18 `certified` at both precisions; 145 additions and
zero modifications or deletions since `5289b6ce`; the gate at exactly one commit; `main` untouched. Nothing an
adjudicator would decide on has moved, and nothing in this review touches any of it.

**Every one of the eight repairs r14 asked for landed.** I checked each edit individually in the diff and again in
the file at HEAD, because last round's failure mode was certifying a repair that had not happened. All eight are
real, and the three strings r14 quoted survive only as historical quotations inside the r14 disposition rows.

What blocks the freeze is **one** new defect, and it is the ninth-round class: **a claim over a mutable corpus
asserted without running the check, written into the disposition register this round and false.**
`ERRATUM_C2.md:454` states that the "Sixth instance" ordinal was "**unremarked by eight reviews**". Two of those
eight reviews remarked on it by name — r8 raised it as its Note 4 and said "Delete the ordinal", and r9 recorded it
twice, the second time as an explicit agreement to leave it so that a later round would *not* treat it as
accumulating debt. The premise came from r14's own Note 4, was not checked, and is now asserted as fact in C2's
voice in the instrument an adjudicator reads to judge how much scrutiny this namespace has actually received. A
single `grep -rn 'Sixth instance' review/` refutes it.

This is C2's own documented failure mode — inheriting a reviewer's unverified premise — which already occupies two
rows of the register it was written into (r10 FAIL 1, r10 FAIL 3), both of which were FAILs.

---

## Reviewer context

I am an independent fresh-context reviewer. I wrote no part of Campaign C2 and had no involvement in rounds one
through fourteen. I reviewed `p5y-k5-tail-c2` at `757db96a` in the worktree `/Users/suzhe/ReBaseGuard-k5c2`,
starting from `git diff 75a97a18..757db96a` as the review request directed, then sweeping the whole namespace
independently. I re-ran every producer into a scratch directory outside the repository and compared bytes. Every
count in this file was extracted by script from the files, not by eye, after the request's warning that r12, r13
and r14 each hand-tallied their own verdict table wrong on the first attempt; my own verdict table below was
produced by the same script that parsed my checklist. I modified no file in this namespace except this one, ran no
writing git command, and did not touch AWS or any remote host. The working tree was clean before I started and
clean when I finished.

The request permits me to rely on r14's sound list (C13–C22). I did rely on it, and I re-derived C13, C14, C15,
C18, C19, C21 and C22 here anyway because my findings touch them. **I have reason to doubt two of its rows**:
C16 and C17 are no longer sound as written, for reasons created by the commit under review, and I have moved both
to the live list (D7, D10). That is not a criticism of r14 — C16 was true of the 25 rows r14 checked, and the
falsifying rows were added afterwards. It is the point: the register grew this round and the universals standing
over it were not re-checked against the larger register.

---

## Checklist

| | check | verdict | evidence |
|---|---|---|---|
| 1 | repair 1 of 8 — the count "twice" removed from the older statement | **PASS** | `:312` now reads "…claiming its prose contains no counts **more than once**…". No numeral. Landed |
| 2 | repair 2 of 8 — the count "three times" removed from the other statement | **PASS** | `:399` now reads "C2 has **repeatedly** written a sentence claiming its prose carries no counts". No numeral. Landed |
| 3 | the two statements can no longer diverge, as `:438` now asserts | **PASS** | both sites re-read at HEAD; neither carries a count; the two quantifiers ("more than once", "repeatedly") are consistent. The row's claim is true this time |
| 4 | repair 3 of 8 — the `grep -c 'self-caught'` instruction withdrawn | **PASS** | `:520–522` now says "Derive it from the **caught by** column of the register above; a `grep -c` over this whole file does not work". Verified: the grep returns 7 at HEAD, the caught-by column gives 4. Landed, and the new negative claim is true |
| 5 | repair 4 of 8 — the exhaustiveness clause deleted | **PASS** | `:408` now reads "It also listed surviving instances of the corpus-claim class"; "all seven … rather than leaving any for a later round" is gone from the live text. Landed |
| 6 | repair 5 of 8 — the "Sixth instance" ordinal deleted | **PASS** | `:552` now reads "See r5 FAIL 1 and its register row.)" The ordinal is gone. Landed |
| 7 | repair 6 of 8 — the "single largest source" superlative removed | **PASS** | `:466–468` now reads "the narrative here has itself produced **many** of the defects it describes". No superlative remains anywhere in the namespace (`grep`ed). Landed |
| 8 | repair 7 of 8 — the "it is not re-told" absolute removed | **PASS** | `:467–468` now reads "episodes recorded in a register row are **generally** not re-told". Landed. *(A sibling absolute at `:517` was not softened — D8, a NOTE)* |
| 9 | repair 8 of 8 — the r5 note-8 attribution restored | **PASS** | `:512` "One substantive point from those episodes is kept — **it is r5's note 8** —". Verified against `REVIEW_C2_PREFREEZE_R5.md:252–260`: that note is exactly the ratio-vs-difference qualification. Correct attribution |
| 10 | the previous round's edits actually applied (the stated near-miss) | **PASS** | all eight strings present at HEAD and absent at `75a97a18`, checked in both directions by script. Whatever happened on the first attempt, the committed tree carries the edits |
| 11 | `"so the two cannot diverge again"` appears only as a historical quote | **PASS** | one occurrence in the namespace outside `review/`: `:451`, inside the r14 Note 1 **finding** column, reporting what the superseded row asserted. Not a live claim |
| 12 | `"all seven surviving instances"` appears only as a historical quote | **PASS** | one occurrence: `:453`, inside the r14 Note 3 finding column. Not a live claim |
| 13 | `"Sixth instance; r5 FAIL 1"` appears only as a historical quote | **PASS** | one occurrence: `:454`, inside the r14 Note 4 finding column. Not a live claim. *(The rest of that row's finding text is a separate matter — row 19)* |
| 14 | the r13 FAIL 2 disposition row now records what happened | **PASS** | `:438` carries the parenthetical "*(The repair changed the older statement's wording and left its count standing, while this row certified that the count had been removed — r14 Note 1. Neither half was true.)*" Verified against `git show 6d987390`: that commit's only change in the sentence was `both times` → `each time` |
| 15 | the new r14 disposition section reports r14's work accurately | **PASS** | "**4 distinct FAILs**" — r14 states "Distinct blocking defects: 4"; "all 25 register rows" — r14 row 31; "recomputed the retained r4 ratio-vs-difference point" — r14 row 9; "nine markdown files, seven Python files" — I counted 9 `.md` outside `review/` and 7 `.py` in `code/` at HEAD; "hand-tallied and wrong on two columns" — r14 says its first draft read 7 FAIL and 10 NOTE against an actual 8 and 9 |
| 16 | r14's own verdict table reproduces, so "4 FAIL" is not a transcribed self-report | **PASS — tallied mechanically** | re-parsed r14's checklist: 56 rows numbered 1–56, **38 PASS / 8 FAIL / 9 NOTE / 1 INFO**, FAIL rows 26, 27, 30, 42, 48, 49, 50, 55 — identical to r14's printed table. 8 rows, 4 distinct defects |
| 17 | the round table row and README row for r14 | **PASS** | `| r14 | 75a97a18 | 4 FAIL | § "Dispositions from the FOURTEENTH…" |`; `75a97a18` is the HEAD r14 reviewed; the named section exists at `:441`. README row "NOT_READY — **4 FAIL**", consistent with the r13 precedent (7 FAIL rows recorded as 3) |
| 18 | the "On the narrative reduction" paragraph is accurate | **PASS** | each clause traced to r14: nothing load-bearing lost (r14 rows 31–36), two of r13's three FAILs outside that section (verified independently — r13 FAIL 1 in § TWELFTH, r13 FAIL 2's sites in § SIXTH and § ELEVENTH), the two fresh self-descriptive claims (r14 Notes 5, 6) |
| 19 | **the r14 Note 4 finding column is accurate** | **FAIL** | `:454` asserts the ordinal was "Present since `fb4d688b` and **unremarked by eight reviews**". False. `REVIEW_C2_PREFREEZE_R8.md:116–119` raises it as Note 4 and says "Delete the ordinal"; `REVIEW_C2_PREFREEZE_R9.md:154–156` and `:278–282` record it twice more. **Note 1** |
| 20 | the three new register rows are accurate | **PASS** | row 1 (`repaired r13 FAIL 2` / `changed the wording, left the count, and certified the count removed`) and row 2 (`supplied a command to re-derive a figure` / `the same commit falsified the command`) verified against git; row 3 (`reduced this section's narrative`) matches r14 Notes 5–6. All three correctly attributed to round 13 |
| 21 | the register's round attribution is right | **PASS** | `6d987390` and `75a97a18` are the repairs of r13's FAILs, so they are round 13; the existing rows follow the same convention (round N = the repair of review rN) |
| 22 | the r13 FAIL 3 replacement figures still reconcile after the register grew | **PASS — tallied mechanically** | 28 register rows; **4** marked `self-caught`, in rounds **4 and 5** only; rounds **6–11** contribute exactly **12** rows, **0** of them self-caught. Every figure in the withdrawal paragraph holds against the larger register |
| 23 | "this document dispositions every FAIL from every one of them" (r14 C13) | **PASS — tallied mechanically** | the round table's 14 rows sum to **38**; the document carries **38** disposition rows — r1's six (FAIL 6, 61, 62, 30, 51, 53) plus 32 `rN FAIL/Note` rows distributed 3/1/3/2/1/2/3/3/3/2/2/3/4 over r2–r14, matching the table cell for cell |
| 24 | **"Every instance has the same shape … The primary claim was sound every time"** | **NOTE** | `:508–510`, now standing over 28 rows rather than the 25 r14 checked. The round-13 row added this round is the one r14 described as "**none-of-one**" — the fix was absent, not decorated — which is expressly *not* the shape the sentence asserts. **Note 2 (D7)** |
| 25 | "Every one of C2's repair rounds has carried an error of its own" | **NOTE** | `:466`. True of rounds 1–13, each of which has at least one register row. It is a universal over a growing corpus that becomes false the first time a round is clean — including, on the strength of this review, in a fairly near future round. **Note 3 (D10)** |
| 26 | "The rest of those episodes are … not re-told here" | **NOTE** | `:517`, introduced at `75a97a18` and not softened when its sibling at `:467` was. The closing parenthetical at `:548–552` re-tells register row 5 at length. **Note 4 (D8)** |
| 27 | r14 C6 ("single largest source") actioned? | **PASS** | yes — deleted, not corrected. Closed |
| 28 | r14 C7 ("it is not re-told") actioned? | **PASS** | yes at the named site `:445`, softened to "generally". Closed at that site; see row 26 for the sibling |
| 29 | r14 C8 ("Its NOTE-level findings were acted on rather than deferred") | **NOTE** | `:417` unchanged. Three of r12's seven NOTE-level findings were acted on. Silently carried to a third round. **Note 5 (D3)** |
| 30 | r14 C9 (a disclosure attributed to r12 that r12 does not contain) | **NOTE** | `:409` — I re-checked `REVIEW_C2_PREFREEZE_R12.md` by grep: it contains no hand-tally disclosure, only "Counts extracted mechanically … not hand-tallied". r13 made that disclosure. **This commit rewrote that very sentence** to delete the exhaustiveness clause beside it and left the false half standing. Third round. **Note 6 (D2)** |
| 31 | r14 C10 ("the only occasion on which C2 has departed…") | **NOTE** | `:369` unchanged, an unbounded universal. Fourth round. **Note 7 (D4)** |
| 32 | r14 C11 ("four independent reviews (r5, r6, r7, r8)") | **NOTE** | `README.md:101–103` unchanged; `ERRATUM_C2.md:31` enumerates the same four. True and non-exclusive; undercounts and drifts every round. Fourth round. **Note 8 (D5)** |
| 33 | r14 C12 ("one is a scientific or decision value") | **NOTE** | `:29–30` unchanged; nine leaves per `:49` and `README.md:93–94`. Fourth round. **Note 9 (D6)** |
| 34 | the two "No such claim is made" compliance clauses | **NOTE** | `:313` and `:399`, both inside sentences this commit edited. Self-referential claims about the document's own prose, of the species `:332` says was "deleted rather than maintained". **Currently true** — every surviving "prose contains no counts" sentence is a historical quotation — but stale-capable by construction. Not on r14's list. **Note 10 (D9)** |
| 35 | `OPEN_NOTES_DISPOSITION_C2.md` N9 "no campaign has built one" | **NOTE** | a universal over the programme's campaigns, unverifiable from this namespace and stale-capable. Long-standing, harmless, listed only so the class list is complete. **Note 11 (D11)** |
| 36 | did the commit introduce any other new defect? | **PASS** | I read all 40 added `ERRATUM_C2.md` lines and the one added `README.md` line individually. Note 1 is the only false one; Notes 2, 3 and 4 are tensions the commit sharpened rather than created |
| 37 | `c2_mutations.py` reproduces byte-for-byte | **PASS** | re-run into scratch; `cmp` clean against `evidence/prefreeze/C2_MUTATIONS.json`; `applied 43`, `real_mutants 35`, `static_assertions 8`, `detected 40`, 3 proven-equivalent, `undetected []`, `pass true`, `sha256 512180f32a5ca85355270f57bc98c5281d8bb8de7f9e32a1d10652e1e0a4ebac` matching the file's own sha |
| 38 | `c2_critical_ratio.py` reproduces byte-for-byte | **PASS** | `cmp` clean against `evidence/phase_d5/C2_CRITICAL_RATIOS.json` |
| 39 | `c2_d1_blocker.py` reproduces byte-for-byte | **PASS** | `cmp` clean against `evidence/phase_d1/C2_D1_BLOCKER.json` |
| 40 | `c2_b0_verify.py` reproduces with only the expected drift | **PASS** | leaf-by-leaf diff: exactly one differing leaf, `/B1_git/head` `5289b6ce…` → `757db96a…` |
| 41 | class, closed subset, open subset | **PASS** | `C2_D5_FORECAST.json`: `D_STAGE_CLASS = D_PARTIAL`, `closed = [305, 306]`, `still_open = [307, 308, 309]` |
| 42 | the three gap falls | **PASS** | `0.46285183476411584` / `0.24593099374719365` / `0.18389841084966285` on 307 / 308 / 309 — the published figures |
| 43 | Γ(305) and Γ(306) | **PASS** | `-0.08802906884054082` and `-0.030469257709306738`, i.e. `−0.088029069` and `−0.030469258`; both negative, both cells close |
| 44 | `C2_RECERTIFY_306.json` verdict and accounting | **PASS** | `BOTH_PASSES_OK`; re-tallied from the artifact: consumed constants (C_T, tau, D_lo, D1, D2) **45/45 ok** in `determinism_256` **and** in `safe_side_384`; `certified: true` on 18/18 in both; `all_ok: true` both; `diagnostic_deviations {count 27, worst_relative 5.3188e-30}` |
| 45 | all changes since `5289b6ce` are additions | **PASS** | `git diff --name-status 5289b6ce..757db96a` → **145** rows, all `A`, zero `M`/`D`/`R` (144 at r14's HEAD, plus the r14 review file) |
| 46 | every change is inside the C2 namespace | **PASS** | no changed path outside `level4/closure_proofs/p5y_k5_tail_c2_closure/` |
| 47 | `main` untouched | **PASS** | `main` = `c123b9bb`, an ancestor of `757db96a` |
| 48 | predecessor namespaces untouched | **PASS** | empty diff since `5289b6ce` over all five predecessor namespaces |
| 49 | frozen gate sha, at exactly one commit | **PASS** | `shasum -a 256 config/FEASIBILITY_GATES_C2.json` = `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`; `git log --all` on that path returns exactly one commit, `87309610` |
| 50 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS** | the most recent commit touching either is `5a94568a` |
| 51 | coverage map r4 intact, no r5 | **PASS** | `K5_COVERAGE_MAP_R4.json` sha256 `a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35`, matching the README's `a3bddd83…`; untouched since `5289b6ce`; the only other map in `level4/` is the predecessor's R3 |
| 52 | nothing pre-empting freeze, qualification, seal or adjudication | **PASS** | no freeze, seal, qualification or adjudication artifact in the namespace; `phase_r/R_STAGE_DESIGN.md:1–5` states DESIGN ONLY, guard **DENY**, `NEW_REAL_ADDRESSES = 0`; `CELL_306_ADOPTION.md` is a disposition of the predecessor reviewer's conditions |
| 53 | all fourteen prior review files committed and unedited | **PASS** | each has exactly one commit in `git log -- <file>`; none amended |
| 54 | all fourteen prior reviews returned NOT_READY | **PASS** | extracted by script from each file's VERDICT line |
| 55 | code comments, docstrings and committed JSON free text swept | **PASS** | every universal in `code/` and in the committed JSON is scoped to a frozen artifact, a frozen registry or the mathematics — not to a mutable corpus. I re-derived C19 independently: no host/machine/platform/toolchain/build field exists anywhere in `evidence/registry_c2/` |
| 56 | working tree clean before and after my re-runs | **PASS** | `git status --porcelain` empty both times; all producer output written to scratch |

---

## Notes

### Note 1 (FAIL 1) — "unremarked by eight reviews" is false, and two committed review files say so

`ERRATUM_C2.md:454`, written this round:

> | **r14 Note 4** | "Sixth instance; r5 FAIL 1" — a hand-maintained ordinal in prose contradicting the register
> beside it, where that episode is the fifth row. **Present since `fb4d688b` and unremarked by eight reviews.** |
> The ordinal is deleted; the text points at the register row instead. |

The ordinal was remarked on, twice, by name, in files committed in this namespace:

- **`REVIEW_C2_PREFREEZE_R8.md:116–119`** — *"Note 4 (NOTE) — `ERRATUM_C2.md:378` 'Sixth instance; r5 FAIL 1'.
  The r5 FAIL 1 row is the fifth row of the instance table, and was the fifth of seven when this parenthetical was
  written at `fb4d688b`. … it is an off-by-one count in prose in the section about off-by-one counts in prose, and
  three rounds have passed over it. **Delete the ordinal.**"*
- **`REVIEW_C2_PREFREEZE_R9.md:154–156`** — *"`ERRATUM_C2.md:394`'s 'Sixth instance; r5 FAIL 1' is still an
  off-by-one … but r8 raised it as a non-blocking Note 4 and the campaign's own 'make the change and stop' doctrine
  makes leaving a note unactioned legitimate — **NOTE, not FAIL**, and it is already disclosed in a committed review
  file."*
- **`REVIEW_C2_PREFREEZE_R9.md:278–282`** — r9's Note 3 lists it again among r8's notes that "remain unactioned,
  **correctly**", and adds: *"I am recording that agreement so a tenth round does not treat them as accumulating
  debt."*

So the sentence is false on its face, and it is false in a particular direction. It does not merely miscount; it
converts a **knowingly deferred item, twice reviewed and once expressly agreed**, into an undetected stale defect
that eight independent reviews walked past. r8 diagnosed it, r9 ratified leaving it, and r9 wrote down in advance
the exact misreading the row now commits.

Two further facts make this the campaign's signature class rather than a slip:

1. **The premise was inherited, not derived.** It comes verbatim from r14's Note 4 ("the eight reviews since
   `fb4d688b` (r6 through r13) did not remark on"). r14 was wrong; C2 transcribed it without checking. The register
   this row sits in already carries two rows for exactly this — *"took r9's 'one place' premise unverified"*
   (r10 FAIL 3) and *"named r9, which had not done the diff"* (r10 FAIL 1) — both of which were FAILs in their
   round.
2. **It violates the rule C2 adopted and prints at `:382–383`**: *"never describe a corpus you can cite; if you
   must describe it, run the check before committing the sentence, and put the command in the text."* The corpus is
   fourteen committed files in `review/`. The check is `grep -rn 'Sixth instance' review/`. It takes a second and it
   returns r8 and r9.

**Why this is a FAIL and not a NOTE.** It is not a self-descriptive imperfection; it is a false statement of fact
about committed evidence, newly written, in the disposition register an adjudicator reads to judge what fourteen
rounds of independent review have actually been worth. Read as written, it says a defect survived eight
consecutive independent reviews unnoticed — a direct and materially wrong signal about the assurance this process
provides — and it erases a documented governance decision about deferred notes. `ERRATUM_C2.md` is the document
whose entire purpose is the accuracy of that record. The bar in the review request is "capable of misleading an
adjudicator about … the governance state, evidence provenance, or the campaign's reliability"; this clears it on
all three. The near-identical r10 FAIL 1 was rated FAIL by r10 on the same reasoning.

**Repair — one clause.** Replace "and unremarked by eight reviews" with what the record shows, for example:
*"Present since `fb4d688b`; raised by r8 as its Note 4 and left unactioned by agreement with r9, then re-raised as
a FAIL by r14."* If C2 prefers not to characterise the review corpus at all, delete the clause: the row loses
nothing an adjudicator needs.

*(Out of scope, but relevant to the round's reliability: the commit message states "Every claim written this round
was re-derived", and names four claims — all four of which I verified. This was the fifth, and it was not. I do
not ask for a commit message to be rewritten and I am not blocking on one; I record it because the shape is
r12 FAIL 1 and r13 FAIL 1 again, one level up — all-but-one, certified complete. No sentence in the namespace makes
that claim, which is correct.)*

### Note 2 (NOTE) — "The primary claim was sound every time" no longer fits the register it stands over

`:508–510`:

> Every instance has the same shape — **a correct primary argument or fix, with a second unverified thing stacked
> on top of it, or a neighbouring sentence the fix failed to carry along.** The primary claim was sound every time;
> the decoration and the leftovers were not.

r14 verified this SOUND against 25 rows (its C16). The commit under review added three rows, and the first of them
is the one r14 went out of its way to distinguish from every predecessor:

> That is the all-but-one shape r12 FAIL 1 and r13 FAIL 1 both named, and this time it is **none-of-one**: the
> commit edited a neighbouring word in the same sentence and left the count itself standing.

A repair that was not made, and was then certified as made, is not "a correct primary fix with decoration on top"
and is not "a neighbouring sentence the fix failed to carry along". The sentence now understates the campaign's
own failure mode in the flattering direction, three lines below the row that refutes it.

I record this as a NOTE and not a FAIL, and I want to be explicit about why, because it is close. The register
sits directly above the sentence and is honest; the r14 disposition section fifty lines up states "**not repaired
at all**" in bold; nothing is hidden from a reader who reads the table the sentence introduces. The claim is also
not crisply new — rows 488, 490 and 491 (the ledger rebuilt over the wrong corpus, the verifier misattribution)
already sat awkwardly under "sound every time", and four reviews passed it. It is a loose self-characterisation
that has become looser, not a false report of fact.

Repair: *"Most instances have the same shape — … The primary claim was usually sound; the decoration and the
leftovers were not. Round 13 is the exception: there the repair itself was absent and was recorded as complete."*

### Note 3 (NOTE) — "Every one of C2's repair rounds has carried an error of its own" is self-undermining

`:466`. True today: rounds 1–13 each hold at least one register row. But it is a universal over a corpus that
grows by one round per review, and it is the one claim in the document that becomes **false the moment the campaign
succeeds**. If a future round is clean, the sentence is wrong and will have to be edited — which is precisely the
edit that has generated defects for nine rounds.

Repair: scope it to the record. *"Every repair round recorded below has carried an error of its own."*

### Note 4 (NOTE) — the sibling absolute at `:517` was not softened with its twin

`:467` was softened this round from "it is not re-told" to "generally not re-told" (r14 Note 6, correctly
actioned). Its twin fifty lines down was not:

> `:517` — "The rest of those episodes are in the register rows above and **are not re-told here**."

The closing parenthetical at `:548–552` re-tells the r5 FAIL 1 episode — register row 5 — at length. Both
sentences make the same claim about the same section; one now carries a hedge and the other does not. r14 named
only the first site, so this is not a failure to repair; it is the all-but-one shape one more time, at NOTE level.
Repair: add "generally", or cut `:548–552` as r14 suggested.

### Note 5 (NOTE) — "Its NOTE-level findings were acted on rather than deferred" (r14 C8, r13 T6)

`:417`, unchanged for a third round. r12 raised seven NOTE-level findings; three were acted on. Defensible as an
introduction to the list that follows, as r13 said; still reads as a universal. Repair: "Three of its NOTE-level
findings were acted on rather than deferred:".

### Note 6 (NOTE) — a disclosure attributed to r12 that r12 does not contain (r14 C9, r13 T7)

`:409` credits r12 with having "disclosed that its own first draft of its verdict table was hand-tallied and
wrong". I grepped `REVIEW_C2_PREFREEZE_R12.md` for every form of the phrase: it says only *"Counts extracted
mechanically from the verdict column of the checklist above, not hand-tallied"*. **r13** made that disclosure
(`REVIEW_C2_PREFREEZE_R13.md`: "My first draft of this table read 29 PASS / 5 FAIL").

What raises this above the other carried NOTEs is that **this commit rewrote that sentence** — it deleted the
exhaustiveness clause sitting beside the falsehood, in the same clause of the same line, and left the falsehood.
Third round unactioned. It misattributes a governance behaviour between two review files, which is checkable in one
grep. It remains a NOTE because no decision turns on which review disclosed its own tally error, but it should not
reach an adjudicator a fourth time, and it should certainly not survive a repair that edits its sentence.

### Note 7 (NOTE) — "the only occasion on which C2 has departed from a reviewer's explicit instruction" (r14 C10)

`:369`, unbounded, unactioned for a fourth round (r11 Note 5, r12 S4, r13 Note 6, r14 Note 11). Repair by scoping
it to the r8/r9 episode.

### Note 8 (NOTE) — "four independent reviews (r5, r6, r7, r8)" (r14 C11)

`README.md:101–103` and `ERRATUM_C2.md:31`. True and non-exclusive; five further reviews have since run the
whole-history D1 leaf diff, so the enumeration drifts every round. Fourth round. Repair by citing rather than
enumerating.

### Note 9 (NOTE) — "one is a scientific or decision value" (r14 C12)

`:29–30`. The subject is leaves, and nine leaves are the scientific correction (`:49`, `README.md:93–94`). Locally
disambiguated by the apposition. Raised by r12, r13 and r14 and unactioned three times. Repair: "one *change* is a
scientific or decision value — nine leaves".

### Note 10 (NOTE) — the two "No such claim is made" compliance clauses

`:313` ("No such claim is made now") and `:399` ("No such claim is made any more"). Both are self-referential
claims about the document's own prose — the species `:332` records as having been *"deleted rather than
maintained"* because *"asserting 'no sentence states a count' is itself a falsifiable claim about every
sentence"*. **I verified both are currently true**: every surviving "prose contains no counts" sentence in the file
sits inside a historical quotation in a register or disposition row. They are nonetheless stale-capable by
construction, and both sit inside sentences this commit edited without reconsidering the clause. Not on r14's
list. Repair: delete the clause; the sentence that follows it ("where prose states a number it should simply be
right, and checked before it is written") carries the whole point without asserting compliance.

### Note 11 (NOTE) — "no campaign has built one"

`OPEN_NOTES_DISPOSITION_C2.md`, N9. A universal over the programme's campaigns, not checkable from this namespace
and stale the day a successor builds a second certifier. Long-standing, used honestly to *narrow* C2's claim, and
listed only so that the class list below is genuinely complete. No repair needed before freeze; a successor should
rescope it when it closes N9.

### Note 12 (INFO) — the empty `theorem/` directory

`theorem/` is present and empty, therefore not committed. r13 and r14 recorded the same. Harmless; mentioned only
so a sixteenth round does not re-discover it.

---

## Did every r14 repair land?

**Yes — all eight, verified individually in the diff and again in the file at HEAD, in both directions (string
present at `757db96a`, absent at `75a97a18`).** I checked this first and separately, because the campaign's failure
mode last round was certifying a repair that had not happened, and because the commit itself reports that a first
attempt "died on shell quoting and applied nothing while appearing to succeed".

| | claimed repair | landed? | evidence at HEAD |
|---|---|---|---|
| 1 | count removed from the **older** statement (r14 Note 1) | **yes** | `:312` "…contains no counts **more than once**…" — no numeral |
| 2 | count removed from the **other** statement (r14 Note 1) | **yes** | `:399` "C2 has **repeatedly** written a sentence…" — no numeral |
| 3 | `grep -c` instruction withdrawn in favour of the **caught by** column (r14 Note 2) | **yes** | `:520–522`; and the replacement is itself true — the grep returns 7, the column gives 4 |
| 4 | exhaustiveness clause deleted (r14 Note 3) | **yes** | `:408` now "listed surviving instances of the corpus-claim class" |
| 5 | "Sixth instance" ordinal deleted (r14 Note 4) | **yes** | `:552` now "See r5 FAIL 1 and its register row.)" |
| 6 | the underived superlative removed (r14 Note 5) | **yes** | `:466–467`; "single largest source" occurs nowhere in the namespace outside `review/` |
| 7 | the false absolute removed (r14 Note 6) | **yes** | `:467–468` "**generally** not re-told" |
| 8 | r5 note-8 attribution restored (r14 Note 8) | **yes** | `:512`; verified against `REVIEW_C2_PREFREEZE_R5.md:252–260` — that is indeed r5's note 8 |

Supporting edits, all present and accurate except where Note 1 says otherwise: the round-table row for r14, the
README review row, the new § "Dispositions from the FOURTEENTH pre-freeze review" with its four rows and its
narrative-reduction paragraph, and three new register rows correctly attributed to round 13.

**The r13 FAIL 2 row now records what actually happened** (`:438`), and its new claim — "Neither statement now
carries a count, so they cannot diverge" — is, this time, true; I read both sites at HEAD. That was the row whose
false certification was r14's FAIL 1, so it mattered that this one be exact, and it is.

**The three residual strings are historical quotations only.** `"so the two cannot diverge again"` at `:451`,
`"all seven surviving instances"` at `:453` and `"Sixth instance; r5 FAIL 1"` at `:454` each occur exactly once in
the namespace outside `review/`, each inside the **finding** column of an r14 disposition row, each reporting what
the superseded text said. None is a live claim. *(The separate defect in one of those rows' surrounding text is
Note 1, and is not about the quoted string.)*

---

## Is the corpus-claim class closed?

**No — but it is closer than it has been, and the shape of what remains has changed.** One live instance is false
(D1, Note 1). The other ten are unverified, overbroad, or stale-capable rather than false, and five of them
(D2–D6) are r14's C8–C12 carried forward with no repair and no acknowledgement anywhere in the namespace.

This is the ninth consecutive round in which a claim over a mutable corpus was written without the check being
run, and the second consecutive round in which the falsifying material was added **by the commit that made the
claim** — last round it was `grep -c` returning 7 instead of 4; this round it is a register that two committed
review files refute.

Below is every instance I found in the namespace — prose, tables, code comments, docstrings and committed JSON
strings — that is a universal, superlative or self-descriptive claim over a mutable corpus and is currently false,
unverified, or capable of going stale. I swept all nine `.md` files outside `review/`, all seven `.py` files in
`code/`, the free-text leaves of every committed JSON under `evidence/` and `config/`, and every added line of this
commit, by script and then by hand. **I have left none for a sixteenth round.**

| | site | the claim | status |
|---|---|---|---|
| **D1** | `ERRATUM_C2.md:454` | the ordinal was "Present since `fb4d688b` and **unremarked by eight reviews**" | **FALSE — FAIL, Note 1.** r8 Note 4 raised it and said "Delete the ordinal"; r9 recorded it twice, once as an explicit agreement to leave it |
| **D2** | `ERRATUM_C2.md:409` | r12 "**disclosed** that its own first draft … was hand-tallied and wrong" | **FALSE — NOTE 6.** r12's file contains no such disclosure; r13 made it. Third round; this commit rewrote the sentence around it (was r14 C9 / r13 T7) |
| **D3** | `ERRATUM_C2.md:417` | "Its NOTE-level findings **were acted on** rather than deferred" | **OVERBROAD — NOTE 5.** Three of r12's seven. Third round (was r14 C8 / r13 T6) |
| **D4** | `ERRATUM_C2.md:369` | "It is **the only occasion** on which C2 has departed from a reviewer's explicit instruction" | **UNBOUNDED — NOTE 7.** Fourth round (was r14 C10 / r13 T8) |
| **D5** | `README.md:101–103`, `ERRATUM_C2.md:31` | "**four** independent reviews (r5, r6, r7, r8) each confirmed this" | **STALE — NOTE 8.** Non-exclusive and true, but drifts every round. Fourth round (was r14 C11 / r13 T9) |
| **D6** | `ERRATUM_C2.md:29–30` | "Of the leaves replaced … **one** is a scientific or decision value" | **DIVERGENT — NOTE 9.** Nine leaves, per `:49` and `README.md:93–94`. Fourth round (was r14 C12 / r13 T10) |
| **D7** | `ERRATUM_C2.md:508–510` | "**Every** instance has the same shape … The primary claim was sound **every time**" | **NO LONGER TRUE — NOTE 2.** The round-13 row added this round is the "none-of-one" case r14 expressly distinguished. **Was r14's C16, rated SOUND over 25 rows; the register is now 28** |
| **D8** | `ERRATUM_C2.md:517` | "The rest of those episodes … **are not re-told here**" | **FALSE — NOTE 4.** `:548–552` re-tells register row 5. Sibling of r14's C7, not softened when its twin was |
| **D9** | `ERRATUM_C2.md:313`, `:399` | "**No such claim is made** now" / "any more" | **TRUE TODAY, STALE-CAPABLE — NOTE 10.** I verified both; every surviving "no counts" sentence is a historical quote. The species `:332` says was deleted rather than maintained. Not listed by r14 |
| **D10** | `ERRATUM_C2.md:466` | "**Every one** of C2's repair rounds has carried an error of its own" | **TRUE TODAY, SELF-UNDERMINING — NOTE 3.** Holds for rounds 1–13; becomes false the first time a round is clean. **Was r14's C17, rated SOUND** |
| **D11** | `OPEN_NOTES_DISPOSITION_C2.md`, N9 | "A second, independently written certifier is the real answer and **no campaign has built one**" | **UNVERIFIABLE IN-NAMESPACE, STALE-CAPABLE — NOTE 11.** Used honestly, to narrow rather than widen. Not listed by r14 |

**Sound side.** I re-derived r14's C13, C14, C15, C18, C19, C21 and C22 here and found each exact — in particular
C13, which has moved: the round table now sums to **38** and the document carries **38** disposition rows, matching
one for one. C20 I spot-checked and it is still correctly narrowed. **C16 and C17 I have moved to the live list**
(D7, D10) for the reasons given; both were sound when r14 checked them and were falsified or loosened by rows added
afterwards. A sixteenth round should not need to re-derive C13–C15 or C18–C22.

**What would close the class.** D1 must be repaired before freeze. D2–D11 are NOTEs and the campaign may freeze
over them — but D2, D4, D5 and D6 have each now been named by three or four consecutive reviews and repaired by
none, and a sixteenth round that fixes D1 alone will be the tenth round in which the class migrates rather than
closes. The cheapest close is mechanical, not editorial: every one of D2–D11 is repaired by deleting a word or
scoping a sentence to a citable artifact, and the whole set is smaller than the repair C2 has performed in each of
the last four rounds.

---

## Did this repair introduce a new defect?

**Yes — one (Note 1), and I assumed it had until I had read every changed sentence.** I extracted all 40 added
lines of `ERRATUM_C2.md` and the one added line of `README.md` and checked each independently:

- The **round-table row**, the **README row** and the **section title** they point at: consistent, and `75a97a18`
  is the commit r14 reviewed.
- The **r14 disposition section's opening paragraph**: every claim traced to r14's file and independently
  confirmed (9 markdown files, 7 Python files, 25 register rows at that commit, the two-column tally disclosure).
- **r14 Note 1's row**: accurate — I confirmed from `git show 6d987390` that the only change in that sentence was
  `both times` → `each time`.
- **r14 Note 2's row**: accurate — I ran the grep at three commits: 4 at `92bc9637`, 7 at `6d987390`, 7 at HEAD.
- **r14 Note 3's row**: accurate — r12 labels S1–S7, r13 labels T1–T11.
- **r14 Note 4's row**: the ordinal and the register position are right; **the clause about eight reviews is
  false** — Note 1.
- The **narrative-reduction paragraph**: accurate, including "two of r13's three FAILs were not in that section",
  which I verified against the section boundaries myself.
- The **three new register rows**: accurate and correctly attributed to round 13.
- The **reduced opener**, the **r5 note-8 attribution**, the **grep withdrawal** and the **deleted ordinal**: all
  correct, and the grep withdrawal's new negative claim ("a `grep -c` over this whole file does not work") is true.

Notes 2, 3 and 4 are tensions this commit **sharpened** rather than created: it added the register rows that
falsify D7, it left one of two twin absolutes hedged, and D10 was already standing. I have not counted any of them
as newly introduced.

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
- The fourteen prior review files end to end. I read r5, r8, r9, r12, r13 and r14 in the parts that bear on my
  findings, extracted every verdict line by script, and confirmed each file's commit count is one.
- r14's C13–C15 and C18–C22 I re-derived; C20 I spot-checked rather than re-derived in full.
- Commit messages as a corpus. I read the one under review and quote it once in Note 1; I did not sweep the
  campaign's commit messages, which are immutable and outside the namespace.

---

## Verdict counts

Extracted from the checklist table above by script, not by hand:

| verdict | rows |
|---|---|
| PASS | 45 |
| FAIL | 1 |
| NOTE | 10 |
| INFO | 0 |
| **total rows** | **56** |

45 + 1 + 10 + 0 = 56, reconciling against the table; rows are numbered contiguously 1–56 with none missing.

**Distinct blocking defects: 1** — Note 1, at checklist row 19.

**NOTE-level findings: 10** — Notes 2 through 11, at checklist rows 24, 25, 26, 29, 30, 31, 32, 33, 34 and 35.
Note 10 covers two sites (`:313` and `:399`) in a single row. Note 12 is INFO and has no checklist row.

*Disclosure, because Note 1 is about exactly this.* My first draft of this table read 44 PASS / 11 NOTE. I had
written it from my count of the Notes section rather than from the checklist, which is the same mechanism as the
defect I am blocking on: a claim about a corpus, stated before the check was run. The figures above are the
script's — it parses the verdict column of the table as committed, and I re-ran it against this file after the
edit. A sixteenth reviewer should re-run the extraction rather than trust the table, for the reason
`ERRATUM_C2.md:382–383` gives.

---

## Where I landed

The request asked me to say plainly whether the bar has been set right, and whether a residual imperfection in an
errata document genuinely rises to a FAIL. My answer is that the calibration is right and that **this one does**,
for a reason that has nothing to do with prose quality: `ERRATUM_C2.md:454` is not a clumsy self-description, it is
a false statement about what is written in two other committed files, and the thing it is false about is how much
independent scrutiny this namespace has received. Fifteen rounds of review are the whole of the governance
evidence here. A sentence in the campaign's own defect register telling an adjudicator that eight of those rounds
walked past a defect — when two of them found it, named it, and one recorded a reasoned decision to leave it — is
the kind of error this process exists to catch, and it is refuted by one grep over a directory in the same
namespace.

I want to be equally plain about what I did **not** block on. The science is untouched and reproduces bit-exactly
for the fifteenth time. The integrity envelope is exact. Every one of the eight repairs r14 asked for landed, which
is more than the last two rounds managed, and the r13 FAIL 2 row — the row whose false certification was last
round's headline — is now accurate. Notes 2, 3, 4 and 10 are real and I have listed them, but none of them would
have held up a freeze on its own, and I say so explicitly so that a sixteenth round does not treat this list as
eleven blockers. It is one blocker and ten pieces of cleanup, most of which have been sitting in three consecutive
review files.

**The namespace is one clause away from fit to freeze.** Repair `:454` — and, I would urge, sweep D2–D11 in the
same commit, since together they are smaller than any of the last four repair rounds — re-run the check before
committing each sentence, and the next review should be able to say so.

**VERDICT: NOT_READY.**
