"""H1 synthetic observer-owned construction; never a caller-bytes signing API.

Fixture-owned facts/enrollment only. No real collector, baseline enrollment,
identity authentication, signer, key, clock or persistence is implemented here.
"""
from dataclasses import dataclass
import hashlib

import d2_ingress_wire as W


ENROLLMENT_FIELDS = frozenset(('guest_machine', 'guest_boot', 'runtime', 'policy'))
FACT_FIELDS = frozenset(('host_id', 'host_boot', 'service', 'interval_start_ms',
                        'interval_end_ms', 'coverage_complete', 'quiet', 'policy_stable'))
MAX_TICK_MS = 2**53 - 1


def digest(value):
    return type(value) is str and W.HEX64.fullmatch(value) is not None


def tick(value):
    return type(value) is int and 0 <= value <= MAX_TICK_MS


def canonical(value):
    import json
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('ascii')


@dataclass(frozen=True)
class Enrollment:
    guest_machine: str
    guest_boot: str
    runtime: str
    policy: str

    def __post_init__(self):
        if not all(digest(getattr(self, key)) for key in ENROLLMENT_FIELDS):
            raise ValueError('exact enrollment digest shapes required')

    def as_dict(self):
        return {key: getattr(self, key) for key in ENROLLMENT_FIELDS}


@dataclass(frozen=True)
class FixtureFacts:
    host_id: str
    host_boot: str
    service: str
    interval_start_ms: int
    interval_end_ms: int
    coverage_complete: bool
    quiet: bool
    policy_stable: bool

    def __post_init__(self):
        if (not all(digest(getattr(self, key)) for key in ('host_id', 'host_boot', 'service'))
                or not tick(self.interval_start_ms) or not tick(self.interval_end_ms)
                or self.interval_end_ms < self.interval_start_ms
                or any(type(getattr(self, key)) is not bool for key in
                       ('coverage_complete', 'quiet', 'policy_stable'))):
            raise ValueError('exact synthetic observer facts required')

    def as_dict(self):
        return {key: getattr(self, key) for key in FACT_FIELDS}


def parse_client_request(raw):
    """H1 request has only challenge and pre-enrolled guest/runtime comparison."""
    obj = W._document(raw, W.MAX_REQUEST_BYTES)
    W._header(obj, 'observer_request', {'protocol', 'kind', 'challenge', 'enrollment'})
    challenge = W._challenge(obj['challenge'])
    W._fields(obj['enrollment'], ENROLLMENT_FIELDS)
    try:
        enrollment = Enrollment(**obj['enrollment'])
    except ValueError as exc:
        raise W.IngressError('bad enrollment shape') from exc
    return challenge, enrollment


def client_request(outbound_h3, enrollment):
    """Wrap an M challenge with configured comparison labels; no host facts."""
    W.parse_observer_request(outbound_h3)
    if type(enrollment) is not Enrollment:
        raise ValueError('synthetic enrollment required')
    obj = W._document(outbound_h3, W.MAX_REQUEST_BYTES)
    obj['enrollment'] = enrollment.as_dict()
    raw = canonical(obj)
    parse_client_request(raw)
    return raw


def _fixture_response(client_raw, *, enrolled, facts, synthetic_only=False):
    """Construct unsigned bytes from fixture-owned inputs, never supplied payload."""
    if synthetic_only is not True:
        raise ValueError('explicit synthetic_only=True required')
    if type(enrolled) is not Enrollment or type(facts) is not FixtureFacts:
        raise ValueError('fixture-owned enrollment/facts required')
    challenge, compared = parse_client_request(client_raw)
    if compared != enrolled:
        raise W.IngressError('enrollment mismatch')
    # baseline_sha256 is echoed as a challenge binding, not accepted as host data.
    payload = dict(schema='P309_D2_SYNTHETIC_OBSERVER_FACTS/1',
                   enrollment=enrolled.as_dict(), facts=facts.as_dict())
    result = dict(schema=W.CHALLENGE_SCHEMA, session_id=challenge.session_id,
                  baseline_sha256=challenge.baseline_sha256, sequence=challenge.sequence,
                  nonce=challenge.nonce, previous_sha256=challenge.previous_sha256, payload=payload)
    return canonical(result)


def checkpoint(message, signature):
    """Unambiguous memory-only chaining; not a protected rollback anchor."""
    return hashlib.sha256(b'P309_D2_MEMORY_CHECKPOINT/1\0' + len(message).to_bytes(8, 'big') +
                          message + len(signature).to_bytes(8, 'big') + signature).hexdigest()
