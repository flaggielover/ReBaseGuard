# Twelfth independent pre-freeze review — Campaign C2, D-stage successor

**VERDICT: NOT_READY**

*Twelfth independent fresh-context pre-freeze review, 2026-09-21, worktree `/Users/suzhe/ReBaseGuard-k5c2`,
branch `p5y-k5-tail-c2`, HEAD `6aa2040a`. Read-only: this file is the only file I wrote, and I ran no writing git
command. AWS was not touched.*

---

## Reviewer context — what I re-derived, and what I took on trust

I wrote none of this work and read it cold. As instructed I started from `git diff 87004e2b..6aa2040a` — three
files, 363 insertions, 14 deletions — and then widened to the whole namespace for the corpus sweep. Everything I
call verified below I verified myself on this machine (macOS/arm64, stdlib CPython 3, `PYTHONINTMAXSTRDIGITS=0`).
I did not use the FLINT venv.

**Re-derived independently.** All four stdlib producers re-run and compared against their committed artifacts:
`code/c2_mutations.py` → `evidence/prefreeze/C2_MUTATIONS.json` **byte-identical** (`cmp` clean), self-reporting
`applied 43, real_mutants 35, static_assertions 8, detected 40, equivalent 3 (M19, M20, M32), undetected [],
pass true`, sha256 `512180f32a5ca85355270f57bc98c5281d8bb8de7f9e32a1d10652e1e0a4ebac` — which is also the sha256
of the committed artifact; `code/c2_d1_blocker.py` → `evidence/phase_d1/C2_D1_BLOCKER.json` **byte-identical**;
`code/c2_critical_ratio.py` → `evidence/phase_d5/C2_CRITICAL_RATIOS.json` **byte-identical**; and I additionally
re-ran `code/c2_b0_verify.py`, which returns **7/7 `ALL_PASS`** and differs from the committed artifact in exactly
one leaf, `.B1_git.head` (`5289b6ce` → `6aa2040a`), as expected and as r6 recorded. From `C2_D5_FORECAST.json` I
read back `D_STAGE_CLASS = D_PARTIAL`, `closed = [305, 306]`, `still_open = [307, 308, 309]`, gap falls
`0.46285183476411584 / 0.24593099374719365 / 0.18389841084966285`, `Gamma(305) = −0.08802906884054082`,
`Gamma(306) = −0.030469257709306738`, `gate_sha256 = 098dd7f5…`, `gate_frozen_before_forecast: true`. From
`C2_RECERTIFY_306.json` I recounted the consumed-constant checks myself against the producer's own
`CONSUMED_UPPER + CONSUMED_LOWER = (C_T, tau, D1, D2, D_lo)`: **45/45 `ok` at 256 bits and 45/45 at 384 bits**
(9 block artifacts × 2 + 9 cell artifacts × 3), `all_ok: true` on both passes, 18/18 `certified: true`, verdict
`BOTH_PASSES_OK`, `registry_sha_pin_ok: true`.

**The ledger, rebuilt from scratch.** I did not take the campaign's file list. I enumerated every path under
`evidence/` and `config/` from `git ls-tree -r HEAD` **and** every path that has ever appeared under those
directories on any ref, wrote my own JSON leaf-flattener, and diffed consecutive revisions of each file with
`git log --reverse --all -- <file>`. Result and full detail in § "Rebuilt replacement ledger" below. **The
campaign's ledger is correct: 19 replaced leaves, three files, 9 + 4 + 6.** r11's FAIL 1 is fully repaired.

**Taken on trust.** The Arb/FLINT passes themselves and every certified constant; the mathematics the producers
implement; N10's build-log premise; anything on a remote host. I also relied on r11's V1–V10, as the review
request permits, after spot-re-deriving V2, V3, V4 and V9 (see row 30).

**Where I landed.** The science, the gate and the integrity envelope are clean, for the twelfth consecutive
round, and I reproduced all of it rather than inheriting it. The repair of r11 FAIL 1 is complete and I verified
it the hard way. But the repair of r11 FAIL 2 is **half done and is recorded as done**, and the new README
provenance paragraph does not reconcile with the ledger it summarises. Both are FAILs. Both are textual, both are
cheap, and neither touches evidence.

---

## Checklist

