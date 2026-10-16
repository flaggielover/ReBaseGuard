# Security Review: p309-local-vm-diagnostic-dev-20261016

## Scope

Independent static re-review of all21 new V2 files. No newly confirmed reportable vulnerability; original finding csf_4a441982603758ecfe183ec2 remains unclosed because the trusted pre-interpreter launcher is absent. Execution blocked; I1-I7 OPEN; no formal admission.

- Scan mode: branch_diff
- Target kind: git_diff
- Target ID: target_sha256_aa743fba3b98454cc8ea65893dba04d7cd5f02ec0a77fd0165042868f408709b
- Revision range: e72da101e036e4bd96c0bb230b89be91058c8857...bc2562fd9ebff705b06dbb4d90d49b06a64fe8d6
- Snapshot digest: codex-security-snapshot/v1:sha256:eb88b136e0fdb3f2069a00f7f671059274086518d5474350ad6cf40d578f5142
- Inventory strategy: diff
- Included paths: .
- Excluded paths: none
- Artifacts reviewed: level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/.gitattributes, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/EtwCapture.cs, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/REPAIR_AND_APPROVAL_SCOPE.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Run-I2Feasibility.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/SOURCE_AND_EVIDENCE_SHA256.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Trusted-Entry.template.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/BINDINGS.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/layout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/review-execution-path-acls.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/windows-powershell-51-parse.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v1-independent-review/coverage.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v1-independent-review/findings.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v1-independent-review/report.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v1-independent-review/scan-manifest.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v1-independent-review/threatmodel.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v4-independent-review/coverage.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v4-independent-review/findings.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v4-independent-review/report.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v4-independent-review/scan-manifest.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v4-independent-review/threatmodel.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/v4-independent-review/EXPORT_MANIFEST.json

Limitations and exclusions:
- Required next implementation: concrete trusted outer launcher supplying fixed command bytes, absolute inbox WinPS, -NoProfile/-NonInteractive and a clean environment BEFORE CLR/PowerShell startup. Template:1-4,24 and scope document:17 only document this obligation; helper environment clearing at Run-I2Feasibility.ps1:69-73 occurs too late for the parent interpreter. Future designs are outside bc2562fd. Original V1 finding is not closed.
- Execution-readiness blocker: finalization exceptions can prevent RESULT or a complete stable manifest (Run-I2Feasibility.ps1:95-122). Final query launch at103 can fail before RESULT118; a guard remaining alive after96 may hold guard.jsonl open while121 hashes all files. Require best-effort stage-specific error recording and explicit partial evidence status; do not present unreadable/live files as a complete closed snapshot.
- Repaired in source: trusted template checks script/approval byte arrays before evaluating exactly those bytes; the binary digest is inside the bound harness; exact approval bytes are archived. Hash relations match. This closes the old self-check/reopen mechanics only conditional on the missing trusted startup chain.
- Repaired in source: guard alone creates a fresh GUID and retains successful nonzero StartTrace handle; no name-based stop exists. Timer starts before logging/receipt. Sampler failure cannot cancel creator ownership/deadline. No runtime cleanup guarantee is claimed when native calls block, StartTrace has not returned, or the guard abruptly disappears.
- Repaired in source: fixtures are created suspended in a private one-member kill-on-close Job through atomic JOB_LIST, limits read back, no handles inherited, exact process held, and exit/active0/total1 evidence required. Harness requires all3 records plus guard clean. Crash-time kill-on-close is a mechanism, not external runtime proof.
- Repaired in source: elevated output is only under newly protected C: root; exact C:/ProgramData parent owner/group/DACL pins are compared, and child owner/protected DACL/reparse state verified before writes. D: inputs remain untrusted. ProgramData pinned custody is a runtime precondition, not host state queried by this review.
- Saved parse evidence now records absolute inbox PowerShell5.1.26100.9444 and correct harness digest, with no parse errors. Existing layout record remains ABI/config-only and records zero trace/fixture/Job creations; no native API, privilege, counter or Windows scheduling behavior was validated.
- All21 files accounted for;20/20 manifest hash+size entries match with no missing/extras. Source/harness/template/binary pin relations match. Ten V1/V4 report/canonical copies are byte-identical to prior sealed artifacts; V4 export gap repaired. Saved compiler/binary binding is not independently reproduced source-to-binary attestation.
- Timing/loss/attribution remain feasibility-only. Guard schedules fixtures relative to its own start while sampler starts after receipt; align actual FILETIME/QPC/counter records during later offline analysis rather than assume perfect overlap. Missing/empty categories, blocking calls and timer delay do not prove full coverage. Success remains CAPTURE_COMPLETED_REQUIRES_OFFLINE_ANALYSIS with coverage_complete=false.
- Guest broker/guardian integration, production observer, service identities, host fallback, runtime compatibility and I1-I7 qualification remain incomplete/outside this delta. AI review is not owner/formal-reviewer authority. Prior sealed finding and scan remain intact.

