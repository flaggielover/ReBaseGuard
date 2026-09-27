# TPT V3: theorem TPT on real, non-target lower-front cells

**Class:** NONTARGET_REAL_VALIDATION.

**Scope:** CUSUM cells 11–44 and m ∈ {1, 2, 3, 5}, giving 136 (cell, m) pairs. The cells cover e ∈ [0.0057097, 0.0252261] with ρ ∈ [2.66e-4, 3.10e-4].

**Target cells:** 0 evaluated. The runtime guard ran 139 times, with 0 refusals. The static scan of the v3 code reported 0 findings.

**Machine-readable results:** `validation/TPT_V3_LOWER_FRONT.json`, with per-pair results, the gate, a summary and the probes.

**Code:**
* `v3/tc_reder.py` re-derives theorem TC independently.
* `v3/tpt_v3_lower_front.py` is the driver.
* `tpt.py` (sha256 `9d497ef1…`) was imported and never edited.

## 1. Method

### Data

Only these inputs were read:
* `p5y_k5_lower_front_order3/evidence/tc_r1/cells/TC_CELL_{11..44}.json`;
* `TC_CONSUMPTION.json`, cut down to cells 11–44 in the same statement that loads it. The rest was deleted before any computation.

Two facts about `TC_CONSUMPTION.json`:
* Its per-cell `consumptions[m].cells` dict holds cells 0–159 only, so it has no entries for the target cells at all.
* No historical campaign module was imported. The import guard was installed first.

The per-file sha256 values are recorded in the JSON.

### Step 1: independent re-derivation of the TC enclosure 𝓗_m

This follows THEOREM_TC §2–3. It uses a deliberately different route from `tc_rule` and `tc_crosscheck`.

* **Taylor bounds.** p0, p1 and p2 are P(ρ), P′(ρ) and P″(ρ) of the single quartic `P(s) = f_F + s f_D + s² f_H/2 + s³ f_G/6 + s⁴ Env4/24`, with `f_X = δ_X + eps_src[order(X)]`.
* **Env4 (P3).** `Env4 = σ4 + Σ_{i=1..4} C(4,i) k_i · T_{4−i}(ρ)`, where T_n(ρ) is the n-th derivative of the candidate majorant `s_F + s s_D + s² s_H/2 + s³ s_G/6`, evaluated at ρ.
* **σ4.**
  * r = 0: `sup_S0[4]`.
  * r ≥ 1: the Leibniz expansion `Σ C(4,i) j_i ‖h_r^(4−i)‖`. It uses the true-object h-tower: ‖h_j‖ ≤ 1, ‖h_1^(n)‖ ≤ sup_S0[n−1], and ‖h_j^(n)‖ ≤ Σ_{i=0..n} C(n,i) k_i ‖h_{j−1}^(n−i)‖.
* **Radius and half-width.** `rad_r = A0 p2 + 2A1 p1 + A2 p0` and `half_r = ρ|Ĝ_r(a)| + rad_r`.
* **Assembly.** F_r gets weight 1/m. `W2["r:j"]` gets weight 1/t − 1/m, with j = t − r − 1.
* **Inputs taken as given.** The A-constants come from `tc_audit[cell][m]["A"]`.

### Step 2: reproduction gate

The gate requires the re-derived 𝓗_m to equal `tc_audit[cell][m]["H_TC"]` exactly, as rationals.

### Step 3: TPT

For each pair that passed the gate, a `tpt.CellProfile` was built from the same per-source quantities: H_at_a, |Ĝ(a)|, f_F…f_G, Env4, and the c-weighted W sum.

* **g_hi.** `g_hi = hi(R − e0·D) = R.hi − e0·D.lo`, taken from the consumed R and D. This is the frozen `k5b_literal` form of K5_GLOBAL_BRIDGE's Γ_k.
* **Quantities computed:**
  * P_tpt (`penalty_closed`);
  * P_riemann with N = 64 and N = 256;
  * P_c5t;
  * P_frozen;
  * the frozen clause exactly as consumed, ρ·x_hi·M_k;
  * Γ = g_hi + P under each of these.
