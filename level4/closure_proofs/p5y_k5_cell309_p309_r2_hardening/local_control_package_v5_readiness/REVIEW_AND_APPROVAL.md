# Single elevated read-only installation-facts package

Status: built and prepared for independent review; **not approved or executed**. I1–I7 OPEN; admission BLOCKED. The preceding one-shot root diagnostic has completed and does not authorize this UAC request.

## Why this step is necessary

Ordinary `EventAccessQuery` returned Windows error 5 for the SystemTraceProvider and proposed private session GUID. No descriptor was returned. Exact existing permissions and rollback cannot be inferred from this error. This package batches installation-critical permission and maintenance metadata into one administrative read, before proposing actual service/identity/policy changes.

## Exact scope and bindings

Input source commit: `a3a478089a9f756853efd6bc68a88d48d83909d1`. Completed package revision and review seal are recorded additively after review. `FINAL_BINDINGS.json` binds invocation, build and query sources.

- One ordinary-owner invocation of the pinned private native entry, one UAC. Private root: `C:\Users\Lenovo\P309-InstallationFacts-build-20261016-v2`.
- Native SHA-256: `7c8345bb9210e61b1d137754d2223c8415cd9a2623a4633c415aacfccf0cbc93`.
- Query script SHA-256: `a756f9d04a418132f799be38ab5574415e7ac56dd8bf815c0eecdb951c5c52aa`.
- New protected evidence directory: `C:\ProgramData\ReBaseGuardP309-InstallationFacts-v1`, administrator-owned, Administrators/SYSTEM full access, current owner read/execute. Existing directory/file is refusal, never adoption.
- Fresh approval file: `D:\ReBaseGuard-309\records\p309-installation-facts-v1-human-approval.json`, scope `P309_SINGLE_ELEVATED_READONLY_INSTALLATION_FACTS_V1`, count 1, actual human reply and source/native/query bindings. It is not created as approval before consent.
- Fixed reads: ETW descriptor and corresponding registry-value presence for two GUIDs; existing LSA rights for three proposed service SIDs; collisions for three exact proposed service names; selected parent ACLs; C/D free space and proposed path collisions; active sleep scheme; selected update/pending-reboot metadata; selected DeviceGuard properties; update task names/state/enabled/wake flags. No task actions, secrets or unrelated file content are collected.
- Only evidence files and process-local compilation temporary files are created. No EventAccessControl, LSA-right assignment, registry write, ETW session, VM, tracing, sampling, workload, key, account, service, group membership or Windows policy change. `-ExecutionPolicy Bypass` is process-only and does not set a Windows policy.

## Validation standard

Verify reviewed source/binary/launcher hashes before requesting UAC, ordinary-owner context, fresh attempt/evidence paths and at least 512 MiB available on each C and D. The native entry loads only pinned template bytes and starts the fixed inbox Windows PowerShell with a clean environment; the template executes the same verified query bytes in memory. Store each query result separately and hash the final JSON records.

Interpret every API status and query exception. Access denied/unsupported/missing account are unavailable facts, never an empty permission grant. Selected policy absence does not prove updates/restarts cannot occur. A successful process exit is not a complete readiness verdict; inspect `unknown` and individual native API return codes. Preserve original elevated records, verify copy hashes to D, and publish minimized summaries only. No admission or installation is authorized by these facts.

Build validation uses Windows PowerShell 5.1.26100.9444, literal-only C# compilation, exact ABI sizes (48/16), a six-import read-only API allowlist, six pure space-boundary checks and ordinary file-binding preflight. None invokes the query methods or harness. The first build's PowerShell Marshal overload failure is retained; it preceded UAC and was fixed in the test helper. The failed v1 private build remains intact.

## Timeout, failure and rollback

The launcher waits up to 260 seconds. Some OS read APIs may block; this is not a guaranteed completion deadline. A timeout or incomplete evidence is UNKNOWN: preserve the owned process identity and files, do not retry or kill unrelated processes. No automatic second invocation. Native entry never starts a VM or persistent service.

There are no policy/privilege/service changes to undo. Rollback is to stop progression and retain/seal the new evidence and private build directories; archive by verified copy to D if required. Do not delete old evidence, backups, Ubuntu or previous builds. Never execute guessed inverse ACL or registry changes. Actual production installation will require a separately reviewed, concrete package and the user's grouped approval once these unavailable baseline facts are obtained.
