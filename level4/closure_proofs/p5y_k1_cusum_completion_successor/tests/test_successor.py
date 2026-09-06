"""PHASE 10: focused tests for the CUSUM completion successor.

Mandatory coverage: producer identity, certificate determinism, chain/resume,
and the science regression (cell 325, drift-aware norms, inherited far field,
frozen invariants).
"""
from __future__ import annotations

import os

# `successor_qualify` pins the BLAS/FLINT thread environment and re-execs itself
# if it was not already pinned, so that the float candidate solve is
# deterministic. A test process must therefore ADOPT that contract before
# importing it -- the vars below are read by OpenBLAS when numpy first loads, so
# they must be set before any import that pulls numpy in. Without this the
# re-exec fires mid-suite with `sys.argv[0] = "python -m unittest"`, which is not
# a file, and the whole process dies.
for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["K1_THREADS_PINNED"] = "1"

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import ancestry                                                 # noqa: E402

from flint import arb                                           # noqa: E402

from math import comb                                           # noqa: E402

import opnorms as reviewed_norms                                # noqa: E402
import producer as repair2_producer                             # noqa: E402
import sharp_norms                                              # noqa: E402
import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402
from intervals import exact, mag_fraction, workprec             # noqa: E402

import determinism                                              # noqa: E402
import far_field_inherited                                      # noqa: E402
import order2                                                   # noqa: E402
import refine2                                                  # noqa: E402
import successor_certhash as CH                                 # noqa: E402
import successor_producer as SP                                 # noqa: E402
import successor_universe as SU                                 # noqa: E402

CELLS = [c for c in spec.CELLS if c["detector"] == "CUSUM"]
RECORDS = sorted((NS / "diagnostics/cells").glob("succ_CUSUM_*.json"))
BLOCK = tuple(range(318, 325))



class _StubCert:
    """Minimal certifier surface for exercising refine2 without a full cell."""

    def __init__(self, cell, *, sup=1, deltaH=F(1, 1000)):
        self.left, self.right = F(cell["left"][0]), F(cell["right"][0])
        self.rho, self.C = cell["rho"][0], cell["C_upper"]
        self.norms = sharp_norms.table(self.left, self.right)
        self.sup = {}
        for r in range(5):
            for kind in ("F", "D", "H"):
                self.sup[kind, r, 0] = exact(F(sup))
        self.residuals = {f"H_{r}": {"delta_cell": exact(deltaH)} for r in range(5)}


class _StubDAG:
    def __init__(self, cert, num, den):
        self.value = exact(F(num, den))

    def get(self, node):
        return self.value


def load(paths):
    return [json.loads(p.read_text()) for p in paths]


def _certs_for(rec):
    import successor_qualify as SQ
    ctx = SU.context(precision_bits=rec["precision_bits"])
    return SQ.build_certificates(rec, ctx), ctx


