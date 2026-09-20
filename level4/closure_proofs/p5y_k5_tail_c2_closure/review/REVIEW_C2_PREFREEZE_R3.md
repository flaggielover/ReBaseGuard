# Campaign C2 — third independent pre-freeze review (focused)

**VERDICT: NOT_READY** — 39 rows, 31 PASS, 7 NOTE, **1 FAIL**. One freeze-blocking defect, text only, one
sentence: the claim r2 refuted as FAIL 65 and that C2 withdrew from `phase_d/D1_BLOCKER_DIAGNOSIS.md` is still
asserted, in the present tense and as a standing reason, in `ERRATUM_C2.md` lines 84–85 — in the same file whose
own r2 disposition table, 45 lines further down, records it as withdrawn. Everything else in scope is genuinely
repaired, and the repair introduced no new error that I can find.

---

## Reviewer context

I am a fresh-context independent reviewer. I wrote none of this work, and this is the third independent
pre-freeze review of Campaign C2. My scope was deliberately narrow: whether r2's three FAILs (65, 66, 10) are
genuinely repaired, whether the repair introduced a new error, whether anything else in the namespace moved, and a
freeze verdict. I did not re-do rounds one and two.

**What I re-derived myself, from the committed evidence, with stdlib Python 3 and `fractions.Fraction`:**

- `C_T`, `τ`, `D_lo`, `Ābar` for all five tail cells read directly out of
  `p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json`, and the four comparisons that FAIL 65
  turns on — `C_T/1.1 vs τ`, `C_T×0.9 vs τ`, `D_lo×1.1 vs 1`, `τ/1.1 vs 1` — on every cell.
- The premise set of the pinned consumer, by reading
  `p5y_k5_perron_deflated_resolvent/code/deflated_consume.py` lines 83–109 (`atom_constants`,
  `atom_constants_r2`) and comparing it line by line against the new guard in `code/c2_d1_blocker.py`.
- A full structural diff of `evidence/phase_d1/C2_D1_BLOCKER.json` at `ef58310c` against the committed one at
  `55c4cf00`, key by key, to the leaf, using `git show` for the old copy.
- `ok = bool(margin > 0) and bool(wmin >= 0)` at `p5y_k5_perron_deflated_resolvent/code/taboo_certify.py:228`,
  and the two places `c2_recertify_306.py` asserts `certified is True`.
- Every diagnostic deviation recorded in `evidence/prefreeze/C2_RECERTIFY_306.json`, recomputed as exact
  rationals from the published/recomputed field pairs, and the block margin the note cites.
- Per-unit C_T elasticities, to test whether the corrected figures mean what the document says they mean.

**What I re-ran:**

- `code/c2_d1_blocker.py` — **byte-identical** to the committed artifact (0.5 s).
- `code/c2_mutations.py` — **byte-identical**, 43 applied / 40 detected / 3 equivalent / 0 undetected / `pass:
  true` (1.8 s).
- `code/c2_critical_ratio.py` — **byte-identical** (7.8 s).

**What I did NOT check — see the closing section.** In particular I did not re-run the Arb/FLINT registry
verification or the 306 re-certification, and I did not re-verify rounds one and two except where I depended on
them.

---

## Checklist

### A. r2 FAIL 65 — the withdrawn convention claim

| # | check | verdict | evidence |
|---|---|---|---|
| 1 | does ÷1.1 drive `C_T` below τ on 307/308/309? | PASS | **yes**, my own exact arithmetic from `REGISTRY_C1.json`: 307 `4.846842 < 4.851873`; 308 `4.553601 < 4.633777`; 309 `4.277739 < 4.418493`. The three pairs printed in `D1_BLOCKER_DIAGNOSIS.md` are correct to the digit |
| 2 | does ×0.9 do the same, on the same three? | PASS | yes: 307 `4.798374 < 4.851873`; 308 `4.508065 < 4.633777`; 309 `4.234961 < 4.418493`. r2 is right; the two conventions are disqualified on exactly the same cells |
| 3 | are 305 and 306 unaffected under both? | PASS | 305 `C_T/1.1 = 5.480867`, `×0.9 = 5.426058`, both above `τ = 5.291155`; 306 `5.155440` / `5.103886` above `5.070746`. The document's "Cells 305 and 306 are unaffected; C_T/1.1 stays above τ there" is exactly right |
| 4 | does `phase_d/D1_BLOCKER_DIAGNOSIS.md` §2 now state this correctly, without over- or under-claiming? | PASS | lines 51–56 withdraw the claim in terms, name the review, and state the correct general fact — "Neither convention is 'uniformly applicable' in that sense, so this is not a reason to prefer either one." No residual hedge, no re-litigation |
| 5 | is the surviving justification (symmetry in `A0 = τ/D_lo`) actually valid? | PASS | **yes.** `A0 = Ā_eff = min(Ā, τ/D_lo)`, and on all five tail cells `τ/D_lo < Ā` (e.g. 309: `5.210202 < 6.900983`), so `A0 = τ/D_lo` in fact. Under ÷1.1 the two perturbations `τ → τ/1.1` and `D_lo → 1.1·D_lo` each send `A0 → A0/1.1` — literally the same multiplicative response. Under ×0.9 they are `0.9·A0` and `A0/0.9 ≈ 1.111·A0`, which are not symmetric. The stated reason is the real one and it is sound |
| 6 | does the withdrawn claim survive anywhere else in the namespace? | **FAIL** | **yes — `ERRATUM_C2.md` lines 84–85.** See note 1 |

