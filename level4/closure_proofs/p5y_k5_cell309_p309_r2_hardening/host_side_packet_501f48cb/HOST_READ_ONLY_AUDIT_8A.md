# 8a: the read-only host audit (deliverable 2 of 10)

**Authority.** Owner message 5, OD-R2-3: "APPROVE the read-only host audit only. This approval does not authorize
mutation of the qualification host, installation or removal of software, service changes, permission changes, reboot,
qualification execution, or target evaluation."

This procedure stays inside that approval. Every command is read-only with respect to the host. The one exception is
the IMDSv2 session-token request, noted at A-01, which the reviewed audit already makes.

**Bytes.** The audit uses r2 `501f48cb`'s `code/p309_host.py` only:
- blob `1763cd2090532af8befc2e764bba432079d1be0d`;
- sha256 `ec9c8416159cf9e2e7372f97ce179a290def987007dc144591833615ca251f65`.

Requirements are cited by their ids in `HOST_REQUIREMENTS_501F48CB.md` (R-…).

## 0. Before the audit (all must hold; otherwise do not start)

| # | precondition | how it is established |
|---|---|---|
| A0.1 | the host to audit is the one an owner record names | message 3 names the shared AWS ReBaseGuard worker (G-1). Any other host needs a new owner record first |
| A0.2 | a separate P309 host-side session with its own access path and a P309-only credential exists (OD-R2-3); never cell 308's session, user, terminal or credential | the owner provides it. This Cloud Session never connects |
| A0.3 | the cell-308 operator's form **Part A** (`CELL308_COORDINATION_8C.md`) is in hand: checkout path(s) and heavy-job command patterns | without Part A the audit still runs, but AF-1 (world-readability) and the process tagging cannot be judged, and 8b is `HOST_AUDIT_INCOMPLETE` |
| A0.4 | the audit runs at a time the cell-308 operator agreed | it takes a 5 s process sample and starts nothing heavy, but it is still the operator's host |
| A0.5 | the audit user is a **non-root** account | `audit()` judges `readable_by_this_user` as the running user. Root would read everything and would not show the P309 user's view. If only root access is offered, record that, and treat AF-1 as not yet established until the post-bootstrap `isolation` runs as the P309 user |

## 1. What the audit must never do

- write any file or directory on the host. Its output goes to the session's own standard output, then to the
  coordinator. It is never saved on the worker, and it is never written with `> file`;
- install, remove or upgrade anything; create users; change permissions, services, timers, mounts, polkit or sudo
  rules; reboot;
- run `git` anywhere on the host. No clone exists before 8c;
- read inside cell 308's checkout. Only the reviewed `stat()` and `access()` of its top directory, made by `audit()`,
  is allowed;
- signal, renice or ionice any process; `systemctl` anything other than the read-only verbs below;
- write into r2 evidence. The audit's output is filed by the coordinator (§6), never pushed by the host session;
- start the 8d drill, the launcher or the runner, or any qualification or target-related code.

**Read-only verbs allowed.**
- `cat` and `head` of the files named below;
- `findmnt`, `df`, `stat -f`, `stat -c`, `ls -ld`, `id -u`, `uname`, `nproc`, `lscpu`, `free`, `getconf`;
- `systemctl show|is-active|is-enabled|list-timers|list-units|--version`, `systemd-run --version`;
- `timedatectl show`, `journalctl --list-boots`, `pkaction --version`, `apt-mark showhold`, `swapon --show`;
- the system `python3` running the verified `p309_host.py` from standard input.

## 2. A-01: the committed audit (r2's 8a; `R2_BOOTSTRAP.md` §8a, `R2_AWS_SESSION_INSTRUCTIONS.md` §1)

**Configuration**, a shell variable held in memory, never a file:
- `p309_roots`: the planned P309 root(s). Before 8c they may not exist, and the audit then records `null` for their
  free space. Add the existing mount point that will hold them, so disk is measured;
- `foreign_roots` and `foreign_heavy_patterns`: from Part A.

```bash
AUDIT_CFG='{"p309_roots": ["<planned P309 root or its existing mount point>"], "foreign_roots": ["<cell-308 checkout path from Part A>"], "foreign_patterns": ["cell[_-]?308"], "foreign_heavy_patterns": ["<cell-308 heavy-job pattern from Part A>"]}'
```

**The audit itself.** It is fetched in memory, verified, and executed from standard input. Nothing is written on the
host, and the token never appears in a process's argv:

