# Ninth independent pre-freeze review — Campaign C2, D-stage successor

**VERDICT: NOT_READY**

*Ninth independent fresh-context pre-freeze review, 2026-09-21, worktree `/Users/suzhe/ReBaseGuard-k5c2`, branch
`p5y-k5-tail-c2`, HEAD `5609358f`. Read-only: this file is the only file I wrote, and I ran no writing git command.
AWS was not touched.*

---

## Reviewer context — what I re-derived, and what I took on trust

I wrote none of this work and read it cold, starting from `git diff 07c0b991..5609358f` as instructed and then
widening. Everything below that I call verified, I verified myself on this machine (macOS 26.5.2, arm64,
CPython 3.14.5, `PYTHONINTMAXSTRDIGITS=0`, stdlib only).

**Re-derived independently.** All three producers re-run and compared with `cmp` against their committed artifacts:
`code/c2_d1_blocker.py` → `evidence/phase_d1/C2_D1_BLOCKER.json` **byte-identical**; `code/c2_critical_ratio.py` →
`evidence/phase_d5/C2_CRITICAL_RATIOS.json` **byte-identical**; `code/c2_mutations.py` →
`evidence/prefreeze/C2_MUTATIONS.json` **byte-identical**, self-reporting `applied 43, real 35, static 8,
detected 40, equivalent 3, undetected [], pass true`, sha256 `512180f32a5ca85355270f57bc98c5281d8bb8de7f9e32a1d10652e1e0a4ebac`.
From `evidence/phase_d5/C2_D5_FORECAST.json` I read back `D_STAGE_CLASS = D_PARTIAL`, `closed = [305, 306]`,
`still_open = [307, 308, 309]`, `gap_fall_fraction` `0.46285183476411584 / 0.24593099374719365 /
0.18389841084966285`, `Gamma(305) = −0.08802906884054082`, `Gamma(306) = −0.030469257709306738`.

For the regenerated evidence I wrote my own JSON leaf-flattener and diffed `07c0b991`'s copy of
`C2_RECERTIFY_306.json` against HEAD's: **1224 leaves on both sides, zero paths added, zero removed, exactly three
values replaced** — `/host/note`, `/passes/determinism_256/cpu_seconds` 1153.9 → 1141.5,
`/passes/safe_side_384/cpu_seconds` 1204.2 → 1196.1. I recounted the pass structure from the artifact rather than
its prose: 18 artifacts per pass, `certified: true` on all 18 in both passes, the five consumed constants
(`C_T, tau, D1, D2, D_lo`) present on the nine `taboo_block_306_*` records giving **45 consumed-constant instances,
45 of them `ok`, at both 256 and 384 bits**, `all_ok: true` on both passes, `verdict: BOTH_PASSES_OK`.

I also verified: the frozen gate's sha256 is `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`
and `git log` on it returns exactly one commit, `87309610`; `code/c2_d5_forecast.py` and
`evidence/phase_d5/C2_D5_FORECAST.json` are last touched at `5a94568a`; **139 files changed since `5289b6ce`, all
`A` (additive), none outside `level4/closure_proofs/p5y_k5_tail_c2_closure/`**; `main` is `c123b9bb`, an ancestor of
HEAD with zero commits ahead; the working tree is clean; `K5_COVERAGE_MAP_R4.json` hashes to
`a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35` at its single commit `f2ac1eb3` and no r5 map
exists anywhere in the repository; each of the eight prior review files has exactly one commit and was never
amended; `REGISTRY_C2.json` contains no host, toolchain or precision field (the string "host" does not occur in it),
so **N10's premise is true as far as the repository can show**; the registry artifact counts are 9/9/10/11/11
sub-blocks → 50 blocks + 50 cells + 5 ARL = 105, matching the `C2_REGISTRY_VERIFY.json` self-report of
`artifacts_rechecked: 105, cells_checked: 5, pass: true`; `C2_B0_VERIFICATION.json` carries B1–B7 with
`ALL_PASS: true` (7/7). I compared the current `README.md` against `git show 87309610:…/README.md` line by line.

