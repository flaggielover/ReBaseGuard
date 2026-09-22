"""C11 Phase 12R -- the certifier's MEASURED runs, emitted as evidence.

Added during Phase 16 repair, in answer to adjudication findings 2, 3 and 8. Before this module
existed, every certifier result reached the verdict as a hand-copied Python literal in
`c11_result.py`, with no committed producer and (for the drift-aware family) no recorded depth or
panel count. Two of those literals were not reproducible. Nothing may reach the verdict that this
module did not measure.

It emits three sections.

IDENTITIES -- the manufactured cases of criterion N8, each with a producer. They were previously
asserted in prose with nothing to run.

POINTWISE REFUTATION -- the check whose absence caused the campaign's central error. At a SINGLE
state the kernel is evaluated exactly by `kernel_apply`, with no box bound and no subdivision, so

    L(x) = w(x) - 1 - (K_e w)(x)

is enclosed rigorously. If L(x).hi < 0 at any x in R, then no supersolution certificate for that w
can exist at ANY subdivision depth, with ANY sharpening of the box bound, on ANY amount of compute.
That is a REFUTATION of the candidate, not a measurement of the machinery. It costs ~0.4 s per state
against ~200 s for one depth-4 certification run, so it is what a candidate family must face first.

CERTIFICATION RUNS -- `supersolution_margin` at recorded (depth, panels), timed.
"""
from __future__ import annotations

import pathlib
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11_common as C
import c11_certifier as X

E_DEV = F(18355, 10000)          # the development drift; see N4 and erratum E4
G = X.G


def _f(iv) -> list[float]:
    return [float(iv.lo), float(iv.hi)]


# -------------------------------------------------------------------------------------------
# N8 identities
# -------------------------------------------------------------------------------------------
def identities() -> dict:
    out = {}

    # (1) standard-normal moments over a wide window must be exactly 1, 0, 1, 0, 3
    Ms = X.moments(F(-12), F(12), 4)
    out["standard_normal_moments"] = {
        "window": "[-12, 12]", "expected": [1, 0, 1, 0, 3],
        "enclosures": [_f(v) for v in Ms],
        "max_deviation": max(float(max(abs(v.lo - t), abs(v.hi - t)))
                             for v, t in zip(Ms, [1, 0, 1, 0, 3])),
        "pass": all(v.lo <= t <= v.hi for v, t in zip(Ms, [1, 0, 1, 0, 3]))}

    # (2) (K_e 1)(p,m) = 1 - h1(p,m): the kernel and the alarm probability are written by
    #     separate code paths, so agreement is not reachable by a shared mistake in either.
    one = {(0, 0): F(1)}
    rows, ok = [], True
    for p, m in [(F(0), F(0)), (F(3), F(1)), (F(0), F(5)), (F(5), F(0)), (F(2), F(2)),
                 (F(23, 5), F(0))]:
        k1 = X.kernel_apply(one, p, m, E_DEV)
        h1 = X.alarm_prob(p, m, E_DEV)
        sep = max(k1.lo - (G.Iv(1, 1) - h1).hi, (G.Iv(1, 1) - h1).lo - k1.hi)
        good = sep <= 0                      # the two rigorous enclosures intersect
        ok = ok and good
        rows.append({"state": [str(p), str(m)], "K_e_1": _f(k1),
                     "one_minus_h1": _f(G.Iv(1, 1) - h1),
                     "separation": float(sep), "intersect": bool(good)})
    out["kernel_vs_alarm_probability"] = {"states": rows, "pass": ok}

    # (3) the box bound must dominate the pointwise kernel -- at INTERIOR points, not only
    #     corners, and for a NON-CONSTANT w (adjudication finding 9).
    wnc = {(0, 0): F(4), (0, 1): F(-1, 2), (1, 0): F(1, 5)}
    rows, ok = [], True
    for (a, b, c, d) in ((F(0), F(1), F(0), F(1)), (F(1), F(2), F(0), F(1)),
                         (F(0), F(1), F(1), F(2)), (F(2), F(3), F(1), F(2)),
                         (F(4), F(5), F(0), F(1))):
        up = X.kernel_box_upper(wnc, a, b, c, d, E_DEV, 12).hi
        pts = []
        for i in range(4):
            for j in range(4):
                p = a + (b - a) * F(i, 3)
                m = c + (d - c) * F(j, 3)
                pts.append(X.kernel_apply(wnc, p, m, E_DEV).hi)
        worst = max(pts)
        good = up >= worst
        ok = ok and good
        rows.append({"box": [str(a), str(b), str(c), str(d)], "box_upper": float(up),
                     "max_pointwise": float(worst), "slack": float(up - worst),
                     "interior_points": len(pts), "dominates": bool(good)})
    out["box_bound_dominates"] = {"boxes": rows, "non_constant_w": True, "pass": ok}

    # (4) the vacuous-enclosure guard added by erratum E5 must actually refuse
    try:
        X.moments(F(-20), F(20), 4)
        refused = False
    except X.CertRefusal:
        refused = True
    out["vacuous_enclosure_guard"] = {
        "in_range_width_M0": float((Ms[0].hi - Ms[0].lo)),
        "out_of_range_refuses": refused, "pass": refused}

    out["ALL_PASS"] = all(v["pass"] for v in out.values() if isinstance(v, dict) and "pass" in v)
    return out


# -------------------------------------------------------------------------------------------
# Pointwise refutation
# -------------------------------------------------------------------------------------------
def _grid(n: int) -> list[tuple[F, F]]:
    ax = [F(5 * i, n - 1) for i in range(n)]
    return [(p, m) for p in ax for m in ax if (p + m <= 4) or p == 0 or m == 0]


