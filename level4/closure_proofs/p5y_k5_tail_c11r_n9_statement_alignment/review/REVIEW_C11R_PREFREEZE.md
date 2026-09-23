# C11R pre-freeze review

- **Reviewer:** independent pre-freeze reviewer. Fresh context, with no part in C2-C11 or C11R.
- **Reviewed:** branch `p5y-k5-tail-c11r-n9-statement-alignment`. The review was requested at `49b17ab4`. `38f59993` was then committed during the review, adding `code/c11r_qualify.py` and `evidence/errata/C11R_ERRATA.json` (see item 14).
- **Namespace:** `level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment/`
- **Method:** I read the source. I recomputed numbers with the campaign's own modules, imported in a scratch directory. No producer was run. Scratch scripts are in the session scratchpad under `rev/`: `indep.py`, `scan.py`, `m1.py` to `m6.py`.
- **Constraints:** `PYTHONINTMAXSTRDIGITS=0`. numpy, scipy, flint, mpmath, sympy and gmpy2 were confirmed absent (Python 3.14.5).

**Status of this file: COMPLETE.** Every item 1 to 14 was reached. Three of the four sub-checks first listed as not reached have since been closed. One remains: V10 at 32 panels, which ran out of memory; see "Not reached".

---

## Summary

**The campaign should not freeze in its current form.** The statement analysis (N9 reading, six-constant table, dependency finding, atom convention, Abar/tau/C_T mapping) is correct; I verified it independently. The block-uniform drift layer is mathematically sound, including `kernel_box_upper_iv` and its atom-window intersection.

The execution and comparison layers have four blocking defects:

1. **CRITICAL: the frozen target runs cannot certify.**
   - Both candidates that `c11r_runs.py` will send give a negative `L_lo` on ordinary boxes of the depth-4 cover, at 16 panels. I computed this with the campaign's own `kernel_box_upper_iv`.
   - `supersolution_margin_iv` takes the minimum over boxes, so both runs will return `certified=False`.
   - The campaign as frozen will therefore produce **zero** independent values, not three.
   - The pointwise screen cannot see this.
2. **CRITICAL: the statement-equivalence comparator is never applied to what was actually proved.**
   - `c11r_compare.py` builds the "independent proposition" by copying the original's proposition and overwriting only the drift domain, which it then sets back to the original's value.
   - `EQ.check` therefore always returns `EQUIVALENT`, whatever `c11r_runs.py` emits.
   - The same module hard-codes result text that my computation shows would be false: "agreement is established with statements equal to the original's", "No target is INVALID".
   - This is C11's result-in-the-gate defect, moved from the gate into the comparison producer.
3. **CRITICAL: the mutation suite cannot give a valid verdict once `runs/` exists.**
   - M26 reads a key (`sealed_sha256`) that the runs producer never writes. It is therefore guaranteed to report SURVIVED.
   - M28 reads `depth` from a sub-dict (`certification`) that the producer never writes. It can therefore never fire.
   - M03 is reported DETECTED while the property it names is violated: `c11r_screen.py` reads the original's certified constants from the table.
4. **MAJOR: the candidate choice was made with the original values on screen, and it crosses the frozen factor-2 threshold.**
   - Erratum E2 discloses the change from `12 - 3/2 m` to `8 - m`. It asserts the change is "NOT fitting to the original's value".
   - That assertion is not demonstrated. `c11r_screen.py:112-115` prints the original Abar, tau and C_T in the same run that produced the screen margins.
   - The change moves both C_T and tau from INSUFFICIENT to AGREES under the frozen rule.

---

## Item-by-item

### 1. N9 interpretation: **C11R is right.**

**Sources I read myself:**

- `p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md:501`: "a **second, independently written certifier** reproducing the six operator constants for cell 306 (closing N9)".
- The disposition file lives at `p5y_k5_tail_c2_closure/OPEN_NOTES_DISPOSITION_C2.md`. The path given in my brief, under `evidence/adjudication/`, does not exist.
- Its lines 78-81 define N9 as "the Arb/FLINT supersolutions remain the residual trust surface ... this is still **one implementation**. A second, independently written certifier is the real answer".

**Finding:**

- The target cell is 306 and the constant count is six. Both come from the adjudicator's closure wording, and C11R reproduces that wording exactly (`C11R_N9_TABLE.json: N9_wording`).
- One nuance C11R does not record (MINOR): the disposition file frames the trust surface as the *supersolutions*. Only three of the six constants (C_T, tau, Abar) come from supersolutions; D_lo, D1 and D2 come from `certify_cell`, which propagates residuals. The adjudicator's "six" governs closure, so C11R's reading is the correct one. It should still say that the six-constant requirement is wider than the surface the disposition file names.

### 2. The six-constant table: **every field verified. The cell-307 claim is correct.**

**Values and drift block.** Checked against `p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json`, block `cell == 306`:

- All six values are bit-identical to the registry block record: Abar `8908589238530053/1125899906842624`, tau `5820699638017325/1125899906842624`, and the long-form C_T, D1, D2 and D_lo.
- `e_lo = 680769/400000`, `e_hi = 17885921/10000000`, `e0 = 17452573/10000000`, `rho = 108337/2500000`, and `e0 ± rho` reproduces `[e_lo, e_hi]` exactly.
- The nine sub-block bounds are contiguous and tile the block exactly.

**Aggregation.** I recomputed from `sub_rows`:

- `max` over the nine sub-rows reproduces the block value exactly for C_T, tau, D1 and D2. `min` does the same for D_lo.
- In every case the extremum is attained at sub-block 0.
- `taboo_alpha = 6/5` in all nine sub-rows. `arl_alpha = 5/4`.

**Artifact hashes.**

- The nine `taboo_artifact_sha256` values match the table's C_T and tau lists.
- The nine `denominator_artifact_sha256` values match the D_lo, D1 and D2 lists.
- The one `arl_artifact_sha256` (`bdf05e57...`) matches Abar.

