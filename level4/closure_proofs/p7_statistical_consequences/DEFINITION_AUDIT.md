# P7 definition audit

**Status:** the P7 monitoring object is *identical* to the object the closed
P1/P2/P3 derivative theorems are about. No convention is introduced, relaxed or
renamed. Correspondence is enforced mechanically, not asserted (§6).

P7 measures statistical consequences. It proves nothing about detectors and it
does not restate P1--P3; it imports them.

---

## 1. Inventory of every convention P7 relies on

| Object | Authoritative source | Exact meaning used by P7 | Finding |
|---|---|---|---|
| reference error | `level4/stage_d/src/stopped.py`; P1 `THEOREM.md` §1 | `e = R_j - mu`, the entering reference minus the in-control location | match |
| innovation | same | `z_t = X_t - R_j`, so in control `z_t ~ N(-e, 1)` | match |
| CUSUM recurrence | `level4/src/rebaseguard_level4/frozen.py::cusum_update` | `S+ = max(0, S+ + z - 1/2)`, `S- = max(0, S- - z - 1/2)`, `k=1/2`, `h=5` | **imported by reference, never re-implemented** |
| SR recurrence | `level4/stage_d/src/stopped.py::_sr_update` | `R+ = (1+R+)exp(z-1/2)`, `R- = (1+R-)exp(-z-1/2)`, log-domain softplus, no head start | restated verbatim in `src/rebaseguard_p7/detectors.py::sr_update` |
| SR threshold | `level4/stage_d/results/calibration_d1.json` | natural `A = 520.886133602749`; `log` taken exactly once | match |
| alarm convention | frozen model §4 | inclusive `>=`, tested **after** the update, plus-arm priority on ties | match |
| stopping time | `stopped.py::simulate_stopped` | ordinary `tau = inf{t>=1 : alarm after the update at t}`; **no minimum dwell** | match (Stage D, not Stage A) |
| terminal increment | same | included in `T_tau` and in the reuse window | match |
| reuse window | `STAGE_D_PROTOCOL.md` §1 (convention A) | `w = min(m, tau)`, `zbar_m = (1/w) sum_{r<w} z_{tau-r}` | match |
| `tau < m` branch | P1 `DEFINITION_AUDIT.md` §3 | denominator is `tau`, not `m`; `zbar_m = T_tau/tau` | match |
| random denominator | P1 `DEFINITION_AUDIT.md` §4 | `1 <= w <= m`, never singular, correlated with the suffix | match |
| gain | P1/P2 `THEOREM.md` | `GammaTilde_{D,m} = E_0[zbar_m T_tau]` | imported from P3, and independently re-measured as a correspondence check |
| reference update | `level4/stage_d/src/chain.py` | `e_{j+1} = rho*(e_j + zbar_m) + (1-rho)*fresh` | match (see §2) |
| fresh reference | `frozen.py::fresh_statistic_scale` | `fresh ~ N(0, 1/m)`, independent of the stopping event | match |
| `rho` semantics | P3 `THEOREM.md` §2 | reuse fraction on `[0,1]`; `0` = pure fresh, `1` = full reuse | match |
| detector reset | `chain.py` | `S+ = S- = 0` (resp. `Y+ = Y- = 0`) and the lag buffer cleared at every alarm | match |
| cycle reset | `chain.py` | the cycle clock restarts at `t = 1`; only the *reference* carries information across cycles | match |
| out-of-control shift | `chain.py` (`e -= shift`) | a process-mean shift `+Delta` is exactly the reference-error offset `-Delta`; the two are the same code path | match |
| multiplier | P3 `THEOREM.md` §1 | `lambda_{D,m}(rho) = rho(1 - GammaTilde_{D,m})` | imported |
| critical fraction | P3 `results/boundary_table.json` | `rho_c = 1/|1 - GammaTilde|`, read from the closed artifact at run time | **loaded, never transcribed** |

## 2. One historical ambiguity, already resolved upstream

