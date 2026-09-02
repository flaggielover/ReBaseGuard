"""R-A' pre-gate diagnostics: radius scaling and far-field truncation.

Reported, never used to choose a parameter -- RA_FROZEN_SPEC section 13 freezes
a single admissible configuration and authorises no retry ladder.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(HERE))

from flint import arb                                          # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402
import ra_certifier as RA                                      # noqa: E402


def far_field_truncation() -> list[dict]:
    """Device 1 is e-free, so this must be flat in e -- against 7.04e44 before."""
    rows = []
    with workprec(RA.BITS):
        eps_z = RA.taylor_remainder(RA.TAYLOR_N, rational(11, 2))
        eps_r = RA.taylor_remainder(RA.TAYLOR_N, rational(5, 2))
        for e in (0, 0.26, 6.5, 12.0):
            e_arb = arb(rational(round(e * 10 ** 6), 10 ** 6))
            allow = (arb(11) * arb(3) * eps_z
                     + (arb(2) + arb(2) * e_arb * (rational(11, 2) + e_arb))
                     * eps_r * (arb(1) + rational(5, 2)))
            rows.append({
                "e": e,
                "ra_kernel_truncation": ball_record(eps_z),
                "ra_reward_truncation": ball_record(eps_r),
                "ra_total_allowance_at_sup_g_3": ball_record(allow),
                "failed_method_maclaurin_order50": {
                    0: "3.75603e-7", 0.26: "4.17665e-5",
                    6.5: "1.36e+28", 12.0: "7.04071e+44"}[e],
            })
    return rows


def radius_scan() -> list[dict]:
    """Does recentring alone change the interval-dependency constant?

    R-A' never feeds an interval e to the symbolic chain, so this measures a
    quantity R-A' does not rely on.  It is recorded to show what recentring did
    and did not fix.
    """
    rows = []
    for num, den in ((0, 1), (1, 10 ** 8), (1, 10 ** 6)):
        t = time.time()
        with workprec(RA.BITS):
            e = arb(rational(1, 4), rational(num, den))
        rec = RA._interval_probe(e)
        rows.append({"e_ball_radius": num / den,
                     "polynomial_residual": ball_record(rec),
                     "wall_seconds": time.time() - t})
        print(json.dumps(rows[-1], indent=1), flush=True)
    return rows


def main() -> None:
    out = {
        "schema": "rebaseguard.p5x.ra.diagnostics.v1",
        "role": "PRE-GATE DIAGNOSTIC; not a certificate, not a parameter selector",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip(),
        "taylor_order": RA.TAYLOR_N,
        "far_field_truncation": far_field_truncation(),
        "radius_scan": radius_scan(),
    }
    (NS / "results" / "ra_diagnostics.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out["far_field_truncation"], indent=1))


if __name__ == "__main__":
    main()
