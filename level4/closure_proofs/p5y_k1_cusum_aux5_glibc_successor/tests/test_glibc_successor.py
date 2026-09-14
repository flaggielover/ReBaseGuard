"""Adversarial tests for the CUSUM Aux5 new-glibc successor governance freeze.

Governance only: every predecessor object here is a SYNTHETIC fixture in a temporary directory, built with the frozen
journal and reaper formats. No certifier runs, no production root or ledger is touched, nothing is authorized.

  python -B tests/test_glibc_successor.py
"""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import glibc_successor as G                                                     # noqa: E402

L = G.load_frozen(G.REPO)
from prod_common import canonical, sha256_bytes                                 # noqa: E402

E = G.EXPECTED
BTIME, CLK, BOOT = 1788930261, 100, "eefa85dc-14db-4ba0-912f-f95eeece9c2b"
DRIFT_NS = 1789366259784621549
DRIFT = DRIFT_NS / 1e9
GENESIS_T = 1789300637.8358
AUTH_BLOCK = {"authorization_id": E["authorization_id"], "authorization_sha256": E["authorization_sha256"],
              "countersignature_sha256": E["countersignature_sha256"], "ledger_id": E["ledger_id"],
              "production_run_id": E["production_run_id"]}
QUAL_SHAS = {"5895bcf5769eae6386483965af10dabc8b7ed25ebfc6028ba2542fe65acc387a",
             "cd0e923c5b4f1d0e489a9733fce26351b8c2c5f659c46d152d176e4789d7eba5",
             "28e6a53e57f10c46b2f965b27d0b7be6395da8170acb604fa34db6e474aec59f",
             "d08a694c56793157069bb1069b7ffe07b80582ec6197d42d9b4de9539505440d"}
RUN_ID = "R20260913T115713Z-103963"


def reaper(kind, pid, cpu, *, sup, exit_code, t):
    body = {"schema": L.REAPER_SCHEMA, "kind": kind, "pid": pid, "boot_id": BOOT, "t_wall": t, "cpu_usec": cpu,
            "is_supervisor": sup, "exited": None if kind == "KEEPER_EXIT" else True, "exit_code": exit_code, "signal": None}
    return {**body, "record_id": sha256_bytes(canonical(body))}


