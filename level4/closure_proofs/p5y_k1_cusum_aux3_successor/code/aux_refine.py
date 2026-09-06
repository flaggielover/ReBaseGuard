"""PHASE 8-10: the second-order node bound that consumes the auxiliary evidence.

THE MEASURED PROBLEM
--------------------
Every whole-cell node value in the frozen DAG is a CASCADE: each node's cell
value is its own local residual plus operator norms times its dependencies' cell
values. At cell 321 the m=5 curvature obligation is dominated by

    S_4^(2) = 2.4577
      = j_0 h_4^(2) (1.093) + 2 j_1 h_4^(1) (1.040) + j_2 h_4^(0) (0.325) + local
    h_4^(2) = 1.679
      = k_0 h_3^(2) (0.769) + 2 k_1 h_3^(1) (0.698) + k_2 h_3^(0) (0.190) + local

seeded by `rho * sup_cell|phi''| = 0.0586` and multiplied by about 2.98 per level.
None of it is equation defect: it is the distance the TRUE object travels across
the cell while the candidate stays fixed in `e`.

THE BOUND
---------
Every candidate is a state-only polynomial, constant in `e`, so for the error
function `E(e) = Xhat^(k) - X^(k)(e)`:

    E'(e) = -X^(k+1)(e),   E''(e) = -X^(k+2)(e)

and Taylor at `e0` with the integral remainder, pointwise in `x`, then sup over
`x`, gives for every `|e - e0| <= rho`:

    eps_cell(X^(k)) <= eps_mid(X^(k))
                     + rho * || X^(k+1)(e0) ||
                     + (rho^2/2) * sup_cell || X^(k+2) ||

    || X^(k+1)(e0) || <= sup|Xhat^(k+1)| + eps_mid(X^(k+1))       (midpoint)
    sup_cell || X^(k+2) || <= T[X, k+2]                            (norm tower)

For `k = 2` the middle term needs `X^(3)` at the midpoint: that is exactly the
auxiliary evidence `aux_certifier` produces. For `k = 0, 1` it needs `X^(1)` and
`X^(2)`, which the frozen object set already carries.

WHY THIS WINS, MEASURED
-----------------------
The norm tower massively overstates the true derivatives, because it multiplies
operator norms by candidate suprema and sums absolute values with no
cancellation. At cell 321:

    sup|hhat_4^(3)| = 0.0394   against tower T[4,3] = 19.81      ( 500x)
    sup|Shat_4^(3)| = 0.00067  against tower U[4,3] = 35.58    (53000x)

so the first-order term collapses and only the `rho^2/2` remainder is left. The
cascade and the Taylor bound are computed for every node and the SMALLER is kept,
so the method is uniform: no cell is tuned, nothing is chosen per cell, and a node
where the cascade already wins simply keeps it.

THE TOWERS
----------
Norm-only bounds on the TRUE objects, from the same frozen recursions:

    T_h[1,0]   <= 1                    T_h[1,n]   = sup_cell |S_0^(n-1)|
    T_h[j,n]   <= sum_i C(n,i) k_i T_h[j-1,n-i]
    T_S[0,n]   = sup_cell |S_0^(n)|
    T_S[r,n]   <= sum_i C(n,i) j_i T_h[r,n-i]
    T_W[r,0,n] = T_S[r,n]
    T_W[r,j,n] <= sum_i C(n,i) k_i T_W[r,j-1,n-i]

evaluated at `n <= 4`, which needs `k_i`, `j_i` for `i <= 4` -- the orders the
drift-aware norm table already provides -- and `sup_cell|S_0^(n)|` for `n <= 4`,
which is the drift-aware pointwise supremum with `He_(n+1)` roots.

RIGOUR
------
Each of the three terms is an upper bound on a distinct piece of an exact Taylor
identity; none is an estimate. The result is combined with the cascade by `min`,
and `assert_not_looser` refuses any node whose kept value exceeds the cascade, so
the pass can only tighten. The auxiliary evidence is used only at the midpoint,
so no whole-cell order-3 quantity is ever required.
"""
from __future__ import annotations

from math import comb

import ancestry                                                 # noqa: F401

from flint import arb                                           # noqa: E402

import cusum_layer1 as L1                                       # noqa: E402
from intervals import exact, mag_fraction, tight_upper          # noqa: E402
from order2 import sup_source_derivative_on                     # noqa: E402

MAX_TOWER_ORDER = 4
METHOD = "second_order_taylor_in_e_with_auxiliary_third_derivative_evidence"


class NodeBoundRegression(RuntimeError):
    """A node bound came out looser than the frozen cascade; refuse it."""


def _min(a: arb, b: arb) -> arb:
    return a if a.upper() <= b.upper() else b


