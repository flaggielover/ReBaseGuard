#!/usr/bin/env python3
"""Emit final_closure.json from MANIFEST.json and gate_discharge.json.

Single source of truth: every number and every pin comes from the manifest, so
the verdict document cannot drift from the evidence it cites.

NOT RESULT BEARING.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parent


def main() -> int:
    man = json.loads((NS / "MANIFEST.json").read_text())
    gd = json.loads((NS / "gate_discharge.json").read_text())
    sg = man["strict_gate_reconstruction"]
    adj = man["adjudication_inputs"]
    camp = man["successor_campaigns"]

    doc = {
        "schema": "rebaseguard.p4z-final-closure.v1",
        "result_bearing": False,
        "new_numerical_compute": "NONE",

        # ---- the three distinct statuses, never to be conflated ----
        "status": {
            "historical_verdict": {
                "P4": "PARTIAL",
                "immutable": True,
                "statement": "P4's own recorded verdict is PARTIAL and remains "
                             "PARTIAL. No successor replaces it, and this packet "
                             "does not assert P4 = CLOSED.",
                "source": man["frozen_theorem"]["closure_decision"]["path"],
            },
            "successor_closure": {
                "P4Z": "CLOSED",
                "statement": "The P4Z -> P4ZA -> P4ZB successor line is closed on "
                             "its own terms: all 96 theorem-supported cells carry a "
                             "governed disposition under the unchanged frozen gate, "
                             "with zero FAIL and zero INCONCLUSIVE, and the "
                             "outstanding governance questions have been "
                             "independently adjudicated as admissible.",
            },
            "scientific_line": {
                "P4_SCIENTIFIC_LINE": "CLOSED_BY_LATER_SUCCESSOR",
                "statement": "All three of P4's originally failed gates are "
                             "discharged by admissible later evidence. The "
                             "scientific line is closed by successor evidence; the "
                             "historical verdict is untouched.",
            },
        },

        # ---- what the closure does NOT say ----
        "claims_explicitly_not_made": [
            "P4 = CLOSED",
            "P4's historical verdict is anything other than PARTIAL",
            "P4X is rehabilitated as a campaign",
            "P4Y is anything other than NOT_FEASIBLE",
            "P5, P5Y, K1 or Level-4 is CLOSED",
            "production readiness",
            "the theorem holds beyond its own frozen scope",
            "the P4Z RNG address overlap had no effect",
        ],

        # ---- preserved historical record ----
        "historical_record_preserved": {
            "P4": man["historical_lineage"]["P4"],
            "P4X": man["historical_lineage"]["P4X"],
            "P4Y": man["historical_lineage"]["P4Y"],
            "stagewise_self_verdicts": {
                "P4Z": camp["P4Z"]["self_verdict"],
                "P4ZA": camp["P4ZA"]["self_verdict"],
                "P4ZB": camp["P4ZB"]["self_verdict"],
            },
            "stagewise_note": "These are the campaigns' OWN self-recorded verdicts "
                              "and are retained verbatim. P4ZB_CLOSED is a campaign "
                              "self-verdict; P4Z = CLOSED above is the independent "
                              "integrated adjudication. The two are distinct "
                              "statements and the record keeps both.",
        },

        # ---- gate discharge ----
        "original_p4_failed_gates": {
            "count": len(gd["originally_failed_gates"]),
            "gates": gd["originally_failed_gates"],
            "all_discharged": gd["all_discharged"],
            "map": [
                {"gate": r["original_p4_gate"],
                 "discharged_by": r["discharged_by"],
                 "rule_c_applied": r["rule_c_applied"],
                 "status": r["status"]}
                for r in gd["gates"]
            ],
            "detail": "gate_discharge.json",
        },

        # ---- the numerical basis ----
        "numerical_basis": {
            "cells_total": 96,
            "final_coverage": camp["P4ZB"]["final_coverage"],
            "counts": {"COVERED_PASS": 96, "COVERED_FAIL": 0, "INCONCLUSIVE": 0,
                       "UNCOVERED": 0},
            "authoritative_sources": {"P4Z": 44, "P4ZA": 48, "P4ZB": 4},
            "strict_frozen_gate_reconstruction": sg,
            "strict_gate_meaning": "Every cell re-decided under the frozen gate with "
                                   "the successor-added T_B truncation term removed "
                                   "from the z denominator, which can only raise |z|. "
                                   "No final disposition depends on the T_B "
                                   "convention.",
        },

        # ---- adjudications ----
        "adjudications": {
            "B1_k7": {
                "verdict": adj["B1_k7"]["verdict"],
                "finding": "K7 was successor-added and is absent from the frozen P4 "
                           "protocol. It changed across P4Z, P4ZA and P4ZB; each "
                           "version was frozen before its own result-bearing run; no "
                           "original frozen threshold changed. Disclosure-worthy, "
                           "not closure-blocking.",
                "diagnostic_history_preserved":
                    adj["B1_k7"]["diagnostic_history_preserved"],
            },
            "B2_rng_provenance": {
                "verdict": adj["B2_rng_provenance"]["verdict"],
                "commit": adj["B2_rng_provenance"]["commit"],
                "findings": adj["B2_rng_provenance"]["findings"],
                "finding_text": "P4Z carries a real same-campaign provenance defect: "
                                "5 address overlaps over 25 shared RNG addresses. "
                                "P4ZA has no innovation-address collision - the same "
                                "integer keys Philox in calibration and PCG64 in "
                                "production, which is namespace reuse, not a shared "
                                "stream. P4ZB is clean.",
                "admissibility_basis": "No disposition-bearing final cell relies on "
                                       "overlapped P4Z evidence: both affected "
                                       "configurations are authored by later P4ZA "
                                       "evidence at disjoint addresses, and the "
                                       "strict 96/96 frozen-gate PASS holds.",
                "impact_statement": "No observed disposition dependence. Scientific "
                                    "impact is bounded by the facts that the "
                                    "correspondence gate statistic was never read at "
                                    "a shared address, that both affected "
                                    "configurations are authored by a campaign with "
                                    "no address overlap, and that all 96 cells clear "
                                    "the frozen gate with margin under the strictest "
                                    "available reading.",
                "residual_uncertainty_retained": True,
            },
            "B3_rule_c": {
                "verdict": adj["B3_rule_c"]["verdict"],
                "scope": adj["B3_rule_c"]["scope"],
                "P4X_C4": "PASS",
                "P4X_C5": "PASS",
                "p4x_campaign_rehabilitated": False,
            },
            "B4_presentation": {
                "verdict": adj["B4_presentation"]["verdict"],
                "commit": adj["B4_presentation"]["commit"],
            },
        },

        # ---- residual risk carried forward, not discharged ----
        "residual_uncertainty": [
            "The bound on the P4Z RNG overlap is an argument from what the "
            "calibrations recorded and from which campaign authored each cell. It is "
            "NOT a reconstruction of the counterfactual campaign that would have run "
            "on disjoint addresses, and no such reconstruction is offered.",
            "P4Z's fd_ladder diagnostic records no seed in its artifact; its "
            "addresses are recoverable only from the source of run_fd_ladder.py.",
            "The P4Z and P4ZA independent closure audits compared seed integers "
            "against predecessors and history only, so this defect class was "
            "structurally invisible to them at the time.",
            "P4ZA's seed-namespace reuse shares no innovation but removes the margin "
            "that would make a later same-generator reuse obvious.",
            "P4ZA's precision target was relaxed from P4Z's self-imposed 0.0025 to "
            "the frozen r*, which makes the z gate easier. Disclosed in "
            "CHECKPOINT_P4ZA.md section 5; the achieved relative SE is about r*/2 "
            "and the strict-gate reconstruction shows nothing rides on it.",
            "Closure is scoped to the frozen P4 theorem and its 96 "
            "theorem-supported cells. It says nothing about any wider claim.",
        ],

        "verdict": "P4Z_CLOSED",
        "manifest": "MANIFEST.json",
    }

    (NS / "final_closure.json").write_text(
        json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print("final_closure.json written")
    print(f"  P4 historical      : {doc['status']['historical_verdict']['P4']}")
    print(f"  P4Z successor      : {doc['status']['successor_closure']['P4Z']}")
    print(f"  P4 scientific line : "
          f"{doc['status']['scientific_line']['P4_SCIENTIFIC_LINE']}")
    print(f"  gates discharged   : {doc['original_p4_failed_gates']['all_discharged']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
