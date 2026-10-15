"""H3 development byte shapes only; signature-shaped bytes remain UNVERIFIED.

No cryptography, collector, clock, credential, transport, broker or OS I/O.
The inner challenge/envelope shapes follow the existing DEV_CHALLENGE/1 format.
The new H3 wrapper is an isolated development encoding, not an installed API.
"""
import base64
from dataclasses import dataclass
import json
import math
import re

PROTOCOL = 'P309_DEV_MONITOR_INGRESS/2'
CHALLENGE_SCHEMA = 'P309_DEV_CHALLENGE/1'
MAX_MESSAGE_BYTES = 1_048_576
MAX_FRAME_BYTES = 1_404_928
MAX_REQUEST_BYTES = 4096
MAX_SEQUENCE = 4096
TOKEN_FIELDS = frozenset(('schema', 'session_id', 'baseline_sha256', 'sequence',
                          'nonce', 'previous_sha256'))
FAILURES = frozenset(('EOF', 'TIMEOUT', 'IO_ERROR', 'PROTOCOL_ERROR'))
HEX64 = re.compile(r'[0-9a-f]{64}')


class IngressError(ValueError):
    pass


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise IngressError('duplicate JSON field')
        result[key] = value
    return result


def _nonfinite(_):
    raise IngressError('nonfinite number')


def _finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise IngressError('nonfinite float')
    return value


def _document(raw, limit):
    if type(raw) is not bytes or not 0 < len(raw) <= limit:
        raise IngressError('invalid bounded raw bytes')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                          parse_constant=_nonfinite, parse_float=_finite_float)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise IngressError('invalid strict UTF-8 JSON') from exc


def _fields(obj, fields):
    if type(obj) is not dict or set(obj) != fields:
        raise IngressError('exact fields required')


@dataclass(frozen=True)
class Challenge:
    session_id: str
    baseline_sha256: str
    sequence: int
    nonce: str
    previous_sha256: str


def _challenge(obj):
    _fields(obj, TOKEN_FIELDS)
    if type(obj['schema']) is not str or obj['schema'] != CHALLENGE_SCHEMA:
        raise IngressError('wrong challenge schema')
    for key in ('session_id', 'baseline_sha256', 'nonce', 'previous_sha256'):
        if type(obj[key]) is not str or HEX64.fullmatch(obj[key]) is None:
            raise IngressError('invalid challenge digest/token shape')
    if type(obj['sequence']) is not int or not 1 <= obj['sequence'] <= MAX_SEQUENCE:
        raise IngressError('invalid challenge sequence')
    return Challenge(*(obj[key] for key in ('session_id', 'baseline_sha256',
                                           'sequence', 'nonce', 'previous_sha256')))


def _header(obj, kind, fields):
    _fields(obj, fields)
    if (type(obj['protocol']) is not str or obj['protocol'] != PROTOCOL or
            type(obj['kind']) is not str or obj['kind'] != kind):
        raise IngressError('wrong protocol/direction/kind')


def parse_observer_request(raw):
    """M->R outbound shape; no host facts or broker command can be included."""
    obj = _document(raw, MAX_REQUEST_BYTES)
    _header(obj, 'observer_request', {'protocol', 'kind', 'challenge'})
    return _challenge(obj['challenge'])


@dataclass(frozen=True)
class UnverifiedObservation:
    # Preserve the ORIGINAL message bytes, never a JSON reserialization.
    message: bytes
    signature: bytes
    challenge: Challenge


@dataclass(frozen=True)
class TransportFailure:
    reason: str


def _base64(value, maximum):
    if type(value) is not str or not 0 < len(value) <= 4 * ((maximum + 2) // 3):
        raise IngressError('invalid base64 budget/type')
    try:
        encoded = value.encode('ascii')
        decoded = base64.b64decode(encoded, validate=True)
    except (ValueError, UnicodeError) as exc:
        raise IngressError('invalid base64') from exc
    if not 0 < len(decoded) <= maximum or base64.b64encode(decoded) != encoded:
        raise IngressError('noncanonical base64 or decoded budget exceeded')
    return decoded


def parse_relay_message(raw):
    """R->M inbound: parse only; NEVER validates a signature or host facts."""
    obj = _document(raw, MAX_FRAME_BYTES)
    if type(obj) is not dict:
        raise IngressError('expected object')
    if obj.get('kind') == 'transport_failure':
        _header(obj, 'transport_failure', {'protocol', 'kind', 'reason'})
        reason = obj['reason']
        if type(reason) is not str or reason not in FAILURES:
            raise IngressError('fixed failure reason required')
        return TransportFailure(reason)
    _header(obj, 'signed_observation', {'protocol', 'kind', 'envelope'})
    envelope = obj['envelope']
    _fields(envelope, {'message_b64', 'signature_b64'})
    message = _base64(envelope['message_b64'], MAX_MESSAGE_BYTES)
    signature = _base64(envelope['signature_b64'], 512)
    if len(signature) not in (256, 384, 512):
        raise IngressError('unsupported signature byte length')
    doc = _document(message, MAX_MESSAGE_BYTES)
    _fields(doc, TOKEN_FIELDS | {'payload'})
    challenge = _challenge({key: doc[key] for key in TOKEN_FIELDS})
    if type(doc['payload']) is not dict:
        raise IngressError('opaque untrusted payload must be object')
    # Payload is intentionally not interpreted or returned as a safe fact.
    return UnverifiedObservation(message, signature, challenge)
