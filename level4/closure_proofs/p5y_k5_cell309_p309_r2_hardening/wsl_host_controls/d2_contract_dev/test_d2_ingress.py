"""Synthetic bytes only: no key generation, signature helper, host or I/O."""
import base64
from dataclasses import FrozenInstanceError
import json
import unittest

import d2_ingress_model as M
import d2_ingress_wire as W


def encode(obj):
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()


def token(**changes):
    obj = dict(schema=W.CHALLENGE_SCHEMA, session_id='1' * 64,
               baseline_sha256='2' * 64, sequence=1, nonce='3' * 64,
               previous_sha256='4' * 64)
    obj.update(changes)
    return obj


def request(**changes):
    return encode(dict(protocol=W.PROTOCOL, kind='observer_request', challenge=token(**changes)))


def signed_message(**changes):
    return encode(dict(**token(**changes), payload={'opaque_fixture': '未验证\r\n'}))


def response(message=None, size=256):
    raw = signed_message() if message is None else message
    return encode(dict(protocol=W.PROTOCOL, kind='signed_observation',
                       envelope={'message_b64': base64.b64encode(raw).decode('ascii'),
                                 'signature_b64': base64.b64encode(b'x' * size).decode('ascii')}))


def failure(reason='EOF', **changes):
    obj = dict(protocol=W.PROTOCOL, kind='transport_failure', reason=reason)
    obj.update(changes)
    return encode(obj)


def opened(**changes):
    return M._fixture_open(request(**changes), generation='a' * 32,
                           relay_instance='synthetic-relay-1', synthetic_only=True)


def relay(instance='synthetic-relay-1', role='p309-relay'):
    return M.SyntheticRelay(role, instance)


