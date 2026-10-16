# Security Review: p309-local-vm-diagnostic-dev-20261016

## Scope

Independent AI static review of all 47 added files in immutable 4070e3d..e72da101: one medium security finding and concrete execution-readiness blockers. This is not owner/formal reviewer approval; I1-I7 OPEN and admission BLOCKED.

- Scan mode: branch_diff
- Target kind: git_diff
- Target ID: target_sha256_aa743fba3b98454cc8ea65893dba04d7cd5f02ec0a77fd0165042868f408709b
- Revision range: 4070e3d346a4530f6d01fecb9b86d80a2cddec02...e72da101e036e4bd96c0bb230b89be91058c8857
- Snapshot digest: codex-security-snapshot/v1:sha256:2032d7fb6f900f7904972f82af5c89cc18b52571a2149c3a35dcdb1e432d8f0f
- Inventory strategy: diff
- Included paths: .
- Excluded paths: none
- Artifacts reviewed: level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/.gitattributes, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/ARCHITECTURE.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/DEPENDENCIES_AND_ORDER.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/I2_FEASIBILITY_REVIEW.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/SOURCE_AND_EVIDENCE_SHA256.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/STATUS.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/guest/owned_instance.py, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/guest/stop_guard.c, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/guest/test_owned_instance.py, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/I2_FINAL_BINARY_BINDING.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/LOCAL_RECORD_MANIFEST.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/etw-i2-final-layout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-adapter-tests-v2.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-adapter-tests.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-guardian-build-v2.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-guardian-build.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-inputs/download-record.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-inputs/manifest-verification.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-inputs/signature-status.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-inputs/signature.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-inputs/verification.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/guest-source-bindings-v2.sha256, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-drift/EXPLANATION.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-inventory-v2/guest-package-delta-final.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-inventory-v2/summary.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-inventory/error-preserved.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-stage-stable/archive.sha256, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-stage-stable/build-commands.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-stage-stable/compiler.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-stage-stable/glibc.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-stage-stable/interpreter-ldd.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-stage-stable/runtime-check.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-stage-stable/system-python-after.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/runtime-stage-stable/system-python-before.sha256, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/v4-independent-review/EXPORT_MANIFEST.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/v4-independent-review/coverage.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/v4-independent-review/report.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-evidence/windows-powershell-51-parse.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-scripts/audit_staged_runtime.py, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-scripts/build_guest_runtime_stable.sh, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-scripts/build_guest_runtime_stage.sh, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-scripts/final_guest_adapter_build.sh, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-scripts/guest_dependency_delta.py, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/preparation-scripts/investigate-runtime-drift.sh, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/EtwCapture.cs, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/I2_BINARY_BINDING.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/Run-I2Feasibility.ps1

Limitations and exclusions:
- Execution blocker: the elevated script is writable by Authenticated Users; its self-hash cannot secure loading. Saved exact-path ACL evidence is retained at artifacts/01_context/supplied-execution-path-acls.json. No compromise or actual run is claimed.
- Execution blocker: fixed-name/GUID watchdog and emergency recovery can stop a matching session never created by this run after the prequery/StartTrace collision window. captureStarted means dispatch, not successful creation (Run-I2Feasibility.ps1:85-96,111-115; EtwCapture.cs:157-164,242-246). Require successful per-run creation ownership and held-handle-only stop. Suppressed as a security finding because untrusted session-creation authority is not established.
- Execution blocker: owned_helpers_exited excludes fixture descendants. The fixture handle is held only by the controller; controller termination loses the independent ability to prove child exit, while watchdog only stops ETW (EtwCapture.cs:133-146,225-248; Run-I2Feasibility.ps1:123-129). Require independent descendant containment/receipt, or preserve UNKNOWN rather than a complete helper-exit claim. Fixed200-ms child limits ordinary impact; no attacker-controlled workload is present.
- Parent custody prerequisite remains unenforced: reparse-only ancestor checks and child protected DACL/owner checks do not prove non-writable ancestors or prevent replacement races (Run-I2Feasibility.ps1:20-27,57-64). Supplied D: ancestor ACLs permit Authenticated Users Modify. Protect or hold the relevant topology before elevated loading/archive access; child protection alone is insufficient evidence of stable custody.
- Approval human_message_reference is nonempty workflow text, not authenticated consent; approval-used.json is recopied from the original mutable path after parsing, so it need not preserve the exact parsed bytes. Fix the evidence binding before treating it as the record of what was approved (Run-I2Feasibility.ps1:10-15,62). No separate hostile approval service is exposed.
- PowerShell proof mismatch: windows-powershell-51-parse.json records version7.6.5 and syntax/build-only; it does not validate Windows PowerShell5.1. EtwCapture layout record proves only saved layout/config assertions, not native execution, token rights or counter availability.
- Timing/loss evidence remains feasibility-only: stopwatch checks occur after potentially blocking ETW/counter calls, watchdog is a75-second scheduled process, and empty/missing Hyper-V categories cannot establish coverage. Three loss counters are checked, but no ETL offline analysis, precise fixture timing acceptance or full observer result exists. Preserve coverage_complete=false and UNKNOWN/failure when evidence is missing.
- Guest cgroup/pidfd adapter and guardian are unintegrated primitives; no root broker serialization, launch authorization, generation lifecycle/ready handshake, service or host fallback is delivered. Passing mocked tests and compilation do not establish runtime safety or deployability.
- All46 source/evidence manifest entries match immutable Git hashes and sizes; no extras/missing entries. Binding source hash matches EtwCapture.cs. Local external binary/runtime/image manifests are retained claims, not independently reproduced builds. Signed-image records mean downloaded/verified, not booted. Dependency gaps and historical runtime drift remain preserved.
- V4 exported report/coverage hashes match. EXPORT_MANIFEST also names scan-manifest.json, findings.json and threatmodel.md that are not copied into this Git package; original sealed scan remains the canonical source. Its prior no-findings conclusion does not cover this new diff.
- Full repository, third-party/OS internals, actual binary equivalence, deployment ACL assurance and execution acceptance are outside this static review. Measured token usage is unavailable until completion metadata.

