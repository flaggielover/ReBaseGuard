Native entry ownership tests, 2026-10-16

The actual static `admin()` and `hash()` functions are included from
`../package/NativeEntry.c` (SHA-256 recorded in NATIVE_OWNERSHIP_RESULT.json).
The console test entry is `main`; the source's entry function is renamed and
never called. Loader, dynamic export lookup, library release, token handle
release and current-process APIs are replaced by pure-memory functions.
Token and CNG exports point only to synthetic functions.

19 cases and 1,186 assertions passed. Cases cover library failures, each of
eight missing exports, token open/query failure, non-elevated token, CNG
algorithm open/hash create/update/finish failure and successful cleanup and
digest formatting. Failed open/create calls deliberately write non-NULL
poison outputs; cleanup rejects those outputs. Successful resources must be
released exactly once. A successful API result with a malformed return length
was not made an accepted API contract or a required defect.

The first ordinary Windows PowerShell invocation was refused by its script
authorization manager before the script ran. The successful invocation was:

    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File outputs\p309-readiness-repair-staging-v3\tests\Run-NativeOwnership.ps1

`-ExecutionPolicy Bypass` applies to that child process; no persistent Windows
execution-policy setting was changed. All compiler/linker/runtime commands,
tool hashes, input hashes and actual exit codes are recorded. TEMP/TMP,
objects, executable and logs were confined to this test directory. The test
binary uses the explicit asInvoker manifest; it did not request UAC.

These tests establish only behavior under synthetic API returns. They do not
prove actual Win32 failure output behavior, real token/CNG access, production
isolation or formal admission. No token/CNG query, elevated entry, ETW trace,
VM, service, production key or P309 workload was invoked. Admission remains
BLOCKED.
