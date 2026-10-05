# Pre-freeze follow-up review (gate step 9): the reviewer's packet (deliverable 8 of 10)

**When it is used.** Only after all of these:
- the 8d drill is classified **PASS** (`WORKER_TIER_PASS_FAIL_RULES.md`);
- the owner's filing authorization at return point R-2 has been given, and the authorized evidence filing into r2 has
  been made and verified (`OWNER_RETURN_CONDITION.md`).

Before that, this packet is prepared, not issued.

**Who.** A **fresh** independent reviewer. They wrote none of:
- r2's code, the hardening, SF1-A or this packet's tools;
- the host evidence;
- any earlier review.

Earlier reports are guides, never evidence: every answer rests on git objects, the filed evidence and the reviewer's
own recomputation.

**Boundaries:**
- **No git write** to the session repository. Use only `git show`, `diff`, `log`, `ls-tree`, `cat-file`,
  `rev-parse`, `merge-base` and `ls-remote`.
- **NEW Γ309 TARGET EVALUATIONS = 0.** Never run or import:
  - the driver;
  - the runner, the launcher, the host tool's run paths or the topology drill;
  - any evaluator.
- No cell values, decoy outputs, grants or network beyond `git ls-remote`.
- **Fresh workspace only.** Use a fresh `--no-local` clone, with `P309_SCRATCH_ROOT`, `P309_EVIDENCE_DIR` and `TMPDIR`
  pointed into the workspace.
- **Tools you may run:**
  - r2's cheap static tools: `code/p309_static_check.py`, `code/p309_scan_pins.py --list`,
    `tests/test_p309_static_controls.py`, `tests/test_p309_scan_allowance.py`, `code/make_freeze_params.py`,
    `code/make_freeze_manifest.py` (incl. `--check`), `code/p309_placeholder_check.py` and
    `code/p309_self_audit.py QUALIFICATION`. Run them in the clone only;
  - this packet's read-only validator, `tools/validate_worker_drill_8d.py`, on a reconstruction (§3).
- **Ledger.** Keep an execution ledger: one JSON row per command, written as you go.

## 1. Inputs (all named by commit and sha256 in the brief that issues this review)

| id | input | where |
|---|---|---|
| I-1 | r2 at the drilled commit `501f48cb` (tree `d7e2c832`), and r2's head after the authorized evidence filing (`<R2_FILING>`) | origin `claude/p5y-k5-cell309-p309-r2` |
| I-2 | the SF1-A records: `governance/REVIEW_SF1A_DELTA.md` (sha256 `1f95ca2f…28a2`), `governance/R2_SF1A_INCORPORATION_RECORD.json`, `governance/OWNER_DECISIONS_R2_MSG6_VERBATIM.md` | r2 `501f48cb` |
| I-3 | the 8a audit bundle; the 8b-initial and 8b-final verdict records | the hardening namespace `host_evidence/`, and r2 if filed |
| I-4 | the owner's OD-R2-4 answer (verbatim) and `APPLIED_CHANGES_<UTC>.json` | the hardening namespace, and r2 governance if filed |
| I-5 | the cell-308 forms, Parts A–D (redacted as the operator asked) | `host_evidence/` |
| I-6 | the 8d records: `LAUNCH_STDOUT`, `launch_<utc>.json`, `STATIC_8D` (pre and post), `PRELAUNCH_8D`, `VALIDATION_8D`, the journal's `[PASS]/[FAIL]` lines, the E-1–E-5 outputs | `host_evidence/DRILL_8D_<stamp>/` |
| I-7 | `evidence/drill/<stamp>/{DRILL_REPORT.json, DRILL_ZERO_TARGET_LEDGER.jsonl, DRILL_EXPOSURE_LEDGER.jsonl}` and the GOVERNANCE ledger row | r2 `<R2_FILING>` |
| I-8 | this packet (all ten files and `tools/`), by its commit and its `PACKET_MANIFEST.json` | the hardening branch |

## 2. The ten questions (answer each YES / NO / PARTLY, with your own evidence)

