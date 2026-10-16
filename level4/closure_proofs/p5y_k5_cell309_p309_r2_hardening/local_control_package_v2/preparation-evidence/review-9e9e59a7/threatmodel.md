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

---

## Saved Model Context

- Source: scan
- Scan: 062501ff-46d7-4197-b864-809cebfb9771
- Target: p309-local-vm-diagnostic-dev-20261016
- Revision: 9e9e59a7dd0be518231c6c92c4ae14dcd329c6d6
- Snapshot: codex-security-snapshot/v1:sha256:ce77da722f7e960a2d320fc39241cbfa59522b687e3b75320f0643fccf9fa389
- Result status: completed
- Model origin: reconciled
- Model scope: level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2
- Scan scope: .
- Scan scope description: Completed independent static security diff review of all 27 changed files in bc2562fd..9e9e59a7, plus supporting unchanged ETW/lifecycle and saved ACL context. One medium build-custody finding; no execution or formal approval.
