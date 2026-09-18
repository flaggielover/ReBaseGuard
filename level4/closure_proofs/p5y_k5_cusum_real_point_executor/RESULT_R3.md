# Real point executor r3: result

**Status: `REAL_POINT_EXECUTOR = PARTIALLY_QUALIFIED`.** The r3 frozen qualification is green (21/21 gates) and the
read-only `check` passes. The independent static review returned **FAIL**:
- **D2, D3, D4 = CLOSED**;
- **D1 = OPEN**, because the integrated real launch path cannot satisfy the frozen verifier.

External authorization must not be sought.

`EXECUTION_AUTHORIZED = false` · `REAL_INPUT_ARITHMETIC_GUARD = DENY` · `REAL_CELL_EXECUTED = NO` ·
`SCIENTIFIC_K5_PROBE_RUN = NO`

`RESULT.md` is the r2 result from publication `b4f1315f`. It is preserved unchanged; this file is the r3 result.

## Commits and hashes

| item | value |
|---|---|
| r3 specification (before code) | `a5d63e71` |
| **EXECUTOR_R3_FREEZE_COMMIT** | `2b9fdf8d` |
| **EXECUTOR_R3_QUALIFICATION_COMMIT** | `b2930bb2` |
| **EXECUTOR_R3_IDENTITY** | `f6ac26767b034e9b44269bba82bab1c4523187b6a8d8a424f3c3dec2347db1d1` |
| **PROTOCOL_R3_HASH** | `390c2a681ef2604fc956c749b9dc8dfa3b94b316038409e8594c62e8a31cda5d` |
| qualification result sha256 | `d06abeda67b60acac3f9bfecd41edbf1c538415ad387af7f5cca51a463a37598` |
| RUN_PROVENANCE.json sha256 | `288f700f320278612303f400606ddfdb25c1612b4bba2c19e800375bf46c3811` |
| science preregistration sha256 | `9ace6896…780a` (unchanged) |
| preserved | r2 freeze `52769488`, r2 evidence `57b51a6f`, r2 review/RESULT `b4f1315f`, r1 files |

## Frozen qualification

The run used a clean detached checkout of `2b9fdf8d` on rebaseguard-vultr-02, with provenance mode
FROZEN_QUALIFICATION and an empty porcelain before and after.

- **Gates:** 21/21 PASS. EG01–EG17 are inherited; EG18 (D1 in-process prelaunch), EG19 (D2 lifecycle and ledger), EG20
  (D3 recovery) and EG21 (D4 provenance) are new.
- **Mutations:** E 16/16, P 4/4, D01–D04 + A01–A03 7/7, L01–L04 + V01 5/5, R01–R02 2/2, C01 1/1.
- **Suites:** D1 50/50 rows, D2 35/35, D3 33/33.
- **Deterministic replay:** `cb28b972…` twice, with 0 scientific leaf differences. It is identical to r2, so no
  scientific leaf changed.
- **Order-2 replay:** identical to RUNG_256.
- **Other inherited checks:** CRAMER contract PASS; the smoke formed no enclosure; runtime identity matches.
- **Cost:** 6426.4 CPU-s per attempt and 19279.2 for the campaign, within the frozen 9000 / 32400 ceilings.
- **`check`:** 0 problems, including the final provenance validation.

## Independent review: FAIL

`review/EXECUTOR_STATIC_REVIEW_R3.md` (verbatim).

- **ACCEPTED_R2_SEMANTICS_UNCHANGED = YES**, **R2_ARTIFACTS_PRESERVED = YES.**
- **D2 CLOSED:** the `slot-N` marker model is the frozen one; writes are atomic and no-overwrite; there is exactly one
  terminal marker, and no COMPLETE without a valid seal; VOID is sealed only for the preregistered classes; the ledger
  reconciliation follows the frozen P09 / P11 semantics.
- **D3 CLOSED:** recovery classifies slots A–E, never launches or recomputes, never infers completion from process
  absence, and fails closed on a torn state; all crash boundaries were tested on both boots, plus a live crash.
- **D4 CLOSED:** `RUN_PROVENANCE.json` is present, complete and validated by `check`.
- **D1 OPEN.** The r2 sub-defects are repaired:
  - the frozen verifier is called in process with its defaults;
  - its returned object is what Q01 consumes, and there is no operator-report path;
  - the verifier source is bound;
  - the authorization is identified by its file bytes and re-hashed;
  - the executor binding chain holds.

  But the reviewer found three load-bearing integration defects. **I verified all three against the frozen verifier
  source.**
  - **N1 (critical).** The supervisor creates `slot-N` and writes RUN_STATE *before* the child runs the in-process
    verification. The frozen P11 requires every existing slot to already carry exactly one LAUNCH_NOTICE and one
    OUTCOME, so every supervised real launch is refused, and each refusal consumes a launch slot.
  - **N2 (critical).** The defence-in-depth guard call in `CusumPointBackend.prepare_point` now runs the full verifier
    *after* ARITHMETIC_STARTED. It would always refuse (the slot then exists), and that refusal would be sealed as an
    INTEGRITY VOID. That VOID permanently blocks the protocol. A network failure of the verifier's `git ls-remote` at
    that point would do the same.
  - **N3 (high).** Real mode admits a missing slot without a supervised RUN_STATE, so the only launch that passes the
    first verification is an unsupervised one, which then reaches N2.

  All three fail closed, so no wrong science is possible. The frozen prelaunch contract, however, cannot be met.
- **Lower findings:**
  - N4: an orphaned child is not covered by the liveness check.
  - N5: seal tmp files are not removed on failure.
  - N6: OOM labelling.
  - N7: countersignature ordering and publication.
  - N8: the prelaunch report details are not persisted.
  - N9: documentation drift (the README pointed to `RESULT.md` for r3, now pointed to this file; TRUST_MODEL wording;
    the guard `rule` text; the spec's L01–L03 against the implemented L01–L04).
  - N10: the frozen P08 basenames do not cover the r3 executor.
  - N11: provenance check gaps.
- **Accepted scope limitations:**
  - the host is not an independent trust root;
  - the real-mode assembly can only be judged statically under DENY;
  - reviews are not proofs;
  - Arb and the 53-bit CRAMER construction are stated assumptions.

## What a repair needs (for a later successor; not done here)

The reviewer's repair is local and changes no science:
- run the single in-process verification before `slot-N` exists, then create the slot and RUN_STATE, and admit only
  that RUN_STATE;
- make the `prepare_point` re-check a pure check of the bound decision (the guard policy plus the authorization
  re-hash);
- require RUN_STATE in real mode;
- add one end-to-end positive-path qualification row on a **synthetic** git repository and namespace (supervisor →
  `verify` → LAUNCH_PERMITTED → ARITHMETIC_STARTED with a manufactured backend), so that the launch integration is
  demonstrated rather than only its refusal paths.

## Next step

`REPAIR_REAL_POINT_EXECUTOR`. Do not seek or activate external authorization while D1 is open.
