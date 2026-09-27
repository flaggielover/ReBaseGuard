# P5Y-K4R1: near-zero successor certificate (specification, written before any target evaluation)

## Standing

Historical K4 is **permanently** `K4_FROZEN_EXECUTION_R1 = NOT_CLOSED` with disposition `K4_INCONCLUSIVE_K1_RECORDS`:
- checkpoint `95b1fd16` @ `e5cc5a90`;
- execution `bc4ba08e`;
- independent review ACCEPTED.

K4R1 is a new, prospectively frozen successor. It does not repair, re-run or relabel that execution.

## Obligation (unchanged)

For each D ∈ {CUSUM, SR} and m ∈ {1, 2, 3, 5}, R_{D,m}(e) < 0 must hold for every e ∈ (0, 2]. The source is the K4 checkpoint target (P5X-T7(1)). The far-field region e > 2 is not asserted, exactly as frozen in K4.

K4R1 does not change any of the following:
- the detectors, the m scope, the domain, or the handoff at 2;
- strictness;
- any historical K4 decision.

## Residual universe

The universe is `config/RESIDUAL_UNIVERSE.json`: exactly the historical CERTIFICATE_TOO_LOOSE cells.

| m | cells | region |
|---|---|---|
| CUSUM m = 2 | 0–1 | (0, 10187/10⁷] |
| CUSUM m = 3 | 0–2 | (0, 957/625000] |
| CUSUM m = 5 | 0–2 | (0, 957/625000] |

The implementation refuses unless this list equals the hash-bound historical report for every (D, m).

## Certificate (route D3)

The exact formulas and their proof are in `config/GATE.json` → `certificate`. In brief, for each residual m:

```
G = D0.hi − L1·e0²/2                       (≥ R'(0))
T = min( M3(a), U0 + a²/2·M5(a) )          (≥ R''' on [0, a])
B = G + a²/6·max(T, 0)                     PASS iff B < 0   ⇒  R(e) ≤ e·B < 0 for all e ∈ (0, a]
```

### Inputs

All inputs are hash-bound in `config/PROVENANCE.json`:

| Symbol | Source |
|---|---|
| D0 | K1 CUSUM Aux5 cell-0 record `4f8df44c`, entry for m, `D_interval` |
| L1, U0 | slot-1 sealed record `cf90f1ea`, `per_m[m]` (ADOPTED, `84299314`) |
| M3, M5 | T-EXT result `cb97cabc`, row with `x_hi == a`, `M['3'][m]` and `M['5'][m]` (ADOPTED 37/37, `a3547b9b`) |

### Premises

- P5-T3: oddness.
- P5X L5: C^∞, used qualitatively only.

### Semantics

- **Arithmetic:** exact rationals; floats are refused.
- **Endpoints:** the region is (0, a]. e = 0 is not required to satisfy R(0) < 0. The handoff at a goes to the historical K4 cell that starts exactly at a.

## Rules

`config/GATE.json` defines:
- `pass_rule`;
- `science_rule`;
- `assembly_rule`;
- `adoption_rule`;
- `inherited_cells` (never recomputed);
- `budget`: 0 new real addresses and at most 60 CPU-s;
- `execution`: exactly once, locked behind `config/FREEZE.json`;
- `stop_conditions`.

There is no tunable parameter.

## Qualification history

- **r1** (candidate `81f5195a`): **QUALIFICATION_REJECTED** (`review/qualification_r1_REJECTED/`, review sha `c1e8cdf1`).
  - Mathematics, universe, provenance, endpoint and leakage checks all passed.
  - Blocking defect: the real-input wiring and the `execute` branch were not tested, and 6 unsound wiring mutants survived.
  - Candidate r1 is never frozen or executed.
- **r2** (candidate `179d5aae`) repaired:
  - wiring tests with distinct per-field values;
  - an end-to-end synthetic `execute` in a throwaway git repository;
  - all 12 reviewer mutants plus the new checks added to the harness (51 mutants in total).
- **r2 also addresses the r1 notes:**
  - **N1:** mandatory freeze bindings, a clean checkout, and FREEZE.json committed at HEAD.
  - **N3:** T-EXT scope stated in `GATE.input_scope_note`.
  - **N4:** disclosure revised in FEASIBILITY.md.
  - **N5:** K1 entry metadata and slot-1 transport consistency are now checked.
  - **N6:** refusals must be `K4R1Refusal`, not crashes.
- **r2** (candidate `179d5aae`): **QUALIFICATION_REJECTED** (`review/qualification_r2_REJECTED/`, review sha `bf42df37`).
  - Q1 was confirmed repaired, and N1 and N3–N6 fixed.
  - Blocking defect Q2: the gate's execution command would have crashed *after* computing the target, spending the exactly-once run without a record. There were two causes:
    - the output directory is absent in a clean checkout;
    - the command's path and working directory were inconsistent.
  - Candidate r2 is never frozen or executed.
- **r3** (candidate `cb5b6c61`) repaired Q2:
  - **Canonical output:** the output path is fixed and cwd-independent.
  - **Early reservation:** the directory is created and the output file is reserved by exclusive create before any source is read.
  - **Crash record:** any later failure is written into the reservation.
  - **`ready` subcommand:** a post-freeze launch check that computes and writes nothing.
  - **One runbook:** a single unambiguous runbook in GATE.
  - **Literal-command tests:** subprocess tests run the literal commands from the repository root and from another cwd, with no pre-created output directory.
