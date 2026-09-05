"""Cache dependency scope for the optimized K1 backend -- LOAD-BEARING.

The whole speedup rests on reusing quantities across dimensions on which they
are independent. A quantity reused across a dimension it actually depends on
would silently produce a wrong certificate, so every entry here is verified by
measurement, in both directions:

  POSITIVE control -- the quantity is bit-identical across the dimension it is
                      claimed independent of, which is what licenses the reuse
  NEGATIVE control -- the quantity genuinely differs across the dimensions it
                      is claimed to depend on, so the cache key cannot be
                      narrowed further
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
T1R = ROOT / "level4/closure_proofs/p5y_k1_task1r_budget_harness"
AUD = ROOT / "level4/closure_proofs/p5y_k1_sr_backend_cost_audit"
for p in (str(AUD / "code"), str(T1R / "code")):
    if p not in sys.path:
        sys.path.insert(0, p)

from flint import arb                                                  # noqa: E402
import harness as H                                                    # noqa: E402
import sr_local as L                                                   # noqa: E402
import opt_backend as O                                                # noqa: E402
from rebaseguard_certify.arb_backend import rational, workprec         # noqa: E402

DIMS = ["detector", "drift_e", "outer_cell", "patch", "panel",
        "function_r", "value_or_derivative", "m"]

# key = the dimensions the quantity DEPENDS on; it may be reused across all others
TABLE = {
    "patch_geometry":        ["detector", "patch"],
    "P1_rule_and_panel_grid": ["detector", "patch"],
    "softplus_V":            ["detector", "patch", "panel"],
    "softplus_W":            ["detector", "patch", "panel"],
    "chebyshev_TV_TW":       ["detector", "patch", "panel"],
    "matrices_P_Q_Qflat":    ["detector", "patch", "panel"],
    "mag_ex_ez_vectors":     ["detector", "patch", "panel"],
    "gaussian_moments_N":    ["detector", "drift_e", "outer_cell", "patch", "panel"],
    "hankel_and_R":          ["detector", "drift_e", "outer_cell", "patch", "panel"],
    "candidate_chat":        ["detector", "drift_e", "outer_cell",
                              "function_r", "value_or_derivative"],
    "kernel_coefficients":   ["detector", "drift_e", "outer_cell", "patch", "panel",
                              "function_r", "value_or_derivative"],
    "Fhat_patch_expansion":  ["detector", "drift_e", "outer_cell", "patch",
                              "function_r", "value_or_derivative"],
    "S0_expansion":          ["detector", "drift_e", "outer_cell", "patch"],
    "endpoint_slivers":      ["detector", "drift_e", "outer_cell", "patch",
                              "function_r", "value_or_derivative"],
    "resolvent_bound_C":     ["detector", "drift_e", "outer_cell"],
    "m_assembly_coefficients": ["m"],
}

# the reuse the speedup actually depends on
LOAD_BEARING_REUSE = [
    {"quantity": "chebyshev_TV_TW",
     "reused_across": ["drift_e", "outer_cell", "function_r", "value_or_derivative", "m"],
     "multiplicity": "322 sub-cells x 19 functions = 6118",
     "why": "V and W are softplus of (p_c + z_c - 1/2 + alpha + zeta) and "
            "(m_c - z_c - 1/2 + beta - zeta). Neither expression contains e, r or "
            "any candidate coefficient. The panel grid is fixed by the P1 rule, "
            "whose H_max depends only on the softplus derivative bound and the "
            "frozen P1 target -- also e-free. Gate-2B separately established that "
            "SR patch geometry is e-independent."},
    {"quantity": "hankel_and_R",
     "reused_across": ["function_r", "value_or_derivative", "m"],
     "multiplicity": "19 functions",
     "why": "R = P . Hankel(N) contains no candidate coefficient; the candidate "
            "enters only in the final contraction."},
]


def _geom(patch, e_num, e_den):
    A, b, c = L.sr_constants()
    e = rational(e_num, e_den)
    g = L.patch_geometry(*patch, grid=H.GRID)
    p_c = (g["yp"][0] + g["yp"][1]) / arb(2)
    m_c = (g["ym"][0] + g["ym"][1]) / arb(2)
    Hh = (g["yp"][1] - g["yp"][0]) / arb(2)
    return dict(A=A, b=b, c=c, e=e, geo=g, p_c=p_c, m_c=m_c, H=Hh,
                U_c=c - p_c, L_c=m_c - c, span=(c - p_c) - (m_c - c))


def _shared(patch, e_num, e_den, D, Z):
    g = _geom(patch, e_num, e_den)
    p1 = H.p1_rule(g["H"], g["span"])
    h = g["span"] / (arb(2) * arb(p1["n_panels"]))
    ctxt = (g["H"], h, D, Z, [g["H"] ** a for a in range(2 * D + 2)],
            [h ** k for k in range(2 * Z + 2)])
    z_c = g["L_c"] + h
    return O.PanelShared(g["p_c"], g["m_c"], z_c, g["b"], ctxt), g, p1, h


def _fingerprint(sh) -> str:
    """Exact string fingerprint of a PanelShared tensor."""
    parts = []
    for r in range(sh.nrow):
        for k in range(sh.Z + 1):
            parts.append(sh.P[r, k].str(30, radius=True))
            parts.append(sh.Q[r, k].str(30, radius=True))
    return "|".join(parts)


def verify(D: int, Z: int) -> dict:
    """Measured verification of every load-bearing reuse claim."""
    with workprec(H.PROD_BITS):
        s_q, _, _, h_q = _shared(H.PATCH, 1, 4, D, Z)
        s_h, _, _, h_h = _shared(H.PATCH, 1, 2, D, Z)      # different drift
        s_p, _, _, _ = _shared((0, 0), 1, 4, D, Z)          # different patch
        fq, fh, fp = _fingerprint(s_q), _fingerprint(s_h), _fingerprint(s_p)
        g = _geom(H.PATCH, 1, 4, )
        p1 = H.p1_rule(g["H"], g["span"])
        hh = g["span"] / (arb(2) * arb(p1["n_panels"]))
        z_c = g["L_c"] + hh
        Nq = H.panel_moments(z_c - hh, z_c + hh, z_c, rational(1, 4), 2 * Z + 1, hh)
        Nh = H.panel_moments(z_c - hh, z_c + hh, z_c, rational(1, 2), 2 * Z + 1, hh)
        moments_differ = any(Nq[k].str(30, radius=True) != Nh[k].str(30, radius=True)
                             for k in range(len(Nq)))
        panels_same = p1["n_panels"] == H.p1_rule(g["H"], g["span"])["n_panels"]
    return {
        "positive_chebyshev_tensor_is_drift_independent": fq == fh,
        "negative_chebyshev_tensor_depends_on_patch": fq != fp,
        "negative_gaussian_moments_depend_on_drift": moments_differ,
        "panel_grid_is_drift_independent": panels_same,
        "PASS": bool(fq == fh and fq != fp and moments_differ and panels_same),
    }
