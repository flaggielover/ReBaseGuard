"""Generate the K1R2 bridge-executor freeze. Deterministic; all hashes reproducible.

K1R2 is ADDITIVE. It changes execution/governance identity ONLY: the scientific
equations, thresholds, precision, m universe and bridge domains are inherited from the
frozen K1R preregistration and are not touched. It creates bridge-only cell tables so
the already-qualified kernels can be called on the frozen bridge intervals, which the
historical producers cannot resolve.
"""
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
ROOT = Path("/home/ubuntu/work/ReBaseGuard")
PROD = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2")
PS1 = PROD / "level4/closure_proofs/p5y_k1_ps1_production"
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"

# ---- inherited, MUST NOT CHANGE (from the frozen K1R preregistration) -------------
M_UNIVERSE = (1, 2, 3, 5)
TARGET = Fr(2)
PRECISION_BITS = 256
B_COVER_CAP = Fr(1, 20)
SR_RHO_CAP = Fr(1, 25)
C_CUSUM, CLOSE_CUSUM = Fr(11, 2), Fr(49750555, 8388608)
C_SR, CLOSE_SR = Fr(3803026123175981, 562949953421312), Fr(1883835, 262144)
COST_CAP_CPU_H = 150.0

# ---- frozen geometry constants (cover_witnesses.json / geometry.py) ---------------
GEOM_BITS = 192
FLINT_VERSION = "0.9.0"
GRID_Q = 10_000_000
A_DEN = 1152921504606846976
A_NUM = 919898268343412807
C_DEN = 4294967296
LAST_FROZEN_C_UPPER = {"CUSUM": 8594972549, "SR": 8589984305}   # cells 325 / 368
BRIDGE_INDEX_BASE = {"CUSUM": 1000, "SR": 2000}
HISTORICAL_INDEX_RANGE = {"CUSUM": [0, 325], "SR": [0, 368]}

KERNEL_MODULES = ("refine2", "aux_certifier", "aux_propagate", "aux_refine", "hash_v2",
                  "scipy_guard", "certhash", "provenance", "intervals", "repair_check", "spec")
KERNEL_PATH = ("level4/closure_proofs/p5y_k1_cusum_aux4_fullcover/code",
               "level4/closure_proofs/p5y_k1_cusum_aux3_successor/code",
               "level4/closure_proofs/p5y_k1_cusum_completion_successor/code",
               "level4/closure_proofs/p5y_k1_final_completion/code",
               "level4/closure_proofs/p5y_k1_cover_ledger_repair2/code",
               "level4/closure_proofs/p5y_k1_cover_ledger_repair1/code",
               "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code",
               "rebaseguard-proof/src")


def q(x: Fr) -> str:
    return f"{x.numerator}/{x.denominator}"


def qf(x: Fr) -> dict:
    return {"exact": q(x), "float": float(x)}


def sha_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canon(o) -> bytes:
    return (json.dumps(o, indent=1, sort_keys=True) + "\n").encode()


def children(lo: Fr, hi: Fr, n: int) -> list:
    w = (hi - lo) / n
    return [(lo + i * w, lo + (i + 1) * w) for i in range(n)]


