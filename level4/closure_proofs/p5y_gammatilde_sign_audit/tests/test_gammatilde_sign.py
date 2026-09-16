"""The r1 result verifies, the m=2 bound is exact, and the consistency rules refuse over-claims."""
import copy
import json
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))

import verify_gammatilde_sign as V  # noqa: E402

RESULT = json.loads(V.RESULT.read_text())
LIVE = V.build()


def test_result_verifies():
    assert V.consistency_problems(RESULT, LIVE) == []


def test_record_binding_and_crosscheck():
    b = LIVE["binding"]
    assert b["record_sha256_equals_composite_export_manifest"] and b["scientific_content_hash_recomputes"]
    assert LIVE["bound"]["tower_indexing_crosscheck_S0_order3"]
    assert all(LIVE["pins_match"].values())


def test_m2_bound_by_hand():
    rec = json.loads(V.RECORD.read_text())
    e0 = F(rec["e0"][0])
    supF3 = [F(rec["whole_cell_refinement"][str(r)]["second_order"]["supF3_final"]) for r in (0, 1)]
    T00 = F(rec["node_refinement"]["decisions"]["S:0:1"]["tower_next_order"])
    M3 = (supF3[0] + supF3[1]) / 2 + T00 / 2
    Dhi = F(rec["m"]["2"]["D_interval"]["hi"])
    lower = 1 - (Dhi + e0 * e0 / 2 * M3)
    assert lower > 1 and F(RESULT["recomputed"]["bound"]["m"]["2"]["GammaTilde_interval_odd_C3"][0]) == lower


def test_m3_m5_not_certified_and_m1_consistent():
    B = LIVE["bound"]["m"]
    assert not B["3"]["GammaTilde_gt_1_certified_by_odd_C3"] and not B["5"]["GammaTilde_gt_1_certified_by_odd_C3"]
    assert B["1"]["intersects_certified_m1_enclosure"] and B["1"]["GammaTilde_gt_1_certified_by_odd_C3"]
    assert all(B[m]["contains_P1N1_estimate"] for m in B)
    assert not any(B[m]["GammaTilde_gt_1_certified_by_first_order"] for m in ("2", "3", "5"))


def test_overclaims_refused():
    for key, bad in (("GAMMATILDE_GT_1_M3", "CERTIFIED"), ("GAMMATILDE_GT_1_M5", "REFUTED"),
                     ("ALL_CUSUM_M_GAMMATILDE_GT_1", "CERTIFIED"), ("H3A_POSITIVE_BRANCH_PREMISE", "SATISFIED"),
                     ("K5_DECLARED_CLOSED", "YES"), ("SCIENTIFIC_COMPUTE_RUN", "YES")):
        tampered = copy.deepcopy(RESULT)
        tampered["verdicts"][key] = bad
        assert V.consistency_problems(tampered, LIVE), key


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