### B. r2 FAIL 66 — the guard and the admissibility clamp

| # | check | verdict | evidence |
|---|---|---|---|
| 7 | is the new guard equivalent to the pinned `deflated_consume.atom_constants`? | NOTE | equivalent on the inequalities that bind, **not literally equivalent**, and the pinned consumer for Lemma Dv′ is `atom_constants_r2`, not `atom_constants`. See note 2. Immaterial to every number published |
| 8 | is clamping `C_T` to τ the right treatment? | PASS (opinion) | **yes, on balance** — it is strictly more informative than reporting the row unavailable, and it is disclosed in both the artifact and the prose. But it is the right treatment only with the qualification in note 3, which the document does not make |
| 9 | are the corrected figures right? | PASS | **my own run of the committed script**: 307 `0.013680760091052447` → **+1.3681 %**; 308 `0.011501645296577124` → **+1.1502 %**; 309 `0.009335012952053988` → **+0.9335 %**. All three match the document and the ERRATUM to four decimal places |
| 10 | are 305 and 306 unchanged at +1.3599 / +1.3672 %? | PASS | `0.013598570…` and `0.013671530…`, and the leaf-level diff against `ef58310c` shows **no change at all** on those two cells |
| 11 | is everything else bit-unchanged between the old and new `C2_D1_BLOCKER.json`? | PASS | **verified exhaustively.** A key-by-key structural diff of the two JSON trees returns exactly **twelve** differences: three added `admissibility_clamp` strings and the nine `magnitude`/`delta_vs_base`/`relative_gain` floats of the `C_T` rows on 307/308/309. Γ, `M_after`, `M_needed`, the required reductions, the twelve radius terms, all five grouped shares, `DOMINANT_BLOCKER_1/2/3`, `order3_attribution`, and every `D_lo`/`τ`/`D1`/`D2`/`A0`/`A1`/`A2`/`A_all` row on **all five** cells are byte-for-byte identical. C2's claim is exactly true |
| 12 | is the disclosure adequate and honest, or does it minimise? | PASS | it does not minimise. The document names the review and the note numbers, prints the inadmissible figures it is replacing, quantifies the overstatement in percentage points (0.01 / 0.24 / 0.46 pp), says the unguarded local copy "returned a number anyway", and the machine-readable artifact carries the clamp string in the row itself. The ERRATUM row is equally direct, including "A repair that introduced a new error, caught before freeze" on FAIL 65. This is the disclosure standard the programme should want |
| 13 | does any conclusion depend on the old inadmissible numbers? | PASS | **no.** `+1.3823 / +1.3945 / +1.3887` appear in exactly two places outside `review/`: `D1_BLOCKER_DIAGNOSIS.md:70` and `ERRATUM_C2.md:131`, both explicitly labelled as the superseded values. `D_STAGE_DECISION.md`, `D_PRIME_OPPORTUNITY.md`, `R_STAGE_DESIGN.md`, `README.md` and `MEASURE_CHANGE_SELF_AUDIT.md` contain no C_T sensitivity figure at all — their C_T references are to the τ/C_T regression (a registry-composition fact) and to the safe-side pass, neither touched. §2's three findings rest on `D_lo`, τ, `D2` and `A0 = τ/D_lo ≥ τ` |
| 14 | is the clamped row comparable to the other columns it sits beside? | NOTE | no, and nothing says so. See note 3 |
| 15 | is the "same treatment D_lo has always had at its cap of 1" analogy accurate? | NOTE | the branch exists but has **never executed**. See note 4 |

