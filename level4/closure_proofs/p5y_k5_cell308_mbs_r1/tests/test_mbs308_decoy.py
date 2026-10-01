"""MB-S r1: the dev-decoy checks (NON-TARGET: decoy cover cell 297, block 0, the development ladder, 2 workers; about
3 minutes per run; cell 297 lies below the band, the guard stays DECOY). Heavy: run deliberately.

* t_dev_decoy_resume_equivalence (MBS-9 ii, dev form): the production `decoy` mode of the successor driver runs
  uninterrupted (A); the same decoy runs through the checkpoint path, SIGKILLed after 2 checkpoints (B1), and is resumed
  from the verified checkpoints (B2). Every certified leaf of Stage 1 and of every Stage-2 decoy bundle of B2 equals A
  (timing keys stripped at every depth, as MB r1 QC04); at least one job was served and at least one computed.
* t_mbr1_repro_tiny (RC2 MBR1_REPRO, tiny form): A's block-0 RLR d4 and C2B N20 job records equal MB r1's committed r3
  QC02 block-0 records exactly (timing stripped). MB r1's driver is never run.
Both run in a sandbox cloned from the separate base store (never the real object store).

    python3.14 -I -S -B test_mbs308_decoy.py [t_name ...] [--out report.json]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mbs308_testlib as T  # noqa: E402

TMP = T.SCRATCH / "t_decoy"
TIMING = {"seconds", "wall_seconds", "cpu_seconds", "cpu_cap"}
_S: dict = {}


def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in TIMING}
    if isinstance(o, list):
        return [strip(v) for v in o]
    return o


def leaves(o) -> int:
    if isinstance(o, dict):
        return sum(leaves(v) for v in o.values())
    if isinstance(o, list):
        return sum(leaves(v) for v in o)
    return 1


def sb() -> T.Sandbox:
    if "sb" not in _S:
        _S["sb"] = T.Sandbox(TMP)
    return _S["sb"]


def baseline() -> dict:
    if "A" not in _S:
        out = TMP / "A_baseline.json"
        p = subprocess.run([T.PY, "-I", "-S", "-B", str(sb().driver), "decoy", "--cell", "297", "--first-blocks", "1",
                            "--dev-ladder", "--workers", "2", "--out", str(out)], capture_output=True, text=True,
                           env=dict(T.GENV), stdin=subprocess.DEVNULL, timeout=1800)
        if p.returncode != 0:
            raise RuntimeError(f"baseline decoy failed: {p.stdout[-300:]} {p.stderr[-300:]}")
        _S["A"] = json.loads(out.read_text())
    return _S["A"]


def t_dev_decoy_resume_equivalence():
    A = baseline()
    T.g(sb().root, "update-ref", "-d", "refs/mbs308-test-decoy/ckpt", check=False)
    b1 = T.child(sb(), "decoy-ckpt", {"fault": {"F3": {"at": 2, "how": "kill"}},
                                      "decoy": {"out": str(TMP / "B1_interrupted.json")}}, timeout=1800)
    names = T.g(sb().root, "ls-tree", "--name-only", "refs/mbs308-test-decoy/ckpt", check=False).split()
    b2 = T.child(sb(), "decoy-ckpt", {"decoy": {"out": str(TMP / "B2_resumed.json"), "resume": True}}, timeout=1800)
    B = json.loads((TMP / "B2_resumed.json").read_text())
    s1a, s1b = strip(A["stage1"]), strip(B["stage1"])
    s2a, s2b = strip(A["stage2_decoys"]), strip(B["stage2_decoys"])
    ctx = B["lifecycle"]["stage1_context"]
    return {"ok": b1["signal"] == 9 and len(names) == 2 and b2["out"] and b2["out"]["served"] == 2
            and b2["out"]["computed"] >= 1 and s1a == s1b and s2a == s2b and not B["lifecycle"]["rejected"],
            "killed_after": names, "served": ctx["served"], "computed": ctx["jobs_computed"],
            "stage1_leaves": leaves(s1a), "stage2_leaves": leaves(s2a), "stage1_equal": s1a == s1b,
            "stage2_equal": s2a == s2b, "peak_rss_bytes_by_kind": A["lifecycle"]["stage1_context"]["peak_rss_bytes_by_kind"],
            "baseline_stage1_wall_s": A["stage1_wall_seconds"], "host": A["host"]["assessment"]["status"]}


def t_mbr1_repro_tiny():
    A = baseline()
    Q = json.loads((T.REPO / T.NSF_REL / "qualification/MB308_QC02_DECOY_297.json").read_text())
    a0, q0 = A["stage1"]["blocks"][0], Q["stage1"]["blocks"][0]
    ra = [r for r in a0["rlr_rungs"] if r["rung"] == 4]
    rq = [r for r in q0["rlr_rungs"] if r["rung"] == 4]
    ca = [r for r in a0["c2b_rungs"] if r["rung"] == 20]
    cq = [r for r in q0["c2b_rungs"] if r["rung"] == 20]
    geo = (a0["tile"], a0["hull"], a0["b"]) == (q0["tile"], q0["hull"], q0["b"])
    return {"ok": geo and len(ra) == len(rq) == 1 and len(ca) == len(cq) == 1 and strip(ra) == strip(rq)
            and strip(ca) == strip(cq), "rlr_d4_equal": strip(ra) == strip(rq), "rlr_d4_leaves": leaves(strip(ra)),
            "c2b_n20_equal": strip(ca) == strip(cq), "c2b_n20_leaves": leaves(strip(ca)), "geometry_equal": geo}


def t_qs_resume_decoy_dev():
    """QS-RESUME-DECOY, DEV form (builder5, brief 50; NONTARGET_DRIFT_VALIDATION): the verifier's own case runner
    (tests/mbs308_resume_decoy.py, the code the official form runs) on decoy 297 block 0 at the dev ladder, 2 workers:
    the uninterrupted production decoy, the checkpoint path SIGKILLed after k = n // 2 durable checkpoints, the resume
    from the verified checkpoints; every certified leaf equal. Also shows the R-MEM fields of the production decoy
    record (brief 50 task 3) on real (decoy) science."""
    import mbs308_resume_decoy as R
    rec = R.run_case("dev")
    A = json.loads((T.SCRATCH / "t_resume_decoy_dev" / "A_uninterrupted.json").read_text())
    lc = A.get("lifecycle", {})
    rmem = {"driver_maxrss_bytes": lc.get("driver_maxrss_bytes"), "rss_sampler": lc.get("rss_sampler"),
            "rmem_run": lc.get("rmem_run")}
    ok = rec.get("pass") is True and rec.get("form") == "dev" and rec.get("k") == rec.get("served") and \
        isinstance(lc.get("driver_maxrss_bytes"), int) and (lc.get("rss_sampler") or {}).get("samples", 0) > 0
    return {"ok": ok, "record": rec, "rmem_fields": rmem}


SCIENCE_DEV_CASES = ("QC01", "QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08", "QC09-SCI", "Q1_theory",
                     "MBR1_REPRO", "Q12_caps", "R_RULES_OFFICIAL")


def t_science_cases_dev():
    """The decision-dependent science cases in their DEV forms (builder6, brief 54; NONTARGET_DRIFT_VALIDATION): the
    verifier itself, in --dev mode, in a sandbox of the separate base store. The ONLY science computed lies on decoy
    cover cell 297, block 0, at the development ladder: the dev decoy (2 workers, run directly), QC04's serial child
    and its ladder pair at block 0's own pointwise drift, QC08's Monte Carlo at block 0's drift. QC01 is never run in
    dev; QC05, QC06, QC07 and QC09-SCI are loader checks (pinned bytes and entry signatures; nothing executed);
    Q1_theory is hashes. Expected: every dev form reports `pass` false (a dev report is never evidence) with
    `dev_checks_ok` true where a dev run exists: QC02 (block 0 ran), QC03 (stand-in), QC04 (serial == pooled; the
    ladder pair identical; planted mutations detected), QC08 (the Monte-Carlo checks hold), MBR1_REPRO tiny (RLR d4 and
    C2B N20 of block 0 equal MB r1's committed QC02 record), Q12_caps (the 17 planted controls and the section-4 values;
    the dev record cannot feed the cap check: no 316 record), R_RULES_OFFICIAL (the dev record carries every rule
    input). The dev decoy's record carries the R-MEM inputs and its host provenance; it was NOT launched by launchd."""
    import shutil
    tmp = T.SCRATCH / "t_science_dev"
    s = T.Sandbox(tmp)
    ns = s.root / T.NS_REL
    shutil.copytree(T.NSS / "config", ns / "config", dirs_exist_ok=True)
    out, work = tmp / "dev_report.json", tmp / "work"
    p = subprocess.run([T.PY, "-I", "-S", "-B", str(ns / "code" / "mbs308_qualify.py"), "--dev", "--work", str(work),
                        "--only", ",".join(SCIENCE_DEV_CASES), "--out", str(out)], capture_output=True, text=True,
                       env=dict(T.GENV), cwd=str(s.root), stdin=subprocess.DEVNULL, timeout=3600)
    try:
        rep = json.loads(out.read_text())
    except (OSError, ValueError):
        return {"ok": False, "rc": p.returncode, "tail": (p.stdout + p.stderr)[-1200:]}
    c = rep["cases"]
    never_pass = all(c.get(k, {}).get("pass") is False for k in SCIENCE_DEV_CASES if k != "Q1_theory") and \
        rep["pass"] is False and rep["dev_mode"] is True
    dev_ok = {k: c.get(k, {}).get("dev_checks_ok") for k in ("QC02", "QC03", "QC04", "QC05", "QC06", "QC07", "QC08",
                                                             "QC09-SCI", "MBR1_REPRO", "Q12_caps",
                                                             "R_RULES_OFFICIAL")}
    wd = sorted(work.glob("mbs308q*"))[-1]
    dec = json.loads((wd / "MBS308_QC02_DECOY_297.json").read_text())
    lc = dec["lifecycle"]
    record = dec["blocks_run"] == [0] and dec["dev_ladder"] is True and lc["rmem_run"]["launched_by_launchd"] is False \
        and lc["rmem_run"]["workers"] == 2 and isinstance(lc["driver_maxrss_bytes"], int) and \
        dec["host"]["assessment"]["status"] in ("CLEAN", "CONTAMINATED", "AMBIGUOUS")
    q04 = c.get("QC04", {})
    ok = p.returncode == 0 and never_pass and all(v is True for v in dev_ok.values()) and record and \
        c.get("Q1_theory", {}).get("pass") is True and c.get("QC01", {}).get("status") == "DEV_FORM" and \
        q04.get("serial_ok") is True and q04.get("ladder_pair_identical") is True and \
        c["Q12_caps"]["planted_controls"]["n"] == 17 and c["Q12_caps"].get("missing") == ["QC03"] and \
        c["MBR1_REPRO"]["rlr_d4"]["equal"] is True and c["MBR1_REPRO"]["c2b_n20"]["equal"] is True
    return {"ok": ok, "rc": p.returncode, "dev_checks_ok": dev_ok, "never_pass": never_pass, "record": record,
            "qc04_jobs": sorted(q04.get("serial_vs_pooled", {})), "ladder_jobs": sorted(q04.get("ladder_pair", {})),
            "mc_rows": (c.get("QC08") or {}).get("n"), "child_exit_codes": rep.get("child_exit_codes"),
            "host": dec["host"]["assessment"]["status"], "wall_s": rep.get("wall_seconds"),
            "tail": "" if ok else (p.stdout + p.stderr)[-600:]}


if __name__ == "__main__":
    T.cli(globals())
