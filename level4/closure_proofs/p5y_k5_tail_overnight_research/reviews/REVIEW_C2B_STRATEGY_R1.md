# REVIEW_C2B_STRATEGY_R1 — independent adversarial review of stream C2b (cell-independent supersolution certifier)

Reviewer: independent agent (wrote none of the reviewed code). Date 2026-09-28.
Scope: NS/streams/C_308/A0X/gen/ (STRATEGY.md §5.3 especially), NS/validation/C2B_VALIDATION.json.
Quarantine: no drift in [1.2,2.6] or mirror evaluated; no 305–309 quantity; amendment-2 R2.1–R2.4 observed (no validation-drift value is quoted next to any tail number; certificate values are referred to by content class only).
Scratch: SCR/review_C2B/.

CERTIFIER_REVIEW: ACCEPTED_WITH_CONDITIONS

Summary: STRATEGY §5.3 is correct line by line (all second-derivative formulas re-derived; claimed domain cell × slab
is right and is what the Taylor argument needs; Popoviciu/Taylor inequality correct in sign, constant and
geometry). The certificate code implements it soundly. Independent evaluator + exhaustive FD (0 exceedances, every
cell kind, rough and smooth W, slabs) + an end-to-end attack found no accepted non-supersolution, and showed the err
term is load-bearing (26/26 rigorous violations accepted by a vertex-only check, rejected by `certify`). No
blockers. Conditions C1–C5 (§6) — persisted/re-verifiable W, deterministic stopping rule, governed execution path
past the quarantine guard, claim corrections, and err-path + full-coverage checks inside the qualification package —
must be met before a freeze. Route stays VALIDATED_NON_TARGET and CLOSURE-ONLY under floor r2.

## 0. What was read
PREAMBLE (Q1–Q8, S1–S8), config/QUARANTINE_AMENDMENT_1.json, QUARANTINE_AMENDMENT_2.json; gen/STRATEGY.md (all),
A0_TIGHTNESS.md, C2B_ROUTE_SUMMARY.md, PROGRESS.md; every gen/c2b_*.py (common, exact, certify, float, pointeval,
checks, fdcheck, controls, validate, report); results/fdcheck_r1.json; validation/C2B_VALIDATION.json (structure);
c7_gaussian.py (read in full: pure, `fractions` only, no import-time side effects; alternating-series and exp tail
bounds are checked at run time). Validation set for this review was declared by rule before any run
(SCR/review_C2B/DECLARED_SET.md): drifts {0, ±1/4, ±1/2, ±1, ±3}; blocks only at |e| ≥ 3 (so every interior drift
sampled is itself declared).

## 1. §5.3 line-by-line

### 1.1 The drift-through-y lemma (§5.1)
Re-derived from the model (window z ∈ [m−C, C−p], next = (max(0,p+z−K), max(0,m−z−K)), z+e ~ N(0,1)):
p-branch u = p+z−K ⇒ z+e = u−y with y = p−K−e; m-branch v = m−z−K ⇒ z+e = η−v with η = m−K+e = s−y−1;
both-positive branch exists iff s > 1 with u ∈ (0, s'), m' = s'−u; atom window [m−K, K−p] non-empty iff s < 1 with
mass Φ(−y) − Φ(η) = Φ(K+e−p) − 1 + Φ(K−e−m) (matches c2b_exact.py:170-175). Upper limits u, v ≤ H follow from the
window. **Correct.** The only drift dependence is through y (at fixed s), so a block in e is a y-interval. Note the
identity s' − y = η, i.e. φ(s'−y) = φ(η): the code bounds this term on the Lp lattice with the p-range
(c2b_exact.py:299), which is a superset of the true η-range by one mesh step — conservative, not wrong.

