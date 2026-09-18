"""T-EXT frozen qualification + evaluation runner (TEXT_SPEC.md section 4). Run from a CLEAN checkout of the freeze
commit on rebaseguard-vultr-02 with the frozen venv. Writes RUN_STATE.json first, then the evidence, then RUN_COMPLETE.json
(or RUN_FAILED.json). No retries: a failed gate is a final NOT_QUALIFIED.

    python -B code/qualify_text.py --out-dir <evidence dir>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[5]
PY = sys.executable


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def cpu_children() -> float:
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime


def step(args: list, out_dir: Path, name: str) -> dict:
    t0 = time.time()
    p = subprocess.run([PY, "-B"] + args, cwd=str(NS), capture_output=True, text=True)
    (out_dir / f"{name}.log").write_text(p.stdout + "\n--- stderr ---\n" + p.stderr)
    return {"rc": p.returncode, "wall_s": round(time.time() - t0, 2), "stdout_tail": p.stdout.strip().splitlines()[-3:]}


def pins(proto: dict) -> dict:
    bad = {}
    for rel, want in proto["pins"].items():
        f = REPO / rel
        got = sha(f) if f.exists() else None
        if got != want:
            bad[rel] = got
    return {"checked": len(proto["pins"]), "mismatched": bad, "pass": not bad and len(proto["pins"]) > 0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=False)
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"], capture_output=True, text=True).stdout
    (out / "RUN_STATE.json").write_text(json.dumps({"pid": os.getpid(), "argv": sys.argv, "head": head,
                                                    "utc": time.time()}, indent=1) + "\n")
    try:
        proto_path = NS / "config/TEXT_PROTOCOL.json"
        proto = json.loads(proto_path.read_text())
        g = {}
        g["Q00_CLEAN_CHECKOUT"] = {"head": head, "dirty": dirty.splitlines(), "pass": dirty == ""}
        g["Q01_PINS"] = pins(proto)
        r = step(["code/text_transport.py", "replay", "--out", str(out / "REPLAY.json")], out, "replay")
        rep = json.loads((out / "REPLAY.json").read_text()) if (out / "REPLAY.json").exists() else {}
        g["Q02_REPLAY"] = {"rc": r["rc"], "pass": r["rc"] == 0 and rep.get("pass") is True}
        r = step(["code/text_fixtures.py", "--out", str(out / "FIXTURES.json")], out, "fixtures")
        fx = json.loads((out / "FIXTURES.json").read_text()) if (out / "FIXTURES.json").exists() else {}
        req = proto["gates"]["Q03_FIXTURES"]
        keys = ("ran", "wide_ran", "violations_total", "max_eta_C_e0", "ran_eta_C_e0_ge_4", "ran_graded_det_in_0_0p1",
                "min_graded_positive_det", "ran_scalar_fallback")
        g["Q03_FIXTURES"] = {"rc": r["rc"], **{k: fx.get(k) for k in keys},
                             "pass": r["rc"] == 0 and fx.get("violations_total") == 0
                             and fx.get("ran", 0) >= req["min_ran"]
                             and fx.get("max_eta_C_e0", 0) >= req["min_max_eta_C_e0"]
                             and fx.get("ran_eta_C_e0_ge_4", 0) >= req["min_ran_eta_C_e0_ge_4"]
                             and fx.get("ran_graded_det_in_0_0p1", 0) >= req["min_ran_graded_det_in_0_0p1"]
                             and fx.get("min_graded_positive_det", 1) <= req["max_min_graded_positive_det"]
                             and fx.get("ran_scalar_fallback", 0) >= req["min_ran_scalar_fallback"]}
        ledger = str(out / "EVAL_LEDGER.jsonl")
        r = step(["code/text_transport.py", "evaluate", "--out", str(out / "TEXT_RESULT.json"), "--ledger", ledger],
                 out, "evaluate")
        tx = json.loads((out / "TEXT_RESULT.json").read_text()) if (out / "TEXT_RESULT.json").exists() else {"rows": []}
        g["Q04_EVALUATE"] = {"rc": r["rc"], "hulls": len(tx["rows"]),
                             "pass": r["rc"] == 0 and [x["cell"] for x in tx["rows"]] == list(range(0, 41))
                             and all(x["resolvent_mode"] == "graded" for x in tx["rows"])}
        tsha = sha(out / "TEXT_RESULT.json") if (out / "TEXT_RESULT.json").exists() else None
        r = step(["code/text_crosscheck.py", "transport", "--text", str(out / "TEXT_RESULT.json"), "--out",
                  str(out / "XA.json")], out, "xa")
        xa = json.loads((out / "XA.json").read_text()) if (out / "XA.json").exists() else {}
        g["Q05_XA"] = {"rc": r["rc"], "problems": xa.get("problems"), "pass": r["rc"] == 0 and xa.get("pass") is True}
        r = step(["code/text_mutants.py", "--text", str(out / "TEXT_RESULT.json"), "--text-sha256", str(tsha), "--out",
                  str(out / "MUTATIONS.json")], out, "mutants")
        mu = json.loads((out / "MUTATIONS.json").read_text()) if (out / "MUTATIONS.json").exists() else {}
        g["Q06_MUTATIONS"] = {"rc": r["rc"], "detected": mu.get("detected"), "total": mu.get("total"),
                              "shams": mu.get("shams_reproduce"), "pass": r["rc"] == 0 and mu.get("pass") is True}
        r = step(["code/text_transport.py", "evaluate", "--out", str(out / "TEXT_RESULT_RERUN.json"), "--ledger", ledger],
                 out, "evaluate_rerun")
        same = (out / "TEXT_RESULT_RERUN.json").exists() and sha(out / "TEXT_RESULT_RERUN.json") == tsha
        g["Q08_DETERMINISM"] = {"rc": r["rc"], "byte_identical": same, "pass": r["rc"] == 0 and same}
        cpu = cpu_children() + time.process_time()
        g["Q07_COST"] = {"cpu_seconds": round(cpu, 1), "ceiling": proto["gates"]["Q07_COST"]["cpu_seconds_max"],
                         "pass": cpu <= proto["gates"]["Q07_COST"]["cpu_seconds_max"]}
        pre = ("Q00_CLEAN_CHECKOUT", "Q01_PINS", "Q02_REPLAY", "Q03_FIXTURES")
        # Sign-blind verdict (no gate reads any value of Lambda or M): a failure before evaluation is NOT_QUALIFIED; a
        # failure of any gate after evaluation voids the result (T_EXT = VOID). No rerun under this protocol.
        if all(v["pass"] for v in g.values()):
            verdict = "QUALIFIED"
        elif all(g[k]["pass"] for k in pre):
            verdict = "VOID"
        else:
            verdict = "NOT_QUALIFIED"
        res = {"schema": "rebaseguard.p5y.k5.remaining-cell-closure.text-qualification.v1", "head": head,
               "protocol_sha256": sha(proto_path), "gates": g, "text_result_sha256": tsha, "verdict": verdict}
        (out / "QUALIFICATION_RESULT.json").write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
        (out / "RUN_COMPLETE.json").write_text(json.dumps({"utc": time.time(), "verdict": verdict,
                                                           "result_sha256": sha(out / "QUALIFICATION_RESULT.json"),
                                                           "text_result_sha256": tsha}, indent=1) + "\n")
        print(verdict, {k: v["pass"] for k, v in g.items()}, "TEXT_RESULT", tsha)
        return 0 if verdict == "QUALIFIED" else 7
    except Exception:
        (out / "RUN_FAILED.json").write_text(json.dumps({"utc": time.time(), "traceback": traceback.format_exc()}) + "\n")
        raise


if __name__ == "__main__":
    sys.exit(main())
