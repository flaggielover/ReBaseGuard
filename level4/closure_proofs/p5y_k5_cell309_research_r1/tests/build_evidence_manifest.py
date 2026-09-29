"""Evidence manifest for the single-code-state SRK qualification package (owner instruction 2026-09-29 overnight, s.3).

  python3 tests/build_evidence_manifest.py  -> evidence/SRK_EVIDENCE_MANIFEST.json; exit 0 iff the package is complete

For every DECLARED job (config/SRK_DECOY_DECLARATION.json whole-kernel blocks; SRK_DECOY_DECLARATION_A2.json cell
sub-blocks) the manifest records: present?, producer fingerprint, git_head_at_start, geometry, kernel, block, weight
block, the ledger lines of its certifier calls (count, first/last UTC), and per certificate: sha256 (recomputed),
status, index, degree, independent-verifier verdict (VERIFY_RESULTS.json, matched by sha256) with the verifier file's
sha256, mutant expectations met / run, MC control row (SRK_MC_CONTROL.json) and, for cells, gate admission
(SRK_CELL_FAMILY_E2E.json).
The ledger-call count is informational: ledgered TEST runs on the same synthetic decoy block (h = 3,
E = [1/4, 9/32]: tests/test_srk_cert_mutants.py, test_srk_wrec_refusal.py) are indistinguishable by purpose line.
Completeness: every declared job present, no undeclared file, one producer state, every certificate ACCEPTED, every
mutant expectation met, every MC row passing, every cell end-to-end check passing.  Anything else is reported, never
dropped.
"""
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(NS / "impl"))
import srk_certify as S  # noqa: E402
import srk_gate as GT  # noqa: E402
import srk_decoy_suite as SUITE  # noqa: E402  (the runner's own declared-job enumeration)


def declared_jobs() -> list:
    out = []
    for mode in ("whole", "cell"):
        for h, k, lo, hi, idx, ladder, whole, wb, sub, name in SUITE.jobs_for(mode):
            out.append({"h": h, "k": k, "lo": lo, "hi": hi, "indices": list(idx), "ladder": list(ladder),
                        "whole": whole, "wb": wb, "sub": sub, "name": name})
    return out

LOCK_COMMIT = "2a03e838498ab8a8c1c61b9a142ba45adb941592"
LOCK_FP = "377057bef1d1f21be4db38488235596c0e4134bb75ffdced08e667e6c48cc8db"


def load(p):
    return json.loads(p.read_text()) if p.exists() else None


