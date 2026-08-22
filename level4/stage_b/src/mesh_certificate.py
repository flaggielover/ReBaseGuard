"""Root and multiplier certificate from THIN-e runs plus a certified |G''|.

Why not an interval-e operator
------------------------------
Enclosing the segment masses over an interval of `e` is hopeless per segment:
`mass_i(e) = Phi(b_i+e) - Phi(a_i+e)` and any per-segment enclosure loses the
constraint that all segments share ONE `e`.  Even the sharp first-order form
costs `w * TV(phi) = 0.8 w` of spurious total mass per source cell, which is
then multiplied by ||G|| and by the resolvent — about `31 w` of error.  With
the `w` that interval Newton needs, that swamps the answer.  (Measured: the
naive enclosure gives total continuation mass 4.47 at w = 0.012, so the upper
operator is expansive and the iteration diverges outright.)

What is done instead
--------------------
Every operator solve is at a THIN `e`, where the mass telescopes exactly and
the total continuation mass is <= 1 to 6 decimal places.  The `e`-dependence is
then handled analytically:

* **Existence** — `H(e) = 2e + G_e(0,0)` is certified at two thin points with
  `H(e_1) < 0 < H(e_2)`; `H` is continuous (Lemma L4), so IVT gives a root.
* **Uniqueness** — `H'` is certified at a mesh of thin points, and
  `|H''| = |G''| <= M` bounds how far `H'` can move between them:
  `H'(e) >= min_i H'_lo(e_i) - M * delta/2 > 0` on the whole interval, so `H`
  is strictly increasing and the root is unique.
* **Multiplier** — the same mesh bounds `F_1'(I)` and hence `lambda_2`.

`M` comes from differentiating the operator equation twice:

    (I - K_e) G'' = 2 (d_e K_e) G' + (d_e^2 K_e) G + d_e^2 r_e

with the analytic operator norms
    ||d_e K_e||   <= int |phi'|  = 2 phi(0) = 0.797884...
    ||d_e^2 K_e|| <= int |phi''| = 4 phi(1) = 0.967883...
    ||d_e^2 r_e|| <= int |w||phi''(w)| dw + |e| int |phi''| = 1.137827... + |e| * 0.967883...
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np

# Analytic constants (exact closed forms; verified in tests/test_constants.py).
PHI0 = 0.3989422804014327          # phi(0) = 1/sqrt(2 pi)
PHI1 = 0.24197072451914337         # phi(1)
INT_ABS_PHI1 = 2.0 * PHI0          # int |phi'|  = 2 phi(0)
INT_ABS_PHI2 = 4.0 * PHI1          # int |phi''| = 4 phi(1)
# int |w| |phi''(w)| dw = 2 int_0^inf w |w^2-1| phi
#   = 2[ (-phi(0) + 2 phi(1)) + 2 phi(1) ] = 8 phi(1) - 2 phi(0)
INT_W_ABS_PHI2 = 8.0 * PHI1 - 2.0 * PHI0
SAFETY = 1.0001                    # covers float evaluation of the constants


def sup_norm(lower: np.ndarray, upper: np.ndarray) -> float:
    return float(np.max(np.maximum(np.abs(lower), np.abs(upper))))


def second_derivative_bound(
    *, resolvent: float, g_sup: float, gp_sup: float, e_abs_max: float
) -> dict[str, float]:
    """Rigorous ||G''||_inf from the twice-differentiated operator equation."""
    d2r = INT_W_ABS_PHI2 + e_abs_max * INT_ABS_PHI2
    rhs = (2.0 * INT_ABS_PHI1 * gp_sup + INT_ABS_PHI2 * g_sup + d2r)
    return {
        "resolvent": resolvent,
        "G_sup": g_sup,
        "Gprime_sup": gp_sup,
        "d2r_bound": d2r,
        "rhs_bound": rhs,
        "G_second_bound": resolvent * rhs * SAFETY,
    }


def self_consistent_gprime_sup(
    *, resolvent: float, g_sup: float, gp_sup_mesh: float, half_spacing: float,
    e_abs_max: float, iterations: int = 40,
) -> dict[str, float]:
    """||G'||_inf over the whole interval, not just at the mesh points.

    Between mesh points `G'` can move by at most `half_spacing * ||G''||`, and
    `||G''||` itself depends on `||G'||`.  Solve the resulting scalar fixed
    point `x = A + half_spacing * R * (2 c1 x + c2 g + d2r)`, which contracts
    when `half_spacing * R * 2 c1 < 1`; the contraction factor is reported so a
    reader can check it rather than take it on faith.
    """
    factor = half_spacing * resolvent * 2.0 * INT_ABS_PHI1
    if factor >= 1.0:
        raise ArithmeticError(
            f"mesh too coarse for a self-consistent ||G'|| bound "
            f"(contraction factor {factor:.4f} >= 1); halve the mesh spacing"
        )
    d2r = INT_W_ABS_PHI2 + e_abs_max * INT_ABS_PHI2
    const = half_spacing * resolvent * (INT_ABS_PHI2 * g_sup + d2r)
    x = gp_sup_mesh
    for _ in range(iterations):
        x = gp_sup_mesh + factor * x + const
    x *= SAFETY
    return {"contraction_factor": factor, "Gprime_sup_interval": x,
            "Gprime_sup_at_mesh": gp_sup_mesh, "half_spacing": half_spacing}


@dataclass
class MeshCertificate:
    mesh_e: list[float]
    H_lo: list[float]
    H_hi: list[float]
    F1p_lo: list[float]
    F1p_hi: list[float]
    Hp_lo: list[float]
    Hp_hi: list[float]
    G_lo: list[float]
    G_hi: list[float]
    spacing: float
    half_spacing: float
    resolvent: float
    G_sup: float
    G_sup_mesh: float
    Gprime_sup_mesh: float
    Gprime_sup_interval: float
    G_second_bound: float
    contraction_factor: float
    bracket_lo_index: int
    bracket_hi_index: int
    root_I_lo: float
    root_I_hi: float
    existence_certified: bool
    Hprime_min_over_I: float
    uniqueness_certified: bool
    zero_excluded: bool
    F1prime_I_lo: float
    F1prime_I_hi: float
    lambda2_lo: float
    lambda2_hi: float
    multiplier_certified: bool
    backend: str
    certified_backend: bool
    precision_bits: int | None
    grid: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def assemble(
    *, mesh_e, G_lo, G_hi, Gp_lo, Gp_hi, G_sup_cells, Gp_sup_cells,
    resolvent: float, backend_name: str, certified_backend: bool,
    precision_bits, grid: dict[str, Any],
) -> MeshCertificate:
    e = np.asarray(mesh_e, dtype=float)
    order = np.argsort(e)
    e = e[order]
    G_lo = np.asarray(G_lo)[order]; G_hi = np.asarray(G_hi)[order]
    Gp_lo = np.asarray(Gp_lo)[order]; Gp_hi = np.asarray(Gp_hi)[order]
    spacing = float(np.max(np.diff(e)))
    half = 0.5 * spacing

    H_lo = 2.0 * e + G_lo
    H_hi = 2.0 * e + G_hi
    Hp_lo = 2.0 + Gp_lo
    Hp_hi = 2.0 + Gp_hi
    F1p_lo = 1.0 + Gp_lo
    F1p_hi = 1.0 + Gp_hi

    g_sup = float(np.max(G_sup_cells))
    gp_sup_mesh = float(np.max(Gp_sup_cells))
    e_abs_max = float(np.max(np.abs(e))) + spacing

    # ||G|| and ||G'|| must hold for every e in I, not only at the mesh
    # points.  Between mesh points G can move by at most half_spacing * ||G'||,
    # so inflate the mesh maximum and re-solve the self-consistent bound once.
    # The correction is tiny here, but "tiny" is not the same as "accounted for".
    sc = self_consistent_gprime_sup(
        resolvent=resolvent, g_sup=g_sup, gp_sup_mesh=gp_sup_mesh,
        half_spacing=half, e_abs_max=e_abs_max)
    g_sup_interval = g_sup + half * sc["Gprime_sup_interval"]
    sc = self_consistent_gprime_sup(
        resolvent=resolvent, g_sup=g_sup_interval, gp_sup_mesh=gp_sup_mesh,
        half_spacing=half, e_abs_max=e_abs_max)
    g_sup_interval = g_sup + half * sc["Gprime_sup_interval"]
    sd = second_derivative_bound(
        resolvent=resolvent, g_sup=g_sup_interval,
        gp_sup=sc["Gprime_sup_interval"], e_abs_max=e_abs_max)
    M = sd["G_second_bound"]

    # existence: innermost pair of mesh points with a certified sign change
    neg = np.flatnonzero(H_hi < 0.0)
    pos = np.flatnonzero(H_lo > 0.0)
    if neg.size and pos.size and neg.max() < pos.min():
        i_lo, i_hi = int(neg.max()), int(pos.min())
        exists = True
        I_lo, I_hi = float(e[i_lo]), float(e[i_hi])
    else:
        i_lo, i_hi, exists = -1, -1, False
        I_lo, I_hi = float(e[0]), float(e[-1])

    inside = (e >= I_lo - 1e-15) & (e <= I_hi + 1e-15)
    hp_min = float(np.min(Hp_lo[inside])) - M * half
    unique = bool(exists and hp_min > 0.0)
    zero_excluded = bool(I_lo > 0.0 or I_hi < 0.0)

    f1_lo = float(np.min(F1p_lo[inside])) - M * half
    f1_hi = float(np.max(F1p_hi[inside])) + M * half
    if f1_lo >= 0.0:
        l2_lo, l2_hi = f1_lo * f1_lo, f1_hi * f1_hi
    elif f1_hi <= 0.0:
        l2_lo, l2_hi = f1_hi * f1_hi, f1_lo * f1_lo
    else:
        l2_lo, l2_hi = 0.0, max(f1_lo * f1_lo, f1_hi * f1_hi)

    return MeshCertificate(
        mesh_e=e.tolist(), H_lo=H_lo.tolist(), H_hi=H_hi.tolist(),
        F1p_lo=F1p_lo.tolist(), F1p_hi=F1p_hi.tolist(),
        Hp_lo=Hp_lo.tolist(), Hp_hi=Hp_hi.tolist(),
        G_lo=G_lo.tolist(), G_hi=G_hi.tolist(),
        spacing=spacing, half_spacing=half, resolvent=resolvent,
        G_sup=g_sup_interval, G_sup_mesh=g_sup,
        Gprime_sup_mesh=gp_sup_mesh,
        Gprime_sup_interval=sc["Gprime_sup_interval"],
        G_second_bound=M, contraction_factor=sc["contraction_factor"],
        bracket_lo_index=i_lo, bracket_hi_index=i_hi,
        root_I_lo=I_lo, root_I_hi=I_hi,
        existence_certified=exists,
        Hprime_min_over_I=hp_min, uniqueness_certified=unique,
        zero_excluded=zero_excluded,
        F1prime_I_lo=f1_lo, F1prime_I_hi=f1_hi,
        lambda2_lo=l2_lo, lambda2_hi=l2_hi,
        multiplier_certified=bool(l2_hi < 1.0),
        backend=backend_name, certified_backend=certified_backend,
        precision_bits=precision_bits, grid=grid,
    )
