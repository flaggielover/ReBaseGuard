"""New binding regressions only. Files are synthetic; no host inventory/capture."""
import csv
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

import run_verified_partition as v

HERE = Path(__file__).absolute().parent
AUDIT = '''from interval_partition import marker
from account_saved_qpc import marker as account_marker
def audit(root, private_decisions=None):
    assert marker == "verified-core" and account_marker == "verified-account"
    for unused in range(2):
        assert len(list(rows(root / "offline" / "qpc-prefix.csv"))) == 2
        assert read(root / "offline" / "qpc.stdout.json")["decoded"] == 2
    return dict(I1_I7="OPEN", admission="BLOCKED", coverage_complete=False)
'''


@unittest.skipUnless(sys.platform == 'win32', 'Windows own-file sharing required')
class PartitionBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=HERE, prefix='synthetic-binding-')
        self.root = Path(self.temp.name)
        off = self.root / 'offline'
        off.mkdir()
        self.csv, self.qpc, self.csw = (off / n for n in ('qpc-prefix.csv', 'qpc.stdout.json', 'CSWITCH_RAW_RESULT.json'))
        self.account, self.core, self.audit = (self.root / n for n in ('account.py', 'core.py', 'audit.py'))
        self.manifest = self.root / 'binding.json'
        self.account.write_text('marker = "verified-account"\n', encoding='utf-8')
        self.core.write_text('marker = "verified-core"\n', encoding='utf-8')
        self.audit.write_text(AUDIT, encoding='utf-8')
        with self.csv.open('w', encoding='ascii', newline='') as out:
            writer = csv.writer(out)
            writer.writerow(v.SCHEMA)
            writer.writerows(((1, 0, 0, 36, 10, 0, 0, 1), (1, 60, 0, 36, 0, 10, 0, 1)))
        self.qpc.write_text(json.dumps(dict(decoded=2, events=2, unknown_required_prefix=0,
                                           header_events_lost=0, header_buffers_lost=0,
                                           process_rc=0, close_rc=0, output_error=0, processors=1)), encoding='utf-8')
        self.csw.write_text(json.dumps(dict(decoded_cswitch=2, events=2, unknown_cswitch=0,
                                           header_events_lost=0, process_trace_rc=0,
                                           close_trace_rc=0, output_error=0, processors=1)), encoding='utf-8')
        self.bind()

    def tearDown(self):
        self.temp.cleanup()

    def bind(self):
        self.m = dict(schema=2, binding_scope=v.BINDING_SCOPE, csv_sha256=v.sha256(self.csv),
                      csv_bytes=self.csv.stat().st_size, qpc_summary_sha256=v.sha256(self.qpc),
                      cswitch_summary_sha256=v.sha256(self.csw), decoded_rows=2, cswitch_rows=2,
                      audit_source_sha256=v.sha256(self.audit), account_source_sha256=v.sha256(self.account),
                      core_source_sha256=v.sha256(self.core), wrapper_source_sha256=v.sha256(Path(v.__file__)))
        self.manifest.write_text(json.dumps(self.m), encoding='utf-8')

    def run_bound(self):
        return v.run_verified(self.root, self.manifest, v.sha256(self.manifest), self.audit, self.account, self.core)

    def test_exact_core_and_account_snapshots_ignore_and_restore_poisoned_modules(self):
        previous = {name: sys.modules.get(name) for name in ('interval_partition', 'account_saved_qpc')}
        poisons = {name: types.ModuleType(name) for name in previous}
        try:
            for name, module in poisons.items():
                module.marker = 'untrusted-import-path'
                sys.modules[name] = module
            result = self.run_bound()
            self.assertEqual(result['numeric_rows'], 2)
            self.assertEqual(len(result['audit_pass_receipts']), 2)
            self.assertTrue(result['all_audit_passes_read_same_verified_file_handle'])
            for name, module in poisons.items():
                self.assertIs(sys.modules[name], module)
            self.assertEqual(result['python_role'], 'OFFLINE_ANALYSIS_TOOL_NOT_TARGET_RUNTIME')
        finally:
            for name, module in previous.items():
                if module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = module

    def test_any_new_core_account_or_adapter_tamper_refused_before_execution(self):
        for path in (self.core, self.account, self.audit):
            original = path.read_bytes()
            with self.subTest(path=path.name):
                path.write_bytes(original + b'\nraise AssertionError("tampered code executed")\n')
                with self.assertRaisesRegex(ValueError, 'SHA-256 differs'):
                    self.run_bound()
            path.write_bytes(original)

    def test_one_consumed_pass_cannot_be_reported_as_two(self):
        self.audit.write_text(AUDIT.replace('range(2)', 'range(1)'), encoding='utf-8')
        self.bind()
        with self.assertRaisesRegex(ValueError, 'exactly two'):
            self.run_bound()

    def test_core_or_audit_cannot_turn_integrity_result_into_admission(self):
        self.audit.write_text(AUDIT.replace('coverage_complete=False', 'coverage_complete=True'), encoding='utf-8')
        self.bind()
        with self.assertRaisesRegex(ValueError, 'OPEN/BLOCKED/incomplete'):
            self.run_bound()

    def test_private_decisions_must_be_new_and_distinct(self):
        with self.assertRaisesRegex(ValueError, 'new distinct output'):
            v.run_verified(self.root, self.manifest, v.sha256(self.manifest), self.audit, self.account, self.core, self.csv)


if __name__ == '__main__':
    unittest.main(verbosity=2)