### Scan Summary

| Field | Value |
| --- | --- |
| Scan outcome | completed |
| Reportable findings | 1 |
| Severity mix | medium: 1 |
| Confidence mix | high: 1 |
| Coverage | complete |
| Validation mode | Generated scoped threat model, fresh-context independent architecture review, 27 canonical inventory items plus 20 supporting artifacts, three candidate validations and one reportable attack path. |

Canonical artifacts: `scan-manifest.json`, `findings.json`, and `coverage.json`. This report is a deterministic projection of those files.

## Threat Model

# Local control candidate threat model

Scope: immutable 4070e3d346a4530f6d01fecb9b86d80a2cddec02..e72da101e036e4bd96c0bb230b89be91058c8857, local_control_package_v1 only. Paths below are relative to level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1. This is unexecuted development source, not a deployment or admission assessment.

## Architecture, assets and authority
windows/Run-I2Feasibility.ps1:9–18 consumes a local human approval record, hash-pinned executable and harness, and requires an elevated administrator token. Lines 20–64 reject existing destinations/reparse ancestry, atomically create protected directories with Administrators owner, SYSTEM/Administrators FullControl and invoking user ReadAndExecute, then copy and rehash the executable. The roots are C:\ProgramData\ReBaseGuardP309-I2-Feasibility-v1 and D:\ReBaseGuard-309\records\p309-i2-native-capture-v1. Existing ancestor ACLs are not modified or established by these checks; trusted parent custody is a prerequisite. The owner/admin is an explicit trust root; approval JSON fields are workflow evidence, not cryptographic human authentication.

windows/EtwCapture.cs:19–93 defines x64 ETW structures and fixed system logger settings: fixed Name/Owner, 64 KiB buffers, 64–256 buffers, 256 MiB sequential ETL, flags 0x77. Capture enables existing SeSystemProfilePrivilege only on its process token and restores it (43–68). Capture creates controller/counter records, starts the session, samples three Hyper-V categories and runs three fixed 200-ms owned children before native stop (167–223). The watchdog is a separate elevated helper using fixed-name/GUID queries and stop after 75 seconds (225–248). No arbitrary command, PID-kill or supplied session name exists, but fixed Name/GUID is not a per-run creation identity. Outputs remain protected local evidence and coverage_complete=false/BLOCKED (Run-I2Feasibility.ps1:129).

The guest library is not exposed by a service or broker. guest/owned_instance.py:123–174 accepts an internal root-broker receipt, validates manager and /proc generation, holds pidfd and cgroup directory/kill FDs, and rechecks membership. request_stop writes only the held kill FD after latching; cleanup separately requires matching invocation, pidfd exit, empty unfrozen cgroup and no manager job (191–242). guest/stop_guard.c:51–118 is a root guardian receiving a read heartbeat pipe and fixed cgroup2 kill FD; it stops on EOF/error/3-second lease expiry/120-second development idle limit/parent death. Broker serialization, launch/stop races, deployment ACLs and host fallback are explicitly unfinished (ARCHITECTURE.md:16–20).

