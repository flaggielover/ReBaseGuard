"""REAL CUSUM signed order-3 producer front-end.

NOT EXECUTED ON ANY CUSUM CELL IN THIS NAMESPACE. `certify_real_cell` refuses before reading a record, building a
certifier or touching an operator unless a real-cell authorization is present in the pinned registry, and the
registry frozen with this producer is EMPTY (config/REAL_CELL_AUTHORIZATION_REGISTRY.json). Adding an authorization
changes the pinned registry hash, hence this file, hence the order-3 producer identity: it is a governed successor
act, never a configuration edit.

What it wires, by explicit construction (no module assignment; checked by Aux3's no_monkeypatch detector):

    frozen, imported in place, unchanged
      qualify5.run_cell science sequence:  Aux3Certifier.prepare -> all_residuals -> aux_residuals
                                           -> aux_propagate.cell_obligations(refine2.refine, AuxiliaryRefinement)
      Aux5 manifest_v3 initial_gate / final_gate (producer identity 3692d0fe, runtime contract), SciPy guard
    new
      Order3Certifier(Aux3Certifier)       degree-12 candidates G_r ~ F_r''' (float Layer 1; proposes only)
      rung3_residual.g_residual            certified midpoint residual of G_r (frozen H_r pattern, one order up)
      collect_inputs                       frozen certified nodes -> engine inputs (no new constant)
      rung3_engine.certify_order3          whole-cell signed R''' interval, per m
      k1_inputs.validate + cross_check_k1  the sealed K1 record is validated and must intersect the recomputation

Candidate cost note: Aux3's `_candidates_order3` does not retain its order-3 collocation, so the rung recomputes it
(about 170 CPU-s at CUSUM scale). This affects cost only, never a certified number.
"""
from __future__ import annotations

import os
import sys

_PINNED = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}
if "numpy" not in sys.modules:
    os.environ.update(_PINNED)
    os.environ["K1_THREADS_PINNED"] = "1"

