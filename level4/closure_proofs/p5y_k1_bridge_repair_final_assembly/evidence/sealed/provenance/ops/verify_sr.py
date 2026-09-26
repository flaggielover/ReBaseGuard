"""K1R4 SR bridge: INDEPENDENT post-production verification (read-only; runs outside the repository roots).
Recomputes every record/certificate hash, the T3 consumed-records hash from the sealed patch archive,
the scientific content hash, the T5 chain, every ledger gate in exact rationals, and the SR coverage."""
import gzip, hashlib, json, subprocess, sys
from fractions import Fraction as Fr
from pathlib import Path
R = Path(sys.argv[1])
WT = Path("/home/ubuntu/work/ReBaseGuard-sr-o9-t1")
K4 = WT / "level4/closure_proofs/p5y_k1r4_bridge_successor"
PROD = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2")
sha = lambda b: hashlib.sha256(b).hexdigest()
canon = lambda o: (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()
git = lambda *a: subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout
authz = json.loads((K4 / "config/SR_BRIDGE_AUTHORIZATION.json").read_text())
cp = json.loads((K4 / "config/CHECKPOINT.json").read_text())
table = json.loads((K4 / "config/SR_BRIDGE_CELL_TABLE.json").read_text())
tcells = {c["index"]: c for c in (table["cells"] if isinstance(table, dict) else table)}
TSHA = sha((K4 / "config/SR_BRIDGE_CELL_TABLE.json").read_bytes())
universe = json.loads((K4 / "config/SR_BRIDGE_UNIVERSE.json").read_text())["cells"]
LIVE = PROD / "level4/closure_proofs/p5y_k1_sr_o9_t345_successor/config/live_patches.txt"
live = [tuple(map(int, l.split())) for l in LIVE.read_text().splitlines() if l.strip()]
out = {"run_root": str(R), "cells": {}}
prod = {"k1r4_tree_equals_freeze": git("diff", "--stat", "d9e8f1185c04ee8beb339efff091a073e6ebc21d", "--", str(K4)) == "" and git("status", "--porcelain", "--", str(K4)) == "",
        "checkpoint": sha((K4 / "config/CHECKPOINT.json").read_bytes()) == "9091cb0d5db6cc0a8d233f1667bea78bc69be676b2672f2e47506c453d2a33f0",
        "stages_equal_authorized_identity": all(sha((K4 / "driver" / n).read_bytes()) == h for n, h in authz["identity_body"]["generated_stages"].items()),
        "producer_identity": authz["producer_identity_sha256"] == cp["producer_identity_sha256"] == "6e3713468634fe9fc5952d65aa2fd13f548312e29c6c749e867c55e98abb47b1",
        "authorization": authz["authorization_id"] == "K1R4-SR-BRIDGE-AUTH-001" and authz["cells"] == list(range(2000, 2006)),
        "bridge_table_hash": TSHA == authz["identity_body"]["bridge_table_sha256"],
        "live_patches": len(live) == 3994}
out["producer"] = prod


def ledger_bad(L):
    bad = []
    for k, g in L["top_level_gates"].items():
        if k in ("top_reserve", "total") or "cap" not in g or g.get("usage") in (None, "None"):
            continue
        if not Fr(str(g["usage"])) <= Fr(str(g["cap"])):
            bad.append(f"top:{k}")
    for k, g in L["nested_candidate_gates"].items():
        if k == "B_reserve" or "cap" not in g:
            continue
        if not Fr(str(g["usage"])) <= Fr(str(g["cap"])):
            bad.append(f"nested:{k}")
    if not Fr(L["cover"]["usage"]) <= Fr(L["cover"]["cap"]):
        bad.append("cover")
    lo, hi = Fr(L["target_gate"]["lo"]), Fr(L["target_gate"]["hi"])
    if not (-2 < lo <= hi < 2):
        bad.append("target")
    return bad


total_cpu = 0.0
for s in range(2000, 2006):
    d, c = R / "evidence" / f"sr_{s}", {}
    launch = json.loads((R / "logs" / f"SR_{s}.launch.json").read_text())
    ex = json.loads((R / "logs" / f"SR_{s}.exit.json").read_text())
    files = sorted(p.name for p in d.iterdir())
    c["process_exit_rc0"] = ex["rc"] == 0
    c["exactly_five_files"] = files == [f"cell_done_{s}.json", f"patches_{s}.jsonl.gz", f"t3_{s}.json", f"t4_{s}.json", f"t5_{s}.json"]
    mk = json.loads((d / f"cell_done_{s}.json").read_text())
    rec = tcells[s]
    t3b, t4b, t5b = ((d / f"t{k}_{s}.json").read_bytes() for k in (3, 4, 5))
    t3, t4, t5 = json.loads(t3b), json.loads(t4b), json.loads(t5b)
    c["marker_identity"] = (mk["marker_schema"] == "rebaseguard.p5y.k1.ps1.cell-done-marker.v1" and mk["cell_id"] == s
                            and mk["task_id"] == launch["task_id"] and mk["successor_id"] == rec["id"] and mk["precision_bits"] == 256)
    c["evidence_file_hashes"] = all(sha((d / Path(v["path"]).name).read_bytes()) == v["sha256"] and Path(v["path"]).parent == d
                                    for v in mk["evidence"].values()) and set(mk["evidence"]) == {"t3", "t4", "t5", "patches_gz"}
    c["t3_record_hash_recomputes"] = sha(canon({k: v for k, v in t3.items() if k != "t3_record_sha256"})) == t3["t3_record_sha256"]
    c["t4_record_hash_recomputes"] = sha(canon({k: v for k, v in t4.items() if k != "t4_record_sha256"})) == t4["t4_record_sha256"] and t4["t3_record_sha256"] == t3["t3_record_sha256"]
    # patches: recompute the consumed-records hash from the sealed archive
    recs, n, succ_ok = {}, 0, True
    for line in gzip.decompress((d / f"patches_{s}.jsonl.gz").read_bytes()).decode().splitlines():
        r = json.loads(line); n += 1
        succ_ok &= r["successor_cell"] == s and r["successor_cells_sha256"] == TSHA
        sci = {k: v for k, v in r.items() if k not in ("cpu_seconds", "peak_rss_kib")}
        sci["modes"]["mid"].pop("cache_hits", None), sci["modes"]["mid"].pop("cache_misses", None)
        recs.setdefault(tuple(r["patch"]), sci)
    c["patches_3994_exact_live_set"] = n == 3994 and set(recs) == set(live) and succ_ok
    c["consumed_records_hash_recomputes"] = sha(canon([recs[p] for p in live if p in recs])) == t3["consumed_records_sha256"]
    c["live_patches_hash"] = t3["live_patches_sha256"] == sha(LIVE.read_bytes())
    c["t3_all_checks_true"] = t3["T3_PASS"] is True and all(t3["checks"].values()) and t3["patches"] == 3994 and not any(t3["failures"].values())
    # geometry from the frozen bridge table
    c["geometry_is_bridge_table"] = (t4["C_upper"] == rec["C_upper"] and t4["e0"] == rec["e0"] and t4["rho"] == rec["rho"]
                                     and t3["successor_id"] == rec["id"] and t3["successor_cell_identity"]["e0"] == rec["e0"]
                                     and t4["terminal_cell"] is False and Fr(rec["rho"][1]) == 0)
    # ledgers, exact
    lb = {m: ledger_bad(L) for m, L in t4["m"].items()}
    c["m_universe_exact"] = sorted(int(m) for m in t4["m"]) == [1, 2, 3, 5]
    c["ledger_gates_recheck_exact"] = all(not b for b in lb.values()) and all(L["status"] == "PASS" for L in t4["m"].values())
    # T5: certificate hashes, chain, universe, all gates
    certs = {o["identity"]["obligation_id"]: o for o in t5["obligations"]}
    hashes_ok = all(sha(canon({k: v for k, v in o.items() if k != "certificate_hash"})) == o["certificate_hash"] for o in t5["obligations"])
    chain_ok = all(certs[dep]["certificate_hash"] == h for o in t5["obligations"] for dep, h in o["identity"]["source_certificate_hashes"].items())
    deps_ok = all(set(o["identity"]["dependencies"]) == set(o["identity"]["source_certificate_hashes"]) for o in t5["obligations"])
    uids = sorted(":".join(u) for u in universe[rec["id"]]["units"])
    c["t5_certificate_hashes_recompute"] = hashes_ok
    c["t5_provenance_chain_recomputes"] = chain_ok and deps_ok
    c["t5_obligations_equal_frozen_universe_28"] = sorted(certs) == uids and len(uids) == 28
    c["t5_every_gate_pass"] = all(o["status"] == "PASS" and all(g["PASS"] for g in o["gates"].values()) for o in t5["obligations"])
    evd = t5["obligations"][0]["evidence_sha256"]
    c["t5_binds_t3_t4"] = (evd["t3_record_sha256"] == t3["t3_record_sha256"] and evd["t4_record_sha256"] == t4["t4_record_sha256"]
                           and evd["t3_file_sha256"] == sha(t3b) and evd["t4_file_sha256"] == sha(t4b) and evd["successor_cells_sha256"] == TSHA
                           and evd["task_id"] == launch["task_id"])
    sch = sha(canon({"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
                     "t5_certificate_hashes": [o["certificate_hash"] for o in t5["obligations"]]}))
    c["scientific_content_hash_recomputes"] = sch == mk["scientific_content_hash"]
    c["marker_declares_consistent"] = mk["ok"] is True and mk["t5_status"] == t5["status"] == "T5_28_OF_28_PASS" and mk["pass_count"] == 28
    total_cpu += mk["cpu_seconds"]
    out["cells"][str(s)] = {"PASS": all(c.values()), "checks": c, "id": rec["id"], "left": rec["left"][0], "right": rec["right"][0],
                            "cpu_h": mk["cpu_seconds"] / 3600, "scientific_content_hash": mk["scientific_content_hash"],
                            "B_cover_ratio": mk["B_cover_ratio"], "ledger_recheck_failures": lb,
                            "target": {m: [float(Fr(L["target_gate"]["lo"])), float(Fr(L["target_gate"]["hi"]))] for m, L in t4["m"].items()}}
out["no_unauthorized_records"] = sorted(p.name for p in (R / "evidence").iterdir()) == [f"sr_{s}" for s in range(2000, 2006)]
out["actual_sr_cpu_h"] = total_cpu / 3600
# SR coverage (exact rationals + certified q_SR < c_SR)
from flint import arb, ctx
ctx.prec = 512
c_sr = (arb(4581762885148045) / arb(8796093022208)).log() + arb(1) / 2
q = Fr(33777657, 5000000)
gap = c_sr - arb(q.numerator) / arb(q.denominator)
cells = [out["cells"][str(s)] for s in range(2000, 2006)]
chain = all(Fr(cells[i]["right"]) == Fr(cells[i + 1]["left"]) for i in range(5))
ends = Fr(cells[0]["left"]) == q and Fr(cells[-1]["right"]) == Fr(1883835, 262144)
dc = json.loads((K4 / "config/DOMAIN_COMPOSITION.json").read_text())["SR"]
out["coverage"] = {"historical_compact": "[0, c_SR] (inherited PS1 369-cell PASS)", "bridge": f"[{q}, 1883835/262144]",
                   "far_field": "[1883835/262144, infinity)", "bridge_chain_exact": chain, "bridge_endpoints_exact": ends,
                   "q_SR_below_c_SR_certified": bool(gap > 0), "c_SR_minus_q_SR": str(gap),
                   "overlap": {"interval": "[33777657/5000000, c_SR]", "classification": dc["overlap"]["classification"]},
                   "uncovered_width": "0" if (chain and ends and gap > 0) else "NONZERO",
                   "PASS": chain and ends and bool(gap > 0) and dc["overlap"]["classification"] == "DECLARED_REDUNDANT_CERTIFIED_OVERLAP"}
out["VERIFIED"] = all(prod.values()) and all(v["PASS"] for v in out["cells"].values()) and out["no_unauthorized_records"]
print(json.dumps(out, indent=1, sort_keys=True, default=str))
