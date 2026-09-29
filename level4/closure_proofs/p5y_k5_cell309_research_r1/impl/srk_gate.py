"""SRK certificate gate (review R1 blocker B2; binding hardened per review R2 finding P-1): the ONLY path from
certificates to the cell-level Gamma-bar_i.

gate(cell_lo, cell_hi, geometry, kernel, certs, verdicts, verdict_source=...) -> GateResult

A certificate is ADMITTED iff all of:
  G1 schema SRK_CERT/1, status CERTIFIED, sha256 == sha256(canonical body without 'sha256')
  G2 geometry == the requested geometry; kernel field == the requested kernel ('whole' | 'taboo'); the field is
     inside the hashed body (certificates without it are refused: pre-B5 certificates cannot pass the gate)
  G3 weight_block == the outward dyadic hull of the cell (srk_certify.cell_blocks), exactly
  G4 block == one of the cell's declared check sub-blocks, exactly; e_c == the block midpoint
  G5 the independent verifier's verdict for THIS sha256 is ACCEPT (verdicts: {sha256: 'ACCEPT'|'REJECT'|'REFUSE'})
  G6 Gamma is a nonnegative rational; hermite_index is an int in the requested indices
Then Gamma_{i,b} = min over admitted certificates for (i, b), and Gamma-bar_i = max_b Gamma_{i,b} if EVERY declared
sub-block b has at least one admitted certificate for index i; otherwise Gamma-bar_i = None (+infinity: the consumer's
min falls back to the TC-T term, THEOREM_SRK section 3).  Every refusal is reported with its reason.

Binding (review R2 P-1).  A GateResult is immutable, can only be constructed inside this module, and records the cell,
geometry, kernel, admitted sha256s and the verdict source (the identity of the verifier that produced the verdicts,
e.g. 'sha256:<hex of the verifier file>' from verdicts_from_verifier).  The consumer adapter checks all of them against
what the Stage-2 driver knows.  Cell endpoints must be exact rationals (Fraction, int or 'p/q'); floats are refused.

Taboo kernel (SRK-T, Lemma SV-T): a taboo certificate bounds (G^_e kbar)(a), NOT (R_e kbar)(a) = (G^_e kbar)(a)/D_e, and
D_e <= 1.  A taboo gate therefore REQUIRES d_lo = {"value": "p/q" with 0 < value <= 1, "domain": ["lo", "hi"]}, a
certified lower bound D_e >= value for every e in domain, with domain containing the cell C (only e in C is used: V_e(a)
is e-affine on each sub-block, so its max over C ∩ b is at most the max at b's endpoints).  It returns
Gamma-hat_i = max_b Gamma_{i,b} / value.  Without d_lo a taboo gate REFUSES.  (SRK-T is OUT of package 1; the consumer
adapter refuses taboo-derived results.)
combine(a, b) = the index-wise min of two GateResults for the same cell, geometry and verdict source.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
from types import MappingProxyType

import srk_certify as S

_TOKEN = object()
_FIELDS = ("gamma", "cell", "geometry", "kernel", "source", "admitted", "verdict_source", "d_lo", "_report_json")


class GateResult:
    """Immutable, module-constructed gate output.  Sources: GATE (whole kernel), GATE_TABOO, GATE_MIN, EMPTY."""
    __slots__ = _FIELDS

    def __init__(self, token, *, gamma, cell, geometry, kernel, source, admitted, verdict_source, d_lo, report):
        if token is not _TOKEN:
            raise TypeError("GateResult is created only by srk_gate (gate / empty / combine)")
        vals = {"gamma": MappingProxyType(dict(gamma)), "cell": (F(cell[0]), F(cell[1])),
                "geometry": MappingProxyType(dict(geometry)), "kernel": kernel, "source": source,
                "admitted": tuple(admitted), "verdict_source": verdict_source, "d_lo": d_lo,
                "_report_json": json.dumps(report, sort_keys=True, default=str)}
        for k, v in vals.items():
            object.__setattr__(self, k, v)

    def __setattr__(self, k, v):
        raise AttributeError("GateResult is immutable")

    def __delattr__(self, k):
        raise AttributeError("GateResult is immutable")

    @property
    def report(self) -> dict:
        return json.loads(self._report_json)

    @classmethod
    def empty(cls, cell_lo, cell_hi, geometry: dict, indices=(1, 2, 3, 4)):
        """all None (the adapter's reproduction case), bound to the cell and geometry like any other result."""
        return cls(_TOKEN, gamma={i: None for i in indices}, cell=(_rat(cell_lo), _rat(cell_hi)), geometry=geometry,
                   kernel="whole", source="EMPTY", admitted=(), verdict_source=None, d_lo=None,
                   report={"note": "all None (reproduction gate)"})


def canonical_sha(cert: dict) -> str:
    body = {k: v for k, v in cert.items() if k != "sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def _fr(x) -> F:
    if not isinstance(x, str):
        raise ValueError("rational fields must be strings 'p/q'")
    return F(x)


def _rat(x) -> F:
    """exact rational from Fraction, int (not bool) or 'p/q' string; floats and anything else are refused."""
    if isinstance(x, bool) or not isinstance(x, (F, int, str)):
        raise ValueError(f"cell endpoint must be an exact rational (Fraction, int or 'p/q'), not {type(x).__name__}")
    return F(x)


def verifier_identity(verifier_module) -> str:
    return "sha256:" + hashlib.sha256(Path(verifier_module.__file__).read_bytes()).hexdigest()


def verdicts_from_verifier(certs: list, verifier_module, kernel_file=None, N: int = 8, max_depth: int = 24) -> tuple:
    """run the independent verifier in-process on every certificate: ({sha256: verdict}, verdict_source)."""
    out = {}
    for c in certs:
        sha = c.get("sha256") if isinstance(c, dict) else None
        if sha is None or sha in out:
            continue
        out[sha] = verifier_module.verify_cert(c, kernel_file, N=N, max_depth=max_depth, procs=1, log=None)["verdict"]
    return out, verifier_identity(verifier_module)


def _d_lo(d_lo, cell_lo, cell_hi) -> F:
    if not isinstance(d_lo, dict) or set(d_lo) != {"value", "domain"}:
        raise ValueError("taboo gate requires d_lo = {'value': 'p/q', 'domain': ['lo', 'hi']}")
    v = _fr(d_lo["value"])
    lo, hi = (_fr(x) for x in d_lo["domain"])
    if not 0 < v <= 1:
        raise ValueError("D_lo must be a rational in (0, 1] (D_e is a probability)")
    if not (lo <= cell_lo and cell_hi <= hi):
        raise ValueError("D_lo validity domain does not contain the cell")
    return v


def gate(cell_lo, cell_hi, geometry: dict, kernel: str, certs: list, verdicts: dict,
         indices=(1, 2, 3, 4), d_lo=None, verdict_source: str | None = None) -> GateResult:
    if kernel not in ("whole", "taboo"):
        raise ValueError("kernel must be 'whole' or 'taboo'")
    if not isinstance(verdict_source, str) or not verdict_source:
        raise ValueError("verdict_source (the identity of the verifier that produced the verdicts) is required")
    cell_lo, cell_hi = _rat(cell_lo), _rat(cell_hi)
    if kernel == "taboo":
        dl = _d_lo(d_lo, cell_lo, cell_hi)
    elif d_lo is not None:
        raise ValueError("d_lo applies to the taboo kernel only")
    wb, subs = S.cell_blocks(cell_lo, cell_hi)
    subs_key = {(a, b) for a, b in subs}
    admitted: dict = {}
    shas = []
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
                i = c["hermite_index"]
                if w != wb:
                    why = "weight_block is not the cell's outward dyadic hull"
                elif blk not in subs_key:
                    why = "block is not a declared check sub-block of the cell"
                elif _fr(c["e_c"]) != (blk[0] + blk[1]) / 2:
                    why = "e_c is not the block midpoint"
                elif verdicts.get(c["sha256"]) != "ACCEPT":
                    why = f"independent verifier verdict {verdicts.get(c['sha256'])!r} != 'ACCEPT'"
                elif isinstance(i, bool) or not isinstance(i, int):
                    why = "hermite_index is not an int"
                else:
                    gm = _fr(c["Gamma"])
                    if gm < 0:
                        why = "negative Gamma"
                    elif i not in indices:
                        why = "index not requested"
                    else:
                        key = (i, blk)
                        admitted[key] = gm if key not in admitted else min(admitted[key], gm)
                        shas.append(c["sha256"])
        except (KeyError, ValueError, TypeError, ZeroDivisionError) as exc:
            why = f"malformed: {exc}"
        if why:
            refused.append({"sha256": c.get("sha256") if isinstance(c, dict) else None, "reason": why})
    gamma = {}
    for i in indices:
        per = [admitted.get((i, b)) for b in subs]
        gamma[i] = None if any(v is None for v in per) else (max(per) if kernel == "whole" else max(per) / dl)
    report = {"cell": [S.fstr(cell_lo), S.fstr(cell_hi)], "weight_block": [S.fstr(x) for x in wb],
              "sub_blocks": [[S.fstr(a), S.fstr(b)] for a, b in subs],
              "admitted": {f"{i}@[{S.fstr(b[0])},{S.fstr(b[1])}]": S.fstr(v) for (i, b), v in sorted(admitted.items())},
              "refused": refused,
              "gamma": {i: (S.fstr(v) if v is not None else None) for i, v in gamma.items()}, "kernel": kernel,
              "d_lo": None if kernel == "whole" else {"value": S.fstr(dl), "domain": list(d_lo["domain"])},
              "verdict_source": verdict_source}
    return GateResult(_TOKEN, gamma=gamma, cell=(cell_lo, cell_hi), geometry=geometry, kernel=kernel,
                      source="GATE" if kernel == "whole" else "GATE_TABOO", admitted=sorted(set(shas)),
                      verdict_source=verdict_source, d_lo=None if kernel == "whole" else dl, report=report)


def combine(a: GateResult, b: GateResult) -> GateResult:
    """index-wise min of two gate results (THEOREM_SRK s.10 'Use': min(Gamma-bar_i, Gamma-hat_i)); None = +infinity.
    Both must be non-empty gate results for the same cell, geometry and verdict source."""
    if not (isinstance(a, GateResult) and isinstance(b, GateResult)) or "EMPTY" in (a.source, b.source):
        raise ValueError("combine takes two non-empty GateResults")
    if a.cell != b.cell or dict(a.geometry) != dict(b.geometry) or a.verdict_source != b.verdict_source:
        raise ValueError("combine: results are for different cells, geometries or verdict sources")
    if set(a.gamma) != set(b.gamma):
        raise ValueError("combine: index sets differ")
    out = {}
    for i in a.gamma:
        x, y = a.gamma[i], b.gamma[i]
        out[i] = y if x is None else x if y is None else min(x, y)
    return GateResult(_TOKEN, gamma=out, cell=a.cell, geometry=a.geometry, kernel="min(" + a.kernel + "," + b.kernel + ")",
                      source="GATE_MIN", admitted=sorted(set(a.admitted) | set(b.admitted)),
                      verdict_source=a.verdict_source, d_lo=b.d_lo if b.d_lo is not None else a.d_lo,
                      report={"combined": [a.report, b.report]})
