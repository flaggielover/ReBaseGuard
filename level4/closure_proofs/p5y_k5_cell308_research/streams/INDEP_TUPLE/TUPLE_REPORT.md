# Stream F3 (INDEP_TUPLE): independent re-derivation of the TC-T profile tuple

Status: research, synthetic only. Nothing was computed for any CUSUM m = 5 tail cell. Gamma ledger contribution
0/0/0/0. Nothing staged or committed.

## Result in one paragraph

The second implementation (`tuple_independent.py`, stdlib only, written from the theorem text and frozen before
any primary code was read) agrees **exactly** with the ASSEMBLY primary on every decoy and every coverage variant.
It agrees with the tuple the primary reads off the frozen consumer, with `tptb_tail.rederive_tuple`, with the
committed decoy record, with the frozen whole-cell enclosure and W sum, and with every profile polynomial that TPT
and TPT-B integrate. That is 4204 exact checks on the 18 decoys and 10668 on 54 variants, with **no disagreement**.
So no defect was found in the primary or in this reading of the theorems. The planted mutants that preserve
rad_r(rho) but change the shape of rad_r(s) are all detected by the exact comparison. Their common-mode versions put
the same defect in the extracted tuple and in `rederive_tuple`. Those pass **every** primary gate (G-R1..G-R4, G-T1,
G-T2, G-D; status OK on 18/18), so the independent tuple is the only check that catches them.

## Files

| file | role | sha256 |
|---|---|---|
| `tuple_independent.py` | T1, the independent module (stdlib only; self-test `python3 -I -B tuple_independent.py`) | `47ae88dc…6cbc8` (frozen) |
| `freeze/FREEZE_SHA256.txt` | the freeze hash and its UTC time (2026-09-28T16:21:20Z, host clock) | — |
| `compare_tuple.py` | T2 + T3: the harness. It refuses to run if the module hash differs from the freeze | `8b356892…7f1f02` |
| `results/COMPARE_TUPLE.json` | the full per-decoy, per-variant and per-mutant record | `b506e46a…6107ae` |

Ledger (`agent = streamF3`):
* 16:13:53Z, INFRASTRUCTURE: the reading record before implementation.
* 16:21:20Z, INFRASTRUCTURE: the freeze, with sha256 and self-test.
* 16:33:19Z, SYNTHETIC_VALIDATION: the T2/T3 run.
* A closing entry for this report.

## Independence record

* **Read before the freeze.**
  * `THEOREM_TCT.md`, lines 1–131 (sections 0–4; section 5 was not read).
  * `THEOREM_TC.md`, all of it.
  * `THEOREM_TPT.md`, lines 82–137 (section 2, Lemma TC-P).
  * `ASSEMBLY/decoy_gen.py`, for the input format.
  * `tct_inputs.py`, lines 1–14, 54–57 and 85–118 only (docstring, `_src`, the emitted dict).
  * `code/c308_quarantine.py`, for the guards, `log_event` and the scan rules.
* **Read after the freeze.**
  * `tptb_tail.py`, lines 1–215 and 340–611.
  * `tpt.py`, lines 82–142 and 349–366.
  * `frozen_path_loader.py`, a grep only.
* **Never read:** `tct_rule.py`, `tc_rule.py`, `LP/p5y_k5_tail_c2_closure/code/*.py`, the F2 `INDEP` code, and any
  cell data file.
* **Before the freeze the module ran only on** its own hand fixtures, plus a parse-only smoke test on the 18 decoys
  with a dummy supply (1, 1, 1). That smoke test inspected no primary value.

## T1: what the module computes (exact `Fraction`, floats refused)

Per r in 0..4, from `meas` (TCT_INPUTS schema), `aux` (Aux3 `candidate_suprema` / `midpoint_eps`) and a given
S = (A0, A1, A2):

**Midpoint inputs (TC (P2)).**
* f_F = delta_F + eps_src[0]
* f_D = delta_D + eps_src[1]
* f_H = delta_H + eps_src[2]

