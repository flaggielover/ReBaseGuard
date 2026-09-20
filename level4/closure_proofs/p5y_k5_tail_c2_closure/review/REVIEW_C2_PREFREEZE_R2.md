# Second independent pre-freeze review — Campaign C2 (`p5y_k5_tail_c2_closure`), branch `p5y-k5-tail-c2` @ `ef58310c`

**VERDICT: NOT_READY** — all six FAILs from the first review at `5a94568a` are genuinely repaired, not papered over,
and every repair I could check reproduces exactly. What blocks the freeze is a *new* defect introduced by one of the
repairs: `phase_d/D1_BLOCKER_DIAGNOSIS.md` §2 now argues that the ×0.9 sensitivity convention is disqualified because
it "drives C_T below τ, violating the Lemma Dv′ premise C ≥ τ". The convention C2 actually publishes does exactly the
same thing, on exactly the same three cells (307, 308, 309), and its published `C_T` sensitivity figures on those
cells are computed outside the Lemma Dv′ hypotheses — surviving only because `c2_d1_blocker.atom_dv_prime` is a local
re-implementation of `deflated_consume.atom_constants_r2` that omits its premise guard. The numeric impact is
negligible (Note 1 quantifies it: 0.01–0.46 percentage points on a third-ranked lever), but it is the same defect
class the first review blocked on twice, and it is newly written rather than inherited. The fix is one paragraph, one
table annotation, and one sentence of code disclosure. Nothing else in the campaign requires change.

**Reviewer context.** Fresh context; I did not write this work and did not participate in the first review. I read
`review/REVIEW_C2_PREFREEZE.md` first, as instructed, and then reviewed the repairs. I had the `numpy` / `scipy` /
`python-flint` stack the first reviewer lacked. What I re-derived **independently**, with my own driver scripts that
import none of `c2_critical_ratio.py`, `c2_d1_blocker.py`, `c2_recertify_306.py` or `c2_refined_registry.py`:

- the critical s_G/s_H ratios under **six** named supplies by my own exact-rational bisection (Lemma G, C1, C2,
  min{G,C1}, the D4 gate rule, and the mixed operator tuple) — reproducing Campaign B's published Lemma-G anchor and
  C2's published C2 column digit for digit, and confirming the new C1 column;
- the D′ operator-mixed requirements, gaps and gap falls on all five cells;
- the containment of the TC-T enclosure in the adopted record's `R2_interval` on all five cells (the M32 equivalence
  proof), and `M = mag(enclosure) < M_R2` on all five;
- the D1 sensitivity table under **both** conventions on cells 305 / 307 / 309, including the `C_T` row and the
  `C ≥ τ` premise at every cell and both registries;
- re-certification of three registry artifacts (`taboo_block_306_02`, `taboo_cell_306_04`, `taboo_block_305_00`) at
  256 bits (bit-identity) and at 384 bits (safe-side), with my own comparison rules rather than the campaign's;
- the `{G, C1}` sub-family provenance that makes M34/M35 load-bearing, and C2's strict dominance on 15/15 fields;
- the producer refusal behaviour, by breaking each published anchor in a scratch copy and confirming refusal;
- a full re-run of the adversarial suite, byte-compared against the committed artifact.

I did **not** re-run the full 105-artifact registry verification (≈2.7 h), did not contact the Vultr or AWS hosts,
did not run any writing git command, and modified no file in the worktree except this one. `git status` was clean
before and after. Section "What I did not check" lists the rest.

