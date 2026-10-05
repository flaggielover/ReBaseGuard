# 8d: the worker-tier drill on r2 `501f48cb` (deliverable 6 of 10)

**Authority.** Owner message 5, sequence step 6: "Perform the required worker-tier drill on the incorporated/reviewed
bytes when the host prerequisites are satisfied." Owner message 6: "The worker-tier drill may be prepared, but it may
only be run when the already-required host prerequisites are satisfied."

This document **prepares** the drill. It runs only from the separate P309 host-side session, and only when every
precondition in §1 holds. This Cloud Session never runs it (message 4 #13).

**What it is.** The drill is development evidence, never qualification evidence (`code/p309_topology_drill.py`
docstring). It does not authorize, invoke or approach a Γ309 evaluation (§11).

**Bytes.** r2 `501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853`, tree `d7e2c8329b73d68ae07ca37192eb495674e572c9`:

| file | sha256 |
|---|---|
| `code/p309_qualify.py` (the runner) | `540df055…a3af` |
| `code/p309_launch.py` | `cd7e4ab9…85fb` |
| `code/p309_topology_drill.py` | `ef4ce1bf…f0c1` |
| `code/p309_host.py` | `ec9c8416…1f65` |

The pre-launch check (§2) verifies all four in full.

**Names.** `<…>` names are defined once in `HOST_SIDE_EXECUTION_CHECKLIST.md` §0. `<NS>` is
`<CLONE>/level4/closure_proofs/p5y_k5_cell309_p309_r2`.

## 1. Preconditions (all must hold; any missing one means the window does not open)

| # | precondition | evidence |
|---|---|---|
| D1 | 8b-final verdict = `HOST_ACCEPTED_FOR_WORKER_TIER` | `host_evidence/VERDICT_8B_final_<UTC>.json` |
| D2 | every OD-R2-4 item the drill needs was consented and applied exactly; nothing unconsented was applied | the owner's OD-R2-4 reply; `APPLIED_CHANGES_<UTC>.json`; 8b row B-37 clear |
| D3 | the cell-308 form: Parts A and B complete, and Part C complete and confirmed for **this** window (≥ 9 h; 12 h recommended; the QC-D5 margin) | `CELL308_FORM_*` |
| D4 | the M4 holds are in effect for this window | OD-R2-4 §4 M4 read-only proof, taken in the hour before launch |
| D5 | origin r2 is exactly `501f48cb`, and the P309 clone is a clean single-branch clone at it | §2 step 3 (`C01`–`C14`) |
| D6 | no earlier worker-tier drill on these bytes exists, unless the owner recorded a decision allowing another (no silent retry) | the P309 clone's `evidence/drill/` holds only the 10 committed records (`C10`); the hardening namespace's `host_evidence/` |
| D7 | the static checks of §2 step 1 pass on `501f48cb` on this host | `STATIC_8D_<UTC>.json` |
| D8 | the A-02d `--print-only` check, in a **fresh** check directory, reports no blocker, within 3 h of launch | the check directory's `launch_<utc>.json` |
| D9 | the pre-launch check passes (all 36 checks, `C01`–`C33`; `C08` has four parts) | `PRELAUNCH_8D_<UTC>.json` |
| D10 | the target-integrity baseline: no ref under `refs/p5y-k5-cell309*` or the other protected prefixes, locally or on origin; no grant or result file | `C12`, `C14`; §9 |
| D11 | the run's scratch root `<RUN_SCRATCH>` is new, empty, resolved and on the P309 volume; it was never a check directory | `C15`–`C18`, `C28` |

## 2. Pre-launch verification (as `<P309_USER>`, in this order, inside the agreed window's first minutes or the hour before)

### Step 1: static checks in a disposable clone (never in `<CLONE>`; the drill refuses a dirty namespace, A4)

```bash
S=<SCRATCH_BASE>/static8d_<UTC>; mkdir "$S" "$S/scratch" "$S/evidence" "$S/tmp"
git clone -q --no-local --single-branch --branch claude/p5y-k5-cell309-p309-r2 <CLONE> "$S/clone"
git -C "$S/clone" rev-parse HEAD                      # must print 501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853
cd "$S/clone/level4/closure_proofs/p5y_k5_cell309_p309_r2"
export P309_SCRATCH_ROOT="$S/scratch" P309_EVIDENCE_DIR="$S/evidence" TMPDIR="$S/tmp"
<INTERP> -B code/p309_static_check.py              # QC12: every T-line [PASS], exit 0
<INTERP> -B tests/test_p309_static_controls.py     # 22 controls [PASS], incl. T14a_main_preflight_after_the_attempt
<INTERP> -B code/p309_scan_pins.py --list          # last line exactly: P309 SCAN PINS: all current
<INTERP> -B tests/test_p309_scan_allowance.py      # every C-line [PASS]
<INTERP> -B code/make_freeze_params.py             # writes freeze/ in THIS disposable clone only
<INTERP> -B code/make_freeze_manifest.py
<INTERP> -B code/p309_placeholder_check.py         # "pass": true, "unallowed": []
<INTERP> -B code/make_freeze_manifest.py --check   # MANIFEST IDENTICAL
<INTERP> -B code/p309_self_audit.py QUALIFICATION  # "ok": true with A1..A10 all true
```

Rules for step 1:
- **Judge by content,** never by exit status alone. Record each command's full output in `STATIC_8D_<UTC>.json`.
- The synthetic `freeze/` made here is a scratch artefact, never a freeze. Delete `"$S"` by its literal path after
  recording.
- These are short, light runs (about 1 min of CPU in total). They run as the P309 user, outside any unit.

### Step 2: the window's check record (A-02d)

```bash
mkdir <SCRATCH_BASE>/check8d_<UTC>                     # fresh; never reused; never a run's scratch root
cd <NS>
P309_SCRATCH_ROOT=<SCRATCH_BASE>/check8d_<UTC> P309_FOREIGN_ROOTS=<FOREIGN_ROOTS> \
  <INTERP> -B code/p309_launch.py --mode drill --host-config <HOST_CONFIG> --print-only
```

It must report `"blockers": []` and exit 0. Read the record's `gate.processes`:
- every uid must be one agreed in Part B or Part C;
- no foreign or unattributable process may be active (SI §4.1 step 4).

If it is blocked, do not launch. A `gate` blocker means the moment was not quiet: wait, then repeat this step in
another fresh check directory.

### Step 3: the read-only pre-launch check (`tools/prelaunch_readonly_check_8d.py`)

```bash
mkdir <RUN_SCRATCH>                                       # e.g. <SCRATCH_BASE>/drill8d_<UTC>; new and empty
<INTERP> -B <PACKET_TOOLS>/prelaunch_readonly_check_8d.py --clone <CLONE> --host-config <HOST_CONFIG> \
  --scratch <RUN_SCRATCH> --check-record <SCRATCH_BASE>/check8d_<UTC>/launch_<utc>.json \
  --verdict <VERDICT_8B_FINAL> --remote --max-age-h 3 > <P309_HOME>/p309_8d_records/PRELAUNCH_8D_<UTC>.json
```

Rules for step 3:
- It must print `"pass": true`, and every one of its 36 checks must be true. It covers:
  - the exact commit, tree and branch, and a clean clone with no untracked file;
  - no alternates or credential, and the four reviewed tools' bytes;
  - no qualification directory, only the committed drill records, launchable ledgers, and no protected ref locally
    or on origin;
  - the scratch root new, empty and disjoint;
  - the launch keys, `foreign_uids`, the unit user, the pinned interpreter (3.11.15 CPython), glibc, and no loaded
    P309 unit;
  - the check record recent and without blockers;
  - host identity (machine-id, hostname and instance hashes, boot id, interpreter and glibc) equal to the 8b-final
    verdict and to the check record.
- **Ledger state, no prior attempt, host identity.** These are `C09`–`C12` and `C29`–`C33`.
- **The filesystem pre-launch probe** cannot be read-only. It is the runner's own `fs_probe` (S1 + SF1-A), which runs
  inside the drill before Q-HOST, the attempt and RUN START. A probe failure is a drill FAIL classed **FAIL-PROBE**
  (§8). No attempt directory or start line exists then.
- `<P309_HOME>/p309_8d_records/` is a P309 directory outside the clone and outside every scratch root.

## 3. The launch (once; never repeated automatically)

```bash
cd <NS>
P309_SCRATCH_ROOT=<RUN_SCRATCH> P309_FOREIGN_ROOTS=<FOREIGN_ROOTS> \
  <INTERP> -B code/p309_launch.py --mode drill --host-config <HOST_CONFIG> \
  | tee <P309_HOME>/p309_8d_records/LAUNCH_STDOUT_<UTC>.json
```

**Expected standard output:** `{"launched": true, "unit": "p309-r2-drill-<utc>", "record": "<RUN_SCRATCH>/launch_<utc>.json", "rc": 0, …, "watch": "journalctl -u p309-r2-drill-<utc> -f"}`.

**What the launcher does,** per `code/p309_launch.py`, refusing on the first failure:
1. the unit user check (A16), and a valid scratch root;
2. the durability preflight, the exclusion gate (60 s sample), and the isolation check;
3. no loaded `p309-r2-*` unit, and the launcher running as the unit user;
4. it writes `launch_<utc>.json` exclusively;
5. it creates `<RUN_SCRATCH>/home` and `<RUN_SCRATCH>/tmp`;
6. it starts **one** transient unit `p309-r2-drill-<utc>`, running `<INTERP> -B <NS>/code/p309_topology_drill.py --tier worker`.

**If the launch does not start:**
- `"launched": false` with `"refused"`, or a `systemd-run` rc ≠ 0, means **NOT_STARTED** (§8). Keep the record.
- Never relaunch in the same window without recording the cause. A relaunch after a host fix needs the fix's own
  consent (OD-R2-4), and a **new**, empty `<RUN_SCRATCH>`.

## 4. Monitoring (read-only; as `<P309_USER>`; at most every 10 min, the external watchdog)

```bash
U=p309-r2-drill-<utc>                                    # from the launch output
A=<RUN_SCRATCH>/drill_<stamp>/clone/level4/closure_proofs/p5y_k5_cell309_p309_r2/qualification/attempt_1
systemctl show "$U" -p ActiveState -p SubState -p MainPID -p ExecMainStatus -p MemoryCurrent --no-pager
journalctl -u "$U" --no-pager -n 40                     # [PASS]/[FAIL] <QC> (<s> s) lines, in gate order
ls -la "$A"                                              # QC records appear one by one
tail -n 2 "$A/QHOST_MONITOR.jsonl"                       # a "sample" row with "pass": true at most ~60 s old
cat /proc/sys/kernel/random/boot_id; grep -o '"boot_id": "[^"]*"' "$A/ATTEMPT_START.json"   # must be equal
cat /proc/loadavg; free -m; df -P <SCRATCH_BASE> <CLONE>
```

Rules while the unit runs:
- `<stamp>` is the drill root's own UTC name (`ls <RUN_SCRATCH>`).
- Reading these files changes no evidence: the runner writes each record complete under its final name (`xwrite`:
  write, fsync, then link).
- **Never, while the unit runs:**
  - any `git` command in `<CLONE>` or under `<RUN_SCRATCH>` (it could take the index lock or refresh the index; F2
    and message 4 #14);
  - any write, rename, delete or `touch` under `<RUN_SCRATCH>` or `<NS>`;
  - `systemctl stop`, `kill` or `renice` of anything, except under §7's incident rule;
  - starting any other work as another user;
  - opening an editor on evidence files.
- **Optional copies.** Read-only copies of completed `QC*.json`, `QHOST_MONITOR.jsonl` and `ATTEMPT_START.json` into
  `<P309_HOME>/p309_8d_records/observed_<UTC>/` are permitted, because the drill deletes its root at the end (§5).
  They are host-local observations, never committed, and decoy outputs are never committed (SI §5).

## 5. Expected artifacts

| when | path | content |
|---|---|---|
| launch | `<RUN_SCRATCH>/launch_<utc>.json` | `P309_R2_LAUNCH/2`: mode `drill`; unit; redacted configuration; preflight, gate and isolation documents; `p309_units_loaded: []`; argv; `blockers: []` |
| launch | `<RUN_SCRATCH>/home/`, `<RUN_SCRATCH>/tmp/` | the unit's HOME and TMPDIR |
| run | `<RUN_SCRATCH>/drill_<stamp>/clone/` | the drill's clone of the committed branch (no remote); the synthetic freeze F′, record FR′ and checkpoint commit |
| run | `…/clone/<NS-rel>/qualification/attempt_1/` | `ATTEMPT_START.json`, `LAUNCH_RECORD.json`, `UNIT_PROPERTIES.json`, `QHOST_BASELINE.json`, `QHOST_MONITOR.jsonl`, `QC01.json` … `QC_D5.json` (QC08/QC10 with their decoy outputs under `evidence/`), `QHOST_SUMMARY.json`; then `qualification/P309_QUALIFICATION.json` |
| end | `<NS>/evidence/drill/<stamp>/DRILL_REPORT.json` | `P309_R2_DRILL/1`, tier `worker`: `clone_base`, topology, witnesses, `items.main` (rc, pass, the 20 gates incl. `Q-HOST`), host functions, controls, ledger rows/sha256/counters/completeness, the embedded launch record and unit properties, `p309_unchanged`, `pass` |
| end | `<NS>/evidence/drill/<stamp>/DRILL_ZERO_TARGET_LEDGER.jsonl`, `DRILL_EXPOSURE_LEDGER.jsonl` | the drill clone's new ledger rows, in full |
| end | `<NS>/ledger/ZERO_TARGET_LEDGER.jsonl` | **one** appended GOVERNANCE row: `topology drill (worker tier) <stamp>: PASS|FAIL`, with the report's sha256 |
| end | the drill root | **deleted** by the drill (the launcher's drill mode passes no `--keep`). So the attempt files above do not persist, except as the report's content and the optional observations of §4 |
| always | the unit's journal | the runner's `[PASS]/[FAIL]` lines and the drill's final JSON |

## 6. Expected gate order and time limits

1. The drill makes its clone, the guard, and the topology (generators, the unresolved-marker check, F′, FR′); then the
   witnesses before the items.
2. The runner (`items.main`), with these internal checks: the manifest check; `fs_probe` (S1 + SF1-A); the H3
   pre-launch state; `qhost_preflight`; `attempt_1` and RUN START; `ATTEMPT_START.json`; the Q-HOST monitor.
3. Then the gates in this exact order (`items_table`):
   **QC01 → QC02 → QC03 → QC04 → QC05 → QC06 → QC07 → QC08 → QC09 → QC10 → QC11 → QC12 → QC13 → QC14 → QC15 → QC16 →
   QC17 → QC_U2 → QC_D5**, then the Q-HOST stop and the summary (`gates` keys `Q01`…`Q17`, `Q_U2`, `Q_D5`, `Q-HOST`).
4. After the runner: the witnesses after the items; the host functions (provenance ×2 and continuity, preflight
   (expected PASS on the worker), `tests/test_p309_host.py`, `tests/test_p309_host_controls.py` (U01–U03 run here
   only; P02 is "not applicable" as a non-root user), and `tests/test_p309_static_controls.py`); the controls
   (R2-M01a, R2-M01b, the second freeze record, the TEST-only prior ref, the push-URL and P309-repository guards); the
   ledger; the export.

**Per-gate limit,** an operator signal only (it never stops anything). Use the "maximum to allow" column of
`HOST_REQUIREMENTS_501F48CB.md` §8. The QC08/QC09/QC10/QC16/QC_D5 limits are 4.3 h / 7.6 h / 4.3 h / 45 min / 2.75 h.

## 7. Timeout and watchdog policy

| layer | rule | effect |
|---|---|---|
| Q-HOST monitor (in the unit) | samples ≤ 60 s apart. It fails on a foreign or unattributable process > 0.5 core or on a heavy pattern; on > 1.0 core together; on any continuity break; on a gap > 105 s; or if the monitor is dead at the stop | the runner SIGKILLs its tree, writes `QHOST_FAIL.json` and a failed summary, and exits 3; the drill stops at once (FAIL-QHOST) |
| the drill's limit on the runner | `subprocess.run(…, timeout=12 h)` | the drill records `TimeoutExpired` and fails (FAIL-TIMEOUT) |
| the runner's per-gate limit | `run(…, timeout=6 h)` for each subprocess | that gate records FAIL |
| the unit | `KillMode=control-group`, `KillSignal=SIGKILL`, `SendSIGKILL=yes`, `TimeoutStopSec=10s` | anything left dies when the unit stops |
| external watchdog (operator) | every ≤ 10 min, the §4 commands only. It **never** writes, restarts, signals or resumes | observations; on an incident (below), the one permitted action |

**Liveness signals:**
- `QHOST_MONITOR.jsonl` grows at least once a minute;
- the next `QC*.json` appears within its limit;
- the unit is `active`;
- the boot id equals `ATTEMPT_START.json`'s.

A signal that is out of bounds is reported. It is **not** acted on, except under the incident rule.

**The incident rule.** The only operator stop is on a target-integrity incident: a ref under `refs/p5y-k5-cell309*`,
a grant file, a `P309_RESULT.json`, or a ledger row with a nonzero target counter. Then:
- the operator stops the unit with `systemctl stop p309-r2-drill-<utc>`, under M3-b, or through the administrator if
  only M3-a was consented;
- and reports to the owner immediately.

Otherwise the operator stops only on the owner's instruction.

## 8. Failure classification and interruption handling

Use `WORKER_TIER_PASS_FAIL_RULES.md` for the exact criteria.

| class | when | what then |
|---|---|---|
| NOT_STARTED | the launcher refused or `systemd-run` failed; or the unit started but the drill refused before creating `drill_<stamp>` (e.g. a dirty namespace, exit 2) | no attempt exists. Record the launch record and the output. A new launch needs the cause fixed (with consent if the host changes) and a new empty scratch root. It is **not** a retry of an attempt |
| PASS | the validator classifies PASS | §10 |
| FAIL-PROBE / FAIL-QHOST / FAIL-GATE / FAIL-HOST-FUNCTIONS / FAIL-CONTROLS / FAIL-LEDGER / FAIL-F2 / FAIL-TIMEOUT | a `DRILL_REPORT.json` exists with `pass: false` | preserve everything; validate; report to the owner at return point R-2. **No second drill without a recorded owner decision** |
| INTERRUPTED | `drill_<stamp>` exists (or the unit started) but no `DRILL_REPORT.json` / GOVERNANCE row for it: reboot, power loss, an OOM kill, `systemctl stop`, or a unit crash | preserve the drill root as it is (it was not deleted). Do not remove, resume or re-run anything. Classify read-only (the journal; `ATTEMPT_START.json` boot id vs the current one). Report at R-2 |
| INCIDENT | any target counter, protected ref, grant or result file | the incident rule (§7); report immediately; it overrides every other class |

**Interruption handling.**
- Nothing is resumed. The runner and the drill have no resume path. A leftover `drill_<stamp>` or attempt directory
  is evidence, deleted only by literal path after the owner has seen the classification.
- A `.p309-fsprobe-<pid>/` directory left in a qualification directory blocks later launches by design. It is removed
  only by hand, after recording (the runner's own message says so).

## 9. Exactly-once checks (after the run; part of the validator)

- exactly one `p309-r2-drill-*` unit started in the window (the journal); exactly one launch record with
  `blockers: []` and `launched: true`;
- exactly one new `evidence/drill/<stamp>/` with exactly its three files; exactly one new GOVERNANCE row in
  `ledger/ZERO_TARGET_LEDGER.jsonl`, naming that stamp and the report's sha256; the exposure ledger unchanged;
- in the drill's own ledger rows: exactly one `RUN START` row, naming F′; every counter 0; no cells; no band hit;
- `clone_base` = `501f48cb`; the P309 clone's HEAD still `501f48cb`, and `p309_unchanged` true;
- no protected ref (locally, in the report's controls, and on origin through `git ls-remote origin`); no grant or
  result file anywhere in the namespace.

## 10. After the run

**1. Validate (read-only).**

```bash
<INTERP> -B <PACKET_TOOLS>/validate_worker_drill_8d.py --clone <CLONE> --stamp <stamp> \
  --launch-record <RUN_SCRATCH>/launch_<utc>.json --verdict <VERDICT_8B_FINAL> \
  --prelaunch <P309_HOME>/p309_8d_records/PRELAUNCH_8D_<UTC>.json > <P309_HOME>/p309_8d_records/VALIDATION_8D_<stamp>.json
```

It must print `"classification": "PASS"` with `"failed": []`. Its 30 checks are listed in
`WORKER_TIER_PASS_FAIL_RULES.md` §2.

**2. Scanner pins still current.** Repeat step 1 of §2 in a new disposable clone of `<CLONE>`'s HEAD (still
`501f48cb`), and judge the same lines.

**3. Origin unchanged.** `git -C <CLONE> ls-remote origin` must show r2 still at `501f48cb` and no protected ref.

**4. Return the evidence to the coordinator, as text.**
- the launch output and launch record; the pre-launch, validation and static records;
- `DRILL_REPORT.json` and the two exported ledgers, with sha256;
- the GOVERNANCE row; the journal's `[PASS]/[FAIL]` lines;
- the Part D form.

The coordinator files them in this hardening namespace (`host_evidence/DRILL_8D_<stamp>/`).

**5. Do not commit or push to r2.**
- The drill's evidence and ledger row sit uncommitted in `<CLONE>`. Leave them exactly so until the owner's filing
  authorization (return point R-2, `OWNER_RETURN_CONDITION.md`).
- They must be committed **before** any freeze: the official runner refuses a namespace with changes outside
  `qualification/` and `ledger/`, and the drill refuses a dirty namespace.
- The filing commit would add only `evidence/drill/<stamp>/` and the ledger row (and any host evidence the owner
  names). The pre-freeze review checks that it changes nothing else.

**6. Cleanup (P309 files only, by literal path, after the coordinator confirms receipt).**
- `<RUN_SCRATCH>` and the static and check directories;
- `systemctl reset-failed p309-r2-drill-<utc>`, only if the unit is in a failed state, and only under M3;
- never anything of cell 308.

**7. Restore the M4 holds** after the window (OD-R2-4 §1 M4, "after the window"), and record it.

## 11. What the drill never does (the Γ309 boundary)

The drill reads no target input and evaluates no quarantined cell. "NEW Γ309 TARGET EVALUATIONS = 0 by construction"
(`p309_topology_drill.py`). In particular:
- the launcher is used **only** in `--mode drill`. `--mode official` and `--mode host-rerun` are never used in this
  packet;
- `p309_driver.py execute`, `seal-only` and `validate-grant` are never run; no grant, marker, pending-result or
  production-namespace ref is created (the drill's own controls check this);
- no freeze is made. F′ is a synthetic freeze inside the drill's disposable clone, which is deleted;
- the 8d result changes no scientific status, adopts nothing, and authorizes neither OD-R2-0(D), a freeze, a
  qualification nor a grant.

**What 8d does not show** (SI §4, follow-up W7). The report review must state it:
- the unit-property and instance-id refusal branches are exercised nowhere;
- the unit's `KillMode=control-group`/SIGKILL backstop after a runner abort, and the drill's own stop on exit 3, are
  unexercised by a passing drill;
- U01–U03 run only here.
