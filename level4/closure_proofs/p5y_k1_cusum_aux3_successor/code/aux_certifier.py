"""PHASE 7-8: certified auxiliary third-derivative objects.

WHAT THIS IS
------------
Nested internal evidence for the EXISTING frozen curvature obligations. It adds
no top-level work id, no DAG obligation and no charge: the auxiliary certificates
are owned by, and hashed into, the parent cell certificate.

THE DERIVATION, TERM BY TERM
----------------------------
The frozen recursions, differentiated three times in `e` with the Leibniz rule.
Every candidate is a state-only polynomial and is CONSTANT in `e`, so no term is
lost by differentiating the candidates -- only the operators carry `e`.

  h_1:      h_1^(k+1) = -S_0^(k)                     exact, from the frozen
            => h_1^(3) = -S_0^(2)                    closed forms

  h_j:      h_j = K_e h_(j-1)
            d_e^3 (K_e h) = sum_(i=0..3) C(3,i) K_i h^(3-i)
            => h_j^(3) = K_0 h_(j-1)^(3) + 3 K_1 h_(j-1)^(2)
                       + 3 K_2 h_(j-1)^(1) + K_3 h_(j-1)^(0)
            coefficients C(3,0..3) = 1,3,3,1

  S_0:      S_0^(k) = phi^(k)(u+e) - phi^(k)(l+e),  phi^(3) = -He_3 phi
            => S_0^(3) = -He_3(u+e) phi(u+e) + He_3(l+e) phi(l+e)

  S_r:      S_r = J_e h_r,  J_i = Kz_i + e K_i + i K_(i-1)
            => S_r^(3) = sum_(i=0..3) C(3,i) J_i h_r^(3-i)

  W_(r,j):  W_(r,j) = K_e W_(r,j-1),  W_(r,0) = S_r
            => W_(r,j)^(3) = sum_(i=0..3) C(3,i) K_i W_(r,j-1)^(3-i)

`J_e` itself is already the exact Leibniz expansion of the frozen raw-variable
operator; continuing it to `i = 3` introduces no new structure, and `K_3` is the
`b[3]` coefficient list the reviewed certifier already builds.

WHAT IS CERTIFIED, AND WHAT IS NOT
----------------------------------
For each auxiliary object this produces `delta_mid`: a certified bound on
`|| Xhat^(3) - X^(3)(e0) ||`, the MIDPOINT error, computed exactly the way the
reviewed certifier computes every other midpoint residual (Bernstein range of the
equation defect over the reachable continuum, plus the frozen truncation
allowance). A whole-cell envelope is also recorded for auditability, but the
consumer -- `aux_refine` -- uses only `delta_mid` and the certified candidate
suprema, because the auxiliary evidence enters through a Taylor expansion anchored
at `e0`.

NO CIRCULARITY
--------------
The order-3 objects depend only on orders 0..2 of the SAME frozen recursions plus
lower-index objects of their own order; the dependency order is
`h_1 -> h_2 -> h_3 -> h_4 -> S_r -> W_(r,j)`, strictly increasing, exactly as at
orders 0..2. Nothing at order 3 is consumed by anything at orders 0..2 except
through `aux_refine`'s Taylor remainder, which never feeds back.
"""
from __future__ import annotations

from math import comb

import ancestry                                                 # noqa: F401

from flint import arb                                           # noqa: E402

import cusum_layer1 as L1                                       # noqa: E402
from cusum_layer2 import Pair, Z_HALF, Z_RANGE                    # noqa: E402
from rebaseguard_certify.polynomial import bi_add, bi_mul, bi_scale  # noqa: E402
from intervals import exact, tight_upper                        # noqa: E402

from order2 import Order2Certifier                              # noqa: E402

import aux_collocation                                          # noqa: E402

AUX_ORDER = 3
AUX_KIND = "auxiliary_third_derivative_evidence_v1"


