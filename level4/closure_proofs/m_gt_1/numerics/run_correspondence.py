#!/usr/bin/env python3
"""Run the protocol-frozen independent derivative correspondence experiment."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_mgt1.analysis import (  # noqa: E402
    Moments, central_difference, inverse_variance_pool, richardson,
)
from rebaseguard_mgt1.model import (  # noqa: E402
    H_LADDER, M_GRID, PRIMARY_H, RHO_GRID, gamma_components,
)
from rebaseguard_mgt1.simulate import simulate_stopped_batch  # noqa: E402

MASTER_SEED = 2026082204
PROTOCOL_SHA256 = "27c3cddad3a09520a562b444e9635a3f4155464ac322f01edc79e0fc74c2d9af"
FULL = {
    "route_a_n": 1_000_000,
    "route_b_n": 500_000,
    "distinction_n": 200_000,
    "batch": 50_000,
    "replicates": 2,
}
QUICK = {
    "route_a_n": 4_000,
    "route_b_n": 2_000,
    "distinction_n": 2_000,
    "batch": 1_000,
    "replicates": 2,
}


def _git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                          text=True, capture_output=True, check=True).stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=_json_default) + "\n")


def _batches(n: int, batch: int):
    left = n
    b = 0
    while left:
        size = min(batch, left)
        yield b, size
        left -= size
        b += 1


def _seed(entropy: list[int]) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(entropy)))


def run_route_a(cfg: dict) -> list[dict]:
    out = []
    m_float = M_GRID.astype(float)
    for rep in range(cfg["replicates"]):
        a = Moments.zeros((M_GRID.size,))
        bmom = Moments.zeros((M_GRID.size,))
        c = Moments.zeros((M_GRID.size,))
        lag = Moments.zeros((int(M_GRID.max()),))
        short = np.zeros(M_GRID.size, dtype=np.int64)
        max_identity_error = 0.0
        seed_keys = []
        tau_sum = 0.0
        for bi, size in _batches(cfg["route_a_n"], cfg["batch"]):
            entropy = [MASTER_SEED, 1, rep, bi]
            batch = simulate_stopped_batch(
                e=0.0, n_paths=size, m_grid=M_GRID, rng=_seed(entropy)
            )
            va = batch.zbar * batch.t_tau[:, None]
            vb = batch.window_sum / m_float[None, :] * batch.t_tau[:, None]
            vc = np.where(
                batch.tau[:, None] < M_GRID[None, :],
                (1.0 / batch.tau[:, None] - 1.0 / m_float[None, :])
                * batch.t_tau[:, None] ** 2,
                0.0,
            )
            # Independently call the pure theorem definition as a code-path check.
            for j, m in enumerate(M_GRID):
                ca, cb, cc = gamma_components(
                    batch.tau, batch.t_tau, batch.window_sum[:, j], int(m)
                )
                max_identity_error = max(
                    max_identity_error,
                    float(np.max(np.abs(ca - cb - cc))),
                    float(np.max(np.abs(va[:, j] - vb[:, j] - vc[:, j]))),
                )
            a.add(va)
            bmom.add(vb)
            c.add(vc)
            lag.add(batch.lags_newest * batch.t_tau[:, None])
            short += (batch.tau[:, None] < M_GRID[None, :]).sum(axis=0)
            tau_sum += float(batch.tau.sum())
            seed_keys.append(entropy)
        out.append({
            "replicate": rep,
            "n_paths": a.n,
            "gamma_tilde": a.mean.tolist(),
            "gamma_tilde_se": a.se.tolist(),
            "predicted_derivative": (1.0 - a.mean).tolist(),
            "gamma_b": bmom.mean.tolist(),
            "gamma_b_se": bmom.se.tolist(),
            "short_correction": c.mean.tolist(),
            "short_correction_se": c.se.tolist(),
            "short_cycle_probability": (short / a.n).tolist(),
            "gamma_lag": lag.mean.tolist(),
            "mean_tau": tau_sum / a.n,
            "max_pathwise_decomposition_error": max_identity_error,
            "seed_keys": seed_keys,
        })
        print(f"  Route A replicate {rep + 1}/{cfg['replicates']} complete", flush=True)
    return out


def _map_moments(e: float, n_paths: int, batch_size: int, entropy_prefix: list[int]) -> Moments:
    moments = Moments.zeros((M_GRID.size,))
    for bi, size in _batches(n_paths, batch_size):
        entropy = [*entropy_prefix, bi]
        batch = simulate_stopped_batch(e=e, n_paths=size, m_grid=M_GRID, rng=_seed(entropy))
        moments.add(e + batch.zbar)
    return moments


def run_route_b(cfg: dict) -> list[dict]:
    out = []
    for rep in range(cfg["replicates"]):
        steps = {}
        for si, h in enumerate(H_LADDER):
            plus = _map_moments(
                float(h), cfg["route_b_n"], cfg["batch"],
                [MASTER_SEED, 2, rep, si, 1],
            )
            minus = _map_moments(
                -float(h), cfg["route_b_n"], cfg["batch"],
                [MASTER_SEED, 2, rep, si, 0],
            )
            derivative, derivative_se = central_difference(
                plus.mean, plus.se, minus.mean, minus.se, float(h)
            )
            steps[str(float(h))] = {
                "h": float(h),
                "F_plus": plus.mean.tolist(),
                "F_plus_se": plus.se.tolist(),
                "F_minus": minus.mean.tolist(),
                "F_minus_se": minus.se.tolist(),
                "derivative": derivative.tolist(),
                "derivative_se": derivative_se.tolist(),
                "plus_seed_prefix": [MASTER_SEED, 2, rep, si, 1],
                "minus_seed_prefix": [MASTER_SEED, 2, rep, si, 0],
            }
            print(f"  Route B replicate {rep + 1}, h={h:g} complete", flush=True)
        d_half = np.array(steps[str(PRIMARY_H)]["derivative"])
        s_half = np.array(steps[str(PRIMARY_H)]["derivative_se"])
        d_full = np.array(steps[str(2 * PRIMARY_H)]["derivative"])
        s_full = np.array(steps[str(2 * PRIMARY_H)]["derivative_se"])
        rv, rs = richardson(d_half, s_half, d_full, s_full)
        out.append({
            "replicate": rep,
            "n_paths_per_point": cfg["route_b_n"],
            "steps": steps,
            "richardson_secondary": rv.tolist(),
            "richardson_secondary_se": rs.tolist(),
        })
    return out


def run_distinction(cfg: dict) -> list[dict]:
    rows = []
    for rep in range(cfg["replicates"]):
        for m in (20, 100):
            moments = {"stage_a_min_dwell": Moments.zeros((1,)),
                       "stage_d_truncated": Moments.zeros((1,))}
            for bi, size in _batches(cfg["distinction_n"], cfg["batch"]):
                parent = np.random.SeedSequence([MASTER_SEED, 3, rep, bi])
                children = parent.spawn(2)
                for ci, (name, dwell) in enumerate((
                    ("stage_a_min_dwell", m), ("stage_d_truncated", None)
                )):
                    batch = simulate_stopped_batch(
                        e=0.1, n_paths=size, m_grid=np.array([m]),
                        rng=np.random.Generator(np.random.PCG64(children[ci])),
                        minimum_dwell=dwell,
                    )
                    moments[name].add((0.1 + batch.zbar[:, 0])[:, None])
            ma, md = moments["stage_a_min_dwell"], moments["stage_d_truncated"]
            diff = float(md.mean[0] - ma.mean[0])
            se = float(np.hypot(md.se[0], ma.se[0]))
            rows.append({
                "replicate": rep, "m": m, "e": 0.1,
                "stage_a_F": float(ma.mean[0]), "stage_a_se": float(ma.se[0]),
                "stage_d_F": float(md.mean[0]), "stage_d_se": float(md.se[0]),
                "difference_D_minus_A": diff, "combined_se": se,
                "abs_z": abs(diff) / se,
                "parent_seed_rule": [MASTER_SEED, 3, rep, "batch"],
                "convention_streams": "SeedSequence.spawn(2)",
            })
            print(f"  map distinction replicate {rep + 1}, m={m} complete", flush=True)
    return rows


def rho_scaling(route_b: list[dict], cfg: dict) -> dict:
    rows = []
    max_error = 0.0
    for rep in range(cfg["replicates"]):
        pm = route_b[rep]["steps"][str(PRIMARY_H)]
        fp = np.array(pm["F_plus"])
        fm = np.array(pm["F_minus"])
        d1 = np.array(pm["derivative"])
        fresh = Moments.zeros((M_GRID.size,))
        for bi, size in _batches(cfg["route_b_n"], cfg["batch"]):
            rng = _seed([MASTER_SEED, 4, rep, bi])
            draws = rng.standard_normal((size, M_GRID.size)) / np.sqrt(M_GRID)[None, :]
            fresh.add(draws)
        for rho in RHO_GRID:
            frp = rho * fp + (1.0 - rho) * fresh.mean
            frm = rho * fm + (1.0 - rho) * fresh.mean
            drho = (frp - frm) / (2.0 * PRIMARY_H)
            err = np.abs(drho - rho * d1)
            max_error = max(max_error, float(err.max()))
            rows.append({
                "replicate": rep, "rho": float(rho),
                "derivative": drho.tolist(),
                "rho_times_full_reuse": (rho * d1).tolist(),
                "max_abs_error": float(err.max()),
                "fresh_pairing": "identical fresh sample at +h and -h",
            })
    return {"rows": rows, "max_abs_error": max_error}


def evaluate(route_a: list[dict], route_b: list[dict], distinction: list[dict],
             rho: dict, quick: bool) -> dict:
    targets = np.array([r["predicted_derivative"] for r in route_a])
    target_ses = np.array([r["gamma_tilde_se"] for r in route_a])
    primary_d = np.array([
        r["steps"][str(PRIMARY_H)]["derivative"] for r in route_b
    ])
    primary_se = np.array([
        r["steps"][str(PRIMARY_H)]["derivative_se"] for r in route_b
    ])
    diff = primary_d - targets
    diff_se = np.hypot(primary_se, target_ses)
    rep_z = np.abs(diff) / diff_se
    pooled_diff, pooled_diff_se = inverse_variance_pool(diff, diff_se)
    pooled_z = np.abs(pooled_diff) / pooled_diff_se
    agreement_z = np.abs(primary_d[0] - primary_d[1]) / np.hypot(primary_se[0], primary_se[1])

    target_pool, target_pool_se = inverse_variance_pool(targets, target_ses)
    step_pooled = {}
    for h in H_LADDER:
        key = str(float(h))
        dv = np.array([r["steps"][key]["derivative"] for r in route_b])
        ds = np.array([r["steps"][key]["derivative_se"] for r in route_b])
        pv, ps = inverse_variance_pool(dv, ds)
        step_pooled[key] = {"derivative": pv.tolist(), "se": ps.tolist(),
                            "discrepancy": (pv - target_pool).tolist()}
    errors = [np.abs(np.array(step_pooled[str(float(h))]["discrepancy"])) for h in H_LADDER]
    shrink_100_050 = int(np.count_nonzero(errors[1] < errors[0]))
    shrink_050_025 = int(np.count_nonzero(errors[2] < errors[1]))
    orders = np.log2(np.maximum(errors[0], 1e-300) / np.maximum(errors[1], 1e-300))
    median_order = float(np.median(orders))

    hist = json.loads((REPO / "level4/stage_d/results/d2_gamma_m.json").read_text())
    hist_gamma = float(hist["rows"][0]["A"]["gamma_m"])
    hist_se = float(hist["rows"][0]["A"]["se"])
    gamma_values = np.array([r["gamma_tilde"] for r in route_a])
    gamma_ses = np.array([r["gamma_tilde_se"] for r in route_a])
    gamma_pool, gamma_pool_se = inverse_variance_pool(gamma_values, gamma_ses)
    hist_z = abs(gamma_pool[0] - hist_gamma) / np.hypot(gamma_pool_se[0], hist_se)

    checks = {
        "primary_pooled_all_within_3se": bool(np.all(pooled_z <= 3.0)),
        "primary_each_rep_all_within_4se": bool(np.all(rep_z <= 4.0)),
        "independent_derivatives_all_within_4se": bool(np.all(agreement_z <= 4.0)),
        "coarse_shrink_0.1_to_0.05_at_least_7": shrink_100_050 >= 7,
        "coarse_shrink_0.05_to_0.025_at_least_6": shrink_050_025 >= 6,
        "coarse_median_order_in_1.25_2.75": 1.25 <= median_order <= 2.75,
        "short_decomposition_roundoff": max(
            r["max_pathwise_decomposition_error"] for r in route_a) <= 1e-9,
        "short_cycles_observed_for_every_m_gt_1": bool(np.all(
            np.array([r["short_cycle_probability"] for r in route_a])[:, 1:] > 0
        )),
        "rho_scaling_roundoff": rho["max_abs_error"] <= 1e-12,
        "stage_a_stage_d_distinct_over_5se": all(r["abs_z"] > 5.0 for r in distinction),
        "m1_new_gamma_agrees_historical_within_4se": bool(hist_z <= 4.0),
    }
    # Quick mode validates plumbing, not frozen scientific thresholds.
    decision = "SMOKE-ONLY" if quick else ("PASS" if all(checks.values()) else "FAIL")
    return {
        "decision": decision,
        "checks": checks,
        "pooled_primary_discrepancy": pooled_diff.tolist(),
        "pooled_primary_combined_se": pooled_diff_se.tolist(),
        "pooled_primary_abs_z": pooled_z.tolist(),
        "replicate_primary_abs_z": rep_z.tolist(),
        "replicate_derivative_agreement_abs_z": agreement_z.tolist(),
        "step_pooled": step_pooled,
        "shrink_counts": {"0.1_to_0.05": shrink_100_050, "0.05_to_0.025": shrink_050_025},
        "coarse_orders_0.1_to_0.05": orders.tolist(),
        "median_coarse_order": median_order,
        "historical_m1_control": {
            "historical_gamma": hist_gamma, "historical_se": hist_se,
            "new_pooled_gamma": float(gamma_pool[0]),
            "new_pooled_se": float(gamma_pool_se[0]), "abs_z": float(hist_z),
        },
    }


def write_csv(path: Path, route_a: list[dict], route_b: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        fields = ["replicate", "m", "h", "gamma_tilde", "gamma_se",
                  "target", "F_plus", "F_plus_se", "F_minus", "F_minus_se",
                  "derivative", "derivative_se", "discrepancy", "combined_se"]
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for rep, (ra, rb) in enumerate(zip(route_a, route_b)):
            for h in H_LADDER:
                step = rb["steps"][str(float(h))]
                for j, m in enumerate(M_GRID):
                    target = ra["predicted_derivative"][j]
                    disc = step["derivative"][j] - target
                    comb = float(np.hypot(step["derivative_se"][j], ra["gamma_tilde_se"][j]))
                    writer.writerow({
                        "replicate": rep, "m": int(m), "h": float(h),
                        "gamma_tilde": ra["gamma_tilde"][j], "gamma_se": ra["gamma_tilde_se"][j],
                        "target": target, "F_plus": step["F_plus"][j],
                        "F_plus_se": step["F_plus_se"][j], "F_minus": step["F_minus"][j],
                        "F_minus_se": step["F_minus_se"][j], "derivative": step["derivative"][j],
                        "derivative_se": step["derivative_se"][j], "discrepancy": disc,
                        "combined_se": comb,
                    })


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="small plumbing run; no scientific verdict")
    parser.add_argument("--resume", action="store_true", help="reuse completed deterministic phase checkpoints")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cfg = dict(QUICK if args.quick else FULL)
    output = args.output or (CAMPAIGN / "results" / ("correspondence_smoke.json" if args.quick else "correspondence.json"))
    actual_hash = _sha256(CAMPAIGN / "PROTOCOL.md")
    if actual_hash != PROTOCOL_SHA256:
        raise RuntimeError(f"protocol hash mismatch: {actual_hash}")
    checkpoint_tag = "smoke" if args.quick else "full"

    def phase(name, function):
        checkpoint = CAMPAIGN / "results" / f"checkpoint_{checkpoint_tag}_{name}.json"
        if args.resume and checkpoint.exists():
            print(f"resuming {name} from {checkpoint.name}", flush=True)
            return json.loads(checkpoint.read_text())
        value = function(cfg)
        _write_json(checkpoint, value)
        return value

    print("Route A: stopped-score theorem prediction", flush=True)
    route_a = phase("route_a", run_route_a)
    print("Route B: direct induced-map central differences", flush=True)
    route_b = phase("route_b", run_route_b)
    print("Stage-A versus Stage-D distinction control", flush=True)
    distinction = phase("distinction", run_distinction)
    rho = rho_scaling(route_b, cfg)
    verdict = evaluate(route_a, route_b, distinction, rho, args.quick)
    payload = {
        "campaign": "ReBaseGuard m>1 derivative closure proof",
        "evidence": "SMOKE" if args.quick else "NEW-CONFIRMATORY-NUMERICAL",
        "protocol_sha256": actual_hash,
        "historical_d2_3": "FAILED",
        "config": cfg,
        "master_seed": MASTER_SEED,
        "m_grid": M_GRID.tolist(),
        "rho_grid": RHO_GRID.tolist(),
        "h_ladder": H_LADDER.tolist(),
        "primary_h": PRIMARY_H,
        "common_random_numbers_primary": False,
        "route_a": route_a,
        "route_b": route_b,
        "rho_scaling": rho,
        "stage_a_stage_d_distinction": distinction,
        "verdict": verdict,
        "richardson_status": "SECONDARY DIAGNOSTIC ONLY",
        "git_head": _git_head(),
        "python": platform.python_version(),
        "numpy": np.__version__,
    }
    _write_json(output, payload)
    csv_path = output.with_suffix(".csv")
    write_csv(csv_path, route_a, route_b)
    print(json.dumps({"decision": verdict["decision"], "checks": verdict["checks"]}, indent=2))
    print(f"wrote {output}")
    print(f"wrote {csv_path}")
    if not args.quick and verdict["decision"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
