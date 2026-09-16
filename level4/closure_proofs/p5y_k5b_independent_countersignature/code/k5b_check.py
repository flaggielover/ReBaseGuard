"""Independent verification of Theorem K5-B (p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md).

READ-ONLY, NON-CERTIFYING FOR K5, NO SCIENTIFIC COMPUTE. Nothing here evaluates the detector response R_{D,m},
reads a K1 record, or produces an order-3 object. Every function below is a synthetic exact-rational polynomial
(or, for the differentiability counterexample, an explicit piecewise polynomial). The checks target the theorem's
logic only.

Written from the theorem text, not from `p5y_k5_order3_readiness_audit/code/k5_minimality.py`. That module is
imported only in the cross-check `readiness_scan_agrees`, after both implementations are built.

Sections
  1. exact polynomial / interval / Sturm utilities (stdlib only, Fraction arithmetic)
  2. literal K5-B recurrences (theorem text) and the readiness-scan variant (gamma_0 = 0)
  3. symbolic spine: g' = -e R'', e^2 s' = g, g_k = (1-k) r_k, parity of R'', R'''
  4. soundness fuzz: every pass certificate is checked EXACTLY (Sturm) against g < 0
  5. adversarial counterexamples (premise necessity, sufficiency-only witnesses, strictness, tail restart)
  6. theorem hash inventory check

  python -B code/k5b_check.py run  [--out evidence/INDEPENDENT_VERIFICATION.json] [--adversarial-out ...]
  python -B code/k5b_check.py verify-hashes --repo-root ../../..
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
SEED = 20260916
INF = None  # +/- infinity is represented by None and handled explicitly; no float ever enters


# ---------------------------------------------------------------- 1. utilities

def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def peval(p, x):
    acc = F(0)
    for c in reversed(p):
        acc = acc * x + c
    return acc


def pder(p):
    return trim([i * p[i] for i in range(1, len(p))] or [F(0)])


def padd(p, q):
    n = max(len(p), len(q))
    return trim([(p[i] if i < len(p) else 0) + (q[i] if i < len(q) else 0) for i in range(n)])


def pscale(p, c):
    return trim([c * a for a in p])


def pmul(p, q):
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return trim(out)


def pshift_e(p, k):
    """Multiply by e^k."""
    return trim([F(0)] * k + list(p))


def prem(a, b):
    a, b = trim(a), trim(b)
    while len(a) >= len(b) and any(a):
        c = a[-1] / b[-1]
        shift = len(a) - len(b)
        for i, bc in enumerate(b):
            a[i + shift] -= c * bc
        a = trim(a[:-1]) if len(a) > 1 else [F(0)]
        if len(a) < len(b):
            break
    return trim(a)


def sturm_chain(p):
    chain = [trim(p), pder(p)]
    while any(chain[-1]) and len(chain[-1]) > 1:
        r = prem(chain[-2], chain[-1])
        if not any(r):
            break
        chain.append(pscale(r, F(-1)))
    return chain


def variations(chain, x):
    signs = [s for s in (peval(q, x) for q in chain) if s != 0]
    return sum(1 for a, b in zip(signs, signs[1:]) if (a > 0) != (b > 0))


def distinct_roots_open(p, a, b):
    """Number of distinct real roots of p in (a, b); requires p(a) != 0 != p(b) (Sturm, valid for non-squarefree p)."""
    if peval(p, a) == 0 or peval(p, b) == 0:
        raise ValueError("Sturm endpoints must not be roots")
    ch = sturm_chain(p)
    return variations(ch, a) - variations(ch, b)


def negative_on_closed(p, a, b):
    """EXACT: p < 0 on [a, b]."""
    return peval(p, a) < 0 and peval(p, b) < 0 and distinct_roots_open(p, a, b) == 0


def imul(x, y):
    c = [x[0] * y[0], x[0] * y[1], x[1] * y[0], x[1] * y[1]]
    return (min(c), max(c))


def ieval(p, lo, hi):
    """Naive Horner interval evaluation: a valid (outer) enclosure of p([lo, hi])."""
    acc = (F(0), F(0))
    for c in reversed(p):
        acc = imul(acc, (lo, hi))
        acc = (acc[0] + c, acc[1] + c)
    return acc


def range_enclosure(p, lo, hi, pieces):
    out = None
    for i in range(pieces):
        a = lo + (hi - lo) * i / pieces
        b = lo + (hi - lo) * (i + 1) / pieces
        e = ieval(p, a, b)
        out = e if out is None else (min(out[0], e[0]), max(out[1], e[1]))
    return out


def g_poly(R):
    return padd(R, pscale(pshift_e(pder(R), 1), F(-1)))


# ---------------------------------------------------------------- 2. K5-B recurrences

def _fmt(x):
    return None if x is None else str(x)


def k5b_literal(cells, mutation=None):
    """Theorem K5-B exactly as written. cells: list of dicts with Fraction fields
    x_lo, x_hi, rho, e0, R, D, H (pairs), M, L (Fraction or None = -inf). Cell 1 is cells[0], x_0 = 0.
    gamma_1 with L_1 = -inf is read as +inf (no bound), the only reading under which the text defines it."""
    rows, ell, gamma = [], F(0), F(0)
    for i, c in enumerate(cells):
        k = i + 1
        dx2 = c["x_hi"] ** 2 - c["x_lo"] ** 2
        if c["e0"] < 0:
            raise ValueError("hi(R - e0 D) = R.hi - e0 D.lo requires e0 >= 0")
        Dc = c["D"][1] if mutation == "wrong_corner" else c["D"][0]
        Gamma = (c["R"][1] - c["e0"] * Dc) + c["rho"] * c["x_hi"] * c["M"]
        L, Hlo = c["L"], c["H"][0]
        lt = (lambda a, b: a <= b) if mutation == "nonstrict" else (lambda a, b: a < b)
        if k == 1:
            if c["x_lo"] != 0:
                raise ValueError("x_0 must be 0")
            ell_k = Hlo if L is None else max(Hlo, 2 * c["rho"] * L)
            gamma_k = None if L is None else (1 if mutation == "gamma1_sign" else -1) * L * c["x_hi"] ** 3 / 3
            mu, U = None, None
            passed = (L is not None and lt(0, L)) or lt(Gamma, 0)
            via = "L1" if (L is not None and lt(0, L)) else ("direct" if lt(Gamma, 0) else None)
        else:
            drop = 2 * c["rho"] * L if (L is not None and mutation == "mu_uses_endpoint") else (
                min(F(0), 2 * c["rho"] * L) if L is not None else None)
            mu = Hlo if L is None else max(Hlo, ell + drop)
            ell_k = Hlo if L is None else max(Hlo, ell + 2 * c["rho"] * L)
            if gamma is None:
                U, gamma_k = None, Gamma
            else:
                U = max(gamma, gamma - mu * dx2 / 2)
                gamma_k = min(gamma - mu * dx2 / 2, Gamma)
            chain_ok = U is not None and lt(U, 0)
            passed = chain_ok or lt(Gamma, 0)
            via = "chain" if chain_ok else ("direct" if lt(Gamma, 0) else None)
        rows.append({"k": k, "mu": mu, "ell": ell_k, "U": U, "gamma": gamma_k, "Gamma": Gamma,
                     "pass": passed, "via": via})
        ell, gamma = ell_k, gamma_k
    return rows


def k5b_readiness_variant(cells):
    """The recurrence as implemented by k5_minimality.py (L_k = -inf everywhere, gamma_0 = 0, chain pass for k >= 2)."""
    rows, gamma = [], F(0)
    for i, c in enumerate(cells):
        Gamma = (c["R"][1] - c["e0"] * c["D"][0]) + c["rho"] * c["x_hi"] * c["M"]
        mu = c["H"][0]
        step = -mu * (c["x_hi"] ** 2 - c["x_lo"] ** 2) / 2
        U = max(gamma, gamma + step)
        passed = Gamma < 0 or (i > 0 and U < 0)
        rows.append({"k": i + 1, "U": U, "gamma": min(gamma + step, Gamma), "Gamma": Gamma, "pass": passed})
        gamma = min(gamma + step, Gamma)
    return rows


def all_pass(rows):
    return all(r["pass"] for r in rows)


# ---------------------------------------------------------------- synthetic enclosures

def make_cover(rng, right_min=F(2)):
    n = rng.randint(3, 12)
    first = F(rng.randint(1, 40), 200)
    pts = sorted({F(rng.randint(1, 1999), 1000) for _ in range(n)} | {first})
    pts = [p for p in pts if p >= first]
    xs = [F(0)] + pts
    if xs[-1] < right_min:
        xs.append(right_min + F(rng.randint(0, 20), 100))
    return xs


def synthetic_cells(R, xs, rng, *, pieces=16, widen=0, l_drop=0.0, l_slack=0, domain_right=F(2)):
    R1, R2, R3 = pder(R), pder(pder(R)), pder(pder(pder(R)))
    cells = []
    for a, b in zip(xs, xs[1:]):
        if a >= domain_right:
            break
        rho, e0 = (b - a) / 2, (a + b) / 2
        w = lambda: F(rng.randint(0, widen), 10 ** 6) if widen else F(0)
        r0, d0 = peval(R, e0), peval(R1, e0)
        H = range_enclosure(R2, a, b, pieces)
        H = (H[0] - w(), H[1] + w())
        L = None
        if rng.random() >= l_drop:
            L = range_enclosure(R3, a, b, pieces)[0] - (F(rng.randint(0, l_slack), 10 ** 4) if l_slack else 0)
        cells.append({"x_lo": a, "x_hi": b, "rho": rho, "e0": e0, "R": (r0 - w(), r0 + w()),
                      "D": (d0 - w(), d0 + w()), "H": H, "M": max(abs(H[0]), abs(H[1])), "L": L})
    return cells


def random_odd_poly(rng):
    R = [F(0)] * 10
    R[1] = -F(rng.randint(10, 200), 100)
    for k in (3, 5, 7, 9):
        R[k] = F(rng.randint(-60, 60), 10 ** rng.randint(2, 4))
    if rng.random() < 0.5:
        R[3] = abs(R[3]) + F(1, 50)
    return trim(R)


# ---------------------------------------------------------------- 3. symbolic spine

def symbolic_spine(rng, trials=200):
    checks = {"g_prime_eq_minus_e_R2": 0, "e2_sprime_eq_g": 0, "g_coeff_eq_(1-k)r_k": 0,
              "g_cubic_coeff_eq_-R3(0)/3": 0, "R2_odd_R3_even": 0, "sprime_linear_coeff_eq_-2a3": 0,
              "g_odd_divisible_by_e3": 0}
    for _ in range(trials):
        R = random_odd_poly(rng)
        g = g_poly(R)
        R2 = pder(pder(R))
        assert pder(g) == pscale(pshift_e(R2, 1), F(-1)); checks["g_prime_eq_minus_e_R2"] += 1
        s = pscale(R[1:], F(-1))                       # s = -R/e, a polynomial because R(0) = 0
        assert pshift_e(pder(s), 2) == g; checks["e2_sprime_eq_g"] += 1
        assert all((g[k] if k < len(g) else 0) == (1 - k) * R[k] for k in range(len(R))); checks["g_coeff_eq_(1-k)r_k"] += 1
        R3_0 = peval(pder(R2), F(0))
        assert (g[3] if len(g) > 3 else 0) == -R3_0 / 3 and R[3] == R3_0 / 6; checks["g_cubic_coeff_eq_-R3(0)/3"] += 1
        assert all(c == 0 for c in R2[0::2]) and all(c == 0 for c in pder(R2)[1::2]); checks["R2_odd_R3_even"] += 1
        sp = pder(s)
        assert (sp[1] if len(sp) > 1 else 0) == -2 * R[3]; checks["sprime_linear_coeff_eq_-2a3"] += 1
        assert g[:3] == [0, 0, 0][:len(g[:3])]; checks["g_odd_divisible_by_e3"] += 1
    return {"trials": trials, "checks": checks, "status": "PASS",
            "general_proofs": {
                "g_prime": "g = R - eR'  =>  g' = R' - R' - eR'' = -eR''",
                "s_prime": "s = -R/e  =>  s' = (-eR' + R)/e^2 = g/e^2  (e > 0); sign(s') = sign(g)",
                "coefficients": "R = sum r_k e^k  =>  eR' = sum k r_k e^k  =>  g = sum (1-k) r_k e^k; odd R => g = -2 r3 e^3 - 4 r5 e^5 - ...",
                "parity": "R odd => R' even => R'' odd (R''(0) = 0) => R''' even",
                "a3": "r3 = R'''(0)/3! = R'''(0)/6"}}


# ---------------------------------------------------------------- 4. soundness fuzz

def exact_h3a_g_part(R):
    """EXACT: g < 0 on (0, 2]. g = e^3 q with q even; returns (holds, q(0))."""
    g = g_poly(R)
    q = trim(g[3:]) if len(g) > 3 else [F(0)]
    q0 = peval(q, F(0))
    if q0 > 0 or peval(q, F(2)) >= 0:
        return False, q0
    if q0 == 0:
        return None, q0                                 # degenerate a3 = 0: decided by a finer argument, not needed here
    return distinct_roots_open(q, F(0), F(2)) == 0, q0


def cell_negative_exact(R, a, b):
    g = g_poly(R)
    q = trim(g[3:]) if len(g) > 3 else [F(0)]
    lo = a if a > 0 else F(0)
    return negative_on_closed(q, lo, b)


def invariants_hold(R, cells, rows):
    """Per-cell bound validity: ell_k <= R''(x_k); gamma_k >= g(x_k); Gamma_1 >= 0; U_k and Gamma_k >= g on a grid."""
    R2, g = pder(pder(R)), g_poly(R)
    for c, r in zip(cells, rows):
        if r["ell"] > peval(R2, c["x_hi"]):
            return "ell"
        if r["gamma"] is not None and r["gamma"] < peval(g, c["x_hi"]):
            return "gamma"
        if r["k"] == 1 and r["Gamma"] < 0:
            return "Gamma_1_negative"
        grid = [c["x_lo"] + (c["x_hi"] - c["x_lo"]) * j / 32 for j in range(33)]
        gm = max(peval(g, t) for t in grid)
        if r["Gamma"] < gm or (r["U"] is not None and r["U"] < gm):
            return "cell_sup"
        if r["mu"] is not None and r["mu"] > min(peval(R2, t) for t in grid):
            return "mu"
    return None


def soundness_fuzz(rng, polys=160):
    stats = {"polynomials": polys, "cell_configurations": 0, "cells_checked": 0, "cell_passes_exactly_verified": 0,
             "passes_by": {"L1": 0, "chain": 0, "direct": 0}, "full_theorem_passes": 0,
             "full_passes_exactly_verified": 0, "invariant_violations": 0, "soundness_violations": 0,
             "h3a_g_part_true_but_theorem_failed": 0, "variant_equivalence_checked_with_Hlo_le_0": 0,
             "variant_equivalence_violations": 0, "variant_divergences_with_some_Hlo_gt_0": 0,
             "readiness_variant_soundness_violations": 0}
    configs = [dict(pieces=64, widen=0, l_drop=0.0, l_slack=0), dict(pieces=16, widen=0, l_drop=0.0, l_slack=5),
               dict(pieces=4, widen=50, l_drop=0.3, l_slack=50), dict(pieces=64, widen=0, l_drop=0.6, l_slack=0),
               dict(pieces=1, widen=0, l_drop=1.0, l_slack=0)]
    for _ in range(polys):
        R = random_odd_poly(rng)
        truth, q0 = exact_h3a_g_part(R)
        for cfg in configs:
            xs = make_cover(rng)
            cells = synthetic_cells(R, xs, rng, **cfg)
            rows = k5b_literal(cells)
            stats["cell_configurations"] += 1
            if invariants_hold(R, cells, rows):
                stats["invariant_violations"] += 1
            for c, r in zip(cells, rows):
                stats["cells_checked"] += 1
                if r["pass"]:
                    stats["passes_by"][r["via"]] += 1
                    if cell_negative_exact(R, c["x_lo"], min(c["x_hi"], max(c["x_hi"], F(0)))):
                        stats["cell_passes_exactly_verified"] += 1
                    else:
                        stats["soundness_violations"] += 1
            if all_pass(rows):
                stats["full_theorem_passes"] += 1
                if truth is True:
                    stats["full_passes_exactly_verified"] += 1
                else:
                    stats["soundness_violations"] += 1
            elif truth is True:
                stats["h3a_g_part_true_but_theorem_failed"] += 1
            # readiness-scan variant: gamma_0 = 0, L = -inf
            cells_noL = [{**c, "L": None} for c in cells]
            var = k5b_readiness_variant(cells_noL)
            for c, r in zip(cells_noL, var):
                if r["pass"] and not cell_negative_exact(R, c["x_lo"], c["x_hi"]):
                    stats["readiness_variant_soundness_violations"] += 1
            lit = k5b_literal(cells_noL)
            same = [a["pass"] for a in lit] == [b["pass"] for b in var]
            if all(c["H"][0] <= 0 for c in cells_noL):
                stats["variant_equivalence_checked_with_Hlo_le_0"] += 1
                if not same:
                    stats["variant_equivalence_violations"] += 1
            elif not same:
                stats["variant_divergences_with_some_Hlo_gt_0"] += 1
            # forced H.lo <= 0 (a valid widening) so the equivalence lemma is exercised on every configuration
            forced = [{**c, "H": (min(c["H"][0], F(0)), c["H"][1])} for c in cells_noL]
            forced = [{**c, "M": max(abs(c["H"][0]), abs(c["H"][1]))} for c in forced]
            stats["variant_equivalence_checked_with_Hlo_le_0"] += 1
            if [a["pass"] for a in k5b_literal(forced)] != [b["pass"] for b in k5b_readiness_variant(forced)]:
                stats["variant_equivalence_violations"] += 1
    stats["status"] = "PASS" if (stats["soundness_violations"] == 0 and stats["invariant_violations"] == 0
                                 and stats["variant_equivalence_violations"] == 0
                                 and stats["readiness_variant_soundness_violations"] == 0
                                 and stats["full_passes_exactly_verified"] > 0) else "FAIL"
    return stats


MUTATIONS = ("nonstrict", "wrong_corner", "gamma1_sign", "mu_uses_endpoint")


def mutation_sensitivity(rng, polys=60):
    """The fuzz oracle must be able to fail: each deliberately broken recurrence has to be caught (an exact
    soundness counterexample, or a per-cell bound invariant violated)."""
    caught = {m: {"soundness": 0, "invariant": 0} for m in MUTATIONS}
    extra = [[F(0), F(-1, 2)], [F(0), F(-1, 2), F(0), F(1, 10)]]
    polys_list = extra + [random_odd_poly(rng) for _ in range(polys)]
    for R in polys_list:
        for cfg in (dict(pieces=64), dict(pieces=16, widen=200, l_slack=4000), dict(pieces=4, widen=2000, l_slack=40000)):
            xs = make_cover(rng)
            cells = synthetic_cells(R, xs, rng, **cfg)
            for m in MUTATIONS:
                rows = k5b_literal(cells, mutation=m)
                if invariants_hold(R, cells, rows):
                    caught[m]["invariant"] += 1
                for c, r in zip(cells, rows):
                    if r["pass"] and not cell_negative_exact(R, c["x_lo"], c["x_hi"]):
                        caught[m]["soundness"] += 1
    return {"mutations": caught,
            "status": "PASS" if all(v["soundness"] + v["invariant"] > 0 for v in caught.values()) else "FAIL"}


# ---------------------------------------------------------------- 5. adversarial counterexamples

def exact_cells(R, xs, L_override=None, H_override=None, M_override=None):
    rng = random.Random(0)
    cells = synthetic_cells(R, xs, rng, pieces=256)
    for i, c in enumerate(cells):
        if L_override and i in L_override:
            c["L"] = L_override[i]
        if H_override and i in H_override:
            c["H"] = H_override[i]
            c["M"] = max(abs(c["H"][0]), abs(c["H"][1]))
        if M_override and i in M_override:
            c["M"] = M_override[i]
    return cells


def adversarial():
    out = {}
    xs = [F(0), F(1, 8), F(1, 4), F(1, 2), F(1), F(3, 2), F(2)]

    # A1 wrong R''' sign near zero
    R = [F(0), F(-1, 2), F(0), F(-1, 10)]
    cells = exact_cells(R, xs)
    rows = k5b_literal(cells)
    truth, q0 = exact_h3a_g_part(R)
    sup_R3_cell1 = range_enclosure(pder(pder(pder(R))), F(0), xs[1], 1)[1]
    g_pos_cell1 = negative_on_closed(pscale(trim(g_poly(R)[3:]), F(-1)), F(0), xs[1])
    out["A1_wrong_R3_sign_near_zero"] = {
        "R": "-e/2 - e^3/10  (a3 = -1/10)", "L_1": str(cells[0]["L"]), "cell1_pass": rows[0]["pass"],
        "certified_sup_R3_cell1": str(sup_R3_cell1), "g_positive_on_(0,x1]_exact": g_pos_cell1, "h3a_g_part": truth,
        "verdict": "theorem cannot pass (L_1 <= inf R''' < 0); sup R''' < 0 on C_1 forces g > 0 there, i.e. H3a false: "
                   "the counterexample direction in K5_GLOBAL_BRIDGE.md is correct",
        "ok": (not rows[0]["pass"]) and g_pos_cell1 and truth is False}

    # A2 R''' unavailable, R'' locally favourable
    R = [F(0), F(-1, 2), F(0), F(1, 10)]
    cells = exact_cells(R, xs, L_override={i: None for i in range(6)})
    rows = k5b_literal(cells)
    truth, _ = exact_h3a_g_part(R)
    out["A2_R3_unavailable_R2_favourable"] = {
        "R": "-e/2 + e^3/10  (R'' = 3e/5 >= 0, g = -e^3/5 < 0)", "H_1": [str(x) for x in cells[0]["H"]],
        "Gamma_1": str(rows[0]["Gamma"]), "cell1_pass": rows[0]["pass"], "h3a_g_part": truth,
        "verdict": "Gamma_1 >= g(0) = 0 for every valid enclosure and H_1.lo <= 0, so cell 1 can never pass without "
                   "L_1 > 0, although H3a holds: order-3 is necessary FOR THIS ROUTE at 0, and failure is not refutation",
        "ok": (not rows[0]["pass"]) and rows[0]["Gamma"] >= 0 and truth is True}

    # A3 chain lower bound too weak (loose L) vs tight L on the same function
    R = [F(0), F(-1, 2), F(0), F(1, 10), F(0), F(-1, 400)]
    tight = k5b_literal(exact_cells(R, xs))
    loose = k5b_literal(exact_cells(R, xs, L_override={0: F(1, 1000), 1: F(-50), 2: F(-50), 3: F(-50), 4: F(-50), 5: F(-50)},
                                    H_override={i: (F(-40), F(40)) for i in range(1, 6)}))
    truth, _ = exact_h3a_g_part(R)
    out["A3_chain_lower_bound_too_weak"] = {
        "R": "-e/2 + e^3/10 - e^5/400", "tight_all_pass": all_pass(tight), "loose_all_pass": all_pass(loose),
        "loose_first_failing_cell": next((r["k"] for r in loose if not r["pass"]), None), "h3a_g_part": truth,
        "verdict": "same function, valid but loose inputs: the theorem fails; with tight inputs it passes. Sufficient only.",
        "ok": all_pass(tight) and not all_pass(loose) and truth is True}

    # A4 strictness: g == 0 identically (s constant, H3a FALSE) and g touching 0 at a cell boundary (H3a TRUE)
    R = [F(0), F(-1, 2)]
    rows = k5b_literal(exact_cells(R, xs, L_override={0: F(0)}))
    nonstrict = all((r["k"] == 1 and exact_cells(R, xs)[0]["L"] >= 0) or (r["U"] is not None and r["U"] <= 0) or r["Gamma"] <= 0 for r in rows)
    c2 = F(1)
    # g = -e^3 (e^2 - c^2)^2 ; r_k = g_k/(1-k): r3 = c^4/2, r5 = -c^2/2, r7 = 1/6
    Rt = [F(0), F(-1, 2), F(0), c2 ** 2 / 2, F(0), -c2 / 2, F(0), F(1, 6)]
    gt = g_poly(Rt)
    touch_ok = peval(gt, F(1)) == 0 and all(peval(gt, F(j, 16)) <= 0 for j in range(1, 33))
    rows_t = k5b_literal(exact_cells(Rt, xs))
    cell_with_touch = [r for c, r in zip(exact_cells(Rt, xs), rows_t) if c["x_lo"] <= 1 <= c["x_hi"]]
    out["A4_strictness_at_boundary"] = {
        "linear_R": "-e/2: g == 0, s constant => H3a false", "strict_theorem_all_pass": all_pass(rows),
        "nonstrict_variant_would_pass": nonstrict,
        "touch_R": "g = -e^3 (e^2-1)^2, touches 0 at the cell boundary e = 1 (s' <= 0 with an isolated zero: H3a TRUE)",
        "touch_g_le_0_and_g(1)=0": touch_ok, "touch_theorem_all_pass": all_pass(rows_t),
        "touch_cells_containing_1_pass": [r["pass"] for r in cell_with_touch],
        "verdict": "strict '<' is what keeps the linear case out (a '<=' implementation would certify a false H3a). "
                   "A touching g cannot be certified by any valid enclosure (U_k, Gamma_k >= g(1) = 0 on both adjacent "
                   "cells) although H3a holds: the degenerate case the theorem text disclaims.",
        "ok": (not all_pass(rows)) and nonstrict and touch_ok and not any(r["pass"] for r in cell_with_touch)}

    # A5 valid local g < 0 but failed propagated bound
    R = [F(0), F(-1, 2), F(0), F(1, 10)]
    cells = exact_cells(R, xs, H_override={3: (F(-30), F(30))}, L_override={3: None})
    rows = k5b_literal(cells)
    local = cell_negative_exact(R, cells[3]["x_lo"], cells[3]["x_hi"])
    out["A5_local_g_negative_chain_fails"] = {
        "R": "-e/2 + e^3/10", "cell": 4, "exact_g_negative_on_cell": local, "cell_pass": rows[3]["pass"],
        "U": str(rows[3]["U"]), "Gamma": str(rows[3]["Gamma"]),
        "verdict": "g < 0 exactly on the cell; a wide (valid) H and no L break both the chain and the direct test",
        "ok": local and not rows[3]["pass"]}

    # A6 differentiability premise violated: R'' jumps at e = 1/2 (R''' has a negative atom)
    # R''(t) = t on [0,1/2], -10 on (1/2, 2]; R''' = 1 a.e. on (0,1/2), 0 a.e. on (1/2,2); R odd by extension.
    ys = [F(0), F(1, 2), F(1), F(3, 2), F(2)]
    def g_piece(e):                                   # g(e) = -int_0^e t R''(t) dt
        if e <= F(1, 2):
            return -e ** 3 / 3
        return -F(1, 24) + 10 * (e ** 2 - F(1, 4)) / 2
    def R_piece(e):                                   # R' = -1/2 + int R'', R = int R'
        if e <= F(1, 2):
            return -e / 2 + e ** 3 / 6
        a = F(1, 2)
        R1a = -F(1, 2) + a ** 2 / 2
        Ra = -a / 2 + a ** 3 / 6
        return Ra + R1a * (e - a) - 10 * (e - a) ** 2 / 2
    def R1_piece(e):
        return -F(1, 2) + e ** 2 / 2 if e <= F(1, 2) else -F(1, 2) + F(1, 8) - 10 * (e - F(1, 2))
    cells = []
    for i, (a, b) in enumerate(zip(ys, ys[1:])):
        e0 = (a + b) / 2
        H = (F(0), F(1, 2)) if i == 0 else (F(-10), F(-10) if i > 0 else F(0))
        if i == 1:
            H = (F(-10), F(1, 2))                    # closed cell [1/2,1] includes R''(1/2) = 1/2
        L = F(1) if i == 0 else F(0)                 # "inf R'''" over the smooth pieces only
        r0, d0 = R_piece(e0), R1_piece(e0)
        assert abs(d0 - (R_piece(e0 + F(1, 10 ** 9)) - r0) * 10 ** 9) < F(1, 10 ** 6)
        cells.append({"x_lo": a, "x_hi": b, "rho": (b - a) / 2, "e0": e0, "R": (r0, r0), "D": (d0, d0),
                      "H": H, "M": max(abs(H[0]), abs(H[1])), "L": L})
    rows = k5b_literal(cells)
    out["A6_differentiability_premise_violated"] = {
        "R''": "t on [0,1/2]; -10 on (1/2,2]  (R in C^1, not C^2; R''' has a -21/2 atom at 1/2)",
        "theorem_all_pass_with_piecewise_L": all_pass(rows), "g(2)": str(g_piece(F(2))),
        "verdict": "with L_k taken over smooth pieces the recurrences certify every cell while g(2) = 449/24 > 0: "
                   "the MVT step needs R'' absolutely continuous with R''' >= L_k, supplied here by P5X L5 analyticity",
        "ok": all_pass(rows) and g_piece(F(2)) > 0}

    # A7 parity premise violated: R''(0) != 0
    Rn = [F(0), F(-1, 2), F(-1, 2), F(1, 6)]
    cells = exact_cells(Rn, xs)
    rows = k5b_literal(cells)
    gn = g_poly(Rn)
    out["A7_parity_premise_violated"] = {
        "R": "-e/2 - e^2/2 + e^3/6  (not odd, R''(0) = -1, R''' = 1)", "L_1": str(cells[0]["L"]),
        "cell1_pass": rows[0]["pass"], "g(1/16)": str(peval(gn, F(1, 16))),
        "verdict": "ell_0 = 0 = R''(0) is exactly where oddness enters; without it the L_1 > 0 test certifies a cell on "
                   "which g > 0",
        "ok": rows[0]["pass"] and peval(gn, F(1, 16)) > 0}

    # A8 interval direction: hi(R - e0 D) must use D.lo
    R = [F(0), F(-1, 2), F(0), F(1, 10)]
    cells = exact_cells(R, xs)
    c = cells[4]
    c["D"] = (c["D"][0] - F(4), c["D"][1] + F(4))
    right = (c["R"][1] - c["e0"] * c["D"][0]) + c["rho"] * c["x_hi"] * c["M"]
    wrong = (c["R"][1] - c["e0"] * c["D"][1]) + c["rho"] * c["x_hi"] * c["M"]
    worst_g_mid = c["R"][1] - c["e0"] * c["D"][0]
    out["A8_interval_direction"] = {
        "Gamma_correct": str(right), "Gamma_wrong_corner": str(wrong),
        "verdict": "the wrong corner under-estimates sup g(e0) over the enclosure by 2*e0*rad(D); the theorem's hi() is "
                   "the correct corner (e0 >= 0)", "ok": wrong < right and worst_g_mid >= c["R"][1] - c["e0"] * c["D"][1]}

    # A9 m=5-style tail: an order-3 island that does NOT start at cell 1 still propagates (local restart from H_j.lo)
    R = [F(0), F(-1, 2), F(0), F(1, 10)]
    base = exact_cells(R, xs, H_override={4: (F(-100), F(9, 10))}, L_override={1: F(3, 5), 2: None, 3: None, 4: None, 5: None})
    island = exact_cells(R, xs, H_override={4: (F(-100), F(9, 10))}, L_override={1: F(3, 5), 2: None, 3: None, 4: F(3, 5), 5: None})
    rb, ri = k5b_literal(base), k5b_literal(island)
    out["A9_tail_local_restart"] = {
        "setup": "cell 5 has a wide valid H (lo = -100); L absent on cells 3-4; island L_5 = 3/5 only",
        "cell5_pass_without_island": rb[4]["pass"], "cell5_pass_with_island": ri[4]["pass"],
        "mu5_without": str(rb[4]["mu"]), "mu5_with": str(ri[4]["mu"]),
        "verdict": "ell restarts from H_{k-1}.lo, so a non-contiguous order-3 island can close a tail cell: K5-B does "
                   "NOT require an unbroken run from cell 0. Whether realised K1 H_k.lo make restarts useful is numerical.",
        "ok": (not rb[4]["pass"]) and ri[4]["pass"]}

    # A10 overshoot: the cell containing 2 extends past 2 and the theorem needs g < 0 on the WHOLE closed cell
    R = [F(0), F(-17, 25), F(0), F(47, 2000), F(0), F(3, 1000), F(0), F(33, 100), F(0), F(-57, 1000)]
    xs10 = [F(0), F(39, 200), F(353, 500), F(229, 250), F(1481, 1000), F(207, 125), F(48, 25), F(1959, 1000), F(211, 100)]
    rows = k5b_literal(exact_cells(R, xs10))
    truth, _ = exact_h3a_g_part(R)
    g = g_poly(R)
    out["A10_last_cell_overshoot_past_2"] = {
        "R": "-17/25 e + 47/2000 e^3 + 3/1000 e^5 + 33/100 e^7 - 57/1000 e^9", "last_cell": "[1959/1000, 211/100]",
        "h3a_g_part_exact": truth, "g(2)": str(peval(g, F(2))), "g(211/100)_positive": peval(g, F(211, 100)) > 0,
        "passes": [r["pass"] for r in rows],
        "verdict": "near-exact inputs (256-piece enclosures, exact L): H3a holds on (0,2] but g > 0 on (2, 2.11], so the "
                   "cell containing 2 cannot pass. THEOREM LIMITATION: the pass condition is over the whole frozen cell, "
                   "not over cell ∩ (0,2] (relevant to CUSUM cell 309 = [1.98391, 2.092283] and SR cell 294)",
        "ok": truth is True and peval(g, F(211, 100)) > 0 and not rows[-1]["pass"] and all(r["pass"] for r in rows[:-1])}

    # A11 granularity: cover ends exactly at 2, near-exact inputs, H3a true, interior coarse cells fail
    R = [F(0), F(-18, 25), F(0), F(1, 250), F(0), F(-27, 500), F(0), F(7, 25), F(0), F(7, 100)]
    xs11 = [F(0), F(2, 25), F(141, 1000), F(189, 250), F(341, 250), F(1497, 1000), F(71, 40), F(357, 200),
            F(901, 500), F(1867, 1000), F(99, 50), F(2)]
    rows = k5b_literal(exact_cells(R, xs11))
    truth, _ = exact_h3a_g_part(R)
    failing = [r["k"] for r in rows if not r["pass"]]
    out["A11_intrinsic_granularity_slack"] = {
        "R": "-18/25 e + 1/250 e^3 - 27/500 e^5 + 7/25 e^7 + 7/100 e^9", "cover_right": "2",
        "h3a_g_part_exact": truth, "failing_cells": failing,
        "failing_cell_widths": [str(xs11[k] - xs11[k - 1]) for k in failing],
        "verdict": "with (near-)exact inputs on a fixed coarse cover the first-order direct bound (slack rho*x*sup|R''|) and "
                   "the chain (slack from min R'' over the cell) both miss a true g < 0: THEOREM LIMITATION of fixed cells, "
                   "not repairable by better enclosures on the same cells",
        "ok": truth is True and bool(failing)}

    return out


# ---------------------------------------------------------------- readiness-scan cross-check

def readiness_scan_agrees(repo_root: Path, rng, trials=40):
    """Run the committed k5_minimality.scan on synthetic records and compare with k5b_readiness_variant and
    k5b_literal. Synthetic records only; no K1 record is read."""
    import importlib.util
    import tempfile
    path = repo_root / "level4/closure_proofs/p5y_k5_order3_readiness_audit/code/k5_minimality.py"
    spec = importlib.util.spec_from_file_location("k5_minimality", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    agree_variant = agree_literal_when_Hlo_le_0 = compared = all_Hlo_le_0 = 0
    for _ in range(trials):
        R = random_odd_poly(rng)
        xs = make_cover(rng)
        while xs[-1] <= 2:
            xs.append(xs[-1] + F(1, 4))
        cells = synthetic_cells(R, xs + [xs[-1] + F(1, 2)], rng, pieces=8, widen=20, l_drop=1.0)
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            table = []
            for i, (a, b) in enumerate(zip(xs + [xs[-1] + F(1, 2)], (xs + [xs[-1] + F(1, 2)])[1:])):
                table.append({"detector": "CUSUM", "index": i, "left": [str(a), "0/1"], "right": [str(b), "0/1"],
                              "rho": [str((b - a) / 2), "0/1"], "e0": [str((a + b) / 2), "0/1"]})
            (td / "cells.json").write_text(json.dumps(table))
            for i, c in enumerate(cells):
                entry = {"e0": str(c["e0"]), "rho": str(c["rho"]), "R_interval": {"lo": str(c["R"][0]), "hi": str(c["R"][1])},
                         "D_interval": {"lo": str(c["D"][0]), "hi": str(c["D"][1])},
                         "R2_interval": {"lo": str(c["H"][0]), "hi": str(c["H"][1])}, "M_R2": str(c["M"])}
                rec = {"cell_index": i, "detector": "CUSUM", "m": {m: entry for m in ("1", "2", "3", "5")}}
                (td / f"aux5_CUSUM_{i}_256.json").write_text(json.dumps(rec))
            rep = mod.scan(td, td / "cells.json", "CUSUM", ("1",))
        theirs = sorted(set(mod.expand(rep["per_m"]["1"]["closed_by_k1"])))
        mine = [i for i, r in enumerate(k5b_readiness_variant(cells)) if r["pass"]]
        compared += 1
        agree_variant += theirs == mine
        if all(c["H"][0] <= 0 for c in cells):
            all_Hlo_le_0 += 1
            lit = [i for i, r in enumerate(k5b_literal(cells)) if r["pass"]]
            agree_literal_when_Hlo_le_0 += theirs == lit
    return {"compared": compared, "agree_with_independent_variant": agree_variant,
            "cases_with_all_Hlo_le_0": all_Hlo_le_0, "agree_with_literal_when_all_Hlo_le_0": agree_literal_when_Hlo_le_0,
            "status": "PASS" if (agree_variant == compared and agree_literal_when_Hlo_le_0 == all_Hlo_le_0) else "FAIL"}


def committed_minimality_has_no_positive_Hlo(repo_root: Path):
    ev = json.loads((repo_root / "level4/closure_proofs/p5y_k5_order3_readiness_audit/evidence/CUSUM_MINIMALITY_R1.json").read_text())
    counts = {m: v["cells_with_R2_interval_lo_positive_count"] for m, v in ev["per_m"].items()}
    return {"cells_with_R2_interval_lo_positive_count": counts, "equivalence_lemma_applies": all(v == 0 for v in counts.values())}


# ---------------------------------------------------------------- 6. hashes

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_hashes(repo_root: Path) -> list[str]:
    inv = json.loads((NS / "config/THEOREM_HASH_INVENTORY.json").read_text())
    problems = []
    for group in ("theorem_files", "premise_files", "reviewed_context_files"):
        for rel, h in inv[group].items():
            p = repo_root / rel
            if not p.exists():
                problems.append(f"MISSING {rel}")
            elif sha256(p) != h["sha256"]:
                problems.append(f"HASH_MISMATCH {rel}")
    return problems


def run(repo_root: Path):
    rng = random.Random(SEED)
    spine = symbolic_spine(rng)
    fuzz = soundness_fuzz(rng)
    adv = adversarial()
    mut = mutation_sensitivity(rng)
    scan = readiness_scan_agrees(repo_root, rng)
    lemma = committed_minimality_has_no_positive_Hlo(repo_root)
    verification = {"schema": "rebaseguard.p5y.k5b.independent-verification.v1", "seed": SEED,
                    "symbolic_spine": spine, "soundness_fuzz": fuzz, "fuzz_mutation_sensitivity": mut,
                    "readiness_scan_cross_check": scan,
                    "readiness_variant_equivalence_on_committed_evidence": lemma,
                    "status": "PASS" if (spine["status"] == fuzz["status"] == scan["status"] == mut["status"] == "PASS"
                                         and lemma["equivalence_lemma_applies"]) else "FAIL"}
    adversarial_record = {"schema": "rebaseguard.p5y.k5b.adversarial-tests.v1", "cases": adv,
                          "status": "PASS" if all(c["ok"] for c in adv.values()) else "FAIL"}
    return verification, adversarial_record


def main() -> int:
    ap = argparse.ArgumentParser(description="Independent K5-B theorem verification (synthetic, read-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--repo-root", default=str(NS.parents[2]))
    r.add_argument("--out")
    r.add_argument("--adversarial-out")
    h = sub.add_parser("verify-hashes")
    h.add_argument("--repo-root", default=str(NS.parents[2]))
    a = ap.parse_args()
    if a.cmd == "verify-hashes":
        problems = verify_hashes(Path(a.repo_root))
        print(json.dumps({"HASHES_VALID": not problems, "problems": problems}, indent=1))
        return 0 if not problems else 1
    ver, adv = run(Path(a.repo_root))
    if a.out:
        Path(a.out).write_text(json.dumps(ver, indent=1, sort_keys=True) + "\n")
    if a.adversarial_out:
        Path(a.adversarial_out).write_text(json.dumps(adv, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verification": ver["status"], "adversarial": adv["status"],
                      "fuzz": {k: ver["soundness_fuzz"][k] for k in ("cells_checked", "cell_passes_exactly_verified",
                               "full_theorem_passes", "soundness_violations", "invariant_violations",
                               "h3a_g_part_true_but_theorem_failed", "variant_equivalence_violations",
                               "variant_divergences_with_some_Hlo_gt_0")},
                      "scan": ver["readiness_scan_cross_check"], "mutations": ver["fuzz_mutation_sensitivity"],
                      "cases": {k: v["ok"] for k, v in adv["cases"].items()}}, indent=1))
    return 0 if ver["status"] == adv["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
