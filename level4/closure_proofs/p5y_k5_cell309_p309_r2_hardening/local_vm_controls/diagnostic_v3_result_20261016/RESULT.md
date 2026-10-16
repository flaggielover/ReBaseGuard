# V3 actual diagnosis: second live member identified as conhost.exe

Approved source 21e14c1664a03ce0d6bdaed913d30aa0acfa7a8f. New candidate-v3 staging verified 222 files / 459,552,711 bytes. One real paused, diskless, networkless diagnostic ran; no second probe or P309 work ran.

Four Job snapshots and two effective-limit readbacks were recorded. Before creation: active=0. Suspended QEMU: active=1. At five seconds: active=2, total=2, limit-terminated=0. Both members were bound to this Job and wait=258 (not signaled): QEMU PID 14452 / creation FILETIME 134365845543990746 and C:\Windows\System32\conhost.exe PID 33996 / FILETIME 134365845544879939. This is live owned-member evidence; it is not a name-based exemption. Limits remained flags=8968 (0x2308), active limit=1, each memory cap=805306368.

On the anomaly the guard requested Job stop at 5031 ms; cleanup observed at 5078 ms. Job active=0, final process wait=0, exit=777, native terminate error=0; external held QEMU handle signaled and guard exit=0. This proves the recorded scoped cleanup, not all partition/kernel resources. The original single-member expectation remains false, so this is not platform admission PASS.

Post-run runtime verification confirms all 222 files and no extras. The five generated cache files now appear under child-scratch/program-data; hashes are saved, contents retained locally and omitted from Git publication. candidate-v1 and its original five extra files remain untouched.

Static investigation: installed QEMU PE subsystem=3 (console). A search of 32,290 C/C++/header files under 4 MB in the already verified upstream QEMU source archive found no AllocConsole/AttachConsole strings. This is a bounded static search, not dynamic attribution and not proof about third-party DLLs. The current CREATE_NO_WINDOW path and Microsoft's console-host documentation support trying DETACHED_PROCESS; the flag change still requires fresh real evidence, not an inferred fix. No Job limit will be raised and no process name exempted.

I1-I7 remain open; formal admission BLOCKED. V1 guard-exit remains NOT_RUN. The next concrete source candidate should preserve this evidence, remove hidden-console creation in favor of detached startup, and prepare the original deadline/guard-exit pair with a stop-on-first-failure gate for a consolidated approval. No additional launch is authorized by this single V3 diagnosis.

Primary references: https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags and https://github.com/microsoft/terminal/blob/main/doc/specs/%23492%20-%20Default%20Terminal/spec.md .
