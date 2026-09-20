# Fifth independent pre-freeze review — K5 Campaign C2

**VERDICT: NOT_READY** — 34 rows, 27 PASS, 5 NOTE, **2 FAIL**. Two freeze-blocking defects, both text only,
neither touching a computed number.

**Yes — the repair introduced a new error again, and this time twice.** Both are the documented shape: a correct
primary fix with a second, unverified thing stacked on top. One of them is in `ERRATUM_C2.md` §"The pattern,
named" itself — the round-4 rewrite of that section left the superseded r3-era paragraphs standing underneath it,
so the section now asserts both that round three avoided a fourth instance of the pattern and, two paragraphs
above, that round three produced instances three *and* four. The other is in `README.md`, in exactly the row r4
FAIL 3 asked C2 to rebuild: the four reviews are now all listed and every **FAIL** count is right, but the
PASS/NOTE/INFO parentheticals C2 added on top are wrong for r1 and r2 and cannot be reconciled with those files.

Everything r4 blocked on substantively is genuinely repaired, and the science is sound. I attacked the C_T
per-unit reading independently and could not break it.

## Reviewer context

Fresh context. I wrote none of this work and had no part in rounds one to four. Worktree
`/Users/suzhe/ReBaseGuard-k5c2`, branch `p5y-k5-tail-c2`, HEAD `1663f558`, reviewed 2026-09-21. Read-only
throughout: no file in the namespace was modified except this one, and no writing git command was run. AWS/PS1
was not touched; no predecessor namespace, no `main`, no coverage map was read for anything but integrity.

**What I re-derived myself, from source, not accepted from any earlier review:**

- All three producers re-run under stdlib Python 3 with `PYTHONINTMAXSTRDIGITS=0` and `cmp`-diffed against their
  committed artifacts: `c2_d1_blocker.py`, `c2_critical_ratio.py`, `c2_mutations.py`. All byte-identical.
- The **complete leaf-level history** of `C2_D1_BLOCKER.json` across every commit that has ever touched it
  (`e71378a0 → 55c4cf00 → d6a4def5 → 92c5d199`), by key path, with per-step changed/added/removed counts — this
  is what I used to adjudicate the README's strongest claim rather than inspecting only the current state.
- The exact operator constants for all five cells from `REGISTRY_C1.json` as `Fraction`s, and from them Ā, τ/D_lo,
  **which branch of `min(Ā, τ/D_lo)` binds on each cell**, and the exact C_T headroom `(C_T − τ)/C_T`.
- An independent re-run of r4's stress test, written from the producer's own primitives: the C_T response
  recomputed at each cell's own admissible cut, at a **common** admissible cut, and as a **marginal slope** at
  ~0, to test the "nearly exhausted" reading against the unequal-window refutation.
- The `relative_gain`, A0-renormalised and per-unit-of-input columns for `D_lo` and τ on all five cells, and
  their ratios, to adjudicate the self-caught correction in `1663f558`.
- Verdict tallies for all four committed reviews, parsed from their checklist tables cell by cell.
- `git diff --name-status 5289b6ce..HEAD`; the gate sha; the coverage-map r4 sha; the file histories of
  `c2_d5_forecast.py`, `C2_D5_FORECAST.json`, `FEASIBILITY_GATES_C2.json` and `evidence/prefreeze/`.
- The README `Result` table checked leaf by leaf against `C2_D5_FORECAST.json`.
- A full read of `README.md`, `ERRATUM_C2.md`, `OPEN_NOTES_DISPOSITION_C2.md`, `phase_d/*`, `phase_r/*` as a set.

