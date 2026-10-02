"""MB-S r1: the case runner of QS-RESUME-DECOY (MBS-9 ii; protocol section 11; non-holder builder5, research brief 50).
NON-TARGET: decoy cover cell 297 only (below the band; the guard stays DECOY and refuses the band), in a SANDBOX cloned
from the separate --no-local base store (never the real object store); nothing here evaluates cell 305-309.

The case: a complete decoy cell run UNINTERRUPTED (A: the driver's production `decoy` mode, no checkpoints), and the
same decoy run through the checkpoint path, SIGKILLed after k durable checkpoints (B1: the test hook's fault F3 in the
sandbox) and RESUMED from the verified checkpoints (B2). Every certified leaf must be byte-identical: every key of the
decoy output except the named provenance keys (timing, lifecycle, host, identity), with the timing keys stripped at
every depth (MB r1's QC04 set and the per-job `cpu_cap`, as the dev test), canonical JSON; in particular Stage 1 and
every Stage-2 decoy bundle. k = n // 2 (n = the jobs of A's Stage 1), so the resumed run serves k jobs and computes
n - k >= 1. Nothing is hard-coded about the job set: n, the job names and the output keys are read from the runs, so
the case is the same whichever science is frozen (MBS-7).

Forms
  official  297, every block, the frozen ladder, WORKERS workers, timeout DECOY_CAP_S (both read from the driver's
            text): only in the official qualification (or a review re-run with --heavy);
  dev       297, block 0, the development ladder, 2 workers, timeout 1800 s (the existing dev-decoy pattern; ledgered
            as NONTARGET_DRIFT_VALIDATION).
The record written to --out is VALUE-FREE (booleans, counts and job names only); the
raw decoy outputs stay in the scratch directory (MBS308_SCRATCH, outside the repository).

    python3.14 -I -S -B mbs308_resume_decoy.py --form official|dev --out FILE
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402
import mbs308_rrules as RR  # noqa: E402

TIMING = {"seconds", "wall_seconds", "cpu_seconds", "cpu_cap"}
PROVENANCE = {"lifecycle", "host", "mode", "driver_sha256", "utc", "wall_seconds", "cpu_seconds_workers",
              "stage1_wall_seconds", "stage2_wall_seconds"}
CKPT_REF = "refs/mbs308-test-decoy/ckpt"


def _int_literal(n):
    """An int literal or a product / sum / power of int literals (e.g. `12 * 3600`); anything else refuses."""
    if isinstance(n, ast.Constant) and isinstance(n.value, int) and not isinstance(n.value, bool):
        return n.value
    if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Mult, ast.Add, ast.Pow)):
        a, b = _int_literal(n.left), _int_literal(n.right)
        return a * b if isinstance(n.op, ast.Mult) else (a + b if isinstance(n.op, ast.Add) else a ** b)
    raise ValueError("not an int literal")


def driver_constant(name: str, code: Path | None = None) -> int:
    """A module-level int literal of the driver under test, read from its text (the driver is not imported here)."""
    src = ((code or T.code_dir()) / "mbs308_driver.py").read_text()
    found = [n for n in ast.parse(src).body if isinstance(n, ast.Assign) and
             [getattr(t, "id", None) for t in n.targets] == [name]]
    if len(found) != 1:
        raise KeyError(name)
    return _int_literal(found[0].value)


def forms(code: Path | None = None) -> dict:
    return {"official": {"cell": 297, "first_blocks": None, "dev_ladder": False,
                         "workers": int(driver_constant("WORKERS", code)), "timeout": int(driver_constant("DECOY_CAP_S", code))},
            "dev": {"cell": 297, "first_blocks": 1, "dev_ladder": True, "workers": 2, "timeout": 1800}}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in TIMING}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def certified(out: dict) -> dict:
    return strip({k: v for k, v in out.items() if k not in PROVENANCE})


def leaves(o) -> int:
    if isinstance(o, dict):
        return sum(leaves(v) for v in o.values())
    if isinstance(o, list):
        return sum(leaves(v) for v in o)
    return 1


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def _watchdog_status(record: dict | None) -> str | None:
    if not isinstance(record, dict) or record.get("decoy_failed") is None:
        return None
    wd = (((record.get("lifecycle") or {}).get("stage1_context") or {}).get("memory_watchdog") or {})
    events = wd.get("events")
    if isinstance(events, list) and RR.cap_events(events):
        return RR.STATUS_OFFICIAL_WATCHDOG
    return None


def run_case(form: str) -> dict:
    # Resolve constants from the sandbox copy under test.  This remains correct for mutant runs where
    # MBS308_TEST_CODE_DIR points at a temporary tree, and avoids importing the source checkout's driver.
    f = forms(T.code_dir())[form]
    if f["cell"] != 297:
        raise RuntimeError("QS-RESUME-DECOY runs on decoy cover cell 297 only")
    tmp = T.SCRATCH / f"t_resume_decoy_{form}"
    sb = T.Sandbox(tmp)
    t0 = time.time()
    a_out = tmp / "A_uninterrupted.json"
    args = [T.PY, "-I", "-S", "-B", str(sb.driver), "decoy", "--cell", str(f["cell"]), "--workers", str(f["workers"]),
            "--out", str(a_out)]
    if f["first_blocks"] is not None:
        args += ["--first-blocks", str(f["first_blocks"])]
    if f["dev_ladder"]:
        args += ["--dev-ladder"]
    p = subprocess.run(args, capture_output=True, text=True, env=dict(T.GENV), stdin=subprocess.DEVNULL,
                       timeout=f["timeout"])
    rec = {"form": form, "cell": f["cell"], "workers": f["workers"], "first_blocks": f["first_blocks"],
           "ladder": "dev" if f["dev_ladder"] else "frozen", "A_rc": p.returncode}
    if p.returncode != 0:
        if a_out.is_file():
            try:
                failed = json.loads(a_out.read_text())
            except (OSError, ValueError):
                failed = {}
            if _watchdog_status(failed):
                return rec | {"pass": False, "status": RR.STATUS_OFFICIAL_WATCHDOG,
                               "fail_closed_statuses": [RR.STATUS_OFFICIAL_WATCHDOG],
                               "reason": "UNINTERRUPTED_RUN_FAILED", "A_tail": p.stdout[-300:] + p.stderr[-300:]}
        return rec | {"pass": False, "reason": "UNINTERRUPTED_RUN_FAILED", "A_tail": p.stdout[-300:] + p.stderr[-300:]}
    A = json.loads(a_out.read_text())
    if not isinstance(A, dict) or not isinstance(A.get("lifecycle"), dict) or not isinstance(
            (A.get("lifecycle") or {}).get("stage1_context"), dict) or \
            not isinstance((A.get("lifecycle") or {}).get("stage1_context", {}).get("jobs_computed"), int):
        return rec | {"pass": False, "reason": "UNINTERRUPTED_RUN_FAILED", "A_tail": p.stdout[-300:] + p.stderr[-300:]}
    n = A["lifecycle"]["stage1_context"]["jobs_computed"]
    k = max(1, n // 2)
    T.g(sb.root, "update-ref", "-d", CKPT_REF, check=False)
    spec = {"cell": f["cell"], "workers": f["workers"], "first_blocks": f["first_blocks"],
            "dev_ladder": f["dev_ladder"]}
    b1 = T.child(sb, "decoy-ckpt", {"fault": {"F3": {"at": k, "how": "kill"}},
                                   "decoy": dict(spec, out=str(tmp / "B1_interrupted.json"))}, timeout=f["timeout"])
    names = T.g(sb.root, "ls-tree", "--name-only", CKPT_REF, check=False).split()
    b2 = T.child(sb, "decoy-ckpt", {"decoy": dict(spec, out=str(tmp / "B2_resumed.json"), resume=True)},
                 timeout=f["timeout"])
    try:
        B = json.loads((tmp / "B2_resumed.json").read_text())
    except (OSError, ValueError):
        failed = None
        try:
            failed = json.loads((tmp / "B2_resumed.json").read_text())
        except (OSError, ValueError):
            pass
        status = _watchdog_status(failed)
        if status:
            return rec | {"pass": False, "status": status, "fail_closed_statuses": [status],
                          "reason": "RESUMED_RUN_FAILED", "B1_signal": b1["signal"], "B2": b2["out"]}
        return rec | {"pass": False, "reason": "RESUMED_RUN_FAILED", "B1_signal": b1["signal"], "B2": b2["out"],
                      "B2_tail": (b2["stdout"] + b2["stderr"])[-400:]}
    status = _watchdog_status(B)
    if status:
        return rec | {"pass": False, "status": status, "fail_closed_statuses": [status],
                      "reason": "RESUMED_RUN_FAILED", "B1_signal": b1["signal"]}
    if not isinstance(B, dict) or not isinstance(B.get("lifecycle"), dict) or not isinstance(
            (B.get("lifecycle") or {}).get("stage1_context"), dict):
        return rec | {"pass": False, "reason": "RESUMED_RUN_FAILED", "B1_signal": b1["signal"]}
    ca, cb = certified(A), certified(B)
    ctx = B["lifecycle"]["stage1_context"]
    s1_eq = ca.get("stage1") == cb.get("stage1")
    s2_eq = ca.get("stage2_decoys") == cb.get("stage2_decoys")
    rec.update({"jobs_uninterrupted": n, "k": k, "killed_signal": b1["signal"], "checkpoints_after_kill": len(names),
                "checkpoint_names_after_kill": names, "resumed_rc": (b2["out"] or {}).get("rc"),
                "served": ctx["jobs_served_from_checkpoints"], "computed": ctx["jobs_computed"],
                "served_names": ctx["served"], "rejected_checkpoints": len(B["lifecycle"]["rejected"]),
                "certified_keys": sorted(ca), "certified_keys_equal": sorted(ca) == sorted(cb),
                "stage1_leaves": leaves(ca.get("stage1")), "stage2_leaves": leaves(ca.get("stage2_decoys")),
                "certified_leaves": leaves(ca), "stage1_equal": s1_eq, "stage2_equal": s2_eq,
                "all_certified_equal": ca == cb, "canonical_bytes_equal": canon(ca) == canon(cb),
                "host_uninterrupted": A["host"]["assessment"]["status"], "wall_s": round(time.time() - t0, 1)})
    rec["pass"] = bool(b1["signal"] == 9 and len(names) == k and rec["resumed_rc"] == 0 and rec["served"] == k
                       and rec["computed"] == n - k and rec["computed"] >= 1 and sorted(rec["served_names"]) ==
                       sorted(names) and rec["rejected_checkpoints"] == 0 and rec["certified_keys_equal"]
                       and "stage1" in ca and s1_eq and (f["cell"] != 297 or ("stage2_decoys" in ca and s2_eq))
                       and rec["all_certified_equal"] and rec["canonical_bytes_equal"])
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--form", choices=("official", "dev"), required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    rec_life = T.lifecycle_begin(f"QS-RESUME-DECOY {a.form}")
    try:
        try:
            rec = run_case(a.form)
        except Exception as exc:                                        # noqa: BLE001 (a failed case, recorded)
            rec = {"form": a.form, "pass": False, "error": f"{type(exc).__name__}: {exc}"[:500]}
        rec.update({"case": "QS-RESUME-DECOY", "target_evaluations": 0})
        Path(a.out).write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    finally:
        T.lifecycle_finish(rec_life)
    print(json.dumps({"pass": rec["pass"], "form": a.form}))
    return 0 if rec["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
