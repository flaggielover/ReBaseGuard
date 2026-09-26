"""Pin every K1R4 file: code, generated stages, config, docs and qualification evidence."""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]


def main() -> int:
    files = {}
    for p in sorted(NS.rglob("*")):
        rel = p.relative_to(NS).as_posix()
        if p.is_file() and "__pycache__" not in rel and not rel.startswith("config/SOURCE_MANIFEST"):
            files[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    out = NS / "config" / "SOURCE_MANIFEST.json"
    out.write_text(json.dumps({"schema": "rebaseguard.p5y.k1r4.source-manifest.v1",
                               "namespace": NS.name, "files": files}, indent=1, sort_keys=True) + "\n")
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    (NS / "config" / "SOURCE_MANIFEST_HASH").write_text(h + "\n")
    print(f"files: {len(files)}\nsha256: {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
