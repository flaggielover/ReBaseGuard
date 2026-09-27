# Stream C1b PROGRESS (RLR certificate on real CUSUM kernel, NON-TARGET drifts only)

Directory: NS/streams/C_308/LR/cusum/  Validation prefix: C1B_

## Log
- [start] skeletons created. Reading preamble inputs next.
- [read] PREAMBLE, README, quarantine + amendment 1, ov_quarantine, THEOREM_LR (all), C1LR_ROUTE_SUMMARY, lr_fsm.rlr_and_dv,
  THEOREM_AD §0-§4 + §8, c11_certifier.py / c11_common.py / c7_gaussian.py (all three: definitions only, no side effects
  at import; c11_common defines git helpers but calls nothing at import).

## DECLARATIONS (written BEFORE any computation; binding for this stream)

D0. Drifts. Point drifts, in this order: e = 1/2, 1/4, 1 (then 3, 0 if time permits). Block (if time permits):
    [1/2, 1/2 + 1/40]. Every entry point calls Q.guard_drift. Nothing in [1.2, 2.6] or mirror. No cell id is used anywhere.

D1. What is certified (math). Reachable set R = {0<=p,m<=5 : p=0 or m=0 or p+m<=4} (C11 spec, re-derived: interior
    states have p+m <= 4). Taboo kernel K^_e (window [m-C, C-p] minus atom window [m-K, K-p]); score S = -(z+e).
    Every certified quantity is reduced to: (a) supersolution inequalities w >= 1 + K w on R (whole and taboo), and
    (b) LINEAR functionals (G^ f)(a) of triangular systems X_k = G^(f_k + sum_i Op_ki X_i), certified by polynomial
    candidates with a rigorous two-sided sup-norm enclosure of the residual on R and the tame-error composition
    |X_k(a) - X~_k(a)| <= tau (sum_i ||Op_ki|| ||E_i|| + ||r_k||),  ||E_k|| <= C_T (same bracket).
    Constants: L1 <= sqrt(tau_a,up * S2^_up)  (THEOREM_LR §cert (i'): exact value of the global-c full quadratic
    certificate; equivalently |mu| <= c/2 + mu^2/(2c) summed), S2^ = E_a sum_{n<sigma} M_n^2 = beta2(a) with
    beta0 = G^1, beta1 = G^ K^(1) beta0, beta2 = G^(K^(2) beta0 + 2 K^(1) beta1);
    L2 <= S2^ + T_N, T_N = E_a sum_{n<sigma} n = (G^ beta0)(a) - tau_a   (§cert (ii-a) triangle);
    D = (G^ h1)(a), D' via d' = G^(K^' d + h1'), D'' via d'' = G^(K^'' d + 2K^' d' + h1'') (THEOREM_AD §8);
    D_lo = max(tame lower bound of d(a), tau_a,lo / A-bar);  A-bar = W(a) for a whole-kernel supersolution W.
    RLR (LR-3): rho_j = L_j,up / tau_a,lo;  A1 = A_eff(rho1 + delta1), A2 = A_eff(rho2 + 2 rho1 delta1 + 2 delta1^2 + delta2)
    and also the non-ratio form L_j,up / D_lo (+ same D terms); report the smaller (both valid, §6).
    Dv' r2 from the SAME certified (A-bar, tau, C_T, D_lo, D1, D2) with kappa1 = sqrt(2/pi), kappa2 = 4 phi(1) (Lemma K).
    Operator norms used in the tame chain: ||K^(1)|| <= sqrt(2/pi), ||K^(2)|| <= 1, ||K^''|| <= 4 phi(1) (Lemma K).
    Statement type: POINTWISE at each declared e (block form only if the block step is reached).

D2. Arithmetic. Exact rationals (fractions) for all polynomial algebra; phi, Phi at rational points by own integer
    fixed-point series (2^-160 grid) with proved remainders, outward rounded; cross-checked against c7_gaussian at
    declared points. Box enclosure: Taylor model of order KT = 10 at each box centre (exact Taylor coefficients of
    phi/Phi via Hermite polynomials; Lagrange remainder with sup|phi^(n)| <= E|Y|^n / sqrt(2 pi)), polynomial range
    bounded by |c_0| + sum |c_alpha| r^alpha. Cover: squares of side 1/4 on [0,4]^2 meeting the triangle
    p+m<=4 plus 1-D segments p in [4,5] (m=0) and m in [4,5] (p=0), each box checked with the region-I form
    (p+m<=1, atom window present) and/or region-II form (p+m>=1) according to which regions it meets.
    Adaptive rule (declared): a box whose enclosure fails the decision (supersolution: lower bound < 0; sup-norm:
    |bound| > 1.25 x max |centre value| over all boxes) is bisected, up to 4 extra levels.

D3. Candidate family ladder (declared): P_d = bivariate polynomials of total degree d in the Chebyshev basis
    T_i(2p/5-1) T_j(2m/5-1), i+j <= d, with d in {6, 8, 10, 12}. Candidate generation (UNTRUSTED float): least-squares
    collocation of the residual (I - K^)X - F on the declared sample set S = {(i/10, j/10): i,j>=0, i+j<=40} union
    {(p,0),(0,p): p = 4 + k/20, k=1..20}; K^ by composite Gauss-Legendre quadrature (10 nodes per unit sub-interval);
    Householder QR. Coefficients rounded to floats (exact dyadics) -> exact rational candidate.
    Scaling rules (declared): supersolutions w_T, W: w = (1+eta) w~ with eta = -r_lo/(1+r_lo) (r_lo = certified lower
    bound of w~ - 1 - K w~ on R, must be > -1; eta := 0 if r_lo >= 0), rounded UP to a multiple of 2^-20; also
    require min_R w~ >= 0. Linear functionals: no scaling, tame-error composition (D1).
    Reported certified value per drift = min over the ladder of the per-rung certified bound (every rung is an
    independently valid certificate; selection uses only certified values at that non-target drift).

D4. Negative controls (declared): (N1) planted non-supersolution: w_T scaled by (1 - 2^-6) must be rejected by the
    supersolution checker (lower bound < 0 AND an exact pointwise centre value < 0 found); (N2) sign-flipped score:
    K^(1) implemented with weight +(z+e) must fail the finite-difference test [K^_{e+h} w - K^_{e-h} w]/(2h) vs K^(1)_e w
    at declared points (h = 2^-12), while the correct sign passes within the proved Taylor bound (h^2/6) sup|d^3/de^3|;
    (N3) mis-specified window: a kernel with the atom window NOT removed (or window [m-C, C-p] shifted by 1/8) must
    fail the mass-balance identity K^1 + k_a + h1 = 1 at declared points and the quadrature cross-check.
D5. Non-certified context (declared): Monte Carlo of L1 = E_a sum_{n<sigma}|M_n|, L2, tau_a, S2^, D at each certified
    drift, N = 200000 excursions, seed 12345; plus float value-iteration values. Labelled NON-CERTIFIED.
- [code] c1b_gauss.py: rigorous phi/Phi (integer fixed point 2^-160, proved series remainders). Selftest PASS; intervals
  intersect c7_gaussian's at 5 declared points (1/3, -7/4, 5/2, -11/2, 9) -> independent-implementation agreement.
- [design] Reduction used: kernel closed form. For p+m>=1 (region II) the window splits at K-p < m-K into three pieces
  (p'=0 | both>0 | m'=0); for p+m<=1 (region I) into two pieces plus the atom window [m-K, K-p]. With u = z+e each
  piece is poly(u; p,m,e) phi(u), so K^(j) w = sum over the 4 boundaries l1=C-p+e, l2=K-p+e, l3=m-K+e, l4=m-C+e of
  poly*phi(l) + poly*Phi(l) (M_n(A,B) = G_n(A)phi(A) - G_n(B)phi(B) + (n-1)!![Phi(B)-Phi(A)] for n even).
- [code] c1b_kernel.py (exact G-forms, point eval, Taylor-model box enclosure, cover of R) + c1b_float.py (untrusted
  quadrature/LS). Cross-check exact closed form vs independent GL quadrature: random degree-6 w, j = 0,1,2 taboo and
  j = 0 whole, 8 points in both regions, e = 1/2: max |diff| = 1.3e-15. Mass balance K^1 + k_a + h1 = 1 holds exactly
  (symbolic telescoping). One degree-12 box enclosure ~0.13 s.
- [explore, NON-CERTIFIED float, e = 1/2, d = 8] tau_a ~ 8.84, S2^ ~ 56.4, T_N ~ 98.3, D ~ 0.2327, D' ~ 0.980, D'' ~ 1.071,
  whole ARL W(a) ~ 37.9985 vs tau_a/D ~ 37.9984 (Lemma SM(d) identity reproduced by independent float solves).

## DECLARATION D6 (before any certification run): explicit THEOREM_LR (i') excursion certificate for L1
  w(x,mu) = a + b1 mu + b2 mu^2 with global c := dyadic(2^-10) rounding of sqrt(b~2(a)/b~0(a)) (float candidates),
  b2 = beta w_T, beta = (1+s)/(2c), s in {2^-6, 2^-4, 2^-2} (declared ladder, min certified value reported),
  b1 = 2 beta (1+eta_T) b~1, a = (c/2) b~0 + beta (1+eta_T) b~2 + lam w_T with lam the smallest dyadic (2^-20) making
  C_x >= B_x^2/(4 A_x) on every box (A_x >= s/(2c) from w_T - K^w_T >= 1). Checker: per box of the cover,
  A_lo > 0, C_lo >= 0, max(B_lo^2, B_hi^2) <= 4 A_lo C_lo.  L1 <= a(atom).  Negative control N4: a' = a - kappa with
  kappa = 2 C(atom)/(k_a(atom)+h1(atom)) (so C'(atom) = -C(atom) < 0 exactly) must be rejected.
  L1 reported = min(explicit certificate, sqrt(tau_a,up * S2^_up)) (both valid).
- [test run, e = 1/2, d = 6, NOT a ladder run] pipeline end-to-end OK (~100 s + 3 quad checks). All three (i') L1
  certificates PASS the checker; L1 <= 55.57 (explicit certificate) vs sqrt(tau_up*S2_up) = 327 (tame chain):
  the tame chain amplifies residuals by C_T^2 (S2_up = 7414 vs float 56.4). LESSON: use ONE-SIDED certificates
  wherever the functional is positive. D2 (tame, two-sided) = 229 at d=6: needs smaller residuals (higher degree).
  Enclosure cost ~10 s/residual at d=6; projected ~60 s at d=12 -> implementing exact dyadic-integer Taylor models.

## DECLARATION D7 (before the ladder runs; amends D1/D2, stricter or equal, no target information involved)
  (a) S2^ upper bound by the ONE-SIDED quadratic supersolution (THEOREM_LR §cert (i') form with forcing mu^2):
      b2 = (1+s) w_T, b1 = 2(1+s)(1+eta_T) b~1, a = (1+s)(1+eta_T) b~2 + lam w_T, s in {2^-6, 2^-4, 2^-2},
      checked by the same A/B/C per-box checker (A = b2 - 1 - K^b2); S2^ <= a(atom). Tame bound kept; min reported.
  (b) T_N upper bound one-sided: u = (1+eta_T) x~T + lam w_T with u - w_T - K^u >= 0 checked on R;
      T_N <= u(atom) - tau_a,lo.  Tame bound kept; min reported.
  (c) tau_a lower bound also by the subsolution v = (1-zeta) b~0, zeta = r_hi/(1+r_hi) (dyadic up); Lambda lower
      bound likewise from W~; max(tame, subsolution) reported.
  (d) Exact arithmetic change only: candidate monomial coefficients are rounded to the 2^-200 grid (candidate is
      then that dyadic polynomial; the family is unchanged), so every G-form coefficient is dyadic and the box
      Taylor models run in exact scaled integers (identical mathematics to D2; cross-checked against the
      Fraction implementation on declared boxes).
  (e) Block (if reached): [1/2, 17/32] (dyadic width 1/32, replaces the non-dyadic 1/40 example).
- [ladder P_d running, e = 1/2 and 1/4] residual sup of b~0 stagnates with degree (e=1/2: d6 -0.43, d8 -0.354,
  d10 -0.345; d~0: 1.16e-2, 9.3e-3, 9.1e-3). Diagnosis (math, not target-driven): G^1, d = G^h1 etc. have gradient
  jumps along p+m = 1 (the atom window closes there: boundary term w(a) phi(K-p+e) present only for p+m<1), and the
  interior piece B (images on p'+m' = p+m-1) propagates the kink to p+m = 2, 3, 4 with geometric damping (mass of
  piece B). A global polynomial converges only O(1/d) at a kink. The functions are smooth on each strip
  {k-1 <= p+m <= k}.

## DECLARATION D8 (before any run of it): strip-piecewise family (extends D3, same scaling rules D3/D6/D7)
  PW_d = {w : w restricted to strip s is a polynomial of total degree <= d in the D3 Chebyshev basis}, strips
  s1 = [0,1], s2 = (1,2], s3 = (2,3], s4 = (3,5] in t = p+m (right-closed; the atom is in s1). Candidates may be
  discontinuous across strip lines (a supersolution need not be continuous; K^w is continuous in x anyway).
  Kernel closed form per x-region J = [J-1, J] of p+m (J = 1..5): image strips split the axis pieces at
  u = l3 - b and u = l2 + b, b in {1,2,3} (new boundary forms), piece B uses the strip of p+m-1.
  Every inequality is checked on each closed x-region with that region's form (a box meeting several regions is
  checked with each). Ladder d in {4, 6, 8}. LS samples: D3 set S plus {(i/20, j/20): i+j <= 20}.
  Plain P_d ladder results are kept as the baseline (valid certificates, kink-limited).
- [plain P_d ladder DONE e=1/2, 1/4] (C1B_POINT_e1_2.json, C1B_POINT_e1_4.json; producer c1b_certify.py). All rungs
  CERTIFIED. e=1/2 d=12: tau 12.01, C_T 27.50, A-bar 37.997, D_lo 0.2015, D1 3.21, D2 102, L1 38.0, L2 316 —
  kink-limited (float: tau_a 8.84, D' 0.98, D'' 1.07).
- [PW test, e=1/2, d=4 (test run, copied to logs/test_pw_e1_2_d4.json)] strip-piecewise family: tau 9.59, C_T 18.5,
  D_lo 0.2249, D1 1.20, D2 8.10, L1 26.35, L2 193; exact pw kernel vs split quadrature 4e-16 (13 pts, j=0,1,2);
  BW=[0,5] reproduces the plain closed form exactly. Launched PW ladder {4,6,8} at e = 1/2 and 1/4.
- [05:13 resume after coordinator notice (API rate limit)] Found the two PW ladder processes (e=1/2, e=1/4; started
  04:50, perl alarm cap 3500 s) STILL RUNNING (ps: pids 15015, 15017), at d=8 (quad checks ~2900 boxes each);
  d=4 and d=6 CERTIFIED at both drifts. Letting them finish within their cap (2 concurrent = limit).
  Coordinator note acknowledged: no transfer of any value into [1.2, 2.6] via Theorem M monotonicity will be
  derived or stated; no juxtaposition with tail numbers (S8).

## DECLARATION D9 (05:20, before any run of it; fairness to the Dv' comparator)
  The D2 adaptive tolerance (1.25 x centre extreme) lets sup_R w_T = C_T be over-estimated by up to 25%; C_T enters
  Dv' (kappa1 C_T, kappa1^2 C_T^2) but not RLR, so a loose C_T would bias the comparison TOWARD RLR. Runs flagged
  --tight-ct (tag PW9) enclose sup_R w_T with tol 1 + 2^-7 and 6 extra levels. Reported comparisons use PW9 runs
  where available; earlier PW runs are kept (valid but with a possibly loose C_T) and are marked so.
- [05:17] PW ladder DONE e=1/2 and e=1/4 (C1B_PW_POINT_e1_2.json, _e1_4.json; d=4,6,8 all CERTIFIED; C_T of these
  runs may be loose, see D9). MC DONE (C1B_MC.json, NON-CERTIFIED). e=1/2 MC: sigma 8.888+-0.026, L1 16.09, L2 84.1,
  S2 58.0, T_N 101.0, D 0.234, Lambda 37.98 -> all certified bounds consistent.
- [negctl run 1] N2 (score FD: true sign passes 6/6, flipped detected 6/6 for both orders), N3 (atom window not
  removed and window shift both detected; correct kernel passes), N4 (planted L1 certificate rejected, 832 pointwise
  violations), N4b (halved T_N certificate rejected) all OK.  **N1 FAILED AS A CONTROL (design error, preserved in
  logs/C1B_NEGCTL_run1_N1_design_error.json):** w_T*(1-2^-6) is NOT an invalid certificate — w_T carries residual
  slack ~0.03 from enclosure looseness + dyadic rounding, so the scaled function is still a genuine supersolution
  (residual lower bound +0.0079) and the checker rightly ACCEPTED it. Same failure pattern as C1a's "slack = 0".
## DECLARATION D10 (before rerun): guaranteed-invalid replacement controls for N1
  N1' : f = 1/2 (f w_T - 1 - K^(f w_T) = f V - 1 < 0 wherever V = w_T - K^w_T < 2; V(atom) checked exactly).
  N1'': tight: x* = box centre of the certified cover with the smallest exact residual rho* of w_T;
        f = floor_{2^-20}(1/(1+rho*)) - 2^-20, so the residual of f w_T at x* is exactly negative.
  Both must be rejected by check_supersolution WITH an exact pointwise centre violation.
- [05:18] launched PW9 (D9 tight C_T): e = 1 {4,6,8}; e = 1/2 {4,6}.
- [05:27] PW9 e=1/2 {4,6} DONE: tight C_T (D9) = 18.549 (d4), 17.667 (d6) — IDENTICAL to the D2-rule values: the
  sup of w_T sits at the axis end (0,5) where boxes are 1-D and the range bound is already tight. D9 therefore
  changes nothing; PW and PW9 records are pooled in the report (all valid). d=8's larger C_T (20.52) is a genuine
  property of that rung's polynomial (endpoint overshoot), not enclosure slack; the ladder minimum takes the best rung.
- [05:31 negctl run 2, C1B_NEGCTL.json] ALL CONTROLS DETECTED: N1' (f=1/2) rejected with pointwise violation;
  N1'' tight (x*=(3.625,0.375), rho*=0.0345, f=0.96666) exact residual at x* = -1.17e-6 < 0 and the checker rejects
  (lower bound -0.0103, pointwise centre violation found); N2 true sign 6/6, flipped 6/6 (both orders); N3 all three;
  N4 planted L1 certificate rejected (832 pointwise violations); N4b rejected. N1 (declared) kept as a preserved design
  error: its acceptance is correct behaviour. Launched PW9 e = 3 {4,6,8}.
- quarantine static scan (code/ov_quarantine.py --scan): 9/9 of this stream's files scanned, 0 findings in them;
  scan negative control detected; the only finding is another stream's validation/build_validation_index.py (UNPARSEABLE).
- [05:40] PW9 e=1 {4,6,8} DONE (d8: tau 6.739, C_T 9.867, A-bar 10.378, D_lo 0.6324, D1 0.634, D2 2.39, L1 16.95,
  L2 77.3); PW9 e=3 {4,6,8} DONE (tau 2.558, A-bar 2.574, D_lo 0.99396, L1 2.69). Launched PW9 e=0 {4,6,8} and the
  declared block [1/2, 17/32] with the e-FREE family PW_4 (THEOREM_LR §6 U1 form: one candidate for the whole block;
  residuals enclosed over R x block with 3-D Taylor models).
- [05:45] block-path spot check (scratchpad script, not a deliverable): on the 3-D box p in [4.75,5], m=0,
  e in [1/2, 17/32] the integer and Fraction Taylor models agree exactly ([-0.07058, +0.06469]) and contain the exact
  pointwise residuals at 9 grid points (min -0.06942 at (5,0,17/32)); with e fixed the 3-variable and substituted
  forms give identical enclosures. (I first misread an e=0 log line as a block line and suspected an unsound block
  enclosure; the check shows the block path is sound — the misreading is recorded here for transparency.)
- [05:46] report (c1b_report.py PW PW9 -> C1B_SUMMARY_PW_PW9.json): MC consistency PASS at e = 1/4, 1/2, 1, 3.
- [06:04] e=0 PW9 d=4,6 CERTIFIED (d6: tau 6.833, A-bar 482.6, D_lo 0.01386, D1 0.0184, L1 25.8); d=8 running.
- [06:04] BLOCK run (declared settings) STOPPED BY ME after 24 min wall (> preamble ~20 min cap): 3-D adaptive
  refinement exploded (d~0 residual enclosure alone 631 s, 28509 boxes). Partial log kept:
  logs/pw9_block_killed_at_24min.log (residual enclosures over R x [1/2,17/32]: b0 [-0.080, 0.094], b1 [-0.146, 0.155],
  b2 [-0.656, 0.687], xT [-1.06, 1.24], d0 [-2.2e-3, 2.5e-3], d1 [-1.05e-2, 9.7e-3] -- all ~1-3x the point residuals
  at e = 1/2, as expected from the first-order e-variation of an e-free candidate).
## DECLARATION D11 (before the relaunch): light block settings to fit the cap
  flag --block-light: residual/range enclosures use 2 extra refinement levels (rigour unchanged, looser);
  explicit (i') certificates use the single rung s = 2^-4. Same block [1/2, 17/32], family PW_4, e-free candidate.
- [06:10] e=0 PW9 {4,6,8} DONE (d8: A-bar 467.49, D_lo 0.01433, D1 0.0042 [true D' = 0 by symmetry], L1 26.2).
  BLOCK (D11 light) [1/2, 17/32] CERTIFIED in 246 s (C1B_PW9_BLOCK_1_2__17_32.json): tau 9.808, C_T 18.79, A-bar 41.74,
  D_lo 0.2204, D1 1.53, D2 17.9, L1 29.23, L2 214.8; A1 RLR 422 vs Dv' 915 (2.17x), A2 10210 vs 35593 (3.49x);
  MC consistent at both endpoints (MC re-run incl. e = 17/32).
- [06:12] report C1B_SUMMARY_PW_PW9.json regenerated (5 point drifts + block; MC checks all PASS). Final quarantine
  scan PASS (0 findings in 9 stream files). Ledger: 22 c1b entries, all NONTARGET_DRIFT_VALIDATION, cells [] , no
  LEAK_FLAG (one retroactive entry for scratchpad test scripts c1b_t1..t6, drifts 1/2 and [1/2,17/32] only).
- [06:13] C1B_ROUTE_SUMMARY.md complete. Route state VALIDATED_NON_TARGET, not FREEZE_READY; CLOSURE-ONLY (floor r2).
