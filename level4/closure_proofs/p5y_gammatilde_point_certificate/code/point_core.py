"""Pure, stdlib-only logic of the GammaTilde point certificate: protocol loading, the point cell, the frozen
adjudication rules, the precision ladder, controls and the scientific hash.

Nothing here imports flint or runs arithmetic on the kernel. `point_eval.py` (which does) calls into this module,
and the qualification tests exercise it on manufactured intervals. Every comparison is on exact Fractions.

FROZEN ADJUDICATION (per target m, from the certified enclosure [lo, hi] of R_m'(0)):

    hi <  0            -> CERTIFIED     (GammaTilde_m = 1 - R_m'(0) has lower bound 1 - hi > 1)
    lo >= 0            -> REFUTED       (GammaTilde_m <= 1 - lo <= 1 is certified)
    otherwise          -> INCONCLUSIVE  (the enclosure contains 0 in its interior or touches it from below)

Precedence is exactly that order; a degenerate [0, 0] is REFUTED. Premise: all targets CERTIFIED -> SATISFIED;
any target REFUTED -> REFUTED; otherwise OPEN.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
CP = "level4/closure_proofs/"
PROTOCOL = NS / "protocol/POINT_PROTOCOL.json"
PROTOCOL_HASH = NS / "protocol/POINT_PROTOCOL_HASH"

CERTIFIED, INCONCLUSIVE, REFUTED = "CERTIFIED", "INCONCLUSIVE", "REFUTED"


class ProtocolViolation(RuntimeError):
    """A frozen protocol rule was violated; no scientific statement may be made."""


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(path) -> str:
    return sha256_bytes(Path(path).read_bytes())


# ------------------------------------------------------------------------------------------------ protocol
def load_protocol(path: Path = PROTOCOL, hash_path: Path = PROTOCOL_HASH) -> dict:
    raw = Path(path).read_bytes()
    expect = Path(hash_path).read_text().strip()
    if sha256_bytes(raw) != expect:
        raise ProtocolViolation(f"protocol hash {sha256_bytes(raw)} != frozen {expect}")
    return json.loads(raw)


def wrapper_pin_problems(protocol: dict, root: Path = ROOT) -> list[str]:
    out = []
    for rel, digest in sorted(protocol["wrapper_files"].items()):
        p = root / rel
        if not p.exists():
            out.append(f"wrapper file missing: {rel}")
        elif sha256_file(p) != digest:
            out.append(f"wrapper file changed after freeze: {rel}")
    return out


def source_pin_problems(protocol: dict, root: Path = ROOT) -> list[str]:
    out = []
    for rel, digest in sorted(protocol["source_hashes"].items()):
        p = root / rel
        if not p.exists() or sha256_file(p) != digest:
            out.append(f"bound source differs: {rel}")
    return out


def identity_problems(protocol: dict, live_identity: dict) -> list[str]:
    """The live manifest-v3 identity must equal the frozen K1 CUSUM producer identity, field by field."""
    out = []
    for key, want in sorted(protocol["producer_identity"].items()):
        got = live_identity.get(key)
        if not isinstance(got, str) or len(got) != 64:
            out.append(f"malformed identity field {key}: {got!r}")
        elif got != want:
            out.append(f"identity {key}: live {got} != frozen {want}")
    return out


def require_m_values(protocol: dict, requested) -> tuple[int, ...]:
    frozen = tuple(protocol["m_values"]["evaluated"])
    req = tuple(sorted(int(m) for m in requested))
    if req != tuple(sorted(frozen)):
        raise ProtocolViolation(f"m values {req} != frozen evaluated set {frozen}")
    return req


# ------------------------------------------------------------------------------------------------ geometry
def point_cell(frozen_cell0: dict, point: F) -> dict:
    """A degenerate cell {point}, inheriting the resolvent bound of the frozen cell that contains it.

    `C_upper` of frozen CUSUM cell 0 is a proven bound on ||(I-K_e)^-1|| for every e in [0, 2 e0], evaluated at
    its left endpoint 0. The point must lie in that closed cell.
    """
    if frozen_cell0["detector"] != "CUSUM" or frozen_cell0["index"] != 0:
        raise ProtocolViolation("the resolvent bound must come from frozen CUSUM cell 0")
    left, right = F(frozen_cell0["left"][0]), F(frozen_cell0["right"][0])
    if F(frozen_cell0["left"][1]) or F(frozen_cell0["right"][1]) or left != 0:
        raise ProtocolViolation("frozen cell 0 geometry is not [0, 2 e0]")
    if F(frozen_cell0["C_evaluation"][0]) != 0 or F(frozen_cell0["C_evaluation"][1]) != 0:
        raise ProtocolViolation("cell 0 C_upper was not evaluated at e = 0")
    point = F(point)
    if not left <= point <= right:
        raise ProtocolViolation(f"point {point} outside frozen cell 0 [{left}, {right}]")
    s = f"{point.numerator}/{point.denominator}"
    return {"detector": "CUSUM", "index": f"POINT[{s}]", "e0": [s, "0/1"], "rho": ["0/1", "0/1"],
            "left": [s, "0/1"], "right": [s, "0/1"], "C_upper": frozen_cell0["C_upper"],
            "C_evaluation": frozen_cell0["C_evaluation"], "C_upper_source": "frozen CUSUM cell 0 (contains the point)"}


# ------------------------------------------------------------------------------------------------ adjudication
def adjudicate(lo, hi) -> str:
    lo, hi = F(lo), F(hi)
    if lo > hi:
        raise ProtocolViolation(f"malformed interval [{lo}, {hi}]")
    if hi < 0:
        return CERTIFIED
    if lo >= 0:
        return REFUTED
    return INCONCLUSIVE


def gamma_from_rprime(lo, hi) -> dict:
    lo, hi = F(lo), F(hi)
    g_lo, g_hi = 1 - hi, 1 - lo
    return {"RPRIME0_INTERVAL": [str(lo), str(hi)], "GAMMATILDE_INTERVAL": [str(g_lo), str(g_hi)],
            "MARGIN_ABOVE_1": str(g_lo - 1), "status": adjudicate(lo, hi)}


def premise(statuses: dict) -> str:
    vals = list(statuses.values())
    if vals and all(v == CERTIFIED for v in vals):
        return "SATISFIED"
    if any(v == REFUTED for v in vals):
        return "REFUTED"
    return "OPEN"


def next_rung(protocol: dict, completed: list[dict]) -> int | None:
    """The frozen ladder: the next precision to run, or None to stop.

    `completed` is the ordered list of rung results {"bits": b, "status": {m: status}} already produced.
    Escalate only while some TARGET m is INCONCLUSIVE; stop at the first rung where every target is decisive.
    """
    ladder = list(protocol["precision_ladder"]["bits"])
    targets = [str(m) for m in protocol["m_values"]["targets"]]
    if [c["bits"] for c in completed] != ladder[:len(completed)]:
        raise ProtocolViolation("rungs were not executed in frozen ladder order")
    if not completed:
        return ladder[0]
    last = completed[-1]["status"]
    if all(last[m] in (CERTIFIED, REFUTED) for m in targets):
        return None
    return ladder[len(completed)] if len(completed) < len(ladder) else None


def final_statuses(protocol: dict, completed: list[dict]) -> dict:
    """Per target: the first decisive rung's status. Contradictory decisive statuses are a protocol failure."""
    out = {}
    for m in (str(x) for x in protocol["m_values"]["targets"]):
        decisive = [c["status"][m] for c in completed if c["status"][m] in (CERTIFIED, REFUTED)]
        if len(set(decisive)) > 1:
            raise ProtocolViolation(f"m={m}: contradictory decisive statuses across rungs {decisive}")
        out[m] = decisive[0] if decisive else INCONCLUSIVE
    return out


# ------------------------------------------------------------------------------------------------ controls
def intervals_intersect(a, b) -> bool:
    return max(F(a[0]), F(b[0])) <= min(F(a[1]), F(b[1]))


def control_problems(protocol: dict, rung: dict) -> list[str]:
    """Consistency controls. They can only invalidate a run; they never change a target gate."""
    out = []
    for m, row in sorted(rung["m"].items()):
        R = row["R_interval"]
        if not F(R["lo"]) <= 0 <= F(R["hi"]):
            out.append(f"m={m}: R_m(0) enclosure {R['lo']}..{R['hi']} excludes 0 (R is odd)")
    for m, ref in sorted(protocol["controls"]["gamma_reference_intervals"].items()):
        if m not in rung["m"]:
            out.append(f"control m={m} missing")
            continue
        D = rung["m"][m]["D_interval"]
        gam = (1 - F(D["hi"]), 1 - F(D["lo"]))
        for name, interval in ref.items():
            if not intervals_intersect(gam, interval):
                out.append(f"control m={m}: point GammaTilde {gam} disjoint from {name} {interval}")
    return out


def scientific_hash(scientific: dict) -> str:
    return sha256_bytes(canonical(scientific))