| | check | verdict | evidence |
|---|---|---|---|
| 1 | **r11 FAIL 1 — ledger rebuilt over every committed `evidence/` + `config/` file** | **PASS — independently rebuilt** | my own sweep over all 115 committed files under those two trees (115 at HEAD; 115 ever, no deletions) finds exactly three multi-revision files and exactly **19** replaced leaves. See § "Rebuilt replacement ledger" |
| 2 | ledger row 1 — `C2_D1_BLOCKER.json`, `e71378a0 → 55c4cf00`, 9 leaves | **PASS — verified** | 9 replaced, all `C_T.{magnitude, delta_vs_base, relative_gain}` on cells 307/308/309. The commit pair, newly pinned this round, is right |
| 3 | ledger row 2 — `C2_MUTATIONS.json`, `5a94568a → 12585997`, 4 leaves | **PASS — verified** | `applied` 33→43, `detected` 31→40, `real_mutants` 25→35, `.mutants.M10_wrong_tail_cell.caught_by[0]` `value`→`tiling`. Exactly as tabulated |
| 4 | ledger rows 3–4 — `C2_RECERTIFY_306.json`, 3 + 3 leaves | **PASS — verified** | `8aee1fc5 → 55c4cf00`: `diagnostic_policy.why`, `cpu_seconds` 1653.6→1153.9 and 1691.8→1204.2. `55c4cf00 → 5609358f`: `host.note`, 1153.9→1141.5 and 1204.2→1196.1. 0 added, 0 removed in both |
| 5 | the 9 + 4 + 6 = 19 breakdown | **PASS — verified** | nine scientific, four suite counts, six free text and wall-clock. Sums to 19 and matches my rebuild leaf for leaf |
| 6 | is anything **still** missing from the ledger? | **PASS** | no replaced leaf anywhere under `evidence/` or `config/` is absent from it. The scope sentence at `:34` is now true under its own regeneration command |
| 7 | "The first version of this ledger listed 15 and claimed to list every one" | **PASS — verified** | at `87004e2b` the table is 9 + 3 + 3 = 15 under the same unqualified scope sentence. Correct |
| 8 | **r11 FAIL 2 — both compliance clauses deleted, as the disposition row states** | **FAIL** | **one of the two survives verbatim.** `ERRATUM_C2.md:403` still reads "The two registers below are where this campaign tallies its own defects; **prose does not**" — r11's site `:379`. **Note 1 — FAIL 1** |
| 9 | is that surviving clause true? | **FAIL (same finding)** | no. `ERRATUM_C2.md:306`, added by this commit, is a prose tally of C2's own defects ("C2 has **twice** written a sentence here…"), as is `:43`. **Note 1** |
| 10 | the first compliance clause (`:298–300` at `87004e2b`) | **PASS — verified** | genuinely gone; the replacement at `:303–308` is normative ("Counts belong in the tables") and makes no claim about the current state of the prose |
| 11 | **r11 S3 — "exactly nine leaves … in this campaign" rescoped** | **PASS — verified** | `:270` now "nine leaves **of that artifact**", `:473` now "nine leaves **of it**". Both occurrences scoped, as the disposition says. `:296` and `:324` were already artifact-scoped in context |
| 12 | **did the repair introduce a new defect?** | **FAIL** | yes, two. Note 1 (above) and the README provenance paragraph, Note 2 |
| 13 | the new `README.md:89–94` paragraph reconciles with the ledger | **FAIL** | "Nineteen leaves … **exactly one of them** is a scientific value: the C_T sensitivity row for cells 307/308/309 … Four are … six are …". 1 + 4 + 6 = 11 of 19, and the "one" is **nine** leaves. Contradicts `ERRATUM_C2.md:46`. **Note 2 — FAIL 2** |
| 14 | the new `ERRATUM_C2.md:25` opening sentence | **NOTE** | same "of the leaves … one is a scientific or decision value" construction, but disambiguated two lines later by "each found the same nine leaves" and by the ledger. **Note 3** |
| 15 | the new `ERRATUM_C2.md:49` sentence | **NOTE** | "No certified constant, Γ, **magnitude**, requirement or gap fall appears anywhere in this table" — `magnitude` appears in the table at `:41`. Intended referent is the cell-level quantity; same collision r5 called a suggestion, not a defect. **Note 4** |
| 16 | the new r11 disposition rows are factually accurate about r11 | **PARTIAL** | FAIL 1's row is exact. FAIL 2's row states a repair that is half done (row 8). The header's PASS/NOTE split does not reconcile with r11's checklist — **Note 5** |
| 17 | r11 disposition header FAIL count | **PASS — verified** | "**2 FAIL**" matches r11's checklist (rows 9 and 31) and its verdict table. The FAIL count is the decision-relevant one and it is right |
| 18 | `ERRATUM_C2.md:4` — "dispositions every FAIL from every one of them" | **PASS — recounted** | 23 `rN FAIL k` rows + 6 r1-style `FAIL k` rows = **29**; round table sums 6+3+1+3+2+1+2+3+3+3+2 = **29**. Reconciles after the r11 row was added |
| 19 | round table and README review table gain a correct r11 row | **PASS — verified** | `r11 | 87004e2b | 2 FAIL` — `87004e2b` is the HEAD r11 reviewed, matching the table's convention for every earlier round; README row "NOT_READY — **2 FAIL**" |
| 20 | three producers reproduce byte-for-byte | **PASS — re-run here** | three for three `cmp` clean, plus B0 7/7. See reviewer context |
| 21 | `c2_mutations.py` 43/43, 0 undetected, sha `512180f3…` | **PASS — re-run here** | 43 applied = 35 real + 8 static, 40 detected, 3 proven-equivalent, `undetected: []`, `pass: true`; artifact sha256 `512180f32a5c…4ebac` |
| 22 | class `D_PARTIAL`, closed {305, 306}, open {307, 308, 309} | **PASS — verified** | read back from `C2_D5_FORECAST.json` |
| 23 | gap falls 0.46285183 / 0.24593099 / 0.18389841 | **PASS — verified** | exact to full precision on cells 307/308/309 |
| 24 | Γ(305) = −0.088029069, Γ(306) = −0.030469258 | **PASS — verified** | −0.08802906884054082 and −0.030469257709306738 |
| 25 | `C2_RECERTIFY_306.json` = `BOTH_PASSES_OK`, 45/45 at both precisions | **PASS — recounted from the artifact** | 45/45 at 256 and 45/45 at 384 over the five consumed constants, 18/18 `certified`, `all_ok` both passes |
| 26 | gate sha `098dd7f5c3cf…b28f` at exactly one commit | **PASS — verified** | `shasum -a 256` matches; `git log --all` on the path returns only `87309610` |
| 27 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS — verified** | per-path history: the forecast JSON's last (and only recent) commit is `5a94568a`; the producer's is `5a94568a`. Neither is in this diff |
| 28 | all-additive and in-namespace since `5289b6ce` | **PASS — verified** | `git diff --name-status 5289b6ce..6aa2040a` → **142 A, 0 M, 0 D**; no path outside `level4/closure_proofs/p5y_k5_tail_c2_closure/` |
| 29 | `main` untouched | **PASS — verified** | `main` is `c123b9bb`, an ancestor of HEAD; no C2 commit on it |
| 30 | coverage map r4 `a3bddd83…` intact; no r5 map | **PASS — verified** | `K5_COVERAGE_MAP_R4.json` hashes to `a3bddd83234f…10a35` at its single commit `f2ac1eb3`; repo-wide `find -iname '*COVERAGE_MAP_R5*'` → nothing. `c2_b0_verify.py` and `c2_mutations.py` both pin the sha as a gate condition |
| 31 | nothing pre-empts freeze, qualification, seal, adoption or adjudication | **PASS — verified** | no lifecycle artifact anywhere in the namespace; the diff adds none; `R_STAGE_DESIGN.md:4–5` guard **DENY**, no authorization artifact; `CELL_306_ADOPTION.md:9–11` states adoption is a terminal governance state nothing in C2 may confer |
| 32 | all eleven prior review files committed and unedited | **PASS — verified** | each of `review/REVIEW_C2_PREFREEZE{,_R2…_R11}.md` has **exactly one** commit in `git log --all`; r11 is committed at `6aa2040a` verbatim |
| 33 | code comments and docstrings swept for the class | **PASS — verified independently** | exactly two corpus universals in `code/`: `c2_critical_ratio.py:14` (= V9) and `c2_recertify_306.py:107` (= V4). Both sound. Confirms r11 row 32 |
| 34 | committed JSON string leaves swept for the class | **PASS — verified independently** | I flattened all 115 committed JSON files and regex-swept every string leaf. 167 flagged; every one is a mathematical or gate-rule quantifier over a fixed object ("for every e in [e_lo, e_hi] …", "EVERY cell it does not close"), except `host.note` (= V4) and `diagnostic_policy.why` (r10-dispositioned). Confirms r11 row 33 |
| 35 | r11's V1–V10 spot-re-derived | **PASS** | V2 (`evidence/registry_c2/` single commit `5a94568a`), V3, V4 and V9 re-checked here; V1, V5–V8, V10 relied on per the review request |
| 36 | the ledger's scope is *replaced* leaves only; additions and removals | **NOTE** | 114 added and 20 removed leaves are outside the ledger's stated scope. All are disclosed elsewhere (`:199` r2 FAIL 66, `:255` r4 FAIL 1) and were verified by r5 and r6. Not a gap, but the ledger does not say so. **Note 6** |
| 37 | `ERRATUM_C2.md:364` — "the one place in **nine rounds**" | **NOTE** | the document now dispositions **eleven**; r11's Note 5 is unactioned and the second register still carries only r2 note 4. **Note 7** |
| 38 | `README.md:96–98` / `ERRATUM_C2.md:29` — "four independent reviews (r5, r6, r7, r8)" | **NOTE** | true and not exclusive, but r11 and this review also performed the whole-history D1 leaf diff. Capable of going stale. **Note 8** |
| 39 | working tree clean; no stray artifact | **PASS** | `git status --porcelain` empty. The empty untracked `theorem/` directory persists; untracked, so outside the freeze. **Note 9** |

