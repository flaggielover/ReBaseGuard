# P5 definition audit — the exact one-step reference-error recursion

Status: **prerequisite artifact.** No P5 experiment or theorem may be read
without it. Everything below is reconstructed from the frozen implementations,
not from prose, and the closing identity is verified numerically in
`tests/test_correspondence.py`.

## 1. Sources of truth

| object | frozen file | read-only use in P5 |
|---|---|---|
| CUSUM recurrence `k=1/2`, `h=5`, inclusive test | `level4/src/rebaseguard_level4/frozen.py::cusum_update` | imported through P7 |
| SR two-chart log-domain recurrence, `A=520.886133602749` | `level4/stage_d/src/stopped.py::_sr_update`, restated verbatim in `p7_.../detectors.py::sr_update` | imported |
| stopping / window / update conventions | `level4/closure_proofs/p7_statistical_consequences/src/rebaseguard_p7/chain.py` | imported and cross-checked |
| `GammaTilde_{D,m}`, `rho_c(D,m)` | `.../m_rho_stability_priority3/results/boundary_table.json` | read as landmarks only |

P5 adds **no** new detector, threshold, calibration or convention.

## 2. Cycle semantics, item by item

Let `j = 0, 1, 2, ...` index re-baselining cycles and let `e_j` be the
**reference error entering cycle `j`** (`e_start[:, j]` in the frozen chain).

1. **Detector reset.** At the start of every cycle both arms are set to zero
   (`plus=minus=0`), the reuse buffer is cleared, and the within-cycle clock is
   reset (`t=0`). There is no head start and no minimum dwell.
2. **Innovation.** At within-cycle step `t >= 1` the simulator draws
   `raw_t ~ N(0,1)` iid and feeds the detector
   ```
   z_t = raw_t - e_j .
   ```
   `raw_t` is the *fresh observation*; `e_j` is a deterministic offset held
   fixed for the whole cycle. **`raw_t` does not depend on `e_j` in any way.**
   This is literally the line `z = rng.standard_normal(idx.size) - e[idx]`.
3. **Sign convention.** A reference that is too high by `e` makes the
   detector see mean `-e`. A genuine process shift `+Delta` is entered in the
   frozen code as `e <- e - Delta`, i.e. shift and reference error are the same
   coordinate with opposite sign. P5 works throughout at `Delta = 0`.
4. **Stopping time.** `tau_j = inf{t >= 1 : alarm after the update at step t}`,
   two-sided, inclusive post-update test, no truncation. `tau_j >= 1` always.
5. **Terminal increment included.** The alarm-causing step `t = tau_j` is part
   of the cycle and part of the reuse window.
6. **Reuse window.** `w_j = min(m, tau_j)` — Stage-D convention A: the window
   is *truncated*, and the *denominator is the truncated length `w_j`*, not `m`.
   `w_j` is therefore a random denominator, and `w_j < m` exactly when
   `tau_j < m`.
7. **Reused estimate.** `zbar_j = (1/w_j) * sum_{r=0}^{w_j-1} z_{tau_j - r}`.
8. **Fresh contribution.** `fresh_j ~ N(0, 1/m)`, drawn *after* the alarm and
   independent of everything in cycle `j`. It is the reference-noise term: a
   fresh baseline of `m` observations has mean variance `1/m`.
9. **Reference update.**
   ```
   e_{j+1} = rho * (e_j + zbar_j) + (1 - rho) * fresh_j ,     rho in [0,1].
   ```
10. **Independence across cycles.** Given `e_j`, cycle `j` uses only fresh
    randomness; `(e_j)` is a time-homogeneous Markov chain on `R`.

## 3. The recursion as written

```
e_{j+1} = rho * ( e_j + (1/w_j) sum_{r<w_j} z_{tau_j - r} ) + (1-rho) * fresh_j
```

with `z_t = raw_t - e_j`, `w_j = min(m, tau_j)`, `fresh_j ~ N(0,1/m)`.

## 4. The raw-mean identity  (the single most important line in P5)

Because `e_j` is constant over the cycle and every window term carries exactly
one `-e_j`,

```
e_j + zbar_j = e_j + (1/w_j) sum_{r<w_j} ( raw_{tau_j-r} - e_j )
             = e_j + (1/w_j) sum_{r<w_j} raw_{tau_j-r}  -  e_j
             = (1/w_j) sum_{r<w_j} raw_{tau_j-r}
             =: Rbar_j .
```

**The `e_j` term cancels identically.** Hence

