# Fourth independent pre-freeze review — K5 Campaign C2

**VERDICT: NOT_READY** — 36 rows, 28 PASS, 5 NOTE, **3 FAIL**. Three freeze-blocking defects, all text or
metadata, none touching a computed number. **Yes, the repair introduced a new error again**, and it is the one
thing this round was asked to look for: the extra sensitivity field C2 added beyond what r3 requested,
`gain_per_unit_of_input_moved`, **reverses the D_lo-vs-τ ordering on all five cells** — the single finding
`D1_BLOCKER_DIAGNOSIS.md` §2 says "the whole section rests on" — and it does so inside the frozen
machine-readable artifact with no caveat anywhere.

## Reviewer context

Fresh context. I wrote none of this work and had no part in rounds one to three. Worktree
`/Users/suzhe/ReBaseGuard-k5c2`, branch `p5y-k5-tail-c2`, HEAD `17123368`, reviewed 2026-09-21. Read-only
throughout: no file in the namespace was modified except this one, and no writing git command was run. AWS/PS1
was not touched.

**What I re-derived myself, from source, not accepted from any earlier review:** all three producers re-run and
diffed byte-for-byte against their committed artifacts; the complete leaf-level diff of `C2_D1_BLOCKER.json`
against both `ef58310c` and `55c4cf00`, by key, with counts; the exact operator constants for all five cells from
`REGISTRY_C1.json` as `Fraction`s, and from them `max D_lo × 1.1`, the `C_T` headroom on every cell, and which
branch of `min(Ā, τ/D_lo)` binds; the five `effective_improvement` and five
`gain_per_unit_of_input_moved` figures for `C_T` and the same for `D_lo` and `τ`; an original experiment r3 did
not run — the `C_T` response recomputed at a *common admissible cut* (1 %, 3 %, 6 %) and as a marginal slope at
zero, to test whether the "flat and slightly rising" reading is an artifact of unequal perturbation windows;
`deflated_consume.py` lines 83–109 read directly; the `taboo_certify.py` pin; a FLINT re-certification of two of
cell 306's artifacts on the venv build, both passes, field by field against the committed record; the leaf diff
of `C2_RECERTIFY_306.json` across `8aee1fc5..55c4cf00`; and every integrity check in §4 of my brief.