---

## Notes

### Note 1 (FAIL 1) — r11 FAIL 2 is half repaired, and the disposition row records it as fully repaired

r11's S2 named **two** sites. At `87004e2b` they were:

> `:298–300` — "So every hand-maintained tally has been deleted from prose in both `README.md` and this section.
> The tables carry the counts … **and prose does not**."
>
> `:379` — "The two registers below are where this campaign tallies its own defects; **prose does not**."

The first is genuinely gone. The second **survives verbatim** at `ERRATUM_C2.md:403`; the commit removed only the
trailing "— so counts are kept to tables" from the sentence after it. The sentence `git diff` shows unchanged is
the clause itself.

The disposition row at `ERRATUM_C2.md:395` says:

> **Both compliance clauses are deleted.** … **No such claim is made any more**: where prose states a number it
> should simply be right, and be checked before it is written.

And the paragraph at `:306`, also added by this commit, says:

> *(C2 has twice written a sentence here claiming its prose contains no counts, and both times the claim was
> false while the sentence itself sat beside counts. **No such claim is made now**…)*

Both statements are false, and the surviving clause is itself false. The two registers are not where this campaign
tallies its own defects *exclusively*: `:306` is a prose tally of C2's own defects — the count is the word
"**twice**" — and `:43` is another ("The first version of this ledger listed **15** and claimed to list every
one; it omitted `C2_MUTATIONS.json` entirely"). Both were written by this commit, in the same document, 97 and 360
lines from the clause that denies they exist.

**Why this is a FAIL and not a NOTE.** It is not the surviving clause on its own — that is a small stale
universal of the kind this campaign has been grinding down for six rounds. It is that the **disposition table**,
which is the instrument an adjudicator reads to confirm that each FAIL from each round was actually repaired,
asserts a repair that was not performed, in the round whose entire purpose was to stop asserting compliance
without checking it. An adjudicator reading `ERRATUM_C2.md:395` would conclude r11 FAIL 2 is closed. It is not.
That misleads about the campaign's repair record and hence its reliability, which is squarely inside the bar.

The shape is exactly the one `ERRATUM_C2.md:453` predicts of itself: a correct primary fix (r11 FAIL 1, which I
verified the hard way and which is excellent work) with an unverified sentence stacked on top.

**To repair:** delete "; prose does not" from `:403`, and rewrite the FAIL 2 row to say what was actually done —
one clause deleted, one clause deleted now — or keep the clause and drop the completeness claim. Text only.

### Note 2 (FAIL 2) — the new README provenance paragraph does not reconcile, and understates the scientific footprint ninefold

`README.md:89–91`, added by this commit:

> Nineteen leaves of committed evidence have been replaced, across three files, and **exactly one of them** is a
> **scientific value**: the C_T sensitivity row for cells 307/308/309 of the D1 diagnosis, corrected to the
> admissible perturbation. **Four are** the adversarial suite's own counts … **six are** free text and wall-clock
> timings in `C2_RECERTIFY_306.json`.

"them" is "nineteen leaves". The three following counts are leaf counts — and four and six are exactly the leaf
counts of rows 2 and 3–4 of the ledger. So the paragraph decomposes nineteen leaves as **1 + 4 + 6 = 11**, leaving
eight unaccounted, and identifies "one of them" with an object that is **nine** leaves.

`ERRATUM_C2.md:46` gets it right, in the same commit:

> Of the 19, **nine** are the scientific correction, **four** are the adversarial suite's own counts … and
> **six** are free text and wall-clock timings.

So the two documents disagree, and the one that is wrong is the front door. A reader who takes the README at its
word concludes that one leaf of C2's committed evidence is scientific; the answer is nine. The previous wording
("One published **scientific value** has changed as a result") was unambiguous because it counted *values*, not
leaves; gluing it to a leaf total is what broke it.

**Why this is a FAIL and not a NOTE.** It is a provenance count in the document an adjudicator reads first, it
does not sum, it contradicts the ledger it explicitly forwards to, and it is the same class the round was
convened to close — a count over a corpus committed without checking that it reconciles. I considered filing it as
a NOTE on the grounds that the intended meaning is recoverable and the pointer to the correct ledger is in the
next sentence. I concluded that a nine-fold understatement of how much *scientific* evidence was rewritten, in a
paragraph whose whole job is to state that honestly, is more than a wording preference.

**To repair:** "…and **nine of them** are the one **scientific value**: the C_T sensitivity row…". One word.

### Note 3 (NOTE) — `ERRATUM_C2.md:25` carries the same construction

> **Of the leaves replaced in committed evidence — all of them in the ledger below — one is a scientific or
> decision value**

Read strictly, "one [leaf] is a scientific or decision value" is false for the same reason as Note 2. Here the
next clause — "each found the same nine leaves" — and the ledger twenty lines below both correct it in place, so
no reader is left with the wrong number. Recorded because it is the same sentence pattern and because if Note 2 is
repaired this one should be made to match.

### Note 4 (NOTE) — "no … magnitude … appears anywhere in this table", eight lines under a table containing `magnitude`

`ERRATUM_C2.md:49` asserts of the ledger: "No certified constant, Γ, **magnitude**, requirement or gap fall
appears anywhere in this table." Row 1 at `:41` reads "C_T `magnitude` / `delta_vs_base` / `relative_gain` on
cells 307, 308, 309". The intended referent is the cell-level `/cells/*/magnitude`, which has never moved — I
verified that across all four commits of the artifact — and the collision is the one r5 raised at `README.md:97`
and explicitly classed as "Suggestion, not a defect". I class it the same way, with the observation that the new
sentence says "anywhere in this table" about a four-row table, which makes the collision easier to hit than r5's.
Dropping the word `magnitude`, or writing "cell-level magnitude", removes it.

### Note 5 (NOTE) — the r11 disposition header copies a self-report that does not reconcile

`ERRATUM_C2.md:390` states r11 as "36 rows, **30 PASS, 1 PARTIAL, 3 NOTE**, **2 FAIL**". I extracted r11's verdict
column mechanically: **36 rows, 31 PASS, 1 PARTIAL, 2 NOTE, 2 FAIL**. C2's figures faithfully reproduce r11's own
verdict-counts table, which does not reconcile with r11's own checklist — r11 counted its sixth note (an INFO
attached to a PASS row) as a checklist NOTE.

