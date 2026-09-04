# P5Y Gate-2F temporal ledger

| anchor | meaning | evidence |
|---|---|---|
| `T0` | preregistration frozen | `GATE2F_PREREGISTRATION.md`, committed with **no** file under `results/` |
| `T1` | code/config/source hashes frozen | `GATE2F_SOURCE_MANIFEST.json`, same commit; 21/21 pre-T2 tests green, including the negative control that reproduces Gate-2E's knife edge and shows the asymmetric fix removes it |
| `T2` | first result-bearing execution | creation of `results/sr_metric_b.json` |
| `T3` | all frozen outcomes complete | same artifact |
| `T4` | final report | `GATE2F_RESULT.md` |

The Gate-2E metric is inherited **by reference** (Gate-2E's module is imported
and its attributes used directly), so the equality audit is structural rather
than a transcription check. Every precision cell is computed by calling
Gate-2E's `run_cell` verbatim.

Pre-T2 correction, before any result-bearing computation: one test string match
that did not account for the tokenizer's whitespace normalisation. No threshold,
constant, object, grid or rule changed.
