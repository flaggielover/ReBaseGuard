"""Generate every frozen K1R preregistration artifact. Deterministic, exact rationals.

K1R is ADDITIVE to the adjudicated K1 = PARTIAL result. It touches no historical
artifact: not P5, not P5X, not P5Y-K1, not the 369-cell SR PS1 campaign or its final
assembly, not the historical CUSUM completion records.
"""
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"

# ---------------------------------------------------------------- frozen science
M_UNIVERSE = (1, 2, 3, 5)
TARGET = Fr(2)
PRECISION_BITS = 256
B_COVER_CAP = Fr(1, 20)
SR_RHO_CAP = Fr(1, 25)                       # frozen RHO_CAP r_max of the PS1 partition

# frozen splice constants (compact side ends exactly here)
C_CUSUM = Fr(11, 2)
C_SR = Fr(3803026123175981, 562949953421312)
# first e0 where the inherited P5X-T3 majorant is below target for EVERY m
CLOSE_CUSUM = Fr(49750555, 8388608)
CLOSE_SR = Fr(1883835, 262144)


def q(x: Fr) -> str:
    return f"{x.numerator}/{x.denominator}"


def qf(x: Fr) -> dict:
    return {"exact": q(x), "float": float(x)}


def children(lo: Fr, hi: Fr, n: int) -> list:
    """n equal exact-rational children of (lo, hi]; endpoints are exact, never shrunk."""
    w = (hi - lo) / n
    out = []
    for i in range(n):
        a, b = lo + i * w, lo + (i + 1) * w
        out.append({"child": i, "lo": qf(a), "hi": qf(b), "width": qf(b - a),
                    "center": qf((a + b) / 2), "rho": qf((b - a) / 2),
                    "lower_open": True, "upper_closed": True})
    assert out[0]["lo"]["exact"] == q(lo) and out[-1]["hi"]["exact"] == q(hi)
    return out


def domain_cover() -> dict:
    d = {"schema": "rebaseguard.p5y.k1r.domain-cover.v1",
         "ownership_rule": (
             "Exactly one segment CERTIFIES each e. The compact segment owns its closed "
             "upper endpoint c. The bridge owns the open-lower/closed-upper interval "
             "(c, e_close], except the single point e_close, whose certification is owned "
             "by the inherited far field; the bridge's coverage of e_close is retained as "
             "declared REDUNDANT_OVERLAP so no endpoint is ever omitted."),
         "far_field_theorem": "P5X-T3 (inherited, unchanged, NOT modified by K1R)",
         "detectors": {}}
    for det, c, close, ncells, src in (
            ("CUSUM", C_CUSUM, CLOSE_CUSUM, 2, "p5y_k1_cusum_* compact cover, cells 0-325"),
            ("SR", C_SR, CLOSE_SR, 6, "PS1 SR campaign, cells 0-368 (369/369, inherited PASS)")):
        kids = children(c, close, ncells)
        d["detectors"][det] = {
            "segments": [
                {"segment": "COMPACT_INHERITED", "lo": qf(Fr(0)), "hi": qf(c),
                 "closure": "[0, c]", "owns_endpoints": ["0", "c"],
                 "status": "INHERITED_PASS", "source": src, "new_compute": False},
                {"segment": "K1R_BRIDGE", "lo": qf(c), "hi": qf(close),
                 "closure": "(c, e_close]", "owns_endpoints": [],
                 "owns_interior": "(c, e_close)", "cells": ncells,
                 "status": "TO_BE_CERTIFIED_BY_K1R", "new_compute": True,
                 "endpoint_note": "e_close covered redundantly; certified by the far field"},
                {"segment": "FAR_FIELD_INHERITED", "lo": qf(close), "hi": "+infinity",
                 "closure": "[e_close, infinity)", "owns_endpoints": ["e_close"],
                 "status": "INHERITED_PASS_AT_AND_ABOVE_e_close", "new_compute": False,
                 "basis": ("P5X-T3 majorant is monotone decreasing in e and is strictly "
                           "below target 2 for every m at e_close")}],
            "children": kids,
            "gap_free_proof": {
                "compact_hi_equals_bridge_lo": q(c),
                "bridge_hi_equals_far_field_lo": q(close),
                "children_chain_exact": all(kids[i]["hi"]["exact"] == kids[i + 1]["lo"]["exact"]
                                            for i in range(len(kids) - 1)),
                "union": "[0, infinity)", "gaps": [], "omitted_endpoints": [],
                "double_ownership_points": [{"point": q(close), "certifier": "FAR_FIELD_INHERITED",
                                             "redundant_cover": "K1R_BRIDGE"}]},
            "bridge_width": qf(close - c)}
    return d