class IngressWire(unittest.TestCase):
    def test_outbound_exact_challenge_shape(self):
        parsed = W.parse_observer_request(request())
        self.assertEqual(parsed, W.Challenge('1' * 64, '2' * 64, 1, '3' * 64, '4' * 64))

    def test_request_rejects_claimed_facts_identity_and_commands(self):
        for key in ('generation', 'operation', 'cpu', 'policy', 'uid', 'pid', 'unit',
                    'command', 'environment', 'safe', 'host_facts'):
            obj = json.loads(request()); obj[key] = 'injected'
            with self.subTest(key=key), self.assertRaises(W.IngressError):
                W.parse_observer_request(encode(obj))
        for key in W.TOKEN_FIELDS:
            obj = json.loads(request()); del obj['challenge'][key]
            with self.subTest(missing=key), self.assertRaises(W.IngressError):
                W.parse_observer_request(encode(obj))

    def test_challenge_tokens_and_sequence_are_exact(self):
        for key in ('session_id', 'baseline_sha256', 'nonce', 'previous_sha256'):
            for value in (None, True, 1, {}, [], 'a' * 63, 'A' * 64, '零' * 64):
                with self.subTest(key=key, value=value), self.assertRaises(W.IngressError):
                    W.parse_observer_request(request(**{key: value}))
        for value in (0, True, 1.0, '1', W.MAX_SEQUENCE + 1):
            with self.subTest(sequence=value), self.assertRaises(W.IngressError):
                W.parse_observer_request(request(sequence=value))
        self.assertEqual(W.parse_observer_request(request(sequence=W.MAX_SEQUENCE)).sequence,
                         W.MAX_SEQUENCE)
        with self.assertRaises(W.IngressError):
            W.parse_observer_request(request(schema='other'))

    def test_direction_and_protocol_do_not_cross_into_h4(self):
        for raw in (request(), encode({'protocol': 'P309_DEV_BROKER_CONTROL/2',
                                      'operation': 'stop', 'generation': 'a' * 32,
                                      'request_id': '1' * 32})):
            with self.subTest(raw=raw), self.assertRaises(W.IngressError):
                W.parse_relay_message(raw)
        for raw in (response(), failure()):
            with self.subTest(raw=raw), self.assertRaises(W.IngressError):
                W.parse_observer_request(raw)
        for value in ('other', True, None):
            obj = json.loads(response()); obj['protocol'] = value
            with self.subTest(protocol=value), self.assertRaises(W.IngressError):
                W.parse_relay_message(encode(obj))

    def test_original_unicode_crlf_whitespace_bytes_preserved(self):
        obj = json.loads(signed_message())
        raw = (' \r\n' + json.dumps(obj, ensure_ascii=False, indent=2) + '\t\r\n').encode()
        parsed = W.parse_relay_message(response(raw))
        self.assertEqual(parsed.message, raw)
        self.assertEqual(parsed.signature, b'x' * 256)
        self.assertIsInstance(parsed, W.UnverifiedObservation)

    def test_supported_signature_lengths_are_shapes_not_validation(self):
        for size in (256, 384, 512):
            self.assertEqual(len(W.parse_relay_message(response(size=size)).signature), size)
        for size in (0, 1, 255, 257, 383, 385, 511, 513):
            with self.subTest(size=size), self.assertRaises(W.IngressError):
                W.parse_relay_message(response(size=size))

    def test_envelope_and_inner_fields_are_exact(self):
        for location in ('frame', 'envelope', 'message'):
            obj = json.loads(response())
            if location == 'frame':
                obj['operation'] = 'stop'
            elif location == 'envelope':
                obj['envelope']['signature_verified'] = True
            else:
                inner = json.loads(signed_message()); inner['safe'] = True
                obj = json.loads(response(encode(inner)))
            with self.subTest(location=location), self.assertRaises(W.IngressError):
                W.parse_relay_message(encode(obj))
        for key in ('message_b64', 'signature_b64'):
            obj = json.loads(response()); del obj['envelope'][key]
            with self.subTest(missing=key), self.assertRaises(W.IngressError):
                W.parse_relay_message(encode(obj))

    def test_duplicate_fields_at_all_json_layers_refused(self):
        for duplicate in (b'"protocol":"x",', b'"envelope":{"x":1,"x":2},'):
            with self.subTest(duplicate=duplicate), self.assertRaises(W.IngressError):
                W.parse_relay_message(b'{' + duplicate + response()[1:])
        raw = signed_message().replace(b'"payload":', b'"payload":{"x":1,"x":2},"ignored":')
        with self.assertRaises(W.IngressError):
            W.parse_relay_message(response(raw))
        raw = request().replace(b'"sequence":1', b'"sequence":1,"sequence":1')
        with self.assertRaises(W.IngressError):
            W.parse_observer_request(raw)

    def test_nonfinite_numbers_in_opaque_payload_refused(self):
        for value in (b'NaN', b'Infinity', b'-Infinity', b'1e400', b'-1e400'):
            raw = signed_message().replace(b'"payload":{', b'"payload":{"n":' + value + b',')
            with self.subTest(value=value), self.assertRaises(W.IngressError):
                W.parse_relay_message(response(raw))

    def test_base64_strict_type_alphabet_padding_and_budget(self):
        obj = json.loads(response())
        for key in ('message_b64', 'signature_b64'):
            for value in (None, 1, [], '', 'AA=A', 'AAAA\n', '!!!!', '非ASCII',
                          obj['envelope'][key] + '='):
                invalid = json.loads(response()); invalid['envelope'][key] = value
                with self.subTest(key=key, value_type=type(value).__name__), self.assertRaises(W.IngressError):
                    W.parse_relay_message(encode(invalid))
        # Change unused pad bits: decoding still gives identical bytes in Python,
        # but the wire requires the unique canonical base64 representation.
        canonical = obj['envelope']['signature_b64']
        noncanonical = canonical[:-3] + 'B=='  # eA== and eB== decode to the same bytes.
        self.assertEqual(base64.b64decode(noncanonical), base64.b64decode(canonical))
        obj['envelope']['signature_b64'] = noncanonical
        with self.assertRaises(W.IngressError):
            W.parse_relay_message(encode(obj))

    def test_strict_utf8_root_types_bom_and_recursion(self):
        for raw in (b'\xff', b'\xef\xbb\xbf' + response(), b'[]', b'null', b'true',
                    b'"object"', b'{' , response() + b'junk',
                    b'[' * 1500 + b'0' + b']' * 1500):
            with self.subTest(length=len(raw)), self.assertRaises(W.IngressError):
                W.parse_relay_message(raw)
        with self.assertRaises(W.IngressError):
            W.parse_relay_message(response(b'\xff'))

    def test_message_and_frame_byte_boundaries(self):
        raw = signed_message()
        largest = raw + b' ' * (W.MAX_MESSAGE_BYTES - len(raw))
        self.assertEqual(len(W.parse_relay_message(response(largest)).message), W.MAX_MESSAGE_BYTES)
        with self.assertRaises(W.IngressError):
            W.parse_relay_message(response(largest + b' '))
        frame = response()
        self.assertEqual(W.parse_relay_message(frame + b' ' * (W.MAX_FRAME_BYTES - len(frame))).message, raw)
        with self.assertRaises(W.IngressError):
            W.parse_relay_message(frame + b' ' * (W.MAX_FRAME_BYTES - len(frame) + 1))
        outbound = request()
        W.parse_observer_request(outbound + b' ' * (W.MAX_REQUEST_BYTES - len(outbound)))
        with self.assertRaises(W.IngressError):
            W.parse_observer_request(outbound + b' ' * W.MAX_REQUEST_BYTES)

    def test_failure_notice_fixed_reason_and_no_asserted_generation(self):
        for reason in W.FAILURES:
            self.assertEqual(W.parse_relay_message(failure(reason)), W.TransportFailure(reason))
        for reason in ('RETRY', '', True, {}, 'detail' * 1000):
            with self.subTest(reason_type=type(reason).__name__), self.assertRaises(W.IngressError):
                W.parse_relay_message(failure(reason))
        with self.assertRaises(W.IngressError):
            W.parse_relay_message(failure(generation='b' * 32))

    def test_payload_is_opaque_untrusted_object(self):
        doc = json.loads(signed_message())
        for value in ([], None, True, 'safe'):
            doc['payload'] = value
            with self.subTest(value=value), self.assertRaises(W.IngressError):
                W.parse_relay_message(response(encode(doc)))
        doc['payload'] = {'safe': True, 'cpu': 0, 'uid': 0}
        parsed = W.parse_relay_message(response(encode(doc)))
        self.assertEqual(parsed.message, encode(doc))
        self.assertFalse(hasattr(parsed, 'safe'))
        self.assertFalse(hasattr(parsed, 'signature_verified'))

    def test_input_exact_bytes_and_returned_values_immutable(self):
        for raw in (b'', response().decode(), bytearray(response()), memoryview(response()), {}):
            with self.subTest(raw_type=type(raw).__name__), self.assertRaises(W.IngressError):
                W.parse_relay_message(raw)
        parsed = W.parse_relay_message(response())
        with self.assertRaises(FrozenInstanceError):
            parsed.message = b'changed'
        with self.assertRaises(FrozenInstanceError):
            parsed.challenge.nonce = '0' * 64


