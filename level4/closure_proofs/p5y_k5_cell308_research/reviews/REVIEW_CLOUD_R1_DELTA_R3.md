# Review — DELTA of revision 3 and amendment r3 after review 60 (Cell 308, MB-S successor, S4 changed branch, Cloud route r1)

* Reviewer: **reviewCLOUD_R1_DELTA2 (fresh agent, brief 61)**
* Date: 2026-10-14 (UTC). The session began at about 20:29Z. A usage limit and a VM worker restart interrupted it, and it
  resumed at about 23:40Z. All process-memory results were re-derived after the restart, and every scratch output
  cited here was regenerated after it.
* Delta reviewed: **ff9006ac..d423c7aa** (HEAD = `d423c7aacc4d1cc15f3c7d77aecb5257a0175392`) on branch
  `claude/cell-308-github-state-skb1g0`. The delta has six commits: 13e11bc3, 8e67a181, bd8da316, 66be23c3, 8bb1c351
  and d423c7aa. The working tree was clean at the start and at the end (`git status --porcelain` empty).
* NS = `level4/closure_proofs/p5y_k5_cell308_research/`. Paths are relative to NS unless stated. Line numbers refer to
  the HEAD files.
* `new_target_evaluations = 0`. No cell, drift, certificate, decoy, science module, qualification case, candidate
  code or quarantine guard was run. Nothing was installed and no setting was changed. No repository file was written.
* Scratch directory: `/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review61/`
  ("scratch" below).

---

## 1. Exposure disclosure

**Files opened in full:**
* Review 60 (`reviews/REVIEW_CLOUD_R1_DELTA_R2.md`).
* At HEAD:
  * `lx_platform.py`, `tests/test_lx_platform.py`, `tests/run_mutants.py` and `results/TEST_RUN.json`;
  * the summary of `results/MUTANTS_RUN.json`;
  * the `git diff ff9006ac..HEAD` of lx_platform.py, lx_inventory.py and README_DEV_ONLY.md;
  * PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R3.md and OWNER_DECISION_BRIEF_CLOUD_R1_R3.md;
  * the lines removed in r3 relative to r2 (`diff r2 r3`);
  * the three added ledger lines (467–469) and the two added BRIEF_INDEX rows;
  * review 60's scratch scripts `probes60.py`, `quotecheck.py.txt` and `probe_zombie_leader.py`, and the head of
    `reviewer60_mutants.py`.

