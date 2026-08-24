# Final report — prior-art / novelty verification

## Scoped decision

> **NOVELTY-VERIFICATION-CLOSED**  
> **N2 — PARTIAL-OVERLAP-FOUND-CLAIMS-NARROWED**

The search requirement is closed as documentation/provenance. This is not a
positive priority finding and does not change a historical scientific result.

## Coverage

- completed scholarly indexes: Crossref, OpenAlex
- additional inspection sources: DOI/publisher pages, arXiv/Project Euclid, Springer, ACM/IEEE metadata, open repository copies
- unavailable primary indexes: Google Scholar, Semantic Scholar (recorded `ACCESS-UNAVAILABLE`)
- mandatory families: 7A, 7B, 7C, 7D, 7E, 7F, 7G, 7H, 7I
- primary unique candidates screened: 1251
- unique non-seed snowball candidates screened: 1241
- combined unique candidate works inspected after DOI/title deduplication: 2445
- included works individually classified: 33
- DIRECT: 0
- HIGH-PARTIAL: 9 (W01, W03, W05, W06, W08, W10, W14, W25, W33)
- snowball: two rounds, no new DIRECT/HIGH-PARTIAL in either round

## Finding

Strong partial overlap exists in self-starting/adaptive CUSUM, adaptive SR,
post-CUSUM estimation bias, nonanticipating unknown-parameter detection,
multi-cyclic detection, forgetting/reset systems, and adaptive drift windows.
The strongest paper-level neighbor is W08. The strongest practical neighbor is
W25. Neither covers the complete stopping-selected post-alarm cross-cycle
reference reuse mechanism together with C3-C9.

Current claims were narrowed. Adaptive reference updating, post-alarm
estimation, repeated detection, reset maps, and adaptive reference windows may
not be described as if introduced by ReBaseGuard.

## Mechanical closure criteria

- NV1: PASS
- NV2: PASS
- NV3: PASS
- NV4: PASS
- NV5: PASS
- NV6: PASS
- NV7: PASS
- NV8: PASS
- NV9: PASS
- NV10: PASS
- NV11: PASS
- NV12: PASS

## Protected status

- historical Stage-F verdict: `LEVEL-4-PARTIAL` — unchanged
- current post-closure global verdict: `LEVEL-4-PARTIAL` — preserved, not recomputed
- D4: `D4-PHASE-MAP-CLOSED` — unchanged
- external validation: untouched
- original L4R-16 requirement: `CLOSED`
- remaining fail/open blocker: `SEMI-REAL EXTERNAL VALIDATION` (scientific)