`STAGE_D_PROTOCOL.md` §2 writes the reuse rule as
`e_{j+1} = rho*zbar_m + (1-rho)*fresh`, omitting the `e_j` term. That line is
loose: the reused *reference* is `R_{j+1} = R_j + zbar_m`, so the reused
*error* is `e_j + zbar_m`. P1's `DEFINITION_AUDIT.md` (row "Stage-D post-alarm
map") and `chain.py` both record the resolved form
`e_{j+1} = rho*(e_j + zbar_m) + (1-rho)*fresh`, which is also the map whose
derivative P1/P2 compute (`F_{rho,m}(e) = rho(e + E_e[zbar_m])`).

P7 uses the resolved form. Nothing upstream is edited.

## 3. Metric definitions fixed for P7

Let `pi_j` be the law of the entering reference error `e_j` at cycle `j`.

| metric | definition | statistical unit |
|---|---|---|
| `A(x)` run-length response | `E[tau | reset state, z_t ~ N(-x,1)]` | independent cycle |
| `ARL_0` (chain) | mean cycle length over post-burn-in cycles | **replicate** |
| nominal `ARL_0` | `A(0)` = the calibrated frozen value (~465.5) | independent cycle |
| finite-cycle `ARL_j` | mean of `tau_j` across replicates, chain started at `e_0 = 0` | replicate |
| false-alarm probability | `FAP(N) = P(tau <= N)` over post-burn-in cycles | replicate |
| false-alarm rate | renewal rate `1/ARL_0(chain)` alarms per observation | derived |
| detection delay | `E[tau]` in the cycle in which the shift `Delta` is present, the shift being applied at a re-baselining instant (the D2.5 convention) | replicate |
| delay ratio | `R_Delta = E[tau_Delta] / E[tau_0]` (D2.5) | derived |
| reference MSE | `E[e^2]` over post-burn-in cycles | replicate |
| `ACF1(e)` | lag-1 autocorrelation of `e_j` post burn-in | pooled cycles |

**Conditioning.** Every chain quantity is *unconditional* on the alarm arm and
is taken with `e_0 = 0` exactly, i.e. from the frozen safe-reference start. Two
distinct controls are reported and never merged: the **nominal** control
`A(0)` (a reference that is never updated) and the **fresh** control `rho = 0`
(a reference re-estimated from `m` fresh observations each cycle). Most of the
absolute ARL loss belongs to the second, and attributing it to reuse would be
an error; reuse-attributable distortion is always quoted against `rho = 0` at
the same `m`.

**Burn-in.** `e_0 = 0` is not stationary, so post-burn-in metrics are
*quasi-stationary*, not stationary. `burn_in = 12` cycles is used; the
finite-cycle curve in the same run is what justifies it (§ `STATISTICAL_CONSEQUENCES.md`).

## 4. Seeds

Seed family `20260831`, distinct from Stage D's `20261001` and from every
closed campaign, so no P7 stream can alias an inherited one. Every run derives
its stream from `np.random.SeedSequence([20260831, stage, detector, m, rho])`
and every batch takes its own spawned child, the Stage-D pattern.

## 5. Innovation reuse

There is **no** innovation reuse between cycles other than through the scalar
reference `e_j`. The lag buffer, both detector arms and the cycle clock are
cleared at every alarm. This is what makes the exact decomposition of
`THEORY_BRIDGE.md` §1 valid.

## 6. Mechanical correspondence checks

`tests/test_correspondence.py` asserts, and does not merely claim:

1. the P7 chain reproduces `level4/stage_d/src/chain.py` **bit-identically**
   (`tau`, `e_start`, `direction`) for CUSUM at several `(m, rho)`, from the
   same seed -- the RNG is consumed in the same order;
2. the P7 cycle simulator reproduces `level4/stage_d/src/stopped.py`'s
   convention-A `Gamma_m` **bit-identically** for both detectors;
3. `rho_c` used by P7 equals the value in P3's `boundary_table.json` exactly;
4. `w = min(m, tau)` and the `tau < m` branch behave as P1 §3 specifies;
5. `A(x)` is even and `g_m(x)` is odd, within Monte Carlo error.
