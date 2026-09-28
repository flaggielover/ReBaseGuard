# Stream D: independent verifier for whole-kernel ARL supersolution certificates

Written 2026-09-28 by agent `streamD`, branch `p5y-k5-cell308-research` (worktree `/Users/suzhe/ReBaseGuard-c308`),
namespace `level4/closure_proofs/p5y_k5_cell308_research/streams/VERIFY/`. Nothing here was staged or committed.
Everything ran at the declared drifts 1/2, 1, 3 and 7/2, which lie outside the quarantined band. No CUSUM m = 5
tail cell was computed, and no cell id appears anywhere in this stream. All validation-drift values of W(a), Lambda
and residuals in this stream are latent proxies. They are kept in this stream's own files only.

## Verdict

| deliverable | status |
|---|---|
| D1 rigorous verifier `vd_verify.verify(W, e)` | **done.** Exact dyadic-rational interval arithmetic; branch and bound over R with 2nd-order interval-AD Taylor bounds |
| D2 format adapter plus independence audit | **done for C1b** (`vd_adapt.py`). The C2b nodal format was **not implemented** (see open issues) |
| D3 produce C1b certificates and verify them | **8/8 PASS**, W(a) == producer A_bar **exactly** in all 8. Stored W equals the adapter's (1 + eta_W) * raw exactly |
| D4 negative controls through `verify()` | **12/12 control outcomes as expected**, every FAIL with a witness confirmed by the second evaluator |
| D5 float cross-check | W(a) >= every float estimate in 8/8. The Monte-Carlo from the process definition is consistent in 8/8 |
| extra: agreement of the two rigorous evaluators | 2003 special-function points and 912 residual evaluations: every pair of enclosures intersects |

The two C1b certificates at 27/10 could not be produced. `certify_degree` raised
`ValueError('G-form coefficient not on the 2^-SC grid')` for the non-dyadic point drift 27/10, so the C1b point
certifier needs dyadic drifts. The declared drift 11/10 is non-dyadic for the same reason and was not attempted.

## 1. What is verified (mathematics)

State x = (p, m) in R = {0 <= p, m <= 5 : p = 0 or m = 0 or p + m <= 4}, with K = 1/2, H = 5 and C = 11/2.
The increment satisfies z + e ~ N(0, 1). The update is T(x, z) = ((p+z-K)^+, (m-z-K)^+). The alarm-free window is
A(x) = [m - C, C - p]. The kernel is (K_e f)(x) = int_{A(x)} f(T(x,z)) phi(z+e) dz, and the atom is a = (0, 0).
Sources are THEOREM_AD section 1 (Lemma K) and section 4 (whole-kernel supersolution), and THEOREM_RLR307 section 0.

**Claim:** W >= 0 and W(x) >= 1 + (K_e W)(x) for all x in R. Then (I - K_e)^{-1} 1 <= W, so E_x[tau] <= W(x) and
Lambda(e) = E_a[tau] <= W(a).

**Note:** for a bounded W, the residual inequality alone already forces W >= 1. If inf W < 0, then
W(y) >= 1 + (K_e 1)(y) inf W >= 1 + inf W for every y, which is impossible. The separate W >= 0 branch and bound is
still run and has its own negative control (iv-b).

**Piece decomposition.** Put u = z + e, a_p = p - K - e and a_m = m - K + e. The breakpoints are
u_L = m - C + e, u_A = K - p + e (the p-arm clips below it), u_M = m - K + e (the m-arm clips above it) and
u_H = C - p + e.
* For t = p + m >= 1:
  * A: u in [u_L, u_A], image (0, a_m - u), running up the m-axis from t - 1 to 5.
  * B: u in [u_A, u_M], image (a_p + u, a_m - u) on the line t' = t - 1.
  * C: u in [u_M, u_H], image (a_p + u, 0).
* For t <= 1:
  * A: u in [u_L, u_M].
  * The atom window: u in [u_M, u_A] with mass W(a)(Phi(u_A) - Phi(u_M)).
  * C: u in [u_A, u_H].

The A and C pieces are split where the image crosses a strip boundary b. For W given on t-strips, the formula is
fixed on each **t-region**; the regions are cut at every b, at b + 1 and at 1. On each piece the integrand is a
polynomial q(u), and int_{u0}^{u1} u^n phi = M_n, where:
* M_0 = Phi(u1) - Phi(u0);
* M_1 = phi(u0) - phi(u1);
* M_n = (n-1) M_{n-2} + u0^{n-1} phi(u0) - u1^{n-1} phi(u1).

## 2. D1: the verifier (`vd_verify.py`)

* **Arithmetic.** Every number is an interval [lo, hi] * 2^-128 held as Python ints. Every operation rounds outward:
  floor for lo and ceil for hi. The comparisons that carry the proof are therefore exact rational comparisons.
  Results are reported as `fractions.Fraction`.
* **Special functions.** These are implemented here, not imported.
  * pi uses Machin's formula with alternating-series bounds, and 1/sqrt(2 pi) uses integer isqrt with directed rounding.
  * exp(-y) splits y into its integer and fractional parts. It uses e^{-1} powers and the alternating Taylor series
    with a tail bound, at 192 internal bits.
  * phi(u) = exp(-u^2/2) / sqrt(2 pi).
  * Phi(u) = 1/2 + sign(u) phi(|u|) S(|u|), with S(v) = sum_n v^{2n+1}/(2n+1)!!. This series has positive terms and a
    geometric tail bound once v^2/(2n+3) <= 1/2.
  * Interval versions use monotonicity (Phi) and unimodality (phi).
* **Forward-mode interval automatic differentiation of order 2.** Each quantity carries a value, a gradient in (p, m)
  and a Hessian. The derivatives of phi and Phi are phi' = -u phi, phi'' = (u^2 - 1) phi, Phi' = phi and Phi'' = -u phi.
  Two sanity checks were run: the AD Hessian matches finite differences of the AD gradient to 7 digits, and the AD
  gradient matches finite differences of the value.
