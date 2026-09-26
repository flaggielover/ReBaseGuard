"""Pin every K1R2 source file. Hash model A (sha256 of the file bytes)."""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
EXTRA = ("README.md", "FROZEN_SCOPE.md", "PREREGISTRATION.md",
         "config/BRIDGE_GEOMETRY_WITNESS.json", "config/CUSUM_BRIDGE_CELL_TABLE.json",
         "config/CUSUM_BRIDGE_PRODUCER_CONTRACT.json", "config/CUSUM_BRIDGE_CHECKPOINT.json",
         "config/SR_BRIDGE_CELL_TABLE.json", "config/SR_BRIDGE_AUTHORIZATION.json",
         "config/SR_BRIDGE_OWNERSHIP.json", "config/RUNTIME_CONTRACT.json",
         "config/PREDECESSOR_BINDING.json", "config/COST_ACCOUNTING.json",
         "config/CHECKPOINT.json")


def main() -> int:
    files = {}
    for d in ("code", "ops", "tests"):
        for p in sorted((NS / d).glob("*.py")):
            files[f"{d}/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
    for rel in EXTRA:
        p = NS / rel
        if p.exists():
            files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    out = NS / "config" / "SOURCE_MANIFEST.json"
    out.write_text(json.dumps({"schema": "rebaseguard.p5y.k1r2.source-manifest.v1",
                               "namespace": NS.name, "files": files},
                              indent=1, sort_keys=True) + "\n")
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    (NS / "config" / "SOURCE_MANIFEST_HASH").write_text(h + "\n")
    print(f"files : {len(files)}\nsha256: {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
