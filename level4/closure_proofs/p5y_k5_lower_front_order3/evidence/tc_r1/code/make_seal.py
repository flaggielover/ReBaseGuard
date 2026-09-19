"""Build evidence/tc_r1/SEAL.json from the run evidence, BEFORE any consumption or pass/open inspection.

Reads only hashes, counts and CPU from the copied run evidence (cells/, repro/, TC_INDEX.json, RUN_LEDGER.jsonl); it
never opens a scientific field. Records the authorization conditions that must be disclosed (C5 budget, C7 parallel
channel, Note A cap discrepancy).

    python3 -B make_seal.py --evidence DIR --out SEAL.json
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve()
EVID = HERE.parents[1]
NS = HERE.parents[3]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ev = Path(a.evidence)
    index = json.loads((ev / "TC_INDEX.json").read_bytes())
    ledger = [json.loads(x) for x in (ev / "RUN_LEDGER.jsonl").read_text().splitlines() if x.strip()]
    outs = [x for x in ledger if x.get("event") == "OUTPUT"]
    reps = [x for x in ledger if x.get("event") == "REPRO"]
    cpu = sum(x.get("cpu_seconds", 0) for x in outs) + sum(x.get("cpu_seconds", 0) for x in reps)
    cells = {p.name: sha(p) for p in sorted((ev / "cells").glob("TC_CELL_*.json"))}
    repro = {p.name: sha(p) for p in sorted((ev / "repro").glob("TC_CELL_*.json"))}
    proto = json.loads((NS / "config/TC_PROTOCOL.json").read_bytes())
    seal = {
        "schema": "rebaseguard.p5y.k5.lower-front-order3.seal.v1",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "protocol_sha256": sha(NS / "config/TC_PROTOCOL.json"),
        "authorization_sha256": sha(EVID / "AUTHORIZATION.json"),
        "qualification_result_sha256": sha(EVID / "QUALIFICATION_RESULT.json"),
        "run_head": index.get("head"),
        "tc_index_sha256": sha(ev / "TC_INDEX.json"),
        "run_ledger_sha256": sha(ev / "RUN_LEDGER.jsonl"),
        "cells": cells, "cells_count": len(cells), "repro": repro,
        "reproduction_identical": index.get("reproduction"),
        "ledger": {"outputs": len(outs), "repro": len(reps), "all_ok": all(x.get("ok") for x in outs),
                   "events": sorted({x["event"] for x in ledger})},
        "new_real_cpu_seconds": cpu, "new_real_cpu_hours": round(cpu / 3600, 3),
        "budget": {"forecast": proto["budget"]["forecast_new_real_cpu_hours"],
                   "protocol_cap_enforced": proto["budget"]["protocol_cap_new_real_cpu_hours"],
                   "campaign_preferred": 20, "campaign_hard": 40,
                   "note_A_cap_discrepancy": "the frozen prose (spec section 7, COST_NOTE, authorization brief) says "
                                             "cap 24 CPU-h; the binding machine-readable protocol says 30 (rationale: "
                                             "review r3 disposition N-R3-7). The enforced cap is 30 (authorization "
                                             "Note A); it must be recorded at adjudication"},
        "disclosure_C7_parallel_channel": "the frozen Order3Certifier of p5y_k5_cusum_order3_real_producer was executed "
                                          "on real CUSUM cells 11-44 under THIS protocol's authorization; that "
                                          "producer's own real-cell authorization registry remains FROZEN EMPTY and "
                                          "neither certify_real_cell nor rung3_engine.certify_order3 was executed. The "
                                          "order-3 namespace's 'no real CUSUM cell is evaluated' wording refers to its "
                                          "own gated entry point only",
        "inspection": "no scientific field of any cell record was read before this seal; no pass/open set exists yet",
        "next": "consumption (tc_consume twice, --out outside the checkout), then independent adjudication",
    }
    Path(a.out).write_text(json.dumps(seal, sort_keys=True, indent=1) + "\n")
    print(json.dumps({k: seal[k] for k in ("cells_count", "new_real_cpu_hours", "reproduction_identical",
                                           "tc_index_sha256")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
