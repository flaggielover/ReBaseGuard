# P6 evaluation protocol

What the full campaign will measure, on what cells, with what units, and — the
part `S8` forces — over how many cycles.

---

## 1. Design cells

| axis | values | rationale |
|---|---|---|
| detector `D` | `CUSUM(k=1/2, h=5)`, `SR(A=520.886133602749)` | frozen, ARL-matched (`D7`). Both are mandatory: reproduction across detectors is a closure criterion (`PREREGISTRATION_OPTIONS.md` C4) |
| window `m` | `{1, 2, 3, 5}` core; `{8}` exploratory | `{1,2,3,5}` is the range P3/P7 support (`L4`, `S14`). `m=8` is outside P3's boundary table and any `rho_c` annotation there must be omitted, not extrapolated |
| reuse `rho` (baselines) | `{0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75, 1.0}` | must resolve `[0.10, 0.35]` (`E2`, `S12`) and must include `0` and `1` as the two named controls |
| fresh count `k` | `{m, 2m, 4m}` | tests `H4` |
| shift `Delta` | `{0, 0.5, 1.0, 2.0}` | `0` for in-control; `1.0` is P7's headline (`S5`, `S9`); `0.5` probes the blind-spot region; `2.0` checks that gains do not reverse for large shifts |
| shift onset | injected at a **post-burn-in** cycle, and separately at cycle `1` | the second is the finite-cycle regime of `S8` |

`m = 1` is retained even though `S14` calls it unusable, because P7's numbers
are worst there and a mitigation that cannot help the worst case is worth
knowing about.

## 2. In-control measurements (`Delta = 0`)

Per cell, per policy, per replicate:

| metric | id | note |
|---|---|---|
| in-control ARL | `Arl0` | primary in-control coordinate; comparable to `S3`/`S4` |
| `FAP(H)`, `H = 100` | `Fap100` | comparable to `S7` |
| alarm rate per 1000 obs | `Rate` | reporting form |
| reference RMS | `Rms` | Tier 3 (`P7` is provisional; P6 measures it, never imports it) |
| reference tail | `Tail(0.2)`, `Tail(0.5)`, `OutCal(beta)` | `c_beta` re-derived from `p7/results/response_curves.json` |
| mean algebraic reuse / sample reuse fraction | `Wbar`, `FracReuse` | |
| fresh & downtime cost | `Fresh`, `Down` | |

## 3. Out-of-control measurements (`Delta > 0`)

| metric | id | note |
|---|---|---|
| mean delay | `Dmean` | `S5` |
| median delay | `Dmed` | **mandatory alongside `Dmean`** — at CUSUM `m=1, rho=1` the median is *better* than nominal while the mean is 5x worse (`S9`) |
| `q95` delay | `Dq95` | |
| `P(delay > L)`, `L in {50, 100}` | `Dtail50`, `Dtail100` | the primary objective candidate `O1` |
| discrimination ratio | `Rdelta` | `S6`; `>= 1` is the pathological regime |
| blind-spot mass (diagnostic) | `P(|e - Delta| < 0.2)` | latent; **diagnostic class only** |

## 4. Efficiency measurements

`Reuse`, `Fresh`, `FracReuse`, `Down`, `Eff` per
`SAFETY_OBJECTIVES.md` §3.3, plus the reference-update wall-clock cost for any
policy that carries a filter or a table lookup (Family B/E/F) — a policy whose
per-alarm cost is a table lookup and a scalar update is deployable; one that
needs an optimisation per alarm needs saying so.

## 5. Dynamic behaviour — the non-negotiable part

`S8` is the reason this section exists: the cycle immediately after the first
re-baselining collapses by `98%` under full reuse. **A method validated on one
cycle is not validated.**

Every serious P6 method is measured in four regimes:

