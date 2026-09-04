# P5Y — FIRST BINDING CHECKPOINT
# K1 / `R_max < 2` PRODUCTION CERTIFICATE CAMPAIGN

**BINDING.** Once this checkpoint is frozen and anchored, the production campaign
it governs may not invent scientific, numerical, budget, scope or verdict rules
after seeing results. Everything a production run needs is fixed here.

**This document creates no result. `P5Y_PRODUCTION_RUN = NO`.**

```text
P5_ORIGINAL_VERDICT = PARTIAL      P5X_FINAL_VERDICT = PARTIAL
P5X_CAMPAIGN = ARCHIVALLY_COMPLETE
P5Y_GATE1 = PASS_ROUTE_B_SUPPORTED     P5Y_GATE2A = SR_PRECISION_PASS_256
P5Y_GATE2B = SR_COVER_PASS_MEASURED    P5Y_GATE2C = M2_ASSEMBLY_INCOMPLETE_EXTERNAL
P5Y_GATE2CBIS = M2_ASSEMBLY_B_PASS     P5Y_GATE2D = SR_REALCANDIDATE_FAIL_REPRESENTATION
P5Y_GATE2E = SR_METRIC_FAIL_CANDIDATE  P5Y_GATE2F = SR_METRIC_B_PASS_256
```
Gate-2D and Gate-2E remain `FAIL` permanently. Their failure modes were
measurement-design and implementation-governance issues, never established
mathematical contradictions, and nothing here reinterprets them.

---

## 1. Sole scientific target

```text
K1:  for every frozen detector D and every frozen m,
     certify   R_max(D,m) = sup_{e in R} | R_{D,m}(e) |  <  2
```

**Explicitly out of scope, and not advanced by any outcome of this campaign:**
`K2` (`s_min > 0`), `K3` (finite / useful `M_2`), `K4` (`H2`), `K5` (`H3a`),
novelty, and global Level-4 closure. A `K1_CLOSED` verdict does **not** close P5
(§17).

## 2. Frozen scientific scope — resolved from authoritative artifacts

Resolved from `p5x_global_nonlinear_dynamics/FROZEN_SCOPE.md` §1, not assumed:

```text
detectors (exactly 2)
  CUSUM  k = 1/2, h = 5, two-sided, inclusive post-update test, plus-arm priority
  SR     symmetric two-chart, A = 520.886133602749, stored y = log(1+R), y_0 = 0,
         inclusive test on max(y+ + z - 1/2, y- - z - 1/2), b_SR = log(1+A) [erratum D1]
observations  raw_t ~ iid N(0,1), Delta = 0, z_t = raw_t - e
windows       m in {1, 2, 3, 5}
stopping      tau inclusive, w = min(m,tau), Stage-D convention A
```

**Cartesian production scope: `2 detectors x 4 m-values x compact e-cover`,
plus the analytic far-field splice.** Eight `(D,m)` cells, all required. No
result-dependent deletion of difficult cells; no `m`-specific narrowing after
freeze.

## 3. Canonical `R_{D,m}(e)` — exact, for every frozen `m`

Raw-variable objects (Gate-1 §6 / Gate-2C-bis, an exact corollary of `P5X-T1`'s
`L1`; `u = c_D - x^+`, `l = x^- - c_D`, all `e`-free in `x`):

```text
S_0^raw = rho_1^raw = phi(u+e) - phi(l+e)                  closed form
h_1     = 1 - K_e 1 = 1 - Phi(u+e) + Phi(l+e)              closed form
h_j     = K_e h_{j-1}                     (j >= 2)
S_r^raw = K_{raw,e} h_r = K_{z,e} h_r + e K_e h_r          (r >= 1)
F_r     = (I - K_e)^{-1} S_r^raw
d_e h_1 = -S_0^raw                                          exact identity
```

**General closed assembly** (derived here from `P5X-T1(c)` by substituting
`raw = Z + e`; the coefficient of every finite term collapses to `1/t - 1/m`):

```text
R_{D,m}(e) = (1/m) sum_{r=0}^{m-1} F_r(x_0)
           + sum_{t=1}^{m-1} ( 1/t - 1/m ) sum_{r=0}^{t-1} ( K_e^{t-r-1} S_r^raw )(x_0)
```

Written out for every frozen `m` — these are the formulas production must use:

