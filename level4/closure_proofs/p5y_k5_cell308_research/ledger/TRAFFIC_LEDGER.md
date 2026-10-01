# MB-S traffic ledger (owner supplement 1, Part VII; compact, approximate)

Bytes "transferred" means bytes intentionally moved between machines by the operation itself (not the API traffic of
the agent that runs it, which cannot be metered per operation from here).

| UTC | operation | host | class | local scratch | bytes transferred | evidence retained | AWS |
|---|---|---|---|---|---|---|---|
| 2026-10-01T11:11Z | network / placement audit | Mac (+1 status command on AWS, 1 failed on Vultr) | REVIEW_ONLY | 0 | < 10 kB | ledger/network_2026-10-01/NETWORK_AND_PLACEMENT_AUDIT.md | status only |
| 2026-10-01T11:13Z | builder5 resumed (brief 50, final-byte re-runs) | Mac | LOCAL_HOST_BOUND | about 0.9 GB peak per mutant, deleted per mutant | 0 | JSON reports in builder5 scratch | no |
| 2026-10-01T12:35Z | builder5 final-byte runs done; T2 committed 555f4cbf | Mac | LOCAL_HOST_BOUND | matrix peak 0.9 GB (95 GB deleted one sandbox at a time) | 0 | JSON reports (builder5 scratch, 67 MB) | no |
| 2026-10-01T12:45Z | reviewQ6 (brief 53) and builder6 (brief 54) started | Mac | REVIEW_ONLY / LOCAL_HOST_BOUND | own base stores (about 0.5 GB each), sandboxes deleted per run | 0 | review file; worktree edits | no |