> **(AUDIT-1) Raw-mean form of the frozen recursion.**
> ```
> e_{j+1} = rho * Rbar_j + (1 - rho) * fresh_j ,
> Rbar_j  = (1/w_j) sum_{r=0}^{w_j-1} raw_{tau_j - r} ,   w_j = min(m, tau_j).
> ```
> `Rbar_j` is the arithmetic mean of **at most `m` standard normal draws**.
> The entering reference error `e_j` enters the next state *only* through the
> selection channel: which draws land in the terminal window, i.e. through the
> joint law of `(tau_j, raw_{tau_j}, ..., raw_{tau_j-w_j+1})` given `e_j`.

This is an algebraic identity, not an approximation, and it holds for every
detector, every `m >= 1`, every `rho in [0,1]` and every `e_j`.

**Numerical confirmation.** `src/rebaseguard_p5/chain.py` re-implements the
frozen chain with the buffer holding `raw_t` and the update written as
`rho*Rbar + (1-rho)*fresh`, consuming the RNG in exactly the frozen order.
Against `rebaseguard_p7.chain.simulate_chain` over 12 configurations
(`det in {cusum, sr}` x `m in {1,3,5}` x `rho in {0.5,1.0}`), 200 replicates,
60 cycles each: **`tau` arrays bit-identical in all 12**, and
`max |e_start difference| = 8.9e-16` (a few ULP of the reordered
floating-point sum). See `results/correspondence.json`.

## 5. Separation of deterministic mean and stochastic innovation

Define, for the frozen `(D, m)`,

```
R_{D,m}(e) := E[ Rbar | e_j = e ] ,      S_{D,m}(e) := Var( Rbar | e_j = e ),
A_{D,m}(e) := E[ tau  | e_j = e ]   (the P7 response function).
```

`fresh_j` has mean `0` and variance `1/m` and is independent of `Rbar_j`, so
**exactly**

```
M_{D,m,rho}(e) := E[e_{j+1} | e_j = e] = rho * R_{D,m}(e) ,
V_{D,m,rho}(e) := Var(e_{j+1} | e_j = e) = rho^2 S_{D,m}(e) + (1-rho)^2 / m .
```

> **(AUDIT-2) rho-factorisation.** The entire reuse-fraction dependence of the
> conditional-mean map is a *multiplicative scalar*. The deterministic skeleton
> family is the one-parameter scaling family `e -> rho * R(e)` of a single
> fixed, detector- and window-specific function `R`.

The stochastic innovation about the mean is
`eta_j = rho (Rbar_j - R(e_j)) + (1-rho) fresh_j`, a martingale difference with
conditional variance `V_{D,m,rho}(e_j)`. It is **not** Gaussian and **not**
homoscedastic; `S(e)` is measured, not assumed.

## 6. Consistency with the closed P1/P2/P3 statements

P1/P2 give `F'_{rho,m}(0) = rho (1 - GammaTilde_{D,m})` with
`GammaTilde_{D,m} = E_0[A_m T_tau]`. Under AUDIT-2 that is the same as

```
R'_{D,m}(0) = 1 - GammaTilde_{D,m} .
```

P5 re-measures `R'(0)` from the map grid and checks it against the frozen P3
`boundary_table.json` (`NUMERICAL_CORRESPONDENCE.md` §2). P3's

```
lambda_{D,m}(rho) = rho (1 - GammaTilde_{D,m}),   rho_c = 1/|1 - GammaTilde|
```

is therefore recovered inside P5 as the *linearisation at `0` of the fixed
function `R` scaled by `rho`* — which is exactly what makes the one-parameter
family amenable to standard one-parameter bifurcation analysis (`THEOREM.md`).

## 7. Symmetry

Both frozen detectors are two-sided and sign-symmetric (both arms use the same
`k`/`A`, both are reset to the same value, the test is the same). Replacing
`raw_t -> -raw_t` and `e -> -e` maps the plus arm to the minus arm and leaves
`tau` invariant while negating `Rbar`. Hence

```
R(-e) = -R(e),      S(-e) = S(e),      A(-e) = A(e)          (AUDIT-3)
```

as exact distributional statements. P5 does **not** impose this symmetry on the
estimates; it is used as an independent falsification test
(`ADVERSARIAL_REVIEW.md` A5).

## 8. What the audit fixes for the rest of P5

* the state is `e_j`, the entering reference error, in reference-error units;
* `rho in [0,1]`, `m in {1,2,3,5}` (the windows P3 supports), `Delta = 0`;
* the conditional-mean map is `rho R(e)`, the conditional variance is
  `rho^2 S(e) + (1-rho)^2/m`;
* the deterministic skeleton is `e_{j+1} = rho R(e_j)`;
* `rho_c(D,m) = 1/|R'(0)|` is a landmark of `R`, imported from P3, never
  re-derived.