```text
m = 1:  R_1 = F_0
m = 2:  R_2 = (1/2)(F_0 + F_1) + (1/2) S_0
m = 3:  R_3 = (1/3)(F_0 + F_1 + F_2) + (2/3) S_0 + (1/6)( K S_0 + S_1 )
m = 5:  R_5 = (1/5)(F_0 + F_1 + F_2 + F_3 + F_4)
            + (4/5)  S_0
            + (3/10) ( K S_0 + S_1 )
            + (2/15) ( K^2 S_0 + K S_1 + S_2 )
            + (1/20) ( K^3 S_0 + K^2 S_1 + K S_2 + S_3 )
```
(all evaluated at `x_0`; `S_r` abbreviates `S_r^raw`). `m = 1` and `m = 2` match
Gate-2C-bis exactly; `m = 3` was verified against the probabilistic
decomposition `E[Rbar] = sum_t (1/min(m,t)) sum_{j<min(m,t)} E[raw_{tau-j}; tau=t]`
term by term during this design.

```text
R_max(D,m) = max( sup_{e in [0, e_star_D]} |R_{D,m}(e)| ,  sup_{|e| >= e_star_D} B_D(e) )
```
with `e < 0` supplied by the exact oddness `P5-T3`, and the second term
discharged analytically by `P5X-T3` (§9).

## 4. Frozen architecture — Route B, as validated

```text
A  raw-variable reformulation, no external "+e" cancellation term anywhere
B  CUSUM backend: recentred Hermite phi-expansion (order 120), exact-dyadic
   Chebyshev candidate degree 12, R2 fast Bernstein range bound, depth ladder
   (0,1,2,3), 256-bit Arb
C  SR backend: degree-8 composed contraction, candidate bidegree (16,16),
   256-bit Arb, patch grid 64 on [0,b_SR]^2, continuous minimal-safe panel rule,
   Gate-2F ASYMMETRIC P1 semantics (§5)
D  m-sharing: solved objects computed ONCE and consumed by every m (§10)
E  far-field splice: P5X-T3 discharges |e| >= e_star_D analytically (§9)
```
No architecture substitution after results. Any substitution requires a **new
successor checkpoint**.

## 5. `P1` rule — frozen, asymmetric, with explicit working precision

```text
eps_P1                 = 1e-3
P1_RULE_TARGET         = (1 - eps_P1) * 1e-9        solves for h_z
P1_CHECK_THRESHOLD     = 1e-9                       tests E_d
P1_HEADROOM_GUARD      = 1e-6                       HEADROOM_REL must exceed this
P1_RULE_WORKPREC       = 512 bits                   EXPLICIT -- fixes the Gate-2F
                                                    one-ulp provenance defect
HEADROOM_REL = ( P1_CHECK_THRESHOLD - E_d ) / P1_CHECK_THRESHOLD
```
The rule target **must be evaluated inside `workprec(512)`**, never at ambient
module precision — that is the exact Gate-2F discrepancy this checkpoint
repairs. Rule and check remain distinct semantic fields; both the `E_d`
comparison and the headroom are computed in Arb, not on floats. Expected
headroom `1.0e-3`, i.e. `1000x` the guard.

## 6. Acceptance metric — ABSOLUTE, proposition-derived

Carried from Gate-2E/2F unchanged. **The old relative `P2` is diagnostic only
and may never gate production.**

```text
scientific target R_MAX_LT_2      metric type ABSOLUTE
slack_R = 2.0     alpha = 0.1     w_target = alpha * slack_R = 0.2
```

Ledger (fractions of `w_target`; absolute values in CPU-independent units of `R`):

| component | fraction | absolute | covers |
|---|---|---|---|
| `B_cover` | 0.25 | **0.050** | `e`-cell Taylor model `h|R'| + (h^2/2) S_2` |
| `B_candidate` | 0.20 | **0.040** | candidate / source approximation |
| `B_kernel` | 0.20 | **0.040** | softplus + panel truncation |
| `B_other` | 0.20 | **0.040** | assembly, derivative equation, hull |
| `B_rounding` | 0.05 | **0.010** | exact-dyadic rounding |
| `B_interval` | 0.05 | **0.010** | Arb working-precision radius |
| `B_resolvent` | — | **0** | `C` is a MULTIPLICATIVE amplifier, never additive |
| reserve | 0.05 | **0.010** | **non-redistributable** |

```text
LOCAL_GATE_BUDGET = B_candidate + B_kernel + B_interval + B_rounding = 0.100
sum(allocated) = 0.190 <= w_target = 0.200
```

