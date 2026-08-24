# Final re-audit failure diagnoses

These failures occurred while reproducing committed closure campaigns during
the final global audit. None exposed a scientific inconsistency, changed a
frozen acceptance rule, or modified historical evidence.

## F1 — legacy clean-tree guard rejected the active audit worktree

- **Observed:** the Track 1B reproducer rejected the main worktree after the
  new final-audit namespace had been created but before it was committed.
- **Cause:** its historical integrity test treats any uncommitted path as a
  protocol mutation, including unrelated post-closure audit files.
- **Resolution:** replay the historical campaign at the audited starting commit
  in a detached temporary worktree. No test or evidence was weakened.

## F2 — temporary environment links appeared as untracked paths

- **Observed:** the first detached replay still failed the legacy clean-tree
  guard after local virtual-environment and Lean-cache links were installed.
- **Cause:** the temporary links were visible to `git status`.
- **Resolution:** use a temporary `core.excludesFile` scoped only to the local
  environment/cache mounts. The detached commit and protected files were not
  changed.

## F3 — Stage E cache absent from the detached worktree

- **Observed:** Track 3A/3B reached its embedded authoritative verifier, where
  11 Stage E tests failed with `FileNotFoundError` for the three source data
  files.
- **Cause:** `level4/stage_e/data/_cache/` is intentionally git-ignored and is
  therefore absent from a fresh worktree.
- **Resolution:** supply the existing local cache to the detached replay. The
  cache contents remain checked against the frozen Stage E manifest.

## F4 — a directory symlink was not traversed by the novelty hash audit

- **Observed:** after mounting the Stage E cache as a directory symlink, Stage E
  passed 59/59, but the novelty protected-history audit counted 33 instead of
  41 files under `level4/stage_e`.
- **Cause:** `Path.rglob()` did not traverse the directory symlink; the missing
  count of eight exactly matched the eight frozen Stage E cache files.
- **Resolution:** copy those eight existing immutable cache files into the
  ignored temporary cache directory. This restores the filesystem shape the
  historical digest expects without changing the repository.

## F5 — `git check-ignore` rejected a V3 cache symlink

- **Observed:** the file-mounted replay passed Stage E, Stage F, the earlier
  re-audit, D4, novelty, and V2, then V3 failed only
  `test_raw_archives_are_gitignored` because the archive path was beyond a
  symbolic link.
- **Cause:** Git deliberately refuses `check-ignore` queries that traverse a
  directory symlink, even when the symlink path itself is excluded.
- **Resolution:** use an actual ignored temporary `data_cache` directory with
  copy-on-write copies of the two existing frozen archives. The V3 acquisition
  step still verifies their official sizes and SHA-256 digests.

The final accepted replay must pass from the file-mounted detached worktree,
and the main audit must separately pass protected-history verification and the
authoritative repository verifier.
