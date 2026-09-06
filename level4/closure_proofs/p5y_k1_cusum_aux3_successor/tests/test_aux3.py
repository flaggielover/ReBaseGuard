"""PHASE 13: provenance, determinism, governance and science tests.

The threading contract is adopted here BEFORE any import that pulls numpy in:
`aux_qualify` refuses to certify in a process where numpy loaded unpinned, so a
harness that imports it must pin first. This is the contract, stated at the top
of the file rather than discovered at run time.
"""
from __future__ import annotations

import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS"):
    os.environ[_var] = "1"
os.environ["K1_THREADS_PINNED"] = "1"

import copy                                                     # noqa: E402
import hashlib                                                  # noqa: E402
import json                                                     # noqa: E402
import re                                                       # noqa: E402
import subprocess                                               # noqa: E402
import sys                                                      # noqa: E402
import tempfile                                                 # noqa: E402
import unittest                                                 # noqa: E402
from fractions import Fraction as F                             # noqa: E402
from math import comb                                           # noqa: E402
from pathlib import Path                                        # noqa: E402

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import ancestry                                                 # noqa: E402

from flint import arb                                           # noqa: E402

import opnorms as reviewed_norms                                # noqa: E402
import propagate as reviewed_propagate                          # noqa: E402
import sharp_norms                                              # noqa: E402
import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402
from intervals import exact, mag_fraction, workprec             # noqa: E402

import aux_certhash as CH                                       # noqa: E402
import aux_certifier                                            # noqa: E402
import aux_propagate                                            # noqa: E402
import aux_refine                                               # noqa: E402
import aux_universe as SU                                       # noqa: E402
import far_field_inherited                                      # noqa: E402
import manifest                                                 # noqa: E402
import no_monkeypatch                                           # noqa: E402
import refine2                                                  # noqa: E402

CELLS = [c for c in spec.CELLS if c["detector"] == "CUSUM"]
RECORDS = sorted((NS / "diagnostics/cells").glob("aux3_CUSUM_*.json"))
BLOCK = tuple(range(318, 325))
CONTROL = 325
FAILED_BEFORE = ((319, "5"), (320, "5"), (321, "5"), (322, "5"), (323, "5"))


def load(paths):
    return [json.loads(p.read_text()) for p in paths]


