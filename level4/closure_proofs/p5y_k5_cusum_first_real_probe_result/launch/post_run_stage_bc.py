"""Stage B/C, run ONLY after the ledger OUTCOME + seal event are committed and published.

B: interpret the sealed record with the frozen consumer.interpret (the only scientific interpreter), and report per m
   the exact L0, U0, M5, transport factor, penalty, L1, U1, verdict, point sign, consequence and consumption key.
C: run the accepted E6 adapter with L1 := L1_m exactly for the m whose frozen consumption key is POSITIVE, and
   L1 := None (-inf) for every other m, as k5b_consumption_map prescribes. Skipped if no m is POSITIVE.
Writes a JSON report to the path given as argv[1] (outside the namespace).
"""
import hashlib
import json
import sys
from decimal import Decimal, getcontext
from fractions import Fraction as F
from pathlib import Path

getcontext().prec = 40
L = Path("/root/work/k5-real-launch-69a162d0")
EX = L / "level4/closure_proofs/p5y_k5_cusum_real_point_executor"
sys.path.insert(0, str(EX / "code"))
import paths  # noqa: E402,F401
import consumer as CO  # noqa: E402
import probe_rules as PR  # noqa: E402

S = Path("/root/work/k5-first-real-probe/slot-1")
raw = (S / "SCIENTIFIC_RECORD_SEALED.json").read_bytes()
rec = json.loads(raw)
res = CO.interpret(rec)
x1 = F(PR.load_prereg()["cell_selection"]["selected"]["x1"])
dec = lambda q: format(Decimal(q.numerator) / Decimal(q.denominator), ".12e")
report = {"sealed_record_sha256": hashlib.sha256(raw).hexdigest(), "scientific_hash": rec.get("scientific_hash"),
          "REAL_PRODUCER_QUALIFICATION": res["REAL_PRODUCER_QUALIFICATION"], "SCIENCE_USABLE": res["SCIENCE_USABLE"],
          "structural_gates": res["gates"], "producer_gates": res["producer_gates"], "per_m": {}}
if res["SCIENCE_USABLE"]:
    for m, v in rec["scientific"]["per_m"].items():
        q = {k: F(x) for k, x in v.items()}
        pen = q["transport_factor"] * q["M5"]
        L1, U1 = PR.transport(q["L0"], q["U0"], q["M5"])
        verdict = res["SCIENTIFIC_PROBE"][m]
        report["per_m"][m] = {
            "exact": {k: str(x) for k, x in q.items()} | {"penalty": str(pen)},
            "decimal": {k: dec(x) for k, x in q.items()} | {"penalty": dec(pen)},
            "transport_factor_equals_x1sq_over_2": q["transport_factor"] == x1 * x1 / 2,
            "sealed_L1U1_equal_frozen_transport": (L1, U1) == (q["L1"], q["U1"]),
            "verdict": verdict["verdict"], "point": verdict["point"], "consequence": verdict["consequence"],
            "consumption_key": PR.consumption_key(verdict["verdict"], verdict["point"])}
    report["aggregate"] = res["aggregate"]
else:
    report["SCIENTIFIC_PROBE"] = res["SCIENTIFIC_PROBE"]

# ------------------------------------------------------------------ C: E6 consumption (POSITIVE m only)
positive = [m for m, v in report["per_m"].items() if v["consumption_key"] == "POSITIVE"]
report["E6"] = {"positive_m": positive}
if positive:
    sys.path.insert(0, str(L / "level4/closure_proofs/p5y_k5b_consumption_adapter/code"))
    import consumption_adapter as AD  # noqa: E402
    assert hashlib.sha256(Path(AD.__file__).read_bytes()).hexdigest() == \
        "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"
    L1map = {m: (F(rec["scientific"]["per_m"][m]["L1"]) if m in positive else None) for m in ("1", "2", "3", "5")}
    out = AD.consume(L1map)
    base = AD.consume(None)
    report["E6"]["result"] = {m: {"pass_ranges": out["per_m"][m]["pass_ranges"], "pass_count": out["per_m"][m]["pass_count"],
                                  "open_ranges": out["per_m"][m]["open_ranges"],
                                  "baseline_L_None_pass_ranges": base["per_m"][m]["pass_ranges"],
                                  "newly_closed": sorted(set(out["per_m"][m]["pass"]) - set(base["per_m"][m]["pass"])),
                                  "rows_sha256": out["per_m"][m]["rows_sha256"]} for m in ("1", "2", "3", "5")}
    report["E6"]["L1"] = out["L1"]
    report["E6"]["adapter_output_sha256"] = hashlib.sha256(AD.canonical(out)).hexdigest()
Path(sys.argv[1]).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
print(json.dumps({k: v for k, v in report.items() if k not in ("structural_gates", "producer_gates")}, indent=1, sort_keys=True))
