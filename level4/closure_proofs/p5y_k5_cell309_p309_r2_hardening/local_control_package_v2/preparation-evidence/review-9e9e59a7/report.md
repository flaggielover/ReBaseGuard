# Security Review: p309-local-vm-diagnostic-dev-20261016

## Scope

Completed independent static security diff review of all 27 changed files in bc2562fd..9e9e59a7, plus supporting unchanged ETW/lifecycle and saved ACL context. One medium build-custody finding; no execution or formal approval.

- Scan mode: branch_diff
- Target kind: git_diff
- Target ID: target_sha256_aa743fba3b98454cc8ea65893dba04d7cd5f02ec0a77fd0165042868f408709b
- Revision range: bc2562fd9ebff705b06dbb4d90d49b06a64fe8d6...9e9e59a7dd0be518231c6c92c4ae14dcd329c6d6
- Snapshot digest: codex-security-snapshot/v1:sha256:ce77da722f7e960a2d320fc39241cbfa59522b687e3b75320f0643fccf9fa389
- Inventory strategy: diff
- Included paths: .
- Excluded paths: none
- Artifacts reviewed: artifacts/01_context/static-artifact-checks.json, artifacts/02_review/independent-reconciliation.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/FINAL_BINDINGS.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Launch-Approved.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/NativeEntry.c, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/REPAIR_AND_APPROVAL_SCOPE.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Run-I2Feasibility.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/SOURCE_AND_EVIDENCE_SHA256.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/TestNativeEntry.c, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Trusted-Entry.template.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/fetch_guest_debs.py, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/BINDINGS.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/VERIFIED_INPUTS.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/bc2562fd-SOURCE_AND_EVIDENCE_SHA256.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/bc2562fd-independent-review/coverage.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/bc2562fd-independent-review/findings.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/bc2562fd-independent-review/report.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/bc2562fd-independent-review/scan-manifest.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/bc2562fd-independent-review/threatmodel.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/compile.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/final-winps51-check.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/guest-dependency-plan.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/pe-inspection.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/readonly-entry-pin-result.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/unit-ACTUAL_RESULT.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/unit-BINDINGS.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/unit-NativeEntry-included.c, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/final-entry-v3/unit-TestNativeEntry.c

Limitations and exclusions:
- I1-I7 remain OPEN and admission BLOCKED; AI technical review is not owner/formal reviewer acceptance.
- Production native entry remains unexecuted. Saved ten codec/hash known-answer checks and read-only pin check are narrow records, not end-to-end evidence.
- Original finding csf_4a441982603758ecfe183ec2 and all old scans remain sealed unchanged; source-level control repair does not update their formal state.
- Pin sharing/reparse snapshot assumptions were examined; no concrete metadata-race bypass established. Native/launcher timeout may leave controller alive and means UNKNOWN/no automatic retry.
- RESULT can precede a late evidence-write failure; final process exit and EVIDENCE_FAILURE/manifest completeness must be interpreted together.
- Offline 19 signed packages remain inputs only; guest installation, broker integration, runtime performance/timing/loss and deployment are not established.
- Current protected-build remediation is only planned outside this revision.

### Scan Summary

| Field | Value |
| --- | --- |
| Scan outcome | completed |
| Reportable findings | 1 |
| Severity mix | medium: 1 |
| Confidence mix | high: 1 |
| Coverage | complete |
| Validation mode | Scoped threat model; full diff inventory; independent fresh-context native review; three candidate validations and one reportable attack path. |

Canonical artifacts: `scan-manifest.json`, `findings.json`, and `coverage.json`. This report is a deterministic projection of those files.

## Threat Model

# Native-entry and evidence-finalization repair threat model

This generated per-scan model covers immutable bc2562fd9ebff705b06dbb4d90d49b06a64fe8d6..9e9e59a7dd0be518231c6c92c4ae14dcd329c6d6:27 changed files in local_control_package_v2. Earlier V1/V2/V4 scans remain sealed. Unchanged EtwCapture.cs is supporting context for lifecycle and cleanup only. All workflows remain unexecuted candidates, I1-I7 OPEN/admission BLOCKED.

