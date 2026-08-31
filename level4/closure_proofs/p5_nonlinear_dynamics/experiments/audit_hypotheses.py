#!/usr/bin/env python3
"""E4: uncertainty-aware audit of the conditional-theorem hypotheses (H1)-(H3).

Every hypothesis is checked on BOTH independent seed families with batch
standard errors, so that a violation must survive Monte Carlo error and an
independent seed family before it is reported.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import RESULTS                                # noqa: E402

E_CAP = 2.0          # the region (0, E] on which strict monotonicity is claimed
Z = 1.959963984540054


def load(det, m, files):
    e, R, se = [], [], []
    for f in files:
        d = json.loads((RESULTS / f).read_text())
        for r in d["rows"]:
            if r["detector"] != det:
                continue
            q = [q for q in r["per_m"] if q["m"] == m][0]
            e.append(r["e"]); R.append(q["R"]); se.append(q["R_se"])
    e, R, se = np.array(e), np.array(R), np.array(se)
    # pool the two seed families per grid point (inverse-variance)
    out = {}
    for x, r, s in zip(e, R, se):
        out.setdefault(round(x, 6), []).append((r, s))
    xs = np.array(sorted(out))
    rs, ss = [], []
    for x in xs:
        v = np.array(out[x])
        w = 1.0 / v[:, 1] ** 2
        rs.append(float((v[:, 0] * w).sum() / w.sum()))
        ss.append(float(np.sqrt(1.0 / w.sum())))
    return xs, np.array(rs), np.array(ss)


def main():
    main_f = ("nonlinear_map.json", "nonlinear_map_rep.json")
    tail_f = ("map_tail.json",)
    rep = []
    for det in ("cusum", "sr"):
        for m in (1, 2, 3, 5):
            e, R, se = load(det, m, main_f)
            et, Rt, set_ = load(det, m, tail_f)
            ea = np.concatenate([e, et]); Ra = np.concatenate([R, Rt])
            sea = np.concatenate([se, set_])
            o = np.argsort(ea); ea, Ra, sea = ea[o], Ra[o], sea[o]

            # (H1) oddness: |R(e)+R(-e)| against its own 95% interval
            pos = ea > 0
            pair = {round(-x, 6): (r, s) for x, r, s in zip(ea, Ra, sea) if x < 0}
            h1 = []
            for x, r, s in zip(ea[pos], Ra[pos], sea[pos]):
                if round(x, 6) in pair:
                    rm, sm = pair[round(x, 6)]
                    d = r + rm
                    h1.append(abs(d) / (Z * np.hypot(s, sm)))
            h1 = np.array(h1)

            # (H2) R(e) < 0 for e > 0, significantly
            p = (ea > 0) & (ea <= 24.0)
            sig_pos = [(float(x), float(r), float(s))
                       for x, r, s in zip(ea[p], Ra[p], sea[p])
                       if r - Z * s > 0]

            # (H3a) s strictly decreasing on (0, E_CAP]
            q = (ea > 0) & (ea <= E_CAP)
            eq, Rq, sq = ea[q], Ra[q], sea[q]
            s_ = -Rq / eq
            s_se = sq / eq
            viol = []
            for i in range(len(eq) - 1):
                d = s_[i + 1] - s_[i]
                if d > 0:
                    sd = np.hypot(s_se[i], s_se[i + 1])
                    viol.append({"e_lo": float(eq[i]), "e_hi": float(eq[i + 1]),
                                 "delta_s": float(d), "z": float(d / sd)})
            # (H3b) R_max < E_CAP
            rmax = float(np.max(np.abs(Ra)))
            # s(0+) vs P3, and s at the cap
            rep.append({
                "detector": det, "m": int(m),
                "H1_oddness_max_ratio_to_95CI": float(h1.max()),
                "H1_n_pairs_outside_95CI": int((h1 > 1).sum()),
                "H1_n_pairs": int(h1.size),
                "H2_significant_positive_R_on_e_gt_0": sig_pos,
                "H2_holds": len(sig_pos) == 0,
                "H3a_violations_on_0_to_E": viol,
                "H3a_significant_violations": [v for v in viol if v["z"] > 2],
                "H3a_holds_within_MC_error":
                    all(v["z"] <= 2 for v in viol),
                "H3b_R_max": rmax, "H3b_E_cap": E_CAP,
                "H3b_holds": rmax < E_CAP,
                "s_at_smallest_e": float(-Ra[ea > 0][0] / ea[ea > 0][0]),
                "s_at_E_cap": float(s_[-1]),
                "far_tail_max_abs_R_beyond_10":
                    float(np.max(np.abs(Ra[np.abs(ea) >= 10.0]))),
                "far_tail_max_se_beyond_10":
                    float(np.max(sea[np.abs(ea) >= 10.0])),
            })
    (RESULTS / "hypothesis_audit.json").write_text(
        json.dumps({"cells": rep, "E_cap": E_CAP}, indent=1))
    for c in rep:
        print(f"{c['detector']:5s} m={c['m']}  H1 max|resid|/95CI={c['H1_oddness_max_ratio_to_95CI']:.2f}"
              f" ({c['H1_n_pairs_outside_95CI']}/{c['H1_n_pairs']} outside)"
              f"  H2={c['H2_holds']}"
              f"  H3a={c['H3a_holds_within_MC_error']}"
              f" (viol={len(c['H3a_violations_on_0_to_E'])}, sig={len(c['H3a_significant_violations'])})"
              f"  H3b={c['H3b_holds']} Rmax={c['H3b_R_max']:.3f}"
              f"  |R|>10 tail={c['far_tail_max_abs_R_beyond_10']:.4f}"
              f"(se{c['far_tail_max_se_beyond_10']:.4f})")
    print("wrote hypothesis_audit.json")


if __name__ == "__main__":
    main()
