"""P5Y Gate-2C-bis: repaired m=2 certifier -- every kernel argument is a
degree-12 exact-dyadic certified candidate.

The ONLY change from Gate-2C's `m2_certifier.py` is the representation of the
source objects handed to `_kernel_polynomials`:

    Gate-2C   h_1 and d_e h_1 as EXACT series, bidegree (121,121) / (120,120)
    Gate-2C-bis  hhat_1 and dhhat_1 as degree-12 exact-dyadic candidates with
                 rigorous sup-error bounds, propagated as explicit allowances

Estimand, assembly, resolvent, precision and correspondence are untouched.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from flint import arb
from scipy.special import ndtr

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P5X = ROOT / "level4" / "closure_proofs" / "p5x_global_nonlinear_dynamics"
G1 = ROOT / "level4" / "closure_proofs" / "p5y_micropilot_gate1"
for p in (str(ROOT / "rebaseguard-proof" / "src"), str(G1),
          str(P5X / "certified_method_repair_ra"), str(P5X / "compute_optimization_r1"),
          str(P5X / "compute_optimization_r2")):
    if p not in sys.path:
        sys.path.insert(0, p)

from rebaseguard_certify.arb_backend import (                                 # noqa: E402
    ball_record, gaussian_cdf, rational, workprec,
)
from rebaseguard_certify.polynomial import (                                  # noqa: E402
    bi_add, bi_eval, bi_scale, chebyshev_payload_to_power,
)
from rebaseguard_certify.residual import _chebyshev_sup, _kernel_polynomials  # noqa: E402
from rebaseguard_certify.spectral_candidate import (                          # noqa: E402
    SpectralCandidate, _barycentric_weights, _basis,
)
import ra_certifier as RA                                                     # noqa: E402
import raw_certifier as RAW                                                   # noqa: E402
from fast_range import max_abs_on_reachable_fast                              # noqa: E402

K_F, H_F, C_F = RA.K_FROZEN, RA.H_FROZEN, RA.C_CUSUM
NORM = math.sqrt(2.0 * math.pi)
CHEB_N = 120          # interpolation degree, frozen
KEEP = 12             # candidate degree, frozen and NOT adjustable after T2
SCALE_BITS = 50       # exact-dyadic rounding, frozen
CRAMER = arb(1086) / arb(1000)

# ---- complexity guard instrumentation -------------------------------------
KERNEL_LOG: list[dict] = []


def guarded_kernel(candidate, phi_coefficients, *, z_weight: int, tag: str):
    dp = max(i for i, _ in candidate)
    dm = max(j for _, j in candidate)
    zdeg = dp + dm + len(phi_coefficients) + z_weight
    KERNEL_LOG.append({"tag": tag, "deg_p": dp, "deg_m": dm,
                       "terms": len(candidate), "z_degree_after": zdeg,
                       "score": (dp + 1) * (dm + 1) * (zdeg + 1),
                       "z_weight": z_weight})
    if dp > KEEP or dm > KEEP:
        raise ArithmeticError(f"kernel argument '{tag}' has bidegree ({dp},{dm}) > (12,12)")
    return _kernel_polynomials(candidate, phi_coefficients, z_weight=z_weight)


# ---- degree-12 exact-dyadic candidates with rigorous sup-error -------------
def _cheb_nodes(n: int):
    return [arb(math.cos(math.pi * k / n)) for k in range(n + 1)]


def cheb_candidate_1d(fn, *, kind: str, n: int = CHEB_N, keep: int = KEEP):
    """Degree-`keep` exact-dyadic Chebyshev candidate of `fn` on [0,5].

    Returns (monomial coefficient list in x, eps) where eps rigorously bounds
    sup_{[0,5]} |fn(x) - candidate(x)|.  `kind` selects the Cramer derivative
    bound: 'cdf' (one integration) or 'pdf'.
    """
    half = arb(5) / arb(2)
    vals = []
    for k in range(n + 1):
        t = arb(math.cos(math.pi * k / n))
        x = half * (t + arb(1))
        vals.append(fn(x))
    # DCT-I: a_j = (2/n) * sum'' f(x_k) cos(pi j k / n)
    coeffs = []
    for j in range(n + 1):
        s = arb(0)
        for k in range(n + 1):
            w = arb(1) / arb(2) if k in (0, n) else arb(1)
            s += w * vals[k] * arb(math.cos(math.pi * j * k / n))
        c = arb(2) * s / arb(n)
        coeffs.append(c / arb(2) if j in (0, n) else c)
    tail = arb(0)
    for j in range(keep + 1, n + 1):
        tail += coeffs[j].abs_upper()
    # degree-n interpolation error: 2 (5/4)^{n+1} sup|f^{(n+1)}| / (n+1)!
    fact = arb(math.factorial(n + 1))
    dord = n if kind == "cdf" else n + 1          # cdf: f^{(k)} = phi^{(k-1)}
    sup_der = (CRAMER / (arb(2) * arb.pi()).sqrt()) * arb(math.factorial(dord)).sqrt()
    interp_err = arb(2) * ((arb(5) / arb(4)) ** (n + 1)) * sup_der / fact
    # exact-dyadic rounding of the kept Chebyshev coefficients
    scale = arb(2) ** SCALE_BITS
    kept = []
    for j in range(keep + 1):
        mid = coeffs[j].mid()
        kept.append(arb(int(round(float(mid * scale)))) / scale)
    round_err = arb(keep + 1) * (arb(1) / scale) + sum(
        (coeffs[j] - kept[j]).abs_upper() for j in range(keep + 1))
    eps = tail + interp_err + round_err
    # Chebyshev -> monomial in t, then t = (2x-5)/5
    T = [[arb(1)], [arb(0), arb(1)]]
    for _ in range(2, keep + 1):
        prev, prev2 = T[-1], T[-2]
        nxt = [arb(0)] * (len(prev) + 1)
        for i, c in enumerate(prev):
            nxt[i + 1] += arb(2) * c
        for i, c in enumerate(prev2):
            nxt[i] -= c
        T.append(nxt)
    tmono = [arb(0)] * (keep + 1)
    for j in range(keep + 1):
        for i, c in enumerate(T[j]):
            tmono[i] += kept[j] * c
    # substitute t = (2/5) x - 1
    xmono = [arb(0)] * (keep + 1)
    for i, c in enumerate(tmono):
        for r in range(i + 1):
            xmono[r] += c * arb(math.comb(i, r)) * ((arb(2) / arb(5)) ** r) * (
                (-arb(1)) ** (i - r))
    return xmono, eps, tail, interp_err, round_err


def build_candidates(e: arb):
    """hhat_1 and dhhat_1 as bidegree-(12,12) BiPolys, with their sup-errors."""
    c = arb(C_F)
    A, epsA, tA, iA, rA = cheb_candidate_1d(lambda x: gaussian_cdf(c - x + e), kind="cdf")
    B, epsB, tB, iB, rB = cheb_candidate_1d(lambda x: gaussian_cdf(x - c + e), kind="cdf")
    phi = lambda t: (-(t * t) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
    P, epsP, tP, iP, rP = cheb_candidate_1d(lambda x: phi(c - x + e), kind="pdf")
    Q, epsQ, tQ, iQ, rQ = cheb_candidate_1d(lambda x: phi(x - c + e), kind="pdf")
    hhat = {(0, 0): arb(1)}
    for i, co in enumerate(A):
        hhat[(i, 0)] = hhat.get((i, 0), arb(0)) - co
    for j, co in enumerate(B):
        hhat[(0, j)] = hhat.get((0, j), arb(0)) + co
    dhhat = {}
    for i, co in enumerate(P):
        dhhat[(i, 0)] = dhhat.get((i, 0), arb(0)) - co
    for j, co in enumerate(Q):
        dhhat[(0, j)] = dhhat.get((0, j), arb(0)) + co
    s0hat = {}
    for i, co in enumerate(P):
        s0hat[(i, 0)] = s0hat.get((i, 0), arb(0)) + co
    for j, co in enumerate(Q):
        s0hat[(0, j)] = s0hat.get((0, j), arb(0)) - co
    return {"hhat": hhat, "dhhat": dhhat, "s0hat": s0hat,
            "eps_h": epsA + epsB, "eps_dh": epsP + epsQ,
            "detail": {"A": [float(epsA), float(tA), float(iA), float(rA)],
                       "B": [float(epsB), float(tB), float(iB), float(rB)],
                       "P": [float(epsP), float(tP), float(iP), float(rP)],
                       "Q": [float(epsQ), float(tQ), float(iQ), float(rQ)]}}


# ---- candidate solve for F_1 (float; candidate only, never proof evidence) --
def collocation_m2(drift: float, degree: int, quadrature_order: int):
    count = degree + 1
    x = np.cos(np.pi * np.arange(count) / degree)
    nodes = 0.5 * H_F * (1.0 - x)
    bary = _barycentric_weights(degree)
    gn, gw = np.polynomial.legendre.leggauss(quadrature_order)
    dim = count * count
    kernel = np.zeros((dim, dim)); kernel_dphi = np.zeros((dim, dim))
    r1 = np.zeros(dim); dr1 = np.zeros(dim)
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            row = i * count + j
            ell, upper = m - C_F, C_F - p
            mid, rad = 0.5 * (ell + upper), 0.5 * (upper - ell)
            for node, weight in zip(gn, gw, strict=True):
                z = mid + rad * node
                y = z + drift
                dens = rad * weight * math.exp(-0.5 * y * y) / NORM
                wp_s = max(0.0, p + z - K_F); wm_s = max(0.0, m - z - K_F)
                interp = np.outer(_basis(wp_s, nodes, bary),
                                  _basis(wm_s, nodes, bary)).ravel()
                kernel[row] += dens * interp
                kernel_dphi[row] += (-y) * dens * interp
                au = C_F - wp_s + drift; al = wm_s - C_F + drift
                h1v = 1.0 - ndtr(au) + ndtr(al)
                dh1v = -(math.exp(-0.5 * au * au) - math.exp(-0.5 * al * al)) / NORM
                r1[row] += dens * y * h1v
                dr1[row] += dens * (h1v + y * dh1v - y * y * h1v)
    return kernel, kernel_dphi, r1, dr1, count


def solve_F1(drift: float, degree: int = RA.DEGREE, quadrature_order: int = RA.QUADRATURE):
    kernel, kernel_dphi, r1, dr1, count = collocation_m2(drift, degree, quadrature_order)
    op = np.eye(count * count) - kernel
    f1 = np.linalg.solve(op, r1)
    df1 = np.linalg.solve(op, kernel_dphi @ f1 + dr1)
    return (SpectralCandidate(f1.reshape(count, count), H_F),
            SpectralCandidate(df1.reshape(count, count), H_F))


# ---- certified residual for F_1, with candidate allowances -----------------
def certify_F1(e_num: int, e_den: int, *, resolvent: arb, order: int = RA.TAYLOR_N,
               degree: int = RA.DEGREE, bits: int = RA.BITS,
               e_hi_for_allowance: float = 0.26) -> dict:
    drift = e_num / e_den
    cf, cdf = solve_F1(drift, degree, RA.QUADRATURE)
    pay_f = cf.to_chebyshev_dyadic(scale_bits=RA.SCALE_BITS)
    pay_df = cdf.to_chebyshev_dyadic(scale_bits=RA.SCALE_BITS)
    with workprec(bits):
        e = rational(e_num, e_den)
        b = RA.phi_taylor_coefficients(order, e)
        db = RA.derivative_coefficients(b)
        cand = build_candidates(e)
        hhat, dhhat = cand["hhat"], cand["dhhat"]
        eps_h, eps_dh = cand["eps_h"], cand["eps_dh"]

        kz_lo, kz_hi = guarded_kernel(hhat, b, z_weight=1, tag="K_z,b hhat")
        k0_lo, k0_hi = guarded_kernel(hhat, b, z_weight=0, tag="K_0,b hhat")
        s1_lo = bi_add(kz_lo, bi_scale(k0_lo, e)); s1_hi = bi_add(kz_hi, bi_scale(k0_hi, e))
        dz_lo, dz_hi = guarded_kernel(dhhat, b, z_weight=1, tag="K_z,b dhhat")
        d0_lo, d0_hi = guarded_kernel(dhhat, b, z_weight=0, tag="K_0,b dhhat")
        pz_lo, pz_hi = guarded_kernel(hhat, db, z_weight=1, tag="K_z,db hhat")
        p0_lo, p0_hi = guarded_kernel(hhat, db, z_weight=0, tag="K_0,db hhat")
        ds1_lo = bi_add(k0_lo, bi_add(bi_add(dz_lo, bi_scale(d0_lo, e)),
                                      bi_add(pz_lo, bi_scale(p0_lo, e))))
        ds1_hi = bi_add(k0_hi, bi_add(bi_add(dz_hi, bi_scale(d0_hi, e)),
                                      bi_add(pz_hi, bi_scale(p0_hi, e))))

        f_hat = chebyshev_payload_to_power(pay_f)
        df_hat = chebyshev_payload_to_power(pay_df)
        kf_lo, kf_hi = guarded_kernel(f_hat, b, z_weight=0, tag="K_0,b F1hat")
        res_lo = bi_add(bi_add(f_hat, bi_scale(kf_hi, -arb(1))), bi_scale(s1_hi, -arb(1)))
        res_hi = bi_add(bi_add(f_hat, bi_scale(kf_lo, -arb(1))), bi_scale(s1_lo, -arb(1)))
        poly_f, coverage = max_abs_on_reachable_fast(res_lo, res_hi, subdivision_depth=0)
        kdf_lo, kdf_hi = guarded_kernel(df_hat, b, z_weight=0, tag="K_0,b dF1hat")
        dkf_lo, dkf_hi = guarded_kernel(f_hat, db, z_weight=0, tag="K_0,db F1hat")
        rd_lo = bi_add(bi_add(df_hat, bi_scale(kdf_hi, -arb(1))),
                       bi_add(bi_scale(dkf_hi, -arb(1)), bi_scale(ds1_hi, -arb(1))))
        rd_hi = bi_add(bi_add(df_hat, bi_scale(kdf_lo, -arb(1))),
                       bi_add(bi_scale(dkf_lo, -arb(1)), bi_scale(ds1_lo, -arb(1))))
        poly_d, _ = max_abs_on_reachable_fast(rd_lo, rd_hi, subdivision_depth=0)

        eps_z = RA.taylor_remainder(order, rational(11, 2))
        eps_dz = arb(order + 1) * eps_z
        sup_f = _chebyshev_sup(pay_f); sup_df = _chebyshev_sup(pay_df)
        e_abs = arb(2) / (arb(2) * arb.pi()).sqrt()          # E|raw| = sqrt(2/pi) upper
        cand_allow = e_abs * eps_h                            # |K_raw (h - hhat)|
        cand_allow_d = arb(2) * eps_h + e_abs * eps_dh
        delta = poly_f + arb(11) * sup_f * eps_z + cand_allow
        delta_d = (poly_d + arb(11) * sup_df * eps_z + arb(11) * sup_f * eps_dz
                   + cand_allow_d)
        if not delta > 0 or not delta_d > 0:
            raise ArithmeticError("invalid residual bounds")
        return {
            "e_rational": f"{e_num}/{e_den}", "object": "F_1", "representation": "raw",
            "candidate_degree": KEEP,
            "eps_h": ball_record(eps_h), "eps_dh": ball_record(eps_dh),
            "eps_detail": cand["detail"],
            "cand_allow": ball_record(cand_allow), "cand_allow_d": ball_record(cand_allow_d),
            "polynomial_residual_value": ball_record(poly_f),
            "delta": ball_record(delta), "delta_derivative": ball_record(delta_d),
            "F1hat_origin": ball_record(bi_eval(f_hat, arb(0), arb(0))),
            "S0raw_origin_candidate": ball_record(bi_eval(cand["s0hat"], arb(0), arb(0))),
            "hhat1_origin": ball_record(bi_eval(hhat, arb(0), arb(0))),
            "_cand_allow": cand_allow, "_eps_h": eps_h, "_eps_dh": eps_dh,
            "_hhat": hhat, "coverage": coverage,
        }
