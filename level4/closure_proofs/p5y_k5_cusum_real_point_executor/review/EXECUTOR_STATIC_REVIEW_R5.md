# Independent static review of the r5 real point executor

## 1. Verdict

**EXECUTOR_STATIC_REVIEW: PASS_WITH_SCOPE_LIMITATION**

## 2. Findings from earlier reviews

- X1 = CLOSED
- N1 = CLOSED
- N2 = CLOSED
- N3 = CLOSED
- D1 = CLOSED
- D2 = CLOSED
- D3 = CLOSED
- D4 = CLOSED

## 3. Binding rulings

- CANONICAL_SLOT_BINDING = PASS
- LAUNCH_NOTICE_BINDING = PASS
- CLI_SLOT_CANNOT_OVERRIDE = PASS
- TOCTOU_SLOT_STATE_BINDING = PASS
- ACCEPTED_SEMANTICS_UNCHANGED = YES
- PREDECESSOR_ARTIFACTS_PRESERVED = YES
- X2_X8_LOAD_BEARING = NONE

---

## Scope and method

- **What I did.** A read-only review of `/Users/suzhe/ReBaseGuard-k5r` at HEAD `f83cd182`. I modified no file and ran nothing on any host. I did not import the executor or the verifier. I used only git, shasum and `json` parsing in python3.
- **Commit chain** (recomputed):
  - `59bd3268` (18:59 +0900) adds only `EXECUTOR_SPEC_R5.md`, 88 lines.
  - `a16d22b5` (20:01) changes only files inside `p5y_k5_cusum_real_point_executor/`.
  - `f83cd182` (HEAD) adds only the 20 files under `evidence/qualification_r5/`.
  - So the spec was committed before the code, and HEAD is the r5 evidence commit on top of the freeze.
  - `EXECUTOR_SPEC_R5.md` has not changed since `59bd3268`.
- **Identity.**
  - I recomputed the executor identity over the 11 `IDENTITY_FILES` as `ef1c86e4…d41b`. It matches the protocol (status FROZEN_PRE_QUALIFICATION), the result and `RUN_PROVENANCE.json`.
  - All 279 entries in `EXECUTOR_PINS.json` match the files at HEAD.
  - The pins sha is `634e4da1…`, equal to the provenance value.
  - The protocol file sha is `59a91e20…`, equal to the `protocol_sha256` in the result.
- **Evidence.**
  - All 16 `part_sha256` values match their files.
  - `sha256(QUALIFICATION_RESULT_EXECUTOR.json) = 9c7ca7ba…7229`. It equals both `RUN_COMPLETE.result_sha256` and `RUN_PROVENANCE.qualification_result_sha256`.
  - All 25 `qualification_sources_sha256` entries match the blobs at `a16d22b5`.
  - `git_commit` and `git_commit_at_end` are both `a16d22b5`, and both porcelain lists are empty.
  - Mode is FROZEN_QUALIFICATION, guard DENY, and there were 0 runner failures.
  - EG01–EG23 are all PASS.
  - The governed rows pass 45/45; 28 of them are `x1_*` rows.
  - The governed mutants N01–N05 and X01–X05 are all detected (10/10).
  - The verdict is QUALIFIED_AWAITING_EXTERNAL_AUTHORIZATION, EXECUTION_AUTHORIZED is false and REAL_CELL_EXECUTED is NO.

## 4. Findings with evidence

### 4.1 X1: the canonical slot is derived before verification (CLOSED)

**Derivation.**
- `supervisor.namespace_slots` (`code/supervisor.py:108-116`) mirrors the frozen `check_P11` (`prelaunch_verify.py:454-466`):
  - it refuses symlinks, non-directories and names that do not start with `slot-`;
  - it requires the slots to be contiguous from `slot-1` via `PR.slot_dir(n)`.
- `slot_binding_problems` (`supervisor.py:119-152`) derives `canonical = PR.slot_dir(len(names)+1)`. This is exactly P11's `PR.slot_dir(len(entries)+1)`.
- `slot_dir` enforces `max_slots` (`probe_rules.py:157-161`). An exception there is refused as "no launch slot left".

