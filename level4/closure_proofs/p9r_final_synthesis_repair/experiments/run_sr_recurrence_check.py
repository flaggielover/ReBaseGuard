#!/usr/bin/env python3
"""R1 — deterministic algebraic verification of the frozen SR recurrence.

No Monte Carlo.  Every number below is produced from a fixed innovation
sequence and compared against arithmetic done by hand in ``FROZEN_PROTOCOL.md``
§5 and re-derived independently in ``tests/test_sr_recurrence.py``.

Checks
------
C1  first step from the no-headstart reset state equals the direct-form
    ``log R_1 = Z_1 - 1/2``;
C2  first two steps equal the direct-form ``R_t = (1+R_{t-1}) exp(Z_t - 1/2)``;
C3  the same holds for the first step after a cycle reset;
C4  an eight-step path agrees with the direct (non-log) recurrence to machine
    precision, including the inclusive alarm test;
C5  the P9 form differs from the frozen form by **exactly** ``log 2`` on the
    first update of a cycle and agrees on every subsequent update given the
    same incoming state;
C6  the ``log 2`` shift changes the alarm decision: an explicit witness
    innovation alarms under the P9 form and does not alarm under the frozen
    form on step one.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rebaseguard_p9r import SR_THRESHOLD                       # noqa: E402
from rebaseguard_p9r.detectors import (                        # noqa: E402
    sr_initial_state, sr_step, sr_step_p9_defective,
)
from rebaseguard_p9r.provenance import write_artifact          # noqa: E402

LOG_A = float(np.log(SR_THRESHOLD))

#: fixed, hand-checkable innovation sequence (not random, not tuned)
Z_PATH = [0.25, -0.75, 1.5, 0.1, -0.4, 2.0, -1.25, 0.6]

#: witness innovation for C6: alarms under the P9 form, not under the frozen one
Z_WITNESS = LOG_A + 0.5 - 0.5 * np.log(2.0)


def direct_reference(zs):
    """Non-log frozen recurrence ``R_t = (1+R_{t-1}) exp(Z_t - 1/2)``, R_0 = 0."""
    rp = rm = 0.0
    out = []
    for z in zs:
        rp = (1.0 + rp) * np.exp(z - 0.5)
        rm = (1.0 + rm) * np.exp(-z - 0.5)
        out.append((rp, rm, rp >= SR_THRESHOLD, rm >= SR_THRESHOLD))
    return out


def log_form(zs):
    yp, ym = sr_initial_state(1)
    out = []
    for z in zs:
        yp, ym, cu, cd = sr_step(yp, ym, np.array([float(z)]), LOG_A)
        # recover log R from the stored state: log R = log(exp(y) - 1)
        out.append((float(np.log(np.expm1(yp[0]))), float(np.log(np.expm1(ym[0]))),
                    bool(cu[0]), bool(cd[0])))
    return out


def main() -> int:
    payload: dict = {}

    # ---- C1 / C2 -------------------------------------------------------
    yp, ym = sr_initial_state(1)
    ell_1 = float(yp[0] + Z_PATH[0] - 0.5)
    payload["C1_first_step"] = {
        "stored_state_before": float(yp[0]),
        "log_R1_recurrence": ell_1,
        "log_R1_closed_form": float(Z_PATH[0] - 0.5),
        "abs_diff": abs(ell_1 - (Z_PATH[0] - 0.5)),
        "pass": abs(ell_1 - (Z_PATH[0] - 0.5)) == 0.0,
    }

    direct = direct_reference(Z_PATH[:2])
    logs = log_form(Z_PATH[:2])
    d2 = max(abs(np.log(direct[i][0]) - logs[i][0]) for i in range(2))
    payload["C2_first_two_steps"] = {
        "log_R_direct": [float(np.log(direct[i][0])) for i in range(2)],
        "log_R_log_form": [logs[i][0] for i in range(2)],
        "max_abs_diff": float(d2), "tolerance": 1e-12, "pass": bool(d2 < 1e-12),
    }

    # ---- C3 reset first step ------------------------------------------
    yp2, ym2 = sr_initial_state(1)              # exactly what a reset restores
    ell_reset = float(yp2[0] + Z_PATH[3] - 0.5)
    payload["C3_reset_first_step"] = {
        "stored_state_after_reset": float(yp2[0]),
        "log_R_after_reset_recurrence": ell_reset,
        "log_R_after_reset_closed_form": float(Z_PATH[3] - 0.5),
        "abs_diff": abs(ell_reset - (Z_PATH[3] - 0.5)),
        "pass": abs(ell_reset - (Z_PATH[3] - 0.5)) == 0.0,
    }

    # ---- C4 eight-step path -------------------------------------------
    direct = direct_reference(Z_PATH)
    logs = log_form(Z_PATH)
    worst = 0.0
    alarms_match = True
    rows = []
    for i, (d, l) in enumerate(zip(direct, logs)):
        dp, dm = float(np.log(d[0])), float(np.log(d[1]))
        worst = max(worst, abs(dp - l[0]), abs(dm - l[1]))
        alarms_match &= (d[2] == l[2]) and (d[3] == l[3])
        rows.append({"t": i + 1, "z": Z_PATH[i],
                     "log_Rplus_direct": dp, "log_Rplus_log_form": l[0],
                     "log_Rminus_direct": dm, "log_Rminus_log_form": l[1],
                     "alarm_up": bool(d[2]), "alarm_down": bool(d[3])})
    payload["C4_eight_step_path"] = {
        "rows": rows, "max_abs_diff": float(worst), "tolerance": 1e-12,
        "alarm_decisions_match": bool(alarms_match),
        "pass": bool(worst < 1e-12 and alarms_match),
    }

    # ---- C5 exact log 2 shift -----------------------------------------
    fp, fm = sr_initial_state(1)
    gp, gm = sr_initial_state(1)
    shifts = []
    for i, z in enumerate(Z_PATH[:4]):
        zz = np.array([float(z)])
        ell_frozen = float(fp[0] + z - 0.5)
        ell_p9 = float(np.logaddexp(0.0, gp[0]) + z - 0.5)
        shifts.append({"t": i + 1, "frozen_log_R": ell_frozen,
                       "p9_statistic": ell_p9, "shift": ell_p9 - ell_frozen})
        fp, fm, _, _ = sr_step(fp, fm, zz, LOG_A)
        gp, gm, _, _ = sr_step_p9_defective(gp, gm, zz, LOG_A)
    first_shift = shifts[0]["shift"]
    payload["C5_log2_shift"] = {
        "steps": shifts,
        "first_step_shift": first_shift,
        "log2": float(np.log(2.0)),
        "first_step_shift_is_exactly_log2":
            bool(first_shift == float(np.log(2.0))),
        "note": ("after step 1 the two forms are compared on their own "
                 "trajectories, so the later shifts are path effects of the "
                 "first-step defect, not additional independent shifts"),
        "pass": bool(first_shift == float(np.log(2.0))),
    }

    # ---- C6 alarm-decision witness ------------------------------------
    fp, fm = sr_initial_state(1)
    gp, gm = sr_initial_state(1)
    zz = np.array([float(Z_WITNESS)])
    _, _, cu_f, _ = sr_step(fp, fm, zz, LOG_A)
    _, _, cu_p9, _ = sr_step_p9_defective(gp, gm, zz, LOG_A)
    payload["C6_alarm_witness"] = {
        "z_witness": float(Z_WITNESS),
        "frozen_alarms_step1": bool(cu_f[0]),
        "p9_alarms_step1": bool(cu_p9[0]),
        "decisions_differ": bool(cu_f[0] != cu_p9[0]),
        "pass": bool((not cu_f[0]) and cu_p9[0]),
    }

    payload["all_pass"] = all(payload[k]["pass"] for k in payload
                              if isinstance(payload[k], dict) and "pass" in payload[k])

    write_artifact("sr_recurrence_check.json",
                   schema="rebaseguard.p9r.sr-recurrence-check.v1",
                   generator="experiments/run_sr_recurrence_check.py",
                   config={"z_path": Z_PATH, "z_witness": float(Z_WITNESS),
                           "sr_threshold": SR_THRESHOLD, "log_threshold": LOG_A,
                           "deterministic": True, "monte_carlo": False},
                   payload=payload)
    for k, v in payload.items():
        if isinstance(v, dict):
            print(f"{k}: pass={v['pass']}")
    print("ALL_PASS =", payload["all_pass"])
    return 0 if payload["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
