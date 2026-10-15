"""Consolidated D2 synthetic contracts; no host/collector/helper or key creation.

RSA known answers use real public verification. Positive SESSION fixtures patch
only verification to simulate a trusted result: they are explicitly not a real
signed-observation end-to-end test. Negative dummy signatures use the verifier.
"""
from dataclasses import FrozenInstanceError, replace
import base64
import json
import unittest
from unittest.mock import patch

import d2_broker_model as B
import d2_chain as C
import d2_ingress_model as I
import d2_ingress_wire as W
import d2_observer as O
import d2_session as S
import d2_signature as V
from public_rsa_vectors import PUBLIC_RSA_VECTORS

PUBLIC = next(row for row in PUBLIC_RSA_VECTORS if row[0] == 2048 and row[2] == 65537 and row[5])
KEY = V.PublicNumbers(int(PUBLIC[1], 16), PUBLIC[2])
ENROLLED = O.Enrollment('1' * 64, '2' * 64, '3' * 64, '4' * 64)
HOST = ('5' * 64, '6' * 64, '7' * 64)
PEER = I.SyntheticRelay('p309-relay', 'synthetic-relay')
FULL = B._SyntheticCleanup(True, True, True, True, True, True, True)


def facts(start=0, end=60000, **changes):
    return replace(O.FixtureFacts(*HOST, start, end, True, True, True), **changes)


def session(generation='1' * 32, **changes):
    params = dict(enrollment=ENROLLED, host_identity=HOST, public=KEY, pin=KEY.fingerprint(),
                  session_id='8' * 64, baseline_sha256='9' * 64, generation=generation,
                  relay_instance='synthetic-relay', now_ms=0, synthetic_only=True)
    params.update(changes)
    return S._fixture_session(**params)


def challenged(**changes):
    return session(**changes).request('a' * 64, now_ms=0)


def envelope(message, signature=None):
    return O.canonical(dict(protocol=W.PROTOCOL, kind='signed_observation', envelope=dict(
        message_b64=base64.b64encode(message).decode('ascii'),
        signature_b64=base64.b64encode(b'x' * 256 if signature is None else signature).decode('ascii'))))


def fixture_message(raw, owned_facts=None, enrolled=ENROLLED):
    return O._fixture_response(O.client_request(raw, enrolled), enrolled=enrolled,
                               facts=facts() if owned_facts is None else owned_facts,
                               synthetic_only=True)


def receive_fixture(model, raw, *, start=0, end=60000, now=60000, completed=60000, **changes):
    signed = fixture_message(raw, facts(start, end, **changes))
    with patch.object(V.PublicNumbers, 'verify', return_value=True):
        return model.receive(envelope(signed), peer=PEER, now_ms=now, completed_ms=completed)


def broker(state='running'):
    model = B._fixture_prepare(B.BrokerModel.new(synthetic_only=True))
    if state in ('starting', 'running'):
        model = B._fixture_event(model, 'begin_start', generation=model.current_id)
        model = B._fixture_event(model, 'dispatch_start', generation=model.current_id)
    if state == 'running':
        model = B._fixture_event(model, 'start_completed', generation=model.current_id)
    return model


def chain(state='running'):
    model = broker(state)
    return C._fixture_chain(session(model.current_id), model, synthetic_only=True)


class PublicVerification(unittest.TestCase):
    def test_all_public_nist_sha256_known_answers(self):
        self.assertEqual(len(PUBLIC_RSA_VECTORS), 54)
        self.assertEqual(sum(row[5] for row in PUBLIC_RSA_VECTORS), 9)
        for bits, n, e, message, signature, valid, reason in PUBLIC_RSA_VECTORS:
            with self.subTest(bits=bits, exponent=e, expected=valid, reason=reason):
                key = V.PublicNumbers(int(n, 16), e)
                self.assertIs(key.verify(bytes.fromhex(message), bytes.fromhex(signature)), valid)

    def test_message_signature_and_key_substitution_rejected(self):
        message, signature = bytes.fromhex(PUBLIC[3]), bytes.fromhex(PUBLIC[4])
        self.assertTrue(KEY.verify(message, signature))
        self.assertFalse(KEY.verify(message + b'!', signature))
        tampered = bytes([signature[0] ^ 1]) + signature[1:]
        self.assertFalse(KEY.verify(message, tampered))
        other = V.PublicNumbers(KEY.n, 3)
        self.assertFalse(other.verify(message, signature))
        self.assertNotEqual(other.fingerprint(), KEY.fingerprint())

    def test_range_length_and_exact_types_rejected(self):
        raw = bytes.fromhex(PUBLIC[3])
        for signature in (KEY.n.to_bytes(256, 'big'), b'\0' * 256, b'', b'x' * 255,
                          b'x' * 257, 'text', bytearray(b'x' * 256)):
            self.assertFalse(KEY.verify(raw, signature))
        for message in (b'', b'x' * (V.MAX_MESSAGE_BYTES + 1), raw.decode('latin1'), bytearray(raw)):
            self.assertFalse(KEY.verify(message, bytes.fromhex(PUBLIC[4])))

    def test_public_number_budget_and_immutability(self):
        for n, e in ((True, 65537), (3, 65537), (2**2047, 65537),
                     (KEY.n, True), (KEY.n, 2), (KEY.n, 2**32 + 1)):
            with self.subTest(n_bits=n.bit_length(), e=e), self.assertRaises(ValueError):
                V.PublicNumbers(n, e)
        with self.assertRaises(FrozenInstanceError):
            KEY.e = 3


