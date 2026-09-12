# P4ZR — RNG provenance repair for the P4Z/P4ZA/P4ZB successor line

**This is an additive governance repair. It is not a scientific campaign, it
produces no scientific result, and it changes no verdict.**

> `P4 = PARTIAL` is immutable and unchanged. P4X's governance record, P4Y's
> `NOT_FEASIBLE` record, and every frozen result-bearing P4Z / P4ZA / P4ZB
> artifact — plans, checkpoints, adjudications, blocks, hashes, manifests —
> are historical protected evidence. Nothing here modifies a byte of any of
> them, and `tests/` proves that on every run.

## What this namespace contains

| path | what it is |
|---|---|
| `RNG_ADDRESS_SEPARATION.md` | the disclosure record: the exact collisions, root cause, chronology, what calibration did and did not observe, bounded impact, residual risk |
| `src/rebaseguard_p4zr/rng_address_audit.py` | the reusable **same-campaign** calibration/production RNG address audit |
| `audit/build_rng_manifests.py` | derives each campaign's RNG manifest from frozen artifacts; asserts every constant it extracts |
| `audit/strict_gate_recheck.py` | re-decides all 96 authoritative cells under the frozen gate with every successor-added uncertainty allowance removed |
| `audit/build_disclosure.py` | composes the machine-readable disclosure |
| `results/` | the derived manifests, the audit reports, the strict-gate reconstruction, the disclosure |
| `tests/` | the audit's own unit tests, and regression tests that re-derive the findings from frozen artifacts |

## The defect, in one paragraph

P4Z's two pre-run diagnostic programs (`run_micropilots.py`,
`run_fd_ladder.py`) seeded themselves from the *base* of the production seed
schedule rather than from a separate calibration namespace. They therefore
consumed 25 RNG addresses that P4Z production later reused for
`frozen/cusum@5/gaussian` and `frozen/cusum@5/laplace` — and on three of the
five overlaps the delivered innovations were byte-identical, not merely
correlated. P4ZA reuses one seed *integer* across two different bit generators,
which shares no innovation but defeats the same bookkeeping. P4ZB is clean.

No calibration program read the correspondence gate statistic or any cell
disposition at a shared address, both affected configurations have all their
cells authored by P4ZA at disjoint addresses, and all 96 cells clear the frozen
gate with margin under the strictest available reading. That bounds the
exposure; it does not prove the overlap changed nothing. See
`RNG_ADDRESS_SEPARATION.md` §5–§6.

## Why a detective check rather than a constructive one

`p8r_temporal_integrity_repair` already makes calibration/production address
reuse impossible **by construction**, for campaigns written against its tag
discipline. The P4Z line predates it and draws directly on the frozen
`p4_theory_generalization` addressing, so that guarantee does not reach it, and
retrofitting it would mean editing frozen historical code. This module is the
missing complement: given the streams a campaign actually consumed, it proves
same-campaign disjointness at real address semantics. P8R prevents; this audits.

## Running it

```bash
# rebuild every derived artifact from frozen evidence
python3 audit/build_rng_manifests.py
python3 audit/strict_gate_recheck.py
python3 audit/build_disclosure.py

# audit one campaign; exits non-zero on RNG_ADDRESS_SEPARATION_FAIL
PYTHONPATH=src python3 -m rebaseguard_p4zr.rng_address_audit \
    results/rng_manifests/p4zb_rng_manifest.json

python3 -m pytest tests/ -q
```

## Still outstanding

This repair is **B2** only. Two independent adjudications remain open and are
not performed here:

- **B1** — independent adjudication of the K7 instrument lineage;
- **B3** — Rule-C ruling on whether P4X obligations C4 and C5 survive P4X's
  governance `FAIL`.

Current independent status of the line, unchanged by this record:

```text
P4                    PARTIAL   (historical, immutable)
P4Z successor line    SCIENTIFICALLY_COMPLETE_GOVERNANCE_INCOMPLETE
P4 scientific line    CLOSABLE_WITH_REMAINING_OBLIGATIONS
```
