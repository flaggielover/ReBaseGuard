# P5Y K1 SR PS1 — PORTABLE RECOVERY SUCCESSOR (PRE-RESULT, NO GENUINE PRODUCTION)

Additive governed successor repairing **execution/lifecycle persistence only**.
Genuine production cells produced by this round: **0**. Nothing historical is modified.

## A. Forensic root cause (established, not inferred)

`HOST_OR_SYSTEMD_INFRASTRUCTURE_EVENT`. On 2026-09-12 `apt-daily-upgrade.service` ran
unattended-upgrades; systemd `255.4-1ubuntu8.17` was re-executed
(`Reexecuting requested from client PID 256457 ('systemctl')` at 06:01:50.951), and the
resulting service restart cascade stopped/restarted the transient production unit at
**06:01:57.767** and **06:02:07.853**. `sshd` took signal 15, journald/chrony/polkit/snapd/
udevd/resolved all cycled — the unit was collateral, not targeted.

Ruled out: OOM (`dmesg` oom-kill count 0), disk pressure, operator/agent stop (last login
05:42:23–05:42:43; no privileged `systemctl stop` in auth.log), scientific failure,
lifecycle defect. The third tear was the sanctioned operator cost stop at 09:58:15Z.

## B. Phase A gate — CELL_LEVEL_FINALIZATION_IS_EXECUTION_ONLY = YES

**Structural**: `succ_t3_aggregate.aggregate()` strips `cpu_seconds`, `peak_rss_kib`,
`cache_hits`, `cache_misses` from every record before `consumed_records_sha256` /
`t3_record_sha256`. Those four are the only values loop order or cache warmth can touch.

**Empirical (metadata scramble)**: identical cell-0 records with those four fields
randomised, aggregated from different directories — `consumed_records_sha256`,
`t3_record_sha256`, `t4_record_sha256`, all 28 t5 certificate hashes, `B_cover_ratio`
and `scientific_content_hash` all identical. Evidence is **location-independent**.

**Empirical (real computation)**: the same 12 live patches for cells [0,1,2,3] through the
same frozen `opt_core.core` under both orderings — **48/48 stripped records bit-identical**,
bundle sha256 `a42d0a95aa07cb1bf4e9cda4a06ae92ee004ada45c898191b2a689958b9510ae` on both sides.

## C. The structural trade-off

Under patch-outer/cells-inner no cell reaches a finalization boundary until all four do
(~50 h). Per-cell durability therefore **requires** cells-outer, which forfeits the
cross-cell cache. Measured: `cache_hits` 1,098 → 0; CPU **1.2265×** (+22.6%).

| | granularity | per cell | campaign |
|---|---|---|---|
| predecessor patch-outer | ~50 h, all-or-nothing | 12.58 | 4,642 CPU-h |
| successor cells-outer | **~15 h, per cell** | 15.43 | **5,694 CPU-h** |

Cap 6,600 → headroom 906 CPU-h. ~24.9 finalized cells/24 h on 16 workers; ~14.8 days.
`cells_per_group` remains a governed parameter for trading durability back for cost.

## D. Retry taxonomy (generation 2)

`SCIENTIFIC_FAILURE` halts, never retried (inherited). `INFRASTRUCTURE_TEAR` bounded at 3
per cell. `OPERATOR_EMERGENCY_STOP` tears only in-flight cells. **`GRACEFUL_DRAIN` is not a
tear** and never increments `torn_attempts`. Generation-1 counters (cells 0–63 = 3) remain
visible forever and are not reset.

## E. Acceptance — 12/12 pass, synthetic only

Phase K tests 1–10 plus identity-drift and domain-completeness fail-closed tests.

## F. Host maintenance

`driver/host_guard.py` fails closed when a disruptive timer fires inside the declared
window. Live: `apt-daily.timer` 2026-09-12T23:14:17Z, `apt-daily-upgrade.timer`
2026-09-13T06:42:02Z → a 24 h window is **UNSAFE**. Mitigation templates take their
privilege prefix from the frozen contract; the operator applies them.

## G. Not done

Launcher integration (`production_launcher` per-cell seal wiring) and the live systemd
drain/resume acceptance are NOT complete. **GENUINE_PRODUCTION_RELAUNCHED = NO.**
