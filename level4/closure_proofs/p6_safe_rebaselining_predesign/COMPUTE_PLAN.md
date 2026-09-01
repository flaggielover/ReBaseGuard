# P6 adaptive compute plan

The dominant cost in this campaign is not the number of policies; it is the
number of *tail events*. Everything below follows from that.

**Cost model.** One simulated cycle costs `~E[tau]` vectorised detector steps.
In-control cells run at `Arl0 ~ 50..180` steps/cycle; shifted cells at
`~10..70`. A replicate of `200` cycles is therefore `~10^4` steps, and the
vectorised chain does `n_rep` replicates in lockstep, so a cell of
`n_rep = 500, n_cycles = 200` is `~10^7` scalar detector updates — seconds, not
hours. **The campaign is cheap until the tail metrics appear**, at which point
`STATISTICAL_DESIGN.md` §5 demands `~10^4` shifted cycles *per arm*, and the arm
count is `policies x detectors x m x Delta`.

---

## 1. Five stages

| stage | purpose | cells | arms | scale per arm | early stop |
|---|---|---|---|---|---|
| **P0 pilot** | measure the `cv`s that `STATISTICAL_DESIGN.md` §7 assumes; check X1–X5 correspondence; verify the harness | 1 detector, `m = 3`, 3 policies | ~5 | `n_rep = 200`, `n_cycles = 100` | n/a |
| **P1 screen** | eliminate dominated policies cheaply, on **in-control + reference** metrics only | both detectors, `m in {1,3,5}`, all baselines + all family variants | `~60..120` | `n_rep = 100`, `n_cycles = 100`, `Delta = 0` | §3 |
| **P2 shortlist** | resolve the survivors on the **full** metric set including one `Delta` | both detectors, `m in {1,3,5}`, `Delta in {0, 1}` | `~15..25` | `n_rep = 500`, `n_cycles = 200` | §3 |
| **P3 confirm** | the preregistered primary objective at full tail precision, plus R1–R4 regimes | both detectors, `m in {1,2,3,5}`, `Delta in {0, 0.5, 1, 2}` | `~6..10` | tail-event rule (`~10^4` shifted cycles/arm) | none |
| **P4 replay** | independent reproduction on the `REPLAY` seed family | the confirmed set only | `~3..5` | as P3 | none |

Tuning and hyperparameter fitting happen **only** in P1/P2 and **only** on the
`TUNE` seed family. P3 and P4 run frozen parameters (`I5`).

## 2. Why screening on a surrogate is legitimate here

`STATISTICAL_DESIGN.md` §7 shows reference metrics need `n_rep` in the single
digits where tail metrics need `10^4` events. Screening on `Rms`/`OutCal` is
therefore `10^2`–`10^3` times cheaper than screening on `Dtail`.

The legitimacy condition is narrow and must be stated: **screening may only
eliminate, never select.** A policy dropped at P1 is dropped because it fails a
*necessary* condition (it does not even reduce reference dispersion, or it
violates a Tier-1 constraint); a policy that survives P1 has proved nothing.
`S18`/`X6` forbid concluding a monitoring gain from a reference-metric gain, and
that prohibition applies to the screen exactly as it applies to the conclusion.

Corollary: the screen must be **one-sided and generous**. A policy is dropped
only if it is worse than the matched-cost fixed-`rho` baseline with the paired
interval excluding zero — never on a point estimate.

## 3. Early-stop rules for dominated candidates

Applied at P1 and P2, on the `TUNE` family, checked after each block of
replicates:

| rule | condition | action |
|---|---|---|
| `ES1` **constraint violation** | a Tier-1 hard constraint (`K1`/`K4`) is violated with the paired interval excluding zero | drop |
| `ES2` **strict domination** | some already-evaluated policy is better on *every* screening coordinate, each difference resolved | drop |
| `ES3` **cost degeneracy** | `Fresh(U) >= Fresh(B0) - epsilon`, i.e. the policy has quietly become fresh-only | drop, and record it — this is failure mode `F3` and it must be reported, not silently pruned |
| `ES4` **no-effect** | the paired difference against the matched-cost baseline is inside the materiality band with a CI narrow enough to exclude a material effect | drop as `RESOLVED_NULL` (**not** `INCONCLUSIVE`) |
| `ES5` **instability** | the R3 finite-cycle curve has not flattened by cycle 50, or diverges | drop, and report as an `H7` instance |

Two disciplines attach to these rules:

* **Every drop is recorded with its reason and its numbers.** A screening stage
  that discards a policy silently is indistinguishable from a screening stage
  that discards an inconvenient one. The dropped-policy table is part of the
  campaign output.
* **`ES4` produces a scientific result, not a non-result.** "State-dependent
  reuse does not beat the best fixed `rho` at matched cost" would be a complete
  and valuable P6 outcome, and the compute plan must be able to reach it without
  the campaign feeling obliged to keep searching.

## 4. Budget shape

Indicative shares of total compute, to be re-derived after P0:

```
P0 pilot        ~2%
P1 screen       ~8%     (many arms, tiny each)
P2 shortlist   ~20%
P3 confirm     ~50%     (tail events dominate)
P4 replay      ~20%
```

Half the budget goes to the final few arms. That is the correct shape for a
prescriptive campaign and the opposite of the "sweep everything at full
precision" shape, which would spend most of its compute resolving policies that
`ES1`–`ES3` can eliminate for free.

## 5. Where the tail budget actually goes

`Dtail(L)` at a target of `0.02` needs `~10^4` shifted cycles per arm
(`STATISTICAL_DESIGN.md` §5). At `~30` steps per shifted cycle that is `~3x10^5`
detector steps per arm — still cheap. **The expense is the arm count**, i.e.
`policies x 2 detectors x 4 windows x 4 shifts = 32` runs per policy at P3. This
is why P3 admits at most `~10` policies, and why the shortlist stage exists.

Two levers, in preference order:
1. **Reduce arms.** Freeze `Delta` to `{0, 1}` for the primary and report the
   other shifts as secondary. Preregister which.
2. **Substitute `Dq95` for `Dtail`** as the primary (declared in advance,
   `STATISTICAL_DESIGN.md` §5). A quantile needs far fewer events.

Raising `n_rep` is the last resort, not the first.

## 6. Resource discipline for the campaign itself

* No repository-wide verification runs. Correspondence checks are scoped to the
  P6 namespace plus the read-only imports it names.
* No re-running of P5 or P7 experiments. Their artifacts are read as data.
* Long runs execute in the background and are collected once, not polled.
* Every stage writes a machine-readable result file before the next stage
  starts, so an interrupted campaign resumes rather than restarts.
* Figures are generated from result files, never from live simulation.
