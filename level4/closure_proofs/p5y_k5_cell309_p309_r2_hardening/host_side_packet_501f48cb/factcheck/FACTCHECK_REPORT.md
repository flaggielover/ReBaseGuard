# Fact-check: host_side_packet_501f48cb against r2 501f48cb

VERDICT: DEFECTS_FOUND. There are no blocking defects, 6 should-fix defects and 15 minor ones.

Packet paths are relative to `host_side_packet_501f48cb/`. Source paths are relative to the extracted r2 namespace
`.../t9/src/level4/closure_proofs/p5y_k5_cell309_p309_r2/`.

## Verified correct (summary)

**Hashes and blobs.** Every sha256 and blob the packet cites matches the source bytes:
- HR `4baeacba`, BS `27939274`, OP `9be65aa6`;
- host `ec9c8416` / blob `1763cd20`, launch `cd7e4ab9`, drill `ef4ce1bf`, runner `540df055`, MAN `15391711`;
- SI blob `085d64bd`, REVIEW_SF1A `1f95ca2f`, HP `04757772`.

**p309_host.py.**
- The subcommands, `--config`/`--config-json`, the exit rule (0/1/2; audit and provenance always 0) and the DEFAULTS keys are correct.
- Every audit field name used in 8A §2 exists in `audit()`.
- The preflight, gate and isolation check names are correct (isolation has 8 checks).
- `UNIT_PROPS` and the `systemctl show` value forms are correct: KillSignal=9, TimeoutStopUSec=10s, InaccessiblePaths hashed after stripping `-`.

**p309_launch.py.**
- Modes, unit names, `--print-only` output keys (`launched`, `print_only`, `record`, `blockers`, `argv`) and the exit codes are correct.
- Blocker names are correct: `p309_units_loaded`, `systemctl_unavailable`, `launcher_not_unit_user`.
- The unit properties, the HOME/TMPDIR creation and the drill argv (`--tier worker`, no `--keep`) are correct.

**p309_topology_drill.py.**
- The dirty-namespace refusal (exit 2, before `drill_<stamp>`) is correct.
- Report keys are correct: verdicts (5), the 9 control keys, witness keys, host keys and ledger keys.
- The worker-tier QHOST abort (rc 3 / QHOST_FAIL.json) and the 12 h runner timeout are correct.
- The GOVERNANCE row is correct: purpose `topology drill (worker tier) <stamp>: PASS|FAIL`, class GOVERNANCE, notes `report sha256 <hex>`.
- The three export files and the deletion of the drill root are correct.

**p309_qualify.py.**
- The gate order matches `items_table`.
- The summary keys `Q01..Q17`, `Q_U2`, `Q_D5`, `Q-HOST` are correct (20 in all).
- The fs_probe step names, including SF1-A appendability, are correct.
- The relative order fs_probe → H3 → qhost_preflight → attempt_1/RUN START is correct.
- `UNIT_REQUIRED` and the six checked properties are correct.

**Tests and static tools.**
- `test_p309_static_controls` has 22 controls, including T14a.
- K02 uses 2×512 MB.
- U01–U03 apply in the worker tier only, and P02 is "not applicable" without root.
- "P309 SCAN PINS: all current" and "MANIFEST IDENTICAL" are the exact output strings.
- The self-audit A1–A10 and `"ok"` claims are correct.

**Tools.**
- prelaunch has exactly 36 checks (C01–C33, with C08×4).
- The validator has exactly 30 entries (V01–V29, with V19×2).
- `COMMITTED_DRILLS` equals the 10 committed `evidence/drill` directories.
- Both tools are read-only: git runs only read verbs with `GIT_OPTIONAL_LOCKS=0`, no file is written, and bytecode is suppressed.
- Validator fields match what r2 writes: launch record keys, `unit_properties` keys/values, the GOVERNANCE row's `class`/`script`/`purpose`/`notes`, the gate keys and the control keys.

