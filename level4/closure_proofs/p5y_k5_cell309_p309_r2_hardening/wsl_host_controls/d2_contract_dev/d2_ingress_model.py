"""One-challenge synthetic H3 staging model; no verification/continuation API.

Private factory is fixture setup, NOT enrollment or a real challenge issuer.
An unsigned/invalid-signature-shaped response can reach UNVERIFIED: this is not
acceptance. A future separately reviewed verifier must own subsequent decisions.
"""
from dataclasses import dataclass, replace

from d2_control_wire import valid_id
import d2_ingress_wire as W


@dataclass(frozen=True)
class SyntheticRelay:
    role: str
    instance: str


@dataclass(frozen=True)
class IngressModel:
    generation: str
    relay_instance: str
    outstanding: W.Challenge
    state: str = 'AWAITING_RESPONSE'
    stop_latched: bool = False
    staged: W.UnverifiedObservation | None = None
    failure: str | None = None

    def diagnostic(self):
        return dict(scope='SYNTHETIC_ONE_CHALLENGE_H3_STAGING_ONLY',
                    state=self.state, associated_generation=self.generation,
                    stop_requested=self.stop_latched, failure=self.failure,
                    staged_unverified=self.staged is not None,
                    actual_peer_authenticated=False, signature_verified=False,
                    host_facts_validated=False, observation_accepted=False,
                    continuation_authorized=False, actual_os_effects=False,
                    formal_admission='BLOCKED', route_accepted=False,
                    deployment_authorized=False, execution_authorized=False,
                    qualification_authorized=False, target_execution_authorized=False)

    def _fail(self, code):
        # Never retain attacker bytes after failure. Keep fixed binding/reason.
        return replace(self, state='TERMINAL_STOP', stop_latched=True,
                       staged=None, failure=code)

    def receive(self, raw, *, peer):
        """Pure reducer; serial snapshots only, not an atomic live monitor."""
        if self.stop_latched:
            return self
        if (type(peer) is not SyntheticRelay or type(peer.role) is not str or
                peer.role != 'p309-relay' or type(peer.instance) is not str or
                peer.instance != self.relay_instance):
            return self._fail('PEER_REFUSED')
        if self.state != 'AWAITING_RESPONSE':
            return self._fail('UNEXPECTED_ADDITIONAL_RESPONSE')
        try:
            parsed = W.parse_relay_message(raw)
        except W.IngressError:
            return self._fail('BAD_MESSAGE')
        if type(parsed) is W.TransportFailure:
            return self._fail('TRANSPORT_' + parsed.reason)
        if parsed.challenge != self.outstanding:
            return self._fail('CHALLENGE_MISMATCH')
        return replace(self, state='UNVERIFIED', staged=parsed)

    def transport_lost(self):
        """Synthetic local event, associated with this fixture's generation."""
        return self if self.stop_latched else self._fail('LOCAL_TRANSPORT_LOST')


def _fixture_open(request_raw, *, generation, relay_instance, synthetic_only=False):
    """No random token, trust bootstrap, key, enrolled identity or OS effect."""
    if synthetic_only is not True:
        raise ValueError('explicit synthetic_only=True required')
    if not valid_id(generation):
        raise ValueError('synthetic generation shape required')
    if (type(relay_instance) is not str or not 0 < len(relay_instance) <= 128 or
            not relay_instance.isascii()):
        raise ValueError('bounded synthetic relay label required')
    return IngressModel(generation, relay_instance, W.parse_observer_request(request_raw))