**What I took on trust:** the three committed reviews' accounts of what *they* verified in rounds one to three,
except where I re-derived it above; C1's and Campaign B's upstream evidence, which I treated as given inputs.

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| **r3 FAIL 6 and its acted-on NOTEs** |
| 1 | is the present-tense ×0.9 claim gone from `ERRATUM_C2.md`? | PASS | yes. `ERRATUM_C2.md:82–87` now reads "**A further claim made here in the first repair round has since been withdrawn**… It is not, because ÷1.1 does the same thing on the same three cells", and forward-references the r2 FAIL 65 row. The self-contradiction r3 found is gone |
| 2 | is the replacement text accurate? | PASS | yes on both halves. ÷1.1 does drive `C_T` under τ on 307/308/309 (I recomputed the headroom: 8.9966 / 7.4903 / 6.0997 %, all < 9.0909 %), and 305/306 are unaffected (12.2376 / 10.5844 %). "The only surviving reason to prefer ÷1.1 is symmetry in A0 = τ/D_lo" matches `D1_BLOCKER_DIAGNOSIS.md:51–58` |
| 3 | namespace sweep — does the withdrawn ×0.9 claim survive anywhere else? | PASS | swept `*.md`, `*.py`, `*.json` outside `review/`. Six hits, every one either the withdrawal itself or a disposition row. No surviving assertion |
| 4 | namespace sweep — does the **"refuses exactly as"** overclaim survive anywhere? | **FAIL** | **yes — `code/c2_d1_blocker.py:62–65`, untouched by this diff.** See note 1 |
| 5 | does the withdrawn "not a bound anyone relies on" wording survive? | PASS | no. Corrected in `code/c2_recertify_306.py`'s `DIAGNOSTIC_NOTE` and, byte-for-byte, in the committed JSON string `/diagnostic_policy/why` — I diffed the leaf directly across `8aee1fc5..55c4cf00` |
| 6 | is the "cap of 1" analogy withdrawn from both documents? | PASS | yes. The only surviving hit outside `review/` is the code's own `clamped = "D_lo capped at 1"` string, which is a live branch label, not a claim |
| 7 | do the old inadmissible figures survive anywhere unlabelled? | PASS | `+1.3823 / +1.3945 / +1.3887` appear twice outside `review/` (`D1_BLOCKER_DIAGNOSIS.md:70`, `ERRATUM_C2.md:134`), both explicitly labelled superseded |
| 8 | is the stale `62531bf5…` sha gone? | PASS | `D1_BLOCKER_DIAGNOSIS.md:3` and `ERRATUM_C2.md:134` both now cite `601f2f33…`, which is the sha my own re-run produced |
| **the new sensitivity fields** |
| 9 | is `eff = abs(p[name] − op[name]) / op[name]` the right quantity per row? | PASS as *defined* | it is exactly "the fraction of the input moved", and the code comment says so. 1/11 = 9.0909 % for the four upper bounds, 1/10 = 10 % for `D_lo`, less where a clamp bound the move. Arithmetically correct on all 25 rows |
| 10 | is `D_lo`'s 10 % against everyone else's 9.0909 % consistent with the ÷1.1 convention? | PASS, and it is *not* misleading as a standalone field | the asymmetry is the convention working as designed. τ ÷ 1.1 and `D_lo` × 1.1 each divide A0 = τ/D_lo by exactly 1.1 — equal effect on A0, unequal fractions of the input. `D1_BLOCKER_DIAGNOSIS.md:40–43` states precisely this. `effective_improvement` is correctly named and correctly computed |
| 11 | …but is it safe to use that field as a **denominator** to compare rows? | **FAIL** | **no.** `gain_per_unit_of_input_moved` divides `D_lo` by 0.1 and τ by 0.0909…, discarding the A0-symmetry the convention exists to preserve, and **inverting the ordering on all five cells**. See note 2 |
| 12 | do the published per-unit `C_T` figures reproduce? | PASS | 0.14958426 / 0.15038680 / 0.15206656 / 0.15355479 / 0.15304176 → 0.1496 / 0.1504 / 0.1521 / 0.1536 / 0.1530. Exact match to the document and to r3's table |
| 13 | do the published admissible cuts reproduce from the registry? | PASS | computed as (C_T − τ)/C_T in exact rationals: 9.090909 / 9.090909 / 8.996561 / 7.490255 / 6.099651 %. Document's 8.997 / 7.490 / 6.100 and the brief's 8.9966 / 7.4903 / 6.0997 both round correctly |
| 14 | is "C_T is nearly exhausted, 6.1 % of travel left" correct? | PASS — **the campaign is right** | headroom at 309 is 6.099651 %, and the `C ≥ τ` premise is what stops it. The substantive reading r3 supplied and C2 adopted is sound |
| 15 | is "per unit the response is flat" an artifact of the unequal windows? | PASS — **the campaign is right, and I tested this specifically** | recomputed at a *common* cut admissible on every cell: at 6 % → 0.149896 / 0.150696 / 0.152366 / 0.153702 / 0.153051; marginal slope at 0 → 0.150501 / 0.151297 / 0.152965 / 0.154292 / 0.153622. The window difference moves each figure by < 0.0009 against a cross-cell spread of 0.0034, and changes no ordering. The shape is genuine |
| 16 | is "slightly **rising** across the tail" exactly right? | NOTE | it rises 305→308 then **falls** at 309 (0.153702 → 0.153051 at a common 6 % cut; 0.154292 → 0.153622 at the margin). Non-monotone. The document prints all five numbers so a reader sees it. Note 4 |
| 17 | is "for the same structural reason τ cannot fall: A0 = τ/D_lo ≥ τ" sound? | NOTE | its two factual components check out — `min(Ā, τ/D_lo)` takes the `τ/D_lo` branch on **all five** cells, and D_lo ≤ 1 so τ/D_lo ≥ τ — but the clause is a non-sequitur as support for `C_T`'s headroom collapse, and τ falls 16.5 % across the tail. Finding 3 states the argument correctly; the ◆ note's restatement garbles it. Note 5 |
| 18 | are the new fields added "on every row"? | NOTE | no — 5 of 11 rows per cell (`C_T`, `D1`, `D2`, `D_lo`, `tau`); `A0`, `A1`, `A2`, `A_all`, `rho_frozen`, `C_upper_frozen` have neither. Harmless (the four A rows are all unclamped at 9.0909 %) but the claim is false as written. Note 3 |
| **claims C2 says it verified at source** |
| 19 | max `D_lo` × 1.1 across the tail = 0.932851, so the `D_lo` cap never executes? | PASS — **verified independently, exact** | `0.932850929487011` at cell 309; the five values are 0.845470 / 0.869982 / 0.891423 / 0.911759 / 0.932851, all < 1. `p["D_lo"] > 1` is false on every cell and no `D_lo` row carries an `admissibility_clamp` key |
| 20 | does `deflated_consume.atom_constants` type-check its inputs? | PASS — **verified at source** | `deflated_consume.py:85–89`: `isinstance(v, F)` and `v >= 0` on each of τ, C, D_lo, D1, D2, k1, k2, raising `DeflationRefusal` |
| 21 | does `atom_constants_r2` post-check r2 ≤ r1? | PASS — **verified at source** | `deflated_consume.py:106–108`: raises if `out[j] > base[j]` for any j ∈ {A0, A1, A2}. It also adds the `Ā ≥ 1` test at line 100–101 |
| 22 | is the new guard description ("four premise inequalities … not byte-for-byte") accurate in the two prose files? | PASS | the guard tests `Dlo > 0 and tau >= 1 and C >= tau and Abar >= 1` — four, matching what the `atom_constants` / `atom_constants_r2` path validates, minus the type checks and the post-condition, exactly as stated |
| 23 | …and in the source comment? | **FAIL** | no — see row 4 and note 1 |
| 24 | leaf diff vs `ef58310c`: nine values changed, C_T `magnitude`/`delta_vs_base`/`relative_gain` on 307/308/309? | PASS | exactly nine, exactly those keys, exactly those cells |
| 25 | three `admissibility_clamp` strings added, nothing removed? | PASS | 3 added, 0 removed across `ef58310c..HEAD` and `55c4cf00..HEAD` |
| 26 | "53 further leaves added this round"? | NOTE | **50**, not 53. 25 `effective_improvement` + 25 `gain_per_unit_of_input_moved`. 53 is the *total* added since `ef58310c`, which already counts the three clamp strings the same sentence counts separately. Note 3 |
| **determinism and integrity** |
| 27 | `c2_d1_blocker.py` reproduces byte-for-byte? | PASS | my run: `sha256 601f2f337f466a86221ebe680983f7e4dbb9dcd6b8768bd07ee0a16d79702b0f`, `cmp` clean against the committed artifact |
| 28 | `c2_mutations.py` reproduces byte-for-byte, 43/43, 0 undetected? | PASS | `cmp` clean. `applied 43` = 35 real mutants + 8 static assertions; `detected 40`, `equivalent 3` (`M19`, `M20`, `M32`), **`undetected []`**, `pass true`, `sha256 512180f3…` |
| 29 | `c2_critical_ratio.py` reproduces byte-for-byte? | PASS | `cmp` clean |
| 30 | `C2_RECERTIFY_306.json` verdict `BOTH_PASSES_OK`? | PASS | verdict `BOTH_PASSES_OK`, 18 artifacts, `registry_sha_pin_ok true`, `taboo_sha256 ced9422c…` — and I confirmed that pin against the live `p5y_k5_perron_deflated_resolvent/code/taboo_certify.py` |
| 31 | FLINT spot-check of at least one artifact | PASS | **two**, on the venv build (macOS 26.5.2 / arm64 / Python 3.14.5 / numpy 2.5.3 / python-flint 0.9.0). `taboo_block_306_04` (6 fields) and `taboo_cell_306_07` (7 fields), both at 256 bits strict and 384 bits safe-side: `certified=True`, `ok=True`, and every recomputed value **string-identical** to the committed record |
| 32 | the r3 re-execution credit — "~40 minutes, every field but the note and two `cpu_seconds` bit-identical" | PASS — **verified, and it is a fair credit** | leaf diff `8aee1fc5..55c4cf00`: 1224 leaves, **3 changed** — `/diagnostic_policy/why` and the two `cpu_seconds`. 1153.9 + 1204.2 s = 39.3 min |
| 33 | `git diff --name-status 5289b6ce..HEAD` all additive, all in-namespace? | PASS | 134 entries, every one `A`, every one under `p5y_k5_tail_c2_closure/` |
| 34 | gate still sha `098dd7f5…`, still one commit? | PASS | `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`; `git log -- config/FEASIBILITY_GATES_C2.json` returns exactly `87309610` |
| 35 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmodified since `5a94568a`? | PASS | `git diff 5a94568a..HEAD` on both paths is empty. The class, closed set and gap falls have not moved |
| 36 | predecessors, `main`, coverage map r4, no r5, nothing pre-empting the chain? | PASS / **FAIL on the README** | predecessor namespaces byte-unchanged; `main` at `c123b9bb` is an ancestor of HEAD with 0 commits ahead; `K5_COVERAGE_MAP_R4.json` untouched and no r5 exists; the pre-emption sweep is clean (the only "frozen" hit outside `review/` is `ERRATUM_C2.md:40`, a true statement about the gate). **But `README.md` has not been touched since `12585997` and is now materially stale** — note 3 covers the counts; see note 6 |

