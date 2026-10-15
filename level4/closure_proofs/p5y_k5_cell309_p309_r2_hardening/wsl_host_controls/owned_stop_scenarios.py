"""Shared synthetic end-to-end cases; signer selected by the test subclass."""
import copy
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from unittest.mock import patch

import dev_session as D
from observation_monitor import ObservationMonitor, MonitorError
from synthetic_owned_stop import SyntheticOwnedTree, identity
from test_host_controls import fixture


class StopScenarios:
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix='p309-owned-stop-chain-')
        self.mono, self.wall = 1000.0, 1060.0
        host, guest = fixture()
        self.latest = dict(host=host, guest=guest)
        self.session = D.DevSession(Path(self.scratch.name) / 'p309-wsl-dev-owned-stop',
                                    self.latest, self.public, D.sha(self.public), clock=lambda: self.mono)
        self.monitor = ObservationMonitor(self.session, wall_clock=lambda: self.wall,
                                          monotonic=lambda: self.mono)
        self.tree = None
        self.bystander = subprocess.Popen([sys.executable, '-I', '-B', '-c', 'import time; time.sleep(30)'],
                                          start_new_session=True)
        self.bystander_start = identity(self.bystander.pid)['start_ticks']

    def tearDown(self):
        try:
            if self.tree is not None:
                self.tree.close()
        finally:
            try:
                self.monitor.close()
            finally:
                self.bystander.terminate()
                self.bystander.wait(timeout=3)
                self.scratch.cleanup()

    def start_tree(self):
        self.tree = SyntheticOwnedTree(self.monitor.stop_requested, synthetic_only=True)

    def next_envelope(self, busy=False):
        token = self.monitor.challenge()
        payload = copy.deepcopy(self.latest)
        for name in ('wall_s', 'uptime_s', 'active_s'):
            payload['host']['start'][name] = self.latest['host']['end'][name] + 1
            payload['host']['end'][name] = self.latest['host']['end'][name] + 61
        payload['guest']['utc'] = dt.datetime.fromtimestamp(
            payload['host']['end']['wall_s'], dt.timezone.utc).isoformat()
        self.mono += 61
        self.wall = payload['host']['end']['wall_s']
        if busy:
            payload['host']['process_observation']['rows'][0]['cpu_fraction'] = .500001
        self.latest = payload
        return self.sign(D.canonical(dict(token, payload=payload)))

    def assert_stopped(self):
        report = self.tree.wait_stopped()
        self.assertTrue(report['owned_tree_reaped'])
        self.assertEqual(len(report['reaped']), 3)
        self.assertEqual(report['formal_admission'], 'BLOCKED')
        self.assertIs(report['qualification_authorized'], False)
        self.assertIs(report['target_execution_authorized'], False)
        for row in report['members']:
            try:
                now = identity(row['pid'])
            except FileNotFoundError:
                continue
            self.assertNotEqual(now['start_ticks'], row['start_ticks'])
        self.assertIsNone(self.bystander.poll())
        self.assertEqual(identity(self.bystander.pid)['start_ticks'], self.bystander_start)
        print('SYNTHETIC_STOP_CHAIN=' + json.dumps(dict(
            case=self.id(), signer=self.signer_kind, stop=self.monitor.status(),
            fixture=report, bystander_alive=True), sort_keys=True), flush=True)

    def test_safe_then_signed_busy_terminates_tree(self):
        self.start_tree()
        result = self.monitor.accept(self.next_envelope())
        self.assertTrue(result['diagnostic_continue'])
        self.assertFalse(self.tree._done.is_set())
        with self.assertRaises(MonitorError):
            self.monitor.accept(self.next_envelope(busy=True))
        self.assertEqual(self.monitor.status()['reason'], 'candidate_observations_refused')
        self.assert_stopped()

    def test_transport_failure_terminates_tree(self):
        self.start_tree()
        self.monitor.bridge_failed()
        self.assert_stopped()

    def test_watchdog_without_next_input_terminates_tree(self):
        self.start_tree()
        self.monitor.start_watchdog(.01)
        self.mono += 106
        self.assert_stopped()

    def _blocked_operation(self, name):
        self.start_tree()
        self.monitor.start_watchdog(.01)
        envelope = self.next_envelope()
        entered, release = threading.Event(), threading.Event()
        errors = []
        original = getattr(self.session, name)
        def blocked(value):
            entered.set()
            if not release.wait(10):
                raise RuntimeError('synthetic synchronization timeout')
            return original(value)
        def receive():
            try:
                self.monitor.accept(envelope)
            except MonitorError as exc:
                errors.append(str(exc))
        with patch.object(self.session, name, side_effect=blocked):
            thread = threading.Thread(target=receive)
            thread.start()
            try:
                self.assertTrue(entered.wait(2))
                self.mono += 45
                self.assert_stopped()
                self.assertTrue(thread.is_alive(), 'fixture must stop while the operation remains blocked')
            finally:
                release.set()
                thread.join(3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(len(errors), 1)

    def test_blocked_verifier_does_not_block_tree_termination(self):
        self._blocked_operation('accept')

    def test_blocked_persistence_does_not_block_tree_termination(self):
        self._blocked_operation('record_monitor_decision')

    def test_bad_signature_terminates_tree(self):
        self.start_tree()
        envelope = self.next_envelope()
        import base64
        signature = bytearray(base64.b64decode(envelope['signature_b64']))
        signature[0] ^= 1
        envelope['signature_b64'] = base64.b64encode(signature).decode()
        with self.assertRaises(MonitorError):
            self.monitor.accept(envelope)
        self.assert_stopped()

    def test_preexisting_stop_refuses_to_launch(self):
        self.monitor.bridge_failed()
        with patch('synthetic_owned_stop.subprocess.Popen') as launch:
            with self.assertRaises(ValueError):
                self.start_tree()
            launch.assert_not_called()
