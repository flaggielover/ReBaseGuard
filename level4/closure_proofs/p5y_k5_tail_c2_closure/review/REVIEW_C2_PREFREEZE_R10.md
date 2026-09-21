# Tenth independent pre-freeze review — Campaign C2, D-stage successor

**VERDICT: NOT_READY**

*Tenth independent fresh-context pre-freeze review, 2026-09-21, worktree `/Users/suzhe/ReBaseGuard-k5c2`, branch
`p5y-k5-tail-c2`, HEAD `575919cb`. Read-only: this file is the only file I wrote, and I ran no writing git command.
AWS was not touched.*

---

## Reviewer context — what I re-derived, and what I took on trust

I wrote none of this work and read it cold, starting from `git diff 5609358f..575919cb` as instructed and then
widening. Everything below that I call verified, I verified myself on this machine (macOS/arm64, stdlib
CPython 3, `PYTHONINTMAXSTRDIGITS=0`).

**Re-derived independently.** All three producers re-run and `cmp`-compared against their committed artifacts:
`code/c2_d1_blocker.py` → `evidence/phase_d1/C2_D1_BLOCKER.json` **byte-identical**; `code/c2_critical_ratio.py` →
`evidence/phase_d5/C2_CRITICAL_RATIOS.json` **byte-identical**; `code/c2_mutations.py` →
`evidence/prefreeze/C2_MUTATIONS.json` **byte-identical**, self-reporting `applied 43, real 35, static 8,
detected 40, equivalent 3, undetected [], pass true`, sha256
`512180f32a5ca85355270f57bc98c5281d8bb8de7f9e32a1d10652e1e0a4ebac`. From `C2_D5_FORECAST.json` I read back
`D_STAGE_CLASS = D_PARTIAL`, `closed = [305, 306]`, `still_open = [307, 308, 309]`, `gap_fall_fraction`
`0.46285183476411584 / 0.24593099374719365 / 0.18389841084966285`, `Gamma(305) = −0.08802906884054082`,
`Gamma(306) = −0.030469257709306738`, `gate_sha256 = 098dd7f5…`, `gate_frozen_before_forecast: true`.

I wrote my own JSON leaf-flattener and applied it to `C2_RECERTIFY_306.json` **across all three of its commits**,
not only the last pair: `8aee1fc5 → 55c4cf00` replaced three leaves, `55c4cf00 → 5609358f` replaced three leaves,
1224 leaves throughout, nothing ever added or removed. From the artifact itself I recounted 18 artifacts per pass,
`certified: true` on all 18 in both passes, the five consumed constants on the nine `taboo_block_306_*` records
giving **45 consumed-constant instances, 45 `ok`, at both 256 and 384 bits**, `all_ok: true` on both passes,
`verdict: BOTH_PASSES_OK`, `registry_sha_pin_ok: true`, `diagnostic_deviations` 27 / worst 5.3188387505108386e−30.
I probed the artifact for every fragment of the repaired docstring and enumerated its string leaves by key.

I compared the current `README.md` against `git show 87309610:…/README.md` line by line and hashed the closing
line on both sides. I read the committed files of reviews r5, r6, r7, r8 and r9 for what each one actually
verified about `C2_D1_BLOCKER.json`. I confirmed 90.248003954 and 88.257109067 directly in
`taboo_block_306_02.json` and `taboo_block_305_00.json`; `evidence/registry_c2/` has exactly one commit
(`5a94568a`); the gate hashes to `098dd7f5…` at its single commit `87309610`; `c2_d5_forecast.py` and
`C2_D5_FORECAST.json` are last touched at `5a94568a`; **140 paths changed since `5289b6ce`, all `A`, none outside
the namespace**; `main` is `c123b9bb`, an ancestor of HEAD with zero commits ahead; the working tree is clean;
`K5_COVERAGE_MAP_R4.json` hashes to `a3bddd83…` at its single commit `f2ac1eb3` and no r5 map exists anywhere;
each of the nine prior review files has exactly one commit.

**Not checked.** I did not use the FLINT venv and did not re-execute either Arb/FLINT pass, so the certified values
inside `C2_RECERTIFY_306.json` are checked by me only for stability across the campaign's own regenerations, not
independently recomputed. I contacted no remote host, so N10's supporting premise about the worker's build log
remains a campaign report I cannot falsify. I did not re-derive the K5-B / TC-T mathematics from first principles.
I read r9 in full and r5–r8 by targeted search. I did not verify predecessor namespace contents beyond
establishing that nothing outside the C2 namespace changed since `5289b6ce`.

