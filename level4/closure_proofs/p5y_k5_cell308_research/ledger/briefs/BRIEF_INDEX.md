# Agent briefs of the cell-308 research campaign (incident review C5)

Every brief and follow-up message sent by the coordinator to a sub-agent, in order. Files are verbatim copies of the
prompt text as sent (the coordinator re-typed them from its own context; whitespace may differ from the transmitted
bytes, content does not). This directory is a sanctioned location because brief 01 names committed cell-308 values
(stream A's pre-registered reconstruction targets). No other brief contains a committed tail figure or a
308-derived scale; each was checked by the scanner (`code/c308_quarantine.py --scan` covers `ledger/` only as
sanctioned, so the check below is a separate grep recorded in `BRIEF_CHECK.json`).

| # | file | agent | kind | launched (UTC, approx.) | tail figures? |
|---|---|---|---|---|---|
| 01 | 01_streamA.txt | stream A (history + C3 knockout) | Agent | 2026-09-28 12:4x | **yes, by design** (committed values to reproduce: C3 §K row, C4 §4 statement) |
| 02 | 02_streamC.txt | stream C (A0 certifier) | Agent | 12:5x | no |
| 03 | 03_streamD.txt | stream D (independent verifier) | Agent | 12:5x | no |
| 04 | 04_streamE.txt | stream E (assembly) | Agent | 12:5x | no |
| 05 | 05_reviewMB.txt | Theorem MB proof review | Agent | 13:0x | no |
| 06 | 06_resumeA.txt | stream A resume (network error) | SendMessage | ~13:4x | no |
| 07 | 07_resumeC.txt | stream C resume (network error) | SendMessage | ~13:4x | no |
| 08 | 08_streamF2.txt | F2 independent reconstruction | Agent | ~14:2x | no |
| 09 | 09_finishC.txt | stream C: batch-3 crash | SendMessage | ~15:0x | no |
| 10 | 10_followupD.txt | stream D follow-up (C2b PL format) | SendMessage | ~15:0x | no |
| 11 | 11_builder.txt | formal builder | Agent | ~15:1x | no |
| 12 | 12_builder_note1.txt | builder note 1 (F2, decreasing constants) | SendMessage | ~15:4x | no |
| 13 | 13_reviewA0.txt | A0 certifier review | Agent | ~15:4x | no |
| 14 | 14_streamF3.txt | F3 tuple re-derivation | Agent | ~15:4x | no |
| 15 | 15_builder_note2.txt | builder note 2 (G-R3b) | SendMessage | ~16:3x | no |
| 16 | 16_builder_note3.txt | builder note 3 (A0 conditions) | SendMessage | ~16:5x | no |
| 17 | 17_reviewINC.txt | incident-independence review | Agent | ~17:0x | no |
| 18 | 18_builder_note4.txt | builder note 4 | SendMessage | 2026-09-29 (added to this index later) | no |
| 19 | 19_builder_note5.txt | builder note 5 | SendMessage | 2026-09-29 (added to this index later) | no |
| 20 | 20_reviewQUAL.txt | qualification review (r2; not launched: r2 qualification FAILED) | Agent | not sent | no |
| 21 | 21_reviewR3REPAIR.txt | r3 host-environment repair review (pre-freeze) | Agent | 2026-09-29 ~05:3xZ | no |
| 22 | 22_reviewR3DELTA.txt | r3 repair delta review (F6; same reviewer resumed) | SendMessage | 2026-09-29 ~07:0xZ | no |
| 23 | 23_reviewQUAL_R3.txt | qualification review of freeze r3 (fresh) | Agent | 2026-09-29 ~10:3xZ | no |
| 24 | 24_reviewINTERRUPTION.txt | review of the execution-interruption recovery assessment (fresh) | Agent | 2026-09-30 ~15:4xZ | no |
| 25 | 25_reviewINTERRUPTION_DELTA.txt | delta review of addendum A1 (C2; same reviewer resumed) | SendMessage | 2026-09-30 ~18:0xZ | no |
| 26 | 26_reviewINTERRUPTION_R3.txt | re-check R3 of erratum E1 (same reviewer resumed) | SendMessage | 2026-09-30 ~18:4xZ | no |
| 27 | 27_reviewEXEC.txt | execution review (section 10 step 6, adapted; fresh) | Agent | 2026-09-30 ~19:0xZ | no |
| 28 | 28_reviewGOV.txt | successor-governance review (fresh) | Agent | 2026-09-30 ~19:2xZ | no |
| 29 | 29_reviewROUTE.txt | successor route review (fresh) | Agent | 2026-09-30 ~19:4xZ | no |
| 30 | 30_builderMBS.txt | successor MB-S r1 builder (Phases 4-8, target-free) | Agent | 2026-09-30 ~20:0xZ | no |
| 31 | 31_adjudicatorMB308.txt | MB r1 adjudication (section 10 step 7; fresh) | Agent | 2026-09-30 ~20:3xZ | no |
| 32 | 32_reviewGOV_DELTA.txt | governance delta review (same reviewer resumed) | SendMessage | 2026-09-30 ~21:0xZ | no |
| 33 | 33_reviewROUTE_DELTA.txt | route delta review (same reviewer resumed) | SendMessage | 2026-09-30 ~21:0xZ | no |
| 34 | 34_reviewADJ.txt | MB r1 adjudication review (section 10 step 8; fresh) | Agent | 2026-09-29 ~21:2xZ | no |
| 35 | 35_reviewROUTE_R3.txt | route re-check of erratum E1 (same reviewer resumed) | SendMessage | see ledger | no |
| 36 | 36_reviewINC_SUCCESSOR.txt | incident-independence re-rating for the successor (S12; fresh) | Agent | see ledger | no |
| 37 | 37_reviewIMPL_MBS.txt | successor implementation review (fresh, non-holder) | Agent | see ledger | no |
| 38 | 38_reviewINC2_T6.txt | bounded T6 ruling (reviewINC2 resumed) | SendMessage | see ledger | no |
| 39 | 39_readerUDB.txt | non-holder reader check of the user decision brief (MBS-10) | Agent | see ledger | no |
| 40 | 40_builderMBS_R124.txt | builder2 repairs R1/R2/R4 at the non-holder reviewer's request (M4) | SendMessage | see ledger | no |
| 41 | 41_ratifierMBS_R3.txt | non-holder constants ratification (R3 / M1) | Agent | see ledger | no |
| 42 | 42_ratifierMBS_apply.txt | non-holder applies the ratified constants + deterministic M33 test | SendMessage | see ledger | no |
| 43 | 43_reviewIMPL_DELTA.txt | implementation delta review R1-R4 (reviewIMPL resumed) | SendMessage | see ledger | no |

Times are approximate (the coordinator has no transmission timestamps); the ledger lines of each agent give the
first activity time.

**Erratum (2026-09-29 ~21:2xZ).** Rows 24–31 and 32–33 carry dates written as "2026-09-30 ~HH:MMZ". Those were local
(JST, +0900) dates paired with approximate UTC clock times. The UTC date of those launches is **2026-09-29**, and the
UTC times shown are approximate. The adjudicator's note gives rows 30 and 31 as about 18:20Z and 18:31Z, 2026-09-29.
Each agent's own ledger lines carry the exact UTC first-activity times. The rows themselves are not edited.

**Erratum 2.** The coordinator's approximate UTC times in rows 24–34, and in the erratum above, were not taken from a
clock and are unreliable. The authoritative times are the UTC timestamps of each agent's research-ledger lines. For
example, rows 30 and 31 are about 2026-09-29 18:20Z and 18:31Z. The rows are not edited.
