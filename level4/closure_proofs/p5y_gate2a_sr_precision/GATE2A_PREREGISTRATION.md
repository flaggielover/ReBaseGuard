# P5Y GATE 2A — PILOT-SR-PRECISION preregistration

**NON-BINDING.** A single-question precision/conditioning pilot. Not P5Y
production, not a cover, not a binding checkpoint. Frozen before any
result-bearing execution (T2); nothing here changes after T2.

```text
P5_ORIGINAL_VERDICT = PARTIAL     P5X_FINAL_VERDICT = PARTIAL
P5X_CAMPAIGN = ARCHIVALLY_COMPLETE
P5Y_GATE1_DECISION = GATE1_PASS_ROUTE_B_SUPPORTED   (immutable)
```

## 0. The single question

At the Gate-1-selected degree-8 SR back-end, what working precision yields a
**healthy** mathematical margin, and what CPU multiplier does it cost?

## 1. Compute cap

```text
GATE2A_CPU_CAP       <= 0.10 CPU-hours   (hard, no extension after results)
GATE2A_CPU_PREFERRED <= 0.05 CPU-hours
```
If the grid cannot complete inside the cap: STOP and return
`SR_PRECISION_INCOMPLETE_EXTERNAL`. Repeat counts are frozen in §6 and may not
be reduced after seeing timings.

## 2. Frozen scope — the only experimental variable is working precision

| item | frozen value | provenance |
|---|---|---|
| detector | SR, `m = 1` | Gate-1 M2, unchanged |
| state patch | `(17, 11)` on `grid = 64` | Gate-1 M2, unchanged. **No other patch may be used** |
| drift | `e = 1/4` exact rational | unchanged |
| candidate | bidegree `(16,16)`, `unit_candidate()` imported verbatim | unchanged |
| domain | `b_SR = log(1+A)`, `A = 4581762885148045/8796093022208` | unchanged |
| **degrees** | **`{8, 10}`** — degree 12 **PROHIBITED** | §4 of the brief |
| **precisions** | **`{256, 384, 512}` bits** | §4 of the brief |
| control precision | `192` bits, rerun because it is essentially free and anchors the scaling curve — **frozen here, before T2** | Gate-1 baseline |
| panel rule | Gate-1 continuous minimal-safe rule, **evaluated once at 192 bits and its output frozen**, so the geometry is bit-identical across every precision cell | §5 of the brief |

Frozen panel geometry (copied from `p5y_micropilot_gate1/results/m2_sr_degree.json`):

```text
degree 8 :  h_z = 0.19386660811172551   H_used = 0.24275293177756252   n_z = 28
degree 10:  h_z = 0.31331186801206190   H_used = 0.36219819167789891   n_z = 17
```

Recomputing the rule inside each precision cell could shift `n_z` by +/-1 through
the `float()` step and would confound the comparison; freezing its output is the
faithful reading of "the only experimental variable is working precision".

**No 768 or 1024-bit point may be added after results. No degree may be added.**

## 3. Mathematical gates (all inherited from Gate-1 / R3, unchanged)

```text
P1  softplus local remainder E_d <= 1e-9
P2  composed+integrated relative half-width       <-- SAFETY TARGET, see section 4
P3  max composed coefficient radius < 1e-20
T1  enclosure contains point evaluations at -H, -H/2, 0, H/2, H
T2  remainder monotone in H
T3  core/strip split exhaustive
T5  centred Gaussian moment decay
T6  exact rational e     T7  b_SR = log(1+A)      T8  no empirical monotonicity
```
Every gate reports **both** a boolean and a numerical margin to its threshold.

## 4. Frozen safety-margin requirement

```text
P2_SAFETY_TARGET = 1e-8
```
This is 100x inside the Gate-1 acceptance boundary of `1e-6`, and Gate-1's
degree-8 value was `7.4487e-7` (margin only `1.34x`). The definition of `P2` is
unchanged from Gate-1/R3:

```text
rem_width = 16 * 2 * E_d * N_0 * sup|candidate coefficients|
P2        = radius( [0 +/- rem_width] + acc ) / |acc|_upper
```

**Declared in advance:** `rem_width` is a *mathematical* softplus-truncation
term and is **precision-independent**. Therefore `P2` has a floor
`P2_floor = rem_width / |acc|` that no amount of precision can cross. This pilot
must report `P2_floor` separately; if `P2_floor > 1e-8` the safety target is
unreachable at this degree by precision alone, and that is a **FAIL** outcome to
be reported, not engineered around.

## 5. Pre-registered predictions (so the pilot can falsify me)

