# Eleventh independent pre-freeze review — Campaign C2, D-stage successor

**VERDICT: NOT_READY**

*Eleventh independent fresh-context pre-freeze review, 2026-09-21, worktree `/Users/suzhe/ReBaseGuard-k5c2`,
branch `p5y-k5-tail-c2`, HEAD `87004e2b`. Read-only: this file is the only file I wrote, and I ran no writing git
command. AWS was not touched.*

---

## Reviewer context — what I re-derived, and what I took on trust

I wrote none of this work and read it cold, starting from `git diff 575919cb..87004e2b` as instructed and then
widening to the whole namespace. Everything below that I call verified, I verified myself on this machine
(macOS/arm64, stdlib CPython 3, `PYTHONINTMAXSTRDIGITS=0`). I did not use the FLINT venv.

**Re-derived independently.** All three committed producers re-run and `cmp`-compared against their artifacts:
`code/c2_mutations.py` → `evidence/prefreeze/C2_MUTATIONS.json` **byte-identical**, sha256
`512180f32a5ca85355270f57bc98c5281d8bb8de7f9e32a1d10652e1e0a4ebac`, self-reporting `applied 43, real 35,
static 8, detected 40, equivalent 3, undetected [], pass true`; `code/c2_d1_blocker.py` →
`evidence/phase_d1/C2_D1_BLOCKER.json` **byte-identical**; `code/c2_critical_ratio.py` →
`evidence/phase_d5/C2_CRITICAL_RATIOS.json` **byte-identical**. From `C2_D5_FORECAST.json` I read back
`D_STAGE_CLASS = D_PARTIAL`, `closed = [305, 306]`, `still_open = [307, 308, 309]`, gap falls
`0.46285183476411584 / 0.24593099374719365 / 0.18389841084966285`, `Gamma(305) = −0.08802906884054082`,
`Gamma(306) = −0.030469257709306738`, `gate_sha256 = 098dd7f5…`, `gate_frozen_before_forecast: true`.

**The corpus sweep, which is what I was sent to do.** I wrote my own JSON leaf-flattener and ran it over the
**whole history of every evidence and config file in the namespace**, not the two files the ledger names —
`git log --reverse --all -- <file>`, consecutive revisions, leaf by leaf. Three files have more than one commit:
`C2_D1_BLOCKER.json` (4), `C2_RECERTIFY_306.json` (3), and **`C2_MUTATIONS.json` (2)**. The first two reproduce
the ledger exactly. The third is not in the ledger and has four replaced leaves. That is note 1 and it is a FAIL.

I then swept the namespace for universal, superlative and self-descriptive claims over a mutable corpus: every
Markdown file, every `.py` docstring and comment, and every string leaf of every committed JSON. Section
§"The corpus-claim defect class" below lists every instance I found and says which are sound.

**Taken on trust.** The Arb/FLINT passes themselves; the mathematics the producers implement; N10's build-log
premise; anything on a remote host.

---

## Checklist

