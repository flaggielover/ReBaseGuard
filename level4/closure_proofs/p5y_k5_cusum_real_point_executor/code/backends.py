"""Point backends of the real point executor (EXECUTOR_SPEC.md section 2).

CusumPointBackend            PRODUCTION, real_input = True. Refused by REAL_INPUT_ARITHMETIC_GUARD (DENY) in
                             executor_core.execute before any method runs, and again inside prepare_point.
SyntheticCusumSmokeBackend   QUALIFICATION of the real Arb stages: R3 SyntheticGradedCert (real kernels, synthetic
                             parity-pure candidates, no collocation) at the degenerate cell {0}; shares every method
                             after prepare_point with the production backend. Used ONLY by smoke.py, which stops before
                             any enclosure is formed.
ManufacturedPointBackend     QUALIFICATION with exact truth: R2 sigma-system GradedRig at e0 = 0, rho = 0.
"""
from __future__ import annotations

import hashlib
import json
import os
from fractions import Fraction as F
from math import comb  # noqa: F401

import paths  # noqa: F401

import executor_core as EC  # noqa: E402
import rung3_engine as R1E  # noqa: E402

FAM = ("F", "D", "H", "G")


def node_for_key(key):
    """frozen candidate key -> graded node name (orders <= 3), or None."""
    if not isinstance(key, tuple) or len(key) != 3:
        return None
    head, a, n = key
    if head in FAM and n == 0:
        return f"F:{a}:{FAM.index(head)}"
    if head in ("h", "S") and isinstance(a, int) and isinstance(n, int) and n <= 3:
        return f"{head}:{a}:{n}"
    if head == "W" and isinstance(a, tuple) and isinstance(n, int) and n <= 3:
        return f"W:{a[0]}:{a[1]}:{n}"
    return None


# ------------------------------------------------------------------ manufactured
class ManufacturedPointBackend:
    real_input = False
    real_operator = False

    def __init__(self, spec: dict):
        self.spec = dict(spec)

    def describe(self) -> dict:
        return {"backend": "ManufacturedPointBackend", "fixture": self.spec.get("id"),
                "spec_sha256": hashlib.sha256(json.dumps(self.spec, sort_keys=True).encode()).hexdigest()}

    def prepare_point(self, ctx) -> dict:
        import sigma_systems as SS
        x1 = F(self.spec["x1"])
        if x1 != F(ctx.k1_binding["right"]):
            raise EC.ExecutorRefusal("CELL_ENDPOINT_MISMATCH: fixture x1 differs from the binding")
        sysm = SS.build(self.spec)
        noise, seed = F(self.spec.get("noise", "0")), int(self.spec["seed"])
        gr0 = SS.GradedRig(sysm, F(0), F(0), seed=seed, noise=noise)
        grH = SS.GradedRig(sysm, x1 / 2, x1 / 2, seed=seed, noise=noise)
        return {"sysm": sysm, "gr0": gr0, "grH": grH, "x1": x1}

    def constants(self, state) -> dict:
        ex = R1E.exact
        gr0, grH = state["gr0"], state["grH"]
        return {"C_point": ex(gr0.C), "C_hull": ex(grH.C), "C_e0": ex(grH.C_e0), "C_o0": ex(grH.C_o0),
                "source": "manufactured: exact sigma-block resolvent norms of the system"}

    def point_graded_inputs(self, state, constants) -> dict:
        return state["gr0"].engine_inputs()

    def candidate_graded_sups(self, state) -> dict:
        import sigma_systems as SS
        ex = R1E.exact
        out = {}
        for key, vec in state["gr0"].P.items():
            node = node_for_key(key)
            if node is not None:
                ge, go, _ = SS.gnorm(vec)
                out[node] = (ex(ge), ex(go))
        return out

    def hull_tower_base(self, state, constants) -> dict:
        import manufactured_chain as MC
        ex = R1E.exact
        grH, x1 = state["grH"], state["x1"]
        hk = [MC.sup_deriv_poly(grH.rig.ex["K"], i, x1 / 2, mat=True) for i in range(7)]
        hj = [MC.sup_deriv_poly(grH.rig.ex["J"], i, x1 / 2, mat=True) for i in range(7)]
        return {"C": constants["C_hull"], "C_e0": constants["C_e0"], "C_o0": constants["C_o0"],
                "k": {i: ex(hk[i]) for i in range(7)}, "j": {i: ex(hj[i]) for i in range(7)}, "eta": ex(x1),
                "S0": {n: ex(grH.rig.T["S", 0, n]) for n in range(7)},
                "h1": {n: ex(grH.rig.T["h", 1, n]) for n in range(7)}}


