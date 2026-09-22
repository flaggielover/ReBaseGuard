"""C11R Phase 14 -- target execution, sealed before any comparison.

This module NEVER reads REGISTRY_C2. It produces the independent certificates and writes them with
their own hash; only c11r_compare.py, run afterwards and from a later commit, loads the original's
values. That ordering is the seal-before-compare discipline C11 recorded as structurally
unavailable when its own module layout shows it was simply not arranged.

It also enforces the screen: a candidate the Phase 6 screen classified POINTWISE_REFUTED is not
sent to a certification run, and a candidate absent from the screen is not run at all. Spending an
expensive run on a refuted candidate is mutant M28; running an unscreened one is how C11 spent its
budget.

Target mapping -- which certificate produces which of the six constants:

    Abar   <- the K_e supersolution, evaluated at the atom
    tau    <- the Khat_e supersolution, evaluated at the atom
    C_T    <- the SAME Khat_e supersolution, as sup over the reachable set
    D_lo   } these three are NOT produced by a supersolution certificate at all. They come from
    D1     } the original's certify_cell, which solves d = Khat_e d + h_1 and its first two drift
    D2     } derivatives, and they are CONDITIONAL on C_T and tau.
"""
from __future__ import annotations

import pathlib
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_idrift as I

# name in the screen artifact -> (weight, atom_removed, depth, panels)
# The Khat_e candidate is w = 8 - m rather than 12 - 3/2 m: the screen shows it eligible, and it
# produces BOTH atom-removed constants at once -- tau as w(atom) and C_T as sup over R -- so a
# tighter constant improves two targets from one certification run.
CANDIDATES = {
    "K_e  w=12-3/2m": ({(0, 0): F(12), (0, 1): F(-3, 2)}, False, 4, 16),
    "Khat w=8-1m": ({(0, 0): F(8), (0, 1): F(-1)}, True, 4, 16),
}