**Clauses** (all accumulated, with no short circuit):
- the CLI slot equals the canonical slot (`:128`);
- the countersignature's `attempt_slot` equals the canonical slot (`:130`);
- the ledger holds at least one LAUNCH_NOTICE for it, and not more than one (`:132-137`);
- the ledger holds no event other than that notice for the canonical slot (`:138`);
- the ledger names no slot absent from the namespace other than the canonical one (`:140`). This is the same set expression as P11 at `prelaunch_verify.py:467`.
- The notice has exactly the keys `{event, slot, authorization_sha256, utc}`. These are the frozen `retry_policy.slots_and_ledger` fields.
- The notice names the authorization's file-bytes sha256.
- The notice is not older than `AUTHORIZATION_UTC` (`:143-151`).

**Inputs.**
- `launch_state` (`:155-182`) reads the ledger only through the frozen `PV.ledger_entries()`, which requires it to be committed, unmodified and append-only. Any exception becomes a refusal.
- It hashes the same `AUTHORIZATION_ACTIVE.json` path that the verifier uses (`paths.PROTOCOL_NS/protocol/…` and `prelaunch_verify.AUTH_ACTIVE`).
- It reads the same `COUNTERSIGNATURE_FILE` that `countersignature_problems` uses.
- A non-int `attempt_slot` becomes None, and is therefore refused. A bool becomes `"slot-True"`, which is also refused.

**Order of operations** (`governed_prelaunch`, `:192-217`):
1. Namespace check (`:199`).
2. Guard policy check.
3. `launch_state` (`:204`). Any problem returns `refusal: SLOT_BINDING_REFUSED` before binding, before the verifier and before any mkdir.
4. `supervise` (`:229-254`) keeps SLOT_EXISTS first (`:234`). `slot.mkdir()` (`:245`) and `RUN_STATE` (`:254`) come only after a permitted decision.
5. On refusal it returns `terminal: None`. No marker, no RUN_STATE, no VOID. `failure_class` SLOT_BINDING_REFUSED is never written to disk. CLI exit code is 3 (`:404`).

**No fallback or rewrite.**
- `main` builds the slot only from `--slot` (`:401`).
- Nothing in `supervise` picks, corrects or replaces a slot.
- `tests/test_executor.py::test_r5_canonical_slot_before_verification` asserts that `slot_dir(len(` does not appear in `supervise`.

**The r4 counterexample is now refused.**
- Setup: empty namespace, notice for slot-1, countersignature slot 2, `--slot 2`.
- `slot_binding_problems` yields "requested slot slot-2 is not the canonical slot slot-1" and "countersignature slot slot-2 …", i.e. SLOT_BINDING_REFUSED.
- Evidence row `x1_02_authorization_and_cli_slot_2_refused` carries both reasons and shows `slot-2` absent.

### 4.2 Faithful reading of "authorization.slot == canonical_slot"

- The r4 authorization template admits no extra keys, so no slot field can be added.
- r5 binds the authorization to the slot in two independent ways:
  - **The LAUNCH_NOTICE** names the slot and the authorization's file-bytes sha256. It is committed and published: the frozen P11 checks both the notice and the publication (`prelaunch_verify.py:494-502`).
  - **The countersignature** is committed exactly once, after the authorization, by an identity independent of the execution host. It names the authorization's sha256 and the slot (`authorization_interface.py:177-223`).
- Both must equal the canonical slot before the verifier runs. I judge this a faithful and complete reading.
- The added staleness rule (notice UTC ≥ AUTHORIZATION_UTC) only narrows admission. It cannot conflict with the frozen contract.

### 4.3 TOCTOU binding (PASS)

- **Snapshot.** `launch_state` records the canonical slot, the namespace slot list, the ledger sha256, the authorization sha256, the countersignature sha256 and the notice.
- **After PASS** (`:212-215`):
  - The launch state is re-derived and compared key by key (`launch_state_changes`, `:220-226`).
  - The verifier's own P11 detail must approve the same slot. `verifier_approved_slot` (`:185-189`) parses `next slot <slot-N> (…`. That wording is only produced on a P11 pass (`prelaunch_verify.py:503`). The frozen text is fixed, so the parse is stable.
- **Ignored problems in the second snapshot.** The second snapshot's `problems` are ignored (`after, _ =`), and that is safe. Every problem-generating change also alters a compared field:
  - An unreadable ledger gives `launch_notice` None.
  - A foreign entry changes `namespace_slots`.
  - A changed UTC or slot changes the authorization or countersignature sha.