# ------------------------------------------------------------------ real CUSUM stack (shared methods)
class _CusumStack:
    real_operator = True

    def __init__(self, binding: dict):
        self.binding = dict(binding)

    def point_cell(self) -> dict:
        import k1_inputs
        import point_core
        return point_core.point_cell(k1_inputs.frozen_cell(0), F(0))

    def constants(self, state) -> dict:
        import constants_r4 as K4
        c = K4.load_certificates()
        ex = R1E.exact
        C = ex(F(state["cell"]["C_upper"]))
        return {"C_point": C, "C_hull": C, "C_e0": ex(c["C_e0"]), "C_o0": ex(c["C_o0"]),
                "certificate_registry_sha256": hashlib.sha256(K4.CERT_REGISTRY.read_bytes()).hexdigest(),
                "source": "C_upper of frozen CUSUM cell 0; C_o0 (R4 odd block), C_e0 (R3) from constants_r4"}

    def point_graded_inputs(self, state, constants) -> dict:
        import graded_real as GR
        import constants_r4 as K4
        c = K4.load_certificates()
        cert = state["cert"]
        inputs = GR.graded_inputs(cert, state["residuals"], left=F(0), right=F(0),
                                  certificates={"C_o0": c["C_o0"], "C_e0": c["C_e0"]})
        inputs["origin"] = ({("G", r): cert.origin(("G", r, 0)) for r in range(5)}
                            | {("W", (r, j)): cert.origin(("W", (r, j), 3)) for r in range(4) for j in range(4 - r)})
        return inputs

    def candidate_graded_sups(self, state) -> dict:
        import graded_real as GR
        cert, out = state["cert"], {}
        for key in list(cert.P):
            node = node_for_key(key)
            if node is not None:
                v = GR.graded_sup(cert, key)
                out[node] = (v.e, v.o)
        return out

    def hull_tower_base(self, state, constants) -> dict:
        import hermite6_ext as H6
        ex = R1E.exact
        x1 = F(self.binding["right"])
        t = H6.norm_table(F(0), x1)
        return {"C": constants["C_hull"], "C_e0": constants["C_e0"], "C_o0": constants["C_o0"], "k": t["k"], "j": t["j"],
                "eta": ex(x1), "S0": {n: H6.sup_S0_on(n, F(0), x1) for n in range(7)}}


class CusumPointBackend(_CusumStack):
    """PRODUCTION. Never runs in this successor: REAL_INPUT_ARITHMETIC_GUARD = DENY."""
    real_input = True

    def describe(self) -> dict:
        return {"backend": "CusumPointBackend", "cell": "degenerate {0} of frozen CUSUM cell 0"}

    def prepare_point(self, ctx) -> dict:
        EC.enforce_guard(self)                                   # defense in depth: DENY refuses here
        if os.environ.get("K1_THREADS_PINNED") != "1":
            raise EC.ExecutorRefusal("thread environment was not pinned before numpy import")
        import graded_real as GR
        import manifest_v3
        manifest_v3.initial_gate()
        cell = self.point_cell()
        cert = GR.GradedRealCertifier(cell, bits=EC.PRECISION).prepare()
        residuals = GR.all_residuals_for_graded(cert)
        return {"cell": cell, "cert": cert, "residuals": residuals}


class SyntheticCusumSmokeBackend(_CusumStack):
    """QUALIFICATION of the real Arb stages with synthetic candidates at the degenerate cell {0}."""
    real_input = False

    def __init__(self, binding: dict, seed: int):
        super().__init__(binding)
        self.seed = int(seed)

    def describe(self) -> dict:
        return {"backend": "SyntheticCusumSmokeBackend", "seed": self.seed, "cell": "degenerate {0}, synthetic candidates"}

    def prepare_point(self, ctx) -> dict:
        import graded_real as GR
        import synthetic_real as SR
        cell = self.point_cell()
        cert = SR.SyntheticGradedCert(dict(cell), bits=EC.PRECISION).prepare_synthetic(self.seed)
        residuals = GR.all_residuals_for_graded(cert)
        return {"cell": cell, "cert": cert, "residuals": residuals}
