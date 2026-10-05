# F-DRILL-ORDER review

**Status on the adoption candidate `93d55063`:** fixed. This is the minimal reviewed-order correction, plus the one
scanner pin that the correction makes stale, re-pinned with r2's own tool.

All of this work is result-free. No drill was run through the launcher, nothing was frozen, and nothing was evaluated.

## 1. Where the drill tooling is

| item | location (r2 `101ef2cb`) |
|---|---|
| drill tool | `level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_topology_drill.py` |
| function that builds the synthetic freeze | `make_topology(clone, scratch)`, lines 215–236, called once from `main()` (line 426) |
| generators it runs (unmodified) | `code/make_freeze_params.py`, `code/make_freeze_manifest.py`, `code/p309_placeholder_check.py` |
| tiers | `--tier cloud`: items one by one through `items_table()` / `run_item()`; never calls the runner's `main()`. `--tier worker`: the runner's `main()` through `code/p309_launch.py --mode drill` (the 8d worker-tier drill) |
| runner precondition the order breaks | `code/p309_qualify.py` `main()`, r2 lines 728–731: `make_freeze_manifest.py --check` must succeed, otherwise `QUALIFICATION REFUSED: the freeze manifest does not regenerate identically` |

## 2. The exact current order (r2 `101ef2cb`, `make_topology`, lines 218–220)

```python
gen = [run_py([sys.executable, "-B", str(code / "make_freeze_manifest.py")], clone, scratch),
       run_py([sys.executable, "-B", str(code / "make_freeze_params.py")], clone, scratch),
       run_py([sys.executable, "-B", str(code / "p309_placeholder_check.py")], clone, scratch)]
```

The current order is **manifest → params → placeholder check**.

## 3. Why the manifest is incomplete under that order

- `make_freeze_manifest.build()` pins every tracked or untracked (non-ignored) file of r2's namespace whose first
  directory is in `FROZEN_DIRS = ("code", "config", "fc2", "freeze", "tests", "verify", "governance")`. The only
  exception is the manifest itself (`EXCLUDE = {OUT_REL}`). So the parameter file `freeze/P309_FREEZE.json` is pinned
  **if it exists when the manifest is built**.
- `make_freeze_params.py` writes `freeze/P309_FREEZE.json`. It does not read the manifest, so nothing makes
  params-after-manifest necessary.
- Under the current order, the manifest is built **before** the parameter file exists, and so it lacks that pin. The
  parameter file is then created, and F′ is committed with both files.
- The runner's `main()` re-runs `make_freeze_manifest.py --check`. This recomputes the manifest from the tree, which
  now contains `freeze/P309_FREEZE.json`, so the recomputed manifest differs from the committed one. The runner
  therefore refuses before any attempt. The worker-tier drill (which runs `main()`) cannot pass. The cloud tier never
  calls `main()`, so it never sees the defect.
- A real freeze uses params → manifest. r1's real recorded F manifest pins its own `freeze/P309_FREEZE.json` (below).

**Demonstration** (`evidence/F_DRILL_ORDER_DEMO.json`, tool `tools/drill_order_demo.py`):
- two fresh no-local scratch clones of r2 `101ef2cb`;
- r2's own unmodified generators, run exactly as `make_topology` runs them (`python -B <script>`, cwd in the clone);
- then the runner's precondition, `make_freeze_manifest.py --check`.

| order | generators rc | manifest pins `freeze/P309_FREEZE.json` | code pins (`"path"` entries incl. data) | `--check` |
|---|---|---|---|---|
| current r2 (manifest, params, placeholder) | 0, 0, 0 | **no** | 182 (193) | rc 1, **MANIFEST DIFFERS** |
| corrected (params, manifest, placeholder) | 0, 0, 0 | **yes** | 183 (194) | rc 0, **MANIFEST IDENTICAL** |
| r1's real recorded F manifest (reference) | n/a | **yes** (its own params file) | (125) | n/a |

The independent reviewer reproduced this in its own scratch clone (182 vs 183 code pins, DIFFERS vs IDENTICAL), and the candidate's rehearsal built F′ with 183 code pins. The same defect was found independently in Task 2. The baseline crash matrix was first invalid (every run refused)
until the replica builder used the real-freeze order (`R2_FAILURE_MATRIX.json` R15).

