"""Unit tests of the new-glibc successor production layer (portable; no certifier, no supervisor, no host state).

  python -B tests/test_gs_unit.py
The Linux lifecycle scenarios are in tests/gs_acceptance.py and run on the bound host.
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import gs_schema as GS                                                           # noqa: E402
import gs_composite as GC                                                        # noqa: E402
import gs_host as H                                                              # noqa: E402
import gs_settle as ST                                                           # noqa: E402
import gs_spec as SP                                                             # noqa: E402
import prod_ledger as L                                                          # noqa: E402
from prod_common import Refusal, canonical, sha256_bytes                          # noqa: E402

BINDING = json.loads(GS.BINDING.read_bytes())
HAVE_CP = GS.CHECKPOINT.exists()


# ---------------------------------------------------------------------- end-of-campaign settlement (pure evidence plan)
def _reap(kind, pid, cpu, *, sup, t, exit_code=0, boot="B"):
    r = {"schema": L.REAPER_SCHEMA, "kind": kind, "pid": pid, "boot_id": boot, "t_wall": t, "cpu_usec": cpu,
         "is_supervisor": sup, "exited": True if kind == "CHILD_REAPED" else None,
         "exit_code": exit_code if kind == "CHILD_REAPED" else None, "signal": None}
    return {**r, "record_id": sha256_bytes(canonical(r))}


def _terminal(**run):
    base = {"pid": 7, "boot_id": "B", "started_wall": 900.0, "ended_wall": 999.0, "end": "EXITED", "settled": False,
            "self_cpu_seen_usec": 50, "children_usec": 1000, "charged_usec": 1050, "last_charge_wall": 999.0, "settlement": None}
    return {"disposition": "COMPLETE", "overhead_charges": {}, "supervisor_runs": {"R2": {**base, **run}}}


def _good_reaper():
    return [_reap("CHILD_REAPED", 7, 1200, sup=True, t=1000.0), _reap("KEEPER_EXIT", 6, 30, sup=False, t=1000.1)]


class SettlementPlan(unittest.TestCase):
    def test_complete_unsettled_final_run(self):
        plan = ST.plan_settlement(_terminal(), _good_reaper(), 0)
        self.assertEqual(plan["runs"]["R2"]["extra_usec"], 150)
        self.assertEqual(plan["runs"]["R2"]["evidence"], "REAPER_RUSAGE")
        self.assertEqual([u for _r, u in plan["overhead"]], [30])

    def test_already_settled_plans_nothing(self):
        st = _terminal(settled=True)
        reaped = _good_reaper()
        st["overhead_charges"] = {reaped[1]["record_id"]: 30}
        self.assertEqual(ST.plan_settlement(st, reaped, 0), {"runs": {}, "overhead": []})

    def test_crash_between_transitions_plans_only_the_keeper_exit(self):
        plan = ST.plan_settlement(_terminal(settled=True), _good_reaper(), 0)
        self.assertEqual((plan["runs"], [u for _r, u in plan["overhead"]]), ({}, [30]))

    def test_fail_closed_evidence(self):
        good = _good_reaper()
        cases = {
            "unreadable_line": (_terminal(), good, 1, "REAPER_UNREADABLE"),
            "no_reap": (_terminal(), good[1:], 0, "SETTLEMENT_EVIDENCE_MISSING"),
            "no_keeper_exit": (_terminal(), good[:1], 0, "SETTLEMENT_EVIDENCE_MISSING"),
            "two_reaps": (_terminal(), good + [_reap("CHILD_REAPED", 7, 1300, sup=True, t=1000.5)], 0, "SETTLEMENT_EVIDENCE_AMBIGUOUS"),
            "reap_below_charged": (_terminal(), [_reap("CHILD_REAPED", 7, 1049, sup=True, t=1000.0)] + good[1:], 0,
                                   "SETTLEMENT_EVIDENCE_CONTRADICTORY"),
            "wrong_exit_code": (_terminal(), [_reap("CHILD_REAPED", 7, 1200, sup=True, t=1000.0, exit_code=20)] + good[1:], 0,
                                "SETTLEMENT_EVIDENCE_CONTRADICTORY"),
            "reaped_before_end": (_terminal(), [_reap("CHILD_REAPED", 7, 1200, sup=True, t=950.0)] + good[1:], 0,
                                  "SETTLEMENT_EVIDENCE_CONTRADICTORY"),
            "other_pid": (_terminal(pid=8), good, 0, "SETTLEMENT_EVIDENCE_MISSING"),
            "other_boot": (_terminal(boot_id="rebooted"), good, 0, "SETTLEMENT_EVIDENCE_MISSING"),
            "run_not_ended": (_terminal(end=None, ended_wall=None), good, 0, "SETTLEMENT_EVIDENCE_CONTRADICTORY"),
        }
        for name, (st, reaped, bad, want) in cases.items():
            with self.subTest(name):
                self.assertEqual(code(ST.plan_settlement, st, reaped, bad), want)

    def test_two_unsettled_runs_or_not_latest_refuse(self):
        st = _terminal()
        st["supervisor_runs"]["R3"] = {**st["supervisor_runs"]["R2"], "pid": 9, "started_wall": 1500.0, "ended_wall": 1600.0}
        self.assertEqual(code(ST.plan_settlement, st, _good_reaper(), 0), "SETTLEMENT_EVIDENCE_CONTRADICTORY")
        st["supervisor_runs"]["R3"]["settled"] = True
        self.assertEqual(code(ST.plan_settlement, st, _good_reaper(), 0), "SETTLEMENT_EVIDENCE_CONTRADICTORY")

    def test_disposition_exit_codes(self):
        for disposition, exit_code in (("HALTED", 20), ("INCOMPLETE_BUDGET_EXHAUSTED", 40)):
            with self.subTest(disposition):
                st = {**_terminal(), "disposition": disposition}
                reaped = [_reap("CHILD_REAPED", 7, 1200, sup=True, t=1000.0, exit_code=exit_code), _good_reaper()[1]]
                self.assertEqual(ST.plan_settlement(st, reaped, 0)["runs"]["R2"]["extra_usec"], 150)

    def test_target_refusals(self):
        from types import SimpleNamespace as NS_
        cases = {GS.PREDECESSOR_RUNTIME_ROOT: "REFUSED_ROOT", GS.BLOCKED_RUNTIME_ROOT / "x": "REFUSED_ROOT",
                 GS.AUX5_NS / "evidence/qualification_r1": "QUALIFICATION_ROOT",
                 GS.NS / "evidence/requalification_r1/qualification_r1": "QUALIFICATION_ROOT",
                 Path("/root/work/postk1-runs/glibc-successor-q6"): "QUALIFICATION_ROOT",
                 GS.NS / "config": "REPOSITORY_ROOT", GS.PREDECESSOR_CHECKOUT_PATH / "x": "REPOSITORY_ROOT"}
        for root, want in cases.items():
            with self.subTest(str(root)):
                self.assertEqual(code(ST.precheck_target, NS_(root=root, cell_indices=[128])), want)
        self.assertIsNone(code(ST.precheck_target, NS_(root=GS.SUCCESSOR_RUNTIME_ROOT, cell_indices=list(GS.NEW_CELLS))))
        self.assertEqual(code(ST.precheck_target, NS_(root=GS.SUCCESSOR_RUNTIME_ROOT, cell_indices=[127, 128])),
                         "RECOMPUTATION_OF_CARRYOVER_CELL")

    def test_entrypoint_exposes_settle_and_refuses_unreadable_input(self):
        import contextlib
        import io
        import gs_entry as E
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = E.main(["settle", "--synthetic-spec", "/nonexistent/cfg.json"])
        self.assertEqual((rc, "REFUSED [SETTLE_INPUT_UNREADABLE]" in out.getvalue()), (30, True))

    def test_no_settlement_bypass_in_successor_tests(self):
        banned = tuple("".join(x) for x in ((".set", "tle("), ("recon", "cile("), ("op_settle", "_run("),
                                            ("op_charge", "_overhead("), ("unmatched", "_overhead(")))
        hits = [f"{f.name}:{i}" for f in sorted((GS.NS / "tests").glob("*.py"))
                for i, line in enumerate(f.read_text().splitlines(), 1)
                if any(t in line.split("#", 1)[0] for t in banned) and "c13_helper" not in line]
        self.assertEqual(hits, [])


def code(fn, *a, **kw):
    try:
        fn(*a, **kw)
    except Refusal as r:
        return r.code
    return None


class Universe(unittest.TestCase):
    def test_partition_constants(self):
        self.assertEqual(set(GS.OLD_CELLS) & set(GS.NEW_CELLS), set())
        self.assertEqual(set(GS.OLD_CELLS) | set(GS.NEW_CELLS), set(range(326)))

    def test_check_universe(self):
        self.assertIsNone(code(SP.check_universe, GS.NEW_CELLS))
        self.assertIsNone(code(SP.check_universe, [128, 325]))
        for bad in ([0], [127, 128], list(range(326))):
            self.assertEqual(code(SP.check_universe, bad), "RECOMPUTATION_OF_CARRYOVER_CELL")
        self.assertEqual(code(SP.check_universe, [326]), "CELL_NOT_IN_UNIVERSE")
        self.assertEqual(code(SP.check_universe, [128, 128]), "CELL_NOT_IN_UNIVERSE")

    def test_frozen_lifecycle_refuses_old_cells(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = {"root": f"{d}/root", "config_path": f"{d}/cfg.json", "checkpoint_sha256": "SYNTHETIC-unit",
                   "cells": [128, 325], "cores": [0, 2], "cap_usec": 10 ** 12, "reservation_usec": 1000}
            spec = SP.synthetic_spec(cfg)
            self.assertEqual(code(SP.synthetic_spec, {**cfg, "cells": [127, 128]}), "RECOMPUTATION_OF_CARRYOVER_CELL")
            self.assertEqual(code(SP.synthetic_spec, {**cfg, "root": str(GS.SUCCESSOR_RUNTIME_ROOT / "x")}),
                             "SYNTHETIC_PRODUCTION_MIX")
            lock = L.CampaignLock(spec.root)
            lock.acquire({"tool": "unit"})
            try:
                led = L.Ledger(spec, lock)
                led.open(allow_genesis=True)
                st = copy.deepcopy(led.state)
                self.assertEqual(set(st["cells"]), {"128", "325"})
                for cell in (0, 127, 326):
                    self.assertEqual(code(L.op_reserve, copy.deepcopy(st), spec, cell, 0, "T"), "CELL_NOT_IN_UNIVERSE")
                L.op_reserve(st, spec, 128, 0, "T")
                L.op_reserve(st, spec, 325, 2, "T")
                self.assertEqual(code(L.op_reserve, st, spec, 128, 4, "T"), "DUPLICATE_CELL")
                forged = copy.deepcopy(led.state)
                forged["cells"]["0"] = {"status": "SEALED", "attempt": None, "infra_tears": 0}
                self.assertEqual(code(L.validate_state, forged, spec), "LEDGER_CORRUPT")
                reset = copy.deepcopy(led.state)
                reset["cap"]["cap_usec"] = GS.ABSOLUTE_CAP_US
                self.assertEqual(code(L.validate_state, reset, spec), "CAP_CHANGE_FORBIDDEN")
            finally:
                lock.release()


class Cap(unittest.TestCase):
    GOOD = {"absolute_campaign_cap_usec": GS.ABSOLUTE_CAP_US, "predecessor_settled_usec": GS.PREDECESSOR_SETTLED_US,
            "successor_residual_cap_usec": GS.RESIDUAL_CAP_US, "cap_usec": GS.RESIDUAL_CAP_US,
            "invariant": [115, 100], "reservation_usec": GS.RESERVATION_US}

    def test_exact_values(self):
        self.assertEqual(GS.ABSOLUTE_CAP_US - GS.PREDECESSOR_SETTLED_US, GS.RESIDUAL_CAP_US)
        self.assertEqual(GS.ABSOLUTE_CAP_US, 300 * 3600 * 10 ** 6)
        self.assertEqual(BINDING["accounting"]["settled_usec"], GS.PREDECESSOR_SETTLED_US)
        self.assertIsNone(code(SP.check_cost_cap, self.GOOD))

    def test_fail_closed(self):
        cases = {
            "reset_to_300": ({"cap_usec": GS.ABSOLUTE_CAP_US, "successor_residual_cap_usec": GS.ABSOLUTE_CAP_US}, "CAP_RESET_FORBIDDEN"),
            "omit_predecessor": ({"predecessor_settled_usec": 0}, "CAP_PREDECESSOR_CONSUMPTION"),
            "changed_residual": ({"cap_usec": GS.RESIDUAL_CAP_US - 1}, "CAP_RESIDUAL_CHANGED"),
            "changed_invariant": ({"invariant": [110, 100]}, "CAP_INVARIANT_CHANGED"),
            "raised_absolute": ({"absolute_campaign_cap_usec": GS.ABSOLUTE_CAP_US + 3_600_000_000}, "CAP_ABSOLUTE_CHANGED"),
            "double_charge": ({"cap_usec": GS.ABSOLUTE_CAP_US - 2 * GS.PREDECESSOR_SETTLED_US,
                               "successor_residual_cap_usec": GS.ABSOLUTE_CAP_US - 2 * GS.PREDECESSOR_SETTLED_US},
                              "CAP_RESIDUAL_CHANGED"),
            "undercharge_keeper_exit": ({"predecessor_settled_usec": GS.PREDECESSOR_SETTLED_US - 70947},
                                        "CAP_PREDECESSOR_CONSUMPTION"),
        }
        for name, (delta, want) in cases.items():
            with self.subTest(name):
                self.assertEqual(code(SP.check_cost_cap, {**self.GOOD, **delta}), want)


class CompositeTolerance(unittest.TestCase):
    def rep(self):
        pairs = {str(c): {"record_sha256": f"{c:064x}"} for c in range(128)}
        return {"issues": {GS.STOP_ISSUE: [BINDING["predecessor"]["stop"]], "D_unsettled_supervisor_runs": [GS.UNSETTLED_RUN]},
                "disposition": "HALTED", "pairs": pairs, "A_completeness": {"sealed": 128},
                "ledger_state_sha256": BINDING["ledger_state_sha256"],
                "genesis_entry_sha256": BINDING["journal"]["genesis_entry_sha256"]}

    def tol(self, rep):
        return {**GC.tolerance_for_production(BINDING), "pairs_sha256": GC.pairs_digest(rep["pairs"])}

    def test_exact_tolerance(self):
        r = self.rep()
        self.assertEqual(GC.predecessor_problems(r, self.tol(r)), [])

    def test_real_binding_digest_is_the_tolerance(self):
        self.assertEqual(GC.tolerance_for_production(BINDING)["pairs_sha256"],
                         "07e6adb37efd624d182df6d50c396b4f1d4da26aeec374a18a9e1f7a66a70067")

    def test_any_other_issue_refuses(self):
        mutations = {
            "extra_issue": lambda r: r["issues"].__setitem__("B_pair_refused", [[3, "RECORD_MISMATCH", ""]]),
            "open_attempts": lambda r: r["issues"].__setitem__("D_open_attempts", ["A00001-C0001"]),
            "other_stop": lambda r: r["issues"].__setitem__(GS.STOP_ISSUE, [{"reason": "RETRY_LIMIT"}]),
            "other_run": lambda r: r["issues"].__setitem__("D_unsettled_supervisor_runs", ["R-other"]),
            "missing_pair": lambda r: r["pairs"].pop("127"),
            "not_halted": lambda r: r.__setitem__("disposition", "OPEN"),
            "state_changed": lambda r: r.__setitem__("ledger_state_sha256", "0" * 64),
        }
        for name, m in mutations.items():
            with self.subTest(name):
                r = self.rep()
                tol = self.tol(r)
                m(r)
                self.assertTrue(GC.predecessor_problems(r, tol), name)

    def test_attestation_only_from_complete(self):
        for state in ("INCOMPLETE", "REFUSED"):
            rep = {"schema": GS.COMPOSITE_AUDIT_SCHEMA, "state": state, "problems": []}
            self.assertEqual(code(GC.build_composite_attestation, rep, successor_checkpoint_sha256="a",
                                  predecessor_checkpoint_sha256="b"), "ATTESTATION_REFUSED")


class HostAndProcesses(unittest.TestCase):
    def test_argv_element_classification_never_self_matches(self):
        self.assertIsNone(H.classify_argv(["bash", "-c", "cd /x && python gs_entry.py _supervise"]))
        self.assertIsNone(H.classify_argv(["python", "-B", "/x/code/gs_entry.py", "preflight"]))
        self.assertIsNone(H.classify_argv(["grep", "qualify5.py"]))
        self.assertIsNone(H.classify_argv(["pgrep", "-af", "prov_supervisor.py"]))
        self.assertEqual(H.classify_argv(["python", "-B", "/x/code/gs_entry.py", "_supervise"]), "ENTRY_LIVE")
        self.assertEqual(H.classify_argv(["/usr/bin/env", "-i", "PATH=/usr/bin", "/venv/python", "/r/code/qualify5.py", "--cell", "128"]),
                         "CERTIFIER")
        self.assertEqual(H.classify_argv(["python", "/r/tests/prov_synthetic_worker.py", "--cell", "1"]), "SUPERVISOR_OR_WORKER")

    def test_identity_and_containment_problems(self):
        bound = {"bound_facts": {"host_name": "h", "libc_sha256": "new"}, "system_libraries_sha256": {"/l": "1"},
                 "packages": {"libc6": "u4"}, "boot_id": "b"}
        live = {"host_name": "h", "libc_sha256": "new", "system_libraries_sha256": {"/l": "1"}, "packages": {"libc6": "u4"},
                "boot_id": "b"}
        self.assertEqual(H.identity_problems(bound, live), [])
        for k, v in (("boot_id", "rebooted"), ("libc_sha256", "old"), ("packages", {"libc6": "u5"}),
                     ("system_libraries_sha256", {"/l": "2"})):
            with self.subTest(k):
                self.assertTrue(H.identity_problems(bound, {**live, k: v}))
        post = {k: f"bound-{k}" for k in GS.CONTAINMENT_KEYS}
        self.assertEqual(H.containment_problems(post, dict(post)), [])
        self.assertTrue(H.containment_problems(post, {**post, "holds": []}))


@unittest.skipUnless(HAVE_CP, "the checkpoint is built first")
class FrozenObjects(unittest.TestCase):
    def test_checkpoint_bindings(self):
        cp, sha = SP.load_checkpoint()
        self.assertEqual(cp["production_universe"], list(GS.NEW_CELLS))
        self.assertEqual(cp["carryover_cells"], list(GS.OLD_CELLS))
        self.assertEqual(cp["countersignature_sha256"], GS.COUNTERSIGNATURE_SHA256)
        self.assertEqual(cp["predecessor"]["checkpoint_sha256"][:8], "dd4c89d7")
        self.assertEqual(cp["cost_cap"]["cap_usec"], GS.RESIDUAL_CAP_US)
        self.assertEqual(cp["host"]["boot_id"], GS.BOUND_BOOT_ID)
        self.assertEqual(sorted(cp["conditions"]), list("abcde"))
        spec = SP.spec_from_checkpoint(cp, sha)
        self.assertEqual((spec.cell_indices, spec.cap_usec), (list(GS.NEW_CELLS), GS.RESIDUAL_CAP_US))

    @unittest.skipUnless(GS.AUTHORIZATION.exists(), "authorization is written after the checkpoint")
    def test_authorization_recomputes_and_refuses_mutation(self):
        import gs_authorization as GA
        cp, sha = SP.load_checkpoint()
        spec = SP.spec_from_checkpoint(cp, sha)
        auth, _asha = GA.load_authorization(GS.AUTHORIZATION, GS.AUTHORIZATION_HASH)
        GA.verify_authorization(auth, spec, cp)
        for mutate in (lambda a: a["cap"].__setitem__("cap_usec", GS.ABSOLUTE_CAP_US),
                       lambda a: a["universe"].__setitem__("first_index", 0),
                       lambda a: a["host"].__setitem__("boot_id", "other"),
                       lambda a: a.__setitem__("q6_result_sha256", "0" * 64)):
            bad = copy.deepcopy(auth)
            mutate(bad)
            self.assertEqual(code(GA.verify_authorization, bad, spec, cp), "AUTHORIZATION_MISMATCH")


if __name__ == "__main__":
    unittest.main()