* **Box bound.** For each t-region that a box meets, the region's analytic formula F_J is evaluated. It is exact on
  its region and extends analytically to the whole box, which is sound because F_J is smooth on the box. The lower
  bound is the maximum of two forms:
  * the mean-value form F_J(c) - sum_i max|dF_J/dx_i(box)| r_i;
  * the Taylor form F_J(c) - sum_i |dF_J/dx_i(c)| r_i - (1/2) sum_ij max|H_ij(box)| r_i r_j.

  The box bound is the minimum over the regions. The closed t-intervals are used, so boxes that straddle a region
  or strip boundary get every adjacent formula.
* **Cover of R.** The 2-D part {t <= 4} is covered by dyadic boxes inside [0, 4]^2. The first grid is 1/4, and boxes
  whose lower-left corner has t >= 4 are dropped because their only point of R is a corner that another box covers.
  The 1-D segments {(p, 0), (0, m) : 4 <= p, m <= 5} are covered separately.
* **Decision.**
  * A box whose lower bound is >= 0 is certified.
  * If the box centre lies in R and the residual there has an upper bound < 0 under the centre's own region formula,
    the centre is a rigorous witness. The verdict is FAIL and all workers stop.
  * Otherwise the box is bisected. There is a width floor of 2^-40 and a box budget, beyond which the result is
    UNDECIDED; no run reached them.
  * The same branch and bound, with W's own polynomial, decides W >= 0.
* **Output.** `verify(W, e)` returns `certified`, `verdict` (PASS/FAIL/UNDECIDED), `min_margin_lower_bound`,
  `min_residual_upper_bound` and its point, `W_min_lower_bound`, `W_at_atom` (exact Fraction) and
  `witness_if_refuted` (exact point with the residual enclosure).
* **Margin semantics.** `min_margin_lower_bound` is the smallest lower bound over the certified leaves. It is a
  rigorous lower bound on min_R(W - 1 - K_e W), but it is not tight, because branch and bound stops refining as soon
  as a bound is >= 0. The true minimum lies in [min_margin_lower_bound, min_residual_upper_bound].
* **Speed.** The first-order-only version needed 4446 boxes for the e = 3, d = 4 certificate and 32022 for e = 1,
  d = 4. The order-2 bound needs 623 and 1938 boxes. One core handles about 3-6 ms per box, and 3 workers are used.

**Second evaluator (`vd_point.py`).** This is a pointwise evaluator with no shared routine:
* exact `Fraction` arithmetic;
* pi from the BBP series;
* exp by argument halving plus exact Taylor terms plus squaring;
* Phi from the *alternating* Maclaurin series with exact partial sums;
* generic breakpoint discovery: the candidate cuts are sorted, and on each sub-interval the image branch and strip
  are decided from its midpoint, with no region bookkeeping;
* integration by an antiderivative: q = c + uA - A' gives int q phi = c Phi - A phi.

It confirms every D4 witness. The final D4 and crosscheck runs used vd_point sha256 `d0b0f5c9754114b4...`, which
includes the drift guard. Final source hashes are in `logs/sources_final_runs.sha256`. `vd_crosscheck.py` checks that the two evaluators agree on 2003 random special-function
points and on 912 residual evaluations: 8 certificates, 57 structural and random points each, with and without the
atom window. Every pair of enclosures intersects, and the largest vd_verify special-function width is 2.1e-36.

## 3. D2: formats, lines read, import audit, measured shared surface

**C1b layout** (adapter `vd_adapt.from_c1b_raw`):
* W is a list over strips [P_1, ..., P_S], each P_s = {(i, j, k): c} meaning c p^i m^j e^k, with k = 0 for point
  certificates.
* Strip s is [BW[s-1], BW[s]] of t = p + m. Strips are right-closed, and the first is closed at 0.
* The value in x-region J = ceil(t) uses the strip containing [J-1, J]. For integer BW this is exactly the
  right-closed strip of t, and the adapter asserts integer BW.
* The certified W is (1 + eta_W) * rec['_c']['W'], and A_bar is strip 1 evaluated at (0, 0).
* The producer stores both the raw layout (`c1b_raw`) and the pre-scaled strips. The verifier rebuilds W from the
  raw layout and checks that it equals the stored strips exactly.

**Original code that I READ (layout, and what I saw beyond layout):**

| file (OV/streams/C_308/...) | lines | what |
|---|---|---|
| LR/cusum/c1b_certpw.py | 1-140, 187-302; a grep of 340-410 | Header, helpers, `Ctx`, `residual_forms`, `at_atom`, `check_supersolution`, `certify_degree` and the record keys. The layout facts are at lines 119-120, 193, 206-207, 211, 279 and 298 |
| LR/cusum/c1b_pw.py | 1-60, 97-127, 236-258 | Strip semantics docstring, `BW_PW`, `strip_of_interval`/`strip_of_t`, the first lines of `kernel_gf_pw`, `tpoly`, `region_of_point`, `regions_of_box`, `in_R`, `solve_chain_pw`, `to_exact_pw` |
| LR/cusum/c1b_kernel.py | 1-80, 677-684 | Docstring, polynomial dict helpers, `peval`, `dyadic_round_poly` |
| LR/cusum/c1b_float.py | 261-271 | `to_exact_poly` head |
| LR/cusum/c1b_gauss.py | 30-42 plus the function list | Read **after** my verifier was written, only to explain an identical line found by the overlap scan |
| A0X/gen/c2b_exact.py | 1-70 | P1 nodal mesh and cell layout |
| A0X/gen/c2b_common.py, c2b_certify.py | grep only | constants; storage keys |
| A0X/gen/results/block_1_11_10_N20_whole.json | top-level keys only | nodal vector not stored (alpha, beta, certificate summary) |
| cell-307 `code/rlr307_stage1.py` | 60-100 | `certify_degree(e_c, d, pw.BW_PW, log=..., e_r=...)` call pattern |

**Disclosure:** the c1b_kernel.py docstring (lines 1-22) describes the original algorithm, which I read before
writing mine. It works in "G-forms" (closed forms in phi/Phi at affine breakpoints with polynomial coefficients),
encloses them with Taylor models of order 10 using Hermite coefficients and a Lagrange remainder, and bounds
polynomial ranges by |c_0| + sum |c_a| r^a.