### Scan Summary

| Field | Value |
| --- | --- |
| Scan outcome | completed |
| Reportable findings | 0 |
| Severity mix | none |
| Confidence mix | none |
| Coverage | partial |
| Validation mode | Generated scoped threat model plus fresh-context architecture review;14 canonical inventory items plus7 supporting artifacts;2 candidate validations and1 deferred attack-path assessment. |

Canonical artifacts: `scan-manifest.json`, `findings.json`, and `coverage.json`. This report is a deterministic projection of those files.

## Threat Model

# V2 I2 repair threat model

Scope is the immutable e72da101e036e4bd96c0bb230b89be91058c8857..bc2562fd9ebff705b06dbb4d90d49b06a64fe8d6 diff:21 new files in local_control_package_v2. Prior V1/guest/V4 code is unchanged and consulted only as necessary context. This is a prepared, unexecuted native feasibility candidate; I1-I7 OPEN, admission BLOCKED.

## Architecture and trust roots
Trusted-Entry.template.ps1 is explicitly data, not an executable privileged file. The proposed actual entry is fixed reviewed literal text passed through trusted -EncodedCommand to the absolute inbox Windows PowerShell5.1 interpreter, with its process environment cleaned BEFORE that interpreter starts. Template lines17-22 read untrusted script and approval bytes and compare them to fixed digests;28-29 evaluate the same script bytes in memory and pass the same approval bytes. Script digest is fixed; approval digest remains an unfilled placeholder until actual human approval. There is no concrete external launcher implementation in these three source files; its initialization must not be assumed.

Run-I2Feasibility.ps1:15-22 parses the verified approval bytes, requires administrator authority, reads candidate binary bytes and checks its embedded SHA256. It requires1GiB free, refuses root collision, rejects reparse parents, compares exact C:/ and C:/ProgramData owner/group/DACL pins, creates a protected Administrators-owned directory and checks exact DACL before writing (23-54). It saves the same binary/approval bytes in C:/ProgramData/ReBaseGuardP309-I2-Feasibility-v2. No elevated write to AU-writable D: is present. Explicit child environment is cleared and rebuilt before process start (64-74).

EtwCapture.cs:186-235 moves ETW creation into an independent guard. The guard generates a fresh GUID, accepts only successful StartTrace nonzero handle and starts a75-second timer before logging/receipt. Query/Stop require that handle and GUID; no name-based stop entrypoint exists (138-152,262-269). The sampler verifies the creation receipt and guard PID/creation time, reads counters and session stats, then publishes done/failure (236-260). The guard runs three fixed short fixtures, then owns final Stop and loss checks. Abrupt creator loss or blocked native APIs remain UNKNOWN; no other process adopts the session.

OwnedFixture.Run:375-427 creates a private unnamed Job with kill-on-close, one-process limit and256MiB process/job memory, checks limits, atomically attaches a suspended detached child through JOB_LIST with no handle inheritance, then resumes. It retains process identity/handle and requires exit0 plus active0/total1 before returning evidence. Job handle closure covers controller disappearance; this is a lifecycle control, not independent proof of actual cleanup after a crash. Harness requires all3 fixture records and guard-clean marker; failure preserves UNKNOWN (110-120).

## Attackers, resources and boundaries
Windows owner/admin and OS are trusted; a distinct local authenticated writer can modify D: checkout/source inputs (saved V1 exact-path ACL evidence). Candidate inputs are untrusted until byte hashes are checked. Trusted bootstrap literals, interpreter configuration and pre-start environment are new privilege boundaries; template comments do not enforce those external prerequisites. C: system-parent pinned ACLs and new protected directory are intended custody roots. No public ingress, service, arbitrary PID/command/session stop, guest execution, or production broker is added.

Protected resources include administrator execution integrity, unrelated ETW sessions/processes, bounded fixture resources, sensitive raw ETL/counter files and truthful approval/result provenance. Raw ETL can contain host process/image/module data; local retention and screened publication remain requirements. Approval reference is human workflow evidence, not an independent authentication service.

## Hypotheses and limits
Review whether clean interpreter startup is concretely provided, the exact verified bytes are evaluated, ACL pins are enforced before writing, creation handles cannot be confused with name collisions, fixture Job membership is atomic, native structure/flags/privilege paths are consistent, deadlines and failure outputs cannot overclaim. No dynamic API/ETW/counter/fixture success follows from saved layout/parse checks. Offline trace attribution, guest broker integration, runtime compatibility, service identity and admission remain outside this prepared scope. This reviewer executes no tests, native calls, host queries, URL fetches or workload. Generated model pending independent architecture reconciliation.

