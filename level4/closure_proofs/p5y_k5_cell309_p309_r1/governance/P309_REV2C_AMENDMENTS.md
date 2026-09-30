# P309 package rev. 2c: the complete list of changes from the reviewed rev. 2b (pre-freeze; formal campaign)

**Base.** Package rev. 2b, the research-namespace blobs that the incident review's condition C2 names:

| document | blob |
|---|---|
| `P309_PROTOCOL.md` | 5ac10d01 |
| `P309_FORMAL_PACKAGE.md` | 0867df9d |
| `P309_REVIEW_BRIEFS.md` | dadbf178 |
| `P309_OWNER_DECISIONS.md` | 613b2949 |

Those files are **not edited**, since the research namespace stays unchanged. The frozen package is rev. 2b **plus this
document**, which governs wherever the two differ.

**Review.** Incident review condition C2 says "Any change to a rule or parameter after this review needs a new
incident-independence review of the delta." Every change below is therefore submitted to:
* (a) that delta review;
* (b) the independent pre-freeze review.

The changes come from:
* the owner's rulings 2 (`governance/OWNER_RULINGS_2_P309_VERBATIM.md`);
* the independent reviews (`reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`, `reviews/REVIEW_U2_CHECK_P309.md`);
* implementation constraints found while building FC1–FC6.

**No Stage-1 scientific parameter changes.** The following are all exactly as in rev. 2b:
* the degree ladders;
* the indices;
* the numerics;
* the hull rules;
* the cover;
* the 48 CPU-h start threshold and the 12 CPU-h per-job limit;
* the Stage-1b budget of 21 600 s;
* the failure mapping;
* the Stage-1b fallback;
* the outcome table;
* strictness, rounding and adoption semantics.

## Changes