**Producer, mode, kernel and quantity.** Checked against `p5y_k5_perron_deflated_resolvent/code/taboo_certify.py`:

- `certify_block(..., full=False)` emits `C_T = upper(wmax)` and `tau = upper(wa)` with `wa = w(0,0)` (lines 200-239). Its statement is "w >= 1 + Khat_e w ... ||Ghat_e|| <= C_T and (Ghat_e 1)(a) <= tau".
- `full=True` uses `Ops.khat(..., full=True)`, which returns `_kernel_polynomials` with the origin piece kept, i.e. K_e. Its `tau` field is Abar.
- `certify_cell` emits D_lo, D1 and D2 (lines 284-349).
- The table's attributions are all correct. The table also correctly does not use the `C_T` field that `full=True` artifacts emit; that is the sup of a different w.

**The cell-307 claim.** The registry's cell 307 has `e_lo = 17885921/10000000` and `e_hi = 1882413/1000000`, with **10** sub-blocks. The quoted `[1.7885921, 1.882413]` is therefore cell 307's block, and its lower endpoint equals cell 306's `e_hi` exactly. C11R's resolution is correct: the instruction names cell 306 throughout and the registry it points at is unambiguous. The discrepancy is recorded (table `CAMPAIGN_INSTRUCTION_DISCREPANCY`, erratum E3), not silently resolved.

**Dependency granularity (MINOR, verified).** The table records `depends_on: [C_T, tau]` at block level, with C_T and tau as the *max* over sub-blocks. The actual dependency is per sub-block:

- I located all nine denominator artifacts by content hash: `p5y_k5_tail_c2_closure/**/taboo_cell_306_00.json` through `_08.json`, whose sha256 values match the registry's `denominator_artifact_sha256`.
- Each one's `tau` and `C_T` inputs equal *its own* sub-block's taboo values, and each one's `e0 ± rho` equals that sub-block's bounds. This holds 9/9.

So an independent D-constant for sub-block *i* must be conditioned on an independent C_T and tau *for sub-block i*, or on a single block-uniform pair. `prop()` is increasing in both, so the block-uniform pair is also sound. The table should state the per-sub-block dependency.

### 3. The dependency claim: **correct, verified from source. The consequence is drawn but not enforced.**

**What the source shows.** `certify_cell(e0, rho, tau, C, payloads, ...)` (line 284) takes tau and C_T as *inputs*:

- `T, Cc = exact(tau), exact(C)` (line 319).
- `prop()` builds every propagated error from `Cc * lam` and `T * lam` (lines 321-327).
- The emitted statement is "(given ||Ghat_e|| <= C_T and (Ghat_e 1)(a) <= tau on the same set)" (line 349).

So D_lo, D1 and D2 are conditional on C_T and tau. An independent certifier that fed in the original's C_T and tau would be consuming the original's outputs. C11R's conclusion is correct.

**Where it falls short.** The consequence is recorded in prose (`DEPENDENCY_FINDING`) but encoded nowhere that could fail. `c11r_equiv.EXACT_FIELDS` has no `depends_on` or provenance field (see item 4).

**What else D would need.** In the original, `certify_cell` also consumes:

- `opnorms.kernel_norm(1..3)`
- `opnorms.sup_source_derivative`
- the `closed_h1` truncation allowances

An independent D needs independent versions of all of these, not only of C_T and tau. C11R's `what_would_be_required` list in `c11r_runs.py:115-122` does name the kernel norms.

### 4. Statement-equivalence comparator: **self-test real, production path tautological (CRITICAL), provenance unguarded (MAJOR).**

**The self-test is real.** `c11r_equiv.self_test` mutates metadata fields and executes `check` on them. Cross-substituting D1/D2, D_lo/D1, tau/Abar and tau/C_T is rejected. The six quantity labels are pairwise distinct, so no substitution among the six passes. That part is sound.

**CRITICAL: the production path cannot fail.** `c11r_compare.py:103-105`:

```python
indep_prop = dict(orig_props[name])
indep_prop["drift_domain"] = block_dom        # what this campaign actually proved over
eq = EQ.check(name, orig_props[name], indep_prop)
```

- `block_dom` is `[e_lo_float, e_hi_float]`, which is exactly `orig_props[name]["drift_domain"]`. The "independent" proposition is therefore the original with nothing changed, and `EQ.check` returns `EQUIVALENT` on every call.
- None of the runs artifact's own fields is read: not per-candidate `kernel` or `statement`, and not per-target `from` or `quantity`.
- A mapping error in `c11r_runs.py` would pass as EQUIVALENT: tau taken from the `K_e` candidate, C_T taken as `w_at_atom`, or the K_e candidate run with `atom_removed=True`.
- G2 requires that "the independent proposition matches the original on kernel, quantity, state, direction and bounded object". In the real comparison nothing is matched, so G2 is met only by its self-test.

**MAJOR: provenance is not a compared field.** `depends_on` is not in `EXACT_FIELDS`. Consider an "independent" D1 computed by feeding in the original's C_T and tau: it would match on kernel, quantity, state, direction, bounds and domain, and be classified EQUIVALENT. That is exactly the independence violation the table's `DEPENDENCY_FINDING` identifies, and the comparator is the place meant to catch it.

**MINOR.**

- Domains are compared as binary floats (`F(1.7019225)`), not as the exact rationals G3 requires. `F(1.7019225) != 680769/400000`, so an independent proposition that stated its domain exactly could be misclassified as SUBSET or INCOMPARABLE.
- `bounds` is compared as a free-text string. That is safe (it can only produce false negatives) but brittle.

### 5. Drift uniformity, the central scientific claim: **sound.**

Each piece was checked analytically line by line. Scalar collapse and containment were recomputed.

**`Phi_iv` (idrift:85-87).** Phi is increasing, so `[Phi(lo).lo, Phi(hi).hi]` encloses `Phi(A)` for every `A` in `[lo, hi]`. Correct.

