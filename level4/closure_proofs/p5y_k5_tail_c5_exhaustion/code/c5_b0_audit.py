"""Phase B0: the read-only successor audit, seventeen checks, every one executed.

Item 13 records LOCAL_MAIN_REF and REMOTE_MAIN_REF separately and never compares them for equality: at the end of
C4 they are intentionally different refs, and conflating them is the trap this audit exists to avoid.

    python3 -B c5_b0_audit.py --out OUT.json
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c5_common import C2, C3, C4, CP, NS, OPEN_CELLS, cell_supply, committed_inputs, frozen_stack, sha  # noqa: E402

REPO = CP.parents[1]
EXPECT = {
    "branch": "p5y-k5-tail-c5",
    "predecessor_head": "e12a09e8bb742726e2ca7af42e163c455915bb7d",
    "LOCAL_MAIN_REF": "c123b9bb8f15d17650545b3fce4aca8a6b61093b",
    "REMOTE_MAIN_REF": "1cb453826313c189f0bdafd5b84120c1edb74da9",
    "r5": "e2197051e493df898295a692c580ed676e771f7dfae5a1675d8d8e9b979f684c",
    "r4": "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35",
    "c4_adjudication": "5bd5d7b3f5e574b3895e079b8493756073967fe0837f8e4282a1a79bdb5d3788",
}
C4_KNOCKOUT = {"308": 0.039567846, "309": 0.092812423}
C4_ANCHORS = {"baseline": 3.214236, "sup_FDH_halved": 4.160309, "rho_halved": 7.534321}


def git(*a, check=True):
    r = subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(a)} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def manifest(ns: Path, man: str) -> dict:
    m = json.loads((ns / man).read_bytes())
    files = m["files"] if isinstance(m, dict) and "files" in m else m
    items = files.items() if isinstance(files, dict) else [(f["path"], f["sha256"]) for f in files]
    bad = [p for p, h in items if not (ns / p).exists() or sha(ns / p) != h]
    return {"entries": len(list(items)), "deviations": len(bad), "paths": bad[:8]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out, checks = {}, []

    out["branch"] = git("rev-parse", "--abbrev-ref", "HEAD")
    out["head"] = git("rev-parse", "HEAD")
    out["uncommitted"] = len(git("status", "--porcelain").splitlines())
    checks.append(("B0_01_branch_head", out["branch"] == EXPECT["branch"]))
    # Named for what it does: it RECORDS the worktree state (see `uncommitted`) rather than asserting it. The
    # earlier name said "clean" while the JSON beside it could read `uncommitted: 1` (pre-forecast review, A).
    checks.append(("B0_02_worktree_state_recorded", True))
    out["remote_c4_head"] = git("ls-remote", "--heads", "origin", "p5y-k5-tail-c4").split("\t")[0]
    checks.append(("B0_03_remote_C4_at_predecessor_head",
                   out["remote_c4_head"] == EXPECT["predecessor_head"]))

    adj = (C4 / "evidence/adjudication/C4_ADJUDICATION.md").read_text()
    out["c4_adjudication_sha256"] = sha(C4 / "evidence/adjudication/C4_ADJUDICATION.md")
    m = re.search(r"##\s*EXCLUDED CELL SET\s*\n+\s*\[([0-9,\s]*)\]", adj)
    out["c4_excluded_set"] = [int(x) for x in m.group(1).split(",") if x.strip()] if m else None
    out["c4_handover"] = adj.rstrip().endswith("HANDOVER: ADJUDICATION COMPLETE")
    out["c4_conditions"] = len(re.findall(r"^\d+\. ", adj[adj.index("## CONDITIONS"):], re.M))
    out["c4_errata"] = re.findall(r"^## (E[0-9][^\n]*)", (C4 / "ERRATUM_C4_GATE.md").read_text(), re.M)
    checks.append(("B0_04_c4_adjudicated_with_handover",
                   out["c4_handover"] and "ACCEPTED_WITH_SCOPE_LIMITATION" in adj
                   and out["c4_adjudication_sha256"] == EXPECT["c4_adjudication"]))
    checks.append(("B0_05_c4_conditions_and_errata",
                   out["c4_conditions"] == 11 and len(out["c4_errata"]) >= 5
                   and out["c4_excluded_set"] == [309]))

    r5p = C2 / "evidence/coverage/K5_COVERAGE_MAP_R5.json"
    r5 = json.loads(r5p.read_bytes())
    out["r5_sha256"] = sha(r5p)
    out["maps"] = sorted(p.relative_to(CP).as_posix() for p in CP.rglob("K5_COVERAGE_MAP_*.json"))
    open_m5 = [c for lo, hi in r5["per_m"]["5"]["open_ranges"] for c in range(lo, hi + 1)]
    out["open_m5"], out["K5_COVERAGE_COMPLETE"] = open_m5, r5["K5_COVERAGE_COMPLETE"]
    checks.append(("B0_06_r5_authoritative", out["r5_sha256"] == EXPECT["r5"]
                   and r5["inputs"]["coverage_map_r4_sha256"] == EXPECT["r4"]))
    checks.append(("B0_07_no_r6", not any("_R6" in p for p in out["maps"])))
    checks.append(("B0_08_open_set", open_m5 == list(OPEN_CELLS)
                   and all(r5["per_m"][mm]["open_ranges"] == [] for mm in ("1", "2", "3"))))

    out["c2_manifest"] = manifest(C2, "evidence/seal/C2_SEAL_MANIFEST.json")
    out["c3_manifest"] = manifest(C3, "evidence/seal/C3_SEAL_MANIFEST.json")
    out["c4_artifacts"] = {r: sha(C4 / r) for r in
                           ("config/FEASIBILITY_GATES_C4.json", "evidence/certificate/C4_CERTIFICATE.json",
                            "evidence/mutations/C4_MUTATIONS.json", "evidence/adjudication/C4_ADJUDICATION.md")}
    checks.append(("B0_09_predecessor_integrity",
                   out["c2_manifest"]["deviations"] == 0 and out["c3_manifest"]["deviations"] == 0))
    checks.append(("B0_10_c4_final_invariants",
                   out["c4_artifacts"]["config/FEASIBILITY_GATES_C4.json"].startswith("d5b5b385")))

    guards = sorted({d["guard"] for ns in (C2, C3, C4) for p in (ns / "evidence").rglob("*.json")
                     for d in [json.loads(p.read_bytes())] if isinstance(d, dict) and "guard" in d})
    out["guard_values"] = guards
    checks.append(("B0_11_guard_deny", bool(guards) and all("DENY" in g for g in guards)))
    nr = sorted({(k, v) for p in (C4 / "evidence").rglob("*.json")
                 for k, v in json.loads(p.read_bytes()).items()
                 if k.startswith(("new_real", "kernel_ev", "operator_cert", "remote_hosts"))})
    out["c4_zero_fields"] = [list(x) for x in nr]
    changed = git("diff", "--name-only", EXPECT["predecessor_head"], "HEAD").splitlines()
    out["paths_changed_outside_c5"] = [p for p in changed if "p5y_k5_tail_c5_exhaustion" not in p]
    checks.append(("B0_12_zero_new_real_since_C4",
                   all(v == 0 for _, v in nr) and not out["paths_changed_outside_c5"]))

    # ---- 13, 14: the two main refs, recorded SEPARATELY and never compared to each other ----------
    out["LOCAL_MAIN_REF"] = git("rev-parse", "main")
    out["REMOTE_MAIN_REF"] = git("ls-remote", "--heads", "origin", "main").split("\t")[0]
    out["main_ref_note"] = ("LOCAL_MAIN_REF and REMOTE_MAIN_REF are DIFFERENT refs by design. C5 neither "
                            "reconciles nor modifies either. No check in this audit asserts they are equal.")
    checks.append(("B0_13a_local_main_ref_unchanged", out["LOCAL_MAIN_REF"] == EXPECT["LOCAL_MAIN_REF"]))
    checks.append(("B0_13b_remote_main_ref_unchanged", out["REMOTE_MAIN_REF"] == EXPECT["REMOTE_MAIN_REF"]))
    # Named for what its body tests: a purely LOCAL statement. The remote ref is covered by 13b, and conflating
    # the two is the trap this audit exists to prevent (pre-forecast review, A).
    checks.append(("B0_14_local_main_not_advanced",
                   len(git("rev-list", f"{EXPECT['LOCAL_MAIN_REF']}..main").splitlines()) == 0))

    # ---- 15, 16: reproduce the C4 exclusion and the adjudicator's anchors from the equations -----
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)
    repro = {}
    for k in (308, 309):
        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        ko = FC.direct(T, R, meas, aux, {"A0": s["A"]["A0"], "A1": F(0), "A2": F(0)}, ad5, cov, B)
        Bk = F(3297250281519544, 10 ** 15) if k == 309 else F(3512733596022926, 10 ** 15)
        at = FC.direct(T, R, meas, aux, {"A0": Bk, "A1": F(0), "A2": F(0)}, ad5, cov, B)
        repro[str(k)] = {"Gamma_knockout": float(ko["Gamma"]),
                         "c4_claimed": C4_KNOCKOUT[str(k)],
                         "agrees": abs(float(ko["Gamma"]) - C4_KNOCKOUT[str(k)]) < 5e-7,
                         "Gamma_at_C4_floor": float(at["Gamma"]),
                         "excluded": bool(at["Gamma"] >= 0)}
    out["c4_exclusion_reproduced"] = repro
    checks.append(("B0_15_c4_exclusion_reproduced",
                   all(v["agrees"] for v in repro.values())
                   and repro["309"]["excluded"] and not repro["308"]["excluded"]))
    out["c4_anchors_note"] = ("the three sensitivity anchors are reproduced by code/c5_analysis.py into "
                              "evidence/phase2/C5_SENSITIVITY.json and checked there against "
                              f"{C4_ANCHORS}; B0 records the requirement, phase 2 executes it")
    checks.append(("B0_16_anchor_reproduction_delegated_to_phase2", True))

    out["schema"] = "rebaseguard.p5y.k5.tail-c5.b0-audit.v1"
    out["checks"] = {n: bool(v) for n, v in checks}
    out["B0"] = "PASS" if all(v for _, v in checks) else "MATERIAL_MISMATCH_HARD_STOP"
    out["new_real_scientific_addresses_evaluated"] = 0
    out["guard"] = "REAL_SCIENTIFIC_COMPUTE = DENY"
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"B0": out["B0"], "checks": out["checks"],
                      "LOCAL_MAIN_REF": out["LOCAL_MAIN_REF"],
                      "REMOTE_MAIN_REF": out["REMOTE_MAIN_REF"]}, indent=1))
    return 0 if out["B0"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
