"""Write config/ORDER3_PRODUCER_MANIFEST.json: the order-3 producer's trusted inputs, by exact repository path.

The Aux5 science inputs are NOT re-listed: they are bound transitively by the Aux5 producer manifest v3 artifact
(identity 3692d0fe), whose bytes are bound here and whose own verify()/final_gate run inside certify_real_cell.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
NSREL = "level4/closure_proofs/p5y_k5_cusum_order3_real_producer/"
FILES = [
    NSREL + "code/rung3_engine.py",
    NSREL + "code/rung3_residual.py",
    NSREL + "code/cusum_order3.py",
    NSREL + "code/k1_inputs.py",
    NSREL + "config/REAL_CELL_AUTHORIZATION_REGISTRY.json",
    "level4/closure_proofs/p5y_k1_cusum_aux5_successor/manifests/producer_manifest_v3.json",
    "level4/closure_proofs/p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
    "level4/closure_proofs/p5y_k1_cusum_aux4_fullcover/code/hash_v2.py",
    "level4/closure_proofs/p5y_k1_cusum_aux4_fullcover/code/schema.py",
    "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/checkpoint.json",
    "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json",
    "level4/closure_proofs/p5y_k5_cusum_order3_producer_design/DESIGN.md",
    "level4/closure_proofs/p5y_k5_cusum_order3_producer_design/code/order3_algebra.py",
]


def build() -> dict:
    return {"schema": "rebaseguard.p5y.k5.order3-producer-manifest.v1",
            "producer": "p5y_k5_cusum_order3_real_producer",
            "aux5_producer_identity_hash": "3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19",
            "production_precision_bits": 256,
            "runtime_contract_expected": {"host": "rebaseguard-vultr-02", "prefix": "/root/work/rbg-cusum-aux5-venv",
                                          "python": "3.12.3", "python_flint": "0.9.0", "numpy": "2.5.2",
                                          "binding": "Aux5 manifest_v3 runtime contract, enforced by its gates"},
            "files": {f: hashlib.sha256((REPO / f).read_bytes()).hexdigest() for f in FILES}}


if __name__ == "__main__":
    (NS / "config/ORDER3_PRODUCER_MANIFEST.json").write_text(json.dumps(build(), indent=1, sort_keys=True) + "\n")
