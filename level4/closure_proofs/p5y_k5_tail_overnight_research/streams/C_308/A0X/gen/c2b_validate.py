"""C2b validation runner (non-target drifts only).  One task per invocation, one JSON per task in gen/results/.

  python3 c2b_validate.py point  <e> <N> <whole|taboo> [P1|F0_affine_m]
  python3 c2b_validate.py block  <e_lo> <e_hi> <N> <whole|taboo>
  python3 c2b_validate.py truth  <e> <N1,N2,...>
  python3 c2b_validate.py controls <e> <N>

Validation set declared by rule BEFORE any run (PROGRESS.md step 8): drifts {0, 1/4, 1/2, 1, 3}; blocks
[e0, e0 + W] for e0 in {1/2, 1, 3}, W in {1/40, 1/20, 1/10}.  Every entry point calls the quarantine drift guard.
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F

import c2b_common as CM
import c2b_certify as CE
import c2b_float as FL

RES = CM.HERE / "results"


def _save(name, obj):
    RES.mkdir(exist_ok=True)
    p = RES / (name + ".json")
    p.write_text(json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n")
    return p


def _tag(x):
    return str(F(x)).replace("/", "_")


def task_point(e, N, kind, family="P1"):
    CM.guard(e)
    r = CE.run(int(N), F(e), None, kind, family)
    CM.Q.log_execution("gen/c2b_validate.py", f"C2B point certificate e={e} N={N} {kind} {family}",
                       cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION")
    return _save(f"point_{_tag(e)}_N{N}_{kind}_{family}", r)


def task_block(e_lo, e_hi, N, kind):
    CM.guard(e_lo, e_hi)
    r = CE.run(int(N), F(e_lo), F(e_hi), kind, "P1")
    CM.Q.log_execution("gen/c2b_validate.py", f"C2B block certificate [{e_lo},{e_hi}] N={N} {kind}",
                       cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION")
    return _save(f"block_{_tag(e_lo)}_{_tag(e_hi)}_N{N}_{kind}", r)


def task_truth(e, Ns):
    CM.guard(e)
    t0 = time.process_time()
    out, _rows = FL.truth(F(e), tuple(int(n) for n in Ns.split(",")))
    out["label"] = "NON-CERTIFIED float Nystrom + Richardson (O(h^2) assumed); convergence = spread of successive extrapolants"
    out["cpu_seconds"] = time.process_time() - t0
    CM.Q.log_execution("gen/c2b_validate.py", f"C2B float truth e={e} N={Ns}", cells_touched=[],
                       klass="NONTARGET_DRIFT_VALIDATION")
    return _save(f"truth_{_tag(e)}_N{Ns.replace(',', '-')}", out)


def task_truthgrid(e0, wmax, k, Ns="20,40"):
    """NON-CERTIFIED sup over a block: Nystrom + Richardson Lambda at e0 + r*wmax/k, r = 0..k."""
    e0, wmax, k = F(e0), F(wmax), int(k)
    CM.guard(e0, e0 + wmax)
    t0 = time.process_time()
    pts = []
    for r in range(k + 1):
        e = e0 + r * wmax / k
        out, _ = FL.truth(e, tuple(int(n) for n in Ns.split(",")))
        pts.append({"e": str(e), "Lambda_richardson": out["Lambda_richardson"][-1],
                    "Lambda_meshes": [m["Lambda"] for m in out["meshes"]]})
    res = {"e0": str(e0), "wmax": str(wmax), "points": pts, "cpu_seconds": time.process_time() - t0,
           "label": "NON-CERTIFIED"}
    CM.Q.log_execution("gen/c2b_validate.py", f"C2B float truth grid [{e0},{e0 + wmax}]", cells_touched=[],
                       klass="NONTARGET_DRIFT_VALIDATION")
    return _save(f"truthgrid_{_tag(e0)}_{_tag(wmax)}", res)


def task_robust(e0, w, N):
    """NON-CERTIFIED robust ARL W*(a) on the lattice drift grid of [e0, e0 + w] at mesh N (A0 floor diagnostic)."""
    e0, w, N = F(e0), F(w), int(N)
    CM.guard(e0, e0 + w)
    J = w * N
    assert J.denominator == 1
    grid = [e0 + F(r, N) for r in range(int(J) + 1)]
    t0 = time.process_time()
    r = FL.robust(N, grid)
    r.update({"e0": str(e0), "w": str(w), "N": N, "grid": [str(x) for x in grid],
              "cpu_seconds": time.process_time() - t0, "label": "NON-CERTIFIED"})
    CM.Q.log_execution("gen/c2b_validate.py", f"C2B robust ARL [{e0},{e0 + w}] N={N}", cells_touched=[],
                       klass="NONTARGET_DRIFT_VALIDATION")
    return _save(f"robust_{_tag(e0)}_{_tag(w)}_N{N}", r)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "robust":
        print(task_robust(a[1], a[2], a[3]))
    elif a[0] == "truthgrid":
        print(task_truthgrid(a[1], a[2], a[3]))
    elif a[0] == "point":
        print(task_point(a[1], a[2], a[3], a[4] if len(a) > 4 else "P1"))
    elif a[0] == "block":
        print(task_block(a[1], a[2], a[3], a[4]))
    elif a[0] == "truth":
        print(task_truth(a[1], a[2]))
    else:
        raise SystemExit("unknown task")
