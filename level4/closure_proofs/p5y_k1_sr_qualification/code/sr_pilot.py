"""SR representative pilot runner -- PREPARED, DELIBERATELY NOT EXECUTED.

Entry point for the first real SR numerical qualification. It is NOT run in this
lane: the CUSUM Aux4 326-cell full-cover campaign owns all four physical cores
and SR heavy numerics are prohibited while it is active. `--force` is
deliberately absent; the CPU gate cannot be overridden from the command line.

Pilots address REAL frozen SR cells, chosen from `config/cells.json`, not
invented drifts -- an earlier probe used an artificial rho and drew the wrong
conclusion about large-drift cells (SR_RESOLVENT_GOVERNANCE.md section 3).

Usage once the CUSUM campaign has finished naturally:

    python code/sr_pilot.py --pilot central   --m all --bits 256
    python code/sr_pilot.py --pilot hardest   --m all --bits 256
    python code/sr_pilot.py --pilot splice    --m all --bits 256
    python code/sr_pilot.py --pilot easiest   --m 1   --bits 256
    python code/sr_pilot.py --all             --m all --bits 256

Add `--corroborate N` to also run the independent n-step resolvent certifier at
`n = N` and record whether it corroborates the frozen `C_upper`.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
CODE = NS / "code"
IMPL = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code"
SPECC = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor/code"
for _p in (str(CODE), str(IMPL), str(SPECC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flint import arb, ctx                                         # noqa: E402

import spec                                                        # noqa: E402
import sr_cost as CO                                               # noqa: E402
import sr_nstep as NST                                             # noqa: E402
import sr_propagate as P                                           # noqa: E402
import sr_provenance as PR                                         # noqa: E402

CUSUM_RUNNER = "qualify_batch.sh"

# Representative cells, selected from the frozen cover, with the reason recorded.
PILOT_CELLS = {
    "central":  (150, "central SR cell, moderate drift"),
    "hardest":  (0,   "smallest drift: largest frozen C_upper (1205.94)"),
    "easiest":  (313, "largest drift: smallest frozen C_upper (2.0005)"),
    "splice":   (315, "the compact/far-field splice cell"),
    "midrange": (275, "best measured utilisation in the Phase-7 sweep"),
}


class CusumCampaignActive(SystemExit):
    """The CPU resource gate refused to start SR numerics."""


def cusum_active() -> dict:
    out = subprocess.run(["ps", "-eo", "pgid,args"], capture_output=True,
                         text=True).stdout
    hits = [l for l in out.splitlines() if CUSUM_RUNNER in l and "ps -eo" not in l]
    return {"active": bool(hits), "n_procs": len(hits),
            "pgids": sorted({l.split()[0] for l in hits})}


def resource_gate() -> None:
    st = cusum_active()
    if st["active"]:
        raise CusumCampaignActive(
            f"REFUSED: the CUSUM full-cover campaign is still running "
            f"({st['n_procs']} processes, pgid {st['pgids']}). SR heavy numerics "
            f"are prohibited on this host while it holds the four physical cores. "
            f"Do not kill it to make room.")


def _arb(f) -> arb:
    f = F(f)
    return arb(f.numerator) / arb(f.denominator)


def sr_cell(index: int) -> dict:
    return next(c for c in spec.CELLS
                if c["detector"] == "SR" and int(c["index"]) == index)


def run(pilot: str, m_arg: str, bits: int, corroborate_n: int = 0) -> dict:
    resource_gate()                       # fail-closed BEFORE any numerical work
    ctx.prec = bits
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        os.environ[v] = "1"
    idx, why = PILOT_CELLS[pilot]
    cell = sr_cell(idx)
    lo, hi = F(cell["left"][0]), F(cell["right"][0])
    rho = abs(F(cell["rho"][0]))
    res = NST.ResolventCertificate.from_frozen_cell(cell)

    records: list = []
    corr = None
    if corroborate_n:
        with CO.measure(f"resolvent:{pilot}", records):
            ind = NST.certify(lo, hi, n=corroborate_n, partition=48, z_panels=48,
                              bits=bits)
        corr = res.corroborate(ind)
        corr["independent_certificate"] = ind.to_json()
    with CO.measure(f"cell:{pilot}", records):
        cert = P.cell_certificate(resolvent=res, e_lo=_arb(lo), e_hi=_arb(hi),
                                  rho=_arb(rho), cell_e=(lo, hi))

    ms = list(cert["per_m"]) if m_arg == "all" else [int(m_arg)]
    out = {
        "pilot": pilot, "why": why, "cell_index": idx, "bits": bits,
        "e0": cell["e0"], "rho": str(rho), "C_upper": str(F(cell["C_upper"])),
        "n": res.n, "q_n": res.q_n, "C_n": res.C_n,
        "resolvent_certificate": res.to_json(),
        "corroboration": corr,
        "runtime": records,
    }
    for m in ms:
        d = cert["per_m"][m]
        out[f"m={m}"] = {k: (v.str(20) if hasattr(v, "str") else str(v))
                         for k, v in d.items()}
    out["tcb_modules"] = len(PR.tcb_from_execution())
    out["runtime_binding"] = PR.runtime_binding()
    out["cost"] = CO.campaign_projection(records)
    dest = NS / f"diagnostics/pilots/sr_pilot_{pilot}_{bits}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", choices=sorted(PILOT_CELLS))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--m", default="all")
    ap.add_argument("--bits", type=int, default=256)
    ap.add_argument("--corroborate", type=int, default=0,
                    help="also run the independent n-step certifier at this n")
    ap.add_argument("--check-gate-only", action="store_true")
    a = ap.parse_args()
    if a.check_gate_only:
        print(json.dumps(cusum_active(), indent=1))
        sys.exit(0)
    targets = sorted(PILOT_CELLS) if a.all else [a.pilot]
    if not targets or targets == [None]:
        ap.error("give --pilot NAME or --all")
    for t in targets:
        print(json.dumps(run(t, a.m, a.bits, a.corroborate), indent=1, default=str))