The **mathematical closed form is common** to both: the integrals of a polynomial times phi via phi and Phi at the
piece ends, which the brief itself prescribes. The **enclosure technique is different**: second-order interval
automatic differentiation with mean-value and Taylor forms, versus order-10 Taylor models. My special functions, my
piece and region bookkeeping, and my cover of R were written from the mathematics. The second evaluator shares
neither the moment recurrence nor the region logic.

**Import audit** (`results/D2_INDEPENDENCE.json`):
* **Static (AST).** 10 verifier-side files: vd_verify, vd_point, vd_adapt, vd_float, vd_controls, vd_d3_verify_all,
  vd_d5, vd_mc, vd_crosscheck and vd_independence. They import only the stdlib and each other. There are **zero**
  `c1b_*`, `c2b_*`, `c7_*` or `ov_quarantine` imports.
* **Quarantine module.** `c308_quarantine.py` is loaded by file path in vd_verify, vd_point, vd_float and vd_produce.
* **Planted control.** A file importing c1b_pw, c2b_exact and c7_gaussian is flagged 3/3.
* **Runtime.** After importing all verifier modules and running a residual, a branch and bound and a vd_point
  evaluation, `sys.modules` (112 modules) contains no certifier module. The planted runtime control, a subprocess
  importing c1b_gauss, is detected.
* **Producer.** `vd_produce.py` is the only file that imports C1b (`c1b_certpw` and `c1b_pw`). It is not part of the
  verifier.

**Measured shared code surface.** Lines were normalised by collapsing whitespace, keeping only lines of at least 25
characters and dropping comments. They were compared with all 25 `.py` files of the two original certifier
directories.

| verifier-side file | normalised lines | identical to any original line | shared top-level names (coincidental) |
|---|---|---|---|
| vd_verify.py | 413 | 8: `from __future__ ...`, `from fractions import Fraction as F`, `from functools import lru_cache`, `HERE = Path(__file__)...`, `if __name__ == "__main__":`, two lines of a generic `jsonable`, `PI_LO, PI_HI = _pi_bounds()` | `_pi_bounds`, `Phi_iv`, `phi_iv`, `in_R`, `jsonable` |
| vd_point.py | 107 | 2 (the two `from` imports) | `Phi`, `phi`, `exp_neg`, `padd`, `pmul`, `ppow`, `peval` |
| vd_adapt.py | 26 | 2 (imports) | - |
| all 10 files | 1043 | 46 (boilerplate imports, `__main__` guards, `HERE = ...`) | generic names (`main`, `run`) |

The `_pi_bounds` line is a coincidence of a common name. I checked c1b_gauss lines 30-42 afterwards: it is also
Machin's formula, which is the textbook choice, so it is a common-mode *formula*, but it is independently coded. The
second evaluator uses BBP. **No function body, algorithmic line or module is shared.** Shared *conventions* are the
kernel model, the strip semantics and the moment closed form; see open issue 3.

## 4. D3: C1b certificates produced and verified

`vd_produce.py` calls `c1b_certpw.certify_degree(e, d, c1b_pw.BW_PW, log, e_r=F(0))` under 3 spawn workers. Each
status is CERTIFIED, taking 43-256 CPU-s. The certificates are in `certs/CERT_e<num>_<den>_d<d>.json` with
`sha256_body` and a manifest.

**Producer reproducibility.** Runs 1-2 and run 3 gave byte-identical pre-scaled strips, eta_W and A_bar for all 8
certificates (`results/PRODUCER_REPRODUCIBILITY.json`).

Final run (`results/D3_VERIFY_ALL.json`, vd_verify sha256 `cd4cec35...`):

| certificate | drift | d | verdict | W(a) == A_bar exactly | adapter == stored | margin lower bound | min residual upper bound | boxes | s |
|---|---|---|---|---|---|---|---|---|---|
| CERT_e1_1_d4.json | 1 | 4 | PASS | True | True | 3.14e-07 | 0.00349 | 1938 | 4.4 |
| CERT_e1_1_d6.json | 1 | 6 | PASS | True | True | 1.46e-07 | 0.000322 | 34390 | 96.7 |
| CERT_e1_2_d4.json | 1/2 | 4 | PASS | True | True | 2.93e-05 | 0.0235 | 1127 | 2.7 |
| CERT_e1_2_d6.json | 1/2 | 6 | PASS | True | True | 2.94e-07 | 0.000768 | 25404 | 76.1 |
| CERT_e3_1_d4.json | 3 | 4 | PASS | True | True | 1.28e-05 | 0.00592 | 623 | 1.9 |
| CERT_e3_1_d6.json | 3 | 6 | PASS | True | True | 2.28e-08 | 0.000242 | 31375 | 94.7 |
| CERT_e7_2_d4.json | 7/2 | 4 | PASS | True | True | 9.43e-05 | 0.00926 | 753 | 2.0 |
| CERT_e7_2_d6.json | 7/2 | 6 | PASS | True | True | 8.54e-07 | 0.000662 | 20810 | 57.1 |

The d = 6 certificates have true minimum residuals of order 1e-4. This is the eta_W rescaling rule working as
designed: W is scaled until the producer's own lower bound reaches 0, plus a dyadic rounding of at most 2^-20.

| file | sha256 |
|---|---|
| CERT_e1_1_d4.json | 8f7df6e01a69b320... |
| CERT_e1_1_d6.json | 1c40f1ed633a1c16... |
| CERT_e1_2_d4.json | 281eaf4076f6c1a1... |
| CERT_e1_2_d6.json | 0bc8f2ead18a5184... |
| CERT_e3_1_d4.json | dda322d6c3fb47e2... |
| CERT_e3_1_d6.json | b86fed7291ccf043... |
| CERT_e7_2_d4.json | 22fb92b23aafb5d4... |
| CERT_e7_2_d6.json | 6587b4a3aeb6052e... |

## 5. D4: negative controls, all through `verify()` (`results/D4_CONTROLS.json`)

