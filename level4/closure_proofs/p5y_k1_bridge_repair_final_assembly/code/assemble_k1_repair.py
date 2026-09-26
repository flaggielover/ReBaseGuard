"""P5Y K1 bridge-repair FINAL ASSEMBLY (additive). Binds inherited and new evidence; decides NOTHING about K1.

Output: evidence/K1_REPAIR_ASSEMBLY.json. It may set READY_FOR_INDEPENDENT_K1_SUCCESSOR_ADJUDICATION = YES only if
every gate passes. It never declares K1 CLOSED and never modifies historical adjudication (P5 / P5X / P5Y-K1 stay PARTIAL).
Sealed production evidence (markers, T3/T4/T5, CUSUM records, verification reports, launch/exit records) is copied
byte-for-byte into evidence/sealed/; the SR patch archives (~30 MB) stay external and are bound by SHA-256.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
WT = NS.parents[2]
REPO = Path("/home/ubuntu/work/ReBaseGuard")
PRODB = Path("/home/ubuntu/work/k1-bridge-prod")
SR_RUN = PRODB / "run-20260926T075918Z"
CU_RUN = PRODB / "run-k1r6-20260926T125551Z"
AUX4 = REPO / "level4/closure_proofs/p5y_k1_cusum_aux4_fullcover"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()           # noqa: E731
j = lambda p: json.loads(Path(p).read_text())                                # noqa: E731
git = lambda *a: subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout  # noqa: E731
G = []


def gate(name, ok, **detail):
    G.append({"gate": name, "status": "PASS" if ok else "FAIL", **detail})
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    return ok


FREEZES = {"p5y_k1r_successor": "adad61f",          # final committed record (freeze 7f671b9 + B1/halt evidence)
           "p5y_k1r2_bridge_executor": "b258c18",
           "p5y_k1r4_bridge_successor": "d9e8f1185c04ee8beb339efff091a073e6ebc21d",
           "p5y_k1r5_cusum_entry": "0cd4e8dd36615971745eb37c00197d735723cc82",
           "p5y_k1r6_cusum_bridge_repair": "3e9f3dcf8b98b23e41097aae2ec2f07484946a32",
           "p5y_k1_ps1_aws_only_assembly": "15e70072"}


def main() -> int:
    ev = NS / "evidence"
    sealed = ev / "sealed"
    if sealed.exists():
        raise SystemExit("evidence/sealed already exists: assembly is write-once")
    print("P5Y K1 bridge-repair final assembly")
    # ---------------------------------------------------------------- inherited
    b1p = CP / "p5y_k1r_successor/evidence/B1_ADMISSION_RESULT.json"
    b1 = j(b1p)
    gate("A1 inherited B1 PASS (Aux5 composite admission; 1304/1304; blocker cells 319-323 m=5 PASS)",
         sha(b1p) == "41fd34c6ede08b358c9b897f82662e9dd258d3c1619464a47e7f568ebf9f37bb" and b1["all_a1_a10"] == "PASS"
         and b1["g_aux5_status_gate"]["verdict"] == "CLEAR" and b1["g_aux5_status_gate"]["non_pass_count"] == 0
         and b1["g_aux5_status_gate"]["obligations_evaluated"] == 1304, sha256=sha(b1p))
    recs = {}
    for p in sorted((AUX4 / "diagnostics/cells").glob("aux4_CUSUM_*_256.json")):
        r = j(p)
        recs[r["cell_index"]] = r
    iv = sorted((Fr(r["e0"][0]) - Fr(r["rho"][0]), Fr(r["e0"][0]) + Fr(r["rho"][0])) for r in recs.values())
    tile = sorted(recs) == list(range(326)) and iv[0][0] == 0 and iv[-1][1] == Fr(11, 2) and all(iv[k][1] == iv[k + 1][0] for k in range(325))
    gate("A2 historical CUSUM compact [0, 11/2]: 326 cells tile exactly (aux4 fullcover geometry); admitted status from B1 (A1)",
         tile, cells=len(recs), span=[str(iv[0][0]), str(iv[-1][1])])
    ps1p = CP / "p5y_k1_ps1_aws_only_assembly/evidence/FINAL_ASSEMBLY.json"
    ps1 = j(ps1p)
    gate("A3 historical SR compact [0, c_SR]: PS1 generation-2 AWS-only assembly 369/369 cells, 10332 obligations",
         sha(ps1p) == "a3ffb9ec89b1c2da255e7d7397399720d3045f53c9d12b1ffba4141c81369860" and ps1["cells_completed"] == 369
         and ps1["obligations_completed"] == 10332 and ps1["pending"] == 0 and ps1["unique_cell_coverage"] is True, sha256=sha(ps1p))
    dcov = CP / "p5y_k1r_successor/config/DOMAIN_COVER.json"
    k1rcp = j(CP / "p5y_k1r_successor/config/CHECKPOINT.json")
    ff_ok = all(s["status"] == "INHERITED_PASS_AT_AND_ABOVE_e_close" for det in j(dcov)["detectors"].values()
                for s in det["segments"] if s["segment"] == "FAR_FIELD_INHERITED")
    bound = any(h == sha(dcov) for h in json.dumps(k1rcp).split('"') if len(h) == 64)
    gate("A4 inherited far field [e_close, infinity) for CUSUM and SR: P5X-T3 (frozen K1R DOMAIN_COVER, checkpoint-bound)",
         ff_ok and bound, domain_cover_sha256=sha(dcov), theorem=j(dcov)["far_field_theorem"])
    # ---------------------------------------------------------------- new genuine evidence
    vsr = j(SR_RUN / "VERIFICATION_SR.json")
    vcu = j(CU_RUN / "VERIFICATION_K1R6.json")
    gate("A5 K1R4 SR bridge 6/6 genuine cells independently verified (20/20 checks each), producer/authorization bound",
         vsr["VERIFIED"] is True and len(vsr["cells"]) == 6 and all(c["PASS"] for c in vsr["cells"].values())
         and all(vsr["producer"].values()) and vsr["no_unauthorized_records"], verification_sha256=sha(SR_RUN / "VERIFICATION_SR.json"))
    gate("A6 K1R6 CUSUM bridge 2/2 genuine cells independently verified (22/22 checks each)",
         vcu["VERIFIED"] is True and len(vcu["cells"]) == 2 and all(c["PASS"] for c in vcu["cells"].values())
         and vcu["no_unauthorized_records"], verification_sha256=sha(CU_RUN / "VERIFICATION_K1R6.json"))
    # ---------------------------------------------------------------- copy sealed evidence byte-for-byte
    copied, external = {}, {}
    for s in range(2000, 2006):
        d = SR_RUN / "evidence" / f"sr_{s}"
        mk = j(d / f"cell_done_{s}.json")
        for n in (f"cell_done_{s}.json", f"t3_{s}.json", f"t4_{s}.json", f"t5_{s}.json"):
            dst = sealed / "sr" / f"sr_{s}" / n
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(d / n, dst)
            copied[str(dst.relative_to(NS))] = sha(dst)
        gz = d / f"patches_{s}.jsonl.gz"
        external[str(gz)] = {"sha256": sha(gz), "bytes": gz.stat().st_size, "marker_sha256": mk["evidence"]["patches_gz"]["sha256"]}
    for i in (1000, 1001):
        d = CU_RUN / "evidence" / f"cusum_{i}"
        for n in (f"cell_done_{i}.json", f"k1r6_CUSUM_{i}_256.json"):
            dst = sealed / "cusum" / f"cusum_{i}" / n
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(d / n, dst)
            copied[str(dst.relative_to(NS))] = sha(dst)
    prov = {SR_RUN: ["VERIFICATION_SR.json", "CUSUM_HALT.json"] + [f"logs/SR_{s}.{k}.json" for s in range(2000, 2006) for k in ("launch", "exit")]
            + [f"logs/CUSUM_{i}.{k}.json" for i in (1000, 1001) for k in ("launch", "exit")],
            CU_RUN: ["VERIFICATION_K1R6.json"] + [f"logs/CUSUM_{i}.{k}.json" for i in (1000, 1001) for k in ("launch", "exit")],
            PRODB: ["phase0.py", "phase0_sr.json", "phase0_cusum.json", "phase0_k1r6.py", "phase0_k1r6_20260926T125551Z.json",
                    "cell.sh", "cell_k1r6.sh", "verify_sr.py", "verify_k1r6.py"]}
    for root, names in prov.items():
        tag = {SR_RUN: "run_sr_and_k1r5", CU_RUN: "run_k1r6", PRODB: "ops"}[root]
        for n in names:
            dst = sealed / "provenance" / tag / n
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / n, dst)
            copied[str(dst.relative_to(NS))] = sha(dst)
    ok_copy = all(v["sha256"] == v["marker_sha256"] for v in external.values())
    for s in range(2000, 2006):
        mk = j(sealed / "sr" / f"sr_{s}" / f"cell_done_{s}.json")
        ok_copy &= all(copied[f"evidence/sealed/sr/sr_{s}/{Path(v['path']).name}"] == v["sha256"] for k, v in mk["evidence"].items() if k != "patches_gz")
    for i in (1000, 1001):
        mk = j(sealed / "cusum" / f"cusum_{i}" / f"cell_done_{i}.json")
        ok_copy &= copied[f"evidence/sealed/cusum/cusum_{i}/k1r6_CUSUM_{i}_256.json"] == mk["record_sha256"]
    gate("A7 sealed evidence copied byte-for-byte (hashes equal the seals); SR patch archives bound by SHA-256",
         ok_copy, copied=len(copied), external=len(external))
    # ---------------------------------------------------------------- domain composition
    cov_c, cov_s = vcu["coverage"], vsr["coverage"]
    comp = {"CUSUM": {"historical_compact": "[0, 11/2]", "bridge": cov_c["bridge"], "far_field": cov_c["far_field"],
                      "union": cov_c["union"], "uncovered_domain_width": cov_c["uncovered_width"], "overlap": "none (exact rational splices)"},
            "SR": {"historical_compact": "[0, c_SR], c_SR = log(4581762885148045/8796093022208) + 1/2", "bridge": cov_s["bridge"],
                   "far_field": cov_s["far_field"], "union": "[0, infinity)", "uncovered_domain_width": cov_s["uncovered_width"],
                   "overlap": cov_s["overlap"], "c_SR_minus_q_SR": cov_s["c_SR_minus_q_SR"]}}
    gate("A8 exact final domain composition: CUSUM and SR unions = [0, infinity), uncovered width 0; SR overlap "
         "[q_SR, c_SR] DECLARED_REDUNDANT_CERTIFIED_OVERLAP with q_SR < c_SR certified",
         cov_c["PASS"] is True and cov_s["PASS"] is True and cov_c["uncovered_width"] == cov_s["uncovered_width"] == "0"
         and cov_s["q_SR_below_c_SR_certified"] is True and comp["SR"]["overlap"]["classification"] == "DECLARED_REDUNDANT_CERTIFIED_OVERLAP")
    # ---------------------------------------------------------------- identities / cost / immutability
    k4a = j(CP / "p5y_k1r4_bridge_successor/config/SR_BRIDGE_AUTHORIZATION.json")
    k6i = j(CP / "p5y_k1r6_cusum_bridge_repair/config/PRODUCER_IDENTITY.json")
    k4rt = j(CP / "p5y_k1r4_bridge_successor/config/RUNTIME_CONTRACT.json")["SR_BRIDGE"]
    idents = {"K1R4_SR": {"producer": "K1R4-SR-BRIDGE-PRODUCER", "producer_identity_sha256": k4a["producer_identity_sha256"],
                          "authorization": k4a["authorization_id"], "checkpoint": (CP / "p5y_k1r4_bridge_successor/config/CHECKPOINT_HASH").read_text().strip(),
                          "runtime": {k: k4rt[k] for k in ("host", "sys_vendor", "python", "python_flint", "precision_bits", "threads")}},
              "K1R6_CUSUM": {"producer": k6i["producer"], "producer_identity_hash": k6i["producer_identity_hash"],
                             "runtime_contract_hash": k6i["runtime_contract_hash"],
                             "checkpoint": (CP / "p5y_k1r6_cusum_bridge_repair/config/CHECKPOINT_HASH").read_text().strip(),
                             "authorization": "operator EXECUTION instruction 2026-09-26 (K1R6 launch)"},
              "B1_AUX5": {"frozen_contract_sha256": b1["frozen_contract_sha256"], "k1r_freeze": b1["k1r_freeze_commit"]},
              "PS1": {"assembly_sha256": ps1["assembly_sha256"], "route": ps1["route"]}}
    gate("A9 producer identities, authorizations and runtime identities bound",
         idents["K1R4_SR"]["producer_identity_sha256"] == "6e3713468634fe9fc5952d65aa2fd13f548312e29c6c749e867c55e98abb47b1"
         and idents["K1R4_SR"]["authorization"] == "K1R4-SR-BRIDGE-AUTH-001"
         and idents["K1R6_CUSUM"]["producer_identity_hash"] == "3527b3b9399c12b406217c72548264293f11b8f14f1250f5cede138e7ba84671"
         and all(c["checks"]["producer_identity"] for c in vcu["cells"].values()) and k4rt["sys_vendor"] == "Amazon EC2")
    sr_h = sum(c["cpu_h"] for c in vsr["cells"].values())
    cu_h = sum(c["cpu_h"] for c in vcu["cells"].values())
    cost = {"K1R4_SR_committed_cpu_h": round(sr_h, 4), "K1R6_CUSUM_committed_cpu_h": round(cu_h, 4),
            "K1R5_consumed_unsealed_cpu_h": 0.61, "K1R_K1R2_K1R3_cpu_h": 0.0,
            "total_genuine_repair_cpu_h": round(sr_h + cu_h + 0.61, 4), "cap_cpu_h_shared": 150.0,
            "accounting": "committed CPU-h from sealed markers' cpu_seconds; unsealed K1R5 consumption carried forward; "
                          "qualification/verification runs are non-genuine and excluded"}
    gate("A10 CPU accounting within the shared cap (never raised)", cost["total_genuine_repair_cpu_h"] <= 150.0, **cost)
    diff = git("diff", "--name-only", "HEAD").split() + [l[3:] for l in git("status", "--porcelain").splitlines() if not l[3:].startswith(str(NS.relative_to(WT)))]
    frozen_ok = all(git("diff", "--stat", rev, "--", str(CP / d)) == "" for d, rev in FREEZES.items())
    frozen_ok &= git("diff", "--stat", "7f671b9ba2d7111b5e8cde010bc660904925fa1c", "--", str(CP / "p5y_k1r_successor/config")) == ""
    gate("A11 historical states immutable: no tracked file changed; K1R/K1R2/K1R4/K1R5/K1R6/PS1-assembly namespaces equal their final committed records (K1R config == its freeze)",
         diff == [] and frozen_ok, changed=diff)
    # ---------------------------------------------------------------- assemble
    ready = all(g["status"] == "PASS" for g in G)
    body = {"schema": "rebaseguard.p5y.k1.bridge-repair.final-assembly.v1",
            "gates": G, "gates_passed": sum(g["status"] == "PASS" for g in G), "gates_total": len(G),
            "domain_composition": comp, "identities": idents, "cpu_accounting": cost,
            "cells": {"SR_bridge": {s: {k: c[k] for k in ("id", "left", "right", "cpu_h", "scientific_content_hash")} for s, c in vsr["cells"].items()},
                      "CUSUM_bridge": {i: {k: c[k] for k in ("record_sha256", "scientific_content_hash", "cpu_h", "zero_case_count", "zero_case_by_object_part")}
                                       for i, c in vcu["cells"].items()}},
            "sealed_copies": copied, "external_bound": external,
            "notes": ["CUSUM bridge records carry result_bearing=False: text inherited from the aux4 qualification harness "
                      "(K1R5/K1R6 assemble() constant), NOT a scientific verdict; scientific status is the independently "
                      "re-verified ledgers and certificates (A6).",
                      "K1R6 frozen campaign label is 'p5y_k1r6_cusum_entry' (mechanical rename of the K1R5 label).",
                      "CUSUM 1001: 8 zero-case firings, all on F_4 (candidate and source both exactly zero); exact [0,0], hashed."],
            "historical": {"P5": "PARTIAL", "P5X": "PARTIAL", "P5Y_K1": "PARTIAL", "modified": False},
            "k1_status": "NOT_DECIDED_HERE: producer assembly is not scientific adjudication",
            "READY_FOR_INDEPENDENT_K1_SUCCESSOR_ADJUDICATION": "YES" if ready else "NO"}
    body["assembly_sha256"] = hashlib.sha256((json.dumps(body, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
    (ev / "K1_REPAIR_ASSEMBLY.json").write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    print(f"\n{body['gates_passed']}/{body['gates_total']} gates; READY_FOR_INDEPENDENT_K1_SUCCESSOR_ADJUDICATION = "
          f"{body['READY_FOR_INDEPENDENT_K1_SUCCESSOR_ADJUDICATION']}; assembly_sha256 {body['assembly_sha256']}")
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
