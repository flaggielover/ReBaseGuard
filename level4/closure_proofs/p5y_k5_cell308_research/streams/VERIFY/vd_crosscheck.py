"""Stream D: agreement tests between the two rigorous evaluators (vd_verify vs vd_point).

(1) special functions: Phi, phi enclosures of both implementations must intersect at 2000 random dyadic points in
    [-10, 10] (plus 0 and +-1/2), widths reported;
(2) residual r(x) = W(x) - 1 - K_e W(x) for every stored certificate at its drift, at the structural points
    (atom, t = 1, 2, 3, 4 on and off the axes, (5,0), (0,5), strip boundaries) and 40 random rational points of R,
    with and without the atom window: the two enclosures must intersect.  vd_verify uses the region bookkeeping and the
    moment recurrence; vd_point finds breakpoints generically and integrates by antiderivatives, so this tests the
    piece logic as well as the arithmetic.
Output: results/CROSSCHECK.json.
"""
from __future__ import annotations

import json
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_verify as V  # noqa: E402
import vd_point as P  # noqa: E402
import vd_adapt as AD  # noqa: E402

Q = V.Q


def meet(a, b) -> bool:
    return not (a[1] < b[0] or b[1] < a[0])


def special(n=2000, seed=5) -> dict:
    rng = random.Random(seed)
    pts = [F(0), F(1, 2), F(-1, 2)] + [F(rng.randint(-10 * 2 ** 20, 10 * 2 ** 20), 2 ** 20) for _ in range(n)]
    bad, wmax = [], F(0)
    for x in pts:
        xi = V.ifr(x)
        assert xi[0] == xi[1]
        a = V.Phi_point(xi[0]); a = (F(a[0], V.ONE), F(a[1], V.ONE))
        b = V.phi_point(xi[0]); b = (F(b[0], V.ONE), F(b[1], V.ONE))
        c, d = P.Phi(x), P.phi(x)
        wmax = max(wmax, a[1] - a[0], b[1] - b[0])
        if not (meet(a, c) and meet(b, d)):
            bad.append(str(x))
    return {"points": len(pts), "disagreements": bad, "max_width_vd_verify": wmax}


def residuals(seed=7, n_random=40) -> list:
    rng = random.Random(seed)
    out = []
    for path in sorted((HERE / "certs").glob("CERT_*.json")):
        obj = json.loads(path.read_text())
        e = F(obj["drift"])
        W = AD.from_c1b_raw(obj["c1b_raw"])
        Wp = P.PW(W.to_json())
        pts = [(F(0), F(0)), (F(1), F(0)), (F(0), F(1)), (F(1, 2), F(1, 2)), (F(2), F(0)), (F(1), F(1)),
               (F(3, 2), F(3, 2)), (F(3), F(0)), (F(2), F(2)), (F(4), F(0)), (F(0), F(4)), (F(5), F(0)), (F(0), F(5)),
               (F(9, 2), F(0)), (F(0), F(19, 4)), (F(1, 3), F(2, 3)), (F(7, 3), F(5, 3))]
        while len(pts) < 17 + n_random:
            p, m = F(rng.randint(0, 500), 100), F(rng.randint(0, 500), 100)
            if rng.random() < 0.15:
                m = F(0)
            if V.in_R(p, m):
                pts.append((p, m))
        bad = []
        for omit in (False, True):
            pre = V.Prep(W, e, omit_atom=omit)
            for p, m in pts:
                a = V.residual_point(pre, p, m)
                b = P.residual(Wp, e, p, m, omit)
                if not meet(a, b):
                    bad.append([str(p), str(m), omit])
        out.append({"certificate": path.name, "points": len(pts), "variants": 2, "disagreements": bad})
    return out


if __name__ == "__main__":
    Q.log_event("streams/VERIFY/vd_crosscheck.py", "agreement of the two rigorous evaluators (special functions and "
                "pointwise residuals) at declared non-target drifts 1/2, 1, 3, 7/2", klass="NONTARGET_DRIFT_VALIDATION",
                agent="streamD")
    t0 = time.time()
    s = special()
    r = residuals()
    doc = {"schema": "VD_CROSSCHECK/1", "special_functions": s, "residuals": r,
           "all_agree": not s["disagreements"] and all(not x["disagreements"] for x in r),
           "seconds": round(time.time() - t0, 1)}
    (HERE / "results" / "CROSSCHECK.json").write_text(json.dumps(V.jsonable(doc), indent=1) + "\n")
    print(json.dumps(V.jsonable({"all_agree": doc["all_agree"], "special": {k: s[k] for k in ("points", "disagreements")},
                                 "max_width": float(s["max_width_vd_verify"]),
                                 "residual_points": sum(x["points"] * 2 for x in r), "seconds": doc["seconds"]})))
