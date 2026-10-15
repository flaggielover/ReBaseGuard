"""Actual Windows CNG -> WSL monitor -> fixed synthetic Linux process tree."""
import json
import unittest

from owned_stop_scenarios import StopScenarios
from synthetic_windows_bridge import WindowsSyntheticSigner


class WindowsStopChain(StopScenarios, unittest.TestCase):
    signer_kind = 'ephemeral_real_windows_cng_test_key'

    @classmethod
    def setUpClass(cls):
        # Fail rather than skip when Windows interop is unavailable.
        cls.signer = WindowsSyntheticSigner()
        cls.public = cls.signer.public
        print('WINDOWS_SIGNER=' + json.dumps(cls.signer.metadata(), sort_keys=True), flush=True)

    @classmethod
    def tearDownClass(cls):
        cls.signer.close()

    def sign(self, message):
        return self.signer.sign(message)


if __name__ == '__main__':
    unittest.main()
