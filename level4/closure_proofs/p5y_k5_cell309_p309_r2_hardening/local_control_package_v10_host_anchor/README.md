# P309 host anchor v10: development implementation, enrollment revision 3

This additive package implements a real Windows file journal and purpose-restricted ACK signer for a future fixed idle-only controller. It is not an installer, service transport, VM runtime, collector, formal grant, or approval to execute a production adapter. I1–I7 remain OPEN; formal admission remains BLOCKED.

The current source is `NativeFile.cs`, `ServiceIdentity.cs`, `HostAnchor.cs`, and `AnchorAck.cs`. The ordinary harness is `Build-And-Test.ps1`, `BuildToolRunner.cs`, and `TestHostAnchor.cs`. Production compilation excludes every fixture opener, synthetic identity lease, and synthetic reserve-ACK marker. The production DLL was separately inspected by reflection during the tests.

`HostAnchor.OpenInstalled(VerifiedVmReservation)` has one fixed production path and requires an opaque, verified guest-root pre-start/held-VM lease. No public constructor or JSON-to-authority converter exists. The real VM/H2 lease factory is a required separate component and is not implemented by pretending a guest string is an authenticated fact. No production factory was called during this work.

The latest actual ordinary build is `build-broker-g-v3-01`: production and test compilation succeeded with warnings treated as errors; 24 owned temporary-file/process test cases passed. `test-runs/broker-g-v3-01` contains only this run's fixtures. Tests used real Windows file sharing, flush, rename, hard-link, and metadata APIs on those fixtures, not production ACLs or service tokens. No service, account, production directory, key, VM, trace, policy, or privilege was created/changed. No production host-facts query or UAC request occurred.

Exact command, from this package directory, using a new explicit run name:

```powershell
& 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File '.\Build-And-Test.ps1' -RunName 'explicit-fresh-name'
```

The harness refuses an existing run/build name. It copies source bytes to that fresh build, records their hashes, retains read-only handles while compiling/testing, saves bounded child streams and results, and preserves failures. A human-directed development rebuild after a source correction is not a production retry.

`history-single-consume-v1` matches all five input hashes recorded by the original 16-case `build-ordinary-06`. `build-two-phase-01` retains the intermediate 20-case logs, hashes, and binaries. `history-two-phase-v2-22` retains all six exact source inputs from the subsequent 22-case build; `build-two-phase-02` also retains those copies. None is the current accepted protocol. Earlier failed builds/fixtures remain unchanged.

See `DESIGN.md`, `WIRE_SCHEMAS.md`, `INTEGRATION_AND_ACTUAL_VALIDATION.md`, `PRIMARY_SOURCES.md`, and `DEVELOPMENT_RESULTS.md`. Publish only explicitly selected source, documents, sanitized results and hashes. Keep `build-*` binaries, raw child streams, absolute-path command/result records, and all `test-runs` fixtures local; do not bulk-add this directory to Git.
