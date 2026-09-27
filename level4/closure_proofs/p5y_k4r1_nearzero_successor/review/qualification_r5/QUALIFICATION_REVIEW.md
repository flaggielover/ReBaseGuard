# P5Y-K4R1 qualification review r5

- **Verdict:** QUALIFICATION_ACCEPTED
- **Candidate:** `93d82c87d2f5aa33109f5b37125caf283967b694` (branch `p5y-k4r1-nearzero-successor`)
- **Reviewer:** independent adversarial pre-result qualification reviewer r5 (fresh context; not the designer, and not a reviewer of rounds r1-r4)
- **Date:** 2026-09-27
- **Machine-readable record:** QUALIFICATION_REVIEW.json (same directory)

## Outcome

Q4, the r4 blocking defect, is repaired, and Q1-Q3 remain repaired. There are **no blocking defects**. Every remaining finding is non-blocking.

`verify_freeze` now enforces all of the following:

- **Review files are pinned.** `review_files` must be exactly one `QUALIFICATION_REVIEW.{json,md}` pair, in one `review/qualification_rN` directory, and both files must be absent at the candidate.
- **The bound review is read.** Its JSON must have verdict `QUALIFICATION_ACCEPTED` and must name `qualified_candidate_commit`.
- **Single freeze commit.** HEAD's only parent must be the candidate, and the diff is taken with `--no-renames`.
- **Committed bytes.** Every bound file must equal its HEAD blob.
- **Clean namespace.** No untracked or ignored entry may exist in the namespace.
- **Isolated mode.** Both scripts refuse to run without `-I`.

Together these checks mean that every tracked file except the four freeze-delta paths is byte-identical to the qualified candidate. Only the stdlib and the bound script are imported. Under the runbook, only the qualified candidate plus exactly the review pair can produce a recorded EXECUTED result.

## Evidence (summary)

### 1. Literal flow

All four JSON data sources were replaced by synthetic ones in an exported copy, before any run. The copy was then taken through `freeze_procedure` and the `execution` runbook exactly as written:

| Environment | Result |
|---|---|
| Python 3.9.6, from the repo root | FREEZE WRITTEN; READY PASS; EXECUTED; second execute EXACT_ONCE |
| Python 3.14.5, from the repo root and from cwd `/` | same |
| Fresh full clone of the freeze commit | same |
| Linked git worktree | same |

### 2. Post-freeze attacks (all refused)

- the r4 Q4 smuggle, applied to the code, to GATE and to SPEC;
- a (json, code) pair;
- a `..` traversal;
- an extra commit;
- a review that is REJECTED, names another candidate, names an abbreviated candidate, or has a lowercase verdict;
- the `.md` named as `qualification_review`;
- a third review file;
- an abbreviated candidate commit;
- a merge commit carrying edited code;
- an empty commit on top of the freeze;
- assume-unchanged and skip-worktree edits, with and without a rewritten FREEZE;
- an excluded shadow module inside `code/`;
- a run without `-I`.

Stray modules and environment variables outside the namespace are inert under `-I`.

### 3. make_freeze attacks (all refused)

- no `-I`;
- a skip-worktree edit;
- an untracked file outside the namespace;
- an excluded shadow module inside the namespace, refused cleanly;
- a review-dir suffix;
- a nested review dir.

### 4. Real worktree

- `git status --porcelain --ignored --untracked-files=all` is empty before and after this review.
- There are no replace refs, grafts, hooks or risky git config, and the repository is not shallow.
- None of the paths the freeze and execution will write is gitignored.
- `review/qualification_r5` is new.
- `python3 -I -B ... preflight` passes under 3.9 and 3.14, byte-identical to `evidence/qualification_r5/PREFLIGHT.json`.
- Assembly on the real historical report (synthetic certificates) is 8/8 PASS.

### 5. Tests and harness

- The tests pass 92/92 under 3.9 and 3.14.
- The harness kills 102/102 mutants, with outcomes and file hashes identical to the committed `MUTATION_REPORT.json`.
- All 6 documented equivalents hold.