## Architecture and resources
Launch-Approved.ps1 is a normal-user launcher, not a privileged script. The trusted tool caller is required to hash the launcher against an independent reviewed constant and execute those same in-memory bytes (3-5). It rejects already-elevated invocation, compiles an embedded file-pin helper, opens ancestor paths root-first with read sharing only/no write or delete sharing and reparse-point flags, then holds a single-link leaf read handle and hashes it (28-56). The fixed native entry is D:/ReBaseGuard-309/records/p309-local-control-package-preparation-20261016-01/i2-native-entry-v3-b4/NativeEntry.exe. It calls ShellExecute runas on that exact path with a64-hex approval digest, fixed System32 cwd, and retains pins through the normal native process wait (61-71). ReadOnlyPreflight returns before any elevation.

NativeEntry.c is a small native PE, built with no CRT/default libraries and embedded requireAdministrator manifest. It has only kernel32 static imports according to saved PE inspection; dynamic advapi32 and bcrypt are explicitly System32. It validates the argument and elevated token, reads a<=16384-byte template as data, hashes it against an embedded digest, substitutes exactly one marker with the64-hex approval digest, converts strict UTF8 to UTF16, base64 encodes those same bytes, and CreateProcessW launches the absolute inbox WinPS5.1 with -NoProfile -NonInteractive -EncodedCommand, no handle inheritance, System32 cwd and an explicit six-variable Unicode environment (58-90). This supplies the previously missing pre-CLR environment boundary; it does not rely on ShellExecute environment inheritance. The native240-second timeout does not kill the controller and reports nonzero status.

The bound template hashes the harness and approval bytes before evaluating the same in-memory harness and passing the same approval byte array. The harness retains the prior protected C:/ProgramData root and parent ACL pins, embedded ETW binary digest, same-byte staging and cleared helper environments. Unchanged ETW guard uses fresh GUID/successful creation handle and75-second timer; no name-based stop exists. Fixtures remain atomically attached suspended to private one-process256MiB kill-on-close Jobs with retained identity and empty-job receipts.

Run-I2Feasibility.ps1:95-144 now collects separate cleanup/evidence errors, tries final query/output/fixture/result stages independently, hashes evidence only when all helpers exited, writes MANIFEST_INCOMPLETE for live helpers and attempts EVIDENCE_FAILURE on persistence errors. Media failure can still prevent files; the outer retained process exit is part of failure interpretation. RESULT can precede later manifest errors and must be considered together with EVIDENCE_FAILURE and exit status.

fetch_guest_debs.py is preparation tooling: it verifies retained APT InRelease signatures against the existing OS keyring, validates exact Packages hash/size, selects19 exact plan versions, downloads bounded-by-manifest package identities and verifies size/hash. It does not install or boot a guest. Signed package metadata/OS keyring are trust roots; saved records remain input preparation only.

## Actors and trust boundaries
Trusted actors are the approving human, trusted ordinary-user tool invocation/constants, Windows OS/admin, installed compilers/keyring and protected system directories. Lower-trust authenticated users can write D: inputs under the supplied ACL facts. The security objective is preventing those writers from substituting bytes between hash checks and privileged evaluation, while not confusing another session/process with this invocation. Pin metadata/reparse and native image loading semantics are OS assumptions to examine, not guarantees created by comments. Privileged/native/PowerShell timeouts produce UNKNOWN; no automatic escalation, name adoption or retry is authorized.

Assets include administrator execution integrity, approved input identity, unrelated sessions/processes, sensitive ETL/counter data and accurate failure evidence. No public ingress, production broker, installed service, arbitrary command interface, guest run or formal grant is added. Raw ETL stays local; copy/export is ordinary-user evidence handling, not trusted executable custody.

## Review limits
Only static immutable source and saved evidence are reviewed; no reviewed code/tests/native APIs/host queries/UAC/trace/counters/fixture/Job/VM/services/URLs are executed. Build and known-answer records prove only their recorded scope. The launcher read-only pin test does not demonstrate adversarial race resistance or a successful elevated launch; codec/hash checks do not execute production Entry. Fresh-context independent native review is complete and reconciled. Prior bootstrap/finalization gaps must be evaluated against this new implemented chain, preserving residual assumptions and keeping I1-I7 OPEN/BLOCKED.

