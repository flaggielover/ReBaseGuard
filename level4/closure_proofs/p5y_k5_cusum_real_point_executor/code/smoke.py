"""Real-stage smoke (QUALIFICATION ONLY): the real Arb stages of the executor at the degenerate cell {0} with SYNTHETIC
candidates (R3 SyntheticGradedCert: real kernels, parity-pure synthetic polynomials that approximate no DAG object, no
collocation). Runs the SAME shared stages as executor_core.execute (run_stages_before_enclosure: prepare, residuals,
graded inputs + origin values, candidate graded suprema, hull base) and STOPS: no graded point cascade, no local tower,
no transport, so no R''' or R^(5) enclosure of any kind is formed (structural test: this module references none of
certify_graded / local_tower / enclosure_stages / execute).

Binding: RealInputAdapter (metadata only; validates the frozen K1 cell-0 record; payload redacted).
Checks: stage outputs complete; graded point residual bounds dominate independent float-quadrature parity parts of the
synthetic residuals at e = 0 (names whose source is not the r = 0 closed form); cost of the real Arb stages.
"""
from __future__ import annotations

import hashlib
import json
import resource
import time

import paths  # noqa: F401

import executor_core as EC  # noqa: E402
import input_adapters as IA  # noqa: E402
import rung3_engine as R1E  # noqa: E402

CHECK_NAMES = ["h_1:2", "S_0:1", "h_2:1", "h_3:2", "S_1:1", "S_2:2", "dF_1", "H_1", "G_1", "W_0_1:1", "W_1_1:2",
               "h_2:3", "S_1:3", "W_0_1:3"]


def run(seed: int) -> dict:
    import backends as B
    import synthetic_real as SR
    binding = IA.RealInputAdapter().bind()
    backend = B.SyntheticCusumSmokeBackend(binding, seed)
    EC.enforce_guard(backend)
    ctx = EC.ExecutionContext(k1_binding=binding, output_dir=paths.NS / "unused")
    t0, w0 = time.process_time(), time.time()
    with R1E.precision(EC.PRECISION):
        from flint import ctx as flint_ctx
        observed = flint_ctx.prec
        stages = EC.run_stages_before_enclosure(backend, ctx)
    t_stages = time.process_time() - t0
    cert, inputs = stages["state"]["cert"], stages["inputs"]
    viol = []
    for name in CHECK_NAMES:
        ent = inputs["res"][EC_engine_name(name)]
        be = float(R1E.fraction_of(ent["mid"][0].abs_upper()))
        bo = float(R1E.fraction_of(ent["mid"][1].abs_upper()))
        for p, m in SR.reachable_states():
            v, vs = SR.residual_float(cert, name, p, m, 0.0), SR.residual_float(cert, name, m, p, 0.0)
            if abs(v + vs) / 2 > be + SR.FLOAT_TOL or abs(v - vs) / 2 > bo + SR.FLOAT_TOL:
                viol.append(f"{name} at {p},{m}")
    summary = {"residual_names": sorted(inputs["res"]), "candidate_nodes": sorted(stages["candidates"]),
               "base_keys": sorted(stages["base"]), "origin_keys": sorted(str(k) for k in inputs["origin"]),
               "constants_source": stages["constants"]["source"]}
    return {"schema": "rebaseguard.p5y.k5.cusum-real-point-executor.smoke.v1", "binding": binding,
            "backend": backend.describe(), "guard": EC.guard_decision(), "observed_precision_bits": observed,
            "enclosure_formed": False, "structure": summary,
            "structure_sha256": hashlib.sha256(json.dumps(summary, sort_keys=True).encode()).hexdigest(),
            "float_containment_violations": viol[:20], "float_containment_count": len(viol),
            "cost": {"cpu_seconds_real_arb_stages": t_stages, "wall_seconds": time.time() - w0,
                     "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}


def EC_engine_name(name: str) -> str:
    import graded_real as GR
    return GR.engine_name(name)
