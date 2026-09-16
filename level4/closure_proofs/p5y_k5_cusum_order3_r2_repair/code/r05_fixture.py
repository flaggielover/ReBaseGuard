"""R2-A: predeclared manufactured fixture isolating the r = 0 CLOSED-FORM source edge of the rung-3 residual.

Distinguishes the correct residual (r = 0 subtracts the exact closed form Sclosed_3) from R1 mutation R05 (r = 0
subtracts the candidate S_0'''). Design only, informed by the post-R1 diagnostic; no diagnostic output is reused.

Construction (on the R1 manufactured backend, R1 code unchanged):
    base system  controlled_K3 scalar chain centred at e0 (K_1(e0) = K_2(e0) = 0)
    candidates   exact truth, except S_0''' candidate := S_0'''(e0) + offset
    new rung     G_0 re-solved EXACTLY from the offset candidate:  (I - K_0) G_0 = K_3 F + 3 K_2 D + 3 K_1 H + S_0'''_cand
    consequence  the true G_0 error is C * offset, reachable ONLY through the r = 0 source term. The correct producer
                 charges it in its residual (closed form), the R05 mutant sees a zero residual and a zero source
                 allowance, so its bound misses the error.

Ablations (fixture self-mutation tests, predeclared):
    ABL_ZERO_OFFSET        offset = 0                         -> nothing to detect: R05 mutant must show 0 violations
    ABL_RESOLVE_CLOSED     G_0 re-solved from the closed form  -> the error path is gone: R05 mutant 0 violations

Frozen invariants: unmutated producer 0 violations on the fixture and both ablations; R05 mutant > 0 violations on
the fixture; R05 mutant 0 violations on both ablations.
"""
from __future__ import annotations

import sys
from fractions import Fraction as Fr
from math import factorial
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R1_CODE = NS.parents[0] / "p5y_k5_cusum_order3_real_producer/code"
if str(R1_CODE) not in sys.path:
    sys.path.append(str(R1_CODE))

import fixtures as R1F  # noqa: E402
import manufactured_chain as MC  # noqa: E402


def build_rig(spec: dict, *, ablation: str | None = None):
    base = {"kind": spec["base_kind"], "e0": spec["e0"], "rho": spec["rho"], "noise": "0"}
    sysm, e0, rho, _seed, _noise = R1F.build(base)
    offset = Fr(0) if ablation == "ABL_ZERO_OFFSET" else Fr(spec["source_offset"])
    rig = MC.Rigorous(sysm, e0, rho, seed=0, noise=Fr(0))
    ex = rig.ex
    D = MC.ChainSystem.deriv
    n = sysm.n
    rig.P["S", 0, 3] = [x + offset for x in rig.P["S", 0, 3]]
    rig.P["W", (0, 0), 3] = rig.P["S", 0, 3]
    for key in (("S", 0, 3), ("W", (0, 0), 3)):
        rig.sup[key] = MC.vnorm(rig.P[key])
    rig.mid["S:0:3"] = MC.vnorm(MC.vsub(rig.P["S", 0, 3], D(ex["S"][0], 3)))
    rig.mid["W:0:0:3"] = rig.mid["S:0:3"]
    Kd = [MC.mscale(factorial(i), ex["K"][i]) if i < len(ex["K"]) else MC.zeros_m(n) for i in range(4)]
    I_K0 = [[(Fr(1) if a == b else Fr(0)) - Kd[0][a][b] for b in range(n)] for a in range(n)]
    src = D(ex["S"][0], 3) if ablation == "ABL_RESOLVE_CLOSED" else rig.P["S", 0, 3]
    rhs = MC.vadd(MC.vadd(MC.matvec(Kd[3], rig.P["F", 0, 0]), MC.vscale(3, MC.matvec(Kd[2], rig.P["D", 0, 0]))),
                  MC.vadd(MC.vscale(3, MC.matvec(Kd[1], rig.P["H", 0, 0])), src))
    rig.P["G", 0, 0] = MC.solve(I_K0, rhs)
    rig.sup["G", 0, 0] = MC.vnorm(rig.P["G", 0, 0])
    return sysm, e0, rho, rig
