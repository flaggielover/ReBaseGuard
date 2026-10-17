# Actual-host evidence plan H1–H8 — Cell-308 Cloud route r1 (preparation)

**Status: PREPARATION · PROPOSED · NOT ACCEPTED · NOT IN FORCE.** This plan specifies the inventory and attestation
evidence a **separately controlled machine** would have to supply under amendment r5 §2.2 (H1–H8). It qualifies no host,
acquires nothing, installs nothing and changes no setting. `new_target_evaluations = 0` · `cell309_activity = none`.

Requirement source: `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md` §2.2 (sha256 `d0963b11…ba933`), itself PROPOSED. Its
**[ACCEPTED]** bases are governance S6 / S17, route erratum E1 DR2, brief R2 §9 and the HOST row of route addendum A1.
Rule: an unknown is a failure; every H item is established **on the actual machine** by a Phase-1 inventory plus a
committed owner attestation accepted under `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_20261016.md`.

## 1. The current hosted session is not a candidate

Amendment r5 §2.1 classifies the Anthropic-hosted Claude session **HOST_UNSUITABLE** for the official stages (confirmed by
review 59). A read-only re-inventory taken today, `CLOUD_HOST_INVENTORY_R3_20261016.json`, is an illustration only, not
an official-host inventory. It adds this evidence:

| H item | reading on 2026-10-16 (session host) | consequence |
|---|---|---|
| H1 lifetime | the container restarted three times today. Two restarts (about 02:00Z and 02:26Z) stopped background runs; uptime at the 06:05Z reading was 211 s | not a lifetime-stable host |
| H2 supervision | PID 1 is `process_api`, not systemd | L-LAUNCH cannot pass |
| H3 updates | kernel build was `6.18.44-fc-v114` earlier in this session and `6.18.44-fc-v139` now; the provider controls the image | the owner cannot freeze updates |
| H6 limits | cgroup v1 (`memory:/process_api/…`); no cgroup v2 `memory.max` / `cpu.max` readable at `/sys/fs/cgroup`; ancestors not provable | no effective allowance |
| H8 identity | no DMI `product_uuid`; only `/etc/machine-id` (not an identity on image-cloned VMs) | no hardware-bound identity |
| other | 4 online CPUs (WORKERS 5); no power-supply entries; no thermal zones; CPython 3.14 absent | see D-WORKERS-CORES, D-POWER-ABSENT, D-THERMAL, D-INTERPRETER |

**Missing evidence for any official host: all of H1–H8.** No separately controlled machine has been identified, no
access to one exists in this session, and no provider guarantee is on record. OD-1 (V-A / V-B / V-C) is undecided.

## 2. Inventory and attestation requirements per item

Each row lists:
* the **read-only inventory** to be taken on the machine (with `lx_inventory.py`, or the reviewed successor's
  inventory, run unprivileged where possible and never changing a setting);
* the **owner attestation field** (in the committed attestation JSON);
* the **acceptance evidence** the accepting reviewer must see.

