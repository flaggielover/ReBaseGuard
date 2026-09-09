"""Multi-worker SR contract throughput benchmark. Identical bytes on every host.
Result-free: evaluates the frozen DENSE benchmark candidate, writes no SR cell record."""
import hashlib, json, os, resource, sys, time
from pathlib import Path
from multiprocessing import Process, Queue

ROOT = Path(sys.argv[1]); HOST = sys.argv[2]
CORES = [int(c) for c in sys.argv[3].split(",")]
NCTR = int(sys.argv[4]); OUT = sys.argv[5]
CP = ROOT / "level4/closure_proofs"


def setup():
    for p in (CP / "p5y_k1_sr_backend_cost_audit/code",
              CP / "p5y_k1_task1r_budget_harness/code",
              CP / "p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic",
              ROOT / "rebaseguard-proof/src"):
        if str(p) not in sys.path:
            sys.path.insert(0, str(p))
    from flint import arb, ctx
    import harness as H, sr_local as L, opt_backend as OB
    from rebaseguard_certify.arb_backend import rational
    par = json.loads((CP / "p5y_k1_task1r_budget_harness/config/frozen_parameters.json"
                      ).read_text())["selection"]
    ctx.prec = H.PROD_BITS
    A, b, c = L.sr_constants()
    e = rational(H.E_NUM, H.E_DEN)
    geo = L.patch_geometry(17, 11, grid=H.GRID)
    p_c = (geo["yp"][0] + geo["yp"][1]) / arb(2)
    m_c = (geo["ym"][0] + geo["ym"][1]) / arb(2)
    Hh = (geo["yp"][1] - geo["yp"][0]) / arb(2)
    U_c, L_c = c - p_c, m_c - c
    span = U_c - L_c
    D, Z = par["D_selected"], par["Z_selected"]
    p1 = H.p1_rule(Hh, span)
    h = span / (arb(2) * arb(p1["n_panels"]))
    ctxt = (Hh, h, D, Z, [Hh ** a for a in range(2 * D + 2)],
            [h ** k for k in range(2 * Z + 2)])
    sh = OB.PanelShared(p_c, m_c, L_c + h, b, ctxt)
    Nf = H.panel_moments(L_c, L_c + arb(2) * h, L_c + h, e, 2 * Z + 4, h)
    pd = OB.PanelDrift(sh, Nf)
    import random
    random.seed(0)
    n = H.CAND_DEGREE + 1
    cand = [[arb(random.randint(-50, 50)) / arb(97) for _ in range(n)] for _ in range(n)]
    return OB, pd, cand, D + 1, arb


def worker(core, q):
    os.sched_setaffinity(0, {core})
    OB, pd, cand, Dp, arb = setup()
    for _ in range(20):                                  # warmup, not measured
        OB.contract(pd, cand)
    t_cpu0 = time.process_time(); t_w0 = time.perf_counter()
    for _ in range(NCTR):
        coef, ex, ez = OB.contract(pd, cand)
    cpu = time.process_time() - t_cpu0
    wall = time.perf_counter() - t_w0
    parts = []
    for a in range(Dp):
        for bq in range(Dp):
            x = coef[a][bq]
            m, me = x.mid().man_exp(); r, re_ = x.rad().man_exp()
            parts.append(f"{int(m)}:{int(me)}:{int(r)}:{int(re_)}")
    sci = hashlib.sha256("|".join(parts).encode()).hexdigest()
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    q.put({"core": core, "cpu_s": cpu, "wall_s": wall, "contracts": NCTR,
           "sci": sci, "rss_kib": rss})


def run(W):
    cores = CORES[:W]
    q = Queue()
    ps = [Process(target=worker, args=(c, q)) for c in cores]
    t0 = time.perf_counter()
    for p in ps:
        p.start()
    recs = [q.get() for _ in ps]
    for p in ps:
        p.join()
    wall = time.perf_counter() - t0
    cpu = sum(r["cpu_s"] for r in recs)
    ctr = sum(r["contracts"] for r in recs)
    sci = sorted({r["sci"] for r in recs})
    return {"workers": W, "cores": cores, "wall_s": wall, "cpu_s": cpu,
            "contracts": ctr, "contracts_per_s": ctr / wall,
            "ms_per_contract_cpu": 1000.0 * cpu / ctr,
            "cpu_per_wall": cpu / wall,
            "peak_rss_mb": sum(r["rss_kib"] for r in recs) / 1024.0,
            "distinct_scientific_hashes": len(sci), "scientific_hash": sci[0],
            "per_worker_cpu_s": [round(r["cpu_s"], 3) for r in recs]}


if __name__ == "__main__":
    res = {"host": HOST, "cores_available": CORES, "contracts_per_worker": NCTR,
           "runs": []}
    for W in [int(x) for x in sys.argv[6].split(",")]:
        r = run(W)
        res["runs"].append(r)
        print(f"W={W:2d} wall={r['wall_s']:8.2f}s cpu={r['cpu_s']:9.2f}s "
              f"ctr/s={r['contracts_per_s']:9.2f} ms/ctr={r['ms_per_contract_cpu']:7.4f} "
              f"cpu/wall={r['cpu_per_wall']:5.2f} rss={r['peak_rss_mb']:7.1f}MB "
              f"sci_uniq={r['distinct_scientific_hashes']}")
    base = res["runs"][0]["contracts_per_s"]
    for r in res["runs"]:
        r["speedup_vs_w1"] = r["contracts_per_s"] / base
        r["parallel_efficiency"] = r["speedup_vs_w1"] / r["workers"]
    Path(OUT).write_text(json.dumps(res, indent=1, sort_keys=True))
    print("scientific hash:", res["runs"][0]["scientific_hash"])