```bash
printf 'Authorization: Bearer %s\n' "$P309_GH_TOKEN" | curl -fsS -H @- -H 'Accept: application/vnd.github.raw' \
  'https://api.github.com/repos/flaggielover/ReBaseGuard/contents/level4/closure_proofs/p5y_k5_cell309_p309_r2/code/p309_host.py?ref=501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853' \
| python3 -B -c 'import sys, hashlib
b = sys.stdin.buffer.read()
h = hashlib.sha256(b).hexdigest()
if h != "ec9c8416159cf9e2e7372f97ce179a290def987007dc144591833615ca251f65":
    sys.exit("REFUSED: p309_host.py bytes are not 501f48cb (sha256 %s)" % h)
exec(compile(b, "p309_host.py", "exec"), {"__name__": "__main__"})' audit --config-json "$AUDIT_CFG"
```

Equivalently, the session's own GitHub tool may supply the bytes. The same sha256 check must come before execution.

**Ground rules:**
- **Read-only guarantee.** `p309_host.py` writes nothing but its standard output (module docstring; reviewed). It runs
  `systemd-detect-virt`, `systemd-detect-virt --container`, `journalctl --list-boots`, `journalctl -k --since -30d`,
  `systemctl is-active unattended-upgrades.service`, `systemctl is-enabled dnf-automatic.timer`, `git version` and
  `timedatectl show -p NTPSynchronized --value`.
- **The IMDS token.** The IMDSv2 `PUT api/token` creates a 60 s metadata session token inside the metadata service. It
  changes no host file, setting or process.
- **Expected output.** One JSON document with `"schema": "P309_R2_HOST/1"`, `"kind": "audit"` and `"read_only": true`.
  Exit status 0 (the audit always passes; the judgement is in 8b).
- **Fail criterion.** A nonzero exit, a `REFUSED:` line (wrong bytes), or JSON that does not parse. Then the audit did
  not happen: record the failure and stop. Do not retry with other bytes.

**Fields and the decisions they feed:**

| audit field | requirement | 8b pass criterion | 8b fail criterion | feeds |
|---|---|---|---|---|
| `provenance.python.version` (system Python) | R-PY-6 | ≥ 3.6 (it ran) | — | 8a only |
| `provenance.glibc` | R-LIBC-1 | recorded (any value) | missing | `glibc` in the host configuration |
| `provenance.kernel`, `provenance.arch` | R-OS-1, R-CPU-3 | Linux; `x86_64` | another arch | 8b; HOST_REJECTED |
| `provenance.machine_id_sha256` | R-ID-1 | non-null | null | 8b; OD-R2-4 X-item |
| `provenance.hostname_sha256` = `etc_hostname_sha256` | R-ID-2 | equal | unequal or null | OD-R2-4 X-item |
| `provenance.ntp_synchronized` | R-CLK-1, R-SD-9 | `true` | `false` / `null` | OD-R2-4 X-item |
| `provenance.suspended_s` | R-DUR-4 | a number | null | 8b (Q-HOST cannot judge suspend) |
| `provenance.cloud.available` | R-IMDS-1 | `true` | `false` | **AF-2** |
| `provenance.cloud.instance_type` | R-CPU-2 | known and not `t2./t3./t3a./t4g.` | burstable or unknown | HOST_REJECTED (resize is outside M1–M5) |
| `provenance.cloud.instance_life_cycle` | R-IMDS-3 | ≠ `spot` | `spot` | HOST_REJECTED |
| `provenance.cloud.scheduled_maintenance` | R-IMDS-2 | `[]`, empty or null | an event | HOST_AUDIT_INCOMPLETE until it has passed; re-audit |
| `provenance.cloud.spot_instance_action` | R-IMDS-3 | null | non-null | HOST_REJECTED |
| `os` (`/etc/os-release`) | R-OS-3 | recorded | — | advisory |
| `pid1` | R-SD-1 | `systemd` | anything else | HOST_REJECTED |
| `cpu.affinity_cpus`, `cpu.logical_cpus`, `cpu.models`, `cpu.hypervisor_flag` | R-CPU-1 | affinity ≥ 4 | < 4 | HOST_REJECTED |
| `cpu.loadavg` | 8c `load_baseline` | recorded | — | 8c baseline (with the operator) |
| `mem_total_gb`, `mem_available_gb` | R-RAM-1/2 | available ≥ 8 (now); total ≥ 8 + the agreed cell-308 working memory | total < 8 | HOST_REJECTED; `memory_max` sizing (OD-R2-4) |
| `disk_free_gb` | R-DISK-1 | ≥ 40 on every planned root | < 40 / null | OD-R2-4 M2 |
| `boots.uptime_h`, `boots.journal_boot_count`, `oom_events_30d` | R-DUR-6 | recorded | — | 8b narrative; window planning |
| `auto_update.automatic_reboot`, `auto_update.needrestart_mode` | R-DUR-1 | false; ≠ `a` | true / `a` | OD-R2-4 M4 |
| `auto_update.unattended_upgrades_active`, `auto_update.dnf_automatic_enabled` | R-DUR-2 | both false | either true | OD-R2-4 M4 |
| `auto_update.reboot_required` | R-DUR-3 | false | true | OD-R2-4 X-item (a reboot is host-wide; cell-308 consent) |
| `container.in_container`, `virt` | R-OS-2 | `false`; `virt` recorded | `true` | HOST_REJECTED |
| `tools.git` | R-GIT-1 | ≥ 2.32 | < 2.32 / null | OD-R2-4 X-item |
| `tools.systemd_run` | R-SD-2 | `true` | `false` | OD-R2-4 X-item |
| `tools.python3_11` | R-PY-3 | recorded. The system `python3.11` is **not** the pinned interpreter (M5) | — | M5 sizing |
| `proc.readable`, `proc.hidepid`, `proc.foreign_visible` | R-FS-10 | `true`, `false`, > 0 | otherwise | OD-R2-4 X-item (a remount is host-wide) |
| `rebaseguard_processes` (pid, uid, tag, CPU fraction, cmd sha256) | R-ISO-6; 8c | recorded | — | `foreign_uids` with the operator (8c); window agreement |
| `foreign_roots.<sha>.exists`, `world_readable`, `readable_by_this_user` | R-ISO-4 | exists; `world_readable=false`; `readable_by_this_user=false` (non-root audit user) | world-readable | **AF-1** |

