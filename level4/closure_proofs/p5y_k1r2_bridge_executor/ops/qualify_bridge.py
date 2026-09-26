"""K1R2 bridge qualification. NON-DECISIVE: resolves cells, binds identity, runs no science.

It never constructs a certifier, never computes an obligation and never reads a historical
result status.
"""
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
ROOT = Path("/home/ubuntu/work/ReBaseGuard")
PROD = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2")
PS1 = PROD / "level4/closure_proofs/p5y_k1_ps1_production"
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"
OUT = []
# Scientific RESULT fields. A governance "status" string (a host being unqualified, a
# handoff being unused, B1's inherited verdict) is not a scientific result and is allowed.
FORBIDDEN_RESULT_FIELDS = ("statuses", "pass_count", "failing_m", "utilization",
                           "worst_top_level_utilization", "R_interval", "R_interval_mag",
                           "M_R2", "certificate_hash", "scientific_content_hash",
                           "obligations_completed", "target_gate", "top_level_gates")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def j(name):
    return json.loads((CFG / name).read_text())


def rec(name, ok, detail=""):
    OUT.append({"check": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" -- {detail}" if detail else ""))
    return ok


def resolve(table, index):
    """The bridge resolver: bridge indices only, historical indices refused."""
    lo, hi = table["historical_index_range_refused"]
    if lo <= index <= hi:
        raise LookupError(f"cell {index} is a historical cell: inherited evidence, never new work")
    hits = [c for c in table["cells"] if c["index"] == index]
    if not hits:
        raise LookupError(f"cell {index} is not in the K1R2 bridge cover")
    return hits[0]


