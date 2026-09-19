"""Atom-deflated re-enclosure of the adopted CUSUM K1 records, consumed by the frozen K5-B (theorem AD, THEOREM_AD.md).

Composition plus one new certified rule. Nothing here evaluates the CUSUM model: every input is a published, manifest-bound
K1 record (residual norms, source errors, recorded eps radii and intervals), the adopted T-EXT result (cells 0..40), and an
operator-constant registry (tau_a, C_T, D, |D'|, |D''| per e-block). The frozen loader, the frozen K5-B and the adopted
T-EXT channel derivation are executed from their pinned bytes.

RULE (theorem AD, sections 4-5). For a block B with rational bounds
    tau >= Ghat 1 (a),  C >= ||Ghat||,  Dlo <= D,  D1 >= |D'|,  D2 >= |D''|,  k1 >= ||Khat'||,  k2 >= ||Khat''||
on every e in B:
    A0 = tau / Dlo
    A1 = tau k1 C / Dlo + tau D1 / Dlo^2
    A2 = tau (2 k1^2 C^2 + k2 C) / Dlo + 2 tau k1 C D1 / Dlo^2 + tau (2 D1^2 / Dlo^3 + D2 / Dlo^2)
and for every object r, with f = local residual + source error (recorded):
    |E_F(a)| <= A0 fF,   |E_D(a)| <= A0 fD + A1 fF,   |E_H(a)| <= A0 fH + 2 A1 fD + A2 fF
(midpoint residuals for F, D at e0; whole-cell residuals for H, uniformly on the cell).
A recorded enclosure centre +- (sum |c| eps_rec + rest) is tightened by Delta = sum |c| max(0, eps_rec - eps_new).

    python -B code/deflated_consume.py forecast --profile P.json --scale S [--out OUT]      (NON-CERTIFIED constants)
    python -B code/deflated_consume.py consume --registry REG.json --registry-sha256 SHA --out OUT   (certified; frozen)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
ADAPTER = CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py"
ADAPTER_SHA256 = "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"
TEXT_CONSUME = CP + "p5y_k5_remaining_cell_closure/transport_extension/code/text_consume.py"
TEXT_CONSUME_SHA256 = "657458ade03c4283ae6d5bd97e5567603380bf0e6281d8483f9c1fd45a62d0ea"
TEXT_RESULT = CP + "p5y_k5_remaining_cell_closure/transport_extension/evidence/qualification_r1/TEXT_RESULT.json"
TEXT_RESULT_SHA256 = "cb97cabcc3b5848665584e33ad4207c6d36ce835729725265d585dc8f3ee4f87"
SEALED = CP + "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json"
SEALED_SHA256 = "cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae"
MS = ("1", "2", "3", "5")
TEXT_CHANNEL = tuple(range(1, 41))
TEXT_CURVATURE = tuple(range(0, 41))
# Rational upper bounds of the whole-line Gaussian moments E|He_1(Y)| = sqrt(2/pi), E|He_2(Y)| = 4 phi(1)
# (theorem AD, lemma K; the qualification re-proves both inequalities in Arb).
K1_BOUND = F(7978846, 10 ** 7)
K2_BOUND = F(9678830, 10 ** 7)
SCHEMA = "rebaseguard.p5y.k5.perron-deflation.deflated-consumption.v1"


class DeflationRefusal(RuntimeError):
    pass


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def _load_pinned(repo: Path, rel: str, pin: str, name: str):
    path = repo / rel
    if sha256_bytes(path.read_bytes()) != pin:
        raise DeflationRefusal(f"{name} does not match its pin")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------------------------------------ theorem AD, rule
def atom_constants(tau: F, C: F, Dlo: F, D1: F, D2: F, k1: F = K1_BOUND, k2: F = K2_BOUND) -> dict:
    """A0, A1, A2 of theorem AD (monotone: upper bounds in, lower bound Dlo in)."""
    for name, v in (("tau", tau), ("C", C), ("Dlo", Dlo), ("D1", D1), ("D2", D2), ("k1", k1), ("k2", k2)):
        if not isinstance(v, F) or v < 0:
            raise DeflationRefusal(f"constant {name} must be a nonnegative Fraction")
    if not Dlo > 0 or not tau >= 1 or not C >= tau:
        raise DeflationRefusal("constants violate tau >= 1, C >= tau, Dlo > 0")
    A0 = tau / Dlo
    A1 = tau * k1 * C / Dlo + tau * D1 / Dlo ** 2
    A2 = (tau * (2 * k1 ** 2 * C ** 2 + k2 * C) / Dlo + 2 * tau * k1 * C * D1 / Dlo ** 2
          + tau * (2 * D1 ** 2 / Dlo ** 3 + D2 / Dlo ** 2))
    return {"A0": A0, "A1": A1, "A2": A2}


def atom_constants_r2(Abar: F, tau: F, C: F, Dlo: F, D1: F, D2: F, k1: F = K1_BOUND, k2: F = K2_BOUND) -> dict:
    """Lemma Dv' (r2): A_j = Abar_eff * (tame factor), Abar_eff = min(Abar, tau/Dlo) >= E_a[tau]."""
    base = atom_constants(tau, C, Dlo, D1, D2, k1, k2)          # validates the constants
    if not isinstance(Abar, F) or not Abar >= 1:
        raise DeflationRefusal("Abar must be a Fraction >= 1")
    ab = min(Abar, tau / Dlo)
    d1, d2 = D1 / Dlo, D2 / Dlo
    out = {"A0": ab, "A1": ab * (k1 * C + d1),
           "A2": ab * (2 * k1 ** 2 * C ** 2 + k2 * C + 2 * k1 * C * d1 + 2 * d1 ** 2 + d2)}
    for j in ("A0", "A1", "A2"):                                   # r2 never exceeds r1 by construction
        if out[j] > base[j]:
            raise DeflationRefusal(f"r2 constant {j} exceeds r1 (impossible)")
    return out


