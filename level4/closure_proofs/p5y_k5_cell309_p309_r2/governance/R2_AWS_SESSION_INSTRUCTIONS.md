# P309-r2: instructions for a future AWS-side P309 session (gate step 8)

**Status when written: HOST_SUITABILITY_PENDING.** The AWS worker has not been audited. Nothing here has run there.

These steps cover the shared AWS ReBaseGuard worker that cell 308 uses (owner message 3). They complete
`R2_BOOTSTRAP.md` and `R2_HOST_REQUIREMENTS.md` and do not replace them. They were revised after the follow-up reviews
(`REVIEW_R2_DELTA_FOLLOWUP_1.md`, FU1 and FU4; `REVIEW_R2_DELTA_FOLLOWUP_2.md`, SF1, SF2, W7 and W8;
`REVIEW_R2_DELTA_FOLLOWUP_3.md`, X7).

**Working directory.** Every `code/...` command in this document runs from the r2 namespace directory of the P309
clone, `<clone>/level4/closure_proofs/p5y_k5_cell309_p309_r2`, not from the clone's root (follow-up X7). **No step may start before the owner has
answered OD-R2-3 (the access path) and, for 8c onward, OD-R2-4 (consent to host changes).**

## 0. Who runs this, and what never happens

**Who:** a separate P309 session, with its own access path and its own P309-only credential (OD-R2-3). Never cell
308's session, terminal, user or credential.

**What never happens, at any step:**
* any read, `git` command, checkout, clean, reset or write inside cell 308's checkout, worktree, evidence or refs;
* any signal, kill, pause, renice or ionice of any process the P309 session did not start;
* any `systemctl` action on a unit not named `p309-r2-*`;
* any reboot, upgrade, package install or configuration change on the host without OD-R2-4 consent;
* any target evaluation, production-namespace ref, grant, marker or pending-result ref, and no freeze or official
  qualification without the later owner decisions;
* any bulk data through the owner's own machine.

## 1. Step 8a: read-only audit (no clone, no user, no install)

**Getting the file.** Fetch the reviewed `code/p309_host.py` blob through the P309 session from GitHub (branch
`claude/p5y-k5-cell309-p309-r2`, at the commit the owner names). Keep it **in memory or on standard input only**;
nothing is saved on the worker. For example, read it through the session's GitHub tool and pipe it into Python.

**The command.** Run it on the worker's system Python:

```text
python3 - audit --config-json '{"p309_roots": ["<planned P309 root path>"], "foreign_roots": ["<cell-308 checkout path, as given by the owner or the cell-308 operator>"], "foreign_patterns": ["cell[_-]?308"], "foreign_heavy_patterns": ["<cell-308 heavy-job command patterns, from the cell-308 operator>"]}'
```

The rows of the audit carry each tagged process's uid. Together with the cell-308 operator, they establish the
`foreign_uids` for §3.1. The audit itself does not need them: without them, it reports what it can see.

**What the audit records:**
* **Identities:** hostname, machine-id and instance id, each as sha256 only.
* **Hardware:** CPU model and count, RAM, disk free on the planned roots.
* **OS and runtime:** OS, kernel, glibc, Python, git version.
* **Durability:** boots (journal count, uptime), OOM events (30 days), automatic upgrade and reboot settings, pending
  reboot, container detection, systemd.
* **AWS:** IMDSv2 instance type, life cycle, scheduled maintenance and spot action. The request uses a proxy-free
  opener with 1 s timeouts.
* **/proc visibility:** hidepid, and whether foreign processes are visible.
* **ReBaseGuard processes:** counts by tag; for each, pid, uid, CPU fraction and command-line sha256 only.
* **The cell-308 checkout:** only a `stat()` of its top directory, recorded as a hash, whether it is world-readable
  (a boolean; delta review A9), and whether this user could read it.

**Return.** The JSON goes on standard output. The session returns it to the coordinator, who commits it as
`evidence/host/AUDIT_<utc>.json` in the r2 branch.

## 2. Step 8b: verdict (no host change)

Apply `R2_HOST_REQUIREMENTS.md` §4 to the audit:

| verdict | when |
|---|---|
| HOST_SUITABLE pending bootstrap | every §2 item is met, or can be met by a listed bootstrap item |
| HOST_NOT_SUITABLE | an item cannot be met without an unconsented change |
| HOST_SUITABILITY_PENDING | anything is unknown |

Report to the owner and the cell-308 operator:
* the measured CPU, RAM and disk;
* every proposed host change (§3), each marked read-only or mutating;
* the windows needed, about 9 h each, for the worker drill and the official run.