## 3. Supplementary read-only observations (S-01 … S-17)

Each runs as the audit user and prints to the session only. They cover what the user asked to observe beyond `audit()`
(filesystem, mounts, limits, clock detail, scheduled work).

"Read-only" means each command only reads kernel or file state. None opens a file for writing or changes
configuration. `<R>` is each planned P309 root, or its existing mount point before 8c.

| id | command | purpose | expected output | read-only? | pass | fail | feeds |
|---|---|---|---|---|---|---|---|
| S-01 | `findmnt -no SOURCE,FSTYPE,OPTIONS --target <R>` | filesystem type and mount options | one line, e.g. `/dev/nvme1n1 ext4 rw,relatime` | yes | FSTYPE ∈ {ext4, xfs, btrfs} and no `nobarrier` / `barrier=0` | tmpfs, overlay, nfs*, cifs, fuse*, or `nobarrier` | R-FS-7 (RECOMMENDED): 8b note; OD-R2-4 M2 (choice of volume) |
| S-02 | `df -PT <R>` and `df -Pi <R>` | free space and free inodes | one row each | yes | ≥ 40 GB available; inodes not near exhaustion | < 40 GB | R-DISK-1: M2 |
| S-03 | `stat -f -c '%T bsize=%S blocks=%b avail=%a' <R>` | the filesystem as the kernel names it (cross-check of S-01) | e.g. `ext2/ext3 bsize=4096 …` | yes | agrees with S-01 | disagrees: record, NEEDS AUDIT | R-FS-7 |
| S-04 | `cat /sys/block/<dev>/queue/write_cache` for S-01's device (strip the partition suffix) | volatile write cache | `write back` or `write through` | yes (sysfs read) | either, recorded. `write back` is normal; the kernel flushes on fsync unless `nobarrier` | unreadable: record | R-FS-8 (ADVISORY) |
| S-05 | `ls -ld <R>` and `stat -c '%U:%G %a' <R>` | ownership and mode of the planned roots, or their mount point | recorded | yes | recorded | — | M1/M2 planning |
| S-06 | `cat /proc/1/comm`; `systemctl --version`; `systemd-run --version` | systemd as PID 1, and its version | `systemd`; version lines | yes | `systemd`, both commands present | otherwise | R-SD-1/2: HOST_REJECTED / X-item |
| S-07 | `pkaction --version`; `ls -ld /etc/polkit-1/rules.d` | polkit present (needed for M3) | version; the directory exists | yes | present | absent: X-item (install polkit) | R-SD-4: M3 |
| S-08 | `timedatectl show -p NTPSynchronized -p NTP -p TimeUSec --value` and, if present, `chronyc -n tracking` | clock and time sync | `yes`, `yes`, a time; tracking | yes (`chronyc tracking` is a query) | NTPSynchronized=yes | no / absent | R-CLK-1: X-item |
| S-09 | `cat /proc/self/limits`; `cat /proc/sys/kernel/pid_max /proc/sys/kernel/threads-max`; `cat /proc/sys/vm/overcommit_memory`; `swapon --show` | process and resource limits as the audit user | recorded | yes | recorded | — | ADVISORY (no r2 threshold); `memory_max` sizing |
| S-10 | `cat /sys/fs/cgroup/cgroup.controllers`; `systemctl show -p DefaultMemoryAccounting -p DefaultTasksMax -p DefaultCPUAccounting` | cgroup v2 and the memory controller (`MemoryMax` needs it) | includes `memory cpu io` | yes | `memory`, `cpu` and `io` present | missing: the unit limits cannot apply. X-item | R-SD-6 |
| S-11 | `uname -srm`; `getconf GNU_LIBC_VERSION`; `python3 -VV`; `command -v python3.11 || true`; `git --version` | runtime identity (cross-check of A-01) | recorded | yes | agrees with A-01 | disagrees: re-audit | R-PY-6, R-LIBC-1, R-GIT-1 |
| S-12 | `uptime -s`; `journalctl --list-boots --no-pager \| tail -n 5` | reboot and uptime history | boot list | yes | recorded | — | R-DUR-6; window planning |
| S-13 | `systemctl list-timers --all --no-pager`; for each listed service: `systemctl show -p User -p DynamicUser <service>` | scheduled work, and the account it runs as (SI §4.1, W8) | table | yes | recorded | — | 8c whole-host window agreement |
| S-14 | `python3 -B -c '<S-14 program>'` (below) | cron jobs: schedule and account, command as sha256 only | one line per job | yes (it only reads `/etc/crontab` and `/etc/cron.d/*`) | recorded | unreadable: record | 8c window agreement |
| S-15 | `ls -l /etc/cron.hourly /etc/cron.daily /etc/cron.weekly` | root's periodic jobs | listing | yes | recorded | — | 8c; M4 |
| S-16 | `systemctl is-enabled unattended-upgrades.service apt-daily.timer apt-daily-upgrade.timer 2>&1 \|\| true`; `apt-mark showhold 2>/dev/null \|\| true`; `cat /etc/apt/apt.conf.d/20auto-upgrades 2>/dev/null \|\| true` | automatic upgrade machinery | states | yes | recorded | — | OD-R2-4 M4 (exact current state) |
| S-17 | `ps -eo uid= \| sort -un`; `id -u` | the set of uids with processes (no names, no commands); the audit user's uid | uids | yes | recorded | — | 8c `foreign_uids` (with the operator) and the unattributable rule |

