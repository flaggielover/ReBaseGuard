# PROPOSED route amendment A1 — Cell-308 MB-S new-host route (S4 changed branch): Linux platform contract

> **Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** Drafted 2026-10-14 by the coordinator of a Claude Cloud
> session under the owner's authorization to draft a Cloud successor route amendment
> (`USER_AUTHORIZATION_20261014.md`). It amends nothing until (1) an independent route / governance review accepts it,
> (2) the owner decides the points marked **[OPEN]**, and (3) a fresh S12 incident-independence reviewer rates the
> route. The coordinator's preparation is not an independent review (ROUTE_PREPARATION, Phase 2).
>
> `new_target_evaluations = 0` · `cell309_activity = none` · no designation, qualification, freeze, grant or target
> step is authorized by or performed for this document.

## 0. How to read this document

| label | meaning |
|---|---|
| **[ACCEPTED]** | text of an accepted source, quoted verbatim with its path. Binding today. Never weakened here. |
| **[PROPOSED]** | a new requirement or a Linux replacement this document asks a reviewer to accept. Not binding. |
| **[OPEN]** | a rule-semantics or host decision that this document refuses to make. Until decided, every dependent gate is `OPEN_DECISION`, which never passes. |
| **[OBSERVED]** | a fact recorded in this session's evidence (`CLOUD_FEASIBILITY_R2.md`, `OFFICIAL_PROVIDER_FACTS_20261014.md`, `CLOUD_HOST_INVENTORY_R2_20261014.json`). |

No threshold, number, rule output or scientific input is changed by this document. Where it says "Linux reading",
the reading is a proposal for review, never a substitute applied by the coordinator.

## 1. What stays, what is proposed to change

**Unchanged [ACCEPTED]** — and this document proposes no change to any of them:

* the science and its byte identity (governance A1 **S11**); Theorem MB r1, the cover, D1–D14, the criterion
  (d1 §5.4), the members;
* WORKERS 5, the floors, k, every number of R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW
  (`CONSTANTS_RATIFICATION_MBS308.md`, "Written rules"), the caps (`EVAL_CAP_S`, `DECOY_CAP_S`, rung CPU caps), the
  resume budget (3) and the 7-day deadline;
* exactly-once (**S7**), the S1 ruling requirement, S14–S17, the quarantine (**S9**), Cell-309 isolation (**S10**);
* the MB-S r1 record: designated evidence `86d3f8cb…`, derivation `8a4e7984…`, `NOT_DERIVED` / R-FREE
  `GATE_UNATTAINABLE`, the three INVALID series, `ALREADY_DESIGNATED`. **The old designated series is never deleted,
  replaced or measured again** (ROUTE_PREPARATION, "Immutable baseline");
* MB r1's INDETERMINATE outcome, consumed marker `afa93072`, and its status "not scientifically negative".

**Proposed change [PROPOSED]:** the platform (macOS build 25F84 / arm64 / CPython 3.14.5 framework build, as recorded in brief R2 §9 → a Linux host) and
the host infrastructure only. Under the accepted texts this is S4's **changed branch**:

> [ACCEPTED] `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md`, HOST row: "moving the successor to another host |
> **EXCLUDED unless RC2 is discharged there** | the determinism argument binds the platform. A different host means
> the S4 changed branch, and its own exact reproduction of MB r1's r3 records would be required"

## 2. Host scope [PROPOSED]

### 2.1 What the Anthropic-hosted Cloud session environment may be used for

Target-free development, synthetic tests, static analysis and reviews only. Not the designated series, not the
official qualification, not the execution. Basis: `CLOUD_FEASIBILITY_R2.md` §3–§4 (U1–U3: idle pause and reclaim,
fresh VM on resume, observed cross-session platform change; coordinator classification `HOST_UNSUITABLE`, pending
independent review; fallback `HOST_UNVERIFIED`).

### 2.2 Requirements on the official host (H1–H8)

Each requirement is a **fact to be established on the actual machine** by a Phase-1 inventory plus a committed owner
attestation; none can be satisfied by assumption, and an unknown is a failure.