class Aux3Certifier(Order2Certifier):
    """Order2Certifier plus certified auxiliary third-derivative objects.

    Inherits, unchanged: the drift-aware operator norms (adjudicated SOUND), the
    order-2 Taylor tightening of the residuals, the Repair1 single-S0-charge
    correction, and every frozen constant.
    """

    provides_aux_order3 = True

    # ------------------------------------------------------------- setup
    def prepare(self):
        super().prepare()
        self._closed_forms_order3()
        self._candidates_order3()
        return self

    def _closed_forms_order3(self):
        """S_0^(3) and h_1^(3), continuing the frozen closed-form sequence.

            S_0^(k) = (-1)^k [He_k(u+e) phi(u+e) - He_k(l+e) phi(l+e)]
            h_1^(k+1) = -S_0^(k)

        He_3(t) = t^3 - 3t, so the k = 3 line is
            S_0^(3) = -[He_3(au) phi_u - He_3(al) phi_l].
        """
        au, al = self.arg_u, self.arg_l
        he3_u = bi_add(bi_mul(bi_mul(au, au), au), bi_scale(au, -arb(3)))
        he3_l = bi_add(bi_mul(bi_mul(al, al), al), bi_scale(al, -arb(3)))
        s3 = bi_scale(bi_add(bi_mul(he3_u, self.phi_u),
                             bi_scale(bi_mul(he3_l, self.phi_l), -arb(1))),
                      -arb(1))
        self.S0_closed[3] = s3
        self.h1_closed[3] = bi_scale(self.S0_closed[2], -arb(1))
        # Truncation allowance: the closed form is |He_k(A)| times the truncated
        # phi series, so the representation error is majorised by the same
        # coefficient-wise bound the reviewed code uses (|He_k| with every sign
        # taken positive). |He_3(A)| <= A^3 + 3A.
        A = Z_HALF + exact(self.e_max)
        self.reward_allow[3] = arb(2) * (A * A * A + arb(3) * A) * self.eps_r
        self.h1_allow[3] = self.reward_allow[2]
        # Certified suprema of the closed forms, drift-aware, one order further.
        from order2 import sup_source_derivative_on
        self.sup_S0[3] = sup_source_derivative_on(3, self.left, self.right)
        self.sup_h1[3] = self.sup_S0[2]

    def _candidates_order3(self):
        """Degree-12 candidates for every auxiliary object."""
        co3 = aux_collocation.collocation_order3(float(self.e0))
        vals = aux_collocation.objects_order3(self.co, self.obj, co3)
        self.aux_weight = co3["weight"]
        self.P["hclosed", 1, 3] = self.h1_closed[3]
        self.sup["hclosed", 1, 3] = self.sup_h1[3]
        self.P["Sclosed", 0, 3] = self.S0_closed[3]
        self.sup["Sclosed", 0, 3] = self.sup_S0[3]
        for j in range(1, 5):
            self.P["h", j, 3], self.sup["h", j, 3] = self._cand(vals["h3"][j])
        for r in range(5):
            self.P["S", r, 3], self.sup["S", r, 3] = self._cand(vals["S3"][r])
        for (r, j), v in vals["W3"].items():
            if j == 0:
                self.P["W", (r, 0), 3] = self.P["S", r, 3]
                self.sup["W", (r, 0), 3] = self.sup["S", r, 3]
            else:
                self.P["W", (r, j), 3], self.sup["W", (r, j), 3] = self._cand(v)

    # -------------------------------------------------- auxiliary residuals
    def aux_residuals(self) -> dict:
        """Certified midpoint residuals for every auxiliary order-3 object."""
        out = {}
        k_ = self.norms["k"]
        j_ = self.norms["j"]
        n = AUX_ORDER

        # h_1^(3): degree-12 candidate against the exact closed form -S_0^(2).
        self._begin()
        res = Pair(self.P["h", 1, 3]) - Pair(self.P["hclosed", 1, 3])
        out["h_1:3"] = self.certify("h_1:3", res, self.h1_allow[3],
                                    self.sup_S0[3])

        # S_0^(3): degree-12 candidate against the exact closed form.
        self._begin()
        res = Pair(self.P["S", 0, 3]) - Pair(self.P["Sclosed", 0, 3])
        out["S_0:3"] = self.certify(
            "S_0:3", res, self.reward_allow[3],
            from_order2_sup_source(self, 4))

        # h_j^(3) = sum_i C(3,i) K_i h_(j-1)^(3-i)
        for j in range(2, 5):
            self._begin()
            res = Pair(self.P["h", j, 3])
            extra = arb(0)
            env = arb(0)
            for i in range(n + 1):
                c = arb(comb(n, i))
                src = self.P["h", j - 1, n - i]
                s = self.sup["h", j - 1, n - i]
                res = res - self.K(src, i).scale(c)
                extra = extra + c * Z_RANGE * s * self.eps_zi(i)
                env = env + c * k_[i + 1] * s
            out[f"h_{j}:3"] = self.certify(f"h_{j}:3", res, extra, env)

        # S_r^(3) = sum_i C(3,i) J_i h_r^(3-i)
        for r in range(1, 5):
            self._begin()
            res = Pair(self.P["S", r, 3])
            extra = arb(0)
            env = arb(0)
            for i in range(n + 1):
                c = arb(comb(n, i))
                src = self.P["h", r, n - i]
                s = self.sup["h", r, n - i]
                res = res - self.J(src, i).scale(c)
                extra = extra + c * self._J_trunc(i, s)
                env = env + c * j_[i + 1] * s
            out[f"S_{r}:3"] = self.certify(f"S_{r}:3", res, extra, env)

        # W_(r,j)^(3) = sum_i C(3,i) K_i W_(r,j-1)^(3-i)
        for (r, j) in L1.W_INDICES:
            self._begin()
            res = Pair(self.P["W", (r, j), 3])
            extra = arb(0)
            env = arb(0)
            for i in range(n + 1):
                c = arb(comb(n, i))
                src = self.P["W", (r, j - 1), n - i]
                s = self.sup["W", (r, j - 1), n - i]
                res = res - self.K(src, i).scale(c)
                extra = extra + c * Z_RANGE * s * self.eps_zi(i)
                env = env + c * k_[i + 1] * s
            out[f"W_{r}_{j}:3"] = self.certify(f"W_{r}_{j}:3", res, extra, env)

        self.aux = out
        return out