| id | requirement (r5) | read-only inventory on the machine | owner attestation field (proposed schema) | acceptance evidence | blocks |
|---|---|---|---|---|---|
| H1 | not paused, reclaimed or replaced from the designated series to the 7-day deadline | `boot_id`, uptime, `systemd-detect-virt`, DMI vendor / product, hypervisor flag in `/proc/cpuinfo`, cloud metadata presence (read only, no credentials) | `lifetime`: machine class (bare metal / dedicated VM / other), provider and contract reference, statement that no pause, live migration, reclaim or replacement occurs in the window, and who can trigger one | the owner's written statement, the provider's documented terms (quoted, with URL and retrieval time, stored verbatim), inventory showing the same identity at every step | designation, qualification, execution |
| H2 | systemd is PID 1; the campaign runs as a service outside any agent session | `/proc/1/comm`, `systemctl --version`, `systemctl show -p Version`, unit search path | `supervision`: unit names the campaign will use; statement that the campaign runs as a systemd service, not inside a Claude session | `launched_by_systemd()` passes in a synthetic dry launch of a non-science service on that machine (reviewed procedure) | L-LAUNCH |
| H3 | every update vector disabled by the owner from qualification to the deadline | `apt-config dump` (periodic / unattended / Automatic-Reboot), unit states of `apt-daily*`, `unattended-upgrades`, snapd refresh hold, cloud-init upgrade settings, livepatch status, image or AMI id where readable | `updates`: each vector with the owner action taken and the date; the token `ATTESTED_NO_IMAGE_OR_OS_CHANGE` for the provider-image half | `auto_update_settings()` shows every vector disabled, plus the attestation | L-UPD, L-PIN |
| H4 | exclusivity can be arranged (no other heavy compute, including other sessions) | process list, CPU-tick shares over the decided window (D-EXCL-WINDOW), other users / agent runners present | `exclusivity`: statement that nothing else computes on the machine in the window, including any Claude session or runner; how it is enforced | prepared-state readings meeting the decided exclusivity rule | `host_exclusive` (needs D-EXCL-WINDOW, D-ALLOW-PATHS, D-ALLOW-BASE39) |
| H5 | local disk honours fsync; the store survives a reboot of the same machine | mount table, filesystem type, device (local / network / overlay), write cache state where readable, free space | `storage`: device and filesystem; statement that it is local, persistent across reboot, and not ephemeral instance storage | durable-write tests of the reviewed implementation on that machine; one controlled reboot survival check, scheduled by the owner and taken before the designated series | L-FSYNC, L-DISK |
| H6 | the effective memory allowance is fixed and readable; no cgroup ancestor is hidden | cgroup version, the full chain of `memory.max` / `memory.high` / `memory.current` (or v1 limits), `cpu.max`, `cpuset.cpus.effective`, `pids.max`, the cgroup namespace inode against the initial one | `root_cgroup_is_real: true`, with how the owner knows it (e.g. host root namespace, no container runtime) | `memory_readings()` returns a numeric `effective_limit` only through `root_attestation()` | L-FREE, R-MEM, R-FREE |
| H7 | the operator can reach the machine to launch `resume` / `recover` | none (procedural) | `operator_access`: access path, who holds it, the expected response time within the 7-day window | owner statement | MBS-3 recovery |
| H8 | the same machine at every official step; hardware-bound identity | DMI `product_uuid` (sha256 only), `machine-id` (sha256), CPU model and count, MAC addresses (hashed), disk serials (hashed) | `machine`: `machine_id_sha256`, `product_uuid_sha256`, `hardware_bound: true` | `machine_identity()` equal at every step to the attested values | every official step |

Attestation schema (proposed): `rebaseguard.p5y.k5.newhost-cloud-r1.host-attestation.v1`. Its existing fields are
`schema`, `reviewed`, `accepted`, `machine`, `provider_image_updates`, `root_cgroup_is_real` (`lx_platform.attestation_valid`).
The new fields proposed above are `lifetime`, `supervision`, `updates`, `exclusivity`, `storage` and `operator_access`.
They are **not** in the current schema. Adding them is part of the D-HOST-LIFETIME decision and the implementation
review.

## 3. Order of taking the evidence

1. The owner decides OD-1 and names one machine. No inventory before a named machine.
2. The read-only Phase-1 inventory runs on that machine and is committed unchanged, separate from any designated
   evidence.
3. The owner performs the H3 update actions and the H5 storage choice. The campaign never changes a setting.
4. The owner writes and commits the attestation JSON.
5. An eligible reviewer accepts or rejects it (acceptance procedure), and the ledger binds the outcome.
6. The inventory is repeated, and `machine_identity()` compared, at every official step.

## 4. What cannot be prepared without the owner

* A machine (OD-1).
* Every attestation field.
* The provider's documented lifetime terms.
* A controlled reboot.
* The decisions H4 and H6 depend on.

Everything else is ready: the field list, the inventory commands, the acceptance procedure and the gate mapping.
