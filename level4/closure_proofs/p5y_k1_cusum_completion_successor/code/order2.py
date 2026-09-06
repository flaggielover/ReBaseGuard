"""PHASE 6: second-order Taylor-in-e tightening of the order-2 chain.

THE MEASURED PROBLEM (Phase 5)
------------------------------
In cells 318-324 every order-2 residual's whole-cell bound is >= 99.8% the
mean-value term:

    delta_cell = delta_mid + rho * Env          (Env bounds sup_cell |d_e r|)

    cell 321  S_1:2   delta_mid 4.9e-04   rho*Env 0.7214   share 0.9993
              h_2:2   delta_mid 1.1e-04   rho*Env 0.4271   share 0.9997

`Env` is a product of operator norms and candidate sup norms,
`Env = sum_i C(k,i) j_(i+1) sup|hhat|`. That bound is loose twice over: an
operator applied to a SPECIFIC candidate is far from its worst case, and the
terms in the sum can cancel. The certified `delta_mid` for the very same
residual is four orders of magnitude smaller, which is exactly the gap.

THE TIGHTENING
--------------
Taylor with Lagrange remainder in `e`, for each fixed `x`, then sup over `x`:

    sup_(e in cell) |r(x;e)|  <=  sup_x |r(x;e0)|
                               +  rho * sup_x |d_e r(x;e0)|
                               +  (rho^2/2) * sup_(x, e in cell) |d_e^2 r(x;e)|

Only the LAST term still uses the loose operator-norm envelope, and it now
carries `rho^2/2` instead of `rho` -- a factor `2/rho` smaller multiplier
(13.7x at cell 321). The middle term is the certified Bernstein range of the
ACTUAL differentiated residual, computed exactly the way `delta_mid` is, so it
inherits both the specificity and the cancellation.

Because every candidate is a state-only polynomial constant in `e`, `d_e r`
consists only of differentiated OPERATORS applied to fixed candidates:

    h_j^(k)      r  = hhat_(j,k) - sum_i C(k,i) K_i hhat_(j-1,k-i)
                 r' = -sum_i C(k,i) K_(i+1) hhat_(j-1,k-i)
                 r''-> Env2 = sum_i C(k,i) k_(i+2) sup|hhat_(j-1,k-i)|
    S_r^(k)      r' = -sum_i C(k,i) J_(i+1) hhat_(r,k-i)
                 r''-> Env2 = sum_i C(k,i) j_(i+2) sup|hhat_(r,k-i)|
    H_r          r' = -K_1 Hhat_r - K_3 Fhat_r - 2 K_2 Dhat_r
                 r''-> Env2 = k_2 sup|Hhat| + k_4 sup|Fhat| + 2 k_3 sup|Dhat|
    W_(r,j)^(k)  as for h.

CLOSED-FORM LEAVES
------------------
`h_1^(k)` and `S_0^(k)` are exact closed forms whose whole-cell error is
`rho * sup|S_0^(k+1)|`, bounded in the predecessor by the WHOLE-LINE Cramer
supremum `2 sup_R |phi^(k+1)|`. But on the cell the arguments live in bounded
windows: `u + e` and `l + e` with `u in [k, c]`, `l in [-c, -k]`, so

    sup_cell |S_0^(n)| <= sup_(Y_u) |phi^(n)| + sup_(Y_l) |phi^(n)|

with `Y_u = [k + e_min, c + e_max]`, `Y_l = [-c + e_min, -k + e_max]`, each
evaluated exactly as `max |He_n| phi` over the window using the same Hermite
sign-partitioning the drift-aware norms use. At cell 321 that takes
`2 sup|phi'''| = 2.122` down to about 0.55.

EVERY STEP IS AN UPPER-BOUND IMPROVEMENT, NOT A NUMERICAL ONE
--------------------------------------------------------------
Each new bound is `min(new, predecessor)`, and `assert_improvement` refuses any
object where the new bound is not <= the predecessor's. Nothing about the cell
geometry, rho, precision, degree, budgets or Taylor semantics changes.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import comb

import ancestry                                                 # noqa: F401

from flint import arb                                           # noqa: E402

import opnorms as reviewed_norms                                # noqa: E402
import sharp_norms                                              # noqa: E402
from cusum_layer2 import Pair, Z_RANGE                          # noqa: E402
from intervals import exact, tight_upper                        # noqa: E402
from sharp_certifier import SharpCellCertifier                  # noqa: E402

K_FROZEN = F(1, 2)                  # detector k
C_FROZEN = F(11, 2)                 # c_D = h + k
H_FROZEN = F(5)                     # state half width


class BoundRegression(RuntimeError):
    """A 'tightening' produced a bound that is not <= the predecessor's."""