**Non-borrowing rule (§7 of the brief): NON-REDISTRIBUTABLE.** No component may
consume another's unused budget, and the reserve may never be drawn. No
redistribution rule is defined, therefore none exists. Post-result rebudgeting
is forbidden.

### 6.1 The `m = 1` tightening — a design decision made now, not later

Gate-2E derived its per-panel budget with a factor `1/2`, which is the `m = 2`
assembly coefficient on `F_r`. K1 covers **`m = 1` as well**, where that
coefficient is `1`. The production budget therefore uses the worst case over the
frozen `m` set:

```text
max_m (assembly coefficient on F_r) = max_m (1/m) = 1        (attained at m = 1)

delta_max(D, e)      = LOCAL_GATE_BUDGET / C_D(e_lo)
w_panel_max(D,e,P)   = LOCAL_GATE_BUDGET / ( C_D(e_lo) * n_panels(P) )
```
This is **twice as strict** as Gate-2E's cell budget. At the SR reference cell
(`e = 1/4`, patch `(17,11)`, `n_panels = 30`, `C_SR = 187.7472`) it gives
`w_panel_max = 1.7754e-05` against Gate-2E's `3.5509e-05`. Gate-2F's measured
`hhat_1` value of `2.9771e-08` still passes it by `596x`, but the tightening is
adopted because it is correct for the frozen scope, not because it is affordable.

`C_D(e_lo)` is evaluated at the **smallest `|e|` of each cell**, which is the
worst case by the drift monotonicity `M2` (§8).

## 7. Amplification bounds — per detector, with direction audit

Both detectors use a **drift-explicit monotone one-sided Bellman minorant**;
they do **not** share a formula, and each is frozen separately.

| | CUSUM | SR |
|---|---|---|
| source | `compute_optimization_r1/drift_minorant.py::drift_monotone_resolvent` | Gate-2B `sr_cover.py::sr_drift_monotone_resolvent` |
| chart | one-sided CUSUM, barrier `h = 5`, `k = 1/2` | one-sided softplus, alarm on the pre-update value at `log A` |
| grid | `[0, h]`, 100 cells, left endpoints (`M1`) | `[0, b_SR]`, 200 cells, left endpoints (`M1`) |
| horizon / bits | `n_max = 250`, 192 | `n_max = 250`, 192 |
| value | `C = min_t t / H_t(0)` | `C = min_t t / H_t(0)` |
| **type** | **UPPER** bound on `\|\|(I-K_e)^{-1}\|\|_inf = sup_x E_{x,e}[tau]` | **UPPER**, same |
| cross-check | `C(0) = 1232.84 <= certified N-01 1315.79` | `C(0) = 1205.94 <= certified 25000/19 = 1315.79`; `H_250(0)` reproduces the certified value to 17 s.f. |
| monotonicity | `M1` state-monotone envelope, `M2` drift-monotone one-sided walk (both proved in R1 `PROOF.md`) | same |

**Direction audit, mandatory before any cell runs.** `H_t` is a *lower* envelope
of the hit probability, so `t/H_t` is an *upper* bound on the resolvent norm. A
test asserts that an upper error-propagation bound never consumes a lower
resolvent bound, that `C(0)` does not exceed the certified cap, and that `C` is
non-increasing in `e` for both detectors. Failure ⇒ `K1_FAIL_GOVERNANCE`, before
the grid.

Neither bound uses the unproved `sup_e E[tau|e] = E[tau|0]` (P5X defect `D3`).

## 8. Compact cover — frozen per detector, from authoritative manifests

```text
CUSUM   e in [0, e_star_CUSUM],  e_star_CUSUM = c_D = 11/2 = 5.5
        cover: 323 sub-cells   (R1 optimized monotone-minorant cover on [0, e_star])
        rule:  h(e) = 1/(4 a C(e)), a = 2 phi(0), greedy walk, exact tiling
SR      e in [0, e_star_SR],     e_star_SR = c_SR = log A + 1/2
                                             = 6.75553146432147319284577138577
        cover: 322 sub-cells upper bound (309 lower), 9 bookkeeping outer cells,
               exact tiling, widths 5.196e-04 / 1.551e-03 / 3.133e-01 (min/med/max)
        patches: 4096 nominal, 3994 live, 102 excluded by the exact
               multiplicative invariant (xi+' - 1)(xi-' - 1) = xi+ xi- / e
        panels: 83,452 over live patches (n_z per patch, mean 18.89, NOT a global 28)
```

