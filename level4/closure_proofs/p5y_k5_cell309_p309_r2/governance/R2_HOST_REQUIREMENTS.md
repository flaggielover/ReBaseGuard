# P309-r2 compute host: requirements and the verdict rule

This document is provider-independent. It names no address and no credential.

**Its basis:**
* the plan (`R2_PLAN.md` §6–§8);
* addenda 1 and 2;
* review conditions P9–P15, P20–P22 and F7–F8, and the delta review's C2–C9, C14 (`REVIEW_R2_DELTA.md`);
* the owner's messages 1 and 3 (`OWNER_INSTRUCTIONS_R2_VERBATIM.md`).

**The host it describes.** The host is the shared AWS ReBaseGuard worker that cell 308 uses (owner message 3). The
model is **shared host, exclusive heavy compute**:
* cell 308 is never altered, interrupted or slowed by P309;
* P309 runs heavy work only when the exclusion gate passes.

## 1. Measured workload (r1, 2026-09-30, cloud container, 4 workers)

| item | wall | notes |
|---|---|---|
| QC08 (decoy Stage 1a) | 4 310 s | 15 461 CPU-s on 4 workers |
| QC09 | 9 769 s | |
| QC10 (decoy, byte-identity with QC08) | 3 864 s | |
| QC01–QC_U2 in total | 5.47 h | |
| a complete single attempt, including QC_D5 | about 5.7–5.9 h | |
| peak RAM with 4 jobs | under 1 GB used | about 15 GB of 16 GB stayed available |
| repository `.git` | 483 MB | |

## 2. Minimum host (each item is a check in `code/p309_host.py`)

| requirement | value | check |
|---|---|---|
| CPU | **≥ 4 dedicated x86_64 vCPU**; no burstable type (t2/t3/t3a/t4g) | `enough_cpus`, `not_burstable` |
| RAM available | **≥ 8 GB** at the gate (16 GB recommended) | `ram_available` |
| disk free on every P309 root | **≥ 40 GB** | `disk_available` |
| OS | Linux with systemd as PID 1; not a container | `pid1_is_systemd`, `not_in_container`, `systemd_run_available` |
| interpreter | **CPython 3.11.15 exactly**, P309-private, path pinned | `python_exact`, `interpreter_pinned` |
| glibc | pinned to the value recorded at the audit | `glibc_pinned` |
| runtime binding | the freeze manifest pins the python version, glibc and the interpreter binary's sha256; the driver refuses any difference (delta review C14) | `check_bindings` (driver) |
| launch privilege | a polkit rule for the P309 user's `p309-r2-*` transient system units (the code never uses sudo) | the launcher's start |
| unit stop | `KillSignal=SIGKILL`, `SendSIGKILL=yes`, `TimeoutStopSec=10s` (the heavy jobs ignore SIGTERM; C5) | the runner's `qhost_preflight` (`systemctl show`) |
| git | ≥ 2.32 | audit `tools.git` |
| durability | no automatic reboot; upgrades held; no pending reboot | `no_automatic_reboot`, `upgrades_held`, `no_pending_reboot` |
| cloud | instance metadata readable; no scheduled maintenance; not spot | `cloud_metadata_available`, `no_scheduled_maintenance`, `not_spot` |
| clock | NTP synchronised | `ntp_synchronized` |
| identity | machine-id present; static hostname equals the running one | `machine_id_present`, `hostname_static` |
| scratch | `P309_SCRATCH_ROOT` valid, and empty for the official run | `scratch_root_valid` |

## 3. Windows needed (exclusive heavy compute; cell 308 idle)

| run | expected wall | window to agree |
|---|---|---|
| worker-tier topology drill (P14; runs the full runner, QC08–QC10 included) | about 6 h | **about 9 h** |
| the single official r2 qualification | about 5.9 h | **about 9 h** |
| the eventual target execution, if OD-R2-6 names this host | up to about 31.5 h (A6 bounds) | owner decision |

**Choosing a window.** Each window must begin with cell 308 idle, as the exclusion gate shows. **If cell 308 needs the
host, P309 waits; it never interrupts it** (owner message 3, item 8).

**If cell 308 starts heavy work during a P309 run:**
* **Option (i)** (OD-R2-5) applies by default: Q-HOST records FAIL and the single attempt ends (P23).
* **Option (ii)** would need the owner to amend message 3 §3.

## 4. Verdict rule

**HOST_SUITABLE** requires all of these:
* the step-8a audit shows every §2 requirement met, or met by a bootstrap step the owner and the cell-308 operator
  consented to (OD-R2-4);
* the isolation check passes after bootstrap;
* the worker-tier drill (P14) passes, with QC08's byte identity and QC10.

**HOST_NOT_SUITABLE** applies when any §2 item cannot be met without an unconsented change to the shared host.

**HOST_SUITABILITY_PENDING** applies otherwise. It is the state until step 8a has run.

## 5. Isolation on the shared host (owner message 3, items 2, 5 and 6; P9, P12; addendum 2, F7)

**Separation:**
* a separate Unix user for P309 with **no group membership** that grants access to cell 308's checkout;
* a single-branch full clone of `claude/p5y-k5-cell309-p309-r2` in that user's home;
* a P309-only credential that is not stored in the repository configuration.

**Cell 308's checkout is never altered.** The P309 unit marks it `InaccessiblePaths=`. The isolation check confirms it
is unreadable to the P309 user with a top-directory `stat()`/`access()` only; it never runs git there.

**Nothing is shared:** no shared object store, alternates, worktree, ref, temporary directory or evidence directory.
The isolation check (`code/p309_host.py isolation`) proves this for each run.

**Data movement:** bulk data stays on the worker and GitHub. The owner's own machine is never a relay.

**A world-readable checkout.** The isolation check runs as the P309 user outside the unit. If cell 308's checkout is
world-readable (the 8a audit records this as a boolean), `foreign_roots_unreadable` fails. Proceeding would then need
an owner amendment of message 3 §6, with the cell-308 operator's consent (OD-R2-4).

## 6. Seeing cell 308 from a separate user (P9; delta review C2, A8)

**The limit.** A separate P309 user cannot read another user's process working directory. So a cell-308 process is
recognised only by one of these:
* **its uid:** `foreign_uids`. It is required: the gate fails while it is empty or holds the P309 user's uid;
* **its command line:** `foreign_patterns` and `foreign_heavy_patterns`;
* **as unattributable:** a process of another non-root user whose working directory cannot be read. It counts as
  foreign.

If cell 308 runs as root, uid 0 must be listed, and then every root process counts as foreign. Kernel threads never
count.

**What fails, and when:**

| | the start (exclusion gate) | during a run (Q-HOST monitor) |
|---|---|---|
| one foreign or unattributable process | blocks above 0.05 of a core, on a heavy pattern, or if it appeared during the 60 s sample | fails above 0.5 of a core, or on a heavy pattern; a newly seen process is judged one sample later |
| all of them together | the load must be at most baseline + 0.5 | fails above 1.0 core |
| the monitor itself | — | fails if it is dead at the stop, or any gap exceeds 60 s + 30 s |
| the host | the durability preflight | fails on any continuity break (boot, machine-id, hostname, instance, interpreter, glibc, suspend); a final sample is taken at the stop |

**Termination.** On a monitor failure, the runner SIGKILLs its own process tree at once and records Q-HOST FAIL. The
unit's SIGKILL stop handles anything left. Detection takes up to about one interval, or two for a newly started
process.

**Records.** Foreign roots and the cell-308 patterns appear in every P309 record only as sha256: the launch record,
the attempt's copy of it, and the unit properties (C9).

