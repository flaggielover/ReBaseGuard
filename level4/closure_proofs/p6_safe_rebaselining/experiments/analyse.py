"""Turn the confirmation artifacts into the tables RESULTS.md reports.

Everything here is arithmetic on ``results/confirm_*.json`` and the per-replicate
``.npz`` files.  No simulation runs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RESULTS = ROOT / "results"

from rebaseguard_p6c import stats as S                                  # noqa: E402

DETECTORS = ("cusum", "sr")
M_GRID = (1, 2, 3, 5)
PRIMARY_KEY = "cusum_m3"
PRIMARY_SHIFT = 1.0
RHO_GRID = (0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50, 0.75)
MATERIAL = 0.10          # 10% relative: P7's materiality convention


#: bootstrap resamples.  Paired resampling is CHUNKED so the index array never
#: exceeds ~40 MB: at n = 60000 replicates a single 10000 x n index block would
#: be 4.8 GB.
N_BOOT = 4000
_CHUNK = 100


def _paired_boot(a, b, fn, n_boot=N_BOOT, seed=0):
    """Bootstrap the paired ratio ``fn(a)/fn(b) - 1`` over replicate PAIRS."""
    rng = np.random.default_rng(seed)
    n = a.size
    outs = []
    for start in range(0, n_boot, _CHUNK):
        k = min(_CHUNK, n_boot - start)
        idx = rng.integers(0, n, size=(k, n))
        outs.append(fn(a[idx]) / fn(b[idx]) - 1.0)
    r = np.concatenate(outs)
    lo, hi = np.quantile(r, [0.025, 0.975])
    est = float(fn(a[None, :])[0] / fn(b[None, :])[0] - 1.0)
    corr = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else float("nan")
    return {"rel": est, "lo": float(lo), "hi": float(hi), "n": int(n),
            "pair_corr": corr, "n_boot": int(n_boot),
            "resolved": bool(lo > 0.0 or hi < 0.0)}


def _boot_rel(a, b, n_boot=N_BOOT, seed=0):
    a = np.asarray(a, float).ravel(); b = np.asarray(b, float).ravel()
    return _paired_boot(a, b, lambda x: x.mean(axis=1), n_boot, seed)


def _tail_rel(a, b, thresh, n_boot=N_BOOT, seed=0):
    return _boot_rel((a > thresh).astype(float), (b > thresh).astype(float),
                     n_boot=n_boot, seed=seed)


def _quantile_rel(a, b, q, n_boot=N_BOOT, seed=0):
    a = np.asarray(a, float).ravel(); b = np.asarray(b, float).ravel()
    return _paired_boot(a, b, lambda x: np.quantile(x, q, axis=1), n_boot, seed)


def verdict(eff, material=MATERIAL):
    if not eff["resolved"]:
        return S.INCONCLUSIVE
    return S.PRACTICALLY_MATERIAL if abs(eff["rel"]) >= material \
        else S.STATISTICALLY_RESOLVED


def pick_b2_star(delay_rows, ic_rows, objective="Dtail100"):
    """Best fixed-rho at matched Fresh on the primary objective."""
    cands = {p: delay_rows[p][objective] for p in delay_rows
             if p.startswith("B2_rho")}
    best = min(cands, key=cands.get)
    return best, cands


def main(family="eval"):
    ic = json.loads((RESULTS / f"confirm_ic_{family}.json").read_text())
    dl = json.loads((RESULTS / f"confirm_delay_{family}.json").read_text())
    out = {"family": family, "material_threshold": MATERIAL}

    # ---------- B2* per cell, on the primary objective -------------------
    b2star = {}
    for det in DETECTORS:
        for m in M_GRID:
            key = f"{det}_m{m}"
            rows = dl["cells"][f"{key}_d{PRIMARY_SHIFT}"]
            best, cands = pick_b2_star(rows, ic["cells"][key])
            b2star[key] = {"best": best, "Dtail100": cands[best],
                           "grid": cands,
                           "Arl0": ic["cells"][key][best]["Arl0"],
                           "best_by_arl0": max(
                               (p for p in ic["cells"][key] if p.startswith("B2_rho")),
                               key=lambda p: ic["cells"][key][p]["Arl0"]),
                           "best_by_rms": min(
                               (p for p in ic["cells"][key] if p.startswith("B2_rho")),
                               key=lambda p: ic["cells"][key][p]["Rms"])}
    out["b2_star"] = b2star

    # ---------- primary-cell paired comparisons --------------------------
    npz = np.load(RESULTS / f"confirm_delay_primary_{family}.npz")
    icz = np.load(RESULTS / f"confirm_ic_{family}_{PRIMARY_KEY}.npz")
    ctrl = b2star[PRIMARY_KEY]["best"]
    primary = {}
    for method in ("SAW_M", "SAW_T", "SAW_A_flat", "SAW_A_no_tau", "SAW_A_naive",
                   "B6_zbar_two_level", "B11_conf_gate", "Z1_oracle_saw",
                   "Z2_oracle_tail", "Z3_oracle_reset", "B0_fresh_only",
                   "B9_fresh_inject_2m", "B9_fresh_inject_4m"):
        if method not in npz:
            continue
        a, b = npz[method].astype(float), npz[ctrl].astype(float)
        cmp = {
            "vs": ctrl,
            "Dtail100": _tail_rel(a, b, 100), "Dtail50": _tail_rel(a, b, 50),
            "Dq95": _quantile_rel(a, b, 0.95), "Dmean": _boot_rel(a, b),
            "Dmed": _quantile_rel(a, b, 0.5),
        }
        for k in ("Arl0", "Rms", "Mad", "Q95e", "Fap100", "Tail0.5", "Tail1.0",
                  "OutCal0.25", "OutCal0.5", "Fresh", "Wbar", "FracReuse",
                  "FreshProp"):
            if f"{method}|{k}" in icz:
                cmp[k] = _boot_rel(icz[f"{method}|{k}"], icz[f"{ctrl}|{k}"])
        cmp["Coll"] = _paired_boot(
            icz[f"{method}|Coll_num"] , icz[f"{ctrl}|Coll_num"],
            lambda x: x.mean(axis=1))
        cmp["Coll_abs"] = {
            "method": float(icz[f"{method}|Coll_num"].mean()
                            / icz[f"{method}|Coll_den"].mean()),
            "control": float(icz[f"{ctrl}|Coll_num"].mean()
                             / icz[f"{ctrl}|Coll_den"].mean())}
        cmp["Wbar_abs"] = {"method": float(icz[f"{method}|Wbar"].mean()),
                           "control": float(icz[f"{ctrl}|Wbar"].mean())}
        cmp["verdicts"] = {k: verdict(v) for k, v in cmp.items()
                           if isinstance(v, dict) and "resolved" in v}
        # and against full reuse, for gate G-A
        a3 = npz["B3_full_reuse"].astype(float)
        cmp["vs_B3"] = {"Dtail100": _tail_rel(a, a3, 100),
                        "Dq95": _quantile_rel(a, a3, 0.95),
                        "Dmean": _boot_rel(a, a3)}
        primary[method] = cmp
    out["primary_cell"] = {"cell": PRIMARY_KEY, "shift": PRIMARY_SHIFT,
                           "control": ctrl, "comparisons": primary}

    # ---------- reproduction breadth -------------------------------------
    breadth = {}
    for det in DETECTORS:
        for m in M_GRID:
            key = f"{det}_m{m}"
            z = np.load(RESULTS / f"confirm_ic_{family}_{key}.npz")
            rows = dl["cells"][f"{key}_d{PRIMARY_SHIFT}"]
            ctl = b2star[key]["best"]
            cell = {}
            for method in ("SAW_M", "SAW_T"):
                e_arl = _boot_rel(z[f"{method}|Arl0"], z[f"{ctl}|Arl0"])
                e_rms = _boot_rel(z[f"{method}|Rms"], z[f"{ctl}|Rms"])
                e_out = _boot_rel(z[f"{method}|OutCal0.25"], z[f"{ctl}|OutCal0.25"])
                e_coll = _paired_boot(z[f"{method}|Coll_num"], z[f"{ctl}|Coll_num"],
                                      lambda x: x.mean(axis=1))
                cell[method] = {
                    "vs": ctl,
                    "Arl0": e_arl, "Arl0_verdict": verdict(e_arl),
                    "Rms": e_rms, "Rms_verdict": verdict(e_rms),
                    "OutCal0.25": e_out, "Coll": e_coll,
                    "Dtail100_point": rows[method]["Dtail100"],
                    "Dtail100_ctrl": rows[ctl]["Dtail100"],
                    "Dtail100_rel_point": rows[method]["Dtail100"] / rows[ctl]["Dtail100"] - 1,
                    "Dq95_rel_point": rows[method]["Dq95"] / rows[ctl]["Dq95"] - 1,
                    "Fresh_matched": bool(abs(
                        ic["cells"][key][method]["Fresh"]
                        - ic["cells"][key][ctl]["Fresh"]) < 1e-9),
                }
            breadth[key] = cell
    out["breadth"] = breadth

    # ---------- ablation ladder, all cells --------------------------------
    ladder = {}
    for det in DETECTORS:
        for m in M_GRID:
            key = f"{det}_m{m}"
            rows = dl["cells"][f"{key}_d{PRIMARY_SHIFT}"]
            icr = ic["cells"][key]
            ladder[key] = {p: {"Arl0": icr[p]["Arl0"], "Rms": icr[p]["Rms"],
                               "Coll": icr[p]["Coll"], "Wbar": icr[p]["Wbar"],
                               "Fresh": icr[p]["Fresh"],
                               "Dtail100": rows[p]["Dtail100"],
                               "Dq95": rows[p]["Dq95"], "Dmean": rows[p]["Dmean"],
                               "Dmed": rows[p]["Dmed"]}
                          for p in ("SAW_A_flat", "SAW_A_naive", "SAW_A_no_tau",
                                    "SAW_M", "SAW_T", "Z1_oracle_saw",
                                    "Z2_oracle_tail")
                          if p in rows and p in icr}
    out["ablation_ladder"] = ladder

    (RESULTS / f"analysis_{family}.json").write_text(json.dumps(out, indent=1))
    print(f"wrote analysis_{family}.json")
    print("B2* per cell:", {k: v["best"] for k, v in b2star.items()})
    for meth in ("SAW_M", "SAW_T", "Z1_oracle_saw"):
        if meth in primary:
            c = primary[meth]
            print(f"{meth} vs {ctrl}: Dtail100 {c['Dtail100']['rel']:+.3f} "
                  f"[{c['Dtail100']['lo']:+.3f},{c['Dtail100']['hi']:+.3f}] "
                  f"Dq95 {c['Dq95']['rel']:+.3f} Arl0 {c['Arl0']['rel']:+.3f} "
                  f"Rms {c['Rms']['rel']:+.3f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "eval")
