# Campaign C2 — fourteenth independent pre-freeze review

**VERDICT: NOT_READY**

The science, the gate and the integrity envelope are clean for the fourteenth consecutive round, and I reproduced
all of it here rather than inheriting it: three producers byte-for-byte, `D_PARTIAL` with closed = {305, 306}, the
three gap falls, both Γ, `BOTH_PASSES_OK` with 45/45 consumed constants at both precisions and 18/18 certified,
144 additions and zero modifications or deletions since `5289b6ce`, the gate at one commit, `main` untouched.
None of that is in question and none of it has ever been.

What blocks the freeze is four textual defects. Two are in the two commits under review (Notes 1 and 2); one
entered at `92bc9637`, the commit r13 reviewed, and r13 did not name it (Note 3); one has stood since the
round-five repair `fb4d688b` unremarked by every review since (Note 4).

The first is decisive on its own: **r13 FAIL 2 is not repaired.** The two divergent counts r13 named — "twice" at
`ERRATUM_C2.md:310` and "three times" at `:398` — still disagree, verbatim, and the disposition row written for
that FAIL asserts "The count is removed from the older statement, so the two cannot diverge again." That is the
all-but-one shape r12 FAIL 1 and r13 FAIL 1 both named, and this time it is none-of-one: the commit edited a
neighbouring word in the same sentence and left the count itself standing.

---

## Reviewer context

I am an independent fresh-context reviewer. I wrote no part of Campaign C2 and had no involvement in rounds one
through thirteen. I reviewed `p5y-k5-tail-c2` at `75a97a18` in the worktree `/Users/suzhe/ReBaseGuard-k5c2`,
starting from `git diff 92bc9637..75a97a18` as the review request directed, and then sweeping the whole namespace
independently. I re-ran the producers into a scratch directory outside the repository and compared bytes; I
re-extracted every count I report from the files by script rather than by eye, after being warned that r12's and
r13's own first verdict tables were both hand-tallied and wrong. I modified no file in this namespace except this
one, ran no writing git command, and did not touch AWS or any remote host. The working tree was clean before I
started and clean when I finished.

I relied on r13's V1–V12 sound-claim list where the review request permits, and re-derived the parts of it that
bear on my findings (the replacement-ledger figures, the register tallies, the 45/45 accounting). I did not find
reason to doubt any V-row.

---

## Checklist

