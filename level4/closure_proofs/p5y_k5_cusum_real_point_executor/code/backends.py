"""Point backends of the real point executor (EXECUTOR_SPEC.md section 2).

CusumPointBackend            PRODUCTION, real_input = True. Refused by REAL_INPUT_ARITHMETIC_GUARD (DENY) in
                             executor_core.execute before any method runs, and again inside prepare_point.
SyntheticCusumSmokeBackend   QUALIFICATION of the real Arb stages: R3 SyntheticGradedCert (real kernels, synthetic
                             parity-pure candidates, no collocation) at the degenerate cell {0}; shares every method
                             after prepare_point with the production backend. Used ONLY by smoke.py, which stops before
                             any enclosure is formed.
ManufacturedPointBackend     QUALIFICATION with exact truth: R2 sigma-system GradedRig at e0 = 0, rho = 0.

r2 (EXECUTOR_SPEC_R2.md): every backend returns the evidence of the preregistered producer-qualification gates it owns
(Q02, Q03, Q04, Q06, Q08, Q10) from producer_gate_evidence(stages, enc, ctx), called by executor_core.execute after the
enclosure stages and before the seal. The real-stack methods (Aux5 production gate, certificate replay, graded/scalar
consistency, order-2 cross replay) live on _CusumStack so that the smoke exercises the same code as production.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from fractions import Fraction as F
from math import comb  # noqa: F401

import paths  # noqa: F401

import executor_core as EC  # noqa: E402
import rung3_engine as R1E  # noqa: E402

# ------------------------------------------------------------------ CRAMER compatibility contract (r2 repair)
# The frozen ra_certifier builds CRAMER = arb(1086) / arb(1000) at IMPORT time, so its ball (and every Taylor remainder,
# allowance and certificate endpoint downstream) depends on the precision at which the module is first imported. The
# C_o0 / C_e0 artifacts and the K1 records were generated with it first imported at python-flint's default 53-bit
# context. That construction is an inherited compatibility contract: the certificate stack is initialised here under
# an explicit 53-bit context, and require/check_cramer_contract refuses any other construction (fail closed).
CRAMER_CONTRACT = {"schema": "rebaseguard.p5y.k5.cusum-real-point-executor.cramer-contract.v1",
                   "module": "ra_certifier", "symbol": "CRAMER", "expression": "arb(1086) / arb(1000)",
                   "construction_precision_bits": 53,
                   "mid": "2445454597662179/2251799813685248", "rad": "1/4503599627370496",
                   "inherited_from": "import context of the frozen C_o0 (R4) / C_e0 (R3) artifact generation and the K1 records"}
CRAMER_CONTRACT_SHA256 = hashlib.sha256(json.dumps(CRAMER_CONTRACT, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _init_certificate_stack() -> None:
    from flint import ctx as flint_ctx
    with flint_ctx.workprec(CRAMER_CONTRACT["construction_precision_bits"]):
        import odd_block_certificate  # noqa: F401  (imports ra_certifier through the Aux5 ancestry)
        import resolvent_certificate  # noqa: F401
        import ra_certifier  # noqa: F401


_init_certificate_stack()


def _ball(x) -> dict:
    m, r = x.mid().fmpq(), x.rad().fmpq()
    return {"mid": f"{int(m.p)}/{int(m.q)}", "rad": f"{int(r.p)}/{int(r.q)}"}


def check_cramer_contract() -> dict:
    """Shared fail-closed check: ra_certifier.CRAMER equals arb(1086)/arb(1000) rebuilt under explicit 53-bit
    precision, midpoint AND radius, and equals the recorded contract ball."""
    import ra_certifier
    from flint import arb, ctx as flint_ctx
    with flint_ctx.workprec(CRAMER_CONTRACT["construction_precision_bits"]):
        reference = _ball(arb(1086) / arb(1000))
    used = _ball(ra_certifier.CRAMER)
    contract = {"mid": CRAMER_CONTRACT["mid"], "rad": CRAMER_CONTRACT["rad"]}
    ok = used == reference == contract
    return {"pass": ok, "contract_sha256": CRAMER_CONTRACT_SHA256, "used": used, "reference_53": reference,
            "contract": contract, "ra_certifier_file": ra_certifier.__file__}

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

    def producer_gate_evidence(self, stages, enc, ctx) -> dict:
        import input_adapters as IA
        import prelaunch_verify as PV
        x1 = F(self.spec["x1"])
        fresh = self.constants(self.prepare_point(ctx))
        same = all(fresh[k] == stages["constants"][k] if isinstance(fresh[k], str)
                   else R1E.fraction_of(fresh[k].abs_upper()) == R1E.fraction_of(stages["constants"][k].abs_upper())
                   for k in fresh)
        diff = EC.runtime_differences(EC.prereg()["host_runtime_contract"], PV.live_host_facts())
        return {"Q02": {"pass": IA.ManufacturedInputAdapter().bind(self.spec) == ctx.k1_binding, "mode": "MANUFACTURED"},
                "Q03": {"pass": x1 == F(ctx.k1_binding["right"]) and R1E.fraction_of(stages["inputs"]["eta_mid"].abs_upper()) == 0,
                        "mode": "MANUFACTURED"},
                "Q04": {"pass": not diff, "mode": "HARNESS_ANALOGUE", "host_runtime_differences": diff},
                "Q06": {"pass": same, "mode": "MANUFACTURED", "note": "system constants rebuilt from the fixture spec"},
                "Q08": graded_not_looser(stages["inputs"], mode="MANUFACTURED"),
                "Q10": {"pass": True, "mode": "NOT_APPLICABLE_MANUFACTURED"}}


# ------------------------------------------------------------------ gate helpers
RUNG_256 = EC.paths.POINT_NS / "result/RUNG_256.json"
R4_CERT_REGISTRY_REL = "level4/closure_proofs/p5y_k5_cusum_order3_r4_tightening/config/OPERATOR_CERTIFICATES_R4.json"


def graded_not_looser(inputs, *, mode) -> dict:
    """Q08 radius part: graded point radius <= scalar point radius per m, on the origin-free cascade."""
    g = EC.radius_only_cascade(inputs, parity=True)
    sc = EC.radius_only_cascade(inputs, parity=False)
    looser = [m for m in EC.M_SET if not (g["rad_mid"][m].upper() <= sc["rad_mid"][m].upper())]
    return {"pass": not looser, "mode": mode, "graded_looser_m": looser}


def order2_rows(cert) -> dict:
    """The frozen order-2 midpoint path of 84aaa6a5 (point_eval.evaluate) on the given certifier: R(0) and R'(0)."""
    import aux_propagate
    import assembly
    import propagate as reviewed
    from intervals import record
    mid = aux_propagate.cell_dag(cert, "delta_mid")
    enc = reviewed.enclosures(cert, mid, mid, None)
    rows = {}
    for m in EC.M_SET:
        R = record(assembly.assemble(m, enc["F"], enc["W"][0]))
        D = record(assembly.assemble(m, enc["D"], enc["W"][1]))
        rows[str(m)] = {"R_interval": {"lo": R["lo"], "hi": R["hi"]}, "D_interval": {"lo": D["lo"], "hi": D["hi"]}}
    return rows