The authoritative machine manifests, not these prose numbers, govern:
`manifests/cover_sr.json` and `manifests/cover_cusum.json`, each carrying the
source artifact and its SHA-256.

**No adaptive cell splitting.** No split rule is preregistered, therefore none
exists. A cell that fails its budget fails the campaign under §13.

## 9. Far-field splice

```text
CUSUM  |e| >= 5.5                    SR  |e| >= 6.755531464321473...
theorem P5X-T3 (PROOF.md L3), majorant B_D(e) = phi(a) + sqrt( Phi(a) m_2(e) ),
        a = c_D - |e|,  m_2 = Phi(a) + |a| phi(a) + Phi(a)/(1-Phi(a))
certified sup_{|e| in [c_D, c_D+1]} B_D = 1.2649965374940489448718... < 2
        and B_D proved strictly decreasing beyond c_D + 1
valid for EVERY m simultaneously (on {tau = 1}, w = min(m,1) = 1 for all m)
```
Production numerics stop exactly at the compact boundary. **No numerical
extension beyond `e_star_D` "just to be safe" after results.** The splice
requires one certified evaluation per detector: `B_D` on `[c_D, c_D+1]` and the
monotonicity range — three outward-rounded Gaussian tail values, the cheapest
item in the campaign.

## 10. `m`-sharing solve DAG

Objects are defined **without reference to `m`** (`P5X-T1` `L1.5`–`L1.7`), so the
required sets are nested and the union over `m in {1,2,3,5}` equals the `m = 5`
set. Gate-1 `PILOT-MSHARE` verified nesting and the absence of any `m`-specific
solve; Gate-2C-bis measured the `m = 2` increment at `ratio_per_unit = 0.629`,
i.e. the accounting below is **conservative**.

```text
per detector, 19 certified functions (Gate-1 union, first moment):
  F_0..F_4      5   resolvent solves
  d_e F_0..F_4  5   derivative resolvent solves        -> 10 resolvent solves
  h_1..h_4      4   h_1 closed form; h_j = K_e h_{j-1}
  S_0..S_4      5   S_0 closed form; S_r = K_{raw,e} h_r

consumption:
  m = 1  <- F_0, dF_0
  m = 2  <- + F_1, dF_1, S_0
  m = 3  <- + F_2, dF_2, S_1, h_1
  m = 5  <- + F_3, F_4, dF_3, dF_4, S_2, S_3, S_4, h_2, h_3, h_4
assembly       finite kernel powers K^j S_r, j <= 3, per the §3 formulas
```
**The geometric cover (sub-cells x live patches x panels) is shared across all
`m` and is never multiplied by `m`.** The `19` is a FUNCTION count; the `24.5x`
unit multiplier of prior gates covered first *and* second moments and is
therefore **not** used here (§14).

## 11. Production Task 1 — `F_r` candidate qualification

The **first result-bearing task** of the campaign. Not a pilot: a production
task inside the binding campaign, frozen now.

```text
detector      SR                 (96% of projected cost; all candidate risk to date is SR)
object        F_0                (consumed by EVERY m, so maximally load-bearing)
drift         e = 1/4 exact      (the load-bearing near region; C_SR = 187.7472)
patch         (17,11) on grid 64 (R3's incumbent-worst patch)
why conservative  the object every m consumes, at the incumbent-worst patch, in the
                  region where the amplification is large -- not an easy case
candidate     bidegree (16,16), exact-dyadic at 2^-50
residual      certified by the EQUATION DEFECT, not by an approximation tail:
              delta_0 = || Fhat_0 - K_e Fhat_0 - S_0^raw ||  bounded by the
              reachable-set / patch range bound, then propagated as C * delta_0.
              (This is why a 2-D Chebyshev tail argument -- which Gate-2D showed
              is unaffordable for a non-separable object -- is not needed.)
guard         representation-complexity guard (§12) BEFORE kernel construction
budget        the ALREADY-FROZEN B_candidate = 0.040. No new budget is defined for F_r.
acceptance    C_SR(1/4) * delta_0 contribution <= B_candidate through the full
              propagated absolute chain, AND w_panel_total <= w_panel_max (§6.1),
              AND P1 (§5), AND the representation guard
```

**PASS** requires all of: valid construction; valid exact-dyadic representation;
rigorously certified residual; guard PASS; propagated contribution inside
`B_candidate`; `P1` and inherited guards PASS; no hidden high-degree path.

**FAIL ⇒ STOP the campaign immediately.** Do not proceed to any cover. The
frozen verdict is:

