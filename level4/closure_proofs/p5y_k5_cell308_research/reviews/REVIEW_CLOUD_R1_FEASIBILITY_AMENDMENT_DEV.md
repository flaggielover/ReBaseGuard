# Review — Cloud route r1: r2 feasibility classification, PROPOSED route amendment A1, dev-only Linux platform layer

* Reviewer: **reviewCLOUD_R1 (fresh agent, brief 59)**
* Date: 2026-10-14 (UTC, review session approx. 19:10–19:45Z)
* Commit reviewed: **b3d8eb5e** (branch `claude/cell-308-github-state-skb1g0`; descends from research tip 88a16f74,
  verified with `git merge-base --is-ancestor`). The branch head moved to 77bc8a93, then 1385935f, during the review.
  Those two commits add only `ledger/briefs/59_reviewCLOUD_R1.txt` and one `BRIEF_INDEX.md` row, so every reviewed path
  is byte-identical to b3d8eb5e.
* Namespace NS = `level4/closure_proofs/p5y_k5_cell308_research/`.
* `new_target_evaluations = 0` · no cell, drift, decoy, science module, candidate code, quarantine guard or
  qualification case was run · nothing installed · no setting changed · no repository file written.

---

## 1. Exposure disclosure

### 1.1 Files opened (paths relative to NS unless stated)

* **Material under review (all at b3d8eb5e):**
  `governance/new_host_route_cloud_r1/` CLOUD_FEASIBILITY_R2.md, OFFICIAL_PROVIDER_FACTS_20261014.md,
  CLOUD_HOST_INVENTORY_R2_20261014.json, ROUTE_PREPARATION.md, OWNER_SELECTION.md, CLOUD_FEASIBILITY.md,
  CLOUD_HOST_INVENTORY.json, OFFICIAL_PROVIDER_FACTS_20261004.md, USER_AUTHORIZATION_20261014.md,
  PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md and OWNER_DECISION_BRIEF_CLOUD_R1.md (all read in full).
  I did not open `CLAUDE_CLOUD_PREPARATION_PROMPT.txt`.
  `streams/CLOUD_R1_LINUX_DEV/`: README_DEV_ONLY.md, lx_platform.py, lx_inventory.py, lx_portmap.py,
  tests/test_lx_platform.py, tests/run_mutants.py and results/TEST_RUN.json (all in full);
  results/MUTANTS_RUN.json (first 50 lines); results/PORT_MAP_142D97A9.json (top-level keys and summary counts only,
  read through python).
* **Accepted sources:**
  * Read in full: governance/SUCCESSOR_GOVERNANCE_308.md, governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md,
    governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1_ERRATUM_E1.md, governance/USER_DECISION_BRIEF_308_MBS_R1_RFREE_STOP.md,
    registry/SUCCESSOR_ROUTE_AUDIT_308.md, registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md,
    registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E1.md and registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E2.md.
  * governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md: headings, lines 300–440, and grep hits for
    resume / EVAL_CAP / 7-day.
  * governance/CONSTANTS_RATIFICATION_MBS308.md: headings and lines 36–84 ("Written rules").
  * reviews/REVIEW_SUCCESSOR_ROUTE_308.md: grep hits, lines 128–170 and lines 195–260.
  * reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md: grep hits, lines 94–240 and lines 270–300.
  * README.md: lines 1–54.
* **Ledger:** only the `git diff 88a16f74 b3d8eb5e` hunk of `ledger/TARGET_INTEGRITY_LEDGER.jsonl`. That is the three new
  lines plus three context lines from 2026-10-04, which carry no target value; the context includes the R-FREE stop
  summary, which is non-target. I also read the last lines of the `88a16f74~1..88a16f74` diff.
* **Brief records seen through `git diff b3d8eb5e 1385935f`:** `ledger/briefs/59_reviewCLOUD_R1.txt` (my own brief) and
  `BRIEF_INDEX.md` rows 56-A to 59, as diff context.
* **Candidate (read with `git show 142d97a9:…` only; never checked out, imported or run):**
  * `code/mbs308_host.py`, in full.
  * `code/mbs308_driver.py`: lines 200–240, plus grep hits at lines 150–152, 206–207, 248, 392–393, 533–544, 584,
    722–741, 788, 972, 1080, 1210 and 1872–1875.
  * One-line grep hits from mbs308_derive, measure, qualify, repin, rrules, state, launch and manifest.
  * The candidate file list (`git ls-tree`).
* **External:** three provider pages, fetched live with `maxAge 0` at review time through Firecrawl:
  code.claude.com/docs/en/cloud-environments, /claude-code-on-the-web and /self-hosted-environments. Extracts are
  saved under `scratchpad/review59/fetched/`.
* **Host (read-only):**
  * `/proc/sys/kernel/random/boot_id`, `/proc/uptime`, the `model name` line of `/proc/cpuinfo` and `uname -r`.
  * `dpkg-query -W` for libc6 and libpython3.13*.
  * The size of `/etc/machine-id` only; its value was not printed.
  * `/proc/self/ns`, the `/proc` line of `/proc/self/mountinfo`, and `/proc/self/maps` inside a probe.
  * This reviewer runs on the **same VM and boot** as the coordinator's r2 inventory (boot_id 00661362-…), so I am
    not an independent host observation.

### 1.2 Commands run

* **Git:** `git status`, `git log`, `git show`, `git diff`, `git ls-tree`, `git branch -a`, `git rev-parse` and
  `git merge-base`.
* **Hashing and reading:** `sha256sum` and `git show | sha256sum` for every ledger-bound file at f4875373, 19b4e8b8 and
  b3d8eb5e, plus `cat`, `sed`, `grep` and `python3 -I`, used only to read files.
* **From `streams/CLOUD_R1_LINUX_DEV`:**
  * `python3 -m unittest discover -s tests -v`: 44 tests, OK.
  * The same under `python3.11 -B` and `python3.12 -B`: 44 tests, OK.
  * `PYTHONDONTWRITEBYTECODE=1 python3 tests/run_mutants.py` with no output argument: 20/20 killed. `results/` was not
    written.