# =========================================================== producer identity
class ProducerIdentity(unittest.TestCase):
    def test_deterministic_and_canonically_ordered(self):
        a, b = SP.producer_manifest(), SP.producer_manifest()
        self.assertEqual(a, b)
        self.assertEqual(list(a["files"]), sorted(a["files"]))

    def test_no_timestamps_pids_or_wallclock(self):
        blob = json.dumps(SP.producer_manifest())
        for noise in ("timestamp", "generated", "mtime", "pid", "/tmp/", "utc"):
            self.assertNotIn(noise, blob.lower())

    def test_modifying_a_successor_module_changes_the_hash(self):
        base = SP.producer_manifest()
        for name in SP.SUCCESSOR_MODULES:
            rel = str((NS / "code" / name).relative_to(ancestry.ROOT))
            self.assertIn(rel, base["files"], name)
            m = copy.deepcopy(base); m["files"][rel] = "0" * 64
            self.assertNotEqual(SP.producer_hash(m), SP.producer_hash(base), name)

    def test_modifying_any_inherited_executed_module_changes_the_hash(self):
        base = SP.producer_manifest()
        inherited = (
            [ancestry.FINAL_NS / "code" / n for n in SP.FINAL_MODULES]
            + [ancestry.REPAIR2_NS / "code" / n for n in SP.REPAIR2_MODULES]
            + [ancestry.REPAIR1_NS / "code" / n for n in SP.REPAIR1_MODULES]
            + [ancestry.IMPL_NS / "code" / n for n in SP.REVIEWED_MODULES]
            + [ancestry.SPEC_NS / n for n in SP.FROZEN_INPUTS]
            + list(SP.BACKEND_INPUTS))
        for p in inherited:
            rel = str(p.relative_to(ancestry.ROOT))
            self.assertIn(rel, base["files"], rel)
            m = copy.deepcopy(base); m["files"][rel] = "0" * 64
            self.assertNotEqual(SP.producer_hash(m), SP.producer_hash(base), rel)

    def test_version_and_threading_pins_are_bound(self):
        gp = SP.producer_manifest()["generation_parameters"]
        for key in ("python_flint_version", "numpy_version", "blas_threads",
                    "flint_threads"):
            self.assertIn(key, gp)
        base = SP.producer_manifest()
        m = copy.deepcopy(base); m["generation_parameters"]["blas_threads"] = 8
        self.assertNotEqual(SP.producer_hash(m), SP.producer_hash(base))

    def test_documentation_is_out_of_scope(self):
        files = SP.producer_manifest()["files"]
        for rel in files:
            self.assertNotIn("/diagnostics/", rel)
            self.assertNotIn("/tests/", rel)
            self.assertNotIn("/manifests/", rel)
        self.assertNotIn(str((NS / "README.md").relative_to(ancestry.ROOT)), files)

    def test_lineage_only_repair2_hash_is_rejected(self):
        self.assertNotEqual(SP.producer_hash(), repair2_producer.producer_hash())
        self.assertIn(repair2_producer.producer_hash(),
                      SP.rejected_producer_hashes().values())

    def test_producer_hash_is_not_a_commit_id(self):
        for c in (ancestry.FINAL_COMMIT, ancestry.REPAIR2_COMMIT,
                  ancestry.REPAIR1_COMMIT, ancestry.REVIEWED_COMMIT):
            self.assertNotEqual(SP.producer_hash(), c)

    def test_loaded_module_coverage_audit_runs_isolated(self):
        """Isolated process: no cross-suite sys.modules contamination.

        Run from a script file, not `python -c`: `successor_qualify` re-execs
        itself to pin BLAS before numpy loads, and a `-c` process has no argv
        that can be re-executed faithfully (it fails loudly, exit 2).
        """
        code = (f"import sys; sys.path.insert(0, {str(NS / 'code')!r})\n"
                "import successor_qualify as SQ, successor_producer as SP\n"
                "r = SP.verify_loaded_modules_covered(strict=False)\n"
                "print(r['ok'], r['uncovered_loaded_modules'])\n")
        with tempfile.TemporaryDirectory() as d:
            script = Path(d) / "probe.py"
            script.write_text(code)
            out = subprocess.run([sys.executable, str(script)], cwd=ancestry.ROOT,
                                 capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stderr[-2000:])
        self.assertTrue(out.stdout.startswith("True"), out.stdout)


