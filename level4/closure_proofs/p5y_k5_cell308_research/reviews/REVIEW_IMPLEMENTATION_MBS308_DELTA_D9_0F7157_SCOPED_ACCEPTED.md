# Cell-308 MB-S fresh delta reviewD9: mutant coverage repair 0f7157fb
DELTA_ACCEPTED

Reviewer: reviewD9 (fresh non-holder; no MB r1 run observation supplied)
Date: 2026-10-03

## Candidate and scope

Reviewed immutable successor commit `0f7157fb4641f6a3b9dfe6b955c7a3d12b154b91`
(`repair final mutant coverage for history and QC12`), parent
`40761f7b3633d47a964b96879839ef449f08334b`, clean branch
`p5y-k5-cell308-mbs-r1`. The exact delta changes only
`level4/closure_proofs/p5y_k5_cell308_mbs_r1/tests/test_mbs308_mutants.py` (5 insertions,
5 deletions): stale MB104, MQ44 and MQ50 mutation fragments are replaced with fragments
present in the accepted implementation. No code, configuration, constants, or accepted
rules changed. The prior final-matrix rejection is preserved in
`REVIEW_IMPLEMENTATION_MBS308_DELTA_D9_FINAL40761F7B_REJECTED.md`.

## Scoped evidence

I independently ran the affected mutant subset with the repository's synthetic, target-free
mutant harness using my own scratch/base store:

`/private/tmp/codex-cell308-reviewd9/mutants_affected_0f7157_run2.json`

SHA-256: `82f50b3e3b4174f7da2e6e4b2ee7c3bd952ca8e400346d899ef0e2b5761897a2`.

The report is 3/3 killed, 0 survivors, 0 not-run, no disk refusal, unmutated baseline
passes, and no per-mutant errors. Each result is verified and assertion-killed (rc 1):

- MB104: `cases::t_measure_refuses_and_invalidates` — persistent `ALREADY_DESIGNATED`
guard mutation killed.
- MQ44: `qualify::t_qc12s_raw_text_only_match` — raw/decoded mismatch fail-closed mutation
killed.
- MQ50: `qualify::t_qc12s_json_escaped_figure` — outside-post-freeze decoded-scan
mutation killed.

`git diff --check` between `40761f7b` and `0f7157fb` is clean and the candidate worktree
is clean.

## Scoped verdict and boundary

This accepts the repair of the three previously rejected mutant definitions and their
focused regression evidence. It does not accept the full 297-mutant matrix or complete
final-byte qualification evidence: the prior report recorded 294/297 with these three
failures, and a fresh full-matrix report for `0f7157fb` remains required. No target,
measurement, official qualification, freeze, apply, grant, marker, pending-result, seal,
or host-setting operation was performed by this reviewer.
