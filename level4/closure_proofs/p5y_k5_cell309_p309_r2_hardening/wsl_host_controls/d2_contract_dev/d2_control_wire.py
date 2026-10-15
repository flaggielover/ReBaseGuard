"""Strict H4 wire shape only. No OS credentials, transport, or execution."""
from dataclasses import dataclass
import hashlib
import json
import re

PROTOCOL = 'P309_DEV_BROKER_CONTROL/2'
MAX_REQUEST_BYTES = 16384
FIELDS = frozenset(('protocol', 'request_id', 'operation', 'generation'))
HEX_ID = re.compile(r'[0-9a-f]{32}')


class WireError(ValueError):
    pass


@dataclass(frozen=True)
class Request:
    request_id: str
    operation: str
    generation: str | None

    def fingerprint(self):
        raw = json.dumps(dict(protocol=PROTOCOL, request_id=self.request_id,
                              operation=self.operation, generation=self.generation),
                         sort_keys=True, separators=(',', ':'), allow_nan=False).encode('ascii')
        return hashlib.sha256(raw).hexdigest()


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise WireError('duplicate field')
        result[key] = value
    return result


def _nonfinite(_):
    raise WireError('nonfinite number')


def valid_id(value):
    return type(value) is str and HEX_ID.fullmatch(value) is not None


def parse_request(raw):
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_REQUEST_BYTES:
        raise WireError('request must be 1..16384 raw bytes')
    try:
        obj = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                         parse_constant=_nonfinite)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise WireError('invalid strict UTF-8 JSON request') from exc
    if type(obj) is not dict or set(obj) != FIELDS:
        raise WireError('exact request fields required')
    if type(obj['protocol']) is not str or obj['protocol'] != PROTOCOL:
        raise WireError('wrong protocol')
    if not valid_id(obj['request_id']):
        raise WireError('invalid request ID')
    if type(obj['operation']) is not str or obj['operation'] not in ('status', 'stop'):
        raise WireError('only status/stop permitted')
    generation = obj['generation']
    if generation is not None and not valid_id(generation):
        raise WireError('invalid generation')
    if obj['operation'] == 'stop' and generation is None:
        raise WireError('stop requires generation')
    return Request(obj['request_id'], obj['operation'], generation)
