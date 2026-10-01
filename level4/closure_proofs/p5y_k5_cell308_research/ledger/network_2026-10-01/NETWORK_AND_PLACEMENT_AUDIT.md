# Network-path and compute-placement audit for MB-S (owner supplement 1, Part III)

Coordinator (editorR3C1), 2026-10-01T11:10-11:20Z. Target-free, read-only: interface and per-process byte counters,
process names, directory sizes on the Mac; one read-only status command on the AWS worker; one on the Vultr worker
(failed, see below). No credential, proxy configuration or cell-309 content was read; nothing was changed.

## 1. Evidence

| where | reading | value |
|---|---|---|
| Mac, uptime | since boot | 1 day 20 h (44 h) |
| Mac `en0` | bytes since boot | in 9.0 GB, out 5.3 GB |
| Mac `utun6` (the proxy's TUN, 198.18.0.1) | bytes since boot | in 16.0 GB, out 4.3 GB |
| Mac `lo0` | bytes since boot | 12.1 GB each way (local only) |
| Mac per-process (`nettop`, since each process start) | largest | verge-mihomo 0.2 GB + 0.2 GB; Claude Helper 0.17 GB in; nothing else above 50 MB |
| Mac sync / backup | processes | no Time Machine destination; iCloud `bird` idle; no rsync / scp / rclone / Dropbox / Syncthing |
| Mac repository | layout | one object store `/Users/suzhe/ReBaseGuard/.git` (1.1 GB) shared by all worktrees; last fetch 2026-09-28T21:11 local; branches local only (never pushed) |
| campaign scratch | size now | builder3/4/5 + reviewers about 2.1 GB (local, under /private/tmp; never synchronised) |
| session transcripts | size | 563 MB for 57 sessions of this project (local) |
| AWS worker | uptime 22 days | `enp39s0` rx 0.4 GB, tx 1.1 GB in total; load 0.00; x86_64, 32 cores, Python 3.12.3 |
| Vultr worker | status | SSH timed out during banner exchange (66.42.38.97:22): not readable from here |

## 2. Findings (section 15 of the supplement)

| candidate cause | finding | basis |
|---|---|---|
| repeated scratch synchronisation | NOT OBSERVED for this campaign | all MB-S scratch is local; no sync process; counters |
| repeated repository cloning | local only | sandboxes are `git clone --shared` of a local `--no-local` base store: disk, no network |
| Git object transfer | NOT a cause | no fetch since 2026-09-28; nothing pushed |
| cloud-session workspace synchronisation | UNKNOWN | this session is local; other sessions were not inspected |
| large log streaming / polling large files | small | AWS worker 1.5 GB total in 22 days; this session has not used either worker before this audit |
| qualification artifact transfer | none | qualification evidence is local commits |
| proxy / VLESS routing | the Mac's whole proxied volume since boot is about 20 GB in 44 h | `utun6` counters |
| package downloads | none by this campaign | no install step in any brief |
| background file sync | NOT OBSERVED | process list |

**Conclusion.** The Mac moved about 14 GB on `en0` (20 GB through the proxy TUN) in the 44 h since boot, i.e. roughly
8-11 GB per day; the AWS worker moved 1.5 GB in 22 days. Neither is of the order of 2 TB in four days (about 500 GB per
day). **The source of the 2 TB is UNKNOWN from the hosts readable here.** Not excluded: the Mac before its last boot
(counters reset at boot); the Vultr host (unreachable; if it is the proxy server it also carries every other client
of that proxy); other devices or sessions using the same proxy. The owner can read the proxy server's own per-client
accounting; the campaign does not touch the proxy configuration.

What this campaign does send: API requests of the coordinator and its agents (each tool call re-sends that agent's
context) and nothing else. That is inside the 5.3 GB the Mac sent since boot. Low-traffic mode (section 4) reduces it.

## 3. Compute-placement classification (section 11 of the supplement)

AWS worker = x86_64 Linux, Python 3.12.3. Frozen-to-be platform pins (protocol section 8) = arm64, macOS build
25F84, Python 3.14.5 framework build with pinned interpreter and libpython hashes; the host contract reads macOS
facilities (`ps` lstart, `pmset`, `vm_stat`, `sysctl kern.*`, `launchctl`, `caffeinate`, `notifyutil`).

| operation | class | reason |
|---|---|---|
| builder5 remaining tests | LOCAL_HOST_BOUND | they exercise the macOS host module and launchd; reviewed results must come from the pinned interpreter |
| static tests | LOCAL_HOST_BOUND | assert the platform pins and the pinned file hashes on the qualification host |
| unit / state tests | LOCAL_HOST_BOUND | liveness (`ps`), boot UUID, memory and disk gates are macOS readings |
| mutant matrices | LOCAL_HOST_BOUND | same suites under mutation; a Linux run would be a different test object needing its own review |
| crash / recovery mutants | LOCAL_HOST_BOUND | process groups, SIGKILL timing and launchd behaviour of the execution host |
| decoy computations | LOCAL_HOST_BOUND | platform pins are re-verified in every computing mode; certified bytes are pinned to the platform |
| MBR1_REPRO | LOCAL_HOST_BOUND | exact equality with MB r1's records is the RC2 platform argument itself |
| QS-RESUME-DECOY | LOCAL_HOST_BOUND | decoy computation + the host's checkpoint / kill path |
| designated pre-freeze R-rule measurements | LOCAL_HOST_BOUND | R-MEM / R-FREE / R-EXCL-PCT / R-ALLOW measure THIS host |
| official qualification decoy runs | LOCAL_HOST_BOUND | launchd launcher, frozen values, host provenance |
| Q12 | LOCAL_HOST_BOUND | runtimes of the execution host against the fixed caps |
| host-readiness / disk checks / memory measurements | LOCAL_HOST_BOUND | readings of the execution host |
| hash verification, manifest generation | LOCAL_HOST_BOUND | over the local worktree and object store; seconds of CPU, no network |
| independent reconstruction | LOCAL_HOST_BOUND | frozen as a step of the local protocol on the pinned platform |
| independent reviews | REVIEW_ONLY | agents reading local files; their re-runs are the local suites above |
| target execution | LOCAL_HOST_BOUND | the frozen host contract |
| sealing | LOCAL_HOST_BOUND | refs and objects of the local repository |
| adjudication | REVIEW_ONLY | mechanical application of the frozen criterion to the sealed record |

AWS_SAFE_COMPUTE: none. UNKNOWN: none.

**Decision recorded: `AWS_OFFLOAD_DEFERRED_FOR_MB-S`.** Moving any computing item would need a new platform
qualification (pins, host module, launcher) or would change MBR1_REPRO's premise; and no item above sends data over
the network when run locally, so an offload would add transfers (code out, evidence back) and avoid none. Estimated
bytes avoided by AWS offload: 0. Tasks moved to AWS: none. The only AWS use is this audit's one status command.

## 4. Low-traffic operating mode (in force from 2026-10-01T11:11Z)

* agents: batched commands, long output to local files, short summaries read back, bounded polling, no re-reading of
  large logs, base stores reused when intact, sandboxes deleted after each heavy run;
* coordinator: fewer and larger tool calls; agent transcripts never read; reviews by hash and targeted reads;
* scratch classes ACTIVE / EVIDENCE / DISPOSABLE as in builder5's scratch-lifecycle gate; DISPOSABLE never leaves the
  host; nothing is pushed or fetched;
* independent review is not reduced.

Traffic ledger: `ledger/TRAFFIC_LEDGER.md`.
