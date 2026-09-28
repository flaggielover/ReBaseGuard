"""Stream D, D6(b): controls of the PL verifier, every one through vd_pl.verify_pl().

Base objects: stream-A0 stored C2b P1 supersolutions (read-only) at declared drifts.  Every FAIL must carry a centroid
witness that the independent evaluator vd_point (generic breakpoints, exact antiderivatives) confirms.  The
vertex-only control (7) builds a candidate whose residual is RIGOROUSLY >= 0 at every mesh node but negative inside a
triangle: (1 - s) W with s strictly between the interior minimum ratio and the node minimum ratio of r/(1 + r).
Output: results/D6_PL_CONTROLS.json.
"""
from __future__ import annotations

import json
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
OUT = HERE / "results" / "D6_PL_CONTROLS.json"
WORKERS = 3


def load(name: str):
    W, cert = PLm.load_a0(A0 / name)
    return W, F(cert["drift"]), F(cert["claim_w_atom"])


def confirm(W: PLm.PLW, e, wit, omit_atom=False) -> dict:
    if not wit or "p" not in wit:
        return {"confirmed": False, "reason": "no point witness"}
    lo, hi = P.residual(P.make(W.to_json()), F(e), F(wit["p"]), F(wit["m"]), omit_atom)
    return {"confirmed": hi < 0, "independent_residual_lo": lo, "independent_residual_hi": hi,
            "point": [wit["p"], wit["m"]]}


def summ(r: dict) -> dict:
    keys = ("verdict", "certified", "direction", "drift", "N", "min_margin_lower_bound", "min_residual_upper_bound",
            "W_min_node", "W_at_atom", "witness_if_refuted", "boxes", "seconds", "claim_mismatch",
            "W_at_atom_equals_claim", "early_exit_on_witness", "sha256_W")
    return {k: r.get(k) for k in keys if k in r}


def record(out, name, expected, observed, ok, r=None, extra=None):
    rec = {"control": name, "expected": expected, "observed": observed, "control_pass": bool(ok),
           "verify": summ(r) if r else None}
    if extra:
        rec.update(extra)
    out.append(rec)
    print(json.dumps(V.jsonable({"control": name, "expected": expected, "observed": observed, "pass": bool(ok)})),
          flush=True)
    OUT.write_text(json.dumps(V.jsonable({"schema": "VD_D6_PL_CONTROLS/1", "controls": out}), indent=1) + "\n")


def nodes_of(W: PLm.PLW) -> list:
    return [(F(i, W.N), F(j, W.N)) for i, col in enumerate(W.w) for j in range(len(col))]


def node_residuals(W: PLm.PLW, e) -> list:
    E = PLm.Engine(W, F(e))
    return [(p, m, E.point_residual(p, m)) for p, m in nodes_of(W)]


