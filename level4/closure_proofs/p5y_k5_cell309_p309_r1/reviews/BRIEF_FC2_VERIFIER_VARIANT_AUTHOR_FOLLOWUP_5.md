# Brief: verifier author, follow-up 5 (the last caller-supplied operand in `verify/scoped_sandbox.py`)

This brief is committed before it is issued (condition C5).

**Recipient:** the independent author of the verifier variant and its sandbox helper. The role separation holds.

## Why

Your follow-up-4 report found the last bare caller-supplied operand. In `Sandbox.reset_hard_index`,
`_git(self.root, 'update-ref', cur, commit)` passes the caller's `commit` without `--end-of-options`. The
fourth-delta record (A42) states that every caller-supplied operand in the helper is protected, so this one closes it.

## The change (only this)

In `reset_hard_index`: `_git(self.root, 'update-ref', '--end-of-options', cur, commit)`.

Change nothing else. Your follow-up-3 and follow-up-4 changes stay as they are.
`verify/srk_verify_indep_scoped.py`, the tests and `verify/run_verify_all_scoped.py` stay byte-identical.

## Then

1. Run `python3 -I -S -B tests/test_verify_scoped.py` once, ledgered with notes prefixed "verifier author:".
2. Report the new sha256 and the counts.
3. Confirm that no bare caller-supplied operand remains in the helper.
4. Do not commit.

## Boundaries (unchanged)

* No grant exists. NEW Γ309 TARGET EVALUATIONS must stay 0.
* No ref under `refs/p5y-k5-cell309-p309-r1/`; TEST names only in sandboxes.
* No 305–309 value; no git writes.
