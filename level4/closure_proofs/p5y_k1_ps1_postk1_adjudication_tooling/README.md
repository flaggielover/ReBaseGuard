# Post-K1 adjudication tooling (PREPARED, NOT EXECUTED on genuine data)

This is result-agnostic integrity tooling for the day PS1 completes. It establishes completeness,
consistency and accounting. It never decides scientific success, and the producer may not self-award `K1_CLOSED`.

| file | role |
|---|---|
| `code/ps1_adjudication_audit.py` | Audits A–G: sealed-cell completeness (369), ledger↔file reconciliation, evidence re-hash and recomputed `scientific_content_hash`, torn/duplicate/orphan-marker/reservation/run/halt state, CPU-hour accounting (92.32 imported + science + settlement charges vs the 6,600 cap), continuity hash chains. Writes the per-cell coverage matrix CSV. **Blinded by default**: scientific status values are never loaded; `--unblind` is reserved for the independent adjudicator and adds only a verbatim column. |
| `CLOSURE_REPORT_SKELETON.md` | Mechanical placeholders for integrity and accounting. Scientific status and verdict sections are adjudicator-only; §17 consequences are pre-stated. |
| `tests/test_adjudication_audit.py` | 5 fixture tests (blinding, partial-but-integral, tamper and orphan detection, open-reservation accounting, unblind column): **5 passed on Vultr** |

Intended read-only invocation on AWS, after the run is drained and settled, never while live:

```
python code/ps1_adjudication_audit.py \
  --production-root /home/ubuntu/work/ReBaseGuard-ps1-prod-gen2 \
  --runtime-dir /home/ubuntu/rbg-runtime/p5y_k1_ps1_generation2 \
  --evidence-root /home/ubuntu/rbg-runtime/p5y_k1_ps1_production/evidence \
  --evidence-root /home/ubuntu/rbg-runtime/p5y_k1_ps1_generation2/evidence \
  --gen1-ledger /home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/p5y_k1_ps1_production/production/PRODUCTION_LEDGER.json \
  --out-dir <outside every source tree>
```

Both evidence roots are passed because live gen2 cells were written to the gen1 runtime root
(see `p5y_k1_ps1_gen2_runtime_isolation/AUDIT.md` M1/M3). Sealed records carry absolute evidence paths,
so the audit is location-independent.
