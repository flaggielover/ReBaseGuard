"""Runs one worker-count configuration: launches N pinned workers, releases them
together, samples system load, and aggregates."""
import os, sys, json, time, subprocess, shutil, argparse, resource

VENV = "/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python"
W    = "/home/ubuntu/work/sr_scaling/worker.py"
BASE = "/home/ubuntu/work/sr_scaling"

def affinity_map(n):
    """CPUs 0-15 are distinct physical cores; 16-31 are their SMT siblings
    (cpu i and cpu i+16 share physical core i)."""
    if n <= 16:
        return list(range(n)), "one worker per DISTINCT physical core (cpus 0-%d)" % (n-1)
    extra = n - 16
    return (list(range(16)) + list(range(16, 16+extra)),
            "all 16 physical cores singly occupied (cpus 0-15), plus %d SMT siblings "
            "(cpus 16-%d) so %d physical cores are DOUBLY occupied" % (extra, 16+extra-1, extra))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, required=True)
    ap.add_argument("--packets", type=int, required=True)
    ap.add_argument("--rep", type=int, required=True)
    ap.add_argument("--cand", default="real")
    args = ap.parse_args()
    n = args.workers
    tag = f"{args.cand}_w{n}_r{args.rep}"
    d = f"{BASE}/results/{tag}"
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    cpus, aff_doc = affinity_map(n)

    env = dict(os.environ)
    for v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS","BLIS_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
        env[v] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    start = f"{d}/START"
    procs = []
    for i in range(n):
        cmd = ["taskset","-c",str(cpus[i]), VENV, W,
               "--out",f"{d}/w{i}.json","--ready",f"{d}/r{i}",
               "--start",start,"--packets",str(args.packets),
               "--cand",args.cand,"--wid",str(i)]
        if i == 0: cmd.append("--check-baseline")
        procs.append(subprocess.Popen(cmd, cwd="/home/ubuntu/work/ReBaseGuard",
                                      env=env, stdout=open(f"{d}/w{i}.log","w"),
                                      stderr=subprocess.STDOUT))
    # wait for every worker to finish setup
    t_setup = time.time()
    while sum(os.path.exists(f"{d}/r{i}") for i in range(n)) < n:
        if time.time()-t_setup > 900: raise SystemExit("workers failed to become ready")
        time.sleep(0.1)

    samples = []
    t0 = time.monotonic()
    open(start,"w").write("1")
    # sample load / utilisation while the batch runs
    def cpu_tot():
        f = open("/proc/stat").readline().split()[1:]
        v = list(map(int,f)); idle = v[3]+v[4]; return sum(v), idle
    s_tot, s_idle = cpu_tot()
    while any(p.poll() is None for p in procs):
        time.sleep(2.0)
        try:
            la = open("/proc/loadavg").read().split()[:3]
            samples.append({"t": time.monotonic()-t0, "loadavg": la})
        except Exception: pass
    t1 = time.monotonic()
    e_tot, e_idle = cpu_tot()
    for p in procs: p.wait()
    ruc = resource.getrusage(resource.RUSAGE_CHILDREN)

    ws = []
    for i in range(n):
        try: ws.append(json.load(open(f"{d}/w{i}.json")))
        except Exception as e:
            ws.append({"wid":i,"ERROR":str(e),"log":open(f"{d}/w{i}.log").read()[-800:]})
    ok = [w for w in ws if "ERROR" not in w]
    d_tot = e_tot - s_tot; d_idle = e_idle - s_idle
    out = {
      "tag": tag, "workers": n, "rep": args.rep, "cand": args.cand,
      "packets_per_worker": args.packets,
      "affinity_cpus": cpus, "affinity_doc": aff_doc,
      "batch_wall_s": t1 - t0,
      "worker_wall_s": [w.get("wall_s") for w in ok],
      "worker_cpu_s": [w.get("cpu_s") for w in ok],
      "worker_user_s": [w.get("user_s") for w in ok],
      "worker_sys_s": [w.get("sys_s") for w in ok],
      "worker_maxrss_kib": [w.get("maxrss_kib") for w in ok],
      "worker_probe_before": [w.get("probe_rate_before") for w in ok],
      "worker_probe_after": [w.get("probe_rate_after") for w in ok],
      "worker_invol_ctx": [w.get("invol_ctx_switches") for w in ok],
      "contracts_total": sum(w.get("contracts",0) for w in ok),
      "cpu_s_total": sum(w.get("cpu_s",0.0) for w in ok),
      "user_s_total": sum(w.get("user_s",0.0) for w in ok),
      "sys_s_total": sum(w.get("sys_s",0.0) for w in ok),
      "children_rusage_cpu_s": ruc.ru_utime + ruc.ru_stime,
      "peak_rss_aggregate_kib": sum(w.get("maxrss_kib",0) for w in ok),
      "peak_rss_max_worker_kib": max([w.get("maxrss_kib",0) for w in ok] or [0]),
      "scientific_hashes": sorted({w.get("scientific_hash") for w in ok}),
      "thread_env_violations": sorted({v for w in ok for v in w.get("thread_env_violations",[])}),
      "baseline_check": next((w.get("baseline_check") for w in ok if w.get("baseline_check")), None),
      "errors": [w for w in ws if "ERROR" in w],
      "system_cpu_busy_fraction": (d_tot-d_idle)/d_tot if d_tot else None,
      "loadavg_samples": samples[-6:],
      "n_contexts": ok[0].get("n_contexts") if ok else None,
    }
    json.dump(out, open(f"{BASE}/results/{tag}.json","w"), indent=1)
    print(json.dumps({k:out[k] for k in
        ("tag","workers","rep","batch_wall_s","cpu_s_total","contracts_total",
         "scientific_hashes","thread_env_violations","peak_rss_aggregate_kib")}, indent=1))

main()
