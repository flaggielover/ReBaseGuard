"""Phase 0: the read-only continuation audit. Twelve checks, every one executed, none transcribed.

Items 11 and 12 re-derive the C3 adjudicator's knockout and critical A0 values from the committed equations
(theorem TC-T -> frozen K5-B direct clause), not from its prose.

    python3 -B c4_phase0_audit.py --out OUT.json
"""
import argparse
import json
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c4_common import C2, C3, CP, NS, OPEN_CELLS, cell_supply, committed_inputs, frozen_stack, gamma_at, sha  # noqa: E402

REPO = CP.parents[1]
EXPECTED = {
    "branch": "p5y-k5-tail-c4", "start_head": "019ecce030ef294b95e98391c71715fb0b43d1cf",
    "main": "c123b9bb8f15d17650545b3fce4aca8a6b61093b",
    "r4_sha256": "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35",
    "r5_sha256": "e2197051e493df898295a692c580ed676e771f7dfae5a1675d8d8e9b979f684c",
    "c3_adjudication_sha256": "71b50f6aca9f6f014051685d0446fd9e0013e065640f719d9d35df50bf72088d",
}


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=True).stdout.strip()


def manifest_ok(ns: Path, man: str) -> dict:
    m = json.loads((ns / man).read_bytes())
    files = m["files"] if isinstance(m, dict) and "files" in m else m
    items = files.items() if isinstance(files, dict) else [(f["path"], f["sha256"]) for f in files]
    bad = [p for p, h in items if not (ns / p).exists() or sha(ns / p) != h]
    return {"entries": len(list(items)), "deviations": len(bad), "deviating_paths": bad[:10]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    checks, out = [], {}

    # ---- 1. branch / HEAD / clean tree -------------------------------------------------------------
    branch, head = git("rev-parse", "--abbrev-ref", "HEAD"), git("rev-parse", "HEAD")
    dirty = git("status", "--porcelain")
    out["branch"], out["head"] = branch, head
    checks.append(("1_branch_head_clean", branch == EXPECTED["branch"]
                   and git("rev-parse", EXPECTED["start_head"]) == EXPECTED["start_head"]
                   and git("merge-base", "--is-ancestor", EXPECTED["start_head"], "HEAD") == ""))

    # ---- 2, 3. C3 verdict and adopted set, parsed from the adjudication document -------------------
    adj = (C3 / "evidence/adjudication/C3_ADJUDICATION.md").read_text()
    out["c3_adjudication_sha256"] = sha(C3 / "evidence/adjudication/C3_ADJUDICATION.md")
    import re
    verdict_rejected = bool(re.search(r"\*\*VERDICT:\s*REJECTED", adj))
    m = re.search(r"##\s*ADOPTED CELL SET\s*\n+\s*\[([0-9,\s]*)\]", adj)
    adopted_set = [int(x) for x in m.group(1).split(",") if x.strip()] if m else None
    out["c3_verdict_rejected"], out["c3_adopted_set"] = verdict_rejected, adopted_set
    checks.append(("2_c3_rejected", verdict_rejected
                   and out["c3_adjudication_sha256"] == EXPECTED["c3_adjudication_sha256"]))
    checks.append(("3_adopted_set_empty", adopted_set == []))

    # ---- 4, 5, 6. r5 authoritative, no r6, open set ------------------------------------------------
    r5p = C2 / "evidence/coverage/K5_COVERAGE_MAP_R5.json"
    r5 = json.loads(r5p.read_bytes())
    out["r5_sha256"] = sha(r5p)
    maps = sorted(p.relative_to(CP).as_posix() for p in CP.rglob("K5_COVERAGE_MAP_*.json"))
    out["coverage_maps_present"] = maps
    checks.append(("4_r5_authoritative", out["r5_sha256"] == EXPECTED["r5_sha256"]
                   and r5["inputs"]["coverage_map_r4_sha256"] == EXPECTED["r4_sha256"]))
    checks.append(("5_no_r6", not any("_R6" in p for p in maps)))
    open_m5 = [c for lo, hi in r5["per_m"]["5"]["open_ranges"] for c in range(lo, hi + 1)]
    out["open_m5"], out["K5_COVERAGE_COMPLETE"] = open_m5, r5["K5_COVERAGE_COMPLETE"]
    out["open_m1_m2_m3"] = {m: r5["per_m"][m]["open_ranges"] for m in ("1", "2", "3")}
    checks.append(("6_open_set", open_m5 == list(OPEN_CELLS)
                   and all(r5["per_m"][m]["open_ranges"] == [] for m in ("1", "2", "3"))))

    # ---- 7. C2 and C3 namespaces byte-intact against their own sealed manifests --------------------
    out["c2_manifest"] = manifest_ok(C2, "evidence/seal/C2_SEAL_MANIFEST.json")
    out["c3_manifest"] = manifest_ok(C3, "evidence/seal/C3_SEAL_MANIFEST.json")
    checks.append(("7_namespaces_intact",
                   out["c2_manifest"]["deviations"] == 0 and out["c3_manifest"]["deviations"] == 0))

    # ---- 8. main untouched -------------------------------------------------------------------------
    out["main"] = git("rev-parse", "main")
    checks.append(("8_main_untouched", out["main"] == EXPECTED["main"]
                   and git("merge-base", "--is-ancestor", "main", "HEAD") == ""))

    # ---- 9, 10. guard and zero new-real since C3 ---------------------------------------------------
    guards = sorted({v for p in (C3 / "evidence").rglob("*.json")
                     for v in [json.loads(p.read_bytes()).get("guard")] if v})
    newreal = sorted({(k, v) for p in (C3 / "evidence").rglob("*.json")
                      for k, v in json.loads(p.read_bytes()).items() if k.startswith("new_real")})
    out["c3_guard_values"], out["c3_new_real_fields"] = guards, [list(x) for x in newreal]
    checks.append(("9_guard_deny", bool(guards) and all("DENY" in g for g in guards)))
    changed = git("diff", "--name-only", "ae4cbc2c", "HEAD").splitlines()
    out["paths_changed_since_c3_start_outside_c3_ns"] = [p for p in changed if "p5y_k5_tail_c3_closure" not in p]
    checks.append(("10_zero_new_real", all(v == 0 for _, v in newreal)
                   and not out["paths_changed_since_c3_start_outside_c3_ns"]))

    # ---- 11, 12. the knockout and the critical A0, re-derived from the equations -------------------
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)
    per = {}
    for k in OPEN_CELLS:
        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        A = s["A"]
        full = gamma_at(FC, T, R, B, meas, aux, ad5, cov, A["A0"], A["A1"], A["A2"])
        ko = gamma_at(FC, T, R, B, meas, aux, ad5, cov, A["A0"], 0, 0)
        crit = None
        if not ko["pass"]:                       # bisect the A1 = A2 = 0 critical A0 (Gamma is nondecreasing in A0)
            lo, hi = F(0), A["A0"]
            if gamma_at(FC, T, R, B, meas, aux, ad5, cov, lo, 0, 0)["pass"]:
                for _ in range(220):
                    mid = (lo + hi) / 2
                    if gamma_at(FC, T, R, B, meas, aux, ad5, cov, mid, 0, 0)["pass"]:
                        lo = mid
                    else:
                        hi = mid
                crit = {"closes_below": str(lo), "open_at_or_above": str(hi),
                        "float_lo": float(lo), "float_hi": float(hi),
                        "A0_reduction_factor_needed": float(A["A0"] / lo)}
        per[str(k)] = {"A0_certified": float(A["A0"]), "A1_certified": float(A["A1"]),
                       "A2_certified": float(A["A2"]),
                       "Gamma_mixed": float(full["Gamma"]), "closes_mixed": bool(full["pass"]),
                       "Gamma_A1A2_zero": float(ko["Gamma"]), "closes_A1A2_zero": bool(ko["pass"]),
                       "critical_A0_A1A2_zero": crit}
    out["knockout"] = per
    # the adjudicator's published figures, as the thing being reproduced
    adj_fig = {"308": {"Gamma_A1A2_zero": 0.039568, "critical_A0": 4.3752},
               "309": {"Gamma_A1A2_zero": 0.092812, "critical_A0": 3.2142}}
    ok11 = all(not per[k]["closes_A1A2_zero"] and abs(per[k]["Gamma_A1A2_zero"] - v["Gamma_A1A2_zero"]) < 5e-7
               for k, v in adj_fig.items())
    ok12 = all(abs(per[k]["critical_A0_A1A2_zero"]["float_lo"] - v["critical_A0"]) < 5e-5
               for k, v in adj_fig.items())
    checks.append(("11_knockout_reproduced", ok11))
    checks.append(("12_critical_A0_reproduced", ok12))

    out["schema"] = "rebaseguard.p5y.k5.tail-c4.phase0-audit.v1"
    out["checks"] = {n: bool(v) for n, v in checks}
    out["PHASE0"] = "PASS" if all(v for _, v in checks) else "MATERIAL_MISMATCH_STOP"
    out["new_real_scientific_addresses_evaluated"] = 0
    out["guard"] = "REAL_SCIENTIFIC_COMPUTE = DENY"
    out["uncommitted_files_at_audit"] = len(dirty.splitlines())
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"PHASE0": out["PHASE0"], "checks": out["checks"]}, indent=1))
    return 0 if out["PHASE0"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
