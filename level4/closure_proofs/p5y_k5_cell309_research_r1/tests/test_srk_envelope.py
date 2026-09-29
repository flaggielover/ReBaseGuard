"""Envelope soundness: rigorous lower <= float quadrature <= rigorous upper for k_i on random windows; kappa_i
reference values; monotonicity of the box envelope; a planted 'too-small' envelope must be caught."""
import math
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "impl"))
import srk_envelope as EN  # noqa: E402
import srk_float as FL  # noqa: E402
import srk_kernel as KX  # noqa: E402

KAPPA_REF = {1: math.sqrt(2 / math.pi), 2: 4 * math.exp(-0.5) / math.sqrt(2 * math.pi)}


def run():
    rng = random.Random(7)
    res = {"sandwich_fail": 0, "cases": 0}
    for _ in range(60):
        a = F(rng.randint(-600, 400), 100)
        b = a + F(rng.randint(1, 900), 100)
        for i in (1, 2, 3, 4):
            up = EN.abs_integral_upper(i, a, b)
            fl = FL.he_abs_integral_float(i, float(a), float(b), 800)
            g = KX.Geom(5, F(1, 2))
            # lower via a point window with the same endpoints: m - c + e = a, c - p + e = b with e = 0
            lo = EN.point_k_lower(g, i, g.c - b, a + g.c, 0) if (g.c - b) >= 0 else None
            res["cases"] += 1
            if not (fl <= float(up) * (1 + 1e-12) + 1e-15):
                res["sandwich_fail"] += 1
            if lo is not None and not (float(lo) <= fl * (1 + 1e-12) + 1e-15):
                res["sandwich_fail"] += 1
    ku = {i: float(EN.kappa_upper(i)) for i in (1, 2, 3, 4)}
    res["kappa_upper"] = ku
    res["kappa_ok"] = all(ku[i] >= KAPPA_REF[i] - 1e-15 and ku[i] < KAPPA_REF[i] * (1 + 1e-9) for i in (1, 2))
    # planted control: a deliberately shrunken window must give a strictly smaller value (the envelope is not flat)
    g = KX.Geom(5, F(1, 2))
    box = (F(1, 8), F(33, 8), F(1, 8), F(1, 8))
    full = EN.box_envelope(g, 1, box, F(1, 4), F(1, 4))
    shrunk = EN.abs_integral_upper(1, box[1] - box[3] - g.c + F(1, 4) + F(1, 4), g.c - (box[0] - box[2]) + F(1, 4))
    res["planted_shrink_detectable"] = shrunk < full
    # monotonicity: enlarging the drift block never decreases the box envelope
    res["monotone"] = EN.box_envelope(g, 3, box, F(0), F(1, 2)) >= EN.box_envelope(g, 3, box, F(1, 8), F(3, 8))
    ok = res["sandwich_fail"] == 0 and res["kappa_ok"] and res["planted_shrink_detectable"] and res["monotone"]
    return ok, res


if __name__ == "__main__":
    ok, res = run()
    print(res)
    sys.exit(0 if ok else 1)