**Q1. Is r2 `501f48cb` exactly what was drilled?** Check all of:
- `DRILL_REPORT.json` `clone_base` = `501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853`;
- the embedded `p309_before.head` = `501f48cb`;
- the pre-launch check's C01 (HEAD), C02 (tree `d7e2c832`) and C08 (the four reviewed files' sha256) were true;
- the filing commit `<R2_FILING>` descends from `501f48cb` and changes **only** `evidence/drill/<stamp>/`,
  `ledger/ZERO_TARGET_LEDGER.jsonl` (one appended row), and whatever host evidence or governance records the owner's
  R-2 authorization names. `git diff --stat 501f48cb <R2_FILING>`; every `code/`, `config/`, `fc2/`, `tests/`,
  `verify/` and `freeze/` blob is identical (`git ls-tree -r`).

**Q2. Was SF1 resolved on those exact bytes?** Check all of:
- `code/p309_qualify.py` at `501f48cb` has sha256 `540df0552bfc31512289e30eaf1ead57bf82a4ac806f38080439c05c43f9a3af`,
  the bytes `REVIEW_SF1A_DELTA.md` accepted ("SF1: RESOLVED");
- `R2_SF1A_INCORPORATION_RECORD.json` binds that fast-forward;
- in the drill, the runner passed its `fs_probe` with the ledger-appendability step: `items.main.rc` = 0, and the
  gates exist, which the runner writes only after the probe, H3, Q-HOST and RUN START;
- state which filesystem was probed: the drill clone under `P309_SCRATCH_ROOT`. Say whether it is the same filesystem
  as the P309 clone (R-FS-9; the 8a S-01 records for both roots).

**Q3. Did the host audit pass?** Check all of:
- A-01 ran the verified `p309_host.py` bytes (sha256 `ec9c8416…`);
- every 8b row is evidenced;
- the 8b-final verdict is `HOST_ACCEPTED_FOR_WORKER_TIER`, by the rules in `HOST_VERDICT_RULES_8B.md` (recompute the
  verdict from the rows yourself);
- the NEEDS CONTROLLED WRITE TEST items were evidenced by 8d, not assumed.

**Q4. Were all owner-approved host changes applied exactly?** Check all of:
- every item in `APPLIED_CHANGES` matches the owner's OD-R2-4 text item by item (the command, the scope, and the polkit
  rule's sha256);
- no unconsented change was made (B-37);
- the A-02 results agree;
- the M4 holds were restored after the window, with a record.

**Q5. Did the worker-tier drill pass?** Re-validate independently (§3). Your validator output must be PASS with
`failed: []`. Also check all of:
- E-1–E-5;
- the report states, or you state, what 8d does not show (`WORKER_TIER_DRILL_8D.md` §11, W7);
- the 20 gates, the 9 controls and the host functions (U01–U03 ran; P02 not applicable as non-root).

**Q6. Were the Cell-308 coordination constraints satisfied?** Check all of:
- Parts A–C were complete before the launch, and the drill's `utc_start`…`utc_end` lies inside Part C's window;
- the launch record's `gate` passed, and its `gate.processes` uids are the agreed ones;
- `foreign_uids` was non-empty (the redacted `host_config`);
- Q-HOST passed for the whole run (`gates["Q-HOST"]`);
- Part D reports no cell-308 heavy start;
- the M4 consent included the operator's.

**Q7. Are scanner pins and manifests current?** Check all of:
- the runner's `Q_D5` passed inside the drill, and the post-run static re-run was current;
- your own run in your clone at `<R2_FILING>`: `p309_scan_pins.py --list` ends "P309 SCAN PINS: all current";
- the generators and `make_freeze_manifest.py --check` give "MANIFEST IDENTICAL";
- the unresolved-marker check passes;
- QC15 A1–A10 are all true (A7: no path outside r2's namespace changed since `c902fe2f`; A3: governance immutable).

**Q8. Were there any interruptions?** Check all of:
- list every NOT_STARTED, INTERRUPTED or FAIL event in the window, with its evidence: the journal's boot list (no
  reboot inside the window), `ATTEMPT_START`'s boot id if observed, Part D, and the hardening namespace's
  `host_evidence/`;
- none may be unreported.

**Q9. Were any retries or resumes attempted?** Check all of:
- exactly one launch with `launched: true` (E-2) and one unit (E-1);
- one new `evidence/drill/<stamp>/` and one GOVERNANCE row;
- no earlier worker-tier drill on these bytes, or an owner record authorizing a further one, which is then quoted;
- no resume path used (none exists).

**Q10. Are there remaining blockers before OD-R2-0(D)?** List each item as **blocking** or **not blocking**, with
its owner. At minimum, consider:

