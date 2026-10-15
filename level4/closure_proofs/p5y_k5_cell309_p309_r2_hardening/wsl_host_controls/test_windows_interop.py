"""Real Windows CNG signatures, synthetic observations, WSL/OpenSSL verification."""
import base64
import copy
import datetime as dt
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import dev_session as D
import host_controls as H
from observation_monitor import ObservationMonitor, MonitorError
from synthetic_windows_bridge import WindowsSyntheticSigner, MAX_MESSAGE
from test_host_controls import fixture


class WindowsInterop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('openssl'):
            raise RuntimeError('OpenSSL required; interoperability must not skip')
        print('OPENSSL=' + subprocess.check_output(['openssl', 'version'], text=True).strip(), flush=True)
        cls.signer = WindowsSyntheticSigner()
        print('WINDOWS_SIGNER=' + json.dumps(cls.signer.metadata(), sort_keys=True), flush=True)

    @classmethod
    def tearDownClass(cls):
        cls.signer.close()

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix='p309-windows-interop-')
        self.sessions = []
        h, g = fixture()
        self.payload = {'host': h, 'guest': g}

    def tearDown(self):
        try:
            for session in self.sessions:
                session.close()
        finally:
            self.scratch.cleanup()

    def create(self, signer=None, pin=None):
        signer = signer or self.signer
        root = Path(self.scratch.name) / ('p309-wsl-dev-' + str(len(self.sessions)))
        session = D.DevSession(root, self.payload, signer.public, pin or signer.pin)
        self.sessions.append(session)
        return session

    def signed(self, session, payload=None, signer=None):
        message = D.canonical(dict(session.challenge(), payload=payload or self.payload))
        return (signer or self.signer).sign(message)

    def assert_blocked_ack(self, result):
        self.assertTrue(result['signature_valid'])
        self.assertEqual(result['formal_admission'], 'BLOCKED')
        self.assertIs(result['qualification_authorized'], False)
        self.assertIs(result['target_execution_authorized'], False)

    def test_2048_3072_4096_real_windows_signatures(self):
        for bits in (2048, 3072, 4096):
            with self.subTest(bits=bits), WindowsSyntheticSigner(bits) as signer:
                print('WINDOWS_SIGNER=' + json.dumps(signer.metadata(), sort_keys=True), flush=True)
                session = self.create(signer)
                self.assert_blocked_ack(session.accept(self.signed(session, signer=signer)))
                journal = [json.loads(x) for x in (session.root / 'journal.jsonl').read_bytes().splitlines()]
                self.assertEqual(journal[-1]['kind'], 'verified_development_envelope')

    def test_unicode_crlf_whitespace_are_exact_bytes(self):
        session = self.create()
        payload = copy.deepcopy(self.payload)
        payload['synthetic_note'] = 'Windows → WSL 中文 🔐\r\n'
        message = json.dumps(dict(session.challenge(), payload=payload), ensure_ascii=False, indent=2)
        raw = message.replace('\n', '\r\n').encode('utf-8') + b'\r\n'
        envelope = self.signer.sign(raw)
        self.assertEqual(base64.b64decode(envelope['message_b64']), raw)
        self.assert_blocked_ack(session.accept(envelope))

    def test_two_sequences_then_replay_is_terminal(self):
        session = self.create()
        first = self.signed(session)
        self.assertEqual(session.accept(first)['sequence'], 1)
        second = self.signed(session)
        self.assertEqual(session.accept(second)['sequence'], 2)
        session.challenge()
        with self.assertRaises(D.SessionError):
            session.accept(first)
        self.assertTrue(session.terminal)

    def test_cross_session_rejected(self):
        first, second = self.create(), self.create()
        signed = self.signed(first)
        second.challenge()
        with self.assertRaises(D.SessionError):
            second.accept(signed)

    def test_message_and_signature_tamper_rejected(self):
        for field in ('message_b64', 'signature_b64'):
            with self.subTest(field=field):
                session = self.create()
                envelope = self.signed(session)
                raw = bytearray(base64.b64decode(envelope[field]))
                raw[-1] ^= 1
                envelope[field] = base64.b64encode(raw).decode()
                with self.assertRaises(D.SessionError):
                    session.accept(envelope)

    def test_fresh_key_wrong_pin_and_wrong_signer_rejected(self):
        with WindowsSyntheticSigner() as other:
            self.assertNotEqual(other.pin, self.signer.pin)
            with self.assertRaises(D.SessionError):
                self.create(pin=other.pin)
            self.assertEqual(list(Path(self.scratch.name).iterdir()), [])
            session = self.create()
            with self.assertRaises(D.SessionError):
                session.accept(self.signed(session, signer=other))

    def test_signed_identity_change_rejected(self):
        session = self.create()
        changed = copy.deepcopy(self.payload)
        changed['guest']['interpreter_sha256'] = 'f' * 64
        with self.assertRaises(D.SessionError):
            session.accept(self.signed(session, payload=changed))

    def test_duplicate_json_rejected_even_with_windows_signature(self):
        session = self.create()
        raw = D.canonical(dict(session.challenge(), payload=self.payload))
        raw = b'{"sequence":1,' + raw[1:]
        with self.assertRaises(D.SessionError):
            session.accept(self.signer.sign(raw))

    def test_signed_busy_payload_is_not_safe_or_authorized(self):
        session = self.create()
        payload = copy.deepcopy(self.payload)
        payload['host']['process_observation']['rows'][0]['cpu_fraction'] = 2.0
        self.assert_blocked_ack(session.accept(self.signed(session, payload=payload)))
        result = H.assess(payload['host'], payload['guest'], now=1060)
        self.assertFalse(result['candidate_observations_pass'])
        self.assertFalse(result['checks']['individual_cpu_quiet'])

    def test_invalid_helper_requests_are_terminal(self):
        cases = ({'synthetic': False, 'message_b64': 'YQ=='},
                 {'synthetic': True, 'message_b64': 'bad!'},
                 {'synthetic': True, 'message_b64': ''},
                 {'synthetic': True, 'message_b64': 'YQ==', 'extra': 1})
        for request in cases:
            with self.subTest(request=request), WindowsSyntheticSigner() as signer:
                with self.assertRaises(RuntimeError):
                    signer.request(request)
                self.assertNotEqual(signer.process.wait(timeout=10), 0)

    def test_real_windows_signatures_feed_fail_stop_monitor(self):
        session = self.create()
        clock = {'mono': 1000.0, 'wall': 1060.0}
        monitor = ObservationMonitor(session, monotonic=lambda: clock['mono'], wall_clock=lambda: clock['wall'])
        latest = copy.deepcopy(self.payload)
        try:
            for busy in (False, True):
                token = monitor.challenge()
                payload = copy.deepcopy(latest)
                for name in ('wall_s', 'uptime_s', 'active_s'):
                    payload['host']['start'][name] = latest['host']['end'][name] + 1
                    payload['host']['end'][name] = latest['host']['end'][name] + 61
                payload['guest']['utc'] = dt.datetime.fromtimestamp(
                    payload['host']['end']['wall_s'], dt.timezone.utc).isoformat()
                clock['mono'] += 61
                clock['wall'] = payload['host']['end']['wall_s']
                if busy:
                    payload['host']['process_observation']['rows'][0]['cpu_fraction'] = .500001
                envelope = self.signer.sign(D.canonical(dict(token, payload=payload)))
                if busy:
                    with self.assertRaises(MonitorError):
                        monitor.accept(envelope)
                    self.assertTrue(monitor.stop_requested.is_set())
                else:
                    self.assertEqual(monitor.accept(envelope)['formal_admission'], 'BLOCKED')
                latest = payload
            self.assertEqual(monitor.status()['valid_observations'], 1)
        finally:
            monitor.close()

    def test_client_budget_and_helper_eof(self):
        signer = WindowsSyntheticSigner()
        try:
            for message in (b'', b'x' * (MAX_MESSAGE + 1), 'not bytes'):
                with self.assertRaises(ValueError):
                    signer.sign(message)
        finally:
            self.assertEqual(signer.close(), 0)


if __name__ == '__main__':
    unittest.main()
