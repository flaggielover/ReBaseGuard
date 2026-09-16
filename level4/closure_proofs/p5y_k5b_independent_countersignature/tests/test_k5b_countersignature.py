"""Tests for the independent K5-B countersignature namespace (synthetic, read-only, no scientific compute).

  python -B tests/test_k5b_countersignature.py
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
sys.path.insert(0, str(NS / "code"))

import k5b_check as K  # noqa: E402

THEOREM = "level4/closure_proofs/p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md"


def load(rel):
    return json.loads((NS / rel).read_text())


class HashBinding(unittest.TestCase):
    def test_inventory_hashes_match_repository_bytes(self):
        self.assertEqual(K.verify_hashes(REPO), [])

    def test_countersignature_binds_the_inventory_theorem_hash(self):
        cs, inv = load("COUNTERSIGNATURE.json"), load("config/THEOREM_HASH_INVENTORY.json")
        self.assertEqual(cs["theorem"]["path"], THEOREM)
        self.assertEqual(cs["theorem"]["sha256"], inv["theorem_files"][THEOREM]["sha256"])
        self.assertEqual(cs["theorem"]["sha256"], hashlib.sha256((REPO / THEOREM).read_bytes()).hexdigest())
        for rel, h in cs["bound_namespace_files"].items():
            self.assertEqual(hashlib.sha256((NS / rel).read_bytes()).hexdigest(), h, rel)

    def test_theorem_never_modified_after_introduction(self):
        inv = load("config/THEOREM_HASH_INVENTORY.json")
        for group in ("theorem_files", "premise_files"):
            for rel, h in inv[group].items():
                self.assertEqual(h["commits_touching"], 1, rel)
                self.assertEqual(h["introduced_in"], h["last_modified_in"], rel)


class Verdict(unittest.TestCase):
    def test_verdict_fields_and_non_claims(self):
        cs = load("COUNTERSIGNATURE.json")
        self.assertEqual(cs["K5_B_INDEPENDENT_REVIEW"], "PASS_WITH_SCOPE_LIMITATION")
        self.assertEqual(cs["K5_B_LOGICAL_STATUS"], "SUFFICIENT_ONLY")
        for k in ("ENDPOINT_ARGUMENT", "INTERIOR_CHAIN", "TEMPORAL_INTEGRITY"):
            self.assertEqual(cs[k], "PASS", k)
        self.assertEqual(cs["STRICTNESS_PRESERVED"], "YES")
        self.assertEqual(cs["CIRCULARITY"], "NONE")
        self.assertEqual(cs["M5_TAIL_CLASSIFICATION"], "BOTH")
        nc = cs["non_claims"]
        for k in ("K5_DECLARED_CLOSED", "P5Y_DECLARED_CLOSED", "P5Z_VERDICT_ISSUED", "K5_PRODUCTION_EVIDENCE_GENERATED",
                  "SCIENTIFIC_COMPUTE_RUN", "CUSUM_CLOSURE_MODIFIED", "ORIGINAL_THEOREM_MODIFIED", "AWS_PS1_TOUCHED",
                  "ORIGIN_MAIN_TOUCHED"):
            self.assertIs(nc[k], False, k)
        self.assertIn("does not imply", cs["scope"]["failure_semantics"])


class DependencyDag(unittest.TestCase):
    def test_acyclic_and_no_forbidden_ancestor(self):
        dag = load("evidence/DEPENDENCY_DAG.json")
        nodes, edges = set(dag["nodes"]), dag["edges"]
        self.assertTrue(all(a in nodes and b in nodes for a, b in edges))
        indeg = {n: 0 for n in nodes}
        for _, b in edges:
            indeg[b] += 1
        queue, seen = [n for n, d in indeg.items() if d == 0], 0
        while queue:
            n = queue.pop()
            seen += 1
            for a, b in edges:
                if a == n:
                    indeg[b] -= 1
                    if indeg[b] == 0:
                        queue.append(b)
        self.assertEqual(seen, len(nodes), "cycle in dependency DAG")
        parents = {}
        for a, b in edges:
            parents.setdefault(b, set()).add(a)
        anc, stack = set(), ["K5B_THEOREM"]
        while stack:
            for p in parents.get(stack.pop(), ()):
                if p not in anc:
                    anc.add(p)
                    stack.append(p)
        self.assertFalse(anc & set(dag["forbidden_ancestors_of_K5B_THEOREM"]))


class TheoremLogic(unittest.TestCase):
    def test_symbolic_spine(self):
        self.assertEqual(K.symbolic_spine(random.Random(1), trials=40)["status"], "PASS")

    def test_gamma1_lower_bound_nonnegative_on_first_cell(self):
        rng = random.Random(2)
        for _ in range(40):
            R = K.random_odd_poly(rng)
            cells = K.synthetic_cells(R, K.make_cover(rng), rng, pieces=8, widen=30, l_drop=1.0)
            self.assertGreaterEqual(K.k5b_literal(cells)[0]["Gamma"], 0)

    def test_small_soundness_fuzz(self):
        self.assertEqual(K.soundness_fuzz(random.Random(3), polys=12)["status"], "PASS")

    def test_mutations_are_detected(self):
        self.assertEqual(K.mutation_sensitivity(random.Random(4), polys=20)["status"], "PASS")

    def test_adversarial_cases(self):
        cases = K.adversarial()
        self.assertEqual({k for k, v in cases.items() if not v["ok"]}, set())

    def test_readiness_variant_equivalence_lemma(self):
        self.assertTrue(K.committed_minimality_has_no_positive_Hlo(REPO)["equivalence_lemma_applies"])
        self.assertEqual(K.readiness_scan_agrees(REPO, random.Random(5), trials=8)["status"], "PASS")

    def test_sturm_counts(self):
        p = K.pmul([F(-1), F(0), F(1)], [F(-1), F(0), F(1)])       # (e^2-1)^2: one distinct root in (0,2)
        self.assertEqual(K.distinct_roots_open(p, F(0), F(2)), 1)
        self.assertEqual(K.distinct_roots_open([F(1), F(0), F(1)], F(-5), F(5)), 0)


class EvidenceReproduces(unittest.TestCase):
    def test_committed_evidence_reproduces_bit_for_bit(self):
        ver, adv = K.run(REPO)
        self.assertEqual(json.dumps(ver, indent=1, sort_keys=True) + "\n",
                         (NS / "evidence/INDEPENDENT_VERIFICATION.json").read_text())
        self.assertEqual(json.dumps(adv, indent=1, sort_keys=True) + "\n",
                         (NS / "evidence/ADVERSARIAL_TESTS.json").read_text())


if __name__ == "__main__":
    unittest.main(verbosity=1)
