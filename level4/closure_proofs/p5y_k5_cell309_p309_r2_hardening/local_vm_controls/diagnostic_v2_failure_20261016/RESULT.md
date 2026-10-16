# V2 actual attempt: rejected before VM creation

Exact source 9e690eb178d86a635b7346b3fb16b42c8990236d was approved by request_user_input_async/call_8e1dc0953e774e11915a48a4c669a657/item0: 批准单次诊断 V2.
The guard rejected an unlisted runtime file in LockRuntime, before CreateJobObject and CreateProcess. deadline.jsonl is empty. No V2 QEMU process/VM was created; no second launch was attempted. The harness conservatively reports UNKNOWN because it never received owned_start; this does not itself imply a lingering VM.

A complete read-only audit then verified all 222 pinned files unchanged and found five extra .db files under the literal ucrt64/bin/%SystemDrive%/ProgramData/Microsoft/Windows/Caches directory. Creation UTC 00:20:10 falls within V1's recorded lifetime (00:20:04-00:20:20). No bytes were removed or changed. Their hashes/timestamps are in runtime-extra-file-investigation.json; cache contents are not published.

The old child environment did not define SystemDrive and used the runtime bin directory as CWD. These facts support a cache-path-expansion hypothesis, not definitive attribution of the writing process, and do not explain the Job active count of two. The V2 preparation failed to recheck unlisted runtime files before requesting approval; the guard correctly rejected them at execution. This preparation error is retained.

Next candidate should preserve candidate-v1 and all extra files, stage exactly the pinned 222 files into a new runtime root only after approval, explicitly populate SystemDrive and windir, move CWD and user cache directories into the new evidence area, and run a complete read-only preflight before consuming a one-launch reservation. It must retain the atomic Job creation, member diagnostics and all limits. No automatic new real attempt is authorized by this failed attempt.

V1 remains FAIL; V1 guard-exit NOT_RUN; V2 NOT_CREATED. I1-I7 open; admission BLOCKED. No platform rejection of all Windows/WHPX architectures is justified yet.
