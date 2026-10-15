"""Synthetic messages and ephemeral test keys only; no Windows or P309 launch."""
import base64
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch

import dev_session as D
from test_host_controls import fixture


class Sessions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('openssl'):
            raise RuntimeError('OpenSSL is required; crypto tests must not silently skip')
        cls.keys = tempfile.TemporaryDirectory(prefix='p309-ephemeral-test-keys-')
        cls.private = Path(cls.keys.name) / 'private.pem'
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:2048',
                        '-out', str(cls.private)], check=True, capture_output=True)
        cls.public = subprocess.check_output(['openssl', 'pkey', '-in', str(cls.private), '-pubout'])

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix='p309-session-tests-')
        self.path = Path(self.scratch.name) / 'p309-wsl-dev-case'
        self.now = 1000.0
        h, g = fixture()
        self.payload = {'host': h, 'guest': g}
        self.session = None

    def tearDown(self):
        if self.session is not None:
            self.session.close()
        self.scratch.cleanup()

    def create(self, path=None):
        self.session = D.DevSession(path or self.path, self.payload, self.public, D.sha(self.public),
                                    clock=lambda: self.now)
        return self.session

    def sign_raw(self, message):
        result = subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(self.private),
                                 '-sigopt', 'rsa_padding_mode:pkcs1'], input=message,
                                capture_output=True, check=True)
        return {'message_b64': base64.b64encode(message).decode(),
                'signature_b64': base64.b64encode(result.stdout).decode()}

    def signed(self, token, payload=None):
        return self.sign_raw(D.canonical(dict(token, payload=self.payload if payload is None else payload)))

    def test_good_envelope_is_persisted_but_never_authorizes(self):
        session = self.create()
        result = session.accept(self.signed(session.challenge()))
        self.assertEqual(result['sequence'], 1)
        self.assertTrue(result['signature_valid'])
        self.assertEqual(result['formal_admission'], 'BLOCKED')
        self.assertIs(result['qualification_authorized'], False)
        self.assertIs(result['target_execution_authorized'], False)
        journal = [json.loads(line) for line in (self.path / 'journal.jsonl').read_bytes().splitlines()]
        self.assertEqual([r['kind'] for r in journal], ['created', 'challenge', 'verified_development_envelope'])
        self.assertEqual((self.path / 'baseline.json').read_bytes(), D.canonical(self.payload))
        self.assertEqual(os.stat(self.path / 'baseline.json').st_mode & 0o777, 0o600)

    def test_signature_binds_payload_bytes(self):
        session = self.create()
        envelope = self.signed(session.challenge())
        message = base64.b64decode(envelope['message_b64']).replace(b'CPython', b'PyOther')
        envelope['message_b64'] = base64.b64encode(message).decode()
        with self.assertRaises(D.SessionError):
            session.accept(envelope)
        self.assertTrue(session.terminal)

    def test_key_pin_is_required_before_any_directory_is_created(self):
        with self.assertRaises(D.SessionError):
            D.DevSession(self.path, self.payload, self.public, '0' * 64)
        self.assertFalse(self.path.exists())

    def test_signed_identity_or_runtime_change_is_refused(self):
        for field in ('interpreter_sha256', 'boot_id_sha256', 'machine_id_sha256', 'glibc'):
            with self.subTest(field=field):
                session = self.create(Path(self.scratch.name) / ('p309-wsl-dev-' + field))
                payload = copy.deepcopy(self.payload)
                payload['guest'][field] = 'glibc 2.40' if field == 'glibc' else '9' * 64
                with self.assertRaises(D.SessionError):
                    session.accept(self.signed(session.challenge(), payload))
                session.close()

    def test_old_envelope_is_rejected_after_a_new_challenge(self):
        session = self.create()
        old = self.signed(session.challenge())
        session.accept(old)
        session.challenge()
        with self.assertRaises(D.SessionError):
            session.accept(old)

    def test_cross_session_envelope_is_rejected(self):
        session = self.create()
        old = self.signed(session.challenge())
        session.close()
        session = self.create(Path(self.scratch.name) / 'p309-wsl-dev-second')
        session.challenge()
        with self.assertRaises(D.SessionError):
            session.accept(old)

    def test_signed_wrong_nonce_sequence_or_checkpoint_is_refused(self):
        for field, value in (('nonce', '0' * 64), ('sequence', True), ('previous_sha256', '0' * 64)):
            with self.subTest(field=field):
                session = self.create(Path(self.scratch.name) / ('p309-wsl-dev-' + field))
                token = session.challenge()
                token[field] = value
                with self.assertRaises(D.SessionError):
                    session.accept(self.signed(token))
                session.close()

    def test_expired_challenge_and_clock_regression_are_refused(self):
        for delta in (105.001, -1.0):
            with self.subTest(delta=delta):
                self.now = 1000.0
                session = self.create(Path(self.scratch.name) / ('p309-wsl-dev-time-' + str(delta)))
                envelope = self.signed(session.challenge())
                self.now += delta
                with self.assertRaises(D.SessionError):
                    session.accept(envelope)
                session.close()

    def test_105_second_boundary_is_inclusive(self):
        session = self.create()
        envelope = self.signed(session.challenge())
        self.now += 105
        self.assertEqual(session.accept(envelope)['sequence'], 1)

    def test_bad_clock_values_are_refused(self):
        for index, value in enumerate((True, float('nan'), float('inf'), 10**400)):
            with self.subTest(value=value):
                self.now = 1000.0
                session = self.create(Path(self.scratch.name) / ('p309-wsl-dev-clock-' + str(index)))
                self.now = value
                with self.assertRaises(D.SessionError):
                    session.challenge()
                session.close()

    def test_expiry_during_persistence_has_no_successful_ack(self):
        session = self.create()
        envelope = self.signed(session.challenge())
        fsync = D.os.fsync
        def delayed(fd):
            fsync(fd)
            self.now += 106
        with patch.object(D.os, 'fsync', delayed), self.assertRaises(D.SessionError):
            session.accept(envelope)
        self.assertTrue(session.terminal)
        last = json.loads((self.path / 'journal.jsonl').read_bytes().splitlines()[-1])
        self.assertEqual(last['kind'], 'verified_development_envelope')

    def test_signature_does_not_attest_workload_safety(self):
        session = self.create()
        busy = copy.deepcopy(self.payload)
        busy['host']['process_observation']['rows'][0]['cpu_fraction'] = 100
        result = session.accept(self.signed(session.challenge(), busy))
        self.assertTrue(result['signature_valid'])
        self.assertEqual(result['formal_admission'], 'BLOCKED')
        self.assertFalse(result['qualification_authorized'])

    def test_expiry_during_crypto_verification_is_refused(self):
        session = self.create()
        envelope = self.signed(session.challenge())
        original = D.verify_signature
        def delayed(*args):
            original(*args)
            self.now += 106
        with patch.object(D, 'verify_signature', delayed), self.assertRaises(D.SessionError):
            session.accept(envelope)

    def test_duplicate_json_keys_are_refused_even_when_signed(self):
        session = self.create()
        raw = D.canonical(dict(session.challenge(), payload=self.payload))
        raw = b'{"sequence":1,' + raw[1:]
        with self.assertRaises(D.SessionError):
            session.accept(self.sign_raw(raw))

    def test_nonfinite_and_oversized_messages_are_refused(self):
        session = self.create()
        session.challenge()
        with self.assertRaises(D.SessionError):
            session.accept(self.sign_raw(b'{"value":NaN}'))
        session.close()
        session = self.create(Path(self.scratch.name) / 'p309-wsl-dev-big')
        session.challenge()
        with self.assertRaises(D.SessionError):
            session.accept({'message_b64': 'A' * (D.MAX_MESSAGE * 2 + 1), 'signature_b64': ''})

    def test_journal_rollback_and_baseline_changes_are_refused(self):
        session = self.create()
        before = (self.path / 'journal.jsonl').read_bytes()
        token = session.challenge()
        (self.path / 'journal.jsonl').write_bytes(before)
        with self.assertRaises(D.SessionError):
            session.accept(self.signed(token))
        session.close()
        session = self.create(Path(self.scratch.name) / 'p309-wsl-dev-baseline')
        (session.root / 'baseline.json').write_bytes(b'{}')
        with self.assertRaises(D.SessionError):
            session.challenge()

    def test_replaced_journal_is_refused(self):
        session = self.create()
        path = self.path / 'journal.jsonl'
        raw = path.read_bytes()
        path.rename(self.path / 'old-journal')
        path.write_bytes(raw)
        with self.assertRaises(D.SessionError):
            session.challenge()

    def test_existing_or_orphaned_directory_is_never_resumed(self):
        session = self.create()
        session.challenge()
        # Simulate descriptor loss without a successful close record.
        session._release()
        with self.assertRaises(FileExistsError):
            self.create()

    def test_git_checkout_and_unscoped_storage_are_refused(self):
        with self.assertRaises(D.SessionError):
            self.create(Path(self.scratch.name) / 'ordinary-directory')
        (Path(self.scratch.name) / '.git').mkdir()
        with self.assertRaises(D.SessionError):
            self.create()
        self.assertFalse(self.path.exists())

    def test_durability_error_is_terminal_and_not_acknowledged(self):
        session = self.create()
        envelope = self.signed(session.challenge())
        with patch.object(D.os, 'fsync', side_effect=OSError('synthetic fsync failure')):
            with self.assertRaises(D.SessionError):
                session.accept(envelope)
        self.assertTrue(session.terminal)
        with self.assertRaises(D.SessionError):
            session.challenge()

    def test_concurrent_replay_is_acknowledged_at_most_once(self):
        session = self.create()
        envelope = self.signed(session.challenge())
        def accept():
            try:
                return session.accept(envelope)
            except D.SessionError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: accept(), range(2)))
        self.assertEqual(sum(r is not None for r in results), 1)


if __name__ == '__main__':
    unittest.main()
