"""Target-free, immutable session reducer with public verification and fake time.

All enrollment/baseline/time/facts are synthetic fixture inputs. Accepted MODEL
observations NEVER authorize actual continuation. No I/O, keys or OS effects.
"""
from dataclasses import dataclass, replace

import d2_ingress_model as I
import d2_ingress_wire as W
import d2_observer as O
from d2_signature import PublicNumbers

MAX_RECORDS = 4096
RESPONSE_LIMIT_MS = 105000  # unchanged 60s sample +45s gap allowance
MIN_INTERVAL_MS = 60000


@dataclass(frozen=True)
class Session:
    enrollment: O.Enrollment
    host_identity: tuple[str, str, str]
    public: PublicNumbers
    pin: str
    session_id: str
    baseline_sha256: str
    generation: str
    relay_instance: str
    head: str = '0' * 64
    sequence: int = 1
    issued_nonces: tuple[str, ...] = ()
    pending: I.IngressModel | None = None
    issued_ms: int | None = None
    last_tick_ms: int = 0
    liveness_anchor_ms: int = 0
    previous_interval_end_ms: int | None = None
    terminal: bool = False
    reason: str | None = None
    model_observations: int = 0

    def diagnostic(self):
        return dict(scope='SYNTHETIC_D2_MEMORY_SESSION_ONLY', sequence=self.sequence,
                    generation=self.generation, terminal=self.terminal, reason=self.reason,
                    stop_requested=self.terminal, model_observations=self.model_observations,
                    checkpoint=self.head, challenge_outstanding=self.pending is not None,
                    actual_peer_authenticated=False, trusted_enrollment=False,
                    actual_host_facts_validated=False, observation_accepted=False,
                    continuation_authorized=False, actual_os_effects=False,
                    formal_admission='BLOCKED', route_accepted=False,
                    deployment_authorized=False, execution_authorized=False,
                    qualification_authorized=False, target_execution_authorized=False)

    def _fail(self, reason):
        return self if self.terminal else replace(self, terminal=True, reason=reason,
                                                 pending=None, issued_ms=None)

    def _time_ok(self, now_ms):
        return O.tick(now_ms) and now_ms >= self.last_tick_ms

    def request(self, nonce, *, now_ms):
        """Synthetic fixture caller supplies nonce/fake time; no entropy/clock read."""
        if self.terminal:
            return self, None
        checked = self.tick(now_ms=now_ms)
        if checked.terminal:
            return checked, None
        if self.pending is not None:
            return self._fail('OUTSTANDING_REQUEST'), None
        if len(self.issued_nonces) >= MAX_RECORDS or self.sequence > MAX_RECORDS:
            return self._fail('SESSION_BUDGET_EXHAUSTED'), None
        if not O.digest(nonce) or nonce in self.issued_nonces:
            return self._fail('NONCE_INVALID_OR_REUSED'), None
        obj = dict(protocol=W.PROTOCOL, kind='observer_request', challenge=dict(
            schema=W.CHALLENGE_SCHEMA, session_id=self.session_id,
            baseline_sha256=self.baseline_sha256, sequence=self.sequence,
            nonce=nonce, previous_sha256=self.head))
        raw = O.canonical(obj)
        pending = I._fixture_open(raw, generation=self.generation,
                                  relay_instance=self.relay_instance, synthetic_only=True)
        return replace(self, pending=pending, issued_ms=now_ms, last_tick_ms=now_ms,
                       issued_nonces=self.issued_nonces + (nonce,)), raw

    def tick(self, *, now_ms):
        """Fake-time loss/timeout transition; no actual timer/watchdog is started."""
        if self.terminal:
            return self
        if not self._time_ok(now_ms):
            return self._fail('CLOCK_INVALID')
        # Response and observation liveness are independent deadlines. A late
        # challenge cannot replace the anchor of the last accepted observation
        # or add another105s of grace. Both checks also run after verification.
        if self.pending is not None and now_ms - self.issued_ms > RESPONSE_LIMIT_MS:
            return self._fail('RESPONSE_TIMEOUT')
        if now_ms - self.liveness_anchor_ms > RESPONSE_LIMIT_MS:
            return self._fail('MONITOR_GAP')
        return replace(self, last_tick_ms=now_ms)

    def transport_lost(self):
        return self._fail('TRANSPORT_LOST')

    def receive(self, raw, *, peer, now_ms, completed_ms):
        if self.terminal:
            return self
        checked = self.tick(now_ms=now_ms)
        if checked.terminal:
            return checked
        if self.pending is None:
            return self._fail('NO_OUTSTANDING_CHALLENGE')
        ingress = self.pending.receive(raw, peer=peer)
        if ingress.stop_latched:
            return self._fail(ingress.failure)
        staged = ingress.staged
        try:
            if self.public.fingerprint() != self.pin:
                return self._fail('PUBLIC_PIN_MISMATCH')
            if not self.public.verify(staged.message, staged.signature):
                return self._fail('SIGNATURE_REFUSED')
        except Exception:
            return self._fail('VERIFICATION_ERROR')
        # Fake post-verification time must be monotonic and inside original
        # challenge deadline. Verification never grants extra time.
        if not O.tick(completed_ms) or completed_ms < now_ms:
            return self._fail('CLOCK_INVALID')
        checked = checked.tick(now_ms=completed_ms)
        if checked.terminal:
            return checked
        doc = W._document(staged.message, W.MAX_MESSAGE_BYTES)
        payload = doc['payload']
        try:
            W._fields(payload, {'schema', 'enrollment', 'facts'})
            if payload['schema'] != 'P309_D2_SYNTHETIC_OBSERVER_FACTS/1':
                raise ValueError('wrong facts schema')
            W._fields(payload['enrollment'], O.ENROLLMENT_FIELDS)
            W._fields(payload['facts'], O.FACT_FIELDS)
            enrollment = O.Enrollment(**payload['enrollment'])
            facts = O.FixtureFacts(**payload['facts'])
        except (ValueError, TypeError):
            return self._fail('FACTS_SHAPE_REFUSED')
        if enrollment != self.enrollment:
            return self._fail('ENROLLMENT_CHANGED')
        if (facts.host_id, facts.host_boot, facts.service) != self.host_identity:
            return self._fail('HOST_IDENTITY_CHANGED')
        duration = facts.interval_end_ms - facts.interval_start_ms
        if not MIN_INTERVAL_MS <= duration <= RESPONSE_LIMIT_MS:
            return self._fail('INTERVAL_INVALID')
        if (facts.interval_start_ms < self.issued_ms or facts.interval_end_ms > now_ms
                or completed_ms - facts.interval_end_ms > RESPONSE_LIMIT_MS):
            return self._fail('INTERVAL_NOT_CURRENT')
        if (self.previous_interval_end_ms is not None and
                not 0 <= facts.interval_start_ms - self.previous_interval_end_ms <= RESPONSE_LIMIT_MS):
            return self._fail('INTERVAL_GAP')
        if not (facts.coverage_complete and facts.quiet and facts.policy_stable):
            return self._fail('OBSERVATION_UNSAFE_OR_UNKNOWN')
        return replace(self, head=O.checkpoint(staged.message, staged.signature),
                       sequence=self.sequence + 1, pending=None, issued_ms=None,
                       last_tick_ms=completed_ms, liveness_anchor_ms=completed_ms,
                       previous_interval_end_ms=facts.interval_end_ms,
                       model_observations=self.model_observations + 1)


