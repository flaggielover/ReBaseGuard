"""REVIEW_THEOREM_MB_R1 scratch (reviewMB): NON-RIGOROUS float sanity checks of Theorem M at declared non-target
drifts only: {0, 1/4, 1/2, 1, 11/10, 27/10, 3, 7/2}. guard_drift is called on every drift before any evaluation.

Kernel: K = 1/2, H = 5, C = 11/2, z = r - e with r ~ N(0,1), window A(x) = [m - C, C - p], T(x,z) = ((p+z-K)+, (m-z-K)+).

  N1  exact n = 1 alarm probability a1_x(e) = Phi_c(C - p0 + e) + Phi(m0 - C + e), starts: atom, diagonal (1,1),(2,2),
      off-diagonal (1,0),(5/2,0),(5,0),(2,1). Monotone detector along increasing e: survival must be nonincreasing.
  N2  n = 2 alarm probability by composite Gauss-Legendre over z1 (split at the clip kinks), same starts/detector.
  N3  derivative of P_x(tau > n) at e = 0 for n = 1 (closed form) and n = 2 (differentiated integrand; window e-free).
  N4  Monte Carlo E[tau] from the atom with common random numbers: paired differences between consecutive drifts,
      reported ONLY as z-scores and signs (no atom ARL value is written anywhere, per quarantine T1/T2).
  N5  Monte Carlo evenness failure off the diagonal: E_(5,0)[tau] vs E_(0,5)[tau] at e = 1/4 (= E_(5,0) at -1/4 by
      the reflection (z,e,p,m) -> (-z,-e,m,p)); and the same pair from the atom and from (2,2) as controls.
"""
from __future__ import annotations

import json
import math
import random
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
sys.path.insert(0, str(NS / "code"))
import c308_quarantine as Q  # noqa: E402

Q.install_import_guard()

DRIFTS = [Fr(0), Fr(1, 4), Fr(1, 2), Fr(1), Fr(11, 10), Fr(27, 10), Fr(3), Fr(7, 2)]
for _d in DRIFTS:
    Q.guard_drift(_d)
EF = [float(d) for d in DRIFTS]
K, H = 0.5, 5.0
C = H + K
SQ2 = math.sqrt(2.0)
STARTS = {"atom": (0.0, 0.0), "diag(1,1)": (1.0, 1.0), "diag(2,2)": (2.0, 2.0),
          "off(1,0)": (1.0, 0.0), "off(5/2,0)": (2.5, 0.0), "off(5,0)": (5.0, 0.0), "off(2,1)": (2.0, 1.0)}


def Phi(x):
    return 0.5 * math.erfc(-x / SQ2)


def Phic(x):
    return 0.5 * math.erfc(x / SQ2)


def phi(x):
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def a1(p, m, e):
    """one-step alarm probability from (p, m) at drift e (z = r - e, r ~ N(0,1))."""
    return Phic(C - p + e) + Phi(m - C + e)


def da1(p, m, e):
    return -phi(C - p + e) + phi(m - C + e)


# Gauss-Legendre nodes (n = 20) computed by Newton iteration (stdlib only)
def gauss_legendre(n):
    xs, ws = [], []
    for i in range(1, n + 1):
        x = math.cos(math.pi * (i - 0.25) / (n + 0.5))
        for _ in range(100):
            p0, p1 = 1.0, x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            dp = n * (x * p1 - p0) / (x * x - 1)
            dx = p1 / dp
            x -= dx
            if abs(dx) < 1e-16:
                break
        xs.append(x)
        ws.append(2 / ((1 - x * x) * dp * dp))
    return xs, ws


GX, GW = gauss_legendre(20)


def integrate(f, a, b, pieces=400):
    tot = 0.0
    h = (b - a) / pieces
    for j in range(pieces):
        lo = a + j * h
        c, r = lo + h / 2, h / 2
        tot += r * sum(w * f(c + r * x) for x, w in zip(GX, GW))
    return tot


def a2(p0, m0, e, deriv=False):
    """P(alarm by step 2) (or its e-derivative) from (p0, m0)."""
    lo, hi = m0 - C, C - p0
    kinks = sorted(k for k in (K - p0, m0 - K) if lo < k < hi)
    pts = [lo] + kinks + [hi]

    def g(z):
        p1, m1 = max(0.0, p0 + z - K), max(0.0, m0 - z - K)
        if not deriv:
            return phi(z + e) * a1(p1, m1, e)
        return -(z + e) * phi(z + e) * a1(p1, m1, e) + phi(z + e) * da1(p1, m1, e)

    s = sum(integrate(g, a, b) for a, b in zip(pts, pts[1:]))
    return (da1(p0, m0, e) if deriv else a1(p0, m0, e)) + s