def order2_compare(rows: dict) -> dict:
    """Q10: every R and R' enclosure intersects the committed RUNG_256 enclosure (84aaa6a5)."""
    ref = json.loads(RUNG_256.read_text())["scientific"]["m"]
    bad = []
    for m in EC.M_SET:
        for name in ("R_interval", "D_interval"):
            a, b = rows[str(m)][name], ref[str(m)][name]
            if not (F(a["lo"]) <= F(a["hi"]) and F(a["lo"]) <= F(b["hi"]) and F(b["lo"]) <= F(a["hi"])):
                bad.append(f"m={m} {name}")
    identical = all(rows[str(m)][n] == ref[str(m)][n] for m in EC.M_SET for n in ("R_interval", "D_interval"))
    return {"pass": not bad, "disjoint": bad, "identical_to_reference": identical,
            "reference_sha256": hashlib.sha256(RUNG_256.read_bytes()).hexdigest()}


def scipy_guard_module():
    """The Aux4 ScipyGuard, imported through the Aux5 ancestry exactly as the 84aaa6a5 point_eval does."""
    import ancestry5  # noqa: F401
    import scipy_guard
    return scipy_guard


def production_gate(stage: str, guard=None) -> dict:
    """Aux5 production gate in the 84aaa6a5 point_eval pattern: manifest_v3.verify, producer identity 3692d0fe,
    TCB coverage over the committed Aux5 files and the executor pins, runtime_identity5.require, ScipyGuard clean."""
    import manifest_v3
    import runtime_identity5
    import tcb5
    problems = []
    contract = check_cramer_contract()
    if not contract["pass"]:
        problems.append(f"CRAMER_CONTRACT_VIOLATED: used {contract['used']} != 53-bit reference {contract['reference_53']}")
    state = manifest_v3.verify()
    problems += [f"manifest: {x}" for x in state["problems"]]
    committed = manifest_v3.load()
    ident = manifest_v3.identity(committed)
    want = EC.prereg()["producer_identity"]["aux5_producer_identity"]
    if not ident["producer_identity_hash"].startswith(want):
        problems.append(f"producer identity {ident['producer_identity_hash'][:8]} != {want}")
    pins = json.loads(EC.PINS_FILE.read_text())["files"]
    cov = tcb5.verify_coverage(set(committed["files"]) | set(pins))
    problems += [f"module outside TCB + executor pins: {u}" for u in cov["uncovered"]]
    try:
        runtime_identity5.require(committed["runtime"])
    except Exception as exc:
        problems.append(f"runtime: {exc}")
    scipy = None
    if guard is not None:
        try:
            scipy = guard.require_clean()["scipy_free"]
        except Exception as exc:
            problems.append(f"scipy guard: {exc}")
    return {"stage": stage, "pass": not problems, "problems": problems[:10],
            "producer_identity_hash": ident["producer_identity_hash"], "scipy_free": scipy,
            "cramer_contract_sha256": contract["contract_sha256"], "cramer_contract_pass": contract["pass"]}


