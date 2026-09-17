"""Real point executor core (EXECUTOR_SPEC.md). Computes CERTIFICATES ONLY; never interprets a sign.

    execute(backend, context)              -> sealed record (scientific payload + separate metadata)
    run_stages_before_enclosure(backend, context) -> the shared real-stack stages (prepare, residuals, graded inputs,
                                             candidate graded suprema, hull base) used by execute() and by the
                                             real-stage smoke (which stops here: no enclosure is formed)

Pipeline after those stages (R2/R3/R4 reuse, no new mathematics):
    graded_dag.certify_graded(inputs, parity=True)             -> I0_m = R3_mid (point, degenerate cell {0})
    local_r5.local_tower(base, cands, point nodes, x1)          -> M5_m >= sup_[0,x1] |R_m^(5)|
    transport_factor = x1^2/2 (exact);  L1 = L0 - tf M5;  U1 = U0 + tf M5
REAL_INPUT_ARITHMETIC_GUARD: config/REAL_INPUT_GUARD.json. Policy DENY (frozen) refuses a backend with real_input = True
before any backend method is called; policy EXTERNAL_AUTHORIZATION (not active) permits it only for a bundle accepted by
authorization_interface.validate (EXECUTOR_SPEC_R2.md R2-3). Every attempt appends VALIDATED / ARITHMETIC_STARTED /
SEALED | VOID to ATTEMPT_LOG.jsonl; any failure after ARITHMETIC_STARTED (including SIGXCPU) seals a VOID record.
The sealed record carries the preregistered producer-qualification gates Q01..Q16 with their evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import resource
import signal
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
def guard_decision(bundle=None, ctx=None) -> dict:
    """REAL_INPUT_ARITHMETIC_GUARD read from the guard file (config/REAL_INPUT_GUARD.json, frozen policy DENY)."""
    try:
        policy = json.loads(GUARD_FILE.read_text()).get("policy")
    except (OSError, ValueError, AttributeError):
        return {"policy": None, "real_arithmetic_permitted": False, "reason": "guard file unreadable: DENY"}
    return decide(policy, bundle, ctx)


def decide(policy, bundle, ctx) -> dict:
    """Pure decision. DENY denies always; EXTERNAL_AUTHORIZATION permits only a bundle accepted by
    authorization_interface.validate; any other policy value denies."""
    if policy == "DENY":
        return {"policy": "DENY", "real_arithmetic_permitted": False, "reason": "REAL_INPUT_ARITHMETIC_GUARD = DENY"}
    if policy == "EXTERNAL_AUTHORIZATION":
        import authorization_interface as AI
        ok, problems, auth_sha = AI.validate(bundle, ctx)
        return {"policy": policy, "real_arithmetic_permitted": ok, "authorization_sha256": auth_sha,
                "reason": "external authorization accepted" if ok else f"external authorization refused: {problems[:5]}"}
    return {"policy": policy, "real_arithmetic_permitted": False, "reason": f"unrecognized guard policy {policy!r}: DENY"}


def enforce_guard(backend, ctx=None) -> dict:
    decision = guard_decision(getattr(ctx, "authorization_bundle", None), ctx)
    if getattr(backend, "real_input", True) and not decision["real_arithmetic_permitted"]:
        raise ExecutorRefusal(f"UNAUTHORIZED_REAL_ARITHMETIC: {decision['reason']}")
    return decision


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
    authorization_bundle: dict | None = None
    cpu_soft_seconds: float | None = None


BINDING_KEYS = {"kind", "detector", "k1_cell_index", "left", "right", "C_upper", "C_evaluation", "record_sha256",
                "export_manifest_sha256", "cells_json_sha256", "adapter", "redacted"}
PINS_FILE = NS / "config/EXECUTOR_PINS.json"


def prereg() -> dict:
    return json.loads(SCIENCE_FILE.read_text())


def pinned_hashes() -> dict:
    """sha256 of every file named in config/EXECUTOR_PINS.json (Q05 / Q13)."""
    try:
        pins = json.loads(PINS_FILE.read_text())["files"]
    except (OSError, ValueError, KeyError):
        raise ExecutorRefusal("PINS_UNAVAILABLE: config/EXECUTOR_PINS.json")
    out = {}
    for rel in pins:
        path = paths.REPO / rel
        out[rel] = sha(path.read_bytes()) if path.exists() else None
    return {"pinned": pins, "live": out}


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


SEAL_NAMES = (REAL_SEAL_NAME, MANUFACTURED_SEAL_NAME, "VOID_RECORD_SEALED.json", "MANUFACTURED_VOID_RECORD_SEALED.json")


def refuse_finalized_addresses(ctx: ExecutionContext, addr: dict) -> None:
    root = Path(ctx.output_dir).parent
    wanted = {a["address_sha256"] for a in addr.values()}
    if not root.exists():
        return
    for name in SEAL_NAMES:
        for path in root.rglob(name):
            try:
                rec = json.loads(path.read_text())
                found = {a["address_sha256"] for a in rec["scientific"]["addresses"].values()}
            except (ValueError, KeyError, TypeError):
                raise ExecutorRefusal(f"FINALIZED_ADDRESS_EXISTS: unreadable sealed record {path}")
            if wanted & found:
                raise ExecutorRefusal(f"FINALIZED_ADDRESS_EXISTS: {path}")


# ------------------------------------------------------------------ attempt events
class AttemptLog:
    def __init__(self, out: Path):
        self.out = out
        self.events = []

    def emit(self, event: str, **fields):
        entry = {"event": event, "utc_epoch": time.time(), **fields}
        self.events.append(entry)
        self.out.mkdir(parents=True, exist_ok=True)
        with open(self.out / "ATTEMPT_LOG.jsonl", "a") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())


class _CpuLimit:
    """SIGXCPU (RLIMIT_CPU soft limit set by the supervisor) -> ExecutorRefusal('CPU_RLIMIT') in the main thread."""

    def __enter__(self):
        self.previous = signal.signal(signal.SIGXCPU, self._handler)
        return self

    @staticmethod
    def _handler(signum, frame):
        raise ExecutorRefusal("CPU_RLIMIT: soft CPU limit reached (SIGXCPU)")

    def __exit__(self, *exc):
        signal.signal(signal.SIGXCPU, self.previous)
        return False


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


def radius_only_cascade(inputs: dict, *, parity: bool) -> dict:
    """The graded cascade on inputs WITHOUT origin values: nodes and radii only, no centre, hence no enclosure (Q08)."""
    stripped = {k: v for k, v in inputs.items() if k != "origin"}
    if "origin" in stripped:
        raise ExecutorRefusal("radius-only cascade received origin values")
    out = G.certify_graded(stripped, parity=parity)
    if out["m"]:
        raise ExecutorRefusal("radius-only cascade formed an enclosure")
    return out


# ------------------------------------------------------------------ execute
def execute(backend, ctx: ExecutionContext) -> dict:
    decision = enforce_guard(backend, ctx)                   # FIRST: before any backend method
    p = validate_context(ctx, backend)
    addr = addresses(ctx)
    refuse_finalized_addresses(ctx, addr)
    out = Path(ctx.output_dir)
    log = AttemptLog(out)
    pins_start = pinned_hashes()
    log.emit("VALIDATED", guard_policy=decision["policy"], real_input=bool(backend.real_input))
    x1 = F(ctx.k1_binding["right"])
    t0, w0 = time.process_time(), time.time()
    partial = {}
    try:
        with _CpuLimit(), R1E.precision(ctx.precision_bits):
            from flint import ctx as flint_ctx
            observed_precision = flint_ctx.prec
            log.emit("ARITHMETIC_STARTED")
            stages = run_stages_before_enclosure(backend, ctx)
            enc = enclosure_stages(stages, x1)
            partial["per_m"] = {str(m): {k: q(val) for k, val in v.items()} for m, v in enc["per_m"].items()}
            intermediates = serialize_intermediates(stages, enc)
            partial["intermediates"] = intermediates
            q_extra = backend.producer_gate_evidence(stages, enc, ctx)
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
            "guard": decision,
            "per_m": per_m,
            "addresses": {str(m): a for m, a in addr.items()},
            "intermediates": intermediates,
        }
        check_certificate_chain(scientific)
        cpu, wall = time.process_time() - t0, time.time() - w0
        pq = producer_gates(scientific, q_extra, pins_start, pinned_hashes(), log, p, cpu, wall, decision, backend, ctx)
        scientific["producer_qualification"] = {"gates": pq["gates"], "modes": pq["modes"]}
        record = {"scientific": scientific, "scientific_hash": sha(canonical(scientific)),
                  "metadata": {"incidental": True, "cpu_seconds": cpu, "wall_seconds": wall,
                               "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                               "producer_qualification_evidence": pq["evidence"]}}
        seal(record, out, REAL_SEAL_NAME if backend.real_input else MANUFACTURED_SEAL_NAME)
        log.emit("SEALED", scientific_hash=record["scientific_hash"])
        return record
    except BaseException as exc:
        if any(e["event"] == "ARITHMETIC_STARTED" for e in log.events) and not (out / REAL_SEAL_NAME).exists() \
                and not (out / MANUFACTURED_SEAL_NAME).exists():
            void = {"void": True, "failure": f"{type(exc).__name__}: {str(exc)[:300]}",
                    "scientific": {"schema": RECORD_SCHEMA + "#void", "binding": {k: ctx.k1_binding.get(k) for k in sorted(BINDING_KEYS)},
                                   "addresses": {str(m): a for m, a in addr.items()}, "computed_before_failure": partial}}
            void["scientific_hash"] = sha(canonical(void["scientific"]))
            seal(void, out, "VOID_RECORD_SEALED.json" if backend.real_input else "MANUFACTURED_VOID_RECORD_SEALED.json")
            log.emit("VOID", failure=void["failure"][:120])
        raise


def producer_gates(s: dict, extra: dict, pins_start: dict, pins_seal: dict, log: AttemptLog, p: dict, cpu: float,
                   wall: float, decision: dict, backend, ctx: ExecutionContext) -> dict:
    """Q01..Q16 of the preregistration, evaluated by the executor with their evidence (sign independent).
    Real mode evaluates every gate as preregistered. Manufactured / synthetic mode marks harness analogues with a
    'mode' label; the separate record reader refuses such labels when the binding kind is real."""
    real = bool(backend.real_input)
    vals = {m: {k: F(x) for k, x in v.items()} for m, v in s["per_m"].items()}
    x1 = F(s["context"]["x1"])
    frozen_x1 = x1 == F(p["cell_selection"]["selected"]["x1"])

    def transported(v):                   # the frozen rule at the preregistered x1; the same formula at a fixture's x1
        if frozen_x1:
            return PR.transport(v["L0"], v["U0"], v["M5"], x1)
        return v["L0"] - x1 * x1 / 2 * v["M5"], v["U0"] + x1 * x1 / 2 * v["M5"]

    q07 = (frozen_x1 or not real) and all(
        v["L0"] <= v["U0"] and v["M5"] >= 0 and v["L1"] <= v["L0"] <= v["U0"] <= v["U1"]
        and v["transport_factor"] == x1 * x1 / 2 and (v["L1"], v["U1"]) == transported(v) for v in vals.values())
    it = s["intermediates"]
    tri_ok = all(F(e) <= F(t) and F(o) <= F(t) for table in ("point_nodes", "local_anchors", "tower_nodes")
                 for e, o, t in it[table].values())
    q09 = len(it["M5_trace_m1"]) == 13 and tri_ok and all(int(n.split(":")[-1]) <= 3 for n in it["local_anchors"])
    events = [e["event"] for e in log.events]
    started = next(e["utc_epoch"] for e in log.events if e["event"] == "ARITHMETIC_STARTED")
    pins_ok = pins_start == pins_seal and None not in pins_seal["live"].values() \
        and pins_seal["live"] == pins_seal["pinned"]
    order_ok = events[:2] == ["VALIDATED", "ARITHMETIC_STARTED"] and "VOID" not in events and "SEALED" not in events
    if real:
        bundle = ctx.authorization_bundle or {}
        rep = bundle.get("prelaunch_report") or {}
        auth_sha = decision.get("authorization_sha256")
        q01 = {"pass": decision["policy"] == "EXTERNAL_AUTHORIZATION" and decision["real_arithmetic_permitted"] is True
               and rep.get("verdict") == "LAUNCH_PERMITTED" and rep.get("authorization_sha256") == auth_sha
               and isinstance(rep.get("utc_epoch"), (int, float)) and rep["utc_epoch"] <= started, "mode": "REAL"}
        utc = ((bundle.get("authorization") or {}).get("countersigner") or {}).get("utc")
        q16 = {"pass": order_ok and isinstance(utc, (int, float)) and utc <= started, "mode": "REAL",
               "authorization_utc": utc, "arithmetic_started_utc": started}
        q14 = {"pass": decision["real_arithmetic_permitted"] is True and order_ok, "mode": "REAL"}
    else:
        q01 = {"pass": decision["real_arithmetic_permitted"] is False and decision["policy"] is not None,
               "mode": "HARNESS_ANALOGUE", "note": "guard decision recorded before arithmetic; no prelaunch for non-real input"}
        q16 = {"pass": order_ok, "mode": "HARNESS_ANALOGUE", "note": "event order only"}
        q14 = {"pass": decision["real_arithmetic_permitted"] is False and order_ok, "mode": "HARNESS_ANALOGUE"}
    ceil = p["cpu_ceiling"]
    ev = {"Q01": q01, "Q14": q14, "Q16": q16, **extra,
          "Q05_Q13": {"pass": pins_ok, "pinned_files": len(pins_seal["pinned"])},
          "Q15": {"cpu_seconds": cpu, "wall_seconds": wall}, "events": events}
    gates = {
        "Q01_PRELAUNCH_VERIFIED": q01["pass"] is True,
        "Q02_K1_INPUT_BINDING": extra["Q02"]["pass"] is True,
        "Q03_EXACT_CELL_IDENTITY": extra["Q03"]["pass"] is True,
        "Q04_RUNTIME_AND_AUX5_GATES": extra["Q04"]["pass"] is True,
        "Q05_SOURCE_AND_MANIFEST_HASHES": pins_ok,
        "Q06_CERTIFICATE_REPLAY": extra["Q06"]["pass"] is True,
        "Q07_INTERVAL_CONSISTENCY": q07,
        "Q08_GRADED_SCALAR_CONSISTENCY": extra["Q08"]["pass"] is True,
        "Q09_R5_CERTIFICATE_VALIDITY": q09,
        "Q10_ORDER2_CROSS_REPLAY": extra["Q10"]["pass"] is True,
        "Q11_DETERMINISTIC_SERIALIZATION": canonical(s) == canonical(json.loads(canonical(s))),
        "Q12_SCIENTIFIC_ADDRESS_UNIQUE": len({a["address_sha256"] for a in s["addresses"].values()}) == len(M_SET),
        "Q13_NO_MUTATION": pins_ok,
        "Q14_FAIL_CLOSED": q14["pass"] is True,
        "Q15_COST_CEILING": cpu <= ceil["per_attempt_cpu_seconds_soft"] and wall <= ceil["per_attempt_wall_seconds"],
        "Q16_TEMPORAL_INTEGRITY": q16["pass"] is True,
    }
    modes = {k: v.get("mode") for k, v in ev.items() if isinstance(v, dict) and "mode" in v}
    return {"gates": gates, "modes": modes, "evidence": ev}


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
