# Results — CUSUM aux3 successor

**Verdict: `CUSUM_AUX3_READY_FOR_INDEPENDENT_ADJUDICATION`.**
CUSUM compact cover: `PASS_CANDIDATE`. Far field: inherited `PASS`.
Not production, not result-bearing, no cell claimed closed beyond its own
certificate.

## The five obligations this task targeted

The predecessor left exactly five failures: (319,5), (320,5), (321,5), (322,5),
(323,5). After the auxiliary third-derivative refinement:
**5 of 5 now PASS**.

## Counts, stated exactly

* cells 318–324: **28 of 28** obligations PASS
* cells 318–325: **32 of 32** obligations PASS
* cell 325 regression control: clean, all m PASS

| cell | rho | m | status | classification | cover util | M_R2 | nodes tightened |
| ---: | ---: | ---: | :--- | :--- | ---: | ---: | ---: |
| 318 | 0.10732 | 1 | PASS | CERTIFIED_PASS | 56.08% | 1.4452 | 28 |
| 318 | 0.10732 | 2 | PASS | CERTIFIED_PASS | 43.96% | 2.0813 | 28 |
| 318 | 0.10732 | 3 | PASS | CERTIFIED_PASS | 40.76% | 2.7037 | 28 |
| 318 | 0.10732 | 5 | PASS | CERTIFIED_PASS | 51.91% | 3.7885 | 28 |
| 319 | 0.12280 | 1 | PASS | CERTIFIED_PASS | 57.24% | 1.6081 | 27 |
| 319 | 0.12280 | 2 | PASS | CERTIFIED_PASS | 48.09% | 2.0828 | 27 |
| 319 | 0.12280 | 3 | PASS | CERTIFIED_PASS | 44.69% | 2.6071 | 27 |
| 319 | 0.12280 | 5 | PASS | CERTIFIED_PASS | 58.32% | 3.5531 | 27 |
| 320 | 0.13650 | 1 | PASS | CERTIFIED_PASS | 41.08% | 1.5870 | 25 |
| 320 | 0.13650 | 2 | PASS | CERTIFIED_PASS | 41.42% | 1.9072 | 25 |
| 320 | 0.13650 | 3 | PASS | CERTIFIED_PASS | 47.29% | 2.2787 | 25 |
| 320 | 0.13650 | 5 | PASS | CERTIFIED_PASS | 63.68% | 3.1443 | 25 |
| 321 | 0.14657 | 1 | PASS | CERTIFIED_PASS | 50.96% | 1.3839 | 23 |
| 321 | 0.14657 | 2 | PASS | CERTIFIED_PASS | 45.50% | 1.6204 | 23 |
| 321 | 0.14657 | 3 | PASS | CERTIFIED_PASS | 58.90% | 1.8929 | 23 |
| 321 | 0.14657 | 5 | PASS | CERTIFIED_PASS | 73.04% | 2.5472 | 23 |
| 322 | 0.15250 | 1 | PASS | CERTIFIED_PASS | 71.28% | 0.9809 | 20 |
| 322 | 0.15250 | 2 | PASS | CERTIFIED_PASS | 54.29% | 1.2900 | 20 |
| 322 | 0.15250 | 3 | PASS | CERTIFIED_PASS | 63.66% | 1.5116 | 20 |
| 322 | 0.15250 | 5 | PASS | CERTIFIED_PASS | 73.26% | 1.9235 | 20 |
| 323 | 0.15525 | 1 | PASS | CERTIFIED_PASS | 74.78% | 0.8241 | 18 |
| 323 | 0.15525 | 2 | PASS | CERTIFIED_PASS | 54.54% | 1.1209 | 18 |
| 323 | 0.15525 | 3 | PASS | CERTIFIED_PASS | 60.37% | 1.2874 | 18 |
| 323 | 0.15525 | 5 | PASS | CERTIFIED_PASS | 65.26% | 1.4901 | 18 |
| 324 | 0.15627 | 1 | PASS | CERTIFIED_PASS | 60.22% | 0.9402 | 18 |
| 324 | 0.15627 | 2 | PASS | CERTIFIED_PASS | 44.66% | 1.0644 | 18 |
| 324 | 0.15627 | 3 | PASS | CERTIFIED_PASS | 47.12% | 1.1399 | 18 |
| 324 | 0.15627 | 5 | PASS | CERTIFIED_PASS | 48.78% | 1.2076 | 18 |
| 325 | 0.09624 | 1 | PASS | CERTIFIED_PASS | 12.81% | 0.6741 | 18 |
| 325 | 0.09624 | 2 | PASS | CERTIFIED_PASS | 8.72% | 0.5860 | 18 |
| 325 | 0.09624 | 3 | PASS | CERTIFIED_PASS | 8.67% | 0.5665 | 18 |
| 325 | 0.09624 | 5 | PASS | CERTIFIED_PASS | 8.48% | 0.5456 | 18 |

## Against the predecessor (70a2943)