def make_predecessor(base: Path, *, n_old=128, post_drift_admission=False, post_drift_start=False,
                     disposition=G.TERMINAL, science_delta=0, final_reap_cpu_delta=0) -> Path:
    """A synthetic, format-faithful terminal predecessor with the real bound accounting totals."""
    root = base / "root"
    root.mkdir()
    events = [(GENESIS_T, "GENESIS", {"checkpoint_sha256": E["checkpoint_sha256"], "production_authorization": AUTH_BLOCK}),
              (GENESIS_T + 0.004, "RUN_OPENED", {"run_id": RUN_ID})]
    attempts, cells = {}, {str(i): {"status": "PENDING", "attempt": None, "infra_tears": 0} for i in range(326)}
    science = 262623734174 + science_delta
    per = science // 128
    for i in range(n_old):
        aid = f"A{i:05d}-C{i:04d}"
        t_res = GENESIS_T + 5 + i * 500
        if post_drift_admission and i == n_old - 1:
            t_res = DRIFT + 30
        t_start = t_res + (1800 if post_drift_start and i == n_old - 1 and not post_drift_admission else 0)
        if post_drift_start and i == n_old - 1:
            t_start = DRIFT + 45
        t_run = t_start + 0.02
        t_close = max(t_run, t_res) + 2070 if i < n_old - 4 else DRIFT + 100 + i
        rec_rel = f"attempts/{aid}/aux5_CUSUM_{i}_256.json"
        env_rel = f"provenance/{aid}/CUSUM_{i:04d}.envelope.json"
        rec = json.dumps({"fixture": "SYNTHETIC_NOT_SCIENCE", "cell_index": i}).encode()
        (root / rec_rel).parent.mkdir(parents=True)
        (root / rec_rel).write_bytes(rec)
        env = json.dumps({"scientific_record": {"sha256": sha256_bytes(rec)}, "cell": {"cell_index": i},
                          "authorization": {"authorization_sha256": E["authorization_sha256"],
                                            "countersignature_sha256": E["countersignature_sha256"]},
                          "qualification": {"is_qualification_record": False}}).encode()
        (root / env_rel).parent.mkdir(parents=True)
        (root / env_rel).write_bytes(env)
        charge = per if i < 127 else science - per * 127
        attempts[aid] = {"cell": i, "status": "SEALED", "core": [0, 2, 4, 6][i % 4], "run_id": RUN_ID, "boot_id": BOOT,
                         "t_reserved": t_res, "pid": 200000 + i, "pid_start_ticks": int(round((t_start - 0.05 - BTIME) * CLK)),
                         "t_spawn": t_start, "cpu_sample_usec": charge, "record": rec_rel, "charge_usec": charge,
                         "charge_evidence": "WAIT4_RUSAGE", "seal": {"record_sha256": sha256_bytes(rec),
                                                                   "scientific_content_hash": sha256_bytes(b"sci%d" % i)},
                         "t_closed": t_close, "provenance": {"envelope": env_rel, "envelope_sha256": sha256_bytes(env)}}
        cells[str(i)] = {"status": "SEALED", "attempt": aid, "infra_tears": 0}
        events += [(t_res, "RESERVED", {"cell": i, "core": attempts[aid]["core"]}),
                   (t_run, "RUNNING", {"attempt": aid, "pid": 200000 + i}),
                   (t_close, "SEALED", {"attempt": aid, "cell": i}), (t_close + 0.17, "PROVENANCE_BOUND", {"attempt": aid})]
    t_stop = DRIFT + 90.06
    events.append((t_stop, G.STOP_EVENT, {"reason": "HOST_DRIFT"}))
    t_disp = max(t for t, _e, _d in events) + 0.2
    events.append((t_disp, "DISPOSITION_" + str(disposition), {"run_id": RUN_ID}))
    events.sort(key=lambda x: x[0])
    refused_sup = reaper("CHILD_REAPED", 102197, 4366444, sup=True, exit_code=30, t=GENESIS_T - 4000)
    refused_keeper = reaper("KEEPER_EXIT", 102196, 75363, sup=False, exit_code=None, t=GENESIS_T - 4000)
    final_sup = reaper("CHILD_REAPED", 103963, 262682097826 + final_reap_cpu_delta, sup=True, exit_code=20, t=t_disp + 0.01)
    final_keeper = reaper("KEEPER_EXIT", 103960, 70947, sup=False, exit_code=None, t=t_disp + 0.02)
    (root / "reaper.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n"
                                               for r in (refused_sup, refused_keeper, final_sup, final_keeper)))
    overhead = {refused_sup["record_id"]: 4366444, refused_keeper["record_id"]: 75363}
    st = {"schema": L.LEDGER_SCHEMA, "mode": "PRODUCTION", "campaign_id": "p5y_k1_cusum_aux5_production_provenance_r1",
          "checkpoint_sha256": E["checkpoint_sha256"],
          "cap": {"cap_usec": E["cap_usec"], "reservation_usec": E["reservation_usec"], "invariant": E["invariant"]},
          "cells": cells, "attempts": attempts, "overhead_charges": overhead,
          "supervisor_runs": {RUN_ID: {"pid": 103963, "boot_id": BOOT, "started_wall": GENESIS_T + 0.004, "ended_wall": t_disp,
                                       "end": "EXITED", "settled": False, "self_cpu_seen_usec": 58121474,
                                       "children_usec": 262623904846, "charged_usec": 58292146, "last_charge_wall": t_disp,
                                       "settlement": None}},
          "committed_usec": {"science": science, "torn": 0, "failed": 0, "released": 0, "supervisor": 62733953},
          "production_authorization": AUTH_BLOCK, "disposition": disposition,
          G.STOP_KEY: {"reason": "HOST_DRIFT", "t_wall": t_stop,
                       "problems": [f"host libc_sha256: live '{E['new_libc_sha256']}' != bound '{E['bound_libc_sha256']}'"]},
          "seq": len(events) - 1, "prev_state_sha256": None, "first_admission_wall": GENESIS_T + 5}
    prev, lines = None, []
    for seq, (t, ev, detail) in enumerate(events):
        state = L.state_sha256(st) if seq == len(events) - 1 else sha256_bytes(b"state%d" % seq)
        e = {"schema": L.JOURNAL_SCHEMA, "seq": seq, "event": ev, "state_sha256": state,
             "prev_entry_sha256": prev["entry_sha256"] if prev else None, "t_wall": t, "detail": detail}
        e["entry_sha256"] = sha256_bytes(canonical(e))
        lines.append(json.dumps(e, sort_keys=True))
        prev = e
    (root / "journal.jsonl").write_text("\n".join(lines) + "\n")
    (root / "ledger.json").write_text(json.dumps(st, indent=1, sort_keys=True) + "\n")
    return root


