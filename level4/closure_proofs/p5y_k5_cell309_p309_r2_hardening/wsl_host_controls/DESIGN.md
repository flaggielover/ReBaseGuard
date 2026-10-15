# WSL host controls — development proposal, 2026-10-15

Base: `657ec3da602b396835b17b93d9235d7ed18e2cb7`; accepted r2 reference remains
`501f48cb31fd3f80d5c6dd33f1eef6b8f01b2853`. Nothing here is a route approval.

## Choice and boundary

Three approaches were considered: change the r2 preflight directly; add more prose
to readiness; or implement a separate observation/evaluation layer. The third is
chosen: it makes Windows failure cases executable and reviewable without wiring
an unapproved WSL route into the launcher. The first would change accepted
semantics prematurely; the second would not exercise error handling.

User authorization covers private runtime preparation and target-free development.
No launch, freeze, grant, qualification, worker-tier drill, target evaluation,
process signalling, or power/update setting changes are included.

## Data flow

`collect_host_controls.ps1` performs two read-only Windows process snapshots and
reads power settings, reboot indicators, task/event-log coverage, boot identity,
wall time and the Windows unbiased interrupt clock. It emits JSON only. Names,
command lines, user names and machine identifiers are not emitted; identity
material is SHA-256 hashed. PID + creation time prevents PID reuse from being
treated as a stable process. CPU is seconds per wall second (one full logical
CPU = 1.0), never divided by the visible CPU count. New/disappeared processes and
unreadable observations remain explicit. All processes are conservatively
unattributed: there is no user-editable allowlist that can hide `vmmemWSL` or
other VM/container load. This can overcount this very WSL session, intentionally.
Windows PID 0 (System Idle Process) is excluded because it accounts for unused
CPU time; ordinary processes, including System and VM processes, remain included.

The bounded process sampler cannot see processes born and terminated between
snapshots, and CIM success cannot prove all protected processes were readable.
It therefore always reports visibility attestation as unknown. An accepted
implementation would need independently reviewed identity/classification and
event-backed process lifetime accounting, including guest/host deduplication.

`host_controls.py` is a pure, offline diagnostic evaluator. No subprocess, network,
signals, git/ref changes, durable claims, or automatic enforcement. Schema,
finite nonnegative numbers, timestamp freshness, process IDs, clock ordering,
coverage flags and continuity are validated. Unknowns refuse candidate checks.
Monitor diagnostics require a prior checkpoint and original baseline: both check
boot identity, suspend/clock discontinuity, interpreter and glibc changes, while
the previous checkpoint checks sample gaps. Baseline comparison accumulates
repeated sub-tolerance suspensions; it is NOT a durable anti-replay store.

## Existing thresholds retained

The constants are checked by AST against the untouched r2 `p309_host.DEFAULTS`:
4 CPUs, 8 decimal GB available RAM, 40 decimal GB storage, 60 s process sample,
start CPU fraction >0.05, monitor fraction >0.5, aggregate monitor fraction >1.0,
5 s suspend tolerance and 45 s monitor gap tolerance. Host and guest minima both
apply. Existing load-baseline/margin checks, Linux isolation, scratch validation,
NTP, cgroup accounting and unit controls are still required; this layer does not
replace them. No setting in the candidate may lower those accepted values.

Windows-specific additions (freshness limit, power policy interpretation,
event-log continuity and complete host visibility) are proposed stricter controls,
not accepted requirements. They cannot establish the 6 h or 31.5 h window merely
by a short successful sample. Process birth at start blocks; at monitor time
unknown/new activity also blocks in this prototype (stricter than r2's one-sample
grace). This difference requires review and is not silently asserted equivalent.

## AWS and WSL mapping — all pending approval

* `cloud_metadata_available` / instance identity: replace only after review with
  authenticated Windows host + boot + WSL guest identity and a protected bridge.
* `not_spot`: local custody and interruption-risk evidence; absence of AWS metadata
  is not evidence of non-preemptibility.
* `not_burstable`: effective guest quota plus dedicated host capacity, not just
  logical CPU visibility. Shared laptop scheduling does not establish this.
* `no_scheduled_maintenance`: update/reboot/task evidence plus an operator window
  and continuous monitoring; registry flags alone cannot establish no future work.
* `not_in_container`: WSL is detected as a container; an explicit reviewed route
  exception is needed. The original check is not disabled.

Every result, including a fully synthetic all-green example, has
`formal_admission=BLOCKED`, `qualification_authorized=false`,
`target_execution_authorized=false`, `route_accepted=false`. There is no override.
The original exactly-once guard, forbidden namespaces, immutable r1 references,
grant and freeze machinery remain byte-identical; synthetic tests check this
boundary without importing or invoking those entrypoints.

## Validation plan

Synthetic tests cover malformed/stale/future input, booleans and NaNs in numeric
fields, CPU thresholds/boundaries/aggregate load, process churn/reuse and denied
coverage, reboot/suspend/clock regression, update pending/unknown, changed runtime,
host/guest resource minima, unchanged r2 defaults/protected sources, no execution
authorization even with perfect synthetic input. Live collection is only a short
read-only development smoke. Private Python tests use bounded stdlib imports and
small multiprocessing children, not project evaluators or worker-tier drills.

Self-review: all unknown evidence remains blocking; no acceptance mechanism is
present; the candidate has no execution integration. An independent route review,
account/bridge isolation and durable runtime monitor are still outstanding.
