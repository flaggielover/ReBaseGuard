# Recovered briefs and prompts to every agent of the research and formal campaigns (incident review condition C5)

Every instruction the coordinator gave to another agent in this session is reproduced **verbatim**, byte-for-byte from
the session transcript, in `AGENT_BRIEFS_TRANSCRIPT.jsonl`, one JSON object per line, with its transcript timestamp
and the sha256 of its text. The file covers:
* the firewalled readers A, B and C (items 1–3);
* the independent verifier's author (item 4 and its follow-ups);
* reviewers R1, R2 and R3, and their follow-ups;
* the incident-independence reviewer;
* the FC2 variant author.

**Post-hoc commitment evidences content, not timing.** The briefs listed below were not committed before they were
issued. Their timing rests on the transcript timestamps alone, which git cannot corroborate. This gap is carried in
`disclosed_liabilities`, as condition C8 requires. From now on every brief is committed before it is issued, as
`reviews/BRIEF_*` shows.

**Note on item 1.** Its firewall wording contains an illustrative placeholder number, in the form "Γ = <number> is
NOT allowed". It is a made-up example of a forbidden disclosure, not a value of any cell.

| # | transcript UTC | tool | label | chars | sha256 | committed before issue? |
|---|---|---|---|---|---|---|
| 1 | 2026-09-29T12:59:21.099Z | Agent | 309 history firewalled reader | 4928 | `b1640293f6c0722a…` | no |
| 2 | 2026-09-29T12:59:37.190Z | Agent | Governance/protocol conventions reader | 4056 | `fa45406f6f681b38…` | no |
| 3 | 2026-09-29T13:02:57.435Z | Agent | Sanitized theory digest writer | 3775 | `7b858621d0c100ef…` | no |
| 4 | 2026-09-29T13:46:33.253Z | Agent | Build independent SRK certificate verifier | 5033 | `2c6d9818896d7440…` | no |
| 5 | 2026-09-29T13:55:24.079Z | SendMessage | Spec update: optional weight_block key | 522 | `83fd3a51b7786e47…` | no |
| 6 | 2026-09-29T13:58:55.097Z | SendMessage | Spec update: optional taboo kernel mode | 527 | `fc4e34eaa8faedc4…` | no |
| 7 | 2026-09-29T15:10:32.291Z | SendMessage | Resume after container restart | 741 | `309297008b3fe904…` | no |
| 8 | 2026-09-29T15:21:56.276Z | SendMessage | Spec erratum SE-1 on mutant #2 | 452 | `3096bae0fe341433…` | no |
| 9 | 2026-09-29T15:25:30.975Z | Agent | Independent SRK route review R1 | 2381 | `3446f78d33487b65…` | brief R1 committed |
| 10 | 2026-09-29T15:53:04.290Z | SendMessage | Scanner markers added; certificates changing | 926 | `577ca2ce23eb4c7e…` | no |
| 11 | 2026-09-29T16:14:05.485Z | Agent | Independent route review R2 (phase A) | 2480 | `21a3b1d0e2fe5052…` | brief R2 committed |
| 12 | 2026-09-29T23:09:52.029Z | SendMessage | R2 phase B: evidence complete, issue verdict | 4067 | `5e0dcfe5bbeeb79b…` | no |
| 13 | 2026-09-29T23:27:35.645Z | SendMessage | Fix 7q quarantine mutant reason (R2 condition C3) | 2354 | `179135497d46ef04…` | no |
| 14 | 2026-09-29T23:36:27.442Z | SendMessage | Resume C3 v2 rerun after container restart | 1642 | `b866d75acb6eeddb…` | no |
| 15 | 2026-09-29T23:41:50.841Z | SendMessage | Fix the two failing verifier self-tests | 1307 | `e95ec633bdeb3ebd…` | no |
| 16 | 2026-09-29T23:47:18.612Z | SendMessage | R2 phase C: conditions-closure check | 3483 | `05bc79a176399850…` | no |
| 17 | 2026-09-30T00:00:12.405Z | SendMessage | R2 phase D: check C4 closure | 2685 | `a7e1749d08ee79e4…` | no |
| 18 | 2026-09-30T00:09:46.554Z | Agent | Independent package review R3 | 1871 | `bc711792c9558695…` | brief R3 committed |
| 19 | 2026-09-30T00:34:34.200Z | SendMessage | R3 follow-up: check notes N1-N19 settled | 3458 | `468e331951821c9a…` | no |
| 20 | 2026-09-30T00:41:28.821Z | SendMessage | R3 second follow-up: rev. 2b closure check | 2288 | `7a6d8735d8aa7a34…` | no |
| 21 | 2026-09-30T00:47:04.566Z | SendMessage | R3 third follow-up: D1 and polish check | 2336 | `d171297611fc1376…` | no |
| 22 | 2026-09-30T01:47:22.061Z | Agent | Independent incident-independence review P309 | 2034 | `4503242cf524e70d…` | yes (reviews/BRIEF_INCIDENT_INDEPENDENCE_P309.md) |
| 23 | 2026-09-30T01:49:53.487Z | SendMessage | Build grant-scoped verifier variant (FC2b) | 4411 | `37fc8c14b9786f93…` | no |
| 24 | 2026-09-30T02:44:27.216Z | SendMessage | Independent check of U2 corrected proposition | 1750 | `cb5f498924dff1e9…` | yes (reviews/BRIEF_U2_CHECK_P309.md) |
| 25 | 2026-09-30T02:51:03.634Z | SendMessage | FC2 rev. 2: build the band-scoped verifier variant | 1799 | `98e3bf176896e6e7…` | yes (reviews/BRIEF_FC2_VERIFIER_VARIANT_AUTHOR.md) |

The per-item full sha256 values are in the JSONL file. Agent identifiers are withheld.
