"""Stream A mechanism study (NON-TARGET, FLOAT, NON-CERTIFIED): where does a candidate family's slack come from?

Question (stream brief, deliverable 2): at declared non-target drifts, how far are I2's candidate families
(w = A - B m for Abar on K_e and for tau / C_T on Khat_e; u = alpha + beta m for D_lo) from the true operator
constants, how much of that is the FAMILY (ansatz), how much is BLOCK-UNIFORMITY and how much is the BOX/PANEL
verification discretisation, and do richer families (same statements) remove it?  If richer families of the
SAME statement drive the value to the truth, the gap is IMPLEMENTATION_SLACK; if the value were pinned away
from the truth by the statement itself, it would be PROOF_STRENGTH_DIFFERENCE.  Either outcome was possible.

DECLARED BEFORE ANY RUN (rule, not similarity to any target):
  drifts                 e in {1/2, 1, 3}                              (brief; all outside [6/5, 13/5])
  block widths           w in {0, 1/32, 1/16, 1/8}, block [e, e + w]   (a dyadic ladder, fixed a priori)
  truth                  piecewise-linear Nystrom, N in {20, 40}, Richardson (N=40) + (N=40 - N=20)/3
  family LPs             Nystrom operator N = 10, constraints at every node (consistent-model slack)
  families               L1 {1,m}; M2,M3,M4,M6 (poly in m); PM2,PM3,PM4 (poly in p,m, total degree);
                         HATm (piecewise-linear in m, knots k/2); HATpm (HATm(m) + HATp(p))
  box/panel emulation    C11R's frozen configuration depth 5, 32 u-panels (C11R_POLICY), float re-implementation
                         of c11r_boxdata.box_upper_coeffs / box_lower_coeffs, cross-checked against the exact
                         c11_certifier box bound at a point drift (depth 3, 8 panels)
  negative controls      NC1 full nodal family on a tiny operator (N = 4) must reproduce the truth exactly;
                         NC2 a planted 0.99 x truth candidate must FAIL the pointwise supersolution screen;
                         NC3 a planted wrong atom split must break the Sherman-Morrison identity v(a) = t(a)/D;
                         NC4 every family value must lie on the correct side of the truth (any violation is a
                             detected solver/assembly defect, never silently dropped).
No quantity is evaluated at any CUSUM m=5 tail drift; every drift passes ov_quarantine.guard_drift.
"""
from __future__ import annotations

import json
import math
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[2]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(HERE))
import ov_quarantine as Q  # noqa: E402
import mech_core as MC  # noqa: E402
import mech_lp as LP  # noqa: E402

Q.install_import_guard()

DRIFTS = (Fr(1, 2), Fr(1), Fr(3))
WIDTHS = (Fr(0), Fr(1, 32), Fr(1, 16), Fr(1, 8))
N_TRUTH = (20, 40)
N_LP = 10
BOX_DEPTH, BOX_PANELS = 5, 32


# ------------------------------------------------------------------------------------------------ families
def fam_basis(name: str) -> list:
    """List of (label, f(p, m)) with values O(1) on [0,5]^2."""
    s = lambda p: p / 5.0  # noqa: E731
    if name == "L1":
        return [("1", lambda p, m: 1.0), ("m", lambda p, m: m / 5.0)]
    if name.startswith("M") and name[1:].isdigit():
        k = int(name[1:])
        return [(f"m^{j}", (lambda j: lambda p, m: (m / 5.0) ** j)(j)) for j in range(k + 1)]
    if name.startswith("PM") and name[2:].isdigit():
        k = int(name[2:])
        return [(f"p^{i}m^{j}", (lambda i, j: lambda p, m: s(p) ** i * (m / 5.0) ** j)(i, j))
                for i in range(k + 1) for j in range(k + 1 - i)]
    knots = [0.5 * i for i in range(11)]

    def hat(x, i):
        c = knots[i]
        return max(0.0, 1.0 - abs(x - c) / 0.5)
    if name == "HATm":
        return [(f"hm{i}", (lambda i: lambda p, m: hat(m, i))(i)) for i in range(11)]
    if name == "HATpm":
        return ([(f"hm{i}", (lambda i: lambda p, m: hat(m, i))(i)) for i in range(11)]
                + [(f"hp{i}", (lambda i: lambda p, m: hat(p, i))(i)) for i in range(1, 11)])
    raise ValueError(name)


FAMILIES = ("L1", "M2", "M3", "M4", "M6", "PM2", "PM3", "PM4", "HATm", "HATpm")