### 1.2 Second derivatives (re-derived independently, integration by parts, P1 w)
With T3 = ∫_{s'}^H a φ(u−y), T2 = ∫_{s'}^H b φ(v−s'+y), T1 = ∫_0^{s'} w(u,s'−u) φ(u−y) (s ≥ 1), and T4 = w(a)[Φ(−y)−Φ(η)] (s < 1):

| formula (STRATEGY line) | my derivation | verdict |
|---|---|---|
| Ψ_yy, s ≥ 1 (l.129-131) | value terms at u = s' (T1 vs T3: c(s') = a(s')) and at u = 0 (T1 vs T2: c(0) = b(s')) cancel; a'(s'+) − c'(s'−) = g_m[L(q,0)], b'(s'+) + c'(0+) = g_p[L(0,q)]; boundary terms at H with (H−y)φ, (H−η)φ; kink sums of a, b over (s',H) and of c over all breaks | **match** |
| Ψ_s (l.132) | T1 upper-limit term cancels T3 lower-limit term; T2 lower-limit term cancels after IBP | **match** |
| Ψ_sy (l.133-134) | −g_m(s'−)φ(s'−y) + g_m(0+)φ(y) + Σ_all Δg_m φ(β−y) + b(H)(H−η)φ(H−η) + b'(H−)φ(H−η) − b'(s'+)φ(y) − Σ Δb'φ(v_k−η); g_m(0+) on L(0,q) equals b'(s'+) on the m-axis edge of L(0,q) ⇒ cancels | **match** |
| Ψ_ss (l.135-136) | only *moving* (horizontal) breaks move with s; sign −Δg_m; T2 gives −b(H)(H−η)φ − b'(H−)φ + Σ Δb'φ | **match** |
| s < 1, whole (l.144-146) | value terms a(0)(−y)φ(y), −b(0)ηφ(η) cancel against ∂²T4 = w(a)[yφ(y)+ηφ(η)] since a(0)=b(0)=w(a); Ψ_s = −b(H)φ(H−η) + ∫_0^H b'φ, Ψ_sy = −Ψ_ss | **match** |
| s < 1, taboo (l.148-149) | without T4: extra −w(a)[yφ(y)+ηφ(η)] in Ψ_yy, ∓w(a)ηφ(η) in Ψ_ss/Ψ_sy | **match** |

