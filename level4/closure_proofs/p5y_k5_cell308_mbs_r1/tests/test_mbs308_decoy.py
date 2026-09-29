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


if __name__ == "__main__":
    T.cli(globals())
