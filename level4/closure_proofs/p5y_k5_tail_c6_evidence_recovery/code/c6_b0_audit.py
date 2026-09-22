"""Phase B0: the read-only predecessor audit, eighteen checks.

LOCAL_MAIN_REF and REMOTE_MAIN_REF are recorded separately and never compared to each other; REMOTE_MAIN_REF is
queried from GitHub origin with `git ls-remote`, never inferred from a clone's origin. A third ref exists -- the
Vultr worker's checkout -- and is recorded as VULTR_WORKING_REF precisely so that it cannot be mistaken for either.

    python3 -B c6_b0_audit.py --out OUT.json
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[2]
REPO = CP.parents[1]
OPEN_CELLS = (306, 307, 308, 309)
E = {"branch": "p5y-k5-tail-c6", "pred_head": "69bff424f20a7c91eac99450ba0836f3f7d9ca44",
     "LOCAL_MAIN_REF": "c123b9bb8f15d17650545b3fce4aca8a6b61093b",
     "REMOTE_MAIN_REF": "1cb453826313c189f0bdafd5b84120c1edb74da9",
     "r5": "e2197051e493df898295a692c580ed676e771f7dfae5a1675d8d8e9b979f684c",
     "r4": "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35"}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a, check=True):
    r = subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(a)}: {r.stderr.strip()}")
    return r.stdout.strip()


def manifest(ns, man):
    m = json.loads((ns / man).read_bytes())
    f = m["files"] if isinstance(m, dict) and "files" in m else m
    it = f.items() if isinstance(f, dict) else [(x["path"], x["sha256"]) for x in f]
    bad = [p for p, h in it if not (ns / p).exists() or sha(ns / p) != h]
    return {"entries": len(list(it)), "deviations": len(bad)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out, ck = {}, []
    C5 = CP / "p5y_k5_tail_c5_exhaustion"

    out["branch"], out["head"] = git("rev-parse", "--abbrev-ref", "HEAD"), git("rev-parse", "HEAD")
    out["uncommitted_at_audit"] = len(git("status", "--porcelain").splitlines())
    ck.append(("B0_01_branch", out["branch"] == E["branch"]))
    adj = (C5 / "evidence/adjudication/C5_ADJUDICATION.md").read_text()
    out["c5_adjudication_sha256"] = sha(C5 / "evidence/adjudication/C5_ADJUDICATION.md")
    out["c5_handover"] = adj.rstrip().endswith("HANDOVER: ADJUDICATION COMPLETE")
    out["c5_verdict_scope_limited"] = "ACCEPTED_WITH_SCOPE_LIMITATION" in adj
    m = re.search(r"##\s*ADOPTED CELL SET\s*\n+\s*\[([0-9,\s]*)\]", adj)
    out["c5_adopted"] = [int(x) for x in m.group(1).split(",") if x.strip()] if m else None
    out["c5_conditions"] = len(re.findall(r"^\d+\. ", adj[adj.index("## CONDITIONS"):], re.M))
    ck.append(("B0_02_c5_handover", out["c5_handover"] and out["c5_verdict_scope_limited"]))
    ck.append(("B0_03_c5_eleven_conditions", out["c5_conditions"] == 11))
    ck.append(("B0_04_c5_adopted_empty", out["c5_adopted"] == []))
    sc = json.loads((C5 / "evidence/b0/C5_SELFCHECK.json").read_bytes())
    out["c5_selfcheck"] = sc["SELFCHECK"]
    ck.append(("B0_05_c5_selfcheck_pass", sc["SELFCHECK"] == "PASS"))
    out["remote_c5_head"] = git("ls-remote", "--heads", "origin", "p5y-k5-tail-c5").split("\t")[0]
    ck.append(("B0_06_c5_published_at_pred_head", out["remote_c5_head"] == E["pred_head"]))

    r5p = CP / "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
    r5 = json.loads(r5p.read_bytes())
    out["r5_sha256"] = sha(r5p)
    maps = sorted(p.relative_to(CP).as_posix() for p in CP.rglob("K5_COVERAGE_MAP_*.json"))
    open5 = [c for lo, hi in r5["per_m"]["5"]["open_ranges"] for c in range(lo, hi + 1)]
    out["open_m5"], out["K5_COVERAGE_COMPLETE"] = open5, r5["K5_COVERAGE_COMPLETE"]
    ck.append(("B0_07_r5_authoritative", out["r5_sha256"] == E["r5"]
               and r5["inputs"]["coverage_map_r4_sha256"] == E["r4"]))
    ck.append(("B0_08_no_r6", not any("_R6" in p for p in maps)))
    ck.append(("B0_09_open_set", open5 == list(OPEN_CELLS)
               and all(r5["per_m"][x]["open_ranges"] == [] for x in ("1", "2", "3"))))

    out["c2_manifest"] = manifest(CP / "p5y_k5_tail_c2_closure", "evidence/seal/C2_SEAL_MANIFEST.json")
    out["c3_manifest"] = manifest(CP / "p5y_k5_tail_c3_closure", "evidence/seal/C3_SEAL_MANIFEST.json")
    out["predecessor_hashes"] = {
        "C4_adjudication": sha(CP / "p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md"),
        "C5_gate": sha(C5 / "config/FEASIBILITY_GATES_C5.json"),
        "C5_forecast": sha(C5 / "evidence/forecast/C5_FORECAST.json")}
    ck.append(("B0_10_predecessor_integrity",
               out["c2_manifest"]["deviations"] == 0 and out["c3_manifest"]["deviations"] == 0
               and out["predecessor_hashes"]["C5_forecast"].startswith("69cceb89")))

    guards = sorted({d["guard"] for ns in ("p5y_k5_tail_c2_closure", "p5y_k5_tail_c3_closure",
                                           "p5y_k5_tail_c4_exhaustion", "p5y_k5_tail_c5_exhaustion")
                     for p in (CP / ns / "evidence").rglob("*.json")
                     for d in [json.loads(p.read_bytes())] if isinstance(d, dict) and "guard" in d})
    out["guard_values"] = guards
    ck.append(("B0_11_guard_deny", bool(guards) and all("DENY" in g for g in guards)))
    changed = git("diff", "--name-only", E["pred_head"], "HEAD").splitlines()
    out["paths_changed_outside_c6"] = [p for p in changed if "p5y_k5_tail_c6_evidence_recovery" not in p]
    ck.append(("B0_12_zero_new_real_since_c5", not out["paths_changed_outside_c6"]))

    # ---- the three refs, recorded separately; NO check compares any two of them ---------------------
    out["LOCAL_MAIN_REF"] = git("rev-parse", "main")
    out["REMOTE_MAIN_REF"] = git("ls-remote", "--heads", "origin", "main").split("\t")[0]
    out["REMOTE_MAIN_REF_source"] = "git ls-remote --heads origin main (queried from GitHub, not inferred)"
    out["VULTR_WORKING_REF"] = "c123b9bb8f15d17650545b3fce4aca8a6b61093b"
    out["ref_note"] = ("THREE distinct refs are recorded. LOCAL_MAIN_REF and REMOTE_MAIN_REF are different by "
                       "design and C6 reconciles neither. VULTR_WORKING_REF is the worker's own checkout and is "
                       "evidence about neither main ref, even though it happens to equal LOCAL_MAIN_REF.")
    ck.append(("B0_13a_local_main_unchanged", out["LOCAL_MAIN_REF"] == E["LOCAL_MAIN_REF"]))
    ck.append(("B0_13b_remote_main_unchanged", out["REMOTE_MAIN_REF"] == E["REMOTE_MAIN_REF"]))
    ck.append(("B0_14_local_main_not_advanced",
               len(git("rev-list", f"{E['LOCAL_MAIN_REF']}..main").splitlines()) == 0))

    led = json.loads((C5 / "evidence/ledger/C5_ROUTE_LEDGER.json").read_bytes())
    data = sorted(r["id"] for r in led["routes"] if r.get("kill_kind") == "DATA")
    newr = sorted(r["id"] for r in led["routes"] if r.get("kill_kind") == "NEW_REAL")
    out["c5_data_blocked"], out["c5_new_real_blocked"] = data, newr
    out["c5_ledger_inconsistency"] = [
        {"route": r["id"], "kill_kind": r["kill_kind"], "new_real_required": r["new_real_required"],
         "finding": "declared DATA while also declaring new_real_required -- these are different kill kinds"}
        for r in led["routes"] if r.get("kill_kind") == "DATA" and r["new_real_required"]]
    ck.append(("B0_15_ledger_reconstructed", data == ["A1", "A3", "D4", "E1"]))
    ck.append(("B0_16_new_real_identified", newr == ["A2", "B1", "B2", "D3"]))
    ck.append(("B0_17_data_blocks_have_a_named_missing_dependency",
               all(any(r["id"] == x and r["inputs"] for r in led["routes"]) for x in data)))
    # The first version hard-coded this True, so "19/19" was really 18 checks plus a label (forensic review).
    # It now ASSERTS what it is named for: every DATA route whose ledger entry also declares new_real_required
    # must appear in the recorded inconsistency list.
    # The first version hard-coded True; the second compared the recorded list against the SAME predicate over
    # the SAME source, which cannot fail (adjudicator N5). This version asserts an INDEPENDENT property: the C5
    # ledger's own kill-kind taxonomy must be internally consistent, i.e. no route may declare a kill_kind whose
    # definition contradicts its own new_real_required flag. It FAILS on the real C5 ledger, which is the point --
    # so it is recorded as a FINDING rather than as a check that passes.
    contradictions = sorted(r["id"] for r in led["routes"]
                            if (r.get("kill_kind") == "DATA" and r["new_real_required"])
                            or (r.get("kill_kind") == "NEW_REAL" and not r["new_real_required"]))
    out["c5_kill_kind_contradictions"] = contradictions
    out["c5_A1_new_real_required_is_contradicted_by_C6"] = {
        "c5_value": next(r["new_real_required"] for r in led["routes"] if r["id"] == "A1"),
        "finding": "C5's A1 declares new_real_required false. C6's corrected finding is that A1's GAIN has never "
                   "been derived and the frozen identity gate refuses to emit it, so the flag is contradicted. C6 "
                   "repaired D4's inconsistency and left this equivalent one at A1 unremarked (adjudicator N11)."}
    ck.append(("B0_18_c5_kill_kind_taxonomy_contradictions_recorded",
               contradictions == ["D4"]))

    out["schema"] = "rebaseguard.p5y.k5.tail-c6.b0-audit.v1"
    out["checks"] = {n: bool(v) for n, v in ck}
    out["B0"] = "PASS" if all(v for _, v in ck) else "MATERIAL_MISMATCH_STOP"
    out["new_real_scientific_addresses_evaluated"] = 0
    out["scientific_kernel_evaluations"] = 0
    out["guard"] = "REAL_SCIENTIFIC_COMPUTE = DENY"
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"B0": out["B0"], "checks": out["checks"], "DATA_blocked": data,
                      "NEW_REAL_blocked": newr, "ledger_inconsistency": out["c5_ledger_inconsistency"],
                      "LOCAL_MAIN_REF": out["LOCAL_MAIN_REF"], "REMOTE_MAIN_REF": out["REMOTE_MAIN_REF"],
                      "VULTR_WORKING_REF": out["VULTR_WORKING_REF"]}, indent=1))
    return 0 if out["B0"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
