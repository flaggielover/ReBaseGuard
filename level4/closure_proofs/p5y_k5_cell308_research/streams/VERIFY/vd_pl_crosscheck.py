"""Stream D: agreement of the two rigorous PL evaluators (vd_pl kink/Psi formula vs vd_point generic breakpoints).

For a sample of stream-A0 C2b certificates (read-only): at every structural point class (atom, t = 1, band
boundaries t = k h, mesh nodes, cell centroids, the axes beyond t = 4, (5,0), (0,5)) and at random rational points
of R, with and without the atom window, the enclosures of W - 1 - K_e W must intersect; the exact values W(x) of the
two independent cell-location codes must be equal.  Output: results/D6_PL_CROSSCHECK.json.
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
import vd_pl as PLm  # noqa: E402
import vd_point as P  # noqa: E402
import vd_verify as V  # noqa: E402

Q = V.Q
A0 = HERE.parent / "A0" / "certs"
SAMPLE = ["C2B_SUPER_e3_N10.json", "C2B_SUB_e1_N10.json", "C2B_SUPER_e11_10_N10.json", "C2B_SUPER_e1_2_N20.json",
          "C2BX_SUPER_e27_10_N20.json", "C2B_SUB_e7_2_N20.json", "C2BX_SUPER_e1_N40.json"]


def points(N: int, rng: random.Random, n_random: int) -> list:
    h = F(1, N)
    pts = [(F(0), F(0)), (F(1), F(0)), (F(0), F(1)), (F(1, 2), F(1, 2)), (F(5), F(0)), (F(0), F(5)),
           (F(4), F(0)), (F(0), F(4)), (F(2), F(2)), (F(9, 2), F(0)), (F(0), F(19, 4)),
           (h / 3, h / 3), (1 + h / 2, F(0)), (F(1, 3), 1 - F(1, 3)), (F(1, 3), 1 - F(1, 3) + h / 7),
           (7 * h + h / 3, 11 * h + h / 3), (7 * h + 2 * h / 3, 11 * h + 2 * h / 3), (3 * h, 5 * h),
           (F(3, 2), F(3, 2) - h / 5), (F(1), F(1) + h), (F(0), 3 * h + h / 2), (13 * h + h / 4, F(0))]
    while len(pts) < 22 + n_random:
        p, m = F(rng.randint(0, 5000), 1000), F(rng.randint(0, 5000), 1000)
        if rng.random() < 0.1:
            m = F(0)
        if V.in_R(p, m):
            pts.append((p, m))
    return pts


def main() -> dict:
    rng = random.Random(17)
    rows = []
    for name in SAMPLE:
        W, cert = PLm.load_a0(A0 / name)
        e = F(cert["drift"])
        Wp = P.make(W.to_json())
        pts = points(W.N, rng, 12 if W.N <= 20 else 6)
        bad, vbad = [], []
        t0 = time.time()
        for omit in (False, True):
            E = PLm.Engine(W, e, omit_atom=omit)
            for p, m in pts:
                a = E.point_residual(p, m)
                b = P.residual(Wp, e, p, m, omit)
                if a[1] < b[0] or b[1] < a[0]:
                    bad.append([str(p), str(m), omit])
                if not omit and W.value(p, m) != Wp.value(p, m):
                    vbad.append([str(p), str(m)])
        rows.append({"certificate": name, "N": W.N, "drift": cert["drift"], "points": len(pts), "variants": 2,
                     "residual_disagreements": bad, "value_disagreements": vbad, "seconds": round(time.time() - t0, 1)})
        print(json.dumps(rows[-1]), flush=True)
    return {"schema": "VD_D6_PL_CROSSCHECK/1", "rows": rows,
            "all_agree": all(not r["residual_disagreements"] and not r["value_disagreements"] for r in rows),
            "evaluations": sum(r["points"] * 2 for r in rows)}


if __name__ == "__main__":
    Q.log_event("streams/VERIFY/vd_pl_crosscheck.py", "agreement of the two rigorous PL evaluators on stream-A0 C2b "
                "certificates (read-only) at declared drifts", klass="NONTARGET_DRIFT_VALIDATION", agent="streamD")
    t0 = time.time()
    doc = main()
    doc["seconds"] = round(time.time() - t0, 1)
    (HERE / "results" / "D6_PL_CROSSCHECK.json").write_text(json.dumps(V.jsonable(doc), indent=1) + "\n")
    print("ALL_AGREE", doc["all_agree"], doc["evaluations"])