**STOP** until OD-R2-3 and OD-R2-4 are answered.

## 3. Step 8c: bootstrap (only the items consented under OD-R2-4)

Every item below changes the host and needs consent:

| item | change | notes |
|---|---|---|
| P309 Unix user | create a user, e.g. `p309`, with no supplementary group that can read cell 308's checkout | mutating |
| volume / quota | at least 40 GB free on the P309 roots | mutating if new storage |
| clone | `git clone --single-branch --branch claude/p5y-k5-cell309-p309-r2 <repository URL>` in the P309 user's home; full history; no alternates; credential kept outside the repository config | P309 files only |
| interpreter | CPython 3.11.15 built or installed under the P309 user's home (the system Python untouched); record path, sha256 and glibc | P309 files only |
| launch privilege | a **polkit** rule letting the P309 user start (and reset, if failed) only transient system units named `p309-r2-*`. The launcher calls `systemd-run` directly, so a sudo rule is never used. `systemctl list-units` and `systemctl show` are read-only and need no rule | mutating, privileged |
| durability holds | automatic reboot off and upgrades held for each window | mutating; host-wide; the cell-308 operator must agree |
| host config | `~p309/p309_host_config.json` (not in the repository; readable by the P309 user, not world-writable): §3.1. The launch record binds its sha256, and the run refuses if its bytes change before the runner reads it (`P309_HOST_CONFIG`) | P309 files only |

### 3.1 The host configuration (every key is required unless marked; unknown keys are refused)

```json
{
 "p309_roots": ["/home/p309/ReBaseGuard", "/p309vol/scratch"],
 "foreign_roots": ["<the cell-308 checkout path(s) given by the owner or the cell-308 operator>"],
 "foreign_patterns": ["cell[_-]?308"],
 "foreign_heavy_patterns": ["<command patterns of cell-308 heavy jobs, from the cell-308 operator>"],
 "foreign_uids": [1000],
 "load_baseline": 0.0,
 "load_margin": 0.5,
 "heavy_cpu_fraction": 0.05,
 "monitor_heavy_cpu_fraction": 0.5,
 "monitor_aggregate_cpu_fraction": 1.0,
 "monitor_gap_tolerance_s": 45,
 "ram_floor_gb": 8,
 "disk_floor_gb": 40,
 "min_cpus": 4,
 "sample_s": 60,
 "suspend_tolerance_s": 5,
 "python_version": "3.11.15",
 "interpreter": "/home/p309/opt/python3.11.15/bin/python3.11",
 "glibc": "<the value the 8a audit recorded, e.g. glibc 2.35>",
 "branch": "refs/heads/claude/p5y-k5-cell309-p309-r2",
 "unit_user": "p309",
 "unit_group": "p309",
 "memory_max": "12G",
 "oom_score_adjust": 500,
 "cpu_weight": 20,
 "io_weight": 20
}
```

* **`load_baseline`** is the host's idle 1-minute and 5-minute load, measured together with the cell-308 operator
  (P9).
* **`heavy_cpu_fraction`** is the start gate's strict threshold: any cell-308 process above it, or newly
  appeared, blocks the start. **`monitor_heavy_cpu_fraction`** is the in-run Q-HOST threshold (heavy work only;
  OD-R2-5 (i)).
* **`foreign_heavy_patterns`** are the cell-308 job command patterns. They are matched in memory only. Every record
  holds them as sha256 only: the launch record, the attempt's copy of it, and the unit properties. The monitor receives
  its configuration on standard input, never on its command line (delta review C9).
* **`foreign_uids`** (the `1000` above is only an example; the real value is the cell-308 campaign's uid or uids,
  established from the 8a audit's rows with the cell-308 operator) must be non-empty, and must not hold the P309 user's uid: the gate refuses otherwise (delta
  review C2). Under the separate P309 user, a cell-308 process's working directory cannot be read, so it is
  recognised by its uid, its command line, or as **unattributable**:
  * an unattributable process is one of another non-root user whose working directory cannot be read;
  * it counts as foreign at the gate and in the monitor.

  If cell 308 runs as root, its uid 0 must be listed. Every root process then counts as foreign. Kernel threads do
  not count.
* **`monitor_aggregate_cpu_fraction`**: the in-run monitor also fails when foreign and unattributable processes
  together use more than this many cores (A8).
* **`monitor_gap_tolerance_s`**: Q-HOST fails when the monitor is dead at the stop (C4), or when any gap exceeds the
  interval (60 s) plus this tolerance. The gaps are measured between the runner's start, every monitor event and the
  runner's stop, on the monotonic clock. Each sample writes two events: a start-of-sample row and a result row (follow-up
  SF1). So with samples of at most 60 s, every gap is at most the longer of the sample's duration and the interval: at
  most 60 s, whatever the moment of the stop. The code allows a sample of about 47 s at worst (a 20 s process sample,
  a 20 s `timedatectl` timeout, the metadata reads), so the default of 45 s leaves a margin of 45 s over 60 s. A sample
  that hangs for more than 105 s fails Q-HOST. The control `MV01`–`MV05` in `tests/test_p309_host.py` drives the
  committed monitor loop on a virtual clock to show this.
