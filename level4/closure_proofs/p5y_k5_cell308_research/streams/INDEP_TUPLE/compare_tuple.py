"""Stream F3 (INDEP_TUPLE) T2 + T3: exact comparison of the independent TC-T profile tuple (tuple_independent.py,
frozen sha256 47ae88dc...) with the ASSEMBLY primary on the synthetic decoy bundles of NS/streams/ASSEMBLY/decoy_gen.py.

Synthetic decoys only (labels DECOY, cells 9000+, geometries outside the drift band; every primary entry point calls
the c308 guards, and the independent module refuses quarantined labels and band geometries by itself). No file is
read other than code modules; nothing is computed for any CUSUM cell.

Per decoy, everything is compared EXACTLY (Fraction equality), coefficient by coefficient:
  C-a  the tuple the primary extracts from the frozen consumer (ext.terms, read off the capturing proxy): fF fD fH fG
       Env4 abs_G H_at_a per r, and the frozen per-r calls at s = rho (taylor_bounds -> (p0, p1, p2), radius,
       object_half_width) against the independent p_j(rho), rad_r(rho), rad_r(rho) + rho |G(a)|
  C-b  tptb_tail.rederive_tuple: fF fD fH fG Env4 abs_G H_at_a sigma3 sigma4 per r
  C-c  the decoy's committed per_r record and committed H_exact
  C-d  the frozen whole-cell enclosure (lo, hi) and the primary's W sum
  C-e  the profile polynomials TPT / TPT-B actually integrate: every call of tpt.lo_hi_polys (cell constants and each
       block's constants), coefficient lists lo(s), hi(s), against the independent polynomials with the same A
  C-f  the primary's own p_at / rad_at on 7 distinct s in [0, rho] against the independent polynomials (7 > degree 4,
       so pointwise equality is polynomial identity)
  C-L  Lemma G: the independent (A0, A1, A2) from C_upper against the frozen tct_rule.atom_constants_generic

T3 planted mutants travel through the primary's code path (the ``mutate`` hook of evaluate_bundle, a patched
tpt.rad_poly, or a patched rederive_tuple). The COMMON-MODE variants apply the same defect to the extracted tuple AND to
rederive_tuple and drop the committed per_r record, so that the primary's own gates cannot see it; the rad(rho)-
preserving ones then pass G-R1 (the whole-cell reproduction at s = rho), and only the independent comparison can fail.

    python3 -I -B compare_tuple.py            # writes results/COMPARE_TUPLE.json, prints a summary
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[2]
FROZEN_SHA = "47ae88dcc792779b247ae1827e66c9f460a5e1b2c56e6b081a828ae245e6cbc8"


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


IT_PATH = HERE.parent / "tuple_independent.py"
if hashlib.sha256(IT_PATH.read_bytes()).hexdigest() != FROZEN_SHA:
    raise SystemExit("tuple_independent.py differs from its frozen sha256; refusing")
IT = _load("f3_tuple_independent", IT_PATH)
DG = _load("c308E_decoy_gen", NS / "streams" / "ASSEMBLY" / "decoy_gen.py")
TB = sys.modules["c308E_tptb_tail"]
Q = TB.Q
TPT = TB.TPT

TUP = ("fF", "fD", "fH", "fG", "Env4")
S_GRID = 7


# ------------------------------------------------------------------------------------------------ helpers

def norm(p):
    p = [F(v) for v in p]
    while p and p[-1] == 0:
        p.pop()
    return p


def my_lo_hi(res, A):
    """lo(s), hi(s) coefficient lists from the independent per-r tuple with constants A (assembly as THEOREM_TPT s2)."""
    m = res["m"]
    lo, hi = [res["W"][0]], [res["W"][1]]
    for r in range(m):
        t = res["per_r"][r]
        rad = IT.profiles(t, A)["rad"]
        rad = IT.padd(rad, [F(0), t["abs_G"]])
        lo = IT.padd(lo, IT.pscale(F(1, m), IT.padd([t["H_at_a"][0]], IT.pscale(F(-1), rad))))
        hi = IT.padd(hi, IT.pscale(F(1, m), IT.padd([t["H_at_a"][1]], rad)))
    return lo, hi


class Recorder:
    """Wraps tpt.lo_hi_polys to record every (A, lo, hi) the transport integrates. Delegates unchanged."""

    def __init__(self):
        self.calls = []
        self._orig = TPT.lo_hi_polys

    def __enter__(self):
        orig = self._orig

        def wrapped(cp):
            out = orig(cp)
            self.calls.append({"A": (cp.A0, cp.A1, cp.A2), "lo": list(out[0]), "hi": list(out[1])})
            return out
        TPT.lo_hi_polys = wrapped
        return self

    def __exit__(self, *exc):
        TPT.lo_hi_polys = self._orig
        return False


def run_primary(bundle, mutate=None):
    hold = {}

    def obs(ext):
        if mutate is not None:
            mutate(ext)
        hold["ext"] = copy.deepcopy(ext)
    with Recorder() as rec:
        out = TB.evaluate_bundle(bundle, mutate=obs)
    return out, hold.get("ext"), rec.calls


def compare(bundle, out, ext, poly_calls, *, red=None) -> dict:
    """All exact comparisons for one decoy. Returns {"mismatches": [...], "checked": n, ...}."""
    meas, aux = bundle["meas"], bundle["aux"]
    S, _prov = TB.supply_from(bundle, meas)
    mine = IT.tuple_tct(meas, aux, S)
    rho = mine["rho"]
    mm, n = [], 0

    def eq(tag, a, b):
        nonlocal n
        n += 1
        if a != b:
            mm.append(tag)

    # C-a: tuple extracted from the frozen consumer + the frozen per-r calls at s = rho
    if ext is None:
        mm.append("C-a:no_extraction")
    else:
        eq("C-a:n_terms", len(ext["terms"]), mine["m"])
        for r, t in enumerate(ext["terms"]):
            me = mine["per_r"][r]
            for x in TUP + ("abs_G",):
                eq(f"C-a:r{r}.{x}", t[x], me[x])
            eq(f"C-a:r{r}.H_at_a", tuple(t["H_at_a"]), tuple(me["H_at_a"]))
            pj = tuple(IT.peval(me[p], rho) for p in ("p0", "p1", "p2"))
            eq(f"C-a:r{r}.frozen_taylor_bounds(p0,p1,p2)@rho", tuple(t["frozen_p"]), pj)
            eq(f"C-a:r{r}.frozen_radius@rho", t["frozen_rad"], IT.peval(me["rad"], rho))
            eq(f"C-a:r{r}.frozen_half@rho", t["frozen_half"], IT.peval(me["rad"], rho) + rho * me["abs_G"])
        eq("C-d:W_sum", tuple(ext["W"]), tuple(mine["W"]))
    # C-b: tptb_tail.rederive_tuple
    red = TB.rederive_tuple(meas, aux) if red is None else red
    for r in range(mine["m"]):
        me = mine["per_r"][r]
        for x in TUP + ("abs_G", "sigma3", "sigma4"):
            eq(f"C-b:r{r}.{x}", red[r][x], me[x])
        eq(f"C-b:r{r}.H_at_a", tuple(red[r]["H_at_a"]), tuple(me["H_at_a"]))
    # C-c: committed decoy record
    com = bundle.get("committed") or {}
    if com.get("per_r") is not None:
        for r in range(mine["m"]):
            c, me = com["per_r"][str(r)], mine["per_r"][r]
            for x in TUP + ("abs_G",):
                eq(f"C-c:r{r}.{x}", F(c[x]), me[x])
            eq(f"C-c:r{r}.H_at_a", tuple(F(v) for v in c["H_at_a"]), tuple(me["H_at_a"]))
    wc = IT.whole_cell(mine)
    if com.get("H_exact") is not None:
        eq("C-c:H_exact", tuple(F(v) for v in com["H_exact"]), wc)
    # C-d: frozen whole-cell enclosure
    fr = (out.get("gates") or {}).get("G-R1", {}).get("frozen")
    if fr is not None:
        eq("C-d:frozen_whole_cell", tuple(F(v) for v in fr), wc)
    # C-e: every profile polynomial the transport integrates
    for i, call in enumerate(poly_calls):
        lo, hi = my_lo_hi(mine, call["A"])
        eq(f"C-e:call{i}.lo_coeffs", norm(call["lo"]), norm(lo))
        eq(f"C-e:call{i}.hi_coeffs", norm(call["hi"]), norm(hi))
    # C-f: primary's own p_at / rad_at on S_GRID distinct points (polynomial identity for degree <= 4)
    if ext is not None:
        for r, t in enumerate(ext["terms"]):
            me = mine["per_r"][r]
            for i in range(S_GRID):
                sv = rho * F(i, S_GRID - 1)
                eq(f"C-f:r{r}.p_at@{i}", tuple(TB.p_at(t, sv)), tuple(IT.peval(me[p], sv) for p in ("p0", "p1", "p2")))
                eq(f"C-f:r{r}.rad_at@{i}", TB.rad_at(t, S, sv), IT.peval(me["rad"], sv) + sv * me["abs_G"])
    # own-module consistency: harness lo/hi at S equals IT.profile_band on the grid
    lo, hi = my_lo_hi(mine, S)
    for i in range(S_GRID):
        sv = rho * F(i, S_GRID - 1)
        eq(f"self:band@{i}", (IT.peval(lo, sv), IT.peval(hi, sv)), IT.profile_band(mine, sv))
    # C-L: Lemma G supply against the frozen generic rule
    for name, src in (bundle.get("supply_sources") or {}).items():
        if src["kind"] == "lemma_G":
            k = [F(v) for v in meas["norms"]["k"]]
            fz = TB.T.atom_constants_generic(F(src["C_upper"]), k[1], k[2])
            mineG = IT.lemma_G(src["C_upper"], k)
            eq(f"C-L:{name}", tuple(fz[j] for j in ("A0", "A1", "A2")), mineG)
            # the cell supply cannot exceed a valid Lemma-G supply (combination is a minimum)
            eq(f"C-L:{name}.S_le_G", all(a <= b for a, b in zip(S, mineG)), True)
    return {"mismatches": mm, "checked": n, "status": out.get("status"), "stop_code": out.get("stop_code"),
            "gates": {g: v.get("pass") for g, v in (out.get("gates") or {}).items()},
            "tuple_digest": IT.digest(mine), "n_poly_calls": len(poly_calls)}


# ------------------------------------------------------------------------------------------------ T3 mutants

def _A(bundle):
    return TB.supply_from(bundle, bundle["meas"])[0]


def mut_fH_fG(frac):
    """Move mass between f_H and f_G with exact compensation so that rad_r(rho) is unchanged for the cell supply.
    frac > 0: f_H grows by frac*f_H and f_G shrinks; frac < 0: f_H shrinks and f_G grows."""
    def make(bundle):
        A0, A1, A2 = _A(bundle)
        rho = F(bundle["meas"]["rho"])
        wH = A0 + 2 * A1 * rho + A2 * rho ** 2 / 2          # d rad(rho) / d fH
        wG = A0 * rho + A1 * rho ** 2 + A2 * rho ** 3 / 6   # d rad(rho) / d fG

        def edit(t):
            x = frac * t["fH"]
            y = x * wH / wG
            if frac > 0:
                y = min(y, t["fG"] / 2)
                x = y * wG / wH
            t["fH"], t["fG"] = t["fH"] + x, t["fG"] - y
        return edit
    return make


def mut_env4_into_fF(bundle):
    """Drop Env4 and put its whole rad(rho) contribution into f_F (rad(rho) preserved; shape changed)."""
    A0, A1, A2 = _A(bundle)
    rho = F(bundle["meas"]["rho"])
    wE = A0 * rho ** 2 / 2 + A1 * rho ** 3 / 3 + A2 * rho ** 4 / 24
    wF = A2

    def edit(t):
        t["fF"] = t["fF"] + t["Env4"] * wE / wF
        t["Env4"] = F(0)
    return edit


def mut_env4_drop(bundle):
    def edit(t):
        t["Env4"] = F(0)
    return edit


def mut_centre_flip(bundle):
    def edit(t):
        lo, hi = t["H_at_a"]
        t["H_at_a"] = (-hi, -lo)
    return edit


def mut_fD_fF(bundle):
    """Move f_D mass into f_F with exact compensation (rad(rho) preserved)."""
    A0, A1, A2 = _A(bundle)
    rho = F(bundle["meas"]["rho"])
    wD = 2 * A1 + A2 * rho
    wF = A2

    def edit(t):
        x = t["fD"] / 2
        t["fD"] = t["fD"] - x
        t["fF"] = t["fF"] + x * wD / wF
    return edit


TUPLE_MUTANTS = {
    "fH_up_fG_down_compensated": mut_fH_fG(F(1, 3)),
    "fG_up_fH_down_compensated": mut_fH_fG(F(-1, 3)),
    "fD_into_fF_compensated": mut_fD_fF,
    "Env4_into_fF_compensated": mut_env4_into_fF,
    "Env4_dropped": mut_env4_drop,
    "centre_sign_flipped": mut_centre_flip,
}


def run_tuple_mutant(bundle, name, common_mode: bool):
    make = TUPLE_MUTANTS[name]
    edit = make(bundle)

    def mutate(ext):
        for t in ext["terms"]:
            edit(t)
    b = copy.deepcopy(bundle)
    orig_red = TB.rederive_tuple
    red_used = None
    if common_mode:
        b.setdefault("committed", {}).pop("per_r", None)

        def red_mut(meas, aux):
            out = orig_red(meas, aux)
            for r in out:
                edit(out[r])
            return out
        TB.rederive_tuple = red_mut
    try:
        out, ext, calls = run_primary(b, mutate)
        if common_mode:
            red_used = red_mut(b["meas"], b["aux"])
    finally:
        TB.rederive_tuple = orig_red
    res = compare(b, out, ext, calls, red=red_used)
    return res


def run_poly_mutant(bundle):
    """Planted in tpt.rad_poly (the polynomial the transport integrates): move mass between the s-linear and the
    s-quadratic coefficient of rad_r(s), exactly preserving rad_r(rho). The tuple is untouched."""
    orig = TPT.rad_poly

    def rad_poly_mut(cp, t):
        p = list(orig(cp, t)) + [F(0)] * 5
        d = p[2] * cp.rho / 2            # take half the s^2 mass (at s = rho) and put it on s^1
        p[1] += d
        p[2] -= d / cp.rho
        return p[:5]
    TPT.rad_poly = rad_poly_mut
    try:
        out, ext, calls = run_primary(copy.deepcopy(bundle))
    finally:
        TPT.rad_poly = orig
    return compare(bundle, out, ext, calls)


def _alt_sigmas(bundle) -> dict:
    """Two realistic (P3') misreadings, computed here from the independent towers:
    sigma4_N1_midpoint_tower  review-N1 class (unsound): the order-4 recursion run on the MIDPOINT order-3 slot
                              min(T[j,3], adoptedh(j)) without the rho mean-value correction;
    sigma3_from_cell_tower    sigma3 from the cell tower's corrected order-3 slot (sound but not the stated rule)."""
    from math import comb
    P = IT.parse(bundle["meas"], bundle["aux"])
    tw = IT.towers(P["k"], P["j"], P["sup_S0"], P["adopted3"], P["adoptedh"], P["rho"])
    T, Tm, Tc = tw["T"], tw["Tm"], tw["Tc"]
    k, jn = P["k"], P["j"]
    Tn = dict(Tm)
    Tn[1, 4] = T[1, 4]
    for jj in range(2, 5):
        Tn[jj, 4] = min(sum((comb(4, i) * k[i] * Tn[jj - 1, 4 - i] for i in range(5)), F(0)), T[jj, 4])
    s4 = {0: P["sup_S0"][4]}
    s3 = {0: tw["sigma3"][0]}
    for r in range(1, 5):
        s4[r] = sum((comb(4, i) * jn[i] * Tn[r, 4 - i] for i in range(5)), F(0))
        s3[r] = min(sum((comb(3, i) * jn[i] * Tc[r, 3 - i] for i in range(4)), F(0)), P["adopted3"][r])
    return {"sigma4_N1_midpoint_tower": s4, "sigma3_from_cell_tower": s3}


def run_rederive_defect(bundle, kind):
    """A defect planted only in tptb_tail.rederive_tuple (the primary's own cross-check), e.g. sigma4 from the pure
    tower (the review-N1 class: the rho mean-value correction lost) or sigma3 from the cell tower."""
    orig = TB.rederive_tuple
    mine = IT.tuple_tct(bundle["meas"], bundle["aux"], _A(bundle))
    tw = mine["towers"]

    def red_mut(meas, aux):
        out = orig(meas, aux)
        for r in out:
            if kind == "sigma4_pure_tower":
                d = tw["sigma4_pure"][r] - out[r]["sigma4"]
                out[r]["sigma4"] += d
                out[r]["Env4"] += d
            elif kind == "fG_without_eps_src3":
                out[r]["fG"] -= F(bundle["meas"]["r"][str(r)]["eps_src"][3])
            elif kind in ("sigma4_N1_midpoint_tower", "sigma3_from_cell_tower"):
                alt = _alt_sigmas(bundle)[kind][r]
                key = "sigma4" if kind.startswith("sigma4") else "sigma3"
                d = alt - out[r][key]
                out[r][key] += d
                out[r]["Env4" if key == "sigma4" else "fG"] += d
        return out
    TB.rederive_tuple = red_mut
    try:
        out, ext, calls = run_primary(copy.deepcopy(bundle))
        red = red_mut(bundle["meas"], bundle["aux"])
    finally:
        TB.rederive_tuple = orig
    return compare(bundle, out, ext, calls, red=red)


# ------------------------------------------------------------------------------------------------ branch coverage

def coverage(bundle) -> dict:
    """Which side of every min() of (P3') binds, measured with the independent towers."""
    from math import comb
    P = IT.parse(bundle["meas"], bundle["aux"])
    tw = IT.towers(P["k"], P["j"], P["sup_S0"], P["adopted3"], P["adoptedh"], P["rho"])
    T, Tm, Tc = tw["T"], tw["Tm"], tw["Tc"]
    c = {"sigma3_r0_adopted_binds": int(P["adopted3"][0] < P["sup_S0"][3]),
         "sigma3_r0_supS0_binds": int(P["adopted3"][0] >= P["sup_S0"][3]),
         "sigma3_r_adopted_binds": 0, "sigma3_r_tower_binds": 0, "Tm3_adopted_binds": 0, "Tm3_pure_binds": 0,
         "Tc3_corrected_binds": 0, "Tc3_pure_binds": 0, "Tc4_recursion_below_pure": 0, "Tc4_recursion_equal_pure": 0,
         "Tc4_clamp_fires": 0}
    for r in range(1, 5):
        tow = sum((comb(3, i) * P["j"][i] * Tm[r, 3 - i] for i in range(4)), F(0))
        c["sigma3_r_adopted_binds" if P["adopted3"][r] < tow else "sigma3_r_tower_binds"] += 1
    for jj in range(1, 5):
        c["Tm3_adopted_binds" if P["adoptedh"][jj] < T[jj, 3] else "Tm3_pure_binds"] += 1
        c["Tc3_corrected_binds" if P["adoptedh"][jj] + P["rho"] * T[jj, 4] < T[jj, 3] else "Tc3_pure_binds"] += 1
        if jj >= 2:
            rec = sum((comb(4, i) * P["k"][i] * Tc[jj - 1, 4 - i] for i in range(5)), F(0))
            c["Tc4_recursion_below_pure" if rec < T[jj, 4] else
              ("Tc4_recursion_equal_pure" if rec == T[jj, 4] else "Tc4_clamp_fires")] += 1
    return c


def variants(bundle) -> dict:
    """In-memory coverage variants of one decoy (synthetic; committed record dropped since it no longer applies):
    V_r0   the r = 0 adopted order-3 source bound made to bind (candidate 'Sclosed:0:3' := sup_S0[3] / 4)
    V_low  every adopted order-3 candidate supremum divided by 1000 (adopted side of every min binds)
    V_high every adopted order-3 candidate supremum multiplied by 1000 (pure-tower side of every min binds)"""
    out = {}
    b = copy.deepcopy(bundle)
    b.pop("committed", None)
    b["aux"]["candidate_suprema"]["Sclosed:0:3"] = str(F(b["meas"]["sup_S0"][3]) / 4)
    out["V_r0"] = b
    for name, fac in (("V_low", F(1, 1000)), ("V_high", F(1000))):
        b = copy.deepcopy(bundle)
        b.pop("committed", None)
        cs = b["aux"]["candidate_suprema"]
        for key in list(cs):
            cs[key] = str(F(cs[key]) * fac)
        out[name] = b
    return out


# ------------------------------------------------------------------------------------------------ main

def main() -> int:
    Q.install_import_guard()
    ds = DG.decoy_set()
    for b in ds:
        lab = b["label"]
        Q.guard_cell(lab["detector"], lab["m"], lab["cell"])
        Q.guard_drift(F(b["meas"]["left"]), F(b["meas"]["right"]))
    report = {"schema": "p5y.k5.c308-research.indep-tuple.compare.v1", "independent_module_sha256": FROZEN_SHA,
              "n_decoys": len(ds), "baseline": [], "mutants": {}, "summary": {}}
    # T2 baseline
    base_ok = True
    total_checks = 0
    for b in ds:
        out, ext, calls = run_primary(b)
        res = compare(b, out, ext, calls)
        res["decoy"] = {k: b["decoy_meta"][k] for k in ("index", "regime", "cap_mode", "nblocks",
                                                        "with_supply_sources", "e0_edge")}
        report["baseline"].append(res)
        total_checks += res["checked"]
        base_ok &= (not res["mismatches"]) and res["status"] == "OK"
    report["summary"]["baseline_all_equal_and_primary_OK"] = base_ok
    cov_tot = {}
    for b in ds:
        for key, v in coverage(b).items():
            cov_tot[key] = cov_tot.get(key, 0) + v
    report["summary"]["baseline_branch_coverage"] = cov_tot
    # coverage variants (T2 extension): same exact comparisons on in-memory variants of every decoy
    var_rows, var_ok, var_cov = [], True, {}
    for b in ds:
        for vname, vb in variants(b).items():
            out, ext, calls = run_primary(vb)
            res = compare(vb, out, ext, calls)
            for key, v in coverage(vb).items():
                var_cov[key] = var_cov.get(key, 0) + v
            var_rows.append({"index": b["decoy_meta"]["index"], "variant": vname, "mismatches": res["mismatches"],
                             "checked": res["checked"], "primary_status": res["status"],
                             "primary_stop": res["stop_code"], "n_poly_calls": res["n_poly_calls"]})
            var_ok &= not res["mismatches"]
    report["variants"] = var_rows
    report["summary"]["variants_all_equal"] = var_ok
    report["summary"]["variants_n"] = len(var_rows)
    report["summary"]["variants_exact_checks"] = sum(r["checked"] for r in var_rows)
    sts = [f"{r['primary_status']}/{r['primary_stop']}" for r in var_rows]
    report["summary"]["variants_primary_status"] = {st: sts.count(st) for st in sorted(set(sts))}
    report["summary"]["variants_branch_coverage"] = var_cov
    report["summary"]["baseline_exact_checks"] = total_checks
    report["summary"]["baseline_poly_calls_compared"] = sum(r["n_poly_calls"] for r in report["baseline"])
    # T3 mutants
    det_all = True
    for name in TUPLE_MUTANTS:
        for cm in (False, True):
            key = f"{name}{'__common_mode' if cm else ''}"
            rows = []
            for b in ds:
                res = run_tuple_mutant(b, name, cm)
                rows.append({"index": b["decoy_meta"]["index"], "detected": bool(res["mismatches"]),
                             "n_mismatch": len(res["mismatches"]), "first": res["mismatches"][:4],
                             "primary_status": res["status"], "primary_stop": res["stop_code"],
                             "G-R1_whole_cell_at_rho": res["gates"].get("G-R1"),
                             "G-R3_primary_coeff_gate": res["gates"].get("G-R3")})
            det = all(r["detected"] for r in rows)
            det_all &= det
            report["mutants"][key] = {
                "detected_on_all_decoys": det, "n": len(rows),
                "primary_G-R1_passed_on": sum(1 for r in rows if r["G-R1_whole_cell_at_rho"] is True),
                "primary_status_OK_on": sum(1 for r in rows if r["primary_status"] == "OK"),
                "primary_G-R3_passed_on": sum(1 for r in rows if r["G-R3_primary_coeff_gate"] is True),
                "rows": rows}
    rows = []
    for b in ds:
        res = run_poly_mutant(b)
        rows.append({"index": b["decoy_meta"]["index"], "detected": bool(res["mismatches"]),
                     "n_mismatch": len(res["mismatches"]), "first": res["mismatches"][:4],
                     "primary_status": res["status"], "primary_stop": res["stop_code"],
                     "G-R1_whole_cell_at_rho": res["gates"].get("G-R1")})
    det = all(r["detected"] for r in rows)
    det_all &= det
    report["mutants"]["rad_poly_linear_quadratic_shift_in_tpt"] = {
        "detected_on_all_decoys": det, "n": len(rows),
        "primary_G-R1_passed_on": sum(1 for r in rows if r["G-R1_whole_cell_at_rho"] is True),
        "primary_status_OK_on": sum(1 for r in rows if r["primary_status"] == "OK"), "rows": rows}
    for kind in ("sigma4_pure_tower", "fG_without_eps_src3", "sigma4_N1_midpoint_tower", "sigma3_from_cell_tower"):
        rows = []
        for b in ds:
            res = run_rederive_defect(b, kind)
            # a defect is only a defect where it changes a value; count only those decoys
            rows.append({"index": b["decoy_meta"]["index"], "detected": bool(res["mismatches"]),
                         "n_mismatch": len(res["mismatches"]), "first": res["mismatches"][:4],
                         "primary_status": res["status"], "primary_stop": res["stop_code"]})
        eff = []
        for b in ds:
            tw = IT.tuple_tct(b["meas"], b["aux"], _A(b))["towers"]
            if kind == "sigma4_pure_tower":
                eff.append(any(tw["sigma4"][r] != tw["sigma4_pure"][r] for r in range(5)))
            elif kind in ("sigma4_N1_midpoint_tower", "sigma3_from_cell_tower"):
                key = "sigma4" if kind.startswith("sigma4") else "sigma3"
                alt = _alt_sigmas(b)[kind]
                eff.append(any(alt[r] != tw[key][r] for r in range(5)))
            else:
                eff.append(True)
        report["mutants"][f"rederive_defect_{kind}"] = {
            "detected_on": sum(1 for r in rows if r["detected"]), "n": len(rows),
            "value_changing_on": sum(eff),
            "detected_exactly_where_value_changes": [r["detected"] for r in rows] == eff, "rows": rows}
        det_all &= [r["detected"] for r in rows] == eff
    report["summary"]["all_planted_mutants_detected"] = det_all
    out_dir = HERE.parent / "results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "COMPARE_TUPLE.json").write_text(json.dumps(report, indent=1, default=str) + "\n")
    print(json.dumps(report["summary"], indent=1))
    for k, v in report["mutants"].items():
        print(k, {x: v[x] for x in v if x != "rows"})
    print("variants", {k: report["summary"][k] for k in report["summary"] if k.startswith("variants")})
    print("coverage", report["summary"]["baseline_branch_coverage"])
    return 0 if (base_ok and det_all and var_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