| id | requirement | why (accepted source) | how established |
|---|---|---|---|
| H1 | the machine is not paused, reclaimed or replaced while the campaign is idle or running, from the designated series to the 7-day deadline | one host across designation, qualification and execution (brief R2 §9 host-identity row; ROUTE_PREPARATION step 7) | owner attestation + Phase-1 inventory; `host_lifetime_attested` gate |
| H2 | systemd is PID 1 (or another reviewed service manager) so the campaign runs as a service, outside any agent session | S6 ("a launcher that survives the hosting app's death and the launcher's parent's death") | `launched_by_systemd` gate (§3 row L-LAUNCH) |
| H3 | no OS, kernel, libc or interpreter change from the qualification to the deadline | RC2; brief R2 §9 "Platform unchanged" row | Linux pins (row L-PIN) re-verified at execute and every resume; owner controls image and updates |
| H4 | exclusivity can be arranged (no other heavy compute, including other sessions) | S17 "Host exclusivity" | `host_exclusive` gate (D-EXCL-WINDOW, D-ALLOW-PATHS) |
| H5 | local disk honours fsync; the store survives a reboot of the same machine | S6 "crash-safe, atomic, durable persistence" | owner attestation of the storage; durable-write tests on the machine |
| H6 | the effective memory allowance is fixed and readable (no hidden cgroup ancestor, no balloon) | R-MEM step 5, R-FREE (whatever D-MEM-* decides) | cgroup chain reader: unreadable ancestor ⇒ UNKNOWN |
| H7 | the operator can reach the machine to launch `resume` / `recover` | MBS-3, brief R2 §8 item 8 ("launched by the operator") | owner statement |
| H8 | the machine is the same one for every official step (machine id, boot id at each step recorded) | as H1 | inventory records `/etc/machine-id` and boot id at every step |

Candidate machines are an owner decision (`OWNER_DECISION_BRIEF_CLOUD_R1.md`, OD-1).

## 3. Linux platform contract [PROPOSED]

Development implementation of every row: `streams/CLOUD_R1_LINUX_DEV/lx_platform.py` (DEV_ONLY); tests:
`tests/test_lx_platform.py` (44 tests, 20/20 mutants killed). Port map of what the candidate uses:
`results/PORT_MAP_142D97A9.json` (457 lines, 28 files).

