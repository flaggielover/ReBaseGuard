"""Write config/ORDER3_PRODUCER_MANIFEST_R2.json: the R2 method's trusted inputs by exact path (R1 bound unchanged)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
R = "level4/closure_proofs/p5y_k5_cusum_order3_r2_repair/"
FILES = [R + "code/graded_dag.py", R + "code/cusum_graded.py", R + "config/REAL_CELL_AUTHORIZATION_REGISTRY.json",
         R + "config/OPERATOR_CERTIFICATE_REGISTRY.json", R + "config/FEASIBILITY_CRITERION.json",
         "level4/closure_proofs/p5y_k5_cusum_order3_real_producer/config/ORDER3_PRODUCER_MANIFEST.json",
         "level4/closure_proofs/p5y_k5_cusum_order3_real_producer/code/rung3_engine.py",
         "level4/closure_proofs/p5y_k5_cusum_order3_real_producer/code/rung3_residual.py"]


def build() -> dict:
    return {"schema": "rebaseguard.p5y.k5.order3-r2.producer-manifest.v1",
            "method": "sigma-graded parity-block certified error propagation (graded_dag), on top of R1",
            "production_precision_bits": 256, "precision_escalation_set": [128, 192, 256, 384, 512],
            "required_unbuilt_inputs": ["certified C_o0 operator certificate (OPERATOR_CERTIFICATE_REGISTRY)",
                                        "graded real residual wiring for every DAG equation (cusum_graded)"],
            "files": {f: hashlib.sha256((REPO / f).read_bytes()).hexdigest() for f in FILES}}


if __name__ == "__main__":
    (NS / "config/ORDER3_PRODUCER_MANIFEST_R2.json").write_text(json.dumps(build(), indent=1, sort_keys=True) + "\n")