### C. r2 FAIL 10 — the premature adoption declarative

| # | check | verdict | evidence |
|---|---|---|---|
| 16 | does `phase_d/CELL_306_ADOPTION.md` still assert a terminal governance state? | PASS | no. "It is adopted." is gone. The replacement is explicit in the other direction: "It is not *adopted* yet, and nothing in this campaign may say that it is: adoption is a terminal governance state that the freeze, qualification, seal, deterministic double consumption and independent adjudication chain confers, and none of those has happened." It self-cites the review note that caught it |
| 17 | does any other file in the namespace assert adoption, closure-as-adopted, or another unconferred terminal state? | PASS | **swept the whole namespace.** Every occurrence of "adopt*" outside `review/` is one of: a reference to a *predecessor's* adopted inputs (`ADOPTED_TAIL_INPUTS`, the adopted Aux3 source error, the adopted lower front, the adopted record's R2 interval — all legitimate, all upstream); an explicitly conditional branch ("adopt {305, 306}", "adopt 305 only", "when the adjudication chain completes", "before cell 306 may be adopted"); or an explicit negation (`README.md` lines 9 and 12: "**not adopted**", twice). I also swept for `is sealed` / `is qualified` / `is frozen` / `is closed` / `stands adopted` / `has been adopted` / `K5 CLOSED`: the only hit outside `review/` is `ERRATUM_C2.md:40` "the gate is the copy that is frozen", which is a true statement about `config/FEASIBILITY_GATES_C2.json` at `87309610`. **No second instance of r2's defect exists** |
| 18 | did the rewrite degrade any neighbouring sentence? | NOTE | one, harmlessly. See note 5 |

### D. new errors introduced by this repair

