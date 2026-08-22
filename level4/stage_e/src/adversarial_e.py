"""Stage E adversarial suite (protocol S14). All 14 checks, reported pass or
fail. Failures stay visible; tolerances are never widened after a result is
seen."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drift import inject, injection_grid                     # noqa: E402
from loaders import LOADERS                                  # noqa: E402
from monitor import run_monitor                              # noqa: E402
from residuals import build_stream                           # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
PROTO_SHA = "974487019f57c7c319b3bfafcdc20497ab6fca86834ad0d2245a694296ef23cc"
TASKS = {"electricity": 120, "air_quality": 24, "bike_sharing": 46}
FILES = {t: f"task_{t}_confirmatory.json" for t in TASKS}
SEED_RERUN = 20261103
PRIOR_SEEDS = {1234, 1729, 2024, 2026, 4242, 5150, 8080, 31337, 90210,
               20260820, 20260821, 20260822, 20260901, 20260902, 20260931,
               20261001, 20261002, 20261031}
RHO_P2 = 0.029796


def load(n):
    return json.loads((RES / n).read_text())


def _delays(r, scale, h, rho, r0, grid, ev_lo, ev_hi, warmup,
            cond="STEP", mag=1.0):
    out = []
    for t0 in grid:
        inj = inject(r, scale=scale, t0=int(t0), condition=cond, magnitude=mag)
        run = run_monitor(inj, scale=scale, threshold=h, rho=rho, r0=r0,
                          start=max(ev_lo, int(t0) - warmup), stop=ev_hi)
        hit = next((c.alarm for c in run.cycles if c.alarm >= t0), None)
        if hit is not None:
            out.append(float(hit - t0))
    return np.array(out)


def _n_se(a, b):
    if a.size < 2 or b.size < 2:
        return float("nan")
    se = float(np.hypot(a.std(ddof=1) / np.sqrt(a.size),
                        b.std(ddof=1) / np.sqrt(b.size)))
    return abs(a.mean() - b.mean()) / se if se > 0 else 0.0


def main():
    t0 = time.time()
    checks = []

    def add(cid, name, ok, detail):
        checks.append({"id": cid, "check": name, "passed": bool(ok), **detail})
        print(f"  [{cid:>3}] {'PASS' if ok else 'FAIL'}  {name}", flush=True)

    # ---- A1 protocol hash -------------------------------------------------
    actual = hashlib.sha256((ROOT / "STAGE_E_PROTOCOL.md").read_bytes()).hexdigest()
    add("A1", "Stage E protocol hash unchanged", actual == PROTO_SHA,
        {"expected": PROTO_SHA, "actual": actual})

    # ---- A2 seed / split integrity ---------------------------------------
    seeds = set(load("protocol_hash.json")["seeds"].values())
    ok, det = True, {}
    for t in TASKS:
        d = load(FILES[t])
        s = d["split"]
        c = (s["train"][0] == 0 and s["train"][1] == s["calib"][0]
             and s["calib"][1] == s["eval"][0] and s["eval"][1] == d["n_total"])
        det[t] = {"split": s, "contiguous_and_complete": c}
        ok &= c
    add("A2", "Stage E seeds disjoint from prior work; splits contiguous",
        ok and seeds.isdisjoint(PRIOR_SEEDS),
        {"stage_e_seeds": sorted(seeds), "overlap_with_prior": sorted(seeds & PRIOR_SEEDS),
         "per_task": det})

    # ---- A3 no future-data leakage ---------------------------------------
    leak, det = False, {}
    for t in TASKS:
        d = load(FILES[t])
        s, cb, g = d["split"], d["calibration"]["calibration_block"], d["injection_grid"]
        bad = not (cb[0] >= s["calib"][0] and cb[1] <= s["calib"][1]
                   and min(g) >= s["eval"][0] and max(g) < s["eval"][1])
        det[t] = {"calibration_block": cb, "eval": s["eval"],
                  "grid_range": [min(g), max(g)], "leak": bad}
        leak |= bad
    add("A3", "model, scale and threshold use no evaluation or future data",
        not leak, {"per_task": det})

    # ---- A4 fresh-control sanity -----------------------------------------
    ok, det = True, {}
    for t in TASKS:
        d = load(FILES[t])
        cl = np.array(d["in_control"]["P0_fresh"]["tau0_cycle_lengths"])
        good = d["policies"]["P0_fresh"] == 0.0 and cl.size > 0 and bool((cl > 0).all())
        det[t] = {"rho": d["policies"]["P0_fresh"], "n_cycles": int(cl.size),
                  "mean_cycle": float(cl.mean()) if cl.size else None, "ok": good}
        ok &= good
    add("A4", "fresh control has rho = 0 and well-formed positive cycles", ok,
        {"per_task": det})

    # ---- A5 calibration sanity -------------------------------------------
    ok, det = True, {}
    for t in TASKS:
        c = load(FILES[t])["calibration"]
        good = (abs(c["relative_error"]) <= 0.05
                and c["policy_used"] == "fresh (rho = 0)")
        det[t] = {"h": c["threshold_h"], "achieved_arl0": c["achieved_arl0"],
                  "ci": c["arl0_ci"], "relative_error": c["relative_error"],
                  "policy_used": c["policy_used"], "within_5pct": good}
        ok &= good
    add("A5", "calibration on calibration block only, fresh policy, within 5% "
              "of the frozen target", ok, {"per_task": det})

    # ---- A6 full-reuse reproduction under an independent grid seed --------
    ok, det = True, {}
    for t in TASKS:
        d = load(FILES[t])
        ms = build_stream(LOADERS[t]())
        lo, hi = ms.split.eval.start, ms.split.eval.stop
        g2 = injection_grid(hi - lo, lo, TASKS[t], SEED_RERUN)
        rerun = _delays(ms.residual, ms.scale, d["threshold_h"], 1.0,
                        d["r0_initial_reference"], g2, lo, hi,
                        d["warmup_before_onset"])
        orig = np.array(d["drift"]["STEP_1.0"]["P1_full_reuse"]["delays"])
        dev = _n_se(rerun, orig)
        det[t] = {"rerun_seed": SEED_RERUN, "mean_rerun": float(rerun.mean()),
                  "mean_original": float(orig.mean()), "n_se": float(dev)}
        ok &= dev < 3.0
    add("A6", "full reuse reproduces on an independent injection-grid seed",
        ok, {"tolerance": "< 3 pooled SE", "per_task": det})

    # ---- A7 ReBaseGuard policy outcome-blind ------------------------------
    outcomes = []
    for t in TASKS:
        d = load(FILES[t])
        outcomes.append(f"{d['threshold_h']:.4g}")
        outcomes.append(
            f"{d['in_control']['P2_rebaseguard']['E2_reference_error']['mean']:.4g}")
    outcomes = sorted(set(outcomes))
    hits = []
    for f in sorted((ROOT / "src").glob("*.py")):
        if f.name == "adversarial_e.py":
            continue
        code = re.sub(r'""".*?"""', "", f.read_text(), flags=re.S)
        code = re.sub(r"#.*", "", code)
        for v in outcomes:
            if v in code:
                hits.append({"file": f.name, "value": v})
    src = (ROOT / "src" / "run_task.py").read_text()
    frozen = str(RHO_P2) in src
    add("A7", "P2 rho is the frozen Stage C constant; no measured outcome is "
              "hard-coded in executable source", frozen and not hits,
        {"rho_p2": RHO_P2, "rho_is_frozen_stage_c_constant": frozen,
         "values_scanned": outcomes, "hits": hits})

    # ---- A8 matched-stream comparison -------------------------------------
    ok, det = True, {}
    for t in TASKS:
        d = load(FILES[t])
        rhos = sorted(set(d["policies"].values()))
        good = len(rhos) == 4 and len(d["injection_grid"]) == TASKS[t]
        det[t] = {"shared_threshold": d["threshold_h"],
                  "shared_scale": d["residual_scale_reference_block"],
                  "shared_m": d["m_window"], "shared_model": d["model_kind"],
                  "n_grid_points": len(d["injection_grid"]),
                  "distinct_rhos": rhos, "only_rho_differs": good}
        ok &= good
    add("A8", "policies differ ONLY in rho; stream, model, scale, threshold, "
              "grid and m are shared", ok, {"per_task": det})

    # ---- A9 replicate-count sensitivity ------------------------------------
    ok, det = True, {}
    for t in TASKS:
        full = np.array(load(FILES[t])["drift"]["STEP_1.0"]["P2_rebaseguard"]["delays"])
        half = full[::2]
        dev = _n_se(full, half)
        det[t] = {"n_full": int(full.size), "n_half": int(half.size),
                  "mean_full": float(full.mean()), "mean_half": float(half.mean()),
                  "n_se": float(dev)}
        ok &= dev < 3.0
    add("A9", "halving the event count moves E4 by less than 3 SE", ok,
        {"per_task": det})

    # ---- A10 warm-up sensitivity -------------------------------------------
    ok, det = True, {}
    for t in TASKS:
        d = load(FILES[t])
        ms = build_stream(LOADERS[t]())
        lo, hi = ms.split.eval.start, ms.split.eval.stop
        g = np.array(d["injection_grid"])
        base = np.array(d["drift"]["STEP_1.0"]["P2_rebaseguard"]["delays"])
        alt = _delays(ms.residual, ms.scale, d["threshold_h"], RHO_P2,
                      d["r0_initial_reference"], g, lo, hi, 400)
        dev = _n_se(base, alt)
        det[t] = {"warmup_frozen": d["warmup_before_onset"], "warmup_alt": 400,
                  "mean_frozen": float(base.mean()), "mean_alt": float(alt.mean()),
                  "n_se": float(dev)}
        ok &= dev < 3.0
    add("A10", "halving the warm-up moves E4 by less than 3 SE", ok,
        {"per_task": det})

    # ---- A11 drift-location sensitivity ------------------------------------
    ok, det = True, {}
    for t in TASKS:
        d = np.array(load(FILES[t])["drift"]["STEP_1.0"]["P2_rebaseguard"]["delays"])
        a, b = d[:d.size // 2], d[d.size // 2:]
        dev = _n_se(a, b)
        det[t] = {"first_half_mean": float(a.mean()),
                  "second_half_mean": float(b.mean()), "n_se": float(dev)}
        ok &= dev < 3.0
    add("A11", "early vs late injection locations agree within 3 SE", ok,
        {"per_task": det,
         "note": "a failure here indicates natural nonstationarity dominating "
                 "the injected effect, not an implementation bug"})

    # ---- A12 alternative valid residual scaling ----------------------------
    ok, det = True, {}
    for t in TASKS:
        ms = build_stream(LOADERS[t]())
        rr = ms.residual[ms.split.train]
        mad = float(np.median(np.abs(rr - np.median(rr))) * 1.4826)
        ratio = mad / ms.scale
        det[t] = {"frozen_sd_scale": ms.scale, "robust_mad_scale": mad,
                  "ratio": ratio}
        ok &= 0.5 < ratio < 2.0
    add("A12", "robust MAD scale is within 2x of the frozen SD scale", ok,
        {"per_task": det,
         "note": "checks that conclusions do not hinge on a fragile scale choice; "
                 "the frozen scale remains the reference-block SD"})

    # ---- A13 loader reproducibility ----------------------------------------
    ok, det = True, {}
    man = load("data_manifest.json")["_streams"]
    for t in TASKS:
        s1, s2 = LOADERS[t](), LOADERS[t]()
        same = (np.array_equal(s1.X, s2.X) and np.array_equal(s1.y, s2.y)
                and s1.source_sha256 == s2.source_sha256)
        rec = man[t]["source_sha256"] == s1.source_sha256
        det[t] = {"deterministic": bool(same),
                  "checksum_matches_manifest": bool(rec),
                  "sha256": s1.source_sha256, "n": int(s1.X.shape[0])}
        ok &= same and rec
    add("A13", "loaders are deterministic and match the recorded checksums", ok,
        {"per_task": det})

    # ---- A14 figures regenerate from machine-readable results only ---------
    figs = sorted((ROOT / "figures").glob("*.png"))
    fsrc = (ROOT / "src" / "figures_e.py").read_text()
    reads_only_json = ("run_monitor" not in fsrc and "simulate" not in fsrc
                       and "LOADERS" not in fsrc)
    add("A14", "figures regenerate from results JSON only, with no re-simulation",
        len(figs) >= 4 and reads_only_json,
        {"n_figures": len(figs), "figures": [f.name for f in figs],
         "figure_source_reads_only_results_json": reads_only_json})

    n_pass = sum(c["passed"] for c in checks)
    out = {"suite": "Stage E adversarial", "n_checks": len(checks),
           "n_passed": n_pass, "n_failed": len(checks) - n_pass,
           "protocol_sha256": PROTO_SHA, "independent_rerun_seed": SEED_RERUN,
           "checks": checks, "elapsed_s": round(time.time() - t0, 1)}
    (RES / "adversarial.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  {n_pass}/{len(checks)} adversarial checks passed "
          f"({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
