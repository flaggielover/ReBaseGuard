# P8 experiment protocol — frozen before production

Frozen after the runtime/variance pilot (`results/pilot_notes.json`) and
**before** any production cell was generated. The pilot fixed sample sizes and
confirmed that P8's independent implementation reproduces P3 and P4; it fixed
no verdict and no gate threshold that depends on a P8 outcome.

---

## 1. The question

> Does the recursive re-baselining structure established for the two frozen
> Gaussian specialisations — the stopped-selection gain `Gamma`, the local
> stability boundary `rho_c` (P3), and the operational monitoring degradation
> (P7) — survive outside that specialisation, across innovation-distribution
> families, detector families, reuse windows, reuse conventions and drift
> patterns?

Derived from repository authority only; see `P8_DEFINITION_AUDIT.md` §2.

## 2. Factors

| factor | levels | source |
|---|---|---|
| innovation family `f` | `gaussian`, `t10`, `t5`, `t3`, `contam0.05`, `contam0.1` | the six frozen Stage-D D3 families, re-implemented in `src/rebaseguard_p8/families.py` and cross-checked against P4's `route_a.py` |
| detector `D` | frozen two-sided CUSUM (`k=1/2`), frozen symmetric two-chart SR | the only two families P1/P2 close |
| window `m` | `1, 2, 3, 5` (P3-supported) and `10, 20` (labelled `EXTRAPOLATION_BEYOND_P3`) | P3 supports `{1,2,3,5}`; Stage D used `{1,5,20}` |
| window convention | A (`denominator min(m,tau)`) primary, B (`denominator m`) contrast | `C4`, `C5` |
| reuse fraction `rho` | ladder `{0.25,0.5,0.8,1.0,1.25,1.5,2.0,4.0} x rho_c(D,f,m)` plus absolute anchors `{0,0.25,0.5,0.75,1.0}`, clipped to `[0,1]` | **P7's ladder, verbatim**, so P7's boundary criterion can be applied literally |
| drift pattern | in control; step `Delta in {0.5,1,2}` applied at a re-baselining instant; linear ramp `Delta_j = slope * j`, `slope in {0.02,0.05}` per cycle | step is P7's pattern; ramp is P8's own, declared here |

**Detector statistics are frozen at their Gaussian design in every family; only
the threshold is recalibrated.** (Stage-D D3 convention; `THEORY.md` §0.)

## 3. Operating point and thresholds

Frozen target `ARL_0 = 465.50394`, read at run time from
`stage_d/results/d3_nongaussian.json`.

* **CUSUM.** Family thresholds `h_f` are read from that file and are **never
  recalibrated** (the same discipline P4 adopted). P8 re-measures the achieved
  `ARL_0` at each and reports the residual.
* **SR.** No non-Gaussian SR threshold exists in the repository. P8 calibrates
  `A_f` per family by bisection in `log A` against the same target, with the
  same procedure Stage D used for CUSUM, using P8's addressable primitive field
  and a fully recorded trace. Labelled `NEW_P8_CALIBRATION` everywhere.
  Gaussian SR uses the frozen `A = 520.886133602749` unchanged.

## 4. Randomness

The repaired P6 **addressable primitive** standard is inherited
(`src/rebaseguard_p8/primitives.py`): every draw is a pure function of its
address, materialised in Philox blocks so that overflow past any tape end is not
a special case. Addresses contain no live-set position, no execution order, no
stopping time, no branch order and no consumed-draw count.

CRN scope, declared:

| comparison | paired? | why |
|---|---|---|
| across detector `D`, window `m`, convention A/B, lag depth | **yes** — those axes are absent from the stopped-cycle address | they are P8's primary contrasts |
| across `rho`, shift size, drift pattern | **yes** — absent from the chain address | the `rho` ladder is compared within a cell |
| across innovation family `f` | **no** — `f` is in the address | different families have different laws; pairing is not meaningful and a shared-uniform construction would force an expensive and family-asymmetric inverse-CDF layer |

Seed namespace `0x50385F4D_43520001`, distinct from Stage D, P7 and P6R2b.
Integer family/detector codes are used; no `hash()` of a string ever enters an
address.

## 5. Sample sizes (fixed by the pilot, not by results)

| experiment | size | statistical unit |
|---|---|---|
| `E1` stopped-cycle `Gamma` matrix | `4,096,000` cycles per `(D, f)` cell = 20 batches x 50 row blocks x 4096 | the cycle; **batch means over the 20 batches** give the reported SE |
| `E2` SR calibration | `250,000` cycles per bisection evaluation, `2,048,000` cycles for the final verification | the cycle |
| `E3` chain ladder | `2,000` replicates x `70` cycles, `burn_in = 20` (amended, see below) | the **replicate** |
| `E4` drift / delay | `6,000` replicates x `24` cycles, change at cycle `20` (amended, see below) | the replicate |
| `E5` seed / grid sensitivity | `E1` repeated at an independent batch family (batches `100..119`) and `E3` at an independent replicate family | as above |
| `E6` P4 replication diagnostic | 12 independent `m=1` CUSUM replications of `409,600` cycles each, per family | the cycle |

