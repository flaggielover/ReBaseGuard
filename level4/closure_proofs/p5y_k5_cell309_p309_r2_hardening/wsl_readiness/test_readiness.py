"""Synthetic checks of the readiness report's evidence and resource boundaries."""
import copy
import unittest
from inspect_wsl import assess


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.linux = {'schema': 'P309_WSL_READONLY_FACTS/1', 'affinity_cpus': 32,
                      'system': 'Linux', 'kernel': '6.6.114.1-microsoft-standard-WSL2',
                      'available_memory_bytes': 14_000_000_000, 'guest_disk_free_bytes': 950_000_000_000,
                      'pid1': 'systemd', 'python': {'implementation': 'CPython', 'version': '3.11.15'}}
        self.windows = {'schema': 'P309_WINDOWS_READONLY_FACTS/1', 'available_memory_bytes': 16_000_000_000,
                        'backing_free_bytes': 137_000_000_000, 'backing_drive': 'D:',
                        'vhdx_registered_and_present': True, 'wsl_version': 2}

    def test_cloud_linux_cannot_be_mistaken_for_wsl2(self):
        self.linux['kernel'] = '6.18.44'
        self.assertEqual(assess(self.linux, self.windows)['resource_checks']['wsl2_guest_and_registration'], 'FAIL')

    def test_wsl1_registration_cannot_pass_from_kernel_name(self):
        self.windows['wsl_version'] = 1
        self.assertEqual(assess(self.linux, self.windows)['resource_checks']['wsl2_guest_and_registration'], 'FAIL')

    def test_guest_capacity_cannot_hide_full_backing_drive(self):
        self.windows['backing_free_bytes'] = 185_000_000
        result = assess(self.linux, self.windows)
        self.assertEqual(result['resource_checks']['guest_and_backing_storage_at_least_40GB'], 'FAIL')
        self.assertEqual(result['effective_free_storage_bytes'], 185_000_000)

    def test_missing_backing_registration_cannot_pass_from_guest_capacity(self):
        self.windows['vhdx_registered_and_present'] = False
        self.assertEqual(assess(self.linux, self.windows)['resource_checks'][
            'guest_and_backing_storage_at_least_40GB'], 'UNKNOWN')

    def test_windows_memory_pressure_limits_guest_memory_claim(self):
        self.windows['available_memory_bytes'] = 4_000_000_000
        self.assertEqual(assess(self.linux, self.windows)['resource_checks'][
            'available_ram_guest_and_host_at_least_8GB'], 'FAIL')

    def test_bad_numbers_and_absent_host_evidence_are_unknown(self):
        for bad in (True, '137000000000', float('nan'), float('inf'), -1, None):
            with self.subTest(value=bad):
                windows = dict(self.windows, backing_free_bytes=bad)
                self.assertEqual(assess(self.linux, windows)['resource_checks'][
                    'guest_and_backing_storage_at_least_40GB'], 'UNKNOWN')
        self.assertEqual(assess(self.linux, {})['resource_checks'][
            'available_ram_guest_and_host_at_least_8GB'], 'UNKNOWN')

    def test_unrelated_snapshot_schema_cannot_supply_resources(self):
        self.windows['schema'] = 'OTHER/1'
        result = assess(self.linux, self.windows)
        self.assertFalse(result['input_schemas_valid'])
        self.assertIsNone(result['effective_free_storage_bytes'])

    def test_current_python_fails_exact_pin(self):
        self.linux['python']['version'] = '3.12.3'
        self.assertEqual(assess(self.linux, self.windows)['resource_checks']['pinned_python_3_11_15'], 'FAIL')

    def test_all_resource_checks_never_authorize_official_work(self):
        before = copy.deepcopy((self.linux, self.windows))
        result = assess(self.linux, self.windows)
        self.assertTrue(all(v == 'PASS' for v in result['resource_checks'].values()))
        self.assertEqual(result['formal_admission'], 'BLOCKED')
        self.assertFalse(result['qualification_authorized'])
        self.assertFalse(result['target_execution_authorized'])
        self.assertEqual((self.linux, self.windows), before)


if __name__ == '__main__':
    unittest.main()
