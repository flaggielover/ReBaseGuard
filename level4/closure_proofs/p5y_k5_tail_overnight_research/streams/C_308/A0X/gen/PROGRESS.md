# STREAM C2b PROGRESS (gen/)

Stream: C2b -- general, cell-independent operator-tuple certification strategy (brief s17) + A0 tightness.
Directory: NS/streams/C_308/A0X/gen/ ; validation prefix C2B_.

## Log
- step 1: read PREAMBLE; created gen/ with skeletons (PROGRESS.md, STRATEGY.md, C2B_ROUTE_SUMMARY.md, A0_TIGHTNESS.md).
- step 2: read quarantine (README, TARGET_QUARANTINE, AMENDMENT_1: drift band [6/5,13/5] refused), ov_quarantine.py,
  c11_certifier.py (model docstring confirmed: window z in [m-11/2, 11/2-p], next (max(0,p+z-1/2), max(0,m-z-1/2)),
  z+e~N(0,1); R = {0<=p,m<=5, p+m<=4 or p==0 or m==0}), c7_gaussian.py (pure, fractions only), c11_common.py
  (module constants + functions only; no side effects at import), SCR/graph_B_operators.md.
- DESIGN DECISION (before any computation): family = P1 (piecewise-linear) on the uniform anti-diagonal triangulation of
  mesh h=1/N; proposal = float Nystrom/product-integration value iteration on the SAME grid (exactly the discrete
  equation of the family); certificate = exact vertex margins (fixed-point integer intervals from c7 enclosures) plus a
  rigorous P1 interpolation-error bound from closed-form Hessian bounds of Psi_w(s,y). Key structural lemma:
  K_e w(p,m) = Psi_w(p+m, p-K-e)  (drift enters only through y = p-K-e) => block-uniform check = pointwise check on
  a widened y-range (lattice-aligned e-steps).
- step 3: c2b_float.py (Nystrom, float) smoke test: Lambda_h(e=1) N10 10.375612 / N20 10.375880; e=0: 462.49 / 464.70
  (ARL0 of two-sided H=5,K=1/2 ~ 465, consistent with textbook); e=3: 2.573390 / 2.573286. ~30 ms per apply at N=20.
- step 4: c2b_exact.py written (exact P1 vertex kernel + Hessian bounds + certify). Cross-check vs C11 kernel_apply
  (independent code) for w = 20 - (5/4) m at N=10, e=1, 15 nodes: all enclosures overlap, widths < 1e-33; taboo
  difference = atom mass * w(a) exactly where s<1 and 0 elsewhere.
- S8 acknowledged (coordinator, mid-task): no tightness figure / ratio will be placed next to or combined with any
  committed tail-cell factor, margin or critical value; the 3.06% scale appears only as the brief's stated motivating
  scale. Checked: nothing written so far in gen/ does this (no tail numbers appear in gen/ at all).
- step 5: c2b_pointeval.py (independent float point evaluator of Psi_w at arbitrary (s,y)): agrees with Nystrom at
  nodes to 5e-15 and with brute-force z-quadrature off-node to 5e-9 (N=10, e=1).
- step 6: c2b_checks.py: Hessian-bound FD check (N=10, e=1, 60 cells x 3 pts): whole max |FD|/bound = 0.994 (bound is
  sharp but never exceeded), taboo 0.947; 0 violations; NEGATIVE CONTROL bounds x0.05 -> 501 violations (detected).
  C11 kernel check: 0/28 mismatches; NEGATIVE CONTROL wrong K=0.4 -> 28/28 mismatches (detected).
- step 7: hessian_bounds rewritten for speed (precomputed lattice signs, suffix sums over axis kinks); FD check
  reproduces the old routine's ratios exactly (0.99429/0.94737, 0 violations; control 501) -> same bounds.