## Independent reconciliation and effective resources

A fresh-context worker independently reviewed both PowerShell files and the approval-scope document. The coordinator reviewed all C# and retained evidence, verified both script-control conclusions, and reconciled the supplied ACL context. Immutable tree and SECURITY.md resolver found no policy. No external URLs or reviewed code were executed. The original V1 finding remains a seeded unresolved end-to-end repair because the concrete trusted outer launcher is absent; this is not evidence that the correct same-byte template itself is exploitable.

| Consumer | Effective resource | Enforcement and limits |
| --- | --- | --- |
| Outer privileged startup | Required C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe with -NoProfile -NonInteractive -EncodedCommand | Caller must clean environment before CLR/engine load; only documented, no implementation in this diff. |
| ScriptBlock | D:\\ReBaseGuard-309\\workspace\\p309-local-vm-diagnostic-dev-20261016\\level4\\closure_proofs\\p5y_k5_cell309_p309_r2_hardening\\local_control_package_v2\\Run-I2Feasibility.ps1 | Trusted command hashes exact ReadAllBytes result and evaluates that same array; template script digest matches immutable blob. |
| Approval | D:\\ReBaseGuard-309\\records\\p309-i2-v2-human-approval.json | Trusted command digest still a placeholder; same verified bytes are validated and archived. No approval exists by implication. |
| Helper | D:\\ReBaseGuard-309\\records\\p309-local-control-package-preparation-20261016-01\\i2-repair-v2\\EtwCapture-v2.exe -> C:\\ProgramData\\ReBaseGuardP309-I2-Feasibility-v2\\EtwCapture.exe | Embedded binary digest, same-byte protected staging, absolute process path and cleared five-variable child environment. Build record binds source/binary/compiler; no independent binary rebuild/disassembly performed. |
| Evidence root | C:\\ProgramData\\ReBaseGuardP309-I2-Feasibility-v2 | Exact parent ACL pins, new protected root owner/DACL/reparse checks and CreateNew writes. Ordinary-user export to D: remains a later caller action; no elevated D: output. |
| ETW | Fixed name ReBaseGuard-P309-I2-Feasibility-v2, per-run new GUID, creator handle | Only creator can Stop its successful handle; other name queries are read-only. Native blockage or creator loss remain UNKNOWN. |
| Fixture | Protected EtwCapture.exe --fixture-child-approved | Per-fixture unnamed Job, atomic JOB_LIST assignment, no inheritance, retained process identity and empty-job evidence; no arbitrary input. |

Failure finalization is not guaranteed: Run-I2Feasibility.ps1:95-122 contains fallible query launch, output saving, JSON parsing, RESULT creation and all-file hashing without an independent fallback recorder. A guard left alive after timeout can retain writable/unstable evidence; no complete snapshot should be asserted. This is a concrete reliability/readiness gap, not established security exploitation. Same-byte fixes, handle-only session ownership, atomic fixture containment and corrected5.1 parse record are positive source evidence; none demonstrates native runtime success. All20 manifest entries and ten previous sealed-report copies match exact bytes. Prior scans are unchanged.


## Findings

### No findings

No reportable findings survived the canonical discovery, validation, and reportability gates.

## Reviewed Surfaces

| Surface | Risk Area | Outcome | Notes |
| --- | --- | --- | --- |
| Trusted bootstrap and elevated harness | not recorded | Needs follow-up | Same-byte script/approval repair and pinned binary validated statically; actual trusted pre-engine launcher absent, so original finding remains unclosed. |
| Failure result and manifest robustness | not recorded | Rejected | Suppressed as security vulnerability because no hostile protected-output writer or false admission is established. Concrete execution-readiness defect retained: fallible finally can omit RESULT or stable complete SHA256SUMS. |
| Creator-owned ETW and atomic fixture Jobs | not recorded | No issue found | All428 C# lines reviewed: x64 native structures, existing-token privilege restoration, successful creator handle/GUID ownership, timer, read-only queries, atomic fixture Job assignment/limits/identity/cleanup and conservative failure claims. Native execution untested. |
| All retained evidence and manifest bindings | not recorded | No issue found | All21 files reviewed.20/20 manifest entries match;10 copied prior canonical/report files identical to sealed originals. Correct5.1 parse evidence. No source-to-binary rebuild or native success inferred. Evidence: artifacts/01_context/static-artifact-checks.json |

## Open Questions And Follow Up

- Original csf_4a441982603758ecfe183ec2 repair cannot be closed end-to-end: concrete trusted external launcher with pre-interpreter environment cleaning and fixed command custody absent at bc2562fd.
  - Follow-up prompt: Review deferred unit v2-bootstrap-gap and close its stated proof gap. Surfaces: v2-bootstrap.
