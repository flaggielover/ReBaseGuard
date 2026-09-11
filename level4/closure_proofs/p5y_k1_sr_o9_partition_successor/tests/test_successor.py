"""Pre-anchor tests. They use only the frozen cell table, candidate construction (T1 proposes, it certifies nothing)
and HISTORICAL T3/T4/T5 evidence of frozen cell 150; no successor scientific result is produced."""
import copy
import hashlib
import json
import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
sys.path.insert(0, str(NS / "code"))

import sr_o9_candidates as T              # noqa: E402
import partition_generator as G           # noqa: E402
import succ_cells as SC                   # noqa: E402
import succ_t1 as S1                      # noqa: E402
import make_successor_stages as MK        # noqa: E402

EV = CP / "p5y_k1_sr_o9_t345_successor/evidence"


class Partition(unittest.TestCase):
    def test_generator_deterministic_and_committed(self):
        b = G.canonical(G.generate())
        self.assertEqual(b, (NS / "config/successor_cells.json").read_bytes())
        self.assertTrue(G.verify(json.loads(b)))

    def test_counts_and_old313(self):
        t = json.loads((NS / "config/successor_cells.json").read_text())
        self.assertEqual(t["n_cells"], 369)
        kids = [c for c in t["cells"] if c["parent_index"] == 313]
        self.assertEqual([c["child"] for c in kids], [0, 1, 2, 3])
        self.assertEqual(kids[0]["left"], T.frozen_cell(313)["left"])
        self.assertEqual(kids[-1]["right"], T.frozen_cell(313)["right"])
        self.assertTrue(t["cells"][-1]["terminal"] and t["cells"][-1]["parent_index"] == 315)

    def test_generator_reads_no_results(self):
        src = (NS / "code/partition_generator.py").read_text()
        body = src.split('"""', 2)[2]
        import re
        hits = re.findall(r"\b(evidence|PASS|FAIL|B_cover|ratio|diag\w*|curvature|kill|t[345]_\w*)\b", body)
        self.assertEqual(hits, [])

    def test_unsplit_geometry_equals_frozen(self):
        with T.scientific_precision():
            for p in (0, 150, 315):
                rec = SC.cells_of_parent(p)[0]
                g, h = SC.geometry(rec), T.cell_geometry(T.frozen_cell(p))
                for k in ("left", "right", "e0", "rho"):
                    self.assertEqual(rec[k], T.frozen_cell(p)[k], (p, k))
                    self.assertTrue(g[k].mid() == h[k].mid() and g[k].rad() == h[k].rad(), (p, k))

    def test_successor_refuses_foreign_records(self):
        rec = SC.cells_of_parent(313)[0]
        bad = dict(rec, rho=["1/10", "0/1"])
        with self.assertRaises(SC.SuccessorCellRefused):
            SC.validate(bad)
        with self.assertRaises(T.CellRefused):
            T.validate_cell(rec)             # the frozen layer still refuses successor records


class Stages(unittest.TestCase):
    def test_generated_stages_reproduce(self):
        a, b = MK.build()
        self.assertEqual(a, (NS / "code/succ_t4.py").read_text())
        self.assertEqual(b, (NS / "code/succ_t5.py").read_text())

    def test_t1_mantissas_equal_frozen_for_unsplit_parent(self):
        rec = SC.cells_of_parent(150)[0]
        s = {c["node"]: c["mantissas"] for c in S1.build(rec)["scientific"]["candidates"]}
        f = {c["node"]: c["mantissas"] for c in T.build_cell_candidates(150)["scientific"]["candidates"]}
        self.assertEqual(s, f)

    def test_t4_t5_regression_on_historical_cell150(self):
        import succ_t4 as S4
        import succ_t5 as S5
        rec = SC.cells_of_parent(150)[0]
        t3 = json.loads((EV / "t3/t3_c150.json").read_text())
        h4 = json.loads((EV / "t4/t4_c150.json").read_text())
        h5 = json.loads((EV / "t5/t5_c150.json").read_text())
        hashes = {c["node"]: c["identity_hash"] for c in S1.build(rec)["scientific"]["candidates"]}
        v = copy.deepcopy(t3)
        v["candidate_identity_list_sha256"] = [hashlib.sha256(T.canonical(sorted(hashes.items()))).hexdigest()]
        v["cell"] = rec["index"]
        r4 = S4.t4(v, rec)
        self.assertEqual(r4["B_cover_ratio"], h4["B_cover_ratio"])
        for m in ("1", "2", "3", "5"):
            for k in ("M_R2", "D_interval_mag", "R_interval_mag"):
                self.assertEqual(r4["m"][m][k], h4["m"][m][k], (m, k))
        r5 = S5.obligations(v, r4, {"regression": True}, rec)
        self.assertEqual(r5["pass_count"], h5["pass_count"])
        self.assertEqual([o["status"] for o in r5["obligations"]], [o["status"] for o in h5["obligations"]])
        self.assertTrue(r5["obligation_ids_equal_frozen_universe"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