C2 followed the convention r11 itself endorsed at its row 28, so this is not carelessness. But `README.md:51–54`
says of exactly this hazard that PASS/NOTE/INFO breakdowns are "**deliberately not transcribed** here: a previous
version did transcribe them, and one was wrong — not through miscounting but by faithfully copying a self-report
that did not reconcile with its own stated total. See `ERRATUM_C2.md`, r5 FAIL 2." The erratum's disposition
headers do transcribe them, and this one has reproduced precisely that failure. The FAIL count — the only figure
any decision rests on — is right, so I file this as a NOTE. Either count the rows before transcribing, or drop the
breakdown from the disposition headers as the README already does from its table.

### Note 6 (NOTE) — the ledger is scoped to replacements, and does not say so

My rebuild finds, besides the 19 replacements: **114 leaves added** and **20 removed**, all in
`C2_D1_BLOCKER.json` and `C2_MUTATIONS.json`. The 20 removals are the `gain_per_unit_of_input_moved` field struck
from the four non-C_T operator rows at `92c5d199` — r4's FAIL 1 remedy. None of this is hidden: `:199` (r2 FAIL
66) and `:255` (r4 FAIL 1) disclose it in detail, and r5 row 1 and r6 row 157–158 each verified the counts.

The ledger's scope sentence — "Every leaf this campaign has **replaced**" — is exact, and I confirmed it holds.
But an adjudicator arriving at a section headed "Replacement ledger" and told it is the complete provenance
accounting may reasonably read it as covering every change to committed evidence, which it does not. One clause
("additions and removals are separately accounted at r2 FAIL 66 and r4 FAIL 1; this table is value replacements")
would close the reading. Not a defect: the sentence is true as written.

