# Durable-host execution packet: the r2 qualification

**Scope.** This packet covers the operator procedure for **r2's single official qualification** and its preceding
**worker-tier drill** on a durable host. It is result-free: nothing in it evaluates Γ309, arms a marker or touches a
grant.

**Read this first.** This packet does not authorize anything. Running it requires all of these:
- the owner's answers to OD-R2-0 (D), OD-R2-3, OD-R2-4 and OD-R2-5;
- the proposed OD-R2-H (whether the frozen package carries the runtime hardening);
- the prerequisites in §0.

The binding host rules are r2's own `governance/R2_HOST_REQUIREMENTS.md` (at `101ef2cb`). This packet adds to them
and never relaxes them.

## 0. Prerequisites (each must be true before step 1 of §8)

| # | prerequisite | why | status at this packet |
|---|---|---|---|
| P0.1 | the owner has answered OD-R2-0 (A)–(D), -1, -2, -3, -4 and -5 (`OWNER_DECISIONS_OD_R2.md`) | authority (msg 4 item 7) | **open** |
| P0.2 | the package to freeze is fixed: r2 `101ef2cb`, or r2 + the hardening `claude/p309-r2-hardening-20261005` after its delta review (OD-R2-H) | durability (§6) | **open** (recommended: hardened) |
| P0.3 | F-DRILL-ORDER fixed in `code/p309_topology_drill.py` (params before manifest) and re-reviewed, **or** the drill replaced by `r2h_rehearse.py` plus the launcher's `--mode drill` | otherwise the worker-tier drill refuses at the runner's manifest precondition | **open** |
| P0.4 | the host provides a cloud metadata service (IMDS), **or** a reviewed host-portability change to `durability_preflight` exists | `cloud_metadata_available`, `not_spot`, `not_burstable`, `no_scheduled_maintenance` fail closed without one | met only on an IMDS cloud host |
| P0.5 | the cell-308 operator's `foreign_uids` and heavy patterns, and window agreement with every non-root workload on the host | OD-R2-4/5 | **open** |

## 1. Minimum host (all from `R2_HOST_REQUIREMENTS.md` §2, unchanged)

| resource | minimum | recommended |
|---|---|---|
| CPU | **4 dedicated x86_64 vCPU**, not burstable | 4–8 dedicated; **single-tenant** if possible (OD-R2-5 (i) lets any heavy foreign process end the attempt) |
| RAM available at the gate | **8 GB** | 16 GB (measured peak under 1 GB with 4 jobs) |
| free disk on every P309 root | **40 GB** | 60 GB (repository about 0.5 GB per clone; a full attempt with decoy outputs is about 3–4 MB; scratch mirrors are about 1 GB) |
| OS | Linux, systemd as PID 1, not a container, `systemd-run` present | Ubuntu 24.04 LTS (the measured runs) |
| interpreter | **CPython 3.11.15 exactly**, P309-private, path pinned; its binary sha256 is pinned in the freeze manifest | build once, record its sha256 at the 8a audit |
| glibc | pinned to the 8a audit's value (the manifest binds it) | — |
| git | ≥ 2.32 | 2.43 (measured) |
| clock | NTP synchronised | — |

## 2. Filesystem requirements (new; durability of the evidence)

- The repository, `P309_SCRATCH_ROOT` and the qualification directory lie on a **local, persistent, journaling
  filesystem that honours fsync**: ext4 (default `data=ordered`), xfs or btrfs.
- They must **not** be on tmpfs, overlayfs or other container layers, network filesystems (NFS, SMB, FUSE),
  `nobarrier` mounts, or a disk with volatile write cache that is not flushed.
  - Check: `findmnt -no FSTYPE,OPTIONS --target <path>`. The rehearsal tool records the type and, with
    `--require-durable-host`, refuses anything outside {ext4, xfs, btrfs, zfs, ext3}.
