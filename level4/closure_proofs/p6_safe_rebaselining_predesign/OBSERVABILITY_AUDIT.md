# P6 observability audit

**This is the most load-bearing document in the pre-design.** A prescriptive
campaign whose policy secretly reads a latent variable produces a method that
cannot be deployed and a result that is not merely wrong but *unfalsifiable by
its own experiments*. `X11` forbids it; this document makes the forbidding
operational, and `src/rebaseguard_p6/policy.py` makes it structural.

---

## 1. The two coordinate systems

The frozen model is written in **error coordinates** (`D2`, `D8`):

```
z_t = raw_t - e_j ,      e_j = mu_j - theta
```

where `mu_j` is the reference value the operator is actually using in cycle `j`
and `theta` is the true process mean. The operator's world is

| quantity | operator knows it? | why |
|---|---|---|
| `mu_j` (the reference value in use) | **yes** — the operator computed it | |
| `x_t` (the raw observation as recorded) | **yes** | |
| `z_t = x_t - mu_j` | **yes** — this is the detector input | |
| `theta` (true mean) | **no** | it is the thing being monitored |
| `raw_t = x_t - theta` | **no** | requires `theta` |
| `e_j = mu_j - theta` | **no** | requires `theta` |

So: **everything the frozen code writes in `raw` or `e` coordinates is latent;
everything it writes in `z` or `mu` coordinates is observable.** That single
sentence resolves most of the audit, and it is worth stating because the frozen
simulator works natively in the *latent* coordinate system — which is exactly
why an accidental leak is easy to write and hard to see.

## 2. Feature-by-feature audit

`YES` = legally usable by an implementable policy at the alarm ending cycle `j`.

| # | feature | available before alarm | at alarm | after alarm | verdict | note |
|---|---|---|---|---|---|---|
| F01 | `tau_j` (cycle length) | no | **yes** | yes | **YES** | the single most informative scalar; see §3.2 |
| F02 | alarm arm / direction (`+1/-1`) | no | **yes** | yes | **YES** | sign information |
| F03 | detector statistic at alarm (`plus`, `minus`) | yes (running) | **yes** | yes | **YES** | |
| F04 | alarm **overshoot** beyond threshold | no | **yes** | yes | **YES** | `plus - h` (CUSUM) or `log r_plus - log A` (SR) |
| F05 | the terminal window `{z_{tau_j}, ..., z_{tau_j - L+1}}`, `L = ` preregistered cap | partially | **yes** | yes | **YES** | the operator stored these; capping `L` is a memory-budget decision, not an information one |
| F06 | `zbar_j(m)` for **any** candidate `m <= L` | no | **yes** | yes | **YES** | but see the selection hazard, §6 |
| F07 | terminal-window sample variance | no | **yes** | yes | **YES** | weak feature; estimates the innovation variance (`= 1`), not `e` |
| F08 | window mean magnitude `|zbar_j|` | no | **yes** | yes | **YES** | the high-gain sensor, §3.1 |
| F09 | **previous reference movement** `mu_j - mu_{j-1}` | yes | yes | yes | **YES** | equals `e_j - e_{j-1}` exactly; see §4 — this is a *differences-are-observable* result and it is not obvious |
| F10 | cumulative displacement `d_j = mu_j - mu_0 = e_j - e_0` | yes | yes | yes | **YES** | §4 |
| F11 | history `{(tau_i, zbar_i, overshoot_i, direction_i)}_{i <= j}` | yes | yes | yes | **YES** | enables pooling, §4 |
| F12 | the cycle index `j` and the number of re-baselinings so far | yes | yes | yes | **YES** | licences warm-up schedules |
| F13 | `k_i`, `m_i`, `rho_i` chosen in the past | yes | yes | yes | **YES** | the policy's own history |
| F14 | `e_j` (entering reference error) | — | — | — | **NO — LATENT** | `X11`. Oracle only |
| F15 | `Rbar_j = e_j + zbar_j` (raw-window mean) | — | — | — | **NO — LATENT** | it is `zbar_j` shifted by the latent `e_j` |
| F16 | `R(e_j)`, `S(e_j)`, `A(e_j)` evaluated at the true `e_j` | — | — | — | **NO — LATENT** | the *functions* are known; the *argument* is not |
| F17 | `e_{j+1}` (the consequence of the decision) | — | — | — | **NO — LATENT and FUTURE** | oracle only |
| F18 | `Delta` (the shift), or whether a shift has occurred | — | — | — | **NO — never observable** | `H8`; see §5 |
| F19 | `tau_{j+1}` or any post-decision outcome | — | — | — | **NO — FUTURE** | |
| F20 | the stationary law `pi` of the *current* policy | — | — | — | **NO for online use** | a *precomputed* law for a *fixed* design is a design-time constant, which is legal; a law of the running closed loop is not |
| F21 | precomputed frozen tables: `A(.)`, the law of `tau` given `e`, `GammaTilde_{D,m}` | design time | — | — | **YES as constants** | they are functions, computed offline; using them does not require knowing `e` |