### Note 7 (NOTE) — "in nine rounds" now covers eleven; r11's Note 5 is unactioned

`ERRATUM_C2.md:364` still reads "That is the one place **in nine rounds** where C2 departed from a reviewer's
explicit instruction, and the departure held up." The document now dispositions eleven rounds, and C2 has since
declined r10's explicit structural recommendation without registering it in the second register, which still
carries only r2 note 4. r11 raised this as its Note 5 and asked for one of two cheap fixes; neither was made and
the r11 disposition section does not mention it. Carried forward unchanged, still a NOTE. A round-anchored count
of this kind will go stale every round it survives; "the one place so far" removes the maintenance.

### Note 8 (NOTE) — "four independent reviews (r5, r6, r7, r8)"

`README.md:96–98` and `ERRATUM_C2.md:29`. r11 verified this sound (V1) and I did not disturb it: the four named
reviews each did perform the whole-history leaf diff and r9 did not. The sentence is not exclusive, so it is not
false. But r11 (its row 8) and this review both performed the same diff, so the enumeration is already an
undercount of who has confirmed it, and will drift further each round. Citing the check rather than the cast —
"every review that has run the whole-history leaf diff has found the same nine leaves" — is stable.

### Note 9 (INFO) — empty untracked `theorem/`, and one thing C2 got right that is worth recording

`level4/closure_proofs/p5y_k5_tail_c2_closure/theorem/` still exists on disk, is empty and untracked, so it is
outside the freeze. Unchanged from r11's Note 6.

Separately, and against the run of this campaign's history: the r11 disposition header says r11 "verified **ten**
corpus claims sound". r11's own section heading says "**(9)**" above a table of ten rows, V1–V10. C2 counted the
rows instead of copying the header, and got it right. That is the failure mode inverted, in the same paragraph
where Note 5 records it recurring, and it deserves to be on the record alongside the FAILs.

---

## Rebuilt replacement ledger

Rebuilt independently, taking no file list from the campaign. Method: enumerate every path under
`evidence/` and `config/` from `git ls-tree -r --name-only HEAD`, union with every path ever touched under those
trees on any ref (`git log --all --name-only --diff-filter=ACDMRT`); for each, walk `git log --reverse --all --
<file>`, parse each revision's blob as JSON, flatten to leaves keyed by full path (dict keys and list indices),
and diff consecutive revisions. A **replaced** leaf is one whose key exists in both revisions with a different
value.

**Corpus.** 115 committed files under `evidence/` + `config/` at HEAD; 115 ever seen in history; **no file has
ever been deleted or renamed**. 112 are single-revision. Three have more than one:

| file | revisions | replaced | added | removed |
|---|---|---|---|---|
| `evidence/phase_d1/C2_D1_BLOCKER.json` | 4 | **9** | 58 | 20 |
| `evidence/prefreeze/C2_MUTATIONS.json` | 2 | **4** | 56 | 0 |
| `evidence/prefreeze/C2_RECERTIFY_306.json` | 3 | **6** | 0 | 0 |
| **total** | | **19** | 114 | 20 |

**19 replaced leaves, three files, 9 + 4 + 6. The campaign's ledger is correct in every cell**, including the
`e71378a0 → 55c4cf00` commit pair it pinned this round in place of "across its history".

