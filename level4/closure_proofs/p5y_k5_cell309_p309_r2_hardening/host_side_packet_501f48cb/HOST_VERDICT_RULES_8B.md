# 8b: host verdict rules (deliverable 3 of 10)

**Authority.** The rules apply r2's verdict rule (`governance/R2_HOST_REQUIREMENTS.md` §4) to the evidence of 8a.
They add no requirement, and they perform no change.

**The verdicts.** Exactly one verdict is issued at each evaluation point:
- `HOST_ACCEPTED_FOR_WORKER_TIER`
- `HOST_CHANGES_REQUIRED`
- `HOST_REJECTED`
- `HOST_AUDIT_INCOMPLETE`

## 1. Relation to r2's own terms

| this packet | r2 (`R2_HOST_REQUIREMENTS.md` §4; `R2_BOOTSTRAP.md` 8b) | meaning |
|---|---|---|
| `HOST_AUDIT_INCOMPLETE` | `HOST_SUITABILITY_PENDING` | something required is unknown, or the evidence is missing |
| `HOST_CHANGES_REQUIRED` | "HOST_SUITABLE pending bootstrap" | every requirement is met, or can be met by a listed change that needs consent (OD-R2-4, AF-1) |
| `HOST_REJECTED` | `HOST_NOT_SUITABLE` | a requirement cannot be met without a change outside the consentable list, or without changing r2's bytes |
| `HOST_ACCEPTED_FOR_WORKER_TIER` | (no r2 term; a precondition of 8d) | after the consented bootstrap, every read-only check passes as the P309 user. r2's `HOST_SUITABLE` additionally needs the 8d drill to PASS (§4), so it is **not** issued here |

## 2. Evaluation points

| point | evidence | possible verdicts |
|---|---|---|
| **8b-initial** | A-01, S-01…S-17 (`HOST_READ_ONLY_AUDIT_8A.md` §2–§3) and Part A of the 8c form | `HOST_REJECTED`, `HOST_AUDIT_INCOMPLETE`, `HOST_CHANGES_REQUIRED`. Accepted is impossible here: the P309 user, interpreter and launch privilege do not exist before 8c |
| **8b-final** | A-02a–d (§5 there), run as the P309 user after the consented bootstrap; the OD-R2-4 application check (`OD_R2_4_HOST_CHANGE_PACKET.md` §4); Parts A and B of the 8c form | all four |

**Precedence.** Evaluate every row of §3. Then:
1. if any row yields `HOST_REJECTED`, the verdict is `HOST_REJECTED`;
2. otherwise, if any row yields `HOST_AUDIT_INCOMPLETE`, the verdict is `HOST_AUDIT_INCOMPLETE`;
3. otherwise, if any row yields `HOST_CHANGES_REQUIRED`, the verdict is `HOST_CHANGES_REQUIRED`;
4. otherwise, at 8b-final only, the verdict is `HOST_ACCEPTED_FOR_WORKER_TIER`.

**Never inferred.** A field that is missing, `null` or unreadable yields `HOST_AUDIT_INCOMPLETE` for its row, never a
pass. The capabilities marked NEEDS CONTROLLED WRITE TEST (8a §4) never block 8b and never count as passed. They are
listed in the verdict record as pending, to be evidenced by 8d.

## 3. Rows (blocker → verdict → owner → OD-R2-4 → smallest change)

"Owner" says whether owner approval is needed. "OD-R2-4" names the mapping: M1–M5 are r2's consentable list; X-n are
the additional host changes `OD_R2_4_HOST_CHANGE_PACKET.md` §3 presents; AF-1 and AF-2 are message 5's conditional
items.

