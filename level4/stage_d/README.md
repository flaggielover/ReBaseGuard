# Stage D — generalisation of stopped-selection reference reuse

**Decision: `STAGE-D-PARTIAL`** → [`../reports/STAGE_D_REPORT.md`](../reports/STAGE_D_REPORT.md)

Stage D tests whether the `m = 1` frozen-CUSUM mechanism survives three
generalisations: a **second detector** (D1), **longer stopped windows** (D2), and
**non-Gaussian innovations** (D3). It does so in part. Two pre-specified
criteria did not hold and are reported as failures, not repaired.

Everything here is **Monte Carlo**. Nothing in Stage D is certified or proved.

## Results at a glance

| Gate | Status |
|---|---|
| D1.1 SR ARL0-matched (`A = 520.886134`) | **PASS** |
| D1.2 `Gamma_SR = 17.3198 ± 0.0280`, lower bound > 2 | **PASS** |
| D1.3 SR excess `+1.4746 ± 0.0400` | **PASS** |
| D1.4 SR period-2 root `e* = 1.036719 ± 0.001496` | **CANDIDATE** |
| D2.2 crossing bracket `m* ∈ [50, 75]` | **PASS** |
| D2.3 derivative correspondence at `m > 1` | **FAIL** (0/8 at `h = 0.05`) |
| D2.4 `Gamma_inf = 1.4037 ± 0.0013` | numerical only |
| D2.5 operational consequence of the crossing | **MATHEMATICAL, NOT OPERATIONAL** |
| D3.2 `Gamma_psi > 2`, six families | **PASS** 6/6 frozen, 5/6 normalised |
| D3.2-t3 | **AMBIGUOUS** |
| D4 stability map | **NOT RUN** (gate not met) |
| adversarial suite | **12/12** |

## The two negative results, stated plainly

**D2.3 failed and stays failed.** The discrepancy is `O(h^2)` truncation of a
steep map — order `p = 1.938`, Richardson within `0.40` SE — a diagnosis written
down *before* the run. Re-running at a smaller step and calling that the primary
result would be re-tuning after seeing a `Gamma`, which protocol §8 forbids.

**The `Gamma_m = 2` crossing has no operational counterpart.** All four
pre-specified monitoring metrics vary smoothly and monotonically through
`m* ≈ 72`; none peaks there; alarm alternation persists above it (`−0.456` at
`m = 100`). `m*` is a **local-stability boundary of the deterministic
conditional-mean skeleton at `e = 0`** — not a stochastic phase transition.

## Layout

| Path | Contents |
|---|---|
| `STAGE_D_PROTOCOL.md` | the frozen protocol, sha256 `925adecf…` |
| `notes/CORRESPONDENCE_AUDIT.md` | Phase 0 audit; Addendum A1 on the dwell-vs-truncation divergence |
| `notes/D2_3_STEP_PRECOMMIT.md` | FD step and D1.4 scan, fixed before any map data |
| `notes/D2_5_PRECOMMIT.md` | bridge design, fixed before any bridge data |
| `notes/D3_REGULARITY.md` | D3.1 assumptions A1–A7 with evidential labels |
| `notes/FAILURE_DIAGNOSES.md` | D2.3, adversarial A11, and the low-power A4 check |
| `notes/PROTOCOL_DEVIATIONS.md` | deviations (none) and post-freeze code changes |
| `src/` | simulators, campaigns, adversarial suite, figures, decision |
| `results/` | every confirmatory artifact, one JSON per gate |
| `figures/` | figures A–F, generated from final data only |
| `tests/` | 72 tests |

## Conventions

* Frozen CUSUM `k = 1/2`, `h = 5`, two-sided, inclusive post-update alarm.
* **No minimum dwell** — `tau = inf{t >= 1 : alarm}` — with the truncated reuse
  window `w = min(m, tau)` (convention A). Stage A's simulator *does* apply a
  dwell, so **its `m > 1` map is a different object**; the two agree at `m = 1`.
* SR thresholds are in **natural units** `A`; the recursion logs them once.
* Seeds: confirmatory `20261001`, replication `20261002`, sizing `20261031`.

## Reproduce

```bash
bash level4/stage_d/reproduce.sh
```

About 110 minutes; D2.5 and D3 dominate. All campaigns are seeded and
deterministic.
