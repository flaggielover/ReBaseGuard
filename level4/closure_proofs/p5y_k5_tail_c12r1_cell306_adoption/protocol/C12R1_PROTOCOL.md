# C12-R1: cell-306 adoption under K5 tail adoption floor r2 (successor of C12, repairing blocker B1)

**Status at this commit: FROZEN and prospective.** No Γ under any supply that contains an I2 constant has been computed,
estimated or inspected, by C12 or by C12-R1. The freeze commit holds `code/` and `protocol/`. Nothing after it may change
them: the driver derives the freeze commit from git and refuses a grant whose chain does not start at it.

**Predecessor.**
- **C12.** Freeze `b9ffc87f`, qualification `aac6dae9`, **QUALIFICATION_REJECTED** at `2cdfa467` with blocker B1.
- **Status:** `eba56027`. C12 stays immutable: its target was never evaluated, it has no grant and no marker, and its
  rejection stands.

**Authority.**
- Floor r2: rule `a15d083b`, review `3fadb422`, gate G00–G14.
- N9 CLOSED: `7d67989d` / `fb237288`.
- The user's overnight instruction, which starts with C12-R1. It requires the campaign to stop immediately on any
  rejecting or blocking verdict.

**Scope.**
- Cell 306 at m = 5 only. Cell 305 is used only as a historical I1 control rehearsal.
- The driver refuses cells 307–309.
- r5 is read and never written.

## 1. The B1 repair: three independent barriers

B1 was that the C12 verifier's sandbox, built at HEAD, would pass every guard at the accepted-review and grant commits,
and would then evaluate Γ(5, 306; S_I2) outside the real exactly-once marker. Each barrier below alone prevents that:

1. **The verifier cannot run at a later state.**
   - `c12r1_verify.py` runs only when HEAD is the freeze commit (official mode) or, with `--review`, the
     qualification-evidence commit directly on top of it.
   - It also requires that nothing below exists anywhere: in the tree, on disk, in any history or in any ref, for this
     campaign or for C12. Specifically: a qualification review, grant, adjudication, execution result, coverage output, or
     exactly-once marker.
   - Otherwise it prints `VERIFY REFUSED` and does nothing.
2. **Sandboxes come from the freeze commit and carry no real target.**
   - Every sandbox is built at the freeze commit, which is derived from git and is never HEAD.
   - Sandbox A has the real inputs. It is used only for baselines and input-tampering refusals, and never receives a grant
     or review.
   - Every governance-state and exactly-once test runs in sandbox B. Sandbox B's three I2 input files are replaced by
     minimal SYNTHETIC decoys (τ = 2, C_T = 3, Ā = 9, D_lo = 1/2, D1 = D2 = 1), so no real I2 or original D1/D2 value
     exists in its working tree. A failed guard there could only ever evaluate a decoy.
3. **The driver checks where it runs.**
   - `execute` and `seal-only` first require the qualified worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, git dir
     `/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-k5c11rd`, common dir `/Users/suzhe/ReBaseGuard/.git`, and branch
     `refs/heads/p5y-k5-tail-c11rd-d1d2-extension`.
   - Then it requires no marker or result of this campaign or of C12 anywhere.
   - Then it checks, still before the exactly-once marker exists: a clean tree and index, no git locks, the grant chain,
     the bindings, the governance state, and every seal precondition (committer identity, a buildable private index, a
     writable result directory, a resolvable branch ref).
   - After the marker exists, **every** exception, including `SystemExit` and the wall cap, is recorded and sealed.
     `seal-only` completes a failed seal and never computes.

**The adversarial tests the user required** (verifier sections A, B and X; each asserts that no result was written and no
marker was created unless one is expected):

| requirement | tests |
|---|---|
| freeze-commit sandbox PASS | A00, A00b |
| qualification-commit sandbox cannot target-evaluate | B01, X04 (Q) |
| accepted-review-state sandbox cannot target-evaluate | B02, B02v, X04 (R) |
| grant-state sandbox cannot target-evaluate | B03, B03s, B03v |
| consumed-state sandbox cannot target-evaluate | B04, B04v, X08, A07d, A07e |
| copied repository cannot target-evaluate | B05, X03 |
| wrong branch or worktree cannot consume | X01, X02, X02b |
| a planted result cannot cause a second evaluation | A07, A07b, A07c, X06, X07, X07b, B06v |
| a seal failure cannot cause a second scientific execution | X09, X10 |
| the pipeline itself works exactly once, on a DECOY target | X05 |
| barrier 1 at the freeze state itself | B07v, B08v, B09v |

## 2. What is computed, and by what

Unchanged from C12 §1. The consumer is C2's frozen path, executed from pinned bytes; every file is bound by sha256
**and** git blob (N1).
- **S_I1** = min componentwise {G, Dv′(REGISTRY_C1 block 306), Dv′(REGISTRY_C2 block 306)}. This is C2's adopted supply
  and the chosen supply.
- **S_I2** = min componentwise {G, Dv′(C11R C_T, τ, Ā, D_lo + C11RD D1, D2)}. It is never mixed with S_I1.

**Control (G10).** An exact reproduction of C2's committed cell-306 record, covering Γ, A, provenance, H, M and pass, and
**also C2's per-supply records for G, C1 and C2** (N2), so the substituted Lemma-G input is checked as well.

