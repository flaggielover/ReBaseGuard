"""PRE-REPAIR2 controls: prove Repair1's two provenance defects, empirically.

Nothing in the repository is mutated. Repair1's certifying bytes are copied to a
scratch tree and altered there, and Repair1's own hash functions are applied to
the result, so the defect is demonstrated rather than asserted.

Control A  a Repair1-produced certificate keeps the SAME stamped
           implementation hash after Repair1's certificate-producing code
           changes.
Control B  a dependency certificate's content changes while Repair1's
           source_certificate_hash for it stays identical.

Both controls fail under Repair2.
"""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import prior2                                                   # noqa: E402

import universe as reviewed                                     # noqa: E402
import repair_universe as RU1                                   # noqa: E402

import certhash                                                 # noqa: E402
import producer                                                 # noqa: E402
import provenance                                               # noqa: E402
import repair2_universe as RU2                                  # noqa: E402

REPAIR1_RECORD = (prior2.REPAIR1_NS
                  / "diagnostics/regression/repaired_221_256_full.json")


def repair1_record() -> dict:
    return json.loads(REPAIR1_RECORD.read_text())


class ControlA_ProducerHashDoesNotCoverProducer(unittest.TestCase):
    """Repair1 stamps the reviewed PARENT hash, which excludes Repair1's code."""

    def test_repair1_evidence_stamps_the_parent_hash(self):
        rec = repair1_record()
        stamped = {i["implementation_hash"] for i in rec["identity"].values()}
        self.assertEqual(stamped, {reviewed.implementation_hash()})
        backends = {i["backend_hash"] for i in rec["identity"].values()}
        self.assertEqual(backends, {reviewed.implementation_hash()})

    def test_parent_hash_reads_no_repair1_file(self):
        code = prior2.IMPL_NS / "code"
        read = {str((code / n).resolve()) for n in reviewed.CERTIFYING_MODULES}
        for name in producer.REPAIR1_MODULES:
            self.assertNotIn(str((prior2.REPAIR1_NS / "code" / name).resolve()),
                             read, name)

    def test_mutating_repair1_producer_code_leaves_the_stamp_unchanged(self):
        """THE DEFECT: the producer changes, the stamped identity does not."""
        before = reviewed.implementation_hash()
        scratch = Path(tempfile.mkdtemp(prefix="repair1_scratch_"))
        try:
            shutil.copytree(prior2.REPAIR1_NS / "code", scratch / "code")
            target = scratch / "code/repair_layer2.py"
            original = target.read_bytes()
            # A change that would alter every certified delta this module emits.
            target.write_bytes(original.replace(
                b"ROUNDING_SLACK = F(1, 2 ** 40)",
                b"ROUNDING_SLACK = F(1, 2 ** 8)"))
            self.assertNotEqual(hashlib.sha256(target.read_bytes()).hexdigest(),
                                hashlib.sha256(original).hexdigest(),
                                "scratch mutation did not take")
            after = reviewed.implementation_hash()
            self.assertEqual(before, after,
                             "Repair1's stamped hash is blind to its own code")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def test_repair2_producer_hash_is_sensitive_to_the_same_change(self):
        """Repair2 binds the same file, so the same change moves its hash."""
        base = producer.producer_manifest()
        rel = str((prior2.REPAIR1_NS / "code/repair_layer2.py")
                  .relative_to(prior2.ROOT))
        self.assertIn(rel, base["files"])
        mutated = copy.deepcopy(base)
        mutated["files"][rel] = "0" * 64
        self.assertNotEqual(producer.producer_hash(base),
                            producer.producer_hash(mutated))

    def test_repair2_hash_is_distinct_from_the_parent_and_covers_repair1(self):
        self.assertNotEqual(producer.producer_hash(), producer.parent_hash())
        self.assertTrue(producer.covers_repair1_producer_code())


class ControlB_SourceHashesIgnoreCertificateContent(unittest.TestCase):
    """Repair1 hashes dependency IDENTITY, never the dependency's content."""

    UNIT = ("CUSUM", 221, "object", "dF_2")

    def test_repair1_source_hash_is_identity_only(self):
        ctx = RU1.context(backend_hash="B")
        a = RU1.canonical_identity(self.UNIT, **ctx)["source_certificate_hashes"]
        # Recomputing from pure metadata reproduces it exactly: no content enters.
        for dep in RU1.dependencies_of(self.UNIT):
            base = RU1._base_identity(dep, backend_hash=ctx["backend_hash"],
                                      impl_hash=ctx["impl_hash"],
                                      precision_bits=ctx["precision_bits"])
            uid = "|".join(str(x) for x in dep)
            self.assertEqual(a[uid],
                             hashlib.sha256(RU1.canonical(base)).hexdigest())

    def test_changing_the_dependency_certificate_does_not_move_repair1_hash(self):
        """THE DEFECT: a different certificate, the same source hash."""
        ctx = RU1.context(backend_hash="B")
        before = RU1.canonical_identity(self.UNIT, **ctx)["source_certificate_hashes"]

        rec = repair1_record()
        mutated = copy.deepcopy(rec)
        # A scientifically meaningful change to the consumed F_2 certificate.
        mutated["objects"]["F_2"]["delta_mid"] = "1/2"
        mutated["eps_mid"]["F:2"] = "1/2"

        after = RU1.canonical_identity(self.UNIT, **ctx)["source_certificate_hashes"]
        self.assertEqual(before, after,
                         "Repair1's source hash moved with content (it should "
                         "not, pre-repair)")
        # The consumed content really did change.
        self.assertNotEqual(rec["objects"]["F_2"]["delta_mid"],
                            mutated["objects"]["F_2"]["delta_mid"])

    def test_repair2_source_hash_does_move_with_content(self):
        ctx = RU2.context()
        rec = repair1_record()
        certs = provenance.build_cell_certificates(rec, **ctx)
        mutated_rec = copy.deepcopy(rec)
        mutated_rec["objects"]["F_2"]["delta_mid"] = "1/2"
        mutated_rec["eps_mid"]["F:2"] = "1/2"
        certs2 = provenance.build_cell_certificates(mutated_rec, **ctx)

        f2 = "CUSUM|221|object|F_2"
        self.assertNotEqual(certhash.certificate_hash(certs[f2]),
                            certhash.certificate_hash(certs2[f2]))
        # ... and the parent that consumes it changes too.
        parent = "CUSUM|221|object|dF_2"
        self.assertNotEqual(
            certs[parent]["identity"]["source_certificate_hashes"][f2],
            certs2[parent]["identity"]["source_certificate_hashes"][f2])
        self.assertNotEqual(certhash.certificate_hash(certs[parent]),
                            certhash.certificate_hash(certs2[parent]))

    def test_repair2_rejects_the_swapped_dependency(self):
        ctx = RU2.context()
        rec = repair1_record()
        certs = provenance.build_cell_certificates(rec, **ctx)
        mutated_rec = copy.deepcopy(rec)
        mutated_rec["objects"]["F_2"]["delta_mid"] = "1/2"
        swapped = dict(certs)
        swapped["CUSUM|221|object|F_2"] = provenance.build_cell_certificates(
            mutated_rec, **ctx)["CUSUM|221|object|F_2"]
        with self.assertRaises(RU2.ProvenanceRejected):
            provenance.verify_chain(("CUSUM", 221, "object", "dF_2"),
                                    swapped, **ctx)


if __name__ == "__main__":
    unittest.main(verbosity=2)
