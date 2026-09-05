"""REPAIR 1 applied to the m = 1 scoped path used by the precision diagnostic.

`scoped.residuals_m1` carries the same duplicate as `cusum_layer2.all_residuals`:

    scoped.py   F_0 : Z_RANGE*sup_F*eps_zi(0) + cert.reward_allow[0]
    scoped.py   dF_0: ... + cert.reward_allow[1]
    scoped.py   H_0 : ... + cert.reward_allow[2]

while `_propagate_m1` builds the `Sclosed:k` node from the same quantity. The
correction is identical and is applied through the shared helper so the two
paths cannot drift apart.

The expensive Bernstein range bounds are computed once by the reviewed function
and reused; only the scalar `extra` is recomputed.
"""
from __future__ import annotations

from fractions import Fraction as F

import prior                                                    # noqa: F401

import assembly                                                 # noqa: E402
import ledger                                                   # noqa: E402
import refine                                                   # noqa: E402
import scoped                                                   # noqa: E402
from intervals import mag_fraction, record                      # noqa: E402

from repair_layer2 import correct_residuals                     # noqa: E402


def residuals_m1(cert) -> dict:
    """Reviewed m=1 residuals with the duplicate S0 remainder removed."""
    out = scoped.residuals_m1(cert)
    out = correct_residuals(cert, out)
    cert.residuals = out
    return out


def cell_obligation_m1(cert) -> dict:
    """The complete frozen cover ledger for (cell, m=1), repaired.

    Mirrors `scoped.cell_obligation_m1` exactly, differing only in the residual
    source. The propagation, enclosure, assembly and ledger steps are the
    reviewed ones, reused unchanged.
    """
    residuals_m1(cert)
    mid = scoped._propagate_m1(cert, "delta_mid")
    cellwise = scoped._propagate_m1(cert, "delta_cell")
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
            "scope": "m1_only", "repair": "repair1", "m": {1: led},
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
