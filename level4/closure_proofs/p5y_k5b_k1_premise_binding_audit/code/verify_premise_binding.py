"""Verifier for the K5-B -> K1 CUSUM premise-binding audit, result r1.

    python3 -B code/verify_premise_binding.py            # recompute every Git-checkable fact, compare to the result
    python3 -B code/verify_premise_binding.py --emit     # print the recomputed machine sections (used once to write r1)

It recomputes:
  pins           sha256 of every cited source at the audit base commit
  manifest       producer manifest v3: every bound file hash vs repository bytes; manifest hash, runtime hash and
                 producer identity recomputed with the frozen canonical form
  geometry       frozen CUSUM cover: contiguity from x_0 = 0, midpoint/half-width consistency, the cell containing 2
  assembly       the frozen coefficient table equals the convention-A rule c_(m,t) = 1/t - 1/m
  records        the two committed record copies (cells 0, 309): sha256 == committed composite export manifest;
                 frozen scientific hash (Aux4 hash_v2) recomputes; producer identity/manifest; geometry == cells.json
  PB6            exact-rational lower bound of R on cell 309 from the record's own R/D/M_R2, per m
  PB3            exact-rational enclosure of R'(0) from cell 0 (D_interval widened by e0 * M_R2), and the implied
                 GammaTilde interval, compared with the recorded estimates / certified m=1 enclosure

No scientific computation: every number is exact rational arithmetic on committed certified endpoints.
Standard library only (plus the frozen, stdlib-only Aux4 hash_v2).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = "level4/closure_proofs/"
RESULT = NS / "result_r1/PREMISE_BINDING_RESULT.json"
BASE = "1bf31bc87afb0422be116c4b2cd1d673c68fc308"
M_VALUES = ("1", "2", "3", "5")

CITED = [
    "p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md",
    "p5y_k5b_independent_countersignature/COUNTERSIGNATURE.json",
    "p5y_k5b_k1_premise_binding_audit/config/AUDIT_PLAN.json",
    "p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md",
    "p5x_global_nonlinear_dynamics/PROOF.md",
    "p5x_global_nonlinear_dynamics/DEPENDENCY_AUDIT.md",
    "p5x_global_nonlinear_dynamics/DEFECT_REGISTER.md",
    "p5x_global_nonlinear_dynamics/FEASIBILITY_AUDIT.md",
    "p5_nonlinear_dynamics/THEOREM.md",
    "p5_nonlinear_dynamics/PROOF.md",
    "m_gt_1_priority1/THEOREM.md",
    "m_gt_1_priority1/CLOSURE_REPORT.md",
    "p9_final_synthesis/CLAIM_LEDGER.json",
    "d4_phase_map/DEFINITION_AUDIT.md",
    "p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md",
    "p5y_k1_cover_ledger_successor/config/cells.json",
    "p5y_k1_cover_ledger_successor/config/checkpoint.json",
    "p5y_k1_cusum_kernel/IMPLEMENTATION_MAP.md",
    "p5y_k1_cover_ledger_implementation/code/cusum_layer1.py",
    "p5y_k1_cover_ledger_implementation/code/cusum_layer2.py",
    "p5y_k1_cover_ledger_implementation/code/propagate.py",
    "p5y_k1_cover_ledger_implementation/code/refine.py",
    "p5y_k1_cover_ledger_implementation/code/assembly.py",
    "p5y_k1_cover_ledger_implementation/code/ledger.py",
    "p5y_k1_cover_ledger_implementation/code/intervals.py",
    "p5y_k1_cusum_completion_successor/code/order2.py",
    "p5y_k1_cusum_completion_successor/code/refine2.py",
    "p5y_k1_cusum_aux3_successor/code/aux_propagate.py",
    "p5y_k1_cusum_aux3_successor/code/aux_refine.py",
    "p5y_k1_cusum_aux3_successor/code/aux_certifier.py",
    "p5y_k1_cusum_aux3_successor/code/ancestry.py",
    "p5y_k1_cusum_aux4_fullcover/code/ancestry4.py",
    "p5y_k1_cusum_aux4_fullcover/code/hash_v2.py",
    "p5y_k1_cusum_aux5_successor/code/qualify5.py",
    "p5y_k1_cusum_aux5_successor/code/manifest_v3.py",
    "p5y_k1_cusum_aux5_successor/manifests/producer_manifest_v3.json",
    "p5y_k1_cusum_aux5_production_checkpoint/code/prod_sealer.py",
    "p5y_k1_cusum_aux5_glibc_successor/config/GLIBC_SUCCESSOR_CHECKPOINT.json",
    "p5y_k1_cusum_aux5_composite_closure/README.md",
    "p5y_k1_cusum_aux5_composite_closure/config/CLOSURE_VERDICT.json",
    "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
]
R2_PATH_MODULES = ("aux_propagate.py", "aux_refine.py", "aux_certifier.py", "refine2.py", "refine.py", "order2.py",
                   "propagate.py", "assembly.py", "depgraph.py", "ledger.py", "intervals.py", "cusum_layer1.py",
                   "cusum_layer2.py", "sharp_norms.py", "sharp_certifier.py", "opnorms.py", "spec.py", "qualify5.py",
                   "aux_collocation.py")
GAMMA_ESTIMATES = {"1": "15.916540430", "2": "13.264824962", "3": "11.957078195", "5": "10.226363970"}
GAMMA_CERT_M1 = ("3.9243482005828971282", "27.8493821275467032805")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob(commit: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{path}"], check=True,
                          capture_output=True).stdout


def canonical_v3(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def pins() -> dict:
    return {CP + p: sha(git_blob(BASE, CP + p)) for p in CITED}


def manifest_section() -> dict:
    mpath = REPO / CP / "p5y_k1_cusum_aux5_successor/manifests/producer_manifest_v3.json"
    m = json.loads(mpath.read_text())
    mismatched = sorted(p for p, h in m["files"].items()
                        if not (REPO / p).exists() or sha((REPO / p).read_bytes()) != h)
    names = {Path(p).name for p in m["files"]}
    src = (REPO / CP / "p5y_k1_cusum_aux5_successor/code/manifest_v3.py").read_text()
    schema = re.search(r'^SCHEMA = "([^"]+)"', src, re.M).group(1)
    mh = sha(canonical_v3(m))
    rh = sha(canonical_v3(m["runtime"]))
    pid = sha(canonical_v3({"schema": schema, "manifest_version": m["manifest_version"],
                            "manifest_hash": mh, "runtime_contract_hash": rh}))
    closure = json.loads((REPO / CP / "p5y_k1_cusum_aux5_composite_closure/config/CLOSURE_VERDICT.json").read_text())
    return {"bound_files": len(m["files"]), "bound_file_mismatches": mismatched,
            "r2_path_modules_missing_from_manifest": sorted(n for n in R2_PATH_MODULES if n not in names),
            "manifest_hash": mh, "runtime_contract_hash": rh, "producer_identity_hash": pid,
            "equals_closure_producer_identity": pid == closure["producer_identity_hash"]}


def _v(pair) -> F:
    if F(pair[1]) != 0:
        raise ValueError("symbolic affine component in a CUSUM cell")
    return F(pair[0])


def geometry_section() -> dict:
    cells = sorted((c for c in json.loads((REPO / CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_text())
                    if c["detector"] == "CUSUM"), key=lambda c: c["index"])
    problems = []
    for i, c in enumerate(cells):
        lo, hi, e0, rho = _v(c["left"]), _v(c["right"]), _v(c["e0"]), _v(c["rho"])
        if c["index"] != i:
            problems.append(f"index {i}")
        if e0 != (lo + hi) / 2 or rho != (hi - lo) / 2 or rho <= 0:
            problems.append(f"midpoint/half-width {i}")
        if (i == 0 and lo != 0) or (i > 0 and lo != _v(cells[i - 1]["right"])):
            problems.append(f"contiguity {i}")
    containing_2 = [c["index"] for c in cells if _v(c["left"]) <= 2 <= _v(c["right"])]
    return {"cells": len(cells), "problems": problems, "x0": str(_v(cells[0]["left"])),
            "cells_meeting_0_2": sum(1 for c in cells if _v(c["left"]) < 2),
            "cells_containing_2": containing_2,
            "cell_309": [str(_v(cells[309]["left"])), str(_v(cells[309]["right"]))]}


def assembly_section() -> dict:
    table = json.loads((REPO / CP / "p5y_k1_cover_ledger_successor/config/checkpoint.json").read_text())["assembly"]
    ok = {}
    for m in M_VALUES:
        mm = int(m)
        rule = [("F", r, 0, F(1, mm)) for r in range(mm)]
        rule += [("W", r, t - r - 1, F(1, t) - F(1, mm)) for t in range(1, mm) for r in range(t)]
        ok[m] = sorted((k, int(r), int(j), F(c)) for k, r, j, c in table[m]) == sorted(rule)
    return {"frozen_table_equals_convention_A_rule": ok}


def _record(i: int) -> tuple[dict, bytes]:
    raw = (NS / f"result_r1/records/aux5_CUSUM_{i}_256.json").read_bytes()
    return json.loads(raw), raw


def records_section(ident: str, manifest_hash: str) -> dict:
    sys.path.insert(0, str(REPO / CP / "p5y_k1_cusum_aux4_fullcover/code"))
    import hash_v2 as H  # frozen, stdlib-only
    export = json.loads((REPO / CP / "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/"
                                      "COMPOSITE_EXPORT_MANIFEST.json").read_text())["files"]
    frozen = {c["index"]: c for c in json.loads((REPO / CP / "p5y_k1_cover_ledger_successor/config/cells.json")
                                                .read_text()) if c["detector"] == "CUSUM"}
    out = {}
    for i in (0, 309):
        rec, raw = _record(i)
        fz = frozen[i]
        out[str(i)] = {
            "sha256": sha(raw),
            "sha256_equals_committed_export_manifest": sha(raw) == export[f"k4_records/aux5_CUSUM_{i}_256.json"],
            "scientific_content_hash_recomputes": H.record_scientific_hash(rec) == rec["scientific_content_hash"],
            "producer_identity_equals_manifest_v3": rec["producer_identity_hash"] == ident,
            "producer_manifest_hash_equals_manifest_v3": rec["producer_manifest_hash"] == manifest_hash,
            "producer_manifest_path": rec["producer_manifest_path"],
            "geometry_equals_frozen_cells": (rec["e0"], rec["rho"], rec["C_upper"]) == (fz["e0"], fz["rho"],
                                                                                       fz["C_upper"]),
            "detector": rec["detector"], "precision_bits": rec["precision_bits"],
        }
    return out


def pb6_section() -> dict:
    rec, _ = _record(309)
    e0, rho = _v(rec["e0"]), _v(rec["rho"])
    out = {"cell": [str(e0 - rho), str(e0 + rho)], "contains_2": e0 - rho <= 2 <= e0 + rho, "m": {}}
    for m in M_VALUES:
        L = rec["m"][m]
        Rlo = F(L["R_interval"]["lo"])
        D = (F(L["D_interval"]["lo"]), F(L["D_interval"]["hi"]))
        M = F(L["M_R2"])
        lower = Rlo - rho * max(abs(D[0]), abs(D[1])) - rho * rho * M / 2
        tg = L["target_gate"]
        out["m"][m] = {"target_gate_status": tg["status"], "strictly_inside_minus2_2": tg["strictly_inside_minus2_2"],
                       "recorded_gate_lo": tg["lo"], "exact_whole_cell_lower_bound_of_R": str(lower),
                       "exact_lower_bound_float_diagnostic": float(lower),
                       "margin_above_minus_2": float(lower + 2),
                       "exact_lower_bound_gt_minus_2": lower > -2,
                       "recorded_gate_lo_le_exact_recheck": F(tg["lo"]) <= lower,
                       "M_R2_equals_mag_R2_interval": M == max(abs(F(L["R2_interval"]["lo"])),
                                                               abs(F(L["R2_interval"]["hi"])))}
    return out


def pb3_section() -> dict:
    rec, _ = _record(0)
    e0, rho = _v(rec["e0"]), _v(rec["rho"])
    lo_c, hi_c = F(GAMMA_CERT_M1[0]), F(GAMMA_CERT_M1[1])
    out = {"e0": str(e0), "rho": str(rho), "cell_0_is_0_to_2e0": e0 == rho, "m": {}}
    for m in M_VALUES:
        L = rec["m"][m]
        D = (F(L["D_interval"]["lo"]), F(L["D_interval"]["hi"]))
        M = F(L["M_R2"])
        rp0 = (D[0] - e0 * M, D[1] + e0 * M)          # |R'(0) - R'(e0)| <= e0 * sup_[0,e0] |R''| <= e0 * M_R2
        gam = (1 - rp0[1], 1 - rp0[0])
        est = F(GAMMA_ESTIMATES[m])
        row = {"R_prime_0_enclosure_float_diagnostic": [float(rp0[0]), float(rp0[1])],
               "implied_GammaTilde_interval_float_diagnostic": [float(gam[0]), float(gam[1])],
               "implied_width": float(gam[1] - gam[0]),
               "contains_recorded_estimate": gam[0] <= est <= gam[1],
               "R_prime_0_negative_certified": rp0[1] < 0}
        if m == "1":
            row["intersects_certified_m1_enclosure"] = max(gam[0], lo_c) <= min(gam[1], hi_c)
            row["inside_certified_m1_enclosure"] = lo_c <= gam[0] and gam[1] <= hi_c
        out["m"][m] = row
    return out


def build() -> dict:
    man = manifest_section()
    return {"pins_at_base_commit": pins(), "manifest_v3": man, "geometry": geometry_section(),
            "assembly": assembly_section(),
            "records": records_section(man["producer_identity_hash"], man["manifest_hash"]),
            "pb6_recheck": pb6_section(), "pb3_external_consistency": pb3_section()}


def consistency_problems(result: dict, live: dict) -> list[str]:
    errs = []
    for k, v in live.items():
        if result.get("recomputed", {}).get(k) != v:
            errs.append(f"recomputed section {k} differs from the committed result")
    man, geo, rec = live["manifest_v3"], live["geometry"], live["records"]
    must = {
        "manifest bound files match repository": man["bound_file_mismatches"] == [],
        "R'' path modules all bound": man["r2_path_modules_missing_from_manifest"] == [],
        "identity reproduces closure": man["equals_closure_producer_identity"],
        "cover contiguous from 0": geo["problems"] == [] and geo["x0"] == "0",
        "unique cell containing 2 is 309": geo["cells_containing_2"] == [309],
        "assembly rule": all(live["assembly"]["frozen_table_equals_convention_A_rule"].values()),
        "records bound": all(r["sha256_equals_committed_export_manifest"] and r["scientific_content_hash_recomputes"]
                             and r["producer_identity_equals_manifest_v3"]
                             and r["producer_manifest_hash_equals_manifest_v3"] and r["geometry_equals_frozen_cells"]
                             for r in rec.values()),
    }
    errs += [f"required fact false: {k}" for k, ok in must.items() if not ok]
    v = result["verdicts"]
    pb6_ok = live["pb6_recheck"]["contains_2"] and all(
        x["target_gate_status"] == "PASS" and x["exact_lower_bound_gt_minus_2"] for x in live["pb6_recheck"]["m"].values())
    if v["PB6_R2_ENDPOINT_GATE"] in ("BOUND", "BOUND_WITH_NOTE") and not pb6_ok:
        errs.append("PB6 claims binding but the exact recheck does not support it")
    ext = all(x["contains_recorded_estimate"] for x in live["pb3_external_consistency"]["m"].values())
    if v["PB3_EXTERNAL_CONSISTENCY"] == "PASS" and not ext:
        errs.append("PB3 external consistency claimed PASS but the check fails")
    if v["PB5_WHOLE_CELL_R2"] in ("BOUND", "BOUND_WITH_NOTE") and not (must["manifest bound files match repository"]
                                                                       and must["R'' path modules all bound"]
                                                                       and must["identity reproduces closure"]):
        errs.append("PB5 claims binding without manifest binding")
    if result["B3_REOPENED"] != "NO" or result["NEW_K5_BLOCKER_CREATED"] not in ("YES", "NO"):
        errs.append("B3 must not be reopened by this audit")
    if v["CUSUM_K5B_K1_PREMISE_BINDING"] == "PASS" and any(
            v[k] != "BOUND" for k in ("PB2", "PB3", "PB4_FUNCTION_IDENTITY", "PB5_WHOLE_CELL_R2", "PB6_R2_ENDPOINT_GATE")):
        errs.append("overall PASS requires every PB item BOUND without note")
    if result["SR_PREMISE_BINDING"] != "UNDETERMINED_PENDING_PS1":
        errs.append("SR binding must remain UNDETERMINED_PENDING_PS1")
    return errs


def main(argv) -> int:
    live = build()
    if "--emit" in argv:
        print(json.dumps(live, indent=1, sort_keys=True))
        return 0
    result = json.loads(RESULT.read_text())
    errs = consistency_problems(result, live)
    print("PREMISE_BINDING_RESULT_VERIFIED" if not errs else "PREMISE_BINDING_RESULT_REFUSED",
          sha(RESULT.read_bytes()))
    for e in errs:
        print(" -", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