def nodal(ny, f) -> list:
    return [f(*ny.xy(r)) for r in range(ny.n)]


# ------------------------------------------------------------------------------------------------ LP assembly
def lp_family(nys: list, fam: str, objective: str) -> dict:
    """objective in {'Abar', 'tau', 'C_T', 'D'} ; nys: operators at the block's sample drifts."""
    return lp_nodal(nys, [nodal(nys[0], f) for _, f in fam_basis(fam)], objective)


def lp_nodal(nys: list, vals: list, objective: str) -> dict:
    """The family spanned by the given nodal vectors (same node set for every drift)."""
    nb = len(vals)
    ny0 = nys[0]
    G, g = [], []
    atom_removed = objective != "Abar"
    for ny in nys:
        Pv = [ny.apply(v, atom_removed) for v in vals]
        for r in range(ny.n):
            row = [vals[k][r] - Pv[k][r] for k in range(nb)]
            if objective == "D":
                G.append([-x for x in row])
                g.append(-ny.h1[r])
            else:
                G.append(row)
                g.append(1.0)
    for r in range(ny0.n):                                # nonnegativity (both lemmas need w, u >= 0)
        G.append([vals[k][r] for k in range(nb)])
        g.append(0.0)
    atomv = [vals[k][0] for k in range(nb)]
    if objective == "C_T":
        # min T  s.t.  T - w(x) >= 0  at every node
        G = [row + [0.0] for row in G]
        for r in range(ny0.n):
            G.append([-vals[k][r] for k in range(nb)] + [1.0])
            g.append(0.0)
        c = [0.0] * nb + [1.0]
    elif objective == "D":
        c = [-a for a in atomv]
    else:
        c = atomv
    sol = LP.solve(G, g, c)
    val = -sol["primal_obj"] if objective == "D" else sol["primal_obj"]
    return {"value": val, "gap": sol["gap"], "min_slack": sol["min_slack"], "iterations": sol["iterations"],
            "params": nb}


# ------------------------------------------------------------------------------------------------ linear family, exact 1-D search
def _ternary(f, lo, hi, maximise=False, it=200):
    for _ in range(it):
        a, b = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        fa, fb = f(a), f(b)
        if (fa > fb) if maximise else (fa < fb):
            hi = b
        else:
            lo = a
    x = 0.5 * (lo + hi)
    return x, f(x)


def linear_upper_nystrom(nys: list, atom_removed: bool, b_max: float = 4.0) -> dict:
    """min A over B in [0, b_max] with A - B m >= 1 + P(A - B m) at every node of every sample drift, A >= 5B."""
    rows = []
    ones = [1.0] * nys[0].n
    mm = [ny_m for ny_m in (nys[0].xy(r)[1] for r in range(nys[0].n))]
    for ny in nys:
        P1, Pm = ny.apply(ones, atom_removed), ny.apply(mm, atom_removed)
        for r in range(ny.n):
            rows.append((1.0 - P1[r], mm[r] - Pm[r]))

    def a_req(B):
        best = 5.0 * B
        for den, dm in rows:
            need = (1.0 + B * dm) / den if den > 0 else math.inf
            if need > best:
                best = need
        return best
    B, A = _ternary(a_req, 0.0, b_max)
    return {"A": A, "B": B}


def linear_lower_nystrom(nys: list, beta_max: float = 1.0) -> dict:
    """max alpha over beta in [0, beta_max] with alpha + beta m <= h1 + Phat(alpha + beta m) at every node."""
    rows = []
    ones = [1.0] * nys[0].n
    mm = [nys[0].xy(r)[1] for r in range(nys[0].n)]
    for ny in nys:
        P1, Pm = ny.apply(ones, True), ny.apply(mm, True)
        for r in range(ny.n):
            rows.append((1.0 - P1[r], mm[r] - Pm[r], ny.h1[r]))

    def a_max(beta):
        best = math.inf
        for den, dm, h in rows:
            v = (h - beta * dm) / den
            if v < best:
                best = v
        return best
    beta, alpha = _ternary(a_max, 0.0, beta_max, maximise=True)
    return {"alpha": alpha, "beta": beta}


