# Receipt: A6c candidate 5, Phase-1 disclosure (Cell-308 Cloud route r1), 2026-10-24

**Status: RECEIPT OF OWNER-RELEASED EVIDENCE · ADMINISTRATIVE EFFECTS ONLY · NO DETERMINATION · NO PHASE 2.**
`new_target_evaluations = 0` · `cell309_activity = none`.

```text
A6C_CANDIDATE_5   PHASE_1_COMPLETE
                  ELIGIBILITY_PENDING
                  NO_PHASE_2_AUTHORIZATION
```

## 1. The record

| item | value |
|---|---|
| file | `reviews/external/A6C_EXTERNAL_CANDIDATE5_PHASE1_DISCLOSURE.md` |
| bytes / sha256 | 6,026 / `4b383452afc235d6fd0a2e10b88b01b4c3096ec428adaece0997560cc9ac2b2a`. The owner-stated count and digest **MATCH**. Both were checked from the git object before the file was read |
| blob | `da00f1ca5e07751de397bdf4063964910e30337f` |
| owner release | branch `owner-review/cell308-A6c-candidate5`, commit `5d78af7e9d6d19a0afe128a4abff13bcc1ec388a`. Its only parent is `9d1f61d87404f8ba56bbbe6268c246b18934e876`. It adds only this file |
| recording | `codex/cell308-claude-r5-integration` fast-forwarded to `5d78af7e`. The file is byte-identical: not retyped. No force-push and no history rewrite |
| pre-read scan | confined scoped scan **before** display (scanner `e103c196`, configuration `ab0104c6`, `python3 -I -B`, counts only): 1 text file, **0 findings**, controls detected, PASS |
| governing protocol | the canonical brief `ledger/briefs/A6C_REDERIVATION_CLOUD_R1.txt` at `797248fc` (17,499 bytes, `489dec78…2f0c`), as amended by brief erratum E14 at `cd2fb234` (4,293 bytes, `13622974…39e`, adopted in `OWNER_DECISION_A6C_ERRATUM_E14_ADOPTION_20261024.md`). E14 pins the manifest at `be78ccd5` (20,603 bytes, `45e2d97d…3999`) |
| appointment | the owner reports that the candidate verified the brief, E14 and the pinned manifest. The appointment's date and exact text were not supplied to the recorder. Line 1 of the disclosure reads "E14 is treated as in force per your appointment" |

## 2. The disclosure, item by item (as disclosed; nothing upgraded)

| brief item | disclosed (line) | status |
|---|---|---|
| 1 identity | role: "A6C external candidate 5, Cloud route r1" (5). Platform: "Codex agent in a managed cloud environment" (6). Thread ID: **UNVERIFIED**; "none was exposed in my execution context" (7). Account arrangement: **UNVERIFIED** beyond the current Codex-managed execution (8) | present |
| 2 context and history | available: the appointment, platform instructions, environment metadata and the three verified pinned documents (12). No compaction or summary indicated (13). Prior turns, hidden history and omitted context: **UNVERIFIED** (14). No history from other candidate, coordinator, recorder, Claude or owner-assistance conversations (15) | present |
| 3 prior roles | none known in Cell-308, MB r1, MB-S, Cloud r1, ReBaseGuard or Cell-309 (19). The roles named in the brief or appointment are "referenced … but none is mine" (20). Personal owner-assistance, integration, review, recording or A6b-trace involvement: **UNVERIFIED** (21). Any prior risk rating: **UNVERIFIED** (22) | present |
| 4 excluded sources | "No direct read, search, listing, hash, or process contact targeted any of these" (26). Each listed source is **UNVERIFIED** beyond its name appearing in the brief (28–31, 33). The MB r1 namespace is **UNVERIFIED** "beyond textual/path references in supplied metadata" (32). MB r1 runtime or host observations and Cell-309 material: **UNVERIFIED**; none read (34–35). "No excluded source contents reached me" (37) | present |
| 5 the coordinator, recorder and environment | no relationship or contact established with `session_01S66r3p84SFdY6Vc4RchSWr` or `session_01EKeyysqJNJgvrdiLFAA43o` (41–42). Whether either can reach the candidate: **UNVERIFIED** (43). Environment `ccarenv_b64_Y2NhcmVudl8wMGQ1ZmE4NGE0NDQ4MTkxYjdkMDQ5ODliNzJlMzBkMQ` (44). No attached project, artifact, repository or terminal session shown by metadata (45). Isolation beyond that metadata: **UNVERIFIED**; "I do not certify isolation" (46) | present |
| 6 checkout or clone | no automatic checkout or clone shown; no checkout or repository path read; no `git`, repository listing, recursive search or repository-worker operation (50–52). `/workspace` not inspected (101) | present |
| 7 tools | `functions.exec_command`, used only for `/tmp` scratch work and the three raw URLs (56). `apply_patch`, `download_file`, `view_image`: available, unused (57). `spawn_agent`, `send_message`, `followup_task`, `list_agents`, `wait_agent` and thread-management tools: available, unused (58). Cloud environment status and wait tools: used for environment readiness and metadata only (59). No remote-worker, repository-worker or conversation-management tool used (60) | present |
| verification | brief 17,499 bytes, `489dec78…2f0c`; E14 4,293 bytes, `13622974…39e`; manifest 20,603 bytes, `45e2d97d…3999` (64–68). All **MATCH** the canonical values. "The manifest was not edited, reconstructed, or reserialized" (70) | — |
| Phase 2 inputs | "No Phase 2 input was fetched" (1) | — |
| commands and paths | four command blocks, given in full (76–99). Paths touched: `/tmp`, `/tmp/a6c_phase1_VHvnYr` and the three files in it (101). "Phase 1 is complete; stopped here" (101) | — |

