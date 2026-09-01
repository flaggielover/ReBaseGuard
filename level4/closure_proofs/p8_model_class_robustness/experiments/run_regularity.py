"""G1d / G1e: exact regularity identities and the independent-implementation check.

Cheap, deterministic, no Monte Carlo.  Run first.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8 import families as F                      # noqa: E402
from rebaseguard_p8.config import (                           # noqa: E402
    FAMILIES, RESULTS, P4, stage_d_cusum_thresholds)


def p4_reference():
    sys.path.insert(0, str(P4 / "src"))
    from rebaseguard_location_family import route_a            # noqa: E402
    return route_a


def main() -> None:
    ra = p4_reference()
    import json as _json
    from rebaseguard_p8.config import STAGE_D
    d3 = _json.loads((STAGE_D / "results" / "d3_nongaussian.json").read_text())
    e_psi_prime = {r["family"]: float(r["E_psi_prime"]) for r in d3["rows"]}

    grid = np.concatenate([np.linspace(-12.0, 12.0, 4801),
                           np.array([0.0, 1e-9, -1e-9, 30.0, -30.0])])
    rows = []
    for name in FAMILIES:
        fam = F.get(name)
        e_zpsi = F.expected_z_psi(fam)
        e_psi = F.expected_psi(fam)
        info = F.fisher_information(fam)
        fd = F.score_by_finite_difference(fam, np.linspace(-6, 6, 121))
        fd_err = float(np.max(np.abs(fam.psi(np.linspace(-6, 6, 121)) - fd)))
        p4_psi = ra.location_score(name, grid)
        p8_psi = fam.psi(grid)
        score_diff = float(np.max(np.abs(p4_psi - p8_psi)))
        p4_lp = ra.log_density(name, grid)
        p8_lp = fam.logpdf(grid)
        lp_diff = float(np.max(np.abs(p4_lp - p8_lp)))
        rows.append({
            "family": name,
            "variance": fam.variance,
            "tail_moment_order": fam.tail_moment_order,
            "E_z_psi": e_zpsi, "E_z_psi_error": abs(e_zpsi - 1.0),
            "E_psi": e_psi,
            "fisher_information": info,
            "stage_d_E_psi_prime": e_psi_prime[name],
            "fisher_vs_stage_d_abs_diff": abs(info - e_psi_prime[name]),
            "psi_vs_finite_difference_max_abs": fd_err,
            "psi_vs_P4_route_a_max_abs": score_diff,
            "logpdf_vs_P4_route_a_max_abs": lp_diff,
            "gamma_integrand_second_moment_finite": fam.tail_moment_order > 2,
            "gamma_integrand_third_moment_finite": fam.tail_moment_order > 3,
        })

    # distributional check of the independently written draw() against P4's
    draw_rows = []
    for name in FAMILIES:
        fam = F.get(name)
        a = fam.draw(np.random.Generator(np.random.Philox(11)), 400_000)
        b = ra.draw_innovations(name, np.random.Generator(np.random.Philox(11)),
                                400_000)
        from scipy import stats
        ks = stats.ks_2samp(a, b)
        draw_rows.append({"family": name, "p8_var": float(a.var()),
                          "p4_var": float(b.var()),
                          "ks_stat": float(ks.statistic),
                          "ks_p": float(ks.pvalue), "n": 400_000})

    thr = stage_d_cusum_thresholds()
    out = {
        "schema": "rebaseguard.p8.family-regularity.v1",
        "note": ("E[eps psi(eps)] = 1 and E[psi(eps)] = 0 are exact for every "
                 "regular location family (P8-L1(a)); the Fisher information "
                 "must reproduce Stage-D's independently computed E[psi']."),
        "rows": rows,
        "draw_distribution_check": draw_rows,
        "stage_d_cusum_thresholds": thr,
        "gates": {
            "G1d_E_z_psi_max_error": max(r["E_z_psi_error"] for r in rows),
            "G1d_E_psi_max_abs": max(abs(r["E_psi"]) for r in rows),
            "G1d_fisher_max_abs_diff": max(r["fisher_vs_stage_d_abs_diff"]
                                           for r in rows),
            "G1d_pass": bool(max(r["E_z_psi_error"] for r in rows) <= 1e-4
                             and max(abs(r["E_psi"]) for r in rows) <= 1e-8
                             and max(r["fisher_vs_stage_d_abs_diff"]
                                     for r in rows) <= 1e-6),
            "G1e_psi_max_abs_diff": max(r["psi_vs_P4_route_a_max_abs"]
                                        for r in rows),
            "G1e_logpdf_max_abs_diff": max(r["logpdf_vs_P4_route_a_max_abs"]
                                           for r in rows),
            "G1e_pass": bool(max(r["psi_vs_P4_route_a_max_abs"]
                                 for r in rows) <= 1e-12),
        },
    }
    p = RESULTS / "family_regularity.json"
    p.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["gates"], indent=1))


if __name__ == "__main__":
    main()
