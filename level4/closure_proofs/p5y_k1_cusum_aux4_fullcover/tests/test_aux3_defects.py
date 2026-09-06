"""PHASE 1: reproduce every adjudicated Aux3 identity defect, as controls.

These tests PASS by demonstrating the defect is really present in the committed
Aux3 bytes. They are written against the predecessor without mutating any of its
files, and they are the measured justification for each Aux4 repair.

Adjudicated: PRODUCER_MANIFEST, STRICT_PRODUCER_ENFORCEMENT, RUNTIME_BINDING,
CERTIFICATE_DETERMINISM and AUXILIARY_GOVERNANCE all FAIL.
"""
from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["K1_THREADS_PINNED"] = "1"

import copy                                                     # noqa: E402
import json                                                     # noqa: E402
import subprocess                                               # noqa: E402
import sys                                                      # noqa: E402
import unittest                                                 # noqa: E402
from pathlib import Path                                        # noqa: E402

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import ancestry4                                                # noqa: E402

AUX3 = ancestry4.AUX3_NS
AUX3_MANIFEST = json.loads(
    (AUX3 / "manifests" / "producer_manifest_v1.json").read_text())
AUX3_RECORDS = sorted((AUX3 / "diagnostics" / "cells").glob("aux3_CUSUM_*.json"))
BLAS_EVIDENCE = NS / "evidence" / "blas_kernel_sensitivity.json"


def _aux3(module: str):
    """Import an Aux3 module in isolation and return it."""
    if str(AUX3 / "code") not in sys.path:
        sys.path.insert(0, str(AUX3 / "code"))
    return __import__(module)


class Defect1ManifestScope(unittest.TestCase):
    """PRODUCER_MANIFEST: an execution-relevant source outside the manifest."""

    SP = ("level4/closure_proofs/p5y_k1_cusum_completion_successor/code/"
          "successor_producer.py")

    def test_successor_producer_is_execution_relevant(self):
        src = (AUX3 / "code" / "aux_universe.py").read_text()
        self.assertIn("import successor_producer as predecessor", src)
        self.assertIn("predecessor.producer_hash()", src)
        # and its result lands in the record, inside the scientific hash
        self.assertIn("rejected_producer_identities", src)
        rec = json.loads(AUX3_RECORDS[0].read_text())
        self.assertIn("rejected_identities", rec["producer"])

    def test_but_it_is_absent_from_the_aux3_manifest(self):
        self.assertNotIn(self.SP, AUX3_MANIFEST["files"])

    def test_and_a_basename_whitelist_exempts_it_from_coverage(self):
        m3 = _aux3("manifest")
        self.assertIn("successor_producer.py", m3.NON_CERTIFYING_BASENAMES)
        # a basename is not an identity: any file with that name is exempted
        self.assertNotIn("/", "successor_producer.py")

    def test_aux4_binds_by_exact_path_with_no_basename_rule(self):
        import tcb
        self.assertFalse(hasattr(tcb, "NON_CERTIFYING_BASENAMES"))
        for path in tcb.tcb_paths():
            self.assertIn("/", path, "TCB membership must be a path, not a name")


class Defect2GateOrder(unittest.TestCase):
    """STRICT_PRODUCER_ENFORCEMENT: the last check ran too early."""

    def test_aux3_final_check_precedes_assembly_import_and_hash(self):
        body = (AUX3 / "code" / "aux_qualify.py").read_text().split("def run_cell")[1]
        science = body.index("aux_propagate.cell_obligations")
        final_gate = body.index("manifest.require()", science)
        for label, marker in (("auxiliary assembly", 'record["auxiliary_evidence"]'),
                              ("certificate construction", "build_certificates(record"),
                              ("lazy import", "SU.rejected_producer_identities()"),
                              ("scientific hash", 'record["scientific_content_hash"] = CH')):
            self.assertLess(final_gate, body.index(marker),
                            f"Aux3 gate should precede {label}")

    def test_aux4_final_gate_runs_after_the_scientific_hash(self):
        body = (NS / "code" / "qualify4.py").read_text().split("def run_cell")[1]
        first_hash = body.index('record["scientific_content_hash"] = H')
        final_gate = body.index("manifest_v2.final_gate(scipy_guard=guard)")
        self.assertGreater(final_gate, first_hash)
        self.assertGreater(final_gate, body.index("build_certificates(record"))
        self.assertGreater(final_gate, body.index('record["auxiliary_evidence"]'))


