"""Actual CNG signatures/helper exit plus explicit blocking fault injection."""
import json
import os
import unittest

from synthetic_windows_bridge import WindowsSyntheticSigner
from transport_stop_scenarios import TransportStopScenarios


class WindowsTransportStop(TransportStopScenarios, unittest.TestCase):
    signer_kind = 'actual_windows_cng_with_disclosed_blocking_fault_injection'

    def make_signer(self):
        signer = WindowsSyntheticSigner()
        print('WINDOWS_SIGNER=' + json.dumps(signer.metadata(), sort_keys=True), flush=True)
        return signer

    def break_transport(self):
        # An actual invalid request makes the owned synthetic helper exit. Keep
        # stdin open: the next normal bridge request encounters a broken pipe.
        os.write(self.signer.process.stdin.fileno(), b'{"synthetic":false,"message_b64":"YQ=="}\n')
        self.assertNotEqual(self.signer.process.wait(timeout=5), 0)
        print('WINDOWS_TRANSPORT_FAULT=owned_helper_exited_after_invalid_synthetic_request', flush=True)


if __name__ == '__main__':
    unittest.main()