* **`memory_max`** must leave cell 308 its working memory. It is agreed under OD-R2-4.
* **`p309_repo`** and **`require_empty_scratch`** are set by the launcher itself.

After bootstrap, run the launcher's `--print-only` as the P309 user from the clone, with a fresh scratch directory
used for nothing else (follow-up SF2). It reads the §3.1 file as the launch does (`load_launch_config`). It runs the
durability preflight, the exclusion gate and the isolation check, writes one redacted record into that directory,
and starts nothing:

```text
mkdir <a fresh check directory on the P309 volume>
P309_SCRATCH_ROOT=<that directory> P309_FOREIGN_ROOTS=<cell-308 paths> python3.11 -B code/p309_launch.py --mode drill --host-config ~/p309_host_config.json --print-only
```

It must report no blocker. Preserve the record (`launch_<utc>.json`) in `evidence/host/`. That directory is never
reused as the scratch root of a real launch, which must start empty for an official run or a host re-run.

"No blocker" includes the exclusion gate (follow-up X7). The check therefore needs a quiet moment on the host: no
foreign or unattributable process above 0.05 of a core, and the load at the agreed baseline. Run it at a time agreed
with the cell-308 operator. A gate blocker at this step says only that the moment was not quiet; it is not a host
verdict. The record keeps at most 80 process rows (`processes[:80]`), with counts by tag for all of them.

`code/p309_host.py isolation|preflight|gate --config FILE` reads a host configuration **without** the six launch
settings: it refuses unknown keys, and the launch settings count as unknown there. To run those subcommands alone,
give them a copy of the §3.1 file without those six keys, plus
`--config-json '{"p309_repo": "<the clone path>"}'` for `isolation`.

## 4. Step 8d: worker-tier drill (P14), the burn-in

**Preconditions:**
* the exclusion gate shows cell 308 idle at the start of the agreed window;
* `P309_SCRATCH_ROOT` is a fresh, empty directory on the P309 volume;
* `P309_FOREIGN_ROOTS` lists cell 308's checkout path(s).

**The command:**

```text
P309_SCRATCH_ROOT=<fresh dir> P309_FOREIGN_ROOTS=<cell-308 paths> python3.11 -B code/p309_launch.py --mode drill --host-config ~/p309_host_config.json
```

The launcher refuses at once if the unit user is root, owns a foreign root, or is a configured cell-308 uid (A16).

**What the launcher does.** It refuses unless all of these pass:
* the scratch root;
* the durability preflight;
* the exclusion gate (60 s sample);
* the isolation check;
* no loaded `p309-r2-*` unit (a failing `systemctl` is a blocker).

It then writes `launch_<utc>.json` exclusively (§8) and starts **one** transient unit `p309-r2-drill-<utc>`:
* `Restart=no`, `KillMode=control-group`, `KillSignal=SIGKILL`, `SendSIGKILL=yes`, `TimeoutStopSec=10s` (the heavy
  jobs ignore SIGTERM; delta review C5);
* MemoryMax, OOMScoreAdjust, low CPU/IO weight;
* ProtectSystem=strict, PrivateTmp, NoNewPrivileges;
* InaccessiblePaths for the foreign roots.

It never retries.

**What happens inside the unit:**
* the drill clones the committed branch under the scratch root;
* it builds F' and FR';
* it runs the clone's runner `main()`. That passes Q-HOST because the record names this unit, the configuration
  file's bytes match the record, six of the unit's effective properties (`systemctl show`: Restart, KillMode,
  KillSignal, NoNewPrivileges, PrivateTmp, ProtectSystem) are the launcher's, and the host
  is unchanged;
* then the host functions run (including `tests/test_p309_host_controls.py`, whose cross-uid case needs root and is
  recorded as not applicable under the P309 user), and then the controls.