**The S-14 program.** It prints the schedule and account fields of each cron job, and the command only as a sha256.

```python
import glob, hashlib
for f in ["/etc/crontab"] + sorted(glob.glob("/etc/cron.d/*")):
    try:
        lines = open(f).read().splitlines()
    except OSError as e:
        print(f, "UNREADABLE", type(e).__name__); continue
    for l in lines:
        s = l.strip()
        if not s or s.startswith("#") or "=" in s.split()[0]:
            continue
        p = s.split(None, 6)
        if len(p) == 7:
            print(f, " ".join(p[:5]), "user=" + p[5], "cmd_sha256=" + hashlib.sha256(p[6].encode()).hexdigest())
```

Per-user crontabs (`/var/spool/cron`) are not readable by a non-root user. Ask the host administrator for the non-root
accounts that have one (SI §4.1, follow-up X7). Record the answer in the 8c form, Part C.

## 4. What 8a cannot prove read-only: NEEDS CONTROLLED WRITE TEST

| capability | why read-only inference is insufficient | the controlled write test | when |
|---|---|---|---|
| exclusive create refuses an existing name (R-FS-1) | only a create shows it | the runner's `fs_probe` | inside the 8d drill, before its attempt |
| hard links (R-FS-2) | S-01 shows a type that normally supports them; only `link()` proves it | `fs_probe` | 8d |
| file fsync (R-FS-3) | the type and mount options suggest it; only an fsync call proves it succeeds | `fs_probe` | 8d |
| directory fsync (R-FS-4) | as above | `fs_probe` | 8d |
| ledger appendability (R-FS-5, SF1-A) | the ledgers do not exist before the 8c clone | `fs_probe` (SF1-A) | 8d (drill clone) and the official launch (P309 clone) |
| power-loss durability (R-FS-8) | needs a power-cut test | none planned (SAFE_BUT_UNPROVEN; review 5, C5) | — |
| polkit rule works for transient `p309-r2-*` units (R-SD-4) | needs the rule (M3) and a real start | the drill launch itself. A failed start is NOT_STARTED, not an attempt (`WORKER_TIER_PASS_FAIL_RULES.md`) | 8d |
| unit properties take effect (R-SD-5) | needs a unit | the runner's `qhost_preflight` inside the drill unit | 8d |