**What I took on trust:** the four committed reviews' accounts of what *they* verified in rounds one to four,
except where I re-derived it above; C1's, Campaign B's and the cover ledger's upstream evidence, treated as given
inputs; the FLINT re-certification of cell 306 (I did not re-run Arb — `C2_RECERTIFY_306.json` is unmodified
since `55c4cf00` and r4 re-certified two of its artifacts independently).

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| **r4 FAIL 1 — the field that inverted the ordering** |
| 1 | is `gain_per_unit_of_input_moved` gone from the D_lo / τ / D1 / D2 rows? | PASS | yes. Enumerated from the committed artifact: the field is present on the `C_T` row of all five cells and on **no other row of any cell**. The leaf diff `d6a4def5 → 92c5d199` shows exactly 20 removals, all `gain_per_unit_of_input_moved` |
| 2 | does the artifact now carry the comparability limit? | PASS | `per_unit_comparability` on the `C_T` row of all five cells, 5 additions in the same leaf diff. §2 of `D1_BLOCKER_DIAGNOSIS.md:86–93` states the same limit in prose, as r4's remedy (c) required "in both the artifact and §2" |
| 3 | **is restricting to `C_T` sufficient, or should the field have been removed entirely?** | PASS — **sufficient, and removal would have been worse** | see note 1. I re-derived the across-cells C_T reading three ways and it survives all three |
| 4 | is the C_T-across-cells comparison sound given the clamp gives different cells different windows? | PASS — **tested specifically, independently of r4** | own-cut 0.149584 / 0.150387 / 0.152067 / 0.153555 / 0.153042 (reproduces the published column exactly); common cut 6.0997 % → 0.149886 / 0.150686 / 0.152356 / 0.153692 / 0.153042; marginal slope → 0.150501 / 0.151297 / 0.152965 / 0.154293 / 0.153622. Same shape, same ordering, rise-then-ease at 309 in all three. The window is not driving it |
| 5 | **is `per_unit_comparability` another instance of the pattern (an unrequested extra)?** | PASS — **no, and I looked for it** | r4's note 2 offers three remedies; remedy **(c)** is "keep it and add an explicit caveat, **in both the artifact and §2**". The string is that caveat, requested verbatim. C2 in fact did (a) for the four other rows *and* (c) for `C_T`, which is stricter than either alone. Not an instance |
| 6 | is the in-source cause explanation correct — that D_lo × 1.1 and τ / 1.1 each divide A0 = τ/D_lo by exactly 1.1? | PASS — **verified, including the premise nobody had to state** | A0 = `min(Ā, τ/D_lo)`, so the identity only holds if the τ/D_lo branch binds. It does, on all five cells: Ā = 8.290719 / 7.912417 / 7.555613 / 7.217875 / 6.900983 against τ/D_lo = 6.884064 / 6.411423 / 5.987123 / 5.590460 / 5.210202. Given that, both perturbations send A0 → A0/1.1 exactly, and the input fractions are 1/10 and 1/11 |
| 7 | does the per-unit column really invert the D_lo > τ ordering, as claimed? | PASS | τ/D_lo per-unit ratio is 1.025229 / 1.027292 / 1.027587 / 1.028069 / 1.030544 — τ ahead on **all five**, against `relative_gain` where D_lo leads on all five. r4's finding is correct and C2's account of it is correct |
| 8 | is the restriction load-bearing as the comment claims? | PASS | the comment's "REVERSE the D_lo > τ ordering on all five cells" is exactly what I measure. Correctly stated, correctly scoped |
| **r4 FAIL 2 — the source comment** |
| 9 | is the withdrawn "refuses exactly as `deflated_consume.atom_constants`" claim gone from `c2_d1_blocker.py`? | PASS | `code/c2_d1_blocker.py:62–70` rewritten. No occurrence of the overclaim survives |
| 10 | does the replacement correctly name `atom_constants_r2`? | PASS | line 62: "The pinned consumer `deflated_consume.atom_constants_r2` validates these premises". Correct entry point |
| 11 | does it correctly disclaim equivalence? | PASS | "This guard enforces the four premise inequalities ONLY. It is deliberately NOT a claim of equivalence… which additionally type-checks every input… and post-checks that no r2 constant exceeds its r1 counterpart." The guard tests `Dlo > 0 and tau >= 1 and C >= tau and Abar >= 1` — four, as stated |
| 12 | is the withdrawal recorded rather than silently made? | PASS | the comment carries its own erratum ("An earlier version of this comment said… which overclaimed; withdrawn on pre-freeze review r4"), and `ERRATUM_C2.md:166–169` corrects the false "corrected in both places" in place rather than deleting it |
| 13 | does the overclaim survive anywhere else in the namespace? | PASS | swept `*.md`, `*.py`, `*.json` outside `review/`. No surviving assertion |
| **r4 FAIL 3 — the README** |
| 14 | are all four reviews now listed? | PASS | `README.md:40–43`, one row each, each pointing at the right file |
| 15 | is the FAIL count per review right, and does the total reconcile? | PASS | 6 / 3 / 1 / 3 from my own tallies; 6 + 3 + 1 + 3 = 13, and `ERRATUM_C2.md` carries exactly **13** FAIL disposition rows. "all thirteen FAILs dispositioned" is correct |
| 16 | **are the PASS / NOTE / INFO counts right?** | **FAIL** | **no, on two of the four rows.** See note 2 |
| 17 | is "exactly two published numbers changed" correct? | PASS | yes, and I checked it against history rather than the current state. (i) the C_T sensitivity row on 307/308/309 — nine leaves, at `55c4cf00`; (ii) the `DOMINANT_BLOCKER_3` ranking in `D1_BLOCKER_DIAGNOSIS.md`, at `12585997` (f_H → f_F), where the *artifact* had always said `order0_residual_fF` and only the prose was wrong. Both in the D1 diagnosis, both disclosed, and no third |
| 18 | **"no Γ, magnitude, margin, requirement, gap fall, class or adopted-subset value has changed at any point"** | PASS on substance, NOTE on wording | I diffed every leaf across all four commits that ever touched `C2_D1_BLOCKER.json`. **Exactly nine leaves have ever changed**, all of the form `/cells/{307,308,309}/sensitivity_10pct_improvement/C_T/{magnitude, delta_vs_base, relative_gain}`. `/cells/*/Gamma`, `/cells/*/magnitude`, `/cells/*/gap_above_1`, `/cells/*/required_uniform_atom_constant_reduction`, `DOMINANT_BLOCKER_*` and every D5 value: **never**. The claim is true as intended. See note 3 for the wording |
| 19 | do the README `Result` numbers match the D5 forecast? | PASS | Γ −0.088029 / −0.030469 / +0.033133 / +0.102700 / +0.162249 and gap falls 46.29 / 24.59 / 18.39 % all match `C2_D5_FORECAST.json` leaf for leaf; `D_PARTIAL`, closed {305, 306}, `materially_tightened` 307✔ 308✔ 309✘; 20 − 18.39 = 1.61 pp, "fails on one cell by 1.6 percentage points" ✔ |
| **the self-caught correction in `1663f558`** |
| 20 | does renormalising by equal A0 effect preserve `relative_gain`'s ratio exactly? | PASS — **verified on all five cells** | ratio of `relative_gain` = 1.072931 / 1.070776 / 1.070469 / 1.069968 / **1.067398**; ratio after dividing both rows by 1/11 = **identical to every printed digit**. "1.0674 at cell 309 either way" is right |
| 21 | does r4's A0-normalised table reproduce? | PASS | D_lo per equal A0 effect 0.946320 / 0.949350 / 0.954024 / 0.958748 / 0.959045 and τ 0.881996 / 0.886600 / 0.891220 / 0.896053 / 0.898489 — exact match. r4's arithmetic was right; only its word "wider" was loose |
| 22 | is the corrected statement right? | PASS | "divides **both** rows by the same constant 1 − 1/1.1, so it preserves `relative_gain`'s ordering and its ratio exactly" is exactly what the numbers do |
| 23 | **is C2's characterisation of its own error honest, or is it overstating its diligence?** | PASS — honest | it names the error, states it was inherited from a reviewer and restated unchecked, files it as the **fifth** instance of its own named failure mode, and claims only that this is "the first time in five instances" it was self-caught — which `1663f558` predating this review makes verifiable. It claims no more than that. One small qualification in note 4 |
| **determinism and integrity** |
| 24 | `c2_d1_blocker.py` reproduces its artifact byte-for-byte? | PASS | sha256 `1d7715a2b88708cab3082f3e0cd1e188bbcec9343029d9c160f765ceff93db45`, identical to the committed file; 0.4 s |
| 25 | `c2_critical_ratio.py`? | PASS | `cmp` clean against `C2_CRITICAL_RATIOS.json` |
| 26 | `c2_mutations.py`, 43 applied, 0 undetected? | PASS | `cmp` clean against `C2_MUTATIONS.json`. `applied 43`, `detected 40`, `equivalent 3`, `undetected []`, `pass true`, `real_mutants 35`, `static_assertions 8`. 40 + 3 = 43 ✔, and `OPEN_NOTES_DISPOSITION_C2.md`'s "35 real mutants and 8 static assertions" matches |
| 27 | is the regenerated sha re-cited everywhere it is published? | PASS | `601f2f33…` → `1d7715a2…` in both places r4 named (`D1_BLOCKER_DIAGNOSIS.md:3`, `ERRATUM_C2.md:134`). No occurrence of `601f2f33` or the older `62531bf5` survives outside `review/` |
| 28 | is the leaf accounting in `ERRATUM_C2.md:134` now exact? | PASS — **recomputed** | "487 → 525; nine changed; 38 added — 25 `effective_improvement`, 5 `gain_per_unit_of_input_moved`, 5 `per_unit_comparability`, 3 `admissibility_clamp`; nothing removed". My measurement: 487 → 525, changed 9, added 25 + 5 + 5 + 3 = 38, net removed 0. Exact, and r4's note 3 is fully discharged |
| 29 | `git diff --name-status 5289b6ce..HEAD` — all additive, all in-namespace? | PASS | 142 paths, every one `A`, every one under `level4/closure_proofs/p5y_k5_tail_c2_closure/`. Zero modifications outside the namespace |
| 30 | gate sha still `098dd7f5…`, one commit? | PASS | sha256 `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`; `git log` on the path returns exactly one commit, `87309610`, and `C2_D5_FORECAST.json` pins the same sha with `gate_frozen_before_forecast: true` |
| 31 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmodified since `5a94568a`? | PASS | last commit touching either is `5a94568a`. Untouched by all four repair rounds |
| 32 | prefreeze artifacts as specified? | PASS | `C2_RECERTIFY_306.json`: `BOTH_PASSES_OK`, 18 artifacts, `registry_sha_pin_ok true`. `C2_REGISTRY_VERIFY.json`: `pass true`, `artifacts_rechecked 105`, `cells_checked 5`, `problems []`. Neither modified since `55c4cf00` |
| 33 | predecessors byte-unchanged, `main` untouched, coverage map r4 untouched, no r5? | PASS | no path outside the C2 namespace differs from `5289b6ce`. `main` is `c123b9bb` and is an ancestor of HEAD. `K5_COVERAGE_MAP_R4.json` = `a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35`, matching the README; no `K5_COVERAGE_MAP_R5.json` anywhere, and `c2_b0_verify.py:144` asserts its absence as a gate condition |
| 34 | anything pre-empting freeze, qualification, sealing or adjudication? | PASS | nothing. `phase_r/R_STAGE_DESIGN.md:1` "**DESIGN ONLY; nothing is executed**", guard DENY, no authorization artifact, blocking precondition stated up front. `CELL_306_ADOPTION.md:10` "It is not *adopted* yet". `OPEN_NOTES_DISPOSITION_C2.md` carries N1 forward unchanged and states C2 does not pre-empt the bridge |

