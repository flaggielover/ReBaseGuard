"""Generate every K1R4 frozen artifact. Deterministic; every value re-derived from frozen rules.

Nothing here is chosen by hand: q_SR is the frozen generator's own terminal floor on the frozen
geometry grid; the SR partition is the frozen two-level construction (geometry march with the
frozen step and monotone-C rules, then RHO_CAP children on the frozen dyadic ladder); C_upper comes
from the frozen non-decisive geometry routines; the obligation universe comes from the frozen
work_ids definition as the generated T5 stage will call it.
"""
import hashlib
import json
import os
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
ROOT = Path("/home/ubuntu/work/ReBaseGuard")
PROD = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2")
PS1 = PROD / "level4/closure_proofs/p5y_k1_ps1_production"
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"
for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
          "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[k] = "1"

# ---- inherited, unchanged -----------------------------------------------------------
M_UNIVERSE, TARGET, PRECISION_BITS, B_COVER_CAP = (1, 2, 3, 5), Fr(2), 256, Fr(1, 20)
COST_CAP = 150.0
C_CUSUM, CLOSE_CUSUM = Fr(11, 2), Fr(49750555, 8388608)
CLOSE_SR = Fr(1883835, 262144)
OLD_SR_LOWER = Fr(3803026123175981, 562949953421312)        # defective K1R endpoint
# ---- frozen geometry constants (cover_witnesses.json / geometry.py) -------------------
Q, A_DEN, A_NUM, C_DEN = 10_000_000, 1152921504606846976, 919898268343412807, 4294967296
SR_A = (4581762885148045, 8796093022208)                     # c_SR = log(A) + 1/2
LADDER, RMAX = (1, 2, 4, 8, 16, 32, 64), Fr(1, 25)
LAST_FROZEN = {"CUSUM": 8594972549, "SR": 8589984305}         # last frozen rows (cells 325 / parent 315)
EXPECT_TERMINAL_FLOOR_Q = 67555314                           # recorded in cover_witnesses.json


def q(x: Fr) -> str:
    return f"{x.numerator}/{x.denominator}"


def pair(x: Fr) -> list:
    return [q(x), "0/1"]


