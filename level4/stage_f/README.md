# Stage F — Level-4 final closure audit

**Verdict: Level 1–3 `CLOSED` · Level 4 `LEVEL-4-PARTIAL`**

Stage F is an **audit**, not an experiment. It ran no new science, generated no
new scientific data, and modified no historical scientific artifact.

## Entry points

| Document | Contents |
|---|---|
| [`../reports/LEVEL_4_FINAL_REPORT.md`](../reports/LEVEL_4_FINAL_REPORT.md) | the closure report (26 sections) |
| [`../reports/LEVEL_4_FINAL_LEDGER.md`](../reports/LEVEL_4_FINAL_LEDGER.md) | 32 claims with scope, evidence, safe and forbidden wording |
| [`FINAL_DECISION.md`](FINAL_DECISION.md) | the verdict and its mechanical path |
| [`LEVEL4_REQUIREMENTS_RECONSTRUCTION.md`](LEVEL4_REQUIREMENTS_RECONSTRUCTION.md) | what Level 4 was pre-specified to require |
| [`INTEGRITY_AUDIT.md`](INTEGRITY_AUDIT.md) | hashes, decisions, verification transcripts |
| [`SCIENTIFIC_SYNTHESIS.md`](SCIENTIFIC_SYNTHESIS.md) | cross-stage synthesis, layer by layer |
| [`notes/FAILURE_DIAGNOSES.md`](notes/FAILURE_DIAGNOSES.md) | the failed-first adversarial run and every preserved historical failure |
| `results/final_decision.json` | machine-readable verdict |
| `results/adversarial_f_FIRST_RUN.json` | **11/18 first run, preserved permanently** |

## The three findings that shaped the verdict

1. **No pre-specified Level-4 closure criteria exist.** The Level 1–3 closure
   report says "Level 4 is not authorized by this document and has not been
   started". Level 4 was defined stage by stage. This is why
   `LEVEL-4-CLOSED-WITH-LIMITATIONS` is unavailable: there is no original
   architecture to permit it.
2. **The verdict is robust to the one interpretive ambiguity.** Whether
   `staged_task_ranking.csv`'s MANDATORY labels bind or not, both readings give
   "not closed".
3. **The rigorous core describes a deterministic skeleton that does not govern
   the stochastic process** — falsified in the 2026-08-21 design ledger and
   independently confirmed by Stage D's D2.5 (`MATHEMATICAL, NOT OPERATIONAL`).

## Reproduce

```bash
bash level4/stage_f/reproduce.sh
```

Read-only with respect to every historical artifact; regenerates only Stage F's
own outputs.
