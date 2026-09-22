"""C9 -- the E1 lever the first pass MISSED, quantified from committed evidence.

The first pass declared "blocker 1": that re-running the committed E1 producer reproduces the
committed block, so E1 cannot close cell 307. The fresh-context review returned STOP_PREMATURE and
was right. Two errors produced that false blocker:

  (a) C9 redefined E1 as "one authorized execution of the COMMITTED producer". C6 defines it as
      "a BETTER operator tuple", existence OBJECT_ONLY_HYPOTHESIZED, "there is nothing to replay",
      "a TOOLCHAIN for the WORK ... the result does not exist"; C8's gate defines R3 as "a BETTER
      certified upper bound". Under the real definition, changing the certifier's SEARCH is the work,
      not a deviation from it. C9's own B0_15 quoted the C6 entry it then contradicted.
  (b) The dependency scan read only the WRAPPER's CLI. `taboo_certify.py` exposes --alpha, --beta,
      --depth and --degree as first-class arguments, so the search parameters are not hardcoded at
      the certifier at all.

THE LEVER. The taboo supersolution candidate is w = dyadic(alpha * g) and the block certification is
affine in w. The wrapper walks the ladder (6/5, 13/10, 7/5, 3/2, 2, 3) in ASCENDING order and takes
the FIRST rung that certifies. Cell 307 certified at the very first rung, 6/5, on all ten sub-blocks,
each with a recorded margin_lower_bound of about 0.16 STILL IN HAND. The ladder has no rung below
6/5, so a smaller alpha was never tried.

Scaling w by c scales the certified surplus by c, so a block still certifies whenever

    c >= 1 / (1 + margin_lower_bound),

and tau, being the supersolution value, scales with c as well. Since eff = tau / D_lo and A1, A2 are
proportional to eff, a smaller alpha tightens the whole supply at the SAME geometry, SAME degree and
essentially the SAME cost.

STATUS. Everything below is a COUNTERFACTUAL PROJECTION resting on the affine scaling argument and
on the recorded margins. It is NOT certified. `dyadic` rounding makes the scaling approximate, so the
projection must be confirmed by actually running the certifier at the chosen alpha. That is exactly
the one governed execution C9 was chartered to perform and could not authorize.
"""
from __future__ import annotations

import glob
import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c9_common as C
import c9_chain as X

K1 = F(7978846, 10 ** 7)
K2 = F(9678830, 10 ** 7)
CELL = 307
REQUIRED_CLOSURE = F(10960072461461898, 10 ** 16)
REQUIRED_ADOPTION = F(13700090576827373, 10 ** 16)


