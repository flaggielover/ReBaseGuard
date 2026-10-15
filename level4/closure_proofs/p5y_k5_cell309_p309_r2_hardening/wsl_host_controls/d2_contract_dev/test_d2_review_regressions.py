"""Review regressions and real signed synthetic protocol chains; NO mocks.

Only pre-generated public message/signature fixtures; no private numbers, key
generation, signing operation, Windows helper, host query or actual workload.
"""
from dataclasses import replace
import hashlib
import unittest

import d2_broker_model as B
import d2_chain as C
import d2_observer as O
import d2_signature as V
from signed_protocol_vectors import SIGNED_PROTOCOL_VECTORS
from test_d2_complete import PEER, chain, envelope, session


def bundle(bits=2048):
    row = next(row for row in SIGNED_PROTOCOL_VECTORS if row[0] == bits)
    return V.PublicNumbers(int(row[1], 16), row[2]), {
        label: (bytes.fromhex(message), bytes.fromhex(signature))
        for label, message, signature in row[3]}


def real_chain(bits=2048):
    public, messages = bundle(bits)
    model = chain().broker
    bound = session(model.current_id, public=public, pin=public.fingerprint())
    return C._fixture_chain(bound, model, synthetic_only=True), messages


def receive(model, message, *, now, completed=None):
    return model.receive(envelope(*message), peer=PEER, now_ms=now,
                         completed_ms=now if completed is None else completed)


def occupied_stop_id(model):
    """Reproduce the original fixed-ID collision using a legitimate status."""
    identifier = hashlib.sha256(('D2_SESSION_STOP/1:' + model.session.session_id + ':' +
                                 model.session.generation).encode('ascii')).hexdigest()[:32]
    status = O.canonical(dict(protocol='P309_DEV_BROKER_CONTROL/2',
                              request_id=identifier, operation='status',
                              generation=model.session.generation))
    out = model.broker.dispatch(status, peer=model.monitor)
    assert out.receipt.code == 'OK'
    return replace(model, broker=out.model), identifier


