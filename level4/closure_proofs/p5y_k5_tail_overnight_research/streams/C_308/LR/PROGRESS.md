# STREAM C1a (LR / score representation) — PROGRESS

Stream directory: NS/streams/C_308/LR/ ; validation prefix C1LR_.
Scope: THEORY + EXACT SYNTHETIC VALIDATION ONLY. No CUSUM target cells, no drift in [1.2,2.6] or mirror.

## Log
- [start] skeletons created (THEOREM_LR.md, C1LR_ROUTE_SUMMARY.md, PROGRESS.md).
- [read] PREAMBLE, IDEA_LR_SCORE_CONSTANTS.md, pm_probe_synthetic.py, ov_fixtures.py, ov_quarantine.py (scan flags int literals 305..309 in any NS .py -> avoid them), THEOREM_AD §1-4 (Lemma K/T/SM/Dv/Dv'), graph_B §a.2.
- [plan / key structural observations, written before any computation]
  1. Proof of the LR identity via the operator series (R K' R = sum_n sum_k K^{k-1} K' K^{n-k}) + Markov property; absolute
     convergence is exactly the positive majorant (R|K'|R|f|)(a) -> chain true <= LR <= PM falls out of the proof.
  2. Two score levels: noise-level (CUSUM: S=-(Z+e)) and state-level (finite fixtures: K1/K0). State-level =
     conditional expectation of noise-level given the X path -> LR_state <= LR_noise (Jensen). For CUSUM they differ only
     on transitions into the atom window.
  3. HEURISTIC/EXAMPLE: plain whole-kernel LR is O(Lambda^{3/2}) for A1 and O(Lambda^2) for A2 while true is
     O(Lambda polylog) -> plain LR can LOSE to Dv' when Lambda >> C_T. Explicit one-state example planned (noise-level).
  4. Fix = REGENERATIVE LR (RLR): apply LR only inside the taboo excursion (G^ = (I-K^)^{-1}) and keep the
     Sherman-Morrison quotient of Dv'. Then rho1 := sup L1/tau_a <= kappa1*C_T and rho2 <= 2kappa1^2C_T^2+kappa2C_T, so
     RLR dominates Dv' term by term with the same (Abar, tau, D_lo, delta1, delta2) inputs. Must be proved in §5.
  5. Certificates: minimal nonnegative solution argument (w >= |mu| + P w, w >= 0 or polynomial growth + geometric tail).
     Quadratic delta-version (as specified), full quadratic with linear term (exact = sqrt(Lambda*S2) at optimal c),
     per-(n,y) Cauchy-Schwarz finite horizon + certified tail (alternative iii). A2: triangle bound E sum M^2 + E sum |N|
     (linear), quartic global CS.
- [declared validation rule, BEFORE running] Set V1: ov_fixtures.random_family(n=6+seed%4, seed, e_range=(0,1/4),
  kill=1/20), seeds 1..12, evaluation drift e=1/8 (synthetic). Set V2: same with kill=1/5 (fixture default), seeds 1..12.
  Block-uniformity demo (if time): block [0,1/4] on V1 seeds 1..8. No selection by outcome; all seeds reported.
- [done] THEOREM_LR §0-§4 written (setting, Theorem LR-1 with proof via Neumann series, Lemma TL, CUSUM specialisation, Corollary LR-2).
- [done] THEOREM_LR §5 (Prop LR-4 chain, E1/E2 examples, heuristic orders, Theorem LR-3 RLR dominating Dv').
- [done] THEOREM_LR §6 (block uniformity: e-free certificate U1, sign subtlety, RLR ratio forms) and §cert
  (Lemma C0, Prop C1 delta-cert, (i') full quadratic + per-state CS, (ii) A2 triangle/quartic, (iii) finite horizon +
  certified tail, (iv) Holder lower bound, regenerative versions, cost).
- [declared BEFORE running, additional] Example E2 ladder: two-state chain a->a (1-eps)(1+e)/2, a->b (1-eps)(1-e)/2,
  b->a (1-eps), e=0, eps in {1/10,1/20,1/40,1/80,1/160}. Example E1d: one-state chain with 3-point noise lifted to a
  3-copy state chain, same eps ladder. Certificate grids: c in {2^k/8 : k=0..6} * c_hat (c_hat = dyadic approx of
  sqrt(S2/Lambda)), delta in {1/4,1/2,1,2} * 1/(2c). Horizons: head H=12 for (iii); lower bound H_LB=80 (fixtures).
- [next] writing lr_fsm.py incrementally.
- [smoke] lr_fsm.py seed1 H_lb=20: all identities exact, fd/path-enum match, neg controls detected, chains hold; 0.6 s. Finding: exact LR lower bound (0.72) already ~3x above true A1 (0.24) -> most cancellation is BETWEEN paths, LR recovers only PM/LR.
- [declared BEFORE running examples] E1d/E2 lower-bound horizon H = 4/eps (i.e. 4*Lambda-scale); certificates as in fixtures.
- [running] --sets (bg, cap 1200s) and --examples (bg, cap 1200s).
- [result, preserved] --examples done (validation/C1LR_EXAMPLES.json). E2: LR lower bound / Dv'(exact) = 1.33, 1.75, 2.40,
  3.34, 4.69 on the ladder (LB ~ 0.40 Lambda^1.5; Dv' ~ 1.07 Lambda; RLR ~ 0.66 Lambda < Dv'). E1d AS DECLARED shows NO
  separation (LB/Dv' = 1.12, 0.91, 0.82, 0.80, 0.82): design error on my part -- its killing derivative is O(1) so
  delta1 = |D'|/D ~ Lambda/6 grows linearly, and true = Dv' ~ Lambda^2 dominates Lambda^1.5. The Gaussian E1 has
  delta1 ~ sqrt(2 log Lambda). Theory predicts ratio ~ sqrt(Lambda)/delta1, so no separation is the CORRECT outcome
  for that family. Preserved as-is.
- [declared BEFORE running] E1d' (faithful analogue): q1=(1-eps)/3+e/3, q2=(1-eps)/3-e/3, q3=(1-eps)/3-eps*e, so
  D = eps(1+e), delta1 = 1 at e=0; same eps ladder, H=4/eps.
- [result] --sets done -> validation/C1LR_FSM_VALIDATION.json (V1 kill=1/20: Lambda 4.1-8.4; V2 kill=1/5: Lambda 2.7-4.0;
  12+12 seeds, ~5 s each). ALL 24: identities exact (1st+2nd order), fd + path-enumeration independent checks match,
  sign-flip / t-flip negative controls detected [CORRECTED per REVIEW_GLOBAL_INTEGRITY_R1 C-10: the t-flip
  control was class (d) -- a bare != on U20-U01 that never ran moment_totals -- and is withdrawn; see the R1-repair
  entry below for the in-solver replacement], all certificates pass the exact checker, all 4 planted
  non-supersolutions rejected (whole + excursion), regenerative identities exact, PMhat <= Dv' factor.
  Chain true <= LR_cert <= PM <= G holds 24/24 for A1 and A2.
  A1 ratios (V1 median): LR_lower/true 1.99, LR_cert/true 3.21, PM/true 7.79, Dv'(exact inputs)/true 6.52,
  RLR/true 2.26, Dv'/RLR 2.39 (range 1.83-2.99). LR_cert < Dv' 12/12 at these small Lambda.
  A2 (V1 median): LR_cert/true 4.67, PM/true 13.2, Dv'/true 11.9, RLR/true 4.19, Dv'/RLR 2.42.
  Finding: the exact LR itself sits ~2x (median) above the true functional norm -> half of the slack is
  between-path cancellation that NO |M_n|-type bound can recover.
- [result] E1d' (declared): Dv' = true = Lambda exactly; noise-LR lower bound ~0.40 Lambda^1.5; LB/Dv' reaches 5.10 at
  Lambda=160, growing like sqrt(Lambda) -> Example E1 separation CONFIRMED on the faithful analogue.
- [declared BEFORE running] block demo (item e): V1 seeds 1..8, block [0,1/4] split into m=8 sub-intervals, e-free
  full-quadratic certificate (per-state c from midpoint 1/8, b2 inflation eta=1/100, b1 = midpoint exact, slack from
  worst |B|), exact interval-Horner enclosures; pointwise grid e=k/32 (k=0..8) with LB horizon 60; negative control:
  same certificate with slack=0 must be rejected.
- [result, preserved] --block baseline (eta=1/100, m=8): e-free certificates PASS the interval checker on all seeds run,
  slack=0 negative control rejected, LB(e) <= block bound on the grid; but overhead block/max-pointwise-cert = 1.55-3.43x
  and seed 1 block LR (4.15) > block PM (3.18) -> crude construction (tiny A = eta/(2c) forces a large discriminant slack;
  K_up envelope inflates Lambda).
- [declared BEFORE running] block variants: eta in {1/100, 1/10, 1/2, 2} x m in {8, 32}; report all; block value = min
  over checker-passing variants (all are valid certificates); diagnostic Lambda_up = (R_up 1)(a) vs max_grid Lambda(e).
- [result, preserved] --block-variants: best (m=32, eta=1/10 on 7/8 seeds) overhead 1.44-1.94x over max pointwise cert;
  Lambda envelope inflation 1.05-1.10; chain block_LR <= block_PM <= block_G holds 8/8; all 64 variants pass checker.
  The slack=0 control was NOT a guaranteed-invalid plant: it passed for seed 7 with eta=2 (m=8 and m=32), legitimately
  (the sup-envelope forcing already carries slack). My control design error; preserved.
- [declared BEFORE running] guaranteed-invalid block control: best variant scaled by s = maxLB/(2*value) (value < LB <=
  LR(e) for some e, so it cannot be a valid certificate) must be rejected, all 8 seeds.
- [S8 notice received] grepped all C1a files: no committed tail-cell constant/share/factor/margin anywhere, no product of
  a route factor with one. Renamed my certificate ids C0-C4 -> CT0-CT4 in the route summary (avoid "C3" ambiguity).
  No other correction needed.
- [result] --block-negctl: guaranteed-invalid scaled certificate rejected 8/8. Quarantine scan: 0 findings in C1a files
  (one finding in another stream's file, not mine); ledger 6 lr_fsm entries (one per flag run; --one smoke runs did not log), 0 LEAK_FLAG.
- [done] THEOREM_LR §7 filled, route summary written.
- [R1 repair, 2026-09-28, per NS/reviews/REVIEW_GLOBAL_INTEGRITY_R1.md C-10/C-11, F7, F11, F18] lr_fsm.py changed:
  (1) withdrew class-(d) `neg_t_flip`; added in-solver hooks to Chain.moment_totals (tsign, plant) and shared
  comparators identity1_holds/identity2_holds; new controls `neg2_plant_detected` (+1e-9 at the atom of the (0,1) rhs,
  guaranteed since R[a][a] >= 1) and `neg2_tflip_in_solver_detected` (t sign flipped inside the solver, fire rate
  reported); (2) A<0 plant for check_quadratic_cert (A = -1/(4c), B = C = 0 exactly: only the A>=0 conjunct can reject),
  plus a mutant-checker demo (A conjunct dropped must accept it); (5) Q.guard_drift in identity_checks,
  block_enclosures, build_block_cert. Pre-repair copy kept in SCR/lr_fsm_pre_r1repair.py. Re-running all flags.
- [R1 repair result] re-ran --sets, --examples, --example-e1dp, --block, --block-variants, --block-negctl; all three
  C1LR_*.json regenerated (06:25-06:27). Headline numbers unchanged (Dv'/RLR, E2/E1d' ratios, block overheads identical).
  New controls: identity-1 sign flip 24/24; neg2_plant 24/24 (+5/5 E2); neg2_tflip_in_solver 24/24 (+5/5 E2; class (b));
  A<0 plant rejected 24/24 whole + 24/24 excursion, mutant checker (no A conjunct) accepts it 24/24/24 -> A conjunct
  covered. Chains 24/24, all certificates pass, block guaranteed-invalid control 8/8. Ledger: 12 lr_fsm entries, 0
  LEAK_FLAG. Docs corrected: THEOREM_LR:3 + §7, C1LR summary status/controls/G6, this log (C-10 note). C-11
  (`rebuilt_matches_and_passes`) is a consistency check, not a control; it is not cited as evidence. cusum/ untouched.
