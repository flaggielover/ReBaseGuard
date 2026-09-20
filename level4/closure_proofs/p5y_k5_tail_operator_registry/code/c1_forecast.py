"""Campaign C1, Phase B: consume the certified tail operator registry through theorem TC-T and the frozen K5-B, and
classify the result under the C1 feasibility gate frozen at `36d8e39b` (before this file could produce a number).

Every scientific component is the adopted/frozen one, executed from its pinned bytes:
    Lemma Dv' atom constants      `deflated_consume.atom_constants_r2`      (adopted Perron consumer, ef5d0474)
    theorem TC-T enclosure        `tct_rule.tail_enclosure` + its independent crosscheck   (Campaign B, reviewed x2)
    adopted-state composition     `tail_forecast_r2.adopted_state/compose`  (Campaign B, reviewed x2)
    the predicate                 `k5b_check.k5b_literal`                   (frozen K5-B, ddd54dc4)

Independent second path, as the C1 gate requires: the Lemma Dv' constants are recomputed here from theorem AD section 4
directly (`_atom_constants_independent`), sharing no function with `deflated_consume`, and the TC-T enclosure is
recomputed by `tct_rule.tail_enclosure_crosscheck`, which shares no function with `tail_enclosure`. Both must agree
exactly, as rationals, on every cell and every m.

    python3 -B c1_forecast.py --registry DIR/REGISTRY_C1.json --records DIR --measurements DIR
                              --adopted-inputs FILE --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = REPO / "level4/closure_proofs"
B_NS = CP / "p5y_k5_m5_tail_closure"
AD_NS = CP / "p5y_k5_perron_deflated_resolvent"
GATE = NS / "config/FEASIBILITY_GATES_C1.json"
GATE_SHA = "927ecfc7597c6d75c485117177b1b0d0a87729aeb6f5e469813905ed242ceb98"
TAIL = (305, 306, 307, 308, 309)
MS = ("1", "2", "3", "5")
DEGRADE = F(5, 4)                                   # the frozen DEGRADED scenario factor
K1_BOUND = F(7978846, 10 ** 7)                      # whole-line E|He_1(Y)|, as the frozen consumer uses
K2_BOUND = F(9678830, 10 ** 7)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_module(path: Path, name: str, pin: str | None = None):
    raw = path.read_bytes()
    if pin is not None and sha(raw) != pin:
        raise SystemExit(f"{path} does not match its pin")
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    return mod


def _atom_constants_independent(Abar: F, tau: F, C: F, Dlo: F, D1: F, D2: F) -> dict:
    """Lemma Dv' re-derived here from THEOREM_AD.md section 4, sharing no function with `deflated_consume`:
    A_j = Abar_eff * (tame factor) with Abar_eff = min(Abar, tau/Dlo), d1 = D1/Dlo, d2 = D2/Dlo,
        A0 = Abar_eff,  A1 = Abar_eff (k1 C + d1),
        A2 = Abar_eff (2 k1^2 C^2 + k2 C + 2 k1 C d1 + 2 d1^2 + d2)."""
    if not (Dlo > 0 and tau >= 1 and C >= tau and Abar >= 1):
        raise SystemExit("operator constants violate tau >= 1, C >= tau, Dlo > 0, Abar >= 1")
    eff = Abar if Abar < tau / Dlo else tau / Dlo
    d1, d2 = D1 / Dlo, D2 / Dlo
    return {"A0": eff,
            "A1": eff * (K1_BOUND * C + d1),
            "A2": eff * (2 * K1_BOUND ** 2 * C ** 2 + K2_BOUND * C + 2 * K1_BOUND * C * d1 + 2 * d1 ** 2 + d2)}


def classify(gate: dict, certified_closed: list, degraded_closed: list, margins: dict,
             material: bool) -> str:
    """The frozen C1 classes, applied mechanically."""
    n_c, n_d = len(certified_closed), len(degraded_closed)
    beyond_305 = [k for k in certified_closed if k != 305]
    if n_c == 5 and n_d == 5 and all(margins[k] >= F(11, 10) for k in certified_closed):
        return "STRONG"
    if n_c >= 2 and beyond_305 and material:
        return "USEFUL"
    if n_c >= 1 or material:
        return "MARGINAL"
    return "INFEASIBLE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True)
    ap.add_argument("--records", required=True)
    ap.add_argument("--measurements", required=True)
    ap.add_argument("--adopted-inputs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    gate_raw = GATE.read_bytes()
    if sha(gate_raw) != GATE_SHA:
        raise SystemExit("the C1 feasibility gate is not the frozen one")
    gate = json.loads(gate_raw)

    FC = load_module(B_NS / "code/tail_forecast_r2.py", "b_tail_forecast_r2")
    T = sys.modules["tct_rule"] if "tct_rule" in sys.modules else load_module(B_NS / "code/tct_rule.py", "tct_rule")
    DC = load_module(AD_NS / "code/deflated_consume.py", "ad_deflated_consume",
                     "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72")

    reg_raw = Path(a.registry).read_bytes()
    reg = json.loads(reg_raw)
    if reg.get("rule") != "r2" or reg.get("operator_only") is not True:
        raise SystemExit("the C1 registry must be an operator-only r2 registry")
    if not reg.get("certified"):
        raise SystemExit("the C1 registry is not certified on every tail cell")
    blocks = {b["cell"]: b for b in reg["blocks"]}
    if sorted(blocks) != list(TAIL):
        raise SystemExit("the C1 registry does not cover exactly the frozen tail universe")

    st = FC.adopted_state(Path(a.records))
    meas, aux = {}, {}
    adopted = json.loads(Path(a.adopted_inputs).read_bytes())
    for k in TAIL:
        d = json.loads((Path(a.measurements) / f"TCT_INPUTS_{k}.json").read_bytes())
        if d["cell"] != k or not d["identity_gate"]["identical"] or d["order3_fields_present"]:
            raise SystemExit(f"measurement {k} is not a gated order-3-free replay")
        rec = st["records"][k]
        if d["k1_record_sha256"] != st["hashes"][str(k)]:
            raise SystemExit(f"measurement {k} is not bound to the adopted K1 record")
        d["C_upper"] = str(FC.rat(rec["C_upper"]))
        g = T.derived_identity_gate(st["R"], d, rec)
        if not g["pass"]:
            raise SystemExit(f"derived identity gate failed at cell {k}")
        meas[k], aux[k] = d, rec["auxiliary_evidence"]
        if adopted["cells"][str(k)]["record_sha256"] != st["hashes"][str(k)]:
            raise SystemExit(f"adopted extract {k} is not bound to the adopted K1 record")

    # --- baseline: the adopted post-Campaign-A state with no tail route
    sealed = json.loads(FC.pinned("tc_consumption"))["consumptions"]
    base = {}
    for m in MS:
        _, _, passed, _ = FC.compose(st, m, None)
        base[m] = passed
        if FC.ranges(passed) != sealed[m]["pass_ranges"]:
            raise SystemExit(f"replay gate: pass ranges differ for m={m}")

    # --- the C1 atom constants, two independent derivations
    consts, xchk = {}, []
    for k in TAIL:
        b = blocks[k]
        args = tuple(F(b[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2"))
        A_frozen = DC.atom_constants_r2(*args)
        A_mine = _atom_constants_independent(*args)
        if {j: A_frozen[j] for j in "A0 A1 A2".split()} != A_mine:
            raise SystemExit(f"atom-constant crosscheck disagrees at cell {k}")
        xchk.append(k)
        kn = {i: F(meas[k]["norms"]["k"][i]) for i in range(5)}
        generic = T.atom_constants_generic(F(meas[k]["C_upper"]), kn[1], kn[2])
        consts[k] = {"generic": generic, "c1": A_frozen}

    out = {"schema": "rebaseguard.p5y.k5.tail-operator-registry.forecast.v1",
           "gate_sha256": sha(gate_raw), "gate_frozen_before_forecast": True,
           "registry_sha256": sha(reg_raw), "registry_cpu_seconds": reg["cpu_seconds_total"],
           "atom_constant_crosscheck_cells": xchk,
           "replay_gate": "PASS (adopted post-Campaign-A state reproduces the sealed consumption pass ranges)",
           "scenarios": {}}

    need = {str(k): F(str(gate["baseline"]["required"][str(k)])) for k in TAIL}
    for sname, factor in (("CERTIFIED", F(1)), ("DEGRADED", DEGRADE)):
        tail = {m: {} for m in MS}
        detail = {}
        for k in TAIL:
            A = {j: consts[k]["c1"][j] * factor for j in ("A0", "A1", "A2")}
            obj = None
            for m in MS:
                lo, hi, obj = T.tail_enclosure(st["R"], meas[k], aux[k], A, int(m), None)
                if (lo, hi) != T.tail_enclosure_crosscheck(meas[k], aux[k], A, int(m), None):
                    raise SystemExit(f"TC-T crosscheck disagrees at cell {k} m {m}")
                tail[m][k] = (lo, hi)
            detail[k] = {"A": {j: float(A[j]) for j in A},
                         "per_r_rad": {str(r): float(obj[r]["rad"]) for r in range(5)}}
        per_m, margins, closed = {}, {}, []
        for m in MS:
            _, rows, passed, audit = FC.compose(st, m, tail)
            per_m[m] = {"pass_ranges": FC.ranges(passed),
                        "open_ranges": FC.ranges(sorted(set(range(310)) - set(passed))),
                        "newly_passing": sorted(set(passed) - set(base[m])),
                        "regressed": sorted(set(base[m]) - set(passed)),
                        "tail": {str(k): ({"H_tail_exact": audit[str(k)]["H_tail"],
                                           "M_after_exact": audit[str(k)]["M"],
                                           "Gamma_exact": str(rows[k]["Gamma"])} if m == "5" else {})
                                 | {"mag_tail": float(max(abs(F(audit[str(k)]["H_tail"][0])),
                                                          abs(F(audit[str(k)]["H_tail"][1])))),
                                    "M_after": float(F(audit[str(k)]["M"])), "empty": audit[str(k)]["empty"],
                                    "pass": bool(k in passed), "via": rows[k]["via"],
                                    "Gamma": float(rows[k]["Gamma"])} for k in TAIL}}
        for k in TAIL:
            M = F(per_m["5"]["tail"][str(k)]["M_after_exact"])
            margins[k] = need[str(k)] / M if M else F(0)
            if per_m["5"]["tail"][str(k)]["pass"]:
                closed.append(k)
        out["scenarios"][sname] = {"closed_m5": closed, "margins": {str(k): float(v) for k, v in margins.items()},
                                   "per_m": per_m, "detail": {str(k): detail[k] for k in TAIL}}
        out["scenarios"][sname]["_margins_exact"] = {str(k): str(v) for k, v in margins.items()}

    # --- material-improvement test, exactly as the gate states it.
    # The gate's quantity is the UNIFORM ATOM-CONSTANT reduction factor still required, i.e. the bisected uniform
    # scale on (A0, A1, A2) at which the frozen direct test starts to pass - the same construction that produced the
    # baseline 2.252903 from Campaign B. Review C1-prefreeze note 1: an earlier version of this block used
    # 1/margin = M_after/M_needed, a MAGNITUDE ratio, and compared it against an atom-constant baseline. The two are
    # different quantities and the mixed comparison overstated the fall as 16.1 % where it is 6.72 %.
    cert = out["scenarios"]["CERTIFIED"]
    still_open = [k for k in TAIL if k not in cert["closed_m5"]]
    base_worst = F(str(gate["baseline"]["uniform_atom_constant_reduction_still_needed"]["309"]))

    def uniform_reduction_still_needed(k: int) -> F:
        """The factor by which A0, A1, A2 must fall UNIFORMLY for the frozen direct test to pass cell k, under C1's
        certified constants. Exact bisection; 1 when the cell already passes."""
        A = consts[k]["c1"]
        ad = adopted["cells"][str(k)]["m"]["5"]
        H = (F(ad["R2_interval"]["lo"]), F(ad["R2_interval"]["hi"]))
        M0 = F(ad["M_R2"])
        cov = {c["index"]: c for c in st["cover"]}[k]
        x_hi, rho, e0 = (st["KM"].rat(cov[t]) for t in ("right", "rho", "e0"))
        g_hi = F(ad["R_interval"]["hi"]) - e0 * F(ad["D_interval"]["lo"])

        def passes(scale: F) -> bool:
            lo, hi, _ = T.tail_enclosure(st["R"], meas[k], aux[k], {j: A[j] * scale for j in A}, 5, None)
            a_, b_ = max(H[0], lo), min(H[1], hi)
            M = M0 if a_ > b_ else min(M0, max(abs(a_), abs(b_)))
            return g_hi + rho * x_hi * M < 0

        if passes(F(1)):
            return F(1)
        lo_s, hi_s = F(1, 1000), F(1)
        if not passes(lo_s):
            return None
        for _ in range(50):
            mid = (lo_s + hi_s) / 2
            if passes(mid):
                lo_s = mid
            else:
                hi_s = mid
        return 1 / lo_s

    per_cell_reduction = {k: uniform_reduction_still_needed(k) for k in TAIL}
    worst_now = None
    if still_open:
        worst_now = max(per_cell_reduction[k] for k in still_open)
    out["material_improvement"] = {
        "baseline_worst_required_uniform_reduction": float(base_worst),
        "still_open": still_open,
        "worst_required_uniform_reduction_now": (float(worst_now) if worst_now is not None else 0.0),
        "relative_fall": (float(1 - worst_now / base_worst) if worst_now is not None else 1.0),
        "threshold": 0.10,
        "quantity": "uniform atom-constant reduction factor still required (bisected uniform scale on A0, A1, A2), "
                    "the same construction that produced the gate's baseline",
        "per_cell_uniform_reduction_still_needed": {str(k): (float(v) if v is not None else None)
                                                    for k, v in per_cell_reduction.items()},
        "pass": bool(worst_now is None or (1 - worst_now / base_worst) >= F(1, 10))}

    cls = classify(gate, cert["closed_m5"], out["scenarios"]["DEGRADED"]["closed_m5"],
                   {k: F(cert["_margins_exact"][str(k)]) for k in TAIL},
                   out["material_improvement"]["pass"])
    out["C1_CLASS"] = cls
    out["selection_verdict"] = "EXECUTE" if cls in ("STRONG", "USEFUL") else "STOP_AND_WRITE_COSTED_C2_PLAN"
    out["constants"] = {str(k): {"generic_LemmaG": {j: float(consts[k]["generic"][j]) for j in ("A0", "A1", "A2")},
                                 "c1_LemmaDv_prime": {j: float(consts[k]["c1"][j]) for j in ("A0", "A1", "A2")},
                                 "reduction": {j: float(consts[k]["generic"][j] / consts[k]["c1"][j])
                                               for j in ("A0", "A1", "A2")},
                                 "operator": {x: float(F(blocks[k][x])) for x in
                                              ("Abar", "tau", "C_T", "D_lo", "D1", "D2")}} for k in TAIL}
    data = json.dumps(out, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({"C1_CLASS": cls, "verdict": out["selection_verdict"],
                      "CERTIFIED_closed": cert["closed_m5"],
                      "DEGRADED_closed": out["scenarios"]["DEGRADED"]["closed_m5"],
                      "margins": cert["margins"],
                      "material_improvement": out["material_improvement"],
                      "A0_reduction": {k: round(v["reduction"]["A0"], 3) for k, v in out["constants"].items()},
                      "sha256": sha(data)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