class IngressStaging(unittest.TestCase):
    def test_explicit_private_fixture_setup_only(self):
        for value in (False, 1, 'true', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                M._fixture_open(request(), generation='a' * 32, relay_instance='r', synthetic_only=value)
        for generation in (None, True, 'A' * 32, 'a' * 31):
            with self.subTest(generation=generation), self.assertRaises(ValueError):
                M._fixture_open(request(), generation=generation, relay_instance='r', synthetic_only=True)
        for instance in ('', 'r' * 129, '非ASCII', None, True):
            with self.subTest(instance=instance), self.assertRaises(ValueError):
                M._fixture_open(request(), generation='a' * 32, relay_instance=instance, synthetic_only=True)

    def test_matching_response_only_stages_unverified_bytes(self):
        before = opened()
        after = before.receive(response(), peer=relay())
        self.assertEqual(before.state, 'AWAITING_RESPONSE')
        self.assertIsNone(before.staged)
        self.assertEqual(after.state, 'UNVERIFIED')
        self.assertEqual(after.staged.message, signed_message())
        self.assertEqual(after.outstanding, before.outstanding)
        self.assertEqual(after.outstanding.sequence, 1)  # No sequence/checkpoint advancement.
        self.assertFalse(after.stop_latched)

    def test_every_challenge_component_mismatch_is_terminal(self):
        for key, value in (('session_id', '5' * 64), ('baseline_sha256', '6' * 64),
                           ('sequence', 2), ('nonce', '7' * 64), ('previous_sha256', '8' * 64)):
            before = opened()
            after = before.receive(response(signed_message(**{key: value})), peer=relay())
            with self.subTest(component=key):
                self.assertEqual(after.failure, 'CHALLENGE_MISMATCH')
                self.assertTrue(after.stop_latched)
                self.assertIsNone(after.staged)
                self.assertEqual(after.generation, before.generation)

    def test_wrong_synthetic_peer_cannot_stage_or_route_control(self):
        for candidate in (None, {}, relay(role='p309-monitor'), relay(role='p309-runner'),
                          relay(role='root'), relay(instance='other'), M.SyntheticRelay(True, 'r')):
            after = opened().receive(response(), peer=candidate)
            with self.subTest(candidate=candidate):
                self.assertEqual(after.failure, 'PEER_REFUSED')
                self.assertTrue(after.stop_latched)
                self.assertIsNone(after.staged)

    def test_malformed_message_and_h4_command_latch_associated_stop(self):
        for raw in (b'{', request(), encode({'operation': 'stop', 'generation': 'b' * 32})):
            after = opened().receive(raw, peer=relay())
            with self.subTest(raw=raw):
                self.assertEqual(after.failure, 'BAD_MESSAGE')
                self.assertEqual(after.generation, 'a' * 32)
                self.assertTrue(after.stop_latched)

    def test_transport_failure_only_latches_locally_bound_generation(self):
        for reason in W.FAILURES:
            after = opened().receive(failure(reason), peer=relay())
            self.assertEqual(after.failure, 'TRANSPORT_' + reason)
            self.assertEqual(after.generation, 'a' * 32)
            self.assertTrue(after.stop_latched)
        before = opened()
        after = before.transport_lost()
        self.assertEqual(after.failure, 'LOCAL_TRANSPORT_LOST')
        self.assertIs(after.transport_lost(), after)

    def test_duplicate_or_second_response_cannot_advance(self):
        staged = opened().receive(response(), peer=relay())
        for raw in (response(), response(signed_message(sequence=2))):
            after = staged.receive(raw, peer=relay())
            self.assertEqual(after.failure, 'UNEXPECTED_ADDITIONAL_RESPONSE')
            self.assertTrue(after.stop_latched)
            self.assertIsNone(after.staged)
            self.assertEqual(after.outstanding.sequence, 1)

    def test_terminal_state_does_not_reopen_or_replace_first_failure(self):
        terminal = opened().receive(failure(), peer=relay())
        for raw in (response(), request(), failure('TIMEOUT')):
            self.assertIs(terminal.receive(raw, peer=relay()), terminal)
        self.assertIs(terminal.transport_lost(), terminal)

    def test_loss_after_staging_discards_bytes_without_observation_acceptance(self):
        staged = opened().receive(response(), peer=relay())
        terminal = staged.transport_lost()
        self.assertEqual(terminal.state, 'TERMINAL_STOP')
        self.assertIsNone(terminal.staged)
        self.assertFalse(terminal.diagnostic()['observation_accepted'])

    def test_other_session_or_sequence_cannot_reuse_staged_message(self):
        raw = response()
        for before in (opened(session_id='9' * 64), opened(sequence=2)):
            after = before.receive(raw, peer=relay())
            self.assertEqual(after.failure, 'CHALLENGE_MISMATCH')
            self.assertTrue(after.stop_latched)

    def test_payload_safe_claims_and_dummy_signature_never_authorize(self):
        doc = json.loads(signed_message()); doc['payload'] = {'safe': True, 'formal_admission': 'PASS'}
        after = opened().receive(response(encode(doc)), peer=relay())
        self.assertEqual(after.state, 'UNVERIFIED')
        diagnostic = after.diagnostic()
        self.assertEqual(diagnostic['formal_admission'], 'BLOCKED')
        for key in ('signature_verified', 'host_facts_validated', 'observation_accepted',
                    'continuation_authorized', 'execution_authorized'):
            self.assertIs(diagnostic[key], False)

    def test_all_states_export_false_authority_and_no_raw_payload(self):
        initial = opened(); staged = initial.receive(response(), peer=relay())
        for model in (initial, staged, staged.transport_lost()):
            row = model.diagnostic()
            self.assertEqual(row['formal_admission'], 'BLOCKED')
            for key in ('actual_peer_authenticated', 'signature_verified', 'host_facts_validated',
                        'observation_accepted', 'continuation_authorized', 'actual_os_effects',
                        'route_accepted', 'deployment_authorized', 'execution_authorized',
                        'qualification_authorized', 'target_execution_authorized'):
                self.assertIs(row[key], False, key)
            self.assertNotIn('message', row)
            self.assertNotIn('payload', row)
            self.assertNotIn('signature', row)

    def test_snapshot_and_diagnostic_are_not_mutable_aliases(self):
        model = opened().receive(response(), peer=relay())
        with self.assertRaises(FrozenInstanceError):
            model.state = 'VERIFIED'
        row = model.diagnostic(); row['formal_admission'] = 'PASS'
        self.assertEqual(model.diagnostic()['formal_admission'], 'BLOCKED')


if __name__ == '__main__':
    unittest.main()