def main() -> int:
    cp, ck = j("CHECKPOINT.json"), j("CUSUM_BRIDGE_CHECKPOINT.json")
    rec("checkpoint hash file matches", sha(CFG / "CHECKPOINT.json")
        == (CFG / "CHECKPOINT_HASH").read_text().strip())
    rec("every frozen artifact is bound by the checkpoint",
        all(sha(CFG / n) == h for n, h in cp["frozen_artifacts"].items()),
        f"{len(cp['frozen_artifacts'])} artifacts")

    cu, sr = j("CUSUM_BRIDGE_CELL_TABLE.json"), j("SR_BRIDGE_CELL_TABLE.json")
    # ---- CUSUM: resolves exactly the two bridge cells, nothing else
    got = []
    for i in (1000, 1001):
        got.append(resolve(cu, i)["index"])
    refused = 0
    for bad in (0, 319, 325, 999, 1002, 2000):
        try:
            resolve(cu, bad)
        except LookupError:
            refused += 1
    rec("CUSUM bridge resolves exactly its 2 cells", got == [1000, 1001] and refused == 6,
        f"resolved {got}, refused 6/6 non-bridge indices incl. historical 0/319/325")
    rec("CUSUM endpoints are the frozen K1R intervals",
        Fr(cu["cells"][0]["left"]) == Fr(11, 2)
        and Fr(cu["cells"][0]["right"]) == Fr(95887899, 16777216)
        and Fr(cu["cells"][1]["left"]) == Fr(95887899, 16777216)
        and Fr(cu["cells"][1]["right"]) == Fr(49750555, 8388608))
    rec("CUSUM bridge table hash bound into producer contract and checkpoint",
        j("CUSUM_BRIDGE_PRODUCER_CONTRACT.json")["cell_table_sha256"]
        == sha(CFG / "CUSUM_BRIDGE_CELL_TABLE.json")
        == ck["geometry"]["cells_sha256"])

    # ---- scientific kernel identity: byte-identical to the qualified lineage
    ker = j("CUSUM_BRIDGE_PRODUCER_CONTRACT.json")["scientific_kernel"]
    drift = [n for n, m in ker["modules"].items() if sha(ROOT / m["path"]) != m["sha256"]]
    rec("CUSUM scientific kernel byte-identical to the bound modules", not drift,
        f"{ker['module_count']} modules, drift {drift}")
    digest = hashlib.sha256(json.dumps({k: v["sha256"] for k, v in sorted(ker["modules"].items())},
                                       sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    rec("kernel identity digest recomputes", digest == ker["kernel_identity_sha256"]
        == ck["kernel_identity_sha256"] == j("RUNTIME_CONTRACT.json")["kernel_identity_sha256"])
    rec("frozen cover spec untouched",
        sha(SPEC_NS / "config/cells.json") == ker["frozen_spec_cells_sha256"]
        and sha(SPEC_NS / "config/checkpoint.json") == ker["frozen_spec_checkpoint_sha256"]
        and sha(SPEC_NS / "config/record_schema.json") == ker["frozen_spec_record_schema_sha256"])
    hist = json.loads((SPEC_NS / "config/cells.json").read_text())
    hist = hist if isinstance(hist, list) else hist["cells"]
    ref = next(c for c in hist if c.get("detector") == "CUSUM" and c.get("index") == 325)
    bridge_keys = set(ref) - {"index"} | {"index"}
    rec("bridge cell entries carry every frozen geometry field",
        all(bridge_keys <= set(c) for c in cu["cells"]),
        f"frozen fields {sorted(bridge_keys)}")

    # ---- SR: ownership, topology, executor identity, schema
    own = j("SR_BRIDGE_OWNERSHIP.json")
    ids = [c["index"] for c in sr["cells"]]
    rec("SR bridge resolves exactly its 6 cells",
        [resolve(sr, i)["index"] for i in ids] == ids == [2000, 2001, 2002, 2003, 2004, 2005])
    srefused = 0
    for bad in (0, 368, 1000, 2006):
        try:
            resolve(sr, bad)
        except LookupError:
            srefused += 1
    rec("SR refuses historical PS1 ids and non-bridge ids as new work", srefused == 4)
    rec("SR ownership map is bridge-only and AWS-only",
        sorted(int(k) for k in own["owners"]) == ids
        and set(own["owners"].values()) == {"AWS"})
    auth = j("SR_BRIDGE_AUTHORIZATION.json")
    rec("SR authorization is AWS-only with no Vultr and no handoff",
        auth["topology"] == "A_AWS_ONLY" and auth["hosts"]["VULTR"]["cells"] == []
        and auth["hosts"]["VULTR"]["substitution"] == "PROHIBITED"
        and auth["handoff"]["public_key_fingerprint"] is None
        and auth["synthetic_path"] == "PROHIBITED")
    ps1auth = json.loads((PS1 / "config/LAUNCH_AUTHORIZATION.json").read_text())
    exdrift = [f for f in ps1auth["executor_source_manifest"]
               if sha(PROD / f) != ps1auth["executor_source_sha256"][f]]
    x = auth["scientific_executor"]
    rec("SR scientific executor byte-identical to the qualified PS1 lineage", not exdrift
        and x["source_manifest_files"] == len(ps1auth["executor_source_manifest"])
        and x["scientific_adapter_hash"] == ps1auth["scientific_adapter_hash"]
        and x["producer_commit"] == ps1auth["producer_commit"]
        and x["checkpoint_sha256"] == ps1auth["checkpoint_sha256"],
        f"{x['source_manifest_files']} files, drift {exdrift}")
    rec("historical PS1 evidence is inherited-only and unmodified",
        auth["historical_ps1"]["resolvable_as_new_work"] is False
        and auth["historical_ps1"]["modification"] == "PROHIBITED"
        and auth["historical_ps1"]["production_ledger_sha256"]
        == sha(PS1 / "production/PRODUCTION_LEDGER.json"))

    # ---- inherited science unchanged, and nothing decisive present
    inh = cp["inherited_unchanged"]
    rec("inherited science unchanged from K1R",
        inh["m_universe"] == [1, 2, 3, 5] and inh["target"] == "2/1"
        and inh["precision_bits"] == 256 and inh["b_cover_cap"] == "1/20"
        and inh["cusum_domain"] == {"lo": "11/2", "hi": "49750555/8388608", "cells": 2}
        and inh["sr_domain"] == {"lo": "3803026123175981/562949953421312",
                                 "hi": "1883835/262144", "cells": 6}
        and inh["cost_cap_cpu_h"] == 150.0)
    pb = j("PREDECESSOR_BINDING.json")
    rec("K1R predecessor bound, halt preserved, B1 inherited PASS",
        pb["k1r"]["final_state"].startswith("HALTED_BY_GOVERNANCE")
        and pb["k1r"]["modification"].startswith("PROHIBITED")
        and pb["b1"]["status"] == "INHERITED_PASS" and pb["b1"]["rerun"] == "PROHIBITED"
        and pb["b1"]["aux5_admission"].startswith("CLOSED")
        and pb["lineage"]["K1R"].startswith("HALTED_BY_GOVERNANCE")
        and pb["lineage"]["P5Y_K1"] == "PARTIAL")
    blob = json.dumps({n: j(n) for n in cp["frozen_artifacts"]}).lower()
    leaked = [f for f in FORBIDDEN_RESULT_FIELDS if f'"{f.lower()}"' in blob]
    cellblob = json.dumps({"cu": cu["cells"], "sr": sr["cells"]})
    verdicts = [v for v in ("PASS", "FAIL", "MARGINAL", "CERTIFICATE_TOO_LOOSE")
                if v in cellblob]
    percell = [c["index"] for c in cu["cells"] + sr["cells"]
               if any(f in c for f in FORBIDDEN_RESULT_FIELDS) or "m" in c]
    rec("no frozen artifact carries a bridge scientific result",
        not leaked and not verdicts and not percell,
        f"result fields {leaked}, verdicts in cell tables {verdicts}, cells with results {percell}")
    cost = j("COST_ACCOUNTING.json")
    rec("cost accounting at zero new compute",
        cost["consumed_new_cpu_h"] == 0.0 and cost["cap_cpu_h_shared_with_k1r"] == 150.0)
    res = [str(p.relative_to(NS)) for p in (NS / "evidence").rglob("*") if p.is_file()]
    rec("no bridge result exists", not any("cell" in r.lower() for r in res), str(res))

    bad = [o for o in OUT if o["status"] != "PASS"]
    print(f"\n{len(OUT) - len(bad)}/{len(OUT)} qualification checks passed")
    print("K1R2_QUALIFICATION = " + ("PASS" if not bad else "FAIL"))
    (NS / "evidence" / "QUALIFICATION_RESULT.json").write_text(json.dumps(
        {"schema": "rebaseguard.p5y.k1r2.qualification-result.v1", "checks": OUT,
         "passed": len(OUT) - len(bad), "total": len(OUT),
         "verdict": "PASS" if not bad else "FAIL", "decisive_computation": False,
         "new_cpu_h": 0.0}, indent=1, sort_keys=True) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