def monotone_violations(vals):
    """survival must be nonincreasing along increasing e  <=>  alarm probability nondecreasing."""
    return [(EF[i], EF[i + 1]) for i in range(len(vals) - 1) if vals[i + 1] < vals[i] * (1 - 1e-12) - 1e-300]


def mc_tau(p0, m0, e, rng, cap=200000):
    p, m = p0, m0
    for n in range(1, cap + 1):
        z = rng.gauss(0.0, 1.0) - e
        up, um = p + z - K, m - z - K
        if up > H or um > H:
            return n
        p, m = max(0.0, up), max(0.0, um)
    return cap


def main():
    out = {"drifts": [str(d) for d in DRIFTS], "note": "NON-RIGOROUS float sanity checks; non-target drifts only"}
    # N1, N2
    for n, fun in ((1, lambda s, e: a1(*STARTS[s], e)), (2, lambda s, e: a2(*STARTS[s], e))):
        res = {}
        for s in STARTS:
            vals = [fun(s, e) for e in EF]
            viol = monotone_violations(vals)
            res[s] = {"violations": len(viol), "violating_pairs": viol}
            if s.startswith("off"):
                res[s]["alarm_prob_by_drift"] = vals
        out[f"N{n}_alarm_by_step_{n}"] = res
    # N3 derivatives at e = 0 of the SURVIVAL probability (= minus the alarm derivative)
    out["N3_dsurvival_de_at_0"] = {s: {"n1": -da1(*STARTS[s], 0.0), "n2": -a2(*STARTS[s], 0.0, deriv=True)}
                                   for s in STARTS}
    # N4 MC from the atom, common random numbers across drifts (seed per path)
    Npaths = 3000
    diffs = [[] for _ in range(len(EF) - 1)]
    for i in range(Npaths):
        taus = [mc_tau(0.0, 0.0, e, random.Random(1_000_003 * i + 17)) for e in EF]
        for j in range(len(EF) - 1):
            diffs[j].append(taus[j] - taus[j + 1])
    zs = []
    for j, d in enumerate(diffs):
        mu = sum(d) / len(d)
        sd = math.sqrt(sum((x - mu) ** 2 for x in d) / (len(d) - 1))
        zs.append({"pair": [str(DRIFTS[j]), str(DRIFTS[j + 1])], "z_E_lower_minus_E_higher": mu / (sd / math.sqrt(len(d)))})
    out["N4_atom_MC_paired_z"] = {"paths": Npaths, "pairs": zs,
                                  "all_positive_beyond_3SE": all(z["z_E_lower_minus_E_higher"] > 3 for z in zs)}
    # N5 evenness failure off the diagonal, e = 1/4 only
    e = 0.25
    res5 = {}
    for name, (a, b) in {"off(5,0)_vs_(0,5)": ((5.0, 0.0), (0.0, 5.0)), "diag(2,2)_vs_itself_mirror": ((2.0, 2.0), (2.0, 2.0)),
                         "atom_vs_atom": ((0.0, 0.0), (0.0, 0.0))}.items():
        N = 4000 if name.startswith("off") else 1500
        t1 = [mc_tau(a[0], a[1], e, random.Random(7 * i + 1)) for i in range(N)]
        t2 = [mc_tau(b[0], b[1], e, random.Random(7 * i + 3)) for i in range(N)]
        m1, m2 = sum(t1) / N, sum(t2) / N
        v1 = sum((x - m1) ** 2 for x in t1) / (N - 1)
        v2 = sum((x - m2) ** 2 for x in t2) / (N - 1)
        zval = (m1 - m2) / math.sqrt(v1 / N + v2 / N)
        rec = {"paths_each": N, "z": zval}
        if name.startswith("off"):
            rec.update({"mean_first": m1, "mean_mirror": m2})
        res5[name] = rec
    out["N5_evenness_e_1_4"] = res5
    print(json.dumps(out, indent=1))
    (HERE / "out_t5_theorem_m.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    Q.log_event("reviews/scratch_MB_R1/t5_theorem_m_numerics.py",
                "REVIEW_THEOREM_MB_R1 T5: non-rigorous Theorem M sanity checks (exact n=1, quadrature n=2, derivatives "
                "at e=0, MC paired z-scores from the atom, MC evenness failure off-diagonal)",
                klass="REVIEW", agent="reviewMB",
                notes="declared drifts {0,1/4,1/2,1,11/10,27/10,3,7/2} only, guard_drift called; atom ARL values not "
                      "written (z-scores/signs only); no cell id, no tail file, no juxtaposition")


if __name__ == "__main__":
    main()
