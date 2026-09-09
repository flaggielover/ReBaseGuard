"""One scaling-study worker. Runs the FROZEN packet, records resource usage,
an effective-per-core-speed probe, and a byte-exact scientific hash."""
import sys, os, time, json, resource, hashlib, argparse
sys.path.insert(0, '/home/ubuntu/work/sr_scaling')

THREAD_VARS = ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS","BLIS_NUM_THREADS","VECLIB_MAXIMUM_THREADS")

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--ready", required=True)
ap.add_argument("--start", required=True)
ap.add_argument("--packets", type=int, required=True)
ap.add_argument("--cand", default="real", choices=["real","dense"])
ap.add_argument("--wid", type=int, required=True)
ap.add_argument("--check-baseline", action="store_true")
a = ap.parse_args()

env = {v: os.environ.get(v) for v in THREAD_VARS}
bad = [v for v,x in env.items() if x != "1"]

import packet as P
from flint import arb, arb_mat, ctx
import opt_backend as OB

def exact(x):
    """Exact dyadic (mantissa, exponent) of midpoint and radius."""
    return (x.mid().man_exp(), x.rad().man_exp())

def rate_probe(reps=400):
    """Effective per-core arithmetic speed on the SAME instruction mix as the
    workload (256-bit arb multiply-add). Rate falls if the core is slowed."""
    u = arb(1)/arb(97); v = arb(1)/arb(89); acc = arb(0)
    t = time.process_time()
    for _ in range(reps):
        acc = acc + u*v
    dt = time.process_time() - t
    return reps/dt if dt > 0 else float('nan')

cand = P.real_candidate() if a.cand == "real" else P.dense_random_candidate(1)
ctxs = P.build_contexts()
AVs  = [P.absvecs_of(c['sh']) for c in ctxs]

probe_before = rate_probe()

# optional: confirm O9 is bit-for-bit equal to the ACCEPTED baseline backend
baseline_check = None
if a.check_baseline:
    c0 = ctxs[0]; Rb = P.build_Rbig(c0['pd'])
    b_coef, bex, bez = OB.contract(c0['pd'], cand)
    o_coef, oex, oez = P.contract_O9(c0['pd'], cand, Rb, AVs[0])
    bitexact = all(exact(b_coef[i][j]) == exact(o_coef[i][j])
                   for i in range(len(b_coef)) for j in range(len(b_coef[0])))
    maxrat = 0.0
    for i in range(len(b_coef)):
        for j in range(len(b_coef[0])):
            rb = float(b_coef[i][j].rad())
            if rb > 0: maxrat = max(maxrat, float(o_coef[i][j].rad())/rb)
    from fractions import Fraction as _F
    def _dy(v):
        m,e = v.man_exp(); return _F(int(m))*(_F(2)**int(e))
    _sf = []
    for _o,_b in ((oex,bex),(oez,bez)):
        _ov,_bv = _dy(_o.abs_upper()), _dy(_b.abs_upper())
        _sf.append(float((_bv-_ov)/_bv) if _bv != 0 else 0.0)
    baseline_check = {"taylor_bit_for_bit_identical": bitexact,
                      "max_radius_ratio_O9_over_baseline": maxrat,
                      "error_channel_rel_shortfall_vs_baseline": max(_sf),
                      "error_channel_within_256bit_rounding": max(_sf) < 2.0**-200}

open(a.ready, "w").write("1")
while not os.path.exists(a.start): time.sleep(0.02)

ru0 = resource.getrusage(resource.RUSAGE_SELF)
w0 = time.monotonic()
sci = None
n_contracts = 0
for rep in range(a.packets):
    h = hashlib.sha256() if rep == 0 else None
    for ci, c in enumerate(ctxs):
        Rb = P.build_Rbig(c['pd'])                 # panel-only work, once per panel
        for k in range(P.CONTRACTS_PER_PANEL):
            coef, ex, ez = P.contract_O9(c['pd'], cand, Rb, AVs[ci])
            n_contracts += 1
            if h is not None and k == 0:
                h.update(repr((c['patch'], c['panel'], c['shift'])).encode())
                for r_ in coef:
                    for v_ in r_: h.update(repr(exact(v_)).encode())
                h.update(repr(exact(ex)).encode()); h.update(repr(exact(ez)).encode())
    if h is not None: sci = h.hexdigest()
w1 = time.monotonic()
ru1 = resource.getrusage(resource.RUSAGE_SELF)
probe_after = rate_probe()

json.dump({
  "wid": a.wid, "cand": a.cand, "packets": a.packets,
  "contracts": n_contracts,
  "wall_s": w1 - w0,
  "user_s": ru1.ru_utime - ru0.ru_utime,
  "sys_s":  ru1.ru_stime - ru0.ru_stime,
  "cpu_s": (ru1.ru_utime - ru0.ru_utime) + (ru1.ru_stime - ru0.ru_stime),
  "maxrss_kib": ru1.ru_maxrss,
  "vol_ctx_switches": ru1.ru_nvcsw - ru0.ru_nvcsw,
  "invol_ctx_switches": ru1.ru_nivcsw - ru0.ru_nivcsw,
  "minor_faults": ru1.ru_minflt - ru0.ru_minflt,
  "major_faults": ru1.ru_majflt - ru0.ru_majflt,
  "probe_rate_before": probe_before, "probe_rate_after": probe_after,
  "scientific_hash": sci,
  "thread_env": env, "thread_env_violations": bad,
  "affinity": sorted(os.sched_getaffinity(0)),
  "baseline_check": baseline_check,
  "n_contexts": len(ctxs),
}, open(a.out, "w"), indent=1)
