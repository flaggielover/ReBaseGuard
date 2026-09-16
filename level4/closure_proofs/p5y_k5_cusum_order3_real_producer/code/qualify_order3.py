"""Runner for the FROZEN order-3 producer qualification protocol (config/QUALIFICATION_PROTOCOL.json).

    python -B code/qualify_order3.py run   --outdir evidence/qualification_r1
    python -B code/qualify_order3.py check --outdir evidence/qualification_r1

`run` executes every part in a FRESH interpreter process (so loaded-module fences and peak RSS are per part), then
assembles QUALIFICATION_RESULT.json with the G01-G16 gate verdicts. `check` re-verifies the part hashes, the bound
code hashes and the protocol hash, and recomputes every verdict from the part files. No part reads a CUSUM cell
table, runs a CUSUM collocation or computes any R_(D,m) derivative; parts K1 and FENCE read the committed K1 record
copies for validation only, and part OPERATOR applies CUSUM Arb kernels to synthetic polynomials only.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import platform
import resource
import socket
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = REPO / "level4/closure_proofs"
sys.path.insert(0, str(NS / "code"))
FROZEN_PROTOCOL = NS / "config/QUALIFICATION_PROTOCOL.json"
PROTOCOL = Path(os.environ.get("O3_DEV_PROTOCOL_PATH", str(FROZEN_PROTOCOL)))   # dev calibration only


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def q(x: Fr) -> str:
    return f"{x.numerator}/{x.denominator}"


def runtime() -> dict:
    import flint
    import numpy
    return {"python": platform.python_version(), "python_flint": flint.__version__, "numpy": numpy.__version__,
            "host": socket.gethostname(), "prefix": sys.prefix, "machine": platform.machine()}


def load_protocol() -> dict:
    return json.loads(PROTOCOL.read_text())


def fixture_by_id(proto: dict, fid: str) -> dict:
    return next(f for f in proto["fixtures"] if f["id"] == fid)


# ------------------------------------------------------------------ one fixture, full evidence
def evaluate_fixture(spec: dict, *, bits: int, engine=None, residual=None, check_truth: bool = True) -> dict:
    import fixtures
    import rung3_engine as E
    import soundness as SD
    from run_fixture import certify_fixture
    engine = E if engine is None else engine
    residual = __import__("rung3_residual") if residual is None else residual
    sysm, e0, rho, seed, noise = fixtures.build(spec)
    inflate = Fr(spec.get("inflate", "1"))
    t0 = time.process_time()
    try:
        perturb = (int(spec["perturb_F"][0]), Fr(spec["perturb_F"][1])) if "perturb_F" in spec else None
        rig, g, res, _cpu = certify_fixture(sysm, e0, rho, seed=seed, noise=noise, bits=bits, inflate=inflate,
                                            engine=engine, residual=residual, perturb=perturb)
    except E.ProducerRefusal as exc:
        return {"id": spec["id"], "refused": str(exc), "violations": [], "bits": bits}
    except Exception as exc:  # a mutant may crash; that is recorded, never counted as detection
        return {"id": spec["id"], "crashed": f"{type(exc).__name__}: {exc}", "violations": [], "bits": bits}
    cpu = time.process_time() - t0
    viol = SD.violations(sysm, rig, res) if check_truth else []
    per_m = {}
    for m in E.M_VALUES:
        v = res["m"][m]
        L, U = v["R3_cell"]
        mlo, mhi = v["R3_mid"]
        tlo, thi = SD.truth_range(sysm, e0, rho, m) if check_truth else (None, None)
        per_m[str(m)] = {"L": q(L), "U": q(U), "width": q(U - L), "sign_status": E.sign_status(L, U),
                         "mid_width": q(mhi - mlo),
                         "centre_float": float(sum(E.ball_fractions(v["centre"])) / 2),
                         "truth_grid_min": None if tlo is None else q(tlo),
                         "truth_grid_max": None if thi is None else q(thi)}
    g_delta = max(E.upper_fraction(g[r]["delta_mid"]) for r in range(5))
    payload = E.scientific_payload(res, {"fixture": spec, "kind": "MANUFACTURED_NON_SCIENTIFIC"})
    return {"id": spec["id"], "bits": bits, "violations": viol, "per_m": per_m, "cpu_seconds": cpu,
            "C": q(rig.C), "rho": q(rig.rho), "C_times_rho": float(rig.C * rig.rho), "k0": q(rig.k[0]),
            "max_G_residual_delta_mid": q(g_delta), "noise": spec.get("noise", "0"),
            "kept_bounds": {n: c["bound"] for n, c in payload["components"].items() if n.startswith("F:")},
            "scientific_hash": E.scientific_hash(payload)}


# ------------------------------------------------------------------ parts
def part_soundness(proto, args) -> dict:
    rows = [evaluate_fixture(f, bits=256) for f in proto["fixtures"]]
    return {"rows": rows}


def part_determinism(proto, args) -> dict:
    rows = [evaluate_fixture(f, bits=256, check_truth=False) for f in proto["fixtures"]]
    return {"hashes": {r["id"]: r.get("scientific_hash") for r in rows}}


def _load_mutant(target: str, old: str, new: str, tag: str):
    src = (NS / "code" / target).read_text()
    if src.count(old) != 1:
        raise RuntimeError(f"mutation anchor for {tag} matches {src.count(old)} times")
    tmp = Path(tempfile.mkdtemp(prefix="o3mut-"))
    path = tmp / f"mutant_{tag}.py"
    path.write_text(src.replace(old, new))
    spec = importlib.util.spec_from_file_location(f"mutant_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def part_mutation(proto, args) -> dict:
    import rung3_engine as E
    import rung3_residual as RR
    mut = next(m for m in proto["mutations"] if m["id"] == args.mutation)
    mod = _load_mutant(mut["target"], mut["old"], mut["new"], mut["id"])
    eng = mod if mut["target"] == "rung3_engine.py" else E
    resid = mod if mut["target"] == "rung3_residual.py" else RR
    hits = []
    for fid in proto["mutation_trials"]:
        row = evaluate_fixture(fixture_by_id(proto, fid), bits=256, engine=eng, residual=resid)
        consistency = None
        if Fr(fixture_by_id(proto, fid).get("noise", "0")) == 0 and "max_G_residual_delta_mid" in row:
            consistency = Fr(row["max_G_residual_delta_mid"]) <= Fr(proto["residual_consistency_threshold"])
        detected = bool(row["violations"]) or consistency is False
        hits.append({"trial": fid, "violations": len(row["violations"]), "first": row["violations"][:1],
                     "residual_consistency": consistency, "refused": row.get("refused"),
                     "crashed": row.get("crashed"), "detected": detected})
        if detected:
            break
    return {"mutation": mut["id"], "detected": any(h["detected"] for h in hits), "trials": hits}


def part_precision(proto, args) -> dict:
    row = evaluate_fixture(fixture_by_id(proto, args.fixture), bits=args.bits)
    row["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return row


def part_crosscheck(proto, args) -> dict:
    import fixtures
    import independent_crosscheck as IC
    rows = []
    for fid in proto["crosscheck_fixtures"]:
        spec = fixture_by_id(proto, fid)
        eng = evaluate_fixture(spec, bits=256)
        sysm, e0, rho, _s, _n = fixtures.build(spec)
        per_m = {}
        for m in (1, 2, 3, 5):
            a, b = IC.enclosure(sysm, e0, rho, m, pieces=int(proto["crosscheck_pieces"]))
            L, U = Fr(eng["per_m"][str(m)]["L"]), Fr(eng["per_m"][str(m)]["U"])
            tlo, thi = Fr(eng["per_m"][str(m)]["truth_grid_min"]), Fr(eng["per_m"][str(m)]["truth_grid_max"])
            contradiction = (a > 0 and U < 0) or (b < 0 and L > 0)
            ok = max(a, L) <= min(b, U) and a <= tlo and thi <= b and L <= tlo and thi <= U and not contradiction
            ind_sign = "CERTIFIED_POSITIVE" if a > 0 else "CERTIFIED_NEGATIVE" if b < 0 else "SIGN_INDETERMINATE"
            per_m[str(m)] = {"independent": [q(a), q(b)], "engine": [q(L), q(U)], "intersect": max(a, L) <= min(b, U),
                             "sign_contradiction": contradiction, "independent_sign": ind_sign,
                             "engine_sign": eng["per_m"][str(m)]["sign_status"],
                             "width_ratio_engine_over_independent": float((U - L) / (b - a)) if b > a else None,
                             "pass": ok}
        rows.append({"id": fid, "engine_violations": len(eng["violations"]), "per_m": per_m,
                     "pass": all(v["pass"] for v in per_m.values()) and not eng["violations"]})
    return {"rows": rows}


def part_reference(proto, args) -> dict:
    import reference_differential as RD
    design_proto = json.loads((CP / "p5y_k5_cusum_order3_producer_design/config/QUALIFICATION_PROTOCOL.json")
                              .read_text())
    rows = [RD.compare(t) for t in design_proto["QN1_SOUNDNESS"]["trials"]]
    return {"design_protocol_sha256": sha((CP / "p5y_k5_cusum_order3_producer_design/config/"
                                           "QUALIFICATION_PROTOCOL.json").read_bytes()), "rows": rows}


def part_operator(proto, args) -> dict:
    watch = _watch_forbidden(proto)
    import real_operator_integration as ROI
    rows = []
    with watch:
        for item in proto["operator_integration"]:
            r = ROI.run(int(item["seed"]), Fr(item["e0"]), Fr(item["rho"]))
            rows.append(r)
    return {"rows": rows, "forbidden_calls": watch.hits,
            "loaded_forbidden_modules": sorted(m for m in proto["forbidden_loaded_modules_operator"]
                                               if m in sys.modules)}


class _Watch:
    def __init__(self, names):
        self.names, self.hits = set(names), []

    def _prof(self, frame, event, arg):
        if event == "call" and frame.f_code.co_name in self.names and frame.f_code.co_filename.startswith(str(REPO)):
            self.hits.append(f"{frame.f_code.co_filename}:{frame.f_code.co_name}")

    def __enter__(self):
        sys.setprofile(self._prof)
        return self

    def __exit__(self, *a):
        sys.setprofile(None)


def _watch_forbidden(proto):
    return _Watch(proto["forbidden_function_names"])


def part_failclosed(proto, args) -> dict:
    import fixtures
    import k1_inputs as K1
    import manufactured_chain as MC
    import rung3_engine as E
    import rung3_residual as RR
    from flint import arb
    from run_fixture import certify_fixture
    rec_dir = CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records"
    rec0 = (rec_dir / "aux5_CUSUM_0_256.json").read_bytes()
    rec309 = (rec_dir / "aux5_CUSUM_309_256.json").read_bytes()
    base = fixture_by_id(proto, proto["failclosed_base_fixture"])
    out = {}

    def expect_refusal(name, fn, exc_types):
        try:
            fn()
        except exc_types as exc:
            out[name] = {"pass": True, "refused": f"{type(exc).__name__}: {str(exc)[:160]}"}
            return
        except Exception as exc:
            out[name] = {"pass": False, "wrong_exception": f"{type(exc).__name__}: {exc}"}
            return
        out[name] = {"pass": False, "refused": None}

    def certify(spec, bits=256, **kw):
        sysm, e0, rho, seed, noise = fixtures.build(spec)
        return certify_fixture(sysm, e0, rho, seed=seed, noise=noise, bits=bits, **kw)

    def inputs_for(spec):
        sysm, e0, rho, seed, noise = fixtures.build(spec)
        rig = MC.Rigorous(sysm, e0, rho, seed=seed, noise=noise)
        with E.precision(256):
            cert = MC.ManufacturedCert(rig)
            g = {r: RR.g_residual(cert, r) for r in range(5)}
            return MC.engine_inputs(cert, g)

    expect_refusal("FC01_insufficient_precision_64", lambda: certify(base, bits=64), E.ProducerRefusal)
    expect_refusal("FC01b_unlisted_precision_200", lambda: certify(base, bits=200), E.ProducerRefusal)
    expect_refusal("FC02_malformed_record_bytes", lambda: K1.validate(rec0[:-17], cell_index=0), K1.K1InputRefused)
    bad_manifest = bytearray((K1.EXPORT_MANIFEST).read_bytes())
    bad_manifest[-3] ^= 1
    expect_refusal("FC03_wrong_manifest", lambda: K1.validate(rec0, cell_index=0, manifest_bytes=bytes(bad_manifest)),
                   K1.K1InputRefused)
    expect_refusal("FC04_wrong_cell", lambda: K1.validate(rec0, cell_index=309), K1.K1InputRefused)
    expect_refusal("FC05_wrong_m_engine", lambda: E.coefficients(4), E.ProducerRefusal)
    expect_refusal("FC05b_wrong_m_record", lambda: K1.validate(rec309, cell_index=309, m_values=("4",)),
                   K1.K1InputRefused)
    ck = json.loads((REPO / proto["assembly_table"]["path"]).read_text())[proto["assembly_table"]["key"]]
    table_ok = _table_matches(ck, E.coefficients)
    tampered = json.loads(json.dumps(ck))
    _tamper_table(tampered)
    out["FC06_wrong_coefficient_table"] = {"pass": table_ok and not _table_matches(tampered, E.coefficients),
                                           "frozen_table_matches_engine": table_ok}

    def explode():
        inp = inputs_for(base)
        inp["refined"]["H:2"] = arb("inf")
        E.certify_order3(inp)
    expect_refusal("FC07_interval_explosion_nonfinite", explode, E.ProducerRefusal)

    def nan_origin():
        inp = inputs_for(base)
        inp["origin"][("G", 0)] = arb("nan")
        E.certify_order3(inp)
    expect_refusal("FC07b_nan_candidate", nan_origin, E.ProducerRefusal)
    huge = fixture_by_id(proto, proto["failclosed_huge_C_fixture"])
    row = evaluate_fixture(huge, bits=256)
    out["FC07c_huge_C_finite_wide_sound"] = {"pass": not row.get("refused") and not row["violations"],
                                             "widths": {m: float(Fr(v["width"])) for m, v in row["per_m"].items()}}
    zero = evaluate_fixture(fixture_by_id(proto, proto["failclosed_sign_fixture"]), bits=256)
    out["FC08_sign_uncertainty_not_fabricated"] = {
        "pass": zero["per_m"]["1"]["sign_status"] == "SIGN_INDETERMINATE" and not zero["violations"],
        "m1": zero["per_m"]["1"]}

    def singular():
        spec = dict(base)
        sysm, e0, rho, seed, noise = fixtures.build(spec)
        sysm.A = [[[Fr(1) if i == j else Fr(0) for j in range(sysm.n)] for i in range(sysm.n)]] + sysm.A[1:]
        MC.Rigorous(sysm, e0, rho, seed=seed, noise=noise)
    expect_refusal("FC09_singular_resolvent", singular, ValueError)

    def nonpositive_C():
        inp = inputs_for(base)
        inp["C"] = arb(0)
        E.certify_order3(inp)
    expect_refusal("FC09b_nonpositive_C", nonpositive_C, E.ProducerRefusal)
    near = evaluate_fixture(fixture_by_id(proto, proto["failclosed_near_singular_fixture"]), bits=256)
    out["FC09c_near_singular_sound"] = {"pass": not near.get("refused") and not near["violations"], "C": near.get("C")}
    expected = proto["runtime_contract"]
    observed = runtime()
    mism = dict(observed, host="some-other-host")
    out["FC10_runtime_mismatch"] = {"pass": _runtime_problems(expected, observed) == [] and
                                    _runtime_problems(expected, mism) != [],
                                    "observed_matches_contract": _runtime_problems(expected, observed) == []}

    def missing_key():
        inp = inputs_for(base)
        del inp["towers"]
        E.certify_order3(inp)
    expect_refusal("FC12_missing_input", missing_key, E.ProducerRefusal)

    def negative_rho():
        inp = inputs_for(base)
        inp["rho"] = arb(-1)
        E.certify_order3(inp)
    expect_refusal("FC13_negative_rho", negative_rho, E.ProducerRefusal)
    return {"checks": out}


def part_realgate(proto, args) -> dict:
    """Real-cell governance gate and fences. Runs in its own process with a call watcher."""
    watch = _watch_forbidden(proto)
    rec0 = (CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json").read_bytes()
    out = {}
    with watch:
        import cusum_order3 as CO
        for name, auth, rb in (("no_authorization", None, rec0),
                               ("forged_authorization", {"cells": [0], "purpose": "forged"}, rec0),
                               ("gate_precedes_record_validation", None, b"not a record")):
            try:
                CO.certify_real_cell(0, authorization=auth, record_bytes=rb)
                out[name] = {"pass": False}
            except CO.RealCellNotAuthorized as exc:
                out[name] = {"pass": True, "refused": str(exc)}
            except Exception as exc:
                out[name] = {"pass": False, "wrong_exception": f"{type(exc).__name__}: {exc}"}
        registry = json.loads(CO.AUTH_REGISTRY.read_text())
        out["registry_empty"] = {"pass": registry.get("authorizations") == []}
        out["producer_manifest_verifies"] = {"pass": CO.producer_manifest_problems() == [],
                                             "problems": CO.producer_manifest_problems()}
        out["order3_certifier_is_aux3_subclass"] = {
            "pass": issubclass(CO.Order3Certifier, CO.aux_certifier.Aux3Certifier)
            and set(vars(CO.Order3Certifier)) - {"__module__", "__doc__", "__qualname__", "__firstlineno__",
                                                 "__static_attributes__"}
            == {"provides_rung3", "vec", "z_range", "prepare", "_candidates_rung3"}}
    return {"checks": out, "forbidden_calls": watch.hits}


def part_k1(proto, args) -> dict:
    import k1_inputs as K1
    rows = {}
    for i in proto["k1_validation_cells"]:
        b = (CP / f"p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_{i}_256.json").read_bytes()
        v = K1.validate(b, cell_index=i)
        rows[str(i)] = {"checks": v["checks"], "record_sha256": v["record_sha256"],
                        "endpoint_region": v["endpoint_region"],
                        "target_gate": {m: x["target_gate"] for m, x in v["per_m"].items()},
                        "pass": all(v["checks"].values())}
    return {"rows": rows, "pb2_note": K1.PB2_NOTE}


def part_fence(proto, args) -> dict:
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
        out[mod] = {"imports": sorted(names), "forbidden": bad, "pass": not bad}
    tree = ast.parse((code / "cusum_order3.py").read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "certify_real_cell")
    first = fn.body[0]
    first_call = (isinstance(first, ast.Assign) and isinstance(first.value, ast.Call)
                  and getattr(first.value.func, "id", None) == "require_authorization")
    out["authorization_gate_is_first_statement"] = {"pass": first_call}
    prod_src = "".join((code / m).read_text() for m in proto["producer_modules"])
    bad_tokens = [t for t in proto["forbidden_producer_tokens"] if t in prod_src]
    out["no_unsigned_or_finite_difference_substitution"] = {"pass": not bad_tokens, "found": bad_tokens}
    sys.path.append(str(CP / "p5y_k1_cusum_aux3_successor/code"))
    spec = importlib.util.spec_from_file_location("no_monkeypatch", CP / "p5y_k1_cusum_aux3_successor/code/"
                                                  "no_monkeypatch.py")
    nm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nm)
    findings = []
    for f in sorted(code.glob("*.py")):
        findings += nm.scan_source(f.read_text(), f.name)
    control = nm.scan_source("import propagate\npropagate.refine = object()\n", "control")
    out["no_monkeypatch"] = {"pass": not findings and bool(control), "findings": findings,
                             "detector_fires_on_control": bool(control)}
    return {"checks": out}


def _table_matches(frozen, coefficients) -> bool:
    for m_key, rows in frozen.items():
        m = int(m_key)
        want = sorted((str(r[0]), int(r[1]), int(r[2]), Fr(str(r[3]))) for r in rows)
        got = sorted((k, r, j, c) for k, r, j, c in coefficients(m))
        if want != got:
            return False
    return True


def _tamper_table(table) -> None:
    key = sorted(table)[-1]
    row = table[key][-1]
    row[3] = str(Fr(str(row[3])) + Fr(1, 7))


def _runtime_problems(expected: dict, observed: dict) -> list[str]:
    return [k for k, v in expected.items() if observed.get(k) != v]


PARTS = {"soundness": part_soundness, "determinism": part_determinism, "mutation": part_mutation,
         "precision": part_precision, "crosscheck": part_crosscheck, "reference": part_reference,
         "operator": part_operator, "failclosed": part_failclosed, "realgate": part_realgate, "k1": part_k1,
         "fence": part_fence}


def run_part(args) -> None:
    proto = load_protocol()
    t0, w0 = time.process_time(), time.time()
    body = PARTS[args.part](proto, args)
    loaded = sorted(m for m in proto["forbidden_loaded_modules"] if m in sys.modules)
    rec = {"part": args.part, "argv": sys.argv[2:], "runtime": runtime(), "body": body,
           "protocol_sha256": sha(PROTOCOL.read_bytes()),
           "loaded_forbidden_modules": loaded if args.part not in ("operator", "realgate") else None,
           "metadata": {"cpu_seconds": time.process_time() - t0, "wall_seconds": time.time() - w0,
                        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")


# ------------------------------------------------------------------ orchestration and verdicts
def jobs(proto: dict, outdir: Path) -> list[list[str]]:
    J = []
    for name in ("soundness", "reference", "crosscheck", "failclosed", "realgate", "k1", "fence", "operator"):
        J.append(["part", name, "--out", str(outdir / f"part_{name}.json")])
    for rep in (1, 2):
        J.append(["part", "determinism", "--out", str(outdir / f"part_determinism_{rep}.json")])
    for m in proto["mutations"]:
        J.append(["part", "mutation", "--mutation", m["id"], "--out", str(outdir / f"part_mutation_{m['id']}.json")])
    for fid in proto["precision"]["fixtures"]:
        for b in proto["precision"]["bits"]:
            J.append(["part", "precision", "--fixture", fid, "--bits", str(b),
                      "--out", str(outdir / f"part_precision_{fid}_{b}.json")])
    return J


def cmd_run(args) -> None:
    proto = load_protocol()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               NUMEXPR_NUM_THREADS="1", PYTHONHASHSEED="0")
    pending = [[sys.executable, "-B", str(Path(__file__).resolve())] + j for j in jobs(proto, outdir)]
    running = []
    failures = []
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
                    failures.append({"cmd": cmd[3:], "rc": p.returncode, "log": log[-2000:]})
    result = assemble(proto, outdir)
    result["runner_failures"] = failures
    (outdir / "QUALIFICATION_RESULT.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps(result["verdicts"], indent=1))


def _read(outdir: Path, name: str) -> dict:
    return json.loads((outdir / name).read_text())


def precision_classification(rows_by_bits: dict, width_key: str = "width") -> dict:
    bits = sorted(rows_by_bits)
    widths = []
    unstable = []
    for b in bits:
        row = rows_by_bits[b]
        if row.get("refused") or row.get("crashed") or row["violations"]:
            unstable.append(f"{b}: refused/crashed/violation")
            widths.append(None)
            continue
        widths.append(max(Fr(v[width_key]) for v in row["per_m"].values()))
    for m in ("1", "2", "3", "5"):
        signs = {rows_by_bits[b]["per_m"][m]["sign_status"] for b in bits if "per_m" in rows_by_bits[b]}
        if {"CERTIFIED_POSITIVE", "CERTIFIED_NEGATIVE"} <= signs:
            unstable.append(f"m={m}: sign flip across precision")
        ivs = [(Fr(rows_by_bits[b]["per_m"][m]["L"]), Fr(rows_by_bits[b]["per_m"][m]["U"]))
               for b in bits if "per_m" in rows_by_bits[b]]
        for i in range(len(ivs)):
            for j in range(i + 1, len(ivs)):
                if max(ivs[i][0], ivs[j][0]) > min(ivs[i][1], ivs[j][1]):
                    unstable.append(f"m={m}: disjoint intervals across precision")
    if unstable:
        label = "UNSTABLE"
    elif None in widths:
        label = "INCONCLUSIVE"
    else:
        nonincreasing = all(widths[i + 1] <= widths[i] * (1 + Fr(1, 2 ** 64)) for i in range(len(widths) - 1))
        if not nonincreasing:
            label = "INCONCLUSIVE"
        elif widths[-1] < widths[0] / 2:
            label = "CONTRACTING"
        else:
            label = "STAGNATING"
    return {"label": label, "max_width_by_bits": {str(b): (None if w is None else float(w))
                                                  for b, w in zip(bits, widths)}, "unstable": unstable}


def assemble(proto: dict, outdir: Path) -> dict:
    parts = {p.name: sha(p.read_bytes()) for p in sorted(outdir.glob("part_*.json"))}
    snd = _read(outdir, "part_soundness.json")
    ref = _read(outdir, "part_reference.json")
    xc = _read(outdir, "part_crosscheck.json")
    fc = _read(outdir, "part_failclosed.json")
    rg = _read(outdir, "part_realgate.json")
    k1 = _read(outdir, "part_k1.json")
    fe = _read(outdir, "part_fence.json")
    op = _read(outdir, "part_operator.json")
    d1, d2 = _read(outdir, "part_determinism_1.json"), _read(outdir, "part_determinism_2.json")
    muts = {m["id"]: _read(outdir, f"part_mutation_{m['id']}.json") for m in proto["mutations"]}
    prec = {}
    for fid in proto["precision"]["fixtures"]:
        rows = {b: _read(outdir, f"part_precision_{fid}_{b}.json")["body"] for b in proto["precision"]["bits"]}
        cls = precision_classification(rows)
        cls["midpoint_interval"] = precision_classification(rows, "mid_width")
        cls["per_bits"] = {str(b): {"cpu_seconds": rows[b].get("cpu_seconds"), "peak_rss_kib": rows[b].get("peak_rss_kib"),
                                    "signs": {m: v["sign_status"] for m, v in rows[b].get("per_m", {}).items()},
                                    "centre_m1": rows[b].get("per_m", {}).get("1", {}).get("centre_float")}
                           for b in proto["precision"]["bits"]}
        prec[fid] = cls
    order = ["UNSTABLE", "INCONCLUSIVE", "STAGNATING", "CONTRACTING"]
    overall_prec = next((lab for lab in order if any(c["label"] == lab for c in prec.values())), "INCONCLUSIVE")

    s_rows = snd["body"]["rows"]
    all_parts = [snd, ref, xc, fc, rg, k1, fe, op, d1, d2] + list(muts.values())
    runtimes_ok = all(_runtime_problems(proto["runtime_contract"], p["runtime"]) == [] for p in all_parts)
    protocol_ok = all(p["protocol_sha256"] == sha(PROTOCOL.read_bytes()) for p in all_parts)
    exact_rows = [r for r in s_rows if Fr(r.get("noise", "0")) == 0 and "max_G_residual_delta_mid" in r]
    consistency = all(Fr(r["max_G_residual_delta_mid"]) <= Fr(proto["residual_consistency_threshold"])
                      for r in exact_rows)
    fixtures_ok = all(not r.get("refused") and not r.get("crashed") and not r["violations"] for r in s_rows)
    finite_ordered = all(Fr(v["L"]) <= Fr(v["U"]) for r in s_rows for v in r.get("per_m", {}).values())
    signs_seen = {v["sign_status"] for r in s_rows for v in r.get("per_m", {}).values()}
    required = [m["id"] for m in proto["mutations"] if m["required"]]
    mut_ok = all(muts[i]["body"]["detected"] for i in required)
    no_contam = (all(p.get("loaded_forbidden_modules") in ([], None) for p in all_parts)
                 and not op["body"]["forbidden_calls"] and not rg["body"]["forbidden_calls"]
                 and not op["body"]["loaded_forbidden_modules"])
    G = {
        "G01_input_identity": k1["body"]["rows"] and all(r["pass"] for r in k1["body"]["rows"].values())
        and fc["body"]["checks"]["FC03_wrong_manifest"]["pass"] and fc["body"]["checks"]["FC04_wrong_cell"]["pass"],
        "G02_producer_identity": rg["body"]["checks"]["producer_manifest_verifies"]["pass"] and protocol_ok,
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
        "G10_precision_escalation_consistency": overall_prec != "UNSTABLE",
        "G11_deterministic_scientific_serialization": d1["body"]["hashes"] == d2["body"]["hashes"]
        and all(r.get("scientific_hash") == d1["body"]["hashes"][r["id"]] for r in s_rows),
        "G12_deterministic_scientific_hash": d1["body"]["hashes"] == d2["body"]["hashes"]
        and None not in d1["body"]["hashes"].values(),
        "G13_runtime_dependency_identity": runtimes_ok,
        "G14_fail_closed": all(v["pass"] for v in fc["body"]["checks"].values())
        and all(v["pass"] for v in rg["body"]["checks"].values()),
        "G15_k1_record_provenance": all(r["pass"] for r in k1["body"]["rows"].values())
        and all(all(t["status"] == "PASS" for t in r["target_gate"].values()) for r in k1["body"]["rows"].values()),
        "G16_no_scientific_probe_contamination": no_contam and all(v["pass"] for v in fe["body"]["checks"].values()),
    }
    G = {k: "PASS" if bool(v) else "FAIL" for k, v in G.items()}
    Q = {
        "QS_manufactured_soundness": "PASS" if fixtures_ok else "FAIL",
        "QC_residual_consistency_exact_candidates": "PASS" if consistency else "FAIL",
        "QM_mutation_sensitivity": "PASS" if mut_ok else "FAIL",
        "QR_reference_kernel_differential": "PASS" if all(r["pass"] for r in ref["body"]["rows"]) else "FAIL",
        "QX_independent_crosscheck": "PASS" if all(r["pass"] for r in xc["body"]["rows"]) else "FAIL",
        "QO_real_operator_integration_synthetic": "PASS" if all(r["pointwise_all_ok"] and r["dominates"]
                                                                for r in op["body"]["rows"]) else "FAIL",
        "QP_precision_behavior": overall_prec,
    }
    return {"schema": "rebaseguard.p5y.k5.order3-real-producer.qualification-result.v1",
            "protocol_sha256": sha(PROTOCOL.read_bytes()), "part_sha256": parts,
            "gates": G, "questions": Q,
            "verdicts": {**G, **Q},
            "mutations": {i: {"required": next(m["required"] for m in proto["mutations"] if m["id"] == i),
                              "detected": muts[i]["body"]["detected"],
                              "trials": muts[i]["body"]["trials"]} for i in muts},
            "precision": prec, "soundness_summary": [
                {"id": r["id"], "violations": len(r["violations"]), "C": r.get("C"), "C_times_rho": r.get("C_times_rho"),
                 "signs": {m: v["sign_status"] for m, v in r.get("per_m", {}).items()},
                 "width_m1": r.get("per_m", {}).get("1", {}).get("width"), "cpu_seconds": r.get("cpu_seconds"),
                 "kept_F_bounds": r.get("kept_bounds")} for r in s_rows],
            "real_cell_qualification": "NOT_AUTHORIZED", "real_k5_scientific_cell_evaluated": "NO"}


def cmd_check(args) -> None:
    proto = load_protocol()
    outdir = Path(args.outdir)
    stored = json.loads((outdir / "QUALIFICATION_RESULT.json").read_text())
    problems = [] if PROTOCOL == FROZEN_PROTOCOL else ["not the frozen protocol"]
    for rel, h in proto["bound_code_sha256"].items():
        if sha((REPO / rel).read_bytes()) != h:
            problems.append(f"bound code moved: {rel}")
    again = assemble(proto, outdir)
    for key in ("gates", "questions", "part_sha256", "protocol_sha256"):
        if again[key] != stored[key]:
            problems.append(f"recomputed {key} differs")
    print(json.dumps({"problems": problems, "verdicts": again["verdicts"]}, indent=1))
    sys.exit(1 if problems else 0)


def main() -> None:
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