class ObserverContract(unittest.TestCase):
    def test_client_request_contains_no_host_facts(self):
        _, h3 = challenged()
        raw = O.client_request(h3, ENROLLED)
        challenge, enrollment = O.parse_client_request(raw)
        self.assertEqual(challenge, W.parse_observer_request(h3))
        self.assertEqual(enrollment, ENROLLED)
        self.assertEqual(set(json.loads(raw)), {'protocol', 'kind', 'challenge', 'enrollment'})

    def test_injected_facts_commands_and_generic_sign_input_rejected(self):
        _, h3 = challenged()
        for key in ('payload', 'facts', 'cpu', 'policy', 'coverage', 'bytes_to_sign',
                    'command', 'path', 'unit', 'uid', 'pid', 'signature'):
            obj = json.loads(O.client_request(h3, ENROLLED)); obj[key] = 'injected'
            with self.subTest(key=key), self.assertRaises(W.IngressError):
                O._fixture_response(O.canonical(obj), enrolled=ENROLLED,
                                     facts=facts(), synthetic_only=True)

    def test_enrollment_must_match_fixture_owned_configuration(self):
        _, h3 = challenged()
        changed = replace(ENROLLED, runtime='f' * 64)
        with self.assertRaises(W.IngressError):
            O._fixture_response(O.client_request(h3, changed), enrolled=ENROLLED,
                                 facts=facts(), synthetic_only=True)

    def test_bad_enrollment_and_duplicates_refused(self):
        _, h3 = challenged()
        obj = json.loads(O.client_request(h3, ENROLLED))
        for value in (True, 'A' * 64, '0' * 63, 1):
            obj['enrollment']['runtime'] = value
            with self.subTest(value=value), self.assertRaises(W.IngressError):
                O.parse_client_request(O.canonical(obj))
        raw = O.client_request(h3, ENROLLED)
        with self.assertRaises(W.IngressError):
            O.parse_client_request(b'{"enrollment":{},' + raw[1:])

    def test_fixture_owned_facts_construct_response_not_client_claims(self):
        _, raw = challenged()
        message = fixture_message(raw, facts(quiet=False))
        parsed = W.parse_relay_message(envelope(message))
        doc = json.loads(parsed.message)
        self.assertFalse(doc['payload']['facts']['quiet'])
        self.assertEqual(doc['payload']['enrollment'], ENROLLED.as_dict())
        self.assertEqual(doc['baseline_sha256'], '9' * 64)  # binding only

    def test_explicit_fixture_and_fact_types(self):
        _, raw = challenged()
        with self.assertRaises(ValueError):
            O._fixture_response(O.client_request(raw, ENROLLED), enrolled=ENROLLED, facts=facts())
        for changes in ({'quiet': 1}, {'interval_end_ms': -1}, {'host_boot': 'bad'},
                        {'interval_start_ms': True}, {'interval_end_ms': O.MAX_TICK_MS + 1}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                facts(**changes)

    def test_checkpoints_bind_both_message_and_signature(self):
        first = O.checkpoint(b'ab', b'c')
        self.assertNotEqual(first, O.checkpoint(b'a', b'bc'))
        self.assertNotEqual(first, O.checkpoint(b'ab', b'd'))
        self.assertEqual(first, O.checkpoint(b'ab', b'c'))


class SessionContract(unittest.TestCase):
    def test_request_binds_one_outstanding_challenge(self):
        original = session()
        after, raw = original.request('a' * 64, now_ms=0)
        self.assertIsNone(original.pending)
        parsed = W.parse_observer_request(raw)
        self.assertEqual((parsed.sequence, parsed.previous_sha256, parsed.baseline_sha256),
                         (1, '0' * 64, original.baseline_sha256))
        failed, second = after.request('b' * 64, now_ms=1)
        self.assertTrue(failed.terminal)
        self.assertEqual(failed.reason, 'OUTSTANDING_REQUEST')
        self.assertIsNone(second)

    def test_real_verifier_rejects_dummy_signature_in_protocol_message(self):
        model, raw = challenged()
        failed = model.receive(envelope(fixture_message(raw)), peer=PEER, now_ms=60000, completed_ms=60000)
        self.assertEqual(failed.reason, 'SIGNATURE_REFUSED')
        self.assertEqual(failed.model_observations, 0)
        self.assertIsNone(failed.pending)

    def test_wrong_pin_refused_before_verifier(self):
        model, raw = challenged(pin='f' * 64)
        with patch.object(V.PublicNumbers, 'verify', return_value=True) as mocked:
            failed = model.receive(envelope(fixture_message(raw)), peer=PEER,
                                   now_ms=60000, completed_ms=60000)
        self.assertEqual(failed.reason, 'PUBLIC_PIN_MISMATCH')
        mocked.assert_not_called()

    def test_synthetic_verified_observation_advances_only_model_sequence(self):
        model, raw = challenged()
        accepted = receive_fixture(model, raw)
        self.assertFalse(accepted.terminal)
        self.assertEqual((accepted.sequence, accepted.model_observations), (2, 1))
        self.assertIsNone(accepted.pending)
        self.assertEqual(accepted.head, O.checkpoint(fixture_message(raw), b'x' * 256))
        self.assertFalse(accepted.diagnostic()['continuation_authorized'])

    def test_two_synthetic_verified_intervals_chain_checkpoint(self):
        model, first = challenged()
        after = receive_fixture(model, first)
        pending, raw = after.request('b' * 64, now_ms=60000)
        parsed = W.parse_observer_request(raw)
        self.assertEqual(parsed.previous_sha256, after.head)
        self.assertEqual(parsed.sequence, 2)
        final = receive_fixture(pending, raw, start=60000, end=120000, now=120000, completed=120000)
        self.assertFalse(final.terminal)
        self.assertEqual(final.model_observations, 2)
        self.assertNotEqual(final.head, after.head)

    def test_nonce_reuse_across_synthetic_observations_refused(self):
        model, raw = challenged()
        after = receive_fixture(model, raw)
        failed, request = after.request('a' * 64, now_ms=60000)
        self.assertEqual(failed.reason, 'NONCE_INVALID_OR_REUSED')
        self.assertIsNone(request)

    def test_replayed_response_without_or_with_new_challenge_refused(self):
        model, raw = challenged()
        after = receive_fixture(model, raw)
        old = envelope(fixture_message(raw))
        self.assertEqual(after.receive(old, peer=PEER, now_ms=60000, completed_ms=60000).reason,
                         'NO_OUTSTANDING_CHALLENGE')
        pending, _ = after.request('b' * 64, now_ms=60000)
        self.assertEqual(pending.receive(old, peer=PEER, now_ms=60000, completed_ms=60000).reason,
                         'CHALLENGE_MISMATCH')

    def test_wrong_session_baseline_sequence_nonce_and_checkpoint(self):
        model, raw = challenged()
        for key, value in (('session_id', 'f' * 64), ('baseline_sha256', 'f' * 64),
                           ('sequence', 2), ('nonce', 'f' * 64), ('previous_sha256', 'f' * 64)):
            doc = json.loads(fixture_message(raw)); doc[key] = value
            with self.subTest(component=key):
                failed = model.receive(envelope(O.canonical(doc)), peer=PEER,
                                       now_ms=60000, completed_ms=60000)
                self.assertEqual(failed.reason, 'CHALLENGE_MISMATCH')

    def test_wrong_peer_and_transport_failure_terminal(self):
        model, raw = challenged()
        failed = model.receive(envelope(fixture_message(raw)), peer=I.SyntheticRelay('root', 'x'),
                               now_ms=60000, completed_ms=60000)
        self.assertEqual(failed.reason, 'PEER_REFUSED')
        frame = O.canonical(dict(protocol=W.PROTOCOL, kind='transport_failure', reason='EOF'))
        self.assertEqual(model.receive(frame, peer=PEER, now_ms=0, completed_ms=0).reason,
                         'TRANSPORT_EOF')

    def test_deadline_exact_boundary_and_expiry_during_verification(self):
        model, raw = challenged()
        on_boundary = receive_fixture(model, raw, now=105000, completed=105000)
        self.assertFalse(on_boundary.terminal)
        expired = receive_fixture(model, raw, now=60000, completed=105001)
        self.assertEqual(expired.reason, 'RESPONSE_TIMEOUT')
        self.assertEqual(model.tick(now_ms=105001).reason, 'RESPONSE_TIMEOUT')

    def test_idle_tick_and_new_request_cannot_renew_liveness(self):
        model = session()
        for now in (1000, 50000, 100000, 105000):
            model = model.tick(now_ms=now)
            self.assertFalse(model.terminal)
        self.assertEqual(model.tick(now_ms=105001).reason, 'MONITOR_GAP')
        failed, raw = model.request('a' * 64, now_ms=105001)
        self.assertEqual(failed.reason, 'MONITOR_GAP')
        self.assertIsNone(raw)

    def test_regressing_and_invalid_fake_time_refused(self):
        model = session().tick(now_ms=100)
        for now in (99, True, -1, float('nan'), 100.0, O.MAX_TICK_MS + 1):
            with self.subTest(now=now):
                self.assertEqual(model.tick(now_ms=now).reason, 'CLOCK_INVALID')
        pending, raw = challenged()
        self.assertEqual(receive_fixture(pending, raw, now=60000, completed=59999).reason, 'CLOCK_INVALID')

    def test_verifier_exception_is_terminal_without_completion(self):
        model, raw = challenged()
        with patch.object(V.PublicNumbers, 'verify', side_effect=RuntimeError('synthetic fault')):
            failed = model.receive(envelope(fixture_message(raw)), peer=PEER,
                                   now_ms=60000, completed_ms=60000)
        self.assertEqual(failed.reason, 'VERIFICATION_ERROR')
        self.assertEqual(failed.model_observations, 0)

    def test_host_boot_service_and_enrollment_changes_refused(self):
        model, raw = challenged()
        for key in ('host_id', 'host_boot', 'service'):
            with self.subTest(key=key):
                self.assertEqual(receive_fixture(model, raw, **{key: 'f' * 64}).reason,
                                 'HOST_IDENTITY_CHANGED')
        doc = json.loads(fixture_message(raw)); doc['payload']['enrollment']['runtime'] = 'f' * 64
        with patch.object(V.PublicNumbers, 'verify', return_value=True):
            failed = model.receive(envelope(O.canonical(doc)), peer=PEER,
                                   now_ms=60000, completed_ms=60000)
        self.assertEqual(failed.reason, 'ENROLLMENT_CHANGED')

    def test_unknown_coverage_busy_or_unstable_policy_refused(self):
        model, raw = challenged()
        for key in ('coverage_complete', 'quiet', 'policy_stable'):
            with self.subTest(key=key):
                self.assertEqual(receive_fixture(model, raw, **{key: False}).reason,
                                 'OBSERVATION_UNSAFE_OR_UNKNOWN')

    def test_interval_duration_order_and_future_facts_refused(self):
        model, raw = challenged()
        self.assertEqual(receive_fixture(model, raw, end=59999).reason, 'INTERVAL_INVALID')
        self.assertEqual(receive_fixture(model, raw, end=105001, now=105000, completed=105000).reason,
                         'INTERVAL_INVALID')
        self.assertEqual(receive_fixture(model, raw, start=1, end=60001).reason, 'INTERVAL_NOT_CURRENT')
        later, _ = session().request('a' * 64, now_ms=1000)
        self.assertEqual(receive_fixture(later, raw, end=60000).reason, 'INTERVAL_NOT_CURRENT')

    def test_malformed_signed_payload_never_becomes_host_facts(self):
        model, raw = challenged()
        doc = json.loads(fixture_message(raw)); doc['payload']['facts']['quiet'] = 1
        for mutate in (doc, dict(json.loads(fixture_message(raw)), payload={'safe': True})):
            with patch.object(V.PublicNumbers, 'verify', return_value=True):
                failed = model.receive(envelope(O.canonical(mutate)), peer=PEER,
                                       now_ms=60000, completed_ms=60000)
            self.assertEqual(failed.reason, 'FACTS_SHAPE_REFUSED')

    def test_session_budget_retains_fences_and_terminal_failure(self):
        model = replace(session(), sequence=S.MAX_RECORDS + 1)
        failed, raw = model.request('a' * 64, now_ms=0)
        self.assertEqual(failed.reason, 'SESSION_BUDGET_EXHAUSTED')
        self.assertIsNone(raw)
        self.assertEqual(failed.sequence, S.MAX_RECORDS + 1)
        self.assertIs(failed.transport_lost(), failed)
        self.assertIs(failed.tick(now_ms=0), failed)
        self.assertEqual(failed.request('b' * 64, now_ms=0), (failed, None))

    def test_factory_rejects_unscoped_bindings_and_exports_remain_blocked(self):
        for changes in ({'synthetic_only': False}, {'now_ms': True}, {'pin': 'bad'},
                        {'host_identity': list(HOST)}, {'generation': 'bad'}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                session(**changes)
        model, raw = challenged()
        for value in (session(), model, receive_fixture(model, raw), model.transport_lost()):
            row = value.diagnostic()
            self.assertEqual(row['formal_admission'], 'BLOCKED')
            for key in ('actual_peer_authenticated', 'trusted_enrollment', 'actual_host_facts_validated',
                        'observation_accepted', 'continuation_authorized', 'actual_os_effects',
                        'route_accepted', 'deployment_authorized', 'execution_authorized',
                        'qualification_authorized', 'target_execution_authorized'):
                self.assertIs(row[key], False, key)


class StopComposition(unittest.TestCase):
    def test_real_forgery_rejection_requests_stop_of_owned_generation(self):
        original = chain()
        pending, raw = original.request('a' * 64, now_ms=0)
        failed = pending.receive(envelope(fixture_message(raw)), peer=PEER,
                                 now_ms=60000, completed_ms=60000)
        self.assertEqual(original.broker._current().state, B.State.RUNNING)
        self.assertEqual(failed.session.reason, 'SIGNATURE_REFUSED')
        self.assertEqual(failed.broker._current().state, B.State.STOP_REQUESTED)
        self.assertTrue(failed.stop_receipt.stop_requested)
        self.assertFalse(failed.stop_receipt.cleanup_confirmed)

    def test_synthetic_valid_then_busy_chain_stops_without_start_authority(self):
        model, raw = chain().request('a' * 64, now_ms=0)
        with patch.object(V.PublicNumbers, 'verify', return_value=True):
            accepted = model.receive(envelope(fixture_message(raw)), peer=PEER,
                                     now_ms=60000, completed_ms=60000)
            pending, next_raw = accepted.request('b' * 64, now_ms=60000)
            busy = pending.receive(envelope(fixture_message(next_raw, facts(60000, 120000, quiet=False))),
                                   peer=PEER, now_ms=120000, completed_ms=120000)
        self.assertFalse(accepted.session.terminal)
        self.assertIsNone(accepted.stop_receipt)
        self.assertEqual(busy.broker._current().state, B.State.STOP_REQUESTED)
        self.assertEqual(busy.session.model_observations, 1)
        self.assertFalse(busy.diagnostic()['execution_authorized'])

    def test_timeout_transport_loss_wrong_peer_and_h4_injection_stop(self):
        pending, raw = chain().request('a' * 64, now_ms=0)
        failures = (pending.tick(now_ms=105001), pending.transport_lost(),
                    pending.receive(envelope(fixture_message(raw)), peer=None,
                                    now_ms=60000, completed_ms=60000),
                    pending.receive(b'{"operation":"start"}', peer=PEER,
                                    now_ms=0, completed_ms=0))
        for failed in failures:
            self.assertEqual(failed.broker._current().state, B.State.STOP_REQUESTED)
            self.assertFalse(failed.stop_receipt.cleanup_confirmed)

    def test_stop_while_armed_suppresses_fixture_start(self):
        failed = chain('armed').transport_lost()
        self.assertTrue(failed.broker._current().start_suppressed)
        after = failed._fixture_event('begin_start', generation=failed.broker.current_id)
        self.assertEqual(after.broker._current().state, B.State.STOP_REQUESTED)
        self.assertFalse(after.broker._current().dispatch_issued)

    def test_inflight_start_completion_after_failure_never_running(self):
        failed = chain('starting').transport_lost()
        self.assertTrue(failed.broker._current().start_pending)
        after = failed._fixture_event('start_completed', generation=failed.broker.current_id)
        self.assertEqual(after.broker._current().state, B.State.CLEANUP_PENDING)
        self.assertFalse(after.stop_receipt.cleanup_confirmed)

    def test_cleanup_requires_all_predicates_and_late_ack_updates_model_only(self):
        failed = chain().transport_lost()
        cleanup = failed._fixture_event('begin_cleanup', generation=failed.broker.current_id)
        incomplete = cleanup._fixture_event('cleanup_proof', generation=failed.broker.current_id,
                                           proof=replace(FULL, acknowledged=False))
        self.assertEqual(incomplete.broker._current().state, B.State.CLEANUP_PENDING)
        self.assertFalse(incomplete.stop_receipt.cleanup_confirmed)
        stopped = incomplete._fixture_event('cleanup_proof', generation=failed.broker.current_id, proof=FULL)
        self.assertEqual(stopped.broker._current().state, B.State.STOPPED)
        self.assertTrue(stopped.stop_receipt.cleanup_confirmed)  # SYNTHETIC MODEL ONLY
        self.assertFalse(stopped.diagnostic()['actual_os_effects'])
        self.assertTrue(stopped.session.terminal)

    def test_monitor_or_broker_restart_cannot_resume_session(self):
        for event in ('restart', 'monitor_restart', 'recovery_failure'):
            failed = chain()._fixture_event(event)
            self.assertTrue(failed.session.terminal)
            self.assertTrue(failed.broker.epoch_unknown)
            self.assertFalse(failed.stop_receipt.cleanup_confirmed)
            self.assertIsNone(failed.request('a' * 64, now_ms=0)[1])

    def test_old_session_stop_never_affects_replacement_generation(self):
        failed = chain().transport_lost()
        cleanup = failed._fixture_event('begin_cleanup', generation=failed.broker.current_id)
        stopped = cleanup._fixture_event('cleanup_proof', generation=failed.broker.current_id, proof=FULL)
        new_broker = B._fixture_prepare(stopped.broker)
        for kind in ('begin_start', 'dispatch_start', 'start_completed'):
            new_broker = B._fixture_event(new_broker, kind, generation=new_broker.current_id)
        stale = replace(stopped, broker=new_broker).transport_lost()
        self.assertEqual(stale.stop_receipt.code, 'STALE_GENERATION')
        self.assertIs(stale.broker, new_broker)
        self.assertEqual(stale.broker._current().state, B.State.RUNNING)

    def test_repeated_failure_is_idempotent_without_binding_growth(self):
        first = chain().transport_lost()
        again = first.transport_lost().tick(now_ms=0)
        self.assertEqual(again.broker, first.broker)
        self.assertTrue(again.stop_receipt.duplicate)
        self.assertEqual(len(again.broker.bindings), 0)  # internal safety path allocates no client ID
        self.assertEqual(again.session.reason, 'TRANSPORT_LOST')

    def test_exactly_once_model_fence_retained_when_budget_exhausts(self):
        original = chain()
        exhausted = replace(original, broker=replace(original.broker, event_count=B.MAX_EVENTS))
        failed = exhausted.transport_lost()
        self.assertTrue(failed.broker.epoch_unknown)
        self.assertTrue(failed.broker.budget_exhausted)
        self.assertFalse(failed.stop_receipt.cleanup_confirmed)
        self.assertTrue(failed.session.terminal)

    def test_no_fixture_start_or_foreign_pid_unit_in_client_data(self):
        pending, _ = chain().request('a' * 64, now_ms=0)
        failed = pending.receive(O.canonical({'kind': 'start', 'pid': 1, 'unit': 'foreign'}),
                                 peer=PEER, now_ms=0, completed_ms=0)
        self.assertEqual(failed.session.reason, 'BAD_MESSAGE')
        self.assertEqual(failed.broker.current_id, pending.broker.current_id)
        self.assertEqual(failed.broker._current().state, B.State.STOP_REQUESTED)

    def test_no_unscoped_factory_and_all_chain_exports_blocked(self):
        with self.assertRaises(ValueError):
            C._fixture_chain(session(), broker())
        for value in (chain(), chain().transport_lost()):
            row = value.diagnostic()
            self.assertEqual(row['formal_admission'], 'BLOCKED')
            for key in ('actual_os_effects', 'actual_peer_authenticated', 'route_accepted',
                        'deployment_authorized', 'execution_authorized',
                        'qualification_authorized', 'target_execution_authorized'):
                self.assertIs(row[key], False)


if __name__ == '__main__':
    unittest.main()