## Actors, boundaries, objectives and assumptions
Protected assets are elevated executable/evidence integrity, unrelated ETW sessions and processes, host resource bounds, owned guest process generation and truthful provenance. Windows owner/admin, guest root/kernel, pinned compiler and signed supply inputs are trusted. Conditional attackers can influence files or protocol inputs only if an actual separate less-trusted actor is established; no production broker/observer or public ingress is present. Ordinary local users are not newly enrolled as service principals. Do not invent privilege separation between same-authority admin actors or count local build facts as guest execution.

Review session creation-to-cleanup identity, elevated path/ACL/collision behavior, native layout and token restoration, watchdog/helper lifecycle, timing/loss/record failures, guest PID/cgroup generation, heartbeat freshness, runtime manifests and build provenance. Approval, capture, source hash, and formal admission are separate claims. No reviewed result grants deployment authority. I1–I7 remain OPEN; BLOCKED remains mandatory.

## Known limits and hypotheses
Static review cannot reproduce ETW return values, counter presence, native privilege requirements, guest systemd/cgroup semantics or build-to-binary attestation. A concrete source-level readiness concern is that watchdog/emergency cleanup use a fixed name/GUID without a receipt proving this invocation successfully created the session. This is an ownership/reliability concern under the trusted-admin model, not yet a reportable attacker boundary violation. No runtime tests, native APIs, fixtures, traces, counter sampling, VM/services, host queries or external URL retrieval are permitted in this review.

## Independent architecture reconciliation and supplied ACL correction

A fresh-context independent reviewer mapped the same source without executing it or fetching URLs. No SECURITY.md was found in the immutable tree. The initial model's trusted-parent and trusted-harness assumptions are not satisfied by the supplied deployment evidence: a later saved ACL record for the exact Run-I2Feasibility.ps1 and checkout directory contains Authenticated Users Modify, (A;ID;0x1301bf;;;AU). This is evidence supplied by the engineering coordinator and read from a saved file; this reviewer did not query host ACLs. A separate sandbox-SID write ACE on the task CWD was also supplied, but is not generalized to arbitrary paths. A local authenticated writer is therefore a distinct lower-trust actor for the proposed elevated script load. The self-hash is actually line14 (line13 compares the binary pin). The protected binary copy does not cover already executing PowerShell. This correction supersedes the early trusted-operator-only assumption for script integrity; Windows owner/admin and guest root/kernel remain trust roots.

| Resource / consumer | Effective name and custody | Control and limit |
| --- | --- | --- |
| Elevated harness | D:\\ReBaseGuard-309\\workspace\\p309-local-vm-diagnostic-dev-20261016\\level4\\closure_proofs\\p5y_k5_cell309_p309_r2_hardening\\local_control_package_v1\\windows\\Run-I2Feasibility.ps1 | Exact supplied DACL permits Authenticated Users Modify; self-verification is inside the privileged script, not before load. |
| Binary and approval | Fixed EtwCapture-i2-final.exe under D: records; adjacent I2_BINARY_BINDING.json; caller-selected approval JSON | Pins, copy and rehash; human reference is not authenticated consent. No trusted external script bootstrap is provided. |
| Capture/evidence | C:\\ProgramData\\ReBaseGuardP309-I2-Feasibility-v1, archive D:\\ReBaseGuard-309\\records\\p309-i2-native-capture-v1 | Atomic protected child DACL, collision and reparse checks; ancestors are not proven non-writable or held against replacement. |
| ETW session | ReBaseGuard-P309-I2-Feasibility-v1, GUID b65ec272-436b-45e5-a4e3-87fddbc73a80 | Controller holds creation handle; watchdog/recovery use fixed-name lookup, not a per-run creation receipt. |
| Local raw evidence | capture.etl, controller.jsonl, hypervisor-raw.jsonl, watchdog records | May contain process/image/module/command-line detail; retain protected locally and publish only screened summaries. |
| Guest stop authority | fixed p309-dev-owned-check.service cgroup, held pidfd/kill FD, FIFO heartbeat | Root broker, generation serialization, guardian-ready handshake, deployment and fallback remain future work. |

Native structure sizes/offset assertions, fixed 0x77 flags, existing-token SeSystemProfilePrivilege enable/restore and loss checks were statically reviewed; no native ABI/privilege/counter success is established by this review. Windows timers are not real-time guarantees. The existing layout record is layout-only, and the file named windows-powershell-51-parse.json records PowerShell7.6.5, not5.1. The private runtime build and signed-image records do not establish installation, guest compatibility or actual VM execution. All I1–I7 remain OPEN and formal admission BLOCKED.