def source_node(r: int, k: int) -> str:
    """Frozen propagate._source_node: the closed form for r = 0, the candidate otherwise."""
    return f"Sclosed:{k}" if r == 0 else f"S:{r}:{k}"


def deflated_radii(rec: dict, A: dict) -> dict:
    """Point errors at the atom for every r: F, D at the midpoint; H uniformly on the cell."""
    obj, em, ec = rec["objects"], rec["eps_mid"], rec["eps_cell"]
    out = {}
    for r in range(5):
        fF_mid = F(obj[f"F_{r}"]["delta_mid"]) + F(em[source_node(r, 0)])
        fD_mid = F(obj[f"dF_{r}"]["delta_mid"]) + F(em[source_node(r, 1)])
        fF_cell = F(obj[f"F_{r}"]["delta_cell"]) + F(ec[source_node(r, 0)])
        fD_cell = F(obj[f"dF_{r}"]["delta_cell"]) + F(ec[source_node(r, 1)])
        fH_cell = F(obj[f"H_{r}"]["delta_cell"]) + F(ec[source_node(r, 2)])
        out[r] = {"F": A["A0"] * fF_mid,
                  "D": A["A0"] * fD_mid + A["A1"] * fF_mid,
                  "H": A["A0"] * fH_cell + 2 * A["A1"] * fD_cell + A["A2"] * fF_cell}
    return out


def tighten(interval: tuple, eps_rec: list, eps_new: list, m: int) -> tuple:
    """centre +- (sum (1/m) eps_rec + rest)  ->  shrink both ends by sum (1/m) max(0, eps_rec - eps_new)."""
    lo, hi = interval
    need = sum((F(1, m) * e for e in eps_rec), F(0))
    if (hi - lo) / 2 < need:
        raise DeflationRefusal("recorded interval narrower than its recorded radii (assembly assumption violated)")
    delta = sum((F(1, m) * max(F(0), a - b) for a, b in zip(eps_rec, eps_new)), F(0))
    nlo, nhi = lo + delta, hi - delta
    if nlo > nhi:
        raise DeflationRefusal("empty tightened interval")
    return nlo, nhi


def block_for(registry: dict, x_lo: F, x_hi: F):
    """Worst-case constants over every registry block meeting [x_lo, x_hi] (r2 registries: meeting the open
    interval (x_lo, x_hi), so a block ending at x_lo does not count); None if the cell is not covered."""
    if registry.get("rule") == "r2":
        hit = [b for b in registry["blocks"] if F(b["e_lo"]) < x_hi and x_lo < F(b["e_hi"])]
    else:
        hit = [b for b in registry["blocks"] if F(b["e_lo"]) <= x_hi and x_lo <= F(b["e_hi"])]
    if not hit:
        return None
    lo_cov = min(F(b["e_lo"]) for b in hit)
    hi_cov = max(F(b["e_hi"]) for b in hit)
    if lo_cov > x_lo or hi_cov < x_hi:
        return None
    # contiguity of the hit blocks over [x_lo, x_hi]
    edges = sorted((F(b["e_lo"]), F(b["e_hi"])) for b in hit)
    reach = edges[0][0]
    for a, b in edges:
        if a > reach:
            return None
        reach = max(reach, b)
    out = {"tau": max(F(b["tau"]) for b in hit), "C": max(F(b["C_T"]) for b in hit),
           "Dlo": min(F(b["D_lo"]) for b in hit), "D1": max(F(b["D1"]) for b in hit),
           "D2": max(F(b["D2"]) for b in hit)}
    if registry.get("rule") == "r2":
        out["Abar"] = max(F(b["Abar"]) for b in hit)
    return out