---

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| **A. Integrity and scope** |
| 1 | `git diff --name-status 5289b6ce..HEAD` is entirely additive and entirely inside the C2 namespace | PASS | 132 entries, **all `A`**; the complement `grep -v 'p5y_k5_tail_c2_closure/'` is empty |
| 2 | the frozen gate is byte-unchanged and still one commit | PASS | `shasum -a 256` = `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`; `git log --all -- config/FEASIBILITY_GATES_C2.json` returns exactly `87309610` |
| 3 | `main` untouched | PASS | `main` = `c123b9bb`, an ancestor of HEAD; `git branch --contains 87309610` returns only `p5y-k5-tail-c2` |
| 4 | coverage map r4 untouched, no r5 anywhere | PASS | `K5_COVERAGE_MAP_R4.json` sha `a3bddd83…`, single commit `f2ac1eb3`; the only other coverage maps are r3 and the pre-r3 file, both in predecessor namespaces |
| 5 | predecessor namespaces byte-unchanged | PASS | implied by row 1; no `M`/`D`/`R` entry exists in the whole range |
| 6 | `c2_d5_forecast.py` unmodified since `5a94568a` | PASS | `git diff 5a94568a..HEAD -- code/c2_d5_forecast.py` is empty. No published forecast number can have moved |
| 7 | the phase-D evidence artifacts are unmodified since `5a94568a` | PASS | `C2_D5_FORECAST.json`, `C2_ROBUSTNESS_AND_R_ATTRIBUTION.json`, `REGISTRY_C2.json`, `C2_D1_BLOCKER.json` all last touched at `5a94568a` or earlier. The **only** modified evidence file in the range is `C2_MUTATIONS.json` |
| 8 | …and that modification changed no baseline | PASS | `baseline` block byte-identical; ten mutants added, none removed; one existing row (`M10`) gained a `caught_by` entry (`"tiling"`), still detected |
| 9 | `REGISTRY_C2.code_sha256.c2_refined_registry` still matches the builder in the tree | **NOTE** | it does not. The pin is `4ac24d9e…` (the builder at `5a94568a`); the file now hashes to `0d1d8021…`. Benign — `build()` is byte-identical, only `verify()`/`main()` changed — but undisclosed. Note 6 |
| 10 | nothing in the namespace pre-empts freeze, qualification, sealing or adjudication | **FAIL (text)** | one new declarative: `phase_d/CELL_306_ADOPTION.md` line 9, of cell 305, "**It is adopted.**" Adoption is a terminal state of the adjudication chain; the gate itself says "always adopted *when the adjudication chain completes*". Everything else in the namespace is correctly conditional. Note 7 |
| 11 | the README's new Result section is accurate | PASS with note | Γ −0.088029 / −0.030469 / +0.033133 / +0.102700 / +0.162249, margins 1.353 / 1.112 / 0.891 / 0.705 / 0.579, gap falls 46.29 / 24.59 / 18.39 %, 2.69 CPU-h, 0 new real addresses, guard DENY — every one reproduces. Note: it states `closed = {305, 306}` without saying that *adopting* 306 is now referred out and may end as 305 alone |
| **B. FAIL 61 / 62 — the critical-ratio baseline** |
| 12 | the true C1 column is 34.55795 / 20.93621 / 12.18694 | PASS | my own bisection: **34.55795 / 20.93621 / 12.18694** (and 68.81660 / 51.59944 at 305/306). Independent of both the campaign's producer and the first reviewer's implementation |
| 13 | the C2 column equals C2's published anchor | PASS | 72.71753 / 54.86736 / **37.32219 / 23.26035 / 14.15799**, equal to `C2_ROBUSTNESS_AND_R_ATTRIBUTION.critical_sG_over_sH` to all printed digits |
| 14 | the Lemma-G column equals Campaign B's published anchor | PASS | 64.72474 / 47.98610 / 32.03283 / 19.19506 / 10.54598 = `TAIL_FORECAST_R2.critical_sup_G_over_sup_H_ratio` exactly — confirming the first review's diagnosis that the old "C1" column was Campaign B's |
| 15 | the restated improvement +8.0 / +11.1 / +16.2 % is right | PASS | mine: **+7.9989 / +11.1010 / +16.1734 %** |
| 16 | …and the withdrawn "16–34 %" really was the improvement over Campaign B | PASS | mine, C2 over Lemma G: **+16.51 / +21.18 / +34.25 %** — the quoted range exactly |
| 17 | the new producer refuses unless both anchors reproduce bit-exactly | PASS | I perturbed `TAIL_FORECAST_R2["307"]` by 1e-9 in a scratch copy → `SystemExit: Lemma-G column does not reproduce Campaign B`, **no output file written**. Separately perturbed `C2_ROBUSTNESS["308"]["Gamma"]` by 1e-12 → `SystemExit: C2 column does not reproduce published Gamma`, no output. Committed evidence never touched |
| 18 | the producer reproduces the committed artifact | PASS | run clean, `cmp` against `evidence/phase_d5/C2_CRITICAL_RATIOS.json` → **byte-identical** |
| 19 | the adopted lower-front range "34.79 – 80.50" over 34 cells | PASS | my own scan of `p5y_k5_lower_front_order3/evidence/tc_r1/cells/`: 34 cells, min 34.78567, max 80.50035 |
| 20 | "what C2 bought at 307 is margin within the range, not entry into it" (+7.2 %) | PASS | min{G, C1} = **34.82089** > 34.78567, already inside; 37.32219 / 34.82089 − 1 = **7.183 %** |
| 21 | `R_STAGE_DESIGN.md` §2 and `D_STAGE_DECISION.md` §5 are now accurate and do not over-claim in a new way | PASS | both name the column by supply, both state the error rather than patching it silently, both now carry the narrowed 307 claim and the D′ precondition. I found no new over-claim in either |
| **C. FAIL 30 — the D1 blocker ranking** |
| 22 | `D1_BLOCKER_DIAGNOSIS.md` §1 now matches `C2_D1_BLOCKER.json` | PASS | prose f_F 0.602 / 0.545 / 0.475 / 0.378 / 0.285 %, f_D 0.320 / 0.340 / 0.342 / 0.322 / 0.282 %, f_H 0.170 / 0.179 / 0.177 / 0.161 / 0.135 % against JSON `radius_grouped` 0.0060248 / 0.0031989 / 0.0016992 (cell 305) and the four others — exact. `DOMINANT_BLOCKER_3 = order-0 f_F 0.28–0.60 %` matches `{"term": "order0_residual_fF", "share": 0.006025}` |
| **D. FAIL 6 — the gate's inverted justification** |
| 23 | the gate was **not** amended | PASS | rows 2 and 3 above; the erratum carries the correction |
| 24 | the erratum's statement of the correct direction is itself correct | PASS | `gap_fall/raw_fall = (1+g₀)/g₀ > 1` always, largest for small g₀. Distortion factors: 1.2621/0.2621 = **4.816** at 307 and 2.1016/1.1016 = **1.908** at 309, against the erratum's "4.82" and "1.91" |
| 25 | carrying an erratum rather than amending is the right call | PASS (opinion) | yes. A pre-registration whose bytes can be edited after a review is not a pre-registration. The clause that carries the argument ("a cell closes when its requirement reaches 1…") is sound on its own, and `OPEN_NOTES` carries it forward as **N6** with "a successor gate must not copy the sentence" |
| **E. FAIL 51 — re-certification of cell 306** |
| 26 | determinism at 256 bits is bit-identical on an independent host | PASS | **my own run**, macOS 26.5.2 / arm64 / Python 3.14.5 / numpy 2.5.3 / python-flint 0.9.0: `taboo_block_306_02` 6/6 fields exactly equal; `taboo_cell_306_04` 7/7 exactly equal; `taboo_block_305_00` 6/6 exactly equal. `certified: true` in every case |
| 27 | the 384-bit pass leaves every consumed bound valid | PASS | **my own run**: `taboo_block_306_02` C_T rel −9.97e-50 (≤ published ✓), τ exactly equal; `taboo_cell_306_04` D_lo rel **+1.27e-45** (≥ published ✓), D1 −3.87e-44, D2 −2.97e-44 (≤ published ✓). `certified: true` at 384 on all three |
| 28 | the artifact's own field accounting reconciles | PASS | determinism 117 strict comparisons = 9×6 block + 9×7 cell; safe-side 45 asserted = 9×(C_T, τ) + 9×(D_lo, D1, D2), 27 measured = 9×3 diagnostics, 45 recorded-only = 18 `certified` + 9×3 cell diagnostics |
| 29 | the "second host" claim is evidenced | **NOTE** | the *re-certification* host is recorded in two artifacts. The **build** host (`CELL_306_ADOPTION.md`'s left column: Linux x86_64 vultr-02, Python 3.12.3, numpy 2.5.2) is recorded **nowhere** in the repository — `REGISTRY_C2.json` still has no host field. Note 4 |
| 30 | …is there any in-repo corroboration that the registry was built elsewhere? | INFO | yes, weak but real: the artifacts record `cpu_seconds` 90.2 (block 306_02) and 88.3 (block 305_00); the same certifications took **56.2 s** and **66.1 s** on this host. Consistent with a different, slower machine |
| **F. The question the campaign asked to be challenged (moved goalpost)** |
| 31 | claim (b): the consumed-constant test is **unchanged** from the first version | PASS | `git diff 12585997 8aee1fc5 -- code/c2_recertify_306.py`: the comparisons are `g_ <= p_` for C_T/τ/D1/D2 and `g_ >= p_` for D_lo in **both** versions. Only the membership tuples were split and the three diagnostics moved to a `MEASURED` branch |
| 32 | claim (c): the determinism pass is unchanged and still demands bit-identity on **every** field | PASS | the `elif strict: good = p_ == g_` branch is byte-identical across the two versions, and precedes every other numeric branch |
| 33 | the first (failing) version is actually in git, so the claim is checkable | PASS | committed at `12585997`; modified at `8aee1fc5`. The campaign did not merely assert the history, it left it |
| 34 | is the defence sound? | PASS — **and understated** | `certify_block` sets `ok = bool(margin > 0) and bool(wmin >= 0)`, and `compare` asserts `certified is True` in **both** passes. So the only load-bearing content of `margin_lower_bound` and `w_min_lower_bound` — their sign — is still asserted, at 384 bits, with the 384-bit allowance. Note 3 |
| 35 | …and the magnitudes make the relaxation immaterial | PASS | I reproduce the worst violating deviation exactly: `allowance_upper` on `taboo_block_306_02`, rel **+5.1903e-30** = **+3.85e-34 absolute**, against that block's `margin_lower_bound` of **0.15596**. A shortfall of 4e-34 in a truncation allowance cannot flip a margin of 0.156. Nine of 27 diagnostic fields moved in the violating direction (4 `allowance_upper`, 5 `margin_lower_bound`); `w_min_lower_bound` never did |
| 36 | is the `DIAGNOSTIC_NOTE`'s own wording accurate? | **NOTE** | "a quantity which is not a bound anyone relies on" is wrong for `allowance_upper`: it *is* relied on, inside `certify_block`, as the truncation allowance added to the certification inequality. The correct statement is that its effect is subsumed by `certified`, which is asserted at both precisions. Note 3 |
| **G. FAIL 53 — the margin floor** |
| 37 | is referring the floor to the adjudicator legitimate, or an evasion? | PASS (opinion) | **Legitimate, and it is precisely what the first reviewer prescribed** (Note 12 item 1: "a margin floor set by the adjudicator, not by C2 — since the number is already public, C2 cannot freeze one honestly"). C2 also states the reason correctly: a floor picked with the answer in hand "would be worse than having none, because it would look like a pre-registration" |
| 38 | is pre-committing both branches meaningful? | PASS (opinion) | Yes. What C2 pre-commits is a *response function*, not a threshold, and it removes C2's own discretion: floor met → {305, 306}; floor failed **or declined** → 305 only. The default on "declines" is the conservative branch, which is the test of whether a two-sided pre-commitment is real |
| 39 | does it comply with the frozen `D_PARTIAL` rule? | NOTE | partially. The rule's first clause is "**ADOPT THE CLOSED SUBSET** ANYWAY" — definite article, i.e. {305, 306}; its last clause is "a **non-empty** closed subset is always adopted". C2 leans on the second. Under-adoption is the safe direction and no cell is closed unsoundly, but the document asserts compliance without acknowledging the first clause. Note 5 |
| 40 | is the adverse evidence stated? | PASS | yes, and against interest: the table prints 306's 1.112× margin, its failure under ×1.25 (`Γ_deg = +0.029163`), and 305's survival (`−0.033733`), all of which I reproduce |
| **H. Note 11 / the D′ finding** |
| 41 | gap falls 57.27 / 30.57 / 23.03 % under the componentwise-best operator supply | PASS | my own computation: requirement **1.1119662371 / 1.4606547994 / 1.8478734998**, gaps 0.11196624 / 0.46065480 / 0.84787350, falls **57.2741 % / 30.5669 % / 23.0323 %** — all three ≥ 20 %, i.e. `D_USEFUL` under the frozen classes |
| 42 | the soundness argument: C1's blocks are exactly the frozen cover's cells | PASS | verified exactly, as rationals, on all five cells: C1's `(e_lo, e_hi)` = `(e₀−ρ, e₀+ρ)` from `cells.json`. C2's sub-blocks tile the same interval (row 49). Both supplies are therefore whole-cell bounds and the componentwise best satisfies all six Lemma Dv′ hypotheses simultaneously |
| 43 | …and the mixed tuple is admissible under the pinned consumer | PASS | `deflated_consume.atom_constants_r2` accepts it on all five cells (τ ≥ 1, C ≥ τ, D_lo > 0, Ā ≥ 1, and r2 ≤ r1). The document's parenthetical claim is true |
| 44 | is C2 right to refuse to use it? | PASS (opinion) | **Yes, unambiguously.** The gate pre-registers the minimum over A0/A1/A2 *across supplies*; a minimum over the six operator constants *before* Lemma Dv′ is a different rule. Adopting it after seeing 309 land at 18.39 % would convert a missed threshold into a met one by changing the rule. Refusing is not over-scrupulous; it is the only defensible conduct |
| 45 | is it right that this **blocks** the R stage? | PASS (opinion) | **Yes.** The gate's own reading of a sub-20 % result is "the deterministic direction is exhausted"; that premise is what would justify spending the programme's first real order-3 tail address. A sound, pre-registerable, zero-CPU deterministic step clears the same bar on all three open cells, so the premise is false as stated. `R_STAGE_DESIGN.md` opening with a blocking precondition is the correct response, and `D_PRIME_OPPORTUNITY.md` §5 sequences the successor correctly (freeze the D′ rule *first*) |
| 46 | the D′ critical ratios 38.07 / 23.90 / 14.72 | PASS | mine: **38.06518 / 23.89921 / 14.72182** |
| 47 | …and the document does not over-sell it | PASS | §5 states plainly that D′ is *not* predicted to close 307/308/309 (it still needs 1.11× / 1.46× / 1.85×), only to clear the material-tightening bar. That is exactly right |
| **I. The broken verifier** |
| 48 | the account of the defect is true | PASS | `git diff` confirms `str(got.get(fld)) != str(r[fld])` → `F(str(rec[fld])) != F(str(r[fld]))` with `rec = got["recomputed"]`. `verify_block`/`verify_cell` return `{"identical", "certified", "recomputed"}`, so every prior comparison was `"None" != "<value>"` and always failed |
| 49 | the fix is correct and structural | PASS | `rec[fld]` raises `KeyError` on a missing field instead of silently comparing against `None`; `F(str(...))` is a value comparison, not a string comparison. The composition re-derivation (max on C_T/τ/D1/D2, min on D_lo) was already correct and is untouched |
| 50 | "not on the production path, no published number affected" — did `build()` ever call `verify()`? | PASS | **No.** `main()` dispatches on `mode`; the `build` branch returns before `verify` is reached. I also compared every top-level function across `5a94568a..ef58310c` by AST: `build`, `cover`, `sub_blocks`, `_sub`, `_arl`, `_import`, `sha` all **byte-identical**; only `verify` and `main` changed |
| 51 | could the defect have **masked** a real registry problem? | PASS | No. A verifier that can never pass cannot produce a false pass. It could only have *failed to detect* — which is what happened, for the whole campaign, until row 52 |
| 52 | `C2_REGISTRY_VERIFY.json` is coherent | PASS | `pass: true`, `problems: []`, `cells_checked: 5`, `artifacts_rechecked: 105` = 2×50 sub-rows + 5 ARL cells; `registry_sha256` `1b2b8349…` equals my `shasum` of the committed `REGISTRY_C2.json`; host and toolchain recorded |
| **J. The adversarial suite, 33 → 43** |
| 53 | re-runs byte-identically | PASS | my re-run: `{"applied": 43, "real_mutants": 35, "static_assertions": 8, "detected": 40, "equivalent": [M19, M20, M32], "undetected": [], "pass": true}`; `cmp` against `C2_MUTATIONS.json` → **byte-identical** |
| 54 | M26/M27 mutate the crosscheck rather than the frozen path — legitimate or a dodge? | PASS with note | **Legitimate.** Both anchors are unique and both live inside `tail_enclosure_crosscheck` (lines 272 and 276 of `tct_rule.py`; `tail_enclosure` is lines 180–212), so the two paths genuinely hold separate copies of the assembly. The detector is the symmetric equality `(lo, hi) == crosscheck(...)`, so exercising either side exercises the channel. Caveat in Note 8 |
| 55 | M28–M30 (tiling geometry) — real tests or self-referential? | PASS with note | Real, and they matter: each is caught **only** by `tiling`, never by a value or outcome change — confirming the first review's Note 14(ii) that a broken cover is otherwise silent (the extrema all sit on sub-block 0, so dropping a row changes no composed constant). The invariant is also evaluated on the **unmutated real registry** and `run()` refuses to start if it fails. Note 8 records where it ought to live |
| 56 | M32: is the containment real? | PASS | **verified independently on all five cells.** `R2_interval` ⊋ TC-T enclosure strictly: e.g. cell 305 [−5.498291, 4.964936] ⊃ [−3.615110, 3.081755]; cell 309 [−5.269941, 5.096960] ⊃ [−3.400934, 3.227953]. And `M = mag(enclosure) < M_R2` on all five, so the enclosure — not the record — sets Γ, exactly as the proof says |
| 57 | …and is the run-time containment check real? | PASS | it recomputes `T.tail_enclosure` per cell and compares against the record's interval; `containment_verified` is emitted per cell in the artifact; the code reverts the row to an undetected miss if any cell fails. Not an assertion, a computation |
| 58 | M31 / M33 (M_after min/max, emptiness branch) | PASS | both detected by a Γ change on every cell |
| 59 | M34 / M35 — does the `{G, C1}` minimum genuinely mix? | PASS | yes: A0 comes from C1 on all five cells; A1 from **G** at 307/308/309 (35.57778 < 36.16689 at 307) and from C1 at 305/306; A2 from **G** on all five. `D_STAGE_DECISION` §2's statement ("at cell 307, A0 comes from C1 while A1 and A2 come from Lemma G") is exactly right. Both mutants detected on value **and** provenance |
| 60 | …and the M19/M20 "equivalent" verdict is still correctly scoped | PASS | C2 is the strict minimum on **15/15** fields, verified. The scoping language is honest |
| 61 | mechanisms still without a mutant | INFO | `c2_d1_blocker.atom_dv_prime` (Note 2), the Ā inertness path, and the ARL-cell composition. Note 9 |
| **K. Did the campaign correct the first reviewer correctly?** |
| 62 | "the review compared τ under one convention against D_lo under the other" | PASS — **the campaign is right** | my own computation at cell 305, C1 registry: ÷1.1 → D_lo **+8.6029 %**, τ **+8.0181 %**; ×0.9 → D_lo **+9.4566 %**, τ **+8.8200 %**. The review's "τ +8.82 vs D_lo +8.60" takes one figure from each column. Within either convention, **D_lo > τ on every cell** (307: 8.673/8.102 and 9.534/8.912; 309: 8.719/8.168 and 9.584/8.985) |
| 63 | the campaign's quoted ×0.9 figures (D_lo +9.457 %, τ +8.820 %) | PASS | reproduced exactly |
| 64 | "× 0.9 drives C_T below τ at cell 307, violating the Lemma Dv′ premise C ≥ τ" | PASS (as a bare fact) | true: C1 C_T(307) × 0.9 = 4.798374 < τ = 4.851873. Also true at 308 and 309, and under the C2 registry |
| 65 | …but is it a **reason to prefer** the published convention? | **FAIL** | No. The published ÷1.1 convention violates `C ≥ τ` on **exactly the same three cells**: C_T/1.1 = 4.846842 < 4.851873 (307), 4.553601 < 4.633777 (308), 4.277739 < 4.418493 (309). `deflated_consume.atom_constants_r2` **refuses all three**. Neither convention is "uniformly applicable". Note 1 |
| 66 | …and are the published `C_T` sensitivity figures on those cells inside the lemma's hypotheses? | **FAIL** | No, and this is nowhere disclosed. `c2_d1_blocker.atom_dv_prime` re-implements `atom_constants_r2` without its premise guard (and without its `r2 ≤ r1` check). I reproduce the published `C_T` gains exactly through that unguarded path — 1.3599 / 1.3672 / **1.3823 / 1.3945 / 1.3887 %** — and my guarded path refuses on the last three. Note 2 |
| 67 | does anything in §2's conclusion move? | PASS | **No.** The largest *admissible* C_T cut is to C_T = τ: 8.997 % at 307, 7.490 % at 308, 6.100 % at 309, giving gains of 1.368 / 1.150 / 0.934 % against the published 1.382 / 1.395 / 1.389 %. C_T remains a distant third behind D_lo (~8.7 %) and τ (~8.1 %), and "D2 is irrelevant" (0.07 %) is untouched |
| **L. The erratum's other claims** |
| 68 | "No number C2 published has changed" | PASS | rows 6–8: the only modified evidence file is `C2_MUTATIONS.json`, whose baseline is byte-identical |
| 69 | `MEASURE_CHANGE_SELF_AUDIT.md`'s four-axis table and arithmetic | PASS | raw falls 9.61 / 9.81 / 9.64 %; gap-equivalents of C1's 10 %: 0.1·1.2620573/0.2620573 = **48.16 %**, 25.07 %, 19.08 %; under C1's gate verbatim (2.252903 → 1.8990149) the fall is **15.7084 %** ⇒ USEFUL. All reproduce. The audit states both halves ("on the measure alone — yes; on the gate as a whole — the opposite") |
| 70 | `OPEN_NOTES_DISPOSITION_C2.md` carries N6–N9 | PASS | N6 gate sentence, N7 D′ blocking the R stage, N8 the margin floor, N9 the Arb/FLINT residual trust surface. The mutant count is updated to 35 real + 8 static |
| 71 | the erratum's account of the verifier discovery | PASS | accurate, including the self-critical framing ("a check nobody has run is not a check") |

---

## Notes

### Note 1 (FAIL) — the new argument for the sensitivity convention is not an argument

`phase_d/D1_BLOCKER_DIAGNOSIS.md` §2, added at `12585997` as part of the repair of the first review's row 32, now
reads:

> There is also a reason to prefer the tabulated convention beyond symmetry: × 0.9 is not uniformly applicable. At
> cell 307 it drives C_T below τ, violating the Lemma Dv′ premise C ≥ τ, and `deflated_consume.atom_constants`
> refuses outright. A sensitivity convention that puts the constants outside the lemma's hypotheses is the wrong one
> to publish.

Every clause of that is true except the one that matters: the implied contrast. Under the C1 registry, which is what
phase D1 uses:

| cell | τ | C_T | **C_T × 0.9** | **C_T ÷ 1.1 (the published convention)** | C ≥ τ under ×0.9 | C ≥ τ under ÷1.1 |
|---|---|---|---|---|---|---|
| 305 | 5.291155 | 6.028953 | 5.426058 | 5.480867 | ✔ | ✔ |
| 306 | 5.070746 | 5.670984 | 5.103886 | 5.155440 | ✔ | ✔ |
| 307 | 4.851873 | 5.331527 | 4.798374 | **4.846842** | ✘ | **✘** |
| 308 | 4.633777 | 5.008961 | 4.508065 | **4.553601** | ✘ | **✘** |
| 309 | 4.418493 | 4.705512 | 4.234961 | **4.277739** | ✘ | **✘** |

The two conventions fail the premise on the *same three cells*. `deflated_consume.atom_constants_r2` refuses ÷1.1 at
307, 308 and 309 exactly as it refuses ×0.9 — I ran both. So "× 0.9 is not uniformly applicable" is a property the
published convention shares, and cannot distinguish them. The paragraph's other reason (symmetry of A0 = τ/D_lo in
its two factors) is sound and sufficient on its own, exactly as the erratum argues for the gate's own inverted
sentence in FAIL 6. The fix is to delete the third paragraph or restate it as what it actually is: *neither*
convention can cut C_T by 10 % at 307–309 without leaving the lemma's hypotheses.