- **Digest.** The snapshot is stored as `decision["launch_state"]` (`:216`) before `LC.build_run_state` hashes the decision (`lifecycle.py:156`). So `prelaunch_decision_sha256` covers it.
  - The evidence row `permitted_synthetic_end_to_end` recomputes this digest over the decision that includes `launch_state`.
  - `x1_01_canonical_slot_bound_everywhere` shows that RUN_STATE, the decision, the canonical slot, the verifier's approval, the notice and the countersignature all name slot-1, and that the notice carries the decision's authorization sha.

### 4.4 Child re-check (PASS)

- `bound_decision_problems` (`authorization_interface.py:333`) adds one clause: `launch_state.canonical_slot` must equal the output slot. The existing checks already covered the decision's slot, RUN_STATE's slot and the digest.
- The re-check stays pure: no git, no ledger, no verifier.
- Row `x1_10_run_state_slot_not_canonical_refused` is refused for exactly that single reason.

### 4.5 X1 matrix and mutants (load-bearing, with notes)

**28 X1 rows:**
- 6 integration rows in the synthetic governed clone: 01, 02, 02b, 03, 06 and 10.
- 14 pure rows, including one positive case, the next slot after a completed slot.
- 7 TOCTOU comparator rows.
- 1 static order row.

**Each integration refusal carries its own reason.** The `refused()` helper (`qualify_governed.py:231-235`) requires:
- the specific refusal class;
- a digit-masked reason needle;
- that the named slot is absent;
- that the namespace is absent.

**Mutant detection.** Detection is recorded as "any row fails" (`qualify_governed.py:547-548`). The recorded `failing` lists show that each X mutant is caught by its own target rows:

| Mutant | Rows that catch it |
|---|---|
| X01 trust CLI slot | `x1_02_*`, `x1_03_*` (integration and pure) |
| X02 ignore countersignature slot | `x1_02b_*` (integration and pure). The integration row would otherwise fall through to the verifier's countersignature check as PRELAUNCH_REFUSED, so the needle and class make it load-bearing. |
| X03 ignore notice slot | `x1_pure_04`, `x1_pure_05`, `canonical_slot_already_has_outcome` |
| X04 skip post-verification check | `x1_09_static_toctou_order` only |
| X05 allow duplicate notices | `x1_pure_05` |

Two weaknesses in the matrix, neither load-bearing:
- **X04 is caught only structurally.** No integration row changes the launch state during verification. The comparator itself is covered by the pure TOCTOU rows.
- **Some pure rows check only that a refusal happened.** The TOCTOU rows and `noncontiguous_namespace` check truthiness rather than a reason needle.

### 4.6 N1–N3 and D1–D4 remain closed

- **N1.** The verify-before-mkdir order is unchanged; the order row and the static test both pass.
  - The r4 integration row `verifier_exception_creates_no_slot` was replaced by `prelaunch_refused_before_authorization_creates_no_slot`. That row now stops at SLOT_BINDING_REFUSED and accepts either refusal class with no reason needle.
  - The verifier-exception path is still covered at unit level (`part_authorization`: `verifier_raises`, "verifier raised FileNotFoundError").
  - It is also safe by construction: `run_verifier` fails closed, and any exception propagates before `mkdir`. See D-2 in §5.
- **N2.** `static_single_verifier_call_site` and `post_start_full_verifier_unreachable` pass, and N02/N05 are detected.
- **N3.** `slot_admission_requires_supervisor` passes and N03 is detected.
- **D1–D4.**
  - `executor_core`, `lifecycle`, `backends`, `consumer`, `input_adapters`, `executor_cli`, `paths` and `exec_fixtures` are byte-identical between `77afd942` and `a16d22b5`.
  - EG18–EG21 pass. The mutant groups are not reduced: E 16/16, P 4/4, D+A 7/7, L+V 5/5, R 2/2, N 5/5, plus the new X 5/5.

### 4.7 Semantics and predecessors (unchanged)

