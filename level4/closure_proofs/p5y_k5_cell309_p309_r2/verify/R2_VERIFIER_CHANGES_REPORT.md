# P309-r2, gate step 3: the verifier author's changes (report)
VERIFIER_R2_CHANGES_DONE

**Brief:** `governance/BRIEF_R2_VERIFIER_AUTHOR_1.md`, committed before issue at `2183b8f2` (branch
`claude/p5y-k5-cell309-p309-r2`). It follows plan addendum 2, F11.

**Author:** r1's independent verifier author. No coordinator code was used to make these changes.

**Base:** the step-3a relocation baseline `e07e3ee8`. Before any edit, the six files under FNS2 were checked
byte-identical to r1's freeze F (`4c754a73`) and to r1's working tree: `9d9f8cec…`, `58d15e63…`, `45902e30…`,
`7625ecf9…`, `bad3ffa7…`, `1483d6c2…`.

NEW Γ309 TARGET EVALUATIONS = 0. No REAL-band evaluation took place. No ref was created, updated or deleted under
`refs/p5y-k5-cell309-p309-r1/` or `refs/p5y-k5-cell309-p309-r2/`, in any repository, sandbox or clone. No git write was
made in the real repository. Nothing is committed.

## 0. Summary

| item | outcome |
|---|---|
| V1 literals | done: variant 163 (owner), 170 (rename), 175 (binding); tests 791 and 815 (binding). Every "keep" row is kept |
| V2 both namespaces | done: variant `FORBIDDEN_REF_NAMESPACES` (r1 and r2) in `_validated_sandbox`; helper `_FORBIDDEN_REF_PREFIX = (_R1, _R2)` in every guard; static check added |
| V3 base rule | done: `scoped_sandbox.sandbox_base_commit()`, plus pre- and postconditions, the P6(e) static check and a shape test; the scratch-clone control passed |
| V4 `P309_SCRATCH_ROOT` | done: `scratch_sandbox_base()` with loud refusals and no fallback; no session path left in code; 18 negative and 2 positive controls, plus 7 constructor-level controls |
| V5 results file | **regenerated** in 594.7 s wall time; all 2369 entries match r1 (verdicts identical); no finding |
| V6 README | r2 section appended (+120 lines, 0 removed) |
| V7 re-pins | 5 AST re-pins (CPython 3.11.15), plus the config entries step 4 needs; a simulation with them applied gives scanner PASS with 0 findings |
| tests | run A (before V3): 40/40 OK; run B (after V3): 42/42; V5 harness unit tests: 42/42; run C (post-freeze topology): 42/42 |

**New sha256 values:**

| file | r1 (F) | r2 |
|---|---|---|
| `verify/srk_verify_indep_scoped.py` | `9d9f8cec52cfd49ab146a45c44e03fde493614f81551af584317ab7d3545498f` | `e82d68121ecd0003c61ed304d57e65f8ef7cda1aa9aad1c1ea08b8c01336aebf` |
| `verify/scoped_sandbox.py` | `58d15e632511af18c3ce4397a22ea8722a094f423ff468c67274ceefcdf21159` | `5fff1ba8c671af77d04dfcad3ef6d8f993db8d50ea46e995214d07fd218fd0d2` |
| `tests/test_verify_scoped.py` | `1483d6c2f5c9d8d3a469915fe6ab85d0cb27f3abdfcac53b168ff6754a64a10c` | `94db67d47ea30f2cfdbdd4a1ecc0ff039f775f887f155dca57887334e06c7ad3` |
| `verify/run_verify_all_scoped.py` | `45902e30cb59db718c2a133fa321e30ee183a3fa18781c3698a11ce7f48b90d8` | unchanged |
| `verify/VERIFY_RESULTS_SCOPED.json` | `bad3ffa7…` | `404e3c3cb3323865fee80e6c91573506df1c4db83e1c6968487357f0a4c2cafe` |
| `verify/README_VERIFY_SCOPED.md` | `7625ecf9…` | `79eff9008d8cd0e258bfd9280e2e8f1e6d8f59bd946babc96baf23669a5f9bad` |

The variant's `verifier_id` therefore becomes `sha256:e82d68121ecd0003c61ed304d57e65f8ef7cda1aa9aad1c1ea08b8c01336aebf`.

## 1. Where everything ran (a judgement, disclosed)

