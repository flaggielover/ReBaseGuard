"""Build config/TC_PROTOCOL.json (the pre-registration of the theorem-TC successor). Run on rebaseguard-vultr-02 in the
frozen venv, from a clean checkout, BEFORE the freeze commit. The pin list is every repository file the producer and
the consumer actually load (collected from sys.modules after importing the frozen chain) plus every predecessor
artifact and every file of this namespace that the successor executes or reads.

    python -B make_tc_protocol.py --out config/TC_PROTOCOL.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import socket
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
NS_REL = "level4/closure_proofs/p5y_k5_lower_front_order3"
CP = "level4/closure_proofs/"
OWN = ["code/tc_rule.py", "code/tc_producer.py", "code/tc_consume.py", "code/tc_crosscheck.py",
       "code/tc_manufactured.py", "code/tc_qualify.py", "code/tc_run.py", "code/tc_lifecycle_sim.py",
       "code/lower_front_blocker_map.py",
       "theorem/THEOREM_TC.md", "config/FEASIBILITY_GATES_A.json", "phase_a/LOWER_FRONT_BLOCKER_MAP.json",
       "phase_b/ROUTE_COMPARISON.md", "evidence/forecast_r1/ROUTE_FORECAST.json", "evidence/forecast_r1/COST_NOTE.md",
       "TC_SUCCESSOR_SPEC.md", "review/REVIEW_R1.md", "review/REVIEW_R1_DISPOSITION.md", "review/REVIEW_R2.md",
       "review/REVIEW_R2_DISPOSITION.md", "review/REVIEW_BRIEF_R1.md", "review/AUTHORIZATION_BRIEF.md"]
PREDECESSORS = [
    CP + "p5y_k5_perron_deflated_resolvent/evidence/successor_r1/DEFLATED_CONSUMPTION.json",
    CP + "p5y_k5_perron_deflated_resolvent/evidence/successor_r1/K5_COVERAGE_MAP_R3.json",
    CP + "p5y_k5_perron_deflated_resolvent/evidence/successor_r1/adjudication_r1/ADJUDICATION_R1.json",
    CP + "p5y_k5_perron_deflated_resolvent/evidence/registry_r1/REGISTRY.json",
    CP + "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
    CP + "p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md",
    CP + "p5y_k5_remaining_cell_closure/transport_extension/evidence/qualification_r1/TEXT_RESULT.json",
    CP + "p5y_k5_remaining_cell_closure/transport_extension/code/text_consume.py",
    CP + "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json",
    CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py",
    CP + "p5y_k5b_independent_countersignature/code/k5b_check.py",
    CP + "p5y_k5_order3_readiness_audit/code/k5_minimality.py",
    CP + "p5y_k1_cover_ledger_successor/config/cells.json",
    CP + "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
    CP + "p5y_k5_cusum_order3_real_producer/config/ORDER3_PRODUCER_MANIFEST.json",
    CP + "p5y_k1_cusum_aux5_successor/manifests/producer_manifest_v3.json",
]
ADDRESSES = list(range(11, 45))


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def loaded_repo_modules() -> list[str]:
    sys.path.insert(0, str(NS / "code"))
    import tc_producer
    tc_producer._import_chain()
    out = set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        p = Path(f).resolve()
        try:
            rel = p.relative_to(REPO)
        except ValueError:
            continue
        out.add(str(rel))
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import numpy
    import scipy
    import flint
    mods = loaded_repo_modules()
    pins = {}
    for rel in [f"{NS_REL}/{x}" for x in OWN] + PREDECESSORS + mods:
        p = REPO / rel
        if not p.is_file():
            raise SystemExit(f"missing pin target {rel}")
        pins[rel] = sha(p)
    man = REPO / PREDECESSORS[13]
    files = json.loads(man.read_bytes())["files"]
    records = {str(k): files[f"k4_records/aux5_CUSUM_{k}_256.json"] for k in ADDRESSES}
    proto = {
        "schema": "rebaseguard.p5y.k5.lower-front-order3.tc-protocol.v1",
        "successor": "theorem TC (Taylor-cell atom-deflated whole-cell R'' enclosure), Campaign A route TC",
        "theorem": f"{NS_REL}/theorem/THEOREM_TC.md",
        "start_frontier": "7cb01e38e2831983ba8f29b3d8c14c189678e4ac",
        "gates_commit": "e89b33f2925c235c4bac30bdb207ea55141aa08b",
        "feasibility_gate": "STRONG (evidence/forecast_r1/ROUTE_FORECAST.json, frozen rule config/FEASIBILITY_GATES_A.json)",
        "addresses": {"detector": "CUSUM", "cells": ADDRESSES, "m": [1, 2, 3, 5], "count": len(ADDRESSES),
                      "orders": "F_r, dF_r, H_r (reproduction of the adopted K1 candidates) and the order-3 candidate "
                                "G_r at the cell midpoint e0, r = 0..4; no other cell, order or drift"},
        "k1_record_sha256": records,
        "producer": {"code": f"{NS_REL}/code/tc_producer.py", "mode": "real",
                     "frozen_chain": "cusum_order3.Order3Certifier + Aux3 residuals + frozen midpoint DAG, "
                                     "rung3_residual.g_residual; no whole-cell refine2",
                     "precision_bits": 256, "threads": "1 per process (pinned before numpy import)",
                     "identity_gate": "every recomputed K1 object delta_mid, eps_mid node and eps_cell node equals the "
                                      "sealed K1 record exactly at 256 bits; the Aux3 midpoint eps, Aux3 object "
                                      "delta_mid and Aux3 candidate suprema equal the record's 53-bit rendering exactly "
                                      "(the adopted qualify5._aux_record serialised them outside workprec(256)) and the "
                                      "256-bit values are no larger",
                     "real_mode_checks": "protocol committed and pin-exact; namespace clean; QUALIFICATION (QUALIFIED at "
                                         "the freeze) -> AUTHORIZATION (bound to that qualification sha) -> GUARD ALLOW "
                                         "(bound to that authorization sha), committed in that order; runtime equal to "
                                         "this protocol; order-3 producer manifest and Aux5 manifest verify; K1 record sha "
                                         "as pre-registered; no repository module loaded outside the frozen list",
                     "parallel_channel": "the frozen Order3Certifier is called directly (its own real-cell registry "
                                         "stays empty); this protocol's authorization is the governing gate",
                     "published_order3": "only certified quantities: delta_mid(G_r), the certified candidate supremum "
                                         "sup.G (needed by Env4) and the upper bound |Ghat_r(a)|; no uncertified "
                                         "order-3 candidate value is recorded"},
        "consumer": {"code": f"{NS_REL}/code/tc_consume.py", "replay_gate": "empty-TC composition reproduces the "
                     "sealed DEFLATED_CONSUMPTION 5dcc9b7d exactly (rows sha, pass/open ranges, cells 0..159)"},
        "fields": {"per_cell": ["norms.k[0..4]", "norms.j[0..4]", "sup_S0[0..4]", "rho", "e0",
                                "r.{0..4}.{delta_F,delta_D,delta_H,delta_G,eps_src[0..3],sup.{F,D,H,G},H_at_a,"
                                "abs_G_at_a}", "W2.{r:j}", "identity_gate", "runtime_checks", "binding"]},
        "expected_outputs": {"evidence/tc_r1/cells/TC_CELL_<k>.json": "one per address",
                             "evidence/tc_r1/repro/TC_CELL_<11,44>.json": "the pre-registered reproduction",
                             "evidence/tc_r1/TC_INDEX.json": "sha256 of every cell file",
                             "evidence/tc_r1/RUN_LEDGER.jsonl": "START/OUTPUT lines per cell",
                             "evidence/tc_r1/TC_CONSUMPTION.json": "after the seal"},
        "acceptance": ["every address produces exactly one gated real record (identity gate identical)",
                       "the reproduction of cells 11 and 44 is byte-identical to the first run (metadata excluded)",
                       "tc_rule and tc_crosscheck agree exactly on every cell and m",
                       "the consumer replay gate passes and no TC intersection is empty",
                       "A-constants of every address equal the adopted audit values"],
        "budget": {"forecast_new_real_cpu_hours": 16.3, "protocol_cap_new_real_cpu_hours": 24,
                   "campaign_hard_cap_cpu_hours": 40, "workers": 4,
                   "basis": "evidence/forecast_r1/COST_NOTE.md (measured dev replays of cells 11 and 44)"},
        "stopping_rule": "each address is evaluated exactly once (plus the pre-registered 2-cell reproduction); "
                         "no re-run, no additional address, no adaptive choice; any refusal or failed acceptance item "
                         "makes the run VOID (no consumption) and stops Campaign A execution",
        "seal_rule": "cells/, repro/, TC_INDEX.json and RUN_LEDGER.jsonl are committed once (with GUARD back to DENY) "
                     "before any consumption or pass/open inspection, and never modified afterwards",
        "runtime": {"host": socket.gethostname(), "python": platform.python_version(), "numpy": numpy.__version__,
                    "scipy": scipy.__version__, "python_flint": flint.__version__, "venv": sys.prefix},
        "post_freeze_allowed_prefix": f"{NS_REL}/evidence/tc_r1/",
        "qualification_result": f"{NS_REL}/evidence/tc_r1/QUALIFICATION_RESULT.json",
        "loaded_repository_modules": mods,
        "pins": pins,
    }
    Path(a.out).write_text(json.dumps(proto, sort_keys=True, indent=1) + "\n")
    print("pins", len(pins), "modules", len(mods), "sha256", sha(Path(a.out)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
