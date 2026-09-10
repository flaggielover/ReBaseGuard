# P5Y K1 SR — pre-edit production-lifecycle failure-mode inventory (PHASE 0)

Written BEFORE any file of this successor was created. Parent (frozen, untouched):
`p5y-k1-sr-production-authorized-preresult` @ `bd7cf269792bc146e911ee57a85533b7b7b1aa9d`.
Genuine SR production cells at inventory time: **0**.

Classes: BLOCKING · NON_BLOCKING_LIMITATION · ALREADY_CLOSED · FALSE_POSITIVE ·
OPEN_GOVERNANCE (not an engineering defect; flagged for the adjudicator).

| id | stage | failure mode (evidence) | class | resolution in this successor |
|---|---|---|---|---|
| L01 | pre-launch | live HEAD must equal the approved tag, worktree clean (`gate_approved_launch_head`) | ALREADY_CLOSED | unchanged; production runs from the parent-tag worktree |
| L02 | pre-launch/restart | `production/PRODUCTION_LEDGER.json`, `.json.lock`, `.tmp`, `cells/NNNN.json`, `cells/.tmp-*` are untracked and NOT ignored, so `git status --porcelain` refuses every restart after the first ledger write | BLOCKING | governed runtime-state exclude block (exact bytes, hash-bound, verified by probes) + content classifier |
| L03 | pre-launch | the qualified venv lives in the main checkout (other branch) | NON_BLOCKING_LIMITATION | frozen runtime-hash gate fails closed on drift; contract binds the interpreter path |
| L04 | handoff | no operational entry calls `export_handoff/verify_handoff/apply_handoff` against the PRODUCTION ledger (tests only) | BLOCKING | `prodctl handoff-export` / `handoff-import` composing the frozen functions |
| L05 | assembly | no entry calls `assemble_production_campaign`; AWS records have no authenticated transport to the assembling host | BLOCKING | `prodctl assemble`: AWS ledger authenticated through the signed `aws_ledger_hash` + `aws_result_manifest_hash` |
| L06 | pre-launch | private key only on AWS; pubkey fingerprint frozen | ALREADY_CLOSED | unchanged |
| L07 | pre-launch | six thread variables | ALREADY_CLOSED (gate) | environment bound exactly in the service contract |
| L08 | any | a human can still invoke `production_launcher.py --produce` directly, bypassing ops accounting | NON_BLOCKING_LIMITATION | DETECTED: ledger continuity chain refuses any ledger mutation not produced by a sanctioned run |
| S01 | detached start | `--produce` runs in the foreground; daemon workers die with the parent; nothing survives session exit | BLOCKING | ONE systemd transient system service per run |
| S02 | detached start | no campaign-level singleton: two launchers can run on one ledger | BLOCKING | kernel `flock` campaign lock with bound owner identity |
| S03 | running | status needs an interactive session | BLOCKING (operability) | `prodctl status` from ledger + runtime dir + systemd |
| R01 | running | `main()` uses `run_production_cells(poll_timeout=3600)`; the cost basis is 8–11.5 CPU-h per single-core cell, so the first result arrives hours after start, `queue.Empty` escapes after 1 h and EVERY run dies | BLOCKING | sanctioned entry calls the frozen `run_production_cells(pf, poll_timeout=None)`; worker loss is detected by the supervisor instead |
| R02 | running | on a worker-reported failure (`ok=False`) the frozen scheduler `release()`s the reservation: the attempt's CPU is charged ZERO and the headroom is immediately re-admitted | BLOCKING | release is converted into a torn-attempt escrow reservation (never dropped); exact CPU charged at settlement |
| R03 | running | frozen protocol: "a SCIENTIFIC failure is NEVER retried — recorded and the campaign stops"; the frozen scheduler re-runs the failed cell at the next launch | BLOCKING | a worker-reported/malformed failure HALTS the campaign (recorded; pre-start refuses until adjudication) |
| R04 | running | exception paths after `inflight.pop` (validate/seal/write/commit-gate) leave an ORPHAN reservation | BLOCKING | settled by the recovery state machine |
| R05 | running | worker death (OOM/segfault) never returns a result; parent waits (forever with R01's fix) | BLOCKING | supervisor watchdog: live children < W while cell reservations open → WORKER_LOST → settle |
| R06 | running | attempt CPU above its reservation is invisible until commit | NON_BLOCKING_LIMITATION (frozen predictive semantics) | closed anyway: a shadow reservation tracks uncommitted measured run CPU |
| R07 | running | frozen ledger writes are not fsynced | NON_BLOCKING_LIMITATION | ext4 rename gives old-or-new; ops writes are fsynced; recovery tolerates a rolled-back ledger |
| R08 | running | protocol stop condition "free disk < 5 GiB" is not implemented | BLOCKING (governance) | supervisor stop + pre-start refusal |
| R09 | running | protocol stop condition "wall clock > 14 days" vs authorization `excluded_bindings` ("wall-clock projection is not a gate; the ONE binding limit is 4500 CPU-h") | OPEN_GOVERNANCE | NOT enforced (would contradict the production authorization); elapsed wall clock reported in status |
| R10 | running | launcher overhead CPU (preflight, imports, pool start) is never charged | NON_BLOCKING_LIMITATION | charged by run-level exact settlement |
| CA | crash A | before reservation | ALREADY_CLOSED | run CPU still settled exactly |
| CB | crash B | after reservation, before worker start → orphan reservation | BLOCKING (via RS01) | settlement |
| CC | crash C/J | parent SIGKILLed: daemon workers are orphaned, keep computing, then block forever on the queue | BLOCKING | cgroup kill (`KillMode=control-group`) + supervisor subreaper kill |
| CD | crash D | result computed, not written → orphan | covered by CB | settlement, retry |
| CE | crash E/F | `cells/.tmp-*` left behind (frozen cleanup runs only on exceptions) | BLOCKING (dirty tree, possible partial file) | quarantined outside the source tree, never read |
| CG | crash G | `cells/NNNN.json` renamed, ledger commit lost | BLOCKING | orphan result quarantined (never adopted), cell retried, CPU charged |
| CH | crash H | ledger finalize before reservation release | FALSE_POSITIVE | `commit()` pops and completes in ONE atomic write |
| CI | crash I | parent dies holding `PRODUCTION_LEDGER.json.lock` → every later op refuses after 30 s | BLOCKING | owner classification LIVE / DEAD / AMBIGUOUS (boot time, pid, process start time, cgroup) |
| CK | crash K | host reboot/power loss: transient unit gone, pids meaningless, cgroup CPU lost | BLOCKING | evidence hierarchy: supervisor final → systemd journal `CPU_USAGE_NSEC` → last fsynced shadow sample + physical tail bound |
| RS01 | restart | `draw()` refuses a cell with an open (orphan) reservation → admission stops at restart (deadlock) | BLOCKING | orphans closed at settlement, before admission |
| RS02 | restart | protocol "infrastructure failures retry at most twice per cell" not enforced | BLOCKING (governance) | torn-attempt counter per cell; 3rd torn attempt HALTS |
| RS03 | restart | pending = owned − completed | ALREADY_CLOSED | re-verified |
| RS04 | restart | completed cell never recomputed (`draw` refuses) | ALREADY_CLOSED | re-verified |
| RS05 | restart | a DELETED/replaced ledger silently resets the budget (`_read` returns an empty state) and re-opens all cells | BLOCKING | fsynced continuity chain outside the tree; monotonicity check |
| N01 | completion | relaunch after completion builds a pool and no-ops | NON_BLOCKING | `start` refuses by phase |
| H01 | handoff | export requires zero open reservations | ALREADY_CLOSED | ops keys settled first |
| H02 | handoff | torn/unattributed charges must reach Vultr | closed by design | charges land in `committed_cpu_h_by_role`, which the signed `aws_finalized_cpu_h`/`aws_ledger_hash` carry |
| H03 | handoff | `apply_handoff` writes `evidence/handoff_consumed.json` inside the Vultr tree | NON_BLOCKING | Vultr has no git gate; declared runtime state for VULTR only |
| H04 | handoff | Vultr has no git: `verify_handoff(approved_head=…)` needs a bound head | BLOCKING (entry) | contract binds the parent commit |
| V01 | Vultr | all crash/restart modes identical | closed by the same layer | |
| V02 | Vultr | Vultr before authenticated completion | ALREADY_CLOSED | + ops phase refusal |
| F01 | assembly | frozen assembler caps only Σ record CPU (omits torn/overhead charges) | NON_BLOCKING (report undercount) | ops assembler re-gates the GOVERNED totals and reconciles records + settlements |
| F02 | assembly | Phase-8 synthetic records | ALREADY_CLOSED (provenance firewall) | re-tested |
| P01 | post | restart after completion | closed | `start` refuses, assembly deterministic/idempotent |