# ------------------------------------------------------------------------------------------------ box/panel emulation (C11R D5/P32)
def cover(depth: int) -> list:
    boxes = [(0.0, 5.0, 0.0, 5.0)]
    for _ in range(depth):
        nxt = []
        for (a, b, c, d) in boxes:
            am, cm = 0.5 * (a + b), 0.5 * (c + d)
            for bx in ((a, am, c, cm), (am, b, c, cm), (a, am, cm, d), (am, b, cm, d)):
                aa, bb, cc, dd = bx
                if not (bb < 0 or dd < 0 or aa > 5 or cc > 5) and ((aa + cc <= 4) or cc == 0 or aa == 0):
                    nxt.append(bx)
        boxes = nxt
    return boxes


def box_upper_rows(elo: float, ehi: float, depth: int, panels: int) -> list:
    """Float re-implementation of c11r_boxdata.box_upper_coeffs (K and Khat keys)."""
    out = []
    for (a, b, c, d) in cover(depth):
        lo_z, hi_z = c - MC.CC, MC.CC - a
        u0a, u1a = lo_z + elo, hi_z + ehi
        step = (u1a - u0a) / panels
        at_lo, at_hi = d - MC.KK, MC.KK - b
        S = {"K": [0.0, 0.0], "H": [0.0, 0.0]}
        for k in range(panels):
            u0, u1 = u0a + step * k, u0a + step * (k + 1)
            z_lo, z_hi = u0 - ehi, u1 - elo
            m_lo = max(0.0, c - z_hi - MC.KK)
            mass = MC.pmass(u0, u1)
            S["K"][0] += mass
            S["K"][1] += m_lo * mass
            if not (at_lo < at_hi and z_lo >= at_lo and z_hi <= at_hi):
                S["H"][0] += mass
                S["H"][1] += m_lo * mass
        out.append((d, S))
    return out


def box_select_upper(rows: list, key: str, b_max: float = 4.0) -> dict:
    def a_req(B):
        best = 5.0 * B
        for d, S in rows:
            S0, S1 = S[key]
            den = 1.0 - S0
            need = (1.0 - B * (S1 - d)) / den if den > 0 else math.inf
            if need > best:
                best = need
        return best
    B, A = _ternary(a_req, 0.0, b_max)
    return {"A": A, "B": B}


def box_lower_rows(elo: float, ehi: float, depth: int, panels: int) -> list:
    """Float re-implementation of c11r_boxdata.box_lower_coeffs + h1_box_lower."""
    out = []
    for (a, b, c, d) in cover(depth):
        u0a, u1a = d - MC.CC + ehi, MC.CC - b + elo
        M0 = M1 = 0.0
        if u1a > u0a:
            step = (u1a - u0a) / panels
            ulo, uhi = c - MC.KK, MC.KK - a
            for k in range(panels):
                u0, u1 = u0a + step * k, u0a + step * (k + 1)
                z_lo, z_hi = u0 - ehi, u1 - elo
                meets = ulo < uhi and z_lo < uhi and z_hi > ulo
                if meets:
                    continue
                mass = MC.pmass(u0, u1)
                M0 += mass
                M1 += max(0.0, c - z_hi - MC.KK) * mass
        h1lo = MC.pmass(-50.0, c - MC.CC + elo) + MC.pmass(MC.CC - a + ehi, 50.0)
        out.append((d, M0, M1, h1lo))
    return out


def box_select_lower(rows: list, beta_max: float = 1.0) -> dict:
    def a_max(beta):
        best = math.inf
        for d, M0, M1, h in rows:
            den = 1.0 - M0
            v = (h + beta * (M1 - d)) / den if den > 0 else -math.inf
            if v < best:
                best = v
        return best
    beta, alpha = _ternary(a_max, 0.0, beta_max, maximise=True)
    return {"alpha": alpha, "beta": beta}


def box_crosscheck_exact(e: Fr) -> dict:
    """Float box bound vs the EXACT c11_certifier box bound (point drift, depth 3, 8 panels, w = 3 - m/2)."""
    Q.guard_drift(e)
    sys.path.insert(0, str(NS.parent / "p5y_k5_tail_c11_n9_independent_certifier/code"))
    import c11_certifier as X   # pure library (read first; no side effects beyond sys.path)
    w = {(0, 0): Fr(3), (0, 1): Fr(-1, 2)}
    ex = X.supersolution_margin(w, e, depth=3, panels=8)
    rows = box_upper_rows(float(e), float(e), 3, 8)
    A, B = 3.0, 0.5
    fl = min(A * (1 - S["K"][0]) + B * (S["K"][1] - d) - 1 for d, S in rows)
    return {"exact_margin_lower_bound": float(ex["margin_lower_bound"]), "float_emulation": fl,
            "abs_diff": abs(float(ex["margin_lower_bound"]) - fl), "boxes": ex["boxes"],
            "agree_1e-12": abs(float(ex["margin_lower_bound"]) - fl) < 1e-12}


