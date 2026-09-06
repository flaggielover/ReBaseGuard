# Results — CUSUM Aux4 full cover

**Verdict: `CUSUM_AUX4_INCOMPLETE_FULL_COVER`.**
CUSUM full cover: `INCOMPLETE`. Far field: inherited `PASS`.
Not production, not result-bearing.

## Cover state

* cells certified under the Aux4 producer: **2 of 326**
* obligations PASS: **8 of 8** certified
* cell 325 control all-`m` PASS: None
* difficult cells: {"323,m5": "PASS"}

No predecessor certificate is composed into this ledger: adjudication required a
full 326-cell rerun under a new producer, and the ledger admits a cell only if it
carries this namespace's producer identity.

## Producer identity

| | |
| --- | --- |
| manifest schema | `k1.cusum-aux4.producer-manifest.v2` |
| manifest path | `level4/closure_proofs/p5y_k1_cusum_aux4_fullcover/manifests/producer_manifest_v2.json` |
| manifest hash | `72c75c2244f553d6fd08a6b1e0369eaaf01b2c3cda77a9e5a54943b6805b21cb` |
| runtime contract hash | `d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191` |
| producer identity hash | `f85bd92cd5d32122d4b9618f5981c2a83653266b2a59b097339c6271ed9dcb7c` |
| files bound | 58 |
| OpenBLAS runtime kernel | `SkylakeX` |

## Cost

`COST_CAP` remains **NOT_ESTABLISHED**. the 1126 CPU-hour cap is for the COMPLETE K1 campaign. Only the CUSUM contribution is recorded here; SR is unimplemented and unmeasured, so no campaign-level cost conclusion follows.

{
  "auxiliary_cpu_seconds_mean": 188.9,
  "auxiliary_share": 0.0832,
  "cells_measured": [
    318,
    323
  ],
  "chosen_workers": 4,
  "conditions": "4 workers on 4 physical cores (8 logical), one thread each",
  "cpu_seconds_per_cell_mean": 2270.1,
  "cpu_seconds_per_cell_worst": 2278.1,
  "cusum_only_exceeds_hard_cap": false,
  "cusum_share_of_cap": 0.1826,
  "hard_cap_cpu_hours": 1126,
  "logical_cpus": 8,
  "measured": true,
  "peak_rss_mib_per_worker": 260.7,
  "physical_cores": 4,
  "projected_cusum_cpu_hours": 205.6,
  "projected_cusum_wall_hours": 51.4,
  "scope_note": "the cap governs the COMPLETE K1 campaign. SR (316 cells) is unimplemented and unmeasured, so this is the CUSUM contribution only and implies nothing about campaign cost.",
  "worker_choice_rationale": "8 logical CPUs are 4 hyperthreaded cores. Measured on the predecessor, 8 workers inflate per-cell CPU by 2.04x for the same wall time, so 4 workers deliver the same throughput at half the CPU-hours. CPU-hours are the governed quantity."
}

## Cells 318–325 (the previously difficult block)

| cell | m | status | cover util | M_R2 |
| ---: | ---: | :--- | ---: | ---: |
| 318 | 1 | PASS | 56.08% | 1.4452 |
| 318 | 2 | PASS | 43.96% | 2.0813 |
| 318 | 3 | PASS | 40.76% | 2.7037 |
| 318 | 5 | PASS | 51.91% | 3.7885 |
| 323 | 1 | PASS | 74.78% | 0.8241 |
| 323 | 2 | PASS | 54.54% | 1.1209 |
| 323 | 3 | PASS | 60.37% | 1.2874 |
| 323 | 5 | PASS | 65.26% | 1.4901 |
