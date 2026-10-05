# Host requirements for P309-r2 at `501f48cb` (deliverable 1 of 10)

**Scope.** This file lists every host requirement for the remaining pre-freeze work (8a–8d and the pre-freeze review)
on r2 commit `501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853` (tree `d7e2c8329b73d68ae07ca37192eb495674e572c9`). It is
**result-free**, and it **authorizes nothing**: no host change, no drill, no freeze, no qualification, no grant, and no
Γ309 evaluation.

**Sources.** Every requirement below is quoted or derived from r2's own bytes at `501f48cb`. Nothing has been added.

| key | source at `501f48cb` (r2 namespace `level4/closure_proofs/p5y_k5_cell309_p309_r2/`) | sha256 |
|---|---|---|
| HR | `governance/R2_HOST_REQUIREMENTS.md` (§2 minimum host, §3 windows, §5–§6 isolation) | `4baeacba…1746` |
| BS | `governance/R2_BOOTSTRAP.md` (8a–8d) | `27939274…ca79` |
| SI | `governance/R2_AWS_SESSION_INSTRUCTIONS.md` (host-side session; §3.1 host configuration) | blob `085d64bd` |
| OP | `governance/OWNER_DECISION_PACKET_R2.md` (OD-R2-3, OD-R2-4 M1–M5, OD-R2-5) | `9be65aa6…caca` |
| HOST | `code/p309_host.py` (`durability_preflight`, `exclusion_gate`, `isolation`, `audit`, `continuity`) | `ec9c8416…1f65` |
| LAUNCH | `code/p309_launch.py` (unit properties, refusals 0–6) | `cd7e4ab9…85fb` |
| DRILL | `code/p309_topology_drill.py` (worker tier) | `ef4ce1bf…f0c1` |
| RUN | `code/p309_qualify.py` (the runner: `fs_probe` with SF1-A, `prelaunch_state`, `qhost_preflight`, Q-HOST) | `540df055…a3af` |
| MAN | `code/make_freeze_manifest.py` (`runtime_identity`; `host_id_sha256`) | `15391711…b27f` |
| MSG | owner messages 3, 4, 5 and 6 (`governance/OWNER_INSTRUCTIONS_R2_VERBATIM.md`, `…_MSG4_…`, `OWNER_DECISIONS_R2_MSG5_VERBATIM.md`, `…_MSG6_…`) | per file |
| HP | the hardening branch's `DURABLE_HOST_EXECUTION_PACKET.md` (not r2-authoritative) | `04757772…94da` |

Values that come only from **HP** are marked as such. HP is not part of r2, so those values are at most RECOMMENDED or
ADVISORY. They never make anything REQUIRED.

**Classification.**
- **REQUIRED:** r2's code refuses without it, or an r2 governance record or owner message requires it.
- **RECOMMENDED:** r2 or HP recommends it, and r2's code does not refuse without it.
- **ADVISORY:** worth observing. No r2 source makes it a requirement.
- **UNKNOWN / NEEDS AUDIT:** no source fixes the value, or only the 8a audit can establish it.

The column "machine check" names the exact check that refuses. "—" means no code checks it.

## 1. OS and runtime