## 4. The proposed and applied corrected order

```python
gen = [run_py([sys.executable, "-B", str(code / "make_freeze_params.py")], clone, scratch),
       run_py([sys.executable, "-B", str(code / "make_freeze_manifest.py")], clone, scratch),
       run_py([sys.executable, "-B", str(code / "p309_placeholder_check.py")], clone, scratch)]
```

The corrected order is **params → manifest → placeholder check**, the order of a real freeze. The diff is exactly the
two swapped lines (`git diff 101ef2cb 93d55063 -- code/p309_topology_drill.py`: 2 insertions, 2 deletions).

## 5. Consequence: one scanner pin

`make_topology` is AST-pinned in r2's scanner allowance (`config/SCANNER_ALLOWANCE_P309.json`,
`ref_mutation_functions[20]`), because it makes `git add` / `git commit` calls in the drill clone. Swapping two calls
changes its AST.

- **Without a re-pin**, r2's own `code/p309_scan_pins.py --list` reports `make_topology: STALE HASH` ("1 NOT
  CURRENT"; `evidence/SCAN_PINS_LIST_BEFORE_REPIN.txt`). r2 at `101ef2cb` itself is "all current"
  (`evidence/SCAN_PINS_LIST_R2.txt`).
- **The re-pin** was made with r2's own maintenance tool, `code/p309_scan_pins.py --refresh` ("recompute the AST
  sha256 of the ALREADY-LISTED entries (pre-freeze only)"), in a scratch clone. Its output names exactly one entry. The
  resulting file was copied byte for byte.
- **Structural diff of the allowance** (`evidence/ALLOWANCE_DIFF.json`): 1 228 leaves before and after; exactly one
  changed: `/ref_mutation_functions[20]/ast_sha256` `9b59c12f…` → `8af1bb78…`. No entry was added or removed, and
  one text line changed. The new value equals `sha256(ast.dump(make_topology))` of the candidate, recomputed
  independently. After the refresh, `--list` reports "all current" (`evidence/SCAN_PINS_LIST_AFTER_REPIN.txt`).
- **Untouched:** `exactly_once_sites` (owner-ratified), `reviewed_functions` and every other pin.

## 6. No scientific or target code is affected

- **Files changed by this correction:** `code/p309_topology_drill.py` (one function, `make_topology`) and one hash in
  `config/SCANNER_ALLOWANCE_P309.json`. AST diff of the drill file (`evidence/AST_DRILL_R2_VS_CANDIDATE.json`): of 17
  top-level functions, only `make_topology` changed. The other 16 and every module-level statement are
  byte-identical. The drill's process-policy-pinned functions (`git`, `run_py`, `controls`) and its other
  ref-mutation-pinned function (`main`) are byte-identical.
- **What `make_topology` does:**
  - it runs, inside a scratch drill clone that has no remote, the generators that write the synthetic F′;
  - it commits F′, FR′ and a checkpoint-style record **in that clone only**.
  The change alters which generator runs first, nothing else. The generators themselves, the runner, the driver, the
  guard, the evaluators, every gate, the tests, the ledgers and the evidence are unchanged.
- **The order matters only for the synthetic, non-target freeze of a drill.** A real freeze is made by the owner's
  freeze procedure, not by this function, so the order of a real freeze is unaffected.
- **No target quantity:**
  - the drill imports nothing from the runner, driver, guard, generators or tests (module docstring F2);
  - the generators read only package and pin files (data files are hashed, never parsed);
  - the demonstration ran only the generators and `--check`.

## 7. Verdict on F-DRILL-ORDER

**Fixed correctly on the adoption candidate:**
- the drill now builds F′ in the order of a real freeze;
- the runner's manifest precondition is met (`MANIFEST IDENTICAL`);
- the only collateral change is the one stale pin, refreshed by r2's own tool.

**Validation still owed** (it can only happen on a durable host with the launcher and the systemd unit, owner-gated):
the worker-tier drill itself (`p309_launch.py --mode drill`). This session never runs the launcher or the drill tool;
the session guard refuses both by name.