## Independent reconciliation and final disposition

All 27 changed files and 22 authoritative inventory items are closed. Fresh-context reviewer /root/security_preflight/v3_native_review examined native codecs, bounds, dynamic imports, environment, builder and launcher interfaces. No additional concrete native memory or codec vulnerability was established. The one reportable issue is build-time custody: a separate AU writer can affect compiler inputs/object/output before the resulting binary digest becomes the elevation pin. Post-build source hashes are not a record of the bytes actually consumed. Parent explicitly confirmed that no further build-custody evidence exists. The trusted Windows owner and protected OS/toolchain are not adversaries. A planned protected rebuild is outside this immutable revision.

The prior pre-CLR startup and staged-finalization source omissions are implemented in this revision; this is conditional source-level closure, not a change to old sealed finding state or formal acceptance. Read-only pin records do not prove all reparse metadata races; no concrete bypass was established. Native/launcher timeouts can leave the controller alive and mean UNKNOWN, requiring retained process identity and no automatic retry. GetFileSize's low DWORD is a file-size-validation limitation, but the only consumed prefix still requires the fixed template hash. These limits do not substitute for native acceptance evidence after authorization. I1-I7 remain OPEN, admission BLOCKED.

Static artifact checks: 43 manifest entries match size/hash; six source bindings and native/template/harness pin relationships match; five prior report exports are byte-identical; test-native copy differs only in template digest. This establishes consistency, not source-to-binary provenance. Supplemental receipts: artifacts/01_context/static-artifact-checks.json and artifacts/02_review/independent-reconciliation.json.


## Findings