def main():
    ver = load(NS / "verify" / "VERIFY_RESULTS.json") or {"files": {}}
    vsha = hashlib.sha256((NS / "verify" / "srk_verify_indep.py").read_bytes()).hexdigest()
    by_sha = {}
    for rel, fres in ver.get("files", {}).items():
        for label, e in fres.items():
            if isinstance(e, dict) and e.get("sha256"):
                ms = e.get("mutants", {})
                by_sha[e["sha256"]] = {"file": rel, "verdict": e.get("verdict"), "reason": e.get("reason"),
                                       "mutants_run": len(ms),
                                       "mutants_met": sum(1 for m in ms.values() if m.get("expectation_met"))}
    mc = load(NS / "evidence" / "SRK_MC_CONTROL.json") or {"rows": []}
    mc_rows = {(r["file"], r["i"]): r for r in mc.get("rows", [])}
    e2e = load(NS / "evidence" / "SRK_CELL_FAMILY_E2E.json")
    ledger = [json.loads(l) for l in (NS / "ledger" / "ZERO_TARGET_LEDGER.jsonl").read_text().splitlines() if l.strip()]
    jobs = declared_jobs()
    out, problems = [], []
    present_names = {(sub, p.name) for sub in ("srk_decoys", "srk_decoys_cell")
                     for p in (NS / "evidence" / sub).glob("*.json")}
    declared_names = {(j["sub"], j["name"]) for j in jobs}
    for extra in sorted(present_names - declared_names):
        problems.append(f"undeclared evidence file {extra}")
    for j in jobs:
        p = NS / "evidence" / j["sub"] / j["name"]
        d = load(p)
        key = f"h={F(j['h'])},k={F(j['k'])}"
        tag = f"E=[{j['lo']},{j['hi']}]"
        lines = [r for r in ledger if r.get("script") == "impl/srk_certify.py" and key in r.get("purpose", "")
                 and r.get("purpose", "").endswith(tag) and r["utc"] >= "2026-09-29T16:07:30Z"
                 and (j["wb"] is None or f"weight=[{j['wb'][0]},{j['wb'][1]}]" in r.get("purpose", "")
                      or "certify_W" in r.get("purpose", ""))]
        rec = {"job": j, "present": d is not None, "ledger_calls": len(lines),
               "ledger_first": lines[0]["utc"] if lines else None, "ledger_last": lines[-1]["utc"] if lines else None}
        if d is None:
            problems.append(f"missing {j['sub']}/{j['name']}")
            out.append(rec)
            continue
        rec.update({"producer": d["producer"]["combined"], "git_head_at_start": d.get("git_head_at_start"),
                    "geometry": d["geometry"], "kernel": d["kernel"], "block": d["block"],
                    "weight_block": d.get("weight_block"),
                    "W_status": [r["W_status"] for r in d["rungs"]]})
        if rec["producer"] != LOCK_FP or rec["git_head_at_start"] != LOCK_COMMIT:
            problems.append(f"{j['name']}: code state differs from the lock")
        if d["kernel"] != "whole":
            problems.append(f"{j['name']}: kernel {d['kernel']}")
        certs = []
        for i, c in sorted(d["certificates"].items(), key=lambda kv: int(kv[0])):
            v = by_sha.get(c.get("sha256"), {})
            row = {"i": int(i), "status": c.get("status"), "sha256": c.get("sha256"),
                   "sha_recomputed_ok": c.get("status") != "CERTIFIED" or GT.canonical_sha(c) == c.get("sha256"),
                   "degree": c.get("degree"), "Gamma_present": c.get("Gamma") is not None,
                   "verifier_verdict": v.get("verdict", "NOT_VERIFIED"), "verifier_reason": v.get("reason"),
                   "mutants_met": v.get("mutants_met"), "mutants_run": v.get("mutants_run")}
            if j["sub"] == "srk_decoys":
                m = mc_rows.get((j["name"], int(i)))
                row["mc_control"] = None if m is None else {"pass": m["control_pass"], "tightness": m["tightness"]}
                if m is None or not m["control_pass"]:
                    problems.append(f"{j['name']}#{i}: MC control {'missing' if m is None else 'FAIL'}")
            if c.get("status") != "CERTIFIED":
                problems.append(f"{j['name']}#{i}: status {c.get('status')}")
            if not row["sha_recomputed_ok"]:
                problems.append(f"{j['name']}#{i}: sha mismatch")
            if row["verifier_verdict"] != "ACCEPT":
                problems.append(f"{j['name']}#{i}: verifier {row['verifier_verdict']}")
            if row["mutants_run"] is None or row["mutants_met"] != row["mutants_run"] or row["mutants_run"] == 0:
                problems.append(f"{j['name']}#{i}: mutant expectations {row['mutants_met']}/{row['mutants_run']}")
            certs.append(row)
        rec["certificates"] = certs
        out.append(rec)
    if e2e is None:
        problems.append("cell-family end-to-end result missing")
    else:
        for c in e2e["cells"]:
            bad = [k for k, v in c["checks"].items() if not v]
            if bad:
                problems.append(f"e2e cell {c['geometry']} {c['cell']}: failing {bad}")
    manifest = {"schema": "SRK_EVIDENCE_MANIFEST/1", "lock_commit": LOCK_COMMIT, "lock_producer_fingerprint": LOCK_FP,
                "verifier_file_sha256": vsha, "declared_jobs": len(jobs),
                "present_jobs": sum(1 for r in out if r["present"]),
                "certificates": sum(len(r.get("certificates", [])) for r in out),
                "complete": not problems, "problems": problems, "jobs": out,
                "e2e_ok": None if e2e is None else e2e["ok"], "mc_ok": mc.get("ok")}
    (NS / "evidence" / "SRK_EVIDENCE_MANIFEST.json").write_text(json.dumps(manifest, indent=1, sort_keys=True))
    print(json.dumps({k: manifest[k] for k in ("declared_jobs", "present_jobs", "certificates", "complete",
                                                "e2e_ok", "mc_ok")}))
    for pr in problems[:40]:
        print("  -", pr)
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
