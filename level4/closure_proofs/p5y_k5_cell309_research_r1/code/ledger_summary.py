"""Summarize the two campaign ledgers (exposure reads and executions) for the handover."""
import json
from collections import Counter
from pathlib import Path

NS = Path(__file__).resolve().parent.parent


def load(name):
    p = NS / "ledger" / name
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def main():
    exp = load("EXPOSURE_LEDGER.jsonl")
    exe = load("ZERO_TARGET_LEDGER.jsonl")
    by_reader = Counter(r["reader"] for r in exp)
    with_nums = Counter(r["reader"] for r in exp if r["carried_309_numeric_values"])
    out = {"exposure_rows": len(exp), "exposure_by_reader": dict(by_reader),
           "rows_with_305_309_numbers_by_reader": dict(with_nums),
           "execution_rows": len(exe), "execution_classes": dict(Counter(r["class"] for r in exe)),
           "new_target_evaluations": sum(r["new_target_evaluations"] for r in exe),
           "target_equivalent_proxies_executed": sum(r["target_equivalent_proxies"] for r in exe),
           "target_informed_optimisation": sum(r["target_informed_optimisation"] for r in exe),
           "drifts_used_real_kernel": sorted({tuple(d) for r in exe for d in r.get("drifts", [])})}
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    main()