# ------------------------------------------------------- B1 admission decision tree
AUX5 = {
    "host": "rebaseguard-vultr-02",
    "export_root": "/root/work/postk1-runs/closure-r1",
    "records": "COMPOSITE_EXPORT/k4_records/aux5_CUSUM_<cell>_256.json",
    "export_manifest_sha256": "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334",
    "composite_audit_sha256": "2ec4dcbb9f2bc27568742db053133c01a369863a21f9a4f066471fcd9cb4b670",
    "composite_audit_self_declared_sha256": "fa1d79b52c8ac6014c34ced67f1c53dd862b55c66cd6fcee47ab1797c7404266",
    "k4_attestation_sha256": "039e2e1cbebb9561c177ddca790dbc2c675eafde15553ad4e1282777d9bd8d2c",
    "producer_identity_hash": "3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19",
    "producer_checkpoint_sha256": "f9380847c92b6f5eb014d56021d11c2b66a95bef0990e392c7021c05d537a6cb",
    "halves": {
        "predecessor_cells_0_127": {
            "authorization_id": "CUSUM-AUX5-PROD-AUTH-001",
            "authorization_sha256": "b8f11ec05efc2476f733dd989ae02b542dc9efa374f24fa0a27688d76ec2b329",
            "countersignature_sha256": "1ceb92d463d1332dfb26505143454b3c3fd87a611bc731372d9e227017682b07",
            "production_checkpoint_sha256": "dd4c89d773c411355d93d0d703e40c027f9913e11e116e4bfe35117f84b4baf2",
            "ledger_state_sha256": "b3cee6fff848d55aaba7ae143b43e77563663b929c8f5483d8eeec47875b60cb",
            "integrity_audit_sha256": "67ab1637a260fbcc7def7ce5621d7589de007ea1f0f40dcd3b4a6d8b12dd3834",
            "disposition": "HALTED", "verified_pairs": 128},
        "successor_cells_128_325": {
            "authorization_id": "CUSUM-AUX5-GLIBC-PROD-AUTH-002",
            "authorization_sha256": "0c7621d47fd862e06355276492fe9a425f8fe2eec280d8c7375a4acedaaa043f",
            "countersignature_sha256": "e1ee7fb112c4d013c53f3adf10f12421c04b39f2ec1d3edd98ec2cc07edf143a",
            "production_checkpoint_sha256": "f9380847c92b6f5eb014d56021d11c2b66a95bef0990e392c7021c05d537a6cb",
            "ledger_state_sha256": "241af4f12aa6ee390af6c113cbc262cbefbb9476f6f442be7acfd40f877cffca",
            "integrity_audit_sha256": "fe7d9ed8951b16bc629193848e3a5cb4cc87548e549f32409fe90da8aed532d1",
            "disposition": "COMPLETE", "verified_pairs": 198}},
}