import hashlib                                                         # noqa: E402
import json                                                            # noqa: E402
import resource                                                        # noqa: E402
import time                                                            # noqa: E402
from fractions import Fraction as F                                    # noqa: E402
from pathlib import Path                                               # noqa: E402

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = REPO / "level4/closure_proofs"
AUX5_CODE = CP / "p5y_k1_cusum_aux5_successor/code"
for _p in (str(NS / "code"), str(AUX5_CODE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import ancestry5                                                       # noqa: E402,F401  frozen import bootstrap

import numpy as np                                                     # noqa: E402

import aux_certifier                                                   # noqa: E402
import aux_collocation                                                 # noqa: E402
import aux_propagate                                                   # noqa: E402
import aux_refine                                                      # noqa: E402
import manifest_v3                                                     # noqa: E402
import order2                                                          # noqa: E402
import refine2                                                         # noqa: E402
import scipy_guard                                                     # noqa: E402
import spec                                                            # noqa: E402
from cusum_layer2 import Pair, Z_RANGE                                 # noqa: E402
from intervals import exact, workprec                                  # noqa: E402

import k1_inputs                                                       # noqa: E402
import rung3_engine as E                                               # noqa: E402
import rung3_residual as RR                                            # noqa: E402

AUTH_REGISTRY = NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY.json"
AUTH_REGISTRY_SHA256 = "dfe0384b132c7769fb15245948461708264b2a1c8853fdcfe69688fcb148d3a3"
PRODUCER_MANIFEST = NS / "config/ORDER3_PRODUCER_MANIFEST.json"
DETECTOR = {"name": "CUSUM", "k": "1/2", "h": "5", "two_sided": True, "reset": "0"}
ASSEMBLY_TABLE = {"path": "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/checkpoint.json",
                  "key": "assembly",
                  "sha256": "1c2a6825f19e19de6fb588647ca3fc4618068087ef0976292ca7bbeca701f13f"}
SOURCE_DEFINITIONS = {
    "order3_design_commit": "10911e512ddae51bdc9b2b6b599076f2ec82784c",
    "order3_design_DESIGN.md": "level4/closure_proofs/p5y_k5_cusum_order3_producer_design/DESIGN.md",
    "K5B_theorem_sha256": "c1c62346dcd11b3a56b028e4aca7b61d7c4254353b1504701f16989205339d3f",
    "K5B_countersignature_commit": "d7d3c08b5ae9b072f243704b0581b2f708228087",
    "premise_binding_commit": "10769e07029eb66be264109f274d5ca3269b5cbf",
}


class RealCellNotAuthorized(E.ProducerRefusal):
    pass


# ------------------------------------------------------------------ governance gate (runs FIRST)
def require_authorization(cell_index: int, authorization: dict | None) -> dict:
    raw = AUTH_REGISTRY.read_bytes()
    if hashlib.sha256(raw).hexdigest() != AUTH_REGISTRY_SHA256:
        raise RealCellNotAuthorized("authorization registry bytes differ from the pinned registry")
    registry = json.loads(raw)
    if authorization is None:
        raise RealCellNotAuthorized(f"cell {cell_index}: no real-cell authorization supplied")
    digest = hashlib.sha256(E.canonical(authorization)).hexdigest()
    for entry in registry.get("authorizations", []):
        if entry.get("authorization_sha256") == digest and cell_index in entry.get("cells", []):
            return entry
    raise RealCellNotAuthorized(f"cell {cell_index}: authorization {digest[:12]} is not in the pinned registry")


def producer_manifest_problems() -> list[str]:
    m = json.loads(PRODUCER_MANIFEST.read_text())
    out = []
    for rel, sha in sorted(m["files"].items()):
        p = REPO / rel
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != sha:
            out.append(rel)
    return out


# ------------------------------------------------------------------ the new rung's candidates
class Order3Certifier(aux_certifier.Aux3Certifier):
    """Aux3Certifier plus degree-12 candidates G_r for F_r''' and the residual surface rung3_residual needs."""

    provides_rung3 = True
    vec = staticmethod(Pair)
    z_range = Z_RANGE

    def prepare(self):
        super().prepare()
        self._candidates_rung3()
        return self

    def _candidates_rung3(self):
        """Layer 1 (float, proposes): (I - K) G_r = dddK F_r + 3 ddK D_r + 3 dK H_r + S_r''' on the frozen grid."""
        co, obj = self.co, self.obj
        co3 = aux_collocation.collocation_order3(float(self.e0))
        vals = aux_collocation.objects_order3(co, obj, co3)
        op = np.eye(co["dim"]) - co["K"]
        for r in range(5):
            rhs = (co3["dddK"] @ obj["F"][r] + 3.0 * (co["ddK"] @ obj["D"][r])
                   + 3.0 * (co["dK"] @ obj["H"][r]) + vals["S3"][r])
            self.P["G", r, 0], self.sup["G", r, 0] = self._cand(np.linalg.solve(op, rhs))


def collect_inputs(cert, record: dict, aux_mid: dict, g: dict) -> dict:
    """Frozen certified quantities -> engine inputs. Every value is a certified upper bound already produced by the
    adjudicated order 0-2 machinery or Aux3's order-3 source evidence; nothing new is estimated here."""
    return {
        "C": exact(cert.C), "rho": exact(cert.rho),
        "k": {i: cert.norms["k"][i] for i in range(5)}, "j": {i: cert.norms["j"][i] for i in range(5)},
        "mid": dict(aux_mid),
        "cell": {key: exact(F(v)) for key, v in record["eps_cell"].items()},
        "refined": {key: exact(F(v)) for key, v in record["eps_cell_refined"].items()},
        "aux": {name: {"delta_mid": v["delta_mid"], "delta_cell": v["delta_cell"]} for name, v in cert.aux.items()},
        "g": g,
        "towers": aux_refine.towers(cert),
        "sup_S0_4": order2.sup_source_derivative_on(4, cert.left, cert.right),
        "sup_hat": {(fam, r): cert.sup[fam, r, 0] for fam in ("F", "D", "H", "G") for r in range(5)},
        "origin": {("G", r): cert.origin(("G", r, 0)) for r in range(5)}
        | {("W", (r, j)): cert.origin(("W", (r, j), 3)) for r in range(4) for j in range(4 - r)},
    }


def cross_check_k1(recomputed: dict, sealed: dict) -> dict:
    """Both are certified enclosures of the same (D, m, cell) quantities: they must intersect."""
    out = {}
    for m in k1_inputs.M_VALUES:
        row = {}
        for name in ("R_interval", "D_interval", "R2_interval"):
            a = recomputed["m"][int(m)][name]
            lo_a, hi_a = F(a["lo"]), F(a["hi"])
            lo_b, hi_b = (F(x) for x in sealed["per_m"][m][name])
            if max(lo_a, lo_b) > min(hi_a, hi_b):
                raise E.ProducerRefusal(f"K1 cross-check: recomputed {name} m={m} is disjoint from the sealed record")
            row[name] = {"intersects": True, "identical": (lo_a, hi_a) == (lo_b, hi_b)}
        out[m] = row
    return out


def certify_real_cell(cell_index: int, *, authorization: dict | None, record_bytes: bytes,
                      bits: int = E.PRODUCTION_BITS) -> dict:
    entry = require_authorization(cell_index, authorization)          # FIRST: nothing precedes the gate
    sealed = k1_inputs.validate(record_bytes, cell_index=cell_index)
    if bits != E.PRODUCTION_BITS:
        raise E.ProducerRefusal("real cells run at the frozen production precision only")
    problems = producer_manifest_problems()
    if problems:
        raise E.ProducerRefusal(f"order-3 producer manifest mismatch: {problems}")
    if os.environ.get("K1_THREADS_PINNED") != "1":
        raise E.ProducerRefusal("thread environment was not pinned before numpy import")
    manifest_v3.initial_gate()
    cell = next(c for c in spec.CELLS if c["detector"] == "CUSUM" and c["index"] == cell_index)
    t0, w0 = time.process_time(), time.time()
    guard = scipy_guard.ScipyGuard()
    with guard:
        with workprec(bits):
            cert = Order3Certifier(cell, bits=bits).prepare()
            cert.all_residuals()
            cert.aux_residuals()
            holder = {}

            def make_backend(c, mid_nodes):
                holder["aux_mid"] = aux_certifier.midpoint_order3_eps(c, mid_nodes)
                return aux_refine.AuxiliaryRefinement(c, mid_nodes, holder["aux_mid"])

            record = aux_propagate.cell_obligations(cert, whole_cell_refinement=refine2.refine,
                                                    node_refinement_factory=make_backend)
            g = {r: RR.g_residual(cert, r) for r in range(5)}
            result = E.certify_order3(collect_inputs(cert, record, holder["aux_mid"], g), bits=bits)
        k1_check = cross_check_k1(record, sealed)
    binding = {
        "detector": DETECTOR, "D": "CUSUM(k=1/2,h=5)", "m": list(E.M_VALUES), "cell_id": cell_index,
        "cell": {"left": cell["left"][0], "right": cell["right"][0], "e0": cell["e0"][0], "rho": cell["rho"][0],
                 "C_upper": cell["C_upper"]},
        "precision_bits": bits, "coefficient_table": ASSEMBLY_TABLE, "source_definitions": SOURCE_DEFINITIONS,
        "k1_producer_identity": sealed["producer_identity_hash"], "k1_record_sha256": sealed["record_sha256"],
        "k1_scientific_content_hash": sealed["scientific_content_hash"],
        "k1_export_manifest_sha256": sealed["export_manifest_sha256"],
        "order3_producer_manifest_sha256": hashlib.sha256(PRODUCER_MANIFEST.read_bytes()).hexdigest(),
        "aux5_runtime_contract_hash": manifest_v3.runtime_contract_hash(),
        "authorization": entry, "k1_cross_check": k1_check,
    }
    payload = E.scientific_payload(result, binding)
    gate = manifest_v3.final_gate(scipy_guard=guard)
    return {"scientific": payload, "scientific_hash": E.scientific_hash(payload),
            "metadata": {"cpu_seconds": time.process_time() - t0, "wall_seconds": time.time() - w0,
                         "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                         "final_gate_stage": gate["stage"]}}
