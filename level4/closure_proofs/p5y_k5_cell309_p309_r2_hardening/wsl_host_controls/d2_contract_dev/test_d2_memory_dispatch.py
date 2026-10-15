"""Pure-memory fixtures and ordinary unittest threads; no OS/helper workload."""
from dataclasses import FrozenInstanceError
import threading
import unittest
from unittest.mock import patch

import d2_broker_model as M
import d2_memory_dispatch as D
from test_d2_model import FULL, peer
from test_d2_wire import message


def running():
    queue = D.MemoryDispatch(synthetic_only=True)
    queue._fixture_prepare()
    for kind in ('begin_start', 'dispatch_start', 'start_completed'):
        queue._fixture_event(kind, generation=queue.snapshot().current_id)
    return queue


def enqueue(queue, number=1, operation='status', generation=None, candidate=None):
    return queue.submit(message(request_id=f'{number:032x}', operation=operation,
                                generation=generation),
                        peer=peer(queue.snapshot()) if candidate is None else candidate)


def stop_and_clean(queue):
    generation = queue.snapshot().current_id
    enqueue(queue, operation='stop', generation=generation)
    queue.dispatch_next()
    queue._fixture_event('begin_cleanup', generation=generation)
    queue._fixture_event('cleanup_proof', generation=generation, proof=FULL)


