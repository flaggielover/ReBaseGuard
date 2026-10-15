# Windows to WSL synthetic signing interoperability

Development design and boundary, 2026-10-15. The user authorized implementation
and testing with ephemeral synthetic keys only. No route approval is implied.

## Design

The chosen approach is an explicitly invoked, short-lived Windows PowerShell 7
process. It creates an unnamed ephemeral RSACng key, exports only its public PEM,
and signs the exact bytes received over redirected stdin. Alternatives were
temporary private-key files (unnecessary secret material on disk) and a named-key
Windows service (outside this preparation scope). Neither is implemented.

The WSL test harness starts that Windows executable through WSL interop. It pins
the exact public PEM bytes from its own synthetic helper handshake and passes
them to the unchanged DevSession/OpenSSL verifier. This is test fixture setup,
NOT independent production trust provisioning. No network listener, certificate
store, named key, account, service, scheduled task or policy change is used.

The helper requires -SyntheticOnly, uses RSA PKCS#1 v1.5 with SHA-256, permits
2048/3072/4096-bit test keys, bounds requests and exits after at most 32 signatures.
No private-key import/export or persistence path exists. EOF disposes the key.
Its line protocol carries base64 of raw message bytes; JSON is not reserialized
before signing. No production signing policy is implemented: this is a synthetic
signing oracle owned and closed by the test harness, not an authenticated bridge.

WSL sessions and journals use exclusive temporary Linux directories outside Git.
The harness bounds response size and waits, closes its child processes and removes
its own temporary session data. Evidence contains results and public fingerprints,
never private keys. Disposal is not a claim of forensic memory erasure or safety
against the same user/debugger controlling either process.

## Validation plan

Run the newly supplied test_dev_session once with private CPython 3.11.15 and
record openssl version -a. Retain the prior 21 Python / 11 Windows tests as
historical evidence because their inputs are unchanged.

The new interoperability suite uses real Windows signatures verified in WSL:
all three supported key sizes; multi-message sequencing and replay; UTF-8 Unicode,
CRLF and JSON whitespace byte preservation; wrong-key pin and signature refusal;
payload/signature tampering; cross-session and changed-identity rejection; signed
duplicate-key JSON rejection; signed busy observations never authorize execution;
malformed helper requests and oversized input; fresh-process key rotation and
EOF exit. Successful acknowledgments must remain BLOCKED/false. OpenSSL, WSL
interop or PowerShell absence is an error, never a silent skip or fallback.

## Running

Use the existing Windows PowerShell 7 executable, without installing software.
Set P309_WINDOWS_PWSH to its /mnt/c/.../pwsh.exe path inside Ubuntu, then:

```sh
/home/suzhe/p309/runtime/cpython-3.11.15/bin/python3.11 -B -m unittest -v test_windows_interop
```

The helper requires PowerShell 7.2+ on Windows; Windows PowerShell 5.1 does not
provide the public PEM export API used here. The existing 5.1 sampler tests are
unrelated and remain unchanged. Only a test helper runs, never the host collector.

Self-review: the signing key is ephemeral by a checked CNG property; signatures
cover exact bytes; independent production trust and credential isolation remain
unimplemented. Signed evidence is not proof of process visibility, workload
safety, persistence against a privileged adversary or approved AWS/WSL semantics.
No live enforcement, long-duration claim or P309 execution integration is added.

API references:
https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.rsacng.-ctor
https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.rsa.signdata
https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.asymmetricalgorithm.exportsubjectpublickeyinfopem