ARTIFACT_AMBIENT_BITS = 53


def certificate_replay() -> dict:
    """Q06: C_o0 (R4 odd block) and C_e0 (R3) artifacts replay exactly; the registry and loader agree. Refused (no
    verifier call) unless the CRAMER compatibility contract holds."""
    contract = check_cramer_contract()
    if not contract["pass"]:
        return {"pass": False, "refused": "CRAMER_CONTRACT_VIOLATED", "cramer_contract": contract, "checks": {}}
    import constants_r4 as K4
    import odd_block_certificate as OB
    import resolvent_certificate as RC
    from flint import ctx as flint_ctx
    reg = json.loads(K4.CERT_REGISTRY.read_text())
    loaded = K4.load_certificates()
    out, evidence = {}, {}
    for entry in reg["certificates"]:
        path = EC.paths.REPO / entry["artifact"]
        art = json.loads(path.read_text())
        # The verifiers export endpoints with arb.upper() at the AMBIENT precision; the artifacts were produced and
        # qualified (R3 / R4) at python-flint's default 53-bit context, so the replay runs in that context too.
        with flint_ctx.workprec(ARTIFACT_AMBIENT_BITS):
            v = (OB if entry["name"] == "C_o0" else RC).verify_artifact(art)
        identical = v["recomputed"] == art["certified"]
        if not identical:
            evidence[entry["name"]] = {"stored": art["certified"], "recomputed": v["recomputed"],
                                       "difference_recomputed_minus_stored": {
                                           k: str(F(v["recomputed"][k]) - F(art["certified"][k])) for k in art["certified"]}}
        out[entry["name"]] = {"certified": bool(v["certified"]), "identical": identical,
                              "artifact_sha256_matches": hashlib.sha256(path.read_bytes()).hexdigest() == entry["artifact_sha256"],
                              "loader_value_matches": loaded[entry["name"]] == F(entry["value_upper"])
                              == F(art["certified"]["C_upper_bound"])}
    after = check_cramer_contract()
    ok = set(out) == {"C_o0", "C_e0"} and all(all(r.values()) for r in out.values()) and after["pass"]
    return {"pass": ok, "checks": out, "cramer_contract": after, "mismatch_evidence": evidence}


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

    def scalar_consistency(self, state, inputs, mode) -> dict:
        """Q08 on the real stack: scalar mode of the ORIGIN-FREE graded cascade equals the frozen midpoint DAG
        (R3 C1 rule, relative 2^-200), and graded radius <= scalar radius per m. No centre, no enclosure."""
        import synthetic_real as SR
        cert = state["cert"]
        saved = (cert.residuals, getattr(cert, "aux", None))
        stripped = {k: v for k, v in inputs.items() if k != "origin"}
        try:
            problems = SR.scalar_equivalence(cert, state["residuals"], stripped)
        finally:
            cert.residuals, cert.aux = saved
        radii = graded_not_looser(stripped, mode=mode)
        return {"pass": not problems and radii["pass"], "mode": mode, "scalar_problems": problems[:10],
                "graded_looser_m": radii["graded_looser_m"]}

    def shared_structure(self, state, stages) -> dict:
        """Checks of the shared methods (R2-4): registry constants, hull base x1, origin payload identity, parity."""
        import constants_r4 as K4
        c = K4.load_certificates()
        const = stages["constants"]
        problems = []
        if R1E.fraction_of(const["C_o0"].abs_upper()) != c["C_o0"] or R1E.fraction_of(const["C_e0"].abs_upper()) != c["C_e0"]:
            problems.append("constants differ from the R4 registry")
        if R1E.fraction_of(const["C_point"].abs_upper()) < F(state["cell"]["C_upper"]):
            problems.append("C_point below the frozen C_upper")
        lo, hi = R1E.ball_fractions(stages["base"]["eta"])
        x1 = F(self.binding["right"])
        if not (lo <= x1 <= hi and hi - lo <= x1 / 2 ** 200):
            problems.append("hull base eta differs from the binding x1")
        cert = state["cert"]
        for r in range(5):
            o = stages["inputs"]["origin"][("G", r)]
            ref = cert.origin(("G", r, 0))
            if not (o.upper() == ref.upper() and o.lower() == ref.lower()):
                problems.append(f"origin G{r}")
        for (r, j), o in [(k[1], v) for k, v in stages["inputs"]["origin"].items() if k[0] == "W"]:
            ref = cert.origin(("W", (r, j), 3))
            if not (o.upper() == ref.upper() and o.lower() == ref.lower()):
                problems.append(f"origin W{r},{j}")
        return {"problems": problems}


