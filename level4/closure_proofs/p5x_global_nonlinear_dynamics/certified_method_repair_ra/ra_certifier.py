"""R-A' certified enclosure of R_{CUSUM,m=1}(e) over a cell.

Implements exactly `RA_FROZEN_SPEC.md`.  Proof-critical.

The failed first method (`../certificate/drift_certificate.py`, result at commit
528908b) is left untouched as the historical record.  R-A' changes only the
*representation*, never the certified equation:

  Device 1 (recentring).  phi(z+e) is expanded about `e` in the UNSHIFTED
  innovation z, whose range (l,u) = (m-11/2, 11/2-p) is e-free, so the Taylor
  remainder eps_rec(N) = 0.4333 (11/2)^{N+1}/sqrt((N+1)!) does not depend on the
  drift at all.  Reward arguments u+e and l+e are recentred at 3+e and -3+e,
  whose expansion variables 5/2-p and m-5/2 are likewise e-free.  Coefficients
  come from the exact Hermite recurrence, not from a cancellation-prone
  binomial sum.

  Device 2 (exact-centre Taylor model in e).  Every symbolic computation runs at
  an exact rational e_0 with zero radius, so the 4.96e41 interval-dependency
  amplification measured for the failed method has no input to act on.  The
  cell is covered by sub-cells of frozen half-width h = 1/(4 a C), and R over a
  sub-cell is enclosed by a first-order Taylor model in e whose second-order
  remainder is bounded by the closed bootstrap of the specification.

Because the z-formulation's limits, reset kinks and state map are all e-free,
the inherited kernel assembly `_kernel_polynomials` is reused UNMODIFIED; the
drift enters only through the coefficient list handed to it.
"""
from __future__ import annotations

import math
import sys
from math import factorial
from pathlib import Path

import numpy as np
from flint import arb
from scipy.special import ndtr

_PROOF_SRC = Path(__file__).resolve().parents[4] / "rebaseguard-proof" / "src"
if str(_PROOF_SRC) not in sys.path:
    sys.path.insert(0, str(_PROOF_SRC))

from rebaseguard_certify.arb_backend import (            # noqa: E402
    ball_record, gaussian_cdf, rational, workprec,
)
from rebaseguard_certify.polynomial import (             # noqa: E402
    BiPoly, bi_add, bi_eval, bi_mul, bi_scale, chebyshev_payload_to_power,
)
from rebaseguard_certify.residual import (               # noqa: E402
    _chebyshev_sup, _kernel_polynomials, _max_abs_on_reachable, _series_at_affine,
)
from rebaseguard_certify.spectral_candidate import (     # noqa: E402
    SpectralCandidate, _barycentric_weights, _basis,
)

K_FROZEN = 0.5
H_FROZEN = 5.0
C_CUSUM = H_FROZEN + K_FROZEN               # 11/2
DEGREE = 12
QUADRATURE = 400
SCALE_BITS = 50
TAYLOR_N = 120                              # frozen: RA_FROZEN_SPEC section 2
SUBDIVISION_DEPTH = 3
BITS = 256
RESOLVENT_N_MAX = 60
CRAMER = arb(1086) / arb(1000)              # >= 1.086, Cramer's constant


