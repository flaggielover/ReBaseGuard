# ReBaseGuard Level 1–3 Closure — Progress Checkpoint

**Status: COMPLETE.** All twelve phases finished on 2026-08-20.
Decision: `LEVEL 1–3: CLOSED`. Authoritative document:
[`LEVEL_1_3_CLOSURE_REPORT.md`](LEVEL_1_3_CLOSURE_REPORT.md).

This file is retained as the interruption-safety / resumption record.

**Project root:** `/Users/suzhe/ReBaseGuard`
**Lean repo:** `/Users/suzhe/ReBaseGuard/rebaseguard-lean`

---

## Phase status

| # | Phase | Status | Artifact |
|---|---|---|---|
| 0 | Relocation health check | **PASS** | — |
| 1 | Evidence inventory | **DONE** | `ARTIFACT_INDEX.md` |
| 2 | Frozen model audit | **DONE — no mismatch** | `01_FROZEN_MODEL.md` |
| 3 | Theorem / claim map | **DONE** | `02_THEOREM_MAP.md` |
| 4 | Lean verification | **DONE — PASS** | `03_LEAN_VERIFICATION.md` |
| 5 | Lean semantic correspondence | **DONE — 17/17** | `03_LEAN_VERIFICATION.md` |
| 6 | Arb certificate audit | **DONE — CERTIFICATE REPRODUCED** | `04_ARB_CERTIFICATE.md` |
| 7 | Numerical validation | **DONE** | `05_NUMERICAL_VALIDATION.md` |
| 8 | Claim ledger | **DONE — no known overclaim** | `06_CLAIM_LEDGER.md` |
| 9 | Reproducibility | **DONE — script written and run, exit 0** | `07_REPRODUCIBILITY.md`, `../scripts/verify_level_1_3.sh` |
| 10 | Limitations | **DONE** | `08_LIMITATIONS_AND_BOUNDARIES.md` |
| 11 | Final closure report | **DONE** | `LEVEL_1_3_CLOSURE_REPORT.md` |
| 12 | Repository / git audit | **DONE** | `LEVEL_1_3_CLOSURE_REPORT.md` §12 |

---

## Commands run, with exit codes

| # | Command | Cwd | Exit | Note |
|---|---|---|---|---|
| 1 | stale-path grep × 4 variants (incl. `.git`/`.lake`, binary-as-text) | ReBaseGuard | 1 | no hits — relocation clean |
| 2 | `lake build` | rebaseguard-lean | **0** | 8717 jobs |
| 3 | `lake env lean RebaseguardLean/<M>.lean` × 9 modules + root | rebaseguard-lean | **0 ×10** | 5 / 261 / 246 / 222 / 259 / 213 / 217 / 211 / 222 / 238 s |
| 4 | bypass scan `grep -rni {sorry,admit,axiom,unsafe,native_decide}` | rebaseguard-lean | — | **0 matches, all five** |
| 5 | `lake env lean AxFull.lean` (9 × `#print axioms` + `#check`) | rebaseguard-lean | **0** | all `[propext, Classical.choice, Quot.sound]` |
| 6 | `python -m rebaseguard_certify.audit proofs/certificate.json` | rebaseguard-proof | **0** | 129 s, full replay PASS, bit-identical |
| 7 | `pytest -q` | rebaseguard-proof | **0** | 90 passed |
| 8 | `python scripts/run_diagnostics.py` | rebaseguard-proof | **0** | stored fields bit-identical; artifact restored |
| 9 | `scripts/verify_level_1_3.sh` (first run) | ReBaseGuard | 1 | **my own** sanity check wrongly asserted `Γ_lower = b̂ − E_b` exactly |
| 10 | `scripts/verify_level_1_3.sh` (after fixing the check) | ReBaseGuard | **0** | 543 s, `RESULT: ALL CHECKS PASSED` |

Run 9 → 10 is worth keeping in the record: the failure was in the verification
script, not the certificate. The stored interval is *wider* than `b̂ ± E_b` by
`5.28e-8` (radius rounded outward to the dyadic `11.962516963481903076171875`),
exactly symmetric about `b̂(0,0)` — conservative, not defective. The check now
asserts containment plus symmetry.

Session logs: `/private/tmp/claude-501/-Users-suzhe-ReBaseGuard-rebaseguard-lean/64639ea3-1e66-4fcb-aec9-4b3420c8919f/scratchpad`

---

## Evidence verified

**Lean** — `lake build` exit 0; all 10 modules elaborate from source, exit 0, no
errors; bypass scan completely clean; 9/9 theorems on baseline axioms; final
theorem `#check` matches the frozen model literal-for-literal (`k = 1/2`,
`h = 5`, `iIndepFun X μ`, `μ.map (X j) = gaussianReal 0 1`); 17/17 semantic
correspondence items pass. Toolchain `v4.34.0-rc1`, Mathlib `de5ce8a9…`.

**Arb** — `CERTIFICATE REPRODUCED`: full replay, exit 0, 129 s, `status: PASS`,
`Γ ∈ [3.9243482005828971282…, 27.8493821275467032805…]`, `Gamma_lower_gt_2: true`,
endpoints bit-identical, regenerated `audit_report.md` byte-identical
(SHA-256 `034ccb1b…2238d7b`), all 5 pinned artifact hashes OK, model enforced as
exact rationals `k=1/2`, `h=5/1`, target enforced as `E[Z_tau*T_tau]`.

**Numerics** — 90/90 tests; MC `Γ ≈ 15.9619 / 15.9010` (seeds 1729 / 20260818,
`n = 200 000`), both inside the certified interval ≈12 SE above its lower
endpoint; finite Arb Bellman `18.7401…` inside (auditor-enforced);
`gamma_table.csv` internally consistent (`F₁'(0) = 1−Γ` and `ρ_c = 1/|F₁'(0)|`
hold at all 12 rows).

**Model** — no substantive mismatch across human derivation, Python model, Arb
certificate and Lean formalization.

---

## Artifacts created

`closure/` (11 files) · `scripts/verify_level_1_3.sh` · `README.md` (new root
navigation; there was no prior root README).

**No pre-existing file was modified.** `rebaseguard-proof/proofs/audit_report.md`
and `rebaseguard-proof/diagnostics/reference.json` were rewritten by reproduction
runs and verified/restored byte-for-byte identical.

---

## Current blocker

NONE.

---

## Exact next action

**Stop.** Level 1–3 closure is complete and Level 4 is not authorized.

The only outstanding *recommendation* (not executed, requires authorization) is
the repository freeze in `LEVEL_1_3_CLOSURE_REPORT.md` §12 — most urgently,
committing the Lean sources, which currently exist only as untracked
working-tree files in a repository with zero commits.