- The hardened runner's guarantees (§6) assume a filesystem where `fsync(file)` followed by `fsync(dir)` makes a
  newly linked name durable. On the listed filesystems this holds. **It is not provable without a power-cut test**,
  so the matrix classifies it SAFE_BUT_UNPROVEN.
- Free space is checked by the exclusion gate (`disk_available`). Keep at least 40 GB free for the whole window: a
  full disk mid-run makes a record write fail, which is recorded as a FAIL or leaves the attempt INTERRUPTED.

## 3. Host identity rules

- Identity = machine-id sha256 + hostname sha256 (`p309_guard.host_id`), plus, during the run, boot id, instance id
  (IMDS), interpreter sha256, glibc and suspend time (`p309_host.continuity`).
- The **freeze must be made on the qualification host**: the freeze manifest records `runtime.host_id_sha256`, and the
  runner refuses (`make_freeze_manifest --check`) on any other host. A freeze on one host cannot be qualified on
  another.
- The static hostname must equal the running one (`hostname_static`). Never rename the host during a window.
- Any continuity break during the run (reboot, suspend, instance change, interpreter or glibc change) makes Q-HOST
  FAIL. The attempt then ends and is never resumed.

## 4. Network requirements

- **During the run:** only the instance-metadata endpoint (IMDS, link-local) is read by Q-HOST. No other network
  access is needed or used by the gates. Outbound access can be closed for the unit's window.
- **Before and after:** git fetch / push of the P309 branch to GitHub through the P309-only credential (r2's
  checkpoint tool). The owner's own machine is never a relay (msg 3 item 9).
- No SSH into the unit is needed. Inspection (§9) runs as the P309 user, read-only.

## 5. Expected durations (measured; maximum = 2× the slowest observation, rounded up)

| gate | r1 freeze host, 2026-09-30 (4 workers) | this review's cloud container (4 vCPU, contended) | **maximum to allow** |
|---|---|---|---|
| QC01–QC05 | 1–8 s each | 1–11 s each | 1 min each |
| QC06 (verifier battery) | 831 s | 1 108 s | **40 min** |
| QC07 | 143 s | 124–202 s | 7 min |
| QC08 (decoy Stage 1a) | 4 310 s | 7 639 s | **4.3 h** |
| QC09 (decoy Stage 1b ×2) | 9 769 s | 13 702 s | **7.6 h** |
| QC10 (decoy Stage 1a again; byte identity) | 3 864 s | about 2 h (Run D) | **4.3 h** |
| QC11 | — (r1 crashed early) | 178–288 s | 10 min |
| QC12 | 7 s | 10–17 s | 1 min |
| QC13–QC15, QC17, QC_U2 | 0.1–61 s | 0.1–83 s | 3 min each |
| QC16 | 654 s | 1 218–1 286 s | **45 min** |
| **QC_D5** | — (r1 killed in it) | **3 582 s (r1 frozen); 4 913 s (r2, contended)** | **2.75 h** |
| **whole attempt** | 5.47 h for QC01–QC_U2; about 5.7–5.9 h complete | about 8–9 h projected under contention | **window ≥ 9 h exclusive** (r2 §3), **12 h** recommended on a host with any co-tenant |

**The QC-D5 window.** QC-D5 is the **last** gate, and its D5-exception controls are a single CPU-bound process
(dozens of planted-mutant tree copies and scans) that runs 60–85 min on a 4-vCPU host. r1's attempt (22:35→22:41Z)
and two runs in this programme were interrupted inside it. Plan the window so that **QC-D5 starts with at least
2.75 h of guaranteed host time left**. That means no maintenance, reboot or co-tenant start until the summary
exists.

## 6. What the runtime guarantees (hardened package, if OD-R2-H is adopted)