---

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| 1 | diff scope: `5609358f..575919cb` touches only the C2 namespace | **PASS** | four paths: `ERRATUM_C2.md`, `README.md`, `code/c2_recertify_306.py`, added `review/REVIEW_C2_PREFREEZE_R9.md` |
| 2 | r9 committed verbatim, one commit, unedited | **PASS** | `git log -- review/REVIEW_C2_PREFREEZE_R9.md` → `575919cb` only |
| 3 | all nine prior review files committed, one commit each, never amended | **PASS** | `12585997`, `55c4cf00`, `d6a4def5`, `92c5d199`, `fb4d688b`, `5a098ec6`, `07c0b991`, `5609358f`, `575919cb` |
| 4 | **r9 FAIL 1(a) — the README pre-registration footnote is now true** | **PASS — verified** | full line-by-line diff against `git show 87309610:…/README.md`; every clause of `README.md:56–60` checks out (see Note 1) |
| 5 | …"its closing line is unchanged from it" | **PASS — verified** | frozen line 41 and current line 100 hash identically to `c1fb22bb…` |
| 6 | …"its B0 and gate rows already read `7/7 PASS` and `frozen at this commit`" | **PASS** | frozen README lines 36–37, verbatim |
| 7 | …"first written as a pre-registration and committed with the gate at `87309610`" | **PASS** | `README.md` and `config/FEASIBILITY_GATES_C2.json` are both first added at `87309610` |
| 8 | **r9 FAIL 1(b) — the r6 row's "single place" absolute is gone** | **PASS** | `ERRATUM_C2.md:281` is rewritten in the past tense and records its own incompleteness; the phrase occurs nowhere else outside `review/` |
| 9 | **r9 FAIL 2 — "exactly one published value has changed" is gone from both documents** | **PASS** | the phrase survives only as a quotation of the withdrawn text (`ERRATUM_C2.md:32`, `:368`) and in `review/` |
| 10 | …and the replacement ledger that replaces it is complete | **FAIL** | it accounts for one of the two post-review regenerations of the same artifact. **FAIL 3** |
| 11 | …the cited corroboration figures are 90.248 / 88.257, per-artifact, in the named files | **PASS — verified** | 90.248003954 in `taboo_block_306_02.json`, 88.257109067 in `taboo_block_305_00.json`; neither is a pass total |
| 12 | …`evidence/registry_c2/` is byte-unchanged throughout the campaign | **PASS — verified** | all 106 paths added at `5a94568a`; no later commit touches the directory |
| 13 | **r9 FAIL 3 — the build-host assertion is gone from the docstring** | **PASS** | `code/c2_recertify_306.py:12–18` now states only what is recorded and cites N10; the docstring no longer contradicts the comment at `:101–107` |
| 14 | …and from every other site in the namespace | **PASS** | swept for "second host / different host / different build / than produced the registry / across the OS" outside `review/`: no survivor |
| 15 | …the artifact was **not** regenerated, as r9 instructed | **PASS** | `C2_RECERTIFY_306.json` is not in the diff; this is the one lifecycle-sensitive instruction of the round and it was obeyed |
| 16 | …the docstring is genuinely not captured in the artifact | **PASS — verified independently** | probed the raw artifact for ten fragments of both the old and the new docstring: **none present**; no regeneration was needed |
| 17 | …the supporting claim offered alongside that probe | **FAIL** | "the only free text the artifact carries is [four fields]" is false by two orders of magnitude. **FAIL 2** |
| 18 | **attribution of the whole-history D1 leaf diff** | **FAIL** | credited to r9, which did not perform it; and counted as two reviews when four performed it. **FAIL 1** |
| 19 | r9's header counts transcribed correctly | **PASS** | "37 rows, 33 PASS, 1 PARTIAL, 3 FAIL" matches r9's own verdict table, and 33 + 1 + 3 = 37 reconciles |
| 20 | the three new rows in the pattern register are accurate | **PASS** | each matches r9 FAIL 1 / 2 / 3; the round-8 labelling is consistent with the existing convention (round *N* = the repair of review *N*) |
| 21 | the r9 quotation in §"On r9's judgement of the r8 deviation" | **PARTIAL** | substance right, but it is a paraphrase inside quotation marks — see Note 3 |
| 22 | "leaving `c2_recertify_306.py` contradicting its own comment **forty lines below**" | **NOTE** | at `5609358f` the assertion was at `:14` and the comment at `:98–102` — about 84 lines. r9 said "across 85 lines". See Note 4 |
| 23 | producer `c2_d1_blocker.py` reproduces byte-for-byte | **PASS — verified** | `cmp` clean |
| 24 | producer `c2_critical_ratio.py` reproduces byte-for-byte | **PASS — verified** | `cmp` clean; it refuses unless it first reproduces Campaign B's Lemma-G anchor and C2's own published ratio, and it did not refuse |
| 25 | producer `c2_mutations.py` reproduces; 43/43, 0 undetected, sha `512180f3…` | **PASS — verified** | `cmp` clean; 35 real + 8 static, 40 detected, 3 proven equivalent, 0 undetected, `pass: true` |
| 26 | class `D_PARTIAL`, closed {305, 306}, open {307, 308, 309} | **PASS — verified** | read from `C2_D5_FORECAST.json` |
| 27 | gap falls 0.46285183 / 0.24593099 / 0.18389841 | **PASS — verified** | exact match to `gap_fall_fraction` |
| 28 | Γ(305) = −0.088029069, Γ(306) = −0.030469258 | **PASS — verified** | −0.08802906884054082, −0.030469257709306738 |
| 29 | `C2_RECERTIFY_306.json` = `BOTH_PASSES_OK`, 45/45 at both precisions | **PASS — verified** | recounted from the artifact, not its prose: 18/18 `certified` and 45/45 consumed-constant instances `ok` at 256 **and** at 384; `all_ok: true` both passes |
| 30 | the `5609358f` regeneration changed exactly 3 of 1224 leaves | **PASS — verified** | my own leaf diff: 1224 → 1224, 0 added, 0 removed, 3 replaced (`/host/note`, two `cpu_seconds`); the 1221 others include every `fields/*`, every `certified` and every `recomputed` value |
| 31 | all-additive and in-namespace since `5289b6ce` | **PASS — verified** | 140 paths, all status `A`, 0 outside `level4/closure_proofs/p5y_k5_tail_c2_closure/` |
| 32 | gate sha `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f` at exactly one commit | **PASS — verified** | `shasum` matches; the path's entire history is `87309610` |
| 33 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS — verified** | last commit on each path is `5a94568a` |
| 34 | `main` untouched | **PASS — verified** | `c123b9bb`, ancestor of HEAD, 0 commits ahead; no out-of-namespace path in the range |
| 35 | coverage map r4 `a3bddd83…` intact; no r5 map | **PASS — verified** | sha matches at its single commit `f2ac1eb3`; no `*coverage_map_r5*` anywhere in the repository |
| 36 | nothing pre-empts freeze, qualification, seal, adoption or adjudication | **PASS** | no freeze/seal/qualification/authorization artifact in the tree; `R_STAGE_DESIGN.md:1` "DESIGN ONLY; nothing is executed"; guard DENY; `D_STAGE_DECISION.md:4` `NEW_REAL_ADDRESSES = 0`; `CELL_306_ADOPTION.md` states adoption is not conferred. The diff adds none of these |

