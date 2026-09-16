"""R2 development tests (seed-disjoint). Arb tests skip without python-flint.

    python3 -B tests/test_r2.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
sys.path.insert(0, str(NS / "code"))
sys.path.append(str(CP / "p5y_k5_cusum_order3_real_producer/code"))

import manufactured_chain as MC  # noqa: E402
import r05_fixture as R05  # noqa: E402
import sigma_systems as SS  # noqa: E402

HAVE_FLINT = importlib.util.find_spec("flint") is not None


class Stdlib(unittest.TestCase):
    def test_r05_fixture_error_path_is_the_source_offset(self):
        spec = {"base_kind": "controlled_K3", "e0": "2/7", "rho": "1/90", "source_offset": "1/400"}
        sysm, e0, rho, rig = R05.build_rig(spec)
        truth = sysm.truth(e0)[("F", 0)][3]
        err = MC.vnorm(MC.vsub(rig.P["G", 0, 0], truth))
        self.assertEqual(err, Fr(1, 400) / (1 - Fr(3, 10)))      # controlled_K3: K(e0) = 3/10, scalar
        _s, _e, _r, rig0 = R05.build_rig(spec, ablation="ABL_ZERO_OFFSET")
        self.assertEqual(MC.vnorm(MC.vsub(rig0.P["G", 0, 0], truth)), 0)
        _s, _e, _r, rigc = R05.build_rig(spec, ablation="ABL_RESOLVE_CLOSED")
        self.assertEqual(MC.vnorm(MC.vsub(rigc.P["G", 0, 0], truth)), 0)

    def test_sigma_system_parity_structure(self):
        s = SS.build({"id": "t", "seed": 424242, "C_target": 7, "deg": 3})
        for p, A in enumerate(s.A):
            self.assertEqual(SS.sig_m(A), [[(-1) ** p * x for x in row] for row in A])
        for p, B in enumerate(s.B):
            self.assertEqual(SS.sig_m(B), [[(-1) ** (p + 1) * x for x in row] for row in B])
        for p, a in enumerate(s.a):
            self.assertEqual(SS.sig_v(a), [(-1) ** p * x for x in a])
        for p, b in enumerate(s.b):
            self.assertEqual(SS.sig_v(b), [(-1) ** (p + 1) * x for x in b])

    def test_true_objects_have_the_derived_parities_at_zero(self):
        s = SS.build({"id": "t", "seed": 434343, "C_target": 6})
        tr = s.truth(Fr(0))
        for r in range(5):
            for n in range(4):
                v = tr[("F", r)][n]
                self.assertEqual(SS.sig_v(v), [(-1) ** (n + 1) * x for x in v])     # F odd, F' even, F'' odd, ...
                if n % 2 == 0:
                    self.assertEqual(v[0], 0)                                      # odd levels vanish at x0

    def test_registries_empty_and_pinned(self):
        src = (NS / "code/cusum_graded.py").read_text()
        for name, key in (("REAL_CELL_AUTHORIZATION_REGISTRY.json", "authorizations"),
                          ("OPERATOR_CERTIFICATE_REGISTRY.json", "certificates")):
            raw = (NS / "config" / name).read_bytes()
            self.assertIn(hashlib.sha256(raw).hexdigest(), src)
            self.assertEqual(json.loads(raw)[key], [])


@unittest.skipUnless(HAVE_FLINT, "python-flint not installed")
class Arb(unittest.TestCase):
    def test_graded_sound_and_never_looser(self):
        import graded_dag as G
        import rung3_engine as R1E
        spec = {"id": "t", "seed": 454545, "C_target": 300}
        gr = SS.GradedRig(SS.build(spec), Fr(3133, 3000000), Fr(3133, 3000000), seed=1, noise=Fr(1, 10 ** 6))
        with R1E.precision(256):
            g = G.certify_graded(gr.engine_inputs(), parity=True)
            s = G.certify_graded(gr.engine_inputs(), parity=False)
        self.assertEqual(SS.graded_violations(gr, g, parity=True), [])
        for m in g["rad_mid"]:
            self.assertLessEqual(R1E.fraction_of(g["rad_mid"][m]), R1E.fraction_of(s["rad_mid"][m]))


if __name__ == "__main__":
    unittest.main(verbosity=1)