def from_order2_sup_source(cert, n: int) -> arb:
    """sup_cell |S_0^(n)|, drift-aware, for the closed-form envelope."""
    from order2 import sup_source_derivative_on
    return sup_source_derivative_on(n, cert.left, cert.right)


def midpoint_order3_eps(cert, mid_nodes: dict) -> dict:
    """The order-3 midpoint error node values, given the frozen order 0..2 ones.

    `mid_nodes` maps frozen node ids ("h:3:2", "S:4:1", "W:1:2:0", ...) to their
    certified MIDPOINT error bounds. The returned map adds the order-3 nodes.
    """
    k_ = cert.norms["k"]
    j_ = cert.norms["j"]
    res = cert.aux
    n = AUX_ORDER
    out = dict(mid_nodes)

    def eps(node: str) -> arb:
        return out[node]

    out["h:1:3"] = tight_upper(res["h_1:3"]["delta_mid"])
    for j in range(2, 5):
        acc = res[f"h_{j}:3"]["delta_mid"]
        for i in range(n + 1):
            acc = acc + arb(comb(n, i)) * k_[i] * eps(f"h:{j - 1}:{n - i}")
        out[f"h:{j}:3"] = tight_upper(acc)

    out["Sclosed:3"] = tight_upper(res["S_0:3"]["truncation_allowance"])
    out["S:0:3"] = tight_upper(res["S_0:3"]["delta_mid"])
    for r in range(1, 5):
        acc = res[f"S_{r}:3"]["delta_mid"]
        for i in range(n + 1):
            acc = acc + arb(comb(n, i)) * j_[i] * eps(f"h:{r}:{n - i}")
        out[f"S:{r}:3"] = tight_upper(acc)

    for r in range(4):
        out[f"W:{r}:0:3"] = out[f"S:{r}:3"]
    for (r, j) in L1.W_INDICES:
        acc = res[f"W_{r}_{j}:3"]["delta_mid"]
        for i in range(n + 1):
            acc = acc + arb(comb(n, i)) * k_[i] * eps(f"W:{r}:{j - 1}:{n - i}")
        out[f"W:{r}:{j}:3"] = tight_upper(acc)
    return out