This is the same defect class the first review blocked on — a claim whose arithmetic does not support its label —
and unlike rows 61/62 and 30 it was **written during the repair**, in a paragraph explicitly prefaced "Recomputed
here rather than accepted, because it is the finding the whole section rests on."

### Note 2 (FAIL) — three published sensitivity figures are computed outside the Lemma Dv′ hypotheses

The direct consequence of Note 1. `code/c2_d1_blocker.py` line 58:

```python
def atom_dv_prime(Abar, tau, C, Dlo, D1, D2) -> dict:
    eff = Abar if Abar < tau / Dlo else tau / Dlo
    ...
```

This is a local re-implementation of `deflated_consume.atom_constants_r2`. Its *arithmetic* is identical, but it
omits both guards the pinned consumer carries: the premise check
`if not Dlo > 0 or not tau >= 1 or not C >= tau: raise DeflationRefusal`, and the `r2 ≤ r1` consistency check.
Because the `C_T` sensitivity row perturbs `C_T` to `C_T·10/11` and feeds it straight to `atom_dv_prime`, the
published figures for cells **307, 308 and 309** — 1.3823 %, 1.3945 %, 1.3887 % in
`C2_D1_BLOCKER.json.cells[*].sensitivity_10pct_improvement.C_T` and in the §2 table — are computed from a constant
tuple that Lemma Dv′ does not admit. I reproduced all five published values exactly through the unguarded path,
which is how I identified the cause.