# ================================================== certificate determinism
class CertificateDeterminism(unittest.TestCase):
    def test_field_classification_is_complete(self):
        c = determinism.classify_fields()
        for f in CH.EXCLUDED_RUNTIME_FIELDS:
            self.assertIn(f, c["excluded_from_scientific_hash"])
        self.assertIn("float_candidate_coefficients", c["classes"])
        self.assertEqual(c["classes"]["float_candidate_coefficients"],
                         determinism.IMPLEMENTATION_DEFECT)

    def test_runtime_noise_does_not_change_the_scientific_hash(self):
        if not RECORDS:
            self.skipTest("no records")
        rec = json.loads(RECORDS[0].read_text())
        before = CH.record_scientific_hash(rec)
        noisy = copy.deepcopy(rec)
        noisy["cpu_seconds_including_dependencies"] = 99999.0
        noisy["wall_seconds"] = 1.0
        noisy["peak_rss_kib"] = 1
        noisy["threading"] = {"blas_threads": "8"}
        for o in noisy["objects"].values():
            o["cpu_seconds"] = 0.0
            o["bernstein_calls"] = 999
        self.assertEqual(before, CH.record_scientific_hash(noisy))

    def test_benign_json_reordering_does_not_change_the_hash(self):
        if not RECORDS:
            self.skipTest("no records")
        rec = json.loads(RECORDS[0].read_text())
        shuffled = json.loads(json.dumps(
            {k: rec[k] for k in reversed(list(rec))}))
        self.assertEqual(CH.record_scientific_hash(rec),
                         CH.record_scientific_hash(shuffled))

    def test_certified_interval_change_changes_the_hash(self):
        if not RECORDS:
            self.skipTest("no records")
        rec = json.loads(RECORDS[0].read_text())
        before = CH.record_scientific_hash(rec)
        changed = copy.deepcopy(rec)
        changed["m"]["5"]["M_R2"] = "123456789/1"
        self.assertNotEqual(before, CH.record_scientific_hash(changed))

    def test_scientific_bound_change_changes_the_hash(self):
        if not RECORDS:
            self.skipTest("no records")
        rec = json.loads(RECORDS[0].read_text())
        before = CH.record_scientific_hash(rec)
        changed = copy.deepcopy(rec)
        k = sorted(changed["objects"])[0]
        changed["objects"][k]["delta_cell"] = "1/2"
        self.assertNotEqual(before, CH.record_scientific_hash(changed))

    def test_stored_scientific_hash_matches_recomputation(self):
        for rec in load(RECORDS):
            self.assertEqual(rec["scientific_content_hash"],
                             CH.record_scientific_hash(rec))


    def test_repeated_fresh_runs_reproduce_the_scientific_hash(self):
        """The adjudicated predecessor defect: repeats must be bit-identical."""
        path = NS / "diagnostics" / "determinism.json"
        if not path.exists():
            self.skipTest("no repeat runs recorded")
        rep = json.loads(path.read_text())
        self.assertTrue(rep["cells"], "determinism record is empty")
        for cell, v in rep["cells"].items():
            self.assertTrue(v["producer_identical"], cell)
            self.assertEqual(v["recorded_scientific_hash"],
                             v["repeat_scientific_hash"], cell)
            # a repeat that is byte-identical everywhere proves nothing
            self.assertTrue(v["runtime_fields_differed"], cell)
        self.assertTrue(rep["all_identical"])

    def test_threading_contract_is_pinned_before_numpy(self):
        for rec in load(RECORDS):
            self.assertTrue(rec["threading"]["pinned_before_numpy_import"])
            self.assertEqual(rec["threading"]["blas_threads"], "1")
            self.assertEqual(rec["threading"]["flint_threads"], 1)