class CusumPointBackend(_CusumStack):
    """PRODUCTION. Never runs in this successor: REAL_INPUT_ARITHMETIC_GUARD = DENY."""
    real_input = True

    def describe(self) -> dict:
        return {"backend": "CusumPointBackend", "cell": "degenerate {0} of frozen CUSUM cell 0"}

    def prepare_point(self, ctx) -> dict:
        EC.enforce_guard(self, ctx)                              # defense in depth: DENY refuses here
        if os.environ.get("K1_THREADS_PINNED") != "1":
            raise EC.ExecutorRefusal("thread environment was not pinned before numpy import")
        import graded_real as GR
        import input_adapters as IA
        scipy_guard = scipy_guard_module()
        if IA.RealInputAdapter().bind() != ctx.k1_binding:
            raise EC.ExecutorRefusal("K1_IDENTITY_MISMATCH: binding differs from a fresh adapter validation")
        initial = production_gate("initial")
        if not initial["pass"]:
            raise EC.ExecutorRefusal(f"AUX5_GATE_REFUSED: {initial['problems']}")
        self.guard = scipy_guard.ScipyGuard().__enter__()        # closed in producer_gate_evidence (final gate)
        cell = self.point_cell()
        cert = GR.GradedRealCertifier(cell, bits=EC.PRECISION).prepare()
        residuals = GR.all_residuals_for_graded(cert)
        return {"cell": cell, "cert": cert, "residuals": residuals, "gate_initial": initial}

    def producer_gate_evidence(self, stages, enc, ctx) -> dict:
        import input_adapters as IA
        state = stages["state"]
        try:
            q08 = self.scalar_consistency(state, stages["inputs"], "REAL")
            rows = order2_rows(state["cert"])
            q10 = order2_compare(rows) | {"mode": "REAL"}
            q06 = certificate_replay() | {"mode": "REAL"}
        finally:
            self.guard.__exit__(None, None, None)
        final = production_gate("final", self.guard)
        structure = self.shared_structure(state, stages)
        cell = state["cell"]
        q03 = (F(cell["left"][0]) == F(cell["right"][0]) == F(cell["e0"][0]) == 0 and F(cell["rho"][0]) == 0
               and F(ctx.k1_binding["right"]) == F(EC.prereg()["cell_selection"]["selected"]["x1"]))
        return {"Q02": {"pass": IA.RealInputAdapter().bind() == ctx.k1_binding, "mode": "REAL"},
                "Q03": {"pass": q03 and not structure["problems"], "mode": "REAL", "structure": structure["problems"]},
                "Q04": {"pass": state["gate_initial"]["pass"] and final["pass"] and final["scipy_free"] is True,
                        "mode": "REAL", "initial": state["gate_initial"], "final": final},
                "Q06": q06, "Q08": q08, "Q10": q10}


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
