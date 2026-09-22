"""C11R Phase 6 -- the mandatory cheap refutation screen.

C11 spent its campaign blaming its own box bound for a candidate family that fails pointwise, and
published a false blocker as the successor's instruction. This module makes that impossible here:
no candidate may reach an expensive certification run until it has survived a rigorous pointwise
necessary condition, and a refuted candidate is sealed as refuted rather than retried with more
compute.

At a single state the kernel is evaluated exactly -- no box bound, no subdivision -- so

    L(x) = w(x) - 1 - (K w)(x)

is enclosed rigorously and uniformly over the drift block. If L(x).hi < 0 for any reachable x then
no supersolution certificate for that w exists at ANY subdivision depth, over that block, for that
kernel. The screen costs a fraction of a certification run.

It also records the ORIENTING threshold: a CONSTANT w certifies iff w >= 1 / min h, where h is the
one-step escape probability for the kernel in question. Nothing below that threshold can work, so
it bounds the whole constant family before a single expensive run.
"""
from __future__ import annotations

import pathlib
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_idrift as I

sys.path.insert(0, str(C.C7 / "code"))
import c7_gaussian as G              # noqa: E402


def grid(n: int = 15) -> list[tuple[F, F]]:
    ax = [F(5 * i, n - 1) for i in range(n)]
    return [(p, m) for p in ax for m in ax if (p + m <= 4) or p == 0 or m == 0]


def constant_threshold(E: I.Blk, atom_removed: bool, n: int = 15) -> dict:
    """1 / min over R and over the whole block of the one-step escape probability.

    For K_e that is h_1 = 1 - K_e 1. For Khat_e it is 1 - Khat_e 1, which is LARGER because the
    atom piece has been removed, so the atom-removed constant family is strictly easier.
    """
    one = {(0, 0): F(1)}
    worst, arg = None, None
    for p, m in grid(n):
        # 1 - Khat_e 1 = (1 - K_e 1) + atom mass = h_1 + atom. Computing it that way keeps the
        # two tight single-moment enclosures instead of subtracting a piecewise sum from 1: over
        # the whole block the piecewise form's lower end can fall below zero at the atom, where
        # h_1 is only 7.3e-05 and the block widening is far larger than that. The identity is the
        # same; the enclosure is not.
        h = I.alarm_prob_iv(p, m, E)
        if atom_removed:
            h = h + I.atom_contribution_iv(one, p, m, E)
        if worst is None or h.lo < worst:
            worst, arg = h.lo, (str(p), str(m))
    return {"kernel": "Khat_e" if atom_removed else "K_e",
            "min_escape_probability_lower_bound": float(worst),
            "min_escape_exact": str(worst),
            "at_state": arg,
            "constant_family_threshold": (float(1 / worst) if worst > 0 else None),
            "threshold_unavailable_reason": (
                None if worst > 0 else
                "the block-uniform lower bound on the escape probability is not positive at the "
                "binding state, so no constant supersolution can be certified over the whole "
                "block by this route")}


def screen(w: dict, E: I.Blk, *, atom_removed: bool = False, n: int = 15) -> dict:
    t = time.time()
    worst, arg = None, None
    for p, m in grid(n):
        L = (I.kernel_apply_iv.__globals__["X"].poly_eval_iv(w, G.Iv(p, p), G.Iv(m, m))
             - G.Iv(1, 1) - I.kernel_apply_iv(w, p, m, E, atom_removed=atom_removed))
        if worst is None or L.hi < worst:
            worst, arg = L.hi, (str(p), str(m))
    refuted = worst < 0
    return {"kernel": "Khat_e" if atom_removed else "K_e",
            "grid": f"{n}x{n} on R", "states": len(grid(n)),
            "min_L_upper_bound": float(worst),
            "min_L_exact": str(worst),
            "binding_state": arg,
            "classification": "POINTWISE_REFUTED" if refuted else "ELIGIBLE_FOR_CERTIFICATION",
            "reason": ("a rigorous enclosure proves L < 0 at a reachable state, uniformly over the "
                       "drift block, so no certificate exists at any depth"
                       if refuted else
                       "the necessary condition holds at every screened state; this is ELIGIBILITY, "
                       "not certification"),
            "seconds": round(time.time() - t, 1)}


def main() -> int:
    t0 = time.time()
    tbl = C.load(C.NS / "evidence" / "table" / "C11R_N9_TABLE.json")
    e_lo, e_hi = F(tbl["drift_domain"]["e_lo"]), F(tbl["drift_domain"]["e_hi"])
    BLOCK = I.Blk(e_lo, e_hi)

    print(f"drift block = [{float(e_lo):.7f}, {float(e_hi):.7f}]  width {float(e_hi - e_lo):.7f}")
    print("\n=== orienting thresholds for the CONSTANT family ===", flush=True)
    th = {}
    for ar in (False, True):
        r = constant_threshold(BLOCK, ar)
        th[r["kernel"]] = r
        th_s = ("%.1f" % r["constant_family_threshold"]) if r["constant_family_threshold"] \
            else "UNAVAILABLE"
        print(f"  {r['kernel']:8s} min escape = {r['min_escape_probability_lower_bound']:.6e} "
              f"at {r['at_state']}   threshold = {th_s}", flush=True)

    # the original's own values, for orientation only -- NOT loaded as comparison here
    orig = {k: tbl["constants"][k]["value_float"] for k in ("Abar", "tau", "C_T")}
    print(f"\n  (orientation only) original Abar {orig['Abar']:.4f}, tau {orig['tau']:.4f}, "
          f"C_T {orig['C_T']:.4f}", flush=True)

    print("\n=== candidate screen ===", flush=True)
    cands = []
    for A, B in ((F(12), F(3, 2)), (F(20), F(3, 2)), (F(40), F(3)), (F(100), F(6))):
        cands.append((f"K_e  w={A}-{B}m", {(0, 0): A, (0, 1): -B}, False))
    for A, B in ((F(8), F(1)), (F(12), F(3, 2)), (F(20), F(3, 2))):
        cands.append((f"Khat w={A}-{B}m", {(0, 0): A, (0, 1): -B}, True))
    rows = {}
    for name, w, ar in cands:
        r = screen(w, BLOCK, atom_removed=ar)
        rows[name] = {"w": {f"{i},{j}": str(c) for (i, j), c in sorted(w.items())}, **r}
        print(f"  {name:22s} min_L <= {r['min_L_upper_bound']:+12.4f} at {r['binding_state']}"
              f"  {r['classification']}  ({r['seconds']}s)", flush=True)

    out = {"schema": "C11R_SCREEN/1",
           "policy": ("mandatory before any expensive certification run; a POINTWISE_REFUTED "
                      "candidate must be sealed as refuted and MUST NOT be sent to certification"),
           "drift_block": {"e_lo": str(e_lo), "e_hi": str(e_hi),
                           "float": [float(e_lo), float(e_hi)],
                           "uniformity": ("carried as an interval through every step; not a grid, "
                                          "not endpoints, not a midpoint")},
           "constant_family_thresholds": th,
           "candidates": rows,
           "eligible": [k for k, v in rows.items()
                        if v["classification"] == "ELIGIBLE_FOR_CERTIFICATION"],
           "refuted": [k for k, v in rows.items() if v["classification"] == "POINTWISE_REFUTED"],
           "seconds": round(time.time() - t0, 1)}
    s = C.write_evidence(C.NS / "evidence" / "screen" / "C11R_SCREEN.json", out)
    print(f"\nwrote evidence/screen/C11R_SCREEN.json sha256 {s[:16]}...  ({out['seconds']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