```text
K1_CAMPAIGN_FAIL_ARCHITECTURE
```
No repair inside this checkpoint. Any architecture repair requires a **new
successor checkpoint**.

## 12. Representation-complexity guard — production threshold, derived now

```text
COMPLEXITY_SCORE(call) = (deg_a + 1) * (deg_b + 1) * (composed_z_degree + 1)
hard bidegree limits:  SR candidates <= (16,16) ; CUSUM candidates <= (12,12)
composed z-degree:     SR 16*8 = 128 ; CUSUM 12 + 12 + 121 = 145
per-object scores:     SR  17*17*129 =  37,281      (Gate-2F measured, PASS)
                       CUSUM 13*13*146 =  24,674    (Gate-1/2C-bis measured, PASS)
PRODUCTION_COMPLEXITY_CEILING = 60,000 per composed-contraction invocation
```
**Derivation, from measured feasible objects and available compute, without
production results:** the two validated production object classes score `37,281`
(SR) and `24,674` (CUSUM). A ceiling of `60,000` admits both with `1.61x` and
`2.43x` headroom — enough to absorb a modestly denser real `F_r` coefficient
array at the same bidegree — while rejecting any degree escalation (bidegree
`(20,20)` would score `21*21*161 = 70,941 > 60,000`) and rejecting the Gate-2C
class of defect by three orders of magnitude (a degree-121 argument scores
`> 5.4e6`). It is **not** the pilots' `100,000`, which was a pilot-era ceiling
with no production justification.

The guard **fires before expensive kernel construction**, as a precondition, and
its ordering is asserted by test.

## 13. Production phase order — chosen for failure containment

```text
Phase A  checkpoint integrity + direction audits + Task-1 F_r qualification (SR)
Phase B  CUSUM compact certificate      323 sub-cells x 19 functions   ~27 CPU-h
Phase C  SR compact certificate         322 sub-cells x 19 functions  ~864 CPU-h
Phase D  all-m assembly (both detectors), per the §3 formulas
Phase E  far-field splice, both detectors
Phase F  final K1 adjudication (independent, §18)
```

**Justification, frozen.** Task 1 runs first and on SR because that is where
every candidate failure of this campaign's history has occurred, and it costs a
single cell. CUSUM then runs before SR because it is `~3%` of projected cost yet
exercises the identical raw-variable assembly, the identical `m`-sharing DAG and
the identical budget ledger: a scientific or governance failure surfacing in
CUSUM costs `~27` CPU-hours instead of `~864`. SR follows. No order optimization
after observing production outcomes.

## 14. CPU model — audited, and re-scoped to K1

The carried P5Y programme model is **reproduced exactly** from measured
primitives by `code/cpu_model_k1.py`:

```text
( SR 2227.7928 + CUSUM 70.1308 ) x 1.17 x 1.15 = 3091.856205551252 CPU-h
carried programme central (Gate-2B)            = 3091.856205551252 CPU-h   IDENTICAL
```

**That model covers `K1 + K2 + K3 + K4 + K5`.** This checkpoint governs `K1`
alone, so two of its factors leave scope. Both removals are *derivations from the
frozen scope*, not optimistic re-estimates:

```text
function count  49 -> 19    the 49 = 24.5 units x 2 spans FIRST AND SECOND moments;
                            Gate-1 MSHARE's union for the FIRST moment alone is 19,
                            because K2 (s_min) and K3 (M_2) are out of scope
C3 factor       x1.17 -> 1  the +17% is the H2/H3a derivative rung, i.e. K4/K5, out
overhead        x1.15       RETAINED (assembly, resolvent, auditor replay)

K1 scope factor = (19/49) / 1.17 = 0.331415
  SR    K1-scoped   863.838 CPU-h        CUSUM K1-scoped    27.194 CPU-h
```

Band multipliers, each attached to a named, already-measured assumption:

| band | K1 CPU-h | multiplier and its provenance |
|---|---|---|
| optimistic | **656.9** | `x0.66805` — Gate-2C-bis MEASURED `ratio_per_unit = 0.629` applied to the 17 non-`m=1` functions — **and** `x0.95963` from the SR cover lower bound 309/322 |
| **central** | **1024.7** | no multiplier: measured geometry, degree 8 @ 256 bits, `ratio_per_unit` conservatively held at 1.0 |
| **conservative** | **1231.7** | `x1.202` — Gate-2A measured `t_panel(384)/t_panel(256)`, i.e. a production SR candidate forcing 384 bits |
| worst plausible | **1539.6** | `x1.25` on top — the Gate-2B cover walk used a monotone ENVELOPE, so the true cover may be larger |