| | check | verdict | evidence |
|---|---|---|---|
| 1 | `c2_mutations.py` reproduces byte-for-byte | **PASS** | re-run into scratch; `cmp` clean against `evidence/prefreeze/C2_MUTATIONS.json`; `applied 43`, `real_mutants 35`, `static_assertions 8`, `detected 40`, 3 proven-equivalent, `undetected []`, `pass true`, sha256 `512180f32a5ca853…` matching both the artifact's own field and the file's sha |
| 2 | `c2_critical_ratio.py` reproduces byte-for-byte | **PASS** | `cmp` clean against `evidence/phase_d5/C2_CRITICAL_RATIOS.json` |
| 3 | `c2_d1_blocker.py` reproduces byte-for-byte | **PASS** | `cmp` clean against `evidence/phase_d1/C2_D1_BLOCKER.json` |
| 4 | `c2_b0_verify.py` reproduces with only the expected drift | **PASS** | single-leaf diff, `head` `5289b6ce…` → `75a97a18…`; nothing else differs |
| 5 | class, closed subset, open subset | **PASS** | from `C2_D5_FORECAST.json`: `D_STAGE_CLASS = D_PARTIAL`, `closed = [305, 306]`, `still_open = [307, 308, 309]` |
| 6 | the three gap falls | **PASS** | `0.46285183476411584` / `0.24593099374719365` / `0.18389841084966285` on 307 / 308 / 309 — the published `0.46285183 / 0.24593099 / 0.18389841` |
| 7 | Γ(305) and Γ(306) | **PASS** | `-0.08802906884054082` and `-0.030469257709306738`, i.e. `−0.088029069` and `−0.030469258`; both negative, both cells close |
| 8 | `C2_RECERTIFY_306.json` verdict and accounting | **PASS** | `BOTH_PASSES_OK`; re-tallied from the artifact rather than its prose: consumed constants (C_T, tau, D_lo, D1, D2 over nine artifacts) `45/45 ok` in `determinism_256` **and** in `safe_side_384`; `certified: true` on 18/18 in both passes; `all_ok: true` both passes; `diagnostic_deviations {count 27, worst_relative 5.3188e-30}` |
| 9 | the one substantive point retained by the reduction | **PASS** | recomputed from `C2_D1_BLOCKER.json` cell 309: D_lo `relative_gain` `0.08718592913635831`, τ `0.08168084117495086`; ratio `1.0673975…` = **1.0674**; difference `0.00550508796…` = **0.005505**; ×11 = `0.06055596757…` = **0.060556**. The retained sentence is exactly right on both halves |
| 10 | `0.932851` (max D_lo × 1.1) still present and unaltered | **PASS** | present once, at `:500`; the value itself I did not recompute — see "What I did not check" |
| 11 | all changes since `5289b6ce` are additions | **PASS** | `git diff --name-status 5289b6ce..75a97a18` → 144 rows, all `A`, zero `M`/`D`/`R` |
| 12 | every change is inside the C2 namespace | **PASS** | no changed path outside `level4/closure_proofs/p5y_k5_tail_c2_closure/` |
| 13 | `main` untouched | **PASS** | `main` = `c123b9bb`, an ancestor of `75a97a18`, unchanged |
| 14 | predecessor namespaces untouched | **PASS** | empty diff since `5289b6ce` over `p5y_k5_lower_front_order3`, `p5y_k5_perron_deflated_resolvent`, `p5y_k5_tail_operator_registry`, `p5y_k5_m5_tail_closure`, `p5y_k5_remaining_cell_closure` |
| 15 | frozen gate sha, at exactly one commit | **PASS** | `shasum -a 256 config/FEASIBILITY_GATES_C2.json` = `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`; `git log --all` on that path returns exactly one commit, `87309610` |
| 16 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS** | last commit touching either is `5a94568a` |
| 17 | coverage map r4 intact, no r5 | **PASS** | `K5_COVERAGE_MAP_R4.json` sha256 `a3bddd83234f3398…`, matching the README's `a3bddd83…`; the file is untouched since `5289b6ce`; no r5 map exists anywhere in `level4/` |
| 18 | nothing pre-empting freeze, qualification, seal or adjudication | **PASS** | no freeze, seal, qualification or adjudication artifact in the namespace; `phase_r/` states DESIGN ONLY and guard DENY; `NEW_REAL_ADDRESSES = 0`; `CELL_306_ADOPTION.md` is a disposition of the predecessor reviewer's conditions, not an adoption record |
| 19 | all thirteen prior review files committed and unedited | **PASS** | each of the thirteen has exactly one commit in `git log -- <file>`; none has ever been amended |
| 20 | all thirteen prior reviews returned NOT_READY | **PASS** | extracted by script from each file's VERDICT line |
| 21 | working tree clean before and after my re-runs | **PASS** | `git status --porcelain` empty both times; all producer output written to scratch |
| 22 | r13's "115 committed files under `evidence/` and `config/`" | **PASS** | `git ls-tree -r --name-only 75a97a18` over those two paths → 115 |
| 23 | r13 FAIL 1 — the surviving header is stripped | **PASS** | `:73` now reads `**6 FAIL**.` with the `60 PASS / 10 INFO / 3 NOT_CHECKABLE_LOCALLY` transcription gone |
| 24 | r13 FAIL 1 — no disposition header still carries sub-counts | **PASS** | printed all thirteen `## Dispositions from the …` headers and the three lines following each; every one carries a FAIL count only |
| 25 | r13 FAIL 1 — the exhaustiveness claim deleted rather than corrected | **PASS** | `:420` is now scoped to "the disposition headers" (true, per row 24), and `:424–426` tells the reader to grep for `PASS` instead of asserting a result. Correctly done |
| 26 | **r13 FAIL 2 — the divergence r13 named is repaired** | **FAIL** | it is not. `:310` still reads "C2 has **twice** written a sentence here claiming its prose contains no counts"; `:398` still reads "…carries no counts **three times**". The commit changed "both times" → "each time" in the same sentence and left the count. **Note 1** |
| 27 | r13 FAIL 2 — the disposition row records the repair accurately | **FAIL (same finding)** | `:438` asserts "The count is removed from the older statement, so the two cannot diverge again." Both halves are false. **Note 1** |
| 28 | r13 FAIL 3 — the self-flattering claim withdrawn | **PASS** | "the self-audit is now finding these faster than the reviews are" is gone; `:493–494` records it as false when written and false for six rounds, attributed to r13 FAIL 3 |
| 29 | r13 FAIL 3 — the replacement figures are right | **PASS — tallied mechanically** | over the 25 register rows: **4** rows marked `self-caught`, in rounds **4 and 5** only; rounds **6–11** contribute exactly **12** rows, **0** of them self-caught. Every figure in the withdrawal reconciles |
| 30 | **r13 FAIL 3 — the derivation the text offers reproduces the figure** | **FAIL** | `:495` instructs the reader to run `grep -c 'self-caught' ERRATUM_C2.md`. It returns **7**, not 4 — because `6d987390` itself added three further occurrences of the string (`:439`, `:495`, `:496`) in the act of writing the instruction. **Note 2** |
| 31 | all 25 repair-register rows survive the reduction | **PASS — tallied mechanically** | 25 rows, distributed 1/1/2/3/4/1/1/3/3/2/2/2 over rounds 1–12; identical to the pre-reduction file |
| 32 | the second register survives | **PASS** | `:475–480`, the r2-note-4 row, untouched |
| 33 | the operational lesson survives | **PASS** | `:504–509`, "when a review asks for one change, make that change and stop", untouched |
| 34 | the r13 FAIL 3 withdrawal survives the reduction | **PASS** | `:493–497`, including the unflattering corrected reading |
| 35 | every figure the reduction claims it preserved is present | **PASS** | `0.932851`, `1.0674` (×2), `0.005505`, `0.060556`, `five-and-two`, `four-and-three` all present |
| 36 | the reduction lost nothing load-bearing | **NOTE** | one loss: the attribution of the ratio-vs-difference qualification to **r5 note 8** is dropped, so a successor reading the retained paragraph cannot see where it came from. Everything else removed is carried by a register row. **Note 8** |
| 37 | **the reduction's new opening claim is checked** | **NOTE** | `:443–445` asserts this section's narrative "has been the **single largest source** of the defects it describes" — an unverified superlative over the register, and one the document's own r13 rows cut against: two of r13's three FAILs sat in the *disposition* sections, not here. **Note 5** |
| 38 | **the reduction's new editorial rule is true of the section** | **NOTE** | `:445` asserts "Where an episode is in a register row, it is not re-told." False as written: `:521–525` re-tells the r5 FAIL 1 episode at length, and that episode is register row 5. **Note 6** |
| 39 | the reduction targeted where r13's FAILs actually lived | **NOTE** | it did not; and the two `r13 FAIL 2` sites it left untouched are the ones still defective. **Note 7** |
| 40 | r13 T1 / T2 / T3 (the sub-count exhaustiveness claims) | **PASS** | closed by deletion and rescoping; verified at rows 23–25 |
| 41 | r13 T4 ("the self-audit is now finding these faster") | **PASS** | closed by withdrawal; verified at row 28 |
| 42 | r13 T5 (the "twice" / "three times" divergence) | **FAIL (same as row 26)** | open. **Note 1** |
| 43 | r13 T6 ("Its NOTE-level findings were acted on rather than deferred") | **NOTE** | tense changed, substance unchanged: r12 raised seven NOTE-level findings and three were acted on. Still reads as a universal. **Note 9** |
| 44 | r13 T7 (a disclosure attributed to r12) | **NOTE** | `:409` unchanged; r12's committed file contains no such disclosure, only "Counts extracted mechanically … not hand-tallied". **Note 10** |
| 45 | r13 T8 ("the only occasion on which C2 has departed from a reviewer's explicit instruction") | **NOTE** | `:367–368` unchanged, an unbounded universal with at least one further candidate — `75a97a18` itself cuts prose that r10 said to keep. **Note 11** |
| 46 | r13 T9 ("four independent reviews (r5, r6, r7, r8)") | **NOTE** | `README.md:100–101` and `ERRATUM_C2.md:29–31` unchanged; true and non-exclusive, now undercounting by three. **Note 12** |
| 47 | r13 T10 ("one is a scientific or decision value") | **NOTE** | `:28` unchanged; reads as a leaf count and the ledger twenty lines below says nine. Locally disambiguated. Third consecutive round deferred. **Note 13** |
| 48 | **r13 T11 ("every hand-maintained tally was deleted from the prose")** | **FAIL** | `:308–309` is still false of the present: `:525` carries "**Sixth instance**", a hand-maintained ordinal in prose that the register beside it contradicts. **Note 4** |
| 49 | **`:408` — "listed all seven surviving instances … rather than leaving any for a later round"** | **FAIL** | false. r12 listed S1–S7; r13 then listed eleven, of which at least T4 and T11 were present and unlisted at r12's round. r12's own file makes no exhaustiveness claim, so the universal is C2's. **Note 3** |
| 50 | **`:525` — "Sixth instance; r5 FAIL 1"** | **FAIL (same as row 48)** | the r5 FAIL 1 episode is register row **five**, and was row five when the phrase was written at `fb4d688b`. **Note 4** |
| 51 | code comments, docstrings and committed JSON strings swept for the class | **PASS** | 181 candidate lines extracted by script across all `.md` and `.py` outside `review/`, then triaged; every universal in `code/` and in `C2_RECERTIFY_306.json`'s free text is scoped to a frozen artifact or to a named file, not to a mutable corpus |
| 52 | the ledger's own scope sentence | **PASS** | `:38` "Every leaf this campaign has replaced in an already-committed evidence file", immediately followed by "Do not trust this table — regenerate it", with the command. This is the class handled correctly and is the model the rest of the document should follow |
| 53 | the two new register rows are accurate | **PASS** | both round-12 rows match r13's Note 1 and Note 2 exactly. The second says the document "now contradicted itself on it" in the past tense, which understates the position — it still does (Note 1) |
| 54 | r13's own round-table and README rows | **PASS** | `| r13 | 92bc9637 | 3 FAIL |` — `92bc9637` is the HEAD r13 reviewed; README row "NOT_READY — **3 FAIL**"; r13's file has exactly three FAIL-bearing notes and returns NOT_READY |
| 55 | **did these two commits introduce a new defect?** | **FAIL** | yes — Note 2 (a derivation command false the moment it was written, inside the repair of the FAIL about unverified self-description), plus Notes 5 and 6 at NOTE level. Notes 1, 3 and 4 are failures to repair or pre-existing |
| 56 | r13's V1–V12 sound-claim list | **INFO** | relied on as the review request permits; I re-derived the register tallies, the 45/45 accounting and the ledger figures that bear on my findings and found no V-row in doubt |

