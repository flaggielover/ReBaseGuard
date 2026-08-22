#!/usr/bin/env python
"""Gate 4.2 driver — conditional nonlinear map estimator.

Stages, in order, each one gated on the previous:

1.  score route          Gamma(m) and F_1'(0) = 1 - Gamma from an e = 0 sample.
                         This is the link to the frozen Level 1-3 certificate.
2.  coarse map           F_rho on a wide symmetric grid: locates the bend-back,
                         the extrema, and any sign change of H_rho.
3.  near-zero map        dense symmetric grid for the local derivative, run
                         twice: once with common random numbers, once with
                         independent seeds and CRN off.
4.  adaptive refinement  a dense grid around each located H_rho sign change.
5.  analysis             derivative correspondence, symmetry, roots, candidate
                         classification, and the rho transition.

Everything is written to level4/results and consumed by the figure and report
scripts; nothing is computed twice in a notebook.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rebaseguard_level4 import analysis, provenance, storage  # noqa: E402
from rebaseguard_level4.campaigns import (  # noqa: E402
    RESULTS,
    run_gate42_gamma,
    run_gate42_map,
)

GAMMA_CERT_LOW = 3.9243482005828971281857775466050952672958374023437500
GAMMA_CERT_HIGH = 27.849382127546703280529527546605095267295837402343750

COARSE_HALF = (0.0125, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35,
               0.4, 0.5, 0.6, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0)
NEAR_ZERO_HALF = (0.0125, 0.025, 0.0375, 0.05, 0.0625, 0.075, 0.0875, 0.1,
                  0.1125, 0.125, 0.1375, 0.15)
DELTA_SCAN = (0.15, 0.1, 0.075, 0.05, 0.025, 0.0125)
FIT_WINDOWS = (0.05, 0.075, 0.1, 0.125, 0.15)


def symmetric(half: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(sorted({0.0, *half, *(-v for v in half)}))


def records_arrays(result: dict, key: str) -> tuple[np.ndarray, ...]:
    recs = result["records"]
    e = np.array([r["e"] for r in recs])
    f = np.array([r[key] for r in recs])
    s = np.array([r[f"{key}_se"] for r in recs])
    order = np.argsort(e)
    return e[order], f[order], s[order]


def batch_matrix(result: dict, key: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(e, batch_means[n_batches, n_grid], se)`` sorted by ``e``."""
    recs = result["records"]
    e = np.array([r["e"] for r in recs])
    order = np.argsort(e)
    e = e[order]
    means = np.array([recs[i][f"{key}_batch_means"] for i in order]).T
    se = np.array([recs[i][f"{key}_se"] for i in order])
    return e, means, se

