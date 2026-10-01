"""MB-S r1 tests: a SYNTHETIC launchd payload standing in for the driver's `decoy` mode (brief 54; never the driver,
no science, no drift, no cell geometry). It runs as the transient LaunchAgent the measurement code bootstraps, takes the
REAL host-provenance readings of the host module for its short interval and the REAL launchd check, and writes a record
in the driver's decoy-record format whose rule inputs are PLANTED numbers.

    mbs308_decoy_payload.py <nss code dir> <out> <cell> <first_blocks | all> <workers> <spec json>
spec: {"cap": bytes, "poll": seconds, "ladder": "frozen" | "dev", "event": bool (a planted memory-watchdog event:
       the record is then the driver's FAILED-decoy record and the payload exits 1), "event_cells": [cells] (the event
       only for these cells), "rss_mb": per-job peak, "sleep_s": seconds the payload lives, "spacing_ns": the sampler's
       largest observed spacing (planted), "growth": the sampler's highest growth rate (planted)}
"""
from __future__ import annotations

import json
import os
import sys
import time


def main() -> int:
    code, out, cell, fb, workers, spec = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4], int(sys.argv[5]), \
        json.loads(sys.argv[6])
    sys.path.insert(0, code)
    import mbs308_host as H
    first_blocks = None if fb == "all" else int(fb)
    h0, smp = H.snapshot(), H.Sampler().start()
    time.sleep(float(spec.get("sleep_s", 1.0)))
    mib = 1024 * 1024
    rss = int(spec.get("rss_mb", 100)) * mib
    blocks = list(range(first_blocks)) if first_blocks is not None else [0, 1]
    jobs = {f"{k}.{b}.{r}": rss + 1000 * b for b in blocks for k, r in (("RLR", 4), ("RLR", 6), ("C2B", 20), ("C1B", 8))}
    event = bool(spec.get("event")) and cell in spec.get("event_cells", [cell])
    cap = int(spec.get("cap", 3 * 1024 ** 3))
    events = [{"utc": "planted", "worker_pid": 1, "rss_bytes": cap + 1, "cap_bytes": cap, "killed": True},
              {"utc": "planted", "event": "broken_pool_worker_killed", "worker_pid": 2}] if event else []
    if event:                                    # as the driver's failed decoy: no job finished
        jobs = {}
    rec = {"synthetic_payload": True, "decoy_cell": cell, "blocks_total": 5,
           "blocks_run": "all" if first_blocks is None else blocks, "dev_ladder": spec.get("ladder") == "dev",
           "mode": "decoy", "driver_sha256": "0" * 64, "utc": "planted",
           "lifecycle": {"stage1_context": {"jobs_served_from_checkpoints": 0, "jobs_computed": len(jobs),
                                            "job_maxrss_bytes": jobs,
                                            "memory_watchdog": {"cap_bytes": spec.get("cap"), "events": events,
                                                                "worker_peak_rss_bytes": rss + 2 * mib}},
                         "driver_maxrss_bytes": 60 * mib,
                         "rss_sampler": {"interval_s": "0.25", "samples": 12, "failed_reads": 0,
                                         "max_spacing_s": int(spec.get("spacing_ns", 300_000_000)) / 1e9,
                                         "max_spacing_ns": int(spec.get("spacing_ns", 300_000_000)),
                                         "max_growth_bytes_per_s": int(spec.get("growth", 10 * mib))},
                         "rmem_run": {"workers": workers, "ladder": spec.get("ladder", "frozen"),
                                      "mem_cap_bytes": spec.get("cap", 3 * 1024 ** 3),
                                      "mem_poll_s": spec.get("poll", 2.0), "first_blocks": first_blocks,
                                      "launched_by_launchd": H.launched_by_launchd()["pass"]}},
           "host": H.provenance(h0, smp.stop(), H.snapshot())}
    if event:
        rec["decoy_failed"] = "PlantedBrokenProcessPool"
    tmp = out + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(rec, fh)
    os.replace(tmp, out)
    return 1 if event else 0


if __name__ == "__main__":
    sys.exit(main())
