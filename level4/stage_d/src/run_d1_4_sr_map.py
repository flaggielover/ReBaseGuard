"""D1.4 -- SR induced map and period-2 candidate at m = 1.

Gated on D1.2 passing with Gamma_SR > 4. Symmetric period-2 orbits satisfy
F(e) = -e, i.e. a root of H(e) = F(e) + e, using odd symmetry F(-e) = -F(e).

CUSUM is run alongside on the same grid purely as a replication check against
the Stage B certified root e* in [1.028724, 1.044724]. That certificate is NOT
transferred to SR by this run; nothing here is certified.
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stopped import CUSUM, SR, simulate_stopped              # noqa: E402

SEED = 20261001
N_POINT = 500_000
BATCH = 250_000
E_SCAN = [0.4, 0.6, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.8]   # committed in advance
N_REFINE = 6
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "d1_4_sr_map.json"
Z = 1.959964
M1 = np.array([1], dtype=np.int64)


def _git() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, cwd=ROOT).stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def H_at(detector: str, threshold: float, e: float,
         key: list[int]) -> tuple[float, float]:
    """H(e) = F(e) + e and its SE."""
    ss = np.random.SeedSequence(key)
    stats = None
    for child in ss.spawn(N_POINT // BATCH):
        rng = np.random.Generator(np.random.PCG64(child))
        s = simulate_stopped(detector=detector, threshold=threshold, e=e,
                             n_paths=BATCH, L=2, m_grid=M1, rng=rng)
        stats = s if stats is None else stats.combine(s)
    F = float(stats.induced_map(e)[0])
    se = float(stats.induced_map_se()[0])
    return F + e, se


def scan(detector: str, threshold: float, tag: int) -> dict:
    print(f"  {detector}: coarse scan", flush=True)
    pts = []
    for i, e in enumerate(E_SCAN):
        h, se = H_at(detector, threshold, e, [SEED, 50, tag, i])
        pts.append({"e": e, "H": h, "se": se, "z": h / se})
        print(f"    e={e:<5} H={h:+.5f} +/- {se:.5f}  ({h / se:+7.1f} SE)",
              flush=True)

    # a candidate needs a sign change with BOTH ends more than 3 SE from zero
    bracket, rejected = None, []
    for a, b in zip(pts, pts[1:]):
        if a["H"] * b["H"] < 0:
            if abs(a["z"]) > 3.0 and abs(b["z"]) > 3.0:
                bracket = (a, b)
                break
            rejected.append({"e_lo": a["e"], "e_hi": b["e"],
                             "z_lo": a["z"], "z_hi": b["z"],
                             "reason": "sign change within 3 SE of zero"})

    result = {"detector": detector, "threshold": threshold, "scan": pts,
              "rejected_crossings": rejected}
    if bracket is None:
        result["verdict"] = "NO-CANDIDATE"
        result["root"] = None
        print(f"    -> NO-CANDIDATE", flush=True)
        return result

    lo, hi = bracket[0]["e"], bracket[1]["e"]
    h_lo = bracket[0]["H"]
    print(f"  {detector}: refining in [{lo}, {hi}]", flush=True)
    for it in range(N_REFINE):
        mid = 0.5 * (lo + hi)
        h, se = H_at(detector, threshold, mid, [SEED, 51, tag, it])
        print(f"    e={mid:.6f} H={h:+.5f} +/- {se:.5f}", flush=True)
        if h * h_lo > 0:
            lo, h_lo = mid, h
        else:
            hi = mid
    root = 0.5 * (lo + hi)
    h_root, se_root = H_at(detector, threshold, root, [SEED, 52, tag, 0])

    # slope from the coarse bracket, to convert the H uncertainty into an e CI
    slope = ((bracket[1]["H"] - bracket[0]["H"])
             / (bracket[1]["e"] - bracket[0]["e"]))
    mc_se = abs(se_root / slope) if slope != 0 else float("nan")
    # The bisection grid, not the Monte Carlo, can be the binding constraint:
    # after N_REFINE halvings the root is only located to within the final
    # bracket width. Quoting the MC SE alone would overstate the precision.
    resolution = abs(hi - lo)
    res_half = 0.5 * resolution
    root_half_width = float(np.hypot(Z * mc_se, res_half))
    result.update({
        "verdict": "CANDIDATE",
        "root": root, "root_bracket": [lo, hi],
        "H_at_root": h_root, "H_se_at_root": se_root,
        "local_slope": slope,
        "root_se_monte_carlo": mc_se,
        "bisection_resolution": resolution,
        "resolution_limited": bool(res_half > Z * mc_se),
        "root_half_width": root_half_width,
        "root_interval": [root - root_half_width, root + root_half_width],
        "precision_note": (
            "root_half_width combines the Monte Carlo uncertainty with the "
            "half-width of the final bisection bracket. The Monte Carlo SE "
            "ALONE would overstate the precision whenever the bisection grid "
            "is the binding constraint."),
    })
    print(f"    -> CANDIDATE root e* = {root:.6f} "
          f"+/- {root_half_width:.6f}  (MC {mc_se:.6f}, "
          f"bisection resolution {resolution:.6f})", flush=True)
    return result


def main() -> None:
    t0 = time.time()
    d1 = json.loads((ROOT / "results" / "d1_gamma.json").read_text())
    cal = json.loads((ROOT / "results" / "calibration_d1.json").read_text())
    gate_ok = d1["d1_2"]["criterion_met"] and d1["d1_2"]["gamma_sr_exceeds_4"]
    if not gate_ok:
        print("D1.4 NOT RUN: gate requires D1.2 to pass with Gamma_SR > 4")
        OUT.write_text(json.dumps({"gate": "D1.4", "run": False,
                                   "reason": "gate not met"}, indent=2) + "\n")
        return
    A = cal["sr"]["threshold"]
    print(f"D1.4  gate met (Gamma_SR lower bound "
          f"{d1['d1_2']['lower_bound_normal']:.3f} > 4).  A = {A:.6f}", flush=True)

    sr = scan(SR, A, 0)
    cu = scan(CUSUM, 5.0, 1)

    stage_b = [1.028724, 1.044724]
    # the whole reported interval must sit inside the enclosure, not just the point
    cu_in_b = (cu["root"] is not None
               and stage_b[0] <= cu["root_interval"][0]
               and cu["root_interval"][1] <= stage_b[1])

    out = {
        "gate": "D1.4", "run": True,
        "protocol_sha256":
            "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e",
        "precommit_sha256":
            "7b7a54c64f4c86334415a03cd45797e7cb8b923d378fa90180a71f1831588dea",
        "n_cycles_per_point": N_POINT, "e_scan": E_SCAN, "seed_family": SEED,
        "sr": sr, "cusum": cu,
        "cusum_vs_stage_b": {
            "stage_b_certified_interval": stage_b,
            "cusum_mc_root": cu["root"],
            "cusum_mc_root_interval": cu["root_interval"],
            "whole_interval_inside_certified_interval": bool(cu_in_b),
            "note": ("A Monte Carlo root landing inside the Stage B enclosure "
                     "is a consistency check on this simulator. It adds nothing "
                     "to the certificate and does not extend it to SR."),
        },
        "evidence_status": "CANDIDATE",
        "forbidden_wordings_note": (
            "This is a Monte Carlo candidate. It is NOT certified, NOT proved, "
            "and agreement between CUSUM and SR is two-detector replication, "
            "NOT detector-independence."),
        "git_head": _git(), "python": platform.python_version(),
        "numpy": np.__version__, "elapsed_s": round(time.time() - t0, 1),
    }
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  SR    : {sr['verdict']}"
          + (f"  e* = {sr['root']:.6f} +/- {sr['root_half_width']:.6f}"
             if sr["root"] else ""), flush=True)
    print(f"  CUSUM : {cu['verdict']}"
          + (f"  e* = {cu['root']:.6f} +/- {cu['root_half_width']:.6f}"
             if cu["root"] else ""), flush=True)
    print(f"  CUSUM root INTERVAL "
          f"[{cu['root_interval'][0]:.6f}, {cu['root_interval'][1]:.6f}] "
          f"inside Stage B enclosure {stage_b}: {cu_in_b}", flush=True)
    print(f"  -> {OUT}   ({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