ADMISSION_CONDITIONS = [
    ("A1", "the record universe is exactly the 326 cells 0..325, no more, no fewer",
     "count record files and their cell_index set", "structural"),
    ("A2", "the obligation universe is exactly 1304 = 326 cells x 4 m-values {1,2,3,5}",
     "count obligation slots per record; m-key set equality", "structural"),
    ("A3", "every source hash named by the export manifest and the composite audit resolves",
     "resolve export_manifest_sha256, composite_audit_sha256, k4_attestation_sha256, "
     "both halves' ledger_state/integrity_audit/authorization/countersignature hashes",
     "identity"),
    ("A4", "every record's scientific hash verifies against the export manifest entry",
     "recompute sha256 per record file and compare to the manifest map", "identity"),
    ("A5", "the producer lineage is explicitly identified for every admitted cell",
     "producer_identity_hash + production_checkpoint_sha256 present and equal to the "
     "frozen values for the half that owns the cell", "identity"),
    ("A6", "no post-result editing of scientific values",
     "record hashes equal the hashes recorded by the composite audit taken at closure; "
     "the audit's own digest is unchanged", "identity"),
    ("A7", "the composite construction is result-agnostic by its own declaration",
     "COMPOSITE_AUDIT.result_agnostic is true AND obligation_statuses_read is false AND "
     "K4 attestation k4_values_evaluated is false", "governance"),
    ("A8", "temporal provenance suffices for use as an ADDITIVE successor source",
     "each half carries an authorization AND a countersignature issued before its own "
     "campaign, and the campaign predates the K1R preregistration freeze", "governance"),
    ("A9", "admission is total: the whole 326-cell composite or nothing",
     "no per-cell, per-m or per-half selection is representable in this contract",
     "governance"),
    ("A10", "no host/runtime identity inconsistency that invalidates scientific use",
     "HOST_AT_CLOSURE library/package identities resolve, and the runtime that produced "
     "each half matches the authorization countersigned for that half", "identity"),
]


def b1_contract() -> dict:
    return {
        "schema": "rebaseguard.p5y.k1r.b1-admission-contract.v1",
        "blocker": "B1 - CUSUM compact-cover admission, original cells 319-323 at m=5",
        "historical_mechanism": (
            "B_cover curvature-budget exhaustion under the old cover width: curvature = "
            "M_R2 * w^2 / 8 crossed the frozen 1/20 cap at m=5. NOT an observed "
            "target-bound violation: the enclosures were 0.0991-0.1636 against target 2."),
        "decision_is_outcome_independent": True,
        "decision_inputs_permitted": ["cell/obligation counts", "hash resolution and equality",
                                      "producer and runtime identity", "authorization and "
                                      "countersignature provenance", "self-declared audit mode"],
        "decision_inputs_forbidden": ["any obligation status", "any enclosure value",
                                      "any utilization", "any margin", "any majorant",
                                      "anything that reveals whether a cell passes"],
        "routes": {
            "AUX5_COMPOSITE_ADMISSION": {
                "taken_when": "every condition A1..A10 PASSES",
                "effect": "the 326-cell composite is admitted INDIVISIBLY as the B1 source",
                "new_compute_cpu_h": 0.0,
                "fallback_must_not_run": True},
            "PREREGISTERED_RECOMPUTE_FALLBACK": {
                "taken_when": "any condition A1..A10 FAILS (then zero Aux5 records are admitted)",
                "cells": [319, 320, 321, 322, 323],
                "split": "each original cell exactly once into 2 equal exact-rational children",
                "total_children": 10,
                "m_universe": list(M_UNIVERSE),
                "second_refinement": "PROHIBITED",
                "expected_cpu_h": 3.2,
                "host": "the qualified CUSUM runtime consistent with the selected producer "
                        "lineage; never the Mac"}},
        "conditions": [{"id": i, "statement": s, "check": c, "class": k,
                        "decidable_without_scientific_values": True}
                       for i, s, c, k in ADMISSION_CONDITIONS],
        "all_or_nothing": True,
        "candidate_source": AUX5,
        "disclosed_prior_observation": (
            "During the read-only residual-blocker reconstruction that preceded this "
            "preregistration, the Aux5 record statuses were observed (326/326 cells, "
            "1304/1304 obligations PASS, m=5 utilisation 0.583-0.733 on cells 319-323). "
            "This is disclosed so no reviewer is misled about what was known. It creates no "
            "selection freedom: admission is total under A9, the admission conditions read "
            "no scientific value, and the Aux5 kill gate halts K1R if any admitted "
            "obligation is not PASS."),
    }