* **Scratch (`/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review59/`):**
  * `base/lx_platform.py` is a copy (sha256 b2c64063…, equal to the committed file).
  * `probes.py`: synthetic sysfs and cgroup trees, plus pin coverage.
  * `probe_zombie_leader.py`: a synthetic child process whose main thread calls `pthread_exit` while a second thread
    spins.
  * `reviewer_mutants.py`: 10 mutants applied to copies in scratch temp dirs. The repository's unchanged test suite is
    run against them via `LX_PLATFORM_DIR`, with `-B`.
  * Results are in `reviewer_mutants_result.json`.
* **Side effect, disclosed:** the first plain `unittest` run may have created or refreshed the git-ignored
  `streams/CLOUD_R1_LINUX_DEV/__pycache__/` and `tests/__pycache__/`. `git status --porcelain` is clean, and they were
  not deleted because they may predate this review. Every later run used `-B` / `PYTHONDONTWRITEBYTECODE`.

### 1.3 Excluded material

I did not open, grep or list any of these:
* `audit/EXECUTION_INTERRUPTION_ASSESSMENT*` or `audit/INCIDENT_AUDIT*`;
* `reviews/REVIEW_EXECUTION_INTERRUPTION*`;
* anything under `p5y_k5_cell308_mb_r1/postexec/`, or any MB r1 target-run record;
* `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`, not even its headings;
* any Cell-309 branch, file or record.

Cell-309 branch names appeared in `git branch -a`, which is permitted. The accepted texts I read name E1″ and the
"runtime-only observations" but give no values. I hold no MB r1 target-run runtime observation. No accidental contact
with excluded material occurred.

---

## 2. Verdicts

CLASSIFICATION: HOST_UNSUITABLE_CONFIRMED
AMENDMENT_DRAFT: NEEDS_REVISION
DEV_CODE: NOT_FAIL_CLOSED

**My verdict on the amendment draft is NOT acceptance of the amendment.** Only these can accept, reject or put it into
force: a formal independent route / governance review, a fresh S12 incident-independence re-rating, and the owner's
decisions (OD-1 to OD-3 and the [OPEN] items). This review is a review of a draft. The classification is confirmed only
together with the corrections in F16 and F17. Those corrections do not change it.

---

## 3. Answers

### Q1 — Classification

**Confirmed, on a sharper basis than the one given.**

**Provider quotations, checked live at review time:**
* P1, P2, P3 and P6 appear verbatim on /claude-code-on-the-web ("Environment expired" section, line 354 of my
  extract, and line 11) and on /cloud-environments (line 342).
* P4 is verbatim at /cloud-environments line 339, with an ellipsis.
* P5 is verbatim at line 344.
* P7, P8 and P9 are verbatim on /self-hosted-environments.

**Two discrepancies:**
* The live P4 paragraph continues: *"Setting `BASH_DEFAULT_TIMEOUT_MS` above `1800000` milliseconds lengthens that limit
  as well as the foreground default."*
  * OFFICIAL_PROVIDER_FACTS_20261014 "settled" item 3 says the documentation "does not say that the background time
    limit … can be" raised. That is false against the page as fetched now.
  * I cannot verify whether the page changed after 18:55Z (UNVERIFIED).
  * CLOUD_FEASIBILITY_R2 E1/U2 ("limited to ≤ 10 min foreground plus ≤ 30 min background") also contradicts the r1
    inventory's own record: "Bash tool background runs are capped at 7200000 ms (2 h)" (CLOUD_HOST_INVENTORY.json,
    `boot_and_lifetime.background_task_limit_of_agent_tool`).
  * U2's conclusion stands: no documented basis exists for an 8-h unattended run (F17).