---

## Note 1 (PASS, and the substantive question the brief asked) — restricting to `C_T` is the right call, and removing it entirely would have been the wrong one

I was asked whether the `C_T`-only restriction is *sufficient*, or whether the field should have gone entirely.
I tested C2's own argument rather than accepting it, and then tested the conclusion the field supports.

C2's argument is that per-unit normalisation is valid for the **same input across cells** and invalid **across
inputs**. The second half I confirm at row 7: the ÷1.1 convention equalises the *A0 effect* of the D_lo and τ
perturbations, which is precisely why their input fractions are unequal, so dividing each by its own input
fraction re-introduces a factor 1.1 in τ's favour and flips a finding §2 puts in bold. That half is unarguable.

The first half is the one that needed testing, because the clamp does give different cells different windows —
9.0909 / 9.0909 / 8.9966 / 7.4903 / 6.0997 %. A per-unit figure computed over unequal windows is a **secant
slope**, not a derivative, so if the response were materially non-linear in the cut, comparing secants across
cells would be comparing different things. I checked it three ways, from the producer's own primitives:

| | 305 | 306 | 307 | 308 | 309 | spread |
|---|---|---|---|---|---|---|
| at each cell's own admissible cut (published) | 0.149584 | 0.150387 | 0.152067 | 0.153555 | 0.153042 | 0.003971 |
| at a **common** cut of 6.0997 % | 0.149886 | 0.150686 | 0.152356 | 0.153692 | 0.153042 | 0.003806 |
| **marginal slope** (cut → 0) | 0.150501 | 0.151297 | 0.152965 | 0.154293 | 0.153622 | 0.003791 |

