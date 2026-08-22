# Definition and provenance audit

**Audit date:** 2026-08-22
**Repository head at audit:** `37f828c75307f884faab6de673bf598da21017f4`
**Historical artifacts modified:** no

## 1. Baseline and frozen-artifact integrity

The authoritative command was run before any campaign artifact existed:

```text
PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' \
  bash scripts/verify_level_4.sh
```

It exited zero with 695 tests:

| Suite | Passed |
|---|---:|
| frozen Level 1–3 | 90 |
| Level 4 Stage A | 290 |
| Stage B | 46 |
| Stage C | 48 |
| Stage C.1 | 36 |
| Stage D | 72 |
| Stage E | 59 |
| Stage F | 54 |
| **Total** | **695** |

The verifier reported `STAGE-D-PARTIAL`, historical D2.3 `FAIL` (`0/8` at
the frozen primary step `h=0.05`), `12/12` Stage-D adversarial checks, and
`LEVEL-4-PARTIAL` with the `m>1` derivative theorem unmet.

Frozen SHA-256 values checked during the audit:

| Artifact | SHA-256 |
|---|---|
| `level4/stage_d/STAGE_D_PROTOCOL.md` | `925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e` |
| `level4/stage_d/notes/CORRESPONDENCE_AUDIT.md` | `985018981b11e2030128e5d4cb78f08e803155c6ed4fdbbbdb48c96001f6c2c2` |
| `level4/stage_d/notes/D2_3_STEP_PRECOMMIT.md` | `7b7a54c64f4c86334415a03cd45797e7cb8b923d378fa90180a71f1831588dea` |
| `level4/stage_d/results/d2_3_derivative.json` | `ea1d026384866de0fc5ad0ded3e68f159d32deaa3be24505aab449b73db8e020` |
| `level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md` | `41ea8cd6a33f430be44d66376df60efc979b6dda5f00308616a519b7ece6a106` |

The Git tree objects at the audit boundary were Stage D `98b15dd8...`,
Stage-A source `0d4b6f00...`, Stage F `0c408843...`, closure `ddde11f1...`,
`rebaseguard-proof` `727edc80...`, and `rebaseguard-lean` `702f3653...`.
The campaign tests retain the full values.

## 2. Common frozen detector

Set the true in-control mean to zero. The current reference error is `e` and
the residual supplied to the detector is

\[
  Z_t=X_t-e,\qquad X_t\stackrel{\mathrm{iid}}\sim N(0,1).
\]

For the frozen two-sided CUSUM, `k=1/2`, `h=5`,

\[
 S_t^+=\max(0,S_{t-1}^++Z_t-k),\qquad
 S_t^-=\max(0,S_{t-1}^--Z_t-k),
\]

and the ordinary alarm time is

\[
 \tau=\inf\{t\ge1:\max(S_t^+,S_t^-)\ge h\}.
\]

The alarm is tested after the update with an inclusive boundary. The stopped
sum is `T_tau=sum_{t=1}^tau Z_t`, including the terminal observation.

## 3. Stage A and Stage D are different maps

| Concept | Stage A definition | Stage D definition | Code path | Mathematical object | Same object? |
|---|---|---|---|---|---|
| `tau` | ordinary alarm exists, but is not the `m>1` reuse stop | `inf {t>=1 : alarm at t}` | frozen update: `level4/src/rebaseguard_level4/frozen.py`; Stage D: `stage_d/src/stopped.py:201-234` | ordinary CUSUM stopping time | **No** at `m>1` usage |
| `tau_m` | `inf {t>=m : alarm at t}` | not used | `conditional.py:120-147`; `multicycle.py:213-216` | dwell-modified stopping time | **No** |
| `m` | nominal and realized reuse length | nominal maximum reuse length | Stage A configs; Stage D `m_grid` | fixed positive integer | **Yes** as parameter only |
| `w` | always `m`, since `tau_m>=m` | `min(m,tau)` | `stage_d/src/stopped.py:256-259`; `stage_d/src/chain.py:120-125` | random realized window length | **No** |
| stopped window | exactly the last `m` residuals at `tau_m` | last `w` residuals at ordinary `tau` | Stage A circular buffer versus Stage D reversed buffer | stopped path suffix | **No** |
| reuse residual statistic | `(1/m) sum_{r<m} Z_{tau_m-r}` | `(1/w) sum_{r<w} Z_{tau-r}` | `conditional.py:143,153`; `stopped.py:256-265` | residual window mean | **No** |
| denominator | fixed `m` | random `w=min(m,tau)` | same lines | normalization of stopped suffix | **No** on `tau<m` |
| reused reference | `e + (1/m)sum Z` | `e + (1/w)sum Z` | Stage A `conditional.py:153`; Stage D `stopped.py:126-132`, `chain.py:126-130` | raw/physical reference estimate | **No** at `m>1` |
| fresh reference | independent `N(0,1/m)` | independent `N(0,1/m)` | `frozen.py:fresh_statistic_scale`; `chain.py:128` | matched nominal-information control | **Yes** |
| `rho` update | `rho*reuse+(1-rho)*fresh` | same mixing form, with Stage-D reuse | `frozen.py:rebaseline`; `chain.py:128-129` | next reference error | form yes; induced map no |
| `Gamma_m` | `(1/m)E[W_{tau_m,m}T_{tau_m}]` for the dwell stop | primary convention A: `E[A_m T_tau]` | Stage A `conditional.py:score_gamma`; Stage D `stopped.py:103-109,256-265` | stopped score covariance/gain | **No** |
| `F_{rho,m}(e)` | conditional mean under `tau_m` | conditional mean under ordinary `tau` and truncation | Stage A `conditional.py`; Stage D `stopped.py:126-132` plus `chain.py` | induced conditional-mean reference map | **No** for `m>1` |

