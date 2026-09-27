# C12-R2: cell-306 adoption under K5 tail adoption floor r2 (successor of C12-R1)

**Status at this commit:** FROZEN, prospective.
- No Γ has ever been computed, estimated or inspected under a supply containing a real I2 constant, by C12, C12-R1 or
  C12-R2. The real Γ(5, 306; S_I2) has been evaluated **0** times.
- No marker, grant, result or seal exists.
- The freeze commit holds `code/` and `protocol/`. The driver derives it from git and refuses a grant whose chain does not
  start at it.

**Predecessors (immutable):**

| campaign | freeze | qualification | review | status |
|---|---|---|---|---|
| C12 | `b9ffc87f` | `aac6dae9` | QUALIFICATION_REJECTED `2cdfa467` (B1: sandbox at HEAD) | `eba56027` |
| C12-R1 | `5cfe336a` | `2e7bc7d6` | QUALIFICATION_REJECTED `e89402c1` (the C12-R1 blocker below) | `13e06db0` |

**Authority.**
- Floor r2: rule `a15d083b`, review `3fadb422`.
- N9 CLOSED: `7d67989d` / `fb237288`.
- The user's C12-R2 authorization. It covers repair, freeze, qualification and a fresh qualification review **only**.
  **No grant is issued under it.** The grant and execution phase needs a separate explicit authorization.

**Scope.**
- Cell 306 at m = 5 only. Cell 305 is used only as a historical I1 control rehearsal.
- The driver refuses cells 307–309.
- r5 is read and never written, and no r6 is created.

## 1. The C12-R1 blocker and its repair

**Blocker.**
- C12-R1 wrote its result through `evidence/execution/C12R1_CELL306_RESULT.tmp`. `.gitignore` ignores `*.tmp`, so the
  clean-tree check could not see an object planted there, and no pre-marker check examined that path.
- The write also ran outside the post-marker handler.
- On decoys, the reviewer showed two consequences:
  - a planted directory made the one evaluation unsealable;
  - a planted symlink diverted the full result outside the repository while the driver printed SEALED.
- It allowed neither a second evaluation nor an evaluation outside the marker. The C12-R1 barriers against C12's B1 were
  found sound.

**Repair**, in `code/c12r2_cell306.py`:

**R3: seal from memory. No filesystem write precedes the seal.**
- The result is serialized in memory.
- The bytes go straight into the object store with `git hash-object -w --stdin`. Their blob id is checked against a SHA-1
  computed locally.
- A pending-result ref records them (`refs/c12r2/cell306-pending-result`, created by CAS).
- They are committed through a private index with `update-index --cacheinfo 100644,<blob>,<path>`, so no worktree file
  is read.
- After the commit, the committed entry is verified to be exactly that blob, with mode 100644.
- Only **after** the seal is the worktree copy written: every path component is opened with `O_NOFOLLOW` from the verified
  worktree root, the execution directory is created fresh (`mkdir`, which fails if anything exists), and the file is
  created with `O_CREAT|O_EXCL|O_NOFOLLOW`.
- The copy is then read back and compared with the sealed bytes, and must be a regular file with a link count of 1.
- There is no temporary result file, no rename and no replacement.

**R1: pre-marker path refusal.**
- Before the marker, `lstat` (which never follows links) must find **no object of any kind** at the result path, at the
  conventional temporary names (`…RESULT.tmp`, `…RESULT.json.tmp`, `…RESULT.partial`), or at `evidence/execution` itself.
  "Any kind" covers files, directories, symlinks, broken symlinks, FIFOs, sockets and devices.
- The path from the worktree to `evidence/` must have no symlinked component.
- The check is repeated immediately before the marker.

**R2: ignored-aware cleanliness.**
- Before the marker, `git status --porcelain --ignored --untracked-files=all -- <namespace>` must be empty.
- The repository-wide tracked and untracked check is kept.
- `.gitignore` is not changed.

**R4: complete post-marker handling. From the marker on, the campaign is consumed:**
- Interrupt signals (INT, TERM, HUP and QUIT) are ignored from just before the marker.
- The wall cap is re-scoped to the evaluation alone, and a timeout inside it is recorded.
- `after_marker` lets nothing escape. Evaluation exceptions of every kind, including `SystemExit`, `KeyboardInterrupt` and
  the cap, are recorded, and so are serialization failures.
- The evidence is persisted through **two channels** before any seal attempt:
  1. the object store plus the pending ref;
  2. a fallback file created with `O_EXCL|O_NOFOLLOW` in the qualified git dir.
- The outcome is always one of these, and none of them is ever "safe to rerun":
  - sealed (0, or 5 for a failure status);
  - UNSEALED with evidence persisted (4);
  - sealed but not materialized (7);
  - CONSUMED_UNRECORDED, when both channels fail (6). The marker remains, and it is refused forever.
- `seal-only` seals or materializes **existing** evidence only. It never loads the consumer and never evaluates.

**Other pre-marker additions.**
- An object-store write probe.
- A trial commit object created with the current configuration (N4).
- A writable parent directory for the worktree copy.
- Interpreter flags `-I -S -B` required (N8).
- A pending ref, or an emergency file, counts as prior-evaluation evidence.

## 2. C12-R1 protections kept (unchanged or strengthened)

- The verifier refuses to run unless HEAD is the freeze commit, or with `--review` the qualification-evidence commit on it.
- It refuses when any of these exists anywhere, for C12-R2, C12-R1 or C12:
  - a qualification review, grant, adjudication, execution or coverage output;
  - a marker or pending ref;
  - an emergency file.