| guarantee | mechanism | evidence |
|---|---|---|
| no torn or empty record or completion marker | H1: temp O_EXCL → write → fsync → link (never overwrite) → dir fsync | matrix C04–C07, C12; unit T04 |
| ledger rows durable before the next step | H2: fsync of both ledgers after every start line, gate record and abort | unit T07; matrix fsync logs |
| no launch over a prior or partial run | H3: refuses on stray / temporary files, a torn or unparseable or nonzero ledger row, or a start line after the freeze with no attempt | matrix S04–S06; unit T05–T06 |
| an interrupted attempt is attributable | H4: durable attempt entry + `ATTEMPT_START.json` (boot id, pid, runner sha) | unit T08 |
| a completion marker that proves completeness | H5: the summary binds the sha256 of every attempt file | `r2h_validator.py status` |
| no retry, no resume | unchanged (A27 / R4 B8 / P23): any existing attempt or trace refuses | every restart probe: 3 requests, bytes unchanged |

With r2 as shipped, the same procedure applies, but a crash can leave a torn record (CORRUPT, the attempt lost), and
a lost attempt directory permits a second start (`R2_FAILURE_MATRIX.json` R01, R05, R07).

## 7. Watchdog rules

- **Q-HOST monitor (in the unit):** samples ≤ 60 s apart. It fails on:
  - a foreign or unattributable process above 0.5 core, or all of them together above 1.0 core;
  - a heavy pattern;
  - any continuity break;
  - a monitor gap above 105 s, or the monitor dead at the stop.
  On a failure, the runner SIGKILLs its tree, writes `QHOST_FAIL.json` and a pass:false summary, and exits 3.
- **External watchdog (operator, read-only):** every ≤ 10 min, run the §9 inspection commands. **The external
  watchdog never writes, restarts, signals or resumes anything.** Its only outputs are observations and, on an abort
  condition (§11), a report to the owner.
- **Liveness signals to watch:**
  - `QHOST_MONITOR.jsonl` grows at least once a minute;
  - a new `QCxx.json` appears within the §5 maximum of the previous one;
  - the unit is `active (running)`;
  - the boot id equals `ATTEMPT_START.json`'s.

## 8. Commands to start (in order; as the P309 user, in the P309 clone of the frozen package)

```bash
# 1. read-only audit and suitability (r2 procedure 8a / 8b); no consent needed beyond OD-R2-3
python3 -B code/p309_host.py audit        --config HOST.json > audit.json
python3 -B code/p309_host.py preflight    --config HOST.json            # durability preflight: must PASS
python3 -B code/p309_host.py isolation    --config HOST.json            # must PASS
python3 -B code/p309_host.py gate         --config HOST.json            # exclusion gate: must PASS

# 2. result-free rehearsal of the exact package (synthetic freeze; never qualification) -- see FULL_RESULT_FREE_REHEARSAL.md
python3 <hardening-ns>/code/r2h_rehearse.py run --source <P309 clone> --commit <package commit> \
        --root <empty dir on the P309 volume>/rehearsal_1 --gates all --require-durable-host
python3 <hardening-ns>/code/r2h_rehearse.py status --root <...>/rehearsal_1            # must say PASS

# 3. worker-tier drill through the launcher (needs P0.3), then -- only with OD-R2-0 (D) -- the freeze and the run
python3 -B code/p309_launch.py --mode drill    --host-config HOST.json --print-only     # inspect the unit command
python3 -B code/p309_launch.py --mode drill    --host-config HOST.json
#    ... freeze per r2's procedure (owner-authorized), on THIS host ...
python3 -B code/p309_launch.py --mode official --host-config HOST.json --print-only
python3 -B code/p309_launch.py --mode official --host-config HOST.json                  # the one official attempt
```

`HOST.json` is the host configuration defined in r2's session instructions §3.1. Every value is recorded (redacted) in
the launch record and bound by sha256.

The subcommands and flags above were checked against the bytes at `101ef2cb`:
- `p309_host.py {audit|gate|isolation|provenance|preflight|scratch} [--config PATH | --config-json JSON]`;
- `p309_launch.py --mode {drill|official|host-rerun} --host-config HOST.json [--print-only]`.

r2's 8a audit has a form that writes nothing on the worker: `python3 - audit --config-json '{...}' < p309_host.py`.

