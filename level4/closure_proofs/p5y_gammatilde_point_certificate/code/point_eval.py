"""Certified point evaluation of R_m'(e) and R_m(e) at ONE exact e, with the frozen K1 CUSUM kernel.

    <frozen venv python> -B code/point_eval.py replay-cell0 --out F      # qualification: reproduce K1 cell 0
    <frozen venv python> -B code/point_eval.py point-e0     --out F      # qualification: degenerate cell at e0
    <frozen venv python> -B code/point_eval.py science --bits B --qualification Q [--prior R ...] --out F

WHAT IS COMPUTED, AND WHAT IS NOT
---------------------------------
Exactly the midpoint path that produced R_interval and D_interval in every K1 CUSUM record
(p5y_k1_cusum_aux3_successor/code/aux_propagate.cell_obligations):

    cert = Order2Certifier(cell, bits).prepare(); cert.all_residuals()      # frozen certifier, unedited
    mid  = aux_propagate.cell_dag(cert, "delta_mid")                         # unrefined midpoint DAG
    enc  = propagate.enclosures(cert, mid, mid)                              # reviewed enclosures at x0
    R    = assembly.assemble(m, enc["F"], enc["W"][0])                       # order 0 at e0
    D    = assembly.assemble(m, enc["D"], enc["W"][1])                       # order 1 at e0

Order2Certifier is the parent of the production Aux3Certifier; Aux3 only ADDS order-3 auxiliary objects, which feed
the whole-cell curvature refinement and never the midpoint enclosures. NOT computed: whole-cell refinement
(refine2), auxiliary order-3 evidence, M_R2, the cover ledger, K5-B recurrences. `all_residuals` is monolithic in
the frozen code, so the order-2 midpoint residuals are also produced; they are never consumed.

For the degenerate cell {e} (left = right = e0 = e, rho = 0) every midpoint residual is certified AT e exactly, the
drift-aware norms are taken over the window of the single point, and C is frozen cell 0's resolvent bound (valid on
[0, 2 e0], evaluated at 0).

GATES (fail closed, before AND after the arithmetic)
----------------------------------------------------
frozen protocol hash; wrapper-file pins; bound-source pins; manifest-v3 verify (every TCB file, science-unchanged,
runtime contract); live identity == frozen K1 identity; loaded repository modules within TCB + pinned wrapper files;
thread contract; SciPy guard clean.
"""
from __future__ import annotations

import os
import sys

_PINNED = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}
if "numpy" in sys.modules:
    raise RuntimeError("numpy imported before the thread contract was pinned")
os.environ.update(_PINNED)
os.environ["K1_THREADS_PINNED"] = "1"

import argparse                                                                   # noqa: E402
import json                                                                       # noqa: E402
import resource                                                                   # noqa: E402
import time                                                                       # noqa: E402
from fractions import Fraction as F                                               # noqa: E402
from pathlib import Path                                                          # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import point_core as PC                                                           # noqa: E402

sys.path.insert(1, str(PC.ROOT / PC.CP / "p5y_k1_cusum_aux5_successor/code"))
import ancestry5                                                                  # noqa: E402,F401

import spec                                                                       # noqa: E402
from intervals import record, workprec                                            # noqa: E402
from repair_check import require_single_charge                                    # noqa: E402
from order2 import Order2Certifier                                                # noqa: E402
import aux_propagate                                                              # noqa: E402
import propagate as reviewed                                                      # noqa: E402
import assembly                                                                   # noqa: E402
import manifest_v3                                                                # noqa: E402
import runtime_identity5                                                          # noqa: E402
import tcb5                                                                       # noqa: E402
import scipy_guard                                                                # noqa: E402

RECORD_CELL0 = PC.ROOT / PC.CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json"


class GateFailure(RuntimeError):
    pass


def gate(protocol: dict, stage: str, guard=None) -> dict:
    problems = []
    problems += PC.wrapper_pin_problems(protocol)
    problems += PC.source_pin_problems(protocol)
    state = manifest_v3.verify()
    problems += [f"manifest: {p}" for p in state["problems"]]
    committed = manifest_v3.load()
    ident = manifest_v3.identity(committed)
    problems += PC.identity_problems(protocol, ident)
    allowed = set(committed["files"]) | set(protocol["wrapper_files"])
    cov = tcb5.verify_coverage(allowed)
    problems += [f"module outside TCB + wrapper pins: {u}" for u in cov["uncovered"]]
    try:
        runtime_identity5.require(committed["runtime"])
    except Exception as exc:                                                       # recorded, then refused
        problems.append(f"runtime: {exc}")
    guard_report = None
    if guard is not None:
        try:
            guard_report = guard.require_clean()
        except Exception as exc:
            problems.append(f"scipy guard: {exc}")
    if problems:
        raise GateFailure(f"[{stage}] " + "; ".join(problems[:10]))
    return {"stage": stage, "producer_identity": {k: ident[k] for k in protocol["producer_identity"]},
            "manifest_file_count": ident["manifest_file_count"], "loaded_repository_modules":
            cov["loaded_repository_modules"], "scipy_guard": guard_report}