def half_batch_arrays(result: dict, key: str) -> tuple[np.ndarray, ...]:
    """Estimate the map from only the first half of each grid point's batches.

    This is an honest Monte-Carlo-sample-size sensitivity: same seeds, same
    grid, half the paths.  Comparing a coarse grid against a refined one (as an
    earlier version of this driver did) measures grid resolution, not sample
    size, and mislabels every candidate.
    """
    recs = result["records"]
    e, f, s = [], [], []
    for r in recs:
        means = np.asarray(r[f"{key}_batch_means"], dtype=float)
        half = means[: max(len(means) // 2, 2)]
        e.append(r["e"])
        f.append(float(half.mean()))
        s.append(float(half.std(ddof=1) / np.sqrt(half.size)))
    e, f, s = np.array(e), np.array(f), np.array(s)
    order = np.argsort(e)
    return e[order], f[order], s[order]


def first_root(e, f, s, *, rho, derivative=None):
    accepted = analysis.find_h_roots(e, f, s, rho=rho, derivative=derivative)
    return accepted[0] if accepted else None

def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    cfg = json.loads(Path(argv[1]).read_text())
    stage, m, seed = cfg["stage"], cfg["m"], cfg["master_seed"]
    rho_values = tuple(cfg["rho_values"])
    all_rho = tuple(sorted({0.0, *rho_values, 1.0}))
    started = time.time()
    print(f"Gate 4.2 — stage={stage}, m={m}")
    print(f"  purpose: {cfg['purpose']}\n")

    findings: dict[str, object] = {
        "gate": "4.2", "stage": stage, "m": m, "master_seed": seed,
        "certified_gamma_enclosure": [GAMMA_CERT_LOW, GAMMA_CERT_HIGH],
    }

    # -- 1. score route ----------------------------------------------------
    print("1. score / change-of-measure route")
    gamma_run = run_gate42_gamma(
        stage=stage, n_paths=cfg["gamma_paths"], m_values=[m],
        master_seed=seed, n_batches=cfg["gamma_batches"],
        seed_replicates=(0, 1))
    primary, replication = gamma_run["records"][0], gamma_run["records"][1]
    pooled_gamma = 0.5 * (primary["gamma"] + replication["gamma"])
    pooled_se = 0.5 * np.hypot(primary["gamma_se"], replication["gamma_se"])
    score_slope = 1.0 - pooled_gamma
    findings["score_route"] = {
        "experiment_id": gamma_run["experiment_id"],
        "primary": primary, "independent_seed_replication": replication,
        "pooled_gamma": pooled_gamma, "pooled_gamma_se": pooled_se,
        "F1_prime_0": score_slope, "F1_prime_0_se": pooled_se,
        "inside_certified_enclosure":
            bool(GAMMA_CERT_LOW < pooled_gamma < GAMMA_CERT_HIGH),
        "seed_replication_z": float(
            abs(primary["gamma"] - replication["gamma"])
            / np.hypot(primary["gamma_se"], replication["gamma_se"])),
    }
    print(f"   pooled Gamma = {pooled_gamma:.4f} +/- {pooled_se:.4f}"
          f"   ->  F1'(0) = {score_slope:.4f}")
    print(f"   inside certified enclosure: "
          f"{findings['score_route']['inside_certified_enclosure']}\n")

    # -- 2. coarse map -----------------------------------------------------
    print("2. coarse conditional map")
    coarse = run_gate42_map(
        stage=stage, label="coarse", e_values=symmetric(COARSE_HALF),
        n_paths_per_e=cfg["coarse_paths"], m=m, master_seed=seed,
        rho_values=all_rho, n_batches=cfg["n_batches"],
        common_random_numbers=True, seed_replicate=0)
    findings["coarse_map"] = {"experiment_id": coarse["experiment_id"],
                              "result": coarse["result"]}

    # -- 3. near-zero map, twice ------------------------------------------
    print("3. near-zero maps (CRN primary, independent-seed replication)")
    near = run_gate42_map(
        stage=stage, label="near_zero_crn", e_values=symmetric(NEAR_ZERO_HALF),
        n_paths_per_e=cfg["near_zero_paths"], m=m, master_seed=seed,
        rho_values=all_rho, n_batches=cfg["n_batches"],
        common_random_numbers=True, seed_replicate=0)
    near_indep = run_gate42_map(
        stage=stage, label="near_zero_independent",
        e_values=symmetric(NEAR_ZERO_HALF),
        n_paths_per_e=cfg["near_zero_paths"], m=m, master_seed=seed,
        rho_values=all_rho, n_batches=cfg["n_batches"],
        common_random_numbers=False, seed_replicate=1)

    e, f1, s1 = records_arrays(near["result"], "F1")
    eb, mb, sb = batch_matrix(near["result"], "F1")
    selection = analysis.select_derivative_fit(eb, mb, sb, windows=FIT_WINDOWS)
    fit = selection["selected"]
    if fit is None:
        raise RuntimeError(
            "no polynomial order converged on any fit window; the derivative "
            "estimate is not defensible and Gate 4.2 cannot proceed"
        )
    # Replicate with independent seeds at the SELECTED window and order, so the
    # replication tests the same estimator rather than a differently-chosen one.
    ebi, mbi, sbi = batch_matrix(near_indep["result"], "F1")
    fit_i = analysis.odd_polynomial_fit_batched(
        ebi, mbi, max_abs_e=fit["max_abs_e"], n_terms=fit["n_terms"])
    scan = analysis.central_difference_scan(e, f1, s1, DELTA_SCAN)
    symmetry = analysis.symmetry_diagnostics(e, f1, s1)

    direct_slope = fit["derivative_at_zero"]
    direct_se = fit["derivative_at_zero_se"]
    gap = direct_slope - score_slope
    gap_se = float(np.hypot(direct_se, pooled_se))
    findings["near_zero"] = {
        "experiment_id": near["experiment_id"],
        "independent_experiment_id": near_indep["experiment_id"],
        "odd_polynomial_fit": fit,
        "odd_polynomial_fit_independent_seed": fit_i,
        "fit_selection": selection,
        "central_difference_scan": scan,
        "symmetry": symmetry,
        "result": near["result"],
        "result_independent": near_indep["result"],
    }
    findings["derivative_correspondence"] = {
        "direct_conditional_simulator": {"F1_prime_0": direct_slope,
                                         "se": direct_se},
        "score_change_of_measure": {"F1_prime_0": score_slope, "se": pooled_se},
        "independent_seed_direct": {
            "F1_prime_0": fit_i["derivative_at_zero"],
            "se": fit_i["derivative_at_zero_se"]},
        "gap": gap, "gap_se": gap_se,
        "gap_z": float(abs(gap) / gap_se) if gap_se else float("nan"),
        "certified_F1_prime_0_enclosure": [1.0 - GAMMA_CERT_HIGH,
                                           1.0 - GAMMA_CERT_LOW],
        "direct_inside_certified_enclosure":
            bool(1.0 - GAMMA_CERT_HIGH < direct_slope < 1.0 - GAMMA_CERT_LOW),
        "verdict": ("CONSISTENT" if abs(gap) < 3.0 * gap_se
                    else "MATERIAL-DISAGREEMENT"),
    }
    print(f"   direct  F1'(0) = {direct_slope:.4f} +/- {direct_se:.4f}")
    print(f"   score   F1'(0) = {score_slope:.4f} +/- {pooled_se:.4f}")
    print(f"   gap = {gap:+.4f} ({findings['derivative_correspondence']['gap_z']:.2f} "
          f"sigma) -> {findings['derivative_correspondence']['verdict']}")
    print(f"   symmetry max|z| = {symmetry['max_abs_z']:.2f}\n")

    # -- 4. rho transition -------------------------------------------------
    print("4. rho transition")
    rho_rows = []
    for rho in all_rho:
        key = f"F_rho_{rho:g}"
        er, mr, sr = batch_matrix(near["result"], key)
        # Same window and order as the F_1 fit: chosen once, applied uniformly,
        # so the rho scan cannot be tuned point by point.
        rfit = analysis.odd_polynomial_fit_batched(
            er, mr, max_abs_e=fit["max_abs_e"], n_terms=fit["n_terms"])
        rho_rows.append({
            "rho": rho,
            "F_rho_prime_0": rfit["derivative_at_zero"],
            "F_rho_prime_0_se": rfit["derivative_at_zero_se"],
            "predicted_rho_times_F1_prime_0": rho * direct_slope,
            "chi2_per_dof": float("nan"),
            "fit_window": fit["max_abs_e"], "fit_n_terms": fit["n_terms"],
        })
        print(f"   rho={rho:<5g}  F'_rho(0) = {rfit['derivative_at_zero']:+8.4f} "
              f"+/- {rfit['derivative_at_zero_se']:.4f}   "
              f"(rho*F1'(0) = {rho * direct_slope:+8.4f})")
    crit = analysis.critical_rho(direct_slope, direct_se)
    crit_score = analysis.critical_rho(score_slope, pooled_se)
    certified = analysis.rho_c_from_gamma_interval(GAMMA_CERT_LOW,
                                                   GAMMA_CERT_HIGH)
    findings["rho_transition"] = {
        "rows": rho_rows,
        "rho_c_from_direct": crit,
        "rho_c_from_score": crit_score,
        "rho_c_certified_enclosure": certified,
        "note": "the rho scan reuses one set of simulated cycles with different "
                "re-baselining weights, so the points are perfectly correlated "
                "across rho by construction; that IS the policy definition, but "
                "it means the scan cannot independently confirm linearity",
    }
    print(f"   rho_c (direct) = {crit['rho_c']:.5f} "
          f"[{crit['rho_c_ci95'][0]:.5f}, {crit['rho_c_ci95'][1]:.5f}]")
    print(f"   rho_c certified enclosure = "
          f"[{certified['rho_c_enclosure'][0]:.5f}, "
          f"{certified['rho_c_enclosure'][1]:.5f}]\n")

    # -- 5. H_rho roots and adaptive refinement ----------------------------
    print("5. H_rho roots and adaptive refinement")
    root_findings = []
    for rho in all_rho:
        key = f"F_rho_{rho:g}"
        ec, fc, sc = records_arrays(coarse["result"], key)
        deriv_c = analysis.local_derivative(ec, fc, sc, half_window=3)
        screen = analysis.find_h_crossings(ec, fc, sc, rho=rho,
                                           derivative=deriv_c)
        entry: dict[str, object] = {
            "rho": rho,
            "coarse_experiment_id": coarse["experiment_id"],
            "coarse_accepted": [r.as_dict() for r in screen["accepted"]],
            "coarse_rejected": screen["rejected"],
        }
        if not screen["accepted"]:
            entry["classification"] = "NO-CANDIDATE"
            entry["reason"] = (
                "no statistically supported sign change of H_rho away from "
                "e = 0 on the coarse grid"
            )
            root_findings.append(entry)
            print(f"   rho={rho:<5g}  NO-CANDIDATE"
                  + (f"  ({len(screen['rejected'])} sub-threshold sign "
                     f"change(s) screened out)" if screen["rejected"] else ""))
            continue

        best = screen["accepted"][0]
        lo, hi = best.bracket
        pad = 0.4 * (hi - lo)
        fine_half = tuple(np.linspace(max(lo - pad, 1e-3), hi + pad, 13))
        refined = run_gate42_map(
            stage=stage, label=f"root_refine_rho{rho:g}",
            e_values=symmetric(fine_half), n_paths_per_e=cfg["root_paths"],
            m=m, master_seed=seed, rho_values=(rho,),
            n_batches=cfg["n_batches"], common_random_numbers=True,
            seed_replicate=0)
        refined_indep = run_gate42_map(
            stage=stage, label=f"root_refine_indep_rho{rho:g}",
            e_values=symmetric(fine_half), n_paths_per_e=cfg["root_paths"],
            m=m, master_seed=seed, rho_values=(rho,),
            n_batches=cfg["n_batches"], common_random_numbers=False,
            seed_replicate=1)

        er, fr, sr = records_arrays(refined["result"], key)
        rderiv = analysis.local_derivative(er, fr, sr, half_window=3)
        primary_root = first_root(er, fr, sr, rho=rho, derivative=rderiv)
        if primary_root is None:
            entry["classification"] = "NUMERICALLY-INCONSISTENT"
            entry["reason"] = ("the coarse grid carried a supported sign change "
                               "but the refined grid did not reproduce it")
            entry["refined_experiment_id"] = refined["experiment_id"]
            root_findings.append(entry)
            print(f"   rho={rho:<5g}  NUMERICALLY-INCONSISTENT "
                  f"(refinement lost the crossing)")
            continue

        # sensitivities, each varying exactly one thing
        sub = slice(None, None, 2)
        grid_root = first_root(er[sub], fr[sub], sr[sub], rho=rho)
        mc_root = first_root(*half_batch_arrays(refined["result"], key), rho=rho)
        ei, fi, si = records_arrays(refined_indep["result"], key)
        seed_root = first_root(ei, fi, si, rho=rho)
        grid_shift = (grid_root.e_star - primary_root.e_star
                      if grid_root else None)
        mc_shift = mc_root.e_star - primary_root.e_star if mc_root else None
        seed_shift = (seed_root.e_star - primary_root.e_star
                      if seed_root else None)

        # dedicated confirmation run exactly AT the located root, both signs.
        # The interpolated residual is zero by construction, so it proves
        # nothing; only a fresh simulation at e* is a real residual test.
        confirm = run_gate42_map(
            stage=stage, label=f"root_confirm_rho{rho:g}",
            e_values=(-primary_root.e_star, primary_root.e_star),
            n_paths_per_e=cfg["root_paths"], m=m, master_seed=seed,
            rho_values=(rho,), n_batches=cfg["n_batches"],
            common_random_numbers=False, seed_replicate=2)
        cneg, cpos = confirm["result"]["records"]
        resid = float(cpos[key] + cpos["e"])
        resid_se = float(cpos[f"{key}_se"])
        sym_at_root = float(cpos[key] + cneg[key])
        sym_at_root_se = float(np.hypot(cpos[f"{key}_se"], cneg[f"{key}_se"]))
        sym_z = sym_at_root / sym_at_root_se if sym_at_root_se else float("nan")

        classified = analysis.classify_candidate(
            primary_root, h_residual_direct=resid, h_residual_direct_se=resid_se,
            symmetry_z=sym_z, grid_sensitivity=grid_shift,
            mc_sensitivity=mc_shift, seed_replication_delta=seed_shift)
        entry.update({
            "classification": classified.classification,
            "refined": classified.as_dict(),
            "refined_experiment_id": refined["experiment_id"],
            "independent_experiment_id": refined_indep["experiment_id"],
            "confirmation_experiment_id": confirm["experiment_id"],
            "confirmation": {
                "e_star_used": primary_root.e_star,
                "H_residual": resid, "H_residual_se": resid_se,
                "H_residual_z": abs(resid) / resid_se if resid_se else None,
                "F_at_plus": cpos[key], "F_at_minus": cneg[key],
                "odd_symmetry_gap": sym_at_root,
                "odd_symmetry_gap_se": sym_at_root_se,
                "odd_symmetry_z": sym_z,
            },
            "sensitivities": {
                "grid_halved_shift": grid_shift,
                "sample_size_halved_shift": mc_shift,
                "independent_seed_shift": seed_shift,
                "e_star_ci95_width": 2 * analysis.Z95 * primary_root.e_star_se,
            },
        })
        root_findings.append(entry)
        print(f"   rho={rho:<5g}  e* = {classified.e_star:.5f} "
              f"+/- {classified.e_star_se:.5f}   "
              f"F'(e*) = {classified.derivative:+.4f}   "
              f"multiplier = {classified.multiplier:.4f}   "
              f"H(e*) = {resid:+.5f} ({abs(resid) / resid_se:.1f}z)   "
              f"-> {classified.classification}")
    findings["h_roots"] = root_findings

    findings["runtime_seconds"] = time.time() - started
    exp_id = provenance.experiment_id("gate4.2-findings", stage,
                                      {**cfg, "stage": stage})
    out_dir = RESULTS / "processed" / exp_id
    manifest = provenance.build_manifest(
        gate="4.2", stage=stage, config=cfg,
        extra={"role": "aggregated Gate 4.2 findings",
               "runtime_seconds": findings["runtime_seconds"]})
    provenance.write_manifest(manifest, out_dir / "manifest.json")
    storage.write_json(findings, out_dir / "findings.json")
    latest = RESULTS / "processed" / f"gate42_findings_{stage}.json"
    storage.write_json({"experiment_id": exp_id,
                        "findings_path": str(out_dir / "findings.json")},
                       latest)
    print(f"\nfindings   : {out_dir / 'findings.json'}")
    print(f"total time : {findings['runtime_seconds']:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