* **Independent checks:**
  * P* computed exactly by closed-form integration of my own profile polynomials;
  * a Riemann **lower** sum with N = 64, as a bracket from below.

**H_K1.** The K1-only `R2_interval` is **not** in the allowed data. The tc_r1 records carry no R2_interval, and the consumption stores only H_final = H_prior ∩ H_TC. The question turns out not to matter:
* For all 136 pairs, H_final equals H_TC on both sides, so the prior enclosure never binds.
* Since lo(s) ≥ lo(ρ) = H_TC.lo ≥ H_prior.lo, we have max(H_prior.lo, lo(s)) = lo(s).
* So variant A (`H_K1 = None`) is exactly the TPT bound with the true prior cap.

Variant B uses `H_K1 := H_final` and is identical on all 136 pairs.

## 2. Reproduction gate

**136/136 pass. 0 were gated out. There are no mismatches.** In addition, `tpt.whole_cell_enclosure` (the profile evaluated at s = ρ) equals H_TC on all 136 pairs, and `tpt.lo_hi_polys` equals my independent profile polynomials coefficient for coefficient on all 136.

## 3. Results

Every check below holds on all 136 pairs unless stated otherwise.

| check | result |
|---|---|
| P_tpt = independent exact P* (I_right and I_left each equal exactly) | 136/136 |
| lower sum₆₄ ≤ P_tpt ≤ P_riemann₂₅₆ ≤ P_riemann₆₄ | 136/136. Relative gap is 2.0e-4…7.2e-4 at N = 64 and 5.1e-5…1.8e-4 at N = 256, i.e. O(1/N) |
| P_tpt ≤ P_c5t < P_frozen (TPT-D) | 136/136; `tpt.evaluate` raised 0 times |
| tpt P_frozen equals the consumed clause ρ·x_hi·M_k | 136/136, because M_k = mag(H_final) on these pairs |
| profile at e0 meets H_final (a real-data consistency probe) | 136/136 |
| profile coefficients ≥ 0, so Corollary TPT-M applies | 136/136 |

**Ratios.** Distributions over all 136 pairs:

| ratio | min | median | max |
|---|---|---|---|
| **P_tpt / P_c5t** | 0.97520 | 0.98856 | 0.99262 |
| P_tpt / P_frozen | 0.9128 | 0.9608 | 0.9743 |
| P_c5t / P_frozen | 0.9360 | 0.9720 | 0.9816 |

Per m, the P_tpt/P_c5t medians are 0.9880 (m = 1), 0.9887 (m = 2), 0.9888 (m = 3) and 0.9889 (m = 5).

**Γ changes.**
* Γ_c5t − Γ_tpt lies in [4.54e-7, 3.50e-6].
* Γ_frozen − Γ_tpt lies in [1.93e-6, 1.19e-5].
* Relative to |g_hi|, the gain over C5-T has median 0.060% and maximum 3.26%.

**Pass/fail (information only).** All 136 pairs were already closed via `chain`.

| consumer | direct clause passes (Γ < 0) |
|---|---|
| frozen | 30 |
| C5-T | 30 |
| TPT | 31 |

The one flip is **cell 41, m = 5**:

| consumer | Γ |
|---|---|
| frozen | +5.39e-6 |
| C5-T | +2.16e-8 |
| TPT | −2.10e-6 |

No pair's overall status changes.

## 4. Findings

1. **TPT is sound on this data.** It dominates C5-T everywhere, but its gain is small here: 0.7–2.5% of the penalty.
   * In this regime R'' > 0 on every cell (H_TC.lo > 0 on 136/136), so P* is always attained on the left side, through the upper profile.
   * The gain is capped by how much hi(s) varies across the cell: 1.3–4.6% of hi(ρ), and 5–10% of the enclosure width.