| | check | verdict | evidence |
|---|---|---|---|
| 1 | **r10 FAIL 1 — verifier attribution corrected** | **PASS — verified** | `ERRATUM_C2.md:27` and `README.md:95` now credit r5, r6, r7, r8. I re-checked each committed review file myself: r5 (`:28`, `:73`), r6 (`:20`, `:64`, `:152`), r7 (`:37`, `:73`, `:351`), r8 (`:21`, `:56`) each record a whole-history leaf diff of `C2_D1_BLOCKER.json` |
| 2 | r9 did **not** perform that diff | **PASS — verified** | r9's only leaf-diff work is `C2_RECERTIFY_306.json` across `07c0b991 → 5609358f` (r9 row 14). Its `C2_D1_BLOCKER.json` work is a one-revision `cmp` (r9 row 18). The correction is right |
| 3 | **r10 FAIL 2 — free-text bound withdrawn** | **PASS — verified** | The "only free text the artifact carries is four fields" bound appears nowhere in the namespace outside the r10 disposition row that withdraws it. I reproduced both numbers: the artifact holds **835 string leaves, 236 of them at a `.test` key** |
| 4 | the probe the withdrawn bound was ornamenting | **PASS — reproduced** | I tokenised `c2_recertify_306.py`'s docstring and searched the artifact's raw bytes for every 6-, 8-word run: **0 hits**. The only 5-word hit is the generic "An earlier version of this", which occurs in `diagnostic_policy.why` and is not a docstring capture. The claim stands on its own, as C2 says |
| 5 | **r10 FAIL 3 — ledger lists both `C2_RECERTIFY_306.json` regenerations** | **PARTIAL** | Both rows are present and both are exactly right (note 2). But the ledger's stated scope is every evidence file, and it is met for two of three (note 1) |
| 6 | ledger row 2 — `8aee1fc5 → 55c4cf00`, 3 leaves | **PASS — verified** | my leaf diff: 1224 → 1224, 0 added, 0 removed, **3 replaced** — `diagnostic_policy.why`, `cpu_seconds` 1653.6 → 1153.9 and 1691.8 → 1204.2. Exactly as tabulated |
| 7 | ledger row 3 — `55c4cf00 → 5609358f`, 3 leaves | **PASS — verified** | 1224 → 1224, 0 added, 0 removed, **3 replaced** — `host.note`, `cpu_seconds` 1153.9 → 1141.5 and 1204.2 → 1196.1. Exactly as tabulated |
| 8 | ledger row 1 — `C2_D1_BLOCKER.json`, 9 leaves across its history | **PASS — verified** | my diff across all four commits: `e71378a0 → 55c4cf00` replaces **9** leaves (C_T `magnitude`/`delta_vs_base`/`relative_gain` on 307/308/309); `55c4cf00 → d6a4def5` replaces **0**; `d6a4def5 → 92c5d199` replaces **0**. Nine is right |
| 9 | **the ledger is complete over every evidence file** | **FAIL** | `evidence/prefreeze/C2_MUTATIONS.json`, `5a94568a → 12585997`, replaces **4** leaves and is absent from the ledger. **Note 1 — FAIL 1** |
| 10 | "Neither regeneration changed a certified value … all 18 artifacts stayed `certified: true`" | **PASS — verified** | neither pair touches a `certified` leaf; I counted 36 `certified` leaves (18 artifacts × 2 passes) at HEAD, all `true` |
| 11 | `evidence/registry_c2/` has exactly one commit in its history | **PASS — verified** | `git log --all --format=%H -- evidence/registry_c2/` → one commit, `5a94568a`. All 76 files in it are single-commit |
| 12 | no build-host record anywhere in C2's `evidence/` or `config/` | **PASS — verified** | the registry's 50 distinct key paths carry no host/platform/toolchain field. The only two host records are `C2_RECERTIFY_306.json.host` and `C2_REGISTRY_VERIFY.json.host`, both of the *re-certifying / verifying* host; `config/` has no host record at all |
| 13 | the wider claim, "the registry's build host is not recorded anywhere in this repository" (`host.note`, `CELL_306_ADOPTION.md`, N10) | **PASS — spot-checked** | `grep -rl 'registry_c2\|REGISTRY_C2\|c2_refined_registry'` over the repo returns **only** paths inside this namespace, so no out-of-namespace file records anything about that registry, let alone its build host |
| 14 | the "only in-repo corroboration" claim is narrowed, as the commit says | **PASS** | `CELL_306_ADOPTION.md:47–48` now reads "One piece … C2 does not claim it is the only such corroboration, only that it is the one identified" |
| 15 | the corroboration figures | **PASS — verified** | 90.248003954 in `taboo_block_306_02.json`, 88.257109067 in `taboo_block_305_00.json`, per-artifact and distinct from the pass totals, as stated |
| 16 | producers reproduce byte-for-byte | **PASS — re-run here** | three for three, `cmp` clean; see reviewer context |
| 17 | class, closed subset, open subset | **PASS — verified** | `D_PARTIAL`, `{305, 306}` closed, `{307, 308, 309}` open, read back from the artifact |
| 18 | gap falls 0.46285183 / 0.24593099 / 0.18389841 | **PASS — verified** | exact match, full precision |
| 19 | Γ(305) = −0.088029069, Γ(306) = −0.030469258 | **PASS — verified** | −0.08802906884054082 and −0.030469257709306738 |
| 20 | `C2_RECERTIFY_306.json` = `BOTH_PASSES_OK`, 45/45 at both precisions | **PASS — recounted** | `verdict: BOTH_PASSES_OK`; I recounted the consumed-constant checks from the artifact: **45 at 256 bits, 45 at 384 bits, all `ok`**; 18 artifacts, 9 blocks × 5 constants |
| 21 | gate sha `098dd7f5c3cf…b28f` at exactly one commit | **PASS — verified** | `shasum -a 256` matches; the path's entire history is `87309610` |
| 22 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS — verified** | last commit on each path is `5a94568a` |
| 23 | all-additive and in-namespace since `5289b6ce` | **PASS — verified** | `git diff --name-status 5289b6ce..87004e2b` → **141 A, 0 M, 0 D**; no path outside `level4/closure_proofs/p5y_k5_tail_c2_closure/` |
| 24 | `main` untouched | **PASS — verified** | `main` is `c123b9bb`; no C2 commit on it |
| 25 | coverage map r4 `a3bddd83…` intact; no r5 map | **PASS — verified** | sha matches `a3bddd83234f…10a35` at its single commit `f2ac1eb3`; `find -iname '*COVERAGE_MAP_R5*'` → nothing |
| 26 | nothing pre-empts freeze, qualification, seal, adoption or adjudication | **PASS** | no lifecycle artifact anywhere in the tree; the diff adds none; guard DENY; `R_STAGE_DESIGN.md` design-only; `CELL_306_ADOPTION.md` states adoption is not conferred |
| 27 | all ten prior review files committed and unedited | **PASS — verified** | each of `review/REVIEW_C2_PREFREEZE{,_R2…_R10}.md` has **exactly one** commit in `git log --all` |
| 28 | the r10 disposition header reconciles with r10's own verdict table | **PASS — verified** | "36 rows, 31 PASS, 1 PARTIAL, 1 NOTE, 3 FAIL" against r10 `:433–441`: identical |
| 29 | `ERRATUM_C2.md:4` — "this document dispositions every FAIL from every one of them" | **PASS — recounted** | 27 disposition rows; round table sums 6+3+1+3+2+1+2+3+3+3 = **27**. Reconciles |
| 30 | `README.md:3` — "Nothing outside this namespace is modified" | **PASS — verified** | row 23 |
| 31 | **did the repair introduce a new defect?** | **FAIL** | yes. `ERRATUM_C2.md:298–300` and `:379` claim compliance — "every hand-maintained tally has been deleted from prose … and prose does not" — and the repair commit added a fresh prose tally to `README.md:95`. **Note 3 — FAIL 2** |
| 32 | code comments and docstrings swept for the class | **PASS** | one corpus universal in `code/`: `c2_recertify_306.py:107`'s "recorded anywhere in this repository", which is row 13 and holds. Nothing else |
| 33 | committed JSON string leaves swept for the class | **PASS** | every universal in committed JSON is a mathematical or gate-rule quantifier over a fixed object ("for every e in [e_lo, e_hi] …", "every cell that C2 does not close"), not a claim about a corpus of files |
| 34 | `ERRATUM_C2.md:262` — "exactly nine leaves have ever changed **in this campaign**" | **NOTE** | scoped to `C2_D1_BLOCKER.json` in the same clause, but "in this campaign" reads campaign-wide, where the figure is 19. Now in tension with the ledger three sections above. **Note 4** |
| 35 | `ERRATUM_C2.md:354` — "the one place in **nine rounds** where C2 departed from a reviewer's explicit instruction" | **NOTE** | the document now dispositions ten rounds, and C2 declined r10's restructuring recommendation. **Note 5** |
| 36 | working tree clean; no stray artifact | **PASS** | `git status --porcelain` empty. An empty untracked directory `theorem/` exists locally; it is not tracked and cannot be frozen. **Note 6** |