def apply_deflation(cells: list, records: dict, registry: dict, m: str, cover: list, domain: tuple) -> dict:
    """Tighten R, D (midpoint) and R'' (whole cell) of every covered cell in the domain; return per-cell audit."""
    mi = int(m)
    audit = {}
    for i, c in enumerate(cover):
        k = c["index"]
        if not (domain[0] <= k <= domain[1]):
            continue
        cons = block_for(registry, cells[i]["x_lo"], cells[i]["x_hi"])
        if cons is None:
            continue
        rec = records[k]
        if registry.get("rule") == "r2":
            A = atom_constants_r2(cons["Abar"], cons["tau"], cons["C"], cons["Dlo"], cons["D1"], cons["D2"])
        else:
            A = atom_constants(cons["tau"], cons["C"], cons["Dlo"], cons["D1"], cons["D2"])
        rad = deflated_radii(rec, A)
        em, er = rec["eps_mid"], rec["eps_cell_refined"]
        R = tighten(cells[i]["R"], [F(em[f"F:{r}"]) for r in range(mi)], [rad[r]["F"] for r in range(mi)], mi)
        D = tighten(cells[i]["D"], [F(em[f"D:{r}"]) for r in range(mi)], [rad[r]["D"] for r in range(mi)], mi)
        H = tighten(cells[i]["H"], [F(er[f"H:{r}"]) for r in range(mi)], [rad[r]["H"] for r in range(mi)], mi)
        cells[i]["R"], cells[i]["D"], cells[i]["H"] = R, D, H
        cells[i]["M"] = min(cells[i]["M"], max(abs(H[0]), abs(H[1])))
        audit[k] = {"A0": str(A["A0"]), "A1": str(A["A1"]), "A2": str(A["A2"]),
                    "eps_new": {str(r): {t: str(rad[r][t]) for t in "FDH"} for r in range(mi)}}
    return audit


# ------------------------------------------------------------------------------------------------ consumption
def run(registry: dict, records_dir: Path, *, repo: Path = REPO, domain=(0, 309), with_text: bool = True) -> dict:
    A = _load_pinned(repo, ADAPTER, ADAPTER_SHA256, "e6_adapter_for_deflation")
    TC = _load_pinned(repo, TEXT_CONSUME, TEXT_CONSUME_SHA256, "text_consume_for_deflation")
    traw = (repo / TEXT_RESULT).read_bytes()
    sraw = (repo / SEALED).read_bytes()
    if sha256_bytes(traw) != TEXT_RESULT_SHA256 or sha256_bytes(sraw) != SEALED_SHA256:
        raise DeflationRefusal("adopted T-EXT result or slot-1 record hash mismatch")
    per = json.loads(sraw)["scientific"]["per_m"]
    L1 = {m: F(per[m]["L1"]) for m in MS}
    lam, m2 = TC.text_objects(json.loads(traw), {m: per[m]["L1"] for m in MS})
    comp = A.frozen_components(repo)
    KM, KB = comp["loader"], comp["theorem"]
    A.bound_file(repo / A.CELLS_JSON, A.CELLS_SHA256, "cells.json")
    manifest = json.loads(A.bound_file(repo / A.MANIFEST, A.MANIFEST_SHA256, "record manifest"))
    cover = KM.load_cells(repo / A.CELLS_JSON, A.DETECTOR)
    if [c["index"] for c in cover] != list(range(0, 310)):
        raise DeflationRefusal("cover universe mismatch")
    records, hashes = A.read_records(KM, Path(records_dir), cover, manifest)
    out = {}
    for m in MS:
        cells = A.cells_for_m(KM, cover, records, m, L1[m])
        audit = apply_deflation(cells, records, registry, m, cover, domain)
        if with_text:
            for k in TEXT_CHANNEL:
                if cells[k]["L"] is not None:
                    raise DeflationRefusal("unexpected order-3 channel before T-EXT assignment")
                cells[k]["L"] = lam[m][k]
            for k in TEXT_CURVATURE:
                b = m2[m][k]
                lo, hi = cells[k]["H"]
                if max(lo, -b) > min(hi, b):
                    raise DeflationRefusal(f"empty curvature enclosure cell {k} m {m}")
                cells[k]["H"] = (max(lo, -b), min(hi, b))
                cells[k]["M"] = min(cells[k]["M"], b)
        rows = KB.k5b_literal(cells)
        passed = [cover[i]["index"] for i, r in enumerate(rows) if r["pass"] is True]
        opened = [k for k in range(310) if k not in set(passed)]
        out[m] = {"pass_ranges": KM.ranges(passed), "pass_count": len(passed), "open_ranges": KM.ranges(opened),
                  "open_count": len(opened), "rows_sha256": sha256_bytes(canonical(A.row_json(rows))),
                  "deflated_cells": sorted(audit), "via": {str(i): rows[i]["via"] for i in range(0, 160)},
                  "cells": {str(i): {"R": [str(x) for x in cells[i]["R"]], "D": [str(x) for x in cells[i]["D"]],
                                     "H": [str(x) for x in cells[i]["H"]], "M": str(cells[i]["M"])}
                            for i in range(0, 160)},
                  "audit": audit}
    return {"schema": SCHEMA, "consumptions": out,
            "inputs": {"adapter_sha256": ADAPTER_SHA256, "text_consume_sha256": TEXT_CONSUME_SHA256,
                       "text_result_sha256": TEXT_RESULT_SHA256, "sealed_record_sha256": SEALED_SHA256,
                       "manifest_sha256": A.MANIFEST_SHA256, "cells_json_sha256": A.CELLS_SHA256,
                       "records_sha256": sha256_bytes(canonical(hashes)), "record_count": len(hashes),
                       "components": comp["sha256"]},
            "domain": list(domain), "with_text": with_text, "code_sha256": sha256_bytes(HERE.read_bytes())}


