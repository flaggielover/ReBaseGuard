"""Theorem-based cover-compression audit: certify e_star from P5X-T3.

ALLOWED: a proved theorem makes a far-field region need no cellwise Fredholm
solve.  NOT ALLOWED: shortening the range because it is expensive.  This script
derives e_star from the far-field majorant of PROOF.md L3, it does not choose it.

    B_D(e) = phi(a) + sqrt( q' * m2 ),   a = c_D - |e| ,  q' = Phi(a) ,
    m2 = Phi(a) + |a| phi(a) + q'/(1-q') ,          valid for |e| >= c_D ,
and B_D is proved strictly decreasing on |e| >= c_D + 1 (L3.4).

So it suffices to bound B_D on the compact [c_D, c_D+1] by interval arithmetic.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from flint import arb

HERE = Path(__file__).resolve().parent
NS = HERE.parent
_PROOF_SRC = NS.parents[4] / "rebaseguard-proof" / "src"
if str(_PROOF_SRC) not in sys.path:
    sys.path.insert(0, str(_PROOF_SRC))
from rebaseguard_certify.arb_backend import (      # noqa: E402
    ball_record, gaussian_cdf, rational, workprec,
)

A_SR = "4581762885148045/8796093022208"            # exact runtime dyadic


def phi(x: arb) -> arb:
    return (-(x * x) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()


def majorant(a: arb) -> arb:
    q = gaussian_cdf(a)
    f = phi(a)
    m2 = q + a.abs_upper() * f + q / (arb(1) - q)
    return f + (q * m2).sqrt()


def certify(c_d: arb, *, panels: int = 4000, bits: int = 192) -> dict:
    """sup of B_D on |e| in [c_D, c_D+1], by a continuum interval cover."""
    with workprec(bits):
        worst = arb(0)
        worst_at = None
        for i in range(panels):
            lo = c_d + arb(i) / arb(panels)
            hi = c_d + arb(i + 1) / arb(panels)
            e_iv = (lo + hi) / arb(2) + arb(0, ((hi - lo) / arb(2)).upper())
            b = majorant(c_d - e_iv)
            if b.abs_upper() > worst.abs_upper():
                worst = arb(b.abs_upper())
                worst_at = float(((lo + hi) / arb(2)))
        tail = majorant(c_d - (c_d + arb(1)))       # value at c_D + 1
        return {"c_D": ball_record(c_d), "panels": panels,
                "sup_B_on_[c_D, c_D+1]": ball_record(worst),
                "argmax_approx": worst_at,
                "B_at_c_D_plus_1": ball_record(tail),
                "sup_below_2": bool(worst < arb(2)),
                "e_star": float(c_d.upper()),
                "continuum_cover": True, "sampled_grid_used": False}


def main() -> None:
    with workprec(192):
        c_cusum = rational(11, 2)
        a_sr = arb(A_SR.split("/")[0]) / arb(A_SR.split("/")[1])
        c_sr = a_sr.log() + rational(1, 2)
    out = {"schema": "rebaseguard.p5x.opt-r1.cover-compression.v1",
           "role": "THEOREM-BASED cover compression; derived, not chosen",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "basis": "P5X-T3 / PROOF.md L3 far-field majorant B_D",
           "applies_to": "the C1 first-moment cover only",
           "cusum": certify(c_cusum), "sr": certify(c_sr)}
    for d in ("cusum", "sr"):
        r = out[d]
        print(f"{d}: c_D={float(arb(r['c_D']['ball'])):.6f}  sup B on [c_D,c_D+1] = "
              f"{r['sup_B_on_[c_D, c_D+1]']['ball'][:24]}  <2? {r['sup_below_2']}  "
              f"B(c_D+1)={r['B_at_c_D_plus_1']['ball'][:16]}  e_star={r['e_star']:.6f}")
    (NS / "results" / "r1_cover_compression.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
