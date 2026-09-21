# Campaign C2 — erratum, and the disposition of the independent pre-freeze reviews

Independent fresh-context pre-freeze reviews have run on this campaign in successive rounds, each so far
returning **NOT_READY**, and this document dispositions every FAIL from every one of them. The table below is the
count. Counts belong in the tables of this document and of `README.md`, not in prose — for the reason given in
§"The pattern, named".

| round | at | verdict | dispositioned in |
|---|---|---|---|
| r1 | `5a94568a` | 6 FAIL | §§ below, through "The finding that outranks all of the above" |
| r2 | `ef58310c` | 3 FAIL | § "Dispositions from the SECOND pre-freeze review" |
| r3 | `55c4cf00` | 1 FAIL | § "Dispositions from the THIRD pre-freeze review" |
| r4 | `17123368` | 3 FAIL | § "Dispositions from the FOURTH pre-freeze review" |
| r5 | `1663f558` | 2 FAIL | § "Dispositions from the FIFTH pre-freeze review" |
| r6 | `ec5b08ca` | 1 FAIL | § "Dispositions from the SIXTH pre-freeze review" |
| r7 | `5a098ec6` | 2 FAIL | § "Dispositions from the SEVENTH pre-freeze review" |
| r8 | `07c0b991` | 3 FAIL | § "Dispositions from the EIGHTH pre-freeze review" |
| r9 | `5609358f` | 3 FAIL | § "Dispositions from the NINTH pre-freeze review" |
| r10 | `575919cb` | 3 FAIL | § "Dispositions from the TENTH pre-freeze review" |
| r11 | `87004e2b` | 2 FAIL | § "Dispositions from the ELEVENTH pre-freeze review" |
| r12 | `6aa2040a` | 2 FAIL | § "Dispositions from the TWELFTH pre-freeze review" |
| r13 | `92bc9637` | 3 FAIL | § "Dispositions from the THIRTEENTH pre-freeze review" |

**The result has never moved.** In every round so far, no Γ, magnitude, margin, requirement, gap fall, class or
adopted-subset value has changed: the class is `D_PARTIAL`, the closed subset is {305, 306}, and the frozen gate
is byte-untouched at `098dd7f5…`.

**Of the leaves replaced in committed evidence — all of them in the ledger below — one is a scientific or
decision value**: the C_T sensitivity row on cells 307–309 of the D1 diagnosis, corrected to the admissible
perturbation. Reviews r5, r6, r7 and r8 each independently
diffed every leaf of that artifact across its whole history and each found the same nine leaves. One published
*table* was additionally corrected against evidence that never changed: D1 §1's ranking of the three negligible
blocker terms, which named the smallest of them and printed "~0" for the two larger, while the machine-readable
file had said `order0_residual_fF` from the start.

### Replacement ledger

Every leaf this campaign has replaced in an already-committed evidence file. Do not trust this table — regenerate
it, with the loop in `git log --reverse --all -- <file>` diffing consecutive revisions leaf by leaf:

| file | commit pair | leaves replaced | what |
|---|---|---|---|
| `evidence/phase_d1/C2_D1_BLOCKER.json` | `e71378a0 → 55c4cf00` | **9** | C_T `magnitude` / `delta_vs_base` / `relative_gain` on cells 307, 308, 309 — the one scientific change |
| `evidence/prefreeze/C2_MUTATIONS.json` | `5a94568a → 12585997` | **4** | `applied` 33 → 43, `detected` 31 → 40, `real_mutants` 25 → 35, `M10.caught_by[0]` `value` → `tiling` — the r1-requested suite extension, disclosed below |
| `evidence/prefreeze/C2_RECERTIFY_306.json` | `8aee1fc5 → 55c4cf00` | **3** | `diagnostic_policy.why`; `cpu_seconds` 1653.6 → 1153.9 and 1691.8 → 1204.2 |
| `evidence/prefreeze/C2_RECERTIFY_306.json` | `55c4cf00 → 5609358f` | **3** | `host.note`; `cpu_seconds` 1153.9 → 1141.5 and 1204.2 → 1196.1 |

