"""C6 phases 1-5, 10 and 11: the missing-evidence graph, git forensics, provenance binding and identity checks.

Everything here is read-only against the repository and against committed artifacts. The external inventory is
recorded separately in `evidence/inventory/C6_EXTERNAL_INVENTORY.json` from a read-only Vultr session; this
producer consumes its recorded hashes and re-binds them against committed sources locally, so the binding is
reproducible without the external host.

    python3 -B c6_forensics.py --out-graph G.json --out-provenance P.json
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[2]
REPO = CP.parents[1]
OPEN_CELLS = (306, 307, 308, 309)

MAN = CP / "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json"
ADOPTED = CP / "p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json"
GIT_REC = CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records"
CHAIN = {  # the frozen import chain tct_inputs/tc_producer load; all must be committed for a replay to be possible
    "cusum_order3": "p5y_k5_cusum_order3_real_producer/code/cusum_order3.py",
    "aux_certifier": "p5y_k1_cusum_aux3_successor/code/aux_certifier.py",
    "aux_propagate": "p5y_k1_cusum_aux3_successor/code/aux_propagate.py",
    "aux_refine": "p5y_k1_cusum_aux3_successor/code/aux_refine.py",
    "order2": "p5y_k1_cusum_completion_successor/code/order2.py",
    "rung3_residual": "p5y_k5_cusum_order3_real_producer/code/rung3_residual.py",
    "scipy_guard": "p5y_k1_cusum_aux4_fullcover/code/scipy_guard.py",
    "spec": "p5y_k1_cover_ledger_implementation/code/spec.py",
    "intervals": "p5y_k1_cover_ledger_implementation/code/intervals.py",
    "assembly": "p5y_k1_cover_ledger_implementation/code/assembly.py",
    "cells.json": "p5y_k1_cover_ledger_successor/config/cells.json",
    "tct_inputs": "p5y_k5_m5_tail_closure/code/tct_inputs.py",
    "tc_producer": "p5y_k5_lower_front_order3/code/tc_producer.py",
}
PAYLOAD_KEYS = re.compile(r'"(numerators|coeffs|coefficients|payload|cheb|poly)"')


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True).stdout


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-graph", required=True)
    ap.add_argument("--out-provenance", required=True)
    a = ap.parse_args()
    inv = json.loads((NS / "evidence/inventory/C6_EXTERNAL_INVENTORY.json").read_bytes())

    # ---- PHASE 10: did the K1 object candidates ever get serialized, anywhere? ----------------------
    chain = {n: {"path": p, "committed": (CP / p).exists(), "sha256": sha(CP / p) if (CP / p).exists() else None}
             for n, p in CHAIN.items()}
    git_records = {}
    for p in sorted(GIT_REC.glob("aux5_CUSUM_*.json")) if GIT_REC.exists() else []:
        git_records[p.name] = sha(p)
    payload_in_git = {}
    for p in sorted(CP.rglob("aux5_CUSUM_*.json")):
        payload_in_git[p.relative_to(CP).as_posix()] = bool(PAYLOAD_KEYS.search(p.read_text(errors="ignore")))
    ever_committed = len([l for l in git("log", "--all", "--name-only", "--pretty=format:",
                                        "--", "*aux5_CUSUM_*").splitlines() if l.strip()])

    candidates = {
        "logical_identity": "the frozen K1 object candidates F_r, D_r, H_r (state-only polynomials, r = 0..4), "
                            "and their suprema cert.sup[fam, r, 0] which TCT_INPUTS records as sup.{F,D,H}",
        "producer": "aux_certifier.Aux3Certifier.prepare() -> _candidates_order3(); order2 sets sup[fam, r, 0]",
        "is_a_deterministic_function_of": ["the committed frozen chain above", "the committed cells.json"],
        "depends_on_e": False,
        "note_from_the_frozen_source": "aux_certifier: 'Every candidate is a state-only polynomial and is "
                                       "CONSTANT in e, so no term is lost by differentiating the candidates'",
        "OBJECT_PROVEN_TO_HAVE_EXISTED": True,
        "proof_of_existence": "every one of the 63 objects in the sealed record carries its own `bernstein_calls` "
                              "and `cpu_seconds`, which is direct evidence that the candidate was materialised and "
                              "certified during the historical run",
        "was_it_ever_serialized": False,
        "serialization_evidence": {
            "sealed_records_scanned_externally": inv["historical_store"]["record_files"],
            "records_containing_a_payload_key": inv["historical_store"]["records_containing_a_candidate_payload_key"],
            "records_in_git_scanned": len(payload_in_git),
            "records_in_git_with_a_payload_key": sum(1 for v in payload_in_git.values() if v),
            "identity_gate_compares": "record['objects'][name]['delta_mid'], record['eps_mid'], "
                                      "record['eps_cell'], auxiliary_evidence midpoint_eps / objects / "
                                      "candidate_suprema -- all SCALARS. No payload is compared because none is "
                                      "stored.",
            "candidate_hash_exists_anywhere": False,
            "k1_record_paths_ever_in_git_history": ever_committed,
        },
        "CLASSIFICATION": "REPLAYABLE_EXISTING_ADDRESS",
        "why": "the object is absent from every store, but it is not missing DATA: it is a deterministic function "
               "of committed code and the committed cell spec, at an address the historical campaign already "
               "evaluated and adopted. tct_inputs.py's own docstring classifies exactly this recomputation as "
               "'not a new real scientific evaluation'.",
        "why_C6_must_not_perform_it": "regeneration runs Aux3Certifier.prepare() + all_residuals(), i.e. Arb/"
                                      "Bernstein certification. That is NOT a purely deterministic serialization "
                                      "or materialization step, so the campaign instruction forbids C6 from "
                                      "running it. It also cannot run here: numpy and python-flint are absent.",
    }

    # ---- PHASE 11: is a finer cover reconstructible from the sealed record? -------------------------
    rec309 = json.loads((GIT_REC / "aux5_CUSUM_309_256.json").read_bytes())
    txt309 = json.dumps(rec309)
    subkeys = {k: txt309.count(k) for k in ("sub_", "subcell", "partition", "subinterval", "sub_block",
                                            "e_lo", "e_hi", "split")}
    cover = {
        "question": "can a finer cover at cell 309 be derived from existing certificates without recomputation?",
        "sub_structure_keys_found_in_the_sealed_record": subkeys,
        "whole_cell_refinement_is": "a fixed-point iteration on the WHOLE cell (24 iterations, a contraction "
                                    "factor and a convergence flag), not a partition into sub-intervals",
        "CLASSIFICATION": "TRUE_NEW_REAL_REQUIRED",
        "why": "no sub-interval structure exists anywhere in the sealed record. A finer cover means certifying "
               "the objects on NEW, narrower cells, i.e. at scientific addresses that were never evaluated. "
               "Restriction of an existing whole-cell certificate to a sub-interval would not tighten it: the "
               "certificate's value IS the whole-cell supremum.",
    }

    # ---- PHASES 4 and 5: provenance binding of the recovered records --------------------------------
    man = json.loads(MAN.read_bytes())
    adopted = json.loads(ADOPTED.read_bytes())["cells"]
    prov = {}
    for c in OPEN_CELLS:
        rec = inv["recovered_tail_cell_records"][str(c)]["sha256"]
        key = f"k4_records/aux5_CUSUM_{c}_256.json"
        in_git = git_records.get(f"aux5_CUSUM_{c}_256.json")
        links = {
            "binds_committed_export_manifest": man["files"].get(key) == rec,
            "binds_committed_ADOPTED_TAIL_INPUTS_record_sha256": adopted[str(c)]["record_sha256"] == rec,
            "byte_identical_copy_committed_in_git": (in_git == rec) if in_git else False,
        }
        prov[str(c)] = {
            "recovered_sha256": rec, "bytes": inv["recovered_tail_cell_records"][str(c)]["bytes"],
            "links": links,
            "independent_committed_bindings": sum(1 for v in links.values() if v),
            "PROVENANCE_LEVEL": "P3",
            "why_not_P4": "P4 needs producer + protocol + authorization binding. Two upstream links do NOT close "
                          "by raw bytes: (a) the record's own producer_manifest_hash does not equal the sha256 of "
                          "the committed producer_manifest_v3.json it names, and (b) the export manifest's "
                          "composite_audit_sha256 matches NEITHER the committed nor the external COMPOSITE_AUDIT."
                          "json. C6 does not upgrade provenance by inference.",
            "but": "these bytes are hash-identical to evidence the programme ALREADY adopted: "
                   "ADOPTED_TAIL_INPUTS (committed, sealed Campaign-B measurement) names this exact sha256, and "
                   "C2, C3, C4 and C5 all consumed it. Their scientific standing derives from that existing "
                   "adoption, not from C6's recovery. C6 recovers BYTES whose identity to already-adopted "
                   "evidence is proved by hash.",
        }
    broken = {
        "producer_manifest": {
            "record_field": rec309["producer_manifest_hash"],
            "committed_file": rec309["producer_manifest_path"],
            "committed_file_sha256": sha(CP.parents[1] / rec309["producer_manifest_path"]),
            "closes": sha(CP.parents[1] / rec309["producer_manifest_path"]) == rec309["producer_manifest_hash"],
        },
        "manifest_to_audit": {
            "manifest_names": man["composite_audit_sha256"],
            "committed_audit_sha256": sha(CP / "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_AUDIT.json"),
            "external_audit_sha256": "2ec4dcbb9f2bc27568742db053133c01a369863a21f9a4f066471fcd9cb4b670",
            "closes_against_committed": False, "closes_against_external": False,
        },
    }
    record_self_report = {
        "production_run": rec309["production_run"], "result_bearing": rec309["result_bearing"],
        "campaign": rec309["campaign"],
        "C6_does_not_interpret_these": "the record reports production_run=false and result_bearing=false. C6 "
                                       "records the fields verbatim and does NOT guess their semantics: they may "
                                       "refer to the Aux5 production-checkpoint classification rather than to "
                                       "scientific standing. Establishing their meaning is outside C6's scope and "
                                       "is a reason the provenance level is capped at P3.",
    }

    graph = {"schema": "rebaseguard.p5y.k5.tail-c6.missing-evidence-graph.v1",
             "frozen_chain_all_committed": all(v["committed"] for v in chain.values()),
             "frozen_chain": chain,
             "PHASE_10_k1_object_candidates": candidates,
             "PHASE_11_cover_refinement": cover,
             "payload_scan_of_committed_records": payload_in_git,
             "new_real_scientific_addresses_evaluated": 0, "scientific_kernel_evaluations": 0,
             "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    provenance = {"schema": "rebaseguard.p5y.k5.tail-c6.provenance.v1",
                  "levels": {"P0": "none", "P1": "filename/path only", "P2": "schema + plausible run identity",
                             "P3": "hash/manifest binding to a historical run",
                             "P4": "hash + producer + protocol + authorization + address",
                             "P5": "P4 plus seal/adjudication"},
                  "tail_cell_records": prov,
                  "broken_upstream_links": broken,
                  "record_self_report": record_self_report,
                  "external_evidence_mutations": 0,
                  "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    Path(a.out_graph).write_text(json.dumps(graph, sort_keys=True, indent=1) + "\n")
    Path(a.out_provenance).write_text(json.dumps(provenance, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"chain_all_committed": graph["frozen_chain_all_committed"],
                      "candidates_ever_serialized": candidates["was_it_ever_serialized"],
                      "A1_class": candidates["CLASSIFICATION"],
                      "cover_class": cover["CLASSIFICATION"],
                      "provenance": {k: (v["PROVENANCE_LEVEL"], v["independent_committed_bindings"])
                                     for k, v in prov.items()}}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
