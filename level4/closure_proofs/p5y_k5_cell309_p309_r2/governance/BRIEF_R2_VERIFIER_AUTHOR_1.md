# Brief: the verifier author's changes for P309-r2 (gate step 3)

This brief is committed before it is issued (C5). It follows plan addendum 2, F11.

## Who and why

**Recipient.** The independent author of r1's verifier-side files:
* `verify/srk_verify_indep_scoped.py`;
* `verify/scoped_sandbox.py`;
* `verify/run_verify_all_scoped.py`;
* `verify/README_VERIFY_SCOPED.md`;
* `verify/VERIFY_RESULTS_SCOPED.json`;
* `tests/test_verify_scoped.py`.

The coordinator does not make these changes (owner rulings 2, GRANT ADMISSION CODE, applied to r2 as a constraint).

**Context.**
* **The campaign.** r2 (`p5y_k5_cell309_p309_r2`, FNS2) is a successor campaign for qualification infrastructure and
  execution-host durability. The scientific object is inherited byte for byte.
* **Its plan, as governed:**
  * `governance/R2_PLAN.md`;
  * `governance/REVIEW_R2_PLAN.md` (conditions P1–P23);
  * `governance/R2_PLAN_ADDENDUM_1.md`;
  * `governance/REVIEW_R2_PLAN_FOLLOWUP_1.md` (F1–F11);
  * `governance/R2_PLAN_ADDENDUM_2.md`.
* **The files you will edit.** At step 3a (commit `e07e3ee8`), FNS2's `verify/` and `tests/` were copied byte for byte
  from r1's freeze F (`4c754a73`). Your files under FNS2 are therefore exactly r1's. Edit them **in FNS2 only**.

## Hard boundaries (unchanged from r1)

* **The target.**
  * NEW Γ309 TARGET EVALUATIONS = 0.
  * No REAL-band evaluation. Keep the existing `prepare` tripwire.
  * No target-equivalent proxy.
* **Refs.** No ref is ever created, updated or deleted under `refs/p5y-k5-cell309-p309-r1/` or
  `refs/p5y-k5-cell309-p309-r2/`, anywhere, sandboxes and tests included (F1). The production grant path is never
  written.
* **Git.** No git write in the real repository: no commit, push, ref, stash or config change. The coordinator commits
  your files after you report.
* **Scope.**
  * Edit only the six files above, under FNS2.
  * Do not touch r1's namespace, `code/`, `config/`, `fc2/` or `governance/`.
  * No cell-305–309 values. No cell-307/308 file contents, which also excludes hashes.
  * No network.
* **Inputs.** Do not read decoy outputs beyond what the existing harness reads.

## The changes

### V1: literals, per `governance/R2_LITERAL_DISPOSITION.json`

OD-R2-1 is implemented provisionally as option (b) (addendum 2, F7).

**Variant (`verify/srk_verify_indep_scoped.py`):**
* line 163, `PRODUCTION_MARKER` → `refs/p5y-k5-cell309-p309-r2/target-consumed` (`owner`);
* line 170, `_FNS_REL` → `level4/closure_proofs/p5y_k5_cell309_p309_r2/` (`rename`; this carries the grant and result
  paths);
* line 175, `campaign` → `p5y_k5_cell309_p309_r2` (`binding`).

**Tests (`tests/test_verify_scoped.py`).** Lines 791 and 815 carry the production-shaped campaign value, and follow the
binding.

**Kept unchanged:**
* every schema-format name (`P309_GRANT/1`, etc.);
* the verifier history commit `6522db10` in the README;
* the variant's research-namespace (RNS) reads.

### V2: both production namespaces forbidden (F1)

* **`verify/scoped_sandbox.py`.** `_FORBIDDEN_REF_PREFIX` becomes a tuple that holds **both** r1's and r2's namespace.
  Every mutating guard refuses either.
* **The variant's `TestContext` / `_validated_sandbox` refusal** (today it uses `PRODUCTION_REF_NAMESPACE` only) refuses
  a sandbox that holds a ref under **either** namespace.
* **Static check.** Add a static (AST or literal) check, in `tests/test_verify_scoped.py`, that both namespaces appear in
  each of those two places.
* **No control may create such a ref.** If you need a prior-marker prefix control, the only permitted name is
  `refs/p5y-k5-cell309-TEST-ONLY-prior/x`. You will then have to allow it explicitly in `_ALLOWED_REF_PREFIXES`, with
  its reason. Otherwise, do not add it.