Code vs formulas (c2b_exact.py:285-327): every term appears with |coefficient| × φ-max or |t|φ-max; moving breaks
(L→U, horizontal edge m' = (q−k)h, u ∈ [kh,(k+1)h]) and fixed breaks (U→L, vertical edge u = (k+1)h) are classified
correctly (l.278-281); kink suffix sums start at k = q+1 (s ≥ 1) and k = 1 (s < 1) (l.301-302, 314-315); `_PM.pm`
(φ decreasing in |t|) and `_PM.tpm` (|t|φ maximal at |t| = 1, monotone on intervals avoiding ±1) are correct
(l.202-210). **No missing or mis-signed term found.**

### 1.3 Domain (cell × slab) and the interpolation inequality
* Every φ-range is built from the cell's *box* ranges: Lp terms use p ∈ [ilo,ihi]h, Lm terms use m ∈ [jlo,jhi]h,
  e ∈ slab (l.291-293). The s ≥ 1 / s < 1 structure is fixed by the cell's s-strip. So the bounds hold on
  (bounding box ∩ strip) × slab ⊇ cell × slab. On the (s, y) rectangle they do NOT hold, because η = s−y−1 ranges
  over a wider set than m−K+e on the cell (for U(3,8), N=20 the rectangle admits m up to 0.50 vs the cell's 0.45).
  The author's statement of the claimed domain (STRATEGY l.157-159) is **correct**, and it is exactly what the
  certificate needs: the Taylor points ξ_i lie on segments [x, x_i] inside the tetrahedron ⊂ T × S.
* Interpolation inequality (l.107-116): on a tetrahedron with vertices x_i (prism vertices of T × S) and
  barycentric λ, IΨ(x) − Ψ(x) = ½ Σ λ_i (x_i−x)ᵀ D²Ψ(ξ_i)(x_i−x) (first-order terms cancel because Σλ_i(x_i−x)=0).
  In (p,m,e) the quadratic form is Ψ_ss ds² + 2Ψ_sy ds dy + Ψ_yy dy² (ds = dp+dm, dy = dp−de). Popoviciu gives
  Σλ_i ds_i² ≤ r_s²/4, Σλ_i dy_i² ≤ r_y²/4 (s, y affine ⇒ weighted means are s(x), y(x)); the cross term needs
  Σλ_i|ds_i||dy_i| ≤ r_s r_y/4, which follows by Cauchy–Schwarz (the ξ_i differ, so the signed form written at l.112
  is not literally what is used; the absolute form holds and is what the code implements). Hence
  |Ψ − IΨ| ≤ (r_s²H_ss + 2 r_s r_y H_sy + r_y² H_yy)/8 with r_s = h, r_y = (p-width + slab width)
  (= (wp+je)h at l.323; AXM has wp = 0). **Sign, constant 1/8 and geometry are correct.** Then
  w − 1 − Ψ ≥ (w − 1 − IΨ) − |IΨ − Ψ| ≥ min_vertices(w − 1 − Ψ_upper) − err, the certified condition (l.340-345).
* Regularity: each triangle lies in one closed s-strip (L(i,j): [(i+j)h,(i+j+1)h], U(i,j): [(i+j+1)h,(i+j+2)h]),
  inside which moving breaks never meet fixed breaks, so Ψ is C² on the open strip with second derivatives that
  extend continuously to the closed strip; the Taylor identity holds on the closed tetrahedron.

## 2. Soundness of the full certificate

### 2.1 Code audit (c2b_exact.py, c2b_common.py, c2b_certify.py)
* **Vertex values** (l.128-177). Segment weights A = N(t₁M₀−M₁), B = N(M₁−t₀M₀) are the exact P1 hat integrals;
  interval arithmetic in `_seg` (l.86-99) is correct for either sign of t, and clipping A_lo, B_lo at 0 is valid
  (A, B ≥ 0 mathematically). Lattice offsets: T3 uses d = k − i + jj (t = u−p+K+e), T2 uses d = k − j − jj
  (t = v−m+K−e), T1 at a node with s' = qh on the grid anti-diagonal uses nodes (k, q−k). Upper bounds are taken
  with `pick` = hi for W ≥ 0, and `certify` refuses any negative nodal value (l.333-334), so the supersolution
  lemma's w ≥ 0 hypothesis and the `pick` logic are both covered. All sums are integers at scale 2^-(P+Q); no
  rounding inside sums. "Exact" in STRATEGY §5.2 means *rigorous enclosure*, which is what is needed. c7 enclosures
  (`Phi_iv`, `phi_iv`, c2b_common.py:65-75) reproduce c7_gaussian.Phi/phi with √(2π) cached — same primitives.
* **Certified condition** (l.340-345): for each cell and slab, vmin is taken over all prism vertices (both slab
  ends, l.342), err is ceiled, `slack <= 0` fails. Slabs (jj, 1), jj < J, tile [e_lo, e_hi]; margins are computed at
  every lattice drift jj = 0..J (l.184-186). Cells tile R exactly (L/U over p+m ≤ 4, AXP/AXM over the axis tails).
* **Scaling / bump loop / block proposal** (c2b_certify.py:91-139): purely a search for a candidate; soundness does
  not depend on it because every returned value comes from `EX.certify` on the final integer vector. The bump loop
  terminates (≤ 65 attempts) and a failure is reported as `certified: False`.
* **Taboo / C_T**: K̂ omits exactly the atom window (the only route to (0,0)); max_R ŵ = max nodal value for P1.

### 2.2 Independent evaluator (reviewer code, SCR/review_C2B/rev_common.py)
Written from the model, not from c2b code: decomposition in the increment z (not in (s,y)), exact breakpoints
(p' = kh, m' = jh, window ends, K−p, m−K), own P1 point location, linear pieces integrated against φ(z+e); fast
float mode (geometry exact for dyadic N, p, m, e) and a rigorous mode (Fractions + c7 intervals).
* T1 (`t1_vertex.py`, N ∈ {4, 10}, 9 declared drifts × {V/t, RND, SPK} × {whole, taboo}): **75 024 node
  evaluations, 0 outside the certifier's rigorous [lower, upper] vertex enclosures**. Negative control (evaluator at
  the mirror drift −e, a different kernel): detected in 128/128 cases with e ≠ 0 (at e = 0 it is the same kernel,
  as expected).
* Cross-check vs brute-force midpoint quadrature (40 000 steps): max deviation 2.1e-5 (consistent with midpoint
  error at the taboo jump).

### 2.3 Attack results (declared drifts only; exact-geometry evaluator; see §3 for the FD test)
T3/T3b (`t3_attack.py`, `t3b_loadbearing.py`): family α·g with g = the float proposal, whose vertex residual is ≈ 0
— every between-vertex deficit of α·g is a pure interpolation effect, so this is the most err-sensitive candidate
family available. α = 1 + k·2^-24; k_v = smallest k passing a *vertex-only* check (err ignored), k_c = smallest k
accepted by `certify`, and a dense interior scan (every cell, 8–12 dyadic interior points per cell + all nodes) of
r(x) = w − 1 − K_e w at k_c.
Cases: N=4 all 9 drifts × {whole, taboo} (14 certifiable; whole at e ∈ {0, ±1/4} is not certifiable with α ≤ 9 at
this coarse mesh — a tightness fact, not a soundness one), N=4 slabs [3,7/2] and [−7/2,−3] (drift scanned at
eighths of h across every slab, 31 410 (x, e) samples per case), N=8 at e ∈ {±1, 1/2, 3} × 2 kinds.
* **Accepted candidates never violate**: in all **26/26** certifiable cases the accepted α_c·g has sampled min
  r ≥ 0 (0 negative points; 2 273–31 410 samples per case; `t3b_N4_point.log`, `t3b_N4_slab.log`,
  `t3b_N8_point.log`, and `t3_N4_point.log`). No counterexample.
* **Rough candidates** (`t3c_rough.py`): g' = g + ε·RND (ε ∈ {0.01, 0.05} of max g, kinks of random sign at every
  node), bisected to the certify threshold at N=4, e ∈ {±1/2, ±1, 3}, both kinds: 18/20 certifiable, **0 negative
  residuals** over 4 385 interior points each (smallest sampled min r is positive, 0.015).
