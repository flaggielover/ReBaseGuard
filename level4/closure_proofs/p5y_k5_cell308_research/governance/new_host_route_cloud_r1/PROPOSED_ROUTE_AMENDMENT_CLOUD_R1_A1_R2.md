# PROPOSED route amendment A1, revision r2 — Cell-308 MB-S new-host route (S4 changed branch): Linux platform contract

> **Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** Revision r2 of the draft
> `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md` (kept byte-unchanged as the reviewed r1 draft). r2 repairs the findings of
> the fresh independent review 59 (`reviews/REVIEW_CLOUD_R1_FEASIBILITY_AMENDMENT_DEV.md`; verdict on r1:
> NEEDS_REVISION). Disposition of every finding: §10. It amends nothing until (1) an independent route / governance
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
| H6 | the effective memory allowance is fixed and readable; **no cgroup ancestor is hidden** (a reader cannot see ancestors above a cgroup-namespace root, so this is attested, not read) | R-MEM step 5, R-FREE (whatever D-MEM-* decides) | attestation `root_attested`; without it the reader gives only `visible_limit_upper_bound` |
| H7 | the operator can reach the machine to launch `resume` / `recover` | MBS-3; brief R2 §7 item 8 ("launched by the operator") | owner statement |
| H8 | the same physical / virtual machine for every official step: hardware-bound identity (DMI `product_uuid`, hashed) or an owner attestation; `/etc/machine-id` alone is **not** an identity on image-cloned VMs | as H1 | `machine_identity()` recorded at every step; attestation binds it |

## 3. Linux platform contract [PROPOSED]

Development implementation: `streams/CLOUD_R1_LINUX_DEV/lx_platform.py` revision 2 (DEV_ONLY); tests
`tests/test_lx_platform.py` (60 tests); mutation harness `tests/run_mutants.py` (42 mutants: 32 coordinator,
10 from review 59). Port map: `results/PORT_MAP_142D97A9.json`.