# ------------------------------------------------------------------------------------------------ truth
def truth_at(e: Fr) -> dict:
    Q.guard_drift(e)
    out = {}
    for N in N_TRUTH:
        ny = MC.Nystrom(N, float(e))
        tr = ny.truth()
        out[N] = {"v_a": tr["v"][0], "t_a": tr["t"][0], "sup_t": max(tr["t"]), "D": tr["d"][0],
                  "sup_v": max(tr["v"]), "SM_identity_err": tr["v"][0] - tr["t"][0] / tr["d"][0],
                  "argmax_t": list(ny.xy(max(range(ny.n), key=lambda r: tr["t"][r]))),
                  "iters": tr["iters"], "residuals": tr["residuals"]}
    rich = {k: out[40][k] + (out[40][k] - out[20][k]) / 3.0 for k in ("v_a", "t_a", "sup_t", "D")}
    return {"by_N": {str(k): v for k, v in out.items()}, "richardson": rich,
            "richardson_uncertainty": {k: abs(out[40][k] - out[20][k]) / 3.0 for k in ("v_a", "t_a", "sup_t", "D")}}


def D_derivs(e: Fr, N: int = 40, dl: Fr = Fr(1, 32)) -> dict:
    Q.guard_drift(e - dl, e + dl)
    Ds = {}
    for s in (-1, 0, 1):
        ny = MC.Nystrom(N, float(e + s * dl))
        d, _, _ = ny.solve(ny.h1, True)
        Ds[s] = d[0]
    h = float(dl)
    return {"D'": (Ds[1] - Ds[-1]) / (2 * h), "D''": (Ds[1] - 2 * Ds[0] + Ds[-1]) / h ** 2, "step": h, "N": N}


# ------------------------------------------------------------------------------------------------ negative controls
def nc_full_nodal(e: Fr) -> dict:
    """NC1 (truth-in-family): when the exact discrete solution is a member of the family, the LP must return it
    (Abar: v(a); tau: t(a); D: d(a)); the same family without it (L1) must NOT (it is strictly looser)."""
    Q.guard_drift(e)
    ny = MC.Nystrom(N_LP, float(e))
    tr = ny.truth()
    one = [1.0] * ny.n
    mm = [ny.xy(r)[1] / 5.0 for r in range(ny.n)]
    res = {}
    for obj, key in (("Abar", "v"), ("tau", "t"), ("D", "d")):
        withv = lp_nodal([ny], [list(tr[key]), one, mm], obj)["value"]
        without = lp_nodal([ny], [one, mm], obj)["value"]
        res[obj] = {"truth": tr[key][0], "family_with_truth": withv, "family_without": without,
                    "reproduces": abs(withv - tr[key][0]) <= 1e-8 * max(1.0, abs(tr[key][0])),
                    "without_is_looser": (without > tr[key][0] * (1 + 1e-6)) if obj != "D"
                    else (without < tr[key][0] * (1 - 1e-6))}
    return {"per_objective": res, "nodes": ny.n,
            "pass": all(r["reproduces"] and r["without_is_looser"] for r in res.values())}


def nc_planted_shrink(e: Fr) -> dict:
    """NC2: 0.99 x truth is NOT a supersolution; the pointwise screen must detect it (and accept 1.0 x truth + 1e-9)."""
    Q.guard_drift(e)
    ny = MC.Nystrom(10, float(e))
    tr = ny.truth()
    res = {}
    for lab, fac, add in (("planted_0.99", 0.99, 0.0), ("truth_plus", 1.0, 1e-9)):
        w = [fac * x + add for x in tr["v"]]
        Pw = ny.apply(w, False)
        res[lab] = min(w[r] - 1.0 - Pw[r] for r in range(ny.n))
    return {"min_margin": res, "pass": res["planted_0.99"] < 0 and res["truth_plus"] > -1e-10}


def nc_wrong_atom(e: Fr) -> dict:
    """NC3: dropping the atom piece from K as well (a planted wrong split) must break v(a) = t(a)/D."""
    Q.guard_drift(e)
    ny = MC.Nystrom(10, float(e))
    tr = ny.truth()
    good = abs(tr["v"][0] - tr["t"][0] / tr["d"][0])
    saved = ny.atom
    ny.atom = MC.array("d", [0.0] * ny.n)            # planted defect: atom piece dropped from K as well
    vbad, _, _ = ny.solve([1.0] * ny.n, False)      # "whole kernel" now equals Khat: v_bad = t
    ny.atom = saved
    bad = abs(vbad[0] - tr["t"][0] / tr["d"][0])
    return {"good_identity_err": good, "planted_identity_err": bad, "pass": good < 1e-9 and bad > 1e-3}


