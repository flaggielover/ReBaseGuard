"""Deterministic builder and fail-closed verifier of the CUSUM Aux5 new-glibc Q6 requalification result.

NON-CERTIFYING, NON-PRODUCTION, READ-ONLY. It reads only committed evidence under evidence/requalification_r1/ and
evidence/containment/, and it never runs a certifier. A Q6 PASS makes carry-over ELIGIBLE FOR INDEPENDENT REVIEW only:
it authorizes nothing, and launch readiness stays NOT_READY without a countersignature and a successor checkpoint.

  python q6_result.py build     write evidence/requalification_r1/Q6_RESULT.json from the committed evidence
  python q6_result.py verify    exit 0 iff the committed result rebuilds exactly and every gate holds
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parent))

import glibc_successor as G                                                      # noqa: E402

RESULT_REL = "evidence/requalification_r1/Q6_RESULT.json"
RUNS = (("318", "A"), ("318", "B"), ("323", "A"), ("323", "B"))
CPUS = {"318A": "0", "318B": "2", "323A": "4", "323B": "6"}
FAMILIES = ("libflint-", "libgmp-", "libmpfr-", "libscipy_openblas64_-")
CERTIFIER_CONSTANT_FLAGS = {"production_run": False, "result_bearing": False, "scientific_certification_of_full_cover": False}
BINDINGS = {
    "governance_freeze_commit": "3e26bb3016a45236a3ecb38236dc0ddd463e5650",
    "proposal_manifest_sha256": "964dc9691a4d5261d244c64426b6438a2ca7e6d2ef7329c26399345d60e34241",
    "predecessor_binding_sha256": "0676fc8267bac3fc6044ab4cb9f57c8769b2b9d62e0d2f0bb2a2d3b1d9db8ac3",
    "requalification_protocol_sha256": "38a7f97884736e3e7cb1e35bcf7e6e2d7d82abbe263fc0cfcdb9feaad019d244",
    "q6_reference_sha256": "124376c0f98a112ebc2404db72bec782646d1d14fd8a359b8dd6425df5548597",
    "qualification_worktree_commit": "d31ea4edd5a96be5c9ac0a7d4acea2a5a3c5e563",
}
FROZEN_FILES = {
    "code/qualify5.py": "7d917e51c3b4851236e4cdf5b600d593c0d85b3e89778f1745e7ccae94c0403d",
    "code/run_qualification.sh": "9b38489d91c586ba519cf63d2ea03bbdc516d5880fee87b1ab8a13e3f7ccf50c",
    "code/analyze_qualification.py": "dc2d9fb5f9e0faa1a891d8df45fc69d5c4b1799517b1bc9f29443763bdda48ae",
    "code/cap_formula.py": "bf1008841ee10ea0e9b4b94ae69eb1e17318f2a89169181452f5558294dd089e",
    "config/QUALIFICATION_PROTOCOL.json": "81e28577fdb0ebf671e0ea99799245e6d02a58015cf7c8e7a229f0d4f26b1d94",
    "manifests/producer_manifest_v3.json": "611bd0a9f356b0e7f5e63da60567ac1afa9e69fc1f8c464c7e5b89aeedbd2b9f",
}
IDENTITY = {"manifest_hash": "b55a2da1fea0c7ee889f8da6a4b893c12d3ef24e2bc02d19bd5488187fd30fd9",
            "runtime_contract_hash": "bc75c9ea7cd5f9406a0509bb0a161aa2c013f80427d1035197989e3d202c845a",
            "producer_identity_hash": "3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19"}
HOLDS = sorted(["libc6", "libc-bin", "libgcc-s1", "libstdc++6", "zlib1g", "libcrypt1", "linux-image-amd64",
                "linux-image-6.12.107+deb13-amd64"])
DROPIN = 'APT::Periodic::Update-Package-Lists "0";\nAPT::Periodic::Unattended-Upgrade "0";\n'
MAX_CMAX_FOR_CAP_300 = 2431.904


def _sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def _json(p):
    return json.loads(Path(p).read_bytes())


def containment_problems(pre: dict, post: dict, post_run: dict) -> list[str]:
    p = []
    for label, st in (("POST", post), ("POST_RUN", post_run)):
        u = st.get("units") or {}
        if not all(u.get(t) == {"enabled": "disabled", "active": "inactive"} for t in ("apt-daily.timer", "apt-daily-upgrade.timer")):
            p.append(f"CONTAINMENT_{label}: apt timers not disabled/inactive")
        if not all((u.get(s) or {}).get("enabled") == "masked" for s in ("apt-daily.service", "apt-daily-upgrade.service")):
            p.append(f"CONTAINMENT_{label}: apt services not masked")
        cfg = st.get("apt_config") or []
        if 'APT::Periodic::Update-Package-Lists "0";' not in cfg or 'APT::Periodic::Unattended-Upgrade "0";' not in cfg:
            p.append(f"CONTAINMENT_{label}: periodic keys not zero")
        if st.get("holds") != HOLDS:
            p.append(f"CONTAINMENT_{label}: holds differ")
        if (st.get("freeze_dropin") or {}).get("content") != DROPIN:
            p.append(f"CONTAINMENT_{label}: drop-in differs")
        if any((st.get("other_managers") or {}).values()):
            p.append(f"CONTAINMENT_{label}: another package manager is installed")
    if pre.get("holds") != [] or (pre.get("freeze_dropin") or {}).get("exists") is not False:
        p.append("CONTAINMENT_PRE: pre-state is not the unmodified host")
    for key in ("packages", "system_libraries_sha256", "kernel_release"):
        if not (pre.get(key) == post.get(key) == post_run.get(key)):
            p.append(f"CONTAINMENT: {key} changed across containment or the run")
    if {k: v for k, v in (post.get("apt_conf_d_sha256") or {}).items() if k != "99-rebaseguard-cusum-freeze"} != pre.get("apt_conf_d_sha256"):
        p.append("CONTAINMENT: a Debian apt configuration file changed")
    for key in ("units", "holds", "apt_config", "apt_conf_d_sha256", "freeze_dropin"):
        if post.get(key) != post_run.get(key):
            p.append(f"CONTAINMENT: {key} changed during the run")
    return p


def build_result(ns=G.NS, repo=G.REPO) -> tuple[dict, list[str]]:
    """Returns (result, problems). The result is deterministic in the committed evidence."""
    ns, repo = Path(ns), Path(repo)
    ev, raw = ns / "evidence/requalification_r1", ns / "evidence/requalification_r1/qualification_r1"
    cont = ns / "evidence/containment"
    p: list[str] = []
    for rel, key in (("config/GLIBC_SUCCESSOR_PROPOSAL.json", "proposal_manifest_sha256"),
                     ("config/PREDECESSOR_BINDING.json", "predecessor_binding_sha256"),
                     ("config/REQUALIFICATION_PROTOCOL.json", "requalification_protocol_sha256"),
                     ("config/Q6_REFERENCE.json", "q6_reference_sha256")):
        if _sha(ns / rel) != BINDINGS[key]:
            p.append(f"BINDING: {rel} != {key}")
    meta = _json(ev / "RUN_METADATA.json")
    probe, host_launch, host_end = _json(ev / "PROBE.json"), _json(ev / "HOST_AT_LAUNCH.json"), _json(ev / "HOST_AT_RUN_END.json")
    affinity, analysis = _json(ev / "AFFINITY_AT_LAUNCH.json"), _json(ev / "ANALYSIS_RESULT.json")
    pre, post, post_run = (_json(cont / f"{n}.json") for n in ("PRE_STATE", "POST_STATE", "POST_RUN_STATE"))
    rq = _json(ns / "config/REQUALIFICATION_PROTOCOL.json")
    reference = _json(ns / "config/Q6_REFERENCE.json")

    clone = meta.get("clone") or {}
    if clone.get("commit") != BINDINGS["qualification_worktree_commit"] or (raw / "checkout_head").read_text().strip() != clone.get("commit"):
        p.append("WORKTREE: not the frozen qualification commit")
    for when in ("before_launch", "after_runs"):
        st = clone.get(when) or {}
        if st.get("tracked_changes") != 0 or st.get("untracked") != 0:
            p.append(f"WORKTREE: not clean {when}")
    if clone.get("frozen_files_sha256") != FROZEN_FILES:
        p.append("WORKTREE: frozen qualification files differ")
    if clone.get("path") == "/root/work/postk1-aux5":
        p.append("WORKTREE: the production checkout was reused")
    links = meta.get("evidence_sha256") or {}
    for name in ("PROBE.json", "HOST_AT_LAUNCH.json", "HOST_AT_RUN_END.json", "AFFINITY_AT_LAUNCH.json", "ANALYSIS_RESULT.json"):
        if links.get(name) != _sha(ev / name):
            p.append(f"METADATA_LINK: {name}")
    for name in ("PRE_STATE.json", "POST_STATE.json", "POST_RUN_STATE.json"):
        if links.get(f"containment/{name}") != _sha(cont / name):
            p.append(f"METADATA_LINK: containment/{name}")
    if meta.get("cusum_production_processes") != {"at_launch": 0, "after_runs": 0}:
        p.append("HOST: a CUSUM production process was present")
    if meta.get("predecessor_binding_sha256_after_runs") != BINDINGS["predecessor_binding_sha256"]:
        p.append("PREDECESSOR: the terminal predecessor changed during requalification")

    if not (probe.get("manifest_verify_ok") is True and probe.get("problems") == [] and probe.get("files") == 60
            and all(probe.get(k) == v for k, v in IDENTITY.items()) and probe.get("scipy_imported_in_probe") is False):
        p.append("PROBE: manifest v3 verification or identity")
    sw = rq["software"]
    if (probe.get("cpython_version_full"), probe.get("numpy_version"), probe.get("python_flint_version"),
            probe.get("scipy_version_metadata"), probe.get("openblas_runtime_corename"), probe.get("openblas_config")) != \
            (sw["cpython_version_full"], sw["numpy"], sw["python_flint"], sw["scipy"], sw["openblas_runtime_corename"], sw["openblas_config"]):
        p.append("PROBE: software versions differ from the requalification protocol")
    for label, facts in (("launch", host_launch), ("run_end", host_end)):
        for key in ("host_name", "machine_id_sha256", "cpu_model", "logical_cpus", "physical_cores", "smt_groups", "kernel_release",
                    "libc_path", "libc_sha256", "glibc_package_version", "system_libraries_sha256", "packages"):
            if facts.get(key) != rq["host"][key]:
                p.append(f"HOST_{label.upper()}: {key} differs from the requalification protocol")
    p += containment_problems(pre, post, post_run)

    runs, cells = {}, {}
    for cell, rep in RUNS:
        label, d = f"{cell}{rep}", raw / f"c{cell}_{rep}"
        rec_path = d / f"aux5_CUSUM_{cell}_256.json"
        rc = int((d / "rc").read_text().strip()) if (d / "rc").is_file() else None
        rec = _json(rec_path) if rec_path.is_file() else {}
        prod = rec.get("producer") or {}
        libs = (prod.get("runtime") or {}).get("backend_libraries") or {}
        aff = affinity.get(label) or {}
        argv = aff.get("argv") or []
        pinned = (aff.get("affinity") == CPUS[label] and "--cell" in argv and argv[argv.index("--cell") + 1] == cell
                  and "--bits" in argv and argv[argv.index("--bits") + 1] == "256")
        runs[label] = {
            "rc": rc, "record_sha256": _sha(rec_path) if rec_path.is_file() else None,
            "run_log_sha256": _sha(d / "run.log") if (d / "run.log").is_file() else None,
            "cell_index": rec.get("cell_index"), "precision_bits": rec.get("precision_bits"),
            "final_gate_stage": (prod.get("final_gate") or {}).get("stage"),
            "provenance_chain_all_verified": (rec.get("provenance_chain") or {}).get("all_verified"),
            "scipy_free": (rec.get("scipy_guard") or {}).get("scipy_free"),
            "runtime_contract_hash": rec.get("runtime_contract_hash"), "producer_identity_hash": rec.get("producer_identity_hash"),
            "backend_libraries": libs, "certifier_constant_flags": {k: rec.get(k) for k in CERTIFIER_CONSTANT_FLAGS},
            "cpu_affinity_observed": aff.get("affinity"), "pinned_as_frozen": pinned,
            "scientific_content_hash": rec.get("scientific_content_hash"),
            "certificate_hashes": {k: v["certificate_hash"] for k, v in sorted((rec.get("certificates") or {}).items())},
            "cpu_seconds_including_dependencies": rec.get("cpu_seconds_including_dependencies"),
            "cpu_seconds_auxiliary": rec.get("cpu_seconds_auxiliary"), "wall_seconds": rec.get("wall_seconds"),
            "peak_rss_kib": rec.get("peak_rss_kib")}
        cells.setdefault(cell, {})[rep] = {k: runs[label][k] for k in ("record_sha256", "scientific_content_hash", "certificate_hashes")}
    r = runs
    p1 = {k: bool(v["rc"] == 0 and v["final_gate_stage"] == "final" and v["provenance_chain_all_verified"] is True
                  and v["scipy_free"] is True) for k, v in r.items()}
    p4 = {k: bool(v["runtime_contract_hash"] == IDENTITY["runtime_contract_hash"]
                  and v["producer_identity_hash"] == IDENTITY["producer_identity_hash"]) for k, v in r.items()}
    p5 = {k: bool(v["backend_libraries"] and all(x.startswith("/") for x in v["backend_libraries"])
                  and all(any(Path(x).name.startswith(f) for x in v["backend_libraries"]) for f in FAMILIES)) for k, v in r.items()}
    p2 = {c: r[c + "A"]["scientific_content_hash"] is not None and r[c + "A"]["scientific_content_hash"] == r[c + "B"]["scientific_content_hash"]
          for c in ("318", "323")}
    p3 = {c: bool(r[c + "A"]["certificate_hashes"]) and r[c + "A"]["certificate_hashes"] == r[c + "B"]["certificate_hashes"]
          for c in ("318", "323")}
    criteria = {"P1_runs_complete": all(p1.values()), "P2_determinism_scientific_hash": all(p2.values()),
                "P3_determinism_certificates": all(p3.values()), "P4_runtime_binding": all(p4.values()),
                "P5_backend_repair": all(p5.values())}
    shape = {k: bool(v["pinned_as_frozen"] and v["cell_index"] == int(k[:3]) and v["precision_bits"] == 256
                     and v["certifier_constant_flags"] == CERTIFIER_CONSTANT_FLAGS) for k, v in r.items()}
    analyzer_agrees = analysis.get("criteria") == criteria and analysis.get("protocol_sha256") == FROZEN_FILES["config/QUALIFICATION_PROTOCOL.json"]
    if not analyzer_agrees:
        p.append("ANALYZER: the frozen analyzer does not agree with the independent re-derivation")
    if not all(shape.values()):
        p.append(f"RUN_SHAPE: {sorted(k for k, v in shape.items() if not v)}")
    original = all(criteria.values()) and analyzer_agrees and all(shape.values())

    obj = {"schema": G.Q6_RESULT_SCHEMA, "qualification_P1_P5": "PASS" if original else "FAIL",
           "libc_sha256": host_end.get("libc_sha256"), "glibc_package_version": host_end.get("glibc_package_version"),
           "cells": cells}
    q6 = G.evaluate_q6(obj, reference)
    sci = all(cells[c][rep]["scientific_content_hash"] == reference["cells"][c]["scientific_content_hash"]
              for c in ("318", "323") for rep in ("A", "B"))
    cert = all(cells[c][rep]["certificate_hashes"] == reference["cells"][c]["certificate_hashes"]
               for c in ("318", "323") for rep in ("A", "B"))
    differences = []
    for c in ("318", "323"):
        ref = reference["cells"][c]
        for rep in ("A", "B"):
            got = cells[c][rep]
            if got["scientific_content_hash"] != ref["scientific_content_hash"]:
                differences.append({"cell": c, "repeat": rep, "field": "scientific_content_hash",
                                    "expected": ref["scientific_content_hash"], "observed": got["scientific_content_hash"]})
            for unit in sorted(set(ref["certificate_hashes"]) | set(got["certificate_hashes"])):
                if got["certificate_hashes"].get(unit) != ref["certificate_hashes"].get(unit):
                    differences.append({"cell": c, "repeat": rep, "field": f"certificate_hash[{unit}]",
                                        "expected": ref["certificate_hashes"].get(unit), "observed": got["certificate_hashes"].get(unit)})
    sys.path.insert(0, str(repo / G.AUX5_REL / "code"))
    import cap_formula                                                          # noqa: E402
    cpu = [v["cpu_seconds_including_dependencies"] for v in r.values() if isinstance(v["cpu_seconds_including_dependencies"], (int, float))]
    c_max = max(cpu) if len(cpu) == 4 else None
    cap = cap_formula.cap(c_max_cpu_seconds=repr(c_max)) if c_max is not None else None
    if cap is None or cap["CAP_cpu_h"] != 300:
        p.append("CAP: requalified c_max does not keep the frozen 300 CPU-h cap (governance stop, never a raise)")
    final = q6["state"] == "PASS" and original and sci and cert and not p
    result = {
        **obj, "status": "RECORDED_NOT_AN_AUTHORIZATION", "production": False, "result_bearing": False,
        "bindings": {**BINDINGS, "run_metadata_sha256": _sha(ev / "RUN_METADATA.json"),
                     "analysis_result_sha256": _sha(ev / "ANALYSIS_RESULT.json"),
                     "containment": {n: _sha(cont / f"{n}.json") for n in ("PRE_STATE", "POST_STATE", "POST_RUN_STATE")}},
        "runs": runs, "per_run": {"P1": p1, "P4": p4, "P5": p5, "frozen_shape": shape}, "per_cell": {"P2": p2, "P3": p3},
        "criteria": criteria, "frozen_analyzer_agrees": analyzer_agrees, "Q6_ORIGINAL_GATES": "PASS" if original else "FAIL",
        "q6_evaluation": {k: q6[k] for k in ("state", "CARRYOVER_ROUTE", "problems")},
        "Q6_SCIENTIFIC_HASH_IDENTITY": "PASS" if sci else "FAIL", "Q6_CERTIFICATE_HASH_IDENTITY": "PASS" if cert else "FAIL",
        "differences": differences, "verification_problems": p, "Q6_FINAL": "PASS" if final else "FAIL",
        "CARRYOVER_ROUTE": "ELIGIBLE_FOR_INDEPENDENT_REVIEW" if final else "REJECTED",
        "qualification_cpu_accounting": {"per_run_cpu_seconds_including_dependencies": {k: v["cpu_seconds_including_dependencies"] for k, v in r.items()},
                                         "total_cpu_seconds": sum(cpu), "c_max_cpu_seconds": c_max, "derived_cap": cap,
                                         "counted_against_campaign_cap": False, "disclosed": True},
        "host_identity": {k: host_end.get(k) for k in ("host_name", "kernel_release", "libc_sha256", "glibc_package_version")},
        "authorizations": {"CARRYOVER_AUTHORIZED": False, "COUNTERSIGNATURE_CREATED": False,
                           "SUCCESSOR_CHECKPOINT_CREATED": False, "PRODUCTION_LAUNCHED": False}}
    return result, p


def verify_result(ns=G.NS, repo=G.REPO) -> list[str]:
    ns, repo = Path(ns), Path(repo)
    try:
        committed = (ns / RESULT_REL).read_bytes()
        result, p = build_result(ns, repo)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"Q6_RESULT_UNREADABLE: {type(exc).__name__}: {exc}"]
    if committed != G.dump(result):
        p = p + ["Q6_RESULT_DOES_NOT_REBUILD: committed evidence or result changed"]
    if result["Q6_FINAL"] != "PASS":
        p = p + [f"Q6_FINAL_{result['Q6_FINAL']}: {result['q6_evaluation']['problems'][:6]}"]
    p += [f"PROPOSAL: {x}" for x in G.verify_proposal(ns, repo)]
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 new-glibc Q6 result (read-only)")
    ap.add_argument("cmd", choices=("build", "verify"))
    a = ap.parse_args(argv)
    if a.cmd == "build":
        result, problems = build_result()
        (G.NS / RESULT_REL).write_bytes(G.dump(result))
        print(json.dumps({"Q6_FINAL": result["Q6_FINAL"], "CARRYOVER_ROUTE": result["CARRYOVER_ROUTE"], "problems": problems,
                          "sha256": _sha(G.NS / RESULT_REL)}, indent=1))
        return 0 if result["Q6_FINAL"] == "PASS" else 30
    problems = verify_result()
    print(json.dumps({"Q6_RESULT_VALID": not problems, "problems": problems}, indent=1))
    return 0 if not problems else 30


if __name__ == "__main__":
    raise SystemExit(main())
