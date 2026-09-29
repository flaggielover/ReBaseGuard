"""Gate logic (impl/srk_gate.py, review R1 B2) on constructed certificate objects: every admission rule G1-G6 must
refuse its planted violation, a genuine full cover must yield max-over-sub-blocks of min-over-rungs, and a missing
sub-block must yield None (fallback to TC-T)."""
import copy
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "impl"))
import srk_certify as S  # noqa: E402
import srk_gate as GT  # noqa: E402

GEOM = {"h": "3/1", "k": "1/2"}
CELL = (F(1, 3), F(1, 3) + F(1, 17))


def mk(i, blk, wb, gamma, kernel="whole"):
    c = {"schema": "SRK_CERT/1", "status": "CERTIFIED", "geometry": GEOM, "block": [S.fstr(blk[0]), S.fstr(blk[1])],
         "weight_block": [S.fstr(wb[0]), S.fstr(wb[1])], "e_c": S.fstr((blk[0] + blk[1]) / 2), "hermite_index": i,
         "degree": 8, "kernel": kernel, "Gamma": S.fstr(gamma), "V0": {"0,0": "1/1"}, "V1": {}, "W0": {"0,0": "1/1"},
         "W1": {}}
    c["sha256"] = GT.canonical_sha(c)
    return c


def run():
    wb, subs = S.cell_blocks(*CELL)
    certs, verdicts = [], {}
    for i in (1, 2, 3, 4):
        for j, b in enumerate(subs):
            for rung, g in ((8, F(10 + j + i, 1)), (10, F(9 + j + i, 1))):   # two rungs; min must be taken
                c = mk(i, b, wb, g)
                c["degree"] = rung
                c["sha256"] = GT.canonical_sha(c)
                certs.append(c)
                verdicts[c["sha256"]] = "ACCEPT"
    res = {}
    r = GT.gate(*CELL, GEOM, "whole", certs, verdicts)
    res["genuine_max_of_min"] = all(r.gamma[i] == F(9 + 3 + i) for i in (1, 2, 3, 4)) and not r.report["refused"]
    # missing sub-block -> None
    drop = [c for c in certs if not (c["hermite_index"] == 2 and c["block"][0] == S.fstr(subs[1][0]))]
    r2 = GT.gate(*CELL, GEOM, "whole", drop, verdicts)
    res["missing_subblock_gives_None"] = r2.gamma[2] is None and r2.gamma[1] is not None

    def refused_alone(mut, verd=None, kernel="whole"):
        base = [c for c in certs if not (c["hermite_index"] == 1 and c["block"][0] == S.fstr(subs[0][0]))]
        m = copy.deepcopy([c for c in certs if c["hermite_index"] == 1 and c["block"][0] == S.fstr(subs[0][0])][0])
        mut(m)
        vv = dict(verdicts)
        if verd is not None:
            vv[m["sha256"]] = verd
        else:
            vv[m["sha256"]] = "ACCEPT"
        rr = GT.gate(*CELL, GEOM, kernel, base + [m], vv)
        return rr.gamma[1] is None and len(rr.report["refused"]) == 1

    def resha(f):
        def g(m):
            f(m)
            m["sha256"] = GT.canonical_sha(m)
        return g
    res["G1_sha_tamper"] = refused_alone(lambda m: m.__setitem__("Gamma", "1/1"))
    res["G1_status"] = refused_alone(resha(lambda m: m.__setitem__("status", "NO_CERTIFIED_RUNG")))
    res["G2_geometry"] = refused_alone(resha(lambda m: m.__setitem__("geometry", {"h": "4/1", "k": "1/2"})))
    res["G2_kernel_mismatch"] = refused_alone(resha(lambda m: m.__setitem__("kernel", "taboo")))
    res["G2_kernel_absent"] = refused_alone(resha(lambda m: m.pop("kernel")))
    res["G3_weight_block_small"] = refused_alone(resha(lambda m: m.__setitem__(
        "weight_block", [S.fstr(wb[0]), S.fstr(wb[1] - F(1, 4096))])))
    res["G4_block_not_declared"] = refused_alone(resha(lambda m: (m.__setitem__("block", [S.fstr(subs[0][0]), S.fstr(
        subs[0][1] - F(1, 8192))]), m.__setitem__("e_c", S.fstr((subs[0][0] + subs[0][1] - F(1, 8192)) / 2)))))
    res["G4_e_c_wrong"] = refused_alone(resha(lambda m: m.__setitem__("e_c", S.fstr(subs[0][0]))))
    res["G5_verifier_reject"] = refused_alone(lambda m: None, verd="REJECT")
    res["G5_verifier_missing"] = refused_alone(lambda m: None, verd="")
    res["G6_negative_gamma"] = refused_alone(resha(lambda m: m.__setitem__("Gamma", "-1/1")))
    res["malformed_refused"] = refused_alone(resha(lambda m: m.__setitem__("block", ["x", "y"])))
    # taboo kernel (SRK-T): D_lo is mandatory, divides, and must be valid on the whole cell
    tcerts, tverd = [], {}
    for c in certs:
        t = copy.deepcopy(c)
        t["kernel"] = "taboo"
        t["sha256"] = GT.canonical_sha(t)
        tcerts.append(t)
        tverd[t["sha256"]] = "ACCEPT"

    def refuses(**kw):
        try:
            GT.gate(*CELL, GEOM, "taboo", tcerts, tverd, **kw)
        except ValueError:
            return True
        return False
    dl_ok = {"value": "1/2", "domain": [S.fstr(CELL[0]), S.fstr(CELL[1])]}
    res["taboo_without_D_lo_refused"] = refuses()
    res["taboo_D_lo_nonpositive_refused"] = refuses(d_lo={"value": "0/1", "domain": dl_ok["domain"]})
    res["taboo_D_lo_domain_short_refused"] = refuses(d_lo={"value": "1/2", "domain": [
        S.fstr(CELL[0]), S.fstr(CELL[1] - F(1, 10 ** 6))]})
    res["taboo_D_lo_extra_key_refused"] = refuses(d_lo=dict(dl_ok, note="x"))
    rt = GT.gate(*CELL, GEOM, "taboo", tcerts, tverd, d_lo=dl_ok)
    res["taboo_divides_by_D_lo"] = all(rt.gamma[i] == F(9 + 3 + i) * 2 for i in (1, 2, 3, 4)) and rt.source == "GATE_TABOO"
    try:
        GT.gate(*CELL, GEOM, "whole", certs, verdicts, d_lo=dl_ok)
        res["whole_with_D_lo_refused"] = False
    except ValueError:
        res["whole_with_D_lo_refused"] = True
    rt_big = GT.gate(*CELL, GEOM, "taboo", tcerts, tverd, d_lo={"value": "4/1", "domain": dl_ok["domain"]})
    cm = GT.combine(r, rt_big)
    res["combine_is_indexwise_min"] = all(cm.gamma[i] == min(r.gamma[i], rt_big.gamma[i]) for i in (1, 2, 3, 4)) \
        and cm.source == "GATE_MIN"
    cm2 = GT.combine(r2, rt)
    res["combine_None_is_infinity"] = cm2.gamma[2] == rt.gamma[2]
    try:
        GT.combine(r, GT.GateResult.empty())
        res["combine_refuses_EMPTY"] = False
    except ValueError:
        res["combine_refuses_EMPTY"] = True
    ok = all(res.values())
    return ok, res


if __name__ == "__main__":
    ok, res = run()
    print(res)
    sys.exit(0 if ok else 1)