**19 leaves, three files.** The first version of this ledger listed 15 and claimed to list every one; it omitted
`C2_MUTATIONS.json` entirely (r11 FAIL 1). Of the 19, **nine** are the scientific correction, **four** are the
adversarial suite's own counts after it was extended at r1's request, and **six** are free text and wall-clock
timings. **No value of a certified operator constant, of Γ, of a cell magnitude, of a required reduction or of a
gap fall was replaced.** (The D1 row names a field called `magnitude`; it is the magnitude of a *sensitivity probe*
at a perturbed C_T, not a cell's magnitude, and its cell magnitudes are untouched — r12 S3.)

`C2_RECERTIFY_306.json` has therefore been regenerated after a review **twice**, not once. A previous version of
this section recorded only the second, because C2 took r9's premise — "the one place where the campaign rewrote
committed evidence after a review" — without checking it. Inheriting a reviewer's unverified claim is the
campaign's own documented failure mode; it is recorded in the register below and was caught by r10.

Neither regeneration changed a certified value: in both pairs the replaced leaves are free text and wall-clock
timings, nothing was added or removed, and all 18 artifacts stayed `certified: true`. **The `cpu_seconds` cited as
build-host corroboration are not these**: those are 90.248003954 and 88.257109067, per-artifact values inside
`taboo_block_306_02.json` and `taboo_block_305_00.json`, and `evidence/registry_c2/` has one commit in its history.

(An earlier version of this paragraph also said "two published numbers have changed", conflating a value change
with a table correction. Corrected in self-audit; the blocker evidence has never changed.)

The open governance question the campaign ends on is in § "Cell 306", and the finding that matters most for what
happens next is in § "The finding that outranks all of the above".

## Dispositions from the FIRST pre-freeze review

`review/REVIEW_C2_PREFREEZE.md`, at `5a94568a`: **6 FAIL**.
It reproduced every decision-relevant number bit-exactly from an implementation written independently from the
theorem documents, and found no arithmetic error anywhere in C2. What it blocked the freeze on was what would have
been frozen *alongside* the arithmetic. The three sections that follow disposition all six, plus the corrections
that came out of its INFO rows.

### The one thing that cannot be repaired at source

| | |
|---|---|
| **FAIL 6** | `config/FEASIBILITY_GATES_C2.json` → `residual_measure.why_gap_and_not_ratio` is **directionally inverted**. |

The frozen sentence reads: measuring progress as a fraction of the raw requirement *"flatters a cell that is
already nearly closed and penalises one that is far from closing"*. **That is backwards.** Writing Δ for the
absolute fall in a cell's required reduction factor and g₀ = r₀ − 1 for its starting gap:

    gap_fall = Δ/g₀        raw_fall = Δ/r₀        gap_fall / raw_fall = (1 + g₀)/g₀ > 1  always

so the ratio measure always reports the *smaller* number, and the shortfall is **largest** when g₀ is smallest —
that is, for a nearly-closed cell. A cell going from requirement 1.05 to exactly 1.0 has closed completely and
scores 4.8 % on the ratio measure against 100 % on the gap measure. The ratio measure **penalises** the nearly
closed cell; it cannot flatter it. C2's own numbers show it: the distortion factor is 4.82 at cell 307 (g₀ = 0.262)
and only 1.91 at cell 309 (g₀ = 1.102).

**The gate is not amended.** It was frozen at `87309610` before any C2 number existed, and its integrity as a
pre-registration is worth more than the tidiness of one sentence. Amending a frozen gate after a review, even to
fix a true error in its prose, is the precedent this programme must not set. The correction is carried here.

**Nothing decided by the gate changes.** The sentence has two clauses and only the first is wrong; the second — *"a
cell closes when its requirement reaches 1, so the distance above 1 is exactly what remains to be removed"*, and
that the ratio is not scale-correct — is both true and sufficient on its own to justify the measure. The threshold,
the classes and the verdict are unaffected. `phase_d/MEASURE_CHANGE_SELF_AUDIT.md` (written before the review
reported) already states the direction correctly, so C2 had the right direction in one document and the wrong one
in the other; the gate is the copy that is frozen.

### Repaired at source

| | finding | repair |
|---|---|---|
| **FAIL 61** | `phase_r/R_STAGE_DESIGN.md` §2 and `phase_d/D_STAGE_DECISION.md` §5 label a column "under C1 constants". Those are **Campaign B's Lemma-G** values (32.03 / 19.20 / 10.55 = `TAIL_FORECAST_R2.critical_sup_G_over_sup_H_ratio`, a file whose own `premise_supply` says it uses Lemma-G constants). C1 never computed a critical ratio. | Column relabelled; the **true C1 values 34.55795 / 20.93621 / 12.18694** computed and substituted. |
| **FAIL 62** | "C2's deterministic work raised every threshold by 16–34 %" is the improvement over **Campaign B**, two campaigns back, presented under C1's name — a ~2× overstatement of C2's own contribution. | Restated as the true **+8.0 / +11.1 / +16.2 %** over C1, in both documents, with the error described rather than silently corrected. |
| **FAIL 30** | `phase_d/D1_BLOCKER_DIAGNOSIS.md` §1 names f_H as `DOMINANT_BLOCKER_3` and prints "~0" for f_D and f_F; its own JSON says `order0_residual_fF`, and both f_F and f_D exceed f_H. | Table and blocker line corrected to the true order **f_F > f_D > f_H**, with real percentages instead of "~0". The JSON was right; the prose was wrong. |
| **FAIL 51** | Cell 306 was re-certified by re-executing the **same** pinned `taboo_certify` bytes on a different partition, with no host, toolchain or precision recorded — so the Arb supersolution machinery, the one surface no reviewer could check, was never independently exercised. | `code/c2_recertify_306.py` + `evidence/prefreeze/C2_RECERTIFY_306.json`. See below. |
| **FAIL 53** | No margin floor was frozen; C2 is deciding "is 11.2 % enough?" *after* seeing 11.2 %. | Not repairable by C2 — see **Cell 306** below. |

Two further gaps, neither raised as a FAIL, were closed at the same time:

- **The critical ratios had no committed producer.** They were published from an uncommitted scratch script, which
  is how the mislabelling survived in the first place. There is now `code/c2_critical_ratio.py` →
  `evidence/phase_d5/C2_CRITICAL_RATIOS.json`: it computes the ratio under every supply **by name**, runs from
  committed evidence alone on any machine with stdlib Python, and **refuses to emit anything** unless it first
  reproduces Campaign B's Lemma-G column and C2's own published Γ, perfect-candidate Γ and critical ratio
  bit-exactly. Those anchors are what license the new C1 column.
- **The registry's re-verifiability was asserted, not demonstrated** (review row 79) — **and the assertion turned
  out to be false.** Running `c2_refined_registry.py verify`, as the row asked, exposed a defect in C2's own
  verifier: it read the recomputed constants from `got.get("C_T")` when `verify_block` / `verify_cell` return them
  nested under `got["recomputed"]`. Every comparison was therefore `str(None) != "<value>"`, so **the verifier
  reported a mismatch on every field of every sub-block and could never pass** — which is precisely why no run of
  it had ever been committed. The defect is in the verifier only: it is not on the production path, `build()`
  produced the registry without it, and no published number is affected. Confirmed directly by re-certifying
  `taboo_block_305_00` on the independent host, which reproduces bit-identically. Fixed, and fixed structurally —
  the repaired code indexes `rec[fld]`, so a missing field now raises instead of silently comparing against
  `None`. A full verification run against the committed registry is committed with its output:
  `evidence/prefreeze/C2_REGISTRY_VERIFY.json` — **105 artifacts re-checked across all five cells, `pass: true`,
  no problems**, on the same independent macOS/arm64 host, with host, toolchain and the registry's own sha256
  recorded in the artifact. So the registry is now demonstrably re-verifiable. The C1 reviewer's complaint that
  `REGISTRY_C2.json` records no host or toolchain is **not** thereby answered, and an earlier version of this
  sentence wrongly said it was: the two verification artifacts record the host that *re-certified*, not the host
  that *built*, and nothing in the repository records the latter. See `phase_d/CELL_306_ADOPTION.md` and **N10**;
  raised as note 4 by review r2 and as a FAIL by review r7.

  This one is worth stating plainly: a review row marked **INFO**, not FAIL, and phrased only as "not demonstrated
  in-repo", led to the discovery that a verification tool this campaign pointed at as evidence of its own
  soundness had never worked. The lesson is the row's, not C2's: a check nobody has run is not a check.

### Corrections arising from the INFO rows

- **Sensitivity convention stated** (row 32). "A 10 % improvement" means scale by 1.1 in the improving direction.
  The review also suggested that the other convention (× 0.9) reverses the D_lo-vs-τ ordering. **It does not**, and
  C2 says so: that comparison takes τ from one convention and D_lo from the other. Recomputed on all five cells
  under both registries and both conventions, D_lo outranks τ everywhere — and the second review independently
  confirmed that C2 was right on this point. **A further claim made here in the first repair round has since been
  withdrawn**: C2 also argued that ×0.9 was disqualified for driving C_T below τ. It is not, because ÷1.1 does the
  same thing on the same three cells. See the r2 FAIL 65 row below; the only surviving reason to prefer ÷1.1 is
  symmetry in A0 = τ/D_lo.
- **Loose percentages tightened** (row 15). τ regressed by 1.90–2.24 % (not "2–3 %"); the A0 gain is 4.49–4.65 % of
  C1's value, or 4.71–4.88 % as C1/C2 − 1.
- **The measure-change self-audit was one-sided** (row 7 / Note 4). It audited the one change unfavourable to C2
  and left the other three unexamined. It now carries the full four-axis comparison and the finding that under
  **C1's gate verbatim C2 would have been USEFUL**, against `D_PARTIAL` under its own — i.e. C2's gate is, in net,
  *harder* on C2 than its predecessor's was.
- **The adversarial suite was extended from 33 to 43** (Notes 13 and 14): 35 real mutants and 8 static assertions,
  40 detected, 3 proven equivalent, **0 undetected**. New coverage for the three mechanisms the review found
  unmutated — the assembly coefficients, the sub-block tiling geometry, and the intersection / `M_after` step — and
  the selector mutants re-run over the `{G, C1}` sub-family, where the componentwise minimum genuinely mixes, which
  converts the review's Note 13 into two real detections.
- **A new equivalent mutant is recorded with a proof, not an excuse.** `M32_intersection_skipped` is undetectable
  because the TC-T enclosure is strictly *contained* in the adopted record's R2 interval on all five cells, so the
  intersection is the identity. The suite now verifies that containment at run time; if it ever fails, the row
  reverts to an undetected miss. The containment is also the reason TC-T binds at all: M = mag(enclosure) < M_R2 on
  every cell, so the enclosure and not the record is what sets Γ.

## The finding that outranks all of the above

Review **Note 11**, which is not a FAIL and is the most consequential thing in the document: a sound
operator-level combination that C2 did not pre-register — componentwise best of the C1 and C2 registries, min on
the five upper bounds and max on D_lo — clears the gate's own 20 % bar on **all three** still-open cells, including
the 309 that cost C2 the `D_USEFUL` class, at **zero** new CPU and zero new real addresses.

C2 does not take it, and must not: the gate pre-registers the minimum over A0/A1/A2 across *supplies*, not over the
six operator constants, and adopting the second rule after seeing that 309 landed at 18.39 % is exactly the
post-hoc choice the gate exists to forbid. C2's class stands at `D_PARTIAL`.

But the consequence is load-bearing: the premise under which the programme's first real order-3 tail address would
be spent — that the deterministic direction is exhausted — is **not established by this campaign**. What ran out is
C2's pre-registration, not the deterministic direction. This is recorded in full in
`phase_d/D_PRIME_OPPORTUNITY.md`, and `phase_r/R_STAGE_DESIGN.md` now opens with it as a **blocking precondition**
on any R-stage authorization.

## Dispositions from the SECOND pre-freeze review

A second independent fresh-context review ran on the repairs at `ef58310c`
(`review/REVIEW_C2_PREFREEZE_R2.md`): **3 FAIL**. It confirmed every repair
above independently — including re-certifying cell 306 artifacts on the Arb/FLINT stack, which neither earlier
reviewer could do — and it found that on the one point where C2 corrected the *first* reviewer (the ×0.9
convention and the D_lo-vs-τ ordering), **C2 was right**. Its three FAILs:

| | finding | repair |
|---|---|---|
| **r2 FAIL 65** | C2's *newly added* claim that ×0.9 is disqualified because it drives C_T below τ is **wrong**: the published ÷1.1 convention does exactly the same thing on exactly the same three cells (307: 4.846842 < 4.851873; 308: 4.553601 < 4.633777; 309: 4.277739 < 4.418493). | Claim withdrawn in `phase_d/D1_BLOCKER_DIAGNOSIS.md`. The only reason to prefer ÷1.1 is symmetry in A0 = τ/D_lo, and the text now says that and nothing more. A repair that introduced a new error, caught before freeze. |
| **r2 FAIL 66** | Consequently the published C_T sensitivity figures for 307/308/309 were computed **outside the Lemma Dv′ hypotheses**, reached only because `c2_d1_blocker.atom_dv_prime` is an unguarded local copy of the pinned consumer, which would have refused. Undisclosed. | Guard added, enforcing the four premise inequalities that `deflated_consume.atom_constants_r2` validates (not a byte-for-byte copy: the pinned consumer also type-checks its inputs and post-checks r2 ≤ r1). The C_T column now reports the **admissible best C_T = τ**, giving +1.3681 / +1.1502 / +0.9335 % against the inadmissible +1.3823 / +1.3945 / +1.3887 %. Evidence regenerated (`1d7715a2…`). Γ, magnitudes, blocker shares and every other sensitivity row are bit-unchanged. Measured against `ef58310c` the file goes from 487 leaves to 525: **nine values changed**, all `magnitude` / `delta_vs_base` / `relative_gain` on the C_T row of cells 307, 308, 309; **38 leaves added** — 25 `effective_improvement` (five operator rows × five cells, which is 5 of the 11 sensitivity rows per cell, not "every row"), 5 `gain_per_unit_of_input_moved` and 5 `per_unit_comparability` on the C_T rows, and 3 `admissibility_clamp` strings; **nothing removed**. The nine changed values plus the three clamp strings are the twelve r3 verified. **The inference C2 drew from this was itself wrong and r3 corrected it**: a clamped row is not a 10 % improvement (the admissible cuts are 8.997 / 7.490 / 6.100 % against 9.0909 % on the other upper-bound rows), and per unit of C_T removed the response is essentially flat across the tail — 0.1496 / 0.1504 / 0.1521 / 0.1536 / 0.1530, rising over the first four and easing slightly at 309. C_T is not a weaker lever at 309; it is a **nearly exhausted** one, with only 6.1 % of travel left before it meets τ. r4 independently stress-tested that reading at a common admissible cut and at the marginal slope and confirmed it is not an artifact of the smaller window. |
| **r2 FAIL 10** | `phase_d/CELL_306_ADOPTION.md` asserted "It is adopted." of cell 305 — a terminal governance state the adjudication chain has not reached. | Rewritten: cell 305 is *carried to adoption unconditionally*, and the text now states that adoption is conferred only by the freeze → qualification → seal → double consumption → adjudication chain, none of which has happened. |

On the question C2 asked the reviewer to attack — separating three internal diagnostics from asserted to measured
*after* a test failed — the review found it **not a moved goalpost**, verified from the git history that the
consumed-constant comparisons and the strict determinism branch are character-for-character unchanged across
`12585997..8aee1fc5`, and supplied a stronger argument than C2's own: `certify_block` sets
`ok = margin > 0 and wmin >= 0`, and `certified is True` is asserted unconditionally in **both** passes, so the
load-bearing content of all three diagnostics was never relaxed — only their low-order digits. It also correctly
criticised C2's wording: "not a bound anyone relies on" is wrong for `allowance_upper`, which *is* an input to the
certification inequality. That wording is withdrawn here.

## Dispositions from the THIRD pre-freeze review

A third focused review ran on the r2 repairs at `55c4cf00` (`review/REVIEW_C2_PREFREEZE_R3.md`): **1 FAIL**. It re-ran all three producers and confirmed each reproduces **byte-for-byte**, verified the
leaf-level diff of the regenerated D1 evidence is exactly twelve values, and confirmed both rewritten
`DIAGNOSTIC_NOTE` claims against `taboo_certify.py` source.

| | finding | repair |
|---|---|---|
| **r3 FAIL 6** | C2 repaired the withdrawn ×0.9 claim in `D1_BLOCKER_DIAGNOSIS.md` but **left the identical claim standing, in the present tense, in this file** — 45 lines above its own r2 FAIL 65 disposition saying it was withdrawn. The errata register contradicted itself, in the very commit that repaired the defect, in the document an adjudicator reads first. | Fixed above. The claim is now explicitly marked withdrawn where it was made. |

Three of its NOTEs were substantive enough to act on, and one of them corrected C2's own inference:

- **The clamped C_T rows are not 10 % improvements.** Acted on; see the r2 FAIL 66 row. This is the third
  successive review round in which C2's *repair* carried an error of its own, and the pattern is worth naming:
  each was a case of C2 reaching for a second, unverified supporting argument on top of a correct primary one.
- **"The same treatment D_lo has always had at its cap of 1" was misleading.** That cap has **never executed** —
  the maximum D_lo × 1.1 across the tail is 0.9329, comfortably under 1. The phrasing invited the reader to think
  the D_lo column was itself clamped. The analogy is withdrawn from both documents rather than restated.
- **"Refuses exactly as `deflated_consume.atom_constants` does" overclaimed.** The guard enforces the four premise
  inequalities but is not a byte-for-byte copy — the pinned consumer also type-checks its inputs and post-checks
  r2 ≤ r1, and the relevant entry point is `atom_constants_r2`. Corrected in the document — **but NOT, at the
  time, in the source comment r3 had explicitly named**, which went on asserting it for another round until r4
  caught it. The claim "corrected in both places" was itself false when written. Now corrected in both places.

One NOTE was a credit C2 had not claimed, and it belongs in the record because it is evidence, not praise: when
`c2_recertify_306.py` was re-run only to correct a comment, **both Arb/FLINT passes genuinely re-executed** (~40
minutes) and every field other than the note string and two `cpu_seconds` values came back **bit-identical**. That
is a second, independent determinism replication of cell 306's eighteen artifacts on the macOS/arm64 FLINT build,
obtained incidentally. It is recorded here because it strengthens the FAIL 51 disposition above.

## Dispositions from the FOURTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R4.md`, at `17123368`: **3 FAIL**. It verified both claims
C2 had checked at source, confirmed all three producers reproduce byte-for-byte, re-certified cell-306 artifacts
on FLINT at both precisions, and stress-tested the "nearly exhausted" reading harder than r3 had — recomputing at
a common admissible cut and at the marginal slope, specifically hunting the refutation that it is an artifact of
a smaller window. It is not: window effects move each figure by < 0.0009 against a 0.0034 spread.

**And it found that the repair had introduced a new error for the third consecutive round**, in precisely the
shape §"The pattern, named" predicts.

| | finding | repair |
|---|---|---|
| **r4 FAIL 1** | r3 asked for **one** new field, `effective_improvement`. C2 added that, correctly — and then added a second field r3 never requested and C2 never checked: `gain_per_unit_of_input_moved`, on all five operator rows. **It reverses the D_lo-vs-τ ordering on every cell** (309: τ 0.898489 against D_lo 0.871859), contradicting the one finding §2 states in bold that the whole section rests on — the point r1 attacked, C2 defended, and r2 confirmed C2 was right about — uncaveated, in the machine-readable artifact. | The field is now emitted **on the C_T row only**, where it answers the same-input headroom question it exists for, and the artifact carries a `per_unit_comparability` string stating the limit. Cause recorded in-source: the ÷1.1 convention equalises the effect on A0 = τ/D_lo, which is *why* the input fractions differ (10 % against 9.0909 %); dividing by the input fraction discards exactly that symmetry and inflates τ by 1.1. Renormalising by equal A0 effect instead divides **both** rows by the same constant 1 − 1/1.1, so it preserves `relative_gain`'s ordering and its ratio exactly — 1.0674 at cell 309 either way. That is the point: a normalisation consistent with the convention changes nothing, and only dividing by each input's own fraction inverts the result. |
| **r4 FAIL 2** | The withdrawn "refuses exactly as `deflated_consume.atom_constants`" claim **survived verbatim in the source comment** at `c2_d1_blocker.py`, which r3's note 2 had explicitly named — while this file asserted "Corrected in both places". Same shape as r3 FAIL 6, one round later: the prose was fixed and the copy the reviewer pointed at was not. | Comment rewritten to state that the guard enforces the four premise inequalities **only**, and is deliberately not a claim of equivalence. The false "in both places" sentence is corrected above rather than deleted. |
| **r4 FAIL 3** | `README.md` had been stale since `12585997`: it advertised one review of three and six FAILs of ten, and said "no published number changed" when nine had. | Rewritten to list every review, and to state which published numbers had changed. *(Both parts of that repair were themselves superseded later: the per-review PASS/NOTE/INFO counts it added were removed at r5 FAIL 2, and "two published numbers" was corrected to one value plus one table in self-audit — see the top of this document.)* |

Non-blocking corrections from its notes, all applied: the leaf accounting is now exact (487 → 525; nine changed,
38 added, none removed) rather than the double-counted "53"; "on every row" is corrected to five of the eleven
sensitivity rows per cell; "slightly rising" is corrected to essentially flat, since the series eases at 309
rather than rising monotonically; and the ◆ note's closing clause "for the same structural reason τ cannot fall"
is removed as a non-sequitur — both its components are true and the τ/D_lo branch does bind on all five cells,
but it supports finding 3, not the C_T headroom claim it was attached to.

## Dispositions from the FIFTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R5.md`, at `1663f558`: **2 FAIL**. Both text-only, and both
the documented shape again. It also did something no earlier round did: diffed **every leaf of
`C2_D1_BLOCKER.json` across its entire commit history**, confirming that exactly nine leaves of that artifact have ever changed in
this campaign, all of them C_T sensitivity on cells 307–309.

| | finding | repair |
|---|---|---|
| **r5 FAIL 1** | Round four replaced this section's opening with a table but **left the superseded r3-era paragraphs standing underneath**, claiming C2 had avoided "repeating the pattern a fourth time" — contradicted by the table twenty lines above and by the new paragraph saying "That was not enough". A stale self-contradicting remnant left by a repair, inside the section about stale remnants left by repairs. | Removed, with a marker recording what stood there. |
| **r5 FAIL 2** | In the README row r4 asked C2 to rebuild, C2 added PASS/NOTE/INFO parentheticals **nobody requested** and got r2's wrong. | The parentheticals are **removed, not corrected** — that is the point of the lesson below. The README now carries FAIL counts only, which reconcile against the disposition rows here, and says why the rest is not transcribed. |

**On r5 FAIL 2, the review is half right and the half it gets wrong matters.** Its claim that r1 has *zero*
`NOT_CHECKABLE_LOCALLY` rows is **false**: the string occurs five times in that file and r1's own verdict table
records `NOT_CHECKABLE_LOCALLY | 3` against a total of 79. C2's transcription of r1 was faithful. On r2 the review
is right that the true breakdown is 62 PASS / 4 NOTE / 2 INFO — but C2's README faithfully transcribed **r2's own
header**, which states 55 / 5 / 3 against a total of 71, and 55 + 5 + 3 + 3 = 66 ≠ 71. So the inconsistency
originates in r2's self-report, not in C2's copying of it. Independently recounted for the two documents in
dispute: r1's own verdict table (60 PASS / 10 INFO / 3 NOT_CHECKABLE_LOCALLY / 6 FAIL) reconciles with its 79
rows; r2's own header (55 / 5 / 3 against a stated total of 71) does not, and its true breakdown is 62 / 4 / 2.

That does not rescue the decoration, and C2 is not going to argue it does. The counts were not asked for, were not
needed, and propagated someone else's arithmetic error into the campaign's front door. **The fix is deletion, not
correction.**

## Dispositions from the SIXTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R6.md`, at `ec5b08ca`: **1 FAIL**. It independently
re-derived the gap falls (0.462852 / 0.245931 / 0.183898) and confirmed `D_PARTIAL` with closed = {305, 306} is
mechanical under the frozen gate; ran its own leaf diff across **all four commits** that have ever touched
`C2_D1_BLOCKER.json`, confirming exactly nine leaves have ever had a value replaced; verified that `5a94568a`'s
copy already said `DOMINANT_BLOCKER_3 = order0_residual_fF`; and confirmed C2's correction of r5 — r1 does have
three `NOT_CHECKABLE_LOCALLY` rows, and r2's own header genuinely does not reconcile with its own total.

| | finding | repair |
|---|---|---|
| **r6 FAIL 1** | `README.md` still said "**Four** independent pre-freeze reviews" and "— **three separate times** — an error introduced by a repair", two lines above the paragraph `ec5b08ca` had just rewritten, which correctly says "the **fifth** review". The same file's own table listed five. | Both counts **removed rather than updated**, with the review table left to carry them and the prose pointing at it. *(That repair was incomplete and its claim to completeness was itself wrong twice more — see r7 FAIL 1, r8 FAIL 1 and r9 FAIL 1 below.)* |

**The repair is structural, not another number.** Several of the instances in the register below are a count left
stale by a later edit, and this was another. Updating the number would have set the same trap for the next round. So every
hand-maintained tally was deleted from the prose that carried it. Counts belong in the tables — the review list
at the top of the README, the round table at the top of this document, and the registers below. *(C2 has twice
written a sentence here claiming its prose contains no counts, and each time the claim was false while the
sentence itself sat beside counts. No such claim is made now: where prose states a number it should simply be
right, and checked before it is written.)*

On the review's own closing point, which C2 accepts: what it blocked on was not prose quality but *a wrong count
of how many independent reviews the campaign had survived, in the front-door document*. That is a claim about the
campaign's reliability, in the document an adjudicator reads first, and failing it was consistent with r4 FAIL 3
and r5 FAIL 2 rather than a softening of them.

## Dispositions from the SEVENTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R7.md`, at `5a098ec6`: **2 FAIL**. It re-derived the D-stage
result independently (gap falls 0.462852 / 0.245931 / 0.183898, `classify()` a faithful transcription of the frozen
gate), re-certified five artifacts across cells 305/306/309 on the Arb/FLINT stack itself — bit-identical at 256
bits, safe-side-valid at 384 — reproduced the mixed-operator supply's 57.27 / 30.57 / 23.03 % and its whole-cell
premise, verified the 384-bit separation from git history, and diffed the D1 evidence across all four of its
commits to confirm nine leaves have ever changed.

| | finding | repair |
|---|---|---|
| **r7 FAIL 1** | The de-counting commit `5a098ec6` cleaned `README.md` and **left five prose counts in `ERRATUM_C2.md`** — "Across all five rounds" twice, "three separate instances below", and a four-review recount tally — while asserting **twice** that no sentence in the namespace states a count. The claim that two tables are the only places a count appears was also false: this document's own round table is a third. | The five counts are removed or rescoped, and **both self-referential assertions are deleted rather than maintained**. Asserting "no sentence states a count" is itself a falsifiable claim about every sentence, and it had already been falsified twice; the text now states where counts belong, without claiming compliance. The recount is rescoped to the two self-reports actually in dispute (r1's reconciles; r2's does not), which is fixed historical fact rather than a running tally. |
| **r7 FAIL 2** | `phase_d/CELL_306_ADOPTION.md`'s comparison table presented a **build-host column that is recorded in no committed artifact**, and the bolded claim that the machinery "reproduces across the OS, architecture and FLINT build boundary" rested entirely on it. This document additionally claimed the provenance complaint "is answered by the two artifacts that do". **Review r2 asked for exactly this column to be marked reported-rather-than-recorded, in its note 4, and C2 left it undispositioned for five rounds.** | The column is now labelled **reported, not recorded** against a **recorded** right column; the bolded claim is scoped to what the artifacts establish — reproduction on a fully recorded host, not across a recorded boundary; the "is answered" sentence is corrected; and the gap is carried forward as **N10**, with the weak but real in-repo corroboration r2 found (build-host `cpu_seconds` 90.2 / 88.3 against 56.2 / 66.1 on the re-certifying host) cited as what it is. |

**FAIL 2 is not an instance of the documented pattern, and C2 is not going to file it as one.** The pattern is
unverified decoration added on top of a correct fix. This was the opposite: a reviewer note that asked for *less*
confidence in a claim, received, understood, and then simply never actioned across five subsequent rounds while the
claim stayed bolded. That is a distinct and arguably worse failure — the pattern produces wrong ornaments, this
produced an unsupported load-bearing sentence — and the register below now tracks the two separately.

## Dispositions from the EIGHTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R8.md`, at `07c0b991`: **3 FAIL**. It re-verified the science
cold — all three producers byte-for-byte, the class and closed subset, the gap falls, both Γ, the gate at one
commit, `REGISTRY_C2.json`'s 50 key paths carrying no host field — and confirmed the rescoped recount and the
cited `cpu_seconds` corroboration (90.248 / 88.257) from the artifacts.

| | finding | repair |
|---|---|---|
| **r8 FAIL 1** | r7's FAIL 1 was **not** repaired. r7 enumerated five surviving prose counts; C2 fixed four and never touched the fifth — "reproducing bit-exactly under **four** independent implementations" — which r7 had named explicitly. The repair then created two fresh self-contradictions: "the **two** tables — [three listed] — carry the counts", and "the table below is the campaign's **only** tally" left standing while the same commit added a second register 19 lines below. The disposition row itself said r7 found "four prose counts" where r7 found five, which is how the fifth survived. | All five counts now removed or rescoped; the two orphaned sentences rewritten to describe the tables as they are; the disposition row corrected to five in both halves. C2 also swept the namespace itself this round rather than trusting a grep for counts, and found **two more** survivors neither r7 nor r8 listed: `README.md`'s claim that its phase table "is the only part of this README written after any C2 number existed" — false, since the whole Result section was — and an absolute "the only thing standing between" in N10. Both corrected. |
| **r8 FAIL 2** | The unscoped claim survived in §"Cell 306", this document's own summary of the closing governance question: "the independent re-certification is now delivered on a **genuinely second host**" — the exact phrase r2's note 4 named, now contradicted by the repaired `CELL_306_ADOPTION.md`. It bears directly on whether C1's reviewer's adoption condition 2 is met. | Rewritten to the weaker sense the evidence supports: every field of all eighteen artifacts reproduces on a host whose OS, architecture, Python and Arb/FLINT build are recorded, the registry's build host is recorded nowhere, and **no second host is evidenced** (**N10**). |
| **r8 FAIL 3** | **The committed evidence itself asserted the boundary N10 says is recorded nowhere.** `C2_RECERTIFY_306.json`'s `host.note` read "second host: a different OS, CPU architecture and compiled Arb/FLINT build than the registry" — a hardcoded editorial string sitting inside the `host` object beside five genuinely recorded fields, where any reader or machine consumer takes it as recorded, while `CELL_306_ADOPTION.md` says that difference "rests on C2's report, not on an artifact". | **Fixed at the source and the artifact regenerated**, rather than disclosed. The review proposed two disclosure clauses and no artifact rewrite; C2 deliberately took the heavier route, because an evidence file should contain only what was observed and a disclosure elsewhere leaves the misleading string where it is read as fact. The field now records that its values were observed on the re-certifying host and makes no claim about the build host, with the removal explained in-source. Regenerating also re-executed both Arb/FLINT passes, a third independent determinism replication. |

## Dispositions from the NINTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R9.md`, at `5609358f`: **3 FAIL**. It reproduced the
regeneration accounting independently — 1224 leaves both sides, 0 added, 0 removed, exactly 3 replaced, every
certified value bit-identical — and confirmed the science, the gate and the integrity envelope.

| | finding | repair |
|---|---|---|
| **r9 FAIL 1** | The false-absolute class again, with one instance **added by the commit that was repairing it**. `README.md`'s new footnote was false twice: "only the material above the table is part of the pre-registration" is refuted by the README's own closing line, which sits *below* the table and is byte-identical to `87309610`'s; and "the phase rows above read '—'" is false for two of the four rows that existed at the freeze (B0 read `7/7 PASS`, the gate row `frozen at this commit`). Surviving separately: the r6 disposition row's "the review table is now the single place in this namespace that counts reviews", contradicted five lines below. | The footnote no longer describes the pre-registration at all — it states which rows were what, and **points the reader at `git show 87309610:…/README.md`** rather than asking them to trust a description. The r6 row is rewritten in the past tense with its own incompleteness recorded. |
| **r9 FAIL 2** | The r8 repair **replaced two published values and left "exactly one published value has changed in the whole campaign" standing** in two documents. `cpu_seconds` is not inert here: it is cited in `CELL_306_ADOPTION.md` as the only in-repo corroboration for the build host. The 3-of-1224 accounting existed only in a commit message, not in the namespace. | Both documents now separate the **scientific** value change (the C_T row, nine leaves, verified independently by r5, r6, r7 and r8) from the **wall-clock** totals the regenerations replaced, with the full ledger stated in the namespace and the command to regenerate it. *(This repair was itself incomplete — it named r9 as a verifier, which it was not, and recorded one of the two regenerations; see r10 FAILs 1 and 3.)* Checked and stated: the cited corroboration figures are **90.248 and 88.257**, per-artifact values inside `taboo_block_306_02.json` and `taboo_block_305_00.json`, not the pass totals — and `evidence/registry_c2/` is byte-unchanged throughout the campaign. |
| **r9 FAIL 3** | r8 named **three** sites carrying the build-host assertion; the r8 repair fixed two and missed the docstring, leaving `c2_recertify_306.py` contradicting its own comment forty lines below. | Withdrawn in the docstring, which now states what the module does claim and cites **N10** for what it does not. No regeneration, and the artifact was checked rather than reasoned about: its raw bytes were probed for fragments of the docstring and contain none. The bound C2 gave for *why* — that the artifact carries only four free-text fields — was **false and is withdrawn**: it holds 835 string leaves, 236 of them hardcoded English `test` strings (r10 FAIL 2). The probe stands on its own; the bound was ornament, and wrong. |

**On r9's judgement of the r8 deviation.** The review found that overriding its own recommendation — regenerating
the artifact instead of disclosing around it — was **right**, and that the execution was merely unfinished: "Keep
the regeneration and finish it — do not reverse it." It is finished here. It is the only occasion on which C2 has
departed from a reviewer's explicit instruction, and the departure held up.

## Dispositions from the TENTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R10.md`, at `575919cb`: **3 FAIL**. All three are
the same class, and all three are claims C2 asserted **over a corpus without running the check**.

| | finding | repair |
|---|---|---|
| **r10 FAIL 1** | C2 wrote that "r5 and r9 each verified by diffing every leaf of that artifact across its entire history". **r9 never did that** — its only leaf diff was of `C2_RECERTIFY_306.json` across one commit pair. Checking every committed review file shows **r5, r6, r7 and r8** each did it. The README's "two independent reviews" was therefore false where four applied, and it replaced text that had been true. | Corrected to r5, r6, r7, r8 in both documents, after re-checking each review file. |
| **r10 FAIL 2** | C2's justification for not regenerating the artifact after the docstring fix claimed "the only free text the artifact carries is `taboo_sha256`, `verdict`, `host.note` and `diagnostic_policy.why`". It carries **835 string leaves, 236 of them hardcoded English `test` strings** — a bound that was wrong by two orders of magnitude, asserted one round after a blocking defect that was editorial English hiding in this very artifact. | The bound is **withdrawn, not corrected**. The primary claim never depended on it: the artifact's raw bytes were probed for docstring fragments and contain none, which r10 reproduced. The bound was ornament, and wrong. |
| **r10 FAIL 3** | The replacement ledger accounted for **one of two** post-review regenerations of `C2_RECERTIFY_306.json`. `8aee1fc5 → 55c4cf00` had already replaced `diagnostic_policy.why` and both `cpu_seconds` (1653.6 → 1153.9, 1691.8 → 1204.2). C2 inherited the "one place" premise from r9 without checking it. | The ledger is rebuilt from the artifact's full history, lists **both** regenerations and the D1 change, and **carries the command to regenerate it rather than trust it**. That C2 took a reviewer's premise unverified is recorded in the register below. |

**The rule r10 supplied, which C2 adopts.** *Never describe a corpus you can cite; if you must describe it, run
the check before committing the sentence, and put the command in the text.* r10's diagnosis of why this class
keeps migrating rather than closing is that C2 has fixed one corpus per round. This round the rule was applied to
every corpus claim in the bookkeeping documents at once: the ledger now carries its regeneration command, and the
remaining universals were each re-derived — `evidence/registry_c2/` has exactly one commit in its history, no
build-host record exists anywhere in C2's `evidence/` or `config/`, and the "only in-repo corroboration" claim is
narrowed to the corroboration r2 identified, since C2 cannot establish it is the only one.

## Dispositions from the ELEVENTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R11.md`, at `87004e2b`: **2 FAIL**. It rebuilt
the replacement ledger itself over every committed evidence and config file, and separately verified ten corpus
claims sound and listed them so a later round need not re-derive them.

| | finding | repair |
|---|---|---|
| **r11 FAIL 1** | The replacement ledger — the instrument built the previous round *to be* the complete provenance accounting — was **incomplete**. Its scope sentence claimed every replaced leaf; it omitted `evidence/prefreeze/C2_MUTATIONS.json` (`5a94568a → 12585997`, four leaves: `applied` 33 → 43, `detected` 31 → 40, `real_mutants` 25 → 35, `M10.caught_by[0]`). C2 had rebuilt the ledger over the two files it already knew about rather than over the corpus its own sentence named. | The ledger is rebuilt over **every** committed file under `evidence/` and `config/` and now carries all **19** leaves across **three** files, with the breakdown: nine scientific, four suite counts, six free text and timings. |
| **r11 FAIL 2** | The repair introduced a new instance of the very class it was closing: `87004e2b` added "four independent reviews (r5, r6, r7, r8)" to the README while this document asserted "every hand-maintained tally has been deleted from prose … and prose does not". Compliance claimed, counts present. | The compliance clauses are deleted. *(The first repair removed one of the two and recorded both as gone — r12 FAIL 1. The second survived verbatim for a further round and is deleted now.)* C2 has written a sentence claiming its prose carries no counts three times, and each time the claim was false while sitting beside counts. No such claim is made any more: where prose states a number it should simply be right, and be checked before it is written. The accurate counts themselves are kept. |

Also acted on: "exactly nine leaves have ever changed in this campaign" was true of `C2_D1_BLOCKER.json` and false
campaign-wide, where the figure is 19. Both occurrences are now scoped to the artifact.

## Dispositions from the TWELFTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R12.md`, at `6aa2040a`: **2 FAIL**. It rebuilt the replacement ledger independently
over all 115 committed files under `evidence/` and `config/`, taking no file list from C2, and confirmed
**19 leaves / three files / 9 + 4 + 6 correct in every cell, with nothing missing** — r11 FAIL 1 fully repaired.
It also listed all seven surviving instances of the corpus-claim class rather than leaving any for a later round,
and disclosed that its own first draft of its verdict table was hand-tallied and wrong, which it re-extracted
mechanically before finishing — the same hazard it was auditing.

| | finding | repair |
|---|---|---|
| **r12 FAIL 1** | r11 named **two** compliance clauses. C2 deleted one, deleted a trailing fragment of a neighbouring sentence, and recorded both as gone. The second survived **verbatim** ("…prose does not") for a further round, in a document whose disposition row asserted "Both compliance clauses are deleted. … No such claim is made any more." | The surviving clause is deleted and the row rewritten to record that the first repair was partial. |
| **r12 FAIL 2** | The new README provenance paragraph did not reconcile: "Nineteen leaves … exactly **one** of them is a scientific value … **Four** are … **six** are" — 1 + 4 + 6 = 11, not 19, and the "one" scientific correction is **nine** leaves. It contradicted this document eight sections away, in the front-door file. | Rewritten as 9 + 4 + 6 = 19, with the nine named as the one scientific correction. |

Its NOTE-level findings were acted on rather than deferred: the claim that no "magnitude" appears in the ledger
table is now stated as a claim about **values** (the D1 row does name a field called `magnitude`, but it is a
sensitivity probe's magnitude at a perturbed C_T, not a cell's); "the one place in nine rounds" no longer carries a
round count; and the transcribed per-review PASS/NOTE/INFO sub-counts were removed from the disposition headers.
r12 had caught that the r11 header copied a self-report which does not reconcile with r11's own checklist
(31/1/2/2 against a stated 30/1/3/2).

*(That last repair was itself incomplete, and the sentence recording it claimed otherwise — r13 FAIL 1. One header
still carried its sub-counts a round later, and the count of headers given was wrong. This paragraph no longer
asserts that the removal is exhaustive; to check it, grep this file for `PASS` and read what is left.)*

## Dispositions from the THIRTEENTH pre-freeze review

`review/REVIEW_C2_PREFREEZE_R13.md`, at `92bc9637`: **3 FAIL**, all textual, none touching evidence. It rebuilt
the replacement ledger from the git object store over all 115 committed `evidence/` and `config/` files, taking no
list from C2 or from r12, and confirmed 19 leaves / three files / 9 + 4 + 6 correct in every cell. It extracted its
own verdict counts by script after finding its first hand-tally wrong, and disclosed that.

| | finding | repair |
|---|---|---|
| **r13 FAIL 1** | The paragraph dispositioning r12 claimed "**every** transcribed per-review sub-count has been stripped" and "Only FAIL counts remain". One header still carried its sub-counts, and the count of headers given was wrong. **This is r12 FAIL 1's exact shape — all-but-one repaired and recorded as complete — committed in the paragraph dispositioning r12, in precisely the kind of sentence r12 asked C2 to stop writing.** | The surviving header is stripped, and **the exhaustiveness claim is deleted rather than corrected**. The paragraph now tells the reader how to check for themselves instead of asserting the result. |
| **r13 FAIL 2** | Two statements of the same fact in this document disagreed: one said C2 had written a "prose contains no counts" sentence **twice**, the other **three times**. r12 had named both sites; only one was repaired. | The count is removed from the older statement, so the two cannot diverge again. |
| **r13 FAIL 3** | "**The self-audit is now finding these faster than the reviews are**" was false when written and had been false for six rounds. | Withdrawn, and replaced with what the register actually shows, re-derived here: of its instances, **four** were self-caught, all in rounds four and five, and **none** of the twelve added in rounds six to eleven. The self-audit stopped finding them; the reviews did not. That is the honest reading and it is not flattering. |

## The pattern, named

**Every one of C2's repair rounds has carried an error of its own.** The registers below are the record; the prose
after them is deliberately short, because this section's narrative has been the single largest source of the
defects it describes. Where an episode is in a register row, it is not re-told.

| round | the repair | the error it introduced | caught by |
|---|---|---|---|
| 1 | corrected the mislabelled critical-ratio column | added an unverified second argument for the ÷1.1 convention that was simply false | r2 FAIL 65 |
| 2 | corrected that, and guarded the premise | left the same claim contradicting itself in this file, and drew the wrong inference from its own corrected numbers | r3 FAIL 6 |
| 3 | corrected that, and added the field r3 asked for | added a **second** field r3 did not ask for, which reverses the ordering §2 rests on | r4 FAIL 1 |
| 3 | said the overclaim was "corrected in both places" | corrected the prose, not the source comment r3 had explicitly named | r4 FAIL 2 |
| 4 | replaced this section's opening with a table | left the superseded paragraphs underneath, contradicting the new table | r5 FAIL 1 |
| 4 | rebuilt the README review row as r4 asked | added PASS/NOTE/INFO counts nobody asked for, propagating r2's own arithmetic error | r5 FAIL 2 |
| 4 | wrote up r4 FAIL 1 | restated a reviewer's comparative claim unverified; it was false | **self-caught**, `1663f558` |
| 5 | wrote the README footnote explaining the removal | said a previous version "got two wrong"; only one was wrong | **self-caught**, `a58bbdd8` |
| 5 | rewrote this section's prose | miscounted its own table as five-and-two; it was four-and-three | **self-caught**, `a58bbdd8` |
| 5 | summarised what had changed | said "two published numbers"; conflated one evidence change with one prose correction | **self-caught**, `ec5b08ca` |
| 5 | rewrote the README's "one published value" paragraph | left the paragraph one line above saying "four reviews" and "three separate times" | r6 FAIL 1 |
| 6 | deleted every hand-maintained count from prose | cleaned `README.md`, left five counts in this document, and asserted twice that none remained | r7 FAIL 1 |
| 7 | repaired r7 FAIL 1 | fixed four of the five counts r7 listed, and orphaned two more sentences by adding a second register | r8 FAIL 1 |
| 8 | repaired r8 FAIL 1 | the replacement footnote was itself false twice over | r9 FAIL 1 |
| 8 | repaired r8 FAIL 3 by regenerating the artifact | replaced two published values while leaving "exactly one published value has changed" standing | r9 FAIL 2 |
| 8 | repaired r8 FAIL 3 | fixed two of the three sites r8 named, missing the docstring | r9 FAIL 3 |
| 9 | wrote the replacement ledger | took r9's "one place" premise unverified; there were two regenerations | r10 FAIL 3 |
| 9 | justified not regenerating after the docstring fix | added a free-text bound wrong by two orders of magnitude | r10 FAIL 2 |
| 9 | corrected the verifier attribution | named r9, which had not done the diff; four other rounds had | r10 FAIL 1 |
| 10 | built the replacement ledger to be complete | rebuilt it over the two files C2 already knew of, not the corpus its own sentence named | r11 FAIL 1 |
| 10 | applied the cite-don't-describe rule | added a new prose count in the same commit as a clause claiming none remained | r11 FAIL 2 |
| 11 | deleted the compliance clauses r11 named | deleted one of two and recorded both as gone | r12 FAIL 1 |
| 11 | summarised the completed ledger in the README | wrote a breakdown summing to 11 of 19 | r12 FAIL 2 |
| 12 | stripped the transcribed sub-counts | left one header, miscounted the headers, and claimed the removal was exhaustive | r13 FAIL 1 |
| 12 | rewrote one of two statements of the same fact | left the other, so the document now contradicted itself on it | r13 FAIL 2 |

A separate register, for a different failure — a review note received and then never actioned, rather than
decoration added:

| round asked | the note | what happened | caught by |
|---|---|---|---|
| r2 | note 4: mark the build-host column "reported rather than recorded" | never actioned; the bolded claim resting on it stayed unqualified for five rounds | r7 FAIL 2 |

Every instance has the same shape — **a correct primary argument or fix, with a second unverified thing stacked
on top of it, or a neighbouring sentence the fix failed to carry along.** The primary claim was sound every time;
the decoration and the leftovers were not.

One substantive point from those episodes is kept because a successor re-reading r4 against this document would
otherwise conclude one of them is in error: r4's remark that renormalising by equal A0 effect makes D_lo "lead by a
wider margin" is **false of the ratio** — that renormalisation divides both rows by the same constant, leaving it
at 1.0674 at cell 309 either way — and **true of the absolute difference**, which the same renormalisation
multiplies by eleven, 0.005505 to 0.060556. Both documents are arithmetically exact and are describing different
quantities. The rest of those episodes are in the register rows above and are not re-told here.

**C2 wrote here that "the self-audit is now finding these faster than the reviews are". That was false when
written and had been false for six rounds** (r13 FAIL 3). Derive it from the register above —
`grep -c 'self-caught' ERRATUM_C2.md` against the row count — and the position is: of the instances recorded,
**four** were self-caught, all of them in rounds four and five, and **none** of the twelve added in rounds six to
eleven. The self-audit stopped finding them, and the reviews did not.

Checking inherited claims at source is necessary and has not been sufficient: C2 verified the two it took from r3
(the D_lo cap at 1 never executes, max D_lo × 1.1 across the tail being **0.932851**; `deflated_consume` does
type-check its inputs and post-check r2 ≤ r1), and r4 confirmed both to the digit — and that same round still
shipped an unrequested field whose effect it had not computed.

The operational lesson for a successor is narrower than "be careful". It is: **when a review asks for one change,
make that change and stop.** Most of the instances above are C2 doing more than was asked and not checking the
extra part; the rest are C2 failing to clean up after a change it did make — usually a neighbouring sentence the
fix should have carried along. Counting them by kind is left to the table, deliberately. Any sentence in this
namespace beginning "a further reason", and any artifact field or summary figure not traceable to a specific
review request or gate clause, should be treated as unverified until checked.

The failure mode has a visible signature: it never touched a computed quantity. In every round, **no Γ,
magnitude, margin, requirement, gap fall, class or adopted-subset value has changed** — r5 confirmed by diffing
every leaf of the D1 evidence across its whole history that exactly nine leaves of it have ever changed, all C_T
sensitivity on 307–309. Every instance was in labelling, framing, or an ornament attached to a result that kept
reproducing bit-exactly under every independent implementation written against it. That is worth knowing about a
campaign: its
arithmetic was never the weak part, and its prose always was.

A successor should expect this failure mode from this campaign's authorship specifically.

*(The two paragraphs that stood here until pre-freeze review r5 were the r3-era version of the text above, left
in place when round four replaced the opening with the table. They claimed C2 had avoided "repeating the pattern
a fourth time" — contradicted by the table twenty lines up, which records round three producing instances three
and four — and re-asserted the leaf count r4 had already corrected. A stale, self-contradicting remnant left by a
repair, inside the section about stale remnants left by repairs. Sixth instance; r5 FAIL 1.)*

## Cell 306

The predecessor's reviewer set three conditions before 306 may be adopted. The disposition is in
`phase_d/CELL_306_ADOPTION.md`. In short: the finer partition was delivered and worked (margin 1.9 % → 11.2 %); the
independent re-certification is delivered only in the weaker sense the evidence supports — every field of all
eighteen artifacts reproduces on a host whose OS, architecture, Python and Arb/FLINT build are recorded, but the
registry's build host is recorded nowhere, so no *second host* is evidenced (**N10**); and the margin floor
**cannot honestly be
set by C2**, because C2 has already seen the margin. It is therefore referred to the adjudicator, with C2's
decision pre-committed in both directions before the answer is known.