Nothing else in the D1 artifact is affected: the baseline constants satisfy `C ≥ τ` on every cell, so the unperturbed
A-tuples, the radius decomposition, the D_lo/τ/D1/D2 sensitivity rows, the required reductions and the attribution
test are all identical under either implementation (and the first reviewer reproduced them to <1e-12 with a third).

The magnitude of the error is small, and I say so plainly. Constraining the perturbation to the admissible range —
C_T down to τ, the tightest value Lemma Dv′ permits — gives:

| cell | largest admissible C_T cut | gain at that cut | published (assumed 9.091 % cut) | overstatement |
|---|---|---|---|---|
| 307 | 8.997 % | 1.3681 % | 1.3823 % | 0.014 pp |
| 308 | 7.490 % | 1.1502 % | 1.3945 % | 0.244 pp |
| 309 | 6.100 % | 0.9335 % | 1.3887 % | 0.455 pp |

§2's three findings are unaffected: D_lo (~8.7 %) and τ (~8.1 %) still dominate, C_T is still third at ~1 %, D2 is
still 0.07 %, and finding 3 (no operator tightening closes 309) rests on `A0 = τ/D_lo ≥ τ`, not on C_T at all. What
needs to change is disclosure, not conclusions: annotate the three cells, and record that `atom_dv_prime` is an
unguarded local copy of the pinned consumer.

