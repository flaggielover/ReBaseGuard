"""SYNTHETIC worker for acceptance tests. NOT SCIENCE.

It writes a structurally complete fixture record stamped SYNTHETIC_FIXTURE_NOT_SCIENCE under a synthetic producer
identity. No certified number is computed and the frozen certifier is never started.

  synthetic_worker.py --cell N --out FILE --config CFG.json

The behaviour for (cell, attempt number) is CFG["plan"][str(cell)][attempt] (the last entry repeats; default "ok"):
  ok                   burn ~burn_s CPU, write the record atomically, exit 0
  slow                 as ok after sleeping slow_s
  fail                 exit 3 without a record
  noout                exit 0 without a record
  malformed            write a record whose scientific hash does not recompute, exit 0
  overclaim            write a valid record claiming 10^6 CPU-s, exit 0
  wrong_identity       write a record under another producer identity, exit 0
  wrong_runtime        write a record under another runtime contract, exit 0
  selfkill             SIGKILL itself before writing
  write_then_selfkill  write the record, then SIGKILL itself
  write_then_hang      write the record, then sleep forever
  hang                 sleep forever without writing
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import tempfile
import time
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
from prod_common import sha256_bytes, canonical                            # noqa: E402
from prod_sealer import PER_M_KEYS, SYNTHETIC_STAMP, hash_modules          # noqa: E402
from prod_spec import CampaignSpec                                         # noqa: E402

PRODUCER_KEYS = ("producer_manifest_hash", "producer_manifest_path", "producer_manifest_schema",
                 "producer_manifest_version", "runtime_contract_hash", "producer_identity_hash",
                 "implementation_hash_kind")


def attempt_number(out: Path, cell: int) -> int:
    return sum(1 for d in out.parent.parent.iterdir() if d.is_dir() and d.name.endswith(f"-C{cell:04d}")) - 1


def burn(seconds: float) -> None:
    t, x = time.process_time(), 0
    while time.process_time() - t < seconds:
        x += 1


def interval(k: int) -> dict:
    return {"encoding": "SYNTHETIC", "lo": f"-{k + 2}/1000", "hi": f"-{k + 1}/1000", "mag": f"{k + 2}/1000"}


def build_record(spec, cell: int, t0: float, w0: float, *, behaviour: str) -> dict:
    geo, ident, runtime = spec.cells[cell], dict(spec.identity), dict(spec.runtime)
    if behaviour == "wrong_identity":
        ident["producer_identity_hash"] = sha256_bytes(b"another producer")
    if behaviour == "wrong_runtime":
        runtime["schema"] = "ANOTHER_RUNTIME"
        ident["runtime_contract_hash"] = sha256_bytes(canonical(runtime))
    m = {}
    for i, key in enumerate(("1", "2", "3", "5")):
        entry = {k: {} for k in PER_M_KEYS}
        entry.update({"C_upper": geo["C_upper"], "D_interval": interval(10 * cell + i),
                      "D_interval_mag": f"{10 * cell + i + 2}/1000", "M_R2": f"{cell + 1}/7",
                      "R2_interval": interval(20 * cell + i), "R_interval": interval(30 * cell + i),
                      "R_interval_mag": f"{30 * cell + i + 2}/1000", "cell_index": cell, "detector": "CUSUM",
                      "e0": geo["e0"], "m": int(key), "rho": geo["rho"], "status": "SYNTHETIC_NOT_A_STATUS",
                      "worst_top_level_utilization": 0.0})
        m[key] = entry
    rec = {SYNTHETIC_STAMP: True, "cell_index": cell, "detector": "CUSUM", "e0": geo["e0"], "rho": geo["rho"],
           "C_upper": geo["C_upper"], "precision_bits": 256, "obligation_universe_total": 17978,
           "universe": {"ok": True, "total": 17978}, **ident,
           "producer": {**{k: ident[k] for k in PRODUCER_KEYS}, "precision_bits": 256, "runtime": runtime,
                        "final_gate": {"stage": "final", "ran_after_scientific_hash": True}},
           "m": m, "auxiliary_evidence": {"kind": "SYNTHETIC"}, "node_refinement": None,
           "certificates": {f"SYNTHETIC|{cell}|{u}": {"certificate_hash": "0" * 64, "status": "SYNTHETIC"}
                            for u in range(28)},
           "provenance_chain": {"all_verified": True, "obligations": 28, "units_verified": 28,
                                "auxiliary_evidence_bound": True},
           "scipy_guard": {"scipy_free": True}}
    H, _S = hash_modules()
    rec["auxiliary_evidence_hash"] = H.auxiliary_evidence_hash(rec)
    rec["cpu_seconds_including_dependencies"] = 1e6 if behaviour == "overclaim" else time.process_time() - t0
    rec["wall_seconds"] = time.time() - w0
    rec["scientific_content_hash"] = H.record_scientific_hash(rec)
    if behaviour == "malformed":
        rec["scientific_content_hash"] = "f" * 64
    return rec


def write_atomic(path: Path, rec: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=".json")
    with os.fdopen(fd, "w") as fh:
        fh.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def main() -> int:
    t0, w0 = time.process_time(), time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", required=True)
    a = ap.parse_args()
    cfg = json.loads(Path(a.config).read_text())
    spec = CampaignSpec.synthetic(cfg)
    out = Path(a.out)
    plan = cfg.get("plan", {}).get(str(a.cell), ["ok"])
    behaviour = plan[min(attempt_number(out, a.cell), len(plan) - 1)]
    burn(float(cfg.get("burn_s", 0.2)))
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
    write_atomic(out, build_record(spec, a.cell, t0, w0, behaviour=behaviour))
    if behaviour == "write_then_selfkill":
        os.kill(os.getpid(), signal.SIGKILL)
    if behaviour == "write_then_hang":
        while True:
            time.sleep(60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