| # | check | verdict | evidence |
|---|---|---|---|
| 19 | is the clamp logic correct in every branch? | PASS | the clamp is evaluated **before** `atom_dv_prime` is called, so `p["C_T"] = p["tau"]` is already in place when the guard runs and `C >= tau` holds at equality. I checked the guard against every one of the five perturbed tuples per cell: the `τ` row lowers τ to `τ/1.1` (min `4.016811 ≥ 1` ✓) while leaving `C_T` at its registry value, so `C ≥ τ` strengthens; the `D_lo` row only raises `D_lo` (`D_lo > 0` unaffected); `D1`/`D2` touch neither `τ` nor `C_T`. `PremiseRefusal` is therefore never raised on this input set — which the byte-identical re-run proves constructively, since every row is present in the output |
| 20 | does the `D_lo` clamp still behave as before? | PASS | the only change to that branch is the added `clamped = "D_lo capped at 1"` assignment; the `if p["D_lo"] > 1: p["D_lo"] = F(1)` test and body are untouched. `clamped` is initialised to `None` on every iteration via the tuple assignment `p, clamped = dict(op) | better, None`, so no value leaks between rows. No `D_lo` row in the committed artifact carries an `admissibility_clamp` key, before or after — consistent |
| 21 | could the guard now refuse an input on which the old code legitimately succeeded, silently changing something? | PASS | **no.** The guard's four conditions hold on the base tuple of all five cells (`τ ≥ 1`: 4.418–5.291; `C_T ≥ τ` ✓; `D_lo > 0`: 0.769–0.848; `Ā ≥ 1`: 6.90–8.29), and on every perturbed tuple except the three C_T rows that are now clamped first. The only calls the guard would have refused are precisely the three illegitimate ones. Nothing else in the namespace imports `atom_dv_prime` — it has no other caller |
| 22 | does `c2_d1_blocker.py` reproduce the committed artifact byte-for-byte? | PASS | **yes.** `sha256 62531bf564ec9439b49c348381492a8e1be88d4863300be47258d9a684f29b15`, identical to the committed file and to the `62531bf5…` prefix cited in `D1_BLOCKER_DIAGNOSIS.md:3` and `ERRATUM_C2.md:131`. The stale `e929e857…` prefix appears nowhere outside `review/` |
| 23 | does `c2_mutations.py` reproduce 43/43 and a byte-identical artifact? | PASS | `{"applied": 43, "real_mutants": 35, "static_assertions": 8, "detected": 40, "equivalent": [M19, M20, M32], "undetected": [], "pass": true}`, `sha256 512180f3…`, `cmp` clean against `evidence/prefreeze/C2_MUTATIONS.json` |
| 24 | does `c2_critical_ratio.py` reproduce byte-identically? | PASS | `cmp` clean against `evidence/phase_d5/C2_CRITICAL_RATIOS.json`; C2 ratios 72.71753 / 54.86736 / 37.32219 / 23.26035 / 14.15799 |
| 25 | `DIAGNOSTIC_NOTE` claim — `certify_block` sets `ok = (margin > 0 and wmin >= 0)` | PASS | **true, verbatim.** `taboo_certify.py:228`: `ok = bool(margin > 0) and bool(wmin >= 0)`, where `margin = min(mins[1], mins[-1])` over both expansion endpoints and `wmin` is the reachable-set minimum of `w`. It is returned as the artifact's `certified` field at line 231 |
| 26 | `DIAGNOSTIC_NOTE` claim — `certified is True` is asserted unconditionally in **both** passes | PASS | **true, and doubly so.** (i) `main`'s artifact loop, which runs for both `("determinism_256", 256, True)` and `("safe_side_384", 384, False)`, contains `if not r["certified"]: raise SystemExit(f"{name} fails to certify at {bits} bits")` — no `strict` guard. (ii) `compare`'s first branch, `if isinstance(p_, bool) or isinstance(g_, bool): good = (p_ == g_ and g_ is True)`, is evaluated *before* the `elif strict` branch and so applies in both passes. The reviewer's argument, which C2 adopted, is sound: the diagnostics' load-bearing content (`margin > 0`, `wmin ≥ 0`) is re-checked at 384 bits even though their digits are not |
| 27 | `DIAGNOSTIC_NOTE` claim — worst violating deviation `allowance_upper` +5.19e-30 relative, +3.85e-34 absolute, block margin 0.156 | PASS | **all three verified as exact rationals** from the committed artifact. The nine violating deviations are all in `safe_side_384`; the largest is `taboo_block_306_02.json` / `allowance_upper`, relative `+5.190e-30`, absolute `+3.852e-34`, and that block's `margin_lower_bound` is `18058665028400143779873778337040821451296891207372565209322790853091095303501 / 2^256` = **0.155958…** ≈ 0.156. The note's "Every one of those deviations was in margin_lower_bound or allowance_upper" also holds — no `w_min_lower_bound` violation exists |
| 28 | `C2_RECERTIFY_306.json` verdict and note | PASS | `"verdict": "BOTH_PASSES_OK"`, both passes `all_ok: true`, 18 artifacts, `diagnostic_deviations: {count: 27, worst_relative: 5.3188e-30}`. The `diagnostic_policy.why` string is **character-identical** to the module's `DIAGNOSTIC_NOTE` literal (I reconstructed the literal from source and compared), so the artifact was regenerated from the corrected module and not hand-edited |
| 29 | what else moved in `C2_RECERTIFY_306.json`? | NOTE | only `cpu_seconds`, 1653.6 → 1153.9 and 1691.8 → 1204.2. See note 6 — this is a *strengthening* and it is unremarked |

### E. integrity

| # | check | verdict | evidence |
|---|---|---|---|
| 30 | `git diff --name-status 5289b6ce..HEAD` — additive and inside the namespace? | PASS | 136 paths, **every one `A`**, every one under `level4/closure_proofs/p5y_k5_tail_c2_closure/`. Filtering the diff for anything outside that prefix returns nothing |
| 31 | frozen gate untouched? | PASS | `shasum -a 256 config/FEASIBILITY_GATES_C2.json` = `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f` — matches. `git log -- config/FEASIBILITY_GATES_C2.json` returns **exactly one** commit, `87309610`, the freeze commit |
| 32 | `code/c2_d5_forecast.py` unmodified since `5a94568a`? | PASS | its last touching commit is `5a94568a`, and it does not appear in `git diff --name-status 5a94568a..HEAD` |
| 33 | `evidence/phase_d5/C2_D5_FORECAST.json` unchanged? | PASS | same: last touched at `5a94568a`, absent from the `5a94568a..HEAD` diff. The class, the closed set and the gap falls have not moved |
| 34 | predecessor namespaces byte-unchanged? | PASS | `git diff --name-only 5289b6ce..HEAD` over `p5y_k5_m5_tail_closure`, `p5y_k5_tail_operator_registry`, `p5y_k5_perron_deflated_resolvent`, `p5y_k1_cover_ledger_successor` returns empty. The `taboo_certify.py` sha pin `ced9422c…` in `c2_recertify_306.py` is checked at run time against the unmodified file |
| 35 | `main` untouched? | PASS | `main` = `c123b9bb`, which is exactly `git merge-base main HEAD`. The branch is strictly ahead; nothing was written to `main` |
| 36 | coverage map r4 untouched, no r5? | PASS | `p5y_k5_lower_front_order3/evidence/tc_r1/K5_COVERAGE_MAP_R4.json` last touched at `f2ac1eb3`; the whole `p5y_k5_lower_front_order3/` tree is absent from `5289b6ce..HEAD`. No r5 coverage map exists anywhere (the `*r5*` hits in `level4` are all unrelated executor/majorant artifacts in other namespaces) |
| 37 | does anything pre-empt freeze, qualification, sealing or adjudication? | PASS | no — see row 17. `phase_r/R_STAGE_DESIGN.md` opens with the blocking precondition, `OPEN_NOTES_DISPOSITION_C2.md:77` refers 306 out to the adjudicator, `README.md` says "not adopted" twice, and `CELL_306_ADOPTION.md` now states the chain explicitly |

