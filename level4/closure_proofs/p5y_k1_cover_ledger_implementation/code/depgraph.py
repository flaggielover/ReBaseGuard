"""Complete derivative dependency propagation (frozen ERROR_ALGEBRA sections 1, 2, 6).

Implements, with an auditable edge log and hard no-double-counting checks:

    epsF_r = C * (deltaF_r + epsS_r)
    epsD_r = C * (deltaD_r + k1 * epsF_r + epsS1_r)
    epsH_r = C * (deltaH_r + k2 * epsF_r + 2 * k1 * epsD_r + epsS2_r)   [whole cell]

and the general operator-sum edge rule

    Y = sum_i b_i T_i X_i    =>    epsY <= lY + sum_i |b_i| ||T_i|| epsX_i

whose finite-power specialisation is the frozen Leibniz recurrence

    epsW_next,0 <= l0 + k0 epsW0
    epsW_next,1 <= l1 + k0 epsW1 + k1 epsW0
    epsW_next,2 <= l2 + k0 epsW2 + 2 k1 epsW1 + k2 epsW0.

Ownership is by the frozen 4-tuple key
(primitive_certificate, propagation_path, destination_quantity, derivative_order):
a contribution may legitimately reach both R(e0) and R'(e0), but the SAME tagged
edge may never be added twice. `Charge` uniqueness is enforced, not assumed.

Two structural prohibitions are enforced as exceptions rather than conventions:

  * `B_candidate` may never receive a derivative-order-1 or -2 charge. The old
    campaign's `C * delta_dF` value-style charge against B_candidate is the
    defect this successor exists to repair; `ValueStyleDerivativeCharge` is
    raised if it is attempted.
  * `cover()` refuses a separate rho*epsD term: derivative uncertainty is inside
    D_interval exactly once (STYLE_1).

All arithmetic is Arb ball arithmetic at the frozen 256-bit production
precision; every bound is an upper endpoint after outward rounding.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction as F

from flint import arb

import spec
from intervals import exact, tight_upper


class DoubleCountingError(RuntimeError):
    """The same tagged propagation edge or ledger charge was added twice."""


class ValueStyleDerivativeCharge(RuntimeError):
    """A derivative-order term was charged to a value channel (the old defect)."""


class MissingDependency(RuntimeError):
    """A propagation consumed a node that has no certificate."""


DERIVATIVE_OWNERS = {
    "dF_equation_certificate", "Kprime_F_dependency", "derivative_source_dependency",
    "finite_derivative_chain", "derivative_arithmetic", "curvature_envelope",
    "nominal_drift_variation", "cover_arithmetic",
}
VALUE_CHANNELS = {"B_candidate", "B_kernel", "B_rounding", "B_interval"}


@dataclass(frozen=True)
class Edge:
    """One propagation edge, exactly the record ERROR_ALGEBRA section 2 demands."""
    source_id: str
    dest_id: str
    derivative_order: int
    coefficient: str            # exact rational string
    norm_bound: str             # exact rational upper bound of ||T_i||
    local_certificate_ids: tuple
    owner: str


@dataclass(frozen=True)
class Charge:
    """A ledger charge keyed by the frozen ownership 4-tuple."""
    primitive_certificate: str
    propagation_path: str
    destination_quantity: str
    derivative_order: int
    owner: str
    amount: str                 # exact rational string


@dataclass
class ErrorDAG:
    """Node error bounds plus the audit log of how each was produced."""
    C: arb
    norms: dict
    nodes: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)
    charges: dict = field(default_factory=dict)
    _edge_keys: set = field(default_factory=set)
    _locals: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ nodes
    def local(self, node_id: str, value: arb, *, owner: str, order: int) -> arb:
        """Record a LOCAL certificate (a residual/defect), not a propagation."""
        if node_id in self._locals:
            raise DoubleCountingError(f"local certificate {node_id} declared twice")
        value = tight_upper(value)
        if not value >= 0:
            raise ValueError(f"local certificate {node_id} must be nonnegative")
        self._check_owner(owner, order, node_id)
        self._locals[node_id] = value
        return value

    def get(self, node_id: str) -> arb:
        if node_id not in self.nodes:
            raise MissingDependency(f"no certificate for {node_id}")
        return self.nodes[node_id]

    def set(self, node_id: str, value: arb) -> arb:
        if node_id in self.nodes:
            raise DoubleCountingError(f"node {node_id} assigned twice")
        self.nodes[node_id] = tight_upper(value)
        return self.nodes[node_id]

    # ------------------------------------------------------------------ rules
    def _check_owner(self, owner: str, order: int, what: str) -> None:
        budget = spec.CLAIMANT_OWNERS.get(owner)
        if budget is None:
            raise ValueError(f"unknown claimant {owner!r}")
        if order >= 1 and budget in VALUE_CHANNELS:
            raise ValueStyleDerivativeCharge(
                f"{what}: derivative order {order} may not be charged to {budget} "
                f"via claimant {owner!r}; the frozen ledger routes every derivative "
                f"and curvature term to B_cover")

    def _edge(self, src: str, dest: str, order: int, coeff, norm, locals_, owner) -> None:
        key = (src, dest, order, str(F(coeff)), owner)
        if key in self._edge_keys:
            raise DoubleCountingError(f"duplicate tagged edge {key}")
        self._edge_keys.add(key)
        self.edges.append(Edge(src, dest, order, str(F(coeff)),
                               _rat(norm), tuple(locals_), owner))

    def operator_sum(self, dest: str, order: int, local_id: str, terms, *, owner: str) -> arb:
        """epsY <= lY + sum_i |b_i| ||T_i|| epsX_i, with one tagged edge per i."""
        self._check_owner(owner, order, dest)
        out = self._locals[local_id]
        for coeff, norm, src in terms:
            eps = self.get(src)
            out = out + exact(abs(F(coeff))) * norm * eps
            self._edge(src, dest, order, abs(F(coeff)), norm, (local_id,), owner)
        return self.set(dest, out)

    def resolvent_value(self, dest: str, delta_id: str, source_ids) -> arb:
        """epsF_r = C * (deltaF_r + epsS_r). Order 0."""
        owner = "F_equation_certificate_value"
        self._check_owner(owner, 0, dest)
        total = self._locals[delta_id]
        for sid in source_ids:
            total = total + self.get(sid)
            self._edge(sid, dest, 0, 1, arb(1), (delta_id,), "source_dependency_value")
        return self.set(dest, self.C * total)

    def resolvent_derivative(self, dest: str, delta_id: str, eps_F_id: str,
                             source1_ids) -> arb:
        """epsD_r = C * (deltaD_r + k1 * epsF_r + epsS1_r). Order 1.

        The k1*epsF term is the dependency the old campaign omitted; it is added
        exactly once, and it is charged to B_cover as Kprime_F_dependency.
        """
        k1 = self.norms["k"][1]
        total = self._locals[delta_id] + k1 * self.get(eps_F_id)
        self._edge(eps_F_id, dest, 1, 1, k1, (delta_id,), "Kprime_F_dependency")
        for sid in source1_ids:
            total = total + self.get(sid)
            self._edge(sid, dest, 1, 1, arb(1), (delta_id,), "derivative_source_dependency")
        self._check_owner("dF_equation_certificate", 1, dest)
        return self.set(dest, self.C * total)

    def resolvent_curvature(self, dest: str, delta_id: str, eps_F_id: str,
                            eps_D_id: str, source2_ids) -> arb:
        """epsH_r = C*(deltaH_r + k2 epsF_r + 2 k1 epsD_r + epsS2_r), whole cell."""
        k1, k2 = self.norms["k"][1], self.norms["k"][2]
        total = (self._locals[delta_id]
                 + k2 * self.get(eps_F_id)
                 + arb(2) * k1 * self.get(eps_D_id))
        self._edge(eps_F_id, dest, 2, 1, k2, (delta_id,), "curvature_envelope")
        self._edge(eps_D_id, dest, 2, 2, k1, (delta_id,), "curvature_envelope")
        for sid in source2_ids:
            total = total + self.get(sid)
            self._edge(sid, dest, 2, 1, arb(1), (delta_id,), "curvature_envelope")
        self._check_owner("curvature_envelope", 2, dest)
        return self.set(dest, self.C * total)

    def power_step(self, dest_prefix: str, src_prefix: str, local_ids, orders=(0, 1, 2)):
        """Frozen Leibniz finite-power recurrence for W_next = K W, orders 0..2."""
        k = self.norms["k"]
        out = {}
        for order in orders:
            terms = []
            for i in range(order + 1):
                from math import comb
                terms.append((comb(order, i), k[i], f"{src_prefix}:{order - i}"))
            owner = ("finite_kernel_chain_value" if order == 0
                     else "finite_derivative_chain" if order == 1
                     else "curvature_envelope")
            out[order] = self.operator_sum(
                f"{dest_prefix}:{order}", order, local_ids[order], terms, owner=owner)
        return out

    # ---------------------------------------------------------------- ledger
    def charge(self, *, primitive: str, path: str, destination: str, order: int,
               owner: str, amount: arb) -> None:
        self._check_owner(owner, order, primitive)
        key = (primitive, path, destination, order)
        if key in self.charges:
            raise DoubleCountingError(f"duplicate ledger charge for {key}")
        self.charges[key] = Charge(primitive, path, destination, order, owner,
                                   _rat(amount))

    def usage_by_budget(self) -> dict:
        out = {b: F(0) for b in spec.TOP_BUDGETS}
        for c in self.charges.values():
            out[spec.CLAIMANT_OWNERS[c.owner]] += F(c.amount)
        return out

    def audit(self) -> dict:
        derivative_edges = [e for e in self.edges if e.derivative_order >= 1]
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "distinct_edge_keys": len(self._edge_keys),
            "duplicate_edges": len(self.edges) - len(self._edge_keys),
            "derivative_edges": len(derivative_edges),
            "derivative_edges_all_cover": all(
                spec.CLAIMANT_OWNERS[e.owner] == "B_cover" for e in derivative_edges),
            "charges": len(self.charges),
            "ownership_key": list(spec.OWNERSHIP_KEY),
        }


def _rat(x) -> str:
    if isinstance(x, arb):
        q = x.upper().fmpq()
        v = F(int(q.p), int(q.q))
    else:
        v = F(x)
    return f"{v.numerator}/{v.denominator}"


# ------------------------------------------------------------------ mirrors
def reference_resolvent_errors(C, delta_F, eps_S, k1, delta_D, eps_Sprime):
    """Exact-rational mirror of the frozen algebra.py reference, for tests."""
    args = tuple(map(F, (C, delta_F, eps_S, k1, delta_D, eps_Sprime)))
    if min(args) < 0:
        raise ValueError("negative error input")
    C, delta_F, eps_S, k1, delta_D, eps_Sprime = args
    eps_F = C * (delta_F + eps_S)
    eps_D = C * (delta_D + k1 * eps_F + eps_Sprime)
    return eps_F, eps_D


def reference_power_step(k0, k1, k2, errors, local_errors):
    e0, e1, e2 = map(F, errors)
    l0, l1, l2 = map(F, local_errors)
    return (F(k0) * e0 + l0,
            F(k0) * e1 + F(k1) * e0 + l1,
            F(k0) * e2 + 2 * F(k1) * e1 + F(k2) * e0 + l2)