**I2 checks, all before the marker:**
- statuses, directions, classes and statements;
- `independence_violations == []` in both comparisons (N8);
- D1 and D2 equal to the sealed C11RD runs;
- the drift domain equal to cell 306's cover cell;
- consumer validation and the atom crosscheck.

## 3. Order of operations

1. **Freeze** (this commit).
2. **Qualification.** `c12r1_verify.py --out evidence/qualification/C12R1_QUALIFICATION.json`, run at the freeze commit.
   It is committed as the next commit, containing qualification evidence only.
3. **Qualification review.** A fresh, read-only reviewer writes `review/C12R1_QUALIFICATION_REVIEW.md` with line 2
   exactly `QUALIFICATION_ACCEPTED` or `QUALIFICATION_REJECTED`. It is preserved alone in the next commit.
   **If it is REJECTED, the entire overnight campaign stops.**
4. **Grant.**
   - `code/c12r1_grant.py`, frozen here, is run once at the review commit.
   - It re-runs the driver's own checks and requires the chain freeze → qualification → review.
   - It writes `authorization/C12R1_GRANT.json` and commits it alone.
   - **Authorization** is the user's overnight instruction together with this frozen, qualified grant procedure. There is
     no separate authorization review. The execution review re-verifies the grant.
5. **Pre-execution check.** The worktree is idle, with no other git activity, and resources are sufficient. It is
   recorded outside the namespace. Then `c12r1_cell306.py execute` runs **once**, at HEAD = the grant commit. The driver
   verifies the chain freeze → qualification → review → grant exactly, together with the driver bytes named in the grant.
6. **Seal.** The driver itself commits the result through a private index, with CAS on the branch. It prints only the
   status.
7. **Execution review.** A fresh reviewer writes `review/C12R1_EXECUTION_REVIEW.md`, line 2 `EXECUTION_ACCEPTED` or
   `EXECUTION_REJECTED`. It independently re-derives both Γ values from the committed inputs.
8. **Adoption adjudication.** A fresh, independent adjudicator writes `adjudication/C12R1_ADOPTION_ADJUDICATION.md`,
   line 2 `CELL306_ADOPTED` or `CELL306_NOT_ADOPTED`, with an `## ADOPTED CELL SET` block of `[306]` if adopting. It must
   state explicitly:
   - closure under I1;
   - closure or non-closure under I2;
   - F1′ eligibility;
   - floor-r2 eligibility;
   - the adoption status.
9. **Adjudication review.** A fresh reviewer writes `review/C12R1_ADJUDICATION_REVIEW.md`, line 2
   `ADJUDICATION_ACCEPTED` or `ADJUDICATION_REJECTED`.
10. **Coverage.** Only after `CELL306_ADOPTED` and `ADJUDICATION_ACCEPTED`: `code/c12r1_r6_from_adjudication.py` writes
    `evidence/coverage/K5_COVERAGE_MAP_R6.json` as the successor of r5. The only change is that (5, 306) moves OPEN → PASS.
    It checks committed bytes, a clean tree and a safe `--out` (N7).

**On any REJECTED or blocking verdict, or on CONTROL_FAILED, TARGET_EVALUATION_FAILED or UNSEALED (use seal-only only):
preserve the evidence and STOP the whole campaign.**

## 4. Decision table (floor r2, frozen): unchanged from C12 §3

| quantity | rule |
|---|---|
| base clause | Γ(5, 306; S_I1) < 0 |
| F1′ (a)–(c) | I1 and I2 each certified all six constants on the whole block; six AGREES/STRONGER with EQUIVALENT/STRONGER statements in accepted comparisons; no independence violation; soundness evidence per implementation (floor r2 §6) |
| F1′ (d) | Γ(5, 306; S_I1) < 0 **and** Γ(5, 306; S_I2) < 0, separately |
| F2 | NOT_SATISFIED. C2 published F2 FAIL on S_I1 for 306, and it is neither re-evaluated nor redefined. |
| floor r2 satisfied | base AND F1′ |
| adoption | floor r2 satisfied AND EXECUTION_ACCEPTED AND an independent adjudication CELL306_ADOPTED AND ADJUDICATION_ACCEPTED |
| closure disagreement | Γ(S_I1) < 0 but Γ(S_I2) ≥ 0: F1′ fails, the cell is NOT adopted, the disagreement is recorded, and nothing is re-evaluated |

**Kept separate throughout:**
- **Scientific closure:** Γ < 0 under a given supply.
- **Floor eligibility:** the table above.
- **Adoption:** the adjudication.
- **Coverage:** r6.

**What is never inferred:** K5 closure from any of these. STRONGER is never treated as soundness evidence.

## 5. G00–G14

Enforced exactly as C12 §4. In addition:
- **G03.** Enforced by barriers 1–3.
- **G11.** Enforced by the marker, now created only after every precondition.
- **G13.** Enforced by §3 steps 7–10.

## 6. Caps

- 900 s wall clock per invocation.
- This machine only, with zero new real scientific addresses.
- The marker is never deleted or moved.

## 7. Statement at freeze

- The only Γ evaluations run while building C12-R1 are two kinds. Both involve only decoy or historical data:
  - **I1 controls** for 306 and 305. They reproduce C2's committed pre-N9 records exactly.
  - **Decoy runs on synthetic I2 values** in a scratch clone's sandbox during debugging. These were stand-in commits,
    never in this repository.
- Nothing depends on any post-N9 magnitude.
