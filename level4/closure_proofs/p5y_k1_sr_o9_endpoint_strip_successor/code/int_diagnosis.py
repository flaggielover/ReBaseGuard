"""DIAGNOSTIC of the pre-existing interval channel (not evidence of any bound).
(1) frozen Gaussian-clamped vs raw exact-recursion panel moments (both rigorous);
(2) the softplus Lagrange interval coefficient replaced by its midpoint -- DELIBERATELY
NON-RIGOROUS, used only to attribute the channel; never a certificate."""
import json
from fractions import Fraction as Fr
import sr_o9_candidates as T, sr_o9_patch_certifier as PC, sr_o9_endpoint_strips as ES
from flint import arb
H, L = PC.H, PC.L
built = T.build_cell_candidates(0, nodes=["F:0:k0"])["scientific"]
cell = T.frozen_cell(0); C = Fr(cell["C_upper"])
frozen_pm, frozen_sp = H.panel_moments, L.softplus_local_enclosure
raw_pm = lambda z_lo, z_hi, z_c, e, kmax, h: list(L.centred_gaussian_moments(z_lo, z_hi, z_c, e, kmax))[: kmax + 1]
def mid_sp(centre, rho, degree):
    a, E_, a_next = frozen_sp(centre, rho, degree)
    return a, E_, arb(a_next.mid())
out = {"case": "cell 0, patch (51,63), F:0:k0, strip method", "int_allowance": float(Fr(1, 500) / C)}
with T.scientific_precision():
    cand = {"F:0:k0": T.to_arb_matrix(built["candidates"][0]["mantissas"])}
    e0 = T.cell_geometry(cell)["e0"]
    for tag, pm, sp in (("frozen_rigorous", frozen_pm, frozen_sp), ("raw_moments_rigorous", raw_pm, frozen_sp),
                        ("lagrange_midpoint_NON_RIGOROUS_DIAGNOSTIC", frozen_pm, mid_sp)):
        H.panel_moments, L.softplus_local_enclosure = pm, sp
        try:
            r = ES.certify_patch_strips(51, 63, e0, cand, cand_hashes={}, C_gate=C, nodes=["F:0:k0"])
        finally:
            H.panel_moments, L.softplus_local_enclosure = frozen_pm, frozen_sp
        out[tag] = r["nodes"]["F:0:k0"]["channels_float"]
print(json.dumps(out, indent=1, sort_keys=True))