- step 8: first end-to-end certificate N=10, e=1 (2 CPU-s): whole Lambda <= 10.442332 (alpha 1.00635, beta 8.6e-4),
  taboo tau_a <= 6.810225, C_T <= 9.940577 (alpha 1.0227). Exact, 0 bumps.
  VALIDATION SET DECLARED BY RULE (before any further run, Q6): pointwise e in {0,1/4,1/2,1,3} x N in {10,20,40}
  x {whole,taboo}, P1; comparator F0 (affine in m) at N=20 for each e; truth = Nystrom N in {10,20,40} + Richardson
  (N=80 where affordable); blocks [e0, e0+W], e0 in {1/2, 1, 3}, W in {1/40,1/20,1/10}, N=40 (and N=20 for
  W in {1/20,1/10}); negative controls at e=1 and e=1/2. No case chosen by similarity to anything.
- step 9: STRATEGY.md sections 0-7 written (fixed before the batch runs). Batches A (truth) and B (pointwise
  certificates) launched in background (capped via perl alarm, nice, 2 processes). c2b_controls.py and
  c2b_report.py written. Partial results (e=1, e=3): all certified; tightness vs Nystrom-Richardson truth:
  e=1 whole 0.64% (N10) / 0.16% (N20) / 0.049% (N40); e=3 whole 0.23/0.054/0.025%; taboo tau_a e=1 2.2/0.55%,
  e=3 0.22/0.075/0.025%. At e=3,N=40 the alpha ladder step 2^-12 (0.0244%) is the binding resolution.
- step 10: quarantine static scan (NS/code/ov_quarantine.py --scan): all 9 gen/ files scanned, 0 findings in gen/,
  planted negative control detected. Added robust-ARL diagnostic (c2b_float.robust) and the A0 floor lemma
  (A0_TIGHTNESS.md s1). Batches C (blocks + F0 comparator) and D (truth grids, robust ARL, controls) queued.
- step 11: controls at e=1, N=10 (results/controls_1_N10.json), all DETECTED: C1 0.97xV_h and 0.999xV_h fail
  certification; C2 10/10 single-node 5% notches fail; C3 sign-flipped drift: flipped certificate valid for K_{-e}
  but below the +e float truth at 430 nodes (worst (5,0): 1.89 vs 9.60); its atom value 10.4136 >= truth 10.3756, so
  an atom-only comparison CANNOT detect a sign flip (p<->m symmetry: Lambda(e)=Lambda(-e)); C4 FD/bound 0.994, 0
  violations, control 501 flagged; C5 C11 kernel 0/28 mismatches, wrong-K 28/28; C6 off-node sampling (1505 points,
  independent float evaluator) min residual of the certified w = +0.0042, control 0.97V min residual -0.032.
  e=1/2 pointwise: whole 1.71/0.43/0.12% (N10/20/40), taboo 3.59/0.86% (N10/20); bumps 3 and 2 needed at N20/N40.
- step 12: e=1/4 pointwise: whole 7.04/1.59/0.386% (N10/20/40), taboo 3.08/0.76%; C_T tightness e=1/2 0.215% (N40),
  e=1 0.145%, e=3 0.025%. Exact part (Gauss enclosures + margins + Hessian + certify) ~2/6/20 CPU-s at N=10/20/40,
  independent of e; the float proposal dominates at small e (~130 CPU-s at N=40). Added ladder_decision/run_ladder
  (declared stopping rule, pure function of the rung sequence) and report columns; ROUTE_SUMMARY gates/binds drafted.
- step 13: truth convergence (N=10,20,40,80): Richardson extrapolants e=1: 10.375970113 / 10.375969934 / 10.375969922;
  e=3: 2.573252048 / .051 / .051 (O(h^2) confirmed, truth uncertainty ~1e-8 relative). e=0 N=10: certified 549.4 vs
  truth 465.44 (+18%): large Lambda costs as predicted (overhead ~ Lambda h^2).
