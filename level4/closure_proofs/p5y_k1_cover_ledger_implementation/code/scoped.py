"""m=1 scoped certification path, used ONLY for the precision diagnostic.

For m = 1 the frozen all-m assembly is exactly

    R_1^(k) = F_0^(k)(x0)

with no finite-power part (`assembly.coefficients(1) == [("F", 0, 0, 1)]`), so
the complete cover ledger for that obligation needs exactly three certified
equations -- F_0, D_0 and H_0 -- plus the closed-form S_0^(k) sources. Nothing
is dropped from the m=1 obligation: this is the whole of it.

This is NOT a reduced-scope certification of the campaign. m = 2, 3, 5 still
require the full h/S/W chain and are computed by the ordinary full path. This
module exists so the 256/384/512-bit comparison can be run at three precisions
without paying the full-cell cost three times.
"""
from __future__ import annotations

from fractions import Fraction as F

from flint import arb

import assembly
import depgraph
import ledger
import opnorms
import propagate
import refine
import spec
from cusum_layer2 import Pair, Z_RANGE
from intervals import exact, mag_fraction, record, tight_upper


def residuals_m1(cert) -> dict:
    """The three certified equations and the closed-form leaves for m = 1."""
    out = {}
    k_ = cert.norms["k"]
    for k in range(3):
        allow = tight_upper(cert.h1_allow[k])
        env = opnorms.sup_source_derivative(k)
        out[f"h_1:{k}"] = {"object": f"h_1:{k}", "polynomial_residual": arb(0),
                           "truncation_allowance": allow, "delta_mid": allow,
                           "envelope": env,
                           "delta_cell": tight_upper(allow + exact(cert.rho) * env),
                           "closed_form": True, "cpu_seconds": 0.0,
                           "bernstein_calls": 0, "kernel_calls": 0}
        allow0 = tight_upper(cert.reward_allow[k])
        env0 = opnorms.sup_source_derivative(k + 1)
        out[f"Sclosed_{k}"] = {"object": f"Sclosed_{k}", "polynomial_residual": arb(0),
                               "truncation_allowance": allow0, "delta_mid": allow0,
                               "envelope": env0,
                               "delta_cell": tight_upper(allow0 + exact(cert.rho) * env0),
                               "closed_form": True, "cpu_seconds": 0.0,
                               "bernstein_calls": 0, "kernel_calls": 0}

    P, sup = cert.P, cert.sup
    cert._begin()
    res = Pair(P["F", 0, 0]) - cert.K(P["F", 0, 0], 0) - Pair(P["Sclosed", 0, 0])
    out["F_0"] = cert.certify(
        "F_0", res,
        Z_RANGE * sup["F", 0, 0] * cert.eps_zi(0) + cert.reward_allow[0],
        k_[1] * sup["F", 0, 0])          # source e-variation lives in epsS

    cert._begin()
    res = (Pair(P["D", 0, 0]) - cert.K(P["D", 0, 0], 0)
           - cert.K(P["F", 0, 0], 1) - Pair(P["Sclosed", 0, 1]))
    out["dF_0"] = cert.certify(
        "dF_0", res,
        Z_RANGE * sup["D", 0, 0] * cert.eps_zi(0)
        + Z_RANGE * sup["F", 0, 0] * cert.eps_zi(1) + cert.reward_allow[1],
        k_[1] * sup["D", 0, 0] + k_[2] * sup["F", 0, 0])

    cert._begin()
    res = (Pair(P["H", 0, 0]) - cert.K(P["H", 0, 0], 0)
           - cert.K(P["F", 0, 0], 2) - cert.K(P["D", 0, 0], 1).scale(arb(2))
           - Pair(P["Sclosed", 0, 2]))
    out["H_0"] = cert.certify(
        "H_0", res,
        Z_RANGE * sup["H", 0, 0] * cert.eps_zi(0)
        + Z_RANGE * sup["F", 0, 0] * cert.eps_zi(2)
        + arb(2) * Z_RANGE * sup["D", 0, 0] * cert.eps_zi(1)
        + cert.reward_allow[2],
        k_[1] * sup["H", 0, 0] + k_[3] * sup["F", 0, 0]
        + arb(2) * k_[2] * sup["D", 0, 0])
    cert.residuals = out
    return out


