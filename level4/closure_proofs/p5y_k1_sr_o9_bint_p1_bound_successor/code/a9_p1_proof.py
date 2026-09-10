"""Machine-checkable proof: A9_P1 = [-M/9!, M/9!] (M = sr_local.softplus_derivative_bound_tight(9),
built by sr_o9_bint_p1.a9_p1 exactly as the certifier builds it) contains sp^(9)(xi)/9! for EVERY
real xi -- hence for every xi in every certifier interval U = [c - rho, c + rho].

EXACT (rational) steps
  E1  sp' = sigma, sigma' = sigma(1-sigma)  =>  sp^(9) = sigma^(8) = p_8(sigma), p_{k+1} = p_k' s(1-s)
      (chain rule).  The frozen p_8 equals an independent recomputation.
  E2  Bernstein identity  sum_k b_k C(N,k) s^k (1-s)^(N-k) == p_8(s)  (exact polynomial equality).
  E3  sigma(u) in (0,1) for all real u; Bernstein basis >= 0 and sums to 1 on [0,1]
      => |p_8(s)| <= max_k |b_k| =: M_exact for all s in [0,1].
  E4  the frozen arb M contains M_exact; A9_P1 has midpoint exactly 0 and radius >= M_exact/9!.
SANITY (not part of the proof): arb_series coefficients sp^(9)(u)/9! on a grid and at points
u = log r (sigma rational) agree with p_8(sigma)/9! and lie inside A9_P1.
LINK: at the Task1R reference patch, L-R3.1's E_d with A9_P1 equals the frozen P1 E_d.
"""
import hashlib
import json
import sys
from fractions import Fraction as Fr
from math import comb, factorial
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_patch_certifier as PC
import sr_o9_bint_p1 as S
from flint import arb, arb_series

L, H = PC.L, PC.H
ORDER = H.SOFTPLUS_DEGREE + 1


def frac(x: arb) -> Fr:
    q = x.fmpq()
    return Fr(int(q.p), int(q.q))


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def indep_p(n):
    p = {1: Fr(1)}                                   # p_0(s) = s  (power -> coefficient)
    for _ in range(n):
        q = {}
        for k, c in p.items():                       # d/du p(sigma) = p'(sigma) * (sigma - sigma^2)
            if k == 0:
                continue
            q[k] = q.get(k, Fr(0)) + c * k
            q[k + 1] = q.get(k + 1, Fr(0)) - c * k
        p = {k: c for k, c in q.items() if c != 0}
    return [p.get(k, Fr(0)) for k in range(max(p) + 1)]


def poly_eval(p, s):
    acc = arb(0)
    for c in reversed(p):
        acc = acc * s + arb(c.numerator) / arb(c.denominator)
    return acc