| # | control | expected | observed | pass |
|---|---|---|---|---|
| 0 | e = 3, d = 4 certificate at its own drift | PASS | PASS | yes |
| i | (1 - 2^-k) W, k = 20, 19, ... | PASS ... then FAIL | PASS for k = 20..8, **FAIL at k = 7**; witness (31/128, 481/128), independent residual hi -8.0e-5 | yes |
| ii-a | strip-1 coefficient of p^2 m^2 lowered by 1 | FAIL | FAIL; witness (7/32, 11/16), independently confirmed | yes |
| ii-b | strip-2 constant raised by 2^-20 | PASS | PASS | yes |
| iii | e = 3 certificate at e' = 1 | FAIL | FAIL; witness (1/8, 1/8), confirmed (independent hi -0.736) | yes |
| iii | e = 1 certificate at e' = 1/2 | FAIL | FAIL; witness (1/8, 1/8), confirmed (independent hi -0.482) | yes |
| iii | e = 7/2 certificate at e' = 3 | FAIL | FAIL; witness (1/8, 1/8), confirmed (independent hi -0.122) | yes |
| iv | strip-4 constant lowered by 50, so W < 0 on t in (3, 5] | FAIL | FAIL through the residual; witness (3/16, 23/8), confirmed (independent hi -32.7) | yes |
| iv-b | the W >= 0 branch and bound alone, on the same W | REFUTED | REFUTED; W upper bound -48.7 at (1/8, 25/8) | yes |
| v-a | atom window omitted, valid e = 3 certificate | residual at a changes by W(a)(Phi(K+e) - Phi(e-K)) | the difference encloses exactly that product; the verdict stays PASS | yes |
| v-b | planted W - delta (1-t)^2 on strip 1, e = 1, delta = 1/4 | FAIL with the atom, PASS without | **FAIL with the atom** (witness (1/8, 1/8), confirmed); **PASS without it** | yes |
| vi | notched W: (1 + 2^-5) W + (1/2) prod_{i=4..8}(4t - i) on strip 2 | FAIL | FAIL; witness (3/16, 9/8) at t = 21/16, **not a sample point**, confirmed | yes |

Notes on individual controls:
* **(i)** The expectation is PASS for large k, then FAIL once 2^-k > r_min / (1 + r_min). The ladder brackets r_min
  in [0.00392, 0.00787], which is consistent with the base-run bracket [1.28e-5, 0.00592].
* **(ii-a)** The residual at (1/2, 1/2) drops by exactly 1/16, because the A/C/atom images carry p'm' = 0. An
  independent check confirmed that the drop encloses 1/16.
* **(ii-b)** 2^-20 is below the certified margin lower bound 1.28e-5. The residual moves by >= -2^-20, so the
  certificate must stay valid.
