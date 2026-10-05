#!/usr/bin/env python3
"""Check the committed a119e978 rehearsal: record hashes vs REHEARSAL_SUMMARY, every record names the synthetic freeze,
QC15 audit items (A1-A10, A7 detail), QC11 flow counts, QC12/QC_D5 content, gate ledger counters, provenance binding."""
import hashlib
import json
import re
from pathlib import Path

B = Path("/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t5/review/ev")
for lab in ("r2_candidate_followup/evidence/rehearsal", "r2_candidate/evidence/rehearsal"):
    R = B / lab
    S = json.loads((R / "REHEARSAL_SUMMARY.json").read_text())
    P = R / "PROVENANCE.json"
    prov = json.loads(P.read_text())
    print(f"== {lab}: commit {prov.get('commit')} F {prov.get('synthetic_freeze')}")
    print("  provenance sha matches summary:", hashlib.sha256(P.read_bytes()).hexdigest() == S.get("provenance_sha256"))
    bad = [k for k, h in S["files"].items()
           if hashlib.sha256((R / "attempt" / f"{k}.json").read_bytes()).hexdigest() != h]
    print("  record hashes mismatching summary:", bad)
    F = prov.get("synthetic_freeze")
    for k in S["files"]:
        rec = json.loads((R / "attempt" / f"{k}.json").read_text())
        if rec.get("freeze_commit") != F or rec.get("qc") != k or rec.get("pass") is not True:
            print("  RECORD PROBLEM", k, rec.get("freeze_commit"), rec.get("qc"), rec.get("pass"))
    q15 = json.loads((R / "attempt" / "QC15.json").read_text())
    txt = json.dumps(q15)
    a_items = sorted(set(re.findall(r'\\"(A\d+)[^\\"]*\\": (true|false)', txt)))
    print("  QC15 pass:", q15.get("pass"), "A-items (name,value):", a_items[:30])
    tails = [r.get("stdout_tail", "") for r in q15.get("runs", [])]
    for t in tails:
        for line in t.splitlines():
            if re.search(r"A7|A\d+|outside|ecd1c359|eb9a9c22|c902fe2f", line):
                print("   QC15|", line[:220])
    q11 = json.loads((R / "attempt" / "QC11.json").read_text())
    t11 = "".join(r.get("stdout_tail", "") for r in q11.get("runs", []))
    print("  QC11 pass:", q11.get("pass"), "PASS lines in tail:", t11.count("[PASS]"), "FAIL:", t11.count("[FAIL]"),
          "summary lines:", [l for l in t11.splitlines() if re.search(r"\d+/\d+|flows|passed", l)][-3:])
    q12 = json.loads((R / "attempt" / "QC12.json").read_text())
    t12 = "".join(r.get("stdout_tail", "") for r in q12.get("runs", []))
    print("  QC12 pass:", q12.get("pass"), "T5:", "[PASS] T5_formal_scan" in t12, "T14:",
          "[PASS] T14_qhost_refusals_before_the_attempt" in t12, "FAIL:", t12.count("[FAIL]"))
    qd5 = json.loads((R / "attempt" / "QC_D5.json").read_text())
    print("  QC_D5 pass:", qd5.get("pass"), "parts:", [p.get("pass") for p in qd5.get("parts", [])],
          "pins all current:", any("all current" in r.get("stdout_tail", "") for p in qd5.get("parts", [])
                                    for r in p.get("runs", [])))
    rows = [json.loads(l) for l in (R / "GATE_LEDGER.jsonl").read_text().splitlines() if l.strip()]
    nz = [r for r in rows if any(r.get(k, 0) for k in ("new_target_evaluations", "target_equivalent_proxies",
                                                         "target_informed_optimisation"))]
    print("  gate ledger rows:", len(rows), "nonzero target rows:", len(nz),
          "starts:", [r.get("purpose", "")[:60] for r in rows if "START" in str(r.get("purpose", ""))])