### V3: the sandbox base rule (P6(e); plan §4)

**The rule.** `Sandbox.__init__` must not base the sandbox on the live HEAD when HEAD's history holds this namespace's
freeze record, `<FNS2>/ledger/FREEZE_RECORD.json`. In that case the base is the recorded freeze commit F. Otherwise
(development) the base is HEAD.

**Implement it independently in `verify/`.** Do not import from `code/` or `tests/`. It must match the semantics of the
coordinator's `sandbox_base()` and of `p309_driver.recorded_freeze`:
* exactly one commit in HEAD's history touches the record;
* that commit touches only the record;
* its only parent equals the record's `freeze_commit`;
* any other shape **raises**, failing loudly rather than in the shape of a refusal.

**Pre- and postconditions (P6(b)).**
* The base's history holds **0** commits touching the record.
* After your fixtures, the sandbox holds exactly the number of record commits your flow expects. That is 0 for the FC2
  tests, unless a test builds one deliberately.

**Static check (P6(e)).** No other read of the real repository's HEAD is used as a sandbox base in `verify/` or
`tests/test_verify_scoped.py`.

### V4: `P309_SCRATCH_ROOT` (P7)

**Remove the hard-coded session path.** `SANDBOX_BASE` (`scoped_sandbox.py` line 29) is a hard-coded session path.
Derive it as `<P309_SCRATCH_ROOT>/fc2_sandbox_verifier`.

**Refuse loudly** (raise, never fall back) if any of these is true of `P309_SCRATCH_ROOT`:
* it is unset or not absolute;
* it differs from its own `realpath`;
* it is not an existing directory;
* it lies inside the repository;
* it overlaps any path in `P309_FOREIGN_ROOTS`. That variable is optional, `os.pathsep`-separated and absolute; the
  launcher sets it to the cell-308 paths.

**No session path left.** No hard-coded session or scratchpad path may remain in executable code of your six files.
Comments and the README may describe the layout.

### V5: `VERIFY_RESULTS_SCOPED.json` (P2)

**Recommended: regenerate it** for r2's variant bytes with the existing harness. The run is decoy-only and FC2
admission-only:
* at most 3 jobs, as in r1's settings;
* in this cloud session;
* with `P309_SCRATCH_ROOT` set to a fresh directory under your scratchpad;
* report the wall time.

The verdicts must match r1's (the expectation rule is unchanged). Any difference is a finding: report it, and do not
"fix" it to match.

**Alternative.** If you judge regeneration inappropriate, mark the file explicitly as inherited from r1, with r1's
variant sha256, and say why. QC16 then regenerates it at the r2 qualification.

### V6: README

**Append** an r2 section to `verify/README_VERIFY_SCOPED.md`. Do not rewrite the r1 text. The section gives:
* V1–V5;
* the variant's new sha256;
* the test counts.

### V7: the re-pin list (P6(g))

**List** every pinned hash your changes alter, with the old and new hash, each AST hash computed on **CPython 3.11**.
This environment's `/usr/local/bin/python3` is 3.11.15. The list includes:
* `TestFC2Scoped.test_N10_production_cannot_be_synthesized`;
* the module hashes of the T7 exemptions for `test_verify_scoped.py` and `scoped_sandbox.py`;
* the variant's `multiprocessing` exemption;
* anything else.

**Do not edit `config/`.** The coordinator applies the re-pins at step 4.

## Tests

* **The full self-tests and FC2 tests in `tests/test_verify_scoped.py`.** They must pass, with
  `P309_SCRATCH_ROOT` set, before and after V3.
* **A V4 negative control for each refusal case.**
* **A V3 control.** In a scratch clone, under your scratchpad, with **no push URL** and no ref in either production
  namespace:
  * commit a synthetic F′ and its record-only child FR′;
  * show that `Sandbox` bases on F′ there, and on HEAD in the plain development topology;
  * show that a malformed record raises.

  The scratch clone is yours. Delete it by its literal path when you are done.

## Output

**`verify/R2_VERIFIER_CHANGES_REPORT.md`.** Its line 2 is exactly one of:
* `VERIFIER_R2_CHANGES_DONE`;
* `VERIFIER_R2_CHANGES_BLOCKED`, with reasons.

The report gives:
* the V1–V7 outcomes;
* the per-file diff summary;
* the re-pin list;
* the test and control results;
* the regeneration wall time;
* a disclosure of every read, run and write.

**`verify/R2_VERIFIER_EXEC_LEDGER.jsonl`.** One row per command you run.

**Do not commit.**
