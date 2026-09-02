# P9R theory — the exact core, the one missing premise, and nothing else

P9 asserted one theorem, `P9-T2`, at `EXACT_THEOREM` class. Independent
adjudication found that its identity content is exact and its strict inequality
is not: the proof used global monotonicity of the run-length response `A` as
though authoritative P7 had proved it. P7's own adjudication says the opposite —
*"Global strict monotonicity of `A` is not proved."*

P9R therefore splits `P9-T2` into an exact theorem and a conditional theorem,
and it makes the missing premise a named object (`ASM-DOM`) that appears in the
claim ledger, in the dependency graph, and in every sentence that depends on it.

The repair also **weakens the premise that is actually needed**. Monotonicity is
sufficient but not necessary: the strict-deficit argument needs only that `A`
attains its maximum at `e = 0` almost everywhere. That is a strictly weaker
hypothesis, so `P9R-T2b` is a strictly stronger conditional theorem than the
one P9 would have obtained by simply labelling its own proof conditional.

Throughout, `D` is one of the two frozen detectors

* two-sided CUSUM, `k = 1/2`, `h = 5`, inclusive post-update alarm;
* symmetric two-chart SR, `A = 520.886133602749`, **no headstart** (`R_0 = 0`),
  inclusive post-update alarm on the raw state,

`m >= 1` is the window, convention A is the frozen re-baselining convention
(`w = min(m, tau)`, denominator `w`, `F ~ N(0, 1/m)` independent of the stopping
event), and

```text
A(e) := E_e[tau]
```

is the expected length of one cycle started from the reset detector state with
constant entering reference error `e`. `A` is a property of the detector alone:
it does not depend on `m` or on `rho`.

---

## 1. Four exact lemmas

These are elementary. They are stated separately because each one carries part
of the load that P9 tried to carry with monotonicity, and because two of them
(`L2`, `L4`) make the strictness half of `P9R-T2b` free.

### Lemma L1 (evenness) — `EXACT`

> `A(e) = A(-e)` for every `e` and both frozen detectors.

*Proof.* Under `P_e` the innovations are `Z_t = X_t - e` with `X_t` iid
`N(0,1)`. The map `omega -> -omega` on the innovation sequence sends `X_t` to
`-X_t`, whose law is again iid `N(0,1)`, and sends `Z_t` to `-Z_t - 2e`, i.e. to
the innovation sequence of `P_{-e}` after also exchanging the two charts. Both
frozen detectors are exactly symmetric under simultaneously negating `Z` and
exchanging the two arms: `S+ <-> S-` for CUSUM by inspection of
`max(0, S +- Z - k)`, and `R+ <-> R-` for SR by inspection of
`(1 + R) exp(+-Z - 1/2)`. The alarm rule `max(.,.) >= threshold` is symmetric
in the two arms, so the stopping time is preserved pathwise. Hence `tau` has the
same law under `P_e` and `P_{-e}`. ∎

`L1` is *not* monotonicity and does not imply it.

### Lemma L2 (uniform boundedness and integrability) — `EXACT`

> `sup_{e in R} A(e) <= C_D < infinity`, with
> `C_CUSUM = 10 / Phi(-1)^10` and `C_SR = 1 / Phi(-(log A + 1/2))`.
> Consequently `A` is integrable under **every** probability law on `e`, and for
> any `L > 0` and any law `pi`,
> `int_{|e| > L} A d(pi) <= C_D * pi(|e| > L)`.

*Proof.* SR: from any reachable state `y >= 0`, a single innovation with
`Z_t >= log A + 1/2` gives `ell_t = y + Z_t - 1/2 >= log A`, an inclusive
crossing; symmetrically for `Z_t <= -(log A + 1/2)`. For every `e`, at least one
of the two directions has probability at least `Phi(-(log A + 1/2))`: if
`e <= 0` then `P(Z >= c) = P(X >= c + e) >= Phi(-c)`, and if `e >= 0` then
`P(Z <= -c) = P(X <= e - c) >= Phi(-c)`. So `tau` is dominated by a geometric
variable with success probability at least `Phi(-c)`, uniformly in `e`.

CUSUM: from any reachable state, ten consecutive innovations with `Z_t >= 1`
increase `S+` by at least `1 - k = 1/2` each and so reach `h = 5`; symmetrically
for ten consecutive `Z_t <= -1`. By the same one-sided argument, for every `e`
one of the two directions has per-step probability at least `Phi(-1)`, so `tau`
is dominated by `10` times a geometric variable with success probability at
least `Phi(-1)^10`, uniformly in `e`.

The constants are loose by design; only finiteness and uniformity are used. ∎

`L2` is what makes the mixture in `P9R-T2a` well defined without borrowing
anything from `P5-T7`'s ergodicity constants, and it is what turns the
quadrature truncation error in the numerical work into a *rigorous* bound rather
than an unquantified remainder.

### Lemma L3 (`A(0) > 1`) — `EXACT`

> `A(0) > 1` for both frozen detectors.

