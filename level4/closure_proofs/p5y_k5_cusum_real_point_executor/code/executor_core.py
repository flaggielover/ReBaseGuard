"""Real point executor core (EXECUTOR_SPEC.md). Computes CERTIFICATES ONLY; never interprets a sign.

    execute(backend, context)              -> sealed record (scientific payload + separate metadata)
    run_stages_before_enclosure(backend, context) -> the shared real-stack stages (prepare, residuals, graded inputs,
                                             candidate graded suprema, hull base) used by execute() and by the
                                             real-stage smoke (which stops here: no enclosure is formed)

Pipeline after those stages (R2/R3/R4 reuse, no new mathematics):
    graded_dag.certify_graded(inputs, parity=True)             -> I0_m = R3_mid (point, degenerate cell {0})
    local_r5.local_tower(base, cands, point nodes, x1)          -> M5_m >= sup_[0,x1] |R_m^(5)|
    transport_factor = x1^2/2 (exact);  L1 = L0 - tf M5;  U1 = U0 + tf M5
REAL_INPUT_ARITHMETIC_GUARD: config/REAL_INPUT_GUARD.json; the only recognized policy is DENY; a backend with
real_input = True is refused before any backend method is called.
"""
from __future__ import annotations

import hashlib
import json
import os
import resource
import time
from dataclasses import dataclass, field
from fractions import Fraction as F
from pathlib import Path

import paths  # noqa: F401  (sys.path for R1-R4, protocol, point certificate)

import graded_dag as G  # noqa: E402
import local_r5 as LR  # noqa: E402
import probe_rules as PR  # noqa: E402
import rung3_engine as R1E  # noqa: E402

NS = Path(__file__).resolve().parents[1]
GUARD_FILE = NS / "config/REAL_INPUT_GUARD.json"
SCIENCE_FILE = paths.PROTOCOL_NS / "protocol/SCIENCE_PREREGISTRATION_R4.json"
RECORD_SCHEMA = "rebaseguard.p5y.k5.cusum-real-point-executor.record.v1"
M_SET = [1, 2, 3, 5]
PRECISION = 256
REAL_SEAL_NAME = "SCIENTIFIC_RECORD_SEALED.json"
MANUFACTURED_SEAL_NAME = "MANUFACTURED_RECORD_SEALED.json"
FAMILIES = ("F", "D", "H", "G")


