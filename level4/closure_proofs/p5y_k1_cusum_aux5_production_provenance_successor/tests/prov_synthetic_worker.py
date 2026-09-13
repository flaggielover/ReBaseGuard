"""SYNTHETIC worker for the provenance successor. NOT SCIENCE.

It reuses the predecessor synthetic worker, unchanged, and adds the three certifier-constant fields the frozen Aux5
certifier emits (production_run, result_bearing, scientific_certification_of_full_cover, all false). The composite
verifier is therefore exercised on the real record shape. Extra behaviours:
  flags_true   result_bearing=true (never emitted by the frozen certifier)
  no_flags     the three fields are absent
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import prov_schema as S                                                      # noqa: E402
sys.path.insert(0, str(S.PRED_NS / "tests"))
import synthetic_worker as SW                                                # noqa: E402
from prod_sealer import hash_modules                                         # noqa: E402
from prov_spec import synthetic_spec                                         # noqa: E402


def main() -> int:
    t0, w0 = time.process_time(), time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", required=True)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text())
    spec = synthetic_spec(cfg)
    out = Path(a.out)
    plan = cfg.get("plan", {}).get(str(a.cell), ["ok"])
    behaviour = plan[min(SW.attempt_number(out, a.cell), len(plan) - 1)]
    SW.burn(float(cfg.get("burn_s", 0.2)))
    if behaviour == "slow":
        time.sleep(float(cfg.get("slow_s", 3.0)))
    if behaviour == "hang":
        while True:
            time.sleep(60)
    if behaviour == "selfkill":
        os.kill(os.getpid(), signal.SIGKILL)
    if behaviour == "fail":
        return 3
    if behaviour == "noout":
        return 0
    base = "ok" if behaviour in ("flags_true", "no_flags", "slow", "write_then_hang", "write_then_selfkill") else behaviour
    rec = SW.build_record(spec, a.cell, t0, w0, behaviour=base)
    if behaviour != "no_flags":
        rec.update(S.CERTIFIER_CONSTANT_FLAGS)
        if behaviour == "flags_true":
            rec["result_bearing"] = True
    if behaviour != "malformed":
        H, _S = hash_modules()
        rec["scientific_content_hash"] = H.record_scientific_hash(rec)
    SW.write_atomic(out, rec)
    if behaviour == "write_then_selfkill":
        os.kill(os.getpid(), signal.SIGKILL)
    if behaviour == "write_then_hang":
        while True:
            time.sleep(60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
