"""C2b negative controls (each must be DETECTED) and independent checks, at declared non-target drifts.

  C1 below-truth scaling   w = 0.97 V_h (and w with w(a) = 0.999 x Nystrom-Richardson truth): certify must FAIL.
  C2 local notch           w = certified w with one nodal value lowered by 5% (every node class tried): must FAIL.
  C3 sign-flipped kernel   certify with drift -e; its w' must violate w'(x) >= V_e(x) somewhere (float truth at +e);
                           records that the ATOM value alone cannot detect it (Lambda(e) = Lambda(-e) by p<->m symmetry).
  C4 Hessian FD check      at further drifts, whole and taboo; control: bounds x 0.05 must be flagged.
  C5 C11 kernel check      at further drifts; control: wrong K = 2/5 must mismatch.
Usage: python3 c2b_controls.py <e> <N>
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F

import c2b_common as CM
import c2b_certify as CE
import c2b_checks as CH
import c2b_exact as EX
import c2b_float as FL


def main(e, N):
    e = F(e)
    CM.guard(e)
    CM.guard(-e)
    out = {"e": str(e), "N": N}
    S = EX.Setup(N, e)
    fk = FL.FloatKernel(N, float(e))
    sol = fk.solve_taboo()
    V = sol["V"]
    Qw = CE.Q
    # ---------------- C1
    c1 = {}
    for lab, fac in (("0.97xV_h", 0.97), ("0.999xV_h", 0.999)):
        W = [[int(fac * v * (1 << Qw)) for v in col] for col in V]
        r = EX.certify(S, W, Qw, True)
        c1[lab] = {"certified": r["certified"], "failing_cells": r.get("failing_cells"),
                   "w_atom": r.get("w_atom_float"), "detected": not r["certified"]}
    out["C1_below_truth"] = c1
    # ---------------- reference certificate at +e
    ref = CE.run(N, e, None, "whole", "P1")
    rc = ref["certificate"]
    out["reference"] = {"certified": rc["certified"], "w_atom": rc["w_atom_float"], "alpha": ref["alpha_float"],
                        "beta": ref["beta_float"]}
    g_int = CE._dyadic(V)
    cons = CE.prepare(S, g_int, True)
    Wref, alpha, beta = CE.build_w(g_int, ref["ladder_index"], cons)
    Qref = CE.Q + CE.ALPHA_BITS
    assert EX.certify(S, Wref, Qref, True)["certified"]
    # ---------------- C2: notch one node of each class (atom, p-axis, m-axis, interior, far axes)
    probes = [(0, 0), (N // 2, 0), (0, N // 2), (N, N), (2 * N, N), (N // 2, 3 * N), (9 * N // 2, 0),
              (0, 9 * N // 2), (4 * N, 0), (0, 4 * N)]
    c2 = {}
    for (i, j) in probes:
        W = [col[:] for col in Wref]
        W[i][j] = int(W[i][j] * 0.95)
        r = EX.certify(S, W, Qref, True)
        c2[f"{i},{j}"] = {"certified": r["certified"], "failing_cells": r["failing_cells"],
                          "detected": not r["certified"]}
    out["C2_local_notch"] = c2
    # ---------------- C3: sign-flipped drift
    flip = CE.run(N, -e, None, "whole", "P1")
    Sf = EX.Setup(N, -e)
    gf = CE._dyadic(FL.FloatKernel(N, float(-e)).solve_taboo()["V"])
    consf = CE.prepare(Sf, gf, True)
    Wf, _, _ = CE.build_w(gf, flip["ladder_index"], consf)
    sc = 2.0 ** -Qref
    viol = [(i, j, Wf[i][j] * sc, V[i][j]) for (i, j) in S.mesh.nodes if Wf[i][j] * sc < V[i][j] * (1 - 1e-9)]
    worst = min(viol, key=lambda r: r[2] / r[3]) if viol else None
    out["C3_sign_flipped_kernel"] = {
        "flipped_certificate_certified_for_K_minus_e": flip["certificate"]["certified"],
        "flipped_w_atom": Wf[0][0] * sc, "truth_atom_float_plus_e": sol["Lambda"],
        "atom_only_detects": Wf[0][0] * sc < sol["Lambda"],
        "nodes_scanned": len(S.mesh.nodes), "nodes_where_w_flip_below_truth": len(viol),
        "worst_node": None if worst is None else {"node": worst[:2], "w_flip": worst[2], "V_truth": worst[3],
                                                  "ratio": worst[2] / worst[3]},
        "detected": bool(viol),
    }
    # ---------------- C4, C5
    out["C4_hessian_fd"] = {
        "whole": CH.hessian_fd_check(N, float(e), V, True),
        "taboo": CH.hessian_fd_check(N, float(e), sol["t"], False),
        "control_x0.05_violations": CH.hessian_fd_check(N, float(e), V, True, scale=0.05)["violations"],
    }
    out["C5_c11_kernel"] = {"check": CH.c11_kernel_check(10, e), "control_wrong_K": CH.c11_kernel_check(10, e, Kref=F(2, 5))}
    # ---------------- C6: off-node residual sampling of the certified w (independent float evaluator)
    import random
    import c2b_pointeval as PE
    rnd = random.Random(11)
    pts = []
    while len(pts) < 1500:
        u = rnd.random()
        if u < 0.1:
            pts.append((rnd.uniform(0, 5), 0.0))
        elif u < 0.2:
            pts.append((0.0, rnd.uniform(0, 5)))
        else:
            p, m = rnd.uniform(0, 4), rnd.uniform(0, 4)
            if p + m <= 4:
                pts.append((p, m))
    pts += [(0.0, 0.0), (5.0, 0.0), (0.0, 5.0), (0.49, 0.5), (1e-3, 1e-3)]

    def min_resid(Wfl):
        worst = None
        for (p, m) in pts:
            r = PE.w_at(Wfl, N, p, m) - 1.0 - PE.K_at(Wfl, N, p, m, float(e), True)
            if worst is None or r < worst[0]:
                worst = (r, p, m)
        return worst

    Wq = [[x * sc for x in col] for col in Wref]
    Wbad = [[0.97 * v for v in col] for col in V]
    r_ok, r_bad = min_resid(Wq), min_resid(Wbad)
    out["C6_offnode_sampling"] = {
        "points": len(pts), "certified_w_min_residual": r_ok[0], "at": r_ok[1:],
        "certified_w_all_nonneg": r_ok[0] >= -1e-9,
        "control_0.97V_min_residual": r_bad[0], "control_detected": r_bad[0] < 0,
    }
    CM.Q.log_execution("gen/c2b_controls.py", f"C2B negative controls e={e} N={N}", cells_touched=[],
                       klass="NONTARGET_DRIFT_VALIDATION")
    p = CM.HERE / "results" / f"controls_{str(e).replace('/', '_')}_N{N}.json"
    p.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(p)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
