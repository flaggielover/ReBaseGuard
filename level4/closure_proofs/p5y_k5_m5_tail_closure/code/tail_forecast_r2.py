"""Campaign B, Phase C: the measurement-anchored tail forecast, and the frozen-K5-B evaluation of every candidate
tail route. Runs where the adopted K1 records live. Exact Fractions; no model quantity is evaluated here.

State: the ADOPTED post-Campaign-A state, recomposed exactly as the adopted consumer does (pinned E6 adapter, frozen
loader, frozen K5-B, adopted Perron consumer with certified registry r1 on [0, 148], adopted T-EXT C1/C2 channel,
and the SEALED Campaign-A theorem-TC enclosures on cells 11-44). Replay gate: with no tail route applied, the pass
and open ranges must equal the sealed Campaign-A consumption (1fa8d8de...) exactly.

Routes scored on top of that state at cells 305-309, ALL of them through the same premise supply
(`tct_rule.tail_enclosure`, Lemma G constants and the (P3') sigma3/sigma4; review r1 note N4: (P3') is a statement
about the source and is independent of the choice of Ghat, so every route is entitled to it):
  TCT0    theorem TC-T with the ZERO order-3 candidate (zero new real scientific addresses; nothing is estimated -
          this is a derivation, not a forecast)
  T2_AUDIT        route T2 at the frozen route comparison's own NOMINAL inputs (sG = 10, sH = 5, sD = 2, sF = 1,
                  |Ghat(a)| = sG, delta_G = 1e-3). NOT a certified bound: sF = 1 is below the measured candidate
                  supremum for two objects (review r1 note N8). It reconstructs what the comparison forecast.
  T2_AUDIT_MEAS   the same order-3 inputs on the measured adopted candidate suprema
  T2_EVIDENCE     route T2 with the order-3 scale estimated from the ADOPTED Campaign-A records (the worst per-r
                  sup.G/sup.H ratio applied to the measured tail sup.H; |Ghat(a)| = 0.681 sup.G; delta_G the worst
                  adopted per-r value)
CONSERVATIVE multiplies every NOT-YET-MEASURED input of the route by 4 in the unfavourable direction, as the frozen
gates define it - for T2_AUDIT that includes sF, sD and sH, which are assumed rather than measured there (note N3).

    python3 -B tail_forecast_r2.py --records DIR --measurements DIR --adopted-inputs FILE --out OUT.json
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
CP = "level4/closure_proofs/"
sys.path.insert(0, str(HERE.parent))
import tct_rule as T                                                   # noqa: E402

A_NS = CP + "p5y_k5_lower_front_order3"
PINS = {
    "adapter": (CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py",
                "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"),
    "deflated": (CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
                 "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72"),
    "text_consume": (CP + "p5y_k5_remaining_cell_closure/transport_extension/code/text_consume.py",
                     "657458ade03c4283ae6d5bd97e5567603380bf0e6281d8483f9c1fd45a62d0ea"),
    "registry": (CP + "p5y_k5_perron_deflated_resolvent/evidence/registry_r1/REGISTRY.json",
                 "1b7f5da743a2ce0d7f557c2dae054ab358a9175212eaa1fa29dea63a25780cb5"),
    "text_result": (CP + "p5y_k5_remaining_cell_closure/transport_extension/evidence/qualification_r1/TEXT_RESULT.json",
                    "cb97cabcc3b5848665584e33ad4207c6d36ce835729725265d585dc8f3ee4f87"),
    "slot1": (CP + "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json",
              "cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae"),
    "tc_consumption": (A_NS + "/evidence/tc_r1/TC_CONSUMPTION.json",
                       "1fa8d8dee78483c83d54bd90dba86a9316fb5c67c4acd43781a05103ab111f51"),
}
MS = ("1", "2", "3", "5")
TAIL = (305, 306, 307, 308, 309)
A_CELLS = list(range(11, 45))
ADOPTED_DOMAIN = (0, 148)
TEXT_CHANNEL = tuple(range(1, 41))
TEXT_CURVATURE = tuple(range(0, 41))
SCEN = {"NOMINAL": F(1), "CONSERVATIVE": F(4)}
AUDIT_SUP = {"F": F(1), "D": F(2), "H": F(5)}                 # the route comparison's own assumed suprema
AUDIT_SG = F(10)
AUDIT_DG = F(1, 1000)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pinned(key: str) -> bytes:
    rel, pin = PINS[key]
    raw = (REPO / rel).read_bytes()
    if sha(raw) != pin:
        raise SystemExit(f"{rel} does not match its pin")
    return raw


def module(key: str, name: str):
    raw = pinned(key)
    mod = types.ModuleType(name)
    mod.__file__ = str(REPO / PINS[key][0])
    exec(compile(raw, mod.__file__, "exec"), mod.__dict__)
    return mod


def ranges(xs):
    xs, out = sorted(xs), []
    for x in xs:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def rat(p) -> F:
    return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


# ------------------------------------------------------------------ the adopted post-Campaign-A state
def adopted_state(records_dir: Path):
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    X = T.load_frozen("tc_crosscheck", T.FROZEN["tc_crosscheck"][1])
    A = module("adapter", "fc_adapter")
    DC = module("deflated", "fc_deflated")
    TCm = module("text_consume", "fc_text")
    registry = json.loads(pinned("registry"))
    text = json.loads(pinned("text_result"))
    per = json.loads(pinned("slot1"))["scientific"]["per_m"]
    lam, m2 = TCm.text_objects(text, {m: per[m]["L1"] for m in MS})
    comp = A.frozen_components(REPO)
    KM, KB = comp["loader"], comp["theorem"]
    A.bound_file(REPO / A.CELLS_JSON, A.CELLS_SHA256, "cells.json")
    manifest = json.loads(A.bound_file(REPO / A.MANIFEST, A.MANIFEST_SHA256, "record manifest"))
    cover = KM.load_cells(REPO / A.CELLS_JSON, A.DETECTOR)
    if [c["index"] for c in cover] != list(range(310)):
        raise SystemExit("cover universe mismatch")
    records, hashes = A.read_records(KM, records_dir, cover, manifest)
    a_cells = {k: json.loads((REPO / f"{A_NS}/evidence/tc_r1/cells/TC_CELL_{k}.json").read_bytes()) for k in A_CELLS}
    return {"R": R, "X": X, "A": A, "DC": DC, "KM": KM, "KB": KB, "registry": registry, "cover": cover,
            "records": records, "hashes": hashes, "L1": {m: F(per[m]["L1"]) for m in MS}, "lam": lam, "m2": m2,
            "a_cells": a_cells}


def compose(st, m: str, tail: dict | None):
    """Adopted composition for one m, then (optionally) the tail enclosures."""
    A, DC, KM, KB, R, X = st["A"], st["DC"], st["KM"], st["KB"], st["R"], st["X"]
    cover, records, registry = st["cover"], st["records"], st["registry"]
    cells = A.cells_for_m(KM, cover, records, m, st["L1"][m])
    DC.apply_deflation(cells, records, registry, m, cover, ADOPTED_DOMAIN)
    for k in TEXT_CHANNEL:
        cells[k]["L"] = st["lam"][m][k]
    for k in TEXT_CURVATURE:
        b = st["m2"][m][k]
        lo, hi = cells[k]["H"]
        cells[k]["H"] = (max(lo, -b), min(hi, b))
        cells[k]["M"] = min(cells[k]["M"], b)
    for k in A_CELLS:                                   # the SEALED Campaign-A theorem-TC enclosures
        cons = DC.block_for(registry, cells[k]["x_lo"], cells[k]["x_hi"])
        Ak = DC.atom_constants_r2(cons["Abar"], cons["tau"], cons["C"], cons["Dlo"], cons["D1"], cons["D2"])
        lo, hi = R.cell_enclosure(st["a_cells"][k], Ak, int(m))
        if (lo, hi) != X.enclosure(st["a_cells"][k], Ak, int(m)):
            raise SystemExit(f"Campaign-A crosscheck disagrees at {k} m {m}")
        a, b = max(cells[k]["H"][0], lo), min(cells[k]["H"][1], hi)
        if a > b:
            raise SystemExit(f"empty Campaign-A intersection at {k} m {m}")
        cells[k]["H"] = (a, b)
        cells[k]["M"] = min(cells[k]["M"], max(abs(a), abs(b)))
    audit = {}
    if tail:
        for k, (lo, hi) in tail[m].items():
            a, b = max(cells[k]["H"][0], lo), min(cells[k]["H"][1], hi)
            empty = a > b
            if not empty:
                cells[k]["H"] = (a, b)
                cells[k]["M"] = min(cells[k]["M"], max(abs(a), abs(b)))
            audit[str(k)] = {"H_tail": [str(lo), str(hi)], "empty": bool(empty), "M": str(cells[k]["M"])}
    rows = KB.k5b_literal(cells)
    passed = [cover[i]["index"] for i, r in enumerate(rows) if r["pass"] is True]
    return cells, rows, passed, audit


# ------------------------------------------------------------------ the routes
def order3_inputs(mode: str, meas_r: dict, r: int, scen: F, lf: dict) -> dict | None:
    """The order-3 supply of one route for one object. None means the zero candidate (P2')."""
    if mode == "TCT0":
        return None
    sH_meas = F(meas_r["sup"]["H"])
    if mode == "T2_AUDIT":                                   # assumed suprema too: all six inputs are unmeasured
        q = {"sup_F": AUDIT_SUP["F"] * scen, "sup_D": AUDIT_SUP["D"] * scen, "sup_H": AUDIT_SUP["H"] * scen,
             "sup_G": AUDIT_SG * scen, "abs_G_at_a": AUDIT_SG * scen, "delta_G": AUDIT_DG * scen}
    elif mode == "T2_AUDIT_MEAS":                            # measured suprema; only the order-3 inputs are scaled
        q = {"sup_G": AUDIT_SG * scen, "abs_G_at_a": AUDIT_SG * scen, "delta_G": AUDIT_DG * scen}
    elif mode == "T2_EVIDENCE":
        sG = lf[r]["gh_max"] * sH_meas * scen
        q = {"sup_G": sG, "abs_G_at_a": lf[r]["ag_max"] * sG, "delta_G": lf[r]["dg_max"] * scen}
    else:
        raise SystemExit(f"unknown mode {mode}")
    return {key: str(v) for key, v in q.items()}


def tail_enclosures(st, meas: dict, aux: dict, mode: str, scen: F, lf: dict):
    """The tail interval per (m, cell) for one route and scenario, through the single premise supply."""
    R = st["R"]
    out = {m: {} for m in MS}
    detail = {}
    for k in TAIL:
        mk, ak = meas[k], aux[k]
        kn = {i: F(mk["norms"]["k"][i]) for i in range(5)}
        A = T.atom_constants_generic(F(mk["C_upper"]), kn[1], kn[2])
        o3 = None
        if mode != "TCT0":
            o3 = {str(r): order3_inputs(mode, mk["r"][str(r)], r, scen, lf) for r in range(5)}
        obj = None
        for m in MS:
            lo, hi, obj = T.tail_enclosure(R, mk, ak, A, int(m), o3)
            if (lo, hi) != T.tail_enclosure_crosscheck(mk, ak, A, int(m), o3):
                raise SystemExit(f"{mode} crosscheck disagrees at cell {k} m {m}")
            out[m][k] = (lo, hi)
        detail[k] = {"A": {n: float(A[n]) for n in A},
                     "per_r": {str(r): {"sigma3": float(obj[r]["sigma3"]), "sigma4": float(obj[r]["sigma4"]),
                                        "order3_residual_bound": float(obj[r]["order3_residual_bound"]),
                                        "f_G_incl_eps_src3": float(obj[r]["f_G"]),
                                        "sup_G": float(obj[r]["sup_G"]),
                                        "abs_G_at_a": float(obj[r]["abs_G_at_a"]),
                                        "env4": float(obj[r]["env4"]), "rad": float(obj[r]["rad"]),
                                        "half": float(obj[r]["half"])} for r in range(5)}}
    return out, detail


def critical_ratio(st, meas: dict, aux: dict, lf: dict, k: int, m: str = "5"):
    """The largest sup.G / sup.H ratio (with |Ghat(a)| = 0.681 sup.G and the worst adopted delta_G) at which the
    frozen direct test still passes this cell, by exact bisection on the record's own R'' and M."""
    R = st["R"]
    mk, ak = meas[k], aux[k]
    kn = {i: F(mk["norms"]["k"][i]) for i in range(5)}
    A = T.atom_constants_generic(F(mk["C_upper"]), kn[1], kn[2])
    cov = {c["index"]: c for c in st["cover"]}[k]
    x_hi, rho, e0 = (st["KM"].rat(cov[t]) for t in ("right", "rho", "e0"))
    mm = st["records"][k]["m"][m]
    Rr = (F(mm["R_interval"]["lo"]), F(mm["R_interval"]["hi"]))
    Dd = (F(mm["D_interval"]["lo"]), F(mm["D_interval"]["hi"]))
    Hh = (F(mm["R2_interval"]["lo"]), F(mm["R2_interval"]["hi"]))
    M0 = F(mm["M_R2"])
    g_hi = Rr[1] - e0 * Dd[0]

    def ok(ratio: F) -> bool:
        o3 = {}
        for r in range(5):
            sG = ratio * F(mk["r"][str(r)]["sup"]["H"])
            o3[str(r)] = {"sup_G": str(sG), "abs_G_at_a": str(lf[r]["ag_max"] * sG),
                          "delta_G": str(lf[r]["dg_max"])}
        lo, hi, _ = T.tail_enclosure(R, mk, ak, A, int(m), o3)
        a, b = max(Hh[0], lo), min(Hh[1], hi)
        M = M0 if a > b else min(M0, max(abs(a), abs(b)))
        return g_hi + rho * x_hi * M < 0

    if not ok(F(0)):
        return None
    lo_r, hi_r = F(0), F(500)
    if ok(hi_r):
        return float("inf")
    for _ in range(50):
        mid = (lo_r + hi_r) / 2
        if ok(mid):
            lo_r = mid
        else:
            hi_r = mid
    return float(lo_r)


def atom_constant_requirement(st, meas: dict, aux: dict, k: int, m: str = "5") -> dict:
    """With Ghat := 0, the factor by which A0,A1,A2 (uniformly) and A0 alone must fall for the frozen direct test
    to pass this cell. Exact bisection."""
    R = st["R"]
    mk, ak = meas[k], aux[k]
    kn = {i: F(mk["norms"]["k"][i]) for i in range(5)}
    A = T.atom_constants_generic(F(mk["C_upper"]), kn[1], kn[2])
    cov = {c["index"]: c for c in st["cover"]}[k]
    x_hi, rho, e0 = (st["KM"].rat(cov[t]) for t in ("right", "rho", "e0"))
    mm = st["records"][k]["m"][m]
    Rr = (F(mm["R_interval"]["lo"]), F(mm["R_interval"]["hi"]))
    Dd = (F(mm["D_interval"]["lo"]), F(mm["D_interval"]["hi"]))
    Hh = (F(mm["R2_interval"]["lo"]), F(mm["R2_interval"]["hi"]))
    M0 = F(mm["M_R2"])
    g_hi = Rr[1] - e0 * Dd[0]

    def ok(all_s=F(1), a0_s=F(1)) -> bool:
        Ax = {"A0": A["A0"] * all_s * a0_s, "A1": A["A1"] * all_s, "A2": A["A2"] * all_s}
        lo, hi, _ = T.tail_enclosure(R, mk, ak, Ax, int(m), None)
        a, b = max(Hh[0], lo), min(Hh[1], hi)
        M = M0 if a > b else min(M0, max(abs(a), abs(b)))
        return g_hi + rho * x_hi * M < 0

    def bisect(which):
        lo_s, hi_s = F(1, 1000), F(1)
        if ok(**{which: hi_s}):
            return 1.0
        if not ok(**{which: lo_s}):
            return None
        for _ in range(40):
            mid = (lo_s + hi_s) / 2
            if ok(**{which: mid}):
                lo_s = mid
            else:
                hi_s = mid
        return float(1 / lo_s)

    return {"uniform_A_reduction_needed": bisect("all_s"), "A0_only_reduction_needed": bisect("a0_s"),
            "A0": float(A["A0"]), "A1": float(A["A1"]), "A2": float(A["A2"])}


def classify(closed_nominal: int, closed_conservative: int) -> str:
    """The frozen classes of config/FEASIBILITY_GATES_B.json, applied mechanically."""
    if closed_conservative == 5:
        return "STRONG"
    if closed_conservative >= 3 or closed_nominal == 5:
        return "USEFUL"
    if closed_nominal >= 1:
        return "MARGINAL"
    return "INFEASIBLE"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True)
    ap.add_argument("--measurements", required=True)
    ap.add_argument("--adopted-inputs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    st = adopted_state(Path(a.records))
    adopted_raw = Path(a.adopted_inputs).read_bytes()
    adopted = json.loads(adopted_raw)
    meas, aux, gates = {}, {}, {}
    for k in TAIL:
        raw = (Path(a.measurements) / f"TCT_INPUTS_{k}.json").read_bytes()
        d = json.loads(raw)
        if d["cell"] != k or not d["identity_gate"]["identical"] or d["order3_fields_present"]:
            raise SystemExit(f"measurement {k} is not a gated order-3-free replay")
        rec = st["records"][k]
        ad = adopted["cells"][str(k)]
        if d["k1_record_sha256"] != st["hashes"][str(k)] or ad["record_sha256"] != st["hashes"][str(k)]:
            raise SystemExit(f"measurement or adopted extract {k} is not bound to the adopted K1 record")
        # the committed extract must be byte-faithful to the record it claims to copy
        for fam in ("candidate_suprema", "midpoint_eps"):
            for key, v in ad["auxiliary_evidence"][fam].items():
                if rec["auxiliary_evidence"][fam][key] != v:
                    raise SystemExit(f"adopted extract {k}: {fam}[{key}] differs from the record")
        for key, v in ad["eps_cell_refined"].items():
            if rec["eps_cell_refined"][key] != v:
                raise SystemExit(f"adopted extract {k}: eps_cell_refined[{key}] differs from the record")
        for m in MS:
            for fld in ("R_interval", "D_interval", "R2_interval"):
                for t in ("lo", "hi"):
                    if rec["m"][m][fld][t] != ad["m"][m][fld][t]:
                        raise SystemExit(f"adopted extract {k}: m[{m}].{fld}.{t} differs from the record")
            if rec["m"][m]["M_R2"] != ad["m"][m]["M_R2"]:
                raise SystemExit(f"adopted extract {k}: m[{m}].M_R2 differs from the record")
        d["C_upper"] = str(rat(rec["C_upper"]))
        if rat(ad["C_upper"]) != rat(rec["C_upper"]):
            raise SystemExit(f"adopted extract {k}: C_upper differs from the record")
        gates[str(k)] = T.derived_identity_gate(st["R"], d, rec) | {"measurement_sha256": sha(raw),
                                                                    "producer_identity_gate": d["identity_gate"]}
        meas[k], aux[k] = d, rec["auxiliary_evidence"]
    if not all(v["pass"] for v in gates.values()):
        raise SystemExit("derived identity gate failed")

    lf = {r: {"gh": [], "ag": [], "dg": []} for r in range(5)}
    for k, d in st["a_cells"].items():
        for r in range(5):
            o = d["r"][str(r)]
            g, h = F(o["sup"]["G"]), F(o["sup"]["H"])
            lf[r]["gh"].append(g / h)
            lf[r]["ag"].append(F(o["abs_G_at_a"]) / g)
            lf[r]["dg"].append(F(o["delta_G"]))
    LF = {r: {"gh_max": max(v["gh"]), "ag_max": max(v["ag"]), "dg_max": max(v["dg"])} for r, v in lf.items()}

    sealed = json.loads(pinned("tc_consumption"))["consumptions"]
    base = {}
    for m in MS:
        _, _, passed, _ = compose(st, m, None)
        base[m] = passed
        if ranges(passed) != sealed[m]["pass_ranges"]:
            raise SystemExit(f"replay gate: pass ranges differ for m={m}")
    out = {"schema": "rebaseguard.p5y.k5.m5-tail.forecast.v2",
           "label": "MEASUREMENT-ANCHORED (non-certified where an input is estimated; the TCT0 route estimates "
                    "nothing). T2_AUDIT is a reconstruction of the frozen route comparison's forecast, not a bound.",
           "gates": "config/FEASIBILITY_GATES_B.json (frozen before any Campaign-B forecast)",
           "premise_supply": "every route uses tct_rule.tail_enclosure with the Lemma-G constants and the (P3') "
                             "sigma3 (midpoint tower) / sigma4 (cell tower with the mean-value correction)",
           "replay_gate": "PASS (adopted post-Campaign-A state reproduces the sealed consumption pass ranges)",
           "adopted_inputs_sha256": sha(adopted_raw),
           "derived_identity_gate": gates,
           "adopted_order3_evidence": {str(r): {n: str(v) for n, v in LF[r].items()} for r in range(5)},
           "routes": {}}
    for mode in ("TCT0", "T2_AUDIT", "T2_AUDIT_MEAS", "T2_EVIDENCE"):
        scen_out = {}
        for sname, scen in SCEN.items():
            if mode == "TCT0" and sname == "CONSERVATIVE":
                scen_out[sname] = {"note": "identical to NOMINAL: the TCT0 route has no not-yet-measured input",
                                   "closed_m5": scen_out["NOMINAL"]["closed_m5"],
                                   "per_m": scen_out["NOMINAL"]["per_m"]}
                continue
            tail, detail = tail_enclosures(st, meas, aux, mode, scen, LF)
            per_m = {}
            for m in MS:
                _, rows, passed, audit = compose(st, m, tail)
                per_m[m] = {"pass_ranges": ranges(passed),
                            "open_ranges": ranges(sorted(set(range(310)) - set(passed))),
                            "newly_passing": sorted(set(passed) - set(base[m])),
                            "regressed": sorted(set(base[m]) - set(passed)),
                            "tail": {str(k): ({"H_tail_exact": audit[str(k)]["H_tail"],
                                               "M_after_exact": audit[str(k)]["M"],
                                               "Gamma_exact": str(rows[k]["Gamma"])} if m == "5" else {})
                                     | {"H_tail": [float(F(x)) for x in audit[str(k)]["H_tail"]],
                                        "mag_tail": float(max(abs(F(audit[str(k)]["H_tail"][0])),
                                                              abs(F(audit[str(k)]["H_tail"][1])))),
                                        "M_after": float(F(audit[str(k)]["M"])),
                                        "empty": audit[str(k)]["empty"], "pass": bool(k in passed),
                                        "via": rows[k]["via"], "Gamma": float(rows[k]["Gamma"])}
                                     for k in TAIL}}
            scen_out[sname] = {"closed_m5": sum(1 for k in TAIL if per_m["5"]["tail"][str(k)]["pass"]),
                               "per_m": per_m, "detail": {str(k): detail[k] for k in TAIL}}
        cls = classify(scen_out["NOMINAL"]["closed_m5"], scen_out["CONSERVATIVE"]["closed_m5"])
        out["routes"][mode] = {"class_under_frozen_gates": cls, "scenarios": scen_out,
                               "new_real_addresses": 0 if mode == "TCT0" else 5}
    out["critical_sup_G_over_sup_H_ratio"] = {str(k): critical_ratio(st, meas, aux, LF, k) for k in TAIL}
    out["atom_constant_requirement"] = {str(k): atom_constant_requirement(st, meas, aux, k) for k in TAIL}
    out["selection"] = {
        "rule": "config/FEASIBILITY_GATES_B.json selection_rule and stop_rule, applied mechanically",
        "classes": {m: out["routes"][m]["class_under_frozen_gates"] for m in out["routes"]},
        "verdict": ("EXECUTE" if any(out["routes"][m]["class_under_frozen_gates"] in ("STRONG", "USEFUL")
                                     for m in out["routes"]) else "STOP_AND_WRITE_COSTED_CONTINUATION_PLAN")}
    data = json.dumps(out, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({"classes": out["selection"]["classes"], "verdict": out["selection"]["verdict"],
                      "closed_m5": {m: {s: out["routes"][m]["scenarios"][s]["closed_m5"] for s in SCEN}
                                    for m in out["routes"]},
                      "tct0_m5": {str(k): {n: out["routes"]["TCT0"]["scenarios"]["NOMINAL"]["per_m"]["5"]["tail"]
                                           [str(k)][n] for n in ("mag_tail", "M_after", "Gamma", "pass")}
                                  for k in TAIL},
                      "critical_ratio": out["critical_sup_G_over_sup_H_ratio"],
                      "atom_constant_requirement": {k: v["uniform_A_reduction_needed"]
                                                    for k, v in out["atom_constant_requirement"].items()},
                      "sha256": sha(data)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
