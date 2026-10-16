# Scoped V4 platform-probe threat model

This model covers the immutable V4 guard, harness, evidence verdict and changed V3/V4 records at 4070e3d346a4530f6d01fecb9b86d80a2cddec02. It is not a repository-wide or production admission model. Source paths below are relative to level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_vm_controls/.

## Architecture and protected assets
The operator invokes detached_v4/Run-ApprovedDetached.ps1 with a local approval record and evidence directory. Lines 5–30 validate scope, two-launch count, a nonempty human reference, ordinary-user execution, host preconditions, digest pins, and a new approved directory. Lines 47–85 run deadline then guard-exit, stop the batch on first failed verdict, and observe a PID plus creation-time bound process handle. Approval authenticity is a human/workflow assumption; the JSON reference is not authenticated and the same user owns source and execution.

RuntimePreflight.ps1:14–38 checks all listed runtime files, path containment, reparse rejection, hashes and extras. OwnedVmDetached.cs:120–150 locks listed runtime files for read sharing and requires the QEMU executable and no extra files. These are integrity checks over a trusted local installation, not a sandbox against a writer with equivalent operator authority. Directory topology is not held immutable.

OwnedVmDetached.cs:85–89 fixes q35/WHPX, four vCPUs, 128 MiB, paused CPU, no disk/network/display/serial/monitor. Lines 295–326 create a private unnamed Job with kill-on-close, 768 MiB process/job commit and active-count one, then atomically attach a suspended process with no inherited handles. Lines 329–337 start an independent 14.5-second watchdog before resume. A minimal twelve-variable environment and child-scratch working/profile/cache paths are supplied (163–184,317–323). Job termination is scoped to the held private handle (269–277); no arbitrary PID-kill interface exists.

ProbeVerdict.ps1:10–56 binds limits, raw PID-buffer counts/identities, process generation, unique membership, expected image, exit codes and deadline timing. It returns a scoped result only and hardcodes formal_admission BLOCKED. Logs remain local same-user files; neither logs nor approval JSON establish an authenticated remote trust boundary. Historical records describe two paused probes and preserve V3's extra conhost failure; they do not prove guest boot, full hypervisor reclamation or I1–I7 closure.

## Actors, boundaries and assumptions
Assets are host process/resource safety, exact artifact execution, a bounded two-case workflow and honest scoped evidence. Trusted actors are the human operator, Windows kernel, pinned compiler/runtime and harness. Candidate external influence consists of malformed/corrupt evidence and filesystem/runtime inputs if supplied across an additional boundary. No network service, tenant, guest workload, arbitrary command, or privilege-grant consumer is introduced. A same-user attacker who can replace scripts, approval and runtime already has the execution authority used here; do not infer privilege escalation from that control. The native guard assumes the caller passed through the separately trusted approval workflow; its Main entry validates mode/fixed paths but not human consent (429–439).

## Hypotheses and limits
Review corruption/coercion or missing evidence causing false scoped pass; runtime/launch time-of-check-to-use races; process identity reuse; ownership/handle lifetime; deadline and guard-exit observation bounds; failure preservation and accidental claim promotion. These are review hypotheses, not confirmed findings. Fixed arguments, explicit application path, no shell, strict job limits, atomic membership, no inherited handles and identity-held external observation materially constrain the exposed surface. Windows scheduling is not a hard-real-time guarantee. Static source review cannot establish binary-source correspondence, runtime host state, authenticity of human consent, dynamic API behavior or full resource reclamation. No tests/probes are executed in this scan. I1–I7 remain OPEN; admission remains BLOCKED. Independent AI review provides no owner/formal-reviewer approval.

## Independent architecture reconciliation
A fresh-context source reviewer independently mapped the same immutable guard/harness/verdict scope. The main reviewer checked the material consumer locations against immutable Git source. No source evidence established an additional untrusted principal, production path or formal grant API. No tracked SECURITY.md or AGENTS.md exists in the immutable tree; the security-guidance resolver returned no policy. The independent review did not execute software or create a second scan.

