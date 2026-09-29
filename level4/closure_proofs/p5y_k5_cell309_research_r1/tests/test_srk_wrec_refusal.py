"""certify_weight must refuse a W record that is not CERTIFIED or that belongs to another geometry, check block, e_c,
degree or kernel (review R1 B4).  Every refusal happens before any computation; a genuine W record is accepted
(positive control: one degree-8 weight certificate on the declared synthetic decoy h = 3, E = [1/4, 9/32])."""
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "impl"))
import srk_certify as S  # noqa: E402
import srk_kernel as KX  # noqa: E402

G3 = KX.Geom(3, F(1, 2))
LO, HI, D = F(1, 4), F(9, 32), 8


def refused(Wrec, g=G3, lo=LO, hi=HI, d=D) -> bool:
    try:
        S.certify_weight(g, 1, lo, hi, d, Wrec, log=lambda s: None)
    except ValueError:
        return True
    return False


def run():
    W = S.certify_W(G3, LO, HI, D, log=lambda s: None)
    res = {"W_certified": W["status"] == "CERTIFIED"}
    res["not_certified"] = refused(dict(W, status="W_NEGATIVE"))
    res["other_geometry"] = refused(W, g=KX.Geom(4, F(1, 2)))
    res["other_block"] = refused(W, hi=F(17, 64))
    res["other_degree"] = refused(W, d=10)
    res["e_c_tampered"] = refused(dict(W, e_c=LO))
    res["kernel_missing"] = refused({k: v for k, v in W.items() if k != "whole"})
    res["not_a_dict"] = refused(None)
    V = S.certify_weight(G3, 1, LO, HI, D, W, log=lambda s: None)
    res["genuine_accepted"] = V["status"] == "CERTIFIED" and V["Gamma"] > 0
    return all(res.values()), res


if __name__ == "__main__":
    ok, res = run()
    print(res)
    sys.exit(0 if ok else 1)
