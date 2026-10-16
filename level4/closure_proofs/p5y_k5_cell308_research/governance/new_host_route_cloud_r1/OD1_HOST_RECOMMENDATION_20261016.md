# OD-1 recommendation: official host for the Cell-308 Cloud route r1 (one recommendation, with its H1–H8 evidence)

**Status: COORDINATOR RECOMMENDATION · ADVICE TO THE OWNER · OD-1 UNDECIDED.** This document qualifies no host, buys or
provisions nothing, installs nothing and changes no setting. The administrative actions in §5 are a **proposal for the
owner to perform**, not actions taken. `new_target_evaluations = 0` · `cell309_activity = none`.

The criteria come from `HOST_EVIDENCE_PLAN_H1_H8_ERRATUM_E1_20261016.md` §1. Minimum criteria M1–M8 were classed by
formal review FR1 F3 against accepted text. The preferences are proposals that depend on open D-* items and are kept
as proposals. The S12 rating is in `reviews/REVIEW_S12_RISK_CLOUD_R1.md` (§4 below).

## 1. Which machines could be evaluated, through access already authorized

The only access this session holds is read-only access to its own container. On 2026-10-16 the session read its
environments and peers and found:

| source | result |
|---|---|
| `list_environments` | one environment, `env_01GTgmTdDaUY28GtoGZVi3QY` "Default", kind `anthropic_cloud`. No self-hosted environment (V-A) is configured |
| `ListAgents` | no other session, Remote Control machine or cloud session reachable; only this session's own review subagents |
| the owner's Mac (MB r1 / MB-S r1 host) | no access from this session. It is macOS, not Linux, so it is outside this Linux route by definition. MB-S r1 on it ended NOT_DERIVED (R-FREE GATE_UNATTAINABLE) |

So one machine can be evaluated: **the session host itself.**

## 2. H1–H8 evidence matrix

Each cell is one of three kinds of statement:
* **OBSERVED FAILURE**: read on the machine;
* **MISSING EVIDENCE**: not readable, or not taken;
* **UNKNOWN PROVIDER GUARANTEE**: no documented term found, and none is invented here.

Sources:
* inventory r3 (`CLOUD_HOST_INVENTORY_R3_20261016.json`);
* readings later on 2026-10-16 (plan erratum E1 §2);
* `OFFICIAL_PROVIDER_FACTS_20261014.md` P1–P9 with its erratum E1.

| item / min. criterion | Anthropic session host (`anthropic_cloud`) | self-hosted runner (V-A) | owner-supplied machine (V-B) |
|---|---|---|---|
| H1 lifetime / M1 | **OBSERVED FAILURE**: four restarts on 2026-10-16 (about 02:00Z, about 02:26Z, 06:01:44Z, 06:23:11Z; boot ids `fdbfb93e…` and `7bccdecb…`). Provider docs: an idle VM "pauses" and "can be reclaimed" (P1, P3), and running processes are "not restored" (P2). **UNKNOWN PROVIDER GUARANTEE** of no pause or reclaim in a 7-day window: none documented | no machine exists | MISSING EVIDENCE: no machine named |
| H2 supervision / M3 | **OBSERVED FAILURE**: PID 1 is `process_api`, not systemd. The campaign could run only inside an agent session (S17, MBS-3 / L6) | — | MISSING |
| H3 updates / M2 | **OBSERVED FAILURE**: kernel `6.18.44-fc-v114` earlier, `6.18.44-fc-v139` now, i.e. the provider changes the image. **UNKNOWN PROVIDER GUARANTEE** of an image freeze: none documented | — | MISSING |
| H4 exclusivity / M6 | MISSING EVIDENCE: other tenants on the hypervisor cannot be seen. **UNKNOWN PROVIDER GUARANTEE** of dedicated hardware | — | MISSING |
| H5 storage / M4 | MISSING EVIDENCE: `/dev/vda` ext4 (virtual disk). Scratch files survived the restarts in practice, but fsync honouring and reboot survival are not documented | — | MISSING |
| H6 limits / M5 | **OBSERVED FAILURE**: cgroup v1 under `/process_api/…`; no cgroup-v2 controller files readable; `systemd-detect-virt` = `docker` (a container) | — | MISSING |
| H7 operator access / M7 | MISSING: access only through the session, which itself can be reclaimed | — | MISSING |
| H8 identity / M8 | **OBSERVED FAILURE**: no DMI `product_uuid`; `/etc/machine-id` only, and a boot-id change at every restart | — | MISSING |
| ≥ 6 physical cores (proposal) | **OBSERVED FAILURE**: 4 online CPUs | — | MISSING |
| bare metal (proposal) | **OBSERVED FAILURE**: `hypervisor` CPU flag; container | — | MISSING |
| PSI (proposal) | observed present (`/proc/pressure/memory` readable) | — | MISSING |
| thermal zones (proposal) | **OBSERVED FAILURE**: 0 zones | — | MISSING |
| CPython 3.14.5 buildable (proposal) | MISSING: not attempted, since installing is not authorized; 3.14 absent | — | MISSING |

