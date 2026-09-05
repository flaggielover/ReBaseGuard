"""T2O: profile the baseline, gate correctness, then time the frozen routes."""
from __future__ import annotations

import json, resource, statistics, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
T1R = ROOT / "level4/closure_proofs/p5y_k1_task1r_budget_harness"
for p in (str(HERE), str(T1R / "code")):
    if p not in sys.path:
        sys.path.insert(0, p)

from flint import arb                                                  # noqa: E402
import harness as H                                                    # noqa: E402
import sr_local as L                                                   # noqa: E402
import opt_backend as O                                                # noqa: E402
from rebaseguard_certify.arb_backend import rational, workprec         # noqa: E402

CFG = json.loads((NS / "config/frozen_audit.json").read_text())
D = json.loads((T1R / "config/frozen_parameters.json").read_text())["selection"]["D_selected"]
Z = json.loads((T1R / "config/frozen_parameters.json").read_text())["selection"]["Z_selected"]
REPS = 3                                    # frozen repetitions
SR_CELLS = CFG["work_model"]["SR_subcells"]
NFUN = CFG["work_model"]["functions_per_detector"]
EVALS = CFG["work_model"]["SR_panel_evaluations"]
CUSUM = CFG["work_model"]["CUSUM_projection_cpu_h"]
OVH = CFG["work_model"]["overhead_factor"]
CAP = CFG["immutable_history"]["HARD_CPU_CAP_historical"]


def geom_for(patch):
    A, b, c = L.sr_constants()
    e = rational(H.E_NUM, H.E_DEN)
    geo = L.patch_geometry(*patch, grid=H.GRID)
    p_c = (geo["yp"][0] + geo["yp"][1]) / arb(2)
    m_c = (geo["ym"][0] + geo["ym"][1]) / arb(2)
    Hh = (geo["yp"][1] - geo["yp"][0]) / arb(2)
    U_c, L_c = c - p_c, m_c - c
    return dict(A=A, b=b, c=c, e=e, geo=geo, p_c=p_c, m_c=m_c, H=Hh,
                U_c=U_c, L_c=L_c, span=U_c - L_c)


def unit_cand(v=None):
    cc = [[arb(0)] * (H.CAND_DEGREE + 1) for _ in range(H.CAND_DEGREE + 1)]
    if v is not None:
        cc[0][0] = arb(v)
    return cc


def build_ref_candidate(g):
    sys.path.insert(0, str(ROOT / "level4/closure_proofs/p5y_k1_binding_campaign/task1"))
    from task1_f0 import build_candidate
    return build_candidate(float(g["b"]), float(g["c"]), float(g["e"]))[0]


def overlaps(x: arb, y: arb) -> bool:
    return not (x.lower() > y.upper() or y.lower() > x.upper())


def profile_baseline(g, p1, cand):
    """ROUTE-INDEPENDENT profile of where the qualified backend's time goes."""
    b = g["b"]
    n_z = p1["n_panels"]
    h = g["span"] / (arb(2) * arb(n_z))
    Hp = [g["H"] ** a for a in range(2 * D + 2)]
    hp = [h ** k for k in range(2 * Z + 2)]
    ctxt = (g["H"], h, D, Z, Hp, hp)
    half = arb(1) / arb(2)
    z_c = g["L_c"] + h
    z_lo, z_hi = z_c - h, z_c + h
    t = {}
    t0 = time.process_time()
    V = H.softplus_tm2(g["p_c"] + z_c - half, ctxt, +1)
    W = H.softplus_tm2(g["m_c"] - z_c - half, ctxt, -1)
    t["softplus_source_expansion"] = time.process_time() - t0
    t0 = time.process_time()
    TV = H.cheb_tm2(V.scaled(arb(2) / b, shift=arb(-1)), H.CAND_DEGREE)
    TW = H.cheb_tm2(W.scaled(arb(2) / b, shift=arb(-1)), H.CAND_DEGREE)
    t["chebyshev_composition_tensors"] = time.process_time() - t0
    t0 = time.process_time()
    N = H.panel_moments(z_lo, z_hi, z_c, g["e"], 2 * Z + 1, h)
    t["gaussian_moment_construction"] = time.process_time() - t0
    t0 = time.process_time()
    for i in range(H.CAND_DEGREE + 1):
        inner = H.TM2.zero(ctxt)
        for j in range(H.CAND_DEGREE + 1):
            if not cand[i][j].is_zero():
                inner = inner + TW[j].scaled(cand[i][j])
    t["candidate_inner_combination"] = time.process_time() - t0
    t0 = time.process_time()
    coef = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    for i in range(H.CAND_DEGREE + 1):
        inner = H.TM2.zero(ctxt)
        for j in range(H.CAND_DEGREE + 1):
            if not cand[i][j].is_zero():
                inner = inner + TW[j].scaled(cand[i][j])
        P, Q = TV[i], inner
        P.mag(); Q.mag()
        for a in range(D + 1):
            prow = P.c[a]
            if all(x.is_zero() for x in prow):
                continue
            for bq in range(D + 1):
                qrow = Q.c[bq]
                acc = arb(0)
                for k1, pk in enumerate(prow):
                    if pk.is_zero():
                        continue
                    for k2, qk in enumerate(qrow):
                        if not qk.is_zero():
                            acc += pk * qk * N[k1 + k2]
                coef[a][bq] += acc
    t["taylor_coefficient_contraction"] = time.process_time() - t0 - t["candidate_inner_combination"]
    return t


def time_call(fn, reps=REPS):
    ts = []
    for _ in range(reps):
        t0 = time.process_time()
        fn()
        ts.append(time.process_time() - t0)
    return {"median": statistics.median(ts), "min": min(ts), "max": max(ts),
            "spread": (max(ts) - min(ts)) / statistics.median(ts) if statistics.median(ts) else 0.0}


