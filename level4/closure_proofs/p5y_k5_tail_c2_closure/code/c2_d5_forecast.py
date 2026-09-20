"""Campaign C2, Phase D5: the deterministic forecast. Combines every valid certified atom-constant supply under the
PRE-REGISTERED componentwise-minimum rule, consumes the result through theorem TC-T and the frozen K5-B, and
classifies it under the C2 gate frozen at `87309610` before this file could produce a number.

Supplies (all three upper-bound the same three quantities, so their componentwise minimum is itself a valid bound):
    G    Lemma G generic, from the frozen K1 block bound C_upper
    C1   Lemma Dv' from the adopted-machinery C1 tail registry (one block per cell)
    C2   Lemma Dv' from C2's refined sub-block registry (sub-blocks no wider than 1/100)

Provenance is recorded per cell and per field. Two independent paths are required by the gate and are used here:
`_atom_independent` re-derives Lemma Dv' from THEOREM_AD section 4 sharing no function with `deflated_consume`, and
`tct_rule.tail_enclosure_crosscheck` re-derives the enclosure sharing no function with `tail_enclosure`.

    python3 -B c2_d5_forecast.py --registry DIR/REGISTRY_C2.json --records DIR --measurements DIR
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
C1_NS = CP / "p5y_k5_tail_operator_registry"
AD_NS = CP / "p5y_k5_perron_deflated_resolvent"
GATE = NS / "config/FEASIBILITY_GATES_C2.json"
GATE_SHA = "098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f"
C1_REG_SHA = "87bb1cfacb09c2a144cab0270427d91980ea742b36fd80f8963265a22d2eebb3"
DC_SHA = "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72"
TAIL = (305, 306, 307, 308, 309)
MS = ("1", "2", "3", "5")
K1_BOUND = F(7978846, 10 ** 7)
K2_BOUND = F(9678830, 10 ** 7)
FIELDS = ("A0", "A1", "A2")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load(path: Path, name: str, pin: str | None = None):
    raw = path.read_bytes()
    if pin is not None and sha(raw) != pin:
        raise SystemExit(f"{path} does not match its pin {pin[:12]}")
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    return mod


def _atom_independent(Abar, tau, C, Dlo, D1, D2) -> dict:
    """Lemma Dv' re-derived from THEOREM_AD section 4; shares no function with deflated_consume."""
    if not (Dlo > 0 and tau >= 1 and C >= tau and Abar >= 1):
        raise SystemExit("operator constants violate tau >= 1, C >= tau, Dlo > 0, Abar >= 1")
    eff = Abar if Abar < tau / Dlo else tau / Dlo
    d1, d2 = D1 / Dlo, D2 / Dlo
    return {"A0": eff, "A1": eff * (K1_BOUND * C + d1),
            "A2": eff * (2 * K1_BOUND ** 2 * C ** 2 + K2_BOUND * C + 2 * K1_BOUND * C * d1 + 2 * d1 ** 2 + d2)}


def combine(supplies: dict) -> tuple:
    """The gate's D4 rule: A_j := min over valid supplies, componentwise, with provenance per field."""
    A, prov = {}, {}
    for j in FIELDS:
        name, val = min(((n, s[j]) for n, s in supplies.items()), key=lambda nv: nv[1])
        A[j], prov[j] = val, name
    return A, prov


def direct(T, R, meas, aux, A, ad, cov, KM):
    lo, hi, obj = T.tail_enclosure(R, meas, aux, A, 5, None)
    if (lo, hi) != T.tail_enclosure_crosscheck(meas, aux, A, 5, None):
        raise SystemExit("theorem TC-T crosscheck disagrees")
    H = (F(ad["R2_interval"]["lo"]), F(ad["R2_interval"]["hi"]))
    M0 = F(ad["M_R2"])
    a, b = max(H[0], lo), min(H[1], hi)
    M = M0 if a > b else min(M0, max(abs(a), abs(b)))
    e0, rho, x_hi = (KM.rat(cov[t]) for t in ("e0", "rho", "right"))
    Gam = (F(ad["R_interval"]["hi"]) - e0 * F(ad["D_interval"]["lo"])) + rho * x_hi * M
    return {"lo": lo, "hi": hi, "mag": max(abs(lo), abs(hi)), "M": M, "Gamma": Gam, "pass": Gam < 0, "obj": obj}


