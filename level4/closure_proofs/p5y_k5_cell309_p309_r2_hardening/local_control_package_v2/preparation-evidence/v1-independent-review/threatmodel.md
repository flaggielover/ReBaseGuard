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

---

## Saved Model Context

- Source: scan
- Scan: 2b0afe33-d593-4325-95db-5a2313e50159
- Target: p309-local-vm-diagnostic-dev-20261016
- Revision: e72da101e036e4bd96c0bb230b89be91058c8857
- Snapshot: codex-security-snapshot/v1:sha256:2032d7fb6f900f7904972f82af5c89cc18b52571a2149c3a35dcdb1e432d8f0f
- Result status: completed
- Model origin: generated
- Model scope: level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v1
- Scan scope: .
- Scan scope description: Independent AI static review of all 47 added files in immutable 4070e3d..e72da101: one medium security finding and concrete execution-readiness blockers. This is not owner/formal reviewer approval; I1-I7 OPEN and admission BLOCKED.
