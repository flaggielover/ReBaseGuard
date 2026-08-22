# ReBaseGuard Level 4 — Gates 4.1 and 4.2

**Everything in this directory is a non-rigorous Monte Carlo diagnostic.**
Nothing here is proof evidence, and nothing here modifies, reinterprets or
supersedes any frozen Level 1–3 artifact. The frozen model
([`closure/01_FROZEN_MODEL.md`](../closure/01_FROZEN_MODEL.md)) is treated as
immutable scientific ground truth and is only ever *checked against*.

## What this is

A reproducible **Multi-Cycle Experimental Oracle** for the frozen two-sided
CUSUM (`k = 1/2`, `h = 5`), built to determine whether the proposed
nonlinear/period-2 mechanism is actually present — not to confirm it.

| Stage | Gate | Deliverable | Report |
|---|---|---|---|
| A | 4.1 | repeated-cycle simulator, re-baselining policies, metrics, replicate-level inference | [`reports/GATE_4_1_REPORT.md`](reports/GATE_4_1_REPORT.md) |
| A | 4.2 | conditional map estimator `F_rho(e) = E[E_{j+1} | E_j = e]` | [`reports/GATE_4_2_REPORT.md`](reports/GATE_4_2_REPORT.md) |
| A | — | scientific result ledger | [`reports/LEDGER.md`](reports/LEDGER.md) |
| **B** | — | **rigorous period-2 certificate at `rho = 1`** | [`reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md`](reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md) |
| B | — | Stage B ledger (Stage A untouched) | [`reports/STAGE_B_LEDGER.md`](reports/STAGE_B_LEDGER.md) |
| **C** | — | **stability-aware reuse policy and the reuse-performance tradeoff** | [`reports/STAGE_C_METHOD_REPORT.md`](reports/STAGE_C_METHOD_REPORT.md) |
| C | — | Stage C ledger (Stage A/B untouched) | [`reports/STAGE_C_LEDGER.md`](reports/STAGE_C_LEDGER.md) |
| **C.1** | — | **confirmatory sensitivity evaluation** | [`reports/STAGE_C1_CONFIRMATORY_REPORT.md`](reports/STAGE_C1_CONFIRMATORY_REPORT.md) |
| C.1 | — | Stage C.1 ledger (Stage C untouched) | [`reports/STAGE_C1_LEDGER.md`](reports/STAGE_C1_LEDGER.md) |

Stage A is Monte Carlo and is labelled as such throughout. **Stage B**
([`stage_b/`](stage_b/)) upgrades the `rho = 1` period-2 result from
`CANDIDATE` to `RIGOROUS-CERTIFIED` using validated numerics in which every
approximation between the true continuous-state map and the computed object is
explicitly bounded. Its entry point is [`stage_b/README.md`](stage_b/README.md).

**Stage C** ([`stage_c/`](stage_c/)) turns the certified boundary into a
monitoring policy and measures what it costs. Decision:
`STAGE-C-PARTIAL` — one pre-specified criterion failed and was left failed.
Its entry point is [`stage_c/README.md`](stage_c/README.md).

**Stage C.1** ([`stage_c1/`](stage_c1/)) is a *separate* confirmatory
experiment, not a revision of Stage C. Stage C's criterion C6 failed and
stays failed; Stage C.1 preregistered a baseline-normalised sensitivity
metric, froze it before generating data, used entirely new seeds, and
reached `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`.

## Layout

```text
level4/
  src/rebaseguard_level4/   the package
    frozen.py               exact restatement of the frozen CUSUM semantics
    streams.py              deterministic, per-replicate recoverable RNG
    multicycle.py           GATE 4.1 repeated-cycle simulator
    conditional.py          GATE 4.2 conditional map + score/LR cross-checks
    metrics.py              metrics and replicate-level bootstrap inference
    analysis.py             derivatives, symmetry, H_rho roots, candidates
    reference.py            slow scalar reference implementations (tests only)
    campaigns.py            staged experiment campaigns
    provenance.py           run manifests
    storage.py              Parquet / JSON / CSV persistence
    figures.py              publication figures
    ledger.py               result ledger with status discipline
  configs/                  one JSON per stage (smoke / pilot / full)
  experiments/              drivers: run_gate41, run_gate42, make_figures, make_reports
  results/raw/              cycle-level Parquet (gitignored — regenerable)
  results/processed/        manifests, summaries, findings, ledger (tracked)
  figures/                  generated figures + figure_index.json (tracked)
  reports/                  the two gate reports and the ledger (tracked)
  tests/                    the Level 4 test suite
```

