# P8R frozen protocol

**Frozen at the temporal anchor, before any production result existed.** Every
number below is quoted from `src/rebaseguard_p8r/config.py`, which is the single
authority; this file never restates a budget independently of that module. Gate
`I2` hashes this file, `I3` hashes that module, and `I13` re-derives the executed
calibration counts from the stored trace and compares them to it.

---

## 1. The question

> Does the recursive re-baselining structure established for the two frozen
> Gaussian specialisations — the stopped-selection gain `Gamma`, the local
> stability boundary `rho_c`, and the operational monitoring degradation —
> survive outside that specialisation, across innovation-distribution families,
> detector families, reuse windows, reuse conventions and drift patterns, and
> which parts fail to transfer?

Provenance and scope: `DEFINITION_AUDIT.md`.

## 2. Hypotheses, frozen

| id | hypothesis | admissible outcomes |
|---|---|---|
| `H1` | **Window separability.** The window factor `K(D,f,m) = rho_c(D,f,m)/rho_c(D,f,1)` is a function of `m` alone, invariant across detector and innovation family. | `SUPPORTED` / `REJECTED` |
| `H1-D` | `K` is invariant across the two detectors, family by family. | `SUPPORTED` / `REJECTED` |
| `H1-F` | `K` is invariant across families, detector by detector. | `SUPPORTED` / `REJECTED` |
| `H2` | **Regime survival.** In every eligible `(D,f,m)` cell, `Gamma_A > 2`: full reuse is locally repelling. | `SUPPORTED` / `REJECTED` |
| `H3` | **Exact decomposition.** `Gamma_A(m) = (1/m) sum_{r<m} gamma_r + R_m` holds to Monte Carlo error in every cell. | `SUPPORTED` / `REJECTED` |
| `H4` | **Convention identity.** `Gamma_A - Gamma_B = R_m` exactly, to floating point. | `SUPPORTED` / `REJECTED` |
| `H5` | **Operational degradation.** In every declared chain cell, the re-baselining chain's `ARL` at `rho = 1` is below half the same-cell nominal `ARL_0`. | `SUPPORTED` / `REJECTED` |
| `H6` | **P7 boundary transfer.** P7's boundary criterion reproduces family by family on the declared sub-family grid. | `SUPPORTED` / `REJECTED` |
| `H7` | **Detector transfer.** `Gamma_A(cusum,f,m) / Gamma_A(sr,f,m) = 1`. | `SUPPORTED` / `REJECTED` / `INCONCLUSIVE` |
| `H8` | **Seed insensitivity.** An independent batch family reproduces every `Gamma_A(D,f,m)`. | `SUPPORTED` / `REJECTED` |
| `H9` | **Heavy-tail attraction at `t3`, `m=20`.** `Gamma_A < 2` in that cell. | `SUPPORTED` / `INCONCLUSIVE` |

`H1`, `H1-D`, `H1-F`, `H6` and `H7` were **rejected or unestablished in P8**.
They are re-asked here at numerically identical thresholds. They are not repair
targets and no threshold protecting them may move.

## 3. Tested model classes

Innovation family `f`, the six frozen Stage-D D3 families, re-implemented in
`src/rebaseguard_p8r/families.py` and cross-checked against P4's `route_a`:

`gaussian`, `t10`, `t5`, `t3`, `contam0.05`, `contam0.1`
(`config.FAMILIES`).

Conventions inherited verbatim: the `t` families are rescaled to unit variance;
the contaminated families are **not** rescaled and carry variance `1 + 8 eps_c`,
which is the frozen Stage-D convention.

`t3` is declared `MOMENT_MARGINAL` before any result: the `Gamma` integrand has a
divergent third absolute moment, so no Berry–Esseen rate is available and the
sample variance itself has infinite variance. Its cells are reported in full and
never counted in `S6` either way.

## 4. Detector families

Two, and only two — the families P1/P2 close (`config.DETECTORS`):

* frozen two-sided CUSUM, `k = 1/2`, imported read-only from
  `level4/src/rebaseguard_level4/frozen.py`; never re-implemented;
* frozen symmetric two-chart Shiryaev–Roberts, the log-domain softplus
  recursion of `level4/stage_d/src/stopped.py`, restated exactly.

**The detector statistics are frozen at their Gaussian design in every family.
Only the threshold is recalibrated.** That is the Stage-D D3 convention and the
operationally realistic scenario: a practitioner deploys the standard chart and
tunes its limit.

## 5. Window sizes

`config.M_GRID = (1, 2, 3, 5, 10, 20)`.

* `M_P3_SUPPORTED = (1, 2, 3, 5)` — the windows P3 supports. **Gated.**
* `EXTRAPOLATION_M = (10, 20)` — outside P3's support. **Reported, never
  gated**; `S7X` resolves to `OUT_OF_SCOPE` by construction and may never be
  used to support or reject the window law. `tests/test_claim_firewall.py`
  checks that no `m in {10,20}` cell appears in `S7`/`S7D`/`S7F`'s evidence.

Chain and drift experiments use `M_CHAIN = (1, 5)` only; that is declared here,
not discovered afterwards.

## 6. Conventions

* **A** (primary): window denominator `w = min(m, tau)`.
* **B** (contrast): window denominator `m`.