**Every test, control, scan and the V5 regeneration ran in a scratch clone of the r2 branch**, never in place in FNS2:
* the clone was `<scratchpad>/r2/clone`, made by `git clone --single-branch --branch claude/p5y-k5-cell309-p309-r2`;
* the source is shallow, so git used its file transport;
* `origin` was removed, so the clone had no remote and no push URL;
* it held 0 refs under either production namespace, checked before, during and after;
* it was **deleted by its literal path** at the end.

**Why.** My test file and the harness ledger every execution through `code/p309_env.py`, which writes
`<FNS>/ledger/ZERO_TARGET_LEDGER.jsonl`, with FNS resolved from its own location.
* FNS2 has no `ledger/` yet. Its genesis line belongs to the coordinator at step 4 (R2-I1).
* This step may write only the six files and the two outputs.
* An in-place run would therefore have created `FNS2/ledger/ZERO_TARGET_LEDGER.jsonl` ahead of the genesis line. The
  clone's own run A did exactly that, in the clone.

The clone's bytes of the six files were checked equal to FNS2's before every run.

**Note.** Addendum 2's step 3a says "No QC item, drill or test is run on it before then [step 4]". This brief directs
tests at step 3, so I ran them, but only in the scratch clone. Nothing was executed in place on FNS2.

## 2. The changes

### V1: literals (`governance/R2_LITERAL_DISPOSITION.json`; OD-R2-1 (b), provisional per F7)

| file:line (r1) | r1 literal | r2 literal | disposition |
|---|---|---|---|
| variant:163 `PRODUCTION_MARKER` | `refs/p5y-k5-cell309-p309-r1/target-consumed` | `refs/p5y-k5-cell309-p309-r2/target-consumed` | owner |
| variant:170 `_FNS_REL` | `level4/closure_proofs/p5y_k5_cell309_p309_r1/` | `level4/closure_proofs/p5y_k5_cell309_p309_r2/` | rename (carries the grant, manifest and result paths; supplement 1 cross-reference) |
| variant:175 `campaign` | `p5y_k5_cell309_p309_r1` | `p5y_k5_cell309_p309_r2` | binding |
| tests:791 (N10), tests:815 (N11) | `campaign: p5y_k5_cell309_p309_r1` | `campaign: p5y_k5_cell309_p309_r2` | binding |

**Kept unchanged:**
* the schema names: `P309_GRANT/1` (variant 174; tests 791, 815), `P309_TEST_GRANT/1` and `/2`, `P309_TEST_RESULT/1`,
  and `P309_TEST_FREEZE_MANIFEST/1`;
* the README's verifier history `6522db10` (lines 21 and 52);
* the variant's research-namespace reads.

**No other r1 token remains** in the four Python files. The scan was `p309[_-]r1`, `cell309-p309`, session and
scratchpad patterns; the only hit is r1's namespace, deliberately kept by V2.

### V2: both production namespaces forbidden (addendum 2, F1)

**The variant:**
* `PRIOR_PRODUCTION_REF_NAMESPACE = 'refs/p5y-k5-cell309-p309-r1/'`;
* `FORBIDDEN_REF_NAMESPACES = (PRIOR_PRODUCTION_REF_NAMESPACE, PRODUCTION_REF_NAMESPACE)`;
* `_validated_sandbox` (the `TestContext` refusal) now loops over that tuple, running `for-each-ref` on each namespace,
  and refuses a sandbox with a ref under either;
* `PRODUCTION_REF_NAMESPACE` is still derived from the marker, so it is r2's.

**The helper:**
* `_FORBIDDEN_REF_PREFIX = (_FORBIDDEN_REF_PREFIX_R1, _FORBIDDEN_REF_PREFIX_R2)`;
* `_assert_ref`, called by `update_ref`, `delete_ref` and `reset_hard_index` (every ref-moving method), refuses either;
* the new `assert_no_production_refs()` checks both, at construction and on leaving the context.

**Why each literal is its own named constant.** `p309_scan.formal_rules` accepts a production-token literal only as the
`ast.Constant` value of a module-level assignment to a reviewed home (`token_definitions`). A tuple of literals would
be two `MARKER_TOKEN` findings. Each literal therefore has its own constant, and the tuple holds the names. See §4 for
the config entries.

**Static check:** `TestR2Verifier.test_V2_both_namespaces_forbidden`. It checks, by AST:
* both literals;
* the tuple's members;
* the loop in `_validated_sandbox`, and that it never uses `PRODUCTION_REF_NAMESPACE` alone;
* that `TestContext.__init__` calls `_validated_sandbox`;
* that `_FORBIDDEN_REF_PREFIX` is used by `_assert_ref` and `assert_no_production_refs`;
* that every ref-moving method calls `_assert_ref`.

