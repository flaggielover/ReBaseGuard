"""Synthetic signed observations; watchdog stop requests, never job execution."""
import base64
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch

import dev_session as D
from observation_monitor import ObservationMonitor, MonitorError
from test_host_controls import fixture


class Monitors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keys = tempfile.TemporaryDirectory(prefix='p309-monitor-test-keys-')
        cls.private = Path(cls.keys.name) / 'private.pem'
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt', 'rsa_keygen_bits:2048',
                        '-out', str(cls.private)], capture_output=True, check=True)
        cls.public = subprocess.check_output(['openssl', 'pkey', '-in', str(cls.private), '-pubout'])

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='p309-monitor-test-')
        self.mono, self.wall = 1000.0, 1060.0
        h, g = fixture()
        self.baseline = {'host': h, 'guest': g}
        self.latest = copy.deepcopy(self.baseline)
        self.session = self.monitor = None

    def tearDown(self):
        if self.monitor is not None:
            self.monitor.close()
        elif self.session is not None:
            self.session.close()
        self.temp.cleanup()

    def create(self):
        path = Path(self.temp.name) / 'p309-wsl-dev-monitor'
        self.session = D.DevSession(path, self.baseline, self.public, D.sha(self.public), clock=lambda: self.mono)
        self.monitor = ObservationMonitor(self.session, wall_clock=lambda: self.wall, monotonic=lambda: self.mono)
        return self.monitor

    def next_payload(self, gap=1, duration=60, delay=0):
        payload = copy.deepcopy(self.latest)
        previous = self.latest['host']['end']
        for name in ('wall_s', 'uptime_s', 'active_s'):
            payload['host']['start'][name] = previous[name] + gap
            payload['host']['end'][name] = previous[name] + gap + duration
        payload['guest']['utc'] = dt.datetime.fromtimestamp(
            payload['host']['end']['wall_s'], dt.timezone.utc).isoformat()
        self.wall = payload['host']['end']['wall_s'] + delay
        self.mono += gap + duration + delay
        return payload

    def sign(self, token, payload):
        raw = D.canonical(dict(token, payload=payload))
        signature = subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(self.private)],
                                   input=raw, capture_output=True, check=True).stdout
        return dict(message_b64=base64.b64encode(raw).decode(), signature_b64=base64.b64encode(signature).decode())

    def test_two_samples_keep_identity_and_baseline_without_authorizing(self):
        monitor = self.create()
        for sequence in (1, 2):
            token = monitor.challenge()
            payload = self.next_payload()
            result = monitor.accept(self.sign(token, payload))
            self.latest = payload
            self.assertEqual(result['sequence'], sequence)
            self.assertTrue(result['diagnostic_continue'])
            self.assertEqual(result['formal_admission'], 'BLOCKED')
            self.assertFalse(result['qualification_authorized'])
            self.assertFalse(result['target_execution_authorized'])
        self.assertEqual(monitor.status()['valid_observations'], 2)
        records = [json.loads(line) for line in (self.session.root / 'journal.jsonl').read_bytes().splitlines()]
        self.assertEqual(sum(r['kind'] == 'monitor_diagnostic' for r in records), 2)

    def test_signed_busy_sample_latches_stop(self):
        monitor = self.create()
        token = monitor.challenge()
        payload = self.next_payload()
        payload['host']['process_observation']['rows'][0]['cpu_fraction'] = .500001
        with self.assertRaises(MonitorError):
            monitor.accept(self.sign(token, payload))
        self.assertTrue(monitor.stop_requested.is_set())
        self.assertEqual(monitor.status()['reason'], 'candidate_observations_refused')
        self.assertEqual(monitor.status()['valid_observations'], 0)

    def test_signed_incomplete_visibility_is_not_authenticated_safety(self):
        monitor = self.create()
        token = monitor.challenge()
        payload = self.next_payload()
        payload['host']['process_observation']['coverage'] = 'BEST_EFFORT'
        with self.assertRaises(MonitorError):
            monitor.accept(self.sign(token, payload))
        self.assertTrue(monitor.stop_requested.is_set())

    def test_baseline_must_pass_start_diagnostics(self):
        self.baseline['host']['process_observation']['rows'][0]['cpu_fraction'] = .050001
        monitor = self.create()
        self.assertTrue(monitor.stop_requested.is_set())
        with self.assertRaises(MonitorError):
            monitor.challenge()

    def test_challenge_alone_cannot_refresh_liveness(self):
        monitor = self.create()
        self.mono += 80
        monitor.challenge()
        self.mono += 26
        self.assertFalse(monitor.poll())

    def test_in_transit_age_reduces_the_next_deadline(self):
        monitor = self.create()
        token = monitor.challenge()
        payload = self.next_payload(delay=20)
        monitor.accept(self.sign(token, payload))
        self.mono += 86
        self.assertFalse(monitor.poll())

    def test_transport_failure_is_terminal_even_before_deadline(self):
        monitor = self.create()
        monitor.bridge_failed()
        self.assertTrue(monitor.stop_requested.is_set())
        with self.assertRaises(MonitorError):
            monitor.challenge()
        monitor.stop_requested.clear()  # A consumer cannot clear the internal latch.
        self.assertFalse(monitor.poll())

    def test_watchdog_stops_without_another_input(self):
        monitor = self.create()
        monitor.start_watchdog(.01)
        self.mono += 106
        self.assertTrue(monitor.stop_requested.wait(1))
        self.assertEqual(monitor.status()['reason'], 'observation_deadline_exceeded')

    def test_watchdog_does_not_wait_for_a_blocked_verifier(self):
        monitor = self.create()
        monitor.start_watchdog(.01)
        token = monitor.challenge()
        envelope = self.sign(token, self.next_payload())
        entered, release = threading.Event(), threading.Event()
        original = self.session.accept
        errors = []
        def blocked(value):
            entered.set()
            if not release.wait(2):
                raise RuntimeError('test synchronization timeout')
            return original(value)
        def receive():
            try:
                monitor.accept(envelope)
            except MonitorError as exc:
                errors.append(exc)
        with patch.object(self.session, 'accept', side_effect=blocked):
            thread = threading.Thread(target=receive)
            thread.start()
            try:
                self.assertTrue(entered.wait(1))
                self.mono += 45
                self.assertTrue(monitor.stop_requested.wait(1))
                self.assertTrue(thread.is_alive())
            finally:
                release.set()
                thread.join(2)
        self.assertEqual(len(errors), 1)
        self.assertEqual(monitor.status()['valid_observations'], 0)

    def test_watchdog_does_not_wait_for_blocked_diagnostic_persistence(self):
        monitor = self.create()
        monitor.start_watchdog(.01)
        envelope = self.sign(monitor.challenge(), self.next_payload())
        entered, release = threading.Event(), threading.Event()
        original = self.session.record_monitor_decision
        errors = []
        def blocked(value):
            entered.set()
            if not release.wait(2):
                raise RuntimeError('test synchronization timeout')
            return original(value)
        def receive():
            try:
                monitor.accept(envelope)
            except MonitorError as exc:
                errors.append(exc)
        with patch.object(self.session, 'record_monitor_decision', side_effect=blocked):
            thread = threading.Thread(target=receive)
            thread.start()
            try:
                self.assertTrue(entered.wait(1))
                self.mono += 45
                self.assertTrue(monitor.stop_requested.wait(1))
                self.assertTrue(thread.is_alive())
            finally:
                release.set()
                thread.join(2)
        self.assertEqual(len(errors), 1)

    def test_persistence_failure_never_returns_continue(self):
        monitor = self.create()
        envelope = self.sign(monitor.challenge(), self.next_payload())
        original = D.os.fsync
        calls = 0
        def broken(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('synthetic diagnostic fsync failure')
            original(fd)
        with patch.object(D.os, 'fsync', side_effect=broken), self.assertRaises(MonitorError):
            monitor.accept(envelope)
        self.assertTrue(monitor.stop_requested.is_set())
        self.assertTrue(self.session.terminal)

    def test_changed_identity_stops_monitor(self):
        monitor = self.create()
        token = monitor.challenge()
        payload = self.next_payload()
        payload['guest']['interpreter_sha256'] = '1' * 64
        with self.assertRaises(MonitorError):
            monitor.accept(self.sign(token, payload))
        self.assertTrue(monitor.stop_requested.is_set())

    def test_invalid_signature_stops_monitor(self):
        monitor = self.create()
        envelope = self.sign(monitor.challenge(), self.next_payload())
        signature = bytearray(base64.b64decode(envelope['signature_b64']))
        signature[0] ^= 1
        envelope['signature_b64'] = base64.b64encode(signature).decode()
        with self.assertRaises(MonitorError):
            monitor.accept(envelope)
        self.assertTrue(monitor.stop_requested.is_set())

    def test_closed_session_stops_monitor(self):
        monitor = self.create()
        self.session.close()
        self.assertFalse(monitor.poll())
        self.assertEqual(monitor.status()['reason'], 'session_terminated')

    def test_clock_regression_stops_monitor(self):
        monitor = self.create()
        self.mono -= 1
        self.assertFalse(monitor.poll())
        self.assertTrue(monitor.stop_requested.is_set())

    def test_monitor_cannot_record_authorized_decision(self):
        self.create()
        with self.assertRaises(D.SessionError):
            self.session.record_monitor_decision({'formal_admission': 'ACCEPTED',
                'qualification_authorized': True, 'target_execution_authorized': True})
        self.assertFalse(self.monitor.poll())


if __name__ == '__main__':
    unittest.main()
