"""Host-only plumbing smoke test (vultr-02, K1 records present). NO scientific content: a placeholder TEXT_RESULT on the
real geometry with every M_n = 10^30, so Lambda = -10^30 (an order-3 channel equivalent to None) and the M2 tightening
is vacuous. Then C1 and C2 must reproduce the adopted E6 pass sets exactly and the independent X-B must pass.

    python -B tests/host_smoke_consume.py
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[3]
sys.path.insert(0, str(NS / "code"))
import text_consume as TC  # noqa: E402
import text_crosscheck as TX  # noqa: E402

BIG = F(10) ** 30
cells = sorted((c for c in json.loads((REPO / "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json")
                                       .read_text()) if c["detector"] == "CUSUM"), key=lambda c: c["index"])
per = json.loads((REPO / TC.SEALED).read_text())["scientific"]["per_m"]
rows = [{"cell": k, "x_lo": str(F(cells[k]["left"][0])), "x_hi": str(F(cells[k]["right"][0])),
         "M": {str(n): {m: str(BIG) for m in TC.MS} for n in (2, 3, 4, 5)}} for k in range(0, 41)]
for r in rows[1:]:
    X = F(r["x_hi"])
    r["Lambda"] = {m: str(max(F(per[m]["L0"]) - sum((BIG * ((X - F(q["x_lo"])) ** 2 - (X - F(q["x_hi"])) ** 2) / 2
                                                     for q in rows[:r["cell"] + 1]), F(0)), -BIG)) for m in TC.MS}
text = {"rows": rows, "channel_cells": list(range(1, 41)), "sealed_record_sha256": TC.SEALED_SHA256,
        "sealed_L1": {m: per[m]["L1"] for m in TC.MS}, "L0": {m: per[m]["L0"] for m in TC.MS}}
tmp = Path(tempfile.mkdtemp(prefix="text-smoke-", dir="/var/tmp"))
tp = tmp / "PLACEHOLDER_TEXT_RESULT.json"
tp.write_text(json.dumps(text))
sha = hashlib.sha256(tp.read_bytes()).hexdigest()
res = TC.consume(tp, sha, Path("/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records"))
cp = tmp / "CONS.json"
cp.write_text(json.dumps(res))
e6 = json.loads((REPO / "level4/closure_proofs/p5y_k5_cusum_first_real_probe_result/consumption/"
                        "E6_POSITIVE_CONSUMPTION_OUTPUT.json").read_text())
ok_e6 = all(res["consumptions"][v][m]["pass_ranges"] == e6["per_m"][m]["pass_ranges"] for v in ("C1", "C2") for m in TC.MS)
xb = TX.consumption(tp, cp, Path("/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records"))
print("C1/C2 equal E6:", ok_e6, "X-B:", xb["pass"], xb["problems"][:3])
sys.exit(0 if ok_e6 and xb["pass"] else 1)
