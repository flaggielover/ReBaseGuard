# Proof Track 3 forensic audit

**Audit date:** 2026-08-23  
**Baseline commit:** `a2d1ebce9ce13346ebc0b8af3c8fa25f631a56fe`  
**Baseline state:** clean `main`, identical to `origin/main`

## 1. Baseline verification

`bash scripts/verify_level_4.sh` passed all 695 authoritative tests from a
clean worktree at the baseline commit.  The verifier reproduced these
historical decisions without modification:

- Level 1--3: `CLOSED`;
- Stage D: `STAGE-D-PARTIAL`, including D2.3 `FAIL`;
- Stage F and overall Level 4: `LEVEL-4-PARTIAL`;
- Proof Track 1: `MGT1-THEOREM-PARTIAL`;
- Proof Track 1A: `MGT1-TRACK1A-FAILED`;
- Proof Track 1B: `MGT1-TRACK1B-CLOSED`; and
- Proof Track 2: `SR-DERIVATIVE-CLOSED`, with its rigorous SR instability
  certificate still `OPEN`.

The exact dependency hashes are recorded in `results/historical_manifest.json`.

## 2. Repository-wide prior-claim search

The audit searched tracked Markdown, Python, JSON, Lean, TOML, and YAML for
`score`, `location family`, `non-Gaussian`, `Gamma_psi`, `Gamma_f`, `D1`, `D2`,
`D3`, `distribution-free`, `six innovation families`, `t3`, and
`stability-normalized`/`stability-normalised`.

The load-bearing prior sources are:

- `level4/stage_d/STAGE_D_PROTOCOL.md`;
- `level4/stage_d/notes/D3_REGULARITY.md`;
- `level4/stage_d/src/nongaussian.py`;
- `level4/stage_d/src/stopped.py`;
- `level4/stage_d/results/d3_nongaussian.json`;
- `level4/reports/STAGE_D_REPORT.md`;
- the Track-2 definition and stopped-score proof; and
- `StoppedLikelihood.lean`, `IntegralBridge.lean`, and
  `ReBaseGuardIdentity.lean`.

Older blueprint and phase-audit prose contains candidate claims about a
"general score route" or a "detector-independent" identity.  Those claims are
not treated as authority.  Track 3 re-derives the result from the frozen
residual convention and uses the narrower phrase "fixed path functional under
explicit stopped-time differentiation hypotheses."

## 3. Exact Stage-D numerical record

Stage D used a two-sided CUSUM with `k=1/2`, inclusive post-update alarm, and
family-specific thresholds chosen to match the Gaussian in-control ARL.  Its
non-Gaussian campaign used one million cycles per family and reported:

| family | threshold | measured ARL | `E[psi']` | frozen `Gamma_psi` at `m=1` | `Gamma_psi/E[psi']` | naive `Gamma_T` |
|---|---:|---:|---:|---:|---:|---:|
| Gaussian | 5.000000 | 465.600 | 1.000000 | 15.8671 | 15.8671 | 15.8671 |
| t10 | 5.234518 | 466.566 | 1.057692 | 11.9938 | 11.3396 | 19.9203 |
| t5 | 5.669498 | 464.873 | 1.250000 | 7.1890 | 5.7512 | 33.8362 |
| t3 | 6.337011 | 465.891 | 2.000000 | 2.5980 | 1.2990 | 99.5586 |
| contaminated normal 5% | 7.671712 | 465.743 | 0.883256 | 5.7572 | 6.5182 | 46.8949 |
| contaminated normal 10% | 9.381983 | 464.357 | 0.796051 | 5.0474 | 6.3405 | 59.2507 |

These results remain exactly what Stage D said:

- frozen `Gamma_psi>2`: 6/6 numerical passes;
- normalized `Gamma_psi/E[psi']>2`: 5/6 numerical passes;
- t3: `AMBIGUOUS` (`2.5980` versus `1.2990`);
- differentiation and stopped-score square-integrability for the
  non-Gaussian families: `UNPROVED`; and
- no distribution-free, universal, or certified conclusion.

Other Stage-D results are also preserved: SR D1.1--D1.3 passed numerically,
D1.4 remained a candidate, D2.2 bracketed the mathematical `m` crossing,
D2.3 failed 0/8 at its frozen primary step, D2.5 found no operational phase
transition, and D4 was not run.

## 4. Sign reconstruction

The frozen physical convention is

```text
X_t = mu + epsilon_t,
e   = R_j - mu,
Z_t = X_t - R_j = epsilon_t - e.
```

If `epsilon_t` has density `f`, then the residual density is

```text
f_e(z) = f(z+e).
```

Consequently the likelihood score in the parameter `e` is

```text
s(z) = d/de log f(z+e)|_0 = f'(z)/f(z).
```

Stage D stores the conventional location score

```text
psi(z) = -f'(z)/f(z),
```

so the likelihood score is `s=-psi`.  Stage D's Python module states this sign
correctly.  One table in the historical protocol calls `psi` the derivative
of `log f_e`; that label is inconsistent with its own formulas.  It is not
silently repaired: the historical protocol stays frozen, and Track 3 records
the exact distinction.

## 5. Resolution of the Stage-D estimand question

At actual matched `m=1` ReBaseGuard reuse, the reused reference is the terminal
physical observation.  Its next error is `e+Z_tau`, not a score-transformed
M-estimator.  Therefore the theorem-relevant gain is

```text
Gamma_f = E_0[Z_tau sum_{t<=tau} psi(Z_t)].
```

Stage D instead froze

```text
Gamma_psi = E_0[psi(Z_tau) sum_{t<=tau} psi(Z_t)].
```

The normalized Stage-D quantity divides that second object by `E[psi']` and
is appropriate to a different update whose terminal influence function is
`psi/E[psi']`.  Neither Stage-D candidate is the derivative gain for the
actual raw-observation ReBaseGuard update, except in the Gaussian case where
`psi(z)=z` and `E[psi']=1`.

This is a mathematical resolution, not a choice based on new numerical
outcomes.  No Track-3 confirmatory outcome existed when it was recorded.