| regime | definition | what it catches |
|---|---|---|
| **R1 cycle 1** | from `e_0 = 0`, first cycle only | the regime that looks fine and hides everything (`S8`) |
| **R2 cycle 2** | the cycle immediately after the first re-baselining | the collapse itself; `Coll = E[tau_2]/E[tau_1]` |
| **R3 finite-cycle** | cycles `1..50` from `e_0 = 0`, no burn-in, curves reported per cycle | transients, slow drifts, and any feedback instability a state-dependent policy introduces (`H7`) |
| **R4 burn-in / long-run** | cycles after a preregistered burn-in, run long | the operating regime |

**Burn-in.** P7 used 12 cycles on empirical mixing evidence of ~3 cycles (`E4`).
P6 inherits `12` as the *default for fixed-`rho` baselines only*. For any
state-dependent policy the burn-in must be **re-established empirically per
policy** from the R3 curves, because `H7` removes the licence to assume the
closed-loop chain mixes as fast as the open-loop one. A policy whose R3 curve
has not flattened by cycle 50 is reported as such and its R4 numbers are
labelled provisional.

**A preregistered non-negotiable:** no P6 claim may be based on R1 or R4 alone.
Every headline table carries the R2/R3 columns beside it.

**Open decision (entry gate).** R1–R3 as specified fix `e_0 = 0`, which is P7's
finite-cycle convention. A policy using the history channel cannot legally run
there (`OBSERVABILITY_AUDIT.md` §4a), so either R1–R3 gain an `e_0 ~ N(0,1/m_0)`
variant for such policies, or history-using policies are reported in R4 only —
with the missing finite-cycle evidence stated explicitly. The first option is
preferred; it costs an extra arm, not an extra design.

## 6. Statistical unit and comparison

* **Unit:** the independent replicate `r`. Never the cycle — cycles within a
  replicate are autocorrelated (`STATISTICAL_DESIGN.md` §4).
* **Comparisons are paired by seed.** Policy `U` and policy `U'` are run with
  the same replicate seeds; the analysis is on the per-replicate differences.
* **Every effect is reported with an interval**, and the verdict labels are
  P7's, reused verbatim so the two campaigns read together:
  `INCONCLUSIVE` / `STATISTICALLY_RESOLVED` / `PRACTICALLY_MATERIAL`.
* Details, including the honest limits of common random numbers in this chain,
  are in `STATISTICAL_DESIGN.md`.

## 7. Correspondence requirements (run before any science)

| # | check | assertion |
|---|---|---|
| X1 | constant-policy correspondence | a `(rho, m)`-constant P6 policy reproduces `rebaseguard_p7.chain.simulate_chain` with **bit-identical `tau`** and `max |e_start difference| < 1e-13` |
| X2 | convention A | `w_j = min(m_j, tau_j)` with truncated denominator; a fixed-`m` denominator variant must *fail* an assertion (`X4`, `P15`) |
| X3 | P7 reproduction | `B0`, `B2` at `rho in {0.25, 0.5, 0.75, 1}` and `B3` reproduce P7's `consequences.json` `Arl0` to within the reported bootstrap intervals, in all 8 families |
| X4 | detector identity | the CUSUM step is the imported frozen `cusum_update`; the SR step is the verbatim Stage-D recursion |
| X5 | observability | `tests/test_observability.py` passes (`OBSERVABILITY_AUDIT.md` §7) |

X3 is the one that would catch a silent semantic drift. It must run at full
precision on the evaluation seed family before any policy result is believed.

## 8. Reporting format

Every results row carries: `detector, m, policy_id, policy_class,
policy_params, seed_family, n_rep, n_cycles, burn_in, regime, Delta, metric,
estimate, interval, verdict`. `policy_class` is mandatory so that no table can
present an oracle as a recommendation (`OBSERVABILITY_AUDIT.md` §7.4).

Figures must plot the oracle ceiling (`Z5` at minimum) and the matched-cost
fixed-`rho` baseline `B2*` on the same axes as any proposed method. A figure
showing a method beating only `B3` is not acceptable.
