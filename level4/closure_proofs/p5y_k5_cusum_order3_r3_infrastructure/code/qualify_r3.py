"""R3 qualification runner (config/QUALIFICATION_PROTOCOL_R3.json). NON-SCIENTIFIC.

    python -B code/qualify_r3.py run   --outdir evidence/qualification_r3 --workers 4
    python -B code/qualify_r3.py check --outdir evidence/qualification_r3

Every part runs in a fresh interpreter. No real CUSUM cell is evaluated and no R''' of any (D,m) is computed.
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
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = REPO / "level4/closure_proofs"
R1_NS = CP / "p5y_k5_cusum_order3_real_producer"
R2_NS = CP / "p5y_k5_cusum_order3_r2_repair"
for _p in (str(R1_NS / "code"), str(R2_NS / "code"), str(NS / "code")):
    sys.path.insert(0, _p)

FROZEN_PROTOCOL = NS / "config/QUALIFICATION_PROTOCOL_R3.json"
PROTOCOL = Path(os.environ.get("O3R3_DEV_PROTOCOL_PATH", str(FROZEN_PROTOCOL)))    # dev calibration only


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
    tmp = Path(tempfile.mkdtemp(prefix="o3r3-")) / f"{tag}.py"
    tmp.write_text(src.replace(old, new))
    spec = importlib.util.spec_from_file_location(tag, tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ parts
def part_certificates(proto, args):
    import resolvent_certificate as RC
    out = {}
    for name, rel in proto["certificate_artifacts"].items():
        art = json.loads((NS / rel).read_text())
        v = RC.verify_artifact(art)
        out[name] = {"certified": v["certified"], "identical": v["recomputed"] == art["certified"],
                     "C_upper_bound": art["certified"]["C_upper_bound"],
                     "C_float": float(F(art["certified"]["C_upper_bound"])),
                     "margin_lower": float(F(art["certified"]["supersolution_margin_lower_bound"])),
                     "artifact_sha256": sha((NS / rel).read_bytes()), "pass": v["certified"] and v["recomputed"] == art["certified"]}
    reg = json.loads((NS / "config/OPERATOR_CERTIFICATES_R3.json").read_text())
    out["registry_consistent"] = {"pass": all(
        e["artifact_sha256"] == out[e["name"]]["artifact_sha256"] and e["value_upper"] == out[e["name"]]["C_upper_bound"]
        for e in reg["certificates"])}
    return {"checks": out}


def part_certificate_mutations(proto, args):
    """Negative controls: a non-supersolution payload (the odd payload scaled by 4/5) must be REJECTED by the frozen
    verifier. A verifier mutation is detected if it ACCEPTS that payload, or if its replay of the frozen C_o0 artifact
    does not reproduce the stored certified numbers exactly (the artifact replay is the verifier's own check)."""
    import resolvent_certificate as RC
    art = json.loads((NS / proto["certificate_artifacts"]["C_o0"]).read_text())
    bad = json.loads(json.dumps(art["payload"]))
    bad["numerators"] = [[(4 * x) // 5 for x in row] for row in bad["numerators"]]
    base = RC.certify("odd", bad, bits=256, depth=art["subdivision_depth"])
    rows = {"frozen_verifier_rejects_bad_payload": {"pass": not base["certified"]}}
    for mut in proto["certificate_mutations"]:
        mod = load_mutant(NS / "code/resolvent_certificate.py", mut["old"], mut["new"], mut["id"])
        try:
            r = mod.certify("odd", bad, bits=256, depth=art["subdivision_depth"])
            accepted = bool(r["certified"])
        except Exception as exc:
            accepted, r = False, {"error": str(exc)}
        try:
            rep = mod.verify_artifact(art)
            replay_differs = not (rep["identical"] and rep["certified"])
        except Exception as exc:
            replay_differs = True
        rows[mut["id"]] = {"accepts_bad_payload": accepted, "artifact_replay_differs": replay_differs,
                           "detected": accepted or replay_differs}
    return {"rows": rows}


def part_he6(proto, args):
    import hermite6_ext as H6
    import opnorms
    import sharp_norms
    from intervals import workprec
    with workprec(256):
        ver = H6.verification()
        cells = []
        for left, right in proto["he6_cells"]:
            l, r = F(left), F(right)
            t = H6.norm_table(l, r)
            s = sharp_norms.table(l, r)
            compat = all(t["k"][i].upper() == s["k"][i].upper() and t["j"][i].upper() == s["j"][i].upper() for i in range(5))
            emax = H6.exact(max(abs(l), abs(r)))
            ext_le_rev = (t["j"][5].upper() <= opnorms.raw_kernel_norm(5, emax).upper()
                          and t["k"][6].upper() <= opnorms.kernel_norm(6).upper()
                          and H6.sup_S0_on(5, l, r).upper() <= opnorms.sup_source_derivative(5).upper())
            import math
            lo, hi = sharp_norms._window(l, r)
            a, b = float(lo.mid()), float(hi.mid())
            nn = 20000
            h = (b - a) / nn
            quad = sum(abs((x ** 6 - 15 * x ** 4 + 45 * x * x - 15) * math.exp(-x * x / 2) / math.sqrt(2 * math.pi)) * h
                       for x in (a + (i + 0.5) * h for i in range(nn)))
            cells.append({"cell": [left, right], "frozen_orders_0_4_identical": compat, "extension_le_reviewed": ext_le_rev,
                          "j5": float(t["j"][5].upper()), "k6": float(t["k"][6].upper()),
                          "float_quadrature_int_W_abs_He6_phi": quad,
                          "certified_moment_dominates_quadrature": float(H6.absolute_hermite_moment6(lo, hi).upper()) >= quad * (1 - 1e-6)})
        try:
            balls = H6.root_balls(256)
            H6._interior(balls, balls[3], balls[3] + H6.exact(1))
            straddle = False
        except H6.HermiteExtensionRefusal:
            straddle = True
    return {"verification": ver, "cells": cells, "straddle_refused": straddle,
            "pass": ver["pass"] and straddle and all(c["frozen_orders_0_4_identical"] and c["extension_le_reviewed"]
                                                     and c["certified_moment_dominates_quadrature"] for c in cells)}


def _synth_payload(cert, residuals, inputs, gout, sout):
    import rung3_engine as R1E
    q = lambda x: str(R1E.fraction_of(x.abs_upper()))
    return {"residuals": {n: [q(v[i]) for i in range(3)] for n, e in sorted(inputs["res"].items()) for v in [e["mid"]]},
            "cell_residuals": {n: [q(v[i]) for i in range(3)] for n, e in sorted(inputs["res"].items()) for v in [e["cell"]]},
            "graded_rad_mid": {str(m): q(v) for m, v in gout["rad_mid"].items()},
            "graded_rad_cell": {str(m): q(v) for m, v in gout["rad_cell"].items()},
            "scalar_rad_mid": {str(m): q(v) for m, v in sout["rad_mid"].items()},
            "scalar_rad_cell": {str(m): q(v) for m, v in sout["rad_cell"].items()}}


def part_synthetic_real(proto, args):
    import graded_dag as G
    import graded_real as GR
    import synthetic_real as SR
    from intervals import workprec
    t0 = time.process_time()
    cert, residuals = SR.build(int(proto["synthetic_seed"]))
    t_build = time.process_time() - t0
    certs = GR.load_certificates()
    refs = SR.float_references(cert)
    with workprec(256):
        inputs = GR.graded_inputs(cert, residuals, left=F(SR.CELL["left"][0]), right=F(SR.CELL["right"][0]),
                                  certificates=certs)
        c1 = SR.scalar_equivalence(cert, residuals, inputs)
        gout = G.certify_graded(inputs, parity=True)
        sout = G.certify_graded(inputs, parity=False)
        c5 = [m for m in gout["rad_mid"] if not (gout["rad_mid"][m].upper() <= sout["rad_mid"][m].upper()
                                               and gout["rad_cell"][m].upper() <= sout["rad_cell"][m].upper())]
        payload = _synth_payload(cert, residuals, inputs, gout, sout)
    c23 = SR.graded_residual_checks(inputs, refs)
    c6 = SR.candidate_parity_checks(GR, cert)
    c7 = SR.leibniz_checks(GR, cert, residuals)
    muts = {}
    if not args.no_mutations:
        for mut in proto["wiring_mutations"]:
            mod = load_mutant(NS / "code/graded_real.py", mut["old"], mut["new"], mut["id"])
            try:
                with workprec(256):
                    mi = mod.graded_inputs(cert, residuals, left=F(SR.CELL["left"][0]), right=F(SR.CELL["right"][0]),
                                           certificates=certs)
                    m1 = SR.scalar_equivalence(cert, residuals, mi)
                m23 = SR.graded_residual_checks(mi, refs)
                m6 = SR.candidate_parity_checks(mod, cert)
                m7 = SR.leibniz_checks(mod, cert, residuals)
                muts[mut["id"]] = {"detected": bool(m1 or m23 or m6 or m7), "c1": len(m1), "c23": len(m23),
                                   "c6": len(m6), "c7": len(m7), "first": (m1 or m23 or m6 or m7)[:1]}
            except Exception as exc:
                muts[mut["id"]] = {"detected": False, "crashed": f"{type(exc).__name__}: {str(exc)[:150]}"}
    return {"C1_scalar_equivalence_problems": c1[:20], "C1_count": len(c1),
            "C2C3_graded_residual_violations": c23[:20], "C2C3_count": len(c23),
            "C6_candidate_parity_violations": c6[:20], "C6_count": len(c6),
            "C7_leibniz_structure_problems": c7[:20], "C7_count": len(c7),
            "C5_graded_looser_m": [str(m) for m in c5], "residual_names": len(residuals),
            "payload_sha256": sha(canonical(payload)), "payload": payload, "mutations": muts,
            "cpu_build_seconds": t_build}


def part_parity(proto, args):
    import synthetic_real as SR
    v = SR.parity_identity_checks(None)
    return {"violations": v, "pass": not v}


def part_first_cell(proto, args):
    import first_cell as FC
    import r5_majorant as R5
    rows = [FC.run(spec) for spec in proto["first_cell_fixtures"]]
    lemma = FC.evenness_lemma_check(int(proto["lemma_seed"]))
    muts = {}
    for mut in proto["r5_mutations"]:
        mod = load_mutant(NS / "code/r5_majorant.py", mut["old"], mut["new"], mut["id"])
        hits = []
        for fid in proto["r5_mutation_trials"]:
            spec = next(f for f in proto["first_cell_fixtures"] if f["id"] == fid)
            try:
                r = FC.run(spec, r5=mod)
                det = r["violation_count"] > 0
                hits.append({"trial": fid, "violations": r["violation_count"], "first": r["violations"][:1]})
            except Exception as exc:
                det = False
                hits.append({"trial": fid, "crashed": str(exc)[:150]})
            if det:
                break
        muts[mut["id"]] = {"detected": any(h.get("violations", 0) > 0 for h in hits), "trials": hits}
    payload = [{"id": r["id"], "radii": r["radii"]} for r in rows]
    return {"rows": rows, "lemma": lemma, "mutations": muts, "payload_sha256": sha(canonical(payload))}


def part_forecast(proto, args):
    import cell0_forecast_r3 as CF
    fc = json.loads(json.dumps(CF.compute(), default=str))
    return {"forecast": fc, "payload_sha256": sha(canonical(fc))}


def part_r2_regression(proto, args):
    import qualify_r2 as Q2
    r2proto = json.loads((R2_NS / "config/QUALIFICATION_PROTOCOL_R2.json").read_text())
    body = Q2.part_graded_soundness(r2proto, args)
    return {"rows": [{k: r[k] for k in ("id", "graded_violation_count", "scalar_violation_count", "graded_never_looser")}
                     for r in body["rows"]],
            "pass": all(r["graded_violation_count"] == 0 and r["scalar_violation_count"] == 0 and r["graded_never_looser"]
                        for r in body["rows"])}


def part_failclosed(proto, args):
    import graded_real as GR
    import graded_dag as G
    import resolvent_certificate as RC
    out = {}
    rec0 = (CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json").read_bytes()
    for name, auth, rb in (("no_authorization", None, rec0), ("forged_authorization", {"cells": [0]}, rec0),
                           ("gate_precedes_record_validation", None, b"garbage")):
        try:
            GR.certify_real_cell_r3(0, authorization=auth, record_bytes=rb)
            out[name] = {"pass": False}
        except GR.R3Refusal as exc:
            out[name] = {"pass": str(exc).startswith("REAL_CELL_NOT_AUTHORIZED"), "refused": str(exc)}
    tmp = Path(tempfile.mkdtemp(prefix="o3r3fc-"))
    reg = json.loads((NS / "config/OPERATOR_CERTIFICATES_R3.json").read_text())
    reg["certificates"] = [e for e in reg["certificates"] if e["name"] != "C_o0"]
    (tmp / "reg.json").write_text(json.dumps(reg))
    mod = load_mutant(NS / "code/graded_real.py", 'CERT_REGISTRY = NS / "config/OPERATOR_CERTIFICATES_R3.json"',
                      f'CERT_REGISTRY = Path("{tmp / "reg.json"}")', "fc_missing_Co0")
    for label, m in (("missing_C_o0_registry_bytes_changed", mod),):
        try:
            m.load_certificates()
            out[label] = {"pass": False}
        except m.R3Refusal as exc:
            out[label] = {"pass": True, "refused": str(exc)}
    src = (NS / "code/graded_real.py").read_text()
    pinned = src.split('CERT_REGISTRY_SHA256 = "')[1].split('"')[0]
    mod2 = load_mutant(NS / "code/graded_real.py", f'CERT_REGISTRY_SHA256 = "{pinned}"',
                       f'CERT_REGISTRY_SHA256 = "{sha((tmp / "reg.json").read_bytes())}"', "fc_missing_Co0_repinned")
    mod2b = load_mutant(Path(mod2.__file__), 'CERT_REGISTRY = NS / "config/OPERATOR_CERTIFICATES_R3.json"',
                        f'CERT_REGISTRY = Path("{tmp / "reg.json"}")', "fc_missing_Co0_repinned_b")
    try:
        mod2b.load_certificates()
        out["missing_C_o0_even_if_repinned"] = {"pass": False}
    except mod2b.R3Refusal as exc:
        out["missing_C_o0_even_if_repinned"] = {"pass": "MISSING_OPERATOR_CERTIFICATE C_o0" in str(exc), "refused": str(exc)}
    art = json.loads((NS / proto["certificate_artifacts"]["C_o0"]).read_text())
    art["certified"]["C_upper_bound"] = "4"
    v = RC.verify_artifact(art)
    out["tampered_certificate_value_detected"] = {"pass": not v["identical"]}
    try:
        from intervals import workprec
        with workprec(256):
            G.certify_graded({"C": G.R1E.exact(1)})
        out["engine_missing_inputs"] = {"pass": False}
    except G.ProducerRefusal:
        out["engine_missing_inputs"] = {"pass": True}
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
    for label, pins in (("r1_immutable", proto["r1_bound_sha256"]), ("r2_immutable", proto["r2_bound_sha256"])):
        moved = [rel for rel, h in pins.items() if sha((REPO / rel).read_bytes()) != h]
        out[label] = {"pass": not moved, "moved": moved}
    tree = ast.parse((code / "graded_real.py").read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "certify_real_cell_r3")
    first = fn.body[0]
    out["authorization_gate_first"] = {"pass": isinstance(first, ast.Assign) and "AUTH_REGISTRY" in ast.unparse(first)}
    auth = json.loads((NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY_R3.json").read_text())
    src = (code / "graded_real.py").read_text()
    out["registries_pinned_auth_empty"] = {"pass": auth["authorizations"] == []
                                           and sha((NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY_R3.json").read_bytes()) in src
                                           and sha((NS / "config/OPERATOR_CERTIFICATES_R3.json").read_bytes()) in src}
    return {"checks": out, "pass": all(v["pass"] for v in out.values())}


PARTS = {"certificates": part_certificates, "certificate_mutations": part_certificate_mutations, "he6": part_he6,
         "synthetic_real": part_synthetic_real, "parity": part_parity, "first_cell": part_first_cell,
         "forecast": part_forecast, "r2_regression": part_r2_regression, "failclosed": part_failclosed,
         "fence": part_fence}


def run_part(args):
    proto = load_protocol()
    t0, w0 = time.process_time(), time.time()
    body = PARTS[args.part](proto, args)
    rec = {"part": args.part, "argv": sys.argv[2:], "runtime": runtime(), "body": body,
           "protocol_sha256": sha(PROTOCOL.read_bytes()),
           "metadata": {"cpu_seconds": time.process_time() - t0, "wall_seconds": time.time() - w0,
                        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")


def jobs(proto, outdir):
    J = [["part", "synthetic_real", "--out", str(outdir / "part_synthetic_real.json")],
         ["part", "synthetic_real", "--no-mutations", "--out", str(outdir / "part_synthetic_real_replay.json")]]
    for n in ("certificates", "certificate_mutations", "he6", "parity", "first_cell", "forecast", "r2_regression",
              "failclosed", "fence"):
        J.append(["part", n, "--out", str(outdir / f"part_{n}.json")])
    J.append(["part", "forecast", "--out", str(outdir / "part_forecast_replay.json")])
    return J


def cmd_run(args):
    proto = load_protocol()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONHASHSEED="0")
    for k in ("O3_DEV_PROTOCOL_PATH", "O3R2_DEV_PROTOCOL_PATH"):
        env.pop(k, None)
    pending = [[sys.executable, "-B", str(Path(__file__).resolve())] + j for j in jobs(proto, outdir)]
    running, failures = [], []
    while pending or running:
        while pending and len(running) < int(args.workers):
            cmd = pending.pop(0)
            running.append((cmd, subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)))
        time.sleep(1)
        for item in list(running):
            cmd, p = item
            if p.poll() is not None:
                running.remove(item)
                log = p.stdout.read().decode(errors="replace")
                if p.returncode != 0:
                    failures.append({"cmd": cmd[3:], "rc": p.returncode, "log": log[-3000:]})
    result = assemble(proto, outdir)
    result["runner_failures"] = failures
    (outdir / "QUALIFICATION_RESULT_R3.json").write_text(json.dumps(result, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"verdicts": result["verdicts"], "runner_failures": len(failures)}, indent=1))


def rd(outdir, name):
    return json.loads((outdir / name).read_text())


def assemble(proto, outdir):
    names = ["synthetic_real", "synthetic_real_replay", "certificates", "certificate_mutations", "he6", "parity",
             "first_cell", "forecast", "forecast_replay", "r2_regression", "failclosed", "fence"]
    P = {n: rd(outdir, f"part_{n}.json") for n in names}
    parts = {f"part_{n}.json": sha((outdir / f"part_{n}.json").read_bytes()) for n in names}
    B = {n: p["body"] for n, p in P.items()}
    runtimes_ok = all(all(p["runtime"].get(k) == v for k, v in proto["runtime_contract"].items()) for p in P.values())
    protocol_ok = all(p["protocol_sha256"] == sha(PROTOCOL.read_bytes()) for p in P.values())
    sr = B["synthetic_real"]
    wiring_req = [m["id"] for m in proto["wiring_mutations"] if m["required"]]
    r5_req = [m["id"] for m in proto["r5_mutations"] if m["required"]]
    cert_req = [m["id"] for m in proto["certificate_mutations"] if m["required"]]
    fc_rows = B["first_cell"]["rows"]
    G = {
        "R01_R1_R2_preserved": B["fence"]["checks"]["r1_immutable"]["pass"] and B["fence"]["checks"]["r2_immutable"]["pass"],
        "R02_C_o0_certificate_replayed": B["certificates"]["checks"]["C_o0"]["pass"],
        "R03_C_e0_certificate_replayed": B["certificates"]["checks"]["C_e0"]["pass"],
        "R04_certificate_registry_consistent": B["certificates"]["checks"]["registry_consistent"]["pass"],
        "R05_sigma_invariance_real_kernels": B["parity"]["pass"],
        "R06_real_graded_wiring_scalar_equivalence": sr["C1_count"] == 0 and sr["C7_count"] == 0,
        "R07_real_graded_residual_containment": sr["C2C3_count"] == 0 and sr["C6_count"] == 0,
        "R08_graded_never_looser": not sr["C5_graded_looser_m"],
        "R09_he6_j5_extension": B["he6"]["pass"],
        "R10_first_cell_manufactured_soundness": all(r["violation_count"] == 0 for r in fc_rows),
        "R11_evenness_lemma_independent_check": B["first_cell"]["lemma"]["pass"],
        "R12_mutation_suites": all(sr["mutations"][i]["detected"] for i in wiring_req)
        and all(B["first_cell"]["mutations"][i]["detected"] for i in r5_req)
        and all(B["certificate_mutations"]["rows"][i]["detected"] for i in cert_req)
        and B["certificate_mutations"]["rows"]["frozen_verifier_rejects_bad_payload"]["pass"],
        "R13_determinism": sr["payload_sha256"] == B["synthetic_real_replay"]["payload_sha256"]
        and B["forecast"]["payload_sha256"] == B["forecast_replay"]["payload_sha256"]
        and all(B["certificates"]["checks"][n]["identical"] for n in ("C_o0", "C_e0")),
        "R14_fail_closed": B["failclosed"]["pass"],
        "R15_fences_and_registries": B["fence"]["pass"] and protocol_ok,
        "R16_runtime_identity": runtimes_ok,
        "R17_r2_graded_regression": B["r2_regression"]["pass"],
    }
    G = {k: "PASS" if v else "FAIL" for k, v in G.items()}
    fc = B["forecast"]["forecast"]
    binding = fc["sweep"]["1"]["m"]["1"]
    order = ["PROMISING", "MARGINAL", "UNINFORMATIVE", "STRUCTURALLY_BLOCKED"]
    counts = {
        "wiring_mutations": f"{sum(1 for i in wiring_req if sr['mutations'][i]['detected'])}/{len(wiring_req)} required, "
                            f"{sum(1 for m in sr['mutations'].values() if m['detected'])}/{len(sr['mutations'])} total",
        "r5_mutations": f"{sum(1 for i in r5_req if B['first_cell']['mutations'][i]['detected'])}/{len(r5_req)} required",
        "certificate_mutations": f"{sum(1 for i in cert_req if B['certificate_mutations']['rows'][i]['detected'])}/{len(cert_req)} required",
    }
    manufactured = [{"id": r["id"], "C_e0": r["C_e0"], "C_o0": r["C_o0"],
                     "m1": {k: r["radii"]["1"][k] for k in ("radius_A", "radius_B_point", "penalty_B", "radius_B", "M5", "true_max_abs_R5")}}
                    for r in fc_rows]
    return {"schema": "rebaseguard.p5y.k5.order3-r3.qualification-result.v1", "protocol_sha256": sha(PROTOCOL.read_bytes()),
            "part_sha256": parts, "gates": G, "counts": counts, "verdicts": G,
            "certificates": {n: {k: B["certificates"]["checks"][n][k] for k in ("C_float", "C_upper_bound", "margin_lower")}
                             for n in ("C_o0", "C_e0")},
            "wiring_mutations": sr["mutations"], "r5_mutations": {k: v["detected"] for k, v in B["first_cell"]["mutations"].items()},
            "certificate_mutations": B["certificate_mutations"]["rows"],
            "he6": {"verification": B["he6"]["verification"], "cells": B["he6"]["cells"]},
            "first_cell_manufactured": manufactured, "forecast_binding_g1_m1": binding,
            "forecast_S_star": fc["S_star"], "forecast_diagnostics": fc["diagnostics_g1_m1"],
            "strategy_A_class": binding["strategy_A_class"], "strategy_B_class": binding["strategy_B_class"],
            "preferred_strategy": ("B" if binding["strategy_B_radius"] < binding["strategy_A_radius"] else "A")
            if order.index(binding["strategy_B_class"]) <= order.index(binding["strategy_A_class"]) else "A",
            "real_cell_qualification": "NOT_AUTHORIZED", "real_k5_scientific_cell_evaluated": "NO"}


def cmd_check(args):
    proto = load_protocol()
    outdir = Path(args.outdir)
    stored = json.loads((outdir / "QUALIFICATION_RESULT_R3.json").read_text())
    problems = [] if PROTOCOL == FROZEN_PROTOCOL else ["not the frozen protocol"]
    for label in ("bound_code_sha256", "r1_bound_sha256", "r2_bound_sha256"):
        problems += [f"{label} moved: {rel}" for rel, h in proto[label].items() if sha((REPO / rel).read_bytes()) != h]
    again = assemble(proto, outdir)
    for key in ("gates", "part_sha256", "protocol_sha256", "counts"):
        if again[key] != stored[key]:
            problems.append(f"recomputed {key} differs")
    print(json.dumps({"problems": problems, "verdicts": again["verdicts"], "counts": again["counts"]}, indent=1))
    sys.exit(1 if problems else 0)


def main():
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


if __name__ == "__main__":
    main()
