# Incident 309R1-04: Phase-4 drafting began before any route was FREEZE_READY (process deviation; no target information)

| field | value |
|---|---|
| found | 2026-09-30 ~01:1xZ, by the coordinator, prompted by independent package review R3 (follow-up 2, D1) |
| rule | The owner's instruction ("PHASE 4 … If and only if one route becomes genuinely FREEZE_READY: Prepare …") and the charter (`README.md`: "protocol_prep/: prepared only if a route is independently reviewed as FREEZE_READY") |
| what happened | The coordinator drafted Phase-4 documents in its **uncommitted scratchpad** long before any FREEZE_READY verdict. `P309_PROTOCOL_DRAFT.md` was first written at 2026-09-29 14:11:58Z and `P309_FORMAL_PACKAGE_DRAFT.md` at 14:12:43Z. Both came before review R1's verdict (NOT_READY, ~15:55Z). They were edited at 16:13–16:41Z and 23:29Z. The scratch manifest generator ran at 23:11:03Z (file creation) and 23:47:29Z (refresh). Those two runs read git metadata and hashed committed code bytes. The research namespace received no Phase-4 material until after R2's final FREEZE_READY (commit f026c80b, 2026-09-30 00:06Z) |
| target information | **None.** The drafts contain no 305–309 number and no quantity derived from 309. They were not used to select the route, a parameter or a reviewer verdict |
| review contact | Review R1 and review R2 never saw the drafts: R2 reported `protocol_prep/` as empty, since it was untracked and outside its reading. The committed package was reviewed only after FREEZE_READY, by review R3 |
| risk | A procedural and motivational risk: drafting the endpoint early can create a bias toward reaching it. It is mitigated by independent reviewers who had no access to the drafts, and by the fact that every repair was driven by reviewer findings |
| liability | **LOW** (process deviation; no target information). Recorded under the owner's no-concealment rule. It is to be assessed by the incident-independence review, together with the three rule choices of candidate rev. 2 |
