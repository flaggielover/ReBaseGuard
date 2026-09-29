"""Port identity: srk_kernel with Geom(5, 1/2) must reproduce the pinned C1b kernel exactly (G-forms and
box enclosures) on fixed random dyadic polynomials, for j in {0,1,2}, taboo and whole kernel."""
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "impl"))
import srk_kernel as KX  # noqa: E402
C1B = HERE.parents[1] / "p5y_k5_tail_overnight_research" / "streams" / "C_308" / "LR" / "cusum"
sys.path.insert(0, str(C1B))
import c1b_kernel as CK  # noqa: E402


def rand_poly(rng, deg):
    P = {}
    for a in range(deg + 1):
        for b in range(deg + 1 - a):
            P[(a, b, 0)] = F(rng.randint(-2 ** 12, 2 ** 12), 2 ** rng.randint(0, 14))
    return {k: v for k, v in P.items() if v}


def run():
    rng = random.Random(20260929)
    g = KX.REAL
    ok = True
    n = 0
    for deg in (0, 2, 5):
        P = rand_poly(rng, deg)
        for j in (0, 1, 2):
            for whole in (False, True):
                a = KX.kernel_gf(g, P, j, whole)
                b = CK.kernel_gf(P, j, whole)
                ok &= (a == b)
                n += 1
                if a == b and j == 0:
                    # enclosure identity on a few boxes, drift block around e = 1/4 (out of band)
                    Ai = KX.pair_to_int(a)
                    Bi = CK.pair_to_int(b)
                    for box in KX.base_cover(g, F(1, 2))[:6] + KX.base_cover(g, F(1, 2))[-2:]:
                        for reg in KX.regions_of_box(g, box):
                            x = KX.gf_box_int(g, Ai[reg], (box[0], box[1], F(1, 4)), (box[2], box[3], F(1, 64)))
                            y = CK.gf_box_int(Bi[reg], (box[0], box[1], F(1, 4)), (box[2], box[3], F(1, 64)))
                            ok &= (x == y)
                            n += 1
    return ok, n


if __name__ == "__main__":
    ok, n = run()
    print({"identical": ok, "comparisons": n})
    sys.exit(0 if ok else 1)