At run time it also checks the tuple values and that `_assert_ref` raises for a name in either namespace. The guard
raises before any git call, so no ref is created.

**No ref was created anywhere.** The TEST-only prior-marker name `refs/p5y-k5-cell309-TEST-ONLY-prior/x` was not
needed, so `_ALLOWED_REF_PREFIXES` is unchanged.

### V3: the sandbox base rule (P6(b), P6(e); plan §4)

**Implementation.** `scoped_sandbox.sandbox_base_commit(repo=None, record_rel=None)` is implemented in `verify/` only,
importing nothing from `code/` or `tests/`.
* **The record.** `freeze_record_rel()` is `<FNS>/ledger/FREEZE_RECORD.json`, relative to the repository top level.
  FNS is derived from the helper's own location, so r1's record at r1's path is never mistaken for r2's. r2's HEAD
  history does contain r1's FR `2f66bc56` at r1's path.
* **The touching commits.** `touching = git rev-list --end-of-options HEAD^{commit} -- <record>`.
  * **0 commits:** the base is HEAD (`'development'`).
  * **Exactly 1 commit `rc`:** it must have exactly one parent (`rev-list --parents -n 1`), and it must touch only
    the record (`diff-tree -r --name-only --no-commit-id <parent> <rc>` equals `[record]`). Its record must be JSON
    with a 40-hex `freeze_commit` equal to that parent. The base is then F (`'post-freeze'`).
  * **Any other shape** raises `FreezeRecordError(RuntimeError)`, which is loud and never a refusal.
* **Precondition (P6(b)).** The base's history holds 0 commits touching the record, else the call raises.
* **`Sandbox.__init__`.**
  * It computes the base before creating any directory, so a bad record leaves nothing behind.
  * It sets `refs/heads/fc2-sandbox` to `self.base_commit`.
  * It asserts that the sandbox holds 0 record commits and that its branch equals the base.
  * It tears the sandbox down if construction fails after `git init`.
* **Postcondition (P6(b)).** `check_freeze_records()` runs:
  * in `build_valid`, after the fixture;
  * in `__exit__`, on normal exit from the context.

  The expected number is `Sandbox(tag, expect_freeze_records=0)`, which is 0 for every FC2 flow. No flow builds a
  record at the namespace path.
* **Static check (P6(e)):** `TestR2Verifier.test_V3_base_rule_static`.
  * The constructor has no base parameter, and the branch is set only from `sandbox_base_commit()`'s result.
  * **Every** git `HEAD` operand in the four Python files is accounted for by owner and by the repository operand it
    names:
    * `sandbox_base_commit`: `repo`. This is the one real-HEAD read used as a base.
    * `Sandbox.__init__`, `.head`, `.reset_hard_index`, `.freeze_record_commits`, `TestFC2Scoped.fresh` and
      `test_N13`: the sandbox only.
    * the variant's `_admission`: the repository under admission, never a base.
    * `TestFC2Scoped.no_production_artifacts`: a read of the grant path's absence at HEAD, never a base.
  * `sandbox_base_commit` is called only by `Sandbox.__init__` and, on sandboxes, by the shape test.
  * The variant does not import the helper.
* **Shapes:** `TestR2Verifier.test_V3_base_rule_shapes`, with a TEST-named record path (`TEST_ONLY/FREEZE_RECORD.json`)
  inside a sandbox. It covers development, F′/FR′, a checkpoint after FR′, and 9 malformed shapes. Each malformed shape
  raises `FreezeRecordError`, and none is a `Refusal` or a `TestContextRefused`.

**Semantics: a difference to check against the coordinator's code.** "Touching" commits are found with git's default
history simplification for a path, the same as `git log -- <path>`.
* I first used `--full-history`, but `process_policy.git_verb_options` does not allow it for `rev-list` (scanner
  finding `GIT_OPTION_FORBIDDEN`). Rather than widen a reviewed rule, I used the default. `diff-tree --no-renames` was
  dropped for the same reason; plumbing `diff-tree` does no rename detection without `-M`.
* In a linear history the two readings are identical, and r2's history from F onwards is linear (single writer).
* In a merge topology where a side branch adds and later removes the record, the default can hide those commits.
* I did not read `p309_driver.recorded_freeze` or the coordinator's `sandbox_base()`. Their equivalence to this
  implementation should be confirmed at the delta review.