**F21 deserves emphasis.** A policy may carry a lookup table of `A(e)` or of
`P(tau = t | e)` and still be implementable, because it uses the table to form a
*likelihood over* `e`, never to evaluate at the true `e`. The distinction
between "knows the function" and "knows the argument" is the whole audit.

## 3. The two implementable sensors

### 3.1 `zbar_j` is a **high-gain** readout of the latent error

From the frozen definitions alone (`D2`, `D5`: `z_t = raw_t - e_j`, and the
window average of a constant is that constant),

```
zbar_j  =  Rbar_j - e_j ,        so       E[ zbar_j | e_j = e ]  =  R(e) - e .
```

Differentiating at the origin and substituting the **closed** local identity
`R'(0) = 1 - GammaTilde_{D,m}` (`L1`, `L2`):

```
d/de  E[ zbar | e ] |_{e=0}   =   R'(0) - 1   =   - GammaTilde_{D,m}
                              in  [ -17.3 , -11.8 ]        (L4)
```

> **The selection effect that causes the damage is also a sensor.** Near the
> origin, `zbar` responds to the latent reference error with a gain of `12x` to
> `17x`, not `1x`. A reference error of `0.05` — the tolerance implied by `E1` —
> produces a mean `zbar` of about `-0.6`, against a per-cycle noise sd of
> `sqrt(S(0)) ~ 2.0` (`P11`, provisional). One cycle gives `SNR ~ 0.3`; ten
> pooled cycles give `SNR ~ 0.9`.

This is a `DESIGN_HYPOTHESIS` (`H1`) as a *method*, but the gain statement rests
only on `L1`/`L2`/`L4`, which are `AUTHORITATIVE_CLOSED`. It therefore survives
every P5 branch. The magnitude of the noise (`S(0) ~ 4.04`) is `PROVISIONAL_P5`
(`P11`) and must be re-measured by P6 rather than imported.

Far from the origin the gain degrades to `1x` (because `R -> 0`, `P10`), so the
sensor is sharp exactly where the tolerance is tight and blunt where the error
is already obviously large. That is a favourable, not an unfavourable, shape.

### 3.2 `tau_j` is a **sign-blind** readout of `|e_j|`