# ------------------------------------------------------- closed-form suprema
def sup_phi_derivative_on(n: int, lo, hi) -> arb:
    """sup_(y in [lo,hi]) |phi^(n)(y)| = max |He_n(y)| phi(y), exactly.

    The extrema of `|He_n| phi` are the zeros of its derivative, i.e. the roots
    of `He_(n+1)`, because `d/dy (He_n phi) = -He_(n+1) phi`. So the supremum
    over a window is attained at an endpoint or at an interior root of
    `He_(n+1)`, all of which are tabulated exactly.
    """
    pts = [lo, hi]
    for r in sharp_norms._roots(n + 1):
        v = sharp_norms._root_value(r)
        if v > lo and v < hi:
            pts.append(v)
    best = arb(0)
    for y in pts:
        val = (sharp_norms.hermite_he(n, y) * sharp_norms.phi(y)).abs_upper()
        if val.upper() > best.upper():
            best = val
    return tight_upper(best)


def sup_source_derivative_on(n: int, left, right) -> arb:
    """sup_cell |S_0^(n)| for S_0 = phi(u+e) - phi(l+e), drift-aware.

    u in [k, c] and l in [-c, -k] over the reachable state square, so the two
    arguments range over Y_u and Y_l below. Never worse than the predecessor's
    whole-line Cramer bound.
    """
    e_lo, e_hi = exact(F(left)), exact(F(right))
    yu_lo, yu_hi = exact(K_FROZEN) + e_lo, exact(C_FROZEN) + e_hi
    yl_lo, yl_hi = -exact(C_FROZEN) + e_lo, -exact(K_FROZEN) + e_hi
    sharp = tight_upper(sup_phi_derivative_on(n, yu_lo, yu_hi)
                        + sup_phi_derivative_on(n, yl_lo, yl_hi))
    reviewed = reviewed_norms.sup_source_derivative(n)
    return tight_upper(sharp if sharp.upper() <= reviewed.upper() else reviewed)


# ----------------------------------------------------------------- certifier
ORDER2_H = tuple((j, 2) for j in range(2, 5))
ORDER2_S = tuple((r, 2) for r in range(1, 5))