- **Mathematical code paths.** `git diff 77afd942 a16d22b5` touches only `supervisor.py`, `authorization_interface.py` (+2 lines, the slot clause), the qualification harness, the pins, the protocol, the tests, the README and DEV_CALIBRATION. No mathematical code path changed.
- **Replay.** The replay payload is `cb28b972…e7e0` twice, with 0 scientific leaf differences. It is identical to r4.
- **Science file.** `SCIENCE_PREREGISTRATION_R4.json` has sha256 `9ace6896…3780a`.
- **Frozen protocol namespace.** `git diff 327cc35e HEAD` on `p5y_k5_cusum_first_real_probe_protocol/` is empty. The verifier is still `54b198bc…`.
- **Predecessor files.** `git diff 327cc35e HEAD` is empty for all of these:
  - `evidence/qualification`, `_r2`, `_r3` and `_r4`;
  - `review/*R1-R4`;
  - `RESULT.md`, `RESULT_R3.md` and `RESULT_R4.md`;
  - `EXECUTOR_SPEC.md` and `EXECUTOR_SPEC_R2` to `EXECUTOR_SPEC_R4`;
  - `TRUST_MODEL.md`.

  `git diff 34bb9b0b HEAD` on the r1–r3 files is also empty.

### 4.8 Classification of X2–X8 (NONE is load-bearing)

I agree with DEV_CALIBRATION's r5 classification:

| Finding | Why it is not load-bearing |
|---|---|
| X2 | DENY is also enforced by the child guard and the verifier. |
| X3 | Unreachable behind the static and runtime fences, and fails closed as a non-transient class. |
| X4 | A VOID on genuine drift within milliseconds is the frozen-consistent outcome. |
| X5 | Documentation only. |
| X6 | Evidence granularity only. |
| X7 | The authorization bytes, the executor identity, the protocol and the K1 binding are all re-hashed. |
| X8 | See below. |

**X8.** Under r5, `--mode governed_manufactured` against a live activation would satisfy the canonical binding and spend the authorized slot on a MANUFACTURED record.
- It cannot produce a wrong or unreproducible scientific record.
- No real R''' is formed.
- The frozen P11 then blocks the campaign, so it fails closed.
- It is an operator-procedure item. TRUST_MODEL already prescribes `supervisor.py launch --mode real` (`TRUST_MODEL.md:52`). The external activation runbook should forbid every other mode on the execution host.

## 5. New defects, ranked

No new load-bearing defect was found.

- **D-1. LOW, not load-bearing.** The notice `utc` format is not frozen; `retry_policy` only names the field.
  - `_utc` (`supervisor.py:98-104`) refuses a notice whose `utc` is a numeric epoch. The refusal is fail-closed, but its reason text ("stale LAUNCH_NOTICE") is misleading.
  - A timestamp without a timezone offset is read in local time, the same semantics as P12.
  - The activation runbook should require ISO-8601 with an explicit offset.
- **D-2. LOW, test coverage, not load-bearing.**
  - The integration evidence for "a verifier exception creates no slot" (r4 row `verifier_exception_creates_no_slot`) was replaced by a row that now stops earlier, at the slot binding. That row accepts either refusal class with no reason needle.
  - The exception path is still covered by the `part_authorization` unit row and by construction: `run_verifier` fails closed, and any raise propagates before `mkdir`.
- **D-3. LOW, test strength, not load-bearing.**
  - X04 is detected only by the static order row.
  - The TOCTOU comparator and namespace pure rows check truthiness rather than a specific reason.
  - Detection is recorded as "any row fails", not per target row. The recorded `failing` lists do show target rows for X01–X05.
- **D-4. INFO.** `launch_state` imports and calls `prelaunch_verify.ledger_entries` before `validate` checks the verifier's source pin. The call is git-read-only, and a tampered module is still refused by `verifier_source_problems` before any decision exists. This falls under the accepted host limitation; I recommend no on-host change.

## 6. Scope limitations accepted

- **The host is not a trust root.** The canonical-slot binding, the TOCTOU re-snapshot and the child re-check are consistency and fail-closed measures against accidents.
  - An on-host actor could swap state A→B→A during verification, race the gap between the re-snapshot and `mkdir`, or forge a coherent RUN_STATE.
  - This belongs to external authorization, the published ledger and independent adjudication. I recommend no further on-host anti-tamper work.
- **Publication read.** Publication is simulated by a local bare repository. A real `git ls-remote` against GitHub has not been run end to end. This is frozen-verifier behaviour, and the verifier is unchanged.
- **Manufactured input only.** The positive end-to-end path uses manufactured input (`governed_manufactured`). The real-mode re-hash and the Q01/Q14 gates are covered statically and by unit rows only.
- **Real input remains denied.** REAL_INPUT_ARITHMETIC_GUARD = DENY and EXECUTION_AUTHORIZED = false. No real K1 cell was executed and no real R''' was formed.
