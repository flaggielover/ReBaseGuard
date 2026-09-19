"""Phase A: exact lower-front blocker map (deterministic reuse of adopted evidence only).

Inputs (all adopted, pinned by sha256):
  - the sealed Perron-deflated consumption (DEFLATED_CONSUMPTION.json, 5dcc9b7d..., ADOPTED at 7cb01e38): per-cell R, R',
    R'' enclosures and M after theorem AD tightening and the T-EXT curvature channel, cells 0..159, every m;
  - the frozen CUSUM cover cells.json (341eb5e9...);
  - the adopted T-EXT result (cb97cabc...) through its pinned channel derivation text_consume.text_objects (657458ad...);
  - the sealed slot-1 record (cf90f1ea...): L0, U0 (point enclosure of R'''(0)) and L1;
  - the frozen Theorem K5-B implementation k5b_check.k5b_literal (ddd54dc4...).

The script replays the frozen K5-B on cells 0..159 for every m (the chain on cells <= 159 depends only on cells <= 159),
checks that the replayed pass set and `via` equal the sealed ones, and writes one row per lower-front open cell with the
failed predicate and the margin a closure would need. It computes no model quantity.

    python3 -B code/lower_front_blocker_map.py --out phase_a/LOWER_FRONT_BLOCKER_MAP.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
PINS = {
    CP + "p5y_k5_perron_deflated_resolvent/evidence/successor_r1/DEFLATED_CONSUMPTION.json":
        "5dcc9b7d26c92babbf1b19ad064b29969ea7bd829ea9629004e312520123274a",
    CP + "p5y_k5_perron_deflated_resolvent/evidence/successor_r1/K5_COVERAGE_MAP_R3.json":
        "6d598dc53293f91cdffb99f8fb3a0080542d8d0ca75c3110cc5fcc4db97a544d",
    CP + "p5y_k1_cover_ledger_successor/config/cells.json":
        "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f",
    CP + "p5y_k5_remaining_cell_closure/transport_extension/evidence/qualification_r1/TEXT_RESULT.json":
        "cb97cabcc3b5848665584e33ad4207c6d36ce835729725265d585dc8f3ee4f87",
    CP + "p5y_k5_remaining_cell_closure/transport_extension/code/text_consume.py":
        "657458ade03c4283ae6d5bd97e5567603380bf0e6281d8483f9c1fd45a62d0ea",
    CP + "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json":
        "cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae",
    CP + "p5y_k5b_independent_countersignature/code/k5b_check.py":
        "ddd54dc469375a2d64352782add8573231be07b94f7246dad83c4e55a2bf35a6",
}
DEFLATED, MAP_R3, CELLS, TEXT_RESULT, TEXT_CONSUME, SEALED, K5B = list(PINS)
MS = ("1", "2", "3", "5")
N_REPLAY = 160
SCHEMA = "rebaseguard.p5y.k5.lower-front-order3.blocker-map.v1"


class BlockerMapRefusal(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def pinned_bytes(rel: str) -> bytes:
    raw = (REPO / rel).read_bytes()
    if sha(raw) != PINS[rel]:
        raise BlockerMapRefusal(f"{rel} does not match its pin")
    return raw


def load_module(rel: str, name: str):
    raw = pinned_bytes(rel)
    mod = types.ModuleType(name)
    mod.__file__ = str(REPO / rel)
    exec(compile(raw, str(REPO / rel), "exec"), mod.__dict__)
    return mod


def rat(p) -> F:
    return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


def ranges(xs):
    out = []
    for x in sorted(xs):
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def fl(x) -> float | None:
    return None if x is None else float(x)


def build() -> dict:
    deflated = json.loads(pinned_bytes(DEFLATED))
    map_r3 = json.loads(pinned_bytes(MAP_R3))
    cover = sorted((c for c in json.loads(pinned_bytes(CELLS)) if c["detector"] == "CUSUM"), key=lambda c: c["index"])
    text = json.loads(pinned_bytes(TEXT_RESULT))
    sealed = json.loads(pinned_bytes(SEALED))["scientific"]["per_m"]
    TC = load_module(TEXT_CONSUME, "text_consume_blocker")
    KB = load_module(K5B, "k5b_check_blocker")
    lam, m2 = TC.text_objects(text, {m: sealed[m]["L1"] for m in MS})
    out = {"schema": SCHEMA, "inputs": dict(PINS), "per_m": {}, "rows": []}
    for m in MS:
        cons = deflated["consumptions"][m]
        cells = []
        for k in range(N_REPLAY):
            c, g = cons["cells"][str(k)], cover[k]
            L = F(sealed[m]["L1"]) if k == 0 else (lam[m][k] if k in lam[m] else None)
            cells.append({"x_lo": rat(g["left"]), "x_hi": rat(g["right"]), "rho": rat(g["rho"]), "e0": rat(g["e0"]),
                          "R": tuple(F(v) for v in c["R"]), "D": tuple(F(v) for v in c["D"]),
                          "H": tuple(F(v) for v in c["H"]), "M": F(c["M"]), "L": L})
        rows = KB.k5b_literal(cells)
        via = [rows[k]["via"] for k in range(N_REPLAY)]
        if via != [cons["via"][str(k)] for k in range(N_REPLAY)]:
            raise BlockerMapRefusal(f"replayed K5-B via differs from the sealed consumption for m={m}")
        opened = [k for k in range(N_REPLAY) if not rows[k]["pass"]]
        sealed_open = [k for a, b in cons["open_ranges"] for k in range(a, b + 1) if k < N_REPLAY]
        if opened != sealed_open:
            raise BlockerMapRefusal(f"replayed open set differs from the sealed one for m={m}")
        r3_open = [k for a, b in map_r3["per_m"][m]["open_ranges"] for k in range(a, b + 1)] \
            if "open_ranges" in map_r3["per_m"][m] else None
        L0, U0 = F(sealed[m]["L0"]), F(sealed[m]["U0"])
        out["per_m"][m] = {"open_front": ranges([k for k in opened if k >= 11]), "open_front_count":
                           len([k for k in opened if k >= 11]), "coverage_map_r3_open": r3_open,
                           "R3_at_0": {"L0": str(L0), "U0": str(U0), "L0_float": float(L0), "U0_float": float(U0)}}
        for k in opened:
            if k < 11:
                raise BlockerMapRefusal("unexpected open cell below 11")
            c, row, prev = cells[k], rows[k], rows[k - 1]
            g_lo = c["R"][0] - c["e0"] * c["D"][1]          # enclosure of g(e0) = R(e0) - e0 R'(e0)
            g_hi = c["R"][1] - c["e0"] * c["D"][0]
            pen = c["rho"] * c["x_hi"] * c["M"]
            dx2h = (c["x_hi"] ** 2 - c["x_lo"] ** 2) / 2
            gam = prev["gamma"]
            # chain: U_k < 0 iff gamma_{k-1} < 0 and mu_k > 2 gamma_{k-1} / dx2
            mu_req = (2 * gam / (c["x_hi"] ** 2 - c["x_lo"] ** 2)) if (gam is not None and gam < 0) else None
            failed = []
            if not row["Gamma"] < 0:
                failed.append("DIRECT: Gamma_k = hi(R - e0 D) + rho x_hi M >= 0")
            if gam is None or not gam < 0:
                failed.append("CHAIN: gamma_{k-1} >= 0 (chain broken before this cell)")
            elif not row["U"] < 0:
                failed.append("CHAIN: U_k >= 0 (mu_k too small)")
            out["rows"].append({
                "m": int(m), "cell": k, "e_lo": str(c["x_lo"]), "e_hi": str(c["x_hi"]), "e0": str(c["e0"]),
                "rho": str(c["rho"]),
                "e_lo_float": float(c["x_lo"]), "e_hi_float": float(c["x_hi"]),
                "g_e0_interval_float": [float(g_lo), float(g_hi)],
                "g_cell_upper_float (Gamma_k)": float(row["Gamma"]),
                "R_interval_float": [float(x) for x in c["R"]], "R1_interval_float": [float(x) for x in c["D"]],
                "R2_cell_interval_float": [float(x) for x in c["H"]], "M_float": float(c["M"]),
                "R3_available": {"L_k (T-EXT Lambda, K5-B channel)": fl(c["L"]),
                                 "R3(0) point enclosure": [float(L0), float(U0)]},
                "point_radius_R_float": float((c["R"][1] - c["R"][0]) / 2),
                "point_radius_R1_float": float((c["D"][1] - c["D"][0]) / 2),
                "whole_cell_radius_R2_float": float((c["H"][1] - c["H"][0]) / 2),
                "transport_penalty_rho_xhi_M_float": float(pen),
                "chain_state": {"gamma_prev_float": fl(gam), "ell_prev_float": fl(prev["ell"]),
                                "mu_k_float": fl(row["mu"]), "U_k_float": fl(row["U"])},
                "failed_predicate": failed,
                "margin_direct": {"Gamma_k_must_drop_by_more_than_float": float(row["Gamma"])},
                "margin_chain": {
                    "mu_required_given_adopted_gamma_prev_float": fl(mu_req),
                    "sufficient_uniform_rule": "H.lo >= 0 on every cell 11..k (then U_j = gamma_10 < 0 for all j)",
                    "H_lo_now_float": float(c["H"][0]),
                    "H_lo_increase_needed_for_uniform_rule_float": float(max(F(0), -c["H"][0]))},
                "dx2_half_float": float(dx2h),
            })
    out["union_open_front"] = ranges(sorted({r["cell"] for r in out["rows"]}))
    out["row_count"] = len(out["rows"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = build()
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print({m: v["open_front"] for m, v in res["per_m"].items()}, "rows", res["row_count"], "sha256", sha(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