**`_phi_pair` (136-146).**

- phi is even and unimodal with its maximum at 0. On any interval its infimum is at an endpoint, so taking the minimum of the endpoint lower bounds is correct.
- Its supremum is `phi(0)` when `0` is in `[x_lo, x_hi]`, and the larger endpoint otherwise.
- The straddle branch uses `G.phi(0).hi`. Correct.

**`_monomial_pair` (149-157).**

- For odd `n`, `u^n` is monotone, so the endpoints are correct.
- For even `n` not straddling 0, `u^n` is monotone on the interval, so the endpoints are correct.
- For even `n` straddling 0, the infimum is 0 and the supremum is `max(a, b)`. The code sets `lo = 0` and keeps `hi = max(a, b)`. Correct.
- The `n = 0` case returns exactly `(1, 1)`.

**`_moments_pair` (106-133).**

- `M_0 = Phi(B) - Phi(A)` and `M_1 = phi(A) - phi(B)` are correct interval enclosures.
- The recursion `M_j = (j-1) M_{j-2} + A^{j-1} phi(A) - B^{j-1} phi(B)` treats `A` in the monomial, `A` in `phi`, and `(A, B)` inside `M_{j-2}` as independent. That is the standard interval dependency effect. It widens the enclosure but keeps it valid for every fixed `(A, B)`.

**`shifted_moments_iv` (160-177).** Both places the drift enters are handled.

- **Limits.** `Ms = _moments_pair(a+E.lo, a+E.hi, b+E.lo, b+E.hi, j)`: `A = a + e` ranges over `[a+e_lo, a+e_hi]` and `B` likewise. Correct.
- **Coefficients.** `(-e)^(j-i)` is enclosed by `_monomial_pair(-E.hi, -E.lo, j-i)`, which is the interval `-E`, the correct sign. `comb(j, i) >= 0`, so `Iv(c*plo, c*phi_)` is correctly ordered. The width is the exact range of `(-e)^(j-i)` over the block.
- **Dependency.** The same `e` appears in the limits and the coefficients, and they are enclosed independently. The result is wider but valid for each `e`.

**What "simultaneously for every e" means, and why it suffices.** For each `e` in `E`, the true value lies in the one computed interval. The certificate checks `w.lo - 1 - (K w).hi > 0` with `(K w).hi` bounding `(K_e w)` for every such `e`. That is exactly "`w >= 1 + K_e w` for every `e` in `E`". No grid and no endpoint theorem are needed. The extra facts are the three stated in the module docstring, plus two inherited ones:

- C7's outward-rounded `Iv` and its rigorous `Phi`/`phi` series;
- the E5 vacuity guard.

**`kernel_box_upper_iv` (275-316): a valid upper bound for every state in the box and every `e` in the block.**

- **Window.** For `p` in `[a, b]` and `m` in `[c, d]`, the alarm-free window `[m-C, C-p]` lies inside `[c-C, C-a]`. Correct.
- **u-range.** In `u = z + e` the window lies inside `[lo_z + e_lo, hi_z + e_hi]` for every `e`. Correct.
- **z-range per panel.** For `u` in `[u0, u1]` and `e` in `[e_lo, e_hi]`, `z = u - e` lies in `[u0 - e_hi, u1 - e_lo]`. Correct.
- **Image-state box.**
  - `p' = max(0, p + z - K)` is nondecreasing in `p` and `z`, so `p'` lies in `[max(0, a + z_lo - K), max(0, b + z_hi - K)]`.
  - `m' = max(0, m - z - K)` is nondecreasing in `m` and nonincreasing in `z`, so `m'` lies in `[max(0, c - z_hi - K), max(0, d - z_lo - K)]`.
  - The code matches both.
- **Mass.** `Phi(u1) - Phi(u0)` is taken at point arguments, so it is exact and not widened by the drift.
- **Upper-bound argument.** Each panel contributes `max(w.hi, 0) * mass.hi`. That is at least `w * phi` integrated over the panel's intersection with the true window. Every panel's contribution is non-negative. Summing panels therefore bounds the integral over the true window, for every state and every `e`.
- **The O(W) end over-count is safe, and does not depend on `w >= 0`.** The clamp `hi = max(wv.hi, 0)` already makes every added panel non-negative. The docstring's "With w >= 0 enforced separately, extra mass can only raise the bound" names an unnecessary condition (MINOR, documentation only). `w >= 0` *is* enforced separately (`certified` requires `w_min_lower_bound >= 0`), which the supersolution lemma needs.

**The atom-window intersection (304-307): correct and conservative.**

- The atom window at state `(p, m)` is `[m - K, K - p]`. Over the box, the intersection is `[max over m of (m - K), min over p of (K - p)] = [d - K, K - b]`. This is `at_lo, at_hi`, and it is non-empty iff `b + d < 2K = 1`.
- A panel is skipped only if its widest z-range `[u0 - e_hi, u1 - e_lo]` lies inside the intersection. It then lies inside every state's atom window for every `e`, so all of its mass belongs to the removed piece.
- The kept panels cover the true window minus the atom. So the sum still bounds `Khat_e w = ∫ over (W \ atom) of w phi`.
- A panel only partly inside the atom window is kept whole. That over-estimates, which is the safe direction.
- In practice the skip rarely fires: a panel of width `step + W >= 0.0867` must fit inside a window of width `1 - b - d`, so only boxes near the origin can skip anything. It is sound but nearly inert. This contributes to item 13(a).

**Scalar collapse (V6), reproduced beyond the campaign's own set (`m2.py`):**

- **Weights and states.** Three weights: `m_only`, `mixed`, and a new degree-2 weight `{(0,0): 7, (1,1): -1/3, (0,2): 1/7}` with a `p*m` cross term. Five states: `(0,0)`, `(3,1)`, `(1/4,1/4)`, `(23/5,0)`, `(0,5)`.
- **Boxes.** Four, one of them `(0, 5/4, 3, 4)`, which is not in the campaign's set.
- **Result.** `kernel_apply`, `alarm_prob` and `kernel_box_upper` at 12 panels all match. **0 mismatches** in `(lo, hi)` across 15 kernel, 5 alarm and 12 box comparisons.

