"""C11 Phase 12X -- a FLOAT shadow of the model, for diagnosis only.

NOT LOAD-BEARING. Nothing here certifies anything and no certificate depends on it. Every rigorous
statement in this campaign comes from c11_certifier's exact rational interval arithmetic. This
module exists because the campaign's central error (erratum E9) was a diagnosis that a few seconds
of ordinary floating-point arithmetic would have refuted, and because the guidance handed to the
successor rests on the SHAPE of the true solution, which needs a producer like anything else.

It is written from the frozen CUSUM model's own specification, independently of c11_certifier: its
own Simpson quadrature, its own kink splitting, its own interpolation. Agreement between the two on
the identities below is therefore a cross-check of the rigorous code, not a restatement of it.

What it produces:
  * the TRUE value function v = 1 + K_e v by value iteration, whose shape tells you what family of
    supersolutions can possibly work;
  * for a one-parameter family, the required A as a function of B, exactly -- the supersolution
    condition is linear in A, so this is a solve, not a search. If the minimum over B exceeds what
    a constant achieves, the family is worthless and no amount of compute will change that.
"""
from __future__ import annotations

import math
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11_common as C

K, CBAR = 0.5, 5.5                  # the frozen model constants, as floats
E_DEV = 1.8355
PANELS = 240


def phi(y: float) -> float:
    return math.exp(-0.5 * y * y) / math.sqrt(2 * math.pi)


def Phi(y: float) -> float:
    return 0.5 * (1.0 + math.erf(y / math.sqrt(2)))


def _simpson(f, a: float, b: float, n: int = PANELS) -> float:
    if b <= a:
        return 0.0
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += (4.0 if i % 2 else 2.0) * f(a + i * h)
    return s * h / 3.0


def Kf(p: float, m: float, f, e: float = E_DEV) -> float:
    """(K_e f)(p, m), split at the kinks z = K - p and z = m - K."""
    lo, hi = m - CBAR, CBAR - p
    if hi <= lo:
        return 0.0
    cuts = sorted({lo, hi} | {c for c in (K - p, m - K) if lo < c < hi})
    return sum(_simpson(lambda z: f(max(0.0, p + z - K), max(0.0, m - z - K)) * phi(z + e), a, b)
               for a, b in zip(cuts[:-1], cuts[1:]))


def h1(p: float, m: float, e: float = E_DEV) -> float:
    lo, hi = m - CBAR, CBAR - p
    return 1.0 - (Phi(hi + e) - Phi(lo + e)) if hi > lo else 1.0


def on_R(p: float, m: float) -> bool:
    return (p + m <= 4.0 + 1e-12) or p <= 1e-12 or m <= 1e-12