def frozen_cell0() -> dict:
    return next(c for c in spec.CELLS if c["detector"] == "CUSUM" and c["index"] == 0)


def evaluate(cell: dict, bits: int, ms) -> dict:
    t0, w0 = time.process_time(), time.time()
    started_epoch = int(w0)
    guard = scipy_guard.ScipyGuard()
    with guard:
        with workprec(bits):
            cert = Order2Certifier(cell, bits=bits).prepare()
            cert.all_residuals()
            require_single_charge(cert, cert.residuals)
            mid = aux_propagate.cell_dag(cert, "delta_mid")
            enc = reviewed.enclosures(cert, mid, mid, None)
            rows = {}
            for m in ms:
                R = assembly.assemble(m, enc["F"], enc["W"][0])
                D = assembly.assemble(m, enc["D"], enc["W"][1])
                rows[str(m)] = {"R_interval": {k: record(R)[k] for k in ("lo", "hi")},
                                "D_interval": {k: record(D)[k] for k in ("lo", "hi")}}
    scientific = {"cell": {k: cell[k] for k in ("detector", "index", "e0", "rho", "left", "right", "C_upper")},
                  "precision_bits": bits, "method": "frozen_K1_CUSUM_midpoint_path_orders_0_1", "m": rows}
    runtime = {"started_epoch": started_epoch, "cpu_seconds": time.process_time() - t0, "wall_seconds": time.time() - w0,
               "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    return {"scientific": scientific, "runtime": runtime, "guard": guard}


def write(path: str, obj: dict) -> None:
    p = Path(path)
    if p.exists():
        raise GateFailure(f"refusing to overwrite {p}")
    p.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("replay-cell0", "point-e0", "science"))
    ap.add_argument("--bits", type=int, default=None)
    ap.add_argument("--qualification", default=None)
    ap.add_argument("--prior", action="append", default=[])
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    protocol = PC.load_protocol()
    ms = PC.require_m_values(protocol, protocol["m_values"]["evaluated"])
    g0 = gate(protocol, "initial")
    c0 = frozen_cell0()

    if a.mode == "replay-cell0":
        bits = protocol["precision_ladder"]["bits"][0]
        cell = c0
    elif a.mode == "point-e0":
        bits = protocol["precision_ladder"]["bits"][0]
        cell = PC.point_cell(c0, F(c0["e0"][0]))
    else:
        q = json.loads(Path(a.qualification).read_text()) if a.qualification else {}
        if q.get("POINT_EVALUATOR_QUALIFICATION") != "PASS" or q.get("protocol_sha256") != \
                PC.PROTOCOL_HASH.read_text().strip():
            raise GateFailure("science refused: no PASS qualification bound to this frozen protocol")
        prior = [json.loads(Path(p).read_text()) for p in a.prior]
        completed = [{"bits": r["scientific"]["precision_bits"], "status": r["target_status"]} for r in prior]
        want = PC.next_rung(protocol, completed)
        if want is None or a.bits != want:
            raise GateFailure(f"science refused: frozen ladder requires {want}, got {a.bits}")
        bits = a.bits
        cell = PC.point_cell(c0, F(protocol["scientific_target"]["e"]))

    ev = evaluate(cell, bits, ms)
    g1 = gate(protocol, "final", guard=ev["guard"])
    out = {"mode": a.mode, "protocol_sha256": PC.PROTOCOL_HASH.read_text().strip(),
           "scientific": ev["scientific"], "scientific_hash": PC.scientific_hash(ev["scientific"]),
           "runtime": ev["runtime"], "gates": [g0, g1]}
    if a.mode == "science":
        out["target_status"] = {str(m): PC.adjudicate(ev["scientific"]["m"][str(m)]["D_interval"]["lo"],
                                                      ev["scientific"]["m"][str(m)]["D_interval"]["hi"])
                                for m in protocol["m_values"]["targets"]}
        out["control_problems"] = PC.control_problems(protocol, ev["scientific"])
    write(a.out, out)
    print(a.mode, "written", a.out, out["scientific_hash"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