| # | requirement | class | value / rule | source | machine check |
|---|---|---|---|---|---|
| R-OS-1 | Linux kernel | REQUIRED | Linux (`/proc`, `/proc/self/cgroup`, `CLOCK_BOOTTIME`, `sched_getaffinity`) | HR §2; HOST | implicit (the host functions read `/proc`) |
| R-OS-2 | not a container | REQUIRED | none of `/.dockerenv`, `/run/.containerenv` or `/run/systemd/container` exists, and `systemd-detect-virt --container` returns nonzero | HR §2 | `not_in_container` |
| R-OS-3 | distribution | RECOMMENDED | Ubuntu 24.04 LTS, the release of the measured runs (HP §1). r2 names no distribution | HP | — |
| R-PY-1 | interpreter version | REQUIRED | **CPython 3.11.15 exactly** | HR §2; SI §3.1 `python_version` | `python_exact` |
| R-PY-2 | implementation | REQUIRED | `CPython` (the freeze manifest pins `implementation`; `check_bindings` refuses any difference) | MAN `runtime_identity`; driver `RUNTIME_KEYS` | `check_bindings` (in the drill's synthetic freeze and in the real freeze) |
| R-PY-3 | P309-private interpreter, path pinned | REQUIRED | under the P309 user's home; the system Python untouched; `interpreter` in the host configuration equals the real path of the running interpreter | HR §2; BS 8c-4; SI §3.1 | `interpreter_pinned` |
| R-PY-4 | interpreter binary pinned | REQUIRED | the sha256 of the real interpreter binary is pinned by the freeze manifest | MAN; HR §2 "runtime binding" | `check_bindings` |
| R-PY-5 | stdlib only | REQUIRED | no third-party package. The modules r2 imports are stdlib (`argparse ast copy datetime fractions functools glob hashlib importlib json math multiprocessing os pathlib platform pwd random re resource runpy shutil signal socket stat subprocess sys tempfile time types unittest urllib uuid`) plus repository modules | MAN `stdlib_only=True`; import scan of `501f48cb` | indirect (an import error fails the gate that needs it) |
| R-PY-6 | system Python for 8a | REQUIRED | Python ≥ 3.6 on the host (the audit runs on the system interpreter from standard input) | HOST docstring; BS 8a | — (a SyntaxError or ImportError) |
| R-LIBC-1 | glibc pinned | REQUIRED | equal to the value 8a records (`os.confstr("CS_GNU_LIBC_VERSION")`); the manifest binds it | HR §2; SI §3.1 `glibc` | `glibc_pinned`; `check_bindings`; Q-HOST `same_glibc` |
| R-GIT-1 | git version | REQUIRED | ≥ 2.32 | HR §2 | audit `tools.git` (recorded; the code needs `rev-parse --path-format=absolute`) |
| R-GIT-2 | git build | RECOMMENDED | 2.43, the version of the measured runs | HP §1 | — |

## 2. CPU, RAM and storage

| # | requirement | class | value / rule | source | machine check |
|---|---|---|---|---|---|
| R-CPU-1 | dedicated vCPUs | REQUIRED | ≥ 4 in this process's affinity mask (`min_cpus`; the launcher runs the runner with `--workers 4`) | HR §2; LAUNCH `SCRIPT` | `enough_cpus` |
| R-CPU-2 | not burstable | REQUIRED | the IMDS instance type matches none of `t2.`, `t3.`, `t3a.` or `t4g.`, and is known | HR §2 | `not_burstable` (fails without IMDS) |
| R-CPU-3 | architecture | REQUIRED (document) | x86_64. HR §2 states it; no code refuses another architecture, and the audit records `arch` | HR §2 | — (recorded: `provenance.arch`) |
| R-CPU-4 | single tenant, 4–8 dedicated | RECOMMENDED | under OD-R2-5 (i), any heavy foreign process ends an attempt | HP §1 | — |
| R-RAM-1 | RAM available at the gate | REQUIRED | `MemAvailable` ≥ 8 GB (`ram_floor_gb`) | HR §2 | `ram_available` (preflight and gate) |
| R-RAM-2 | RAM size | RECOMMENDED | 16 GB. Measured peak under 1 GB with 4 jobs; about 15 of 16 GB stayed available | HR §1, §2 | — |
| R-RAM-3 | unit memory limit | REQUIRED (value agreed) | `MemoryMax` must leave cell 308 its working memory; the value is agreed under OD-R2-4 (SI's example is `12G`) | OP OD-R2-4; SI §3.1 | set by the launcher, recorded, **not checked** by the runner |
| R-RAM-4 | test headroom | REQUIRED (derived) | the host controls' K02 case starts two 512 MB TEST processes inside the unit, so `MemoryMax` must leave room for them beside the runner | `tests/test_p309_host_controls.py` K02 | the drill's `host_controls_rc` |
| R-DISK-1 | free disk | REQUIRED | ≥ 40 GB free on **every** `p309_roots` entry (`disk_floor_gb`), at the preflight and at the gate | HR §2 | `disk_available` |
| R-DISK-2 | free disk during the window | RECOMMENDED | keep ≥ 40 GB free for the whole window; a full disk mid-run makes a record write fail | HP §2 | — |
| R-DISK-3 | size | RECOMMENDED | 60 GB: about 0.5 GB per clone, about 1 GB of scratch mirrors, and the drill clone and decoy outputs | HP §1 | — |

## 3. Filesystem

| # | requirement | class | value / rule | source | machine check |
|---|---|---|---|---|---|
| R-FS-1 | exclusive create | REQUIRED | `O_CREAT|O_EXCL|O_NOFOLLOW` creates, and refuses an existing name | RUN `fs_probe`, `xwrite` | `fs_probe` step "exclusive create (O_EXCL)" and "… over an existing name" |
| R-FS-2 | hard links | REQUIRED | a same-directory `link()` gives a second name of the same inode (`st_nlink` ≥ 2, the same bytes) and refuses an existing name | RUN `fs_probe`, `xwrite` (H1) | `fs_probe` steps "same-directory hard link" and "… over an existing name" |
| R-FS-3 | file fsync | REQUIRED | `fsync(fd)` succeeds | RUN `fs_probe`, H1/H2 | `fs_probe` step "file fsync" |
| R-FS-4 | directory fsync | REQUIRED | `fsync` of a directory fd (`O_RDONLY|O_DIRECTORY`) succeeds | RUN `fs_probe`, `_fsync_dir` | `fs_probe` step "directory fsync" |
| R-FS-5 | ledger appendability (SF1-A) | REQUIRED | `ledger/ZERO_TARGET_LEDGER.jsonl` and `ledger/EXPOSURE_LEDGER.jsonl` exist and open `O_WRONLY|O_APPEND|O_NOFOLLOW`; nothing is written | RUN `fs_probe` (SF1-A); `governance/REVIEW_SF1A_DELTA.md` | `fs_probe` step "ledger appendability" |
| R-FS-6 | ledgers launchable | REQUIRED | every ledger row parses, the file ends with a newline, and every target counter is 0 | RUN `prelaunch_state` (H3) | `_ledger_problems` |
| R-FS-7 | filesystem type | RECOMMENDED | local, persistent and journaling, and honouring fsync: ext4 (`data=ordered`), xfs or btrfs. Not tmpfs, overlayfs, NFS/SMB/FUSE, `nobarrier`, or a volatile write cache that is not flushed | HP §2; review 5 C5 ("depends on the host filesystem (ext4 / xfs)") | — |
| R-FS-8 | power-loss durability | ADVISORY | SAFE_BUT_UNPROVEN. It cannot be proven without a power-cut test | HP §2; review 5 C5 | — |
| R-FS-9 | where the probe runs | ADVISORY (important) | `fs_probe` probes the filesystem of the **qualification directory**. In the 8d drill that directory is inside the drill clone, under `P309_SCRATCH_ROOT`; in the official run it is inside the P309 clone. If the clone and the scratch root are on different filesystems, the drill does not probe the clone's filesystem; the official launch then probes it, before any attempt exists. Placing both on one filesystem makes the drill's probe cover the official run's filesystem | derived from RUN and DRILL | — |
| R-FS-10 | `/proc` | REQUIRED | readable; not mounted with `hidepid` (≠ 0/off); at least one process of another user visible | HOST `proc_access` | gate `proc_readable`, `proc_not_hidepid`, `foreign_processes_visible` |

**What 8a can establish.** A read-only audit cannot prove R-FS-1 to R-FS-5. They are **NEEDS CONTROLLED WRITE TEST**.
The reviewed controlled write test is the runner's own `fs_probe`. It runs:
- inside the 8d drill, in the drill clone's qualification directory, before Q-HOST, the attempt and the RUN START;
- at the official launch, in the P309 clone's qualification directory.

It writes only inside `.p309-fsprobe-<pid>/`, which it creates and removes itself.

## 4. systemd, privilege and the unit

| # | requirement | class | value / rule | source | machine check |
|---|---|---|---|---|---|
| R-SD-1 | systemd as PID 1 | REQUIRED | `/proc/1/comm` = `systemd` | HR §2 | `pid1_is_systemd` |
| R-SD-2 | `systemd-run` | REQUIRED | on `PATH` | HR §2 | `systemd_run_available` |
| R-SD-3 | `systemctl` works | REQUIRED | `systemctl list-units --all --no-legend --plain` succeeds; no `p309-r2-*` unit is loaded | LAUNCH refusal 5 | `p309_units_loaded` / `systemctl_unavailable` |
| R-SD-4 | launch privilege | REQUIRED | a **polkit** rule lets the P309 user start only transient system units named `p309-r2-*` (SI §3 adds: and reset them if failed). No sudo rule is used | HR §2; BS 8c-5; OP OD-R2-4 M3; SI §3 | the unit's start (`systemd-run` rc) |
| R-SD-5 | unit properties (checked) | REQUIRED | `Restart=no`, `KillMode=control-group`, `KillSignal=SIGKILL` (`9`), `NoNewPrivileges=yes`, `PrivateTmp=yes`, `ProtectSystem=strict` | LAUNCH; RUN `UNIT_REQUIRED` | `qhost_preflight` (refuses) |
| R-SD-6 | unit properties (recorded only) | REQUIRED (set by the launcher) | `SendSIGKILL=yes`, `TimeoutStopSec=10s`, `MemoryMax`, `OOMScoreAdjust`, `CPUWeight`, `IOWeight`, `ReadWritePaths=<repo> <scratch>`, `InaccessiblePaths=-<each foreign root>` | LAUNCH; OP OD-R2-4 | recorded in `UNIT_PROPERTIES.json` / the drill report, **not checked** (follow-up FU1 (a)) |
| R-SD-7 | the launcher runs as the unit user | REQUIRED | `getuid()` equals the unit user's uid | LAUNCH refusal 6 | `launcher_not_unit_user` |
| R-SD-8 | unit user | REQUIRED | exists; not root; owns no foreign root; not a configured cell-308 uid | LAUNCH refusal 0 (A16) | `unit_user_check` |
| R-SD-9 | `timedatectl` | REQUIRED (effective) | `ntp_status()` returns None without `timedatectl`, so `ntp_synchronized` fails | HOST `ntp_status` | `ntp_synchronized` |
| R-SD-10 | `journalctl`, `systemd-detect-virt` | RECOMMENDED | without them the audit's boot and OOM counts are null, and container detection falls back to its file checks; r2 refuses nothing for their absence | HOST `system_reads`, `_container` | — (audit fields) |

## 5. Durability and boot/restart expectations

| # | requirement | class | value / rule | source | machine check |
|---|---|---|---|---|---|
| R-DUR-1 | no automatic reboot | REQUIRED | no `Unattended-Upgrade::Automatic-Reboot "true"/"1"` under `/etc/apt/apt.conf.d`; needrestart mode ≠ `a` | HR §2 | `no_automatic_reboot` |
| R-DUR-2 | upgrades held | REQUIRED | `unattended-upgrades.service` not active; `dnf-automatic.timer` not enabled | HR §2 | `upgrades_held` |
| R-DUR-3 | no pending reboot | REQUIRED | `/var/run/reboot-required` absent | HR §2 | `no_pending_reboot` |
| R-DUR-4 | no reboot or suspend during a window | REQUIRED | Q-HOST fails on another boot id or on more than `suspend_tolerance_s` (5 s) of suspend | HR §6; HOST `continuity` | Q-HOST `same_boot`, `no_suspend` |
| R-DUR-5 | time left for QC-D5 | RECOMMENDED | QC-D5 starts with ≥ 2.75 h of guaranteed host time left: no maintenance, reboot or co-tenant start until the summary exists | HP §5 | — |
| R-DUR-6 | host history | NEEDS AUDIT | uptime, journal boot count, OOM events in 30 days (recorded by the audit; no threshold in r2) | HOST `audit` | — (recorded) |

## 6. Cloud metadata and network

| # | requirement | class | value / rule | source | machine check |
|---|---|---|---|---|---|
| R-IMDS-1 | instance metadata readable | REQUIRED | IMDSv2 at `169.254.169.254`: a token `PUT`, then `meta-data/…`; proxy-free; 1 s timeouts | HR §2; HOST `imds` | `cloud_metadata_available` |
| R-IMDS-2 | no scheduled maintenance | REQUIRED | `events/maintenance/scheduled` ∈ {`[]`, empty, absent} with IMDS available | HR §2 | `no_scheduled_maintenance` |
| R-IMDS-3 | not spot | REQUIRED | `instance-life-cycle` ≠ `spot`, with IMDS available | HR §2 | `not_spot` |
| R-IMDS-4 | no IMDS | REQUIRED condition | without IMDS, R-IMDS-1–3 and R-CPU-2 fail closed. The route is owner condition **AF-2**: a minimal reviewed portability proposal, never implemented pre-emptively | MSG 5 AF-2; HP P0.4 | — |
| R-NET-1 | during a window | REQUIRED | only IMDS (link-local) is read by the gates. The drill clones from the local P309 repository, so no other network access is used | HP §4; DRILL step 1 | — |
| R-NET-2 | before and after | REQUIRED | fetch and push of the P309 branch to GitHub, through a P309-only credential kept out of the repository configuration; the owner's machine is never a relay | HR §5; MSG 3 item 9 | `isolation.p309_config_has_no_credential` |
| R-NET-3 | ports and services | ADVISORY | r2 opens no port and runs no service other than the transient `p309-r2-*` units | LAUNCH; HOST | — |

## 7. Clock, identity and isolation

| # | requirement | class | value / rule | source | machine check |
|---|---|---|---|---|---|
| R-CLK-1 | NTP synchronised | REQUIRED | `timedatectl show -p NTPSynchronized --value` = `yes` | HR §2 | `ntp_synchronized` |
| R-ID-1 | machine-id present | REQUIRED | `/etc/machine-id` non-empty | HR §2 | `machine_id_present` |
| R-ID-2 | static hostname | REQUIRED | `/etc/hostname` equals `gethostname()`; never rename the host during a window | HR §2; HP §3 | `hostname_static` |
| R-ID-3 | host identity | REQUIRED | host id = sha256("machine-id:" + machine-id + "\nhostname:" + hostname) (`p309_guard.host_id`). Q-HOST continuity also binds the boot id, the instance id (IMDS), the interpreter, glibc and suspend. All identities are recorded as sha256 only | RUN; HOST `continuity`; MAN `host_id_sha256` | Q-HOST; `check_bindings` |
| R-ID-4 | the freeze host is the qualification host | REQUIRED (later) | the freeze manifest records `runtime.host_id_sha256`, so a freeze cannot be qualified on another host (step 10; outside this packet) | MAN; HP §3; BS 8d | `make_freeze_manifest --check` |
| R-ISO-1 | separate P309 user | REQUIRED | no group membership that grants access to cell 308's checkout | HR §5; OP M1 | `isolation.foreign_roots_unreadable` |
| R-ISO-2 | P309 clone | REQUIRED | a single-branch full clone of `claude/p5y-k5-cell309-p309-r2`, top level, no alternates, no cell-308 ref, on the r2 branch, no credential in its configuration | HR §5; HOST `isolation` | `isolation` (8 checks) |
| R-ISO-3 | disjoint roots | REQUIRED | P309 roots, the clone and `P309_SCRATCH_ROOT` never overlap a foreign root; the scratch root is absolute, resolved, existing, and does not overlap the clone | HOST `isolation`, `scratch_root` | `p309_roots_disjoint_from_foreign_roots`; `scratch_root_valid` |
| R-ISO-4 | cell-308 checkout unreadable to the P309 user | REQUIRED | by its permissions, outside the unit. If it is world-readable, owner condition **AF-1** applies | HR §5; MSG 5 AF-1 | `foreign_roots_unreadable` |
| R-ISO-5 | foreign-root path characters | REQUIRED | every foreign root is absolute, from `[A-Za-z0-9._/+@,=~-]` only | LAUNCH refusal 0 | `unit_user_check` |
| R-ISO-6 | `foreign_uids` | REQUIRED | non-empty, and not the P309 user's uid | HR §6; OP C2 | gate `foreign_uids_configured` |
| R-ISO-7 | nothing shared | REQUIRED | no shared object store, alternates, worktree, ref, temporary directory or evidence directory with cell 308 | HR §5; MSG 3 items 1, 2, 5 | `isolation` |

## 8. Gate durations and the QC-D5 envelope

Wall times as measured. "Maximum" is HP's rule: 2× the slowest observation, rounded up. Only the 9 h windows and the
QC08–QC10 measurements come from r2 (HR §1, §3); the rest is HP and is RECOMMENDED.

| gate | r1 freeze host, 4 workers (HR §1 / HP) | cloud container, contended (HP) | worker-tier observation | maximum to allow (HP) |
|---|---|---|---|---|
| QC01–QC05 | 1–8 s each | 1–11 s each | none yet | 1 min each |
| QC06 | 831 s | 1 108 s | none yet | 40 min |
| QC07 | 143 s | 124–202 s | none yet | 7 min |
| QC08 (decoy Stage 1a) | 4 310 s | 7 639 s | none yet | 4.3 h |
| QC09 | 9 769 s | 13 702 s | none yet | 7.6 h |
| QC10 (byte identity with QC08) | 3 864 s | about 2 h | none yet | 4.3 h |
| QC11 | — | 178–288 s | none yet | 10 min |
| QC12 | 7 s | 10–17 s | none yet | 1 min |
| QC13–QC15, QC17, QC_U2 | 0.1–61 s | 0.1–83 s | none yet | 3 min each |
| QC16 | 654 s | 1 218–1 286 s (725.5 s in cloud drill attempt 10) | none yet | 45 min |
| **QC_D5** | — (r1 killed in it) | **3 582 s; 4 913 s; 3 499.4 s (cloud drill attempt 10)** | none yet | **2.75 h** |
| whole runner | 5.47 h for QC01–QC_U2; about 5.7–5.9 h complete | about 8–9 h projected | none yet | — |

| window | r2 (HR §3) | HP |
|---|---|---|
| worker-tier drill (8d) | about 6 h expected; **about 9 h** window | 12 h recommended with any co-tenant |
| the drill's own limit on the runner | 12 h (`run_items` subprocess timeout) | — |
| official qualification (later, outside this packet) | about 5.9 h; about 9 h window | — |

**The QC-D5 envelope.** The class is REQUIRED for the window and RECOMMENDED for the 2.75 h margin. QC-D5 is the last
gate. Its controls run as a single CPU-bound process for 60–85 min on 4 vCPU.
- Plan the window so that QC-D5 starts with ≥ 2.75 h of guaranteed host time left (HP §5).
- r1's attempt and two development runs were interrupted inside QC-D5.

## 9. Owner and governance facts that bound the host work (not host properties)

| # | fact | source |
|---|---|---|
| G-1 | **Which host.** Message 3 permits sharing "the existing AWS ReBaseGuard worker currently used by cell 308". Message 5 OD-R2-3: "Dedicated qualification-host availability is not decided by this answer. Treat it as pending host selection/confirmation unless an already-authoritative owner record states otherwise." Message 3 is such a record for the **shared** worker. A different or dedicated host needs a new owner record | MSG 3; MSG 5 |
| G-2 | OD-R2-3 approves **the read-only host audit only**. It does not authorize "mutation of the qualification host, installation or removal of software, service changes, permission changes, reboot, qualification execution, or target evaluation" | MSG 5 |
| G-3 | OD-R2-4 is **DEFERRED** until the audit identifies the exact host changes. "Do not infer consent to host mutation from OD-R2-3" | MSG 5 |
| G-4 | OD-R2-5 = **(i)**: a cell-308 heavy start, or any qualifying foreign or unattributable activity, during a run ends the single attempt | MSG 5 |
| G-5 | this Cloud Session is never the durable host | MSG 4 #13 |
| G-6 | no AWS, Vultr, SSH or paid external compute from this session; the host-side work belongs to a separate P309 session with its own access path (OD-R2-3) | standing prohibitions; OP OD-R2-3 |
| G-7 | the drill runs on the incorporated bytes `501f48cb` (formal review 5, C3; SF1-A review, C-F1) | `governance/R2_DELTA_FOLLOWUP_5_RECORD.md`; `governance/REVIEW_SF1A_DELTA.md` |
| G-8 | OD-R2-0(D) is OPEN. No freeze and no qualification; no grant (AF-4); Γ309 forbidden; Cell 309 OPEN | MSG 5, MSG 6 |
