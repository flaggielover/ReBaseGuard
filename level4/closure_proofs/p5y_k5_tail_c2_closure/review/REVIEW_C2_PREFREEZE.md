# Independent pre-freeze review — Campaign C2 (`p5y_k5_tail_c2_closure`), branch `p5y-k5-tail-c2` @ `5a94568a`

**VERDICT: NOT_READY** — every published number reproduces bit-exactly and the gate is honestly frozen, but two
freeze artifacts carry a comparison labelled with the wrong baseline that overstates C2's own contribution by about
2×, and the adoption of cell 306 still does not meet the conditions the predecessor's reviewer set.

Reviewer context: fresh context, did not write this work. Everything decision-relevant was recomputed from the
committed evidence with an independently written exact-rational implementation (`fractions.Fraction` only, stdlib
only), built from `THEOREM_TCT.md`, `THEOREM_TC.md`, `THEOREM_AD.md` and `k5b_check.k5b_literal`, importing none of
`c2_d5_forecast.py`, `c2_d1_blocker.py`, `tct_rule.py`, `tc_rule.py`, `tc_crosscheck.py` or `deflated_consume.py`.
Those files were read only afterwards, to explain disagreements and to audit `classify()`. No remote host was
contacted; no writing git command was run; no file in the worktree was modified except this one.

