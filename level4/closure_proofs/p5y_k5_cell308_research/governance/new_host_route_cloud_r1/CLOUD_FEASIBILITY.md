# Cell-308 new-host route (Claude Cloud, r1) — Phase 1 feasibility

Date: 2026-10-04 (inventory collected 06:13:19Z–06:17:03Z). Class: INFRASTRUCTURE. Not designated evidence.

**Classification: `HOST_UNVERIFIED`.**

`new_target_evaluations: 0` · `proxy_evaluations: 0` · `cell309_activity: none` · no benchmark, decoy, designation,
qualification, freeze, grant, apply or target step · no package installed, no system setting changed · the historical
candidate `142d97a9` and the MB-S r1 evidence (`86d3f8cb…`) and its `NOT_DERIVED` / R-FREE `GATE_UNATTAINABLE` stop are
untouched.

This report was prepared by the coordinating agent of this session. It is **not an independent review** of anything,
including of itself.

## 1. Sources verified

* Research tip `39b75ad52c5015410892c74a2b4d77be0d81153f` descends from the verification baseline
  `b565d89e4589f1387c5c3367a29267e32fe54e92`; the tip adds only the three route-preparation files and one ledger line.
* All five source bindings of ROUTE_PREPARATION.md match, byte for byte, at both `b565d89e` and `39b75ad5`:
  SUCCESSOR_GOVERNANCE_308 `4e9e6ad4…`, its ADDENDUM_A1 `c170c726…`, USER_DECISION_BRIEF_308_MBS_R1_RFREE_STOP
  `770778cd…`, USER_DECISION_BRIEF_308_SUCCESSOR_R2 `cda3cf45…`, INCIDENT_INDEPENDENCE_REVIEW_MBS308 `89a2b6ae…`.
* Historical candidate branch still at `142d97a90a1c3fafff394044aa1448674f7a633c`; its designated evidence sha256
  `86d3f8cb…ee90fe`; the research audit copy of the derivation sha256 `8a4e7984…29c17`. No conflict between the
  planning text and the accepted sources was found in the parts read.

## 2. What the host is (observed; full detail in CLOUD_HOST_INVENTORY.json)

| fact | observed |
|---|---|
| virtualization | Firecracker microVM under KVM; PID 1 is `/process_api --firecracker-init` |
| OS / kernel / arch | Ubuntu 24.04.4 LTS; Linux 6.18.44-fc-v64; x86_64 |
| Python | 3.10.20, 3.11.15 (default), 3.12.3, 3.13.14 under /usr/bin; **3.14 absent** (historical pin: CPython 3.14.5, macOS framework build) |
| CPU | 4 vCPUs, Intel Xeon @ 2.80 GHz, 1 thread/core; affinity 0–3; cgroup v1 `cfs_quota_us = -1` (no quota in the guest); host-side quota/overcommit **unknown** |
| memory | MemTotal 16 876 515 328 B (15.72 GiB); no swap; hybrid cgroup v1/v2 |
| effective memory limit | **14 345 035 776 B (13.36 GiB)**, cgroup v1 leaf `/process_api/<id>/claude-code-bash` (this shell and its children); every ancestor unlimited; v2 memory files absent |
| storage | `/dev/vda` ext4, write-back cache; 29 087 260 672 B available (per-session allowance; total device 270 GB) |
| supervisor | none usable: systemd present but not PID 1 (offline); no launchd equivalent; no supervisord/runit/s6/tini |
| clocks | clocksource tsc; MONOTONIC = BOOTTIME so far in this boot; guest visibility of host pause/snapshot unknown |
| power / thermal | `/sys/class/power_supply` and `/sys/class/thermal` empty |
| co-resident | the session controller (`claude`, ~312 MiB RSS), `environment-manager`, `process_api` share the 4 vCPUs |
| boot | boot_id `f2d36d2c-76e0-424a-a332-0d6dab2d6412`, booted 06:12Z |