*Proof.* `A(0) >= 1 + P_0(tau > 1)`. At `e = 0` an alarm at `t = 1` from the
reset state requires `|Z_1| >= h + k = 5.5` (CUSUM) or `|Z_1| >= log A + 1/2`
(SR); each has probability strictly below one, so `P_0(tau > 1) > 0`. ∎

### Lemma L4 (`A(e) -> 1`, hence a positive-measure strict set) — `EXACT`

> `A(e) -> 1` as `e -> +infinity`, and by `L1` also as `e -> -infinity`.
> Consequently there exists `e*` with `A(e) < A(0)` for every `e >= e*`, and
> `N(0, 1/m)(\{e >= e*\}) > 0` for every `m >= 1`.

*Proof.* CUSUM: after one step, `S^-_1 = max(0, -Z_1 - k) = max(0, e - X_1 - k)`,
so the event `\{X_1 <= e - h - k\}` forces `S^-_1 >= h` and an alarm at `t = 1`.
Its probability is `Phi(e - 5.5) -> 1`. SR: the event
`\{X_1 <= e - (log A + 1/2)\}` forces `ell^-_1 >= log A` and has probability
`Phi(e - log A - 1/2) -> 1`. In both cases `P_e(tau = 1) -> 1`; combined with
the uniform integrability of `L2`, `A(e) = E_e[tau] -> 1`. Since `A(0) > 1` by
`L3`, there is `e*` beyond which `A(e) < A(0)`, and the Gaussian law gives every
half-line positive measure. ∎

`L4` supplies **strictness for free**. This matters: it means the only thing
separating `P9R-T2b` from an exact theorem is the *upper bound*, not the strict
part, and it is why P9R does not need — and does not claim — monotonicity.

---

## 2. `P9R-T2a` — the exact `rho = 0` core

> **Theorem P9R-T2a.** Fix a frozen detector `D`, convention A, a window
> `m >= 1`, and set `rho = 0`. Then:
>
> 1. `e_{j+1} ~ N(0, 1/m)` independently of the current state; hence `N(0,1/m)`
>    is an invariant law of the reference-error chain and it is the unique one;
> 2. the stationary in-control ARL is exactly
>    `ARL_0 = E_{e ~ N(0,1/m)}[A(e)]`, and this expectation is finite;
> 3. the first-order local multiplier `rho(1 - Gamma)` is exactly `0`, the
>    minimum possible absolute multiplier on `rho in [0,1]`.

*Proof.* **(1)** `P5-T1` gives the exact update
`e_{j+1} = rho * U + (1 - rho) * F` with `F ~ N(0, 1/m)` drawn independently of
the stopping event. At `rho = 0` the transition kernel is the constant kernel
`K(x, .) = N(0, 1/m)`, which ignores its argument. A constant kernel has exactly
one invariant law, namely itself. (`P5-T7` gives the same existence and
uniqueness conclusion for every fixed `rho`; at `rho = 0` it is immediate.)

**(2)** `P7-A-ID` is the exact finite-cycle identity `E[tau_j | e_j] = A(e_j)`,
and hence `ARL_0 = E_pi[A]` for any entering-error law `pi` for which `A` is
`pi`-integrable. Apply it with `pi = N(0,1/m)` from (1). Integrability is
unconditional by `L2`.

**(3)** `P3-T1` gives the conditional-mean map's multiplier as `rho(1 - Gamma)`;
at `rho = 0` it is `0` regardless of `Gamma`. ∎

**What T2a does not contain.** No inequality. No comparison with `A(0)`. No
operational conclusion. The phrase "maximally locally stable" is defensible
*only* in the first-order multiplier sense of (3); it is a statement about the
deterministic conditional-mean map, not about the stochastic chain and not about
monitoring performance.

`hypotheses = NONE_BEYOND_MODEL`. Premises: `P5-T1`, `P5-T7`, `P7-A-ID`,
`P9R-L2`, `P3-T1` — all `EXACT_THEOREM`, none conditional, none empirical.

---

## 3. `P9R-T2b` — the conditional strict deficit

> **Assumption ASM-DOM.** `A(e) <= A(0)` for `N(0,1/m)`-almost every `e`.
>
> **Theorem P9R-T2b.** Under `ASM-DOM`, and with the setting of `P9R-T2a`,
>
> ```text
> E_{e ~ N(0,1/m)}[A(e)]  <  A(0)     strictly.
> ```

*Proof.* Write `pi = N(0,1/m)`. By `L2`, `A` is `pi`-integrable, so the
expectation exists. By `ASM-DOM`, `A(0) - A(e) >= 0` for `pi`-a.e. `e`. By `L4`
there is `e*` with `A(0) - A(e) > 0` for all `e >= e*`, and `pi(\{e >= e*\}) > 0`.
A nonnegative measurable function that is strictly positive on a set of positive
measure has strictly positive integral, so
`A(0) - E_pi[A] = E_pi[A(0) - A(e)] > 0`. ∎

Three things are worth stating plainly.