def main() -> int:
    t_audit = time.process_time()
    out = {"schema": "rebaseguard.p5y.k1.srbackend.bench.v1", "binding": True,
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                        capture_output=True, text=True).stdout.strip(),
           "D": D, "Z": Z, "timing_repetitions": REPS}

    with workprec(H.PROD_BITS):
        gA = geom_for(tuple(CFG["benchmark_cells"][0]["patch"]))
        p1A = H.p1_rule(gA["H"], gA["span"])
        cand = build_ref_candidate(gA)

        # ---------- 1. baseline profile
        prof = profile_baseline(gA, p1A, cand)
        tot_prof = sum(prof.values())
        t0 = time.process_time()
        H.run_panels(cand, D, Z, gA, p1A, only_panel=0)
        one_panel = time.process_time() - t0
        out["cost_profile_baseline"] = {
            "absolute_seconds": prof, "profiled_sum": tot_prof,
            "measured_single_panel": one_panel,
            "reconciliation_ratio": tot_prof / one_panel,
            "percent": {k: 100 * v / tot_prof for k, v in prof.items()}}

        # ---------- 2. CORRECTNESS GATE (before any speed claim)
        base = H.run_panels(cand, D, Z, gA, p1A, only_panel=0)
        opt = O.run_panels_opt(cand, D, Z, gA, p1A, only_panel=0)
        bad = []
        maxrel = 0.0
        for a in range(D + 1):
            for bq in range(D + 1):
                x, y = base[0][a][bq], opt[0][a][bq]
                if not overlaps(x, y):
                    bad.append((a, bq))
                m = max(abs(float(x.mid())), abs(float(y.mid())))
                if m > 0:
                    maxrel = max(maxrel, abs(float(x.mid()) - float(y.mid())) / m)
        out["correctness"] = {
            "coefficients_compared": (D + 1) ** 2,
            "enclosure_overlap_failures": bad,
            "max_relative_midpoint_difference": maxrel,
            "baseline_ex": float(base[1].abs_upper()), "opt_ex": float(opt[1].abs_upper()),
            "baseline_ez": float(base[2].abs_upper()), "opt_ez": float(opt[2].abs_upper()),
            "opt_error_is_conservative": (float(opt[1].abs_upper()) >= float(base[1].abs_upper())
                                          and float(opt[2].abs_upper()) >= float(base[2].abs_upper())),
            "PASS": not bad}

        # ---------- 3. timing on the frozen benchmark set
        cells = {}
        for spec in CFG["benchmark_cells"]:
            if spec["id"] == "E_cusum_control":
                continue
            patch = tuple(spec["patch"])
            g = geom_for(patch)
            p1 = H.p1_rule(g["H"], g["span"])
            cd = cand if spec["object"] == "F_0" else unit_cand(1)
            tb = time_call(lambda: H.run_panels(cd, D, Z, g, p1, only_panel=0))
            sc, dc = {}, {}
            t_sh = time_call(lambda: O.PanelShared(
                g["p_c"], g["m_c"], g["L_c"] + g["span"] / (arb(2) * arb(p1["n_panels"])),
                g["b"], (g["H"], g["span"] / (arb(2) * arb(p1["n_panels"])), D, Z,
                         [g["H"] ** a for a in range(2 * D + 2)],
                         [(g["span"] / (arb(2) * arb(p1["n_panels"]))) ** k
                          for k in range(2 * Z + 2)])))
            O.run_panels_opt(cd, D, Z, g, p1, only_panel=0, shared_cache=sc, drift_cache=dc)
            t_full = time_call(lambda: O.run_panels_opt(cd, D, Z, g, p1, only_panel=0,
                                                        shared_cache={}, drift_cache={}))
            t_warm = time_call(lambda: O.run_panels_opt(cd, D, Z, g, p1, only_panel=0,
                                                        shared_cache=sc, drift_cache=dc))
            t_drift = max(t_full["median"] - t_sh["median"] - t_warm["median"], 0.0)
            amort = t_sh["median"] / (SR_CELLS * NFUN) + t_drift / NFUN + t_warm["median"]
            cells[spec["id"]] = {
                "patch": list(patch), "n_panels": p1["n_panels"],
                "baseline_t_panel": tb, "opt_shared_build": t_sh,
                "opt_cold_total": t_full, "opt_per_function": t_warm,
                "opt_drift_stage": t_drift,
                "amortized_t_panel": amort,
                "speedup_vs_task1r": tb["median"] / amort if amort > 0 else float("inf"),
            }
        out["cells"] = cells

    # ---------- 4. CUSUM control
    sys.path.insert(0, str(ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics"
                           / "certified_method_repair_ra"))
    import ra_certifier as RA
    t0 = time.process_time()
    RA.certify_at_exact_drift(1, 4)
    out["cusum_control"] = {"t_certify_s": time.process_time() - t0,
                            "reference_s": 234.10,
                            "regression": abs(time.process_time() - t0 - 234.10) / 234.10}

    out["runtime"] = {"cpu_seconds": time.process_time() - t_audit,
                      "cpu_hours": (time.process_time() - t_audit) / 3600,
                      "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2)}
    (NS / "results").mkdir(exist_ok=True)
    (NS / "results" / "benchmark.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("cost_profile_baseline", "correctness")}, indent=1))
    for k, v in cells.items():
        print("%-16s baseline %.4f s  amortized %.6f s  speedup %.1fx"
              % (k, v["baseline_t_panel"]["median"], v["amortized_t_panel"], v["speedup_vs_task1r"]))
    print("CUSUM control %.1f s (ref 234.1)" % out["cusum_control"]["t_certify_s"])
    print("audit CPU %.1f s" % out["runtime"]["cpu_seconds"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