class ReviewRegressions(unittest.TestCase):
    # These FOUR methods are also run against the immutable original commit to
    # record the supplied counterexamples before repair.
    def test_new_challenge_does_not_extend_observation_liveness(self):
        model, messages = real_chain()
        pending, _ = model.request('a' * 64, now_ms=0)
        accepted = receive(pending, messages['first'], now=60000)
        self.assertFalse(accepted.session.terminal)
        pending, raw = accepted.request('b' * 64, now_ms=165000)
        self.assertIsNotNone(raw)  # request at the original105s boundary
        failed = receive(pending, messages['late_second'], now=225000)
        self.assertTrue(failed.session.terminal)
        self.assertEqual(failed.session.reason, 'MONITOR_GAP')
        self.assertEqual(failed.session.model_observations, 1)
        self.assertEqual(failed.broker._current().state, B.State.STOP_REQUESTED)

    def test_status_cannot_occupy_internal_same_generation_stop(self):
        original, identifier = occupied_stop_id(chain())
        failed = original.transport_lost()
        self.assertEqual(failed.broker._current().state, B.State.STOP_REQUESTED)
        self.assertTrue(failed.stop_receipt.stop_requested)
        self.assertFalse(failed.stop_receipt.cleanup_confirmed)
        self.assertEqual(failed.broker.bindings, original.broker.bindings)
        # Ordinary changed-content ID reuse remains forbidden, even after the
        # owner-internal failure path has latched stop.
        raw = O.canonical(dict(protocol='P309_DEV_BROKER_CONTROL/2', request_id=identifier,
                               operation='stop', generation=original.session.generation))
        ordinary = failed.broker.dispatch(raw, peer=original.monitor)
        self.assertEqual(ordinary.receipt.code, 'REQUEST_ID_REUSED')
        self.assertIs(ordinary.model, failed.broker)

    def test_sample_end_not_future_at_receipt_despite_verification_delay(self):
        model, messages = real_chain()
        pending, _ = model.request('a' * 64, now_ms=0)
        self.assertTrue(pending.session.public.verify(*messages['future']))
        failed = receive(pending, messages['future'], now=60000, completed=90000)
        self.assertTrue(failed.session.terminal)
        self.assertEqual(failed.session.reason, 'INTERVAL_NOT_CURRENT')
        self.assertEqual(failed.session.model_observations, 0)

    def test_negative_modulus_rejected_at_every_supported_width(self):
        for bits in (2048, 3072, 4096):
            public, _ = bundle(bits)
            self.assertEqual((-public.n).bit_length(), bits)
            with self.assertRaises(ValueError):
                V.PublicNumbers(-public.n, public.e)

    def test_independent_liveness_deadline_checked_after_verification(self):
        model, messages = real_chain()
        pending, _ = model.request('a' * 64, now_ms=0)
        accepted = receive(pending, messages['first'], now=60000)
        pending, _ = accepted.request('b' * 64, now_ms=105000)
        failed = receive(pending, messages['boundary_second'], now=165000, completed=165001)
        self.assertEqual(failed.session.reason, 'MONITOR_GAP')
        self.assertEqual(failed.session.model_observations, 1)

    def test_exact_liveness_boundary_still_accepts_valid_signed_observation(self):
        model, messages = real_chain()
        pending, _ = model.request('a' * 64, now_ms=0)
        accepted = receive(pending, messages['first'], now=60000)
        pending, _ = accepted.request('b' * 64, now_ms=105000)
        final = receive(pending, messages['boundary_second'], now=165000)
        self.assertFalse(final.session.terminal)
        self.assertEqual(final.session.model_observations, 2)
        self.assertEqual(final.session.liveness_anchor_ms, 165000)

    def test_pending_tick_never_replaces_observation_deadline(self):
        model, messages = real_chain()
        pending, _ = model.request('a' * 64, now_ms=0)
        accepted = receive(pending, messages['first'], now=60000)
        pending, _ = accepted.request('b' * 64, now_ms=165000)
        failed = pending.tick(now_ms=165001)
        self.assertEqual(failed.session.reason, 'MONITOR_GAP')
        self.assertEqual(failed.broker._current().state, B.State.STOP_REQUESTED)

    def test_internal_stop_is_idempotent_and_allocates_no_request_id(self):
        model = chain()
        first = B._internal_stop(model.broker, generation=model.session.generation, peer=model.monitor)
        again = B._internal_stop(first.model, generation=model.session.generation, peer=model.monitor)
        self.assertEqual(first.model.bindings, model.broker.bindings)
        self.assertIs(again.model, first.model)
        self.assertTrue(again.receipt.duplicate)
        self.assertFalse(again.receipt.cleanup_confirmed)

    def test_internal_stop_with_full_request_table_retains_all_fences(self):
        original = chain()
        bindings = tuple(B._Binding(f'{i:032x}', '0' * 64) for i in range(B.MAX_REQUEST_IDS))
        model = replace(original.broker, bindings=bindings)
        stopped = B._internal_stop(model, generation=model.current_id, peer=original.monitor)
        self.assertEqual(stopped.model._current().state, B.State.STOP_REQUESTED)
        self.assertIs(stopped.model.bindings, bindings)
        self.assertFalse(stopped.model.epoch_unknown)

    def test_internal_stop_stale_generation_cannot_touch_replacement(self):
        model = chain().transport_lost()
        model = model._fixture_event('begin_cleanup', generation=model.broker.current_id)
        proof = B._SyntheticCleanup(True, True, True, True, True, True, True)
        model = model._fixture_event('cleanup_proof', generation=model.broker.current_id, proof=proof)
        newer = B._fixture_prepare(model.broker)
        for event in ('begin_start', 'dispatch_start', 'start_completed'):
            newer = B._fixture_event(newer, event, generation=newer.current_id)
        refused = B._internal_stop(newer, generation=model.session.generation, peer=model.monitor)
        self.assertEqual(refused.receipt.code, 'STALE_GENERATION')
        self.assertIs(refused.model, newer)
        self.assertEqual(newer._current().state, B.State.RUNNING)

    def test_internal_stop_requires_non_null_exact_generation_and_synthetic_monitor(self):
        model = chain()
        for generation in (None, True, '', 'f' * 31, 'F' * 32):
            out = B._internal_stop(model.broker, generation=generation, peer=model.monitor)
            self.assertEqual(out.receipt.code, 'STALE_GENERATION')
            self.assertIs(out.model, model.broker)
        for peer in (None, B.SyntheticPeer('p309-relay', 1, model.broker.monitor_instance),
                     replace(model.monitor, monitor_epoch=2),
                     replace(model.monitor, monitor_instance='other')):
            out = B._internal_stop(model.broker, generation=model.session.generation, peer=peer)
            self.assertEqual(out.receipt.code, 'PEER_REFUSED')
            self.assertIs(out.model, model.broker)

    def test_id_collision_during_armed_or_inflight_start_still_latches_stop(self):
        for state in ('armed', 'starting'):
            model, _ = occupied_stop_id(chain(state))
            failed = model.transport_lost()
            self.assertEqual(failed.broker._current().state, B.State.STOP_REQUESTED)
            if state == 'armed':
                self.assertTrue(failed.broker._current().start_suppressed)
            else:
                completed = failed._fixture_event('start_completed', generation=failed.broker.current_id)
                self.assertEqual(completed.broker._current().state, B.State.CLEANUP_PENDING)
                self.assertFalse(completed.stop_receipt.cleanup_confirmed)

    def test_internal_stop_budget_exhaustion_latches_unknown_without_erasing_history(self):
        model = chain()
        exhausted = replace(model.broker, event_count=B.MAX_EVENTS)
        stopped = B._internal_stop(exhausted, generation=model.session.generation, peer=model.monitor)
        self.assertTrue(stopped.model.epoch_unknown)
        self.assertTrue(stopped.model.budget_exhausted)
        self.assertTrue(stopped.receipt.stop_requested)
        self.assertFalse(stopped.receipt.cleanup_confirmed)
        self.assertEqual(stopped.model.bindings, exhausted.bindings)

    def test_zero_even_and_negative_public_numbers_refused_while_positive_supported(self):
        for bits in (2048, 3072, 4096):
            public, messages = bundle(bits)
            self.assertTrue(public.verify(*messages['first']))
            for invalid in (0, -1, -(1 << (bits - 1)) - 1, public.n - 1):
                with self.assertRaises(ValueError):
                    V.PublicNumbers(invalid, public.e)