| Finding | Severity | Confidence | Detailed write-up |
| --- | --- | --- | --- |
| [Build-time substitution can become the approved elevated binary](#finding-1) | medium | high | inline below |

### Confidence Scale

| Label | Meaning |
| --- | --- |
| high | Direct evidence supports the finding with no material unresolved blocker. |
| medium | Evidence supports a plausible issue, but material runtime or reachability proof remains. |
| low | Evidence is incomplete and the item is retained only for explicit follow-up. |

<a id="finding-1"></a>

### [1] Build-time substitution can become the approved elevated binary

| Field | Value |
| --- | --- |
| Severity | medium |
| Confidence | high |
| Confidence rationale | Source shows path-based compilation and linking before post-build hashes. The supplied ACL premise establishes a distinct lower-trust writer and parent confirms no additional custody evidence. |
| Category | untrusted-code-inclusion |
| CWE | CWE-829 |
| Affected lines | level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:2-5, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:9-17, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Launch-Approved.ps1:55-64, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/FINAL_BINDINGS.json:29-30 |

#### Summary

A separate local writer with the supplied AU write access can change NativeEntry.c before compilation or NativeEntry.obj before linking, restore the reviewed source before the builder hashes it, and cause the substituted executable's digest to become the launcher pin. A later approved RunAs would execute those bytes as administrator. The current binary is not alleged to be malicious; the defect is the missing binding between reviewed source and compiler-consumed bytes.

#### Root Cause

The required invariant is that an executable approved for administrator execution derives from the exact reviewed inputs. The builder places source, intermediate and output paths across a lower-trust write boundary, invokes cl.exe and link.exe without protecting their consumed bytes, and computes source/output hashes afterwards. A restored source file can match review while the produced output contains different code. The launcher faithfully pins that output, so its strong runtime byte checks do not repair the earlier loss of provenance.

**Source and output are ordinary D: paths** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:2-5`

The source and build directory are in the supplied AU-writable hierarchy. Ordinary directory creation supplies no protected build custody before compiler consumption.

```powershell
$source='D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v2\NativeEntry.c'
$out='D:\ReBaseGuard-309\records\p309-local-control-package-preparation-20261016-01\i2-native-entry-v3-b4'
if(Test-Path -LiteralPath $out) {throw 'output collision'}
New-Item -ItemType Directory -Path $out | Out-Null
```

**Compiler reads the source by mutable path** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:9-10`

cl.exe consumes the current source path and writes NativeEntry.obj. No reviewed input hash or held immutable input handle binds what the compiler reads.

```powershell
$argsCompile=@('/nologo','/c','/GS-','/O1','/Oi-','/Zl','/D_WIN32_WINNT=0x0602',('/I'+'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\include'),('/I'+$sdk+'\Include\10.0.26100.0\ucrt'),('/I'+$sdk+'\Include\10.0.26100.0\um'),('/I'+$sdk+'\Include\10.0.26100.0\shared'),('/Fo'+$out+'\NativeEntry.obj'),$source)
& $cl @argsCompile 2>&1 | Tee-Object -FilePath (Join-Path $out 'compile.txt')
```

**Linker consumes the mutable intermediate** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:12-13`

link.exe reopens NativeEntry.obj and creates the privileged executable. A separate writer can substitute the intermediate before this read.

```powershell
$argsLink=@('/NOLOGO','/NODEFAULTLIB','/ENTRY:Entry','/SUBSYSTEM:WINDOWS','/DYNAMICBASE','/NXCOMPAT','/MANIFEST:EMBED',"/MANIFESTUAC:level='requireAdministrator' uiAccess='false'",('/OUT:'+$out+'\NativeEntry.exe'),($out+'\NativeEntry.obj'),($sdk+'\Lib\10.0.26100.0\um\x64\kernel32.lib'))
& $link @argsLink 2>&1 | Tee-Object -FilePath (Join-Path $out 'link.txt')
```

**Hashes are computed after compiler and linker use** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:17`

BINDINGS hashes the current source and executable only after use. Restoring reviewed source before this point allows a clean source hash to accompany a substituted binary hash.

```powershell
[ordered]@{source_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant();binary_sha256=(Get-FileHash -LiteralPath (Join-Path $out 'NativeEntry.exe') -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$cl;compiler_sha256=(Get-FileHash -LiteralPath $cl -Algorithm SHA256).Hash.ToLowerInvariant();compiler_args=$argsCompile;linker=$link;linker_sha256=(Get-FileHash -LiteralPath $link -Algorithm SHA256).Hash.ToLowerInvariant();linker_args=$argsLink;build_exit=0;native_executions=0;uac_requests=0;admission='BLOCKED'} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $out 'BINDINGS.json') -Encoding UTF8
```

**The generated binary pin becomes the elevation gate** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Launch-Approved.ps1:55-64`

The launcher checks the held file against the adopted output hash, then invokes RunAs. This prevents later swaps but cannot detect that the adopted output was produced from substituted build inputs.

```powershell
    try {$actual=[BitConverter]::ToString($sha.ComputeHash($pin.File)).Replace('-','').ToLowerInvariant()} finally {$sha.Dispose()}
    if($actual -cne $expected) {throw 'native entry fixed-byte mismatch'}
    if($ReadOnlyPreflight) {
        [ordered]@{scope='READ_ONLY_ENTRY_AND_ANCESTOR_PIN_CHECK';sha256=$actual;uac_requests=0;native_entry_executions=0;admission='BLOCKED'} | ConvertTo-Json
        return
    }
    $psi=[Diagnostics.ProcessStartInfo]::new()
    $psi.FileName=$candidate;$psi.Arguments=$ApprovalDigest;$psi.WorkingDirectory='C:\Windows\System32'
    $psi.UseShellExecute=$true;$psi.Verb='runas';$psi.WindowStyle=[Diagnostics.ProcessWindowStyle]::Hidden
    $process=[Diagnostics.Process]::Start($psi)
```

#### Validation

The source and saved bindings show the mutable build stages and the subsequent privileged consumer. All retained hashes are internally consistent; consistency cannot establish the input bytes that the compiler consumed.

Validation method: Static immutable build-to-elevation trace, saved ACL/evidence comparison and independent native review

**Source and output are ordinary D: paths** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:2-5`

The source and build directory are in the supplied AU-writable hierarchy. Ordinary directory creation supplies no protected build custody before compiler consumption.

```powershell
$source='D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v2\NativeEntry.c'
$out='D:\ReBaseGuard-309\records\p309-local-control-package-preparation-20261016-01\i2-native-entry-v3-b4'
if(Test-Path -LiteralPath $out) {throw 'output collision'}
New-Item -ItemType Directory -Path $out | Out-Null
```

**Compiler reads the source by mutable path** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:9-10`

cl.exe consumes the current source path and writes NativeEntry.obj. No reviewed input hash or held immutable input handle binds what the compiler reads.

```powershell
$argsCompile=@('/nologo','/c','/GS-','/O1','/Oi-','/Zl','/D_WIN32_WINNT=0x0602',('/I'+'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\include'),('/I'+$sdk+'\Include\10.0.26100.0\ucrt'),('/I'+$sdk+'\Include\10.0.26100.0\um'),('/I'+$sdk+'\Include\10.0.26100.0\shared'),('/Fo'+$out+'\NativeEntry.obj'),$source)
& $cl @argsCompile 2>&1 | Tee-Object -FilePath (Join-Path $out 'compile.txt')
```

**Linker consumes the mutable intermediate** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:12-13`

link.exe reopens NativeEntry.obj and creates the privileged executable. A separate writer can substitute the intermediate before this read.

```powershell
$argsLink=@('/NOLOGO','/NODEFAULTLIB','/ENTRY:Entry','/SUBSYSTEM:WINDOWS','/DYNAMICBASE','/NXCOMPAT','/MANIFEST:EMBED',"/MANIFESTUAC:level='requireAdministrator' uiAccess='false'",('/OUT:'+$out+'\NativeEntry.exe'),($out+'\NativeEntry.obj'),($sdk+'\Lib\10.0.26100.0\um\x64\kernel32.lib'))
& $link @argsLink 2>&1 | Tee-Object -FilePath (Join-Path $out 'link.txt')
```

**Hashes are computed after compiler and linker use** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:17`

BINDINGS hashes the current source and executable only after use. Restoring reviewed source before this point allows a clean source hash to accompany a substituted binary hash.

```powershell
[ordered]@{source_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant();binary_sha256=(Get-FileHash -LiteralPath (Join-Path $out 'NativeEntry.exe') -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$cl;compiler_sha256=(Get-FileHash -LiteralPath $cl -Algorithm SHA256).Hash.ToLowerInvariant();compiler_args=$argsCompile;linker=$link;linker_sha256=(Get-FileHash -LiteralPath $link -Algorithm SHA256).Hash.ToLowerInvariant();linker_args=$argsLink;build_exit=0;native_executions=0;uac_requests=0;admission='BLOCKED'} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $out 'BINDINGS.json') -Encoding UTF8
```

**The generated binary pin becomes the elevation gate** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Launch-Approved.ps1:55-64`

The launcher checks the held file against the adopted output hash, then invokes RunAs. This prevents later swaps but cannot detect that the adopted output was produced from substituted build inputs.

```powershell
    try {$actual=[BitConverter]::ToString($sha.ComputeHash($pin.File)).Replace('-','').ToLowerInvariant()} finally {$sha.Dispose()}
    if($actual -cne $expected) {throw 'native entry fixed-byte mismatch'}
    if($ReadOnlyPreflight) {
        [ordered]@{scope='READ_ONLY_ENTRY_AND_ANCESTOR_PIN_CHECK';sha256=$actual;uac_requests=0;native_entry_executions=0;admission='BLOCKED'} | ConvertTo-Json
        return
    }
    $psi=[Diagnostics.ProcessStartInfo]::new()
    $psi.FileName=$candidate;$psi.Arguments=$ApprovalDigest;$psi.WorkingDirectory='C:\Windows\System32'
    $psi.UseShellExecute=$true;$psi.Verb='runas';$psi.WindowStyle=[Diagnostics.ProcessWindowStyle]::Hidden
    $process=[Diagnostics.Process]::Start($psi)
```

Assertions:
- The trusted Windows owner/compiler are not adversaries; other AU/sandbox writers are the lower-trust actors.
- The builder does not create a protected build workspace or hold reviewed input bytes through compilation/linking.
- Source hashing occurs after compilation/linking, and the generated binary hash is adopted by the RunAs gate.
- Parent confirms no additional custody evidence for this immutable revision.

Limitations:
- No build, tampering, native execution or live ACL query was performed by the review.
- Supplied saved ACL context is the deployment premise; no actual malicious output is asserted.
- Future protected rebuilding is outside the reviewed revision.

#### Dataflow

AU-writable source/object -\> compiler/linker -\> post-build output digest -\> launcher fixed pin -\> RunAs

- **Source:** Separate local writer's substituted source or object bytes

- **Sink:** Process.Start with Verb runas

- **Outcome:** Administrator execution of the substituted native output after approval

**Source and output are ordinary D: paths** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:2-5`

The source and build directory are in the supplied AU-writable hierarchy. Ordinary directory creation supplies no protected build custody before compiler consumption.

```powershell
$source='D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v2\NativeEntry.c'
$out='D:\ReBaseGuard-309\records\p309-local-control-package-preparation-20261016-01\i2-native-entry-v3-b4'
if(Test-Path -LiteralPath $out) {throw 'output collision'}
New-Item -ItemType Directory -Path $out | Out-Null
```

**Linker consumes the mutable intermediate** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:12-13`

link.exe reopens NativeEntry.obj and creates the privileged executable. A separate writer can substitute the intermediate before this read.

```powershell
$argsLink=@('/NOLOGO','/NODEFAULTLIB','/ENTRY:Entry','/SUBSYSTEM:WINDOWS','/DYNAMICBASE','/NXCOMPAT','/MANIFEST:EMBED',"/MANIFESTUAC:level='requireAdministrator' uiAccess='false'",('/OUT:'+$out+'\NativeEntry.exe'),($out+'\NativeEntry.obj'),($sdk+'\Lib\10.0.26100.0\um\x64\kernel32.lib'))
& $link @argsLink 2>&1 | Tee-Object -FilePath (Join-Path $out 'link.txt')
```

**Hashes are computed after compiler and linker use** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:17`

BINDINGS hashes the current source and executable only after use. Restoring reviewed source before this point allows a clean source hash to accompany a substituted binary hash.

```powershell
[ordered]@{source_sha256=(Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant();binary_sha256=(Get-FileHash -LiteralPath (Join-Path $out 'NativeEntry.exe') -Algorithm SHA256).Hash.ToLowerInvariant();compiler=$cl;compiler_sha256=(Get-FileHash -LiteralPath $cl -Algorithm SHA256).Hash.ToLowerInvariant();compiler_args=$argsCompile;linker=$link;linker_sha256=(Get-FileHash -LiteralPath $link -Algorithm SHA256).Hash.ToLowerInvariant();linker_args=$argsLink;build_exit=0;native_executions=0;uac_requests=0;admission='BLOCKED'} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $out 'BINDINGS.json') -Encoding UTF8
```

**The generated binary pin becomes the elevation gate** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Launch-Approved.ps1:55-64`

The launcher checks the held file against the adopted output hash, then invokes RunAs. This prevents later swaps but cannot detect that the adopted output was produced from substituted build inputs.

```powershell
    try {$actual=[BitConverter]::ToString($sha.ComputeHash($pin.File)).Replace('-','').ToLowerInvariant()} finally {$sha.Dispose()}
    if($actual -cne $expected) {throw 'native entry fixed-byte mismatch'}
    if($ReadOnlyPreflight) {
        [ordered]@{scope='READ_ONLY_ENTRY_AND_ANCESTOR_PIN_CHECK';sha256=$actual;uac_requests=0;native_entry_executions=0;admission='BLOCKED'} | ConvertTo-Json
        return
    }
    $psi=[Diagnostics.ProcessStartInfo]::new()
    $psi.FileName=$candidate;$psi.Arguments=$ApprovalDigest;$psi.WorkingDirectory='C:\Windows\System32'
    $psi.UseShellExecute=$true;$psi.Verb='runas';$psi.WindowStyle=[Diagnostics.ProcessWindowStyle]::Hidden
    $process=[Diagnostics.Process]::Start($psi)
```

**Compiler reads the source by mutable path** — `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-NativeEntry.ps1:9-10`

cl.exe consumes the current source path and writes NativeEntry.obj. No reviewed input hash or held immutable input handle binds what the compiler reads.

```powershell
$argsCompile=@('/nologo','/c','/GS-','/O1','/Oi-','/Zl','/D_WIN32_WINNT=0x0602',('/I'+'C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.44.35207\include'),('/I'+$sdk+'\Include\10.0.26100.0\ucrt'),('/I'+$sdk+'\Include\10.0.26100.0\um'),('/I'+$sdk+'\Include\10.0.26100.0\shared'),('/Fo'+$out+'\NativeEntry.obj'),$source)
& $cl @argsCompile 2>&1 | Tee-Object -FilePath (Join-Path $out 'compile.txt')
```

#### Reachability

Requires local write access to the supplied D: build paths during preparation and later human approval. No remote ingress, malicious trusted owner or existing compromise is assumed.

- **Attacker:** Separate lower-trust authenticated local writer

- **Entry point:** NativeEntry.c or NativeEntry.obj during build

- **Outcome:** A malicious build can satisfy the adopted runtime output pin

#### Severity

**Medium** — Administrator code execution is possible, but requires a local writer to interfere during preparation and the trusted operator subsequently to approve the prepared binary. Absolute trusted toolchain paths and runtime pins protect different stages and do not close this build window.

Protected build custody, reviewed digest-bound inputs and protected intermediates/output would remove this path; evidence of an attacker-controlled produced executable or routine unattended elevation would increase likelihood.

Impact assessment:
- **Level:** high
- **Why:** The resulting native entry is intentionally run as administrator.

Likelihood assessment:
- **Level:** medium
- **Why:** The attacker must hit the preparation window and wait for a later approved invocation.

#### Remediation

Build both privileged binaries in a newly created protected workspace under trusted parent custody. Bind every reviewed input before use and preserve its bytes through compiler consumption; protect objects and outputs from other AU/sandbox writers. Retain provenance, hash protected outputs and repin the launcher/harness only to those rebuilt outputs. D: copies must remain verification copies, not the privileged execution source.

Tests:
- For a future authorized isolated check, prove a distinct lower-trust identity cannot modify source, objects or output during the build.
- Verify protected inputs match immutable reviewed hashes and that final pins refer to protected outputs. Do not count post-build source hashes alone as provenance.

Preventive controls:
- Make build custody and immutable input bindings prerequisites for adopting privileged output hashes.
- Preserve the trusted owner/OS boundary without granting other authenticated or sandbox SIDs equivalent write trust.

## Reviewed Surfaces

| Surface | Risk Area | Outcome | Notes |
| --- | --- | --- | --- |
| Failure finalization and build/provenance records | not recorded | Reported | Build-time source/object/output write boundary becomes privileged binary pin. All 43 manifest hashes/sizes, six source bindings, pin relationships, five sealed copied reports and prior manifest are internally consistent; this does not prove source-to-binary custody. Evidence: artifacts/01_context/static-artifact-checks.json, artifacts/02_review/independent-reconciliation.json |
| Seeded original script and missing pre-CLR startup control | not recorded | Rejected | Source-level repair implemented by trusted ordinary launcher, held binary hash, native System32 bootstrap and same-memory template/harness/approval chain. Original sealed finding state not changed; build provenance is separately reported. |
| Prior cleanup evidence failure omission | not recorded | Rejected | Independent error stages and incomplete-manifest branch now implemented. Nonzero outer exit/EVIDENCE_FAILURE remain mandatory evidence interpretation; media persistence never guaranteed. |
| Ordinary-user pinning and native trusted startup | not recorded | No issue found | All native/launcher source and interfaces reviewed, including independent fresh-context bounds/codec/import/environment analysis. Concrete same-byte pre-CLR chain now exists; genuine compiled bytes are a precondition separately violated by reported build custody. No further concrete bypass established. Evidence: artifacts/02_review/independent-reconciliation.json |
| Offline guest package preparation | not recorded | No issue found | Reviewed signature/index/exact-version/package-hash chain and 19 offline package records (4,312,926 bytes). No install/guest execution claim. Trusted OS keyring and signed metadata assumptions retained; inputs need verification at later use. Evidence: artifacts/01_context/static-artifact-checks.json |
