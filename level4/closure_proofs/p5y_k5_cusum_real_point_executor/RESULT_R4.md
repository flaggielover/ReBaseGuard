# Real point executor r4: result

**Status: `REAL_POINT_EXECUTOR = PARTIALLY_QUALIFIED`.** Everything r4 was asked to repair is repaired:
- the independent review rules **N1 = N2 = N3 = CLOSED, D1 = CLOSED**, and D2, D3 and D4 remain CLOSED;
- the frozen qualification is green (22/22 gates) and the read-only `check` passes.

The review verdict is nevertheless **FAIL**. It is caused by one **new** load-bearing finding, **X1**, which r4 exposed
by making the governed launch path reachable. External authorization must not be sought.

`EXECUTION_AUTHORIZED = false` · `REAL_INPUT_ARITHMETIC_GUARD = DENY` · `REAL_CELL_EXECUTED = NO` ·
`SCIENTIFIC_K5_PROBE_RUN = NO`

`RESULT.md` (r2) and `RESULT_R3.md` (r3) are preserved unchanged.

## Commits and hashes

| item | value |
|---|---|
| r4 specification (before code) | `b0e3f6c6` |
| **EXECUTOR_R4_FREEZE_COMMIT** | `77afd942` |
| **EXECUTOR_R4_QUALIFICATION_COMMIT** | `d64bcd10` |
| **EXECUTOR_R4_IDENTITY** | `47f3557b51f8db53fcd84865426edfe6387dffffca2d6d513ad0b9e910e5b8d2` |
| **PROTOCOL_R4_HASH** | `1a62e5d1e2094da800743a1b189c2a4d8a07621c9581278133b0e2d19f2b1012` |
| qualification result sha256 | `d8982c74937dcb6c089e4fd93d931274b56c00ad19ed412d8655f1b09ac3185e` |
| RUN_PROVENANCE.json sha256 | `6e6282b0a23fdad212db1adfda7b40aad5daee3cab7a453ebf5d38cadea12240` |
| science preregistration | `9ace6896…` (unchanged) |
| preserved | r3 `a5d63e71` / `2b9fdf8d` / `b2930bb2` / `34bb9b0b`, and all r1/r2 artifacts |

## What r4 changed (EXECUTOR_SPEC_R4.md)

- **N1: one authoritative decision, before the slot exists.**
  - The supervisor takes the only authoritative pre-arithmetic decision (the frozen `prelaunch_verify.verify`, in
    process, with its defaults) before `slot-N` exists.
  - REFUSED, or any verifier exception, returns `PRELAUNCH_REFUSED` with no slot, no RUN_STATE and no VOID.
  - After PASS, the decision (with the full frozen report) is bound into RUN_STATE.
- **N2: a pure re-check, and a fence.**
  - The child and backend guard is a pure re-check of that bound decision: no git, no network, no ledger, no slot and
    no verdict.
  - A post-start fence makes the full verifier unreachable after ARITHMETIC_STARTED. Reaching it is an executor defect,
    never sealed as VOID.
  - The only verifier call site is the supervisor (an AST fence).
- **N3: the supervisor is required in real mode.** A real or governed attempt needs a supervised slot and a matching
  RUN_STATE (attempt_uid, decision digest, supervisor pid and exact argv).
- **A permitted synthetic governed launch, end to end.**
  - The unmodified frozen verifier returns LAUNCH_PERMITTED (P01–P12). The chain is: slot → RUN_STATE → child pure
    re-check → manufactured arithmetic → seal → RUN_COMPLETE → ledger reconciliation.
  - It runs in throwaway synthetic clones with SYNTHETIC governance commits that are never pushed.
  - Only two things are virtualised: the network publication read (a `git` shim), and the preregistered namespace (a
    private mount namespace with an overlay over `/root/work`). The real namespace was never created.

## Frozen qualification

The run used a clean detached checkout of `77afd942` on rebaseguard-vultr-02, with provenance FROZEN_QUALIFICATION and
an empty porcelain.
- **Gates:** 22/22 PASS. EG01–EG21 are inherited (including the D1–D4 suites as regressions); EG22 is the governed
  launch.
- **Mutations:** E 16/16, P 4/4, D01–D04 + A01–A03 7/7, L01–L04 + V01 5/5, R01–R02 2/2, N01–N05 5/5, C01 1/1.
- **Suites:** D1 50/50 rows, D2 36/36, D3 33/33, governed 17/17.
- **Replay:** `cb28b972…` twice with 0 scientific leaf differences, identical to r2 and r3.
- **Other checks:** the order-2 replay is identical to RUNG_256; the CRAMER contract passes.
- **Cost:** 6462.7 CPU-s per attempt and 19388.1 for the campaign, within 9000 / 32400.
- **`check`:** 0 problems.

## Independent review: FAIL on X1 only

`review/EXECUTOR_STATIC_REVIEW_R4.md` (verbatim).

- **Rulings:** N1, N2, N3, D1, D2, D3 and D4 are all CLOSED.
- **Preservation:** ACCEPTED_R3_SEMANTICS_UNCHANGED = YES; PREDECESSOR_ARTIFACTS_PRESERVED = YES.
- **The reviewer ruled** that a pre-slot PRELAUNCH_REFUSED is consistent with the frozen
  `retry_policy.attempt_start` and P11: a failed prelaunch verification is a precondition failure, not a launch. There
  is a literal-wording tension, and it is not load-bearing.

**X1 (medium, load-bearing): the launch slot is not bound to the slot the verifier approved.** I verified this
against the frozen verifier source.
- The frozen P11 approves launching only `slot_dir(len(entries)+1)` and checks the LAUNCH_NOTICE for that slot only.
- The supervisor launches the CLI's `--slot N`, checking only the namespace.
- The only slot binding is the countersignature's `attempt_slot`, which never reads the ledger.
- **Consequence.** If a countersignature and a CLI both name slot 2 while the ledger names slot 1, the launch passes
  verification for slot-1 and then runs real arithmetic in an un-noticed slot-2. Its sealed record would be final, and
  P11 would refuse every later launch.
- **Fix (small, a pure read in the supervisor):** before verifying, require
  `slot.name == slot_dir(<existing slot dirs> + 1)` and exactly one committed LAUNCH_NOTICE naming that slot and this
  authorization's sha256. Add a qualification negative for the mismatch case.

**Lower findings, none load-bearing:**
- X2: the new D2 "prelaunch refused" row is refused by the namespace check rather than by DENY, and the supervisor's
  DENY branch is unexercised; `DEV_CALIBRATION.md` item 3 misdescribes the row.
- X3: a post-start verifier call is classified INTEGRITY_REFUSAL without a VOID. It is fail-closed and unreachable.
- X4: the `prepare_point` re-check runs after ARITHMETIC_STARTED, so a mismatch there seals VOID rather than failing
  "before arithmetic" as the spec says.
- X5: documentation still describes the r3 design (TRUST_MODEL, docstrings, the guard `rule` text).
- X6: evidence granularity of the mutant and fence rows.
- X7: the child re-check does not re-read HEAD.
- X8: `governed_manufactured` is a production mode; TRUST_MODEL should forbid non-`real` modes on the execution host
  after activation.

**Accepted scope limitations:**
- the host is not a trust root (an operator can forge a coherent RUN_STATE);
- the real GitHub `ls-remote` is not exercised end to end;
- the governed real backend is covered only statically and by unit rows, since no real arithmetic may run before
  authorization.

## Next step

`REPAIR_REAL_POINT_EXECUTOR`: an additive r5 for X1 (plus the cheap X2/X5 corrections). Do not seek or activate
external authorization while the review verdict is FAIL.
