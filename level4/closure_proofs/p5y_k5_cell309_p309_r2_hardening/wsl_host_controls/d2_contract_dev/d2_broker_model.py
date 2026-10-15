"""Immutable synthetic H4/lifecycle reference model. NO real authority or I/O.

dispatch accepts bytes and synthetic role metadata, returning a new snapshot and
model receipt. Private fixture functions model internal lifecycle events only.
There is no callback, executor, persistence, socket, credential query or start API.
"""
from dataclasses import dataclass, replace
from enum import Enum

from d2_control_wire import parse_request, WireError

MAX_REQUEST_IDS = 4096
MAX_GENERATIONS = 16
MAX_EVENTS = 8192


class State(str, Enum):
    UNARMED = 'UNARMED'
    ARMED = 'ARMED'
    STARTING = 'STARTING'
    RUNNING = 'RUNNING'
    STOP_REQUESTED = 'STOP_REQUESTED'
    CLEANUP_PENDING = 'CLEANUP_PENDING'
    STOPPED = 'STOPPED'
    RECOVERY_UNKNOWN = 'RECOVERY_UNKNOWN'


TERMINAL = frozenset((State.STOPPED, State.RECOVERY_UNKNOWN))


@dataclass(frozen=True)
class SyntheticPeer:
    """Caller-constructed simulation, NEVER authenticated kernel credentials."""
    role: str
    monitor_epoch: int
    monitor_instance: str = ''


@dataclass(frozen=True)
class _Generation:
    generation: str
    monitor_instance: str = ''
    state: State = State.ARMED
    stop_latched: bool = False
    permit_consumed: bool = False
    start_pending: bool = False
    dispatch_issued: bool = False
    instance_established: bool = False
    start_suppressed: bool = False
    cleanup_confirmed: bool = False


@dataclass(frozen=True)
class _Binding:
    request_id: str
    fingerprint: str


@dataclass(frozen=True)
class Receipt:
    code: str
    epoch: int
    generation: str | None
    state: State | None
    stop_requested: bool = False
    cleanup_confirmed: bool = False
    duplicate: bool = False
    historical_state: State | None = None

    def as_dict(self):
        return dict(code=self.code, epoch=self.epoch, generation=self.generation,
                    state=self.state.value if self.state else None,
                    historical_state=self.historical_state.value if self.historical_state else None,
                    stop_requested=self.stop_requested, cleanup_confirmed=self.cleanup_confirmed,
                    duplicate=self.duplicate, scope='SYNTHETIC_PURE_MEMORY_MODEL_ONLY',
                    actual_peer_authenticated=False, actual_os_effects=False,
                    formal_admission='BLOCKED', route_accepted=False, deployment_authorized=False,
                    execution_authorized=False, qualification_authorized=False,
                    target_execution_authorized=False)


@dataclass(frozen=True)
class Outcome:
    model: 'BrokerModel'
    receipt: Receipt


