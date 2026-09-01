# P6R — repair and independent-confirmation preparation

```text
ORIGINAL P6 VERDICT (independent)  = PARTIAL          closure REJECTED
T6-B                               = EXACT_VALID
T6-C                               = VALID_WITH_NARROWER_ASSUMPTIONS   (fixed k)
SCIENTIFIC CORE                    = SURVIVES
THIS CAMPAIGN                      = a NEW, separately auditable confirmation campaign
FIRST-PARTY VERDICT                = see CONFIRMATION_REPORT.md; the next
                                     independent reviewer owns final closure
```

The original campaign at `../p6_safe_rebaselining/` is **historical evidence**.
It is preserved byte-for-byte — `precommit/historical_p6_manifest.json` hashes
all 121 files of it and its pre-design, and `tests/test_p6r_scope.py` asserts
they never change. Nothing here is arranged to make the original execution look
retroactively compliant.

---

## What P6R repairs, and what it does not touch

| adjudicated defect | repair |
|---|---|
| **B1** `B2*` selected on EVAL/REPLAY | `select.py` rule **S1**: TUNE-only, on a frozen `0.01`-spaced grid `{0.05 … 0.35}`, written to `precommit/baseline_selection.json` **before** any EVAL run; plus a second declared control at the adjudication-identified `rho = 0.25` |
| **B2** preregistered statistics not executed | `stats_r.py`: exactly 10,000 resamples, BCa with a real jackknife, normal intervals emitted beside every BCa, ratios bootstrapped as ratios over replicate pairs, BH-FDR over declared families, a 200-event tail floor. `tests/test_p6r_stats.py` asserts each element **runs** |
| **B3** temporal precommitment unestablished | Checkpoint A is committed and pushed before confirmation EVAL; `confirm_eval.py` **refuses to run** until `results/precommit_anchor.json` records that commit's SHA |
| **B4** `G-E` ordering defect | not re-litigated. `Coll` is a **thresholdless reported diagnostic**, declared so in advance |

**Not touched:** the method. `SAW-M`, the chain and the frozen detector are
imported from the adjudicated `rebaseguard_p6c` package rather than
re-implemented, so the object under confirmation is the object that was
adjudicated. `tests/test_p6r_scope.py::test_p6r_does_not_reimplement_the_method`
asserts it.

## Read in this order

| file | what it is |
|---|---|
| `ADJUDICATION_RECORD.md` | **first.** The verdict, the four blocking defects, and nine material non-blocking qualifications, unsoftened |
| `THEOREM_SCOPE.md` | T6-B unchanged with its policy class pinned field-by-field; T6-C stated exactly, **for fixed `k` only** |
| `REPAIRED_PROTOCOL.md` | the whole precommitment: grid, selection rule, cells, metrics, statistics, BH families, tail floor, cost definitions, `Delta` scope, calibration diagnostics, closure rule, execution order |
| `NOVELTY_SCOPE.md` | the conservative independent wording, adopted verbatim |
| `CONFIRMATION_REPORT.md` | the repaired results and the first-party verdict *(Checkpoint B)* |
| `precommit/` | the frozen artifacts: calibration audit, `s1` sensitivity, TUNE baseline selection, manifest, historical hashes |

## Package

```
src/rebaseguard_p6r/
  select.py    TUNE-only fixed-rho selection (rule S1)
  stats_r.py   the repaired statistical procedure
  onestep.py   the direct realized one-step risk statistic (formula precommitted)
  costs.py     the three cost accountings, with the permitted claim stated
  audit.py     calibration diagnostics
```

## Running it

```bash
V=level4/.venv/bin/python
P=level4/closure_proofs/p6r_safe_rebaselining_confirmation

$V -m pytest $P/tests -q                       # focused tests
$V $P/experiments/precommit_freeze.py          # TUNE only: audit + selection
#   --- Checkpoint A: commit and push; record the SHA in results/precommit_anchor.json
$V $P/experiments/confirm_eval.py              # refuses to run before the anchor exists
$V $P/experiments/analyse_r.py eval
$V $P/experiments/confirm_eval.py replay
$V $P/experiments/analyse_r.py replay
#   --- Checkpoint B: commit and push
```

## Standing

P6R does **not** award closure. It prepares a package another independent
reviewer can adjudicate, and its own verdict is first-party only.
