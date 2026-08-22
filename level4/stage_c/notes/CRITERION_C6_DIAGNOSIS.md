# Why criterion C6 failed, and what the data actually show

**C6 failed. It stands as failed, and the Stage C decision reflects that.**
This note explains what went wrong with the criterion; it does not amend it.

## What C6 said

> C6 — improvement is not bought by destroying detection: for every `Delta`, the
> paired 95% CI for `delay(RBG) - delay(rho=1)` must lie below
> `+0.25 x delay(rho=1)`; i.e. RBG may not be more than 25% slower.

## What happened

| `Delta` | delay(RBG) | delay(`rho=1`) | difference | threshold | verdict |
|---|---|---|---|---|---|
| 0.25 | 77.68 | 51.91 | +25.77 | +12.98 | **FAIL** |
| 0.50 | 74.10 | 50.28 | +23.82 | +12.57 | **FAIL** |
| 1.00 | 52.00 | 53.19 | −1.19 | +13.30 | PASS |
| 1.50 | 33.73 | 44.37 | −10.64 | +11.09 | PASS |

## The flaw in the criterion

C6 compares **raw** delays between two policies whose in-control cycle ARLs
differ by a factor of 1.7 (RBG 85.2, full reuse 50.0). A detector that alarms
constantly will always post short "delays", whether or not anything changed.
Comparing raw delays across such different baseline alarm rates is not
like-for-like, and I flagged that hazard in the protocol (§9) and then failed to
build the criterion around it.

## What the data actually show

Normalising each policy by its own in-control delay removes the baseline alarm
rate and measures sensitivity as such:

| `rho` | `Delta`=0.25 | 0.5 | 1.0 | 1.5 |
|---|---|---|---|---|
| 0 (fresh) | 0.921 | 0.895 | 0.681 | 0.433 |
| **0.0298 (RBG)** | **0.932** | **0.889** | **0.624** | **0.405** |
| 0.25 | 0.900 | 0.805 | 0.565 | 0.264 |
| **1.0 (full reuse)** | **1.027** | **0.995** | **1.052** | **0.878** |

Full reuse's ratio sits at essentially **1.0 at every shift**: its detection
delay is almost identical whether or not a change occurred. Its alarms are
driven by its own reference instability, not by the data. That is the opposite
of sensitivity.

ReBaseGuard's ratios fall from 0.93 to 0.41, i.e. it responds to the change. And
in absolute terms at `Delta = 1.5` it is **faster** than full reuse (33.7 vs
44.4) despite a 1.7× longer in-control run length.

So the scientific concern C6 was written to capture — *is the stability gain
bought by making the detector blind?* — is answered decisively **no**, in the
opposite direction from the criterion's verdict.

## What this does and does not change

* The pre-specified criterion **failed**; the decision rule was applied as
  written, giving `STAGE-C-PARTIAL`.
* The criterion was **not** rewritten, and the baseline-free ratio is reported
  as a clearly-labelled **secondary diagnostic**, never as a gate.
* A future protocol should specify the detection criterion on the
  baseline-normalised ratio, or on delay at a matched in-control ARL. The latter
  is impossible here because `h` is frozen, which is precisely why the ratio is
  the right normalisation for this model.
