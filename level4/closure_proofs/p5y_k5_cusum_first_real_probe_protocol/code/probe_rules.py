"""Pure, stdlib-only frozen rules of the first governed real CUSUM signed-R''' probe, r3 (no flint, no kernel, no I/O
besides reading the frozen preregistration). Fixed BEFORE any real result exists; unit-tested on hypothetical inputs.

    transport(L0, U0, M5)              -> (L1, U1)   Strategy-B enclosure of R''' over C_1 = [0, x1], x1 from the prereg
    scientific_verdict(L1, U1)         -> SUPPORTS_K5B_FIRST_CELL | INCONCLUSIVE | CONTRADICTS_REQUIRED_POSITIVE_SIGN
    point_sign(L0, U0)                 -> POINT_POSITIVE | POINT_UNDETERMINED | POINT_NEGATIVE
    h3a_consequence(verdict, point)    -> per-(CUSUM, m) consequence (Lemma K5-L, K5-B bridge)
    consumption_key(verdict, point)    -> POSITIVE | INCONCLUSIVE | NEGATIVE | VOID   (keyed on the consequence)
    k5b_consumption(verdict, point)    -> the frozen K5-B consumption entry
    aggregate(per_m)                   -> CUSUM-level consequence and route
    scientific_address(...)            -> per-m address (NO attempt id) + sha256;  slot_dir(n)
    failure_class(evidence)            -> failure class derived mechanically from supervisor evidence
    producer_qualification(gates)      -> PASS | FAIL (sign independent);  science_usable(gates)
    retry_decision(state)              -> NOT_AN_ATTEMPT_RELAUNCH_AFTER_VERIFIER | RETRY_PERMITTED | NO_RETRY
    adoption_status(...)               -> ADOPTED | PENDING_INDEPENDENT_ADJUDICATION | NOT_ADOPTABLE
    next_rung(completed)               -> 256 | None
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
PREREG = NS / "protocol/SCIENCE_PREREGISTRATION_R3.json"

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
    if isinstance(x, (int, str)) and not isinstance(x, bool):
        return F(x)
    raise RuleViolation(f"exact rational required, got {type(x).__name__}")      # floats are refused


# ------------------------------------------------------------------ scientific objects and verdicts
def transport(L0, U0, M5, x1=None):
    """R odd => R''' even, R''''(0) = 0 => |R'''(e) - R'''(0)| <= (e^2/2) sup_[0,e] |R^(5)| on [0, x1]."""
    frozen = _q(load_prereg()["cell_selection"]["selected"]["x1"])
    if x1 is not None and _q(x1) != frozen:
        raise RuleViolation("x1 differs from the preregistered cell")
    L0, U0, M5 = _q(L0), _q(U0), _q(M5)
    if L0 > U0:
        raise RuleViolation("point interval has lo > hi")
    if M5 < 0:
        raise RuleViolation("M5 must be >= 0")
    pen = frozen * frozen / 2 * M5
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
    """Lemma K5-L (K5_TARGET_AND_THIRD_ORDER.md lines 46, 50-52): certified R'''(0) < 0 => a3 < 0 => H3a false."""
    if verdict == VOID:
        return "NO_SCIENTIFIC_CONSEQUENCE"
    if verdict == CONTRADICTS or point == "POINT_NEGATIVE":
        return "H3A_FALSE_FOR_THIS_M"
    if verdict == SUPPORTS:
        return "K5B_CELL_1_PASSES_FOR_THIS_M"
    return "K5B_CELL_1_UNRESOLVED_FOR_THIS_M"


def consumption_key(verdict: str, point: str) -> str:
    return {"NO_SCIENTIFIC_CONSEQUENCE": "VOID", "H3A_FALSE_FOR_THIS_M": "NEGATIVE",
            "K5B_CELL_1_PASSES_FOR_THIS_M": "POSITIVE",
            "K5B_CELL_1_UNRESOLVED_FOR_THIS_M": "INCONCLUSIVE"}[h3a_consequence(verdict, point)]


def k5b_consumption(verdict: str, point: str) -> dict:
    return load_prereg()["k5b_consumption_map"][consumption_key(verdict, point)]


def aggregate(per_m: dict) -> dict:
    prereg = load_prereg()
    per_m = {int(m): v for m, v in per_m.items()}
    ms = sorted(per_m)
    if ms != sorted(prereg["m_values"]["set"]):
        raise RuleViolation(f"per-m verdicts {ms} are not exactly the frozen m set")
    cons = {m: h3a_consequence(per_m[m]["verdict"], per_m[m]["point"]) for m in ms}
    vals = set(cons.values())
    routes = prereg["aggregate_routes"]
    if "NO_SCIENTIFIC_CONSEQUENCE" in vals and vals != {"NO_SCIENTIFIC_CONSEQUENCE"}:
        raise RuleViolation("VOID applies to the whole sealed record (all m share one run); mixed VOID is refused")
    if "NO_SCIENTIFIC_CONSEQUENCE" in vals:
        label = "VOID"
    elif "H3A_FALSE_FOR_THIS_M" in vals:
        label = "CUSUM_H3A_TARGET_REFUTED_FOR_SOME_M"
    elif vals == {"K5B_CELL_1_PASSES_FOR_THIS_M"}:
        label = "FIRST_CELL_SUPPORTED_ALL_M"
    elif "K5B_CELL_1_PASSES_FOR_THIS_M" in vals:
        label = "FIRST_CELL_SUPPORTED_SOME_M_UNRESOLVED_OTHERS"
    else:
        label = "FIRST_CELL_UNRESOLVED_ALL_M"
    return {"per_m": {str(m): cons[m] for m in ms}, "label": label, "route": routes[label]}


# ------------------------------------------------------------------ address, attempts, qualification, retry, adoption
def scientific_address(*, m: int, k1_record_sha256: str, producer_identity_sha256: str, executor_binding_sha256: str,
                       protocol_sha256: str, precision_bits: int) -> dict:
    prereg = load_prereg()
    schema, cell = prereg["scientific_address"], prereg["cell_selection"]["selected"]
    if m not in prereg["m_values"]["set"]:
        raise RuleViolation(f"m={m} outside the frozen m set")
    if precision_bits not in prereg["precision_ladder"]["bits"]:
        raise RuleViolation(f"precision {precision_bits} is not a frozen rung")
    addr = {"schema": schema["schema"], "detector": "CUSUM", "k": "1/2", "h": "5", "m": m, "theorem_cell": "C_1",
            "k1_cell_index": cell["k1_cell_index"], "left": cell["left"], "right": cell["right"], "point_e": cell["point_e"],
            "object": prereg["scientific_object"]["primary"]["name"], "k1_record_sha256": k1_record_sha256,
            "producer_identity_sha256": producer_identity_sha256, "executor_binding_sha256": executor_binding_sha256,
            "protocol_sha256": protocol_sha256, "precision_bits": precision_bits}
    if sorted(addr) != sorted(schema["fields"]):
        raise RuleViolation("address fields differ from the frozen schema")
    return {"address": addr, "address_sha256": sha256(canonical(addr))}


def slot_dir(n: int) -> str:
    rp = load_prereg()["retry_policy"]
    if not 1 <= n <= rp["max_slots"]:
        raise RuleViolation(f"slot {n} outside 1..{rp['max_slots']}")
    return f"slot-{n}"


def failure_class(evidence: dict) -> str:
    """Mechanical derivation from the SUPERVISOR's evidence (never self-declared by the executor), frozen order.
    evidence keys: boot_id_changed, wall_timeout, signal (int|None), cpu_soft_limit_reached, kernel_oom_record,
    enospc, integrity_refusal (str|None), exit_code (int|None)."""
    e = evidence or {}
    if e.get("boot_id_changed") is True:
        return "HOST_REBOOT_OR_BOOT_ID_CHANGE"
    if e.get("wall_timeout") is True:
        return "WALL_TIMEOUT"
    if e.get("signal") == 24 or e.get("cpu_soft_limit_reached") is True:
        return "CPU_RLIMIT"
    if e.get("integrity_refusal"):
        return "INTEGRITY_REFUSAL"
    if e.get("signal") == 9 and e.get("kernel_oom_record") is True:
        return "PROCESS_KILLED_OOM"
    if e.get("signal") in (1, 2, 9, 15) and e.get("kernel_oom_record") is not True:
        return "PROCESS_KILLED_BY_EXTERNAL_SIGNAL"
    if e.get("enospc") is True:
        return "DISK_FULL_BEFORE_SEAL"
    if e.get("exit_code") == 0 and e.get("signal") is None:
        return "COMPLETED"
    return "UNKNOWN_FAILURE"


def producer_qualification(gates: dict) -> str:
    ids = [g["id"] for g in load_prereg()["real_producer_qualification"]["gates"]]
    if sorted(gates) != sorted(ids):
        raise RuleViolation("qualification gate set differs from the frozen set")
    return "PASS" if all(gates[i] is True for i in ids) else "FAIL"


def science_usable(gates: dict) -> bool:
    return all(gates.get(i) is True for i in load_prereg()["real_producer_qualification"]["science_requires"])


def retry_decision(state: dict) -> dict:
    """state: {"arithmetic_started": bool, "sealed_record_exists": bool, "failure_class": str | None, "attempts_started": int}.
    An attempt starts at the ARITHMETIC_STARTED event; refusals before it are not attempts."""
    rp = load_prereg()["retry_policy"]
    if state["sealed_record_exists"]:
        return {"decision": "NO_RETRY", "reason": "a sealed record (scientific or VOID) exists and is final"}
    if not state["arithmetic_started"]:
        return {"decision": "NOT_AN_ATTEMPT_RELAUNCH_AFTER_VERIFIER",
                "reason": "refused before arithmetic; relaunch only after the prelaunch verifier permits again"}
    if state["attempts_started"] >= rp["max_attempts"]:
        return {"decision": "NO_RETRY", "reason": "maximum attempts reached"}
    if state.get("failure_class") in rp["transient_failure_classes_after_arithmetic"]:
        return {"decision": "RETRY_PERMITTED", "reason": state["failure_class"]}
    return {"decision": "NO_RETRY", "reason": f"failure class {state.get('failure_class')} is not transient"}


def adoption_status(*, sealed: bool, science_usable_: bool, independent_replay_pass: bool | None,
                    independent_review_pass: bool | None) -> str:
    if not sealed or not science_usable_:
        return "NOT_ADOPTABLE"
    if independent_replay_pass is True and independent_review_pass is True:
        return "ADOPTED"
    if independent_replay_pass is False or independent_review_pass is False:
        return "NOT_ADOPTABLE"
    return "PENDING_INDEPENDENT_ADJUDICATION"


def next_rung(completed_bits: list[int]) -> int | None:
    pl = load_prereg()["precision_ladder"]
    if not completed_bits:
        return pl["bits"][0]
    if completed_bits != pl["bits"][:len(completed_bits)]:
        raise RuleViolation("rungs out of the frozen order")
    if not pl["escalation_allowed"]:
        return None
    return pl["bits"][len(completed_bits)] if len(completed_bits) < len(pl["bits"]) else None