* The same page says a *paused* VM is restored as **the same VM** on the next message ("Your next message restores the
  same VM", /cloud-environments line 67). Only a *reclaim* yields a fresh VM. U1 is worded correctly ("may then be
  reclaimed"), but the owner brief item 1 merges pause and reclaim.

**The r1-vs-r2 table (CLOUD_FEASIBILITY_R2:37–48):** every row matches the two JSONs. However:
* The JSON's automated `comparison_with_r1_20261004` booleans for cpu model, kernel, OS and interpreters are
  format-confounded. The r1 strings carry suffixes and full `uname` text, and r1 lists `/usr/bin/python3` while r2's
  glob excludes it. These rows would read `same: false` even for identical hosts (`lx_inventory.py:103–116`). The
  differences are real when read by hand.
* E2's sentence "Every platform-pin-relevant property except architecture and vCPU count differs" (line 50) is not
  shown by the recorded evidence:
  * glibc is recorded as `glibc 2.39` on r2 and `2.39-0ubuntu8.7` on r1.
  * `/usr/bin/python3.12` is 3.12.3 on both, although the digests differ.
  * At package level libc does differ: this VM has `libc6 2.39-0ubuntu8.9` (`dpkg-query`), r1 had `8.7`. That supports
    the conclusion, but r2 never recorded it (F16).

**U1–U4:**
* **U1 holds.** The accepted chain requires one platform from the qualification (pins "taken from the qualification
  host at the freeze") to the 7-day deadline:
  * brief R2 §9, lines 407–408;
  * route E1 DR2 ("The no-update rule covers the whole post-marker window … must be disabled for that window. This is an
    operator action by the user").

  Owner decisions and reviews sit between the steps. The provider documents idle pause, then possible reclaim, then a
  fresh VM. The decisive point, which **the coordinator did not state**, is that DR2's no-update requirement is an
  *operator action by the user*. On a provider-managed image the owner has no means to perform it: the image changed
  between sessions (OS point release, Python 3.13.14→3.13.16, 3.10 removed, kernel build, libc6 8.7→8.9), and
  `provider_image_updates` is UNKNOWN by construction (`lx_platform.py:457`). That is a contradiction with an accepted
  requirement, not a missing fact.
* **U2 holds as an auxiliary** (see the correction above).
* **U3 holds:**
  * brief R2 §7 item 8 (lines 355–357): "A platform change gives close-indeterminate";
  * route E1 DR2: "never a mixed-platform resume".

  The citation "brief R2 §8 item 8" (CLOUD_FEASIBILITY_R2:59, :81; amendment H7) is wrong: §8 is the sequencing
  question, and the text is §7 item 8 (F16).
* **U4 is correct for r2.** For r1, the inventory records no suspend_stats or journal reading, so "both hosts" is
  partly unsupported (F16).

HOST_UNVERIFIED would understate the record. The r1 report (CLOUD_FEASIBILITY:162) refused UNSUITABLE because "no
observed fact, on its own, contradicts an accepted rule". The r2 provider text plus DR2's user-action requirement now
supply that contradiction.

### Q2 — No silent relaxation

**Quotations, compared word for word with whitespace normalised (script output in §1.2):**
* Verbatim: S5, S7 and S10 (bold label moved outside); the HOST row; the RC2 bullet; the route-review sentence; the
  incident-review "changed branch" passage; ROUTE_PREPARATION's R-ALLOW / R-FREE sentence.
* **S13 is not carried without loss (F3).** The "[…]" omits the whole sentence "The builder was instructed so on
  2026-09-29 ~20:40Z, **and must disclose any prior reading**". That sentence carries a disclosure obligation, not only
  the time that erratum E1 D2 corrects. E1 D3's holder-list extension ("Neither may take a successor route,
  implementation or caps role (S13)") is not carried either. Ledger line 3 nevertheless asserts "S5/S7/S10/S13 carried
  verbatim".
* **Mislabelled as [ACCEPTED] (F18):** ROUTE_PREPARATION (amendment §4 and the "why" column of H1). Its own status is
  "PREPARATION_ONLY — HOST_UNVERIFIED — ROUTE_REVIEW_PENDING", and "the plan does not amend that source". It is a
  preparation instruction, not an independently accepted text. Its content is restrictive, so no relaxation follows.
* **Quoted out of context (F4):** the S12 quotation (amendment §6). It refers to the *member-trade* changed branch
  (INCIDENT_INDEPENDENCE_REVIEW_MBS308 Q3, L3). The text that governs a platform change is line 129 ("If any of N1–N4
  fails, the successor is on S4's changed branch. Its value is then a second, different draw, the decisive argument is
  lost") and trigger T1. The amendment's conclusion (treat as HIGH) is conservative, but it omits the "second, different
  draw" consequence.

**Threshold relaxations:**
* No number of R-MEM, R-FREE, R-EXCL-PCT or R-ALLOW and no cap is changed in the text.
* **L-PIN is materially weaker than RC2's "OS build" (F1).** On macOS, any OS update changes the build (25F84), and
  libm ships with the OS. The proposed Linux keys are os-release VERSION, the kernel release and the
  `CS_GNU_LIBC_VERSION` string. None of these changes when the `libc6` package, which contains `libm.so.6`, is
  updated: r1 had 8.7, this VM has 8.9, and both report `glibc 2.39` and VERSION "24.04.x". RC2's determinism rests on
  libm (A0 certifier N2, quoted in amendment §5).
* **The libpython pin pins a file that the Ubuntu interpreter does not load.** Probe P10: `Py_ENABLE_SHARED = 1`, but
  `/usr/lib/x86_64-linux-gnu/libpython3.13.so.1.0` is not mapped. The mapped set is `ld-linux`, `libc.so.6`,
  `libm.so.6` and others, and none of them is pinned. `math` is built into the executable.
* This is a silent relaxation of RC2's coverage, presented as a mechanical replacement.

**Unknown or absent treated as passing in code:** yes, in several places (Q5, F8–F11).

**PROPOSED vs ACCEPTED otherwise:**
* The amendment is labelled PROPOSED throughout, and the dev code is labelled DEV_ONLY.
* `README_DEV_ONLY.md:14` claims "every failed reading returns UNKNOWN; neither ever passes". That claim is false
  (Q5).
* L-ID-1 is presented as "PROPOSED (mechanical)" in §3. It changes the accepted outcome: under macOS O-4, a zombie
  reads `(name)` and is classified UNKNOWN (`mbs308_host.py:357–360, 384–385`). It therefore belongs in §4 (F2).

### Q3 — Completeness of the open decisions

Missing macOS-dependent rule elements, using the port map and `git show` of the candidate (F6):

1. **S15 preflight is host-local.**
   * `mbs308_driver.py:206–207, 392–393` checks for MB r1's emergency file in `MBR1_GIT_DIR =
     "/Users/suzhe/ReBaseGuard/.git/worktrees/ReBaseGuard-c308mb"` with `os.path.lexists`.
   * On any other host that path does not exist, so the S15 assertion "no emergency file" passes *vacuously*.
   * S15 is accepted (A1 §4), and nothing in A1 says how it is asserted from a new host.
   * The qualified-worktree constants (`QUALIFIED_WORKTREE` / `QUALIFIED_GIT_DIR` / `QUALIFIED_COMMON_DIR`, lines
     150–152) are equally host-bound.
2. **R-ALLOW's base set.** The rule is "the current 39 names ∪ …" (CONSTANTS_RATIFICATION:72), and those names are
   macOS daemons (`mbs308_driver.py:538–544`: `launchd`, `logd`, `mds`, `cloudd`, …).
   * On Linux they are meaningless, and a process could adopt such a basename.
   * D-ALLOW-PATHS covers only clause (b).
   * Keeping the 39 names is a semantic hazard, and dropping them is a rule change. Neither is listed.
3. **Caps on a different CPU (MBS-8 / §14 G2).**
   * Per-job CPU caps (RLR 1800 / 4200 / 8700 s) and EVAL_CAP come from macOS arm64 decoy runtimes.
   * The thin Q12 margins ("about 6 % and 9 %", route A1 §5 item 3) were measured there.
   * The Linux candidate is x86-64 at 2.1 GHz (r2) or 2.8 GHz (r1).
   * RLIMIT_CPU enforcement (`mbs308_driver.py:722–741`) has OS-specific signal semantics.
   * The amendment keeps the caps "unchanged" (§1) but does not put the MBS-8 choice under a changed CPU to the owner.
   * D-WORKERS-CORES covers core count only.
4. **The interpreter.** The candidate pins CPython 3.14.5, which is absent on both Cloud hosts. Which Linux build is
   used (version, source, compiler, flags) must be fixed before L-DET, or a post-failure choice becomes possible (Q4).
5. **Accepted texts that name launchd.** R-MEM step 1 ("under the launchd launcher") and brief R2 §9 ("`execute` and
   `resume` run only under the launchd launcher") need textual amendment. L-LAUNCH calls this "mechanical".
6. **Lid / clamshell reading.** `mbs308_qualify.py:338–341` (`ioreg AppleClamshellState`) is part of the
   host-readiness checklist and has no row.
7. **Update vectors beyond apt.** The Linux counterpart of the brief R2 §9 "Automatic restart" row is missing:
   unattended-upgrades `Automatic-Reboot`. So are snapd auto-refresh, cloud-init `package_upgrade` and kernel livepatch.
   Livepatch changes kernel code without changing the release string that L-PIN uses.

**Options that are rule changes but not labelled as such (F7):**
* D-MEM-FREE (a)–(d): each substitutes R-FREE's measured quantity.
* D-MEM-WIRED, both options.
* D-MEM-PRESSURE "over N readings": a new, unset number.
* D-THERMAL "no zone at or above a passive trip point": a new rule.
* D-ALLOW-PATHS options 2–3. "Package-manager-owned" paths are root-writable, so they are not SIP-equivalent, which
  breaks R-ALLOW's stated rationale.
* D-EXCL-WINDOW "hosting app = none": removes R-EXCL-PCT's one exception.

The table header "no recommendation is a rule decision" is not a per-option label.

### Q4 — RC2 / L-DET

L-DET is not yet a faithful implementation of RC2 and the HOST row (F5):

* **Case set not enumerated.**
  * RC2 (route review lines 237–241; route A1 §3, "MBR1_REPRO") names QC02 (decoy 297), QC03 (decoy 316, blocks 0–2)
    and the **QC04 validation-drift ladder pair**.
  * L-DET item 1 says "MB r1's committed non-target r3 **decoy** records", which on a natural reading excludes the
    QC04 drift pair.
  * Neither the record paths nor their sha256 / commit are fixed.
* **The code path is unspecified.** RC2 requires re-running the cases "through the successor's code". The Linux
  successor does not exist yet. L-DET is placed before any designated series, but must not run through an ad-hoc
  harness, which would be new, unreviewed code on the evaluation path (incident review N2).
* **Comparison semantics.** RC2 says "exact equality of every certified leaf, timing stripped". L-DET says "byte-equal
  after the QC04 timing strip". The strip function and the serializer must be pinned by sha256, and both comparisons
  (leaf values and bytes) should be required.
* **Stop rules are incomplete.**
  * No rule covers a run that does not complete (crash, cap hit, host interruption): may it be repeated, and must all
    attempts be recorded and disclosed?
  * "No re-run selection" covers only reruns on the same platform.
  * **Host shopping is open.** After a mismatch on host A, OD-1 can select host B with a different libm. That is
    exactly the "changing … libm or interpreter" that item 4 forbids, done by changing machines.
  * Required: every L-DET attempt on every host is recorded; a mismatch on any host is disclosed in every later brief;
    a further host needs a new owner ruling and a fresh review with the prior failure in view.
* **The interpreter and toolchain must be fixed in the accepted amendment before L-DET runs** (see Q3 item 4).
* **Target adjacency.**
  * Decoys 297 and 316 are outside 305–309, and the drift band is excluded (item 1). That is adequate.
  * Qualification review E8 ("never placed next to a cell-308 quantity") is not restated.
  * The status of L-DET's runtimes for the caps decision is not stated: S13 / MBS-8 allow only official decoy or
    qualification evidence, so they must be excluded or designated in advance.
* **Determinism scope.** Item 5 hedges, but the accepted texts conflict:
  * the HOST row says the route is "EXCLUDED unless RC2 is discharged there";
  * route A1 §1 says the value equals the lost run's "only on the same platform";
  * the incident review (line 129 and T1) says that if N3 fails, "a second, different draw".

  Brief R2 §9 (last paragraph) already records "Which of the two governs is not settled". The amendment does not raise
  this as an [OPEN] decision. OD-3's framing ("single most decisive target-free test of the whole route") implies that
  an exact match restores the decisive argument, which the incident review denies (F4).

### Q5 — Dev code fail-closed properties

* **Suite results:** the unit suite passes on 3.11.17, 3.12.3 and 3.13.16. The 20 existing mutants are all killed.
  **All 10 of my mutants survive** (§5).
* **Paths where a failed or absent reading yields a pass state.** Probes are in `probes.py` and
  `probe_zombie_leader.py`. They ran against a scratch copy of lx_platform.py with sha256 b2c64063… (identical to the
  committed file).
  * **AC from a failed read.**
    * A Mains supply online plus a Battery whose `type` read fails (here, a directory) returns `"AC"` while the
      battery is `Discharging`, because unreadable types are skipped (`lx_platform.py:266–279`).
    * A discharging `UPS` supply is ignored and also returns `"AC"`.
    * This propagates into `assess` and can make it **CLEAN** (`:234–238`).
  * **PASS from an absent reading.** `preflight(... readings={"updates": {}})` gives `no_automatic_os_install = PASS`.
    So does `provider_image_updates` set to `None`, `"unknown"` or `"NOT_ATTESTED"`: anything but the literal
    `"UNKNOWN"` passes (`:647–648`). The committed test itself passes with `"ATTESTED_FROZEN"`
    (`test_lx_platform.py:440`).
  * **PASS from a rejected attestation.** `host_attestation={"reviewed": True, "accepted": "REJECTED"}` gives
    `host_lifetime_attested = PASS`, as do `{"reviewed": "no", "accepted": "false"}` and `{1, 1}`. The check is
    truthiness, and the attestation is not bound to any file, sha256 or machine (`:650–651`).
  * **Numeric memory allowance from a failed read.** `cgroup_min_headroom` skips every level whose limit or usage is
    unreadable:
    * the binding level has an unreadable usage: the result is headroom `100000000`, computed from the other levels;
    * an ancestor limit is unreadable: `effective_limit` is None but headroom is `2999999600` (`:383–387`).

    This is exactly D-MEM-FREE option (c).
  * **cgroup v2.** The root never has `memory.max` or `memory.current`, so on a standard systemd host with unified
    cgroup v2 the chain always ends in `limit=None`. `effective_limit` and headroom are then **always UNKNOWN** (P4c).
    That is fail-closed, but it makes H6 unattainable on exactly the host class H2 requires, and `test_v2` pins the
    behaviour. Other gaps:
    * `memory.high` is ignored, so an allowance throttled at `memory.high` is overstated;
    * ancestors hidden by a cgroup namespace are invisible, and nothing detects them;
    * ROUTE_PREPARATION's Phase-1 list (`memory.high`, `cpu.max`, `cpuset.cpus.effective`, `pids.max`) is not read.
  * **DEAD for a live process (L-ID-1).** A child whose main thread calls `pthread_exit` while a second thread computes
    shows `State: Z (zombie)`, `Threads: 2`, `/proc/<pid>/task = [leader, worker]`, and CPU ticks rising
    63→114→164→214. `identity_state` returns **DEAD** on all four readings. Under the accepted semantics a recorded
    process that is not positively dead "keeps the run CONSUMED_COMPUTING" (brief R2 §7 item 8), and macOS would read
    UNKNOWN. A false DEAD lets `recover` / `resume` start a second computation beside a live one.
  * **Exclusivity readings that look clean:**
    * a CPU hog born inside the window is not reported;
    * PID reuse gives a negative delta and is not reported;
    * `own_pids ∋ 1` exempts every daemon (`:439–447`);
    * `/proc` under a PID namespace or `hidepid` shows a partial process set.

    The gate is OPEN_DECISION today, so these are latent.
  * **Namespaces.** `os.kill` ESRCH and `/proc/<pid>/stat` starttime are PID- and time-namespace-relative. A reader in
    a different namespace from the recorder gets false DEAD from ESRCH or a starttime mismatch.
  * **The launch gate disappears instead of failing.** `preflight(launched=None)` removes the `launched_by_systemd`
    gate. This mirrors the candidate (`mbs308_host.py:585–601`), but the Linux docstring does not limit it to the
    launcher's own preflight.
  * **Auto-update parsing (`:452–473`).**
    * A commented `// APT::Periodic::Enable "0";` counts as positive evidence that updates are disabled (P5a).
    * So does a `*.dpkg-old` file, which apt ignores (P5b).
    * Nested `APT { Periodic { … } }` syntax and `/etc/apt/apt.conf` are not read (P5c).
    * `Unattended-Upgrade "0"` is accepted even with the binary present, contrary to the docstring (P5d).
    * In the other direction, the r2 inventory reports `guest_auto_install_enabled: true` on a host with
      `APT::Periodic::Enable "0"` and no systemd PID 1, which is factually wrong but conservative.
* **Channel P** is acceptable as an additional, strictly stricter channel. It can only remove CLEAN, never create it
  (`:216–217`). It is not a pause detector: a hypervisor pause invisible to both guest clocks leaves K′ and P silent,
  and K′ only sees guest-initiated suspend. On a VM, D-PAUSE cannot be closed by K′/S′/L′/P alone. Note also that
  L′ (journal) has no reader in the module. A future reader that returns `[]` on failure would make `assess` CLEAN.
* **What holds:** `boot_id`, `proc_stat`, `cmdline_sha256`, the unrecorded-field rules, `durable_write` atomicity under
  SIGKILL, `pin_mismatches` (None never matches), and the hard OPEN_DECISION gates.
* **Why the verdict is NOT_FAIL_CLOSED rather than "with defects":** the readers violate the module's own invariant in
  at least four directions (AC, PASS, numeric allowance, DEAD-while-alive). The live `preflight` cannot pass only
  because five gates are hard-wired OPEN_DECISION, and that protection disappears as soon as any D-* decision is
  taken.

### Q6 — Preservation

* **S5, S7 and S10 are carried verbatim. S13 is not** (F3).
* MB-S r1 immutability is carried (amendment §1, lines 34–37): designated evidence `86d3f8cb…`, derivation `8a4e7984…`,
  NOT_DERIVED / GATE_UNATTAINABLE, three INVALID series and ALREADY_DESIGNATED. The amendment should also say expressly
  that a new-host designated series is not a "replacement series" in the sense of the R-FREE stop brief §4 item 2. This
  is covered implicitly by S4's changed branch.
* **Exactly-once:** §7 states the count would become 2 under a new S1 ruling per A1 §3 / E1 D1. MBS-5(b) is not
  restated: any evaluation after an MB-S marker, of any route, is rated not lower than HIGH.
* **The false-DEAD path (F2) is an exactly-once hazard** in the code that the amendment cites as its implementation.
* **Candidate untouched:**
  * `git diff 88a16f74 b3d8eb5e --stat`: 16 files, all under the research namespace;
  * `--diff-filter=MDR` shows only the ledger file modified (appended);
  * zero paths under `p5y_k5_cell308_mbs_r1/`;
  * the local remote-tracking refs are `origin/p5y-k5-cell308-mbs-r1-candidate = 142d97a9…` and
    `origin/p5y-k5-cell308-mbs-r1-research = 88a16f74…`.

  The live remote state was not queried (UNVERIFIED; `git ls-remote` was outside the permitted command list).

### Q7 — Ledger

* There are **three** new lines between 88a16f74 and b3d8eb5e, not four.
* Every sha256 they bind recomputes exactly:

  | file | sha256 |
  |---|---|
  | provider facts | `4da1d938…` |
  | r2 inventory | `a0fb5504…` |
  | CLOUD_FEASIBILITY_R2 | `02a030ad…` |
  | port map | `b6464533…` |
  | lx_platform.py | `b2c64063…` |
  | test_lx_platform.py | `059e017c…` |
  | amendment | `386f49f3…` |
  | owner brief | `c7960a9a…` |

  These values hold at the commit that introduced each line and are unchanged at b3d8eb5e.
* `USER_AUTHORIZATION_20261014.md` (`a202596d…`), the owner's verbatim instruction, is bound by no ledger line.
* The inventory was produced with lx_platform `65a18b59…` (at f4875373). The tool was then changed in 19b4e8b8:
  `boot_id_recorded`, FAIL→UNKNOWN when absent. This is traceable in git, but not noted in the inventory or the ledger.
* Ledger line 3 claims "S5/S7/S10/S13 carried verbatim", which is false for S13.
* TEST_RUN.json reports `tests_ok 43 / tests_total 43` next to "Ran 44 tests".
* Brief 59's BRIEF_INDEX row says "see ledger", but no ledger line records the brief's issuance. That commit is
  outside b3d8eb5e.

---

## 4. Findings

Findings marked **[PRE-REVIEW]** must be fixed before the draft goes to a formal route / governance review.

**F1 — BLOCKING [PRE-REVIEW] — L-PIN does not cover libm. The libpython pin pins an unloaded file.**
* **Location:** amendment §3 row L-PIN; `lx_platform.py:579–610`.
* **Evidence:**
  * libc6 is 8.7 on r1 and 8.9 on r2, both reporting `glibc 2.39`.
  * `/proc/self/maps` of python3.13 maps `libm.so.6`, `libc.so.6` and `ld-linux`, none pinned.
  * The pinned `libpython3.13.so.1.0` is not mapped.
  * Reviewer mutant R06, which drops `libpython_sha256` and `glibc` from `PIN_KEYS`, survives.
* **Correction:**
  * Pin the sha256 of every shared object the interpreter maps, at least `libm.so.6`, `libc.so.6` and the dynamic
    loader, and of every `lib-dynload` module the science imports.
  * Pin the dpkg versions of `libc6` and the python packages.
  * Record whether the interpreter is statically linked, and drop or justify the libpython pin.
  * Record the kernel livepatch state.
  * State in the L-PIN row why the set is equivalent to macOS "OS build" coverage for RC2, and add tests.

**F2 — BLOCKING [PRE-REVIEW] — L-ID-1 (zombie ⇒ DEAD) is unsound and a semantic change.**
* **Location:** amendment §3 row L-ID; `lx_platform.py:155–156`; `test_lx_platform.py:76`.
* **Evidence:** probe P6, a zombie thread-group leader with a live computing thread, reads DEAD. Accepted macOS O-4
  semantics read a zombie as UNKNOWN. Brief R2 §7 item 8 requires that a process not positively dead keeps the run
  CONSUMED_COMPUTING. Reviewer mutant R07, which widens the set to T/t/D, survives.
* **Correction:**
  * Remove L-ID-1, or require Z/X **and** `/proc/<pid>/task` containing only the leader (else UNKNOWN).
  * Add the probe as a test.
  * Move L-ID-1 to §4 as an [OPEN] decision that changes an accepted outcome.

**F3 — MAJOR [PRE-REVIEW] — S13 is carried with loss.**
* **Location:** amendment §7 (S13 block); ledger line 3.
* **Correction:**
  * Quote S13 in full, including "and must disclose any prior reading".
  * Carry the E1 D2 time correction as a bracketed erratum, not an omission, and add E1 D3's holder extension.
  * Correct the ledger claim in a new line; never edit the old one.

**F4 — MAJOR [PRE-REVIEW] — The determinism-scope conflict is not raised. The S12 quotation is out of context.**
* **Location:** amendment §5 item 5, §6 and §4; owner brief OD-3.
* **Correction:**
  * Add an [OPEN] decision D-RC2-SCOPE. It should cite route A1 §1 ("only on the same platform"), the HOST row, brief
    R2 §9 ("Which of the two governs is not settled"), incident review line 129 and trigger T1.
  * State that T1 has fired by construction for any platform change.
  * Replace the member-trade quotation in §6 with line 129 and T1.
  * Reword OD-3 so that it does not imply that an exact decoy match restores the decisive argument.

**F5 — MAJOR [PRE-REVIEW] — L-DET is under-specified and selection-prone.**
* **Location:** amendment §5, items 1–5.
* **Correction:** pre-register all of the following.
  * The exact RC2 case set (QC02 decoy 297; QC03 decoy 316 blocks 0–2; the QC04 validation-drift ladder pair), with
    record paths, commit and sha256.
  * The code that runs it: the reviewed successor build, after step 4. No ad-hoc harness.
  * The interpreter and toolchain build, fixed before any run.
  * Pinned strip and serializer functions, and both leaf-value and byte equality.
  * A rule for non-completing runs: every attempt is recorded and disclosed; no best-of-N.
  * A cross-host rule: one L-DET per owner host decision; every failure disclosed in later briefs; a new host needs a
    new ruling and a fresh review.
  * E8 restated.
  * Whether L-DET runtimes are excluded from, or designated for, the caps evidence (S13 / MBS-8).

**F6 — MAJOR [PRE-REVIEW] — Open decisions are missing (Q3 items 1–7).**
* **Location:** amendment §4.
* **Correction:** add [OPEN] rows for:
  * the S15 assertion on a new host (host-local `MBR1_GIT_DIR` / emergency-file check passes vacuously on Linux) and
    the qualified-worktree path constants;
  * R-ALLOW's base set of 39 macOS names;
  * caps validity on a different CPU (the MBS-8 choice, thin Q12 margins, RLIMIT_CPU semantics);
  * interpreter version and build;
  * the textual amendments to R-MEM step 1 and brief R2 §9 ("launchd launcher");
  * the lid / clamshell check;
  * non-apt update and reboot vectors (unattended `Automatic-Reboot`, snapd, cloud-init, livepatch).

**F7 — MAJOR [PRE-REVIEW] — Options are not labelled as rule changes.**
* **Location:** amendment §4 table.
* **Correction:** add a column "amends which accepted text / introduces which new number". Mark D-MEM-FREE (a)–(d),
  both D-MEM-WIRED options, the D-MEM-PRESSURE "N", the D-THERMAL trip rule, D-ALLOW-PATHS options 2–3 and
  D-EXCL-WINDOW "hosting app = none" as rule changes.

**F8 — MAJOR [PRE-REVIEW] — Gate logic passes absent or rejected records.**
* **Location:** `lx_platform.py:647–651`.
* **Correction:**
  * `no_automatic_os_install` is PASS only if `guest_auto_install_enabled is False` **and** `provider_image_updates`
    equals one accepted token derived from a reviewed attestation. Anything else is UNKNOWN.
  * `host_lifetime_attested` requires `is True` for both fields, plus a committed attestation path, its sha256, the
    machine identity and an acceptance-record reference.
  * Add tests for `{}`, `None`, `"REJECTED"` and `"false"`.

**F9 — MAJOR [PRE-REVIEW] — power_source returns AC on failed or unknown supplies.**
* **Location:** `lx_platform.py:256–284`.
* **Correction:**
  * An unreadable `type` returns None.
  * An unknown type (`UPS`, `USB`, `Wireless`) returns None, or "not AC" if it is discharging.
  * Add tests, and pin `assess`'s per-sample power check (reviewer mutant R10 survives).

**F10 — MAJOR [PRE-REVIEW] — cgroup readings.**
* **Location:** `lx_platform.py:328–393`; `test_v2`.
* **Correction:**
  * Headroom is None if any level's limit or usage is unreadable.
  * Treat the v2 root as "no limit by construction" only after establishing that the visible root is the real root
    (cgroup-namespace check, otherwise UNKNOWN).
  * Include `memory.high`, and read `cpu.max`, `cpuset.cpus.effective` and `pids.max` as ROUTE_PREPARATION requires.
  * Rewrite `test_v2` so that it no longer pins "always UNKNOWN".
  * State in H6 that hidden ancestors are established by attestation, not by the reader.

**F11 — MAJOR [PRE-REVIEW] — The auto-update reader takes comments and ignored files as positive evidence.**
* **Location:** `lx_platform.py:452–473`; amendment L-UPD.
* **Correction:**
  * Use the read-only `apt-config dump`, or a parser that honours apt's ignore rules, comments, nesting and
    `/etc/apt/apt.conf`.
  * Reconcile the docstring and the code on `Unattended-Upgrade`.
  * Add the other update vectors (F6).
  * Correct the inventory's "guest_auto_install_enabled: true" wording into "not shown disabled".

**F12 — MAJOR [PRE-REVIEW] — The test suite does not pin the fail-closed properties it claims.**
* **Location:** `tests/test_lx_platform.py`; amendment §3 "20/20 mutants killed"; §9 item 1.
* **Evidence:** reviewer mutants R01–R10 all survive, including removal of the data fsync (R03), removal of the
  directory fsync (R08), a 25 s suspend tolerance (R04), a 390 s sample gap (R09) and a hidden allow-list for the
  session controller (R05).
* **Correction:** add tests that kill R01–R10. In particular, check `SLEEP_GAP_TOL_NS` and `MAX_SAMPLE_GAP_S` against
  the candidate's `mbs308_host` values, and assert the fsync calls through a monkeypatched `os.fsync`. Re-run, and
  report the reviewer mutants alongside the self-selected ones.

**F13 — MINOR — Exclusivity reader blind spots.**
* **Location:** `lx_platform.py:409–448`.
* **Correction:**
  * Report processes born in the window from their `starttime`, or return UNKNOWN.
  * Key processes by (pid, starttime).
  * Reject `own_pids` containing 1 or 0.
  * Detect a PID namespace or `hidepid`, and return None.

**F14 — MINOR — Identity is namespace-relative.**
* **Location:** `lx_platform.py:109–165`.
* **Correction:** record the `/proc/self/ns/pid` and `ns/time` inodes in the identity. A mismatch at read time gives
  UNKNOWN.

**F15 — MINOR — `preflight(launched=None)` drops the launch gate.**
* **Location:** `lx_platform.py:653–654`.
* **Correction:** document the mode restriction as the candidate does, and add a test that execute and resume callers
  cannot pass None.

**F16 — MINOR [PRE-REVIEW] — Citation and evidence errors in CLOUD_FEASIBILITY_R2.**
* **Locations and corrections:**
  * "brief R2 §8 item 8" (lines 59 and 81; amendment H7) becomes §7 item 8.
  * E2 line 50 overstates. glibc as recorded and python3.12's version are identical; record the libc6 package version
    instead.
  * U4's "both hosts" for suspend_stats and the journal is not supported by the r1 inventory.
  * Add the DR2 user-action contradiction (Q1) as the primary basis for U1.
  * Distinguish a pause (same VM restored) from a reclaim, in U1 and in owner brief item 1.

**F17 — MINOR [PRE-REVIEW] — The provider-facts interpretation is contradicted by the live page.**
* **Location:** OFFICIAL_PROVIDER_FACTS_20261014, "settled" item 3; CLOUD_FEASIBILITY_R2 E1 / U2.
* **Correction:**
  * Record the omitted P4 sentence about `BASH_DEFAULT_TIMEOUT_MS > 1800000`.
  * Withdraw "does not say that the background time limit … can be" raised.
  * Reconcile it with r1's recorded 2-h tool cap.
  * State U2 as "no documented basis for an 8-h unattended computation", not as "limited to 10 + 30 min".

**F18 — MINOR [PRE-REVIEW] — The [ACCEPTED] label is applied to ROUTE_PREPARATION.**
* **Location:** amendment §4 and H1.
* **Correction:** relabel it as a preparation instruction (not independently accepted), or cite an accepted source for
  the same content.

**F19 — MINOR — The r2 inventory comparison is format-confounded and the inventory is incomplete.**
* **Location:** `lx_inventory.py:103–116`; CLOUD_HOST_INVENTORY_R2.
* **Correction:**
  * Normalise the fields before comparing (model string, kernel release, PRETTY_NAME, the same interpreter glob).
  * Add the libc6 package version, `cpu.max`, `cpuset`, `pids.max`, `memory.high` and mount characteristics.

**F20 — MINOR — Host identity and V-A.**
* **Location:** amendment H8; owner brief V-A.
* **Correction:**
  * `/etc/machine-id` is not a hardware identity on image-cloned VMs. Add DMI `product_uuid` or an owner attestation.
  * The live self-hosted page states that a session can be requeued to another runner after a signal-less host kill.
    The owner brief should say that V-A gives no host-identity guarantee beyond the owner's own machine.

**F21 — NOTE — Ledger and records.**
* There are three new lines, not four. All hashes match.
* The owner instruction file is unbound by the ledger.
* TEST_RUN.json's counts are inconsistent (43 vs 44).
* The inventory's tool version differs from the committed lx_platform.py; the change is traceable to f4875373.
* No ledger line records brief 59.

**F22 — NOTE — Tautological controls, contrary to NS README rule 6.**
* **Location:** `test_lx_platform.py:90–91` (assertNotEqual against `"never"`) and `:135–141` (a wrapper "mutant" that
  cannot fail the suite).
* **Correction:** replace them with controls that run through the code under test.

**F23 — NOTE — `durable_write`'s fixed `.tmp` name blocks every later write after a crash.**
* **Location:** `lx_platform.py:532–533`.
* **Detail:** a stale tmp makes every later write fail with FileExistsError.
* **Correction:** the recovery semantics of the future state machine must name this state and its operator action
  (record, never delete), as for MB-S's lockfiles.

**Counts:** BLOCKING 2 · MAJOR 10 · MINOR 8 · NOTE 3 (23 findings). The 15 findings marked [PRE-REVIEW] are F1–F12 and
F16–F18.

---

## 5. Reviewer mutants

Each mutant was applied to a copy of `lx_platform.py` (sha256 b2c64063…) in a scratch temp dir and run against the
**unchanged** repository suite (`LX_PLATFORM_DIR=<copy>`, `-B`). The unmutated suite passes. **0 of 10 were killed.**

```
### R01 SURVIVED | unreadable Battery status skipped (a failed read can yield AC)
@@ -278 +278 @@
-                return None
+                continue

### R02 SURVIVED | host attestation accepted when the 'accepted' key is merely present (e.g. 'REJECTED')
@@ -651 +651 @@
-                                           and host_attestation.get("accepted")) else UNKNOWN,
+                                           and "accepted" in host_attestation) else UNKNOWN,

### R03 SURVIVED | durable_write never fsyncs the data
@@ -541 +541 @@
-        os.fsync(fd)
+        pass

### R04 SURVIVED | suspend / pause tolerance raised from 2 s to 25 s
@@ -41 +41 @@
-SLEEP_GAP_TOL_NS = 2_000_000_000                # same tolerance as mbs308_host channel K
+SLEEP_GAP_TOL_NS = 25_000_000_000               # same tolerance as mbs308_host channel K

### R05 SURVIVED | hidden name allow-list for the Cloud session controller in busy_processes
@@ -440 +440 @@
-        if pid in own_pids or ppid in own_pids:
+        if pid in own_pids or ppid in own_pids or comm in ("claude", "environment-man", "process_api"):

### R06 SURVIVED | libpython_sha256 and glibc dropped from PIN_KEYS
@@ -604,2 +604,2 @@
-PIN_KEYS = ("python_executable", "python_sha256", "libpython", "libpython_sha256", "python_sys_version", "os_id",
-            "os_version_id", "os_version", "kernel_release", "machine", "glibc")
+PIN_KEYS = ("python_executable", "python_sha256", "libpython", "python_sys_version", "os_id",
+            "os_version_id", "os_version", "kernel_release", "machine")

### R07 SURVIVED | L-ID-1 widened: stopped (T/t) and uninterruptible (D) tasks read as DEAD
@@ -155 +155 @@
-    if st.get("state") in ("Z", "X"):
+    if st.get("state") in ("Z", "X", "T", "t", "D"):

### R08 SURVIVED | durable_write never fsyncs the directory after the rename
@@ -551 +551 @@
-        os.fsync(dfd)
+        pass

### R09 SURVIVED | maximum sample spacing raised from 180 s to 390 s
@@ -42 +42 @@
-MAX_SAMPLE_GAP_S = 180                          # same as mbs308_host
+MAX_SAMPLE_GAP_S = 390                          # same as mbs308_host

### R10 SURVIVED | assess checks power only at start and end, not at the samples
@@ -234 +234 @@
-    power = [x.get("power") if isinstance(x, dict) else None for x in seq]
+    power = [x.get("power") if isinstance(x, dict) else None for x in (start, end)]
```

The probes that are not mutants (P1–P10, P6) are in `probes.py` and `probe_zombie_leader.py` in the same scratch
directory. Their outputs are quoted in Q5.