**The runner's Q-HOST monitor:**
* samples every ≤ 60 s for continuity (boot, machine-id, hostname, instance, interpreter, glibc, suspend);
* also samples cell-308 or other ReBaseGuard heavy activity outside the unit's cgroup;
* on any failure it signals the runner. The runner SIGKILLs its own process tree at once, records QHOST FAIL and
  exits 3;
* the drill then stops at once: no witness, host function or control runs after it. It reports FAIL and exits, and
  the unit's KillMode=control-group with SIGKILL stops anything left;
* at the end, Q-HOST also requires the monitor to have been alive at the stop with no gap over the limit, and a final
  sample to show the same host;
* there is no retry.

**Watching:** `journalctl -u p309-r2-drill-<utc> -f` (read-only).

### 4.1 Operating procedure for the unattributable rule (follow-up FU4)

The gate and the monitor count as foreign every process of another non-root user whose working directory the P309
user cannot read. That includes service accounts and other login sessions. Under OD-R2-5 option (i), such a process
can end a run. Before every heavy window (the 8d drill, the official run, a host re-run):
1. **Run everything as the P309 user.** Every process the P309 session starts during a window runs as the P309 user,
   whose own processes are never classified. That includes shells, editors and `journalctl`. Nothing runs under
   another account.
2. **Record the gate as the P309 user.** After 8c, and again shortly before each window, run the `--print-only`
   check of §3 in a fresh check directory, and preserve its record in `evidence/host/`. The record's
   `gate.processes` rows show the uid of every `unattributable` and `foreign` process, with its CPU fraction, and
   nothing else. One sample cannot show work that starts later, so also list, read-only, what is scheduled
   (follow-up W8):
   * `systemctl list-timers --all --no-pager`, then, for each timer's service, the account it runs under:
     `systemctl show -p User,DynamicUser <service>`;
   * `cat /etc/crontab /etc/cron.d/*` (read-only): the sixth field of each job line names its account;
     `ls -l /etc/cron.hourly /etc/cron.daily` (these run as root).

   Per-user crontabs (`/var/spool/cron`) are not readable by the P309 user. Ask the host's administrator for the
   non-root accounts that have one (follow-up X7).
3. **Agree the window for the whole host.**
   * Identify each non-root uid in those rows: cell 308's (which belongs in `foreign_uids`), a service account, or
     another user.
   * Identify the timers and cron jobs that would run under a non-root account during the window.
   * Agree the window with every workload they show, not only with the cell-308 operator.
   * Record the agreement in the window's evidence.
4. **Check just before the official launch** (follow-up SF2).
   * Run the `--print-only` check once more, as `--mode official`, in a **separate** fresh check directory, and read
     its record's `gate.processes`:
     * the uids must be the ones agreed in step 3;
     * no unattributable or foreign process may be active.
   * Only then launch the official run, with **another** scratch root that is empty. The check directory is never the
     run's scratch root.

   If either check fails, do not launch. The launcher's own gate refuses an active process anyway.

**Expected:** about 6 h of wall time. QC08, QC09 and QC10 run here; they are skipped on the cloud tier.

**What 8d does and does not show** (follow-up W7). The drill's report must state these points:
* The in-unit refusal controls U01–U03 run here, and only here: an altered configuration file, an altered
  configuration hash, and another boot.
* Two refusal branches are exercised nowhere: the unit-property branch and the instance-id branch. Neither can be
  forced from inside a correct unit.
* Two stop paths remain unexercised: the unit's `KillMode=control-group`/SIGKILL backstop after a runner abort, and
  the drill's own stop on exit status 3. That is because a passing drill never aborts.

## 5. Evidence export (bulk data stays on AWS or GitHub)

The drill writes `evidence/drill/<utc>/`: its ledger rows in full, with sha256, the report, controls and witnesses.
It also writes one GOVERNANCE row in the P309 clone's ledger.

The P309 session then:
* commits those paths only;
* checks the commit is namespace-only (`code/checkpoint_push_p309.py --dry`);
* pushes the r2 branch with `code/checkpoint_push_p309.py`, one explicit refspec and no force.

Nothing large passes through the owner's machine, and decoy outputs are not committed.

## 6. Cleanup (P309-only; never cell 308)

* **The drill root:** the drill deletes its own root by its literal path unless `--keep` was given. A kept root is
  deleted by the P309 user with its literal path, after checking that the path lies under `P309_SCRATCH_ROOT` and is
  named `drill_<utc>`.
