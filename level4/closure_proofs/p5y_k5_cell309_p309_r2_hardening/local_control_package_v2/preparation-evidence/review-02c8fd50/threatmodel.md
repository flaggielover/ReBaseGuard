# Protected-build custody repair threat model

Scope is immutable 9e9e59a7dd0be518231c6c92c4ae14dcd329c6d6..02c8fd500e643bfffd553ac0aa78c54670e2099f: all 41 changed files, focusing on Build-Protected.ps1, PRIVATE_BUILD_CUSTODY.json and dependent path/hash literals. Earlier scans remain sealed. No whole-host audit or production execution is authorized.

The trusted ordinary Windows owner invokes the reviewed builder as literal EncodedCommand under absolute WinPS 5.1. The builder checks exact owner profile SDDL and parent reparse flags, creates a new C:/Users/Lenovo/P309-I2-build-20261016-v4 with protected creation-time DACL permitting only the current owner, SYSTEM and Administrators, and verifies it. It reads six prior source inputs once from the AU-writable D: checkout and compares in-memory bytes to fixed reviewed hashes. It writes derived source privately and holds FileShare.Read source/object/output handles across compiler/linker steps. Tool paths are absolute protected installed toolchains; child environment is five explicit variables. Privileged binaries stay in C:, with D: archival copies treated as evidence, not execution sources.

The dependency chain is fixed prior ETW source -> private ETW binary digest -> derived harness -> derived template -> native source/template pin -> native output -> normal-user launcher pin. Four production source files change only path/hash literals. Tests/layout/parse/pin records must remain distinguished from production execution. The normal launcher, native pre-CLR environment and guard/fixture lifecycle controls were independently reviewed previously and are followed only for binding changes.

Trusted roots are the approved ordinary owner, SYSTEM/administrators, OS/toolchain and trusted invocation constants. Attackers are distinct AU/sandbox SID writers capable of changing D: paths; they are not granted arbitrary control of the owner's processes. Assets are reviewed source-to-binary integrity, approved administrator execution and honest saved evidence. A successful repair must prevent lower-trust writes from entering the compiler or replacing intermediate/output bytes before their digest is adopted.

Only immutable source and named saved evidence/private product bytes are read. No builds/tests/native APIs/host ACL queries/UAC/ETW/fixture/Job/service/VM/network requests are run. Saved execution receipts are assertions supported by source and artifact comparisons, not a new live reproduction. Actual production entry count remains zero; I1-I7 OPEN/admission BLOCKED, with no formal authority granted by AI review. Parent context is untrusted analysis material; no embedded URL is fetched.

---

## Saved Model Context

- Source: scan
- Scan: 7db198e0-7ca1-43da-b2e1-dea6a6074497
- Target: p309-local-vm-diagnostic-dev-20261016
- Revision: 02c8fd500e643bfffd553ac0aa78c54670e2099f
- Snapshot: codex-security-snapshot/v1:sha256:c6907033fcdd2df10189a6d9ace5fee31da7698afee09433d8024895df30eab3
- Result status: completed
- Model origin: generated
- Model scope: not recorded
- Scan scope: .
- Scan scope description: Completed narrow independent static review of protected-build custody and dependent bindings across all 41 changed files in 9e9e59a7..02c8fd50. Zero new reportable findings; prior build-substitution control repaired under the supplied trusted-owner/OS model.