### Note 3 (the moved-goalpost question) — the defence is sound, and the campaign undersells it

Asked directly: **this is not a moved goalpost.** Three reasons, in increasing order of force.

1. **The claim is checkable and the campaign left the evidence.** The failing first version is committed at
   `12585997`; `git diff 12585997 8aee1fc5` shows the consumed-constant comparisons (`g_ <= p_` for C_T/τ/D1/D2,
   `g_ >= p_` for D_lo) and the strict determinism branch are **character-for-character unchanged**. Only the three
   internal diagnostics moved from an asserted branch to a measured one. A campaign hiding a relaxation does not
   commit the pre-relaxation code first.
2. **The relaxed quantities are absolutely negligible.** I reproduce the worst violating deviation exactly:
   `allowance_upper` on `taboo_block_306_02`, +5.1903e-30 relative = **+3.85e-34 absolute**, against that block's
   `margin_lower_bound` of **0.15596**. Even reading the deviation as a genuine shortfall in the truncation
   allowance, the certification inequality has 33 orders of magnitude of slack.
3. **The strongest argument is one the campaign does not make.** `certify_block` computes
   `ok = bool(margin > 0) and bool(wmin >= 0)` — so `certified` *is* the sign of `margin_lower_bound` and
   `w_min_lower_bound` — and `compare` asserts `certified is True` in **both** passes, unconditionally, ahead of
   every numeric branch. At 384 bits the whole certification is re-derived with the 384-bit allowance and still
   certifies. The load-bearing content of all three "relaxed" diagnostics was therefore never relaxed at all; only
   their low-order digits were released. I verified `certified: true` at 384 on all three artifacts I re-ran.