**Amendment `A1` (`results/protocol_amendments.json`).** `E3` and `E4` were
declared at `4,000 x 80` and `8,000 x 40`. A chain smoke run showed those
extrapolate to compute that was not budgeted, so they were reduced to
`2,000 x 70` and `6,000 x 24` **before any `E3` or `E4` production artifact
existed**. Nothing else changed: not the `rho` ladder, not the burn-in, not the
shift cycle, not a metric, not a gate, not the `E1`/`E5` sizes, not the tail
floor. The amendment record states what the smoke run showed and that no gate
threshold was chosen from it.

## 6. Estimands

Per stopped cycle: `tau`, `T_tau = sum Z_t`, `Psi_tau = sum psi(Z_t)`, the lag
vector `Z_{tau-r}` and `psi(Z_{tau-r})` for `r < 20`, validity `1{r<tau}`.

```text
Gamma_A(D,f,m) = E[ zbar^A_m * Psi_tau ]         PRIMARY
Gamma_B(D,f,m) = E[ zbar^B_m * Psi_tau ]         convention contrast
gamma_r(D,f)   = E[ Z_{tau-r} 1{r<tau} Psi_tau ] lag selection profile
R_m            = Gamma_A - Gamma_B               truncation remainder (identity)
Gamma_naive    = E[ zbar^A_m * T_tau ]           WRONG-SCORE diagnostic only
Gamma_psipsi   = E[ psibar^A_m * Psi_tau ]       Stage-D D3 estimand, for RE3
rho_c          = 1 / |1 - Gamma_A|               P3 A3, applied per cell
K(D,f,m)       = (Gamma_A(...,1) - 1)/(Gamma_A(...,m) - 1)
```

Chain metrics, per replicate, post burn-in: mean cycle length (`ARL`),
`ref_mse = mean(e^2)`, `fap100 = P(cycle length <= 100)` pooled per replicate,
`e_acf1`, and for shifted runs the detection delay of the first post-shift
cycle with `q50/q95/P(delay>100)`.

## 7. Baselines and controls (both reported, never merged)

* `rho = 0` **fresh control**: pure fresh re-baselining at the same `m`. Isolates
  the cost of re-baselining *per se* from the cost of *reuse*.
* **nominal control**: `A_f(0)`, the single-cycle ARL from the reset state,
  measured in `E1`. The nominal reference for "how much was lost".
* **wrong-score diagnostic** `Gamma_naive`: what a Gaussian-score analysis would
  report for a non-Gaussian family. Reported to quantify the error of *not*
  generalising, never as a result.

## 8. Statistical procedure

* Batch means over 20 batches (`E1`) or replicate-level means (`E3`, `E4`);
  SE = `sd/sqrt(n_units)`; 95% intervals `+- 1.96 SE`.
* `rho_c` and `K` intervals by the delta method, with the exact monotone image
  used where the transformation is monotone (P3's rule).
* **Multiplicity.** One primary hypothesis (`H1`, gate `G4`) at one primary
  metric. Secondary metric families use Benjamini–Hochberg at `q = 0.10` within
  the family. The real protection is reproduction across two detectors, six
  families, six windows and an independent seed family — not the adjustment.
* **Large-`n` discipline.** With `4.1e6` cycles a `1%` difference is significant.
  Every invariance gate is therefore a **practical-equivalence** gate with a
  pre-declared margin; the formal homogeneity test is reported as *descriptive*
  evidence of detectable-but-small heterogeneity and is never the gate.
* **Moment-marginal family.** The `Gamma_A` integrand is `zbar * Psi_tau`; for
  unit-variance `t_nu`, `psi` is bounded and `tau` has geometric-type tails, so
  the integrand inherits the tail index `nu`. Hence `E[integrand^2] < inf` iff
  `nu > 2` and `E|integrand|^3 < inf` iff `nu > 3`. **`t3` sits exactly on the
  third-moment boundary**: the CLT applies but no Berry–Esseen rate does, and
  the sample variance has infinite variance, so its reported SE is not
  trustworthy. `t3` is declared `MOMENT_MARGINAL` **here, before production**,
  is excluded from the primary invariance gate `G4`, and is reported in full
  everywhere. `t5` (`nu = 5`) has finite fourth moment and is fully eligible.
* **Grid-selection caveat.** Every optimum reported over a finite `rho` ladder
  is reported as *the best grid point*, with the neighbouring points and their
  intervals, never as an "exact optimum".

## 9. Early stopping

None. Every declared cell is run to its declared size. If a cell fails
numerically (non-alarming path, tie, overflow) the run raises rather than
silently truncating.

## 10. Negative-result interpretation, declared in advance

| outcome | how it is reported |
|---|---|
| `H1` fails across families but holds across detectors | **NARROWED**: "window separability is a cross-detector law, not a cross-distribution law". This is a real result and is reported as the headline if it occurs |
| `H1` fails on both axes | **REJECTED**: P8 reports the measured `K` surface as a descriptive robustness table and the campaign's contribution is the matrix plus the reproduction/consistency findings |
| `Gamma_A <= 2` in some cell | reported as a **regime change**: full reuse is locally attracting there, and P3's regime audit table `A4` is applied to classify it. Not suppressed, not averaged away |
| P7's boundary verdict does not transfer | reported as a **new finding about `rho_c`'s operational status outside the Gaussian core**, with P7's criterion applied verbatim |
| a reproduction target is missed | reported as a **discrepancy**, with P8's number, the historical number, both SEs, the `z`, and an explicit statement that P8 does not own and does not edit the historical artifact |