1. **`ASM-DOM` is not established.** It is weaker than global monotonicity of
   `A` in `|e|`, which is also not established (`P7-A-MONO`,
   `GLOBAL_MONOTONICITY` in `RESULTS.md`). Every downstream sentence that uses
   the strict deficit must carry the hypothesis.
2. **Strictness is not the gap.** `L3` and `L4` discharge it unconditionally.
   The entire gap is the a.e. upper bound.
3. **P9R does not attempt to prove `ASM-DOM`.** A proof would require a
   stochastic-ordering or coupling argument showing that a nonzero reference
   error can only accelerate the two-sided detector, uniformly over the reset
   state. That is a genuine open problem for these detectors and it does not
   follow cleanly from existing machinery. Manufacturing it for the sake of
   closure is exactly the failure mode this repair exists to remove.

---

## 4. The operational corollary, narrowed

P9 wrote: *"no threshold in `rho` is an operational safety boundary."* That is
overbroad — it quantifies over every conceivable threshold, tolerance, metric,
detector and model class. P9R claims only the following.

> **P9R-T3 (negative result).** For the two frozen Gaussian detectors and
> `m in {1,2,3,5}`, `rho < rho_c` does **not** guarantee preservation of the
> nominal in-control ARL. At `rho = 0` — which lies strictly below `rho_c` for
> every supported `(D, m)` and at which the local multiplier is exactly zero —
> the entering reference is still an *estimate*, the stationary ARL is the
> mixture `E[A(e)]` of `P9R-T2a`, and that mixture is measured far below `A(0)`
> in every tested cell.

The exact content is `P9R-T2a`: at `rho = 0` the operating quantity is a
mixture, not `A(0)`. That the mixture is *smaller* is `P9R-T2b` if one grants
`ASM-DOM`, and is `P9R-E1`/`P9R-E3` empirically otherwise. Either way the
conclusion "being on the stable side of `rho_c` is not sufficient for
operational safety" survives — as an exact structural statement plus measured
magnitudes, not as a universal impossibility claim.

`rho_c` itself is untouched: it remains the exact local boundary of `P3-T1`.

---

## 5. Frozen SR recurrence — the algebra the repair rests on

The frozen symmetric two-chart SR chart is, in natural units,

```text
R+_0 = 0                      (no headstart)
R+_t = (1 + R+_{t-1}) exp(Z_t - 1/2)
alarm iff max(R+_t, R-_t) >= A       (inclusive, tested after the update)
```

The numerically stable log-domain form stores `y = log(1 + R)`, so `y_0 = 0`
encodes `R_0 = 0`, and each step is

```text
ell_t = y_{t-1} + Z_t - 1/2        (= log R_t, the ALARM statistic)
y_t   = logaddexp(0, ell_t)        (= log(1 + R_t), the STORED state)
```

Hand-checked first step, from `y_0 = 0`:

```text
ell_1 = 0 + Z_1 - 1/2 = Z_1 - 1/2          so   R_1 = exp(Z_1 - 1/2)
```

which is exactly `(1 + 0) exp(Z_1 - 1/2)`. Second step:

```text
y_1   = logaddexp(0, Z_1 - 1/2) = log(1 + exp(Z_1 - 1/2))
ell_2 = log(1 + R_1) + Z_2 - 1/2           so   R_2 = (1 + R_1) exp(Z_2 - 1/2)
```

P9 instead computed

```text
ell_t^{P9} = logaddexp(0, ell_{t-1}^{P9}) + Z_t - 1/2 ,   ell_0^{P9} = 0
```

i.e. it stored the alarm statistic in the slot that must hold the state and
initialised it to `0`, which encodes `R_0 = 1`, a headstart. On the first step
of every cycle,

```text
ell_1^{P9} = logaddexp(0, 0) + Z_1 - 1/2 = log 2 + Z_1 - 1/2
           = ell_1 + log 2                                    exactly.
```

Because the state is reset at every cycle boundary, the shift recurs at the
start of every cycle. It changes alarm decisions: with

```text
Z = log A + 1/2 - (log 2)/2
```

the frozen form gives `ell_1 = log A - (log 2)/2 < log A` (no alarm) while the
P9 form gives `ell_1^{P9} = log A + (log 2)/2 >= log A` (alarm).

`experiments/run_sr_recurrence_check.py` checks all of this deterministically,
including an eight-step path against the non-log recurrence, and
`tests/test_sr_recurrence.py` re-derives the same numbers independently of that
program.

---

## 6. What P9R deliberately does not attempt

| candidate | decision |
|---|---|
| prove `ASM-DOM` or global monotonicity | **declined** — it does not follow cleanly from existing machinery, and a forced proof is the failure mode being repaired |
| upgrade `P9-T2` to exact by any other route | **declined** — no route exists that avoids an upper bound on `A` |
| strengthen the operational corollary to a universal impossibility | **declined** — `P9R-T3` is deliberately narrower than P9's sentence |
| re-derive P8/P8R model-class transfer | **declined** — outside the repair mandate; `P8R-RECON` records the status distinction instead |
| a new novelty search | **declined** — `NOVELTY_STATUS = NOT_ESTABLISHED` stands |
