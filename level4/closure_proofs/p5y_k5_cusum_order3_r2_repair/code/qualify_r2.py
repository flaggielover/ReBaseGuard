"""R2 qualification runner (config/QUALIFICATION_PROTOCOL_R2.json). NON-SCIENTIFIC.

    python -B code/qualify_r2.py run   --outdir evidence/qualification_r2 --workers 4
    python -B code/qualify_r2.py check --outdir evidence/qualification_r2

R1 is immutable: its producer and its part functions are imported from p5y_k5_cusum_order3_real_producer/code and
called as a library with the R2 protocol (same keys). R2 adds the R05 isolating fixture (inside QM and as its own
invariant part) and the graded-method parts. Every part runs in a fresh interpreter.
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
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = REPO / "level4/closure_proofs"
R1_NS = CP / "p5y_k5_cusum_order3_real_producer"
sys.path.insert(0, str(NS / "code"))
sys.path.insert(1, str(R1_NS / "code"))

import qualify_order3 as Q1  # noqa: E402  (R1 runner as a library; its globals are not used for R2 verdicts)

FROZEN_PROTOCOL = NS / "config/QUALIFICATION_PROTOCOL_R2.json"
PROTOCOL = Path(os.environ.get("O3R2_DEV_PROTOCOL_PATH", str(FROZEN_PROTOCOL)))    # dev calibration only


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_protocol() -> dict:
    return json.loads(PROTOCOL.read_text())


def q(x: Fr) -> str:
    return f"{x.numerator}/{x.denominator}"


# ------------------------------------------------------------------ R1-producer fixtures incl. the R05 isolating one
def evaluate(spec: dict, *, bits: int, engine=None, residual=None, ablation=None, check_truth=True) -> dict:
    if spec["kind"] != "r05_isolating":
        return Q1.evaluate_fixture(spec, bits=bits, engine=engine, residual=residual, check_truth=check_truth)
    import r05_fixture as R05
    import rung3_engine as E
    import rung3_residual as RR
    import soundness as SD
    from run_fixture import certify_fixture
    engine = E if engine is None else engine
    residual = RR if residual is None else residual
    sysm, e0, rho, rig = R05.build_rig(spec, ablation=ablation)
    try:
        _rig, g, res, _cpu = certify_fixture(sysm, e0, rho, seed=0, noise=Fr(0), bits=bits, engine=engine,
                                             residual=residual, rig=rig)
    except E.ProducerRefusal as exc:
        return {"id": spec["id"], "refused": str(exc), "violations": [], "bits": bits}
    except Exception as exc:
        return {"id": spec["id"], "crashed": f"{type(exc).__name__}: {exc}", "violations": [], "bits": bits}
    viol = SD.violations(sysm, rig, res) if check_truth else []
    per_m = {}
    for m in E.M_VALUES:
        L, U = res["m"][m]["R3_cell"]
        mlo, mhi = res["m"][m]["R3_mid"]
        per_m[str(m)] = {"L": q(L), "U": q(U), "width": q(U - L), "mid_width": q(mhi - mlo),
                         "sign_status": E.sign_status(L, U)}
    payload = E.scientific_payload(res, {"fixture": spec, "ablation": ablation, "kind": "MANUFACTURED_NON_SCIENTIFIC"})
    return {"id": spec["id"], "bits": bits, "violations": viol, "per_m": per_m, "noise": "0",
            "max_G_residual_delta_mid": q(max(E.upper_fraction(g[r]["delta_mid"]) for r in range(5))),
            "scientific_hash": E.scientific_hash(payload), "ablation": ablation}


def fixture(proto, fid):
    return next(f for f in proto["fixtures"] if f["id"] == fid)


def part_soundness(proto, args):
    return {"rows": [evaluate(f, bits=256) for f in proto["fixtures"]]}


def part_determinism(proto, args):
    return {"hashes": {f["id"]: evaluate(f, bits=256, check_truth=False).get("scientific_hash")
                       for f in proto["fixtures"]}}


def part_mutation(proto, args):
    import rung3_engine as E
    import rung3_residual as RR
    mut = next(m for m in proto["mutations"] if m["id"] == args.mutation)
    mod = Q1._load_mutant(mut["target"], mut["old"], mut["new"], mut["id"])
    eng = mod if mut["target"] == "rung3_engine.py" else E
    resid = mod if mut["target"] == "rung3_residual.py" else RR
    hits = []
    for fid in proto["mutation_trials"]:
        spec = fixture(proto, fid)
        row = evaluate(spec, bits=256, engine=eng, residual=resid)
        consistency = None
        if Fr(spec.get("noise", "0")) == 0 and "max_G_residual_delta_mid" in row and spec["kind"] != "r05_isolating":
            consistency = Fr(row["max_G_residual_delta_mid"]) <= Fr(proto["residual_consistency_threshold"])
        detected = bool(row["violations"]) or consistency is False
        hits.append({"trial": fid, "violations": len(row["violations"]), "first": row["violations"][:1],
                     "residual_consistency": consistency, "refused": row.get("refused"),
                     "crashed": row.get("crashed"), "detected": detected})
        if detected:
            break
    return {"mutation": mut["id"], "detected": any(h["detected"] for h in hits), "trials": hits}


def part_r05(proto, args):
    import rung3_engine as E
    import rung3_residual as RR
    spec = fixture(proto, proto["r05_fixture"])
    mut = next(m for m in proto["mutations"] if m["id"] == "R05_RESIDUAL_R0_USES_CANDIDATE_SOURCE")
    mod = Q1._load_mutant(mut["target"], mut["old"], mut["new"], "R05_iso")
    rows = {}
    for abl in (None, "ABL_ZERO_OFFSET", "ABL_RESOLVE_CLOSED"):
        for label, resid in (("unmutated", RR), ("R05", mod)):
            r = evaluate(spec, bits=256, residual=resid, ablation=abl)
            rows[f"{abl or 'FIXTURE'}:{label}"] = {"violations": len(r["violations"]), "refused": r.get("refused"),
                                                   "crashed": r.get("crashed"), "first": r["violations"][:1]}
    inv = proto["r05_invariants"]
    checks = {key: (rows[key]["violations"] > 0 if want == "positive" else rows[key]["violations"] == 0)
              and rows[key]["refused"] is None and rows[key]["crashed"] is None
              for key, want in inv.items()}
    return {"rows": rows, "invariants": checks, "pass": all(checks.values())}


# ------------------------------------------------------------------ graded method parts
def graded_eval(spec, *, bits=256, parity=True, graded_module=None, truth=True):
    import graded_dag as G0
    import rung3_engine as R1E
    import sigma_systems as SS
    G = G0 if graded_module is None else graded_module
    sysm = SS.build(spec)
    pert = None
    if "perturb" in spec:
        pert = (int(spec["perturb"][0]), [Fr(x) for x in spec["perturb"][1]])
    gr = SS.GradedRig(sysm, Fr(spec["e0"]), Fr(spec["rho"]), seed=int(spec["seed"]), noise=Fr(spec.get("noise", "0")),
                      perturb=pert)
    t0 = time.process_time()
    try:
        with R1E.precision(bits):
            out = G.certify_graded(gr.engine_inputs(graded=G), bits=bits, parity=parity)
    except Exception as exc:
        return {"id": spec["id"], "crashed": f"{type(exc).__name__}: {exc}", "violations": []}
    cpu = time.process_time() - t0
    viol = SS.graded_violations(gr, out, parity=parity) if truth else []
    fl = lambda d: {str(m): q(R1E.fraction_of(v)) for m, v in d.items()}
    nodes = {w: {n: [q(R1E.fraction_of(v.e)), q(R1E.fraction_of(v.o)), q(R1E.fraction_of(v.t))]
                 for n, v in sorted(out[w]["nodes"].items())} for w in ("mid", "cell")}
    payload = {"schema": "rebaseguard.p5y.k5.order3-r2.graded-payload.v1", "fixture": spec, "parity": parity,
               "bits": bits, "rad_mid": fl(out["rad_mid"]), "rad_cell": fl(out["rad_cell"]), "nodes": nodes,
               "export": {str(m): [q(v["R3_cell"][0]), q(v["R3_cell"][1])] for m, v in out["m"].items()},
               "resolvent_mode": [out["mid"]["resolvent"]["mode"], out["cell"]["resolvent"]["mode"]]}
    return {"id": spec["id"], "parity": parity, "violations": viol, "rad_mid": payload["rad_mid"],
            "rad_cell": payload["rad_cell"], "resolvent_mode": payload["resolvent_mode"], "cpu_seconds": cpu,
            "C": float(gr.C), "C_e0": float(gr.C_e0), "C_o0": float(gr.C_o0), "eta_cell": float(gr.eta_cell),
            "nodes": nodes, "hash": R1E_hash(payload)}


def R1E_hash(payload):
    import rung3_engine as R1E
    return R1E.scientific_hash(payload)


def part_graded_soundness(proto, args):
    rows = []
    for spec in proto["sigma_fixtures"]:
        s = graded_eval(spec, parity=False)
        g = graded_eval(spec, parity=True)
        never_looser = "crashed" not in g and "crashed" not in s and all(
            Fr(g["nodes"][w][n][0]) <= Fr(s["nodes"][w][n][2]) and Fr(g["nodes"][w][n][1]) <= Fr(s["nodes"][w][n][2])
            and Fr(g["nodes"][w][n][2]) <= Fr(s["nodes"][w][n][2]) for w in ("mid", "cell") for n in g["nodes"][w]) \
            and all(Fr(g[k][m]) <= Fr(s[k][m]) for k in ("rad_mid", "rad_cell") for m in g[k])
        rows.append({"id": spec["id"], "scalar_violations": s["violations"][:3], "graded_violations": g["violations"][:3],
                     "scalar_violation_count": len(s["violations"]), "graded_violation_count": len(g["violations"]),
                     "crashed": [x.get("crashed") for x in (s, g) if x.get("crashed")], "graded_never_looser": never_looser,
                     "C": g.get("C"), "C_e0": g.get("C_e0"), "C_o0": g.get("C_o0"), "eta_cell": g.get("eta_cell"),
                     "resolvent_mode": g.get("resolvent_mode"),
                     "rad_mid": {"scalar": s.get("rad_mid"), "graded": g.get("rad_mid")},
                     "rad_cell": {"scalar": s.get("rad_cell"), "graded": g.get("rad_cell")},
                     "contraction_mid_m1": (float(Fr(s["rad_mid"]["1"]) / Fr(g["rad_mid"]["1"]))
                                            if not s.get("crashed") and not g.get("crashed") and Fr(g["rad_mid"]["1"]) > 0 else None),
                     "contraction_cell_m1": (float(Fr(s["rad_cell"]["1"]) / Fr(g["rad_cell"]["1"]))
                                             if not s.get("crashed") and not g.get("crashed") and Fr(g["rad_cell"]["1"]) > 0 else None),
                     "hash_scalar": s.get("hash"), "hash_graded": g.get("hash")})
    return {"rows": rows}


def part_graded_determinism(proto, args):
    return {"hashes": {spec["id"]: graded_eval(spec, parity=True, truth=False).get("hash")
                       for spec in proto["sigma_fixtures"]}}


def part_graded_mutation(proto, args):
    mut = next(m for m in proto["graded_mutations"] if m["id"] == args.mutation)
    src = (NS / "code" / mut["target"]).read_text()
    if src.count(mut["old"]) != 1:
        raise RuntimeError(f"anchor for {mut['id']} matches {src.count(mut['old'])} times")
    tmp = Path(tempfile.mkdtemp(prefix="o3gmut-")) / f"gm_{mut['id']}.py"
    tmp.write_text(src.replace(mut["old"], mut["new"]))
    spec_ = importlib.util.spec_from_file_location(f"gm_{mut['id']}", tmp)
    mod = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(mod)
    hits = []
    for fid in proto["graded_mutation_trials"]:
        spec = next(f for f in proto["sigma_fixtures"] if f["id"] == fid)
        r = graded_eval(spec, parity=True, graded_module=mod)
        det = bool(r["violations"])
        hits.append({"trial": fid, "violations": len(r["violations"]), "first": r["violations"][:1],
                     "crashed": r.get("crashed"), "detected": det})
        if det:
            break
    return {"mutation": mut["id"], "detected": any(h["detected"] for h in hits), "trials": hits}


def part_graded_precision(proto, args):
    spec = next(f for f in proto["sigma_fixtures"] if f["id"] == args.fixture)
    r = graded_eval(spec, bits=args.bits, parity=True)
    r["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    r.pop("nodes", None)
    return r


def part_graded_failclosed(proto, args):
    import graded_dag as G
    import rung3_engine as R1E
    import sigma_systems as SS
    from flint import arb
    spec = next(f for f in proto["sigma_fixtures"] if f["id"] == proto["graded_failclosed_base"])
    gr = SS.GradedRig(SS.build(spec), Fr(spec["e0"]), Fr(spec["rho"]), seed=int(spec["seed"]),
                      noise=Fr(spec.get("noise", "0")))
    out = {}

    def expect(name, mutate, exc=R1E.ProducerRefusal):
        with R1E.precision(256):
            inp = gr.engine_inputs()
            mutate(inp)
            try:
                G.certify_graded(inp)
            except exc as e:
                out[name] = {"pass": True, "refused": str(e)[:160]}
                return
            except Exception as e:
                out[name] = {"pass": False, "wrong_exception": f"{type(e).__name__}: {e}"}
                return
        out[name] = {"pass": False}

    expect("GF01_missing_hull_norms", lambda i: i.pop("k_hull"))
    expect("GF02_x0_not_sigma_fixed", lambda i: i.pop("x0_sigma_fixed"))
    expect("GF03_nonfinite_C_o0", lambda i: i.__setitem__("C_o0", arb("inf")))
    expect("GF04_nan_residual", lambda i: i["res"].__setitem__("F_0:3", {"mid": (arb("nan"),) * 3,
                                                                        "cell": (arb("nan"),) * 3}))
    expect("GF05_missing_residual", lambda i: i["res"].pop("W_0_1:2"), KeyError)
    try:
        with R1E.precision(100):
            pass
        out["GF06_precision_outside_set"] = {"pass": False}
    except R1E.ProducerRefusal:
        out["GF06_precision_outside_set"] = {"pass": True}
    # a huge odd resolvent certificate must fall back toward scalar, never produce a smaller radius than scalar
    with R1E.precision(256):
        inp = gr.engine_inputs()
        inp["C_o0"] = R1E.exact(10 ** 9)
        big = G.certify_graded(inp)
        sc = G.certify_graded(gr.engine_inputs(), parity=False)
    out["GF07_bad_certificate_never_below_scalar_cap"] = {
        "pass": all(R1E.fraction_of(big["rad_mid"][m]) <= R1E.fraction_of(sc["rad_mid"][m]) for m in big["rad_mid"])}
    import cusum_graded as CG
    for name, kw in (("GF08_real_front_end_no_authorization", {"authorization": None, "operator_certificate": None}),
                     ("GF09_real_front_end_forged_authorization",
                      {"authorization": {"cells": [0]}, "operator_certificate": {"C_o0": "5"}})):
        try:
            CG.certify_real_cell_r2(0, record_bytes=b"", **kw)
            out[name] = {"pass": False}
        except CG.R2Refusal as e:
            out[name] = {"pass": str(e).startswith("REAL_CELL_NOT_AUTHORIZED"), "refused": str(e)}
    reg_a = json.loads(CG.AUTH_REGISTRY.read_text())
    reg_o = json.loads(CG.OPERATOR_CERT_REGISTRY.read_text())
    out["GF10_registries_empty_and_pinned"] = {
        "pass": reg_a["authorizations"] == [] and reg_o["certificates"] == []
        and sha(CG.AUTH_REGISTRY.read_bytes()) == CG.AUTH_REGISTRY_SHA256
        and sha(CG.OPERATOR_CERT_REGISTRY.read_bytes()) == CG.OPERATOR_CERT_REGISTRY_SHA256}
    return {"checks": out}


def part_method_comparison(proto, args):
    rows = []
    for fid in proto["stress_fixtures"]:
        spec = next(f for f in proto["sigma_fixtures"] if f["id"] == fid)
        s = graded_eval(spec, parity=False, truth=False)
        g = graded_eval(spec, parity=True, truth=False)
        low = dict(spec, noise=str(Fr(spec.get("noise", "0")) / 10), id=spec["id"] + "_noise_div10")
        s10 = graded_eval(low, parity=False, truth=False)
        cat = lambda x: next(c["label"] for c in proto["feasibility_criterion"]["categories"] if x >= c["min"])
        cm = float(Fr(s["rad_mid"]["1"]) / Fr(g["rad_mid"]["1"]))
        cc = float(Fr(s["rad_cell"]["1"]) / Fr(g["rad_cell"]["1"]))
        rows.append({"id": fid, "C": g["C"], "C_e0": g["C_e0"], "C_o0": g["C_o0"],
                     "method_1_scalar_generic": {"mid": s["rad_mid"]["1"], "cell": s["rad_cell"]["1"]},
                     "method_2_graded_parity": {"mid": g["rad_mid"]["1"], "cell": g["rad_cell"]["1"]},
                     "method_3_residual_correction_emulated_noise_div10_scalar": {"mid": s10["rad_mid"]["1"],
                                                                                 "cell": s10["rad_cell"]["1"]},
                     "contraction_mid": cm, "contraction_cell": cc,
                     "category_mid": cat(cm), "category_cell": cat(cc)})
    return {"rows": rows}


def part_operator_parity(proto, args):
    import operator_parity_integration as OPI
    watch = Q1._watch_forbidden(proto)
    rows = []
    with watch:
        for seed in proto["operator_parity_seeds"]:
            r = OPI.run(int(seed))
            rows.append({k: v for k, v in r.items() if k not in ("P1", "P2")})
    return {"rows": rows, "forbidden_calls": watch.hits}


def part_forecast(proto, args):
    import cell0_forecast as CF
    watch = Q1._watch_forbidden(proto)
    with watch:
        fc = json.loads(json.dumps(CF.compute()))
    return {"forecast": fc, "forbidden_calls": watch.hits}


def part_fence_r2(proto, args):
    out = {}
    code = NS / "code"
    for mod in proto["r2_pure_modules"]:
        tree = ast.parse((code / mod).read_text())
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module.split(".")[0])
        bad = sorted(names & set(proto["r2_forbidden_imports_pure"]))
        out[mod] = {"forbidden": bad, "pass": not bad}
    spec = importlib.util.spec_from_file_location("no_monkeypatch", CP / "p5y_k1_cusum_aux3_successor/code/no_monkeypatch.py")
    sys.path.append(str(CP / "p5y_k1_cusum_aux3_successor/code"))
    nm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nm)
    findings = []
    for f in sorted(code.glob("*.py")):
        findings += nm.scan_source(f.read_text(), f.name)
    out["no_monkeypatch_r2"] = {"pass": not findings, "findings": findings}
    moved = [rel for rel, h in proto["r1_bound_sha256"].items() if sha((REPO / rel).read_bytes()) != h]
    out["r1_immutable"] = {"pass": not moved, "moved": moved}
    tree = ast.parse((code / "cusum_graded.py").read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "certify_real_cell_r2")
    first = fn.body[0]
    out["r2_authorization_gate_first"] = {"pass": isinstance(first, ast.Assign) and isinstance(first.value, ast.Call)
                                          and getattr(first.value.func, "id", None) == "_pinned"
                                          and "AUTH" in ast.unparse(first.value)}
    return {"checks": out}


PARTS = {"soundness": part_soundness, "determinism": part_determinism, "mutation": part_mutation, "r05": part_r05,
         "precision": lambda p, a: Q1.part_precision(p, a), "crosscheck": lambda p, a: Q1.part_crosscheck(p, a),
         "reference": lambda p, a: Q1.part_reference(p, a), "operator": lambda p, a: Q1.part_operator(p, a),
         "failclosed": lambda p, a: Q1.part_failclosed(p, a), "realgate": lambda p, a: Q1.part_realgate(p, a),
         "k1": lambda p, a: Q1.part_k1(p, a), "fence": lambda p, a: Q1.part_fence(p, a),
         "graded_soundness": part_graded_soundness, "graded_determinism": part_graded_determinism,
         "graded_mutation": part_graded_mutation, "graded_precision": part_graded_precision,
         "graded_failclosed": part_graded_failclosed, "method_comparison": part_method_comparison,
         "operator_parity": part_operator_parity, "forecast": part_forecast, "fence_r2": part_fence_r2}
UNFENCED = {"operator", "realgate", "operator_parity", "forecast", "graded_failclosed"}


def run_part(args):
    proto = load_protocol()
    t0, w0 = time.process_time(), time.time()
    body = PARTS[args.part](proto, args)
    loaded = sorted(m for m in proto["forbidden_loaded_modules"] if m in sys.modules)
    rec = {"part": args.part, "argv": sys.argv[2:], "runtime": Q1.runtime(), "body": body,
           "protocol_sha256": sha(PROTOCOL.read_bytes()),
           "loaded_forbidden_modules": None if args.part in UNFENCED else loaded,
           "metadata": {"cpu_seconds": time.process_time() - t0, "wall_seconds": time.time() - w0,
                        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")


def jobs(proto, outdir):
    J = [["part", n, "--out", str(outdir / f"part_{n}.json")] for n in
         ("soundness", "r05", "reference", "crosscheck", "failclosed", "realgate", "k1", "fence", "operator",
          "graded_soundness", "graded_failclosed", "method_comparison", "operator_parity", "forecast", "fence_r2")]
    for rep in (1, 2):
        J.append(["part", "determinism", "--out", str(outdir / f"part_determinism_{rep}.json")])
        J.append(["part", "graded_determinism", "--out", str(outdir / f"part_graded_determinism_{rep}.json")])
    for m in proto["mutations"]:
        J.append(["part", "mutation", "--mutation", m["id"], "--out", str(outdir / f"part_mutation_{m['id']}.json")])
    for m in proto["graded_mutations"]:
        J.append(["part", "graded_mutation", "--mutation", m["id"],
                  "--out", str(outdir / f"part_graded_mutation_{m['id']}.json")])
    for fid in proto["precision"]["fixtures"]:
        for b in proto["precision"]["bits"]:
            J.append(["part", "precision", "--fixture", fid, "--bits", str(b),
                      "--out", str(outdir / f"part_precision_{fid}_{b}.json")])
    for fid in proto["graded_precision_fixtures"]:
        for b in proto["precision"]["bits"]:
            J.append(["part", "graded_precision", "--fixture", fid, "--bits", str(b),
                      "--out", str(outdir / f"part_graded_precision_{fid}_{b}.json")])
    return J


def cmd_run(args):
    proto = load_protocol()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1", PYTHONHASHSEED="0")
    env.pop("O3_DEV_PROTOCOL_PATH", None)             # never let the R1 library read a DEV protocol
    pending = [[sys.executable, "-B", str(Path(__file__).resolve())] + j for j in jobs(proto, outdir)]
    running, failures = [], []
    while pending or running:
        while pending and len(running) < int(args.workers):
            cmd = pending.pop(0)
            running.append((cmd, subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)))
        time.sleep(0.5)
        for item in list(running):
            cmd, p = item
            if p.poll() is not None:
                running.remove(item)
                log = p.stdout.read().decode(errors="replace")
                if p.returncode != 0:
                    failures.append({"cmd": cmd[3:], "rc": p.returncode, "log": log[-3000:]})
    result = assemble(proto, outdir)
    result["runner_failures"] = failures
    (outdir / "QUALIFICATION_RESULT_R2.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdicts": result["verdicts"], "runner_failures": len(failures)}, indent=1))


def read(outdir, name):
    return json.loads((outdir / name).read_text())


def assemble(proto, outdir):
    parts = {p.name: sha(p.read_bytes()) for p in sorted(outdir.glob("part_*.json"))}
    snd, ref, xc, fc, rg, k1, fe, op = (read(outdir, f"part_{n}.json") for n in
                                         ("soundness", "reference", "crosscheck", "failclosed", "realgate", "k1",
                                          "fence", "operator"))
    r05, gs, gf, mc, opp, fcst, fe2 = (read(outdir, f"part_{n}.json") for n in
                                       ("r05", "graded_soundness", "graded_failclosed", "method_comparison",
                                        "operator_parity", "forecast", "fence_r2"))
    d1, d2 = read(outdir, "part_determinism_1.json"), read(outdir, "part_determinism_2.json")
    gd1, gd2 = read(outdir, "part_graded_determinism_1.json"), read(outdir, "part_graded_determinism_2.json")
    muts = {m["id"]: read(outdir, f"part_mutation_{m['id']}.json") for m in proto["mutations"]}
    gmuts = {m["id"]: read(outdir, f"part_graded_mutation_{m['id']}.json") for m in proto["graded_mutations"]}
    prec = {}
    for fid in proto["precision"]["fixtures"]:
        rows = {b: read(outdir, f"part_precision_{fid}_{b}.json")["body"] for b in proto["precision"]["bits"]}
        c = Q1.precision_classification(rows)
        c["midpoint_interval"] = Q1.precision_classification(rows, "mid_width")
        prec[fid] = c
    order = ["UNSTABLE", "INCONCLUSIVE", "STAGNATING", "CONTRACTING"]
    overall_prec = next((lab for lab in order if any(c["label"] == lab for c in prec.values())), "INCONCLUSIVE")
    gprec = {}
    for fid in proto["graded_precision_fixtures"]:
        rows = {b: read(outdir, f"part_graded_precision_{fid}_{b}.json")["body"] for b in proto["precision"]["bits"]}
        ws = [Fr(rows[b]["rad_cell"]["1"]) if not rows[b].get("crashed") and not rows[b]["violations"] else None
              for b in proto["precision"]["bits"]]
        wm = [Fr(rows[b]["rad_mid"]["1"]) if not rows[b].get("crashed") and not rows[b]["violations"] else None
              for b in proto["precision"]["bits"]]
        def lab(w):
            if None in w:
                return "UNSTABLE"
            if not all(w[i + 1] <= w[i] * (1 + Fr(1, 2 ** 64)) for i in range(len(w) - 1)):
                return "INCONCLUSIVE"
            return "CONTRACTING" if w[-1] < w[0] / 2 else "STAGNATING"
        gprec[fid] = {"cell_label": lab(ws), "mid_label": lab(wm), "rad_cell_m1": [None if x is None else float(x) for x in ws],
                      "rad_mid_m1": [None if x is None else float(x) for x in wm]}

    s_rows = snd["body"]["rows"]
    all_parts = [snd, ref, xc, fc, rg, k1, fe, op, d1, d2, r05, gs, gf, mc, opp, fcst, fe2, gd1, gd2] \
        + list(muts.values()) + list(gmuts.values())
    runtimes_ok = all(Q1._runtime_problems(proto["runtime_contract"], p["runtime"]) == [] for p in all_parts)
    protocol_ok = all(p["protocol_sha256"] == sha(PROTOCOL.read_bytes()) for p in all_parts)
    exact_rows = [r for r in s_rows if Fr(r.get("noise", "0")) == 0 and "max_G_residual_delta_mid" in r
                  and not r["id"].startswith("T25")]
    consistency = all(Fr(r["max_G_residual_delta_mid"]) <= Fr(proto["residual_consistency_threshold"]) for r in exact_rows)
    fixtures_ok = all(not r.get("refused") and not r.get("crashed") and not r["violations"] for r in s_rows)
    finite_ordered = all(Fr(v["L"]) <= Fr(v["U"]) for r in s_rows for v in r.get("per_m", {}).values())
    signs_seen = {v["sign_status"] for r in s_rows for v in r.get("per_m", {}).values()}
    qm_detected = sum(1 for m in muts.values() if m["body"]["detected"])
    no_contam = (all(p.get("loaded_forbidden_modules") in ([], None) for p in all_parts)
                 and not op["body"]["forbidden_calls"] and not rg["body"]["forbidden_calls"]
                 and not opp["body"]["forbidden_calls"] and not fcst["body"]["forbidden_calls"]
                 and not op["body"]["loaded_forbidden_modules"])
    G = {
        "G01_input_identity": bool(k1["body"]["rows"]) and all(r["pass"] for r in k1["body"]["rows"].values())
        and fc["body"]["checks"]["FC03_wrong_manifest"]["pass"] and fc["body"]["checks"]["FC04_wrong_cell"]["pass"],
        "G02_producer_identity": rg["body"]["checks"]["producer_manifest_verifies"]["pass"] and protocol_ok
        and fe2["body"]["checks"]["r1_immutable"]["pass"],
        "G03_exact_derivative_order_3": all(r["pass"] for r in ref["body"]["rows"]) and fixtures_ok and consistency,
        "G04_finite_interval": fixtures_ok and fc["body"]["checks"]["FC07_interval_explosion_nonfinite"]["pass"]
        and fc["body"]["checks"]["FC07b_nan_candidate"]["pass"],
        "G05_lo_le_hi": finite_ordered,
        "G06_signed_interval_semantics": fixtures_ok and {"CERTIFIED_POSITIVE", "CERTIFIED_NEGATIVE",
                                                          "SIGN_INDETERMINATE"} <= signs_seen
        and muts["M15_EXPORT_USES_MID_RADIUS"]["body"]["detected"],
        "G07_whole_cell_soundness": fixtures_ok and all(muts[i]["body"]["detected"] for i in proto["whole_cell_mutations"]),
        "G08_no_unsigned_magnitude_substitution": fe["body"]["checks"]["no_unsigned_or_finite_difference_substitution"]["pass"]
        and "CERTIFIED_NEGATIVE" in signs_seen,
        "G09_no_finite_difference_substitution": fe["body"]["checks"]["no_unsigned_or_finite_difference_substitution"]["pass"],
        "G10_precision_escalation_consistency": overall_prec != "UNSTABLE" and all(
            v["cell_label"] != "UNSTABLE" and v["mid_label"] != "UNSTABLE" for v in gprec.values()),
        "G11_deterministic_scientific_serialization": d1["body"]["hashes"] == d2["body"]["hashes"]
        and all(r.get("scientific_hash") == d1["body"]["hashes"][r["id"]] for r in s_rows)
        and gd1["body"]["hashes"] == gd2["body"]["hashes"],
        "G12_deterministic_scientific_hash": d1["body"]["hashes"] == d2["body"]["hashes"]
        and None not in d1["body"]["hashes"].values() and None not in gd1["body"]["hashes"].values(),
        "G13_runtime_dependency_identity": runtimes_ok,
        "G14_fail_closed": all(v["pass"] for v in fc["body"]["checks"].values())
        and all(v["pass"] for v in rg["body"]["checks"].values())
        and all(v["pass"] for v in gf["body"]["checks"].values()),
        "G15_k1_record_provenance": all(r["pass"] for r in k1["body"]["rows"].values())
        and all(all(t["status"] == "PASS" for t in r["target_gate"].values()) for r in k1["body"]["rows"].values()),
        "G16_no_scientific_probe_contamination": no_contam and all(v["pass"] for v in fe["body"]["checks"].values())
        and all(v["pass"] for v in fe2["body"]["checks"].values()),
    }
    G = {k: "PASS" if bool(v) else "FAIL" for k, v in G.items()}
    gm_required = [m["id"] for m in proto["graded_mutations"] if m["required"]]
    gs_rows = gs["body"]["rows"]
    Q = {
        "QS_manufactured_soundness": "PASS" if fixtures_ok else "FAIL",
        "QC_residual_consistency_exact_candidates": "PASS" if consistency else "FAIL",
        "QM_mutation_sensitivity": "PASS" if qm_detected == len(muts) else "FAIL",
        "QM_count": f"{qm_detected}/{len(muts)}",
        "R05_ISOLATING_FIXTURE": "PASS" if r05["body"]["pass"] and muts["R05_RESIDUAL_R0_USES_CANDIDATE_SOURCE"]["body"]["detected"] else "FAIL",
        "QR_reference_kernel_differential": "PASS" if all(r["pass"] for r in ref["body"]["rows"]) else "FAIL",
        "QX_independent_crosscheck": "PASS" if all(r["pass"] for r in xc["body"]["rows"]) else "FAIL",
        "QO_real_operator_integration_synthetic": "PASS" if all(r["pointwise_all_ok"] and r["dominates"]
                                                                for r in op["body"]["rows"]) else "FAIL",
        "QP_precision_behavior": overall_prec,
        "QG1_graded_soundness": "PASS" if all(r["graded_violation_count"] == 0 and r["scalar_violation_count"] == 0
                                              and not r["crashed"] for r in gs_rows) else "FAIL",
        "QG2_graded_never_looser_than_scalar": "PASS" if all(r["graded_never_looser"] for r in gs_rows) else "FAIL",
        "QG3_graded_mutation_sensitivity": "PASS" if all(gmuts[i]["body"]["detected"] for i in gm_required) else "FAIL",
        "QG3_count": f"{sum(1 for i in gm_required if gmuts[i]['body']['detected'])}/{len(gm_required)} required, "
                     f"{sum(1 for m in gmuts.values() if m['body']['detected'])}/{len(gmuts)} total",
        "QG4_real_kernel_parity_structure": "PASS" if all(r["P1_operator_parity_all_ok"] and r["P2_graded_range_all_ok"]
                                                          for r in opp["body"]["rows"]) else "FAIL",
        "QG5_graded_determinism": "PASS" if gd1["body"]["hashes"] == gd2["body"]["hashes"] else "FAIL",
        "QG6_graded_fail_closed": "PASS" if all(v["pass"] for v in gf["body"]["checks"].values()) else "FAIL",
    }
    fc0 = fcst["body"]["forecast"]
    binding = next(r for r in fc0["cells"]["0"] if r["g_residual_factor"] == 1 and r["C_e0"] == "C_upper"
                   and r["C_o0"].startswith("float"))
    cats = proto["feasibility_criterion"]["categories"]
    cat = lambda x: next(c["label"] for c in cats if x >= c["min"])
    forecast = {"binding_row": {"C_e0": "C_upper (certified)", "C_o0": "float estimate (NOT certified)", "g_residual_factor": 1},
                "R1_mid_m1": binding["R1_scalar_mid"]["1"], "R2_mid_m1": binding["R2_mid"]["1"],
                "R1_cell_m1": binding["R1_scalar_cell"]["1"], "R2_cell_m1": binding["R2_cell"]["1"],
                "R2_point0_conservative_proxy_m1": binding["R2_point0_conservative_proxy"]["1"],
                "contraction_mid": binding["R1_scalar_mid"]["1"] / binding["R2_mid"]["1"],
                "contraction_cell": binding["R1_scalar_cell"]["1"] / binding["R2_cell"]["1"]}
    forecast["category_mid"] = cat(forecast["contraction_mid"])
    forecast["category_cell"] = cat(forecast["contraction_cell"])
    forecast["sweep"] = [{"g": r["g_residual_factor"], "C_e0": r["C_e0"], "C_o0": r["C_o0"],
                          "R2_mid_m1": r["R2_mid"]["1"], "R2_cell_m1": r["R2_cell"]["1"],
                          "category_mid": cat(r["R1_scalar_mid"]["1"] / r["R2_mid"]["1"])} for r in fc0["cells"]["0"]]
    forecast["reconstruction_of_committed_eps_mid"] = all(r["scalar_reconstruction_of_committed_eps_mid"]["equal"]
                                                          for c in fc0["cells"].values() for r in c)
    forecast["budget_cell0"] = fc0["budget_cell0"]
    return {"schema": "rebaseguard.p5y.k5.order3-r2.qualification-result.v1", "protocol_sha256": sha(PROTOCOL.read_bytes()),
            "part_sha256": parts, "gates": G, "questions": Q, "verdicts": {**G, **Q},
            "mutations": {i: {"detected": m["body"]["detected"], "by": [t["trial"] for t in m["body"]["trials"]][-1]}
                          for i, m in muts.items()},
            "graded_mutations": {i: {"required": next(x["required"] for x in proto["graded_mutations"] if x["id"] == i),
                                     "detected": m["body"]["detected"],
                                     "by": [t["trial"] for t in m["body"]["trials"]][-1]} for i, m in gmuts.items()},
            "r05": r05["body"], "precision_r1_producer": {k: {"label": v["label"], "midpoint": v["midpoint_interval"]["label"]}
                                                          for k, v in prec.items()},
            "precision_graded": gprec, "method_comparison": mc["body"]["rows"],
            "graded_soundness_summary": [{k: r[k] for k in ("id", "graded_violation_count", "scalar_violation_count",
                                                            "graded_never_looser", "C", "C_e0", "C_o0", "resolvent_mode",
                                                            "contraction_mid_m1", "contraction_cell_m1")} for r in gs_rows],
            "operator_parity": opp["body"]["rows"], "cell0_forecast": forecast,
            "real_cell_qualification": "NOT_AUTHORIZED", "real_k5_scientific_cell_evaluated": "NO"}


def cmd_check(args):
    proto = load_protocol()
    outdir = Path(args.outdir)
    stored = json.loads((outdir / "QUALIFICATION_RESULT_R2.json").read_text())
    problems = [] if PROTOCOL == FROZEN_PROTOCOL else ["not the frozen protocol"]
    problems += [f"bound code moved: {rel}" for rel, h in proto["bound_code_sha256"].items()
                if sha((REPO / rel).read_bytes()) != h]
    problems += [f"R1 moved: {rel}" for rel, h in proto["r1_bound_sha256"].items() if sha((REPO / rel).read_bytes()) != h]
    again = assemble(proto, outdir)
    for key in ("gates", "questions", "part_sha256", "protocol_sha256"):
        if again[key] != stored[key]:
            problems.append(f"recomputed {key} differs")
    print(json.dumps({"problems": problems, "verdicts": again["verdicts"]}, indent=1))
    sys.exit(1 if problems else 0)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("part")
    p.add_argument("part", choices=sorted(PARTS))
    p.add_argument("--out", required=True)
    p.add_argument("--mutation")
    p.add_argument("--fixture")
    p.add_argument("--bits", type=int, default=256)
    r = sub.add_parser("run")
    r.add_argument("--outdir", required=True)
    r.add_argument("--workers", default="4")
    c = sub.add_parser("check")
    c.add_argument("--outdir", required=True)
    args = ap.parse_args()
    {"part": run_part, "run": cmd_run, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    main()