---

## FAIL 1 — the repair credits a whole-history verification to a review that did not perform it, and halves the count of those that did

This is the defect I would block on if it were the only one. It is not a bookkeeping quibble about the document's
own prose; it is a false statement about what an independent reviewer did, in the sentence that carries the
campaign's headline reliability claim, in both documents an adjudicator reads first. It was written by the commit
under review, and it replaced text that was **true**.

**(a) `ERRATUM_C2.md:24–26`.**

> **No scientific or decision value has ever been replaced except one**: the C_T sensitivity row on cells 307–309
> of the D1 diagnosis… **r5 and r9 each verified** by diffing every leaf of that artifact across its entire history
> that those nine leaves are the only ones that have ever changed.

**r9 did not do this.** Its committed file contains no whole-history leaf diff of `C2_D1_BLOCKER.json`. What r9
did with that artifact is row 18 — "producer `c2_d1_blocker.py` reproduces byte-for-byte — `cmp` clean" — which is
a reproduction check on one revision, not a diff across a history. r9's only leaf-diff work was on
`C2_RECERTIFY_306.json`, and even there it covered one commit pair (`07c0b991` → HEAD), not that artifact's
entire history either. r9 says so itself, and attributes the D1 work to other rounds
(`REVIEW_C2_PREFREEZE_R9.md:190–193`):

> r6's row 14 passed it on the reading "a published value being replaced by a different value", and r8's row 14
> re-verified it the same way; **both scoped their leaf diffs to `C2_D1_BLOCKER.json`**…

The same misattribution is repeated in this round's r9 FAIL 2 disposition row, `ERRATUM_C2.md:336`: "the C_T row,
nine leaves, **verified by r5 and r9**".

**The document contradicts itself on the point.** `ERRATUM_C2.md:411–412`, untouched by this commit, still says
"**r5** confirmed by diffing every leaf of the D1 evidence across its whole history" — the correct, single
attribution. So the erratum now names r5 alone in one place and r5-and-r9 in two others.

**(b) `README.md:92–94`.**

> **No Γ, magnitude, margin, requirement, gap fall, class or adopted-subset value has changed at any point**, which
> **two independent reviews** confirmed by diffing every leaf of the D1 evidence across its entire commit history.