Leaf by leaf:

    C2_D1_BLOCKER.json    e71378a0 → 55c4cf00   9 replaced, 3 added, 0 removed
      ~ .cells.307.sensitivity_10pct_improvement.C_T.magnitude        3.722493965153606   → 3.7230322916462693
      ~ .cells.307…C_T.delta_vs_base                                 -0.05217871789165455 → -0.051640391398991466
      ~ .cells.307…C_T.relative_gain                                  0.01382337550114644 → 0.013680760091052447
      ~ .cells.308…C_T.magnitude                                      3.7323525101063026  → 3.7416016751989813
      ~ .cells.308…C_T.delta_vs_base                                 -0.05278446801397618 → -0.04353530292129725
      ~ .cells.308…C_T.relative_gain                                  0.013945193613624323 → 0.011501645296577124
      ~ .cells.309…C_T.magnitude                                      3.6717094388476177  → 3.6886584652029244
      ~ .cells.309…C_T.delta_vs_base                                 -0.05170716861183401 → -0.034758142256526896
      ~ .cells.309…C_T.relative_gain                                  0.013887022072213043 → 0.009335012952053988
    C2_D1_BLOCKER.json    55c4cf00 → d6a4def5   0 replaced, 50 added, 0 removed
    C2_D1_BLOCKER.json    d6a4def5 → 92c5d199   0 replaced, 5 added, 20 removed

    C2_MUTATIONS.json     5a94568a → 12585997   4 replaced, 56 added, 0 removed
      ~ .applied                                          33 → 43
      ~ .detected                                         31 → 40
      ~ .real_mutants                                     25 → 35
      ~ .mutants.M10_wrong_tail_cell.caught_by[0]    'value' → 'tiling'

    C2_RECERTIFY_306.json 8aee1fc5 → 55c4cf00   3 replaced, 0 added, 0 removed
      ~ .diagnostic_policy.why                       (free text)
      ~ .passes.determinism_256.cpu_seconds          1653.6 → 1153.9
      ~ .passes.safe_side_384.cpu_seconds            1691.8 → 1204.2
    C2_RECERTIFY_306.json 55c4cf00 → 5609358f   3 replaced, 0 added, 0 removed
      ~ .host.note                                   (free text)
      ~ .passes.determinism_256.cpu_seconds          1153.9 → 1141.5
      ~ .passes.safe_side_384.cpu_seconds            1204.2 → 1196.1

**Is anything still missing? No.** Every replaced leaf under `evidence/` and `config/` appears in the campaign's
ledger, and no leaf in the ledger is absent from my rebuild. Additions and removals are outside the ledger's
stated scope and are separately disclosed — see Note 6.

**Cross-check of the stability claim.** Net of the whole campaign, measured from `ef58310c` (the state before the
first evidence rewrite) to HEAD, `C2_D1_BLOCKER.json` goes 487 → 525 leaves: **9 replaced, 38 added, 0 removed**,
the additions being 25 `effective_improvement` + 5 `gain_per_unit_of_input_moved` + 5 `per_unit_comparability` +
3 `admissibility_clamp`. That is exactly what `ERRATUM_C2.md:199` claims, and it reconciles with the staged
sequence 487 → 490 → 540 → 525 that r8 recorded. No `Gamma`, cell-level `magnitude`, `gap_above_1`,
`required_uniform_atom_constant_reduction` or `DOMINANT_BLOCKER_*` leaf has ever been replaced, added or removed.

---

## The corpus-claim defect class — is it closed?

**No, but it is one clause and one word from closed, and the substance of it — the provenance accounting itself —
is now correct and independently confirmed.**

This is the seventh consecutive round in which the class survives. What survives is materially smaller than what
r11 found: the ledger, which was the instrument at the centre of r11 FAIL 1, is now **complete and correct**, and
I established that by rebuilding it rather than reading it. The class no longer touches the science, the gate, the
integrity envelope, the review attribution or evidence provenance *as recorded in the erratum*. What remains is
two sentences and four stale or drift-prone universals.

Below is **every** universal, superlative or self-descriptive claim over a mutable corpus I found in the
namespace — Markdown prose and tables, `.py` comments and docstrings, and every string leaf of all 115 committed
JSON files. I do not leave one for a next round.

**Surviving instances — currently false (3):**

| # | site | claim | why it fails |
|---|---|---|---|
| **S1** | `ERRATUM_C2.md:403` | "The two registers below are where this campaign tallies its own defects; **prose does not**" | `:306` ("C2 has **twice** written…") and `:43` ("listed **15** and claimed to list every one") are prose tallies of C2's own defects, both added by this commit. Survives verbatim from `87004e2b`. **FAIL 1 / Note 1** |
| **S2** | `ERRATUM_C2.md:395`, `:306` | "**Both** compliance clauses are deleted … **No such claim is made any more / now**" | one of the two survives (S1). A compliance claim about compliance claims, again unchecked. **FAIL 1 / Note 1** |
| **S3** | `ERRATUM_C2.md:49` | "No certified constant, Γ, **magnitude**, requirement or gap fall appears **anywhere in this table**" | `magnitude` appears in the table at `:41`. Intended referent is the cell-level quantity and the table is four rows long, so the misreading is immediately self-correcting. **Note 4** |