### F. other

| # | check | verdict | evidence |
|---|---|---|---|
| 38 | is the ◆ cross-reference in §2 correct? | NOTE | "see the ◆ note above" — the ◆ note is *below* that paragraph. See note 7 |
| 39 | do the two "worst deviation" numbers in the 306 artifact agree? | NOTE | they measure different things and both are right, but a reader will read them as a discrepancy. See note 8 |

---

## Notes

### Note 1 (FAIL) — the withdrawn convention claim is still asserted in `ERRATUM_C2.md`

`ERRATUM_C2.md`, under **"Corrections arising from the INFO rows"**, lines 82–85:

> The review also suggested that the other convention (× 0.9) reverses the D_lo-vs-τ ordering. **It does not**, and
> C2 says so: that comparison takes τ from one convention and D_lo from the other. Recomputed on all five cells
> under both registries and both conventions, D_lo outranks τ everywhere. **A further reason to prefer the published
> convention is recorded: × 0.9 drives C_T below τ at cell 307, violating the Lemma Dv′ premise C ≥ τ outright.**

The bolded sentence is the claim r2 raised as FAIL 65. Its factual half is true — `C_T(307) × 0.9 = 4.798374 <
4.851873` — but the sentence does not assert the fact, it asserts the *inference*: that the fact is "a further
reason to prefer the published convention". It is not, because `C_T(307) ÷ 1.1 = 4.846842 < 4.851873` does the
same thing, which is the whole content of r2 note 1 and which I re-derived independently in rows 1 and 2.

`phase_d/D1_BLOCKER_DIAGNOSIS.md` §2 was repaired. `ERRATUM_C2.md` was not — the repair commit added a new
section ("Dispositions from the SECOND pre-freeze review") whose FAIL 65 row says the claim is "withdrawn in
`phase_d/D1_BLOCKER_DIAGNOSIS.md`", and left the original paragraph standing 45 lines above it, in the present
tense, unmarked and unqualified. The file now contradicts itself: line 85 offers the reason, line 130 says the
reason is wrong.

I make this freeze-blocking rather than a note, for three reasons.

1. **It is the same defect r2 blocked on, in the same namespace, at freeze time.** r2's FAIL 65 was not "the
   diagnosis document says X"; it was "C2 asserts X". C2 still asserts X. A freeze seals the namespace, not one
   file in it.
2. **`ERRATUM_C2.md` is the register an adjudicator reads first.** It is the document that exists specifically to
   record what was wrong and what was corrected. A refuted claim surviving *in the errata register*, under a
   heading that reads "Corrections", is worse placed than it was in the diagnosis.
3. **It is the campaign's own stated standard.** `D1_BLOCKER_DIAGNOSIS.md` line 27: "a document that disagrees
   with its own evidence file should not be frozen, so it is fixed here rather than explained away." A document
   that disagrees with itself is not a better case.

**What must change:** delete the sentence at `ERRATUM_C2.md` lines 84–85, or restate it the way §2 was restated —
that the fact is true of *both* conventions and is therefore a reason to prefer neither, with the surviving reason
being symmetry in `A0 = τ/D_lo`. One sentence. Nothing else in the file needs to move, and no number changes.

I checked for other survivals of the same kind and found none: `D_STAGE_DECISION.md`, `D_PRIME_OPPORTUNITY.md`,
`R_STAGE_DESIGN.md`, `README.md`, `MEASURE_CHANGE_SELF_AUDIT.md` and `OPEN_NOTES_DISPOSITION_C2.md` contain no
statement about the sensitivity convention at all.

