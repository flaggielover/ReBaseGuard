# Sixth independent pre-freeze review — K5 Campaign C2

**VERDICT: NOT_READY** — 33 rows, 27 PASS, 5 NOTE, **1 FAIL**. One freeze-blocking defect, text only, in
`README.md`. **Yes, the repair introduced a new defect again**: it is the eleventh instance of the campaign's
documented pattern and it is the third consecutive round in which the defect is in the README's account of its own
review history.

r5's two FAILs are genuinely repaired. Everything else I checked — the additivity, the frozen gate, the producers,
the corrected factual claims, the decision, the 306 referral — is sound, and I could not break any of it.

## Reviewer context

Fresh context. I wrote none of this work and had no part in rounds one to five. Worktree
`/Users/suzhe/ReBaseGuard-k5c2`, branch `p5y-k5-tail-c2`, HEAD `ec5b08ca`, reviewed 2026-09-21. Read-only
throughout: no file in the namespace was modified except this one, no writing git command was run, AWS/PS1 was not
touched, and no predecessor namespace, `main` or coverage map was read for anything but integrity.

**What I re-derived myself, from source, not accepted from any earlier review:**

- The complete **leaf-level diff of `C2_D1_BLOCKER.json` across every commit that has ever touched it**
  (`e71378a0`, `55c4cf00`, `d6a4def5`, `92c5d199`), by key, with per-transition counts — rather than accepting
  r5's version of it.
- `DOMINANT_BLOCKER_1/2/3` read out of **`5a94568a`'s own copy** of that artifact and compared against `e71378a0`
  and HEAD, to test C2's claim that the blocker-ranking correction was a document table fixed against evidence
  that never changed.
- The r5-note-8 qualification, from the artifact: the D_lo/τ ratio at cell 309 under `relative_gain`, and the
  absolute difference, and the factor by which the equal-A0 renormalisation multiplies each.
- C2's assertion that r5 was **wrong** about r1's `NOT_CHECKABLE_LOCALLY` rows, and that r2's self-report does not
  reconcile — both checked in the review files themselves, by grep and by reading both verdict tables.
- Every row of the erratum's new navigation table — each round's reviewed commit, taken from that review's own
  header or footer, and each FAIL count, taken from that review's own verdict section.
- Three producers re-run from the committed code and compared **byte-for-byte** against their artifacts:
  `c2_d1_blocker.py`, `c2_mutations.py`, `c2_critical_ratio.py`. Also `c2_b0_verify.py`, which I re-ran in full.
- The D-stage class, the closed subset and all three gap falls, recomputed from `C2_D5_FORECAST.json` against the
  gate's frozen baseline with `fractions.Fraction`, and the sign of every `Gamma_exact` against its float.
- Additivity and namespace containment since `5289b6ce`; the gate's sha256 and commit count; the D5 files' commit
  history; the coverage-map sha and history.

I read the five earlier reviews and the erratum, but I re-derived every claim I report on below rather than
inheriting it — which is the failure mode this campaign has recorded against itself four times.