---

## Notes

### Note 1 (FAIL 1) — the replacement ledger is incomplete: it omits `C2_MUTATIONS.json`

`ERRATUM_C2.md:34` opens the new section with an unqualified universal:

> Every leaf this campaign has replaced in an already-committed evidence file. Do not trust this table — regenerate
> it, with the loop in `git log --reverse --all -- <file>` diffing consecutive revisions leaf by leaf

I ran that loop over **every** file under `evidence/` and `config/`, which is what the sentence quantifies over.
Three evidence files have more than one commit. The ledger accounts for two. The third is

    evidence/prefreeze/C2_MUTATIONS.json    5a94568a → 12585997    197 → 253 leaves
      ~ .applied                                  33 → 43
      ~ .detected                                 31 → 40
      ~ .real_mutants                             25 → 35
      ~ .mutants.M10_wrong_tail_cell.caught_by[0] 'value' → 'tiling'   (list ['value'] → ['tiling','value'])
      + 56 leaves (M26–M35, and M32's containment proof)

Four replaced leaves, three of them the artifact's headline totals. `12585997` is the repair of the **first**
review, so this is a rewrite of already-committed evidence after a review — the exact event the ledger was built
to enumerate.

**Why this is a FAIL and not a NOTE.** Three separate statements are wrong as a result, all of them provenance
statements in the two documents an adjudicator reads first:

1. `ERRATUM_C2.md:34` — "Every leaf this campaign has replaced in an already-committed evidence file". False: at
   least four such leaves are missing. The table is not merely untrusted, it is incorrect, and the command the
   section supplies is what exposes it.
2. `ERRATUM_C2.md:25` — "**One scientific or decision value has been replaced in this campaign**". The adversarial
   suite's `applied` / `detected` / `real_mutants` were replaced, and they are decision-relevant: they are the
   campaign's own evidence-quality figures, they are quoted as "43/43, 0 undetected", and 33/33 stood in a commit
   subject and in the committed artifact before them.
3. `README.md:89–93` — "One published **scientific value** has changed … Two later repairs regenerated
   `C2_RECERTIFY_306.json`". The same two-file accounting, in the front-door document.

**What is *not* wrong.** The underlying event is disclosed, and disclosed well, at `ERRATUM_C2.md:152`: "The
adversarial suite was extended from 33 to 43 (Notes 13 and 14) … 40 detected, 3 proven equivalent, 0 undetected."
Nothing is hidden and nothing scientific is misstated: no Γ, magnitude, margin, requirement, gap fall, class or
adopted-subset value moved, the M10 change is a strengthening (one detection channel became two), and the suite
grew because r1 asked it to. The defect is that the instrument built this round to be the complete accounting is
not complete, and its scope sentence is false.

**This is the defect class, in the section built to close it.** The commit message states the rule and claims it
was applied "to every corpus claim in the bookkeeping documents at once". The claim was not run against the corpus
it quantifies over: the check was performed on the two files r9 and r10 had named, and the sentence was written as
if it covered all of them. That is the same inheritance the campaign's own register describes.

**Repair.** One row, a scope word, and a re-check:

| file | commit pair | leaves replaced | what |
|---|---|---|---|
| `evidence/prefreeze/C2_MUTATIONS.json` | `5a94568a → 12585997` | **4** | `applied` 33 → 43, `detected` 31 → 40, `real_mutants` 25 → 35, `M10.caught_by[0]` `value` → `tiling`; 56 leaves added with M26–M35 — the r1-requested suite extension, § "…FIRST pre-freeze review" |

and then `ERRATUM_C2.md:25` and `README.md:89` need "one scientific value" narrowed to what it actually is: one
scientific value **in the D1 diagnosis**, with the suite totals named as the second, non-scientific replacement.
Then re-run the loop over the whole evidence tree before committing the sentence.

### Note 2 (PASS, recorded because it is the part that worked) — the two `C2_RECERTIFY_306.json` rows are exact

Both ledger rows reproduce to the leaf and to the digit on my own flattener: 1224 → 1224 leaves in each pair, zero
added, zero removed, three replaced, and the six replaced values are the six the table prints. `certified: true`
on all 18 artifacts in both passes throughout, and every `fields/*` value untouched. r10 FAIL 3's substance is
repaired; only the scope sentence around it is not.

### Note 3 (FAIL 2) — a compliance claim about the namespace's own prose, falsified by this commit

`ERRATUM_C2.md:296–300`, in the r6 disposition:

> So every hand-maintained tally has been deleted from prose in both `README.md` and this section. The tables
> carry the counts — the review list at the top of the README, the round table at the top of this document, and
> the registers below — and prose does not.

and again at `:379`:

> The two registers below are where this campaign tallies its own defects; prose does not.

The document defines its own terms at `:379–380`: a hand-maintained count in prose is "a number left stale by a
later edit". By that definition, prose currently carries several:

- `README.md:95` — "**four** independent reviews (r5, r6, r7, r8) each confirmed this". **Added by `87004e2b`**,
  in the repair of r10 FAIL 1. It replaced "two independent reviews", which r10 failed as a stale prose count.
- `README.md:89` — "**One** published **scientific value** has changed". This exact number is the one r9 FAIL 2
  blocked on when it went stale.
- `README.md:91` — "**Two** later repairs regenerated `C2_RECERTIFY_306.json`". Was "a later repair" before r10
  FAIL 3 made it stale.
- `ERRATUM_C2.md:25` — "**One** scientific or decision value has been replaced in this campaign".
- `ERRATUM_C2.md:43` — "has therefore been regenerated after a review **twice**, not once".

**Why this is a FAIL.** r7 FAIL 1 and r8 FAIL 1 both blocked on assertions of this exact kind, and the r7
disposition row at `:318` states the remedy C2 adopted: "**both self-referential assertions are deleted rather
than maintained** … the text now states where counts belong, **without claiming compliance**." That is accurate
about the two sentences r7 named — I confirmed they were deleted at `07c0b991` — and inaccurate about the
document, because a third compliance claim survives two sections away and a fourth at `:379`. So the disposition
row misdescribes the namespace's state, and the surviving sentences are false. r10 asked for exactly this:
"Delete every sentence that asserts a property of the namespace's own current text. Not soften — delete."

This misleads about the campaign's reliability rather than about the science: it tells an adjudicator that a
discipline is in force which the same commit broke. It is also cheap to repair — delete "and prose does not" and
the "every hand-maintained tally has been deleted" clause, keep the policy sentence at `:4–5`, which r10
explicitly blessed.

I am **not** filing `README.md:95` itself as a defect. It enumerates the four reviews it counts, so it cannot go
silently stale, and it is the phrasing r10's FAIL 1 invited. The defect is the sentence that claims no such
sentence exists.

### Note 4 (NOTE, non-blocking) — "in this campaign" at `ERRATUM_C2.md:262`

> diffed **every leaf of `C2_D1_BLOCKER.json` across its entire commit history**, confirming that exactly nine
> leaves have ever changed in this campaign

Read with "in this campaign" as the temporal window, this is true and is what r5 did. Read with it as the corpus,
it is false — 19 leaves have been replaced campaign-wide (9 + 3 + 3 + 4) — and it contradicts the ledger three
sections above, which already lists 15. The sister sentences at `:288`, `:314` and `:447` are cleanly scoped to
the artifact; only this one slides. Rescope to "nine leaves of that artifact" and the ambiguity is gone.

### Note 5 (NOTE, non-blocking) — "in nine rounds" now covers ten

`ERRATUM_C2.md:354`: "That is the one place in nine rounds where C2 departed from a reviewer's explicit
instruction, and the departure held up." The document now dispositions ten rounds, and C2 did depart from r10's
explicit structural recommendation ("Convert the six bookkeeping disposition rows to a single short section"),
keeping the rows and adding an eleventh. That departure is legitimate — r10 classed the structure as a NOTE, not a
FAIL, and said the erratum is a net asset — but it belongs in the second register, the one for "a review note
received and then never actioned", which still carries only r2 note 4. Either register it or say plainly in the
r10 section that the restructuring was considered and declined, and why.

### Note 6 (INFO) — empty untracked `theorem/`

`level4/closure_proofs/p5y_k5_tail_c2_closure/theorem/` exists on disk, is empty and is untracked, so it is
outside the freeze and nothing references it. Recorded only so the next reader does not wonder.

---

## The corpus-claim defect class — is it closed?

**No. It is narrower than it was, and it is no longer in the science or the review attribution, but it is not
closed.** The rule r10 supplied — *never describe a corpus you can cite; if you must describe it, run the check
before committing the sentence and put the command in the text* — was adopted in the text and applied to most
of the corpora. It was not applied to the two claims below, one of which is the new section's own scope sentence.

Below is **every** universal, superlative or self-descriptive claim over a mutable corpus I could find in the
namespace — prose, tables, code comments and docstrings, and committed JSON strings. I checked each one.

**Surviving instances — currently false (2):**

| # | site | claim | why it fails |
|---|---|---|---|
| **S1** | `ERRATUM_C2.md:34` | "Every leaf this campaign has replaced in an already-committed evidence file" | omits `C2_MUTATIONS.json`, `5a94568a → 12585997`, 4 replaced leaves. Drags `ERRATUM_C2.md:25` and `README.md:89–93` with it. **FAIL 1 / note 1** |
| **S2** | `ERRATUM_C2.md:298–300` and `:379` | "every hand-maintained tally has been deleted from prose … and prose does not" | `README.md:89`, `:91`, `:95` and `ERRATUM_C2.md:25`, `:43` are hand-maintained prose counts; `:95` was added by this commit. **FAIL 2 / note 3** |

**Surviving instance — ambiguous, capable of being read false (1):**

| # | site | claim | status |
|---|---|---|---|
| **S3** | `ERRATUM_C2.md:262` | "exactly nine leaves have ever changed in this campaign" | true of the artifact, false campaign-wide, contradicts the ledger on the wider reading. **Note 4** |

**Corpus claims I checked and found sound (9)** — recorded so a twelfth round need not re-derive them:

| # | site | claim | how I checked it |
|---|---|---|---|
| V1 | `ERRATUM_C2.md:27`, `README.md:95` | r5, r6, r7 and r8 each diffed every leaf of `C2_D1_BLOCKER.json` across its whole history; r9 did not | read all ten review files; the four record it at the lines cited in checklist row 1, r9 records only a one-pair diff |
| V2 | `ERRATUM_C2.md:48` | "`evidence/registry_c2/` has one commit in its history" | `git log --all` → `5a94568a` only, for the directory and for each of its 76 files |
| V3 | `ERRATUM_C2.md:372–373` | "no build-host record exists anywhere in C2's `evidence/` or `config/`" | enumerated all 50 distinct registry key paths and all host records in `evidence/`+`config/`; both are re-certification/verification hosts |
| V4 | `C2_RECERTIFY_306.json.host.note`, `CELL_306_ADOPTION.md`, N10 | "the registry's build host is not recorded anywhere in this repository" | no file outside this namespace mentions the C2 registry at all |
| V5 | `ERRATUM_C2.md:350` | the artifact's bytes contain no fragment of the docstring | tokenised the docstring, searched all 6- and 8-word runs against the raw bytes: 0 hits |
| V6 | `ERRATUM_C2.md:4` | "this document dispositions every FAIL from every one of them" | 27 disposition rows against 27 FAILs in the round table |
| V7 | `README.md:3` | "Nothing outside this namespace is modified" | 141 A, 0 M, 0 D since `5289b6ce`, all in-namespace |
| V8 | `OPEN_NOTES…:81`, `CELL_306_ADOPTION.md:98` | "no campaign has built [a second, independently written certifier]" | previously checked by r2 and r7; no contrary artifact in the repo |
| V9 | `R_STAGE_DESIGN.md:60` | "the C1 column, which nothing else in the programme has ever computed" | `grep -rl` for the critical-ratio keys over the repo returns only this namespace and Campaign B's Lemma-G file |
| V10 | `CELL_306_ADOPTION.md:47–48` | the in-repo corroboration is "the one identified", not "the only" | the narrowing is in place and the two figures are in the artifacts named |

**On why the class keeps surviving.** r10 diagnosed it as one-corpus-per-round and prescribed a single sweep.
This round did sweep more corpora than any before it, and V1–V10 are the proof: nine independently checkable
universals, all sound, several of them genuinely hard. What it did not do is apply the rule to the **two new
sentences the sweep itself wrote** — the ledger's scope line and the compliance line the r6 row still carries.
The pattern has therefore not changed shape at all: a correct primary argument with an unverified sentence
stacked on top of it, which is exactly what `ERRATUM_C2.md:453` says a successor should expect. The register at
`:384` should gain a row for round 10: *wrote the replacement ledger to close the class → gave it a scope it had
not checked.*

---

## What I did not check

- **The Arb/FLINT passes.** I did not use the FLINT venv and recomputed no certified constant. Determinism and
  safe-side results are trusted on the artifact, my leaf-stability diff across all three of its commits, and ten
  prior reviews.
- **Anything on a remote host.** AWS was not touched; `rebaseguard-vultr` was not contacted. N10's build-log
  premise is unverified by me, as it was by r8, r9 and r10.
- **The underlying K5-B / TC-T mathematics.** I verified that the committed producers reproduce their artifacts
  byte-for-byte, not that the mathematics is correct.
- **`code/c2_b0_verify.py` and `code/c2_refined_registry.py`** beyond confirming they are unchanged in this diff
  and reading `c2_refined_registry.py`'s comments for the corpus sweep. I did not re-run B0.
- **`evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json`** beyond confirming it is single-commit.
- **`D_PRIME_OPPORTUNITY.md`'s counter-combination arithmetic (N7).** Read, not recomputed.
- **Reviews r1–r4 end to end.** I read r10 in full and r1–r9 by targeted search — for checklist rows 1 and 2, by
  searching each of r1–r10 for its leaf-diff work specifically, and for row 27 by history rather than content.
- **Predecessor namespace contents.** I established only that no path outside the C2 namespace changed since
  `5289b6ce`, and that nothing outside it references the C2 registry.

---

## Verdict counts

| | |
|---|---|
| rows | 36 |
| PASS | 30 |
| PARTIAL | 1 |
| NOTE | 3 |
| **FAIL** | **2** |
| notes | 6 |

**VERDICT: NOT_READY.**

Both FAILs are textual and both are the same class. The science is untouched and, for the eleventh consecutive
round, independently reproduced: three producers byte-identical, `D_PARTIAL`, closed {305, 306}, the gap falls and
both Γ exact, recertification `BOTH_PASSES_OK` at 45/45 and both precisions, 43/43 mutants with 0 undetected. The
integrity envelope is clean: 141 additions and nothing else since `5289b6ce`, the gate frozen at one commit and
byte-exact, `main` untouched, coverage map r4 intact with no r5, no lifecycle artifact pre-empting anything, and
all ten prior reviews committed and unedited. Two of r10's three FAILs are fully repaired and the third is
repaired in substance.

**The namespace is not yet fit to freeze**, and the reason is narrow: freezing now would freeze a provenance
ledger whose first sentence is false under its own regeneration command, and a claim that the namespace's prose
carries no hand-maintained counts in a commit that added one. Both repairs are small and neither touches evidence.
If the campaign makes them, it should make only them, run the ledger loop over the whole evidence tree first, and
put the resulting command output in the text — including for the sentence that says the sweep is complete.

**On the calibration.** I think it is right, and I applied it as written. Neither finding is style: S1 is a false
universal in the instrument the campaign built this round to establish evidence provenance, and S2 is a false
statement about a remediation that blocked three earlier rounds. I considered filing both as NOTEs — the
underlying facts are disclosed elsewhere in the same document, and no adjudicable quantity moves either way — and
concluded that a provenance ledger which is wrong on first regeneration, and a compliance claim falsified by the
commit asserting it, each meet the bar for misleading an adjudicator about evidence provenance and about the
campaign's reliability. I did not withhold a ready verdict for want of one: if these two sentences are repaired
and nothing else is disturbed, I see nothing else in this namespace that should block a freeze.
