"""Sign-independent qualification gates of a sealed executor record (EXECUTOR_SPEC.md section 1).

STRUCTURAL RULE (tested): this module never calls a verdict function. From the protocol rules it may use only
`scientific_address` and `load_prereg`. Every predicate is invariant under the negation map
    (L0, U0, L1, U1) -> (-U0, -L0, -U1, -L1)   with M5 and all magnitudes unchanged,
so a positive, inconclusive or negative certificate qualifies identically.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F

import paths  # noqa: F401

import probe_rules as PR  # noqa: E402

ALLOWED_PROTOCOL_ATTRIBUTES = ("scientific_address", "load_prereg")
LEAVES = ("L0", "U0", "M5", "transport_factor", "L1", "U1")
M_SET = [1, 2, 3, 5]


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _frac(s):
    if not isinstance(s, str) or "." in s or "e" in s.lower():
        raise ValueError(f"not an exact rational string: {s!r}")
    return F(s)


def gates(record: dict, *, science_file_sha256: str) -> dict:
    g = {}
    s = record.get("scientific", {}) if isinstance(record, dict) else {}
    p = PR.load_prereg()
    try:
        ctx, b, per_m, it = s["context"], s["binding"], s["per_m"], s["intermediates"]
        g["QE01_SCHEMA"] = set(s) >= {"schema", "binding", "context", "backend", "guard", "per_m", "addresses",
                                     "intermediates", "producer_qualification"}
    except (KeyError, TypeError):
        return {"QE01_SCHEMA": False}
    g["QE02_BINDING"] = (b.get("adapter") in ("RealInputAdapter", "ManufacturedInputAdapter") and b.get("redacted") is True
                         and b.get("kind") in ("real", "manufactured") and b.get("left") == "0/1"
                         and b.get("k1_cell_index") == 0)
    try:
        x1 = _frac(ctx["x1"])
        g["QE03_CONTEXT"] = (ctx["m_set"] == M_SET and ctx["point_e"] == "0/1" and ctx["theorem_cell"] == "C_1"
                             and x1 == _frac(b["right"]) and x1 > 0 and ctx["precision_bits"] == 256
                             and ctx["observed_precision_bits"] == 256)
    except (KeyError, ValueError):
        g["QE03_CONTEXT"] = False
        x1 = None
    g["QE04_IDENTITIES"] = (ctx.get("producer_identity_sha256") == p["producer_identity_sha256"]
                            and ctx.get("protocol_sha256") == science_file_sha256
                            and ctx.get("runtime_identity_sha256") == p["host_runtime_identity_sha256"])
    # r2: the DENY guard is a qualification-harness check, not a consumer condition (QE05 removed). QE05 now checks that
    # the preregistered producer-qualification gate set is present with admissible evaluation modes: a record whose
    # binding kind is real must carry REAL evaluations only; harness analogues are admissible only for manufactured input.
    pq = s.get("producer_qualification") if isinstance(s.get("producer_qualification"), dict) else {}
    ids = sorted(x["id"] for x in p["real_producer_qualification"]["gates"])
    modes = pq.get("modes") if isinstance(pq.get("modes"), dict) else None
    allowed = {"REAL"} if b.get("kind") == "real" else {"MANUFACTURED", "HARNESS_ANALOGUE", "NOT_APPLICABLE_MANUFACTURED"}
    g["QE05_PRODUCER_GATES_AND_MODES"] = (isinstance(pq.get("gates"), dict) and sorted(pq["gates"]) == ids
                                          and all(isinstance(v, bool) for v in pq["gates"].values())
                                          and modes is not None and bool(modes) and set(modes.values()) <= allowed)
    try:
        vals = {int(m): {k: _frac(v[k]) for k in LEAVES} for m, v in per_m.items()}
        g["QE06_EXACT_RATIONALS"] = sorted(vals) == M_SET and all(set(per_m[str(m)]) == set(LEAVES) for m in M_SET)
    except (KeyError, ValueError, TypeError):
        vals, g["QE06_EXACT_RATIONALS"] = {}, False
    g["QE07_INTERVAL_CONSISTENCY"] = bool(vals) and all(
        v["L0"] <= v["U0"] and v["M5"] >= 0 and v["L1"] <= v["L0"] and v["U0"] <= v["U1"] for v in vals.values())
    g["QE08_TRANSPORT_EXACT"] = bool(vals) and x1 is not None and all(
        v["transport_factor"] == x1 * x1 / 2 and v["L1"] == v["L0"] - v["transport_factor"] * v["M5"]
        and v["U1"] == v["U0"] + v["transport_factor"] * v["M5"] for v in vals.values())
    try:
        recomputed = {str(m): PR.scientific_address(m=m, k1_record_sha256=b["record_sha256"],
                                                    producer_identity_sha256=ctx["producer_identity_sha256"],
                                                    executor_binding_sha256=ctx["executor_binding_sha256"],
                                                    protocol_sha256=ctx["protocol_sha256"],
                                                    precision_bits=ctx["precision_bits"]) for m in M_SET}
        g["QE09_ADDRESSES"] = (recomputed == s["addresses"]
                               and len({a["address_sha256"] for a in recomputed.values()}) == len(M_SET))
    except Exception:
        g["QE09_ADDRESSES"] = False
    try:
        tri_ok = all(_frac(e) <= _frac(t) and _frac(o) <= _frac(t)
                     for table in ("point_nodes", "local_anchors", "tower_nodes") for e, o, t in it[table].values())
        present = (all(k in it["constants"] for k in ("C_point", "C_hull", "C_e0", "C_o0"))
                   and all(f"F:{r}:3" in it["point_nodes"] and f"F:{r}:5" in it["tower_nodes"] for r in range(5))
                   and bool(it["local_anchors"]) and bool(it["M5_trace_m1"]))
        g["QE10_CERTIFICATE_CHAIN"] = tri_ok and present
    except (KeyError, ValueError, TypeError):
        g["QE10_CERTIFICATE_CHAIN"] = False
    try:
        import rung3_engine as R1E
        ok = True
        for m in M_SET:
            bound = sum((abs(c) * _frac((it["tower_nodes"][f"F:{r}:5"] if kind == "F" else it["tower_nodes"][f"W:{r}:{j}:5"])[0])
                         for kind, r, j, c in R1E.coefficients(m)), F(0))
            M5 = vals[m]["M5"]
            ok = ok and bound * (1 - F(1, 2 ** 100)) <= M5 <= bound * (1 + F(1, 2 ** 100)) + F(1, 2 ** 200)
        g["QE11_M5_FROM_EVEN_TOWER"] = bool(vals) and ok
    except Exception:
        g["QE11_M5_FROM_EVEN_TOWER"] = False
    g["QE12_SCIENTIFIC_HASH"] = record.get("scientific_hash") == hashlib.sha256(_canonical(s)).hexdigest()
    return g


def negated(record: dict) -> dict:
    """The negation map of the module docstring (with the scientific hash recomputed)."""
    r = json.loads(json.dumps(record))
    for v in r["scientific"]["per_m"].values():
        L0, U0, L1, U1 = (F(v[k]) for k in ("L0", "U0", "L1", "U1"))
        for k, x in (("L0", -U0), ("U0", -L0), ("L1", -U1), ("U1", -L1)):
            v[k] = f"{x.numerator}/{x.denominator}"
    r["scientific_hash"] = hashlib.sha256(_canonical(r["scientific"])).hexdigest()
    return r
