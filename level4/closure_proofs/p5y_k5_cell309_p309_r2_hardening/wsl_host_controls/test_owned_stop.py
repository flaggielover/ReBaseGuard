"""Real Linux fixture termination, never a P309 workload or admission check."""
import os
import signal
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

import synthetic_owned_stop as S


class OwnedStop(unittest.TestCase):
    def assert_reaped(self, tree, report):
        self.assertTrue(report['owned_tree_reaped'])
        self.assertEqual(report['formal_admission'], 'BLOCKED')
        self.assertIs(report['qualification_authorized'], False)
        self.assertIs(report['target_execution_authorized'], False)
        self.assertEqual(tree._process.returncode, 0)
        self.assertEqual(len(report['reaped']), 3)
        for row in tree.ready['members']:
            try:
                current = S.identity(row['pid'])
            except FileNotFoundError:
                continue
            self.assertNotEqual(current['start_ticks'], row['start_ticks'],
                                'owned process still exists, including as zombie')

    def test_stubborn_three_generation_tree_is_killed_and_reaped_bystander_survives(self):
        bystander = subprocess.Popen([sys.executable, '-I', '-B', '-c', 'import time; time.sleep(30)'],
                                     start_new_session=True)
        try:
            before = S.identity(bystander.pid)
            stop = threading.Event()
            with S.SyntheticOwnedTree(stop, synthetic_only=True) as tree:
                rows = tree.ready['members']
                root = next(r for r in rows if r['ppid'] == tree.ready['owner_pid'])
                child = next(r for r in rows if r['ppid'] == root['pid'])
                self.assertTrue(any(r['ppid'] == child['pid'] for r in rows))
                self.assertNotEqual(root['pgid'], before['pgid'])
                stop.set()
                report = tree.wait_stopped()
                self.assert_reaped(tree, report)
                self.assertTrue(report['sigkill_required'])
                self.assertTrue(all(os.WIFSIGNALED(r['wait_status']) and
                                    os.WTERMSIG(r['wait_status']) == signal.SIGKILL
                                    for r in report['reaped']))
                self.assertIsNone(bystander.poll())
                self.assertEqual(S.identity(bystander.pid)['start_ticks'], before['start_ticks'])
        finally:
            bystander.terminate()
            bystander.wait(timeout=3)

    def test_cooperative_fixture_is_reaped_after_sigterm(self):
        stop = threading.Event()
        with S.SyntheticOwnedTree(stop, synthetic_only=True, stubborn=False) as tree:
            stop.set()
            report = tree.wait_stopped()
            self.assert_reaped(tree, report)
            self.assertFalse(report['sigkill_required'])
            self.assertTrue(all(os.WIFSIGNALED(r['wait_status']) and
                                os.WTERMSIG(r['wait_status']) == signal.SIGTERM
                                for r in report['reaped']))

    def test_close_stops_without_monitor_and_is_idempotent(self):
        tree = S.SyntheticOwnedTree(threading.Event(), synthetic_only=True)
        first = tree.close()
        self.assertEqual(tree.close(), first)
        self.assert_reaped(tree, first)

    def test_clearing_external_event_cannot_restart_completed_fixture(self):
        stop = threading.Event()
        with S.SyntheticOwnedTree(stop, synthetic_only=True) as tree:
            stop.set()
            first = tree.wait_stopped()
            stop.clear()
            self.assertEqual(tree.wait_stopped(), first)
            self.assert_reaped(tree, first)

    def test_explicit_synthetic_scope_and_unlatched_event_required_before_spawn(self):
        stop = threading.Event()
        with patch.object(S.subprocess, 'Popen') as launch:
            for arguments in ({}, {'synthetic_only': 1}, {'synthetic_only': True, 'stubborn': 'yes'}):
                with self.assertRaises(ValueError):
                    S.SyntheticOwnedTree(stop, **arguments)
            stop.set()
            with self.assertRaises(ValueError):
                S.SyntheticOwnedTree(stop, synthetic_only=True)
            with self.assertRaises(ValueError):
                S.SyntheticOwnedTree(None, synthetic_only=True)
            launch.assert_not_called()

    def test_pid_reuse_parent_group_or_session_mismatch_never_signals(self):
        leader = dict(pid=234567, start_ticks=99, ppid=123456, pgid=234567, sid=123456)
        for field in ('start_ticks', 'ppid', 'pgid', 'sid'):
            changed = dict(leader)
            changed[field] += 1
            with self.subTest(field=field), patch.object(S, 'identity', return_value=changed), \
                    patch.object(S.os, 'killpg') as send:
                with self.assertRaises(S.StopError):
                    S._signal_owned(leader, 123456, signal.SIGKILL)
                send.assert_not_called()

    def test_stop_wait_timeout_never_claims_confirmation(self):
        stop = threading.Event()
        with S.SyntheticOwnedTree(stop, synthetic_only=True) as tree:
            with self.assertRaisesRegex(S.StopError, 'unconfirmed'):
                tree.wait_stopped(timeout=0)
            stop.set()
            self.assert_reaped(tree, tree.wait_stopped())

    def test_controller_pipe_eof_stops_and_reaps_fixture(self):
        tree = S.SyntheticOwnedTree(threading.Event(), synthetic_only=True)
        try:
            tree._process.stdin.close()
            report = tree.wait_stopped()
            self.assertEqual(report['trigger'], 'controller_eof')
            self.assert_reaped(tree, report)
        finally:
            tree.close()

    def test_invalid_stop_acknowledgement_is_never_confirmed(self):
        stop = threading.Event()
        tree = S.SyntheticOwnedTree(stop, synthetic_only=True)
        wrong = dict(kind='stopped', members=tree.ready['members'],
                     reaped=[dict(pid=r['pid']) for r in tree.ready['members']],
                     owned_tree_reaped=True, formal_admission='BLOCKED',
                     qualification_authorized=True, target_execution_authorized=False)
        with patch.object(tree, '_receive', return_value=wrong):
            stop.set()
            with self.assertRaisesRegex(S.StopError, 'unconfirmed'):
                tree.wait_stopped()
        self.assertIsNone(tree._report)
        with self.assertRaises(S.StopError):
            tree.close()
        self.assertIsNotNone(tree._process.returncode)
        for row in tree.ready['members']:
            try:
                current = S.identity(row['pid'])
            except FileNotFoundError:
                continue
            self.assertNotEqual(current['start_ticks'], row['start_ticks'])

    def test_fixed_supervisor_lease_stops_without_controller_signal(self):
        with S.SyntheticOwnedTree(threading.Event(), synthetic_only=True) as tree:
            report = tree.wait_stopped(timeout=7)
            self.assertEqual(report['trigger'], 'fixed_lease_expired')
            self.assert_reaped(tree, report)


if __name__ == '__main__':
    unittest.main()
