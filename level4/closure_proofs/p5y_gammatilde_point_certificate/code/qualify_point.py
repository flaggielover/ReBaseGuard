"""Qualification verdict for the point evaluator (stdlib only; no kernel arithmetic).

    python3 -B code/qualify_point.py --replay R --point-e0 P --unit-tests-passed --out V

PASS requires, all frozen in protocol/POINT_PROTOCOL.json before any run:

  Q1 unit tests (qualification/test_point_core.py) passed
  Q2 replay-cell0: the evaluator reproduces the committed K1 CUSUM cell-0 record R_interval and D_interval for every
     m EXACTLY (same exact rational endpoints) -- the wrapper computes the K1 object, not a look-alike
  Q3 point-e0: the degenerate cell {e0} gives, for every m, R and D enclosures CONTAINED in the record's (same
     candidates and centre, point norms can only tighten), and a nonempty interval
  Q4 both runs: bound to the frozen protocol hash, both gates recorded, identity == frozen K1 identity, SciPy clean
  Q5 CPU within the frozen qualification ceiling
"""
from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import point_core as PC  # noqa: E402

RECORD_CELL0 = PC.ROOT / PC.CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json"


def _run_problems(protocol: dict, run: dict, mode: str) -> list[str]:
    out = []
    if run.get("mode") != mode:
        out.append(f"{mode}: wrong mode {run.get('mode')!r}")
    if run.get("protocol_sha256") != PC.PROTOCOL_HASH.read_text().strip():
        out.append(f"{mode}: not bound to the frozen protocol")
    if PC.scientific_hash(run["scientific"]) != run.get("scientific_hash"):
        out.append(f"{mode}: scientific hash does not recompute")
    stages = [g.get("stage") for g in run.get("gates", [])]
    if stages != ["initial", "final"]:
        out.append(f"{mode}: gates {stages}")
    for g in run.get("gates", []):
        out += PC.identity_problems(protocol, g.get("producer_identity", {}))
    if run.get("gates") and run["gates"][-1].get("scipy_guard") is None:
        out.append(f"{mode}: SciPy guard report missing")
    if run["scientific"]["precision_bits"] != protocol["precision_ladder"]["bits"][0]:
        out.append(f"{mode}: qualification must run at the first rung")
    if sorted(run["scientific"]["m"]) != sorted(str(m) for m in protocol["m_values"]["evaluated"]):
        out.append(f"{mode}: m set differs from the frozen evaluated set")
    return out


def verdict(protocol: dict, replay: dict, point_e0: dict, unit_tests_passed: bool, record: dict) -> dict:
    problems = [] if unit_tests_passed else ["Q1 unit tests not passed"]
    problems += _run_problems(protocol, replay, "replay-cell0")
    problems += _run_problems(protocol, point_e0, "point-e0")
    c0 = replay["scientific"]["cell"]
    if (c0["index"], c0["e0"], c0["rho"]) != (0, record["e0"], record["rho"]):
        problems.append("Q2 replay did not use frozen cell 0 geometry")
    p = point_e0["scientific"]["cell"]
    if not (p["rho"] == ["0/1", "0/1"] and p["left"] == p["right"] == p["e0"] == record["e0"]):
        problems.append("Q3 point-e0 cell is not the degenerate cell {e0}")
    rows = {}
    for m in (str(x) for x in protocol["m_values"]["evaluated"]):
        rec = record["m"][m]
        row = {}
        for key in ("R_interval", "D_interval"):
            want = (F(rec[key]["lo"]), F(rec[key]["hi"]))
            got = tuple(F(replay["scientific"]["m"][m][key][e]) for e in ("lo", "hi"))
            pt = tuple(F(point_e0["scientific"]["m"][m][key][e]) for e in ("lo", "hi"))
            row[key] = {"replay_exact_equal": got == want,
                        "point_e0_contained": want[0] <= pt[0] <= pt[1] <= want[1]}
            if got != want:
                problems.append(f"Q2 m={m} {key}: replay {got} != record {want}")
            if not want[0] <= pt[0] <= pt[1] <= want[1]:
                problems.append(f"Q3 m={m} {key}: point-e0 {pt} not inside record {want}")
        rows[m] = row
    cpu = replay["runtime"]["cpu_seconds"] + point_e0["runtime"]["cpu_seconds"]
    ceiling = F(protocol["cpu_ceiling"]["qualification_cpu_hours"]) * 3600
    if F(cpu) > ceiling:
        problems.append(f"Q5 qualification CPU {cpu:.0f}s exceeds ceiling {float(ceiling):.0f}s")
    return {"schema": "p5y.gammatilde-point-certificate.qualification.v1",
            "protocol_sha256": PC.PROTOCOL_HASH.read_text().strip(),
            "POINT_EVALUATOR_QUALIFICATION": "PASS" if not problems else "FAIL",
            "problems": problems, "per_m": rows,
            "replay_scientific_hash": replay["scientific_hash"],
            "point_e0_scientific_hash": point_e0["scientific_hash"],
            "qualification_cpu_seconds": cpu}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", required=True)
    ap.add_argument("--point-e0", required=True)
    ap.add_argument("--unit-tests-passed", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    protocol = PC.load_protocol()
    v = verdict(protocol, json.loads(Path(a.replay).read_text()), json.loads(Path(a.point_e0).read_text()),
                a.unit_tests_passed, json.loads(RECORD_CELL0.read_text()))
    Path(a.out).write_text(json.dumps(v, indent=1, sort_keys=True) + "\n")
    print(v["POINT_EVALUATOR_QUALIFICATION"], *v["problems"][:5])
    return 0 if v["POINT_EVALUATOR_QUALIFICATION"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
