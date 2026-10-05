# Worker-tier drill (8d): PASS / FAIL / INTERRUPTED rules (deliverable 7 of 10)

**Classes.** The drill on r2 `501f48cb` gets exactly one classification:
- `PASS`
- `FAIL` (with a subclass)
- `INTERRUPTED`
- `NOT_STARTED`
- `INCIDENT`

**How it is decided.**
- **From content.** The classification comes from evidence content (`tools/validate_worker_drill_8d.py`, plus the
  operator checks E-1–E-5). It is never decided from exit codes alone.
- **The drill's own report is not enough.** The drill's `"pass": true` is necessary, not sufficient.
- **One classification.** Precedence: **INCIDENT > INTERRUPTED > NOT_STARTED > FAIL > PASS**. A single failing
  criterion is enough for FAIL.

## 1. PASS: every one of these, with no exception

| # | criterion (the owner's list, Task 9 step 7) | evidence that decides it |
|---|---|---|
| P-1 | all required drill gates complete | V12 (the runner rc 0, pass, confined, HEAD unchanged); V13 (all 20 gates `Q01`…`Q17`, `Q_U2`, `Q_D5`, `Q-HOST` present and true); V14 (witnesses before and after, incl. the QC11 sandbox); V15 (all 9 controls caught); V16 (host functions: provenance ×2, continuity, preflight PASS on the worker, host-package tests, host controls incl. U01–U03, static controls); V03 (all five verdicts true); V02 (`pass` true, tier `worker`, no error) |
| P-2 | no evidence corruption | V19 (each exported ledger equals the report's rows byte for byte, and its sha256 equals the report's); V20 (every drill ledger row parses); V24 (the P309 ledger is HEAD's rows plus exactly one parseable row); the report parses as JSON |
| P-3 | no duplicate RUN START | V18 (`run_start_rows` = 1); V20 (exactly one `RUN START` row in the drill's rows, naming F′); E-1 (exactly one `p309-r2-drill-*` unit started in the window); E-2 (exactly one launch with `launched: true`) |
| P-4 | no resume and no silent retry | precondition D6 (no earlier worker-tier drill on these bytes without a recorded owner decision); V22 and V23 (exactly one new `evidence/drill/<stamp>/`, with exactly three files); V24 (exactly one new GOVERNANCE row); E-1, E-2. The runner and the drill have no resume path, and none may be added |
| P-5 | all expected records are present | V23 (`DRILL_REPORT.json`, `DRILL_ZERO_TARGET_LEDGER.jsonl`, `DRILL_EXPOSURE_LEDGER.jsonl`); V06–V08 (the embedded launch record: mode `drill`, no blockers, preflight, gate and isolation PASS, no loaded unit); V10–V11 (the unit properties); V09 (the launch record file equals the embedded one); E-3 (the launch, pre-launch, static and validation records kept in `p309_8d_records/`) |
| P-6 | scanner pins remain current | V13's `Q_D5` (the runner's own `p309_scan_pins.py --list` = "all current" inside the drill); E-4 (the post-run static re-run on `<CLONE>`'s HEAD: "P309 SCAN PINS: all current", MANIFEST IDENTICAL, QC15 A1–A10 true) |
| P-7 | all evidence hashes validate | V19; V24 (the GOVERNANCE row names the report's actual sha256); V09; the pre-launch `C08` (runner, host, launcher and drill bytes = the reviewed sha256) |
| P-8 | host identity remains consistent | V13's `Q-HOST` (continuity during the whole runner: boot, machine-id, hostname, instance, interpreter, glibc, no suspend, the final sample); V16 `continuity_pass`; V26 (the launch identity = 8b-final); V28 (the launch identity = the pre-launch check); V27 (the pre-launch check passed) |
| P-9 | no protected namespace mutation | V01 (the P309 clone's HEAD still `501f48cb`); V05 (`p309_unchanged`: HEAD, refs and status identical before and after the drill body; HEAD = `501f48cb`); V22 (the clone gained only this drill's evidence and the ledger row); V25 (the exposure ledger unchanged); V15's `no_production_namespace_ref`; the incident scan (no protected ref locally); E-5 (origin: r2 still `501f48cb`, no protected ref) |
| P-10 | target evaluations added = 0 | V17 (counters 0, no cells, no band hit); V20 (every drill row's counters 0); V24 (the new row's counters 0); the incident scan |
| P-11 | grants added = 0 | the incident scan (no `P309_GRANT`, `GRANT.json`, `P309_RESULT`, `p309-emergency-result` or `p309-run-nonce` file in the namespace); V15 (TEST-only prior ref refused and removed; no production ref); E-5 |
| P-12 | the drill ran the reviewed bytes | V04 (`clone_base` = `501f48cb`); the pre-launch `C01`–`C08`; V29 (wall time within the drill's 12 h limit) |

**Operator checks** (read-only, recorded with the validation):
- **E-1:** `journalctl -u 'p309-r2-drill-*' --no-pager -o short-iso | grep -c 'Started '` over the window equals 1,
  and `systemctl list-units --all 'p309-r2-*' --no-legend` shows at most that unit.
- **E-2:** the launch output and the scratch root show exactly one launch record with `blockers: []`. Any other
  record in the window has blockers, or a failed `systemd-run` (NOT_STARTED).
- **E-3:** the records of `WORKER_TIER_DRILL_8D.md` §2–§3 and §10 exist.
- **E-4:** §10 step 2 passed by content.
- **E-5:** `git ls-remote origin` shows r2 at `501f48cb` and no ref matching `refs/(p5y-k5-cell30|p309-cell309|rlr-tail/|p309-test/)`.

## 2. The validator's checks (`tools/validate_worker_drill_8d.py`, schema `P309_R2_8D_VALIDATION/1`)

| check | meaning |
|---|---|
| V01 | the P309 clone's HEAD is `501f48cb` |
| V02 | report schema `P309_R2_DRILL/1`, tier `worker`, `pass` true, no `error` |
| V03 | the verdicts are exactly controls, host, items, ledger and witness, all true |
| V04 | `clone_base` = `501f48cb` |
| V05 | `p309_unchanged`; before = after; before.head = `501f48cb` |
| V06 | the embedded launch record: `P309_R2_LAUNCH/2`, mode `drill`, `blockers: []`, `p309_units_loaded: []`, unit `p309-r2-drill-<utc>` not later than the drill stamp |
| V07 | the launch record is redacted (foreign roots and patterns as sha256); `foreign_roots` and `foreign_uids` non-empty |
| V08 | the launch's preflight, gate and isolation passed |
| V09 | (with `--launch-record`) the record file equals the embedded record |
| V10 | the six checked unit properties have the launcher's values |
| V11 | unit Id, User, `SendSIGKILL=yes`, `TimeoutStopUSec=10s`, `InaccessiblePaths` hashed and non-empty |
| V12 | the runner: only `main`; rc 0; pass; confined; HEAD unchanged |
| V13 | all 20 gates present and true, including `Q-HOST` |
| V14 | the witnesses before and after, incl. the QC11 sandbox keys |
| V15 | all 9 controls caught |
| V16 | the host functions (see P-1) |
| V17 | ledger counters 0, `cells_touched` 0, `band_hits` empty |
| V18 | `run_start_rows` = 1, `missing_scripts` empty |
| V19 | each exported ledger = the report's rows; the sha256 values match |
| V20 | the drill rows parse, have zero counters, and hold one RUN START naming F′ |
| V21 | the drill rows are in UTC order |
| V22 | the P309 clone's changes = exactly this drill's files + the ledger |
| V23 | exactly the three exported files |
| V24 | ledger = HEAD rows + one GOVERNANCE row `topology drill (worker tier) <stamp>: PASS`, with the report's sha256 and zero counters |
| V25 | the exposure ledger unchanged |
| V26 | (with `--verdict`) the launch identity (machine-id, hostname, instance id hashes) = 8b-final |
| V27 | (with `--prelaunch`) the pre-launch check passed |
| V28 | (with `--prelaunch`) the launch identity = the pre-launch identity |
| V29 | drill wall time > 0 and ≤ 12 h (+ 1 h of drill overhead) |

`WORKER_TIER_DRILL_8D.md` §10 always passes `--launch-record`, `--verdict` and `--prelaunch`, so all 29 V-checks
apply (30 entries: V19 has two parts). The tool was exercised in this packet's own test on synthetic fixtures built
from the committed cloud-tier report `20261002T052554Z`:
- a complete worker-shaped fixture gives PASS (30/30);
- a failed gate, a changed file, a nonzero counter and a missing report give FAIL, FAIL, INCIDENT and INTERRUPTED.

See `tools/selftest/`.

## 3. FAIL (a `DRILL_REPORT.json` exists, and any P-criterion fails)

Subclass by the first failing area, in this order:

| subclass | when |
|---|---|
| FAIL-PROBE | `items.main.rc` = 2, with the runner's journal line `QUALIFICATION REFUSED: filesystem probe (S1): …` (or `pre-launch state (H3)`, or `Q-HOST:`). No attempt directory was made |
| FAIL-QHOST | `items.main.rc` = 3, or `QHOST_FAIL.json`, or the drill error "Q-HOST aborted the runner", or `gates["Q-HOST"]` false |
| FAIL-TIMEOUT | the report's `error` starts with `TimeoutExpired` |
| FAIL-GATE | any other gate `Q01`…`Q_D5` false |
| FAIL-HOST-FUNCTIONS | V16 false |
| FAIL-CONTROLS | V15 false |
| FAIL-WITNESS | V14 false |
| FAIL-LEDGER | V17, V18, V20 or V21 false |
| FAIL-F2 | V05 or V22 false |
| FAIL-EVIDENCE | V19, V23, V24 or V25 false, or the report does not parse |
| FAIL-IDENTITY | V26 or V28 false (and Q-HOST passed) |
| FAIL-OPERATOR | any of E-1–E-5 false |

**What a FAIL means.**
- The attempt is preserved: the report, the ledger row and the journal.
- It is reported at return point R-2.
- A further drill needs a **recorded owner decision**. Nothing is retried, resumed or "re-run to confirm".

## 4. INTERRUPTED

The class is INTERRUPTED when the unit started (journal) or a `drill_<stamp>` exists, but there is no
`DRILL_REPORT.json` for that stamp, or no GOVERNANCE row naming it. Typical causes:
- a reboot or power loss (the boot id differs from `ATTEMPT_START.json`'s, if the attempt had begun);
- an OOM kill;
- `systemctl stop` (owner instruction or incident);
- a crash of the drill process itself.

**What then.**
- The drill root is **not** deleted: the deletion step never ran. Preserve it unchanged.
- Classify read-only: the journal, the last records present, and the boot id.
- Report at R-2. No resume, no re-run without an owner decision.

## 5. NOT_STARTED

The class is NOT_STARTED when any of these happened:
- the launcher printed `"launched": false` (a refusal, or blockers);
- `systemd-run` returned nonzero;
- the unit started, but the drill refused before creating `drill_<stamp>`, e.g. the namespace was not clean (A4).

**What then.**
- No attempt exists. Keep the launch record and the output.
- A new launch needs the cause removed (with consent, if a host change is needed) and a new empty scratch root.
- This is not a retry. It is still recorded and reported.

## 6. INCIDENT (it overrides every other class)

The class is INCIDENT when, at any time, any of these exists:
- a nonzero target counter in any ledger row;
- a ref matching `refs/(p5y-k5-cell30|p309-cell309|rlr-tail/|p309-test/)` locally or on origin (outside the drill
  clone's TEST-only control, which the drill creates and deletes inside its disposable clone);
- a grant or result file.

**What then.** If the unit still runs, stop it (`WORKER_TIER_DRILL_8D.md` §7). Report to the owner immediately.
Nothing else is done.

## 7. What a PASS does and does not establish

**It establishes:**
- the formal-review-5 condition C3 and the SF1-A review's C-F1, on `501f48cb`;
- F-DRILL-ORDER exercised end to end;
- `fs_probe` with SF1-A passing on the host's real scratch filesystem, under the real unit user;
- Q-HOST on the real host;
- the first worker-tier timing evidence (QC08–QC10, QC_D5).

**It does not establish:**
- power-loss durability (SAFE_BUT_UNPROVEN);
- the official run's filesystem, if it differs from the scratch root's (R-FS-9);
- the unexercised branches named in `WORKER_TIER_DRILL_8D.md` §11;
- r2's `HOST_SUITABLE`. That also needs the pre-freeze review to accept the drill and the host evidence
  (`R2_HOST_REQUIREMENTS.md` §4);
- anything about freeze, qualification, grant or Γ309.