# ------------------------------------------------------------------ bridge plans
def bridge_plan(det: str, c: Fr, close: Fr, ncells: int, cost_per_cell_cpu_h: float,
                host: dict, extra: dict) -> dict:
    kids = children(c, close, ncells)
    p = {
        "schema": f"rebaseguard.p5y.k1r.{det.lower()}-bridge-plan.v1",
        "detector": det,
        "domain": {"lo": qf(c), "hi": qf(close), "closure": "(lo, hi]",
                   "width": qf(close - c), "endpoint_shrinkage": "PROHIBITED"},
        "partition": {"cells": ncells, "rule": "equal exact-rational children",
                      "children": kids},
        "theorem_target": {"statement": f"sup |R_{det},m(e)| < 2 on the bridge domain",
                           "target": q(TARGET), "m_universe": list(M_UNIVERSE),
                           "strict": True},
        "precision_bits": PRECISION_BITS,
        "gates": {"B_cover_cap": q(B_COVER_CAP),
                  "inherited_gates": ["B_candidate", "B_cover", "B_interval", "B_kernel",
                                      "B_other", "B_resolvent", "B_rounding",
                                      "nested: aggregate, end, eq, int, round, tail, trunc"],
                  "target_gate": "frozen; unchanged", "correspondence_gates": "frozen; unchanged"},
        "refinement": {"adaptive_refinement_after_results": "PROHIBITED",
                       "max_refinement_depth": 0,
                       "rule": "the partition above is final; a cell that fails its frozen "
                               "certificate budget HALTS K1R and is reported, never re-split"},
        "host_runtime_contract": host,
        "cost": {"expected_cpu_h_per_cell": cost_per_cell_cpu_h,
                 "expected_cpu_h_total": round(cost_per_cell_cpu_h * ncells, 3)},
        "obligations_created": ncells * len(M_UNIVERSE),
    }
    p.update(extra)
    return p


def cusum_bridge() -> dict:
    return bridge_plan(
        "CUSUM", C_CUSUM, CLOSE_CUSUM, 2, 0.632,
        {"host": "the already-qualified CUSUM runtime of the producer lineage selected by "
                 "the B1 admission decision (Aux5 lineage runtime if admitted)",
         "mac_as_producer": "PROHIBITED",
         "runtime_identity_binding": "producer identity + OpenBLAS/FLINT kernel + libc "
                                     "identities must match the selected lineage's frozen values",
         "aws_permitted": True, "vultr_permitted": True,
         "permission_basis": "the CUSUM lineage is qualified on both hosts; SR is not"},
        {"expected_utilisation_note": (
            "predicted m=5 cover utilisation approx 0.19: curvature = M_R2 * w^2 / 8 with "
            "w = 0.21536 and the inherited M_R2 <= 1.0025 measured at compact cell 325; "
            "this is a PREDICTION and is not a gate"),
         "inherited_reference_cell": {"cell": 325, "e_hi": q(C_CUSUM),
                                      "m5_utilisation": 0.08481270408236977,
                                      "m5_M_R2": 1.0025166}})


def sr_bridge() -> dict:
    kids = children(C_SR, CLOSE_SR, 6)
    rho_ok = all(Fr(k["rho"]["exact"]) <= SR_RHO_CAP for k in kids)
    return bridge_plan(
        "SR", C_SR, CLOSE_SR, 6, 12.705,
        {"host": "AWS ONLY", "aws_permitted": True, "vultr_permitted": False,
         "vultr_substitution": "PROHIBITED (cross-host bit identity FAIL; owns no SR cells)",
         "mac_as_producer": "PROHIBITED",
         "executor_identity": "the qualified PS1 SR executor/runtime lineage",
         "executor_source_manifest_files": 39,
         "scientific_adapter_hash": "13ba2ecd1c8afdaafb3463233f246716f599dd935c5b3722f4074327d8eec5fd",
         "producer_commit": "c9b12670d4da677d384747aa703c725c58bac65a",
         "checkpoint_sha256": "1c2a6825f19e19de6fb588647ca3fc4618068087ef0976292ca7bbeca701f13f",
         "permission_basis": "no previously frozen qualification permits another host for SR"},
        {"rho_constraint": {"r_max": q(SR_RHO_CAP), "satisfied_by_every_child": rho_ok,
                            "max_child_rho": max(k["rho"]["float"] for k in kids)},
         "existing_campaign": {"cells": 369, "status": "INHERITED_PASS",
                               "modification": "PROHIBITED - K1R adds a bridge only",
                               "production_ledger_sha256":
                                   "988725cd8dd02d28f52ef18e3b1add8063825cc42ee828c99d556a12b06d0dd8"}})


