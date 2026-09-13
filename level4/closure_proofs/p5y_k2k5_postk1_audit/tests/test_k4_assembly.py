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


def cover(det, *, breaks=("0", "1/4", "1/2", "1", "3/2", "2", "5/2"), override=None):
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
    rho, M = F(1, 8), F(1, 100)
    rep = K4.assemble(both(override={0: ((F(-13, 100), F(-12, 100)), (F(-2), -rho * M))}))
    assert rep["per_Dm"]["SR|m=1"]["per_cell"][0]["how"] != "CHAIN_RPRIME_NEGATIVE"


def test_cell_starting_exactly_at_two_is_outside_the_domain():
    # the [2, 5/2] cell is made hopeless; it meets (0,2] only in {2}, which the previous cell already covers
    rep = K4.assemble(both(override={5: ((F(-1), F(1)), (F(-5), F(5)))}))
    assert rep["all_eight_cellwise_certified"] is True
    assert rep["per_Dm"]["SR|m=1"]["cells"] == 5


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


def test_float_and_symbolic_handling():
    recs = both()
    recs[0]["m"]["1"]["M_R2"] = 0.01
    with pytest.raises(K4.AssemblyRefusal):
        K4.assemble(recs, verify_sr_integrity=False)
    recs = both() + [rec("SR", 99, "6", "7", R=(-1, 1), D=(-1, 1), sr_hash=False)]
    recs[-1]["rho"] = ["1/2", "1/1000"]            # symbolic terminal-style cell: never in (0, 2]
    assert K4.assemble(recs, verify_sr_integrity=False)["all_eight_cellwise_certified"] is True


def test_sealed_record_path_verifies_hashes(tmp_path):
    sealed = tmp_path / "cells"
    sealed.mkdir()
    for r in cover("SR"):
        t4p = tmp_path / f"t4_{r['cell']:04d}.json"
        t4p.write_text(json.dumps(r))
        (sealed / f"{r['cell']:04d}.json").write_text(json.dumps(
            {"cell_id": r["cell"], "evidence": {"t4": {"path": str(t4p), "sha256": hashlib.sha256(t4p.read_bytes()).hexdigest()}}}))
    assert len(K4.load_sr_sealed(sealed)) == 6
    (tmp_path / "t4_0002.json").write_text(json.dumps(dict(cover("SR")[2], cell=2, extra=1)))
    with pytest.raises(K4.AssemblyRefusal, match="hash drift"):
        K4.load_sr_sealed(sealed)


def test_genuine_mode_refuses_without_every_gate(tmp_path):
    d = tmp_path / "recs"
    d.mkdir()
    for i, r in enumerate(both()):
        (d / f"{i:03d}.json").write_text(json.dumps(r))
    with pytest.raises(K4.AssemblyRefusal, match="GENUINE mode"):
        K4.main(["--records", str(d), "--out", str(tmp_path / "o.json")])
    assert K4.main(["--records", str(d), "--synthetic", "--out", str(tmp_path / "o.json")]) == 0
    att = tmp_path / "att.json"
    att.write_text(json.dumps({"schema": K4.CUSUM_ATTESTATION_SCHEMA, "cells_verified": 2}))
    with pytest.raises(K4.AssemblyRefusal, match="attestation"):
        K4.check_cusum_attestation(att, [])
    r = both()[0]
    r.pop("SYNTHETIC_FIXTURE_NOT_SCIENCE")
    (d / "999.json").write_text(json.dumps(r))
    with pytest.raises(K4.AssemblyRefusal, match="SYNTHETIC_FIXTURE"):
        K4.main(["--records", str(d), "--synthetic", "--out", str(tmp_path / "o.json")])


def test_checkpoint_binding_is_consistent_when_present():
    if not K4.CHECKPOINT.exists():
        pytest.skip("checkpoint not generated yet")
    spec = json.loads(K4.CHECKPOINT.read_text())
    assert spec["bound_sources"] == {r: K4.sha_file(NS / r) for r in K4.BOUND_SOURCES}
    assert K4.genuine_mode_allowed() is (K4.CHECKPOINT_HASH.exists()
                                         and K4.CHECKPOINT_HASH.read_text().strip() == K4.sha_file(K4.CHECKPOINT))


def test_frozen_geometry_meets_the_cover_precondition():
    """Frozen pre-result geometry only (no certified value)."""
    cells = sorted(json.loads(SR_TABLE.read_text())["cells"], key=lambda c: c["index"])
    dom = [c for c in cells if F(c["left"][1]) == 0 and F(c["left"][0]) < 2]
    assert F(dom[0]["left"][0]) == 0 and F(dom[-1]["right"][0]) >= 2
    assert all(F(a["right"][0]) == F(b["left"][0]) and F(a["right"][1]) == 0 for a, b in zip(dom, dom[1:]))
    assert len(dom) == 295