**Block containment and widening.** At every probed `e` the block enclosure contained the scalar enclosure (V7 logic). The block enclosure is strictly wider than the point enclosure (M16 logic).

**V10 (tightening with panels).**

- At 8, 16 and 32 panels my reproduction was killed by the OS (exit 137, memory: exact-rational denominators grow with panel count). **Not reproduced.**
- Analytically: the u-partition at 16 panels refines the one at 8 (same u-range, uniform steps), and a sub-panel's z-range lies inside its parent's. So the image box shrinks, `wv.hi` does not increase (interval evaluation is monotone under inclusion), and the masses add. Monotone tightening therefore holds by construction for dyadic refinements.

**Verdict on item 5:** the block-uniform layer is rigorous as claimed. This is the campaign's strongest part.

### 6. K_e vs Khat_e and the atom convention: **same atom as the original. Decomposition verified.**

**The original's atom** (`rebaseguard-proof/src/rebaseguard_certify/residual.py`):

- `_kernel_polynomials` (lines 144-173) builds a low branch `down[ell, beta] + origin[beta, alpha] + up[alpha, upper]` and a high branch `down[ell, alpha] + both[alpha, beta] + up[beta, upper]`, with `beta = m - 1/2` and `alpha = 1/2 - p`.
- `_substitute_candidate(..., "origin")` (lines 90-93) drops every term with `i > 0` or `j > 0`. The origin piece is therefore `w(0,0) * ∫_beta^alpha phi(z + e) dz`.
- `Ops.khat` (taboo_certify:148-155) subtracts that piece from the low branch only. The high branch applies when `alpha < beta` and has no atom.

**C11R's atom.** `_pieces` takes the window `[m - K, K - p]`, clamped to `[m - C, C - p]`. On R the clamp is a no-op: `beta > ell` and `alpha < up` always hold, and `beta < up` and `alpha > ell` hold iff `p + m < 6`, which is true on R. So this is the same atom and the same normalisation.

**The float proposal.** `float_taboo_kernels`'s `continue` branch removes the same `[beta, alpha]` window. It is a float proposal only, not the certified surface.

**Frozen model constants** (`p5y_k1_cover_ledger_implementation/code/cusum_layer1.py:39-41`): `K_FROZEN = 0.5`, `H_FROZEN = 5.0`, `C_CUSUM = 11/2`. They match C11/C11R. The drift sign `phi(z + e)`, the window `[m - C, C - p]` and the next states `max(0, p + z - K)`, `max(0, m - z - K)` match the original's `float_taboo_kernels` (lines 92-104).

**Numerical decomposition (`m1.py`).** Three weights (`1`, `99/10 - 3/2 m`, and `4 + p/5 - m/2`) at six states (`(0,0)`, `(1/4,1/4)`, `(3/10,1/5)`, `(1/2,1/2)`, `(2,2)`, `(0,9/10)`), over the whole cell-306 block:

- `Khat_e + atom` equals `K_e` to every printed digit in all 18 cases.
- The atom window is present exactly when `p + m < 1`.
- Example: `w = 99/10 - 3/2 m` at `(0,0)` gives `K_e` in `[7.66977, 8.24030]` and atom `≈ 0.84085`.

### 7. Abar vs tau, and C_T and tau from one certificate: **mapping correct.**

In the original, one `certify_block(full=False)` call emits both `C_T = upper(wmax)` and `tau = upper(wa)` for the same `w` (line 233). Lemma T gives `||Ghat_e|| <= sup w` and `(Ghat_e 1)(a) <= w(a)` from the one inequality `w >= 1 + Khat_e w`. So C_T and tau legitimately come from one certificate, and the registry's nine taboo artifacts serve both.

Abar is the `tau` field of the separate `full=True` certificate. C11R's `c11r_runs.py:95-110` mapping (Abar from the K_e run at the atom; tau and C_T from the same Khat_e run) is correct, if the comparator ever looked at it (item 4).

### 8. Independence: **verified clean.**

**Scope of the scan (`indep.py`).** An AST walk of all 11 modules in `code/`, plus the imported independent line: `c11_certifier`, `c11_common`, `c7_gaussian`.

**Result:**

- No import of `taboo_certify`, `resolvent_certificate`, `opnorms`, `ra_certifier`, `fast_range`, `intervals`, `rebaseguard_certify`, `rung3_engine` or `spec`.
- No import of numpy, flint, scipy, mpmath, sympy or gmpy2.
- `c7_gaussian` imports only `fractions`.

**The C11/C7 reuse** is legitimate reuse of the programme's independent line, not the original's graph. Its consequence is that C11R's independence is exactly C11's, and every shared primitive is a single point of failure for both campaigns (item 13(d)).

**MINOR.** M01 scans only *direct* imports, so it would miss a forbidden import added to `c11_certifier` later. I followed the transitive edge myself and it is clean today.

### 9. The prospective gate: **no result language in the gate. Result-dependence sits in the code. Some predicates cannot fail on substance.**

**Scans of the final emitted `config/N9R_GATE_C11R.json`,** including its `result_language_scan` block, which the producer adds *after* scanning:

- The campaign's 17 patterns give **0 hits**.
- My broader 20-pattern scan (`scan.py`: fail/pass, cannot, INVALID, INSUFFICIENT, fewer, outcome, and others) hits only:
  - enumeration names (`INSUFFICIENT`, `INVALID`, `AGREEMENT_INSUFFICIENT`, `EXECUTION_INVALID`);
  - the predecessor fact `C11_verdict: EXECUTION_INVALID`;
  - G12's "the detector can fail";
  - "fewer than the six constants".
- None asserts an outcome for C11R. **The gate text is clean.**

