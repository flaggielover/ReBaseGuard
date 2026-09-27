"""Proposition PF (p-flat ceiling) -- a falsifiable prediction checked on the mechanism study's own LP values.

PROPOSITION PF. Let w(p, m) = f(m) (a "p-flat" function, e.g. I2's w = A - B m) satisfy w >= 0 and
w >= 1 + Khat_e w on R.  For m in [0, 5] put p*(m) = max(0, 1 - m); the state (p*(m), m) lies in R and has an
EMPTY atom window (p* + m >= 1), so Khat_e = K_e there and, because p' does not enter a p-flat function,

    f(m) >= 1 + (K'_e f)(m),     (K'_e f)(m) := int_{m - C}^{C - p*(m)} f(max(0, m - z - K)) phi(z + e) dz,

a one-dimensional sub-Markov kernel on [0, 5] (the m-arm, killed at its own alarm and at the p-arm alarm from
p*(m)).  By Lemma T's induction, f >= L'_e := (I - K'_e)^{-1} 1, hence

    tau_F = C_T,F = f(0) >= L'_e(0)       for every p-flat Khat_e-supersolution.

L'_e(0) is a whole-kernel-type ARL of the m-arm: no p-flat family can certify tau (or C_T) below it, whatever its
degree.  (The true tau_a = D_e * E_a[tau] is smaller by the factor D_e.)

CHECK (could fail): on the SAME discretised operator the family LPs used (Nystrom N = 10), assemble K' from the
rows at the nodes (p*(m), m), solve L', and verify that EVERY p-flat family's certified-optimal tau in
validation/A306_MECHANISM.json is >= L'(0) - 1e-9, while at least one p-dependent family goes BELOW L'(0) (showing
the ceiling is a family property, not a property of the statement).

NEGATIVE CONTROL (R1 repair of REVIEW_GLOBAL_INTEGRITY_R1 C-4, which found the former plant never entered the
detection loop): the p-flat nodal candidate w(p, m) = (1 - 1/1000) L'(m) is run THROUGH the pointwise Khat
supersolution screen min_x (w - 1 - Phat w)(x) on the same operator.  It is guaranteed to fail: at the nodes
(p*(m), m) the screen row equals the K' row, so a p-flat w passing the screen would satisfy w >= 1 + K'w on the
m-grid, hence w >= L' by the discrete comparison principle (row sums of K' = 1 - h1 < 1), contradicting
w(0) < L'(0).  The verdict is gated on it.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(HERE))
import ov_quarantine as Q  # noqa: E402
import mech_core as MC  # noqa: E402

Q.install_import_guard()

PFLAT = ("L1", "M2", "M3", "M4", "M6", "HATm")
PDEP = ("PM2", "PM3", "PM4", "HATpm")


def solve_dense(A: list, b: list) -> list:
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        for r in range(n):
            if r != c and M[r][c] != 0.0:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def pflat_ceiling(e: Fr, N: int) -> dict:
    Q.guard_drift(e)
    ny = MC.Nystrom(N, float(e))
    H2, N_ = ny.H2, ny.N
    mgrid = list(range(0, H2 + 1))                       # m = j h
    col_of = {j: [] for j in mgrid}
    for c, (pi, mi) in enumerate(ny.coords):
        col_of[mi].append(c)
    m_of = [mi for (_, mi) in ny.coords]
    Kp = [[0.0] * len(mgrid) for _ in mgrid]
    for i in mgrid:
        pstar = max(0, N_ - i)                            # p*(m) = max(0, 1 - m) in grid units
        r = ny.index[(pstar, i)] if (pstar, i) != (0, 0) else 0
        if pstar + i < N_:
            raise AssertionError("p* state has a non-empty atom window")
        if ny.atom[r] != 0.0:
            raise AssertionError("atom mass at a p* state")
        for c, w in zip(ny.rows_c[r], ny.rows_w[r]):
            Kp[i][m_of[c]] += w
    A = [[(1.0 if i == j else 0.0) - Kp[i][j] for j in mgrid] for i in mgrid]
    L = solve_dense(A, [1.0] * len(mgrid))
    tr = ny.truth()
    # planted p-flat candidate through the screen (class a control)
    w = [(1.0 - 1e-3) * L[mi] for (_, mi) in ny.coords]
    Pw = ny.apply(w, True)
    marg = [w[r] - 1.0 - Pw[r] for r in range(ny.n)]
    r0 = min(range(ny.n), key=lambda r: marg[r])
    w_ok = [L[mi] + 1.0 for (_, mi) in ny.coords]           # informational twin (not asserted)
    Pok = ny.apply(w_ok, True)
    return {"Lprime_0": L[0], "E_a_tau": tr["v"][0], "tau_a": tr["t"][0], "D": tr["d"][0], "N": N,
            "planted_pflat_screen": {"min_margin": min(marg), "argmin_node": list(ny.xy(r0)),
                                     "fired": min(marg) < 0},
            "twin_Lprime_plus_1_min_margin_info": min(w_ok[r] - 1.0 - Pok[r] for r in range(ny.n))}


def main() -> dict:
    mech = json.loads((NS / "validation" / "A306_MECHANISM.json").read_text())
    out = {"schema": "A306_PFLAT/1", "label": "FLOAT, NON-CERTIFIED, NON-TARGET", "per_drift": {}}
    viol, below = [], []
    for key, res in mech["per_drift"].items():
        e = Fr(key)
        c = pflat_ceiling(e, mech["declared"]["N_lp"])
        fams = res["families_point_N10"]
        c["pflat_tau"] = {f: fams[f]["tau"]["value"] for f in PFLAT}
        c["pdep_tau"] = {f: fams[f]["tau"]["value"] for f in PDEP}
        for f, v in c["pflat_tau"].items():
            if v < c["Lprime_0"] - 1e-9 * c["Lprime_0"]:
                viol.append({"drift": key, "family": f, "tau": v, "ceiling": c["Lprime_0"]})
        for f, v in c["pdep_tau"].items():
            if v < c["Lprime_0"] * (1 - 1e-6):
                below.append({"drift": key, "family": f})
        c["ratio_Lprime_to_E_a_tau"] = c["Lprime_0"] / c["E_a_tau"]
        c["ratio_Lprime_to_tau_a"] = c["Lprime_0"] / c["tau_a"]
        out["per_drift"][key] = c
    out["negative_control"] = {d: c["planted_pflat_screen"] for d, c in out["per_drift"].items()}
    out["negative_control_all_fired"] = all(v["fired"] for v in out["negative_control"].values())
    out["prediction_pflat_never_below_ceiling"] = {"violations": viol, "pass": not viol,
                                                   "checked": len(PFLAT) * len(out["per_drift"])}
    out["pdep_families_below_ceiling"] = below
    out["verdict"] = "PASS" if (not viol and out["negative_control_all_fired"]) else "FAIL"
    return out


if __name__ == "__main__":
    o = main()
    (NS / "validation" / "A306_PFLAT.json").write_text(json.dumps(o, indent=1, sort_keys=True) + "\n")
    Q.log_execution("streams/A_306/mechanism/mech_pflat.py",
                    "Proposition PF: p-flat supersolution ceiling for tau/C_T vs the family LP values",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION",
                    notes="float, non-certified; drifts 1/2, 1, 3 only")
    for k, c in o["per_drift"].items():
        print(k, "L'(0)=%.5f E_a[tau]=%.5f tau_a=%.5f D=%.5f" % (c["Lprime_0"], c["E_a_tau"], c["tau_a"], c["D"]),
              "pflat min tau=%.5f" % min(c["pflat_tau"].values()), "pdep min tau=%.5f" % min(c["pdep_tau"].values()))
    print("violations", o["prediction_pflat_never_below_ceiling"], "below", o["pdep_families_below_ceiling"],
          "NC fired", o["negative_control_all_fired"], o["verdict"])
