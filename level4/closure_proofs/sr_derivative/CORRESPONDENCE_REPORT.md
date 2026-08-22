# SR derivative numerical correspondence report

**Outcome date:** 2026-08-22  
**Protocol SHA-256:** `e9b66ff8ffbf0d8138598b1d4dc19dcc1e44d8b4f33f5b462b5b82f341d5f762`  
**Pre-outcome implementation commit:** `2bacc302b90bc961589aefac88b13623de4d0f47`  
**Authoritative threshold:** `A=520.886133602749`  
**Numerical decision:** `NUMERICAL GATE CLOSED — LEAN AUTHORIZED`

The frozen workload ran without a sample-size, threshold, step, seed, route,
or criterion change.  Total elapsed time was `2690.33 s`.  Route B was not
inspected or evaluated until all 128 independent batch derivatives existed.

## 1. Structural gate

All pre-outcome controls passed:

- raw/log deterministic path correspondence;
- stepwise chart reflection and terminal-statistic sign changes;
- explicit simultaneous-unequal and exact-tie classification;
- `rho=0`, `rho=1`, and `rho=0.37` affine identities;
- Route A/Route B source separation;
- seed-family disjointness;
- authoritative binary64 threshold identity; and
- frozen protocol hash.

Both confirmatory routes observed zero exact ties and zero simultaneous chart
crossings.  No unexpected event was silently assigned a direction.

## 2. Calibration checks

The two calibration checks retained their separate roles.

### 2.1 Calibration-reproduction sanity

The fresh 800,000-cycle CUSUM target estimate was `466.4315625`.  Twelve frozen
SR bisection evaluations reduced the bracket to

```text
[522.402185178, 522.836152670].
```

The geometric-midpoint candidate was

```text
A_candidate = 522.6191238793916,
|A_candidate/A_authoritative-1| = 0.0033270 = 0.333% < 2%.
```

Its fresh 800,000-cycle ARL was `466.78870625`, a diagnostic ratio of
`1.0007657` to the target.  This candidate was not substituted into the
theorem or either numerical route.

### 2.2 Fixed-operating-point matching

At the immutable thresholds, 64 batches of 10,000 cycles gave:

| Detector | ARL mean | Batch SE |
|---|---:|---:|
| SR, `A=520.886133602749` | 464.919859 | 0.543184 |
| CUSUM, `h=5` | 465.672975 | 0.505656 |

The ratio was `0.99838274`, a relative error of `-0.1617%`, inside the frozen
1% blocking band.

Both calibration criteria passed.

## 3. Route A — raw stopped-score prediction

The independent raw-state implementation ran 64 batches of 25,000 reset
cycles, 1,600,000 paths total.

| Quantity | Estimate | Batch SE |
|---|---:|---:|
| `Gamma_SR=E_0[Z_tau T_tau]` | 17.2913209 | 0.0275686 |
| theorem-predicted derivative `1-Gamma_SR` | -16.2913209 | 0.0275686 |
| ARL | 464.912276 | 0.319701 |
| `E[Z_tau]` symmetry control | 0.00107665 | 0.00160268 |
| `E[T_tau]` symmetry control | 0.0185076 | 0.0178317 |

The comparison with the historical Stage D estimate
`17.3198306 ± 0.0280015` gave combined `z=-0.72553`, inside the precommitted
four-SE band.

The batch-Student numerical 99% lower bound was `17.2180948>2`.  This is
strong confirmatory numerical evidence only; it is not an Arb or rigorous
certificate.

Route A recorded zero exact ties and zero simultaneous crossings.  Every
Route-A criterion passed.

## 4. Route B — independent conditional-map derivative

The independently written log-state implementation used two disjoint
replications, each with 64 batches of 12,500 paired paths per sign and step.
Every batch formed its derivative directly from its matched `+h/-h` map means;
the reported SEs are empirical SEs of those paired batch derivatives.

| `h` | Pooled derivative | Paired batch SE | Role |
|---:|---:|---:|---|
| 0.1000 | -12.6117740 | 0.0076854 | diagnostic |
| 0.0500 | -15.1442792 | 0.0161792 | diagnostic |
| 0.0250 | -15.9834501 | 0.0268471 | diagnostic |
| **0.0125** | **-16.1950096** | **0.0390592** | **frozen primary** |

At the primary step:

| Estimate | Value | SE | `z` versus Route A |
|---|---:|---:|---:|
| replication 1 | -16.2240130 | 0.0511375 | 1.15858 |
| replication 2 | -16.1660062 | 0.0592381 | 1.91792 |
| pooled | -16.1950096 | 0.0390592 | 2.01453 |

The two replication estimates differed by only `0.74123` combined SE.  The
pooled discrepancy from the Route-A theorem prediction was `0.59118%`, below
the 2% cap.  Thus:

- pooled `|z|=2.01453<=3`;
- both replication `|z|` values are below 4;
- replication agreement `|z|=0.74123<=3`; and
- pooled relative discrepancy `0.0059118<=0.02`.

Every Route-B primary criterion passed.  Exact ties and simultaneous crossings
were both zero.

## 5. Secondary diagnostics

The Richardson diagnostic was

```text
-16.2655294 ± 0.0471023.
```

Successive observed orders were approximately `1.59` and `1.99`.  These values
were computed only after the primary decision inputs were fixed.  They neither
failed nor rescued the primary gate.

## 6. Decision and scientific boundary

The structural, calibration, Route-A, and Route-B blocks all passed.  The
frozen numerical declaration is therefore:

```text
NUMERICAL GATE CLOSED — LEAN AUTHORIZED
```

The evidence supports the human identity

```text
F'_rho(0)=rho(1-Gamma_SR)
```

for the frozen SR detector/reuse correspondence and authorizes the conditional
Lean proof spine.

At this checkpoint the status boundary is still:

```yaml
derivative theorem: human proof and numerical correspondence CLOSED; Lean pending
Gamma_SR > 2: CONFIRMATORY NUMERICAL
rigorous SR local-instability certificate: OPEN
```

No SR instability claim is described as certified or rigorous.