---

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| **A. r5's two FAILs** |
| 1 | r5 FAIL 1 — the superseded r3-era paragraphs under §"The pattern, named" | **PASS** | Gone. `git diff 1663f558..ec5b08ca` removes all of them; the section no longer asserts that round three avoided a fourth instance. A marker at `ERRATUM_C2.md:306–310` records what stood there and why it was wrong. Removal, not rewording |
| 2 | …and the section is now internally consistent about round three | **PASS** | The table records round three producing instances three and four; no surviving sentence contradicts it |
| 3 | r5 FAIL 2 — the unrequested README PASS/NOTE/INFO parentheticals | **PASS** | `README.md:40–44` now carries FAIL counts only. Deleted, not corrected, with a footnote at `:47–50` saying why. This is the lesson ("make that change and stop") applied to the defect itself |
| 4 | the five FAIL counts the README does keep | **PASS** | 6 / 3 / 1 / 3 / 2 against each review's own verdict section: r1 `| **FAIL** | **6** |`; r2 `| **FAIL** | **3** |`; r3 "**1 FAIL**"; r4 "**28 PASS, 5 NOTE, 3 FAIL**"; r5 "27 PASS, 5 NOTE, **2 FAIL**". Sum 15 = "all fifteen FAILs dispositioned" at `:45` |
| **B. did the repair introduce a new defect?** |
| 5 | `README.md` Result section, review history | **FAIL** | `:69` "**Four** independent pre-freeze reviews have run" and `:75` "**three separate times** — an error introduced by a *repair*". Both stale, in the paragraph this repair round edited around. Note 1 |
| 6 | erratum navigation table — commits | **PASS** | r1 `5a94568a` (its own title line), r2 `ef58310c` (title line), r3 `55c4cf00` (footer), r4 `17123368` (reviewer-context block and footer), r5 `1663f558` (footer). All five match; all five are commits in this branch's history, in that order |
| 7 | erratum navigation table — FAIL counts and disposition sections | **PASS** | Counts as row 4. Each named section exists and contains that round's dispositions |
| 8 | the new §"Dispositions from the FIRST pre-freeze review" header | **PASS** | r1's 79 / 60 / 10 / 3 / 6 transcribed exactly from r1's verdict table; the three subsections under it disposition all six of r1's FAILs (6, 61, 62, 30, 51, 53) |
| 9 | the self-caught "four-and-three" correction to the pattern split | **PASS — verified independently** | I classified the seven table rows myself: doing-more = rows 1, 3, 6, 7; failing-to-clean-up = rows 2 (the claim left contradicting itself), 4 (the source comment r3 named), 5. Four and three. The by-kind tally (2 + 2 + 1 + 1 + 1) also sums to seven. `a58bbdd8`'s correction of "five-and-two" is right |
| 10 | the self-caught "got two wrong" → "only one was wrong" correction | **PASS** | Consistent with rows 15–16 below: r1's transcription was faithful, r2's was a faithful copy of a non-reconciling header |
| 11 | pattern-section instance tally | NOTE | Table has seven rows; prose adds two more from the r5-disposition commit; the tenth, disclosed at `ERRATUM_C2.md:22–23`, is not counted here, and `:253` still says "Four review rounds". Note 2 |
| 12 | r5's review file committed verbatim and unedited | **PASS** | `git log --all -- review/REVIEW_C2_PREFREEZE_R5.md` → one commit, `fb4d688b`. Same for all five review files: one commit each, never amended |
| 13 | did the repair touch anything but the two documents and r5's file? | **PASS** | `git diff --stat 1663f558..ec5b08ca` = `ERRATUM_C2.md`, `README.md`, `review/REVIEW_C2_PREFREEZE_R5.md` (new). No code, no evidence, no config |
| **C. the corrected factual claims** |
| 14 | "exactly ONE published value has ever changed — the C_T sensitivity row, nine leaves" | **PASS — verified independently** | My own leaf diff across all four commits touching `C2_D1_BLOCKER.json`: the only leaves whose **values were replaced** are the nine `/cells/{307,308,309}/sensitivity_10pct_improvement/C_T/{magnitude, delta_vs_base, relative_gain}`, at `e71378a0 → 55c4cf00`. `Gamma`, `magnitude`, `gap_above_1`, `required_uniform_atom_constant_reduction`, `DOMINANT_BLOCKER_*`: never. Wording note at Note 3 |
| 15 | the blocker-ranking correction was a **document** table fixed against evidence that never changed | **PASS — verified at `5a94568a`** | `git show 5a94568a:…/C2_D1_BLOCKER.json` → `DOMINANT_BLOCKER_3 = {"term": "order0_residual_fF", "share": 0.0028459509917783594}`, byte-identical to `e71378a0` and to HEAD. The JSON said `order0_residual_fF` from its first commit. `D1_BLOCKER_DIAGNOSIS.md:23–29` describes the correction accurately, and the corrected table's own percentages give f_F > f_D > f_H on all five cells |
| 16 | C2's claim that r5 was **WRONG** that r1 has zero `NOT_CHECKABLE_LOCALLY` rows | **PASS — C2 is right, r5 was wrong** | The string occurs five times in `REVIEW_C2_PREFREEZE.md` (lines 100, 101, 102, 419, 427); rows 73, 74, 75 carry that verdict; its verdict table records `NOT_CHECKABLE_LOCALLY | 3` against `total | 79`. C2's deleted parenthetical "60 PASS / 10 INFO / 3 N/A" was a faithful transcription |
| 17 | C2's claim that r2's own self-report is internally inconsistent | **PASS — C2 is right** | `REVIEW_C2_PREFREEZE_R2.md:355–363`: PASS 55, INFO 3, NOTE 5, FAIL 3, total 71. 55 + 3 + 5 + 3 = 66 ≠ 71. C2 transcribed r2's header; the arithmetic error originates in r2 |
| 18 | C2's independent recount, r2 = 62/4/2/3 | **PASS** | Reconciles to r2's own stated total of 71, which its header breakdown does not. Consistent with my own row scan |
| 19 | C2's independent recount, r1 / r3 / r4 | PASS with one caveat | r1 60/10/3/6 = 79 ✓; r3 31/7/1 = 39 ✓ against its header. r4 28/4/3 = 35 against r4's own stated 36 rows. Note 4 |
| 20 | r5 note 8 — ratio vs absolute difference at cell 309 | **PASS — verified exactly** | From the artifact: D_lo `relative_gain` 0.08718592913635831, τ 0.08168084117495086. Ratio 1.067401…, i.e. **1.0674**. Difference **0.00550508796…** → ×11 = **0.06055596757…**, i.e. **0.005505 → 0.060556**. Both figures in `ERRATUM_C2.md:275–279` are right, and the ratio/difference distinction is stated correctly |
| **D. integrity** |
| 21 | all-additive since `5289b6ce` | **PASS** | `git diff --name-status 5289b6ce..HEAD` → 136 paths, **every one status `A`**. No `M`, no `D`, no `R` |
| 22 | in-namespace since `5289b6ce` | **PASS** | All 136 paths are under `level4/closure_proofs/p5y_k5_tail_c2_closure/`. Nothing else |
| 23 | gate frozen at one commit, sha as pinned | **PASS** | `git log --all --follow` on `config/FEASIBILITY_GATES_C2.json` → exactly one commit, `87309610`. `shasum -a 256` = `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`, equal to `C2_D5_FORECAST.gate_sha256` |
| 24 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` untouched since `5a94568a` | **PASS** | Their entire commit history is `51f8844b`, `5a94568a`. Nothing since |
| 25 | producers reproduce byte-for-byte | **PASS — re-run here** | `c2_d1_blocker.py` → `cmp` identical to `C2_D1_BLOCKER.json`; `c2_mutations.py` → identical to `C2_MUTATIONS.json`; `c2_critical_ratio.py` → identical to `C2_CRITICAL_RATIOS.json`. Three for three, no differences |
| 26 | mutation suite 43/43, 0 undetected | **PASS** | From the regenerated artifact: `applied 43, real_mutants 35, static_assertions 8, detected 40, equivalent 3, undetected [], pass true` |
| 27 | `C2_RECERTIFY_306.json` = `BOTH_PASSES_OK` | **PASS** (artifact, not re-run) | `verdict: BOTH_PASSES_OK`, 18 artifacts, cell 306, `registry_sha_pin_ok: true`. FLINT re-run not attempted — see "what I did not check" |
| 28 | `C2_REGISTRY_VERIFY.json` = pass / 105 | **PASS** (artifact, not re-run) | `pass: true`, `artifacts_rechecked: 105`, `cells_checked: 5`, `problems: []`, registry sha matches `C2_D5_FORECAST.registry_c2_sha256` |
| 29 | predecessors, `main`, coverage map r4 untouched; no r5 | **PASS — re-run here** | Implied by rows 21–22, and confirmed directly: `K5_COVERAGE_MAP_R4.json` sha `a3bddd83234f…`, single commit `f2ac1eb3`; `find` returns no `K5_COVERAGE_MAP_R5.json` anywhere in the repo; `main` is an ancestor of HEAD. I also re-ran `c2_b0_verify.py` in full: **7/7 ALL_PASS**, and the regenerated artifact differs from the committed one in exactly one field, the recorded `head` (`5289b6ce` then, `ec5b08ca` now) |
| 30 | nothing pre-empts freeze, qualification, seal or adjudication | **PASS** | `R_STAGE_DESIGN.md:1` "**DESIGN ONLY; nothing is executed**", guard DENY, no authorization artifact, blocking precondition first. `CELL_306_ADOPTION.md:10–13` states adoption is not conferred and that nothing here may say it is. No seal, no protocol, no coverage map r5, no ADOPTED claim |
| **E. the decision, freshly** |
| 31 | `D_PARTIAL`, closed = {305, 306}, under the frozen gate | **PASS — re-derived** | From the forecast: 305/306 `pass: true`; 307/308/309 `pass: false` with gap falls recomputed by me from the gate's own baseline gaps as **0.462852 / 0.245931 / 0.183898**, matching the published 0.46285183 / 0.24593099 / 0.18389841. Not D_STRONG (not all five). Not D_USEFUL (309 at 18.39 % < the frozen 20 %). Closes ≥ 1 → **D_PARTIAL**. Mechanical, and correct |
| 32 | the gate is applied as frozen, not as C2 would now prefer | **PASS** | The gate's 20 % bar costs C2 the better class by 1.6 points and is not adjusted; the pre-registered componentwise minimum is applied even though it reduced to "use C2"; and Note 11's cheaper combination, which would clear 20 % on all three, is **refused** as post-hoc and recorded as a blocking precondition on the R stage instead. That is the gate constraining the campaign against its own interest, which is what a gate is for |
| 33 | the cell-306 referral to the adjudicator | **PASS — sound governance** | Note 5 |

---

## Notes

### Note 1 (FAIL) — the README states the wrong number of reviews, and the wrong number of repair-introduced errors, two lines from a sentence that contradicts it

`README.md:69–76`:

> **Read `ERRATUM_C2.md` before relying on anything here.** **Four** independent pre-freeze reviews have run, and
> each returned NOT_READY. […] and — **three separate times** — an error introduced by a *repair* to a previous
> round.

Both figures are stale, and the document contradicts itself about both:

- **Five** reviews have run. The README's own phase table at `:40–44` lists r1 through r5; `:45` says "all
  **fifteen** FAILs dispositioned", which is 6 + 3 + 1 + 3 + 2 and therefore counts five reviews; and `:81`, in
  the very next paragraph — the one this repair round rewrote — says "which the **fifth** review confirmed".
- Repairs have introduced an error that a review then caught **six** times, not three: r2 FAIL 65, r3 FAIL 6, r4
  FAIL 1, r4 FAIL 2, r5 FAIL 1, r5 FAIL 2 — and four more were caught by C2's own self-audit. The erratum's
  pattern table records seven and its prose three more. "Three separate times" was true when r4 was the last
  round; it is not true now.

The enumeration that follows at `:73–76` ("what they found was…") also lists r1's, r2's and r4's findings and
none of r5's.

**Why this is a FAIL and not a note.** I applied the calibration I was given, and I want to be explicit about
where this lands. It is not a phrasing I would have chosen differently. It is a hard, present-tense, wrong count
in the document an adjudicator reads first, flatly contradicted by a table twenty-nine lines above it and by a
sentence two lines below it. The two quantities it gets wrong — how much independent scrutiny this campaign has
had, and how often its repairs have broken something — are precisely the campaign's own reliability record, which
is the thing `ERRATUM_C2.md` exists to disclose and the thing the README's own paragraph is trying to state. Both
errors understate the problem in the campaign's favour. And this is the **third consecutive round** with a
freeze-blocking defect in the README's account of its own review history: r4 FAIL 3 (README stale since
`12585997`), r5 FAIL 2 (unrequested counts, one wrong), and now this. A frozen README that says four when five is
a permanent artifact defect, and "it will be right in the next commit" is exactly the mechanism by which this
campaign's documented pattern propagates.

**The shape is the documented one, again.** `ec5b08ca` rewrote the paragraph at `:79–83` — correctly; the new
paragraph is right and I verified every claim in it (rows 14, 15, 20) — and did not look up one line at the
paragraph it was correcting *from*. That is instance eleven: a correct primary fix, with the text around it left
stale. This time the stale text is not an ornament the fix added; it is the sentence the fix should have carried
along with it.

**The repair is two numbers in one sentence, plus adding r5's findings to the enumeration.** Nothing recomputes,
no sha moves, no artifact regenerates. I would expect a seventh round to be very short.

### Note 2 (NOTE) — the pattern section's tally lags its own disclosures by one, and still says "four review rounds"

`ERRATUM_C2.md:253` introduces the table with "Four review rounds", and the table's seven rows stop at round four.
The prose below correctly discloses that round five's repair did it twice more, and `:270` says "Three were
caught by C2 rather than a reviewer" — but a **tenth** instance is disclosed at `:22–23` ("An earlier version of
this paragraph said 'two published numbers have changed'… Corrected in self-audit") and is self-caught, so the
true figures are ten instances and four self-catches, not nine and three.

I deliberately did **not** fail this, and I want the reasoning on the record because it is close to the line. The
section discloses every instance somewhere in the document, including the uncounted one, prominently, at the top.
"Four review rounds" is readable as labelling the table's scope rather than asserting how many reviews exist —
unlike the README sentence, which asserts it outright. And the direction of the imprecision is mixed: it
undercounts instances (favourable) and undercounts self-catches (unfavourable). An adjudicator reading this
section gets a correct picture of the failure mode, its persistence and its harmlessness to the arithmetic. That
is what the section is for, and it does it. Fixing it while the README is fixed would be tidy; blocking on it
would be the loop.

### Note 3 (NOTE) — "nine leaves have ever changed" counts value replacements only

My own leaf diff of `C2_D1_BLOCKER.json` across its four commits:

| transition | value-replaced | added | removed |
|---|---|---|---|
| `e71378a0 → 55c4cf00` | **9** (C_T `magnitude`/`delta_vs_base`/`relative_gain` on 307, 308, 309) | 3 (`admissibility_clamp`) | 0 |
| `55c4cf00 → d6a4def5` | 0 | 50 (25 `effective_improvement`, 25 `gain_per_unit_of_input_moved`) | 0 |
| `d6a4def5 → 92c5d199` | 0 | 5 (`per_unit_comparability`) | 20 (`gain_per_unit_of_input_moved` off the four non-C_T rows) |

So the strict totals over the whole history are **9 replaced, 58 added, 20 removed**. The claim as C2 states it —
"exactly nine leaves have ever changed", "exactly one published value has changed" — is **true on the reading it
plainly intends** (a published value being replaced by a different value), and every addition and removal is
separately disclosed: the 38-leaf accounting in the r2 FAIL 66 row, and the r4 FAIL 1 row that explains the field
restriction. I note it only because "the only ones that have ever changed" at `:19–20` is stated without the
qualifier, and a successor doing this diff will see 87 leaves move. One clause ("the only leaves whose value has
ever been replaced") would close it. Not blocking: nothing about the science or the decision turns on it.

### Note 4 (NOTE) — the independent recount of r4 does not reconcile with r4's row count

`ERRATUM_C2.md:244–245` gives "r4 28/4/3". That sums to 35; r4's own verdict section says "**36 rows**: 28 PASS,
5 NOTE, 3 FAIL". Both can be defended: r4's checklist has exactly four rows whose verdict cell reads `NOTE` (16,
17, 18, 26) and three that read `**FAIL**` (4, 11, 23), plus a row 36 whose verdict is the hybrid "PASS / **FAIL**
on the README". C2's recount is a fair count of the NOTE cells; it simply leaves the hybrid row unplaced, so it
does not sum to 36.

This sits in the one passage of the document whose whole argument is that counts which do not reconcile should
not be propagated. It is a small irony, not a defect an adjudicator can be misled by — the FAIL count, which is
the only figure anything depends on, is right. Either add "(r4's own header says 36 rows; the difference is its
hybrid row 36)" or drop the non-FAIL recounts, which is the lesson the same section reaches.

### Note 5 (PASS, recorded) — the cell-306 referral is the right call, and I formed my own view of it

The gate defines no margin floor and no degradation scenario. C2 has already seen 306's margin (11.2 %, against
1.9 % under C1). Any floor C2 freezes now is chosen with the answer in hand, and `CELL_306_ADOPTION.md` says so:
"Writing one would be worse than having none, because it would look like a pre-registration." I agree, and I think
that is the substantive governance judgement of this campaign. A post-hoc threshold that *looks* pre-registered is
worse than an acknowledged gap, because it launders the choice.

Three things make the referral sound rather than an evasion:

1. **It is pre-committed in both directions, in writing, before any adjudication exists** — floor met → adopt
   {305, 306}; floor failed or declined → adopt 305 only. C2 cannot benefit from the answer either way.
2. **The frozen `D_PARTIAL` rule is satisfied in both branches**, because 305 is carried unconditionally. The
   referral does not put the gate's "a non-empty closed subset is always adopted" clause at risk, which is the
   thing that would have made it an evasion.
3. **The case against 306 is stated by C2, in C2's own summary table, against C2's interest**: Γ +0.029163 under
   a ×1.25 degradation, "does not close", set beside 305's "still closes". The honest framing — "a *sound*
   closure with a *thin* margin, and how much margin a permanent adoption should require is a policy question" —
   is the correct characterisation, and the policy question genuinely does belong outside the campaign.

The residual trust surface is unchanged and correctly named: one Arb/FLINT implementation run twice, carried
forward as **N9**. That is a limitation of the programme, not of this referral.

---

## What I did not check

- **The Arb/FLINT layer.** I did not re-run `c2_recertify_306.py` or the 105-artifact registry verification. I
  read both artifacts and checked their sha pins against the forecast, but the supersolution machinery itself is
  N9 and I did not touch it. Rounds two and four exercised it on FLINT; I did not.
- **The D5 forecast producer.** I confirmed its two files have not moved since `5a94568a` by commit history, and
  re-derived the class, the closed subset and the gap falls from the committed artifact, but I did not re-execute
  `c2_d5_forecast.py` (it needs the K1 record store, `--records`).
- **An independent implementation of TC-T, the twelve-term radius decomposition, the blocker shares or the
  `order3_attribution` counterfactual.** r1 and r2 each wrote one from the theorem documents and reproduced C2's
  numbers bit-exactly; I relied on that, as my brief permitted, and checked reproducibility instead (row 25).
- **Upstream.** C1's registry, Campaign B's measurements, the adopted Campaign-A evidence model and the cover
  ledger were taken as given.
- **The R-stage design's cost model and address minimality**, and `D_PRIME_OPPORTUNITY.md`'s arithmetic — settled
  in earlier rounds, untouched by this diff, and I read them only far enough to confirm nothing pre-empts
  authorization.
- **AWS/PS1.** Not contacted. No writing git command was run; no file in the namespace was modified except this
  one.

---

## Verdict counts

**NOT_READY** — 33 rows: **27 PASS, 5 NOTE, 1 FAIL.**

Freeze-blocking:

1. **Note 1** — `README.md:69` says four independent reviews have run when five have, and `:75` says a repair
   introduced an error three times when reviews have caught six; both are contradicted inside the same document,
   `:81` two lines below being the clearest. Third consecutive round with a blocking defect in the README's
   account of its own review history. Eleventh instance of the documented pattern.

Non-blocking: notes 2, 3, 4, 5.

## On the calibration I was given

I was asked to say explicitly whether the bar I was handed is legitimate or is being lowered to manufacture a
pass. **I think it is legitimate, and I applied it as written.** A defect must be capable of misleading an
adjudicator about the science, the decision, the governance state or the campaign's reliability; taste and
structure are notes. That is the right bar for a pre-freeze review, and it is not lower than the bar r5 used —
r5's own two FAILs both clear it comfortably, and so would r4's three.

I also think the loop the calibration is worried about is real, and I have tried not to feed it: Note 2 is a
defect I could have failed and chose not to, and I have said why. But the bar cuts the other way here too. The
one thing I am blocking on is not prose quality. It is a wrong count, in the front-door document, of how many
independent reviews this campaign has survived — stated two lines from a sentence that names the fifth one. If
that is not a FAIL, then the README's account of the campaign's own reliability is not under review at all, and
r4 FAIL 3 and r5 FAIL 2 were both wrongly decided. They were not.

**What is not wrong, and should not be lost in a sixth NOT_READY.** The science is finished and correct. Every
producer I re-ran reproduces its artifact byte-for-byte. Exactly nine leaves have ever had a value replaced in
the campaign's central artifact, all nine disclosed and located in one row of one sensitivity table, and the
blocker-ranking correction really was a document fixed against evidence that has said `order0_residual_fF` since
`5a94568a`. No Γ, magnitude, margin, requirement, gap fall, class or adopted subset has ever moved. The gate is
frozen at one commit, its sha still matches, and it was applied against the campaign's own interest on the one
cell where it cost C2 the better class. Everything since `5289b6ce` is additive and inside the namespace; `main`,
the predecessors and coverage map r4 are untouched and there is no r5. Nothing pre-empts freeze, qualification,
sealing or adjudication. `D_PARTIAL` with closed = {305, 306} is correct, and the cell-306 referral is the right
call for the right reason. **One sentence in one file stands between this namespace and a freeze.**

---

*Sixth independent fresh-context pre-freeze review, 2026-09-21, HEAD `ec5b08ca`. Read-only; this file is the only
file written.*
