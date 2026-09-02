"""Aggregate the per-cell Gamma batches into one matrix, with paired covariance.

The 20 addressable batches of a cell are independent by construction, so the
batch-means SE is the honest uncertainty for a single cell.  Across cells the
picture is different: the stopped-cycle address deliberately omits the detector,
the window and the convention, so ``cusum`` and ``sr`` at the same
``(family, batch)`` are driven by the **same** innovations.  Every
cross-detector, cross-window or cross-convention comparison is therefore paired,
and this aggregator stores the batch vectors themselves so that downstream
ratios use the paired covariance rather than a naive independent-SE formula.
That is a preregistered requirement of ``STATISTICAL_ANALYSIS_PLAN.md`` §3 and
was one of the corrections the P8 adjudication had to make by hand.

Usage:  aggregate_gamma.py <E1|E5>
"""
from __future__ import annotations

import sys

import numpy as np

import _common as C                                              # noqa: E402
from rebaseguard_p8r.analysis import batch_mean_se, rho_c_from_gamma  # noqa
from rebaseguard_p8r.config import (DETECTORS, FAMILIES,         # noqa: E402
                                     LAG_DEPTH, M_GRID, RESULTS)


def main() -> None:
    tag = sys.argv[1]
    cells, batch_vectors = [], {}
    for det in DETECTORS:
        for fam in FAMILIES:
            p = RESULTS / "gamma" / f"{tag}_{det}_{fam}.json"
            if not p.exists():
                raise FileNotFoundError(p)
            c = C.load_payload(p)
            if c["status"] != "OK":
                cells.append({"detector": det, "family": fam,
                              "status": c["status"], "reason": c["reason"]})
                continue
            B = c["batches"]
            rec = {"detector": det, "family": fam, "status": "OK",
                   "threshold": c["threshold"],
                   "threshold_provenance": c["threshold_provenance"],
                   "n_batches": len(B), "n_cycles": c["n_cycles"],
                   "arl": batch_mean_se([b["arl"] for b in B])[0],
                   "arl_se": batch_mean_se([b["arl"] for b in B])[1],
                   "n_ties_total": sum(b["n_ties"] for b in B),
                   "max_tau": max(b["max_tau"] for b in B),
                   "per_m": {}}
            for m in M_GRID:
                key = str(m)
                gA = np.array([b["gamma_A"][key] for b in B])
                gB = np.array([b["gamma_B"][key] for b in B])
                gN = np.array([b["gamma_naive"][key] for b in B])
                gP = np.array([b["gamma_psipsi"][key] for b in B])
                Rm = np.array([b["R_m"][key] for b in B])
                pt = np.array([b["p_tau_lt_m"][key] for b in B])
                mA, sA, _ = batch_mean_se(gA)
                d = rho_c_from_gamma(mA, sA)
                # exact per-batch algebraic residuals (P8R-L1(b) / convention)
                lag = np.array([b["gamma_lag"] for b in B])       # (nb, L)
                lag_mean = lag[:, :m].mean(axis=1) if m <= LAG_DEPTH else None
                resid = gA - lag_mean - Rm if lag_mean is not None else None
                rec["per_m"][key] = {
                    "gamma_A": mA, "gamma_A_se": sA,
                    "gamma_B": batch_mean_se(gB)[0],
                    "gamma_B_se": batch_mean_se(gB)[1],
                    "gamma_naive": batch_mean_se(gN)[0],
                    "gamma_psipsi": batch_mean_se(gP)[0],
                    "R_m": batch_mean_se(Rm)[0],
                    "R_m_se": batch_mean_se(Rm)[1],
                    "p_tau_lt_m": float(pt.mean()),
                    "convention_residual_max_abs":
                        float(np.max(np.abs(gA - gB - Rm))),
                    "decomposition_residual":
                        None if resid is None else float(resid.mean()),
                    "decomposition_residual_max_abs":
                        None if resid is None else float(
                            np.max(np.abs(resid))),
                    "rho_c": d["rho_c"], "rho_c_interval": d["rho_c_interval"],
                    "gamma_ci95": d["gamma_ci95"], "regime": d["regime"],
                    "lower_bound_exceeds_2": d["lower_bound_exceeds_2"],
                }
                batch_vectors[f"{det}|{fam}|{m}"] = [float(x) for x in gA]
            rec["gamma_lag_mean"] = [
                float(np.mean([b["gamma_lag"][r] for b in B]))
                for r in range(LAG_DEPTH)]
            rec["p_tau_gt_r"] = [
                float(np.mean([b["p_tau_gt_r"][r] for b in B]))
                for r in range(LAG_DEPTH)]
            cells.append(rec)

    payload = {"tag": tag, "m_grid": list(M_GRID),
               "n_cells": len(cells), "cells": cells,
               "batch_gamma_A": batch_vectors,
               "pairing_note": ("batch_gamma_A holds the raw per-batch "
                                "Gamma_A vectors; detector/window/convention "
                                "comparisons at equal (family, batch) are CRN "
                                "paired and MUST use their covariance.")}
    C.write(RESULTS / f"gamma_matrix_{tag}.json",
            C.envelope(generator="aggregate_gamma.py",
                       schema="rebaseguard.p8r.gamma-matrix.v1",
                       tags=[], payload=payload))
    ok = [c for c in cells if c["status"] == "OK"]
    print(f"{tag}: {len(ok)}/{len(cells)} cells OK")
    for c in ok:
        print(f"  {c['detector']:5s}/{c['family']:11s} "
              f"Gamma_A(1)={c['per_m']['1']['gamma_A']:.4f}"
              f"+-{c['per_m']['1']['gamma_A_se']:.4f} "
              f"rho_c(1)={c['per_m']['1']['rho_c']:.6f}")


if __name__ == "__main__":
    main()
