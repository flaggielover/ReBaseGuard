"""Pin every K1R6 file."""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]


def main() -> int:
    files = {p.relative_to(NS).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(NS.rglob("*")) if p.is_file() and "__pycache__" not in p.as_posix()
             and not p.name.startswith("SOURCE_MANIFEST")}
    out = NS / "config/SOURCE_MANIFEST.json"
    out.write_text(json.dumps({"schema": "rebaseguard.p5y.k1r6.source-manifest.v1", "files": files},
                              indent=1, sort_keys=True) + "\n")
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    (NS / "config/SOURCE_MANIFEST_HASH").write_text(h + "\n")
    print(f"files: {len(files)}\nsha256: {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