class Defect3RuntimeBinding(unittest.TestCase):
    """RUNTIME_BINDING: the numerical backend was not identified."""

    def test_aux3_bound_no_blas_kernel_or_backend_bytes(self):
        runtime = AUX3_MANIFEST["runtime"]
        for absent in ("openblas_runtime_corename", "openblas_config",
                       "backend_libraries"):
            self.assertNotIn(absent, runtime)
        self.assertEqual(runtime.get("python_major_minor"), "3.12")   # not the build

    def test_blas_kernel_changes_certified_candidates(self):
        """Measured on this host: same numpy, different kernel, different candidates."""
        self.assertTrue(BLAS_EVIDENCE.exists(),
                        "the BLAS sensitivity measurement must be committed")
        ev = json.loads(BLAS_EVIDENCE.read_text())
        self.assertGreater(ev["candidates_differing"], 0)
        self.assertEqual(ev["kernels_compared"], ["SkylakeX", "Haswell"])
        self.assertTrue(ev["aux3_declared_identity_identical_across_kernels"])

    def test_aux4_binds_the_runtime_kernel_and_backend_bytes(self):
        import manifest_v2
        runtime = manifest_v2.load()["runtime"]
        self.assertIn("openblas_runtime_corename", runtime)
        self.assertTrue(runtime["backend_libraries"])
        for path in runtime["backend_libraries"]:
            self.assertTrue(path.endswith(".so") or ".so." in path)


class Defect4ProbeNotBound(unittest.TestCase):
    """The SciPy probe steered the contract without being byte-bound."""

    PROBE = ("level4/closure_proofs/p5y_k1_cusum_aux3_successor/evidence/"
             "scipy_execution_probe.json")

    def test_probe_influences_aux3_runtime_contract(self):
        src = (AUX3 / "code" / "manifest.py").read_text()
        self.assertIn("scipy_execution_evidence", src)
        self.assertIn("scipy_status", src)
        self.assertIn("AVAILABILITY_ONLY_IMPORTED_NOT_CALLED",
                      AUX3_MANIFEST["runtime"]["scipy_status"])

    def test_but_the_probe_is_not_in_the_aux3_manifest(self):
        self.assertNotIn(self.PROBE, AUX3_MANIFEST["files"])

    def test_aux4_byte_binds_the_probe_and_enforces_at_runtime(self):
        import manifest_v2, tcb
        self.assertIn(self.PROBE, tcb.tcb_paths())
        self.assertIn(self.PROBE, manifest_v2.load()["files"])
        import scipy_guard
        self.assertTrue(hasattr(scipy_guard, "ScipyGuard"))


