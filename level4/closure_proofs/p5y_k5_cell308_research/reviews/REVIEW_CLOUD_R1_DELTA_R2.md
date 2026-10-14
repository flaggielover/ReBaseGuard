# Review — DELTA of the repairs after review 59 (Cell 308, MB-S successor, S4 changed branch, Cloud route r1)

* Reviewer: **reviewCLOUD_R1_DELTA (fresh agent, brief 60)**
* Date: 2026-10-14 (UTC; session approx. 19:47–20:05Z by the VM clock)
* Delta reviewed: **b3d8eb5e..ff9006ac** on branch `claude/cell-308-github-state-skb1g0`.
  * The checkout HEAD is 13e11bc3. `git diff --stat ff9006ac 13e11bc3` touches only `ledger/TARGET_INTEGRITY_LEDGER.jsonl`
    (one appended line), `ledger/briefs/60_reviewCLOUD_R1_DELTA.txt` and one `BRIEF_INDEX.md` row. Every D1/D2 file is
    therefore byte-identical in the working tree and at ff9006ac; the Q5 hashes were recomputed with `git show ff9006ac:<path>`.
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`. Paths below are relative to NS unless stated.
* `new_target_evaluations = 0`. No cell, drift, certificate, decoy, science module, qualification case, candidate
  code or quarantine guard was run. Nothing was installed and no setting was changed. No repository file was written.

---

## 1. Exposure disclosure

### 1.1 Files opened

* **Review 59 and its record:**
  * `reviews/REVIEW_CLOUD_R1_FEASIBILITY_AMENDMENT_DEV.md`, in full.
  * `reviews/scratch_CLOUD_R1/` (in full): probes.py, the head of probe_zombie_leader.py, the first 30 lines of
    reviewer_mutants.py, and grep and sed extracts of `fetched/cloud-environments.md` and
    `fetched/claude-code-on-the-web.md`.
* **D1:**
  * In full: PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R2.md, OWNER_DECISION_BRIEF_CLOUD_R1_R2.md,
    CLOUD_FEASIBILITY_R2_ERRATUM_E1.md and OFFICIAL_PROVIDER_FACTS_20261014_ERRATUM_E1.md.
  * CLOUD_HOST_INVENTORY_R2B_20261014.json: a structural dump through python.
  * CLOUD_HOST_INVENTORY.json (r1): its top-level values, through python, to check the erratum's U4 row.
* **D2 (all in full):** lx_platform.py, the `git diff` of lx_inventory.py, tests/test_lx_platform.py,
  tests/run_mutants.py, README_DEV_ONLY.md, results/TEST_RUN.json, and results/MUTANTS_RUN.json (its summary).
* **D3:** the `git diff b3d8eb5e 13e11bc3` hunk of the ledger (three added lines; no context line was printed) and the two
  added BRIEF_INDEX rows.
* **Accepted sources:**
  * Read through grep or sed at the quoted passages only: governance/SUCCESSOR_GOVERNANCE_308.md,
    _ADDENDUM_A1.md (lines 150–170) and _ADDENDUM_A1_ERRATUM_E1.md; governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md
    (headings, lines 138–148, 350–358 and 430–440, and grep hits); governance/CONSTANTS_RATIFICATION_MBS308.md (grep
    hits); registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md (headings and grep hits) and _ERRATUM_E1.md;
    reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md (lines 114–135 and 163–170, and grep hits);
    governance/new_host_route_cloud_r1/ROUTE_PREPARATION.md.
  * The quotation checker (`quotecheck.py`) also read these whole files programmatically for substring matching.
* **Candidate:**
  * `git show 142d97a9:…/p5y_k5_cell308_mb_r1/review/MB308_QUALIFICATION_REVIEW.md`, lines 466–480.
  * **Contact beyond E7/E8, disclosed:**
    * The grep that located E7/E8 also printed line 417 (G5: "The grant names E1-E8 and notes N1-N8 …") and line 520
      ("… exactly one execution under E1-E8").
    * The sed range overshot E8 by six lines, showing the heading "## NOTES" and note N1 (start load and thermal level
      "during the official run", "runtimes match r1's").
    * I read this as the official *qualification* run, since it is a qualification review. It contains no cell-308
      value and no figure I retained, and it entered no verdict. Whether "official run" there could mean anything
      else is UNVERIFIED.
  * `mbs308_host.py` was not opened; the suite itself reads two constants from it via `git show`.
* **Host (read-only):** `/proc/self/status` (NSpid), the inodes of `/proc/self/ns/{pid,time,cgroup}`, the `/proc` line
  of `/proc/self/mountinfo`, `/proc/1/comm`, and existence checks of `/sys/class/dmi/id/product_uuid` and
  `/sys/class/power_supply`.
* **Review-59 original scratch (`scratchpad/review59/`):**
  * listed, and the REVIEW file hashed (not read);
  * probes, mutants and fetched pages compared with `cmp` against the committed copies.

### 1.2 Commands run

* **Git:** `git rev-parse`, `log`, `diff`, `show`, `ls-tree`, `branch -a`, `merge-base --is-ancestor`, `status`, and
  `git ls-remote origin` for three heads (a read of the live remote).
* **From `streams/CLOUD_R1_LINUX_DEV`:**
  * `python3 -B -m unittest discover -s tests -v`: 60 tests, OK (3.13.16).
  * The same under `python3.11` and `python3.12` with `-B -W error::ResourceWarning`: 60 OK each.
  * `python3 -B tests/run_mutants.py` with **no output argument**: 42/42 killed, unmutated suite PASS. stdout was
    captured to scratch, and `results/` was not written.
* **Scratch (`/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review60/`):**
  * `base/lx_platform.py`: a copy, sha256 `7561c364…`, equal to the committed file.
  * `probes60.py`: review 59's P1–P8 and P10 re-run against revision 2, plus new probes. Output in `probes60_out.json`.
  * `probe_zombie_leader.py`: review 59's P6, unchanged, re-run on the copy. Output in
    `probe_zombie_leader_rev2_out.json`.
  * `probe_root_attested_out.txt`.
  * `quotecheck.py`.
  * `reviewer60_mutants.py`: 12 mutants, run against the unchanged repository suite through `LX_PLATFORM_DIR` with `-B`.
    Output in `reviewer60_mutants_result.json`.
  * An inline equivalence check showing that each surviving mutant changes an outcome.
  * `which_tests_kill.py`: which tests kill selected committed mutants.
* **Namespace probe, disclosed:** one `unshare --pid --fork --mount-proc python3 -B …` call (as root) imported the
  scratch copy inside a throwaway PID and mount namespace. It read NSpid, the pid-namespace inode, `proc_view_complete()`
  and `cpu_ticks()`. The namespaces ended with the process, and no persistent setting changed. Output is in
  `unshare_probe_out.txt`.
* **Repository state:** `git status --porcelain` is clean. A git-ignored `streams/CLOUD_R1_LINUX_DEV/__pycache__/`
  exists; it predates this review and was not created by it, since every repository-side run used `-B`.

### 1.3 Excluded material

I did not open, grep or read any of the following:
* `audit/EXECUTION_INTERRUPTION_ASSESSMENT*` or `audit/INCIDENT_AUDIT*`;
* `reviews/REVIEW_EXECUTION_INTERRUPTION*`;
* anything under `p5y_k5_cell308_mb_r1/postexec/`, or any MB r1 target-run record;
* `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`;
* any Cell-309 branch, file or record.

**Name-level contact, disclosed:**
* `ls reviews/` printed the file names `REVIEW_EXECUTION_INTERRUPTION.md`, `_DELTA.md` and `_R3.md` (names only).
* `git branch -a` printed Cell-309 branch names, which is permitted.
* A listing of the session scratchpad root showed the coordinator's `mut2.log` and `scan*.json`. They were not
  opened.

I hold no E1″ material and no MB r1 target-run runtime or host observation.

---

## 2. Verdicts

DELTA: DELTA_ACCEPTED_WITH_CONDITIONS
AMENDMENT_DRAFT_R2: FIT_WITH_CONDITIONS
DEV_CODE_R2: NOT_FAIL_CLOSED

**None of these verdicts accepts the amendment.** Only three things can accept, reject or put it into force:
* a formal independent route / governance review;
* a fresh S12 incident-independence re-rating;
* the owner's decisions (OD-1 to OD-3 and the [OPEN] items).

This is a delta review of a draft and a development layer.

**Why each verdict:**

* **DELTA_ACCEPTED_WITH_CONDITIONS.** The repairs are accepted except where conditions apply.
  * Both BLOCKING findings are resolved: libm, libc and the loader are now pinned by content, and a zombie leader is
    never DEAD (re-probed).
  * The governance repairs are faithful: every [ACCEPTED] quotation is verbatim, the errata discipline holds, and every
    ledger hash recomputes.
  * Conditions:
    * (C1) No revision-2 code is cited as the implementation of any L-* row before a revision 3 fixes N1–N8 and passes a
      fresh delta review.
    * (C2) The amendment conditions below.
* **FIT_WITH_CONDITIONS (amendment r2).** No accepted rule is relaxed and PROPOSED vs ACCEPTED is clean. But the §3
  "fail-closed behaviour" column asserts properties the code lacks: L-POWER (N2), L-FREE (N3), L-EXCL (N4) and L-LIFE
  (N1). §0's rule "until decided, every dependent gate is OPEN_DECISION" is contradicted for D-HOST-LIFETIME (N1).
  Several §4 labels are incomplete (N9), and the L-DET pre-registration is deferred (F5, N10). These must be corrected
  in r3, or carried as explicit conditions into the formal review.
* **NOT_FAIL_CLOSED (dev code).** Every review-59 probe now fails closed. But the same failure classes recur through new
  paths, in four of the five output classes the brief names:
  * an **unrecognised** battery status gives **AC** (N2);
  * a **rejected** root attestation (`"no"`, `"REJECTED"`, `{"accepted": False}`) gives a **numeric allowance**
    (N3);
  * an **unrecognised** boot id (`""`, `"garbage"`) gives **PASS** (N6);
  * a **self-asserted** attestation pointing at any committed file gives **PASS** for two gates (N1);
  * a nested PID namespace with its own `/proc` is reported as a **complete** view (N4).

  The README's claim that "a failed, absent or unrecognised reading is UNKNOWN" is false again. The paths are narrower
  than in revision 1, and each has a small fix. The live `preflight` still cannot pass, but only because five gates are
  hard-wired OPEN_DECISION; review 59 already explained why that is not credited.

---

## 3. Q1 — Status of review 59's findings

| F | sev (r59) | status | evidence |
|---|---|---|---|
| F1 | BLOCKING | **RESOLVED** (with NOTE N11) | `lx_platform.py:711–730` (`mapped_objects`), `:733–761` (dpkg versions), `:764–793` (`platform_readings`, `PIN_KEYS` without libpython; `libpython_mapped` recorded); amendment §3 L-PIN row and equivalence paragraph (lines 110, 115–120). Live probe: mapped set includes `libm.so.6`, `libc.so.6`, `ld-linux-x86-64.so.2`; `libpython_mapped=false`; dpkg `libc6 2.39-0ubuntu8.9`. Tests `TestPins.*`; R06 and M30 are killed by three behavioural tests (`test_libm_change_with_same_glibc_string`, `test_unreadable_pins_never_match`, `test_pin_set_covers_libm_libc_loader`). Residual: no required-member check, process-state-dependent set, X09 survives (N11). |
| F2 | BLOCKING | **RESOLVED** | `lx_platform.py:182–183` (Z/X ⇒ UNKNOWN). Review-59 probe P6 re-run unchanged against revision 2: leader `Z`, `Threads: 2`, ticks 86→136→186→235, `identity_state` **UNKNOWN** on all four readings (`probe_zombie_leader_rev2_out.json`). Test `test_zombie_leader_with_live_thread_is_not_dead` passes and asserts that a Z state was really reached. D-ID-ZOMBIE row (amendment line 148). M04 is killed. |
| F3 | MAJOR | **RESOLVED** | Amendment §7 lines 223–238: S13 in full (including "and must disclose any prior reading"), E1 D2 and E1 D3 verbatim (quotecheck: True). Correction in ledger line 465 (`correction_of_earlier_line`); the old line is unedited (0 removed lines in the diff). |
| F4 | MAJOR | **PARTIALLY RESOLVED** | Done: D-RC2-SCOPE (line 130), §5 preamble with route A1 §1, MBR1_REPRO and brief R2 §9 verbatim; §6 replaced by line 129 and T1, both verbatim; OD-3 reworded (owner brief lines 45–49: "does **not** restore"). Not done: the requested statement "T1 has fired by construction for any platform change" is replaced by a conditional ("unless D-RC2-SCOPE is decided otherwise", §6 line 209), and §10 does not record the deviation. The conditional is conservative by default ("if unresolved: treat as (a)"), but §6's escape clause sits uneasily with §5 ("does not by itself restore"). Accepted N3 (incident review line 116) includes the MBR1_REPRO reproduction, so whether N3 fails off-platform is exactly the open question. I accept the substance, not the undocumented deviation. |
| F5 | MAJOR | **PARTIALLY RESOLVED** | Done (§5 items 1–9): case set by name, matching MBR1_REPRO; successor build only, no ad-hoc harness; D-INTERPRETER before any run; leaf and byte equality; attempts recorded; no host shopping; E8 restated; caps exclusion. Not done: record paths, commit and sha256, and the strip / serializer digests, are deferred to "an amendment addendum" (item 1, item 4). The source "MB r1's freeze r3 `c46434a3` evidence" is UNVERIFIED (the r3 qualification records may post-date `c46434a3`). Item 5 introduces a repeat permission with no named decider (N10). |
| F6 | MAJOR | **RESOLVED** | §4 rows D-S15-NEWHOST, D-ALLOW-BASE39, D-CAPS-CPU (Q12 margins, RLIMIT_CPU), D-INTERPRETER, D-TEXT-LAUNCHD and D-LID; H3 / L-UPD list `Automatic-Reboot`, snapd, cloud-init and livepatch; L-S15 names the qualified-worktree constants. |
| F7 | MAJOR | **PARTIALLY RESOLVED** | Column added (line 128). Missing or incomplete labels (N9): D-MEM-PRESSURE, D-THERMAL and D-LPM say "new rule" but replace ratified constants (CONSTANTS_RATIFICATION rows 24 and 25) and brief R2 §9 start-gate rows; D-EXCL-WINDOW's windowed share changes R-EXCL-PCT's measured quantity, not only "a window length"; D-PAUSE / L-AWAKE (CLOCK_MONOTONIC as awake time for EVAL_CAP) is unlabelled. |
| F8 | MAJOR | **PARTIALLY RESOLVED** | Strict `is True`, committed-blob sha256 and hardware-bound identity (`:813–841`); tests reject `"REJECTED"`, `"false"`, `1`, a missing file, a wrong sha and a soft identity; R02 is killed. But the record is self-asserted: a dict pointing at `README.md` with its HEAD sha256 and `acceptance_record: "no such review"` passes (`N_forged_attestation_valid: [true, []]`), and `host_lifetime_attested` and `no_automatic_os_install` both read **PASS** (N1). The gate can PASS while D-HOST-LIFETIME is [OPEN], against §0. |
| F9 | MAJOR | **PARTIALLY RESOLVED** | An unreadable type gives None (P1 re-run: `null`); a discharging UPS gives BATTERY (P1b); USB gives None; R01 and R10 are killed. But an unrecognised Battery/UPS **status** (`Unknown`, `garbage`, `discharging`, a NUL suffix) with Mains online gives **AC** (`:294–298`; probes `N_power_battery_status[*]`). `Unknown` is a real kernel value (N2). |
| F10 | MAJOR | **PARTIALLY RESOLVED** | A partial chain gives None (P4a and P4b re-run: headroom null; P4b everything null); `memory.high` is honoured; cpu.max / cpuset / pids.max are read raw; `test_v2` is rewritten; H6 says the root is "attested, not read". But `root_attested` is an unbound caller truthy flag: `"no"`, `"false"`, `"REJECTED"`, `1` and `{"accepted": False}` all give `effective_limit 3000`, `headroom 2990` (`probe_root_attested_out.txt`; `:401`, `:414`, `:436`). There is no cgroup-namespace check, though the reader can detect a non-initial cgroup ns (inode 4026531835 = 0xEFFFFFFB on this host). `cgroup_resources` reads only the leaf v2 cgroup (`:464–468`), not its ancestors (N3). |
| F11 | MAJOR | **RESOLVED** | `apt-config dump` (`:573–579`), parsed on the live host (`apt_periodic {"Enable":"0"}`); positive evidence across apt, timer, snapd, cloud-init and livepatch (`:603–604`); docstring and code agree on `Unattended-Upgrade "0"`; R2B uses `guest_updates_shown_disabled`. Unreadable livepatch is fail-closed in code (`None != []`), but untested (X03 survives; N5). |
| F12 | MAJOR | **RESOLVED** as specified (new gap: N5) | R01–R10 are in the harness and all killed (my re-run: 42/42); `test_constants_equal_the_candidates` pins `SLEEP_GAP_TOL_NS` / `MAX_SAMPLE_GAP_S` to `142d97a9`; the fsync spy asserts `["file","dir"]`. However **9 of my 12 new mutants survive** (§7). |
| F13 | MINOR | **PARTIALLY RESOLVED** | (pid, starttime) keys; births charged (P7 and P7b re-run: reported); `own_pids ∋ 0/1` gives None; hidepid detected. Not resolved: a nested PID namespace with its own `/proc` is reported **complete** (N4, demonstrated); an exited hog is invisible; an unreadable pid is skipped silently (N7). |
| F14 | MINOR | **RESOLVED** (residual N8) | `identity()` records pidns and timens (`:131–136`); a mismatch, or an unreadable current ns, gives UNKNOWN (`:169–172`); `test_namespace_mismatch_is_unknown`; M22 and my X10 are killed. Residual: an *unrecorded* ns still lets ESRCH or a starttime difference prove DEAD (N8). |
| F15 | MINOR | **RESOLVED** | `mode` parameter (`:855–861`, `:888–891`); execute / resume without a record FAIL; `test_launch_gate_modes`; M29 is killed. Mode remains caller-declared, as in the candidate (N12). |
| F16 | MINOR | **RESOLVED** | Erratum E1 §1 (DR2 primary basis, verbatim), §2 (pause vs reclaim, matching fetched line 67), §3 (citation corrected; the E2 overstatement and the U4 scope are correct against the r1 inventory, which records systemd, power and thermal but no suspend_stats or journal). Owner brief r2 lines 14–16 distinguish pause from reclaim. |
| F17 | MINOR | **RESOLVED** | Provider-facts erratum P4 (completed) and P10 are verbatim against `fetched/cloud-environments.md:339` and `:67` (markdown link syntax removed only); the "withdrawn" clause and the r1 2-h reconciliation are present; U2 is restated (feasibility erratum §4). Whether the sentence existed at 18:55Z is honestly marked UNVERIFIED. |
| F18 | MINOR | **RESOLVED** | Label [PREPARATION] (§0 line 18, §4 line 124); the H1 "basis" column now reads "[PREPARATION] step 7". |
| F19 | MINOR | **RESOLVED** | `lx_inventory.py` normalised comparison (diff), libc6, cgroup resources, root mount, hashed identity, proc view; R2B rows are correct by hand (for example kernel `-fc-v64` vs `-fc-v114`; python 3.12 versions equal, digests differ). |
| F20 | MINOR | **RESOLVED** (one UNVERIFIED point) | H8 (DMI `product_uuid` hashed, or an attestation); `machine_identity` with `hardware_bound`; owner brief V-A (line 29). The "requeue to another runner" wording cannot be checked against stored pages: the self-hosted page is not among the fetched copies in the repository or in review 59's scratch (UNVERIFIED). |
| F21 | NOTE | **RESOLVED** | Ledger line 465 binds the owner instruction (`a202596d…`, recomputed); line 466 notes the inventory's tool version; TEST_RUN.json carries "Ran 60" and `tests_total 60`. Brief 59's issuance is recorded in line 467, which is **after** ff9006ac (in 13e11bc3), so it is resolved at HEAD, not at ff9006ac. |
| F22 | NOTE | **RESOLVED** | The `assertNotEqual(…, "never")` construct and the wrapper "mutant" are gone. New near-tautologies: N13. |
| F23 | NOTE | **RESOLVED** | `StaleTmp` (`:64–66`, `:667–670`); `test_stale_tmp_is_a_named_state` leaves the tmp in place. |

**Tally:**
* RESOLVED (16): F1, F2, F3, F6, F11, F12, F14, F15, F16, F17, F18, F19, F20, F21, F22, F23. F12 is resolved as
  specified; the remaining test gap is N5.
* PARTIALLY RESOLVED (7): F4, F5, F7, F8, F9, F10, F13.
* NOT RESOLVED: 0.
* DISPUTED-JUSTIFIED: 0. The only deviation, the F4 T1 sub-item, is undocumented, so it cannot be rated as a justified
  dispute.

---

## 4. Answers Q2–Q6

### Q2 — New defects

**Paths where a failed, absent, unrecognised or rejected input yields a pass state.** All demonstrated against the
scratch copy `7561c364…`; output in `probes60_out.json` and `probe_root_attested_out.txt`.

* **AC.** `power_source` with Mains online and a Battery whose status is `Unknown`, `garbage`, `discharging` or
  `"Discharging\0"` returns `"AC"` (N2).
* **PASS:**
  * `attestation_valid` accepts a dict referencing any committed blob (here `README.md`), with an arbitrary
    `acceptance_record`. Two gates read PASS (N1).
  * `preflight(readings={"boot_id": ""|"garbage"|0|False})` gives `boot_id_recorded = PASS` (N6).
* **Numeric allowance.** `memory_readings(..., root_attested="no"|"false"|"REJECTED"|1|{"accepted": False})` gives
  `effective_limit=3000`, `cgroup_min_headroom=2990` (N3).
* **CLEAN.** No live path was found. Two untested branches (`samples` absent; K′ with monotonic ahead of boottime) turn
  CLEAN under single-line mutants X06 and X04, which survive (N5).
* **ALIVE.** No path was found.
* **DEAD from a failed reading.** An identity record without `pidns` / `timens` plus ESRCH, or a starttime difference
  from another namespace, gives DEAD (N8).
* **Exclusivity "clean":**
  * inside `unshare --pid --fork --mount-proc`, NSpid has one entry, the pidns inode is 4026532265 (≠ 4026531836),
    `proc_view_complete()` is **True**, and `cpu_ticks()` sees only pid 1 (N4);
  * a hog that exits inside the window is not reported (`N_hog_exits_in_window: []`, N7).

**Tests that cannot or practically cannot fail (N13):**
* `test_live_host_is_never_clean` (`test_lx_platform.py:273–274`): the journal argument is `None`, which alone forces
  AMBIGUOUS, so no single mutant can make it CLEAN.
* `test_r1_vs_r2_hosts_would_mismatch` (`:603–607`) only shows that substituting a different string mismatches.
* `test_dump_lines_only` (`:473–475`) tests regex anchoring, not apt's comment handling.

**Mutant anchors.** No committed mutant is trivially killed:
* R06 and M30 are killed by three behavioural tests, not only by the `PIN_KEYS` literal (`which_tests_kill_out.json`);
* R04 and R09 are killed by behavioural boundary tests as well as by the constant pin;
* M11 is killed only by the blocked-set assertion of `test_all_favourable_still_blocked_by_open_decisions`, which is
  adequate for a gate-wiring mutant.
* R07 is re-anchored as an *added* T/t/D ⇒ DEAD branch, which is the same weakening in revision-2 terms.

**New mutants:** 12 written, **3 killed, 9 survived** (§7). Each survivor was shown not to be equivalent on a synthetic
input:
* X04 and X06 turn AMBIGUOUS into **CLEAN**;
* X08 turns a 2 000 000 000-byte v1 limit into an `effective_limit` of 16 874 930 176 (MemTotal);
* X03 gives `guest_updates_shown_disabled = True` from an unreadable livepatch directory;
* X01 and X02 report a `subset=` `/proc`, or no `/proc` mount line, as complete;
* X05 lets a corrupted read-back go undetected.

### Q3 — Amendment r2 fidelity

**[ACCEPTED] quotations.** 26 quotations and fragments were checked by `quotecheck.py` (whitespace collapsed,
`**` and list markers removed). All are verbatim against their named sources:
* the HOST row;
* DR2 (both the partial and the full form);
* MBS-5(b);
* route A1 §1 and §3 (MBR1_REPRO);
* brief R2 §9 "not settled";
* incident review line 129 and T1;
* S5, S7, S10 and S13;
* E1 D2 and E1 D3;
* the [PREPARATION] quotation;
* the fragments of R-FREE, R-MEM step 1, brief R2 §9 "only under the launchd launcher", S6, brief R2 §7 item 8, and
  R-ALLOW's "the current 39 names".

**Section citations, checked:**
* MBS-5(b) is brief R2 §4 item 5 (line 146–147);
* "§7 item 8" is at lines 353–356;
* the HOST row is route A1 §2 (line 40);
* "Determinism" is route A1 §1 (line 22);
* MBR1_REPRO is route A1 §3 (line 64).

One unlabelled paraphrase: D-S15-NEWHOST quotes "later-found MB r1 evidence is a permanent STOP". The source (A1 line
161) reads "Later-found MB r1 evidence is a permanent STOP for the successor, pending its own governance". That is a
case change and a truncation, not marked [ACCEPTED]; NOTE only.

**§4 labels** (row by row):
* **Correct:** D-RC2-SCOPE, D-MEM-FREE, D-MEM-WIRED, D-POWER-ABSENT, D-ALLOW-PATHS, D-ALLOW-BASE39, D-HOST-LIFETIME,
  D-WORKERS-CORES, D-CAPS-CPU, D-INTERPRETER, D-TEXT-LAUNCHD, D-LID, D-S15-NEWHOST, D-ID-ZOMBIE.
* **Incomplete (N9):**
  * D-MEM-PRESSURE amends ratified row 24 (`kern.memorystatus_vm_pressure_level` = 1) and the brief R2 §9 Memory row,
    besides introducing N.
  * D-THERMAL amends the brief R2 §9 "Thermal pressure level 0" start gate.
  * D-LPM amends ratified row 25 and the brief R2 §9 "Low Power Mode off" row.
  * D-EXCL-WINDOW changes R-EXCL-PCT's measured quantity (windowed ticks vs `ps -o pcpu`).
  * D-PAUSE's "awake time for EVAL_CAP" (L-AWAKE: CLOCK_MONOTONIC) amends the measurement basis of EVAL_CAP and is
    unlabelled.
* **Owner brief.** OD-2 says each of the 19 is "labelled with the accepted text it would amend". Several are labelled
  "none", "reading only" or "new rule".

**Relaxation and ACCEPTED vs PROPOSED.**
* No accepted rule or number is relaxed in the text, and §1 keeps every number.
* PROPOSED and ACCEPTED are cleanly separated, and [PREPARATION] is labelled correctly.
* Exceptions where the §3 table claims code properties that do not hold:
  * L-POWER: "unreadable type / status … ⇒ None", but an unrecognised status gives AC;
  * L-FREE: "numeric only with … the root attested (H6)", but any truthy value counts as attested;
  * L-EXCL: "a nested PID namespace … ⇒ no reading", which is false;
  * L-LIFE: "PASS only for … an acceptance-record reference", which is any string. Moreover the gate PASSes while
    D-HOST-LIFETIME is [OPEN], contrary to §0 line 20.

  These would mislead a formal reviewer into reading the proposed contract as fail-closed (N1–N4).

**L-DET vs MBR1_REPRO and E8.**
* The case set, the "through the successor's code" requirement, exact leaf equality with timing stripped, and "any
  mismatch ⇒ STOP / changed branch" are all carried. Byte equality is added, which is stricter.
* "QC04 … (drifts 3 and 11/10)" matches E8's "QC04 ladder records at 3 and 11/10".
* Item 8 restates E8 for L-DET records. E8 is broader: decoy, validation-drift and qualification values, and "neither
  it nor any handover". Item 8's "no L-DET record or value" covers the L-DET case.
* Three gaps against MBR1_REPRO:
  * Item 5's repeat rule is an addition with no accepted basis, no named decider and no §4 row (N10).
  * The reference-set digests are deferred (F5).
  * The provenance from `c46434a3` is UNVERIFIED.

### Q4 — Errata discipline

* **Unchanged files.** `git diff b3d8eb5e ff9006ac` (and `… 13e11bc3`) is empty for:
  * CLOUD_FEASIBILITY_R2.md, OFFICIAL_PROVIDER_FACTS_20261014.md, PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md,
    OWNER_DECISION_BRIEF_CLOUD_R1.md and CLOUD_HOST_INVENTORY_R2_20261014.json, so all are byte-unchanged;
  * ROUTE_PREPARATION.md, USER_AUTHORIZATION_20261014.md, CLOUD_FEASIBILITY.md and CLOUD_HOST_INVENTORY.json, which
    are also unchanged.
* **Provider quotations.** Both are verbatim against review 59's fetched pages:
  * P4 completed: `cloud-environments.md:339`;
  * P10: `:67`.

  The repository copies are byte-identical (`cmp`) to review 59's original scratch fetches. The fetch time "~19:18Z" is
  consistent with the fetched directory's mtime (19:19).
* **Erratum E1 facts.** Every value is consistent with R2B:
  * the image changes 24.04.4→24.04.5, `-fc-v64`→`-fc-v114`, 3.13.14→3.13.16 and libc6 8.7→8.9, and the removal of
    3.10;
  * the U4 split matches the r1 inventory (systemd, power and thermal recorded; suspend_stats and journal not).
* **One wording issue.** The erratum's "fetched copy line 67" is correct. But the owner brief's "the provider's runner
  lifecycle can requeue a session to another runner" drops the qualifier ("after a signal-less host kill", as worded in
  review 59 F20) and cannot be verified against any stored page (UNVERIFIED). It is conservative, so NOTE only.

### Q5 — Ledger

* **Lines added after b3d8eb5e:** 465 and 466 (in ff9006ac) and 467 (in 13e11bc3, outside the delta but checked).
  The diff removes 0 lines.
* **Every bound sha256 recomputes exactly** (`git show ff9006ac:<path> | sha256sum`; brief 60 at 13e11bc3):
  * review 59 `c394c035…`, also equal to review 59's original scratch output, so it was recorded verbatim;
  * brief 59 `9b78af71…`; owner instruction `a202596d…`;
  * amendment r2 `e61b0963…`; owner brief r2 `22e3be21…`;
  * feasibility erratum `0a40fd65…`; provider-facts erratum `c329d2aa…`; R2B `d41fae8a…`;
  * `lx_platform.py` `7561c364…`; `lx_inventory.py` `8b6cb394…`;
  * tests `139a392b…`; `run_mutants.py` `1ccdad51…`;
  * TEST_RUN `97e43af7…`; MUTANTS_RUN `23aa72fb…`; README `161163f6…`;
  * brief 60 `54e3ef2d…`.
* **Counts checked:**
  * review 59 findings {BLOCKING 2, MAJOR 10, MINOR 8, NOTE 3}, correct; pre-review F1–F12 and F16–F18, correct;
    "0/10 killed", correct;
  * `open_decisions_count 19`: the §4 table has 19 rows, correct;
  * "60/60 OK on CPython 3.11.17, 3.12.3, 3.13.16": re-run on all three, correct;
  * "42/42 killed incl. R01–R10 10/10": re-run, correct.
* **Inaccurate:** line 466's note "Repairs of every review-59 finding" overstates. Seven findings are only partially
  resolved (§3). The correction is a new line, never an edit (N14).
* **Clock consistency** (UNVERIFIED as to intent):
  * Review 59's header gives a session "approx. 19:10–19:45Z", but its output file's mtime is 19:26 and it was
    committed at 19:27:44Z.
  * The repair commit followed at 19:45:19Z: about 2 000 changed lines, three suite runs and 42 mutant runs, with
    TEST_RUN at 19:44:32Z and R2B at 19:41:19Z.

  Nothing indicates the repairs predate the review.

### Q6 — Preservation

* **Remote tips:** `git ls-remote origin` gives candidate `p5y-k5-cell308-mbs-r1-candidate = 142d97a9…` and research
  `p5y-k5-cell308-mbs-r1-research = 88a16f74…`. Both are unchanged (live remote, not only tracking refs).
* **Ancestry:** `88a16f74` is an ancestor of `ff9006ac`.
* **Scope of the delta:**
  * every path changed in `b3d8eb5e..13e11bc3` lies under NS; 0 paths are under `p5y_k5_cell308_mbs_r1/` or
    `p5y_k5_cell308_mb_r1/`;
  * the modified (not added) files are only the appended ledger and BRIEF_INDEX, plus the dev-stream files that review
    59 required to be revised;
  * every reviewed governance document is untouched.
* **Carried verbatim:** S5, S7, S10, S13 with E1 D2 and D3, and MBS-5(b) (Q3).
* **The amendment's own text** stays on the conservative side:
  * the "not a replacement series" paragraph (§1);
  * exactly-once (S7, "second consumed evaluation" under a new S1 ruling);
  * an extended holder rule for L-DET and qualification agents (§7, line 240–241), which is stricter.
* **One exactly-once concern in the code** (N8): DEAD from an unrecorded-namespace record. This is an exactly-once
  hazard of the same kind as review 59's F2, though much narrower.

---

## 5. New findings

**N1 — MAJOR — The host attestation is self-asserted, and the dependent gates can PASS while D-HOST-LIFETIME is [OPEN].**
* **Location:** `lx_platform.py:813–841`, `:868–874`, `:886`; amendment §3 L-LIFE (line 112), H3 (line 76), §0
  (line 20).
* **Evidence:** a forged dict passes, and both gates read PASS. The dict:
  * `path: "README.md"` with its HEAD sha256;
  * `reviewed / accepted True`;
  * `acceptance_record: "no such review"`;
  * `machine` equal to the current identity;
  * `provider_image_updates: "ATTESTED_NO_IMAGE_OR_OS_CHANGE"`.
* **Why it fails:** the committed file is never read. Every asserted field comes from the caller.
* **Correction:**
  * Until D-HOST-LIFETIME is decided, `host_lifetime_attested` and the provider-image half of
    `no_automatic_os_install` must be `OPEN_DECISION`.
  * Afterwards, parse the committed attestation (fixed schema) and take `reviewed`, `accepted`, the token and the
    machine from the file. Require `acceptance_record` to be a committed review that names the attestation's sha256
    and accepts it.
  * Add a test that an arbitrary committed file is refused.
  * Fix the L-LIFE row.

**N2 — MAJOR — An unrecognised battery / UPS status yields AC.**
* **Location:** `lx_platform.py:294–298`; docstring `:276–279`; README line 20; amendment L-POWER (line 97).
* **Evidence:** with Mains online, a status of `Unknown`, `garbage`, `discharging` or `Discharging\0` gives `"AC"`.
  `Unknown` is a status the kernel reports.
* **Correction:**
  * `Discharging` gives BATTERY.
  * Only `Charging`, `Full` and `Not charging` count as not discharging.
  * Anything else gives None.
  * Add tests.

**N3 — MAJOR — `root_attested` is an unbound truthy flag. A rejected attestation yields a numeric memory allowance.**
* **Location:** `lx_platform.py:395–447` (`if not root_attested`), `:481–495`; amendment L-FREE (line 102) and H6
  (line 79).
* **Evidence:** `"no"`, `"false"`, `"REJECTED"`, `1` and `{"accepted": False}` all give `effective_limit 3000` and
  `headroom 2990`.
* **Further gaps:**
  * no cgroup-namespace check (`/proc/self/ns/cgroup` against 0xEFFFFFFB);
  * `cgroup_resources` reads only the leaf v2 cgroup.
* **Correction:**
  * Accept only `root_attested is True`, derived from a verified attestation (N1) rather than passed in.
  * Return None in a non-initial cgroup namespace unless attested.
  * Read cpu.max and pids.max along the chain.
  * Add tests for truthy non-True values.

**N4 — MAJOR — A nested PID namespace with its own `/proc` is reported as a complete view. The L-EXCL claim is false.**
* **Location:** `lx_platform.py:510–527`; `test_proc_view` (`test_lx_platform.py:429–434`); amendment L-EXCL
  (line 105); §10 row F13.
* **Evidence:**
  * NSpid is printed relative to the procfs's own namespace, so a containerised reader sees one entry.
  * The `unshare` probe: NSpid `1`, pidns inode 4026532265, `proc_view_complete() == True`, `cpu_ticks` sees only
    pid 1.
  * The test's two-entry NSpid case cannot arise for a reader whose `/proc` belongs to its own namespace.
* **Correction:** require `/proc/self/ns/pid` to be the initial namespace (inode 0xEFFFFFFC), or attested; otherwise
  return False. Replace the synthetic test with one built on that check. The gate is OPEN_DECISION today, so this is
  latent. It is rated MAJOR because the amendment presents it as fixed.

**N5 — MAJOR — The suite still does not pin several fail-closed properties: 9 of 12 new mutants survive.**
* **Location:** `tests/test_lx_platform.py`; `tests/run_mutants.py`.
* **Evidence:** X01–X09 (§7). They cover CLEAN-producing branches (X04, X06), an inflated allowance (X08), positive
  update evidence from an unreadable reading (X03), view completeness (X01, X02), the read-back verify (X05), the unit
  type (X07) and the package pin (X09).
* **Correction:** add tests that kill X01–X09, add them to the harness, and report them beside M01–M32 and R01–R10.

**N6 — MINOR — `boot_id_recorded` passes any non-None injected value.**
* **Location:** `lx_platform.py:865`, `:882`.
* **Evidence:** `""`, `"garbage"`, `0` and `False` all give PASS.
* **Correction:** validate with `boot_id(boot)`, using the same regex as the reader, and add a test.

**N7 — MINOR — Exclusivity blind spots remain.**
* **Location:** `lx_platform.py:530–569`.
* **Evidence:**
  * a process present at t0 that exits before t1 is not reported;
  * `cpu_ticks` silently skips a pid whose stat cannot be read;
  * `own_pids` holds pid only, so a reused campaign pid exempts its children.
* **Correction:**
  * report t0-only keys as "exited, usage unknown", or return None;
  * count skipped pids and return None above zero (or report them);
  * key `own_pids` by (pid, starttime).

**N8 — MINOR — An unrecorded namespace lets ESRCH or starttime prove DEAD.**
* **Location:** `lx_platform.py:169–185`; amendment L-ID (line 93): "ESRCH in the same namespace".
* **Evidence:** a record without `pidns` / `timens`, read with `current_ns={"pidns":1,"timens":2}`, gives DEAD both on
  ESRCH and on a different starttime.
* **Correction:** if either ns is unrecorded, ESRCH and starttime evidence give UNKNOWN; a boot-id change stays DEAD.
  Add a test.

**N9 — MINOR — Incomplete "amends which accepted text" labels.**
* **Location:** amendment §4 lines 133–135, 139, 140; owner brief r2 line 40–41.
* **Correction:**
  * Label D-MEM-PRESSURE as amending CONSTANTS_RATIFICATION row 24 and the brief R2 §9 Memory row.
  * Label D-LPM as amending row 25 and the brief R2 §9 row.
  * Label D-THERMAL as amending the brief R2 §9 "Thermal pressure level 0" row.
  * Label D-EXCL-WINDOW as changing R-EXCL-PCT's measured quantity.
  * Add an L-AWAKE / EVAL_CAP awake-time label under D-PAUSE.
  * Reword OD-2's "each labelled with the accepted text it would amend".

**N10 — MINOR — L-DET item 5 adds a repeat rule with no decider and no §4 row.**
* **Location:** amendment §5 item 5 (lines 182–185).
* **Detail:** "at most one repeat, only for a positively infrastructural non-completion" is new. MBR1_REPRO neither
  grants nor bounds repeats.
* **Correction:**
  * Name who classifies a non-completion as infrastructural, and on which pre-registered evidence, before the first
    attempt.
  * List the rule in §4 as a new rule.
  * Make the item-1 / item-4 digests part of the text the formal review accepts before OD-3, not a later addendum.

**N11 — NOTE — The pin set depends on process state and has no required-member check.**
* **Location:** `lx_platform.py:711–730`, `:749–761`.
* **Evidence:**
  * the live set includes whatever happens to be imported (`_bz2`, `_lzma`, `libcrypto`, …);
  * a maps text without libm / libc / loader still yields a valid pin;
  * an unknown interpreter package is fail-closed through a placeholder, but this is untested (X09).
* **Correction:**
  * Require that `libm.so.6`, `libc.so.6` and the loader are present.
  * Implement the "pin point after the science imports" as a fixed import list, not prose.
  * Test the unknown-owner path.

**N12 — NOTE — `preflight` trusts caller-supplied records.**
* **Location:** `lx_platform.py:855–891`.
* **Detail:**
  * `launched={"pass": True}` is accepted as is;
  * `mode` is caller-declared;
  * `launched=True` in launcher mode raises AttributeError. That is closed by exception, not by a gate value.
* **Correction:** for execute / resume, compute `launched_by_systemd()` inside `preflight` (or verify the record's
  fields), and reject non-dict records with FAIL.

**N13 — NOTE — Near-tautological tests (successors of F22).**
* **Location:** `test_lx_platform.py:273–274`, `:603–607`, `:473–475`.
* **Detail:** see Q2.
* **Correction:** give `test_live_host_is_never_clean` a list-valued journal argument so that it can detect a
  regression, and rename or strengthen the other two.

**N14 — NOTE — Record wording.**
* **Ledger line 466:** "Repairs of every review-59 finding" overstates (seven are partial). Correct this in a new line.
* **Owner brief V-A:** the "requeue" statement is unverified against stored pages and drops review 59's qualifier.
* **D-S15-NEWHOST:** carries an unlabelled, truncated paraphrase of S15.

**Counts:** BLOCKING 0 · MAJOR 5 (N1–N5) · MINOR 5 (N6–N10) · NOTE 4 (N11–N14), 14 new findings in total.

---

## 6. Conditions (summary)

1. Make the following changes to the dev code (revision 3) and have it pass a fresh delta review, before any L-* row
   cites it as its implementation:
   * the N1–N4 code fixes;
   * the N6–N8 code fixes;
   * the N5 tests.
2. In amendment r3, or as explicit conditions carried into the formal route review:
   * correct the §3 fail-closed claims (L-POWER, L-FREE, L-EXCL, L-LIFE) and §0's OPEN_DECISION rule for
     D-HOST-LIFETIME (N1);
   * complete the §4 labels (N9);
   * make the L-DET repeat rule and the digests part of the accepted text (N10, F5);
   * record the F4 deviation, that T1 is not stated as fired, with its reason.
3. Write a new ledger line correcting "every review-59 finding" (N14).

---

## 7. Reviewer mutants (brief 60)

Each mutant was applied to a copy of `lx_platform.py` (sha256 `7561c364…`) in a temporary directory under scratch
`review60/`. The **unchanged** repository suite was run against it with `LX_PLATFORM_DIR=<copy>`, `-B` and
`PYTHONDONTWRITEBYTECODE=1`.

* The base copy passes (`OK`).
* **3 of 12 were killed and 9 survived.** For every survivor, an equivalence check on a synthetic input showed a changed
  outcome (Q2).
* The script is `reviewer60_mutants.py` and the results are in `reviewer60_mutants_result.json`.

```
### X01 SURVIVED | proc_view_complete: /proc 'subset=' mount option no longer refused
@@ -526 +526 @@
-            return not ("hidepid=" in opts or "subset=" in opts)
+            return not ("hidepid=" in opts)