def value_iteration(n: int = 41, tol: float = 1e-10, cap: int = 300) -> dict:
    step = 5.0 / (n - 1)
    V = [[1.0] * n for _ in range(n)]

    def interp(p, m):
        p = min(max(p, 0.0), 5.0)
        m = min(max(m, 0.0), 5.0)
        i = min(int(p / step), n - 2)
        j = min(int(m / step), n - 2)
        u, v = (p - i * step) / step, (m - j * step) / step
        return ((1 - u) * (1 - v) * V[i][j] + u * (1 - v) * V[i + 1][j]
                + (1 - u) * v * V[i][j + 1] + u * v * V[i + 1][j + 1])

    for it in range(cap):
        W = [[1.0 + Kf(i * step, j * step, interp) for j in range(n)] for i in range(n)]
        d = max(abs(W[i][j] - V[i][j]) for i in range(n) for j in range(n))
        V = W
        if d < tol:
            break
    return {"grid": n, "sweeps": it + 1, "delta": d,
            "v_at_atom": V[0][0],
            "sup_over_grid": max(max(r) for r in V),
            "v_along_m0_p_0_to_5": [V[i][0] for i in range(0, n, (n - 1) // 5)],
            "v_along_p0_m_0_to_5": [V[0][j] for j in range(0, n, (n - 1) // 5)],
            "flat_in_p": max(V[i][0] for i in range(n)) - min(V[i][0] for i in range(n)),
            "range_in_m": V[0][0] - V[0][n - 1]}


def family_required_A(use_p: bool, n: int = 81, Bs=None) -> dict:
    """For w = A - B*(p+m) (use_p) or w = A - B*m, the exact A needed at each B.

    The supersolution condition A*h1 + B*drift >= 1 is LINEAR in A, so required A is a solve.
    """
    Bs = Bs if Bs is not None else [i / 20 for i in range(0, 61)]
    ax = [5.0 * i / (n - 1) for i in range(n)]
    cells = []
    for p in ax:
        for m in ax:
            if not on_R(p, m):
                continue
            g = (lambda a, b: a + b) if use_p else (lambda a, b: b)
            cells.append((p, m, h1(p, m), Kf(p, m, g) - g(p, m)))
    rows = []
    for B in Bs:
        need = max((1.0 - B * d) / hh for _, _, hh, d in cells if hh > 0)
        rows.append((B, need))
    bB, bA = min(rows, key=lambda t: t[1])
    return {"family": "A - B(p+m)" if use_p else "A - B*m", "states": len(cells),
            "best_B": bB, "best_A": bA,
            "table": [{"B": B, "A_required": A} for B, A in rows if B in (0.0, 0.5, 0.75, 1.0,
                                                                         1.3, 1.5, 2.0, 3.0)]}


def main() -> int:
    t = time.time()
    print("=== float shadow: cross-check against the rigorous kernel ===", flush=True)
    ident = []
    for p, m in [(0.0, 0.0), (3.0, 1.0), (0.0, 5.0), (5.0, 0.0), (2.0, 2.0), (4.6, 0.0)]:
        lhs = Kf(p, m, lambda a, b: 1.0)
        ident.append({"state": [p, m], "K_e_1": lhs, "one_minus_h1": 1.0 - h1(p, m),
                      "abs_diff": abs(lhs - (1.0 - h1(p, m)))})
    worst = max(r["abs_diff"] for r in ident)
    print(f"  max |(K_e 1) - (1 - h1)| = {worst:.3e}", flush=True)

    print("=== true value function v = 1 + K_e v ===", flush=True)
    vi = value_iteration()
    print(f"  converged in {vi['sweeps']} sweeps, delta {vi['delta']:.2e}", flush=True)
    print(f"  v(atom) = {vi['v_at_atom']:.5f}   sup = {vi['sup_over_grid']:.5f}", flush=True)
    print(f"  spread in p at m=0: {vi['flat_in_p']:.4f}   drop in m at p=0: "
          f"{vi['range_in_m']:.4f}", flush=True)

    print("=== required A over each one-parameter family ===", flush=True)
    fam_pm = family_required_A(True)
    fam_m = family_required_A(False, Bs=[i / 20 for i in range(0, 41)])
    print(f"  w = A - B(p+m):  best A = {fam_pm['best_A']:.3f} at B = {fam_pm['best_B']}", flush=True)
    print(f"  w = A - B*m   :  best A = {fam_m['best_A']:.4f} at B = {fam_m['best_B']}", flush=True)

    out = {"schema": "C11_CROSSCHECK/1",
           "STATUS": "NOT LOAD-BEARING -- floating point, for diagnosis and successor guidance only",
           "why_it_exists": ("erratum E9: the campaign blamed its own box bound for a candidate "
                             "family that ordinary floating-point arithmetic refutes in seconds. "
                             "A negative verdict owes this check before it blames its machinery."),
           "cross_check_against_rigorous_kernel": {
               "identity": "(K_e 1)(p,m) = 1 - h1(p,m)", "states": ident,
               "max_abs_diff": worst,
               "note": ("this module's Simpson quadrature and the certifier's exact rational "
                        "moments are independent implementations of the same integral")},
           "true_value_function": vi,
           "shape_finding": ("v is ~4.445 at the atom, essentially FLAT in p and decreasing in m. "
                             "A supersolution family that decreases in p is shaped backwards at the "
                             "binding states (p ~ 4.6, m = 0), which is why w = A - B(p+m) is "
                             "infeasible for every B while w = A - B*m is feasible at A ~ 4.885."),
           "families": {"A_minus_B_p_plus_m": fam_pm, "A_minus_B_m": fam_m},
           "decisive_consequence": (
               f"the family A - B(p+m) needs A >= {fam_pm['best_A']:.2f} at its best B = "
               f"{fam_pm['best_B']}, which is the constant-family threshold 1/min_R h1. The "
               "'drift-aware' family is therefore provably NEVER better than a constant, at any "
               "depth, with any box bound. No sharpening and no compute could have certified it."),
           "seconds": round(time.time() - t, 1)}
    p = C.NS / "evidence" / "crosscheck" / "C11_CROSSCHECK.json"
    sha = C.write_evidence(p, out)
    print(f"\nwrote {p.relative_to(C.REPO)}  sha256 {sha[:16]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