```text
SOFT EXPECTED BAND = [ 1024.7 , 1231.7 ] CPU-hours       (central .. conservative)
```

Gate-2B's own `conservative`/`worst` rows (4637.8 / 6183.7) assumed `m>1` cost
factors of `1.5x` and `2x`. **Those assumptions are superseded**: Gate-2C-bis
subsequently *measured* the ratio at `0.629 < 1`, so they now describe a régime
known not to occur, and are not carried. The central band, which never depended
on them, is carried unchanged and reproduces exactly.

The pre-freeze reconnaissance estimate for this checkpoint read
`618 / 1024 / 1224 / 1522`. The derived values above supersede it; the `<= 0.7%`
difference is the CUSUM scope factor, which the script applies uniformly instead
of by hand.

## 15. Hard CPU cap — derived, not chosen for convenience

```text
HARD_CPU_CAP = ceil( beta * K1_conservative ) = ceil( 1.5 x 1231.673 ) = 1,848 CPU-hours
```

`beta = 1.5` is **governance-inherited, not invented here**: it is the same
safety factor Gate-2C-bis froze and justified for `m>1` per-function
uncertainty, applied to the conservative rather than the central band.

The resulting cap is defensible in three directions at once:

```text
1,848 / 1,539.6 (K1 worst plausible) = 1.2003   the cap does NOT bind below the
                                                campaign's own worst projection
1,848 / 1,024.7 (K1 central)         = 1.8035   the cap DOES genuinely constrain
1,848 / 4,597   (programme worst)    = 0.402    consistent with K1 being ~1/3 of
                                                the programme's scope (0.331)
```

The programme-level figure of `4,597` CPU-h is the upper reference for the
**whole** P5Y line (`K1..K5`) and is **not** adopted as this campaign's cap: K1
is a strict sub-scope, and capping a sub-scope at the whole line's worst case
would make the cap non-binding and therefore meaningless.

## 16. CPU stop semantics

On reaching `HARD_CPU_CAP`:

```text
1  stop launching new work immediately
2  preserve every completed artifact and every partial log
3  mark every uncomputed cell explicitly as NOT_COMPUTED (never absent, never inferred)
4  PASS may NOT be inferred from partial coverage under any circumstance
5  final verdict is forced to   K1_INCOMPLETE_BUDGET
6  no cap extension within this checkpoint -- a larger cap needs a successor checkpoint
```
An external interruption that is not a budget breach yields
`K1_INCOMPLETE_EXTERNAL` instead. The distinction is frozen: budget exhaustion is
a campaign property, external interruption is not.

## 17. `K1_CLOSED` does not close P5

Frozen, and binding on every downstream document:

```text
if P5Y_K1_VERDICT = K1_CLOSED then
     K1_CLOSED_BY_P5Y_BINDING_CAMPAIGN
     P5_SCIENTIFIC_LINE_STATUS = PARTIALLY_REPAIRED_BY_SUCCESSOR      (unchanged)
     K2, K3, K4, K5 remain OPEN ; NOVELTY_STATUS = NOT_ESTABLISHED
     LEVEL4_GLOBAL_CLOSURE = NO
```
P5 remains `PARTIAL`. P5X remains `PARTIAL`. Neither is recoloured by any K1
outcome.

## 18. Independent adjudication — mandatory

The producing script may **not** self-award `K1_CLOSED`. A separate adjudicator,
not the producer, must verify every item in `adjudication/ADJUDICATION_CONTRACT.md`:
checkpoint ancestry and hash; protected-tree integrity; absence of post-freeze
amendments; exact scientific scope (2 detectors x 4 m); cover completeness and
exact tiling; far-field splice; budget arithmetic and non-borrowing; candidate
identities; complexity guards; precision policy; `P1` headroom; detector/m
coverage; CPU accounting and work conservation; the final theorem inequality;
and the absence of hidden retries or substitutions.

## 19. Protected tree and namespace

Production may write **only** inside
`level4/closure_proofs/p5y_k1_binding_campaign/{results,certificates,logs}`
plus a declared scratch path. Every other tracked path — all of P5, P5X, and all
P5Y gate namespaces — is immutable for the campaign's duration. Digests are in
`manifests/protected_inputs.json`.

## 20. Precision and degree policy — no adaptation

