"""Stage E per-task hypothesis evaluation against the frozen criteria.

Policy comparisons are PAIRED on the injection-event index wherever the
quantities are measured at the same grid points (E1, E4): the policies see the
same stream and the same onsets, so pairing is both valid and more powerful.
In-control cycle quantities (E2, E3) are not alignable across policies -- the
policies produce different cycle boundaries -- so those use independent block
resampling, which is stated rather than assumed away.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metrics_e import (                                      # noqa: E402
    BLOCK, BOOT_SEED, MIN_EFFECTIVE_BLOCKS, N_BOOT, _mb_indices,
    block_bootstrap_diff,
)

ROOT = Path(__file__).resolve().parents[1]
EPS_PRIMARY = 0.10          # frozen Stage E practical margin
EPS_SECONDARY = 0.05        # frozen secondary; the Stage C.1 margin, reported as-is
CLOSURE_POLICIES = ("P0_fresh", "P1_full_reuse", "P2_rebaseguard")
EXPLORATORY = "P3_moderate_EXPLORATORY"


def _paired_ratio_of_ratios(dA, wA, dB, wB, *, block=BLOCK, n_boot=N_BOOT,
                            seed=BOOT_SEED):
    """Bootstrap R_A / R_B where R = mean(delay)/mean(matched wait), pairing on
    the event index (same grid points for both policies)."""
    dA, wA, dB, wB = (np.asarray(v, float) for v in (dA, wA, dB, wB))
    n = dA.size
    rng = np.random.default_rng(seed)
    idx = _mb_indices(n, block, n_boot, rng)
    with np.errstate(invalid="ignore"):
        ra = np.nanmean(dA[idx], axis=1) / np.nanmean(wA[idx], axis=1)
        rb = np.nanmean(dB[idx], axis=1) / np.nanmean(wB[idx], axis=1)
        r = ra / rb
    point = (np.nanmean(dA) / np.nanmean(wA)) / (np.nanmean(dB) / np.nanmean(wB))
    eff = int(np.ceil(n / max(1, min(block, n))))
    return {"ratio_of_ratios": float(point),
            "ci": [float(np.nanpercentile(r, 2.5)),
                   float(np.nanpercentile(r, 97.5))],
            "upper95": float(np.nanpercentile(r, 97.5)),
            "n_events": int(n), "block": block, "n_blocks_effective": eff,
            "reliable": bool(eff >= MIN_EFFECTIVE_BLOCKS),
            "pairing": "paired on injection-event index"}


def _paired_diff_R(dA, wA, dB, wB, *, block=BLOCK, n_boot=N_BOOT, seed=BOOT_SEED):
    """Bootstrap R_A - R_B, paired on the event index."""
    dA, wA, dB, wB = (np.asarray(v, float) for v in (dA, wA, dB, wB))
    n = dA.size
    rng = np.random.default_rng(seed)
    idx = _mb_indices(n, block, n_boot, rng)
    with np.errstate(invalid="ignore"):
        d = (np.nanmean(dA[idx], axis=1) / np.nanmean(wA[idx], axis=1)
             - np.nanmean(dB[idx], axis=1) / np.nanmean(wB[idx], axis=1))
    point = (np.nanmean(dA) / np.nanmean(wA)) - (np.nanmean(dB) / np.nanmean(wB))
    ci = [float(np.nanpercentile(d, 2.5)), float(np.nanpercentile(d, 97.5))]
    eff = int(np.ceil(n / max(1, min(block, n))))
    return {"difference": float(point), "ci": ci,
            "excludes_zero": bool(ci[0] > 0 or ci[1] < 0),
            "n_events": int(n), "n_blocks_effective": eff,
            "reliable": bool(eff >= MIN_EFFECTIVE_BLOCKS),
            "pairing": "paired on injection-event index"}


def _e3_rate_boot(cycle_lengths, m, *, block=BLOCK, n_boot=N_BOOT, seed=BOOT_SEED):
    """Alert burden per 1000 observations, bootstrapped over cycles.

    Each cycle consumes (length + m) observations: the cycle itself plus the
    fresh settling block, which EVERY policy consumes.
    """
    x = np.asarray(cycle_lengths, float)
    n = x.size
    rng = np.random.default_rng(seed)
    idx = _mb_indices(n, block, n_boot, rng)
    draws = 1000.0 / (x[idx].mean(axis=1) + m)
    eff = int(np.ceil(n / max(1, min(block, n))))
    return {"rate_per_1000": float(1000.0 / (x.mean() + m)),
            "ci": [float(np.percentile(draws, 2.5)),
                   float(np.percentile(draws, 97.5))],
            "n_cycles": int(n), "n_blocks_effective": eff,
            "reliable": bool(eff >= MIN_EFFECTIVE_BLOCKS),
            "unit": "in-control cycle"}


def analyse(task_file: str) -> dict:
    d = json.loads((ROOT / "results" / task_file).read_text())
    ic, dr, m = d["in_control"], d["drift"], d["m_window"]
    conds = list(dr.keys())
    pols = list(d["policies"])

    # ---------- E1 / E4 per policy per condition -------------------------
    e1 = {c: {p: {"R_delta": dr[c][p]["E1_R_delta"]["ratio"],
                  "ci": dr[c][p]["E1_R_delta"]["ci"],
                  "n_blocks_effective": dr[c][p]["E1_R_delta"]["n_blocks_effective"],
                  "reliable": dr[c][p]["E1_R_delta"]["reliable"],
                  "R_delta_cyclelen_denominator":
                      dr[c][p]["E1_R_delta_cyclelen_denominator"]["ratio"],
                  "E4_delay": dr[c][p]["E4_delay"]["mean"],
                  "E4_ci": dr[c][p]["E4_delay"]["ci"]}
              for p in pols} for c in conds}

    # ---------- H-E3 non-inferiority of P2 vs P0, both margins -----------
    w0 = ic["P0_fresh"]["tau0_grid_matched_aligned"]
    w2 = ic["P2_rebaseguard"]["tau0_grid_matched_aligned"]
    h3 = {}
    for c in conds:
        rr = _paired_ratio_of_ratios(dr[c]["P2_rebaseguard"]["delays_aligned_to_grid"],
                                     w2,
                                     dr[c]["P0_fresh"]["delays_aligned_to_grid"],
                                     w0)
        excess = rr["ratio_of_ratios"] - 1.0
        h3[c] = {**rr, "excess_over_fresh": excess,
                 "upper95_excess": rr["upper95"] - 1.0,
                 "non_inferior_eps_0.10": bool(rr["upper95"] - 1.0 <= EPS_PRIMARY),
                 "non_inferior_eps_0.05": bool(rr["upper95"] - 1.0 <= EPS_SECONDARY)}

    # ---------- H-E1 reference-state error --------------------------------
    def e2arr(p):
        return np.array(ic[p]["E2_reference_error_values"]) if \
            "E2_reference_error_values" in ic[p] else None
    e2 = {p: ic[p]["E2_reference_error"] for p in pols}

    # ---------- H-E2 alert burden -----------------------------------------
    e3 = {p: _e3_rate_boot(ic[p]["tau0_cycle_lengths"], m) for p in pols}

    # ---------- H-E4 discrimination: R(P1) vs R(P2) at Delta = 1.0 --------
    w1 = ic["P1_full_reuse"]["tau0_grid_matched_aligned"]
    h4 = _paired_diff_R(dr["STEP_1.0"]["P1_full_reuse"]["delays_aligned_to_grid"],
                        w1,
                        dr["STEP_1.0"]["P2_rebaseguard"]["delays_aligned_to_grid"],
                        w2)
    h4["criterion"] = "R_delta(P1) > R_delta(P2) at Delta=1.0, CI excluding 0"
    h4["supported"] = bool(h4["difference"] > 0 and h4["excludes_zero"])

    out = {
        "task": d["task"], "evidence_status": d["evidence_status"],
        "protocol_sha256": d["protocol_sha256"],
        "threshold_h": d["threshold_h"], "k_events": d["k_events"],
        "m_window": m,
        "denominator": "matched in-control wait at identical grid points "
                       "(used identically for ALL policies)",
        "E1": e1, "E2": e2, "E3": e3,
        "H_E3_non_inferiority": h3, "H_E4_discrimination": h4,
        "closure_policies": list(CLOSURE_POLICIES),
        "exploratory_policy_excluded_from_closure": EXPLORATORY,
        "epsilon_primary": EPS_PRIMARY, "epsilon_secondary": EPS_SECONDARY,
    }
    (ROOT / "results" / task_file.replace(".json", "_analysis.json")).write_text(
        json.dumps(out, indent=2) + "\n")
    return out


if __name__ == "__main__":
    a = analyse(sys.argv[1])
    print(json.dumps({k: v for k, v in a.items()
                      if k in ("task", "evidence_status", "threshold_h")}, indent=2))
