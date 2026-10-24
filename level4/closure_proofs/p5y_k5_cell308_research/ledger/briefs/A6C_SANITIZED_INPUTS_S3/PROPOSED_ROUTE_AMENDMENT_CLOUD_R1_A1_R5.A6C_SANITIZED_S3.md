# PROPOSED route amendment A1, revision r5 — Cell-308 MB-S new-host route (S4 changed branch): Linux platform contract

> **Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** Revision r5 of the draft. Earlier drafts are kept byte-unchanged:
> r1 (reviewed by review 59: NEEDS_REVISION), r2 (delta review 60: FIT_WITH_CONDITIONS), r3 (delta review 61:
> FIT_WITH_CONDITIONS) and r4 (delta review 62: FIT_WITH_CONDITIONS). r5 meets review 62's condition E2
> (`reviews/REVIEW_CLOUD_R1_DELTA_R4.md` §6): rows L-UPD, L-EXCL, L-PIN, L-LIFE and H6 state exactly what revision 5
> does, and the acceptance mechanism's independence is an explicit carried item of D-HOST-LIFETIME. Disposition: §10
> (review 59), §11 (review 60), §12 (review 61), §13 (review 62). It amends nothing until (1) an independent route / governance
> review accepts it, (2) the owner decides the points marked **[OPEN]**, and (3) a fresh S12 incident-independence
> reviewer rates the route. The coordinator's preparation is not an independent review.
>
> `new_target_evaluations = 0` · `cell309_activity = none` · no designation, qualification, freeze, grant or target
> step is authorized by or performed for this document.

## 0. Labels

| label | meaning |
|---|---|
| **[ACCEPTED]** | text of an accepted source, quoted verbatim with its path. Binding today. Never weakened here. |
| **[PREPARATION]** | `ROUTE_PREPARATION.md`: a coordinator preparation instruction (status "PREPARATION_ONLY — HOST_UNVERIFIED — ROUTE_REVIEW_PENDING"), **not** an independently accepted text (F18). Its content is restrictive and is followed, but it is not cited as accepted. |
| **[PROPOSED]** | a new requirement or a Linux replacement that a reviewer is asked to accept. Not binding. |
| **[OPEN]** | a rule-semantics or host decision this document refuses to make. Until decided, every dependent gate is `OPEN_DECISION` (never passes). §4 says for each option whether it **amends an accepted text or introduces a new number**. |
| **[OBSERVED]** | a fact recorded in this session's evidence (`CLOUD_FEASIBILITY_R2.md` with its erratum E1, the r2 / r2b inventories, the provider-fact notes with erratum E1). |

No threshold, number, rule output or scientific input is changed by this document.

## 1. What stays, what is proposed to change

**Unchanged [ACCEPTED]** — no change to any of them is proposed:

* the science and its byte identity (governance A1 **S11**); Theorem MB r1, the cover, D1–D14, the criterion (d1
  §5.4), the members;
* WORKERS 5, the floors, k, every number of R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW (`CONSTANTS_RATIFICATION_MBS308.md`,
  "Written rules"), the caps (`EVAL_CAP_S`, `DECOY_CAP_S`, rung CPU caps), the resume budget (3), the 7-day deadline;
* exactly-once (**S7**), the S1 ruling requirement, S14–S17, the quarantine (**S9**), Cell-309 isolation (**S10**);
* **MBS-5(b)** [ACCEPTED] (brief R2 §4 item 5, route E2): "any evaluation of cell 308 after the MB-S marker, of any
  route, starts at a risk rating not lower than HIGH";
* the MB-S r1 record: designated evidence `86d3f8cb…`, derivation `8a4e7984…`, `NOT_DERIVED` / R-FREE
  `GATE_UNATTAINABLE`, the three INVALID series, `ALREADY_DESIGNATED`. The old designated series is never deleted,
  replaced or measured again;
* MB r1's INDETERMINATE outcome, consumed marker `afa93072`, status "not scientifically negative".

**Not a replacement series.** A designated series on a new host, if ever made, belongs to a separately governed S4
changed-branch campaign with its own namespace, refs and prospective designation policy. It is **not** a "replacement
series" or "best-of-N" in the sense of the R-FREE stop brief §4 item 2 for MB-S r1, whose designated series and stop
stay final.

**Proposed change [PROPOSED]:** the platform (macOS build 25F84 / arm64 / CPython 3.14.5 framework build, as recorded
in brief R2 §9 → a Linux host) and the host infrastructure only. This is S4's **changed branch**:

> [ACCEPTED] `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md`, HOST row: "moving the successor to another host |
> **EXCLUDED unless RC2 is discharged there** | the determinism argument binds the platform. A different host means
> the S4 changed branch, and its own exact reproduction of MB r1's r3 records would be required"

## 2. Host scope [PROPOSED]

### 2.1 The Anthropic-hosted Cloud session environment

Target-free development, synthetic tests, static analysis and reviews only. Basis: `CLOUD_FEASIBILITY_R2.md` with
erratum E1 — **HOST_UNSUITABLE for the official stages, confirmed by review 59**. Primary reason:

> [ACCEPTED] route erratum E1, DR2: "The host's automatic OS and software updates must be disabled for that window.
> This is an operator action by the user; the campaign never changes system settings."

The owner cannot perform that action on a provider-managed image, and the image was observed to change between
sessions (libc6 `8.7` → `8.9`, kernel build, OS point release, interpreters; even `python3.12` 3.12.3 has a different
executable digest).

### 2.2 Requirements on the official host (H1–H8)

Each is a **fact established on the actual machine** by a Phase-1 inventory plus a committed owner attestation that an
independent reviewer accepts; an unknown is a failure.

