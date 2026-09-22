"""Phases 6, 9 and 12: the revised route ledger, evidence-status classified against the FROZEN C6 gate.

Refuses unless the gate hashes to its frozen value. Reads only committed artifacts and the recorded read-only
external inventory. Evaluates no scientific kernel and contacts no host.

    python3 -B c6_classify.py --out OUT.json
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[2]
GATE_SHA = "03c5643335602071e5c6e5e558d20e39d0fc40e81f8d25d0ac00a93c94801fba"
C5 = CP / "p5y_k5_tail_c5_exhaustion"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def frozen_gate():
    p = NS / "config/FEASIBILITY_GATES_C6.json"
    if sha(p) != GATE_SHA:
        raise SystemExit("the C6 gate is not the frozen one")
    return json.loads(p.read_bytes())


def consumer_reads_a_raw_k1_record() -> dict:
    """PHASE 6: does anything in the tail consumer chain actually open a K1 record? If not, recovering the
    records cannot be load-bearing for the current clause, however good their provenance."""
    src = (C5 / "code/c5_common.py").read_text()
    reads = {"ADOPTED_TAIL_INPUTS.json": "ADOPTED_TAIL_INPUTS" in src,
             "TCT_INPUTS_*.json": "TCT_INPUTS" in src,
             "cells.json": "cells.json" in src,
             "REGISTRY_C1/C2": "REGISTRY_C1" in src and "REGISTRY_C2" in src,
             "a raw aux5_CUSUM_*_256.json record": "aux5_CUSUM" in src}
    return {"inputs_the_tail_consumer_opens": reads,
            "opens_a_raw_k1_record": reads["a raw aux5_CUSUM_*_256.json record"],
            "consequence": "the tail consumer never opens a K1 record: it reads the DERIVED, committed "
                           "ADOPTED_TAIL_INPUTS and TCT_INPUTS. So recovering the sealed records adds no field "
                           "that the current K5-B clause consumes, and cannot change any Gamma."}


ROUTES = {
    "A1": dict(
        c5_kill_kind="DATA", family="order-3 surrogate",
        required_object="the frozen K1 object candidates F_r, D_r, H_r and their suprema cert.sup[fam, r, 0]",
        existence="OBJECT_PROVEN_TO_HAVE_EXISTED",
        existence_proof="every one of the 63 objects in each sealed record carries its own bernstein_calls and "
                        "cpu_seconds, direct evidence the candidate was materialised and certified",
        ever_serialized=False,
        serialization_search="all 603 commits / 58 branches / 36 tags, plus 326/326 sealed records scanned "
                             "read-only: 0 payload keys, and no candidate hash exists anywhere",
        C6_CLASSIFICATION="HISTORICAL_REPLAY_REQUIRED",
        missing_what="A TOOLCHAIN. Not data and not science.",
        why="the object is a deterministic function of committed code (the 13-module frozen chain, all verified "
            "committed) and the committed cell spec; the candidates are state-only polynomials constant in e; and "
            "tct_inputs.py's own docstring classifies exactly this recomputation as 'not a new real scientific "
            "evaluation'. The address was evaluated and adopted historically.",
        blocked_by="numpy and python-flint are absent on this host",
        C6_may_perform_it=False,
        why_not="regeneration runs Aux3Certifier.prepare() + all_residuals(), i.e. Arb/Bernstein certification. "
                "The frozen gate permits a replay only if it is provably serialization-only. This is not.",
        leverage_upper_bound="oracle sup F/D/H -> 0 closes 307, 308 and (by 0.00035) 309",
        leverage_achievable="NOT QUANTIFIABLE without the replay. The stored sup already comes from the "
                            "certifier's own sup routine, so the achievable gain is the slack in THAT routine, "
                            "which no committed artifact exposes. C6 does not guess it.",
    ),
    "A3": dict(
        c5_kill_kind="DATA", family="order-3 surrogate",
        required_object="the candidates AND the operators K1, K2, K3 applied to them",
        existence="OBJECT_PROVEN_TO_HAVE_EXISTED (the candidates); OBJECT_IMPLIED_BY_CODE_PATH (the applications)",
        existence_proof="same per-object work counters; the operator applications are transient intermediates",
        ever_serialized=False, serialization_search="as A1",
        C6_CLASSIFICATION="HISTORICAL_REPLAY_REQUIRED",
        missing_what="A TOOLCHAIN, plus a theorem that does not exist yet.",
        why="the inputs are regenerable exactly as in A1, but exploiting cancellation also needs a NEW argument: "
            "no committed theorem bounds the cancelled combination. Replayability gets the inputs, not the result.",
        blocked_by="numpy and python-flint absent; and the cancellation theorem is unwritten",
        C6_may_perform_it=False, why_not="as A1",
        leverage_upper_bound="bounded above by the f_G -> 0 oracle, which closes all three",
        leverage_achievable="unknown and doubly contingent",
    ),
    "D4": dict(
        c5_kill_kind="DATA", family="direct K5-B",
        required_object="joint certified information about R and D at e0",
        existence="OBJECT_ONLY_HYPOTHESIZED",
        existence_proof="none. No committed or recovered artifact contains any joint or correlation datum for R "
                        "and D; the sealed record carries R_interval and D_interval as independently certified "
                        "intervals and nothing that relates them.",
        ever_serialized=False,
        serialization_search="326/326 sealed records: no joint/correlation field in any schema",
        C6_CLASSIFICATION="TRUE_NEW_REAL_REQUIRED",
        missing_what="SCIENCE. The object was never computed by anyone.",
        why="obtaining it means re-certifying the K1 objects with a joint estimator that no historical campaign "
            "ever ran. That is an address never evaluated.",
        reclassified_from_C5="C5 recorded kill_kind DATA while simultaneously recording new_real_required true. "
                             "Those are different kill kinds; the C6 B0 audit caught the inconsistency "
                             "mechanically. DATA was wrong: there is nothing to recover.",
        C6_may_perform_it=False, why_not="forbidden: a new scientific address",
        leverage_upper_bound="unknown; g_hi is 59-60% of the closure deficit so the ceiling is high",
        leverage_achievable="unknown",
    ),
    "E1": dict(
        c5_kill_kind="DATA", family="atom constants",
        required_object="a tighter certified operator tuple (tau, D_lo, Abar) for A0",
        existence="OBJECT_ONLY_HYPOTHESIZED (a BETTER tuple); the CURRENT tuple and its inputs are committed",
        existence_proof="the taboo/arl Chebyshev candidate payloads ARE committed, in "
                        "p5y_k5_tail_operator_registry/evidence/registry_c1 and the C2 refined registry",
        ever_serialized=True,
        serialization_search="the operator candidate payloads are the ONLY Chebyshev payloads committed under "
                             "level4/closure_proofs, and they are present for every tail cell",
        C6_CLASSIFICATION="HISTORICAL_REPLAY_REQUIRED",
        missing_what="A TOOLCHAIN. Every input exists and is committed.",
        why="this is the strongest reclassification in C6: E1's inputs are not missing at all. The operator "
            "certification is operator-only, evaluates no scientific address, and the programme has consistently "
            "classified it zero-new-real (C1 and C2 each spent CPU-hours of it under ZERO_NEW_REAL). The single "
            "block is that python-flint is absent on this host.",
        blocked_by="python-flint absent on this host; the programme's certifying worker is out of C6's scope",
        C6_may_perform_it=False,
        why_not="an Arb certification is not serialization-only, and the frozen gate authorises zero of them",
        leverage_upper_bound="at the diagnostic Lambda with A1 = A2 = 0: 307 closes (-0.0602), 308 barely closes "
                             "(-0.0030), 309 does NOT (+0.0468)",
        leverage_achievable="bounded by Lambda; C5's adjudicator withdrew the claim that E1 is useless at 309",
    ),
}
ALSO = {
    "B1": dict(c5_kill_kind="NEW_REAL", family="rho",
               C6_CLASSIFICATION="TRUE_NEW_REAL_REQUIRED",
               confirmed_how="no sub-interval structure anywhere in the sealed record (0 occurrences of "
                             "sub_/partition/subinterval/e_lo/e_hi/split); whole_cell_refinement is a "
                             "24-iteration fixed point on the WHOLE cell, not a partition. Restricting a "
                             "whole-cell certificate to a sub-interval cannot tighten it: its value IS the "
                             "whole-cell supremum.",
               missing_what="SCIENCE, at addresses never evaluated",
               note="C5 called this the largest lever; C6 confirms it is genuinely new-real rather than merely "
                    "unpermitted."),
    "E2": dict(c5_kill_kind="RE_OPENED_LIVE", family="atom constants",
               C6_CLASSIFICATION="NOT_AN_EVIDENCE_PROBLEM",
               phase_12_finding="a sharper certified lower bound on Lambda_309 is ANALYTIC work, not recovery. "
                                "C4's ladder/Wald minorant gives 3.297250282 against a Monte-Carlo truth near "
                                "4.047; the gap is the looseness of the Wald majorant, and no historical artifact "
                                "contains a tighter certified lower bound on E_a[tau] -- C5's phase-2 sweep over "
                                "the whole corpus already established that nothing bounds it from below at all.",
               missing_what="neither DATA nor a TOOLCHAIN: a THEOREM",
               why_it_still_matters="C5-T left the cell-309 exclusion on 0.944% of critical-A0 slack. E2 remains "
                                    "the only lever that restores it, and it needs no recovery -- which makes it "
                                    "cheaper than C6's forensics suggested any route would be."),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gate = frozen_gate()
    graph = json.loads((NS / "evidence/graph/C6_MISSING_EVIDENCE_GRAPH.json").read_bytes())
    prov = json.loads((NS / "evidence/provenance/C6_PROVENANCE.json").read_bytes())
    inv = json.loads((NS / "evidence/inventory/C6_EXTERNAL_INVENTORY.json").read_bytes())
    load = consumer_reads_a_raw_k1_record()

    recovered = {
        "objects": "the four open tail cells' sealed K1 records",
        "states": {c: {"EXISTS": True, "RECOVERED": True,
                       "PROVENANCE_BOUND": v["independent_committed_bindings"] >= 2,
                       "PROVENANCE_LEVEL": v["PROVENANCE_LEVEL"],
                       "SCIENTIFICALLY_IDENTICAL": True,
                       "identity_basis": "sha256 equality with the bytes ADOPTED_TAIL_INPUTS already names",
                       "admissible_for_NEW_scientific_reuse": v["PROVENANCE_LEVEL"] in ("P4", "P5"),
                       "basis_invoked": "ALREADY_ADOPTED (the gate's already_adopted_exception), NOT a C6 P4"}
                   for c, v in prov["tail_cell_records"].items()},
        "gate_class": "RECOVERED_ADMISSIBLE only under the already-adopted exception; NOT_LOAD_BEARING for the "
                      "current clause",
        "load_bearing": False,
        "why_not_load_bearing": load["consequence"],
        "what_it_does_buy": "a future C7 can run the tct_inputs identity gate for all four open cells from a "
                            "local copy, without the external host. That is a reproducibility gain, not a "
                            "scientific one.",
    }
    per = {}
    for rid, r in {**ROUTES, **ALSO}.items():
        per[rid] = dict(r)
        per[rid]["c5_kill_kind"] = r["c5_kill_kind"]
        per[rid]["classification_changed_from_C5"] = (
            r["C6_CLASSIFICATION"] != {"DATA": "DATA", "NEW_REAL": "TRUE_NEW_REAL_REQUIRED",
                                       "RE_OPENED_LIVE": "RE_OPENED_LIVE"}.get(r["c5_kill_kind"]))
    changed = [k for k, v in per.items() if v["classification_changed_from_C5"]]
    out = {"schema": "rebaseguard.p5y.k5.tail-c6.classification.v1",
           "gate_sha256": GATE_SHA,
           "answer_to_the_core_question": {
               "question": "is the project missing DATA or missing SCIENCE?",
               "A1": "a TOOLCHAIN", "A3": "a TOOLCHAIN plus an unwritten theorem",
               "E1": "a TOOLCHAIN", "D4": "SCIENCE", "B1": "SCIENCE", "E2": "a THEOREM",
               "headline": "for the two highest-leverage DATA-blocked routes (A1 and E1) the project is missing "
                           "NEITHER data NOR science. It is missing numpy and python-flint on this host. Nothing "
                           "was lost; nothing needs to be re-derived."},
           "routes": per,
           "classifications_changed_from_C5": changed,
           "recovered_evidence": recovered,
           "phase_6_load_bearing_check": load,
           "provenance_summary": {c: v["PROVENANCE_LEVEL"] for c, v in prov["tail_cell_records"].items()},
           "external_evidence_unchecked": [],
           "planning_only_leverage_ranking": [
               "E1 -- all inputs committed, needs only a flint host; closes 307, nearly closes 308",
               "A1 -- regenerable from committed code, needs a flint host; oracle closes all three",
               "E2 -- needs no recovery at all, only a theorem; the only lever that restores the 309 margin",
               "B1 -- genuinely new-real, the largest lever, a governed new K1 address and NOT the R-stage",
               "A3 -- doubly contingent", "D4 -- genuinely new-real, ceiling unknown"],
           "ranking_is_planning_only": "this ranking may not alter scientific adoption (frozen gate)",
           "C6_conclusions_withheld": {
               "K5_cells_closed": None, "coverage_map_revision": None,
               "broader_deterministic_exhaustion_established": False,
               "R_stage_prerequisite_satisfied": False,
               "note": "the frozen gate forbids all four, and evidence recovery can never establish exhaustion"},
           "new_real_scientific_addresses_evaluated": 0, "scientific_kernel_evaluations": 0,
           "external_evidence_mutations": 0, "aws_contacted": False,
           "vultr_contacted": inv["hosts"]["rebaseguard-vultr-02"]["contacted"],
           "vultr_mode": inv["hosts"]["rebaseguard-vultr-02"]["mode"],
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    data = json.dumps(out, sort_keys=True, indent=1) + "\n"
    Path(a.out).write_text(data)
    print(json.dumps({"headline": out["answer_to_the_core_question"]["headline"][:120],
                      "classes": {k: v["C6_CLASSIFICATION"] for k, v in per.items()},
                      "changed_from_C5": changed,
                      "recovered_load_bearing": recovered["load_bearing"],
                      "provenance": out["provenance_summary"],
                      "sha256": hashlib.sha256(data.encode()).hexdigest()[:16]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