**Surviving instances — true now, but stale, drifting, or not reconciling (3):**

| # | site | claim | status |
|---|---|---|---|
| **S4** | `ERRATUM_C2.md:364` | "the one place **in nine rounds** where C2 departed from a reviewer's explicit instruction" | the document dispositions **eleven** rounds; r10's recommendation was declined and never registered. r11's Note 5, unactioned. **Note 7** |
| **S5** | `README.md:96`, `ERRATUM_C2.md:29` | "**four** independent reviews (r5, r6, r7, r8) each confirmed this" | true and non-exclusive, but r11 and r12 also ran the diff; the enumeration drifts every round. **Note 8** |
| **S6** | `ERRATUM_C2.md:390` | r11 was "36 rows, **30 PASS, 1 PARTIAL, 3 NOTE**" | r11's checklist tallies 31 PASS / 2 NOTE. C2 faithfully copied a self-report that does not reconcile — the hazard `README.md:51–54` names. FAIL count is right. **Note 5** |

**Counting statements that do not reconcile (1) — same class, different surface:**

| # | site | claim | status |
|---|---|---|---|
| **S7** | `README.md:89–91` | "Nineteen leaves … **exactly one of them** is a scientific value … **Four** are … **six** are" | 1 + 4 + 6 = 11 of 19; the "one" is nine leaves; contradicts `ERRATUM_C2.md:46`. **FAIL 2 / Note 2.** `ERRATUM_C2.md:25` has the same construction, locally disambiguated (**Note 3**) |

**Corpus claims I checked and found sound (12).** V1–V10 are r11's, relied on per the review request; I
re-derived V2, V3, V4 and V9 here and add two of my own. Recorded so a thirteenth round need not re-derive them.

| # | site | claim | how it was checked |
|---|---|---|---|
| V1 | `ERRATUM_C2.md:27`, `README.md:97` | r5/r6/r7/r8 each diffed every leaf of `C2_D1_BLOCKER.json`; r9 did not | r11, from all ten review files (see S5 for the drift caveat) |
| V2 | `ERRATUM_C2.md:48` | "`evidence/registry_c2/` has one commit in its history" | **re-derived here**: `git log --all` on the directory and on each of its 76 files → `5a94568a` only |
| V3 | `ERRATUM_C2.md:383` | "no build-host record exists anywhere in C2's `evidence/` or `config/`" | **re-derived here**: I flattened all 115 committed JSON files; the only host records are `C2_RECERTIFY_306.json.host` and `C2_REGISTRY_VERIFY.json.host`, both of the re-certifying/verifying host; `config/` has none |
| V4 | `C2_RECERTIFY_306.json.host.note`, `c2_recertify_306.py:107`, `CELL_306_ADOPTION.md`, N10 | "the registry's build host is not recorded anywhere in this repository" | **re-derived here**: no file outside this namespace references the C2 registry at all |
| V5 | `ERRATUM_C2.md:350` | the artifact's bytes contain no fragment of the docstring | r11, by tokenised n-gram search |
| V6 | `ERRATUM_C2.md:4` | "dispositions every FAIL from every one of them" | **re-derived here after the r11 row**: 29 disposition rows against 29 FAILs in the round table |
| V7 | `README.md:3` | "Nothing outside this namespace is modified" | **re-derived here**: 142 A, 0 M, 0 D since `5289b6ce`, all in-namespace |
| V8 | `OPEN_NOTES…:81`, `CELL_306_ADOPTION.md:98` | "no campaign has built [a second, independently written certifier]" | r2, r7, r11 |
| V9 | `R_STAGE_DESIGN.md:60`, `c2_critical_ratio.py:14` | "the C1 column, which nothing else in the programme has ever computed" | **re-derived here**: `grep -rl` on the critical-ratio keys returns only this namespace and Campaign B's Lemma-G file |
| V10 | `CELL_306_ADOPTION.md:47–48` | the in-repo corroboration is "the one identified", not "the only" | r11; the narrowing is in place |
| **V11** | `ERRATUM_C2.md:34` — the ledger's scope sentence | "Every leaf this campaign has replaced in an already-committed evidence file" | **re-derived here, from scratch, over all 115 files**: true. This is r11's S1, and it is closed |
| **V12** | `ERRATUM_C2.md:44–47` | "**19 leaves, three files** … nine … four … six" | **re-derived here**: exact, leaf for leaf |

**On why the class keeps surviving, and what would end it.** Round 11 did the substantive thing right: it rebuilt
the ledger over the corpus its own sentence named, and my independent rebuild confirms it cell for cell. What it
did again is write two *new* sentences describing its own compliance — one saying both clauses were deleted when
one was not, one summarising the new ledger with an arithmetic that does not close — and commit them without
running the check on either. Deleting a compliance clause is not a substitute for not writing one; this round
deleted two and wrote two more, in the same commit. The pattern is not in the campaign's diligence, which is by
now considerable, but specifically in the last sentence written before commit, which is always the one describing
what the commit achieved. The only structural cure I can see is the one the campaign has already half-adopted:
never state, in prose, a fact about the campaign's own text or its own evidence tree that is not the printed
output of a command included beside it. `ERRATUM_C2.md:34` now does that and is correct because of it.
`README.md:89` and `ERRATUM_C2.md:395` do not, and are wrong.

