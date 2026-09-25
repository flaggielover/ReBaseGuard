"""Pin every successor source file. Hash model A (sha256 of the file bytes)."""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
DIRS = ("code", "driver", "ops", "tests")


def main() -> int:
    files = {}
    for d in DIRS:
        for p in sorted((NS / d).glob("*.py")):
            files[f"{d}/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
    for extra in ("config/ASSEMBLY_CONTRACT.json", "README.md"):
        p = NS / extra
        if p.exists():
            files[extra] = hashlib.sha256(p.read_bytes()).hexdigest()
    man = {"schema": "rebaseguard.p5y.k1.ps1.aws-only-assembly.source-manifest.v1",
           "namespace": NS.name, "files": files}
    out = NS / "config" / "SOURCE_MANIFEST.json"
    out.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    (NS / "config" / "SOURCE_MANIFEST_HASH").write_text(h + "\n")
    print(f"wrote {out}\n  files : {len(files)}\n  sha256: {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
