# Pre-data audit

**Date:** 2026-08-22  
**Repository head:** `c13b838e025efe034d743d1e1eccc9b3715088bc`  
**Historical artifacts modified:** no

## Repository and previous-track status

- `main`, `origin/main`, and `HEAD` matched at the audit boundary.
- The worktree was clean before the audit.
- The prior protocol SHA-256 was
  `27c3cddad3a09520a562b444e9635a3f4155464ac322f01edc79e0fc74c2d9af`.
- Every artifact listed in the previous track's
  `results/artifact_manifest.json` matched its recorded SHA-256.
- The previous `reproduce.sh --resume` completed successfully and reproduced
  its expected numerical `FAIL` and decision `MGT1-THEOREM-PARTIAL`; its
  46 isolated tests passed.
- The reproduction command rewrote only the stored `git_head` metadata in its
  generated JSON. That metadata-only rewrite was restored to its manifest
  value, leaving the historical artifact byte-identical and the worktree clean.
- The authoritative `scripts/verify_level_4.sh` suite passed all 695 tests.

## Frozen historical hashes

| Artifact | SHA-256 |
|---|---|
| `level4/stage_d/STAGE_D_PROTOCOL.md` | `925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e` |
| `level4/stage_d/notes/CORRESPONDENCE_AUDIT.md` | `985018981b11e2030128e5d4cb78f08e803155c6ed4fdbbbdb48c96001f6c2c2` |
| `level4/stage_d/notes/D2_3_STEP_PRECOMMIT.md` | `7b7a54c64f4c86334415a03cd45797e7cb8b923d378fa90180a71f1831588dea` |
| `level4/stage_d/results/d2_3_derivative.json` | `ea1d026384866de0fc5ad0ded3e68f159d32deaa3be24505aab449b73db8e020` |
| `level4/stage_f/LEVEL4_REQUIREMENTS_RECONSTRUCTION.md` | `41ea8cd6a33f430be44d66376df60efc979b6dda5f00308616a519b7ece6a106` |

## Exact reconstruction of the previous stop

The prior track's primary derivative correspondence passed for all eight
window lengths. The complete frozen gate nevertheless failed two auxiliary
checks:

1. no `tau=1` event appeared in two million paths at `m=2`, where the exact
   event probability is only `3.7979e-8`; and
2. a frozen five-SE-per-cell Stage-A/Stage-D map-separation rule failed in both
   `m=20` replications (`4.73` and `3.20` SE), although both estimates had the
   expected sign and their pooled separation was `5.61` SE.

The `m=100` cells passed that old auxiliary rule (`49.05` and `46.88` SE).
The old gate is not changed, reinterpreted, or reused by Track 1A.

## Definition audit retained

Stage A uses the dwell stop `tau_m = inf {t >= m : alarm at t}` and a full,
fixed-denominator `m`-window. Stage D uses the ordinary stop
`tau = inf {t >= 1 : alarm at t}` and denominator `min(m,tau)`. Thus there are
two distinct sources of difference for `m>1`: the stopping time and the
short-cycle normalization. They coincide at `m=1`.

Historical Stage-D D2.3 remains `FAILED`; Stage F remains
`LEVEL-4-PARTIAL`.
