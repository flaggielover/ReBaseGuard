"""Render the P8 result tables as markdown, straight from the JSON artifacts.

No number in RESULTS.md is typed by hand: this script prints them and they are
pasted verbatim.  Run after ``derive_closure.py``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8.config import DETECTORS, FAMILIES, RESULTS      # noqa: E402


def load(n):
    p = RESULTS / n
    return json.loads(p.read_text()) if p.exists() else None


def t_gamma(mat):
    print("\n### Gamma_A(D,f,m), convention A, 4,096,000 cycles per cell\n")
    ms = [1, 2, 3, 5, 10, 20]
    print("| detector | family | ARL_0 | " + " | ".join(f"m={m}" for m in ms) + " |")
    print("|---|---|---:|" + "---:|" * len(ms))
    for c in mat["cells"]:
        cells = []
        for m in ms:
            r = c["per_m"][str(m)]
            cells.append(f"{r['gamma_A']:.3f} ± {r['gamma_A_se']:.3f}")
        mm = " *(moment-marginal)*" if c["moment_marginal"] else ""
        print(f"| {c['detector']} | `{c['family']}`{mm} | {c['arl0']:.1f} | "
              + " | ".join(cells) + " |")


def t_rhoc(mat):
    print("\n### rho_c(D,f,m) = 1/|1-Gamma_A|, with the exact monotone 95% image\n")
    ms = [1, 2, 3, 5]
    print("| detector | family | " + " | ".join(f"m={m}" for m in ms) + " | regime(m=1) |")
    print("|---|---|" + "---:|" * len(ms) + "---|")
    for c in mat["cells"]:
        cells = []
        for m in ms:
            r = c["per_m"][str(m)]
            lo, hi = r["rho_c_interval"]
            cells.append(f"{r['rho_c']:.4f} [{lo:.4f}, {hi:.4f}]"
                         if lo and hi else f"{r['rho_c']:.4f}")
        print(f"| {c['detector']} | `{c['family']}` | " + " | ".join(cells)
              + f" | {c['per_m']['1']['regime']} |")


def t_K(dec):
    g4 = dec["evidence"]["G4"]
    print("\n### K(D,f,m) = rho_c(D,f,m)/rho_c(D,f,1) -- the window law\n")
    ms = sorted(g4["per_m"], key=int) + sorted(g4["extrapolation"], key=int)
    print("| detector | family | " + " | ".join(f"m={m}" for m in ms) + " |")
    print("|---|---|" + "---:|" * len(ms))
    rows = {}
    for m in ms:
        src = g4["per_m"].get(m) or g4["extrapolation"][m]
        for e in src["entries"]:
            rows.setdefault((e["detector"], e["family"]), {})[m] = e
    for k in sorted(rows):
        print(f"| {k[0]} | `{k[1]}` | " + " | ".join(
            f"{rows[k][m]['K']:.4f} ± {rows[k][m]['K_se']:.4f}" for m in ms) + " |")
    print("\n| m | mean K | min | max | spread (max/min-1) | gate | verdict |")
    print("|---:|---:|---:|---:|---:|---:|---|")
    for m in ms:
        src = g4["per_m"].get(m)
        if src:
            print(f"| {m} | {src['mean_K']:.4f} | {src['min_K']:.4f} | "
                  f"{src['max_K']:.4f} | {src['spread']*100:.2f}% | "
                  f"<= {src['threshold']*100:.0f}% | "
                  f"{'PASS' if src['pass'] else 'FAIL'} |")
        else:
            src = g4["extrapolation"][m]
            print(f"| {m} | {src['mean_K']:.4f} | {src['min_K']:.4f} | "
                  f"{src['max_K']:.4f} | {src['spread']*100:.2f}% | "
                  f"(not gated) | EXTRAPOLATION_BEYOND_P3 |")


def t_lag(mat):
    print("\n### Normalised lag-selection profile w_r = (gamma_r-1)/(gamma_0-1)\n")
    R = 8
    print("| detector | family | " + " | ".join(f"r={r}" for r in range(R)) + " |")
    print("|---|---|" + "---:|" * R)
    for c in mat["cells"]:
        print(f"| {c['detector']} | `{c['family']}` | "
              + " | ".join(f"{c['lag_profile_w'][r]:.4f}" for r in range(R)) + " |")


def t_repro(dec):
    e = dec["evidence"]
    print("\n### Reproduction of P3 (CLOSED) -- Gaussian Gamma_A\n")
    print("| detector | m | P8 | P3 | z | relative |")
    print("|---|---:|---:|---:|---:|---:|")
    for r in e["G1a"]["rows"]:
        print(f"| {r['detector']} | {r['m']} | {r['p8']:.4f} ± {r['p8_se']:.4f} "
              f"| {r['p3']:.4f} ± {r['p3_se']:.4f} | {r['z']:+.2f} | "
              f"{r['relative']*100:+.2f}% |")
    print("\n### Reproduction of P4 (PARTIAL) -- m=1 CUSUM Gamma_f\n")
    print("| family | P8 | P4 | z | relative | moment-marginal |")
    print("|---|---:|---:|---:|---:|---|")
    for r in e["G1b"]["rows"]:
        print(f"| `{r['family']}` | {r['p8']:.4f} ± {r['p8_se']:.4f} | "
              f"{r['p4']:.4f} ± {r['p4_se']:.4f} | {r['z']:+.2f} | "
              f"{r['relative']*100:+.2f}% | {'yes' if r['moment_marginal'] else ''} |")


def t_chain(dec):
    e = dec["evidence"]["G8"]
    print("\n### Operational degradation at full reuse\n")
    print("| detector | family | m | nominal A_f(0) | ARL_0 at rho=1 | "
          "fraction of nominal | vs fresh control (rho=0) |")
    print("|---|---|---:|---:|---:|---:|---:|")
    for r in e["rows"]:
        print(f"| {r['detector']} | `{r['family']}` | {r['m']} | "
              f"{r['nominal_A_f0']:.1f} | {r['arl_rho1']:.2f} ± "
              f"{r['arl_rho1_se']:.2f} | {r['fraction_of_nominal']*100:.1f}% | "
              f"{r['reuse_attributable_relative']*100:+.1f}% |")


def t_boundary(dec):
    e = dec["evidence"]["G7"]
    print("\n### P7's boundary criterion, applied verbatim per family\n")
    print("| family | sub-families | peaks at boundary, per metric | verdict | "
          "reproduces P7 |")
    print("|---|---:|---|---|---|")
    for f, v in e["per_family"].items():
        pm = ", ".join(f"{k}:{n}" for k, n in
                       v["families_peaking_at_boundary_per_metric"].items())
        print(f"| `{f}` | {v['n_sub_families']} | {pm} | {v['verdict']} | "
              f"{'yes' if v['reproduces_P7_verdict'] else 'NO'} |")


def t_drift(dec):
    e = dec["evidence"]["G11"]
    print("\n### Drift-pattern delay (first post-change cycle), m=1\n")
    print("| detector | family | rho | pattern | mean | q50 | q95 | P(>100) | tail |")
    print("|---|---|---:|---|---:|---:|---:|---:|---|")
    for r in e["rows"]:
        if r["m"] != 1 or r["pattern"] == "none":
            continue
        lab = f"{r['pattern']}({r['size'] or r['slope']})"
        print(f"| {r['detector']} | `{r['family']}` | {r['rho']} | {lab} | "
              f"{r['delay_mean']:.2f} ± {r['delay_se']:.2f} | {r['q50']:.0f} | "
              f"{r['q95']:.0f} | {r['p_gt_100']*100:.1f}% | "
              f"{'OK' if r['tail_label']=='OK' else 'INSUFFICIENT'} |")


def t_p4rep():
    d = load("p4_replication_diagnostic.json")
    if not d:
        return
    print("\n### Replication scatter of the m=1 CUSUM gain estimator\n")
    print("| family | mean | obs. sd (12 reps) | mean nominal SE | ratio | "
          "rel. sd | median pair | max of 66 pairs | P(one pair > 3%) |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in d["rows"]:
        print(f"| `{r['family']}` | {r['mean']:.4f} | "
              f"{r['observed_across_replication_sd']:.4f} | "
              f"{r['mean_nominal_within_replication_se']:.4f} | "
              f"{r['variance_inflation_ratio']:.2f}x | "
              f"{r['relative_across_replication_sd']*100:.2f}% | "
              f"{r['median_pairwise_relative_difference']*100:.2f}% | "
              f"{r['max_pairwise_relative_difference']*100:.2f}% | "
              f"{r['empirical_P_single_pair_exceeds_3pct']*100:.1f}% |")


def t_gates(dec):
    print("\n### Gate table\n")
    print("| gate | result |")
    print("|---|---|")
    for k, v in dec["gate_results"].items():
        print(f"| `{k}` | {'PASS' if v else '**FAIL**'} |")
    print(f"\n`{dec['verdict']}` "
          f"({dec['n_pass']}/{dec['n_gates']} gates pass"
          + (f"; failed: {', '.join(dec['failed'])}" if dec["failed"] else "")
          + ")")


def main():
    mat = load("gamma_matrix_E1.json")
    dec = load("closure_decision.json")
    which = sys.argv[1:] or ["all"]
    if "all" in which or "gamma" in which:
        t_gamma(mat); t_rhoc(mat); t_lag(mat)
    if dec:
        if "all" in which or "repro" in which:
            t_repro(dec)
        if "all" in which or "K" in which:
            t_K(dec)
        if "all" in which or "chain" in which:
            t_chain(dec); t_boundary(dec)
        if "all" in which or "drift" in which:
            t_drift(dec)
        if "all" in which or "gates" in which:
            t_gates(dec)
    if "all" in which or "p4rep" in which:
        t_p4rep()


if __name__ == "__main__":
    main()