# ------------------------------------------------------------------------------------------------ main
def main() -> dict:
    t00 = time.time()
    out = {"schema": "A306_MECHANISM/1", "label": "FLOAT, NON-CERTIFIED, NON-TARGET",
           "declared": {"drifts": [str(e) for e in DRIFTS], "widths": [str(w) for w in WIDTHS],
                        "N_truth": list(N_TRUTH), "N_lp": N_LP, "families": list(FAMILIES),
                        "box": {"depth": BOX_DEPTH, "panels": BOX_PANELS}},
           "per_drift": {}, "negative_controls": {}, "crosscheck": {}}
    for e in DRIFTS:
        for w in WIDTHS:
            Q.guard_drift(e, e + w)
    out["crosscheck"]["box_float_vs_exact_c11"] = box_crosscheck_exact(Fr(3))
    for e in DRIFTS:
        key = str(e)
        res = {"truth": truth_at(e), "D_derivatives_truth": D_derivs(e)}
        # truth along each block (sup of v(a), t(a), sup t ; inf of D) at the block's end/mid points, N = 20
        blocks = {}
        for w in WIDTHS:
            pts = sorted({e, e + w / 2, e + w})
            vals, nys = [], []
            for x in pts:
                ny = MC.Nystrom(20, float(x))
                tr = ny.truth()
                nys.append(ny)
                vals.append({"e": str(x), "v_a": tr["v"][0], "t_a": tr["t"][0], "sup_t": max(tr["t"]),
                             "D": tr["d"][0]})
            lin = {"Abar": linear_upper_nystrom(nys, False), "Khat": linear_upper_nystrom(nys, True),
                   "D": linear_lower_nystrom(nys)}
            ub = box_upper_rows(float(e), float(e + w), BOX_DEPTH, BOX_PANELS)
            lb = box_lower_rows(float(e), float(e + w), BOX_DEPTH, BOX_PANELS)
            box = {"Abar": box_select_upper(ub, "K"), "Khat": box_select_upper(ub, "H"), "D": box_select_lower(lb)}
            blocks[str(w)] = {"samples": vals,
                              "truth_sup_v_a": max(v["v_a"] for v in vals),
                              "truth_sup_t_a": max(v["t_a"] for v in vals),
                              "truth_sup_sup_t": max(v["sup_t"] for v in vals),
                              "truth_inf_D": min(v["D"] for v in vals),
                              "linear_pointwise_N20": lin, "linear_box_D5P32": box}
        res["blocks"] = blocks
        # richer families at the point drift, consistent model N = N_LP
        nyl = [MC.Nystrom(N_LP, float(e))]
        trl = nyl[0].truth()
        res["lp_model_truth_N10"] = {"v_a": trl["v"][0], "t_a": trl["t"][0], "sup_t": max(trl["t"]),
                                     "D": trl["d"][0]}
        fams = {}
        for f in FAMILIES:
            fams[f] = {obj: lp_family(nyl, f, obj) for obj in ("Abar", "tau", "C_T", "D")}
        res["families_point_N10"] = fams
        out["per_drift"][key] = res
        print(f"drift {key} done at {time.time() - t00:.0f}s", flush=True)
    # negative controls (declared set)
    out["negative_controls"]["NC1_full_nodal"] = nc_full_nodal(Fr(1))
    out["negative_controls"]["NC2_planted_shrink"] = nc_planted_shrink(Fr(1))
    out["negative_controls"]["NC3_wrong_atom_split"] = nc_wrong_atom(Fr(1))
    viol = []
    for key, res in out["per_drift"].items():
        tru = res["lp_model_truth_N10"]
        for f, objs in res["families_point_N10"].items():
            for obj, r in objs.items():
                ref = {"Abar": tru["v_a"], "tau": tru["t_a"], "C_T": tru["sup_t"], "D": tru["D"]}[obj]
                ok = (r["value"] <= ref + 1e-7) if obj == "D" else (r["value"] >= ref - 1e-7 * ref)
                if not ok or r["min_slack"] < -1e-7:
                    viol.append({"drift": key, "family": f, "objective": obj, "value": r["value"], "truth": ref,
                                 "min_slack": r["min_slack"]})
    out["negative_controls"]["NC4_side_of_truth"] = {"violations": viol, "pass": not viol,
                                                     "checked": sum(len(r["families_point_N10"]) * 4
                                                                    for r in out["per_drift"].values())}
    out["wall_seconds"] = time.time() - t00
    out["verdict"] = "PASS" if all(v.get("pass", False) for v in out["negative_controls"].values()) \
        and out["crosscheck"]["box_float_vs_exact_c11"]["agree_1e-12"] else "CONTROL_FAILED"
    return out