| # | item | expected state |
|---|---|---|
| 1 | the R-2 filing commits made and verified | done |
| 2 | this review's record filed into r2 | needs the owner's filing authorization, if not already given at R-2 |
| 3 | OD-R2-6(i), the target-execution host | open (message 5 left it unanswered). It is a grant-stage decision; say whether it blocks OD-R2-0(D) |
| 4 | OD-R2-6(iii) | "A qualification host must be selected and accepted through the required governance process before the official qualification is authorized". Whether the drilled host is that host is an owner decision, presented together with OD-R2-0(D) |
| 5 | the freeze on the worker (step 10): single writer, clocks synchronised, frozen tree ids equal to those reviewed and drilled | it must be planned. The freeze manifest binds the host id, so it must be the qualification host |
| 6 | the official run's filesystem probe, if R-FS-9 applies | it is checked at the official launch only |
| 7 | advisories | review 5's C4 (SF2, A1, A4–A7) and C5; SF1-A's C-A1–C-A5. Not blocking unless you find otherwise |
| 8 | the QC10 host re-run (OD-R2-6(ii)) | before any grant, not before the freeze |
| 9 | Cell 309 | OPEN; no grant; Γ309 forbidden |

## 3. Re-validating the drill without the host (reconstruction)

The validator judges a P309 clone in its post-drill state. The reviewer reconstructs that state from git:

```bash
git clone -q --no-local --single-branch --branch claude/p5y-k5-cell309-p309-r2 <session repo or origin> "$W/clone"
git -C "$W/clone" checkout -q --detach 501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853
N="$W/clone/level4/closure_proofs/p5y_k5_cell309_p309_r2"
mkdir -p "$N/evidence/drill/<stamp>"
for f in DRILL_REPORT.json DRILL_ZERO_TARGET_LEDGER.jsonl DRILL_EXPOSURE_LEDGER.jsonl; do
  git -C "$W/clone" show "<R2_FILING>:level4/closure_proofs/p5y_k5_cell309_p309_r2/evidence/drill/<stamp>/$f" > "$N/evidence/drill/<stamp>/$f"; done
git -C "$W/clone" show "<R2_FILING>:level4/closure_proofs/p5y_k5_cell309_p309_r2/ledger/ZERO_TARGET_LEDGER.jsonl" > "$N/ledger/ZERO_TARGET_LEDGER.jsonl"
python3 -B <packet>/tools/validate_worker_drill_8d.py --clone "$W/clone" --stamp <stamp> \
  --launch-record <filed launch_<utc>.json> --verdict <filed VERDICT_8B_final> --prelaunch <filed PRELAUNCH_8D>
```

**Expected result:** `PASS` with `failed: []`.

**Reconstruction rules:**
- V01 holds, because the reconstruction's HEAD is `501f48cb`.
- V22 holds only if `<R2_FILING>` added no other file in the namespace. If the owner's authorization added host
  evidence or governance files in the same commit, compare V22's file list against that authorization instead, and
  say so.
- The `<R2_FILING>` ledger must equal `501f48cb`'s rows plus exactly the one drill row. Any other row is a finding.

## 4. Output

Write `REVIEW_PRE_FREEZE_501F48CB.md`, with its `.sha256` and execution ledger:
- **Line 1:** the title.
- **Line 2:** exactly one of:
  - `PRE_FREEZE_REVIEW_ACCEPTED`
  - `PRE_FREEZE_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS`
  - `PRE_FREEZE_REVIEW_REJECTED`
  - `PRE_FREEZE_REVIEW_BLOCKED` (evidence missing or not reconstructable)

**Include:**
- the exact commits and ancestry;
- the evidence reviewed, with hashes;
- the answers to Q1–Q10;
- the sections `## Blockers`, `## Should-fix` and `## Conditions`, with each condition marked
  **blocking-before-OD-R2-0(D)**, **before-freeze** or **advisory**;
- a closing statement on whether the evidence supports bringing OD-R2-0(D) back to the owner.

That last decision is the owner's alone. The review does not take it, and it authorizes no freeze, qualification,
grant or Γ309 evaluation.

**Wording.** Avoid the words that r2's `code/p309_placeholder_check.py` flags, so the record can be filed into r2
verbatim. Read its marker list in the code; do not quote it.
