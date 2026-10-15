from dataclasses import FrozenInstanceError, replace
import itertools
import unittest

import d2_broker_model as M
from test_d2_wire import message


FULL = M._SyntheticCleanup(True, True, True, True, True, True, True)


def peer(model, role='p309-monitor'):
    return M.SyntheticPeer(role, model.epoch, model.monitor_instance)


def event(model, kind, **kwargs):
    return M._fixture_event(model, kind, generation=model.current_id, **kwargs)


def fresh():
    return M._fixture_prepare(M.BrokerModel.new(synthetic_only=True))


def running():
    model = fresh()
    for kind in ('begin_start', 'dispatch_start', 'start_completed'):
        model = event(model, kind)
    return model


def stop(model, request_id='1' * 32):
    return model.dispatch(message(request_id=request_id, operation='stop', generation=model.current_id),
                          peer=peer(model))


def stopped(model):
    model = stop(model).model
    model = event(model, 'begin_cleanup')
    return event(model, 'cleanup_proof', proof=FULL)


class BrokerPolicy(unittest.TestCase):
    def assert_blocked(self, receipt):
        row = receipt.as_dict()
        self.assertEqual(row['scope'], 'SYNTHETIC_PURE_MEMORY_MODEL_ONLY')
        self.assertEqual(row['formal_admission'], 'BLOCKED')
        for key in ('actual_peer_authenticated', 'actual_os_effects', 'route_accepted',
                    'deployment_authorized', 'execution_authorized',
                    'qualification_authorized', 'target_execution_authorized'):
            self.assertIs(row[key], False, key)

    def test_explicit_synthetic_factory_scope(self):
        for value in (False, 1, 'true', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                M.BrokerModel.new(synthetic_only=value)

    def test_only_simulated_monitor_instance_can_dispatch(self):
        model = running()
        for candidate in (None, {'role': 'p309-monitor'}, peer(model, 'p309-relay'),
                          peer(model, 'p309-runner'), peer(model, 'root'),
                          M.SyntheticPeer('p309-monitor', True),
                          M.SyntheticPeer('p309-monitor', model.epoch + 1)):
            out = model.dispatch(message(operation='stop', generation=model.current_id), peer=candidate)
            self.assertEqual(out.receipt.code, 'PEER_REFUSED')
            self.assertIs(out.model, model)
            self.assert_blocked(out.receipt)

    def test_public_start_arm_reset_and_claimed_identity_never_mutate(self):
        model = M.BrokerModel.new(synthetic_only=True)
        for operation in ('start', 'arm', 'rearm', 'reset', 'StartTransientUnit'):
            out = model.dispatch(message(operation=operation), peer=peer(model))
            self.assertEqual(out.receipt.code, 'BAD_REQUEST')
            self.assertIs(out.model, model)
        out = model.dispatch(message(uid=0), peer=peer(model))
        self.assertEqual(out.receipt.code, 'BAD_REQUEST')
        self.assertIs(out.model, model)

    def test_different_monitor_instance_in_same_epoch_is_refused(self):
        model = running()
        wrong = M.SyntheticPeer('p309-monitor', model.epoch, 'other-synthetic-monitor')
        out = model.dispatch(message(operation='stop', generation=model.current_id), peer=wrong)
        self.assertEqual(out.receipt.code, 'PEER_REFUSED')
        self.assertIs(out.model, model)
        self.assertEqual(model._current().monitor_instance, model.monitor_instance)

    def test_monitor_restart_within_broker_epoch_stops_and_invalidates_old_instance(self):
        before = running()
        model = event(before, 'monitor_restart')
        self.assertEqual(model.epoch, before.epoch)
        self.assertNotEqual(model.monitor_instance, before.monitor_instance)
        self.assertTrue(model.epoch_unknown)
        self.assertEqual(model.dispatch(message(), peer=peer(before)).receipt.code, 'PEER_REFUSED')
        out = model.dispatch(message(), peer=peer(model))
        self.assertEqual(out.receipt.code, 'RECOVERY_UNKNOWN')
        self.assertFalse(out.receipt.cleanup_confirmed)

    def test_status_does_not_allocate_or_start_generation(self):
        model = M.BrokerModel.new(synthetic_only=True)
        out = model.dispatch(message(), peer=peer(model))
        self.assertEqual(out.receipt.state, M.State.UNARMED)
        self.assertEqual(out.model.generations, ())
        self.assertIsNone(out.model.current_id)
        self.assert_blocked(out.receipt)

    def test_stop_returns_new_snapshot_and_never_os_completion(self):
        model = running()
        out = stop(model)
        self.assertEqual(model._current().state, M.State.RUNNING)
        self.assertEqual(out.model._current().state, M.State.STOP_REQUESTED)
        self.assertTrue(out.receipt.stop_requested)
        self.assertFalse(out.receipt.cleanup_confirmed)
        with self.assertRaises(FrozenInstanceError):
            model.current_id = None
        self.assert_blocked(out.receipt)

    def test_identical_stop_is_idempotent_without_budget_growth(self):
        first = stop(running())
        second = stop(first.model)
        self.assertTrue(second.receipt.duplicate)
        self.assertEqual(second.model, first.model)
        self.assertFalse(second.receipt.cleanup_confirmed)

    def test_changed_content_request_id_is_refused(self):
        model = running()
        seen = model.dispatch(message(generation=model.current_id), peer=peer(model)).model
        out = stop(seen)  # Same ID, different operation/content.
        self.assertEqual(out.receipt.code, 'REQUEST_ID_REUSED')
        self.assertIs(out.model, seen)
        self.assertEqual(out.model._current().state, M.State.RUNNING)

    def test_stop_without_generation_cannot_reserve_future_authority(self):
        model = M.BrokerModel.new(synthetic_only=True)
        out = model.dispatch(message(operation='stop'), peer=peer(model))
        self.assertIs(out.model, model)
        self.assertEqual(out.receipt.code, 'BAD_REQUEST')

    def test_stop_while_armed_revokes_start_and_can_only_cleanup(self):
        model = stop(fresh()).model
        self.assertTrue(model._current().start_suppressed)
        self.assertTrue(model._current().permit_consumed)
        self.assertEqual(event(model, 'begin_start'), model)
        model = event(model, 'begin_cleanup')
        self.assertEqual(event(model, 'cleanup_proof', proof=FULL)._current().state, M.State.STOPPED)

    def test_stop_before_dispatch_suppresses_start(self):
        model = event(fresh(), 'begin_start')
        model = stop(model).model
        self.assertFalse(model._current().start_pending)
        self.assertFalse(event(model, 'dispatch_start')._current().dispatch_issued)
        unknown = event(model, 'start_completed')
        self.assertTrue(unknown.epoch_unknown)
        self.assertNotEqual(unknown._current().state, M.State.RUNNING)

    def test_stop_during_inflight_start_rejects_early_cleanup_and_late_running(self):
        model = event(event(fresh(), 'begin_start'), 'dispatch_start')
        model = stop(model).model
        model = event(model, 'begin_cleanup')
        self.assertIs(event(model, 'cleanup_proof', proof=FULL), model)
        model = event(model, 'start_completed')
        self.assertEqual(model._current().state, M.State.CLEANUP_PENDING)
        self.assertFalse(model._current().start_pending)
        self.assertTrue(model._current().stop_latched)
        self.assertEqual(event(model, 'cleanup_proof', proof=FULL)._current().state, M.State.STOPPED)

    def test_duplicate_internal_start_cannot_dispatch_twice(self):
        model = event(fresh(), 'begin_start')
        self.assertEqual(event(model, 'begin_start'), model)
        model = event(model, 'dispatch_start')
        self.assertEqual(event(model, 'dispatch_start'), model)
        model = event(model, 'start_completed')
        self.assertEqual(event(model, 'begin_start'), model)
        self.assertEqual(len(model.generations), 1)

    def test_owned_exit_needs_cleanup_proof(self):
        model = event(running(), 'owned_exit')
        self.assertEqual(model._current().state, M.State.CLEANUP_PENDING)
        self.assertTrue(model._current().stop_latched)
        self.assertFalse(model._current().cleanup_confirmed)
        done = event(model, 'cleanup_proof', proof=FULL)
        self.assertEqual(done._current().state, M.State.STOPPED)
        self.assertTrue(done._current().cleanup_confirmed)

    def test_every_missing_cleanup_predicate_prevents_completion(self):
        model = event(stop(running()).model, 'begin_cleanup')
        for field in vars(FULL):
            with self.subTest(field=field):
                incomplete = replace(FULL, **{field: False})
                result = event(model, 'cleanup_proof', proof=incomplete)
                self.assertNotEqual(result._current().state, M.State.STOPPED)
                self.assertFalse(result._current().cleanup_confirmed)
                if field == 'identity_matches':
                    self.assertTrue(result.epoch_unknown)

    def test_synthetic_proof_cannot_arrive_through_wire_or_numeric_booleans(self):
        with self.assertRaises(ValueError):
            replace(FULL, cgroup_empty=1)
        model = running()
        out = model.dispatch(message(operation='stop', generation=model.current_id,
                                     cleanup_proof=vars(FULL)), peer=peer(model))
        self.assertEqual(out.receipt.code, 'BAD_REQUEST')
        self.assertIs(out.model, model)

    def test_mismatched_start_identity_enters_unknown(self):
        model = event(event(fresh(), 'begin_start'), 'dispatch_start')
        model = event(model, 'start_completed', identity_matches=False)
        self.assertTrue(model.epoch_unknown)
        self.assertTrue(model._current().stop_latched)
        self.assertFalse(model._current().cleanup_confirmed)

    def test_completed_stop_is_terminal_and_duplicate_returns_model_only_proof(self):
        model = stopped(running())
        for kind in ('begin_start', 'dispatch_start', 'start_completed', 'owned_exit'):
            self.assertIs(event(model, kind), model)
        out = stop(model)
        self.assertEqual(out.receipt.code, 'STOPPED_MODEL')
        self.assertTrue(out.receipt.cleanup_confirmed)
        self.assertTrue(out.receipt.duplicate)
        self.assert_blocked(out.receipt)
        copied = out.receipt.as_dict()
        copied['execution_authorized'] = True
        self.assert_blocked(out.receipt)

    def test_restart_with_live_generation_is_unknown_and_old_peer_invalid(self):
        before = running()
        model = event(before, 'restart')
        self.assertEqual(model.epoch, before.epoch + 1)
        self.assertTrue(model.epoch_unknown)
        self.assertEqual(model._current().state, M.State.RECOVERY_UNKNOWN)
        self.assertEqual(model.dispatch(message(), peer=peer(before)).receipt.code, 'PEER_REFUSED')
        with self.assertRaises(ValueError):
            M._fixture_prepare(model)
        self.assertIs(event(model, 'cleanup_proof', proof=FULL), model)

    def test_restart_preserves_old_stopped_history_but_not_current_quiescence(self):
        before = stopped(running())
        model = event(before, 'restart')
        self.assertEqual(model.generations, before.generations)
        out = stop(model)
        self.assertEqual(out.receipt.code, 'RECOVERY_UNKNOWN')
        self.assertEqual(out.receipt.state, M.State.RECOVERY_UNKNOWN)
        self.assertEqual(out.receipt.historical_state, M.State.STOPPED)
        self.assertFalse(out.receipt.cleanup_confirmed)
        self.assert_blocked(out.receipt)

    def test_mismatched_late_completion_preserves_stopped_history_but_sets_guard(self):
        before = stopped(running())
        model = event(before, 'start_completed', identity_matches=False)
        self.assertEqual(model.generations, before.generations)
        self.assertTrue(model.epoch_unknown)
        out = model.dispatch(message(request_id='2' * 32), peer=peer(model))
        self.assertEqual(out.receipt.historical_state, M.State.STOPPED)
        self.assertFalse(out.receipt.cleanup_confirmed)

    def test_mismatched_late_cleanup_invalidates_current_quiescence_not_history(self):
        before = stopped(running())
        model = event(before, 'cleanup_proof', proof=replace(FULL, identity_matches=False))
        self.assertEqual(model.generations, before.generations)
        self.assertTrue(model.epoch_unknown)
        self.assertEqual(stop(model).receipt.code, 'RECOVERY_UNKNOWN')

    def test_recovery_failure_preserves_terminal_record_and_refuses_rearm(self):
        before = stopped(running())
        model = event(before, 'recovery_failure')
        self.assertEqual(model.generations, before.generations)
        with self.assertRaises(ValueError):
            M._fixture_prepare(model)
        self.assertTrue(model.epoch_unknown)

    def test_new_fixture_generation_requires_old_terminal_cleanup(self):
        with self.assertRaises(ValueError):
            M._fixture_prepare(running())
        old = stopped(running())
        new = M._fixture_prepare(old)
        self.assertNotEqual(new.current_id, old.current_id)
        self.assertEqual(new.generations[0], old.generations[0])
        self.assertEqual(new.bindings, old.bindings)
        self.assertEqual(new._current().state, M.State.ARMED)

    def test_old_generation_cached_stop_is_stale_before_dedup(self):
        old = stopped(running())
        old_request = message(operation='stop', generation=old.current_id)
        new = M._fixture_prepare(old)
        for kind in ('begin_start', 'dispatch_start', 'start_completed'):
            new = event(new, kind)
        out = new.dispatch(old_request, peer=peer(new))
        self.assertEqual(out.receipt.code, 'STALE_GENERATION')
        self.assertFalse(out.receipt.duplicate)
        self.assertIsNone(out.receipt.state)
        self.assertIs(out.model, new)
        self.assertIs(M._fixture_event(new, 'start_completed', generation=old.current_id), new)

    def test_request_id_cannot_be_repurposed_across_retained_generations(self):
        new = M._fixture_prepare(stopped(running()))
        out = stop(new)  # ID1 was consumed by old-G stop; new G changes content.
        self.assertEqual(out.receipt.code, 'REQUEST_ID_REUSED')
        self.assertIs(out.model, new)

    def test_request_budget_retains_fences_and_does_not_acknowledge_cleanup(self):
        model = running()
        for index in range(M.MAX_REQUEST_IDS):
            out = model.dispatch(message(request_id=format(index, '032x'), generation=model.current_id),
                                 peer=peer(model))
            self.assertEqual(out.receipt.code, 'OK')
            model = out.model
        duplicate = model.dispatch(message(request_id='0' * 32, generation=model.current_id), peer=peer(model))
        self.assertTrue(duplicate.receipt.duplicate)
        self.assertEqual(duplicate.model, model)
        exhausted = model.dispatch(message(request_id='f' * 32), peer=peer(model))
        self.assertEqual(exhausted.receipt.code, 'MODEL_BUDGET_EXHAUSTED')
        self.assertTrue(exhausted.model.epoch_unknown)
        self.assertTrue(exhausted.receipt.stop_requested)
        self.assertEqual(exhausted.model.bindings, model.bindings)
        self.assertFalse(exhausted.receipt.cleanup_confirmed)

    def test_generation_budget_preserves_all_terminal_records(self):
        model = M.BrokerModel.new(synthetic_only=True)
        for index in range(M.MAX_GENERATIONS):
            model = M._fixture_prepare(model)
            model = stop(model, request_id=format(index, '032x')).model
            model = event(model, 'begin_cleanup')
            model = event(model, 'cleanup_proof', proof=FULL)
        exhausted = M._fixture_prepare(model)
        self.assertTrue(exhausted.epoch_unknown)
        self.assertTrue(exhausted.budget_exhausted)
        self.assertEqual(exhausted.generations, model.generations)
        self.assertEqual(len(exhausted.generations), M.MAX_GENERATIONS)

    def test_event_budget_never_rolls_over_or_clears_unknown_guard(self):
        model = M.BrokerModel.new(synthetic_only=True)
        for _ in range(M.MAX_EVENTS):
            model = event(model, 'restart')
        self.assertEqual(model.event_count, M.MAX_EVENTS)
        exhausted = event(model, 'restart')
        self.assertEqual(exhausted.event_count, M.MAX_EVENTS)
        self.assertEqual(exhausted.epoch, model.epoch)
        self.assertTrue(exhausted.epoch_unknown)
        self.assertTrue(exhausted.budget_exhausted)

    def test_finite_start_stop_completion_interleavings_never_reopen_after_stop(self):
        for order in itertools.permutations(('dispatch_start', 'stop', 'start_completed')):
            model = event(fresh(), 'begin_start')
            latched = False
            for action in order:
                model = stop(model).model if action == 'stop' else event(model, action)
                latched = latched or model.epoch_unknown or model._current().stop_latched
                if latched:
                    self.assertNotEqual(model._current().state, M.State.RUNNING, order)
                self.assert_blocked(model.dispatch(message(), peer=peer(model)).receipt)

    def test_stale_status_and_request_flood_do_not_mutate_current_generation(self):
        old = stopped(running())
        new = M._fixture_prepare(old)
        for index in range(20):
            out = new.dispatch(message(request_id=format(index, '032x'), generation=old.current_id), peer=peer(new))
            self.assertEqual(out.receipt.code, 'STALE_GENERATION')
            self.assertIs(out.model, new)


if __name__ == '__main__':
    unittest.main()