2. **THEOREM_TPT §0 overstates the mechanism for these cells.** It says the midpoint radius rad_r(0) = A0 f_H + 2A1 f_D + A2 f_F is "typically orders of magnitude smaller" than rad_r(ρ).
   * On all 136 real pairs, rad(0)/rad(ρ) is **0.939–0.969**. The midpoint residual dominates the TC radius, so the Taylor growth term is only about 4% of it.
   * Most of TPT's gain here comes instead from the centre-motion term ρ|Ĝ(a)|, which is 7–14% of the half-width.
   * This is a statement about the lower front (e ≈ 0.006–0.025) only. **No inference is made about the tail.** Per the quarantine, these ratios are not a calibration for cells 305–309.
3. **The signed Ĝ_r(a) is not recorded.** The cell records carry only an upper bound on |Ĝ_r(a)|.
   * So the §2 consequence formula, with its signed centre (t − e0)Ĝ_r(a), cannot be built from the committed records.
   * `tpt.py` folds s·|Ĝ| into the radius instead. That is a symmetric relaxation, and it is sound: it makes the profile monotone, so TPT-M applies.
   * As a result, THEOREM_TPT's "with Ĝ ≠ 0 use P₊" branch is never needed. §2 should state this.

## 5. Defects in `tpt.py` (reported only, not fixed)

* **T1: guard coverage gap.** The module docstring says every public entry point calls `guard_cell`. It does not.
  * `lo_hi_polys`, `rad_poly` and `whole_cell_enclosure` are public and never call the guard. I counted 0 calls on a cell-11 profile.
  * `whole_cell_enclosure` computes a whole-cell enclosure, which is a forbidden quantity class for target cells.
* **T2: the m label is not bound to the terms.**
  * The guard keys on the label `cp.m`, but the weights use `1/len(cp.terms)`, and nothing checks that the two agree.
  * A profile labelled m = 3 that carries five m = 5 terms is accepted and computes the m = 5 enclosure. This is a label-based way around the guard. I demonstrated it on cell 11 only.
  * The `cell` label is likewise not bound to the geometry (e0, ρ).
* **T3: the split point can land on the wrong side.**
  * `_crossing` returns the bisection midpoint, which can lie past the true crossing.
  * P_closed stays a sound upper bound, but it can exceed P_c5t. In a SYNTH probe with the crossing below the bisection resolution, the excess was +4.7e-42, and `evaluate()` raised a spurious "TPT-D dominance violated".
  * Returning the endpoint on the non-binding side would keep both soundness and dominance.
  * This is not triggered on real cells, because the cap never binds there.
* **T4: minor issues.**
  * `evaluate()` asserts P_closed ≤ P_riemann. That is not a theorem once a split is used, since both are only upper bounds of P*.
  * `penalty_frozen` uses mag(H) rather than the consumed M_k. The two are equal here but could differ elsewhere.
  * `_check` does not validate that H_at_a, W or H_K1 are ordered intervals.
  * Env4 is used at its whole-cell value, although Lemma TC-P allows Env4(s). That would tighten the bound; it is not an error.

## 6. Limitations

* **No ground truth on real cells.** Real-data soundness is shown only through consistency relations: the exact gate, the independent exact P*, the lower/upper bracket, and the check that the midpoint profile meets H_final. Pointwise soundness rests on Lemma TC-P and the synthetic V1 checks.
* **The cap/split code path is untested on real data.** The K1 cap never binds on these cells, so that path was exercised only at the boundary (cap = lo(ρ), no split) and in the synthetic probe.
* **Only the direct clause Γ was evaluated.** The chain recurrences (μ_k and γ_k) were not re-run, because they need L_k and data from other cells.
* **Ledger.** The driver ran twice; the second run only added the `radius_breakdown` fields. Two earlier scratch prototype runs on cells 11 and 44 were not logged when they ran, so I added them to the ledger afterwards, marked RETROACTIVE.
* **Full-namespace scan not run.** `ov_quarantine.py --scan` writes a temporary file under `ledger/`, so I did not run it. The per-file `_scan_file` check of the v3 code passed with 0 findings.
