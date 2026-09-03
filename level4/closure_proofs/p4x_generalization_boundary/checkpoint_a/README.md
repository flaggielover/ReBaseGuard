# P4X Checkpoint A

```text
ARTIFACT   = P4X_CHECKPOINT_A
ACTIVE     = YES
BINDING    = YES
P4_ORIGINAL_VERDICT   = PARTIAL   (immutable)
P4X_SUCCESSOR_VERDICT = NOT_YET_RUN
```

The binding specification of the P4X successor campaign, frozen before any
production run.

| file | content |
|---|---|
| `CHECKPOINT_A.md` | the binding specification, human readable |
| `results/checkpoint_a.json` | the authoritative machine-readable manifest |
| `build_checkpoint.py` | generates the manifest by deriving every frozen number from existing artifacts |
| `tests/` | asserts the manifest is complete, internally consistent, and exactly reproducible |

`results/checkpoint_a.json` is authoritative where it and `CHECKPOINT_A.md`
disagree.

## Status

No production has been run.  No result artifact exists.  No production outcome
has been inspected.  `production_run_performed = false` and
`result_artifacts_generated = false` in the manifest, and the tests assert both.

## Reproducing the manifest

```bash
python build_checkpoint.py
```

Re-running the generator must reproduce `results/checkpoint_a.json` byte for
byte; `tests/test_checkpoint_reproducible.py` asserts exactly that.

## What this namespace must never do

* modify, reopen or reinterpret `../../p4_theory_generalization/`, or any
  `P1`-`P9`, `P8R`, `P9R` or `P5X` namespace;
* relabel historical `P4` as anything other than `PARTIAL`;
* weaken the frozen 3 % accuracy criterion or the `|z| <= 4` criterion;
* adopt a variance-reduction method R0 rejected, or use Route Q as an arbiter;
* change any threshold, budget or scope after seeing a production result;
* claim novelty, or claim Level-4 global closure.