One wording criticism: the `DIAGNOSTIC_NOTE` calls these "a quantity which is not a bound anyone relies on". That is
right for `margin_lower_bound` and `w_min_lower_bound` (they are outputs) but wrong for `allowance_upper`, which is
an *input* to the certification inequality inside `certify_block` — a genuinely under-estimated allowance would be a
soundness question. The correct sentence is that its effect is fully subsumed by `certified`, which is asserted at
both precisions. Reason (3) should replace the note's current phrasing.

### Note 4 (NOTE) — the re-certification host is evidenced; the build host is not

`C2_RECERTIFY_306.json` and `C2_REGISTRY_VERIFY.json` both record `platform`, `machine`, `python`, `numpy` and
`python_flint` for the machine that *re-certified*. Nothing in the repository records the machine that *built* the
registry: `REGISTRY_C2.json` still has no host field, which was precisely the first review's row 51 complaint.
`CELL_306_ADOPTION.md`'s comparison table therefore has one sourced column and one unsourced one, and the sentence
"a genuinely second host" rests on the unsourced half.

Weak in-repo corroboration does exist, and it is worth recording because it is the only evidence there is: the
artifacts carry `cpu_seconds` 90.2 (`taboo_block_306_02`) and 88.3 (`taboo_block_305_00`); the identical
certifications on this host took **56.2 s** and **66.1 s**. Different machine, almost certainly. But a freeze should
not leave the claim resting on a timing inference — a successor should record the build host in the registry, and in
the meantime the table's left column should be marked as reported rather than recorded.

### Note 5 (NOTE) — "THE closed subset" versus "a non-empty closed subset"

`CELL_306_ADOPTION.md` asserts that the 305-only branch satisfies the frozen `D_PARTIAL` rule because "a non-empty
closed subset is always adopted". The rule's first clause, however, is "**ADOPT THE CLOSED SUBSET** ANYWAY" —
definite article, and under the gate's own machinery the closed subset is `{305, 306}`. The gate's stated *rationale*
(an adopted cell is permanent progress; declining preserves nothing; a soundly closed 305 has twice been left
unadopted) also argues for adopting 306.

I do not make this a FAIL. The branch is selected by an authority outside the campaign, under-adoption is the
conservative direction, no cell is closed unsoundly, and the gate genuinely contains both readings. But the document
asserts compliance without acknowledging the clause that cuts the other way, which is the same habit — quoting the
half of a sentence that supports you — that produced FAIL 6 in the first place. One sentence acknowledging the
tension would settle it.

### Note 6 (NOTE) — the registry's own producer pin is now stale

`REGISTRY_C2.json.code_sha256.c2_refined_registry` = `4ac24d9e182656a45770fc02f58e96d9e0492456c7b1991c752426f9bcecdc91`.
That was the builder's hash at `e71378a0`, `5a94568a` and `12585997`. Since `e9c230d3`/`2b045564` the file hashes to
`0d1d8021a3780e13c567f583c1e490025ea2ca43dbfa7082f7dd5905e965b623`. Nothing asserts the pin, so nothing fails — but a
successor or reviewer asking "was this registry produced by the committed builder?" gets a mismatch with no
explanation anywhere in the namespace, in a file about to be frozen.

It is benign, and I established that rather than assuming it: comparing every top-level function across
`5a94568a..ef58310c` by AST, `build`, `cover`, `sub_blocks`, `_sub`, `_arl`, `_import` and `sha` are byte-identical;
only `verify` and `main` changed. One line in `ERRATUM_C2.md` recording the old and new hashes closes it.

### Note 7 (FAIL, text) — one new unconditional adoption claim

`phase_d/CELL_306_ADOPTION.md` line 9, of cell 305: "Neither reviewer has raised an objection to it. **It is
adopted.**" Everywhere else the namespace is scrupulous — "adopt {305, 306}", "adopt 305 only", "when the
adjudication chain completes", `R_STAGE_DESIGN.md`'s "DESIGN ONLY", guard DENY. The first review's row 55 checked
specifically for "no ADOPTED claim beyond the gate's forward-looking language" and passed; this sentence is a new
one, introduced at `8aee1fc5`.

