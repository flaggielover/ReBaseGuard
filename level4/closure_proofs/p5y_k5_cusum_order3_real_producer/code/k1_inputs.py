"""Fail-closed validation of a CUSUM K1 (Aux5 composite closure) record BEFORE the order-3 producer consumes it.

Standard library plus the frozen stdlib-only Aux4 `hash_v2`. It reads a record's bytes and the committed composite
export manifest and refuses unless every check passes:

    V01 manifest bytes     sha256(COMPOSITE_EXPORT_MANIFEST.json) == 29ad1f9b...
    V02 record bytes       sha256(record) == manifest files["k4_records/aux5_CUSUM_<i>_256.json"]
    V03 scientific hash    frozen hash_v2.record_scientific_hash(record) == record["scientific_content_hash"]
    V04 producer identity  producer_identity_hash == 3692d0fe...
    V05 cell identity      detector CUSUM, cell_index, precision 256, e0 / rho / C_upper == frozen cells.json entry
    V06 detector / m       the m blocks are exactly {1,2,3,5}; each block names the same detector and cell
    V07 midpoint semantics R_interval, D_interval: exact rational endpoints, lo <= hi, mag == max(|lo|,|hi|);
                           e0 is the exact cell midpoint and rho the exact half width
    V08 whole-cell R2      R2_interval exact, lo <= hi; M_R2 == mag(R2_interval) (M_R2 >= sup_cell |R''|)
    V09 obligation status  every m block status PASS
    V10 target gate        target_gate.status PASS and strictly_inside_minus2_2 for EVERY m. Enforced here for every
                           consumed record; the composite closure verdict does not enforce it (PB6 note), so this
                           producer does. Cells in the endpoint region (right endpoint >= 2) are flagged.

Carried note (PB2): K5-B's regularity premise P5X L5 was bound but unreviewed at the premise-binding audit
(10769e07); an independent review was published afterwards at 879792d0 (PASS_WITH_SCOPE_LIMITATION: R only,
qualitative, not independent by agent family). This module neither relies on nor strengthens that review.
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = REPO / "level4/closure_proofs"

EXPORT_MANIFEST = CP / "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json"
EXPORT_MANIFEST_SHA256 = "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334"
K1_PRODUCER_IDENTITY = "3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19"
CELLS = CP / "p5y_k1_cover_ledger_successor/config/cells.json"
M_VALUES = ("1", "2", "3", "5")
PB2_NOTE = ("P5X L5 (K5-B regularity premise): BOUND_WITH_NOTE at 10769e07 (not independently reviewed then); "
            "independent review 879792d0 = PASS_WITH_SCOPE_LIMITATION (R only, qualitative, not agent-family "
            "independent). Not relied on or strengthened by the order-3 producer.")


class K1InputRefused(RuntimeError):
    pass


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _rat(s: str) -> F:
    if not isinstance(s, str) or "." in s or "e" in s.lower():
        raise K1InputRefused(f"inexact field {s!r}")
    return F(s)


def _interval(block: dict, name: str) -> tuple[F, F]:
    iv = block.get(name)
    if not isinstance(iv, dict) or iv.get("encoding") != "outward exact rational endpoints":
        raise K1InputRefused(f"{name}: missing or not an exact outward interval")
    lo, hi, mag = _rat(iv["lo"]), _rat(iv["hi"]), _rat(iv["mag"])
    if not lo <= hi:
        raise K1InputRefused(f"{name}: reversed")
    if mag != max(abs(lo), abs(hi)):
        raise K1InputRefused(f"{name}: mag is not max(|lo|,|hi|)")
    return lo, hi


def frozen_cell(index: int) -> dict:
    cells = [c for c in json.loads(CELLS.read_text()) if c["detector"] == "CUSUM" and c["index"] == index]
    if len(cells) != 1:
        raise K1InputRefused(f"cell {index}: not exactly one frozen CUSUM cell")
    return cells[0]


def validate(record_bytes: bytes, *, cell_index: int, manifest_bytes: bytes | None = None,
             m_values=M_VALUES) -> dict:
    checks: dict = {}
    mb = EXPORT_MANIFEST.read_bytes() if manifest_bytes is None else manifest_bytes
    checks["V01_manifest_bytes"] = _sha(mb) == EXPORT_MANIFEST_SHA256
    if not checks["V01_manifest_bytes"]:
        raise K1InputRefused("V01: export manifest bytes do not match 29ad1f9b")
    manifest = json.loads(mb)
    key = f"k4_records/aux5_CUSUM_{cell_index}_256.json"
    checks["V02_record_bytes"] = manifest["files"].get(key) == _sha(record_bytes)
    if not checks["V02_record_bytes"]:
        raise K1InputRefused(f"V02: record bytes do not match the export manifest entry {key}")
    try:
        rec = json.loads(record_bytes)
    except json.JSONDecodeError as exc:
        raise K1InputRefused(f"malformed record: {exc}") from None

    code = str(CP / "p5y_k1_cusum_aux4_fullcover/code")
    if code not in sys.path:
        sys.path.insert(0, code)
    import hash_v2 as H  # frozen, stdlib-only
    checks["V03_scientific_hash"] = H.record_scientific_hash(rec) == rec.get("scientific_content_hash")
    if not checks["V03_scientific_hash"]:
        raise K1InputRefused("V03: frozen scientific hash does not recompute")
    checks["V04_producer_identity"] = rec.get("producer_identity_hash") == K1_PRODUCER_IDENTITY
    if not checks["V04_producer_identity"]:
        raise K1InputRefused("V04: producer identity is not 3692d0fe")

    fc = frozen_cell(cell_index)
    geom_ok = (rec.get("detector") == "CUSUM" and rec.get("cell_index") == cell_index
               and rec.get("precision_bits") == 256 and rec.get("e0") == fc["e0"] and rec.get("rho") == fc["rho"]
               and rec.get("C_upper") == fc["C_upper"])
    checks["V05_cell_identity"] = geom_ok
    if not geom_ok:
        raise K1InputRefused("V05: cell identity / geometry differs from the frozen cells.json entry")

    blocks = rec.get("m", {})
    if sorted(blocks) != sorted(M_VALUES) or not set(m_values) <= set(blocks):
        raise K1InputRefused(f"V06: m blocks {sorted(blocks)} are not exactly {list(M_VALUES)}")
    for m in M_VALUES:
        if blocks[m].get("detector") != "CUSUM" or blocks[m].get("cell_index") != cell_index:
            raise K1InputRefused(f"V06: m={m} block names another detector or cell")
    checks["V06_detector_m"] = True

    left, right = _rat(fc["left"][0]), _rat(fc["right"][0])
    e0, rho = _rat(fc["e0"][0]), _rat(fc["rho"][0])
    if e0 != (left + right) / 2 or rho != (right - left) / 2:
        raise K1InputRefused("V07: e0 / rho are not the exact midpoint / half width")
    per_m = {}
    for m in M_VALUES:
        b = blocks[m]
        R = _interval(b, "R_interval")
        Dv = _interval(b, "D_interval")
        R2 = _interval(b, "R2_interval")
        if _rat(b["M_R2"]) != max(abs(R2[0]), abs(R2[1])):
            raise K1InputRefused(f"V08: m={m} M_R2 != mag(R2_interval)")
        if b.get("status") != "PASS":
            raise K1InputRefused(f"V09: m={m} obligation status {b.get('status')}")
        tg = b.get("target_gate", {})
        if tg.get("status") != "PASS" or tg.get("strictly_inside_minus2_2") is not True:
            raise K1InputRefused(f"V10: m={m} target_gate not PASS")
        per_m[m] = {"R_interval": [str(x) for x in R], "D_interval": [str(x) for x in Dv],
                    "R2_interval": [str(x) for x in R2], "M_R2": b["M_R2"],
                    "target_gate": {"status": tg["status"], "lo": tg["lo"], "hi": tg["hi"]}}
    checks.update({"V07_midpoint_semantics": True, "V08_whole_cell_R2": True,
                   "V09_obligation_status": True, "V10_target_gate_all_m": True})
    return {"cell_index": cell_index, "record_sha256": _sha(record_bytes),
            "scientific_content_hash": rec["scientific_content_hash"],
            "producer_identity_hash": rec["producer_identity_hash"],
            "export_manifest_sha256": EXPORT_MANIFEST_SHA256,
            "endpoint_region": right >= 2, "left": str(left), "right": str(right),
            "checks": checks, "per_m": per_m, "pb2_note": PB2_NOTE}
