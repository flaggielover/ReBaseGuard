# Level-4 Priority 5 — Nonlinear reference-state dynamics

```text
SCIENTIFIC_VERDICT             = PARTIAL
REPOSITORY_INTEGRATION_VERDICT = APPROVED_PARTIAL_CHECKPOINT
PROTECTED_TREE                 = IDENTICAL (294 files)
FOCUSED_TESTS                  = 44 passed, 1 failed (literal G20 worktree scope)
```

P5 asks what nonlinear stochastic mechanism converts the **local repulsion**
proved by P1–P3 (`lambda = rho(1 - GammaTilde)`, `|lambda| > 1` for
`rho > rho_c ~ 0.06–0.11`) into the **bounded, high-dispersion, operationally
costly** long-run behaviour measured by P7.

## The answer in one page

**1. An exact algebraic identity collapses the recursion.** The frozen
Stage-D update `e_{j+1} = rho(e_j + zbar_m) + (1-rho) fresh` is *identically*

```
e_{j+1} = rho * Rbar_j + (1-rho) * fresh_j ,
Rbar_j  = mean of the last w_j = min(m, tau_j) RAW N(0,1) observations.
```

The entering error cancels. `e_j` influences the future **only** by selecting
which observations end up in the terminal reuse window. (`THEOREM.md` T1;
verified bit-for-bit against the frozen P7 chain.)

**2. Consequently the reference error can never run away.** The next state is an
average of at most `m` standard normals plus `N(0,1/m)`. A Jensen + Wald
argument gives a *state-independent* bound on every moment, and a
`tau = 1` minorisation plus a Chebyshev return bound gives a two-step Doeblin
condition on the whole line. Hence, for **both frozen detectors, every `m`, and
every `rho in [0,1]` including full reuse**: a unique invariant law, uniform
geometric ergodicity, and finite moments of every order. This closes all five
stationary-law gaps that P7 left as evidenced-but-unproved. (T4–T7.)

**3. The whole `rho`-dependence of the mean map is a scalar.**
`E[e_{j+1}|e] = rho * R(e)` for one fixed odd function `R` per `(D,m)`. `R` has
slope `1 - GammaTilde` at `0` (recovered to 0.14%–1.6% of the frozen P3 value by
an independent estimator), saturates at `|R| <= 1.59`, and **decays to zero**:
beyond `|e| ~ 8` the measured cycle almost always ends on its first observation,
and the one-step law approaches `N(0, rho^2 + (1-rho)^2/m)`. Local repulsion
and global boundedness are the same selection channel at two ends of its range.
(`NONLINEAR_MAP.md`.)

**4. The measured deterministic skeleton supports a flip interpretation, with
important proof limits.**
Because the family is `rho R`, symmetric 2-cycles are *exactly* the solutions of
`s(e) = 1/rho` with `s(e) = -R(e)/e`. Under measured H2/H3 assumptions, a
continuous symmetric period-2 branch emerges at `rho_c`. A from-scratch scan of
the measured PCHIP map finds only periods 1 and 2 and an attracting branch on
its finite grid. Attraction, absence of asymmetric cycles, and the full
supercritical-flip classification are numerical evidence rather than theorems.
Conditional on the branch, `SNR -> 0` as `rho -> rho_c+`; this is consistent
with P7's negative operational result but does not prove that every stochastic
statistic must be featureless there. (T9, T10.)

**5. P7's effective gain is identified exactly.** `ACF1 = rho(1 - Gamma_eff)` is
an identity with `Gamma_eff = 1 + E_pi[e^2 s(e)]/E_pi[e^2]` — the `e^2`-weighted
stationary average of the secant gain, not the tangent gain `GammaTilde` at
`0`. That is why P7 measured a 5x–25x overshoot of `lambda` over `ACF1`. (T11.)

## Independent verdict

`INDEPENDENT_ADJUDICATION.md` is authoritative for the final P5 status. It
preserves T1 and T7, resolves the T11 numerical discrepancy, narrows the
deterministic claims, and audits all 20 frozen closure gates. P5 is `PARTIAL`
because several universal numerical gates are not literally proved and G20's
worktree-scope criterion is false in the known README/P6 worktree.

## Artifacts

| file | contents |
|---|---|
| `DEFINITION_AUDIT.md` | frozen conventions, the raw-mean identity, correspondence evidence |
| `THEOREM.md` | T1–T12 with explicit tiers |
| `PROOF.md` | full proofs |
| `NONLINEAR_MAP.md` | the measured map `R`, `S`, `A`, hypothesis audit, skeleton scan |
| `STATIONARY_DYNAMICS.md` | dispersion law, ergodicity evidence, mode structure, stress tests |
| `NUMERICAL_CORRESPONDENCE.md` | P1/P2/P3/P7 cross-checks |
| `ADVERSARIAL_REVIEW.md` | attacks, including the ones that changed the campaign |
| `LIMITATIONS.md` | what P5 does not establish |
| `P6_HANDOFF.md` | what a controller should regulate |
| `CODEX_HANDOFF.md` | independent adjudication package |
| `CLOSURE_REPORT.md` | closure gates |
| `INDEPENDENT_ADJUDICATION.md` | final verdict and authoritative claim scoping |

## Reproduction

```bash
bash level4/closure_proofs/p5_nonlinear_dynamics/reproduce.sh
```

Seed families `20260501` (primary) and `20261119` (independent replication).
No `hash(str)` anywhere; all child streams come from
`np.random.SeedSequence([family, detector_code, tag, index])`.

## Scope

P5 stays inside the frozen Gaussian CUSUM/SR core (`Delta = 0`,
`rho in [0,1]`, `m in {1,2,3,5}`). Robustness across distributions and
detectors is P8. Controller design is P6. P5 modifies no frozen artifact.
