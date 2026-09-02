"""S4 / S2(b): exact regularity identities and the independent-implementation
check against P4's ``route_a``.

Cheap, deterministic, no Monte Carlo, no random address consumed at all.  Run
first.

Usage:  run_regularity.py
"""
from __future__ import annotations

import json
import sys

import numpy as np

import _common as C                                              # noqa: E402
from rebaseguard_p8r import families as F                        # noqa: E402
from rebaseguard_p8r.config import (FAMILIES, P4, RESULTS,       # noqa: E402
                                     S2_SCORE_TOL, S4_EPSI_TOL, S4_EZPSI_TOL,
                                     S4_FISHER_TOL, stage_d_cusum_thresholds,
                                     stage_d_psi_prime)


def p4_reference():
    sys.path.insert(0, str(P4 / "src"))
    from rebaseguard_location_family import route_a               # noqa: E402
    return route_a


def main() -> None:
    ra = p4_reference()
    e_psi_prime = stage_d_psi_prime()

    grid = np.concatenate([np.linspace(-12.0, 12.0, 4801),
                           np.array([0.0, 1e-9, -1e-9, 30.0, -30.0])])
    rows = []
    for name in FAMILIES:
        fam = F.get(name)
        e_zpsi = F.expected_z_psi(fam)
        e_psi = F.expected_psi(fam)
        info = F.fisher_information(fam)
        xs = np.linspace(-6, 6, 121)
        fd_err = float(np.max(np.abs(fam.psi(xs)
                                     - F.score_by_finite_difference(fam, xs))))
        score_diff = float(np.max(np.abs(ra.location_score(name, grid)
                                         - fam.psi(grid))))
        lp_diff = float(np.max(np.abs(ra.log_density(name, grid)
                                      - fam.logpdf(grid))))
        rows.append({
            "family": name, "variance": fam.variance,
            "tail_moment_order": fam.tail_moment_order,
            "E_z_psi": e_zpsi, "E_z_psi_error": abs(e_zpsi - 1.0),
            "E_psi": e_psi, "fisher_information": info,
            "stage_d_E_psi_prime": e_psi_prime[name],
            "fisher_vs_stage_d_abs_diff": abs(info - e_psi_prime[name]),
            "psi_vs_finite_difference_max_abs": fd_err,
            "psi_vs_P4_route_a_max_abs": score_diff,
            "logpdf_vs_P4_route_a_max_abs": lp_diff,
            "gamma_integrand_second_moment_finite": fam.tail_moment_order > 2,
            "gamma_integrand_third_moment_finite": fam.tail_moment_order > 3,
        })

    draw_rows = []
    for name in FAMILIES:
        from scipy import stats
        fam = F.get(name)
        a = fam.draw(np.random.Generator(np.random.Philox(11)), 400_000)
        b = ra.draw_innovations(name, np.random.Generator(np.random.Philox(11)),
                                400_000)
        ks = stats.ks_2samp(a, b)
        draw_rows.append({"family": name, "p8r_var": float(a.var()),
                          "p4_var": float(b.var()),
                          "ks_stat": float(ks.statistic),
                          "ks_p": float(ks.pvalue), "n": 400_000})

    payload = {
        "note": ("E[eps psi(eps)] = 1 and E[psi(eps)] = 0 are exact for every "
                 "regular location family; the Fisher information must "
                 "reproduce Stage-D's independently computed E[psi']."),
        "rows": rows,
        "draw_distribution_check": draw_rows,
        "stage_d_cusum_thresholds": stage_d_cusum_thresholds(),
        "statistics": {
            "S4_E_z_psi_max_error": max(r["E_z_psi_error"] for r in rows),
            "S4_E_psi_max_abs": max(abs(r["E_psi"]) for r in rows),
            "S4_fisher_max_abs_diff": max(r["fisher_vs_stage_d_abs_diff"]
                                          for r in rows),
            "S2b_psi_max_abs_diff": max(r["psi_vs_P4_route_a_max_abs"]
                                        for r in rows),
            "S2b_logpdf_max_abs_diff": max(r["logpdf_vs_P4_route_a_max_abs"]
                                           for r in rows)},
        "thresholds": {"S4_EZPSI_TOL": S4_EZPSI_TOL,
                       "S4_EPSI_TOL": S4_EPSI_TOL,
                       "S4_FISHER_TOL": S4_FISHER_TOL,
                       "S2_SCORE_TOL": S2_SCORE_TOL},
    }
    C.write(RESULTS / "family_regularity.json",
            C.envelope(generator="run_regularity.py",
                       schema="rebaseguard.p8r.family-regularity.v1",
                       tags=[], payload=payload))
    print(json.dumps(payload["statistics"], indent=1))


if __name__ == "__main__":
    main()
