# REVIEW A0 CERTIFIER R1 (independent, adversarial)

CERTIFIER_ACCEPTED_WITH_CONDITIONS

Reviewer: reviewA0 (independent; did not write the code under review). Date: 2026-09-29.
Scope: NS/streams/A0 (a0_c2bx, sub_certify, a0_ladder, a0_verify, a0_controls, results C3/C4, certs manifest,
code pins, C5 design) against OV/reviews/REVIEW_C2B_STRATEGY_R1.md conditions C1-C5.
Declared drifts for reviewer runs: {1/2, 1, 11/10, 27/10, 3, 7/2}; guard_drift called first in every script.

Summary. The load-bearing upper bound U is sound: every U reported by `a0_c2bx` (and by the ladder) is the exact atom
value of a nodal vector that the pinned, previously reviewed `c2b_exact.certify` certified at exactly the stated
drift, and that same vector is what is persisted and re-verified (A1). The new lower-bound checker `sub_certify` is
correct in proof and code (A2), and my independent float evaluator, direction-swap controls and err-path controls
in both directions at 27/10 and 11/10 found no defect. An independent reference (own Nystrom + Richardson, own MC)
lies strictly inside [L, U] at e = 3 and e = 11/10 with margins far above its uncertainty (A6). No blocker. The
conditions concern the alarm semantics (R4 is structurally blind at the C2b level), the CPU-cap semantics, the C4
evidence being from an earlier ladder driver, and the still-open REVIEW_C2B conditions C3-C5 (governed execution,
errata, FD/err-path package evidence), now extended to `sub_certify`.

## Blockers (B*)
None. No accepted non-supersolution, no sign slip in `sub_certify`, no divergence between the persisted and the
certified W, and no drift mismatch was found.

## Conditions (C*) - to be met before any freeze of a formal protocol that consumes these certifiers
* **C1 (governed execution; carries REVIEW_C2B C3).** Implement the A0_C5 design: extract a side-effect-free
  `a0_core` (study s5, A0_C5 s6), a formal guard with a hash-bound AUTHORIZATION, marker at HEAD, and admit(b).
  Enforce the guard pins: A0_CODE_PINS.json records sha256 for `c308_quarantine` and `ov_quarantine` but
  a0_common.py:54 and :57 load both by path without any comparison. Re-validate the extracted core with
  byte-identical certificates on declared drifts.
* **C2 (R4 alarm semantics).** a0_ladder.py:14-16 and :92, study s2 (R4 row) and s1.4 claim a soundness alarm
  "across both implementations" that "can fire". State instead: (a) at one C2b rung L <= U holds by construction
  (a0_c2bx.py:45, :56, :63: a_lo <= 2^40 <= a_up, same g); (b) C2b-internal L cannot detect a defect shared by
  `kernel_nodes`/`hessian_bounds`; (c) the implementation-independent alarm is L_C1b <= U_C2b with a sensitivity equal
  to the C1b Lambda_lo slack. Freeze a rule that status CERTIFIED requires at least one certified independent lower
  rung (else a distinct declared status), and record the alarm sensitivity at the validation drifts.
* **C3 (R6 cap).** a0_ladder.py:48-51 silently lowers the declared cap to an outer hard limit (C4 runs: declared
  10200 s, effective 3630 s). Freeze: refuse to start unless the effective cap equals the declared cap, record both,
  and size the cap from the full declared ladder in hull mode (study s1.4 figures put 11/10 near 3600 s).
* **C4 (determinism evidence on the frozen driver).** The C4 ladder files were produced by a0_ladder.py sha
  a08c8fac... (C1b d in {10, 12}); the current file is 7717639f... (d in {8, 10, 12}; certifier modules unchanged).
  Re-run the C4 pair on the frozen driver (after C1), including one non-dyadic drift (hull path) and the d = 8 rung
  inside the ladder.
* **C5 (REVIEW_C2B C4 errata).** Nothing in A0 addresses the six claim corrections; OV is immutable, so the formal
  package must carry an errata file for them.