# ========================================================= chain and resume
class ChainAndResume(unittest.TestCase):
    def setUp(self):
        if not RECORDS:
            self.skipTest("no records")
        self.rec = json.loads(RECORDS[0].read_text())
        self.certs, self.ctx = _certs_for(self.rec)
        self.cell = self.rec["cell_index"]
        self.unit = ("CUSUM", self.cell, "object", "dF_2")
        self.uid = SU.unit_id(self.unit)

    def test_valid_record_admitted(self):
        ident = self.certs[self.uid]["identity"]
        self.assertTrue(SU.admit_resume_record(
            ident, self.unit, dependency_certificates=self.certs, **self.ctx))

    def test_repair2_producer_identity_rejected(self):
        ident = copy.deepcopy(self.certs[self.uid]["identity"])
        ident["implementation_hash"] = repair2_producer.producer_hash()
        with self.assertRaises(SU.ProvenanceRejected):
            SU.admit_resume_record(ident, self.unit,
                                   dependency_certificates=self.certs, **self.ctx)

    def test_stale_successor_producer_rejected(self):
        ident = copy.deepcopy(self.certs[self.uid]["identity"])
        ident["implementation_hash"] = "9" * 64
        with self.assertRaises(SU.ResumeRejected):
            SU.admit_resume_record(ident, self.unit,
                                   dependency_certificates=self.certs, **self.ctx)

    def test_wrong_identity_kind_rejected(self):
        ident = copy.deepcopy(self.certs[self.uid]["identity"])
        ident["implementation_hash_kind"] = "repair2_producer_manifest_v1"
        with self.assertRaises(SU.ProvenanceRejected):
            SU.admit_resume_record(ident, self.unit,
                                   dependency_certificates=self.certs, **self.ctx)

    def test_cross_cell_and_cross_m_rejected(self):
        ident = self.certs[self.uid]["identity"]
        other_cell = ("CUSUM", 325 if self.cell != 325 else 320, "object", "dF_2")
        with self.assertRaises(SU.ResumeRejected):
            SU.admit_resume_record(ident, other_cell,
                                   dependency_certificates=self.certs, **self.ctx)
        a5 = self.certs[SU.unit_id(("CUSUM", self.cell, "assembly", "5"))]["identity"]
        with self.assertRaises(SU.ResumeRejected):
            SU.admit_resume_record(a5, ("CUSUM", self.cell, "assembly", "3"),
                                   dependency_certificates=self.certs, **self.ctx)

    def test_modified_dependency_certificate_rejected(self):
        certs = dict(self.certs)
        dep = f"CUSUM|{self.cell}|object|F_2"
        tampered = copy.deepcopy(certs[dep])
        tampered["certified"]["residual"]["delta_mid"] = "1/2"
        certs[dep] = tampered
        with self.assertRaises(SU.ProvenanceRejected):
            SU.admit_resume_record(self.certs[self.uid]["identity"], self.unit,
                                   dependency_certificates=certs, **self.ctx)

    def test_missing_and_extra_dependency_rejected(self):
        certs = {k: v for k, v in self.certs.items()
                 if k != f"CUSUM|{self.cell}|object|F_2"}
        with self.assertRaises(SU.ProvenanceRejected):
            SU.admit_resume_record(self.certs[self.uid]["identity"], self.unit,
                                   dependency_certificates=certs, **self.ctx)
        ident = copy.deepcopy(self.certs[self.uid]["identity"])
        ident["source_certificate_hashes"][f"CUSUM|{self.cell}|object|h_4"] = "0" * 64
        with self.assertRaises(SU.ProvenanceRejected):
            SU.admit_resume_record(ident, self.unit,
                                   dependency_certificates=self.certs, **self.ctx)

    def test_forged_metadata_only_certificate_rejected(self):
        ident = copy.deepcopy(self.certs[self.uid]["identity"])
        ident["detector"] = "SR"
        ident.pop("unit_hash")
        ident["unit_hash"] = hashlib.sha256(SU.canonical(ident)).hexdigest()
        with self.assertRaises(SU.ResumeRejected):
            SU.admit_resume_record(ident, self.unit,
                                   dependency_certificates=self.certs, **self.ctx)

    def test_leaf_empty_map_and_non_leaf_non_empty(self):
        leaves = set(self.rec["provenance_chain"]["leaf_units"])
        self.assertTrue(leaves)
        for uid, cert in self.certs.items():
            m = cert["identity"]["source_certificate_hashes"]
            if uid in leaves:
                self.assertEqual(m, {}, uid)
            else:
                self.assertTrue(m, uid)

    def test_recorded_chain_verifies(self):
        for rec in load(RECORDS):
            self.assertTrue(rec["provenance_chain"]["all_verified"])
            self.assertEqual(rec["provenance_chain"]["obligations"], 28)


