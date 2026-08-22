# ReBaseGuard Level 4 — Stage C

**Stability-aware reuse, monitoring consequences, and the reuse–performance
tradeoff.**

Stage A established the phenomenon by Monte Carlo. Stage B certified, rigorously,
a locally attracting period-2 orbit of the **deterministic** conditional-mean map
at `rho = 1`. Stage C asks the method question: can the certified *local
stability boundary* be used to control reuse?

| Entry point | Contents |
|---|---|
| [`STAGE_C_PROTOCOL.md`](STAGE_C_PROTOCOL.md) | the protocol, **frozen before the campaign** (sha256 in the report) |
| [`../reports/STAGE_C_METHOD_REPORT.md`](../reports/STAGE_C_METHOD_REPORT.md) | the report and the decision |
| [`../reports/STAGE_C_LEDGER.md`](../reports/STAGE_C_LEDGER.md) | Stage C ledger (Stage A/B untouched) |
| [`src/policy.py`](src/policy.py) | the ReBaseGuard policy definition |

```bash
bash level4/stage_c/reproduce.sh          # full
bash level4/stage_c/reproduce.sh --quick  # reduced, exercises every path
```

## The policy

Require `|F'_rho(0)| <= 1 - delta`. Level 2C proves `F'_rho(0) = rho(1 - Gamma)`,
so

```text
rho_safe(delta) = clip( (1 - delta) / (Gamma - 1), 0, 1 )
```

Two variants, and the difference is the whole point:

* **POINT** uses the Monte Carlo estimate of `Gamma`. Heuristic. At the certified
  upper end of `Gamma` its reuse fraction would sit on the *unstable* side of the
  boundary, so calling it certified would be false.
* **CONSERVATIVE** uses the upper end of the frozen certified `Gamma` enclosure.
  Since `rho(Gamma-1)` increases in `Gamma`, the guarantee then holds for the
  **true** `Gamma` — but it is a guarantee about *local linear stability of the
  deterministic map*, and nothing more.

The policy is a pure function of `Gamma` and `delta`. It cannot see any Stage B
or Stage C outcome, and a test enforces that by scanning the module for outcome
values and identifiers.

## What Stage C does not claim

* **Nothing about the noisy recursion.** Stage B's theorem is about the
  deterministic map `F_1`, not `E_{j+1} = F_1(E_j) + noise`. Stage C does not
  upgrade it. Stationary shapes here are empirical descriptions; there is no
  bimodality, ergodicity or stochastic period-2 claim.
* **Not optimality.** The policy is not the best-performing `rho`, and the
  protocol said so in advance (§12). It buys a certified guarantee, not
  performance.
* **Not a sample-count saving at `m = 1`.** The protocol always draws one fresh
  variate and weights it by `1-rho`, so the fresh-sample *count* is a step
  function of `rho`. The efficiency gain is in reference *weight*.

## Layout

```text
level4/stage_c/
  STAGE_C_PROTOCOL.md      frozen before the campaign
  src/
    policy.py              the ReBaseGuard policy (outcome-blind by test)
    detection.py           post-change simulator; reproduces Stage A bit-for-bit at Delta=0
    arl_curve.py           A(e) = E[tau | E_j = e]
    campaign.py            resumable, per-cell checkpointed runner
    analyze.py             paired inference, Pareto, regime labels
    figures_c.py           the nine figures
    run_arl_curve.py / run_incontrol.py / run_detection.py
    adversarial_c.py / run_analysis.py / make_report_c.py
  tests/                   policy, detection, infrastructure
  results/cells/           per-cell checkpoints, keyed by config hash
  results/                 campaign summaries, findings, ledger
  figures/                 nine figures + index
  reproduce.sh
```

All in-control work uses the **frozen Stage A simulator** directly; Stage C adds
no detector code to that path. The only new simulator is for post-change shifts,
and it reproduces Stage A bit-for-bit when the shift is zero.
