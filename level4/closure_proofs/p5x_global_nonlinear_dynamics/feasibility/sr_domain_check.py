"""Evidence for DEFECT_REGISTER.md D1: the frozen SR pre-alarm state square.

NON-AUTHORITATIVE.  A falsification probe, not a certificate: it exhibits live
SR states above the frozen bound `b_SR = log A`.  A single such state falsifies
the frozen domain claim; no amount of simulation could confirm it, which is why
the *proof* of the correct bound `log(1+A)` is in PROOF.md L1.3 and this file
only supplies the witness.
"""
from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
A = 520.886133602749


def main(n_paths: int = 400_000, seed: int = 20260902, max_steps: int = 4000) -> None:
    log_a = float(np.log(A))
    log_1a = float(np.log(1.0 + A))
    rng = np.random.default_rng(seed)
    yp = np.zeros(n_paths)
    ym = np.zeros(n_paths)
    alive = np.ones(n_paths, dtype=bool)
    max_live = 0.0
    n_above = 0
    for _ in range(max_steps):
        idx = np.flatnonzero(alive)
        if idx.size == 0:
            break
        z = rng.standard_normal(idx.size)
        lp = yp[idx] + z - 0.5
        lm = ym[idx] - z - 0.5
        crossed = (lp >= log_a) | (lm >= log_a)
        new_p = np.logaddexp(0.0, lp)
        new_m = np.logaddexp(0.0, lm)
        live = ~crossed
        if live.any():
            max_live = max(max_live, float(new_p[live].max()), float(new_m[live].max()))
            n_above += int(((new_p[live] >= log_a) | (new_m[live] >= log_a)).sum())
        yp[idx] = new_p
        ym[idx] = new_m
        alive[idx[crossed]] = False
    payload = {
        "status": "FEASIBILITY_PROBE_NON_AUTHORITATIVE",
        "not_a_certificate": True,
        "purpose": "witness for DEFECT_REGISTER.md D1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip(),
        "python": platform.python_version(),
        "seed": seed,
        "n_paths": n_paths,
        "sr_threshold_A": A,
        "log_A_frozen_b_SR": log_a,
        "log_1_plus_A_corrected_b_SR": log_1a,
        "max_live_stored_state": max_live,
        "live_states_at_or_above_log_A": n_above,
        "frozen_b_SR_falsified": bool(max_live >= log_a),
        "within_corrected_b_SR": bool(max_live < log_1a),
    }
    out = HERE / "results" / "sr_domain_check.json"
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(json.dumps(payload, indent=1))


if __name__ == "__main__":
    main()
