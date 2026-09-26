# C12 / overnight K5 tail campaign — status: STOPPED at qualification (QUALIFICATION_REJECTED)

**Stop rule applied:** the campaign instruction says to stop, not improvise, when a reviewer returns a blocking verdict or
qualification fails. The C12 qualification review returned `QUALIFICATION_REJECTED` with blocker B1. It is preserved
verbatim at `review/C12_QUALIFICATION_REVIEW.md`.
- Phase A (cell 306) has not reached an adjudication.
- Phase B (cells 307–309) is not authorized, because it may start only after Phase A has a final preserved adjudication.
  No Phase-B audit, design or computation was started.

## Commits of this campaign

| commit | what |
|---|---|
| `b9ffc87f` | FREEZE: driver, verifier, r6 generator, protocol, freeze record |
| `aac6dae9` | qualification at the freeze commit: PASS 71/71 (its message was amended once before anything referenced it; the tree is unchanged, see review N10) |
| `2cdfa467` | the qualification review, QUALIFICATION_REJECTED (B1), preserved verbatim |
| this commit | this status record |

## Computations actually executed

All ran on this machine, each taking seconds.
- **Driver `preflight`:** checks bindings only.
- **Driver `rehearse`:** the I1 control for cell 306 and for the non-target cell 305. Both reproduce C2's committed,
  pre-N9 records exactly.
- **Verifier (the qualification run):** static checks, sandbox negative controls, synthetic r6 rehearsal, leak scans. No
  target was evaluated.

**Γ(5, 306; S_I2) was never computed.** Exactly-once state:
- target evaluations: **0**;
- `refs/c12/cell306-target-consumed`: **absent**;
- result artifact: **absent**;
- grant: **never created**.

## Prospective coverage table

| cell | scientific closure | floor r2 eligibility | adoption adjudication | authoritative coverage |
|---|---|---|---|---|
| 306 | S_I1: Γ < 0 (C2, historical; reproduced exactly by the control). S_I2: **not evaluated**. | undetermined: F1′(d) needs Γ(S_I2) | none | OPEN (r5) |
| 307 | not closed (historical) | not assessed (Phase B not authorized) | none | OPEN (r5) |
| 308 | not closed (historical) | not assessed | none | OPEN (r5) |
| 309 | not closed (historical) | not assessed | none | OPEN (r5) |

**Governance state:**
- r5 is authoritative and unchanged (blob `f978eeb6`), and r6 does not exist.
- N9 is CLOSED and floor r2 is in force.
- **K5 = PARTIAL.** At m = 5 cells 306–309 are open.

## Repair needed (a C12-R1 successor freeze; not performed: stop rule)

The review names B1 and a fix. Every item below changes frozen code, so it requires a successor freeze, then a fresh
qualification and a fresh review.

1. **Verifier sandbox.**
   - Build the sandbox at the freeze commit, never at HEAD.
   - Refuse to run at all once HEAD's tree contains `authorization/` or an accepted qualification review, or once any
     `refs/c12/*` exists.
2. **Driver: seal preconditions before consumption.**
   - Check every seal precondition before the consumed ref is created: HEAD is a symbolic ref to the campaign branch, and
     the repository's common git dir is the canonical one.
   - A detached HEAD or a foreign clone is then refused with nothing evaluated.
   - Add a CLI control showing that a sandbox carrying a valid grant and review refuses before `prepare_target`.
3. **Driver: named bindings.** Pin the grant's `freeze_commit` and `qualification_commit` to the successor's own commits
   (N5).
4. **Recommended notes from the review:**
   - N2: compare C2's per-supply records, including the Lemma-G supply, in the control.
   - N3: catch `BaseException` after consumption, so a TC-T crosscheck SystemExit or the wall cap is sealed too.
   - N4: `seal-only` checks the result's self-hash and status, and its message states the real status.
   - N6: add the missing grant and r6 refusal controls.
   - N7: the r6 generator compares committed bytes, requires a clean tree, and guards `--out`.
   - N1: add git-blob bindings for the sha-only pins.