**Four did, not two.** I checked each committed file:

| review | where it records the whole-history leaf diff of `C2_D1_BLOCKER.json` |
|---|---|
| r5 | `:28`, `:73` — "I diffed every leaf across all four commits that ever touched `C2_D1_BLOCKER.json`" |
| r6 | `:20`, `:64`, `:152` — "My own leaf diff across all four commits touching `C2_D1_BLOCKER.json`" |
| r7 | `:37`, `:73`, `:351` — "every leaf of `C2_D1_BLOCKER.json` across all four commits that have ever touched it" |
| r8 | `:21`, `:56` — "my own whole-history leaf diff of `C2_D1_BLOCKER.json` (487 → 490 → 540 → 525 leaves…)" |
| **r9** | **nowhere** |

Before this commit the README said "which **the fifth review** confirmed" — true, if conservative. The repair
replaced a true attribution with a false one and, on the charitable reading where the "two" are r5 and r6, still
understates the campaign's own corroboration by half.

**Why this misleads.** The invariant "no decision-relevant number has ever moved" is the entire basis on which
this campaign asks to be trusted after nine NOT_READY rounds, and its weight comes from *who* checked it
independently. An adjudicator told that r9 performed the check will open r9 and find that it did not — and the
natural inference from a false provenance claim in the headline sentence is that the other provenance claims
should be re-checked too. Conversely, the campaign is giving away half of the corroboration it actually has. Both
directions are wrong, and both are checkable with one `git grep` over `review/`.

This is the campaign's own documented signature, verbatim from `ERRATUM_C2.md:378–380`: "a correct primary
argument or fix, with a second unverified thing stacked on top of it." The primary claim — that no Γ, magnitude,
margin, requirement, gap fall, class or adopted-subset value has ever changed — is true, and I verified it.

**Minimal change.** `ERRATUM_C2.md:25` → "r5, r6, r7 and r8 each verified…"; `ERRATUM_C2.md:336` → strike "and
r9"; `README.md:93` → "which four independent pre-freeze reviews confirmed". Or, better and in the spirit of the
one repair this round that is demonstrably right: drop the count and cite — "see `review/`, rounds five through
eight". Three edits, no artifact touched.

---

## FAIL 2 — "the only free text the artifact carries is [four fields]" is false, and it is offered as the ground for not regenerating

`ERRATUM_C2.md:337`, the r9 FAIL 3 disposition row:

> No regeneration: the docstring is not captured in the artifact — verified by probing the output for its
> fragments, and **the only free text the artifact carries is `taboo_sha256`, `verdict`, `host.note` and
> `diagnostic_policy.why`**, none of them touched.

The primary claim is **correct and I verified it independently**: I probed the raw bytes of
`C2_RECERTIFY_306.json` for ten fragments of both the withdrawn and the replacement docstring and found none. No
regeneration was needed.

The corroborating clause is false. `C2_RECERTIFY_306.json` carries **835 string leaves**, and among them:

- **236 `test` fields** — one per compared field per pass — drawn from six hardcoded English templates in
  `c2_recertify_306.py:146–159`, including `"ASSERTED: recomputed <= published (published stays a valid upper
  bound)"`, `"MEASURED (internal diagnostic, not consumed): bound holds, relative deviation -1.076e-77"` and
  `"recorded only (diagnostic, not a one-sided bound)"`;
- **2 `passes/*/test` summaries** — `"bit-identical"`, `"published bound still valid"` (`:201–202`);
- **5 further `host/*` fields** beside `note` — `platform`, `machine`, `python`, `numpy`, `python_flint`.

So the artifact's authored-English surface is roughly 240 strings, not four. The list is also internally
incoherent as a taxonomy: it counts `taboo_sha256` (a 64-character hex digest) and `verdict` (an enum of two
values) as "free text" while excluding `passes/*/test`, which is also an enum of two values, and the `test`
strings, which are the only fields in the artifact that carry an *interpretation* of a comparison rather than the
comparison itself.

**Why this misleads.** The immediately preceding round's blocking defect (r8 FAIL 3) was an editorial claim
hiding inside this artifact, in a string field, read by humans and machine consumers as recorded fact. The obvious
follow-up question for an adjudicator is: *what other editorial strings does this artifact contain?* This sentence
answers that question with a list of four and thereby bounds an audit that should cover ~240 strings. I ran that
audit — none of the `test` strings carries an unattested provenance claim, and the sentence's conclusion survives
— but an adjudicator who trusts the sentence would not have run it, and the sentence is what tells them they need
not.