* **C6 (REVIEW_C2B C5 evidence, extended to `sub_certify`).** In the package: (i) an FD check of `hessian_bounds`
  over every cell kind (L, U, AXP, AXM, s < 1) with at least one rough W at the ladder meshes; (ii) err-path controls
  in BOTH directions through the one verifier, each with a confirmed interior violation (rigorous witness preferred,
  REVIEW_C2B t3b design; my float confirmation here is supporting evidence only); (iii) the two direction-swap
  controls; (iv) a vertex-enclosure agreement test at a non-dyadic drift. `sub_certify` is accepted by this review
  as the L-producer, but it must travel with (ii)-(iii) into any qualification.

## Notes (N*)
* **N1 (tightness, F2 scope).** Exact scale (w = a g, no beta) is worse than the pinned alpha-beta selection at
  e = 1/2 for N <= 40 (A0_C1_TABLES.md, e = 1/2 rows: N = 20 +6.40e-3 vs +4.27e-3). F2 "removes it" holds at N = 80,
  e >= 1. Not a soundness matter; the ladder takes the minimum anyway.
* **N2 (platform).** U depends on the platform float of the proposal (libm, Jacobi) and of the C1b LS candidate;
  the persisted certificate, not a value recomputed on another host, must be the sealed record.
* **N3 (non-dyadic drifts).** The C2b review attacked only dyadic drifts; my node-enclosure test and interior scans
  at 27/10 and 11/10 now cover the non-dyadic lattice path (agreement to 1.8e-15; no violation).
* **N4 (proof text).** a0_c2b.py:15-17 and study s1.2 item 2 bound G1 "by a certified supersolution at the same
  drift"; G1 is bounded independently (one-step alarm probability >= P(N(0,1) > C + |e|) > 0). Say so, so that the
  lower bound does not formally depend on another certificate.
* **N5 (F5 dyadic-down).** Pointwise C1b was only run at denominators <= 2; the dyadic-down alternative (2^-20 grid)
  is plausible (c1b_kernel.py:496, SC = 480) but untested and must be qualified if chosen.
* **N6 (R5 availability).** a0_ladder.py:54-69 has no per-rung exception handling: an exception in the optional C1b
  rung voids a ladder whose C2b U is certified. Fail-closed, but declare whether a rung exception means
  NOT_CERTIFIED or a void run.
* **N7 (R6 wording).** Certificate files are written before the ladder file (a0_ladder.py:77-79), so a cap hit in
  between leaves orphan (valid) certificates; "writes no file" is not exact.
* **N8 (persistence).** streams/A0/ is untracked in git and the 136 certificates (59 MB) exist only in this worktree;
  I re-hashed all 136 against certs/CERTS_MANIFEST.json (0 mismatches) and checked the five C2b pins against both
  the files and the git blobs at HEAD (all match; c2b_exact.py unchanged since the reviewed commit).
* **N9 (stale status).** A0_CERTIFIER_STUDY.md line 9 and s8 still say the 27/10 hull control was running; the file
  C3_CONTROLS_C1BH_e27_10_d12.json exists with 6/6 as expected.
