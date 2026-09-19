"""Frozen qualification of the theorem-TC successor. Run on rebaseguard-vultr-02, frozen venv, from a CLEAN checkout
of the FREEZE commit (the commit that adds config/TC_PROTOCOL.json). Evidence goes to --out-dir (outside the checkout).

Gates (all must pass for QUALIFIED; any failure -> NOT_QUALIFIED, and nothing is patched under this protocol):
  S00 CLEAN        head == freeze commit, namespace clean, protocol committed
  S01 PINS         every pin of TC_PROTOCOL.json matches
  S02 RUNTIME      host / python / numpy / scipy / python-flint / venv equal the protocol; the frozen order-3 producer
                   manifest has no problem; the Aux5 producer manifest verifies (manifest_v3.verify)
  S03 PREDECESSORS adopted artifacts equal their pins (inside S01) and the 34 K1 records equal the export manifest
  S04 THEOREM      tc_manufactured: 0 violations of p_j and of the enclosure on every fixture, frozen assembly table
                   equal, all 14 mutants detected
  S05 CROSSCHECK   tc_rule == tc_crosscheck (exact) on every manufactured fixture and on synthetic all-m records
  S06 REPLAY       tc_producer replay on cells 11 and 44: identity gate identical (no order-3 value is computed)
  S07 CONSUMER     tc_consume --replay-only reproduces the adopted deflated consumption exactly
  S08 REFUSALS     (a) mode real refuses at the freeze commit (no qualification / authorization / guard committed);
                   (b) mode real refuses a wrong protocol sha; (c) replay refuses a wrong record sha;
                   (d) the consumer refuses a TC record of the wrong cell / geometry / without identity gate
  S09 COST         CPU seconds of the qualification recorded

    python -B tc_qualify.py --protocol-sha256 SHA --out-dir DIR
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import socket
import subprocess
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
NS_REL = "level4/closure_proofs/p5y_k5_lower_front_order3"
PY = sys.executable
RECORDS = Path("/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
sys.path.insert(0, str(NS / "code"))


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*a) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=True).stdout


def run(cmd, **kw):
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, **kw)
    return p, time.time() - t0


def s00(proto_rel):
    added = git("log", "--diff-filter=A", "--format=%H", "--", proto_rel).split()
    head = git("rev-parse", "HEAD").strip()
    clean = not git("status", "--porcelain", "--", NS_REL).strip()
    return {"pass": bool(added) and head == added[-1] and clean, "head": head,
            "freeze_commit": added[-1] if added else None, "namespace_clean": clean}


def s01(proto):
    bad = [rel for rel, h in proto["pins"].items() if sha(REPO / rel) != h]
    return {"pass": not bad and len(proto["pins"]) >= 60, "pins": len(proto["pins"]), "mismatch": bad}


def s02(proto):
    import numpy
    import scipy
    import flint
    rt = {"host": socket.gethostname(), "python": platform.python_version(), "numpy": numpy.__version__,
          "scipy": scipy.__version__, "python_flint": flint.__version__, "venv": sys.prefix}
    import tc_producer
    Z = tc_producer._import_chain()
    o3 = Z["O3"].producer_manifest_problems()
    import manifest_v3
    mv = manifest_v3.verify()
    return {"pass": rt == proto["runtime"] and not o3 and mv["ok"], "runtime": rt,
            "order3_manifest_problems": o3, "aux5_manifest_ok": mv["ok"], "aux5_problems": mv["problems"][:5]}


def s03(proto):
    man = json.loads((REPO / "level4/closure_proofs/p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/"
                             "COMPOSITE_EXPORT_MANIFEST.json").read_bytes())["files"]
    bad = []
    for k, want in proto["k1_record_sha256"].items():
        if man[f"k4_records/aux5_CUSUM_{k}_256.json"] != want or sha(RECORDS / f"aux5_CUSUM_{k}_256.json") != want:
            bad.append(k)
    return {"pass": not bad and len(proto["k1_record_sha256"]) == 34, "mismatch": bad}


def s04(out_dir):
    p, dt = run([PY, "-B", str(NS / "code/tc_manufactured.py"), "--mutants", "--out", str(out_dir / "MANUFACTURED.json")])
    res = json.loads((out_dir / "MANUFACTURED.json").read_text()) if (out_dir / "MANUFACTURED.json").exists() else {}
    return {"pass": p.returncode == 0 and res.get("pass") is True, "returncode": p.returncode, "seconds": dt,
            "correct_violations": res.get("correct_violations"), "mutants_detected": res.get("mutants_detected"),
            "sha256": sha(out_dir / "MANUFACTURED.json") if res else None}


def s05():
    import tc_crosscheck as X
    import tc_manufactured as T
    import tc_rule as R
    fx = T.fixtures()
    bad = []
    for name, f in fx:
        if R.cell_enclosure(f["rec"], f["A"], 1) != X.enclosure(f["rec"], f["A"], 1):
            bad.append(name)
    rnd = random.Random(7)
    synth = 0
    for trial in range(20):                         # synthetic all-m records built from the fixture objects
        objs = [fx[rnd.randrange(len(fx))][1] for _ in range(5)]
        rec = {"rho": objs[0]["rec"]["rho"], "norms": {"k": objs[0]["rec"]["norms"]["k"],
                                                     "j": [str(F(rnd.randint(1, 9), 7)) for _ in range(5)]},
               "sup_S0": [str(F(rnd.randint(1, 9), 5)) for _ in range(5)],
               "r": {str(r): objs[r]["rec"]["r"]["0"] for r in range(5)}, "W2": {}}
        for r in range(4):
            for j in range(4 - r):
                a = F(rnd.randint(-1000, 1000), 997)
                rec["W2"][f"{r}:{j}"] = [str(a), str(a + F(rnd.randint(0, 50), 10007))]
        A = objs[0]["A"]
        for m in (1, 2, 3, 5):
            synth += 1
            if R.cell_enclosure(rec, A, m) != X.enclosure(rec, A, m):
                bad.append(f"synthetic_{trial}_m{m}")
    return {"pass": not bad, "fixtures": len(fx), "synthetic": synth, "mismatch": bad}


def s06(out_dir, proto):
    procs = {}
    for k in (11, 44):
        cmd = [PY, "-B", str(NS / "code/tc_producer.py"), "replay", "--cell", str(k),
               "--record", str(RECORDS / f"aux5_CUSUM_{k}_256.json"), "--record-sha256", proto["k1_record_sha256"][str(k)],
               "--out", str(out_dir / f"REPLAY_{k}.json")]
        procs[k] = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    res = {}
    for k, p in procs.items():
        so, se = p.communicate()
        ok = p.returncode == 0
        rec = json.loads((out_dir / f"REPLAY_{k}.json").read_text()) if ok else {}
        meta = json.loads(so.strip().splitlines()[-1]) if ok else {}
        res[str(k)] = {"returncode": p.returncode, "identity": rec.get("identity_gate"),
                       "has_scientific_fields": any(x in rec for x in ("r", "W2", "norms")),
                       "cpu_seconds": meta.get("cpu_seconds"), "stderr_tail": se[-400:] if not ok else ""}
    ok = all(v["returncode"] == 0 and v["identity"] and v["identity"].get("identical") and not v["has_scientific_fields"]
             for v in res.values())
    return {"pass": ok, "cells": res}


def s07(out_dir):
    p, dt = run([PY, "-B", str(NS / "code/tc_consume.py"), "--replay-only", "--tc-rule-sha256",
                 sha(NS / "code/tc_rule.py"), "--out", str(out_dir / "CONSUMER_REPLAY.json")])
    return {"pass": p.returncode == 0, "returncode": p.returncode, "seconds": dt, "stdout": p.stdout[-600:],
            "stderr": p.stderr[-600:], "sha256": sha(out_dir / "CONSUMER_REPLAY.json") if p.returncode == 0 else None}


def s08(out_dir, proto, proto_sha):
    out = {}
    rec11 = str(RECORDS / "aux5_CUSUM_11_256.json")
    r11 = proto["k1_record_sha256"]["11"]
    p, _ = run([PY, "-B", str(NS / "code/tc_producer.py"), "real", "--cell", "11", "--record", rec11,
                "--record-sha256", r11, "--protocol-sha256", proto_sha, "--out", str(out_dir / "MUST_NOT_EXIST_a.json")])
    out["a_real_at_freeze_refused"] = p.returncode != 0 and "TCProducerRefusal" in p.stderr \
        and not (out_dir / "MUST_NOT_EXIST_a.json").exists()
    out["a_message"] = p.stderr.strip().splitlines()[-1] if p.stderr else ""
    p, _ = run([PY, "-B", str(NS / "code/tc_producer.py"), "real", "--cell", "11", "--record", rec11,
                "--record-sha256", r11, "--protocol-sha256", "0" * 64, "--out", str(out_dir / "MUST_NOT_EXIST_b.json")])
    out["b_wrong_protocol_refused"] = p.returncode != 0 and "TCProducerRefusal" in p.stderr
    p, _ = run([PY, "-B", str(NS / "code/tc_producer.py"), "replay", "--cell", "11", "--record", rec11,
                "--record-sha256", "1" * 64, "--out", str(out_dir / "MUST_NOT_EXIST_c.json")])
    out["c_wrong_record_refused"] = p.returncode != 0 and "TCProducerRefusal" in p.stderr
    import tc_consume
    fake = {"mode": "real", "cell": 12, "identity_gate": {"identical": True}, "e0": "0", "rho": "0"}
    cases = {"wrong_cell": ({11: dict(fake)}), "no_identity": ({11: dict(fake, cell=11, identity_gate={})}),
             "wrong_geometry": ({11: dict(fake, cell=11)})}
    for name, tc in cases.items():
        try:
            tc_consume.compose(RECORDS, tc, sha(NS / "code/tc_rule.py"))
            out[f"d_{name}_refused"] = False
        except tc_consume.TCConsumeRefusal:
            out[f"d_{name}_refused"] = True
    out["pass"] = all(v for k, v in out.items() if k.endswith("refused"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol-sha256", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    t0 = time.process_time()
    wall0 = time.time()
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    proto_rel = NS_REL + "/config/TC_PROTOCOL.json"
    if sha(REPO / proto_rel) != a.protocol_sha256:
        raise SystemExit("protocol sha mismatch")
    proto = json.loads((REPO / proto_rel).read_bytes())
    res = {"schema": "rebaseguard.p5y.k5.lower-front-order3.tc-qualification.v1", "protocol_sha256": a.protocol_sha256}
    res["S00"] = s00(proto_rel)
    res["S01"] = s01(proto)
    res["S02"] = s02(proto)
    res["S03"] = s03(proto)
    pre = all(res[s]["pass"] for s in ("S00", "S01", "S02", "S03"))
    if pre:
        res["S04"] = s04(out_dir)
        res["S05"] = s05()
        res["S06"] = s06(out_dir, proto)
        res["S07"] = s07(out_dir)
        res["S08"] = s08(out_dir, proto, a.protocol_sha256)
    res["S09"] = {"pass": True, "cpu_seconds_self": time.process_time() - t0, "wall_seconds": time.time() - wall0,
                  "replay_cpu_seconds": sum((v.get("cpu_seconds") or 0) for v in res.get("S06", {}).get("cells", {}).values())}
    gates = [f"S0{i}" for i in range(10)]
    res["QUALIFIED"] = all(res.get(g, {}).get("pass") is True for g in gates)
    res["verdict"] = "QUALIFIED" if res["QUALIFIED"] else "NOT_QUALIFIED"
    (out_dir / "QUALIFICATION_RESULT.json").write_text(json.dumps(res, sort_keys=True, indent=1, default=str) + "\n")
    print(json.dumps({g: res.get(g, {}).get("pass") for g in gates} | {"verdict": res["verdict"]}))
    return 0 if res["QUALIFIED"] else 1


if __name__ == "__main__":
    sys.exit(main())