# ------------------------------------------------------------------------------------------------ forecast registry
def forecast_registry(profile: dict, scale: F, width: F = F(1, 100), e_max: F = F(12, 100)) -> dict:
    """NON-CERTIFIED registry from the float operator profile: blocks of `width`, each constant taken at the block's
    worst end (every profile quantity is monotone on [0, 0.13]), then C_T and tau multiplied by `scale`
    (the certification loss / threshold sweep parameter). D, D', D'' are taken with a 10 % safety margin."""
    rows = sorted(profile["rows"], key=lambda r: r["e"])

    def interp(e, key):
        for a, b in zip(rows, rows[1:]):
            if a["e"] <= e <= b["e"]:
                t = (e - a["e"]) / (b["e"] - a["e"])
                return a[key] + t * (b[key] - a[key])
        raise ValueError(e)
    blocks = []
    lo = F(0)
    while lo < e_max:
        hi = min(lo + width, e_max)
        f = lambda v: F(v).limit_denominator(10 ** 9)
        blocks.append({"e_lo": str(lo), "e_hi": str(hi),
                       "tau": str(f(interp(float(hi), "tau_a") * float(scale))),
                       "C_T": str(f(interp(float(hi), "C_T") * float(scale))),
                       "D_lo": str(f(interp(float(lo), "D") / 1.1)),
                       "D1": str(f(abs(interp(float(hi), "D1")) * 1.1)),
                       "D2": str(f(interp(float(hi), "D2") * 1.1))})
        lo = hi
    return {"schema": "rebaseguard.p5y.k5.perron-deflation.operator-registry.v1", "certified": False,
            "use": "FORECAST ONLY", "scale": str(scale), "blocks": blocks}


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("forecast")
    f.add_argument("--profile", required=True)
    f.add_argument("--scales", default="1")
    f.add_argument("--records", default="/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
    f.add_argument("--out", required=True)
    c = sub.add_parser("consume")
    c.add_argument("--registry", required=True)
    c.add_argument("--registry-sha256", required=True)
    c.add_argument("--records", default="/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
    c.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "forecast":
        profile = json.loads(Path(a.profile).read_text())
        res = {"schema": SCHEMA + ".forecast", "certified": False, "label": "FORECAST (non-certified constants)",
               "runs": {}}
        for s in a.scales.split(","):
            reg = forecast_registry(profile, F(s))
            r = run(reg, Path(a.records))
            res["runs"][s] = {"registry": reg,
                              "per_m": {m: {k: v for k, v in x.items() if k in ("pass_ranges", "open_ranges",
                                                                                   "open_count", "pass_count")}
                                        for m, x in r["consumptions"].items()}}
            print(s, {m: x["open_ranges"] for m, x in r["consumptions"].items()}, flush=True)
            if s == a.scales.split(",")[0]:
                res["detail_first_scale"] = r
        Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
        return 0
    raw = Path(a.registry).read_bytes()
    if sha256_bytes(raw) != a.registry_sha256:
        raise DeflationRefusal("registry does not match its pin")
    reg = json.loads(raw)
    if reg.get("certified") is not True:
        raise DeflationRefusal("consume requires a certified registry")
    res = run(reg, Path(a.records))
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print({m: x["open_ranges"] for m, x in res["consumptions"].items()}, "sha256", sha256_bytes(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
