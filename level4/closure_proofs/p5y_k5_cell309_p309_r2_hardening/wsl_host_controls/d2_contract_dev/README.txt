First D2 pure-memory implementation slice; development/model use only
Base: 29a9b8a4db4b3376dafb195fc051083b9d964bc3; 2026-10-15

The limited rereview satisfies DR-01/DR-02 at contract level. The user separately
authorized D2 pure-memory protocol/state libraries and synthetic unit tests,
with additive code/evidence publication on an independent branch. That explicit
authorization does not cover service/endpoint/account/key/unit creation, host
queries, elevation, policy changes or actual P309 workloads. I1-I7 remain open.

Modules
1. d2_control_wire.py: strict, bounded H4 status/stop request parsing. UTF-8 JSON
   with duplicate/nonfinite/unknown-field rejection, fixed protocol, bounded
   request ID and opaque generation. No arbitrary command, unit, UID/PID, path,
   environment, property or start/arm/rearm/reset operation. Synthetic peer role
   context is separate from wire data and never claimed to be SO_PEERCRED proof.
2. d2_broker_model.py: pure in-memory generation/lifecycle reducer. Client dispatch
   handles status/stop only. Separate internal fixture functions can model
   ARMED/STARTING/RUNNING/cleanup/restart for tests; they are not a start API,
   administrative permit or OS effect. Immutable terminal history and a distinct
   restart-uncertainty guard prevent old history from proving current quiescence.

This first slice covers H4 policy/state only. It does not implement H1-H3/H5,
observer collection/signing, real peer authentication, sockets, activation,
privileged broker, persistent anchor, live watchdog or kernel/cgroup stop.
No existing launcher, monitor, Windows signer or earlier test is modified.

Explicit model budgets (development only, not accepted host thresholds)
- Control request raw UTF-8 bytes <=16384; exact fields protocol, request_id,
  operation and generation. Protocol is P309_DEV_BROKER_CONTROL/2.
- request_id: exactly32 lowercase hexadecimal characters. generation: null for
  read-only current status, otherwise exactly32 lowercase hexadecimal characters;
  stop requires non-null G. IDs are opaque comparison keys, not authority.
- Retain <=4096 distinct request IDs TOTAL, <=16 synthetic generation records,
  and count <=8192 accepted synthetic events (no event journal is persisted).
  Refuse/stop on budget exhaustion;
  never evict a fence or dedup entry to allow reuse. Exact behavior is documented
  and tested before any claim of a complete D2 library result.
- The budgets bound retained model entries, not Python allocator bytes or a
  supported 31.5-hour production window. Original CPU/memory/sample/suspend
  thresholds are untouched. No clock or resource reservation is introduced.
- Request-ID bindings are global across retained generations; changed-content
  reuse is refused. Status records bounded dedup bookkeeping but does not arm,
  launch or renew liveness. Budget exhaustion sets an unknown guard; well-formed
  stale-G inputs are checked before bookkeeping and do not consume that budget.
- Synthetic monitor instance labels are distinct from the broker epoch and are
  pinned into fixture generations. Monitor restart in the same broker epoch
  enters unknown and invalidates the old label. These labels are caller-created
  simulations, not measured PID/start-time/UID credentials or real enrollment.

Acceptance cases (actual execution results are recorded separately)
- Malformed/duplicate/nonfinite/unknown fields, oversized inputs and invalid IDs.
- Wrong synthetic peer role/instance or caller-asserted identity; R/U cannot
  control B; all public start/arm/rearm/reset attempts are refused.
- Same-G stop is irreversible and idempotent; receipt is not completed cleanup.
- Stop before fixture-start suppresses it; in-flight fixture-start completion
  after stop never yields RUNNING or successful start/continuation.
- STOPPED requires all synthetic proof predicates; incomplete or lost proof
  remains cleanup-pending/unknown and cannot create an OS completion claim.
- Old-G queued request/cached reply is checked for staleness before dedup; it
  cannot affect fresh G. Changed-content request-ID reuse is refused.
- Finite model interleavings exercise start/stop/completion orderings; no real
  concurrent kernel-action guarantee is claimed by a pure reducer.
- Restart keeps old terminal history immutable while a new epoch remains
  RECOVERY_UNKNOWN; reconnect or history lookup cannot rearm or clear it.
- Contradictory current-instance identity after STOPPED preserves terminal
  history but sets an unknown guard; old history is not current quiescence.
- Budget exhaustion retains fences and remains fail-closed.
- Every result is explicitly synthetic/model-only with all formal authority
  false. No model effect is passed to an OS executor.

Authorized verification scope
Coordinator verification uses only new stdlib unittest suites in Cloud Python,
with synthetic data and no
keys, subprocess helpers, host queries, workloads, filesystem state/persistence,
network, privileged interfaces or deployment. A normal test-runner process and
temporary test log files are development tooling, not P309 execution. Record
exact code hashes/test IDs/results; any later private-Python check is separate.
LOCAL_VALIDATION.txt scopes separate private-Python verification of these same
new pure suites. No historical rerun is needed unless inputs actually change.

Unchanged boundaries
I1-I7 remain OPEN_RETAINED. Contract/model tests cannot establish actual Linux/
Windows identity, ACLs, event completeness, unit enforcement, durability or route
acceptance. No install script, host mutation, new distro/account/service/key,
elevation, trace, safety sample, drill, freeze/grant, qualification or target.
The original review and all later records remain immutable historical evidence.