**Order-3 input (TC-T (P2′)).**
* delta_G = 3k₁s_H + 3k₂s_D + k₃s_F + sigma3
* f_G = delta_G + eps_src[3]. This is the implementation convention stated in the theorem text. The bare-premise
  value `fG_theorem = delta_G` is also returned.
* |G_hat_r(a)| = 0. The centre is the interval H_at_a = H_hat_r(a), used with its sign unchanged.

**Towers (TC-T (P3′) r2).**
* Pure tower:
  * T[1,0] = 1 and T[1,n] = sup_S0[n−1].
  * T[j,0] = 1 and T[j,n] = Σ_{i=0..n} C(n,i) k_i T[j−1,n−i].
* Midpoint slot: Tm[j,3] = min(T[j,3], adoptedh(j)).
* Cell tower:
  * Tc[j,3] = min(T[j,3], adoptedh(j) + ρT[j,4]).
  * Tc[1,4] = T[1,4].
  * Tc[j,4] = min(Σ_i C(4,i) k_i Tc[j−1,4−i], T[j,4]).
* sigma3:
  * r = 0: min(sup_S0[3], cs['Sclosed:0:3'] + me['Sclosed:3']).
  * r ≥ 1: min(Σ_{i≤3} C(3,i) j_i Tm[r,3−i], cs['S:r:3'] + me['S:r:3']).
* sigma4:
  * r = 0: sup_S0[4].
  * r ≥ 1: Σ_{i≤4} C(4,i) j_i Tc[r,4−i].

**Env4 (TC-T §4).** Env4 = σ4 + 6k₂s_H + 4k₃(s_D + ρs_H) + k₄(s_F + ρs_D + ρ²s_H/2). This equals TC (P3) at
s_G = 0, which the self-test checks.

**Profiles (Lemma TC-P).** These are ascending coefficient lists in s.
* p0 = [f_F, f_D, f_H/2, f_G/6, Env4/24]
* p1 = [f_D, f_H, f_G/2, Env4/6]
* p2 = [f_H, f_G, Env4/2]
* rad_r = A0p2 + 2A1p1 + A2p0

**W term.** Σ_{1≤t<m} Σ_{r<t} (1/t − 1/m) W_(r,t−r−1).

**Profile band.** [lo(s), hi(s)] = W + Σ_r (1/m)[H_lo − rad_r(s) − s|G|, H_hi + rad_r(s) + s|G|].

**Whole-cell enclosure.** H_m is the profile band at s = ρ.

**Lemma G.** A0 = C, A1 = k₁C² and A2 = k₂C² + 2k₁²C³.

**Refusals (fail-closed).**
* Floats, negative norms, sups or residuals, and unordered centres.
* Any order-3 field of F, or `order3_fields_present` ≠ False.
* left/right that are not exactly e0 ∓ ρ.
* W-key sets other than the 10 of m = 5, and missing aux keys.
* Quarantined labels, and geometries that meet the drift band or its mirror.

**Self-test (all pass).**
* rad = A0p2 + 2A1p1 + A2p0 on a grid.
* Taylor tightness: φ = the quartic with φ⁗ = Env4 gives φ^(j)(s) = p_{2−j}(s) exactly.
* Lemma G equals the generic K1 DAG rule at s = 0.
* Env4 equals TC (P3) at s_G = 0.
* Hand-computed pure, midpoint and cell towers.
* The band is nested in s.
* 13 refusal cases.

## T2: comparison (exact, coefficient by coefficient)

