"""P5Y Gate-1 optional predeclared checks.  NON-DECISIVE for the Gate-1 verdict."""
from __future__ import annotations

import json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in (str(ROOT / "rebaseguard-proof" / "src"),):
    if p not in sys.path:
        sys.path.insert(0, p)
from flint import arb                                                        # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, gaussian_cdf, rational, workprec  # noqa: E402

BITS = 192
C_CUSUM = arb(11) / arb(2)
C_SR = arb("6.75553146432147308692733728672")


# ---------------------------------------------------------------- MSHARE
def function_sets(m: int):
    """Certified backward functions required by P5X-T1(c) and PROOF.md L2 for window m.

    Every name is defined WITHOUT reference to m (PROOF.md L1.5-L1.7, L2.4-L2.6);
    m enters only the finite assembly.  Hence the sets are nested in m.
    """
    first = {f"g_{r}" for r in range(m)} | {f"dg_{r}" for r in range(m)}
    first |= {f"h_{j}" for j in range(1, m)} | {f"S_{j}" for j in range(m)}
    second = {f"G_{r}_{rp}" for r in range(m) for rp in range(r + 1)}
    second |= {f"dG_{r}_{rp}" for r in range(m) for rp in range(r + 1)}
    return first, second


def mshare_check():
    ms = [1, 2, 3, 5]
    sets = {m: function_sets(m) for m in ms}
    f5, s5 = sets[5]
    nested = all(sets[m][0] <= f5 and sets[m][1] <= s5 for m in ms)
    # the m=2 assembly cites only names present in the m=5 set
    m2_first, m2_second = sets[2]
    m2_specific = (m2_first - f5) | (m2_second - s5)
    union_first, union_second = set(), set()
    for m in ms:
        union_first |= sets[m][0]; union_second |= sets[m][1]
    hist_first = sum(4 * m - 2 for m in ms)          # historical lane: sum over m
    hist_second = sum(m * (m + 1) for m in ms)
    return {"nested_in_m": bool(nested),
            "m2_functions_absent_from_m5_set": sorted(m2_specific),
            "no_m_specific_solve": bool(not m2_specific),
            "union_first_moment_functions": len(union_first),
            "union_second_moment_functions": len(union_second),
            "union_total": len(union_first) + len(union_second),
            "historical_lane_first": hist_first,
            "historical_lane_second": hist_second,
            "historical_lane_total": hist_first + hist_second,
            "corrected_multiplier_units": (len(union_first) + len(union_second)) / 2,
            "historical_multiplier_units": (hist_first + hist_second) / 2,
            "overcount_factor": (hist_first + hist_second) / (len(union_first) + len(union_second)),
            "verdict": "PASS" if (nested and not m2_specific) else "FAIL"}


# ------------------------------------------------------------- FARFIELD2
def B1(a):
    q = gaussian_cdf(a)
    m2 = gaussian_cdf(a) + a.abs_upper() * (-(a * a) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
    m2 = m2 + q / (arb(1) - q)
    phi_a = (-(a * a) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
    return phi_a + (q * m2).sqrt()


def B2(a):
    q = gaussian_cdf(a)
    phi_a = (-(a * a) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
    return arb(2) * (q + a.abs_upper() * phi_a) + q / (arb(1) - q)


def farfield2_check():
    rows = []
    for name, c in (("cusum", C_CUSUM), ("sr", C_SR)):
        for e in (arb(10), arb(12)):
            a = c - e
            b1, b2 = B1(a), B2(a)
            s_low = arb(1) - b2 - b1 * b1
            rows.append({"detector": name, "e": float(e), "a": float(a),
                         "B1_first_moment": ball_record(b1), "B1_float": float(b1.upper()),
                         "B2_second_moment": ball_record(b2), "B2_float": float(b2.upper()),
                         "M2_upper_far": float((arb(1) + b2).upper()),
                         "S_lower_far": float(s_low.lower()),
                         "S_lower_positive": bool(s_low.lower() > 0)})
    return {"rows": rows,
            "verdict": "PASS" if all(r["S_lower_positive"] for r in rows) else "FAIL",
            "note": "outward-rounded Arb; supports the proposed L3' far-field lemma. "
                    "Not a proof of L3' itself, which is a human lemma."}


# --------------------------------------------------------- SMIN-ANALYTIC
def trunc_var(Lb, Ub):
    """Var(raw | raw not in (Lb,Ub)) for raw ~ N(0,1), exact Arb expressions."""
    phi = lambda x: (-(x * x) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
    pL = gaussian_cdf(Lb)
    pU = arb(1) - gaussian_cdf(Ub)
    p = pL + pU
    if not p.lower() > 0:
        return None
    m1 = (-phi(Lb) + phi(Ub)) / p          # E[raw ; raw<L] = -phi(L); E[raw; raw>U] = phi(U)
    e2 = ((gaussian_cdf(Lb) - Lb * phi(Lb)) + ((arb(1) - gaussian_cdf(Ub)) + Ub * phi(Ub))) / p
    return e2 - m1 * m1


def smin_analytic_check():
    """SCOPING CHECK, not a certificate: deterministic scan of the reachable
    threshold box for CUSUM.  L = x^- - c + e in [e-c, e-c+h), U = c - x^+ + e in
    (e+c-h, e+c].  Reports the minimum conditional variance found."""
    best = None
    with workprec(BITS):
        c = C_CUSUM
        for ei in range(0, 121):
            e = arb(ei) / arb(10)
            for i in range(0, 21):
                for j in range(0, 21):
                    xm = arb(5) * arb(i) / arb(20)
                    xp = arb(5) * arb(j) / arb(20)
                    Lb = xm - c + e
                    Ub = c - xp + e
                    v = trunc_var(Lb, Ub)
                    if v is None:
                        continue
                    val = float(v.lower())
                    if best is None or val < best[0]:
                        best = (val, float(e), float(Lb), float(Ub))
    return {"kind": "SCOPING_CHECK_NOT_A_CERTIFICATE",
            "grid": "e in [0,12] step 0.1 x 21x21 state grid",
            "min_conditional_variance_found": best[0],
            "at": {"e": best[1], "L": best[2], "U": best[3]},
            "strictly_positive": bool(best[0] > 0),
            "implied_s_min_lower_m1": best[0],
            "implied_s_min_lower_m5": best[0] / 25.0,
            "verdict": "PASS" if best[0] > 0 else "FAIL",
            "caveat": "a finite scan is not an infimum proof; a successor must "
                      "certify inf over the continuum. Non-decisive for Gate-1."}


def main():
    t0 = time.time()
    with workprec(BITS):
        out = {"schema": "rebaseguard.p5y.gate1.optional.v1", "binding": False,
               "decisive": False,
               "generated_utc": datetime.now(timezone.utc).isoformat(),
               "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                            capture_output=True, text=True).stdout.strip(),
               "PILOT_MSHARE": mshare_check(),
               "PILOT_FARFIELD2": farfield2_check(),
               "PILOT_SMIN_ANALYTIC": smin_analytic_check()}
    out["runtime"] = {"wall_seconds": time.time() - t0}
    (HERE / "results" / "optional_checks.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: (v if k != "PILOT_FARFIELD2" else
                          {"verdict": v["verdict"],
                           "rows": [{kk: r[kk] for kk in ("detector", "e", "B1_float",
                                                          "B2_float", "S_lower_far")}
                                    for r in v["rows"]]})
                      for k, v in out.items() if k.startswith("PILOT")}, indent=1))


if __name__ == "__main__":
    main()