Both are evaluated in every cell. Their exact difference is the truncation
remainder `R_m`, which `H4`/`S9` checks to `1e-12`.

## 7. Reuse ladder and drift

Reuse fraction `rho`: P7's ladder verbatim —
`config.RHO_MULTIPLIERS = (0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2.0, 4.0)` times
`rho_c(D,f,m)`, plus the absolute practitioner anchors
`config.RHO_ABSOLUTE = (0.0, 0.25, 0.5, 0.75, 1.0)`, clipped to `[0,1]`.
Using P7's ladder verbatim is what makes P7's boundary criterion literally
applicable.

Drift: in control; step `Delta in config.SHIFTS = (0.5, 1.0, 2.0)` applied at a
re-baselining instant; linear ramp `Delta_j = slope * j` with
`slope in config.RAMP_SLOPES = (0.02, 0.05)`. Step is P7's pattern; the ramp is
this campaign's own and is declared here.

## 8. Operating point and thresholds

Frozen target `ARL_0 = 465.50394`, read at run time from
`stage_d/results/d3_nongaussian.json`.

* **CUSUM.** Family thresholds `h_f` are read from that file and are **never
  recalibrated**. P8R re-measures the achieved `ARL_0` at each and reports the
  residual (`S3`). That measurement is drawn from `PRODUCTION` addresses and is a
  diagnostic, never a tuning input — it cannot be one, because the thresholds are
  owned externally.
* **SR.** No non-Gaussian SR threshold exists in the repository. P8R calibrates
  `A_f` per family under `CALIBRATION_PLAN.md`, which is the single authoritative
  procedure. Gaussian SR uses the frozen `A = 520.886133602749` unchanged and is
  only re-verified on the holdout.

## 9. Randomness

The repaired P6R2b addressable-primitive standard, plus P8R's address-class
discipline. Full statement: `RNG_ADDRESS_PLAN.md`.

Entropy namespace `config.SEED_NAMESPACE = 0x50385F52_4D435201`, distinct from
Stage D, P7, P6R2b **and P8**. P8R is therefore an independent seed realisation
of the same estimands, not a replay of P8's field.

CRN scope, declared:

| comparison | paired? | why |
|---|---|---|
| across detector `D`, window `m`, convention A/B, lag depth | **yes** — those axes are absent from the stopped-cycle address | they are the primary contrasts |
| across `rho`, shift size, drift pattern | **yes** — absent from the chain address | the `rho` ladder is compared within a cell |
| across innovation family `f` | **no** — `f` is in the address | different families have different laws; pairing is not meaningful and a shared-uniform construction would force an expensive, family-asymmetric inverse-CDF layer |
| across seed families `E1`/`E5` | **no** — different production tags, disjoint fields | that independence is what makes `S13` a real reproduction test |

## 10. Sample sizes

All from `config`; see `PRODUCTION_PLAN.md` for the per-experiment table and
`CALIBRATION_PLAN.md` for the calibration budgets. There is no second statement
of any of these numbers anywhere in this campaign.

## 11. Estimands

Per stopped cycle, from a reset detector state, with residual
`z_t = eps_t - e_eff`:

```
tau       first inclusive post-update alarm
T         sum_{t<=tau} z_t
Psi       sum_{t<=tau} psi(z_t)
zbar^A_m  (1/min(m,tau)) sum_{r<min(m,tau)} z_{tau-r}
zbar^B_m  (1/m)          sum_{r<min(m,tau)} z_{tau-r}
Gamma_A   E[zbar^A_m * Psi]          <- the gated estimand
Gamma_B   E[zbar^B_m * Psi]
gamma_r   E[z_{tau-r} 1{r<tau} * Psi]
R_m       E[(1/max(tau,1) - 1/m) T Psi ; tau < m]
rho_c     1 / |1 - Gamma_A|
K(D,f,m)  rho_c(D,f,m) / rho_c(D,f,1)
```

Chain metrics per replicate, post burn-in: `arl`, `ref_mse`, `fap100`,
`e_acf1` (P7's pooled definition, restated).

Drift metric: the length of the first cycle beginning after the change, with
`q50`, `q95`, `P(delay>100)` and an explicit `INSUFFICIENT_TAIL_EVENTS` label
wherever fewer than `config.TAIL_EVENT_FLOOR` tail events occur.

## 12. Statistical treatment

`STATISTICAL_ANALYSIS_PLAN.md`, frozen with this file.

## 13. Theory scope

`P8R-T1` — that the frozen reference map's derivative is `rho (1 - Gamma_A)` —
is inherited as a **conditional theorem**, conditional on P4's
differentiation-under-expectation, score-integrability and stopping-time
integrability hypotheses for the particular detector, family and window. Those
hypotheses are *not* discharged by this campaign, and simulation agreement does
not discharge them. The exact algebraic identities (`P8R-L0`, `P8R-L1`, the
reset decomposition, the convention-A/B truncation decomposition) are exact
algebra under their stated iid/reset model and are separate claims.

The heavy-tailed `t3` case is the most acute: the conditions needed for
differentiation under the expectation are not established there, which is why
`S15` is conservative by design.

## 14. Verdict semantics

`FROZEN_GATES.md` §4. A candidate verdict is not authoritative.
