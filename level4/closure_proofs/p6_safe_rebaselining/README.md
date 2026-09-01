# P6 — Safe re-baselining: the full campaign

```text
P5_STATUS      = PARTIAL (frozen); adjudication read, premises re-tiered
P6_CAMPAIGN    = EXECUTED
CANDIDATE      = SAW  (selection-aware weighting)
NOVELTY        = PARTIAL / NOT_INDEPENDENTLY_ADJUDICATED
CLOSURE        = see CLOSURE_GATES.md; the independent verdict is Codex's, not this campaign's
```

The design phase lives in `../p6_safe_rebaselining_predesign/` and is left
frozen as the record of what was believed before the data existed. This
directory holds the campaign.

---

## The question, and the answer in one paragraph

*Can a post-alarm re-baselining policy use the alarm-triggering data without
suffering the recursive reference distortion P7 documented?*

The reused window is harmful because it is **selected by the stopping time**:
its raw mean has 2.5x-4.7x the second moment of an unselected mean of the same
length. But the selection intensity varies enormously cycle to cycle, and it is
**observable**: a regression of the latent raw window mean on `(zbar, tau)`
reaches `R^2 = 0.95` in every one of the eight `(detector, m)` families. So the
alarm that is about to damage the reference announces how badly. SAW weights
the reused window against the fresh baseline by the inverse-variance weight
`rho_j = (1/k) / (V_hat_j + 1/k)`, evaluated per cycle from that readout. The
best fixed reuse weight is exactly the degenerate `V_hat = const` member of the
same family, and `THEORY.md` T6-C shows the entire difference between them is a
**Jensen gap**.

## Read in this order

| file | what it is |
|---|---|
| `P5_TO_P6_DEPENDENCY_AUDIT.md` | **first.** Every P5 claim re-tiered against the final adjudication; the branch in force; the gate items cleared |
| `METHOD.md` | the method: mechanism, derivation, the implementable rule, the information set, pseudocode |
| `THEORY.md` | T6-A/B/C/D/E with proofs and an honest status table |
| `EXPERIMENT_PROTOCOL.md` | the preregistration: objective, cell, baselines, metrics, cost model, seeds, staging |
| `CLOSURE_GATES.md` | `C1`-`C10` verbatim plus the selected `G-A`..`G-E` options, and the audit |
| `RESULTS.md` | the confirmation numbers |
| `ABLATION.md` | why it works: the information ladder |
| `ROBUSTNESS.md` | the fresh-budget frontier, finite-reference initialisation, shifts, detectors, windows |
| `NOVELTY_AUDIT.md` | the prior-art audit, executed before the confirmation numbers were read |
| `LIMITATIONS.md` | what breaks it |
| `CODEX_HANDOFF.md` | **last.** What Codex should attack, and how to replay it |

## Harness

`src/rebaseguard_p6c/` is the campaign superset of the pre-design harness. The
frozen detector is imported, never re-implemented, and a constant policy
reproduces `rebaseguard_p7.chain.simulate_chain` with bit-identical `tau`.

```
src/rebaseguard_p6c/
  __init__.py    constants and policy classes
  seeds.py       deterministic TUNE / EVAL / REPLAY derivation (asserted disjoint)
  policy.py      the audited observation object; baselines B0-B11; oracles Z3, Z4
  saw.py         the SAW family, its ablations, and oracles Z1, Z2
  calibrate.py   c_beta from P7's response curve; the SAW plug-in calibration
  chain.py       the policy-driven chain over the frozen core
  runner.py      the calibration fixed point and the cell runners
  metrics.py     per-replicate metrics, tagged latent / observable / cost
  stats.py       paired bootstrap, BCa, ratio bootstrap, P7's verdict labels
```

```bash
level4/.venv/bin/python -m pytest \
  level4/closure_proofs/p6_safe_rebaselining/tests \
  level4/closure_proofs/p6_safe_rebaselining_predesign/tests -q
# 125 passed  (93 campaign + 32 pre-design)
```

`tests/test_p6c_claims.py` re-derives every headline number in these documents
from `results/*.json`, so a document and its evidence cannot drift apart
silently.

## Reproducing the campaign

```bash
P=level4/closure_proofs/p6_safe_rebaselining/experiments
V=level4/.venv/bin/python
$V $P/stage1_foundation.py      # X1-X5, c_beta, the SAW calibration      (~7 min)
$V $P/stage2_screen.py          # pilot + screen on TUNE                  (~9 min)
$V $P/stage4_confirm.py eval    # confirmation on EVAL                    (~40 min)
$V $P/analyse.py eval
$V $P/stage5_robustness.py      # frontier, finite reference, approximation
$V $P/stage4_confirm.py replay  # independent reproduction
$V $P/analyse.py replay
```

Every run is a deterministic function of `(family, detector, m, policy_id,
cell_tag, block)`, so any single cell can be regenerated in isolation.
