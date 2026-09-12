"""Emit OPS_SOURCE_MANIFEST for the RECOVERY namespace.

verify_ops_source() resolves man["files"] relative to OPS_NS -- this namespace -- so the
adapter's byte-identical copy is the wrong manifest here. Same rule as the contract:
the manifest's own hash lives OUTSIDE it, in OPS_SOURCE_MANIFEST_HASH.
"""
import hashlib, json, sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
# exactly the files verify_ops_source must pin: the operational code path.
PATTERNS = ("ops/*.py", "driver/*.py")


def main() -> int:
    files = {}
    for pat in PATTERNS:
        for p in sorted(NS.glob(pat)):
            files[str(p.relative_to(NS))] = hashlib.sha256(p.read_bytes()).hexdigest()
    man = {"schema": "rebaseguard.p5y.k1.ps1.recovery-ops-source-manifest.v1", "files": files}
    out = NS / "config" / "OPS_SOURCE_MANIFEST.json"
    payload = (json.dumps(man, indent=1, sort_keys=True) + "\n").encode()
    out.write_bytes(payload)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    (NS / "config" / "OPS_SOURCE_MANIFEST_HASH").write_text(digest + "\n")
    print(f"wrote {out}")
    print(f"  files pinned : {len(files)}")
    print(f"  manifest sha : {digest}  (== sha256 of the written file)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