# ------------------------------------------------------------- gates, cost, checkpoint
KILL_GATES = [
    {"id": "G_SCIENCE", "trigger": "any certified enclosure reaches or exceeds target 2",
     "action": "HALT; record as POTENTIAL_SCIENTIFIC_FAILURE",
     "prohibited_response": "automatic refinement around the failing point"},
    {"id": "G_COVERAGE", "trigger": "any domain gap, endpoint mismatch or partition drift",
     "action": "HALT"},
    {"id": "G_BUDGET", "trigger": "a bridge cell fails its frozen certificate budget while no "
                                  "predeclared refinement is authorised (max depth 0)",
     "action": "HALT"},
    {"id": "G_GOVERNANCE", "trigger": "source hash mismatch, runtime drift, producer mismatch "
                                      "or an unauthorised scientific artifact", "action": "HALT"},
    {"id": "G_AUX5", "trigger": "any Aux5 admission condition fails",
     "action": "admit ZERO Aux5 records, then run the preregistered B1 fallback only"},
    {"id": "G_AUX5_STATUS", "trigger": "an admitted Aux5 obligation is not PASS",
     "action": "HALT (admission is total; a single non-PASS invalidates the admission)"},
    {"id": "G_COST", "trigger": "total NEW K1R compute would exceed 150 CPU-hours",
     "action": "HALT BEFORE exceeding the cap"},
    {"id": "G_SCOPE", "trigger": "any post-result endpoint movement, cell deletion, m deletion, "
                                 "threshold relaxation, precision relaxation, host substitution "
                                 "or theorem narrowing", "action": "HALT"},
]

IMMUTABLE = {
    "P5": "PARTIAL", "P5X": "PARTIAL", "P5Y_K1": "PARTIAL",
    "adjudication": {"K1_THEOREM_SCOPE": "PASS", "PS1_SUCCESSOR_VALIDITY": "PASS",
                     "SR_PS1_K1": "PASS", "K1_GOVERNANCE": "PASS",
                     "CUSUM_K1": "INCOMPLETE", "K1_FAR_FIELD": "FAIL",
                     "K1_FINAL_VERDICT": "K1_PARTIAL",
                     "adjudicated_at_commit": "15e70072ebfb7c0b5863ae8966cdb769d0604535"},
    "rule": "K1R may not restate, weaken or overturn any of the above; it is additive only",
}

INHERITED = {
    "sr_ps1_campaign": {
        "cells": 369, "obligations": 10332, "status": "INHERITED_PASS",
        "production_ledger_sha256": "988725cd8dd02d28f52ef18e3b1add8063825cc42ee828c99d556a12b06d0dd8",
        "predecessor_ledger_sha256": "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab",
        "production_authorization_sha256": "fc7cb93465916c3a7842066701b0e11fb6799bfdfc7fff55073a3f6e4cfc03ef",
        "shard_manifest_sha256": "6450aff37d975a308f5fba5c799ab1163f6f2ab9e678312b53f0ec686b1c9e9c",
        "successor_cells_sha256": "dfaced89653bd71a0bab4a61729407694768456b1e841f042df84c4544bfe349",
        "final_assembly_sha256": "a3ffb9ec89b1c2da255e7d7397399720d3045f53c9d12b1ffba4141c81369860",
        "final_assembly_self_binding": "741fb2b59b8e9139a7c2687d9377db4313853623f53aa0c06b992eedbac4b3e7",
        "assembly_freeze_sha256": "4298716d9158d4f81e33454949ea4ba4e43baa7001ef1b94b800d9194044965f",
        "modification": "PROHIBITED"},
    "far_field": {
        "theorem": "P5X-T3", "modification": "PROHIBITED",
        "diagnostics_sha256": "f3266436764435c4649e93a8ffa0827476a866023868181876f3acf6cc8dcb26",
        "k1_self_audit_sha256": "87ea625cf79d632b64ae08594d73323f43b2a3fc0ab8fcd87a39607ac56c0094",
        "at_splice": {"CUSUM": {"all_m_pass": False, "failure_class": "CERTIFICATE_TOO_LOOSE"},
                      "SR": {"all_m_pass": False, "failure_class": "CERTIFICATE_TOO_LOOSE"}},
        "all_m_close": {"CUSUM": {"e0": q(CLOSE_CUSUM), "majorant_at_minimum": 1.9999988906443582},
                        "SR": {"e0": q(CLOSE_SR), "majorant_at_minimum": 1.9999984076818382}}},
    "cusum_historical": {
        "k1_cited_lineage": "p5y_k1_cusum_completion_successor",
        "k1_commit": "f8e6f7583e798813c7f7e0dc8b952488c2a06a7e",
        "failed_obligations": [{"cell": c, "m": 5, "status": "FAIL", "utilisation": u}
                              for c, u in ((319, 1.152916), (320, 1.257775), (321, 1.335284),
                                           (322, 1.238998), (323, 1.042928))],
        "modification": "PROHIBITED"},
}