| Consumer / workflow | Effective resource and recipients | Enforcing control and source |
| --- | --- | --- |
| Approval harness | Caller-selected JSON, copied as batch approval-used.json | Scope/fields/digests, not authenticated human lookup; Run-ApprovedDetached.ps1:2–7,32 |
| Harness launch | D:\\ReBaseGuard-309\\records\\p309-local-vm-detached-preparation-20261016-0850\\OwnedVmDetached-v4.exe, ordinary-user guard | Prelaunch SHA-256 and argument-list launch; Run-ApprovedDetached.ps1:14–18,55–61 |
| Script modules | RuntimePreflight.ps1 and ProbeVerdict.ps1 adjacent to invoked harness | Per-file digest before dot-source; Run-ApprovedDetached.ps1:19–26 |
| Runtime manifest | D:\\ReBaseGuard-309\\local-vm-feasibility\\candidate-v3.sha256, read by preflight/guard | Caller expected digest, containment/reparse/duplicate checks and C# held read handles; RuntimePreflight.ps1:14–38; OwnedVmDetached.cs:120–150 |
| QEMU executable | candidate-v3\\ucrt64\\bin\\qemu-system-x86_64.exe | Explicit application path, fixed arguments, suspended atomic private Job membership, no inherited handles; OwnedVmDetached.cs:144–148,305–326 |
| QEMU modules | candidate-v3\\ucrt64\\lib\\qemu via QEMU_MODULE_DIR | Rebuilt environment and runtime inventory controls; OwnedVmDetached.cs:147–148,174 |
| QEMU firmware/data | candidate-v3\\ucrt64\\share\\qemu via QEMU_DATA_DIR and -L | Fixed directory and quoted argument; OwnedVmDetached.cs:175,318–323 |
| Each probe scratch/profile/cache | approved-batch\\{deadline,guard-exit}\\child-scratch: cwd/TEMP/TMP; profile for USERPROFILE; profile\\AppData\\Roaming/Local for APPDATA/LOCALAPPDATA; program-data for ProgramData | Fresh case path and explicit environment, not ACL confinement; Run-ApprovedDetached.ps1:52–54; OwnedVmDetached.cs:163–184,317–323. Recorded batch root is D:\\ReBaseGuard-309\\records\\p309-local-vm-detached-v4-run-20261016-01 (detached_v4_result_20261016/approval-used.json:11). |
| Native imports / Windows loading | kernel32.dll from System32; child PATH runtime bin then Windows special-folder System32 | Declared native import search and minimal environment; OwnedVmDetached.cs:11,167–179; Run-ApprovedDetached.ps1:38. OS/WHPX integrity is outside runtime manifest; actual host folder not queried. |
| Deadline Job lifecycle | unnamed private Job; active limit 1; process/job commit each 805306368; flags 0x2308; 14500-ms target, 15000-ms verdict ceiling | Readback, atomic assignment, retained handle, watchdog; OwnedVmDetached.cs:258–277,295–337; ProbeVerdict.ps1:41–47 |
| Guard-exit lifecycle | same private Job; guard exit 86 and generation-held child's signaled handle | Kill-on-close and no inheritance, external observation; OwnedVmDetached.cs:352–354; Run-ApprovedDetached.ps1:69–81; ProbeVerdict.ps1:49–53. Source does not separately establish exclusive kill-on-close causality rather than watchdog or full partition reclamation. |

The guard's direct Main does not itself reject elevated execution or consume approval JSON; these are harness obligations (OwnedVmDetached.cs:429–439; Run-ApprovedDetached.ps1:8–9). Minimal environment redirection does not create a restricted token or filesystem sandbox. Preparation BINDINGS.json:50–52 records execution/review false at preparation time; the later result records two scoped actual launches. Static Git comparison found no detached_v4 source change from the result's source commit 57fac3a72783861b5cd72e84665ba68fafc1cc96 to this scan head. Preserve both historical artifacts.

---

## Saved Model Context

- Source: scan
- Scan: b89e3095-d57b-4ada-881c-c11b3fbdcc87
- Target: p309-local-vm-diagnostic-dev-20261016
- Revision: 4070e3d346a4530f6d01fecb9b86d80a2cddec02
- Snapshot: codex-security-snapshot/v1:sha256:1c8e4377ede409a40cd224c491a5f2e96b28207a80252850a9d7d0a2b08852b5
- Result status: completed
- Model origin: generated
- Model scope: level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_vm_controls/detached_v4, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_vm_controls/detached_v4_result_20261016, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_vm_controls/diagnostic_v3_result_20261016
- Scan scope: .
- Scan scope description: Independent AI static security review: no reportable security vulnerability found in this exact 49-file diff. This is not owner/formal reviewer approval, deployment acceptance or closure of I1–I7.
