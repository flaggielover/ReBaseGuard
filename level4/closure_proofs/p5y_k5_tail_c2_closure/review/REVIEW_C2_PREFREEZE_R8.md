# Eighth independent pre-freeze review — Campaign C2 (`p5y_k5_tail_c2_closure`), branch `p5y-k5-tail-c2` @ `07c0b991`

**VERDICT: NOT_READY** — 38 checklist rows, 32 PASS, 6 rows carrying **3 distinct FAILs**, plus 8 NOTEs. All three
FAILs are text only; none touches a computed number, and the science is unaffected and independently reproduced
again in this round. r7 FAIL 2 is *substantially*
repaired and honestly dispositioned. r7 FAIL 1 is **not** repaired: one of the exact deletions r7 asked for was not
made, and the repair created two new self-contradictions of the same kind in the same section.

## Reviewer context — what I re-derived, and what I did not

I am a fresh-context reviewer with no part in writing this campaign. I read `git diff 5a098ec6..07c0b991` line by
line and treated every new or changed sentence as unverified until checked. I re-derived from the committed evidence,
on this machine, with stdlib Python 3 and `PYTHONINTMAXSTRDIGITS=0`: all three named producers, byte-for-byte
(`c2_d1_blocker.py` → `C2_D1_BLOCKER.json` identical; `c2_mutations.py` → `C2_MUTATIONS.json` identical, 43 applied
/ 35 real / 8 static / 40 detected / 3 proven-equivalent / **0 undetected** / `pass: true`; `c2_critical_ratio.py` →
`C2_CRITICAL_RATIOS.json` identical, both published anchors reproducing and the module refusing otherwise); the
decision quantities straight out of `C2_D5_FORECAST.json` (`D_STAGE_CLASS = D_PARTIAL`, `closed [305, 306]`,
`still_open [307, 308, 309]`, gap falls 0.46285183 / 0.24593099 / 0.18389841, Γ(305) = −0.08802906884,
Γ(306) = −0.03046925771, both negative, 307–309 positive); the frozen gate's sha256 by `shasum` and the fact that
the gate blob exists at exactly one commit in this branch's history (`87309610`, blob `fc1374ed`, never re-written);
the whole-history leaf diff of `C2_D1_BLOCKER.json` across the four commits that have touched it, myself, leaf by
leaf; `REGISTRY_C2.json`'s complete key set (50 distinct paths — no host, platform, toolchain, python, flint, numpy
or precision field anywhere); the build-host `cpu_seconds` in `taboo_block_306_02` (90.248) and
`taboo_block_305_00` (88.257); r1's and r2's own verdict tables and, independently, r2's 71 checklist rows by
verdict (62 PASS-family / 4 NOTE / 2 INFO / 3 FAIL — confirming the rescoped recount at `ERRATUM_C2.md:250–252`);
r7's verdict counts and every factual claim the new r7 disposition paragraph makes about r7's work; and the
integrity set (all-additive and wholly in-namespace since `5289b6ce`, `main` at `c123b9bb` and the merge-base with
it unchanged, coverage map r4 sha `a3bddd83234f…` intact with no r5 map anywhere, `c2_d5_forecast.py` and
`C2_D5_FORECAST.json` last touched at `5a94568a`, every prior review file r1–r7 committed at one commit each and
unedited since).

