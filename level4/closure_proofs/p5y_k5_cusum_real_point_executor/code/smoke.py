"""Real-stage smoke (QUALIFICATION ONLY): the real Arb stages of the executor at the degenerate cell {0} with SYNTHETIC
candidates (R3 SyntheticGradedCert: real kernels, parity-pure synthetic polynomials that approximate no DAG object, no
collocation). Runs the SAME shared stages as executor_core.execute (run_stages_before_enclosure: prepare, residuals,
graded inputs + origin values, candidate graded suprema, hull base) and STOPS: no graded point cascade with origin
values, no local tower, no transport, so no R''' or R^(5) enclosure of any kind is formed (structural test: this module
references none of certify_graded / local_tower / enclosure_stages / execute).

Binding: RealInputAdapter (metadata only; validates the frozen K1 cell-0 record; payload redacted).
Checks: stage outputs complete; graded point residual bounds dominate independent float-quadrature parity parts of the
synthetic residuals at e = 0 (names whose source is not the r = 0 closed form); cost of the real Arb stages.

r2 (EXECUTOR_SPEC_R2.md R2-4) adds, on the SAME production helpers the real backend uses:
  Q04  backends.production_gate initial / final with a ScipyGuard around all smoke arithmetic
  Q06  backends.certificate_replay (C_o0 R4, C_e0 R3)
  Q08  _CusumStack.scalar_consistency on the origin-free cascade (radii only; no centre, no enclosure)
  Q10  backends.order2_rows on the smoke certifier (path check), and order2_reference(): a fresh frozen Order2Certifier
       at the point {0} (the 84aaa6a5 path; R and R' at e = 0, already published) compared by backends.order2_compare
  shared-method checks (registry constants, hull x1, origin payload identity, candidate parity containment) and the
  in-process production-stack mutants P01-P04, which those checks must detect.
"""
from __future__ import annotations

import hashlib
import json
import resource
import time
from fractions import Fraction as F

import paths  # noqa: F401

import executor_core as EC  # noqa: E402
import input_adapters as IA  # noqa: E402
import rung3_engine as R1E  # noqa: E402

CHECK_NAMES = ["h_1:2", "S_0:1", "h_2:1", "h_3:2", "S_1:1", "S_2:2", "dF_1", "H_1", "G_1", "W_0_1:1", "W_1_1:2",
               "h_2:3", "S_1:3", "W_0_1:3"]


def candidate_float_checks(cert, candidates: dict) -> list:
    """Candidate graded suprema (e, o) dominate the float even / odd parts of the synthetic candidate payloads."""
    import backends as B
    import synthetic_real as SR
    viol = []
    for key, pay in sorted(cert.payloads.items(), key=lambda kv: repr(kv[0])):
        node = B.node_for_key(key)
        if node is None or node not in candidates:
            continue
        e, o = candidates[node]
        be, bo = float(R1E.fraction_of(e.abs_upper())), float(R1E.fraction_of(o.abs_upper()))
        for p, m in SR.reachable_states():
            x, y = SR.cheb(pay, p, m), SR.cheb(pay, m, p)
            if abs(x + y) / 2 > be + SR.FLOAT_TOL or abs(x - y) / 2 > bo + SR.FLOAT_TOL:
                viol.append(f"{node} at {p},{m}")
                break
    return viol


def stage_checks(backend, state, stages) -> dict:
    s = backend.shared_structure(state, stages)["problems"]
    c = candidate_float_checks(state["cert"], stages["candidates"])
    return {"structure_problems": s, "candidate_violations": c[:10], "detected": bool(s or c)}


def production_mutants(state, stages, backend) -> dict:
    """P01-P04: text mutants of the shared _CusumStack methods, loaded in-process; detected by the UNMUTATED checks."""
    import importlib.util
    import make_protocol_executor as MP
    rows = {}
    for mut in MP.production_mutations():
        src = (paths.NS / "code" / mut["file"]).read_text()
        if src.count(mut["old"]) != 1:
            rows[mut["id"]] = {"detected": False, "error": "anchor"}
            continue
        spec = importlib.util.spec_from_loader(f"backends_{mut['id']}", loader=None)
        mod = importlib.util.module_from_spec(spec)
        exec(compile(src.replace(mut["old"], mut["new"]), f"<{mut['id']}>", "exec"), mod.__dict__)
        mb = mod.SyntheticCusumSmokeBackend(backend.binding, backend.seed)
        try:
            with R1E.precision(EC.PRECISION):
                consts = mb.constants(state)
                ms = {"state": state, "constants": consts, "inputs": mb.point_graded_inputs(state, consts),
                      "candidates": mb.candidate_graded_sups(state), "base": mb.hull_tower_base(state, consts)}
                rows[mut["id"]] = stage_checks(backend, state, ms)
        except Exception as exc:                                     # a crash is NOT a detection
            rows[mut["id"]] = {"detected": False, "crashed": f"{type(exc).__name__}: {str(exc)[:200]}"}
    return rows