---

## Notes

### Note 1 (FAIL 1) — r13 FAIL 2 is not repaired, and the disposition row says it is

r13's FAIL 2 was that two statements of one fact disagreed:

- `ERRATUM_C2.md:310` — "*(C2 has **twice** written a sentence here claiming its prose contains no counts, and
  **both times** the claim was false…"
- `ERRATUM_C2.md:398` — "C2 has written a sentence claiming its prose carries no counts **three times**, and each
  time the claim was false…"

r13 quoted both, at its checklist rows 17 and 18, and named the second site explicitly as untouched.

`6d987390` changed exactly one word at `:310`: **"both times" → "each time"**. The count — "twice" — was not
touched. The document therefore still says "twice" in one place and "three times" in another, 88 lines apart,
about the same fact.

The disposition row written in the same commit, at `:438`, reads:

> | **r13 FAIL 2** | … one said C2 had written a "prose contains no counts" sentence **twice**, the other **three
> times**. r12 had named both sites; only one was repaired. | The count is removed from the older statement, so
> the two cannot diverge again. |

The count is not removed from the older statement. The two can and do diverge. The finding column of that row
quotes the exact word that survives three lines of its own repair column.

**Why this is a FAIL and not a NOTE.** This is the recurring shape the review request asked me to look for —
all-but-one repaired and recorded as complete — and it is the sharpest instance yet, because it is none-of-one:
the repair edited a word adjacent to the defect and then certified the defect as gone. It sits in the register
that an adjudicator reads to judge whether this campaign's self-reports can be taken at face value. A row in that
register that falsely certifies its own repair is not a stylistic matter; it is the register failing at the one
job it has. That it happened in the round immediately after r13 named the identical shape, in the row created to
dispose of it, is the material fact about the campaign's reliability, and an adjudicator should have it.