class Order2Certifier(SharpCellCertifier):
    """Drift-aware norms (inherited, SOUND) plus the order-2 Taylor tightening."""

    tightens_order2 = True

    # ---- second-derivative envelopes, norms only, carrying rho^2/2 ---------
    def _env2_h(self, j: int, k: int) -> arb:
        out = arb(0)
        for i in range(k + 1):
            out = out + (arb(comb(k, i)) * self.norms["k"][i + 2]
                         * self.sup["h", j - 1, k - i])
        return out

    def _env2_S(self, r: int, k: int) -> arb:
        out = arb(0)
        for i in range(k + 1):
            out = out + (arb(comb(k, i)) * self.norms["j"][i + 2]
                         * self.sup["h", r, k - i])
        return out

    def _env2_W(self, r: int, j: int, k: int) -> arb:
        out = arb(0)
        for i in range(k + 1):
            out = out + (arb(comb(k, i)) * self.norms["k"][i + 2]
                         * self.sup["W", (r, j - 1), k - i])
        return out

    def _env2_H(self, r: int) -> arb:
        k_ = self.norms["k"]
        return (k_[2] * self.sup["H", r, 0] + k_[4] * self.sup["F", r, 0]
                + arb(2) * k_[3] * self.sup["D", r, 0])

    # ---- the differentiated residual at e0, as a certified Pair ------------
    def _dres_h(self, j: int, k: int):
        res, extra = Pair({}), arb(0)
        for i in range(k + 1):
            c = arb(comb(k, i))
            src, s = self.P["h", j - 1, k - i], self.sup["h", j - 1, k - i]
            res = res - self.K(src, i + 1).scale(c)
            extra = extra + c * Z_RANGE * s * self.eps_zi(i + 1)
        return res, extra

    def _dres_S(self, r: int, k: int):
        res, extra = Pair({}), arb(0)
        for i in range(k + 1):
            c = arb(comb(k, i))
            src, s = self.P["h", r, k - i], self.sup["h", r, k - i]
            res = res - self.J(src, i + 1).scale(c)
            extra = extra + c * self._J_trunc(i + 1, s)
        return res, extra

    def _dres_W(self, r: int, j: int, k: int):
        res, extra = Pair({}), arb(0)
        for i in range(k + 1):
            c = arb(comb(k, i))
            src, s = self.P["W", (r, j - 1), k - i], self.sup["W", (r, j - 1), k - i]
            res = res - self.K(src, i + 1).scale(c)
            extra = extra + c * Z_RANGE * s * self.eps_zi(i + 1)
        return res, extra

    def _dres_H(self, r: int):
        res = (Pair({}) - self.K(self.P["H", r, 0], 1)
               - self.K(self.P["F", r, 0], 3)
               - self.K(self.P["D", r, 0], 2).scale(arb(2)))
        extra = Z_RANGE * (self.sup["H", r, 0] * self.eps_zi(1)
                           + self.sup["F", r, 0] * self.eps_zi(3)
                           + arb(2) * self.sup["D", r, 0] * self.eps_zi(2))
        return res, extra

    # ---- assemble the second-order whole-cell bound ------------------------
    def _tighten(self, entry: dict, dres, dextra, env2) -> dict:
        rho = exact(self.rho)
        d_mid = tight_upper(self._range(dres) + tight_upper(dextra))
        new_cell = tight_upper(entry["delta_mid"] + rho * d_mid
                               + rho * rho / arb(2) * tight_upper(env2))
        old_cell = entry["delta_cell"]
        if not old_cell >= new_cell:
            raise BoundRegression(
                f"{entry['object']}: second-order bound {new_cell.str(10)} is "
                f"not <= the predecessor {old_cell.str(10)}")
        out = dict(entry)
        out.update({"delta_cell": new_cell,
                    "predecessor_delta_cell": old_cell,
                    "d_e_residual_at_e0": d_mid,
                    "second_derivative_envelope": tight_upper(env2),
                    "tightening": "second_order_taylor_in_e"})
        return out

    def _tighten_closed(self, entry: dict, n: int) -> dict:
        """Closed-form leaf: drift-aware pointwise supremum of S_0^(n)."""
        rho = exact(self.rho)
        env = sup_source_derivative_on(n, self.left, self.right)
        new_cell = tight_upper(entry["delta_mid"] + rho * env)
        if not entry["delta_cell"] >= new_cell:
            raise BoundRegression(f"{entry['object']}: closed-form bound loosened")
        out = dict(entry)
        out.update({"delta_cell": new_cell,
                    "predecessor_delta_cell": entry["delta_cell"],
                    "envelope": env,
                    "tightening": "drift_aware_closed_form_supremum"})
        return out

    def all_residuals(self) -> dict:
        out = super().all_residuals()

        # closed-form leaves: h_1^(k) uses sup|S_0^(k)|, S_0^(k) uses sup|S_0^(k+1)|
        for k in range(3):
            out[f"h_1:{k}"] = self._tighten_closed(out[f"h_1:{k}"], k)
            out[f"Sclosed_{k}"] = self._tighten_closed(out[f"Sclosed_{k}"], k + 1)
            out[f"S_0:{k}"] = self._tighten_closed(out[f"S_0:{k}"], k + 1)

        for j, k in ORDER2_H:
            dres, dex = self._dres_h(j, k)
            out[f"h_{j}:{k}"] = self._tighten(out[f"h_{j}:{k}"], dres, dex,
                                              self._env2_h(j, k))
        for r, k in ORDER2_S:
            dres, dex = self._dres_S(r, k)
            out[f"S_{r}:{k}"] = self._tighten(out[f"S_{r}:{k}"], dres, dex,
                                              self._env2_S(r, k))
        for r in range(5):
            dres, dex = self._dres_H(r)
            out[f"H_{r}"] = self._tighten(out[f"H_{r}"], dres, dex,
                                          self._env2_H(r))
        import cusum_layer1 as L1
        for (r, j) in L1.W_INDICES:
            dres, dex = self._dres_W(r, j, 2)
            out[f"W_{r}_{j}:2"] = self._tighten(out[f"W_{r}_{j}:2"], dres, dex,
                                                self._env2_W(r, j, 2))
        self.residuals = out
        return out

    def tightening_report(self) -> dict:
        rows = {}
        for name, o in self.residuals.items():
            if "predecessor_delta_cell" not in o:
                continue
            old = float(o["predecessor_delta_cell"].abs_upper())
            new = float(o["delta_cell"].abs_upper())
            rows[name] = {"predecessor": old, "tightened": new,
                          "factor": old / new if new else None,
                          "method": o["tightening"]}
        return rows