def run(seed: int) -> dict:
    import backends as B
    import synthetic_real as SR
    binding = IA.RealInputAdapter().bind()
    backend = B.SyntheticCusumSmokeBackend(binding, seed)
    EC.enforce_guard(backend)
    ctx = EC.ExecutionContext(k1_binding=binding, output_dir=paths.NS / "unused")
    gate_initial = B.production_gate("initial")
    guard = B.scipy_guard_module().ScipyGuard()
    t0, w0 = time.process_time(), time.time()
    with guard, R1E.precision(EC.PRECISION):
        from flint import ctx as flint_ctx
        observed = flint_ctx.prec
        stages = EC.run_stages_before_enclosure(backend, ctx)
        t_stages = time.process_time() - t0
        state = stages["state"]
        cert, inputs = state["cert"], stages["inputs"]
        viol = []
        for name in CHECK_NAMES:
            ent = inputs["res"][EC_engine_name(name)]
            be = float(R1E.fraction_of(ent["mid"][0].abs_upper()))
            bo = float(R1E.fraction_of(ent["mid"][1].abs_upper()))
            for p, m in SR.reachable_states():
                v, vs = SR.residual_float(cert, name, p, m, 0.0), SR.residual_float(cert, name, m, p, 0.0)
                if abs(v + vs) / 2 > be + SR.FLOAT_TOL or abs(v - vs) / 2 > bo + SR.FLOAT_TOL:
                    viol.append(f"{name} at {p},{m}")
        t1 = time.process_time()
        q08 = backend.scalar_consistency(state, inputs, "SMOKE")
        t_q08, t1 = time.process_time() - t1, time.process_time()
        rows = B.order2_rows(cert)
        order2_path = all(F(r[k]["lo"]) <= F(r[k]["hi"]) for r in rows.values() for k in ("R_interval", "D_interval"))
        t_q10, t1 = time.process_time() - t1, time.process_time()
        q06 = B.certificate_replay()
        t_q06 = time.process_time() - t1
        checks = stage_checks(backend, state, stages)
    gate_final = B.production_gate("final", guard)
    mutants = production_mutants(state, stages, backend)
    summary = {"residual_names": sorted(inputs["res"]), "candidate_nodes": sorted(stages["candidates"]),
               "base_keys": sorted(stages["base"]), "origin_keys": sorted(str(k) for k in inputs["origin"]),
               "constants_source": stages["constants"]["source"]}
    return {"schema": "rebaseguard.p5y.k5.cusum-real-point-executor.smoke.v2", "binding": binding,
            "backend": backend.describe(), "guard": EC.guard_decision(), "observed_precision_bits": observed,
            "enclosure_formed": False, "structure": summary,
            "structure_sha256": hashlib.sha256(json.dumps(summary, sort_keys=True).encode()).hexdigest(),
            "float_containment_violations": viol[:20], "float_containment_count": len(viol),
            "Q04": {"initial": gate_initial, "final": gate_final,
                    "pass": gate_initial["pass"] and gate_final["pass"] and gate_final["scipy_free"] is True},
            "Q06": q06, "Q08": q08, "Q10_path_on_smoke_certifier": {"pass": order2_path, "m": sorted(rows)},
            "shared_method_checks": checks, "production_mutants": mutants,
            "cost": {"cpu_seconds_real_arb_stages": t_stages, "cpu_seconds_q06_certificate_replay": t_q06,
                     "cpu_seconds_q08": t_q08, "cpu_seconds_q10_path": t_q10, "wall_seconds": time.time() - w0,
                     "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}


def order2_reference() -> dict:
    """Q10 comparator on the frozen certifier: a fresh Order2Certifier at the point {0} of frozen cell 0 (exactly the
    84aaa6a5 point_eval path; R(0) and R'(0) only, both already published) compared with RUNG_256 by the executor's
    backends.order2_compare; plus a comparator mutant (R' sign flipped) that must be refused."""
    import backends as B
    import k1_inputs
    import point_core
    guard = B.scipy_guard_module().ScipyGuard()                   # imports the Aux5 ancestry first
    from order2 import Order2Certifier
    from repair_check import require_single_charge
    cell = point_core.point_cell(k1_inputs.frozen_cell(0), F(0))
    t0 = time.process_time()
    with guard, R1E.precision(EC.PRECISION):
        cert = Order2Certifier(cell, bits=EC.PRECISION).prepare()
        cert.all_residuals()
        require_single_charge(cert, cert.residuals)
        rows = B.order2_rows(cert)
    cmp_ = B.order2_compare(rows)
    flipped = {m: {"R_interval": r["R_interval"], "D_interval": {"lo": str(-F(r["D_interval"]["hi"])),
                                                                  "hi": str(-F(r["D_interval"]["lo"]))}}
               for m, r in rows.items()}
    mutant = B.order2_compare(flipped)
    return {"compare": cmp_, "comparator_mutant_refused": not mutant["pass"],
            "scipy_free": guard.require_clean()["scipy_free"], "pass": cmp_["pass"] and not mutant["pass"],
            "cpu_seconds": time.process_time() - t0}


def EC_engine_name(name: str) -> str:
    import graded_real as GR
    return GR.engine_name(name)