**Governance.**
- The quotes of messages 3, 4 (#13, #14), 5 (OD-R2-0(D), OD-R2-3, OD-R2-4, step 6, AF-1/2/4) and 6 are verbatim.
- No packet text answers OD-R2-4 or OD-R2-0(D), or claims an authorization that does not exist.

**Internal consistency.**
- Rows B-01..B-38 (plus B-17a, B-20a) map consistently to M1–M5, X-1..X-8 and AF-1/AF-2.
- U-1..U-7, F-1..F-5, R-0..R-3 (with R-1b, R-2b) and O-1..O-10 are consistent across the 10 docs.
- The C and V counts agree everywhere.

## Defects

### Should-fix

**1. The runner's `[PASS]/[FAIL]` and `REFUSED` lines never reach the journal.**
- **Packet claims:**
  - `WORKER_TIER_DRILL_8D.md:143`: the journal shows "[PASS]/[FAIL] <QC> lines, in gate order".
  - `WORKER_TIER_DRILL_8D.md:177` and `:273`: the journal holds "the runner's [PASS]/[FAIL] lines".
  - `PRE_FREEZE_REVIEW_PACKET.md:45`: the same.
  - `WORKER_TIER_PASS_FAIL_RULES.md:91`: FAIL-PROBE is identified by "the runner's journal line `QUALIFICATION REFUSED: filesystem probe (S1)…`".
- **Source:**
  - In the worker tier, the runner runs through `run_py(...)` with `capture_output=True` (`p309_topology_drill.py:169-171, 258-264`).
  - `out["main"]` keeps only rc, wall_s, pass, gates, head_unchanged and confined. The runner's stdout and stderr are discarded.
  - The drill prints only its final JSON (`:479`). The drill root, with any attempt files, is deleted at the end (`:477-478`).
  - So no per-gate line appears in the journal, and an rc 2 refusal (S1, H3 or Q-HOST) cannot be attributed from any persisted evidence.
- **Correction:**
  - Monitor progress only through the attempt files (§4 `ls`/`tail`).
  - State that the journal holds only the drill's final JSON.
  - Redefine FAIL-PROBE as "`items.main.rc` = 2 and `gates` null (refusal before the attempt; the cause, S1, H3 or Q-HOST, is not recorded by r2)". The optional §4 observation copies are the only way to see more.

**2. B-28 turns an HP-only RECOMMENDED value into a blocker.**
- **Packet claims:**
  - `HOST_VERDICT_RULES_8B.md:75` (B-28): a filesystem not in {ext4, xfs, btrfs}, or `nobarrier`, gives CHANGES_REQUIRED (M2). This blocks `HOST_ACCEPTED_FOR_WORKER_TIER`.
  - `OD_R2_4_HOST_CHANGE_PACKET.md:48,53` make "an acceptable filesystem" a condition of M2.
  - `HOST_READ_ONLY_AUDIT_8A.md:129` (S-01 fail column) does the same.
- **Source:**
  - R-FS-7 is RECOMMENDED and HP-only (`HOST_REQUIREMENTS_501F48CB.md:78`).
  - The packet's own rule says HP values "never make anything REQUIRED" (`:24-25`), and 8B says it "add[s] no requirement" (`HOST_VERDICT_RULES_8B.md:4`).
  - r2 has no filesystem-type check. Its write-capability checks are `fs_probe` (`p309_qualify.py:151-236`).
- **Correction:** make B-28 a recorded advisory (an 8b note and an M2 recommendation), not a verdict-changing row, or present it to the owner explicitly as an HP recommendation.

**3. (PLAUSIBLE) The pre-launch tool cannot authenticate to a private origin, so C13/C14 can never pass.**
- **Packet claims:** `tools/prelaunch_readonly_check_8d.py:47-48, 147` runs `git ls-remote origin` with a replaced environment (only LC_ALL, GIT_PAGER, GIT_TERMINAL_PROMPT, GIT_OPTIONAL_LOCKS, PATH and HOME).
- **Source:**
  - The environment strips GIT_ASKPASS and any credential variables. C07 (`:128`) forbids any `credential.*` key in every git config scope.
  - `OD_R2_4_HOST_CHANGE_PACKET.md:38` (F-2) says the credential is supplied per command via GIT_ASKPASS or `-c credential.helper`. Neither reaches this subprocess.
  - If the GitHub repository (flaggielover/ReBaseGuard) is private, C13/C14 are always false, and the pre-launch check can never pass on the host.
  - The self-test passed C13/C14 only inside the Cloud Session's git proxy.
- **Correction:** pass GIT_ASKPASS (and any helper variables) through to the ls-remote call only, or document `~/.netrc` (HOME is kept) as the mechanism.

**4. `PACKET_MANIFEST.json` is referenced but does not exist.**
- **Packet claims:**
  - `HOST_SIDE_EXECUTION_CHECKLIST.md:38, 53, 99, 126` and `PRE_FREEZE_REVIEW_PACKET.md:47` rely on `PACKET_MANIFEST.json`.
  - Checklist step 10 verifies the tools against it before use.
- **Source:** the directory holds only the 10 `.md` files and `tools/`. There is no `PACKET_MANIFEST.json`.
- **Correction:** add the manifest (sha256 of every file) in the packet commit, or change the references.

**5. (PLAUSIBLE) E-1 can fail on a genuine PASS.**
- **Packet claims:** `WORKER_TIER_PASS_FAIL_RULES.md:35-36` (E-1) requires `journalctl -u 'p309-r2-drill-*' … | grep -c 'Started '` = 1. The operator checks run as `<P309_USER>` (8D §4).
- **Source:**
  - The "Started …" message is logged by PID 1 (uid 0) in the system journal.
  - M1 (`OD_R2_4_HOST_CHANGE_PACKET.md:25`) explicitly puts the P309 user in neither `systemd-journal` nor `adm`, so that user normally cannot read it.
  - E-1 would then read 0 and give FAIL-OPERATOR on a genuine PASS.
- **Correction:** have the host administrator run E-1, or base E-1 on the launch stdout plus `systemctl list-units`, or accept the drill's own JSON line in the user journal.

**6. Neither the validator nor the report can show that U01–U03 ran.**
- **Packet claims:**
  - `WORKER_TIER_PASS_FAIL_RULES.md:21` (P-1) cites V16 for "host controls incl. U01–U03".
  - `PRE_FREEZE_REVIEW_PACKET.md:87` asks the reviewer to confirm that "U01–U03 ran".
- **Source:**
  - V16 (`validate_worker_drill_8d.py:150-152`) checks only `host_controls_rc == 0`.
  - If the in-unit condition fails, the test records `U00_in_unit_refusals_not_applicable_outside_a_unit` as PASS (`tests/test_p309_host_controls.py:339-342`), and rc stays 0.
  - The report keeps only `host_controls_pass_lines` (a count; 41 on the cloud tier). It keeps no line names when rc is 0 (`p309_topology_drill.py:368-370`).
- **Correction:** state that U01–U03 cannot be evidenced from the report, or add a count check (worker count = cloud count − 1 + 3 if nothing else differs), marked as heuristic.

### Minor

**7. The protected-ref regex is broader than r2's, and disagrees with the packet's own text.**
- **Packet:** `refs/(?:p5y-k5-cell30|…)` in `tools/prelaunch_readonly_check_8d.py:44`, `tools/validate_worker_drill_8d.py:28`, and `WORKER_TIER_PASS_FAIL_RULES.md:41, 139`.
- **Source:** r2's prefixes are `refs/p5y-k5-cell309`, `refs/p309-cell309`, `refs/rlr-tail/` (`p309_driver.py:67`) and `refs/p309-test/` (`p309_guard.py:52`).
- **Effect:** any `refs/p5y-k5-cell300…308*` ref (for example cell 308's) would give a false C12/C14 failure or INCIDENT. It also disagrees with `WORKER_TIER_DRILL_8D.md:40, 215` ("refs/p5y-k5-cell309*").
- **Correction:** use `cell309`.

**8. The launcher does not refuse on the first failure.**
- **Packet:** `WORKER_TIER_DRILL_8D.md:124-128` says "refusing on the first failure", with the record written at step 4 after the checks.
- **Source:**
  - Only the config, unit-user and scratch errors refuse immediately.
  - Preflight, gate, isolation, loaded units and launcher uid are all evaluated, all blockers collected, and the record is written even when blocked (`p309_launch.py:166-187`; SI §8).
- **Correction:** reword to "collects every blocker, writes the record, then refuses (exit 2) if any".

**9. The runner's per-gate limit is not 6 h for every subprocess.**
- **Packet:** `WORKER_TIER_DRILL_8D.md:203` says "`run(…, timeout=6 h)` for each subprocess".
- **Source:** the decoy runs for QC08, QC09 and QC10 use `timeout=24*3600` (`p309_qualify.py:380-381, 417`).
- **Correction:** "6 h (24 h for the QC08–QC10 decoy runs)".

**10. Not every Q-HOST failure aborts the runner.**
- **Packet:** `WORKER_TIER_DRILL_8D.md:201` gives every Q-HOST failure, including "gap > 105 s" and "monitor dead at the stop", the effect "SIGKILL tree, QHOST_FAIL.json, exit 3".
- **Source:**
  - Liveness and the final-sample continuity are judged only at `stop_qhost_monitor()` (`p309_qualify.py:661-685`).
  - Those failures make `gates["Q-HOST"]` false, the summary false and the runner exit 1, with no QHOST_FAIL. The drill continues to its report.
- **Correction:** split the row into in-run abort (exit 3) and end-of-run Q-HOST false (exit 1). FAIL-QHOST already covers both.

**11. The decoy outputs are not under `evidence/`.**
- **Packet:** `WORKER_TIER_DRILL_8D.md:172` says the decoy outputs are "under `evidence/`".
- **Source:** `QC08_DECOY_STAGE1A.json`, `QC10_DECOY_STAGE1A.json`, `QC09_DECOY_STAGE1B_<k>.json` and `QC14_REHEARSE.json` are written directly in `attempt_1/` (`p309_qualify.py:379, 415, 706`).

**12. The launch record has no `launched` key.**
- **Packet:**
  - `WORKER_TIER_DRILL_8D.md:243-244` says "launch record with `blockers: []` and `launched: true`".
  - `WORKER_TIER_PASS_FAIL_RULES.md:23` has a similar statement.
- **Source:** the record has no `launched` key. `launched` is only in the launcher's stdout (`p309_launch.py:162-193`).
- **Correction:** "the launch stdout shows `launched: true`; the record shows `blockers: []`".

**13. A quote is attributed to the wrong file.**
- **Packet:** `OD_R2_4_HOST_CHANGE_PACKET.md:12-13` quotes OWNER_DECISION_PACKET_R2.md OD-R2-4 as "the cell-308 operator's consent for mutation 4".
- **Source:** that phrase is in `governance/R2_DELTA_FOLLOWUP_5_RECORD.md:146` (and REVIEW_R2_DELTA_FOLLOWUP_5.md:460), not in the owner packet. The owner packet says "(the owner's and the cell-308 operator's)" and "host-wide; it affects cell 308 too".

**14. Two classification or citation slips in HOST_REQUIREMENTS.**
- `HOST_REQUIREMENTS_501F48CB.md:102` (R-SD-9) classes `journalctl` and `systemd-detect-virt` as REQUIRED. No r2 code refuses without them: they only feed audit fields and one input of the container detection. Only `timedatectl` is effectively required, through `ntp_synchronized`.
- `:97` (R-SD-4) cites "HR §2; BS 8c-5; OP M3" for "(and reset them if failed)". The reset verb comes only from SI §3 (`R2_AWS_SESSION_INSTRUCTIONS.md:86`).

**15. B-08 adds a rejection criterion r2 does not have.**
- **Packet:** `HOST_VERDICT_RULES_8B.md:53` (B-08) and `HOST_READ_ONLY_AUDIT_8A.md:100` reject on `spot_instance_action` non-null.
- **Source:** r2 checks only `instance_life_cycle` (`p309_host.py:567`). This is a small added criterion. It is benign, but it contradicts "add no requirement".

**16. Two figures in CELL308 §3–§4 do not match their sources.**
- `CELL308_COORDINATION_8C.md:66` says IMDS gets "about two reads per minute". Each monitor sample calls `provenance()` → `imds()`, which is 1 PUT + 5 GETs: about 6 requests per sample, each ≤ 60 s apart (`p309_host.py:219-240, 683`).
- `:58` cites HP §1 for "about 2–3 GB". HP §1 gives about 0.5 GB per clone, about 1 GB of mirrors and 3–4 MB of outputs.

**17. X-5 to X-7 lack the operator consent the packet says they need.**
- `OD_R2_4_HOST_CHANGE_PACKET.md:123-124` says every X-item is host-wide, so it needs the operator's consent.
- `:176` and CELL308 B8 (`CELL308_COORDINATION_8C.md:119-120`) collect operator consent only for X-1–X-4 and X-8. X-5, X-6 and X-7 (package installs) are missing.

**18. 8A forbids git but its own steps run git.**
- `HOST_READ_ONLY_AUDIT_8A.md:32` says "never run `git` anywhere on the host".
- A-01 itself runs `git version` (`p309_host.py:183`), and S-11 runs `git --version`.
- **Correction:** "no git command in any repository".

**19. Two robustness gaps in the tools.**
- `tools/validate_worker_drill_8d.py:106`: an unparseable DRILL_REPORT.json raises a traceback instead of classifying FAIL-EVIDENCE as PASS_FAIL §3 states.
- `tools/prelaunch_readonly_check_8d.py:210-213` executes the clone's `p309_host.py` even when C08 (its sha256) is false.

**20. The reviewer's allowed git verbs do not include the ones §3 uses.**
- `PRE_FREEZE_REVIEW_PACKET.md:19-20` allows only show, diff, log, ls-tree, cat-file, rev-parse, merge-base and ls-remote.
- The reconstruction in §3 (`:136-137`) uses `git clone` and `git checkout` (in the reviewer's own workspace).
- **Correction:** add clone and checkout, workspace only.

**21. The scan-allowance test prints more than C-lines.**
- `WORKER_TIER_DRILL_8D.md:56` says "every C-line [PASS]".
- `tests/test_p309_scan_allowance.py` also prints `genuine_guard_allowance_holds` and `genuine_full_scan_pass` (`:59-60`).
- **Correction:** "every line [PASS]".

## Governance faithfulness

- No misquotation was found.
- No owner decision is answered on the owner's behalf: OD-R2-4 is presented as a form, and OD-R2-0(D) is asked only at R-3.
- M3-b (polkit `stop`) is an HP-based extension beyond r2's "start only" text. It is correctly offered as a separate consent option.
- The only REQUIRED-classification overreaches are items 2, 14 and 15.
