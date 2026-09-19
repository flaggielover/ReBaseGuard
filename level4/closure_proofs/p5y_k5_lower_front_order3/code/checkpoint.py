"""Write a machine-readable campaign checkpoint (resume aid; never evidence).

    python3 -B code/checkpoint.py --name CP_000_phase_a --stage ... --status ... --next ... \
        [--inputs a,b] [--outputs c,d] [--cpu-hours X] [--new-real-cpu-hours Y] [--open m1=..,m2=..,m3=..,m5=..]
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    for k in ("name", "stage", "status", "next"):
        ap.add_argument(f"--{k}", required=True)
    ap.add_argument("--inputs", default="")
    ap.add_argument("--outputs", default="")
    ap.add_argument("--cpu-hours", default="0")
    ap.add_argument("--new-real-cpu-hours", default="0")
    ap.add_argument("--open", default="")
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

    def hashes(csv):
        out = {}
        for rel in [x for x in csv.split(",") if x]:
            p = NS / rel
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
        return out
    rec = {"schema": "rebaseguard.p5y.k5.lower-front-order3.checkpoint.v1",
           "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "head": head, "stage": a.stage, "status": a.status, "inputs": hashes(a.inputs),
           "outputs": hashes(a.outputs), "compute_cpu_hours": a.cpu_hours,
           "new_real_cpu_hours": a.new_real_cpu_hours,
           "open_cells": dict(x.split("=", 1) for x in a.open.split(",") if x), "next_authorized_stage": a.next,
           "note": a.note}
    # after the freeze (protocol present) only evidence/tc_r1/ may change (review r3 N-R3-2)
    base = NS / "evidence/tc_r1/checkpoints" if (NS / "config/TC_PROTOCOL.json").exists() else NS / "checkpoints"
    base.mkdir(parents=True, exist_ok=True)
    out = base / f"{a.name}.json"
    out.write_text(json.dumps(rec, sort_keys=True, indent=1) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