def _fixture_session(*, enrollment, host_identity, public, pin, session_id,
                     baseline_sha256, generation, relay_instance, now_ms=0,
                     synthetic_only=False):
    if synthetic_only is not True:
        raise ValueError('explicit synthetic_only=True required')
    if (type(enrollment) is not O.Enrollment or type(public) is not PublicNumbers or
            type(host_identity) is not tuple or len(host_identity) != 3 or
            not all(O.digest(v) for v in host_identity) or
            not all(O.digest(v) for v in (pin, session_id, baseline_sha256)) or not O.tick(now_ms)):
        raise ValueError('exact synthetic bindings/public pin/fake time required')
    # Validate G and relay bounds through the existing fixture factory.
    dummy = O.canonical(dict(protocol=W.PROTOCOL, kind='observer_request', challenge=dict(
        schema=W.CHALLENGE_SCHEMA, session_id=session_id, baseline_sha256=baseline_sha256,
        sequence=1, nonce='0' * 64, previous_sha256='0' * 64)))
    I._fixture_open(dummy, generation=generation, relay_instance=relay_instance, synthetic_only=True)
    return Session(enrollment, host_identity, public, pin, session_id, baseline_sha256,
                   generation, relay_instance, last_tick_ms=now_ms, liveness_anchor_ms=now_ms)