* **N10 (reference resolution).** MC (A0's and mine) has relative s.e. 1e-4 to 5e-4 and cannot resolve the certified
  bracket; the only high-resolution independent reference is my Nystrom, an independent implementation of the same
  P1 collocation scheme as the pinned proposal (agreement 2.6e-15). It is a spot check at two drifts, not a
  substitute for C6.
* **N11 (quarantine / ledger).** Reviewer runs used only 27/10, 11/10 and 3 (declared set {1/2, 1, 11/10, 27/10, 3,
  7/2}); `r_common.rv_drift` calls the declared-set check and `c308_quarantine.guard_drift` before any evaluation,
  and a0_common's shim guards again inside the pinned code; self-test refused 19/10, 2, -27/10. 0 band evaluations,
  0 target evaluations, no cell id used, no TCT_INPUTS/C2_D5_FORECAST/REGISTRY/RLR307 file opened, nothing written
  under streams/A0 or OV. Ledger lines: class REVIEW, agent reviewA0. Only relative positions (bound vs reference)
  are quoted; no Lambda value is written in this file. `c308_quarantine._scan_tree(reviews/)` with both planted
  controls: verdict PASS, 0 findings (report-only hits are float literals 2.0 such as sqrt(2.0)). 7 ledger lines
  (REVIEW / reviewA0), 0 LEAK_FLAG; `git status` of OV empty; no file under streams/A0 modified. Scratch:
  reviews/scratch_A0_R1/ (r_common.py, r_eval.py, r_a2a5.py, r_a6.py, t_*.json, log_*.txt).
* **N12 (scope).** The VERIFY stream's uncommitted P1-format files (vd_pl*.py, results/D6_*) were not read or used.

## A1 exact-scale selection soundness

**Result: SOUND. Every U that `a0_c2bx` reports is the exact atom value of the W on which the pinned, reviewed
`c2b_exact.certify` returned `certified: True`, at exactly the drift the certificate states.** Line by line
(streams/A0/a0_c2bx.py):

* l.30/l.38: `declared_drift(e)` then `S = EX.Setup(N, e)` with `e_hi = None`, so `S.J = 0` (pointwise) and both
  Gaussian lattices are built at K +/- e for the exact rational e. The certificate stores `drift = A.fs(e)` (same e).
* l.35-36: the proposal g is the pinned `c2b_certify.proposal` + `_dyadic` (float, untrusted); g_int at 2^-40.
* l.46-56 (selection, untrusted): I re-derived the constraint. For W = a*g_int (a > 0, g_int >= 0) the pinned vertex
  evaluator is exactly linear (`pick` depends only on the sign of W; the atom mass `klo`/`khi` does not depend on W)
  and `hessian_bounds` is exactly homogeneous of degree 1 (every term is |linear in W| times a W-free constant), so
  `certify` passes iff a*Dmin_c - 2^(P+Q+CBITS) - ceil(a*E_c/8N^2) > 0 for every cell c, i.e.
  a >= ceil(8N^2 (2^(P+Q+CBITS)+1) / (8N^2 Dmin_c - E_c)). l.55 is exactly that ceiling; `den <= 0` sets `a_up = None`
  (fail-closed, l.52-54). The selection is in any case only a proposal.
* l.66-74: `Wu = a_up*g_int` is rebuilt before every `EX.certify(S, Wu, Q + CBITS, True)` call; the loop breaks on the
  first certified W; if 65 attempts fail, `up_ok` is False and no U is reported (l.86, l.98).
* l.99-103: U = `res_u["w_atom"]` = str(F(Wu[0][0], 2^(Q+CBITS))) from the certify result of that same Wu; the
  certificate persists that Wu (`make_cert(..., Wu, F(res_u["w_atom"]))`), with `Qbits = Q + CBITS`, `kind = whole`
  (certify was called with `full = True`), and `W_sha256` over the canonical serialisation of Wu. No rounding enters
  the claim (it is the exact node value). No variable aliasing: Wu is not mutated after certification.
* The certified statement is the reviewed one (c2b_exact.py:3-7, REVIEW_C2B s1-s2): W >= 0 at every node (hence the
  P1 interpolant >= 0 on R) and w >= 1 + K_e w on every cell of the mesh, which tiles R = {p+m <= 4} u axis tails to
  H = 5 (the reachable set: K_e maps R into R). Hence E_x[tau] <= w(x), and at the atom Lambda(e) <= U.
* Re-verification (`a0_verify.verify_certificate`, l.39-63) re-runs the same pinned `certify` on the stored integers
  at `Setup(N, e)` and requires exact equality of w(a) with the claim; it uses `certify` iff certifier ==
  C2B_P1_SUPER, so a mislabelled sub-certificate can only be accepted if it really is a supersolution.
* The ladder (a0_ladder.py:55-58, 86) composes the in-memory U string of the same run, i.e. the value of the persisted
  W. (It does not re-read the file; the design's re-verification step is separate, see A3.)

Residual caveats (not soundness): (i) U inherits the platform float of the proposal (libm erf/exp, Jacobi), so U is
reproducible bit-for-bit only on the same platform; the persisted W, not a re-run, is the record (see A3/A4-C2).
(ii) The C2b certifier was reviewed and attacked only at dyadic drifts (REVIEW_C2B declared set {0, +-1/4, +-1/2,
+-1, +-3}); nothing in the lattice construction needs dyadic e (exact `Fraction` t = K +/- e + d h), and my own
independent float scan below (A2/A6) includes the non-dyadic drift 27/10.

## A2 sub_certify

**Result: the lemma (study s1.2, a0_c2b.py:9-17) and the code (a0_c2b.py:88-113) are CORRECT; no sign slip found.**

Proof check (my own derivation, whole kernel K_e, killed at the alarm, P1 w on the C2b mesh):
1. Psi := K_e w. On a cell T (triangle, or axis segment), 1 + Psi - w = (1 + I Psi - w) + (Psi - I Psi) >=
   (1 + I Psi - w) - |Psi - I Psi|. The first bracket is affine on T (w and I Psi are both P1 on T; the map
   (p,m) -> (s,y) is affine at fixed e, so I Psi in (p,m) equals the (s,y) interpolant used in STRATEGY s5.3), so its
   minimum over T is attained at a vertex v, where it equals 1 + Psi(v) - w(v) >= 1 + (K_e w)_lo(v) - w(v). The second
   term is bounded by err(T) (REVIEW_C2B s1.3: the Taylor/Popoviciu bound is an absolute-value bound, valid for any
   sign of W's slopes/jumps, over (bounding box n strip) x slab, which contains T). Hence
   min_v[1 + (Kw)_lo(v) - w(v)] >= err(T) for every T  ==>  w <= 1 + K_e w on the whole tiling of R.
2. G1 = E_.[tau] satisfies G1 = 1 + K_e G1 on R and is bounded (from every state the one-step alarm probability is
   >= P(N(0,1) > C + |e|) > 0, so G1 <= 1/delta; the study's "a certified supersolution bounds it" is sufficient but
   unnecessary, N4). u = G1 - w >= K_e u, K_e positive, so u >= K_e^n u >= -||u|| P_.(tau > n) -> 0 pointwise. So
   w <= G1 on R and L = w(a) <= Lambda(e). The direction is right.

Code, line by line (a0_c2b.py):
* l.93-94: pointwise only (`S.J != 0` raises) - consistent with the lemma as proved (one e).
* l.95-96: negative nodal values refused (not needed by the lemma, harmless; it also makes `pick` well-defined).
* l.98: `kernel_nodes(..., upper=False)`: for W >= 0 `pick` takes the LOWER segment weights (floored, clipped at 0,
  c2b_exact.py:99) and the lower atom mass `klo` (floored Phi enclosures, clipped at 0, l.172-174): a rigorous lower
  bound of (K_e w)(v). The whole kernel (`full`) includes the atom term; the verifier always passes `full = True` and
  requires `kind == whole` (a0_verify.py:47, 54).
* l.99: `defect = one + Klo - (W << P)`: a lower bound of 1 + K w - w at scale 2^-(P+Qb) (same scale as `one`, Klo
  and W<<P). Correct sign.
* l.100-109: `err` from the pinned `hessian_bounds` on the same W (ceiled upward, c2b_exact.py:325); `slack = vmin -
  err`, failure iff `slack < 0` (non-strict acceptance is what the lemma needs). The err term is SUBTRACTED from a
  lower bound of the defect: correct sign.
* l.113: the claim is the exact node value W[0][0]/2^Qb. Killing and boundary: `kernel_nodes` integrates only up to
  H on both axes (the alarm mass is excluded), and the cells tile R including both axis tails (AXP: r_y = h,
  AXM: r_y = 0, both correct for a 1-D P1 segment).
* `a0_c2bx` lower selection (a0_c2bx.py:57-63): floor((2^(P+Q+CBITS) - 1) * 8N^2 / (E - 8N^2 dmin)) is the exact
  largest-a solution of the linearised constraint (one unit conservative); `sub_certify` re-checks the final vector.

Empirical checks (my scripts, reviews/scratch_A0_R1/r_a2a5.py and r_eval.py, outputs t_a2a5_e*_N20.json; stored A0
C2BX certificates at N = 20, reference rung N = 40 re-verified first). r_eval.py is my own float evaluator of
(K_e w)(x) at ARBITRARY x, written from the model (decomposition in z, exact breakpoints at every mesh line crossed,
closed-form erfc integration of each linear piece); it imports nothing from C2b.

| check (e = 27/10, N = 20; the 11/10 repeat is summarised after the table) | result |
|---|---|
| my evaluator vs the pinned rigorous vertex enclosures [K_lo, K_up] at every node (non-dyadic drift) | 3361/3361 nodes inside (tol 1e-12 rel), max rel. deviation from the enclosure midpoint 1.6e-15; negative control (my evaluator at drift 3 vs the 27/10 enclosures): 3361/3361 outside |
| interior scan of the STORED sub-certificate, r = 1 + Kw - w at 83 400 interior/edge points (13 per triangle, 5 per axis segment) | min r > 0 (about 4.4e-4), 0 negative points |
| interior scan of the STORED super-certificate, r = w - 1 - Kw, same points | min r > 0 (about 5.0e-4), 0 negative points |
| direction swap: super W relabelled C2B_P1_SUB (invalid by proof: claim U(20) > U(40) >= Lambda) | `sub_certify` FAIL (CERTIFICATE_INEQUALITY_NOT_CERTIFIED) |
| direction swap: sub W relabelled C2B_P1_SUPER (claim L(20) < L(40) <= Lambda) | `certify` FAIL |
| sub err-path control (NEW): t*W_sub with the largest t = T/2^24 whose vertex defects are all >= 0 | vertex-only sub check accepts; `sub_certify` FAIL; my scan finds 42 304 points in 3 537 cells with 1 + Kw - w < 0 (min about -8.9e-5): the candidate really is not a subsolution and `sub_certify` rejects it through its err term |
| super err-path control (A0 design): t*W with the smallest t whose vertex margins are >= 0 | vertex-only accepts; `certify` FAIL; my scan finds 34 985 points in 3 192 cells with w - 1 - Kw < 0 (min about -2.5e-5): a float-confirmed interior violation (upgrades A0's sensitivity-only control; not rigorous) |
| selection boundary | W_sup = a_up g and W_sub = a_lo g exactly; a_lo <= 2^40 <= a_up (the R4 tautology, A3); `certify((a_up-1) g)` FAILS and `sub_certify((a_lo+1) g)` FAILS: both selections sit exactly on their checker's boundary |

Repeat at e = 11/10, N = 20 (ref N = 40; t_a2a5_e11_10_N20.json): identical outcome on every row - node test
3361/3361 inside (max rel. deviation 1.8e-15; negative control 3361/3361 outside); stored sub and super interior
scans 0 negative of 83 400 (min r about +1.0e-3 and +7.8e-4); both direction swaps FAIL; sub err-path candidate
vertex-accepted, `sub_certify` FAIL, 3 172 negative points in 276 cells (min about -2.5e-4); super err-path
candidate vertex-accepted, `certify` FAIL, 77 672 negative points in 6 164 cells (min about -4.9e-4); both
selections exactly on the checker boundary.

A sign slip of either kind (defect sign flipped, or err added instead of subtracted) would have made the direction
swap or the sub err-path control PASS; neither did, and no accepted certificate shows an interior violation. The
lower-bound checker is therefore sound as far as proof reading and these tests reach; formal adoption still needs the
C5-style package evidence (condition C6).

## A3 ladder rules R1-R6 (a0_ladder.py)

* **R1 fixed rung set / R3 composition: SOUND.** `run` (l.54-69) executes every declared rung; `compose` (l.85-96)
  takes U = min over rungs with `status_U == CERTIFIED`, L = max over rungs with `status_L == CERTIFIED`, exactly (Fraction).
  A min of certified upper bounds is a certified upper bound. No rule reads a result to decide what to run next;
  the only data-dependent loops are the bounded bump/decrement loops inside a rung (<= 65 attempts each), which
  terminate with NOT_CERTIFIED, never with a value from a non-certified vector.
* **R2 determinism: MET for the value path.** No wall-clock or CPU quantity enters any value (CPU seconds are
  recorded only). Dict iteration is insertion-ordered; the C4 re-runs were separate processes (independent
  PYTHONHASHSEED under -I) and produced byte-identical certificates. Residual platform dependence: the float
  proposal (libm, Jacobi) and C1b float LS make U a function of the platform as well as of the declared inputs; the
  persisted certificate, not a re-run, must be the sealed record (C3 below).
* **Hull switch (C1b at non-dyadic b): SOUND.** `dyadic` (l.61) is decided from e only. `a0_c1bh` asserts
  lo < e < hi, width 2^-20, passes both guards on the interval, and uses the pinned block path
  `Ctx(e_c, BW, log, e_r)` (c1b_certpw.py:72-92: e stays symbolic when e_r > 0, enclosures over R x [e_c-e_r, e_c+e_r]).
  The certified statement is block-uniform on [lo, hi], hence holds at b; `a0_verify` requires the stored hull to be
  exactly `hull_of(e)` (a0_verify.py:77-79). The C1b `Lambda_lo` formula (a0_c1b.py:52-53, a0_c1bh.py:66-68) is valid
  at every e' in the hull (residual enclosure over the hull, A_bar block-uniform): max(Wa - A_bar*r_hi+, Wa/(1+r_hi+))
  with z_W rounded up. Note: F5's alternative "dyadic-down b' = floor(b 2^20)/2^20, pointwise C1b" is untested at any
  drift with denominator > 2 (N5).
* **R4 consistency alarm: OVERSTATED (condition C2).** At a single C2b exact-scale rung, U = a_up g(a)/2^80 and
  L = a_lo g(a)/2^80 with the SAME proposal g, and the code forces a_lo <= 2^40 <= a_up (a0_c2bx.py:45, 56, 63: a_lo
  starts at 2^40 and only decreases, a_up starts at 2^40 and only increases). So L_C2b(N) <= U_C2b(N) holds by
  construction and cannot fire, whatever `certify` or `sub_certify` do (even an accept-all `sub_certify` would give
  L = g(a)/2^40 <= U). Across C2b rungs the check compares Nystrom values of different meshes through the SAME vertex
  evaluator and Hessian bounds, so a defect shared by `kernel_nodes`/`hessian_bounds` moves U and L together and is
  invisible to R4. The only implementation-independent alarm is L_C1b <= U_C2b, whose sensitivity is the looseness of
  the C1b Lambda_lo (study F4: 1e-4 to 7e-3 relative; hull d = 10/12 at 11/10 and 27/10: 4e-4 to 1.6e-3), i.e. one
  to two orders of magnitude coarser than the C2b U slack it is meant to police. And if no C1b rung certifies, R4
  silently degrades to the tautology while status stays CERTIFIED (compose l.92: `lo is None or lo <= u`; L_C2b
  always exists). The study's claim "R4 ... a soundness alarm that can fire. It held at every drift" (s2 table R4,
  s1.4) must be restated. L is not load-bearing, so this is not a soundness defect of U.
* **R5 fail-closed: MET.** No certified upper rung -> NOT_CERTIFIED, no U (l.88-89). Any exception in any rung
  (including the optional C1b cross rung) kills the process before the ladder file is written: fail-closed, but it
  voids an otherwise certified C2b U (availability, N6).
* **R6 CPU cap: semantics not as declared (condition C3).** l.50: `eff = min(cap, hard)` silently lowers the cap to an
  outer hard limit. Both C4 ladder files record `process_cpu_cap = 10200` but `effective_cpu_cap = 3630`
  (results/LADDER_e3_detA.json, LADDER_e7_2_detB.json). A lower cap cannot change a value (a cap hit kills the
  process), so determinism is intact, but the declared "sum of per-rung caps, ~2.5x the worst rung" is not what ran;
  the full recommended ladder at 11/10 (C2b N=80 ~530 s + C1b hull d=10/12 ~1140 + ~1550 s + the rest, study s1.4)
  is at or above 3630 s. Also "a cap hit writes no file" is not exact: certificate files are written (atomically,
  one by one) before the ladder file (l.77-79); a kill in between leaves valid but orphan certificates (N7).
* **Can any rule depend on a result?** Within a run, no (fixed set, exact min/max). Across the study, the rung set
  was changed after results (exact-scale after F1; C1b {10,12} -> {8,10,12} after F4); both were decided on
  validation drifts only and are declared in s2 "Selection rule" - acceptable for research, but the C4 evidence was
  produced by a DIFFERENT a0_ladder.py (sha a08c8fac..., declared C1b (10,12)) from the current file (7717639f...);
  C4 must be re-run on the frozen ladder (condition C4).

## A4 review conditions C1-C5 of REVIEW_C2B_STRATEGY_R1

| cond. | requirement (REVIEW_C2B s6) | status after A0 | evidence / gap |
|---|---|---|---|
| C1 persist + re-verify | store exact W (+Q, sha256); verifier runs `certify` on stored W without the proposal | **MET (research)** | `make_cert` (a0_c2b.py:168-173) stores W, Qbits, W_sha256, claim; `verify_certificate` (a0_verify.py:39-63) uses no float; bulk 16/16 PASS; manifest 136 files, I re-hashed all 136: 0 mismatches; I re-verified stored certificates myself (A5). Gap: the 59 MB of certificates and all of streams/A0/ are UNTRACKED in git (worktree only); a freeze must store them content-addressed (N8). |
| C2 deterministic stopping | declared rung set or operation count, no CPU rule | **MET for the A0 ladder** | fixed rung set, no CPU in the value path (A3). The pinned `c2b_certify.ladder_decision` CPU rule (c2b_certify.py:192) still exists and must never be the driver of a formal run (it is not used by A0). Caveats: platform float of the proposal; R6 effective-cap discrepancy (C3). |
| C3 governed execution path (+ bind ov_quarantine hash) | frozen authorization admitted by the guard, no post-freeze edit | **NOT MET (design only)** | A0_C5_GOVERNED_EXECUTION_DESIGN.md is a reasonable design (arm/admit, hash-bound AUTHORIZATION, marker at HEAD, Q1-Q7), nothing implemented; `a0_core` extraction pending (s6). The guard hashes recorded in A0_CODE_PINS.json ("guards") are NOT checked at load: a0_common.py:54,57 load `c308_quarantine` and `ov_quarantine` by path with no sha256 comparison. |
| C4 claim corrections | six corrections to STRATEGY.md / C2B_ROUTE_SUMMARY.md / A0_TIGHTNESS.md | **NOT MET** | nothing in A0 addresses them (grep of streams/A0 for the six items: no hit). OV is immutable, so they must be carried as an errata file inside the formal package (w = const check, 5e-9 quadrature, "no bumps beyond 3" (max 5), "exact" -> rigorous enclosure, absolute cross term, W*_E as minimal fixed point). |
| C5(i) FD over every cell kind, rough W | exhaustive FD of `hessian_bounds`, AXP/AXM/s<1/slabs, >= 1 rough W | **NOT MET in A0** | no FD check in streams/A0. The reviewer's own T2 evidence exists in OV scratch, not in a package. Now also needed for the NEW consumer of `hessian_bounds`: `sub_certify` relies on the same bound with the opposite sign of the residual (sign-free, so the same FD evidence suffices, but it must be in the package). |
| C5(ii) err-path control through `certify` | vertex-only acceptable candidate rejected by `certify`, with a rigorously confirmed interior violation | **PARTIAL** | ERRPATH in a0_controls.py:133-149 goes through `verify_certificate` -> `certify` and can fail for an err-free checker (4/4 as expected), but no interior violation is confirmed (study s7 item 2). My independent float scan (A2/A5 table) confirms interior violations for ERRPATH candidates in both directions (float, not rigorous). No err-path control existed for `sub_certify`. |

## A5 controls

* **Capable of failing: yes, all of them.** The C3 set is two-sided (V0 valid certificates must PASS, so an
  always-FAIL verifier fails the control set; planted invalids must FAIL, so an always-PASS verifier fails it);
  integrity plants hit the sha256 / claim clauses; ERRPATH fails for an err-free `certify`. The C4 comparator has a
  planted negative (one nodal integer +1: detected, results/C4_COMPARATOR_NEGATIVE_CONTROL.json).
* **Same path: yes.** Every control goes through `a0_verify.verify_certificate` (a0_controls.py:38-43), the same
  function used by the bulk re-verification and by my runs.
* **Limits.** (a) Apart from ERRPATH every planted invalid is detected at a vertex (gross plants: 3 %, an atom node
  moved by the bracket width, a relabelled drift), so the C3 set does not exercise the interpolation term except
  through ERRPATH; (b) the invalidity proofs of V1-V3 use L from `sub_certify`, i.e. they are conditional on the new
  checker under review (circular for testing `sub_certify` itself; not for `certify`); (c) no direction-swap control
  and no err-path control for `sub_certify` existed (I added both, A2 table); (d) C3_CONTROLS_C2B_* (pinned
  selection) were produced by an earlier a0_verify.py / a0_controls.py than the current files; the C2BX, C1B, C1BH
  controls and all C3_REVERIFY_FINAL files match the current code (I compared the recorded code sha256 of every
  C3/LADDER result with the files on disk); (e) the study s0/s8 header still says the 27/10 hull control was
  "still running at hand-back"; the file now exists with 6/6 as expected (stale status line, N9).
* **Re-run by me** (through `verify_certificate`, current code, t_a2a5_e27_10_N20.json and t_a2a5_e11_10_N20.json):
  stored C2BX super and sub certificates at N = 20 and the N = 40 reference pair re-verify PASS; planted x0.97 super
  and x1.03 sub FAIL on the certificate inequality; plus the direction-swap and err-path controls of the A2 table.

## A6 independent spot check

Method (reviews/scratch_A0_R1/r_a6.py, outputs t_a6_e3.json, t_a6_e11_10.json; relative positions only are recorded):
(i) my own P1 Nystrom written from the model (node collocation, closed-form product integration of the P1
interpolant against phi, Jacobi to a 1e-14 update), meshes N = 20, 40, 80, 160, Richardson O(h^2) plus an h^4 level
as an error indicator; (ii) my own plain Monte Carlo (random.Random(20260929).gauss, 4e6 paths at e = 3). Compared
with the exact U and L of the A0 ladder run LADDER_e3_detA (deciding rungs C2B_P1_EXACT_SCALE N = 80, super and sub).

| e = 3 | value |
|---|---|
| my Nystrom vs the A0-recorded pinned-float Nystrom at the same mesh (N = 40) | relative difference 2.6e-15 (independent implementation of the same scheme agrees) |
| three-mesh ratios (20/40/80, 40/80/160) | 4.0001, 4.00002 (clean O(h^2)) |
| estimate uncertainty: |Rich(40-80) - Rich(80-160)| / est ; |h^4 - h^2| / est | 5.1e-12 ; 3.4e-13 |
| (U - est) / est | +3.18e-5 |
| (est - L) / est | +3.01e-5 |
| **L <= est <= U** | **TRUE**, with both margins about 10^6 times the estimate's uncertainty |
| Monte Carlo (n = 4e6): relative s.e.; z(MC - est); z(U - MC); z(MC - L) | 1.27e-4; -0.69; +0.94; -0.45 (consistent; MC cannot resolve a 6e-5 bracket) |

| e = 11/10 (U, L from the study's deciding rung C2BX N = 80; meshes 20/40/80; MC n = 1e6) | value |
|---|---|
| three-mesh ratio 20/40/80 | 3.982 |
| estimate uncertainty: |Rich(20-40) - Rich(40-80)| / est ; |h^4 - h^2| / est | 9.6e-10 ; 6.4e-11 |
| (U - est) / est ; (est - L) / est | +7.88e-5 ; +7.87e-5 |
| **L <= est <= U** | **TRUE** (margins about 10^4 to 10^5 times the estimate's uncertainty) |
| Monte Carlo: relative s.e.; z(MC - est); z(U - MC); z(MC - L) | 4.9e-4; +0.34; -0.18; +0.50 (consistent) |

The margins agree with the study's reported U slack +3.2e-5 and L slack -3.0e-5 at e = 3 (s1.4), i.e. my
independent reference and the study's Lambda_ref coincide at that resolution.
