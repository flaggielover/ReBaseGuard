"""Stage D adversarial suite -- all 12 protocol checks, reported pass or fail.

Tolerances are fixed here and are never widened after a result is seen. A check
that fails is diagnosed in notes/FAILURE_DIAGNOSES.md and left failed.
"""
from __future__ import annotations

import hashlib
import json
import platform
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stopped import CUSUM, SR, simulate_stopped              # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = RES / "adversarial_d.json"
SEED_ALT = 20261002                 # independent replication family
Z = 1.959964
PROTOCOL_SHA = "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e"
STAGE_B_ENCLOSURE = (3.9243482, 27.8493821)


def load(name):
    return json.loads((RES / name).read_text())


def gamma_run(detector, threshold, n, m_grid, L, key, **kw):
    ss = np.random.SeedSequence(key)
    batch = min(250_000, n)
    stats = None
    for child in ss.spawn(max(n // batch, 1)):
        rng = np.random.Generator(np.random.PCG64(child))
        s = simulate_stopped(detector=detector, threshold=threshold, e=0.0,
                             n_paths=batch, L=L, m_grid=np.asarray(m_grid),
                             rng=rng, **kw)
        stats = s if stats is None else stats.combine(s)
    return stats


def main() -> None:
    t0 = time.time()
    checks = []

    def add(cid, name, passed, detail):
        checks.append({"id": cid, "check": name, "passed": bool(passed),
                       **detail})
        print(f"  [{cid:>4}] {'PASS' if passed else 'FAIL'}  {name}", flush=True)

    d1 = load("d1_gamma.json")
    d2 = load("d2_gamma_m.json")
    d23 = load("d2_3_derivative.json")
    cal = load("calibration_d1.json")

    # A1 -- independent seed family --------------------------------------
    s = gamma_run(CUSUM, 5.0, 1_000_000, [1, 20, 100], 100, [SEED_ALT, 1, 0])
    g_alt = s.gamma_m("A")
    ref = {r["m"]: (r["A"]["gamma_m"], r["A"]["se"]) for r in d2["rows"]}
    devs = []
    for j, m in enumerate((1, 20, 100)):
        g0, se0 = ref[m]
        se = float(np.hypot(se0, s.gamma_m_se("A")[j]))
        devs.append(abs(float(g_alt[j]) - g0) / se)
    add("A1", "independent seed family 20261002 reproduces Gamma_m",
        max(devs) < 3.0,
        {"m": [1, 20, 100], "gamma_alt": [float(v) for v in g_alt],
         "n_combined_se": devs, "tolerance": "max deviation < 3 SE"})

    # A2 -- CRN on/off for the D1.3 difference ----------------------------
    ss = np.random.SeedSequence([SEED_ALT, 2, 0])
    A = cal["sr"]["threshold"]
    crn_child = ss.spawn(1)[0]
    r_sr = simulate_stopped(detector=SR, threshold=A, e=0.0, n_paths=500_000,
                            L=2, m_grid=np.array([1]),
                            rng=np.random.Generator(np.random.PCG64(crn_child)))
    r_cu = simulate_stopped(detector=CUSUM, threshold=5.0, e=0.0, n_paths=500_000,
                            L=2, m_grid=np.array([1]),
                            rng=np.random.Generator(np.random.PCG64(crn_child)))
    d_crn = float(r_sr.gamma_m("A")[0] - r_cu.gamma_m("A")[0])
    d_ind = d1["d1_3"]["difference"]
    se_ind = d1["d1_3"]["se"]
    add("A2", "CRN on/off: SR-CUSUM excess has the same sign and magnitude",
        abs(d_crn - d_ind) < 5.0 * se_ind and d_crn > 0,
        {"difference_crn": d_crn, "difference_independent": d_ind,
         "se_independent": se_ind,
         "note": ("CRN couples the innovation stream, so its SE is not the "
                  "unpaired SE; only sign and magnitude are compared.")})

    # A3 -- estimator variant: convention A vs B, bootstrap vs normal CI ---
    ok_ci = True
    ci_detail = []
    for r in d2["rows"]:
        n_ci, b_ci = r["A"]["ci_normal"], r["A"]["ci_bootstrap"]
        width_ratio = (b_ci[1] - b_ci[0]) / (n_ci[1] - n_ci[0])
        overlap = not (b_ci[1] < n_ci[0] or n_ci[1] < b_ci[0])
        ci_detail.append({"m": r["m"], "width_ratio": width_ratio,
                          "overlap": overlap})
        ok_ci &= overlap and 0.5 < width_ratio < 2.0
    add("A3", "batch bootstrap and normal CI agree at every m", ok_ci,
        {"per_m": ci_detail, "tolerance": "overlap and width ratio in (0.5, 2)"})

    # A4 -- finite-difference step variation (already run in D2.3) --------
    orders = []
    for r in d23["rows"]:
        b = r["by_step"]
        orders.append(float(np.log2(abs(b["0.05"]["discrepancy"]
                                        / b["0.025"]["discrepancy"]))))
    add("A4", "FD discrepancy shrinks at the O(h^2) rate (D2.3 diagnosis)",
        1.5 < float(np.mean(orders)) < 2.5,
        {"observed_orders": orders, "mean_order": float(np.mean(orders)),
         "note": ("This check validates the DIAGNOSIS of the D2.3 failure. It "
                  "does NOT convert D2.3 into a pass; D2.3 remains FAILED.")})

    # A5 -- threshold recalibration uncertainty ---------------------------
    lo_thr = cal["sr"]["trace"][-1]["threshold"]
    s_lo = gamma_run(SR, lo_thr, 500_000, [1], 2, [SEED_ALT, 5, 0])
    dg = abs(float(s_lo.gamma_m("A")[0]) - d1["sr"]["gamma"])
    add("A5", "Gamma_SR is stable under threshold recalibration uncertainty",
        dg < 0.5,
        {"threshold_used": lo_thr, "threshold_primary": A,
         "gamma_at_alt_threshold": float(s_lo.gamma_m("A")[0]),
         "gamma_primary": d1["sr"]["gamma"], "abs_change": dg,
         "tolerance": "abs change < 0.5"})

    # A6 -- interpolation-method variation for m* -------------------------
    ms = np.array([r["m"] for r in d2["rows"]], float)
    gs = np.array([r["A"]["gamma_m"] for r in d2["rows"]], float)
    j = int(np.where(ms == d2["d2_2_bracket"]["m_lo"])[0][0])
    lo, hi, glo, ghi = ms[j], ms[j + 1], gs[j], gs[j + 1]
    f = (glo - 2.0) / (glo - ghi)
    m_log = float(np.exp(np.log(lo) + f * (np.log(hi) - np.log(lo))))
    m_lin = float(lo + f * (hi - lo))
    k = np.polyfit(np.log(ms[j - 1:j + 3]), gs[j - 1:j + 3], 2)
    rr = np.roots([k[0], k[1], k[2] - 2.0])
    rr = [float(np.exp(x.real)) for x in rr if abs(x.imag) < 1e-9
          and lo <= np.exp(x.real) <= hi]
    m_quad = rr[0] if rr else float("nan")
    spread = max(m_log, m_lin) - min(m_log, m_lin)
    add("A6", "m* is insensitive to the interpolation method",
        spread < 0.1 * m_log and lo <= m_log <= hi,
        {"linear_in_log_m": m_log, "linear_in_m": m_lin,
         "local_quadratic_in_log_m": m_quad, "bracket": [lo, hi],
         "spread": spread, "tolerance": "spread < 10% of m*",
         "note": "The BRACKET, not the interpolated point, is the primary object."})

    # A7 -- direct vs decomposed Gamma_m ----------------------------------
    lag = np.array(d2["d2_1_lag"]["gamma_first_10"])
    b10 = [r for r in d2["rows"] if r["m"] == 10][0]["B"]["gamma_m"]
    dec = float(lag[:10].mean())
    add("A7", "convention B equals the lag decomposition; convention A does not",
        abs(dec - b10) < 1e-6,
        {"decomposed_first_10_mean": dec, "gamma_10_convention_B": b10,
         "gamma_10_convention_A":
             [r for r in d2["rows"] if r["m"] == 10][0]["A"]["gamma_m"],
         "note": ("The blueprint's closed form holds for B by construction and "
                  "is FALSE for the frozen convention A -- see "
                  "notes/CORRESPONDENCE_AUDIT.md Addendum A1.")})

    # A8 -- tau < m edge cases --------------------------------------------
    s_edge = gamma_run(CUSUM, 5.0, 500_000, [1, 100], 100, [SEED_ALT, 8, 0])
    frac = float((s_edge.lag_cnt[99] / s_edge.n))
    ratio = float(s_edge.gamma_m("B")[1] / s_edge.gamma_m("A")[1])
    add("A8", "tau < m paths are handled and drive the A/B divergence",
        0.0 < 1 - frac < 1.0 and ratio < 1.0,
        {"P(tau > 100)": frac, "P(tau <= 100)": 1 - frac,
         "gamma_B_over_gamma_A_at_m100": ratio,
         "note": ("B <= A because B keeps denominator m on short cycles. A "
                  "ratio of exactly 1 would mean the edge case never occurs.")})

    # A9 -- larger Monte Carlo subset -------------------------------------
    s_big = gamma_run(CUSUM, 5.0, 4_000_000, [1], 2, [SEED_ALT, 9, 0])
    g1_ref, se1_ref = ref[1]
    se = float(np.hypot(se1_ref, s_big.gamma_m_se("A")[0]))
    dev = abs(float(s_big.gamma_m("A")[0]) - g1_ref) / se
    add("A9", "4M-cycle run agrees with the 2M primary", dev < 3.0,
        {"gamma_4M": float(s_big.gamma_m("A")[0]),
         "se_4M": float(s_big.gamma_m_se("A")[0]),
         "gamma_primary": g1_ref, "n_combined_se": dev,
         "tolerance": "< 3 SE"})

    # A10 -- implementation equivalence: m=1 vs the Stage B enclosure ------
    g1 = ref[1][0]
    inside = STAGE_B_ENCLOSURE[0] < g1 < STAGE_B_ENCLOSURE[1]
    add("A10", "Gamma at m=1 lies inside the Stage B certified enclosure",
        inside,
        {"gamma_m1": g1, "certified_enclosure": list(STAGE_B_ENCLOSURE),
         "note": ("A Monte Carlo value sitting inside a certified enclosure is "
                  "a consistency check on this simulator. It adds nothing to "
                  "the certificate.")})

    # A11 -- outcome-blind code guard -------------------------------------
    # Outcome values are DERIVED from the confirmatory results, never retyped
    # here: a literal list would (and on first run did) match itself when this
    # file was scanned, producing a false failure. This file is also excluded
    # from the scan, since holding measured values is precisely its job.
    d14 = load("d1_4_sr_map.json")
    d25 = load("d2_5_bridge.json")
    d3f = load("d3_nongaussian.json")
    measured = [
        d2["rows"][0]["A"]["gamma_m"], d1["sr"]["gamma"], d1["cusum"]["gamma"],
        d2["d2_2_bracket"]["m_star_interp"],
        d2["d2_4_asymptote"]["gamma_inf_A_E_Tsq_over_tau"],
        d2["d2_1_lag"]["arl0"], cal["sr"]["threshold"],
        d14["sr"]["root"], d14["cusum"]["root"],
        d25["rows"][0]["cycle_arl"]["mean"],
        d3f["rows"][0]["per_m"][0]["gamma_psi"],
    ]
    # 4- and 6-significant-figure renderings of each measured outcome
    outcomes = sorted({f"{abs(v):.{k}g}" for v in measured for k in (4, 6)
                       if abs(v) > 1e-12})
    src = ROOT / "src"
    hits = []
    for f in sorted(src.glob("*.py")):
        if f.name == Path(__file__).name:
            continue                       # the checker itself is exempt
        txt = f.read_text()
        code = re.sub(r'""".*?"""', "", txt, flags=re.S)
        code = re.sub(r"#.*", "", code)
        for v in outcomes:
            if v in code:
                hits.append({"file": f.name, "value": v})
    add("A11", "no measured outcome value is hard-coded in executable source",
        not hits,
        {"n_values_scanned": len(outcomes), "values_scanned": outcomes,
         "hits": hits,
         "exempt": [Path(__file__).name],
         "note": ("Values are derived from the results files at 4 and 6 "
                  "significant figures. Docstrings and comments are stripped; "
                  "executable code is not.")})

    # A12 -- protocol hash verification -----------------------------------
    actual = hashlib.sha256(
        (ROOT / "STAGE_D_PROTOCOL.md").read_bytes()).hexdigest()
    add("A12", "frozen protocol hash still matches", actual == PROTOCOL_SHA,
        {"expected": PROTOCOL_SHA, "actual": actual})

    n_pass = sum(c["passed"] for c in checks)
    out = {"suite": "Stage D adversarial", "n_checks": len(checks),
           "n_passed": n_pass, "n_failed": len(checks) - n_pass,
           "protocol_sha256": PROTOCOL_SHA,
           "independent_seed_family": SEED_ALT,
           "checks": checks,
           "evidence_status": "NEW-NUMERICAL",
           "python": platform.python_version(), "numpy": np.__version__,
           "elapsed_s": round(time.time() - t0, 1)}
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  {n_pass}/{len(checks)} adversarial checks passed", flush=True)
    print(f"  -> {OUT}  ({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
