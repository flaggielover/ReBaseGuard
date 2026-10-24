# Owner decision A1: corrective Phase 1 scope amendment for A6c candidate 5 (Cell-308 Cloud route r1), 2026-10-24

**Status: OWNER DECISION (the owner's words recorded verbatim in §1) · RECORDED BY claude_cloud_recorder_20261022.**
§1 governs. §2 and §3 apply it, and §1 prevails over them if they differ. `new_target_evaluations = 0` ·
`cell309_activity = none`.

```text
A6C_CANDIDATE_5   PHASE_1_COMPLETE (under the A1 corrective scope amendment)
                  ELIGIBILITY_PENDING
                  NO_PHASE_2_AUTHORIZATION
```

## 1. The owner's decision (verbatim, as issued on 2026-10-24)

> I choose A1.
>
> Formally amend the Phase 1 scope for candidate 5 only. The amendment permits fetching and reading the pinned E14 erratum and the pinned Phase 2 manifest in addition to the canonical brief, provided that:
>
> - each file is fetched at its exact pinned commit and verified by byte count and SHA-256 before reading;
> - no Phase 2 input is fetched;
> - no external source is consulted;
> - no repository, git, worker, conversation, or collaboration tool is used;
> - no result is adopted and no Phase 2 authorization is implied.
>
> Record that candidate 5 followed the owner-issued appointment, that the scope amendment is being issued now as a corrective owner record, and that it does not cure any later-proven role, exposure, independence, or control violation under E-5.
>
> Return candidate 5 to:
>
> PHASE_1_COMPLETE
> ELIGIBILITY_PENDING
> NO_PHASE_2_AUTHORIZATION
>
> Create the owner decision record, receipt, readiness-matrix bookkeeping, and append-only ledger line. Do not issue eligibility and do not send a proceed instruction yet.

## 2. The decision, item by item

1. **Selected option.** A1, from the options prepared after
   `A6C_CANDIDATE5_PHASE1_SCOPE_DEVIATION_RECORD_20261024.md`. The amendment validates candidate 5's completed Phase 1.
2. **Who it applies to.** **Candidate 5 only.** For every other candidate, brief line 16 stays as written: "Fetch
   nothing except this brief."
3. **What it permits.** In addition to the canonical brief (`797248fc`, 17,499 bytes, `489dec78…2f0c`), fetching and
   reading:
   * brief erratum E14: `ledger/briefs/A6C_REDERIVATION_CLOUD_R1_ERRATUM_E14.txt` at
     `cd2fb2340b3a51f0b3e03c3a9e7dfc63279e5dd4`, 4,293 bytes,
     `13622974f3f9f961ec6f8a41a6d33ef1279c0156a21397bbcd479c55bd83a39e`;
   * the pinned Phase 2 manifest: `ledger/briefs/A6C_PHASE2_MANIFEST_R1.json` at
     `be78ccd5286ad0de4548e04361b3798d331f89bb`, 20,603 bytes,
     `45e2d97dbb07a24ef40d0a9027e2c67c08b6e44b36626742b46b9e68ec363999`.
4. **Its conditions:**
   * each file is fetched at its exact pinned commit and verified by byte count and SHA-256 before reading;
   * no Phase 2 input is fetched;
   * no external source is consulted;
   * no repository, git, worker, conversation or collaboration tool is used;
   * no result is adopted, and no Phase 2 authorization is implied.
5. **Candidate 5 followed the owner-issued appointment.** The fetches of E14 and the manifest were included in that
   appointment.
6. **A corrective record.** This amendment is issued **now**, as a corrective owner record, after candidate 5 acted.
   No amendment was recorded before the candidate acted.
7. **No cure.** This amendment does **not** cure any later-proven role, exposure, independence or control violation
   under E-5. This preserves E-5 §2 item 6.
8. **Status.** Candidate 5 returns to `PHASE_1_COMPLETE · ELIGIBILITY_PENDING · NO_PHASE_2_AUTHORIZATION`. This
   replaces the status in `A6C_CANDIDATE5_PHASE1_SCOPE_DEVIATION_RECORD_20261024.md`. That record stays unchanged as
   the record of the deviation.
9. **Non-effects:**
   * no eligibility is issued, and no proceed instruction is sent;
   * the canonical brief, E14 and the manifest are unchanged;
   * nothing is adopted;
   * no statement is issued, and no T6, adoption, host, freeze or execution decision is made.

## 3. Candidate 5's disclosed actions against the conditions (recorder's check; facts only)

| condition | disclosed (line) | as disclosed |
|---|---|---|
| exact pinned commits | the only URLs are the brief at `797248fc`, E14 at `cd2fb234` and the manifest at `be78ccd5` (84–86) | **consistent** |
| verified before reading | `wc -c` and `sha256sum` (91–92) come before `cat` (96–98). All three match (64–70) | **consistent** |
| no Phase 2 input | "No Phase 2 input was fetched" (1) | **consistent** |
| no external source | `exec_command` used only for `/tmp` and "the three specified raw URLs" (56) | **consistent** |
| no repository, git, worker, conversation or collaboration tool | no `git`, repository listing, recursive search or repository-worker operation (52). Conversation and agent tools available, unused (58). No remote-worker, repository-worker or conversation-management tool (60). Cloud environment status and wait tools were used, "for environment readiness and metadata only" (59) | **consistent as disclosed**. Line 59's tools are not in the condition's list on their face; whether they fall under it is the owner's reading |
| no result, no Phase 2 authorization | no result exists; no determination and no proceed instruction | **consistent** |

* **Not verified.** These are the candidate's own statements. The recorder cannot observe candidate 5's environment.
  The disclosure's UNVERIFIED findings stand.
* **Unaffected by this decision:** receipt observation O3 (the fetches followed redirects; no HTTP status recorded).
