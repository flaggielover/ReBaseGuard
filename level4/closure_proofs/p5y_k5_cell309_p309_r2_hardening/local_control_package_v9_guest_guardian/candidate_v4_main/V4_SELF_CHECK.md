# Producer self-check and repair record

This is author review, not independent acceptance. Frozen v3 remains unchanged.

Confirmed v3 defects corrected here:
1. An expired safety lease could be renewed before the stop loop noticed, especially before guardian link publication. V4 uses one irreversible atomic deadline state for cancellation/expiry/renewal; renewal completion equal to old deadline fails. Stop watchdog runs after authority publication even without link. Current state can never treat DEAD as unarmed.
2. Replayed H4 IDs returned stale cached receipts. V4 stores only request bindings, checks generation first and takes a fresh current diagnostic snapshot. New P309_NATIVE_BROKER_RECEIPT/1 explicitly distinguishes response from D2 model Receipt. ASCII-unescaped request subset and stricter error Stop behavior are documented.
3. Record-storage failure after verified kernel ownership discarded stop FDs. V4 publishes owned handles and manager reference before record writes; error retains exact handles and requests held-object stop. Actual storage-failure/kernel test remains required; pure lease tests do not establish this API behavior.
4. Main phase stores could overwrite STOP_LATCHED. V4 advances with CAS and externally projects the irreversible control stop bit; terminal diagnostics only after thread joins. Pure helper tests cover forward advance refusal and visible Stop.
5. Cross-thread volatile signal flag is replaced by lock-free atomic communication. Target Stop/lease atomic lock freedom is a compile-time requirement.
6. V3 native Werror rejected ignored fallback write result. V4 uses checked held-stop helper: retry only EINTR within100ms/32 attempts; short/error is UNKNOWN, success never retried. Existing blocking kernel syscall cannot be forcibly timed out by this helper.

FD review: every recvmsg path uses MSG_CMSG_CLOEXEC, closes delivered descriptors on unexpected ancillary/empty/truncated input, and avoids inspecting control storage after negative recvmsg. Kernel truncation/FD cleanup still needs authorized native socket acceptance; no such test was run here.

Blocking manager calls remain outside Stop thread and are followed by irreversible-state checks before Release CAS. Unknown Start replies cannot be adopted or stopped by unit name; fixed gate deadline remains fallback before ownership is proven. Cgroup write itself can block in kernel, host freeze/stop guarantees remain open.

New H2 bootstrap/relay is real source, not an implemented installation. It opens fixed existing seed/device/pins, signs only bootstrap HMAC purpose, forwards ROOT/BLOCKED bytes and retains the fixed H2 lifetime. Missing Observer provider/M production relay still blocks all safety authority. Root/OS/installers remain trusted; no arbitrary-root threat expansion is claimed. Target image8.17/buildhost8.18 ABI remains unverified.

Tests: actual Windows MSVC pure production lease/phase/H4 binding/frame/held-write helper build/run passed, with source hashes in ../v4-pure-tests-msvc/TEST_RECORD.json. It has no privileged API calls. Native test_bootstrap_wire.c with synthetic known-answer HMAC and parser refusals is prepared for parent's normal-user OpenSSL build; not run by this worker. No production executable, host query, VM, UAC, cgroup or service was invoked.