* **err is load-bearing and correctly signed**: at k = k_v (α−1 = 2^-24) the vertex-only check ACCEPTS, `certify`
  REJECTS, and the scan finds interior points with r < 0 (685–4 136 per case); the worst point is confirmed
  **rigorously** (c7 interval enclosure of r entirely below 0) in **26/26** cases, including both slabs. So a
  certifier without the §5.3 term would be unsound, and the reviewed one rejects these candidates for the right
  reason.
* **Conservatism** (not soundness): the certified α_c − 1 exceeds the sampled true threshold by 1.6–17× pointwise at
  N=4, 1.8–16× at N=8, 17–41× on the N=4 slabs (err is a sum of absolute terms; see N4).
* **Planted-invalid candidates** (`t4_wrong.py`, N ∈ {4, 8}, e ∈ {1/2, 1, 3}): taboo certificate checked against
  the whole kernel; whole certificate checked at another declared drift (e/2 or 1, and −e); alarm moved inward
  (nodes with p or m ≥ 9/2 set to 0); 0.999·V_h — **30/30 rejected**. All are also rejected by a vertex-only check
  (10–1 040 failing cells), as are the author's C1/C2/C3 controls: gross planted errors do not probe err (see §3).

## 3. Test adequacy

### 3.1 The author's evidence, audited
* **FD-domain fix (PROGRESS step 17): the fix is right.** The rectangle sampler (`c2b_checks.hessian_fd_check`,
  l.40-47) draws y from the p-range and s from the strip, so m = s − p ranges over a set wider than the cell's
  m-range, where the Lm-lattice bounds are not claimed (see §1.3). The corrected sampler
  (`hessian_fd_check_cell`, l.89-107) keeps every stencil point inside the cell (margin 3 steps; I checked all six
  stencil offsets of the (s,y) mixed difference map to (p±d, m), (p−d, m+2d), (p+d, m−2d), which stay in the cell).
  The exceedance at U(3,8), m = 0.4805 is exactly the predicted out-of-domain effect, not evidence against §5.3.
* **Coverage of the author's FD check is thin** (reconstructed: `random.Random(7).sample(range(len(cells)),120)`,
  identical for every drift and kind because the seed and the cell list are fixed):
  N=10 — 68 L, 51 U, 1 AXM, **0 AXP**, only 7 cells with s < 1; N=20 — 63 L, 57 U, **0 axis cells**, 9 cells with
  s < 1. The p-axis tail (AXP), the whole taboo s < 1 correction (STRATEGY l.148-149) beyond ~16 cells, and every
  block slab (je = 1) were **never FD-checked**. Only W ∈ {V_h, t_h} (smooth) was used, never a rough W.
* **Certify-path negative controls do not reach the err path.** C1 (0.97×/0.999× V_h) fails in 1620/1620 cells —
  a vertex failure; C2 notches fail at vertex margins (2–258 cells); C3 is a sign flip detected by comparison with
  float truth, not by `certify` failing. A certifier with err ≡ 0 would pass the same controls. The only evidence
  for §5.3 in the stream is the sampled FD check, which does not go through `certify`.