| check | against | result |
|---|---|---|
| C-a | tuple extracted from the frozen consumer: fF fD fH fG Env4 abs_G H_at_a. Also the frozen `taylor_bounds` → (p0, p1, p2)(ρ), `radius` and `object_half_width` at ρ | equal, 18/18 |
| C-b | `tptb_tail.rederive_tuple`: the tuple plus sigma3, sigma4 | equal, 18/18 |
| C-c | committed decoy `per_r` and `H_exact` | equal, 18/18 |
| C-d | frozen whole-cell (lo, hi) and the primary's W sum (from the frozen `coefficients`) | equal, 18/18 |
| C-e | every `tpt.lo_hi_polys` call: 194 calls, the cell constants and each block's constants (TPT-B), lo(s) and hi(s) coefficient lists | equal, 194/194 |
| C-f | the primary's own `p_at` and `rad_at` at 7 distinct s in [0, ρ]. Degree ≤ 4, so this is polynomial identity | equal, 18/18 |
| C-L | Lemma G against the frozen `atom_constants_generic`, and S ≤ the Lemma-G supply (9 decoys with supply sources) | equal, 9/9 |

The primary returned status OK on 18/18 baseline decoys.

**Branch coverage, measured by the harness.** On the ASSEMBLY decoys the r = 0 adopted order-3 source bound
**never binds**: `Sclosed:0:3` loses to sup_S0[3] on 18/18, as the theorem notes for real data. So the
`Sclosed:0:3` / `Sclosed:3` key handling is not exercised there. The harness therefore adds three in-memory
variants per decoy:
* V_r0: the r = 0 candidate is set to sup_S0[3]/4.
* V_low: every adopted candidate is divided by 1000.
* V_high: every adopted candidate is multiplied by 1000.

The committed record is dropped for all variants. Across the 54 variants:
* All are equal (10668 checks), and the primary returns OK on 54/54.
* Both sides of every `min` bind at least once. r = 0 adopted binds 36 times; sigma3 adopted/tower binds 101/115;
  Tm3 adopted/pure 98/118; Tc3 corrected/pure 96/120; Tc4 recursion strictly below pure 75.
* The order-4 clamp never fires. That is correct, since the theorem proves it cannot (monotone recursion), so a
  defect in the clamp is both undetectable and harmless.

**Disagreements: none.** No defect was found in the primary's extraction, in its `rederive_tuple`, in `tpt.py`'s
profile construction, or in this reading of the theorems.

The agreement is three-way:
* the frozen, previously adopted consumer (C-a);
* the primary's own re-derivation (C-b);
* this module, written from the text.

A misreading of the theorem text shared by F3 and the primary would still be caught by C-a. Examples are
T[j,0] = 1, or the `+ eps_src[3]` convention.

## T3: planted mutants (through the primary's code path)

Tuple mutants act through the `mutate` hook on the extracted tuple. The polynomial mutant patches `tpt.rad_poly`.
The rederive defects patch `tptb_tail.rederive_tuple`. In the **common-mode (cm)** runs the same defect is also put
into `rederive_tuple`, and the committed `per_r` record is dropped. There are 18 decoys each.

| mutant | preserves rad_r(ρ) | independent comparison detects | primary G-R1 (ρ) passes | primary status OK |
|---|---|---|---|---|
| f_H ↑ f_G ↓ compensated | yes | 18/18 | 18 | 0 (G-R3); **cm: 18** |
| f_G ↑ f_H ↓ compensated | yes | 18/18 | 18 | 0; **cm: 18** |
| f_D → f_F compensated | yes | 18/18 | 18 | 0; **cm: 18** |
| Env4 → f_F compensated (drops Env4) | yes | 18/18 | 18 | 0; **cm: 18** |
| Env4 dropped | no | 18/18 | 0 | 0 (cm: 0, G-R1) |
| centre sign flipped | no | 18/18 | 0 | 0 (cm: 0, G-R1) |
| rad_r(s) s-linear ↔ s-quadratic shift in `tpt.rad_poly` (tuple untouched) | yes | 18/18 (C-e) | 18 | 0 (G-T1) |
| rederive: sigma4 from the pure tower | — | 11/11 value-changing | — | — |
| rederive: f_G without eps_src[3] | — | 18/18 | — | — |
| rederive: sigma4 on the midpoint tower (review-N1 class, unsound) | — | 11/11 value-changing | — | — |
| rederive: sigma3 from the cell tower | — | 3/3 value-changing | — | — |

