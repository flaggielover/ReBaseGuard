"""Pure, stdlib-only frozen rules of the first governed real CUSUM signed-R''' probe (no flint, no kernel, no I/O besides
reading the frozen protocol files). Everything here is fixed BEFORE any real result exists and is unit-tested only on
hypothetical rational inputs.

    transport(L0, U0, M5, x1)          -> (L1, U1)            Strategy-B enclosure of R''' over C_1 = [0, x1]
    scientific_verdict(L1, U1)         -> SUPPORTS_K5B_FIRST_CELL | INCONCLUSIVE | CONTRADICTS_REQUIRED_POSITIVE_SIGN
    point_sign(L0, U0)                 -> POINT_POSITIVE | POINT_UNDETERMINED | POINT_NEGATIVE     (secondary, frozen)
    h3a_consequence(verdict, point)    -> per-(CUSUM, m) consequence under Lemma K5-L and the K5-B bridge
    aggregate(per_m)                   -> CUSUM-level consequence and the frozen successor route
    k5b_consumption(verdict)           -> the frozen K5-B consumption entry for that outcome
    scientific_address(...)            -> per-m canonical address + sha256
    producer_qualification(gates)      -> PASS | FAIL        (sign independent)
    science_usable(gates)              -> bool               (integrity gates only)
    retry_decision(state)              -> RETRY_PERMITTED | NO_RETRY (+ reason)
    next_rung(...)                     -> None               (single frozen rung)
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
PREREG = NS / "protocol/SCIENCE_PREREGISTRATION.json"

SUPPORTS = "SUPPORTS_K5B_FIRST_CELL"
INCONCLUSIVE = "INCONCLUSIVE"
CONTRADICTS = "CONTRADICTS_REQUIRED_POSITIVE_SIGN"
VOID = "VOID_PRODUCER_INTEGRITY_FAILURE"


class RuleViolation(ValueError):
    pass


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_prereg() -> dict:
    return json.loads(PREREG.read_text())


def _q(x) -> F:
    if isinstance(x, F):
        return x
    if isinstance(x, int):
        return F(x)
    if isinstance(x, str):
        return F(x)
    raise RuleViolation(f"exact rational required, got {type(x).__name__}")      # floats are refused


# ------------------------------------------------------------------ scientific objects and verdicts
def transport(L0, U0, M5, x1):
    """R odd => R''' even, R''''(0) = 0 => |R'''(e) - R'''(0)| <= (e^2/2) sup_[0,e] |R^(5)| on [0, x1]."""
    L0, U0, M5, x1 = _q(L0), _q(U0), _q(M5), _q(x1)
    if L0 > U0:
        raise RuleViolation("point interval has lo > hi")
    if M5 < 0 or x1 <= 0:
        raise RuleViolation("M5 must be >= 0 and x1 > 0")
    pen = x1 * x1 / 2 * M5
    return L0 - pen, U0 + pen


def scientific_verdict(L1, U1) -> str:
    L1, U1 = _q(L1), _q(U1)
    if L1 > U1:
        raise RuleViolation("transported interval has lo > hi")
    if L1 > 0:
        return SUPPORTS
    if U1 < 0:
        return CONTRADICTS
    return INCONCLUSIVE                     # L1 <= 0 <= U1, including touching zero; never resolved by midpoints


def point_sign(L0, U0) -> str:
    L0, U0 = _q(L0), _q(U0)
    if L0 > 0:
        return "POINT_POSITIVE"
    if U0 < 0:
        return "POINT_NEGATIVE"
    return "POINT_UNDETERMINED"


def h3a_consequence(verdict: str, point: str) -> str:
    """Lemma K5-L (K5_TARGET_AND_THIRD_ORDER.md): certified R'''(0) < 0 => a3 < 0 => H3a false for that (D, m)."""
    if verdict == VOID:
        return "NO_SCIENTIFIC_CONSEQUENCE"
    if verdict == CONTRADICTS or point == "POINT_NEGATIVE":
        return "H3A_FALSE_FOR_THIS_M"
    if verdict == SUPPORTS:
        return "K5B_CELL_1_PASSES_FOR_THIS_M"
    return "K5B_CELL_1_UNRESOLVED_FOR_THIS_M"


def aggregate(per_m: dict) -> dict:
    """per_m: {m: {"verdict": ..., "point": ...}} for exactly the frozen m set."""
    prereg = load_prereg()
    ms = sorted(int(m) for m in per_m)
    if ms != sorted(prereg["m_values"]["set"]):
        raise RuleViolation(f"per-m verdicts {ms} are not exactly the frozen m set")
    cons = {m: h3a_consequence(per_m[m]["verdict"] if m in per_m else per_m[str(m)]["verdict"],
                               per_m[m]["point"] if m in per_m else per_m[str(m)]["point"]) for m in ms}
    vals = set(cons.values())
    if "NO_SCIENTIFIC_CONSEQUENCE" in vals:
        label, route = "VOID", "NO_SCIENTIFIC_ROUTING (producer integrity failure; successor protocol required)"
    elif "H3A_FALSE_FOR_THIS_M" in vals:
        label, route = "CUSUM_H3A_REFUTED_FOR_SOME_M", "SEEK_ALTERNATE_K5_ROUTE"
    elif vals == {"K5B_CELL_1_PASSES_FOR_THIS_M"}:
        label, route = "FIRST_CELL_SUPPORTED_ALL_M", "CONSUME_IN_FROZEN_K5B_CHECKER_THEN_PREREGISTER_NEXT_ORDER3_CELLS"
    elif "K5B_CELL_1_PASSES_FOR_THIS_M" in vals:
        label, route = "FIRST_CELL_SUPPORTED_SOME_M_UNRESOLVED_OTHERS", \
            "CONSUME_SUPPORTED_M_IN_FROZEN_K5B_CHECKER; UNRESOLVED_M_REQUIRE_NEW_SUCCESSOR_METHOD"
    else:
        label, route = "FIRST_CELL_UNRESOLVED_ALL_M", "NEW_SUCCESSOR_METHOD_REQUIRED (no rerun under this protocol)"
    return {"per_m": {str(m): cons[m] for m in ms}, "label": label, "route": route}


def k5b_consumption(verdict: str) -> dict:
    prereg = load_prereg()
    key = {SUPPORTS: "POSITIVE", INCONCLUSIVE: "INCONCLUSIVE", CONTRADICTS: "NEGATIVE", VOID: "VOID"}[verdict]
    return prereg["k5b_consumption_map"][key]


# ------------------------------------------------------------------ address, qualification, retry, ladder
def scientific_address(*, m: int, cell: dict, k1_record_sha256: str, producer_identity_sha256: str,
                       protocol_sha256: str, precision_bits: int, attempt_id: str) -> dict:
    prereg = load_prereg()
    schema = prereg["scientific_address"]
    if m not in prereg["m_values"]["set"]:
        raise RuleViolation(f"m={m} outside the frozen m set")
    if precision_bits not in prereg["precision_ladder"]["bits"]:
        raise RuleViolation(f"precision {precision_bits} is not a frozen rung")
    addr = {"schema": schema["schema"], "detector": "CUSUM", "k": "1/2", "h": "5", "m": m,
            "theorem_cell": "C_1", "k1_cell_index": cell["k1_cell_index"], "left": cell["left"], "right": cell["right"],
            "point_e": cell["point_e"], "object": prereg["scientific_object"]["primary"]["name"],
            "k1_record_sha256": k1_record_sha256, "producer_identity_sha256": producer_identity_sha256,
            "protocol_sha256": protocol_sha256, "precision_bits": precision_bits, "attempt_id": attempt_id}
    missing = [f for f in schema["fields"] if f not in addr]
    if missing:
        raise RuleViolation(f"address fields missing: {missing}")
    return {"address": addr, "address_sha256": sha256(canonical(addr))}


def producer_qualification(gates: dict) -> str:
    prereg = load_prereg()
    ids = [g["id"] for g in prereg["real_producer_qualification"]["gates"]]
    if sorted(gates) != sorted(ids):
        raise RuleViolation("qualification gate set differs from the frozen set")
    return "PASS" if all(gates[i] is True for i in ids) else "FAIL"


def science_usable(gates: dict) -> bool:
    prereg = load_prereg()
    return all(gates.get(i) is True for i in prereg["real_producer_qualification"]["science_requires"])


def retry_decision(state: dict) -> dict:
    """state: {"sealed_record_exists": bool, "failure_class": str | None, "attempts_started": int}."""
    prereg = load_prereg()
    rp = prereg["retry_policy"]
    if state["sealed_record_exists"]:
        return {"decision": "NO_RETRY", "reason": "a sealed scientific record exists and is final"}
    if state["attempts_started"] >= rp["max_attempts"]:
        return {"decision": "NO_RETRY", "reason": "maximum attempts reached"}
    if state.get("failure_class") in rp["transient_failure_classes"]:
        return {"decision": "RETRY_PERMITTED", "reason": state["failure_class"]}
    return {"decision": "NO_RETRY", "reason": f"failure class {state.get('failure_class')} is not transient"}


def next_rung(completed_bits: list[int]) -> int | None:
    prereg = load_prereg()
    bits = prereg["precision_ladder"]["bits"]
    if not completed_bits:
        return bits[0]
    if completed_bits != bits[:len(completed_bits)]:
        raise RuleViolation("rungs out of the frozen order")
    return None if prereg["precision_ladder"]["escalation_allowed"] is False else (
        bits[len(completed_bits)] if len(completed_bits) < len(bits) else None)
