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

Taboo kernel (SRK-T, Lemma SV-T): a taboo certificate bounds (G^_e kbar)(a), NOT (R_e kbar)(a) = (G^_e kbar)(a)/D_e, and
D_e <= 1.  A taboo gate therefore REQUIRES d_lo = {"value": "p/q" > 0, "domain": ["lo", "hi"]}, a certified lower bound
D_e >= value for every e in domain, with domain containing the cell C (only e in C is used: V_e(a) is e-affine on each
sub-block, so its max over C ∩ b is at most the max at b's endpoints).  It returns Gamma-hat_i = max_b Gamma_{i,b} / value.
Without d_lo a taboo gate REFUSES (review R2 prep: the raw taboo value would under-bound R_e).
combine(a, b) = the index-wise min of two GateResults (both valid bounds; None = +infinity).
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


def _d_lo(d_lo, cell_lo, cell_hi) -> F:
    if not isinstance(d_lo, dict) or set(d_lo) != {"value", "domain"}:
        raise ValueError("taboo gate requires d_lo = {'value': 'p/q', 'domain': ['lo', 'hi']}")
    v = _fr(d_lo["value"])
    lo, hi = (_fr(x) for x in d_lo["domain"])
    if not v > 0:
        raise ValueError("D_lo must be a positive rational")
    if not (lo <= F(cell_lo) and F(cell_hi) <= hi):
        raise ValueError("D_lo validity domain does not contain the cell")
    return v


def gate(cell_lo, cell_hi, geometry: dict, kernel: str, certs: list, verdicts: dict,
         indices=(1, 2, 3, 4), d_lo=None) -> GateResult:
    if kernel not in ("whole", "taboo"):
        raise ValueError("kernel must be 'whole' or 'taboo'")
    if kernel == "taboo":
        dl = _d_lo(d_lo, cell_lo, cell_hi)
    elif d_lo is not None:
        raise ValueError("d_lo applies to the taboo kernel only")
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
        gamma[i] = None if any(v is None for v in per) else (max(per) if kernel == "whole" else max(per) / dl)
    report = {"weight_block": [S.fstr(x) for x in wb], "sub_blocks": [[S.fstr(a), S.fstr(b)] for a, b in subs],
              "admitted": {f"{i}@[{S.fstr(b[0])},{S.fstr(b[1])}]": S.fstr(v) for (i, b), v in sorted(admitted.items())},
              "refused": refused,
              "gamma": {i: (S.fstr(v) if v is not None else None) for i, v in gamma.items()}, "kernel": kernel,
              "d_lo": None if kernel == "whole" else {"value": S.fstr(dl), "domain": list(d_lo["domain"])}}
    return GateResult(gamma, report, "GATE" if kernel == "whole" else "GATE_TABOO")


def combine(a: GateResult, b: GateResult) -> GateResult:
    """index-wise min of two gate results (THEOREM_SRK s.10 'Use': min(Gamma-bar_i, Gamma-hat_i)); None = +infinity."""
    if not (isinstance(a, GateResult) and isinstance(b, GateResult)) or "EMPTY" in (a.source, b.source):
        raise ValueError("combine takes two non-empty GateResults")
    if set(a.gamma) != set(b.gamma):
        raise ValueError("combine: index sets differ")
    out = {}
    for i in a.gamma:
        x, y = a.gamma[i], b.gamma[i]
        out[i] = y if x is None else x if y is None else min(x, y)
    return GateResult(out, {"combined": [a.report, b.report]}, "GATE_MIN")