def bind(root: Path, *, verified_pairs=128) -> dict:
    st = json.loads((root / "ledger.json").read_text())
    entries, _torn = L.Ledger.read_journal(root / "journal.jsonl")
    integrity = {"frozen_audit": {"verified_pairs": verified_pairs, "sealed": 128, "domain": 326, "complete": False,
                                  "issue_keys": sorted(G.AUDIT_ALLOWED_ISSUES), "pairs_sha256": "0" * 64,
                                  "ledger_state_sha256": L.state_sha256(st), "genesis_entry_sha256": entries[0]["entry_sha256"]},
                 "full_seal_reverified_cells": 128}
    return G.analyze_predecessor(root, L=L, qualification_shas=QUAL_SHAS,
                                 clock={"btime": BTIME, "clk_tck": CLK, "boot_id": BOOT},
                                 drift={"libc_path": G.LIBC, "libc_ctime_ns": DRIFT_NS, "libc_sha256_live": E["new_libc_sha256"],
                                        "bound_libc_sha256": E["bound_libc_sha256"]},
                                 integrity=integrity, host_facts={"libc_sha256": E["new_libc_sha256"]})


class Tmp:
    def __enter__(self):
        self.d = tempfile.TemporaryDirectory()
        return Path(self.d.name)

    def __exit__(self, *exc):
        self.d.cleanup()


def fixture_expected(root: Path) -> dict:
    return {**E, "runtime_root": str(root)}


def cap_doc(**over) -> dict:
    doc = {"schema": G.CAP_SCHEMA, "absolute_campaign_cap_usec": E["cap_usec"], "predecessor_settled_usec": E["settled_usec"],
           "successor_residual_cap_usec": G.RESIDUAL_CAP_USEC, "admission_invariant": [115, 100],
           "reservation_usec": E["reservation_usec"], "absolute_cap_raise_allowed": False,
           "predecessor_consumption_removable": False, "qualification_cpu": {"counted_against_cap": False, "disclosed": True}}
    doc.update(over)
    return doc


REFERENCE = G.q6_reference(G.REPO)


def q6_result(**over) -> dict:
    res = {"schema": G.Q6_RESULT_SCHEMA, "qualification_P1_P5": "PASS", "libc_sha256": E["new_libc_sha256"],
           "glibc_package_version": E["new_glibc_package_version"],
           "cells": {cell: {rep: {"record_sha256": sha256_bytes(f"new {cell}{rep}".encode()),
                                  "scientific_content_hash": ref["scientific_content_hash"],
                                  "certificate_hashes": dict(ref["certificate_hashes"])} for rep in ("A", "B")}
                     for cell, ref in REFERENCE["cells"].items()}}
    res.update(over)
    return res


PROPOSAL_SHA = "a" * 64


def countersignature(q6_sha, **over) -> dict:
    cs = {"schema": G.COUNTERSIGN_SCHEMA, "verdict": G.COUNTERSIGN_VERDICT, "synthetic": False, "proposal_sha256": PROPOSAL_SHA,
          "q6_result_sha256": q6_sha, "reviewer": "TEST_REVIEWER", "reviewer_independent_of_authoring_session": True}
    cs.update(over)
    return cs


def checkpoint(q6_sha, cs_sha, **over) -> dict:
    ck = {"schema": G.CHECKPOINT_SCHEMA, "proposal_sha256": PROPOSAL_SHA, "countersignature_sha256": cs_sha,
          "q6_result_sha256": q6_sha, "carryover_cells": list(G.OLD_CELLS), "production_universe": list(G.NEW_CELLS),
          "successor_residual_cap_usec": G.RESIDUAL_CAP_USEC}
    ck.update(over)
    return ck


