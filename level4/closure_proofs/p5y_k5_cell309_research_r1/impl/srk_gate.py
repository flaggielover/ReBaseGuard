"""SRK certificate gate (review R1 blocker B2): the ONLY path from certificates to the cell-level Gamma-bar_i.

gate(cell, geometry, kernel, certs, verdicts) -> GateResult

A certificate is ADMITTED iff all of:
  G1 schema SRK_CERT/1, status CERTIFIED, sha256 == sha256(canonical body without 'sha256')
  G2 geometry == the requested geometry; kernel field == the requested kernel ('whole' | 'taboo'); the field is
     inside the hashed body (certificates without it are refused: pre-B5 certificates cannot pass the gate)
  G3 weight_block == the outward dyadic hull of the cell (srk_certify.cell_blocks), exactly
  G4 block == one of the cell's declared check sub-blocks, exactly; e_c == the block midpoint
  G5 the independent verifier's verdict for THIS sha256 is ACCEPT (verdicts: {sha256: 'ACCEPT'|'REJECT'|'REFUSE'})
  G6 Gamma is a nonnegative rational
Then Gamma_{i,b} = min over admitted certificates for (i, b), and Gamma-bar_i = max_b Gamma_{i,b} if EVERY declared
sub-block b has at least one admitted certificate for index i; otherwise Gamma-bar_i = None (+infinity: the consumer's
min falls back to the TC-T term, THEOREM_SRK section 3).  Every refusal is reported with its reason.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F

import srk_certify as S


class GateResult:
    __slots__ = ("gamma", "report", "source")

    def __init__(self, gamma: dict, report: dict, source: str):
        self.gamma = dict(gamma)
        self.report = report
        self.source = source            # "GATE" (from certificates) or "EMPTY" (all None: reproduction gate)

    @classmethod
    def empty(cls):
        return cls({i: None for i in (1, 2, 3, 4)}, {"note": "all None (reproduction gate)"}, "EMPTY")


def canonical_sha(cert: dict) -> str:
    body = {k: v for k, v in cert.items() if k != "sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def _fr(x) -> F:
    if not isinstance(x, str):
        raise ValueError("rational fields must be strings 'p/q'")
    return F(x)


def gate(cell_lo, cell_hi, geometry: dict, kernel: str, certs: list, verdicts: dict,
         indices=(1, 2, 3, 4)) -> GateResult:
    if kernel not in ("whole", "taboo"):
        raise ValueError("kernel must be 'whole' or 'taboo'")
    wb, subs = S.cell_blocks(F(cell_lo), F(cell_hi))
    subs_key = {(a, b) for a, b in subs}
    admitted: dict = {}
    refused = []
    for c in certs:
        why = None
        try:
            if not isinstance(c, dict):
                why = "not an object"
            elif c.get("schema") != "SRK_CERT/1" or c.get("status") != "CERTIFIED":
                why = "schema/status"
            elif c.get("sha256") != canonical_sha(c):
                why = "sha256 mismatch"
            elif c.get("geometry") != geometry:
                why = "geometry mismatch"
            elif "kernel" not in c:
                why = "kernel not in hashed body (pre-B5 certificate)"
            elif c["kernel"] != kernel:
                why = f"kernel {c['kernel']} != requested {kernel}"
            else:
                w = tuple(_fr(x) for x in c["weight_block"])
                blk = tuple(_fr(x) for x in c["block"])
                if w != wb:
                    why = "weight_block is not the cell's outward dyadic hull"
                elif blk not in subs_key:
                    why = "block is not a declared check sub-block of the cell"
                elif _fr(c["e_c"]) != (blk[0] + blk[1]) / 2:
                    why = "e_c is not the block midpoint"
                elif verdicts.get(c["sha256"]) != "ACCEPT":
                    why = f"independent verifier verdict {verdicts.get(c['sha256'])!r} != 'ACCEPT'"
                else:
                    gm = _fr(c["Gamma"])
                    i = int(c["hermite_index"])
                    if gm < 0:
                        why = "negative Gamma"
                    elif i not in indices:
                        why = "index not requested"
                    else:
                        key = (i, blk)
                        admitted[key] = gm if key not in admitted else min(admitted[key], gm)
        except (KeyError, ValueError, TypeError, ZeroDivisionError) as exc:
            why = f"malformed: {exc}"
        if why:
            refused.append({"sha256": c.get("sha256") if isinstance(c, dict) else None, "reason": why})
    gamma = {}
    for i in indices:
        per = [admitted.get((i, b)) for b in subs]
        gamma[i] = None if any(v is None for v in per) else max(per)
    report = {"weight_block": [S.fstr(x) for x in wb], "sub_blocks": [[S.fstr(a), S.fstr(b)] for a, b in subs],
              "admitted": {f"{i}@[{S.fstr(b[0])},{S.fstr(b[1])}]": S.fstr(v) for (i, b), v in sorted(admitted.items())},
              "refused": refused,
              "gamma": {i: (S.fstr(v) if v is not None else None) for i, v in gamma.items()}}
    return GateResult(gamma, report, "GATE")