### X02 SURVIVED | proc_view_complete: no /proc mount line found counts as a complete view
@@ -527 +527 @@
-    return None
+    return True

### X03 SURVIVED | auto_update_settings: an unreadable /sys/kernel/livepatch counts as 'no livepatch applied'
@@ -604 +604 @@
-    shown_disabled = bool(apt_off and not timer and not snapd and not cloud and livepatch == [])
+    shown_disabled = bool(apt_off and not timer and not snapd and not cloud and livepatch in ([], None))

### X04 SURVIVED | assess: K' 'monotonic advanced more than boottime' channel removed   (AMBIGUOUS -> CLEAN)
@@ -233,2 +232,0 @@
-            elif db - dm < -SLEEP_GAP_TOL_NS:
-                reasons.append("AMBIGUOUS: K' monotonic advanced more than boottime")

### X05 SURVIVED | durable_write: read-back verification removed
@@ -693 +693 @@
-    if got != want:
+    if False:

### X06 SURVIVED | assess: absent samples (None) no longer AMBIGUOUS                     (AMBIGUOUS -> CLEAN)
@@ -258,2 +257,0 @@
-    if not isinstance(samples, list):
-        reasons.append("AMBIGUOUS: samples absent")

### X07 SURVIVED | launched_by_systemd: a transient .scope accepted as the campaign unit
@@ -633 +633 @@
-            if last.startswith(prefix) and last.endswith(".service"):
+            if last.startswith(prefix) and last.endswith((".service", ".scope")):