def main() -> int:
    ch = X.Chain()
    R = C.C2 / "evidence" / "registry_c2"
    blocks = []
    for f in sorted(glob.glob(str(R / f"taboo_block_{CELL}_*.json"))):
        d = json.loads(pathlib.Path(f).read_bytes())
        blocks.append({"file": pathlib.Path(f).name,
                       "alpha": F(d["proposal"]["alpha"]),
                       "margin_lower_bound": F(d["margin_lower_bound"]),
                       "tau": F(d["tau"]), "certified": d["certified"],
                       "depth": d["depth"], "bits": d["bits"]})
    if not blocks or not all(b["certified"] for b in blocks):
        raise SystemExit("cell 307 taboo sub-blocks are not all certified")
    alpha_old = blocks[0]["alpha"]
    if any(b["alpha"] != alpha_old for b in blocks):
        raise SystemExit("sub-blocks did not share a single alpha rung")
    c_min = max(1 / (1 + b["margin_lower_bound"]) for b in blocks)
    alpha_min = c_min * alpha_old
    tau_old = max(b["tau"] for b in blocks)

    best = ch.operator_best({"C1": ch.blocks1[CELL], "C2": ch.blocks2[CELL]})
    cur = ch.atom_constants(best["Abar"], best["tau"], best["C_T"], best["D_lo"],
                            best["D1"], best["D2"], K1, K2)

    def project(alpha_new):
        c = F(alpha_new) / alpha_old
        if c < c_min:
            return None
        tau_new = c * tau_old
        b2 = dict(best)
        b2["tau"] = min(b2["tau"], tau_new)
        nw = ch.atom_constants(b2["Abar"], b2["tau"], b2["C_T"], b2["D_lo"],
                               b2["D1"], b2["D2"], K1, K2)
        tight = cur["eff"] / nw["eff"]
        return {"alpha": str(F(alpha_new)), "alpha_float": float(F(alpha_new)),
                "scale_c": float(c), "tau_projected": float(tau_new),
                "eff_projected": float(nw["eff"]), "tightening": float(tight),
                "meets_closure": bool(tight >= REQUIRED_CLOSURE),
                "meets_adoption": bool(tight >= REQUIRED_ADOPTION),
                "Gamma_negative_projected": bool(ch.passes_C5T(CELL, nw))}

    ladder = [F(21, 20), F(53, 50), F(107, 100), F(109, 100), F(11, 10), alpha_min]
    proj = [p for p in (project(a) for a in ladder) if p]
    best_p = min((p for p in proj if p["meets_closure"]),
                 key=lambda p: -p["alpha_float"], default=None)

    out = {
        "schema": "C9_ALPHA_LEVER/1",
        "LABEL": "COUNTERFACTUAL_PROJECTION -- not certified evidence",
        "retracts": ("C9's 'blocker 1', which claimed E1 as committed cannot close cell 307. That "
                     "blocker was manufactured by defining E1 as a replay of the committed producer. "
                     "It is WITHDRAWN."),
        "certifier_cli_exposes": ["--lo", "--hi", "--alpha", "--beta", "--depth", "--degree", "--full"],
        "committed_state_of_cell_307": {
            "sub_blocks": len(blocks), "alpha_rung_taken": str(alpha_old),
            "ladder": ["6/5", "13/10", "7/5", "3/2", "2", "3"],
            "ladder_has_no_rung_below": "6/5",
            "margin_lower_bound_min": float(min(b["margin_lower_bound"] for b in blocks)),
            "margin_lower_bound_max": float(max(b["margin_lower_bound"] for b in blocks)),
            "tau_worst_sub_block": float(tau_old),
            "current_eff": float(cur["eff"])},
        "admissible_alpha_window": {
            "c_min_required": float(c_min), "alpha_min": float(alpha_min),
            "alpha_max_exclusive": float(alpha_old),
            "sufficient_condition": "c >= 1/(1+margin_lower_bound) on EVERY sub-block"},
        "projection": proj,
        "recommended_target": best_p,
        "thresholds": {"closure": float(REQUIRED_CLOSURE), "adoption": float(REQUIRED_ADOPTION)},
        "assumptions_that_must_be_DISCHARGED_BY_EXECUTION": [
            "the affine scaling of the certified surplus in w (dyadic rounding makes it approximate)",
            "that tau scales with c exactly rather than approximately",
            "that D_lo does not degrade at the smaller alpha (held FIXED here, conservatively)",
            "that every sub-block still certifies at the chosen alpha",
        ],
        "cost": {"same_geometry": True, "same_degree": True, "same_depth": True,
                 "recorded_cell_307_taboo_cpu_seconds": sum(
                     json.loads((R / b["file"]).read_bytes())["cpu_seconds"] for b in blocks),
                 "note": "a re-run at one alpha costs about what the committed run cost"},
    }
    s = C.write_evidence(C.NS / "evidence" / "phase4" / "C9_ALPHA_LEVER.json", out)
    w = out["committed_state_of_cell_307"]
    print(f"cell 307: {w['sub_blocks']} sub-blocks, all certified at the FIRST ladder rung "
          f"{w['alpha_rung_taken']}")
    print(f"margins still in hand: {w['margin_lower_bound_min']:.6f} .. {w['margin_lower_bound_max']:.6f}")
    print(f"admissible alpha window: [{out['admissible_alpha_window']['alpha_min']:.6f}, "
          f"{out['admissible_alpha_window']['alpha_max_exclusive']:.6f})\n")
    print(f"{'alpha':>8} {'c':>9} {'tau':>12} {'eff':>12} {'tightening':>11} {'closes':>7} {'adoptable':>10}")
    for p in proj:
        print(f"{p['alpha_float']:>8.6f} {p['scale_c']:>9.6f} {p['tau_projected']:>12.9f} "
              f"{p['eff_projected']:>12.9f} {p['tightening']:>11.6f} {str(p['meets_closure']):>7} "
              f"{str(p['meets_adoption']):>10}")
    print(f"\nrequired closure {float(REQUIRED_CLOSURE):.9f}   adoption {float(REQUIRED_ADOPTION):.9f}")
    if best_p:
        print(f"RECOMMENDED alpha {best_p['alpha']}: tightening {best_p['tightening']:.6f}x "
              f"-> Gamma < 0 projected {best_p['Gamma_negative_projected']}")
    print(f"wrote evidence/phase4/C9_ALPHA_LEVER.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