class ExecutorRefusal(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def q(x) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def up(v) -> str:
    return q(R1E.upper_fraction(v))


# ------------------------------------------------------------------ guard
def guard_decision() -> dict:
    """REAL_INPUT_ARITHMETIC_GUARD. Only DENY is recognized; every other state is also a denial."""
    try:
        policy = json.loads(GUARD_FILE.read_text()).get("policy")
    except (OSError, ValueError, AttributeError):
        return {"policy": None, "real_arithmetic_permitted": False, "reason": "guard file unreadable: DENY"}
    if policy == "DENY":
        return {"policy": "DENY", "real_arithmetic_permitted": False, "reason": "REAL_INPUT_ARITHMETIC_GUARD = DENY"}
    return {"policy": policy, "real_arithmetic_permitted": False, "reason": f"unrecognized guard policy {policy!r}: DENY"}


def enforce_guard(backend) -> None:
    if getattr(backend, "real_input", True):
        decision = guard_decision()
        if not decision["real_arithmetic_permitted"]:
            raise ExecutorRefusal(f"UNAUTHORIZED_REAL_ARITHMETIC: {decision['reason']}")


# ------------------------------------------------------------------ context
@dataclass
class ExecutionContext:
    k1_binding: dict
    output_dir: Path
    m_set: list = field(default_factory=lambda: list(M_SET))
    point_e: str = "0/1"
    theorem_cell: str = "C_1"
    precision_bits: int = PRECISION
    producer_identity_sha256: str = ""
    protocol_sha256: str = ""
    runtime_identity_sha256: str = ""
    require_runtime_match: bool = False
    executor_binding_sha256: str = "UNBOUND_QUALIFICATION"


BINDING_KEYS = {"kind", "detector", "k1_cell_index", "left", "right", "C_upper", "C_evaluation", "record_sha256",
                "export_manifest_sha256", "cells_json_sha256", "adapter", "redacted"}


def prereg() -> dict:
    return json.loads(SCIENCE_FILE.read_text())


def validate_context(ctx: ExecutionContext, backend) -> dict:
    p = prereg()
    b = ctx.k1_binding
    if not isinstance(b, dict) or set(b) != BINDING_KEYS:
        raise ExecutorRefusal("UNBOUND_OR_MALFORMED_INPUT: binding does not have the adapter schema")
    if b["adapter"] not in ("RealInputAdapter", "ManufacturedInputAdapter") or b["redacted"] is not True:
        raise ExecutorRefusal("UNBOUND_OR_MALFORMED_INPUT: binding not produced by an input adapter")
    if b["kind"] == "real":
        want = p["k1_input_identity"]
        if b["record_sha256"] != want["record_sha256"] or b["export_manifest_sha256"] != want["manifest_sha256"] \
                or b["cells_json_sha256"] != want["cells_json_sha256"]:
            raise ExecutorRefusal("K1_IDENTITY_MISMATCH")
        if b["right"] != p["cell_selection"]["selected"]["right"]:
            raise ExecutorRefusal("CELL_ENDPOINT_MISMATCH")
        if not backend.real_input:
            raise ExecutorRefusal("real binding with a non-real backend")
    elif b["kind"] == "manufactured":
        if backend.real_input:
            raise ExecutorRefusal("manufactured binding with a real backend")
    else:
        raise ExecutorRefusal("UNBOUND_OR_MALFORMED_INPUT: unknown binding kind")
    if b["detector"] != "CUSUM" or b["k1_cell_index"] != 0 or b["left"] != "0/1" or F(b["C_evaluation"]) != 0:
        raise ExecutorRefusal("CELL_IDENTITY_MISMATCH")
    if not F(b["right"]) > 0:
        raise ExecutorRefusal("CELL_ENDPOINT_MISMATCH")
    if list(ctx.m_set) != M_SET:
        raise ExecutorRefusal(f"M_SET_MISMATCH: {ctx.m_set}")
    if ctx.point_e != "0/1":
        raise ExecutorRefusal(f"POINT_MISMATCH: {ctx.point_e}")
    if ctx.theorem_cell != "C_1":
        raise ExecutorRefusal("THEOREM_CELL_MISMATCH")
    if ctx.precision_bits != PRECISION or ctx.precision_bits not in p["precision_ladder"]["bits"]:
        raise ExecutorRefusal(f"UNSUPPORTED_PRECISION: {ctx.precision_bits}")
    if ctx.producer_identity_sha256 != p["producer_identity_sha256"]:
        raise ExecutorRefusal("PRODUCER_IDENTITY_MISMATCH")
    if ctx.protocol_sha256 != sha(SCIENCE_FILE.read_bytes()):
        raise ExecutorRefusal("PROTOCOL_IDENTITY_MISMATCH")
    if ctx.runtime_identity_sha256 != p["host_runtime_identity_sha256"]:
        raise ExecutorRefusal("RUNTIME_IDENTITY_MISMATCH")
    if backend.real_input or ctx.require_runtime_match:
        import prelaunch_verify as PV
        diff = runtime_differences(p["host_runtime_contract"], PV.live_host_facts())
        if diff:
            raise ExecutorRefusal(f"RUNTIME_MISMATCH: {diff}")
    out = Path(ctx.output_dir)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ExecutorRefusal("STALE_OUTPUT_NAMESPACE")
    return p


def runtime_differences(contract: dict, live: dict) -> list:
    return sorted(k for k, v in contract.items() if live.get(k) != v)


def addresses(ctx: ExecutionContext) -> dict:
    return {m: PR.scientific_address(m=m, k1_record_sha256=ctx.k1_binding["record_sha256"],
                                     producer_identity_sha256=ctx.producer_identity_sha256,
                                     executor_binding_sha256=ctx.executor_binding_sha256,
                                     protocol_sha256=ctx.protocol_sha256, precision_bits=ctx.precision_bits)
            for m in ctx.m_set}


def refuse_finalized_addresses(ctx: ExecutionContext, addr: dict) -> None:
    root = Path(ctx.output_dir).parent
    wanted = {a["address_sha256"] for a in addr.values()}
    if not root.exists():
        return
    for name in (REAL_SEAL_NAME, MANUFACTURED_SEAL_NAME):
        for path in root.rglob(name):
            try:
                rec = json.loads(path.read_text())
            except ValueError:
                raise ExecutorRefusal(f"unreadable sealed record {path}")
            if wanted & {a["address_sha256"] for a in rec["scientific"]["addresses"].values()}:
                raise ExecutorRefusal(f"FINALIZED_ADDRESS_EXISTS: {path}")


# ------------------------------------------------------------------ stages
def run_stages_before_enclosure(backend, ctx: ExecutionContext) -> dict:
    """Shared by execute() and by the real-stage smoke. Must be called inside the certifying precision context."""
    state = backend.prepare_point(ctx)
    constants = backend.constants(state)
    inputs = backend.point_graded_inputs(state, constants)
    candidates = backend.candidate_graded_sups(state)
    base = backend.hull_tower_base(state, constants)
    validate_stage_outputs(inputs, candidates, base)
    return {"state": state, "constants": constants, "inputs": inputs, "candidates": candidates, "base": base}


GRADED_INPUT_KEYS = ("C", "C_e0", "C_o0", "k", "j", "k_hull", "j_hull", "eta_mid", "eta_cell", "res", "origin")
BASE_KEYS = ("C", "C_e0", "C_o0", "k", "j", "eta", "S0")


def validate_stage_outputs(inputs: dict, candidates: dict, base: dict) -> None:
    missing = [k for k in GRADED_INPUT_KEYS if k not in inputs]
    if missing or not inputs.get("x0_sigma_fixed"):
        raise ExecutorRefusal(f"INCOMPLETE_CERTIFICATE_CHAIN: graded inputs missing {missing}")
    if R1E.fraction_of(inputs["eta_mid"].abs_upper()) != 0:
        raise ExecutorRefusal("POINT_MISMATCH: eta_mid is not 0 (the point cell is not e = 0)")
    for r in range(5):
        if ("G", r) not in inputs["origin"]:
            raise ExecutorRefusal("INCOMPLETE_CERTIFICATE_CHAIN: origin values")
    missing = [k for k in BASE_KEYS if k not in base] + [f"k{i}" for i in range(7) if i not in base.get("k", {})]
    if missing:
        raise ExecutorRefusal(f"INCOMPLETE_CERTIFICATE_CHAIN: hull base missing {missing}")
    if not candidates or any(int(n.split(":")[-1]) > 3 for n in candidates):
        raise ExecutorRefusal("INCOMPLETE_CERTIFICATE_CHAIN: candidate graded suprema")


def enclosure_stages(stages: dict, x1: F) -> dict:
    out0 = G.certify_graded(stages["inputs"], parity=True)
    loc = LR.local_tower(stages["base"], stages["candidates"], out0["mid"]["nodes"], x1=R1E.exact(x1))
    tf = x1 * x1 / 2
    per_m = {}
    for m in M_SET:
        if m not in out0["m"]:
            raise ExecutorRefusal("INCOMPLETE_CERTIFICATE_CHAIN: point enclosure")
        L0, U0 = out0["m"][m]["R3_mid"]
        M5 = R1E.fraction_of(loc["M5"][m].abs_upper())
        per_m[m] = {"L0": L0, "U0": U0, "M5": M5, "transport_factor": tf, "L1": L0 - tf * M5, "U1": U0 + tf * M5}
    return {"out0": out0, "local": loc, "per_m": per_m}


# ------------------------------------------------------------------ execute
def execute(backend, ctx: ExecutionContext) -> dict:
    enforce_guard(backend)                                   # FIRST: before any backend method
    p = validate_context(ctx, backend)
    addr = addresses(ctx)
    refuse_finalized_addresses(ctx, addr)
    x1 = F(ctx.k1_binding["right"])
    t0, w0 = time.process_time(), time.time()
    with R1E.precision(ctx.precision_bits):
        from flint import ctx as flint_ctx
        observed_precision = flint_ctx.prec
        stages = run_stages_before_enclosure(backend, ctx)
        enc = enclosure_stages(stages, x1)
        intermediates = serialize_intermediates(stages, enc)
    if observed_precision != PRECISION:
        raise ExecutorRefusal(f"PRECISION_PROBE_MISMATCH: observed {observed_precision}")
    per_m = {}
    for m, v in enc["per_m"].items():
        if x1 == F(p["cell_selection"]["selected"]["x1"]):
            if PR.transport(v["L0"], v["U0"], v["M5"]) != (v["L1"], v["U1"]):
                raise ExecutorRefusal("TRANSPORT_DISAGREES_WITH_FROZEN_RULE")
        per_m[str(m)] = {k: q(val) for k, val in v.items()}
    scientific = {
        "schema": RECORD_SCHEMA,
        "binding": {k: ctx.k1_binding[k] for k in sorted(BINDING_KEYS)},
        "context": {"m_set": list(ctx.m_set), "point_e": ctx.point_e, "theorem_cell": ctx.theorem_cell,
                    "x1": q(x1), "precision_bits": ctx.precision_bits, "observed_precision_bits": observed_precision,
                    "producer_identity_sha256": ctx.producer_identity_sha256, "protocol_sha256": ctx.protocol_sha256,
                    "runtime_identity_sha256": ctx.runtime_identity_sha256,
                    "executor_binding_sha256": ctx.executor_binding_sha256},
        "backend": backend.describe(),
        "guard": guard_decision(),
        "per_m": per_m,
        "addresses": {str(m): a for m, a in addr.items()},
        "intermediates": intermediates,
    }
    check_certificate_chain(scientific)
    record = {"scientific": scientific, "scientific_hash": sha(canonical(scientific)),
              "metadata": {"incidental": True, "cpu_seconds": time.process_time() - t0, "wall_seconds": time.time() - w0,
                           "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}}
    seal(record, Path(ctx.output_dir), REAL_SEAL_NAME if backend.real_input else MANUFACTURED_SEAL_NAME)
    return record


def serialize_intermediates(stages: dict, enc: dict) -> dict:
    c, base = stages["constants"], stages["base"]
    tri = lambda v: [up(v.e), up(v.o), up(v.t)]
    return {
        "constants": {k: (up(v) if hasattr(v, "abs_upper") else v) for k, v in sorted(c.items())},
        "hull_norms": {"k": {str(i): up(base["k"][i]) for i in sorted(base["k"])},
                       "j": {str(i): up(base["j"][i]) for i in sorted(base["j"])},
                       "S0": {str(i): up(base["S0"][i]) for i in sorted(base["S0"])}, "eta": up(base["eta"])},
        "point_nodes": {n: tri(v) for n, v in sorted(enc["out0"]["mid"]["nodes"].items())},
        "point_resolvent_mode": enc["out0"]["mid"]["resolvent"]["mode"],
        "candidate_graded_sups": {n: [up(e), up(o)] for n, (e, o) in sorted(stages["candidates"].items())},
        "local_anchors": {n: tri(v) for n, v in sorted(enc["local"]["anchors"].items())},
        "tower_nodes": {n: tri(v) for n, v in sorted(enc["local"]["towers"].items())},
        "M5_trace_m1": [q(t) for t in enc["local"]["trace_m1"]],
    }


REQUIRED_CONSTANTS = ("C_point", "C_e0", "C_o0", "C_hull")


def check_certificate_chain(s: dict) -> None:
    it = s["intermediates"]
    problems = [k for k in REQUIRED_CONSTANTS if k not in it["constants"]]
    problems += [f"m={m}" for m in M_SET if str(m) not in s["per_m"]
                 or set(s["per_m"][str(m)]) != {"L0", "U0", "M5", "transport_factor", "L1", "U1"}]
    problems += [f"F:{r}:3" for r in range(5) if f"F:{r}:3" not in it["point_nodes"]]
    problems += [f"tower F:{r}:5" for r in range(5) if f"F:{r}:5" not in it["tower_nodes"]]
    if not it["local_anchors"]:
        problems.append("local anchors")
    if set(s["addresses"]) != {str(m) for m in M_SET}:
        problems.append("addresses")
    if problems:
        raise ExecutorRefusal(f"INCOMPLETE_CERTIFICATE_CHAIN: {problems}")


def seal(record: dict, out: Path, name: str) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / (name + ".tmp")
    data = (json.dumps(record, indent=1, sort_keys=True) + "\n").encode()
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    final = out / name
    os.replace(tmp, final)
    return final
