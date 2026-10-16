# Narrow independent implementation feedback closure

The separate `anchor_primary_docs` agent first read the Windows primary API documentation, then statically reviewed the initial native file/identity/anchor/test sources. It did not run a test, query a production API, alter these sources or perform a security scan.

It found two must-fix correctness issues: STOP_REQUESTED swallowed a later MarkRecoveryUnknown; and the abrupt-child test's timeout only disposed Process without stopping the owned child. Both were fixed before the two-phase implementation was accepted for development testing. Current code allows only the forward uncertainty upgrade, retains memory UNKNOWN on failed persistence, and separates State/PersistedState. The owned child timeout now calls Kill through the Process object created by that test and waits two seconds, reporting an unproven stop as failure.

Root independently requested equivalent compiler/test harness timeout cleanup and a complete privilege allowlist. The current ordinary helper records bounded dual raw streams and explicit process/EOF/UNKNOWN states, only requests kill on its own started Process, and does not claim OS calls are hard preemptible. Production identity now requires exactly SeChangeNotifyPrivilege in both actual token and SCM RequiredPrivileges, rather than a six-privilege denylist.

The agent re-read those four narrow closure points after the edits and found no further must-fix there. It explicitly did not review the new revision-3 guest reservation/ACK/CNG integration. A full independent source/contract review of the frozen current package is still required. Temporary tests and this narrow closure do not validate production SCM/token/ACL/key/VM/stop behavior or close any I item.