def towers(cert) -> dict:
    """Norm-only cell bounds on the TRUE objects, orders 0..4."""
    k_, j_ = cert.norms["k"], cert.norms["j"]
    s0 = {n: sup_source_derivative_on(n, cert.left, cert.right)
          for n in range(MAX_TOWER_ORDER + 1)}
    T = {("h", 1, 0): arb(1)}
    for n in range(MAX_TOWER_ORDER):
        T["h", 1, n + 1] = s0[n]
    for j in range(2, 5):
        for n in range(MAX_TOWER_ORDER + 1):
            acc = arb(0)
            for i in range(n + 1):
                acc = acc + arb(comb(n, i)) * k_[i] * T["h", j - 1, n - i]
            T["h", j, n] = tight_upper(acc)
    for n in range(MAX_TOWER_ORDER + 1):
        T["S", 0, n] = s0[n]
        for r in range(1, 5):
            acc = arb(0)
            for i in range(n + 1):
                acc = acc + arb(comb(n, i)) * j_[i] * T["h", r, n - i]
            T["S", r, n] = tight_upper(acc)
    for r in range(4):
        for n in range(MAX_TOWER_ORDER + 1):
            T["W", (r, 0), n] = T["S", r, n]
    for (r, j) in L1.W_INDICES:
        for n in range(MAX_TOWER_ORDER + 1):
            acc = arb(0)
            for i in range(n + 1):
                acc = acc + arb(comb(n, i)) * k_[i] * T["W", (r, j - 1), n - i]
            T["W", (r, j), n] = tight_upper(acc)
    return T


class AuxiliaryRefinement:
    """Explicitly constructed refinement backend. No global state, no patching.

    Built once per cell and passed by reference into the propagation; it holds
    the certified auxiliary evidence and answers one question per node:
    "is there a Taylor bound smaller than the cascade value you just computed?"
    """

    method = METHOD

    def __init__(self, cert, mid_nodes: dict, aux_mid: dict):
        self.cert = cert
        self.rho = exact(cert.rho)
        self.half_rho2 = self.rho * self.rho / arb(2)
        self.mid = dict(mid_nodes)
        self.mid.update(aux_mid)
        self.T = towers(cert)
        self.decisions: dict = {}

    # ---------------------------------------------------------- node bound
    def _candidate_sup(self, family, index, order) -> arb:
        return self.cert.sup[family, index, order]

    def taylor_bound(self, family, index, order: int, node: str):
        """eps_mid + rho*||X^(k+1)(e0)|| + (rho^2/2)*T[X,k+2], or None."""
        if order >= 3:
            return None
        nxt = f"{node[:node.rfind(':')]}:{order + 1}"
        if nxt not in self.mid:
            return None
        key = (family, index, order + 1)
        if key not in self.cert.sup:
            return None
        at_e0 = tight_upper(self.cert.sup[key] + self.mid[nxt])
        tower = self.T[family, index, order + 2]
        return tight_upper(self.mid[node] + self.rho * at_e0
                           + self.half_rho2 * tower), at_e0, tower

    def bound(self, family, index, order: int, node: str, cascade):
        """min(cascade, Taylor) for one node, plus the recorded decision.

        Pure: it computes and returns, it does not write anywhere. The reviewed
        `ErrorDAG` forbids reassigning a node -- its double-counting guard -- and
        that guard is right, so the refined values live in a derived object
        rather than being written back over the frozen cascade.
        """
        found = self.taylor_bound(family, index, order, node)
        if found is None:
            self.decisions[node] = {"kept": "cascade",
                                    "reason": "no auxiliary evidence at this order"}
            return cascade
        taylor, at_e0, tower = found
        kept = _min(cascade, taylor)
        if kept.upper() > cascade.upper():
            raise NodeBoundRegression(f"{node}: kept bound exceeds the cascade")
        self.decisions[node] = {
            "kept": "taylor" if taylor.upper() < cascade.upper() else "cascade",
            "cascade": str(mag_fraction(cascade)),
            "taylor": str(mag_fraction(taylor)),
            "eps_mid": str(mag_fraction(self.mid[node])),
            "derivative_at_e0": str(mag_fraction(at_e0)),
            "tower_next_order": str(mag_fraction(tower)),
            "factor": (float(mag_fraction(cascade) / mag_fraction(kept))
                       if mag_fraction(kept) > 0 else None),
        }
        return kept

    # ------------------------------------------------------------- report
    def report(self) -> dict:
        taken = [n for n, d in self.decisions.items() if d["kept"] == "taylor"]
        factors = [d["factor"] for d in self.decisions.values()
                   if d.get("factor") and d["kept"] == "taylor"]
        return {"method": self.method,
                "nodes_considered": len(self.decisions),
                "nodes_tightened": len(taken),
                "best_factor": max(factors) if factors else None,
                "median_factor": (sorted(factors)[len(factors) // 2]
                                  if factors else None),
                "decisions": dict(sorted(self.decisions.items()))}
