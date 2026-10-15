# Review — DELTA of revision 4 and amendment r4 after review 61 (Cell 308, MB-S successor, S4 changed branch, Cloud route r1)

* Reviewer: **reviewCLOUD_R1_DELTA3 (fresh agent, brief 62)**
* Date: 2026-10-15 (UTC). The session ran from about 00:27Z to about 00:46Z, with no interruption.
* Delta reviewed: **d423c7aa..cd86c326** (HEAD = `cd86c326b573c631749585a46638674e6d8417f4`) on branch
  `claude/cell-308-github-state-skb1g0`.
  * The delta has five commits: fbe47168 (review 61 recorded), e76a4ea0 (revision 4, amendment r4, owner brief r4),
    0e69bdce (brief 62), 54f6cf62 (the test that kills P08) and cd86c326 (MUTANTS_RUN plus ledger line 471).
  * `git status --porcelain` was empty at the start and at the end.
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`. Paths are relative to NS unless stated otherwise. Line numbers
  refer to the HEAD files.
* `new_target_evaluations = 0`. I ran no cell, drift, certificate, decoy, science module, qualification case, candidate
  code or quarantine guard. I installed nothing, changed no setting and wrote no repository file.
* Scratch directory: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review62/`
  ("scratch" below). The probes ran against a copy of `lx_platform.py` in `scratch/base/`, sha256 `90362161…`, which
  equals HEAD.

---

## 1. Exposure disclosure

**Files opened in full:**
* Review 61 (`reviews/REVIEW_CLOUD_R1_DELTA_R3.md`).
* At HEAD:
  * `lx_platform.py`;
  * the `git diff d423c7aa..HEAD` of `lx_platform.py`, `tests/test_lx_platform.py`, `tests/run_mutants.py`,
    `README_DEV_ONLY.md` and `results/TEST_RUN.json`;
  * `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4.md` and `OWNER_DECISION_BRIEF_CLOUD_R1_R4.md`;
  * `diff` of amendment r3 against r4, and of owner brief r3 against r4;
  * ledger lines 467–471 and the added BRIEF_INDEX row;
  * `ledger/briefs/62_reviewCLOUD_R1_DELTA3.txt`.
* Review 61's scratch scripts `probes61`, `quotecheck61`, `ns_probe61`, `ns_probe61b`, `preexisting61`,
  `probe_zombie_leader`, the head and tail of `reviewer61_mutants`, and `q60.txt`.