**Minimal change.** Delete the clause. The probe result carries the claim on its own and is the stronger evidence.
If a positive statement is wanted, the true and narrow one is: "the artifact's only free-text fields that could
have carried the assertion are `host.note` and `diagnostic_policy.why`; neither is touched by this commit, and I
re-probed the output for every fragment of the old and new docstring."

---

## FAIL 3 — the new replacement ledger accounts for one of the two post-review regenerations of the same artifact

r9 FAIL 2 blocked because the campaign's stability claim did not match what a whole-history diff of the evidence
tree finds, and because the 3-of-1224 accounting lived only in a commit message. Its remedy (r9 Note 1) was to
"record the 3-of-1224 accounting in `ERRATUM_C2.md` rather than only in the commit message: an adjudicator does
not read commit messages, and **this is the one place where the campaign rewrote committed evidence after a
review**."

That premise is wrong, and the repair inherited it. **`C2_RECERTIFY_306.json` has been rewritten after a review
twice.** My own leaf diff across all three of its commits:

| transition | leaves | added | removed | replaced |
|---|---|---|---|---|
| `8aee1fc5 → 55c4cf00` (the **r2** repair round) | 1224 → 1224 | 0 | 0 | **3**: `/diagnostic_policy/why`; `cpu_seconds` **1653.6 → 1153.9**; `cpu_seconds` **1691.8 → 1204.2** |
| `55c4cf00 → 5609358f` (the **r8** repair round) | 1224 → 1224 | 0 | 0 | **3**: `/host/note`; `cpu_seconds` 1153.9 → 1141.5; `cpu_seconds` 1204.2 → 1196.1 |

The new ledger at `ERRATUM_C2.md:24–38` states the second and not the first:

> Two **non-scientific** values were also replaced, by the r8 repair… Regenerating `C2_RECERTIFY_306.json` … 3 of
> 1224 leaves, nothing added or removed, every certified value bit-identical.

and `README.md:90–92` mirrors it — "Separately, a later repair regenerated `C2_RECERTIFY_306.json` … replacing
that note and two wall-clock timings".