**The problem is outside the gate text (MAJOR). Only one verdict is reachable from `c11r_compare.py` as written:**

- **INVALID and EXECUTION_INVALID.** `n_invalid` is always 0 (item 4), so the statement-mismatch route to EXECUTION_INVALID is closed.
- **DISAGREES.** `classify()` has no `DISAGREES` return at all, so `SCIENTIFIC_DISAGREEMENT` cannot be reached. The file concedes `reachable_this_campaign: False`, but also says "The branch is implemented and exercised by a negative control". That is false: the control plants `D_lo / 4` and checks for `INSUFFICIENT`, and `classify` contains no DISAGREES branch to exercise.
- **N9_CLOSED.** D_lo, D1 and D2 are hard-coded `value: None` in `c11r_runs.py:111-123`, so `n_ok <= 3 < 6`.
- **What remains.** `AGREEMENT_INSUFFICIENT` is the only verdict reachable, apart from the REFUSE exits.
- **Pre-written result text.** `verdict_derivation` and `IMPORTANT_READING` (lines 161-172) state before any run that "agreement is established with statements equal to the original's" and "No target is INVALID and none DISAGREES". This is the C11 defect class ("the criterion C11 must and does fail") moved into a module the scanner never reads. Given item 13(a), the first sentence would be false if emitted.

**Predicate quality (MODERATE):**

- G11 ("outcomes are recorded"), G12 ("classified by a detector that carries a negative control") and G13 ("recorded") are process predicates. They are satisfied by recording a *failing* V6, a *surviving* mutant, or a failed qualification.
- G8 is effectively unfalsifiable: a "recorded absence of any independent statement" satisfies it for every constant.
- None of these smuggles in an outcome, but they do not constrain one either. The verdict rests entirely on `c11r_compare.py`, which has the defects above.

**MINOR.** `target.substitutions_forbidden` contains "fewer than the six constants", while G8 permits recorded absences. These are consistent only if the forbidden substitution means "fewer than six cannot close N9". The gate should say so.

### 10. The cheap refutation screen: **a valid necessary condition, correctly labelled. Both thresholds reproduced. It gives no information about certifiability at the frozen depth.**

**Validity.** At a single state `x`, the kernel is enclosed over the whole block with no box bound. If `L(x).hi < 0`, then for every `e` in the block `w(x) < 1 + (K_e w)(x)`, so no supersolution certificate exists at any depth. The screened states satisfy the same R specification as `box_meets_R`. `ELIGIBLE_FOR_CERTIFICATION` is described as "ELIGIBILITY, not certification". Correct.

**Thresholds.**

| | K_e | Khat_e |
|---|---|---|
| Binding state | `(0,0)`, at `e_lo` | `(15/14, 0)` |
| Float check (`m3.py`) | `1/h = 13715.2826` | `13715.2002` |
| Exact recomputation with `alarm_prob_iv` / `atom_contribution_iv` | `13715.282580752` | `13715.234997913` |
| Screen evidence | `13715.282580752373` | `13715.234997913423` |

The exact recomputation matches the evidence exactly, and the float check agrees to 6-7 significant figures. The exact values are slightly larger than the float ones, which is the correct direction for a rigorous lower bound on the escape probability.

**What the screen does not tell you (MAJOR):**

- The Khat_e screen binds at `(0, 15/14)`, where `p + m > 1` and the atom is absent. Its binding value is identical to K_e's (`+1.04299` for `12 - 3/2 m` under both kernels). The Khat screen does not exercise atom removal where it binds.
- ELIGIBLE says nothing about whether the depth-4 box bound can certify; item 13(a) shows it cannot.
- `c11r_screen.py:112-115` loads the original's Abar, tau and C_T from the table and prints them in the same process as the candidate margins. This bears on item 13(c) and erratum E2.

### 11. Mutations: **three detectors defective. UNDETERMINED is not silently a pass in this module, but it is in the new qualifier.**

**M26 (CRITICAL, guaranteed false SURVIVED).** The detector tests `bool(runs.get("sealed_sha256"))` (`c11r_mutations.py:210`). `c11r_runs.py` writes `SEALED_BEFORE_COMPARISON` and, through `write_evidence`, `sha256`. It never writes `sealed_sha256`. Once `runs/` exists, M26 reports SURVIVED and `MUTATION_CLASS = REFUSE`. The only ways forward are a post-hoc detector edit after target results exist, or a verdict blocked by a detector bug.

**M28 (MAJOR, tautological).**

- `spent = {k for k, v in runs["candidates"].items() if "depth" in v.get("certification", {})}` (lines 232-233). `c11r_runs.py:71-87` writes `depth` at the top level of each candidate and has no `certification` key. So `spent` is always empty and the test `not (refuted & spent)` is always true.
- Independently, `refuted` is empty, so the detector has nothing to catch. Its own control text concedes this.
- If the module were re-run now, with the screen present and runs absent, the code path would yield DETECTED, which is the "passes because its input is missing" defect the module docstring forbids.

**The committed mutation evidence is stale and reports REFUSE (MAJOR).** `evidence/mutations/C11R_MUTATIONS.json`, committed in `49b17ab4` alongside the frozen gate, records:

- `MUTATION_CLASS = "REFUSE"` and `survivors = ["M29"]`;
- M29 SURVIVED with "scalar collapse is bit-for-bit: **9 mismatches**";
- M28 UNDETERMINED with "**no screen artifact exists yet**".

The committed `C11R_VALIDATION.json` says V6 PASS with **0** mismatches, and the committed `C11R_SCREEN.json` exists. The committed evidence set is therefore internally inconsistent: the mutation run consumed an earlier validation artifact (with 9 V6 mismatches) and ran before the screen, and it was never regenerated. File mtimes agree:

| File | mtime |
|---|---|
| `C11R_MUTATIONS.json` | 03:10 |
| `C11R_VALIDATION.json` | 03:11 |
| `c11r_idrift.py` | 03:13:14 |
| `C11R_SCREEN.json` | 03:26 |