## 9. Commands to inspect progress without mutating state

```bash
systemctl status 'p309-r2-*' --no-pager                       # unit state (read-only)
journalctl -u '<unit>' --no-pager -n 50                       # runner stdout ([PASS]/[FAIL] lines)
ls -la  level4/closure_proofs/p5y_k5_cell309_p309_r2/qualification/attempt_1/
tail -n 3 level4/closure_proofs/p5y_k5_cell309_p309_r2/qualification/attempt_1/QHOST_MONITOR.jsonl
cat /proc/sys/kernel/random/boot_id                           # compare with ATTEMPT_START.json (hardened package)
python3 <hardening-ns>/code/r2h_validator.py status \
        level4/closure_proofs/p5y_k5_cell309_p309_r2/qualification \
        level4/closure_proofs/p5y_k5_cell309_p309_r2/ledger/ZERO_TARGET_LEDGER.jsonl \
        --record-utc "$(git log -1 --format=%cI -- level4/closure_proofs/p5y_k5_cell309_p309_r2/ledger/FREEZE_RECORD.json)" \
        --freeze "$(python3 -c 'import json;print(json.load(open("level4/closure_proofs/p5y_k5_cell309_p309_r2/ledger/FREEZE_RECORD.json"))["freeze_commit"])')"
```

During a run the status validator reports INTERRUPTED: the run is incomplete, so this is normal. It only reads.

## 10. Independent post-run verification (all read-only)

1. `r2h_validator.py status …` (as in §9) must report **COMPLETE_PASS**: every record present, ordered and bound by
   the summary; one RUN START; Q-HOST passed; no stray file.
2. QC10 byte identity, independently of the runner. Run `attempt_validator.py certs` (recovery branch `290b6c10`,
   `level4/closure_proofs/p5y_k5_cell309_q11_recovery/code/`) over `QC08_DECOY_STAGE1A.json` and
   `QC10_DECOY_STAGE1A.json`. Expect 48 certificates, set sha256 `a044291a…` (the value reproduced on two hosts), 0
   self-hash mismatches.
3. The target-evaluation count: `count_target_evaluations.py` (same recovery path) over the repository and the scratch
   root must report **0**. Also check that no ref under `refs/p5y-k5-cell309*` exists locally or on the remote.
4. The independent qualification review (r2's route) reads the attempt as committed. Nothing is re-run to "confirm" it.

## 11. Exact abort conditions

The operator stops nothing that the unit and Q-HOST already stop. Each condition below ends the attempt. Under P23,
the attempt is then preserved, classified, and never retried or resumed; a further attempt needs a new owner decision.

1. Any refusal by the launcher, the durability preflight, the isolation check, the exclusion gate or the runner's
   preconditions: **nothing has started** (no attempt directory). Fix the host and re-run from §8 step 1. That is not a
   retry: no attempt exists.
2. Q-HOST FAIL (foreign heavy work, a continuity break, a monitor gap or a dead monitor) gives an **ABORTED**
   attempt.
3. Host reboot, kernel panic, power loss, OOM-kill of the runner, or `systemctl stop` of the unit gives an
   **INTERRUPTED** attempt.
4. Free disk below 40 GB, or a filesystem error, observed by the watchdog: report it. The unit is not stopped by the
   operator unless the owner instructs; a resulting write failure is recorded as such.
5. **Any** of the following, observed at any time: a ref under `refs/p5y-k5-cell309*`, a grant file, a
   `P309_RESULT.json`, or a ledger row with a nonzero target counter. This is a target-integrity incident: stop the
   unit (`systemctl stop '<unit>'`; SIGKILL by its properties) and report to the owner immediately.
6. The owner instructs to stop: `systemctl stop '<unit>'`, which gives an INTERRUPTED attempt.

**Never:** delete or edit anything under `qualification/` or the ledgers; re-launch while an attempt directory
exists (the runner refuses anyway); copy records between attempts; run `p309_driver.py execute`, `seal-only` or
`validate-grant`.
