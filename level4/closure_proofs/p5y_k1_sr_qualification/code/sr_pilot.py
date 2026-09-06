"""SR representative pilot runner -- PREPARED, DELIBERATELY NOT EXECUTED.

This script is the entry point for the first real SR numerical qualification. It
is NOT run in this lane: the CUSUM Aux4 326-cell full-cover campaign owns all
four physical cores, and SR_HEAVY_NUMERICS_ON_THIS_HOST is prohibited while it
is active. `--force` is deliberately absent; the CPU gate cannot be overridden
from the command line.

Usage once the CUSUM campaign has finished naturally:

    python code/sr_pilot.py --pilot central   --m all --bits 256
    python code/sr_pilot.py --pilot drift     --m all --bits 256
    python code/sr_pilot.py --pilot splice    --m all --bits 256
    python code/sr_pilot.py --pilot difficult --m all --bits 256

Each pilot emits R/D/R2 intervals, M_R2, B_cover utilisation, provenance, CPU
seconds and peak RSS into diagnostics/pilots/.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CODE = NS / "code"
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

from flint import arb, ctx                                         # noqa: E402

import sr_cost as CO                                               # noqa: E402
import sr_propagate as P                                           # noqa: E402
import sr_provenance as PR                                         # noqa: E402

CUSUM_RUNNER = "qualify_batch.sh"

PILOTS = {
    "central":   {"e_lo": (1, 4),  "e_hi": (3, 10), "why": "central SR cell, moderate drift"},
    "drift":     {"e_lo": (1, 1),  "e_hi": (11, 10), "why": "large drift, kernel mass shifted"},
    "splice":    {"e_lo": (1, 100), "e_hi": (1, 50), "why": "near the compact/far-field splice"},
    "difficult": {"e_lo": (1, 1000), "e_hi": (1, 500), "why": "small drift, worst resolvent conditioning"},
}


class CusumCampaignActive(SystemExit):
    """The CPU resource gate refused to start SR numerics."""


def cusum_active() -> dict:
    """Phase-10 CPU gate: is the CUSUM full-cover campaign still running?"""
    out = subprocess.run(["ps", "-eo", "pgid,args"], capture_output=True, text=True).stdout
    hits = [l for l in out.splitlines() if CUSUM_RUNNER in l]
    pgids = sorted({l.split()[0] for l in hits})
    return {"active": bool(hits), "n_procs": len(hits), "pgids": pgids}


def resource_gate() -> None:
    st = cusum_active()
    if st["active"]:
        raise CusumCampaignActive(
            f"REFUSED: the CUSUM full-cover campaign is still running "
            f"({st['n_procs']} processes, pgid {st['pgids']}). SR heavy numerics "
            f"are prohibited on this host while it holds the four physical cores. "
            f"Do not kill it to make room.")


def run(pilot: str, m_arg: str, bits: int, C: str) -> dict:
    resource_gate()                       # fail-closed BEFORE any numerical work
    ctx.prec = bits
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        os.environ[v] = "1"
    cfg = PILOTS[pilot]
    e_lo = arb(cfg["e_lo"][0]) / arb(cfg["e_lo"][1])
    e_hi = arb(cfg["e_hi"][0]) / arb(cfg["e_hi"][1])
    rho = (e_hi - e_lo) / arb(2)
    Cb = arb(C)
    records: list = []
    with CO.measure(f"cell:{pilot}", records):
        cert = P.cell_certificate(C=Cb, e_lo=e_lo, e_hi=e_hi, rho=rho)
    ms = list(cert["per_m"]) if m_arg == "all" else [int(m_arg)]
    out = {"pilot": pilot, "why": cfg["why"], "bits": bits, "runtime": records}
    for m in ms:
        d = cert["per_m"][m]
        out[f"m={m}"] = {k: (v.str(20) if hasattr(v, "str") else str(v))
                         for k, v in d.items()}
    tcb = PR.tcb_from_execution()
    out["tcb_modules"] = len(tcb)
    out["runtime_binding"] = PR.runtime_binding()
    out["cost"] = CO.campaign_projection(records)
    dest = NS / f"diagnostics/pilots/sr_pilot_{pilot}_{bits}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", choices=sorted(PILOTS), required=True)
    ap.add_argument("--m", default="all")
    ap.add_argument("--bits", type=int, default=256)
    ap.add_argument("--C", default="600", help="certified n-step resolvent bound")
    ap.add_argument("--check-gate-only", action="store_true")
    a = ap.parse_args()
    if a.check_gate_only:
        print(json.dumps(cusum_active(), indent=1))
        sys.exit(0)
    print(json.dumps(run(a.pilot, a.m, a.bits, a.C), indent=1, default=str))