class PredecessorBindingTests(unittest.TestCase):
    def assertFailsWith(self, problems, needle):
        self.assertTrue(any(needle in x for x in problems), f"{needle!r} not in {problems[:6]}")

    def test_valid_predecessor_forensic_fixture(self):
        with Tmp() as d:
            root = make_predecessor(d)
            b = bind(root)
            self.assertEqual(G.verify_binding(b, fixture_expected(root)), [])
            self.assertEqual(b["accounting"]["settled_usec"], E["settled_usec"])
            self.assertEqual([c["cell"] for c in b["cells"]], list(range(128)))

    def test_modified_old_ledger_hash_fails(self):
        with Tmp() as d:
            root = make_predecessor(d)
            committed = bind(root)
            st = json.loads((root / "ledger.json").read_text())
            st["attempts"]["A00005-C0005"]["charge_usec"] += 1
            (root / "ledger.json").write_text(json.dumps(st, indent=1, sort_keys=True) + "\n")
            live = bind(root)
            self.assertFailsWith(G.compare_live(committed, live), "PREDECESSOR_CHANGED_SINCE_BINDING")
            self.assertTrue(G.verify_binding(live, fixture_expected(root)))

    def test_missing_envelope_fails(self):
        with Tmp() as d:
            root = make_predecessor(d)
            (root / "provenance/A00042-C0042/CUSUM_0042.envelope.json").unlink()
            self.assertFailsWith(G.verify_binding(bind(root), fixture_expected(root)), "ENVELOPE_MISSING_OR_CHANGED: cell 42")

    def test_post_drift_admission_fails(self):
        with Tmp() as d:
            root = make_predecessor(d, post_drift_admission=True)
            self.assertFailsWith(G.verify_binding(bind(root), fixture_expected(root)), "POST_DRIFT_ADMISSION")

    def test_post_drift_worker_start_fails(self):
        with Tmp() as d:
            root = make_predecessor(d, post_drift_start=True)
            problems = G.verify_binding(bind(root), fixture_expected(root))
            self.assertFailsWith(problems, "POST_DRIFT_WORKER_START")
            self.assertFalse(any("POST_DRIFT_ADMISSION" in x for x in problems), problems[:6])

    def test_missing_old_cell_fails(self):
        with Tmp() as d:
            root = make_predecessor(d, n_old=127)
            self.assertFailsWith(G.verify_binding(bind(root), fixture_expected(root)), "OLD_CELLS_NOT_EXACTLY_0_127")

    def test_altered_cpu_settlement_fails(self):
        with Tmp() as d:
            root = make_predecessor(d, final_reap_cpu_delta=1)
            self.assertFailsWith(G.verify_binding(bind(root), fixture_expected(root)), "ACCOUNTING: settled")
        with Tmp() as d:
            root = make_predecessor(d)
            b = bind(root)
            b["accounting"]["settled_usec"] -= 1
            self.assertFailsWith(G.verify_binding(b, fixture_expected(root)), "ACCOUNTING: settled")
            b = bind(root)
            b["accounting"]["unmatched_overhead"] = []
            b["accounting"]["unmatched_overhead_usec"] = 0
            self.assertFailsWith(G.verify_binding(b, fixture_expected(root)), "charged zero or two times")

    def test_ledger_not_terminal_fails(self):
        with Tmp() as d:
            root = make_predecessor(d, disposition="OPEN")
            self.assertFailsWith(G.verify_binding(bind(root), fixture_expected(root)), "PREDECESSOR_NOT_TERMINAL")

    def test_old_pair_verification_failure_fails(self):
        with Tmp() as d:
            root = make_predecessor(d)
            self.assertFailsWith(G.verify_binding(bind(root, verified_pairs=127), fixture_expected(root)),
                                 "OLD_PAIR_VERIFICATION_FAILED")

    def test_qualification_record_reuse_and_duplicate_fail(self):
        with Tmp() as d:
            root = make_predecessor(d)
            b = bind(root)
            QUAL_SHAS.add(b["cells"][7]["record_sha256_file"])
            try:
                self.assertFailsWith(G.verify_binding(bind(root), fixture_expected(root)), "QUALIFICATION_RECORD_REUSE: cell 7")
            finally:
                QUAL_SHAS.discard(b["cells"][7]["record_sha256_file"])
            b["cells"][9]["scientific_content_hash"] = b["cells"][8]["scientific_content_hash"]
            b["cells_digest_sha256"] = G.sha256_bytes(G.canon(b["cells"]))
            self.assertFailsWith(G.verify_binding(b, fixture_expected(root)), "DUPLICATE: scientific_content_hash")