### V4: `P309_SCRATCH_ROOT` (P7)

**`scratch_sandbox_base(environ=None, repo=None)`** returns `<P309_SCRATCH_ROOT>/fc2_sandbox_verifier`. It raises
`ScratchRootError(RuntimeError)`, and never falls back, when `P309_SCRATCH_ROOT`:
* is unset or empty;
* is not absolute;
* differs from its own `realpath`;
* is not an existing directory;
* lies inside the repository (equal to it or under it);
* overlaps, meaning equals, contains or lies inside, any `P309_FOREIGN_ROOTS` entry. Both the entry as given and its
  `realpath` are compared.

`P309_FOREIGN_ROOTS` is optional and `os.pathsep`-separated, and every entry must be absolute. A set-but-empty value,
or an empty entry, is refused as "not absolute": a fail-closed reading.

**The constructor.**
* `Sandbox.__init__` calls it as its first statement, on every construction.
* It also refuses a `fc2_sandbox_verifier` directory that is a symlink.
* `_assert_sandbox` and `teardown` use the validated directory.

**No session path left.**
* r1's `SANDBOX_BASE` constant is removed. So are the session id in the tests' ledger purpose string
  (`session_01RiV5…`) and `scratchpad/fc2_sandbox_verifier` in a ledger note.
* N10's fake worktree now lives under `sb.sandbox_base`.
* `test_V4_no_session_path_in_code` asserts that no string constant in the four Python files contains `/tmp/`,
  `scratchpad`, `claude-0` or `session_01`, outside the test itself.

**Note.** Plan R2-I2 proposed "a fixed default (`<repo parent>/p309_r2_scratch`)". The brief says to refuse when the
variable is unset, so there is no default here. The launcher must set `P309_SCRATCH_ROOT`; P7's `TMPDIR` is the
launcher's concern.

### V5: `VERIFY_RESULTS_SCOPED.json`: regenerated (see §6)

### V6: README

A "P309-r2" section is appended to `verify/README_VERIFY_SCOPED.md`. The r1 text is unchanged: +120 lines, 0 removed.

### V7: see §4

## 3. Per-file diff summary (against `e07e3ee8`, which equals F)

| file | +/− lines | AST summary (per top-level unit) |
|---|---|---|
| `verify/srk_verify_indep_scoped.py` | +10 / −6 | **string constants only:** `PRODUCTION_MARKER`, `_FNS_REL`, `_PROD_FIELDS` (campaign) and the `TestContext` docstring. **Added:** `PRIOR_PRODUCTION_REF_NAMESPACE`, `FORBIDDEN_REF_NAMESPACES`. **Structural:** `_validated_sandbox` only (the loop over both namespaces). Admission (`_admission`, `admission_decision`), verification, bands and kernels are byte-for-byte unchanged |
| `verify/scoped_sandbox.py` | +196 / −36 | **added:** `import re`; `FNS_DIR`, `FREEZE_RECORD_LEAF`, `SCRATCH_ENV`, `FOREIGN_ENV`, `SANDBOX_DIRNAME`, `_HEX40`, `_FORBIDDEN_REF_PREFIX_R1/_R2`; `ScratchRootError`, `_within`, `scratch_sandbox_base`; `FreezeRecordError`, `freeze_record_rel`, `_record_touching`, `sandbox_base_commit`; `Sandbox.assert_no_production_refs`, `.freeze_record_commits`, `.check_freeze_records`. **Removed:** `SANDBOX_BASE`. **Structural:** `_FORBIDDEN_REF_PREFIX` (now a tuple), `Sandbox.__init__`, `__exit__`, `_assert_sandbox`, `teardown`, `build_valid`. **Unchanged:** `_git`, `commit`, `_stage`, `update_ref`, `delete_ref`, `reset_hard_index`, `_assert_ref`, `_assert_path`, fixtures |
| `tests/test_verify_scoped.py` | +294 / −9 | **string constants only:** `_Ledgered.setUp` (session id removed), the `TestFC2Scoped` ledger note, N11 (campaign) and the docstring. **Structural:** `no_production_artifacts` (both namespaces) and N10 (campaign; `sb.sandbox_base`). **Added:** `import ast, shutil, tempfile`; helpers `_tree_of`, `_assigned`, `_def`, `_loads`, `_callees`, `_owners`; `_R1_NAMESPACE`, `_R2_NAMESPACE`, `_MY_FILES`; class `TestR2Verifier` (5 tests). The 21 ported tests and the other FC2 tests are unchanged |
| `verify/run_verify_all_scoped.py` | 0 | byte-identical (`45902e30…`) |
| `verify/VERIFY_RESULTS_SCOPED.json` | +1041 / −1036 | regenerated (§6) |
| `verify/README_VERIFY_SCOPED.md` | +120 / −0 | r2 section appended |

