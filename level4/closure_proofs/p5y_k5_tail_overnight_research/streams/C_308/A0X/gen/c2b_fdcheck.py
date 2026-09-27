"""C2b corrected Hessian-bound FD check (r1 sampler: inside the cell) at all declared drifts; writes
results/fdcheck_r1.json.  Controls: bounds x 0.05 (declared, must be flagged) and x 0.98 (sensitivity probe)."""
from __future__ import annotations

import json
from fractions import Fraction as F

import c2b_common as CM
import c2b_checks as CH
import c2b_float as FL

out = []
for e in (F(0), F(1, 4), F(1, 2), F(1), F(3)):
    CM.guard(e)
    for N in (10, 20):
        sol = FL.FloatKernel(N, float(e)).solve_taboo()
        for kind, W, full in (("whole", sol["V"], True), ("taboo", sol["t"], False)):
            r = CH.hessian_fd_check_cell(N, float(e), W, full, n_cells=120)
            r["kind"] = kind
            r["control_x0.05_violations"] = CH.hessian_fd_check_cell(N, float(e), W, full, n_cells=120,
                                                                      scale=0.05)["violations"]
            r["probe_x0.98_violations"] = CH.hessian_fd_check_cell(N, float(e), W, full, n_cells=120,
                                                                    scale=0.98)["violations"]
            out.append(r)
            print(e, N, kind, r["max_ratio_fd_over_bound"], r["violations"], r["control_x0.05_violations"],
                  r["probe_x0.98_violations"], flush=True)
CM.Q.log_execution("gen/c2b_fdcheck.py", "C2B corrected Hessian FD check (in-cell sampler)", cells_touched=[],
                   klass="NONTARGET_DRIFT_VALIDATION")
(CM.HERE / "results" / "fdcheck_r1.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