def tables(o: dict) -> str:
    L = ["# Mechanism study tables (generated by mech_study.py; FLOAT, NON-CERTIFIED, NON-TARGET)", ""]
    L.append("## Truth (Nystrom, Richardson N=20/40)")
    L.append("")
    L.append("| e | E_a[tau] = v(a) | tau_a = t(a) | sup t (C_T truth) | D | D' | D'' |")
    L.append("|---|---|---|---|---|---|---|")
    for k, r in o["per_drift"].items():
        t, dd = r["truth"]["richardson"], r["D_derivatives_truth"]
        L.append(f"| {k} | {t['v_a']:.6f} | {t['t_a']:.6f} | {t['sup_t']:.6f} | {t['D']:.6f} | {dd[chr(68) + chr(39)]:.5f} | {dd[chr(68) + chr(39) + chr(39)]:.5f} |")
    L.append("")
    L.append("## Family slack at the point drift (consistent model N=10): value / truth (D: value / truth, <= 1)")
    L.append("")
    L.append("| e | family | params | Abar | tau | C_T | D_lo |")
    L.append("|---|---|---|---|---|---|---|")
    for k, r in o["per_drift"].items():
        tr = r["lp_model_truth_N10"]
        for f, objs in r["families_point_N10"].items():
            L.append(f"| {k} | {f} | {objs['Abar']['params']} | {objs['Abar']['value'] / tr['v_a']:.4f} | "
                     f"{objs['tau']['value'] / tr['t_a']:.4f} | {objs['C_T']['value'] / tr['sup_t']:.4f} | "
                     f"{objs['D']['value'] / tr['D']:.4f} |")
    L.append("")
    L.append("## Linear family (I2's families): pointwise (Nystrom N=20, block samples) vs box/panel D5/P32 vs truth")
    L.append("")
    L.append("| e | width | truth sup v(a) | L1 pointwise A (K) | L1 box A (K) | truth sup t(a) | truth sup sup t | "
             "L1 pointwise A (Khat) | L1 box A (Khat) | truth inf D | L1 pointwise alpha | L1 box alpha |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, r in o["per_drift"].items():
        for w, b in r["blocks"].items():
            lp, bx = b["linear_pointwise_N20"], b["linear_box_D5P32"]
            L.append(f"| {k} | {w} | {b['truth_sup_v_a']:.5f} | {lp['Abar']['A']:.5f} | {bx['Abar']['A']:.5f} | "
                     f"{b['truth_sup_t_a']:.5f} | {b['truth_sup_sup_t']:.5f} | {lp['Khat']['A']:.5f} | "
                     f"{bx['Khat']['A']:.5f} | {b['truth_inf_D']:.5f} | {lp['D']['alpha']:.5f} | {bx['D']['alpha']:.5f} |")
    L.append("")
    L.append("## Negative controls and cross-check")
    L.append("")
    for k, v in o["negative_controls"].items():
        L.append(f"* {k}: pass = {v['pass']}")
    c = o["crosscheck"]["box_float_vs_exact_c11"]
    L.append(f"* box float emulation vs exact c11_certifier (e = 3, depth 3, 8 panels, w = 3 - m/2): "
             f"|diff| = {c['abs_diff']:.3e} ({c['boxes']} boxes), agree = {c['agree_1e-12']}")
    L.append(f"* verdict: {o['verdict']}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    o = main()
    (NS / "validation" / "A306_MECHANISM.json").write_text(json.dumps(o, indent=1, sort_keys=True) + "\n")
    (HERE / "MECHANISM_TABLES.md").write_text(tables(o))
    Q.log_execution("streams/A_306/mechanism/mech_study.py",
                    "family / block / box-panel slack of I2-style and richer candidate families vs float truth, "
                    "declared non-target drifts {1/2, 1, 3}",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION",
                    notes="float, non-certified; drifts guarded by guard_drift; no target cell or tail drift")
    print(tables(o))
