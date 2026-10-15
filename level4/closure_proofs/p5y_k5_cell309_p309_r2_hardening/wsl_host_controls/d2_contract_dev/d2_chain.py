"""Pure immutable D2 session->generation-bound stop composition, never an actor.

No queue worker, timer, executor or real safety path. Synchronous verification
can block its caller; independent enforcement and durable fencing remain I6.
"""
from dataclasses import dataclass, replace
import hashlib

import d2_broker_model as B
from d2_control_wire import PROTOCOL
import d2_observer as O
from d2_session import Session


@dataclass(frozen=True)
class Chain:
    session: Session
    broker: B.BrokerModel
    monitor: B.SyntheticPeer
    stop_receipt: B.Receipt | None = None

    def _sync(self):
        session = self.session
        current = self.broker._current()
        # Historical or different-generation state never binds this session to
        # a replacement generation or renews its authority.
        if not session.terminal and (self.broker.epoch_unknown or
                current is None or current.generation != session.generation or
                current.stop_latched or current.state in B.TERMINAL):
            session = session._fail('BROKER_NOT_ACTIVE_FOR_SESSION')
        if not session.terminal:
            return replace(self, session=session)
        request_id = hashlib.sha256(('D2_SESSION_STOP/1:' + session.session_id + ':' +
                                    session.generation).encode('ascii')).hexdigest()[:32]
        raw = O.canonical(dict(protocol=PROTOCOL, request_id=request_id,
                               operation='stop', generation=session.generation))
        outcome = self.broker.dispatch(raw, peer=self.monitor)
        return replace(self, session=session, broker=outcome.model, stop_receipt=outcome.receipt)

    def request(self, nonce, *, now_ms):
        chain = self._sync()
        session, raw = chain.session.request(nonce, now_ms=now_ms)
        return replace(chain, session=session)._sync(), raw

    def receive(self, raw, *, peer, now_ms, completed_ms):
        chain = self._sync()
        session = chain.session.receive(raw, peer=peer, now_ms=now_ms, completed_ms=completed_ms)
        return replace(chain, session=session)._sync()

    def tick(self, *, now_ms):
        chain = self._sync()
        return replace(chain, session=chain.session.tick(now_ms=now_ms))._sync()

    def transport_lost(self):
        return replace(self, session=self.session.transport_lost())._sync()

    def _fixture_event(self, event, **kwargs):
        broker = B._fixture_event(self.broker, event, **kwargs)
        return replace(self, broker=broker)._sync()

    def diagnostic(self):
        return dict(scope='SYNTHETIC_D2_SESSION_BROKER_COMPOSITION_ONLY',
                    session=self.session.diagnostic(),
                    stop_receipt=self.stop_receipt.as_dict() if self.stop_receipt else None,
                    actual_os_effects=False, actual_peer_authenticated=False,
                    formal_admission='BLOCKED', route_accepted=False,
                    deployment_authorized=False, execution_authorized=False,
                    qualification_authorized=False, target_execution_authorized=False)


def _fixture_chain(session, broker, *, synthetic_only=False):
    if synthetic_only is not True or type(session) is not Session or type(broker) is not B.BrokerModel:
        raise ValueError('explicit synthetic session/broker fixture required')
    monitor = B.SyntheticPeer('p309-monitor', broker.epoch, broker.monitor_instance)
    return Chain(session, broker, monitor)._sync()