```text
SR production precision      = 256 bits          (Gate-2A selected, Gate-2F confirmed
                                                  with a genuine candidate)
CUSUM production precision   = 256 bits          (ra_certifier BITS, validated Gate-1)
P1_RULE_WORKPREC             = 512 bits          (§5, explicit)
PRECISION_ESCALATION_ALLOWED = NO
DEGREE_ADAPTATION_ALLOWED    = NO
POST_RESULT_REBUDGETING      = NO
```
If a cell fails because the 256-bit interval radius is too wide, the campaign
**fails or stops** under §13/§21 — it does not silently rerun at 384 or 512.
Candidate degree families are frozen by object class: SR state candidates
`(16,16)`; CUSUM candidates `(12,12)`; backward/source objects at the same
bidegree as their detector's class. Each carries the residual gate of §6 and the
complexity gate of §12. Failure means STOP.

## 21. Early scientific STOP rules — stop immediately, every one of them

```text
S01  a certified cell enclosure fails to lie strictly inside (-2, 2)   -> STOP
S02  candidate budget B_candidate cannot be met                        -> STOP
S03  representation-complexity guard fails                             -> STOP
S04  amplification direction invalid (lower bound used as upper)       -> STOP
S05  any protected artifact mutated                                    -> STOP
S06  checkpoint hash mismatch                                          -> STOP
S07  cover gap or overlap detected                                     -> STOP
S08  far-field splice mismatch (numerics do not meet e_star_D exactly) -> STOP
S09  P1 headroom below 1e-6                                            -> STOP
S10  unapproved precision or degree substitution                       -> STOP
S11  budget-ledger violation or attempted redistribution               -> STOP
S12  deterministic work-conservation mismatch (§22)                    -> STOP
S13  CPU cap breach                                                    -> STOP (§16)
```
No "continue to see what happens". This checkpoint marks **no** later work as
non-decisive diagnostics, so no exception exists.

## 22. Deterministic work partitioning and conservation

The K1 certificate is **deterministic certified numerics**. There is no
stochastic path in the verdict.

```text
RNG_NOT_LOAD_BEARING = YES
```
Monte Carlo may appear only as *correspondence* evidence in `logs/`, never in a
certificate or a verdict, and gate `G8`'s firewall from P5X applies unchanged.

Work is a set of integer-addressed deterministic units:

```text
unit = (detector, e_subcell_index, function_id)
total_units = CUSUM 323 * 19 + SR 322 * 19 = 6,137 + 6,118 = 12,255
partition: shard k receives units with index in [ floor(k*N/S), floor((k+1)*N/S) )
required invariants, all tested:
  sum over shards of |shard| == total_units EXACTLY   (no ceil-per-shard overrun)
  no overlap, no omission, deterministic address mapping
  aggregation identity: recomputing from per-unit artifacts reproduces the hull
  every unit individually recomputable from its stored record (§23)
```
No aggregate-only representation. An invalid shard must be removable and the
campaign recomputable without it.

## 23. Cell output contract

Every production cell record must carry, at minimum:

```text
detector | m-relevance | e_interval [lo,hi] | state patch / cover cell id
candidate_id | candidate_degree | candidate_residual
kernel_residual | resolvent_amplification_bound C(e_lo) | rounding_error
interval_radius | propagated_absolute_half_width | allowed_absolute_half_width
budget_usage_by_component {B_candidate,B_kernel,B_interval,B_rounding}
P1_E_d | P1_headroom_rel | complexity_score | working_precision_bits
timing_cpu_seconds | PASS/FAIL | failure_class
```
Summary-only artifacts are forbidden: every cell must be independently
recomputable from its own record.

## 24. Failure taxonomy

```text
NONE | MATHEMATICAL_COUNTEREXAMPLE | CANDIDATE_RESIDUAL_TOO_LARGE
KERNEL_ERROR_TOO_LARGE | INTERVAL_WIDTH_TOO_LARGE
REPRESENTATION_COMPLEXITY_FAILURE | P1_HEADROOM_FAILURE
COVER_INTEGRITY_FAILURE | FAR_FIELD_SPLICE_FAILURE | PRECISION_FAILURE
BUDGET_EXCEEDED | CHECKPOINT_INTEGRITY_FAILURE | IMPLEMENTATION_DEFECT
INCOMPLETE_EXTERNAL | UNKNOWN
```
Every failed cell and every failed phase maps to exactly one.

## 25. Final K1 verdict taxonomy

