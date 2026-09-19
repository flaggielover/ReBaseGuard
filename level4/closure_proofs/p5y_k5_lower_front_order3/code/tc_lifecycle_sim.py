"""Qualification S08(l): the whole governed lifecycle, simulated in a THROWAWAY clone (review r2 N-R2-1, B-R2-1).

No CUSUM value is computed: every "cell record" is a synthetic NO-OP record (huge radii), so the consumption must equal
the adopted one. The clone is `git clone --shared` of the qualification checkout (at the freeze commit) into
OUT_DIR/lifecycle_sim; all commits happen there only.

Sequence (spec section 8): QUALIFICATION_RESULT -> AUTHORIZATION -> GUARD ALLOW (three commits); the producer's
`require_authorized` must PASS for an address and REFUSE a non-address; a sealed evidence set (34 no-op records,
2 reproductions, TC_INDEX, RUN_LEDGER, GUARD back to DENY) is committed; `tc_consume.py` (non-replay) must PASS with
pass sets identical to the adopted ones; then four tamper cases must be REFUSED:
  T1 uncommitted pin-consistent edit of tc_rule.py and the protocol     T2 committed edit of TC_INDEX.json
  T3 GUARD committed back to ALLOW                                       T4 committed edit of tc_rule.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

NS_REL = "level4/closure_proofs/p5y_k5_lower_front_order3"
EVID = NS_REL + "/evidence/tc_r1"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def dump(o) -> bytes:
    return json.dumps(o, sort_keys=True, indent=1).encode() + b"\n"


def run(repo: Path, out_dir: Path, protocol_sha256: str, py: str, records: str) -> dict:
    tmp = out_dir / "lifecycle_sim"
    if tmp.exists():
        raise RuntimeError("lifecycle_sim already exists")
    subprocess.run(["git", "clone", "-q", "--shared", str(repo), str(tmp)], check=True)

    def git(*a, check=True):
        return subprocess.run(["git", "-C", str(tmp), "-c", "user.name=sim", "-c", "user.email=sim@local", *a],
                              capture_output=True, text=True, check=check).stdout

    def write(rel: str, data: bytes):
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def commit(msg: str, *paths):
        git("add", "-f", *paths)
        git("commit", "-q", "-m", msg)
        return git("rev-parse", "HEAD").strip()

    res = {}
    proto = json.loads((tmp / NS_REL / "config/TC_PROTOCOL.json").read_bytes())
    addrs = proto["addresses"]["cells"]
    freeze = git("rev-parse", "HEAD").strip()
    qual = dump({"QUALIFIED": True, "protocol_sha256": protocol_sha256, "S00": {"head": freeze}, "simulation": True})
    write(EVID + "/QUALIFICATION_RESULT.json", qual)
    commit("sim: qualification", EVID + "/QUALIFICATION_RESULT.json")
    auth = dump({"verdict": "AUTHORIZED", "protocol_sha256": protocol_sha256, "addresses": addrs,
                 "qualification_result_sha256": sha(qual), "simulation": True})
    write(EVID + "/AUTHORIZATION.json", auth)
    commit("sim: authorization", EVID + "/AUTHORIZATION.json")
    guard = {"state": "ALLOW", "addresses": addrs, "protocol_sha256": protocol_sha256,
             "authorization_sha256": sha(auth)}
    write(EVID + "/GUARD.json", dump(guard))
    run_head = commit("sim: guard allow", EVID + "/GUARD.json")
    code = tmp / NS_REL / "code"
    probe = ("import sys, json; sys.path.insert(0, %r); import tc_producer as T\n"
             "b = T.require_authorized(int(sys.argv[1]), %r); b.pop('protocol'); print(json.dumps(b))") % (
        str(code), protocol_sha256)
    p = subprocess.run([py, "-B", "-c", probe, "11"], capture_output=True, text=True)
    res["gate_positive_pass"] = p.returncode == 0
    binding = json.loads(p.stdout.strip().splitlines()[-1]) if p.returncode == 0 else None
    p = subprocess.run([py, "-B", "-c", probe, "10"], capture_output=True, text=True)
    res["gate_non_address_refused"] = p.returncode != 0 and "TCProducerRefusal" in p.stderr
    if binding is None:
        res["pass"] = False
        res["stderr"] = p.stderr[-800:]
        return res
    res["binding_head_is_run_head"] = binding["head"] == run_head
    trun = [py, "-B", str(code / "tc_run.py"), "--protocol-sha256", protocol_sha256, "--preflight-only"]
    p = subprocess.run(trun + ["--evidence", str(out_dir / "sim_run_evidence")], capture_output=True, text=True)
    res["run_preflight_positive_pass"] = p.returncode == 0 and not (out_dir / "sim_run_evidence").exists()
    inside = tmp / EVID / "run_evidence_inside"
    p = subprocess.run(trun + ["--evidence", str(inside)], capture_output=True, text=True)
    res["run_preflight_inside_checkout_refused"] = p.returncode == 2 and not inside.exists()
    cover = {c["index"]: c for c in json.loads((tmp / "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/"
                                                "cells.json").read_bytes()) if c["detector"] == "CUSUM"}
    big = "1000000"
    shas = {}
    for k in addrs:
        c = cover[k]
        rec = {"schema": "rebaseguard.p5y.k5.lower-front-order3.tc-cell.v1", "mode": "real", "cell": k,
               "e0": str(F(c["e0"][0]) + F(c["e0"][1])), "rho": str(F(c["rho"][0]) + F(c["rho"][1])),
               "identity_gate": {"identical": True}, "k1_record_sha256": proto["k1_record_sha256"][str(k)],
               "runtime_checks": {"runtime": proto["runtime"]},
               "binding": binding, "norms": {"k": ["1"] * 5, "j": ["1"] * 5}, "sup_S0": ["1"] * 5,
               "r": {str(r): {"delta_F": big, "delta_D": big, "delta_H": big, "delta_G": big, "eps_src": ["0"] * 4,
                              "sup": {"F": "1", "D": "1", "H": "1", "G": "1"}, "H_at_a": ["0", "0"],
                              "abs_G_at_a": "0"} for r in range(5)},
               "W2": {f"{r}:{j}": ["-1", "1"] for r in range(4) for j in range(4 - r)}}
        data = dump(rec)
        write(f"{EVID}/cells/TC_CELL_{k}.json", data)
        shas[str(k)] = sha(data)
    for k in (11, 44):
        write(f"{EVID}/repro/TC_CELL_{k}.json", (tmp / f"{EVID}/cells/TC_CELL_{k}.json").read_bytes())
    index = {"schema": "rebaseguard.p5y.k5.lower-front-order3.tc-index.v1", "protocol_sha256": protocol_sha256,
             "head": run_head, "cells": shas, "reproduction": {"11": True, "44": True}, "cpu_seconds_total": 0}
    write(EVID + "/TC_INDEX.json", dump(index))
    isha = sha((tmp / EVID / "TC_INDEX.json").read_bytes())
    lines = [{"event": "RUN_START"}] + [{"event": "START", "cell": k} for k in addrs] + \
            [{"event": "OUTPUT", "cell": k, "ok": True, "sha256": shas[str(k)]} for k in addrs] + \
            [{"event": "REPRO", "cell": k, "identical": True} for k in (11, 44)] + \
            [{"event": "RUN_END", "reproduction_identical": True, "index_sha256": isha}]
    lines = [dict(x, head=run_head) for x in lines]
    write(EVID + "/RUN_LEDGER.jsonl", "".join(json.dumps(x, sort_keys=True) + "\n" for x in lines).encode())
    write(EVID + "/GUARD.json", dump(dict(guard, state="DENY")))
    seal = commit("sim: seal", EVID)
    cons = [py, "-B", str(code / "tc_consume.py"), "--records", records, "--protocol-sha256", protocol_sha256]
    p = subprocess.run(cons + ["--out", str(out_dir / "sim_consume.json")], capture_output=True, text=True)
    res["consume_positive_pass"] = p.returncode == 0
    if p.returncode == 0:
        sim = json.loads((out_dir / "sim_consume.json").read_bytes())
        base = json.loads((out_dir / "CONSUMER_REPLAY.json").read_bytes())
        res["consume_noop_unchanged"] = all(
            sim["consumptions"][m]["rows_sha256"] == base["consumptions"][m]["rows_sha256"] for m in "1235") \
            and sim["crosscheck_comparisons"] == 4 * len(addrs)
    else:
        res["consume_stderr"] = p.stderr[-800:]

    def refused(name: str):
        p = subprocess.run(cons + ["--out", str(out_dir / f"sim_{name}.json")], capture_output=True, text=True)
        res[f"{name}_refused"] = p.returncode != 0 and "TCConsumeRefusal" in p.stderr
        git("reset", "-q", "--hard", seal)
    # T1 uncommitted, pin-consistent edit of tc_rule.py + protocol (the r2 demonstration)
    rule = code / "tc_rule.py"
    new_rule = rule.read_bytes().replace(b"p2 = fH + rho * fG + rho ** 2 * e4 / 2", b"p2 = (fH + rho * fG) / 2")
    rule.write_bytes(new_rule)
    pr = tmp / NS_REL / "config/TC_PROTOCOL.json"
    pj = json.loads(pr.read_bytes())
    pj["pins"][NS_REL + "/code/tc_rule.py"] = sha(new_rule)
    pr.write_bytes(dump(pj))
    cons_t1 = cons[:-1] + [sha(pr.read_bytes())]
    p = subprocess.run(cons_t1 + ["--out", str(out_dir / "sim_T1.json")], capture_output=True, text=True)
    res["T1_uncommitted_rule_edit_refused"] = p.returncode != 0 and "TCConsumeRefusal" in p.stderr
    git("reset", "-q", "--hard", seal)
    # T2 committed edit of the sealed index
    ix = tmp / EVID / "TC_INDEX.json"
    ix.write_bytes(ix.read_bytes() + b" \n")
    commit("sim: tamper index", EVID + "/TC_INDEX.json")
    refused("T2_index_edit")
    # T3 guard back to ALLOW
    write(EVID + "/GUARD.json", dump(guard))
    commit("sim: guard allow again", EVID + "/GUARD.json")
    refused("T3_guard_allow")
    # T4 committed edit of tc_rule.py
    rule.write_bytes(new_rule)
    commit("sim: tamper rule", NS_REL + "/code/tc_rule.py")
    refused("T4_committed_rule_edit")
    res["pass"] = all(v for k, v in res.items() if k.endswith(("_pass", "_refused", "_unchanged", "_run_head")))
    shutil.rmtree(tmp)                                   # scoped: the throwaway clone created above
    return res


if __name__ == "__main__":
    out = run(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.executable, sys.argv[4])
    print(json.dumps(out))
    sys.exit(0 if out["pass"] else 1)
