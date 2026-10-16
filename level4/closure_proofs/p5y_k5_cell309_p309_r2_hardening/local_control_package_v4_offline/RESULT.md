# Root-scheduler diagnostic: completed capture, incomplete attribution

This is the result of the **one** human-approved `62496ba9b3e14d4afbce1664b613dcf1b34d45cf` execution, not permission for another capture. Invocation ran 2026-10-16 02:56:41–02:57:53 UTC. Native entry exit code 0. The creator's session-GUID-matched stop returned 0; session absence, helper exit, three native fixture Jobs empty, and the WHP fixture Job empty were recorded. No QEMU, guest OS, disk, network, services, accounts, production keys or P309 workload was started.

The original protected capture remains at `C:\ProgramData\ReBaseGuardP309-I2-RootDiagnostic-v3`. Additive local archive and analysis: `D:\ReBaseGuard-309\records\p309-i2-root-v3-attempt-20261016-01`. Original files and earlier failed attempts remain unchanged.

## Actual observations

- ETL: 308,346,880 bytes, SHA-256 `3faee3bd46a7fd33b046edce00da058f630296a0b73d1893c3281c250e1d6870`.
- Saved-file decode: 4,249,919 events; reported event/buffer loss zero. This removes the earlier capture's loss obstacle for this window only.
- Fixed native children exited with code 0. WHP used one VP, 2 MiB, a fixed instruction loop, no guest OS. WHP exit 0; cancellation/run APIs returned success; owned Job had zero active members after exit.
- Same-QPC WHP run window: 1.0041661 seconds wall time. Scheduled run-thread time 0.9950553 seconds; overlapping DPC/ISR union 0.0048037 seconds; subtraction 0.9902516 seconds. VP total-counter delta 0.9731643 seconds; hypervisor-counter delta 0.0047603 seconds; whole-process CPU delta 0.96875 seconds. These counters have different scope and boundary times. They are **not summed or declared equivalent**, and do not prove host/guest accounting completeness.
- A 60-second interior window has closed intervals for all 32 CPU indices and no observed CSwitch continuity break. 1,920 CPU-seconds classify as 1,649.5231501 idle, 253.4771364 other identified, 16.5604543 protected-flag, and **0.4392592 unknown identity across 1,328 intervals**. Protected process flags are observations, not proof of complete PPL coverage.

## Analysis corrections and limits

The earlier text projection failed strict CP936 decoding; its error is retained. The new native offline decoder consumes the existing ETL with `PROCESS_TRACE_MODE_RAW_TIMESTAMP`, records clock type/frequency and processor-index flags, and extracts only documented/version-checked prefixes needed for this analysis. Zero `unknown_required_prefix` means no rejected prefix in the explicitly handled classes; it does not mean every ETW event or every workload is covered. Raw ETL, full CSV/XML and unrelated process/thread identities remain local.

Matching DCStart after a real Start is coalesced without widening the actual birth bound. Two new memory tests validate that correction and identity mismatch rejection; the four unchanged lifetime tests were not repeated. Original results, corrected V2 and V3 results remain separate. V2 source was reconstructed and verified against the digest recorded by that execution, explicitly labelled as reconstruction. V3 changes only numeric CSV parsing and optional local diagnostic identities and has the same aggregate result as V2.

There are 40 unresolved thread event histories after the correction, including end-only/idle histories and starts after the comparison window. Some unknown intervals cross the recorded ThreadEnd boundary. That is a lead, **not an accepted extension of thread ownership**. Check payload versus event-header identities, terminal scheduling semantics, TID reuse and idle aliases against exact event evidence before proposing any correction. Do not waive these intervals, use names as an allowlist, or replace missing identity with a synthetic assertion.

The saved-trace analyser used existing Windows CPython **3.12.14** (`b847bb9f4e48c19f585c8bf7d8b355f3f8c6d2125717ece9c9d7e16fb9f09de8`), not private Ubuntu 3.11.15. No historical D2/WSL suites were rerun. This interpreter was used solely for new offline numerical analysis; it is not a P309 runtime qualification. Native decoder prefix checks: 12; interval unittest methods: 10; original lifetime methods: 4; new rundown methods: 2. These verify parser/arithmetic properties, not production isolation or complete host coverage.

## Remaining work and order

**I1–I7 remain OPEN; formal admission BLOCKED.** This capture demonstrates feasibility of these particular administrative ETW/WHP operations, not the isolated production service identity or an accepted route revision.

1. I2: retain unknown attribution; resolve event/identity semantics, counter boundaries, protected/short-lived workload coverage and loss detection. Read exact current ETW/LSA permissions before specifying minimal non-admin observer rights and exact rollback. Ordinary EventAccessQuery returned access denied, not an empty descriptor.
2. I4: establish actual guest image and whole installed runtime/library provenance; existing build-host records do not prove the future VM runtime.
3. I1/I3/I5: implement and verify VM custody, separate service identities and keys, peer/public-key enrollment, fixed broker actions and runtime limits using the actual approved install plan.
4. I6: validate independent stop, durable exactly-once state, crash/reboot/recovery and cleanup under real failures. Prior paused probes and the current successful cleanup do not close this requirement. A 75-second stop-request thread cannot preempt a stuck system call.
5. I7: obtain independent review and explicit accepted route/admission authority, including unresolved AWS-dependent contract changes. Then, and only with valid formal authority, follow original freeze/grant/qualification/target/exactly-once rules. No threshold changes or self-issued authorization.

The next prepared package is a single elevated **read-only** installation-facts query, not an installer or another trace. Its approval is separate because the one approved real diagnostic is consumed.
