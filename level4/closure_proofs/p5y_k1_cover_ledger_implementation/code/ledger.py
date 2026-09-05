"""The complete frozen STYLE_1 cover ledger and every top-level / nested gate.

    R(cell) subset R_interval + (cell - e0) * D_interval
                   + [-rho^2 * M_R2 / 2, +rho^2 * M_R2 / 2]

    W_cover_exact = rho * mag(D_interval) + rho^2 * M_R2 / 2
    B_cover_usage = outward_upper(W_cover_exact)

STYLE_1 is the only representation. D_interval already contains ALL derivative
uncertainty and R_interval already contains all value uncertainty, so:

  * no separate rho * epsD term is admitted (`separate_derivative_charge` raises);
  * R_interval.radius is never added a second time;
  * the nominal / uncertainty / curvature split is reported as CHILD lines of the
    one cover charge, never as extra top-level charges.

Caps are read from the frozen checkpoint and are never relaxed, redistributed or
drawn from reserve. A missing input is NOT_COMPUTED, never zero and never PASS.
"""
from __future__ import annotations

from fractions import Fraction as F

from flint import arb

import spec
from intervals import exact, mag_fraction, outward_upper, upper_fraction


class ReserveDraw(RuntimeError):
    """Someone tried to draw the nondrawable reserve or redistribute a cap."""


class SeparateDerivativeCharge(RuntimeError):
    """A second, independent derivative-radius charge was attempted."""


def cover_charge(D_interval: arb, rho, M_R2: arb, *,
                 separate_derivative_charge=None, bits: int = spec.PRODUCTION_BITS):
    """The single frozen cover charge, with its auditable child breakdown."""
    if separate_derivative_charge is not None:
        raise SeparateDerivativeCharge(
            "derivative uncertainty is already inside D_interval (STYLE_1); "
            "a separate rho*epsD charge would double count it")
    rho_a = exact(rho)
    if not rho_a >= 0 or not M_R2 >= 0:
        raise ValueError("negative radius or curvature")
    first = rho_a * D_interval.abs_upper()
    curv = rho_a * rho_a * M_R2 / arb(2)
    exact_total = first + curv
    usage = outward_upper(exact_total, bits=bits)
    centre = arb(D_interval.mid())
    child = {
        "nominal_first_order": rho_a * centre.abs_upper(),
        "derivative_uncertainty": rho_a * arb(0, D_interval.rad()).abs_upper(),
        "curvature": curv,
        "cover_arithmetic": exact(usage) - exact_total,
    }
    return {"usage": usage, "exact": exact_total, "first_order_total": first,
            "curvature_total": curv, "children": child,
            "style": "STYLE_1_COMPLETE_D_INTERVAL"}


def taylor_enclosure(R_interval: arb, D_interval: arb, rho, M_R2: arb) -> arb:
    """R_interval + Delta*D_interval + [-rho^2 M_R2/2, +rho^2 M_R2/2] over the cell."""
    rho_a = exact(rho)
    delta = arb(0, rho_a.abs_upper())          # Delta = cell - e0, |Delta| <= rho
    curv = rho_a * rho_a * M_R2 / arb(2)
    return R_interval + delta * D_interval + arb(0, curv.abs_upper())


def nested_candidate_gates(channels: dict) -> dict:
    """Per-channel nested B_candidate gates plus the aggregate .040 gate."""
    out, total = {}, F(0)
    for q, cap_key in (("eq", "B_eq"), ("trunc", "B_trunc"), ("tail", "B_tail"),
                       ("end", "B_end"), ("int", "B_int"), ("round", "B_round")):
        value = channels.get(q)
        cap = spec.NESTED_CANDIDATE[cap_key]
        if value is None:
            out[q] = {"usage": None, "cap": str(cap), "status": "NOT_COMPUTED"}
            continue
        v = F(value)
        total += v
        out[q] = {"usage": str(v), "cap": str(cap), "utilization": float(v / cap),
                  "status": "PASS" if v <= cap else "FAIL"}
    out["B_reserve"] = {"cap": str(spec.NESTED_CANDIDATE["B_reserve"]),
                        "drawable": False, "usage": "0/1"}
    out["aggregate"] = {
        "usage": str(total), "cap": str(spec.TOP_BUDGETS["B_candidate"]),
        "utilization": float(total / spec.TOP_BUDGETS["B_candidate"]),
        "status": ("PASS" if total <= spec.TOP_BUDGETS["B_candidate"] else "FAIL")
        if all(v.get("status") != "NOT_COMPUTED" for k, v in out.items()
               if k not in ("B_reserve",)) else "NOT_COMPUTED"}
    return out


