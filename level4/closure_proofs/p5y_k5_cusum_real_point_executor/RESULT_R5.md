# Real point executor r5: result

**Status: `REAL_POINT_EXECUTOR = QUALIFIED_AWAITING_EXTERNAL_AUTHORIZATION`.** r5 closes the single load-bearing r4
finding **X1** (the launch slot was not bound to the slot the frozen verifier approved):
- the frozen qualification passes 23/23 gates, and the read-only `check` passes with 0 problems;
- the independent review returns **PASS_WITH_SCOPE_LIMITATION** and rules X1, N1–N3 and D1–D4 all CLOSED.

This qualifies the executor for **external** authorization only. Nothing is authorized:

`EXECUTION_AUTHORIZED = false` · `REAL_INPUT_ARITHMETIC_GUARD = DENY` · `REAL_CELL_EXECUTED = NO` ·
`SCIENTIFIC_K5_PROBE_RUN = NO`

`RESULT.md` (r2), `RESULT_R3.md` and `RESULT_R4.md` are preserved unchanged.

## Commits and hashes

| item | value |
|---|---|
| r5 specification (before code) | `59bd3268` |
| **EXECUTOR_R5_FREEZE_COMMIT** | `a16d22b5` |
| **EXECUTOR_R5_QUALIFICATION_COMMIT** | `f83cd182` |
| **EXECUTOR_R5_IDENTITY** | `ef1c86e40bff0b13e40e924ba27d0841aff71f7344d114f71f517ab3adfdd41b` |
| **PROTOCOL_R5_HASH** | `59a91e20077ab14243e28d094a4ca5527bda692ec17e2f00108bf0f05dbd989a` |
| qualification result sha256 | `9c7ca7babdaba438b452aa98c7abbb7892d5ab1c11ffae67c47a854855b77229` |
| RUN_PROVENANCE.json sha256 | `f8cdba5b42f8083838183a989d174226cf6190eee560afebdd750e9d0913ff17` |
| science preregistration | `9ace6896…` (unchanged); the frozen protocol namespace is byte-unchanged |
| preserved | r4 `b0e3f6c6` / `77afd942` / `d64bcd10` / `327cc35e`, r3 `a5d63e71` / `2b9fdf8d` / `b2930bb2` / `34bb9b0b`, and all r1/r2 artifacts |

## What r5 changed (EXECUTOR_SPEC_R5.md)

The changes are in the supervisor only, plus one clause in the child's pure re-check. The mathematical code paths are
byte-identical to r4.

- **One canonical launch slot, derived before verification.**
  - `canonical_slot = slot_dir(number of slot-N directories + 1)`, exactly as the frozen P11 derives it.
  - Before the frozen verifier runs, the supervisor requires all of these to name that slot:
    - the CLI slot;
    - the countersignature's `attempt_slot`;
    - exactly one well-formed, non-stale LAUNCH_NOTICE naming this authorization's file-bytes sha256.
  - Any violation gives **SLOT_BINDING_REFUSED**: no verifier call, no slot, no RUN_STATE, no VOID, no address consumed.
  - Nothing falls back to, rewrites or auto-corrects the slot.
- **The authorization is bound through the notice and the countersignature.** The r4 authorization template has no
  slot field and admits no extra keys, so this is the only binding available.
- **A TOCTOU-bound launch state.**
  - The launch state is snapshotted before the verifier: namespace, ledger, authorization, countersignature and notice.
  - After PASS and before the slot is created, the state is re-derived and must be identical. The verifier's own P11
    approval must also name the same slot.
  - The snapshot is bound into the decision digest carried in RUN_STATE.
  - The child re-checks that the decision's canonical slot is its own slot.

## Frozen qualification

The run used a clean detached checkout of `a16d22b5` on rebaseguard-vultr-02, with provenance FROZEN_QUALIFICATION and
an empty porcelain.
- **Gates:** 23/23 PASS. EG01–EG22 are regressions (including N1–N3 and D1–D4); EG23 is the canonical launch slot.
- **X1 matrix:** 28 rows, all PASS:
  - integration rows in the synthetic governed clone (X1-01 permitted end to end, X1-02, X1-02b, X1-03, X1-06, X1-10);
  - pure rows (X1-04 to X1-08, malformed notice, outcome already present, non-contiguous or foreign namespace);
  - TOCTOU comparator rows and a static order row.
- **Governed rows:** 45/45.
- **Mutations:** E 16/16, P 4/4, D+A 7/7, L+V 5/5, R 2/2, N 5/5, **X 5/5** (X01 trust the CLI slot, X02 ignore the
  countersignature slot, X03 ignore the notice slot, X04 skip the post-verification re-check, X05 allow duplicate
  notices), C01 1/1.
- **Replay:** `cb28b972…` twice with 0 scientific leaf differences, identical to r2–r4. The order-2 replay is identical
  to RUNG_256.
- **Cost:** 6456.1 CPU-s per attempt and 19368.4 for the campaign, within 9000 / 32400.
- **`check`:** 0 problems.
- The real `/root/work/k5-first-real-probe` was never created.

## Independent review: PASS_WITH_SCOPE_LIMITATION

`review/EXECUTOR_STATIC_REVIEW_R5.md` (verbatim).
- **Closed findings:** X1, N1, N2, N3, D1, D2, D3 and D4 are all CLOSED.
- **Binding rulings:** CANONICAL_SLOT_BINDING, LAUNCH_NOTICE_BINDING, CLI_SLOT_CANNOT_OVERRIDE and
  TOCTOU_SLOT_STATE_BINDING all PASS.
- **Preservation:** ACCEPTED_SEMANTICS_UNCHANGED = YES; PREDECESSOR_ARTIFACTS_PRESERVED = YES.
- **X2–X8:** none is load-bearing.
- **New defects:** none load-bearing, only LOW items:
  - D-1: the notice `utc` format should be pinned in the activation runbook as ISO-8601 with an explicit offset;
  - D-2 and D-3: test-strength notes;
  - D-4 (INFO): falls under the accepted host limitation.
- **Operator-procedure notes for the activation runbook** (X8, D-1):
  - only `supervisor.py launch --mode real` may run on the execution host after activation;
  - the LAUNCH_NOTICE `utc` must carry an explicit offset.
- **Accepted scope limitations:**
  - the host is not a trust root;
  - the real GitHub `ls-remote` is not exercised end to end;
  - the positive end-to-end run used manufactured input, since no real arithmetic may run before authorization.

## Next step

`SEEK_INDEPENDENT_EXTERNAL_AUTHORIZATION`. That step belongs to an independent authority outside this task; nothing here
authorizes or activates execution.