**Accepted sources, read only as grep or sed extracts:**
* `governance/CONSTANTS_RATIFICATION_MBS308.md`: rows 24 and 25 (line 29 is ratification row 24, which carries the
  ratification's own H1/H2 macOS host-readiness readings).
* `governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md`: grep hits at lines 89, 91, 254, 411, 414 and 428, plus its
  headings. Lines 89 and 91 are the brief's own macOS host readings.
* `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`: lines 112–118.

`quotecheck61.py` also read the following whole files programmatically, for substring matching only:
* `governance/SUCCESSOR_GOVERNANCE_308*.md`;
* `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1*.md`;
* `governance/new_host_route_cloud_r1/ROUTE_PREPARATION.md`.

**Candidate:** `git show 142d97a9:…/p5y_k5_cell308_mbs_r1/code/mbs308_host.py`, `identity_state` only (lines 435–466).
The suite itself reads two constants from that file.

**Host (read-only):**
* `/proc/1/comm`, `/proc/self/ns/{pid,cgroup}`, `/proc/self/status` (NSpid) and `/proc/self/cgroup`;
* listings of `timers.target.wants` and `/run/systemd/system`;
* interpreter versions.

**Network (read-only):** one `curl` GET of `https://code.claude.com/docs/en/self-hosted-environments` at about
23:43Z, saved to `scratch/fetched/` (sha256 `b074611d…`). It was used only to check the owner brief's V-A quotation.

**Namespaces:** `unshare` was used five times: once with no flags, twice with `--cgroup`, once with
`--pid --fork --mount-proc`, and once more with `--cgroup` for the Y04 check. Each run read the scratch copy only, and
the namespaces ended with the process.

**Not opened, grepped or read:**
* `audit/EXECUTION_INTERRUPTION_ASSESSMENT*` and `audit/INCIDENT_AUDIT*`;
* `reviews/REVIEW_EXECUTION_INTERRUPTION*`;
* anything under `p5y_k5_cell308_mb_r1/postexec/`, or any MB r1 target-run record;
* `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`;
* any Cell-309 branch, file or record.

**Name-level contact only:** a listing of the session scratchpad root showed the coordinator's files
`MUTANTS_RUN_R3.json`, `gate.txt`, `inv_check.json`, `mut2.log`, `mut3.log` and `scan*.json`. None was opened. I also
listed `scratchpad/review60/` and hashed its review file, without reading it.

I hold no E1″ material and no MB r1 target-run runtime or host observation.

---

## 2. Verdicts

DELTA: DELTA_ACCEPTED_WITH_CONDITIONS
AMENDMENT_DRAFT_R3: FIT_WITH_CONDITIONS
DEV_CODE_R3: FAIL_CLOSED_WITH_DEFECTS

**No verdict here accepts the amendment.** Only three things can accept, reject or put it into force:
* a formal independent route / governance review;
* a fresh S12 incident-independence re-rating;
* the owner's decisions (OD-1 to OD-3 and the [OPEN] items).

This is a delta review of a draft and a development layer.

**Why each verdict:**

* **DEV_CODE_R3 = FAIL_CLOSED_WITH_DEFECTS**, not CONFIRMED and not NOT_FAIL_CLOSED.
  * Every path review 60 demonstrated is now closed. These were re-probed against a copy, sha256 `6978cba7…`:
    * an unrecognised battery status;
    * a truthy root flag other than `True`;
    * a forged dict attestation;
    * an invalid boot id;
    * a nested PID namespace (`unshare` probe: `proc_view_complete() == False`);
    * an unrecorded namespace with ESRCH or a starttime difference;
    * an exited hog;
    * an unreadable pid.
  * I found no path where a **failed, absent, unrecognised or rejected reading** yields PASS, ALIVE, AC, a numeric
    allowance, a complete /proc view or CLEAN.
  * What remains is a class of **caller-asserted / self-designated** inputs, each demonstrated:
    * a literal `root_attested=True` gives a numeric allowance, even when the module's own reading shows a non-initial
      cgroup namespace. Live, that allowance is **inflated**: 16 874 930 176 instead of the real leaf limit
      14 343 688 192 (P2);
    * an attestation chooses its own "acceptance record", which can be any committed file, including a review that
      rejects it (P1);
    * a `decided` argument, even the string `"xxD-HOST-LIFETIMExx"`, opens D-HOST-LIFETIME. With P1 this gives PASS on
      two gates (P5);
    * a caller-built launch record gives `launched_by_systemd = PASS` on this non-systemd host (P6);
    * a caller-supplied empty journal list gives CLEAN with no journal reader in existence (P7);
    * 6 of my 9 new mutants survive (P4).
  * The defects are rated "with defects", not NOT_FAIL_CLOSED, for three reasons:
    * no reading failure passes;
    * `preflight` cannot pass, because five gates stay `OPEN_DECISION` whatever `decided` holds (probe B2b);
    * each remaining path needs a caller to assert something.
  * A stricter reading of the brief's "caller-asserted input" clause would give NOT_FAIL_CLOSED. The finding list is
    the same either way.
* **AMENDMENT_DRAFT_R3 = FIT_WITH_CONDITIONS.**
  * Resolved in r3:
    * the §4 labels are complete (N9), and every new [ACCEPTED] quotation is verbatim;
    * the L-DET repeat rule is withdrawn (N10);
    * the F4 deviation is recorded with an adequate reason;
    * C1 is honoured;
    * no accepted rule is relaxed.
  * Still open: §3 again asserts code properties that do not hold, in L-FREE, L-LIFE, L-SLEEP and L-LAUNCH (P3), and
    §4's D-HOST-LIFETIME row contradicts §0.
  * The owner brief asks the owner to commission a review of "amendment r2" (P12).
* **DELTA = DELTA_ACCEPTED_WITH_CONDITIONS.**
  * The repairs of N2, N4, N6, N7, N8, N9, N13 and N14 are accepted. N1, N3, N11 and N12 are partially resolved.
  * The records check out:
    * every bound hash recomputes;
    * a fresh harness run reproduces `MUTANTS_RUN.json` mutant by mutant (65/65);
    * a fresh suite run reproduces TEST_RUN (75 OK on 3.11.17, 3.12.3 and 3.13.16);
    * r1/r2 and review 59/60 are byte-unchanged.
  * Conditions are in §5 (D1–D4).

---

## 3. Q1 — Status of review 60's findings and conditions

| item | sev (r60) | status | evidence |
|---|---|---|---|
| N1 | MAJOR | **PARTIALLY RESOLVED** | Resolved: (a) `preflight:962–981`: `host_lifetime_attested` and the provider-image half of `no_automatic_os_install` are `OPEN_DECISION` while `"D-HOST-LIFETIME" not in decided` (default `DECIDED = frozenset()`); probe `A_N1_forged_gates_default_decided` both OPEN_DECISION. (b) `attestation_valid:887–920` takes only `{path, sha256}` and reads every fact from the committed blob; review 60's forged dict is refused ("reference must be exactly {path, sha256}"), `README.md` as reference is refused ("not JSON"); `"REJECTED"`, `"false"`, `1` read from the file are refused (A_P3). Tests `test_attestation_read_from_the_committed_file`, `test_forged_or_unaccepted_attestations_refused`, `test_reference_digest_must_match_the_committed_file`, `test_lifetime_gates_open_while_undecided`. **Not resolved:** review 60 required that `acceptance_record` be "a committed review that names the attestation's sha256 **and accepts it**". The code accepts **any committed file the attestation itself names** that contains the whole line, including a scratch note, a file next to the attestation, and a review whose verdict is REJECTED but which quotes the line (B1: all three `valid: true`; with `decided` both gates PASS). The `decided` override is itself caller-asserted and unvalidated (P5). See P1, P5. |
| N2 | MAJOR | **RESOLVED** | `power_source:312–317`, `KNOWN_NOT_DISCHARGING`. Re-probe: `Unknown`, `garbage`, `discharging`, `"Discharging \x00"`, `""` and a status directory all give None; `Not charging` and `Full` give AC; UPS Discharging gives BATTERY; unreadable type gives None. Test `test_unrecognised_battery_status_is_unknown`; R01 and N14 killed. |
| N3 | MAJOR | **PARTIALLY RESOLVED** | Resolved: `is True` at `:420`, `:433`, `:455`, `:509`. All of `"no"`, `"false"`, `"REJECTED"`, `1`, `{"accepted": False}`, `[True]` and `1.0` give `[None, None]` (A_N3). `cgroup_resources` reads cpu / cpuset / pids along the whole chain (`:485–498`, test; my Y09 killed). Not resolved: (a) "derived from a verified attestation rather than passed in" is only a docstring (`:505–506`). `root_cgroup_is_real` is consumed nowhere (grep: docstrings only), and a caller literal `True` gives `[3000, 2990]`. (b) "Return None in a non-initial cgroup namespace unless attested": the namespace is now **recorded** (`cgroup_ns_initial`), but a positively non-initial namespace does not block a number when the caller passes True. **Live demonstration** (`ns_probe61b_out.txt`): under `unshare --cgroup`, `memory_readings(root_attested=True)` sees the chain `["/"]` and gives `effective_limit = 16 874 930 176` (MemTotal), while the true leaf limit, read in the initial namespace, is `14 343 688 192`. The output also carries `cgroup_ns_initial: false`. See P2. |
| N4 | MAJOR | **RESOLVED** | `proc_view_complete:534–557` requires `ns_inode("pid") == 0xEFFFFFFC`. `unshare --pid --fork --mount-proc`: NSpid `1`, pidns `4026532265`, `proc_view_complete() == False`, `cpu_ticks` sees 1 process (`ns_probe61_out.txt`). In the initial namespace, True. Test `test_proc_view`; X01, X02 and N06 killed. |
| N5 | MAJOR | **RESOLVED as specified** | X01–X09 are in `run_mutants.py:119–137`, re-anchored with the same weakening (checked by eye against `reviewer60_mutants.py`). My fresh run: 65/65 killed, X 9/9, R 10/10, unmutated suite PASS. However **6 of my 9 new mutants survive** (§6, P4). |
| N6 | MINOR | **RESOLVED** | `:977` validates with `boot_id()`. `""`, `"garbage"`, `0`, `False` and the uppercase form give UNKNOWN (A_N6). Test `test_boot_id_must_be_valid`; N07 killed. |
| N7 | MINOR | **RESOLVED** | Exited processes are reported with `pct None` (`:608–610`; A_N7 shows the hog). An existing but unreadable `/proc/<pid>` makes the snapshot None (`:571–573`; A_N7 shows None). `own` is keyed by (pid, starttime), and a child of a reused campaign pid counts (A_N7 shows it reported). Tests in `TestBusy`; N08, N09 and N10 killed. Residual test gap: the start-time condition in the **exited** loop is untested (Y02 survives; P4). |
| N8 | MINOR | **RESOLVED** | `:185–189`. An unrecorded namespace with ESRCH, or with a different starttime, gives UNKNOWN (A_N8). A boot-id change stays DEAD (test). Test `test_unrecorded_namespace_never_proves_death`; N11 killed. |
| N9 | MINOR | **RESOLVED** | §4 lines 135–142: D-MEM-PRESSURE amends ratification row 24 (verified: line 29, `kern.memorystatus_vm_pressure_level` = 1) and the brief R2 §9 Memory row. D-THERMAL amends the brief R2 §9 "Thermal pressure level 0" row (verified: brief line 414). D-LPM amends row 25 (verified: line 30) and the "Low Power Mode off" row (line 411). D-EXCL-WINDOW "changes R-EXCL-PCT's measured quantity". D-PAUSE / L-AWAKE quotes the brief "EVAL_CAP applies **per attempt, on awake time** (CLOCK_UPTIME_RAW)", which is verbatim (line 254). OD-2 is reworded and states 20 decisions, which equals the §4 row count. |
| N10 | MINOR | **RESOLVED** (repeat) / **CARRIED-AS-CONDITION** (digests) | §5 item 5: no repeat, and r2's rule is withdrawn. New §4 row D-LDET-REPEAT, labelled a "new rule". The digests (records, strip, serializer) are carried in item 1 as an explicit condition: they must be in the text the formal review accepts before OD-3, and the owner brief OD-3 says the same. Acceptable to carry, because it gates OD-3 and no run is authorised. |
| N11 | NOTE | **PARTIALLY RESOLVED** | Required members are enforced (`:772–774`); A_N11 shows a maps text without libm gives None and a `(deleted)` mapping gives None; test. The unknown-owner path is tested (X09 killed). Not resolved: (a) the "fixed import list" is still prose. `pin_point(modules)` takes the list from the caller and accepts `()` (B8: returns a pin), and the amendment names no list. (b) The loader membership is untested (Y06 survives). See P4, P11. |
| N12 | NOTE | **PARTIALLY RESOLVED** | A non-dict record now gives FAIL, not AttributeError (A_N12: `launched=True` gives FAIL). But the "verify the record's fields" option is implemented as a **self-consistency** check of caller data. Nothing is compared with `os.environ["INVOCATION_ID"]`, `/proc/self/cgroup` or a fresh `systemctl show`. A caller-built dict gives PASS on this host, where `launched_by_systemd()["pass"] is False` and `INVOCATION_ID` is unset (B3). See P6. |
| N13 | NOTE | **RESOLVED** (with NOTE P10) | `test_live_host_is_never_clean` passes `[]` (`:292–296`). `test_dump_lines_only` is renamed. The kernel test is sharpened against the r1 inventory. The live-host tests are host-dependent (P10). |
| N14 | NOTE | **RESOLVED** | Ledger line 468 carries `correction_of_earlier_line`, and the earlier line is unedited (numstat +3/−0). D-S15-NEWHOST now quotes S15 in full, verbatim (quotecheck). Owner brief r3 V-A quotes "the session resumes on a fresh runner when the user sends their next message". This is **verbatim on the live page**, which I fetched at about 23:43Z (`scratch/fetched/self-hosted-environments.html`, sha256 `b074611d…`), in the retire-time / idle-release passage. The brief honestly says the extract is not stored in the repository, so whether it was present at 18:52Z is UNVERIFIED. |
| C1 | condition | **RESOLVED** (honoured at HEAD) | Amendment §3 preamble (lines 86–89) and README line 15 state that no L-* row cites revision-3 code before this review. No row in §3 cites it as accepted. For which rows may now cite revision 3, see §5 D1. |
| C2 | condition | **PARTIALLY RESOLVED** | Done: §4 labels (N9); the L-DET repeat rule (N10); the digests carried as a condition (F5); the F4 deviation recorded in §11 with its reason; §0's OPEN_DECISION rule now holds in the code for D-HOST-LIFETIME by default. Not done: §3 claims that are again false of the code (P3), namely L-FREE "never a caller flag", L-LIFE "itself a committed review" and "none from the caller", L-SLEEP "L′ is always AMBIGUOUS", and L-LAUNCH "fields all verify". §4's D-HOST-LIFETIME row says "if unresolved: gate UNKNOWN", while §0 and the code say OPEN_DECISION. |
| C3 (r60 §6 item 3) | condition | **RESOLVED** | Ledger line 468 (see N14). |

**Tally (N1–N14):**
* RESOLVED: 9 (N2, N4, N5 as specified, N6, N7, N8, N9, N13, N14).
* N10: RESOLVED / CARRIED.
* PARTIALLY RESOLVED: 4 (N1, N3, N11, N12).
* NOT RESOLVED: 0.

Conditions: C1 and C3 resolved; C2 partial.

---

## 4. Answers Q2–Q5

### Q2 — Fail-closed audit of revision 3 (adversarial)

**Review 60's probes, re-run.** `probes60.py` uses revision 2's API (`host_attestation=`), so I ported it unchanged in
substance as part A of `scratch/probes61.py`. Output is in `probes61_out.json`, against a copy with sha256 `6978cba7…`.
Review 59's P1–P8 and P10, carried inside probes60, are included.

* Every review-60 demonstration is closed: P1, P1b, the five N2 statuses, P2 (×3), P3 (×3), the N1 forgery, N6 (×5),
  launcher-mode `True`, the N3 truthy values (×7), the N4 live and nested-namespace cases, the N7 hog, unreadable
  pid and reused pid, and the N8 ESRCH and starttime cases.
* Review 59's P6 zombie probe was re-run unchanged on the copy (`probe_zombie_leader_rev3_out.json`). The leader is in
  `Z` with `Threads: 2`, ticks rise 86→137→187→237, and `identity_state` is **UNKNOWN** on all four readings.

**New adversarial probes (part B, and the `unshare` probes).**

| # | input class | result | finding |
|---|---|---|---|
| B1 | self-designated acceptance: the attestation names `scratch/anything.txt`, `att/ACCEPT_BY_SELF.txt`, or a `reviews/REVIEW_X.md` that says "Verdict: REJECTED … We refuse." around the line | `attestation_valid` **valid** in all three; with `decided={"D-HOST-LIFETIME"}`, `host_lifetime_attested` = **PASS** and `no_automatic_os_install` = **PASS** | P1 |
| B2 | caller-asserted `decided`: `"D-HOST-LIFETIME"`, `"xxD-HOST-LIFETIMExx"` (a substring test on str), a list, a set, a dict | both gates **PASS** in every case (with an injected valid attestation) | P5 |
| B2b | `decided = all D-* ids` | lowpowermode, thermal, memory pressure, free memory and host_exclusive stay OPEN_DECISION: `decided` does not unlock them, contrary to the docstring at `:951–953` | P5 |
| B3 | caller-built launch record on a host with no systemd (`/proc/1/comm = process_api`, `INVOCATION_ID` unset) | `launched_by_systemd` gate = **PASS**; a float MainPID is also accepted | P6 |
| B4 | malformed recorded `boot_id` (`"garbage"`, truncated); negative recorded pid | **DEAD** (kill(−N, 0) has process-group semantics and returns ESRCH). The same in revision 2 and in the candidate's `identity_state` (git show 142d97a9, lines 446–451) | P9 (NOTE, inherited) |
| B5 | `assess(…, journal_suspend_events=[])` with no journal reader in existence | **CLEAN** (None gives AMBIGUOUS). The same in revision 2 | P7 |
| B6 | `timers_dir` absent, or the timer enabled only under another unit path | `guest_updates_shown_disabled` = **True**. The same in revision 2 | P8 |
| B7 | `unshare --cgroup` plus caller `root_attested=True` | live `effective_limit` **16 874 930 176** (MemTotal) vs the real leaf limit 14 343 688 192; `cgroup_ns_initial: false` is reported alongside | P2 |
| B8 | `pin_point(())` | returns a pin; no fixed list exists | P11 |
| B10 | `own={(True, 5)}`; `own={("99", 1)}` | None; the str key is simply not matched (the child is charged), so fail-closed | — |

**Classes not found:**
* No path to **ALIVE**: ALIVE needs every field, both namespaces and a live non-Z/X state.
* No path to **AC** from an unrecognised supply.
* No path to a **complete /proc view** from a nested namespace, `hidepid`/`subset`, a missing `/proc` line or an
  unreadable namespace.

**Tests that cannot or practically cannot fail.** None of the review-60 kind remains. Three live-host tests are
host-dependent instead (P10).

**New mutants:** 9 written, **3 killed and 6 survived** (§6). Each survivor was shown to change an outcome on a
synthetic input (`equiv61_out.json`, `equiv61_out_y04_unshare.txt`):
* Y01: `decided={"D-MEM-FREE"}` turns OPEN_DECISION into **PASS**.
* Y02: an exited child of a reused campaign pid is no longer reported.
* Y03: a rejecting sentence containing the token is accepted.
* Y04: in a new cgroup namespace, `cgroup_ns_initial` reads True.
* Y05: an attestation of an image-cloned VM (same machine-id, different DMI uuid) is accepted. This is the F20 case.
* Y06: a pin without the loader is accepted.

### Q3 — Regressions and strictness

**No regression found:**
* **Zombie rule:** unchanged (`:199–200`). P6 was re-probed (UNKNOWN), and M04 and R07 were killed.
* **Pins:** `PIN_KEYS` and `pin_mismatches` are unchanged. `mapped_objects` is stricter (required members). The
  `TestPins` tests pass, and M17, M30 and R06 are killed.
* **durable_write:** byte-identical in the diff. M16, R03, R08 and X05 are killed, and the crash-injection test passes.
* **R01–R10:** 10/10 killed in my fresh run. R01 is re-anchored to the new status check, and its weakening ("an
  unreadable status skipped") is preserved as a superset.
* **`assess`, `auto_update_settings`, `launched_by_systemd`:** unchanged code.
* **Pre-existing paths:** B4, B5 and B6 behave identically in revision 2 (`preexisting61_out.txt`). They are
  pre-existing, not regressions.

**NOTES — stricter, possibly unattainable on a legitimate host (deliberate fail-closed, not defects):**
* `busy_processes` reports **every** process present at t0 and gone at t1 (cron jobs, `git`, the operator's shell
  commands), with `pct None`. `cpu_ticks` returns None if a process is exiting, so that its `/proc/<pid>` directory
  exists but its `stat` cannot be read, which is a normal race. If the future gate refuses on any reported entry,
  `host_exclusive` may be unattainable on an ordinary systemd host. The amendment says "may be unattainable" only under
  D-ALLOW-PATHS, not under D-EXCL-WINDOW / L-EXCL.
* A peripheral (scope = Device) battery with status `Unknown`, such as a Bluetooth mouse, now makes `power_source`
  None, so `ac_power` is UNKNOWN on such a laptop. This is new in revision 3 (N2) and unstated.
* `proc_view_complete` is False in any container or nested PID namespace. That is correct, but on such a host
  `test_live_snapshot` then fails the suite (see P10).

### Q4 — Amendment r3

* **§3 fail-closed claims.**
  * True of the code now: L-POWER, L-EXCL, L-ID, L-BOOT, L-PIN (except that the "fixed module list" is not fixed), L-UPD
    (except the timer-path gap, P8) and L-DISK.
  * **False (P3):**
    * **L-FREE:** "`root_attested is True`, taken from a verified attestation's `root_cgroup_is_real` field (H6), never a
      caller flag". It is a caller flag, and the field is read nowhere (B7 / P2).
    * **L-LIFE:** "an `acceptance_record` that is itself a committed review containing the line … Every fact is read
      from the committed files, none from the caller". Any committed file counts, including a rejecting review (B1);
      the attestation chooses its own acceptance record; and `decided` comes from the caller (B2).
    * **L-SLEEP:** "L′ … no reader exists yet, so L′ is always AMBIGUOUS". A caller `[]` gives CLEAN (B5).
    * **L-LAUNCH:** "a launch record whose **fields** all verify". The fields are only checked against each other
      (B3).
  * §4 D-HOST-LIFETIME: "if unresolved: gate UNKNOWN" contradicts §0 and `preflight` (OPEN_DECISION).
* **§4 labels.**
  * Complete for the 20 rows.
  * Each relabel was checked against its source: rows 24 and 25 at ratification lines 29–30; brief R2 lines 254, 411
    and 414.
  * D-LDET-REPEAT is labelled correctly as a new rule.
  * The new "HOST_ATTESTATION_ACCEPTED sha256=" acceptance convention is a new governance mechanism, part of
    D-HOST-LIFETIME's "new rule". It should be named there, because it decides what counts as a review's acceptance
    (P1).
* **§5 L-DET.**
  * Faithful to MBR1_REPRO (route A1 §3, verbatim):
    * the case set by name;
    * "through the successor's code" (item 2);
    * exact leaf equality with timing stripped (item 4a, plus a stricter byte equality 4b);
    * mismatch means STOP / S4 changed branch (item 6);
    * E8 (item 8 restates it for L-DET records; E8's wider scope stays governed by its own text).
  * **No repeat** (item 5) is stricter than MBR1_REPRO, which is silent. That is acceptable, and it is listed as D-LDET-REPEAT.
  * The reference-digest condition is carried explicitly into the formal review and gates OPEN OD-3. The `c46434a3`
    provenance is now stated as "to be identified there, not assumed", which resolves review 60's UNVERIFIED point.
* **F4 deviation (§11).** Adequately justified.
  * Incident-review N3 (line 116–118, read) includes "The MBR1_REPRO case reproduces MB r1's committed r3 non-target
    records exactly", and its pin clauses compare the successor with itself.
  * So whether N3, and hence T1, fails off-platform is exactly the D-RC2-SCOPE reading.
  * The default treatment is the conservative one (HIGH, decisive argument lost, a second, different draw), and it can
    change only by an independent reviewer **and** the owner.
* **[ACCEPTED] quotations.** `quotecheck61.py` (review 60's checker, extended) found every quotation present in r3
  verbatim in its source (`quotecheck61_out.json`):
  * review 60's set: the HOST row, DR2, MBS-5(b), route A1 §1 and §3, "not settled", incident lines 129 and T1, S5, S7,
    S10, S13, E1 D2, E1 D3, [PREPARATION] and the fragments;
  * the new r3 ones: S15 in full, brief R2 EVAL_CAP awake time, "Thermal pressure level 0", "Low Power Mode off", and
    the ratified keys.

  None is non-verbatim.

### Q5 — Records

* **Ledger lines after ff9006ac.** These are 467 (13e11bc3), 468 (8e67a181) and 469 (d423c7aa); the diff removes 0
  lines. Every bound sha256 recomputes from the HEAD bytes:
  * brief 59 `9b78af71…`, brief 60 `54e3ef2d…`;
  * review 60 `8c242e5f…`, which also equals the original `scratchpad/review60/REVIEW_CLOUD_R1_DELTA_R2.md`, so it was
    recorded verbatim;
  * amendment r3 `5f121941…`, owner brief r3 `3291feb1…`;
  * lx_platform `6978cba7…`, lx_inventory `8ea74ed3…`;
  * tests `e7f9b2d6…`, run_mutants `9feca6b4…`;
  * TEST_RUN `2d168594…`, MUTANTS_RUN `e2db08c2…`, README `003f6722…`;
  * brief 61 `c4b3caa4…`.
* **Counts in line 469.**
  * "75/75 OK on CPython 3.11.17, 3.12.3, 3.13.16": re-run with `-B -W error::ResourceWarning`, 75 OK on each.
  * "65/65 killed (R 10/10; X 9/9)": re-run, correct.
  * `open_decisions_count 20`: correct.
  * The review-60 counts in line 468 match review 60 §3 and §5.
* **TEST_RUN.json.** Its `lx_platform_sha256` and `tests_sha256` equal HEAD. Its "Ran 75" matches my run. Its boot id
  `00661362…` is a different boot from mine (`2fe3cc44…`; the VM was restarted), which is consistent.
* **MUTANTS_RUN.json.** My fresh `python3 -B tests/run_mutants.py` (no output argument; stdout in
  `scratch/committed_mutants_stdout.json`) equals it in both hashes, the unmutated PASS, 65/65, the R and X counts and
  every (id, status) pair. No mutant is NOT_APPLIED.
* **Byte-unchanged files.** `git diff ff9006ac..HEAD` is empty for:
  * PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md and _R2.md;
  * OWNER_DECISION_BRIEF_CLOUD_R1.md and _R2.md;
  * REVIEW_CLOUD_R1_FEASIBILITY_AMENDMENT_DEV.md.

  REVIEW_CLOUD_R1_DELTA_R2.md is unchanged since it was recorded in 8e67a181. The only change to review-60 scratch is
  the rename `quotecheck.py → .py.txt`, with 0 content change (disclosed in ledger 469 `process_notes`).
* **Scope.** Every path changed in the delta lies under NS. No path is under `p5y_k5_cell308_mbs_r1/` or
  `p5y_k5_cell308_mb_r1/`. Live remote tips are unchanged: candidate `142d97a9…`, research `88a16f74…`
  (`git ls-remote`).
* **Inaccuracies (P13):**
  * amendment §3 and README say "74 tests" (HEAD has 75);
  * the harness docstring says "N01-N12" (N01–N14 exist);
  * the line-1 docstrings of lx_platform.py and test_lx_platform.py still say "revision 2";
  * §10 cites `test_launch_gate_modes`, which no longer exists;
  * M25 survived the first revision-3 suite. I confirmed this: run against the test file of 66be23c3, M25 adds no
    failure (`reviewer61_mutants_result.json`, `M25_vs_tests_at_66be23c3`). This is disclosed only in commit
    8bb1c351's message, not in ledger 469's `process_notes`.

---

## 5. New findings

**P1 — MAJOR — The attestation designates its own acceptance record, and any committed file containing the line counts,
including a review that rejects it.**
* **Location:** `lx_platform.py:916–919`; amendment §3 L-LIFE (line 114); §11 N1 row.
* **Evidence:** probe B1. With `decided`, two gates PASS. Y03 (substring match) survives too.
* **Correction:**
  * Fix the acceptance record outside the attestation: for example a fixed `reviews/` path pattern, or a ledger REVIEW
    line whose recomputed `review_sha256` and a verdict field name this attestation's sha256 as ACCEPTED.
  * Refuse a record outside that set, refuse an acceptance record written in the same commit as the attestation, and
    refuse any record that also carries a REJECTED verdict.
  * Name the mechanism in §4 D-HOST-LIFETIME as a new rule.
  * Add tests for B1's three cases, and kill Y03.

**P2 — MAJOR — A caller literal `root_attested=True` yields a numeric allowance, even in a positively non-initial cgroup
namespace (live: inflated to MemTotal).**
* **Location:** `lx_platform.py:430–438`, `:452–456`, `:502–516`; amendment L-FREE (line 104), H6.
* **Evidence:** `ns_probe61b_out.txt`: `effective_limit` 16 874 930 176 under `unshare --cgroup`, against the true
  14 343 688 192.
* **Correction:**
  * Take root attestation only from an `attestation_valid()` record (`rec["root_cgroup_is_real"] is True`) passed as
    that record, not as a boolean.
  * Return None whenever `ns_inode("cgroup") != INIT_CGROUP_NS`, or when the namespace is unreadable, whatever the
    attestation says: the reader's own namespace hides ancestors on this very host.
  * Add a test that kills Y04.

**P3 — MAJOR — Amendment r3 §3 again states fail-closed properties the code does not have (C2 not fully met).**
* **Location:**
  * L-FREE (line 104): "never a caller flag";
  * L-LIFE (line 114): "itself a committed review", "none from the caller";
  * L-SLEEP (line 97): "L′ is always AMBIGUOUS";
  * L-LAUNCH (line 93): "fields all verify";
  * §4 D-HOST-LIFETIME (line 143): "gate UNKNOWN", against §0.
* **Evidence:** B7, B1, B2, B5, B3.
* **Correction:** fix the code (P1, P2, P5–P7), or restate each row exactly as implemented and carry it as a
  condition. Either way, the D-HOST-LIFETIME row must say OPEN_DECISION.

**P4 — MAJOR — The suite does not pin six revision-3 properties: 6 of 9 new mutants survive.**
* **Location:** `tests/test_lx_platform.py`, `tests/run_mutants.py`.
* **Evidence:** §6, with equivalence shown for each survivor. Y05 is the F20 hardware-binding property: an
  image-cloned VM with the same machine-id is accepted. Y06 is N11's loader membership.
* **Correction:** add tests that kill Y01–Y06, and add Y01–Y09 to the harness beside M, R, X and N.

**P5 — MINOR — `decided` is a caller-asserted, unvalidated parameter of the production `preflight`.**
* **Location:** `lx_platform.py:948`, `:962`; docstring `:951–953`.
* **Evidence:** B2: a str is tested by substring, so `"xxD-HOST-LIFETIMExx"` opens the decision. Any container works.
  B2b: the docstring claims other gates depend on `decided`; they are hard-wired.
* **Correction:**
  * Derive `decided` from a committed, reviewed decision record, as for P1, or keep it a module constant and remove
    the parameter from the production signature.
  * Require a `frozenset` of known D-* ids.
  * Correct the docstring.

**P6 — MINOR — The launch record is checked only for self-consistency; a caller-built record passes on a host without
systemd.**
* **Location:** `lx_platform.py:935–944`, `:983–984`; amendment L-LAUNCH.
* **Evidence:** B3: PASS while `launched_by_systemd()["pass"] is False` and `INVOCATION_ID` is unset. A float MainPID is
  accepted.
* **Correction:** for execute / resume, call `launched_by_systemd()` inside `preflight` and require equality with the
  record, or compare the record with `os.environ["INVOCATION_ID"]`, `/proc/self/cgroup` and a fresh `systemctl show`.
  Require an `int`, non-bool MainPID.

**P7 — MINOR — Channel L′ is silenced by a caller-supplied `[]` although no journal reader exists; `assess` returns
CLEAN.**
* **Location:** `lx_platform.py:261–264`; docstring `:234–235`; amendment L-SLEEP.
* **Evidence:** B5. The behaviour is pre-existing (revision 2 identical).
* **Correction:** until a reviewed journal reader exists, treat L′ as AMBIGUOUS whatever the caller passes. Or accept
  only a value produced by that reader (a typed result), not a bare list.

**P8 — MINOR — The apt-daily-upgrade timer vector is checked in one directory only; an absent directory, or a timer
enabled elsewhere, reads as "no timer".**
* **Location:** `lx_platform.py:624`, `:638`.
* **Evidence:** B6. The behaviour is pre-existing.
* **Correction:** use `systemctl is-enabled apt-daily-upgrade.timer` (read-only), or every unit search path, with an
  unreadable result giving None, so that the vector is not shown disabled. Consider `apt-daily.timer` and
  `unattended-upgrades.service` too. Add a test.

**P9 — NOTE — `identity_state` lets an unvalidated recorded field prove DEAD (malformed boot id; negative pid with
process-group `kill` semantics).**
* **Location:** `lx_platform.py:177–195`.
* **Evidence:** B4. The behaviour is inherited verbatim from the accepted candidate semantics (`mbs308_host.py:441–451`)
  and from revision 2, so it is not a regression.
* **Correction:** validate the record's shape (`boot_id` by `_BOOT_ID`, pid a positive non-bool int) and give UNKNOWN
  otherwise, or record why the R2 semantics are kept unchanged.

**P10 — NOTE — Strictness and host-dependence.**
* **Location:** `busy_processes:608–610`, `cpu_ticks:571–573`, `power_source:316–317`; tests
  `test_live_host_is_never_clean`, `test_r1_recorded_kernel_is_not_this_hosts`, `test_live_snapshot`.
* **Evidence:**
  * Exclusivity may be unattainable on an ordinary host: short-lived processes are reported, and the exit race gives
    None.
  * A peripheral battery with status `Unknown` gives UNKNOWN power.
  * The three tests assert properties of *this* Cloud VM. On a legitimate official host they would fail: an idle host
    with AC and `suspend_stats` is CLEAN; the r1 kernel host; any nested PID namespace.
* **Correction:** state these consequences under D-EXCL-WINDOW and D-POWER-ABSENT, and mark the live tests as
  host-dependent, or make them conditional on the host facts they assume.

**P11 — NOTE — The pin point's "fixed module list" exists neither in code nor in the amendment.**
* **Location:** `lx_platform.py:818–826`; amendment L-PIN.
* **Evidence:** B8: `pin_point(())` returns a pin.
* **Correction:** define the list as a module constant once the science imports are known, or name it in the amendment
  as an item for the formal review. Refuse an empty list.

**P12 — MINOR — Owner brief r3 OD-2 asks the owner to commission the formal review of "amendment r2".**
* **Location:** `OWNER_DECISION_BRIEF_CLOUD_R1_R3.md:39`.
* **Correction:** issue a corrected brief (r3 erratum or r4) naming amendment r3, and record it in a ledger line. The
  r3 brief stays unedited.

**P13 — NOTE — Record wording.** These are the items listed under Q5 "Inaccuracies":
* 74 vs 75 tests in the amendment §3 and the README;
* "N01-N12" in the harness docstring;
* "revision 2" in the line-1 docstrings;
* the stale `test_launch_gate_modes` citation in §10;
* M25's initial survival not in ledger `process_notes`;
* the V-A quotation verified only against the live page (not stored).

Correct these in a new ledger line or the next revision, never by editing recorded lines.

**Counts:** BLOCKING 0 · MAJOR 4 (P1–P4) · MINOR 5 (P5–P8, P12) · NOTE 4 (P9–P11, P13); 13 new findings in total.

**Conditions:**
* **D1.** Revision 3 (sha256 `6978cba7…`) may be referenced as the DEV_ONLY implementation of L-ID, L-BOOT, L-POWER,
  L-EXCL (reader), L-PIN (with P4/Y06 and P11 open), L-DISK and L-FSYNC. It may **not** be cited for L-FREE, L-LIFE,
  L-UPD, L-LAUNCH or L-SLEEP before a revision 4 fixes P1, P2 and P5–P8, the suite kills Y01–Y06, and a fresh delta
  review confirms both.
* **D2.** Amendment r4, or explicit conditions carried into the formal route review, must correct the four §3 rows and
  the D-HOST-LIFETIME row (P3), and must name the attestation-acceptance mechanism (P1).
* **D3.** Correct owner brief OD-2 (P12).
* **D4.** Write a ledger line for the P13 wording, including M25's initial survival.

---

## 6. Reviewer mutants (brief 61)

**Method:**
* Each mutant was applied to a copy of `lx_platform.py` (sha256 `6978cba7…`) in a temporary directory under scratch.
* The **unchanged** repository suite was run against it with `LX_PLATFORM_DIR=<copy>`, `-B` and
  `PYTHONDONTWRITEBYTECODE=1`.
* The base copy passes (`OK`).
* **3 of 9 were killed and 6 survived.** For each survivor, the equivalence check (`equiv61.py`,
  `equiv61_out.json`, `equiv61_out_y04_unshare.txt`) shows a changed outcome.
* The script is `reviewer61_mutants.py` and the results are in `reviewer61_mutants_result.json`.

```
### Y01 SURVIVED | any non-empty 'decided' opens D-HOST-LIFETIME     (decided={'D-MEM-FREE'}: OPEN_DECISION -> PASS)
@@ -962 +962 @@
-    lifetime_open = "D-HOST-LIFETIME" not in decided
+    lifetime_open = not decided

### Y02 SURVIVED | exited-in-window loop exempts any child of a campaign pid, whatever its start (exited child of a
###               reused campaign pid: reported -> not reported)
@@ -609 +609 @@
-        if (pid, start) not in t1 and (pid, start) not in own and not (ppid in own_start and start >= own_start[ppid]):
+        if (pid, start) not in t1 and (pid, start) not in own and not (ppid in own_start):

### Y03 SURVIVED | acceptance token matched as a substring anywhere   ("REJECTED -- do NOT read as <token>": refused -> valid)
@@ -918 +918 @@
-    if review is None or f"{ACCEPTANCE_LINE}{want}".encode() not in review.splitlines():
+    if review is None or f"{ACCEPTANCE_LINE}{want}".encode() not in review:

### Y04 SURVIVED | cgroup namespace reading hard-wired to 'initial'   (under unshare --cgroup: False -> True)
@@ -513 +513 @@
-            "root_attested": root_attested, "cgroup_ns_initial": ns_inode("cgroup") == INIT_CGROUP_NS,
+            "root_attested": root_attested, "cgroup_ns_initial": True,

### Y05 SURVIVED | attestation bound to /etc/machine-id only          (image-cloned VM, other DMI uuid: refused -> valid)
@@ -914 +914 @@
-    if not cur.get("hardware_bound") or rec.get("machine") != cur:
+    if not cur.get("hardware_bound") or (rec.get("machine") or {}).get("machine_id_sha256") != cur.get("machine_id_sha256"):

### Y06 SURVIVED | the loader is no longer a required pin member      (maps with libm + libc, no loader: None -> a pin)
@@ -778 +778 @@
-REQUIRED_MAPPED = ("libm.so.6", "libc.so.6", "ld-linux")   # N11: members every Linux pin must contain
+REQUIRED_MAPPED = ("libm.so.6", "libc.so.6")   # N11: members every Linux pin must contain

### Y07 KILLED (test_launch_record_fields_are_verified) | launch record: unit type (.service) not checked
@@ -942 +942 @@
-                and unit.endswith(".service") and isinstance(rec.get("invocation_id"), str) and rec["invocation_id"]
+                and isinstance(rec.get("invocation_id"), str) and rec["invocation_id"]

### Y08 KILLED (test_lifetime_gates_open_while_undecided) | a merely truthy guest_updates_shown_disabled counts
@@ -963 +963 @@
-    if not isinstance(upd, dict) or upd.get("guest_updates_shown_disabled") is not True:
+    if not isinstance(upd, dict) or not upd.get("guest_updates_shown_disabled"):

### Y09 KILLED (test_cgroup_resources_whole_chain) | cgroup_resources reads the leaf only (N3 chain repair undone)
@@ -488 +488 @@
-        for i in range(len(parts), -1, -1):
+        for i in range(len(parts), len(parts) - 1, -1):
```

**M25 against the test file of 66be23c3** (before 8bb1c351): the unmutated and the M25 runs fail on the same two
path-dependent tests only (the copied test file cannot reach the repository). M25 adds no failure, so it **survived**
that suite. This confirms the commit message of 8bb1c351.

**Committed harness, re-run by this reviewer** (no output file): unmutated suite PASS; **65/65 killed**; R01–R10 10/10;
X01–X09 9/9; N01–N14 14/14. Both sha256 values equal `MUTANTS_RUN.json`, and every (id, status) pair is identical.
