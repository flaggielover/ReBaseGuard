"""R4 development tests. Arb tests skip without python-flint (full coverage runs in qualify_r4.py on vultr-02).

    python3 -B tests/test_r4.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
REPO = NS.parents[2]
sys.path.insert(0, str(NS / "code"))

HAVE_FLINT = importlib.util.find_spec("flint") is not None


def phi(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


def q(p, m, z):
    return max(0.0, p + z - 0.5), max(0.0, m - z - 0.5)


class Stdlib(unittest.TestCase):
    def test_registries_pinned_and_authorization_empty(self):
        src = (NS / "code/constants_r4.py").read_text()
        for name in ("REAL_CELL_AUTHORIZATION_REGISTRY_R4.json", "OPERATOR_CERTIFICATES_R4.json"):
            self.assertIn(hashlib.sha256((NS / "config" / name).read_bytes()).hexdigest(), src)
        self.assertEqual(json.loads((NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY_R4.json").read_text())["authorizations"], [])

    def test_certificate_registry_matches_artifacts(self):
        reg = json.loads((NS / "config/OPERATOR_CERTIFICATES_R4.json").read_text())
        self.assertEqual({e["name"] for e in reg["certificates"]}, {"C_o0", "C_e0"})
        for e in reg["certificates"]:
            raw = (REPO / e["artifact"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), e["artifact_sha256"])
            art = json.loads(raw)
            self.assertEqual(art["certified"]["C_upper_bound"], e["value_upper"])
            self.assertGreater(F(art["certified"]["supersolution_margin_lower_bound"]), 0)
        co = next(e for e in reg["certificates"] if e["name"] == "C_o0")
        self.assertLess(F(co["value_upper"]), F(json.loads((NS / "config/FEASIBILITY_CRITERION_R4.json").read_text())["C_o0_R3"]))

    def test_frozen_scale_and_classes(self):
        c = json.loads((NS / "config/FEASIBILITY_CRITERION_R4.json").read_text())
        r3 = json.loads((CP / "p5y_k5_cusum_order3_r3_infrastructure/evidence/qualification_r3/QUALIFICATION_RESULT_R3.json").read_text())
        self.assertEqual(c["S_star"], r3["forecast_S_star"])
        self.assertEqual([x["label"] for x in c["C_o0_classes"]], ["NEAR_NUMERICAL", "MATERIAL", "MODEST", "NO_IMPROVEMENT"])
        self.assertEqual([x["label"] for x in c["transport_classes"]], ["TIGHT", "PROMISING", "MARGINAL", "UNINFORMATIVE"])

    def test_reflection_identity_and_positive_kernel(self):
        """sigma q(x, z) = q(x, -d - z) and phi(z) >= phi(-d - z) for z >= -d/2 (p >= m)."""
        for p, m in ((0.3, 0.1), (2.0, 1.5), (3.5, 0.0), (1.0, 1.0), (4.6, 0.0)):
            d = p - m
            for i in range(41):
                z = (m - 5.5) + i * (11 - p - m) / 40
                a, b = q(p, m, z)
                c, e = q(p, m, -d - z)
                self.assertAlmostEqual(b, c, places=12)
                self.assertAlmostEqual(a, e, places=12)
                if z >= -d / 2:
                    self.assertGreaterEqual(phi(z) - phi(-d - z), -1e-15)
                    self.assertGreaterEqual(a - b, -1e-12)

    def test_mutation_anchors_match_once(self):
        import make_protocol_r4 as MP
        for m in MP.odd_certificate_mutations():
            self.assertEqual((NS / "code/odd_block_certificate.py").read_text().count(m["old"]), 1, m["id"])
        for m in MP.local_r5_mutations():
            self.assertEqual((NS / "code/local_r5.py").read_text().count(m["old"]), 1, m["id"])
        r5 = (CP / "p5y_k5_cusum_order3_r3_infrastructure/code/r5_majorant.py").read_text()
        for m in MP.r5_mutations_r3():
            self.assertEqual(r5.count(m["old"]), 1, m["id"])
        self.assertEqual(len(MP.r5_mutations_r3()), 6)

    def test_fixture_seeds_disjoint_from_r3(self):
        import make_protocol_r4 as MP
        r3 = json.loads((CP / "p5y_k5_cusum_order3_r3_infrastructure/config/QUALIFICATION_PROTOCOL_R3.json").read_text())
        r3_seeds = {f["seed"] for f in r3["first_cell_fixtures"]} | {f["seed"] + 900000 for f in r3["first_cell_fixtures"]}
        for dev in (False, True):
            seeds = {f["seed"] for f in MP.fixtures(dev)}
            self.assertFalse(seeds & r3_seeds)
        self.assertFalse({f["seed"] for f in MP.fixtures(False)} & {f["seed"] for f in MP.fixtures(True)})

    def test_pure_modules_forbidden_imports(self):
        for mod in ("local_r5.py", "first_cell_r4.py", "m5_crosscheck.py"):
            src = (NS / "code" / mod).read_text()
            for bad in ("cusum_layer1", "cusum_layer2", "aux_certifier", "graded_real", "synthetic_real",
                        "resolvent_certificate", "odd_block_certificate", "subprocess", "socket"):
                self.assertIsNone(re.search(rf"^\s*(import|from)\s+{bad}\b", src, re.M), (mod, bad))

    def test_no_module_attribute_assignment(self):
        for f in sorted((NS / "code").glob("*.py")):
            self.assertIsNone(re.search(r"^\s*(ctx|flint|np|numpy)\.\w+\s*=", f.read_text(), re.M), f.name)


@unittest.skipUnless(HAVE_FLINT, "python-flint not installed")
class Arb(unittest.TestCase):
    def test_local_r5_refuses_missing_inputs(self):
        import local_r5 as LR
        from flint import arb
        with self.assertRaises(LR.LocalR5Refusal):
            LR.local_tower({"C": arb(1)}, {"F:0:0": (arb(1), arb(1))}, {}, x1=arb(0))

    def test_real_entry_refuses(self):
        import constants_r4 as K4
        with self.assertRaises(K4.R4Refusal):
            K4.certify_real_cell_r4(0)


if __name__ == "__main__":
    unittest.main()
