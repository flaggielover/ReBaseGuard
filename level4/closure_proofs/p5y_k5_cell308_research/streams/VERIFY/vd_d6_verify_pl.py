"""Stream D, D6(a): verify every stored stream-A0 C2b / C2bx P1 certificate with the independent PL verifier.

For each NS/streams/A0/certs/C2B*_{SUPER,SUB}_*.json (read-only): adapter (shape + W_sha256 recomputed from the
stored integers), declared drift, direction from the certifier field (C2B_P1_SUPER -> W >= 1 + K_e W and W >= 0;
C2B_P1_SUB -> W <= 1 + K_e W), then vd_pl.verify_pl at the certificate's exact drift and N, and the exact comparison
W(a) == claim_w_atom.  Results are merged into results/D6_VERIFY_PL.json after every certificate.
Usage: python3 -I -B vd_d6_verify_pl.py [N ...]      (default: 10 20 40)
Imports: stdlib, vd_pl, vd_verify.  No certifier module; stream A0 code is NOT imported.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_pl as PLm  # noqa: E402
import vd_verify as V  # noqa: E402

Q = V.Q
A0_CERTS = HERE.parent / "A0" / "certs"
OUT = HERE / "results" / "D6_VERIFY_PL.json"
DECLARED = {F(1, 2), F(1), F(11, 10), F(27, 10), F(3), F(7, 2)}


def run(Ns: list, workers: int = 3) -> dict:
    doc = json.loads(OUT.read_text()) if OUT.exists() else {"schema": "VD_D6/1", "rows": {}}
    files = sorted(p for p in A0_CERTS.glob("C2B*.json") if ("_SUPER_" in p.name or "_SUB_" in p.name))
    for pth in files:
        Q.guard_path(pth)
        raw = pth.read_bytes()
        cert = json.loads(raw)
        N = int(cert["N"])
        if N not in Ns:
            continue
        e = F(cert["drift"])
        if e not in DECLARED:
            raise SystemExit(f"undeclared drift in {pth.name}")
        Q.guard_drift(e)
        row = {"file": pth.name, "file_sha256": hashlib.sha256(raw).hexdigest(), "certifier": cert["certifier"],
               "selection": cert.get("selection"), "drift": cert["drift"], "N": N, "kind": cert.get("kind")}
        try:
            W = PLm.from_a0_cert(cert)
            row["W_sha256_ok"] = True
        except ValueError as exc:
            row.update({"W_sha256_ok": False, "verdict": "FAIL", "reason": str(exc)})
            doc["rows"][pth.name] = row
            continue
        direction = "super" if cert["certifier"] == "C2B_P1_SUPER" else "sub"
        if cert.get("kind") != "whole":
            row.update({"verdict": "FAIL", "reason": "KIND_NOT_WHOLE"})
            doc["rows"][pth.name] = row
            continue
        t0 = time.process_time()
        r = PLm.verify_pl(W, e, direction=direction, workers=workers, claim=cert["claim_w_atom"])
        row.update({"direction": direction, "verdict": r["verdict"], "expected": "PASS",
                    "W_at_atom": r["W_at_atom"], "claim_w_atom": cert["claim_w_atom"],
                    "W_at_atom_equals_claim": r["W_at_atom_equals_claim"],
                    "min_margin_lower_bound": r["min_margin_lower_bound"],
                    "min_residual_upper_bound": r["min_residual_upper_bound"],
                    "W_min_node": r["W_min_node"], "cells": r["cells"], "boxes": r["boxes"],
                    "n_undecided": r["n_undecided"], "witness": r["witness_if_refuted"],
                    "wall_seconds": r["seconds"], "main_cpu_seconds": round(time.process_time() - t0, 1),
                    "sha256_W_vd": r["sha256_W"], "workers": workers})
        row["control_pass"] = row["verdict"] == "PASS" and row["W_at_atom_equals_claim"] and row["W_sha256_ok"]
        doc["rows"][pth.name] = V.jsonable(row)
        print(json.dumps({k: row[k] for k in ("file", "verdict", "direction", "W_at_atom_equals_claim", "boxes",
                                              "wall_seconds")}), flush=True)
        rows = list(doc["rows"].values())
        doc["n"] = len(rows)
        doc["all_pass"] = all(x.get("control_pass") for x in rows)
        OUT.write_text(json.dumps(V.jsonable(doc), indent=1, sort_keys=True) + "\n")
    return doc


if __name__ == "__main__":
    args = list(sys.argv[1:])
    workers = 3
    if "--workers" in args:
        k = args.index("--workers")
        workers = int(args[k + 1])
        del args[k:k + 2]
    Ns = [int(x) for x in args] or [10, 20, 40]
    Q.log_event("streams/VERIFY/vd_d6_verify_pl.py", f"D6(a) independent verification of stream-A0 C2b/C2bx P1 "
                f"certificates (read-only) at their declared drifts, N in {Ns}", klass="NONTARGET_DRIFT_VALIDATION",
                agent="streamD", notes="declared validation drifts 1/2, 1, 11/10, 27/10, 3, 7/2; no cell id")
    d = run(Ns, workers)
    print("ALL_PASS", d.get("all_pass"), "n", d.get("n"))
