"""PHASE 16: Aux4 negative controls, determinism, governance and science.

The thread contract is adopted before any import that pulls numpy in, because
`qualify4` refuses to certify in a process where numpy loaded unpinned.
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
import tempfile                                                 # noqa: E402
import unittest                                                 # noqa: E402
from fractions import Fraction as F                             # noqa: E402
from pathlib import Path                                        # noqa: E402

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import ancestry4                                                # noqa: E402

import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402

import aggregate_ledger                                         # noqa: E402
import hash_v2 as H                                             # noqa: E402
import identity4 as ID                                          # noqa: E402
import manifest_v2                                              # noqa: E402
import runtime_identity                                         # noqa: E402
import schema                                                   # noqa: E402
import scipy_guard                                              # noqa: E402
import tcb                                                      # noqa: E402

CELLS_DIR = NS / "diagnostics" / "cells"
RECORDS = sorted(CELLS_DIR.glob("aux4_CUSUM_*.json"))
PREAMBLE = (
    "import os, sys, json\n"
    "for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',"
    "'NUMEXPR_NUM_THREADS'):\n    os.environ[v] = '1'\n"
    "os.environ['K1_THREADS_PINNED'] = '1'\n"
    f"sys.path.insert(0, {str(NS / 'code')!r})\n")


def load(paths):
    return [json.loads(p.read_text()) for p in paths]


def probe(source: str) -> dict:
    with tempfile.TemporaryDirectory() as d:
        script = Path(d) / "probe.py"
        script.write_text(PREAMBLE + source)
        out = subprocess.run([sys.executable, str(script)], cwd=ancestry4.ROOT,
                             capture_output=True, text=True,
                             env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if out.returncode != 0:
        raise AssertionError(f"probe failed: {out.stderr[-1500:]}")
    return json.loads(out.stdout.strip().splitlines()[-1])


# =========================================================== producer TCB
class ProducerTrustBoundary(unittest.TestCase):
    def test_manifest_verifies_and_is_current(self):
        state = manifest_v2.verify()
        self.assertTrue(state["ok"], state["problems"])
        self.assertEqual(manifest_v2.build(), manifest_v2.load(),
                         "run `python code/manifest_v2.py --write` and commit")

    def test_membership_is_by_exact_path_not_basename(self):
        for path in tcb.tcb_paths():
            self.assertIn("/", path)
        # the module must define no basename-exemption mechanism at all
        self.assertFalse(hasattr(tcb, "NON_CERTIFYING_BASENAMES"))
        self.assertFalse(hasattr(tcb, "NON_CERTIFYING_DIRS"))
        for name in dir(tcb):
            self.assertNotIn("BASENAME", name.upper())

    def test_execution_relevant_predecessor_helpers_are_bound(self):
        files = manifest_v2.load()["files"]
        for rel in (
            "level4/closure_proofs/p5y_k1_cusum_aux3_successor/code/aux_certifier.py",
            "level4/closure_proofs/p5y_k1_cusum_aux3_successor/code/aux_propagate.py",
            "level4/closure_proofs/p5y_k1_cusum_completion_successor/code/refine2.py",
            "level4/closure_proofs/p5y_k1_cover_ledger_repair2/code/certhash.py",
            "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/propagate.py",
        ):
            self.assertIn(rel, files, rel)

    def test_read_artifacts_are_byte_bound(self):
        files = manifest_v2.load()["files"]
        for rel in (
            "level4/closure_proofs/p5y_k1_cusum_aux3_successor/manifests/producer_manifest_v1.json",
            "level4/closure_proofs/p5y_k1_cusum_aux3_successor/evidence/scipy_execution_probe.json",
        ):
            self.assertIn(rel, files, rel)

    def test_coverage_is_clean_in_a_real_certifying_process(self):
        out = probe("import qualify4, tcb\nprint(json.dumps(tcb.verify_coverage()))\n")
        self.assertTrue(out["ok"], out["uncovered"])

    def test_basename_bypass_is_detected(self):
        """A file named like an exempted one is still uncovered by path."""
        intruder = NS / "code" / "successor_producer.py"      # the Aux3 exempt name
        intruder.write_text("VALUE = 1\n")
        try:
            out = probe("import qualify4, tcb\n"
                        "import successor_producer\n"
                        "print(json.dumps(tcb.verify_coverage()))\n")
        finally:
            intruder.unlink()
        self.assertFalse(out["ok"], "a basename must not exempt anything")
        self.assertTrue(any("successor_producer.py" in p for p in out["uncovered"]))

    def test_missing_manifest_input_aborts(self):
        out = probe("import manifest_v2, json\n"
                    "m = manifest_v2.load()\n"
                    "m['files']['level4/closure_proofs/absent_file.py'] = '0'*64\n"
                    "manifest_v2.load = lambda: m\n"
                    "s = manifest_v2.verify()\n"
                    "print(json.dumps({'ok': s['ok'], 'p': s['problems'][:2]}))\n")
        self.assertFalse(out["ok"])
        self.assertTrue(any("missing" in p for p in out["p"]))

    def test_modified_certifying_byte_aborts(self):
        files = list(manifest_v2.load()["files"])
        for rel in files[:4] + files[-4:]:
            out = probe("import manifest_v2, json\n"
                        "m = manifest_v2.load()\n"
                        f"m['files'][{rel!r}] = '0'*64\n"
                        "manifest_v2.load = lambda: m\n"
                        "s = manifest_v2.verify()\n"
                        "print(json.dumps({'ok': s['ok'], 'p': s['problems'][:2]}))\n")
            self.assertFalse(out["ok"], rel)
            self.assertTrue(any("content changed" in p for p in out["p"]))


# ======================================================== runtime binding
class RuntimeBinding(unittest.TestCase):
    def test_blas_kernel_and_backend_bytes_are_bound(self):
        runtime = manifest_v2.load()["runtime"]
        self.assertIn("openblas_runtime_corename", runtime)
        self.assertIn("openblas_config", runtime)
        self.assertGreaterEqual(len(runtime["backend_libraries"]), 4)
        for rel, sha in runtime["backend_libraries"].items():
            self.assertEqual(len(sha), 64)
            self.assertTrue((ancestry4.ROOT / rel).exists(), rel)

    def test_runtime_mismatch_aborts(self):
        for key, bogus in (("openblas_runtime_corename", "Haswell"),
                           ("numpy_version", "0.0.0"),
                           ("python_flint_version", "0.0.0"),
                           ("cpython_version", "1.0.0"),
                           ("precision_bits", 128)):
            out = probe("import manifest_v2, json\n"
                        "m = manifest_v2.load()\n"
                        f"m['runtime'][{key!r}] = {bogus!r}\n"
                        "manifest_v2.load = lambda: m\n"
                        "s = manifest_v2.verify()\n"
                        "print(json.dumps({'ok': s['ok'], 'p': s['problems'][:3]}))\n")
            self.assertFalse(out["ok"], key)
            self.assertTrue(any(key in p for p in out["p"]), out["p"])

    def test_backend_library_mismatch_aborts(self):
        out = probe("import manifest_v2, json\n"
                    "m = manifest_v2.load()\n"
                    "k = sorted(m['runtime']['backend_libraries'])[0]\n"
                    "m['runtime']['backend_libraries'][k] = '0'*64\n"
                    "manifest_v2.load = lambda: m\n"
                    "s = manifest_v2.verify()\n"
                    "print(json.dumps({'ok': s['ok'], 'p': s['problems'][:2]}))\n")
        self.assertFalse(out["ok"])
        self.assertTrue(any("backend_libraries" in p for p in out["p"]))

    def test_runtime_contract_hash_is_separate_from_the_manifest_hash(self):
        ident = manifest_v2.identity()
        self.assertNotEqual(ident["runtime_contract_hash"],
                            ident["producer_manifest_hash"])
        self.assertNotEqual(ident["producer_identity_hash"],
                            ident["producer_manifest_hash"])


# ============================================================ scipy contract
class ScipyContract(unittest.TestCase):
    def test_guard_reports_scipy_free_on_the_real_path(self):
        for rec in load(RECORDS):
            self.assertTrue(rec["scipy_guard"]["scipy_free"])
            self.assertEqual(rec["scipy_guard"]["scipy_calls_observed"], [])

    def test_guard_actually_fires_on_a_scipy_call(self):
        """A guard that never fires proves nothing."""
        out = probe("import scipy_guard, json\n"
                    "g = scipy_guard.ScipyGuard()\n"
                    "with g:\n"
                    "    from scipy.special import ndtr\n"
                    "    ndtr(0.5)\n"
                    "try:\n"
                    "    g.require_clean(); fired = False\n"
                    "except scipy_guard.ScipyExecuted:\n"
                    "    fired = True\n"
                    "print(json.dumps({'fired': fired, "
                    "'calls': g.report()['scipy_calls_observed'][:3]}))\n")
        self.assertTrue(out["fired"], "the SciPy guard failed to detect a call")
        self.assertTrue(out["calls"])

    def test_probe_artifact_is_bound_not_merely_trusted(self):
        rel = ("level4/closure_proofs/p5y_k1_cusum_aux3_successor/evidence/"
               "scipy_execution_probe.json")
        self.assertIn(rel, manifest_v2.load()["files"])
        out = probe("import manifest_v2, json\n"
                    "m = manifest_v2.load()\n"
                    f"m['files'][{rel!r}] = '0'*64\n"
                    "manifest_v2.load = lambda: m\n"
                    "print(json.dumps({'ok': manifest_v2.verify()['ok']}))\n")
        self.assertFalse(out["ok"])


# ======================================================== final gate order
class FinalGate(unittest.TestCase):
    def test_gate_runs_after_the_scientific_hash(self):
        body = (NS / "code" / "qualify4.py").read_text().split("def run_cell")[1]
        self.assertGreater(body.index("manifest_v2.final_gate(scipy_guard=guard)"),
                           body.index('record["scientific_content_hash"] = H'))

    def test_late_import_after_the_initial_gate_aborts(self):
        intruder = NS / "code" / "_late_probe_module.py"
        intruder.write_text("VALUE = 1\n")
        try:
            out = probe("import qualify4, manifest_v2, json\n"
                        "manifest_v2.initial_gate()\n"
                        "import _late_probe_module\n"
                        "try:\n"
                        "    manifest_v2.final_gate(); aborted = False; msg = ''\n"
                        "except manifest_v2.ManifestFailure as e:\n"
                        "    aborted = True; msg = str(e)[:140]\n"
                        "print(json.dumps({'aborted': aborted, 'msg': msg}))\n")
        finally:
            intruder.unlink()
        self.assertTrue(out["aborted"], "a late import must abort the final gate")
        self.assertIn("_late_probe_module", out["msg"])

    def test_late_source_mutation_aborts(self):
        target = NS / "code" / "schema.py"
        original = target.read_bytes()
        try:
            out = probe("import qualify4, manifest_v2, json, pathlib\n"
                        "manifest_v2.initial_gate()\n"
                        f"p = pathlib.Path({str(target)!r})\n"
                        "p.write_bytes(p.read_bytes() + b'\\n# late mutation\\n')\n"
                        "try:\n"
                        "    manifest_v2.final_gate(); aborted = False; msg = ''\n"
                        "except manifest_v2.ManifestFailure as e:\n"
                        "    aborted = True; msg = str(e)[:140]\n"
                        "print(json.dumps({'aborted': aborted, 'msg': msg}))\n")
        finally:
            target.write_bytes(original)
        self.assertTrue(out["aborted"])
        self.assertIn("content changed", out["msg"])

    def test_final_gate_requires_a_clean_scipy_guard(self):
        out = probe("import qualify4, manifest_v2, scipy_guard, json\n"
                    "g = scipy_guard.ScipyGuard()\n"
                    "g.observed.append('scipy.special.ndtr')\n"
                    "try:\n"
                    "    manifest_v2.final_gate(scipy_guard=g); aborted = False\n"
                    "except scipy_guard.ScipyExecuted:\n"
                    "    aborted = True\n"
                    "print(json.dumps({'aborted': aborted}))\n")
        self.assertTrue(out["aborted"])

    def test_certification_refuses_without_the_threading_contract(self):
        out = probe("for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS',"
                    "'MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):\n"
                    "    os.environ.pop(v, None)\n"
                    "os.environ.pop('K1_THREADS_PINNED', None)\n"
                    "import numpy\n"
                    "import qualify4\n"
                    "try:\n"
                    "    qualify4.run_cell(325); refused = False\n"
                    "except qualify4.ThreadingContractViolated:\n"
                    "    refused = True\n"
                    "print(json.dumps({'refused': refused}))\n")
        self.assertTrue(out["refused"])


# ====================================================== scientific hash V2
class ScientificHashV2(unittest.TestCase):
    def setUp(self):
        if not RECORDS:
            self.skipTest("no records yet")
        self.rec = json.loads(RECORDS[0].read_text())
        self.base = H.record_scientific_hash(self.rec)

    def test_stored_hash_recomputes(self):
        for rec in load(RECORDS):
            self.assertEqual(rec["scientific_content_hash"],
                             H.record_scientific_hash(rec))
            self.assertEqual(rec["auxiliary_evidence_hash"],
                             H.auxiliary_evidence_hash(rec))

    def test_no_record_field_is_unaccounted_for(self):
        for rec in load(RECORDS):
            audit = H.audit_record(rec)
            self.assertEqual(audit["unaccounted"], [])
            self.assertTrue(audit["ok"])

    def test_the_three_aux3_omissions_are_bound(self):
        for field in ("candidate_suprema", "order", "hermite_weight"):
            bad = copy.deepcopy(self.rec)
            if field == "candidate_suprema":
                key = sorted(bad["auxiliary_evidence"][field])[0]
                bad["auxiliary_evidence"][field][key] = "999999/1"
            else:
                bad["auxiliary_evidence"][field] = "TAMPERED"
            self.assertNotEqual(self.base, H.record_scientific_hash(bad), field)
            self.assertNotEqual(H.auxiliary_evidence_hash(self.rec),
                                H.auxiliary_evidence_hash(bad), field)

    def test_every_scientific_field_moves_the_hash(self):
        """Exhaustive over the classified scientific leaves of a real record."""
        # `scientific_content_hash` is the digest itself: it cannot be an input
        # to its own computation, so it is excluded from the record before
        # hashing. Tampering with the stored digest is caught by recomputation
        # (`test_stored_hash_recomputes`), not by self-binding.
        paths = [p for p, c in schema.classify_record(self.rec)["paths"].items()
                 if c == schema.SCIENTIFIC and p != "scientific_content_hash"]
        self.assertGreater(len(paths), 500)
        unbound = []
        for path in paths:
            bad = copy.deepcopy(self.rec)
            keys = path.split(".")
            cur = bad
            try:
                for k in keys[:-1]:
                    cur = cur[int(k)] if isinstance(cur, list) else cur[k]
                last = keys[-1]
                if isinstance(cur, list):
                    cur[int(last)] = "MUTATED"
                else:
                    cur[last] = "MUTATED"
            except (KeyError, IndexError, ValueError):
                continue
            if H.record_scientific_hash(bad) == self.base:
                unbound.append(path)
        self.assertEqual(unbound, [], f"{len(unbound)} scientific fields unbound")

    def test_incidental_runtime_noise_is_ignored(self):
        noisy = copy.deepcopy(self.rec)
        noisy["cpu_seconds_including_dependencies"] = 1.0
        noisy["cpu_seconds_auxiliary"] = 0.0
        noisy["cpu_seconds_prepare"] = 0.0
        noisy["wall_seconds"] = 1.0
        noisy["peak_rss_kib"] = 1
        for o in noisy["objects"].values():
            o["cpu_seconds"] = 0.0
            o["bernstein_calls"] = 999
        self.assertEqual(self.base, H.record_scientific_hash(noisy))

    def test_auxiliary_hash_corruption_is_detected(self):
        bad = copy.deepcopy(self.rec)
        bad["auxiliary_evidence_hash"] = "0" * 64
        self.assertNotEqual(self.base, H.record_scientific_hash(bad))


# ============================================================== provenance
class Provenance(unittest.TestCase):
    def setUp(self):
        if not RECORDS:
            self.skipTest("no records yet")
        self.rec = json.loads(RECORDS[0].read_text())
        self.cell = self.rec["cell_index"]
        self.certs = {uid: {"identity": c["identity"], "status": c["status"]}
                      for uid, c in self.rec["certificates"].items()}
        self.ctx = ID.context(precision_bits=self.rec["precision_bits"])
        self.aux_hash = self.rec["auxiliary_evidence_hash"]

    def _unit(self, tag="dF_2"):
        return ("CUSUM", self.cell, "object", tag)

    def test_identity_carries_all_five_required_bindings(self):
        ident = self.rec["certificates"][f"CUSUM|{self.cell}|object|dF_2"]["identity"]
        m = manifest_v2.identity()
        for key in ("producer_manifest_schema", "producer_manifest_version",
                    "producer_manifest_path", "producer_manifest_hash",
                    "runtime_contract_hash", "producer_identity_hash"):
            self.assertEqual(ident[key], m[key], key)

    def test_stale_producer_rejected(self):
        for field in ("producer_manifest_hash", "runtime_contract_hash",
                      "producer_identity_hash"):
            ident = copy.deepcopy(
                self.rec["certificates"][f"CUSUM|{self.cell}|object|dF_2"]["identity"])
            ident[field] = "9" * 64
            with self.assertRaises(ID.ResumeRejected, msg=field):
                ID.admit_resume_record(ident, self._unit(),
                                       dependency_certificates=self.certs,
                                       auxiliary_evidence_hash=self.aux_hash,
                                       **self.ctx)

    def test_predecessor_identities_rejected(self):
        base = self.rec["certificates"][f"CUSUM|{self.cell}|object|dF_2"]["identity"]
        for name, value in ID.rejected_producer_identities().items():
            ident = copy.deepcopy(base)
            ident["producer_manifest_hash"] = value
            with self.assertRaises(ID.ProvenanceRejected, msg=name):
                ID.admit_resume_record(ident, self._unit(),
                                       dependency_certificates=self.certs,
                                       auxiliary_evidence_hash=self.aux_hash,
                                       **self.ctx)

    def test_cross_cell_substitution_rejected(self):
        ident = self.rec["certificates"][f"CUSUM|{self.cell}|object|dF_2"]["identity"]
        other = ("CUSUM", 7 if self.cell != 7 else 8, "object", "dF_2")
        with self.assertRaises(ID.ResumeRejected):
            ID.admit_resume_record(ident, other,
                                   dependency_certificates=self.certs,
                                   auxiliary_evidence_hash=self.aux_hash, **self.ctx)

    def test_auxiliary_hash_tamper_rejected(self):
        ident = self.rec["certificates"][f"CUSUM|{self.cell}|object|dF_2"]["identity"]
        with self.assertRaises(ID.ProvenanceRejected):
            ID.admit_resume_record(ident, self._unit(),
                                   dependency_certificates=self.certs,
                                   auxiliary_evidence_hash="0" * 64, **self.ctx)

    def test_chain_verifies_with_28_obligations(self):
        for rec in load(RECORDS):
            self.assertTrue(rec["provenance_chain"]["all_verified"])
            self.assertEqual(rec["provenance_chain"]["obligations"], 28)
            self.assertTrue(rec["provenance_chain"]["auxiliary_evidence_bound"])


# ================================================================== ledger
class AggregateLedger(unittest.TestCase):
    def test_ledger_rejects_a_predecessor_record(self):
        aux3 = sorted((ancestry4.AUX3_NS / "diagnostics" / "cells")
                      .glob("aux3_CUSUM_*.json"))
        if not aux3:
            self.skipTest("no Aux3 records")
        rec = json.loads(aux3[0].read_text())
        cell = next(c for c in aggregate_ledger.cusum_cells()
                    if c["index"] == rec["cell_index"])
        v = aggregate_ledger.verify_cell(rec, cell, manifest_v2.identity())
        self.assertFalse(v["ok"], "an Aux3 record must not be composable")
        self.assertTrue(any("producer" in p for p in v["problems"]))

    def test_missing_and_duplicate_cells_are_detected(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = aggregate_ledger.build(d)          # empty directory
            self.assertEqual(ledger["cusum_full_cover"], "INCOMPLETE")
            self.assertEqual(len(ledger["universe"]["cells_missing"]), 326)
        if RECORDS:
            with tempfile.TemporaryDirectory() as d:
                rec = json.loads(RECORDS[0].read_text())
                for name in ("aux4_CUSUM_1_256.json", "aux4_CUSUM_2_256.json"):
                    (Path(d) / name).write_text(json.dumps(rec))
                with self.assertRaises(ValueError):
                    aggregate_ledger.load_records(d)

    def test_ledger_binds_far_field_and_frozen_hashes(self):
        ledger = aggregate_ledger.build(CELLS_DIR)
        self.assertEqual(ledger["far_field"]["CUSUM_FAR_FIELD"], "PASS")
        self.assertFalse(
            ledger["far_field"]["superseded_gap_interpretation_reintroduced"])
        self.assertEqual(ledger["frozen"]["checkpoint_hash"], spec.CHECKPOINT_SHA256)
        self.assertEqual(ledger["frozen"]["cusum_cell_count"], 326)
        self.assertTrue(aggregate_ledger.verify(ledger)["ok"])

    def test_ledger_hash_detects_corruption(self):
        ledger = aggregate_ledger.build(CELLS_DIR)
        bad = copy.deepcopy(ledger)
        bad["universe"]["cells_present"] = 999
        self.assertFalse(aggregate_ledger.verify(bad)["ok"])


# ============================================================== governance
class Governance(unittest.TestCase):
    def test_universe_and_geometry_unchanged(self):
        self.assertEqual(len(reviewed.work_ids()), 17978)
        self.assertEqual(spec.TOTAL_UNITS, 17978)
        self.assertEqual(len(aggregate_ledger.cusum_cells()), 326)
        self.assertEqual(spec.M_VALUES, (1, 2, 3, 5))
        self.assertEqual(spec.COUNTS, {"CUSUM": 326, "SR": 316})
        self.assertEqual(spec.PRODUCTION_BITS, 256)
        self.assertEqual(spec.HARD_CAP_CPU_H, 1126)
        self.assertFalse(spec.PRODUCTION_ENABLED)
        self.assertEqual(sum(spec.TOP_BUDGETS.values()), F(19, 100))
        self.assertEqual(spec.verify_frozen_spec(), spec.FROZEN_HASHES)
        self.assertTrue(ID.universe_unchanged()["ok"])

    def test_auxiliary_evidence_adds_no_top_level_id_or_dag_node(self):
        import re
        self.assertFalse(ID.AUXILIARY_OWNERSHIP["creates_top_level_work_ids"])
        self.assertFalse(ID.AUXILIARY_OWNERSHIP["creates_dag_edges"])
        order3 = re.compile(r"^(?:(?:h|S):\d+:3|Sclosed:3|W:\d+:\d+:3)$")
        for rec in load(RECORDS):
            self.assertEqual(rec["universe"]["total"], 17978)
            for node in list(rec["eps_cell"]) + list(rec["eps_mid"]):
                self.assertIsNone(order3.match(node), node)

    def test_predecessor_namespaces_byte_preserved(self):
        for name, (ns, commit) in ancestry4.PREDECESSOR_NAMESPACES.items():
            rel = str(ns.relative_to(ancestry4.ROOT))
            out = subprocess.run(["git", "diff", "--name-only", commit, "--", rel],
                                 cwd=ancestry4.ROOT, capture_output=True, text=True)
            self.assertEqual([x for x in out.stdout.split("\n") if x.strip()], [], name)

    def test_no_monkey_patching(self):
        import ast
        for path in sorted((NS / "code").rglob("*.py")):
            tree = ast.parse(path.read_text())
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported |= {a.asname or a.name.split(".")[0] for a in node.names}
                elif isinstance(node, ast.ImportFrom):
                    imported |= {a.asname or a.name for a in node.names}
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for t in node.targets:
                        if (isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                                and t.value.id in imported):
                            self.fail(f"{path.name}:{node.lineno} patches "
                                      f"{t.value.id}.{t.attr}")

    def test_sr_untouched_and_production_off(self):
        self.assertEqual([p.name for p in (NS / "code").glob("sr_*.py")], [])
        for folder in ("results", "certificates", "production_logs"):
            self.assertFalse((NS / folder).exists())
        for rec in load(RECORDS):
            self.assertEqual(rec["detector"], "CUSUM")
            self.assertFalse(rec["production_run"])
            self.assertFalse(rec["result_bearing"])


# ================================================================= science
class Science(unittest.TestCase):
    def test_records_carry_all_four_m_levels(self):
        for rec in load(RECORDS):
            self.assertEqual(sorted(rec["m"], key=int), ["1", "2", "3", "5"])

    def test_difficult_cells_remain_pass(self):
        by_cell = {r["cell_index"]: r for r in load(RECORDS)}
        for cell, m in ((319, "5"), (320, "5"), (321, "5"), (322, "5"), (323, "5")):
            if cell in by_cell:
                self.assertEqual(by_cell[cell]["m"][m]["status"], "PASS",
                                 f"cell {cell} m={m}")
        if 325 in by_cell:
            for m, L in by_cell[325]["m"].items():
                self.assertEqual(L["status"], "PASS", f"control 325 m={m}")

    def test_failures_would_be_certificate_looseness(self):
        for rec in load(RECORDS):
            for m, L in rec["m"].items():
                if L["status"] == "PASS":
                    continue
                self.assertLess(F(L["R2_interval"]["lo"]), 0)
                self.assertGreater(F(L["R2_interval"]["hi"]), 0)

    def test_s0_charged_exactly_once(self):
        for rec in load(RECORDS):
            self.assertTrue(rec["s0_charge_audit"]["all_charged_exactly_once"])

    def test_determinism_record(self):
        path = NS / "diagnostics" / "determinism.json"
        if not path.exists():
            self.skipTest("no repeat runs recorded")
        rep = json.loads(path.read_text())
        self.assertTrue(rep["cells"])
        for cell, v in rep["cells"].items():
            for key in ("scientific_hash_identical", "auxiliary_hash_identical",
                        "producer_identical", "intervals_identical",
                        "error_bounds_identical"):
                self.assertTrue(v[key], f"cell {cell}: {key}")
            self.assertTrue(v["runtime_fields_differed"], cell)


if __name__ == "__main__":
    unittest.main(verbosity=2)