| row | macOS mechanism (accepted, candidate `142d97a9`) | Linux replacement (proposed) | fail-closed behaviour | status |
|---|---|---|---|---|
| L-LAUNCH | launchd job; `launched_by_launchd` | systemd service `rebaseguard-mbs308-*.service`; `launched_by_systemd`: systemd PID 1, own cgroup is that unit, `INVOCATION_ID` == `systemctl show` InvocationID, MainPID == pid. `preflight(mode=…)`: `execute` / `resume` without the launch record FAIL; only `launcher_preflight` may omit it | any failed reading ⇒ not launched | PROPOSED; the accepted texts that name launchd need textual amendment (**[OPEN] D-TEXT-LAUNCHD**) |
| L-DETACH | launchd detachment | systemd service; a `setsid` grandchild is **not** a launcher (survives its parent, not the host) | — | PROPOSED |
| L-ID | (pid, `ps lstart` UTC, boot UUID, `ps command` sha256); R2 / N-2; O-4: an unreadable argv (zombie) is a failed reading ⇒ UNKNOWN | (pid, `/proc/<pid>/stat` starttime, `boot_id`, `/proc/<pid>/cmdline` sha256, **recorder's PID and time namespace inodes**); same tri-state; **a zombie (Z/X) is UNKNOWN**, never DEAD (L-ID-1 of r1 is **withdrawn**: a zombie leader can carry live threads, review 59 probe P6, now a test); namespace mismatch ⇒ UNKNOWN | DEAD only on positive evidence (reboot, ESRCH in the same namespace, recorded starttime or cmdline differs) | PROPOSED (mechanical); any further death evidence is **[OPEN] D-ID-ZOMBIE** |
| L-BOOT | `kern.bootsessionuuid` | `boot_id` | malformed ⇒ None | PROPOSED; a VM pause need not change it (D-PAUSE) |
| L-SLEEP | channels K, S, L | K′ (BOOTTIME − MONOTONIC), S′ (`suspend_stats`), L′ (journal; **no reader exists yet**, so L′ is always AMBIGUOUS), plus **P** (REALTIME − MONOTONIC ⇒ AMBIGUOUS only; P is **not** a pause detector) and a boot-id change ⇒ CONTAMINATED; power at every reading; `SLEEP_GAP_TOL_NS` and `MAX_SAMPLE_GAP_S` pinned by a test to the candidate's values | CLEAN only if every channel exists and none fires | PROPOSED; **[OPEN] D-PAUSE** (on a VM, K′/S′/L′/P cannot see a hypervisor pause invisible to the guest clocks) |
| L-AWAKE | `AwakeCap` on `CLOCK_UPTIME_RAW` (absent on Linux) | `CLOCK_MONOTONIC` | — | **[OPEN] D-PAUSE** |
| L-POWER | `pmset -g batt` = "AC Power" | Mains online, no Battery / UPS discharging, every supply readable and of a known type ⇒ AC; no supply ⇒ `ABSENT`; unreadable type / status or a type other than Mains, Battery, UPS (USB-C, wireless) ⇒ None | `ABSENT` ⇒ `OPEN_DECISION`; None ⇒ UNKNOWN | **[OPEN] D-POWER-ABSENT** |
| L-THERMAL | thermal-pressure level 0 | raw zones and trip points only | `OPEN_DECISION` | **[OPEN] D-THERMAL** |
| L-LPM | `pmset lowpowermode` 0 | none chosen | `OPEN_DECISION` | **[OPEN] D-LPM** |
| L-LID | `ioreg AppleClamshellState` (host-readiness checklist, `mbs308_qualify.py` lines 338–341) | none chosen (servers have no lid; laptops expose `/proc/acpi/button/lid/*/state` on some hardware) | not part of the gate set | **[OPEN] D-LID** |
| L-MEMP | `kern.memorystatus_vm_pressure_level` == 1 | raw PSI only | `OPEN_DECISION` | **[OPEN] D-MEM-PRESSURE** |
| L-FREE | R-FREE's `free_memory_bytes` = vm_stat free + inactive + speculative + purgeable | raw MemAvailable, MemFree, Inactive(file), cgroup chain (v1 limit / usage; v2 min(memory.max, memory.high) / memory.current); `effective_limit` and `cgroup_min_headroom` numeric **only** with every level readable **and** the root attested (H6); otherwise `visible_limit_upper_bound` only; raw cpu.max / cpuset / pids.max | no R-FREE value; a partial chain never yields a number | **[OPEN] D-MEM-FREE** |
| L-WIRED | R-MEM step 5: `hw.memsize − W_idle` | none chosen | `OPEN_DECISION` | **[OPEN] D-MEM-WIRED** |
| L-RSS | watchdog `ps -o rss`; `ru_maxrss` | VmRSS or `ps -o rss` (KiB); `ru_maxrss` is KiB on Linux, **bytes on macOS** | — | PROPOSED; unit handled explicitly (reviewer item) |
| L-EXCL | `ps -o pcpu` (a decaying average on macOS) | per-process ticks over a fixed window, keyed by (pid, starttime); a process born in the window is charged all its ticks; `own_pids` may not contain 0 or 1; a nested PID namespace or `hidepid` / `subset` /proc ⇒ no reading | no reading ⇒ gate fails | **[OPEN] D-EXCL-WINDOW** |
| L-ALLOW | R-ALLOW (b) SIP prefixes; the base set of 39 macOS names | none: no Linux path or name is auto-allowed (strictest) | busy non-campaign process ⇒ refuse | **[OPEN] D-ALLOW-PATHS**, **D-ALLOW-BASE39** |
| L-UPD | SoftwareUpdate keys; missing key = enabled | `apt-config dump` (apt's own parsing) + timer + snapd + cloud-init + livepatch + `Automatic-Reboot`; "shown disabled" only on positive evidence for every vector; provider image changes UNKNOWN unless attested | not shown disabled ⇒ UNKNOWN | PROPOSED (H3) |
| L-SLEEPPREV | `caffeinate -i -m -s` | server: nothing; laptop: `systemd-inhibit --what=sleep:idle` | detection binds | PROPOSED |
| L-FSYNC | fsync + `F_FULLFSYNC`; git `core.fsync` | fsync file, rename, fsync directory (order tested); a stale tmp raises the named state `StaleTmp`, never deleted (the state machine must name its operator action) | read-back verify | PROPOSED; device honouring fsync is H5 |
| L-PIN | `PLATFORM_PINS`: interpreter path + sha256, libpython sha256, `sys.version`, `sw_vers` build, arch | interpreter path + sha256; `sys.version`; **sha256 of every shared object mapped into the interpreter at the pin point (after the science modules are imported)** — this includes `libm.so.6`, `libc.so.6`, the loader and every `lib-dynload` extension; dpkg versions of `libc6` and the interpreter's packages; livepatch list; os-release; kernel release; machine; glibc string. libpython is pinned only if mapped (it is not, for Ubuntu's static `python3.x`). CPU model and vCPU count recorded | an unreadable pin (or a None inside a dict pin) never matches | PROPOSED; see equivalence below |
| L-DISK | `statvfs` ≥ 2 GiB | same | unreadable ⇒ UNKNOWN | PROPOSED (mechanical) |
| L-LIFE | (none on macOS) | `host_lifetime_attested`: PASS only for a record with `reviewed is True` and `accepted is True`, a path committed at HEAD whose blob sha256 matches, an acceptance-record reference, and a hardware-bound machine identity equal to the current one | otherwise UNKNOWN | PROPOSED; **[OPEN] D-HOST-LIFETIME** |
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
| D-MEM-PRESSURE | "pressure normal" | PSI `some avg10` = 0 over N readings; v1 pressure events; none | **new rule; new number N** | start gate never passes |
| D-THERMAL | thermal level 0 | no zone at/above a passive trip; undefined without zones | **new rule** | never passes on hosts without zones |
| D-LPM | low-power mode off | platform profile / governor | **new rule** | never passes |
| D-POWER-ABSENT | AC gate with no Mains supply, or USB-C / UPS supplies | keep (only Mains hosts); server rule | keep: none; server rule: **amends the AC precondition** (brief R2 §9 AC row; R-FREE prepared state) | AC gate and prepared state fail |
| D-ALLOW-PATHS | SIP-equivalent classes | none (current); package-manager-owned paths; a name list | options 2–3 **amend R-ALLOW (b)** (package paths are root-writable, not SIP-equivalent, breaking (b)'s rationale) | stricter exclusivity (may be unattainable) |
| D-ALLOW-BASE39 | R-ALLOW's base set "the current 39 names" (macOS daemons) on Linux | keep the names (semantic hazard: a Linux process could use such a basename); drop them | keep: none (hazard); drop: **amends R-ALLOW** | exclusivity per strictest reading |
| D-EXCL-WINDOW | an R-EXCL-PCT reading on Linux; who is the "hosting app" | windowed share with a window length; hosting app = none on a systemd host | window length: **new number**; "hosting app = none": **removes R-EXCL-PCT's one exception** | gate never passes |
| D-PAUSE | hypervisor pause; "awake time" for EVAL_CAP | channel P; hypervisor attestation; bare metal only | attestation route: **new rule** | Q12-type evidence never CLEAN |
| D-HOST-LIFETIME | what establishes H1 / H3 / H5 / H6 / H8 | owner statement + provider documentation + inventory at every step | **new rule** (no macOS counterpart) | gate UNKNOWN |
| D-WORKERS-CORES | "WORKERS 5 on 6 cores": do caps or texts assume cores ≥ WORKERS? | reviewer reading; WORKERS unchanged | reading only | needed before any caps question |
| D-CAPS-CPU | caps measured on macOS arm64 decoys (thin Q12 margins about 6 % and 9 %, route A1 §5 item 3); RLIMIT_CPU semantics differ | keep the caps (MBS-8 (i)) or re-derive from new-host decoys (MBS-8 (ii)) | (ii) changes caps by the accepted §3.2 rule; either is an **owner MBS-8 choice under a changed CPU** | no freeze |
| D-INTERPRETER | the interpreter: CPython 3.14.5 is absent on both Cloud hosts | a named build (version, source, compiler, flags), fixed **before** L-DET | **new pin** | L-DET cannot run (a post-failure interpreter choice would be selection) |
| D-TEXT-LAUNCHD | R-MEM step 1 ("under the launchd launcher") and brief R2 §9 ("only under the launchd launcher") | textual amendment to "under the reviewed launcher (L-LAUNCH)" | **amends R-MEM step 1** and the brief text | R-MEM inputs undefined on Linux |
| D-LID | the clamshell readiness check | drop for servers; Linux lid state for laptops | **amends the readiness checklist** | — |
| D-S15-NEWHOST | how S15 (MB r1 recorded state; "later-found MB r1 evidence is a permanent STOP") is asserted from another host | read the MB r1 refs from the pushed repository; owner attestation that the Mac store holds no emergency file; both | **new assertion mechanism for an accepted condition** | the S15 preflight would pass vacuously: forbidden |
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
   validation-drift ladder pair (drifts 3 and 11/10) — compared against MB r1's committed r3 records. Before any run,
   an amendment addendum lists each record's path, commit and sha256 (taken from MB r1's freeze r3 `c46434a3`
   evidence by a non-holder), so the reference set cannot be chosen afterwards.
2. **Code path:** the reviewed Linux successor build only (after ROUTE_PREPARATION step 4, implementation review). No
   ad-hoc harness: it would be new, unreviewed code on the evaluation path.
3. **Interpreter and toolchain (D-INTERPRETER):** fixed in the accepted amendment before any run, with the Linux pins
   of §3 taken at the pin point.
4. **Comparison:** both (a) exact equality of every certified leaf value in exact rationals and (b) byte equality of
   the serialised records after the QC04 timing strip; the strip function and the serializer are pinned by sha256 in
   the addendum of item 1.
5. **Attempts:** every attempt on every host is recorded (start, end, outcome, pins) and disclosed in every later
   brief. A run that does not complete (crash, cap hit, host interruption) is recorded as such; it may be repeated
   only under a rule fixed before the first attempt — proposed: **at most one repeat, only for a positively
   infrastructural non-completion, never after any comparison result has been seen.** No best-of-N.
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

> [ACCEPTED] `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`: "**If any of N1–N4 fails,** the successor is on S4's
> changed branch. Its value is then a second, different draw, the decisive argument is lost, and this rating does not
> apply (trigger T1 in Q4)."
>
> [ACCEPTED] same review, Q4: "**T1.** Any of N1–N4 fails at qualification or at any resume (the science is then
> "changed" under S4)."

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
>   * No successor brief contains them or points to REVIEW_EXECUTION_INTERRUPTION §4b.
>   * The successor's route, implementation and caps agents have not seen them. The builder was instructed so on
>     2026-09-29 ~20:40Z, and must disclose any prior reading.
>   * The caps decision is justified from decoy and qualification evidence only.
>
> [ACCEPTED erratum, governance A1 erratum E1 **D2**:] "The successor builder was instructed about GC-6 at
> **2026-09-29 18:39:04Z**, not "~20:40Z". The same applies to A1 §4 S13 ("2026-09-29 ~20:40Z")."
>
> [ACCEPTED, same erratum **D3**:] "The holder list is extended by: **reviewGOV**, the successor-governance reviewer,
> who read REVIEW_EXECUTION_INTERRUPTION §4b's per-coalition CPU figures; **the step-8 adjudication reviewer**
> (reviewADJ), who reads the recovery chain and the execution review. Neither may take a successor route,
> implementation or caps role (S13)."