class PartitionCapTests(unittest.TestCase):
    def test_exact_partition_passes(self):
        self.assertEqual(G.check_partition(G.OLD_CELLS, G.NEW_CELLS), [])

    def test_overlapping_successor_cell_fails(self):
        self.assertTrue(any("PARTITION_OVERLAP" in x for x in G.check_partition(G.OLD_CELLS, (127,) + G.NEW_CELLS)))

    def test_missing_cell_in_union_fails(self):
        self.assertTrue(any("PARTITION_UNION" in x for x in G.check_partition(G.OLD_CELLS, G.NEW_CELLS[:-1])))

    def test_recomputation_of_old_cell_fails(self):
        self.assertEqual(G.check_no_recomputation([128, 200, 325]), [])
        self.assertTrue(G.check_no_recomputation([128, 5]))

    def test_cap_continuity(self):
        with Tmp() as d:
            b = bind(make_predecessor(d))
        self.assertEqual(G.check_cap(cap_doc(), b), [])
        self.assertTrue(any("CAP_RESET_FORBIDDEN" in x for x in G.check_cap(cap_doc(successor_residual_cap_usec=E["cap_usec"]), b)))
        self.assertTrue(G.check_cap(cap_doc(absolute_campaign_cap_usec=350 * 3600 * 10**6), b))
        self.assertTrue(G.check_cap(cap_doc(predecessor_settled_usec=0, successor_residual_cap_usec=E["cap_usec"]), b))
        self.assertTrue(G.check_cap(cap_doc(admission_invariant=[110, 100]), b))
        self.assertTrue(G.check_cap(cap_doc(qualification_cpu={"counted_against_cap": False, "disclosed": False}), b))


class Q6ReadinessTests(unittest.TestCase):
    def test_q6_reference_matches_frozen_qualification(self):
        self.assertEqual(REFERENCE["cells"]["318"]["scientific_content_hash"],
                         "01ff4f7a2632102475805537f439ccbe7932b68339eafa37d5ecdd03c13edda9")
        self.assertEqual(REFERENCE["cells"]["323"]["scientific_content_hash"],
                         "054a5ef0cd932ddcac3b4b2dc1a9b461e353ae6b51a2d726a5ccbc9607e57077")
        self.assertEqual({c["certificate_count"] for c in REFERENCE["cells"].values()}, {28})

    def test_q6_missing_proposal_may_exist_but_launch_not_ready(self):
        q6 = G.evaluate_q6(None, REFERENCE)
        self.assertEqual(q6["state"], "ABSENT")
        rep = G.launch_readiness(proposal_problems=[], proposal_sha256=PROPOSAL_SHA, q6=q6)
        self.assertEqual(rep["state"], "NOT_READY")
        self.assertIn("Q6_ABSENT", rep["problems"])
        self.assertFalse(rep["CARRYOVER_AUTHORIZED"])

    def test_q6_mismatch_rejects_carryover(self):
        res = q6_result()
        key = sorted(res["cells"]["323"]["B"]["certificate_hashes"])[3]
        res["cells"]["323"]["B"]["certificate_hashes"][key] = "0" * 64
        q6 = G.evaluate_q6(res, REFERENCE, result_sha256="b" * 64)
        self.assertEqual((q6["state"], q6["CARRYOVER_ROUTE"]), ("REJECTED", "REJECTED"))
        cs = countersignature("b" * 64)
        rep = G.launch_readiness(proposal_problems=[], proposal_sha256=PROPOSAL_SHA, q6=q6, countersignature=cs,
                                 countersignature_sha256="c" * 64, checkpoint=checkpoint("b" * 64, "c" * 64))
        self.assertEqual((rep["state"], rep["CARRYOVER_ROUTE"]), ("NOT_READY", "REJECTED"))
        sci = q6_result()
        sci["cells"]["318"]["A"]["scientific_content_hash"] = "1" * 64
        self.assertEqual(G.evaluate_q6(sci, REFERENCE)["state"], "REJECTED")
        wrong_host = q6_result(glibc_package_version="2.41-12+deb13u3")
        self.assertEqual(G.evaluate_q6(wrong_host, REFERENCE)["state"], "REJECTED")
        copied = q6_result()
        copied["cells"]["318"]["A"]["record_sha256"] = REFERENCE["cells"]["318"]["reference_record_sha256"]["A"]
        self.assertTrue(any("QUALIFICATION_RECORD_REUSE" in x for x in G.evaluate_q6(copied, REFERENCE)["problems"]))
        single = q6_result()
        del single["cells"]["323"]["B"]
        self.assertEqual(G.evaluate_q6(single, REFERENCE)["state"], "REJECTED")

    def test_countersignature_missing_launch_not_ready(self):
        q6 = G.evaluate_q6(q6_result(), REFERENCE, result_sha256="b" * 64)
        self.assertEqual(q6["state"], "PASS")
        rep = G.launch_readiness(proposal_problems=[], proposal_sha256=PROPOSAL_SHA, q6=q6,
                                 checkpoint=checkpoint("b" * 64, "c" * 64))
        self.assertEqual(rep["state"], "NOT_READY")
        self.assertIn("COUNTERSIGNATURE_ABSENT", rep["problems"])
        stale = countersignature("b" * 64, proposal_sha256="d" * 64)
        rep = G.launch_readiness(proposal_problems=[], proposal_sha256=PROPOSAL_SHA, q6=q6, countersignature=stale,
                                 countersignature_sha256="c" * 64, checkpoint=checkpoint("b" * 64, "c" * 64))
        self.assertIn("COUNTERSIGNATURE_INVALID", rep["problems"])

    def test_exact_valid_composite_state_ready(self):
        q6 = G.evaluate_q6(q6_result(), REFERENCE, result_sha256="b" * 64)
        rep = G.launch_readiness(proposal_problems=[], proposal_sha256=PROPOSAL_SHA, q6=q6,
                                 countersignature=countersignature("b" * 64), countersignature_sha256="c" * 64,
                                 checkpoint=checkpoint("b" * 64, "c" * 64))
        self.assertEqual((rep["state"], rep["CARRYOVER_AUTHORIZED"], rep["problems"]), ("READY_TO_LAUNCH_SUCCESSOR", True, []))
        bad_universe = checkpoint("b" * 64, "c" * 64, production_universe=[5] + list(G.NEW_CELLS))
        rep = G.launch_readiness(proposal_problems=[], proposal_sha256=PROPOSAL_SHA, q6=q6,
                                 countersignature=countersignature("b" * 64), countersignature_sha256="c" * 64,
                                 checkpoint=bad_universe)
        self.assertIn("SUCCESSOR_CHECKPOINT_INVALID", rep["problems"])
        rep = G.launch_readiness(proposal_problems=["X"], proposal_sha256=PROPOSAL_SHA, q6=q6,
                                 countersignature=countersignature("b" * 64), countersignature_sha256="c" * 64,
                                 checkpoint=checkpoint("b" * 64, "c" * 64))
        self.assertEqual(rep["state"], "NOT_READY")


