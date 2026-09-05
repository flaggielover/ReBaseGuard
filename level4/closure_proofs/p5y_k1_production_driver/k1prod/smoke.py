"""Tiny NON-LOAD-BEARING scaling smoke. Infers no K1 scientific result."""
from __future__ import annotations

import json, multiprocessing as mp, os, resource, sys, time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _work(_i: int) -> float:
    from flint import arb, arb_mat, ctx
    ctx.prec = 256
    n, z = 204, 21
    P = arb_mat(n, z); Q = arb_mat(n, z); Hk = arb_mat(z, z)
    for i in range(n):
        for k in range(z):
            P[i, k] = arb(i + 1) / arb(k + 3); Q[i, k] = arb(k + 1) / arb(i + 5)
    for a in range(z):
        for b in range(z):
            Hk[a, b] = arb(1) / arb(a + b + 2)
    t = time.process_time()
    for _ in range(3):
        _ = (P * Hk) * Q.transpose()
    return time.process_time() - t


def smoke(counts=(1, 8, 16, 32, 64)) -> dict:
    avail = os.cpu_count() or 1
    rows = []
    for w in counts:
        eff = min(w, avail)
        t0w = time.time(); t0c = time.process_time()
        if eff == 1:
            cpu_list = [_work(0)]
        else:
            with mp.Pool(eff) as p:
                cpu_list = p.map(_work, range(eff))
        wall = time.time() - t0w
        worker_cpu = sum(cpu_list)
        rows.append({"requested_workers": w, "effective_workers": eff,
                     "wall_seconds": wall, "worker_cpu_seconds": worker_cpu,
                     "parent_cpu_seconds": time.process_time() - t0c,
                     "cpu_utilisation": worker_cpu / wall if wall else 0.0,
                     "startup_overhead_s": max(wall - max(cpu_list), 0.0),
                     "peak_rss_mib": resource.getrusage(
                         resource.RUSAGE_SELF).ru_maxrss / 1024 ** 2,
                     "oversubscribed": w > avail})
    base = rows[0]["worker_cpu_seconds"] / max(rows[0]["effective_workers"], 1)
    flags = []
    for r in rows:
        per = r["worker_cpu_seconds"] / max(r["effective_workers"], 1)
        r["per_worker_cpu_vs_serial"] = per / base if base else 0.0
        # Only a NON-oversubscribed row can evidence scaling collapse. On a host
        # with fewer cores than requested workers, elevated per-worker CPU is
        # oversubscription, not collapse, and says nothing about the target server.
        if (r["effective_workers"] > 1 and not r["oversubscribed"]
                and r["per_worker_cpu_vs_serial"] > 2.0):
            flags.append(f"severe scaling collapse at {r['effective_workers']} workers")
        if r["oversubscribed"]:
            flags.append(f"oversubscribed: {r['requested_workers']} requested on "
                         f"{avail} cores -- not predictive of the target server")
    return {"schema": "rebaseguard.p5y.k1.scaling_smoke.v1",
            "result_bearing": False, "infers_K1_science": False,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "host_cpu_count": avail, "rows": rows, "flags": flags,
            "note": "synthetic panel-shaped work; NOT a cover cell"}


if __name__ == "__main__":
    print(json.dumps(smoke(), indent=1))