class MemoryDispatch(unittest.TestCase):
    def test_explicit_synthetic_factory(self):
        for value in (False, 1, 'true', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                D.MemoryDispatch(synthetic_only=value)

    def test_fifo_receipts_and_no_implicit_dispatch(self):
        queue = running()
        before = queue.snapshot()
        tickets = [enqueue(queue, n) for n in range(1, 5)]
        self.assertIs(queue.snapshot(), before)
        receipts = [queue.dispatch_next() for _ in tickets]
        self.assertEqual([r.ticket for r in receipts], tickets)
        self.assertEqual(len(queue.snapshot().bindings), 4)
        self.assertEqual([r.revision for r in receipts], list(range(5, 9)))
        self.assertIsNone(queue.dispatch_next())

    def test_queued_status_reads_dispatch_time_state(self):
        queue = D.MemoryDispatch(synthetic_only=True)
        enqueue(queue)
        queue._fixture_prepare()
        result = queue.dispatch_next()
        self.assertEqual(result.receipt.state, M.State.ARMED)
        self.assertEqual(result.receipt.generation, queue.snapshot().current_id)

    def test_cached_old_generation_rechecked_on_dequeue(self):
        queue = running()
        old_generation = queue.snapshot().current_id
        stop_and_clean(queue)
        enqueue(queue, operation='stop', generation=old_generation)  # Same cached ID.
        queue._fixture_prepare()
        for kind in ('begin_start', 'dispatch_start', 'start_completed'):
            queue._fixture_event(kind, generation=queue.snapshot().current_id)
        before, revision = queue.snapshot(), queue.stats()['revision']
        result = queue.dispatch_next()
        self.assertEqual(result.receipt.code, 'STALE_GENERATION')
        self.assertIs(queue.snapshot(), before)
        self.assertEqual(result.revision, revision)
        self.assertEqual(before._current().state, M.State.RUNNING)

    def test_queued_peer_refused_after_monitor_restart(self):
        queue = running()
        enqueue(queue, operation='stop', generation=queue.snapshot().current_id)
        queue._fixture_event('monitor_restart')
        before = queue.snapshot()
        self.assertEqual(queue.dispatch_next().receipt.code, 'PEER_REFUSED')
        self.assertIs(queue.snapshot(), before)

    def test_wrong_role_is_not_authenticated_by_enqueue(self):
        queue = running()
        before = queue.snapshot()
        for role in ('p309-relay', 'p309-runner', 'root'):
            enqueue(queue, candidate=peer(before, role))
            self.assertEqual(queue.dispatch_next().receipt.code, 'PEER_REFUSED')
        self.assertIs(queue.snapshot(), before)

    def test_copies_synthetic_metadata_without_caller_alias(self):
        queue = running()
        candidate = peer(queue.snapshot())
        enqueue(queue, candidate=candidate)
        # Deliberate Python fixture mutation: no claim of a Python security boundary.
        object.__setattr__(candidate, 'role', 'p309-runner')
        self.assertEqual(queue.dispatch_next().receipt.code, 'OK')

    def test_submission_primitive_and_size_bounds_do_not_mutate(self):
        queue = running()
        before, stats = queue.snapshot(), queue.stats()
        good = peer(before)
        for raw in (b'', 'text', bytearray(message()), b'x' * (D.MAX_REQUEST_BYTES + 1)):
            with self.subTest(raw_type=type(raw).__name__), self.assertRaises(D.SubmissionError):
                queue.submit(raw, peer=good)
        for candidate in (None, {}, M.SyntheticPeer('x' * 33, 1, 'i'),
                          M.SyntheticPeer('非ASCII', 1, 'i'),
                          M.SyntheticPeer('p309-monitor', True, 'i'),
                          M.SyntheticPeer('p309-monitor', 0, 'i'),
                          M.SyntheticPeer('p309-monitor', 1, ''),
                          M.SyntheticPeer('p309-monitor', 1, 'i' * 129)):
            with self.subTest(candidate=candidate), self.assertRaises(D.SubmissionError):
                queue.submit(message(), peer=candidate)
        self.assertIs(queue.snapshot(), before)
        self.assertEqual(queue.stats(), stats)

    def test_maximum_raw_size_is_validated_only_at_dispatch(self):
        queue = running()
        raw = message()
        queue.submit(raw + b' ' * (D.MAX_REQUEST_BYTES - len(raw)), peer=peer(queue.snapshot()))
        self.assertEqual(queue.dispatch_next().receipt.code, 'OK')

    def test_invalid_wire_and_public_start_never_advance_model(self):
        queue = running()
        before = queue.snapshot()
        for raw in (b'{', message(operation='start'), message(operation='arm'),
                    message(operation='rearm'), message(operation='reset')):
            queue.submit(raw, peer=peer(before))
            self.assertEqual(queue.dispatch_next().receipt.code, 'BAD_REQUEST')
        self.assertIs(queue.snapshot(), before)

    def test_full_queue_refuses_without_eviction_or_ticket_consumption(self):
        queue = running()
        tickets = [enqueue(queue, n) for n in range(1, D.MAX_PENDING + 1)]
        stats = queue.stats()
        with self.assertRaises(D.SubmissionError):
            enqueue(queue, 100, 'stop', queue.snapshot().current_id)
        self.assertEqual(queue.stats(), stats)
        self.assertEqual([queue.dispatch_next().ticket for _ in tickets], tickets)
        self.assertEqual(queue.snapshot()._current().state, M.State.RUNNING)

    def test_duplicate_stop_has_one_model_update_and_no_cleanup_claim(self):
        queue = running()
        generation = queue.snapshot().current_id
        enqueue(queue, operation='stop', generation=generation)
        enqueue(queue, operation='stop', generation=generation)
        first, second = queue.dispatch_next(), queue.dispatch_next()
        self.assertEqual(first.revision, second.revision)
        self.assertTrue(second.receipt.duplicate)
        self.assertTrue(second.receipt.stop_requested)
        self.assertFalse(second.receipt.cleanup_confirmed)
        self.assertEqual(len(queue.snapshot().bindings), 1)

    def test_close_retains_fifo_for_unknown_refusals_and_cannot_reopen(self):
        queue = running()
        tickets = [enqueue(queue, n) for n in (1, 2)]
        closed = queue.close()
        self.assertEqual(closed, queue.close())
        self.assertEqual(closed['pending'], 2)
        for ticket in tickets:
            result = queue.dispatch_next()
            self.assertEqual(result.ticket, ticket)
            self.assertEqual(result.receipt.code, 'RECOVERY_UNKNOWN')
            self.assertFalse(result.receipt.cleanup_confirmed)
        with self.assertRaises(D.SubmissionError):
            enqueue(queue)
        with self.assertRaises(D.SubmissionError):
            queue._fixture_prepare()
        with self.assertRaises(D.SubmissionError):
            queue._fixture_event('begin_start')

    def test_close_preserves_terminal_history_without_fresh_cleanup_claim(self):
        queue = running()
        stop_and_clean(queue)
        historical = queue.snapshot()._current()
        enqueue(queue, 2)
        queue.close()
        result = queue.dispatch_next()
        self.assertEqual(queue.snapshot()._current(), historical)
        self.assertEqual(result.receipt.historical_state, M.State.STOPPED)
        self.assertEqual(result.receipt.state, M.State.RECOVERY_UNKNOWN)
        self.assertFalse(result.receipt.cleanup_confirmed)

    def test_calculation_exception_retains_item_and_latches_unknown(self):
        queue = running()
        ticket = enqueue(queue)
        with patch.object(M.BrokerModel, 'dispatch', side_effect=RuntimeError('synthetic calculation failure')):
            with self.assertRaisesRegex(RuntimeError, 'synthetic calculation failure'):
                queue.dispatch_next()
        self.assertTrue(queue.stats()['closed'])
        self.assertEqual(queue.stats()['pending'], 1)
        self.assertTrue(queue.snapshot().epoch_unknown)
        result = queue.dispatch_next()
        self.assertEqual(result.ticket, ticket)
        self.assertEqual(result.receipt.code, 'RECOVERY_UNKNOWN')
        self.assertFalse(result.receipt.cleanup_confirmed)

    def test_last_ticket_then_exhaustion_is_terminal(self):
        queue = running()
        # Counter-boundary setup, not evidence of a long-lived 65536-message run.
        queue._next_ticket = D.MAX_TICKET_IDS
        self.assertEqual(enqueue(queue).sequence, D.MAX_TICKET_IDS)
        with self.assertRaises(D.SubmissionError):
            enqueue(queue, 2)
        self.assertTrue(queue.stats()['closed'])
        self.assertEqual(queue.dispatch_next().receipt.code, 'RECOVERY_UNKNOWN')

    def test_snapshot_and_export_mutation_cannot_change_published_model(self):
        queue = running()
        before = queue.snapshot()
        with self.assertRaises(FrozenInstanceError):
            before.current_id = None
        enqueue(queue)
        result = queue.dispatch_next()
        exported = result.as_dict()
        exported['receipt']['state'] = 'invented'
        self.assertEqual(result.receipt.state, M.State.RUNNING)
        self.assertEqual(before.bindings, ())
        self.assertEqual(len(queue.snapshot().bindings), 1)

    def test_all_exports_remain_blocked(self):
        queue = running()
        enqueue(queue)
        result = queue.dispatch_next()
        for row in (queue.stats(), result.as_dict(), result.receipt.as_dict()):
            self.assertEqual(row['formal_admission'], 'BLOCKED')
            for key in ('deployment_authorized', 'execution_authorized',
                        'qualification_authorized', 'target_execution_authorized'):
                self.assertIs(row[key], False)
        self.assertIs(result.as_dict()['actual_peer_authenticated'], False)
        self.assertIs(result.as_dict()['actual_os_effects'], False)

    def test_concurrent_submit_keeps_unique_tickets(self):
        queue = running()
        tickets, errors = [], []
        guard = threading.Lock()
        def worker(offset):
            try:
                own = [enqueue(queue, offset + n) for n in range(1, 9)]
                with guard:
                    tickets.extend(own)
            except Exception as exc:
                with guard:
                    errors.append(exc)
        threads = [threading.Thread(target=worker, args=(offset,)) for offset in (0, 8, 16, 24)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(3)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(errors, [])
        self.assertEqual(sorted(t.sequence for t in tickets), list(range(1, 33)))
        self.assertEqual([queue.dispatch_next().ticket.sequence for _ in tickets], list(range(1, 33)))
        self.assertEqual(len(queue.snapshot().bindings), 32)

    def test_concurrent_drain_publishes_each_request_once(self):
        queue = running()
        for number in range(1, 33):
            enqueue(queue, number)
        completions, errors = [], []
        guard = threading.Lock()
        def worker():
            try:
                own = [queue.dispatch_next() for _ in range(8)]
                with guard:
                    completions.extend(own)
            except Exception as exc:
                with guard:
                    errors.append(exc)
        threads = [threading.Thread(target=worker) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(3)
        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertEqual(errors, [])
        self.assertEqual(sorted(r.ticket.sequence for r in completions), list(range(1, 33)))
        self.assertEqual(sorted(r.revision for r in completions), list(range(5, 37)))
        self.assertEqual(len(queue.snapshot().bindings), 32)
        self.assertIsNone(queue.dispatch_next())

    def test_paused_first_calculation_serializes_second_without_lost_update(self):
        queue = running()
        enqueue(queue, 1)
        enqueue(queue, 2, 'stop', queue.snapshot().current_id)
        entered, release, attempted, second_done = [threading.Event() for _ in range(4)]
        original = M.BrokerModel.dispatch
        calls, results, errors = [], [], []
        def calculation(model, raw, *, peer):
            calls.append(model)
            if len(calls) == 1:
                entered.set()
                if not release.wait(3):
                    raise RuntimeError('test fixture release timed out')
            return original(model, raw, peer=peer)
        def worker(second=False):
            if second:
                attempted.set()
            try:
                results.append(queue.dispatch_next())
            except Exception as exc:
                errors.append(exc)
            finally:
                if second:
                    second_done.set()
        first = threading.Thread(target=worker)
        second = threading.Thread(target=worker, args=(True,))
        with patch.object(M.BrokerModel, 'dispatch', calculation):
            first.start()
            try:
                self.assertTrue(entered.wait(2))
                second.start()
                self.assertTrue(attempted.wait(2))
                self.assertFalse(second_done.is_set())
                self.assertEqual(len(calls), 1)
            finally:
                release.set()
                first.join(3)
                if second.ident is not None:
                    second.join(3)
        self.assertFalse(first.is_alive())
        self.assertFalse(second.is_alive())
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 2)
        self.assertEqual(len(calls[0].bindings), 0)
        self.assertEqual(len(calls[1].bindings), 1)
        self.assertEqual(len(queue.snapshot().bindings), 2)
        self.assertEqual(queue.snapshot()._current().state, M.State.STOP_REQUESTED)
        self.assertFalse(queue.snapshot()._current().cleanup_confirmed)


if __name__ == '__main__':
    unittest.main()