def main() -> int:
    t0 = time.time()
    tbl = C.load(C.NS / "evidence" / "table" / "C11R_N9_TABLE.json")
    gate = C.load(C.NS / "config" / "N9R_GATE_C11R.json")
    screen = C.load(C.NS / "evidence" / "screen" / "C11R_SCREEN.json")

    e_lo, e_hi = F(tbl["drift_domain"]["e_lo"]), F(tbl["drift_domain"]["e_hi"])
    BLOCK = I.Blk(e_lo, e_hi)
    if [str(e_lo), str(e_hi)] != gate["target"]["drift_domain"]:
        raise SystemExit("REFUSE: the drift block does not match the frozen gate")

    eligible = set(screen["eligible"])
    refuted = set(screen["refuted"])

    runs = {}
    for name, (w, ar, depth, panels) in CANDIDATES.items():
        if name in refuted:
            raise SystemExit(f"REFUSE: {name!r} is POINTWISE_REFUTED; a certification run must "
                             f"not be spent on it (gate predicate G10)")
        if name not in eligible:
            raise SystemExit(f"REFUSE: {name!r} was not screened; no candidate may reach a "
                             f"certification run unscreened (gate predicate G10)")
        t = time.time()
        r = I.supersolution_margin_iv(w, BLOCK, depth=depth, panels=panels, atom_removed=ar)
        sec = round(time.time() - t, 1)
        w_atom = I.X.poly_eval_iv(w, I.G.Iv(0, 0), I.G.Iv(0, 0))
        sup_w = max(I.X.poly_eval_iv(w, I.G.Iv(a, b), I.G.Iv(c, d)).hi
                    for (a, b, c, d) in I.X.cover(depth))
        runs[name] = {
            "w": {f"{i},{j}": str(c) for (i, j), c in sorted(w.items())},
            "kernel": r["kernel"], "depth": depth, "panels": panels, "boxes": r["boxes"],
            "margin_lower_bound": float(r["margin_lower_bound"]),
            "margin_exact": str(r["margin_lower_bound"]),
            "w_min_lower_bound": float(r["w_min_lower_bound"]),
            "certified": r["certified"],
            "w_at_atom": str(w_atom.hi), "w_at_atom_float": float(w_atom.hi),
            "sup_over_R": str(sup_w), "sup_over_R_float": float(sup_w),
            "seconds": sec,
            "screen_classification": screen["candidates"][name]["classification"],
            "statement": (
                f"for every e in [{e_lo}, {e_hi}]: w >= 1 + "
                f"{'Khat_e' if ar else 'K_e'} w on the reachable set R"
                + (", hence ||Ghat_e|| <= sup_R w and (Ghat_e 1)(atom) <= w(atom)" if ar else
                   ", hence E_x[tau] <= w(x) and w(atom) bounds the ARL at the atom")),
        }
        print(f"  {name:18s} d={depth} pan={panels} boxes={r['boxes']:4d} "
              f"margin={float(r['margin_lower_bound']):+.5f} cert={r['certified']} ({sec}s)",
              flush=True)

    ke = runs.get("K_e  w=12-3/2m", {})
    khat = runs.get("Khat w=8-1m", {})
    targets = {
        "Abar": ({"from": "K_e  w=12-3/2m", "quantity": "w_at_atom",
                  "value": ke.get("w_at_atom"), "certified": ke.get("certified")}
                 if ke.get("certified") else
                 {"from": "K_e  w=12-3/2m", "quantity": "w_at_atom", "value": None,
                  "certified": False, "reason": "the K_e candidate did not certify"}),
        "tau": ({"from": "Khat w=8-1m", "quantity": "w_at_atom",
                 "value": khat.get("w_at_atom"), "certified": khat.get("certified")}
                if khat.get("certified") else
                {"from": "Khat w=8-1m", "quantity": "w_at_atom", "value": None,
                 "certified": False, "reason": "the Khat_e candidate did not certify"}),
        "C_T": ({"from": "Khat w=8-1m", "quantity": "sup_over_R",
                 "value": khat.get("sup_over_R"), "certified": khat.get("certified")}
                if khat.get("certified") else
                {"from": "Khat w=8-1m", "quantity": "sup_over_R", "value": None,
                 "certified": False, "reason": "the Khat_e candidate did not certify"}),
    }
    for k in ("D_lo", "D1", "D2"):
        targets[k] = {
            "from": None, "quantity": None, "value": None, "certified": False,
            "reason": "NO_INDEPENDENT_STATEMENT",
            "what_would_be_required": [
                "a candidate d solving d = Khat_e d + h_1, and its first two drift derivatives",
                "the drift derivatives of the kernel, Khat' and Khat'', with Hermite-weighted "
                "densities phi^(i)(z+e) = (-1)^i He_i(z+e) phi(z+e)",
                "closed forms for h_1' and h_1'' (elementary: h_1' = phi(ell+e) - phi(up+e))",
                "operator norm bounds kernel_norm(0..3) over the block",
                "a residual-to-error propagation argument consuming THIS campaign's own C_T and "
                "tau, never the original's -- the cell certificate is conditional on them"],
        }

    out = {"schema": "C11R_RUNS/1",
           "SEALED_BEFORE_COMPARISON": True,
           "contains_no_original_value": True,
           "gate_sha256": gate["sha256"],
           "screen_sha256": screen["sha256"],
           "drift_block": {"e_lo": str(e_lo), "e_hi": str(e_hi),
                           "float": [float(e_lo), float(e_hi)],
                           "uniformity": "carried as an interval; not a grid, midpoint or endpoints"},
           "candidates": runs,
           "targets": targets,
           "seconds": round(time.time() - t0, 1)}
    s = C.write_evidence(C.NS / "evidence" / "runs" / "C11R_RUNS.json", out)
    print(f"\ntargets with an independent certified value: "
          f"{sorted(k for k, v in targets.items() if v.get('value'))}")
    print(f"targets with no independent statement: "
          f"{sorted(k for k, v in targets.items() if v.get('reason') == 'NO_INDEPENDENT_STATEMENT')}")
    print(f"wrote evidence/runs/C11R_RUNS.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
