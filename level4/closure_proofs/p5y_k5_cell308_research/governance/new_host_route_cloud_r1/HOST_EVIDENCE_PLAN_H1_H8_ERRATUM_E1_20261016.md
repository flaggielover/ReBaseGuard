# Erratum E1 to the H1–H8 host evidence plan, with the reviewed host-selection criteria (Cell-308 Cloud route r1)

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** This erratum corrects `HOST_EVIDENCE_PLAN_H1_H8_20261016.md` (sha256
`901a05d7…4ec8`), which is preserved unchanged. Its source is the formal route review FR1
(`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md`, sha256 `af150ef4…b6df`): F3, G5, G11, G15, G28 and G32. It qualifies
no host. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. Host-selection criteria, classed by FR1 F3

The criteria below are **reviewed** in the sense that FR1 classed each one against accepted text. Classing them is
not an acceptance. Accepted-in-substance criteria still carry proposed means. **Proposals stay proposals** until the
owner decides the named D-* item.

### 1.1 Minimum before an inventory is worth taking (from accepted text; a "no" on any one ends the candidate)

| # | criterion | accepted basis (FR1 F3) | proposed means (not accepted) |
|---|---|---|---|
| M1 | one persistent machine under the owner's control, not a provider-managed session image | route A1 HOST row; brief R2 §9 host row ("this host only") | — |
| M2 | the owner can disable every update vector, including image changes and automatic reboot, from the L-DET interpreter build to the 7-day deadline | route E1 DR2 | H3's vector list; the window start (G5) |
| M3 | a launcher that survives the death of the hosting app and its parent; the campaign runs with no agent session on the machine during the window | governance S6; S17; MBS-3 / route E2 L6 | systemd as PID 1 with the campaign as a service (H2); the no-session window (G28) |
| M4 | durable, fsync-honouring local persistence that survives a reboot of the same machine | governance S6 | the reboot-survival check (H5) |
| M5 | a memory allowance that is the machine's own and readable for R-MEM / R-FREE | ratification R-MEM, R-FREE | no container runtime; the initial cgroup namespace; no hidden ancestor (H6) |
| M6 | exclusivity can be arranged: no other heavy compute, including other sessions | governance A1 S17 | the D-EXCL-WINDOW reading |
| M7 | operator access to launch `resume` / `recover` within the 7-day window | ratification items 18, 19 | — |
| M8 | one machine at every step, with a hardware-bound identity or a stated substitute | route A1 HOST row | DMI `product_uuid` (H8) |

### 1.2 Proposal-level preferences (each depends on an open D-* decision)

| criterion | D-* item | class |
|---|---|---|
| ≥ 6 physical cores in the unit's effective cpuset | D-WORKERS-CORES | proposal (new host requirement) |
| bare metal (no hypervisor pause) | D-PAUSE | proposal |
| PSI enabled | D-MEM-PRESSURE | proposal |
| readable thermal zones with trip points | D-THERMAL | proposal |
| CPython 3.14.5 builds from source on the host's toolchain | D-INTERPRETER | proposal / host fact |
| owner reachability for the anchor check at every official step | D-HOST-LIFETIME (procedure r2 §5) | proposal |

**Architecture** (x86_64 or arm64) is not a criterion in any text (FR1 F3). It is fixed by OD-1 and never changed after
an L-DET outcome.

## 2. Corrections to the plan

* **G5 (windows).** In §2 rows H1, H3 and H8, the window is "from the interpreter build for L-DET to the 7-day
  deadline", as amendment erratum E1.4.
* **G11 (split acceptance).** §3 step 5 becomes two steps:
  * acceptance part 1 (H1, H3, H6, H7, H8) after the inventory and the owner's H3 actions;
  * acceptance part 2 (H2, H5) after the implementation review, before OD-3, with the evidence named in the plan's H2
    and H5 rows (procedure r2 §4).
* **G28 (V-A).** Add to H4: "no agent session (including a self-hosted Claude runner's sessions) runs on the machine
  from the L-DET interpreter build to the seal".
* **G15.** Rows that say "online CPUs" read "physical cores in the unit's effective cpuset".
* **G32 (restart count, reconciled).** The session host's restarts on 2026-10-16, from boot ids and uptime readings
  only:

| restart | evidence |
|---|---|
| about 02:00Z | stopped a background run (ledger) |
| about 02:26Z | stopped a background run (ledger) |
| 06:01:44Z ± 1 s | boot `fdbfb93e…`, uptime 211.26 s at the 06:05:15Z inventory r3 reading |
| 06:23:11Z ± 1 s | boot `7bccdecb…`, uptime 1690.34 s at a 06:51:21Z reading |

  That is **four** restarts. The inventory's `observed_in_this_session` field lists only the two that stopped
  background work, and the plan's "three" counted up to the 06:05Z reading. Both earlier files stay unchanged. The
  same readings show the root filesystem `/dev/vda` ext4 and `systemd-detect-virt` = `docker`. These session-host
  facts strengthen HOST_UNSUITABLE. They are no evidence about any other machine.