| row | macOS mechanism (accepted, candidate `142d97a9`) | Linux replacement (proposed) | fail-closed behaviour | dev test | status |
|---|---|---|---|---|---|
| L-LAUNCH | launchd job; `launched_by_launchd`: `XPC_SERVICE_NAME` == label, PPID 1, `launchctl print` names the pid | transient or installed systemd service `rebaseguard-mbs308-*.service`; `launched_by_systemd`: systemd is PID 1, own cgroup is that unit, `INVOCATION_ID` set and equal to `systemctl show InvocationID`, `MainPID` == pid | any failed reading ⇒ not launched | `test_launched_by_systemd_requires_everything`, `test_live_host_not_launched` | PROPOSED (mechanical) |
| L-DETACH | launchd detachment; launcher never boots out a live job | systemd service (`KillMode=`, `Restart=no`); a `setsid` grandchild is **not** accepted as a launcher (it survives its parent, not the host) | — | `test_detached_child_survives_parent_death` (documents the limit) | PROPOSED |
| L-ID | identity (pid, `ps lstart` UTC, boot session UUID, `ps command` sha256); R2 / N-2 tri-state | (pid, `/proc/<pid>/stat` starttime ticks, `/proc/sys/kernel/random/boot_id`, `/proc/<pid>/cmdline` sha256); same tri-state; empty cmdline = failed read | DEAD only on positive evidence | `TestIdentity` (10 tests) | PROPOSED (mechanical); **L-ID-1**: a zombie (state Z/X) counts as DEAD — a reading for review |
| L-BOOT | `kern.bootsessionuuid` | `boot_id` | malformed ⇒ None | `TestBootId` | PROPOSED; note: a VM pause need not change it (D-PAUSE) |
| L-SLEEP | channels K (MONOTONIC_RAW − UPTIME_RAW), S (`kern.sleeptime/waketime`), L (`pmset -g log`) | K′ (BOOTTIME − MONOTONIC), S′ (`/sys/power/suspend_stats/success`), L′ (journal suspend entries), **plus P** (REALTIME − MONOTONIC divergence ⇒ AMBIGUOUS) and a boot-id change ⇒ CONTAMINATED | CLEAN only if every channel exists and none fires | `TestAssess` (7 tests) | PROPOSED; P is an added, strictly stricter channel; whether K′/S′/L′/P are an acceptable replacement for K/S/L is **[OPEN] D-PAUSE** |
| L-AWAKE | `AwakeCap` on `CLOCK_UPTIME_RAW` (absent on Linux) | `CLOCK_MONOTONIC` (stops in suspend) | — | — (not built: it is driver code) | **[OPEN] D-PAUSE**: whether guest MONOTONIC advances during a hypervisor pause is a host fact |
| L-POWER | `pmset -g batt` = "AC Power" | `/sys/class/power_supply`: Mains online and no Battery discharging ⇒ AC; no supply ⇒ `ABSENT` | `ABSENT` ⇒ `OPEN_DECISION`; failed read ⇒ UNKNOWN | `test_power_classes` | **[OPEN] D-POWER-ABSENT** |
| L-THERMAL | thermal-pressure level 0 (`notifyutil`) | raw `/sys/class/thermal` zones and trip points only | gate `OPEN_DECISION` | `test_thermal_raw_only` | **[OPEN] D-THERMAL** |
| L-LPM | `pmset lowpowermode` 0 | none chosen | gate `OPEN_DECISION` | preflight tests | **[OPEN] D-LPM** |
| L-MEMP | `kern.memorystatus_vm_pressure_level` == 1 | raw PSI `/proc/pressure/memory` only | gate `OPEN_DECISION` | — | **[OPEN] D-MEM-PRESSURE** |
| L-FREE | R-FREE's `free_memory_bytes` = vm_stat free + inactive + speculative + purgeable | raw MemAvailable, MemFree, Inactive(file), cgroup chain limits / usage / headroom, side by side; **no R-FREE value** | gate `OPEN_DECISION`; an unreadable cgroup ancestor ⇒ UNKNOWN, never unlimited | `TestMemory` (6 tests) | **[OPEN] D-MEM-FREE** |
| L-WIRED | R-MEM step 5: `hw.memsize − W_idle` (vm_stat wired) | none chosen | feasibility check `OPEN_DECISION` | — | **[OPEN] D-MEM-WIRED** |
| L-RSS | watchdog `ps -o rss`; `ru_maxrss` | `/proc/<pid>/status` VmRSS or `ps -o rss` (KiB, same unit); `ru_maxrss` is KiB on Linux, **bytes on macOS** | — | — | PROPOSED; unit difference must be handled explicitly (reviewer item) |
| L-EXCL | `ps -o pcpu` (a decaying recent average on macOS) | per-process CPU ticks over a fixed window from `/proc/<pid>/stat`; Linux `ps %cpu` (a lifetime average) is **not** used | no reading ⇒ None ⇒ gate fails | `TestBusy` (4 tests) | **[OPEN] D-EXCL-WINDOW** (window length and the hosting-app exception's meaning on Linux) |
| L-ALLOW | R-ALLOW (b): SIP prefixes `/System/`, `/usr/libexec/`, `/usr/sbin/`, `/sbin/`, `/Library/Apple/` | none: no Linux path is auto-allowed (strictest reading) | any busy non-campaign process ⇒ refuse | `test_no_path_allowlist` | **[OPEN] D-ALLOW-PATHS** |
| L-UPD | SoftwareUpdate keys; a missing key counts as enabled | apt `APT::Periodic::*`, `apt-daily-upgrade.timer`, `unattended-upgrade`; disabled only on positive evidence; provider-image updates UNKNOWN unless attested | UNKNOWN ⇒ not pass | `test_update_positive_evidence_only` | PROPOSED; image-level control is part of H3 |
| L-SLEEPPREV | `caffeinate -i -m -s` supervisor | on a server: nothing to prevent; on a laptop: `systemd-inhibit --what=sleep:idle` | detection (L-SLEEP) binds, as on macOS | — | PROPOSED |
| L-FSYNC | fsync + `F_FULLFSYNC`; git `core.fsync=loose-object,reference` | fsync (no `F_FULLFSYNC` on Linux); same git settings (git ≥ 2.36) | read-back sha256 verify | `TestDurableWrite` (5 tests, SIGKILL injection) | PROPOSED; whether the device honours fsync is H5 |
| L-PIN | `PLATFORM_PINS`: interpreter path + sha256, libpython sha256, `sys.version`, `sw_vers` build, arch | interpreter path + sha256, libpython path + sha256, `sys.version`, os-release ID / VERSION_ID / VERSION, kernel release, machine, glibc; CPU model and vCPU count recorded | an unreadable pin never matches | `test_pins`, `test_r1_vs_r2_hosts_would_mismatch` | PROPOSED; whether CPU model is pinned is a reviewer item |
| L-DISK | `statvfs` ≥ 2 GiB | same | unreadable ⇒ UNKNOWN | preflight tests | PROPOSED (mechanical) |
| L-LIFE | (no macOS counterpart: a laptop is not reclaimed) | `host_lifetime_attested`: PASS only with a committed, independently reviewed and accepted attestation of H1/H5/H8 | otherwise UNKNOWN | `test_preflight_unknowns_never_pass` | PROPOSED; **[OPEN] D-HOST-LIFETIME** |

The gate set as a whole is `lx_platform.preflight`: it passes only if every gate is `PASS`
(`test_preflight_all_pass_requires_every_gate` shows that even with every reading favourable, the five
`OPEN_DECISION` gates keep it from passing).

## 4. Open decisions [OPEN] — not made here

For each, the constraint from ROUTE_PREPARATION applies verbatim:

> [ACCEPTED] "The existing R-ALLOW path-class rules and R-FREE memory definition may not transfer to Linux. If
> unchanged semantics cannot be supported, stop and put the exact incompatibility to an independent route reviewer
> and the owner; do not substitute a Linux metric or path policy silently."

| id | question | options seen (no recommendation is a rule decision) | consequence if unresolved |
|---|---|---|---|
| D-MEM-FREE | which Linux quantity, if any, is R-FREE's "free memory" | (a) MemAvailable; (b) MemFree + Inactive(file); (c) min over the cgroup chain of (limit − usage); (d) min of (a) and (c); (e) none: R-FREE has no Linux meaning ⇒ the route stops | R-FREE cannot be derived ⇒ no freeze |
| D-MEM-WIRED | the right-hand side of R-MEM step 5 under a cgroup limit | effective limit − unreclaimable kernel memory at idle; or effective limit − idle usage; or none | R-MEM feasibility undefined ⇒ no freeze |
| D-MEM-PRESSURE | "pressure normal" on Linux | PSI `some avg10` = 0 over N readings; cgroup v1 `memory.pressure_level` events; none | start gate never passes |
| D-THERMAL | "thermal-pressure level 0" | no zone at or above a passive trip point; hosts with no zones: undefined | start gate never passes on a VM / server without zones |
| D-LPM | low-power mode off | platform profile / governor reading; "not applicable on a server" needs a rule text, not a default | start gate never passes |
| D-POWER-ABSENT | AC gate on a host with no power supply | keep the rule (⇒ only hosts that expose Mains); a rule text for servers (would be a rule change) | start gate and every R-FREE prepared-state reading fail |
| D-ALLOW-PATHS | SIP-equivalent path classes on Linux | none (strictest; current dev behaviour); package-manager-owned read-only system paths; a name list | stricter exclusivity than on macOS (acceptable direction, but may make the gate unattainable) |
| D-EXCL-WINDOW | what an R-EXCL-PCT reading is on Linux, and who the "hosting app" is on a service host | windowed CPU share (window = macOS ps's decay horizon?); hosting app = none on a systemd host | exclusivity gate never passes |
| D-PAUSE | detection of a hypervisor pause / snapshot; meaning of "awake time" for EVAL_CAP | channel P (proposed); hypervisor attestation; bare-metal only | Q12-type timing evidence never CLEAN ⇒ qualification fails |
| D-HOST-LIFETIME | what attestation establishes H1/H5/H8 | owner statement + provider documentation + inventory at every step | `host_lifetime_attested` UNKNOWN ⇒ never passes |
| D-WORKERS-CORES | brief R2 §9: "WORKERS 5 on 6 cores". On a host with < 6 cores, do the caps or any accepted text assume cores ≥ WORKERS? | reviewer reading of the accepted texts; WORKERS itself is not changed | a reading is needed before any caps question |

## 5. Determinism on the new platform (RC2) — the decisive target-free question

> [ACCEPTED] `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md`: "**Determinism is conditional on RC2.** The value
> of MB-S equals the value the lost MB r1 run would have produced only **on the same platform**: interpreter,
> libpython, OS build and architecture. The A0 certifier review's N2 says the float proposals use libm. Off that
> platform the S4 "changed" branch applies."
>
> [ACCEPTED] `reviews/REVIEW_SUCCESSOR_ROUTE_308.md`: "It would break the determinism argument (RC2) unless
> cross-platform bit-identity is shown on decoys. Record it as EXCLUDED unless RC2 is discharged on that platform."

[OBSERVED] The glue `mb308_a0core.py` line 212 builds an "untrusted float candidate (proposal only)"; the accepted
review names `math.erfc`, `exp` and a float LS / Jacobi step in the C2b / C1b proposals. glibc and the macOS libm are
different implementations; nothing in this session establishes that they agree bit for bit on the inputs used.

**[PROPOSED] Gate L-DET (RC2 discharge on the Linux host), pre-registered here, NOT executed:**

1. Inputs: only MB r1's committed **non-target** r3 decoy records and the pinned science bytes (S11 list); the
   quarantine guard active; no cell in 305–309; no drift in [6/5, 13/5] or its mirror.
2. Run on the official Linux host (after H1–H8 are established), with the Linux pins recorded.
3. Pass criterion, fixed now: **every** committed certified non-target output reproduces **exactly** (byte-equal after
   the QC04 timing strip). No tolerance, no subset, no re-run selection.
4. Any mismatch: the HOST row stays **EXCLUDED** on that platform; the route stops before any designated series and the
   mismatch is put to the owner and an independent reviewer. A mismatch is **not** repaired by changing science,
   seeds, libm or interpreter to make the outputs agree (that would be tuning on decoys toward a target-adjacent
   identity claim; any such change is S4's changed branch for the science itself and needs its own review).
5. An exact match discharges RC2 *for that platform only*, subject to the reviewer; it does not by itself make the
   decisive argument of governance A1 hold — that argument is also "conditional on completion" (erratum E1 note) and on
   the pins holding at every resume.

Authorization needed before step 2 runs: route-review acceptance of this protocol and an owner decision (OD-3). This
session ran no decoy and no science module.

## 6. Incident-independence (S12)

> [ACCEPTED] `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`: "**I give no rating to the changed branch,** because it
> does not exist yet. It is **presumptively HIGH**: both premises that keep MB-S at MEDIUM–HIGH (a single draw, and no
> science choice after the loss) are absent. Only a fresh re-rating before that freeze can rebut this (MBS-7)."

This document proposes no rating. A fresh S12 reviewer, who has not seen the MB r1 target-run observations, rates the
route before any freeze. Until then the route is treated as **HIGH** for every decision that needs a rating.

## 7. Carried verbatim (unchanged)

> [ACCEPTED] SUCCESSOR_GOVERNANCE_308 **S5**: "**Liabilities carried forward verbatim.** Incidents 01–03, H4.3b, I-a…I-e
> with E1′, the F2/F3 exposures, the quarantine breach, single-implementation inputs, and result-chasing MEDIUM–HIGH. The
> C4 conditions U1–U8 are the minimum for any new ruling."

> [ACCEPTED] SUCCESSOR_GOVERNANCE_308 **S7**: "**Exactly-once, again.** The successor has its own single marker and
> grant. A failure after its marker gives its own frozen INDETERMINATE-class outcome. Any further successor needs a
> further governance process and user ruling."

> [ACCEPTED] SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1 **S13** (its bullets run together here; […] marks the omitted sentence on the builder's instruction time, which erratum E1 D2 corrects): "**Exposure.** A formal exposure addendum (E1″ in
> `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`) names, never values, the MB r1 target-run runtime and host observations,
> where they are recorded, and who holds them. No successor brief contains them or points to
> REVIEW_EXECUTION_INTERRUPTION §4b. The successor's route, implementation and caps agents have not seen them. […] The
> caps decision is justified from decoy and qualification evidence only."

> [ACCEPTED] SUCCESSOR_GOVERNANCE_308 **S10**: "**Isolation from cell 309.** Cell 309 is EXTERNALLY_IN_PROGRESS in a
> separate session. No inspection for continuation, duplication, review, proxy, qualification, authorisation or
> evaluation of cell 309."

For this route specifically [PROPOSED]: the route counts as MB-S's successor-route consumption of cell 308 only if a
grant is ever issued; it would be cell 308's **second** consumed evaluation (MB r1 being the first), under a new S1
ruling that meets governance A1 §3 as amended by erratum E1 D1, plus the changed-platform terms of §5–§6.

## 8. Sequence (ROUTE_PREPARATION steps) with the state of each gate on 2026-10-14

| step | content | state |
|---|---|---|
| 1 | inventory and source verification | done for the Anthropic-hosted environment (r1, r2); **not done** for any official host |
| 2 | feasible-host determination, route amendment, independent route / governance review, fresh S12, operator design approval | this document **drafted**; independent review of the draft commissioned in this session (`reviews/`), which is a review of a draft, not acceptance of the amendment; host determination needs OD-1 |
| 3 | isolated campaign namespace and reviewed platform implementation; synthetic regressions | **dev-only** precursor exists (`streams/CLOUD_R1_LINUX_DEV/`); no campaign namespace, no refs |
| 4 | implementation and premeasurement review; designation policy; platform bindings | blocked on 2–3 |
| 5 | genuine new-host designated series and exact derivation | blocked; also needs every **[OPEN]** D-MEM-* decision and L-DET |
| 6 | apply, final pre-freeze review, one freeze | blocked |
| 7 | official qualification on the frozen host | blocked |
| 8 | new-route S1 owner ruling | blocked; not satisfied by any owner text so far |
| 9 | grant, final host preflight, target | blocked; **not authorized** |

## 9. Checklist for the independent route reviewer

1. Does any row of §3 or any sentence here relax an accepted threshold, rule or gate, or turn an unknown into a
   pass? (Intended answer: no; the dev code and its mutants are evidence for the implementation side.)
2. Are the §4 open decisions complete? Is any listed "option" in fact a rule change that the document fails to label?
3. Is L-ID-1 (zombie ⇒ DEAD) an acceptable reading of "positive evidence of death"?
4. Is channel P acceptable as an additional, stricter channel, and is K′/S′/L′/P an adequate replacement for K/S/L, or
   is D-PAUSE unresolvable without bare metal?
5. Does L-DET faithfully implement RC2 and the HOST row, and are its stop rules adequate?
6. Is the `HOST_UNSUITABLE` classification of the Anthropic-hosted environment (CLOUD_FEASIBILITY_R2 §3–§4) sound, or
   should it stay `HOST_UNVERIFIED`?
7. Are S5, S7, S10 and S13 carried without loss?
