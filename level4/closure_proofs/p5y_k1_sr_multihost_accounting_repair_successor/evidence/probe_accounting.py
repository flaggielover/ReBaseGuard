"""Read-only adversarial probe of the FROZEN cap-repair driver. Result-free."""
import json, math, sys
sys.path.insert(0, sys.argv[1] + "/driver")
import multihost as M

def probe(label, fn):
    try:
        r = fn()
        return {"label": label, "outcome": "ADMITTED", "charged": r.get("charged_cpu_h")
                if isinstance(r, dict) else r}
    except M.MultiHostRefusal as e:
        return {"label": label, "outcome": "FAIL_CLOSED", "refusal": str(e)[:90]}
    except Exception as e:
        return {"label": label, "outcome": "OTHER_EXCEPTION", "err": f"{type(e).__name__}: {e}"[:90]}

INF, NAN = float("inf"), float("nan")
res = []
# --- named defect: governed_overhead_cpu_h ------------------------------
res.append(probe("overhead=NaN, sr=5000",  lambda: M.gate_global_cap({"AWS": 5000.0}, NAN)))
res.append(probe("overhead=-inf, sr=5000", lambda: M.gate_global_cap({"AWS": 5000.0}, -INF)))
res.append(probe("overhead=-5000, sr=5000",lambda: M.gate_global_cap({"AWS": 5000.0}, -5000.0)))
res.append(probe("overhead=+inf, sr=0",    lambda: M.gate_global_cap({"AWS": 0.0}, INF)))
res.append(probe("overhead=-0.0, sr=0",    lambda: M.gate_global_cap({"AWS": 0.0}, -0.0)))
res.append(probe("overhead='206' (str)",   lambda: M.gate_global_cap({"AWS": 0.0}, "206")))
res.append(probe("overhead=True (bool)",   lambda: M.gate_global_cap({"AWS": 0.0}, True)))
# --- other paths into the aggregate -------------------------------------
res.append(probe("host component NaN",     lambda: M.gate_global_cap({"AWS": NAN})))
res.append(probe("host component -inf",    lambda: M.gate_global_cap({"AWS": -INF})))
res.append(probe("host component negative",lambda: M.gate_global_cap({"AWS": -100.0})))
res.append(probe("host bool True",         lambda: M.gate_global_cap({"AWS": True})))
res.append(probe("sr overflows to +inf",   lambda: M.gate_global_cap({"A": 1e308, "B": 1e308})))
res.append(probe("sr=+inf AND overhead=-inf -> NaN",
                 lambda: M.gate_global_cap({"A": 1e308, "B": 1e308}, -INF)))
# --- reconcile_accounting -----------------------------------------------
def rec(cell, role, cpu_s):
    return {"cell_id": cell, "role": role, "producer_commit": "a"*40,
            "checkpoint_sha256": "c"*64,
            "runtime_contract_hash": M.ROLES[role]["runtime_contract_hash"],
            "scientific_content_hash": "%064x" % cell, "cpu_seconds": cpu_s,
            "obligations_completed": 28, "complete": True}
def inf_reconcile():
    led = {"VULTR": [rec(4, "VULTR", 1e308*3600), rec(9, "VULTR", 1e308*3600)]}
    acct = {"VULTR": {"role": "VULTR", "cells": 2, "cpu_h": INF,
                      "projected_share_cpu_h": 0.0, "variance_cpu_h": 0.0,
                      "over_projected_share": True, "enforcement": "ACCOUNTING_ONLY"}}
    return M.reconcile_accounting(acct, led)
res.append(probe("reconcile inf==inf (abs(inf-inf)=NaN)", inf_reconcile))
# --- module constants ----------------------------------------------------
res.append({"label": "OVERHEAD_FACTOR validated at use?", "outcome": "NOT_VALIDATED",
            "value": M.OVERHEAD_FACTOR})
res.append({"label": "CUSUM_CPU_H validated at use?", "outcome": "NOT_VALIDATED",
            "value": M.CUSUM_CPU_H})
print(json.dumps(res, indent=1))