`A` is even and steeply decreasing in `|e|` (`S2`, closed): `A(0)=465`,
`A(0.2)=191`, `A(0.5)=38`. A short cycle is strong evidence of a large `|e_j|`.
`tau_j` carries no sign information (`T3`-type symmetry, and `S2`'s evenness),
so it must be combined with `F02`/`F08` to be actionable.

`tau_j` is also **geometric-tailed and therefore individually noisy**: one cycle
of length `40` is weak evidence. The likelihood-based pooling of §4 is what
makes it useful.

## 4. Differences of the latent state **are** observable

This is the audit's least obvious result, and it changes what P6 can build.

The operator computes `mu_{j+1}` from quantities it knows. With `theta`
constant,

```
e_{j+1} - e_j  =  mu_{j+1} - mu_j          (exactly, and observably)
```

so the whole **increment path** of the latent state is known, and

```
e_j  =  e_0 + d_j ,        d_j := mu_j - mu_0     observable ,
```

with a single unknown scalar `e_0` — the error of the very first baseline,
distributed `N(0, 1/m_0)` with `m_0` known to the operator.

**Two consequences, one positive and one that prevents over-claiming.**

* *(positive)* The filtering problem is **one-dimensional in a fixed unknown**,
  not a general nonlinear filtering problem. Every cycle's reading can be
  *aligned* by its known offset and pooled:
  ```
  zbar_i + d_i   is a readout of   -e_0   (with bias R(e_i)),  for every i,
  ```
  so `n` cycles reduce the sensor variance by `~1/n` instead of estimating a
  fresh unknown each time. A concrete implementable estimator is
  ```
  ehat_j  =  d_j  -  (1/n) sum_{i=j-n+1}^{j} ( zbar_i + d_i ) .
  ```
  This is `DESIGN_HYPOTHESIS H3`. Its bias is `-(1/n) sum R(e_i)`, which is
  **not** small — `sup|R|` is of order `1` (`P5`/`P9`, provisional) — so the raw
  form above is a starting point, not the proposal. The bias-corrected version
  needs the `R` table (`F21`) and is stated in `P6_METHOD_CANDIDATES.md`
  Family E.
* *(preventing over-claiming)* Knowing every increment does **not** solve the
  problem. The chain forgets `e_0` dynamically (`P10`), so `d_j` alone tells the
  operator only that `e_j` is `O(1)` — which is just the stationary law. The
  prior sd of `e_0` is `1/sqrt(m_0)` (`0.45` at `m_0 = 5`), an order of magnitude
  above the `~0.05` tolerance of `E1`. All genuine information about the *level*
  comes from `{(tau_i, zbar_i)}` through the frozen likelihood, and it arrives
  slowly. **P6 must not present increment observability as a solution.**

Note also that this construction is exactly where a real deployment would break
first: it assumes `theta` constant, i.e. **no shift**. Under a shift, `mu_{j+1}
- mu_j` is still observable but no longer equals `e_{j+1} - e_j`, and the filter
is misspecified. That misspecification is simultaneously a hazard (`F10` in
`FAILURE_MODE_REGISTER.md`) and a possible signal, and P6 must evaluate any
filter-based policy under `Delta > 0`, not only at `Delta = 0`.

## 4a. Addendum — the history channel leaks whenever `e_0` is known

This was found while implementing the harness, and it is the kind of defect the
audit exists to catch, so it is recorded rather than quietly fixed.

The frozen simulator runs with `theta = 0` and, in P7's finite-cycle
convention, with `e_0 = 0`. In that setting

```
d_j  =  e_j - e_0  =  e_j
```

exactly. So handing `displacement` to a policy in a run with a **known** `e_0`
hands it the latent state — a perfect instance of `F1`, arriving through a
channel that §4 had just certified as legal. The channel is legal; the
*initialisation* is what breaks it, and the two are easy to separate only once
they have been separated.

**Resolution, enforced in `chain.simulate_policy_chain`:**

| `e0` | meaning | `displacement` / `last_move` |
|---|---|---|
| `None` | draw `e_0 ~ N(0, 1/m0)` per replicate — the deployable setting; `e_0` is unknown to the policy | **supplied** |
| a float (e.g. `0.0`, P7's convention) | a *known* initial error | **withheld (NaN)**, and a policy declaring `uses_history = True` is refused with an error |

`tests/test_observability.py` asserts both directions.

**Two consequences for the campaign.**

1. Any Family E policy must be evaluated in the `e0 = None` regime. It therefore
   cannot be evaluated in R1/R2/R3 as those are currently specified
   (`EVALUATION_PROTOCOL.md` §5 fixes `e_0 = 0` for the finite-cycle regimes).
   Either those regimes gain an `e0 = None` variant for history-using policies,
   or such policies are reported in R4 only — with the loss of finite-cycle
   evidence stated. **This is an open design decision for the entry gate.**
2. More generally: *an information channel can be legal in the model and
   leaky in the simulation*. The audit must be re-run against the harness, not
   only against the mathematics. No other channel in §2 has this property —
   `tau`, the window, the overshoot and the policy's own history are all
   observable regardless of how `e_0` is initialised — but the check should be
   repeated for any field added later.

## 5. The blind spot has no implementable proxy

`S10` identifies the mechanism behind the delay tail: a cycle whose entering
`e_j` happens to sit near the post-change mean is effectively blind, and
`P(|e - Delta| < 0.2)` is the risk. But `Delta` is unobservable in *direction*
as well as magnitude (`F18`), so **no implementable policy can target the blind
spot directly.**

The honest surrogate chain is:

```
blind-spot risk  ->  needs |e - Delta| small  ->  Delta unknown, sign unknown
                 ->  minimise mass of |e| away from 0 in EVERY direction
                 ->  implementable target: OutCal(beta) = P(|e| > c_beta)
```

This is `H8`, and it is why `SAFETY_OBJECTIVES.md` offers `OutCal` as the
surrogate objective `O2` while insisting the delay tail `Dtail` be *measured*
rather than inferred (`S18`, `X6`). An oracle policy that knows `Delta` is a
legitimate **ceiling** (§7 of `P6_METHOD_CANDIDATES.md`) and an illegitimate
method.

## 6. Two legal-but-hazardous mechanisms

Both are permitted by this audit and both need a preregistered guard.

* **Post-hoc window selection (`F06`).** Choosing `m_j` *after* inspecting
  `zbar_j(m)` for every candidate `m` is legal — the operator really does have
  those numbers. But a rule such as "pick the `m` minimising `|zbar_j(m)|`"
  selects on the noise and biases the reference update toward *not moving*,
  which under a real shift is exactly the wrong direction. Any policy that
  selects `m` on window contents must be evaluated at `Delta > 0` and must be
  compared against the same policy with `m` chosen from `tau_j` alone.
* **History-dependent gains (`F11`).** A policy that adapts on its own past
  decisions creates a feedback loop with no stationarity guarantee (`H7`). It
  must be run for enough cycles to expose slow instabilities
  (`EVALUATION_PROTOCOL.md` §5) and must never be validated on cycle 1.

## 7. The three policy classes

The distinction is enforced in code, not in prose.

| class | may read | purpose | may be recommended? |
|---|---|---|---|
| **implementable** | `F01`–`F13`, `F21` | the actual P6 deliverable | **yes** |
| **oracle** | additionally `F14`–`F19` (`e_j`, `e_{j+1}`, `Delta`) | quantify the *ceiling* on what adaptive control could ever buy | **never** |
| **diagnostic** | anything, including the stationary law | explain *why* a policy behaves as it does | **never** |

Enforcement (`src/rebaseguard_p6/policy.py`):

1. Implementable policies receive a `CycleObservation` object that **has no
   field containing `e`, `raw`, `Rbar` or `shift`**. There is nothing to leak.
2. Oracle policies must set `requires_oracle = True`; only then does the chain
   construct an `OracleObservation` carrying the latent fields.
3. `tests/test_observability.py` asserts (a) every registered implementable
   policy has `requires_oracle = False`, (b) `CycleObservation`'s field set is
   exactly the audited list, and (c) an implementable policy asked for a latent
   attribute raises rather than silently returning something.
4. Every results record carries the policy's class, so a table can never mix an
   oracle into a recommendation without it being visible.