## Notes

### Note 1 (FAIL) — the withdrawn overclaim still stands in the source, and the erratum says it was "corrected in both places"

`ERRATUM_C2.md:165–168` disposes of r3's note 2:

> **"Refuses exactly as `deflated_consume.atom_constants` does" overclaimed.** … Corrected in both places.

r3's note 2 named the places explicitly: "`ERRATUM_C2.md:131` says the local copy 'now refuses exactly as
`deflated_consume.atom_constants` does', **and the in-code comment says the same**." C2 corrected
`ERRATUM_C2.md` and `phase_d/D1_BLOCKER_DIAGNOSIS.md`. The in-code comment is untouched — the diff of
`c2_d1_blocker.py` across `55c4cf00..17123368` touches only the `sens` block at lines 195–205. It still reads,
verbatim, at lines 62–65:

```
# The pinned consumer `deflated_consume.atom_constants` refuses unless these hold; this local copy did not,
# and so would happily return constants for an inadmissible tuple. … The guard is added so the two agree.
```

Both of r3's inaccuracies survive there intact. It names `atom_constants`, which does **not** enforce `Ā ≥ 1` —
that test comes from `atom_constants_r2` alone, and the guard on the very next line does include it, so
"refuses unless these hold" is literally false of the function named. And "the guard is added so the two agree"
is the "refuses exactly as" overclaim restated: the two do not agree, the guard having neither the type checks
nor the `r2 ≤ r1` post-condition.

