"""NON-PRODUCTION, NON-DISPOSITION-BEARING cross-host replay of committed PS1 SR patch records.

Re-executes a predeclared set of (successor cell, patch) pairs through the bound PS1 per-patch
function (opt_core.core, frozen certifier + bit-identical memoisation, 256 bits) in ONE fresh
interpreter with a COLD per-patch cache, and compares the scientific leaves (nodes, geo) with
the COMMITTED AWS Phase-4 qualification records of the same pairs. Nothing is sealed, no ledger
or production namespace is read or written, and no cell obligation (T3/T4/T5) is evaluated: a
patch record is an intermediate, not a verdict.

  python crosshost_patch_replay.py --pick PREDECLARATION.json --chunks <qual/chunks> --out OUT.json --label R1
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import platform
import resource
import time
from pathlib import Path

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
               "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def leaf_hash(nodes, geo) -> str:
    return hashlib.sha256(canon({"nodes": json.loads(canon(nodes)), "geo": json.loads(canon(geo))})).hexdigest()


def runtime():
    import flint
    import numpy
    cfg = numpy.show_config(mode="dicts")
    blas = (cfg.get("Build Dependencies", {}) or {}).get("blas", {})
    fp = {"python": platform.python_version(), "implementation": platform.python_implementation(),
          "machine": platform.machine(), "python_flint": flint.__version__, "numpy": numpy.__version__,
          "blas": {k: blas.get(k) for k in ("name", "version")},
          "thread_environment": {v: os.environ.get(v) for v in THREAD_VARS}}
    extra = {"cpu_model": next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo")
                                if l.startswith("model name")), None),
             "OPENBLAS_CORETYPE": os.environ.get("OPENBLAS_CORETYPE"), "affinity": sorted(os.sched_getaffinity(0))}
    try:
        from threadpoolctl import threadpool_info
        extra["threadpools"] = [{k: d.get(k) for k in ("internal_api", "version", "architecture", "num_threads")}
                                for d in threadpool_info()]
    except Exception:                                                  # noqa: BLE001
        extra["threadpools"] = "threadpoolctl unavailable"
    return {"fingerprint": fp, "sha256": hashlib.sha256((json.dumps(fp, sort_keys=True, separators=(",", ":"),
                                                                    ensure_ascii=True) + "\n").encode()).hexdigest(),
            "diagnostic": extra}


def committed(chunks: Path, want: set) -> dict:
    out = {}
    for f in sorted(glob.glob(str(chunks / "rec_s*_p*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            key = (r["successor_cell"], tuple(r["patch"]))
            if key in want:
                m = r["modes"]["mid"]
                out[key] = {"leaf_sha256": leaf_hash(m["nodes"], m["geo"]), "aws_cpu_s": r["cpu_seconds"],
                            "nodes": m["nodes"], "geo": m["geo"]}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", required=True)
    ap.add_argument("--chunks", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True)
    a = ap.parse_args()
    if not all(os.environ.get(v) == "1" for v in THREAD_VARS):
        raise SystemExit("six-variable thread contract not in force")
    wall0, u0 = time.time(), resource.getrusage(resource.RUSAGE_SELF)
    import sr_o9_candidates as T
    import sr_o9_bint_p1 as BP
    import opt_core as OC
    import succ_t3 as S3
    from flint import ctx
    pick = json.loads(Path(a.pick).read_text())["pick"]
    want = {(int(c), tuple(p["patch"])) for c, ps in pick.items() for p in ps}
    ref = committed(Path(a.chunks), want)
    missing = sorted(want - set(ref))
    if missing:
        raise SystemExit(f"committed AWS records missing for {missing[:4]}")
    rows, cell_inputs_cpu = [], {}
    with T.scientific_precision():
        if ctx.prec != 256:
            raise SystemExit(f"precision {ctx.prec} != 256")
        for c, ps in sorted(pick.items(), key=lambda kv: int(kv[0])):
            s = int(c)
            t0 = time.process_time()
            cands, hashes, C, e0, _clsha = S3.cell_inputs(s)
            cell_inputs_cpu[c] = time.process_time() - t0
            for p in ps:
                i, j = p["patch"]
                t, w = time.process_time(), time.time()
                with BP.p1_lagrange_factor():
                    nodes, geo, st = OC.core(i, j, e0, cands, cand_hashes=hashes, C_gate=C, shared_cache={},
                                             mode="mid")
                cpu, wall = time.process_time() - t, time.time() - w
                h = leaf_hash(nodes, geo)
                r = ref[(s, (i, j))]
                rows.append({"cell": s, "patch": [i, j], "leaf_sha256": h,
                             "bit_identical_to_committed_aws": h == r["leaf_sha256"]
                             and json.loads(canon(nodes)) == r["nodes"] and json.loads(canon(geo)) == r["geo"],
                             "cpu_s": cpu, "wall_s": wall, "aws_cpu_s": r["aws_cpu_s"],
                             "cache_hits": st.get("hits"), "cache_misses": st.get("misses"),
                             "peak_rss_kib_so_far": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})
                print(json.dumps({k: rows[-1][k] for k in ("cell", "patch", "bit_identical_to_committed_aws", "cpu_s")}),
                      flush=True)
    u1 = resource.getrusage(resource.RUSAGE_SELF)
    out = {"schema": "rebaseguard.p5y.k1.sr.ps1.vultr-crosshost-replay.v1", "label": a.label,
           "result_bearing": False, "production": False, "disposition_bearing": False,
           "host": os.uname().nodename, "runtime": runtime(), "pid": os.getpid(),
           "n": len(rows), "all_bit_identical": all(r["bit_identical_to_committed_aws"] for r in rows),
           "process_cpu_s": (u1.ru_utime + u1.ru_stime) - (u0.ru_utime + u0.ru_stime),
           "process_wall_s": time.time() - wall0, "peak_rss_kib": u1.ru_maxrss,
           "cell_inputs_cpu_s": cell_inputs_cpu, "rows": rows}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("label", "n", "all_bit_identical", "process_cpu_s", "peak_rss_kib")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
