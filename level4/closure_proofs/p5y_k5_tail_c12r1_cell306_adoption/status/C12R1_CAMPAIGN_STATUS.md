# C12-R1 / overnight K5 tail campaign: STOPPED at qualification (QUALIFICATION_REJECTED)

**Stop rule applied.** The campaign instruction says: "If rejected, preserve the rejection and STOP THE ENTIRE OVERNIGHT
CAMPAIGN."
- The C12-R1 qualification review returned `QUALIFICATION_REJECTED` with one blocker. It is preserved verbatim at
  `review/C12R1_QUALIFICATION_REVIEW.md` in commit `e89402c1`, together with the reviewer's verifier rerun and decoy-only
  probe.
- Phase A2 (grant and execution), Phase A3 (adjudication) and Phase B (cells 307–309) were **not** entered.

## Commits of this campaign (in order, starting from eba56027)

| commit | what |
|---|---|
| `5cfe336a` | C12-R1 FREEZE: driver, verifier, r6 generator, grant generator, protocol, freeze record |
| `2e7bc7d6` | qualification at the freeze commit: PASS 115/115 |
| `e89402c1` | qualification review QUALIFICATION_REJECTED (blocker B1 of C12-R1), preserved verbatim |
| this commit | this status record |

C12's artifacts (`b9ffc87f`, `aac6dae9`, `2cdfa467`, `eba56027`) are unchanged.

## Computations actually executed

All ran on this machine.
- **Driver preflight.**
- **The I1 control** for cell 306 and the non-target cell 305, run several times: by the verifier, in its sandboxes and
  by the reviewer. Every run reproduces C2's committed pre-N9 records exactly, including C2's per-supply records.
- **Decoy target evaluations** on synthetic I2 values: by the verifier in its sandbox B and in a scratch clone, and by the
  reviewer in its own decoy sandboxes.
- **No computation under the real S_I2 took place:**
  - Γ(5, 306; S_I2) with real I2 constants: **0** evaluations.
  - `refs/c12r1/*` and `refs/c12/*`: **absent**.
  - Grant: **never created**. Result: **absent**.

## Blocker (C12-R1 review B1)

**What happens.**
- The driver writes its result through `evidence/execution/C12R1_CELL306_RESULT.tmp`.
- `.gitignore:60` ignores `*.tmp`, so the clean-tree check cannot see an object planted at that path. No check before the
  marker looks at it either.
- `write_result`, and any seal failure that is not a `Refusal`, run outside the post-marker handler.

**Consequences, reproduced on decoys only:**
- a directory at that path makes the one evaluation unsealable;
- a symlink at that path diverts the full result outside the repository while the driver reports SEALED.

**What it does not allow:** a second evaluation, or an evaluation outside the marker.

## Repair needed (a C12-R2 successor freeze; not performed: stop rule)

1. **Before the marker:** refuse if the `.tmp` or the `.json` result path exists in any form (`os.path.lexists`),
   including symlinks and directories. Also run the clean-tree check with `--ignored`, restricted to the namespace.
2. **Write the result exclusively and without following symlinks:** `O_CREAT|O_EXCL|O_NOFOLLOW` and fsync, then an
   atomic rename checked with `lstat`. Verify the written bytes before sealing, and refuse a symlink or non-regular
   result anywhere in `seal-only`.
3. **After the marker:** bring `write_result` and every sealer failure (any exception) under recorded, sealable handling.
   The `seal-only` path must be able to recover from each of them.
4. **Decoy tests:**
   - a directory at the `.tmp` path;
   - a symlink at the `.tmp` path;
   - a symlink or directory at the `.json` path;
   - a sealer raising a non-Refusal error.
5. **Review notes to carry:**
   - N1: narrow the protocol's claims.
   - N2: add a committed test planting this campaign's own result at the freeze state.
   - N3: `--review` checks that the code it runs equals the freeze and requires a clean tree.
   - N4/N6: add the missing grant-variant and r6 tests.
   - N7: confine the r6 generator's `--out` to evidence/coverage/, and check `cell == 306` and the marker target.
   - N8: enforce `-I -S -B` through `sys.flags`.
   - N9: the grant generator requires `QUAL_REL` and a sanitized environment.
   - N10: list the G07 soundness evidence for the adjudicator to verify.
   - N11: an exact recheck of the Lemma-G substitution.

## Prospective coverage table

| cell | scientific closure | applicable floor/rule | adoption | authoritative coverage |
|---|---|---|---|---|
| 306 | S_I1: Γ < 0 (C2, historical; reproduced). S_I2: **not evaluated** | floor r2 (F1′ undetermined) | not adopted | OPEN (r5) |
| 307 | not closed (historical) | none assessed (Phase B not entered) | not adopted | OPEN (r5) |
| 308 | not closed (historical) | none assessed | not adopted | OPEN (r5) |
| 309 | not closed (historical) | none assessed | not adopted | OPEN (r5) |

**Governance state.**
- r5 is authoritative and unchanged (blob `f978eeb6`), and r6 does not exist.
- N9 is CLOSED and floor r2 is in force.
- **K5 = PARTIAL.** At m = 5 cells 306–309 are open.

**Branch refs.** They are recorded separately and were not synchronized: local main `c123b9bb`, remote main `1cb45382`.