---

## What I did not check

- **The Arb/FLINT passes and every certified constant.** I did not use the FLINT venv and recomputed no certified
  value. The determinism and safe-side results are trusted on the artifact, on my leaf-stability diff across all
  three of its commits, and on eleven prior reviews. I recounted 45/45 from the artifact; I did not re-derive it.
- **The underlying K5-B / TC-T mathematics.** I verified that the committed producers reproduce their artifacts
  byte-for-byte, not that what they compute is mathematically correct.
- **Anything on a remote host.** AWS was not touched; `rebaseguard-vultr` was not contacted. N10's build-log
  premise is unverified by me, as it was by r8–r11.
- **`code/c2_refined_registry.py`** beyond confirming it is unchanged in this diff and reading its comments for
  the corpus sweep. I did not run `build` or `verify`, and did not re-derive the 105/105 registry verification.
- **`evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json`** beyond confirming it is single-commit and clean in
  my ledger rebuild.
- **`D_PRIME_OPPORTUNITY.md`'s counter-combination arithmetic (N7).** Read, not recomputed. It is the finding the
  README says outranks the rest, and it has not been independently recomputed by any round I read.
- **Reviews r1–r10 end to end.** I read r11 in full and r1–r10 by targeted search — for the compliance-clause
  sites, the leaf-diff attributions, and row 32 by history rather than content.
- **Predecessor namespace contents.** I established only that no path outside the C2 namespace changed since
  `5289b6ce`, that `main` is untouched, and that nothing outside the namespace references the C2 registry.
- **r11's V1, V5, V6, V7, V8, V10** beyond what rows 18, 28 and 35 record; relied on per the review request.

---

## Verdict counts

| | |
|---|---|
| rows | 39 |
| PASS | 29 |
| PARTIAL | 1 |
| NOTE | 5 |
| **FAIL** | **4** |
| notes | 9 (2 FAIL, 6 NOTE, 1 INFO) |

Counts extracted mechanically from the verdict column of the checklist above, not hand-tallied — for the reason
given in Note 5. The four FAIL rows are **2 distinct defects**: rows 8, 9 and 12 are the single finding of Note 1
(row 12 is the "did the repair introduce a new defect?" row and points at both), and row 13 is Note 2.

**Distinct blocking defects: 2.**

**VERDICT: NOT_READY.**

**The science, the gate and the integrity envelope are clean, and I re-derived them rather than inheriting them:**
four producers byte-identical (three artifacts plus B0 at 7/7), `D_PARTIAL` with closed {305, 306} and open
{307, 308, 309}, all three gap falls and both Γ exact to full precision, `BOTH_PASSES_OK` with 45/45 consumed
constants at 256 and 384 bits and 18/18 `certified`, 43/43 mutants with 0 undetected reproducing sha
`512180f32a5c…`. 142 additions and nothing else since `5289b6ce`; the gate byte-exact at `098dd7f5…` and at
exactly one commit; `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a`; `main` untouched;
coverage map r4 `a3bddd83…` intact at `f2ac1eb3` with no r5 anywhere; guard DENY and no lifecycle artifact
pre-empting freeze, qualification, seal, adoption or adjudication; all eleven prior reviews committed and
unedited.

**r11 FAIL 1 is fully and genuinely repaired**, and I say so having rebuilt the ledger from the git object store
over all 115 committed evidence and config files without looking at the campaign's list: 19 leaves, three files,
9 + 4 + 6, every cell right, nothing missing. That was the harder of r11's two findings and it was answered
properly.

**The namespace is not yet fit to freeze**, for two narrow reasons, both introduced by `6aa2040a` and neither
touching evidence: freezing now would freeze (i) a disposition row stating that both of r11 FAIL 2's compliance
clauses were deleted when one survives verbatim eight lines into the next section, and is false where it stands;
and (ii) a front-door provenance paragraph whose nineteen leaves decompose as eleven and which calls a nine-leaf
correction "exactly one of them", contradicting the ledger it forwards the reader to. The repairs are one clause
and one word. If the campaign makes them, it should make only them, and it should not write a third sentence
saying that it has.

**On the calibration.** I think it is right and I applied it as written. I did not withhold a ready verdict to
avoid leniency: the six NOTEs and the INFO are genuinely non-blocking, I say so plainly, and I have recorded
twelve corpus claims as sound — including the two this round created and got right — specifically so that a
thirteenth round is not spent re-deriving them. Nor did I grant one to end the cycle: a disposition table that
reports an unperformed repair is a defect about the campaign's reliability, and a provenance paragraph that does
not sum is a defect about evidence provenance. Both are named in the calibration. **If these two sentences are
repaired and nothing else is disturbed, I see nothing else in this namespace that should block a freeze** — and
I looked, over the whole namespace, in prose, tables, code and every string leaf of every committed JSON.