Consequences:

- The committed validation artifact was produced by an *earlier* `c11r_idrift.py` than the committed one.
- None of the validation, mutation or screen artifacts records the producer or code hash it was generated from, so this cannot be established from the evidence itself.
- My own V6 re-run on the committed code passes (item 12). The code is therefore fine in substance, but the evidence was not produced by it.
- The 9-mismatch validation that M29 read was never committed, so "9" has no committed support.
- The brief handed to me described M26 and M28 as UNDETERMINED "because the runs artifact does not exist yet". That is accurate for M26 only. M28's recorded reason is the absent *screen*, and the brief omits M29 SURVIVED and the committed class REFUSE. The campaign did not notice that it froze its gate beside a REFUSE mutation class.

**M03 (MAJOR, mis-scoped).**

- The detector is named "reading the original's certified constants during construction". It only fires on the literal `"REGISTRY_C2.json"` inside a call's AST.
- `c11r_screen.py` reads `tbl["constants"][k]["value_float"]`, the same certified constants, copied into `C11R_N9_TABLE.json`. The detector is reported DETECTED while the property it names is violated.

**M29 (MODERATE).** Its negative control is a transcribed historical claim ("the pre-fix implementation produced 28 mismatches"). It is not executed, and the number has no committed support; this is the C2 Finding J-1 class. V6, and hence M29, covers only `atom_removed=False`.

**Weaker detectors (MINOR).**

- M16's control ("a degenerate block reproduces the point exactly") is not executed inside M16.
- M18 and M23 rest partly on substring or presence checks of gate text.
- M17, M18, M22 and M25 exercise the comparator on planted metadata. They are real tests of the comparator, which is never used on real data (item 4).