For this route: every route, implementation, caps, L-DET or qualification agent discloses any prior reading of E1″
material before taking the role, and E1″ holders (including reviewGOV and reviewADJ) take none of these roles.

> [ACCEPTED] SUCCESSOR_GOVERNANCE_308 **S10**: "**Isolation from cell 309.** Cell 309 is EXTERNALLY_IN_PROGRESS in a
> separate session. No inspection for continuation, duplication, review, proxy, qualification, authorisation or
> evaluation of cell 309."

Any grant on this route would be cell 308's **second** consumed evaluation, under a new S1 ruling meeting governance
A1 §3 as amended by erratum E1 D1, plus §5–§6 above.

## 8. Sequence (ROUTE_PREPARATION steps) — state on 2026-10-14

| step | content | state |
|---|---|---|
| 1 | inventory and source verification | done for the Anthropic-hosted environment (r1, r2, r2b); **not done** for any official host |
| 2 | feasible-host determination, route amendment, independent route / governance review, fresh S12, operator design approval | r2 draft; reviews of drafts only (59, and a delta review of r2); host needs OD-1 |
| 3 | campaign namespace and reviewed implementation | dev-only precursor (`streams/CLOUD_R1_LINUX_DEV/`, revision 2); no namespace, no refs |
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
| F15 launch gate | L-LAUNCH (`mode`); test `test_launch_gate_modes` |
| F16, F17 | `CLOUD_FEASIBILITY_R2_ERRATUM_E1.md`, `OFFICIAL_PROVIDER_FACTS_20261014_ERRATUM_E1.md` |
| F18 [ACCEPTED] on ROUTE_PREPARATION | label [PREPARATION] (§0, §4) |
| F19 inventory comparison | `lx_inventory.py` revision 2; `CLOUD_HOST_INVENTORY_R2B_20261014.json` |
| F20 identity / V-A | H8; owner brief r2 V-A |
| F21 ledger notes | new ledger lines (counts, bindings, tool version noted); TEST_RUN counts from "Ran N" |
| F22 tautological controls | removed; the mutation harness is the control |
| F23 stale tmp | L-FSYNC (`StaleTmp`); test `test_stale_tmp_is_a_named_state` |