Read in context it plainly means "C2's decision is to adopt it in either branch", which is correct and is what the
rest of the section says. But a pre-freeze artifact should not contain a bare declarative that a terminal governance
state has been reached, and downstream checks in this programme scan for exactly that phrasing. "C2 adopts it under
either branch below" fixes it.

### Note 8 (opinion) — the new mutants are real, with one structural comment each

**M26 / M27 are legitimate, not a dodge.** The frozen assembly cannot be mutated because `tct_rule` is pinned by sha;
mutating the crosscheck's copy exercises the same detector, because the detector is the symmetric equality
`(lo, hi) == tail_enclosure_crosscheck(...)` — a disagreement is caught whichever side moves. I verified the two
copies are genuinely distinct code: both anchors are unique and both sit inside `tail_enclosure_crosscheck`
(lines 272 and 276) while `tail_enclosure` occupies 180–212. The honest limitation, which the comment in the module
states, is that this proves the *channel* works, not that the frozen path is right; a shared upstream helper would
defeat both. There is no such helper here.

**M28 / M29 / M30 are the most valuable addition in the repair**, and for a reason worth stating: each is caught
**only** by the new `tiling` flag, never by a value or outcome change. Dropping a sub-block, or opening a 1/1000 gap,
leaves every composed constant unchanged — because all five extrema fall on sub-block 0 — so Γ does not move and the
cover could have been broken without any published number noticing. That is precisely the silent unsoundness the
first review's Note 14(ii) predicted. The invariant is also evaluated on the *real, unmutated* registry and `run()`
refuses to proceed if it fails, so the committed registry's geometry is now checked by executed code, not argued.

The structural comment: that invariant lives in `code/c2_mutations.py`, not in `c2_refined_registry.verify()` — which
is the artifact a successor would re-run, and which re-derives the max/min composition without ever checking that the
rows it composes cover the cell. The check is in the wrong module. Moving it is a few lines and would close the hole
for good.

### Note 9 (INFO) — what still has no mutant

The suite now covers the three mechanisms the first review named. Three remain uncovered, one of which is where I
found Note 2:

- **`c2_d1_blocker.atom_dv_prime`** — an unguarded duplicate of the pinned `deflated_consume.atom_constants_r2`. A
  mutant asserting that the two agree, or that the local copy refuses on the same inputs, would have caught Note 2
  automatically. This is the single highest-value mutant the suite is missing.
- **the Ā inertness path** — `Ā_eff = min(Ā, τ/D_lo)`; the first review established Ā never binds (20–39 % slack on
  every cell, both registries), so a mutant swapping the min for a max would be undetected on this data and would
  need the same kind of scoped equivalence proof M32 carries.
- **the ARL-cell composition** — `Abar` is taken from a per-cell artifact rather than composed over sub-blocks; no
  mutant probes that path, though `verify()` does re-check it.

### Note 10 (context) — what reproduces

Everything I checked reproduced, and where the campaign and the first reviewer disagreed I found the campaign right.
Bit-exact or digit-exact from my own drivers: all six critical-ratio columns including the two published anchors; the
D′ requirements, gaps and gap falls; the TC-T/R2 containment on all five cells; the D1 sensitivity table under both
conventions; the `{G, C1}` provenance and C2's 15/15 dominance; the measure-audit arithmetic; the erratum's
distortion factors; the 34-cell lower-front range. From the FLINT stack on a second host: bit-identical
re-certification of three registry artifacts at 256 bits and safe-side domination at 384. The mutation suite
re-runs byte-identically and the critical-ratio producer reproduces its committed artifact byte-identically and
refuses on a broken anchor. **I found no arithmetic error anywhere in C2, in either review round.**

---

## What I did not check

- **The full 105-artifact registry re-verification.** I re-certified three artifacts (two from cell 306, one from
  cell 305) at two precisions; the committed `C2_REGISTRY_VERIFY.json` covers all 105 and I checked its internal
  coherence and its registry sha against the committed file, but I did not spend the ~2.7 h to re-run it. Nor did I
  re-run the remaining 15 artifacts of cell 306.
- **The Arb/FLINT supersolutions as mathematics.** I re-ran the certifier and confirmed determinism and safe-side
  domination at higher precision on a second architecture and FLINT build. That tests reproducibility and precision
  robustness; it does not test the certifier's *logic*, which remains the residual trust surface the campaign carries
  forward as **N9**. A second, independently written certifier is still the real answer and still does not exist.
- **The frozen theorem modules.** My drivers call the pinned `tct_rule.tail_enclosure`, `tc_rule` and
  `deflated_consume.atom_constants_r2` rather than reimplementing the theorems. The first reviewer wrote an
  independent implementation from the theorem documents and it agreed bit-exactly with C2 on everything
  decision-relevant; I relied on that for theorem-level correctness and concentrated on what a second pair of hands
  and a FLINT stack could add.
- **The K1 record store, the replay gate and cells 0–304.** Not in the repository; `c2_d5_forecast.py --records`
  cannot run here. Unchanged from the first review's position.
- **The build host.** Note 4. No remote host was contacted; per the task constraints I did not touch AWS and chose
  not to touch Vultr.
- **The provenance of the adopted Campaign-A / Campaign-B inputs** (`TCT_INPUTS_*`, `ADOPTED_TAIL_INPUTS.json`,
  `cells.json`, the lower-front order-3 evidence). C2 alters none of them; their correctness is not reopened here.
- **Whether the adjudicator will in fact set a margin floor.** Out of scope by construction — that is the point of
  the referral.

---

## Verdict counts

| verdict | count |
|---|---|
| PASS | 55 |
| PASS with note / PASS (opinion) recorded separately above | (included in PASS) |
| INFO | 3 |
| NOTE | 5 |
| **FAIL** | **3** |
| **total** | **71** |

**FAIL rows:**

- **65** — `D1_BLOCKER_DIAGNOSIS.md` §2's new claim that the ×0.9 convention is disqualified by the `C ≥ τ` premise
  is not a reason to prefer the published convention: ÷1.1 violates the same premise on the same three cells
  (307, 308, 309) and `deflated_consume.atom_constants_r2` refuses all three.
