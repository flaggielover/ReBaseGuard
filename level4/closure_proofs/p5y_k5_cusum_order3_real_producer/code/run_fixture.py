"""Build a manufactured fixture, certify it with the engine, and check containment. NON-SCIENTIFIC."""
from __future__ import annotations

import resource
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import manufactured_chain as MC  # noqa: E402
import rung3_engine as E  # noqa: E402
import rung3_residual as RR  # noqa: E402
import soundness as SD  # noqa: E402


def certify_fixture(sysm: MC.ChainSystem, e0: Fr, rho: Fr, *, seed: int, noise: Fr, bits: int,
                    inflate: Fr = Fr(1), engine=E, residual=RR, rig: MC.Rigorous | None = None, perturb=None):
    rig = MC.Rigorous(sysm, e0, rho, seed=seed, noise=noise, perturb=perturb) if rig is None else rig
    t0 = time.process_time()
    with engine.precision(bits):
        cert = MC.ManufacturedCert(rig)
        g = {r: residual.g_residual(cert, r) for r in range(5)}
        inp = MC.engine_inputs(cert, g, inflate=inflate)
        res = engine.certify_order3(inp, bits=bits)
    cpu = time.process_time() - t0
    return rig, g, res, cpu


def summary(res: dict) -> dict:
    out = {}
    for m, v in sorted(res["m"].items()):
        L, U = v["R3_cell"]
        out[m] = {"L": L, "U": U, "width": U - L, "sign": E.sign_status(L, U)}
    return out


if __name__ == "__main__":
    sysm = MC.random_chain(int(sys.argv[1]) if len(sys.argv) > 1 else 101, 3, centre=Fr(1, 10))
    e0, rho = Fr(1, 10), Fr(1, 50)
    rig, g, res, cpu = certify_fixture(sysm, e0, rho, seed=5, noise=Fr(1, 10**6), bits=256)
    for m, s in summary(res).items():
        print(m, float(s["L"]), float(s["U"]), s["sign"], "truth", [float(x) for x in SD.truth_range(sysm, e0, rho, m)])
    print("violations", SD.violations(sysm, rig, res))
    print("g delta_mid", [float(g[r]["delta_mid"].mid()) for r in range(5)], "cpu", round(cpu, 2),
          "rss_mib", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
