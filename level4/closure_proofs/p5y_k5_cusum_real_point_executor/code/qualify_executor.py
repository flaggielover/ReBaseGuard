"""Frozen qualification of the real point executor (config/EXECUTOR_QUALIFICATION_PROTOCOL.json). NON-SCIENTIFIC.

    python -B code/qualify_executor.py run   --outdir evidence/qualification --workers 4
    python -B code/qualify_executor.py check --outdir evidence/qualification

Only manufactured systems, synthetic candidates and operator certificates. REAL_INPUT_ARITHMETIC_GUARD = DENY throughout:
no real K1 cell is executed, no real R''' / R^(5) / L1 / U1 is formed. Completion: RUN_STATE.json (pid) -> result ->
RUN_COMPLETE.json (result sha256); RUN_FAILED.json on an exception.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import resource
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from fractions import Fraction as F
from pathlib import Path

import paths

NS = paths.NS
PROTOCOL = NS / "config/EXECUTOR_QUALIFICATION_PROTOCOL.json"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode()


def load_protocol() -> dict:
    return json.loads(PROTOCOL.read_text())


def runtime() -> dict:
    import platform
    import flint
    import numpy
    import prelaunch_verify as PV
    facts = PV.live_host_facts()
    facts.update({"flint_library": getattr(flint, "__FLINT_VERSION__", None), "python_flint_module": flint.__version__,
                  "numpy_module": numpy.__version__, "python_impl": platform.python_implementation(),
                  "env": {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                                                         "PYTHONHASHSEED")}})
    return facts


# ------------------------------------------------------------------ fixture execution (shared by parts and mutants)
def context_for(binding, out):
    import executor_core as EC
    p = EC.prereg()
    return EC.ExecutionContext(k1_binding=binding, output_dir=out, producer_identity_sha256=p["producer_identity_sha256"],
                               protocol_sha256=sha(EC.SCIENCE_FILE.read_bytes()),
                               runtime_identity_sha256=p["host_runtime_identity_sha256"])


def run_fixture(spec, root: Path):
    import backends as B
    import executor_core as EC
    import input_adapters as IA
    binding = IA.ManufacturedInputAdapter().bind(spec)
    return EC.execute(B.ManufacturedPointBackend(spec), context_for(binding, root / spec["id"]))


def evaluate_fixtures(proto, root: Path) -> dict:
    import consumer as CO
    import exec_fixtures as FX
    rows = {}
    for spec in proto["fixtures"]:
        row = {"id": spec["id"], "purpose": spec["purpose"]}
        try:
            rec = run_fixture(spec, root)
            it = CO.interpret(rec)
            tr = FX.truth(spec)
            viol = FX.containment(rec, tr)
            verdicts = {m: (v["verdict"], v["point"]) for m, v in it["SCIENTIFIC_PROBE"].items()} \
                if isinstance(it["SCIENTIFIC_PROBE"], dict) else it["SCIENTIFIC_PROBE"]
            ratio = {}
            for m in (1, 2, 3, 5):
                truth5 = tr[m]["max_abs_R5"]
                ratio[m] = float(F(rec["scientific"]["per_m"][str(m)]["M5"]) / truth5) if truth5 else None
            row.update({"refused": None, "qualification": it["REAL_PRODUCER_QUALIFICATION"],
                        "failed_gates": [k for k, v in it["gates"].items() if not v], "verdicts": verdicts,
                        "truth_violations": viol, "scientific_hash": rec["scientific_hash"],
                        "M5_over_truth": {str(m): r for m, r in ratio.items()}, "cpu_seconds": rec["metadata"]["cpu_seconds"]})
            exp = spec["expect"]
            ok = (it["REAL_PRODUCER_QUALIFICATION"] == "PASS" and not viol
                  and {m: list(v) for m, v in verdicts.items()} == exp["verdicts"])
            if "M5_ratio_max" in exp:
                ok = ok and all(r is not None and r <= exp["M5_ratio_max"] for r in ratio.values())
            if "M5_ratio_min_m1" in exp:
                ok = ok and ratio[1] is not None and ratio[1] >= exp["M5_ratio_min_m1"]
            row["pass"] = bool(ok)
        except Exception as exc:
            row.update({"refused": f"{type(exc).__name__}: {str(exc)[:200]}", "pass": False})
        rows[spec["id"]] = row
    return rows


def refusal_tests(proto, root: Path, *, include_real_tripwire: bool) -> dict:
    """F10-F12 and the fail-closed list. Each test expects one refusal class."""
    import backends as B
    import executor_core as EC
    import input_adapters as IA
    base = proto["fixtures"][0]
    out = {}

    def expect(name, fn, needle):
        try:
            fn()
            out[name] = {"pass": False, "outcome": "NOT_REFUSED"}
        except (EC.ExecutorRefusal, IA.InputRefused) as exc:
            out[name] = {"pass": needle in str(exc), "outcome": str(exc)[:200]}
        except Exception as exc:
            out[name] = {"pass": False, "outcome": f"{type(exc).__name__}: {str(exc)[:200]}"}

    def ctx(binding=None, **kw):
        c = context_for(binding or IA.ManufacturedInputAdapter().bind(base), root / f"t{len(out)}_{id(kw)}" / "o")
        for k, v in kw.items():
            setattr(c, k, v)
        return c

    class DropOrigin(B.ManufacturedPointBackend):
        def point_graded_inputs(self, state, constants):
            inp = dict(super().point_graded_inputs(state, constants))
            inp.pop("origin")
            return inp

    expect("F10_malformed_certificate_chain", lambda: EC.execute(DropOrigin(base), ctx()), "INCOMPLETE_CERTIFICATE_CHAIN")
    ident = EC.prereg()["k1_input_identity"]
    wrong = dict(IA.ManufacturedInputAdapter().bind(base), kind="real", record_sha256="0" * 64,
                 export_manifest_sha256=ident["manifest_sha256"], cells_json_sha256=ident["cells_json_sha256"])
    expect("F11_wrong_k1_identity", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(wrong)), "K1_IDENTITY_MISMATCH")
    expect("F11b_real_adapter_tampered_record",
           lambda: IA.RealInputAdapter().bind((paths.REPO / EC.prereg()["k1_input_identity"]["record"]).read_bytes() + b" "),
           "K1 validation refused")
    expect("F12_wrong_m_identity", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(m_set=[1, 2, 3, 4])), "M_SET_MISMATCH")
    expect("unbound_input", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(binding={"kind": "manufactured"})),
           "UNBOUND_OR_MALFORMED_INPUT")
    expect("producer_hash_mismatch", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(producer_identity_sha256="0" * 64)),
           "PRODUCER_IDENTITY_MISMATCH")
    expect("protocol_hash_mismatch", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(protocol_sha256="0" * 64)),
           "PROTOCOL_IDENTITY_MISMATCH")
    expect("unsupported_precision", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(precision_bits=384)),
           "UNSUPPORTED_PRECISION")
    expect("wrong_point", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(point_e="1/40")), "POINT_MISMATCH")
    bad_x1 = dict(IA.ManufacturedInputAdapter().bind(base), right="1/3")
    expect("wrong_cell_endpoint", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(bad_x1)), "CELL_ENDPOINT_MISMATCH")
    stale = root / "stale"
    stale.mkdir(parents=True, exist_ok=True)
    (stale / "leftover").write_text("x")
    expect("stale_output_namespace", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(output_dir=stale)),
           "STALE_OUTPUT_NAMESPACE")
    first = root / "addr" / "first"
    EC.execute(B.ManufacturedPointBackend(base), ctx(output_dir=first))
    expect("finalized_address_exists", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(output_dir=root / "addr" / "second")),
           "FINALIZED_ADDRESS_EXISTS")
    contract = EC.prereg()["host_runtime_contract"]
    out["runtime_mismatch_detector"] = {"pass": EC.runtime_differences(contract, dict(contract, host="elsewhere", libc_sha256="0"))
                                        == ["host", "libc_sha256"] and EC.runtime_differences(contract, dict(contract)) == []}
    import prelaunch_verify as PV
    on_host = not EC.runtime_differences(contract, PV.live_host_facts())
    if on_host:
        rec = EC.execute(B.ManufacturedPointBackend(base), ctx(require_runtime_match=True))
        out["runtime_match_on_frozen_host"] = {"pass": bool(rec["scientific_hash"])}
    else:
        expect("runtime_mismatch_off_host", lambda: EC.execute(B.ManufacturedPointBackend(base), ctx(require_runtime_match=True)),
               "RUNTIME_MISMATCH")

    class Tripwire(B.CusumPointBackend):
        def prepare_point(self, ctx_):
            raise RuntimeError("TRIPWIRE_REACHED: real backend entered")

    expect("guard_deny_real_backend_real_binding",
           lambda: EC.execute(Tripwire(IA.RealInputAdapter().bind()), ctx(IA.RealInputAdapter().bind())),
           "UNAUTHORIZED_REAL_ARITHMETIC")
    expect("guard_deny_production_backend_direct", lambda: B.CusumPointBackend(IA.RealInputAdapter().bind()).prepare_point(None),
           "UNAUTHORIZED_REAL_ARITHMETIC")
    return {"tests": out, "pass": all(v["pass"] for v in out.values())}


# ------------------------------------------------------------------ parts
def part_fixtures(proto, args):
    root = Path(tempfile.mkdtemp(prefix="exec-fx-"))
    rows = evaluate_fixtures(proto, root)
    payload = {k: v.get("scientific_hash") for k, v in sorted(rows.items())}
    return {"rows": rows, "pass": all(r["pass"] for r in rows.values()), "scientific_hashes": payload,
            "payload_sha256": sha(canonical(payload))}


def part_refusals(proto, args):
    root = Path(tempfile.mkdtemp(prefix="exec-rf-"))
    res = refusal_tests(proto, root, include_real_tripwire=True)
    import executor_core as EC
    res["tests"]["runtime_identity_mismatch_context"] = _one(lambda: EC.execute(
        __import__("backends").ManufacturedPointBackend(proto["fixtures"][0]),
        _ctx_with(proto, root, runtime_identity_sha256="0" * 64)), "RUNTIME_IDENTITY_MISMATCH")
    res["pass"] = all(v["pass"] for v in res["tests"].values())
    return res


def _ctx_with(proto, root, **kw):
    import input_adapters as IA
    c = context_for(IA.ManufacturedInputAdapter().bind(proto["fixtures"][0]), root / "ctxw")
    for k, v in kw.items():
        setattr(c, k, v)
    return c


def _one(fn, needle):
    import executor_core as EC
    try:
        fn()
        return {"pass": False, "outcome": "NOT_REFUSED"}
    except EC.ExecutorRefusal as exc:
        return {"pass": needle in str(exc), "outcome": str(exc)[:200]}


def part_separation(proto, args):
    import consumer as CO
    import qualification_gates as QG
    root = Path(tempfile.mkdtemp(prefix="exec-sep-"))
    out = {}
    for label, fid in proto["separation_fixtures"].items():
        spec = next(f for f in proto["fixtures"] if f["id"] == fid)
        rec = run_fixture(spec, root)
        it = CO.interpret(rec)
        neg = QG.negated(rec)
        g1 = QG.gates(rec, science_file_sha256=sha((paths.PROTOCOL_NS / "protocol/SCIENCE_PREREGISTRATION_R4.json").read_bytes()))
        g2 = QG.gates(neg, science_file_sha256=sha((paths.PROTOCOL_NS / "protocol/SCIENCE_PREREGISTRATION_R4.json").read_bytes()))
        out[label] = {"fixture": fid, "qualification": it["REAL_PRODUCER_QUALIFICATION"],
                      "verdict_m1": it["SCIENTIFIC_PROBE"]["1"]["verdict"], "gates_sign_invariant": g1 == g2}
    structural = qualification_structure()
    ok = (out["SUPPORTS"]["qualification"] == out["INCONCLUSIVE"]["qualification"] == out["CONTRADICTS"]["qualification"] == "PASS"
          and out["SUPPORTS"]["verdict_m1"] == "SUPPORTS_K5B_FIRST_CELL" and out["INCONCLUSIVE"]["verdict_m1"] == "INCONCLUSIVE"
          and out["CONTRADICTS"]["verdict_m1"] == "CONTRADICTS_REQUIRED_POSITIVE_SIGN"
          and all(v["gates_sign_invariant"] for v in out.values()) and structural["pass"])
    return {"cases": out, "structural": structural, "pass": ok}


def qualification_structure() -> dict:
    code = NS / "code"
    problems = []
    qg = ast.parse((code / "qualification_gates.py").read_text())
    for node in ast.walk(qg):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "PR" \
                and node.attr not in ("scientific_address", "load_prereg"):
            problems.append(f"qualification_gates uses PR.{node.attr}")
    for mod in ("executor_core.py", "backends.py", "input_adapters.py"):
        tree = ast.parse((code / mod).read_text())
        names = {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module} | \
                {a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
        if names & {"consumer", "qualification_gates"}:
            problems.append(f"{mod} imports the consumer or qualification gates")
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "PR" \
                    and node.attr in ("scientific_verdict", "point_sign", "h3a_consequence", "aggregate", "consumption_key",
                                      "k5b_consumption", "adoption_status"):
                problems.append(f"{mod} calls PR.{node.attr}")
    sm = (code / "smoke.py").read_text()
    tree = ast.parse(sm)
    used = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)} | {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for forbidden in ("certify_graded", "local_tower", "enclosure_stages", "execute", "transport"):
        if forbidden in used:
            problems.append(f"smoke.py references {forbidden}")
    return {"pass": not problems, "problems": problems}


def part_crosscheck(proto, args):
    import first_cell as FC3
    import m5_crosscheck as X
    import sigma_systems as SS
    root = Path(tempfile.mkdtemp(prefix="exec-xc-"))
    rows = []
    for fid in proto["crosscheck_fixtures"]:
        spec = next(f for f in proto["fixtures"] if f["id"] == fid)
        rec = run_fixture(spec, root)
        sysm = SS.build(spec)
        x1 = F(spec["x1"])
        grid = [x1 * F(g, 4) for g in range(5)]
        M5 = {m: float(F(rec["scientific"]["per_m"][str(m)]["M5"])) for m in (1, 2, 3, 5)}
        xc = X.crosscheck(spec, M5, lambda e, m, n: FC3.true_R(FC3.true_derivs(sysm, e), m, n), grid)
        encl = []
        for m in (1, 2, 3, 5):
            v = {k: F(s) for k, s in rec["scientific"]["per_m"][str(m)].items()}
            c3 = [X.cauchy_derivative(sysm, e, m, 3) for e in grid]
            tol = 1e-9 * max(1.0, max(abs(c) for c in c3))
            if not (float(v["L0"]) - tol <= c3[0] <= float(v["U0"]) + tol and float(v["L1"]) - tol <= min(c3)
                    and max(c3) <= float(v["U1"]) + tol):
                encl.append(m)
        rows.append({"fixture": fid, "cauchy": xc, "enclosure_disagreements_m": encl,
                     "pass": xc["pass"] and not encl})
    return {"rows": rows, "pass": all(r["pass"] for r in rows)}


def part_smoke(proto, args):
    import smoke
    rep = smoke.run(int(proto["smoke_seed"]))
    rep["pass"] = (rep["enclosure_formed"] is False and rep["observed_precision_bits"] == 256
                   and rep["guard"]["policy"] == "DENY" and rep["float_containment_count"] == 0)
    return rep


def part_inherited_r4(proto, args):
    os.environ.pop("O3R4_DEV_PROTOCOL_PATH", None)
    spec = importlib.util.spec_from_file_location("qualify_r4_inherited", paths.R4_NS / "code/qualify_r4.py")
    Q4 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(Q4)
    p4 = Q4.load_protocol()
    ns = argparse.Namespace(no_mutations=False)
    out = {}
    for name in proto["inherited_r4_parts"]:
        body = Q4.PARTS[name](p4, ns)
        if name == "first_cell":
            ok = all(r["violation_count"] == 0 and r.get("reference_R3_violations", 0) == 0 for r in body["rows"]) \
                 and all(r["violation_count"] == 0 for r in body["r3_rows"]) and body["lemma"]["pass"]
        elif name == "r5_mutations":
            ok = all(v["detected"] for v in body["mutations"].values())
        elif name == "odd_certificate":
            ok = all(v["pass"] for v in body["checks"].values())
        else:
            ok = body.get("pass") is True
        out[name] = {"pass": ok, "summary": {k: v for k, v in body.items() if k in ("pass",)}}
    return {"parts": out, "pass": all(v["pass"] for v in out.values())}


def part_runtime(proto, args):
    import executor_core as EC
    rt = runtime()
    contract = EC.prereg()["host_runtime_contract"]
    diff = sorted(k for k, v in contract.items() if rt.get(k) != v)
    return {"runtime": rt, "contract_differences": diff, "pass": not diff}


def part_fence(proto, args):
    out = {}
    for label, key in (("r1_r4_and_protocol_pins", "pins_sha256"), ("executor_sources", "executor_sources_sha256")):
        moved = [r for r, h in proto[key].items() if not (paths.REPO / r).exists() or sha((paths.REPO / r).read_bytes()) != h]
        out[label] = {"pass": not moved, "moved": moved[:10]}
    guard = json.loads((NS / "config/REAL_INPUT_GUARD.json").read_text())
    out["guard_policy_deny"] = {"pass": guard.get("policy") == "DENY"}
    spec = importlib.util.spec_from_file_location("no_monkeypatch", paths.CP / "p5y_k1_cusum_aux3_successor/code/no_monkeypatch.py")
    sys.path.append(str(paths.CP / "p5y_k1_cusum_aux3_successor/code"))
    nm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nm)
    findings = []
    for f in sorted((NS / "code").glob("*.py")):
        findings += nm.scan_source(f.read_text(), f.name)
    out["no_monkeypatch"] = {"pass": not findings, "findings": findings}
    auth = json.loads((NS / "config/EXTERNAL_AUTHORIZATION_TEMPLATE.json").read_text())
    out["authorization_inactive"] = {"pass": auth.get("EXECUTION_AUTHORIZED") is False and auth.get("status") == "INACTIVE_TEMPLATE"}
    science = paths.PROTOCOL_NS / "protocol/SCIENCE_PREREGISTRATION_R4.json"
    out["science_preregistration_unchanged"] = {"pass": sha(science.read_bytes()) == proto["science_preregistration_sha256"]}
    return {"checks": out, "pass": all(v["pass"] for v in out.values())}


def _run_mutant_check(mutant_dir: Path) -> dict | None:
    out = mutant_dir / "result.json"
    cmd = [sys.executable, "-B", str(Path(__file__).resolve()), "mutant-check", "--mutant-dir", str(mutant_dir), "--out", str(out)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    if not out.exists():
        return {"error": f"mutant check produced no result rc={p.returncode}", "stderr": p.stderr[-800:]}
    return json.loads(out.read_text())


def part_mutations(proto, args):
    """Control first: the unmutated sources must meet every expectation. A mutant is DETECTED only if its check ran to
    completion and some expectation failed; a harness crash is NOT a detection."""
    control_dir = Path(tempfile.mkdtemp(prefix="exec-mut-control-"))
    control = _run_mutant_check(control_dir)
    res = {}
    for mut in proto["mutations"]:
        tmp = Path(tempfile.mkdtemp(prefix=f"exec-mut-{mut['id']}-"))
        src = (NS / "code" / mut["file"]).read_text()
        if src.count(mut["old"]) != 1:
            res[mut["id"]] = {"detected": False, "error": f"anchor matches {src.count(mut['old'])} times"}
            continue
        mutated = src.replace(mut["old"], mut["new"]).replace("NS = Path(__file__).resolve().parents[1]", f'NS = Path("{NS}")')
        (tmp / mut["file"]).write_text(mutated)
        r = _run_mutant_check(tmp)
        if "error" in r:
            res[mut["id"]] = {"detected": False, **r}
        else:
            res[mut["id"]] = {"detected": not r["all_expected"], "failing": r["failing"][:6]}
            shutil.rmtree(tmp, ignore_errors=True)
    control_ok = "error" not in control and control["all_expected"]
    return {"control": {"pass": control_ok, "failing": control.get("failing", control.get("error"))},
            "mutations": res, "pass": control_ok and all(v["detected"] for v in res.values()),
            "count": f"{sum(v['detected'] for v in res.values())}/{len(res)}"}


def mutant_check(args):
    """Runs inside a fresh process with the mutated module shadowing the frozen one."""
    sys.path.insert(0, args.mutant_dir)
    proto = load_protocol()
    root = Path(tempfile.mkdtemp(prefix="exec-mc-"))
    rows = evaluate_fixtures(proto, root)
    try:
        refusals = refusal_tests(proto, root / "rf", include_real_tripwire=True)
    except Exception as exc:                                  # a crash inside the refusal harness is a failed expectation
        refusals = {"tests": {"refusal_harness": {"pass": False, "outcome": f"{type(exc).__name__}: {str(exc)[:200]}"}}}
    failing = [k for k, v in rows.items() if not v["pass"]] + [k for k, v in refusals["tests"].items() if not v["pass"]]
    Path(args.out).write_text(json.dumps({"all_expected": not failing, "failing": failing,
                                          "rows": {k: {x: v.get(x) for x in ("refused", "failed_gates", "truth_violations")}
                                                   for k, v in rows.items()}}, default=str))


PARTS = {"fixtures": part_fixtures, "refusals": part_refusals, "separation": part_separation,
         "crosscheck": part_crosscheck, "smoke": part_smoke, "inherited_r4": part_inherited_r4, "runtime": part_runtime,
         "fence": part_fence, "mutations": part_mutations}
ORDER = ["smoke", "mutations", "inherited_r4", "fixtures", "fixtures_replay", "refusals", "separation", "crosscheck",
         "runtime", "fence"]


def run_part(args):
    proto = load_protocol()
    t0, w0 = time.process_time(), time.time()
    body = PARTS[args.part](proto, args)
    rec = {"part": args.part, "body": body, "runtime": runtime(), "protocol_sha256": sha(PROTOCOL.read_bytes()),
           "metadata": {"incidental": True, "cpu_seconds": time.process_time() - t0, "wall_seconds": time.time() - w0,
                        "children_cpu_seconds": resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime,
                        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    Path(args.out).write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")


def assemble(proto, outdir: Path) -> dict:
    P = {n: json.loads((outdir / f"part_{n}.json").read_text()) for n in ORDER}
    B = {n: p["body"] for n, p in P.items()}
    fx, smk = B["fixtures"], B["smoke"]
    fixture_cpu = max(r.get("cpu_seconds", 0) for r in fx["rows"].values())
    projected = (smk["cost"]["cpu_seconds_real_arb_stages"] + proto["cost_model"]["committed_collocation_cpu_seconds"]
                 + proto["cost_model"]["enclosure_and_tower_allowance_cpu_seconds"]) * proto["cost_model"]["safety_factor"]
    ceil = proto["cpu_ceiling"]
    cost_ok = projected <= ceil["per_attempt_cpu_seconds_soft"] and projected * ceil["max_attempts"] <= ceil["campaign_cpu_seconds_hard"]
    diffs = sorted(k for k in fx["scientific_hashes"] if fx["scientific_hashes"][k] != B["fixtures_replay"]["scientific_hashes"].get(k))
    gates = {
        "EG01_manufactured_fixtures_truth_and_expected_verdicts": fx["pass"],
        "EG02_fail_closed_refusals": B["refusals"]["pass"],
        "EG03_real_input_arithmetic_guard_deny": all(B["refusals"]["tests"][t]["pass"] for t in
                                                     ("guard_deny_real_backend_real_binding", "guard_deny_production_backend_direct")),
        "EG04_qualification_science_separation": B["separation"]["pass"],
        "EG05_independent_derivative_crosscheck": B["crosscheck"]["pass"],
        "EG06_executor_mutations_all_detected": B["mutations"]["pass"] and len(B["mutations"]["mutations"]) == 16,
        "EG07_inherited_r4_gates": B["inherited_r4"]["pass"],
        "EG08_deterministic_replay": fx["payload_sha256"] == B["fixtures_replay"]["payload_sha256"] and not diffs,
        "EG09_real_stage_smoke_no_enclosure": smk["pass"],
        "EG10_runtime_identity": B["runtime"]["pass"] and all(
            all(P[n]["runtime"].get(k) == v for k, v in proto["runtime_contract"].items()) for n in ORDER),
        "EG11_fences_and_pins": B["fence"]["pass"] and all(P[n]["protocol_sha256"] == sha(PROTOCOL.read_bytes()) for n in ORDER),
        "EG12_cost_within_frozen_ceiling": cost_ok,
    }
    verdict = "QUALIFIED_AWAITING_EXTERNAL_AUTHORIZATION" if all(gates.values()) else (
        "NOT_READY" if not (gates["EG01_manufactured_fixtures_truth_and_expected_verdicts"] and gates["EG02_fail_closed_refusals"]
                            and gates["EG03_real_input_arithmetic_guard_deny"] and gates["EG05_independent_derivative_crosscheck"])
        else "PARTIALLY_QUALIFIED")
    return {"schema": "rebaseguard.p5y.k5.cusum-real-point-executor.qualification-result.v1",
            "protocol_sha256": sha(PROTOCOL.read_bytes()), "part_sha256": {n: sha((outdir / f"part_{n}.json").read_bytes()) for n in ORDER},
            "gates": {k: "PASS" if v else "FAIL" for k, v in gates.items()}, "REAL_POINT_EXECUTOR": verdict,
            "executor_identity_sha256": proto["executor_identity_sha256"],
            "mutations": B["mutations"]["count"], "mutation_detail": B["mutations"]["mutations"],
            "fixtures": {k: {x: v.get(x) for x in ("purpose", "qualification", "verdicts", "truth_violations", "M5_over_truth", "pass")}
                         for k, v in fx["rows"].items()},
            "scientific_leaf_differences": diffs, "replay_payload_sha256": [fx["payload_sha256"], B["fixtures_replay"]["payload_sha256"]],
            "separation": B["separation"]["cases"], "crosscheck": [{k: r[k] for k in ("fixture", "enclosure_disagreements_m", "pass")}
                                                                   for r in B["crosscheck"]["rows"]],
            "smoke": {k: smk[k] for k in ("enclosure_formed", "observed_precision_bits", "float_containment_count", "cost", "structure_sha256")},
            "cost": {"measured_manufactured_fixture_cpu_seconds_max": fixture_cpu,
                     "measured_real_arb_stages_cpu_seconds": smk["cost"]["cpu_seconds_real_arb_stages"],
                     "projected_real_attempt_cpu_seconds": projected, "projected_campaign_cpu_seconds_max_attempts": projected * ceil["max_attempts"],
                     "ceiling": ceil, "compatible": cost_ok},
            "runtime": B["runtime"]["runtime"],
            "REAL_INPUT_ARITHMETIC_GUARD": "DENY", "EXECUTION_AUTHORIZED": False, "REAL_CELL_EXECUTED": "NO"}


def jobs(outdir):
    J = []
    for n in ORDER:
        part = "fixtures" if n == "fixtures_replay" else n
        J.append([sys.executable, "-B", str(Path(__file__).resolve()), "part", part, "--out", str(outdir / f"part_{n}.json")])
    return J


def cmd_run(args):
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "RUN_STATE.json").write_text(json.dumps({"pid": os.getpid(), "argv": sys.argv, "started_unix": time.time()}) + "\n")
    try:
        proto = load_protocol()
        env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", PYTHONHASHSEED="0")
        pending, running, failures = list(jobs(outdir)), [], []
        while pending or running:
            while pending and len(running) < int(args.workers):
                cmd = pending.pop(0)
                log = open(str(cmd[-1]).replace(".json", ".log"), "w")
                running.append((cmd, subprocess.Popen(cmd, env=env, stdout=log, stderr=subprocess.STDOUT), log))
            time.sleep(2)
            for item in list(running):
                cmd, p, log = item
                if p.poll() is not None:
                    running.remove(item)
                    log.close()
                    if p.returncode != 0:
                        failures.append({"cmd": cmd[3:], "rc": p.returncode})
        result = assemble(proto, outdir)
        result["runner_failures"] = failures
        raw = (json.dumps(result, indent=1, sort_keys=True, default=str) + "\n").encode()
        (outdir / "QUALIFICATION_RESULT_EXECUTOR.json").write_bytes(raw)
        (outdir / "RUN_COMPLETE.json").write_text(json.dumps({"pid": os.getpid(), "result_sha256": sha(raw),
                                                              "runner_failures": len(failures)}) + "\n")
        print(json.dumps({"verdict": result["REAL_POINT_EXECUTOR"], "gates": result["gates"]}, indent=1))
    except BaseException:
        (outdir / "RUN_FAILED.json").write_text(json.dumps({"pid": os.getpid(), "traceback": traceback.format_exc()}) + "\n")
        raise


def cmd_check(args):
    proto = load_protocol()
    outdir = Path(args.outdir)
    stored = json.loads((outdir / "QUALIFICATION_RESULT_EXECUTOR.json").read_text())
    again = assemble(proto, outdir)
    problems = [k for k in ("gates", "part_sha256", "protocol_sha256", "REAL_POINT_EXECUTOR", "mutations") if again[k] != stored[k]]
    moved = [r for key in ("pins_sha256", "executor_sources_sha256") for r, h in proto[key].items()
             if sha((paths.REPO / r).read_bytes()) != h]
    done = json.loads((outdir / "RUN_COMPLETE.json").read_text())
    if done["result_sha256"] != sha((outdir / "QUALIFICATION_RESULT_EXECUTOR.json").read_bytes()):
        problems.append("completion marker")
    print(json.dumps({"problems": problems + moved, "verdict": again["REAL_POINT_EXECUTOR"], "gates": again["gates"]}, indent=1))
    sys.exit(1 if problems or moved else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("part")
    p.add_argument("part", choices=sorted(PARTS))
    p.add_argument("--out", required=True)
    mc = sub.add_parser("mutant-check")
    mc.add_argument("--mutant-dir", required=True)
    mc.add_argument("--out", required=True)
    r = sub.add_parser("run")
    r.add_argument("--outdir", required=True)
    r.add_argument("--workers", default="4")
    c = sub.add_parser("check")
    c.add_argument("--outdir", required=True)
    a = ap.parse_args()
    {"part": run_part, "mutant-check": mutant_check, "run": cmd_run, "check": cmd_check}[a.cmd](a)