| id | blocker (exact condition) | verdict | owner | maps to | smallest change that would resolve it |
|---|---|---|---|---|---|
| B-01 | audit not run, did not parse, or ran other bytes than sha256 `ec9c8416…` | INCOMPLETE | no | — | run A-01 with the verified bytes |
| B-02 | Part A of the 8c form missing (no foreign roots / heavy patterns) | INCOMPLETE | no (operator data) | — | obtain Part A; re-run A-01 |
| B-03 | `pid1` ≠ `systemd` | REJECTED | yes (another host) | none | another host (a new owner record, G-1) |
| B-04 | `container.in_container` = true | REJECTED | yes | none | another host |
| B-05 | `provenance.arch` ≠ `x86_64` | REJECTED | yes | none | another host |
| B-06 | `cpu.affinity_cpus` < 4 | REJECTED | yes | none (an instance resize is outside M1–M5) | resize or replace the instance: a new owner decision; host-wide, so cell-308 consent too |
| B-07 | instance type burstable (`t2./t3./t3a./t4g.`) or unknown with IMDS available | REJECTED | yes | none | as B-06 |
| B-08 | `instance_life_cycle` = `spot`, or `spot_instance_action` non-null | REJECTED | yes | none | another (on-demand) instance |
| B-09 | `mem_total_gb` < 8 | REJECTED | yes | none | as B-06 |
| B-10 | `provenance.cloud.available` = false (no IMDS) | REJECTED for the bytes `501f48cb` | yes | **AF-2** (not OD-R2-4) | AF-2: a minimal reviewed portability proposal for `durability_preflight`. It changes r2's bytes, so 8d would no longer be on `501f48cb`, and it needs its own owner decision. Never pre-emptive |
| B-11 | `scheduled_maintenance` holds an event | INCOMPLETE | no | — | wait until the event has passed; re-run A-01 |
| B-12 | `foreign_roots.*.world_readable` = true | CHANGES_REQUIRED | yes (owner and cell-308 operator) | **AF-1** (message 3 §6 amendment) | AF-1: return with the evidence and the exact proposed amendment (e.g. restrict the checkout's mode); change nothing of cell 308 beforehand |
| B-13 | `foreign_roots.*.exists` = false | INCOMPLETE | no | — | correct the path with the operator (Part A) |
| B-14 | `foreign_roots.*.readable_by_this_user` = true while not world-readable (group or ACL access for the audit user) | INCOMPLETE at 8b-initial; at 8b-final, REJECTED unless resolved | yes | M1 (a P309 user without that group) | create the P309 user without the group. A-02c then decides |
| B-15 | no P309 user (always so at 8b-initial) | CHANGES_REQUIRED | yes | **M1** | create the P309 user |
| B-16 | a planned root has < 40 GB free, or does not exist | CHANGES_REQUIRED | yes | **M2** | a P309 volume or quota with ≥ 40 GB free (60 GB recommended) |
| B-17 | no polkit rule for `p309-r2-*` transient units (always so at 8b-initial) | CHANGES_REQUIRED | yes | **M3** | the polkit rule of OD-R2-4 M3 |
| B-17a | polkit absent (S-07) | CHANGES_REQUIRED | yes | **X-6** | install polkit (a system package) |
| B-18 | `automatic_reboot` true, `needrestart_mode` = `a`, `unattended_upgrades_active` true, or `dnf_automatic_enabled` true | CHANGES_REQUIRED | yes (owner and cell-308 operator: host-wide) | **M4** | hold reboots and upgrades for each window |
| B-19 | `reboot_required` = true | CHANGES_REQUIRED | yes (owner and cell-308 operator) | **X-1** | one agreed reboot before the window (it interrupts cell 308, so the operator's consent is needed); re-audit afterwards |
| B-20 | no P309-private CPython 3.11.15 (always so at 8b-initial) | CHANGES_REQUIRED | yes | **M5** | build or install it under the P309 home |
| B-20a | M5 needs build dependencies that are not installed | CHANGES_REQUIRED | yes | **X-7** | install the build dependencies (system packages), or a reviewed prebuilt alternative (§3 of the OD-R2-4 packet) |
| B-21 | `ntp_synchronized` false or null | CHANGES_REQUIRED | yes (host-wide) | **X-2** | enable time synchronization (e.g. `systemd-timesyncd` or chrony) |
| B-22 | `etc_hostname_sha256` ≠ `hostname_sha256` | CHANGES_REQUIRED | yes (host-wide, identity) | **X-3** | make the static and running hostnames equal (never during a window) |
| B-23 | `machine_id_sha256` null | CHANGES_REQUIRED | yes (host-wide, identity) | **X-3** | initialize `/etc/machine-id` (`systemd-machine-id-setup`) |
| B-24 | `proc.hidepid` true, or `proc.foreign_visible` = 0 | CHANGES_REQUIRED | yes (host-wide) | **X-4** | remount `/proc` without `hidepid` (or `hidepid=0`), or an exempting `gid=` for the P309 user |
| B-25 | `tools.git` < 2.32 or absent | CHANGES_REQUIRED | yes | **X-5** | a git ≥ 2.32 (system package; or a P309-private git, which r2 does not describe) |
| B-26 | `tools.systemd_run` false | CHANGES_REQUIRED | yes | **X-6** | install the package providing `systemd-run` |
| B-27 | cgroup v2 `memory`, `cpu` or `io` controller missing (S-10) | CHANGES_REQUIRED | yes (host-wide) | **X-8** | enable the controllers (kernel or boot configuration: host-wide, reboot) |
| B-28 | filesystem not in {ext4, xfs, btrfs}, or `nobarrier` (S-01) | CHANGES_REQUIRED | yes | **M2** (choose the volume) | put the P309 roots on an ext4/xfs/btrfs volume without `nobarrier` |
| B-29 | `foreign_uids` unknown, or contains the P309 user's uid | INCOMPLETE | no (operator data) | — | Part B of the 8c form |
| B-30 | load baseline not agreed (`load_baseline`) | INCOMPLETE | no (operator data) | — | Part B of the 8c form |
| B-31 | the unit limits (`memory_max`, `oom_score_adjust`, `cpu_weight`, `io_weight`) not agreed | CHANGES_REQUIRED | yes (owner and cell-308 operator) | **OD-R2-4 unit limits** | agree the values (§2 of the OD-R2-4 packet) |
| B-32 | 8b-final: A-02b (`preflight`) not PASS | per the failing check's row above | per row | per row | per row |
| B-33 | 8b-final: A-02c (`isolation`) not PASS | the failing check: `foreign_roots_unreadable` → B-12/B-14; `p309_on_r2_branch`, `p309_no_alternates`, `p309_repo_is_toplevel`, `p309_git_dir_inside_p309_repo` or `p309_config_has_no_credential` → CHANGES_REQUIRED (redo the P309 clone, a P309-files action inside M1's home; no new consent unless the remedy touches the host) | per row | M1 (home) | re-clone exactly per `R2_BOOTSTRAP.md` 8c-3 |
| B-34 | 8b-final: A-02d blockers include `gate` | INCOMPLETE (not a host fault: the moment was not quiet; SI §3) | no | — | repeat A-02d at an agreed quiet moment |
| B-35 | 8b-final: A-02d blockers include `p309_units_loaded` or `systemctl_unavailable` | INCOMPLETE | no | — | find out why. Never stop or reset a unit that is not P309's |
| B-36 | 8b-final: A-02d blockers include `launcher_not_unit_user` | INCOMPLETE | no | — | run A-02d as the unit user |
| B-37 | 8b-final: any consented change applied differently from its consent (OD-R2-4 packet §4), or any unconsented change found | REJECTED until the owner rules | yes | OD-R2-4 | report to the owner; change nothing back without instruction |
| B-38 | 8b-final: A-01 vs A-02 shows an unexplained runtime change (kernel, glibc, identity hashes) | INCOMPLETE | no | — | explain it from the bootstrap record, or re-audit |

## 4. The verdict record (one per evaluation point)

The coordinator writes `host_evidence/VERDICT_8B_<point>_<UTC>.json` into this hardening namespace:

```json
{"schema": "P309_R2_HOST_VERDICT_8B/1", "point": "initial|final", "utc": "...",
 "host": {"machine_id_sha256": "...", "hostname_sha256": "...", "instance_id_sha256": "..."},
 "evidence": {"audit_8a": "<path and sha256>", "a02": "<path and sha256, final only>", "cell308_form": "<path and sha256>"},
 "rows": {"B-01": {"state": "clear|blocker", "value": "..."}, "...": {}},
 "needs_controlled_write_test": ["R-FS-1", "R-FS-2", "R-FS-3", "R-FS-4", "R-FS-5", "R-SD-4", "R-SD-5"],
 "verdict": "HOST_ACCEPTED_FOR_WORKER_TIER|HOST_CHANGES_REQUIRED|HOST_REJECTED|HOST_AUDIT_INCOMPLETE",
 "required_owner_items": ["M1", "M3", "..."],
 "statement": "no host change was made by this evaluation; NEW Γ309 TARGET EVALUATIONS = 0"}
```

## 5. What each verdict permits

| verdict | next step |
|---|---|
| `HOST_AUDIT_INCOMPLETE` | collect the missing evidence and re-evaluate. No host change |
| `HOST_CHANGES_REQUIRED` (8b-initial) | owner return **R-1**: the OD-R2-4 packet, filled with the exact current states, plus AF-1 if B-12. **STOP** until the owner has answered. Nothing is changed before consent |
| `HOST_CHANGES_REQUIRED` (8b-final) | the same, for the remaining items |
| `HOST_REJECTED` | owner return **R-1** with the blocker. No change and no drill on this host |
| `HOST_ACCEPTED_FOR_WORKER_TIER` | the 8d drill may be **prepared**, and run only when every precondition in `WORKER_TIER_DRILL_8D.md` §1 holds (window, Part C of the 8c form, the pre-launch check) |