## 3. The recorder's administrative observations (facts only; no eligibility judgment)

* **O1. Environment.** The disclosed environment ID's payload decodes, as a string, to
  `ccarenv_00d5fa84a4448191b7d04989b72e30d1`.
  * It is **not equal** to the coordinator's `env_01GTgmTdDaUY28GtoGZVi3QY`.
  * It is **not equal** to the environment candidate 4 disclosed (`ccarenv_76474f1a701481918809c534e7b1b17b`).
  * This says **nothing** about account or control identity, which stay UNVERIFIED.
* **O2. Fetches beyond the brief in Phase 1.** Brief line 16 reads "Fetch nothing except this brief. Then stop."
  * The candidate also fetched E14 and the pinned manifest (lines 85–86), and displayed all three files with `cat`
    (96–98).
  * The disclosure attributes this to the appointment (lines 1 and 12). The owner reports that the candidate verified
    all three.
  * The appointment text is not on the record, so the recorder cannot compare it. The manifest holds only paths,
    commits, byte counts, digests and URLs. No allowlisted input was fetched.
* **O3. Redirects.** The three fetches used `curl --fail --location` (84–86), which follows redirects. No HTTP status
  or final URL is recorded.
  * E14.2 item 4 ("no redirects followed") governs the Phase 2 entry fetches. It is not stated for these Phase 1
    fetches.
  * The fetched bytes match the pinned values in every case.
* **O4. The decline list.** No category is disclosed as applicable. None is affirmatively excluded either: personal
  involvement and any prior risk rating are UNVERIFIED (lines 21–22). "Not candidates 1–4, and not the A6b candidate"
  rests on lines 19–20.
* **O5. Wording in item 4.** The MB r1 namespace line says "supplied metadata" (32), where the other lines say "the
  brief". What that metadata was is not stated.
* **O6. Reach-capable tools.** Agent-spawning, messaging and thread-management tools were available, and are disclosed
  as unused. Environment status tools were used, for readiness and metadata only.
* **O7. Commands complete.** All commands are given in full, with no abbreviations; candidate 4's O3 does not recur.
  The paths list is complete as stated.

## 4. State and non-effects

* **Eligibility is PENDING.** That is the owner's individual determination. The recorder makes none.
* **Every UNVERIFIED finding stands as disclosed:**
  * thread identity and account arrangement;
  * omitted or hidden history;
  * personal prior involvement and any risk rating;
  * prior contact with the excluded sources;
  * whether the coordinator or recorder can reach the candidate;
  * isolation and hidden attachment status.
* **Not done:**
  * no eligibility is issued;
  * no proceed instruction is sent;
  * the recorder fetched no Phase 2 input and performed no re-derivation;
  * nothing is adopted, and no statement is issued;
  * the register was not read.
* **Not added:** a matrix erratum and a ledger line. The owner asked for the disclosure and its receipt.
* **The recorder:** `claude_cloud_recorder_20261022` (`session_01EKeyysqJNJgvrdiLFAA43o`), as disclosed in
  `OWNER_STATEMENT_7_RECEIPT_20261022.md` §5. It is never the candidate, and it had no contact with candidate 5.
