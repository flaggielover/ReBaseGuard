"""SRK consumer adapter: the only place SRK touches the frozen TC-T consumer path (design for a formal campaign).

The frozen path computes, per tail cell, the TC-T whole-cell enclosure of R''_m through
``tct_rule.tail_enclosure(R, meas, aux, A, m)`` -> (lo, hi, obj), where obj[r] carries f_G, env4, p, rad, half,
sigma3, sigma4 (see p5y_k5_m5_tail_closure/code/tct_rule.py, read-only).  SRK changes exactly one thing: the per-object
half width half_r = rad_r (|G(a)| = 0) becomes rad_r^SRK (THEOREM_SRK section 3), and the enclosure is re-assembled
with the frozen coefficient table.  Everything else (H_at_a centres, W2 enclosures, coefficients, the intersection
with R2_interval, M, the direct clause) is untouched and stays in the frozen path.

This module never imports the frozen consumer.  The formal driver INJECTS the pinned functions:
  frozen_obj   : the obj dict returned by the pinned tct_rule.tail_enclosure for the cell
  frozen_lohi  : (lo, hi) returned by the same call
  coefficients : the pinned tc_rule.coefficients
Reproduction gate (must hold before the SRK enclosure is used): with every Gamma_i = None the re-assembly equals
frozen_lohi EXACTLY; otherwise the adapter refuses (REPRODUCTION_FAILED).
"""
from __future__ import annotations

from fractions import Fraction as F

import srk_assemble as SA
import srk_gate as GT


class AdapterRefusal(ValueError):
    pass


def fields_for_r(meas: dict, obj_r: dict, rho: F, A: dict, r: int) -> dict:
    m = meas["r"][str(r)]
    return {"sF": F(m["sup"]["F"]), "sD": F(m["sup"]["D"]), "sH": F(m["sup"]["H"]),
            "fF": F(m["delta_F"]) + F(m["eps_src"][0]), "fD": F(m["delta_D"]) + F(m["eps_src"][1]),
            "fH": F(m["delta_H"]) + F(m["eps_src"][2]), "fG": F(obj_r["f_G"]), "Env4": F(obj_r["env4"]),
            "sigma3": F(obj_r["sigma3"]), "eps3": F(m["eps_src"][3]), "sigma4": F(obj_r["sigma4"]),
            "rho": F(rho), "A0": F(A["A0"]), "A1": F(A["A1"]), "A2": F(A["A2"])}


def assemble(meas: dict, halves: dict, m: int, coefficients) -> tuple:
    lo = hi = F(0)
    for kind, r, jj, c in coefficients(m):
        if kind == "F":
            a, b = (F(x) for x in meas["r"][str(r)]["H_at_a"])
            if a > b:
                raise AdapterRefusal("inverted centre interval")
            lo += c * (a - halves[r])
            hi += c * (b + halves[r])
        else:
            a, b = (F(x) for x in meas["W2"][f"{r}:{jj}"])
            if a > b or c < 0:
                raise AdapterRefusal("inverted W enclosure or negative coefficient")
            lo += c * a
            hi += c * b
    return lo, hi


def srk_enclosure(meas: dict, A: dict, m: int, gate_result, frozen_obj: dict, frozen_lohi: tuple,
                  coefficients, allow_test_gamma: bool = False) -> dict:
    """gate_result must be a srk_gate.GateResult (review R1 B2): Gamma-bar values reach the consumer only through the
    certificate gate.  allow_test_gamma=True admits a raw {i: value} dict and exists for unit tests only."""
    if isinstance(gate_result, GT.GateResult):
        if gate_result.source not in ("GATE", "GATE_TABOO", "GATE_MIN", "EMPTY"):
            raise AdapterRefusal(f"unknown GateResult source {gate_result.source!r}")
        gamma = gate_result.gamma
    elif allow_test_gamma and isinstance(gate_result, dict):
        gamma = gate_result
    else:
        raise AdapterRefusal("Gamma-bar must come from srk_gate.gate() (GateResult)")
    rho = F(meas["rho"])
    # reproduction gate: the frozen half widths must be exactly rad_r (|G(a)| = 0, (P2'))
    base_halves = {}
    for r in range(5):
        o = frozen_obj[r]
        if F(o.get("abs_G_at_a", 0)) != 0 or F(o.get("sup_G", 0)) != 0:
            raise AdapterRefusal("SRK-0 applies to the zero order-3 candidate (P2') only")
        rt = SA.rad_tct(fields_for_r(meas, o, rho, A, r))
        if rt != F(o["rad"]) or F(o["half"]) != rt:
            raise AdapterRefusal(f"REPRODUCTION_FAILED: r={r} frozen rad/half != recomputed TC-T radius")
        base_halves[r] = rt
    if assemble(meas, base_halves, m, coefficients) != (F(frozen_lohi[0]), F(frozen_lohi[1])):
        raise AdapterRefusal("REPRODUCTION_FAILED: re-assembly with TC-T half widths != frozen enclosure")
    halves, per = {}, {}
    for r in range(5):
        out = SA.rad_srk(fields_for_r(meas, frozen_obj[r], rho, A, r), gamma)
        halves[r] = out["rad_srk"]
        per[r] = {k: out[k] for k in ("rad_srk", "rad_tct", "branch3", "branch4")}
    lo, hi = assemble(meas, halves, m, coefficients)
    if not (lo >= F(frozen_lohi[0]) and hi <= F(frozen_lohi[1])):
        raise AdapterRefusal("dominance violated (SRK enclosure not inside the TC-T enclosure)")
    return {"lo": lo, "hi": hi, "per_r": per, "frozen_lo": F(frozen_lohi[0]), "frozen_hi": F(frozen_lohi[1])}
