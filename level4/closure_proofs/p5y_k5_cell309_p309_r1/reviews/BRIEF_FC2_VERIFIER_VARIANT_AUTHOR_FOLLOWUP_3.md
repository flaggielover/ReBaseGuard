# Brief: verifier author, follow-up 3 (one hardening line in `verify/scoped_sandbox.py`; R4 follow-up 2, R4F2-C1(e))

This brief is committed before it is issued (condition C5).

**Recipient:** the independent author of the band-scoped verifier variant and its sandbox helper, author of:
* `verify/srk_verify_indep_scoped.py`;
* `verify/scoped_sandbox.py`;
* `tests/test_verify_scoped.py`.

The role separation of your earlier briefs holds. The coordinator does not edit your files. You make the change,
test it, and report.

## Why

R4's follow-up-2 review (`reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_2_P309.md`, condition R4F2-C1(e)) requires that an
operand forwarded from a function's parameters into a git command is either:
* preceded by `--end-of-options`;
* passed as the argument of a literal option; or
* validated.

In `Sandbox.commit`, the `parents` values reach git in two places:
* as the arguments of `-p` to `commit-tree`, which is fine;
* as a bare operand of `read-tree` in `subprocess.run(['git', '-C', self.root, 'read-tree', parents[0]], …)`.

A value beginning with `-` there would be parsed as a `read-tree` option, for example `--index-output=<path>`. Today's
callers pass git-produced commit ids, so the case is inert. The rule is general, however.

## The change (only this)

In `verify/scoped_sandbox.py`, `Sandbox.commit`, change the `read-tree` call so that `--end-of-options` precedes the
forwarded parent:

```python
subprocess.run(['git', '-C', self.root, 'read-tree', '--end-of-options', parents[0]], check=True, env=env,
               capture_output=True)
```

Git 2.43 accepts this. The coordinator checked in a scratch repository: `git read-tree --end-of-options HEAD` succeeds,
and `git read-tree --end-of-options --index-output=/dev/null` fails with "Not a valid object name".

**Change nothing else.** In particular, leave `verify/srk_verify_indep_scoped.py` and the tests byte-identical.

## Then

1. Run `python3 -I -S -B tests/test_verify_scoped.py` once. Ledger the run through `code/p309_env.py` with notes prefixed
   "verifier author:", as in your earlier follow-ups.
2. Report the new sha256 of `verify/scoped_sandbox.py` and the test counts.
3. Do not commit. The coordinator commits your file as you leave it, citing this brief.

## Boundaries (unchanged)

* No grant exists. NEW Γ309 TARGET EVALUATIONS must stay 0.
* Never create, arm or consume any ref under `refs/p5y-k5-cell309-p309-r1/`, anywhere.
* TEST names only in sandboxes.
* No 305–309 value; no git writes.