def pointwise_refute(w: dict, e: F, n: int = 15) -> dict:
    """Rigorous upper bound on min_R L. Negative => no certificate exists at any depth."""
    worst, arg = None, None
    for p, m in _grid(n):
        L = X.poly_eval_iv(w, G.Iv(p, p), G.Iv(m, m)) - G.Iv(1, 1) - X.kernel_apply(w, p, m, e)
        if worst is None or L.hi < worst:
            worst, arg = L.hi, (str(p), str(m))
    return {"grid": f"{n}x{n} on R", "states": len(_grid(n)),
            "min_L_upper_bound": float(worst), "binding_state": arg,
            "REFUTED_AT_ANY_DEPTH": bool(worst < 0)}


# -------------------------------------------------------------------------------------------
def main() -> int:
    t_all = time.time()
    print("=== N8 identities ===", flush=True)
    ident = identities()
    for k, v in ident.items():
        if isinstance(v, dict):
            print(f"  {k:32s} pass={v.get('pass')}", flush=True)

    # the theoretical threshold, independently derivable: a constant w certifies iff w >= 1/min h1
    h1min = None
    for p, m in _grid(15):
        h = X.alarm_prob(p, m, E_DEV).lo
        if h1min is None or h < h1min:
            h1min = h
    threshold = float(1 / h1min)
    print(f"  1/min_R h1 ~ {threshold:.2f}", flush=True)

    candidates = [
        ("constant_9000",      {(0, 0): F(9000)},                                3, 16, True),
        ("constant_6000",      {(0, 0): F(6000)},                                3, 16, True),
        ("pm_A9_B13_10",   {(0, 0): F(9),  (1, 0): F(-13, 10), (0, 1): F(-13, 10)}, 3, 16, True),
        ("pm_A12_B2",      {(0, 0): F(12), (1, 0): F(-2),      (0, 1): F(-2)},      3, 16, True),
        ("pm_A20_B3",      {(0, 0): F(20), (1, 0): F(-3),      (0, 1): F(-3)},      3, 16, True),
        ("m_only_A99_10_B3_2", {(0, 0): F(99, 10), (0, 1): F(-3, 2)},            4, 16, True),
        ("m_only_A12_B3_2",    {(0, 0): F(12),     (0, 1): F(-3, 2)},            4, 16, True),
    ]

    print("\n=== pointwise refutation (exact kernel, no box bound, no depth) ===", flush=True)
    runs = {}
    for name, w, depth, panels, do_cert in candidates:
        t = time.time()
        pr = pointwise_refute(w, E_DEV)
        pr["seconds"] = round(time.time() - t, 1)
        runs[name] = {"w": {f"{i},{j}": str(c) for (i, j), c in sorted(w.items())},
                      "pointwise": pr}
        print(f"  {name:22s} min_L <= {pr['min_L_upper_bound']:+9.4f} at {pr['binding_state']}"
              f"  REFUTED={pr['REFUTED_AT_ANY_DEPTH']}  ({pr['seconds']}s)", flush=True)

    print("\n=== certification runs (rigorous, recorded settings) ===", flush=True)
    for name, w, depth, panels, do_cert in candidates:
        if not do_cert:
            continue
        if runs[name]["pointwise"]["REFUTED_AT_ANY_DEPTH"]:
            runs[name]["certification"] = {
                "not_run": "refuted pointwise; a certification run cannot succeed and is not spent"}
            print(f"  {name:22s} SKIPPED (refuted pointwise)", flush=True)
            continue
        t = time.time()
        r = X.supersolution_margin(w, E_DEV, depth=depth, panels=panels)
        sec = round(time.time() - t, 1)
        runs[name]["certification"] = {
            "depth": depth, "panels": panels, "boxes": r["boxes"],
            "margin_lower_bound": float(r["margin_lower_bound"]),
            "margin_exact": str(r["margin_lower_bound"]),
            "w_min_lower_bound": float(r["w_min_lower_bound"]),
            "certified": r["certified"], "seconds": sec,
            "statement": ("w >= 1 + K_e w on R, hence E_x[tau] <= w(x); w(atom) bounds the ARL at "
                          "the atom. This is the quantity the ORIGINAL certifier reports as Abar "
                          "(taboo_certify.certify_block full=True), NOT its tau field.")}
        print(f"  {name:22s} d={depth} pan={panels} boxes={r['boxes']:4d} "
              f"margin={float(r['margin_lower_bound']):+.5f} cert={r['certified']} ({sec}s)",
              flush=True)

    out = {"schema": "C11_CERT_RUNS/1",
           "campaign": "C11 -- N9 independent second-certifier closure",
           "purpose": ("every certifier number that reaches the verdict, measured by a committed "
                       "producer at recorded settings; replaces the hand-copied literals that "
                       "adjudication finding 8 showed were partly unreproducible"),
           "drift": {"value": str(E_DEV), "kind": "SINGLE RATIONAL POINT",
                     "limitation": ("the original certifies UNIFORMLY over the e-block "
                                    "[e_lo, e_hi]; this certifier has no interval-drift path, so "
                                    "it solves a strictly easier problem -- see erratum E4")},
           "identities": ident,
           "theoretical_threshold_constant_family": {
               "value": threshold,
               "meaning": "a CONSTANT w certifies iff w >= 1/min_R h1; nothing below it can work"},
           "candidates": runs,
           "total_seconds": round(time.time() - t_all, 1)}
    p = C.NS / "evidence" / "runs" / "C11_CERT_RUNS.json"
    sha = C.write_evidence(p, out)
    print(f"\nwrote {p.relative_to(C.REPO)}  sha256 {sha[:16]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