* C11 kernel check (`c11_kernel_check`) uses an affine w = A − Bm, which has no kinks: it does not exercise the
  kink-sum or T1 piece logic of the vertex evaluator.

### 3.2 Reviewer's gap-filling tests (all at declared drifts; scripts + JSON in SCR/review_C2B/)
| test | coverage | result | control |
|---|---|---|---|
| T1 vertex values vs independent evaluator (`t1_vertex.py`) | N ∈ {4,10}; all 161/881 nodes; 9 drifts; W ∈ {V/t, RND, SPK}; whole+taboo; 75 024 node evals | 0 outside rigorous enclosure | mirror-drift kernel detected 128/128 (e ≠ 0) |
| T2 exhaustive FD of `hessian_bounds` (`t2_fd.py`) | **every cell** (L, U, AXP, AXM) of N=4 (264) and N=8 (1040); 9 drifts point-wise + slabs [3,7/2], [−7/2,−3] (drift sampled inside each slab, y probed also through e); W ∈ {V/t, RND, SPK, ALT(checkerboard)}; 124 runs, 184 704 points, 578 944 components | **0 exceedances** beyond float noise; max FD/bound 0.9988 (yy), 0.9905 (AXP), 0.9904 (y via e in a slab) | ×0.5 bounds flagged in 77/124 runs, ×0.9 in 64/124 (bounds are sharp for V/t and ALT; loose for RND/SPK) |
| T3/T3b end-to-end (`t3_attack.py`, `t3b_loadbearing.py`) | 26 certifiable cases: N=4 (9 drifts, 2 slabs), N=8 (4 drifts); every cell scanned | 26/26 accepted candidates with 0 negative sampled residuals | **err-path control**: vertex-only accepts, certify rejects, interior violation proved rigorously, 26/26 |
| T3c rough candidates (`t3c_rough.py`) | 20 cases, N=4 | 18 certifiable, 0 negative residuals | — (soundness scan) |
| T4 planted-invalid (`t4_wrong.py`) | 30 candidates, N ∈ {4,8} | 30/30 rejected | all vertex-detectable |

Reproduce (from SCR/review_C2B/, python 3.14, stdlib; every script guards its drifts and logs to the redirected
ledger SCR/review_C2B/REVIEW_LEDGER.jsonl, 16 entries, 0 LEAK_FLAG, 0 entries in NS/ledger):
`python3 -B t1_vertex.py 4|10`; `python3 -B t2_fd.py 4 point RND,VT 4`; `… 4 point SPK,ALT 4`;
`… 4 slab VT,RND,SPK,ALT 4`; `… 8 point VT,ALT 2`; `python3 -B t3_attack.py 4 point 12`;
`python3 -B t3b_loadbearing.py 4 point 8`; `… 4 slab 6`; `… 8 point 4 whole,taboo 1/2,1,3,-1`;
`python3 -B t3c_rough.py`; `python3 -B t4_wrong.py`. Outputs: t1_vertex_N*.json, t2_fd_N*.json, t3*_*.json/log,
t4_wrong.json. These outputs are validation-drift certificate artifacts: latent proxies under amendment 2 R2.3;
this review quotes only pass/fail counts, ratios and residual signs from them.

Ratios > 1 appear only at e ≤ −3 in cells where the bound itself is < 1e-12; `t2_diag.py`/`t2_diag3.py` show
|FD| ≈ 3e-11–1e-10 there, jumping between 0 and one ulp/d² as the step changes — float noise, below the absolute
tolerance, not an exceedance.

## 4. Claims vs code; cell-independence; A0 floor