def _run(source: str, expect_fail: bool = False) -> dict:
    """Run a probe in a fresh process; return its last stdout line as JSON."""
    with tempfile.TemporaryDirectory() as d:
        script = Path(d) / "probe.py"
        script.write_text(source)
        out = subprocess.run([sys.executable, str(script)], cwd=ancestry.ROOT,
                             capture_output=True, text=True,
                             env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if expect_fail:
        return {"returncode": out.returncode, "stderr": out.stderr,
                "stdout": out.stdout}
    if out.returncode != 0:
        raise AssertionError(f"probe failed: {out.stderr[-1500:]}")
    return json.loads(out.stdout.strip().splitlines()[-1])


PREAMBLE = (
    "import os, sys, json\n"
    "for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',"
    "'NUMEXPR_NUM_THREADS'):\n    os.environ[v] = '1'\n"
    "os.environ['K1_THREADS_PINNED'] = '1'\n"
    f"sys.path.insert(0, {str(NS / 'code')!r})\n")


# ================================================================ no patching
class NoMonkeyPatching(unittest.TestCase):
    def test_namespace_is_statically_clean(self):
        report = no_monkeypatch.scan_namespace()
        self.assertTrue(report["clean"], report["findings"])

    def test_detector_actually_detects(self):
        """A detector that never fires proves nothing."""
        bad = ("import propagate\n"
               "import sys\n"
               "propagate.refine = sys.modules[__name__]\n"
               "setattr(propagate, 'x', 1)\n"
               "sys.modules['propagate'] = None\n")
        found = {f["pattern"] for f in no_monkeypatch.scan_source(bad, "<probe>")}
        self.assertEqual(found, {"module_attribute_assignment",
                                 "setattr_on_module", "sys_modules_assignment"})

    def test_reviewed_module_is_not_redirected_at_runtime(self):
        import refine as reviewed_refine
        self.assertIs(reviewed_propagate.refine, reviewed_refine,
                      "the reviewed propagate must still call the reviewed refine")

    def test_refinements_are_passed_not_patched(self):
        src = (NS / "code" / "aux_qualify.py").read_text()
        self.assertIn("whole_cell_refinement=refine2.refine", src)
        self.assertIn("node_refinement_factory=make_backend", src)
        sig = (NS / "code" / "aux_propagate.py").read_text()
        self.assertIn("def cell_obligations(cert, *, whole_cell_refinement,", sig)


# ================================================================== manifest
class ImmutableProducerManifest(unittest.TestCase):
    def test_artifact_is_committed_and_verifies(self):
        self.assertTrue(manifest.ARTIFACT.exists())
        state = manifest.verify()
        self.assertTrue(state["ok"], state["problems"])

    def test_hash_recomputes_from_the_committed_bytes_alone(self):
        committed = json.loads(manifest.ARTIFACT.read_text())
        recomputed = hashlib.sha256(manifest.canonical(committed)).hexdigest()
        self.assertEqual(recomputed, manifest.manifest_hash(committed))
        for rel, sha in committed["files"].items():
            self.assertEqual(manifest.sha256_file(ancestry.ROOT / rel), sha, rel)

    def test_manifest_is_current_with_the_working_tree(self):
        self.assertEqual(manifest.build(), json.loads(manifest.ARTIFACT.read_text()),
                         "run `python code/manifest.py --write` and commit")

    def test_modifying_any_certifying_byte_fails_verification(self):
        committed = json.loads(manifest.ARTIFACT.read_text())
        for rel in list(committed["files"])[:6] + list(committed["files"])[-6:]:
            probe = PREAMBLE + (
                "import json, manifest\n"
                "m = json.loads(manifest.ARTIFACT.read_text())\n"
                f"m['files'][{rel!r}] = '0'*64\n"
                "orig = manifest.load\n"
                "manifest.load = lambda: m\n"
                "state = manifest.verify()\n"
                "print(json.dumps({'ok': state['ok'], "
                "'problems': state['problems'][:2]}))\n")
            out = _run(probe)
            self.assertFalse(out["ok"], rel)
            self.assertTrue(any("content changed" in p for p in out["problems"]))

    def test_runtime_version_mismatch_fails_verification(self):
        for key, bogus in (("numpy_version", "0.0.0"),
                           ("python_flint_version", "0.0.0"),
                           ("python_major_minor", "1.0"),
                           ("precision_bits", 128)):
            probe = PREAMBLE + (
                "import json, manifest\n"
                "m = json.loads(manifest.ARTIFACT.read_text())\n"
                f"m['runtime'][{key!r}] = {bogus!r}\n"
                "manifest.load = lambda: m\n"
                "state = manifest.verify()\n"
                "print(json.dumps({'ok': state['ok'], "
                "'problems': state['problems'][:2]}))\n")
            out = _run(probe)
            self.assertFalse(out["ok"], key)
            self.assertTrue(any(key in p for p in out["problems"]), out["problems"])

    def test_missing_artifact_aborts(self):
        probe = PREAMBLE + (
            "import manifest, json\n"
            "manifest.ARTIFACT = manifest.ARTIFACT.with_name('absent.json')\n"
            "try:\n"
            "    manifest.require()\n"
            "    print(json.dumps({'raised': False}))\n"
            "except manifest.ManifestFailure as e:\n"
            "    print(json.dumps({'raised': True, 'msg': str(e)[:120]}))\n")
        out = _run(probe)
        self.assertTrue(out["raised"])
        self.assertIn("missing", out["msg"])

    def test_documentation_and_reporting_are_out_of_scope(self):
        files = json.loads(manifest.ARTIFACT.read_text())["files"]
        for rel in files:
            self.assertNotIn("/tests/", "/" + rel)
            self.assertNotIn("/diagnostics/", "/" + rel)
            self.assertNotIn("/manifests/", "/" + rel)
            self.assertNotIn("/evidence/", "/" + rel)
        for name in manifest.AUX3_NON_CERTIFYING:
            self.assertNotIn(
                str((NS / "code" / name).relative_to(ancestry.ROOT)), files)

    def test_every_certifying_module_of_this_namespace_is_listed(self):
        files = json.loads(manifest.ARTIFACT.read_text())["files"]
        for name in manifest.AUX3_MODULES:
            self.assertIn(str((NS / "code" / name).relative_to(ancestry.ROOT)),
                          files, name)

    def test_producer_identity_is_not_a_commit_or_a_lineage_hash(self):
        ident = manifest.identity()["producer_manifest_hash"]
        for name, value in SU.rejected_producer_identities().items():
            self.assertNotEqual(ident, value, name)


# ======================================================== strict coverage
class StrictLoadedModuleCoverage(unittest.TestCase):
    def test_coverage_is_clean_in_a_real_certifying_process(self):
        probe = PREAMBLE + (
            "import aux_qualify, manifest\n"
            "r = manifest.loaded_module_coverage()\n"
            "print(json.dumps(r))\n")
        out = _run(probe)
        self.assertTrue(out["ok"], out["uncovered_loaded_modules"])

    def test_an_uncovered_certifying_module_aborts_certification(self):
        """Dynamically introduce an uncovered certifying module; require abort."""
        with tempfile.TemporaryDirectory() as d:
            intruder = NS / "code" / "_probe_uncovered_module.py"
            intruder.write_text("VALUE = 1\n")
            try:
                probe = PREAMBLE + (
                    "import aux_qualify, manifest\n"
                    "import _probe_uncovered_module\n"
                    "try:\n"
                    "    aux_qualify.manifest.require()\n"
                    "    print(json.dumps({'aborted': False}))\n"
                    "except manifest.ManifestFailure as e:\n"
                    "    print(json.dumps({'aborted': True, 'msg': str(e)[:160]}))\n")
                out = _run(probe)
            finally:
                intruder.unlink()
        self.assertTrue(out["aborted"], "an uncovered module must abort the run")
        self.assertIn("_probe_uncovered_module", out["msg"])

    def test_certification_refuses_without_the_threading_contract(self):
        probe = (
            "import os, sys, json\n"
            "for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',"
            "'NUMEXPR_NUM_THREADS'):\n    os.environ.pop(v, None)\n"
            "os.environ.pop('K1_THREADS_PINNED', None)\n"
            "import numpy\n"                     # numpy first, unpinned
            f"sys.path.insert(0, {str(NS / 'code')!r})\n"
            "import aux_qualify\n"
            "try:\n"
            "    aux_qualify.run_cell(325)\n"
            "    print(json.dumps({'refused': False}))\n"
            "except aux_qualify.ThreadingContractViolated:\n"
            "    print(json.dumps({'refused': True}))\n")
        out = _run(probe)
        self.assertTrue(out["refused"])

    def test_the_gate_runs_before_anything_is_emitted(self):
        src = (NS / "code" / "aux_qualify.py").read_text()
        body = src.split("def run_cell")[1]
        self.assertLess(body.index("manifest.require()"),
                        body.index("Aux3Certifier"))


# =============================================== equivalence and injection
class InjectionEquivalence(unittest.TestCase):
    def test_recorded_dag_matches_the_reviewed_topology(self):
        """With no node refinement the aux DAG must equal the reviewed one."""
        if not RECORDS:
            self.skipTest("no records")
        rec = json.loads(RECORDS[0].read_text())
        self.assertEqual(rec["dag_audit_mid"]["edges"],
                         rec["dag_audit_cell"]["edges"])
        self.assertEqual(rec["dag_audit_cell"]["duplicate_edges"], 0)
        self.assertTrue(rec["dag_audit_cell"]["derivative_edges_all_cover"])

    def test_midpoint_dag_is_untouched_by_the_node_bound(self):
        """The node bound is a whole-cell device; midpoints must not move."""
        for rec in load(RECORDS):
            for node, value in rec["eps_mid"].items():
                self.assertGreater(F(value), 0, node)
            for node, dec in rec["node_refinement"]["decisions"].items():
                self.assertIn(node, rec["eps_cell"])

    def test_node_bound_never_loosens(self):
        for rec in load(RECORDS):
            for node, dec in rec["node_refinement"]["decisions"].items():
                if dec["kept"] == "cascade" and "cascade" not in dec:
                    continue
                if "cascade" in dec:
                    self.assertLessEqual(min(F(dec["cascade"]), F(dec["taylor"])),
                                         F(dec["cascade"]), node)


# ============================================================= determinism
class Determinism(unittest.TestCase):
    def test_stored_scientific_hash_recomputes(self):
        for rec in load(RECORDS):
            self.assertEqual(rec["scientific_content_hash"],
                             CH.record_scientific_hash(rec))

    def test_runtime_noise_does_not_change_the_hash(self):
        if not RECORDS:
            self.skipTest("no records")
        rec = json.loads(RECORDS[0].read_text())
        before = CH.record_scientific_hash(rec)
        noisy = copy.deepcopy(rec)
        noisy["cpu_seconds_including_dependencies"] = 1.0
        noisy["cpu_seconds_auxiliary"] = 0.0
        noisy["wall_seconds"] = 1.0
        noisy["peak_rss_kib"] = 1
        noisy["threading"] = {"blas_threads": "8"}
        for o in noisy["objects"].values():
            o["cpu_seconds"] = 0.0
            o["bernstein_calls"] = 999
        for o in noisy["auxiliary_evidence"]["objects"].values():
            o["cpu_seconds"] = 0.0
            o["kernel_calls"] = 999
        self.assertEqual(before, CH.record_scientific_hash(noisy))

    def test_scientific_interval_change_changes_the_hash(self):
        if not RECORDS:
            self.skipTest("no records")
        rec = json.loads(RECORDS[0].read_text())
        before = CH.record_scientific_hash(rec)
        for mutate in (
                lambda r: r["m"]["5"].__setitem__("M_R2", "123/1"),
                lambda r: r["eps_cell_refined"].__setitem__("H:4", "1/2"),
                lambda r: r["objects"]["H_4"].__setitem__("delta_cell", "1/2"),
                lambda r: r["producer"].__setitem__(
                    "producer_manifest_hash", "0" * 64)):
            changed = copy.deepcopy(rec)
            mutate(changed)
            self.assertNotEqual(before, CH.record_scientific_hash(changed))

    def test_auxiliary_evidence_change_changes_the_hash(self):
        if not RECORDS:
            self.skipTest("no records")
        rec = json.loads(RECORDS[0].read_text())
        before = CH.record_scientific_hash(rec)
        changed = copy.deepcopy(rec)
        name = sorted(changed["auxiliary_evidence"]["objects"])[0]
        changed["auxiliary_evidence"]["objects"][name]["delta_mid"] = "7/8"
        self.assertNotEqual(before, CH.record_scientific_hash(changed))
        self.assertNotEqual(CH.auxiliary_evidence_hash(rec),
                            CH.auxiliary_evidence_hash(changed))

    def test_repeated_fresh_runs_reproduce_the_hash(self):
        path = NS / "diagnostics" / "determinism.json"
        if not path.exists():
            self.skipTest("no repeat runs recorded")
        rep = json.loads(path.read_text())
        self.assertTrue(rep["cells"])
        for cell, v in rep["cells"].items():
            self.assertTrue(v["producer_identical"], cell)
            self.assertEqual(v["recorded_scientific_hash"],
                             v["repeat_scientific_hash"], cell)
            self.assertTrue(v["runtime_fields_differed"], cell)
        self.assertTrue(rep["all_identical"])


# ============================================================== provenance
class ProvenanceChain(unittest.TestCase):
    def setUp(self):
        if not RECORDS:
            self.skipTest("no records")
        self.rec = json.loads(RECORDS[0].read_text())
        self.cell = self.rec["cell_index"]
        self.certs = {uid: {"identity": c["identity"], "status": c["status"],
                            "certified": None}
                      for uid, c in self.rec["certificates"].items()}
        self.ctx = SU.context(precision_bits=self.rec["precision_bits"])
        self.aux_hash = self.rec["auxiliary_evidence_hash"]

    def test_every_identity_carries_a_resolvable_manifest(self):
        for uid, cert in self.rec["certificates"].items():
            ident = cert["identity"]
            self.assertEqual(ident["producer_manifest_schema"], manifest.SCHEMA)
            self.assertEqual(ident["producer_manifest_path"],
                             str(manifest.ARTIFACT.relative_to(ancestry.ROOT)))
            self.assertEqual(ident["producer_manifest_hash"],
                             manifest.manifest_hash())
            self.assertEqual(ident["implementation_hash_kind"], SU.IDENTITY_KIND)
            self.assertEqual(ident["auxiliary_evidence_hash"], self.aux_hash)

    def test_recorded_chain_verifies_with_28_obligations(self):
        for rec in load(RECORDS):
            self.assertTrue(rec["provenance_chain"]["all_verified"])
            self.assertEqual(rec["provenance_chain"]["obligations"], 28)
            self.assertTrue(rec["provenance_chain"]["leaf_maps_empty"])
            self.assertTrue(rec["provenance_chain"]["auxiliary_evidence_bound"])

    def test_stale_producer_rejected(self):
        ident = copy.deepcopy(
            self.rec["certificates"][f"CUSUM|{self.cell}|object|dF_2"]["identity"])
        ident["producer_manifest_hash"] = "9" * 64
        with self.assertRaises(SU.ResumeRejected):
            SU.admit_resume_record(
                ident, ("CUSUM", self.cell, "object", "dF_2"),
                dependency_certificates=self.certs,
                auxiliary_evidence_hash=self.aux_hash, **self.ctx)

    def test_predecessor_lineage_identities_rejected(self):
        base = self.rec["certificates"][
            f"CUSUM|{self.cell}|object|dF_2"]["identity"]
        for name, value in SU.rejected_producer_identities().items():
            ident = copy.deepcopy(base)
            ident["producer_manifest_hash"] = value
            with self.assertRaises(SU.ProvenanceRejected, msg=name):
                SU.admit_resume_record(
                    ident, ("CUSUM", self.cell, "object", "dF_2"),
                    dependency_certificates=self.certs,
                    auxiliary_evidence_hash=self.aux_hash, **self.ctx)

    def test_auxiliary_evidence_tamper_rejected(self):
        ident = self.rec["certificates"][
            f"CUSUM|{self.cell}|object|dF_2"]["identity"]
        with self.assertRaises(SU.ProvenanceRejected):
            SU.admit_resume_record(
                ident, ("CUSUM", self.cell, "object", "dF_2"),
                dependency_certificates=self.certs,
                auxiliary_evidence_hash="0" * 64, **self.ctx)

    def test_wrong_identity_kind_rejected(self):
        ident = copy.deepcopy(self.rec["certificates"][
            f"CUSUM|{self.cell}|object|dF_2"]["identity"])
        ident["implementation_hash_kind"] = "repair2_producer_manifest_v1"
        with self.assertRaises(SU.ProvenanceRejected):
            SU.admit_resume_record(
                ident, ("CUSUM", self.cell, "object", "dF_2"),
                dependency_certificates=self.certs,
                auxiliary_evidence_hash=self.aux_hash, **self.ctx)

    def test_cross_cell_and_cross_m_rejected(self):
        ident = self.rec["certificates"][
            f"CUSUM|{self.cell}|object|dF_2"]["identity"]
        other = ("CUSUM", 325 if self.cell != 325 else 320, "object", "dF_2")
        with self.assertRaises(SU.ResumeRejected):
            SU.admit_resume_record(ident, other,
                                   dependency_certificates=self.certs,
                                   auxiliary_evidence_hash=self.aux_hash,
                                   **self.ctx)
        a5 = self.rec["certificates"][
            f"CUSUM|{self.cell}|assembly|5"]["identity"]
        with self.assertRaises(SU.ResumeRejected):
            SU.admit_resume_record(a5, ("CUSUM", self.cell, "assembly", "3"),
                                   dependency_certificates=self.certs,
                                   auxiliary_evidence_hash=self.aux_hash,
                                   **self.ctx)

    def test_missing_dependency_certificate_rejected(self):
        certs = {k: v for k, v in self.certs.items()
                 if k != f"CUSUM|{self.cell}|object|F_2"}
        ident = self.rec["certificates"][
            f"CUSUM|{self.cell}|object|dF_2"]["identity"]
        with self.assertRaises(SU.ProvenanceRejected):
            SU.admit_resume_record(ident, ("CUSUM", self.cell, "object", "dF_2"),
                                   dependency_certificates=certs,
                                   auxiliary_evidence_hash=self.aux_hash,
                                   **self.ctx)


# ============================================================== governance
class Governance(unittest.TestCase):
    def test_top_level_universe_unchanged(self):
        self.assertEqual(len(reviewed.work_ids()), 17978)
        self.assertEqual(spec.TOTAL_UNITS, 17978)
        state = SU.universe_unchanged()
        self.assertTrue(state["ok"])
        self.assertEqual(state["new_top_level_ids_added_here"], 0)
        for rec in load(RECORDS):
            self.assertEqual(rec["universe"]["total"], 17978)

    def test_auxiliary_evidence_creates_no_top_level_id(self):
        self.assertFalse(SU.AUXILIARY_OWNERSHIP["creates_top_level_work_ids"])
        self.assertFalse(SU.AUXILIARY_OWNERSHIP["creates_dag_nodes"])
        for rec in load(RECORDS):
            own = rec["auxiliary_evidence"]["ownership"]
            self.assertFalse(own["creates_top_level_work_ids"])
            self.assertEqual(own["obligation_universe_total"], 17978)
            # auxiliary objects are NOT frozen DAG nodes. An order-3 node would
            # be h:j:3, S:r:3, Sclosed:3 or W:r:j:3 -- note `D:3` is the frozen
            # derivative node for r = 3, not an order-3 node.
            order3 = re.compile(r"^(?:(?:h|S):\d+:3|Sclosed:3|W:\d+:\d+:3)$")
            for node in list(rec["eps_cell"]) + list(rec["eps_mid"]):
                self.assertIsNone(order3.match(node), node)
            self.assertTrue(any(n.startswith("D:") for n in rec["eps_cell"]))

    def test_extra_top_level_dependency_rejected(self):
        if not RECORDS:
            self.skipTest("no records")
        rec = json.loads(RECORDS[0].read_text())
        cell = rec["cell_index"]
        certs = {uid: {"identity": c["identity"], "status": c["status"]}
                 for uid, c in rec["certificates"].items()}
        ident = copy.deepcopy(certs[f"CUSUM|{cell}|object|dF_2"]["identity"])
        ident["source_certificate_hashes"][f"CUSUM|{cell}|object|h_4"] = "0" * 64
        with self.assertRaises(SU.ProvenanceRejected):
            SU.admit_resume_record(
                ident, ("CUSUM", cell, "object", "dF_2"),
                dependency_certificates=certs,
                auxiliary_evidence_hash=rec["auxiliary_evidence_hash"],
                **SU.context(precision_bits=rec["precision_bits"]))

    def test_frozen_invariants_unchanged(self):
        self.assertEqual(spec.HARD_CAP_CPU_H, 1126)
        self.assertEqual(spec.PRODUCTION_BITS, 256)
        self.assertFalse(spec.PRODUCTION_ENABLED)
        self.assertFalse(spec.PRECISION_ESCALATION_ALLOWED)
        self.assertFalse(spec.DEGREE_ADAPTATION_ALLOWED)
        self.assertEqual(sum(spec.TOP_BUDGETS.values()), F(19, 100))
        self.assertEqual(spec.M_VALUES, (1, 2, 3, 5))
        self.assertEqual(spec.COUNTS, {"CUSUM": 326, "SR": 316})
        self.assertEqual(spec.verify_frozen_spec(), spec.FROZEN_HASHES)
        self.assertEqual(spec.CELLS_SHA256,
                         spec.CHECKPOINT["geometry"]["cells_sha256"])

    def test_cover_geometry_unchanged(self):
        for rec in load(RECORDS):
            c = next(x for x in CELLS if x["index"] == rec["cell_index"])
            self.assertEqual(rec["rho"], c["rho"])
            self.assertEqual(rec["e0"], c["e0"])
            self.assertEqual(rec["C_upper"], c["C_upper"])

    def test_predecessor_namespaces_byte_preserved(self):
        for name, (ns, commit) in ancestry.PREDECESSOR_NAMESPACES.items():
            rel = str(ns.relative_to(ancestry.ROOT))
            out = subprocess.run(["git", "diff", "--name-only", commit, "--", rel],
                                 cwd=ancestry.ROOT, capture_output=True, text=True)
            self.assertEqual([x for x in out.stdout.split("\n") if x.strip()], [],
                             name)

    def test_sr_untouched_and_production_off(self):
        self.assertEqual([p.name for p in (NS / "code").glob("sr_*.py")], [])
        self.assertFalse(spec.PRODUCTION_ENABLED)
        for folder in ("results", "certificates", "production_logs"):
            self.assertFalse((NS / folder).exists())
        for rec in load(RECORDS):
            self.assertEqual(rec["detector"], "CUSUM")
            self.assertFalse(rec["production_run"])
            self.assertFalse(rec["result_bearing"])


# ================================================================= science
class Science(unittest.TestCase):
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

    def test_refine2_regression_only_tightens(self):
        for rec in load(RECORDS):
            for r, a in rec["whole_cell_refinement"].items():
                so = a["second_order"]
                for key in ("epsF_cell", "epsD_cell", "epsH_cell"):
                    self.assertLessEqual(F(so["refined"][key]),
                                         F(so["predecessor"][key]), (r, key))

    def test_order2_tightening_only_tightens(self):
        for rec in load(RECORDS):
            for name, t in rec["tightening_report"].items():
                self.assertLessEqual(t["tightened"], t["predecessor"], name)

    def test_auxiliary_towers_match_the_frozen_recursions(self):
        cell = next(c for c in CELLS if c["index"] == 321)
        with workprec(256):
            class Stub:
                pass
            s = Stub()
            s.left, s.right = F(cell["left"][0]), F(cell["right"][0])
            s.norms = sharp_norms.table(s.left, s.right)
            T = aux_refine.towers(s)
            k_ = s.norms["k"]
            for j in range(2, 5):
                for n in range(aux_refine.MAX_TOWER_ORDER + 1):
                    expect = sum(F(mag_fraction(arb(comb(n, i)) * k_[i]
                                                * T["h", j - 1, n - i]))
                                 for i in range(n + 1))
                    self.assertLessEqual(
                        F(mag_fraction(T["h", j, n])) - expect, F(1, 2 ** 40),
                        (j, n))

    def test_auxiliary_objects_are_all_certified(self):
        for rec in load(RECORDS):
            aux = rec["auxiliary_evidence"]["objects"]
            expected = ({"h_1:3", "S_0:3"}
                        | {f"h_{j}:3" for j in range(2, 5)}
                        | {f"S_{r}:3" for r in range(1, 5)}
                        | {f"W_{r}_{j}:3" for r in range(4)
                           for j in range(1, 4 - r)})
            self.assertEqual(set(aux), expected)
            for name, o in aux.items():
                self.assertGreater(F(o["delta_mid"]), 0, name)
                self.assertGreaterEqual(F(o["delta_mid"]),
                                        F(o["truncation_allowance"]), name)

    def test_cell_325_regression_control_all_pass(self):
        rec = next((r for r in load(RECORDS) if r["cell_index"] == CONTROL), None)
        self.assertIsNotNone(rec, "cell 325 regression control is required")
        for m, L in rec["m"].items():
            self.assertEqual(L["status"], "PASS", m)
            self.assertLess(L["cover"]["utilization"], 1.0, m)

    def test_every_previously_failing_obligation_is_reported(self):
        by_cell = {r["cell_index"]: r for r in load(RECORDS)}
        for cell, m in FAILED_BEFORE:
            self.assertIn(cell, by_cell, f"cell {cell} must be replayed")
            self.assertIn(m, by_cell[cell]["m"])

    def test_block_and_control_counts(self):
        by_cell = {r["cell_index"] for r in load(RECORDS)}
        if not by_cell:
            self.skipTest("no records")
        self.assertTrue(set(BLOCK) <= by_cell)
        block_obligations = sum(len(r["m"]) for r in load(RECORDS)
                                if r["cell_index"] in BLOCK)
        all_obligations = sum(len(r["m"]) for r in load(RECORDS))
        self.assertEqual(block_obligations, 28)      # 318-324
        if CONTROL in by_cell:
            self.assertEqual(all_obligations, 32)    # 318-325

    def test_failures_are_certificate_looseness_not_science(self):
        for rec in load(RECORDS):
            for m, L in rec["m"].items():
                if L["status"] == "PASS":
                    continue
                self.assertLess(F(L["R2_interval"]["lo"]), 0, (rec["cell_index"], m))
                self.assertGreater(F(L["R2_interval"]["hi"]), 0,
                                   (rec["cell_index"], m))

    def test_s0_charged_exactly_once(self):
        for rec in load(RECORDS):
            self.assertTrue(rec["s0_charge_audit"]["all_charged_exactly_once"])

    def test_far_field_inherited_unchanged(self):
        r = far_field_inherited.report()["inherited"]
        self.assertEqual(r["CUSUM_FAR_FIELD"], "PASS")
        self.assertEqual(r["SR_FAR_FIELD"], "PASS")
        self.assertFalse(r["re_derived_here"])
        self.assertFalse(r["gap_claim_reintroduced"])
        self.assertIsNone(r["uncovered_interval_between_c_D_and_e_far"])
        self.assertEqual([p.name for p in (NS / "code").glob("far_field.py")], [])

    def test_scipy_not_executed_on_the_certifying_path(self):
        ev = json.loads((NS / "evidence" / "scipy_execution_probe.json").read_text())
        self.assertTrue(ev["measured"])
        self.assertFalse(ev["called_on_certifying_path"])
        self.assertEqual(ev["scipy_functions_called"], [])
        runtime = json.loads(manifest.ARTIFACT.read_text())["runtime"]
        self.assertEqual(runtime["scipy_status"],
                         "AVAILABILITY_ONLY_IMPORTED_NOT_CALLED")
        self.assertIsNone(runtime["scipy_version"])
        for rec in load(RECORDS):
            self.assertFalse(rec["scipy_called_during_run"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