Maximum movement from the published column to the common-cut column is 0.000302; to the marginal slope,
0.000917. The cross-cell spread is 0.0038–0.0040 in every normalisation. The shape — essentially flat, rising
305→308, easing slightly at 309 — is identical in all three, and no ordering changes. **The window is not
driving the reading.** (My common-cut figures sit ~0.00001 below r4's because r4 used a round 6 % and I used the
exact 6.0997 % maximum admissible on cell 309; my marginal slopes match r4's to the last printed digit.)

So the per-unit column is the evidence for a *published finding* — that C_T is nearly exhausted rather than
weak, which is the correction r3 supplied and C2 adopted. Dropping it (r4's remedy (a)) would have removed the
support for a conclusion the diagnosis still states. Restricting it to the row where it is meaningful, and
shipping the limit inside the artifact, is the better of the three remedies r4 offered. I would not change it.

The residual imprecision is minor and I record it only for completeness: the `per_unit_comparability` string says
"same input across cells only" without adding that even within `C_T` the cells' windows differ, so the figure is
a secant. A reader is not misled — `effective_improvement` sits on the same row and prints the window, and §2
prints all five cuts explicitly — but a successor could sharpen the string. Not a defect.

## Note 2 (FAIL) — the README's review counts are wrong on two of the four rows, in the row r4 asked C2 to rebuild

`README.md:40–41`:

> \| independent pre-freeze review r1 \| … \| NOT_READY — 6 FAIL (**60 PASS / 10 INFO / 3 N/A**) \|
> \| independent pre-freeze review r2 \| … \| NOT_READY — 3 FAIL (**55 PASS / 5 NOTE / 3 INFO**) \|

I parsed the verdict column of every checklist row in all four review files.

| review | README says | actual | rows |
|---|---|---|---|
| r1 | 60 PASS / 10 INFO / **3 N/A** / 6 FAIL | 60 PASS / 10 INFO / **0 N/A** / 6 FAIL | 76 |
| r2 | **55 PASS / 5 NOTE / 3 INFO** / 3 FAIL | **62 PASS / 4 NOTE / 2 INFO** / 3 FAIL | 71 |
| r3 | 31 PASS / 7 NOTE / 1 FAIL | 31 PASS / 7 NOTE / 1 FAIL ✔ | 39 |
| r4 | 28 PASS / 5 NOTE / 3 FAIL | as r4's own header states ✔ | 36 |

- **r1 has no N/A rows at all.** The string "N/A" does not occur anywhere in `REVIEW_C2_PREFREEZE.md`, in any
  case, nor does "not applicable". Its 76 rows decompose as 60 PASS (52 bare + 4 "PASS (opinion)" + 2 "PASS
  (computed)" + 1 "PASS with scope" + 1 "PASS with note"), 10 INFO, 6 FAIL — and 60 + 10 + 6 = 76 exactly, so
  there is no room for three more. The three PASS/INFO figures are right; the fourth category is invented.
- **r2's three non-FAIL counts are all wrong** and do not sum to its row count: 55 + 5 + 3 + 3 = 66 against 71
  actual rows. The true decomposition is 62 PASS (51 bare + 5 "(opinion)" + 3 "with note" + 3 one-off PASS
  phrasings), 4 NOTE, 2 INFO, 3 FAIL = 71. r2 states no counts of its own anywhere, so unlike the r3 and r4 rows
  — which faithfully copy those reviews' own headers — these were computed by C2 and not checked.

**Why it is freeze-blocking rather than cosmetic.** r4's note 6 called `README.md` "the namespace's front door
and the first thing a cold adjudicator reads" and FAILed it specifically for misstating its own review history.
The repair got the load-bearing part right — all four reviews listed, all four FAIL counts correct, 13
reconciling against 13 disposition rows, and the two changed numbers named. Then it added a layer of detail r4
had not asked for, in the very act of fixing a defect about unverified counts, and got half of it wrong. An
adjudicator who does what I did — open the review files and count — finds the front door misdescribing the
review record on the round after that was the blocking finding.

**This is the named pattern again**, and its shape is exact: correct primary fix, unverified decoration.

**To repair:** either correct the two rows to the figures above, or — better, and in the spirit of the
operational lesson `ERRATUM_C2.md` itself draws — drop the PASS/NOTE/INFO parentheticals entirely and keep the
FAIL counts, which are what r4 actually blocked on and which are all correct. Text only; no artifact regenerates.

## Note 3 (FAIL) — §"The pattern, named" was rewritten but the superseded paragraphs were left underneath it, and one of them now contradicts the new table

`ERRATUM_C2.md:203–241`. The round-4 repair replaced the section's opening paragraph with a four-row table and
three new paragraphs, and `1663f558` added the fifth-instance paragraph. But the two r3-era paragraphs that the
new text supersedes were never removed. The section now ends with a near-verbatim duplicate:

| | line | text |
|---|---|---|
| new (`92c5d199`) | 223–227 | "**C2 did check**, at source, the two claims it inherited from r3 **rather than repeating the pattern there**… Both true, and r4 confirmed both to the digit. It also caught its own stale leaf-count before a reviewer had to. **That was not enough**: the same round still shipped an unrequested field whose effect it had not computed." |
| stale (r3-era) | 234–238 | "**C2 has now checked**, at source, the two claims it inherited from r3 **rather than repeating the pattern a fourth time**… Both are true. It also corrected its own restatement of r3's leaf-diff count before a reviewer had to." |

And again:

| | line | text |
|---|---|---|
| new | 229–232 | "The operational lesson for a successor… **when a review asks for one change, make that change and stop.**… Any sentence in this namespace beginning 'a further reason'… should be treated as unverified until checked." |
| stale | 240–241 | "A successor should expect this failure mode from this campaign's authorship specifically, and should treat any sentence beginning 'a further reason' as unverified until it is checked." |

Three things are wrong with leaving 234–241 standing, in increasing order of seriousness:

1. It is a duplicate, and it restates 0.932851 and the `atom_constants` / `atom_constants_r2` facts a second time
   within fifteen lines.
2. Its closing sentence — "It also corrected its own restatement of r3's leaf-diff count before a reviewer had
   to" — is the *uncorrected* version of the claim. r4's note 3 found that corrected restatement was itself
   wrong by three, and the new paragraph at 226 concedes it ("It also caught its own stale leaf-count before a
   reviewer had to. **That was not enough**"). The stale line reasserts the credit without the concession.
3. **It directly contradicts the table two paragraphs above it.** "C2 has now checked… **rather than repeating
   the pattern a fourth time**" says round three avoided a fourth instance. The table at 205–210 records round
   three producing instances **three and four** (r4 FAIL 1 and r4 FAIL 2), and the paragraph at 216–220 records a
   fifth. A cold adjudicator reading the section straight through is told, within twenty lines, both that the
   pattern reached four instances and that it did not.

**Why it is freeze-blocking rather than cosmetic.** This is not a stray sentence in an appendix. §"The pattern,
named" is the campaign's own assessment of its own reliability, it is the section `README.md` points the
adjudicator at, and it is the section whose entire subject is C2 failing to clean up after its own repairs. A
self-contradiction *inside* it is not a typographical matter; it is the document failing at the one thing it
exists to do. It is also, precisely, **instance six**, and of the sub-type r4 FAIL 2 already named: the prose was
rewritten and the older copy left asserting the withdrawn version.

**To repair:** delete lines 233–241. Everything in them is already said, better and with the correction attached,
at 223–232. Text only; no artifact regenerates. If C2 wishes to preserve the superseded wording it should be
marked superseded, as the source comment at `c2_d1_blocker.py:67–70` and the "in both places" correction at
`ERRATUM_C2.md:166–169` both correctly do.

## Note 4 (NOTE) — "no … magnitude … has changed at any point" is true as intended but collides with a key name

`README.md:74`. Three of the nine leaves that have ever changed are literally named `magnitude`:
`/cells/{307,308,309}/sensitivity_10pct_improvement/C_T/magnitude`. The intended referent is plainly the
cell-level `/cells/*/magnitude`, which has never moved — I verified that across every commit — and the sentence
immediately before discloses that the C_T sensitivity row changed. No adjudicator is misled for longer than it
takes to read the previous sentence. But a one-word fix ("no cell-level magnitude", or dropping `magnitude` and
leaving Γ, which carries the same information) removes the collision. Suggestion, not a defect.

## Note 5 (NOTE) — "three separate times" in the README against "five instances" in the erratum

`README.md:69` lists among the reviews' findings "— three separate times — an error introduced by a *repair* to
a previous round." `ERRATUM_C2.md` tabulates **four** reviewer-caught instances (rounds 1, 2, 3, 3) and a fifth
caught by self-audit. Three is defensible as a count of *rounds whose repair carried an error* as found by the
reviews, which is how I read it; but the README sentence is a list of things the reviews *found*, and they found
four. A reader who goes from the README to the erratum meets 3, then 4, then 5 in quick succession. Recommend
"in three separate rounds" or simply aligning on the erratum's count. Also note this review adds two more.

## Note 6 (NOTE) — the erratum quotes r4's stress-test spread slightly off, in r4's own words

`ERRATUM_C2.md:186` repeats r4's "window effects move each figure by < 0.0009 against a 0.0034 spread". My
independent recomputation gives a maximum movement of **0.000917** (published column to marginal slope, cell
305) and a cross-cell spread of **0.0038–0.0040** depending on normalisation. Both figures are r4's, not C2's,
and neither error favours the argument — the true ratio of movement to spread (0.24) is slightly *better* than
the quoted one (0.26). The conclusion "not a window artifact" is correct and I confirm it independently at row 4.
Recorded for accuracy only.

## Note 7 (NOTE) — the erratum has no section for r1's dispositions, only for r2, r3 and r4

`ERRATUM_C2.md` has explicit headed sections "Dispositions from the SECOND / THIRD / FOURTH pre-freeze review",
but r1's six FAILs are dispositioned across four differently-titled sections ("The one thing that cannot be
repaired at source", "Repaired at source", "Corrections arising from the INFO rows", "The finding that outranks
all of the above") with no header naming r1. The document is otherwise navigable and has not become a changelog
— the campaign's actual result still reads cleanly, and §"Cell 306" ends it on the open governance question
rather than on the repair history. But a cold adjudicator asked "where are r1's six dispositioned?" has to infer
it. A one-line heading or a pointer in the first section would fix it. Cosmetic.

## Note 8 (NOTE) — one qualification on the self-caught correction

`ERRATUM_C2.md:216–220` says flatly of r4's "wider margin" remark: "It does not." Strictly, r4's claim is false
as a statement about the **ratio** (which is what C2 checks, correctly) and true as a statement about the
**absolute difference** — dividing both rows by 1/11 multiplies the gap by 11, from 0.005505 to 0.060556 at cell
309. C2's corrected sentence is explicit that it means the ratio, so it is not itself wrong, and the ratio
reading is the right one in a section about orderings. I record this only because a successor re-checking the
erratum against r4 will notice r4's table is arithmetically exact and may wonder which of the two is in error.
Neither is, on its own terms.

## What I did not check

- I did not re-run the FLINT/Arb re-certification of cell 306. `C2_RECERTIFY_306.json` is unmodified since
  `55c4cf00`, reports `BOTH_PASSES_OK` over 18 artifacts with the registry sha pin satisfied, and r4
  independently re-certified two of its artifacts field by field on the venv build. I verified the file's
  contents and history, not its contents' provenance.
- I did not re-run `c2_refined_registry.py`, `c2_recertify_306.py` or `c2_b0_verify.py`. The registry's
  re-verifiability is evidenced by `C2_REGISTRY_VERIFY.json` (105/105, `problems: []`), which r2 and r3 exercised.
- I did not re-derive rounds one to four. Where I depend on a finding from an earlier review I re-derived it
  myself and say so in the reviewer-context list; everything else in those reviews I took on trust, as instructed.
- I did not re-verify C1's `REGISTRY_C1.json`, Campaign B's measurement records, the frozen cover, or
  `deflated_consume.py`'s source beyond what the C2 producers read. r4 read `deflated_consume.py:83–109` directly
  and I accepted that.
- I did not independently re-derive the `margin` column of the README `Result` table (1.353× … 0.579×); I checked
  Γ, the gap falls, the class, the closed subset and the materially-tightened flags against `C2_D5_FORECAST.json`
  and found them exact, and earlier rounds verified the margins.
- I did not touch AWS/PS1, any predecessor namespace, `main`, or any coverage map beyond hashing r4 and
  confirming no r5 exists.

## FINAL VERDICT: NOT_READY

**34 rows — 27 PASS, 5 NOTE, 2 FAIL.**

| | |
|---|---|
| **FAIL** — note 2 | `README.md:40–41`: the r1 and r2 review counts are wrong (r1 has zero N/A rows, not three; r2 is 62/4/2, not 55/5/3), in the row r4 FAIL 3 asked C2 to rebuild |
| **FAIL** — note 3 | `ERRATUM_C2.md:233–241`: the superseded r3-era paragraphs were left standing under the rewritten §"The pattern, named", duplicating it and asserting that round three avoided a fourth instance of the pattern, which the table twenty lines above contradicts |

**Both are text-only. No artifact regenerates, no sha changes, no number moves.** Deleting nine lines from the
erratum and correcting or dropping two parentheticals in the README discharges both.

**On the question this round was asked to answer: yes, it happened again, twice.** Round four's repair fixed all
three of r4's findings correctly on the substance — the field is restricted, the comment is accurate, the README
is no longer stale — and then stacked an unverified extra on two of the three: counts nobody asked for in the
README, and a rewrite that added new text without removing the text it replaced in the erratum. That is the
sixth and seventh instances, in the same shape the campaign has now characterised five times. The one round where
C2 did *not* do it is `1663f558`, which made exactly one correction and stopped — which is the lesson
`ERRATUM_C2.md:229–232` states, applied.

**What is not wrong, and should not be lost in a fifth NOT_READY.** Every published number reproduces
byte-for-byte from its producer. Nine leaves have changed in the entire history of the campaign's central
artifact and all nine are disclosed, dispositioned and located in a single row of a sensitivity table. No Γ, no
cell magnitude, no requirement, no gap fall, no class, no adopted subset has ever moved. The gate is frozen at
one commit and its sha still matches. The mutation suite is clean at 43 with nothing undetected. Nothing outside
the namespace is touched, `main` is untouched, coverage map r4 is intact and no r5 exists. Nothing pre-empts
freeze, qualification, sealing or adjudication, and the R stage is correctly and self-critically blocked. The
substantive finding I attacked hardest — that C_T is nearly exhausted rather than weak at the far tail —
survived a common-cut recomputation and a marginal-slope recomputation I wrote from scratch. **The science is
sound and the two blocking defects are bookkeeping about the campaign's own review history.**

---

*Fifth independent pre-freeze review, 2026-09-21, HEAD `1663f558`. Read-only; this file is the only file written.*