## Environment

Level 4 uses **its own virtual environment** so that the frozen
`rebaseguard-proof` environment is never mutated. NumPy and SciPy are pinned to
the same versions the certificate was produced with.

```bash
python3 -m venv level4/.venv
level4/.venv/bin/python -m pip install "numpy==2.5.2" "scipy==1.18.0" "pytest==9.1.1" "pyarrow==25.0.1" "matplotlib==3.11.1"
```

The frozen package is put on `sys.path` for the tests rather than installed, so
running the Level 4 suite cannot write to any frozen artifact.

## Reproducing

```bash
level4/.venv/bin/python -m pytest level4/tests -q
```

```bash
bash scripts/verify_level_4.sh
```

```bash
bash level4/stage_b/reproduce.sh
```

```bash
bash level4/stage_c/reproduce.sh
```

```bash
bash level4/stage_c1/reproduce.sh
```

Staged campaigns, cheapest first — never run the expensive stage before the
cheap one has passed:

```bash
level4/.venv/bin/python level4/experiments/run_gate41.py level4/configs/gate41_smoke.json
```

```bash
level4/.venv/bin/python level4/experiments/run_gate42.py level4/configs/gate42_full.json
```

Then regenerate every figure and report from the saved results:

```bash
level4/.venv/bin/python level4/experiments/make_figures.py <gate41-campaign-dir> <gate42-findings.json>
```

## Conventions this code implements

All are traced to the repository, not invented here. See the module docstring of
[`src/rebaseguard_level4/frozen.py`](src/rebaseguard_level4/frozen.py) for the
source line of each.

| Item | Convention |
|---|---|
| detector | `S±_t = max(0, S±_{t-1} ± Z_t − k)`, shared innovation `Z_t` |
| constants | `k = 1/2`, `h = 5`, exact |
| alarm | `max(S⁺,S⁻) ≥ h`, inclusive, tested **after** the update |
| `τ` | starts at `t = 1`; `T_τ` includes the terminal increment |
| tie | plus arm has priority (unreachable in practice; recorded, not assumed) |
| reference | `Z_t = X_t − e`, `X_t ~ N(0,1)` physical |
| reuse statistic | `μ̂ = (1/m) Σ_{r=0}^{m−1} X_{τ−r}`, alarm observation included |
| `m ≥ 2` | minimum dwell `τ_m = inf{t ≥ m : …}` |
| fresh statistic | `μ̂_fresh = (1/m) Σ Y_r`, independent of the stopping event |
| re-baselining | `E_{j+1} = ρ·μ̂_reuse + (1−ρ)·μ̂_fresh` |

## Discipline

* **The replicate is the statistical unit** in Gate 4.1; the path is the unit in
  Gate 4.2. Both are stated in every summary file.
* **Every aggregate has recoverable seeds.** Replicate `r` can be re-simulated
  alone and reproduces bit-for-bit.
* **Raw data is not committed.** It is regenerable from the tracked manifest,
  config and seed rule.
* **No figure is edited by hand.**
* **`NEW-NUMERICAL` never becomes theorem language.** `ledger.py` refuses proof
  vocabulary on any status below `FROZEN-*`.

---

## Stage D — generalisation (Monte Carlo)

**`STAGE-D-PARTIAL`** — [`stage_d/README.md`](stage_d/README.md) ·
[`reports/STAGE_D_REPORT.md`](reports/STAGE_D_REPORT.md) ·
[`reports/STAGE_D_LEDGER.md`](reports/STAGE_D_LEDGER.md)

Tests whether the `m = 1` mechanism survives a second detector, longer stopped
windows, and non-Gaussian innovations. D1 passes; D2 finds a tightly bracketed
crossing `m* in [50, 75]` but D2.3 **fails**; D2.5 finds the crossing has **no
operational counterpart**; D3 gives numerical robustness over six families with
`t3` **ambiguous**. Adversarial suite 12/12.

```bash
bash level4/stage_d/reproduce.sh
```

