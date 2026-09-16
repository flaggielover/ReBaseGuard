"""Adversarial tests for the CUSUM Aux5 composite closure verifier. Governance only: every mutation happens on a
temporary copy of this namespace, no production object is touched and nothing is authorized.

  python -B tests/test_verify_closure.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

import verify_closure as V                                                       # noqa: E402

EV = V.EV


class Copy:
    def __enter__(self):
        self.d = tempfile.TemporaryDirectory()
        self.ns = Path(self.d.name) / "ns"
        shutil.copytree(V.NS, self.ns)
        return self.ns

    def __exit__(self, *exc):
        self.d.cleanup()


def rewrite(path: Path, mutate) -> None:
    obj = json.loads(path.read_bytes())
    mutate(obj)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")


class ClosureVerifierTests(unittest.TestCase):
    def test_committed_package_verifies(self):
        self.assertEqual(V.verify(), [])

    def test_records_rebuild_from_the_committed_evidence(self):
        self.assertEqual((V.NS / V.HASHES).read_text(),
                         json.dumps(V.build_hashes(), indent=1, sort_keys=True) + "\n")
        self.assertEqual((V.NS / V.VERDICT).read_text(),
                         json.dumps(V.build_verdict(), indent=1, sort_keys=True) + "\n")

    def test_verdict_is_scoped_to_the_composite_and_claims_no_recomputation(self):
        v = json.loads((V.NS / V.VERDICT).read_bytes())
        self.assertEqual((v["cusum_aux5_composite_closure"], v["k4_attestation"]), ("CLOSED", "PASS"))
        self.assertEqual((v["composite_total"], v["carryover_cells"], v["successor_cells"]), (326, 128, 198))
        self.assertIs(v["predecessor_cells_recomputed"], False)
        self.assertEqual(v["predecessor_disposition"], "HALTED")
        for word in ("K1 CLOSED", "P5Y CLOSED", "SR CLOSED", "PS1 CLOSED"):
            self.assertNotIn(word, json.dumps(v))

    def test_edited_artifact_is_caught(self):
        with Copy() as ns:
            rewrite(ns / EV / "HOST_AT_CLOSURE.json", lambda o: o.__setitem__("packages", {}))
            self.assertTrue(any("ARTIFACT_HASH_DIFFERS" in x or "DOES_NOT_REBUILD" in x for x in V.verify(ns)))

    def test_missing_artifact_fails_closed(self):
        with Copy() as ns:
            (ns / EV / "CONTAINMENT_POST_RESTORE.json").unlink()
            self.assertTrue(V.verify(ns))

    def test_audit_state_downgrade_is_caught(self):
        with Copy() as ns:
            rewrite(ns / EV / "COMPOSITE_AUDIT.json", lambda o: o.__setitem__("state", "INCOMPLETE"))
            problems = V.verify(ns)
            self.assertTrue(any("DOES_NOT_REBUILD" in x for x in problems), problems[:3])
            V.write_records(ns)                                                  # even a re-stamped inventory fails
            problems = V.verify(ns)
            self.assertTrue(any("AUDIT_NOT_COMPLETE" in x for x in problems), problems[:3])

    def test_audit_digest_rebinding_is_caught(self):
        """Rewriting the audit and its inventory hash still breaks the digest the attestation binds."""
        with Copy() as ns:
            rewrite(ns / EV / "COMPOSITE_AUDIT.json", lambda o: o["halves"]["successor"]["pairs"].pop("325"))
            V.write_records(ns)
            problems = V.verify(ns)
            self.assertTrue(any("SUCCESSOR_UNIVERSE_IS_NOT_128_325" in x for x in problems), problems[:3])
            self.assertTrue(any("CANONICAL_AUDIT_DIGEST_DIFFERS" in x for x in problems), problems[:3])
            self.assertTrue(any("ATTESTATION_DOES_NOT_REBUILD" in x for x in problems), problems[:3])

    def test_attestation_cell_count_downgrade_is_caught(self):
        with Copy() as ns:
            rewrite(ns / EV / "K4_COMPOSITE_ATTESTATION.json", lambda o: o.__setitem__("cells_verified", 325))
            V.write_records(ns)
            problems = V.verify(ns)
            self.assertTrue(any("ATTESTATION_DOES_NOT_REBUILD" in x for x in problems), problems[:3])
            self.assertTrue(any("326_COMPOSITE_CELLS" in x for x in problems), problems[:3])

    def test_export_manifest_record_swap_is_caught(self):
        with Copy() as ns:
            rewrite(ns / EV / "COMPOSITE_EXPORT_MANIFEST.json",
                    lambda o: o["files"].__setitem__("k4_records/aux5_CUSUM_200_256.json", "0" * 64))
            V.write_records(ns)
            self.assertTrue(any("EXPORT_RECORD_NOT_THE_AUDITED_PAIR" in x for x in V.verify(ns)))

    def test_short_export_manifest_is_caught(self):
        with Copy() as ns:
            rewrite(ns / EV / "COMPOSITE_EXPORT_MANIFEST.json",
                    lambda o: (o["files"].pop("k4_records/aux5_CUSUM_0_256.json"), o.__setitem__("cells", 325)))
            V.write_records(ns)
            self.assertTrue(any("IS_NOT_326_RECORDS_0_325" in x for x in V.verify(ns)))

    def test_predecessor_binding_swap_is_caught(self):
        with Copy() as ns:
            rewrite(ns / EV / "PREDECESSOR_BINDING_FINAL.json",
                    lambda o: o["predecessor"].__setitem__("disposition", "COMPLETE"))
            V.write_records(ns)
            self.assertTrue(any("PREDECESSOR_BINDING_CHANGED" in x for x in V.verify(ns)))

    def test_verdict_cannot_claim_recomputed_predecessor_cells(self):
        with Copy() as ns:
            rewrite(ns / V.VERDICT, lambda o: o.__setitem__("predecessor_cells_recomputed", True))
            self.assertTrue(any("DOES_NOT_REBUILD" in x for x in V.verify(ns)))

    def test_external_tree_check_rejects_a_wrong_tree(self):
        with Copy() as ns:
            man = json.loads((ns / EV / "COMPOSITE_EXPORT_MANIFEST.json").read_bytes())
            tree = Path(ns) / "fake_export/k4_records"
            tree.mkdir(parents=True)
            for rel in man["files"]:
                (tree / Path(rel).name).write_bytes(b"{}\n")
            problems = V.verify_export_tree(tree.parent, man)
            self.assertTrue(any("EXPORT_TREE_HASH_DIFFERS" in x for x in problems))
            self.assertTrue(any("EXPORT_TREE_DIGEST_DIFFERS" in x for x in problems))

    def test_git_package_verifies_without_the_external_tree(self):
        self.assertEqual(V.verify(export_tree=None), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
