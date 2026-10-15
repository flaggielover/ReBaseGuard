"""Isolated development sessions for signed WSL observations; no admission API.

Creates only a new p309-wsl-dev-* directory outside Git checkouts. There is no
reopen/resume operation. Key provisioning, Windows identity/ACL isolation,
complete observation and continuous enforcement are NOT implemented here.
"""
import base64
import functools
import hashlib
import json
import math
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import tempfile
import threading
import time

from host_controls import THRESHOLDS

MAX_MESSAGE = 1_048_576
MAX_JOURNAL = 268_435_456
MAX_RECORDS = 4096
FIELDS = ('host_id', 'host_boot', 'guest_boot', 'guest_machine', 'interpreter', 'policy')


class SessionError(Exception):
    pass


def canonical(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise SessionError('duplicate JSON key')
            result[key] = value
        return result
    def nonfinite(_):
        raise SessionError('non-finite JSON number')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=nonfinite)


def identity(payload):
    try:
        host, guest = payload['host'], payload['guest']
        start, end = host['start'], host['end']
        result = dict(host_id=end['host_id_sha256'], host_boot=end['boot_id_sha256'],
                      guest_boot=guest['boot_id_sha256'], guest_machine=guest['machine_id_sha256'],
                      interpreter=guest['interpreter_sha256'], policy=host['policy']['policy_sha256'],
                      glibc=guest['glibc'])
        if any(not isinstance(result[k], str) or not re.fullmatch('[a-f0-9]{64}', result[k]) for k in FIELDS):
            raise SessionError('missing identity digest')
        if not isinstance(result['glibc'], str) or not result['glibc'].startswith('glibc '):
            raise SessionError('missing glibc identity')
        if any(start[k] != end[k] for k in ('host_id_sha256', 'boot_id_sha256')):
            raise SessionError('host identity changes within sample')
        return result
    except (KeyError, TypeError) as exc:
        raise SessionError('malformed identity') from exc


def _openssl(args):
    result = subprocess.run(['openssl', *args], stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=10)
    if result.returncode:
        raise SessionError('OpenSSL verification failed')
    return result.stdout


def verify_signature(public_key, message, signature):
    # No private key is accepted, generated, read, or persisted by this module.
    with tempfile.TemporaryDirectory(prefix='p309-signature-') as directory:
        root = Path(directory)
        for name, data in (('public.pem', public_key), ('message', message), ('signature', signature)):
            (root / name).write_bytes(data)
        description = _openssl(['pkey', '-pubin', '-in', str(root / 'public.pem'), '-text', '-noout'])
        if b'Modulus:' not in description or not any(
                ('(%d bit)' % bits).encode() in description for bits in (2048, 3072, 4096)):
            raise SessionError('expected RSA public key of at least 2048 bits')
        _openssl(['dgst', '-sha256', '-verify', str(root / 'public.pem'), '-signature',
                  str(root / 'signature'), '-sigopt', 'rsa_padding_mode:pkcs1', str(root / 'message')])


