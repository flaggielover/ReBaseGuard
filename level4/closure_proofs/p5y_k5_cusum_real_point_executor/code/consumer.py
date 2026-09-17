"""The separate frozen consumer: the ONLY place where a sealed executor record is interpreted scientifically.

    interpret(record) -> {"REAL_PRODUCER_QUALIFICATION": PASS|FAIL, "gates": {...},
                          "SCIENTIFIC_PROBE": {m: {verdict, point_sign, consequence}} | VOID, "aggregate": ...}

Order: qualification gates first (sign independent: the executor's sealed Q01..Q16 through the frozen
probe_rules.producer_qualification / science_usable, plus the structural checks of qualification_gates.py); the
scientific verdicts of the frozen preregistration are computed only from a record that is science usable, otherwise VOID.
The executor never imports this module.
"""
from __future__ import annotations

import hashlib
from fractions import Fraction as F

import paths

import probe_rules as PR  # noqa: E402
import qualification_gates as QG  # noqa: E402

SCIENCE_FILE = paths.PROTOCOL_NS / "protocol/SCIENCE_PREREGISTRATION_R4.json"


def interpret(record: dict) -> dict:
    """r2: REAL_PRODUCER_QUALIFICATION = frozen probe_rules.producer_qualification over the sealed Q01..Q16 gates AND the
    sign-independent structural checks QE01..QE12; the probe is scientifically usable only if the frozen
    probe_rules.science_usable holds AND the structural checks pass. Otherwise VOID."""
    g = QG.gates(record, science_file_sha256=hashlib.sha256(SCIENCE_FILE.read_bytes()).hexdigest())
    structural = bool(g) and all(g.values())
    try:
        q = record["scientific"]["producer_qualification"]["gates"]
        pq = PR.producer_qualification(q)
        usable = PR.science_usable(q)
    except (KeyError, TypeError, PR.RuleViolation):
        q, pq, usable = {}, "FAIL", False
    qualification = "PASS" if structural and pq == "PASS" else "FAIL"
    out = {"REAL_PRODUCER_QUALIFICATION": qualification, "gates": g, "producer_gates": q,
           "SCIENCE_USABLE": bool(structural and usable)}
    if not out["SCIENCE_USABLE"]:
        out["SCIENTIFIC_PROBE"] = PR.VOID
        return out
    per_m = {}
    for m, v in record["scientific"]["per_m"].items():
        verdict = PR.scientific_verdict(F(v["L1"]), F(v["U1"]))
        point = PR.point_sign(F(v["L0"]), F(v["U0"]))
        per_m[m] = {"verdict": verdict, "point": point, "consequence": PR.h3a_consequence(verdict, point)}
    out["SCIENTIFIC_PROBE"] = per_m
    out["aggregate"] = PR.aggregate({int(m): {"verdict": v["verdict"], "point": v["point"]} for m, v in per_m.items()})
    return out