For every rederive defect, detection happens exactly on the decoys where the defect changes a value, and nowhere
else.

**Key finding.** A mis-shaped profile that reproduces the whole-cell radius at s = ρ passes G-R1. If the same shape
error sits in the extraction and in `rederive_tuple`, it passes every primary gate and the transport runs on it. The
exact comparison with this independent tuple detects all four such mutants on 18/18 decoys.

The `tpt.rad_poly` shape mutant is caught by the primary's own G-T1 (its independent integrator uses its own
`rad_at`). It is also caught at the coefficient level by C-e.

## T4: shared code surface

**Imports.** `tuple_independent.py` imports only the standard library: `fractions`, `math.comb`, `json`,
`hashlib`, and `random` / `copy` in the self-test. It shares **no** import with the primary.

**AST comparison.** Measured against `rederive_tuple`, `p_at`, `rad_at`, `band_at` and `whole_cell_from_tuple`:
* **Common string constants:** input-schema keys only (`delta_F`, `eps_src`, `sup_S0`, `candidate_suprema`,
  `midpoint_eps`, `Sclosed:0:3`, `Sclosed:3`, the f-string templates `S:{}:3` and `h:{}:3`) and the output field
  names (`fF` … `Env4`, `abs_G`, `sigma3`, `sigma4`).
* **Common identifiers:** theorem notation (sF, sD, sH, rho, k, p0–p2) and the variable names cs, me, jn, s0. Those
  names also appear in `decoy_gen.py`, which F3 read for the input format.
* **Identical lines:** 4 of the primary's 68 in these functions, all trivial (`for n in range(5):`,
  `for n in range(1, 5):`, `return lo, hi`, and one list comprehension in the self-test that parses the k norms).

Verdict: **boilerplate only.** The quarantine guard in the module restates the band and the quarantined labels from
the config. It is governance boilerplate, and the scan marks it as literal-ok.

Shared **inputs** (not code):
* The decoy bundles, and the cell supply S. For the 9 source-supplied decoys, S comes from the frozen
  `c2_d5_forecast.combine` over Lemma G and Lemma Dv′. F3 checks only the Lemma-G component and S ≤ G.
* The block triples.

The tuple itself does not depend on S. The rad and lo/hi polynomials are linear in S and are compared at the same S.

## Open issues

1. **Supply not independently re-derived.** The Lemma Dv′ part of S (theorem AD, `atom_constants_r2`) and the
   frozen `combine` rule are outside F3's reading list. Only the Lemma-G component is checked independently. The
   primary cross-checks Dv′ against `C2._atom_independent`, and that is not an F3 check.
2. **Decoy coverage gap.** The r = 0 adopted order-3 bound never binds on the ASSEMBLY decoy set. The gap is
   covered here only by the variants. Consider adding such a regime to `decoy_gen.py`, or making the V_r0 variant
   part of the ASSEMBLY validation.
3. **Recommendation.** Wire the frozen `tuple_independent.tuple_tct` (pinned by sha256) into any formal builder as
   an extra coefficient gate next to G-R3. Only an independent tuple closes the common-mode, rad(ρ)-preserving
   blind spot of the primary's own gates.
4. **Observation, not a defect, and not quantified.** The theorem's midpoint and cell order-3 slots take the
   *pure* T[j,3]. A Leibniz recursion over the already-refined slots of h_{j−1} (Σ C(3,i) k_i Tm[j−1,3−i], and the
   same for Tc) is also pointwise valid and would add a sound third term to those minima. This is outside the
   theorem as frozen and is left to a theory stream. No number was computed for it.
5. **Block triples.** The harness checks the TPT-B polynomials for each block's given constants. Whether those
   constants are valid supplies is not a tuple question and is not checked here.