| cell | m | predecessor (70a2943) | this successor | improvement |
| ---: | ---: | :--- | :--- | ---: |
| 318 | 1 | 56.08% PASS | 56.08% PASS | 1.00x |
| 318 | 2 | 43.96% PASS | 43.96% PASS | 1.00x |
| 318 | 3 | 47.35% PASS | 40.76% PASS | 1.16x |
| 318 | 5 | 98.29% PASS | 51.91% PASS | 1.89x |
| 319 | 1 | 57.24% PASS | 57.24% PASS | 1.00x |
| 319 | 2 | 48.30% PASS | 48.09% PASS | 1.00x |
| 319 | 3 | 53.34% PASS | 44.69% PASS | 1.19x |
| 319 | 5 | 115.29% FAIL | 58.32% PASS | 1.98x |
| 320 | 1 | 41.08% PASS | 41.08% PASS | 1.00x |
| 320 | 2 | 42.64% PASS | 41.42% PASS | 1.03x |
| 320 | 3 | 58.87% PASS | 47.29% PASS | 1.24x |
| 320 | 5 | 125.78% FAIL | 63.68% PASS | 1.98x |
| 321 | 1 | 50.96% PASS | 50.96% PASS | 1.00x |
| 321 | 2 | 48.53% PASS | 45.50% PASS | 1.07x |
| 321 | 3 | 72.27% PASS | 58.90% PASS | 1.23x |
| 321 | 5 | 133.53% FAIL | 73.04% PASS | 1.83x |
| 322 | 1 | 71.28% PASS | 71.28% PASS | 1.00x |
| 322 | 2 | 57.76% PASS | 54.29% PASS | 1.06x |
| 322 | 3 | 75.87% PASS | 63.66% PASS | 1.19x |
| 322 | 5 | 123.90% FAIL | 73.26% PASS | 1.69x |
| 323 | 1 | 74.78% PASS | 74.78% PASS | 1.00x |
| 323 | 2 | 57.46% PASS | 54.54% PASS | 1.05x |
| 323 | 3 | 70.91% PASS | 60.37% PASS | 1.17x |
| 323 | 5 | 104.29% FAIL | 65.26% PASS | 1.60x |
| 324 | 1 | 60.22% PASS | 60.22% PASS | 1.00x |
| 324 | 2 | 47.24% PASS | 44.66% PASS | 1.06x |
| 324 | 3 | 55.69% PASS | 47.12% PASS | 1.18x |
| 324 | 5 | 75.48% PASS | 48.78% PASS | 1.55x |
| 325 | 1 | 12.81% PASS | 12.81% PASS | 1.00x |
| 325 | 2 | 9.21% PASS | 8.72% PASS | 1.06x |
| 325 | 3 | 10.37% PASS | 8.67% PASS | 1.20x |
| 325 | 5 | 12.71% PASS | 8.48% PASS | 1.50x |

## Auxiliary evidence

Nested third-derivative certificates (`h'''`, `S'''`, `W'''`) owned by the cell's
existing curvature obligations. No top-level work id, no DAG node: the frozen
universe stays at 17,978.

| cell | auxiliary objects | aux CPU s | aux share | nodes considered | nodes tightened | best factor |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 318 | 15 | 385 | 8.3% | 45 | 28 | 2.85x |
| 319 | 15 | 388 | 8.4% | 45 | 27 | 2.87x |
| 320 | 15 | 393 | 8.4% | 45 | 25 | 2.64x |
| 321 | 15 | 385 | 8.3% | 45 | 23 | 3.27x |
| 322 | 15 | 385 | 8.3% | 45 | 20 | 3.80x |
| 323 | 15 | 387 | 8.3% | 45 | 18 | 4.55x |
| 324 | 15 | 390 | 8.4% | 45 | 18 | 5.64x |
| 325 | 15 | 387 | 8.4% | 45 | 18 | 9.44x |

## Provenance

| | |
| --- | --- |
| producer manifest hash | `9deb4d552e3381b855140cb33310465f9e77a5177f7c899f749e1aee375f16f8` |
| manifest schema | `k1.cusum-aux3.producer-manifest.v1` |
| committed artifact | `level4/closure_proofs/p5y_k1_cusum_aux3_successor/manifests/producer_manifest_v1.json` |
| files bound | 51 |
| manifest verifies from disk | True |
| strict coverage in the certifying process | True |

## Determinism

| cell | recorded hash | fresh repeat | identical | CPU s (recorded / repeat) |
| ---: | :--- | :--- | :--- | :--- |
| 318 | `2853045fc5d4f14d` | `2853045fc5d4f14d` | yes | 4628 / 2267 |
| 323 | `0a739fe7e68c105a` | `0a739fe7e68c105a` | yes | 4632 / 2269 |

## Cost

`COST_CAP` remains **NOT_ESTABLISHED**. the block ran 8 workers on 8 cores; per-cell CPU seconds are inflated by memory-bandwidth stalls. Only the repeat runs, at 2 workers, are clean measurements, and even those are not a cost model.
Auxiliary evidence costs 8.4% of the per-cell CPU.