I **did not** run the FLINT stack: no re-certification, no 384-bit pass, no registry verification. Rounds 2, 4, 6
and 7 did that and I rely on their reports for it. I did not run `c2_d5_forecast.py` end-to-end (it needs the K1
record store, absent here). I did not touch AWS, any remote host, or any file in this repository — this review file
is the only thing I wrote, and I ran no writing git command.

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| **A. The diff is what it claims to be** |
| 1 | `5a098ec6..07c0b991` is documentation-only | **PASS** | five files: four `.md` edits plus the r7 review added. `git diff --name-status … -- code evidence` returns **nothing** |
| 2 | no `code/` or `evidence/` file changed | **PASS** | as row 1; every producer and artifact byte-identical to `5a098ec6` |
| 3 | additive and in-namespace since `5289b6ce` | **PASS** | `git diff --name-status 5289b6ce..07c0b991` is all `A`; nothing outside `level4/closure_proofs/p5y_k5_tail_c2_closure/` |
| 4 | `main` untouched | **PASS** | `main` = `c123b9bb`, merge-base with HEAD = `c123b9bb`; the branch is strictly ahead |
| 5 | nothing pre-empts freeze, qualification, seal, adoption or adjudication | **PASS** | no freeze/seal/qualification/countersignature/authorization artifact; `R_STAGE_DESIGN.md:1` "DESIGN ONLY; nothing is executed"; `CELL_306_ADOPTION.md:10` "It is not *adopted* yet"; guard DENY, `NEW_REAL_ADDRESSES = 0`. The diff adds none of these |
| 6 | every prior review file committed, one commit each, unedited | **PASS** | r1 `12585997`, r2 `55c4cf00`, r3 `d6a4def5`, r4 `92c5d199`, r5 `fb4d688b`, r6 `5a098ec6`, r7 `07c0b991` — one commit apiece, no later commit touches any of them |
| **B. The science** |
| 7 | `c2_d1_blocker.py` reproduces its artifact byte-for-byte | **PASS** | `cmp` identical; sha256 `1d7715a2…` |
| 8 | `c2_mutations.py` reproduces, 43 applied, 0 undetected | **PASS** | `cmp` identical; sha256 `512180f3…`; 35 real + 8 static, 40 detected, 3 proven-equivalent (`M19`, `M20`, `M32`), `pass: true` |
| 9 | `c2_critical_ratio.py` reproduces, both anchors hold | **PASS** | `cmp` identical; the module refuses unless Campaign B's Lemma-G column and C2's own published `critical_sG_over_sH` / `Gamma` / `Gamma_perfect_order3` reproduce bit-exactly, and both do |
| 10 | class, closed and open subsets | **PASS** | `D_PARTIAL`; `closed [305, 306]`; `still_open [307, 308, 309]` |
| 11 | gap falls 0.462852 / 0.245931 / 0.183898 | **PASS** | 0.46285183476, 0.24593099375, 0.18389841085 from `gap_fall_fraction` |
| 12 | Γ(305) = −0.088029069, Γ(306) = −0.030469258 | **PASS** | −0.08802906884054082 and −0.030469257709306738; 307/308/309 all > 0 |
| 13 | gate sha `098dd7f5…` at exactly one commit, never modified | **PASS** | `config/FEASIBILITY_GATES_C2.json` appears in one commit only (`87309610`), one blob; `shasum -a 256` = `098dd7f5c3cf…db28f` |
| 14 | the "result has never moved" invariant | **PASS** | my own whole-history leaf diff of `C2_D1_BLOCKER.json` (487 → 490 → 540 → 525 leaves over `e71378a0`, `55c4cf00`, `d6a4def5`, `92c5d199`): exactly **nine** leaves ever had a value replaced, all `sensitivity_10pct_improvement/C_T/{delta_vs_base, magnitude, relative_gain}` on cells 307/308/309. No cell Γ, magnitude, requirement, margin, gap fall, class or adopted subset ever changed. See Note 3 on the wording |
| 15 | `c2_d5_forecast.py` / `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS** | last touching commit is `5a94568a` for both |
| 16 | coverage map r4 intact, no r5 | **PASS** | `K5_COVERAGE_MAP_R4.json` sha `a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35`, last touched `f2ac1eb3`; no `*COVERAGE_MAP_R5*` anywhere |
| **C. r7 FAIL 1 — the de-counting repair** |
| 17 | both self-referential "no sentence states a count" assertions deleted | **PASS** | `:4–5` and the old `:278–279` are gone; `git diff` confirms deletion, not restatement |
| 18 | r7's four rescope/deletion targets 1–4 actioned | **PASS** | `:18` "In every round so far"; `:366` "In every round"; `:306` "several of the instances below"; `:250–252` recount rescoped to r1's and r2's own self-reports |
| 19 | the rescoped recount is arithmetically true | **PASS** | verified independently: r1's verdict table 60/10/3/6 against 79 rows reconciles; r2's header 55/5/3 + 3 FAIL = 66 ≠ its stated 71; r2's true breakdown, which I recounted row by row from its 71 checklist rows, is **62 PASS-family / 4 NOTE / 2 INFO** (+ 3 FAIL) |
| 20 | r7's target 5 actioned — "four independent implementations" | **FAIL** | **`ERRATUM_C2.md:369` still reads "reproducing bit-exactly under four independent implementations".** Untouched by `07c0b991`. See FAIL 1 |
| 21 | the "two tables" enumeration corrected | **FAIL** | **`:274` now reads "the two tables — [three tables] — carry the counts".** See FAIL 1 |
| 22 | `README.md:71`'s "only place that counts them" corrected | **PASS** | rewritten to "they are listed in the table above, and `ERRATUM_C2.md` carries the same list with each round's disposition" — true of both files |
| 23 | the replacement compliance claims are true | **FAIL** | `:5` "Counts belong in the tables … not in prose", `:274` "prose does not", `:306` "counts are kept to tables", `:305` "the table below is the campaign's **only** tally of them" — all four falsified within the same file. See FAIL 1 |
| 24 | the r7 FAIL 1 disposition row characterises r7 accurately | **FAIL** | `:294` says r7 found "**four** prose counts"; r7 enumerated **five** (`:200–221`, items 1–5), and item 5 is the one left unrepaired. See FAIL 1 |
| 25 | the r7 disposition paragraph's claims about r7's work | **PASS** | every one checked against the r7 file: "41 rows, 33 PASS, 6 NOTE, 2 FAIL" (r7:3 and r7's verdict table; 33+6+2 = 41 = its 41 numbered rows); gap falls (r7:21); `classify()` faithful (r7 row 30); five artifacts across 305/306/309, bit-identical at 256 and safe-side-valid at 384 (r7 row 34, r7:400–402); mixed supply 57.27 / 30.57 / 23.03 % (r7's answer H); 384-bit separation from git history (r7 rows 38–39); leaf diff across all four commits (r7:37, :351) |
| 26 | `phase_d/` and `phase_r/` carry no round-sensitive count | **PASS** | swept all six documents: every numeral is a result (five cells, 18 artifacts, 45/45, 105/5, 9/9/10/11/11 sub-blocks, 7/7, 2.69 CPU-h, three still-open cells) or a fixed reference to a named review note. None can go stale as rounds accrue |
| 27 | no round-sensitive count in code comments, docstrings or committed JSON | **PASS** *(for counts)* | swept `code/*.py` and every committed artifact: the only maintained tally is `OPEN_NOTES_DISPOSITION_C2.md:25` "35 real mutants and 8 static assertions", which matches `C2_MUTATIONS.json` exactly as I re-ran it. Provenance strings are a separate matter — row 34 |
| **D. r7 FAIL 2 — the build-host provenance** |
| 28 | `REGISTRY_C2.json` has no host / toolchain / precision field | **PASS** | verified directly: 50 distinct key paths; `host`, `platform`, `arch`, `machine`, `toolchain`, `python`, `flint`, `numpy`, `precision`, `os`, `uname` all absent as substrings of the serialised document. No per-artifact registry file carries one either |
| 29 | the comparison table is relabelled reported-vs-recorded | **PASS** | `CELL_306_ADOPTION.md:32–37`: left column "the worker that built the registry — **reported, not recorded**", right column "the host that re-certified — **recorded**", with `:39–46` stating the asymmetry, its consequence, and that r2 asked for it and C2 did not act for five rounds |
| 30 | the bolded cross-boundary claim is rescoped | **PASS** | `:69–76` now asserts reproduction *on a fully recorded host*, names the withdrawn "across the OS, architecture and FLINT build boundary" phrasing explicitly, and states the two things it falls short of (a second implementation, a recorded second host) |
| 31 | `ERRATUM_C2.md`'s "is answered by the two artifacts that do" corrected | **PASS** | `:102–106` now says the complaint is **not** thereby answered and that an earlier version wrongly said it was |
| 32 | the **N10** chain is complete and not dangling | **PASS** | defined once (`OPEN_NOTES_DISPOSITION_C2.md:82–90`), referenced from `ERRATUM_C2.md:105` and `CELL_306_ADOPTION.md:52` and `:76`. N9 rewritten in the same commit to drop "genuinely independent host and toolchain build" — which r7 flagged as the third restatement |
| 33 | r2's note 4 is honestly dispositioned, including the five-round lapse | **PASS** | stated four times, in bold where it matters: `ERRATUM_C2.md:295`, `:297–301`, the second register at `:329–331`, `CELL_306_ADOPTION.md:40–42`, `OPEN_NOTES:87`. I checked r2's note 4 (r2:226–238) and its summary line (r2:435) — the request was exactly "the table's left column should be marked as reported rather than recorded", and it is now marked |
| 34 | no document restates the unscoped second-host claim | **FAIL** | **`ERRATUM_C2.md:384` still says "the independent re-certification is now delivered on a genuinely second host"** — the phrase r2's note 4 named and r7 FAIL 2 blocked on, now contradicted by `CELL_306_ADOPTION.md:44`. See FAIL 2 |
| 35 | the campaign did not manufacture build-host provenance | **FAIL** | it manufactured none in this round — but the committed evidence already asserts the boundary, undisclosed: `C2_RECERTIFY_306.json` → `host.note` = "second host: a different OS, CPU architecture and compiled Arb/FLINT build than the registry", written from the hardcoded string at `code/c2_recertify_306.py:98` and echoed in its docstring at `:1` and `:11–13`. `CELL_306_ADOPTION.md:45` says the opposite ("rests on C2's report, **not on an artifact**"). See FAIL 3 |
| 36 | the in-repo corroboration cited is accurate | **PASS** *(with Note 1)* | verified: `taboo_block_306_02.cpu_seconds` = 90.248 → "90.2"; `taboo_block_305_00.cpu_seconds` = 88.257 → "88.3"; 56.2 s and 66.1 s are r2's own figures for the same two blocks (r2 row 30, r2:235–236), correctly paired. The host attribution is Note 1 |
| **E. Freeze readiness in the round** |
| 37 | the namespace reads coherently as a set | **PASS** *(with the FAILs)* | `README.md` → `ERRATUM_C2.md` → `phase_d/` → `phase_r/` → `OPEN_NOTES_DISPOSITION_C2.md` tell one story; cross-references resolve; N6–N10 map onto the five open governance questions; the R-stage document opens by arguing against its own recommendation; the erratum still tells a reader what not to trust. The three defects below are the exceptions, and all three are in the two documents whose job is to be trustworthy about the campaign's own record |
| 38 | the decision an adjudicator must make is presented against C2's interest | **PASS** | 306's margin 1.112× against 305's 1.353×, and Γ under ×1.25 degradation +0.029163 — "does *not* survive" — in the table; `D_USEFUL` recorded as failed by 1.6 points; N7 (the cheaper deterministic route C2 did not pre-register) blocks the R stage the campaign itself wants; the margin floor referred out with both branches pre-committed. Unchanged by this diff and still the strongest thing in the namespace |

## Notes

**Note 1 (NOTE) — the timing corroboration is attributed to the wrong host, and the artifact's own figure would
have carried it.** `CELL_306_ADOPTION.md:47–51` says the 56.2 s / 66.1 s comparison figures were measured "on the
re-certifying host". r2, which is where they come from, says "on **this** host" (r2:235) — r2's reviewing machine.
Nothing records that r2's machine and the machine in `C2_RECERTIFY_306.json`'s `host` block are the same, and r7's
own re-runs of the same blocks gave different numbers again (62.2 s for `taboo_block_305_00`, r7:277–279), which is
what one expects of per-review measurements. The inference itself survives, and from C2's own artifact rather than a
reviewer's: `C2_RECERTIFY_306.json` records `determinism_256.cpu_seconds` = 1153.9 for 18 artifacts, i.e. ≈ 64.1 s
per artifact on the recorded host, against 88–90 s for those blocks in the registry. That figure is in the
artifact, is not cited, and would make the corroboration self-contained. As it stands the sentence credits r2
correctly for the finding and then relabels r2's host as C2's, which is the smallest possible instance of the thing
§"The pattern, named" is about — one unverified word on top of a correct fix. Non-blocking.

**Note 2 (NOTE) — "five rounds" against r7's "four rounds later", unreconciled.** C2 says the note "sat
undispositioned for five rounds" (`ERRATUM_C2.md:295`, `:299`, `:331`, `OPEN_NOTES:87`, `CELL_306_ADOPTION.md:41`);
r7 says "Four rounds later the column is unmarked" (r7:288). Both are defensible — five reviews ran after r2
counting r7, four repair rounds elapsed before it — and C2 is internally consistent. But it is a hand-maintained
count of the campaign's own history that differs from the review it dispositions, with no clause reconciling them,
which is precisely the shape of r7's FAIL 1 item 4. One clause would settle it.

**Note 3 (NOTE) — "nine leaves have ever changed" is looser than "nine leaves have ever had a value replaced".**
`ERRATUM_C2.md:23–24` and `:288–290` use the former; `:264` uses the latter, which is the accurate one. My own
whole-history leaf diff: nine leaves had a value **replaced** (all `C_T` sensitivity on 307–309), and a further 58
leaf paths were **added or removed** across the r3 and r4 repairs (`effective_improvement`,
`gain_per_unit_of_input_moved`, `per_unit_comparability`, `admissibility_clamp`) — 487 → 490 → 540 → 525. Nothing
misleading follows, because those field additions and removals are disclosed at length elsewhere in the same
document, and the invariant the sentence exists to support is true. But one of the nine replaced leaves is literally
named `magnitude`, and the headline sentence at `:18` says "no … magnitude … has changed"; a reader who checks will
need the qualifier "no *cell* magnitude". Use the `:264` wording in all three places.

**Note 4 (NOTE) — `ERRATUM_C2.md:378` "Sixth instance; r5 FAIL 1".** The r5 FAIL 1 row is the **fifth** row of the
instance table, and was the fifth of seven when this parenthetical was written at `fb4d688b`. A fixed historical
ordinal, so it cannot go stale with further rounds, and no decision depends on it — but it is an off-by-one count in
prose in the section about off-by-one counts in prose, and three rounds have passed over it. Delete the ordinal.

**Note 5 (NOTE) — N10 rests on one premise a reviewer cannot check.** "the worker's build log records only the
registry summary" (`OPEN_NOTES:83–84`) is a negative claim about a log on `rebaseguard-vultr-02` that is not
committed and that no reviewer may fetch. It is very likely true and it is used honestly — to *narrow* C2's claim
rather than widen it — so it is not a FAIL. But N10's force is "recorded nowhere", and the part of that assertion
covering the worker's own log is itself a campaign report. Say so in the note.

**Note 6 (NOTE) — the heading over N6–N10 is still singular.** `OPEN_NOTES_DISPOSITION_C2.md:64` reads "Notes
opened by the C2 pre-freeze review"; seven reviews have now contributed to that list, and r4 flagged the singular at
its `:239`. Cosmetic; recorded because it is the one place where the note numbering's provenance is stated.

**Note 7 (NOTE) — r7's Notes 1, 5 and 6 were correctly not actioned, and are worth carrying.** r7 asked for none of
them as conditions, and the campaign's own lesson is "make the change and stop", so leaving them was right. For the
adjudicator: `C2_B0_VERIFICATION.json` records the HEAD it ran at, so a reviewer running `cmp` on it sees a
mismatch that is correct behaviour (r7 Note 1); `D1_BLOCKER_DIAGNOSIS.md` never states that all its figures are
under **C1's** constants, which matters because r1 FAIL 61/62 were exactly a column labelled with the wrong
campaign (r7 Note 5 — I confirmed `c2_d1_blocker.py` reads `registry_c1/REGISTRY_C1.json` and the evidence carries
`closes_under_C1_constants`); and `c2_recertify_306.compare()` iterates the recomputed dict, so a consumed field
that stopped being emitted would never be compared (r7 Note 6). All three belong in a successor's inbox.

**Note 8 (NOTE, and my answer on the meta-claim question) — deleting the self-referential assertions was the right
call; replacing them with softer compliance claims was not.** r7 was right that "no sentence in this namespace
states a count" is an unmaintainable universal claim about every sentence, and deleting both instances was correct.
But the replacement text is the same claim in normative clothing: "Counts belong in the tables … **not in prose**"
(`:5`), "prose does **not**" (`:274`), "counts **are kept** to tables" (`:306`), "the table below is the campaign's
**only** tally of them" (`:305`). Each is still falsifiable by any sentence in the namespace, and all four are
falsified inside the same file. So the repair removed the sharpest edge of its own detector without removing the
defect — the worst of the two available outcomes. The honest form is a rule addressed to the successor with no claim
about the present state ("counts of this campaign's review history belong in the tables; a successor should not
reintroduce them in prose"), or, better, no meta-sentence at all: the tables speak for themselves, and every
sentence the campaign has written *about* its counts has needed a later repair.

## FAIL 1 — r7 FAIL 1 is not repaired: one of its five named counts survives, and the repair created two more

r7's FAIL 1 enumerated **five** surviving prose counts (its items 1–5) and asked for each to be deleted or
rescoped, plus a correction to the "two tables" sentence and to `README.md:71`. Four of the five were done, cleanly,
and `README.md` is clean (row 22, and r7 row 21 had already found no count there). What is wrong:

**(a) r7's item 5 was not actioned at all.** `ERRATUM_C2.md:369` still reads "reproducing bit-exactly under **four**
independent implementations". `git diff 5a098ec6..07c0b991 -- ERRATUM_C2.md` does not touch the line. r7 said of it:
"Another prose count, now an undercount: six rounds have reproduced the result", and listed it in its minimal-change
instruction — *"Delete the count from each of `:16`, `:280`, `:331` and `:335`"*, where `:335` is this line. It is
now an undercount by more: with this round, at least seven independent implementations have reproduced the D-stage
result, and I reproduced all three named producers byte-for-byte myself. It sits in §"The pattern, named", nine
lines below the sentence claiming counts are kept to tables.

**(b) The reason (a) happened is a miscount in the disposition itself.** `:294` describes r7 as having found "**four**
prose counts in `ERRATUM_C2.md`" and enumerates four — "Across all five rounds" twice, "three separate instances
below", and the four-review recount tally. r7 enumerated five. The row undercounts the review it is dispositioning
by exactly the item that was then left unrepaired. An adjudicator reading `ERRATUM_C2.md` alone would conclude the
de-counting was complete; reading r7 alongside it, they would find it 4-of-5.

**(c) "The two tables" now enumerates three tables.** `:274–276`:

> "So every hand-maintained tally has been deleted from prose in both `README.md` and this section, and **the two
> tables** — the review list at the top of the README, the round table at the top of this document, and the
> instance table below — carry the counts, and prose does not."

r7 FAIL 1's closing sentence was precisely *"The claim that two tables are the only places a count appears was also
false: this document's own round table is a third"*, and its minimal change was *"correct `:268–269` … so that each
describes the tables that actually exist"*. The repair added the third item to the list and left the word "two". The
sentence is now self-refuting on its face, in the paragraph that is the disposition of r6 FAIL 1 and immediately
above the disposition of r7 FAIL 1 — both of which were blocked on exactly this.

**(d) Two further count sentences were left stale by this same commit.** `:272–273`: "**Three** of the instances in
the table below are a count left stale by a later edit; this was **the fourth**." The same commit added a fifth such
row to that table — row `| 6 | deleted every hand-maintained count from prose | cleaned README.md, left four counts
in this document, and asserted twice that none remained | r7 FAIL 1 |`, which is by the campaign's own
characterisation counts left in place by an edit that should have removed them. And `:305`: "The table below is the
campaign's **only** tally of them" — the same commit added a **second** tally table nineteen lines below it, under
the heading "A separate register, for a different failure". Neither sentence was carried along.

**Why this blocks rather than being a NOTE.** It is not prose quality, and it is not a count I would have phrased
differently. It is (i) a specific, enumerated repair a prior independent review required, not made; (ii) a
disposition row that miscounts that review's finding, in the document whose entire purpose is an accurate account of
what every review found; and (iii) three completeness claims — "prose does not", "counts are kept to tables", "the
only tally" — that the same commit falsified. r6 blocked on a wrong count of the campaign's review history in the
front-door document and C2 accepted that framing (`:278–280`, "a claim about the campaign's reliability, in the
document an adjudicator reads first"); r7 blocked on the same defect in the second front-door document and C2
accepted it again (`:294`, the FAIL 1 row). The defect class is not ended. On the brief's question: deleting
the meta-claims was right, but what replaced them is still a compliance assertion, and it is still false — so what
was removed was the detector's sharpest edge, not the defect. See Note 8.

**Minimal change required.** Four word-level edits, no computation: delete "four" at `:369` (e.g. "under every
independent implementation that has reproduced it"); change "the two tables" at `:274` to "the three tables", or drop
the count and the trailing "and prose does not"; replace "Three of the instances … this was the fourth" at `:272–273`
with an uncounted form ("several of the instances below … this was another"); and at `:305` say "the campaign's tally
of them" rather than "only tally", since a second register now exists. Correcting `:294` to say five is optional
once `:369` is fixed, but it is one word.

## FAIL 2 — the unscoped "genuinely second host" claim survives in `ERRATUM_C2.md`, contradicting the repaired document

`ERRATUM_C2.md:382–386`, §"Cell 306" — the section the erratum's own navigation at `:32` calls the place where
"the open governance question the campaign ends on" is stated:

> "In short: the finer partition was delivered and worked (margin 1.9 % → 11.2 %); **the independent
> re-certification is now delivered on a genuinely second host**; and the margin floor **cannot honestly be set by
> C2** …"

The repaired `phase_d/CELL_306_ADOPTION.md:43–46` says the opposite, in the same commit:

> "So what the evidence establishes on its own is narrower than **"a genuinely second host"**: the re-certification
> host is fully recorded, and the artifacts it re-certified reproduce on it bit-identically. That the *build* host
> differed rests on C2's report, not on an artifact."

This is the fourth restatement of the claim, and the one document that still asserts it unqualified. r2's note 4
named the phrase directly — *"the sentence 'a genuinely second host' rests on the unsourced half"* (r2:231–232) —
and r7 FAIL 2 blocked on it and swept for restatements, catching N9 (which the repair fixed) but not this one. It is
not a stylistic residue: condition 2 of cell 306's adoption, set by C1's reviewer, was "an independent
re-certification … or at minimum a second execution on a second host". An adjudicator who reads §"Cell 306" —
plausibly the *only* section they read on this question, since it is the erratum's stated summary of it — is told
condition 2 is delivered on a genuinely second host. The document that decides the adoption says it is not. Nothing
in the namespace reconciles them.

Two lesser instances of the same framing, which I would not fail on their own but which should move with it:
`:97` "on the independent host" and `:102` "on the same independent macOS/arm64 host". "Independent" is doing the
work that N10 says is unestablished — independence *of the build host* is the unrecorded half. Both are
one-adjective fixes.

**Minimal change required.** Rewrite `:384` to what the artifacts establish, e.g. "the re-certification is now
delivered, bit-identically at 256 bits and safe-side at 384, on a host whose OS, architecture, Python and Arb/FLINT
build are recorded in the artifact — short of a recorded *second* host (N10)". One sentence. Optionally drop
"independent" at `:97` and `:102`.

## FAIL 3 — the committed evidence asserts the boundary that N10 says is recorded nowhere, and nothing discloses it

`evidence/prefreeze/C2_RECERTIFY_306.json` carries, inside its `host` object and beside the five genuinely recorded
fields (`platform`, `machine`, `python`, `numpy`, `python_flint`):

> `"note": "second host: a different OS, CPU architecture and compiled Arb/FLINT build than the registry"`

It is written from a hardcoded string at `code/c2_recertify_306.py:98`, and the module's docstring states the same
thing twice more (`:1` "on a second host at higher precision"; `:11–13` "Run here on a different operating system, a
different CPU architecture, a different Python and a DIFFERENT COMPILED BUILD of the Arb/FLINT stack than produced
the registry"). This is a comparative claim about the **build** host, asserted in the artifact that is cited as the
evidence, and it is unattested for exactly the reason N10 gives.

The repair states the opposite twice:

- `CELL_306_ADOPTION.md:45` — "That the *build* host differed rests on C2's report, **not on an artifact**."
- `OPEN_NOTES:82–85` — "the *build* host is reported by this campaign and **recorded nowhere**. Both verification
  artifacts record the host that *re-certified*, which is a different claim."

The second is defensible about the build host's *identity* — no platform string, no versions — and it is the reading
r2 took. The first is not: the assertion that the build host differed **is** in an artifact, in the field an
adjudicator would look at, generated by the campaign's own producer. And no document in the namespace discloses
that it is there.

**Why this blocks.** The whole point of the r7 FAIL 2 repair is to draw the recorded/reported line precisely on the
question that decides an adoption condition. An adjudicator who follows the citation from `CELL_306_ADOPTION.md` to
`C2_RECERTIFY_306.json` finds the artifact declaring, in its `host` block, that a second OS, a second architecture
and a second compiled FLINT build were involved — and is left to resolve an undisclosed contradiction with the prose
in either of two wrong directions: conclude that the evidence is stronger than the document admits and grant
condition 2, or conclude that the artifact overstates and distrust the determinism and safe-side results, which are
sound. The campaign did **not** manufacture any new build-host provenance in this round — I checked every added line
— but the sweep it ran to close the defect class covered prose and stopped at the namespace's own evidence.

This is repairable with no change to any artifact, and it must be: the artifact and the producer are the evidence
and should not be rewritten after the fact.

**Minimal change required.** One clause in N10 and one in `CELL_306_ADOPTION.md`, disclosing that
`C2_RECERTIFY_306.json.host.note` and `c2_recertify_306.py`'s docstring both assert the boundary, that this
assertion is the campaign's own report written into the artifact by its producer rather than anything measured about
the build host, and that it is not edited post-hoc for that reason. Replace "not on an artifact" at
`CELL_306_ADOPTION.md:45` with "rests on C2's report — including the `host.note` string its own producer writes into
`C2_RECERTIFY_306.json` — and not on anything measured about the build host".

## What I did not check

- **Anything requiring FLINT.** No re-certification at 256 or 384 bits, no `C2_RECERTIFY_306.json` re-run, no
  105-artifact registry verification. Rounds 2, 4, 6 and 7 ran these; r7 spot-checked five artifacts across three
  cells at both precisions and r6 ran the full registry verification. I relied on their reports and re-read the
  artifacts, not the stack.
- **`c2_d5_forecast.py` end-to-end.** It needs the adopted K1 record store, absent from this repository. I read the
  committed `C2_D5_FORECAST.json` and took `classify()`'s faithfulness to the frozen gate from r6 and r7, both of
  which read it line by line against the gate.
- **`c2_b0_verify.py`, `c2_refined_registry.py` and `c2_recertify_306.py` as executed producers.** I read them; I
  re-ran only the three named in my brief.
- **The mathematics of theorem TC-T and Lemma Dv′ from the source theorem documents.** I verified that the committed
  producers reproduce their committed artifacts and that the D-stage classification is mechanical under the frozen
  gate; I did not re-derive the theorems. Rounds 1 and 7 did that from independent implementations.
- **Predecessor namespaces beyond the two integrity facts in rows 4 and 16.** I did not audit Campaign B, C1, the
  lower-front campaign or the AD campaign. I touched no AWS tool and contacted no remote host.
- **The seven prior reviews' own arithmetic**, except where the diff relies on it: I independently verified r1's and
  r2's verdict tables and recounted r2's 71 rows by verdict (row 19), and I verified every claim the new r7
  disposition paragraph makes about r7 (row 25). I did not recount r3, r4, r5 or r6.
- **Whether the review host and the re-certification host are the same machine** (Note 1). Not determinable from the
  repository, which is the point of the note.

## Verdict counts

Checklist rows, by verdict:

| verdict | count |
|---|---|
| PASS | 32 |
| **FAIL** | **6** |
| **total** | **38** |

Those six rows carry **3 distinct FAILs**: rows 20, 21, 23 and 24 are FAIL 1; row 34 is FAIL 2; row 35 is FAIL 3.
Separately, **8 NOTEs** are recorded above, none of them blocking. No row was marked INFO or
NOT_CHECKABLE_LOCALLY; what I could not check is listed in §"What I did not check" instead.

## Closing assessment

**Is the calibration in my brief right?** Yes, and I applied it. Eight rounds have produced no arithmetic error and
the D-stage result has been reproduced bit-exactly by every implementation that has looked at it, mine included. I
have written eight NOTEs I am not blocking on, including two off-by-one counts (Notes 2 and 4) and a wording
imprecision in the campaign's headline invariant (Note 3), because none of them could change an adjudicator's
decision. I did not withhold a verdict to avoid appearing lenient: had r7's five deletions been made and `:384`
carried along, this would be `READY_TO_FREEZE_WITH_NOTES` today.

**Did the repair introduce a new defect?** Yes — two, both created by this commit and both of the documented type
"a neighbouring sentence the fix failed to carry along": `:274`'s "the two tables" now enumerating three tables, and
`:305`'s "the campaign's only tally" left standing while the same commit added a second register below it. The
second register and **N10** were not requested by r7, and neither is *wrong* — N10 is a genuine improvement and the
second register is a defensible refusal to file a distinct failure under the wrong heading — but adding structure
around a text repair is what has gone wrong in this campaign seven times, and it went wrong again here in the two
sentences the new structure orphaned.

**Is the namespace fit to freeze?** Not yet, and the gap is small and entirely textual. The science is settled: the
producers reproduce byte-for-byte, the class is `D_PARTIAL` with closed = {305, 306}, the gate is byte-untouched at
one commit, the adversarial suite is 43/43 with nothing undetected, and the campaign's hardest finding — N7, the
cheaper deterministic route it did not pre-register, which blocks the R stage it wanted — is stated against its own
interest and is the most valuable thing here. The governance posture is correct: guard DENY, zero new real
addresses, nothing pre-empted, the 306 margin floor referred out with both branches pre-committed. What is not yet
fit is the account the campaign gives of its own record: after eight rounds, `ERRATUM_C2.md` still tells an
adjudicator that the de-counting is complete when four of its own sentences say otherwise, and still tells them in
§"Cell 306" that the second-host condition is delivered when the document that decides it says it is not. The
sentence-level edits named under the three FAILs above — four in §"The pattern, named" and the r6 disposition, one
in §"Cell 306", and two disclosure clauses for the artifact note — involve no computation and no change to any
artifact, and with them made I would expect this to freeze.