# --------------------------------------------------------------------------
# Device 1 — recentred Taylor coefficients of phi, by the Hermite recurrence
# --------------------------------------------------------------------------
def phi_taylor_coefficients(order: int, centre: arb) -> list[arb]:
    """[b_0..b_order] with b_i = phi^{(i)}(centre)/i! = (-1)^i He_i(c) phi(c)/i!.

    Uses t_0 = 1, t_1 = c, t_{i+1} = (c t_i - t_{i-1})/(i+1) for t_i = He_i(c)/i!,
    which is exact for rational `centre` and free of the cancellation that
    wrecked the binomial double sum of the failed method.
    """
    phi_c = (-(centre * centre) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
    t = [arb(1)]
    if order >= 1:
        t.append(arb(centre))
    for i in range(1, order):
        t.append((centre * t[i] - t[i - 1]) / arb(i + 1))
    return [((-arb(1)) ** i) * t[i] * phi_c for i in range(order + 1)]


def taylor_remainder(order: int, radius: arb) -> arb:
    """0.4333 * radius^{order+1} / sqrt((order+1)!)  --  Cramer, and e-free."""
    return (CRAMER / (arb(2) * arb.pi()).sqrt()) * (radius ** (order + 1)) / (
        arb(factorial(order + 1)).sqrt())


def derivative_coefficients(b: list[arb]) -> list[arb]:
    """d_e b_i = (i+1) b_{i+1}; zero-padded to the same length."""
    return [arb(i + 1) * b[i + 1] for i in range(len(b) - 1)] + [arb(0)]


# --------------------------------------------------------------------------
# Recentred reward polynomials
# --------------------------------------------------------------------------
def _recentred_sites(order: int, e: arb):
    """phi and Phi at u+e and l+e, as BiPolys in (p, m), recentred at +/-3+e."""
    c_plus = arb(3) + e
    c_minus = -arb(3) + e
    s_plus: BiPoly = {(0, 0): rational(5, 2), (1, 0): -arb(1)}     # (u+e) - (3+e)
    s_minus: BiPoly = {(0, 0): -rational(5, 2), (0, 1): arb(1)}    # (l+e) - (-3+e)
    out = {}
    for tag, centre, svar in (("plus", c_plus, s_plus), ("minus", c_minus, s_minus)):
        beta = phi_taylor_coefficients(order, centre)
        phi_poly = _series_at_affine(beta, svar)
        integ = [beta[i] / arb(i + 1) for i in range(len(beta))]
        cdf_poly = bi_add({(0, 0): gaussian_cdf(centre)},
                          bi_mul(svar, _series_at_affine(integ, svar)))
        out[tag] = (phi_poly, cdf_poly)
    arg_plus: BiPoly = {(0, 0): rational(11, 2) + e, (1, 0): -arb(1)}
    arg_minus: BiPoly = {(0, 0): -rational(11, 2) + e, (0, 1): arb(1)}
    return out["plus"], out["minus"], arg_plus, arg_minus


def reward_rho1(order: int, e: arb) -> BiPoly:
    (phi_u, cdf_u), (phi_l, cdf_l), _, _ = _recentred_sites(order, e)
    bracket = bi_add({(0, 0): arb(1)}, bi_add(bi_scale(cdf_u, -arb(1)), cdf_l))
    return bi_add(bi_add(phi_u, bi_scale(phi_l, -arb(1))), bi_scale(bracket, -e))


def reward_drho1(order: int, e: arb) -> BiPoly:
    """d_e rho_1 = -(u+e)phi(u+e) + (l+e)phi(l+e) - (1-Phi(u+e)+Phi(l+e))
                   + e(phi(u+e) - phi(l+e))."""
    (phi_u, cdf_u), (phi_l, cdf_l), arg_u, arg_l = _recentred_sites(order, e)
    bracket = bi_add({(0, 0): arb(1)}, bi_add(bi_scale(cdf_u, -arb(1)), cdf_l))
    out = bi_scale(bi_mul(arg_u, phi_u), -arb(1))
    out = bi_add(out, bi_mul(arg_l, phi_l))
    out = bi_add(out, bi_scale(bracket, -arb(1)))
    out = bi_add(out, bi_scale(bi_add(phi_u, bi_scale(phi_l, -arb(1))), e))
    return out


# --------------------------------------------------------------------------
# Candidates (NOT proof evidence)
# --------------------------------------------------------------------------
def _collocation(drift: float, degree: int, quadrature_order: int):
    count = degree + 1
    x = np.cos(np.pi * np.arange(count) / degree)
    nodes = 0.5 * H_FROZEN * (1.0 - x)
    bary = _barycentric_weights(degree)
    gn, gw = np.polynomial.legendre.leggauss(quadrature_order)
    dim = count * count
    kernel = np.zeros((dim, dim))
    kernel_dphi = np.zeros((dim, dim))
    reward = np.zeros(dim)
    dreward = np.zeros(dim)
    norm = math.sqrt(2.0 * math.pi)
    for i, p in enumerate(nodes):
        for j, m in enumerate(nodes):
            row = i * count + j
            ell = m - C_CUSUM
            upper = C_CUSUM - p
            mid = 0.5 * (ell + upper)
            rad = 0.5 * (upper - ell)
            for node, weight in zip(gn, gw, strict=True):
                z = mid + rad * node
                y = z + drift
                dens = rad * weight * math.exp(-0.5 * y * y) / norm
                wp = _basis(max(0.0, p + z - K_FROZEN), nodes, bary)
                wm = _basis(max(0.0, m - z - K_FROZEN), nodes, bary)
                interp = np.outer(wp, wm).ravel()
                kernel[row] += dens * interp
                kernel_dphi[row] += (-y) * dens * interp
            au = upper + drift
            al = ell + drift
            pu = math.exp(-0.5 * au * au) / norm
            pl = math.exp(-0.5 * al * al) / norm
            brack = 1.0 - ndtr(au) + ndtr(al)
            reward[row] = pu - pl - drift * brack
            dreward[row] = -au * pu + al * pl - brack + drift * (pu - pl)
    return nodes, kernel, kernel_dphi, reward, dreward, count


def solve_candidates(drift: float, degree: int = DEGREE,
                     quadrature_order: int = QUADRATURE):
    """Chebyshev candidates for g and d_e g at the exact drift `drift`."""
    _, kernel, kernel_dphi, reward, dreward, count = _collocation(
        drift, degree, quadrature_order)
    dim = count * count
    operator = np.eye(dim) - kernel
    g = np.linalg.solve(operator, reward)
    dg = np.linalg.solve(operator, kernel_dphi @ g + dreward)
    return (SpectralCandidate(g.reshape(count, count), H_FROZEN),
            SpectralCandidate(dg.reshape(count, count), H_FROZEN))


# --------------------------------------------------------------------------
# Resolvent — unchanged from the first method, drift-explicit, no import
# --------------------------------------------------------------------------
def resolvent_bound(e_ball: arb, *, n_max: int = RESOLVENT_N_MAX):
    best = None
    for n in range(1, n_max + 1):
        sqrt_n = arb(n).sqrt()
        base = (arb(H_FROZEN) + arb(n) * arb(K_FROZEN)) / sqrt_n
        q_n = gaussian_cdf(-base - e_ball * sqrt_n) + gaussian_cdf(-base + e_ball * sqrt_n)
        q_lo = q_n.lower()
        if not q_lo > 0:
            continue
        bound = arb(n) / q_lo
        if best is None or bound.upper() < best[0].upper():
            best = (bound, n, q_lo)
    if best is None:
        raise ArithmeticError("no valid resolvent block length")
    return best


# --------------------------------------------------------------------------
# The certified residuals at one exact rational drift
# --------------------------------------------------------------------------
def certify_at_exact_drift(e_num: int, e_den: int, *, order: int = TAYLOR_N,
                           degree: int = DEGREE, quadrature_order: int = QUADRATURE,
                           scale_bits: int = SCALE_BITS,
                           subdivision_depth: int = SUBDIVISION_DEPTH,
                           bits: int = BITS, e_hi_for_allowance: float = 0.26) -> dict:
    """delta, delta', ghat(x_0), ghat'(x_0) and sup norms at e = e_num/e_den."""
    drift = e_num / e_den
    cand_g, cand_dg = solve_candidates(drift, degree, quadrature_order)
    pay_g = cand_g.to_chebyshev_dyadic(scale_bits=scale_bits)
    pay_dg = cand_dg.to_chebyshev_dyadic(scale_bits=scale_bits)

    with workprec(bits):
        e = rational(e_num, e_den)
        b = phi_taylor_coefficients(order, e)
        db = derivative_coefficients(b)
        g_hat = chebyshev_payload_to_power(pay_g)
        dg_hat = chebyshev_payload_to_power(pay_dg)

        kg_low, kg_high = _kernel_polynomials(g_hat, b, z_weight=0)
        rho1 = reward_rho1(order, e)
        res_g_low = bi_add(bi_add(g_hat, bi_scale(kg_low, -arb(1))), bi_scale(rho1, -arb(1)))
        res_g_high = bi_add(bi_add(g_hat, bi_scale(kg_high, -arb(1))), bi_scale(rho1, -arb(1)))
        poly_g, coverage = _max_abs_on_reachable(
            res_g_low, res_g_high, subdivision_depth=subdivision_depth)

        kdg_low, kdg_high = _kernel_polynomials(dg_hat, b, z_weight=0)
        dkg_low, dkg_high = _kernel_polynomials(g_hat, db, z_weight=0)
        drho1 = reward_drho1(order, e)
        res_d_low = bi_add(bi_add(dg_hat, bi_scale(kdg_low, -arb(1))),
                           bi_add(bi_scale(dkg_low, -arb(1)), bi_scale(drho1, -arb(1))))
        res_d_high = bi_add(bi_add(dg_hat, bi_scale(kdg_high, -arb(1))),
                            bi_add(bi_scale(dkg_high, -arb(1)), bi_scale(drho1, -arb(1))))
        poly_d, _ = _max_abs_on_reachable(
            res_d_low, res_d_high, subdivision_depth=subdivision_depth)

        eps_z = taylor_remainder(order, rational(11, 2))
        eps_reward = taylor_remainder(order, rational(5, 2))
        eps_dz = arb(order + 1) * eps_z          # conservative for the phi' list
        sup_g = _chebyshev_sup(pay_g)
        sup_dg = _chebyshev_sup(pay_dg)
        e_hi = arb(rational(round(e_hi_for_allowance * 10 ** 6), 10 ** 6))
        reward_allow = (arb(2) + arb(2) * e_hi * (rational(11, 2) + e_hi)) * (
            eps_reward * (arb(1) + rational(5, 2)))
        delta = poly_g + arb(11) * sup_g * eps_z + reward_allow
        delta_d = (poly_d + arb(11) * sup_dg * eps_z + arb(11) * sup_g * eps_dz
                   + reward_allow * (arb(1) + rational(11, 2) + e_hi))
        if not delta > 0 or not delta_d > 0:
            raise ArithmeticError("invalid residual bounds")

        return {
            "e_rational": f"{e_num}/{e_den}",
            "e_float": drift,
            "polynomial_residual_value": ball_record(poly_g),
            "polynomial_residual_derivative": ball_record(poly_d),
            "eps_recentred_z": ball_record(eps_z),
            "eps_recentred_reward": ball_record(eps_reward),
            "delta": ball_record(delta),
            "delta_derivative": ball_record(delta_d),
            "sup_chebyshev_g": ball_record(sup_g),
            "sup_chebyshev_dg": ball_record(sup_dg),
            "ghat_origin": ball_record(bi_eval(g_hat, arb(0), arb(0))),
            "dghat_origin": ball_record(bi_eval(dg_hat, arb(0), arb(0))),
            "_delta": delta, "_delta_d": delta_d,
            "_sup_g": sup_g, "_sup_dg": sup_dg,
            "_g0": bi_eval(g_hat, arb(0), arb(0)),
            "_dg0": bi_eval(dg_hat, arb(0), arb(0)),
            "coverage": {**coverage, "sampled_grid_used": False,
                         "reachable_continuum_complete": True},
        }


# --------------------------------------------------------------------------
# Diagnostic only (RA_FROZEN_SPEC section 12.2).  Never on a proof path:
# R-A' certifies exclusively at exact rational drifts.
# --------------------------------------------------------------------------
def _interval_probe(e_ball: arb, *, order: int = TAYLOR_N, degree: int = DEGREE,
                    subdivision_depth: int = SUBDIVISION_DEPTH) -> arb:
    """Bernstein residual with an interval-valued e, to measure dependency."""
    cand_g, _ = solve_candidates(float(e_ball.mid()), degree, QUADRATURE)
    payload = cand_g.to_chebyshev_dyadic(scale_bits=SCALE_BITS)
    with workprec(BITS):
        b = phi_taylor_coefficients(order, e_ball)
        g_hat = chebyshev_payload_to_power(payload)
        low, high = _kernel_polynomials(g_hat, b, z_weight=0)
        rho1 = reward_rho1(order, e_ball)
        r_low = bi_add(bi_add(g_hat, bi_scale(low, -arb(1))), bi_scale(rho1, -arb(1)))
        r_high = bi_add(bi_add(g_hat, bi_scale(high, -arb(1))), bi_scale(rho1, -arb(1)))
        mx, _ = _max_abs_on_reachable(r_low, r_high, subdivision_depth=subdivision_depth)
        return mx