@dataclass(frozen=True)
class BrokerModel:
    """Reference snapshot, not an atomic shared store or a privilege boundary.

    Use new(synthetic_only=True). Serial dispatch orders/interleavings can be
    simulated; publishing snapshots in a real concurrent controller is NOT
    implemented. Every state, peer and cleanup predicate here is synthetic.
    """
    epoch: int = 1
    monitor_counter: int = 1
    monitor_instance: str = 'synthetic-monitor-1'
    current_id: str | None = None
    generations: tuple[_Generation, ...] = ()
    bindings: tuple[_Binding, ...] = ()
    event_count: int = 0
    epoch_unknown: bool = False
    budget_exhausted: bool = False
    generation_counter: int = 0

    @classmethod
    def new(cls, *, synthetic_only=False):
        if synthetic_only is not True:
            raise ValueError('explicit synthetic_only=True required')
        return cls()

    def _current(self):
        return next((g for g in self.generations if g.generation == self.current_id), None)

    def _with_generation(self, generation):
        return replace(self, generations=tuple(
            generation if old.generation == generation.generation else old
            for old in self.generations))

    def _receipt(self, code, *, duplicate=False, requested=None, hide_state=False):
        g = self._current()
        state = State.RECOVERY_UNKNOWN if self.epoch_unknown else (g.state if g else State.UNARMED)
        return Receipt(code, self.epoch, requested if hide_state else self.current_id,
                       None if hide_state else state,
                       stop_requested=False if hide_state else (self.epoch_unknown or bool(g and g.stop_latched)),
                       cleanup_confirmed=not hide_state and not self.epoch_unknown and bool(g and g.cleanup_confirmed),
                       duplicate=duplicate,
                       historical_state=g.state if not hide_state and self.epoch_unknown and g else None)

    def _unknown(self, *, exhausted=False):
        model = replace(self, epoch_unknown=True,
                        budget_exhausted=self.budget_exhausted or exhausted)
        g = model._current()
        if g is not None and g.state not in TERMINAL:
            model = model._with_generation(replace(g, state=State.RECOVERY_UNKNOWN, stop_latched=True))
        return model

    def dispatch(self, raw, *, peer):
        """Only public client surface. Never accepts caller instance/OS inputs."""
        if (type(peer) is not SyntheticPeer or type(peer.role) is not str or peer.role != 'p309-monitor' or
                type(peer.monitor_epoch) is not int or peer.monitor_epoch != self.epoch or
                type(peer.monitor_instance) is not str or peer.monitor_instance != self.monitor_instance):
            return Outcome(self, self._receipt('PEER_REFUSED', hide_state=True))
        try:
            request = parse_request(raw)
        except WireError:
            return Outcome(self, self._receipt('BAD_REQUEST', hide_state=True))
        # Compare generation before looking up ANY cached/deduplicated request.
        if request.generation is not None and request.generation != self.current_id:
            return Outcome(self, self._receipt('STALE_GENERATION', requested=request.generation, hide_state=True))
        if self.epoch_unknown:
            return Outcome(self, self._receipt('RECOVERY_UNKNOWN'))
        fingerprint = request.fingerprint()
        prior = next((b for b in self.bindings if b.request_id == request.request_id), None)
        if prior is not None and prior.fingerprint != fingerprint:
            return Outcome(self, self._receipt('REQUEST_ID_REUSED'))
        duplicate = prior is not None
        if not duplicate and (len(self.bindings) >= MAX_REQUEST_IDS or self.event_count >= MAX_EVENTS):
            model = self._unknown(exhausted=True)
            return Outcome(model, model._receipt('MODEL_BUDGET_EXHAUSTED'))
        model = self
        if not duplicate:
            model = replace(model, bindings=model.bindings + (_Binding(request.request_id, fingerprint),),
                            event_count=model.event_count + 1)
        if request.operation == 'status':
            return Outcome(model, model._receipt('OK', duplicate=duplicate))
        g = model._current()
        if g is None:  # Defensive; non-null stop was already generation-checked.
            return Outcome(model, model._receipt('STALE_GENERATION', hide_state=True))
        if g.state not in TERMINAL:
            g = _latch(g)
            model = model._with_generation(g)
        return Outcome(model, model._receipt('STOPPED_MODEL' if g.state == State.STOPPED else 'STOP_REQUESTED_MODEL',
                                             duplicate=duplicate))


def _latch(g):
    if g.state in TERMINAL:
        return g
    suppressed = not g.dispatch_issued
    state = State.CLEANUP_PENDING if g.state == State.CLEANUP_PENDING else State.STOP_REQUESTED
    return replace(g, state=state, stop_latched=True, permit_consumed=True,
                   start_pending=g.start_pending if not suppressed else False,
                   start_suppressed=g.start_suppressed or suppressed)


@dataclass(frozen=True)
class _SyntheticCleanup:
    """Private fixture predicates. Wire requests cannot supply or invoke these."""
    identity_matches: bool
    unit_exit: bool
    cgroup_empty: bool
    reaped: bool
    no_inflight_operations: bool
    handles_closed: bool
    acknowledged: bool

    def __post_init__(self):
        if any(type(v) is not bool for v in vars(self).values()):
            raise ValueError('synthetic proof predicates must be booleans')

    def complete(self):
        return all(vars(self).values())


