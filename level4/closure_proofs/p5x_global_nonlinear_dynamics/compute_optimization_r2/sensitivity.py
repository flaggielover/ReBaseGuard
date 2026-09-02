"""R2 step 2 - PRE-RESULT sensitivity of the certified residual to Taylor order
N and Bernstein subdivision depth.  Feasibility measurement only: the selection
RULE is frozen in the spec and evaluated at run time; no value is picked here.
"""
from __future__ import annotations

import json
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
sys.path.insert(0, str(NS / "certified_method_repair_ra"))

from flint import arb                                                    # noqa: E402
from rebaseguard_certify.arb_backend import ball_record, rational, workprec  # noqa: E402
from rebaseguard_certify.polynomial import bi_add, bi_scale, chebyshev_payload_to_power  # noqa: E402
from rebaseguard_certify.residual import _kernel_polynomials, _max_abs_on_reachable  # noqa: E402
import ra_certifier as RA                                                # noqa: E402

C_OPT = arb("220.7075187096823143058125152854812294891688046029854141728")
E_HI = arb(rational(26, 100))
ORDERS = (30, 40, 50, 60, 80, 120)
DEPTHS = (0, 1, 2, 3)


def main() -> None:
    e = rational(1, 4)
    cand_g, cand_dg = RA.solve_candidates(0.25)
    pay_g = cand_g.to_chebyshev_dyadic(scale_bits=RA.SCALE_BITS)
    rows = []
    with workprec(RA.BITS):
        g_hat = chebyshev_payload_to_power(pay_g)
        sup_g = arb(str(sum(abs(int(n)) for row in pay_g["numerators"] for n in row))) / (arb(2) ** 50)
        for N in ORDERS:
            t0 = time.process_time()
            b = RA.phi_taylor_coefficients(N, e)
            kl, kh = _kernel_polynomials(g_hat, b, z_weight=0)
            rw = RA.reward_rho1(N, e)
            kernel_cpu = time.process_time() - t0
            rl = bi_add(bi_add(g_hat, bi_scale(kl, -arb(1))), bi_scale(rw, -arb(1)))
            rh = bi_add(bi_add(g_hat, bi_scale(kh, -arb(1))), bi_scale(rw, -arb(1)))
            deg = max(i + j for (i, j) in list(rl) + list(rh))
            eps_z = RA.taylor_remainder(N, rational(11, 2))
            eps_r = RA.taylor_remainder(N, rational(5, 2))
            allow = (arb(11) * sup_g * eps_z
                     + (arb(2) + arb(2) * E_HI * (rational(11, 2) + E_HI))
                     * eps_r * (arb(1) + rational(5, 2)))
            for d in DEPTHS:
                t = time.process_time()
                mx, cov = _max_abs_on_reachable(rl, rh, subdivision_depth=d)
                bern_cpu = time.process_time() - t
                delta = mx + allow
                cdelta = C_OPT * delta
                rows.append({
                    "N": N, "depth": d, "residual_degree": deg,
                    "truncation_allowance": ball_record(allow),
                    "truncation_allowance_float": float(allow.upper()),
                    "bernstein_residual": ball_record(mx),
                    "bernstein_residual_float": float(mx.upper()),
                    "delta_float": float(delta.upper()),
                    "C_delta_float": float(cdelta.upper()),
                    "kernel_cpu_s": kernel_cpu, "bernstein_cpu_s": bern_cpu,
                    "total_cpu_s": kernel_cpu + bern_cpu,
                    "bernstein_patches": cov["bernstein_patches"],
                    "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20,
                })
                print(f"N={N:3d} d={d}  deg={deg:3d}  trunc={float(allow.upper()):9.2e}  "
                      f"resid={float(mx.upper()):9.3e}  C*delta={float(cdelta.upper()):9.3e}  "
                      f"kern={kernel_cpu:6.2f}s  bern={bern_cpu:7.2f}s", flush=True)
    out = {"schema": "rebaseguard.p5x.opt-r2.sensitivity.v1",
           "role": "PRE-RESULT feasibility table; no value is selected here",
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                        capture_output=True, text=True).stdout.strip(),
           "cell": "CUSUM m=1 e=1/4", "C_used": ball_record(C_OPT),
           "r1_reference": {"N": 120, "depth": 3, "delta": 1.0257899457283196e-05,
                            "C_delta": 0.012712330410017238},
           "rows": rows}
    (NS / "results" / "r2_sensitivity.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
