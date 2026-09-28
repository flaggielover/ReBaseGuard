"""Cell-307 RLR campaign (r1) -- Stage 1: block-uniform RLR certification of the atom constants over one cover cell.

Frozen rules (protocol section 3; every rule is fixed before any target computation and none depends on a target):

  P1 partition   the cell's cover interval [x_lo, x_hi] is split into N = max(1, ceil((x_hi - x_lo) / (1/100)))
                 equal sub-blocks: C2's registry rule (`c2_refined_registry.sub_blocks`), adopted verbatim.
  P2 hull        each sub-block [lo, hi] is certified on its outward dyadic hull [floor(lo 2^20)/2^20,
                 ceil(hi 2^20)/2^20]. The pinned integer Taylor models require dyadic centre and radius
                 (`c1b_kernel._dy_exp`); a certificate on a superset of drifts is valid on the subset. The grid is the
                 certifier's own scaling grid 2^-20 (declaration D3).
  P3 rungs       on each hull block, the pinned `c1b_certpw.certify_degree` at every degree of the D8 ladder (4, 6, 8),
                 e-free strip-piecewise candidate family PW_d solved at the block midpoint (D12), with the pinned block
                 flags TIGHT_CT and BLOCK_LIGHT (D9, D11), D13 coverage (in the pinned code).
  P4 ladder      a rung counts only if its status is CERTIFIED. The block record is the ladder composition of the
                 pinned CLI (`c1b_certpw.run_point`): componentwise min over certified rungs of LADDER_KEYS_MIN, max of
                 LADDER_KEYS_MAX, then `c1b_certpw.assemble` (declaration D14 combined SUPPLY). A block with no
                 certified rung is NOT_CERTIFIED.
  P5 cell        if every block is certified, the cell constants are the componentwise MAX over blocks of
                 A1_SUPPLY and A2_SUPPLY (worst block; each block bound holds on its hull, the hulls cover the cell).
                 Otherwise the Stage-1 outcome is CERTIFICATION_FAILED; there is no retry with other settings.

The functions here compute and return exact records only. They never write a file and never print a value; the log
of the pinned certifier is captured in memory.
"""
from __future__ import annotations

import hashlib
import math
import time
from fractions import Fraction as F

SUB_BLOCK_MAX_WIDTH = F(1, 100)
HULL_BITS = 20
LADDER = (4, 6, 8)
EXACT_RECORD_KEYS = ("tau", "C_T", "C_R", "A_bar", "Lambda_lo", "tau_a_lo", "tau_a_up", "S2_up", "TN_up", "D_lo",
                     "D1", "D2", "L1_up", "L2_up", "eta_T", "eta_W", "c_global", "A0", "delta1", "delta2", "rho1",
                     "rho2", "A1_RLR", "A2_RLR", "A1_Dv", "A2_Dv", "G0", "G1", "G2", "A0_SUPPLY", "A1_SUPPLY",
                     "A2_SUPPLY")


def fs(x: F) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def partition(x_lo: F, x_hi: F) -> list:
    """P1 (C2 rule verbatim)."""
    n = max(1, math.ceil((x_hi - x_lo) / SUB_BLOCK_MAX_WIDTH))
    w = (x_hi - x_lo) / n
    return [(x_lo + i * w, x_lo + (i + 1) * w) for i in range(n)]


def hull(lo: F, hi: F, bits: int = HULL_BITS) -> tuple:
    """P2: outward dyadic hull on the 2^-bits grid."""
    s = 1 << bits
    return F(math.floor(lo * s), s), F(math.ceil(hi * s), s)


def blocks_for(x_lo: F, x_hi: F) -> list:
    out = []
    for i, (lo, hi) in enumerate(partition(F(x_lo), F(x_hi))):
        hlo, hhi = hull(lo, hi)
        out.append({"index": i, "sub_lo": lo, "sub_hi": hi, "hull_lo": hlo, "hull_hi": hhi})
    return out


def _exactify(v):
    if isinstance(v, F):
        return fs(v)
    if isinstance(v, dict):
        return {str(k): _exactify(x) for k, x in v.items() if not str(k).startswith("_")}
    if isinstance(v, (list, tuple)):
        return [_exactify(x) for x in v]
    return v


def certify_rung(mods: dict, hull_lo: F, hull_hi: F, d: int) -> dict:
    """P3: one pinned rung. Returns an exact, JSON-able record (every Fraction as 'p/q'); the in-memory log of the
    pinned certifier is returned with it. Exceptions propagate to the caller, which classifies them."""
    cp, pw = mods["c1b_certpw"], mods["c1b_pw"]
    lines: list = []
    e_c, e_r = (F(hull_lo) + F(hull_hi)) / 2, (F(hull_hi) - F(hull_lo)) / 2
    t0 = time.process_time()
    rec = cp.certify_degree(e_c, d, pw.BW_PW, log=lambda s: lines.append(str(s)), e_r=e_r)
    out = _exactify(rec)
    out["_cpu_seconds"] = round(time.process_time() - t0, 3)
    out["_log"] = lines
    return out


def ladder_compose(cp, rung_records: list) -> dict:
    """P4: the pinned CLI's ladder composition (c1b_certpw.run_point), on exact inputs."""
    cert = [r for r in rung_records if r.get("status") == "CERTIFIED"]
    if not cert:
        return {"status": "NOT_CERTIFIED", "certified_degrees": []}
    best = {k: min(F(r[k]) for r in cert) for k in cp.LADDER_KEYS_MIN}
    best.update({k: max(F(r[k]) for r in cert) for k in cp.LADDER_KEYS_MAX})
    best.update(cp.assemble(best))
    out = {k: (fs(v) if isinstance(v, F) else v) for k, v in best.items()}
    out["status"] = "CERTIFIED"
    out["certified_degrees"] = [r["degree"] for r in cert]
    return out


def cell_compose(block_records: list) -> dict:
    """P5: worst block (componentwise max of the SUPPLY upper bounds) over a cover of the cell."""
    if not block_records or any(b.get("status") != "CERTIFIED" for b in block_records):
        return {"status": "CERTIFICATION_FAILED",
                "failed_blocks": [i for i, b in enumerate(block_records) if b.get("status") != "CERTIFIED"]}
    return {"status": "CERTIFIED",
            "A0_SUPPLY_max": fs(max(F(b["A0_SUPPLY"]) for b in block_records)),
            "A1_SUPPLY_max": fs(max(F(b["A1_SUPPLY"]) for b in block_records)),
            "A2_SUPPLY_max": fs(max(F(b["A2_SUPPLY"]) for b in block_records)),
            "n_blocks": len(block_records)}


def log_digest(lines: list) -> str:
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()
