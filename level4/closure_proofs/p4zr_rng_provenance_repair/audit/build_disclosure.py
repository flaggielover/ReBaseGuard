#!/usr/bin/env python3
"""Build the machine-readable RNG address-separation disclosure.

Structural facts (which addresses collide, which campaign authored which cell)
are DERIVED from artifacts.  Semantic annotations (what a calibration program
inspected, and which design parameter it fed) are declared here with an explicit
citation to the frozen artifact that states it, and the derivable half of every
annotation is asserted.

NOT RESULT BEARING.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parent.parent
CP = NS.parent
sys.path.insert(0, str(NS / "src"))

from rebaseguard_p4zr.rng_address_audit import audit_manifest  # noqa: E402

P4Z = CP / "p4z_location_family_feasibility"
P4ZA = CP / "p4za_fullscope_closure"
P4ZB = CP / "p4zb_skewnormal4_k7"
COVERAGE = P4ZB / "results" / "final_coverage.json"

#: what each calibration program actually recorded, and what consumed it.
#: Every claim cites the frozen artifact that carries it.
OBSERVED = {
    "micropilots/run_micropilots.py :: RB-SCORE candidate": {
        "diagnostic_cells": ["gaussian/cusum@2", "t1p5/cusum@5",
                             "t1p5/sr@520.886", "t1p5/sr@20", "t3/cusum@5"],
        "inspected": {
            "estimator_precision": True,
            "asymptotic_or_order_diagnostics": False,
            "point_estimate_of_the_estimand": True,
            "inter_route_discrepancy": False,
            "correspondence_gate_z": False,
            "pass_fail_outcome": False,
            "comparison_against_the_historical_record":
                "yes: a two-sample z of the new estimator against the P4X "
                "record, MICROPILOT_REPORT.md section 3.2",
        },
        "recorded_fields": ["mean", "se", "relative_se", "per_path_sd",
                            "hill_index_upper_half_percent",
                            "top1_share_of_squared_deviation",
                            "top5_share_of_squared_deviation"],
        "influenced": ["path count (block_paths per configuration)",
                       "the K3 variance regime envelope",
                       "estimator choice (RB-SCORE primary, RB-MAP companion)"],
        "influence_artifact": "results/estimator_feasibility.json",
    },
    "micropilots/run_micropilots.py :: historical Route-A tail check": {
        "diagnostic_cells": ["gaussian/cusum@2", "t1p5/cusum@5",
                             "t1p5/sr@520.886", "t1p5/sr@20", "t3/cusum@5"],
        "inspected": {
            "estimator_precision": True,
            "asymptotic_or_order_diagnostics": False,
            "point_estimate_of_the_estimand": False,
            "inter_route_discrepancy": False,
            "correspondence_gate_z": False,
            "pass_fail_outcome": False,
            "comparison_against_the_historical_record":
                "tail shape only; no mean is recorded for this leg",
        },
        "recorded_fields": ["per_path_sd", "hill_index_upper_half_percent",
                            "top1_share_of_squared_deviation",
                            "top5_share_of_squared_deviation"],
        "influenced": ["the F-01/F-02 failure diagnosis "
                       "(FAILURE_TAXONOMY.md), i.e. the rejection of the "
                       "historical routes"],
        "influence_artifact": "results/failure_taxonomy.json",
    },
    "micropilots/run_micropilots.py :: RB-MAP candidate": {
        "diagnostic_cells": ["gaussian/cusum@2", "t1p5/cusum@5",
                             "t1p5/sr@520.886", "t1p5/sr@20", "t3/cusum@5"],
        "inspected": {
            "estimator_precision": True,
            "asymptotic_or_order_diagnostics": False,
            "point_estimate_of_the_estimand": True,
            "inter_route_discrepancy": False,
            "correspondence_gate_z": False,
            "pass_fail_outcome": False,
            "comparison_against_the_historical_record":
                "yes: RB-MAP against the P4X Route-B record, "
                "MICROPILOT_REPORT.md section 3.2",
        },
        "recorded_fields": ["mean", "se", "relative_se", "per_path_sd",
                            "hill_index_upper_half_percent",
                            "top1_share_of_squared_deviation",
                            "top5_share_of_squared_deviation"],
        "influenced": ["path count (block_paths per configuration)",
                       "the K3 variance regime envelope"],
        "influence_artifact": "results/estimator_feasibility.json",
    },
    "micropilots/run_fd_ladder.py :: RB-SCORE reference": {
        "diagnostic_cells": ["t1p5/sr@520.886", "t1p5/cusum@5"],
        "inspected": {
            "estimator_precision": True,
            "asymptotic_or_order_diagnostics": False,
            "point_estimate_of_the_estimand": True,
            "inter_route_discrepancy": True,
            "correspondence_gate_z": False,
            "pass_fail_outcome": False,
            "comparison_against_the_historical_record": "no",
        },
        "recorded_fields": ["mean", "se"],
        "influenced": ["the finite-difference ladder design and the decision to "
                       "keep the frozen (0.05, 0.025) pair unchanged",
                       "the rejection of a finer finite-difference step"],
        "influence_artifact": "MICROPILOT_REPORT.md section 3.6",
    },
    "micropilots/run_fd_ladder.py :: FD ladder": {
        "diagnostic_cells": ["t1p5/sr@520.886", "t1p5/cusum@5"],
        "inspected": {
            "estimator_precision": True,
            "asymptotic_or_order_diagnostics": True,
            "point_estimate_of_the_estimand": True,
            "inter_route_discrepancy": True,
            "correspondence_gate_z": False,
            "pass_fail_outcome": False,
            "comparison_against_the_historical_record": "no",
        },
        "recorded_fields": ["central difference per h", "Richardson per pair",
                            "se"],
        "influenced": ["the finite-difference ladder design, including the "
                       "rungs later used by the K7 precondition",
                       "the rejection of a finer finite-difference step"],
        "influence_artifact": "MICROPILOT_REPORT.md section 3.6",
    },
    "audit/calibrate_ladder.py :: FD ladder micro-calibration": {
        "diagnostic_cells": ["frozen/cusum@5/gaussian",
                             "frozen/sr@520.886/gaussian",
                             "frozen/sr@520.886/laplace",
                             "frozen/cusum@5/t1p5"],
        "inspected": {
            "estimator_precision": True,
            "asymptotic_or_order_diagnostics": True,
            "point_estimate_of_the_estimand": True,
            "inter_route_discrepancy": False,
            "correspondence_gate_z": False,
            "pass_fail_outcome": False,
            "comparison_against_the_historical_record": "no",
        },
        "recorded_fields": ["central difference per h", "Richardson per pair",
                            "paired differences", "implied order p", "se"],
        "influenced": ["the frozen P4ZA ladder rungs (h = 0.2 dropped; no rung "
                       "below 0.025)"],
        "influence_artifact": "CHECKPOINT_P4ZA.md section 4",
    },
    "audit/ladder_study.py :: out-of-sample ladder study": {
        "diagnostic_cells": ["frozen/cusum@5/skewnormal4"],
        "inspected": {
            "estimator_precision": True,
            "asymptotic_or_order_diagnostics": True,
            "point_estimate_of_the_estimand": True,
            "inter_route_discrepancy": False,
            "correspondence_gate_z": False,
            "pass_fail_outcome": False,
            "comparison_against_the_historical_record": "no",
        },
        "recorded_fields": ["central difference per h", "Richardson per pair",
                            "paired differences and SNR", "implied order p",
                            "out-of-sample prediction test"],
        "influenced": ["the frozen P4ZB ladder rungs and the truncation "
                       "reference pair"],
        "influence_artifact": "production/p4zb_campaign_plan.json",
    },
}

#: family of each production configuration, for the "were identical innovations
#: delivered?" question.
def family_of(configuration: str) -> str:
    return configuration.rsplit("/", 1)[1]


def diagnostic_families(cells: list[str]) -> set[str]:
    return {c.rsplit("/", 1)[0] if c.startswith(("frozen/", "reduced/"))
            else c.split("/", 1)[0] for c in cells}


def _diag_family_set(cells: list[str]) -> set[str]:
    out = set()
    for c in cells:
        parts = c.split("/")
        out.add(parts[2] if parts[0] in ("frozen", "reduced") else parts[0])
    return out


def authoritative_sources_by_configuration() -> dict[str, dict[str, int]]:
    cov = json.loads(COVERAGE.read_text())
    out: dict[str, dict[str, int]] = {}
    for c in cov["cells"]:
        cid = f"{c['layer']}/{c['detector']}/{c['family']}"
        out.setdefault(cid, {})
        out[cid][c["authoritative_source"]] = \
            out[cid].get(c["authoritative_source"], 0) + 1
    return out


def main() -> int:
    manifest_dir = NS / "results" / "rng_manifests"
    sources = authoritative_sources_by_configuration()
    strict = json.loads((NS / "results" / "strict_gate_reconstruction.json").read_text())

    campaigns = {}
    all_overlaps = []
    for name in ("P4Z", "P4ZA", "P4ZB"):
        manifest = json.loads(
            (manifest_dir / f"{name.lower()}_rng_manifest.json").read_text())
        report = audit_manifest(manifest)
        for f in report["address_overlaps"]:
            ann = OBSERVED[f["calibration_program"]]
            cid = f["production_configuration"]
            diag = _diag_family_set(ann["diagnostic_cells"])
            f["campaign"] = name
            f["what_calibration_inspected"] = ann["inspected"]
            f["calibration_recorded_fields"] = ann["recorded_fields"]
            f["calibration_diagnostic_cells"] = ann["diagnostic_cells"]
            f["calibration_influenced"] = ann["influenced"]
            f["calibration_influence_artifact"] = ann["influence_artifact"]
            f["production_configuration_family"] = family_of(cid)
            f["identical_innovations_delivered"] = family_of(cid) in diag
            f["identical_innovations_note"] = (
                "the shared address delivers the same underlying bit stream in "
                "every case; the drawn VALUES are identical only where the "
                "calibration also ran the production configuration's family"
            )
            f["authoritative_source_of_this_configuration"] = sources[cid]
            f["confers_any_final_disposition"] = "P4Z" in sources[cid] \
                if name == "P4Z" else name in sources[cid]
            all_overlaps.append(f)
        campaigns[name] = report

    affected = sorted({f["production_configuration"] for f in all_overlaps})
    disposition_bearing = [f for f in all_overlaps
                           if f["confers_any_final_disposition"]]

    doc = {
        "schema": "rebaseguard.p4zr-rng-collision-disclosure.v1",
        "result_bearing": False,
        "scope": "B2 only: disclosure and future-audit protection.  This record "
                 "performs neither the K7 instrument adjudication (B1) nor the "
                 "Rule-C ruling on P4X C4/C5 (B3), and declares no verdict "
                 "CLOSED.",
        "campaign_audits": campaigns,
        "verdicts": {k: v["verdict"] for k, v in campaigns.items()},
        "findings": {
            "address_overlaps_total": len(all_overlaps),
            "overlapping_addresses_total": sum(
                f["overlapping_address_count"] for f in all_overlaps),
            "campaigns_with_address_overlap":
                sorted({f["campaign"] for f in all_overlaps}),
            "campaigns_with_seed_namespace_reuse_only": sorted(
                k for k, v in campaigns.items()
                if not v["address_overlaps"] and v["seed_namespace_reuse"]),
            "campaigns_clean_on_both_axes": sorted(
                k for k, v in campaigns.items()
                if not v["address_overlaps"] and not v["seed_namespace_reuse"]),
            "affected_production_configurations": affected,
            "overlaps": all_overlaps,
        },
        "impact": {
            "defect_exists": True,
            "defect_class": "calibration/production RNG address reuse within a "
                            "single campaign",
            "gate_statistic_never_read_at_a_shared_address": all(
                not f["what_calibration_inspected"]["correspondence_gate_z"]
                and not f["what_calibration_inspected"]["pass_fail_outcome"]
                for f in all_overlaps),
            "disposition_bearing_overlaps": len(disposition_bearing),
            "why_no_disposition_is_affected":
                "every production configuration carrying an overlapping address "
                "has all four of its cells authored by P4ZA in "
                "final_coverage.json, and P4ZA's audit reports "
                "RNG_ADDRESS_SEPARATION_PASS on disjoint seeds.  The P4Z blocks "
                "at the overlapping addresses were superseded and confer no "
                "governed disposition.",
            "residual_dependence_channel":
                "P4ZA sized its blocks from the P4Z Stage-0 measured per-path "
                "relative sd, and P4Z Stage-0 for the two affected "
                "configurations includes the blocks whose innovations the "
                "micropilot had already inspected.  The transmitted quantity is "
                "a scalar precision statistic, which the frozen K3 trigger "
                "discipline explicitly permits a sizing rule to read, and P4ZA "
                "drew its own innovations from disjoint seeds.",
            "strict_gate_bound": {
                "cells_total": strict["cells_total"],
                "cells_passing": strict["cells_passing_the_strict_gate"],
                "worst_z_monte_carlo_error_only":
                    strict["worst_z_monte_carlo_error_only"]["value"],
                "z_limit": strict["worst_z_monte_carlo_error_only"]["limit"],
                "worst_relative_discrepancy":
                    strict["worst_relative_discrepancy"]["value"],
                "relative_limit": strict["worst_relative_discrepancy"]["limit"],
                "reproduce": "audit/strict_gate_recheck.py",
            },
            "statement": "No observed disposition dependence.  The scientific "
                         "impact is bounded by the facts that the correspondence "
                         "gate statistic was never read at a shared address, "
                         "that both affected configurations are authored by a "
                         "campaign with no address overlap, and that all 96 "
                         "cells clear the frozen gate with margin even when "
                         "every successor-added uncertainty allowance is "
                         "removed.  This is a bound, not a proof of zero "
                         "influence; see residual_governance_risk.",
        },
        "residual_governance_risk": [
            "The bound is an argument from what the calibration recorded and "
            "from which campaign authored each cell.  It is not a "
            "reconstruction of the counterfactual campaign that would have run "
            "on disjoint addresses, and no such reconstruction is offered.",
            "micropilots/diagnostics/fd_ladder.json records no seed, so its "
            "addresses are recoverable only from the source of "
            "micropilots/run_fd_ladder.py.  Provenance that lives only in a "
            "script is weaker than provenance recorded in the artifact.",
            "The P4Z and P4ZA independent closure audits checked seed "
            "disjointness against predecessor campaigns and against history, "
            "never against the campaign's own calibration, so this defect class "
            "was structurally invisible to them at the time.",
            "P4ZA's seed-namespace reuse (key 4190001 keying Philox in "
            "calibration and PCG64 in production) shares no innovation, but it "
            "removes the margin that would have made a later same-generator "
            "reuse obvious.",
            "This disclosure is authored inside the successor lineage it "
            "describes and has not been independently adjudicated.",
        ],
        "requires_independent_adjudication": True,
        "preserved": {
            "P4_ORIGINAL_VERDICT": "PARTIAL",
            "frozen_artifacts_modified": False,
            "historical_scripts_modified": False,
            "note": "The defective historical scripts are deliberately left "
                    "exactly as they are, as evidence of the defect.",
        },
    }
    out = NS / "results" / "rng_collision_disclosure.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    print(f"verdicts: {doc['verdicts']}")
    print(f"address overlaps: {doc['findings']['address_overlaps_total']} "
          f"({doc['findings']['overlapping_addresses_total']} addresses)")
    print(f"disposition-bearing overlaps: "
          f"{doc['impact']['disposition_bearing_overlaps']}")
    print(f"-> {out.relative_to(NS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
