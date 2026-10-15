"""Local OpenSSL signatures -> monitor -> real fixed Linux fixture termination."""
import base64
from pathlib import Path
import subprocess
import tempfile
import unittest

from owned_stop_scenarios import StopScenarios


class LocalStopChain(StopScenarios, unittest.TestCase):
    signer_kind = 'ephemeral_local_openssl_test_key'

    @classmethod
    def setUpClass(cls):
        cls.keys = tempfile.TemporaryDirectory(prefix='p309-owned-stop-test-keys-')
        cls.private = Path(cls.keys.name) / 'private.pem'
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'RSA', '-pkeyopt',
                        'rsa_keygen_bits:2048', '-out', str(cls.private)], capture_output=True, check=True)
        cls.private.chmod(0o600)
        cls.public = subprocess.check_output(['openssl', 'pkey', '-in', str(cls.private), '-pubout'])

    @classmethod
    def tearDownClass(cls):
        cls.keys.cleanup()

    def sign(self, message):
        signature = subprocess.run(['openssl', 'dgst', '-sha256', '-sign', str(self.private)],
                                   input=message, capture_output=True, check=True).stdout
        return dict(message_b64=base64.b64encode(message).decode(),
                    signature_b64=base64.b64encode(signature).decode())


if __name__ == '__main__':
    unittest.main()