### X08 SURVIVED | v1 'unlimited' sentinel lowered to 1 GiB  (a 2e9 limit read as no limit: allowance -> MemTotal)
@@ -43 +43 @@
-UNLIMITED_CGROUP_V1 = 2 ** 62                   # memory.limit_in_bytes at or above this is "no limit" (v1 sentinel)
+UNLIMITED_CGROUP_V1 = 2 ** 30                   # memory.limit_in_bytes at or above this is "no limit" (v1 sentinel)

### X09 SURVIVED | pins: an interpreter whose dpkg owner is unknown silently drops out of the package pin
@@ -761 +761 @@
-    return (owner or "<unknown-interpreter-package>", f"libpython{v}-stdlib")
+    return tuple(x for x in (owner, f"libpython{v}-stdlib") if x)

### X10 KILLED (test_namespace_mismatch_is_unknown) | ESRCH proves death when the reader's namespaces are unreadable
@@ -171 +171 @@
-        if ident.get(k) is not None and ns.get(k) != ident[k]:
+        if ident.get(k) is not None and ns.get(k) is not None and ns.get(k) != ident[k]:

### X11 KILLED (test_power_classes) | Mains 'online' unreadable treated as offline
@@ -292 +292 @@
-                return None
+                on = "0"

### X12 KILLED (test_unreadable_pins_never_match) | an EMPTY dict pin counts as readable
@@ -799 +799 @@
-        return v is None or (isinstance(v, dict) and (not v or any(x is None for x in v.values())))
+        return v is None or (isinstance(v, dict) and any(x is None for x in v.values()))
```

X07 is mitigated in practice by the MainPID check, since a scope has `MainPID=0`, but the unit-type property itself is
untested.

**Committed harness, re-run by this reviewer** (no output file): unmutated suite PASS; **42/42 killed**; R01–R10
10/10; lx_platform and tests sha256 equal to the recorded values.