**Not checked.** I did not use the FLINT venv and did not re-execute either Arb/FLINT certification pass, so the
certified values inside `C2_RECERTIFY_306.json` are checked by me only for *stability across the campaign's own
regeneration*, not independently recomputed. I did not contact `rebaseguard-vultr-02` or any remote host, so N10's
supporting premise "the worker's build log records only the registry summary" remains a campaign report I cannot
falsify (r8's Note 5 says the same). I did not re-derive the K5-B / theorem-TC-T mathematics from first principles;
I relied on the producers reproducing byte-for-byte and on eight prior reviews having done that work. I read
`REVIEW_C2_PREFREEZE_R8.md` in full and the earlier seven by targeted search rather than end to end. I did not
verify predecessor namespace *contents* beyond establishing that no file outside the C2 namespace has changed since
`5289b6ce`. I did not locate the `56.2` / `66.1` re-certifying-host `cpu_seconds` figures quoted in
`CELL_306_ADOPTION.md:47–49`; they are in no committed artifact I could find, which is r8's Note 1 and remains a
NOTE here.

---

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| 1 | diff scope: `07c0b991..5609358f` touches only the C2 namespace | **PASS** | six paths: `ERRATUM_C2.md`, `OPEN_NOTES_DISPOSITION_C2.md`, `README.md`, `code/c2_recertify_306.py`, `evidence/prefreeze/C2_RECERTIFY_306.json`, and the added `review/REVIEW_C2_PREFREEZE_R8.md` |
| 2 | r8 committed verbatim, one commit, unedited | **PASS** | `git log -- review/REVIEW_C2_PREFREEZE_R8.md` → `5609358f` only; all eight review files one commit each |
| 3 | r8's three FAILs are each addressed *somewhere* | **PASS** | §"Dispositions from the EIGHTH pre-freeze review" added, one row per FAIL |
| 4 | **r8 FAIL 1 — the stale-count / false-absolute class is exhausted** | **FAIL** | three currently-false claims survive, two of them written or left by this commit. **FAIL 1** |
| 5 | the five counts r7 enumerated are now gone or rescoped | **PASS** | "four independent implementations" → "every independent implementation written against it" (`ERRATUM_C2.md:384–386`); the "two tables" sentence rewritten (`:273–277`); "the campaign's only tally" → "the two registers below" (`:319–321`); r7-row corrected to "five" in both halves (`:295`); r6-row prose de-counted |
| 6 | the two survivors C2 claims to have self-found are corrected | **PARTIAL** | N10's "the only thing standing between" is gone (`OPEN_NOTES:89`). The README one is **replaced by a new false claim** — see FAIL 1(a) |
| 7 | no round-sensitive count in code comments or docstrings | **PASS** | swept `code/*.py`; the only maintained tally is `OPEN_NOTES_DISPOSITION_C2.md:25` "35 real mutants and 8 static assertions", which my own run reproduces exactly |
| 8 | no round-sensitive count in committed JSON strings | **PASS** | flattened every committed artifact and inspected every string leaf over 40 chars; no tally, and after this commit no provenance assertion either (see row 12) |
| 9 | `phase_d/` and `phase_r/` numerals are results, not tallies | **PASS** | 5 cells, 18 artifacts, 45/45, 105/5, 9/9/10/11/11, 7/7, 2.69 CPU-h, three still-open cells — I re-derived every one of these from the artifacts or the file tree |
| 10 | **r8 FAIL 2 — no unscoped "second host" claim survives in the documents** | **PASS** | `ERRATUM_C2.md:399–403` now says "no *second host* is evidenced (**N10**)"; `CELL_306_ADOPTION.md:43–45, :69–76` and `OPEN_NOTES:82–89` are consistent with it; `README.md` makes no host claim. I swept for "second host / different host / independent host / two hosts / across the OS" outside `review/` |
| 11 | …including in the producer source | **FAIL** | the docstring's PASS 1 paragraph still asserts the build-host boundary verbatim. **FAIL 3** |
| 12 | **r8 FAIL 3 — the artifact no longer asserts the boundary** | **PASS** | `/host/note` now reads "observed on the host that ran this re-certification; the registry's build host is not recorded anywhere in this repository and no claim about it is made here". No other string leaf in any committed artifact makes a build-host comparison |
| 13 | the new `host.note` claims only what was observed | **PASS** | it asserts one observation (these values were observed here) and one repository-checkable negative (the registry records no build host), which I confirmed directly against `REGISTRY_C2.json` |
| 14 | regeneration changed exactly 3 of 1224 leaves | **PASS — verified independently** | my own leaf diff: 1224 → 1224, 0 added, 0 removed, 3 replaced (`/host/note`, two `cpu_seconds`) |
| 15 | every certified value bit-identical across the regeneration | **PASS — verified independently** | the 1221 unchanged leaves include every `fields/*` comparison, every `certified`, every `recomputed` value, `registry_sha_pin_ok`, `taboo_sha256`, `diagnostic_deviations` (27, worst 5.3188387505108386e−30) |
| 16 | artifact still `BOTH_PASSES_OK`, 45/45 at both precisions | **PASS — verified independently** | recounted from the artifact, not its prose: 45 consumed-constant instances, 45 `ok`, at 256 and at 384; `all_ok: true` both passes; `certified: true` on 18/18 both passes |
| 17 | was overriding r8's "no artifact rewrite" recommendation right? | **PASS on the decision, FAIL on the execution** | see Note 1 and FAILs 2–3 |
| 18 | producer `c2_d1_blocker.py` reproduces byte-for-byte | **PASS** | `cmp` clean |
| 19 | producer `c2_mutations.py` reproduces, 43/43, 0 undetected, sha `512180f3…` | **PASS** | `cmp` clean; 35 real + 8 static, 40 detected, 3 proven-equivalent, 0 undetected |
| 20 | producer `c2_critical_ratio.py` reproduces byte-for-byte | **PASS** | `cmp` clean; it refuses unless it reproduces Campaign B's Lemma-G anchor and C2's own published ratio, and it did not refuse |
| 21 | class, closed subset, open subset | **PASS** | `D_PARTIAL`, `{305, 306}`, `{307, 308, 309}` read from the forecast artifact |
| 22 | gap falls 0.46285183 / 0.24593099 / 0.18389841 | **PASS** | exact match to the artifact's `gap_fall_fraction` |
| 23 | Γ(305) = −0.088029069, Γ(306) = −0.030469258 | **PASS** | −0.08802906884054082, −0.030469257709306738 |
| 24 | no `evidence/` file other than `C2_RECERTIFY_306.json` changed in the diff | **PASS** | `git diff --name-status 07c0b991..5609358f` |
| 25 | all-additive and in-namespace since `5289b6ce` | **PASS** | 139 paths, all `A`, 0 outside the namespace |
| 26 | gate sha `098dd7f5…` at exactly one commit | **PASS** | `shasum` matches; `git log --follow` → `87309610` alone; `C2_D5_FORECAST.gate_sha256` and `c2_d5_forecast.GATE_SHA` carry the same string |
| 27 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS** | last commit on each path is `5a94568a` |
| 28 | `main` untouched | **PASS** | `c123b9bb`, ancestor of HEAD, 0 commits ahead; no out-of-namespace path in the range |
| 29 | coverage map r4 `a3bddd83…` intact; no r5 | **PASS** | sha verified; single commit `f2ac1eb3`; no `*COVERAGE_MAP_R5*` anywhere |
| 30 | nothing pre-empts freeze, qualification, seal, adoption or adjudication | **PASS** | no freeze/seal/qualification/authorization artifact; `R_STAGE_DESIGN.md:1` "DESIGN ONLY; nothing is executed", guard DENY; `CELL_306_ADOPTION.md:10–13` states adoption is not conferred; `NEW_REAL_ADDRESSES = 0`. The diff adds none of these |
| 31 | all eight prior review files committed and unedited | **PASS** | one commit each: `12585997`, `55c4cf00`, `d6a4def5`, `92c5d199`, `fb4d688b`, `5a098ec6`, `07c0b991`, `5609358f` |
| 32 | the campaign's headline evidence-stability claim is still true | **FAIL** | this commit replaced two published `cpu_seconds` values and left "exactly one published value has changed" standing in two documents. **FAIL 2** |
| 33 | the pre-registration boundary is stated correctly | **FAIL** | the sentence written by this commit is false on two counts. **FAIL 1(a)** |
| 34 | N9 / N10 chain complete and mutually consistent | **PASS** | N10 defined once at `OPEN_NOTES:82–89`, referenced from `ERRATUM_C2.md` and `CELL_306_ADOPTION.md:52, :76`; N9 correctly says "still one implementation" |
| 35 | cell 306's three conditions are honestly dispositioned | **PASS** | condition 1 delivered; condition 2 explicitly *not* delivered in the strong sense, in all four places that discuss it (documents only — see FAIL 3 for the source); condition 3 referred out with the decision pre-committed in both branches |
| 36 | the adoption decision is not narrowed by C2 | **PASS** | both branches keep a non-empty closed subset, so the frozen `D_PARTIAL` rule is satisfied either way |
| 37 | R stage correctly blocked | **PASS** | N7 open (`D_PRIME_OPPORTUNITY.md` shows a non-pre-registered combination clearing the 20 % bar at zero cost), N1 open, guard DENY |

---

## FAIL 1 — the false-absolute class is not exhausted; this commit added one and left another

This is the fourth consecutive round in which a repair to this defect class has itself carried an instance of the
class. I am listing every instance I found, so none is left for a tenth round.

**(a) `README.md:55–57` — new in `5609358f`, and false on two counts.**

> *(The phase rows above read "—" in the version frozen with the gate. Everything in this README from this table
> onwards — the phase states, the Result section and these notes — was written after C2's numbers existed; only the
> material above the table is part of the pre-registration.)*

`git show 87309610:level4/closure_proofs/p5y_k5_tail_c2_closure/README.md` is 41 lines. Against it:

1. **"only the material above the table is part of the pre-registration" is false.** The frozen README's line 41 —
   "K5 remains **PARTIAL** (m = 5 open on 305–309); coverage map r4 (`a3bddd83…`) is authoritative and no r5
   exists." — sits *below* the table and is **byte-identical** to the current README's line 95. I diffed the two
   lines; they are the same bytes. So pre-registration material does exist below the table, and the sentence's own
   exhaustive "only" is falsified by the document it describes.
2. **"The phase rows above read '—'" is false for two of the four phase rows that existed.** At `87309610` the
   table's B0 row read `7/7 PASS` and the gate row read `frozen at this commit`; only the D1–D5 and R-stage rows
   read "—". The B0 result — a C2 number — was recorded *at* the freeze, not after it, which is the opposite of
   what the sentence tells a reader.

Lines 1–33 of the current README *are* byte-identical to the frozen version, so the sentence's positive half is
true; it is the two universal quantifiers that are not.

This matters because the parenthetical exists solely to draw the pre-registration boundary in the front-door
document. An adjudicator uses exactly that boundary to decide which of C2's statements were made before the
campaign's numbers existed. A boundary statement that is wrong in both directions — understating the
pre-registration at the end of the file, mis-describing the frozen table's contents — is a governance-provenance
error, not a stylistic one, and it is checkable in one `git show`.

**(b) `ERRATUM_C2.md:271` — surviving, and contradicted five lines below it by text this same commit wrote.**

> "The review table is now the single place in this namespace that counts reviews, and the prose points at it."

There are two tables in this namespace that count reviews: `README.md:40–47` (eight review rows) and this
document's own round table at `:8–17` (eight round rows). The paragraph at `:273–277`, rewritten by `5609358f`,
enumerates the tables itself — "the review list at the top of the README, the round table at the top of this
document, and the registers below" — so the document now asserts one place and lists three, five lines apart. This
is the identical shape of r7 FAIL 1's closing point ("the claim that two tables are the only places a count appears
was also false") and of r8 FAIL 1(c). On its own I would file this as a NOTE; in the fourth round of this class,
inside the section the class is documented in, it belongs in the FAIL.

**(c) For completeness, instances I checked and found clean.** `ERRATUM_C2.md:4–6` states where counts belong
without claiming compliance — correct, and the right fix. Both "no sentence in this namespace states a count"
assertions are deleted, not restated. The per-round header counts ("79 checks — 60 PASS…", "38 rows, 32 PASS, 8
NOTE, 3 FAIL") are fixed historical facts about specific committed files and cannot go stale; I reconciled r8's
against its own file. `OPEN_NOTES:25`'s "35 real mutants and 8 static assertions" matches my re-run exactly.
`ERRATUM_C2.md:394`'s "Sixth instance; r5 FAIL 1" is still an off-by-one (that row is the fifth of thirteen), but
r8 raised it as a non-blocking Note 4 and the campaign's own "make the change and stop" doctrine makes leaving a
note unactioned legitimate — **NOTE, not FAIL**, and it is already disclosed in a committed review file.

**Minimal change.** Rewrite `README.md:55–57` to something that is true and cannot go stale, e.g. *"The material
above this table, and the closing line about K5's coverage map, are the version frozen with the gate at
`87309610`; the phase states from D1–D5 downward, the review rows, the Result section and these notes were written
after C2's numbers existed."* Rewrite `ERRATUM_C2.md:271` to "The tables are where reviews are counted, and the
prose points at them." Two sentences. Nothing else.

---

## FAIL 2 — this commit replaced two published values and left "exactly one published value has changed" standing in two documents

`ERRATUM_C2.md:23–25`:

> Exactly **one** published *value* has changed in the whole campaign — the C_T sensitivity row on cells 307–309 of
> the D1 diagnosis…

`README.md:85–86`:

> Exactly **one published value** has changed as a result: the C_T sensitivity row for cells 307/308/309 of the D1
> diagnosis, corrected to the admissible perturbation.

`5609358f` replaced `/passes/determinism_256/cpu_seconds` (1153.9 → 1141.5) and
`/passes/safe_side_384/cpu_seconds` (1204.2 → 1196.1) in `evidence/prefreeze/C2_RECERTIFY_306.json`, plus the
`/host/note` string. Those are published values in a committed evidence artifact, replaced by different values, in
the whole campaign. Neither sentence was touched.

This is not a semantic quibble about what counts as "published". `cpu_seconds` is load-bearing evidence *in this
namespace*: `CELL_306_ADOPTION.md:47–49` and `ERRATUM_C2.md:296` both cite the registry artifacts' `cpu_seconds`
(90.2 / 88.3 — I confirmed 90.248003954 and 88.257109067 in `taboo_block_306_02.json` and `taboo_block_305_00.json`)
as the one piece of in-repo corroboration for the build host being a different and slower machine. The campaign
asks an adjudicator to weigh `cpu_seconds` as evidence in one section and asserts two sections earlier that no
published value but one has ever changed — while having just changed two of them.

The reading under which the claim was previously verified is exactly the reading that now fails. r6's row 14 passed
it on the reading "a published value being replaced by a different value", and r8's row 14 re-verified it the same
way; both scoped their leaf diffs to `C2_D1_BLOCKER.json`, which was correct at the time because no other evidence
file had ever had a value replaced. That is no longer true, and the sentence says "in the whole campaign".

**Why it misleads.** These two sentences are the campaign's headline reason to trust it after eight NOT_READY
rounds: the prose was always the weak part, the numbers never moved. An adjudicator who checks that claim the way
three reviews have checked it — diff the evidence tree across the campaign's history — now finds a second artifact
with replaced values and no sentence in the namespace disclosing it. The disclosure exists only in the commit
message of `5609358f` ("3 of 1224 leaves changed — host.note and the two wall-clock cpu_seconds"), which is not part
of the namespace an adjudicator reads. The erratum's own r8 FAIL 3 row says the artifact was "regenerated" and that
this re-executed both passes, but never says that any published value changed.

I want to be precise about what is *not* wrong here. The narrower invariant one paragraph above, `ERRATUM_C2.md:19–21`
— "no Γ, magnitude, margin, requirement, gap fall, class or adopted-subset value has changed" — is still true, and I
verified it: all 1221 other leaves, including every certified field, are bit-identical. The defect is the unscoped
sentence that follows it, not the science.

**Minimal change.** Scope both sentences and disclose the regeneration where the claim is made. E.g.
`ERRATUM_C2.md:23`: *"Exactly one published value bearing on a result has changed in the whole campaign — the C_T
sensitivity row… Separately, the r8 FAIL 3 repair regenerated `C2_RECERTIFY_306.json`: 3 of its 1224 leaves changed
— the `host.note` string and the two wall-clock `cpu_seconds` totals — and every certified value reproduced
bit-identically."* Mirror the scoping in `README.md:85`. Two clauses and one sentence; no artifact is touched.

---

## FAIL 3 — the build-host assertion r8 named still stands in the producer's docstring, which now contradicts its own source comment

r8 FAIL 3 named **three** places carrying the assertion: `code/c2_recertify_306.py:98` (the hardcoded string),
the docstring at `:1`, and the docstring at `:11–13`. `5609358f` fixed the first two. The third is untouched and is
now at lines 13–15:

> PASS 1 -- DETERMINISM, at the artifacts' own 256 bits. … Run here on **a different operating system, a different
> CPU architecture, a different Python and a DIFFERENT COMPILED BUILD of the Arb/FLINT stack than produced the
> registry**. Identity across that gap is evidence the certification does not depend on the machine it ran on.

That is the same comparative claim about the **build** host, in capitals, and the sentence after it makes the claim
load-bearing ("identity across that gap"). It is the assertion N10 says is recorded nowhere and that
`CELL_306_ADOPTION.md:45` says "rests on C2's report, **not on an artifact**".

The file now contradicts itself across 85 lines. At `:98–102` the same module says:

> It deliberately makes no claim about the host that built the registry: nothing in the repository records that, so
> a "second host" or "different build" assertion would not be an observation. … Removed on pre-freeze review r8.

A reader who opens the producer to check what the evidence means reads the docstring first. This is materially the
same defect r8 blocked on — the campaign's cited producer asserting an unattested boundary — surviving eighty-odd
lines above the comment that explains its removal, and it is the fourth round in which a repair fixed the named
instances minus one. It also
means the row-11 form of r8 FAIL 2 ("no equivalent unscoped claim survives *anywhere*") is not satisfied.

**Minimal change.** Rewrite `code/c2_recertify_306.py:13–15` to the sense the rest of the file now uses: the pass
re-runs certification on a host whose OS, architecture, Python and Arb/FLINT build are recorded in the artifact, and
bit-identity is evidence the certification does not depend on the machine it ran on — with no comparative claim
about the registry's build host. **The artifact must not be regenerated for this**: the docstring is not written
into `C2_RECERTIFY_306.json`, and `code_sha256` in the artifact pins `taboo_certify.py`, not this module. I checked
that a docstring edit does not perturb the artifact's leaves. Editing a docstring without regenerating is the whole
point of the distinction the campaign drew in FAIL 3's disposition.

---

## Notes (non-blocking)

**Note 1 — on the artifact-regeneration deviation: the decision was right; the execution was not finished.**
r8 recommended two disclosure clauses and explicitly no artifact rewrite. C2 regenerated instead. I think C2 was
right, and I would not want the reasoning softened: an evidence file that carries an editorial assertion inside its
`host` object, beside five genuinely recorded fields, is read by both humans and machine consumers as recorded fact,
and a disclosure in a different document does not repair the artifact — it documents that the artifact is wrong and
leaves it wrong. Removing the string at source and re-deriving the file is the stronger repair, and it was done in
an auditable way: I reproduced the campaign's accounting exactly and independently (3 of 1224 leaves, 0 added, 0
removed, every certified value bit-identical), so the regeneration cost nothing in verifiability and bought a third
independent determinism replication. A campaign that regenerates evidence after a review deserves suspicion by
default; this one earned the benefit of the doubt by making the change small, mechanical and checkable.

What it did not do is carry the change through. The same module still asserts the removed claim in its docstring
(FAIL 3), and the two sentences that quantify how much published evidence has ever moved were not updated by the
commit that moved some (FAIL 2). That is the campaign's own documented failure mode — "a neighbouring sentence the
fix failed to carry along" — applied to its own heaviest repair. The right disposition now is to **keep the
regeneration and finish it**, not to reverse it. I would also record the 3-of-1224 accounting in
`ERRATUM_C2.md` rather than only in the commit message: an adjudicator does not read commit messages, and this is
the one place where the campaign rewrote committed evidence after a review.

**Note 2 — the self-sweep is real and is working, just not yet complete.** The commit's claim to have swept the
namespace itself rather than grepping is borne out: N10's "the only thing standing between" is a genuine
self-catch, and I found no instance of the class in `phase_d/`, `phase_r/`, `config/`, `code/` (counts) or any
committed JSON. The three defects above are all in the two documents the sweep rewrote, which suggests the sweep
covered the namespace but not the diff.

**Note 3 — r8's Notes 3, 4, 5 and 6 remain unactioned, correctly.** "nine leaves have ever changed" vs "have ever
had a value replaced" (r8 Note 3), the "Sixth instance" ordinal (Note 4), N10's uncheckable build-log premise
(Note 5) and the singular heading over N6–N10 (Note 6) are all still there. r8 marked all four non-blocking and the
campaign's own lesson is to make the change asked for and stop. I agree with leaving them, and I am recording that
agreement so a tenth round does not treat them as accumulating debt. If any one of them is touched, Note 3's
wording is the one worth fixing, because one of the nine replaced leaves is literally named `magnitude` while
`ERRATUM_C2.md:19` says no magnitude has changed.

**Note 4 — the 56.2 / 66.1 figures still have no committed source.** `CELL_306_ADOPTION.md:47–49` cites them as
timings "on the re-certifying host". `C2_RECERTIFY_306.json` records per-pass totals only (now 1141.5 and 1196.1),
not per-artifact timings, so I could not locate these two numbers in any committed artifact. This is r8's Note 1;
it remains a NOTE because the corroboration argument does not depend on the exact figures and the direction is not
in doubt.

**Note 5 — on the calibration I was given.** I think it is right and I applied it as written. The science has not
moved and I re-derived it; every defect I am blocking on is textual. But two of the three are false statements about
what this campaign's own evidence and pre-registration contain, made in the two documents an adjudicator reads
first, and one of them was created by the commit under review. "Textual" is not the same as "cosmetic". I record
also that I considered and rejected `READY_TO_FREEZE_WITH_NOTES`: FAIL 2 in particular would have an adjudicator
weighing a stability guarantee that the namespace no longer satisfies, and it takes two clauses to fix.

---

## What I did not check

- The Arb/FLINT passes themselves. I did not use the FLINT venv and did not recompute any certified constant. The
  determinism and safe-side results are trusted on the strength of the artifact plus eight prior reviews; my
  contribution is that the regeneration perturbed none of them.
- Anything on a remote host. AWS was not touched at all; `rebaseguard-vultr-02` was not contacted. N10's build-log
  premise is therefore unverified by me.
- The underlying K5-B / TC-T derivations from first principles. I verified that the committed producers reproduce
  their artifacts byte-for-byte, not that the mathematics they implement is correct.
- The seven pre-r8 review files end to end; I read r8 in full and searched the rest.
- Predecessor namespace contents. I established only that no path outside the C2 namespace changed since
  `5289b6ce`.
- The `D_PRIME_OPPORTUNITY.md` counter-combination arithmetic (N7). Prior rounds derived it; I read it and did not
  recompute it.

---

## Verdict counts

| | |
|---|---|
| rows | 37 |
| PASS | 33 |
| PARTIAL | 1 |
| **FAIL** | **3** |
| notes | 5 |

**VERDICT: NOT_READY.**

Three changes, all textual, no artifact regenerated:

1. `README.md:55–57` — restate the pre-registration boundary truthfully (the closing K5 line is also frozen text;
   the B0 and gate rows did not read "—"); and `ERRATUM_C2.md:271` — "the single place … that counts reviews" is
   contradicted five lines below it.
2. `ERRATUM_C2.md:23` and `README.md:85` — scope "exactly one published value has changed" to values bearing on a
   result, and disclose in the erratum that the r8 FAIL 3 repair replaced three of `C2_RECERTIFY_306.json`'s 1224
   leaves with every certified value bit-identical.
3. `code/c2_recertify_306.py:13–15` — remove the surviving build-host comparison from the docstring, which
   contradicts the same file's own comment at `:97–101`. Do not regenerate the artifact.

The science is settled, reproduced and unmoved; the D-stage result, the closed subset, the gate and the integrity
envelope are all in order, and the artifact regeneration was the right call and is fully auditable. The namespace is
three sentences away from being fit to freeze.

*Ninth independent fresh-context pre-freeze review, 2026-09-21, HEAD `5609358f`. Read-only; this file is the only
file I wrote.*