* **Units:** `systemctl list-units --all 'p309-r2-*'` (read-only). A failed P309 unit is cleared only with
  `systemctl reset-failed p309-r2-<...>`, exactly that unit, under the consented privilege.
* **Scratch roots:** they are removed only by literal path and only after their evidence is committed.
* **Cell 308:** nothing of cell 308 is ever cleaned, listed recursively or touched.

## 7. What remains owner-gated after 8d

Each of these needs its owner decision first:
* the pre-freeze follow-up review (gate step 9);
* the freeze **on the worker** (step 10: single writer, clocks synchronised, the frozen tree ids equal to those
  reviewed and drilled), after OD-R2-0;
* the single official qualification through `code/p309_launch.py --mode official`;
* QC10's host re-run on an owner-named execution host, only through `code/p309_launch.py --mode host-rerun` (exclusion
  gate and Q-HOST; delta review C7);
* any grant (never part of this package). On a host shared with another campaign, `execute` is not gated by these
  bytes. It may run there only after the reviewed amendment that `governance/P309_R2_AMENDMENTS.md` §C requires.

## 8. The launch record (`<P309_SCRATCH_ROOT>/launch_<utc>.json`, schema `P309_R2_LAUNCH/2`)

**How it is written.** The launcher writes it exclusively (`open(..., "x")`): one record per launch, never
overwritten. It is written before any unit starts, and also when the launch is blocked. It is **redacted** (delta
review C9): foreign roots, `foreign_patterns` and `foreign_heavy_patterns` appear only as sha256.

| field | content |
|---|---|
| `schema`, `utc`, `mode` | `P309_R2_LAUNCH/2`; the write time; `drill`, `official` or `host-rerun` |
| `unit` | `p309-r2-drill-<utc>`, `p309-r2-qualify-<utc>` or `p309-r2-hostrerun-<utc>`; the mode fixes the name |
| `host_config` | the validated configuration as the launcher used it (`p309_repo` and `require_empty_scratch` set by the launcher), redacted |
| `host_config_sha256` | the sha256 of that configuration before redaction (canonical JSON) |
| `host_config_file`, `host_config_file_sha256` | the configuration file's path and the sha256 of its bytes |
| `launch_settings` | the six unit settings (`unit_user`, `unit_group`, `memory_max`, `oom_score_adjust`, `cpu_weight`, `io_weight`) |
| `scratch_root` | the validated `P309_SCRATCH_ROOT`; it must be empty for `official` and `host-rerun` |
| `preflight` | the full `durability_preflight` document, including `provenance`, the Q-HOST launch baseline |
| `gate` | the full `exclusion_gate` document (60 s sample; processes as pid, uid, tag, CPU fraction and cmdline sha256 only) |
| `isolation` | the full `isolation` document (foreign roots as a stat hash, world-readability and readability only) |
| `p309_units_loaded` | the loaded `p309-r2-*` units; must be `[]`; `null` if `systemctl` is absent or failed |
| `argv` | the `systemd-run` argv with every property and environment variable, foreign roots redacted |
| `blockers` | the failed sections; empty means the unit was started |

**How the runner uses it.** The runner's Q-HOST preflight reads this record through `P309_LAUNCH_RECORD`. Before any
attempt directory or start line exists, it refuses unless all of these hold:
* the record and the run's scratch root lie under `scratch_root`;
* `blockers` is empty, and `mode` is the one the invocation needs (`official` or `drill` for the run, `host-rerun`
  for the host re-run);
* `mode` fits the repository;
* the process runs in `unit`, and six of that unit's effective properties are the launcher's: Restart, KillMode,
  KillSignal, NoNewPrivileges, PrivateTmp and ProtectSystem. The others (MemoryMax, OOMScoreAdjust, CPUWeight,
  IOWeight, SendSIGKILL, TimeoutStopSec, InaccessiblePaths) are set by the launcher's command and recorded in
  `UNIT_PROPERTIES.json`, but not checked (follow-up FU1 (a));
* the file named by `P309_HOST_CONFIG` has `host_config_file_sha256`, and gives `host_config_sha256`;
* the instance id, if the launch read one, is read again;
* continuity holds against `preflight.provenance`.

**Evidence.**
* The official run and the host re-run copy the record into their attempt (`LAUNCH_RECORD.json`), together with the
  unit's effective properties (`UNIT_PROPERTIES.json`). Their sha256 values are in `QHOST_BASELINE.json`.
* The worker-tier drill embeds the record and the unit properties in `DRILL_REPORT.json`.
* The record is never edited.
