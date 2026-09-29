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
    # BOX-ENVELOPE SOUNDNESS CONTROL (review R1 B4): the envelope must dominate a rigorous LOWER bound of k_i at
    # sample points of box x E (corners and interior); planted wrong-corner mutants must be caught by the same check.
    g = KX.Geom(5, F(1, 2))
    E = (F(1, 4), F(9, 32))
    boxes = [(F(1, 8), F(1, 8), F(1, 8), F(1, 8)), (F(3, 8), F(29, 8), F(1, 8), F(1, 8)),
             (F(29, 8), F(3, 8), F(1, 8), F(1, 8)), (F(35, 8), F(0), F(1, 8), F(0)), (F(0), F(37, 8), F(0), F(1, 8)),
             (F(3, 2), F(3, 2), F(1, 4), F(1, 4))]  # q309: literal-ok (state coordinates (p, m), not drifts)

    def samples(b):
        pc, mc, rp, rm = b
        for dp in (-rp, 0, rp):
            for dm in (-rm, 0, rm):
                for e in (E[0], (E[0] + E[1]) / 2, E[1]):
                    p, m = pc + dp, mc + dm
                    if g.in_X(p, m):
                        yield p, m, e

    def envelope_ok(fn):
        for i in (1, 2, 3, 4):
            for b in boxes:
                top = max(EN.point_k_lower(g, i, p, m, e) for p, m, e in samples(b))
                if fn(g, i, b, *E) < top:
                    return False
        return True

    def mut_p1(g_, i, b, lo, hi):
        pc, mc, rp, rm = b
        return EN.abs_integral_upper(i, (mc - rm) - g_.c + lo, g_.c - (pc + rp) + hi)   # p1 instead of p0

    def mut_elo_for_ehi(g_, i, b, lo, hi):
        pc, mc, rp, rm = b
        return EN.abs_integral_upper(i, (mc - rm) - g_.c + lo, g_.c - (pc - rp) + lo)   # e_lo instead of e_hi

    def mut_m1(g_, i, b, lo, hi):
        pc, mc, rp, rm = b
        return EN.abs_integral_upper(i, (mc + rm) - g_.c + lo, g_.c - (pc - rp) + hi)   # m1 instead of m0

    def mut_ehi_for_elo(g_, i, b, lo, hi):
        pc, mc, rp, rm = b
        return EN.abs_integral_upper(i, (mc - rm) - g_.c + hi, g_.c - (pc - rp) + hi)   # e_hi instead of e_lo
    res["box_envelope_dominates_samples"] = envelope_ok(EN.box_envelope)
    res["mutants_caught"] = {n: not envelope_ok(f) for n, f in (("p1_for_p0", mut_p1), ("elo_for_ehi", mut_elo_for_ehi),
                                                                ("m1_for_m0", mut_m1), ("ehi_for_elo", mut_ehi_for_elo))}
    # monotonicity: enlarging the drift block never decreases the box envelope
    res["monotone"] = all(EN.box_envelope(g, 3, b, F(0), F(1, 2)) >= EN.box_envelope(g, 3, b, F(1, 8), F(3, 8)) for b in boxes)
    ok = (res["sandwich_fail"] == 0 and res["kappa_ok"] and res["monotone"] and res["box_envelope_dominates_samples"]
          and all(res["mutants_caught"].values()))
    return ok, res


if __name__ == "__main__":
    ok, res = run()
    print(res)
    sys.exit(0 if ok else 1)