# ======================================================= science regression
class ScienceRegression(unittest.TestCase):
    def test_cell_325_still_passes_every_m(self):
        rec = next((r for r in load(RECORDS) if r["cell_index"] == 325), None)
        self.assertIsNotNone(rec, "cell 325 regression control is required")
        for m, L in rec["m"].items():
            self.assertEqual(L["status"], "PASS", m)
            self.assertLess(L["cover"]["utilization"], 1.0, m)

    def test_drift_aware_norms_still_only_tighten(self):
        with workprec(256):
            for c in CELLS[::37] + CELLS[-8:]:
                left, right = F(c["left"][0]), F(c["right"][0])
                e_max = exact(max(abs(left), abs(right)))
                for i in range(4):
                    self.assertLessEqual(
                        sharp_norms.kernel_norm(i, left, right).upper(),
                        reviewed_norms.kernel_norm(i).upper())
                    self.assertLessEqual(
                        sharp_norms.raw_kernel_norm(i, left, right).upper(),
                        reviewed_norms.raw_kernel_norm(i, e_max).upper())

    def test_order2_tightening_only_tightens(self):
        for rec in load(RECORDS):
            for name, t in rec["tightening_report"].items():
                self.assertLessEqual(t["tightened"], t["predecessor"], name)

    def test_closed_form_supremum_never_exceeds_the_whole_line_bound(self):
        with workprec(256):
            for c in (CELLS[0], CELLS[200], CELLS[321], CELLS[325]):
                for n in range(4):
                    sharp = order2.sup_source_derivative_on(
                        n, F(c["left"][0]), F(c["right"][0]))
                    self.assertLessEqual(
                        sharp.upper(),
                        reviewed_norms.sup_source_derivative(n).upper())

    def test_every_failure_is_certificate_looseness(self):
        for rec in load(RECORDS):
            for m, L in rec["m"].items():
                if L["status"] != "FAIL":
                    continue
                self.assertLess(F(L["R2_interval"]["lo"]), 0, (rec["cell_index"], m))
                self.assertGreater(F(L["R2_interval"]["hi"]), 0, (rec["cell_index"], m))

    def test_s0_charged_exactly_once(self):
        for rec in load(RECORDS):
            self.assertTrue(rec["s0_charge_audit"]["all_charged_exactly_once"])

    def test_far_field_pass_inherited_not_re_derived(self):
        r = far_field_inherited.report()
        self.assertEqual(r["inherited"]["CUSUM_FAR_FIELD"], "PASS")
        self.assertEqual(r["inherited"]["SR_FAR_FIELD"], "PASS")
        self.assertFalse(r["inherited"]["re_derived_here"])
        self.assertFalse(r["inherited"]["far_field_logic_changed_here"])
        self.assertIsNone(r["inherited"]["uncovered_interval_between_c_D_and_e_far"])
        self.assertIn("SUPERSEDED", r["superseded_predecessor_reading"]["status"])


# ============================================== second-order whole-cell refinement
class SecondOrderRefinement(unittest.TestCase):
    def setUp(self):
        if not RECORDS:
            self.skipTest("no records")

    def test_substitution_is_recorded_in_every_record(self):
        for rec in load(RECORDS):
            sub = rec["whole_cell_refinement_module"]
            self.assertEqual(sub["module"], "refine2")
            self.assertEqual(sub["tightening"], refine2.TIGHTENING)
            self.assertIn("second_order_taylor_in_e_whole_cell_D_and_F",
                          rec["changes"])

    def test_install_routes_propagate_through_refine2(self):
        import propagate
        self.assertEqual(refine2.install(), refine2.TIGHTENING)
        self.assertIs(propagate.refine, refine2)
        # and the certifying runner must actually call it, before any cell runs
        src = (NS / "code" / "successor_qualify.py").read_text()
        self.assertIn("refine2.install()", src)
        self.assertLess(src.index("refine2.install()"),
                        src.index("propagate.cell_obligations"))

    def test_refinement_never_loosens_any_r(self):
        for rec in load(RECORDS):
            for r, a in rec["whole_cell_refinement"].items():
                so = a["second_order"]
                for key in ("epsF_cell", "epsD_cell", "epsH_cell"):
                    self.assertLessEqual(F(so["refined"][key]),
                                         F(so["predecessor"][key]),
                                         (rec["cell_index"], r, key))
                for key in ("epsF_cell", "epsD_cell", "epsH_cell"):
                    self.assertLessEqual(F(so["refined"][key]),
                                         F(a["crude"][key]),
                                         (rec["cell_index"], r, key))

    def test_regression_guard_fires_when_min_is_defeated(self):
        """Negative control: without the min, a looser bound must be refused."""
        rec = json.loads(RECORDS[0].read_text())
        cell = next(c for c in CELLS if c["index"] == rec["cell_index"])
        original = refine2._min
        try:
            refine2._min = lambda a, b: b          # always take the new value
            with workprec(256):
                cert = _StubCert(cell)
                with self.assertRaises(refine2.RefinementRegression):
                    refine2.refine(cert, _StubDAG(cert, 1, 500000),
                                   _StubDAG(cert, 1, 1000000000), rs=(0,))
        finally:
            refine2._min = original

    def test_h_tower_matches_the_frozen_recursion(self):
        cell = next(c for c in CELLS if c["index"] == 321)
        with workprec(256):
            cert = _StubCert(cell)
            T = refine2.h_tower(cert)
            k_ = cert.norms["k"]
            for j in range(2, 5):
                for k in range(4):
                    expect = sum(F(mag_fraction(arb(comb(k, i)) * k_[i] * T[j - 1, k - i]))
                                 for i in range(k + 1))
                    self.assertLessEqual(F(mag_fraction(T[j, k])) - expect,
                                         F(1, 2 ** 40), (j, k))
            # leaves are the exact closed forms, never worse than whole-line
            for k in range(3):
                self.assertLessEqual(
                    T[1, k + 1].upper(),
                    reviewed_norms.sup_source_derivative(k).upper())

    def test_third_derivative_source_bound_is_finite_and_ordered(self):
        cell = next(c for c in CELLS if c["index"] == 321)
        with workprec(256):
            cert = _StubCert(cell)
            T = refine2.h_tower(cert)
            prev = None
            for r in range(5):
                v = F(mag_fraction(refine2.sup_source_third_derivative(cert, r, T)))
                self.assertGreater(v, 0)
                if prev is not None and r > 1:
                    self.assertGreater(v, prev)      # deeper source, larger bound
                prev = v