| quantity | prediction |
|---|---|
| `P1` margin | unchanged at every precision (knife-edge, relative `~4e-16`), proving Gate-1's `P1` defect is **not** a precision artefact |
| degree 8 `P2` at 256/384/512 | `~1e-10` to `~1e-9`, i.e. at the `P2_floor`, PASS at 256 |
| degree 10 `P2` at 256 | `1e-9` to `1e-7`, genuinely uncertain |
| degree 10 `P2` at 384 | PASS, high confidence |
| `t_panel` multiplier vs 192 bits | 256: `1.2-1.6x`; 384: `1.8-3x`; 512: `2.5-5x` |
| Gate decision | `SR_PRECISION_PASS_256` |

## 6. Timing

```text
TIMING_REPEATS = 5 per (degree, precision) cell   -- frozen, not reducible
```
Report median, min, max and relative spread. **Timing noise affects the cost
model only and may never change a mathematical PASS/FAIL.**

## 7. Reproducibility check

Degree 8 at 384 bits is computed **twice** in the same run. The two integrated
enclosures must be **ball-identical** (identical lower and upper endpoints as
exact strings). Timing may differ; the enclosure may not.

## 8. Diagnosis classification (§9 of the brief)

Every failing interval expression is classified using **interval radii**, never
midpoint disagreement:

```text
MATHEMATICALLY_FALSE | PRECISION_INSUFFICIENT | REPRESENTATION_ILL_CONDITIONED
IMPLEMENTATION_DEFECT | UNKNOWN
```
A low-precision failure that contracts correctly at higher precision on the
mathematically identical expression is `PRECISION_INSUFFICIENT`. No formula may
be silently replaced after T2.

## 9. Selection rule (mechanical)

For **degree 8**, select the LOWEST precision in `{256, 384, 512}` with: every
mathematical gate passing with nonzero margin; `P2 <= 1e-8`; no unresolved
interval explosion; and the reproducibility check passing.

```text
256 qualifies -> SR_PRECISION_PASS_256
else 384      -> SR_PRECISION_PASS_384
else 512      -> SR_PRECISION_PASS_512
else          -> SR_PRECISION_FAIL_WITHIN_GRID
```

## 10. Degree-10 replacement rule (frozen before T2)

Degree 10 may become `P5Y_SR_RECOMMENDED_BACKEND` **only if all** hold:

```text
(a) P2 <= 1e-8 ;
(b) every inherited mathematical gate passes with nonzero margin ;
(c) its safety margins are no worse than degree 8 at the same selected precision
    (P2_deg10 <= P2_deg8, and P2_floor_deg10 <= P2_floor_deg8) ;
(d) MATERIALLY_LOWER := projected SR CPU at least 20% below degree 8's,
    computed at each backend's own minimum safe precision.
```
Otherwise degree 8 remains the recommended back-end. A degree-10 win does not
change the reported minimum-safe-precision class for degree 8.

## 11. Feasibility bands and the frozen ceiling

```text
FEASIBILITY_CEILING = 30,000 CPU-hours     (frozen here, before T2)
STRONG        : selected precision <= 256 AND central P5Y CPU <=  5,000 h
MODERATE      : selected precision <= 384 AND central P5Y CPU <= 10,000 h
WEAK          : selected precision  = 512 OR  central in (10,000, 30,000] h
NOT_FEASIBLE  : no precision <= 512 meets the margin, OR central > 30,000 h
```
The `m`-sharing multiplier `24.5x` is carried forward from Gate-1 unless this
pilot finds a genuine reason it changes.

## 12. STOP rules

```text
S1  cumulative result-bearing CPU reaches 0.10 CPU-hours -> STOP, INCOMPLETE_EXTERNAL
S2  a result-bearing semantic bug found after T2 -> STOP that cell; do not patch
    and continue unless the fix is provably reporting-only
S3  interval radii non-monotone in precision -> record and FAIL (kill criterion)
S4  any protected path outside this namespace modified -> STOP the whole gate
S5  a mathematical gate fails in a way that higher precision does not repair
    -> classify as MATHEMATICAL_FAILURE and FAIL; do NOT open the xi route
```

## 13. Out of scope — not run under any circumstances

Second-moment compact pilot, `s_min`, `M_2`, `m>1` production, `H2`/`H3a`
derivative cover, full SR cover, full CUSUM cover, Lean, production Arb
campaign, degree 12, the xi-coordinate back-end.

## 14. Repository safety

Branch `p5y-gate1-micropilots` (continued), namespace
`level4/closure_proofs/p5y_gate2a_sr_precision/`. No merge to main, no push, no
binding checkpoint, no modification of P5, P5X or Gate-1 artifacts.