This is the same defect as r3 FAIL 6 — a claim withdrawn in the prose and left standing elsewhere — one round
later, and this time with the errata register affirmatively asserting the correction is complete when it is not.
Nothing numeric depends on it; r3 established that the guard is equivalent on this input set. It is
freeze-blocking because the errata register is the document whose whole purpose is to be a true account of what
was corrected, and freezing makes the untruth permanent.

**To repair:** rewrite the comment to name `atom_constants_r2` and drop "so the two agree" (r3 offered wording),
or narrow the erratum's "both places" to the two it actually means and add the third. Either is a two-line edit
and neither regenerates evidence — `c2_d1_blocker.py`'s output does not depend on its comments, and I confirmed
the artifact reproduces byte-for-byte as committed.

### Note 2 (FAIL) — `gain_per_unit_of_input_moved` inverts the D_lo-vs-τ ordering on every cell

This is the new error, and it is the extra field.

r3's note 3 recommended one thing: add the effective cut to each clamped row, "`"effective_improvement":
0.060996…` is one line". Its own per-unit table was confined to `C_T` across cells — a *within-lever*
comparison, which is sound, and which I confirmed independently at a common cut (row 15). C2 added
`effective_improvement`, correctly, and then added a **second field r3 never asked for and never checked**,
`gain_per_unit_of_input_moved = relative_gain / effective_improvement`, on all five operator-input rows. It was
not checked against the rest of the table.

It ranks τ above `D_lo` on all five cells. `relative_gain` ranks `D_lo` above τ on all five:

| cell | `relative_gain` D_lo | `relative_gain` τ | order | per-unit D_lo | per-unit τ | order |
|---|---|---|---|---|---|---|
| 305 | 0.086029 | 0.080181 | D_lo > τ | 0.860291 | **0.881996** | **τ > D_lo** |
| 306 | 0.086305 | 0.080600 | D_lo > τ | 0.863046 | **0.886600** | **τ > D_lo** |
| 307 | 0.086729 | 0.081020 | D_lo > τ | 0.867294 | **0.891220** | **τ > D_lo** |
| 308 | 0.087159 | 0.081459 | D_lo > τ | 0.871589 | **0.896053** | **τ > D_lo** |
| 309 | 0.087186 | 0.081681 | D_lo > τ | 0.871859 | **0.898489** | **τ > D_lo** |

**Why it flips, and why the flip is spurious.** The entire flip is the factor 1.1 and nothing else. `D_lo`'s gain
is divided by 0.1 and τ's by 1/11. But `D1_BLOCKER_DIAGNOSIS.md:40–43` states the convention's rationale in
terms: "τ, C_T, D1, D2 and each A_j are **divided** by 1.1; D_lo is **multiplied** by 1.1. That is the convention
under which A0 = τ/D_lo responds symmetrically to its two factors, **which is why it was chosen**." Each of the
two perturbations divides A0 by exactly 1.1 — that is the "unit" the convention defines, and the two input
fractions differ *because* the A0 effects are equal. Dividing by the input fraction throws that away. Normalise
`D_lo` by the same A0 effect (divide by 1/11 rather than 1/10) and the ordering is restored on every cell, by a
wider margin than `relative_gain` shows:

| cell | 305 | 306 | 307 | 308 | 309 |
|---|---|---|---|---|---|
| D_lo, per equal A0 effect | 0.946320 | 0.949350 | 0.954024 | 0.958748 | 0.959045 |
| τ | 0.881996 | 0.886600 | 0.891220 | 0.896053 | 0.898489 |

**Why it is freeze-blocking.** The ordering it reverses is not incidental. `D1_BLOCKER_DIAGNOSIS.md:43–48` puts
it in bold — "**The ordering does not change:** D_lo outranks τ under both conventions, on every cell" — and
adds "Recomputed here rather than accepted, **because it is the finding the whole section rests on**." Finding 1
is "D_lo and τ are the only operator levers that matter." This is the exact point r1 attacked, C2 defended, and
r2 independently confirmed C2 was right about. C2 has now published, into the machine-readable artifact an
adjudicator reads, a column that says the opposite on all five cells — and the erratum's justification for the
field is precisely cross-row comparability: "`effective_improvement` and `gain_per_unit_of_input_moved` are now
recorded per row **so the columns cannot be misread as like-for-like**." The field does not achieve that for
`D_lo` versus τ; it manufactures a new not-like-for-like reading that inverts the section's central finding.
There is no caveat on it anywhere — the only two prose mentions of the field, `ERRATUM_C2.md:134` and
`D1_BLOCKER_DIAGNOSIS.md:77`, discuss `C_T` alone.

To be clear about what is *not* wrong: every number in the column is arithmetically correct, the field is
literally what its name says, and the `C_T`-across-cells reading C2 drew from it survives my independent
common-cut test (row 15). The defect is that a cross-lever quantity was published without being checked against
the cross-lever finding the same document rests on.

**To repair**, any one of: (a) drop `gain_per_unit_of_input_moved` and keep `effective_improvement`, which is
what r3 asked for and is sufficient for the `C_T` point; (b) normalise it by the A0 effect rather than the input
fraction, which preserves the ordering; or (c) keep it and add an explicit caveat, in both the artifact and §2,
that the field is meaningful *within* a lever across cells and **not** between levers, because the ÷1.1
convention deliberately makes the two input fractions unequal. (a) or (b) require regenerating
`C2_D1_BLOCKER.json` and re-citing its sha in two places; (c) does not.

### Note 3 (NOTE, non-blocking) — the leaf-diff restatement is off by three, and "on every row" is false

`ERRATUM_C2.md:134` says: "plus three `admissibility_clamp` strings added — the twelve r3 verified. The present
round adds `effective_improvement` and `gain_per_unit_of_input_moved` on every row (**53 further leaves**)".

Measured: `ef58310c` 487 leaves → HEAD 540. Added 53, of which 3 are the clamp strings the same sentence has
already counted. The present round adds 25 + 25 = **50**. Check: 487 + 3 + 50 = 540 ✓; 487 + 3 + 53 = 543 ✗. And
`55c4cf00` → HEAD, which is exactly "the present round", is 490 → 540: added 50, changed 0, removed 0.

"On every row" is also false: 5 of the 11 rows per cell carry the new fields. `A0`, `A1`, `A2` and `A_all` are
also ×10/11 perturbations and have neither field (harmlessly — they all sit at 9.0909 %); `rho_frozen` and
`C_upper_frozen` are not perturbations at all. `D1_BLOCKER_DIAGNOSIS.md:77` carries the same imprecision
("recorded per row").

Non-blocking on its own — but I record it because it falls in the paragraph where C2 writes "It also corrected
its own restatement of r3's leaf-diff count before a reviewer had to." The corrected restatement is itself wrong
by three, in the same sentence that claims the correction.

### Note 4 (observation) — "slightly rising" is non-monotone

Per unit, `C_T`'s response rises 305 → 308 and then falls at 309: 0.1496, 0.1504, 0.1521, **0.1536**, 0.1530.
This is not a window artifact — at a common 6 % cut it is 0.149896 / 0.150696 / 0.152366 / **0.153702** /
0.153051, and at the margin 0.150501 / 0.151297 / 0.152965 / **0.154292** / 0.153622. The load-bearing word is
"flat", which is right (the whole spread is 2.8 % of the value); "rising" holds 305→309 endpoint to endpoint but
not step by step. The document prints all five figures, so no reader is deceived. Cosmetic.

### Note 5 (observation) — the ◆ note's closing clause does not support what it is attached to

> "…for the same structural reason τ cannot fall: A0 = τ/D_lo ≥ τ, and τ bounds a genuine expected hitting time."

Both factual components are true, and I checked them rather than assuming: `A0 = min(Ā, τ/D_lo)` takes the
`τ/D_lo` branch on **all five** cells (Ā = 8.290719…6.900983 against τ/D_lo = 6.884064…5.210202), and D_lo ≤ 1
on all five, so τ/D_lo ≥ τ. But the inference does not follow. `C_T`'s headroom collapses because the Lemma Dv′
*hypothesis* `C ≥ τ` is a floor and `C_T` approaches τ along the tail — a fact about the constraint, which would
bind whether or not τ were irreducible. "A0 = τ/D_lo ≥ τ" is a statement that τ floors **A0**, which is finding
3's argument and is correct there; it says nothing about the `C_T` − τ gap. And "τ cannot fall" sits awkwardly
beside the tail data, where τ falls 16.5 % from 305 to 309 (5.291155 → 4.418493) — the intended sense is
evidently "cannot be argued down", but the sentence does not say so.

This is the named pattern in attenuated form: a correct primary claim (`C_T` is nearly exhausted, 6.1 % of
travel left — which I confirm) carrying a borrowed supporting clause that was not checked against what it is
being used to prove. Finding 3, four lines down, makes the τ argument properly and does not need this. Not
freeze-blocking; I would simply end the ◆ note at "…before C_T meets τ and Lemma Dv′ stops applying."

### Note 6 (FAIL) — the README is two review rounds stale, and says no published number changed

`README.md` has not been touched since `12585997`, which predates `ef58310c`, `55c4cf00`, `d6a4def5` and
`17123368`. It is the namespace's front door and the first thing a cold adjudicator reads. It currently states:

| independent pre-freeze review | `review/REVIEW_C2_PREFREEZE.md` | **NOT_READY** — 60 PASS / 10 INFO / 3 N/A / 6 FAIL |
| erratum and review disposition | `ERRATUM_C2.md` | all six FAILs dispositioned |

There have been **three** reviews, not one, and **ten** FAILs, not six (6 + 3 + 1). `REVIEW_C2_PREFREEZE_R2.md`
and `REVIEW_C2_PREFREEZE_R3.md` are committed in the same directory and the README mentions neither. The prose
paragraph below the table compounds it: "It reproduced every published number bit-exactly and found no
arithmetic error… All are dispositioned; **no published number changed**." Scoped to r1's six findings that
sentence is true. Read as the namespace's summary of its own review history — which is how a state table reads —
it is false: r2 FAIL 66 changed **nine** published values in `C2_D1_BLOCKER.json` at `55c4cf00`, which is the
single most consequential thing any of the four reviews produced.

I weighed calling this a NOTE. It is the weakest of the three FAILs and reasonable reviewers could downgrade it.
I did not, because the defect is precisely that an adjudicator reading cold would be told the namespace survived
one review with no number moving, when it survived three and nine numbers moved — and freezing fixes that in
place. The fix is one table row and one sentence, with nothing to recompute.

### Note 7 (observation) — `OPEN_NOTES_DISPOSITION_C2.md` is stale in the same way, harmlessly

Last touched at `12585997`. Its heading "Notes opened by the C2 pre-freeze review" is singular and its N6–N9 are
r1's. The content remains accurate — r2 and r3 opened no new *successor obligation*, only repairs — so this is
presentational. Worth folding into the same edit as note 6.

### Note 8 — where the campaign is right, plainly

I want this on the record, because three of my rows are FAILs and the balance matters.

The `C_T` correction chain is sound and well disclosed. The decision to clamp to `C_T = τ` is right. The
substantive reading C2 adopted from r3 — that `C_T` is nearly exhausted rather than weak — is **correct**, and I
tested it harder than r3 did, at a common admissible cut and at the marginal slope, specifically looking for the
"it's an artifact of the smaller window" refutation. It is not an artifact. Both claims C2 says it checked at
source before restating them are **true**, exactly as stated, to the digit. The three producers reproduce
byte-for-byte on a fourth independent run; the mutation suite is 43/43 with zero undetected; two of cell 306's
artifacts re-certify field-identically on the FLINT build, at both precisions, under a verified `taboo_certify`
pin; the frozen gate, the D5 forecast, the predecessor namespaces, the coverage map and `main` are all exactly
where they were. The diff is 134 files, all additive, all in-namespace. Nothing anywhere pre-empts freeze,
qualification, sealing or adjudication.

And the campaign's self-diagnosis in "The pattern, named" is accurate and unusually honest. It simply did not
stop the pattern: the instruction it wrote for its successor — "treat any sentence beginning 'a further reason'
as unverified until it is checked" — needed to extend to *any quantity added beyond what the review asked for*,
which is what note 2 is.

## What I did not check

- I did not re-derive rounds one to three. Where I depend on them I re-derived the specific fact myself; where I
  do not, I relied on the committed reviews. In particular I did not re-verify r3's row 22 sweep of `taboo_certify.py`
  for the two rewritten `DIAGNOSTIC_NOTE` claims, nor r2's 105/105 registry verification.
- I re-certified **2 of cell 306's 18 artifacts** on FLINT, not all 18, and none of cells 305, 307, 308, 309. The
  full registry is ~2.7 h. I did not attempt an independent implementation of the Arb supersolution machinery —
  that is N9, and it remains the residual trust surface.
- I did not re-derive the twelve-term radius decomposition, the blocker shares, the `order3_attribution`
  counterfactual, the D5 forecast's componentwise minimum, or the critical-ratio columns, beyond confirming that
  all three producers reproduce their artifacts byte-for-byte and that the D5 files have not moved since
  `5a94568a`.
- I did not assess the R-stage design, the `D_PRIME_OPPORTUNITY` finding, or whether `D_PARTIAL` is the right
  class — all settled in earlier rounds and untouched by this diff.
- I did not check upstream: C1's registry, Campaign B's measurements and the cover ledger were taken as given.
- I did not touch AWS/PS1, and I ran no writing git command.

## Verdict counts

**NOT_READY** — 36 rows: **28 PASS, 5 NOTE, 3 FAIL.**

Freeze-blocking, in order of consequence:

1. **Note 2** — `gain_per_unit_of_input_moved` reverses the D_lo-vs-τ ordering on all five cells, contradicting
   the finding §2 says the whole section rests on, in the frozen machine-readable artifact, uncaveated.
2. **Note 1** — the withdrawn "refuses exactly as `atom_constants`" claim survives verbatim in
   `code/c2_d1_blocker.py:62–65`, while `ERRATUM_C2.md:165` states it was "corrected in both places".
3. **Note 6** — `README.md` advertises one review of three and six FAILs of ten, and says no published number
   changed when nine did.

Non-blocking: notes 3, 4, 5, 7.

**On the substance, plainly:** every computed number in this namespace that I checked is correct, and I checked
a lot of them. All three defects are text or metadata. Two of the three need no recomputation at all; the third
needs a regenerated `C2_D1_BLOCKER.json` and two sha citations **only if** C2 chooses to remove or renormalise
the field rather than caveat it. This is a campaign whose arithmetic has been right in every round and whose
prose has been wrong in every round, and the fourth round is the same story: the primary repair was correct and
the decoration on top of it was not. I would expect a fifth round to be short.

---

*Fourth independent fresh-context pre-freeze review. Worktree `/Users/suzhe/ReBaseGuard-k5c2`, branch
`p5y-k5-tail-c2`, HEAD `17123368`, reviewed 2026-09-21. Read-only throughout: no file in the namespace was
modified except this one, and no writing git command was run.*