@unittest.skipUnless((G.NS / G.PROPOSAL).is_file(), "the committed proposal manifest is built in the freeze step")
class CommittedProposalTests(unittest.TestCase):
    def test_committed_proposal_verifies_without_q6(self):
        self.assertEqual(G.verify_proposal(), [])
        q6 = G.evaluate_q6(None, json.loads((G.NS / "config/Q6_REFERENCE.json").read_bytes()))
        rep = G.launch_readiness(proposal_problems=[], proposal_sha256=G.sha256_file(G.NS / G.PROPOSAL), q6=q6)
        self.assertEqual(rep["state"], "NOT_READY")

    def test_committed_binding_verifies(self):
        self.assertEqual(G.verify_binding(json.loads((G.NS / "config/PREDECESSOR_BINDING.json").read_bytes())), [])

    def test_changed_governance_artifact_or_binding_breaks_the_proposal(self):
        with Tmp() as d:
            ns = d / "ns"
            shutil.copytree(G.NS, ns)
            with open(ns / "CARRYOVER_PROTOCOL.md", "a") as fh:
                fh.write("\ncarry-over is authorized\n")
            self.assertTrue(any("PROPOSAL_DOES_NOT_REBUILD" in x for x in G.verify_proposal(ns, G.REPO)))
        with Tmp() as d:
            ns = d / "ns"
            shutil.copytree(G.NS, ns)
            b = json.loads((ns / "config/PREDECESSOR_BINDING.json").read_bytes())
            b["files"]["ledger.json"] = "0" * 64
            (ns / "config/PREDECESSOR_BINDING.json").write_bytes(G.dump(b))
            self.assertTrue(any("PROPOSAL_DOES_NOT_REBUILD" in x for x in G.verify_proposal(ns, G.REPO)))

    def test_live_binding_drift_is_refused(self):
        committed = json.loads((G.NS / "config/PREDECESSOR_BINDING.json").read_bytes())
        self.assertEqual(G.compare_live(committed, copy.deepcopy(committed)), [])
        live = copy.deepcopy(committed)
        live["host_facts"]["libc_sha256"] = "0" * 64
        self.assertTrue(any("HOST_CHANGED" in x for x in G.compare_live(committed, live)))
        self.assertTrue(any("HOST_CHANGED" in x for x in G.verify_proposal(live_binding=live)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
