# Erratum E1 to the consolidated D-* package r2 (Cell-308 Cloud route r1) — after FR2 and S12

**Status: PROPOSED · ADVICE TO THE OWNER · NOTHING DECIDED.** This erratum corrects
`CONSOLIDATED_DSTAR_PACKAGE_R2_20261016.md` (`038278fe…e5f`), which is preserved unchanged.

Its sources:
* FR2 (`1ad769bb…8cac`): K12, K13;
* S12 (`9d549eb2…b55c`): S2, S7, S8, S11.

`DECIDED` stays empty. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. Rows replaced

| # | id | replacement (PROPOSED) |
|---|---|---|
| 12 | D-PAUSE | Bare metal is required. **The attestation fallback is withdrawn**, so no SUBST remains for (2). (1) and (3) are unchanged |
| 17 | D-CAPS-CPU | **Owner MBS-8 choice, recorded before OD-1** (amendment erratum E2.5), with no new-host runtime, inventory reading or Q12 result in view. The input "Q12's result under option (i) on that host" is **deleted**. Recommended: **(ii)**. The caps are re-derived by the accepted §3.2 rule from official decoy runtimes on the named host (non-holder, decoys only), with no further choice after the runtimes exist. L-DET runtimes stay excluded |
| 18 | D-TEXT-LAUNCHD | As r2, **plus** the brief R2 §9 launch row "only under the launchd launcher" (bR2 line 420), which amendment r5 listed (FR2 K12) |
| 20 | D-S15-NEWHOST | As r2 (a)–(e), with three changes: <ul><li>(b) The owner's listing for each step is committed at `ledger/owner/S15_REF_LISTING_<step>_<utc>.txt`, carrying the step id, the step's commit and the UTC time, so that preflight can read it. The owner's record holds its sha256 and is the evidence (FR2 K13).</li><li>(b′) A **first listing is committed and anchored before OD-3**. Every later listing must equal it, except for this route's own marker (amendment erratum E2.6) (S12 S7).</li><li>(e) stays SUBST.</li></ul> |
| — | H8 identity | **DMI `product_uuid` is required. No owner-attestation substitute** (S12 S7). A machine without a readable `product_uuid` fails M8 |

## 2. Lists replaced (FR2 K12; S12 S7)

**Owner statements that stand in for measurements (SUBST). Each is listed with its measured cross-check:**

| statement | measured cross-check |
|---|---|
| D-LPM, no-interface case | the inventory shows no `platform_profile`, cpufreq or EPP interface |
| D-POWER-ABSENT mains supply | no supply entries plus a non-portable DMI chassis type; a boot-id change at every step ⇒ CONSUMED_INTERRUPTED |
| D-S15-NEWHOST (b) listing and (e) store state | the listing equals the pre-OD-3 anchored listing; none for (e) |
| H1 lifetime (no pause, reclaim or replacement) | bare metal (`systemd-detect-virt` = none, no `hypervisor` flag); boot id and uptime at every step |
| H2 supervision statement | `launched_by_systemd()` live reading (P2 evidence) |
| H3 `ATTESTED_NO_IMAGE_OR_OS_CHANGE` | `auto_update_settings()`; L-PIN equal at every step |
| H4 exclusivity arrangement | `host_exclusive` at every step |
| H5 storage statement | durable-write tests and the reboot-survival check (P2 evidence) |
| H6 `root_cgroup_is_real` | initial cgroup namespace; no container runtime in the inventory |
| H7 operator access | none (procedural). The binding response time of procedure r3 §5 applies |
| the external anchor record | none (it is the owner's record by design) |

**Rules for which ROUTE_PREPARATION line 19 must be expressly set aside:**
* D-MEM-FREE;
* D-MEM-WIRED;
* D-MEM-PRESSURE;
* D-THERMAL;
* D-LPM;
* D-EXCL-WINDOW;
* D-ALLOW-PATHS;
* D-ALLOW-BASE39;
* **D-PAUSE (1)** (ratification item 4, the EVAL_CAP clock);
* **D-POWER-ABSENT** (the prepared-state AC condition of R-FREE attainability);
* **D-TEXT-LAUNCHD** (R-MEM step 1 inputs; the timeouts of ratification items 30–31).

## 3. New-constant provenance trace (S12 S8)

Every number or rule this route introduces, with its target-free origin. The trace was compiled by the coordinator,
who is a self-declared non-holder. **An M1-style check by a non-holder appointed by the owner is still required**
before the owner decides the D-* items, together with a ruling on whether T6's M1–M6 mitigations transfer.

| constant / rule | value | origin (target-free) | free choice? |
|---|---|---|---|
| exclusivity window (D-EXCL-WINDOW) | 30 s | R-FREE's prepared-reading cadence (ratification R-FREE, "30 s apart") | no, copied |
| PSI readings (D-MEM-PRESSURE) | N = 3, 30 s apart | R-FREE's "3 consecutive" readings and its cadence | no, copied |
| PSI field and level | `some avg10` = `0.00` | `avg10` is PSI's shortest window. `0.00` is the only reading that means "no stall", the Linux analogue of macOS pressure level 1 (normal) in ratification row 24 | interpretive; the level is fixed by the analogy |
| start-gate re-reads (amendment erratum E1.5) | ≤ 3 | **no derivation**: a coordinator choice made to bound the re-read | **yes**. Flagged for the non-holder check. A smaller bound is stricter |
| physical cores (D-WORKERS-CORES) | ≥ 6 | ratification item 15 (WORKERS 5 on 6 cores, one spare) | no, copied |
| thermal rule (D-THERMAL) | the lowest trip of any type | structural, no number | no number |
| HOST-row conditions (amendment erratum E1.2) | four | the RC2 pins (route A1 §1), MBR1_REPRO (route A1 §3), route E1 DR2 | no |
| window bound (amendment erratum E2.7) | owner number before the Phase-1 inventory | not yet chosen | yes, owner |
| H7 / anchor response time (procedure r3 §5) | owner number before the Phase-1 inventory | not yet chosen | yes, owner |
| MBS-8 (ii) caps | by the §3.2 rule | accepted rule; values from decoys only | no choice after the rule is fixed |
| comparator digit limit (L-DET erratum E1 §2) | `sys.set_int_max_str_digits(0)` | avoids a spurious INCOMPLETE; changes no comparison | technical, no threshold |

**Timing (S12 S11).** All 21 D-* items are decided **before the Phase-1 inventory** of the named machine (amendment
erratum E2.5). The two owner numbers are fixed at the same time, with no new-host reading in view.
