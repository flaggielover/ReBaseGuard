"""Proposition SC-T check on synthetic FSM families (target-free).

Identity (exact):  phi'''(e0) = (I - K) F'''(e0) + 3 K1 (H^ - F'') + 3 K2 (D^ - F') + K3 (F^ - F)   (G^ := 0)
Bound:             ||phi'''(e0)|| <= ||(I-K) F'''|| + 3 k1 ||E_H|| + 3 k2 ||E_D|| + k3 ||E_F||
Reports ||phi'''|| / ||(I-K)F'''|| (-> 1 as the candidates improve) and the surrogate's Leibniz gap
S0 / ||(I-K)F'''||.  Same declared fixture rule as d309_supnorm_fsm.py (generic seeds 1..24).
Comparator control (relabelled, review B1): the identity with the coefficient of K2 set to 2 must differ; it tests
the comparator only.
Writes validation/D309_SCT_FSM.json.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d309_core as D  # noqa: E402
import d309_supnorm_fsm as S  # noqa: E402

Q, X = D.Q, D.X


def main() -> None:
    rows = []
    for seed in range(1, 25):
        n = 4 + seed % 4
        rho = (F(1, 64), F(1, 32), F(1, 16))[seed % 3]
        pert = (F(1, 10 ** 6), F(1, 10 ** 4), F(1, 10 ** 2))[(seed // 3) % 3]
        sdeg = (2, 5)[seed % 2]
        fam, fxs = S.build(seed, n, rho, pert, sdeg)
        e0 = F(1, 8)
        k = [D.k_cell(fam, i, e0 - rho, e0 + rho) for i in range(4)]
        for r, fx in fxs:
            Fd = fx.famr.F_derivs(e0, 3)
            K = fx.K
            EF, ED, EH = (D.vadd((F(1), c), (F(-1), t)) for c, t in ((fx.Fh, Fd[0]), (fx.Dh, Fd[1]), (fx.Hh, Fd[2])))
            IKF3 = D.mv(D.I_minus(K[0]), Fd[3])
            rhs = D.vadd((F(1), IKF3), (F(3), D.mv(K[1], EH)), (F(3), D.mv(K[2], ED)), (F(1), D.mv(K[3], EF)))
            bad = D.vadd((F(1), IKF3), (F(3), D.mv(K[1], EH)), (F(2), D.mv(K[2], ED)), (F(1), D.mv(K[3], EF)))
            phi3 = fx.phi_leibniz(3)
            t = D.vnorm(IKF3)
            bound = t + 3 * k[1] * D.vnorm(EH) + 3 * k[2] * D.vnorm(ED) + k[3] * D.vnorm(EF)
            sH, sD, sF = D.vnorm(fx.Hh), D.vnorm(fx.Dh), D.vnorm(fx.Fh)
            S0 = 3 * k[1] * sH + 3 * k[2] * sD + k[3] * sF + D.vnorm(fx.S[3])
            rows.append({"seed": seed, "r": r, "pert": str(pert), "identity": phi3 == rhs, "comparator_control_differs": phi3 != bad,
                         "bound_ok": D.vnorm(phi3) <= bound,
                         "true_over_IKF3": float(D.vnorm(phi3) / t), "S0_over_IKF3": float(S0 / t)})
    by = {}
    for p in sorted({r["pert"] for r in rows}):
        sel = [r for r in rows if r["pert"] == p]
        by[p] = {"true_over_IKF3": [min(r["true_over_IKF3"] for r in sel), max(r["true_over_IKF3"] for r in sel)],
                 "S0_over_IKF3": [min(r["S0_over_IKF3"] for r in sel), max(r["S0_over_IKF3"] for r in sel)]}
    out = {"schema": "OV_D309_SCT_FSM/1", "rows": rows,
           "summary": {"cases": len(rows), "identity_all": all(r["identity"] for r in rows),
                       "bound_all": all(r["bound_ok"] for r in rows),
                       "comparator_control_differs": sum(r["comparator_control_differs"] for r in rows), "by_pert": by}}
    (D.NS / "validation" / "D309_SCT_FSM.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    Q.log_execution("streams/D_309/code/d309_sct.py", "Proposition SC-T identity and bound on synthetic FSM",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