**Observed restart.** The previous turn of this session worked until about 05:36Z. When this turn began, the VM had
booted again at 06:12Z: no process from the earlier boot existed (including this agent's own background tasks), while
the disk contents written at 05:26–05:33Z were still present. The environment description given to this session says
the container is "ephemeral … reclaimed after a period of inactivity (or when the session ends)", and the provider
documentation says "a new session starts on a fresh machine". No guarantee of lifetime, timeout length or disk
durability was found.

## 3. Why the classification is HOST_UNVERIFIED (and not plausible or unsuitable)

Facts the accepted texts make decisive, which this host cannot establish from inside:

1. **Lifetime and exactly-once (S6, S7).** The campaign's single execution must run to completion and persist its
   result durably; a reboot after the marker is a consumed, interrupted run (boot identity row of brief R2). The
   provider's maximum lifetime, inactivity timeout and whether a VM may be reclaimed while a process runs are
   **unknown**, and a restart between turns was observed. Whether any run fits inside a guaranteed window cannot be
   decided. (The run-length side of that comparison is not estimated here; the excluded historical target-runtime
   observations were not consulted.)
2. **Durability.** Disk survived one observed restart; no durability guarantee exists, and the stated model is
   "commit and push". Durable atomic persistence would then depend on a network push — a design question, not a
   verified property.
3. **Host identity.** Designation, qualification and execution must happen on the same host/configuration. "A new
   session starts on a fresh machine": the identity of CPU model, vCPU count, memory limit and image across sessions is
   **unknown**, and boot_id changes on every restart.
4. **Exclusivity.** No evidence of exclusive compute: the vCPUs are shared with the session controller, which must
   run; host-side neighbour isolation is unknown.

Not `HOST_UNSUITABLE`: no observed fact, on its own, contradicts an accepted rule. Memory headroom (13.36 GiB
effective) is larger than the old route's 6.5 GiB R-FREE value — but that value was derived from macOS
measurements and the macOS memory definition; it is a planning reference only, not a new-host output, and no
comparison of the two is claimed as a gate result. Not `HOST_PLAUSIBLE_ROUTE_REVIEW_REQUIRED`: points 1–4 are required
facts that are unavailable. Per the instruction to stop when a required fact is unavailable, **Phase 1 stops here**;
no Linux platform contract or route amendment is drafted.

## 4. Incompatibilities already visible (for whoever resolves the unknowns; not a design)

Recorded so they are not lost; none is resolved here, and none is to be resolved by the coordinator alone:

* **R-FREE memory definition.** The rule's quantity is macOS `vm_stat` free + inactive + speculative + purgeable. There
  is no Linux identity for it; MemAvailable, cgroup `limit − usage` and others are different quantities. Choosing one
  is a rule-semantics decision for an independent route reviewer and the owner (ROUTE_PREPARATION, Phase 2).
* **R-MEM step 5.** `hw.memsize − W_idle` (wired pages) has no direct Linux counterpart under a cgroup limit below
  physical memory.
* **R-ALLOW (b).** The path classes `/System/`, `/usr/libexec/`, `/usr/sbin/`, `/sbin/`, `/Library/Apple/` are macOS
  SIP classes; the co-resident controller runs from `/opt/claude-code` and `/process_api`.
* **R-EXCL-PCT.** Its ceiling rationale cites a median worker reading of about 99 % on the old host. With WORKERS 5
  (fixed) on 4 vCPUs plus the controller, the per-worker reading and that rationale change.
* **WORKERS 5 on 4 vCPUs.** WORKERS is unchanged here, but the old configuration had 6 cores. Whether timing caps or
  any accepted text assume cores ≥ WORKERS needs a reviewer's reading.
* **launchd launcher, detachment, process identity.** No service manager; PID 1 is the sandbox init.
* **AC power and thermal provenance.** No source exists on this host. An absent check must not become an
  unconditional pass.
* **Platform pins.** Python 3.14.5 (macOS) is absent; installing anything was out of scope for Phase 1.

## 5. Exposure disclosure (coordinator)

In this session the coordinator read: the MB-S r1 candidate code excerpts (`mbs308_rrules.py`, `mbs308_derive.py`,
`mbs308_repin.py`, `mbs308_measure.py`, driver constants), the designated pre-freeze evidence (non-target decoy cells
and host readings), protocol sections 8 and 11.2, excerpts of SUCCESSOR_GOVERNANCE_308 (S4–S10), its ADDENDUM_A1
(S11–S13), USER_DECISION_BRIEF_308_SUCCESSOR_R2, CONSTANTS_RATIFICATION_MBS308_READINGS_R1 and
REVIEW_PREMEASUREMENT_IMPLEMENTATION_MBS308 §10, and git commit subject lines across all branches (some name cell-308
incidents; no values). It listed, but did not open, audit files named EXECUTION_INTERRUPTION_ASSESSMENT* and
INCIDENT_AUDIT*. It did not open any MB r1 target-run record or excluded target-runtime observation, and did not read
any Cell-309 content (branch names only, from `git ls-remote`).

## 6. Remaining blockers and the only conditions to resume

Blocker: the provider facts in §3 (lifetime/timeout, reclaim-while-running, durability, cross-session host identity,
exclusivity) are unavailable from inside the container.

Phase 1 may be re-opened only when one of these exists, recorded as a committed source:

* written provider documentation or an owner-supplied statement establishing those facts for a nameable environment;
  or
* an owner ruling to evaluate a different, persistent host under the same S4 route.

Only then may a feasibility re-assessment decide between the three classes. A plausible host still needs, in order,
the route amendment, independent route/governance review, a fresh S12 incident-independence assessment and operator
design approval before any adaptation code (ROUTE_PREPARATION, Required sequence 2–3). Old same-platform determinism
and the old risk acceptance do not transfer.
