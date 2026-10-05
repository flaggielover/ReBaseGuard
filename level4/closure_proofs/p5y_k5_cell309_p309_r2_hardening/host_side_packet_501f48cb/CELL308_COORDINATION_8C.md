# 8c: Cell-308 operator and process-window coordination (deliverable 5 of 10)

**Naming.** In r2's own text, step 8c is the **bootstrap** of the consented items (`R2_BOOTSTRAP.md`; addendum 2,
F8). The bootstrap's host changes are handled in `OD_R2_4_HOST_CHANGE_PACKET.md`. In this packet, **8c** names the
coordination with the cell-308 operator that the bootstrap and every heavy window depend on. Nothing here changes the
host or cell 308.

**What r2 knows about cell 308.** r2 holds **no** cell-308 process data. Every value below is therefore blank here,
to be supplied by the cell-308 operator (and, for other workloads on the host, by their owners or the host
administrator). It is never inferred from P309's own observations. The 8a audit's rows (uid, CPU fraction, command
sha256) only help the operator identify their processes.

**What r2 fixes, and how P309 behaves toward cell 308.**
- **Shared host, exclusive heavy compute** (message 3).
- If cell 308 needs the host, P309 waits. P309 never interrupts, signals, pauses, renices or alters cell 308's
  processes, checkout, refs, evidence or governance (message 3 items 6 and 8; SI §0).

## 1. What must not overlap