---

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| **A. Gate timing, integrity and honesty** |
| 1 | the gate was added at `87309610` and modified zero times | PASS | `git log --all -- config/FEASIBILITY_GATES_C2.json` returns exactly one commit, `87309610`; `--follow` likewise |
| 2 | `87309610` is an ancestor of HEAD | PASS | `git merge-base --is-ancestor 87309610 HEAD` succeeds |
| 3 | gate sha256 is `098dd7f5…` as the forecast pins it | PASS | `shasum -a 256` = `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`, equal to `C2_D5_FORECAST.gate_sha256` and to `GATE_SHA` in `c2_d5_forecast.py` |
| 4 | no file reporting a C2 constant, magnitude, K5-B outcome or class predates the gate | PASS | `87309610` adds exactly four files (`README.md`, `c2_b0_verify.py`, the gate, `C2_B0_VERIFICATION.json`). Every registry/forecast/decision file first appears at `e71378a0`, `51f8844b`, `69656d58` or `5a94568a`. The only constants in the B0 artifact are **C1's** (`B6_c1_constants`), which are committed in C1's namespace at `4ccee386` |
| 5 | the gap measure is the right residual measure | PASS | a cell closes when its requirement reaches 1, so the distance above 1 is exactly what remains; the raw-requirement ratio is not a measure of remaining distance at all. Note 3 |
| 6 | the gate's stated justification for the measure change is accurate | **FAIL** | `why_gap_and_not_ratio` says the ratio measure "flatters a cell that is already nearly closed and penalises one that is far from closing". The direction is inverted: Δ/gap ≥ Δ/requirement always, and the gap between the two is **largest** for a nearly-closed cell. Note 3 |
| 7 | does the measure change make C2's life easier or harder? | INFO | **Mixed, and net harder.** Per cell at the new threshold it is looser on 307/308 and marginally stricter on 309; but C2 also widened the scope from C1's *worst* still-open cell to *every* still-open cell and moved the baseline from Campaign B to Campaign C1, both strictly harder. Under C1's gate verbatim C2 would be **USEFUL**; under its own it is **D_PARTIAL**. Notes 3 and 4 |
| 8 | C2's result under C1's measure and threshold, per cell | PASS (computed) | requirement falls 9.611 % (307), 9.809 % (308), 9.639 % (309) — all three below C1's 10 %. Reported as gap falls they are 46.29 / 24.59 / 18.39 %. Note 3 |
| 9 | C2's result under C1's gate as actually written | PASS (computed) | C1's test is on the **worst** still-open cell vs baseline 2.252903: fall = 15.708 % ≥ 10 % ⇒ passes; closes ≥ 2 with 306 ∈ {306..309} ⇒ **USEFUL**. (C1's own fall was 6.716 % ⇒ MARGINAL.) Note 4 |
| 10 | `c2_d5_forecast.classify()` is a faithful transcription of `D_stage_classes` | PASS | line-by-line: `n==5`→D_STRONG; `n>=2 and all(mt[k] for k in still_open)`→D_USEFUL (ordering supplies "not D_STRONG"); `n>=1`→D_PARTIAL; else D_INSUFFICIENT. Truth table in `C2_MUTATIONS.json` probes all eight corners and matches the gate |
| 11 | the docstring's admission that the gate does not cover "closes no cell but tightens some" is accurate | PASS | the gate's D_INSUFFICIENT requires *closes no cell **AND** no still-open cell tightened*; with `n = 0` and some tightened, no class matches. The admission is exactly right |
| 12 | resolving that hole to D_INSUFFICIENT is correct | PASS | every class above D_INSUFFICIENT requires `n ≥ 1`, so a run that closes nothing cannot reach any of them; resolving downward is the conservative reading and forbids freezing a deterministic successor |
| 13 | the D_PARTIAL adoption rule is defensible | PASS | adopting a soundly closed cell at zero real-compute cost is right, the rule is stated before any C2 number exists, and the programme has three times derived a sound closure of 305 and adopted none |
| 14 | …but was it a risk-bearing pre-registration? | INFO | No. The combination rule includes C1's supply, Γ is monotone non-decreasing in each A_j, and the gate's own baseline already records 305 and 306 at requirement 1.0. D_PARTIAL-or-better, and therefore adoption, was arithmetically **guaranteed** the moment the gate was frozen. The gate does not say so. Note 5 |
| **B. Independent reproduction of C3, C4, C5** |
| 15 | (P3′) pure Leibniz tower reproduces the theorem document | PASS | my σ3 at cell 309 = 5.88 / 16.89 / 36.52 / 67.20 (doc: 5.9 / 16.9 / 36.5 / 67.2); pure-tower σ4 at r = 4 = 355.35 / 352.81 / 350.28 / 347.72 / 345.10 across 305…309, exact match |
| 16 | (P3′) r2 midpoint tower → σ3 and cell tower → σ4 | PASS | refined σ3 at 309 = 0.694…3.805 (doc "0.69–3.81"); σ4 at r = 4 falls 345.10 → 235.12 (doc "to 235") |
| 17 | the assembly (1/m weights, c(m) = 1/t − 1/m, the ten W_(r,j)) is correct | PASS | rebuilding the record `R2_interval` from `H_at_a`, `W2` and `eps_cell_refined` is **contained** in the sealed record for all 5 cells × 4 m, worst relative endpoint gap 3.63·10⁻⁸ — identical to the value the derived identity gate reports |
| 18 | Lemma G supply (A0 = C, A1 = k₁C², A2 = k₂C² + 2k₁²C³) | PASS | reproduces `supplies[*]["G"]` on all five cells |
| 19 | Lemma Dv′ supply from the C1 registry | PASS | reproduces `supplies[*]["C1"]` exactly with the universal κ₁ = 0.7978846, κ₂ = 0.9678830 |
| 20 | Lemma Dv′ supply from the C2 registry | PASS | reproduces `supplies[*]["C2"]` exactly |
| 21 | componentwise minimum and per-field provenance | PASS | C2 is the strict minimum on A0, A1 and A2 of all five cells; my provenance = `{A0:C2, A1:C2, A2:C2}` × 5, matching `C2_D5_FORECAST.cells[*].provenance` |
| 22 | `Gamma_exact`, `M_after_exact`, `H_exact` for all five cells | PASS | **bit-identical as exact rationals** on all five cells, via Γ = (R.hi − e0·D.lo) + ρ·x_hi·M with M = min(M_R2, mag(R2 ∩ 𝓗₅)) |
| 23 | magnitudes and margins | PASS | 3.615110 / 3.511946 / 3.451359 / 3.452456 / 3.400934; M_needed 4.891579 / 3.905056 / 3.076148 / 2.432398 / 1.969828; margins 1.35309× / 1.11194× / 0.891× / 0.705× / 0.579× |
| 24 | required uniform atom-constant reductions | PASS | 1.0 / 1.0 / 1.1407635748 / 1.5002877825 / 1.8990148694 by my own bisection, matching to all printed digits |
| 25 | the gate's baseline is an honest transcription of C1's result | PASS | my bisection under the C1 supply alone gives 1.0 / 1.0 / 1.2620572570527 / 1.6634509287531 / 2.1015967636536, agreeing with `baseline.requirement` to < 2·10⁻¹⁵ |
| 26 | gap falls and material-tightening verdicts | PASS | 46.28518348 % / 24.59309937 % / 18.38984108 %; ≥ 20 % on 307, 308, not on 309 — matching `materially_tightened` |
| 27 | class = D_PARTIAL, closed = {305, 306}, still open = {307, 308, 309} | PASS | follows mechanically from 24–26 under the frozen classes |
| 28 | C3: D2 4.6–6.2×, D1 3.1–4.7×, D_lo ≈ +7 %, τ/C_T 2–3 % worse | PASS | D2 4.5557–6.2337×; D1 3.1086–4.6730×; D_lo +6.777…+7.127 %; τ **+1.895…+2.235 %** worse; C_T **+2.797…+2.937 %** worse. (τ's low end is 1.90 %, marginally outside the stated "2–3 %".) |
| 29 | C2: radius decomposition f_G 73–80 %, Env4 19–26 %, rest negligible | PASS | my grouped shares match `C2_D1_BLOCKER.json` to < 10⁻¹²: f_G 0.7308–0.8011, Env4 0.1880–0.2622, all remaining terms < 0.61 % |
| 30 | C2: the D1 markdown's third blocker agrees with its own evidence | **FAIL** | `D1_BLOCKER_DIAGNOSIS.md` §1 states `DOMINANT_BLOCKER_3 = order-2 residual f_H 0.13-0.18 %` and prints "~0" for f_D and f_F. `C2_D1_BLOCKER.json` names `order0_residual_fF`, share 0.285–0.602 %, and f_D (0.282–0.342 %) is also larger than f_H (0.135–0.180 %). The ranking of the three negligible terms is inverted in the prose. Note 6 |
| 31 | C2: the sensitivity table | PASS | reproduces to < 10⁻¹⁴ on all five cells: D_lo +8.603…+8.719 %, τ +8.018…+8.168 %, C_T +1.360…+1.395 %, D1 +0.536…+0.570 %, D2 +0.070…+0.073 %, A_all ≡ τ |
| 32 | …under the convention the document actually uses | INFO | "a 10 % improvement" is implemented as *scale by 1.1 in the improving direction* (X/1.1 for an upper bound, X·1.1 for D_lo). Internally consistent and it is what makes A0 = τ/D_lo respond symmetrically, but the convention is unstated; the natural reading (×0.9) gives ~10 % larger gains and reverses the D_lo-vs-τ ordering. Note 7 |
| 33 | worst-over-sub-blocks composition: C_T, τ, D1, D2 = MAX; D_lo = MIN | PASS | re-derived from `sub_rows` for all five cells: every field matches the max/min exactly and **no field matches the inverted aggregate**. `c2_refined_registry.verify()` re-derives the same composition |
| 34 | …and no silent max/min inversion anywhere | PASS | on every cell all five extrema fall on sub-block 0 (the leftmost), so the whole-cell composition coincides with the per-sub-block composition; there is no mixing across sub-blocks |
| 35 | the implementation can fail: 6 operator constants | PASS | +1 % on τ / C_T / D_lo / D1 / D2 moves Γ by +2.17e-3 / +3.95e-4 / −2.20e-3 / +4.71e-5 / +4.31e-6; Ā moves Γ only downward (×0.5 → −8.0e-2), which is the inertness of row 42 |
| 36 | …ρ, x_hi, each candidate supremum, each norm, H_at_a, a W2 endpoint, A0/A1/A2 | PASS | all move Γ in the binding direction: x_hi +1 % → +2.49e-3; ρ +1 % → +2.49e-3; sup.F/D/H(r=0) → +7.7e-5/+8.7e-5/+8.1e-5; k₀…k₄ → +2.5e-4…+6.2e-6; j₀…j₄ → +1.0e-4…+2.0e-5; sup_S0[0..4] → +8.1e-5…+1.2e-6; H_at_a(r=0) +1 % → +3.8e-5; W2[0:0].lo −0.01 → +5.5e-4; A0/A1/A2 +1 % → +1.76e-3/+3.75e-4/+3.94e-5 |
| **C. Soundness of the refinement, and operator-only** |
| 37 | the adopted machinery is used unchanged | PASS | `taboo_certify.py` sha256 = `ced9422c…`, equal to `TABOO_SHA256` in `c2_refined_registry.py` and to `code_sha256.taboo_certify`; the file has one commit in its history (`760b3993`, its adoption). `cells.json` sha = `341eb5e9…` as pinned |
| 38 | N_k = ceil(2ρ_k / (1/100)) = 9, 9, 10, 11, 11 | PASS | exact ceil of 2ρ/(1/100) gives 9, 9, 10, 11, 11 and `sub_blocks` / `len(sub_rows)` agree |
| 39 | the sub-blocks tile each cell exactly | PASS | equal width (e_hi−e_lo)/N; row *i* is exactly [e_lo + i·w, e_lo + (i+1)·w]; row 0's e_lo and row N−1's e_hi equal the frozen cover's `left`/`right`; no gap, no overlap; every width ≤ 1/100 |
| 40 | worst-over-a-cover is a valid whole-cell bound | PASS | Lemma T / SM / Dv hypotheses are stated "on a drift set E"; each sub-block certificate holds uniformly on its sub-block, the sub-blocks cover the cell, so the max bounds the cell sup and the min the cell inf, and all six hypotheses hold simultaneously with E = the cell. Note 8 |
| 41 | the registry's own premises hold | PASS | τ ≥ 1, C_T ≥ τ, 0 < D_lo ≤ 1, Ā ≥ 1 and Ā ≥ τ/D_lo on all five cells; all 105 committed artifacts are `certified: true` with `margin_lower_bound > 0`, correct `kind`, and sha256 matching their registry rows; the denominator artifact's (e0, ρ) equals its sub-block's (mid, half) and its (τ, C_T) inputs equal the row's |
| 42 | Ā is inert on all five cells under BOTH registries | PASS | τ/D_lo vs Ā: C1 6.884/6.411/5.987/5.590/5.210 and C2 6.564/6.122/5.714/5.332/4.976 against Ā 8.291/7.912/7.556/7.218/6.901 — Ā exceeds τ/D_lo by 20–39 % everywhere, so Ā_eff = τ/D_lo throughout |
| 43 | keeping Ā at all is defensible | PASS (opinion) | yes: it is the adopted Lemma Dv′ interface, it is a genuinely independent second bound that could bind on other data, and it costs 282 s of 9 688 s (2.9 %) of the registry budget. Keeping it *per cell* rather than per sub-block is right precisely because it never binds. Note 9 |
| 44 | `NEW_REAL_ADDRESSES = 0` | PASS | the registry path forms only the kernel, its atom split, h₁ and polynomial supersolutions (`taboo_certify` §docstring, `block_artifact`/`cell_artifact`); the forecast path reads sealed records and replayed measurements and **refuses** any measurement with `order3_fields_present`; no gated order-3 entry point (`certify_real_cell`, `rung3_engine.certify_order3`, `rung3_residual.g_residual`) is reachable; the registry domain is exactly {305…309} |
| 45 | …does anything read a K1 record, a source, an F/D/H/G candidate, or a value of R? | PASS with scope | not in the **registry** (the claim `OPEN_NOTES_DISPOSITION_C2.md` actually makes). The **forecast** does read sealed K1 records, the replayed δ/ε of the F/D/H candidates and the adopted R/R′/R″ intervals — that is replay of adopted evidence, not a new real evaluation, and the disposition is correctly scoped |
| **D. The τ regression** |
| 46 | verified per cell from the sub-block rows | PASS | τ and C_T are monotone decreasing in e across every cell's sub-rows; the worst sub-block is always sub-block 0; C1 whole-cell τ vs C2 sub-block-0 τ: 5.2912→5.3914, 5.0707→5.1698, 4.8519→4.9521, 4.6338→4.7345, 4.4185→4.5173 |
| 47 | is it a red flag for soundness? | PASS (opinion) | **No.** `block_proposal(ec, …)` builds the degree-20 candidate from the float taboo solve at the block **centre** and scales it by α; the worst sub-block's centre sits ρ(1−1/N) to the left of the cell centre. Predicted regression = |dτ/de|·ρ(1−1/N) matches the observed to 1.8–2.0 % on τ and 2.8–3.1 % on C_T. Both bounds are valid; C2's is simply the weaker certificate on those two fields. Note 10 |
| 48 | both C1 and C2 take the same α rung | PASS | `taboo_alpha = 6/5` (the first rung) for C1's whole-cell block and for C2's sub-block 0 on all five cells — the regression is not a rung change |
| 49 | would a mixed operator supply be better, and was C2 right not to take it? | PASS (opinion) | It would be better, and C2 was right to refrain: the gate pre-registers the minimum on A0/A1/A2 **across supplies**, not on the six operator constants, so a mixed operator tuple is not what was pre-registered and taking it after seeing the τ regression would be exactly the post-hoc choice the gate forbids. Note 11 records what it would have bought |
| **E. Adoption** |
| 50 | Γ(306) = −0.030469, margin 1.112×, fails ×1.25 degradation | PASS | Γ_deg(306) = +0.029163293, bit-identical to `C2_ROBUSTNESS_AND_R_ATTRIBUTION.json`; 305 survives at Γ_deg = −0.033733237 |
| 51 | C1 reviewer's condition "independent re-certification by a second implementation (or at minimum a second execution on a second host)" | **FAIL** | C2 re-executed the **same** pinned `taboo_certify` bytes on a different partition. That is a re-execution with different inputs, not a second implementation; and `REGISTRY_C2.json` records **no host, no toolchain, no precision** at the registry level, so it cannot even be established that a second host was used. Note 12 |
| 52 | C1 reviewer's condition "a finer taboo block partition on 306" | PASS | delivered: 9 sub-blocks of width ≤ 1/100 against C1's single block of width 2ρ ≈ 0.0867; margin 1.9 % → 11.2 % |
| 53 | C1 reviewer's condition "a stated, frozen margin floor" | **FAIL** | none exists. The C2 gate defines no margin floor and no degradation scenario, and `D_STAGE_DECISION.md` §3 says so. C2 is again deciding "is 11.2 % enough?" *after* seeing 11.2 %. Note 12 |
| 54 | is the re-certification enough to adopt 306? | INFO (opinion) | Closer, but not yet — see Note 12 for what I would require |
| 55 | nothing in the namespace pre-empts freeze, qualification or adjudication | PASS | no seal, no protocol, no coverage map r5, no ADOPTED claim beyond the gate's forward-looking language; the R-stage design states DESIGN ONLY, guard DENY, and lists N1/N3/N5 as preconditions |
| **F. The adversarial suite** |
| 56 | `c2_mutations.py` re-runs 33/33 | PASS | rerun locally: `{"applied": 33, "real_mutants": 25, "static_assertions": 8, "detected": 31, "equivalent": ["M19_selector_single_supply","M20_selector_min_by_A0_only"], "undetected": [], "pass": true}`, and the output JSON is **byte-identical** to the committed `C2_MUTATIONS.json` |
| 57 | separating 25 real mutants from 8 static assertions is honest | PASS | the static eight are substring checks that a control *exists*; the module says so in its docstring and the JSON reports the split, so "33/33" is not inflated |
| 58 | are M19/M20 genuinely equivalent, or an artefact of C2 dominating? | PASS with note | Genuinely equal **on this data**, and only because C2 is the strict minimum on 15/15 fields. The recorded `equivalence_proof` says exactly that and scopes it correctly, and `D_STAGE_DECISION.md` §2 repeats it. Honest. But it is an artefact that would vanish on other data — Note 13 shows a free way to have made M20 load-bearing |
| 59 | mutation classes not covered by a real mutant | INFO | no real mutant on (i) the assembly coefficients c(m) = 1/t − 1/m or the 1/m weights, (ii) the sub-block tiling geometry (N_k off-by-one, gap/overlap), (iii) the intersection / M_after step (H ∩ record, M = min(M_R2, mag), the emptiness refusal). Note 14 |
| **G. The R-stage design** |
| 60 | critical ratios 37.32 / 23.26 / 14.16 under C2's constants | PASS | my own bisection with the adopted model (per-r `ag_max`, per-r `dg_max`, s_G = ratio·s_H entering Env4 and ρ|Ĝ(a)| entering the half-width) gives 72.71753 / 54.86736 / **37.32219** / **23.26035** / **14.15799** — exact to all printed digits |
| 61 | the comparison column "under C1 constants" = 32.03 / 19.20 / 10.55 | **FAIL** | those are **Campaign B's Lemma-G** values. My Lemma-G-only bisection reproduces them exactly (64.72474 / 47.98610 / 32.03283 / 19.19506 / 10.54598 = `TAIL_FORECAST_R2.critical_sup_G_over_sup_H_ratio`). Under C1's Lemma Dv′ constants the true values are **34.55795 / 20.93621 / 12.18694**. Note 1 |
| 62 | "C2's deterministic work raised every threshold by 16–34 %" | **FAIL** | that is the improvement over **Campaign B**. Over C1 it is **+8.0 % / +11.1 % / +16.2 %**. The claim overstates C2's own contribution by roughly a factor of two, in both `R_STAGE_DESIGN.md` §2 and `D_STAGE_DECISION.md` §5. Note 1 |
| 63 | "cell 307 is now inside the adopted range at its lower end" | INFO | true as stated (37.32 > 34.79), but the componentwise minimum of the two supplies available **at the end of C1** already gives 34.82089, marginally inside. The "now" carries more weight than the arithmetic supports. Note 1 |
| 64 | "an anchor at one cell does not certify a neighbour" | PASS | correct. Theorem TC-T fixes F̂, D̂, Ĥ, Ĝ at that cell's own midpoint and the centre-motion term is ρ|Ĝ(a)| on that cell; there is no transport theorem for Ĝ across cells, and C2 explicitly declines to propose one |
| 65 | is recommending one address defensible, or under-powered? | PASS (opinion) | defensible and correctly conservative: 307 has the highest critical ratio, is the only still-open cell inside the adopted range, and one measurement of s_G/s_H settles the *estimate* for all three. Under-powered only in the sense that its stated justification is weaker than claimed (rows 61–63) and its "deterministic exhausted" premise is not established (Note 11) |
| 66 | the R-stage eligibility test (a) and (b) | PASS | (a) three cells remain open; (b) with f_G at its `eps_src[3]` floor my magnitudes are 1.0933645 / 1.0986971 / 1.1311143 / 1.1744072 / 1.1995424 and Γ = −0.261936 / −0.217516 / −0.171756 / −0.126655 / −0.087330 — all five close, bit-identical to the committed values. The D1 version under C1's constants also reproduces exactly |
| 67 | compute caps respected | PASS | registry CPU sums over the 105 rows to 9687.627 s = **2.691 CPU-h**, matching `cpu_seconds_total` and `D_STAGE_DECISION.md`'s "2.69 CPU-h", inside the gate's 12 (forecast) / 20 (hard) D-stage caps; the R-stage forecast of 0.44 / 1.3 CPU-h is inside the 3 / 6 new-real caps |
| **H. C8 and everything else load-bearing** |
| 68 | nothing outside the C2 namespace was modified | PASS | `git diff --name-status 5289b6ce..HEAD` = 123 entries, **all `A`**, all under `p5y_k5_tail_c2_closure/` |
| 69 | predecessor namespaces byte-unchanged | PASS | implied by row 68, and independently: all 34 B0 pins re-hash to their recorded sha256 today, with zero mismatches |
| 70 | coverage map r4 untouched, no r5 | PASS | `K5_COVERAGE_MAP_R4.json` sha = `a3bddd83…` as pinned, single commit `f2ac1eb3` in its history; no r5 file anywhere; r4 still shows m = 1, 2, 3 complete and m = 5 non-PASS exactly on 305–309 |
| 71 | `main` untouched | PASS | `main` = `c123b9bb` is an ancestor of HEAD; `git branch --contains 87309610` returns only `p5y-k5-tail-c2` |
| 72 | `OPEN_NOTES_DISPOSITION_C2.md` matches what the code does | PASS | N1: no order-3 entry point reachable, no bridge issued, carried forward — matches. N3: σ₃, σ₄, tower, `eps_src`, `H_at_a`, `W2` are Campaign B's byte-for-byte (verified by reading them from `TCT_INPUTS_*` / `ADOPTED_TAIL_INPUTS.json` and reproducing every downstream number) and only A0/A1/A2 are substituted — matches. N5: `order3 = None` throughout, `order3_fields_present` refused, M09 present — matches. The (P3′) description matches the code and my reimplementation |
| 73 | replay gate "adopted post-Campaign-A state reproduces the sealed consumption pass ranges" | NOT_CHECKABLE_LOCALLY | the K1 record store is not in the repository; `c2_d5_forecast.py --records` cannot be run here |
| 74 | "no previously passing cell regresses; m = 1, 2, 3 remain complete on 0–309" | NOT_CHECKABLE_LOCALLY (partial) | same reason. What I can establish: the C2 registry covers exactly {305…309}, so cells 0–304 are structurally untouched; and for the tail I confirm the m = 5 direct test independently |
| 75 | the Arb/flint operator certification itself | NOT_CHECKABLE_LOCALLY | `taboo_certify` imports `numpy` and `flint`, neither installed. I verified sha pins, artifact/row consistency, premises, geometry and margins, but not the certified supersolutions themselves |
| 76 | f_G adds `eps_src[3]` on top of a σ₃ that already contains the same midpoint source error | INFO | σ₃ takes the adopted branch on every (cell, r ≥ 1), and `eps_src[3]` equals `midpoint_eps["S:r:3"]` to ≥ 9 significant digits, so the allowance is counted twice. Declared in `THEOREM_TCT.md` §2 as "a valid extra allowance", safe direction, ≈ 0.04 % of f_G |
| 77 | the Lemma Dv′ supplies use the universal κ rather than the cell's drift-aware norms | INFO | κ₁ = 0.7978846, κ₂ = 0.9678830 against the cell's own k₁ ∈ [0.79707, 0.79767], k₂ ∈ [0.96498, 0.96705], which are also valid on the cell by (P1). Conservative; leaves 0.02–0.2 % on A1/A2 |
| 78 | README still describes the campaign as unstarted | INFO | `README.md` is frozen at `87309610` and still shows "D1–D5 | `phase_d/` | —" and "R-stage design | `phase_r/` | —". Defensible as a pre-registration document, but the namespace's front door reports no result |
| 79 | no committed re-verification run of the C2 registry | INFO | `c2_refined_registry.py verify` exists and re-derives every artifact and the composition, but no output artifact is committed; the registry's re-verifiability is asserted, not demonstrated in-repo |

---

## Notes

### Note 1 (FAIL) — the critical-ratio comparison is against the wrong campaign

`phase_r/R_STAGE_DESIGN.md` §2 and `phase_d/D_STAGE_DECISION.md` §5 both present:

| cell | "under C1 constants" | under C2 constants |
|---|---|---|
| 307 | 32.03 | 37.32 |
| 308 | 19.20 | 23.26 |
| 309 | 10.55 | 14.16 |

and conclude "C2's deterministic work raised every threshold by 16–34 %".

The left column is not C1. I bisected the critical s_G/s_H ratio myself under each supply in turn, with the adopted
evidence model (per-r `ag_max`, per-r `dg_max`, s_G = ratio·s_H entering Env4 and ρ|Ĝ(a)| entering the half-width).
My C2 column reproduces C2's published values exactly, which validates the model. My **Lemma-G-only** column
reproduces 64.72474 / 47.98610 / 32.03283 / 19.19506 / 10.54598 — that is, digit for digit, Campaign B's
`TAIL_FORECAST_R2.critical_sup_G_over_sup_H_ratio`, whose `premise_supply` field states plainly that "every route
uses `tct_rule.tail_enclosure` with the **Lemma-G constants**".

C1 never computed a critical ratio (there is none in `C1_FORECAST.json`, `C1_DIAGNOSTIC_MIN.json` or
`C1_EXECUTION_DECISION.md`). Under C1's actual Lemma Dv′ constants the values are:

| cell | Lemma G (Campaign B) | **C1 (true)** | min(G, C1) | C2 |
|---|---|---|---|---|
| 307 | 32.03283 | **34.55795** | 34.82089 | 37.32219 |
| 308 | 19.19506 | **20.93621** | 21.26612 | 23.26035 |
| 309 | 10.54598 | **12.18694** | 12.42428 | 14.15799 |

So C2's improvement over C1 is **+8.0 % / +11.1 % / +16.2 %**, not +16–34 %. The quoted range is the improvement
over Campaign B, two campaigns back, presented under C1's name. And the claim that C2 moved 307 "inside the adopted
range at its lower end" (34.8–80.5) is weaker than it reads: the componentwise minimum of the two supplies already
available when C1 stopped gives 34.82089, already marginally inside.

This matters because it is the arithmetic that justifies spending the programme's first real order-3 tail address,
and because it is the same defect class C1's own pre-freeze reviewer caught in C1 — a comparison computed on a
different quantity than its label states. The repair is a text edit plus three numbers, all supplied above; the
recommendation itself (one address, cell 307) survives the correction.

### Note 2 (context) — what reproduces

Everything decision-relevant reproduces **bit-exactly as rationals** from an implementation I wrote from the theorem
documents alone: all five `Gamma_exact`, all five `M_after_exact`, all five `H_exact`, both registries' Lemma Dv′
constants, the Lemma G constants, the componentwise minimum and its provenance, the five required uniform
reductions, the gate's own baseline, the D1 radius decomposition, the D1 sensitivity table, the ×1.25 degradation,
the order-3 attribution test, the critical ratios, and the mutation suite's JSON byte for byte. Two independent
structural checks also pass: my assembly reproduces the derived identity gate's worst 3.63·10⁻⁸, and my Lemma Dv′
derivation is a third independent path agreeing with C2's two. I found no arithmetic error anywhere in C2.

### Note 3 (FAIL, and the fairness question) — the measure change

Three things are true at once and the campaign states only the first.

1. **The gap is the right measure.** A cell closes when its requirement reaches 1, so requirement − 1 is exactly
   what remains. The raw-requirement ratio is not a measure of remaining distance. C2 is right to change it.
2. **The gate's stated reason for changing it is backwards.** `why_gap_and_not_ratio` says the ratio measure
   "flatters a cell that is already nearly closed and penalises one that is far from closing". Since gap <
   requirement, Δ/gap > Δ/requirement always, and the ratio therefore always reports the *smaller* number — most
   severely for a nearly-closed cell. A cell that goes from requirement 1.05 to exactly 1.0, i.e. closes
   completely, scores 4.8 % on the ratio measure and 100 % on the gap measure. The ratio measure *penalises* the
   nearly-closed cell; it cannot flatter it. The correct half of the sentence carries the argument on its own.
3. **The change is more permissive where C2 needed it.** 20 % of gap is stricter than 10 % of requirement iff
   gap > 1. C2's baseline gaps are 0.262 / 0.663 / 1.102, so the new test is looser on 307 and 308 and marginally
   stricter on 309. Concretely, under C1's measure and threshold applied per cell, C2's requirement falls are
   **9.611 % / 9.809 % / 9.639 %** — all three below 10 %, all three would fail. Under C2's measure they are
   46.29 % / 24.59 % / 18.39 % and two pass. C2 publishes only the second set, with no statement of what the first
   set is.

Read narrowly, then: **yes, C2 chose the measure on which its own numbers look between 2.4× and 4.8× better, and
that choice is what earns 307 and 308 their "materially tightened" verdict.** Note 4 is why that is nevertheless
not the whole answer, and why I do not think C2 gamed its gate.

### Note 4 (INFO) — C2's gate is, in net, harder on C2 than C1's was

C2 changed four things at once, and two of them are strictly harder:

| | C1's gate | C2's gate | effect on C2 |
|---|---|---|---|
| measure | fraction of raw requirement | fraction of gap above 1 | looser where gap < 1 |
| threshold | 10 % | 20 % | — (interacts with the above) |
| scope | the **worst** still-open cell, one test | **every** still-open cell | **harder** |
| baseline | Campaign B (2.252903 at 309) | Campaign C1 (1.0/1.0/1.2621/1.6635/2.1016) | **harder** |

Applying C1's gate verbatim to C2's result: the worst still-open requirement is now 1.8990148694 against C1's frozen
baseline 2.252903, a fall of **15.708 %** ≥ 10 % ⇒ the material-improvement test **passes**; C2 closes ≥ 2 cells and
306 ∈ {306, 307, 308, 309} ⇒ the class would be **USEFUL**. Under its own gate C2 is D_PARTIAL. (C1's own fall was
6.716 %, which is why C1 was MARGINAL.)

So C2 wrote a gate that puts it in a **lower** class than its predecessor's gate would have. That is the opposite of
flattering, and I record it prominently because check 6 and Note 3 read harshly on their own. What C2 should have
done, and did not, is say this: publish the predecessor-scale numbers alongside its own, and state which direction
each of the four changes cuts.

### Note 5 (INFO) — the D_PARTIAL adoption rule bore no risk

The gate's D4 rule takes the componentwise minimum over three supplies, one of which is C1's. Γ is monotone
non-decreasing in each A_j (rad_r = A0·p2 + 2A1·p1 + A2·p0 with p0, p1, p2 > 0; a wider 𝓗 gives a larger mag; Γ
increases in M). C2's constants are therefore componentwise ≤ C1's on every cell, so any cell C1 closed, C2 closes.
The gate's own `baseline.requirement` records 305 and 306 at exactly 1.0. Hence at the moment the gate was frozen it
was already arithmetic that C2 would close ≥ 2 cells, that D_INSUFFICIENT was unreachable, and that the D_PARTIAL
rule would fire and something would be adopted.

I do not call this a defect: the rule is right on the merits, the inputs to the inference are all in the gate itself,
and nothing is concealed. But "the comparison is pre-registered here and is not left to judgement after the fact" is
a claim about a test whose outcome was already determined. The only genuinely open question the gate posed was
whether 307/308/309 would clear 20 %, and the answer was 2 of 3.

### Note 6 (FAIL) — the D1 markdown contradicts its own evidence on which term is third

`D1_BLOCKER_DIAGNOSIS.md` §1 asserts `DOMINANT_BLOCKER_3 = order-2 residual f_H  0.13-0.18 %, i.e. nothing`, and its
table prints "~0" in the `order-1 f_D` and `order-0 f_F` columns. `C2_D1_BLOCKER.json` says
`"DOMINANT_BLOCKER_3": {"term": "order0_residual_fF", "share": 0.006025}`. My own decomposition (matching the JSON
to < 10⁻¹²) gives, per cell 305…309:

| term | share |
|---|---|
| f_F | 0.602 %, 0.545 %, 0.475 %, 0.378 %, 0.285 % |
| f_D | 0.320 %, 0.340 %, 0.342 %, 0.322 %, 0.282 % |
| f_H | 0.170 %, 0.179 %, 0.177 %, 0.161 %, 0.135 % |

The ordering of the three small terms is exactly inverted in the prose, and the two the prose calls "~0" are the two
larger ones. No conclusion depends on it — all three are under 1 % and "everything else is negligible" is correct —
but a diagnosis document that disagrees with its own machine-readable evidence should not be frozen.

### Note 7 (INFO) — the sensitivity table's unstated convention

"A 10 % improvement in one input" is implemented as *scale by 1.1 in the improving direction*: τ, C_T, D1, D2 and
each A_j are divided by 1.1; D_lo is multiplied by 1.1. Under that convention my values match the committed ones to
< 10⁻¹⁴ on every cell and every input. Under the more natural reading (upper bounds × 0.9) every gain is about 10 %
larger and, more visibly, the D_lo-vs-τ ordering **reverses** (τ +8.82 % > D_lo +8.60 % at cell 305, instead of
D_lo > τ). The document's conclusion — D_lo and τ are the only operator levers with weight, D2 is irrelevant — is
robust under both conventions, so this is presentation only; but state the convention.

### Note 8 (opinion) — why the worst-over-a-cover is valid

Lemma T, Lemma SM and Lemma Dv/Dv′ of theorem AD are all stated over an arbitrary drift set E: τ_a ≤ τ, ‖Ĝ_e‖ ≤ C,
D_e ≥ D_lo, |∂D| ≤ D1, |∂²D| ≤ D2 for every e ∈ E. Each sub-block certificate establishes those six inequalities
uniformly on its own sub-block. The sub-blocks tile the cell exactly (check 39), so every e in the cell lies in some
sub-block; taking the max of the five upper-bounded quantities and the min of the one lower-bounded quantity yields
six inequalities that hold simultaneously for **every** e in the cell, which is precisely the hypothesis with E =
the cell. The construction is therefore valid, and it is tighter than a single wide certificate exactly when the
per-sub-block bounds are tighter — which, on D_lo, D1 and D2, they are (4.6–6.2× on D2). It happens that all five
extrema fall on sub-block 0, so no mixing across sub-blocks occurs and the composed constants are literally sub-block
0's constants.

### Note 9 (opinion) — keeping Ā

Ā is dead weight on this domain: τ/D_lo is 20–39 % below Ā on all five cells under both registries, so
Ā_eff = min(Ā, τ/D_lo) = τ/D_lo everywhere, and my perturbation confirms it (Ā +1 % moves Γ by exactly zero; Ā ×0.5
moves it by −8·10⁻²). Keeping it is still right: it is the adopted Lemma Dv′ interface, it is an independent bound
that binds on other domains (the adopted front's whole-kernel ARL is the sharper of the two there), and at 282 of
9 688 CPU-seconds it is 2.9 % of the registry budget. Keeping it *per cell* rather than subdividing it is the
correct economy, and C2 justifies it explicitly from the D1 finding.

### Note 10 (opinion) — the τ/C_T regression is the anchor, not the partition

`taboo_certify.block_proposal(ec, α, β, …)` solves the float taboo system at the block **centre** `ec` and takes
w := dyadic_candidate(α·g + β); τ = w(a) and C_T = sup w then inherit that centre. On a cell, C1's centre is e0; on
the worst sub-block, C2's centre is e0 − ρ(1 − 1/N). Since τ and C_T decrease in e, C2's certificate is anchored at
a worse drift. Predicting the regression as |dτ/de| · ρ(1 − 1/N), with the slope read off C2's own sub-rows:

| cell | predicted Δτ | observed Δτ | ratio | predicted ΔC_T | observed ΔC_T | ratio |
|---|---|---|---|---|---|---|
| 305 | +0.09856 | +0.10029 | 1.018 | +0.16395 | +0.16865 | 1.029 |
| 307 | +0.09836 | +0.10018 | 1.019 | +0.14904 | +0.15340 | 1.029 |
| 309 | +0.09685 | +0.09876 | 1.020 | +0.13332 | +0.13739 | 1.031 |

The residual 2–3 % is the narrower block's smaller R₂ allowance pulling the other way. So the regression is fully
explained, it is an artefact of where the candidate is anchored (not of the α ladder — both take the same first rung
6/5, on all five cells), and it is not a soundness signal. Both certificates are valid; C2's is simply weaker on
those two fields and stronger on the other three.

### Note 11 (opinion, and the one that matters for the R stage) — a mixed operator supply reaches the gate's bar on 309

C1's and C2's registries certify the *same six quantities* over the *same cell*, both uniformly. The componentwise
best of the two — τ, C_T, D1, D2 by min, D_lo by max — therefore satisfies all six Lemma Dv′ hypotheses
simultaneously and is a **sound** supply. Feeding it through my implementation:

| cell | requirement | gap | gap fall vs the gate's baseline | ≥ 20 % |
|---|---|---|---|---|
| 307 | 1.11196624 | 0.11196624 | **57.27 %** | yes |
| 308 | 1.46065480 | 0.46065480 | **30.57 %** | yes |
| 309 | 1.84787350 | 0.84787350 | **23.03 %** | **yes** |

All three still-open cells clear 20 %, which under the frozen classes is **D_USEFUL**, not D_PARTIAL.

C2 was right not to do this: the gate pre-registers the minimum on A0/A1/A2 across *supplies*, not on the six
operator constants, and taking a mixed operator tuple after seeing the τ regression is exactly the post-hoc choice
the gate exists to forbid. C2 refrained and said nothing about it, which is correct conduct.

But the consequence is load-bearing and must be recorded before the R stage is designed. The gate's own reading of a
sub-20 % result is "the deterministic direction is exhausted and the programme should route to the R stage rather
than grind". That reading is **not established**. A successor that pre-registers the operator-level combination —
using constants that are already certified, already committed and already reviewed, at zero new CPU — reaches the
gate's own bar on every open cell. The honest statement is that C2's *pre-registration*, not the deterministic
direction, is what ran out. Spending the programme's first real order-3 tail address on the strength of "309 came in
at 18.39 %" would be spending it against a number that a cheaper, sound, pre-registerable deterministic step
already beats.

### Note 12 (opinion, FAIL) — cell 306

C1's reviewer asked for three things before 306 is adopted. C2 delivered one and a half.

- **Finer partition — delivered, and it worked.** Nine sub-blocks of width ≤ 1/100 against one block of width
  2ρ ≈ 0.0867; the K5-B margin went from 1.9 % to 11.2 %, a 5.8× improvement, and Γ from −0.005719 to −0.030469.
  This was the reviewer's "cheapest available real margin" and C2 spent it. Credit where due.
- **Independent re-certification — not delivered.** C2 re-executed the *same* `taboo_certify` bytes (sha pinned,
  and I verified the pin) with different inputs. A systematic error in the Arb supersolution machinery survives
  that unchanged, and that machinery is the one surface neither I nor C1's reviewer can check locally. The
  `atomx` channel cross-checks the *assembly* of A0/A1/A2 from the six constants with a second implementation — I
  independently confirm that assembly is correct — but nothing cross-checks the six constants themselves.
  `REGISTRY_C2.json` records no host, no venv and no precision, so "at minimum a second execution on a second host"
  cannot even be assessed from the artifact.
- **Pre-frozen margin floor — not delivered.** The C2 gate has no margin floor and no degradation scenario at all.
  C2 notes this itself and calls the robustness figures "supplementary; not gate inputs". So the programme is once
  again asking "is 11.2 % enough?" after seeing 11.2 %, which is the exact failure mode both predecessor gates were
  written against. And 306 still does **not** survive the ×1.25 degradation (Γ_deg = +0.029163), while 305 does
  (Γ_deg = −0.033733).

My opinion: 305 should be adopted without further conditions — margin 1.353×, survives degradation, three
independent derivations, nothing contentious. 306 is much stronger than it was and I would not block it forever,
but I would require, before it is adopted:

1. a **margin floor set by the adjudicator**, not by C2 — since the number is already public, C2 cannot freeze one
   honestly, so the floor must come from outside the campaign;
2. a **re-execution of cell 306's nine taboo and nine denominator artifacts at higher precision** (the artifacts
   carry `bits: 256`; re-running at 384 and checking every certified C_T/τ/D_lo/D1/D2 is still on the safe side of
   the published value) **and on a different host**, with the host and toolchain recorded in the artifact — this is
   cheap, needs no second implementation, and directly attacks the un-cross-checked surface;
3. a committed run of `c2_refined_registry.py verify` on a host with the toolchain, with its output as evidence
   (check 79);
4. failing 1–3, adopt 305 alone now, which is uncontested, and let 306 ride with the R-stage successor. That is a
   legitimate `partial_adoption` outcome under the gate and it costs the programme nothing.

### Note 13 (INFO) — M19/M20 could have been made load-bearing for free

The two selector mutants are equal to the pre-registered minimum only because C2 dominates on 15 of 15 fields, and
C2 records exactly that, twice, in honest language. I accept the classification.

It is worth noting how cheaply it could have been a real test. On the `{G, C1}` sub-family alone — both supplies
already loaded by the suite — the componentwise minimum genuinely mixes: at cell 307, A0 comes from C1 (5.98712 <
6.67929) while A1 comes from **G** (35.57778 < 36.16689); the same holds at 309. `M20_selector_min_by_A0_only` run
against `{G, C1}` would pick C1 for all three and differ on A1, i.e. it would be detected. One extra probe over a
supply subset converts two "equivalent" rows into one genuine detection of the rule the gate calls its central
innovation.

### Note 14 (INFO) — what the suite does not mutate

Three load-bearing mechanisms have no real mutant:

- **the assembly coefficients** c(m) = 1/t − 1/m and the 1/m weights. M08 swaps a W *endpoint* but never a
  coefficient. A coefficient error would be caught by `xcheck` only if the crosscheck path re-derives the assembly
  table (`THEOREM_TCT.md` §5 says it does, since note N15), so a channel exists but is never exercised;
- **the sub-block tiling geometry** — an off-by-one in N_k, a gap, or an overlap. M11–M14 perturb which *row* is
  selected, never the geometry. A tiling that failed to cover part of the cell would be silently unsound;
- **the intersection and M_after step** — H ← H ∩ 𝓗₅, M ← min(M_R2, mag(H)), and the emptiness refusal. A min/max
  swap or a skipped refusal here is a direct soundness hole and nothing probes it.

I checked all three by hand in this review and all three are correct. The point is that the suite would not have
told anyone.

### Note 15 (INFO) — smaller things

- `D_STAGE_DECISION.md` §2 says τ and C_T "got 2–3 % worse"; τ is 1.895–2.235 %, so its low end is below 2 %. It
  says the net on A0 is "a 4.5–4.9 % gain"; measured as a fraction of C1's value it is 4.495–4.655 %, measured as
  C1/C2 − 1 it is 4.71–4.88 %. Both are loose rather than wrong.
- `R_STAGE_DESIGN.md` §2 says "δ_G at the worst adopted per-r value". The implementation uses **each r's own**
  `dg_max` and `ag_max`, not the worst; that is the correct choice and it is what reproduces the published ratios
  (the worst-value reading gives 37.28 rather than 37.32). Fix the phrase, not the code.
- f_G adds `eps_src[3]` on top of a σ₃ that already contains the same midpoint source error (check 76). Declared,
  conservative, ≈ 0.04 % of f_G.
- The Lemma Dv′ supplies use the universal κ rather than the cell's tighter drift-aware norms, which are equally
  valid by (P1) (check 77). Conservative; worth 0.02–0.2 % on A1/A2 if a successor wants it.
- `README.md` is frozen at gate time and still reports D1–D5 and the R stage as "—" (check 78).

---

## What I did not check

- **The Arb/flint operator certification itself.** `taboo_certify` needs `numpy` and `python-flint`, neither
  installed here, so I could not re-run `block_artifact`, `cell_artifact`, `verify_block` or `verify_cell`, and I
  could not execute `c2_refined_registry.py verify`. What I did instead: verified the module's sha against its pin
  and its single-commit history, verified all 105 committed artifacts hash to the sha256 recorded in their registry
  rows, verified every C_T/τ/D_lo/D1/D2 in each row equals its artifact's field, verified each artifact's geometry
  against the row and the frozen cover, verified `certified: true` and `margin_lower_bound > 0` on every artifact,
  verified the Lemma T / SM / Dv premises on every composed cell, and verified the max/min composition. The
  supersolutions themselves are the residual trust surface, and they are the same surface C1's reviewer flagged.
- **The consumption over cells 0–309 and the replay gate.** The K1 record store is not in the repository, so
  `c2_d5_forecast.py --records` cannot run here. I could not verify "no previously passing cell regresses",
  "m = 1, 2, 3 remain complete on 0–309", the `tail_via` chain/direct attributions for m = 1, 2, 3, or
  `replay_gate: PASS`. I verified the m = 5 direct test on all five tail cells independently, and that the C2
  registry's domain is exactly {305…309} so cells 0–304 are structurally untouched.
- **The frozen K5-B theorem itself**, which is countersigned elsewhere; I used `k5b_literal`'s direct clause as the
  task specifies and did not re-derive the chain recurrence.
- **The provenance of the adopted inputs** (`TCT_INPUTS_*`, `ADOPTED_TAIL_INPUTS.json`, `cells.json`, the order-3
  evidence model) beyond their committed pins and B0's hash check. C2 alters none of them and I confirmed it alters
  none of them, but their own correctness is Campaign A's and Campaign B's, not C2's, and is not reopened here.
- **Whether the C2 registry was produced on a second host**, because the artifact does not record one.
- **The 0.681 / 34.8–80.5 lower-front evidence model**, which I took from the adopted Campaign-B record as given.

---

## Verdict counts

| verdict | count |
|---|---|
| PASS | 60 |
| INFO | 10 |
| NOT_CHECKABLE_LOCALLY | 3 |
| **FAIL** | **6** |
| **total** | **79** |

FAIL rows: 6 (gate justification inverted), 30 (D1 prose contradicts its own evidence), 51 (no independent
re-certification of 306), 53 (no pre-frozen margin floor), 61 (critical-ratio baseline mislabelled), 62 (improvement
overstated ~2×).

INFO rows: 7, 14, 32, 54, 59, 63, 76, 77, 78, 79. NOT_CHECKABLE_LOCALLY rows: 73, 74, 75.

**FINAL VERDICT: NOT_READY.**

The science is exact and I could not break it: every published rational reproduces bit-for-bit from an implementation
I wrote from the theorem documents, the gate is genuinely frozen before any C2 number existed, the refinement is
sound and operator-only, nothing adopted was touched, `main` is untouched, there is no r5, and nothing pre-empts the
freeze. The class D_PARTIAL and the closed subset {305, 306} are correct under the gate as written.

What blocks the freeze is not arithmetic, it is what would be frozen alongside it. Two documents that will justify
the programme's first real order-3 tail address carry a comparison against Campaign B labelled as Campaign C1,
overstating C2's own contribution by about 2× (Note 1); a third contradicts its own evidence file (Note 6); the
frozen gate's stated reason for its central measure change is directionally false (Note 3); and cell 306 is being
adopted without either of the two conditions the predecessor's reviewer set, on a margin judged sufficient after it
was seen (Note 12). Separately, and most consequentially for what happens next, a sound operator-level combination
that C2 could have pre-registered already clears the gate's own 20 % bar on all three open cells (Note 11), so the
premise that the deterministic direction is exhausted — the premise under which a real address would be spent — is
not established by this campaign.

To reach READY_TO_FREEZE I would want: the critical-ratio column relabelled and its three true values substituted,
with the improvement restated as +8 / +11 / +16 %; the D1 blocker prose corrected against its own JSON; a one-line
correction in the gate's justification carried in an erratum rather than by amending the frozen file, together with
the predecessor-scale figures published alongside C2's own; Note 11 recorded in the R-stage design as an explicit
alternative to spending an address; and either the adjudicator-set margin floor plus a higher-precision, recorded-host
re-execution of cell 306's eighteen artifacts, or adoption of 305 alone for now. None of that requires new science,
and none of it changes a single number C2 has published.

---

*Reviewer: independent fresh-context pre-freeze review. Worktree `/Users/suzhe/ReBaseGuard-k5c2`, branch
`p5y-k5-tail-c2` @ `5a94568a`. No remote host contacted; no writing git command run; no file modified except this
one.*
