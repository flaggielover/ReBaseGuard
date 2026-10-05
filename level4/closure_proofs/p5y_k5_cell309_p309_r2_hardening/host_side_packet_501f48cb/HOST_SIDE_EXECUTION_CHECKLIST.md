# Host-side execution checklist for P309-r2 at `501f48cb` (deliverable 10 of 10)

**What this is.**
- The ordered, no-improvisation checklist for a **future, separate P309 host-side session**, and for the coordinator
  who receives its evidence. Every step names its document, its stop point and its record.
- It **authorizes nothing**. Each step runs only when the step's own authority exists. Steps marked **STOP** wait for
  the owner.
- Standing rules: NEW Γ309 TARGET EVALUATIONS = 0; no grant; no freeze; no qualification; Cell 309 OPEN.

## 0. Names used in every document of this packet

| name | meaning | fixed when |
|---|---|---|
| `<P309_USER>`, `<P309_GROUP>` | the P309 Unix user and its own group (proposed `p309`) | OD-R2-4 M1 |
| `<P309_HOME>` | that user's home | M1 |
| `<CLONE>` | `<P309_HOME>/ReBaseGuard`: the single-branch clone of `claude/p5y-k5-cell309-p309-r2` at `501f48cb` | F-1 |
| `<NS>` | `<CLONE>/level4/closure_proofs/p5y_k5_cell309_p309_r2` (every `code/…` command runs from here; SI X7) | F-1 |
| `<INTERP>` | the pinned CPython 3.11.15, e.g. `<P309_HOME>/opt/python3.11.15/bin/python3.11` | M5 |
| `<HOST_CONFIG>` | `<P309_HOME>/p309_host_config.json` (SI §3.1, with the six launch keys) | F-3, U-1–U-7 |
| `<HOST_CONFIG_NO_LAUNCH_KEYS>` | the same without the six launch keys, for `p309_host.py`'s direct subcommands | F-3 |
| `<P309_VOLDIR>`, `<SCRATCH_BASE>` | the P309 volume or directory; the base for fresh scratch directories | M2, F-4 |
| `<FOREIGN_ROOTS>` | the cell-308 checkout path(s), `:`-joined (Part A, A1) | 8c Part A |
| `<RUN_SCRATCH>` | the drill's own new, empty scratch root, e.g. `<SCRATCH_BASE>/drill8d_<UTC>` | 8d |
| `<PACKET_TOOLS>` | `<P309_HOME>/p309_packet_tools/` (this packet's `tools/`, sha256-verified) | F-5 |
| `<VERDICT_8B_FINAL>` | the 8b-final verdict record, as a P309 file on the host (a copy of the coordinator's record) | 8b-final |
| `<UTC>` | a `YYYYMMDDTHHMMSSZ` stamp chosen at the step | each step |
| `<utc>`, `<stamp>` | the launcher's stamp (unit and record); the drill's stamp (`drill_<stamp>`, `evidence/drill/<stamp>`) | printed by the launch |

**Fixed identities:**

| item | value |
|---|---|
| r2 commit and tree | `501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853`, `d7e2c8329b73d68ae07ca37192eb495674e572c9` |
| runner `code/p309_qualify.py` | sha256 `540df0552bfc31512289e30eaf1ead57bf82a4ac806f38080439c05c43f9a3af` |
| `code/p309_host.py` | blob `1763cd20…`, sha256 `ec9c8416159cf9e2e7372f97ce179a290def987007dc144591833615ca251f65` |
| `code/p309_launch.py` | sha256 `cd7e4ab920b3dae105f5a96d019a7c7f02b7563286ab64483438991fcf3485fb` |
| `code/p309_topology_drill.py` | sha256 `ef4ce1bf4a8dd7e9b0bfcb5947ccf1578e7797757daae29b22c6a6d5289ff0c1` |
| this packet | branch `claude/p309-r2-hardening-20261005`, directory `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/host_side_packet_501f48cb/`, at the commit that adds it; per-file sha256 in `PACKET_MANIFEST.json` |

## 1. The sequence

| # | step | who | document | gate before it | record produced | stop? |
|---|---|---|---|---|---|---|
| 1 | confirm the authority: OD-R2-3 (audit only) is approved; the host is message 3's shared AWS worker, or another host named by a new owner record | coordinator | `HOST_REQUIREMENTS_501F48CB.md` §9 | — | note in `host_evidence/` | — |
| 2 | the owner provides the separate P309 host-side session's access path and P309-only credential (never cell 308's) | owner | OD-R2-3 | 1 | — | **STOP** until provided |
| 3 | request Part A of the cell-308 form | coordinator → cell-308 operator | `CELL308_COORDINATION_8C.md` §6 | 2 | `CELL308_FORM_A_<UTC>` | wait for Part A |
| 4 | the 8a audit: A-01 (verified bytes; stdin; nothing written) and S-01…S-17, as a non-root user, at a time agreed by the operator | host session | `HOST_READ_ONLY_AUDIT_8A.md` §2–§3 | 2, 3 | the returned text bundle → `host_evidence/AUDIT_8A_<UTC>/` (hardening namespace only) | — |
| 5 | 8b-initial: evaluate every row; issue exactly one verdict | coordinator | `HOST_VERDICT_RULES_8B.md` | 4 | `VERDICT_8B_initial_<UTC>.json` | — |
| 6 | return point **R-1**: OD-R2-4, filled with the exact current states; AF-1 or AF-2 only if their rows fired | coordinator → owner | `OD_R2_4_HOST_CHANGE_PACKET.md`; `OWNER_RETURN_CONDITION.md` | 5 | the request text | **STOP** until the owner answers |
| 7 | record the owner's OD-R2-4 answer verbatim, additively (sha256 over the body, as for messages 4–6) | coordinator | — | 6 | `owner_reply_od_r2_4/…_VERBATIM.md` (hardening) | — |
| 8 | Part B of the cell-308 form, incl. the operator's consents for host-wide items | operator | `CELL308_COORDINATION_8C.md` | 6, 7 | `CELL308_FORM_B_<UTC>` | wait |
| 9 | apply **only** the consented items (M1–M5, F-1–F-5, U-1–U-7, any X-n consented), each with a before/after record; then the read-only proofs | host administrator + host session | `OD_R2_4_HOST_CHANGE_PACKET.md` §1–§4 | 7, 8 | `APPLIED_CHANGES_<UTC>.json` | — |
| 10 | fetch this packet's `tools/` into `<PACKET_TOOLS>`, and verify every file against `PACKET_MANIFEST.json` at the packet commit | host session (as `<P309_USER>`) | §3 below | 9 | the verification output | — |
| 11 | 8b-final: A-02a–d as `<P309_USER>` with `<INTERP>` | host session | `HOST_READ_ONLY_AUDIT_8A.md` §5 | 9, 10 | A-02 outputs; the check record | — |
| 12 | 8b-final verdict | coordinator | `HOST_VERDICT_RULES_8B.md` | 11 | `VERDICT_8B_final_<UTC>.json` | if not ACCEPTED: R-1b or wait; **STOP** |
| 13 | agree the window: Part C (≥ 9 h; 12 h recommended; QC-D5 margin); whole-host agreement (timers, cron, other accounts) | operator and others | `CELL308_COORDINATION_8C.md` | 12 | `CELL308_FORM_C_<UTC>` | wait |
| 14 | put the M4 holds into effect for the window; read-only proof | host administrator | OD-R2-4 M4 | 13 | the `APPLIED_CHANGES` addendum | — |
| 15 | pre-launch, step 1: the static checks in a disposable clone, judged by content | host session | `WORKER_TIER_DRILL_8D.md` §2 step 1 | 14 | `STATIC_8D_<UTC>.json` | on a failure: **STOP**, report |
| 16 | pre-launch, step 2: the A-02d check in a fresh check directory, `"blockers": []`, gate uids as agreed | host session | §2 step 2 | 15 | `launch_<utc>.json` (check directory) | on a blocker: wait for a quiet moment, then repeat this step only |
| 17 | pre-launch, step 3: the read-only pre-launch check (all 36 checks true) | host session | §2 step 3 | 16 | `PRELAUNCH_8D_<UTC>.json` | on a failure: **STOP** |
| 18 | **the launch** (once) | host session | `WORKER_TIER_DRILL_8D.md` §3 | 1–17 all true; D1–D11 | `LAUNCH_STDOUT_<UTC>.json`; `launch_<utc>.json` | — |
| 19 | monitoring, read-only only (≤ 10 min), and the incident rule only | host session | §4, §7 | 18 | observations | on INCIDENT: R-0 |
| 20 | after the unit ends: the validator; the static re-run; the origin check; E-1–E-5 | host session | §10; `WORKER_TIER_PASS_FAIL_RULES.md` | 19 | `VALIDATION_8D_<stamp>.json` and the others | — |
| 21 | Part D of the cell-308 form; restore the M4 holds (record); clean up P309 scratch by literal path after the coordinator confirms receipt. **No r2 commit or push** | operator; host administrator; host session | §10 | 20 | `CELL308_FORM_D_<UTC>`; the M4 restore record | — |
| 22 | return the whole 8d record set as text; the coordinator files it | host session → coordinator | §10 step 4 | 20, 21 | `host_evidence/DRILL_8D_<stamp>/` (hardening) | — |
| 23 | return point **R-2**: the classification; on PASS the filing authorization(s) and permission to issue the pre-freeze review; otherwise whether a further drill is allowed | coordinator → owner | `OWNER_RETURN_CONDITION.md` | 22 | the request text | **STOP** |
| 24 | if authorized: the filing commit(s) into r2 exactly as authorized (only the named paths; additive; fast-forward; no force), from `<CLONE>`'s uncommitted drill evidence plus the authorized host and governance files; verified from a fresh clone (each commit adds only the authorized paths; code, config, tests, verify and fc2 trees identical to `501f48cb`; QC15 A1–A10) | host session (push with the P309 credential) and coordinator (verification) | the owner's R-2 text | 23 | the r2 commit id(s); the verification record | — |
| 25 | issue the pre-freeze review to a fresh reviewer | coordinator | `PRE_FREEZE_REVIEW_PACKET.md` | 24 | the brief (committed before issue); the review, `.sha256` and ledger | — |
| 26 | return point **R-2b**, unless already authorized: file the review record into r2 as its own governance-only commit; verify | coordinator → owner; then filing | `OWNER_RETURN_CONDITION.md` | 25 accepted | the r2 commit | **STOP** until authorized |
| 27 | check O-1–O-10. Only if every one holds: return point **R-3**, OD-R2-0(D) together with the OD-R2-6(iii) host confirmation | coordinator → owner | `OWNER_RETURN_CONDITION.md` §2–§3 | 1–26 | the R-3 message | **STOP**. Nothing beyond this point is in this packet |

## 2. Never, at any step

- **Cell 308:** any read inside its checkout beyond the reviewed top-directory `stat()`/`access()`; any git command,
  signal, `renice` or `systemctl` action on it or its units; any change to its files, refs, evidence or processes.
- **Host changes:** anything not consented in writing under OD-R2-4 (or AF-1 or AF-2); any reboot, upgrade or package
  change outside the consented items; any sudo rule.
- **Writes during the audit or a window:** any write on the host during 8a; any `git` command, or any write, inside
  `<CLONE>` or `<RUN_SCRATCH>` while the drill unit runs.
- **Launcher modes and the driver:** `p309_launch.py --mode official` or `--mode host-rerun`; `p309_driver.py
  execute | seal-only | validate-grant`; a freeze; a qualification; a grant; any Γ309 or other target evaluation.
- **No silent repetition:** a second drill without a recorded owner decision; a resume; a "re-run to confirm"; a
  reused scratch or check directory.
- **r2 and its records:** a commit or push to r2 without the owner's filing authorization; a force push; editing any
  earlier record; filing marker-word text into r2.
- **Relays and hosts:** bulk data through the owner's machine; using this Cloud Session as the durable host; AWS,
  Vultr, SSH or paid compute from this Cloud Session.

## 3. Getting and verifying the packet's tools on the host (step 10)

As `<P309_USER>`, fetch `tools/prelaunch_readonly_check_8d.py` and `tools/validate_worker_drill_8d.py` from the
hardening branch at the packet commit. Use the same token-safe GitHub API form as A-01, with
`ref=<packet commit>`. Save them into `<PACKET_TOOLS>/`, then:

```bash
sha256sum <PACKET_TOOLS>/prelaunch_readonly_check_8d.py <PACKET_TOOLS>/validate_worker_drill_8d.py
```

Each value must equal its entry in `PACKET_MANIFEST.json` at the same commit. If one differs, do not use the tools;
report. The tools live outside `<CLONE>`, so the namespace stays clean (A4).

## 4. Where the records go

| record | location |
|---|---|
| everything before the R-2 filing authorization | the hardening namespace (`host_side_packet_501f48cb/host_evidence/…`), committed by the coordinator on `claude/p309-r2-hardening-20261005` |
| the drill's own evidence and ledger row | uncommitted in `<CLONE>` until R-2; then into r2 exactly as authorized |
| owner answers | verbatim records with a body sha256, additive only |

## 5. The packet's files

| # | file | purpose |
|---|---|---|
| 1 | `HOST_REQUIREMENTS_501F48CB.md` | every host requirement, classified, with sources |
| 2 | `HOST_READ_ONLY_AUDIT_8A.md` | the 8a audit: A-01, S-01…S-17, NEEDS CONTROLLED WRITE TEST, A-02 |
| 3 | `HOST_VERDICT_RULES_8B.md` | the four verdicts, rows B-01…B-38, precedence, the verdict record |
| 4 | `OD_R2_4_HOST_CHANGE_PACKET.md` | M1–M5, F-1–F-5, U-1–U-7, X-1–X-8, AF-1/AF-2; the application proofs; the reply form (unanswered) |
| 5 | `CELL308_COORDINATION_8C.md` | non-overlap, directories, limits, resources, the evidence, the operator form A–D |
| 6 | `WORKER_TIER_DRILL_8D.md` | preconditions, pre-launch, launch, monitoring, artifacts, gate order, watchdog, classes, exactly-once, after-run, the Γ309 boundary |
| 7 | `WORKER_TIER_PASS_FAIL_RULES.md` | PASS P-1…P-12, the validator's V01…V29, FAIL subclasses, INTERRUPTED, NOT_STARTED, INCIDENT |
| 8 | `PRE_FREEZE_REVIEW_PACKET.md` | the reviewer's inputs, Q1–Q10, the reconstruction, the output |
| 9 | `OWNER_RETURN_CONDITION.md` | R-0…R-3; O-1…O-10; the R-3 message form |
| 10 | `HOST_SIDE_EXECUTION_CHECKLIST.md` | this file |
| — | `tools/prelaunch_readonly_check_8d.py`, `tools/validate_worker_drill_8d.py` | read-only host tools (stdlib only) |
| — | `tools/selftest/` | the tools' own test in this Cloud Session, on a clone of origin r2 and synthetic fixtures |
| — | `PACKET_MANIFEST.json` | sha256 of every file above |
