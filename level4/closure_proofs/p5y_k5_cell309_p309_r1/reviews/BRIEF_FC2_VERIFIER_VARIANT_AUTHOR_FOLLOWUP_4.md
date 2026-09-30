# Brief: verifier author, follow-up 4 (the two remaining forwarded operands in `verify/scoped_sandbox.py`)

This brief is committed before it is issued (condition C5).

**Recipient:** the independent author of the verifier variant and its sandbox helper. The role separation holds: you
make the change, test it and report; the coordinator commits your file as you leave it.

## Why

Your follow-up-3 report found two more places in `verify/scoped_sandbox.py` where a caller-supplied value reaches git
as a bare operand:
* `Sandbox.reset_hard_index` passes `commit` to `_git(self.root, 'read-tree', commit)`;
* `Sandbox.update_ref` passes `target` to `_git(self.root, 'update-ref', ref, target)`. The `ref` is checked against
  the allowed prefixes, but `target` is not.

To close this class in the helper completely (R4F2-C1(e)), place `--end-of-options` before the caller-supplied operands
there too.

## The change (only this)

* In `reset_hard_index`: `_git(self.root, 'read-tree', '--end-of-options', commit)`.
* In `update_ref`: `_git(self.root, 'update-ref', '--end-of-options', ref, target)`.

Keep your own argument order for any other options. Change nothing else. `verify/srk_verify_indep_scoped.py`, the
tests and `verify/run_verify_all_scoped.py` must stay byte-identical.

## Then

1. Run `python3 -I -S -B tests/test_verify_scoped.py` once, ledgered with notes prefixed "verifier author:".
2. Report the new sha256 of `verify/scoped_sandbox.py` and the test counts.
3. Do not commit.

## Boundaries (unchanged)

* No grant exists. NEW Γ309 TARGET EVALUATIONS must stay 0.
* Never create, arm or consume any ref under `refs/p5y-k5-cell309-p309-r1/`.
* TEST names only in sandboxes.
* No 305–309 value; no git writes.
