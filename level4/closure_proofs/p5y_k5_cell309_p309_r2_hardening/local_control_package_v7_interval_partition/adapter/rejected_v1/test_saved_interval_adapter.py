"""New adapter regressions only. Verified source imports, no actual CSV reads."""
import ast
import hashlib
import json
import tempfile
from pathlib import Path
import sys
import types
import unittest


INPUTS = {
    "interval_partition": (r"C:\Users\Lenovo\Documents\Codex\2026-10-15\rebaseguard-309-windows-cpu-wsl2-ubuntu\outputs\p309-interval-partition-v7-staging\interval_partition.py",
                           "39edb2bde848ab711f68775c7b2c3af18e9dbbc52ffe08fadb1fa9f269a781fa"),
    "account_saved_qpc": (r"D:\ReBaseGuard-309\workspace\p309-local-vm-diagnostic-dev-20261016\level4\closure_proofs\p5y_k5_cell309_p309_r2_hardening\local_control_package_v4_offline\account_saved_qpc.py",
                          "d49f9ed2e49bd7aa0674f59a10a03380e46c5fb1b52839d0e5a60c157b6cd1fd"),
}
for name, (path, expected) in INPUTS.items():
    raw = Path(path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError("source input differs: "+name)
    module = types.ModuleType(name)
    module.__file__ = path
    sys.modules[name] = module
    exec(compile(raw, path, "exec"), module.__dict__)

import saved_interval_adapter as adapter


def index(events):
    return adapter.build_generations(events, 0, 100)


class AdapterTests(unittest.TestCase):
    def test_actual_rundown_anchors_not_synthetic_bounds(self):
        r = index([(3, 5, 7, 20, 0, 1), (4, 80, 7, 20, 0, 2)])
        self.assertEqual(r["generations"][7], [(0, 100, 20, True)])
        proof = r["evidence"][7][0]
        self.assertEqual((proof["start_anchor"], proof["end_anchor"]), (5, 80))
        self.assertEqual(proof["source_row_ordinals"], [1, 2])

    def test_dcstart_corroborates_real_start_without_widening(self):
        r = index([(1, 5, 7, 20, 0, 1), (3, 8, 7, 20, 0, 2), (2, 20, 7, 20, 0, 3)])
        self.assertEqual(r["generations"][7], [(5, 20, 20, False)])
        self.assertEqual(r["evidence"][7][0]["start_anchor"], 5)
        self.assertEqual(r["evidence"][7][0]["source_row_ordinals"], [1, 2, 3])

    def test_any_later_conflict_invalidates_whole_id(self):
        good = [(1, 1, 7, 20, 0, 1), (2, 5, 7, 20, 0, 2)]
        bad_tails = [
            [(2, 8, 7, 20, 0, 3)],
            [(1, 8, 7, 20, 0, 3), (1, 9, 7, 21, 0, 4)],
            [(1, 8, 7, 20, 0, 3), (2, 10, 7, 21, 0, 4)],
            [(1, 8, 7, 20, 0, 3)],
            [(1, 8, 7, 20, 0, 3), (3, 9, 7, 20, 0, 4), (3, 10, 7, 20, 0, 5)],
        ]
        for tail in bad_tails:
            with self.subTest(tail=tail):
                r = index(good+tail)
                self.assertNotIn(7, r["generations"])
                self.assertEqual(len(r["unresolved"][7]["events"]), len(good+tail))

    def test_same_qpc_duplicates_and_adjacent_reuse_unresolved(self):
        for events in ([(1, 5, 7, 20, 0, 1), (1, 5, 7, 20, 0, 2)],
                       [(1, 1, 7, 20, 0, 1), (2, 5, 7, 20, 0, 2), (1, 5, 7, 21, 0, 3)]):
            r = index(events)
            self.assertEqual(r["unresolved"][7]["reason"], "SAME_QPC_LIFECYCLE_ORDER_UNPROVEN")

    def test_trace_bound_rundown_cannot_overlap_another_generation(self):
        r = index([(1, 1, 7, 20, 0, 1), (2, 5, 7, 20, 0, 2),
                   (3, 10, 7, 21, 0, 3), (4, 90, 7, 21, 0, 4)])
        self.assertNotIn(7, r["generations"])
        self.assertIn("OVERLAPPING", r["unresolved"][7]["reason"])

    def test_flags_retained_by_generation_not_pid_key_or(self):
        r = index([(1, 1, 20, 99, 0, 1), (2, 5, 20, 99, 0, 2),
                   (1, 10, 20, 99, 4, 3), (2, 20, 20, 99, 4, 4)])
        self.assertEqual([r["flags"][20][i]["value"] for i in (0, 1)], [0, 4])
        r = index([(1, 1, 20, 99, 0, 1), (2, 5, 20, 99, 4, 2)])
        self.assertFalse(r["flags"][20][0]["consistent"])
        self.assertIsNone(r["flags"][20][0]["value"])

    def test_cross_end_prefix_preserved_without_tail_rebinding(self):
        t = index([(1, 1, 7, 20, 0, 1), (2, 8, 7, 20, 0, 2),
                   (1, 12, 7, 21, 0, 3), (2, 30, 7, 21, 0, 4)])
        p = index([(1, 0, 20, 90, 0, 1), (2, 40, 20, 90, 0, 2),
                   (1, 0, 21, 91, 4, 3), (2, 40, 21, 91, 4, 4)])
        r = adapter.partition_switch_span(7, (2, 20), t, p, (0, 20))
        self.assertEqual((r["known_ticks"], r["unknown_ticks"]), (6, 12))
        self.assertEqual({s["identity"]["pid"] for s in r["slices"] if s["identity"]}, {20})

    def test_historical_comparator_cannot_supply_new_identity(self):
        t = index([(1, 1, 7, 20, 0, 1), (2, 8, 7, 20, 0, 2)])
        p = index([(1, 0, 20, 90, 0, 1), (2, 40, 20, 90, 0, 2)])
        r = adapter.partition_switch_span(7, (2, 20), t, p, (0, 20))
        old = adapter.historical_owner(7, 2, 20, {7: [(1,8,20,False)]}, {20: [(0,40,90,False)]})
        self.assertIsNone(old)
        self.assertEqual(adapter.compare_span(r, old), {"old_unknown_new_known":6, "old_unknown_new_unknown":12})
        self.assertEqual(r["bound_source_events"]["thread"]["events"], [list(e) for e in t["events_by_id"][7]])
        self.assertEqual(r["bound_source_events"]["process"]["metadata"]["source_row_ordinals"], [1,2])
        # Old whole clipped span can appear known while the original start cannot bind.
        r = adapter.partition_switch_span(7, (0, 20), t, p, (2, 5))
        old = adapter.historical_owner(7, 2, 5, {7: [(1,8,20,False)]}, {20: [(0,40,90,False)]})
        self.assertEqual(adapter.compare_span(r, old), {"old_known_new_known":0, "old_known_new_unknown":3})

    def test_historical_lifetimes_exact_ast_body(self):
        path = Path(INPUTS["account_saved_qpc"][0]).with_name("audit_root_coverage.py")
        raw = path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), "3799e88d1726ba2a4e625d8e08decb3765a5bc36527bf92d8329fe81a81fa189")
        source = ast.parse(raw)
        current = ast.parse(Path(adapter.__file__).read_bytes())
        old = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == "lifetimes")
        new = next(n for n in current.body if isinstance(n, ast.FunctionDef) and n.name == "historical_lifetimes")
        self.assertEqual([ast.dump(n) for n in old.body], [ast.dump(n) for n in new.body])
        old_audit = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == "audit")
        old_owner = next(n for n in old_audit.body if isinstance(n, ast.FunctionDef) and n.name == "owner")
        new_owner = next(n for n in current.body if isinstance(n, ast.FunctionDef) and n.name == "historical_owner")
        self.assertEqual([ast.dump(n) for n in old_owner.body], [ast.dump(n) for n in new_owner.body])

    def test_pid_reuse_cannot_reparent_and_clipping_does_not_hide_birth(self):
        t = index([(1, 1, 7, 20, 0, 1), (2, 30, 7, 20, 0, 2)])
        p = index([(1, 0, 20, 90, 0, 1), (2, 8, 20, 90, 0, 2),
                   (1, 12, 20, 91, 4, 3), (2, 40, 20, 91, 4, 4)])
        self.assertEqual(adapter.partition_switch_span(7, (2, 20), t, p, (13, 18))["known_ticks"], 0)

    def test_end_only_pid_zero_stays_unresolved(self):
        t = index([(4, 90, 7, 0, 0, 1)])
        r = adapter.partition_switch_span(7, (2, 20), t, index([]), (0, 20))
        self.assertEqual(r["unknown_ticks"], 18)
        self.assertIsNotNone(r["unresolved_thread"])

    def test_backwards_lifecycle_order_and_duplicate_source_row_fail_closed(self):
        r = index([(1, 5, 7, 20, 0, 1), (2, 4, 7, 20, 0, 2)])
        self.assertEqual(r["unresolved"][7]["reason"], "BACKWARDS_LIFECYCLE_EVENT_ORDER")
        with self.assertRaises(ValueError):
            index([(1, 1, 7, 20, 0, 1), (2, 5, 7, 20, 0, 1)])

    def test_two_pass_audit_uses_original_span_and_keeps_idle_unproven(self):
        header = dict(unknown_required_prefix=0, header_events_lost=0, header_buffers_lost=0,
                      process_rc=0, close_rc=0, output_error=0, clock_type=1, cpu_number_events=0,
                      qpc_frequency=1, processors=1, max_cpu=0, first_qpc=0, last_qpc=70, decoded=6)
        original_read, original_rows = adapter.read, adapter.rows
        try:
            for tid in (7, 0):
                sample = [(1, 0, 0, 36, tid, 0, 0, 1), (4, 1, 0, 3, 99, 20, 4, 1),
                          (3, 2, 0, 3, 20, 7, 0, 1), (3, 64, 0, 4, 20, 7, 0, 1),
                          (4, 64, 0, 4, 99, 20, 4, 1), (1, 65, 0, 36, 0, tid, 0, 1)]
                calls = []
                adapter.read = lambda path: dict(header)
                def fake_rows(path):
                    calls.append(str(path))
                    return iter(sample)
                adapter.rows = fake_rows
                with tempfile.TemporaryDirectory(prefix="adapter-synthetic-", dir=Path(__file__).parent) as directory:
                    output = Path(directory)/"decisions.jsonl"
                    r = adapter.audit(Path("synthetic-root-never-opened"), output)
                    records = [json.loads(line) for line in output.read_text().splitlines()]
                    self.assertEqual(len(records), 1)
                    self.assertEqual(records[0]["cswitch_source_rows"], [1,6])
                    if not tid:
                        self.assertEqual(records[0]["reason"],"TID_ZERO_IDLE_UNPROVEN")
                    preserved = output.read_bytes()
                    with self.assertRaises(FileExistsError):
                        adapter.audit(Path("synthetic-root-never-opened"), output)
                    self.assertEqual(output.read_bytes(), preserved)
                    calls.pop()  # Refused output gets only first pass; no successful retry.

                self.assertEqual(len(calls), 2)
                self.assertEqual(r["row_counts"], [6, 6])
                self.assertEqual(r["ticks_by_class"]["unknown_identity" if tid else "historical_idle_unproven"], 60)
                if tid:
                    self.assertEqual(r["original_span_geometry"], {"touching_original_ticks":65, "inside_window_ticks":60, "outside_window_ticks":5})
                    self.assertEqual(r["historical_comparison_ticks"], {"old_known_new_known":0, "old_known_new_unknown":60})
                    self.assertEqual(r["remaining_new_unknown_ticks"],60)
                self.assertFalse(r["coverage_complete"])
                self.assertFalse(r["tid_zero_idle_proven"])
        finally:
            adapter.read, adapter.rows = original_read, original_rows


if __name__ == "__main__":
    unittest.main()
