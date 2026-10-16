# Security Review: p309-local-vm-diagnostic-dev-20261016

## Scope

Completed narrow independent static review of protected-build custody and dependent bindings across all 41 changed files in 9e9e59a7..02c8fd50. Zero new reportable findings; prior build-substitution control repaired under the supplied trusted-owner/OS model.

- Scan mode: branch_diff
- Target kind: git_diff
- Target ID: target_sha256_aa743fba3b98454cc8ea65893dba04d7cd5f02ec0a77fd0165042868f408709b
- Revision range: 9e9e59a7dd0be518231c6c92c4ae14dcd329c6d6...02c8fd500e643bfffd553ac0aa78c54670e2099f
- Snapshot digest: codex-security-snapshot/v1:sha256:c6907033fcdd2df10189a6d9ace5fee31da7698afee09433d8024895df30eab3
- Inventory strategy: diff
- Included paths: .
- Excluded paths: none
- Artifacts reviewed: artifacts/01_context/protected-build-static-checks.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Build-Protected.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/FINAL_BINDINGS.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Launch-Approved.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/NativeEntry.c, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/PRIVATE_BUILD_REVISION.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Run-I2Feasibility.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/Trusted-Entry.template.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/EtwCapture.cs, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/Launch-Approved.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/NativeEntry.c, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/PREVIOUS_FINAL_BINDINGS_9e9e59a7.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/PRIVATE_BUILD_CUSTODY.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/Run-I2Feasibility.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/SHA256SUMS.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/TestNativeEntry.c, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/Trusted-Entry.template.ps1, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/embedded-manifest.xml, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/etw-compile.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/etw-compile.stdout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/etw-layout-memory-only.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/etw-layout-memory-only.stdout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/native-compile.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/native-compile.stdout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/native-link.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/native-link.stdout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/native-manifest-inspection.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/native-manifest-inspection.stdout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/native-pe-inspection.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/native-pe-inspection.stdout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/readonly-entry-pin-result.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/unit-compile.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/unit-compile.stdout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/unit-link.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/unit-link.stdout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/unit-ten-known-answers.stderr.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/private-build-v4/unit-ten-known-answers.stdout.txt, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/review-9e9e59a7/coverage.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/review-9e9e59a7/findings.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/review-9e9e59a7/report.md, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/review-9e9e59a7/scan-manifest.json, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/local_control_package_v2/preparation-evidence/review-9e9e59a7/threatmodel.md, C:/Users/Lenovo/P309-I2-build-20261016-v4 (32 exact manifest-named files read only), C:/Users/Lenovo/P309-I2-build-20261016-v4/Build-Protected-as-executed.ps1

Limitations and exclusions:
- AI independent technical repair assessment does not grant execution or formal owner/reviewer admission. I1-I7 OPEN; admission BLOCKED.
- Old scan 062501ff and finding csf_25f671586cf62df1813f5007 remain sealed unchanged; technical repair applies to this new immutable snapshot, not retroactively to the old binaries.
- Trusted ordinary owner, administrators, Windows/system ancestors and installed toolchain are assumed trusted. Other AU/sandbox SID writers are distinct and receive no build-root write access in the recorded control.
- Saved WinPS5.1 build/10 known-answer/layout/parse/read-only-pin results have narrow scope; production Entry/UAC/trace/Job/fixture counts remain zero.
- Production timeout may leave controller alive; UNKNOWN/no automatic retry and final exit plus evidence-error interpretation remain required. This is not newly tested or treated as a newly discovered vulnerability.
- An ordinary build-tool timeout throws before the success custody record and may leave that tool alive; it does not authorize using a partial build. No timeout occurred in the nine recorded successful commands.
- Earlier SOURCE_AND_EVIDENCE_SHA256 and Build-NativeEntry evidence are historical; current FINAL_BINDINGS and private-build snapshot identify the protected execution artifacts. D: archives are verification copies only.
- The first pure Git verification encountered Windows long-path handling; rerunning with process-local core.longpaths and cat-file completed all checks without persistent configuration changes.

### Scan Summary

