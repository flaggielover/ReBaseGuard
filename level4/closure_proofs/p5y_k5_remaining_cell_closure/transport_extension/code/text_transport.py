"""T-EXT: wider-hull evenness transport from the sealed, ADOPTED slot-1 record (deterministic; no model solve).

Theorem T-EXT (../TEXT_SPEC.md). For m in {1,2,3,5} and a prefix hull [0, eta] of the frozen CUSUM cover,
    M_n,m(eta) >= sup_[0,eta] |R_m^(n)|, n = 2..5, from the frozen local_r5.local_tower tower
                 (base(eta), sealed candidate graded sups, sealed graded point errors, anchor drift = eta),
    base(eta) = {C = max C_upper over the cover cells 0..k, C_e0, C_o0 (registry a645a157),
                 k, j = hermite6_ext.norm_table(0, eta), S0 = hermite6_ext.sup_S0_on(n, 0, eta), eta}.
Channel for K1 cell k (0-based; theorem cell C_(k+1)), X = x_hi(k), piecewise over the nested hulls j = 0..k:
    B_k = sum_j M5(x_hi(j)) [(X - x_lo(j))^2 - (X - x_hi(j))^2] / 2      (M5(x_hi(0)) = the sealed slot-1 M5)
    Lambda(k) = max(L0 - B_k, -M3(X))  <=  inf_(C_k) R'''.
Only frozen code computes numbers: local_r5 (R4), r5_majorant / hermite6_ext (R3), graded_dag (R2), rung3_engine (R1),
constants_r4 (R4 registry), and the executor's 53-bit CRAMER initialisation (backends, at import), then its contract check.

Pre-freeze guard (review F11): any tower with eta != x1 and every `evaluate` refuse unless config/TEXT_PROTOCOL.json
is git-tracked, unmodified against HEAD, status FROZEN_PRE_RESULT, and every pin in it matches.

    python -B code/text_transport.py replay   --out REPLAY.json
    python -B code/text_transport.py evaluate --out TEXT_RESULT.json --ledger EVAL_LEDGER.jsonl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
TEXT_NS = HERE.parents[1]
REPO = HERE.parents[5]
CP = REPO / "level4/closure_proofs"
sys.path.insert(0, str(CP / "p5y_k5_cusum_real_point_executor/code"))

import paths  # noqa: E402,F401  (the executor's frozen sys.path bootstrap)
import backends  # noqa: E402     (CRAMER compatibility: certificate stack first imported at 53 bits)
import constants_r4 as K4  # noqa: E402
import graded_dag as G  # noqa: E402
import hermite6_ext as H6  # noqa: E402
import local_r5 as LR  # noqa: E402
import r5_majorant as R5  # noqa: E402
import rung3_engine as R1E  # noqa: E402

SCHEMA = "rebaseguard.p5y.k5.remaining-cell-closure.text-result.v2"
PRECISION = 256
MS = ("1", "2", "3", "5")
ORDERS = (2, 3, 4, 5)
SEALED = CP / "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json"
SEALED_SHA256 = "cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae"
CELLS = CP / "p5y_k1_cover_ledger_successor/config/cells.json"
CELLS_SHA256 = "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"
PROTOCOL = TEXT_NS / "config/TEXT_PROTOCOL.json"
HULL_CELLS = tuple(range(1, 41))          # frozen: the whole graded zone of the Phase A map (cells 1..40)
REPLAY_REL_TOL = F(1, 2 ** 160)


class TextRefusal(RuntimeError):
    pass


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def q(x: F) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def bound(path: Path, pin: str, what: str) -> bytes:
    data = Path(path).read_bytes()
    if sha256_bytes(data) != pin:
        raise TextRefusal(f"{what} does not match its pin")
    return data


def _git(*args) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True)


def require_frozen() -> dict:
    """Refuse unless the T-EXT protocol is committed, clean, FROZEN_PRE_RESULT, and every pin matches."""
    rel = str(PROTOCOL.relative_to(REPO))
    if not PROTOCOL.exists() or _git("ls-files", "--error-unmatch", rel).returncode != 0:
        raise TextRefusal("PRE_FREEZE: config/TEXT_PROTOCOL.json is not committed")
    if _git("diff", "--quiet", "HEAD", "--", rel).returncode != 0:
        raise TextRefusal("PRE_FREEZE: config/TEXT_PROTOCOL.json differs from HEAD")
    proto = json.loads(PROTOCOL.read_text())
    if proto.get("status") != "FROZEN_PRE_RESULT":
        raise TextRefusal("PRE_FREEZE: protocol status is not FROZEN_PRE_RESULT")
    bad = [r for r, h in proto["pins"].items() if not (REPO / r).exists() or sha256_bytes((REPO / r).read_bytes()) != h]
    if bad:
        raise TextRefusal(f"PRE_FREEZE: pinned files differ: {bad[:3]}")
    return {"protocol_sha256": sha256_bytes(PROTOCOL.read_bytes()), "head": _git("rev-parse", "HEAD").stdout.strip()}


def load_sealed() -> dict:
    rec = json.loads(bound(SEALED, SEALED_SHA256, "sealed slot-1 record"))
    s = rec["scientific"]
    if s["context"]["x1"] != "5083/10000000" or s["context"]["point_e"] != "0/1":
        raise TextRefusal("sealed record is not the slot-1 point e = 0 / x1 = 5083/10^7 record")
    return s


def cover() -> list[dict]:
    table = json.loads(bound(CELLS, CELLS_SHA256, "cells.json"))
    cells = sorted((c for c in table if c["detector"] == "CUSUM"), key=lambda c: c["index"])
    if [c["index"] for c in cells[:41]] != list(range(41)) or F(cells[0]["left"][0]) != 0:
        raise TextRefusal("cover prefix is not contiguous from 0")
    for a, b in zip(cells[:41], cells[1:42]):
        if F(a["right"][0]) != F(b["left"][0]):
            raise TextRefusal("cover prefix is not contiguous")
    return cells


def anchors_from_sealed(s: dict) -> tuple[dict, dict]:
    """The sealed exact rationals (radius-zero dyadics of the slot-1 run) -> Arb inputs."""
    it = s["intermediates"]
    ex = R1E.exact
    cands = {n: (ex(F(e)), ex(F(o))) for n, (e, o) in it["candidate_graded_sups"].items()}
    pnodes = {n: G.V(ex(F(e)), ex(F(o)), ex(F(t))) for n, (e, o, t) in it["point_nodes"].items()}
    return cands, pnodes


def certified_constants(s: dict) -> dict:
    c = K4.load_certificates()
    sealed = s["intermediates"]["constants"]
    if F(sealed["C_e0"]) != c["C_e0"] or F(sealed["C_o0"]) != c["C_o0"]:
        raise TextRefusal("registry constants differ from the constants used by slot-1")
    return c


def hull_base(eta: F, C: F, consts: dict) -> dict:
    ex = R1E.exact
    t = H6.norm_table(F(0), eta)
    return {"C": ex(C), "C_e0": ex(consts["C_e0"]), "C_o0": ex(consts["C_o0"]), "k": t["k"], "j": t["j"],
            "eta": ex(eta), "S0": {n: H6.sup_S0_on(n, F(0), eta) for n in range(7)}}


def tower(eta: F, C: F, consts: dict, cands: dict, pnodes: dict) -> dict:
    base = hull_base(eta, C, consts)
    drift = R1E.exact(eta)
    if R1E.ball_fractions(drift) != R1E.ball_fractions(base["eta"]):          # review F6: anchor drift == hull
        raise TextRefusal("anchor drift x1 differs from the hull eta")
    mode = G.resolvent_block(base["C"], base["C_e0"], base["C_o0"], base["k"][1], base["k"][2], base["eta"], True)["mode"]
    loc = LR.local_tower(base, cands, pnodes, x1=drift)
    Mn = {n: {m: R1E.fraction_of(R5.m5(loc["towers"], parity=True, order=n)[int(m)].abs_upper()) for m in MS}
          for n in ORDERS}
    if Mn[5] != {m: R1E.fraction_of(loc["M5"][int(m)].abs_upper()) for m in MS}:
        raise TextRefusal("order-5 export differs from local_tower M5")
    return {"M": Mn, "mode": mode, "trace_m1": [F(t) for t in loc["trace_m1"]],
            "hull_norms": {"k": {str(i): q(R1E.upper_fraction(base["k"][i])) for i in sorted(base["k"])},
                           "j": {str(i): q(R1E.upper_fraction(base["j"][i])) for i in sorted(base["j"])},
                           "S0": {str(i): q(R1E.upper_fraction(base["S0"][i])) for i in sorted(base["S0"])},
                           "eta": q(R1E.upper_fraction(base["eta"]))}}   # the sealed record's serialization


def cramer() -> dict:
    c = backends.check_cramer_contract()
    if not c["pass"]:
        raise TextRefusal("CRAMER compatibility contract violated")
    return c


def rel(a: F, b: F) -> F:
    return abs(a - b) / abs(b)


def replay() -> dict:
    s = load_sealed()
    cells = cover()
    cr = cramer()
    with R1E.precision(PRECISION):
        consts = certified_constants(s)
        cands, pnodes = anchors_from_sealed(s)
        x1 = F(cells[0]["right"][0])
        out = tower(x1, F(cells[0]["C_upper"]), consts, cands, pnodes)
    sealed_hn = s["intermediates"]["hull_norms"]
    hull_equal = out["hull_norms"] == sealed_hn
    m5 = {m: {"recomputed": q(out["M"][5][m]), "sealed": s["per_m"][m]["M5"],
              "rel": float(rel(out["M"][5][m], F(s["per_m"][m]["M5"])))} for m in MS}
    m5_ok = all(rel(out["M"][5][m], F(s["per_m"][m]["M5"])) <= REPLAY_REL_TOL for m in MS)
    tr_sealed = [F(t) for t in s["intermediates"]["M5_trace_m1"]]
    tr_ok = len(tr_sealed) == len(out["trace_m1"]) and all(rel(a, b) <= REPLAY_REL_TOL
                                                           for a, b in zip(out["trace_m1"], tr_sealed))
    L1_ok = all(rel(F(s["per_m"][m]["L0"]) - x1 * x1 / 2 * out["M"][5][m], F(s["per_m"][m]["L1"])) <= REPLAY_REL_TOL
                for m in MS)
    return {"schema": SCHEMA + ".replay", "eta": q(x1), "mode": out["mode"], "hull_norms_equal_sealed": hull_equal,
            "M5": m5, "M5_within_tol": m5_ok, "trace_within_tol": tr_ok, "L1_within_tol": L1_ok,
            "tolerance": "relative 2^-160", "cramer_contract": cr["pass"],
            "pass": hull_equal and m5_ok and tr_ok and L1_ok and out["mode"] == "graded" and cr["pass"]}


def channel(cells: list, L0: dict, M5: dict, M3: dict) -> dict:
    """Piecewise transport (review F2). M5[j], M3[j]: bounds on the hull [0, x_hi(j)], j = 0..40 (j = 0 sealed)."""
    out = {}
    for k in HULL_CELLS:
        X = F(cells[k]["right"][0])
        row = {}
        for m in MS:
            B = sum((M5[j][m] * ((X - F(cells[j]["left"][0])) ** 2 - (X - F(cells[j]["right"][0])) ** 2) / 2
                     for j in range(0, k + 1)), F(0))
            row[m] = max(L0[m] - B, -M3[k][m])
        out[k] = row
    return out


def evaluate(ledger: Path | None = None) -> dict:
    frz = require_frozen()
    s = load_sealed()
    cells = cover()
    cr = cramer()
    L0 = {m: F(s["per_m"][m]["L0"]) for m in MS}
    M5_sealed = {m: F(s["per_m"][m]["M5"]) for m in MS}
    if ledger is not None:
        with open(ledger, "a") as f:
            f.write(json.dumps({"event": "EVALUATE_START", "utc": time.time(), **frz,
                                "code_sha256": sha256_bytes(HERE.read_bytes())}) + "\n")
    rows, Mh = [], {}
    with R1E.precision(PRECISION):
        consts = certified_constants(s)
        cands, pnodes = anchors_from_sealed(s)
        for k in (0,) + HULL_CELLS:
            eta = F(cells[k]["right"][0])
            C = max(F(c["C_upper"]) for c in cells[:k + 1])
            out = tower(eta, C, consts, cands, pnodes)
            if k == 0 and out["M"][5] != M5_sealed:
                raise TextRefusal("hull 0 does not reproduce the sealed M5 exactly")
            Mh[k] = out["M"]
            rows.append({"cell": k, "x_lo": q(F(cells[k]["left"][0])), "x_hi": q(eta), "C_hull": q(C),
                         "resolvent_mode": out["mode"], "M": {str(n): {m: q(v) for m, v in out["M"][n].items()}
                                                             for n in ORDERS},
                         "hull_norms": out["hull_norms"], "trace_m1_last": q(out["trace_m1"][-1])})
    lam = channel(cells, L0, {j: Mh[j][5] for j in Mh}, {j: Mh[j][3] for j in Mh})
    for r in rows:
        k = r["cell"]
        if k in lam:
            X = F(r["x_hi"])
            r["Lambda"] = {m: q(lam[k][m]) for m in MS}
            r["L_simple"] = {m: q(L0[m] - X * X / 2 * Mh[k][5][m]) for m in MS}     # disclosure only (not consumed)
    res = {"schema": SCHEMA, "sealed_record_sha256": SEALED_SHA256, "cells_json_sha256": CELLS_SHA256,
           "hull_cells": [0] + list(HULL_CELLS), "channel_cells": list(HULL_CELLS), "precision_bits": PRECISION,
           "L0": {m: q(v) for m, v in L0.items()}, "sealed_L1": {m: s["per_m"][m]["L1"] for m in MS},
           "cramer_contract": cr["pass"], "rows": rows, "freeze": frz, "code_sha256": sha256_bytes(HERE.read_bytes())}
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("replay", "evaluate"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--ledger")
    a = ap.parse_args()
    res = replay() if a.cmd == "replay" else evaluate(Path(a.ledger) if a.ledger else None)
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    if a.cmd == "evaluate" and a.ledger:
        with open(a.ledger, "a") as f:
            f.write(json.dumps({"event": "EVALUATE_OUTPUT", "utc": time.time(), "out": a.out,
                                "sha256": sha256_bytes(data)}) + "\n")
    print(a.cmd, "sha256", sha256_bytes(data), "pass" if res.get("pass", True) else "FAIL")
    return 0 if res.get("pass", True) else 4


if __name__ == "__main__":
    sys.exit(main())
