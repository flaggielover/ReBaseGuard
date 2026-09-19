"""Write config/SUCCESSOR_PROTOCOL.json: every load-bearing file of the successor pinned by sha256.

    python3 -B code/make_protocol.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
NS_REL = "level4/closure_proofs/p5y_k5_perron_deflated_resolvent"
CP = "level4/closure_proofs/"
OWN = ["code/deflated_consume.py", "code/taboo_certify.py", "code/build_registry.py", "code/qualify_ad.py",
       "code/gate_eval.py", "code/xcheck_registry.py", "code/qualify_successor.py", "code/operator_float_diagnostic.py",
       "code/make_protocol.py", "theorem/THEOREM_AD.md", "theorem/OPERATOR_AUDIT.md",
       "K5_PERRON_DEFLATED_SUCCESSOR_SPEC.md", "config/FEASIBILITY_GATES.json",
       "evidence/OPERATOR_FLOAT_PROFILE_deg20.json", "evidence/registry_r1/REGISTRY.json"]
PRED = [CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py",
        CP + "p5y_k5_remaining_cell_closure/transport_extension/code/text_consume.py",
        CP + "p5y_k5_remaining_cell_closure/transport_extension/evidence/qualification_r1/TEXT_RESULT.json",
        CP + "p5y_k5_remaining_cell_closure/transport_extension/evidence/consumption_r1/TEXT_CONSUMPTION.json",
        CP + "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json",
        CP + "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
        CP + "p5y_k1_cover_ledger_successor/config/cells.json",
        CP + "p5y_k5b_independent_countersignature/code/k5b_check.py",
        CP + "p5y_k5_order3_readiness_audit/code/k5_minimality.py",
        CP + "p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md",
        CP + "p5y_k5_cusum_order3_r3_infrastructure/code/resolvent_certificate.py"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()
    pins = {f"{NS_REL}/{rel}": sha(NS / rel) for rel in OWN}
    pins.update({rel: sha(REPO / rel) for rel in PRED})
    proto = {"schema": "rebaseguard.p5y.k5.perron-deflation.successor-protocol.v1",
             "successor": "K5_PERRON_DEFLATED_SUCCESSOR", "rule": "r2",
             "registry": f"{NS_REL}/evidence/registry_r1/REGISTRY.json",
             "registry_artifacts_dir": f"{NS_REL}/evidence/registry_r1",
             "domain": [0, 148], "new_real_scientific_addresses": 0,
             "evaluation": "code/deflated_consume.py consume --protocol-sha256 <sha of this file> (twice; byte-identical)",
             "seal_rule": "the consumption result is committed with its sha256 before any interpretation",
             "pins": pins}
    out = NS / "config/SUCCESSOR_PROTOCOL.json"
    out.write_text(json.dumps(proto, indent=1, sort_keys=True) + "\n")
    print(out, sha(out), len(pins), "pins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
