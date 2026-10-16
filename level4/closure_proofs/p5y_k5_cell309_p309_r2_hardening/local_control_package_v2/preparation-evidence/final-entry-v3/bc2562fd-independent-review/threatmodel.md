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

---

## Saved Model Context

- Source: scan
- Scan: cf137369-9cd1-4958-a9ff-0cbde3d44003
- Target: p309-local-vm-diagnostic-dev-20261016
- Revision: bc2562fd9ebff705b06dbb4d90d49b06a64fe8d6
- Snapshot: codex-security-snapshot/v1:sha256:eb88b136e0fdb3f2069a00f7f671059274086518d5474350ad6cf40d578f5142
- Result status: completed
- Model origin: generated
- Model scope: level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2
- Scan scope: .
- Scan scope description: Independent static re-review of all21 new V2 files. No newly confirmed reportable vulnerability; original finding csf_4a441982603758ecfe183ec2 remains unclosed because the trusted pre-interpreter launcher is absent. Execution blocked; I1-I7 OPEN; no formal admission.
