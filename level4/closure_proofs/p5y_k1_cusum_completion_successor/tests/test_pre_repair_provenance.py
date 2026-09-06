"""PHASE 1: reproduce the f8e6f758 provenance defect (PROVENANCE = FAIL).

No predecessor namespace is modified. The strongest controls need no mutation
at all: the committed artifacts already demonstrate the defect.
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
import shutil
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import ancestry                                                 # noqa: E402

import producer as repair2_producer                             # noqa: E402
import successor_producer as SP                                 # noqa: E402

FINAL_REC = (ancestry.FINAL_NS
             / "diagnostics/cells/sharp_CUSUM_221_256.json")
REPAIR2_REC = (ancestry.REPAIR2_NS
               / "diagnostics/regression/repair2_221_256_full.json")
FINAL_CERTIFIERS = ("base.py", "sharp_norms.py", "sharp_certifier.py",
                    "final_qualify.py")


class Control1_ProducerBlindToItsOwnCode(unittest.TestCase):
    """Changing a final certifier leaves the stamped producer hash unchanged."""

    def test_final_records_stamp_the_repair2_hash(self):
        rec = json.loads(FINAL_REC.read_text())
        self.assertEqual(rec["producer"]["implementation_hash"],
                         repair2_producer.producer_hash())

    def test_repair2_manifest_omits_every_actual_final_certifier(self):
        files = set(repair2_producer.producer_manifest()["files"])
        for name in FINAL_CERTIFIERS:
            rel = str((ancestry.FINAL_NS / "code" / name)
                      .relative_to(ancestry.ROOT))
            self.assertNotIn(rel, files, name)

    def test_mutating_a_final_certifier_leaves_the_stamp_unchanged(self):
        """THE DEFECT: the producer changes, the stamped identity does not."""
        before = repair2_producer.producer_hash()
        scratch = Path(tempfile.mkdtemp(prefix="final_scratch_"))
        try:
            shutil.copytree(ancestry.FINAL_NS / "code", scratch / "code")
            target = scratch / "code/sharp_norms.py"
            original = target.read_bytes()
            target.write_bytes(original.replace(b"Z_HALF = F(11, 2)",
                                                b"Z_HALF = F(9, 2)"))
            self.assertNotEqual(hashlib.sha256(target.read_bytes()).hexdigest(),
                                hashlib.sha256(original).hexdigest())
            self.assertEqual(before, repair2_producer.producer_hash())
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_successor_hash_is_sensitive_to_the_same_change(self):
        base = SP.producer_manifest()
        rel = str((ancestry.FINAL_NS / "code/sharp_norms.py")
                  .relative_to(ancestry.ROOT))
        self.assertIn(rel, base["files"])
        mutated = copy.deepcopy(base)
        mutated["files"][rel] = "0" * 64
        self.assertNotEqual(SP.producer_hash(base), SP.producer_hash(mutated))


class Control2_TwoCertificatesOneProducer(unittest.TestCase):
    """Committed evidence: same producer identity, materially different science."""

    def test_repair2_and_final_records_share_the_stamped_producer(self):
        r2 = json.loads(REPAIR2_REC.read_text())
        fc = json.loads(FINAL_REC.read_text())
        self.assertEqual(r2["producer"]["implementation_hash"],
                         fc["producer"]["implementation_hash"])

    def test_but_they_certify_different_science(self):
        r2 = json.loads(REPAIR2_REC.read_text())
        fc = json.loads(FINAL_REC.read_text())
        differing = [m for m in ("1", "2", "3", "5")
                     if F(r2["m"][m]["M_R2"]) != F(fc["m"][m]["M_R2"])]
        self.assertEqual(differing, ["1", "2", "3", "5"])
        # and materially so, not by a rounding ulp
        self.assertLess(float(F(fc["m"]["5"]["M_R2"])),
                        0.9 * float(F(r2["m"]["5"]["M_R2"])))

    def test_successor_gives_them_different_producer_identities(self):
        self.assertNotEqual(SP.producer_hash(), repair2_producer.producer_hash())
        self.assertIn(repair2_producer.producer_hash(),
                      SP.rejected_producer_hashes().values())


class Control3_RecordCannotIdentifyItsBytes(unittest.TestCase):
    """The final record carries no manifest, so its bytes are unrecoverable."""

    def test_final_record_has_no_producer_manifest(self):
        rec = json.loads(FINAL_REC.read_text())
        self.assertNotIn("manifest", rec["producer"])

    def test_final_record_admits_the_hash_is_lineage_only(self):
        rec = json.loads(FINAL_REC.read_text())
        self.assertIn("lineage only", rec["producer"]["note"])

    def test_successor_record_carries_a_resolvable_manifest(self):
        m = SP.producer_manifest()
        self.assertGreaterEqual(len(m["files"]), 40)
        for name in FINAL_CERTIFIERS[:3]:      # the three actually executed
            rel = str((ancestry.FINAL_NS / "code" / name)
                      .relative_to(ancestry.ROOT))
            self.assertIn(rel, m["files"], name)
        # every digest resolves to a real file with that content
        for rel, digest in list(m["files"].items())[:10]:
            p = ancestry.ROOT / rel
            self.assertTrue(p.exists(), rel)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main(verbosity=2)