def run_all() -> list:
    out: list = []
    W3, e3, claim3 = load("C2B_SUPER_e3_N20.json")
    base = PLm.verify_pl(W3, e3, workers=WORKERS, claim=claim3)
    record(out, "(0) positive: A0 C2B_SUPER e=3 N=20 at its own drift, claim checked", "PASS", base["verdict"],
           base["verdict"] == "PASS" and base["W_at_atom_equals_claim"], base)
    N = W3.N

    # (1) interior node lowered
    i, j = N // 2, N // 2
    Wn = W3.with_node(i, j, W3.w[i][j] - F(1, 64))
    r = PLm.verify_pl(Wn, e3, workers=WORKERS)
    c = confirm(Wn, e3, r["witness_if_refuted"])
    record(out, f"(1) node ({i},{j}) = ({F(i, N)},{F(j, N)}) lowered by 1/64", "FAIL + confirmed witness",
           r["verdict"] + (" + confirmed" if c["confirmed"] else " + NOT confirmed"),
           r["verdict"] == "FAIL" and c["confirmed"], r, {"witness_confirmation": c})

    # (2a) atom node lowered; (2b) atom node raised (inequality may hold, claim must fail)
    Wd = W3.with_node(0, 0, W3.w[0][0] - F(1, 64))
    r = PLm.verify_pl(Wd, e3, workers=WORKERS, claim=claim3)
    c = confirm(Wd, e3, r["witness_if_refuted"])
    record(out, "(2a) atom node lowered by 1/64", "FAIL + confirmed witness",
           r["verdict"] + (" + confirmed" if c["confirmed"] else " + NOT confirmed"),
           r["verdict"] == "FAIL" and c["confirmed"], r, {"witness_confirmation": c})
    Wu = W3.with_node(0, 0, W3.w[0][0] + F(1, 4096))
    r = PLm.verify_pl(Wu, e3, workers=WORKERS, claim=claim3)
    r_noclaim = PLm.verify_pl(Wu, e3, workers=WORKERS)
    record(out, "(2b) atom node raised by 2^-12: inequality still certified, stored claim no longer equals W(a)",
           "inequality PASS, certificate FAIL (claim mismatch)",
           f"inequality {r_noclaim['verdict']}, certificate {r['verdict']} (claim_mismatch={r.get('claim_mismatch')})",
           r_noclaim["verdict"] == "PASS" and r["verdict"] == "FAIL" and r.get("claim_mismatch") is True, r,
           {"inequality_only": summ(r_noclaim)})

    # (3) scaling ladder
    ladder, fail = [], None
    for k in range(20, 0, -1):
        s = 1 - F(1, 2 ** k)
        r = PLm.verify_pl(W3.scaled(s), e3, workers=WORKERS)
        ladder.append({"k": k, "verdict": r["verdict"], "min_lb": r["min_margin_lower_bound"],
                       "witness": r["witness_if_refuted"]})
        print("  ladder", k, r["verdict"], flush=True)
        if r["verdict"] == "FAIL":
            fail = (k, r)
            break
    verd = [x["verdict"] for x in ladder]
    mono = bool(fail) and all(v == "PASS" for v in verd[:-1])
    extra = {"ladder": ladder}
    if fail:
        kf, rf = fail
        cf = confirm(W3.scaled(1 - F(1, 2 ** kf)), e3, rf["witness_if_refuted"])
        extra.update({"first_fail_k": kf, "witness_confirmation": cf,
                      "r_min_bracket_from_ladder": [F(1, 2 ** (kf + 1)) / (1 - F(1, 2 ** (kf + 1))),
                                                    F(1, 2 ** kf) / (1 - F(1, 2 ** kf))],
                      "r_min_bracket_from_base_run": [base["min_margin_lower_bound"],
                                                      base["min_residual_upper_bound"]]})
        lo_l, hi_l = extra["r_min_bracket_from_ladder"]
        extra["brackets_consistent"] = not (hi_l < base["min_margin_lower_bound"]
                                            or base["min_residual_upper_bound"] < lo_l)
        record(out, "(3) (1 - 2^-k) W, k = 20, 19, ...", "PASS...PASS,FAIL + confirmed witness",
               ",".join(verd) + (" + confirmed" if cf["confirmed"] else " + NOT confirmed"),
               mono and cf["confirmed"] and extra["brackets_consistent"], rf, extra)
    else:
        record(out, "(3) (1 - 2^-k) W", "a FAIL", "no FAIL", False, None, extra)

    # (4) wrong drift (towards smaller |e|: Lambda(e') > W_e(a))
    for name, ew in (("C2B_SUPER_e3_N20.json", F(1)), ("C2B_SUPER_e1_N20.json", F(1, 2)),
                     ("C2B_SUPER_e7_2_N20.json", F(3)), ("C2B_SUPER_e27_10_N20.json", F(11, 10))):
        Wc, ec, _ = load(name)
        r = PLm.verify_pl(Wc, ew, workers=WORKERS)
        c = confirm(Wc, ew, r["witness_if_refuted"])
        record(out, f"(4) {name} (e={ec}) checked at e'={ew}", "FAIL + confirmed witness",
               r["verdict"] + (" + confirmed" if c["confirmed"] else " + NOT confirmed"),
               r["verdict"] == "FAIL" and c["confirmed"], r, {"witness_confirmation": c})

    # (5) a negative node
    Wneg = W3.with_node(0, 5 * N, F(-1))
    r = PLm.verify_pl(Wneg, e3, workers=WORKERS)
    c = confirm(Wneg, e3, r["witness_if_refuted"])
    record(out, "(5) node (0, 5N) set to -1 (W < 0 near (0,5))", "FAIL + confirmed witness",
           r["verdict"] + (" + confirmed" if c["confirmed"] else " + NOT confirmed"),
           r["verdict"] == "FAIL" and c["confirmed"], r, {"witness_confirmation": c})

    # (6) atom window omitted: residual at the atom changes by exactly W(a) * P(atom window)
    Ew = PLm.Engine(W3, e3)
    En = PLm.Engine(W3, e3, omit_atom=True)
    a_w = Ew.point_residual(F(0), F(0))
    a_n = En.point_residual(F(0), F(0))
    Wp = P.make(W3.to_json())
    i_w = P.residual(Wp, e3, 0, 0)
    i_n = P.residual(Wp, e3, 0, 0, omit_atom=True)
    mass = (P.Phi(F(1, 2) + e3)[0] - P.Phi(e3 - F(1, 2))[1], P.Phi(F(1, 2) + e3)[1] - P.Phi(e3 - F(1, 2))[0])
    exp_ = (W3.at_atom() * mass[0], W3.at_atom() * mass[1])
    d_lo, d_hi = a_n[0] - a_w[1], a_n[1] - a_w[0]
    ok6 = d_lo <= exp_[1] and exp_[0] <= d_hi and d_lo > 0 and not (i_n[1] < a_n[0] or a_n[1] < i_n[0])
    r6 = PLm.verify_pl(W3, e3, workers=WORKERS, omit_atom=True)
    record(out, "(6) atom window omitted on the valid e=3 certificate", "residual at a rises by W(a)(Phi(K+e)-Phi(e-K))",
           "difference encloses W(a)*mass; independent evaluator agrees" if ok6 else "MISMATCH", ok6, r6,
           {"residual_at_atom_with": a_w, "residual_at_atom_without": a_n, "independent_with": i_w,
            "independent_without": i_n, "W(a)*mass": exp_})

    # (7) vertex-only-acceptable candidate
    extra = {}
    t0 = time.time()
    best = None
    for name in ("C2B_SUPER_e3_N20.json", "C2B_SUPER_e1_N20.json", "C2B_SUPER_e7_2_N20.json",
                 "C2B_SUPER_e1_2_N20.json"):
        Wb, eb, _ = load(name)
        nr = node_residuals(Wb, eb)
        node_min_lo = min(x[2][0] for x in nr)
        rb = PLm.verify_pl(Wb, eb, workers=WORKERS)
        r_int = rb["min_residual_upper_bound"]
        gap = node_min_lo / (1 + node_min_lo) - r_int / (1 + r_int)
        extra[name] = {"node_residual_min_lo": node_min_lo, "interior_centroid_min_hi": r_int,
                       "interior_at": rb["min_residual_upper_bound_at"], "ratio_gap": gap, "n_nodes": len(nr)}
        print("  vertex-only scan", name, float(node_min_lo), float(r_int), float(gap), flush=True)
        at = rb["min_residual_upper_bound_at"]
        two_d = at is not None and F(at[0]) > 0 and F(at[1]) > 0      # interior minimum inside a triangle
        extra[name]["interior_min_in_triangle"] = two_d
        if gap > 0 and two_d and (best is None or gap > best[3]):
            best = (name, Wb, eb, gap, node_min_lo, r_int)
    extra["scan_seconds"] = round(time.time() - t0, 1)
    if best is None:
        record(out, "(7) vertex-only-acceptable candidate", "a certificate with interior min < node min",
               "none found", False, None, extra)
        return out
    name, Wb, eb, gap, node_min_lo, r_int = best
    lo_ratio = r_int / (1 + r_int)
    hi_ratio = node_min_lo / (1 + node_min_lo)
    s = (lo_ratio + hi_ratio) / 2
    s = F(int(s * 2 ** 40), 2 ** 40)
    if not (lo_ratio < s < hi_ratio):
        s = (lo_ratio + hi_ratio) / 2
    Ws = Wb.scaled(1 - s)
    nr_s = node_residuals(Ws, eb)
    nodes_ok = all(x[2][0] > 0 for x in nr_s)
    rs = PLm.verify_pl(Ws, eb, workers=WORKERS)
    cs = confirm(Ws, eb, rs["witness_if_refuted"])
    wit = rs["witness_if_refuted"] or {}
    inside = False
    if "p" in wit:
        wp, wm = F(wit["p"]), F(wit["m"])
        inside = (wp * Ws.N).denominator != 1 or (wm * Ws.N).denominator != 1
    extra["witness_cell"] = wit.get("cell")
    extra.update({"base": name, "s": s, "s_window": [lo_ratio, hi_ratio],
                  "all_node_residuals_positive_rigorous": nodes_ok,
                  "min_node_residual_lo_candidate": min(x[2][0] for x in nr_s), "n_nodes_checked": len(nr_s),
                  "witness_confirmation": cs, "witness_not_a_node": inside})
    record(out, "(7) vertex-only-acceptable PL candidate (1 - s) W: residual > 0 at EVERY node, < 0 inside a triangle",
           "FAIL with a confirmed interior witness; all nodes valid",
           f"{rs['verdict']}; nodes valid={nodes_ok}; witness interior={inside}; confirmed={cs['confirmed']}",
           rs["verdict"] == "FAIL" and nodes_ok and inside and cs["confirmed"]
           and (wit.get("cell") or ["?"])[0] in ("L", "U"), rs, extra)
    return out


if __name__ == "__main__":
    if "--workers" in sys.argv:
        WORKERS = int(sys.argv[sys.argv.index("--workers") + 1])
    Q.log_event("streams/VERIFY/vd_pl_controls.py", "D6(b) controls of the independent PL verifier on stream-A0 C2b "
                "certificates (read-only) at declared drifts 1/2, 1, 11/10, 27/10, 3, 7/2",
                klass="NONTARGET_DRIFT_VALIDATION", agent="streamD")
    t0 = time.time()
    res = run_all()
    doc = {"schema": "VD_D6_PL_CONTROLS/1", "controls": res,
           "all_controls_pass": all(c["control_pass"] for c in res), "seconds": round(time.time() - t0, 1)}
    OUT.write_text(json.dumps(V.jsonable(doc), indent=1) + "\n")
    print("ALL_CONTROLS_PASS", doc["all_controls_pass"])