- **66** — the published `C_T` sensitivity figures for cells 307, 308 and 309 are computed outside the Lemma Dv′
  hypotheses, via `c2_d1_blocker.atom_dv_prime`, an unguarded local copy of the pinned consumer; undisclosed.
- **10** — `CELL_306_ADOPTION.md` contains one new bare declarative, "It is adopted.", of a terminal governance state
  that the adjudication chain has not reached.

**NOTE rows:** 9 (stale builder pin), 29 (build host unevidenced), 36 (`DIAGNOSTIC_NOTE` wording), 39
(`D_PARTIAL` "THE closed subset"), 55/54 structural comments in Note 8.
**INFO rows:** 30, 61, and the coverage observations in Note 9.

---

## FINAL VERDICT: NOT_READY

**Everything the first review blocked on is genuinely fixed.** I want to be unambiguous about that, because the
verdict word is the same and the situation is not. The critical-ratio column is relabelled and its true C1 values —
34.55795 / 20.93621 / 12.18694 — are the ones I get from my own bisection; the improvement is correctly restated as
+8.0 / +11.1 / +16.2 %, and I confirm the withdrawn "16–34 %" was the improvement over Campaign B (+16.5 / +21.2 /
+34.3 %). The ratios now have a committed producer that reproduces two published anchors bit-exactly and genuinely
refuses when either is broken — I broke both and it refused both times, writing nothing. The D1 blocker prose now
matches its JSON to the digit. The gate is byte-unchanged, still one commit, and carrying an erratum rather than
amending it is the right call. Cell 306's eighteen artifacts re-certify **bit-identically at 256 bits on a second
architecture and FLINT build** — I reproduced that myself on two of them, plus one from cell 305 — and every consumed
bound survives 384 bits. The margin floor is referred to the adjudicator, which is exactly what the first reviewer
prescribed, with a two-sided pre-commitment whose default branch is the conservative one. The registry verifier's
defect is truthfully described, correctly and structurally fixed, and provably off the production path (`build()` is
byte-identical). The adversarial suite re-runs byte-identically at 43 mutants, M32's equivalence proof is valid — I
verified the containment on all five cells — and M28–M30 close a real silent-unsoundness hole. And on the one point
where the campaign contradicts the first reviewer, **the campaign is right**: D_lo outranks τ under both conventions
on every cell, and the review's counterexample mixed the two.

The D′ finding is handled correctly in every respect. I reproduce 57.27 / 30.57 / 23.03 %, I verified the soundness
argument exactly (C1's blocks are the frozen cover's cells, endpoint for endpoint, on all five), and I verified the
mixed tuple is admissible under the pinned consumer. Refusing to use it is not over-scrupulous — it is the only
defensible conduct, since the gate pre-registers a minimum across *supplies*, not across the six operator constants,
and taking the other rule after seeing 309 land at 18.39 % would convert a missed threshold into a met one. And yes,
it should block the R stage: the premise that would justify spending the programme's first real order-3 tail address
is that the deterministic direction is exhausted, and a zero-CPU, zero-address, pre-registerable step clears the
gate's own bar on all three open cells. `R_STAGE_DESIGN.md` opening with that precondition is correct.

**What blocks the freeze is one paragraph written during the repair.** `D1_BLOCKER_DIAGNOSIS.md` §2 argues that the
alternative sensitivity convention is disqualified because it puts the constants outside the Lemma Dv′ hypotheses.
The convention C2 publishes does the same thing on the same three cells, and three of its five published `C_T`
figures are computed there — reaching a number at all only because `c2_d1_blocker.atom_dv_prime` omits the premise
guard that the pinned `deflated_consume.atom_constants_r2` enforces. Nothing C2 concludes moves (Note 2 quantifies
the overstatement at 0.01–0.46 percentage points on a third-ranked lever), and I would not raise it at all if the
standard here were lower. But the first review blocked this freeze over a mislabelled column that changed no number
and over a misranking of three sub-1 % terms, and this is the same class of defect, introduced after that review, in
a paragraph that advertises having been "recomputed rather than accepted". A freeze makes it permanent, and a
successor reading §2 would take the published table to be premise-safe when three-fifths of one row is not.

**To reach READY_TO_FREEZE I would want, and nothing more than:**

1. `phase_d/D1_BLOCKER_DIAGNOSIS.md` §2 — delete the "× 0.9 is not uniformly applicable" paragraph, or restate it
   correctly: *neither* convention can cut C_T by 10 % at cells 307–309 without violating `C ≥ τ`. The symmetry
   argument stands on its own, as the erratum itself argues for the gate's inverted sentence.
2. The same section's `C_T` row — mark cells 307, 308 and 309 as computed outside the Lemma Dv′ hypotheses, or
   substitute the admissible figures (1.368 / 1.150 / 0.934 % at C_T = τ, cuts of 8.997 / 7.490 / 6.100 %). Either is
   fine; silence is not.
3. One sentence, in the erratum or the module, recording that `c2_d1_blocker.atom_dv_prime` duplicates
   `deflated_consume.atom_constants_r2` without its premise guard or its `r2 ≤ r1` check — and, ideally, a mutant
   asserting the two agree (Note 9).
4. `phase_d/CELL_306_ADOPTION.md` line 9 — "It is adopted." → a conditional formulation.

Three further items I record as notes rather than conditions, because none of them is a misstatement: the stale
`code_sha256.c2_refined_registry` pin should be disclosed (Note 6); the build-host column should be marked as
reported rather than recorded until `REGISTRY_C2.json` carries a host field (Note 4); and the tiling invariant
belongs in `c2_refined_registry.verify()`, not only in the mutation suite (Note 8). The `DIAGNOSTIC_NOTE`'s "not a
bound anyone relies on" should be replaced by the stronger and correct argument that `certified` is asserted at both
precisions (Note 3).

None of this requires new science, new compute, or a change to any number C2 has published.

---

*Second independent fresh-context pre-freeze review. Worktree `/Users/suzhe/ReBaseGuard-k5c2`, branch
`p5y-k5-tail-c2` @ `ef58310c`. FLINT stack used for operator re-certification on this host; no remote host was
contacted; no writing git command was run; no file in the worktree was modified except this one.*