def _fixture_prepare(model):
    """Synthetic setup only; NO client/admin/start permission or OS action."""
    current = model._current()
    if model.epoch_unknown or (current and current.state != State.STOPPED):
        raise ValueError('fixture generation cannot be prepared from this state')
    if len(model.generations) >= MAX_GENERATIONS or model.event_count >= MAX_EVENTS:
        return model._unknown(exhausted=True)
    counter = model.generation_counter + 1
    generation = _Generation(format(counter, '032x'), monitor_instance=model.monitor_instance)
    # Deterministic fixture ID/instance label, never production entropy/authentication.
    return replace(model, current_id=generation.generation, generations=model.generations + (generation,),
                   generation_counter=counter, event_count=model.event_count + 1)


def _fixture_event(model, event, *, generation=None, proof=None, identity_matches=True):
    """Internal typed fixture path for pure model traces; not the H4 API.

    No external event executor exists. No event touches a unit, manager, process,
    credential, filesystem, clock, key, socket or persistent state.
    """
    events = ('begin_start', 'dispatch_start', 'start_completed', 'begin_cleanup',
              'cleanup_proof', 'owned_exit', 'restart', 'monitor_restart', 'recovery_failure')
    if type(event) is not str or event not in events or type(identity_matches) is not bool:
        raise ValueError('invalid fixture event')
    if event in ('restart', 'monitor_restart', 'recovery_failure'):
        if model.event_count >= MAX_EVENTS:
            return model._unknown(exhausted=True)
        result = model._unknown()
        counter = result.monitor_counter + (event in ('restart', 'monitor_restart'))
        return replace(result, epoch=result.epoch + (event == 'restart'),
                       monitor_counter=counter, monitor_instance='synthetic-monitor-%d' % counter,
                       event_count=result.event_count + 1)
    # A delayed old-generation internal completion also cannot target a new G.
    if generation != model.current_id or model.epoch_unknown:
        return model
    g = model._current()
    if g is None:
        return model
    if g.state in TERMINAL:
        # Preserve the old terminal record, but contradictory CURRENT-instance
        # facts invalidate current-epoch quiescence. A stale-G event above has
        # no such effect on a newer generation.
        contradiction = ((event == 'start_completed' and not identity_matches) or
                         (event == 'cleanup_proof' and type(proof) is _SyntheticCleanup
                          and not proof.identity_matches))
        return model._unknown() if contradiction else model
    if model.event_count >= MAX_EVENTS:
        return model._unknown(exhausted=True)
    if event == 'begin_start':
        if g.state != State.ARMED or g.stop_latched or g.permit_consumed:
            return model
        g = replace(g, state=State.STARTING, permit_consumed=True, start_pending=True)
    elif event == 'dispatch_start':
        if g.state != State.STARTING or g.stop_latched or g.dispatch_issued or not g.start_pending:
            return model
        g = replace(g, dispatch_issued=True)
    elif event == 'start_completed':
        if not g.dispatch_issued or not g.start_pending or not identity_matches:
            return model._unknown()
        g = replace(g, start_pending=False, instance_established=True,
                    state=State.CLEANUP_PENDING if g.stop_latched else State.RUNNING)
    elif event == 'begin_cleanup':
        if g.state != State.STOP_REQUESTED:
            return model
        g = replace(g, state=State.CLEANUP_PENDING)
    elif event == 'owned_exit':
        if g.state != State.RUNNING:
            return model
        g = replace(_latch(g), state=State.CLEANUP_PENDING)
    elif event == 'cleanup_proof':
        if type(proof) is not _SyntheticCleanup:
            raise ValueError('synthetic cleanup proof required')
        if g.state != State.CLEANUP_PENDING:
            return model
        if not proof.identity_matches:
            return model._unknown()
        # Caller/fixture predicates cannot override the model's known in-flight start.
        if g.start_pending or (g.dispatch_issued and not g.instance_established) or not proof.complete():
            return model
        g = replace(g, state=State.STOPPED, stop_latched=True, cleanup_confirmed=True)
    return replace(model._with_generation(g), event_count=model.event_count + 1)