**Detectors that are sound.** M19, M24 and M27 carry executed negative controls. M01 and M02 are sound (see item 8 for M01's direct-only scope).

**UNDETERMINED handling.** `MUTATION_CLASS` is `INCOMPLETE` when anything is undetermined, not `PASS`. That is correct in this module. The new, not-yet-run `c11r_qualify.py` Q7 tests only `not mut["survivors"]`, which **accepts INCOMPLETE** (MODERATE).

### 12. Validation, V6 "scalar collapse bit-for-bit": **reproduced. Bit-equality is the right regression test but narrower than the campaign's framing.**

**Reproduction.** My run is in item 5: 3 weights × 5 states for the kernel, 5 states for the alarm probability, 3 weights × 4 boxes, and **0 mismatches**. This exceeds the requested "two weights, two states". Bit-equality is stronger than containment: the block enclosure could be sound and still widen silently, and containment would not catch that.

**What it hides:**

- **(a)** It exercises only `atom_removed=False`. C11 has no scalar Khat_e, so V6 is silent on the atom path, which is covered instead by V4, V5 and M24. I reproduced the decomposition independently (item 6).
- **(b)** It shows C11R equals C11. It cannot detect an error *shared* with C11 (item 13(d)). It validates the interval extension, not the mathematics.
- **(c)** It tests collapse at a degenerate block. Behaviour at a non-degenerate block rests on the analytic argument in item 5 and on V7's four probes.

### 13. Things C11R has not noticed

**(a) CRITICAL: the frozen runs will not certify.**

Using `c11r_idrift.kernel_box_upper_iv` and `c11_certifier.poly_eval_iv` exactly as `supersolution_margin_iv` does (`m5.py`, `m6.py`), at 16 panels on boxes of the depth-4 cover:

| Candidate (`c11r_runs.CANDIDATES`) | Box `(a, b, c, d)` | `w.lo` | box bound `(K w).hi` | `L_lo` |
|---|---|---|---|---|
| `K_e  w=12-3/2m` | `(0, 5/16, 0, 5/16)` | 11.53125 | 10.54652 | **−0.01527** |
| `K_e  w=12-3/2m` | `(0, 5/16, 15/16, 5/4)` | 10.12500 | 9.23584 | **−0.11084** |
| `K_e  w=12-3/2m` | `(5/2, 45/16, 0, 5/16)` | 11.53125 | 10.45101 | +0.08024 |
| `Khat w=8-1m` | `(0, 5/16, 0, 5/16)` | 7.68750 | 7.03101 | **−0.34351** |
| `Khat w=8-1m` | `(0, 5/16, 15/16, 5/4)` | 6.75000 | 6.15723 | **−0.40723** |
| `Khat w=8-1m` | `(5/2, 45/16, 0, 5/16)` | 7.68750 | 6.96734 | **−0.27984** |

- All three boxes pass `box_meets_R` and belong to `X.cover(4)`. `margin_lower_bound` is a minimum over boxes, so one negative box settles it: **both** planned runs return `certified=False`, and no independent value is produced for Abar, tau or C_T.
- **Mechanism.** For `w = A - B m`, `wv.lo = A - B d`. The box bound evaluates `w` at the smallest image `m'`, which comes from `c`. The loss is about `B (d - c) = B · 5/16` whatever the panel count. That exceeds the pointwise margins the screen found (`+0.36199` for `8 - m`).
- **Scale of the loss.** The Khat candidate misses by 0.28-0.41, and the drift-block widening only adds to it. Tighter subdivision would help: about depth 6 or deeper for Khat, i.e. about 4k boxes at about 4 s per box, around 4-5 hours per candidate.
- **Scope of this check.** This is a reviewer diagnostic on three boxes, not a sealed run. It is enough to show the frozen configuration fails.

**(b) CRITICAL: compare.py is tautological and pre-writes its conclusion.** See items 4 and 9.

**(c) MAJOR: candidate selection with the originals in view, across the factor-2 line.** Erratum E2 is honest that the Khat candidate changed after the screen. Its claim "NOT fitting to the original's value -- the screen reports only this campaign's own margins" is contradicted by `c11r_screen.py:112-115`, which prints `original Abar 7.9124, tau 5.1698, C_T 5.8299` in the same output as the margins. Under the frozen rule, with "AGREES" meaning at most twice the original:

| Constant | Choice | Candidate value | Original | Ratio | Class |
|---|---|---|---|---|---|
| C_T | Khat `12 - 3/2 m` (dropped) | 12 | 5.8299 | 2.058 | INSUFFICIENT |
| C_T | Khat `8 - m` (chosen) | 8 | 5.8299 | 1.372 | AGREES |
| tau | Khat `12 - 3/2 m` (dropped) | 12 | 5.1698 | 2.321 | INSUFFICIENT |
| tau | Khat `8 - m` (chosen) | 8 | 5.1698 | 1.547 | AGREES |
| Abar | K_e `12 - 3/2 m` (chosen) | 12 | 7.9124 | 1.517 | AGREES |
| Abar | K_e `20 - 3/2 m` (next candidate) | 20 | 7.9124 | 2.53 | INSUFFICIENT |

The stated rationale, one run yielding both constants, holds equally for `12 - 3/2 m`, which is also a Khat_e supersolution evaluated at the atom and as a sup. It therefore does not explain the change. The change is exactly the one that crosses the frozen threshold, and the numbers were on screen. Whether or not that was the motive, the campaign cannot show otherwise, and "SAME STATEMENT BEFORE SAME NUMBER" requires that it can.

**Remedy.** Freeze the candidate policy as a rule that does not reference the original (for example "the tightest `w` in a pre-declared family that certifies"). Strip original values from every pre-comparison module, and extend M03 to the table.

**(d) Same-author propagation.** Independence of implementation and backend is established. Independence of authorship is not, and these single points of failure are shared between C11 and C11R with no external check:

- `box_meets_R` and `cover`: the reachable set R, "taken as a specification" in C11.
- `poly_eval_iv` and `_pow_lin`.
- The kernel formula and constants. I checked these against the original's `float_taboo_kernels` and `cusum_layer1` (item 6); they match.

Two things matter here:

- **The set R (now verified, downgraded to MINOR).** C_T is a sup over the state set, so "same statement" includes that set. I read the original's `resolvent_certificate.reachable_pieces` (`p5y_k5_cusum_order3_r3_infrastructure/code/resolvent_certificate.py:67-75`). Its X is the union of four pieces:

  | Piece | Region | Branch used |
  |---|---|---|
  | `_parameterize_triangle` with r in [0, 1] | `p + m <= 1` | low branch |
  | r in [1, 4] | `1 <= p + m <= 4` | high branch |
  | `plus` | `m = 0`, `p` in [4, 5] | high branch |
  | `minus` | `p = 0`, `m` in [4, 5] | high branch |

  - C11's `box_meets_R`, `{0 <= p, m <= 5 and (p + m <= 4 or p == 0 or m == 0)}`, is **the same set**.
  - C11/C11R check the supersolution, and take `sup w`, over a box cover that is a *superset* of R. That makes the inequality stronger and the sup a valid upper bound, so it is safe.
  - All three failing boxes in 13(a) meet R's interior, so their failure is not an artefact of the superset.
  - Remaining MINOR point: the state set should still be a recorded statement field, because the comparator cannot currently express it.
- **V6.** It cannot detect any C11-shared error by construction (item 12(b)).

**(e) D_lo, D1, D2: "NO_INDEPENDENT_STATEMENT" is literally true but understates what is within reach (MODERATE).**

- `IMPORTANT_READING` says they come from "a different theorem this campaign did not implement". C11R already has most of the building blocks:
  - **Drift-derivative kernels.** `d/de ∫ w(z) phi(z + e) dz = -∫ w(z)(z + e) phi(z + e) dz`, and the second derivative uses `(z + e)^2 - 1`. These are shifted moments one or two degrees higher, which `_moments_pair` already supports for any `j`, with coefficients polynomial in `e`, which `_monomial_pair` already encloses.
  - **`h_1'`, `h_1''`.** Closed forms of `phi` at the window ends, already in `alarm_prob_iv`'s ingredients. C11R lists them as elementary.
- **D_lo specifically** does not need the original's residual-to-error propagation. `D_e = P_a(tau < T_a)` is the minimal non-negative solution of `d = h_1 + Khat_e d`. A comparison-principle *sub-solution* gives an unconditional lower bound over the block. That is strictly stronger than the original's conditional statement, although the comparator cannot currently represent conditionality.
  - It needs one new routine: a box *lower* bound for `Khat_e u`, using `wv.lo`, `mass.lo`, and the *intersection* of the window rather than the union.
  - It also needs a proof that the sub-solution argument applies (boundedness and `Khat_e` substochastic).
- **D1 and D2** genuinely need new work: derivative systems, with operator-norm bounds or monotone iteration for `d'` and `d''`.
- **Honest classification:** D_lo is "NOT ATTEMPTED; independent route identified", and D1 and D2 are "NOT ATTEMPTED; requires derivative-system machinery". That is more accurate than implying all three need the original's theorem.
- It also matters for scope. With at most three of six constants, and with item 13(a), C11R cannot move N9 whatever it does. The campaign should say so before freezing, not discover it after.

**(f) The C2 D′ mixing rule (MINOR).** The C2 adjudication's D′ supply is "min on tau, C_T, D1, D2, max on D_lo, min on Abar". If a future N9 closure combines two certifiers' constants, the direction table in `C11R_N9_TABLE.json` is what should govern the combination, not only the comparison. Not blocking.

### 14. Phase-order discipline: **no target artifact exists. The lapse is disclosed. The record moved during review.**

**What I checked:**

- `git log --all -- '*C11R_RUNS.json'` is empty, and no `evidence/runs/` exists on disk.
- At my first check the working tree was clean at `49b17ab4`.
- The only namespace commit at review start was `49b17ab4`.
- File mtimes: `C11R_SCREEN.json` 03:26, then `c11r_runs.py` 03:27. That is consistent with E2: the candidate was edited after the screen output.
- E1 says the runs attempt used "the first candidate". In `CANDIDATES` order that is the K_e one, so the Khat run never started.

**Adequacy of E1.** It is a candid and adequate record of the lapse itself. Its "no target value was observed" is consistent with item 13(a): a depth-4 K_e run would not have printed a certified value.

**What the record does not reflect:**

- `c11r_errata.py`, `c11r_qualify.py` and `evidence/errata/` appeared untracked at 03:44-03:45 while this review was in flight. They were then committed as `38f59993`. The review was requested against `49b17ab4`.
- E1's own "Verified ... the worktree is clean" was false at the moment the errata file was written, because that file was itself untracked.
- The freeze being reviewed has therefore moved once already. A campaign that asks for review of a fixed state should not change that state until the review returns (MODERATE).
- `c11r_qualify.py` was reviewed only for Q7 (item 11); it has not been run. As committed it would fail Q7 anyway, because the committed mutation evidence lists `survivors = ["M29"]`.
- The state submitted for review was already internally inconsistent before any of this. Its mutation evidence predates its validation and screen evidence, and records REFUSE (item 11). A phase-order record should cover the order in which the *evidence* was produced, not only whether target science ran.

---

## Not reached (stated plainly)

1. **V10 at 32 panels.** Killed by the OS (exit 137, memory from growing exact-rational denominators). It is replaced by the analytic refinement argument in item 5: dyadic u-refinement nests the z-ranges, and so shrinks the image boxes. I did not reproduce V10 numerically at 8 or 16 panels either.

Closed after the first draft of this file:

- **R vs X:** equal as sets (item 13(d)).
- **The nine `certify_cell` inputs:** per sub-block, verified 9/9 by content hash (item 2).
- **M28's committed state:** UNDETERMINED for want of the screen, inside a committed REFUSE mutation class (item 11).

I did **not** run `c11r_qualify.py`. I did not review it beyond Q7, and it was not part of the state submitted for review.

## Severity index

| # | Severity | Finding | Location |
|---|---|---|---|
| 13(a) | CRITICAL | Frozen candidates cannot certify at depth 4 / 16 panels; zero independent values | `c11r_runs.py:37-40`; per-box `L_lo` table in item 13(a) |
| 4 / 9 | CRITICAL | Comparator always EQUIVALENT in production; only one verdict reachable; result text pre-written | `c11r_compare.py:103-105`, `111-128`, `161-172` |
| 11 | CRITICAL | M26 reads a key the producer never writes, so it is guaranteed SURVIVED | `c11r_mutations.py:210` vs `c11r_runs.py:125-136` |
| 11 | MAJOR | M28 reads `depth` from a sub-dict the producer never writes; tautological | `c11r_mutations.py:232-233` vs `c11r_runs.py:71-87` |
| 11 / 13(c) | MAJOR | M03 misses originals read through the table; screen prints originals | `c11r_mutations.py:91-108`; `c11r_screen.py:112-115` |
| 13(c) | MAJOR | Candidate change E2 crosses the frozen factor-2 line with originals on screen | erratum E2; `c11r_runs.py:34-36` |
| 4 | MAJOR | `depends_on` / provenance not compared; the dependency finding is unenforced | `c11r_equiv.py:33` |
| 9 | MAJOR | "DISAGREES branch implemented and exercised" is false | `c11r_compare.py:111-128` |
| 11 / 14 | MAJOR | Committed mutation evidence is stale (M29 SURVIVED "9 mismatches" vs validation's 0; M28 "no screen yet") and its class is REFUSE, frozen beside the gate; no producer hashes in validation, mutation or screen evidence | `evidence/mutations/C11R_MUTATIONS.json`; mtimes in item 11 |
| 13(d) | MINOR | R equals the original's X (verified); the state set is still not a recorded statement field | table / `c11r_equiv.py` |
| 13(e) | MODERATE | D_lo classified as out of reach when a sub-solution route exists | `c11r_runs.py:111-123`; `c11r_compare.py:166-172` |
| 9 | MODERATE | G8, G11, G12 and G13 cannot fail on substance | gate |
| 11 | MODERATE | M29's control is transcribed, not executed; qualifier Q7 accepts INCOMPLETE | `c11r_mutations.py:252`; `c11r_qualify.py:100` |
| 14 | MODERATE | Campaign record changed during the review (`38f59993`) | errata / qualify |
| 1, 2, 4, 5, 8 | MINOR | Disposition scope nuance; per-sub-block dependency; float domains; docstring's `w >= 0` rationale; M01 direct-only | as cited |

**What is right and should be kept unchanged:**

- the N9 reading;
- the six-constant table, every field and every hash;
- the cell 306 vs 307 resolution;
- the dependency finding;
- the atom convention and the numerically exact `K_e = Khat_e + atom`;
- the Abar, tau and C_T mapping;
- the interval-drift layer, including the u-partition box bound and the atom-window intersection, which I found rigorous;
- the independence of imports and backend;
- a gate text free of result language;
- the screen's validity and its two thresholds.

**Minimum to reach READY_TO_FREEZE:**

1. Re-derive a candidate and depth policy that certifies, demonstrated on the worst boxes of the actual cover. It must be frozen as a rule that makes no reference to the original values.
2. Make `c11r_compare.py` build the independent proposition from the runs artifact's own fields, including kernel, quantity, state and provenance, and delete the pre-written result text.
3. Fix M26 and M28 against the actual runs schema, each with an executed negative control. Extend M03 to the table.
4. Regenerate validation, screen and mutations from the committed code in dependency order, each recording its producer hash, and get a non-REFUSE mutation class.
5. Add the state set, verified here to equal the original's X, to the compared fields.
6. Remove original values from `c11r_screen.py`.
7. Reclassify D_lo honestly, or attempt it.
8. Hold the worktree fixed while the next review runs.

NOT_READY