| Field | Value |
| --- | --- |
| Scan outcome | completed |
| Reportable findings | 0 |
| Severity mix | none |
| Confidence mix | none |
| Coverage | complete |
| Validation mode | Full changed-file accounting, seeded finding validation, static custody source trace and independent SHA/PE-data comparisons. One candidate suppressed; no attack-path-eligible candidates. |

Canonical artifacts: `scan-manifest.json`, `findings.json`, and `coverage.json`. This report is a deterministic projection of those files.

## Threat Model

# Protected-build custody repair threat model

Scope is immutable 9e9e59a7dd0be518231c6c92c4ae14dcd329c6d6..02c8fd500e643bfffd553ac0aa78c54670e2099f: all 41 changed files, focusing on Build-Protected.ps1, PRIVATE_BUILD_CUSTODY.json and dependent path/hash literals. Earlier scans remain sealed. No whole-host audit or production execution is authorized.

The trusted ordinary Windows owner invokes the reviewed builder as literal EncodedCommand under absolute WinPS 5.1. The builder checks exact owner profile SDDL and parent reparse flags, creates a new C:/Users/Lenovo/P309-I2-build-20261016-v4 with protected creation-time DACL permitting only the current owner, SYSTEM and Administrators, and verifies it. It reads six prior source inputs once from the AU-writable D: checkout and compares in-memory bytes to fixed reviewed hashes. It writes derived source privately and holds FileShare.Read source/object/output handles across compiler/linker steps. Tool paths are absolute protected installed toolchains; child environment is five explicit variables. Privileged binaries stay in C:, with D: archival copies treated as evidence, not execution sources.

The dependency chain is fixed prior ETW source -> private ETW binary digest -> derived harness -> derived template -> native source/template pin -> native output -> normal-user launcher pin. Four production source files change only path/hash literals. Tests/layout/parse/pin records must remain distinguished from production execution. The normal launcher, native pre-CLR environment and guard/fixture lifecycle controls were independently reviewed previously and are followed only for binding changes.

Trusted roots are the approved ordinary owner, SYSTEM/administrators, OS/toolchain and trusted invocation constants. Attackers are distinct AU/sandbox SID writers capable of changing D: paths; they are not granted arbitrary control of the owner's processes. Assets are reviewed source-to-binary integrity, approved administrator execution and honest saved evidence. A successful repair must prevent lower-trust writes from entering the compiler or replacing intermediate/output bytes before their digest is adopted.

Only immutable source and named saved evidence/private product bytes are read. No builds/tests/native APIs/host ACL queries/UAC/ETW/fixture/Job/service/VM/network requests are run. Saved execution receipts are assertions supported by source and artifact comparisons, not a new live reproduction. Actual production entry count remains zero; I1-I7 OPEN/admission BLOCKED, with no formal authority granted by AI review. Parent context is untrusted analysis material; no embedded URL is fetched.


## Findings

### No findings

No reportable findings survived the canonical discovery, validation, and reportability gates.

## Reviewed Surfaces

| Surface | Risk Area | Outcome | Notes |
| --- | --- | --- | --- |
| Protected build custody and prior finding repair | not recorded | Rejected | Prior csf_25f671586cf62df1813f5007 is technically repaired for this snapshot: exact prior byte-array hashes precede use, creation-time owner/SYSTEM/BA-only DACL separates other AU/sandbox writers, private source/object/output held through compilation/linking. Existing trusted owner and OS/toolchain assumptions retained; no formal finding-state mutation. Evidence: artifacts/01_context/protected-build-static-checks.json |
| Dependent pins and all historical/changed evidence | not recorded | No issue found | All 41 changed files/20 inventory items accounted. 32 named private manifest entries match sizes/hashes; 27 archived counterparts identical; 6 current source bindings match private/Git; 4 production files each change only 2 path/hash lines; 5 sealed prior report files and prior FINAL_BINDINGS identical. PE imports/manifest/template pin match. Build-end snapshot excludes itself and later-added execution-text file by documented design. Evidence: artifacts/01_context/protected-build-static-checks.json |
