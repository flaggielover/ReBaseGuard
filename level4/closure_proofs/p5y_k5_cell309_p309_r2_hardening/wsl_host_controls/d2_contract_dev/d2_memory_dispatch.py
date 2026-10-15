"""Bounded, in-process dispatcher for the synthetic H4 model only.

No transport, real credentials, callbacks, OS executor or persistent store. The
lock serializes snapshot publication; it is NOT an independent safety watchdog.
"""
from collections import deque
from dataclasses import dataclass
import threading

import d2_broker_model as M
from d2_control_wire import MAX_REQUEST_BYTES

MAX_PENDING = 64
MAX_TICKET_IDS = 65536
MAX_ROLE_CHARS = 32
MAX_INSTANCE_CHARS = 128


class SubmissionError(ValueError):
    pass


@dataclass(frozen=True)
class Ticket:
    sequence: int


@dataclass(frozen=True)
class _Pending:
    ticket: Ticket
    raw: bytes
    peer: M.SyntheticPeer


@dataclass(frozen=True)
class Completion:
    ticket: Ticket
    revision: int
    receipt: M.Receipt

    def as_dict(self):
        return dict(ticket=self.ticket.sequence, revision=self.revision,
                    scope='SYNTHETIC_IN_PROCESS_MEMORY_DISPATCH_ONLY',
                    receipt=self.receipt.as_dict(), actual_os_effects=False,
                    actual_peer_authenticated=False, formal_admission='BLOCKED',
                    route_accepted=False, deployment_authorized=False, execution_authorized=False,
                    qualification_authorized=False, target_execution_authorized=False)


class MemoryDispatch:
    """Single-process serial publication, not host isolation or durable fencing.

    submit copies bounded primitive synthetic peer metadata. dispatch_next
    checks synthetic identity/protocol through the model at DISPATCH time and atomically
    publishes its returned snapshot. No caller snapshot or callable is accepted.
    """
    def __init__(self, *, synthetic_only=False):
        if synthetic_only is not True:
            raise ValueError('explicit synthetic_only=True required')
        self._lock = threading.RLock()
        self._model = M.BrokerModel.new(synthetic_only=True)
        self._pending = deque()
        self._next_ticket = 1
        self._revision = 0
        self._closed = False

    def _publish(self, model):
        if model != self._model:
            self._model = model
            self._revision += 1

    def snapshot(self):
        with self._lock:
            return self._model

    def stats(self):
        with self._lock:
            return dict(pending=len(self._pending), next_ticket=self._next_ticket,
                        revision=self._revision, closed=self._closed,
                        scope='SYNTHETIC_IN_PROCESS_MEMORY_DISPATCH_ONLY',
                        formal_admission='BLOCKED', route_accepted=False, deployment_authorized=False,
                        execution_authorized=False, qualification_authorized=False,
                        target_execution_authorized=False)

    def submit(self, raw, *, peer):
        if type(raw) is not bytes or not 0 < len(raw) <= MAX_REQUEST_BYTES:
            raise SubmissionError('invalid bounded raw bytes')
        if (type(peer) is not M.SyntheticPeer or type(peer.role) is not str or
                not 0 < len(peer.role) <= MAX_ROLE_CHARS or not peer.role.isascii() or
                type(peer.monitor_epoch) is not int or not 0 < peer.monitor_epoch <= MAX_TICKET_IDS or
                type(peer.monitor_instance) is not str or
                not 0 < len(peer.monitor_instance) <= MAX_INSTANCE_CHARS or not peer.monitor_instance.isascii()):
            raise SubmissionError('bounded primitive synthetic peer metadata required')
        frozen_peer = M.SyntheticPeer(peer.role, peer.monitor_epoch, peer.monitor_instance)
        with self._lock:
            if self._closed:
                raise SubmissionError('dispatcher closed')
            if len(self._pending) >= MAX_PENDING:
                raise SubmissionError('pending queue full; no item evicted')
            if self._next_ticket > MAX_TICKET_IDS:
                self._closed = True
                self._publish(M._fixture_event(self._model, 'recovery_failure'))
                raise SubmissionError('ticket budget exhausted; dispatcher terminal')
            ticket = Ticket(self._next_ticket)
            self._next_ticket += 1
            self._pending.append(_Pending(ticket, raw, frozen_peer))
            return ticket

    def dispatch_next(self):
        with self._lock:
            if not self._pending:
                return None
            item = self._pending[0]
            # No parse-result/cache/snapshot captured at submission is trusted.
            # Unexpected calculation failure retains the item for a refusal
            # after latching unknown; it never reports a completed stop.
            try:
                outcome = self._model.dispatch(item.raw, peer=item.peer)
            except Exception:
                self._closed = True
                self._publish(M._fixture_event(self._model, 'recovery_failure'))
                raise
            self._publish(outcome.model)
            self._pending.popleft()
            return Completion(item.ticket, self._revision, outcome.receipt)

    def close(self):
        with self._lock:
            if not self._closed:
                self._closed = True
                self._publish(M._fixture_event(self._model, 'recovery_failure'))
            # Retain queued bytes/ticket order for explicit terminal refusals.
            return self.stats()

    def _fixture_prepare(self):
        """Internal synthetic setup, not a client start/rearm API."""
        with self._lock:
            if self._closed:
                raise SubmissionError('closed fixture cannot rearm')
            self._publish(M._fixture_prepare(self._model))
            return self._model

    def _fixture_event(self, event, *, generation=None, proof=None, identity_matches=True):
        """Only fixed model events; no supplied callable, executor or OS effect."""
        with self._lock:
            if self._closed:
                raise SubmissionError('closed fixture cannot advance')
            self._publish(M._fixture_event(self._model, event, generation=generation,
                                          proof=proof, identity_matches=identity_matches))
            return self._model