| P309 activity | what cell 308 must not do during it | basis |
|---|---|---|
| the 8d drill unit `p309-r2-drill-<utc>`, from launch to unit exit (about 6 h; a 9 h window, 12 h recommended) | start any heavy job; any one cell-308 or unattributable process above 0.5 core, or matching a heavy pattern; or all foreign and unattributable processes together above 1.0 core | message 3 §3 (second bullet); OD-R2-5 (i). Q-HOST ends the run |
| the start of that window (the exclusion gate's 60 s sample) | any process above 0.05 core, or matching a heavy pattern, or newly started during the sample; a load above `load_baseline + 0.5` | message 3 §4; gate thresholds |
| the A-02d `--print-only` checks (about 2 min each) | the same as the start of a window, for that moment only | SI §3, X7 |
| building the interpreter (M5), about 10–30 min with `-j2` | nothing is required, but the operator agrees the time, since it is CPU work on their host | message 3 §3 (first bullet, reversed) |
| any reboot or upgrade hold (M4, X-1) | the operator agrees the timing; holds are host-wide | OD-R2-4 |

**Whole-host rule.** Under the unattributable rule (`R2_HOST_REQUIREMENTS.md` §6; SI §4.1, FU4), a process of **any**
other non-root user whose working directory the P309 user cannot read counts as foreign. So service accounts, other
login sessions and timers of other accounts must also be quiet for the window. The window is agreed with every such
workload, not only with cell 308 (Part C).

**P309's heavy processes,** which the cell-308 side may want to recognise:
- by uid, `<P309_USER>`;
- by unit name, `p309-r2-*`;
- by r2's own pattern `p309_qualify\.py|p309_driver\.py\s+(_job|decoy)|p309_topology_drill\.py|p309-r2-(drill|qualify|hostrerun)`
  (`p309_host.HEAVY_P309`).

## 2. Directories

| P309 directory | rule |
|---|---|
| `<CLONE>`, `<SCRATCH_BASE>`, `<P309_HOME>` | never overlap any cell-308 root (`p309_roots_disjoint_from_foreign_roots`; `scratch_root`) |
| the unit's `TMPDIR` | `<scratch>/tmp`, and `PrivateTmp=yes`. P309 uses no shared `/tmp` |
| cell 308's checkout(s) | `InaccessiblePaths=` in every P309 unit. The P309 user must not be able to read them (R-ISO-4). Their paths appear in records only as sha256 |
| cell 308's scratch, temporary and evidence directories | needed only to prove disjointness. They are listed in Part A, and also become `foreign_roots` if the operator wants them inaccessible to P309 units |

## 3. CPU, RAM and IO contention limits (the values P309 enforces on itself, or measures)

| quantity | value | where |
|---|---|---|
| P309 CPU share | `CPUWeight=20` (proposed U-3); 4 runner workers | launcher; OD-R2-4 U-3 |
| P309 IO share | `IOWeight=20` (proposed U-4) | U-4 |
| P309 memory ceiling | `MemoryMax=<agreed U-1>`, leaving cell 308 its working memory (Part B) | U-1 |
| OOM preference | `OOMScoreAdjust=500`: P309 dies first | U-2 |
| foreign activity allowed at the start | ≤ 0.05 core per process; load ≤ baseline + 0.5 | `heavy_cpu_fraction`, `load_margin` |
| foreign activity allowed during the run | ≤ 0.5 core per process; ≤ 1.0 core together; no heavy pattern | `monitor_*` (OD-R2-5 (i)) |
| P309 disk use | the drill clone (about 0.5 GB per clone, HP §1), scratch mirrors (about 1 GB, HP §1) and the attempt's outputs (HP §1: about 3–4 MB for a full attempt with decoy outputs), on the P309 volume. If that is the same filesystem as cell 308's, agree the space (M2) | HP §1 |

## 4. Ports, services and other resources

| resource | P309 use | collision check |
|---|---|---|
| network ports | none opened | — |
| systemd units | only transient `p309-r2-*` | cell 308 must use no unit named `p309-r2-*` (the launcher refuses while one is loaded) |
| IMDS | about six requests per Q-HOST sample (a token, then instance-id, instance-type, life cycle, scheduled maintenance and spot action; 1 s timeouts), one sample per ≤ 60 s, plus the launch's and the runner's own reads | the operator says whether cell 308 relies on IMDS in a way a low request rate could disturb (Part B) |
| GitHub | P309's fetch and push before and after a window, with a P309-only credential | separate credentials; no shared clone, ref or object store |
| journald | the unit's output goes to the journal | journal size limits are the host administrator's (Part B) |
| `/dev/shm` | Python multiprocessing semaphores, with unique names | none expected |
| reboot and upgrade holds (M4) | host-wide during windows | operator consent (Part B) |

## 5. Evidence required from the cell-308 side

1. The completed Parts A, B and C below, each with the operator's name or role, the UTC, and the statement that the
   data is accurate. Committed by the coordinator as `host_evidence/CELL308_FORM_<part>_<UTC>.md` in this hardening
   namespace, with foreign paths and patterns as sha256 if the operator asks (SI's C9 redaction applies to P309's
   records in any case).
2. The window agreement (Part C): the exact UTC start and end, and the confirmation that no cell-308 heavy job is
   scheduled in it.
3. After the window (Part D): the confirmation that no cell-308 heavy job was started in it, or the exact time one was.
   This is compared with Q-HOST's evidence in the drill report.

The pre-freeze review (`PRE_FREEZE_REVIEW_PACKET.md`, Q6) checks the windows against these forms, the gate record in
the launch record, and the drill's Q-HOST result.

## 6. The fill-in form for the cell-308 operator

```text
CELL-308 OPERATOR FORM for P309-r2 host work (r2 501f48cb)            form version 1

PART A  (needed before the 8a audit)
A1  Cell-308 checkout path(s) on the host (absolute; characters [A-Za-z0-9._/+@,=~-] only):
    ______________________________________________
A2  Cell-308 scratch / temporary / evidence directories (absolute):
    ______________________________________________
A3  Command-line patterns (Python regular expressions) that identify cell-308 HEAVY jobs:
    ______________________________________________
A4  Command-line patterns for ANY cell-308 process (if different from A3; default used by P309: cell[_-]?308):
    ______________________________________________
A5  Is it acceptable that the read-only audit (5 s process sample; stat() of A1's top directories only)
    runs at: ____ UTC ?   yes / no / other time: ______

PART B  (needed before OD-R2-4 is decided and before 8b-final)
B1  Unix uid(s) under which cell-308 processes run (foreign_uids):  ______
    Does any cell-308 process run as root (uid 0)?  yes / no
    (if yes: uid 0 is listed, and every root process then counts as foreign for P309)
B2  Cell-308 working memory that must remain available while P309 runs (GB): ______
    -> agreed P309 MemoryMax (U-1): ______   agreed: yes / no
B3  Idle load of the host, measured together (1-min / 5-min), and when measured (UTC): ______ / ______  at ______
B4  Normal cell-308 heavy-job schedule (days, UTC hours, typical duration), and how a heavy start is announced:
    ______________________________________________
B5  Cell-308 timers / cron jobs / services that could run during a P309 window (account, schedule):
    ______________________________________________
B6  Other non-root workloads or accounts on the host (service accounts, other users, per-user crontabs),
    and who answers for them:
    ______________________________________________
B7  Consent to the host-wide holds during each P309 window (OD-R2-4 M4): automatic upgrades and reboots
    held for the window, restored after it:   consent / decline
B8  Consent, if the 8b rows fired, to: X-1 reboot __ ; X-2 time sync __ ; X-3 hostname/machine-id __ ;
    X-4 /proc hidepid __ ; X-5 git package __ ; X-6 polkit / systemd-run packages __ ;
    X-7 interpreter build dependencies __ ; X-8 cgroup controllers __ ; the M2 disk space on a shared filesystem __
B9  Does cell 308 rely on IMDS, on unit names beginning with p309-r2-, or on the journal size, in a way P309
    could disturb?  ______
B10 Contact path during a window (for an emergency on cell 308's side): ______

PART C  (per window; needed before every launch, including the 8d drill)
C1  Window start (UTC): ______   end (UTC): ______   (>= 9 h; 12 h recommended)
C2  No cell-308 heavy job is scheduled in the window; none will be started in it:   confirmed / not confirmed
C3  The other workloads of B5/B6 are quiet in the window (each named, each confirmed by its owner):
    ______________________________________________
C4  QC-D5 margin: the window leaves at least 2.75 h of guaranteed host time after QC-D5 can start
    (no maintenance, reboot or co-tenant start before the window ends):   confirmed / not confirmed
C5  Operator name/role, UTC: ______

PART D  (after each window)
D1  Was any cell-308 heavy job started during the window?  no / yes at ______ UTC
D2  Any other event on the host during the window known to the operator (maintenance, reboot, login, job):
    ______________________________________________
D3  Operator name/role, UTC: ______
```

**Rules for the form:**
- An unanswered field is never filled by P309.
- A Part C that is not fully confirmed means the window does not open (`WORKER_TIER_DRILL_8D.md` §1).
- A changed answer after a window has been agreed means that window is cancelled and re-agreed.
