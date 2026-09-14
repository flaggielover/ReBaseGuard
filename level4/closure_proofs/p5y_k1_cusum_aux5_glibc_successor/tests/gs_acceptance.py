"""SYNTHETIC acceptance of the CUSUM Aux5 new-glibc successor. NON-RESULT-BEARING.

Runs on the bound host from the clean successor checkout. Only synthetic workers run, in scratch roots outside the
repository and every production runtime root. The frozen certifier is never started, the successor production runtime
root is never created, the predecessor runtime is only read, and nothing is launched.

Every synthetic settlement goes through the sanctioned command `gs_entry.py settle`; the result records, per scenario,
how many times it was invoked, and refuses PASS if any successor test calls a settlement helper directly.

  python -B tests/gs_acceptance.py --scratch DIR --out RESULT.json [--only NAME ...]
"""
from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gs_fixtures import GS, SCENARIOS, SETTLE_LOG, SP, file_sha_or_none, settlement_bypass_scan  # noqa: E402
import gs_scenarios_a                                                      # noqa: E402,F401  registers scenarios
import gs_scenarios_b                                                      # noqa: E402,F401  registers scenarios
import gs_scenarios_c                                                      # noqa: E402,F401  registers scenarios
import gs_settle as ST                                                     # noqa: E402
from gs_entry import live_record_envelope_digest                            # noqa: E402
from prod_common import Refusal, atomic_write_json                         # noqa: E402

PRED_FILES = ("ledger.json", "journal.jsonl", "reaper.jsonl")


def predecessor_snapshot() -> dict:
    root = GS.PREDECESSOR_RUNTIME_ROOT
    return {"files": {n: file_sha_or_none(root / n) for n in PRED_FILES},
            "record_envelope_digest": live_record_envelope_digest(root) if root.is_dir() else None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    scratch = Path(a.scratch).resolve()
    for root in (GS.SUCCESSOR_RUNTIME_ROOT, *GS.REFUSED_ROOTS):
        if scratch == root or root in scratch.parents:
            print("REFUSED: scratch inside a production runtime root")
            return 30
    scratch.mkdir(parents=True, exist_ok=False)
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        _cp, sha = SP.load_checkpoint()
        bound_ok = True
    except Refusal as r:
        sha, bound_ok = f"UNAVAILABLE: {r}", False
    auth_sha = file_sha_or_none(GS.AUTHORIZATION)
    succ_absent_before = not GS.SUCCESSOR_RUNTIME_ROOT.exists()
    pred_before = predecessor_snapshot()
    bypass = settlement_bypass_scan()
    results, coverage = {}, {}
    for name, covers, fn in SCENARIOS:
        if a.only and name not in a.only:
            continue
        t0, n0 = time.monotonic(), len(SETTLE_LOG)
        try:
            results[name] = {"status": "PASS", "details": fn(scratch)}
        except Exception as exc:                                    # noqa: BLE001
            results[name] = {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}", "trace": traceback.format_exc()[-1500:]}
        results[name]["seconds"] = round(time.monotonic() - t0, 1)
        results[name]["sanctioned_settle_invocations"] = len(SETTLE_LOG) - n0
        for cv in covers:
            coverage.setdefault(cv, []).append(name)
        print(f"{results[name]['status']:4s} {results[name]['seconds']:7.1f}s  settle x{results[name]['sanctioned_settle_invocations']:<2d} {name}"
              + ("" if results[name]["status"] == "PASS" else f"  -- {results[name]['error'][:300]}"), flush=True)
    try:
        _cp2, sha_after = SP.load_checkpoint()
    except Refusal as r:
        sha_after = f"UNAVAILABLE: {r}"
    succ_absent_after = not GS.SUCCESSOR_RUNTIME_ROOT.exists()
    pred_after = predecessor_snapshot()
    head = subprocess.run(["git", "-C", str(GS.ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    settle_tests = sorted(n for n, r in results.items() if r["sanctioned_settle_invocations"])
    ok = (bound_ok and sha == sha_after and succ_absent_before and succ_absent_after and pred_before == pred_after
          and pred_before["record_envelope_digest"] == GS.RECORD_ENVELOPE_DIGEST and not a.only and not bypass
          and file_sha_or_none(GS.AUTHORIZATION) == auth_sha and all(r["status"] == "PASS" for r in results.values()))
    doc = {"schema": GS.ACCEPTANCE_SCHEMA, "GLIBC_SUCCESSOR_SYNTHETIC_ACCEPTANCE": "PASS" if ok else "FAIL",
           "generation": "r4", "checkpoint_sha256": sha, "checkpoint_unchanged_during_run": sha == sha_after,
           "run_authorization_sha256": auth_sha, "bound_sources_verified": bound_ok, "host_name": socket.gethostname(),
           "git_head": head, "python": sys.version.split()[0], "started_utc": started,
           "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "non_result_bearing": True,
           "frozen_certifier_started": False, "production_launched": False,
           "successor_runtime_root_absent_before_and_after": succ_absent_before and succ_absent_after,
           "predecessor_runtime_unchanged": pred_before == pred_after, "predecessor_snapshot": pred_after,
           "settlement": {"command": ST.SETTLE_COMMAND, "version": ST.SETTLE_VERSION,
                          "sanctioned_settlement_tests": settle_tests, "sanctioned_settlement_test_count": len(settle_tests),
                          "sanctioned_settle_invocations_total": len(SETTLE_LOG),
                          "invocations_exit_0": sum(1 for x in SETTLE_LOG if x["rc"] == 0),
                          "invocations_refused": sum(1 for x in SETTLE_LOG if x["rc"] != 0),
                          "direct_settlement_calls_in_tests": bypass,
                          "frozen_harness_helper": "disabled (gs_fixtures._Base.settle raises)"},
           "scratch": str(scratch), "passed": sum(r["status"] == "PASS" for r in results.values()), "total": len(results),
           "tests": results, "coverage": coverage}
    atomic_write_json(a.out, doc)
    print(json.dumps({k: doc[k] for k in ("GLIBC_SUCCESSOR_SYNTHETIC_ACCEPTANCE", "passed", "total")}
                     | {"sanctioned_settlement_tests": len(settle_tests)}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