def canon(o) -> bytes:
    return (json.dumps(o, indent=1, sort_keys=True) + "\n").encode()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def geometry_imports():
    sys.path[:0] = [str(ROOT / "rebaseguard-proof/src"),
                    str(ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r1"),
                    str(ROOT / "level4/closure_proofs/p5y_gate2b_sr_cover")]
    import flint
    if flint.__version__ != "0.9.0":
        raise RuntimeError("frozen python-flint 0.9.0 required")
    from flint import arb
    from rebaseguard_certify.arb_backend import workprec, rational
    from drift_minorant import drift_monotone_resolvent
    from sr_cover import sr_drift_monotone_resolvent
    return arb, workprec, rational, drift_monotone_resolvent, sr_drift_monotone_resolvent


def derive_q_sr(arb, workprec, rational) -> dict:
    wit = json.loads((SPEC_NS / "config/cover_witnesses.json").read_text())
    recorded = wit["detectors"]["SR"]["terminal_floor_q"]
    if recorded != EXPECT_TERMINAL_FLOOR_Q or wit["grid_denominator"] != Q:
        raise SystemExit("frozen witness does not record the expected SR terminal floor")
    with workprec(512):
        c = (arb(SR_A[0]) / arb(SR_A[1])).log() + rational(1, 2)
        lo, hi = int((c.lower() * Q).floor().fmpq()), int((c.upper() * Q).floor().fmpq())
        if not lo == hi == recorded:
            raise SystemExit("two-sided floor of c_SR*Q is not the recorded terminal floor")
        qs = Fr(lo, Q)
        below = c - arb(qs.numerator) / arb(qs.denominator)
        above_next = arb(lo + 1) / arb(Q) - c
        old = arb(OLD_SR_LOWER.numerator) / arb(OLD_SR_LOWER.denominator) - c
        close = arb(CLOSE_SR.numerator) / arb(CLOSE_SR.denominator) - c
        if not (below.lower() > 0 and above_next.lower() > 0 and close.lower() > 0 and old.lower() > 0):
            raise SystemExit("q_SR ordering proof failed")
        return {"q_SR": q(qs), "q_SR_float": float(qs),
                "lattice_rule": "the frozen cover-geometry grid Q = 10^7 (cover_witnesses.grid_denominator); "
                                "q_SR = floor(c_SR * Q) / Q, which the frozen generator itself computed and "
                                "recorded as detectors.SR.terminal_floor_q",
                "c_SR": "log(4581762885148045/8796093022208) + 1/2",
                "c_SR_ball_512": c.str(45),
                "floor_two_sided": {"floor_of_lower": lo, "floor_of_upper": hi, "recorded": recorded},
                "q_SR_lt_c_SR": {"c_SR_minus_q_SR": below.str(25), "strictly_positive": True},
                "canonical_predecessor": {"next_grid_point": q(Fr(lo + 1, Q)),
                                          "next_grid_minus_c_SR": above_next.str(25),
                                          "strictly_positive": True,
                                          "proof": "q_SR is a grid point <= c_SR (floor); the next grid point "
                                                   "exceeds c_SR (certified), so no grid point lies strictly "
                                                   "between q_SR and c_SR"},
                "overlap_width": {"c_SR_minus_q_SR": below.str(25),
                                  "classification": "DECLARED_REDUNDANT_CERTIFIED_OVERLAP"},
                "old_endpoint_gap": {"old_lower": q(OLD_SR_LOWER), "old_minus_c_SR": old.str(20),
                                     "strictly_positive": True, "confirmed": True},
                "c_SR_lt_e_close": {"e_close_minus_c_SR": close.str(20), "strictly_positive": True}}


def derive_sr_partition(qs: Fr, arb, workprec, rational, srres) -> dict:
    parents, left, prev = [], qs.numerator * (Q // qs.denominator), LAST_FROZEN["SR"]
    with workprec(192):
        while True:
            ball, t, _, _, mass = srres(rational(left, Q))
            if not mass:
                raise ArithmeticError("SR mass balance")
            rounded = int((ball.upper() * C_DEN).ceil().fmpq())
            cnum = min(prev, rounded)
            step = Q * A_DEN * C_DEN // (2 * A_NUM * cnum)
            last = Fr(left + step, Q) > CLOSE_SR
            right = CLOSE_SR if last else Fr(left + step, Q)
            parents.append({"left": Fr(left, Q), "right": right, "rounded_C_num": rounded,
                            "C_upper_num": cnum, "step_q": step, "raw_bound_ball": ball.str(40),
                            "t_star": t})
            if last:
                break
            left, prev = left + step, cnum
    return parents


def derive_cusum(arb, workprec, rational, cres) -> list:
    lo, hi = C_CUSUM, CLOSE_CUSUM
    kids = [(lo + i * (hi - lo) / 2, lo + (i + 1) * (hi - lo) / 2) for i in range(2)]
    out, prev = [], LAST_FROZEN["CUSUM"]
    with workprec(192):
        for i, (a, b) in enumerate(kids):
            rec = cres(e_num=a.numerator, e_den=a.denominator)
            ball = arb(rec["resolvent_bound"]["ball"])
            rounded = int((ball.upper() * C_DEN).ceil().fmpq())
            cnum = min(prev, rounded)
            step_q = Q * A_DEN * C_DEN // (2 * A_NUM * cnum)
            if not (b - a) <= Fr(step_q, Q):
                raise SystemExit("CUSUM bridge cell exceeds the frozen geometry step")
            out.append({"C_evaluation": pair(a), "C_upper": f"{cnum}/{C_DEN}", "detector": "CUSUM",
                        "e0": pair((a + b) / 2), "index": 1000 + i, "left": pair(a),
                        "nominal_step_half_width": q(Fr(step_q, 2 * Q)), "rho": pair((b - a) / 2),
                        "right": pair(b)})
            prev = cnum
    return out


SR_CELL_SCHEMA = "rebaseguard.p5y.k1.sr.partition-successor.cell.v1"
BRIDGE_PARENT_BASE, BRIDGE_INDEX_BASE = 9000, 2000


def sr_table(parents: list) -> dict:
    cells, bparents = [], []
    for p, par in enumerate(parents):
        w = par["right"] - par["left"]
        k = next(k for k in LADDER if (w / k) / 2 <= RMAX)
        prec = {"bridge_parent_index": BRIDGE_PARENT_BASE + p, "left": q(par["left"]),
                "right": q(par["right"]), "C_upper": f"{par['C_upper_num']}/{C_DEN}",
                "rounded_C_num": par["rounded_C_num"], "step_q": par["step_q"],
                "raw_bound_ball": par["raw_bound_ball"], "children": k,
                "rule": "frozen geometry march (step + monotone C), then RHO_CAP dyadic ladder"}
        prec_sha = sha(canon(prec))
        bparents.append(dict(prec, record_sha256=prec_sha))
        for j in range(k):
            a, b = par["left"] + j * w / k, par["left"] + (j + 1) * w / k
            cells.append({"C_evaluation": pair(par["left"]), "C_upper": f"{par['C_upper_num']}/{C_DEN}",
                          "child": j, "children": k, "detector": "SR", "e0": pair((a + b) / 2),
                          "id": f"K1R4-SR-B{p:03d}-N{k}-K{j}",
                          "index": BRIDGE_INDEX_BASE + len(cells), "left": pair(a),
                          "parent_index": BRIDGE_PARENT_BASE + p, "parent_record_sha256": prec_sha,
                          "rho": pair((b - a) / 2), "right": pair(b), "schema": SR_CELL_SCHEMA,
                          "terminal": False})
    frozen_rule = json.loads((PROD / "level4/closure_proofs/p5y_k1_sr_o9_partition_successor/"
                                      "config/successor_cells.json").read_text())["rule"]
    return {"schema": "rebaseguard.p5y.k1r4.sr-bridge-table.v1", "n_cells": len(cells),
            "cells": cells, "bridge_parents": bparents, "rule": frozen_rule,
            "partition_rule": "FROZEN two-level construction: geometry march from q_SR with the frozen "
                              "step rule Q*A_DEN*C_DEN//(2*a_num*C_num) and monotone C rule min(prev, "
                              "ceil(bound*2^32)), terminating at e_close; each parent split into the "
                              "smallest k on the frozen dyadic ladder with child rho <= 1/25; children "
                              "inherit the parent's C_upper and C_evaluation (frozen successor rule)",
            "historical_indices_refused": [0, 368], "bridge_indices": [BRIDGE_INDEX_BASE,
                                                                      BRIDGE_INDEX_BASE + len(cells) - 1]}


def bridge_imports():
    auth = json.loads((PS1 / "config/LAUNCH_AUTHORIZATION.json").read_text())
    sys.path[:0] = [str(NS / "driver")] + [str(PROD / r) for r in auth["pythonpath_rel"]] + \
                   [str(PS1 / "driver")]
    import k1r4_bridge_cells as SC
    SC.set_mode("BRIDGE")
    import k1r4_bridge_t5 as S5
    return SC, S5


def universe(SC, S5, table: dict) -> dict:
    """Generated from the frozen work_ids definition exactly as the generated T5 will call it."""
    sys.path.insert(0, str(ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_repair2/code"))
    import certhash
    objects = list(certhash.OBJECTS)
    per_cell, ok = {}, True
    for rec in table["cells"]:
        units = [list(u) for u in S5.cell_units(rec["id"])]
        frozen = [[u[0], rec["id"], u[2], u[3]]
                  for u in S5.universe.work_ids(cells=[SC.universe_carrier(rec)]) if u[2] != "far_field"]
        kinds = {}
        for u in units:
            kinds[u[2]] = kinds.get(u[2], 0) + 1
        good = (sorted(map(tuple, frozen)) == sorted(map(tuple, units)) and len(units) == 28
                and kinds == {"object": 19, "dependency_bundle": 1, "curvature": 4, "assembly": 4}
                and sorted(u[3] for u in units if u[2] == "object") == sorted(objects))
        ok &= good
        per_cell[rec["id"]] = {"index": rec["index"], "units": units, "kind_counts": kinds, "ok": good}
    if not ok:
        raise SystemExit("bridge obligation universe does not derive from the definitions")
    return {"schema": "rebaseguard.p5y.k1r4.sr-bridge-universe.v1", "obligations_per_cell": 28,
            "theorem_invariant": True,
            "derivation": ("universe.work_ids reads only (detector, index) per cell and emits, per cell, "
                           "the 19 certhash.OBJECTS object units, 1 dependency_bundle, one curvature and "
                           "one assembly unit per m in spec.M_VALUES = (1,2,3,5): 19+1+4+4 = 28. succ_t5 "
                           "overwrites the carrier index with rec['id'], so the historical parent lookup "
                           "was a vacuous carrier; the bridge carrier supplies (detector, index) with no "
                           "parent claim. Generated here by calling the generated T5's own universe and "
                           "cell_units, not copied from any historical cell."),
            "objects": objects, "m_values": list(M_UNIVERSE), "cells": per_cell}


def record_schemas() -> dict:
    return {"schema": "rebaseguard.p5y.k1r4.record-schemas.v1",
            "CUSUM": {"consumer": "cusum_layer2.CellCertifier.__init__ (frozen) + aux_propagate",
                      "fields": {
                          "detector": {"type": "str", "value": "CUSUM", "class": "governance"},
                          "left": {"type": "list[str,str]", "encoding": "affine [p, '0/1']; kernel reads [0]", "class": "scientific input geometry"},
                          "right": {"type": "list[str,str]", "encoding": "affine [p, '0/1']; kernel reads [0]", "class": "scientific input geometry"},
                          "e0": {"type": "list[str,str]", "encoding": "affine [p, '0/1']; kernel reads [0]", "class": "scientific"},
                          "rho": {"type": "list[str,str]", "encoding": "affine [p, '0/1']; kernel reads [0], record re-emits the pair", "class": "scientific"},
                          "C_upper": {"type": "str", "encoding": "plain 'num/den' rational, NOT a pair", "class": "scientific"},
                          "index": {"type": "int", "class": "orchestration"},
                          "C_evaluation": {"type": "list[str,str]", "class": "orchestration (not read by the kernel)"},
                          "nominal_step_half_width": {"type": "str", "class": "orchestration (not read by the kernel)"}},
                      "identities": ["e0 == (left+right)/2", "rho == (right-left)/2"]},
            "SR": {"consumer": "generated k1r4_bridge_cells.validate/geometry/identity + t1/t3/t4/t5",
                   "fields": {
                       "left/right/e0/rho/C_evaluation": {"type": "list[str,str]",
                                                          "encoding": "affine [p, s]; bridge cells are non-terminal so s == '0/1' everywhere"},
                       "C_upper": {"type": "str", "encoding": "plain rational, inherited from the bridge parent"},
                       "index": {"type": "int", "range": "2000.."}, "id": {"type": "str"},
                       "parent_index": {"type": "int", "range": "9000.. (bridge parents only)"},
                       "parent_record_sha256": {"type": "str"}, "children": {"type": "int"},
                       "child": {"type": "int"}, "terminal": {"type": "bool", "value": False},
                       "schema": {"value": SR_CELL_SCHEMA}},
                   "identities": ["e0 == (left+right)/2", "rho == (right-left)/2", "rho <= 1/25"]}}


def domain(qd: dict, table: dict) -> dict:
    qs = Fr(qd["q_SR"])
    first, last = Fr(table["cells"][0]["left"][0]), Fr(table["cells"][-1]["right"][0])
    chain = all(Fr(a["right"][0]) == Fr(b["left"][0]) for a, b in zip(table["cells"], table["cells"][1:]))
    if not (first == qs and last == CLOSE_SR and chain):
        raise SystemExit("SR bridge cells do not tile [q_SR, e_close] exactly")
    return {"schema": "rebaseguard.p5y.k1r4.domain-composition.v1",
            "SR": {"historical_compact": "[0, c_SR] (exact affine c_SR, cells 0..368, inherited PASS)",
                   "bridge": f"[{qd['q_SR']}, {q(CLOSE_SR)}]", "far_field": f"[{q(CLOSE_SR)}, infinity)",
                   "ordering_proof": {"q_SR < c_SR": qd["q_SR_lt_c_SR"], "c_SR < e_close": qd["c_SR_lt_e_close"]},
                   "overlap": {"interval": f"[{qd['q_SR']}, c_SR]", "width": qd["overlap_width"]["c_SR_minus_q_SR"],
                               "classification": "DECLARED_REDUNDANT_CERTIFIED_OVERLAP"},
                   "bridge_tiling": {"first_left": q(first), "last_right": q(last), "chain_exact": chain,
                                     "cells": len(table["cells"])},
                   "union": "[0, infinity)", "uncovered_domain_width": "0"},
            "CUSUM": {"historical_compact": "[0, 11/2]", "bridge": f"(11/2, {q(CLOSE_CUSUM)}]",
                      "far_field": f"[{q(CLOSE_CUSUM)}, infinity)", "overlap": "none (rational splice, exact)",
                      "union": "[0, infinity)", "uncovered_domain_width": "0"}}


def scope_amendment(qd: dict) -> dict:
    return {"schema": "rebaseguard.p5y.k1r4.scope-amendment.v1",
            "SCOPE_CHANGE_CLASS": "DOMAIN_ENLARGEMENT_TO_REMOVE_CERTIFICATE_GAP",
            "old_k1r_sr_bridge_lower_endpoint": q(OLD_SR_LOWER),
            "old_endpoint_minus_c_SR": qd["old_endpoint_gap"]["old_minus_c_SR"],
            "defect": "the old endpoint lay approximately 3.0e-17 ABOVE the exact c_SR, leaving "
                      "(c_SR, old endpoint] uncovered by every certificate",
            "new_sr_bridge_lower_endpoint": qd["q_SR"],
            "effect": "prospective replacement in K1R4 only; K1R, K1R2 and K1R3 history is unchanged",
            "why_conservative": ["the bridge domain is enlarged, never narrowed: [q_SR, e_close] strictly contains the old (old, e_close]",
                                 "theorem target unchanged (sup |R| < 2)", "m universe unchanged {1,2,3,5}",
                                 "precision unchanged (256 bits)", "far-field endpoint unchanged (1883835/262144)",
                                 "historical compact evidence unchanged", "the overlap [q_SR, c_SR] is accepted as redundant certification",
                                 "no previously required point is removed"],
            "not": ["threshold relaxation", "post-result narrowing", "a new endpoint chosen by hand"],
            "decided_before_any_bridge_result": True}


def ownership(table: dict) -> dict:
    return {"schema": "rebaseguard.p5y.k1r4.sr-bridge-ownership.v1",
            "owners": {str(c["index"]): "AWS" for c in table["cells"]},
            "cell_count": len(table["cells"]), "bridge_only": True,
            "refused": {"historical_ps1_indices": [0, 368], "unknown_indices": "anything not listed",
                        "foreign_roles": "any role other than AWS"}}


def runtime() -> dict:
    return {"schema": "rebaseguard.p5y.k1r4.runtime-contract.v1",
            "SR_BRIDGE": {"host": "AWS", "sys_vendor": "Amazon EC2", "online_cpus": 32,
                          "python": "/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python",
                          "python_flint": "0.9.0", "precision_bits": PRECISION_BITS,
                          "threads": "single-threaded BLAS/FLINT (all *_NUM_THREADS = 1)",
                          "vultr": "PROHIBITED", "mac": "PROHIBITED", "handoff": "PROHIBITED",
                          "synthetic": "PROHIBITED"},
            "CUSUM_BRIDGE": {"hosts": ["AWS", "VULTR"], "mac": "PROHIBITED",
                             "binding": "runtime identity of the chosen host bound at production start"}}


def cost(n_sr: int) -> dict:
    sr_h, cu_h = round(12.705 * n_sr, 3), round(0.632 * 2, 3)
    total = round(sr_h + cu_h, 3)
    if total >= COST_CAP:
        raise SystemExit(f"expected {total} CPU-h does not fit the frozen {COST_CAP} cap")
    return {"schema": "rebaseguard.p5y.k1r4.cost-accounting.v1", "cap_cpu_h_shared": COST_CAP,
            "consumed_genuine_cpu_h": 0.0, "k1r_k1r2_k1r3_consumed_cpu_h": 0.0,
            "expected": {"sr_bridge_cells": n_sr, "sr_cpu_h": sr_h, "cusum_cells": 2, "cusum_cpu_h": cu_h,
                         "total_cpu_h": total, "basis": "PS1 mean 12.705 CPU-h/cell; CUSUM mean 0.632"},
            "non_production": ["geometry derivation", "369-cell equivalence replay (0.36 CPU-h, no patch solve)",
                               "qualification"],
            "enforcement": "halt BEFORE any launch whose projected cost would exceed the cap"}


def predecessor() -> dict:
    return {"schema": "rebaseguard.p5y.k1r4.predecessor-binding.v1",
            "history": {"P5": "PARTIAL", "P5X": "PARTIAL", "P5Y_K1": "PARTIAL"},
            "k1r": {"freeze": "7f671b9ba2d7111b5e8cde010bc660904925fa1c", "halt_b1": "adad61f",
                    "state": "HALTED_BY_GOVERNANCE after B1 PASS",
                    "b1_result_sha256": "41fd34c6ede08b358c9b897f82662e9dd258d3c1619464a47e7f568ebf9f37bb"},
            "k1r2": {"freeze": "19272cb68aeb24d54a09f7b6188dca00171abe15", "halt": "b258c18",
                     "state": "HALTED before any bridge computation"},
            "k1r3": {"work_record": "6fb3e17", "state": "PREREGISTRATION FAIL, NOT FROZEN, scope defect discovered",
                     "halt_record": "evidence/K1R3_SCOPE_HALT.json"},
            "b1": "INHERITED PASS (1304/1304), not rerun", "rewrite_of_predecessors": "PROHIBITED"}


def main() -> int:
    CFG.mkdir(parents=True, exist_ok=True)
    arb, workprec, rational, cres, srres = geometry_imports()
    qd = derive_q_sr(arb, workprec, rational)
    table = sr_table(derive_sr_partition(Fr(qd["q_SR"]), arb, workprec, rational, srres))
    (CFG / "SR_BRIDGE_CELL_TABLE.json").write_bytes(canon(table))
    cu = {"schema": "rebaseguard.p5y.k1r4.cusum-bridge-table.v1", "cells": derive_cusum(arb, workprec, rational, cres),
          "domain": f"(11/2, {q(CLOSE_CUSUM)}]", "consumed_by": "frozen CellCertifier (unchanged)"}
    (CFG / "CUSUM_BRIDGE_CELL_TABLE.json").write_bytes(canon(cu))
    SC, S5 = bridge_imports()
    arts = {"Q_SR_DERIVATION.json": qd, "SR_BRIDGE_UNIVERSE.json": universe(SC, S5, table),
            "RECORD_SCHEMAS.json": record_schemas(), "DOMAIN_COMPOSITION.json": domain(qd, table),
            "SCOPE_AMENDMENT.json": scope_amendment(qd), "SR_BRIDGE_OWNERSHIP.json": ownership(table),
            "RUNTIME_CONTRACT.json": runtime(), "COST_ACCOUNTING.json": cost(len(table["cells"])),
            "PREDECESSOR_BINDING.json": predecessor()}
    for n, b in arts.items():
        (CFG / n).write_bytes(canon(b))
    h = {n: sha((CFG / n).read_bytes()) for n in sorted(
        list(arts) + ["SR_BRIDGE_CELL_TABLE.json", "CUSUM_BRIDGE_CELL_TABLE.json", "TRANSFORMATION_MANIFEST.json"])}
    tm = json.loads((CFG / "TRANSFORMATION_MANIFEST.json").read_text())
    stages = {k: v["generated_sha256"] for k, v in sorted(tm["stages"].items())}
    stage_drift = [k for k, v in stages.items() if sha((NS / "driver" / k).read_bytes()) != v]
    if stage_drift:
        raise SystemExit(f"generated stage drift vs manifest: {stage_drift}")
    auth = json.loads((PS1 / "config/LAUNCH_AUTHORIZATION.json").read_text())
    lower = {f: auth["executor_source_sha256"][f] for f in auth["executor_source_manifest"]}
    ident_body = {"transformation_manifest_sha256": h["TRANSFORMATION_MANIFEST.json"], "generated_stages": stages,
                  "lower_level_dependencies": lower, "bridge_table_sha256": h["SR_BRIDGE_CELL_TABLE.json"],
                  "bridge_universe_sha256": h["SR_BRIDGE_UNIVERSE.json"],
                  "record_schemas_sha256": h["RECORD_SCHEMAS.json"],
                  "runtime_contract_sha256": h["RUNTIME_CONTRACT.json"], "precision_bits": PRECISION_BITS}
    producer = sha(json.dumps(ident_body, sort_keys=True, separators=(",", ":")).encode())
    authz = {"schema": "rebaseguard.p5y.k1r4.sr-bridge-authorization.v1",
             "authorization_id": "K1R4-SR-BRIDGE-AUTH-001", "producer_identity": "K1R4-SR-BRIDGE-PRODUCER",
             "producer_identity_sha256": producer, "identity_body": ident_body,
             "ps1_authorization_reused": False, "topology": "A_AWS_ONLY", "role": "AWS",
             "cells": [c["index"] for c in table["cells"]], "ownership_sha256": h["SR_BRIDGE_OWNERSHIP.json"],
             "domain_composition_sha256": h["DOMAIN_COMPOSITION.json"],
             "scope_amendment_sha256": h["SCOPE_AMENDMENT.json"],
             "cost_accounting_sha256": h["COST_ACCOUNTING.json"],
             "target": q(TARGET), "precision_bits": PRECISION_BITS, "m_universe": list(M_UNIVERSE),
             "cost_cap_cpu_h": COST_CAP, "vultr": "PROHIBITED", "handoff": "PROHIBITED",
             "synthetic": "PROHIBITED", "result_bearing": False,
             "k1r4_freeze_binding": "CHECKPOINT_HASH + tag p5y-k1r4-bridge-successor-frozen; verified at production start"}
    (CFG / "SR_BRIDGE_AUTHORIZATION.json").write_bytes(canon(authz))
    h["SR_BRIDGE_AUTHORIZATION.json"] = sha((CFG / "SR_BRIDGE_AUTHORIZATION.json").read_bytes())
    cp = {"schema": "rebaseguard.p5y.k1r4.checkpoint.v1", "campaign": "P5Y-K1R4",
          "frozen_artifacts": h, "generated_stages": stages, "producer_identity_sha256": producer,
          "q_SR": qd["q_SR"], "sr_bridge_cells": len(table["cells"]), "cusum_bridge_cells": 2,
          "inherited": {"cusum_domain": f"(11/2, {q(CLOSE_CUSUM)}]", "sr_upper": q(CLOSE_SR),
                        "m_universe": list(M_UNIVERSE), "target": q(TARGET), "precision_bits": PRECISION_BITS,
                        "b_cover_cap": q(B_COVER_CAP), "cost_cap_cpu_h": COST_CAP},
          "production_started": False, "genuine_results_present": False, "result_bearing": False,
          "k1_status": "PARTIAL (unchanged)", "k1r4_status": "NOT_DECIDED_HERE"}
    (CFG / "CHECKPOINT.json").write_bytes(canon(cp))
    (CFG / "CHECKPOINT_HASH").write_text(sha((CFG / "CHECKPOINT.json").read_bytes()) + "\n")
    print(json.dumps({"q_SR": qd["q_SR"], "sr_cells": len(table["cells"]), "producer": producer,
                      "checkpoint": (CFG / "CHECKPOINT_HASH").read_text().strip()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