| id | requirement | basis | how established |
|---|---|---|---|
| H1 | not paused, reclaimed or replaced while idle or running, from the designated series to the 7-day deadline | one host across designation, qualification, execution (brief R2 §9 host row; [PREPARATION] step 7) | attestation + inventory; gate `host_lifetime_attested` |
| H2 | systemd is PID 1; the campaign runs as a service outside any agent session | S6 ("a launcher that survives the hosting app's death and the launcher's parent's death") | gate `launched_by_systemd` (L-LAUNCH) |
| H3 | **every** update vector disabled by the owner from qualification to the deadline: apt periodic / unattended-upgrades (incl. `Automatic-Reboot`), apt-daily-upgrade timer, snapd refresh, cloud-init package upgrades, kernel livepatch, and any provider image change | route E1 DR2 (the no-update rule; an operator action by the user); brief R2 §9 "Platform unchanged" | `auto_update_settings` positive evidence + attestation token `ATTESTED_NO_IMAGE_OR_OS_CHANGE`; pins (L-PIN) at every step |
| H4 | exclusivity can be arranged (no other heavy compute, including other sessions) | S17 | gate `host_exclusive` (D-EXCL-WINDOW, D-ALLOW-PATHS, D-ALLOW-BASE39) |
| H5 | local disk honours fsync; the store survives a reboot of the same machine | S6 durable persistence | attestation of the storage; durable-write tests on the machine |
| H6 | the effective memory allowance is fixed and readable; **no cgroup ancestor is hidden** (a reader cannot see ancestors above a cgroup-namespace root, so this is attested, not read) | R-MEM step 5, R-FREE (whatever D-MEM-* decides) | the verified attestation's field `root_cgroup_is_real: true`, read by `root_attestation()` inside `memory_readings` together with an initial cgroup namespace and D-HOST-LIFETIME decided (no caller flag exists); without it the reader gives only `visible_limit_upper_bound` |
| H7 | the operator can reach the machine to launch `resume` / `recover` | MBS-3; brief R2 §7 item 8 ("launched by the operator") | owner statement |
| H8 | the same physical / virtual machine for every official step: hardware-bound identity (DMI `product_uuid`, hashed) or an owner attestation; `/etc/machine-id` alone is **not** an identity on image-cloned VMs | as H1 | `machine_identity()` recorded at every step; attestation binds it |

## 3. Linux platform contract [PROPOSED]

Development implementation: `streams/CLOUD_R1_LINUX_DEV/lx_platform.py` revision 5 (DEV_ONLY); tests
`tests/test_lx_platform.py`; mutation harness `tests/run_mutants.py` (113 mutants: M01–M32 coordinator; R01–R10,
X01–X09, Y01–Y09 and Z01–Z11 from reviews 59, 60, 61 and 62; N01–N14, P01–P15 and Q01–Q13 weakening the revision-3, -4
and -5 repairs); the recorded counts are in `results/`.

**Citation status** (review 62 condition E1, which replaces D1):
* Revision 4 (sha256 `90362161…`) may be referenced as the DEV_ONLY implementation of:
  * L-ID (with Z11 open), L-BOOT and L-POWER;
  * L-SLEEP (L′ hard-wired AMBIGUOUS);
  * L-LAUNCH;
  * L-FREE, as a reader whose number is gated by `root_attestation`;
  * L-DISK and L-FSYNC;
  * L-EXCL as a reader, **only** when called with `view_complete=proc_view_complete()`.
* Neither revision 4 nor revision 5 is cited for L-LIFE, L-UPD or the L-PIN pin point.
* Revision 5's repairs (L-LIFE, L-UPD, L-PIN, L-EXCL, and Z11 in L-ID) are cited only after a fresh delta review of
  revision 5 confirms them.
* r4's preamble cited revision 3 for L-PIN without review 61 D1's qualifier "with P4 / Y06 and P11 open". That
  qualifier applied (§13, G10).

Port map: `results/PORT_MAP_142D97A9.json`.

**Caller inputs (review 62 G5, G11).**
* `preflight` takes every host reading itself: power, free disk, boot id, update settings, a fresh launch reading, and
  the attestation read from committed files. Its caller inputs are only:
  * `mode`;
  * `other_job_running`, from the reviewed launcher's pidfile check, as in the candidate;
  * `launched`, which is only compared with a fresh reading;
  * `attestation_ref`, which is only a pointer to committed files.
* `busy_processes` reads the /proc view itself. Its snapshots `t0` / `t1` and the campaign set `own` come from the
  caller, and a reviewed caller takes them with `cpu_ticks()`.
* Some readers still take parameters for the tests: texts or roots in `proc_view_complete`, `memory_readings`,
  `power_source`, `auto_update_settings` and `unit_enabled`. **[PROPOSED] requirement:** a reviewed caller never passes
  them. `preflight` passes none. Checking this is an implementation-review item.
* `OPEN_DECISIONS` holds exactly §4's 21 ids, so `DECIDED` can hold any of them. `host_exclusive` maps to D-EXCL-WINDOW,
  D-ALLOW-PATHS and D-ALLOW-BASE39.