### Note 2 (observation) — the guard is not *literally* the pinned consumer, and cites the wrong one

`ERRATUM_C2.md:131` says the local copy "now refuses exactly as `deflated_consume.atom_constants` does", and the
in-code comment says the same. Two inaccuracies, both immaterial:

- **Wrong consumer.** `atom_dv_prime` re-implements `atom_constants_r2` (Lemma Dv′, the `Ā_eff = min(Ā, τ/D_lo)`
  form), not `atom_constants` (theorem AD, the `A0 = τ/D_lo` form). r2 named `atom_constants_r2` correctly in its
  FAIL 66 row. The `C ≥ τ` test does live in `atom_constants`, which `atom_constants_r2` calls first — so the
  citation is not *wrong* so much as one level too shallow, and it loses the `Ā ≥ 1` test, which comes from
  `atom_constants_r2` alone and which the new guard does include.
- **Not exhaustive.** The pinned path additionally enforces (i) `isinstance(v, F) and v >= 0` on each of `τ, C,
  D_lo, D1, D2, k1, k2` and on `Ā`, and (ii) the post-condition `A_j^{r2} ≤ A_j^{r1}` for `j ∈ {0,1,2}`. The
  guard has neither.

Neither omission can bite here. `D1`/`D2` come from the registry non-negative and are only ever multiplied by
`10/11`; every value in the module is a `Fraction` by construction; and the post-condition is an algebraic
identity given non-negativity, since `A_j^{r1} = (τ/D_lo)·(tame factor)` and `A_j^{r2} = min(Ā, τ/D_lo)·(the same
tame factor)`. So the guard is equivalent *on this input set*, which is what the numbers require. But "refuses
exactly as" is a stronger claim than the code supports, and a successor that reuses `atom_dv_prime` on inputs C2
never fed it would not get the pinned consumer's behaviour. I would prefer the honest form: "refuses on the same
four inequalities as the pinned `atom_constants` / `atom_constants_r2` path; the remaining type and
non-negativity checks are not reproduced because every input here is a non-negative `Fraction` by construction."
Not freeze-blocking.

### Note 3 (observation) — is clamping to `C_T = τ` the right treatment? Yes, with one qualification the document does not make

The parent question. My answer is **yes, clamping is better than reporting the row unavailable** — but the
clamped row is not what its column header says it is, and nothing in the campaign says so.

**Why clamping is right.** The decision the table exists to inform is "which certified input is worth attacking".
For that question, "the largest admissible improvement in `C_T` buys 0.93 % at cell 309" is a strictly stronger
and more actionable statement than "n/a". Reporting the row as undefined would discard a real, correct,
lemma-admissible fact, and would leave a reader unable to compare `C_T` against `D_lo` at all on the three cells
where the comparison matters most. `C_T = τ` is also genuinely admissible, not a formal limit: the guard tests
`C >= tau`, equality passes, and the resulting constants are honest Lemma Dv′ constants (`A0 = min(Ā, τ/D_lo)` is
untouched by the `C_T` perturbation, and `A1`, `A2` fall). And the alternative C2 rejected — publishing the
unclamped number — is genuinely unsound, so the choice was between clamping and withholding, not between clamping
and the status quo.

**The qualification.** Every other column in that table is a 10 % improvement. The clamped `C_T` cells are not:
the admissible cuts are **8.997 %** at 307, **7.490 %** at 308, **6.100 %** at 309, against 9.0909 % everywhere
else. The JSON key is still `sensitivity_10pct_improvement`, and the document's column header is still `C_T`
under "a **10 % improvement in one input**". So the reader is invited to compare `+0.9335 %` against `+8.7186 %`
as like for like, and they are not like for like — one is the response to a 6.1 % cut, the other to a 9.09 % cut.

This matters for one sentence. The document says: "**The correction strengthens the section's conclusion**: C_T's
real lever at cell 309 is 0.93 %, not 1.39 %, against D_lo's 8.72 %." As a statement about *what is achievable*
that is correct and I endorse it. But it reads as a statement about *sensitivity*, and `C_T`'s sensitivity did
not fall at all — per unit of `C_T` reduction it is essentially flat across the tail, and marginally **rising**:

| cell | admissible cut | gain | gain per 1 % of `C_T` cut |
|---|---|---|---|
| 305 | 9.0909 % | 1.3599 % | 0.1496 |
| 306 | 9.0909 % | 1.3672 % | 0.1504 |
| 307 | 8.997 % | 1.3681 % | 0.1521 |
| 308 | 7.490 % | 1.1502 % | 0.1536 |
| 309 | 6.100 % | 0.9335 % | **0.1530** |

