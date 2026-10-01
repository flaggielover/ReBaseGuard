# P309-r2 implementation report (gate steps 3a–5), for the r2 delta review (step 6)

**What this covers.** It reports what the coordinator implemented under:
* `R2_PLAN.md`;
* `REVIEW_R2_PLAN.md` (P1–P23);
* `R2_PLAN_ADDENDUM_1.md`;
* `REVIEW_R2_PLAN_FOLLOWUP_1.md` (F1–F11);
* `R2_PLAN_ADDENDUM_2.md`.

The verifier author's step-3 changes are reported in `verify/R2_VERIFIER_CHANGES_REPORT.md` and committed unchanged at
`030b7025`.

**What it does not do.** It verifies nothing on the reviewer's behalf. Every number below can be recomputed from git.

NEW Γ309 TARGET EVALUATIONS = 0.

## 1. Commits (base `c902fe2f`, r1's final head; branch `claude/p5y-k5-cell309-p309-r2`)

| commit | step | content |
|---|---|---|
| `e07e3ee8` | 3a | Byte-identical copy of r1's code/, config/, fc2/, tests/, verify/, start_state/ and 15 governance files at F. Each subtree id equals F's |
| `2183b8f2` | 3 | The verifier author's brief, committed before issue |
| `030b7025` | 3 | The verifier author's V1–V7, committed unchanged (VERIFIER_R2_CHANGES_DONE) |
| `d0aede4e` | 4 / R2-I1 | The declared relocation map only: 32 lines in 16 files |
| `2f09500f` | 4 / R2-I1 | r1's namespace kept forbidden; the anchor split; r1's reviews inherited; ledger genesis |
| `0f02701e` | 4 / R2-I2, I4 | `P309_SCRATCH_ROOT` everywhere; `code/p309_host.py` |
| `2cd574de` | 4 / R2-I3 | The QC11 repair; QC12 T11–T13; the production read path pinned |
| `6aa31504` | 4 / R2-I4, I6 | Q-HOST in the runner; `code/p309_launch.py`; the host requirements and bootstrap documents |
| `e362c3de` | 4 / R2-I5, I6 | `code/p309_topology_drill.py`; scanner registrations; pin refresh |
| `4abc7073` | 5 | Drill attempt 1 (FAIL before F'), preserved; allowlist entries for code/p309_placeholder_check.py |
| `a39ec7c3` | 5 | Drill attempt 2 (FAIL: three defects, all found and fixed), preserved; `governance/R2_REPIN_LIST.json` |
| `93b41bd9` | 5 | Drill attempt 3 (all verdicts PASS; ledger-row defect found and fixed), preserved; `R2_EQUIVALENCE_P8AD.json` |
| `7ed74347` | 5 | Drill attempt 4 PASS (validated 37/37), preserved; `R2_EQUIVALENCE_P8AD_ATTEMPT4.json`; owner message 4 verbatim (own file) |
| `61731123` | 5 | Repairs: worker-tier preflight configuration, Q-HOST continuity and monitor semantics (`gate_checks`, `monitor_verdict`), `tests/test_p309_host.py` (41 cases) run by the drill; self-audit A3 adds message 4; `R2_AWS_SESSION_INSTRUCTIONS.md`; `OWNER_DECISION_PACKET_R2.md` |
| (this commit) | 5 | Drill attempt 5 PASS, preserved; `R2_EQUIVALENCE_P8_FINAL.json`; the final `R2_REPIN_LIST.json`; this report; the delta-review brief |

**Pushes.** Every push used an explicit single-ref refspec, without force, and was verified with `ls-remote`. Through
this report, the coordinator pushed with `git push origin refs/heads/<b>:refs/heads/<b>`, not through r2's
`code/checkpoint_push_p309.py`, because that tool was relocated only at step 4. The pushes are therefore not in
`ledger/CHECKPOINT_PUSHES.jsonl`. Disclosed.

## 2. Equivalence proof (P8): `governance/R2_EQUIVALENCE_P8_FINAL.json`

* **(a) Pins outside the namespace.** From drill attempt 5's synthetic F' `fa65b761` (the final bytes), compared with
  r1's F: **all 73 pins outside the campaign namespace are identical** in path, sha256 and git blob. These are the
  research, producer and data pins.
* **(b) Reverse substitution.** At HEAD, of the operative files compared with F:
  * 12 unchanged;
  * **7 relocation-only, whose bytes after reverse substitution equal F's exactly**;
  * 20 changed beyond the map (§3);
  * 7 new.
* **(c) Completeness.** There are 34 remaining r1-token occurrences.
  * 23 are inherited text: fc2/, verify/*.md and the verifier author's records.
  * 11 are deliberate r2 references: the guard's `_PRIOR_NAMESPACE`; the r1 production token; the planted control's
    `TOKEN_R1`; the verifier author's three r1-namespace constants; `make_freeze_params.R1NS`; the r1-tree checks in
    the self-audit, the checkpoint tool, QC13 and the drill.
* **(d) Frozen-parameter key diff.** 39 differences, each classified in the file, **0 unexpected**:
  * `campaign` (binding);
  * `disclosed_liabilities` (r2 appended);
  * relocated document paths; blob changes only for the quarantine config and the scanner allowance;
  * the driver's path and sha256;
  * the provisional marker and pending names;
  * the result path;
  * the freeze-record path;
  * the inherited and r2 review entries.
* **(e) Runtime pins.** These are host-bound, and r2's are written at the worker freeze.

**No scientific parameter differs.** The budgets, workers, interval, outcome table and Stage parameters are
unchanged. The exactly-once sites and the backstop pins are unchanged (`R2_REPIN_LIST.json`). The production read
path's 13 functions have hashes equal to r1's (T13).

## 3. Files changed beyond the map

| file | change | condition |
|---|---|---|
| `code/p309_guard.py` | `_PRIOR_NAMESPACE`, `_FORBIDDEN_NAMESPACES`; TestContext refuses refs under either namespace | F1, P18 |
| `code/p309_qualify.py` | QC13 checks both namespaces and the r1 tree; `SCRATCH` from `scratch_dir`; Q-HOST (`qhost_preflight`, monitor, abort, the summary gate `Q-HOST`); `items_table` and `run_item` factored out with the same lambdas | F1, P2, P7, P10, F5 |
| `code/p309_driver.py` | the seal commit message says "formal r2" (a campaign label the inventory missed; not pinned) | relocation, disclosed |
| `code/checkpoint_push_p309.py` | base when the ref is absent: c902fe2f; check 7d is the r1 tree; the record message says r2 | P2 |
| `code/p309_self_audit.py` | A3 covers r2's own records, and r2's copies of r1's governance records compared with r1's blobs; A7 base c902fe2f plus the r1 tree; the research check is still eb9a9c22 | P2 |
| `code/make_freeze_params.py` | r1's 12 reviews INHERITED at r1's paths; R2_REVIEWS; R2_DISCLOSED_LIABILITIES appended | P2 |
| `code/p309_env.py` | `scratch_dir()` | P7 |
| `code/p309_static_check.py` | T11 (base rule), T12 (both namespaces), T13 (read path pinned); T7 scope extended | P6(e)(f), F1, F5 |
| `code/p309_placeholder_check.py` | five r2 allowlist entries (file and token) | P16 |
| `code/p309_host.py` (new) | after `61731123`: `gate_checks` / `monitor_verdict` pure; `instance_unverified`; `monitor_heavy_cpu_fraction` | P9, P10 |
| `config/SCANNER_ALLOWANCE_P309.json` | the r1 token kept; token_definitions; import allowlist (p309_host, urllib, urllib.request, p309_qualify for drill -c only); git_runners +3; reviewed_functions +9; ref_mutation_functions +4; verb options clone and version; `production_read_path_pins`; refreshed hashes (`R2_REPIN_LIST.json`) | P4, P6, F1 |
| `tests/test_p309_exactly_once.py` | `sandbox_base()`, `manifest_bytes()`, pre/postconditions, refusal-detail checks, both-namespace leak check, `scratch_dir` | P6(a)–(c), P7, F1 |
| `tests/test_p309_guard.py` | base from `X.sandbox_base()` (tests/ put on sys.path); both-namespace leak checks; `scratch_dir` | P6(e), P7, F1 |
| `tests/test_p309_site_backstop.py`, `tests/test_p309_d5_exception.py` | both-namespace leak checks; `scratch_dir` | F1, P7 |
| `tests/planted_control_p309_formal.py` | `TOKEN_R1` (an r1 token also fires MARKER_TOKEN) | F1 |
| verify/* and `tests/test_verify_scoped.py` | the verifier author's V1–V7 | F11 |

**New files:**
* `code/p309_host.py`;
* `code/p309_launch.py`;
* `code/p309_topology_drill.py`;
* the verifier author's report, ledger and sha256;
* `tests/test_p309_host.py` (41 decision tests; run by the drill).

## 4. Status of every condition (where to check)

* **P2 / F9.** The table and its supplement. The anchors are as in §3. The r1-tree check is in the checkpoint tool,
  the self-audit and QC13.
* **P3.** The bindings are implemented provisionally under OD-R2-1(b):
  * grant path and result path under FNS2;
  * grant `campaign` `p5y_k5_cell309_p309_r2`;
  * result SCHEMA `rebaseguard.p5y.k5.cell309-p309-r2.result.v1`.
* **P4.** The host tools are in code/: no executable bit; reviewed and registered; covered by T7.
* **P5 / F1–F5.** The drill: §5.
* **P6.**
  * (a)–(c): test_p309_exactly_once.
  * (d): the two mutants, built only in the drill clone.
  * (e): the guard harness and the verifier helper, and T11.
  * (f): T13 and `production_read_path_pins`. All 13 hashes equal r1's at F.
  * (g): `R2_REPIN_LIST.json`.
* **P7.** `p309_host.scratch_root`, through `p309_env.scratch_dir` and the verifier author's helper.
* **P8.** §2 and §5.
* **P9.** `p309_host.exclusion_gate` and `isolation`:
  * refuses on unreadable /proc, hidepid, or no visible foreign process;
  * excludes its own cgroup;
  * foreign processes recorded only as pid, uid, tag, CPU fraction and cmdline sha256;
  * git never run in a foreign root;
  * the foreign root only stat()ed.

  In development, a planted busy fake cell-308 process blocked the gate and the monitor, and no command line was
  recorded.
* **P10.**
  * The runner's `qhost_preflight` refuses before the attempt directory and RUN START. Controls: no record, a blocked
    record, and a valid record outside a unit.
  * The monitor samples every ≤ 60 s. Control: FAIL on a planted busy process, then SIGTERM to the parent.
  * The abort records FAIL and the summary. argv[0] is unaltered.
* **P11.** The launcher's unit properties. Development control: `--print-only` blocked in a container.
* **P12–P15.** The documents `R2_HOST_REQUIREMENTS.md` and `R2_BOOTSTRAP.md`, and the preflight checks.
* **P16.** The checker lists every allowed hit. The pre-freeze reviewer confirms them.
* **P23.** Adopted in addendum 1. The runner refuses any second attempt.
* **F6, F7, F8, F10.** Addendum 2 (text).
* **F11.** The verifier author's report.

## 5. The cloud-tier drill (step 5)

| attempt | evidence | outcome |
|---|---|---|
| 1 | `evidence/drill/20261001T132113Z` | FAIL before F': code/p309_placeholder_check.py refused 7 hits in r2's own texts. Fixed (§3) |
| 2 | `evidence/drill/20261001T132325Z` | FAIL. **QC11 PASSED post-freeze**; every control caught. Three defects: (1) the QC16 import; (2) confinement parsing (a false alarm, re-checked clean); (3) the F2 status trip, caused by the coordinator writing a file mid-drill. All fixed (`a39ec7c3`) |
| 3 | `evidence/drill/20261001T143415Z` | Items, witness, controls, host and ledger verdicts all PASS; QC11 193 s post-freeze; QC_D5 2 802 s; the P309 repository was unchanged. **Defect it exposed:** the second-record control's `reset --hard` discarded the items' uncommitted ledger rows before the export (attempts 2–3 carry incomplete drill ledgers, so F4 "rows in full" is not met by them). Fixed with `reset --mixed` plus restoring the record bytes, and a new control `ledger_rows_kept_across_reset` (`93b41bd9`) |
| 4 | `evidence/drill/20261001T160409Z` | **PASS**, independently validated (37/37 checks over the report and the kept clone). 107 drill ledger rows exported in full; F2 held; every control caught |
| 5 | `evidence/drill/20261001T171235Z` | **PASS on the final bytes (`61731123`)**, independently validated (38/38, including the 41 host-package tests in the clone). F' `fa65b761`, FR' `1819aff3`; 108 drill ledger rows in full; QC11 post-freeze, QC12 T1–T13, self-audit A1–A10 and QC13 all pass inside the drill; every control caught; F2 held |

## 5a. Repairs after attempt 4 (`61731123`): none was exercised by the cloud tier

1. **The worker-tier drill's preflight** ran without the host configuration. It would have failed on a suitable
   worker. It now uses the launch record's host config.
2. **Q-HOST continuity:** a single IMDS timeout counted as an instance change and would have ended the single
   official attempt. It now passes as `instance_unverified` when boot, machine-id and hostname are unchanged. A
   different instance still fails.
3. **The Q-HOST monitor** used the start gate's strict threshold, so light cell-308 activity could end r2's only
   attempt. It now uses `monitor_heavy_cpu_fraction` (default 0.5) or a heavy-job pattern (OD-R2-5 option (i)).
   The start gate is unchanged and strict.

The decisions are now the pure functions `gate_checks` and `monitor_verdict`. `tests/test_p309_host.py` has 41
cases; with the old semantics restored, C05 and M01 fail, as they should. The drill runs these tests in its clone.

## 6. Open items for the delta review and later gates

* **The worker tier is untested.** The worker-tier drill (P14), the systemd unit, Q-HOST inside a real unit and the
  launcher's start path have not run, because this container has no systemd. They run at step 8d.
* **`--host-rerun` is not under Q-HOST.** The runner's `--host-rerun` (A14 QC10 re-run before a grant) is not yet
  gated by Q-HOST. It belongs to the later grant window, so it is listed rather than changed now.
* **The linear-history assumption.** `recorded_freeze` and both sandbox base rules use git's default history walk
  (verifier author's note). The single-writer, linear history between F and Q is assumed (P13).
* **QC_D5 takes long.** It took 2 866 s in the container (attempt 2). The worker window in `R2_HOST_REQUIREMENTS.md`
  §3 allows for it.
* **Owner decisions OD-R2-0 … OD-R2-6** (step 7). Nothing in this report decides any of them.