def serialized(method):
    @functools.wraps(method)
    def locked(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return locked


class DevSession:
    def __init__(self, directory, baseline, public_key, expected_key_sha256, *, clock=time.monotonic):
        if type(public_key) is not bytes or len(public_key) > 16_384:
            raise SessionError('invalid public key')
        if sha(public_key) != expected_key_sha256:
            raise SessionError('public key pin mismatch')
        baseline_raw = canonical(baseline)
        if len(baseline_raw) > MAX_MESSAGE:
            raise SessionError('baseline exceeds development budget')
        self.identity = identity(strict_json(baseline_raw))
        requested = Path(directory)
        parent = requested.parent.resolve(strict=True)
        if not requested.name.startswith('p309-wsl-dev-'):
            raise SessionError('development directory prefix required')
        for ancestor in (parent, *parent.parents):
            if (ancestor / '.git').exists() or ((ancestor / 'HEAD').is_file() and (ancestor / 'objects').is_dir()):
                raise SessionError('development records must be outside Git repositories')
        self.root = parent / requested.name
        # mkdir is exclusive even for a pre-existing empty directory or symlink.
        self.root.mkdir(mode=0o700)
        parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(parent_fd)
        finally:
            os.close(parent_fd)
        self._root_identity = (self.root.stat().st_dev, self.root.stat().st_ino)
        self._lock = threading.RLock()
        self.public_key = public_key
        self.key_sha256 = expected_key_sha256
        self.baseline_raw = baseline_raw
        self.baseline_sha256 = sha(baseline_raw)
        self.session_id = secrets.token_hex(32)
        self.clock = clock
        self.last_clock = None
        self.pending = None
        self.sequence = 1
        self.terminal = False
        self.fd = None
        self.journal = b''
        self.head = '0' * 64
        self.records = 0
        try:
            with (self.root / 'baseline.json').open('xb') as stream:
                os.chmod(stream.fileno(), 0o600)
                stream.write(baseline_raw)
                stream.flush()
                os.fsync(stream.fileno())
            self.fd = os.open(self.root / 'journal.jsonl', os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
            directory_fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
            self._append('created', {'baseline_sha256': self.baseline_sha256, 'key_sha256': self.key_sha256})
        except Exception:
            self.terminal = True
            self._release()
            raise

    def _time(self):
        value = self.clock()
        try:
            valid = (type(value) in (float, int) and math.isfinite(value) and value >= 0
                     and (self.last_clock is None or value >= self.last_clock))
        except OverflowError:
            valid = False
        if not valid:
            raise SessionError('invalid or regressing monotonic clock')
        self.last_clock = value
        return value

    def _check_store(self):
        if self.terminal or self.fd is None:
            raise SessionError('session is closed or failed')
        root = self.root.lstat()
        if not stat.S_ISDIR(root.st_mode) or (root.st_dev, root.st_ino) != self._root_identity:
            raise SessionError('development directory replaced')
        entry = (self.root / 'journal.jsonl').lstat()
        opened = os.fstat(self.fd)
        if not stat.S_ISREG(entry.st_mode) or (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino):
            raise SessionError('journal replaced')
        if opened.st_size != len(self.journal) or os.pread(self.fd, len(self.journal), 0) != self.journal:
            raise SessionError('journal changed or rolled back')
        baseline_path = self.root / 'baseline.json'
        if not stat.S_ISREG(baseline_path.lstat().st_mode) or baseline_path.read_bytes() != self.baseline_raw:
            raise SessionError('baseline changed')

    def _append(self, kind, data):
        self._check_store()
        record = canonical(dict(schema='P309_DEV_JOURNAL/1', session_id=self.session_id,
                                record=self.records, previous_sha256=self.head, kind=kind, data=data)) + b'\n'
        if len(self.journal) + len(record) > MAX_JOURNAL or self.records >= MAX_RECORDS:
            raise SessionError('development journal budget exceeded')
        try:
            os.lseek(self.fd, 0, os.SEEK_END)
            remaining = memoryview(record)
            while remaining:
                count = os.write(self.fd, remaining)
                if count <= 0:
                    raise SessionError('journal short write')
                remaining = remaining[count:]
            os.fsync(self.fd)
        except Exception:
            self.terminal = True
            raise
        self.journal += record
        self.head = sha(record)
        self.records += 1

    @serialized
    def challenge(self):
        try:
            self._check_store()
            if self.pending is not None:
                raise SessionError('a challenge is already outstanding')
            token = dict(schema='P309_DEV_CHALLENGE/1', session_id=self.session_id,
                         baseline_sha256=self.baseline_sha256, sequence=self.sequence,
                         nonce=secrets.token_hex(32), previous_sha256=self.head)
            self._append('challenge', token)
            self.pending = (token, self._time())
            return dict(token)
        except Exception:
            self.terminal = True
            raise

    @serialized
    def accept(self, envelope):
        try:
            self._check_store()
            if self.pending is None:
                raise SessionError('no outstanding challenge')
            token, issued = self.pending
            limit = THRESHOLDS['sample_s'] + THRESHOLDS['monitor_gap_tolerance_s']
            if self._time() - issued > limit:
                raise SessionError('challenge expired')
            if not isinstance(envelope, dict) or set(envelope) != {'message_b64', 'signature_b64'}:
                raise SessionError('invalid signed envelope')
            if any(not isinstance(v, str) for v in envelope.values()) or len(envelope['message_b64']) > MAX_MESSAGE * 2:
                raise SessionError('invalid envelope encoding or budget')
            if len(envelope['signature_b64']) > 2048:
                raise SessionError('signature exceeds budget')
            message = base64.b64decode(envelope['message_b64'], validate=True)
            signature = base64.b64decode(envelope['signature_b64'], validate=True)
            if len(message) > MAX_MESSAGE:
                raise SessionError('message exceeds budget')
            verify_signature(self.public_key, message, signature)
            doc = strict_json(message)
            if not isinstance(doc, dict) or set(doc) != set(token) | {'payload'}:
                raise SessionError('invalid signed message fields')
            if type(doc['sequence']) is not int or any(doc[k] != v for k, v in token.items()):
                raise SessionError('challenge/session/sequence mismatch')
            if identity(doc['payload']) != self.identity:
                raise SessionError('baseline identity/runtime/policy mismatch')
            if self._time() - issued > limit:
                raise SessionError('challenge expired during verification')
            # This record establishes verification, not a successful/authorized
            # admission. A persistence delay can still expire the challenge.
            self._append('verified_development_envelope', envelope)
            if self._time() - issued > limit:
                raise SessionError('challenge expired during persistence')
            self.pending = None
            accepted_sequence = self.sequence
            self.sequence += 1
            return dict(sequence=accepted_sequence, journal_head_sha256=self.head,
                        scope='DEVELOPMENT_ONLY', signature_valid=True, formal_admission='BLOCKED',
                        qualification_authorized=False, target_execution_authorized=False)
        except Exception as exc:
            self.terminal = True
            if isinstance(exc, SessionError):
                raise
            raise SessionError('development envelope refused') from exc

    def _release(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    @serialized
    def close(self):
        try:
            if self.fd is not None and not self.terminal:
                self._append('closed', {'outstanding_challenge': self.pending is not None})
        finally:
            self.terminal = True
            self._release()