class RealSignedProtocol(unittest.TestCase):
    def test_all_18_public_protocol_signatures_verify_without_mock(self):
        self.assertEqual(len(SIGNED_PROTOCOL_VECTORS), 3)
        for bits in (2048, 3072, 4096):
            public, messages = bundle(bits)
            self.assertEqual(len(messages), 6)
            for label, pair in messages.items():
                with self.subTest(bits=bits, label=label):
                    self.assertTrue(public.verify(*pair))

    def test_real_session_roundtrip_preserves_raw_bytes_sequence_and_checkpoint(self):
        for bits in (2048, 3072, 4096):
            model, messages = real_chain(bits)
            pending, _ = model.session.request('a' * 64, now_ms=0)
            accepted = receive(pending, messages['first'], now=60000)
            self.assertFalse(accepted.terminal)
            self.assertEqual((accepted.sequence, accepted.model_observations), (2, 1))
            self.assertEqual(accepted.head, O.checkpoint(*messages['first']))
            self.assertTrue(messages['first'][0].startswith(b' \r\n'))
            pending, _ = accepted.request('b' * 64, now_ms=60000)
            final = receive(pending, messages['second'], now=120000)
            self.assertFalse(final.terminal)
            self.assertEqual(final.model_observations, 2)
            self.assertEqual(final.head, O.checkpoint(*messages['second']))

    def test_real_chain_two_valid_observations_then_valid_signed_busy_stop(self):
        for bits in (2048, 3072, 4096):
            model, messages = real_chain(bits)
            for nonce, label, issue, received in (('a', 'first', 0, 60000),
                                                 ('b', 'second', 60000, 120000)):
                pending, _ = model.request(nonce * 64, now_ms=issue)
                model = receive(pending, messages[label], now=received)
                self.assertFalse(model.session.terminal)
                self.assertEqual(model.broker._current().state, B.State.RUNNING)
            self.assertEqual(model.session.model_observations, 2)
            pending, _ = model.request('c' * 64, now_ms=120000)
            failed = receive(pending, messages['busy'], now=180000)
            self.assertEqual(failed.session.reason, 'OBSERVATION_UNSAFE_OR_UNKNOWN')
            self.assertEqual(failed.broker._current().state, B.State.STOP_REQUESTED)
            self.assertFalse(failed.stop_receipt.cleanup_confirmed)

    def test_real_tampering_wrong_key_and_wrong_pin_are_refused(self):
        original, messages = real_chain()
        message, signature = messages['first']
        tampered_message = message.replace(b'"quiet":true', b'"quiet":false')
        self.assertNotEqual(message, tampered_message)
        for pair in ((tampered_message, signature),
                     (message, bytes([signature[0] ^ 1]) + signature[1:])):
            pending, _ = original.request('a' * 64, now_ms=0)
            self.assertEqual(receive(pending, pair, now=60000).session.reason, 'SIGNATURE_REFUSED')
        wrong_key, _ = real_chain(3072)
        pending, _ = wrong_key.request('a' * 64, now_ms=0)
        self.assertEqual(receive(pending, messages['first'], now=60000).session.reason, 'SIGNATURE_REFUSED')
        bad_pin = replace(original, session=replace(original.session, pin='f' * 64))
        pending, _ = bad_pin.request('a' * 64, now_ms=0)
        self.assertEqual(receive(pending, messages['first'], now=60000).session.reason, 'PUBLIC_PIN_MISMATCH')

    def test_real_signed_replay_cross_session_and_old_checkpoint_cannot_resume(self):
        original, messages = real_chain()
        pending, _ = original.request('a' * 64, now_ms=0)
        accepted = receive(pending, messages['first'], now=60000)
        replayed = receive(accepted, messages['first'], now=60000)
        self.assertEqual(replayed.session.reason, 'NO_OUTSTANDING_CHALLENGE')
        self.assertIsNone(replayed.request('b' * 64, now_ms=60000)[1])
        pending, _ = accepted.request('b' * 64, now_ms=60000)
        self.assertEqual(receive(pending, messages['first'], now=120000).session.reason,
                         'CHALLENGE_MISMATCH')
        other = replace(original, session=replace(original.session, session_id='f' * 64))
        pending, _ = other.request('a' * 64, now_ms=0)
        self.assertEqual(receive(pending, messages['first'], now=60000).session.reason,
                         'CHALLENGE_MISMATCH')

    def test_valid_real_signature_still_grants_no_actual_host_or_execution_authority(self):
        original, messages = real_chain()
        pending, _ = original.request('a' * 64, now_ms=0)
        accepted = receive(pending, messages['first'], now=60000)
        self.assertEqual(accepted.session.model_observations, 1)
        for row in (accepted.diagnostic(), accepted.session.diagnostic()):
            self.assertEqual(row['formal_admission'], 'BLOCKED')
            for key in ('actual_peer_authenticated', 'actual_os_effects', 'route_accepted',
                        'deployment_authorized', 'execution_authorized',
                        'qualification_authorized', 'target_execution_authorized'):
                self.assertIs(row[key], False, key)
        self.assertFalse(accepted.session.diagnostic()['actual_host_facts_validated'])
        self.assertFalse(accepted.session.diagnostic()['trusted_enrollment'])


if __name__ == '__main__':
    unittest.main()