* **(iii)** The expected FAIL is based on Lambda(e') > W_e(a), from D5.
* **(iv)** A negative W can never satisfy the residual inequality (see section 1), so the FAIL through the residual
  is the expected route.
* **(v-a)** In the certificate, removing the atom window only raises the residual.
* **(v-b)** delta was chosen by a rigorous point scan on the 1/16 grid of t <= 1.
* **(vi)** The notch is valid, rigorously (every residual lower bound > 0, minimum 0.037), at **all 305 vertices and
  centres of the initial 1/4 grid**, and 13 of those points were confirmed by vd_point. The witness lies inside a
  negative lobe.

Earlier, before the stop-at-first-witness change, the same controls passed identically, but control (vi) took
1029 s and 148,974 boxes because every initial box was still certified. That run is kept in
`results/prev_no_early_exit/`.

## 6. D5: float cross-check (non-rigorous; `results/D5_FLOAT.json`, `results/D5_MC.json`)

**Value iteration (`vd_float.py`).** The unknowns are nodes (ih, jh) with i + j <= 4N, plus the axis nodes up to 5.
U is P1-interpolated along the axes and along the lattice anti-diagonal t' = t - 1. The hat-function weights are
integrated exactly against phi with `math.erf`. The atom mass goes to the node (0, 0). The system is solved by
Gauss-Seidel until the update is < 1e-11, at N = 10 and N = 20, followed by h^2 Richardson extrapolation.

| drift | U_10(a) | U_20(a) | Richardson | W(a) d=4 | W(a) d=6 | min over N=20 nodes of W - U_20 (d4 / d6) |
|---|---|---|---|---|---|---|
| 3 | 2.573390 | 2.573286 | 2.573252 | 2.626366 | 2.575573 | 0.0088 / 0.00046 |
| 7/2 | 2.227594 | 2.227498 | 2.227466 | 2.293723 | 2.232506 | 0.011 / 0.00096 |
| 1 | 10.375612 | 10.375880 | 10.375970 | 10.484976 | 10.386101 | 0.022 / 0.0018 |
| 1/2 | 37.955386 | 37.985943 | 37.996129 | 41.066600 | 38.088833 | 0.72 / 0.024 |

* W(a) is >= every float estimate for all 8 certificates.
* W dominates U_20 at **every** node.
* The relative gap between W(a) and the Richardson value is 0.09-0.24 % for d = 6 and 1.0-8.1 % for d = 4.

**Monte-Carlo (`vd_mc.py`).** This simulates the process directly from the CUSUM definition, which checks the
kernel model shared by all the evaluators. The runs were 4e5, 4e5, 2e5 and 1e5 paths, with fixed seeds.

| drift | mean ± se |
|---|---|
| 3 | 2.5743 ± 0.0010 |
| 7/2 | 2.2288 ± 0.0008 |
| 1 | 10.3765 ± 0.0122 |
| 1/2 | 38.178 ± 0.099 |

These agree with the float values within about 2 se. Each W(a) is >= mean - 4 se; the smallest z-score is -0.91,
for d = 6 at e = 1/2.

## 7. Open issues and limitations

1. **The C2b P1 nodal format is not implemented.** C2b result files do not store the nodal vector: they store
   alpha and beta applied to a Nystrom proposal. Checking one would need (a) a producer that re-runs the C2b proposal
   and (b) triangle-piecewise W support in the verifier. The anti-diagonal B-images cross the mesh at p' = ih, and
   the axis images are piecewise linear with nodes every h. `vd_point` already handles arbitrary breakpoints; the
   branch and bound would need a triangle cover and a region per triangle.
2. **Drifts 27/10 and 11/10 are not covered.** The C1b *point* certifier refuses non-dyadic drifts. Covering them
   would need a dyadic hull block (e_r > 0), which C1b supports but this verifier does not: it verifies at a single
   exact drift. A drift-block extension would enclose the e-derivative by the same AD, adding e as a third variable.
3. **Common-mode assumptions.**
   * The kernel model (window, clipping, alarm semantics, atom) and the strip semantics are shared with C1b by
     construction.
   * The model is checked against the process definition only non-rigorously: Monte-Carlo and float value iteration.
   * The strip semantics come from reading C1b. For integer BW they coincide with "right-closed strip of t".
4. **The margin lower bound is not tight** (see section 2). A tightening pass, refining every box below 3/4 of the best
   upper bound, was tried and abandoned. On flat residuals it needs about 1e5-1e7 boxes because the first-order spread
   dominates.
5. **Speed.** Degree-6 certificates take 57-97 s wall on 3 workers (20k-34k boxes). The cost is Python bigint
   interval arithmetic, about 3-6 ms per box.
6. **Witnesses are not deterministic.** With `imap_unordered` and stop-at-first-witness, the witness point can
   differ between runs. It is always rigorous and always independently confirmed.
7. **Scan notes.** `code/c308_quarantine.py --scan` returns PASS, with 0 findings anywhere. It reports six
   REPORT_ONLY ATTENTION_DRIFT_LITERAL entries in this stream: 3/2, 7/3 and 5/3 are state coordinates p and m in
   vd_crosscheck and a delta step in vd_controls, and 2.0 is `math.sqrt(2.0)` in vd_float. None of them is a drift.

## 8. Quarantine compliance

* Every entry point calls `guard_drift`: `Prep`, `verify`, `vd_point.residual`, `vd_point.kernel_W`, `produce`,
  `vd_float.run` and the vd_mc worker. The vd_point guard was checked once by a refusal test: it refused 19/10 before
  any evaluation.
* The import guard is installed in vd_verify, vd_point, vd_float and vd_produce.
* Drifts used: 1/2, 1, 3, 7/2. The attempt at 27/10 was refused by the certifier, not by the quarantine; 27/10 lies
  outside the band. No band drift was used, no cell id was used, and no forbidden file was opened.
* Ledger: the streamD lines in `ledger/TARGET_INTEGRITY_LEDGER.jsonl` are all class NONTARGET_DRIFT_VALIDATION or
  INFRASTRUCTURE, with 0 target evaluations.
* OV was not written. `git status --short level4/closure_proofs/p5y_k5_tail_overnight_research` is empty. The C1b
  modules were imported under `-B`, so no `__pycache__` was written.

## 9. Files

| path | role |
|---|---|
| `vd_verify.py` | D1 verifier (sha256 cd4cec35e86d8036...) |
| `vd_point.py` | second, independent pointwise rigorous evaluator |
| `vd_adapt.py` | D2 C1b-to-StripPW adapter |
| `vd_produce.py` | D3 producer, the only file that imports C1b |
| `vd_d3_verify_all.py` | D3 runner |
| `vd_controls.py` | D4 controls |
| `vd_float.py`, `vd_d5.py`, `vd_mc.py` | D5 cross-checks |
| `vd_crosscheck.py` | agreement tests between the two evaluators |
| `vd_independence.py` | D2 audit |
| `certs/` | 8 certificates plus the producer manifest |
| `results/` | D2_INDEPENDENCE, D3_VERIFY_ALL, D4_CONTROLS, D5_FLOAT, D5_MC, CROSSCHECK, PRODUCER_REPRODUCIBILITY, prev_no_early_exit/ |
| `logs/` | run logs and the source sha256 of the final runs |

---

# Follow-up (2026-09-29): D6 P1 nodal format, D7 high-degree cost, D8 re-measurement

Sections 1-9 above are unchanged from the first report, which is committed at `c494705d`. The C1b-format verifier
`vd_verify.py` was not modified; its sha256 is still `cd4cec35...`. `vd_point.py` gained P1 support, so the
strip-format crosscheck and the D4 controls were re-run on the final code (section 13). The final source hashes are
in `logs/sources_followup.sha256`. The machine was shared throughout: another stream's pool was running, and my
producer occupied 2 workers for 48 minutes. Wall times are therefore indicative only.

## 10. D6: independent verifier for P1 (triangle-piecewise-linear) nodal certificates (`vd_pl.py`)

### Data layout

This is the only information taken from stream A0 (section 12 lists the lines read).

* The nodes are (ih, jh) with h = 1/N. Column i has height cols(N) = [5N+1] + [4N-i+1 for i = 1..4N] + [1]*N.
* The cells are:
  * L(i,j) = conv{(i,j), (i+1,j), (i,j+1)}, for i + j <= 4N - 1;
  * U(i,j) = conv{(i+1,j), (i,j+1), (i+1,j+1)}, for i + j <= 4N - 2 (the anti-diagonal split);
  * the axis segments beyond t = 4.
* W is linear on every cell.
* Values are stored as integers at scale 2^-Qbits.
* `W_sha256` = sha256(`json.dumps([[str(x) ...]], sort_keys=True, separators=(",", ":"))`).
* `claim_w_atom` = W(a).
* The `certifier` field is `C2B_P1_SUPER` or `C2B_P1_SUB`.
* The adapter `vd_pl.from_a0_cert` recomputes the sha256 from the stored integers, checks the shape and converts
  every value to an exact Fraction.

### Kernel application (derived here; `vd_pl.py` docstring)

Put u = z + e. Along the window [u_L, u_H] = [m - C + e, C - p + e], the path value g(u) = W(T(x, u - e)) is
continuous and piecewise linear. The image moves:
1. down the m-axis;
2. then along the line p' + m' = t - 1 (for t >= 1), or stays in the atom (for t <= 1);
3. then along the p-axis.

With Psi(u) = u Phi(u) + phi(u), so that Psi' = Phi, two integrations by parts give

    int g phi = g(u_H) Phi(u_H) - g(u_L) Phi(u_L) - s_last Psi(u_H) + s_first Psi(u_L) + sum_k (slope jump at u_k) Psi(u_k)

**Kinks.** Every kink is a mesh crossing, at u = ih + K + e - p or at u = m + e - K - jh. The jumps are exact
rationals. They depend only on the nodal values and on the t-band of x:
* second differences on the axes;
* differences of the edge slopes D(i,j) = (w[i+1][j] - w[i][j+1])/h along p' + m' = t - 1;
* the junction coefficients (w[1][b] - w[0][b])/h and (w[b][1] - w[b][0])/h, or (C_1 - C_0)/h and (A_1 - A_0)/h
  when t <= 1.

**Separable residual.** On every mesh cell the residual is exactly alpha + beta p + gamma m - 1 - P_band(p) - M_band(m).

**Cell bound.** On a cell, or on one of its 4 midpoint children:

    F(c) + min over the vertices of grad F(c) . (v - c) - 1/2 (max|P''| r_p^2 + max|M''| r_m^2)

* The linear part is exact on the triangle, so only the second-order remainder is slack.
* It uses the exact dyadic interval arithmetic and the special functions of vd_verify.
* The band-independent tails are handled by suffix sums.

**Decisions.**
* A centroid whose residual has an upper bound < 0 is a rigorous witness, and the run stops.
* W >= 0 on R holds iff every node is >= 0.
* For SUB certificates the verifier checks 1 + K_e W - W >= 0. For bounded W this gives E_x[tau] >= W(x), because the
  resolvent series converges.
* W(a) = w[0][0] is returned exactly and compared with the claim.

### Second, independent evaluator

`vd_point.PL` shares nothing with the kink/Psi formula:
* cells are located by a barycentric test;
* breakpoints are found generically;
* each linear piece is integrated by an exact antiderivative;
* the arithmetic is exact Fraction arithmetic with its own Phi and exp.

`vd_pl_crosscheck.py` compared the two evaluators on 7 certificates:
* N = 10, 20 and 40;
* drifts 1/2, 1, 11/10, 27/10, 3 and 7/2;
* SUPER and SUB;
* the atom, t = 1, band and mesh boundaries, nodes, centroids, the axes beyond 4, (5,0), (0,5) and random rational
  points;
* with and without the atom window.

**Result:** 464 residual evaluations, **all enclosures intersect**, and the exact W(x) of the two cell-location codes
is **identical everywhere** (`results/D6_PL_CROSSCHECK.json`).

### 10a. Every stored A0 C2b / C2bx certificate (`results/D6_VERIFY_PL.json`)

All **98** stored P1 certificates in `streams/A0/certs/` were checked:
* 48 C2B and 50 C2BX; 49 SUPER and 49 SUB;
* N = 10, 20, 40 and 80;
* drifts 1/2, 1, 11/10, 27/10, 3 and 7/2.

Results:
* **98/98 PASS.**
* **W(a) == claim_w_atom exactly in 98/98.**
* The recomputed W_sha256 matches in 98/98.
* 0 are undecided.
* Only 3 needed any subdivision beyond the base cells, all at e = 1/2 (132-264 extra boxes). Every other certificate
  was decided on its mesh cells alone.

Costs are for a single process: `--workers 1`, because the producer held the other slots.

| family | direction | N | certificates | PASS | W(a) == claim | cells | margin lower bound (min .. max) | wall s per certificate (mean / max) |
|---|---|---|---|---|---|---|---|---|
| C2B | sub | 10 | 6 | 6 | 6 | 1620 | 6.71e-04 .. 1.54e-02 | 0.4 / 0.5 |
| C2B | sub | 20 | 6 | 6 | 6 | 6440 | 1.69e-04 .. 3.96e-03 | 2.3 / 2.9 |
| C2B | sub | 40 | 6 | 6 | 6 | 25680 | 4.21e-05 .. 1.00e-03 | 14.6 / 17.6 |
| C2B | sub | 80 | 6 | 6 | 6 | 102560 | 1.05e-05 .. 2.51e-04 | 125.3 / 147.1 |
| C2B | super | 10 | 6 | 6 | 6 | 1620 | 1.20e-04 .. 1.69e-03 | 0.5 / 0.6 |
| C2B | super | 20 | 6 | 6 | 6 | 6440 | 5.34e-07 .. 4.54e-04 | 2.4 / 2.9 |
| C2B | super | 40 | 6 | 6 | 6 | 25680 | 3.32e-06 .. 2.37e-04 | 13.5 / 15.6 |
| C2B | super | 80 | 6 | 6 | 6 | 102560 | 1.07e-04 .. 2.37e-04 | 117.8 / 173.2 |
| C2BX | sub | 20 | 8 | 8 | 8 | 6440 | 1.69e-04 .. 3.96e-03 | 2.7 / 3.1 |
| C2BX | sub | 40 | 9 | 9 | 9 | 25680 | 4.21e-05 .. 1.00e-03 | 12.8 / 14.4 |
| C2BX | sub | 80 | 8 | 8 | 8 | 102560 | 1.05e-05 .. 2.51e-04 | 98.5 / 143.3 |
| C2BX | super | 20 | 8 | 8 | 8 | 6440 | 2.61e-04 .. 5.16e-04 | 2.6 / 3.6 |
| C2BX | super | 40 | 9 | 9 | 9 | 25680 | 6.47e-05 .. 1.22e-04 | 14.4 / 16.9 |
| C2BX | super | 80 | 8 | 8 | 8 | 102560 | 1.61e-05 .. 2.97e-05 | 122.2 / 166.2 |

**Total main-process CPU:**

| N | certificates | CPU seconds |
|---|---|---|
| 10 | 12 | 5 |
| 20 | 28 | 65 |
| 40 | 30 | 394 |
| 80 | 28 | 2816 (54 min wall) |

Cost grows like the number of cells times the band length, roughly N^3. The quoted margin lower bounds are rigorous
but not tight, as in section 2.

### 10b. Controls through `verify_pl()` (`results/D6_PL_CONTROLS.json`)

The base is A0's C2B_SUPER at e = 3, N = 20. Every FAIL witness was confirmed by `vd_point.PL`. The final run
passed all 13 controls in 79 s.

| # | control | expected | observed | witness (cell), independent residual upper bound | pass |
|---|---|---|---|---|---|
| 0 | the base certificate at its own drift, claim checked | PASS | PASS | - | yes |
| 1 | node (10,10) = (1/2,1/2) lowered by 1/64 | FAIL | FAIL | (29/60, 29/60) in U(9,9), -4.7e-3 | yes |
| 2a | atom node lowered by 1/64 | FAIL | FAIL | (1/60, 1/60) in L(0,0), -4.6e-3 | yes |
| 2b | atom node raised by 2^-12 | inequality PASS, certificate FAIL on the claim | inequality PASS; certificate FAIL, `claim_mismatch` | - | yes |
| 3 | (1 - 2^-k) W for k = 20, 19, ... | PASS ... then FAIL | PASS for k = 20..12, **FAIL at k = 11** | (1/60, 23/30) in L(0,15), -7.2e-7 | yes |
| 4 | C2B e = 3 checked at e' = 1 | FAIL | FAIL | (1/60, 1/60), -0.73 | yes |
| 4 | C2B e = 1 checked at e' = 1/2 | FAIL | FAIL | (1/60, 1/60), -0.45 | yes |
| 4 | C2B e = 7/2 checked at e' = 3 | FAIL | FAIL | (1/60, 1/60), -0.15 | yes |
| 4 | C2B e = 27/10 checked at e' = 11/10 | FAIL | FAIL | (1/60, 1/60), -0.66 | yes |
| 5 | node (0, 5N) set to -1 | FAIL | FAIL | (0, 199/40) on an m-axis segment, confirmed | yes |
| 6 | atom window omitted, valid certificate | residual at a rises by W(a)(Phi(K+e) - Phi(e-K)) | the difference encloses exactly that; the independent evaluator agrees | - | yes |
| 7 | **vertex-only-acceptable candidate** (1 - s) W | FAIL with an interior witness while every node is valid | FAIL; **all 3361 node residuals rigorously > 0** (smallest lower bound 5.7e-4); witness (41/3072, 4403/7680) strictly inside triangle L(0,11), not a node; independent upper bound -2.1e-7 | see previous column | yes |

Notes on individual controls:
* **(3)** The ladder brackets r_min in [2.44e-4, 4.89e-4], which is consistent with the base-run bracket
  [3.84e-4, 4.74e-4].
* **(4)** Every wrong drift was chosen with a smaller |e|, so Lambda(e') > W_e(a) and the certificate must fail.
* **(7)** This is the err-path case the C2b review asked for.
  * The base is A0's C2B_SUPER at e = 1/2, N = 20. Scanning four certificates found its interior centroid minimum
    below its node minimum, both rigorous, and the minimum lies inside a triangle.
  * s = 457300367/2^37 (about 3.33e-3) lies strictly inside the window between the two r/(1 + r) ratios, [2.76e-3, 3.89e-3].
  * A vertex-only checker would accept this W. The branch and bound rejects it after 1917 boxes.

## 11. D7: cost of the C1b-format verifier at degrees 8, 10, 12 (e = 1 and e = 3)

**Production.** `vd_produce.py`, run with 2 workers for 48 min wall, called C1b `certify_degree`:

| certificate | producer status | producer CPU |
|---|---|---|
| e = 3, d = 8 | CERTIFIED | 283 s |
| e = 3, d = 10 | CERTIFIED | 1112 s |
| e = 3, d = 12 | CERTIFIED | 1342 s |
| e = 1, d = 8 | CERTIFIED | 739 s |
| e = 1, d = 10 | **SCALING_RULE_INAPPLICABLE** (the float fit's residual lower bound is <= -1) | - |
| e = 1, d = 12 | **SCALING_RULE_INAPPLICABLE** | - |

The four new certificates are in `certs/`. The strip crosscheck (section 13) covers them.

**Verification: not completed, so no verdict is claimed for any d >= 8 certificate.**
* e = 1, d = 8 was aborted after about 23 min wall on 2 workers.
* e = 3, d = 8 was aborted after about 38 min wall on 2 workers, with a budget of 40000 boxes per initial box.
* By comparison, d = 6 takes 57-97 s on 3 workers and d = 4 takes 2-4 s.

**Diagnosis (`vd_d7_probe.py` → `results/D7_PROBE.json`).** A single process, e = 3, at most 200 boxes per initial
box; there are 144 initial boxes:

| degree | ms per second-order box bound | initial boxes certified within 200 boxes | boxes used |
|---|---|---|---|
| 4 | 6.1 | 144/144 | 623 |
| 6 | 7.6 | 83/144 | 22382 |
| 8 | 12.4 | **8/144** | 27962 |
| 10 | 19.2 | **3/144** | 28749 |
| 12 | (probe stopped for time) | - | - |

At d >= 8 the scaled residual is small **everywhere**. The unscaled residual range drops from about 3e-2 (d = 4) to
about 3e-4 (d = 8). The producer's own positive margins are 5.6e-6 (d = 8), 6.1e-8 (d = 10) and 9.1e-7 (d = 12) at
e = 3.

The second-order interval-AD bound needs boxes of size about sqrt(margin/|Hessian enclosure|) over the whole of R.
Its Hessian enclosure also widens with degree, through the dependency effect in the Taylor shift and the moment
recurrence.

**Conclusion.** This verifier is practical up to d = 6 (about 1.5 min) and impractical at d >= 8 in its current
form. The fix would be a tighter local form, such as a Taylor model of order > 2 or Chebyshev remainder forms. That
is exactly where the original C1b spends its effort (order-10 Taylor models), so an independent check of d >= 8
certificates is an open item.

## 12. D8: independence re-measured (final code; `results/D2_INDEPENDENCE.json`)

**Stream A0 lines READ, for layout only:**
* `a0_verify.py`: the whole file, 129 lines.
* `a0_c2b.py`: lines 164-172 (`w_sha256`, `make_cert`).
* `a0_common.py`: lines 102-110, 114-117, 125-126 and 226-227 (`declared_drift`, `fs`, `sha256_bytes`, `canon`).
* `a0_c2bx.py`: grep hits at lines 14 and 88 (the certifier name).
* The top-level JSON keys of 3 A0 certificates.
* The timing keys of 4 A0 `results/C1B_e*_d*.json` files, used only to plan D7.

From the first report I had also read `c2b_exact.py` lines 1-70 (the mesh and cell enumeration). **Disclosure:** the
overlap scan below made me read `c2b_exact.py` lines 236-253 **after** `vd_pl.py` was written. They show that the
original C2b also forms suffix sums over axis second differences. That is the same mathematical structure (kinks of
P1 on the axes), which I reached independently from my own derivation. It is common-mode *mathematics*, not shared
code.

**Import audit.**
* **Static.** All 15 verifier-side files are clean: zero `c1b_*`, `c2b_*`, `c7_*`, `a0_*` or `ov_quarantine`
  imports. `vd_pl.py` imports only the stdlib and `vd_verify`.
* **Planted control.** A file importing a0_c2b, c1b_pw, c2b_exact and c7_gaussian is flagged 4/4.
* **Runtime.** After running vd_verify, vd_point (strip and PL), vd_pl.verify_pl, vd_adapt and vd_float, the
  process holds 113 modules and no certifier module. The planted runtime control is detected.
* The producer remains the only C1b importer.

**Measured shared surface.** Lines were normalised as before and compared with 40 original files: the C1b and C2b
directories of OV plus `streams/A0/*.py`.

| file | normalised lines | identical lines | what the identical lines are |
|---|---|---|---|
| vd_pl.py | 286 | 9 | 5 boilerplate lines; 3 mesh-enumeration loop headers (`for j in range(4 * N - i):`, `for i in range(4 * N, 5 * N):`, `for j in range(4 * N, 5 * N):`) that coincide with `c2b_exact.Mesh.cells`, i.e. the prescribed layout; `for k in range(n5 - 1, 0, -1):`, a suffix-sum loop header that coincides with `c2b_exact.py` line 239/250 (see the disclosure above) |
| vd_d6_verify_pl.py | 56 | 6 | 5 boilerplate lines plus `if cert.get("kind") != "whole":`, the same layout check as `a0_verify.py` |
| vd_point.py | 137 | 2 | imports |
| vd_pl_controls.py, vd_pl_crosscheck.py, vd_d7_cost.py | 227 | 14 | boilerplate |
| vd_verify.py | 413 | 10 | as in section 3, plus 2 boilerplate matches with A0 files |
| **all 15 files** | **1648** | **79** | no function body or algorithmic block is shared |

## 13. Regression re-runs after the `vd_point.py` change

| check | result | log |
|---|---|---|
| Strip-format crosscheck (`vd_crosscheck.py`), now over 12 certificates including the d = 8/10/12 ones | 2003 special-function points and 1368 residual evaluations, all agree | `logs/crosscheck_followup.log` |
| D4 strip controls (`vd_controls.py`) | 12/12 pass | `logs/d4_followup_regression.log` |
| Quarantine scan | PASS; 51 .py and 330 text files, 0 findings, both planted controls fire | - |

The scan reports 8 report-only drift literals in this stream. They are the state coordinates 3/2, 5/3 and 7/3, a
delta step, and `sqrt(2.0)`; none of them is a drift.

**Ledger:** 29 streamD lines, all NONTARGET_DRIFT_VALIDATION or INFRASTRUCTURE, 0 target evaluations and no
LEAK_FLAG. **OV:** `git status` is empty. **Stream A0:** read only; nothing was written there.

## 14. Open issues (follow-up)

1. **D7: no independent verdict for C1b certificates of degree >= 8.** Section 11 gives the diagnosis. Closing this
   needs a higher-order local enclosure in `vd_verify`.
2. **C1b at e = 1, d = 10 and d = 12** returned SCALING_RULE_INAPPLICABLE in the producer (`certify_degree`). Stream
   A0 did store e = 1, d = 10/12 certificates made by its own W-only route, and those were not verified here: their
   format is `C1B_PW_W_SUPER`, whose layout I did not read.
3. **Point certificates only.** `vd_pl` checks one exact drift per call, and drift blocks are not supported. The
   rational drifts 11/10 and 27/10 are handled exactly.
4. **SUB direction.** The conclusion E_x[tau] >= W(x) assumes W bounded, which is automatic for P1, and a convergent
   resolvent series. The convergence follows from any verified supersolution at the same drift, and every SUB drift
   has a verified SUPER certificate here.
5. **Common-mode assumptions.** The kernel model and the P1 layout are shared with C2b by construction. The kink/Psi
   decomposition is my own derivation, but it is mathematically the same object the original C2b sums (section 12).
   The generic evaluator `vd_point.PL` is the independent guard for it.

## 15. Files added in the follow-up

| path | role |
|---|---|
| `vd_pl.py` | D6 P1 verifier: adapter, kink/Psi kernel, cell branch and bound, `verify_pl`, exact W(a) |
| `vd_point.py` | now also evaluates P1 nodal W pointwise (`PL`: barycentric cell search, generic breakpoints) |
| `vd_d6_verify_pl.py` | D6(a) runner |
| `vd_pl_controls.py` | D6(b) controls |
| `vd_pl_crosscheck.py` | agreement of the two PL evaluators |
| `vd_d7_cost.py`, `vd_d7_probe.py` | D7 |
| `certs/CERT_e3_1_d8.json`, `CERT_e3_1_d10.json`, `CERT_e3_1_d12.json`, `CERT_e1_1_d8.json` | new C1b certificates, recorded in the manifest |
| `results/D6_VERIFY_PL.json`, `D6_PL_CONTROLS.json`, `D6_PL_CROSSCHECK.json`, `D7_PROBE.json` | new results |
| `results/D2_INDEPENDENCE.json`, `CROSSCHECK.json`, `D4_CONTROLS.json` | re-run |
| `logs/` | produce_run4_highdeg, d6_run_N10_20/N40/N80, d6_controls_final, d6_pl_crosscheck, d7_run1_aborted, d7_run2, d7_probe, crosscheck_followup, d4_followup_regression, independence_followup, sources_followup.sha256 |
