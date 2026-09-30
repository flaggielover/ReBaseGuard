# Independent package review R3 of the P309 formal-campaign package (candidate)
PACKAGE_REVIEW: PENDING (declaration written before any run; this line is replaced by the verdict)

## 0. Reviewer execution declaration (written 2026-09-30T00:19Z, before any run beyond read-only checks)

Reviewed state: HEAD `f1f8a459` (package content commit `ce829bb4`, manifest commit `65b64e9e`, brief `b48a1fa2`),
clean tree. I am neither the R1 nor the R2 reviewer and have no stake in the outcome.

Rules I follow: `PYTHONDONTWRITEBYTECODE=1`; library calls only, never a `__main__` that writes evidence; the q309
exec and exposure ledgers redirected to `scratchpad/r3/` (`q309_guard.EXEC_LEDGER`, `EXPOSURE_LEDGER`); nothing
written in the repository except this file; no git write. I do not open `ledger/EXPOSURE_LEDGER.jsonl` or
`ledger/INCIDENT_*`, any file outside NS, or the NS files most likely to carry 305–309 numbers
(`dossier/CELL309_DOSSIER.md`, `dossier/digests/*`, `dossier/sources/READER_A_*`, `dossier/ROUTE_MATRIX.md`).

| id | what | kernel / geometry / drift | evaluates? |
|---|---|---|---|
| RD3-0 | Read-only checks: git metadata (`rev-parse`, `ls-tree`, `log`, `diff --stat`, `merge-base`); for pins outside NS, the blob id by tree lookup only (no content read, no sha256 of their bytes); sha256 of NS committed blobs and working-tree files; JSON metadata of NS decoy evidence (rung status, runtime seconds) and `verify/VERIFY_RESULTS.json` (settings, timing); the dangling NS commit `5ddf7b58` (manifest tool) | none | no |
| RD3-1 | `code/self_audit.py`: `run("r3")` in-process through a scratch wrapper. Its A10 subprocess (`code/verifier_probe_envelope.py`) is replaced by a scratch wrapper that runs the same `main()` with the one output write redirected to scratch. Audit JSON to scratch. Includes the tool's own git reads and `git ls-remote origin` (a network read) | none (A10 rebuilds probe dicts only) | no |
| RD3-2 | `code/verifier_probe_envelope.py` `main()` stand-alone through the same wrapper (output to scratch) | none | no |
| RD3-3 | NS tests via their `run()` functions, in-process, ledgers redirected: `test_q309_guard`, `test_srk_gate` (constructed objects, h = 3), `test_srk_adapter` (manufactured objects), `test_srk_assembly_twosided` (exact algebra), `test_srk_envelope` (real-kernel envelope primitives, drifts in [0, 1/2]) | real kernel only at e ∈ [0, 1/2] (envelope primitives); otherwise none | envelope primitives only |

Not run: any producer or verifier on any certificate; `test_srk_port_identity` and `test_srk_fsm_truth` (they import
overnight modules outside NS; not needed here); `e2e_cell_family`, `srk_mc_control`, `test_srk_cert_mutants`,
`test_verify_selftests`, `run_verify_all`, `build_evidence_manifest`. Nothing touches cells 305–309 or evaluates any
drift in [6/5, 13/5] or its mirror.