So the correct reading is not "C_T is a weaker lever at 309" but "**C_T has almost no headroom left at 309** — it
is already within 6.1 % of the floor Lemma Dv′ imposes on it". That is a *different* and arguably more useful
finding than the one the document states, and it points the same way, so no conclusion moves. I would add the
effective cut to each clamped row — the artifact already computes `p["tau"]`, so `"effective_improvement":
0.060996…` is one line — and one clause to the ◆ note. Recommended, not freeze-blocking.

### Note 4 (observation) — the `D_lo` precedent has never actually bound

Both `D1_BLOCKER_DIAGNOSIS.md` ("exactly as the D_lo column has always been capped at 1 because D is a
probability") and `ERRATUM_C2.md` ("the same treatment D_lo has always had at its cap of 1") justify the clamp by
analogy to the `D_lo` cap. The analogy is to a code path that **has never executed in this campaign**:

| cell | 305 | 306 | 307 | 308 | 309 |
|---|---|---|---|---|---|
| `D_lo` | 0.768609 | 0.790892 | 0.810385 | 0.828872 | 0.848046 |
| `D_lo × 1.1` | 0.845470 | 0.869982 | 0.891423 | 0.911759 | **0.932851** |

The maximum is 0.9329, so `p["D_lo"] > 1` is false on every cell and no `D_lo` row in `C2_D1_BLOCKER.json`
carries an `admissibility_clamp` key — I confirmed this against the committed artifact. "Has always been capped"
invites the reader to believe the `D_lo` column in the very table they are reading is a clamped column. It is
not. The precedent is real as a *design intent* in the code, and the analogy still does the argumentative work
C2 wants, but the phrasing overstates it. "Exactly as the `D_lo` row would be capped at 1, D being a probability"
would be accurate. Not freeze-blocking.

### Note 5 (observation) — a small degradation in the `D_PARTIAL` sentence

The FAIL 10 rewrite also changed `CELL_306_ADOPTION.md` line 100 from "**In either branch cell 305 is adopted**"
to "**In either branch cell 305 is the one carried to adoption**". Removing the terminal assertion was right, but
"the one" is wrong in the `{305, 306}` branch, where 305 is not the only cell carried. "In either branch cell 305
is carried to adoption" says what is meant and is true in both branches. Cosmetic.

### Note 6 (observation) — the 306 re-certification was actually re-run, and nobody says so

`C2_RECERTIFY_306.json` changed in exactly three places: the `diagnostic_policy.why` string and the two
`cpu_seconds` fields (`1653.6 → 1153.9`, `1691.8 → 1204.2`). Since `cpu_seconds` is wall-clock-derived and the
note is a module constant, this is a **full ~40-minute re-execution** of both Arb/FLINT passes over all eighteen
artifacts — not a text patch to the artifact. Every one of the several thousand other fields across 117 strict
comparisons and 45 asserted safe-side comparisons came back **bit-identical**, including all 27 diagnostic
deviations.

That is a meaningful independent result: it is a second determinism replication of the pass that r2 could run and
neither earlier reviewer could, and it is stronger evidence than the disclosure it was incidental to. It is
recorded nowhere. The `ERRATUM_C2.md` FAIL 66 row mentions regenerating `C2_D1_BLOCKER.json` (`62531bf5…`) but
says nothing about `C2_RECERTIFY_306.json`. Worth one line in the ERRATUM. This is a *missing credit*, not a
defect.

### Note 7 (observation) — the ◆ cross-reference points the wrong way

`D1_BLOCKER_DIAGNOSIS.md` line 54: "÷ 1.1 does exactly the same thing, on exactly the same three cells — see the
◆ note **above**." The ◆ note is nine lines *below*, after the table. Trivial.

### Note 8 (observation) — two different "worst deviations" in the same artifact

`C2_RECERTIFY_306.json` reports `diagnostic_deviations.worst_relative = 5.3188e-30`; the `DIAGNOSTIC_NOTE` in the
same file says "The worst violating deviation was allowance_upper at +5.19e-30". Both are correct and they are
different quantities: `5.3188e-30` is the worst deviation of *any* sign (`taboo_block_306_05` / `allowance_upper`,
recomputed **below** published — the bound holds, so it is not a violation), while `5.190e-30` is the worst
deviation in the *violating* direction (`taboo_block_306_02` / `allowance_upper`). The note's wording is precise
and I verified both figures. But a reader comparing `5.19e-30` in the prose against `5.3188e-30` in the adjacent
field will suspect an inconsistency. Saying "worst violating (the worst deviation of either sign is 5.32e-30, and
it is on the safe side)" would close it. Cosmetic.

