"""Adjudication of the science rungs (stdlib only), frozen with the protocol before any scientific run.

    python3 -B code/adjudicate_point.py build  --rung result/RUNG_256.json [--rung ...] --out adjudication/ADJUDICATION.json
    python3 -B code/adjudicate_point.py verify                                   # recompute + temporal integrity

Rules (all from protocol/POINT_PROTOCOL.json, applied mechanically):
  * rungs must follow the frozen ladder (point_core.next_rung), and the ladder must have stopped;
  * each rung must be bound to the frozen protocol, carry both gates, and recompute its scientific hash;
  * any control problem invalidates the run (PROTOCOL_FAILURE), it never changes a target gate;
  * per target m: first decisive rung's status (point_core.final_statuses);
  * GAMMATILDE_INTERVAL = [1 - hi, 1 - lo] of the certified R'(0) enclosure, exact rationals (no rounding needed:
    the enclosure endpoints are already outward exact dyadic rationals and 1 - x is exact);
  * premise: point_core.premise over the targets.
Temporal integrity (verify): protocol commit < qualification commit < result commit in first-parent ancestry, the
qualification and result files are absent at the protocol commit, the result files are absent at the
qualification commit, and the protocol and wrapper files are byte-identical at every later commit.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import point_core as PC  # noqa: E402

ADJ = PC.NS / "adjudication/ADJUDICATION.json"


def _dec(x: F, n: int, up: bool) -> str:
    from math import ceil, floor
    k = (ceil if up else floor)(x * 10 ** n)
    s = "-" if k < 0 else ""
    k = abs(k)
    return f"{s}{k // 10 ** n}.{k % 10 ** n:0{n}d}"


def build(protocol: dict, rungs: list[dict]) -> dict:
    problems = []
    completed = []
    for r in rungs:
        if r.get("mode") != "science":
            problems.append("non-science file offered as a rung")
        if r.get("protocol_sha256") != PC.PROTOCOL_HASH.read_text().strip():
            problems.append("rung not bound to the frozen protocol")
        if PC.scientific_hash(r["scientific"]) != r.get("scientific_hash"):
            problems.append("rung scientific hash does not recompute")
        if [g.get("stage") for g in r.get("gates", [])] != ["initial", "final"]:
            problems.append("rung gates incomplete")
        if r["scientific"]["cell"]["e0"] != [protocol["scientific_target"]["e"], "0/1"] or \
                r["scientific"]["cell"]["rho"] != ["0/1", "0/1"]:
            problems.append("rung is not the degenerate cell at the frozen e")
        recomputed = {str(m): PC.adjudicate(r["scientific"]["m"][str(m)]["D_interval"]["lo"],
                                            r["scientific"]["m"][str(m)]["D_interval"]["hi"])
                      for m in protocol["m_values"]["targets"]}
        if recomputed != r.get("target_status"):
            problems.append("rung target_status does not recompute")
        ctrl = PC.control_problems(protocol, r["scientific"])
        if ctrl != r.get("control_problems"):
            problems.append("rung control problems do not recompute")
        problems += [f"control: {c}" for c in ctrl]
        completed.append({"bits": r["scientific"]["precision_bits"], "status": recomputed})
    try:
        for i in range(len(completed) + 1):
            want = PC.next_rung(protocol, completed[:i])
            if i < len(completed) and want != completed[i]["bits"]:
                problems.append(f"rung {i} bits {completed[i]['bits']} != ladder {want}")
        if completed and PC.next_rung(protocol, completed) is not None:
            problems.append("ladder not exhausted: a further rung was required")
        statuses = PC.final_statuses(protocol, completed) if completed else {}
    except PC.ProtocolViolation as exc:
        problems.append(str(exc))
        statuses = {}
    last = rungs[-1]["scientific"] if rungs else None
    per_m = {}
    if last is not None:
        for m in (str(x) for x in protocol["m_values"]["evaluated"]):
            D = last["m"][m]["D_interval"]
            g = PC.gamma_from_rprime(D["lo"], D["hi"])
            g["decimal_outward"] = {
                "RPRIME0_INTERVAL": [_dec(F(D["lo"]), 6, False), _dec(F(D["hi"]), 6, True)],
                "GAMMATILDE_INTERVAL": [_dec(1 - F(D["hi"]), 6, False), _dec(1 - F(D["lo"]), 6, True)],
                "MARGIN_ABOVE_1": _dec(-F(D["hi"]), 6, False)}
            g["role"] = ("TARGET" if int(m) in protocol["m_values"]["targets"] else
                         "CONTROL" if int(m) in protocol["m_values"]["controls"] else "NON_TARGET_CONTROL")
            per_m[m] = g
    targets = {m: statuses.get(str(m), "INCONCLUSIVE") for m in protocol["m_values"]["targets"]}
    failed = bool(problems)
    cpu = sum(r["runtime"]["cpu_seconds"] for r in rungs)
    if F(cpu) > F(protocol["cpu_ceiling"]["science_cpu_hours"]) * 3600:
        problems.append("science CPU ceiling exceeded")
        failed = True
    prem = "OPEN" if failed else PC.premise({str(k): v for k, v in targets.items()})
    return {"schema": "p5y.gammatilde-point-certificate.adjudication.v1",
            "protocol_sha256": PC.PROTOCOL_HASH.read_text().strip(),
            "PROTOCOL_FAILURE": failed, "problems": problems,
            "rungs": [{"bits": c["bits"], "status": c["status"], "scientific_hash": r["scientific_hash"]}
                      for c, r in zip(completed, rungs)],
            "per_m": per_m,
            "M3_GAMMATILDE_GT_1": "INCONCLUSIVE" if failed else targets[3],
            "M5_GAMMATILDE_GT_1": "INCONCLUSIVE" if failed else targets[5],
            "ALL_CUSUM_M_GAMMATILDE_GT_1": {"SATISFIED": "CERTIFIED", "REFUTED": "REFUTED"}.get(prem, "OPEN"),
            "H3A_POSITIVE_BRANCH_PREMISE_CUSUM": prem,
            "science_cpu_seconds": cpu,
            "science_cpu_hours": cpu / 3600}


def _git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(PC.ROOT), *args], capture_output=True, text=True)


def temporal_problems(commits: dict, rung_start_epochs: list[int]) -> list[str]:
    out = []
    q_time = int(_git("show", "-s", "--format=%ct", commits["qualification"]).stdout.strip() or 0)
    for t in rung_start_epochs:
        if not t > q_time:
            out.append(f"a science rung started at {t}, not after the qualification commit time {q_time}")
    rel = str(PC.NS.relative_to(PC.ROOT))
    p, q, r = commits["protocol_freeze"], commits["qualification"], commits["result"]
    for a, b in ((p, q), (q, r)):
        if _git("merge-base", "--is-ancestor", a, b).returncode != 0 or a == b:
            out.append(f"{a[:8]} is not a strict ancestor of {b[:8]}")
    for c, forbidden in ((p, ("qualification/evidence", "result", "adjudication")), (q, ("result", "adjudication"))):
        for d in forbidden:
            if _git("cat-file", "-e", f"{c}:{rel}/{d}").returncode == 0:
                out.append(f"{d} already present at {c[:8]}")
    frozen = ["protocol/POINT_PROTOCOL.json", "protocol/POINT_PROTOCOL_HASH"]
    frozen += [str(Path(f).relative_to(rel)) for f in json.loads(
        _git("show", f"{p}:{rel}/protocol/POINT_PROTOCOL.json").stdout)["wrapper_files"]]
    for c in (q, r):
        for f in frozen:
            if _git("show", f"{p}:{rel}/{f}").stdout != _git("show", f"{c}:{rel}/{f}").stdout:
                out.append(f"{f} changed between protocol freeze and {c[:8]}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=("build", "verify"))
    ap.add_argument("--rung", action="append", default=[])
    ap.add_argument("--out", default=str(ADJ))
    a = ap.parse_args(argv)
    protocol = PC.load_protocol()
    if a.action == "build":
        adj = build(protocol, [json.loads(Path(p).read_text()) for p in a.rung])
        adj["rung_files"] = [str(Path(p).resolve().relative_to(PC.NS)) for p in a.rung]
        Path(a.out).write_text(json.dumps(adj, indent=1, sort_keys=True) + "\n")
        print(json.dumps({k: v for k, v in adj.items() if k.isupper() or k == "problems"}, indent=1))
        return 0
    adj = json.loads(ADJ.read_text())
    live = build(protocol, [json.loads((PC.NS / p).read_text()) for p in adj["rung_files"]])
    live["rung_files"] = adj["rung_files"]
    live["commits"] = adj.get("commits")
    errs = [] if live == adj else ["adjudication does not recompute from the rung files"]
    if not adj.get("commits"):
        errs.append("commits not recorded")
    else:
        errs += temporal_problems(adj["commits"], [json.loads((PC.NS / p).read_text())["runtime"]["started_epoch"]
                                                   for p in adj["rung_files"]])
    print("POINT_ADJUDICATION_VERIFIED" if not errs else "POINT_ADJUDICATION_REFUSED",
          PC.sha256_file(ADJ))
    for e in errs:
        print(" -", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
