"""Tests for the K5 order-3 minimality scan. Synthetic fixtures only: no production record is read or written, no
scientific computation runs, nothing is authorized.

  python -B tests/test_k5_minimality.py
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import k5_minimality as K                                                        # noqa: E402

EVIDENCE = NS / "evidence/CUSUM_MINIMALITY_R1.json"


def cell(index: int, lo: F, hi: F) -> dict:
    e0, rho = (lo + hi) / 2, (hi - lo) / 2
    return {"detector": "CUSUM", "index": index, "left": [str(lo), "0/1"], "right": [str(hi), "0/1"],
            "e0": [str(e0), "0/1"], "rho": [str(rho), "0/1"]}


def record(c: dict, *, R: str, D: str, R2_lo: str, R2_hi: str) -> dict:
    mag = max(abs(F(R2_lo)), abs(F(R2_hi)))
    per_m = {"e0": c["e0"], "rho": c["rho"],
             "R_interval": {"lo": R, "hi": R}, "D_interval": {"lo": D, "hi": D},
             "R2_interval": {"lo": R2_lo, "hi": R2_hi}, "M_R2": str(mag)}
    return {"cell_index": c["index"], "detector": "CUSUM", "m": {m: dict(per_m) for m in K.MS}}


class Fixture:
    """A synthetic cover of `n` unit-step cells with per-cell (R, R', R'') values."""

    def __init__(self, values):
        self.values = values

    def __enter__(self):
        self.d = tempfile.TemporaryDirectory()
        root = Path(self.d.name)
        (root / "records").mkdir()
        cells = []
        x = F(0)
        for i, v in enumerate(self.values):
            step = F(1, 4)
            c = cell(i, x, x + step)
            x += step
            cells.append(c)
            (root / "records" / f"aux5_CUSUM_{i}_256.json").write_text(json.dumps(record(c, **v)))
        (root / "cells.json").write_text(json.dumps(cells))
        return root

    def __exit__(self, *exc):
        self.d.cleanup()


CLOSED = {"R": "-1", "D": "1/10", "R2_lo": "-1/1000", "R2_hi": "1/1000"}          # Gamma < 0: closes directly
OPEN = {"R": "1", "D": "-1", "R2_lo": "-100", "R2_hi": "100"}                     # Gamma > 0 and chain useless


class MinimalityScanTests(unittest.TestCase):
    def test_all_cells_closed_by_the_direct_bound(self):
        with Fixture([CLOSED] * 6) as root:
            rep = K.scan(root / "records", root / "cells.json", "CUSUM")
            self.assertEqual(rep["union_needs_order3"], [])
            self.assertEqual(rep["provably_not_needed_count"], 6)
            self.assertEqual(rep["per_m"]["1"]["closed_by_k1_count"], 6)

    def test_open_prefix_is_reported_as_needing_order3(self):
        with Fixture([OPEN] * 3 + [CLOSED] * 3) as root:
            rep = K.scan(root / "records", root / "cells.json", "CUSUM")
            self.assertEqual(rep["union_needs_order3"], [[0, 2]])
            self.assertEqual(rep["provably_not_needed"], [[3, 5]])
            self.assertTrue(all(r["pass_direct"] is False for r in rep["per_m"]["1"]["boundary_rows"][:1]))

    def test_an_open_cell_after_a_negative_chain_can_still_pass_by_the_chain(self):
        """Once gamma is negative and R'' >= 0 is certified, a cell with Gamma > 0 still passes."""
        chainable = {"R": "1", "D": "-1", "R2_lo": "0", "R2_hi": "1"}
        with Fixture([CLOSED, chainable]) as root:
            rep = K.scan(root / "records", root / "cells.json", "CUSUM")
            self.assertEqual(rep["union_needs_order3"], [])
            row = [r for r in rep["per_m"]["1"]["boundary_rows"] if r["cell"] == 1]
            self.assertTrue(not row or row[0]["pass_chain"])

    def test_positive_R2_lower_bound_is_counted(self):
        with Fixture([CLOSED, {"R": "-1", "D": "1/10", "R2_lo": "1/2", "R2_hi": "1"}]) as root:
            rep = K.scan(root / "records", root / "cells.json", "CUSUM")
            self.assertEqual(rep["per_m"]["1"]["cells_with_R2_interval_lo_positive"], [[1, 1]])

    def test_cover_gap_fails_closed(self):
        with Fixture([CLOSED] * 3) as root:
            cells = json.loads((root / "cells.json").read_text())
            cells[1]["left"] = ["1/2", "0/1"]
            (root / "cells.json").write_text(json.dumps(cells))
            with self.assertRaises(SystemExit):
                K.scan(root / "records", root / "cells.json", "CUSUM")

    def test_record_geometry_mismatch_fails_closed(self):
        with Fixture([CLOSED] * 2) as root:
            p = root / "records/aux5_CUSUM_1_256.json"
            rec = json.loads(p.read_text())
            rec["m"]["1"]["rho"] = ["7/8", "0/1"]
            p.write_text(json.dumps(rec))
            with self.assertRaises(SystemExit):
                K.scan(root / "records", root / "cells.json", "CUSUM")

    def test_mislabelled_record_fails_closed(self):
        with Fixture([CLOSED] * 2) as root:
            p = root / "records/aux5_CUSUM_1_256.json"
            rec = json.loads(p.read_text())
            rec["cell_index"] = 7
            p.write_text(json.dumps(rec))
            with self.assertRaises(SystemExit):
                K.scan(root / "records", root / "cells.json", "CUSUM")

    def test_ranges_round_trip(self):
        self.assertEqual(K.ranges([3, 1, 2, 9]), [[1, 3], [9, 9]])
        self.assertEqual(K.expand([[1, 3], [9, 9]]), [1, 2, 3, 9])

    def test_verify_catches_a_doctored_evidence_file(self):
        with Fixture([OPEN] * 2 + [CLOSED] * 2) as root:
            rep = K.scan(root / "records", root / "cells.json", "CUSUM")
            out = root / "ev.json"
            rep["union_needs_order3"] = []                                       # pretend nothing is needed
            out.write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
            self.assertTrue(any("UNION" in p for p in K.verify(out, None, None)))

    def test_verify_reproduces_from_the_records(self):
        with Fixture([OPEN, CLOSED, CLOSED]) as root:
            rep = K.scan(root / "records", root / "cells.json", "CUSUM")
            out = root / "ev.json"
            out.write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
            self.assertEqual(K.verify(out, root / "records", root / "cells.json"), [])

    @unittest.skipUnless(EVIDENCE.is_file(), "committed CUSUM scan")
    def test_committed_cusum_evidence_is_internally_consistent(self):
        self.assertEqual(K.verify(EVIDENCE, None, None), [])
        ev = json.loads(EVIDENCE.read_bytes())
        self.assertEqual(ev["detector"], "CUSUM")
        self.assertEqual(ev["cells_meeting_domain"], 310)
        self.assertEqual(ev["universe"], [0, 309])
        self.assertEqual(ev["union_needs_order3"], [[0, 148], [305, 309]])
        self.assertEqual(ev["union_needs_order3_count"], 154)
        self.assertEqual(ev["provably_not_needed"], [[149, 304]])
        self.assertEqual({m: v["needs_order3_count"] for m, v in ev["per_m"].items()},
                         {"1": 133, "2": 145, "3": 146, "5": 154})
        for v in ev["per_m"].values():                                           # Z2 never fires on realised widths
            self.assertEqual(v["cells_with_R2_interval_lo_positive_count"], 0)


RECORD = NS / "config/K5_READINESS_RECORD.json"


class ReadinessRecordTests(unittest.TestCase):
    """The audit record must agree with the scan and must claim nothing it has not established."""

    def setUp(self):
        self.rec = json.loads(RECORD.read_bytes())
        self.ev = json.loads(EVIDENCE.read_bytes())

    def test_record_matches_the_scan(self):
        cm = self.rec["cusum_minimality"]
        self.assertEqual(cm["needs_order3_union"], self.ev["union_needs_order3"])
        self.assertEqual(cm["needs_order3_union_count"], self.ev["union_needs_order3_count"])
        self.assertEqual(cm["provably_not_needed"], self.ev["provably_not_needed"])
        self.assertEqual(cm["provably_not_needed_count"], self.ev["provably_not_needed_count"])
        self.assertEqual({m: v for m, v in cm["needs_order3_per_m"].items()},
                         {m: v["needs_order3"] for m, v in self.ev["per_m"].items()})
        self.assertEqual(cm["candidate_cells"], self.ev["cells_meeting_domain"])

    def test_record_authorizes_nothing(self):
        self.assertFalse(any(self.rec["authorizations"].values()))
        self.assertEqual(self.rec["probe_review"]["probes_run"], 0)
        self.assertEqual(self.rec["verdicts"]["k5_full_campaign_recommendation"], "NOT_READY")
        self.assertFalse(self.rec["verdicts"]["full_campaign_technically_ready"])

    def test_record_claims_no_broader_verdict(self):
        blob = json.dumps(self.rec)
        for forbidden in ("K5 CLOSED", "K1 CLOSED", "P5Y CLOSED", "H3A_PROVED", "h3a_proved"):
            self.assertNotIn(forbidden, blob)

    def test_blockers_are_stated_with_their_remedies(self):
        ids = {b["id"] for b in self.rec["blockers"]}
        self.assertEqual(ids, {"B1_NO_CERTIFIED_ORDER3_PRODUCER", "B2_NO_SR_K1_INPUTS",
                               "B3_BRIDGE_NOT_INDEPENDENTLY_COUNTERSIGNED"})
        self.assertTrue(all(b.get("unblocked_by") for b in self.rec["blockers"]))

    def test_frozen_probe_cells_are_recorded_unchanged(self):
        oracle = json.loads((NS.parents[0] / "p5y_k5_feasibility/config/K5_FEASIBILITY_ORACLE.json").read_bytes())
        self.assertEqual(self.rec["probe_review"]["frozen_probe_cells"]["SR"], oracle["probes"]["SR"]["cells"])
        self.assertEqual(self.rec["probe_review"]["frozen_probe_cells"]["CUSUM"], oracle["probes"]["CUSUM"]["cells"])
        self.assertFalse(oracle["executed"])
        self.assertFalse(oracle["full_campaign_authorized"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