def cost_cap() -> dict:
    return {"schema": "rebaseguard.p5y.k1r.cost-cap.v1",
            "cap_cpu_h": 150.0, "consumed_new_cpu_h": 0.0,
            "expected": {"cusum_bridge_cpu_h": 1.264, "sr_bridge_cpu_h": 76.23,
                         "b1_admission_cpu_h": 0.0, "b1_fallback_if_needed_cpu_h": 3.2,
                         "total_expected_cpu_h": 77.494,
                         "total_expected_with_fallback_cpu_h": 80.694},
            "accounting_rule": ("only NEW K1R production counts; inherited evidence and "
                               "admitted Aux5 records contribute zero; verification and "
                               "preflight are not production"),
            "enforcement": "G_COST halts BEFORE the cap is exceeded, never after",
            "authority": "K1R has no claim on the PS1 6600 CPU-h cap; this is its own envelope"}


def checkpoint(parts: dict) -> dict:
    return {"schema": "rebaseguard.p5y.k1r.checkpoint.v1",
            "campaign": "P5Y-K1R", "result_bearing": False,
            "purpose": "close exactly B1, B2, B3 and nothing else",
            "blockers": {"B1": "CUSUM compact-cover admission (cells 319-323, m=5)",
                         "B2": f"CUSUM bridge ({q(C_CUSUM)}, {q(CLOSE_CUSUM)}]",
                         "B3": f"SR bridge ({q(C_SR)}, {q(CLOSE_SR)}]"},
            "immutable_history": IMMUTABLE, "inherited_evidence": INHERITED,
            "m_universe": list(M_UNIVERSE), "detector_universe": ["CUSUM", "SR"],
            "theorem_target": q(TARGET), "precision_bits": PRECISION_BITS,
            "b_cover_cap": q(B_COVER_CAP), "kill_gates": KILL_GATES,
            "frozen_artifacts": parts,
            "production_started": False, "genuine_results_present": False,
            "k1_status_after_k1r_freeze": "K1 remains PARTIAL; K1R decides nothing yet"}


def main() -> int:
    CFG.mkdir(parents=True, exist_ok=True)
    arts = {"DOMAIN_COVER.json": domain_cover(), "B1_ADMISSION_CONTRACT.json": b1_contract(),
            "CUSUM_BRIDGE_PLAN.json": cusum_bridge(), "SR_BRIDGE_PLAN.json": sr_bridge(),
            "COST_CAP.json": cost_cap()}
    hashes = {}
    for name, body in arts.items():
        p = CFG / name
        p.write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
        hashes[name] = hashlib.sha256(p.read_bytes()).hexdigest()
    cp = CFG / "CHECKPOINT.json"
    cp.write_text(json.dumps(checkpoint(hashes), indent=1, sort_keys=True) + "\n")
    h = hashlib.sha256(cp.read_bytes()).hexdigest()
    (CFG / "CHECKPOINT_HASH").write_text(h + "\n")
    for n, v in sorted(hashes.items()):
        print(f"  {n:<28} {v}")
    print(f"  {'CHECKPOINT.json':<28} {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
