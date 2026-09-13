"""READ-ONLY deployment gate for the generation-2 runtime isolation repair.

LANE_A_DEPLOYMENT_ALLOWED_ONLY_AFTER = CURRENT_LIVE_DRAIN_SETTLED

Never run this against a LIVE campaign. The script writes nothing except --out, which must lie
outside every source and runtime tree. The only interaction with runtime state is a non-blocking
flock probe, which is released at once and can never block a holder.

Phases
  settled     the drained run is fully settled; Lane A may be FROZEN (contract must still be unfrozen)
  pre-resume  frozen hashes bound, focused acceptance re-run on the frozen sources, generation DRAIN
              cleared; production may be RESUMED

  python check_deployment_gate.py --phase settled --production-root P --runtime-dir R \
         --expected-sealed 16 [--unit-glob 'rbg-p5y-k1-ps1-*'] [--legacy-work-dir W ...] --out OUT.json
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
NS_REL = "level4/closure_proofs/p5y_k1_ps1_production"


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canon(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def lock_state(path: Path) -> str:
    if not path.exists():
        return "FREE"
    fd = os.open(str(path), os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
        fcntl.flock(fd, fcntl.LOCK_UN)
        return "FREE"
    except BlockingIOError:
        return "LIVE"
    finally:
        os.close(fd)


def chain_valid(path: Path) -> dict:
    if not path.exists():
        return {"present": False, "valid": False}
    prev, n = None, 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        body = {k: v for k, v in rec.items() if k != "sha256"}
        if rec.get("sha256") != hashlib.sha256(canon(body)).hexdigest() or \
                rec.get("prev_sha256") != (prev["sha256"] if prev else None):
            return {"present": True, "valid": False, "broken_at_seq": rec.get("seq")}
        prev, n = rec, n + 1
    return {"present": True, "valid": True, "records": n, "last_event": prev and prev["event"]}


def active_units(glob: str | None) -> list:
    if not glob:
        return []
    r = subprocess.run(["systemctl", "list-units", "--state=active,activating,deactivating,reloading",
                        "--no-legend", "--plain", glob], capture_output=True, text=True, timeout=30)
    return [l.split()[0] for l in r.stdout.splitlines() if l.strip()]


def evaluate(a) -> dict:
    prod_ns = Path(a.production_root) / NS_REL
    rt = Path(a.runtime_dir)
    ledger_p = prod_ns / "production/PRODUCTION_LEDGER.json"
    st = json.loads(ledger_p.read_text())
    ops = st.get("operational_lifecycle") or {}
    completed = st.get("completed_cells", {})
    cells_dir = prod_ns / "production/cells"
    sealed = {int(p.stem): json.loads(p.read_bytes()) for p in sorted(cells_dir.glob("[0-9]*.json"))} \
        if cells_dir.exists() else {}
    qualified = json.loads((NS / "config/QUALIFIED_SOURCE_HASHES.json").read_text())["files"]
    drift = sorted(rel for rel, h in qualified.items() if not (NS / rel).exists() or sha(NS / rel) != h)
    contract = NS / "config/OPERATIONAL_CONTRACT.json"
    hash_file = NS / "config/OPERATIONAL_CONTRACT_HASH"
    gen_drain = rt / "work/DRAIN"
    legacy_drains = [str(Path(w) / "DRAIN") for w in a.legacy_work_dir if (Path(w) / "DRAIN").exists()]
    units = active_units(a.unit_glob)
    g = {
        "G1_no_active_campaign_unit": (not units, {"active": units}),
        "G2_campaign_lock_released": (lock_state(rt / "campaign.lock") == "FREE", {}),
        "G3_frozen_ledger_lock_absent": (not Path(str(ledger_p) + ".lock").exists(), {}),
        "G4_zero_open_reservations": (not st.get("open_reservations"), {"open": sorted(st.get("open_reservations", {}))}),
        "G5_no_unsettled_runs": (not any(r.get("status") == "OPEN" for r in ops.get("runs", {}).values()), {}),
        "G6_torn_attempts_empty": (ops.get("torn_attempts") == {}, {"torn": ops.get("torn_attempts")}),
        "G7_not_halted": (ops.get("halt") is None, {"halt": ops.get("halt")}),
        "G8_expected_sealed_cells": (len(sealed) == a.expected_sealed and set(sealed) == {int(c) for c in completed},
                                     {"sealed": len(sealed), "ledger_completed": len(completed),
                                      "expected": a.expected_sealed}),
        "G9_sealed_records_equal_ledger": (all(sealed[c] == completed.get(str(c)) for c in sealed), {}),
        "G10_continuity_chain_valid": (chain_valid(rt / "continuity.jsonl").get("valid") is True,
                                       chain_valid(rt / "continuity.jsonl")),
        "G11_repair_sources_equal_qualified": (not drift, {"drift": drift}),
    }
    if a.phase == "settled":
        g["G12_contract_still_unfrozen"] = (not hash_file.exists(), {})
    else:
        frozen = hash_file.exists() and hash_file.read_text().strip() == sha(contract)
        g["G12_contract_frozen_and_bound"] = (frozen, {"contract_sha256": sha(contract),
                                                       "hash_file": hash_file.read_text().strip() if hash_file.exists() else None})
        acc = json.loads(Path(a.acceptance).read_text()) if a.acceptance else {}
        g["G13_focused_acceptance_rerun_all_pass"] = (bool(acc.get("results")) and all(v.get("pass") for v in acc["results"].values()),
                                                      {"acceptance": a.acceptance})
        g["G14_generation_drain_cleared"] = (not gen_drain.exists(), {"flag": str(gen_drain)})
    ok = all(v[0] for v in g.values())
    return {"schema": "rebaseguard.p5y.k1.ps1.gen2-runtime-isolation.deployment-gate-check.v1",
            "phase": a.phase, "read_only": True,
            "gates": {k: {"pass": v[0], **v[1]} for k, v in g.items()},
            "legacy_drain_flags_present": legacy_drains, "ledger_sha256": sha(ledger_p),
            ("FREEZE_ALLOWED" if a.phase == "settled" else "RESUME_ALLOWED"): ok}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("settled", "pre-resume"), required=True)
    ap.add_argument("--production-root", required=True)
    ap.add_argument("--runtime-dir", required=True)
    ap.add_argument("--expected-sealed", type=int, required=True)
    ap.add_argument("--legacy-work-dir", action="append", default=[])
    ap.add_argument("--unit-glob")
    ap.add_argument("--acceptance")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    for tree in (Path(a.production_root).resolve(), Path(a.runtime_dir).resolve(), NS.resolve()):
        if str(out).startswith(str(tree) + os.sep):
            raise SystemExit(f"--out {out} lies inside {tree}; refusing to write there")
    rep = evaluate(a)
    out.write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in rep.items() if k.endswith("_ALLOWED")} |
                     {"failed": [k for k, v in rep["gates"].items() if not v["pass"]]}))
    return 0 if rep.get("FREEZE_ALLOWED", rep.get("RESUME_ALLOWED")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
