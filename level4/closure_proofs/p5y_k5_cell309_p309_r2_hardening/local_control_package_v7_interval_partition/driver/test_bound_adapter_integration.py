"""One new integration case with synthetic files; no real trace or host query."""
import csv
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

import run_verified_partition as driver

PACKAGE = Path(__file__).absolute().parent.parent


@unittest.skipUnless(sys.platform == 'win32', 'Windows own-file share locks required')
class BoundAdapterIntegration(unittest.TestCase):
    def test_real_adapter_core_and_driver_share_two_verified_passes(self):
        with tempfile.TemporaryDirectory(dir=PACKAGE / 'driver', prefix='synthetic-integration-') as tmp:
            root = Path(tmp)
            off = root / 'offline'
            off.mkdir()
            audit = root / 'adapter.py'
            account = root / 'account.py'
            core = root / 'core.py'
            for source, target in ((PACKAGE / 'adapter/saved_interval_adapter.py', audit),
                                   (PACKAGE / 'reference/account_saved_qpc.py', account),
                                   (PACKAGE / 'core/interval_partition.py', core)):
                shutil.copyfile(source, target)
            csv_path = off / 'qpc-prefix.csv'
            rows = [(4, 0, 0, 1, 101, 1, 0, 1), (3, 2, 0, 1, 1, 10, 0, 1),
                    (1, 5, 0, 36, 10, 0, 0, 1), (4, 10, 0, 3, 101, 1, 0, 1),
                    (3, 12, 0, 3, 1, 10, 0, 1), (1, 90, 0, 36, 0, 10, 0, 1),
                    (3, 100, 0, 4, 1, 10, 0, 1), (4, 110, 0, 4, 101, 1, 0, 1)]
            with csv_path.open('w', encoding='ascii', newline='') as out:
                writer = csv.writer(out)
                writer.writerow(driver.SCHEMA)
                writer.writerows(rows)
            qpc = off / 'qpc.stdout.json'
            csw = off / 'CSWITCH_RAW_RESULT.json'
            qpc.write_text(json.dumps(dict(decoded=8, events=8, unknown_required_prefix=0,
                                          header_events_lost=0, header_buffers_lost=0, process_rc=0,
                                          close_rc=0, output_error=0, clock_type=1, qpc_frequency=1,
                                          processors=1, cpu_number_events=0, max_cpu=0,
                                          first_qpc=0, last_qpc=110)), encoding='utf-8')
            csw.write_text(json.dumps(dict(decoded_cswitch=2, events=8, unknown_cswitch=0,
                                          header_events_lost=0, process_trace_rc=0, close_trace_rc=0,
                                          output_error=0, processors=1)), encoding='utf-8')
            binding = dict(schema=2, binding_scope=driver.BINDING_SCOPE,
                           csv_sha256=driver.sha256(csv_path), csv_bytes=csv_path.stat().st_size,
                           qpc_summary_sha256=driver.sha256(qpc), cswitch_summary_sha256=driver.sha256(csw),
                           decoded_rows=8, cswitch_rows=2, audit_source_sha256=driver.sha256(audit),
                           account_source_sha256=driver.sha256(account), core_source_sha256=driver.sha256(core),
                           wrapper_source_sha256=driver.sha256(Path(driver.__file__)))
            manifest = root / 'binding.json'
            manifest.write_text(json.dumps(binding), encoding='utf-8')
            result = driver.run_verified(root, manifest, driver.sha256(manifest), audit, account, core)
            actual = result['audit_result']
            self.assertEqual(actual['ticks_by_class'], {'known_other': 60})
            self.assertEqual(actual['original_span_geometry'], dict(touching_original_ticks=85,
                                                                  inside_window_ticks=60,
                                                                  outside_window_ticks=25))
            self.assertEqual(tuple(actual['historical_comparison_ticks'].get(key, 0) for key in
                                   ('old_known_new_known', 'old_known_new_unknown',
                                    'old_unknown_new_known', 'old_unknown_new_unknown')), (60, 0, 0, 0))
            self.assertEqual(actual['window_qpc'], [12, 72])
            self.assertEqual(actual['backwards'], 0)
            self.assertTrue(actual['every_cpu_has_closed_60s_span'])
            self.assertEqual(len(result['audit_pass_receipts']), 2)
            self.assertTrue(all(row == dict(sha256=binding['csv_sha256'], rows=8, cswitch_rows=2)
                                for row in result['audit_pass_receipts']))
            self.assertIsNone(result['private_decisions_sha256'])
            self.assertFalse(actual['coverage_complete'])
            self.assertEqual(result['admission'], 'BLOCKED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