---

## What I did not check

- **Rounds one and two.** I relied on `REVIEW_C2_PREFREEZE_R2.md` for the six round-one repairs, for the
  registry's 105/105 re-verification, for the 306 re-certification's independent Arb/FLINT replication, for the
  `12585997..8aee1fc5` git-history claims about `c2_recertify_306.py`, and for the adopted lower-front range.
  Where I depended on an r2 finding for a conclusion of my own — the ×0.9 and ÷1.1 comparisons, the admissible-cut
  figures, the `certify_block` and `certified is True` claims, the guard-vs-pinned-consumer comparison — I
  re-derived it from source or from the committed evidence rather than accepting it.
- **The Arb/FLINT stack.** I did not re-run the 105-artifact registry verification (~2.7 h) or
  `c2_recertify_306.py`. My conclusions about `C2_RECERTIFY_306.json` are read off the committed artifact and the
  module source; I verified the artifact was produced by the committed module (note 6, row 28) but not that the
  Arb computation inside it is right. r2 did check that, on its own host.
- **`code/c2_b0_verify.py`, `code/c2_refined_registry.py`, `code/c2_d5_forecast.py`** — not re-run. All three are
  outside the repair diff; the latter two were verified by r2 and rows 32–33 establish that `c2_d5_forecast.py`
  and its artifact have not moved since `5a94568a`.
- **The provenance of the upstream inputs** — `TCT_INPUTS_*`, `ADOPTED_TAIL_INPUTS.json`, `REGISTRY_C1.json`,
  `cells.json`, `tct_rule.py`. I read `REGISTRY_C1.json` as a given; its own certification is a predecessor's
  business and its namespace is unchanged (row 34).
- **The mathematics of Lemma Dv′, theorem TC-T and Lemma T themselves.** I checked that the code enforces the
  hypotheses the documents say it enforces, not that those hypotheses suffice for the lemmas.
- **Anything on AWS / SR / PS1.** Not touched, per scope.
- **The two committed review files' fidelity to what those reviewers wrote.** I read them as evidence of what was
  already checked; I have no way to verify they were committed verbatim.

---

## Verdict

**NOT_READY** — 39 rows: **31 PASS, 7 NOTE, 1 FAIL**.

**FAIL rows**

| # | one-line summary |
|---|---|
| 6 | `ERRATUM_C2.md` lines 84–85 still assert the ×0.9 convention claim that r2 refuted (FAIL 65) and that C2 withdrew from `D1_BLOCKER_DIAGNOSIS.md` in the same commit, contradicting the same file's own FAIL 65 disposition row at line 130 |

**To reach `READY_TO_FREEZE`:** delete or restate the sentence at `ERRATUM_C2.md` lines 84–85 so that it no longer
offers `× 0.9`'s violation of `C ≥ τ` as a reason to prefer `÷ 1.1`. Nothing else is required, no artifact needs
regenerating, and no published number changes.

**Recommended but not blocking:** note 3 (add the effective improvement to each clamped row and distinguish
"headroom" from "sensitivity" in the ◆ note's closing sentence), note 2 (soften "refuses exactly as" and cite
`atom_constants_r2`), note 4 ("would be capped" rather than "has always been capped"), note 6 (credit the
re-execution of the 306 re-certification), notes 5, 7 and 8 (cosmetic).

**On the substance, plainly:** r2's three FAILs are otherwise genuinely repaired; the repair introduced no new
arithmetic or code error that I could find, and I looked for one specifically; all three re-runnable artifacts
reproduce byte-for-byte; the correction to the `C_T` sensitivity figures is right, is well disclosed, and leaves
every other number in the campaign bit-unchanged; the decision to clamp to `C_T = τ` is the correct one; and the
namespace contains no unconferred terminal-state assertion anywhere. The frozen gate, the D5 forecast, the
predecessor namespaces, the coverage map and `main` are all untouched. This campaign is one sentence away from
freezeable.

---

*Third independent fresh-context pre-freeze review. Worktree `/Users/suzhe/ReBaseGuard-k5c2`, branch
`p5y-k5-tail-c2`, HEAD `55c4cf00`, reviewed 2026-09-21. Read-only throughout: no file in the namespace was
modified except this one, and no writing git command was run.*