# =============================================================== governance
class Governance(unittest.TestCase):
    def test_frozen_invariants_unchanged(self):
        self.assertEqual(spec.HARD_CAP_CPU_H, 1126)
        self.assertEqual(spec.PRODUCTION_BITS, 256)
        self.assertFalse(spec.PRODUCTION_ENABLED)
        self.assertFalse(spec.PRECISION_ESCALATION_ALLOWED)
        self.assertFalse(spec.DEGREE_ADAPTATION_ALLOWED)
        self.assertEqual(sum(spec.TOP_BUDGETS.values()), F(19, 100))
        self.assertEqual(len(reviewed.work_ids()), 17978)
        self.assertEqual(spec.verify_frozen_spec(), spec.FROZEN_HASHES)

    def test_cover_geometry_unchanged(self):
        self.assertEqual(spec.CELLS_SHA256,
                         spec.CHECKPOINT["geometry"]["cells_sha256"])
        self.assertEqual(spec.COUNTS, {"CUSUM": 326, "SR": 316})
        for rec in load(RECORDS):
            c = next(x for x in CELLS if x["index"] == rec["cell_index"])
            self.assertEqual(rec["rho"], c["rho"])
            self.assertEqual(rec["e0"], c["e0"])

    def test_predecessor_namespaces_byte_preserved(self):
        for ns, commit in ((ancestry.IMPL_NS, ancestry.REVIEWED_COMMIT),
                           (ancestry.REPAIR1_NS, ancestry.REPAIR1_COMMIT),
                           (ancestry.REPAIR2_NS, ancestry.REPAIR2_COMMIT),
                           (ancestry.FINAL_NS, ancestry.FINAL_COMMIT)):
            rel = str(ns.relative_to(ancestry.ROOT))
            out = subprocess.run(["git", "diff", "--name-only", commit, "--", rel],
                                 cwd=ancestry.ROOT, capture_output=True, text=True)
            self.assertEqual([x for x in out.stdout.split("\n") if x.strip()], [],
                             rel)

    def test_writes_only_inside_this_namespace(self):
        changed = subprocess.check_output(
            ["git", "status", "--porcelain"], cwd=ancestry.ROOT).decode().splitlines()
        rel = str(NS.relative_to(ancestry.ROOT))
        self.assertEqual([l for l in changed if rel not in l], [])

    def test_sr_untouched(self):
        self.assertEqual([p.name for p in (NS / "code").glob("sr_*.py")], [])
        for rec in load(RECORDS):
            self.assertEqual(rec["detector"], "CUSUM")

    def test_production_off(self):
        self.assertFalse(spec.PRODUCTION_ENABLED)
        for folder in ("results", "certificates", "production_logs"):
            self.assertFalse((NS / folder).exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