### 4.1 Claims that outrun code (S3/S7)
| claim | location | finding |
|---|---|---|
| "Sanity checks with w ≡ const reproduce the window mass … and its second derivatives" | STRATEGY.md:153-155 | **no producer**: no script, function or result in gen/ performs it (grep for const/window mass: only c2b_float.py:38 `Grid.const`, unused for this) |
| "agrees with brute-force z-quadrature to 5e-9" | STRATEGY.md:161-162, ROUTE_SUMMARY G6, PROGRESS step 5 | `c2b_pointeval.direct_quadrature` exists but has **no committed caller or result file** |
| "Every pointwise run certified with no bumps beyond 3" | C2B_ROUTE_SUMMARY.md:131 | **false**: results/point_0_N40_whole_P1.json has `bumps` = 5 (block_1_2_11_20_N40_whole: 4) |
| G4 "deterministic", G9 "certificate is a pure function of the declared inputs" | C2B_ROUTE_SUMMARY.md:21,26 | the *certificate* (certify on a given W) is; the *reported value* is not: the rung ladder stops on measured CPU time (c2b_certify.py:192, `cpu * 8 > BUDGET_CPU`), and the proposal g is float (libm erfc/exp) and rounded to 2^-40, so W — never persisted in results/ — may differ across machines; a certificate cannot be re-verified without re-running the float proposal |
| "vertex values exact" | STRATEGY.md:92-100 | they are rigorous *enclosures* (upper bounds) — sufficient; wording only |
| signed cross term "∑λ_i d_s d_y ≤ r_s r_y/4" | STRATEGY.md:112 | the proof needs ∑λ_i\|d_s\|\|d_y\| ≤ r_s r_y/4 (Cauchy–Schwarz), since ξ_i differ; the code implements the correct absolute form; wording only |
| 30/30 point and 18/18 block certificates, controls detected, fdcheck 7200 points / ×0.05 20/20 / ×0.98 12/20, max 0.9989 | ROUTE_SUMMARY §2 | **verified** against results/*.json and results/fdcheck_r1.json |

### 4.2 Cell-independence
The certificate path (c2b_common, c2b_exact, c2b_float, c2b_certify) performs no file I/O and reads no registry,
cover, cell index or per-cell constant (grep: no open/read_text/json.load/glob). The only inputs are K, H, the
drift set, N and the declared numerics. The stopping rule `ladder_decision` (c2b_certify.py:183-195) is a function
of the rung sequence (certified values + CPU seconds) only — **cell-independent**, and not target-informed; its
defect is non-determinism (CPU time), not cell dependence (condition C2).

### 4.3 A0 floor (A0_TIGHTNESS.md §1)
Proof checked: with W₀ = 0, W_{n+1} = 1 + sup_{e∈E} K_e W_n, positivity gives W_n ≤ w for any common supersolution
w ≥ 0 and W_n ↑; monotone convergence (per e) gives sup_e K_e W_∞ = lim sup_e K_e W_n, so W_∞ is the minimal
fixed point W*_E ≤ w; and W*_E ≥ 1 + K_e W*_E makes W*_E a K_e-supersolution for each e, hence ≥ V_e. So
Ā(E) ≥ Λ*(E) ≥ sup_E Λ holds **provided Λ*(E) is defined as this minimal fixed point** (the text defines W*_E by
the fixed-point equation only; the proof uses the value-iteration limit — state it). The measured Λ* values are
non-certified float diagnostics on a finite drift grid (a lower estimate of the continuum Λ* at the same mesh),
labelled as such. The sentence "the same floor applies to I1's Ā and I2's Ā" is correct for any certificate that
proves a common supersolution over the block; I did not verify which I1/I2 constants are of that form.

## 5. FREEZE_READY assessment

The pre-freeze item the author named (ROUTE_SUMMARY §3 item 7) is discharged: **STRATEGY §5.3 is correct** —
every second-derivative formula re-derives, the code implements each term with an absolute-value bound over
ranges that contain the cell × slab, the claimed domain is the right one, and the Taylor/Popoviciu inequality is
used with the right sign, constant and geometry. Independent evidence agrees: zero FD exceedances over every cell
kind (incl. AXP and slabs) with rough and smooth W, and an end-to-end attack in which the err term is shown to be
load-bearing (vertex-only acceptance of rigorously non-supersolutions) while no accepted candidate violates.

FREEZE_READY *as a closure-only certifier strategy* is therefore justified **for the mathematics and the
certificate code**, but the freeze *package* is not yet executable/auditable as written: conditions C1–C5 below
must be met (and re-qualified on non-target drifts) before any freeze. None of them touches §5.3. Route state
VALIDATED_NON_TARGET is confirmed; CLOSURE-ONLY under floor r2 is confirmed (third implementation; Ā, τ, C_T only).

Gates (reviewer's view): G2 PASS (was "PASS with caveat"; caveat discharged); G4 PARTIAL (C1, C2); G5 PASS;
G6 PASS after this review (independent evaluator + exhaustive FD + load-bearing control); G7 PASS; G8 PASS with
notes N1–N2; G9 PASS subject to C1–C3; G10 as stated by the author (pointwise PASS, blocks PARTIAL).

## 6. Blockers / conditions / notes

**Blockers: none.**

**Conditions (must hold before a freeze; none requires re-deriving §5.3):**
* **C1 — persist and re-verify.** Store the exact integer nodal vector W (and Q) of every certificate, with its
  SHA-256, and provide a verifier entry that runs `c2b_exact.certify` on a stored W without the float proposal.
  Today results/*.json hold α, β and w(a) only, and W depends on platform float (c2b_float, libm erfc/exp) rounded
  to 2^-40, so a certificate cannot be audited bit-for-bit elsewhere.
* **C2 — deterministic stopping rule.** Replace the CPU-time budget (c2b_certify.py:192) by a declared rung set or
  an operation-count budget, so the reported value is a pure function of declared inputs (ROUTE_SUMMARY G4/G9 claim
  this today; it is not true).
* **C3 — governed execution path.** The certificate path imports ov_quarantine (c2b_common.py:20-23) and
  `Setup`/`run` refuse the quarantine band (c2b_exact.py:65, c2b_certify.py:111). A future target execution would
  need a post-freeze code edit unless the freeze binds, in advance, how an authorized run is admitted (e.g. a
  frozen authorization file checked by the guard). Bind ov_quarantine.py's hash too.
* **C4 — claims.** Remove or produce: the "w ≡ const" sanity check (STRATEGY.md:153-155) and the "5e-9 brute-force"
  check (no committed caller of `direct_quadrature`); correct "no bumps beyond 3" (C2B_ROUTE_SUMMARY.md:131; actual
  maximum 5); write §5.2 "rigorous enclosure" for "exact"; write the cross term at STRATEGY.md:112 as
  ∑λ_i|d_s||d_y| ≤ r_s r_y/4; define W*_E in A0_TIGHTNESS §1 as the minimal fixed point (value-iteration limit).
* **C5 — qualification evidence inside the package.** Add (i) an FD check over *every* cell kind (AXP never
  sampled, AXM once, ≤ 16 cells with s < 1, no slabs, smooth W only in fdcheck_r1) with at least one rough W, and
  (ii) an err-path negative control through `certify` (a vertex-only-acceptable candidate that `certify` rejects,
  with a rigorously confirmed interior violation — the design of SCR/review_C2B/t3b_loadbearing.py). The existing
  certify-path controls (C1, C2) are all vertex-detectable and cannot fail for a certifier that drops err.

**Notes:**
* **N1 (quarantine, informational).** Validation blocks/truth grids/robust runs used drifts in (1/2, 3/5] and
  (1, 11/10] (results/block_1_*, truthgrid_1_*, robust_1_*). They are outside the band and were pre-declared by the
  author's own rule (PROGRESS step 8), but outside the preamble's declared drift list. Under amendment 2 they are
  latent proxies (R2.3). Future qualification blocks should use |e| ≥ 3 (as this review did).
* **N2 (quarantine, action for the coordinator).** C2B_ROUTE_SUMMARY.md §2.1 and A0_TIGHTNESS.md §2 print
  validation-drift Λ/τ/C_T values and were last edited after amendment 2 was written; they must not be copied into
  any cross-route or handover text (R2.3). C2B_ROUTE_SUMMARY.md:49 compares measured tightness with "the brief's"
  motivating percentage; I could not locate the brief to confirm that scale is not tail-derived — if it is, that
  sentence is an R2.1/S8 juxtaposition and should be struck from any handover.
* **N3 (hygiene).** `c2b_float.FloatKernel.__init__`, `c2b_pointeval.K_at` and `direct_quadrature` take a drift
  without calling the guard (every current caller guards first).
* **N4 (tightness only).** The φ(s'−y) = φ(η) term is bounded on the Lp lattice with the p-range
  (c2b_exact.py:299), one mesh step wider than the exact η-range; bounds are not mirror-symmetric, and the
  accepted α differs between ±e (T3b, N=4) although the true threshold is symmetric. Also err is a sum of absolute
  terms: the certified α−1 exceeds the sampled true threshold by 1.6–17× at N=4 (up to ~40× on slabs).
* **N5 (reviewer's own incident).** The first version of my T4 script generated e' = e/2 = 3/2 for e = 3;
  `ov_quarantine.guard_drift` refused it before any evaluation (DRIFT_BAND_REFUSED). The rule was fixed
  (e' = 1 for e = 3). Zero evaluations occurred in the band. Recorded in SCR/review_C2B/PROGRESS.md.