## 4. V7: the re-pin list (P6(g)) and the config entries step 4 needs

**Method.** Every AST hash below was computed on **CPython 3.11.15** (`/usr/local/bin/python3`) with the scanner's own
`p309_scan_pins.owner_hash` / `module_hash`, which is `sha256(ast.dump(node))`. The old column is r1's bytes (equal to
FNS2 at `e07e3ee8`) and the new column is r2's. In every row, the pinned value in `config/SCANNER_ALLOWANCE_P309.json`
equals the old hash.

**Hashes that change (5 entries in 4 places):**

| config list | file | entry | old (pinned) | new |
|---|---|---|---|---|
| `ref_mutation_functions` | `verify/scoped_sandbox.py` | `Sandbox.__init__` | `1820ef2698731ac4eb5c7648f4a99dc9887443576a6932dc68ca91887aa7d981` | `a8a819ffde52c3078f9a78f9b047d6014f7077052f6bf0d4d3865d4ebccf4b94` |
| `process_policy.reviewed_functions` | `verify/scoped_sandbox.py` | `Sandbox.__init__` | `1820ef2698731ac4eb5c7648f4a99dc9887443576a6932dc68ca91887aa7d981` | `a8a819ffde52c3078f9a78f9b047d6014f7077052f6bf0d4d3865d4ebccf4b94` |
| `process_policy.reviewed_functions` | `tests/test_verify_scoped.py` | `TestFC2Scoped.test_N10_production_cannot_be_synthesized` | `02b558f5cd4a07bc1b1bf1a83e4a4eac06bae2d9d88536e4a694990cccb8fba4` | `b11d41fde6c58ba71a48c7e921eae27a5a43e177096d27beb380219edb0d29cc` |
| `t7_exemptions` | `tests/test_verify_scoped.py` | `<module>` | `1398968829daf35fd0d52efc5faaee4dbc7f2f271c022c257417cdcd71b81f0c` | `0ebcd94a496e58ebc95914273e7c12c08b580cc33416b2ef4d015b597927f24a` |
| `import_policy.module_level_exemptions` | `verify/srk_verify_indep_scoped.py` | `multiprocessing` (module) | `9c72beccda731fe6ad1af6486c10cf5edfba37905ccf3a1c5346f2d534fdb3b6` | `56528523686818a0dee8cc7513af42d68e89e8455ceaa152d86c509a3e241247` |

**Unchanged** (checked):
* `ref_mutation_functions`: `Sandbox.commit`, `.update_ref`, `.delete_ref`, `.reset_hard_index`;
* `reviewed_functions`: `test_N13`, `scoped_sandbox._git`, `Sandbox._stage`, `Sandbox.commit`, and the variant's
  `_run_git`, `_git_ok`, `_changed_paths` and `TestContext.__init__`;
* `t7_exemptions` and `module_level_exemptions` for `run_verify_all_scoped.py` (`5ede1f0f…`).

**Reasons to update where the text has gone stale:**
* `t7_exemptions` for `test_verify_scoped.py`: unchanged in substance. The new tests add no module-attribute store.
* `reviewed_functions` `Sandbox.__init__`: still `gitdir_write` (alternates and shallow), now after the V3 base rule
  and the V4 directory check.
* `token_definitions`: the reason for `_FORBIDDEN_REF_PREFIX` (now the two constants below).

**Config entries that are not hashes (step 4; OD-R2-1 (b)):**
1. `names`: the variant's `PRODUCTION_MARKER` literal becomes `refs/p5y-k5-cell309-p309-r2/target-consumed` (the owner
   row). Without it, the scanner reports `TARGET_PATH` at variant:163.