def geometry_witnesses() -> dict:
    """Call the SAME frozen routines the frozen cover used; geometry only, no K1 solves."""
    sys.path[:0] = [str(ROOT / "rebaseguard-proof/src"),
                    str(ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r1"),
                    str(ROOT / "level4/closure_proofs/p5y_gate2b_sr_cover")]
    import flint
    from flint import arb
    from rebaseguard_certify.arb_backend import workprec, rational
    from drift_minorant import drift_monotone_resolvent
    from sr_cover import sr_drift_monotone_resolvent
    if flint.__version__ != FLINT_VERSION:
        raise RuntimeError(f"frozen python-flint {FLINT_VERSION} required")
    out = {"schema": "rebaseguard.p5y.k1r2.bridge-geometry-witness.v1", "bits": GEOM_BITS,
           "python_flint": flint.__version__, "C_upper_den": C_DEN,
           "routine": {"CUSUM": "drift_minorant.drift_monotone_resolvent",
                       "SR": "sr_cover.sr_drift_monotone_resolvent"},
           "decisive": False, "detectors": {}}
    with workprec(GEOM_BITS):
        for det, ivs in (("CUSUM", children(C_CUSUM, CLOSE_CUSUM, 2)),
                         ("SR", children(C_SR, CLOSE_SR, 6))):
            rows, prev = [], LAST_FROZEN_C_UPPER[det]
            for lo, hi in ivs:
                if det == "CUSUM":
                    rec = drift_monotone_resolvent(e_num=lo.numerator, e_den=lo.denominator)
                    ball, t = arb(rec["resolvent_bound"]["ball"]), rec["t_star"]
                else:
                    ball, t, _, _, mass = sr_drift_monotone_resolvent(
                        rational(lo.numerator, lo.denominator))
                    if not mass:
                        raise ArithmeticError("SR mass balance")
                rounded = int((ball.upper() * C_DEN).ceil().fmpq())
                cnum = min(prev, rounded)                       # frozen monotone rule
                step_q = GRID_Q * A_DEN * C_DEN // (2 * A_NUM * cnum)
                rows.append({"left": q(lo), "left_float": float(lo), "raw_bound_ball": ball.str(40),
                             "t_star": t, "rounded_C_num": rounded, "C_upper_num": cnum,
                             "nominal_step_q": step_q,
                             "nominal_step_float": step_q / GRID_Q,
                             "cell_width_float": float(hi - lo),
                             "width_within_frozen_step_rule": float(hi - lo) <= step_q / GRID_Q})
                prev = cnum
            out["detectors"][det] = {"rows": rows,
                                     "monotone_non_increasing": all(
                                         rows[i]["C_upper_num"] >= rows[i + 1]["C_upper_num"]
                                         for i in range(len(rows) - 1)),
                                     "capped_by_last_frozen_cell": LAST_FROZEN_C_UPPER[det]}
    return out


def cell_tables(w: dict) -> dict:
    """Bridge-only cell tables in the FROZEN entry schema, with bridge-only indices."""
    tables = {}
    for det, (c, close, n) in (("CUSUM", (C_CUSUM, CLOSE_CUSUM, 2)),
                               ("SR", (C_SR, CLOSE_SR, 6))):
        rows, cells = w["detectors"][det]["rows"], []
        for i, (lo, hi) in enumerate(children(c, close, n)):
            r = rows[i]
            cells.append({
                "index": BRIDGE_INDEX_BASE[det] + i, "detector": det,
                "left": q(lo), "right": q(hi),
                "e0": q((lo + hi) / 2), "rho": q((hi - lo) / 2),
                "C_evaluation": q(lo),
                "C_upper": f"{r['C_upper_num']}/{C_DEN}",
                "nominal_step_half_width": q(Fr(r["nominal_step_q"], 2 * GRID_Q)),
                "bridge_only": True, "historical_index": None,
                "k1r_child": i, "lower_open": True, "upper_closed": True})
        tbl = {"schema": "rebaseguard.p5y.k1r2.bridge-cell-table.v1", "detector": det,
               "domain": {"lo": qf(c), "hi": qf(close), "closure": "(lo, hi]"},
               "cells": cells, "cell_count": n,
               "index_base": BRIDGE_INDEX_BASE[det],
               "historical_indices_resolvable": False,
               "historical_index_range_refused": HISTORICAL_INDEX_RANGE[det],
               "geometry_witness": w["detectors"][det],
               "inherited": {"m_universe": list(M_UNIVERSE), "target": q(TARGET),
                             "precision_bits": PRECISION_BITS,
                             "b_cover_cap": q(B_COVER_CAP)},
               "endpoint_shrinkage": "PROHIBITED",
               "provenance": "endpoints inherited verbatim from the frozen K1R plans; "
                             "C_upper computed by the frozen cover-geometry routine"}
        if det == "SR":
            tbl["rho_cap"] = q(SR_RHO_CAP)
            tbl["rho_cap_satisfied"] = all(Fr(x["rho"]) <= SR_RHO_CAP for x in cells)
        tables[det] = tbl
    return tables


def kernel_identity() -> dict:
    """Bind the scientific kernel by path+hash, resolved the way Python would resolve it."""
    mods, missing = {}, []
    for name in KERNEL_MODULES:
        for rel in KERNEL_PATH:
            p = ROOT / rel / f"{name}.py"
            if p.exists():
                mods[name] = {"path": str(p.relative_to(ROOT)), "sha256": sha_file(p)}
                break
        else:
            missing.append(name)
    if missing:
        raise RuntimeError(f"kernel modules not resolvable: {missing}")
    digest = hashlib.sha256(json.dumps(
        {k: v["sha256"] for k, v in sorted(mods.items())}, sort_keys=True,
        separators=(",", ":")).encode()).hexdigest()
    return {"modules": mods, "module_count": len(mods),
            "kernel_identity_sha256": digest,
            "search_path": list(KERNEL_PATH),
            "semantics": "UNCHANGED: K1R2 imports these modules and calls them on bridge "
                         "cells; it does not copy, patch or re-implement any of them",
            "frozen_spec_namespace": str(SPEC_NS.relative_to(ROOT)),
            "frozen_spec_cells_sha256": sha_file(SPEC_NS / "config/cells.json"),
            "frozen_spec_checkpoint_sha256": sha_file(SPEC_NS / "config/checkpoint.json"),
            "frozen_spec_record_schema_sha256": sha_file(SPEC_NS / "config/record_schema.json"),
            "frozen_spec_mutation": "PROHIBITED (spec.verify_frozen_spec enforces it)"}


def cusum_producer_contract(tbl: dict, ker: dict) -> dict:
    return {"schema": "rebaseguard.p5y.k1r2.cusum-bridge-producer-contract.v1",
            "producer": "K1R2-CUSUM-BRIDGE",
            "bridge_only": True, "cells": [c["index"] for c in tbl["cells"]],
            "cell_table_sha256": hashlib.sha256(canon(tbl)).hexdigest(),
            "scientific_kernel": ker,
            "certification_entry": {
                "lineage_entry": "p5y_k1_cusum_aux4_fullcover/code/qualify4.py:run_cell",
                "why_not_reused_verbatim": "run_cell resolves its cell from the frozen "
                    "326-cell spec.CELLS, whose sha256 is bound into the historical producer "
                    "identity and cover-geometry gate; a bridge cell cannot be added there "
                    "without mutating a frozen artifact",
                "k1r2_orchestration": "the SAME kernel calls in the SAME order on a bridge "
                    "cell dict: Aux3Certifier(cell, bits).prepare() -> all_residuals -> "
                    "aux_residuals -> aux_propagate.cell_obligations(refine2.refine, "
                    "AuxiliaryRefinement) -> require_single_charge -> tightening_report",
                "historical_producer_modified": False},
            "inherited_science": {"m_universe": list(M_UNIVERSE), "target": q(TARGET),
                                  "precision_bits": PRECISION_BITS,
                                  "b_cover_cap": q(B_COVER_CAP),
                                  "correspondence_gates": "frozen; unchanged",
                                  "equations": "UNCHANGED"},
            "refinement": {"max_refinement_depth": 0,
                           "adaptive_refinement_after_results": "PROHIBITED"},
            "record_schema": "the frozen spec record schema; bridge records add only "
                             "bridge_only/bridge_index provenance fields",
            "qualification_must_not_read": ["historical result statuses",
                                            "historical obligation outcomes"]}


def sr_authorization(tbl: dict) -> dict:
    auth = json.loads((PS1 / "config/LAUNCH_AUTHORIZATION.json").read_text())
    return {"schema": "rebaseguard.p5y.k1r2.sr-bridge-authorization.v1",
            "authorization_id": "K1R2-SR-BRIDGE-AUTH-001",
            "bridge_only": True, "cells": [c["index"] for c in tbl["cells"]],
            "cell_count": len(tbl["cells"]),
            "cell_table_sha256": hashlib.sha256(canon(tbl)).hexdigest(),
            "topology": "A_AWS_ONLY",
            "active_host": "AWS",
            "hosts": {"AWS": {"cells": [c["index"] for c in tbl["cells"]],
                              "online_cpus": 32, "sys_vendor": "Amazon EC2",
                              "python": "/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python"},
                      "VULTR": {"cells": [], "status": "NOT_QUALIFIED_FOR_SR",
                                "substitution": "PROHIBITED"}},
            "handoff": {"status": "NOT_USED (bridge is AWS-only)",
                        "public_key_fingerprint": None},
            "synthetic_path": "PROHIBITED",
            "scientific_executor": {
                "source_manifest_files": len(auth["executor_source_manifest"]),
                "scientific_adapter_hash": auth["scientific_adapter_hash"],
                "producer_commit": auth["producer_commit"],
                "checkpoint_sha256": auth["checkpoint_sha256"],
                "ps1_protocol_sha256": auth["ps1_protocol_sha256"],
                "live_patches_sha256": auth["live_patches_sha256"],
                "semantics": "UNCHANGED: the identical qualified SR executor"},
            "inherited_science": {"m_universe": list(M_UNIVERSE), "target": q(TARGET),
                                  "precision_bits": PRECISION_BITS,
                                  "b_cover_cap": q(B_COVER_CAP), "rho_cap": q(SR_RHO_CAP)},
            "historical_ps1": {"cells": 369, "obligations": 10332,
                               "role": "INHERITED EVIDENCE ONLY",
                               "resolvable_as_new_work": False,
                               "production_ledger_sha256":
                                   "988725cd8dd02d28f52ef18e3b1add8063825cc42ee828c99d556a12b06d0dd8",
                               "successor_cells_sha256": auth["successor_cells_sha256"],
                               "modification": "PROHIBITED"},
            "result_bearing": False}


def sr_ownership(tbl: dict) -> dict:
    ids = [c["index"] for c in tbl["cells"]]
    return {"schema": "rebaseguard.p5y.k1r2.sr-bridge-ownership.v1",
            "owners": {str(i): "AWS" for i in ids},
            "cell_count": len(ids), "bridge_only": True,
            "refuses": {"historical_ps1_cells": HISTORICAL_INDEX_RANGE["SR"],
                        "reason": "historical cells are inherited evidence, never new work",
                        "foreign_host": "any role other than AWS"},
            "gate": "multihost.gate_cell_ownership semantics: a cell absent from this map is "
                    "'not in the frozen cover'; a cell owned by another role is refused"}


def runtime_contract(ker: dict) -> dict:
    return {"schema": "rebaseguard.p5y.k1r2.runtime-contract.v1",
            "geometry": {"python_flint": FLINT_VERSION, "workprec_bits": GEOM_BITS,
                         "routines": ["drift_minorant.drift_monotone_resolvent",
                                      "sr_cover.sr_drift_monotone_resolvent"],
                         "decisive": False},
            "certification": {"precision_bits": PRECISION_BITS,
                              "thread_pinning": "K1_THREADS_PINNED=1 before numpy import; "
                                                "single-threaded BLAS/FLINT",
                              "python": "/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python"},
            "hosts": {"CUSUM_BRIDGE": {"permitted": ["AWS", "VULTR"],
                                       "basis": "the CUSUM lineage is qualified on both; the "
                                                "runtime identity of the chosen host is bound "
                                                "at production start",
                                       "mac": "PROHIBITED"},
                      "SR_BRIDGE": {"permitted": ["AWS"], "vultr": "PROHIBITED",
                                    "mac": "PROHIBITED"}},
            "kernel_identity_sha256": ker["kernel_identity_sha256"]}


def predecessor_binding() -> dict:
    return {"schema": "rebaseguard.p5y.k1r2.predecessor-binding.v1",
            "k1r": {"freeze_commit": "7f671b9ba2d7111b5e8cde010bc660904925fa1c",
                    "freeze_tag": "p5y-k1r-preregistration-frozen",
                    "checkpoint_sha256": "1c57104b74d44a092619609e7bd39df3e82cf054d575abce7e1862e5095279c7",
                    "source_manifest_sha256": "05e4df96699c9d2b88df1188c40d79fccf054c7e4b1b288c52cdefb3b8b14482",
                    "halt_commit": "adad61f",
                    "final_state": "HALTED_BY_GOVERNANCE after B1 PASS",
                    "halt_gate": "G_GOVERNANCE",
                    "modification": "PROHIBITED; the halt is not erased or rewritten"},
            "b1": {"route": "AUX5_COMPOSITE_ADMISSION", "admission_a1_a10": "PASS",
                   "scientific_status": "PASS", "obligations": "1304/1304 PASS",
                   "fallback_run": False, "rerun": "PROHIBITED",
                   "aux5_admission": "CLOSED; not reopened",
                   "result_sha256": "41fd34c6ede08b358c9b897f82662e9dd258d3c1619464a47e7f568ebf9f37bb",
                   "status": "INHERITED_PASS"},
            "lineage": {"P5": "PARTIAL", "P5X": "PARTIAL", "P5Y_K1": "PARTIAL",
                        "K1R": "HALTED_BY_GOVERNANCE after B1 PASS",
                        "K1R2": "bridge-executor successor",
                        "rewrite_of_k1r_as_pass_or_closed": "PROHIBITED"},
            "temporal": {"bridge_scientific_results_before_k1r2_freeze": 0,
                         "k1r2_changes": "execution and governance identity for the frozen "
                                         "bridge cells ONLY",
                         "scientific_domains": "INHERITED UNCHANGED",
                         "theorem_target": "INHERITED UNCHANGED"}}


def cost_accounting() -> dict:
    return {"schema": "rebaseguard.p5y.k1r2.cost-accounting.v1",
            "cap_cpu_h_shared_with_k1r": COST_CAP_CPU_H,
            "consumed_new_cpu_h": 0.0,
            "k1r_consumed_cpu_h": 0.0,
            "expected": {"cusum_bridge_cpu_h": 1.264, "sr_bridge_cpu_h": 76.23,
                         "geometry_witness_cpu_h": 0.0,
                         "total_expected_cpu_h": 77.494},
            "non_production": ["cover-geometry witnesses (192-bit resolvent bounds)",
                               "qualification and preflight"],
            "enforcement": "the frozen K1R G_COST gate applies unchanged: halt BEFORE the cap"}


def main() -> int:
    CFG.mkdir(parents=True, exist_ok=True)
    w = geometry_witnesses()
    tabs = cell_tables(w)
    ker = kernel_identity()
    arts = {
        "BRIDGE_GEOMETRY_WITNESS.json": w,
        "CUSUM_BRIDGE_CELL_TABLE.json": tabs["CUSUM"],
        "SR_BRIDGE_CELL_TABLE.json": tabs["SR"],
        "CUSUM_BRIDGE_PRODUCER_CONTRACT.json": cusum_producer_contract(tabs["CUSUM"], ker),
        "SR_BRIDGE_AUTHORIZATION.json": sr_authorization(tabs["SR"]),
        "SR_BRIDGE_OWNERSHIP.json": sr_ownership(tabs["SR"]),
        "RUNTIME_CONTRACT.json": runtime_contract(ker),
        "PREDECESSOR_BINDING.json": predecessor_binding(),
        "COST_ACCOUNTING.json": cost_accounting(),
    }
    hashes = {}
    for name, body in arts.items():
        (CFG / name).write_bytes(canon(body))
        hashes[name] = sha_file(CFG / name)
    ck = {"schema": "rebaseguard.p5y.k1r2.cusum-bridge-checkpoint.v1",
          "producer": "K1R2-CUSUM-BRIDGE",
          "geometry": {"cells_sha256": hashes["CUSUM_BRIDGE_CELL_TABLE.json"],
                       "witness_sha256": hashes["BRIDGE_GEOMETRY_WITNESS.json"],
                       "cell_count": 2, "bridge_only": True},
          "kernel_identity_sha256": ker["kernel_identity_sha256"],
          "precision_bits": PRECISION_BITS, "target": q(TARGET),
          "m_universe": list(M_UNIVERSE), "b_cover_cap": q(B_COVER_CAP),
          "producer_contract_sha256": hashes["CUSUM_BRIDGE_PRODUCER_CONTRACT.json"],
          "frozen_spec_cells_sha256": ker["frozen_spec_cells_sha256"],
          "historical_producer_identity_modified": False,
          "result_bearing": False}
    (CFG / "CUSUM_BRIDGE_CHECKPOINT.json").write_bytes(canon(ck))
    hashes["CUSUM_BRIDGE_CHECKPOINT.json"] = sha_file(CFG / "CUSUM_BRIDGE_CHECKPOINT.json")
    cp = {"schema": "rebaseguard.p5y.k1r2.checkpoint.v1", "campaign": "P5Y-K1R2",
          "purpose": "authorize and qualify execution of the already-frozen B2/B3 bridge cells",
          "result_bearing": False, "production_started": False,
          "bridge_results_present": False,
          "inherited_unchanged": {"cusum_domain": {"lo": q(C_CUSUM), "hi": q(CLOSE_CUSUM),
                                                   "cells": 2},
                                  "sr_domain": {"lo": q(C_SR), "hi": q(CLOSE_SR), "cells": 6},
                                  "m_universe": list(M_UNIVERSE), "target": q(TARGET),
                                  "precision_bits": PRECISION_BITS,
                                  "b_cover_cap": q(B_COVER_CAP),
                                  "cost_cap_cpu_h": COST_CAP_CPU_H},
          "frozen_artifacts": hashes,
          "k1r2_status": "QUALIFICATION ONLY; no bridge computation has run",
          "k1_status": "PARTIAL (unchanged)",
          "k1r_status": "HALTED_BY_GOVERNANCE after B1 PASS (unchanged)"}
    (CFG / "CHECKPOINT.json").write_bytes(canon(cp))
    h = sha_file(CFG / "CHECKPOINT.json")
    (CFG / "CHECKPOINT_HASH").write_text(h + "\n")
    for n, v in sorted(hashes.items()):
        print(f"  {n:<38} {v[:16]}")
    print(f"  {'CHECKPOINT.json':<38} {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