- **r3 also addresses the r2 notes:**
  - **N7:** tests and harness mutants cover all 19 non-equivalent r2-reviewer survivors (74 mutants in total, 3 documented equivalents).
  - **N8:** the synthetic repositories ignore `__pycache__`, and the suite passes with in-tree bytecode.
  - **N10:** the runbook requires an empty `git status --porcelain`, then `ready`, before `execute`.
  - **N9 and N11 are accepted.** Exact-once is per canonical output with reservation, and HEAD is recorded.
- **Designer disclosure:** while checking the r3 lock, the designer ran `execute` once in the real worktree before any freeze. It was refused at the freeze gate (`FREEZE.json` absent) before any source was read.
- **r3** (candidate `cb5b6c61`): **QUALIFICATION_REJECTED** (`review/qualification_r3_REJECTED/`, review sha `8f49abac`).
  - Q2 was confirmed repaired. The whole planned flow worked on synthetic copies under Python 3.9 and 3.14.
  - Blocking defect Q3: `make_freeze` bound whatever was on disk in the namespace, including edited, untracked and ignored files, without checking git state. In addition, `ready` and `execute` did not verify that the freeze commit equals the qualified candidate plus review and FREEZE files.
  - Candidate r3 is never frozen or executed.
- **r4** (candidate `5d33363c`) repaired Q3 with a git-aware `make_freeze`:
  - it refuses unless the checkout is the candidate plus exactly the two review files;
  - it refuses on any ignored entry in the namespace;
  - it binds exactly the tracked namespace files plus the review files and sources;
  - it records `allowed_freeze_delta`.
- **Launch verification in r4:** `ready` and `execute` verify ancestry, `git diff <candidate> HEAD` against the allowed delta, and bound namespace files against the tracked files.
- **r4 also addresses the r3 notes:**
  - **N12:** the crash record carries HEAD and the freeze hash; KeyboardInterrupt and hard kills are covered.
  - **N13:** majorant signs are checked before the reservation.
  - **N14:** the remaining survivors are now tested or documented as equivalent.
  - **N15:** the wording is fixed.
  - **N16:** the `ready` and `execute` refusal rules are in `GATE.stop_conditions`.
  - **Runbook:** it names exactly which review files are copied.
- **Harness:** 92 mutants across both scripts, all killed (5 documented equivalents); 78 tests.
- **r4** (candidate `5d33363c`): **QUALIFICATION_REJECTED** (`review/qualification_r4_REJECTED/`, review sha `c1718a4c`).
  - Q3 was confirmed repaired against all plausible operator actions.
  - Blocking defect Q4: the launch check trusted the freeze's own `review_files` list. A tampered FREEZE could therefore list an edited implementation as a "review file" and get unqualified code executed. The bound review's verdict and candidate were never read.
  - Candidate r4 is never frozen or executed.
- **r5** (this candidate) repairs Q4. The review files are pinned to exactly one `QUALIFICATION_REVIEW.{json,md}` pair in `review/qualification_rN`, which must be absent at the candidate. The bound review JSON must accept `qualified_candidate_commit`. The r4 notes are addressed as follows:
  - **N19:** every bound file must equal its committed blob at HEAD, and `make_freeze` checks the same.
  - **N20:** both scripts require isolated mode (`-I`), and any untracked or ignored file inside the namespace blocks launch.
  - **N22:** `--no-renames`.
  - **N23:** the freeze commit's only parent must be the candidate.
  - **N24:** stop conditions rewritten. At most one `execute` invocation per lineage, in any checkout or clone, and this takes precedence over the fresh-clone remedy.
  - **N25:** tests for "ready runs the preflight" and for non-mandatory bindings.
- **Test coverage:** 92 tests; 102 mutants, all killed (6 documented equivalents).
- **r5 must pass a new, independent qualification** before any freeze.

## Governance sequence

1. **Candidate commit.** Contains this specification, the gate, the universe, the provenance, the code, the tests, and the qualification evidence (the synthetic suite, the mutation harness, and a value-blind preflight).
2. **Independent pre-result qualification.** A fresh-context reviewer returns exactly one of `QUALIFICATION_ACCEPTED`, `QUALIFICATION_REJECTED` or `QUALIFICATION_BLOCKED`. Anything other than ACCEPTED stops this lineage.
3. **Freeze commit.** `config/FREEZE.json` and `FREEZE_HASH` bind hashes of:
   - the specification, the gate, the universe and the provenance;
   - the code and the tests;
   - the qualification review;
   - every source.
4. **Exactly-once execution** from a clean checkout of the freeze commit, producing `evidence/execution_r1/K4R1_RESULT.json`.
5. **Fresh-context final adjudication:** ACCEPTED, REJECTED or BLOCKED.
6. **Publication.** A closure tag is created only if K4R1_SUCCESSOR_SCIENCE = PASS and the final adjudication is ACCEPTED.

See `FEASIBILITY.md` for the Phase A–C analysis and the pre-result disclosure.