| row | macOS mechanism (accepted, candidate `142d97a9`) | Linux replacement (proposed) | fail-closed behaviour | status |
|---|---|---|---|---|
| L-LAUNCH | launchd job; `launched_by_launchd` | systemd service `rebaseguard-mbs308-*.service`; `launched_by_systemd`: systemd PID 1, own cgroup is that unit (`.service`, never `.scope`), `INVOCATION_ID` == `systemctl show` InvocationID, MainPID (an `int`) == pid. In `preflight`, the launch gate (always for `execute` / `resume`; for `launcher_preflight` only if a record is passed) takes a **fresh** `launched_by_systemd()` reading inside `preflight`; PASS only if that reading verifies field by field (`launch_record_ok`) **and** any passed record equals it — a caller-built record never passes on its own | any failed reading ⇒ FAIL | PROPOSED; the accepted texts that name launchd need textual amendment (**[OPEN] D-TEXT-LAUNCHD**) |
| L-DETACH | launchd detachment | systemd service; a `setsid` grandchild is **not** a launcher (survives its parent, not the host) | — | PROPOSED |
| L-ID | (pid, `ps lstart` UTC, boot UUID, `ps command` sha256); R2 / N-2; O-4: an unreadable argv (zombie) is a failed reading ⇒ UNKNOWN | (pid, `/proc/<pid>/stat` starttime, `boot_id`, `/proc/<pid>/cmdline` sha256, **recorder's PID and time namespace inodes**); same tri-state; **a malformed record** (pid not a positive int, a boot id not matching the reader's format, a negative inode, a non-hex digest) ⇒ UNKNOWN; **a zombie (Z/X) is UNKNOWN**, never DEAD (L-ID-1 of r1 withdrawn); an unrecorded or mismatching namespace ⇒ UNKNOWN for every pid-based reading (only a boot-id change stays DEAD) | DEAD only on positive evidence (reboot; or, with both namespaces recorded and matching, ESRCH or a recorded starttime / cmdline that differs) | PROPOSED (mechanical); any further death evidence is **[OPEN] D-ID-ZOMBIE** |
| L-BOOT | `kern.bootsessionuuid` | `boot_id` | malformed ⇒ None | PROPOSED; a VM pause need not change it (D-PAUSE) |
| L-SLEEP | channels K, S, L | K′ (BOOTTIME − MONOTONIC), S′ (`suspend_stats`), L′ (journal suspend entries), plus **P** (REALTIME − MONOTONIC ⇒ AMBIGUOUS only; not a pause detector) and a boot-id change ⇒ CONTAMINATED; power at every reading; `SLEEP_GAP_TOL_NS` and `MAX_SAMPLE_GAP_S` pinned by a test to the candidate's values. **No reviewed journal reader exists, so L′ is AMBIGUOUS whatever the caller passes** (`JOURNAL_READER_REVIEWED = False`) and no interval can be CLEAN until one is reviewed | CLEAN only if every channel exists and none fires | PROPOSED; **[OPEN] D-PAUSE**; a journal reader is a future reviewed item |
| L-AWAKE | `AwakeCap` on `CLOCK_UPTIME_RAW` (absent on Linux) | `CLOCK_MONOTONIC` | — | **[OPEN] D-PAUSE** |
| L-POWER | `pmset -g batt` = "AC Power" | Mains online, no Battery / UPS discharging, every supply readable and of a known type ⇒ AC; no supply ⇒ `ABSENT`; unreadable type, a type other than Mains, Battery, UPS (USB-C, wireless), or a Battery / UPS status other than `Discharging`, `Charging`, `Full`, `Not charging` (e.g. the kernel's `Unknown`) ⇒ None | `ABSENT` ⇒ `OPEN_DECISION`; None ⇒ UNKNOWN | **[OPEN] D-POWER-ABSENT** |
| L-THERMAL | thermal-pressure level 0 | raw zones and trip points only | `OPEN_DECISION` | **[OPEN] D-THERMAL** |
| L-LPM | `pmset lowpowermode` 0 | none chosen | `OPEN_DECISION` | **[OPEN] D-LPM** |
| L-LID | `ioreg AppleClamshellState` (host-readiness checklist, `mbs308_qualify.py` lines 338–341) | none chosen (servers have no lid; laptops expose `/proc/acpi/button/lid/*/state` on some hardware) | not part of the gate set | **[OPEN] D-LID** |
| L-MEMP | `kern.memorystatus_vm_pressure_level` == 1 | raw PSI only | `OPEN_DECISION` | **[OPEN] D-MEM-PRESSURE** |
| L-FREE | R-FREE's `free_memory_bytes` = vm_stat free + inactive + speculative + purgeable | raw MemAvailable, MemFree, Inactive(file), cgroup chain (v1 limit / usage; v2 min(memory.max, memory.high) / memory.current); `effective_limit` and `cgroup_min_headroom` numeric **only** if every level is readable **and** `root_attestation()` holds, which is computed **inside** `memory_readings` (no caller flag exists): the reader's cgroup namespace is the **initial** one (a non-initial or unreadable namespace blocks a number whatever any record says), D-HOST-LIFETIME is decided, and the verified attestation states `root_cgroup_is_real: true`; otherwise `visible_limit_upper_bound` only; raw cpu.max / cpuset / pids.max along the whole chain | no R-FREE value; a partial chain never yields a number | **[OPEN] D-MEM-FREE** |
| L-WIRED | R-MEM step 5: `hw.memsize − W_idle` | none chosen | `OPEN_DECISION` | **[OPEN] D-MEM-WIRED** |
| L-RSS | watchdog `ps -o rss`; `ru_maxrss` | VmRSS or `ps -o rss` (KiB); `ru_maxrss` is KiB on Linux, **bytes on macOS** | — | PROPOSED; unit handled explicitly (reviewer item) |
| L-EXCL | `ps -o pcpu` (a decaying average on macOS) | per-process ticks over a fixed window, keyed by (pid, starttime); a process born in the window is charged all its ticks; a process that **exits** in the window is reported with unknown usage; a process that exists but cannot be read ⇒ no reading; the campaign tree is a set of (pid, starttime) keys and may not contain pid 0 or 1; the /proc view is read **inside** `busy_processes` by a fresh `proc_view_complete()` (no caller argument, no default): a reader outside the **initial** PID namespace, a `hidepid` / `subset` /proc, no /proc mount line, or an unreadable view ⇒ no reading | no reading ⇒ gate fails | **[OPEN] D-EXCL-WINDOW** |
| L-ALLOW | R-ALLOW (b) SIP prefixes; the base set of 39 macOS names | none: no Linux path or name is auto-allowed (strictest) | busy non-campaign process ⇒ refuse | **[OPEN] D-ALLOW-PATHS**, **D-ALLOW-BASE39** |
| L-UPD | SoftwareUpdate keys; missing key = enabled | `apt-config dump` (apt's own parsing); the units that can install packages (`apt-daily-upgrade.timer`, `unattended-upgrades.service`). **With systemd as PID 1:** enabled if `systemctl is-active` reports active / activating / reloading (a disabled unit can run, pulled in by another unit), or `is-enabled` reports enabled, enabled-runtime, static, indirect, alias, linked or linked-runtime; not enabled if `is-enabled` reports disabled, masked or masked-runtime, or reports not-found **and** no unit file or link for the unit exists in any root of the search path; any other output, a failed query or a not-found with a file present ⇒ unknown. **Without systemd as PID 1:** the 13 roots of the systemd.unit(5) system search path (`UNIT_ROOTS`: `*.control`, `transient`, `generator{.early,,.late}`, `/etc`, `*.attached`, `/run`, `/usr/local/lib`, `/usr/lib`, `/lib`); a missing root is skipped, an unreadable root ⇒ unknown; masked by a `/dev/null` link ⇒ not enabled; an entry for the unit in any `*.wants` / `*.requires` directory, **even a dangling link** ⇒ enabled. Not covered (stated): `Wants=` / `Requires=` written inside another unit's file (not a link), and in file mode a unit started at runtime; `list-dependencies --reverse` is not used. An enabled **or unknown** unit is not "shown disabled"; snapd; cloud-init; livepatch (unreadable ≠ none); `Automatic-Reboot`. The provider-image half is `OPEN_DECISION` while D-HOST-LIFETIME is open, and afterwards PASS only from a verified attestation's token | not shown disabled ⇒ UNKNOWN | PROPOSED (H3) |
| L-SLEEPPREV | `caffeinate -i -m -s` | server: nothing; laptop: `systemd-inhibit --what=sleep:idle` | detection binds | PROPOSED |
| L-FSYNC | fsync + `F_FULLFSYNC`; git `core.fsync` | fsync file, rename, fsync directory (order tested); a stale tmp raises the named state `StaleTmp`, never deleted (the state machine must name its operator action) | read-back verify | PROPOSED; device honouring fsync is H5 |
| L-PIN | `PLATFORM_PINS`: interpreter path + sha256, libpython sha256, `sys.version`, `sw_vers` build, arch | interpreter path + sha256; `sys.version`; sha256 of every shared object mapped into the interpreter at the pin point, which **must** contain `libm.so.6`, `libc.so.6` and the loader; dpkg versions of `libc6` and the interpreter's packages (an unknown owner package never matches); livepatch list; os-release; kernel release; machine; glibc string. The pin point requires every module of the module constant `PIN_POINT_MODULES` to be already imported (no dynamic import); `pin_point()` takes **no parameter** (no caller list can override the constant); the list is **not yet defined** (**[OPEN] D-PIN-POINT**), and `pin_point()` refuses an undefined or empty list. CPU model and vCPU count recorded | an unreadable pin never matches | PROPOSED; see equivalence below |
| L-DISK | `statvfs` ≥ 2 GiB | same | unreadable ⇒ UNKNOWN | PROPOSED (mechanical) |
| L-LIFE | (none on macOS) | `host_lifetime_attested`: **`OPEN_DECISION` while D-HOST-LIFETIME is not in the validated module constant `DECIDED`** (a frozenset of known D-* ids; empty in development; not a `preflight` parameter). Afterwards PASS only if the reference (exactly `path` + `sha256`) names a file committed at HEAD with that sha256, which is JSON with the attestation schema, `reviewed is True`, `accepted is True`, and a machine identity equal to the current one on **both** hashes (hardware-bound); and the acceptance is **found, not named**. **The fixed set:** the files committed at HEAD that are **direct children** of `ACCEPTANCE_REVIEW_DIR` (`reviews/`; no subdirectory, so no reviewer scratch directory) and are named `REVIEW_HOST_ATTESTATION_*.md`. **Accepting:** a file of the set holds the exact line `HOST_ATTESTATION_ACCEPTED sha256=<sha>`, and its only verdict line (case-insensitive `VERDICT:` at line start) is exactly `VERDICT: HOST_ATTESTATION_ACCEPTED`. **Order:** the commit that first introduced the accepting line, searched repository-wide (`git log -S`, so a later move or rename into the set does not reset it), is a strict descendant of the commit that first introduced the attested **blob** (`git log --find-object`, not the path). **Rejection:** any committed file anywhere under `reviews/`, recursively and including scratch, that names the sha and contains a negative word anywhere (reject, withdraw, not accepted, revoke; case-insensitive) refuses. **Stated side effects (fail-closed):** an accepting review cannot contain a negative word anywhere, so it cannot say "no finding was rejected"; a rejection is permanent; in a shallow clone both commits can fall on the boundary commit, so the check refuses and acceptance depends on clone depth. **Not established:** independence. Every commit may come from one coordinator, and commit order is not a reviewer identity | otherwise UNKNOWN | PROPOSED; the acceptance mechanism is a **new rule** under **[OPEN] D-HOST-LIFETIME**, with its independence a carried item (§4) |
| L-S15 | S15: MB r1 marker / emergency-file assertion via host-local paths (`MBR1_GIT_DIR` under `/Users/…`, `os.path.lexists`); qualified-worktree constants | none chosen: on another host the path does not exist, so the check would pass **vacuously** | must not be ported as is | **[OPEN] D-S15-NEWHOST** |

**L-PIN equivalence (for the reviewer).** On macOS any OS update changes `sw_vers -buildVersion`, and libm ships with
the OS, so the build pin covers libm. On Linux no single string does: `libc6` 8.7 and 8.9 both report `glibc 2.39`
and the same os-release VERSION_ID. The proposed set covers libm by **content** (the mapped `libm.so.6` digest) and by
**package version**, and covers kernel-code changes that keep the release string by the livepatch list. Remaining
gaps, stated rather than closed: CPU microcode and model (recorded, not pinned), and modules imported after the pin
point (hence the pin point is fixed after the science imports). Whether this is adequate is a reviewer question.

## 4. Open decisions [OPEN] — none is made here

> [PREPARATION] "The existing R-ALLOW path-class rules and R-FREE memory definition may not transfer to Linux. If
> unchanged semantics cannot be supported, stop and put the exact incompatibility to an independent route reviewer
> and the owner; do not substitute a Linux metric or path policy silently."

| id | question | options seen | **amends which accepted text / new number** | if unresolved |
|---|---|---|---|---|
| D-RC2-SCOPE | which accepted text governs determinism off the old platform (§5) | (a) route A1 §1 "only on the same platform" ⇒ the decisive argument is lost for any platform change; (b) RC2 / N3 exact MBR1_REPRO under new pins may discharge the HOST row | (a) none; (b) **a reading of RC2 that brief R2 §9 says is not settled** | treat as (a): HIGH, decisive argument lost |
| D-MEM-FREE | R-FREE's quantity on Linux | (a) MemAvailable; (b) MemFree + Inactive(file); (c) min over the chain of (limit − usage); (d) min of (a), (c); (e) none ⇒ route stops | (a)–(d) **amend R-FREE** ("measured as the driver's own `free_memory_bytes` (vm_stat …)"); (e) none | no freeze |
| D-MEM-WIRED | R-MEM step 5 under a cgroup limit | limit − idle unreclaimable kernel memory; limit − idle usage; none | both **amend R-MEM step 5** | no freeze |
| D-MEM-PRESSURE | "pressure normal" | PSI `some avg10` = 0 over N readings; v1 pressure events; none | **amends CONSTANTS_RATIFICATION_MBS308 row 24** (`kern.memorystatus_vm_pressure_level` = 1) **and the brief R2 §9 Memory row; new number N** | start gate never passes |
| D-THERMAL | thermal level 0 | no zone at/above a passive trip; undefined without zones | **amends the brief R2 §9 "Thermal pressure level 0" start-gate row; new rule** | never passes on hosts without zones |
| D-LPM | low-power mode off | platform profile / governor | **amends CONSTANTS_RATIFICATION_MBS308 row 25** (lowpowermode 0) **and the brief R2 §9 "Low Power Mode off" row** | never passes |
| D-POWER-ABSENT | AC gate with no Mains supply, or USB-C / UPS supplies, or a peripheral battery reporting `Unknown` | keep (only Mains hosts with recognised statuses); server rule | keep: none; server rule: **amends the AC precondition** (brief R2 §9 AC row; R-FREE prepared state) | AC gate and prepared state fail (a peripheral battery with status `Unknown` makes power UNKNOWN, review 61 P10) |
| D-ALLOW-PATHS | SIP-equivalent classes | none (current); package-manager-owned paths; a name list | options 2–3 **amend R-ALLOW (b)** (package paths are root-writable, not SIP-equivalent, breaking (b)'s rationale) | stricter exclusivity (may be unattainable) |
| D-ALLOW-BASE39 | R-ALLOW's base set "the current 39 names" (macOS daemons) on Linux | keep the names (semantic hazard: a Linux process could use such a basename); drop them | keep: none (hazard); drop: **amends R-ALLOW** | exclusivity per strictest reading |
| D-EXCL-WINDOW | an R-EXCL-PCT reading on Linux; who is the "hosting app" | windowed share with a window length; hosting app = none on a systemd host | windowed share: **changes R-EXCL-PCT's measured quantity** (macOS `ps -o pcpu`); window length: **new number**; "hosting app = none": **removes R-EXCL-PCT's one exception**. Consequence of the current strict reader (review 61 P10): short-lived processes that exit in a window are reported, and an exit race can make a snapshot None, so exclusivity may be unattainable on an ordinary host until this is decided | gate never passes |
| D-PAUSE | hypervisor pause; "awake time" for EVAL_CAP | channel P; hypervisor attestation; bare metal only; L-AWAKE (CLOCK_MONOTONIC) | attestation route: **new rule**; L-AWAKE **amends EVAL_CAP's measurement basis** (brief R2: "EVAL_CAP applies **per attempt, on awake time** (CLOCK_UPTIME_RAW)") | Q12-type evidence never CLEAN; EVAL_CAP basis undefined |
| D-HOST-LIFETIME | what establishes H1 / H3 / H5 / H6 / H8, and how an attestation is accepted | owner statement + provider documentation + inventory at every step; acceptance by the fixed review set of L-LIFE. **Carried items (review 62 E2), to be fixed by the formal review before this can be decided:** (i) a ledger REVIEW line binding the accepting review's path, its recomputed `review_sha256`, the attestation sha256 and the ACCEPTED verdict; (ii) a reviewer identity that is not the coordinator who wrote the attestation, recorded with the review; (iii) the blob-level commit order of L-LIFE. The code implements (iii) only | **new rule** (no macOS counterpart), including the acceptance mechanism | gates `OPEN_DECISION` (§0) |
| D-WORKERS-CORES | "WORKERS 5 on 6 cores": do caps or texts assume cores ≥ WORKERS? | reviewer reading; WORKERS unchanged | reading only | needed before any caps question |
| D-CAPS-CPU | caps measured on macOS arm64 decoys (thin Q12 margins about 6 % and 9 %, route A1 §5 item 3); RLIMIT_CPU semantics differ | keep the caps (MBS-8 (i)) or re-derive from new-host decoys (MBS-8 (ii)) | (ii) changes caps by the accepted §3.2 rule; either is an **owner MBS-8 choice under a changed CPU** | no freeze |
| D-INTERPRETER | the interpreter: CPython 3.14.5 is absent on both Cloud hosts | a named build (version, source, compiler, flags), fixed **before** L-DET | **new pin** | L-DET cannot run (a post-failure interpreter choice would be selection) |
| D-TEXT-LAUNCHD | R-MEM step 1 ("under the launchd launcher") and brief R2 §9 ("only under the launchd launcher") | textual amendment to "under the reviewed launcher (L-LAUNCH)" | **amends R-MEM step 1** and the brief text | R-MEM inputs undefined on Linux |
| D-LID | the clamshell readiness check | drop for servers; Linux lid state for laptops | **amends the readiness checklist** | — |
| D-S15-NEWHOST | how S15 is asserted from another host ([ACCEPTED] governance A1 S15: "Later-found MB r1 evidence is a permanent STOP for the successor, pending its own governance.") | read the MB r1 refs from the pushed repository; owner attestation that the Mac store holds no emergency file; both | **new assertion mechanism for an accepted condition** | the S15 preflight would pass vacuously: forbidden |
| D-LDET-REPEAT | may a non-completing L-DET attempt be repeated | none (current, §5 item 5); a pre-registered repeat rule with a named decider | any repeat rule is a **new rule** not in MBR1_REPRO | no repeat |
| D-PIN-POINT | the fixed module list of the pin point (the science's imports) | the list, fixed in the accepted amendment once the Linux successor build exists | **new pin rule** | `pin_point()` refuses; no pin |
| D-ID-ZOMBIE | may any Linux task state prove death | no (current: zombie ⇒ UNKNOWN); Z/X with only the leader in `/proc/<pid>/task` | yes-option **changes the accepted O-4 outcome** | UNKNOWN (fail closed) |

## 5. Determinism on the new platform (RC2) and gate L-DET

> [ACCEPTED] route A1 §1: "**Determinism is conditional on RC2.** The value of MB-S equals the value the lost MB r1
> run would have produced only **on the same platform**: interpreter, libpython, OS build and architecture. The A0
> certifier review's N2 says the float proposals use libm. Off that platform the S4 "changed" branch applies."
>
> [ACCEPTED] route A1 §3: "**The MBR1_REPRO qualification case.** It re-runs MB r1's committed non-target r3 cases
> through the successor's code: QC02 (decoy 297), QC03 (decoy 316, blocks 0–2), and the QC04 validation-drift ladder
> pair. It requires exact equality of every certified leaf, timing stripped, with MB r1's committed r3 records. Any
> mismatch means STOP and the S4 changed branch. Qualification review E8 applies: these records are never placed next
> to a cell-308 quantity."
>
> [ACCEPTED] brief R2 §9: "Which of the two governs is not settled in the texts I read." (D-RC2-SCOPE)

**What L-DET can and cannot establish.** An exact match shows that this platform reproduces MB r1's **non-target**
records. It does **not** by itself restore governance A1's decisive argument (that the successor's value is the value
the lost run would have produced): under route A1 §1 that argument is lost off the old platform, and the incident
review says so for a changed branch (§6). Whether an exact match discharges the HOST row is D-RC2-SCOPE.

**[PROPOSED] Gate L-DET, pre-registered here, NOT executed:**

1. **Case set (fixed):** exactly MBR1_REPRO's cases — QC02 (decoy 297), QC03 (decoy 316, blocks 0–2) and the QC04
   validation-drift ladder pair (drifts 3 and 11/10) — compared against MB r1's committed r3 records. **Condition
   carried into the formal review (review 60, F5 / N10):** each record's path, commit and sha256, and the sha256 of the
   strip and serializer functions (item 4), are listed by a non-holder in a reference addendum that is **part of the
   text the formal route review accepts**, before OD-3 is put to the owner. Which commit holds the r3 records is to be
   identified there, not assumed (it may post-date freeze r3 `c46434a3`). The coordinator did not compile the list in
   this session.
2. **Code path:** the reviewed Linux successor build only (after ROUTE_PREPARATION step 4, implementation review). No
   ad-hoc harness: it would be new, unreviewed code on the evaluation path.
3. **Interpreter and toolchain (D-INTERPRETER):** fixed in the accepted amendment before any run, with the Linux pins
   of §3 taken at the pin point.
4. **Comparison:** both (a) exact equality of every certified leaf value in exact rationals and (b) byte equality of
   the serialised records after the QC04 timing strip; the strip function and the serializer are pinned by sha256 in
   the addendum of item 1.
5. **Attempts:** every attempt on every host is recorded (start, end, outcome, pins) and disclosed in every later
   brief. **No repeat:** a run that does not complete (crash, cap hit, host interruption) is recorded as such and the
   route stops on that platform until a new owner ruling (r2's proposed one-repeat rule is withdrawn: it had no
   accepted basis and no named decider, review 60 N10; any repeat rule is D-LDET-REPEAT). No best-of-N.
6. **Stop rules:** any mismatch ⇒ HOST row stays EXCLUDED on that platform; the route stops before any designated
   series; the mismatch goes to the owner and an independent reviewer. A mismatch is never repaired by changing
   science, seeds, libm or interpreter.
7. **No host shopping:** one L-DET per owner host decision (OD-1). After a mismatch, any further host needs a new
   owner ruling and a fresh review with the earlier failure in view, and every failure is disclosed in later briefs.
8. **E8:** no L-DET record or value is placed next to a cell-308 quantity.
9. **Caps evidence:** L-DET runtimes are **excluded** from the caps evidence (S13 / MBS-8 allow only official decoy
   or qualification evidence); they are recorded but never designated.

Authorization before any run: route-review acceptance of this protocol, the D-RC2-SCOPE and D-INTERPRETER decisions,
and an owner decision (OD-3). This session ran no decoy and no science module.

## 6. Incident-independence (S12)

> [A6C-SANITIZED S3: original line 239 redacted, class Q: quoted block carrying an excluded-source file path]
> [A6C-SANITIZED S3: original line 240 redacted, class Q: quoted block carrying an excluded-source file path]
> [A6C-SANITIZED S3: original line 241 redacted, class Q: quoted block carrying an excluded-source file path]
>
> [A6C-SANITIZED S3: original line 243 redacted, class Q: quoted block carrying an excluded-source file path]
> [A6C-SANITIZED S3: original line 244 redacted, class Q: quoted block carrying an excluded-source file path]

A platform change is S4's changed branch under route A1 §1 (D-RC2-SCOPE (a)). This proposal therefore treats the route,
for every decision that needs a rating, as **HIGH**, with the decisive argument **lost** and the successor's value a
**second, different draw**, unless D-RC2-SCOPE is decided otherwise by an independent reviewer and the owner.
Independently of that, MBS-5(b) applies after any MB-S marker. A fresh S12 reviewer, who has not seen the MB r1
target-run observations, rates the route before any freeze.

## 7. Carried verbatim (unchanged)

> [ACCEPTED] SUCCESSOR_GOVERNANCE_308 **S5**: "**Liabilities carried forward verbatim.** Incidents 01–03, H4.3b, I-a…I-e
> with E1′, the F2/F3 exposures, the quarantine breach, single-implementation inputs, and result-chasing MEDIUM–HIGH. The
> C4 conditions U1–U8 are the minimum for any new ruling."

> [ACCEPTED] SUCCESSOR_GOVERNANCE_308 **S7**: "**Exactly-once, again.** The successor has its own single marker and
> grant. A failure after its marker gives its own frozen INDETERMINATE-class outcome. Any further successor needs a
> further governance process and user ruling."

> [ACCEPTED] SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1 **S13**, in full:
>
> * **S13 (GC-6). Exposure.** A formal exposure addendum (E1″ in `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`) names,
>   never values, the MB r1 target-run runtime and host observations, where they are recorded, and who holds them.
> [A6C-SANITIZED S3: original line 266 redacted, class C: content attributed to an excluded source by file path and line citation]
>   * The successor's route, implementation and caps agents have not seen them. The builder was instructed so on
>     2026-09-29 ~20:40Z, and must disclose any prior reading.
>   * The caps decision is justified from decoy and qualification evidence only.
>
> [ACCEPTED erratum, governance A1 erratum E1 **D2**:] "The successor builder was instructed about GC-6 at
> **2026-09-29 18:39:04Z**, not "~20:40Z". The same applies to A1 §4 S13 ("2026-09-29 ~20:40Z")."
>
> [ACCEPTED, same erratum **D3**:] "The holder list is extended by: **reviewGOV**, the successor-governance reviewer,
> [A6C-SANITIZED S3: original line 275 redacted, class C: content attributed to an excluded source by file path and line citation]
> (reviewADJ), who reads the recovery chain and the execution review. Neither may take a successor route,
> implementation or caps role (S13)."

For this route: every route, implementation, caps, L-DET or qualification agent discloses any prior reading of E1″
material before taking the role, and E1″ holders (including reviewGOV and reviewADJ) take none of these roles.

> [A6C-SANITIZED S3: original line 282 redacted, class K: quoted text naming an excluded source, source not established, redacted conservatively]
> [A6C-SANITIZED S3: original line 283 redacted, class K: quoted text naming an excluded source, source not established, redacted conservatively]
> [A6C-SANITIZED S3: original line 284 redacted, class K: quoted text naming an excluded source, source not established, redacted conservatively]

Any grant on this route would be cell 308's **second** consumed evaluation, under a new S1 ruling meeting governance
A1 §3 as amended by erratum E1 D1, plus §5–§6 above.

## 8. Sequence (ROUTE_PREPARATION steps) — state on 2026-10-15

| step | content | state |
|---|---|---|
| 1 | inventory and source verification | done for the Anthropic-hosted environment (r1, r2, r2b); **not done** for any official host |
| 2 | feasible-host determination, route amendment, independent route / governance review, fresh S12, operator design approval | r5 draft; reviews of drafts only (59 of r1, 60 of r2, 61 of r3, 62 of r4; a delta review of r5 follows and is recorded only when made); host needs OD-1 |
| 3 | campaign namespace and reviewed implementation | dev-only precursor (`streams/CLOUD_R1_LINUX_DEV/`, revision 5); no namespace, no refs |
| 4–9 | implementation review … grant and target | blocked; **not authorized** |

## 9. Checklist for the formal route reviewer

1. Is anything relaxed, or an unknown turned into a pass (text, table, code)?
2. Are §4's open decisions complete, and is every option correctly labelled as a rule change / new number?
3. Is the L-PIN equivalence argument adequate for RC2?
4. Does L-DET (§5) faithfully implement MBR1_REPRO, and are its attempt, stop and no-host-shopping rules adequate?
5. D-RC2-SCOPE: which text governs?
6. Is the HOST_UNSUITABLE classification (confirmed by review 59) carried correctly?
7. Are S5, S7, S10, S13 (with E1 D2 / D3) and MBS-5(b) carried without loss?

## 10. Disposition of review 59's findings

| finding | where addressed |
|---|---|
| F1 BLOCKING (pins miss libm) | L-PIN row and equivalence; `lx_platform.platform_readings` / `mapped_objects` / `dpkg_versions`; tests `TestPins` |
| F2 BLOCKING (zombie ⇒ DEAD) | L-ID row (L-ID-1 withdrawn); D-ID-ZOMBIE; code; test `test_zombie_leader_with_live_thread_is_not_dead` |
| F3 S13 with loss | §7 (full text, E1 D2, E1 D3); ledger correction line |
| F4 determinism scope; S12 quote | D-RC2-SCOPE; §5 preamble; §6 replaced; owner brief r2 OD-3 reworded |
| F5 L-DET | §5 items 1–9 |
| F6 missing decisions | D-S15-NEWHOST, D-ALLOW-BASE39, D-CAPS-CPU, D-INTERPRETER, D-TEXT-LAUNCHD, D-LID; update vectors in H3 / L-UPD |
| F7 rule-change labels | §4 column "amends which accepted text / new number" |
| F8 gates pass absent / rejected records | L-LIFE, L-UPD; `attestation_valid`; tests `TestAttestationPreflight` |
| F9 power | L-POWER; tests `test_failed_or_unknown_supplies_are_unknown` |
| F10 cgroups | L-FREE, H6; tests `TestMemory` |
| F11 auto-update | L-UPD; tests `TestUpdatesLaunch` |
| F12 tests | 60 tests; reviewer mutants R01–R10 in the harness (all killed) |
| F13 exclusivity | L-EXCL; tests `TestBusy` |
| F14 namespaces | L-ID; test `test_namespace_mismatch_is_unknown` |
| F15 launch gate | L-LAUNCH (`mode`); test `test_launch_gate_modes` (revision 2; in revision 4: `test_launch_gate_uses_a_fresh_reading`) |
| F16, F17 | `CLOUD_FEASIBILITY_R2_ERRATUM_E1.md`, `OFFICIAL_PROVIDER_FACTS_20261014_ERRATUM_E1.md` |
| F18 [ACCEPTED] on ROUTE_PREPARATION | label [PREPARATION] (§0, §4) |
| F19 inventory comparison | `lx_inventory.py` revision 2; `CLOUD_HOST_INVENTORY_R2B_20261014.json` |
| F20 identity / V-A | H8; owner brief r2 V-A |
| F21 ledger notes | new ledger lines (counts, bindings, tool version noted); TEST_RUN counts from "Ran N" |
| F22 tautological controls | removed; the mutation harness is the control |
| F23 stale tmp | L-FSYNC (`StaleTmp`); test `test_stale_tmp_is_a_named_state` |

## 11. Disposition of the delta review 60's findings and conditions

| item | where addressed |
|---|---|
| N1 MAJOR self-asserted attestation; gates PASS while D-HOST-LIFETIME open | L-LIFE and L-UPD rows; `attestation_valid` reads every fact from the committed file and a committed acceptance line; `host_lifetime_attested` and the provider-image half of `no_automatic_os_install` are OPEN_DECISION while the decision is open; tests `test_attestation_read_from_committed_files`, `test_forged_or_unaccepted_attestations_refused`, `test_lifetime_gates_open_while_undecided` (r4 cited `test_attestation_read_from_the_committed_file`, which no longer exists; review 62 G10) |
| N2 MAJOR unrecognised battery status ⇒ AC | L-POWER; `KNOWN_NOT_DISCHARGING`; test `test_unrecognised_battery_status_is_unknown` |
| N3 MAJOR truthy root attestation | L-FREE, H6; `root_attested is True` from the verified attestation; chain-wide cpu / pids; tests `test_root_attestation_is_derived_never_asserted`, `test_v1_needs_root_attestation_for_a_number`, `test_cgroup_resources_whole_chain` (r4 cited `test_root_attestation_must_be_true`, which no longer exists) |
| N4 MAJOR nested PID namespace view | L-EXCL; initial-namespace check; test `test_proc_view` |
| N5 MAJOR surviving mutants X01–X09 | all nine in the harness with tests that kill them |
| N6 boot-id validation | `boot_id_recorded` validates the value; test `test_boot_id_must_be_valid` |
| N7 exclusivity blind spots | exited processes reported; unreadable existing process ⇒ no reading; campaign tree keyed by (pid, starttime); tests in `TestBusy` |
| N8 unrecorded namespace | L-ID; test `test_unrecorded_namespace_never_proves_death` |
| N9 labels | §4 rows D-MEM-PRESSURE, D-THERMAL, D-LPM, D-EXCL-WINDOW, D-PAUSE (L-AWAKE) relabelled; owner brief r3 OD-2 reworded |
| N10 L-DET repeat rule | §5 item 5 (no repeat); D-LDET-REPEAT row |
| N11 pin set | required members; `pin_point`; test `test_required_members_and_pin_point`, `test_unknown_interpreter_package_never_matches` |
| N12 caller-supplied launch record | `launch_record_ok`; tests `test_launched_by_systemd_requires_everything`, `test_launch_gate_uses_a_fresh_reading` (r4 cited `test_launch_record_fields_are_verified`, which no longer exists) |
| N13 near-tautological tests | `test_live_host_is_never_clean` uses a list-valued journal; two tests renamed and sharpened |
| N14 record wording | ledger correction line (review-60 line); owner brief r3 V-A quotes the provider text; D-S15-NEWHOST quotes S15 verbatim |
| F4 deviation (T1 not stated as fired) | **Recorded here, with its reason:** incident-review N3 (line 116) includes MBR1_REPRO's exact reproduction, so whether N3 — and so T1 — fails off-platform is exactly D-RC2-SCOPE. The coordinator does not decide a reading of an accepted review; the **default** treatment (§6) is the conservative one: HIGH, decisive argument lost, a second, different draw. |
| F5 / condition 2 (digests) | carried as an explicit condition into the formal review (§5 item 1); not compiled in this session |
| C1 (no rev-2 code cited) | §3 preamble: revision 3 is cited only after a fresh delta review of revision 3 |

## 12. Disposition of the delta review 61's findings and conditions

| item | where addressed |
|---|---|
| P1 MAJOR self-designated acceptance record | L-LIFE: acceptance found in a fixed review set, exact acceptance and verdict lines, different commit, any rejecting review refuses; D-HOST-LIFETIME labels the mechanism a new rule; test `test_acceptance_is_found_not_named` (incl. review 61 probe B1's three cases and Y03) |
| P2 MAJOR caller `root_attested=True`; non-initial cgroup namespace | L-FREE: `root_attestation()` inside `memory_readings`; non-initial or unreadable cgroup namespace blocks a number; no caller flag; test `test_root_attestation_is_derived_never_asserted` (Y04) |
| P3 MAJOR §3 claims | rows L-FREE, L-LIFE, L-SLEEP, L-LAUNCH, L-UPD, L-PIN, L-ID restated as revision 4 implements them; D-HOST-LIFETIME row says OPEN_DECISION |
| P4 MAJOR surviving mutants | Y01–Y09 in the harness with killing tests (Y01 `test_lifetime_gates_open_while_undecided`, Y02 `test_exited_child_of_reused_campaign_pid_is_reported`, Y03 / Y05 attestation tests, Y04 above, Y06 `test_required_members_and_pin_point`) |
| P5 `decided` parameter | removed; `DECIDED` is a validated module constant; tests `test_no_trust_parameters_in_production`, `test_decided_is_validated` |
| P6 caller-built launch record | fresh `launched_by_systemd()` inside `preflight`, equality with any passed record, int MainPID; test `test_launch_gate_uses_a_fresh_reading` |
| P7 caller-silenced L′ | `JOURNAL_READER_REVIEWED = False`; test `test_no_reviewed_journal_reader_never_clean` |
| P8 timer in one directory | `unit_enabled` over every unit root or `systemctl is-enabled`; tests `test_unit_enabled_from_every_root`, `test_systemctl_path_when_systemd_is_pid1` |
| P9 identity record shape | `_ident_shape_ok`; test `test_malformed_records_prove_nothing` |
| P10 strictness / host-dependence | consequences stated under D-EXCL-WINDOW and D-POWER-ABSENT; the three live tests skip or switch when the host facts they assume do not hold |
| P11 pin-point list | `PIN_POINT_MODULES` undefined ⇒ `pin_point()` refuses; empty list refused; D-PIN-POINT row |
| P12 owner brief OD-2 | owner brief r4 names amendment r4 |
| P13 record wording | the review-61 ledger line and the revision-4 ledger line correct the counts (tests, mutant ids), the stale test citation (§10), M25's initial survival, and the docstring headers |
| D1 citation | §3 preamble |

## 13. Disposition of the delta review 62's findings and conditions

| item | where addressed |
|---|---|
| G1 MAJOR acceptance set includes subdirectories (reviewer scratch) | L-LIFE: direct children of `reviews/` named `REVIEW_HOST_ATTESTATION_*.md` only; `_acceptances`; tests `test_acceptance_is_found_not_named` (subdirectory, wrong-suffix cases); mutants Q02, Q05. A ledger REVIEW binding is **not** implemented; it is carried item (i) of D-HOST-LIFETIME (E2) |
| G2 MINOR commit order bound to paths | L-LIFE: accepting **line** (repository-wide `git log -S`) strictly after the attested **blob** (`--find-object`); `_ordered`; test `test_accepting_line_must_post_date_the_attested_blob` (placeholder review, placeholder attestation, `git mv` into the set, acceptance first); mutants P01, Z05, Z06, Q06. Remaining limit stated in L-LIFE (no independence; clone depth) |
| G3 MINOR rejection only as upper-case `REJECTED` in prefix files | L-LIFE: single verdict line; negative words case-insensitive in every committed file under `reviews/`, recursively; tests in `test_acceptance_is_found_not_named` (lower-case rejection elsewhere, NOT_ACCEPTED in a scratch file, WITHDRAWN, two verdict lines); mutants Z01, Q01, Q03, Q04 |
| G4 MAJOR surviving mutants Z02, Z03, Z04, Z07, Z11 | Z01–Z11 in the harness; killing tests: Z02 / Z04 `test_file_mode_edge_cases`, Z03 `test_systemctl_path_when_systemd_is_pid1`, Z07 `test_failed_systemctl_query_is_no_reading` (the query itself, not a patched wrapper), Z11 `test_malformed_records_prove_nothing`. Z05 / Z06 targeted `_added_in`, which revision 5 removed; the harness carries the same two weakenings of its successor `_ordered` (see `run_mutants.py`) |
| G5 MINOR `preflight(readings=…)` | parameter removed; `preflight` reads power, disk, boot id and updates itself; caller inputs listed in §3 "Caller inputs"; tests `test_no_trust_parameters_in_production`, mutants Q10, Q11 |
| G6 MINOR `busy_processes(view_complete=True)` default | parameter removed; a fresh `proc_view_complete()` inside; L-EXCL; test `test_view_is_read_not_assumed`; mutants M31, Z10 |
| G7 MINOR update units | L-UPD restated: `is-active`, all is-enabled states, full search path (13 roots), dangling links; tests `test_systemctl_path_when_systemd_is_pid1`, `test_file_mode_edge_cases`; mutants Q07, Q09, Q12. Residual gaps (`Wants=` inside unit files; no `list-dependencies --reverse`) stated in L-UPD |
| G8 NOTE pin-point override | `pin_point()` has no parameter; L-PIN; test `test_required_members_and_pin_point` |
| G9 NOTE `not-found` unattainable | not-found ⇒ not enabled only when no unit file or link exists in any root, else unknown; L-UPD; mutant Q08 |
| G10 NOTE record and wording items | §11 citations corrected above (the r4 text is kept unchanged); H6 restated; §3 preamble with the qualifier; `run_mutants.py` docstring "P01-P15"; owner brief r5 states which delta reviews are recorded (E4); the module docstring and README now name the remaining reader parameters as test locations that a reviewed caller never passes; the fail-closed side effects in L-LIFE; the review-62 ledger line records the items (E3) |
| G11 NOTE reader seams; vocabulary | §3 "Caller inputs"; `OPEN_DECISIONS` = §4's 21 ids; `_GATE_DECISION["host_exclusive"]` names its three decisions; tests `test_decided_is_validated`, `test_unknowns_never_pass_and_are_reported` (all three reported; mutant Q13) |
| E1 citation | §3 "Citation status" |
| E2 amendment | L-UPD, L-EXCL, L-PIN, L-LIFE, H6 restated; D-HOST-LIFETIME carried items (i)–(iii) |
| E3 records | a new ledger line; lines 470 and 471 are not edited |
| E4 owner brief | owner brief r5 states that review 62 (of revision 4) is recorded and that revision 5's delta review is not yet recorded when r5 is written |
[A6C-SANITIZED S3 artifact of level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md at 4f814796757bb1a14086b88d677adef94309d0f6 (49318 bytes, sha256 d0963b110baab7beb86fa80184b9ebf2aab21362d7c7e35745fc10b06f9ba933). 10 lines redacted line-for-line (C=2, K=3, Q=5); every other line is byte-identical to the original; line numbers are preserved.]
