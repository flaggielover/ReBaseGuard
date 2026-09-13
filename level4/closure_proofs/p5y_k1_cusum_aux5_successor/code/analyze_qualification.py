"""Apply the FROZEN qualification protocol to the four Aux5 runs. Non-certifying; obligation statuses are not read.

  python analyze_qualification.py OUTDIR RESULT.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import cap_formula  # noqa: E402

RUNS = (("318", "A"), ("318", "B"), ("323", "A"), ("323", "B"))
FAMILIES = ("libflint-", "libgmp-", "libmpfr-", "libscipy_openblas64_-")


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def manifest_identity(m: dict) -> dict:
    mh = hashlib.sha256(canonical(m)).hexdigest()
    rh = hashlib.sha256(canonical(m["runtime"])).hexdigest()
    ph = hashlib.sha256(canonical({"schema": m["schema"], "manifest_version": m["manifest_version"],
                                   "manifest_hash": mh, "runtime_contract_hash": rh})).hexdigest()
    return {"producer_manifest_hash": mh, "runtime_contract_hash": rh, "producer_identity_hash": ph}


def main() -> int:
    out, result_path = Path(sys.argv[1]), Path(sys.argv[2])
    protocol = json.loads((NS / "config/QUALIFICATION_PROTOCOL.json").read_text())
    ident = manifest_identity(json.loads((NS / "manifests/producer_manifest_v3.json").read_text()))
    runs, p1, p4, p5 = {}, {}, {}, {}
    for cell, rep in RUNS:
        d = out / f"c{cell}_{rep}"
        key = f"{cell}{rep}"
        rc = int((d / "rc").read_text().strip()) if (d / "rc").exists() else None
        rec_p = d / f"aux5_CUSUM_{cell}_256.json"
        rec = json.loads(rec_p.read_text()) if rec_p.exists() else None
        runs[key] = rec
        p1[key] = bool(rc == 0 and rec and rec["producer"]["final_gate"]["stage"] == "final"
                       and rec["provenance_chain"]["all_verified"] is True and rec["scipy_guard"]["scipy_free"] is True)
        p4[key] = bool(rec and rec.get("runtime_contract_hash") == ident["runtime_contract_hash"]
                       and rec.get("producer_identity_hash") == ident["producer_identity_hash"])
        libs = (rec or {}).get("producer", {}).get("runtime", {}).get("backend_libraries", {})
        p5[key] = bool(libs and all(k.startswith("/") for k in libs)
                       and all(any(Path(k).name.startswith(f) for k in libs) for f in FAMILIES))
    p2, p3 = {}, {}
    for cell in ("318", "323"):
        a, b = runs[f"{cell}A"], runs[f"{cell}B"]
        p2[cell] = bool(a and b and a["scientific_content_hash"] == b["scientific_content_hash"])
        p3[cell] = bool(a and b and {k: v["certificate_hash"] for k, v in a["certificates"].items()}
                        == {k: v["certificate_hash"] for k, v in b["certificates"].items()})
    criteria = {"P1_runs_complete": all(p1.values()), "P2_determinism_scientific_hash": all(p2.values()),
                "P3_determinism_certificates": all(p3.values()), "P4_runtime_binding": all(p4.values()),
                "P5_backend_repair": all(p5.values())}
    measured = {k: {"cpu_seconds_including_dependencies": r["cpu_seconds_including_dependencies"],
                    "cpu_seconds_auxiliary": r["cpu_seconds_auxiliary"], "wall_seconds": r["wall_seconds"],
                    "peak_rss_kib": r["peak_rss_kib"]} for k, r in runs.items() if r}
    c_max = max((m["cpu_seconds_including_dependencies"] for m in measured.values()), default=None)
    aux4 = NS.parent / "p5y_k1_cusum_aux4_fullcover/diagnostics/cells"
    informational = {}
    for cell in ("318", "323"):
        p = aux4 / f"aux4_CUSUM_{cell}_256.json"
        if p.exists() and runs.get(f"{cell}A"):
            informational[cell] = {"scientific_hash_equal_to_aux4_skylakex_record":
                                   json.loads(p.read_text())["scientific_content_hash"] == runs[f"{cell}A"]["scientific_content_hash"]}
    res = {"schema": "rebaseguard.p5y.k1.cusum-aux5.qualification-result.v1", "result_bearing": False,
           "production": False, "protocol_sha256": hashlib.sha256((NS / "config/QUALIFICATION_PROTOCOL.json").read_bytes()).hexdigest(),
           "manifest_identity": ident, "per_run": {"P1": p1, "P4": p4, "P5": p5}, "per_cell": {"P2": p2, "P3": p3},
           "criteria": criteria, "CUSUM_DETERMINISM": "PASS" if criteria["P2_determinism_scientific_hash"] and criteria["P3_determinism_certificates"] else "FAIL",
           "QUALIFICATION": "PASS" if all(criteria.values()) else "FAIL",
           "measured": measured, "c_max_cpu_seconds": c_max,
           "derived_cap": cap_formula.cap(c_max_cpu_seconds=c_max) if c_max is not None else None,
           "informational_only": informational,
           "transition_to_production_authorized": protocol["transition_to_production"]["authorized_by_this_protocol"]}
    result_path.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in ("QUALIFICATION", "CUSUM_DETERMINISM", "criteria", "c_max_cpu_seconds")}
                     | {"CAP_cpu_h": (res["derived_cap"] or {}).get("CAP_cpu_h")}, indent=1))
    return 0 if res["QUALIFICATION"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
