"""Persist the fixed-path SR scalar-oracle and raw-replay convention audit."""

from __future__ import annotations

import json
import math
from pathlib import Path

from rebaseguard_phase4b.sr_model import run_sr_path
from rebaseguard_phase4b.sr_pathwise import replay_sr_raw


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "proofs" / "phase4b" / "pathwise_replay.json"


def main() -> None:
    threshold = 25.0
    paths = [
        [0.1, -0.2, 0.3, 5.0],
        [-0.1, 0.2, -0.3, -5.0],
        [1.0, -1.5, 0.2, -0.4, 6.0],
    ]
    cases: list[dict[str, object]] = []
    for innovations in paths:
        oracle = run_sr_path(innovations, threshold=threshold)
        raw = replay_sr_raw(innovations, threshold=threshold)
        raw_terminal = raw[-1]
        row_matches = [
            math.isclose(math.expm1(log_row.state.log1p_plus), raw_row.post_plus)
            and math.isclose(math.expm1(log_row.state.log1p_minus), raw_row.post_minus)
            and math.isclose(log_row.t_sum, raw_row.t_sum)
            and log_row.alarm.value == raw_row.alarm
            for log_row, raw_row in zip(oracle.trace, raw, strict=True)
        ]
        cases.append(
            {
                "innovations": innovations,
                "tau": oracle.tau,
                "z_tau": oracle.z_tau,
                "t_tau": oracle.t_tau,
                "terminal_reward": oracle.terminal_reward,
                "alarm": oracle.alarm.name,
                "raw_terminal_reward": raw_terminal.terminal_reward,
                "all_rows_match": all(row_matches),
            }
        )
    reflected = run_sr_path([-z for z in paths[0]], threshold=threshold)
    boundary_cases = []
    for epsilon in (-1e-9, 0.0, 1e-9):
        z = math.log(10.0) + 0.5 + epsilon
        result = run_sr_path([z, 20.0], threshold=10.0)
        raw_result = replay_sr_raw([z, 20.0], threshold=10.0)
        boundary_cases.append(
            {
                "epsilon": epsilon,
                "first_step_alarm": result.tau == 1,
                "tau": result.tau,
                "raw_tau": raw_result[-1].time,
                "oracle_raw_match": result.tau == raw_result[-1].time,
            }
        )
    tie_oracle = run_sr_path([0.0], threshold=0.5)
    tie_raw = replay_sr_raw([0.0], threshold=0.5)
    payload = {
        "schema": "rebaseguard.phase4b.pathwise-replay.v1",
        "proof_role": "NON-RIGOROUS CONVENTION VALIDATION ONLY",
        "delta": 1.0,
        "threshold": threshold,
        "cases": cases,
        "reflection_check": {
            "source_case": 0,
            "reflected_tau": reflected.tau,
            "reflected_alarm": reflected.alarm.name,
            "reward_preserved": math.isclose(
                reflected.terminal_reward, float(cases[0]["terminal_reward"])
            ),
        },
        "simultaneous_tie_check": {
            "oracle_alarm": tie_oracle.alarm.name,
            "raw_alarm": tie_raw[-1].alarm,
            "reward": tie_oracle.terminal_reward,
            "match": tie_oracle.alarm.name == "TIE" and tie_raw[-1].alarm == 2,
        },
        "inclusive_boundary_cases": boundary_cases,
        "all_checks_pass": all(case["all_rows_match"] for case in cases)
        and all(
            case["first_step_alarm"] == (case["epsilon"] >= 0.0)
            and case["oracle_raw_match"]
            for case in boundary_cases
        )
        and tie_oracle.alarm.name == "TIE"
        and tie_raw[-1].alarm == 2,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