| id | rev. 2b text | rev. 2c | source | direction for closure |
|---|---|---|---|---|
| **A1** | QC14: `rehearse --cell 305`, a historical reproduction of 305 | **QC14′**: the full Stage-2 pipeline on **manufactured** consumer inputs, with the committed certificates of the declared out-of-band decoy cell (A2 family, h = 5, [1/2, 37/72]). Checks R1–R5 are in `code/p309_rehearse.py`. The real-data reproduction remains the post-grant, pre-marker historical control (protocol §4, unchanged) | the inherited quarantine forbids Γ(5,305) before a grant; flagged at the start of this campaign | none (qualification only) |
| **A2** | FC2 per protocol §7 and the rev. 1 spec | `fc2/FC2_SPEC_R2.md`: <br>• REAL band geometry-blind; <br>• TEST band = the hull of the declared synthetic h3 decoy cell; <br>• structurally separated production and test contexts; <br>• fail-closed admission bound to schema, cell, geometry, Ew (outward 2⁻¹⁰ hull of the cell), grant commit, frozen commit, manifest sha and self-pin, own identity, marker, the namespace, expiry, host and runtime; <br>• review mode; <br>• synthetic marker `refs/p309-test/TEST_ONLY_DO_NOT_EXECUTE_P309_MARKER`; <br>• the production marker is never created anywhere before the grant | owner rulings 2 (FC2 test band, sandbox marker, admission code) | none (refusal-only before a grant) |
| **A3** | QC08 on the declared A2 decoy cells (h3 and h5) | QC08 on the **h5** A2 decoy cell only. The h3 A2 cell is now the FC2 TEST band: the variant refuses it without a test context, and QC16 verifies its committed certificates under the sandbox test context | consequence of A2 | none |
| **A4** | protocol §7(a): a guard for Stage 1a | the same `p309_guard.producer_adapter` is injected **also as the Stage-1b certifier's `ov_quarantine`**, through the pinned RLR307 loader, in execute mode only. The Stage-1b hulls (the outward 2⁻²⁰ dyadic hull of each sub-block) lie inside Ew (the outward 2⁻¹⁰ hull of the cell), because a floor or ceiling on the coarser grid bounds the one on the finer grid. So the same admission window applies | U2-check §9 (a Stage-1b band guard was missing; without it an in-band Stage 1b raises, which gives EXECUTION_INDETERMINATE) | toward validity of execution; no parameter change |
| **A5** | Stage-1b budget "accounted as in §2.5" (no per-job limit stated) | Stage-1b per-job CPU limit = 21 600 s (the whole Stage-1b budget). Start threshold 21 600 s. Job order = the RLR307 order (degree descending, then block). Terminated jobs are discarded, which falls back | implementation needed a stated limit | none (a job can never exceed the total anyway) |
| **A6** | 307 driver pattern: a post-marker wall-clock cap (EVAL_CAP_S) that raises | **no post-marker wall-clock cap.** Stopping is by protocol §2.5 budget mechanics only (not starting jobs; RLIMIT_CPU per job), and "neither raises an exception" | protocol §2.5 wording; a raising wall cap would convert a slow host into EXECUTION_INDETERMINATE | removes a host-speed route to INDETERMINATE; wall time is unbounded but CPU is bounded (48 + 4 × 12 CPU-h for Stage 1a, 6 CPU-h for Stage 1b) |
| **A7** | `protocol/P309_FREEZE.json`; `postexec/`; "grant-scoped verifier" file | `freeze/P309_FREEZE.json` and `freeze/P309_FREEZE_MANIFEST.json`; post-execution checks in `code/p309_postexec.py`; the variant is `verify/srk_verify_indep_scoped.py` | the formal push procedure (check 7) refuses paths under `protocol/`, `postexec/` and any path containing `GRANT` | none |
| **A8** | check_grant: HEAD^^^ = freeze → qualification → review → grant | the same chain, but **checkpoint-record commits that touch only `ledger/CHECKPOINT_PUSHES.jsonl` may occur between the chain commits**. Q may touch only `qualification/` and the two execution/exposure ledgers; Rv only `reviews/REVIEW_QUALIFICATION_P309*`; G only the grant file, with exactly one parent. The frozen directories (code, config, fc2, freeze, tests, verify, governance) must be unchanged after F | the record-first checkpoint push adds one ledger-only commit per push | none |
| **A9** | grant schema (package §D) | adds the fields the admission checks read: <br>• `cell_interval`, `drift_hull_Ew` (must equal the outward 2⁻¹⁰ hull), `geometry`; <br>• `frozen_commit`, `frozen_manifest_sha256`, `verifier_id`, `guard_id`, `driver_sha256`; <br>• `execution_host.host_id_sha256`, `execution_host.worktree`, `runtime.python`; <br>• `marker_ref`, `not_after_utc`, `executions_authorized` = 1; <br>• `qualification_commit`, `qualification_review_commit` | owner rulings 2 ("grant bound to frozen protocol/hash, cell 309, Ew, verifier identity, execution identity/host requirements, and marker identity") | none |
| **A10** | exactly-once names in package §A | the marker `PRODUCTION_MARKER` and the pending ref `PENDING_REF` are defined once, in `code/p309_guard.py`. The scanner allowance covers the pending-ref NAME in the guard file only, under the owner's conditions (a)–(e) **(an extension of the owner's marker-name allowance, proposed here for review)**. The refs are created only in the two **exactly-once sites** `_arm_marker` and `_persist_pending` of `code/p309_driver.py`. Each begins with `_assert_execute_context`, and each is listed in `config/SCANNER_ALLOWANCE_P309.json` by function name and AST sha256 at the freeze. Emergency file: `<gitdir>/p309-emergency-result.json` | owner rulings 2 (scanner); FC6 | none |
| **A11** | protocol §4.5 "exactly as the pinned direct / combine compute it" | the pinned `c2_d5_forecast.direct` is **called unchanged** through a shim whose `tail_enclosure` returns 𝓗_SRK, computed beforehand from the same arguments (asserted), and whose internal crosscheck returns the same pair (vacuous for SRK). The genuine TC-T crosscheck runs first on the pinned `tct_rule`. QC14′ R2 shows that the shim gives exactly the unchanged `direct`'s Γ on the EMPTY path | U2-check U4(i) | none |
| **A12** | historical control (protocol §4) | two parts, both required byte-identical to C2's committed record for the target cell: <br>• (a) the 307-pattern control (S_I1 through the unchanged `direct`: Γ, A, provenance, 𝓗, M, pass, per-supply); <br>• (b) the P309 pipeline with the EMPTY GateResult. <br>Their digest is sealed | protocol §4; U2 F-U2-3 | none |
| **A13** | K1 record binding (candidate manifest open item) | the 307 pattern: the measurement's `k1_record_sha256` = the adopted input's `record_sha256` = the entry of the pinned K1 export manifest (`COMPOSITE_EXPORT_MANIFEST.json`), and the adopted inputs' `manifest_sha256` = that manifest's pinned sha256. C_upper, the auxiliary evidence and eps_cell_refined are read from the byte-pinned adopted inputs. No other copy of a P3 record (C6's recovered files included) enters | U2-check U6 | none |
| **A14** | QC10 "re-run on the execution host" | the **proposed** execution host is this isolated cloud environment. Its host id (sha256 of machine-id and hostname), interpreter and platform are recorded in the manifest, and QC10 runs here. If the owner names another host in the grant, QC10's host re-run must be repeated there before `execute`, as a grant condition | owner decision on execution isolation | none |
| **A15** | QC09 "RLR Stage-1 decoy per the RLR307 pattern" | declared Stage-1b decoy cover cells: **297 and 316**, the RLR307 decoys, both outside the band (guard-checked at run time) | declaring the decoys prospectively | none |
| **A16** | QC12 static structure | adds: <br>• `cell_inputs` reachable only from `run_execute`; <br>• the two exactly-once sites begin with `_assert_execute_context` and are called only from `run_execute`, `after_marker` and `run_seal_only`; <br>• no call of `main`, `compose`, `requirement`, `classify`, `critical_ratio` or `atom_constant_requirement` of the consumer, and no read of the C2 gate baselines (U2 F-U2-2) | U2-check U4(ii), F-U2-2 | none |
| **A17** | QC suite | **QC-U2**: the extended U2 structure checker (U2-check U3) and its controls pass on the frozen tree, **including the driver and the FC2 components** (U4). If it cannot pass, U2_UNRESOLVED ⇒ STOP before the freeze | U2-check U3/U4 | none |
| **A18** | QC16 | per `fc2/FC2_SPEC_R2.md` §8, both implementations: N1–N13, P1, P2, I1, D1, and the scanner allowance controls | owner rulings 2 | none |
| **A19** | quarantine scan | `code/p309_scan.py`: the research scanner unchanged, plus the owner-authorized narrow allowance, plus the formal rules MARKER_MUTATION, MARKER_ALIAS, MARKER_REBIND and GRANT_WRITE, plus the reviewed exactly-once sites | owner rulings 2 (scanner) | none |

## What is not changed (for the reviewers)

* Protocol §§1–6 (scope, Stage 1a, Stage 1b rules and fallback, Stage 2, the outcome table, the quarantine), except as
  A4–A6 and A11–A12 state.
* No new quantity is computed on the target path.
* No decoy result informed any change. A1 and A3 follow from the quarantine; A2 comes from the owner's ruling; A4–A19
  are mechanics and bindings.
