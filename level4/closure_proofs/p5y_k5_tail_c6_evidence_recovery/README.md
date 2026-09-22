# P5Y / K5 Campaign C6 — evidence recovery and DATA-vs-NEW_REAL classification

C6 is a **forensic** campaign. It does not improve a constant. It asks, for every route C5 classified
`DATA_BLOCKED`, whether the project is missing **data** or missing **science**.

**The answer is neither.** For the two highest-leverage DATA-blocked routes the project is missing a **toolchain**.

Successor to C5, which is complete and immutable. C2, C3, C4 and C5 are unmodified; no historical artifact is
modified. `NEW_REAL_SCIENTIFIC_ADDRESSES = 0`, `SCIENTIFIC_KERNEL_EVALUATIONS = 0`, guard
`REAL_SCIENTIFIC_COMPUTE = DENY`, external evidence mutations **0**. **AWS SR/PS1 was never contacted.**

**Three refs, kept apart.** `LOCAL_MAIN_REF = c123b9bb`, `REMOTE_MAIN_REF = 1cb45382` (queried from GitHub, not
inferred), and `VULTR_WORKING_REF = c123b9bb` — the worker's own checkout, which is evidence about *neither* main
ref even though it happens to equal the local one. C6 reconciles nothing.

| phase | artifact |
|---|---|
| B0 predecessor audit | `evidence/b0/C6_B0_AUDIT.json` (19/19) |
| 1,2,10,11 missing-evidence graph | `evidence/graph/C6_MISSING_EVIDENCE_GRAPH.json` |
| 3 external inventory | `evidence/inventory/C6_EXTERNAL_INVENTORY.json` |
| 4,5 provenance binding | `evidence/provenance/C6_PROVENANCE.json` |
| 13 frozen classification gate | `config/FEASIBILITY_GATES_C6.json` |
| 9 revised route ledger | `evidence/leverage/C6_CLASSIFICATION.json` |
| 14 forensic review | `review/REVIEW_C6_FORENSIC.md` |
| 17 adjudication | `evidence/adjudication/C6_ADJUDICATION.md` |

## The two findings that matter

**1. The K1 object candidates were never serialized — anywhere, ever.** Not in Git (all 603 commits, 58 branches,
36 tags), and not in the historical store: all **326** sealed records were hash-verified read-only against their
own manifest (326 OK, 0 mismatch, 93,093,045 bytes) and **0 of 326** contain any candidate-payload key. The
`identity_gate` compares only scalars, because only scalars were ever stored. But the candidates are a
**deterministic function of committed code and the committed cell spec** — the entire 13-module frozen chain is
committed — and `tct_inputs.py`'s own docstring classifies exactly that recomputation as *"not a new real
scientific evaluation"*. So route A1 is **REPLAYABLE_EXISTING_ADDRESS**, blocked here only because numpy and
python-flint are absent on this host. C6 does **not** perform the replay: it runs the certifier, so it is not the
serialization-only operation the instruction permits.

**2. All four open tail cells' sealed K1 records are recovered, at P3.** Cell 309's copy is even committed in Git
already. Each recovered file is hash-identical to **two independent committed bindings** — the export manifest and
`ADOPTED_TAIL_INPUTS.record_sha256`. Provenance is capped at **P3, not P4**, because two upstream links do not
close by raw bytes: the record's own `producer_manifest_hash` ≠ the sha256 of the committed producer manifest it
names, and the export manifest's `composite_audit_sha256` matches neither the committed nor the external audit.
C6 does not upgrade provenance by inference.
