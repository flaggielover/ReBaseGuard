"""Small saved-file tests only; no ETL/native capture/host facts."""
import csv
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

import run_verified_audit as v

HERE = Path(__file__).absolute().parent


@unittest.skipUnless(sys.platform == "win32", "requires actual Windows file-share locks")
class VerifiedAuditTests(unittest.TestCase):
    def setUp(self):
        # This task confines all writes, including fixtures and Python cache,
        # to its explicit staging directory.
        self.temporary = tempfile.TemporaryDirectory(prefix="synthetic-", dir=HERE)
        self.root = Path(self.temporary.name)
        self.off = self.root / "offline"
        self.off.mkdir()
        self.csv = self.off / "qpc-prefix.csv"
        self.qpc = self.off / "qpc.stdout.json"
        self.csw = self.off / "CSWITCH_RAW_RESULT.json"
        self.audit = self.root / "audit_root_coverage.py"
        self.account = self.root / "account_saved_qpc.py"
        shutil.copyfile(HERE / "audit_root_coverage.snapshot.py", self.audit)
        shutil.copyfile(HERE / "account_saved_qpc.snapshot.py", self.account)
        rows = [(4, 0, 0, 3, 101, 1, 0, 1), (3, 0, 0, 3, 1, 10, 0, 1),
                (1, 0, 0, 36, 10, 0, 0, 1), (1, 60, 0, 36, 0, 10, 0, 1),
                (3, 100, 0, 4, 1, 10, 0, 1), (4, 100, 0, 4, 101, 1, 0, 1)]
        with self.csv.open("w", encoding="ascii", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(v.SCHEMA)
            writer.writerows(rows)
        self.h = dict(decoded=6, events=6, unknown_required_prefix=0, header_events_lost=0,
                      header_buffers_lost=0, process_rc=0, close_rc=0, output_error=0,
                      clock_type=1, qpc_frequency=1, cpu_number_events=0, max_cpu=0,
                      processors=1, first_qpc=0, last_qpc=100)
        self.c = dict(decoded_cswitch=2, events=6, unknown_cswitch=0,
                      header_events_lost=0, process_trace_rc=0, close_trace_rc=0,
                      output_error=0, processors=1)
        self.write_json(self.qpc, self.h)
        self.write_json(self.csw, self.c)
        self.manifest = self.root / "binding.json"
        self.bind()

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def write_json(path, obj):
        path.write_text(json.dumps(obj), encoding="utf-8")

    def bind(self):
        self.m = dict(schema=1, binding_scope=v.BINDING_SCOPE,
                      csv_sha256=v.sha256(self.csv), csv_bytes=self.csv.stat().st_size,
                      qpc_summary_sha256=v.sha256(self.qpc), cswitch_summary_sha256=v.sha256(self.csw),
                      decoded_rows=6, cswitch_rows=2, audit_source_sha256=v.sha256(self.audit),
                      account_source_sha256=v.sha256(self.account), wrapper_source_sha256=v.sha256(Path(v.__file__)))
        self.write_json(self.manifest, self.m)

    def run_bound(self):
        return v.run_verified(self.root, self.manifest, v.sha256(self.manifest), self.audit, self.account)

    def test_actual_historical_audit_small_saved_input(self):
        result = self.run_bound()
        self.assertEqual(result["numeric_rows"], 6)
        self.assertEqual(result["cswitch_rows"], 2)
        self.assertEqual(len(result["audit_pass_receipts"]), 2)
        self.assertTrue(all(receipt == dict(sha256=self.m["csv_sha256"], rows=6, cswitch_rows=2)
                            for receipt in result["audit_pass_receipts"]))
        self.assertTrue(result["all_audit_passes_read_same_verified_file_handle"])
        self.assertFalse(result["all_metadata_writes_prevented"])
        self.assertEqual(result["audit_result"]["scheduled_seconds_by_class"], {"other_identified": 60.0})
        self.assertTrue(result["audit_result"]["every_cpu_has_closed_60s_span"])
        self.assertFalse(result["retroactive_original_run_binding_claimed"])
        self.assertFalse(result["cpu_identity_dual_field_decoder_issue_resolved"])
        self.assertFalse(result["coverage_complete"])
        self.assertEqual(result["admission"], "BLOCKED")

    def test_changed_csv_rejected_even_with_equal_length_and_row_count(self):
        data = self.csv.read_bytes().replace(b"101", b"102")
        self.csv.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "SHA-256 differs"):
            self.run_bound()

    def test_explicit_manifest_digest_required(self):
        with self.assertRaisesRegex(ValueError, "manifest SHA-256 differs"):
            v.run_verified(self.root, self.manifest, "0" * 64, self.audit, self.account)

    def test_missing_row_rejected_despite_new_matching_digest(self):
        lines = self.csv.read_bytes().splitlines(keepends=True)
        self.csv.write_bytes(b"".join(lines[:-1]))
        self.bind()
        with self.assertRaisesRegex(ValueError, "numeric row count differs"):
            self.run_bound()

    def test_cswitch_rows_must_match_independent_summary(self):
        self.c["decoded_cswitch"] = 1
        self.write_json(self.csw, self.c)
        self.bind()
        self.m["cswitch_rows"] = 1
        self.write_json(self.manifest, self.m)
        with self.assertRaisesRegex(ValueError, "numeric CSwitch count differs"):
            self.run_bound()

    def test_decoder_failure_rejected_even_with_bound_summary(self):
        self.h["header_events_lost"] = 1
        self.write_json(self.qpc, self.h)
        self.bind()
        with self.assertRaisesRegex(ValueError, "status/loss not zero"):
            self.run_bound()

    def test_malformed_csv_rejected_after_rebinding(self):
        self.csv.write_bytes(self.csv.read_bytes().replace(b"101", b"bad"))
        self.bind()
        with self.assertRaisesRegex(ValueError, "malformed numeric"):
            self.run_bound()

    def test_duplicate_json_keys_rejected(self):
        self.manifest.write_text(self.manifest.read_text()[:-1] + ',"schema":1}', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            self.run_bound()

    def test_source_tampering_rejected(self):
        self.audit.write_bytes(self.audit.read_bytes() + b"\n# changed\n")
        with self.assertRaisesRegex(ValueError, "SHA-256 differs"):
            self.run_bound()

    def test_existing_writer_refuses_pin(self):
        with self.csv.open("rb+"):
            with self.assertRaises(OSError):
                with v.PinnedInputs([self.csv]):
                    self.fail("a pre-existing write handle must prevent the pin")

    def test_leaf_write_and_ancestor_rename_denied_during_both_passes(self):
        observations = []

        def probe(root):
            for _ in range(2):
                self.assertEqual(len(list(probe.__globals__["rows"](self.csv))), 6)
                self.assertEqual(probe.__globals__["read"](self.qpc), self.h)
                with self.assertRaises(OSError):
                    with self.csv.open("wb"):
                        self.fail("write should be rejected while pinned")
                with self.assertRaises(OSError):
                    os.replace(self.off, self.root / "renamed-offline")
                observations.append(True)
            return dict(admission="BLOCKED", coverage_complete=False)

        with mock.patch.object(v, "load_bound_audit", return_value=probe):
            self.assertEqual(self.run_bound()["admission"], "BLOCKED")
        self.assertEqual(observations, [True, True])
        # Pins are actually released; an owned fixture can be moved afterwards.
        moved = self.root / "renamed-offline"
        os.replace(self.off, moved)
        os.replace(moved, self.off)


if __name__ == "__main__":
    unittest.main(verbosity=2)
