import dataclasses
import json
import unittest

import d2_control_wire as W


def message(*, request_id='1' * 32, operation='status', generation=None, **extra):
    return json.dumps(dict(protocol=W.PROTOCOL, request_id=request_id,
                          operation=operation, generation=generation, **extra),
                      sort_keys=True, separators=(',', ':')).encode()


class ControlWire(unittest.TestCase):
    def test_current_status_and_generation_stop(self):
        self.assertIsNone(W.parse_request(message()).generation)
        parsed = W.parse_request(message(operation='stop', generation='a' * 32))
        self.assertEqual((parsed.operation, parsed.generation), ('stop', 'a' * 32))

    def test_exact_fields_reject_commands_and_claimed_facts(self):
        for key in ('command', 'pid', 'unit', 'uid', 'properties', 'environment',
                    'cpu_fraction', 'coverage', 'cleanup_proof', 'peer'):
            with self.subTest(key=key), self.assertRaises(W.WireError):
                W.parse_request(message(**{key: 'invented'}))

    def test_missing_fields_refused(self):
        for key in W.FIELDS:
            obj = json.loads(message())
            del obj[key]
            with self.subTest(key=key), self.assertRaises(W.WireError):
                W.parse_request(json.dumps(obj).encode())

    def test_protocol_is_fixed(self):
        for value in (None, True, 2, {}, 'P309_DEV_BROKER_CONTROL/1'):
            obj = json.loads(message())
            obj['protocol'] = value
            with self.subTest(value=value), self.assertRaises(W.WireError):
                W.parse_request(json.dumps(obj).encode())

    def test_no_start_arm_rearm_reset_or_generic_manager(self):
        for operation in ('start', 'arm', 'rearm', 'reset', 'StartTransientUnit', '', True, 1, {}):
            with self.subTest(operation=operation), self.assertRaises(W.WireError):
                W.parse_request(message(operation=operation))

    def test_request_id_is_exact_lowercase_hex(self):
        for value in (None, True, 1, 1.0, [], {}, 'a' * 31, 'a' * 33,
                      'A' * 32, 'g' * 32, '零' * 32, '0x' + 'a' * 30):
            with self.subTest(value=value), self.assertRaises(W.WireError):
                W.parse_request(message(request_id=value))

    def test_generation_is_exact_or_null_and_stop_needs_generation(self):
        with self.assertRaises(W.WireError):
            W.parse_request(message(operation='stop'))
        for value in (True, 1, [], {}, 'A' * 32, 'b' * 31, 'b' * 33):
            with self.subTest(value=value), self.assertRaises(W.WireError):
                W.parse_request(message(generation=value))

    def test_duplicate_fields_at_any_depth_refused(self):
        raw = message()
        for duplicate in (b'"operation":"status",', b'"request_id":"' + b'1' * 32 + b'",',
                          b'"extra":{"x":1,"x":2},'):
            with self.subTest(duplicate=duplicate), self.assertRaises(W.WireError):
                W.parse_request(b'{' + duplicate + raw[1:])

    def test_nonfinite_numbers_refused(self):
        for value in (b'NaN', b'Infinity', b'-Infinity'):
            with self.subTest(value=value), self.assertRaises(W.WireError):
                W.parse_request(message().replace(b'null', value))

    def test_strict_utf8_and_no_bom(self):
        for raw in (b'\xff', b'\xef\xbb\xbf' + message(), b'{', message() + b'garbage'):
            with self.subTest(raw=raw), self.assertRaises(W.WireError):
                W.parse_request(raw)

    def test_raw_byte_budget_and_exact_type(self):
        raw = message()
        self.assertEqual(W.parse_request(raw + b' ' * (W.MAX_REQUEST_BYTES - len(raw))).operation, 'status')
        for raw in (b'', raw + b' ' * W.MAX_REQUEST_BYTES, raw.decode(), bytearray(raw), memoryview(raw), {}):
            with self.subTest(type=type(raw).__name__), self.assertRaises(W.WireError):
                W.parse_request(raw)

    def test_nonobject_and_deep_json_refused(self):
        for raw in (b'[]', b'null', b'true', b'"object"', b'[' * 1500 + b'0' + b']' * 1500):
            with self.subTest(length=len(raw)), self.assertRaises(W.WireError):
                W.parse_request(raw)

    def test_fingerprint_binds_semantics_with_canonical_order(self):
        raw = message()
        alternate = json.dumps(json.loads(raw), indent=2).encode()
        self.assertEqual(W.parse_request(raw).fingerprint(), W.parse_request(alternate).fingerprint())
        self.assertNotEqual(W.parse_request(raw).fingerprint(),
                            W.parse_request(message(generation='a' * 32)).fingerprint())

    def test_request_is_immutable(self):
        request = W.parse_request(message())
        with self.assertRaises(dataclasses.FrozenInstanceError):
            request.operation = 'start'


if __name__ == '__main__':
    unittest.main()
