# Campaign C2 — erratum, and the disposition of the independent pre-freeze review

The independent fresh-context pre-freeze review (`review/REVIEW_C2_PREFREEZE.md`, at commit `5a94568a`) returned
**NOT_READY**: 79 checks, 60 PASS, 10 INFO, 3 NOT_CHECKABLE_LOCALLY, **6 FAIL**. It reproduced every
decision-relevant number bit-exactly from an implementation written independently from the theorem documents, and
found no arithmetic error anywhere in C2. What it blocked the freeze on was what would have been frozen *alongside*
the arithmetic.

This document is the disposition of all six, plus the corrections that came out of the INFO rows. **No number C2
published has changed.** The class is still `D_PARTIAL`, the closed subset is still {305, 306}, and the gate is
untouched.

## The one thing that cannot be repaired at source

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

## Repaired at source

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
  recorded in the artifact. So the registry is now demonstrably re-verifiable, and separately the C1 reviewer's
  complaint that `REGISTRY_C2.json` records no host or toolchain is answered by the two artifacts that do.

  This one is worth stating plainly: a review row marked **INFO**, not FAIL, and phrased only as "not demonstrated
  in-repo", led to the discovery that a verification tool this campaign pointed at as evidence of its own
  soundness had never worked. The lesson is the row's, not C2's: a check nobody has run is not a check.

## Corrections arising from the INFO rows

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
(`review/REVIEW_C2_PREFREEZE_R2.md`): 71 rows, 55 PASS, 5 NOTE, 3 INFO, **3 FAIL**. It confirmed every repair
above independently — including re-certifying cell 306 artifacts on the Arb/FLINT stack, which neither earlier
reviewer could do — and it found that on the one point where C2 corrected the *first* reviewer (the ×0.9
convention and the D_lo-vs-τ ordering), **C2 was right**. Its three FAILs:

| | finding | repair |
|---|---|---|
| **r2 FAIL 65** | C2's *newly added* claim that ×0.9 is disqualified because it drives C_T below τ is **wrong**: the published ÷1.1 convention does exactly the same thing on exactly the same three cells (307: 4.846842 < 4.851873; 308: 4.553601 < 4.633777; 309: 4.277739 < 4.418493). | Claim withdrawn in `phase_d/D1_BLOCKER_DIAGNOSIS.md`. The only reason to prefer ÷1.1 is symmetry in A0 = τ/D_lo, and the text now says that and nothing more. A repair that introduced a new error, caught before freeze. |
| **r2 FAIL 66** | Consequently the published C_T sensitivity figures for 307/308/309 were computed **outside the Lemma Dv′ hypotheses**, reached only because `c2_d1_blocker.atom_dv_prime` is an unguarded local copy of the pinned consumer, which would have refused. Undisclosed. | Guard added, enforcing the four premise inequalities that `deflated_consume.atom_constants_r2` validates (not a byte-for-byte copy: the pinned consumer also type-checks its inputs and post-checks r2 ≤ r1). The C_T column now reports the **admissible best C_T = τ**, giving +1.3681 / +1.1502 / +0.9335 % against the inadmissible +1.3823 / +1.3945 / +1.3887 %. Evidence regenerated (`601f2f33…`). Γ, magnitudes, blocker shares and every other sensitivity row are bit-unchanged — r3 confirmed the leaf-level diff is **exactly twelve** values, all in the three C_T rows. **The inference C2 drew from this was itself wrong and r3 corrected it**: a clamped row is not a 10 % improvement (the admissible cuts are 8.997 / 7.490 / 6.100 % against 9.0909 % elsewhere), and per unit of C_T removed the response is flat and slightly *rising* across the tail. C_T is not a weaker lever at 309; it is a **nearly exhausted** one, with only 6.1 % of travel left before it meets τ. `effective_improvement` and `gain_per_unit_of_input_moved` are now recorded per row so the columns cannot be misread as like-for-like. |
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

A third focused review ran on the r2 repairs at `55c4cf00` (`review/REVIEW_C2_PREFREEZE_R3.md`): 39 rows, 31 PASS,
7 NOTE, **1 FAIL**. It re-ran all three producers and confirmed each reproduces **byte-for-byte**, verified the
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
  r2 ≤ r1, and the relevant entry point is `atom_constants_r2`. Corrected in both places.

One NOTE was a credit C2 had not claimed, and it belongs in the record because it is evidence, not praise: when
`c2_recertify_306.py` was re-run only to correct a comment, **both Arb/FLINT passes genuinely re-executed** (~40
minutes) and every field other than the note string and two `cpu_seconds` values came back **bit-identical**. That
is a second, independent determinism replication of cell 306's eighteen artifacts on the macOS/arm64 FLINT build,
obtained incidentally. It is recorded here because it strengthens the FAIL 51 disposition above.

## Cell 306

The predecessor's reviewer set three conditions before 306 may be adopted. The disposition is in
`phase_d/CELL_306_ADOPTION.md`. In short: the finer partition was delivered and worked (margin 1.9 % → 11.2 %); the
independent re-certification is now delivered on a genuinely second host; and the margin floor **cannot honestly be
set by C2**, because C2 has already seen the margin. It is therefore referred to the adjudicator, with C2's
decision pre-committed in both directions before the answer is known.