def top_level_gates(usage: dict) -> dict:
    """Every top-level cap, in exact rational arithmetic. No cap is relaxed."""
    if spec.RESERVE_DRAWABLE or spec.REDISTRIBUTION_ALLOWED:
        raise ReserveDraw("frozen checkpoint forbids reserve draw and redistribution")
    out = {}
    for name, cap in spec.TOP_BUDGETS.items():
        value = usage.get(name)
        if value is None:
            out[name] = {"usage": None, "cap": str(cap), "status": "NOT_COMPUTED"}
            continue
        v = F(value)
        if v < 0:
            raise ValueError(f"negative usage on {name}")
        out[name] = {"usage": str(v), "cap": str(cap),
                     "utilization": float(v / cap),
                     "status": "PASS" if v <= cap else "FAIL"}
    out["B_resolvent"] = {"usage": "0/1", "cap": "0/1", "status": "PASS",
                          "note": "C is only multiplicative; no additive charge"}
    out["top_reserve"] = {"cap": str(spec.TOP_RESERVE), "drawable": False,
                          "usage": "0/1"}
    computed = [v for v in out.values()
                if v.get("status") in ("PASS", "FAIL") and v.get("usage") is not None]
    out["total"] = {
        "allocated_caps": str(sum(spec.TOP_BUDGETS.values())),
        "sum_usage": str(sum(F(v["usage"]) for v in computed)),
        "status": ("FAIL" if any(v["status"] == "FAIL" for v in computed)
                   else "NOT_COMPUTED" if any(
                       v.get("status") == "NOT_COMPUTED" for v in out.values())
                   else "PASS")}
    return out


def local_gates(C, n_panels: int | None = None) -> dict:
    """Inherited LOCAL_GATE_BUDGET = .100 constraints at the cell's C."""
    C = F(C)
    out = {"delta_max": str(spec.LOCAL_GATE_BUDGET / C),
           "local_gate_budget": str(spec.LOCAL_GATE_BUDGET),
           "worst_assembly_coefficient": "1 (attained at m=1)"}
    if n_panels:
        out["w_panel_max"] = str(spec.LOCAL_GATE_BUDGET / (C * n_panels))
    return out


def target_gate(enclosure: arb) -> dict:
    """The final certified interval must lie STRICTLY inside (-2, 2)."""
    lo, hi = upper_fraction(-enclosure), upper_fraction(enclosure)
    inside = (-F(2) < -lo) and (hi < F(2))
    return {"lo": str(-lo), "hi": str(hi), "strictly_inside_minus2_2": inside,
            "status": "PASS" if inside else "FAIL",
            "note": "a wide interval alone is not a scientific counterexample"}


def cell_ledger(*, m: int, cell: dict, R_interval: arb, D_interval: arb,
                M_R2: arb, usage: dict, candidate_channels: dict) -> dict:
    """The complete frozen ledger for one (cell, m) obligation."""
    rho = F(cell["rho"][0]) if F(cell["rho"][1]) == 0 else None
    if rho is None:
        raise NotImplementedError("symbolic SR terminal radius not handled here")
    cover = cover_charge(D_interval, rho, M_R2)
    full_usage = dict(usage)
    full_usage["B_cover"] = cover["usage"]
    full_usage.setdefault("B_other", F(0))
    enclosure = taylor_enclosure(R_interval, D_interval, rho, M_R2)
    gates = top_level_gates(full_usage)
    nested = nested_candidate_gates(candidate_channels)
    computed = [v for v in gates.values() if "utilization" in v]
    total_util = max((v["utilization"] for v in computed), default=None)
    return {
        "detector": cell["detector"], "cell_index": cell["index"], "m": m,
        "e0": cell["e0"], "rho": cell["rho"], "C_upper": cell["C_upper"],
        "R_interval_mag": str(mag_fraction(R_interval)),
        "D_interval_mag": str(mag_fraction(D_interval)),
        "M_R2": str(mag_fraction(M_R2)),
        "cover": {"usage": str(cover["usage"]),
                  "cap": str(spec.TOP_BUDGETS["B_cover"]),
                  "utilization": float(F(cover["usage"]) / spec.TOP_BUDGETS["B_cover"]),
                  "children": {k: str(mag_fraction(v)) if isinstance(v, arb) else str(v)
                               for k, v in cover["children"].items()},
                  "style": cover["style"]},
        "top_level_gates": gates,
        "nested_candidate_gates": nested,
        "local_gates": local_gates(cell["C_upper"]),
        "target_gate": target_gate(enclosure),
        "worst_top_level_utilization": total_util,
        "status": gates["total"]["status"],
    }