- `--review` now also requires a clean tree, including ignored files, and `code/` and `protocol/` identical to the freeze
  (N3). Its temporary output is removed (N13).
- Sandboxes are built from the freeze commit.
- Sandbox A has the real inputs, is used for baselines and input tampering, and never receives a grant or review.
- Sandbox B runs every governance-state, exactly-once, filesystem-attack and post-marker test.
  - These files in it are synthetic decoys:
    - the I2 **supply input files** (`C11R_COMPARISON.json`, `C11RD_COMPARISON.json`, `C11RD_RUNS.json`);
    - `C11R_RUNS.json`;
    - the I2 soundness documents (the C11RD theory and the independence audit).
  - The C11RD run logs are removed from it.
  - Other pinned documents stay unchanged, and they are never read as supply inputs. The floor rule is one example, and
    it mentions C11R's exact C_T supremum (N1).
- The driver requires, before anything else in `execute` and `seal-only`:
  - the qualified worktree `/Users/suzhe/ReBaseGuard-k5c11rd`;
  - the git dir `/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-k5c11rd`;
  - the common dir `/Users/suzhe/ReBaseGuard/.git`;
  - the branch `refs/heads/p5y-k5-tail-c11rd-d1d2-extension`.
- The grant chain freeze → qualification → review → grant is derived and checked exactly. The qualification report must
  be an official, non-review PASS at the freeze commit.
- Every input is pinned by sha256 **and** git blob. That now includes the floor-r2 G07 soundness evidence (N10):
  - `C11R_RUNS.json`;
  - `CELL_306_ADOPTION.md`;
  - the C11RD theory and independence audit;
  - the C2 adjudication.
- The consumer is C2's frozen path, executed from pinned bytes, with `tail_forecast_r2.py` and every non-supply input
  pinned.
- S_I1 and S_I2 are never mixed.
- The G10 control reproduces C2's cell-306 record exactly, and C2's per-supply records for G, C1 and C2.
- Lemma G is re-derived exactly from its statement and cross-checked (N11).
- Scope stays cell 306 only.

## 3. Qualification tests required by the C12-R2 authorization

| requirement | tests (verifier) |
|---|---|
| T1: a directory at the temporary path is refused before the marker; 0 evaluations; no marker; no result | T1 |
| T2: a symlink at the temporary path pointing outside is refused; the destination is unchanged | T2 |
| broken symlink; planted final result (file, symlink, directory, broken symlink); ignored regular `*.tmp`; FIFO; socket; symlinked execution directory; symlinked parent | T3, T4–T4d, T5, T5b, T6, T7, T8, T9 |
| result-write / seal / permission failure after the marker | P06–P08, P09 |
| serialization, evaluation exception, SystemExit, KeyboardInterrupt, wall cap after the marker | P05, P01–P04 |
| unexpected filesystem state after the marker | P10, P11, P11b |
| rerun after a post-marker failure; rerun after a successful decoy run | every P test, X06 |
| recovery never recomputes | every P test (evaluation count stays 1), X06b |
| sealed bytes = produced bytes | X05 |
| the C12-R1 protections | S, R, A, B, X01–X13, F, G |
| review notes N1–N13 classified, with the cited tests passing | N section |

## 4. Order of operations

1. **Freeze** (this commit).
2. **Qualification.** `c12r2_verify.py --out evidence/qualification/C12R2_QUALIFICATION.json`, run at the freeze commit.
   It is committed next, as qualification evidence only.
3. **Fresh read-only qualification review.** It writes `review/C12R2_QUALIFICATION_REVIEW.md`, with line 2 exactly
   `QUALIFICATION_ACCEPTED` or `QUALIFICATION_REJECTED`, preserved alone in its own commit.
   **The C12-R2 authorization ends here, whatever the verdict.**
4. **Only under a separate explicit authorization, after QUALIFICATION_ACCEPTED:**
   - `code/c12r2_grant.py` writes and commits the grant alone;
   - `code/c12r2_cell306.py execute` runs once at the grant commit;
   - then the execution review, the adoption adjudication and its review;
   - and, only if the adjudication is `CELL306_ADOPTED` + `ADJUDICATION_ACCEPTED`, the mechanical r6 by
     `code/c12r2_r6_from_adjudication.py`.

## 5. Decision table (floor r2, frozen): unchanged

| quantity | rule |
|---|---|
| base clause | Γ(5, 306; S_I1) < 0 |
| F1′ (a)–(c) | both implementations certified; six AGREES/STRONGER with EQUIVALENT/STRONGER statements; no independence violation; soundness evidence per implementation |
| F1′ (d) | Γ(5, 306; S_I1) < 0 **and** Γ(5, 306; S_I2) < 0, separately |
| F2 | NOT_SATISFIED. C2 published F2 FAIL on S_I1, and it is neither re-evaluated nor redefined. |
| floor r2 satisfied | base AND F1′ |
| adoption | floor satisfied AND EXECUTION_ACCEPTED AND an independent CELL306_ADOPTED AND ADJUDICATION_ACCEPTED |

These four are kept separate and never inferred from one another:
- scientific closure;
- floor eligibility;
- adoption;
- coverage.

K5 closure is never inferred from any of them.

## 6. Caps

- **Wall clock:** 900 s per invocation. The evaluation alone is capped at 600 s.
- **Resources:** this machine only, with zero new real scientific addresses.
- **Markers:** the marker and the pending ref are never deleted or moved.