2. `token_definitions`:
   * replace the entry (`verify/scoped_sandbox.py`, `_FORBIDDEN_REF_PREFIX`) with `_FORBIDDEN_REF_PREFIX_R1` and
     `_FORBIDDEN_REF_PREFIX_R2`;
   * add (`verify/srk_verify_indep_scoped.py`, `PRIOR_PRODUCTION_REF_NAMESPACE`);
   * add (`tests/test_verify_scoped.py`, `_R1_NAMESPACE`) and (`tests/test_verify_scoped.py`, `_R2_NAMESPACE`).

   The r2 entries are needed once r2's namespace token is in `production_tokens`. The r1 entries are needed as long
   as r1's token stays there (P18 keeps it).
3. `production_tokens` / `production_ref_namespace`: the coordinator's (P18), not changed by me.

**Scanner evidence (run in the scratch clone, whose config is r1's copy, i.e. step 4 not applied):**

| state | verdict | findings |
|---|---|---|
| r1 bytes (baseline) | PASS | 0 |
| my changes, before the option fix | FAIL | 15 |
| my final bytes | FAIL | 12, every one accounted for above (see below) |
| my final bytes, with the 5 re-pins and entries 1–2 applied to the clone's config copy, plus r2's token in `production_tokens` | **PASS** | **0**, anywhere; the pin tool reports nothing stale; the clone's config was then restored byte for byte |

Before the option fix, the extra findings were 2 × `rev-list --full-history` and 1 × `diff-tree --no-renames`, both
removed (§2, V3).

The 12 findings on the final bytes, by cause:
* **TARGET_PATH** for the r2 marker: entry 1.
* **MARKER_TOKEN** for the three r1-namespace constants: entry 2.
* **Stale pins:**
  * REF_MUTATION_UNLISTED ×3, GIT_WRITE_UNLISTED and GITDIR_WRITE ×2 from the `Sandbox.__init__` pins;
  * GITDIR_WRITE from the N10 pin;
  * IMPORT_UNLISTED `multiprocessing` from the variant's module pin.

## 5. Tests and controls

**Counts.** 42 = 21 ported self-tests + 16 FC2 tests (D1, N01–N13, P1, P2) + 5 r2 tests (`TestR2Verifier`).

| run | topology | `P309_SCRATCH_ROOT` | tests | result |
|---|---|---|---|---|
| A: V1, V2 and V4 applied, **before V3** | development (clone at `2183b8f2`) | fresh scratch dir | 40 | **OK** (99.1 s) |
| B: **after V3** | development | fresh scratch dir | 42 | **OK** (101.2 s) |
| V5 harness `--unit-tests` | development | fresh scratch dir | 42 | **OK** (101.1 s) |
| C: after V3 | **post-freeze**: synthetic F′ `5284140a`, record-only FR′ `bbb2095d`, then a checkpoint commit `f4de4058`; sandboxes based on F′ | fresh scratch dir | 42 | **OK** (103.1 s) |

After every run, 0 sandboxes were left and 0 refs existed in either production namespace.

**V4 negative controls in the test file** (`test_V4_scratch_root_refusals`). Each case asserts `ScratchRootError` and
the specific reason:
* unset; empty; relative;
* trailing separator; a `..` component; a symlink (the last three: "differs from its realpath");
* missing; a file;
* the repository itself; inside the repository;
* a foreign root that is equal, containing, contained, reached through a symlink, or the second entry of a list;
* a foreign entry that is relative; a foreign variable that is empty; a foreign list with an empty entry.

Positive controls: a valid root, and a valid root with two non-overlapping foreign entries.

**Constructor-level V4 controls** (in the clone, `Sandbox()` with the environment set, via `v3_control.py v4`): unset,
relative, symlink, missing, inside the repository, overlapping a foreign root, and a relative foreign entry.
* Each raised `ScratchRootError`.
* None created a directory: the scratch root stayed empty.

**V3 control in the scratch clone** (brief, Tests). The clone had no remote, no push URL and no ref in either
production namespace. F′ commits the three changed files; FR′ adds only `<FNS2>/ledger/FREEZE_RECORD.json` with
`freeze_commit = F′`.

| topology (HEAD) | expected | observed |
|---|---|---|
| development (`2183b8f2`) | base = HEAD | base `2183b8f2`, mode `development`; sandbox record commits 0; base history 0 |
| FR′ (`bbb2095d`) | base = F′ | base `5284140a` (F′), mode `post-freeze`; sandbox record commits 0; base history 0 |
| checkpoint commit after FR′ (`f4de4058`) | base = F′ | base `5284140a`, `post-freeze`; 0; 0 |
| **mutant:** the old rule (base = HEAD), in-process only, at the checkpoint | the P6(b) postcondition raises | `FreezeRecordError: the sandbox holds 1 commits touching …/ledger/FREEZE_RECORD.json; the flow expects 0`; no sandbox left |
| freeze_commit ≠ the only parent | raise | `FreezeRecordError` (freeze_commit `2183b8f2` is not its commit's only parent `5284140a`) |
| the record commit touches another path | raise | `FreezeRecordError` (touches 2 paths) |
| a second commit changes the record | raise | `FreezeRecordError` (2 commits touch the record) |
| a second commit removes the record | raise | `FreezeRecordError` (2 commits) |
| the record is not JSON | raise | `FreezeRecordError` (not JSON) |
| freeze_commit is missing | raise | `FreezeRecordError` (no 40-hex freeze_commit, None) |
| freeze_commit is not 40-hex | raise | `FreezeRecordError` (`'F-prime'`) |
| the record commit is a merge (parents F′ and a side commit) | raise | `FreezeRecordError` (2 parents) |

For every malformed shape, no sandbox directory was created.

**Disclosed control error, corrected.** My script's first attempt at the merge shape was built wrongly: the side
commit's directory did not exist at F′. As a result:
* the "side" commit was empty, and `commit-tree` dropped the duplicate parent;
* the resulting commit was a second, **valid** record-only child of F′ on another line. It was correctly accepted with
  base F′, so it was a valid shape, not a merge;
* because that control does not use the context manager, it left one sandbox, which I deleted by its literal path.

I then rebuilt the merge properly (row above).

## 6. V5: regeneration and wall time

* **Command:** `run_verify_all_scoped.py --jobs 3 --unit-tests --out <scratch>`, with the unchanged harness. It ran in
  the scratch clone, in this cloud session, with `P309_SCRATCH_ROOT` a fresh scratchpad directory.
* **Scope:** decoy-only (`RNS/evidence/srk_decoys` and `srk_decoys_cell`), FC2 admission only; REAL-band probes are
  parse-time refusals under the tripwire.
* **Wall time: 594.7 s**, from 2026-10-01T12:36:58Z to 12:46:53Z. I1 took 493.0 s (r1: 492.4 s) and the unit tests
  101.1 s. Exit 0.
* **Comparison with r1's file** (`bad3ffa7…` at F), over 2369 entries (103 genuine, 2266 mutants):
  * verdicts, expectation rules, expectation flags and identity-to-committed flags are **all identical**: 0 verdict
    differences;
  * 41 entries differ in bytes, only by the declared substitution `p5y_k5_cell309_p309_r1` → `…_r2`, in the grant path
    inside "no grant" refusal reasons;
  * summary counts are identical: production 87 certificates (87/71), 1914 mutants (1914/1595), by rule R0 696, R1
    970, R2-refuse 335; test context 16 (16/16), 352 mutants (352/240);
  * the `differences` lists (335 and 112 entries) are equal as multisets; their order follows worker completion.
* **No finding.** The new file records the r2 variant `e82d6812…`, harness `45902e30…`, the tests `94db67d4…` and 42
  OK.

## 7. Notes for the coordinator and the delta review

1. **V3 semantics.** The record-history walk uses git's default path simplification, not `--full-history` (§2, V3).
   Please confirm equivalence with `sandbox_base()` and `recorded_freeze`, which I did not read.
2. **The `P309_SCRATCH_ROOT` default.** The brief's "unset → raise" overrides plan R2-I2's fixed default for this
   helper. The launcher and the drill must export it, as they must for the coordinator's consumers.
3. **The repository rule.** It refuses only a root inside the repository, as the brief states. A root that *contains*
   the repository is not refused by that rule. Its sandboxes would still lie outside the repository.
4. **`P309_FOREIGN_ROOTS` set to an empty value is refused**, not treated as unset (fail closed).
5. **`Sandbox(tag, expect_freeze_records=0)`.** This is a new keyword. The harness and tests call `Sandbox(tag)` as
   before.
6. **Output files.** `verify/R2_VERIFIER_EXEC_LEDGER.jsonl` (`.jsonl`) and this report (`.md`) are allowed by
   `process_policy.file_suffixes`. Neither has an executable bit.
7. **A stale path in a QC16 note.** The tests no longer name the session in their ledger purpose. Any QC16 note that
   quotes the old purpose string, or `scratchpad/fc2_sandbox_verifier`, is stale.
8. **Verification semantics are untouched.** The variant's admission and verification code is unchanged apart from the
   literals and `_validated_sandbox`. Bands, kernels, Taylor models, admission checks 1–10 and review mode are
   byte-identical in AST.

## 8. Disclosure: every read, run and write

**Reads, of the real repository (read-only).**
* **Governance:**
  * `BRIEF_R2_VERIFIER_AUTHOR_1.md`, `R2_PLAN.md` and `R2_PLAN_ADDENDUM_2.md` (full);
  * `REVIEW_R2_PLAN.md` (headings; conditions lines 345–538) and `R2_PLAN_ADDENDUM_1.md` (headings; lines 38–172);
  * `R2_LITERAL_DISPOSITION.json` and `R2_LITERAL_DISPOSITION_SUPPLEMENT_1.json` (rows and keys for my files).
* **Config:** `config/SCANNER_ALLOWANCE_P309.json`: the entries naming my files, `process_policy` (keys,
  `git_verb_options`, `file_suffixes`, `env_keys`), `scope`, the T7 rule, `production_tokens`,
  `production_ref_namespace`, `mutating_git_verbs`, `names` and `token_definitions`.
* **Code:**
  * `code/p309_env.py`: a grep of its path and log lines only;
  * `code/p309_scan.py`: lines 20–79, 120–160, 1046–1082, 1182–1282 and 1315–1472, plus greps;
  * `code/p309_scan_pins.py`: lines 1–105 (full).
* **My six files** and my own r1 files' hashes.
* **Git metadata:**
  * `git log`, `status` and `for-each-ref`;
  * `git show 4c754a73:` and `HEAD:` of my six files;
  * `git diff` of FNS2.
* The decoy evidence was read only by the unchanged harness and tests, as in r1.

**Not opened or read:**
* `code/p309_guard.py` and its tests, `code/p309_driver.py`, and the coordinator's `sandbox_base()`;
* any producer module (`RNS/impl/srk_*.py`) and the overnight modules;
* any cell-305–309 value, and any cell-307/308 file or hash;
* r1's FREEZE_RECORD content, only its commit id seen via `rev-list`.

There was no network access.

**Runs.** One row per command is in `verify/R2_VERIFIER_EXEC_LEDGER.jsonl`. Rows 1–3 were written retroactively, for the
three commands run before the ledger existed. Rows 25 and 31 record exit 0, but their commands exited 1: row 25's
module-style test invocation failed to import under `-I`, and row 31's scan was the expected FAIL with 12 findings.
Row 59 records this correction. Every execution of test, harness, scanner or control code was in the
scratch clone:
* runs A, B and C, and the quick `TestR2Verifier` runs;
* the V5 harness;
* the scanner and pin tool (baseline, stage 2, final) and the config simulation;
* the V3 and V4 control scripts;
* the V7 hash script, which imports the clone's scanner modules read-only with `-B`.

Git writes happened in the clone only:
* the synthetic F′, FR′, checkpoint, side and malformed commits;
* the detached checkouts;
* `remote remove origin`.

**Writes in the real repository** (FNS2 only):
* `verify/srk_verify_indep_scoped.py`, `verify/scoped_sandbox.py` and `tests/test_verify_scoped.py`, via edits;
* `verify/VERIFY_RESULTS_SCOPED.json`, copied from the regeneration;
* `verify/README_VERIFY_SCOPED.md`, appended;
* the new `verify/R2_VERIFIER_CHANGES_REPORT.md` and `verify/R2_VERIFIER_EXEC_LEDGER.jsonl`.

`run_verify_all_scoped.py` is untouched. Nothing else changed: `code/`, `config/`, `fc2/`, `governance/`,
`start_state/`, r1's namespace and the research namespace all have a clean status. There was no commit, push, ref,
stash or config change.

**Scratch writes** (under `<scratchpad>/r2/`):
* the clone, **deleted by its literal path** after the controls;
* seven `P309_SCRATCH_ROOT` directories, empty at the end and deleted;
* my helper scripts (`xl.py`, `run_v5.sh`, `v3_control.py`, `v3_control.sh`, `v5_compare.py`, `v7_repins.py`,
  `v7_simulate.py`), logs, JSON outputs, `pins_old/` and `pins_new/`, and the README draft.

`<scratchpad>/r2/` also holds earlier files that are not mine and that I neither read nor modified (`rd2_*`,
`reviewer_exec_ledger*`, `REVIEW_SRK_R2*`, …).
