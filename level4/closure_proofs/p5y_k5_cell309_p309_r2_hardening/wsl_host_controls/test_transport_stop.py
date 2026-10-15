"""Cloud/Linux link cases with ephemeral OpenSSL test keys and transport doubles."""
import base64
from pathlib import Path
import subprocess
import tempfile
import unittest

from synthetic_transport_link import SyntheticObservationLink
from transport_stop_scenarios import TransportStopScenarios


class LocalSigner:
    def __init__(self, private, public):
        self.private, self.public = private, public
        self.broken = False

    def sign(self, raw):
        if self.broken:
            self.close()  # Models existing bridge cleanup before raising.
            raise EOFError('synthetic transport double EOF')
        signature = subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(self.private)],
                                   input=raw, capture_output=True, check=True).stdout
        return dict(message_b64=base64.b64encode(raw).decode(),
                    signature_b64=base64.b64encode(signature).decode())

    def close(self):
        pass


class LocalTransportStop(TransportStopScenarios, unittest.TestCase):
    signer_kind = 'local_openssl_and_explicit_transport_double'

    @classmethod
    def setUpClass(cls):
        cls.keys = tempfile.TemporaryDirectory(prefix='p309-transport-stop-test-keys-')
        cls.private = Path(cls.keys.name) / 'private.pem'
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt',
                        'rsa_keygen_bits:2048', '-out', str(cls.private)], capture_output=True, check=True)
        cls.private.chmod(0o600)
        cls.public_key = subprocess.check_output(['openssl', 'pkey', '-in', str(cls.private), '-pubout'])

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def make_signer(self):
        return LocalSigner(self.private, self.public_key)

    def break_transport(self):
        self.signer.broken = True


class LinkArguments(unittest.TestCase):
    def test_invalid_scope_or_timeout_is_refused_before_monitor_or_signer_use(self):
        for options in ({}, {'synthetic_only': 1}, {'synthetic_only': True, 'response_timeout': True},
                        {'synthetic_only': True, 'response_timeout': float('nan')},
                        {'synthetic_only': True, 'response_timeout': .01},
                        {'synthetic_only': True, 'response_timeout': 6}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                SyntheticObservationLink(None, None, **options)


if __name__ == '__main__':
    unittest.main()