The repair is one word: delete "twice" from `:310`, or delete "three times" from `:398`, leaving exactly one
statement of the fact. Do not update both to agree — that sets the same trap the campaign has now sprung nine
times.

### Note 2 (FAIL 2) — the derivation offered for the r13 FAIL 3 withdrawal does not reproduce its own figure

`:493–497` withdraws the self-flattering claim and, correctly, replaces it with the register's actual position.
The figures are right; I re-derived all of them (checklist row 29). But the text tells the reader how to check:

> Derive it from the register above — `grep -c 'self-caught' ERRATUM_C2.md` against the row count — and the
> position is: of the instances recorded, **four** were self-caught…

That command returns **7**, not 4. Four hits are the register rows; the other three are prose — `:439` (the r13
FAIL 3 disposition row), `:495` and `:496` (the withdrawal paragraph itself). All three were added by the same
commit that wrote the instruction. At `92bc9637`, before the commit, the command returned 4; `6d987390` broke it
and shipped it in the same change.

This is the eight-round class exactly: a claim over a mutable corpus committed without running the check — and
this time the check *is* the claim, written into the instrument built to end the class, in the repair of the FAIL
about unverified self-description. It will drift further with every round that mentions the word.

**Why this is a FAIL and not a NOTE.** r10's rule, which C2 adopted and prints at `:382–383` — "*never describe a
corpus you can cite; if you must describe it, run the check before committing the sentence, and put the command in
the text*" — was followed to the letter and still produced a false statement, because the command was never run.
An adjudicator who follows the campaign's own instruction gets a number that contradicts the campaign's own
conclusion, in the paragraph the campaign offers as its most honest. That is capable of misleading about how much
weight the document's verification instructions can carry.

Repair: either scope the command to the table (for instance `grep -c '| \*\*self-caught\*\*' ERRATUM_C2.md`,
after checking it), or drop the command and say "count the rows marked `self-caught` in the register above".

### Note 3 (FAIL 3) — "all seven surviving instances", an exhaustiveness claim r12 never made and that is false

`:408`:

> It also listed all seven surviving instances of the corpus-claim class rather than leaving any for a later
> round…

r12 did list seven instances, S1–S7. It did not claim they were all of them; I grepped its committed file and it
contains no exhaustiveness claim. C2 supplied the universal.

The universal is false. r13, one round later, listed eleven (T1–T11). Of those, at least two were present in the
document at r12's round and were not on r12's list:

- **T4** — "the self-audit is now finding these faster than the reviews are", which r13 FAIL 3 established had
  been false for six rounds, so it was false and present when r12 swept.
- **T11** — `:308–309` "So every hand-maintained tally was deleted from the prose that carried it", which predates
  r12 by six rounds.

So r12 did leave instances for a later round, and the sentence saying it did not is a superlative over a mutable
corpus asserted without running the check — inside the paragraph that reports the class being closed.

**Why this is a FAIL and not a NOTE.** The open question before the adjudicator is precisely whether the
corpus-claim class is closed. A sentence in the namespace telling them that a prior round enumerated it
exhaustively, when the next round found four more, misleads them about exactly that. Repair by deleting "all" and
"rather than leaving any for a later round": "It also listed seven surviving instances of the corpus-claim class."

### Note 4 (FAIL 4) — a stale hand-maintained ordinal, in the section reduced to remove them, falsifying the document's own de-counting claim

`:525`, the closing parenthetical of § "The pattern, named":

> …A stale, self-contradicting remnant left by a repair, inside the section about stale remnants left by repairs.
> **Sixth instance**; r5 FAIL 1.)*

