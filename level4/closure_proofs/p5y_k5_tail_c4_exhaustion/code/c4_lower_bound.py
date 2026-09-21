"""Route L: a certified LOWER bound on E_a[tau] by a ladder/Wald minorant. Zero new-real, no kernel, no address.

THE THEOREM (call it L). Fix a K1 CUSUM cell and a drift e in it. With the frozen geometry K > 0, H > 0, the state
(s+, s-) in [0, H]^2 started at the atom a = (0, 0), innovations z_1, z_2, ... i.i.d. with density phi(. + e), the
frozen update s+ <- max(0, s+ + z - K), s- <- max(0, s- - z - K), and tau the first step at which the UNCLIPPED
update exceeds H in either coordinate:

    E_a[tau]  >=  H / E[(|z| - K)^+].

*Proof.* Write V_i := (|z_i| - K)^+ >= 0. Since s >= 0 always, max(0, s + z - K) <= s + (z - K)^+, so by induction
from s+_0 = s-_0 = 0,

    s+_t <= sum_{i<=t} (z_i - K)^+,      s-_t <= sum_{i<=t} (-z_i - K)^+.

K > 0 makes (z - K)^+ and (-z - K)^+ never simultaneously positive, so each is at most V_i and therefore
max(s+_t, s-_t) <= sum_{i<=t} V_i. At the alarm step the unclipped update exceeds H in one coordinate, and that
unclipped value is bounded by the same sum, so H < sum_{i<=tau} V_i. The V_i are i.i.d., non-negative and
integrable, and tau is a stopping time for the same filtration with E[tau] < infinity (Lemma T gives
E_x[tau] <= C_T < infinity), so Wald's identity applies: H <= E[sum_{i<=tau} V_i] = E[V] E[tau]. Divide. QED

WHY THIS IS THE RIGHT QUANTITY. Theorem AD's A0 is admissible only if |[(I - K_e)^-1 f](a)| <= A0 ||f|| uniformly
on the cell, and Lemma SM(d) says the supremum of that ratio over ||f|| <= 1 is exactly E_a[tau], attained at
f = 1. So every admissible A0 satisfies A0 >= sup_{e in cell} E_a[tau](e) >= E_a[tau](e*) for ANY single e* in the
cell. A pointwise lower bound at one drift therefore lower-bounds every admissible A0 on the whole cell.

WHICH POINT. dE[V]/de = Phi(e - K) - Phi(-(e + K)) >= 0, so E[V] increases in e and the bound H/E[V] decreases in
e: the left endpoint e_lo is the best point of the cell for this route. e_lo is an endpoint of the closed cell
[e0 - rho, e0 + rho], so it is admissible. The producer evaluates at e_lo and reports e0 alongside.

    python3 -B c4_lower_bound.py --out OUT.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c4_rigorous_gaussian as G                                                    # noqa: E402
from c4_common import CP, OPEN_CELLS, sha                                           # noqa: E402
from c4_model_identity import model                                                 # noqa: E402

C1_NS = CP / "p5y_k5_tail_operator_registry"
CELLS = CP / "p5y_k1_cover_ledger_successor/config/cells.json"


def cell_geometry() -> dict:
    """The exact rational cell endpoints, cross-checked against the C1 registry's own e_lo / e_hi."""
    cover = {c["index"]: c for c in json.loads(CELLS.read_bytes()) if c["detector"] == "CUSUM"}
    reg = {b["cell"]: b for b in json.loads((C1_NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes())["blocks"]}
    out = {}
    for k in OPEN_CELLS:
        c = cover[k]
        e0, rho = F(c["e0"][0]) + F(c["e0"][1]), F(c["rho"][0]) + F(c["rho"][1])
        lo, hi = e0 - rho, e0 + rho
        if F(reg[k]["e_lo"]) != lo or F(reg[k]["e_hi"]) != hi or F(reg[k]["e0"]) != e0:
            raise SystemExit(f"cell {k}: cover ledger and C1 registry disagree on the cell endpoints")
        out[k] = {"e0": e0, "rho": rho, "e_lo": lo, "e_hi": hi}
    return out


def bound_at(e: F, K: F, H: F) -> dict:
    """H / E[(|z| - K)^+] as a rigorous interval; the LOWER end is the certified lower bound on E_a[tau]."""
    EV = G.E_excess(e, K)
    B = G.Iv(H, H) / EV
    return {"e": e, "EV_lo": EV.lo, "EV_hi": EV.hi, "B_lo": B.lo, "B_hi": B.hi}


def monotone_check(K: F, H: F, lo: F, hi: F, steps: int = 24) -> dict:
    """E[V] increasing in e, exercised on a ladder across the tail range as well as argued from the derivative."""
    pts = [lo + (hi - lo) * F(i, steps) for i in range(steps + 1)]
    vals = [G.E_excess(p, K) for p in pts]
    return {"derivative": "dE[V]/de = Phi(e - K) - Phi(-(e + K)) >= 0",
            "ladder_points": len(pts),
            "EV_nondecreasing": all(vals[i].hi <= vals[i + 1].hi for i in range(len(vals) - 1)),
            "bound_nonincreasing": all((H / vals[i].lo) >= (H / vals[i + 1].lo) for i in range(len(vals) - 1))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    m = model()
    K, H = m["K"], m["H"]
    geo = cell_geometry()
    per = {}
    for k in OPEN_CELLS:
        g = geo[k]
        at_lo, at_e0 = bound_at(g["e_lo"], K, H), bound_at(g["e0"], K, H)
        per[str(k)] = {
            "e_lo": str(g["e_lo"]), "e0": str(g["e0"]), "e_hi": str(g["e_hi"]),
            "evaluated_at": "e_lo",
            "E_excess_at_e_lo": {"lo": str(at_lo["EV_lo"]), "hi": str(at_lo["EV_hi"]),
                                 "hi_float": float(at_lo["EV_hi"])},
            "lower_bound_E_a_tau": str(at_lo["B_lo"]),
            "lower_bound_E_a_tau_float": float(at_lo["B_lo"]),
            "lower_bound_at_e0_float": float(at_e0["B_lo"]),
            "interval_width_float": float(at_lo["B_hi"] - at_lo["B_lo"]),
        }

    out = {"schema": "rebaseguard.p5y.k5.tail-c4.lower-bound.v1",
           "route": "L: ladder/Wald minorant, E_a[tau] >= H / E[(|z| - K)^+]",
           "model": {**{kk: (str(v) if isinstance(v, F) else v) for kk, v in m.items()}},
           "arithmetic": {"library": "fractions.Fraction only", "outward_rounding_grid": f"2^-{G.SCALE}",
                          "exp_terms": G.EXP_TERMS, "erf_terms": G.ERF_TERMS, "atan_terms": G.ATAN_TERMS,
                          "sqrt_2pi": [str(G.sqrt_two_pi().lo), str(G.sqrt_two_pi().hi)]},
           "monotonicity": monotone_check(K, H, min(g["e_lo"] for g in geo.values()),
                                          max(g["e_hi"] for g in geo.values())),
           "cells": per,
           "inputs_sha256": {"cells.json": sha(CELLS), "cusum_layer1.py": m["source_sha256"],
                             "REGISTRY_C1.json": sha(C1_NS / "evidence/registry_c1/REGISTRY_C1.json")},
           "new_real_scientific_addresses_evaluated": 0,
           "kernel_evaluations": 0, "operator_certifications_run": 0,
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(f"model: K={K} H={H}  monotone={out['monotonicity']}")
    for k, v in per.items():
        print(f"cell {k}: e_lo={float(F(v['e_lo'])):.6f}  E[V]<={v['E_excess_at_e_lo']['hi_float']:.9f}  "
              f"E_a[tau] >= {v['lower_bound_E_a_tau_float']:.9f}  (at e0: {v['lower_bound_at_e0_float']:.9f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
