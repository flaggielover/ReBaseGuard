"""C7 shared helpers: repository roots, committed-fact readers, canonical JSON writing.

C7 reads its predecessors READ-ONLY. Nothing in this module writes outside the C7 namespace.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent                                   # .../p5y_k5_tail_c7_e2_lambda309
CLOSURE = NS.parent                                # .../level4/closure_proofs
REPO = CLOSURE.parent.parent                       # worktree root

C4 = CLOSURE / "p5y_k5_tail_c4_exhaustion"
C5 = CLOSURE / "p5y_k5_tail_c5_exhaustion"
C6 = CLOSURE / "p5y_k5_tail_c6_evidence_recovery"
MODEL = CLOSURE / "p5y_k1_cover_ledger_implementation" / "code" / "cusum_layer1.py"

# The pin C4 established and C7 inherits unchanged.
MODEL_SHA256 = "efcc0f36632632577a24c4ddf1a7c2c3579d471cdba5a752dd72c708667cdc79"

CELL = 309
DETECTOR = "CUSUM"
M = 5


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def sha256_obj(o) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def load(p: pathlib.Path):
    return json.loads(p.read_text())


def write_evidence(p: pathlib.Path, obj: dict) -> str:
    """Write canonical JSON with a self-sha over the payload (excluding the sha field itself)."""
    body = {k: v for k, v in obj.items() if k != "sha256"}
    body["sha256"] = sha256_obj(body)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(body, indent=1, sort_keys=True) + "\n")
    return body["sha256"]


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def tracked(relpath: str) -> bool:
    return bool(git("ls-files", "--", relpath))


# -------------------------------------------------------------------------------------------------
# Committed facts C7 is entitled to rely on. Each returns the value AND where it came from, so a
# reviewer can re-derive it without trusting this module.
# -------------------------------------------------------------------------------------------------

def c4_cell309() -> dict:
    cert = load(C4 / "evidence" / "certificate" / "C4_CERTIFICATE.json")
    d = cert["cells"][str(CELL)]
    return {
        "source": "p5y_k5_tail_c4_exhaustion/evidence/certificate/C4_CERTIFICATE.json#/cells/309",
        "e_lo": d["e_lo"], "e_hi": d["e_hi"], "evaluated_at_e": d["evaluated_at_e"],
        "lower_bound_E_a_tau": d["lower_bound_E_a_tau"],
        "lower_bound_float": d["lower_bound_float"],
        "A0_certified_float": d["A0_certified_float"],
        "E_excess_upper": d["E_excess_upper"],
        "critical_A0_frozen_clause": d["critical_A0_reported_only"],
        "slack_over_critical_percent": d["slack_over_critical_percent"],
        "excluded": d["excluded"], "blocker_is_A0": d["blocker_is_A0"],
        "gate_sha256": cert["gate_sha256"],
    }


def c5_critical_a0() -> dict:
    fc = load(C5 / "evidence" / "forecast" / "C5_FORECAST.json")
    blk = fc["c4_exclusion_fragility"]["2_margin_in_C4s_own_currency_critical_A0"]
    return {
        "source": ("p5y_k5_tail_c5_exhaustion/evidence/forecast/C5_FORECAST.json"
                   "#/c4_exclusion_fragility/2_margin_in_C4s_own_currency_critical_A0"),
        "critical_A0_C5T": blk["critical_A0_C5T"],
        "critical_A0_frozen_clause": blk["critical_A0_frozen_clause"],
        "C4_certified_floor_B": blk["C4_certified_floor_B"],
        "slack_percent_C5T": blk["slack_percent_C5T"],
        "slack_percent_frozen": blk["slack_percent_frozen"],
    }