def _propagate_m1(cert, which: str) -> depgraph.ErrorDAG:
    res = cert.residuals
    dag = depgraph.ErrorDAG(C=exact(cert.C), norms=cert.norms)
    for k in range(3):
        nid = f"Sclosed:{k}"
        dag.local(nid, res[f"Sclosed_{k}"][which],
                  owner=propagate.ORDER_OWNER[k], order=k)
        dag.set(nid, dag._locals[nid])
    dag.local("local:F:0", res["F_0"][which],
              owner="F_equation_certificate_value", order=0)
    dag.resolvent_value("F:0", "local:F:0", ["Sclosed:0"])
    dag.local("local:D:0", res["dF_0"][which],
              owner="dF_equation_certificate", order=1)
    dag.resolvent_derivative("D:0", "local:D:0", "F:0", ["Sclosed:1"])
    dag.local("local:H:0", res["H_0"][which],
              owner="curvature_envelope", order=2)
    dag.resolvent_curvature("H:0", "local:H:0", "F:0", "D:0", ["Sclosed:2"])
    return dag


def cell_obligation_m1(cert) -> dict:
    """The complete frozen cover ledger for the (cell, m=1) obligation."""
    residuals_m1(cert)
    mid = _propagate_m1(cert, "delta_mid")
    cellwise = _propagate_m1(cert, "delta_cell")
    refined = refine.refine(cert, mid, cellwise, rs=(0,))
    F_mid = assembly.enclose(cert.origin(("F", 0, 0)), mid.get("F:0"))
    D_mid = assembly.enclose(cert.origin(("D", 0, 0)), mid.get("D:0"))
    H_cell = assembly.enclose(cert.origin(("H", 0, 0)), refined["eps"]["H:0"])
    R_int = assembly.assemble(1, {0: F_mid}, {})
    D_int = assembly.assemble(1, {0: D_mid}, {})
    R2_int = assembly.assemble(1, {0: H_cell}, {})
    M_R2 = assembly.curvature_bound(R2_int)

    C = F(cert.C)
    rF = cert.residuals["F_0"]
    usage = {"B_candidate": C * mag_fraction(rF["delta_mid"]),
             "B_kernel": C * mag_fraction(mid.get("Sclosed:0")),
             "B_interval": mag_fraction(assembly.assembly_arithmetic_excess(
                 1, {0: F_mid}, {}, R_int)),
             "B_rounding": F(0), "B_other": F(0)}
    channels = {"eq": C * mag_fraction(rF["polynomial_residual"]),
                "trunc": C * mag_fraction(rF["truncation_allowance"]),
                "tail": F(0), "end": F(0), "int": F(0), "round": F(0)}
    led = ledger.cell_ledger(m=1, cell=cert.cell, R_interval=R_int,
                             D_interval=D_int, M_R2=M_R2, usage=usage,
                             candidate_channels=channels)
    led["R_interval"] = record(R_int)
    led["D_interval"] = record(D_int)
    led["R2_interval"] = record(R2_int)
    return {"detector": "CUSUM", "cell_index": cert.cell["index"],
            "e0": cert.cell["e0"], "rho": cert.cell["rho"],
            "C_upper": cert.cell["C_upper"], "precision_bits": cert.bits,
            "scope": "m1_only", "m": {1: led},
            "dag_audit_mid": mid.audit(), "dag_audit_cell": cellwise.audit(),
            "whole_cell_refinement": refined["audit"],
            "objects": {n: {"delta_mid": str(mag_fraction(v["delta_mid"])),
                            "delta_cell": str(mag_fraction(v["delta_cell"])),
                            "envelope": str(mag_fraction(v["envelope"])),
                            "cpu_seconds": v.get("cpu_seconds", 0.0)}
                        for n, v in cert.residuals.items()},
            "eps_mid": {k: str(mag_fraction(v)) for k, v in mid.nodes.items()},
            "eps_cell": {k: str(mag_fraction(v)) for k, v in cellwise.nodes.items()},
            "eps_cell_refined": {k: str(mag_fraction(v))
                                 for k, v in refined["eps"].items()},
            "work": {"bernstein_calls": cert.bernstein_calls,
                     "kernel_calls": cert.kernel_calls}}
