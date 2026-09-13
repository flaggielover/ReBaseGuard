"""Synthetic-only tests for the K4 assembly. No genuine or certified record is read for its values."""
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import k4_assembly as K4  # noqa: E402

SR_TABLE = NS.parent / "p5y_k1_sr_o9_partition_successor/config/successor_cells.json"


def iv(lo, hi):
    return {"lo": str(F(lo)), "hi": str(F(hi)), "mag": str(max(abs(F(lo)), abs(F(hi)))), "encoding": "outward exact rational endpoints"}


def rec(det, idx, left, right, *, R, D, M="1/100", sr_hash=True):
    left, right = F(left), F(right)
    e0, rho = (left + right) / 2, (right - left) / 2
    m = {k: {"detector": det, "R_interval": iv(*R), "D_interval": iv(*D), "M_R2": str(F(M))} for k in K4.M_SCOPE}
    r = {"SYNTHETIC_FIXTURE_NOT_SCIENCE": True, "cell": idx, "e0": [str(e0), "0/1"], "rho": [str(rho), "0/1"], "m": m}
    if det == "SR" and sr_hash:
        r["t4_record_sha256"] = hashlib.sha256(K4.t4_canonical(r)).hexdigest()
    return r


def cover(det, *, breaks=("0", "1/4", "1/2", "1", "3/2", "2", "5/2"), near=None, far=None, override=None):
    """R ~ -e with R' ~ -1 near 0 (chain), then clearly negative R."""
    out = []
    for k, (a, b) in enumerate(zip(breaks, breaks[1:])):
        mid = (F(a) + F(b)) / 2
        R = (-mid - F(1, 100), -mid + F(1, 100))
        D = (F(-11, 10), F(-9, 10)) if F(b) <= F(1, 2) else (F(1, 10), F(3, 10))
        if override and k in override:
            R, D = override[k]
        out.append(rec(det, k, a, b, R=R, D=D))
    return out


def both(**kw):
    return cover("SR", **kw) + cover("CUSUM", **kw)


def test_chain_then_direct_certifies_all_eight():
    rep = K4.assemble(both())
    assert rep["all_eight_cellwise_certified"] is True and rep["verdict_issued"] is False
    per = rep["per_Dm"]["SR|m=1"]
    assert [c["how"] for c in per["per_cell"][:2]] == ["CHAIN_RPRIME_NEGATIVE"] * 2
    assert per["chain_certifies_up_to"] == "1/2"


def test_cell_at_zero_needs_the_chain_not_a_direct_enclosure():
    # R' not certified negative on the first cell: R_cell must straddle 0 there -> too loose, never a counterexample
    rep = K4.assemble(both(override={0: ((F(-13, 100), F(-12, 100)), (F(-11, 10), F(2, 10)))}))
    per = rep["per_Dm"]["CUSUM|m=3"]
    assert per["outcome"] == "K4_CERTIFICATE_TOO_LOOSE" and per["too_loose_cells"] == [0]


def test_width_failure_is_too_loose_not_counterexample():
    rep = K4.assemble(both(override={3: ((F(-1, 10), F(1, 10)), (F(-1), F(1)))}))
    assert rep["per_Dm"]["SR|m=5"]["outcome"] == "K4_CERTIFICATE_TOO_LOOSE"
    assert rep["per_Dm"]["SR|m=5"]["counterexample_cells"] == []


def test_certified_positive_midpoint_is_counterexample():
    rep = K4.assemble(both(override={4: ((F(1, 100), F(2, 100)), (F(1, 10), F(2, 10)))}))
    assert rep["per_Dm"]["SR|m=2"]["outcome"] == "K4_MATHEMATICAL_COUNTEREXAMPLE"


def test_strict_inequality_at_zero_boundary():
    # Rprime_cell.hi == 0 exactly (D.hi + rho*M == 0) must not chain
    rho, M = F(1, 8), F(1, 100)
    rep = K4.assemble(both(override={0: ((F(-13, 100), F(-12, 100)), (F(-2), -rho * M))}))
    assert rep["per_Dm"]["SR|m=1"]["per_cell"][0]["how"] != "CHAIN_RPRIME_NEGATIVE"


@pytest.mark.parametrize("breaks", [("1/100", "1", "2", "3"), ("0", "1", "3/2"), ("0", "1/2", "3/4", "2", "3")])
def test_cover_gaps_refused(breaks):
    recs = cover("SR", breaks=breaks) + cover("CUSUM")
    if breaks == ("0", "1/2", "3/4", "2", "3"):
        recs = [r for r in recs if not (r["cell"] == 1 and r["m"]["1"]["detector"] == "SR")]
    assert K4.assemble(recs)["per_Dm"]["SR|m=1"]["outcome"] == "K4_COVER_GAP"


def test_missing_detector_is_scope_incomplete():
    rep = K4.assemble(cover("SR"))
    assert rep["per_Dm"]["CUSUM|m=1"]["outcome"] == "K4_SCOPE_INCOMPLETE" and not rep["all_eight_cellwise_certified"]


def test_tampered_sr_record_refused():
    recs = both()
    recs[2]["m"]["1"]["R_interval"]["hi"] = "-1/1000"
    with pytest.raises(K4.AssemblyRefusal, match="t4_record_sha256"):
        K4.assemble(recs)


def test_float_and_symbolic_refused():
    recs = both()
    recs[0]["m"]["1"]["M_R2"] = 0.01
    with pytest.raises(K4.AssemblyRefusal):
        K4.assemble(recs, verify_sr_integrity=False)
    recs = both()
    recs[1]["rho"] = ["1/8", "1/1000"]
    with pytest.raises(K4.AssemblyRefusal, match="symbolic"):
        K4.assemble(recs, verify_sr_integrity=False)


def test_genuine_mode_locked_and_synthetic_mode_rejects_unstamped(tmp_path):
    assert not K4.CHECKPOINT_HASH.exists() and K4.genuine_mode_allowed() is False
    d = tmp_path / "recs"
    d.mkdir()
    for i, r in enumerate(both()):
        (d / f"{i:03d}.json").write_text(json.dumps(r))
    with pytest.raises(K4.AssemblyRefusal, match="GENUINE mode locked"):
        K4.main(["--records", str(d), "--out", str(tmp_path / "o.json")])
    assert K4.main(["--records", str(d), "--synthetic", "--out", str(tmp_path / "o.json")]) == 0
    r = both()[0]
    r.pop("SYNTHETIC_FIXTURE_NOT_SCIENCE")
    (d / "999.json").write_text(json.dumps(r))
    with pytest.raises(K4.AssemblyRefusal, match="SYNTHETIC_FIXTURE"):
        K4.main(["--records", str(d), "--synthetic", "--out", str(tmp_path / "o.json")])


def test_frozen_sr_geometry_meets_the_cover_precondition():
    """Frozen pre-result geometry only (no certified value): PS1 cells meeting (0,2] are contiguous from 0 to >= 2."""
    cells = sorted(json.loads(SR_TABLE.read_text())["cells"], key=lambda c: c["index"])
    dom = [c for c in cells if F(c["left"][1]) == 0 and F(c["left"][0]) <= 2]
    assert F(dom[0]["left"][0]) == 0 and F(dom[-1]["right"][0]) >= 2
    assert all(F(a["right"][0]) == F(b["left"][0]) and F(a["right"][1]) == 0 for a, b in zip(dom, dom[1:]))
    assert len(dom) == 295
