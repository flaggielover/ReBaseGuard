"""Phase 1: re-run and bind every predecessor verifier / evidence invariant (read-only)."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_endpoint_strips as ES
import sr_o9_bint_p1 as BP

NS = Path(__file__).resolve().parents[1]
CP = T.CP
REPO = CP.parents[1]
VENV = sys.executable
ENV = {"HOME": "/home/ubuntu", "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", **{v: "1" for v in T.THREAD_VARS}}
PYPATH = ":".join(str(CP / p) for p in ("p5y_k1_sr_o9_bint_p1_bound_successor/code", "p5y_k1_sr_o9_endpoint_strip_successor/code",
                                       "p5y_k1_sr_o9_t2_per_patch_successor/code", "p5y_k1_sr_o9_executor_t1_successor/code"))
COMMITS = {"t1": ("ab8d197", "p5y-k1-sr-o9-t1-candidate-construction"),
           "pre_t2_governance": ("a296244", "p5y-k1-sr-o9-pre-t2-governance"),
           "a5_amendment": ("44acc65e", "p5y-k1-sr-o9-pre-t2-a5-amendment"),
           "t2_negative_evidence": ("29ee382b", "p5y-k1-sr-o9-t2-endpoint-not-closing"),
           "endpoint_strip_successor": ("b48973d6", "p5y-k1-sr-o9-endpoint-strip-micropilot"),
           "bint_representation_audit": ("fa92afb", None),
           "bint_governance_authorization": ("014879b", None),
           "bint_pilot": ("0f52b77", None)}
DIRS = ["p5y_k1_sr_o9_executor_t1_successor", "p5y_k1_sr_o9_pre_t2_governance_successor", "p5y_k1_sr_o9_pre_t2_a5_amendment",
        "p5y_k1_sr_o9_t2_per_patch_successor", "p5y_k1_sr_o9_endpoint_strip_successor",
        "p5y_k1_sr_o9_bint_representation_successor", "p5y_k1_sr_o9_bint_p1_bound_successor"]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()          # noqa: E731


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True)


def run(cmd, env_extra=None, cwd=REPO):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env={**ENV, **(env_extra or {})}, timeout=5400)
    return r.returncode, r.stdout, r.stderr


def main():
    T.check_threads()
    checks, rec = {}, {}
    # commits, tags, directory immutability
    full = {k: git("rev-parse", c).stdout.strip() for k, (c, _t) in COMMITS.items()}
    anc = {k: git("merge-base", "--is-ancestor", full[k], "HEAD").returncode == 0 for k in COMMITS}
    tags = {k: (t, git("rev-parse", f"{t}^{{commit}}").stdout.strip()) for k, (c, t) in COMMITS.items() if t}
    rec["commits"] = full
    rec["tags"] = {k: {"tag": t, "commit": c, "matches": c == full[k]} for k, (t, c) in tags.items()}
    checks["predecessor_commits_ancestors_of_HEAD"] = all(anc.values())
    checks["predecessor_tags_point_to_commits"] = all(v["matches"] for v in rec["tags"].values())
    dirs = {d: not git("status", "--porcelain", "--", f"level4/closure_proofs/{d}").stdout.strip()
            and git("diff", "--quiet", "HEAD", "--", f"level4/closure_proofs/{d}").returncode == 0 for d in DIRS}
    rec["dirs_clean_before"] = dirs
    checks["predecessor_dirs_clean_before"] = all(dirs.values())
    # verifiers
    v = {}
    rc, out, err = run([VENV, str(CP / "p5y_k1_sr_o9_pre_t2_governance_successor/code/verify_pre_t2.py"), "verify"])
    pre = json.loads((CP / "p5y_k1_sr_o9_pre_t2_governance_successor/evidence/pre_t2_verification.json").read_text())
    v["verify_pre_t2"] = {"rc": rc, "all_pass": pre["all_pass"], "checks": pre["checks"], "stderr_tail": err[-300:]}
    rc, out, err = run([VENV, str(CP / "p5y_k1_sr_o9_pre_t2_a5_amendment/code/verify_a5.py")])
    try:
        a5 = json.loads(out)
        a5_checks = a5.get("checks")
        a5_pass = (a5.get("all_pass", True) is True and isinstance(a5_checks, dict) and bool(a5_checks)
                   and all(a5_checks.values()) and a5.get("classification", "T2_A5_GOVERNANCE_AMENDMENT_CLOSED")
                   == "T2_A5_GOVERNANCE_AMENDMENT_CLOSED")
    except json.JSONDecodeError:
        a5_pass, a5_checks = False, out[-400:]
    v["verify_a5"] = {"rc": rc, "all_pass": a5_pass, "checks": a5_checks, "stderr_tail": err[-300:]}
    rc, out, err = run([VENV, str(CP / "p5y_k1_sr_o9_bint_p1_bound_successor/code/verify_governance.py"), "verify"],
                       cwd=CP / "p5y_k1_sr_o9_bint_p1_bound_successor/code")
    bg = json.loads((CP / "p5y_k1_sr_o9_bint_p1_bound_successor/evidence/governance_verification.json").read_text())
    v["verify_bint_governance"] = {"rc": rc, "PASS": bg["PASS"], "checks": bg["checks"], "stderr_tail": err[-300:]}
    rec["verifiers"] = v
    checks["verify_pre_t2_pass"] = v["verify_pre_t2"]["rc"] == 0 and v["verify_pre_t2"]["all_pass"]
    checks["verify_a5_pass"] = v["verify_a5"]["rc"] == 0 and v["verify_a5"]["all_pass"]
    checks["verify_bint_governance_pass"] = v["verify_bint_governance"]["rc"] == 0 and v["verify_bint_governance"]["PASS"]
    # endpoint-strip successor evidence invariants
    ESD = CP / "p5y_k1_sr_o9_endpoint_strip_successor"
    man = json.loads((ESD / "config/ENDPOINT_STRIP_MANIFEST.json").read_text())
    def _ev(kind, r):
        c = r["case"]
        if kind == "bounded_pilot":
            return ESD / f"evidence/pilot36/c{c['cell']}_p{c['patch'][0]}_{c['patch'][1]}.json"
        if isinstance(c["cell"], str):
            return ESD / "evidence/micropilot_task1r_reference.json"
        return ESD / f"evidence/micropilot_c{c['cell']}_p{c['patch'][0]}_{c['patch'][1]}.json"
    ev_rows = [(k, r) for k in ("bounded_pilot", "kill_micropilot") for r in man[k]]
    ev_ok = len(ev_rows) == 44 and all(sha(_ev(k, r)) == r["file_sha256"] for k, r in ev_rows)
    src_ok = all(sha(ESD / "code" / n) == h for n, h in man["sources"].items())
    aux_ok = (sha(ESD / "evidence/strip_validation.json") == man["strip_validation_sha256"]
              and sha(ESD / "evidence/raw_shift_fix_checks.txt") == man["raw_shift_fix_checks_sha256"]
              and sha(ESD / "evidence/int_diagnosis.json") == man["int_diagnosis_sha256"])
    stored_val = json.loads((ESD / "evidence/strip_validation.json").read_text())
    val = {}
    for key, (c, i, j) in {"c0_p51_63": (0, 51, 63), "c150_p17_11": (150, 17, 11), "c0_p32_32": (0, 32, 32)}.items():
        val[key] = ES.validate(c, i, j)
    val_equal = json.loads(json.dumps(val)) == stored_val
    old = json.loads((ESD / "evidence/micropilot_c150_p17_11.json").read_text())
    re_run = ES.run_case(150, 17, 11)
    rec["endpoint_successor"] = {"sources_match_manifest": src_ok, "aux_evidence_match_manifest": aux_ok,
                                 "pilot_files_match_manifest": ev_ok, "strip_validation_reproduced": val_equal,
                                 "micropilot_c150_p17_11_scientific_hash_reproduced":
                                     re_run["scientific_hash"] == old["scientific_hash"],
                                 "classification": man["status"]}
    checks["endpoint_successor_invariants"] = (src_ok and aux_ok and ev_ok and val_equal
                                               and re_run["scientific_hash"] == old["scientific_hash"])
    # B_int pilot evidence invariants (0f52b77)
    BPD = CP / "p5y_k1_sr_o9_bint_p1_bound_successor"
    pm = json.loads((BPD / "config/BINT_P1_PILOT_MANIFEST.json").read_text())
    files_ok = all(sha(BPD / r["file"]) == r["file_sha256"] for r in pm["kill_test"] + pm["bounded_pilot"])
    code_ok = all(sha(BPD / f) == h for f, h in pm["code_sha256"].items())
    kc = BP.run_case(0, 51, 63)
    kstored = json.loads((BPD / "evidence/kill/c0_p51_63.json").read_text())
    rec["bint_pilot"] = {"files_match_manifest": files_ok, "code_matches_manifest": code_ok,
                         "counts": pm["counts"], "kill_c0_p51_63_scientific_hash_reproduced":
                             kc["scientific_hash"] == kstored["scientific_hash"]}
    checks["bint_pilot_invariants"] = (files_ok and code_ok and kc["scientific_hash"] == kstored["scientific_hash"]
                                       and pm["counts"]["pilot_all_local_gates_PASS"] == 36)
    dirs_after = {d: not git("status", "--porcelain", "--", f"level4/closure_proofs/{d}").stdout.strip() for d in DIRS}
    rec["dirs_clean_after"] = dirs_after
    checks["predecessor_dirs_clean_after_verifiers"] = all(dirs_after.values())
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.t2-closure-phase1.v1", "checks": checks,
           "all_pass": all(checks.values()), **rec}
    (NS / "evidence/phase1_predecessors.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({"checks": checks, "all_pass": out["all_pass"], "tags": rec["tags"],
                      "endpoint": rec["endpoint_successor"], "bint": {k: v for k, v in rec["bint_pilot"].items() if k != "counts"}}, indent=1))


if __name__ == "__main__":
    main()