```text
K1_CLOSED               all of: checkpoint integrity PASS; Task-1 F_r PASS; EVERY
                        compact-cover cell in scope PASS; all four m assembled for
                        BOTH detectors; far-field splice valid for both; every
                        absolute budget respected with the non-borrowing rule
                        intact; no load-bearing STOP fired; the full required
                        artifact set exists; and INDEPENDENT adjudication passes
K1_FAIL_MATHEMATICAL    a certified enclosure genuinely violates |R| < 2
                        (a true counterexample, not a certificate width failure)
K1_FAIL_CERTIFICATE     the architecture cannot produce enclosures inside budget
                        (candidate, kernel, interval or complexity failure)
K1_FAIL_GOVERNANCE      checkpoint integrity, direction audit, protected tree,
                        work conservation, or an unapproved substitution
K1_CAMPAIGN_FAIL_ARCHITECTURE   Task-1 F_r qualification failed (§11)
K1_INCOMPLETE_BUDGET    hard CPU cap reached (§16)
K1_INCOMPLETE_EXTERNAL  external interruption that is not a budget breach
```
Verdicts are derived mechanically from recorded fields. No narrative override.

## 26. Required artifact set — absence is failure, not silence

```text
certificates/  cusum_compact_certificate.json     SR_compact_certificate.json
               far_field_splice.json              assembly_all_m.json
results/       cells_cusum.jsonl  cells_sr.jsonl  task1_F0_qualification.json
               cpu_ledger.json    budget_ledger_usage.json
logs/          run_log.jsonl      shard_map.json  work_conservation.json
adjudication/  ADJUDICATION_REPORT.md  ADJUDICATION_VERDICT.json
top level      FINAL_K1_VERDICT.json
```
A missing required artifact is a **failure**, adjudicated as
`CHECKPOINT_INTEGRITY_FAILURE` — never an implicit PASS and never silence.

## 27. Amendment policy after freeze

```text
POST_FREEZE_AMENDMENT_ALLOWED = NO
```
No scientific, numerical, budget, scope, threshold or verdict rule may change
after the freeze commit. A discovered defect is **recorded and adjudicated**, and
the campaign either continues under the existing rules or stops. Repairs live in
a **successor checkpoint** with its own preregistration — exactly the discipline
that produced Gates 2C-bis and 2F from the Gate-2C and 2E defects.

## 28. Temporal integrity

```text
T0  namespace + checkpoint authored, no production code executed
T1  freeze commit: SHA-256 of every checkpoint file, protected-input manifest,
    cover manifests, config; anchor commit recorded
T2  design-validation tests pass against the ANCHOR COMMIT via `git ls-tree`
    (never the worktree)                     <-- THIS DESIGN TASK ENDS HERE
T3  production execution                      (NOT PERFORMED)
T4  adjudication                              (NOT PERFORMED)
```
Every hash in `manifests/` is computed from `git ls-tree` blob content at the
named anchor commit, so a dirty worktree cannot forge integrity.

## 29. Residual scientific risk, stated before any result

Honest, and not minimized:

```text
R1  the F_r resolvent-solution candidates have NEVER been built at production
    fidelity. Gate-2D failed on a genuine SR candidate for h_1, an EASIER object
    than F_0 (h_1 is closed form; F_0 solves an integral equation). This is the
    dominant risk and is why Task 1 exists and why its failure stops everything.
R2  C_SR(1/4) = 187.75 multiplies every local error. Near e = 0, C = 1205.94,
    so the smallest cells are the most demanding, and the cover is densest there.
R3  the SR cover of 322 sub-cells was measured with a monotone ENVELOPE walk;
    the true production cover could be larger. This is the x1.25 worst band.
R4  the far-field splice is analytic and certified, but requires the numerics to
    reach e_star_D EXACTLY. A gap is S08 and is fatal, not patchable.
R5  no result of this campaign bears on K2..K5 or on novelty. K1 is necessary
    for the P5 line and nowhere near sufficient.
```

## 30. What this checkpoint does NOT authorize

Second moments; `s_min`; `M_2`; `H2`; `H3a`; Lean or Mathlib work; any merge to
`main`; any modification of P5, P5X or any P5Y gate namespace; any Monte Carlo
in a certificate path; any cap extension; any scope narrowing; and **any
production execution at all under this design task**.

---

## Freeze block

```text
P5Y_K1_CHECKPOINT_STATUS       = FROZEN
P5Y_BINDING_CHECKPOINT_CREATED = YES
P5Y_PRODUCTION_RUN             = NO
```
