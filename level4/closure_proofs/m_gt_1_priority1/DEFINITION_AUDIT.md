# Definition audit

**Audit status:** internally consistent Level-4 definition selected; formal
proof may proceed.

## 1. Source inventory

| Object | Exact source | Mathematical content | Implementation match | Finding |
|---|---|---|---|---|
| Ordinary stopping time `tau` | `level4/stage_d/STAGE_D_PROTOCOL.md`, lines 50--55; `level4/stage_d/src/stopped.py::simulate_stopped` | First `t >= 1` whose post-update CUSUM state reaches the inclusive threshold | The loop starts at 1, updates, then tests `>= h`; the completed path includes that step | Match |
| Frozen CUSUM recurrence | `level4/src/rebaseguard_level4/frozen.py::cusum_update`; frozen model lines 10--17 | `S+_t=max(0,S+_{t-1}+Z_t-1/2)`, `S-_t=max(0,S-_{t-1}-Z_t-1/2)`, alarm at `max >= 5` | Stage D imports this recurrence; the new numerical route independently restates and regression-tests it | Match |
| Stopped sum `T_tau` | `level4/stage_d/src/stopped.py::simulate_stopped` (`total`, `T`) | `sum_{t=1}^tau Z_t`, terminal increment included | `total` is updated before crossing paths are copied to `T` | Match |
| Nominal window `m` | Stage-D blueprint section 2.1; `STAGE_D_PROTOCOL.md` section 1 | Positive integer maximum number of reused terminal observations | `m_grid` is integral and positive in Stage D and in this campaign | Match |
| Realized window `w_m` | blueprint lines 139--145; `STAGE_D_PROTOCOL.md` lines 28--33 | `min(m,tau)` | Stage D uses `np.minimum(m,tau)` | Match |
| Truncated statistic `A_m` | `STAGE_D_PROTOCOL.md` lines 28--33 | `(1/w_m) sum_{r=0}^{w_m-1} Z_{tau-r}` | `stopped.py` reverses the ring buffer, masks lags beyond `tau`, indexes the cumulative sum at `w_m-1`, and divides by `w_m` | Match |
| Stage-D post-alarm map | `level4/stage_d/src/chain.py::simulate_chain`; `stopped.py::StoppedStats.induced_map` | Reused raw reference error is `e+A_m`; mixed next error has conditional mean `rho(e+E_e[A_m])` because fresh data are centered and independent | `chain.py` computes `rho*(e+zbar)+(1-rho)*fresh`; `induced_map` computes `e+mean(zbar)` at full reuse | Match |
| Stage-A minimum dwell | `level4/src/rebaseguard_level4/conditional.py::simulate_cycle_batch`, lines 133--135; `multicycle.py::simulate_multicycle` | `tau_m=inf{t>=m: alarm at t}` for `m>1` | Crossings before `m` are ignored while the recursion continues | Match to Stage A; not Stage D |
| Stage-A reused statistic | `conditional.py`, lines 143 and 153; `multicycle.py`, lines 222--225 | Full `m`-point sum divided by fixed `m`; dwell guarantees `tau_m>=m` | Ring buffer contains a full window at eligible alarm | Match to Stage A; not Stage D |
| Fixed-denominator diagnostic `B_m` | `stage_d/src/stopped.py` module documentation and `gamma_m("B")` | `(1/m) sum_{r<min(m,tau)} Z_{tau-r}` | Accumulator `b_num` divides by `m` | Match, but diagnostic only |
| Track 1B theorem | `level4/closure_proofs/m_gt_1_track1b/THEOREM.md` | Prior statement of the score identity and short-cycle correction | Read-only regression anchor | Not reused as a campaign deliverable |

## 2. Resolved historical ambiguity

The Stage-D blueprint correctly defines `A_m` with denominator `w_m` at lines
141--145, but line 151 also identifies its expectation with the fixed-
denominator lag average. Those claims are incompatible when `P(tau<m)>0`.
The frozen Stage-D protocol already records the resolution: convention A,
with denominator `w_m`, is authoritative; the fixed-denominator expression is
only the auxiliary `B_m` diagnostic. This campaign preserves that history and
does not edit either source.

Stage A and Stage D are not two implementations of one `m>1` object. Stage A
changes the stopping law by imposing a dwell. Stage D holds the detector's
ordinary stopping rule fixed and truncates the available data. They coincide
at `m=1`, when the dwell restriction is vacuous and `w_1=1`.

## 3. Edge cases

### `tau < m`

The retained suffix is the entire path. Therefore

```text
w_m=tau,
sum_{r=0}^{w_m-1} Z_{tau-r}=T_tau,
A_m=T_tau/tau.
```

The denominator is `tau`, not `m`. Replacing it by `m` omits the exact
correction

```text
Q_m=(1/tau-1/m)T_tau^2 > = 0.
```

### `tau = m`

Both descriptions retain the entire path, but `w_m=tau=m`; there is no
correction and both denominators coincide.

### `tau > m`

Only the last `m` increments are retained, `w_m=m`, and the truncated and
fixed denominators coincide.

## 4. Random denominator: differentiability and integrability

Because `tau>=1` and `m>=1`, `1<=w_m<=m` and `0<1/w_m<=1`. The denominator
cannot vanish and creates no analytic singularity. It is an integer-valued
stopped-path functional independent of the real perturbation parameter once a
path is represented on the stopped sigma-field. Thus it does not itself add a
derivative term.

It does create dependence: `w_m`, the suffix sum, and `T_tau` are functions of
the same stopped path. Consequently expectation cannot be moved through the
random reciprocal or replaced by `1/m`.

For fixed finite `m`,

```text
abs(A_m) <= sum_{r=0}^{w_m-1} abs(Z_{tau-r})
          <= sum_{t=1}^{tau} abs(Z_t).
```

The theorem therefore states integrability of `A_m`, `A_m T_tau`, and a local
dominator explicitly. In the frozen Gaussian CUSUM specialization, these are
discharged in the human proof from the assumed stopped exponential-moment
bound. The Lean spine consumes abstract versions of these assumptions and
does not claim to establish the concrete Gaussian stopped-moment bound.

## 5. Audit decision

The Level-4 object is internally consistent:

```text
ordinary tau; inclusive post-update alarm; terminal increment included;
w_m=min(m,tau); denominator w_m; F_{rho,m}(e)=rho(e+E_e[A_m]).
```

The only genuine mismatch is historical and already visible: Stage A is a
different `m>1` stochastic object, and the blueprint's fixed-denominator
closed form is not valid for convention A. Neither is patched. The new proof
is authorized against the Level-4 definition above.
