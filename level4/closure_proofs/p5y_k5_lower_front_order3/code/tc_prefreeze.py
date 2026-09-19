"""Pre-freeze refusal exercise: with the protocol generated but NOT committed, the real-mode producer must refuse before
any computation. Writes evidence/tc_r1/PREFREEZE_REFUSAL.json (committed with the freeze).

    python -B tc_prefreeze.py --protocol-sha256 SHA
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
RECORDS = Path("/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol-sha256", required=True)
    a = ap.parse_args()
    proto = json.loads((NS / "config/TC_PROTOCOL.json").read_bytes())
    k = 11
    cmd = [sys.executable, "-B", str(NS / "code/tc_producer.py"), "real", "--cell", str(k),
           "--record", str(RECORDS / f"aux5_CUSUM_{k}_256.json"), "--record-sha256", proto["k1_record_sha256"][str(k)],
           "--protocol-sha256", a.protocol_sha256, "--out", "/nonexistent/should_not_be_written.json"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    tracked = subprocess.run(["git", "-C", str(REPO), "ls-files", "--error-unmatch",
                              "level4/closure_proofs/p5y_k5_lower_front_order3/config/TC_PROTOCOL.json"],
                             capture_output=True).returncode == 0
    rec = {"schema": "rebaseguard.p5y.k5.lower-front-order3.prefreeze-refusal.v1",
           "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "head": head, "protocol_sha256": a.protocol_sha256, "protocol_tracked": tracked,
           "command": " ".join(cmd[2:]), "returncode": p.returncode,
           "refused": p.returncode != 0 and "TCProducerRefusal" in p.stderr,
           "message": (p.stderr.strip().splitlines() or [""])[-1]}
    out = NS / "evidence/tc_r1/PREFREEZE_REFUSAL.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, sort_keys=True, indent=1) + "\n")
    print(json.dumps(rec))
    return 0 if rec["refused"] and not tracked else 1


if __name__ == "__main__":
    sys.exit(main())