**Session host verdict:** it fails minimum criteria M1, M2, M3, M5 and M8 on observed facts. This confirms
HOST_UNSUITABLE (amendment r5 §2.1, review 59) on more evidence. No provider guarantee could cure M3 or M5: both are
facts about the machine as it is.

## 3. The recommendation

**OD-1 = V-B: one persistent, owner-controlled, single-tenant bare-metal Linux server, named by the owner, used for
this route only.**

Concretely, the owner should name **one** machine with all of these:
* x86_64, bare metal: owner-owned or a rented **dedicated** server, not a VM and not a shared host;
* ≥ 8 physical cores, so that ≥ 6 can be in the campaign unit's cpuset with headroom;
* ≥ 32 GiB RAM. The ratified provisional memory rules (MEM_CAP 3 GiB provisional; FREE_MEM_MIN ≥ 2 GiB by R-FREE)
  are far below this. The margin is for MemAvailable after the OS;
* a local NVMe or SATA SSD with ext4, persistent;
* Ubuntu 24.04 LTS installed by the owner: systemd as PID 1, no container runtime, journald `Storage=persistent`;
* readable DMI (`product_uuid`, chassis type), readable thermal zones with trip points, and PSI enabled;
* remote access for the owner (and, by the owner's choice, a Remote Control session used only **outside** the window
  of amendment erratum E1.7).

Why V-B over V-A:
* V-A runs Claude sessions on the official host, so it adds a runner that must be fully stopped for the window (FR1
  G28).
* It also needs a Team or Enterprise plan feature in public beta (P7).
* V-B needs no plan change.

Why bare metal: it removes the hypervisor-pause problem (D-PAUSE (2)) instead of replacing a measurement with a
statement (SUBST).

Why x86_64: no text prefers an architecture (FR1 F3), and readable DMI and thermal zones are common on x86_64 servers.
The choice is fixed by OD-1 and never changed after an L-DET outcome.

**What the recommendation does not claim:**
* That such a machine will pass L-DET. A different platform may not reproduce MB r1's records. A mismatch stops the
  route on that platform, with no repeat and no host shopping.
* That any provider term protects the window. Any provider term must be quoted verbatim when the machine is named.

## 4. The S12 rating and this recommendation

[Completed after the S12 review: see §6.]

## 5. Administrative actions: a proposal for the owner (none performed)

The order follows plan §3 with erratum E1: the inventory comes before the update actions.

| # | action (owner) | when | evidence produced |
|---|---|---|---|
| A1 | Decide OD-1, then name the machine (hostname, provider and contract reference, or owned-hardware record) in the owner's own record and by a committed owner statement | first | OD-1 record |
| A2 | Install Ubuntu 24.04 LTS on bare metal with systemd. Install no container runtime and no agent runner on it. Enable journald persistence (`/etc/systemd/journald.conf`: `Storage=persistent`; `/var/log/journal` present) | before the inventory | install notes |
| A3 | Give the coordinator, or the reviewed successor's inventory, read-only access to run `lx_inventory.py` unprivileged (for example a Remote Control session opened by the owner, closed again afterwards) | before the inventory | the Phase-1 inventory, committed unchanged |
| A4 | After the inventory, disable each update vector (H3) and record the date of each:<ul><li>`systemctl disable --now unattended-upgrades.service apt-daily.timer apt-daily-upgrade.timer fwupd-refresh.timer`;</li><li>`APT::Periodic::Update-Package-Lists "0"; APT::Periodic::Unattended-Upgrade "0";` in `/etc/apt/apt.conf.d/20auto-upgrades`;</li><li>`Unattended-Upgrade::Automatic-Reboot "false"`;</li><li>`snap refresh --hold` (or remove snapd);</li><li>`touch /etc/cloud/cloud-init.disabled` if cloud-init is present;</li><li>Livepatch / Ubuntu Pro disabled;</li><li>`apt-mark hold` on the running kernel's `linux-image-*`, `linux-modules-*` and `linux-headers-*` packages.</li></ul> | after the inventory, no later than the L-DET interpreter build | `auto_update_settings()` reading; the attestation `updates` field |
| A5 | Build CPython 3.14.5 from the official tarball into a dedicated prefix. Record the tarball sha256, the compiler and the flags. This happens only under the reviewed build procedure, after the successor build is approved | after the implementation-review approval of the procedure | build-provenance record and prefix manifest (L-DET erratum E1 §4) |
| A6 | Write and commit the host attestation (plan §2 fields; no self-asserted `reviewed` / `accepted`, procedure r2 §3). Appoint the acceptance reviewer and the anchor checker by name (procedure r2 §2, §5) | after A4 | attestation; appointment record |
| A7 | Schedule the one controlled reboot-survival check for H5 (part 2) | after the implementation review | H5 evidence |
| A8 | Keep the external anchor record (procedure r2 §5) | at each acceptance and before each official step | owner record |

None of A1–A8 is within this session's authority. Each needs the owner (A5 also the implementation reviewer).

## 6. Blocker

The next step, the Phase-1 inventory of the official host, is blocked on **one host fact**: no machine meeting M1–M8 is
reachable. The resolution, and the authority it needs, are in the consolidated owner package.