The r5 FAIL 1 episode is register row **five** (`:453`, "replaced this section's opening with a table | left the
superseded paragraphs underneath"). It was row five when the phrase was written, at `fb4d688b`: I checked that
revision, where the register had seven rows and the r5 FAIL 1 row was the fifth. The document nowhere says what
else "instance" might be counting, so as it stands the ordinal does not reconcile with the register it sits
beside.

Two consequences:

1. It is a hand-maintained count in prose, contradicting an adjacent table — the exact defect that produced r6
   FAIL 1, r7 FAIL 1 and r8 FAIL 1, and which the document says at `:507` is "left to the table, deliberately".
2. It falsifies `:308–309`, "So every hand-maintained tally was deleted from the prose that carried it" — r13's
   T11, which r13 rated a NOTE on the strength of `:73`. `:73` is now stripped; this one is not, so T11's sentence
   remains false and now has a counterexample that the eight reviews since `fb4d688b` (r6 through r13) did not
remark on.

**Why this is a FAIL and not a NOTE.** The register is the campaign's defect record, and a prose ordinal that
miscounts a row of it corrupts that record in the direction of overstating the count. It is also the surviving
counterexample to a normative claim the document makes about itself. That `75a97a18` reduced this very section on
the ground that its narrative breeds stale counts, and left the stale count in the paragraph it did not touch, is
the point.

Repair: delete "Sixth instance;" — the ordinal adds nothing that "r5 FAIL 1" does not already say, and the
register carries the position.

### Note 5 (NOTE) — "the single largest source of the defects it describes" is unverified, and the commit message's stronger version is false

`:443–445`, new at `75a97a18`:

> The registers below are the record; the prose after them is deliberately short, because this section's narrative
> has been the **single largest source** of the defects it describes.

This is a superlative over the 25-row register and is not derived anywhere. It may well be true; it is not
checked, and the document offers no way to check it. It is the justification an adjudicator is being asked to
accept for a structural edit, so it should either be derived or stated as a judgement rather than a fact.

The commit message states a stronger version which is false: "r13 FAIL 1, FAIL 2 and FAIL 3 were all in that
prose." They were not, and this document says so three paragraphs above. r13 FAIL 1 was in the paragraph
dispositioning r12 (`:417–426`, § "Dispositions from the TWELFTH pre-freeze review"); r13 FAIL 2's two sites are
`:310` (§ SIXTH) and `:398` (§ ELEVENTH). Only FAIL 3 was in § "The pattern, named". Commit messages are immutable
and I am not asking for one to be rewritten, but the in-namespace sentence rests on the same premise.

I am recording this as a NOTE rather than a FAIL because it is a self-descriptive judgement in an errata document
and misleads nobody about the science, the decision, the governance state or provenance. It is listed in the
corpus-claim table below because it is an unverified superlative over a mutable corpus and will go stale.

### Note 6 (NOTE) — "Where an episode is in a register row, it is not re-told" is false of the section that says it

`:445`, new at `75a97a18`. The section then re-tells at least two episodes that are in register rows:

- `:521–525`, the r5 FAIL 1 remnant — register row 5 — re-told in full, including the stale ordinal of Note 4.
- `:487–492`, the r4 "wider margin" episode — register row 7 — re-told, though here the document announces the
  exception in the next clause ("One substantive point from those episodes is kept because…"), which is honest.

The second is declared; the first is not. As written the rule is a false absolute about the document's own
contents, introduced by the commit whose purpose was to stop writing false absolutes. NOTE rather than FAIL
because it misleads only about editorial layout. Repair: cut `:521–525` (which Note 4 recommends anyway), or
soften the rule to "Episodes in a register row are not re-told here, with one exception, below."

### Note 7 (NOTE) — the reduction cut a section that r13's FAILs mostly did not live in, and left the sites that did

Per Note 5, two of r13's three FAILs sat outside § "The pattern, named". `75a97a18` reduced that section and left
`:310` and `:398` — the two `r13 FAIL 2` sites — untouched, which is why Note 1 exists. This is not itself a
defect; it is the observation that the structural remedy was aimed at the wrong target, and it is the reason the
round did not close.

### Note 8 (NOTE) — the reduction dropped the r5-note-8 attribution

The removed prose credited the ratio-vs-difference qualification to r5 note 8 and said explicitly why it belonged
in the document. The retained paragraph keeps the substance and the reason but not the provenance. A successor
reconciling `ERRATUM_C2.md` against `REVIEW_C2_PREFREEZE_R5.md` now has to find the connection unaided. Cheap to
repair: add "(r5 note 8)".

### Note 9 (NOTE) — "Its NOTE-level findings were acted on rather than deferred" (r13 T6)

`:417`. `6d987390` changed "are" to "were" and left the substance. r12 raised seven NOTE-level findings (its Notes
3–9); three were acted on. Defensible if read as introducing the list that follows, as r13 said; still a universal
that a reader will take at face value. Repair: "Three of its NOTE-level findings were acted on rather than
deferred:".

### Note 10 (NOTE) — a disclosure attributed to r12 that r12 does not contain (r13 T7)

`:409` credits r12 with having "disclosed that its own first draft of its verdict table was hand-tallied and
wrong". r12's committed file says only that its counts were "extracted mechanically … not hand-tallied". r13 was
the review that made that disclosure. Unactioned for a second round. This misattributes a governance behaviour,
and should be corrected or deleted.

### Note 11 (NOTE) — "the only occasion on which C2 has departed from a reviewer's explicit instruction" (r13 T8)

`:367–368`, unbounded, unactioned for a third round (r11 Note 5, r12 S4, r13 Note 6). It now has a second
candidate in the namespace's own history: r10 wrote "Keep it, restructure it, **do not cut it**"
(`REVIEW_C2_PREFREEZE_R10.md:336`), and `75a97a18` removes 23 lines of that section and adds 13. Whether that
counts as a cut or a restructure is arguable — which is exactly why an unbounded "only" should not be asserted.
Repair by scoping it to the r8/r9 episode: "It is the departure r9 judged, and it held up."

### Note 12 (NOTE) — "four independent reviews (r5, r6, r7, r8)" (r13 T9)

`README.md:100–101` and `ERRATUM_C2.md:29–31`. True and non-exclusive; r11, r12 and r13 have each also run the
whole-history D1 leaf diff, so the enumeration undercounts by three and will drift every round. Unactioned for a
third round. Repair by citing rather than enumerating: "independently confirmed by every review that has run the
whole-history leaf diff; see the review files."

### Note 13 (NOTE) — "one is a scientific or decision value" (r13 T10)

`:28`. The subject is leaves, and nine leaves are the scientific correction — which the ledger says at `:49` and
the README says at `:92–93`. Locally disambiguated two lines later by the apposition. Raised by r12 (S3/Note 3)
and r13 (T10) and unactioned both times. It is the only remaining numeric divergence in the provenance account
and should not go to an adjudicator a fourth time. Repair: "one *change* is a scientific or decision value — nine
leaves".

### Note 14 (INFO) — the empty `theorem/` directory

`theorem/` is present and empty, and therefore not committed. r13 recorded the same at its Note 10. Harmless,
mentioned only so the next round does not re-discover it.

---

## Is the corpus-claim class closed?

**No.** Twelve instances are live: **five** rows are FAILs (C1–C5, which are the four distinct blocking defects
of Notes 1–4 — C4 and C5 are two sites of Note 4), and **seven** are NOTEs (C6–C12). Below is every instance I
found in the namespace — prose, tables, code comments, docstrings and committed JSON strings — that is a
universal, superlative or self-descriptive claim over a mutable corpus and is currently false, unverified, or
capable of going stale. I swept all nine `.md` files outside `review/`, all seven `.py` files in `code/`, and the free-text
leaves of the committed JSON, by script, then triaged. I have left none for a next round.

| | site | the claim | status |
|---|---|---|---|
| **C1** | `ERRATUM_C2.md:310` vs `:398` | "C2 has **twice** written…" / "…**three times**" | **FALSE — FAIL, Note 1.** Two statements of one fact, disagreeing, with `:438` certifying the repair |
| **C2** | `ERRATUM_C2.md:495` | "`grep -c 'self-caught' ERRATUM_C2.md` against the row count" | **FALSE — FAIL, Note 2.** Returns 7, not 4; broken by the commit that wrote it |
| **C3** | `ERRATUM_C2.md:408` | r12 "listed **all seven surviving instances** … rather than leaving any for a later round" | **FALSE — FAIL, Note 3.** r13 listed eleven; at least two predate r12 |
| **C4** | `ERRATUM_C2.md:525` | "**Sixth instance**; r5 FAIL 1" | **FALSE — FAIL, Note 4.** The register makes it the fifth, and did when the phrase was written |
| **C5** | `ERRATUM_C2.md:308–309` | "So **every** hand-maintained tally was deleted from the prose that carried it" | **FALSE — FAIL, Note 4.** C4 is the surviving counterexample (r13's T11, now with a concrete instance) |
| **C6** | `ERRATUM_C2.md:443–445` | this section's narrative "has been the **single largest source** of the defects it describes" | **UNVERIFIED — NOTE 5.** Not derived; the commit message's stronger form is false |
| **C7** | `ERRATUM_C2.md:445` | "Where an episode is in a register row, **it is not re-told**" | **FALSE — NOTE 6.** `:521–525` re-tells register row 5 |
| **C8** | `ERRATUM_C2.md:417` | "Its NOTE-level findings **were acted on** rather than deferred" | **OVERBROAD — NOTE 9.** Three of r12's seven (r13 T6) |
| **C9** | `ERRATUM_C2.md:409` | r12 "**disclosed** that its own first draft … was hand-tallied and wrong" | **FALSE — NOTE 10.** r12's file contains no such disclosure (r13 T7) |
| **C10** | `ERRATUM_C2.md:367–368` | "It is **the only occasion** on which C2 has departed from a reviewer's explicit instruction" | **UNBOUNDED — NOTE 11.** Now with a second candidate in `75a97a18` itself (r13 T8) |
| **C11** | `README.md:100–101`, `ERRATUM_C2.md:29–31` | "**four** independent reviews (r5, r6, r7, r8) each confirmed this" | **STALE — NOTE 12.** Undercounts by three and drifts every round (r13 T9) |
| **C12** | `ERRATUM_C2.md:28` | "Of the leaves replaced … **one** is a scientific or decision value" | **DIVERGENT — NOTE 13.** Nine leaves, per `:49` and `README.md:92–93` (r13 T10) |
| **C13** | `ERRATUM_C2.md:4` | "this document dispositions **every** FAIL from **every one** of them" | **SOUND — verified mechanically.** The round table's per-round counts sum to **34**; the document carries exactly **34** disposition rows, and the two sets match one for one (r1's six bare-numbered rows plus r2–r13's) |
| **C14** | `ERRATUM_C2.md:38` | "**Every** leaf this campaign has replaced in an already-committed evidence file" | **SOUND — verified.** Scope sentence is exact, and is immediately followed by "Do not trust this table — regenerate it" plus the command. This is the class handled correctly; it is the model for C1–C12 |
| **C15** | `ERRATUM_C2.md:24`, `:511–513`, `README.md:100` | "**no** Γ, magnitude, margin, requirement, gap fall, class or adopted-subset value has changed" | **SOUND — re-verified here** against the producers and the D5 artifact |
| **C16** | `ERRATUM_C2.md:482–484` | "**Every** instance has the same shape…" | **SOUND.** Checked against all 25 rows; the second register is explicitly excluded at `:475–476` and `:336–339` |
| **C17** | `ERRATUM_C2.md:443` | "**Every one** of C2's repair rounds has carried an error of its own" | **SOUND.** Rounds 1–12 each have at least one register row; round 13 is this review's Notes 1–4 |
| **C18** | `code/c2_mutations.py:1`, `:97–99` | "**Every** mutant must be DETECTED, or PROVEN EQUIVALENT"; the tiling invariant | **SOUND.** Claims over the suite's own frozen inputs, re-run here: 43 applied, 40 detected, 3 proven equivalent, 0 undetected |
| **C19** | `code/c2_recertify_306.py:14`, `:101–107`; `C2_RECERTIFY_306.json` `host.note` | "makes **NO** claim about the machine that built the registry"; "not recorded **anywhere** in this repository" | **SOUND.** Re-derived by r10 and r11 over `evidence/` and `config/`; the assertion is negative and scoped to this repository, and no build-host field exists |
| **C20** | `phase_d/CELL_306_ADOPTION.md:48` | "does not claim it is the **only** such corroboration, only that it is the one identified" | **SOUND.** The repair of r7 FAIL 2 / r10; correctly narrowed and is the model for C10 |
| **C21** | `code/c2_d5_forecast.py:1`, `:11`, `:61` | "Combines **every** valid certified atom-constant supply"; "shares **no** function with `deflated_consume`" | **SOUND.** Claims over frozen code and a frozen registry, not a mutable corpus; verified byte-stable since `5a94568a` |
| **C22** | `README.md:3` | "**Nothing** outside this namespace is modified" | **SOUND — re-verified here.** 144 additions, all in-namespace, zero modifications |

C13–C22 are the sound side and I am recording them so a fifteenth round need not re-derive them, in the same
spirit as r11's and r13's V-lists. C1–C5 must be repaired before freeze. C6–C12 are NOTEs; the campaign may freeze
over them, but C8–C12 have each now survived two or three rounds after being named, and a repair round that closes
C1–C5 and leaves C8–C12 standing will be one more round in which the class migrates rather than closes.

---

## On the narrative reduction (`75a97a18`)

**Did it lose anything load-bearing? Almost nothing.** I diffed the section before and after and checked every
removed assertion against what remains. All 25 repair-register rows survive, verified by script, with the same
round distribution. The second register, the operational lesson, the r13 FAIL 3 withdrawal with its unflattering
reading, and all six figures the commit claims to have preserved are present. The three facts the removed prose
carried that a reader might need — that four instances were self-caught, that the r4 episode was one of them and
was corrected at `1663f558`, and that inheriting a reviewer's unverified claim is the same failure mode as
inheriting one's own — are each carried elsewhere: by the register's `self-caught` rows, by row 7's commit pin,
and by `:56–58`. The single loss is the attribution of the ratio-vs-difference qualification to r5 note 8
(Note 8), which costs a successor a cross-reference and nothing else. An adjudicator reading the reduced section
has everything they need.

**Was it the right call?** Directionally yes, in execution no.

The direction is right. The narrative duplicated the register, and a retrospective re-told in prose beside a table
that records the same episodes cannot be edited without a count going stale somewhere — which is what has
happened repeatedly. r10 asked for exactly one restructuring commit and then for the section to be left alone, and
a reduction that leaves the record intact and the storytelling out is a reasonable reading of that. The new
paragraph structure is clearer than what it replaced, and the one substantive point deliberately retained — that
r4's "wider margin" remark is false of the ratio and true of the absolute difference — was the right thing to keep
and is arithmetically exact, which I recomputed.

The execution is wrong in three ways, and I would say plainly that **more should have been cut, in one specific
place, and that the cut was aimed at the wrong section.**

1. **Wrong target.** The commit's premise is that this section's prose is where the defects live, and that r13's
   three FAILs were all in it. Two of the three were not: `r13 FAIL 1` lived in the § TWELFTH disposition
   paragraph and `r13 FAIL 2`'s two sites are in § SIXTH and § ELEVENTH. The reduction left both `r13 FAIL 2`
   sites untouched — and one of them is still defective (Note 1). The campaign reduced prose it had just cleaned
   and left standing the prose that was actively broken.

2. **Too little cut, in one place.** By the commit's own new rule — "Where an episode is in a register row, it is
   not re-told" — the closing parenthetical at `:521–525` should have gone with the rest. It re-tells register row
   5 at length and carries the stale "Sixth instance" ordinal that is Note 4. Cutting it would have removed a FAIL
   and made the new rule true. It was left because the commit treated the r5-era parenthetical as a separate
   fixture rather than as narrative, which is the distinction the rule does not draw.

3. **Two new self-descriptive claims where the commit's whole purpose was to stop writing them.** The new opener
   asserts a superlative it does not derive (Note 5) and an editorial absolute that is false of the section it
   introduces (Note 6). Neither is material on its own. Both are the class, in the reduction commit, which is the
   same pattern as r12 FAIL 1 and r13 FAIL 1 at one level lower in severity.

The right version of this commit cuts the same narrative, cuts `:521–525` as well, replaces the opener with a
sentence carrying no superlative and no absolute — the registers below are the record; the prose is short
deliberately — and repairs `:310`. Three of those four were done.

---

## What I did not check

- The Arb/FLINT passes themselves, every certified constant in `evidence/registry_c2/`, and the mathematics the
  producers implement. I verified that the committed producers reproduce their committed artifacts byte-for-byte,
  which establishes reproducibility, not mathematical correctness.
- `0.932851` (max D_lo × 1.1 across the tail). I confirmed it is present and unaltered but did not recompute it; I
  rely on r3's table and r4's independent exact verification.
- N10's build-log premise, and anything on a remote host. I ran nothing on AWS or Vultr, as the review request
  requires.
- The internal correctness of the predecessor namespaces. I checked only that they are byte-untouched since
  `5289b6ce` and that the r4 coverage map's sha256 matches what the README cites.
- The thirteen prior review files end to end. I read r10, r12 and r13 in the parts that bear on my findings,
  extracted every verdict line by script, and confirmed each file's commit count is one.
- r13's V1–V12 I relied on rather than re-deriving in full, as the review request permits, after re-deriving the
  register tallies, the 45/45 accounting and the ledger figures that my findings touch.
- Commit messages as a corpus. I read the two under review and quote one in Note 5, but I did not sweep the
  campaign's 28 commit messages for the corpus-claim class; they are immutable and outside the namespace.

---

## Verdict counts

Extracted from the checklist table above by script, not by hand, after the warning in the review request:

| verdict | rows |
|---|---|
| PASS | 38 |
| FAIL | 8 |
| NOTE | 9 |
| INFO | 1 |
| **total rows** | **56** |

38 + 8 + 9 + 1 = 56, reconciling against the table. My own first draft of this table said 7 FAIL and 10 NOTE and
was wrong on both, which is why the request says to tally mechanically; the figures above are the script's.

The 8 FAIL rows are 26, 27, 30, 42, 48, 49, 50 and 55. Rows 27 and 42 are the same finding as row 26; row 50 is
the same finding as row 48; row 55 is the aggregate "did these commits introduce a new defect", already counted
at row 30.

**Distinct blocking defects: 4** — Notes 1, 2, 3 and 4.

**NOTE-level findings: 9** — Notes 5 through 13, at checklist rows 36, 37, 38, 39, 43, 44, 45, 46 and 47. Note 14
is INFO and has no checklist row; the table's single INFO row, 56, is my reliance on r13's V-list.

---

## Where I landed

For the fourteenth consecutive round the science is exact, the gate is frozen at one commit and byte-untouched,
the integrity envelope is additive and in-namespace, `main` and every predecessor are untouched, and nothing in
the namespace pre-empts freeze, qualification, seal or adjudication. I reproduced all of that here. Thirteen
reviews and I now agree on it, and the review request's framing is correct: it has never been the weak part.

The freeze is blocked on four textual defects. One of them — r13 FAIL 2 left unrepaired, with its disposition row
certifying the repair — is the campaign's signature failure occurring inside the row created to record that
failure, and it is decisive on its own. One is a verification command that its own commit falsified. One is a
false exhaustiveness claim about the audit of the very class under review. One is a prose ordinal written at the round-five
repair that miscounts the register and falsifies the document's own de-counting claim.

None of the four touches a number an adjudicator would decide on. All four touch whether the campaign's
self-reports can be read at face value, which is the only question left open after thirteen rounds of arithmetic
that never moved.

On the calibration I was given: I think it is right and I applied it as written. I have been explicit above about
why each FAIL clears the bar and why each of Notes 5–13 does not, including two false-as-written claims (C7, C9)
that I deliberately did not escalate because they mislead about layout and attribution rather than about the
science, the decision, the governance state, provenance or reliability. I did not withhold a ready verdict to
avoid appearing lenient; had Note 1 alone been absent I would still have blocked on Notes 2 and 3, and had all
four been absent I would have returned `READY_TO_FREEZE_WITH_NOTES` over C6–C12 without hesitation.

The repairs are four sentences. The fifteenth round should make those four changes, close C8–C12 in the same pass
rather than one corpus per round, and change nothing else.

**VERDICT: NOT_READY**
