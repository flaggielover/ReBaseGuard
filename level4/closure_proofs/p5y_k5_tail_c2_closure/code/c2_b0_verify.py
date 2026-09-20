"""Campaign C2, Phase B0: read-only verification and pinning of every authoritative input. Stdlib only, no remote
host, no model quantity, no operator certification, no forecast. Runs before the C2 gate is frozen, and again inside
qualification.

    python3 -B c2_b0_verify.py --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = REPO / "level4/closure_proofs"

FRONTIER = "5289b6cee7134dd66e3289c3a210c8de5abb6a2c"
MAIN = "1cb453826313c189f0bdafd5b84120c1edb74da9"
TAIL = (305, 306, 307, 308, 309)

# every authoritative input C2 consumes, with the hash it must have (None = record, no prior published value)
PINS = {
    # --- authoritative coverage state
    "coverage_map_r4": ("p5y_k5_lower_front_order3/evidence/tc_r1/K5_COVERAGE_MAP_R4.json",
                        "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35"),
    "campaign_A_consumption": ("p5y_k5_lower_front_order3/evidence/tc_r1/TC_CONSUMPTION.json",
                               "1fa8d8dee78483c83d54bd90dba86a9316fb5c67c4acd43781a05103ab111f51"),
    "campaign_A_adjudication": ("p5y_k5_lower_front_order3/evidence/tc_r1/adjudication_r1/ADJUDICATION_R1.json", None),
    # --- Campaign A adopted TC machinery
    "tc_rule": ("p5y_k5_lower_front_order3/code/tc_rule.py",
                "8d402d11f6fc06ea2af88e3d3a01e376fefbe8ebacd8418f772116010e57afd5"),
    "tc_crosscheck": ("p5y_k5_lower_front_order3/code/tc_crosscheck.py",
                      "1c72117f57197d7dfcf588447510fee43cdb37426ac5f7ca85892b0e10ad8938"),
    "theorem_TC": ("p5y_k5_lower_front_order3/theorem/THEOREM_TC.md", None),
    # --- Campaign B repaired (P3') logic and evidence
    "tct_rule": ("p5y_k5_m5_tail_closure/code/tct_rule.py", None),
    "theorem_TCT": ("p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md", None),
    "tail_forecast_r2_code": ("p5y_k5_m5_tail_closure/code/tail_forecast_r2.py", None),
    "tail_forecast_r2": ("p5y_k5_m5_tail_closure/evidence/forecast_r2/TAIL_FORECAST_R2.json",
                         "0903715d6f20d812cc4cd90be3ad7f44c03d4d552610329b0d54ba73dcd9452d"),
    "adopted_tail_inputs": ("p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json",
                            "485fb1254e459683f48815c239d18d29119d651d0e77876f772c3fee9d29a37d"),
    "campaign_B_gates": ("p5y_k5_m5_tail_closure/config/FEASIBILITY_GATES_B.json",
                         "392101dd03b45ddf8feec5d4b986556ee474e77b5d0ec78488761ffb2cfafd94"),
    "campaign_B_review_r1": ("p5y_k5_m5_tail_closure/review/REVIEW_R1.md",
                             "30680ab623a6e83e27a1e4f86a18f11463050c012d26b5e99a0479b81d75816e"),
    "campaign_B_review_r2": ("p5y_k5_m5_tail_closure/review/REVIEW_R2.md",
                             "51c208cd80eaa901a3d8bad180268f7a23aeb43955c88a1502fc8eac5ec31f92"),
    "campaign_B_notes": ("p5y_k5_m5_tail_closure/CAMPAIGN_A_OPEN_NOTES_DISPOSITION.md", None),
    # --- Campaign C1 operator certification and its review
    "c1_gates": ("p5y_k5_tail_operator_registry/config/FEASIBILITY_GATES_C1.json",
                 "927ecfc7597c6d75c485117177b1b0d0a87729aeb6f5e469813905ed242ceb98"),
    "c1_registry": ("p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json",
                    "87bb1cfacb09c2a144cab0270427d91980ea742b36fd80f8963265a22d2eebb3"),
    "c1_forecast": ("p5y_k5_tail_operator_registry/evidence/forecast_r1/C1_FORECAST.json", None),
    "c1_tail_registry_code": ("p5y_k5_tail_operator_registry/code/c1_tail_registry.py", None),
    "c1_review": ("p5y_k5_tail_operator_registry/review/REVIEW_C1_PREFREEZE.md", None),
    "c1_notes": ("p5y_k5_tail_operator_registry/OPEN_NOTES_DISPOSITION_C1.md", None),
    # --- adopted Perron / taboo / atom machinery
    "theorem_AD": ("p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md", None),
    "taboo_certify": ("p5y_k5_perron_deflated_resolvent/code/taboo_certify.py",
                      "ced9422ca07981a9ad053acd79b72ef0d5007e93e49c16f2501f31c593fd0daa"),
    "build_registry": ("p5y_k5_perron_deflated_resolvent/code/build_registry.py", None),
    "deflated_consume": ("p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
                         "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72"),
    "registry_r1": ("p5y_k5_perron_deflated_resolvent/evidence/registry_r1/REGISTRY.json",
                    "1b7f5da743a2ce0d7f557c2dae054ab358a9175212eaa1fa29dea63a25780cb5"),
    # --- the frozen consumption chain and the order-3 executor identity
    "k5b_check": ("p5y_k5b_independent_countersignature/code/k5b_check.py", None),
    "consumption_adapter": ("p5y_k5b_consumption_adapter/code/consumption_adapter.py",
                            "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"),
    "e6_adapter_spec": ("p5y_k5b_consumption_adapter/README.md", None),
    "text_consume": ("p5y_k5_remaining_cell_closure/transport_extension/code/text_consume.py",
                     "657458ade03c4283ae6d5bd97e5567603380bf0e6281d8483f9c1fd45a62d0ea"),
    "cells_json": ("p5y_k1_cover_ledger_successor/config/cells.json",
                   "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"),
    "export_manifest": ("p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
                        "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334"),
    "order3_executor_registry": ("p5y_k5_cusum_order3_real_producer/config/REAL_CELL_AUTHORIZATION_REGISTRY.json",
                                 None),
    "order3_producer_manifest": ("p5y_k5_cusum_order3_real_producer/config/ORDER3_PRODUCER_MANIFEST.json", None),
}
IMMUTABLE_NS = ("p5y_k5_lower_front_order3", "p5y_k5_m5_tail_closure", "p5y_k5_tail_operator_registry",
                "p5y_k5_perron_deflated_resolvent", "p5y_k5b_independent_countersignature",
                "p5y_k5b_consumption_adapter", "p5y_k5_remaining_cell_closure", "p5y_k1_cover_ledger_successor",
                "p5y_k1_cusum_aux5_composite_closure", "p5y_k5_cusum_order3_real_producer",
                "p5y_k1_cusum_aux3_successor", "p5y_k1_cusum_aux5_successor",
                "p5y_k5_cusum_first_real_probe_protocol")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*a, check=True) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=check).stdout


def rat(p) -> F:
    return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {"schema": "rebaseguard.p5y.k5.tail-c2.b0-verification.v1"}

    head = git("rev-parse", "HEAD").strip()
    anc = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", FRONTIER, head]).returncode == 0
    dirty = [ln for ln in git("status", "--porcelain", "--untracked-files=all").splitlines() if ln.strip()]
    outside = [p for p in dirty if "p5y_k5_tail_c2_closure" not in p]
    ls = {ln.split()[1]: ln.split()[0] for ln in git("ls-remote", "origin", "refs/heads/main").splitlines() if ln.strip()}
    res["B1_git"] = {"head": head, "start_frontier": FRONTIER, "frontier_is_ancestor": anc,
                     "origin_main": ls.get("refs/heads/main"), "main_expected": MAIN,
                     "merges_since_frontier": len(git("log", "--merges", "--format=%H", f"{FRONTIER}..{head}").split()),
                     "dirty_outside_C2": outside,
                     "pass": anc and not outside and ls.get("refs/heads/main") == MAIN
                     and not git("log", "--merges", "--format=%H", f"{FRONTIER}..{head}").split()}

    bad, seen = [], {}
    for name, (rel, want) in PINS.items():
        p = CP / rel
        if not p.is_file():
            bad.append(f"{name}: missing")
            continue
        got = sha(p.read_bytes())
        seen[name] = {"path": "level4/closure_proofs/" + rel, "sha256": got}
        if want is not None and got != want:
            bad.append(f"{name}: {got[:12]} != {want[:12]}")
    res["B2_pins"] = {"count": len(seen), "mismatch": bad, "inputs": seen, "pass": not bad}

    moved = {ns: len(git("diff", "--name-only", FRONTIER, head, "--",
                         f"level4/closure_proofs/{ns}").split()) for ns in IMMUTABLE_NS}
    res["B3_immutability"] = {"changed_files": moved, "pass": all(v == 0 for v in moved.values())}

    r4 = json.loads((CP / PINS["coverage_map_r4"][0]).read_bytes())
    r5 = [str(p.relative_to(REPO)) for p in REPO.rglob("K5_COVERAGE_MAP_R5.json")]
    res["B4_coverage"] = {"K5_COVERAGE_COMPLETE": r4["K5_COVERAGE_COMPLETE"],
                          "union_open_ranges": r4["union_open_ranges"],
                          "open_per_m": {m: r4["per_m"][m]["open_ranges"] for m in r4["per_m"]},
                          "r5_exists": r5,
                          "pass": r4["K5_COVERAGE_COMPLETE"] is False and r4["union_open_ranges"] == [[305, 309]]
                          and r4["per_m"]["5"]["open_ranges"] == [[305, 309]]
                          and all(r4["per_m"][m]["open_ranges"] == [] for m in ("1", "2", "3")) and not r5}

    # B5 -- both predecessor campaigns really did stop before freeze: no protocol, no seal, no adoption
    b_ns, c1_ns = CP / "p5y_k5_m5_tail_closure", CP / "p5y_k5_tail_operator_registry"
    res["B5_predecessors_stopped"] = {
        "campaign_B_protocol_exists": (b_ns / "config/TCT_PROTOCOL.json").exists(),
        "campaign_C1_protocol_exists": (c1_ns / "config/C1_PROTOCOL.json").exists(),
        "campaign_B_seal_exists": any(b_ns.rglob("*SEAL*.json")),
        "campaign_C1_seal_exists": any(c1_ns.rglob("*SEAL*.json")),
        "pass": not (b_ns / "config/TCT_PROTOCOL.json").exists()
        and not (c1_ns / "config/C1_PROTOCOL.json").exists()
        and not any(b_ns.rglob("*SEAL*.json")) and not any(c1_ns.rglob("*SEAL*.json"))}

    # B6 -- the C1 certified operator constants, read as C2's starting point
    reg = json.loads((CP / PINS["c1_registry"][0]).read_bytes())
    blocks = {b["cell"]: b for b in reg["blocks"]}
    cons = {}
    for k in TAIL:
        b = blocks[k]
        v = {x: F(b[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")}
        cons[str(k)] = {x: float(v[x]) for x in v} | {
            "tau_over_D_lo": float(v["tau"] / v["D_lo"]),
            "Abar_eff": float(min(v["Abar"], v["tau"] / v["D_lo"])),
            "Abar_binds": bool(v["Abar"] < v["tau"] / v["D_lo"]),
            "d1": float(v["D1"] / v["D_lo"]), "d2": float(v["D2"] / v["D_lo"]),
            "e_lo": float(F(b["e_lo"])), "e_hi": float(F(b["e_hi"])),
            "taboo_alpha": b.get("taboo_alpha"), "arl_alpha": b.get("arl_alpha")}
    res["B6_c1_constants"] = {"certified": reg.get("certified"), "rule": reg.get("rule"),
                              "operator_only": reg.get("operator_only"), "blocks": len(reg["blocks"]),
                              "per_cell": cons,
                              "Abar_inert_on_all_cells": all(not cons[str(k)]["Abar_binds"] for k in TAIL),
                              "pass": reg.get("certified") is True and reg.get("rule") == "r2"
                              and reg.get("operator_only") is True and sorted(blocks) == list(TAIL)}

    # B7 -- the N1/N3/N5 dispositions exist and N1 is still open (it must be closed before any R-stage)
    c1_notes = (CP / PINS["c1_notes"][0]).read_text()
    b_notes = (CP / PINS["campaign_B_notes"][0]).read_text()
    registry_txt = (CP / PINS["order3_executor_registry"][0]).read_text()
    res["B7_notes"] = {"campaign_B_disposition_present": bool(b_notes.strip()),
                       "campaign_C1_disposition_present": bool(c1_notes.strip()),
                       "N1_still_open": "carried forward" in c1_notes or "carried forward" in b_notes,
                       "order3_registry_frozen_empty": "FROZEN_EMPTY" in registry_txt,
                       "pass": bool(b_notes.strip()) and bool(c1_notes.strip())
                       and "FROZEN_EMPTY" in registry_txt}

    res["ALL_PASS"] = all(v["pass"] for k, v in res.items() if re.fullmatch(r"B\d+_.*", k))
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({k: v["pass"] for k, v in res.items() if re.fullmatch(r"B\d+_.*", k)}
                     | {"ALL_PASS": res["ALL_PASS"], "sha256": sha(data)}))
    return 0 if res["ALL_PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