None of these is recorded as passed at 8a. 8b records each as **NEEDS CONTROLLED WRITE TEST**. The checks are
evidenced by the 8d drill's report (`items.main.pass`, and `host` for the host functions), and by the official
launch for the P309 clone's filesystem when it differs from the scratch root's (R-FS-9).

## 5. After 8c (bootstrap), the same audit as the P309 user (A-02)

Once OD-R2-4 has been decided and its consented items applied (`OD_R2_4_HOST_CHANGE_PACKET.md`), the read-only checks
are repeated **as the P309 user**, with the pinned interpreter and the real host configuration. These are the
reviewed commands of SI §3. Each writes nothing, except the launcher's `--print-only`, which writes exactly one
redacted record into a fresh check directory that is never reused.

```bash
cd <NS>     # <CLONE>/level4/closure_proofs/p5y_k5_cell309_p309_r2 (SI "Working directory")
mkdir <SCRATCH_BASE>/check_<UTC>                                                     # fresh; never a run's scratch root
<INTERP> -B code/p309_host.py audit --config <HOST_CONFIG_NO_LAUNCH_KEYS>           # A-02a
P309_SCRATCH_ROOT=<SCRATCH_BASE>/check_<UTC> \
  <INTERP> -B code/p309_host.py preflight --config <HOST_CONFIG_NO_LAUNCH_KEYS>     # A-02b  must PASS (exit 0)
<INTERP> -B code/p309_host.py isolation --config <HOST_CONFIG_NO_LAUNCH_KEYS> --config-json '{"p309_repo": "<CLONE>"}'   # A-02c must PASS
P309_SCRATCH_ROOT=<SCRATCH_BASE>/check_<UTC> P309_FOREIGN_ROOTS=<FOREIGN_ROOTS> \
  <INTERP> -B code/p309_launch.py --mode drill --host-config <HOST_CONFIG> --print-only   # A-02d: exit 0, "blockers": []
```

Notes:
- `<HOST_CONFIG_NO_LAUNCH_KEYS>` is a copy of the host configuration without the six launch keys (SI §3, last
  paragraph). `p309_host.py` refuses unknown keys, and the launch keys count as unknown there. It is a P309 file in
  the P309 home, outside the clone.
- A-02a–c print to standard output only. A-02d writes exactly one record, `launch_<utc>.json`, into the check
  directory. A-02d is the authoritative combined check: preflight, gate, isolation, no loaded unit, and the launcher
  as the unit user.
- `preflight` and the launcher must run with the pinned interpreter `<INTERP>`. `interpreter_pinned` and
  `python_exact` judge the interpreter that runs them, so `python3` would fail them.
- A-02d's exclusion gate needs a quiet host moment (SI §3). A gate blocker there means only that the moment was not
  quiet; repeat at an agreed quiet moment.

The A-02 outputs decide the **final** 8b verdict (`HOST_VERDICT_RULES_8B.md` §3).

## 6. Recording the audit

The host session returns, as text, to the coordinator:
- A-01's JSON;
- S-01 … S-17's outputs;
- the audit user's uid;
- the exact `AUDIT_CFG`, with foreign roots and patterns replaced by their sha256 (SI's redaction rule C9);
- UTC start and end.

The coordinator commits the bundle as `host_evidence/AUDIT_8A_<UTC>/` in **this hardening namespace**.

**Filing into r2.** r2's text puts the audit in r2's `evidence/host/` (`R2_BOOTSTRAP.md` §8a). Owner message 6
forbids "any additional mutation of r2" under its authorization, and the 8d drill must run on `501f48cb` exactly.
So the audit is **not** filed into r2 before the drill. Its later filing into r2 is part of the owner filing
authorization requested at return point R-2 (`OWNER_RETURN_CONDITION.md`).
