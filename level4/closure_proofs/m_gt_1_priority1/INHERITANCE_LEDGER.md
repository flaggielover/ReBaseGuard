# Inheritance and immutability ledger

## Policy

Track 1B is immutable prior evidence and a regression anchor. This campaign
does not modify it and does not count a Track 1B deliverable as a new campaign
gate. The hashes frozen in `manifest.json` are checked by the campaign verifier.

## Classification

| Source | Use here | Classification |
|---|---|---|
| `level4/closure_proofs/m_gt_1_track1b/` | Compare theorem notation, pathwise decomposition, and regression results | Read-only prior evidence; not closure evidence |
| `level4/stage_d/STAGE_D_PROTOCOL.md` | Authoritative ordinary-stop truncated-window convention | Frozen scientific definition |
| `level4/stage_d/notes/CORRESPONDENCE_AUDIT.md` | Historical diagnosis of the Stage A/Stage D mismatch | Frozen prior audit |
| `level4/stage_d/results/d2_3_derivative.json` | Preserve historical D2.3 failure | Immutable failed gate |
| `level4/closure_proofs/m_gt_1_track1a/results/decision.json` | Preserve Track 1A failure | Immutable failed gate |
| `rebaseguard-lean/RebaseguardLean/IntegralBridge.lean` | Generic dominated stopped-integral derivative interface | Reused Level 1--3 Lean infrastructure |
| `rebaseguard-lean/` pinned toolchain | Compile the new independent Lean source | Reused build infrastructure |
| `level4/src/rebaseguard_level4/frozen.py` | Semantic regression target for constants and one-step recurrence only | Read-only implementation anchor |

## Newly established in this campaign

- the full definition audit;
- the standalone theorem and proof;
- the numerical protocol and independent CUSUM implementation;
- the frozen finite-support witness and Arb certificate;
- the independent Lean proof spine in the new namespace;
- cross-representation correspondence and focused regression tests;
- the five-category closure decision.

The new numerical implementation does not import Stage D or Track 1B
scientific evaluators. The new Lean file does not import the Track 1B Lean
source. Any generic infrastructure import remains visible in source and in
`LEAN_CORRESPONDENCE.md`.
