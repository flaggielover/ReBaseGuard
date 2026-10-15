"""Owned synthetic process doubles only; never starts a Windows helper."""
import io
import subprocess
import threading
import unittest
from unittest.mock import patch
from synthetic_windows_bridge import WindowsSyntheticSigner


class Process:
    def __init__(self, waits):
        self.stdin, self.stdout = io.BytesIO(), io.BytesIO()
        self.waits, self.killed = iter(waits), False

    def wait(self, timeout):
        value = next(self.waits)
        if isinstance(value, Exception):
            raise value
        return value

    def kill(self):
        self.killed = True


def client(waits=(0,)):
    value = WindowsSyntheticSigner.__new__(WindowsSyntheticSigner)
    value.process = Process(waits)
    value.errors = io.BytesIO()
    value._lock = threading.RLock()
    value._closed, value.exit_code = False, None
    return value


class PipeFailures(unittest.TestCase):
    def test_cleanup_timeout_still_closes_all_streams(self):
        timeout = subprocess.TimeoutExpired('owned-test-process', 10)
        value = client([timeout, timeout])
        with self.assertRaises(subprocess.TimeoutExpired):
            value.close()
        self.assertTrue(value.process.killed)
        self.assertTrue(value.process.stdin.closed)
        self.assertTrue(value.process.stdout.closed)
        self.assertTrue(value.errors.closed)

    def test_request_failure_closes_transport_and_refuses_reuse(self):
        value = client()
        with patch.object(value, '_request', side_effect=RuntimeError('synthetic response timeout')):
            with self.assertRaises(RuntimeError):
                value.request({'synthetic': True})
        self.assertTrue(value.errors.closed)
        with self.assertRaisesRegex(RuntimeError, 'closed'):
            value.request({})

    def test_close_is_idempotent_and_retains_exit_status(self):
        value = client([7])
        self.assertEqual(value.close(), 7)
        self.assertEqual(value.close(), 7)

    def test_concurrent_requests_do_not_share_an_inflight_response(self):
        value = client()
        entered, release, second = threading.Event(), threading.Event(), threading.Event()
        def request(arg):
            if arg == 'first':
                entered.set()
                if not release.wait(2):
                    raise RuntimeError('test synchronization timeout')
            else:
                second.set()
            return arg
        results = []
        with patch.object(value, '_request', side_effect=request):
            first = threading.Thread(target=lambda: results.append(value.request('first')))
            other = threading.Thread(target=lambda: results.append(value.request('second')))
            first.start()
            self.assertTrue(entered.wait(1))
            other.start()
            try:
                self.assertFalse(second.wait(0.05))
            finally:
                release.set()
                first.join(2)
                other.join(2)
        self.assertCountEqual(results, ['first', 'second'])
        value.close()


if __name__ == '__main__':
    unittest.main()
