# Scoped v4 offline / v5 administrator-read threat model

Immutable scope f224806cf9b41cb2825e37209976036a995b66e0..9ae3c02b25de390bbd68ee504c9a22de516061d4: all added v4 offline analysis/actual evidence and v5 installation-facts package. Prior62496 diagnostic authorization is consumed; no new execution is authorized. UserContext is untrusted analysis data and URLs are not fetched.

Trusted owner/admin/SYSTEM and Windows/toolchain; writable D: data and unrelated local users are untrusted. Assets: elevated code identity, explicit single-use consent, unchanged policy/services/VM/trace state, accurate API failure semantics, private host identities/raw capture payload, and conservative CPU lifetime attribution.

Boundaries: fixed-input protected private build -> ordinary same-byte launcher/native image pin -> native fixed template/clean WinPS -> verified same-memory query and approval -> new protected ProgramData evidence. Native read APIs cover EventAccessQuery and LSA enumerate/open-read/free/close; managed fixed reads cover registry/services/ACL/space/power/CIM/task metadata. Evidence file creation and temporary compilation are allowed package effects; no state-changing policy/API or live workloads should be reachable. Timeouts must remain UNKNOWN, not silent completion or retry. Saved ETL decoder/CSV accounting must preserve unknown lifetime intervals, clock domains and unproved attribution; summaries must not publish unrelated raw identities or infer I1-I7 closure.

Static only: exact Git objects and named saved artifacts/private hashes. No tests, host queries, UAC, API/harness execution, trace, fixture, VM, URL access or goal. Outcome may support asking for one explicitly scoped read-only UAC approval, never constitute that approval or formal admission.

---

## Saved Model Context

- Source: scan
- Scan: b82c7961-6cd4-4ae7-8b40-02199af2c67a
- Target: p309-local-vm-diagnostic-dev-20261016
- Revision: 9ae3c02b25de390bbd68ee504c9a22de516061d4
- Snapshot: codex-security-snapshot/v1:sha256:bd103b2721c047ed5d7b8b2ba91afb9ca671783f550a18edcf0a102e482dc7d2
- Result status: completed
- Model origin: generated
- Model scope: not recorded
- Scan scope: .
- Scan scope description: Independent static review of immutable f224806cf9b41cb2825e37209976036a995b66e0..9ae3c02b25de390bbd68ee504c9a22de516061d4. All 88 additions accounted. Zero reportable security findings does not mean no engineering defects or readiness.