**Read programmatically only:**
* `quotecheck62.py` (a copy of review 61's checker, pointed at r4) read these files for substring matching:
  * `governance/SUCCESSOR_GOVERNANCE_308*.md`, `governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md`;
  * `governance/CONSTANTS_RATIFICATION_MBS308.md`, `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1*.md`;
  * `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`, `governance/new_host_route_cloud_r1/ROUTE_PREPARATION.md`.
* `grep -c` on review 61's stored fetch `fetched/self-hosted-environments.html`, for the V-A quotation.

**Candidate:** `git show 142d97a9:…/p5y_k5_cell308_mbs_r1/code/mbs308_host.py`. I read only lines 583–600
(`preflight_gates`) and a grep for `other_job_running`. The suite itself reads two constants from that file.

**Host (read-only):**
* `/proc/1/comm`, `/proc/self/cgroup`, the namespace inodes, `boot_id` and interpreter versions;
* `systemctl --version`, and `systemctl is-enabled` for `nonexistent-review62-xyz.service`,
  `apt-daily-upgrade.timer` and `unattended-upgrades.service`. These are read-only queries;
* `git rev-parse --is-shallow-repository`, which returned `true`.

**Namespaces:** `unshare` ran four times, once each with no flags, `--cgroup`, `--pid --fork --mount-proc` and
`--pid --fork --mount-proc` again (for `ns_probe62b`). Each run read only the scratch copy, and each namespace ended with
its process.

**Not opened, grepped or read:**
* `audit/EXECUTION_INTERRUPTION_ASSESSMENT*` and `audit/INCIDENT_AUDIT*`;
* `reviews/REVIEW_EXECUTION_INTERRUPTION*`;
* anything under `p5y_k5_cell308_mb_r1/postexec/`, or any MB r1 target-run record;
* `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`;
* any Cell-309 branch, file or record. I ran no `git branch -a`.

**Name-level contact only:**
* A listing of the session scratchpad root showed the coordinator's files `MUTANTS_RUN_R3.json`,
  `MUTANTS_RUN_R4.json`, `MUTANTS_RUN_R4b.json`, `gate.txt`, `inv_check.json`, `mut2.log`, `mut3.log` and
  `scan*.json`, and the directories `review59`, `review60` and `review61`. None of these files was opened.
* I hashed `scratchpad/review61/REVIEW_CLOUD_R1_DELTA_R3.md` and review 61's original scratch files, to compare them with
  the recorded copies. I did not read them.

I hold no E1″ material and no MB r1 target-run runtime or host observation.

---

## 2. Verdicts

DELTA: DELTA_ACCEPTED_WITH_CONDITIONS
AMENDMENT_DRAFT_R4: FIT_WITH_CONDITIONS
DEV_CODE_R4: FAIL_CLOSED_WITH_DEFECTS

**No verdict here accepts the amendment.** Only three things can accept, reject or put it into force:
* a formal independent route / governance review;
* a fresh S12 incident-independence re-rating;
* the owner's decisions (OD-1 to OD-3 and the [OPEN] items).

This is a delta review of a draft and of a development layer.

**Why each verdict:**

### DEV_CODE_R4 = FAIL_CLOSED_WITH_DEFECTS

Not CONFIRMED and not NOT_FAIL_CLOSED.

**Closed in revision 4.** Every caller-asserted path that review 61 demonstrated is now closed. I re-probed each one on
the copy (`probes62_out.json`, `ns_probe62_out.txt`):
* B1 self-designation;
* B2 `decided` (a str, set, list or unknown id raises ValueError);
* B3 a forged launch record (FAIL in both execute and launcher mode);
* B4 a malformed record (UNKNOWN);
* B5 `[]` for L′ (AMBIGUOUS);
* B6 a timer in a second root;
* B7 under `unshare --cgroup`: no number, even with `DECIDED` and a valid attestation injected;
* B8 an empty or undefined pin list (raises).

**Defects that remain:**
* The new acceptance mechanism accepts any `REVIEW_HOST_ATTESTATION_*` file in **any subdirectory** of `reviews/`,
  which includes the reviewer scratch directories (G1). Its "different commit" rule binds the commit that first added the
  path, not the accepted bytes or the accepting text (G2).
* `preflight(readings=…)` still lets a caller turn `ac_power` from OPEN_DECISION (this host: `ABSENT`) into **PASS**,
  contrary to revision 4's own claim that "test seams are module attributes … not production parameters" (G5).
* `busy_processes` treats an **omitted** `view_complete` as a complete /proc view. Live, in a nested PID namespace that
  sees one process, it returns `[]` (G6). This is pre-existing.
* Update-unit detection reads a timer that is "disabled" but active, a dangling `.wants` link, and units in unlisted
  roots as **not enabled** (G7).
* **5 of my 11 mutants survive with a demonstrated change of outcome.** Two more survive but are equivalent (G4, §7).

**Why "with defects" and not NOT_FAIL_CLOSED:**
* No failed or unreadable reading passes.
* `preflight` still cannot pass, because five gates are hard-wired OPEN_DECISION and D-HOST-LIFETIME is open in the
  shipped `DECIDED`.
* Each acceptance path needs `DECIDED ∋ D-HOST-LIFETIME`, which is now a reviewed code constant, not a caller argument.

### AMENDMENT_DRAFT_R4 = FIT_WITH_CONDITIONS

**Done in r4:**
* §4 has 21 rows, each labelled.
* The acceptance mechanism is labelled a **new rule** in both L-LIFE and D-HOST-LIFETIME.
* D-HOST-LIFETIME now says OPEN_DECISION.
* L-SLEEP, L-LAUNCH and L-FREE now match the code.
* Every [ACCEPTED] quotation is verbatim, and r4 adds no new [ACCEPTED] quotation.

**Still wrong:**
* L-UPD claims "**every** unit root"; the code searches 4 (G7).
* L-EXCL's "no reading" for a non-initial namespace holds only if the caller passes `view_complete` (G6).
* L-PIN says "a fixed list", but `pin_point(modules)` accepts any non-empty caller list (G8).
* L-LIFE does not say that subdirectories count (G1).
* H6 still names `root_attested`, and §11 cites three test names that no longer exist (G10).

### DELTA = DELTA_ACCEPTED_WITH_CONDITIONS

* P2, P4, P5, P6, P7, P9, P10 and P12 are resolved. P1, P3, P8, P11 and P13 are partially resolved (§3).
* The records check out:
  * every bound hash recomputes;
  * a fresh harness run reproduces `MUTANTS_RUN.json` mutant by mutant (89/89);
  * a fresh suite run reproduces TEST_RUN (83 OK on 3.11.17, 3.12.3 and 3.13.16);
  * r1–r3, the r1–r3 owner briefs and reviews 59–61 are byte-unchanged;
  * review 61 and its scratch were recorded byte-identical to the originals.
* Conditions are in §6 (E1–E4).

---

## 3. Q1 — Status of review 61's findings and conditions

| item | sev (r61) | status | evidence |
|---|---|---|---|
| P1 | MAJOR | **PARTIALLY RESOLVED** | **Resolved:** <br>• The attestation can no longer name its acceptance record. `acceptance_record` is ignored, and `_acceptances` (`:993–1011`) scans a fixed directory and prefix (`:74–76`). <br>• Review 61's three B1 cases are all refused (`B1_self_acceptance[*]`). <br>• An exact verdict line is required. <br>• A literal `REJECTED` in a file that names the sha refuses. <br>• Y03 is killed. <br>• The mechanism is named a new rule (L-LIFE, D-HOST-LIFETIME). <br>• Test: `test_acceptance_is_found_not_named`. <br>**Not resolved:** <br>• The "fixed set" is recursive: `ls-tree -r` of `reviews/` plus a basename check (`:998–1002`). A `reviews/scratch_ANY/REVIEW_HOST_ATTESTATION_note.txt` is **valid** (G1 probe). That is review 61's "scratch note" case under a new name. <br>• "Refuse an acceptance record written in the same commit as the attestation" can be bypassed three ways (G2, G3; the Z05 equivalence probe), each **valid**: <br>&nbsp;&nbsp;– add a placeholder review, then write the acceptance in the attestation's commit; <br>&nbsp;&nbsp;– add a placeholder attestation path, then write the attested bytes and the acceptance together; <br>&nbsp;&nbsp;– write the acceptance with the attestation outside the set, then `git mv` it in. <br>• An acceptance committed **before** the attestation exists is valid (G4). <br>• "Refuse any record that also carries a REJECTED verdict" recognises only the literal upper-case token, and only inside prefix-named files. Lower-case "rejected", `…_NOT_ACCEPTED`, "WITHDRAWN", or a `REJECTED` review outside the prefix are all ignored (G5, G6). <br>• Nothing ties an acceptance to a ledger REVIEW line or a reviewer identity. |
| P2 | MAJOR | **RESOLVED** | `root_attestation` (`:537–550`) is called inside `memory_readings` (`:559`), and `root_attested` is no longer a parameter (passing it raises TypeError). Live evidence (`ns_probe62_out.txt`), with `DECIDED={D-HOST-LIFETIME}` and a valid attestation **injected** on the copy: <br>• initial namespace: `effective_limit` = 14 343 688 192, the true leaf limit; <br>• `unshare --cgroup`: `root_attestation` = `[false, ["cgroup namespace not the initial one, or unreadable"]]` and `effective_limit` = `null`. <br>Y04 and P05 are killed, and so is my Z08 (non-initial passes). The residual reader seams are G-NOTE material only (G14 probe; §5 G11). |
| P3 | MAJOR | **PARTIALLY RESOLVED** | **Now true of the code:** <br>• L-SLEEP: "L′ is AMBIGUOUS whatever the caller passes"; <br>• L-LAUNCH: fresh reading and equality, int MainPID; <br>• L-FREE: no caller flag, non-initial namespace blocks; <br>• L-ID: shape check; <br>• D-HOST-LIFETIME: "gates `OPEN_DECISION`". <br>**Still not exact (G6, G7, G8, G1, G10):** <br>• L-UPD "from **every** unit root"; <br>• L-EXCL "a reader outside the initial PID namespace … ⇒ no reading" (true only if the caller supplies `view_complete`); <br>• L-PIN "requires every module of a fixed list"; <br>• L-LIFE omits subdirectories; <br>• H6 "attestation `root_attested`". |
| P4 | MAJOR | **RESOLVED** (as specified) | Y01–Y09 are at `run_mutants.py:170–193`. I checked each re-anchoring by eye against `reviewer61_mutants.py`; each keeps the same weakening. My fresh run killed Y 9/9, with the 89 pairs identical to `MUTANTS_RUN.json`. The new revision-4 properties are again not all pinned: 5 of my 11 survive with a shown change of outcome (G4). |
| P5 | MINOR | **RESOLVED** | `preflight` has no `decided` or `attestation_check` parameter (B2c: the parameters are `repo_path, mode, other_job_running, launched, attestation_ref, readings`). <br>`_decided()` (`:1064–1068`) raises on a str, set, list or unknown id (B2). With `DECIDED` = all ten ids, five gates stay OPEN_DECISION (B2b), and the docstring now names only the two lifetime gates. Tests `test_no_trust_parameters_in_production` and `test_decided_is_validated`; P07 is killed. |
| P6 | MINOR | **RESOLVED** | `:1122–1126`: a fresh `launched_by_systemd()` reading, then `launch_record_ok(fresh)`, then equality with any passed record. Probe results: <br>• B3: a forged record gives FAIL in execute **and** in launcher mode; <br>• no record in execute mode gives FAIL; <br>• a float MainPID is refused. <br>P08, P09 and my Z09 are killed. P08 survived the first revision-4 run (disclosed in ledger 471). |
| P7 | MINOR | **RESOLVED** | `JOURNAL_READER_REVIEWED = False` (`:72`, `:294–295`). B5: both `[]` and `None` give AMBIGUOUS. Test `test_no_reviewed_journal_reader_never_clean`; P10 is killed. |
| P8 | MINOR | **PARTIALLY RESOLVED** | `unit_enabled` (`:688–714`) uses `systemctl is-enabled` when systemd is PID 1, and otherwise scans 4 roots. B6 (enabled in a second root) is now not "shown disabled". `unattended-upgrades.service` is added. **Gaps (G7, G9):** <br>• "disabled" but **active** (pulled in by `Wants=` or started at runtime) gives False; <br>• a dangling `.wants` link gives False (systemd adds the dependency by link name); <br>• `/usr/local/lib/systemd/system`, the `*.control`, `transient` and `generator*` roots are never read; <br>• "not-found" gives None, so the gate is unattainable when the package is absent (G9, NOTE). <br>Z02, Z03, Z04 and Z07 survive. |
| P9 | NOTE | **RESOLVED** | `_ident_shape_ok` (`:179–195`). B4: a garbage, truncated or upper-case boot id, and a negative, str, float or bool pid, all give UNKNOWN. Test `test_malformed_records_prove_nothing`; P14 is killed. Gap: a bool starttime or inode is not pinned by a test (Z11 survives; G4). |
| P10 | NOTE | **RESOLVED** | D-EXCL-WINDOW and D-POWER-ABSENT state the consequences (amendment lines 140, 143). The three live tests skip or branch on the host facts they assume (`test_live_host_is_never_clean`, `test_r1_recorded_kernel_is_not_this_hosts`, `test_live_snapshot`). |
| P11 | NOTE | **PARTIALLY RESOLVED** | `PIN_POINT_MODULES = None`; `pin_point()` and `pin_point(())` raise (B8); the D-PIN-POINT row exists. **Not resolved:** `pin_point(modules)` still takes the list from the caller and overrides the constant. `pin_point(("sys",))` returns a pin (B8), so the list is not "fixed" (G8). |
| P12 | MINOR | **RESOLVED** | Owner brief r4 OD-2 (line 40) names "amendment r4". The r3 brief is byte-unchanged (sha256 `3291feb1…`, equal to ledger 469). |
| P13 | NOTE | **RESOLVED** (the listed items) | Ledger 471 `p13_record_corrections` covers: <br>• 74 → 75 tests; <br>• N01–N12 → N14; <br>• the line-1 "revision 2" docstrings, now "revision 4"; <br>• the stale §10 test citation; <br>• M25's initial survival; <br>• the V-A fetch location; <br>• P08's initial survival. <br>The docstrings and §10 are corrected at HEAD. New wording errors of the same kind are listed in G10. |
| D1 | condition | **RESOLVED** (honoured) | Amendment §3 preamble (lines 88–90) and the README cite revision 4's L-FREE / L-LIFE / L-UPD / L-LAUNCH / L-SLEEP repairs "only after a fresh delta review of revision 4". Deviation: the preamble drops D1's qualifier "(with P4/Y06 and P11 open)" from L-PIN (G10). For what may be cited now, see E1. |
| D2 | condition | **PARTIALLY RESOLVED** | The four §3 rows and the D-HOST-LIFETIME row are corrected, and the mechanism is named. New inexact rows: L-UPD, L-EXCL, L-PIN and L-LIFE (P3 above). |
| D3 | condition | **RESOLVED** | See P12. |
| D4 | condition | **RESOLVED** | Ledger 471 `p13_record_corrections`, including "mutant M25 survived the first revision-3 run (64/65)". Line 471 is a new line, and 467–469 are unedited (numstat +2/−0). |

**Tally (P1–P13):**
* RESOLVED: 8 (P2, P4, P5, P6, P7, P9, P10, P12), plus P13 for its listed items.
* PARTIALLY RESOLVED: 4 (P1, P3, P8, P11).
* NOT RESOLVED: 0.

Conditions: D1, D3 and D4 resolved; D2 partial.

---

## 4. Answers Q2–Q5

### Q2 — Fail-closed audit of revision 4 (adversarial)

**Re-run of review 61's probes.** These are review 61's part A and B1–B10, ported to the revision-4 API. Trust inputs
are changed only by patching module attributes of the copy. Script `scratch/probes62.py`, output `probes62_out.json`.

* **Part A** (reviews 59 and 60):
  * power: an unreadable battery type gives None; a UPS discharging gives BATTERY; `Unknown`, `garbage`, `discharging`,
    `"Discharging \x00"`, `""` and a status directory give None; `Not charging` and `Full` give AC;
  * the update gate is UNKNOWN for `{}`, `None` and `"true"`;
  * a committed attestation with `"REJECTED"`, `"no"`/`"false"` or `1` is refused;
  * a forged dict reference is refused, and README as a reference is refused;
  * N6: the boot-id gate is UNKNOWN for all five bad values;
  * `launched=True` in launcher mode gives FAIL;
  * `attestation_ref` = True, "yes", 1 or a dict gives no number;
  * a newborn hog is reported; `own ∋ pid 1` gives None; a hog that exits is reported; an unreadable pid gives None;
  * N8 ESRCH with unrecorded namespaces gives UNKNOWN;
  * a zombie with a full record gives UNKNOWN;
  * a `(deleted)` libm mapping gives None.
* **B1–B10:** all closed, as listed in §2. B10 `own={("99", 1)}`: the str key is not matched and the child is charged,
  which is fail-closed.
* **Zombie probe (review 59 P6), re-run unchanged on the copy** (`probe_zombie_leader_rev4_out.json`): the leader is in
  `Z` with `Threads: 2`, ticks rise 87→137→187→236, and `identity_state` is **UNKNOWN** on all four readings.
* **`unshare` probes** (`ns_probe62_out.txt`, `ns_probe62b_out.txt`):
  * `--cgroup`: see P2.
  * `--pid --fork --mount-proc`: `proc_view_complete() == False`, and `cpu_ticks` sees 1 process.
  * `busy_processes(a, b, …)` with `view_complete` **omitted** returns **`[]`**, meaning no busy process. With
    `view_complete=proc_view_complete()` it returns None (G6).

**New adversarial probes (part G):**

| # | input class | result | finding |
|---|---|---|---|
| G1 | acceptance file at `reviews/scratch_ANY/REVIEW_HOST_ATTESTATION_note.txt` | `attestation_valid` **valid** | G1 |
| G2 | placeholder review added first, then acceptance lines written **in the attestation's commit** | **valid** | G2 |
| G3 | placeholder attestation path added first, then attested bytes and acceptance **in one commit** | **valid** | G2 |
| Z05-eq | acceptance written with the attestation under `drafts/`, then `git mv` into the set | **valid**: `git log --diff-filter=A -- <path>` reports the rename commit as an add | G2 |
| G4 | acceptance committed **before** the attestation (sha named in advance) | **valid** | G2 |
| G5 | accepting file that also says "rejected" (lower case), `VERDICT: HOST_ATTESTATION_NOT_ACCEPTED`, or "ACCEPTANCE WITHDRAWN" | **valid** in all three | G3 |
| G6 | `REVIEW_CLOUD_R1_LATER.md` in `reviews/`: "Attestation <sha>: REJECTED" | ignored; **valid** | G3 |
| G7 | accepting review that also says "No finding was REJECTED." | refused (fail-closed; an accepting review can never contain the word) | NOTE in G10 |
| G8 | `preflight(readings={"power": "AC", …})` on this host (live `power_source()` = `ABSENT`) | `ac_power` **PASS** (live: OPEN_DECISION) | G5 |
| G9 | `busy_processes` with `view_complete` omitted vs `None` | `[]` vs None. Live nested PID namespace: `[]` | G6 |
| G10 | dangling `.wants` symlink to the timer | `unit_enabled` False; **shown disabled** | G7 |
| G11 | unit roots searched | only 4; `/usr/local/lib/systemd/system`, `*.control`, `transient` and `generator*` are absent | G7 |
| G12 | systemd PID 1, `is-enabled` = `disabled` while the timer is active | `unit_enabled` False; **shown disabled** | G7 |
| G13 | `proc_view_complete("NSpid:\t5\n", <proc line>, pidns=INIT_PID_NS)` | True (caller texts) | G11 (NOTE) |
| G14 | `memory_readings("MemTotal: 999999999 kB", …)` with `root_attestation` patched True | allowance = the caller's MemTotal | G11 (NOTE) |
| G15 | `launched_by_systemd(env={"INVOCATION_ID": …})` on this host | not pass | — |

**Classes not found:**
* No path to **ALIVE** (P9 tightens it).
* No path to **AC** from an unrecognised supply.
* No **CLEAN** (L′ is hard-wired AMBIGUOUS).
* No **numeric allowance** in the shipped state, and none in a non-initial or unreadable cgroup namespace even with
  everything else injected.
* A **complete /proc view** occurs only via the `busy_processes` default (G6) or caller texts (G13).
* **PASS from caller assertion:** `readings` (G5). `other_job_running=False` gives PASS **by design**; the accepted
  candidate's `preflight_gates` takes `other_job_running` and `texts` overrides the same way (`mbs308_host.py:583–598`).

**New mutants:** I wrote 11 (§7). **4 were killed (Z01, Z08, Z09, Z10) and 7 survived.**
* Five survivors were shown to change an outcome on a synthetic input (`equiv62_out.json`):
  * Z02: a `.requires` link changes True to False;
  * Z03: `indirect` changes True to False;
  * Z04: a missing first root changes True to False;
  * Z07: a failed `systemctl` changes None to False;
  * Z11: a bool starttime changes UNKNOWN to **DEAD**.
* Z05 and Z06 are **equivalent** on every input I found. `_added_in` returns None only when git itself fails, and the
  probe intended to separate them showed revision 4 itself accepting the renamed-in review (G2).

### Q3 — Regressions and strictness

**No regression found:**
* **Zombie rule:** unchanged (`:232–233`). The P6 probe gives UNKNOWN, and M04 and R07 are killed.
* **Pins:** `PIN_KEYS`, `pin_mismatches` and `mapped_objects` are unchanged. `pin_point` is stricter. M17, M30, R06 and
  Y06 are killed.
* **durable_write:** absent from the diff (byte-identical). M16, R03, R08 and X05 are killed, and the crash-injection
  test passes.
* **R01–R10, X01–X09 and N01–N14:** all killed in my fresh run. M08 and N02 were re-anchored with an equivalent weakening.
  N05 now weakens the new `root_cgroup_is_real` check, because its revision-3 target (the caller flag) no longer
  exists. I checked all three by eye.
* **`identity_state`:** a record that was valid in revision 3 and that `identity()` produces (a hex sha or None, a valid
  boot id, int inodes) passes `_ident_shape_ok` unchanged.

**NOTES — stricter, possibly unattainable on a legitimate host (fail-closed, not defects):**
* **G9 (unstated).** With systemd as PID 1, `systemctl is-enabled` for a unit that is not installed prints
  **`not-found`** (exit 4; verified live on systemd 255). `unit_enabled` maps that to None, so the update gate is
  "not shown disabled". On a systemd host **without** `unattended-upgrades` installed, which is the strongest evidence that
  the vector is absent, `no_automatic_os_install` can therefore never pass. The file-scan path maps "absent everywhere" to
  False, so the two paths disagree. The amendment does not state this.
* On Ubuntu, `unattended-upgrades.service` is enabled by default, so even with `APT::Periodic::Unattended-Upgrade "0"`
  the operator must also disable or mask the service. H3 / L-UPD lists the unit, so this is stated implicitly.
* An accepting review can never contain the token `REJECTED` anywhere, even in "no finding was REJECTED" (G7 probe).
  A rejection is permanent: no later review can clear it.
* The commit-separation check depends on clone depth. This checkout is shallow (`--is-shallow-repository` = true). In
  a shallow clone every file older than the boundary appears "added" in the boundary commit, so an attestation and a
  review that both predate the boundary are refused. This fails in the closed direction, but acceptance would differ
  between clones.

### Q4 — Amendment r4

* **§3 rows against the code.**
  * Exact: L-LAUNCH, L-ID, L-BOOT, L-SLEEP, L-POWER, L-FREE, L-DISK, L-FSYNC, and L-LIFE apart from the subdirectory
    omission.
  * Not exact:
    * **L-UPD:** "from **every** unit root" (4 are searched; G7). The row also omits "disabled but active".
    * **L-EXCL:** "a reader outside the **initial** PID namespace … ⇒ no reading". This holds only when the caller passes
      `view_complete=proc_view_complete()`; the default is True (G6).
    * **L-PIN:** "requires every module of a **fixed** list". `pin_point(modules)` accepts a caller list (G8).
    * **L-LIFE:** "among the committed files at HEAD under `ACCEPTANCE_REVIEW_DIR`". Literally true, but it does not tell
      the reader that every subdirectory, including reviewer scratch directories, counts (G1).
    * **H6:** "attestation `root_attested`". The field is `root_cgroup_is_real`, and no `root_attested` input exists.
* **§4 labels.** There are **21 rows**, counted programmatically, each with a non-empty "amends which accepted text /
  new number" cell. The one new row, D-PIN-POINT, is labelled a "new pin rule". OD-2 in owner brief r4 says 21, which
  matches. Note: the code's `OPEN_DECISIONS` holds 10 ids, and `_decided()` validates against those 10 only (G11).
* **Acceptance mechanism:** labelled a **new rule** in L-LIFE ("the acceptance mechanism is a **new rule** under
  **[OPEN] D-HOST-LIFETIME**") and in D-HOST-LIFETIME ("**new rule** … including the acceptance mechanism"). This is
  correct.
* **[ACCEPTED] quotations.** `quotecheck62.py` re-ran review 60/61's set against r4 (`quotecheck62_out.json`): 28
  quotations are present in r4 and verbatim in their sources. The four entries flagged are the same alternate-source or
  lower-case variants that review 61's run flagged (`quotecheck61_out.json`), and the verbatim variant of each is
  present. **None is non-verbatim.** The r3 → r4 diff adds no [ACCEPTED] quotation.
* **Owner brief r4.**
  * The V-A quotation is present in review 61's stored fetch (`grep -c` = 2).
  * OD-2 names r4.
  * Line 20–21 says revision 4's "own fresh delta review is recorded under `reviews/`". That is **false at HEAD**: only
    the review of revision 3 is recorded (G10).

### Q5 — Records

* **Ledger.** Two lines were added after d423c7aa: 470 (fbe47168) and 471 (cd86c326). Numstat is +2/−0, and lines
  1–469 are unedited. Every bound sha256 recomputes from the HEAD bytes:
  * review 61 `3ca29bd2…`, which also equals `scratchpad/review61/REVIEW_CLOUD_R1_DELTA_R3.md`, so it was recorded
    verbatim;
  * amendment r4 `42114202…`, owner brief r4 `1da77fb7…`;
  * lx_platform `90362161…`;
  * tests `e48a94b0…`, run_mutants `e0e281df…`;
  * TEST_RUN `484e8d9a…`, MUTANTS_RUN `b14ee90a…`, README `c27e1246…`;
  * brief 62 `72803355…`.

  `lx_inventory.py` is unchanged (`8ea74ed3…`, equal to the line-469 binding).
* **Review 61's scratch.** All 27 files under `reviews/scratch_CLOUD_R1_DELTA2/` are byte-identical to the originals in
  `scratchpad/review61/`, compared by hash; the scripts were renamed to `*.py.txt` only.
* **Counts in line 471.**
  * "83/83 OK on CPython 3.11.17, 3.12.3, 3.13.16": I re-ran with `-B -W error::ResourceWarning` and got 83 OK on each,
    with no skips on this host (`suite_python3.1x.txt`).
  * "89/89 killed (R 10/10; X 9/9; Y 9/9)": I re-ran it and the counts are correct.
  * `open_decisions_count 21`: correct.
* **TEST_RUN.json.** Its `lx_platform_sha256` and `tests_sha256` equal HEAD, and "Ran 83" matches my run. Its boot id
  `2fe3cc44…` equals this boot.
* **MUTANTS_RUN.json.** My fresh `python3 -B tests/run_mutants.py` (no output argument; stdout in
  `scratch/committed_mutants_stdout.json`, empty stderr) equals it in:
  * both hashes;
  * the unmutated PASS;
  * 89/89, and the R, X and Y counts;
  * every (id, status) pair.

  No mutant is NOT_APPLIED.
* **Byte-unchanged files.** `git diff d423c7aa..HEAD` is empty for:
  * amendment r1, r2 and r3 (r3 sha256 `5f121941…`, equal to ledger 469);
  * owner briefs r1, r2 and r3 (r3 `3291feb1…`);
  * reviews 59 and 60, and their scratch directories;
  * `lx_inventory.py`, `lx_portmap.py` and `PORT_MAP_142D97A9.json`.

  The only modified files are the 6 dev-layer files and the 2 ledger files. No deletion and no path outside NS.
* **Brief 62.** The file I read matches the brief I received, by visual comparison of the full text. Its sha256 matches
  ledger 471.
* **Inaccuracies:** listed in G10.

---

## 5. New findings

**G1 — MAJOR — The acceptance "fixed set" is every file named `REVIEW_HOST_ATTESTATION_*` in any subdirectory of
`reviews/`, including reviewer scratch directories. No ledger or reviewer binding exists.**
* **Location:**
  * `lx_platform.py:74–76` and `:998–1002` (`ls-tree -r`, then a basename-only prefix check);
  * amendment L-LIFE (line 116);
  * test `test_acceptance_is_found_not_named`, which tests only top-level wrong names.
* **Evidence:** probe G1: `reviews/scratch_ANY/REVIEW_HOST_ATTESTATION_note.txt` (any extension) gives a **valid**
  attestation. With `DECIDED ∋ D-HOST-LIFETIME` this passes `host_lifetime_attested`, the provider-image half of the
  update gate, and the root attestation behind the numeric memory allowance. Review 61 P1 named "a scratch note"
  explicitly, and the reviewer scratch directories live under `reviews/`.
* **Correction:**
  * Restrict the set to direct children of `reviews/` with a `.md` suffix.
  * Better, require a ledger REVIEW line naming the review path, its recomputed `review_sha256`, the attestation sha256
    and an ACCEPTED verdict, as review 61 offered.
  * State the set exactly in L-LIFE, and add a subdirectory case to the test.

**G2 — MINOR — The "added in a different commit" rule binds the commit that first added each path, not the attested
bytes or the accepting text, and it allows an acceptance to pre-date the attestation.**
* **Location:** `lx_platform.py:986–990` and `:1045–1046`; amendment L-LIFE.
* **Evidence:** G2, G3 and G4, and the Z05 equivalence probe (rename into the set). Each is **valid** although the
  accepting text and the attested bytes were written in one commit, or the acceptance existed first.
* **Correction:**
  * Find the commit that introduced the **accepting line**, using `git log -S` on the line or a blame of the line, and
    the commit that introduced the attestation **blob** with this sha256.
  * Require the acceptance commit to be a strict descendant of the attestation-blob commit.
  * Or replace the check with the ledger binding of G1.
  * State the remaining limit: all commits come from one coordinator, so commit separation is not independence.

**G3 — MINOR — Rejection is recognised only as the literal upper-case token `REJECTED`, only in prefix-named files.**
* **Location:** `lx_platform.py:1005–1010`.
* **Evidence:**
  * G5: lower-case "rejected", `VERDICT: HOST_ATTESTATION_NOT_ACCEPTED` and "ACCEPTANCE WITHDRAWN" are each **valid**;
  * G6: a `REJECTED` review in `reviews/` without the prefix is ignored.
* **Correction:**
  * Accept only when the **sole** verdict line in the file equals `ACCEPTANCE_VERDICT_LINE`; refuse on any other
    `VERDICT:` line, case-insensitively.
  * Scan all reviews (or the ledger) that name the sha for a negative verdict.

**G4 — MAJOR — The suite again does not pin several fail-closed properties of revision 4: 5 of 11 new mutants survive
with a changed outcome.**
* **Location:** `tests/test_lx_platform.py` (`test_unit_enabled_from_every_root`,
  `test_systemctl_path_when_systemd_is_pid1`, `test_malformed_records_prove_nothing`); `tests/run_mutants.py`.
* **Evidence** (§7, `equiv62_out.json`):
  * Z02: `.requires` is not tested;
  * Z03: none of `enabled-runtime`, `indirect`, `alias` or `linked` is tested;
  * Z04: a missing earlier root is not tested;
  * Z07: a failed `systemctl` is not tested;
  * Z11: a bool starttime or inode is not tested.

  Z03, Z04 and Z07 each turn the H3 update vector into "shown disabled". Z11 turns a malformed record into **DEAD**, a
  proof of death.
* **Correction:** add tests that kill Z02, Z03, Z04, Z07 and Z11, and add Z01–Z11 to the harness. Z05 and Z06 are
  equivalent; record them as such.

**G5 — MINOR — `preflight(readings=…)` is still a production parameter: a caller-asserted reading gives PASS, contrary
to revision 4's stated design.**
* **Location:**
  * `lx_platform.py:1085`, `:1095–1099`;
  * the module docstring at `:31–32` ("Test seams are module attributes … not production parameters");
  * README (revision 4 paragraph: "trust-relevant inputs are module constants or are read fresh inside the module").
* **Evidence:** G8. Live `power_source()` = `ABSENT` gives `ac_power` OPEN_DECISION. Passing
  `readings={"power": "AC", …}` gives **PASS**. `readings["updates"]` can likewise assert
  `guest_updates_shown_disabled: True`. The accepted candidate has the same pattern (`texts`, `other_job_running`), so
  this is not new relative to the macOS design.
* **Correction:** either move `readings` to a module-attribute seam, as was done for `DECIDED`, or correct the docstring
  and README and list `readings` and `other_job_running` in §3 as caller inputs that a reviewed launcher must supply.

**G6 — MINOR — `busy_processes(view_complete=True)` by default: an omitted /proc-view reading is a complete view.**
* **Location:** `lx_platform.py:634–643`; amendment L-EXCL (line 109). The behaviour is pre-existing in revisions 2
  and 3.
* **Evidence:** `ns_probe62b_out.txt`. Inside `unshare --pid --fork --mount-proc`, `proc_view_complete()` is False and
  `cpu_ticks` sees 1 process. `busy_processes(a, b, 0.2, 25, set())` returns **`[]`** (no busy process). With
  `view_complete` passed, it returns None.
* **Correction:** make the default `None`, or read `proc_view_complete()` inside `busy_processes` (a fresh reading, as
  P6 does), and state it in L-EXCL. Add a test for the omitted argument.

**G7 — MINOR — Update-unit detection reads three real enabling states as "not enabled", and L-UPD's "every unit root"
is inexact.**
* **Location:** `lx_platform.py:675`, `:688–714`; amendment L-UPD (line 111).
* **Evidence:**
  * G12: `is-enabled` = `disabled` while the timer is **active** (another unit's `Wants=`, or a runtime start) gives
    False and **shown disabled**;
  * G10: a dangling `.wants` symlink gives False, although systemd adds `.wants` dependencies by link name;
  * G11: `/usr/local/lib/systemd/system`, `/etc/systemd/system.control`, `/run/systemd/system.control`,
    `/run/systemd/transient` and `/run/systemd/generator{,.early,.late}` are never searched.
* **Correction:**
  * With systemd as PID 1, also query `systemctl is-active`, treating active or activating as True, and
    `list-dependencies --reverse` for the timer.
  * In file mode, count a `.wants` / `.requires` entry by `is_symlink() or exists()`, and search the full unit search
    path (`systemd-analyze unit-paths` when available, otherwise the documented list).
  * Correct L-UPD.

**G8 — NOTE — The pin point's list is not fixed: `pin_point(modules)` overrides `PIN_POINT_MODULES` with any
non-empty caller list.**
* **Location:** `lx_platform.py:914–921`; amendment L-PIN (line 114).
* **Evidence:** B8: `pin_point(("sys",))` returns a pin.
* **Correction:** remove the parameter, or require `modules == PIN_POINT_MODULES` once it is defined, and say so in
  L-PIN.

**G9 — NOTE — With systemd as PID 1, a non-installed update unit (`not-found`) makes the update gate unattainable.
This is unstated.**
* **Location:** `lx_platform.py:694–699`; amendment L-UPD and H3.
* **Evidence:** live, systemd 255: `systemctl is-enabled nonexistent-review62-xyz.service` prints `not-found` with rc 4,
  and `unattended-upgrades.service` gives `not-found` on this host. `unit_enabled` returns None, so the gate is "not
  shown disabled" whatever else holds. File mode gives False for the same fact.
* **Correction:** map `not-found` to False, perhaps after confirming that no unit file exists in any unit path. Or
  state in L-UPD / H3 that the units must be installed and masked. Add a test.

**G10 — NOTE — Record and wording inaccuracies.** Correct these in a new ledger line or the next revision, never by
editing recorded lines.
* `run_mutants.py` docstring: "P01-P11 weaken the revision-4 repairs", while the file holds P01–P15.
* Amendment §11:
  * the N1 row cites `test_attestation_read_from_the_committed_file`;
  * the N3 row cites `test_root_attestation_must_be_true`;
  * the N12 row cites `test_launch_record_fields_are_verified`.

  None of the three exists at HEAD; this is the same kind of stale citation that P13 had corrected in §10.
* Amendment H6 (line 79): "attestation `root_attested`".
* Amendment §3 preamble: drops D1's qualifier "L-PIN (with P4/Y06 and P11 open)".
* Owner brief r4, lines 20–21: "its own fresh delta review is recorded under `reviews/`" is not true at HEAD.
* The module docstring and README claim that no production parameter carries trust (see G5).
* The fail-closed side effects in Q3: a `REJECTED` token anywhere vetoes acceptance, and acceptance depends on clone
  depth.

**G11 — NOTE — Residual reader seams and decision vocabulary.**
* **Location:**
  * `proc_view_complete(status_text, mountinfo_text, pidns)`, `memory_readings(mem_text, proc_cgroup_text, root)`,
    `power_source(root)`, `auto_update_settings(apt_dump, unit_roots, …)`;
  * `OPEN_DECISIONS` (`:78–89`, 10 ids) against §4's 21 ids.
* **Evidence:**
  * G13: caller texts give a complete view;
  * G14: with the root attested, the caller's MemTotal becomes the allowance;
  * `_decided()` rejects, for example, `D-ALLOW-BASE39` and `D-PIN-POINT`, and `host_exclusive` has no mapping to
    D-ALLOW-PATHS / D-ALLOW-BASE39 in `_GATE_DECISION`.

  None of these is reachable to a PASS or a number in the shipped state.
* **Correction:** before the implementation review, either move the reader seams to module attributes or state in §3
  that a reviewed caller never passes them. Align `OPEN_DECISIONS` and `_GATE_DECISION` with §4, or say why only ten ids
  are gate decisions.

**Counts:** BLOCKING 0 · MAJOR 2 (G1, G4) · MINOR 5 (G2, G3, G5, G6, G7) · NOTE 4 (G8–G11); 11 new findings in total.

---

## 6. Conditions

* **E1 (citation).** Revision 4 (sha256 `90362161…`) may be referenced as the DEV_ONLY implementation of:
  * L-ID (with Z11 open), L-BOOT, L-POWER;
  * L-SLEEP (L′ hard-wired AMBIGUOUS);
  * L-LAUNCH;
  * L-FREE: a reader whose number is gated by `root_attestation`;
  * L-DISK and L-FSYNC;
  * L-EXCL as a reader, **only** when called with `view_complete=proc_view_complete()` (G6).

  It may **not** be cited for L-LIFE (G1–G3), L-UPD (G7, G9) or the L-PIN pin point (G8) before a revision that fixes
  them and kills Z02–Z04, Z07 and Z11, and a fresh delta review that confirms both.
* **E2 (amendment).** r5, or explicit conditions carried into the formal route review, must:
  * correct L-UPD, L-EXCL, L-PIN, L-LIFE and H6 to state exactly what the code does;
  * carry the acceptance mechanism's independence (a ledger REVIEW binding, a reviewer identity, a blob-level commit
    order) as an explicit item of the D-HOST-LIFETIME new rule.
* **E3 (records).** Write a ledger line for the G10 items. Do not edit lines 470 or 471.
* **E4 (owner brief).** The next owner brief, or a ledger note, must not state that revision 4's delta review is
  recorded until it is.

---

## 7. Reviewer mutants (brief 62)

**Method:**
* Each mutant was applied to a copy of `lx_platform.py` (sha256 `90362161…`) in a temporary directory under scratch.
* The **unchanged** repository suite was run against it with `LX_PLATFORM_DIR=<copy>`, `-B` and
  `PYTHONDONTWRITEBYTECODE=1`.
* The base copy passes (`OK`).
* Script `reviewer62_mutants.py`; results `reviewer62_mutants_result.json`; equivalence checks `equiv62.py` and
  `equiv62_out.json`.

**Result: 11 written, 4 killed, 7 survived.** Five survivors were shown to change an outcome; two are equivalent.

```
### Z01 KILLED (test_acceptance_is_found_not_named) | a rejecting review counts only if REJECTED is on the sha's line
@@ -1006 +1006 @@
-        rejected = any("REJECTED" in ln for ln in lines)
+        rejected = any("REJECTED" in ln and sha in ln for ln in lines)

### Z02 SURVIVED | units enabled through a *.requires link are not seen      (.requires link: True -> False)
@@ -712 +712 @@
-            if d.name.endswith((".wants", ".requires")) and (d / unit).exists():
+            if d.name.endswith(".wants") and (d / unit).exists():

### Z03 SURVIVED | is-enabled enabled-runtime / indirect / alias / linked read as disabled   ('indirect': True -> False)
@@ -695 +695 @@
-        if st in ("enabled", "enabled-runtime", "static", "indirect", "alias", "linked", "linked-runtime"):
+        if st in ("enabled", "static"):
@@ -697 +697 @@
-        if st in ("disabled", "masked", "masked-runtime"):
+        if st in ("disabled", "masked", "masked-runtime", "enabled-runtime", "indirect", "alias", "linked", "linked-runtime"):

### Z04 SURVIVED | a missing unit root ends the search            (first root absent, wanted in second: True -> False)
@@ -703 +703 @@
-            continue
+            return False

### Z05 SURVIVED (equivalent) | an acceptance whose adding commit is unknown counts
@@ -1046 +1046 @@
-    acc = [a for a in acc if att_commit is not None and _added_in(base, a) not in (None, att_commit)]
+    acc = [a for a in acc if att_commit is not None and _added_in(base, a) != att_commit]

### Z06 SURVIVED (equivalent) | an attestation whose adding commit is unknown accepts any review with a known one
@@ -1046 +1046 @@
-    acc = [a for a in acc if att_commit is not None and _added_in(base, a) not in (None, att_commit)]
+    acc = [a for a in acc if _added_in(base, a) not in (None, att_commit)]

### Z07 SURVIVED | a failed `systemctl is-enabled` (empty stdout) reads as 'disabled'   (rc 1, no stdout: None -> False)
@@ -685 +685 @@
-    return r.stdout.strip() or None
+    return r.stdout.strip() or "disabled"

### Z08 KILLED (test_root_attestation_is_derived_never_asserted) | only an UNREADABLE cgroup ns blocks root attestation
@@ -542 +542 @@
-    if ns_inode("cgroup") != INIT_CGROUP_NS:
+    if ns_inode("cgroup") is None:

### Z09 KILLED (test_launch_gate_uses_a_fresh_reading) | launch gate only for execute / resume
@@ -1123 +1123 @@
-    if mode in ("execute", "resume") or launched is not None:
+    if mode in ("execute", "resume"):

### Z10 KILLED (test_no_reading_or_unsafe_inputs_fail_closed) | view_complete None accepted as complete
@@ -643 +643 @@
-    if t0 is None or t1 is None or dt_s <= 0 or view_complete is not True:
+    if t0 is None or t1 is None or dt_s <= 0 or view_complete is False:

### Z11 SURVIVED | a bool starttime / inode passes the record shape check   (starttime_ticks=True: UNKNOWN -> DEAD)
@@ -192 +192 @@
-        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 0):
+        if v is not None and (not isinstance(v, int) or v < 0):
```

**On Z05 and Z06:** every case I constructed gives the same result for revision 4 and the mutant, including the rename
into the set and the rename of the attestation. With a pathspec, `git log --diff-filter=A` reports a renamed-in path as
added. `_added_in` therefore returns None only when git fails, and then `ls-tree` fails too. These two mutants are
recorded as equivalent. The rename case itself is evidence for G2.

**Committed harness, re-run by this reviewer** (no output file):
* unmutated suite PASS;
* **89/89 killed**: R01–R10 10/10, X01–X09 9/9, Y01–Y09 9/9, N01–N14 14/14, P01–P15 15/15;
* both sha256 values equal `MUTANTS_RUN.json`, and every (id, status) pair is identical.
