"""R4 qualification runner (config/QUALIFICATION_PROTOCOL_R4.json). NON-SCIENTIFIC.

    python -B code/qualify_r4.py run   --outdir evidence/qualification_r4 --workers 4
    python -B code/qualify_r4.py check --outdir evidence/qualification_r4

Every part runs in a fresh interpreter. No real CUSUM cell is evaluated and no R''' or R^(5) of any (D,m) is computed.
Completion protocol (no process-name matching): the runner writes <outdir>/RUN_STATE.json (pid, start) first, then
QUALIFICATION_RESULT_R4.json and finally RUN_COMPLETE.json (result sha256); on an exception RUN_FAILED.json.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import resource
import subprocess
import sys
import tempfile
import time
import traceback
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = REPO / "level4/closure_proofs"
R3_NS = CP / "p5y_k5_cusum_order3_r3_infrastructure"
for _p in (str(CP / "p5y_k5_cusum_order3_real_producer/code"), str(CP / "p5y_k5_cusum_order3_r2_repair/code"),
           str(R3_NS / "code"), str(NS / "code")):
    sys.path.insert(0, _p)

FROZEN_PROTOCOL = NS / "config/QUALIFICATION_PROTOCOL_R4.json"
PROTOCOL = Path(os.environ.get("O3R4_DEV_PROTOCOL_PATH", str(FROZEN_PROTOCOL)))    # dev calibration only
GATES = json.loads((NS / "config/PRE_RESULT_GATES_R4.json").read_text())


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode()


def load_protocol() -> dict:
    return json.loads(PROTOCOL.read_text())


def runtime() -> dict:
    import platform
    import socket
    import flint
    import numpy
    return {"python": platform.python_version(), "python_flint": flint.__version__, "numpy": numpy.__version__,
            "host": socket.gethostname(), "prefix": sys.prefix, "machine": platform.machine()}


def load_mutant(path: Path, old: str, new: str, tag: str):
    src = path.read_text()
    if src.count(old) != 1:
        raise RuntimeError(f"anchor {tag} matches {src.count(old)} times")
    tmp = Path(tempfile.mkdtemp(prefix="o3r4-")) / f"{tag}.py"
    tmp.write_text(src.replace(old, new))
    spec = importlib.util.spec_from_file_location(tag, tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def r3_protocol():
    return json.loads((R3_NS / "config/QUALIFICATION_PROTOCOL_R3.json").read_text())


def q3():
    os.environ.pop("O3R3_DEV_PROTOCOL_PATH", None)
    import qualify_r3
    return qualify_r3


# ------------------------------------------------------------------ parts: operator constants
def part_odd_certificate(proto, args):
    import constants_r4 as K4
    import odd_block_certificate as OB
    import resolvent_certificate as RC
    art_path = NS / proto["certificate_artifact"]
    art = json.loads(art_path.read_text())
    v = OB.verify_artifact(art)
    reg = json.loads((NS / "config/OPERATOR_CERTIFICATES_R4.json").read_text())
    ce_entry = next(e for e in reg["certificates"] if e["name"] == "C_e0")
    co_entry = next(e for e in reg["certificates"] if e["name"] == "C_o0")
    ce_art = json.loads((REPO / ce_entry["artifact"]).read_text())
    vce = RC.verify_artifact(ce_art)
    try:
        consts = K4.load_certificates()
        loaded = {k: str(x) for k, x in consts.items()}
    except K4.R4Refusal as exc:
        loaded = {"refused": str(exc)}
    checks = {
        "C_o0": {"certified": v["certified"], "identical": v["identical"], "C_upper_bound": art["certified"]["C_upper_bound"],
                 "C_float": float(F(art["certified"]["C_upper_bound"])),
                 "margin_lower": float(F(art["certified"]["supersolution_margin_lower_bound"])),
                 "pass": v["certified"] and v["identical"]},
        "C_e0": {"certified": vce["certified"], "identical": vce["identical"], "C_upper_bound": ce_art["certified"]["C_upper_bound"],
                 "C_float": float(F(ce_art["certified"]["C_upper_bound"])), "pass": vce["certified"] and vce["identical"]},
        "registry": {"pass": co_entry["artifact_sha256"] == sha(art_path.read_bytes())
                     and co_entry["value_upper"] == art["certified"]["C_upper_bound"]
                     and ce_entry["artifact_sha256"] == sha((REPO / ce_entry["artifact"]).read_bytes())
                     and ce_entry["value_upper"] == ce_art["certified"]["C_upper_bound"]
                     and loaded.get("C_o0") == co_entry["value_upper"] and loaded.get("C_e0") == ce_entry["value_upper"],
                     "loaded": loaded}}
    return {"checks": checks}


def part_odd_crosscheck(proto, args):
    import odd_block_certificate as OB
    import odd_block_crosscheck as X
    art = json.loads((NS / proto["certificate_artifact"]).read_text())
    crit = json.loads((NS / "config/FEASIBILITY_CRITERION_R4.json").read_text())
    M, n = OB.odd_matrix()
    return X.crosscheck(art["payload"], float(F(art["certified"]["supersolution_margin_lower_bound"])),
                        float(F(art["certified"]["C_upper_bound"])), float(F(crit["C_o0_R3"])), M=M, n=n)


def part_operator_audit(proto, args):
    import operator_audit as OA
    a = OA.audit()
    art = json.loads((NS / proto["certificate_artifact"]).read_text())
    reg = json.loads((NS / "config/OPERATOR_CERTIFICATES_R4.json").read_text())
    ce = float(F(next(e for e in reg["certificates"] if e["name"] == "C_e0")["value_upper"]))
    co = float(F(art["certified"]["C_upper_bound"]))
    return {"audit": a, "pass": a["odd_block"]["sup_resolvent_of_one"] <= co and a["full_space"]["sup_resolvent_of_one"] <= ce}


def part_odd_certificate_mutations(proto, args):
    """Control: the declared non-supersolution proposal must be REJECTED by the frozen R4 verifier. A mutant is detected
    if it ACCEPTS the control or its replay of the frozen artifact differs from the stored certified numbers."""
    import odd_block_certificate as OB
    art = json.loads((NS / proto["certificate_artifact"]).read_text())
    bp = proto["odd_bad_payload_proposal"]
    bad, _ = OB.proposal(float(F(bp["alpha"])), float(F(bp["beta"])))
    base = OB.certify(bad, bits=256, depth=int(bp["depth"]))
    rows = {"frozen_verifier_rejects_control": {"pass": not base["certified"],
                                                "margin_lower": str(base["supersolution_margin_lower_bound"])}}
    for mut in proto["odd_certificate_mutations"]:
        mod = load_mutant(NS / "code/odd_block_certificate.py", mut["old"], mut["new"], mut["id"])
        try:
            accepted = bool(mod.certify(bad, bits=256, depth=int(bp["depth"]))["certified"])
        except Exception:
            accepted = False
        try:
            rep = mod.verify_artifact(art)
            differs = not (rep["identical"] and rep["certified"])
        except Exception:
            differs = True
        rows[mut["id"]] = {"accepts_control": accepted, "artifact_replay_differs": differs, "detected": accepted or differs}
    return {"rows": rows}


# ------------------------------------------------------------------ parts: R3 suites re-executed unchanged
def part_r3_certificate_mutations(proto, args):
    Q3 = q3()
    return Q3.part_certificate_mutations(r3_protocol(), args)


def part_r3_wiring(proto, args):
    Q3 = q3()
    body = Q3.part_synthetic_real(r3_protocol(), argparse.Namespace(no_mutations=False))
    body.pop("payload", None)
    return body


def part_regressions(proto, args):
    Q3 = q3()
    p3 = r3_protocol()
    return {"r2_graded_soundness": Q3.part_r2_regression(p3, args), "r3_parity": Q3.part_parity(p3, args),
            "r3_he6": {"pass": Q3.part_he6(p3, args)["pass"]}}


# ------------------------------------------------------------------ parts: first cell / R5
def part_first_cell(proto, args):
    import first_cell as FC3
    import first_cell_r4 as FC4
    rows = [FC4.run(spec) for spec in proto["fixtures"]]
    r3rows = [{"id": s["id"], "violation_count": FC3.run(s)["violation_count"]} for s in r3_protocol()["first_cell_fixtures"]]
    lemma = FC3.evenness_lemma_check(int(proto["lemma_seed"]))
    payload = [{"id": r["id"], "radii": r["radii"]} for r in rows]
    return {"rows": rows, "r3_rows": r3rows, "lemma": lemma, "payload_sha256": sha(canonical(payload))}


def _r3_r5_path():
    return R3_NS / "code/r5_majorant.py"


def part_b01(proto, args):
    import first_cell_r4 as FC4
    b01 = next(m for m in proto["r5_mutations"] if m["id"] == "B01_M5_USES_ODD_COMPONENT")
    mut = load_mutant(_r3_r5_path(), b01["old"], b01["new"], "B01")
    shams = {c["id"]: load_mutant(_r3_r5_path(), c["old"], c["new"], c["id"]) for c in proto["b01_controls"]}
    out = {}
    for fid in proto["b01_fixtures"]:
        spec = next(f for f in proto["fixtures"] if f["id"] == fid)
        row = {}
        for bits in proto["b01_precisions"]:
            c = FC4.run(spec, bits=bits, reference=False)
            m = FC4.run(spec, r5=mut, bits=bits, reference=False)
            row[f"correct_{bits}"] = {"violations": c["violation_count"]}
            row[f"B01_{bits}"] = {"violations": m["violation_count"], "kinds": m["violation_kinds"], "first": m["violations"][:2]}
        for sid, smod in shams.items():
            s = FC4.run(spec, r5=smod, reference=False)
            row[sid] = {"violations": s["violation_count"], "kinds": s["violation_kinds"]}
        kinds_ok = all(set(row[f"B01_{b}"]["kinds"]) <= {"M5", "strategyB"} and row[f"B01_{b}"]["violations"] > 0
                       for b in proto["b01_precisions"])
        stable = len({(row[f"B01_{b}"]["violations"], tuple(row[f"B01_{b}"]["kinds"])) for b in proto["b01_precisions"]}) == 1
        row["pass"] = (kinds_ok and stable and all(row[f"correct_{b}"]["violations"] == 0 for b in proto["b01_precisions"])
                       and all(row[s]["violations"] == 0 for s in shams))
        out[fid] = row
    return {"fixtures": out, "pass": bool(out) and all(r["pass"] for r in out.values())}


def part_r5_mutations(proto, args):
    import first_cell_r4 as FC4
    res = {}
    for group, path, key in (("r5", _r3_r5_path(), "r5"), ("local", NS / "code/local_r5.py", "lr")):
        muts = proto["r5_mutations"] if group == "r5" else proto["local_r5_mutations"]
        for mut in muts:
            mod = load_mutant(path, mut["old"], mut["new"], mut["id"])
            hits = []
            for fid in proto["mutation_trials"]:
                spec = next(f for f in proto["fixtures"] if f["id"] == fid)
                try:
                    r = FC4.run(spec, reference=False, **{key: mod})
                    hits.append({"trial": fid, "violations": r["violation_count"], "kinds": r["violation_kinds"],
                                 "first": r["violations"][:1]})
                    if r["violation_count"] > 0:
                        break
                except Exception as exc:
                    hits.append({"trial": fid, "crashed": f"{type(exc).__name__}: {str(exc)[:150]}"})
            res[mut["id"]] = {"group": group, "detected": any(h.get("violations", 0) > 0 for h in hits), "trials": hits}
    return {"mutations": res}


def part_m5_crosscheck(proto, args):
    import first_cell as FC3
    import first_cell_r4 as FC4
    import m5_crosscheck as X
    import sigma_systems as SS
    rows = []
    for fid in proto["m5_crosscheck_fixtures"]:
        spec = next(f for f in proto["fixtures"] if f["id"] == fid)
        r = FC4.run(spec, reference=False)
        sysm = SS.build(spec)
        x1 = F(spec["x1"])
        npts = int(proto["m5_crosscheck_grid_points"])
        grid = [x1 * F(g, npts - 1) for g in range(npts)]
        M5 = {int(m): v["M5_local"] for m, v in r["radii"].items()}
        rows.append(X.crosscheck(spec, M5, lambda e, m, n: FC3.true_R(FC3.true_derivs(sysm, e), m, n), grid))
    return {"rows": rows, "pass": all(x["pass"] for x in rows)}


def part_forecast(proto, args):
    import forecast_r4 as FR4
    fc = FR4.compute()
    return {"forecast": fc, "payload_sha256": sha(canonical(fc))}


# ------------------------------------------------------------------ parts: fail closed / fences
def part_failclosed(proto, args):
    import constants_r4 as K4
    import local_r5 as LR
    import odd_block_certificate as OB
    out = {}
    rec0 = (CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json").read_bytes()
    for name, auth, rb in (("no_authorization", None, rec0), ("forged_authorization", {"cells": [0]}, rec0),
                           ("gate_precedes_record_validation", None, b"garbage")):
        try:
            K4.certify_real_cell_r4(0, authorization=auth, record_bytes=rb)
            out[name] = {"pass": False}
        except K4.R4Refusal as exc:
            out[name] = {"pass": str(exc).startswith("REAL_CELL_NOT_AUTHORIZED"), "refused": str(exc)}
    tmp = Path(tempfile.mkdtemp(prefix="o3r4fc-"))
    reg = json.loads((NS / "config/OPERATOR_CERTIFICATES_R4.json").read_text())
    reg["certificates"] = [e for e in reg["certificates"] if e["name"] != "C_o0"]
    (tmp / "reg.json").write_text(json.dumps(reg))
    src = (NS / "code/constants_r4.py").read_text()
    pinned = src.split('CERT_REGISTRY_SHA256 = "')[1].split('"')[0]
    anchored = load_mutant(NS / "code/constants_r4.py", "NS = Path(__file__).resolve().parents[1]", f'NS = Path("{NS}")',
                           "fc4_anchored")                       # mutants live in a temp dir: pin the namespace path
    base = Path(anchored.__file__)
    m1 = load_mutant(base, 'CERT_REGISTRY = NS / "config/OPERATOR_CERTIFICATES_R4.json"',
                     f'CERT_REGISTRY = Path("{tmp / "reg.json"}")', "fc4_missing")
    try:
        m1.load_certificates()
        out["missing_C_o0_registry_bytes_changed"] = {"pass": False}
    except m1.R4Refusal as exc:
        out["missing_C_o0_registry_bytes_changed"] = {"pass": "REGISTRY_ALTERED" in str(exc), "refused": str(exc)}
    m2 = load_mutant(base, f'CERT_REGISTRY_SHA256 = "{pinned}"',
                     f'CERT_REGISTRY_SHA256 = "{sha((tmp / "reg.json").read_bytes())}"', "fc4_repinned")
    m2b = load_mutant(Path(m2.__file__), 'CERT_REGISTRY = NS / "config/OPERATOR_CERTIFICATES_R4.json"',
                      f'CERT_REGISTRY = Path("{tmp / "reg.json"}")', "fc4_repinned_b")
    try:
        m2b.load_certificates()
        out["missing_C_o0_even_if_repinned"] = {"pass": False}
    except m2b.R4Refusal as exc:
        out["missing_C_o0_even_if_repinned"] = {"pass": "MISSING_OPERATOR_CERTIFICATE C_o0" in str(exc), "refused": str(exc)}
    art = json.loads((NS / proto["certificate_artifact"]).read_text())
    art["certified"]["C_upper_bound"] = "4"
    out["tampered_certificate_value_detected"] = {"pass": not OB.verify_artifact(art)["identical"]}
    from flint import arb
    for label, kwargs in (("local_r5_missing_input", {"base": {"C": arb(1)}, "candidates": {"F:0:0": (arb(1), arb(1))},
                                                      "point_nodes": {}}),
                          ("local_r5_order4_anchor", {"base": {k: arb(1) for k in ("C", "C_e0", "C_o0", "k", "j", "eta", "S0")},
                                                      "candidates": {"F:0:4": (arb(1), arb(1))},
                                                      "point_nodes": {"F:0:4": None}})):
        try:
            LR.local_tower(kwargs["base"], kwargs["candidates"], kwargs["point_nodes"], x1=arb(0))
            out[label] = {"pass": False}
        except LR.LocalR5Refusal as exc:
            out[label] = {"pass": True, "refused": str(exc)}
    return {"checks": out, "pass": all(v["pass"] for v in out.values())}


def part_fence(proto, args):
    out = {}
    code = NS / "code"
    for mod in proto["pure_modules"]:
        tree = ast.parse((code / mod).read_text())
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        bad = sorted(names & set(proto["forbidden_imports_pure"]))
        out[mod] = {"pass": not bad, "forbidden": bad}
    spec = importlib.util.spec_from_file_location("no_monkeypatch", CP / "p5y_k1_cusum_aux3_successor/code/no_monkeypatch.py")
    sys.path.append(str(CP / "p5y_k1_cusum_aux3_successor/code"))
    nm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nm)
    findings = []
    for f in sorted(code.glob("*.py")):
        findings += nm.scan_source(f.read_text(), f.name)
    out["no_monkeypatch"] = {"pass": not findings, "findings": findings}
    for label, key in (("r1_immutable", "r1_bound_sha256"), ("r2_immutable", "r2_bound_sha256"), ("r3_immutable", "r3_bound_sha256")):
        moved = [rel for rel, h in proto[key].items() if not (REPO / rel).exists() or sha((REPO / rel).read_bytes()) != h]
        out[label] = {"pass": not moved, "moved": moved}
    for label, key in (("bound_code", "bound_code_sha256"), ("bound_config", "bound_config_sha256")):
        moved = [rel for rel, h in proto[key].items() if sha((REPO / rel).read_bytes()) != h]
        out[label] = {"pass": not moved, "moved": moved}
    tree = ast.parse((code / "constants_r4.py").read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "certify_real_cell_r4")
    first = fn.body[0]
    out["authorization_gate_first"] = {"pass": isinstance(first, ast.Assign) and "AUTH_REGISTRY" in ast.unparse(first)}
    auth = json.loads((NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY_R4.json").read_text())
    src = (code / "constants_r4.py").read_text()
    out["registries_pinned_auth_empty"] = {"pass": auth["authorizations"] == []
                                           and sha((NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY_R4.json").read_bytes()) in src
                                           and sha((NS / "config/OPERATOR_CERTIFICATES_R4.json").read_bytes()) in src}
    out["r3_protocol_pinned"] = {"pass": sha((REPO / proto["r3_protocol"]).read_bytes()) == proto["r3_protocol_sha256"]}
    return {"checks": out, "pass": all(v["pass"] for v in out.values())}


PARTS = {"odd_certificate": part_odd_certificate, "odd_crosscheck": part_odd_crosscheck,
         "operator_audit": part_operator_audit, "odd_certificate_mutations": part_odd_certificate_mutations,
         "r3_certificate_mutations": part_r3_certificate_mutations, "r3_wiring": part_r3_wiring,
         "regressions": part_regressions, "first_cell": part_first_cell, "b01": part_b01,
         "r5_mutations": part_r5_mutations, "m5_crosscheck": part_m5_crosscheck, "forecast": part_forecast,
         "failclosed": part_failclosed, "fence": part_fence}
ORDER = ["r3_wiring", "odd_certificate_mutations", "odd_certificate", "odd_crosscheck", "operator_audit",
         "r3_certificate_mutations", "first_cell", "b01", "r5_mutations", "m5_crosscheck", "forecast", "forecast_replay",
         "regressions", "failclosed", "fence"]


def run_part(args):
    proto = load_protocol()
    t0, w0 = time.process_time(), time.time()
    body = PARTS[args.part](proto, args)
    rec = {"part": args.part, "argv": sys.argv[2:], "runtime": runtime(), "body": body,
           "protocol_sha256": sha(PROTOCOL.read_bytes()),
           "metadata": {"cpu_seconds": time.process_time() - t0, "wall_seconds": time.time() - w0,
                        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")


def jobs(outdir):
    J = []
    for n in ORDER:
        part = "forecast" if n == "forecast_replay" else n
        J.append(["part", part, "--out", str(outdir / f"part_{n}.json")])
    return J


def cmd_run(args):
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    state = {"pid": os.getpid(), "started_unix": time.time(), "protocol_sha256": sha(PROTOCOL.read_bytes()),
             "jobs": ORDER}
    (outdir / "RUN_STATE.json").write_text(json.dumps(state, indent=1) + "\n")
    try:
        proto = load_protocol()
        env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONHASHSEED="0")
        for k in ("O3_DEV_PROTOCOL_PATH", "O3R2_DEV_PROTOCOL_PATH", "O3R3_DEV_PROTOCOL_PATH"):
            env.pop(k, None)
        pending = [[sys.executable, "-B", str(Path(__file__).resolve())] + j for j in jobs(outdir)]
        running, failures = [], []
        while pending or running:
            while pending and len(running) < int(args.workers):
                cmd = pending.pop(0)
                log = open(outdir / (Path(cmd[-1]).stem + ".log"), "w")
                running.append((cmd, subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT), log))
            time.sleep(2)
            for item in list(running):
                cmd, p, log = item
                if p.poll() is not None:
                    running.remove(item)
                    log.close()
                    if p.returncode != 0:
                        failures.append({"cmd": cmd[3:], "rc": p.returncode,
                                         "log_tail": (outdir / (Path(cmd[-1]).stem + ".log")).read_text()[-3000:]})
        result = assemble(proto, outdir)
        result["runner_failures"] = failures
        raw = (json.dumps(result, indent=1, sort_keys=True, default=str) + "\n").encode()
        (outdir / "QUALIFICATION_RESULT_R4.json").write_bytes(raw)
        (outdir / "RUN_COMPLETE.json").write_text(json.dumps({"pid": os.getpid(), "finished_unix": time.time(),
                                                              "result_sha256": sha(raw), "runner_failures": len(failures)}) + "\n")
        print(json.dumps({"verdict": result["verdict"], "gates": result["gates"], "runner_failures": len(failures)}, indent=1))
    except BaseException:
        (outdir / "RUN_FAILED.json").write_text(json.dumps({"pid": os.getpid(), "traceback": traceback.format_exc()}) + "\n")
        raise


def rd(outdir, name):
    return json.loads((outdir / name).read_text())


def assemble(proto, outdir):
    P = {n: rd(outdir, f"part_{n}.json") for n in ORDER}
    parts = {f"part_{n}.json": sha((outdir / f"part_{n}.json").read_bytes()) for n in ORDER}
    B = {n: p["body"] for n, p in P.items()}
    runtimes_ok = all(all(p["runtime"].get(k) == v for k, v in proto["runtime_contract"].items()) for p in P.values())
    protocol_ok = all(p["protocol_sha256"] == sha(PROTOCOL.read_bytes()) for p in P.values())
    oc, sr, fc = B["odd_certificate"]["checks"], B["r3_wiring"], B["first_cell"]
    om = B["odd_certificate_mutations"]["rows"]
    r3cm = B["r3_certificate_mutations"]["rows"]
    muts = B["r5_mutations"]["mutations"]
    wiring_ok = len(sr["mutations"]) == 12 and all(m["detected"] for m in sr["mutations"].values())
    r3cert_ids = [k for k in r3cm if k != "frozen_verifier_rejects_bad_payload"]
    odd_ids = [m["id"] for m in proto["odd_certificate_mutations"]]
    r5_ids = [m["id"] for m in proto["r5_mutations"]]
    loc_ids = [m["id"] for m in proto["local_r5_mutations"]]
    fcast = B["forecast"]["forecast"]
    binding = fcast["binding_g1_m1"]
    G = {
        "G01_R1_R2_R3_preserved": all(B["fence"]["checks"][k]["pass"] for k in ("r1_immutable", "r2_immutable", "r3_immutable")),
        "G02_C_o0_odd_block_certificate_replayed": oc["C_o0"]["pass"],
        "G03_C_e0_and_registry": oc["C_e0"]["pass"] and oc["registry"]["pass"],
        "G04_C_o0_independent_crosscheck": B["odd_crosscheck"]["pass"],
        "G05_operator_audit": B["operator_audit"]["pass"],
        "G06_R3_wiring_suite_reexecuted": sr["C1_count"] == 0 and sr["C2C3_count"] == 0 and sr["C6_count"] == 0
        and sr["C7_count"] == 0 and not sr["C5_graded_looser_m"] and wiring_ok
        and sr["payload_sha256"] == proto["r3_synthetic_payload_sha256"],
        "G07_certificate_mutation_suites": len(r3cert_ids) == 3 and all(r3cm[i]["detected"] for i in r3cert_ids)
        and r3cm["frozen_verifier_rejects_bad_payload"]["pass"] and all(om[i]["detected"] for i in odd_ids)
        and om["frozen_verifier_rejects_control"]["pass"],
        "G08_first_cell_manufactured_soundness": all(r["violation_count"] == 0 and r.get("reference_R3_violations", 0) == 0
                                                     for r in fc["rows"]) and all(r["violation_count"] == 0 for r in fc["r3_rows"]),
        "G09_B01_test_power_fixture": B["b01"]["pass"],
        "G10_R5_and_local_mutation_suites": all(muts[i]["detected"] for i in r5_ids + loc_ids),
        "G11_M5_independent_crosscheck": B["m5_crosscheck"]["pass"],
        "G12_evenness_lemma": fc["lemma"]["pass"],
        "G13_determinism_replay": B["forecast"]["payload_sha256"] == B["forecast_replay"]["payload_sha256"]
        and oc["C_o0"]["identical"] and oc["C_e0"]["identical"] and sr["payload_sha256"] == proto["r3_synthetic_payload_sha256"],
        "G14_fail_closed": B["failclosed"]["pass"],
        "G15_fences_and_registries": B["fence"]["pass"] and protocol_ok,
        "G16_runtime_identity": runtimes_ok,
        "G17_regressions": B["regressions"]["r2_graded_soundness"]["pass"] and B["regressions"]["r3_parity"]["pass"]
        and B["regressions"]["r3_he6"]["pass"],
    }
    gates = {k: "PASS" if v else "FAIL" for k, v in G.items()}
    sound = all(G[k] for k in G if k[:3] in GATES["soundness_gates"])
    cls, best_cls = binding["strategy_B_class"], fcast["best_grid_class"]
    if not sound:
        verdict = "NOT_READY"
    elif all(G.values()) and cls in ("MARGINAL", "PROMISING"):
        verdict = "QUALIFIED_FOR_GOVERNED_REAL_CELL_QUALIFICATION"
    elif cls == "UNINFORMATIVE" and best_cls == "UNINFORMATIVE":
        verdict = "CURRENT_ROUTE_NUMERICALLY_UNINFORMATIVE"
    else:
        verdict = "PARTIALLY_QUALIFIED"
    blocker = binding["dominant_blocker"]
    if verdict == "QUALIFIED_FOR_GOVERNED_REAL_CELL_QUALIFICATION":
        nxt = "PREPARE_GOVERNED_REAL_CELL_QUALIFICATION"
    elif verdict == "CURRENT_ROUTE_NUMERICALLY_UNINFORMATIVE":
        nxt = "SEEK_ALTERNATE_K5_ROUTE"
    elif blocker == "R5_DOMINANT" or (blocker == "BOTH_COMPARABLE"
                                      and binding["TRANSPORT_PENALTY_R4"] >= binding["POINT_RADIUS_FORECAST"]):
        nxt = "TIGHTEN_R5_AGAIN"
    else:
        nxt = "TIGHTEN_C_o0_AGAIN"
    counts = {
        "wiring_mutations": f"{sum(1 for m in sr['mutations'].values() if m['detected'])}/12",
        "r5_mutations": f"{sum(1 for i in r5_ids if muts[i]['detected'])}/{len(r5_ids)}",
        "certificate_mutations": f"{sum(1 for i in r3cert_ids if r3cm[i]['detected'])}/3",
        "odd_certificate_mutations": f"{sum(1 for i in odd_ids if om[i]['detected'])}/{len(odd_ids)}",
        "local_r5_mutations": f"{sum(1 for i in loc_ids if muts[i]['detected'])}/{len(loc_ids)}",
        "first_cell_violations": sum(r["violation_count"] for r in fc["rows"]),
    }
    return {"schema": "rebaseguard.p5y.k5.order3-r4.qualification-result.v1", "protocol_sha256": sha(PROTOCOL.read_bytes()),
            "part_sha256": parts, "gates": gates, "counts": counts, "verdict": verdict,
            "B1_NO_CERTIFIED_ORDER3_PRODUCER": "CLOSED_FOR_REAL_CELL_QUALIFICATION_ONLY"
            if verdict == "QUALIFIED_FOR_GOVERNED_REAL_CELL_QUALIFICATION" else "OPEN",
            "next_step": nxt, "binding_forecast": binding, "S_star": fcast["S_star"],
            "sensitivity_grid": fcast["sensitivity_grid_g1_m1"], "best_grid_class": best_cls,
            "certificates": {"C_o0": oc["C_o0"], "C_e0": oc["C_e0"]}, "odd_crosscheck": B["odd_crosscheck"],
            "operator_audit": B["operator_audit"]["audit"], "odd_certificate_mutations": om,
            "r3_certificate_mutations": r3cm, "wiring_mutations": sr["mutations"],
            "r5_mutations": {k: {"group": v["group"], "detected": v["detected"]} for k, v in muts.items()},
            "b01": B["b01"], "m5_crosscheck": B["m5_crosscheck"],
            "first_cell_manufactured": [{"id": r["id"], "violations": r["violation_count"], "m1": r["radii"]["1"],
                                         "reference_R3_m1": r.get("reference_R3", {}).get("1")} for r in fc["rows"]],
            "real_cell_qualification": "NOT_AUTHORIZED", "real_k5_scientific_cell_evaluated": "NO"}


def cmd_check(args):
    proto = load_protocol()
    outdir = Path(args.outdir)
    stored = json.loads((outdir / "QUALIFICATION_RESULT_R4.json").read_text())
    problems = [] if PROTOCOL == FROZEN_PROTOCOL else ["not the frozen protocol"]
    for label in ("bound_code_sha256", "bound_config_sha256", "r1_bound_sha256", "r2_bound_sha256", "r3_bound_sha256"):
        problems += [f"{label} moved: {rel}" for rel, h in proto[label].items() if sha((REPO / rel).read_bytes()) != h]
    again = assemble(proto, outdir)
    for key in ("gates", "part_sha256", "protocol_sha256", "counts", "verdict", "next_step"):
        if again[key] != stored[key]:
            problems.append(f"recomputed {key} differs")
    done = json.loads((outdir / "RUN_COMPLETE.json").read_text())
    if done["result_sha256"] != sha((outdir / "QUALIFICATION_RESULT_R4.json").read_bytes()):
        problems.append("completion marker does not match the result")
    print(json.dumps({"problems": problems, "verdict": again["verdict"], "gates": again["gates"],
                      "counts": again["counts"], "next_step": again["next_step"]}, indent=1))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("part")
    p.add_argument("part", choices=sorted(PARTS))
    p.add_argument("--out", required=True)
    p.add_argument("--no-mutations", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--outdir", required=True)
    r.add_argument("--workers", default="4")
    c = sub.add_parser("check")
    c.add_argument("--outdir", required=True)
    args = ap.parse_args()
    {"part": run_part, "run": cmd_run, "check": cmd_check}[args.cmd](args)