The earlier regeneration **is** disclosed in this document, at `:215–219`, about 190 lines below, inside the r3
disposition — where it is framed as a *credit* ("a second, independent determinism replication … obtained
incidentally") rather than as a replacement of published values. Nothing is hidden. But the paragraph at the top
is the ledger: it opens with the campaign-wide absolute "No scientific or decision value has ever been replaced
except one", and everything that follows reads as its exception list. An adjudicator who runs the check r5–r8 ran
— diff the evidence tree across the campaign's history — finds two regeneration events and six leaf replacements
in this artifact, against a ledger describing one event and three, and finds that the same two `cpu_seconds`
leaves have each been replaced twice, with the larger movement (1653.6 → 1153.9, a 30 % fall) being the one the
ledger omits.

I want to be precise about what is **not** wrong here. No individual sentence in the paragraph is false: `:31`
explicitly scopes itself "by the r8 repair", and `:24`'s "scientific or decision value" is true under the
campaign's own taxonomy, in which a wall-clock total and a note string are non-scientific — and I verified that
every certified value is bit-identical across **both** regenerations, not just the second. The defect is that the
ledger presents itself as the complete answer to "what published evidence has ever been rewritten, and when", is
read that way, and is not.

And the framing it inherited is repeated at `:339–342`: "That is the one place in nine rounds where C2 departed
from a reviewer's explicit instruction." That sentence, narrowly about *instructions*, is defensible. The claim
next to it — that this was the one post-review rewrite of committed evidence — is not, and it came from r9 rather
than from C2. `ERRATUM_C2.md:390–391` is the campaign's own rule for this: "Inheriting a reviewer's unverified
claim is the same failure mode as inheriting one's own."

**Minimal change.** Replace `ERRATUM_C2.md:31–38`'s single-event accounting with the two-event table above, and
scope `README.md:90–92` to match ("regenerated twice, both times after a review"). One paragraph and one clause.
No artifact is touched.

---

## Notes (non-blocking)

**Note 1 — the r9 FAIL 1(a) repair is the best thing in this diff, and it is the model.** `README.md:56–60` is now
true in every clause, and I checked each one against `git show 87309610:…/README.md` rather than against the
description: the README and the gate are both first added at `87309610`; the frozen phase table's D1–D5 and
R-stage rows do read "—" while the B0 and gate rows read `7/7 PASS` and `frozen at this commit`; the closing K5
line is byte-identical (both hash to `c1fb22bb…`); and lines 1–33 are unchanged. The final clause — "read
`git show 87309610:…/README.md` rather than trusting a description of it here" — is the repair that cannot rot,
because its referent is immutable. Note that the sentence "The review rows, the Result section and these notes
were added after C2's numbers existed" is a positive enumeration and **not** quantified as exhaustive, which is
why it survives the fact that the phase table's gate row text also changed. That restraint is deliberate and
correct, and it is the discipline the rest of the surface still lacks.

**Note 2 — a surviving instance of the false-absolute class, which I am recording as a NOTE and not as a FAIL.**
`ERRATUM_C2.md:285–287`: "The tables carry the counts — the review list at the top of the README, the round table
at the top of this document, and the registers below — **and prose does not.**" Prose does: `:26` "those nine
leaves", `:34` "3 of 1224 leaves", `:139` "extended from 33 to 43 … 35 real mutants and 8 static assertions, 40
detected, 3 proven equivalent, 0 undetected", `:281` "wrong twice more", `:305` "The five counts", `:329` "37
rows, 33 PASS, 1 PARTIAL, 3 FAIL", and — added by this commit — `:341` "the one place **in nine rounds**". I do
not fail it: the clause predates this diff, every one of those counts is currently correct, r7's FAIL already
extracted the load-bearing lesson, and no adjudicator is misled about anything by it. But `:341`'s "in nine
rounds" is a running tally in prose that goes stale the moment a tenth round exists, and it is the exact species
the document's own doctrine at `:4–6` forbids. Delete the two words, or move the clause into the round table.

**Note 3 — `ERRATUM_C2.md:340–341` presents a paraphrase as a quotation.** It reads: *"Keep the regeneration and
finish it — do not reverse it."* r9's actual sentence (`:266–267`) is "The right disposition now is to **keep the
regeneration and finish it**, not to reverse it." The substance is identical and the reattribution is honest, but
quotation marks in this namespace are load-bearing — three prior FAILs turned on exactly what a document did or
did not say — and this one does not survive a `grep`. Also in the same sentence: "The review found that overriding
**its own** recommendation … was right". The recommendation overridden was **r8's**, not r9's; the nearest
antecedent to "its" is "The review", i.e. r9. Reword to "overriding r8's recommendation".

**Note 4 — `ERRATUM_C2.md:337` says the docstring contradicted "its own comment forty lines below".** At
`5609358f` the docstring assertion sat at `:14` and the comment at `:98–102` — about **84** lines. r9 said "across
85 lines" and "eighty-odd lines above". Cosmetic, and it misleads nobody, but it is a hand-maintained number in
prose that is simply wrong, so fix it while you are in the paragraph.

**Note 5 — a third artifact has had values replaced, and the ledger's taxonomy should say why it is excluded.**
`evidence/prefreeze/C2_MUTATIONS.json` (`5a94568a → 12585997`) had 56 leaves added and **4 replaced**: `applied`
33 → 43, `detected` 31 → 40, `real_mutants` 25 → 35, and `mutants/M10_wrong_tail_cell/caught_by/0` `"value"` →
`"tiling"`. This is the adversarial suite being *extended* at r1's request, is openly described at
`ERRATUM_C2.md:139–143`, and I reproduced the current file byte-for-byte, so I am not filing it as a ledger
omission — the experiment changed, the values did not merely get corrected. But a reader running the
whole-history diff finds three artifacts with replaced values, not two, and one sentence in the ledger saying why
an extended suite is not a replaced result would close the last hole in it.

**Note 6 — "compiled Arb/FLINT build … recorded in the output" is slightly stronger than the artifact.** The new
docstring at `:13–14`, and `CELL_306_ADOPTION.md:30–31` and `:69–70` before it, say the re-certifying host's
compiled Arb/FLINT build is recorded. What `host` actually records is `python_flint: "0.9.0"` — the binding's
version, which in practice pins a bundled FLINT binary but is not itself a record of the compiled library build.
Defensible, pre-existing, and passed by r8 and r9; I record it only because N10 turns on exactly how much
toolchain provenance the artifacts carry.

**Note 7 — r8's Note 1 / r9's Note 4 remain open and should stay open.** The `56.2` / `66.1` re-certifying-host
timings quoted at `CELL_306_ADOPTION.md:48–49` are in no committed artifact; `C2_RECERTIFY_306.json` records
per-pass totals only. I could not locate them either. Two rounds have marked this non-blocking because the
corroboration argument does not depend on the exact figures, and I agree. I also agree with r9's Note 3 that r8's
Notes 3–6 should be left alone: the campaign's own lesson is to make the change asked for and stop, and
manufacturing work from unactioned notes is how three of the last five rounds went wrong.

**Note 8 — on the calibration I was given.** I think it is right and I applied it as written; I did not escalate
anything for recurrence, and I checked each of this round's sentences on its own terms. I record two observations.
First, none of my three FAILs is a stylistic or structural preference: each is a statement of fact that is false
or materially incomplete, each concerns evidence provenance or who independently verified what, and each is
checkable in under a minute with tools already in this repository. Second, all three have the same shape the
campaign documented about itself in round three — a correct primary claim with an unchecked clause stacked beside
it — and in FAIL 3 the unchecked clause was inherited from the reviewer rather than invented. That is worth saying
plainly to whoever decides what happens next: the defect rate here is not noise, it is one authoring habit, and
freezing does not cure it. It does not, however, touch the science, which I re-derived and which has not moved.

---

## On `ERRATUM_C2.md` — asset or liability, keep or cut

I was asked to judge this directly, so I will, without hedging.

**The document is a net asset to a cold adjudicator, and the specific surface that keeps failing is a net
liability. Keep it, restructure it, do not cut it. That judgement is a NOTE, not a FAIL, and it must not block the
freeze on its own.**

**What is load-bearing and must survive any restructuring.** I would not want an adjudicator to receive this
namespace without:

1. §"The one thing that cannot be repaired at source" — the frozen gate's `why_gap_and_not_ratio` sentence is
   directionally inverted, and the gate was deliberately **not** amended. An adjudicator who opens
   `FEASIBILITY_GATES_C2.json` will read a false sentence in a pre-registration; this is the only place that
   explains why it is still there and why nothing the gate decides changes. Irreplaceable.
2. §"The finding that outranks all of the above" — a sound operator-level combination C2 did not pre-register
   clears the gate's own 20 % bar on all three still-open cells at zero cost, so the premise for spending the
   programme's first real order-3 tail address is not established. This is the most consequential governance fact
   in the namespace and it is against C2's own interest.
3. §"Cell 306" — condition 1 delivered, condition 2 delivered only in the weak sense N10 permits, condition 3
   referred out with C2's decision pre-committed in both branches.
4. The disposition rows for the FAILs that moved a published number or narrowed a claim: r1 FAIL 61 / 62 / 30 /
   51, r2 FAIL 65 / 66 / 10, r3's correction of C2's own inference, r4 FAIL 1, r7 FAIL 2.
5. The replacement ledger at the top, **once FAIL 3 is fixed** — what evidence has ever been rewritten, when, and
   by how much.
6. The two registers in §"The pattern, named". The tables, specifically.

**What is narrative and could be deleted without loss to an adjudicator.** Roughly: the prose of §"The pattern,
named" surrounding its two tables (`:378–424`) — the self-caught anecdotes, the r5-note-8 parenthetical
distinguishing ratio from absolute difference, "the only encouraging thing in this section", and the `:420–424`
tombstone describing two paragraphs that were deleted five rounds ago; and the disposition rows whose subject is
the erratum's or the README's own bookkeeping rather than the science — r5 FAIL 1, r5 FAIL 2, r6 FAIL 1, r7 FAIL
1, r8 FAIL 1, r9 FAIL 1. Those six rows and their surrounding prose are the campaign auditing its own prose. They
have produced, directly, nearly every new defect since round five, including two of my three today.

**Is the remaining self-descriptive prose load-bearing?** For the *adjudicator*, almost none of it is. The
adjudicator needs to know that this campaign's prose has been wrong repeatedly while its arithmetic never has —
which is one sentence plus the two registers — and needs the reliability record to be *honest*, not *exhaustive*.
The sentences that keep failing are not the ones conveying that; they are ornamental precision claims about the
document's own current state: "the only place…", "no sentence states a count", "the tables carry the counts and
prose does not", "exactly one published value has changed", "the only free text the artifact carries is…". Every
one of those is a universal quantifier over a mutable corpus, evaluated by hand, in a document that is edited
every round. They cannot be maintained, and they buy the adjudicator nothing. Deleting them costs no information.

**Would replacing description with citation end the class?** Largely yes, and it is the right move — but not
because the trick worked once. It works because a citation's referent is immutable and a description's subject is
not. Test it against this round: all three of my FAILs are claims about corpora that are *already frozen in git* —
what nine committed review files contain (FAIL 1), what a committed artifact contains (FAIL 2), what an
artifact's commit history contains (FAIL 3). Every one of them would have been prevented by the same discipline,
stated as a rule:

> **Never describe a corpus you can cite. If you must describe it, run the command that checks the description
> before you commit the sentence — and put the command in the text.**

r9's footnote repair applied that rule to the pre-registration and is the only sentence in this diff I could not
break. The campaign has been applying it to one corpus at a time, which is why the class migrates rather than
closes: round seven fixed counts in the README, round eight fixed counts in the erratum, round nine fixed the
pre-registration boundary, round ten finds it in review attribution and artifact contents. Apply the rule to
*every* corpus claim in one pass and the class ends.

**So: keep, cut, or restructure?** Restructure, in one commit, and then stop editing it:

- Keep items 1–6 above.
- Delete every sentence that asserts a property of the namespace's own current text. Not soften — delete. A
  sentence that says where counts belong (`:4–6`) is fine because it states a policy; a sentence that claims the
  policy is currently satisfied is a claim about every other sentence in the repository and will be false again.
- Convert the six bookkeeping disposition rows to a single short section: "six of the ten rounds blocked on
  self-descriptive prose in this document and in `README.md`; the instances are r5 FAIL 1–2, r6 FAIL 1, r7 FAIL 1,
  r8 FAIL 1, r9 FAIL 1, r10 FAIL 1–3; see `review/`." One row, one citation, no maintained text.
- Leave the length alone otherwise. 435 lines is long, but an adjudicator reads §"Cell 306" and §"The finding that
  outranks all of the above" and the ledger, all of which are signposted from the top at `:43–44`. Length is not
  what is failing here; self-reference is.

**One thing I will say in the document's favour, because it is easy to lose in the tenth round of this.** The
disclosure discipline in this erratum is better than in any campaign document I have read in this programme. It
discloses a directionally inverted sentence inside its own frozen gate; it records that its own pre-registration
ran out before the deterministic direction did, which is the finding most against its interest; it names its
authorship's failure mode explicitly and tells a successor to expect it. The defects I am filing are all in the
layer the document built to *account for* that honesty, not in the honesty itself. Cutting the accounting layer
back hard would make the document better, not less candid.

---

## What I did not check

- The Arb/FLINT passes themselves. I did not use the FLINT venv and recomputed no certified constant. The
  determinism and safe-side results are trusted on the strength of the artifact, my own stability diff across all
  three of its commits, and nine prior reviews.
- Anything on a remote host. AWS was not touched at all; `rebaseguard-vultr-02` was not contacted. N10's
  build-log premise is unverified by me, as it was by r8 and r9.
- The underlying K5-B / TC-T derivations from first principles. I verified that the committed producers reproduce
  their artifacts byte-for-byte, not that the mathematics they implement is correct.
- `D_PRIME_OPPORTUNITY.md`'s counter-combination arithmetic (N7). I read it and did not recompute it.
- Reviews r1–r4 end to end; I read r9 in full and r5–r8 by targeted search, which for FAIL 1 meant searching each
  of r5–r9 for its leaf-diff work specifically.
- Predecessor namespace contents. I established only that no path outside the C2 namespace changed since
  `5289b6ce`.
- `evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json` and `code/c2_b0_verify.py` / `c2_refined_registry.py`
  beyond confirming they are single-commit and unchanged in this diff.

---

## Verdict counts

| | |
|---|---|
| rows | 36 |
| PASS | 31 |
| PARTIAL | 1 |
| NOTE | 1 |
| **FAIL** | **3** |
| notes | 8 |

**VERDICT: NOT_READY.**

The science is settled and I re-derived it cold: all three producers byte-for-byte, `D_PARTIAL` with closed
{305, 306}, the three gap falls, both Γ, `BOTH_PASSES_OK` with 45/45 at both precisions and 18/18 certified. The
gate is untouched at one commit, the integrity envelope is clean and additive, `main` is untouched, the coverage
map is intact, nothing pre-empts the lifecycle, and the one lifecycle-sensitive instruction of this round — do not
regenerate the artifact — was obeyed. **The namespace is not fit to freeze today, and the distance is three edits
and one paragraph:**

1. `ERRATUM_C2.md:25`, `:336` and `README.md:93` — r9 did not diff `C2_D1_BLOCKER.json` across its history; r5,
   r6, r7 and r8 each did. Correct the attribution, or drop the count and cite `review/`.
2. `ERRATUM_C2.md:337` — delete "the only free text the artifact carries is…". The probe result is the evidence
   and it is sound; the clause is false and bounds an audit it should not bound.
3. `ERRATUM_C2.md:31–38` and `README.md:90–92` — the ledger must show **both** post-review regenerations of
   `C2_RECERTIFY_306.json`: `55c4cf00` (`diagnostic_policy.why`, 1653.6 → 1153.9, 1691.8 → 1204.2) and
   `5609358f` (`host.note`, 1153.9 → 1141.5, 1204.2 → 1196.1). Three of 1224 leaves each time, nothing added or
   removed, every certified value bit-identical across both.

Then apply Note 8's rule to the whole namespace in the same pass rather than to one corpus at a time, and fix
Notes 2–4 while in the file. Nothing here requires touching an artifact, a producer, the gate or any predecessor.

*Tenth independent fresh-context pre-freeze review, 2026-09-21, HEAD `575919cb`. Read-only; this file is the only
file I wrote, and I ran no writing git command. AWS was not touched.*