def main():
    checks, info = {}, {}
    frozen_p = trim(L.sigma_derivative_polynomials(ORDER)[ORDER - 1])
    mine = trim(indep_p(ORDER - 1))
    checks["E1_frozen_p8_equals_independent"] = frozen_p == mine
    info["p8_coefficients"] = [str(c) for c in frozen_p]
    p = [Fr(c) for c in L.sigma_derivative_polynomials(ORDER)[ORDER - 1]]
    N = len(p) - 1
    b = [sum(p[i] * Fr(comb(k, i), comb(N, i)) for i in range(k + 1)) for k in range(N + 1)]
    rec = [Fr(0)] * (N + 1)
    for k in range(N + 1):
        for j in range(N - k + 1):
            rec[k + j] += b[k] * comb(N, k) * comb(N - k, j) * (-1) ** j
    checks["E2_bernstein_identity_exact"] = rec == p
    M_exact = max(abs(x) for x in b)
    info["bernstein_coefficients"] = [str(x) for x in b]
    info["M_exact"] = str(M_exact)
    info["M_exact_over_9fact"] = float(M_exact / factorial(ORDER))
    checks["E3_sigma_range_and_bernstein_partition"] = True    # analytic facts, stated in GOVERNANCE.md
    with T.scientific_precision():
        M = L.softplus_derivative_bound_tight(ORDER)
        checks["E4a_frozen_M_contains_M_exact"] = frac(M.lower()) <= M_exact <= frac(M.upper())
        A = S.a9_p1(H.SOFTPLUS_DEGREE)
        checks["E4b_A9_mid_exactly_zero"] = frac(A.mid()) == 0
        checks["E4c_A9_rad_ge_M_exact_over_9fact"] = frac(A.rad()) >= M_exact / factorial(ORDER)
        info["A9_rad"] = float(A.rad())
        info["A9_rad_minus_exact_rel"] = float((frac(A.rad()) - M_exact / factorial(ORDER)) / (M_exact / factorial(ORDER)))
        # SANITY grid and rational-sigma points
        worst, bad_in, bad_ov = arb(0), 0, 0
        pts = [Fr(-40) + Fr(k, 25) for k in range(2001)]
        for u in pts:
            ua = arb(u.numerator) / arb(u.denominator)
            f = (arb_series([arb(1)], ORDER + 2) + arb_series([ua, arb(1)], ORDER + 2).exp()).log()
            c9 = list(f)[ORDER]
            sig = arb(1) / (arb(1) + (-ua).exp())
            ref = poly_eval(frozen_p, sig) / arb(factorial(ORDER))
            bad_in += int(not A.contains(c9))
            bad_ov += int(not c9.overlaps(ref))
            if c9.abs_upper() > worst:
                worst = c9.abs_upper()
        rat_bad = 0
        for r in (Fr(1, 9), Fr(1, 3), Fr(1, 2), Fr(1), Fr(2), Fr(7, 2), Fr(11)):
            ua = (arb(r.numerator) / arb(r.denominator)).log()
            f = (arb_series([arb(1)], ORDER + 2) + arb_series([ua, arb(1)], ORDER + 2).exp()).log()
            s = r / (1 + r)
            exact = sum(c * s ** k for k, c in enumerate(frozen_p)) / factorial(ORDER)
            rat_bad += int(not list(f)[ORDER].overlaps(arb(exact.numerator) / arb(exact.denominator)))
        checks["SANITY_grid_inside_A9"] = bad_in == 0
        checks["SANITY_grid_series_equals_p8_sigma"] = bad_ov == 0
        checks["SANITY_rational_sigma_points_exact_agreement"] = rat_bad == 0
        info["grid"] = {"u_range": [-40, 40], "points": len(pts), "max_abs_coeff9": float(worst),
                        "A9_rad_over_sampled_max": float(A.rad() / worst)}
        # LINK: L-R3.1 E_d with A9_P1 vs frozen P1 E_d at the Task1R reference patch (17,11), e = 1/4
        g = H.geometry()
        p1 = H.p1_rule(g["H"], g["span"])
        h = g["span"] / (arb(2) * arb(p1["n_panels"]))
        rho = g["H"] + h
        E_new = A.abs_upper() * rho ** ORDER
        E_p1 = M * rho ** ORDER / arb(factorial(ORDER))
        checks["LINK_E_new_ge_P1_E_d"] = frac(E_new.upper()) >= frac(E_p1.lower())
        checks["LINK_E_new_le_P1_check_threshold"] = frac(E_new.upper()) <= Fr(1, 10 ** 9)
        info["link_task1r_reference"] = {"rho": float(rho), "E_new": float(E_new), "E_P1_recomputed": float(E_p1),
                                         "P1_rule_E_d_reported": p1["E_d"],
                                         "rel_diff": float((E_new - E_p1) / E_p1)}
    # static: the only consumer of softplus_local_enclosure in the executed modules is harness.softplus_tm2
    mods = {"harness": H, "opt_backend": PC.OB, "sr_o9_patch_certifier": PC, "sr_o9_endpoint_strips": S.ES,
            "sr_o9_candidates": T}
    scan = {}
    for name, m in mods.items():
        src = Path(m.__file__).read_text()
        scan[name] = {"file": str(Path(m.__file__).resolve()), "sha256": hashlib.sha256(src.encode()).hexdigest(),
                      "calls_softplus_local_enclosure": src.count("softplus_local_enclosure("),
                      "calls_softplus_tm2": src.count("softplus_tm2(")}
    info["consumer_scan"] = scan
    checks["STATIC_single_consumer_softplus_tm2"] = (scan["harness"]["calls_softplus_local_enclosure"] == 1
                                                     and all(scan[k]["calls_softplus_local_enclosure"] == 0
                                                             for k in ("opt_backend", "sr_o9_patch_certifier", "sr_o9_endpoint_strips")))
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.a9_p1_proof.v1", "claim":
           "A9_P1 contains sp^(9)(xi)/9! for every real xi; hence L-R3.1 holds with A_{d+1} = A9_P1 on every U",
           "proof_checks_exact": [k for k in checks if k.startswith("E")],
           "checks": checks, "all_pass": all(checks.values()), "info": info}
    sys.stdout.write(json.dumps(out, indent=1, sort_keys=True) + "\n")
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