The Stage-A buffer is always full because alarms before `m` are suppressed.
The Stage-D buffer is truncated because the detector itself is not changed.
At `m=1`, `tau_1=tau`, `w=1`, and the two definitions coincide.

## 4. Exact Stage-D object

For a fixed `m>=1`, define

\[
 w_m=\min(m,\tau),\qquad
 A_m=\frac1{w_m}\sum_{r=0}^{w_m-1}Z_{\tau-r}.
\]

When `tau<m`, the window contains the entire stopped path and

\[
 A_m=\frac{T_\tau}{\tau}.
\]

Thus the denominator is **`w`**, not `m`. The reused raw reference includes
the current reference additively:

\[
 R_{\mathrm{reuse}}=e+A_m.
\]

If `Ybar_m~N(0,1/m)` is independent fresh information, the frozen Stage-D
update is

\[
 E^+=\rho(e+A_m)+(1-\rho)\bar Y_m.
\]

Consequently the conditional-mean map is

\[
 F_{\rho,m}(e)
   =E_e[E^+\mid E=e]
   =\rho\{e+E_e[A_m]\}.
\]

This proves exact rho scaling, `F_{rho,m}=rho F_{1,m}`, because the fresh
statistic has exactly zero mean and its law does not depend on `e`.

The differentiated quantity is the derivative in the **current reference
error/location parameter `e`**, at fixed integer `m` and fixed `rho`, of this
conditional mean. It is not a pathwise derivative of `tau`, not a derivative
in `m` or `rho`, and not the derivative of a stationary-chain metric.

## 5. Stopped likelihood ratio and theorem candidate

Under `P_e`, the residuals are iid `N(-e,1)`. On the stopped sigma-field the
likelihood ratio relative to `P_0` is

\[
 L_e=\exp\{-eT_\tau-\tfrac12e^2\tau\}.
\]

Therefore

\[
 F_{\rho,m}(e)=\rho\left[e+E_0(A_mL_e)\right].
\]

If differentiation may be exchanged with the stopped expectation,

\[
 F'_{\rho,m}(0)=\rho\left[1-E_0(A_mT_\tau)\right].
\]

Define the Stage-D truncated gain

\[
 \widetilde\Gamma_m:=E_0[A_mT_\tau].
\]

This is exactly the historical Stage-D **convention A** quantity. The tilde is
used in this campaign to distinguish it from the historically asserted but
different fixed-denominator lag average.

## 6. Exact short-cycle correction and lag decomposition

Define fixed-lag stopped contributions

\[
 \gamma_r=E_0[\mathbf1_{\{\tau>r\}}Z_{\tau-r}T_\tau],\qquad r\ge0,
\]

and the fixed-denominator diagnostic

\[
 \Gamma_m^B=\frac1m\sum_{r=0}^{m-1}\gamma_r.
\]

The Stage-D gain is not generally `Gamma_m^B`. Splitting on `tau<m` gives the
exact identity

\[
 \boxed{\widetilde\Gamma_m
   =\frac1m\sum_{r=0}^{m-1}\gamma_r+C_m},
 \qquad
 C_m=E_0\!\left[
   \mathbf1_{\{\tau<m\}}\left(\frac1\tau-\frac1m\right)T_\tau^2
 \right].
\]

Here `C_m>=0`; it is strictly positive whenever a short cycle has positive
probability and nonzero stopped sum. For the frozen CUSUM and every `m>1`, the
event `tau=1` has positive probability and `T_tau` is nonzero there, so
`C_m>0`. This explains the observed Stage-D convention-A/convention-B gap.

At `m=1`, `C_1=0`, `A_1=Z_tau`, and
`widetilde Gamma_1=gamma_0=E_0[Z_tau T_tau]`, the established Level 1–3 object.

## 7. Audit conclusion

The scalar derivative framing is valid for the Stage-D map only when
`Gamma_m` means the **direct truncated-window gain** `widetilde Gamma_m`.
The historical equality `Gamma_m=(1/m)sum_{r<m}gamma_r` is false under that
convention because it omits `C_m`. Historical D2.3 remains failed; this audit
does not alter it.