- step 14 (after coordinator message): inventory of results/: batches B, C, D ALL COMPLETED (30 P1 point runs, 10 F0
  comparator runs, 18 block runs incl. 3 taboo, 3 truth grids, 13 robust runs, controls at e=1 N10/N20 and e=1/2
  N20); no Traceback/alarm in any log. NOT RUN (not in the declared validation set; ladder rule would ask for them):
  N=80 rungs for e=0 taboo, e=1/4 whole+taboo, e=1 taboo (projected cost > the 20-min cap for e<=1/4; skipped).
  c2b_report.py fixed for uncertified comparator rows (certificate None) and taboo block rows (compared with
  tau_a(e_lo), not with the Lambda sup); run with python3 -B -> NS/validation/C2B_VALIDATION.json written.
- step 15: F0 (affine in m) comparator, N=20: e=1 certified 11.917 (+14.9% vs truth; P1 N20 +0.16%), e=3 2.9993
  (+16.6%; P1 +0.054%); e<=1/2 whole certified only at the edge of the declared slope grid (values 1e4-1e7, grid-
  limited), taboo NOT CERTIFIED (no feasible parameters). The same affine w certifies whole and taboo at e=1,3.
- step 16: blocks (N=40, whole): excess over sup Lambda = 4.91/9.76/19.96% at e0=1/2 (W=1/40,1/20,1/10),
  0.95/1.62/2.47% at e0=1, 0.037% at e0=3. Robust floor Lambda*(E) (lattice grid) - sup Lambda: <= 0.003% at e0=1/2,
  ~2e-8 at e0=1, 0 at e0=3 => the excess is almost entirely THIS strategy's block overhead, not intrinsic. Diagnosis:
  beta grows 1.8 -> 7.5 with W while alpha ~ 1.002: the declared block proposal (nodal max of the end-point value
  functions) is not a common supersolution where a larger drift delays the alarm (robust argmax picks e_hi at 128 of
  13121 nodes for [1/2,21/40]); the deficit is paid through beta. Remedy (DEFERRED, NOT RUN, would be amendment r1):
  use the robust value function W*_E as the block proposal.
- step 17: FD-CHECK SAMPLER BUG FOUND AND FIXED. controls_1_2_N20 C4 reported 3 "violations" (FD/bound 1.0005).
  Diagnosis (scratchpad c2b_fd_diag.py): the violating sample (cell U(3,8), m in [0.40,0.45]) was at m = 0.4805,
  OUTSIDE the cell; hessian_fd_check sampled the whole (s,y) rectangle although the bounds are claimed (and needed:
  the Taylor points xi_i lie in the cell) only on the cell. FD value is stable across steps (-1.775529 vs bound
  1.774614), so it is a real exceedance OUTSIDE the claimed domain, not FD noise. Corrected sampler
  (hessian_fd_check_cell, points inside the cell with a 3-step margin): e=1/2 N=20 whole max ratio 0.9907, 0
  violations. The certificate code is unchanged; only the validation check was wrong. Earlier C4 numbers in
  controls_*.json are SUPERSEDED by results/fdcheck_r1.json (all drifts, N=10,20, whole+taboo).
- step 18: corrected FD check (c2b_fdcheck.py -> results/fdcheck_r1.json): 5 drifts x N{10,20} x whole/taboo, 7200
  in-cell points: 0 violations, max FD/bound 0.9989; control x0.05 flagged 20/20; probe x0.98 flagged 12/20.
  STRATEGY 5.3 now states the claimed domain (cell x slab). A0_TIGHTNESS.md s2-3 and C2B_ROUTE_SUMMARY.md s1-4
  filled; Theorem M sentence added (implication acknowledged, not used). c2b_report.py (python3 -B) regenerated
  NS/validation/C2B_VALIDATION.json incl. fdcheck_r1 and notes. Quarantine scan: PASS (56 files, 10 in gen/, 0
  findings, control detected); ledger: 85 C2B lines, 0 LEAK_FLAG. STREAM C2b DONE.