### 6. Reviewer mutants on the r5 changes

20 mutants: 3 killed, 17 survived. The survivors are:

- **Equivalent:** 4 of them.
- **Redundant or tamper-only layers:** the rest. None is unsound under the runbook. See N29.

### 7. Earlier-round invariants

- **No target computed.** A blind scan of all 10 revisions finds only the disclosed K1 D0 endpoints in `RESIDUAL_TABLE.json`. No FREEZE or execution output exists in any revision.
- **Residual universe.** It equals the historical TOO_LOOSE cells (report `83cabce2`).
- **Inheritance and handoff.** Both are sound.
- **Mathematics.** The G/T/B theorem was re-derived against the K4 checkpoint (`D_interval` encloses R'(e0)), the slot-1 PROTOCOL (`[L0,U0]` contains R'''(0), and `L1` bounds R''' on `[0,x1]`) and TEXT_SPEC (`M_n(eta)` bounds sup over `[0,eta]`, with eta an outward rounding).
- **L5.** It is used qualitatively only.
- **Endpoints.** The region is `(0,a]`.
- **Parameters.** There is no tunable parameter and no narrowing.
- **Provenance.** 16/16 PROVENANCE hashes match at 93d82c87.
- **Adoption.** slot-1 and T-EXT are ADOPTED.
- **Unchanged since r1:** the GATE certificate and rule fields, and the formula code.

## Non-blocking notes

- **N27 (deliberate, detectable).** `git replace` of the code blob combined with skip-worktree lets edited code run under a genuine-looking FREEZE. A fresh clone refuses.
  - *Fix for a future revision:* use `--no-replace-objects`.
  - *For this lineage:* the final adjudicator must re-verify every bound hash against `git show <candidate>:<path>` in a fresh clone.
- **N28 (deliberate).** A forged review naming a different commit cannot be detected by code. The adjudicator must check that `qualified_candidate_commit == 93d82c87d2f5aa33109f5b37125caf283967b694` and that the bound review files equal the files of this review.
- **N29.** Some new checks are untested redundant layers. Tests are listed in the JSON.
- **N30.** The stop conditions leave two gaps:
  - They do not say whether a new freeze of the same candidate may follow an ended lineage. A second lineage is technically possible, but exact deterministic arithmetic makes it outcome-neutral.
  - Invocation errors (a missing `-I`, a typo) literally end a lineage.
- **N31.** `PROVENANCE.identities.k1_successor_final_adjudication_commit` has a one-character typo. The real commit is `7d5cf02b7f4b...`. The field is unused by code.
- **N32 (operational).** The review pair must enter the repository only through the freeze commit, as follows:
  1. Check out HEAD == 93d82c87.
  2. Copy the two files into `review/qualification_r5/`.
  3. Run `python3 -I -B .../make_freeze.py --review-dir review/qualification_r5`.
  4. Commit exactly the four paths.

  Do not make a separate "record qualification r5" commit.
- **N33.** The fresh-clone remedy needs a full clone, or at least `--depth 2`.
- **N34.** Carried from earlier rounds: N3, N17 and N26. Also, a non-JSON `qualification_review` crashes before the reservation, which is harmless.

## Reviewer disclosures

- **No target value computed.** I computed no G, T or B and no combination of real K1, slot-1 or T-EXT values. I printed no real slot-1, T-EXT M or Lambda value.
- **Synthetic data only.** All flows, attacks and mutants used synthetic data sources in scratch copies.
- **Commands run in the real worktree:**
  - read-only git commands;
  - `git archive` into scratch;
  - the permitted value-blind `preflight`, under 3.14 and 3.9;
  - one run without `-I`, refused at the isolation guard before reading anything;
  - one in-process structural `check_universe`/`assemble` call on the historical report, with synthetic certificates;
  - a blind leakage scan that printed only labels and counts;
  - hashing of the 16 sources.
- **Not run in the real worktree:** `ready`, `execute`, `make_freeze`, pytest, the harness.
- **No repository changes.** No file in either checkout was modified. There was no commit, checkout, switch, reset or update-index.
