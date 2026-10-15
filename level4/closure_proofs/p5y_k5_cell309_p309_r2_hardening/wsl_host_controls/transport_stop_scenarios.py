"""New link-specific cases; old stop suites are imported only for fixture helpers."""
import base64
import copy
import datetime as dt
import json
import threading
from unittest.mock import patch

from owned_stop_scenarios import StopScenarios
from synthetic_transport_link import SyntheticObservationLink, LinkError


class TransportStopScenarios:
    def setUp(self):
        self.signer = self.make_signer()
        self.addCleanup(self.signer.close)
        self.public = self.signer.public
        StopScenarios.setUp(self)
        self.link = SyntheticObservationLink(self.monitor, self.signer, synthetic_only=True)

    def tearDown(self):
        try:
            self.link.close()
        finally:
            StopScenarios.tearDown(self)

    start_tree = StopScenarios.start_tree

    def next_payload(self, busy=False):
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
        return payload

    def assert_stopped(self):
        StopScenarios.assert_stopped(self)
        print('SYNTHETIC_LINK_STOP=' + json.dumps(dict(
            case=self.id(), transport=self.signer_kind, link=self.link.status()), sort_keys=True), flush=True)

    def test_safe_then_busy_flows_through_link(self):
        self.start_tree()
        result = self.link.observe(self.next_payload())
        self.assertTrue(result['diagnostic_continue'])
        self.assertEqual(result['formal_admission'], 'BLOCKED')
        self.assertFalse(self.tree._done.is_set())
        with self.assertRaises(LinkError):
            self.link.observe(self.next_payload(busy=True))
        self.assertEqual(self.monitor.status()['valid_observations'], 1)
        self.assert_stopped()
        with self.assertRaises(LinkError):
            self.link.observe(self.latest)

    def test_helper_exit_automatically_stops_without_manual_bridge_notification(self):
        self.start_tree()
        self.break_transport()
        with self.assertRaises(LinkError):
            self.link.observe(self.next_payload())
        self.assertEqual(self.link.status()['reason'], 'synthetic_signer_failed')
        self.assert_stopped()

    def test_blocked_signer_times_out_stops_and_discards_late_valid_response(self):
        self.start_tree()
        entered, release = threading.Event(), threading.Event()
        original = self.signer.sign
        def blocked(raw):
            entered.set()
            if not release.wait(10):
                raise RuntimeError('synthetic synchronization timeout')
            return original(raw)
        with patch.object(self.signer, 'sign', side_effect=blocked) as calls:
            try:
                with self.assertRaisesRegex(LinkError, 'timeout'):
                    self.link.observe(self.next_payload())
                self.assertTrue(entered.is_set())
                self.assertTrue(self.link.status()['signer_pending'])
                self.assert_stopped()
                with self.assertRaises(LinkError):
                    self.link.observe(self.latest)
                self.assertEqual(calls.call_count, 1)
                with self.assertRaisesRegex(LinkError, 'cleanup incomplete'):
                    self.link.close(timeout=0)
            finally:
                release.set()
                self.link.close(timeout=3)
        self.assertEqual(self.monitor.status()['valid_observations'], 0)
        self.assertFalse(self.link.status()['signer_pending'])

    def test_blocked_error_cleanup_does_not_delay_tree_stop(self):
        self.start_tree()
        self.break_transport()
        entered, release = threading.Event(), threading.Event()
        original = self.signer.close
        def blocked_cleanup():
            entered.set()
            if not release.wait(10):
                raise RuntimeError('synthetic synchronization timeout')
            return original()
        with patch.object(self.signer, 'close', side_effect=blocked_cleanup):
            try:
                with self.assertRaisesRegex(LinkError, 'timeout'):
                    self.link.observe(self.next_payload())
                self.assertTrue(entered.is_set())
                self.assertTrue(self.link.status()['signer_pending'])
                self.assert_stopped()
            finally:
                release.set()
                self.link.close(timeout=3)
        self.assertEqual(self.monitor.status()['valid_observations'], 0)

    def _inflight(self, action):
        self.start_tree()
        entered, release = threading.Event(), threading.Event()
        errors = []
        original = self.signer.sign
        def blocked(raw):
            entered.set()
            if not release.wait(10):
                raise RuntimeError('synthetic synchronization timeout')
            return original(raw)
        payload = self.next_payload()
        def observe():
            try:
                self.link.observe(payload)
            except LinkError as exc:
                errors.append(str(exc))
        with patch.object(self.signer, 'sign', side_effect=blocked) as calls:
            thread = threading.Thread(target=observe)
            thread.start()
            try:
                self.assertTrue(entered.wait(2))
                action()
                self.assert_stopped()
                self.assertTrue(self.link.status()['signer_pending'])
                self.assertEqual(calls.call_count, 1)
            finally:
                release.set()
                thread.join(3)
                self.link.close(timeout=3)
        self.assertFalse(thread.is_alive())
        self.assertEqual(len(errors), 1)
        self.assertEqual(self.monitor.status()['valid_observations'], 0)

    def test_concurrent_request_stops_without_second_signature(self):
        def concurrent():
            with self.assertRaisesRegex(LinkError, 'concurrent'):
                self.link.observe(self.latest)
        self._inflight(concurrent)

    def test_close_publishes_stop_before_waiting_for_inflight_signer(self):
        def close():
            with self.assertRaisesRegex(LinkError, 'cleanup incomplete'):
                self.link.close(timeout=0)
        self._inflight(close)

    def test_tampered_signature_stops_without_manual_bridge_notification(self):
        self.start_tree()
        original = self.signer.sign
        def changed(raw):
            envelope = original(raw)
            signature = bytearray(base64.b64decode(envelope['signature_b64']))
            signature[0] ^= 1
            envelope['signature_b64'] = base64.b64encode(signature).decode()
            return envelope
        with patch.object(self.signer, 'sign', side_effect=changed):
            with self.assertRaises(LinkError):
                self.link.observe(self.next_payload())
        self.assert_stopped()

    def test_malformed_payload_stops_before_signing(self):
        self.start_tree()
        with patch.object(self.signer, 'sign') as sign:
            with self.assertRaises(LinkError):
                self.link.observe(['not', 'an', 'object'])
            sign.assert_not_called()
        self.assert_stopped()

    def test_close_is_one_shot_and_does_not_own_signer_cleanup(self):
        self.start_tree()
        with patch.object(self.signer, 'close', wraps=self.signer.close) as close:
            first = self.link.close()
            self.assertEqual(self.link.close(), first)
            close.assert_not_called()
        self.assert_stopped()
        with self.assertRaises(LinkError):
            self.link.observe(self.latest)