def requirement(T, R, meas, aux, A, ad, cov, KM) -> F:
    """The uniform atom-constant reduction factor still required; 1 when the cell already passes."""
    if direct(T, R, meas, aux, A, ad, cov, KM)["pass"]:
        return F(1)
    lo_s, hi_s = F(1, 1000), F(1)
    if not direct(T, R, meas, aux, {j: A[j] * lo_s for j in A}, ad, cov, KM)["pass"]:
        return None
    for _ in range(50):
        mid = (lo_s + hi_s) / 2
        if direct(T, R, meas, aux, {j: A[j] * mid for j in A}, ad, cov, KM)["pass"]:
            lo_s = mid
        else:
            hi_s = mid
    return 1 / lo_s


def classify(closed: list, materially_tightened: dict, still_open: list) -> str:
    """The frozen C2 D-stage classes, applied mechanically.

    One case the frozen gate does not cover: it defines D_INSUFFICIENT as "closes no cell, AND no still-open cell is
    materially tightened", so a run that closes no cell while tightening SOME of them matches none of the four
    classes. This implementation resolves that gap to D_INSUFFICIENT, because the gate reserves every class above it
    for a run that closes at least one cell. The case is unreachable in C2 (which closes two), the resolution is
    recorded here rather than by amending the frozen gate, and a successor gate should close the hole explicitly.
    An earlier version carried a redundant trailing branch that duplicated the D_PARTIAL test and masked a mutation
    of it (adversarial suite M23); the redundancy is removed so that every branch is load-bearing."""
    n = len(closed)
    if n == 5:
        return "D_STRONG"
    if n >= 2 and all(materially_tightened[k] for k in still_open):
        return "D_USEFUL"
    if n >= 1:
        return "D_PARTIAL"
    return "D_INSUFFICIENT"


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
        raise SystemExit("the C2 feasibility gate is not the frozen one")
    gate = json.loads(gate_raw)
    base_gap = {k: F(str(gate["baseline"]["gap"][str(k)])) for k in TAIL}
    thresh = F(str(gate["material_tightening_test"]["threshold"]))

    FC = load(B_NS / "code/tail_forecast_r2.py", "b_tail_forecast_r2")
    T = sys.modules["tct_rule"]
    DC = load(AD_NS / "code/deflated_consume.py", "ad_dc", DC_SHA)
    KM = FC.adopted_state.__globals__  # not used; the loader is reached through st below

    c2_raw = Path(a.registry).read_bytes()
    c2 = json.loads(c2_raw)
    if c2.get("rule") != "r2" or c2.get("operator_only") is not True or not c2.get("certified"):
        raise SystemExit("the C2 refined registry is not a certified operator-only r2 registry")
    c2b = {b["cell"]: b for b in c2["blocks"]}
    if sorted(c2b) != list(TAIL):
        raise SystemExit("the C2 registry does not cover exactly the frozen tail universe")
    c1_raw = (C1_NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes()
    if sha(c1_raw) != C1_REG_SHA:
        raise SystemExit("the C1 registry does not match its pin")
    c1b = {b["cell"]: b for b in json.loads(c1_raw)["blocks"]}

    st = FC.adopted_state(Path(a.records))
    R, KMod = st["R"], st["KM"]
    adopted = json.loads(Path(a.adopted_inputs).read_bytes())
    cover = {c["index"]: c for c in st["cover"]}
    meas, aux = {}, {}
    for k in TAIL:
        d = json.loads((Path(a.measurements) / f"TCT_INPUTS_{k}.json").read_bytes())
        rec = st["records"][k]
        if d["cell"] != k or not d["identity_gate"]["identical"] or d["order3_fields_present"]:
            raise SystemExit(f"measurement {k} is not a gated order-3-free replay")
        if d["k1_record_sha256"] != st["hashes"][str(k)]:
            raise SystemExit(f"measurement {k} is not bound to the adopted K1 record")
        d["C_upper"] = str(FC.rat(rec["C_upper"]))
        if not T.derived_identity_gate(R, d, rec)["pass"]:
            raise SystemExit(f"derived identity gate failed at cell {k}")
        meas[k], aux[k] = d, rec["auxiliary_evidence"]

    sealed = json.loads(FC.pinned("tc_consumption"))["consumptions"]
    base = {}
    for m in MS:
        _, _, passed, _ = FC.compose(st, m, None)
        base[m] = passed
        if FC.ranges(passed) != sealed[m]["pass_ranges"]:
            raise SystemExit(f"replay gate: pass ranges differ for m={m}")

    out = {"schema": "rebaseguard.p5y.k5.tail-c2.d5-forecast.v1", "gate_sha256": sha(gate_raw),
           "gate_frozen_before_forecast": True, "registry_c2_sha256": sha(c2_raw),
           "registry_c1_sha256": sha(c1_raw), "registry_c2_cpu_seconds": c2["cpu_seconds_total"],
           "combination_rule": gate["D4_combination_rule"]["rule"],
           "replay_gate": "PASS (adopted post-Campaign-A state reproduces the sealed consumption pass ranges)",
           "cells": {}, "supplies": {}}

    tail_enc, closed, tight, still_open = {m: {} for m in MS}, [], {}, []
    for k in TAIL:
        kn = {i: F(meas[k]["norms"]["k"][i]) for i in range(5)}
        sup = {}
        sup["G"] = T.atom_constants_generic(F(meas[k]["C_upper"]), kn[1], kn[2])
        for name, blk in (("C1", c1b[k]), ("C2", c2b[k])):
            args = tuple(F(blk[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2"))
            frozen = DC.atom_constants_r2(*args)
            if {j: frozen[j] for j in FIELDS} != _atom_independent(*args):
                raise SystemExit(f"atom-constant crosscheck disagrees for supply {name} at cell {k}")
            sup[name] = frozen
        A, prov = combine(sup)
        res = direct(T, R, meas[k], aux[k], A, adopted["cells"][str(k)]["m"]["5"], cover[k], KMod)
        req = requirement(T, R, meas[k], aux[k], A, adopted["cells"][str(k)]["m"]["5"], cover[k], KMod)
        gap = (req - 1) if req is not None else None
        mt = bool(gap is not None and base_gap[k] > 0 and gap <= (1 - thresh) * base_gap[k])
        if res["pass"]:
            closed.append(k)
        else:
            still_open.append(k)
            tight[k] = mt
        for m in MS:
            lo, hi, _ = T.tail_enclosure(R, meas[k], aux[k], A, int(m), None)
            if (lo, hi) != T.tail_enclosure_crosscheck(meas[k], aux[k], A, int(m), None):
                raise SystemExit(f"crosscheck disagrees at cell {k} m {m}")
            tail_enc[m][k] = (lo, hi)
        out["supplies"][str(k)] = {n: {j: float(v[j]) for j in FIELDS} for n, v in sup.items()}
        out["cells"][str(k)] = {
            "A": {j: float(A[j]) for j in FIELDS}, "A_exact": {j: str(A[j]) for j in FIELDS},
            "provenance": prov,
            "magnitude": float(res["mag"]), "M_after": float(res["M"]), "Gamma": float(res["Gamma"]),
            "Gamma_exact": str(res["Gamma"]), "M_after_exact": str(res["M"]),
            "H_exact": [str(res["lo"]), str(res["hi"])], "pass": bool(res["pass"]),
            "required_uniform_atom_constant_reduction": (float(req) if req is not None else None),
            "gap_above_1": (float(gap) if gap is not None else None),
            "baseline_gap": float(base_gap[k]),
            "materially_tightened": mt,
            "gap_fall_fraction": (float(1 - gap / base_gap[k]) if (gap is not None and base_gap[k] > 0) else None)}

    for m in MS:
        _, rows, passed, audit = FC.compose(st, m, tail_enc)
        lost = sorted(set(base[m]) - set(passed))
        if lost:
            raise SystemExit(f"a previously passing cell regressed for m={m}: {lost[:5]}")
        out.setdefault("consumptions", {})[m] = {
            "pass_ranges": FC.ranges(passed), "open_ranges": FC.ranges(sorted(set(range(310)) - set(passed))),
            "newly_passing": sorted(set(passed) - set(base[m])), "regressed": lost,
            "tail_via": {str(k): rows[k]["via"] for k in TAIL}}

    cls = classify(closed, tight, still_open)
    out["D_STAGE_CLASS"] = cls
    out["closed"] = closed
    out["still_open"] = still_open
    out["materially_tightened"] = {str(k): tight[k] for k in still_open}
    out["decision"] = gate["D_stage_decision_rule"][cls]
    data = json.dumps(out, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({"D_STAGE_CLASS": cls, "closed": closed, "still_open": still_open,
                      "materially_tightened": out["materially_tightened"],
                      "per_cell": {k: {"mag": round(v["magnitude"], 6), "req": v["required_uniform_atom_constant_reduction"],
                                       "gap_fall": v["gap_fall_fraction"], "prov": v["provenance"]}
                                   for k, v in out["cells"].items()},
                      "sha256": sha(data)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
