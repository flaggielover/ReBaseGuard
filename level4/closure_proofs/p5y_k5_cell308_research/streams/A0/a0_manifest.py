"""Stream A0: certs/CERTS_MANIFEST.json -- file name -> sha256 -> size (bytes), plus certifier / drift / rung / claim
read from each certificate, so that the manifest can be committed without the certificate files themselves.

  python3 -I -B -S a0_manifest.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a0_common as A  # noqa: E402


def main():
    rows = {}
    for p in sorted(A.CERTS.glob("*.json")):
        if p.name == "CERTS_MANIFEST.json":
            continue
        raw = p.read_bytes()
        c = json.loads(raw)
        rows[p.name] = {"sha256": A.sha256_bytes(raw), "size": len(raw), "certifier": c.get("certifier"),
                        "selection": c.get("selection"), "drift": c.get("drift"), "hull": c.get("hull"),
                        "N": c.get("N"), "degree": c.get("degree"), "Qbits": c.get("Qbits"),
                        "W_sha256": c.get("W_sha256"), "claim_w_atom": c.get("claim_w_atom")}
    out = {"schema": "A0_CERTS_MANIFEST/1", "n_files": len(rows), "total_bytes": sum(r["size"] for r in rows.values()),
           "latent_proxy": "validation-drift certificate values; stream-internal only (T1/T2)",
           "reverify": "python3 -I -B -S a0_verify.py certs/<file> (exact, no float proposal)", "files": rows}
    A.write_json(A.CERTS / "CERTS_MANIFEST.json", out)
    print(out["n_files"], out["total_bytes"])


if __name__ == "__main__":
    main()