class Defect5Determinism(unittest.TestCase):
    """CERTIFICATE_DETERMINISM: the hash depended on module-cache state."""

    def test_a_swallowed_lazy_import_decides_a_hashed_field(self):
        src = (AUX3 / "code" / "aux_universe.py").read_text()
        block = src[src.index("def rejected_producer_identities"):]
        self.assertIn("except Exception:", block)      # failure is swallowed
        rec = json.loads(AUX3_RECORDS[0].read_text())
        # on the real run the import failed: the key is simply absent
        self.assertNotIn("cusum_completion_successor_on_the_fly_hash",
                         rec["producer"]["rejected_identities"])

    def test_the_outcome_moves_the_aux3_scientific_hash(self):
        CH3 = _aux3("aux_certhash")
        rec = json.loads(AUX3_RECORDS[0].read_text())
        base = CH3.record_scientific_hash(rec)
        had_it_worked = copy.deepcopy(rec)
        had_it_worked["producer"]["rejected_identities"][
            "cusum_completion_successor_on_the_fly_hash"] = "a" * 64
        self.assertNotEqual(base, CH3.record_scientific_hash(had_it_worked),
                            "same declared identity, different certificate")

    def test_aux4_performs_no_lazy_import_on_the_certifying_path(self):
        import identity4
        block = (NS / "code" / "identity4.py").read_text()
        block = block[block.index("def rejected_producer_identities"):]
        self.assertNotIn("import ", block.split("def ")[1].split("\n\n")[0])
        self.assertNotIn("except Exception", block)
        self.assertIn("aux3_producer_manifest_hash",
                      identity4.rejected_producer_identities())

    def test_aux4_bootstrap_name_does_not_collide(self):
        self.assertTrue((NS / "code" / "ancestry4.py").exists())
        self.assertFalse((NS / "code" / "ancestry.py").exists())


class Defect6AuxiliaryGovernance(unittest.TestCase):
    """AUXILIARY_GOVERNANCE: scientific fields outside the hash."""

    LOST = ("candidate_suprema", "order", "hermite_weight")

    def test_aux3_hash_ignores_three_scientific_fields(self):
        CH3 = _aux3("aux_certhash")
        rec = json.loads(AUX3_RECORDS[0].read_text())
        base = CH3.record_scientific_hash(rec)
        for field in self.LOST:
            bad = copy.deepcopy(rec)
            if field == "candidate_suprema":
                key = sorted(bad["auxiliary_evidence"][field])[0]
                bad["auxiliary_evidence"][field][key] = "999999/1"
            else:
                bad["auxiliary_evidence"][field] = "TAMPERED"
            self.assertEqual(base, CH3.record_scientific_hash(bad),
                             f"Aux3 was expected to ignore {field}")

    def test_aux3_include_list_is_the_mechanism(self):
        src = (AUX3 / "code" / "aux_certhash.py").read_text()
        block = src[src.index("def auxiliary_evidence("):src.index("def auxiliary_evidence_hash")]
        for field in self.LOST:
            self.assertNotIn(f'"{field}"', block)

    def test_aux4_binds_all_three(self):
        import hash_v2
        rec = json.loads(AUX3_RECORDS[0].read_text())
        base = hash_v2.record_scientific_hash(rec)
        for field in self.LOST:
            bad = copy.deepcopy(rec)
            if field == "candidate_suprema":
                key = sorted(bad["auxiliary_evidence"][field])[0]
                bad["auxiliary_evidence"][field][key] = "999999/1"
            else:
                bad["auxiliary_evidence"][field] = "TAMPERED"
            self.assertNotEqual(base, hash_v2.record_scientific_hash(bad), field)
            self.assertNotEqual(hash_v2.auxiliary_evidence_hash(rec),
                                hash_v2.auxiliary_evidence_hash(bad), field)


class Defect7GreenSuite(unittest.TestCase):
    """The Aux3 suite passes through all of the above."""

    def test_aux3_suite_is_green_or_only_worktree_scoped(self):
        out = subprocess.run(
            [sys.executable, "-m", "unittest", "discover",
             "-s", str(AUX3 / "tests"), "-p", "test_aux3.py"],
            cwd=ancestry4.ROOT, capture_output=True, text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        tail = out.stderr.strip().splitlines()[-1] if out.stderr else ""
        self.assertTrue(tail.startswith("OK")
                        or "test_writes_only_inside_this_namespace" in out.stderr,
                        out.stderr[-600:])
        for word in ("basename", "corename", "openblas", "candidate_suprema",
                     "hermite"):
            self.assertNotIn(word, out.stderr.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
