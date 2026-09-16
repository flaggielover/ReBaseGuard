"""R3 development tests. Arb tests skip without python-flint (full coverage runs in qualify_r3.py on vultr-02).

    python3 -B tests/test_r3.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import unittest
from fractions import Fraction as F
from math import factorial
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
sys.path.insert(0, str(NS / "code"))

HAVE_FLINT = importlib.util.find_spec("flint") is not None
CUBIC = [F(-15), F(45), F(-15), F(1)]
HE6 = [F(-15), F(0), F(45), F(0), F(-15), F(0), F(1)]


def he(n):
    a, b = [F(1)], [F(0), F(1)]
    if n == 0:
        return a
    for k in range(1, n):
        c = [F(0)] + b
        for i, x in enumerate(a):
            c[i] -= k * x
        a, b = b, c
    return b


class Stdlib(unittest.TestCase):
    def test_registries_pinned_and_authorization_empty(self):
        src = (NS / "code/graded_real.py").read_text()
        for name in ("REAL_CELL_AUTHORIZATION_REGISTRY_R3.json", "OPERATOR_CERTIFICATES_R3.json"):
            self.assertIn(hashlib.sha256((NS / "config" / name).read_bytes()).hexdigest(), src)
        self.assertEqual(json.loads((NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY_R3.json").read_text())["authorizations"], [])

    def test_certificate_registry_matches_artifacts(self):
        reg = json.loads((NS / "config/OPERATOR_CERTIFICATES_R3.json").read_text())
        names = set()
        for e in reg["certificates"]:
            raw = (NS / e["artifact"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), e["artifact_sha256"])
            art = json.loads(raw)
            self.assertEqual(art["name"], e["name"])
            self.assertEqual(art["certified"]["C_upper_bound"], e["value_upper"])
            self.assertGreater(F(art["certified"]["supersolution_margin_lower_bound"]), 0)
            self.assertGreaterEqual(F(art["certified"]["w_min_lower_bound"]), 0)
            names.add(e["name"])
        self.assertEqual(names, {"C_o0", "C_e0"})

    def test_he6_recurrence_and_cubic_substitution(self):
        self.assertEqual(he(6), HE6)
        self.assertEqual(he(6)[0::2], CUBIC)                      # He_6(x) = c(x^2)
        roots = [F(0), F(1), F(5), F(15)]
        changes = sum(1 for a, b in zip(roots, roots[1:])
                      if (sum(c * a ** i for i, c in enumerate(CUBIC)) < 0) != (sum(c * b ** i for i, c in enumerate(CUBIC)) < 0))
        self.assertEqual(changes, 3)                              # three positive roots of c: six real roots of He_6

    def test_evenness_transport_on_exact_odd_polynomial(self):
        coeffs = [F(0), F(3), F(0), F(-7, 3), F(0), F(11, 5), F(0), F(-13, 7), F(0), F(2)]
        d = lambda n, e: sum((F(factorial(p), factorial(p - n)) * coeffs[p] * e ** (p - n) for p in range(n, 10)), F(0))
        x1 = F(1, 3)
        sup5 = sum((F(factorial(p), factorial(p - 5)) * abs(coeffs[p]) * x1 ** (p - 5) for p in range(5, 10)), F(0))
        self.assertEqual(d(4, F(0)), 0)
        for i in range(31):
            e = x1 * F(i, 30)
            self.assertGreaterEqual(d(3, e), d(3, F(0)) - e * e / 2 * sup5)

    def test_mutation_anchors_match_once(self):
        sys.path.insert(0, str(NS / "code"))
        import make_protocol_r3 as MP
        files = {"RW": "graded_real.py", "B0": "r5_majorant.py", "CM": "resolvent_certificate.py"}
        for m in MP.wiring_mutations() + MP.r5_mutations() + MP.certificate_mutations():
            src = (NS / "code" / files[m["id"][:2]]).read_text()
            self.assertEqual(src.count(m["old"]), 1, m["id"])

    def test_pure_modules_forbidden_imports(self):
        for mod in ("r5_majorant.py", "first_cell.py"):
            src = (NS / "code" / mod).read_text()
            for bad in ("cusum_layer1", "cusum_layer2", "aux_certifier", "graded_real", "synthetic_real",
                        "resolvent_certificate", "subprocess", "socket"):
                self.assertIsNone(re.search(rf"^\s*(import|from)\s+{bad}\b", src, re.M), (mod, bad))


@unittest.skipUnless(HAVE_FLINT, "python-flint not installed")
class Arb(unittest.TestCase):
    def test_strategy_b_bounds_widen_by_penalty(self):
        import r5_majorant as R5
        from flint import arb
        lo, hi = R5.strategy_b_bounds((F(1), F(2)), F(1, 10), arb(400))
        self.assertEqual((lo, hi), (F(-1), F(4)))

    def test_first_cell_manufactured_sound(self):
        import first_cell as FC
        r = FC.run({"id": "t", "seed": 777001, "C_target": 10, "x1": "1/20", "noise": "0"})
        self.assertEqual(r["violation_count"], 0, r["violations"])


if __name__ == "__main__":
    unittest.main()
