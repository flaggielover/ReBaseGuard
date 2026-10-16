# Actual platform probe failure (2026-10-16)

The user-reported manual reboot is confirmed by boot UTC 2026-10-16T00:02:33.5000000Z. WHP Win32_OptionalFeature InstallState=1, PowerShell 7.6.5, ordinary/non-elevated process. Available RAM before the probe was 17,268,781,056 bytes. The 31 prior evidence files and 222 runtime files passed fresh SHA-256 verification.

Only the approved deadline case ran. It bound QEMU PID 9760, creation FILETIME 134365836056953460. At five seconds the Job reported ActiveProcesses=2, violating the expected value 1. The batch returned failure and did NOT run guard-exit. There was no automatic retry. QEMU remained paused, diskless and networkless; no P309 work ran.

The deadline cleanup record reports wait=0, final_wait=0, ActiveProcesses=0, exit_code=777 (0x309), terminate_error=0, cleanup_proven=true; the external held process handle also signaled (child_wait=0). Guard exit 0 describes its cleanup, not overall probe acceptance. scoped_probe_pass=false is authoritative. This does not prove all hypervisor/kernel resources released.

The original logs do not enumerate Job member identities, read back effective limits, or timestamp the deadline. Therefore the second count cannot be attributed to vmmem, a helper, or a live unauthorized process from these records alone. No member identity is inferred from its name. The discrepancy is unresolved; no retroactive PASS or acceptance relaxation is permitted.

Code review additionally identified a creation-to-assignment crash window: CREATE_SUSPENDED precedes AssignProcessToJobObject. A revised candidate should use the documented PROC_THREAD_ATTRIBUTE_JOB_LIST atomic creation facility, retain the same restrictions, read back configured limits, and log bounded Job-local member identities. That candidate requires new exact bindings and explicit approval before another real VM launch; source/build/unit work is already authorized.

All I1-I7 remain OPEN_RETAINED. Formal admission BLOCKED. This is not decisive proof that Windows/WHPX as a whole is infeasible; it is a decisive rejection of this specific acceptance run. Neither historical nor new synthetic results can replace a future approved real observation.