## Findings

| Finding | Severity | Confidence | Detailed write-up |
| --- | --- | --- | --- |
| [Launching the writable harness elevated allows local users to execute administrator commands](#finding-1) | medium | high | inline below |

### Confidence Scale

| Label | Meaning |
| --- | --- |
| high | Direct evidence supports the finding with no material unresolved blocker. |
| medium | Evidence supports a plausible issue, but material runtime or reachability proof remains. |
| low | Evidence is incomplete and the item is retained only for explicit follow-up. |

<a id="finding-1"></a>

### [1] Launching the writable harness elevated allows local users to execute administrator commands

| Field | Value |
| --- | --- |
| Severity | medium |
| Confidence | high |
| Confidence rationale | Immutable source confirms evaluation-before-self-check; saved ACL evidence for the exact script confirms the distinct lower-trust writer. No dynamic exploit was performed. |
| Category | Privileged code loading from a less-trusted writable file |
| CWE | CWE-829 |
| Affected lines | level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/Run-I2Feasibility.ps1:1-17, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/Run-I2Feasibility.ps1:13-14 |

#### Summary

An authenticated local user can replace the prepared Run-I2Feasibility.ps1, whose saved exact-path DACL grants Authenticated Users Modify. If the operator then invokes that file in elevated PowerShell, substituted statements execute before or instead of its self-hash check. The later protected EtwCapture.exe copy cannot authenticate the already executing harness.

#### Root Cause

The integrity boundary is placed inside the object it is meant to authenticate. The operator passes a mutable path to elevated PowerShell; PowerShell loads and starts the script before line14 compares its path hash to the approval record. The exact script is writable by Authenticated Users, so a distinct lower-trust writer can change the code that performs the check. Adjacent pins and later protected binary staging do not establish trusted custody of the script bytes before evaluation.

**Self-hash runs inside the loaded script** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/Run-I2Feasibility.ps1:11-15`

The editable script itself chooses whether to compare its on-disk bytes; an Authenticated Users writer can remove this block or prepend statements, which PowerShell evaluates before the supposed integrity gate.

```powershell
if($approval.scope -cne 'P309_I2_SINGLE_NATIVE_FEASIBILITY_V1' -or
   $approval.capture_count -ne 1 -or
   $approval.binary_sha256 -cne $pins.binary_sha256 -or
   $approval.harness_sha256 -cne (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant() -or
   [string]::IsNullOrWhiteSpace($approval.human_message_reference)) {throw 'approval binding refused'}
```

**Entrypoint expects administrator authority** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/Run-I2Feasibility.ps1:16-17`

The intended invocation already has an administrator token. Attacker-provided script statements inherit that authority; this check cannot authenticate who wrote them.

```powershell
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(-not ([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {throw 'explicit UAC-approved elevated entry required'}
```

#### Validation

The saved script DACL contains (A;ID;0x1301bf;;;AU), allowing authenticated writers. The source puts its own digest check inside the intended elevated script. No external protected loader is included in this diff.

Validation method: Static immutable-source trace and supplied exact-path ACL record

**Self-hash runs inside the loaded script** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/Run-I2Feasibility.ps1:11-15`

The editable script itself chooses whether to compare its on-disk bytes; an Authenticated Users writer can remove this block or prepend statements, which PowerShell evaluates before the supposed integrity gate.

```powershell
if($approval.scope -cne 'P309_I2_SINGLE_NATIVE_FEASIBILITY_V1' -or
   $approval.capture_count -ne 1 -or
   $approval.binary_sha256 -cne $pins.binary_sha256 -or
   $approval.harness_sha256 -cne (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant() -or
   [string]::IsNullOrWhiteSpace($approval.human_message_reference)) {throw 'approval binding refused'}
```

**Entrypoint expects administrator authority** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/Run-I2Feasibility.ps1:16-17`

The intended invocation already has an administrator token. Attacker-provided script statements inherit that authority; this check cannot authenticate who wrote them.

```powershell
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(-not ([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {throw 'explicit UAC-approved elevated entry required'}
```

Assertions:
- The script self-check occurs after PowerShell begins evaluating the supplied file.
- The saved ACL evidence applies to the precise executable script path, not merely its working directory.
- Protected binary copy cannot retroactively protect the script entrypoint.

Limitations:
- No live write, elevation or exploit performed.
- ACL evidence was read from a supplied saved record, not independently queried.
- Requires the human operator to launch the prepared path elevated.

#### Dataflow

Authenticated Users file write -\> elevated PowerShell file load -\> attacker statements -\> administrator actions

- **Source:** Mutable Run-I2Feasibility.ps1 bytes

- **Sink:** Elevated PowerShell evaluation

- **Outcome:** Arbitrary administrator command execution

**Self-hash runs inside the loaded script** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/Run-I2Feasibility.ps1:11-15`

The editable script itself chooses whether to compare its on-disk bytes; an Authenticated Users writer can remove this block or prepend statements, which PowerShell evaluates before the supposed integrity gate.

```powershell
if($approval.scope -cne 'P309_I2_SINGLE_NATIVE_FEASIBILITY_V1' -or
   $approval.capture_count -ne 1 -or
   $approval.binary_sha256 -cne $pins.binary_sha256 -or
   $approval.harness_sha256 -cne (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant() -or
   [string]::IsNullOrWhiteSpace($approval.human_message_reference)) {throw 'approval binding refused'}
```

**Entrypoint expects administrator authority** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1/windows/Run-I2Feasibility.ps1:16-17`

The intended invocation already has an administrator token. Attacker-provided script statements inherit that authority; this check cannot authenticate who wrote them.

```powershell
$identity=[Security.Principal.WindowsIdentity]::GetCurrent()
if(-not ([Security.Principal.WindowsPrincipal]::new($identity)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {throw 'explicit UAC-approved elevated entry required'}
```

#### Reachability

Exact saved file ACL permits the write; a human elevated invocation remains necessary. No public ingress or installed service is introduced.

- **Attacker:** Local authenticated user distinct from trusted owner/admin

- **Entry point:** Prepared elevated script path

- **Outcome:** Administrator authority for substituted script

#### Severity

**Medium** — Arbitrary administrator code execution has high impact. Exploitation requires local write access and an administrator launching this unexecuted candidate, so likelihood is medium. No actual elevated run or compromise occurred.

A trusted bootstrap verifying exact bytes before evaluation and executing the same bytes with trusted interpreter configuration and fixed pins would remove this path. An unattended privileged launcher would increase likelihood.

Impact assessment:
- **Level:** high
- **Why:** Substituted PowerShell can perform arbitrary administrator actions.

Likelihood assessment:
- **Level:** medium
- **Why:** Local access plus operator elevated invocation are required; the candidate remains unexecuted and blocked.

#### Remediation

Use a separately trusted bootstrap to read script bytes, compare them to an immutable approved digest before any evaluation, then execute those exact verified bytes without reopening a mutable path. Bind adjacent pins in the trusted bootstrap or the verified payload. Protect the executable/evidence ancestor custody, use a trusted absolute interpreter with profiles disabled, and do not rely on self-hashing or current-directory ownership.

Tests:
- In an isolated authorized test, change the mutable input before verification and ensure no payload statement executes.
- Change the source path after verification and prove only the verified in-memory bytes execute.
- Reject untrusted parent/reparse replacement and altered pins; retain refusal evidence.

Preventive controls:
- Keep all privilege-granting bootstrap bytes and fixed digests outside lower-trust writable custody.

## Reviewed Surfaces

| Surface | Risk Area | Outcome | Notes |
| --- | --- | --- | --- |
| Fixed-name ETW cleanup ownership candidate | not recorded | Rejected | Rejected only as a security vulnerability: no lower-trust session-creation authority established. Confirmed execution-readiness defect remains: no successful per-run creation receipt and Stop(0) can adopt a matching competing session. |
| Fixture descendant cleanup accounting candidate | not recorded | Rejected | Rejected only as a security vulnerability: fixture is fixed200-ms work with no attacker input. Confirmed readiness/evidence defect remains: external owned_helpers_exited omits descendants after controller failure. |
| Windows elevated I2 harness and ETW capture | not recorded | Reported | All source reviewed. Elevated writable-script finding; fixed-name cleanup and fixture descendant evidence defects retained as readiness blockers. Token, ABI, loss, deadlines, ACL/collision and evidence claims inspected. Evidence: artifacts/01_context/supplied-execution-path-acls.json |
| Guest owned-instance and guardian primitives | not recorded | No issue found | All three files reviewed, generation/pidfd/cgroup/FIFO/timeout/cleanup paths inspected. Future root broker and deployment remain absent and cannot be accepted. |
| Build scripts and all retained provenance records | not recorded | No issue found | Six preparation scripts plus all changed records reviewed.47 files total,27 canonical items.46/46 manifest hashes and sizes match. PowerShell version filename mismatch and partial prior-review export recorded. Evidence: artifacts/01_context/static-artifact-checks.json |
