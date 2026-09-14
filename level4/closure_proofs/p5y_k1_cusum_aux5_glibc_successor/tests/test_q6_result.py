"""Focused tests for the Q6 requalification result verifier. Governance only: every mutation happens on a temporary
copy of the successor namespace; no certifier runs and nothing is authorized.

  python -B tests/test_q6_result.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import glibc_successor as G                                                     # noqa: E402
import q6_result as R                                                           # noqa: E402

EV = G.NS / "evidence/requalification_r1"
HAVE_EVIDENCE = (G.NS / R.RESULT_REL).is_file()


class Copy:
    def __enter__(self):
        self.d = tempfile.TemporaryDirectory()
        self.ns = Path(self.d.name) / "ns"
        shutil.copytree(G.NS, self.ns)
        return self.ns

    def __exit__(self, *exc):
        self.d.cleanup()


def rewrite_json(path: Path, mutate) -> None:
    obj = json.loads(path.read_bytes())
    mutate(obj)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")


@unittest.skipUnless(HAVE_EVIDENCE, "the Q6 result is built after requalification")
class Q6ResultTests(unittest.TestCase):
    def test_committed_result_verifies_and_is_not_an_authorization(self):
        self.assertEqual(R.verify_result(), [])
        res = json.loads((G.NS / R.RESULT_REL).read_bytes())
        self.assertEqual((res["Q6_FINAL"], res["CARRYOVER_ROUTE"]), ("PASS", "ELIGIBLE_FOR_INDEPENDENT_REVIEW"))
        self.assertFalse(any(res["authorizations"].values()))
        q6 = G.evaluate_q6(res, json.loads((G.NS / "config/Q6_REFERENCE.json").read_bytes()),
                           result_sha256=G.sha256_file(G.NS / R.RESULT_REL))
        self.assertEqual(q6["state"], "PASS")
        rep = G.launch_readiness(proposal_problems=G.verify_proposal(), proposal_sha256=G.sha256_file(G.NS / G.PROPOSAL), q6=q6)
        self.assertEqual(rep["state"], "NOT_READY")
        self.assertEqual(set(rep["problems"]), {"COUNTERSIGNATURE_ABSENT", "SUCCESSOR_CHECKPOINT_ABSENT"})

    def test_certificate_hash_difference_rejects_carryover(self):
        with Copy() as ns:
            rec = ns / "evidence/requalification_r1/qualification_r1/c323_B/aux5_CUSUM_323_256.json"
            key = []
            rewrite_json(rec, lambda o: (key.append(sorted(o["certificates"])[5]),
                                         o["certificates"][key[0]].__setitem__("certificate_hash", "0" * 64)))
            result, _problems = R.build_result(ns, G.REPO)
            self.assertEqual((result["Q6_FINAL"], result["CARRYOVER_ROUTE"]), ("FAIL", "REJECTED"))
            self.assertEqual(result["Q6_CERTIFICATE_HASH_IDENTITY"], "FAIL")
            self.assertTrue(any(d["field"] == f"certificate_hash[{key[0]}]" and d["repeat"] == "B" for d in result["differences"]))
            self.assertTrue(any("Q6_RESULT_DOES_NOT_REBUILD" in x for x in R.verify_result(ns, G.REPO)))

    def test_scientific_hash_difference_fails_p2_and_q6(self):
        with Copy() as ns:
            rec = ns / "evidence/requalification_r1/qualification_r1/c318_A/aux5_CUSUM_318_256.json"
            rewrite_json(rec, lambda o: o.__setitem__("scientific_content_hash", "1" * 64))
            result, _ = R.build_result(ns, G.REPO)
            self.assertFalse(result["criteria"]["P2_determinism_scientific_hash"])
            self.assertEqual((result["Q6_SCIENTIFIC_HASH_IDENTITY"], result["Q6_FINAL"]), ("FAIL", "FAIL"))

    def test_nonzero_exit_fails_original_gates(self):
        with Copy() as ns:
            (ns / "evidence/requalification_r1/qualification_r1/c323_A/rc").write_text("1\n")
            result, _ = R.build_result(ns, G.REPO)
            self.assertFalse(result["criteria"]["P1_runs_complete"])
            self.assertEqual((result["Q6_ORIGINAL_GATES"], result["Q6_FINAL"]), ("FAIL", "FAIL"))

    def test_containment_disarmed_during_run_fails(self):
        with Copy() as ns:
            rewrite_json(ns / "evidence/containment/POST_RUN_STATE.json",
                         lambda o: o["units"].__setitem__("apt-daily-upgrade.timer", {"enabled": "enabled", "active": "active"}))
            problems = R.verify_result(ns, G.REPO)
            self.assertTrue(any("CONTAINMENT_POST_RUN" in x for x in problems), problems[:5])

    def test_wrong_glibc_at_run_end_fails(self):
        with Copy() as ns:
            rewrite_json(ns / "evidence/requalification_r1/HOST_AT_RUN_END.json",
                         lambda o: o.__setitem__("glibc_package_version", "2.41-12+deb13u3"))
            result, problems = R.build_result(ns, G.REPO)
            self.assertTrue(any("HOST_RUN_END" in x for x in problems))
            self.assertEqual(result["Q6_FINAL"], "FAIL")

    def test_wrong_cpu_pinning_fails(self):
        with Copy() as ns:
            rewrite_json(ns / "evidence/requalification_r1/AFFINITY_AT_LAUNCH.json",
                         lambda o: o["318B"].__setitem__("affinity", "3"))
            result, problems = R.build_result(ns, G.REPO)
            self.assertTrue(any("RUN_SHAPE" in x for x in problems) or any("METADATA_LINK" in x for x in problems))
            self.assertEqual(result["Q6_FINAL"], "FAIL")

    def test_qualification_record_copied_from_predecessor_fails(self):
        with Copy() as ns:
            src = G.REPO / G.AUX5_REL / "evidence/qualification_r1/c318_A/aux5_CUSUM_318_256.json"
            shutil.copyfile(src, ns / "evidence/requalification_r1/qualification_r1/c318_A/aux5_CUSUM_318_256.json")
            result, _ = R.build_result(ns, G.REPO)
            self.assertTrue(any("QUALIFICATION_RECORD_REUSE" in x for x in result["q6_evaluation"]["problems"]))
            self.assertEqual(result["Q6_FINAL"], "FAIL")

    def test_missing_run_fails_closed(self):
        with Copy() as ns:
            shutil.rmtree(ns / "evidence/requalification_r1/qualification_r1/c323_B")
            problems = R.verify_result(ns, G.REPO)
            self.assertTrue(problems)

    def test_changed_governance_binding_fails(self):
        with Copy() as ns:
            with open(ns / "config/REQUALIFICATION_PROTOCOL.json", "a") as fh:
                fh.write(" ")
            self.assertTrue(any("BINDING: config/REQUALIFICATION_PROTOCOL.json" in x for x in R.verify_result(ns, G.REPO)))

    def test_cap_consequence_threshold(self):
        sys.path.insert(0, str(G.REPO / G.AUX5_REL / "code"))
        import cap_formula
        self.assertEqual(cap_formula.cap(c_max_cpu_seconds=repr(R.MAX_CMAX_FOR_CAP_300))["CAP_cpu_h"], 300)
        self.assertEqual(cap_formula.cap(c_max_cpu_seconds="2432")["CAP_cpu_h"], 350)


if __name__ == "__main__":
    unittest.main(verbosity=2)
