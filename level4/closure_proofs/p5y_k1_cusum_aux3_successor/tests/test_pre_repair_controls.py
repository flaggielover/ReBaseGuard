"""PHASE 1: reproduce the adjudicated predecessor defects as explicit controls.

These tests PASS by demonstrating that the defect is really there in the
predecessor. They are the reason this successor exists, and they are written
before any fix so that the fix has something to be measured against. No
predecessor file is mutated: every defect is reproduced by reading the committed
bytes, or by exercising the predecessor's own published functions.

Defects reproduced, as adjudicated:

  1. runtime monkey-patching: `propagate.refine = sys.modules[__name__]`
  2. certification path using loaded-module verification with `strict=False`
  3. records carrying a producer identity with no committed immutable manifest
     that a verifier can resolve and independently recompute
  4. every committed record going stale when the numerical runtime moves
  5. the predecessor suite staying green through all of the above
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

import ancestry                                                 # noqa: E402

import no_monkeypatch                                           # noqa: E402

PRED = ancestry.CUSUM_NS
PRED_RECORDS = sorted((PRED / "diagnostics" / "cells").glob("succ_CUSUM_*.json"))


class Defect1RuntimeMonkeyPatching(unittest.TestCase):
    def test_predecessor_assigns_into_an_imported_module(self):
        found = no_monkeypatch.scan_path(PRED / "code")
        patches = [f for f in found
                   if f["pattern"] == "module_attribute_assignment"]
        self.assertTrue(patches, "expected the predecessor's propagate.refine patch")
        self.assertTrue(any(p["detail"] == "propagate.refine" for p in patches))

    def test_the_patch_redirects_a_reviewed_module(self):
        src = (PRED / "code" / "refine2.py").read_text()
        self.assertIn("propagate.refine = sys.modules[__name__]", src)
        # and the reviewed module it redirects is unedited, so a reader of
        # propagate.py cannot see which refinement actually runs
        reviewed = (ancestry.IMPL_NS / "code" / "propagate.py").read_text()
        self.assertIn("import refine", reviewed)
        self.assertIn("refine.refine(cert, mid, cellwise)", reviewed)

    def test_this_successor_is_clean_of_every_pattern(self):
        self.assertEqual(no_monkeypatch.scan_path(NS), [])


class Defect2NonFatalCoverage(unittest.TestCase):
    def test_predecessor_certifying_path_used_strict_false(self):
        src = (PRED / "code" / "successor_qualify.py").read_text()
        self.assertIn("verify_loaded_modules_covered(strict=False)", src)

    def test_strict_false_returns_instead_of_aborting(self):
        """An uncovered certifying module does not stop the predecessor."""
        probe = (
            "import sys, json\n"
            f"sys.path.insert(0, {str(PRED / 'code')!r})\n"
            "import successor_producer as SP\n"
            "real = SP.producer_manifest\n"
            "SP.producer_manifest = lambda: {'files': {}}   # nothing covered\n"
            "r = SP.verify_loaded_modules_covered(strict=False)\n"
            "print(json.dumps({'ok': r['ok'], 'uncovered': len("
            "r['uncovered_loaded_modules']), 'raised': False}))\n")
        out = _run(probe)
        self.assertEqual(out["raised"], False)
        self.assertFalse(out["ok"])
        self.assertGreater(out["uncovered"], 0,
                           "the probe must actually have uncovered modules")


class Defect3UnresolvableProducerIdentity(unittest.TestCase):
    def test_predecessor_has_no_committed_manifest_artifact(self):
        candidates = list(PRED.rglob("*manifest*.json"))
        self.assertEqual(candidates, [],
                         "the predecessor committed no manifest artifact")

    def test_records_carry_a_hash_with_nothing_to_resolve_it_against(self):
        self.assertTrue(PRED_RECORDS)
        for path in PRED_RECORDS:
            rec = json.loads(path.read_text())
            self.assertIn("implementation_hash", rec["producer"])
            self.assertEqual(len(rec["producer"]["implementation_hash"]), 64)
            self.assertNotIn("producer_manifest_path", rec["producer"])
            self.assertNotIn("manifest", rec["producer"])
        # the only way to check that number is to re-run the predecessor's own
        # code over the current working tree and trust the answer
        src = (PRED / "code" / "successor_producer.py").read_text()
        self.assertIn("def producer_manifest()", src)
        self.assertNotIn("json.load", src.split("def producer_manifest")[1][:800])

    def test_this_successor_publishes_a_resolvable_artifact(self):
        import manifest
        self.assertTrue(manifest.ARTIFACT.exists())
        committed = json.loads(manifest.ARTIFACT.read_text())
        self.assertEqual(committed["schema"], manifest.SCHEMA)
        self.assertTrue(committed["files"])


class Defect4StaleOnRuntimeChange(unittest.TestCase):
    def test_a_numpy_version_bump_invalidates_every_committed_record(self):
        probe = (
            "import sys, json, copy\n"
            f"sys.path.insert(0, {str(PRED / 'code')!r})\n"
            "import successor_producer as SP\n"
            "base = SP.producer_manifest()\n"
            "bumped = copy.deepcopy(base)\n"
            "bumped['generation_parameters']['numpy_version'] = '0.0.0-bumped'\n"
            "print(json.dumps({'before': SP.producer_hash(base),\n"
            "                  'after': SP.producer_hash(bumped)}))\n")
        out = _run(probe)
        self.assertNotEqual(out["before"], out["after"])
        stamped = {json.loads(p.read_text())["producer"]["implementation_hash"]
                   for p in PRED_RECORDS}
        self.assertEqual(stamped, {out["before"]},
                         "records were stamped with the pre-bump hash")
        self.assertNotIn(out["after"], stamped,
                         "after a runtime bump no committed record matches")

    def test_the_predecessor_offers_no_way_to_detect_this_from_the_record(self):
        rec = json.loads(PRED_RECORDS[0].read_text())
        self.assertNotIn("runtime", rec["producer"])
        # the versions that the hash depends on are not recorded anywhere in the
        # record, so a reader cannot tell which runtime produced it
        blob = json.dumps(rec)
        self.assertNotIn("numpy_version", blob)
        self.assertNotIn("python_flint_version", blob)


class Defect5GreenSuiteHidesIt(unittest.TestCase):
    def test_predecessor_suite_passes_in_an_isolated_process(self):
        out = subprocess.run(
            [sys.executable, "-m", "unittest", "discover",
             "-s", str(PRED / "tests"), "-p", "test_successor.py"],
            cwd=ancestry.ROOT, capture_output=True, text=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        tail = out.stderr.strip().splitlines()[-1] if out.stderr else ""
        # Green, or green except for the namespace-scoped worktree assertion that
        # a NEW uncommitted namespace necessarily trips. Either way the suite
        # never notices defects 1-4.
        self.assertTrue(
            tail.startswith("OK") or "test_writes_only_inside_this_namespace"
            in out.stderr,
            f"unexpected predecessor suite result: {out.stderr[-800:]}")
        self.assertNotIn("monkey", out.stderr.lower())
        self.assertNotIn("manifest", out.stderr.lower())


def _run(source: str) -> dict:
    out = subprocess.run([sys.executable, "-c", source], cwd=ancestry.ROOT,
                         capture_output=True, text=True,
                         env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if out.returncode != 0:
        raise AssertionError(f"probe failed: {out.stderr[-1200:]}")
    return json.loads(out.stdout.strip().splitlines()[-1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
