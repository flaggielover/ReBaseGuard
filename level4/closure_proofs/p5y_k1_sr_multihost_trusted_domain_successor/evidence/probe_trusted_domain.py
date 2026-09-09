"""Self-consistent adversarial probe for the TRUSTED-DOMAIN driver.

Every claim is COMPUTED from the driver under test; nothing is asserted
statically. This replaces the predecessor probe_accounting.py, whose two final
entries hard-coded 'OVERHEAD_FACTOR / CUSUM_CPU_H NOT_VALIDATED' and were stale
once validate_governed_factor existed. Result-free.
"""
import json, sys
sys.path.insert(0, sys.argv[1] + "/driver")
import multihost as M

INF, NAN = float("inf"), float("nan")


def probe(label, fn):
    try:
        r = fn()
        return {"label": label, "outcome": "ADMITTED",
                "charged": r.get("charged_cpu_h") if isinstance(r, dict) else r}
    except M.MultiHostRefusal as e:
        return {"label": label, "outcome": "FAIL_CLOSED", "refusal": str(e)[:100]}
    except Exception as e:
        return {"label": label, "outcome": "RAW_EXCEPTION_LEAKED",
                "err": f"{type(e).__name__}: {e}"[:100]}


def guarded(name):
    """COMPUTED, not asserted: does the driver actually validate this operand?"""
    fn = getattr(M, name, None)
    if fn is None:
        return {"validator_present": False}
    checks = {}
    for label, bad in (("nan", NAN), ("pos_inf", INF), ("neg_inf", -INF),
                       ("bool", True), ("str", "1"), ("none", None),
                       ("huge_int", 10 ** 400)):
        try:
            fn(bad, "probe") if name != "validate_governed_cap" else fn(bad, "probe", expect=None)
            checks[label] = "ADMITTED"
        except M.MultiHostRefusal:
            checks[label] = "FAIL_CLOSED"
        except Exception as e:
            checks[label] = f"RAW_EXCEPTION_LEAKED:{type(e).__name__}"
    return {"validator_present": True, "checks": checks,
            "all_fail_closed": all(v == "FAIL_CLOSED" for v in checks.values())}


res = {"validators_measured": {n: guarded(n) for n in
       ("validate_governed_cost", "validate_governed_factor", "validate_governed_cap")}}
cases = [
    probe("overhead=NaN sr=5000", lambda: M.gate_global_cap({"AWS": 5000.0}, NAN)),
    probe("overhead=-inf sr=5000", lambda: M.gate_global_cap({"AWS": 5000.0}, -INF)),
    probe("overhead=-5000 sr=5000", lambda: M.gate_global_cap({"AWS": 5000.0}, -5000.0)),
    probe("huge int cpu-h 10**400", lambda: M.gate_global_cap({"AWS": 10 ** 400}, 0.0)),
    probe("valid campaign", lambda: M.gate_global_cap({"AWS": 100.0}, 0.0)),
]
res["cases"] = cases
res["no_raw_exception_leaked"] = not any(
    c["outcome"] == "RAW_EXCEPTION_LEAKED" for c in cases)
print(json.dumps(res, indent=1, sort_keys=True))
