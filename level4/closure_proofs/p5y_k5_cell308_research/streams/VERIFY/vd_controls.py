"""Stream D, D4: negative (and positive) controls that travel through vd_verify.verify().

Every control states its expected verdict BEFORE the call; a FAIL verdict must come with a witness point, which is
re-evaluated by the second, independent pointwise evaluator vd_point.residual (exact fractions, different Phi/exp,
generic breakpoints, antiderivative integration).  Output: results/D4_CONTROLS.json.
Drifts used: 1/2, 1, 3, 7/2 only (declared, outside the quarantined band).
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_verify as V  # noqa: E402
import vd_adapt as AD  # noqa: E402
import vd_point as P  # noqa: E402

Q = V.Q
RESULTS = HERE / "results" / "D4_CONTROLS.json"


def cert(e: F, d: int) -> V.StripPW:
    path = HERE / "certs" / f"CERT_e{e.numerator}_{e.denominator}_d{d}.json"
    Q.guard_path(path)
    obj = json.loads(path.read_text())
    return AD.from_c1b_raw(obj["c1b_raw"])


def indep(W: V.StripPW, e, p, m, omit_atom=False):
    return P.residual(P.PW(W.to_json()), F(e), F(p), F(m), omit_atom)


def confirm(W, e, wit, omit_atom=False) -> dict:
    if not wit or "p" not in wit:
        return {"confirmed": False, "reason": "no point witness"}
    lo, hi = indep(W, e, wit["p"], wit["m"], omit_atom)
    return {"confirmed": hi < 0, "independent_residual_lo": lo, "independent_residual_hi": hi,
            "point": [wit["p"], wit["m"]]}


def with_poly_change(W: V.StripPW, strip: int, delta: dict) -> V.StripPW:
    polys = [dict(P_) for P_ in W.polys]
    for k, v in delta.items():
        polys[strip][k] = polys[strip].get(k, F(0)) + F(v)
        if polys[strip][k] == 0:
            del polys[strip][k]
    return V.StripPW(W.BW, polys)


def poly_of_t(coefs_t: list) -> dict:
    """sum_k a_k (p + m)^k as {(i, j): c}."""
    out: dict = {}
    for k, a in enumerate(coefs_t):
        for i in range(k + 1):
            c = F(a) * V.math.comb(k, i)
            if c:
                out[(i, k - i)] = out.get((i, k - i), F(0)) + c
    return out


def poly_mul_1d(a: list, b: list) -> list:
    o = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            o[i + j] += F(x) * F(y)
    return o


def summary(r: dict) -> dict:
    keep = ("verdict", "certified", "min_margin_lower_bound", "min_residual_upper_bound", "W_min_lower_bound",
            "W_at_atom", "witness_if_refuted", "seconds", "omit_atom", "drift", "sha256_W")
    s = {k: r.get(k) for k in keep}
    s["boxes"] = r["residual_bb"]["boxes"]
    return s


def record(out: list, name: str, expected: str, r: dict, extra: dict | None = None, observed=None,
           ok=None) -> dict:
    obs = observed if observed is not None else r["verdict"]
    rec = {"control": name, "expected": expected, "observed": obs,
           "control_pass": (obs == expected) if ok is None else ok, "verify": summary(r) if r else None}
    if extra:
        rec.update(extra)
    out.append(rec)
    print(json.dumps(V.jsonable({"control": name, "expected": expected, "observed": obs,
                                 "control_pass": rec["control_pass"]})), flush=True)
    RESULTS.write_text(json.dumps(V.jsonable({"schema": "VD_D4/1", "controls": out}), indent=1) + "\n")
    return rec


def run_all() -> list:
    out: list = []
    e3, e1, e72, e12 = F(3), F(1), F(7, 2), F(1, 2)
    W3 = cert(e3, 4)
    base = V.verify(W3, e3)
    record(out, "(0) positive: C1b cert e=3 d=4 at its own drift", "PASS", base)
    lb0, ub0 = base["min_margin_lower_bound"], base["min_residual_upper_bound"]

    # ---------------------------------------------------------------- (i) scaling ladder (1 - 2^-k) W
    ladder = []
    k = 20
    first_fail = None
    while k >= 1:
        s = 1 - F(1, 2 ** k)
        r = V.verify(W3.scaled(s), e3)
        ladder.append({"k": k, "verdict": r["verdict"], "min_lb": r["min_margin_lower_bound"],
                       "witness": r["witness_if_refuted"], "boxes": r["residual_bb"]["boxes"]})
        print(" ladder k", k, r["verdict"], flush=True)
        if r["verdict"] == "FAIL":
            first_fail = (k, r)
            break
        k -= 1
    verdicts = [x["verdict"] for x in ladder]
    monotone = all(v == "PASS" for v in verdicts[:-1]) and verdicts[-1] == "FAIL"
    extra = {"ladder": ladder, "monotone_PASS_then_FAIL": monotone}
    if first_fail:
        kf, rf = first_fail
        Wf = W3.scaled(1 - F(1, 2 ** kf))
        conf = confirm(Wf, e3, rf["witness_if_refuted"])
        # consistency: FAIL at kf => r_min(W) < 2^-kf/(1-2^-kf); PASS at kf+1 => r_min(W) >= 2^-(kf+1)/(1-2^-(kf+1))
        upper_from_fail = F(1, 2 ** kf) / (1 - F(1, 2 ** kf))
        lower_from_pass = F(1, 2 ** (kf + 1)) / (1 - F(1, 2 ** (kf + 1)))
        extra.update({"first_fail_k": kf, "witness_confirmation": conf,
                      "r_min_bracket_from_ladder": [lower_from_pass, upper_from_fail],
                      "r_min_bracket_from_base_run": [lb0, ub0],
                      "brackets_consistent": not (upper_from_fail < lb0 or ub0 < lower_from_pass)})
        record(out, "(i) (1-2^-k) W ladder: PASS for large k then FAIL; FAIL witness confirmed independently",
               "PASS...PASS,FAIL + confirmed witness", rf, extra,
               observed=",".join(verdicts) + (" + confirmed" if conf["confirmed"] else " + NOT confirmed"),
               ok=monotone and conf["confirmed"] and extra["brackets_consistent"])
    else:
        record(out, "(i) (1-2^-k) W ladder", "a FAIL for some k", None, extra, observed="no FAIL", ok=False)

    # ---------------------------------------------------------------- (ii) one coefficient perturbed
    Wp = with_poly_change(W3, 0, {(2, 2): -1})
    r = V.verify(Wp, e3)
    half = F(1, 2)
    base_pt = indep(W3, e3, half, half)
    pert_pt = indep(Wp, e3, half, half)
    record(out, "(ii-a) strip-1 coefficient of p^2 m^2 decreased by 1 (residual at (1/2,1/2) drops by exactly 1/16)",
           "FAIL", r, {"witness_confirmation": confirm(Wp, e3, r["witness_if_refuted"]),
                       "independent_residual_at_(1/2,1/2)_before": base_pt,
                       "independent_residual_at_(1/2,1/2)_after": pert_pt,
                       "exact_drop_check": (base_pt[0] - pert_pt[1] <= F(1, 16) <= base_pt[1] - pert_pt[0])})
    delta = F(1, 2 ** 20)
    Wq = with_poly_change(W3, 1, {(0, 0): delta})
    r = V.verify(Wq, e3)
    record(out, "(ii-b) strip-2 constant increased by 2^-20 < certified margin lower bound (residual moves by >= -2^-20)",
           "PASS" if lb0 is not None and lb0 > delta else "UNKNOWN", r,
           {"base_min_margin_lower_bound": lb0, "delta": delta})

    # ---------------------------------------------------------------- (iii) wrong drift
    for (ec, ew) in ((e3, e1), (F(1), e12), (e72, e3)):
        Wc = cert(ec, 4)
        r = V.verify(Wc, ew)
        record(out, f"(iii) certificate for e={ec} checked at e'={ew} (declared; Lambda(e') > Lambda(e))", "FAIL", r,
               {"witness_confirmation": confirm(Wc, ew, r["witness_if_refuted"])})

    # ---------------------------------------------------------------- (iv) W negative somewhere
    Wn = with_poly_change(W3, 3, {(0, 0): F(-50)})
    wv = Wn.value(F(9, 2), F(0))
    r = V.verify(Wn, e3)
    nn = V._run_bb(Wn, e3, False, "W", {"min_width": F(1, 2 ** 30), "max_boxes": 20000}, 3)
    record(out, "(iv) strip-4 constant lowered by 50 (W < 0 on t in (3,5]); verdict via verify()", "FAIL", r,
           {"W_value_at_(9/2,0)": wv, "witness_confirmation": confirm(Wn, e3, r["witness_if_refuted"]),
            "nonneg_check_alone": {k: nn.get(k) for k in ("status", "min_ub", "witness")},
            "nonneg_check_alone_refutes": nn["status"] == "REFUTED" or (nn["min_ub"] is not None and nn["min_ub"] < 0),
            "note": ("a bounded W with W >= 1 + K_e W is automatically >= 1 (inf W >= 1 + inf W otherwise), so a "
                     "negative W is always rejected by the residual check as well; the W >= 0 branch-and-bound is "
                     "exercised separately and must refute on its own")})
    # the nonnegativity branch-and-bound on its own
    record(out, "(iv-b) nonnegativity branch-and-bound alone on the same W", "REFUTED", {}, None,
           observed=nn["status"], ok=nn["status"] == "REFUTED")

    # ---------------------------------------------------------------- (v) atom window omitted
    r_no = V.verify(W3, e3, omit_atom=True)
    a_with = V.residual_point(V.Prep(W3, e3), F(0), F(0))
    a_without = V.residual_point(V.Prep(W3, e3, omit_atom=True), F(0), F(0))
    ind_with = indep(W3, e3, 0, 0)
    ind_without = indep(W3, e3, 0, 0, omit_atom=True)
    mass = (P.Phi(F(1, 2) + e3)[0] - P.Phi(e3 - F(1, 2))[1], P.Phi(F(1, 2) + e3)[1] - P.Phi(e3 - F(1, 2))[0])
    diff_lo, diff_hi = a_without[0] - a_with[1], a_without[1] - a_with[0]
    expect = (W3.at_atom() * mass[0], W3.at_atom() * mass[1])
    record(out, "(v-a) valid cert e=3: omitting the atom window changes the residual at the atom by W(a)*P(atom)",
           "residual changes by W(a)*(Phi(K+e)-Phi(e-K))", r_no,
           {"residual_at_atom_with": a_with, "residual_at_atom_without": a_without,
            "independent_with": ind_with, "independent_without": ind_without,
            "W(a)*atom_mass_enclosure": expect},
           observed="difference encloses W(a)*mass" if (diff_lo <= expect[1] and expect[0] <= diff_hi and
                                                          diff_lo > 0) else "MISMATCH",
           ok=diff_lo <= expect[1] and expect[0] <= diff_hi and diff_lo > 0)
    # planted: W1 - delta (1 - p - m)^2 on strip 1, at e = 1 (large atom mass)
    W1 = cert(e1, 4)
    notch1 = poly_of_t([F(1), F(-2), F(1)])          # (1 - t)^2
    chosen = None
    grid = [(F(i, 16), F(j, 16)) for i in range(17) for j in range(17) if i + j <= 16]
    pre_cache = {}
    for dl in (F(1, 4), F(1, 2), F(3, 4), F(1), F(3, 2), F(2)):
        Wv = with_poly_change(W1, 0, {k: -dl * c for k, c in notch1.items()})
        pw = V.Prep(Wv, e1)
        pn = V.Prep(Wv, e1, omit_atom=True)
        mw = min(V.residual_point(pw, p, m)[1] for p, m in grid)
        mn = min(V.residual_point(pn, p, m)[0] for p, m in grid)
        pre_cache[str(dl)] = {"min_with_hi": float(mw), "min_without_lo": float(mn)}
        if mw < 0 and mn > 0:
            chosen = dl
            break
    extra = {"delta_scan_on_t<=1_grid_1/16": pre_cache, "delta": chosen}
    if chosen is not None:
        Wv = with_poly_change(W1, 0, {k: -chosen * c for k, c in notch1.items()})
        r_w = V.verify(Wv, e1)
        r_n = V.verify(Wv, e1, omit_atom=True)
        extra.update({"verdict_with_atom": r_w["verdict"], "verdict_without_atom": r_n["verdict"],
                      "witness_confirmation_with_atom": confirm(Wv, e1, r_w["witness_if_refuted"]),
                      "verify_without_atom": summary(r_n)})
        record(out, "(v-b) planted W - delta(1-t)^2 on strip 1 at e=1: FAIL with the atom window, PASS without it",
               "FAIL with atom / PASS without", r_w, extra,
               observed=f"{r_w['verdict']} with atom / {r_n['verdict']} without",
               ok=r_w["verdict"] == "FAIL" and r_n["verdict"] == "PASS"
               and extra["witness_confirmation_with_atom"]["confirmed"])
    else:
        record(out, "(v-b) planted atom-dependent W", "a delta separating the verdicts", None, extra,
               observed="no delta found", ok=False)

    # ---------------------------------------------------------------- (vi) notched W valid at vertices, violated inside
    baseW = W3.scaled(1 + F(1, 32))
    g = [F(1)]
    for i in range(4, 9):
        g = poly_mul_1d(g, [F(-i), F(4)])              # prod_{i=4}^{8} (4t - i): zero at t = 1, 5/4, ..., 2
    gpm = poly_of_t(g)
    verts = []
    for i in range(17):
        for j in range(17):
            if i + j <= 16:
                verts.append((F(i, 4), F(j, 4)))
            if i < 16 and j < 16 and (2 * i + 1) + (2 * j + 1) <= 32:
                verts.append((F(2 * i + 1, 8), F(2 * j + 1, 8)))
    for i in range(1, 9):
        verts += [(4 + F(i, 8), F(0)), (F(0), 4 + F(i, 8))]
    chosen, scan = None, {}
    for A in (F(1, 2), F(1, 4), F(1, 8), F(1, 16)):
        Wn6 = with_poly_change(baseW, 1, {k: A * c for k, c in gpm.items()})
        pre = V.Prep(Wn6, e3)
        vmin = min(V.residual_point(pre, p, m)[0] for p, m in verts)
        inner = V.residual_point(pre, F(11, 16), F(11, 16))     # t = 11/8, inside the negative lobe (5/4, 3/2)
        scan[str(A)] = {"vertex_centre_min_lo": float(vmin), "inner_(11/16,11/16)_hi": float(inner[1])}
        if vmin > 0 and inner[1] < 0:
            chosen = A
            break
    extra = {"A_scan": scan, "A": chosen, "n_sample_points": len(verts)}
    if chosen is not None:
        Wn6 = with_poly_change(baseW, 1, {k: chosen * c for k, c in gpm.items()})
        pre = V.Prep(Wn6, e3)
        vals = [V.residual_point(pre, p, m) for p, m in verts]
        sub = verts[:: max(1, len(verts) // 12)]
        ind = [indep(Wn6, e3, p, m) for p, m in sub]
        extra.update({"all_vertices_and_centres_valid_rigorous": all(v[0] > 0 for v in vals),
                      "min_vertex_centre_residual_lo": min(v[0] for v in vals),
                      "independent_subset_valid": all(v[0] > 0 for v in ind), "independent_subset_size": len(sub)})
        r = V.verify(Wn6, e3)
        conf = confirm(Wn6, e3, r["witness_if_refuted"])
        extra["witness_confirmation"] = conf
        wit = r["witness_if_refuted"] or {}
        if "p" in wit:
            tw = F(wit["p"]) + F(wit["m"])
            extra["witness_t"] = tw
            extra["witness_is_not_a_sample_point"] = (F(wit["p"]), F(wit["m"])) not in set(verts)
        record(out, "(vi) notched W: (1+2^-5)W + A*prod(4t-i) on strip 2, valid at every initial-grid vertex and "
                    "centre, violated inside", "FAIL", r, extra,
               ok=r["verdict"] == "FAIL" and conf["confirmed"] and extra["all_vertices_and_centres_valid_rigorous"])
    else:
        record(out, "(vi) notched W", "an A with valid samples and an inner violation", None, extra,
               observed="no A found", ok=False)
    return out


if __name__ == "__main__":
    Q.log_event("streams/VERIFY/vd_controls.py", "D4 negative/positive controls of the independent verifier at "
                "declared non-target drifts 1/2, 1, 3, 7/2", klass="NONTARGET_DRIFT_VALIDATION", agent="streamD")
    t0 = time.time()
    out = run_all()
    doc = {"schema": "VD_D4/1", "controls": out, "all_controls_pass": all(c["control_pass"] for c in out),
           "seconds": round(time.time() - t0, 1)}
    RESULTS.write_text(json.dumps(V.jsonable(doc), indent=1) + "\n")
    print("ALL_CONTROLS_PASS", doc["all_controls_pass"])
