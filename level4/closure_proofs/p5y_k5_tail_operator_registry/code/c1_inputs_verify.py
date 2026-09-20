"""Campaign C1, Phase A: read-only verification and pinning of every authoritative input. Stdlib only, no remote host,
no model quantity, no operator certification. Runs before the forecast and again inside qualification.

    python3 -B c1_inputs_verify.py --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = REPO / "level4/closure_proofs"

FRONTIER = "76c37de1d20e90e2543dad33f4649d6ed65b0dd1"
MAIN = "1cb453826313c189f0bdafd5b84120c1edb74da9"
GATE_REL = "level4/closure_proofs/p5y_k5_tail_operator_registry/config/FEASIBILITY_GATES_C1.json"
GATE_SHA = "927ecfc7597c6d75c485117177b1b0d0a87729aeb6f5e469813905ed242ceb98"

# every authoritative input C1 consumes, with the hash it must have
PINS = {
    # --- the authoritative coverage state
    "coverage_map_r4": ("p5y_k5_lower_front_order3/evidence/tc_r1/K5_COVERAGE_MAP_R4.json",
                        "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35"),
    "campaign_A_consumption": ("p5y_k5_lower_front_order3/evidence/tc_r1/TC_CONSUMPTION.json",
                               "1fa8d8dee78483c83d54bd90dba86a9316fb5c67c4acd43781a05103ab111f51"),
    # --- Campaign A adopted TC machinery
    "tc_rule": ("p5y_k5_lower_front_order3/code/tc_rule.py",
                "8d402d11f6fc06ea2af88e3d3a01e376fefbe8ebacd8418f772116010e57afd5"),
    "tc_crosscheck": ("p5y_k5_lower_front_order3/code/tc_crosscheck.py",
                      "1c72117f57197d7dfcf588447510fee43cdb37426ac5f7ca85892b0e10ad8938"),
    "theorem_TC": ("p5y_k5_lower_front_order3/theorem/THEOREM_TC.md", None),
    # --- Campaign B repaired TC-T premise supply and evidence
    "tct_rule": ("p5y_k5_m5_tail_closure/code/tct_rule.py", None),
    "theorem_TCT": ("p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md", None),
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
    # --- adopted Perron / atom machinery (the operator side C1 extends)
    "theorem_AD": ("p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md", None),
    "taboo_certify": ("p5y_k5_perron_deflated_resolvent/code/taboo_certify.py", None),
    "build_registry": ("p5y_k5_perron_deflated_resolvent/code/build_registry.py", None),
    "xcheck_registry": ("p5y_k5_perron_deflated_resolvent/code/xcheck_registry.py", None),
    "falsify_registry": ("p5y_k5_perron_deflated_resolvent/code/falsify_registry.py", None),
    "deflated_consume": ("p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
                         "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72"),
    "registry_r1": ("p5y_k5_perron_deflated_resolvent/evidence/registry_r1/REGISTRY.json",
                    "1b7f5da743a2ce0d7f557c2dae054ab358a9175212eaa1fa29dea63a25780cb5"),
    # --- the frozen consumption chain
    "k5b_check": ("p5y_k5b_independent_countersignature/code/k5b_check.py", None),
    "consumption_adapter": ("p5y_k5b_consumption_adapter/code/consumption_adapter.py",
                            "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"),
    "text_consume": ("p5y_k5_remaining_cell_closure/transport_extension/code/text_consume.py",
                     "657458ade03c4283ae6d5bd97e5567603380bf0e6281d8483f9c1fd45a62d0ea"),
    "cells_json": ("p5y_k1_cover_ledger_successor/config/cells.json",
                   "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"),
    "export_manifest": ("p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
                        "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334"),
}
TAIL = (305, 306, 307, 308, 309)
# every namespace C1 must leave byte-unchanged
IMMUTABLE_NS = ("p5y_k5_lower_front_order3", "p5y_k5_m5_tail_closure", "p5y_k5_perron_deflated_resolvent",
                "p5y_k5b_independent_countersignature", "p5y_k5b_consumption_adapter",
                "p5y_k5_remaining_cell_closure", "p5y_k1_cover_ledger_successor",
                "p5y_k1_cusum_aux5_composite_closure", "p5y_k5_cusum_order3_real_producer",
                "p5y_k1_cusum_aux3_successor", "p5y_k1_cusum_aux5_successor",
                "p5y_k5_cusum_first_real_probe_protocol")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*a, check=True) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=check).stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {"schema": "rebaseguard.p5y.k5.tail-operator-registry.input-verification.v1"}

    # A1 -- git state
    head = git("rev-parse", "HEAD").strip()
    anc = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", FRONTIER, head]).returncode == 0
    dirty = [ln for ln in git("status", "--porcelain", "--untracked-files=all").splitlines() if ln.strip()]
    outside = [p for p in dirty if "p5y_k5_tail_operator_registry" not in p]
    res["A1_git"] = {"head": head, "start_frontier": FRONTIER, "frontier_is_ancestor": anc,
                     "merges_since_frontier": len(git("log", "--merges", "--format=%H", f"{FRONTIER}..{head}").split()),
                     "dirty_outside_C1_namespace": outside,
                     "pass": anc and not outside
                     and not git("log", "--merges", "--format=%H", f"{FRONTIER}..{head}").split()}

    # A2 -- the C1 gate is committed, unmodified, and is an ANCESTOR of HEAD (frozen before this run)
    gate_added = git("log", "--diff-filter=A", "--format=%H", "--", GATE_REL).split()
    gate_commits = git("log", "--format=%H", "--", GATE_REL).split()
    gate_sha_now = sha((REPO / GATE_REL).read_bytes())
    res["A2_gate"] = {"sha256": gate_sha_now, "expected": GATE_SHA, "freeze_commit": gate_added[-1] if gate_added else None,
                      "times_modified_since": len(gate_commits) - 1 if gate_commits else None,
                      "pass": gate_sha_now == GATE_SHA and bool(gate_added) and len(gate_commits) == 1}

    # A3 -- every pinned input
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
    res["A3_pins"] = {"count": len(seen), "mismatch": bad, "inputs": seen, "pass": not bad}

    # A4 -- predecessor namespaces byte-unchanged since the start frontier
    moved = {ns: len(git("diff", "--name-only", FRONTIER, head, "--",
                         f"level4/closure_proofs/{ns}").split()) for ns in IMMUTABLE_NS}
    res["A4_immutability"] = {"changed_files": moved, "pass": all(v == 0 for v in moved.values())}

    # A5 -- the authoritative coverage state is what C1 assumes
    r4 = json.loads((CP / PINS["coverage_map_r4"][0]).read_bytes())
    r5 = [str(p.relative_to(REPO)) for p in REPO.rglob("K5_COVERAGE_MAP_R5.json")]
    res["A5_coverage"] = {"K5_COVERAGE_COMPLETE": r4["K5_COVERAGE_COMPLETE"],
                          "union_open_ranges": r4["union_open_ranges"],
                          "open_per_m": {m: r4["per_m"][m]["open_ranges"] for m in r4["per_m"]},
                          "r5_exists": r5,
                          "pass": r4["K5_COVERAGE_COMPLETE"] is False and r4["union_open_ranges"] == [[305, 309]]
                          and r4["per_m"]["5"]["open_ranges"] == [[305, 309]]
                          and all(r4["per_m"][m]["open_ranges"] == [] for m in ("1", "2", "3")) and not r5}

    # A6 -- Campaign B's baseline, as the frozen C1 gate records it
    fc = json.loads((CP / PINS["tail_forecast_r2"][0]).read_bytes())
    t = fc["routes"]["TCT0"]["scenarios"]["NOMINAL"]["per_m"]["5"]["tail"]
    gate = json.loads((REPO / GATE_REL).read_bytes())
    base = gate["baseline"]
    diffs = []
    for k in TAIL:
        if abs(t[str(k)]["mag_tail"] - base["magnitudes"][str(k)]) > 1e-6:
            diffs.append(f"magnitude {k}")
    acr = fc["atom_constant_requirement"]
    for k in TAIL:
        if abs(acr[str(k)]["uniform_A_reduction_needed"]
               - base["uniform_atom_constant_reduction_still_needed"][str(k)]) > 1e-6:
            diffs.append(f"reduction {k}")
    closed = [k for k in TAIL if t[str(k)]["pass"]]
    res["A6_baseline"] = {"gate_baseline_matches_campaign_B": not diffs, "mismatch": diffs,
                          "campaign_B_closes": closed, "gate_says_closes": base["closes"],
                          "pass": not diffs and closed == base["closes"]}

    # A7 -- registry r1's certified domain really does not reach the tail
    reg = json.loads((CP / PINS["registry_r1"][0]).read_bytes())
    from fractions import Fraction as F
    hi = max(F(b["e_hi"]) for b in reg["blocks"])
    cover = [c for c in json.loads((CP / PINS["cells_json"][0]).read_bytes()) if c["detector"] == "CUSUM"]

    def rat(p):
        return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])
    tail_lo = min(rat({c["index"]: c for c in cover}[k]["left"]) for k in TAIL)
    res["A7_registry_domain"] = {"registry_r1_certified": reg.get("certified"), "rule": reg.get("rule"),
                                 "blocks": len(reg["blocks"]), "max_e_hi": float(hi),
                                 "tail_min_e_lo": float(tail_lo), "gap": float(tail_lo - hi),
                                 "pass": reg.get("certified") is True and reg.get("rule") == "r2" and hi < tail_lo}

    res["ALL_PASS"] = all(v["pass"] for k, v in res.items() if re.fullmatch(r"A\d+_.*", k))
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({k: v["pass"] for k, v in res.items() if re.fullmatch(r"A\d+_.*", k)}
                     | {"ALL_PASS": res["ALL_PASS"], "sha256": sha(data)}))
    return 0 if res["ALL_PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
