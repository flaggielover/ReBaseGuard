"""Phase A: exact open-cell map for CUSUM K5 after the adopted slot-1 probe (descriptive; no new scientific arithmetic).

Inputs (all frozen / sealed, each checked against its pin):
  * K1 CUSUM records 0-309 through the accepted E6 adapter's own frozen loading path (manifest 29ad1f9b, cover 341eb5e9,
    frozen k5_minimality loader 3a54f0fb and frozen k5b_check.k5b_literal ddd54dc4);
  * the adopted slot-1 L1 values (sealed record cf90f1ea, consumed exactly as in E6_POSITIVE_CONSUMPTION_OUTPUT);
  * the certified operator constants C_e0, C_o0 (constants_r4 registry a645a157) and the frozen He_6 hull norm table,
    used ONLY to classify each cell by whether the graded parity resolvent block of graded_dag is admissible on the hull
    [0, x_k] (a property of certified operator constants; no value of R or of any derivative of R is computed).

Per open cell and per m the map records the exact reason the frozen theorem K5-B does not pass it:
  FRONT  cells before the first direct pass: no order-3 channel (L_k = None) and H_k.lo <= 0, so mu_k = H_k.lo and the
         gamma chain is destroyed; the direct bound Gamma_k >= 0.  Flags: MIDPOINT_G_INDETERMINATE (hi(R - e0 D) >= 0),
         CURVATURE_SLACK (hi(R - e0 D) < 0 <= Gamma), zone GRADED / SCALAR_ONLY.
  TAIL   cells after the direct-pass region: Gamma_k >= 0 purely by curvature slack; THEOREM_DOMAIN when x_hi > 2.

    python -B code/open_cell_map.py build --repo <clean checkout> --out OPEN_CELL_MAP.json   (vultr-02, records present)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path

SCHEMA = "rebaseguard.p5y.k5.remaining-cell-closure.open-cell-map.v1"
CP = "level4/closure_proofs/"
ADAPTER = CP + "p5y_k5b_consumption_adapter/code/consumption_adapter.py"
ADAPTER_SHA256 = "fbad7d33261fd47fc56c034d6a016f8427b81b51f9199f0e3a8f3e74df35973d"
SEALED = CP + "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json"
SEALED_SHA256 = "cf90f1ea"   # prefix check below uses the full value from the ledger OUTCOME
E6_OUT = CP + "p5y_k5_cusum_first_real_probe_result/consumption/E6_POSITIVE_CONSUMPTION_OUTPUT.json"
E6_OUT_CANON_SHA256 = "89017388681e05ec9b8e63ef8e22305af8bd7cf76d5ab1b571a7c948afcafb6a"
TWO = F(2)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":")).encode()


def load_adapter(repo: Path):
    path = repo / ADAPTER
    if sha256_bytes(path.read_bytes()) != ADAPTER_SHA256:
        raise SystemExit("E6 adapter does not match its pin")
    spec = importlib.util.spec_from_file_location("e6_adapter_readonly", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sealed_L1(repo: Path) -> dict:
    raw = (repo / SEALED).read_bytes()
    if not sha256_bytes(raw).startswith(SEALED_SHA256):
        raise SystemExit("sealed slot-1 record hash mismatch")
    rec = json.loads(raw)
    return {m: F(rec["scientific"]["per_m"][m]["L1"]) for m in ("1", "2", "3", "5")}, sha256_bytes(raw)


def graded_zone(repo: Path, cover: list) -> dict:
    """k -> True iff graded_dag.resolvent_block is admissible (mode 'graded') on the hull [0, x_k] with the certified
    C_e0, C_o0, the He_6 hull norms k_1, k_2 on [0, x_k] and C = max C_upper over cells 0..k. Operator constants only."""
    for p in ("p5y_k5_cusum_order3_r4_tightening/code", "p5y_k5_cusum_order3_r3_infrastructure/code",
              "p5y_k5_cusum_order3_r2_repair/code", "p5y_k5_cusum_order3_real_producer/code"):
        sys.path.append(str(repo / CP / p))
    import hermite6_ext as H6   # noqa: E402  (first import at the default 53-bit context, as the executor does)
    import constants_r4 as K4   # noqa: E402
    import graded_dag as G      # noqa: E402
    import rung3_engine as R1E  # noqa: E402
    c = K4.load_certificates()
    out, cmax = {}, F(0)
    with R1E.precision(256):
        ex = R1E.exact
        for cell in cover:
            cmax = max(cmax, F(cell["C_upper"]))
            x = cell["x_hi"]
            t = H6.norm_table(F(0), x)
            R = G.resolvent_block(ex(cmax), ex(c["C_e0"]), ex(c["C_o0"]), t["k"][1], t["k"][2], ex(x), True)
            out[cell["index"]] = R["mode"] == "graded"
    return out, {k: str(v) for k, v in c.items()}


def build(repo: Path, records_dir: Path) -> dict:
    A = load_adapter(repo)
    comp = A.frozen_components(repo)
    KM, KB = comp["loader"], comp["theorem"]
    L1, sealed_sha = sealed_L1(repo)
    manifest = json.loads(A.bound_file(repo / A.MANIFEST, A.MANIFEST_SHA256, "record manifest"))
    A.bound_file(repo / A.CELLS_JSON, A.CELLS_SHA256, "cells.json")
    cover = KM.load_cells(repo / A.CELLS_JSON, A.DETECTOR)
    if [c["index"] for c in cover] != list(range(0, 310)):
        raise SystemExit("cover universe mismatch")
    records, hashes = A.read_records(KM, records_dir, cover, manifest)
    geo = []
    table = {c["index"]: c for c in json.loads((repo / A.CELLS_JSON).read_bytes()) if c["detector"] == "CUSUM"}
    for c in cover:
        geo.append({"index": c["index"], "x_hi": KM.rat(c["right"]), "C_upper": table[c["index"]]["C_upper"]})
    zone, constants = graded_zone(repo, geo)
    last_graded = max(k for k, v in zone.items() if v and all(zone[j] for j in range(k + 1)))
    per_m, e6_check = {}, {}
    for m in A.MS:
        cells = A.cells_for_m(KM, cover, records, m, L1[m])
        rows = KB.k5b_literal(cells)
        passed = [cover[i]["index"] for i, r in enumerate(rows) if r["pass"] is True]
        opened = [k for k in range(310) if k not in set(passed)]
        first_direct = min(k for k in passed if k > 0)
        open_rows = []
        for k in opened:
            c, r = cells[k], rows[k]
            ghi = c["R"][1] - c["e0"] * c["D"][0]
            glo = c["R"][0] - c["e0"] * c["D"][1]
            pen = c["rho"] * c["x_hi"] * c["M"]
            region = "FRONT" if k < first_direct else "TAIL"
            flags = []
            if c["H"][0] <= 0:
                flags.append("H_BOUND")
            flags.append("MIDPOINT_G_INDETERMINATE" if ghi >= 0 else "CURVATURE_SLACK")
            if c["x_hi"] > TWO:
                flags.append("THEOREM_DOMAIN")
            primary = "MISSING_ORDER3_EVIDENCE" if region == "FRONT" else "INTERVAL_WIDTH"
            open_rows.append({
                "cell": k, "x_lo": str(c["x_lo"]), "x_hi": str(c["x_hi"]), "region": region, "primary": primary,
                "flags": flags, "zone": "GRADED" if zone[k] and k <= last_graded else "SCALAR_ONLY",
                "diag": {"g_mid_hi": float(ghi), "g_mid_width": float(ghi - glo), "g_mid_centre": float((ghi + glo) / 2),
                         "curvature_penalty": float(pen), "Gamma": float(r["Gamma"]), "H_lo": float(c["H"][0]),
                         "M_R2": float(c["M"])}})
        per_m[m] = {"pass_ranges": KM.ranges(passed), "open_ranges": KM.ranges(opened), "open_count": len(opened),
                    "first_direct_pass_after_cell_0": first_direct, "rows_sha256": sha256_bytes(canonical(A.row_json(rows))),
                    "open": open_rows}
        e6_check[m] = KM.ranges(passed)
    e6 = json.loads((repo / E6_OUT).read_bytes())
    e6_ok = sha256_bytes(canonical(e6)) == E6_OUT_CANON_SHA256 and all(
        e6["per_m"][m]["pass_ranges"] == e6_check[m] for m in A.MS)
    if not e6_ok:
        raise SystemExit("initial open sets differ from the adopted E6 consumption output")
    union = sorted({row["cell"] for m in A.MS for row in per_m[m]["open"]})
    return {"schema": SCHEMA, "detector": "CUSUM", "universe": [0, 309], "m_values": list(A.MS),
            "inputs": {"sealed_slot1_sha256": sealed_sha, "L1": {m: str(v) for m, v in L1.items()},
                       "e6_output_canonical_sha256": E6_OUT_CANON_SHA256, "adapter_sha256": ADAPTER_SHA256,
                       "components": comp["sha256"], "manifest_sha256": A.MANIFEST_SHA256,
                       "cells_json_sha256": A.CELLS_SHA256, "records_sha256": sha256_bytes(canonical(hashes)),
                       "operator_constants": constants},
            "initial_sets_equal_adopted_E6_output": e6_ok,
            "graded_zone": {"rule": "graded_dag.resolvent_block mode on hull [0, x_k], C = max C_upper(0..k)",
                            "last_graded_cell": last_graded, "x_hi_last_graded": str(geo[last_graded]["x_hi"]),
                            "first_scalar_only_cell": last_graded + 1},
            "per_m": per_m, "union_open_ranges": KM.ranges(union), "union_open_count": len(union)}


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--repo", required=True)
    b.add_argument("--records", default="/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
    b.add_argument("--out", required=True)
    a = ap.parse_args()
    res = build(Path(a.repo), Path(a.records))
    Path(a.out).write_bytes(json.dumps(res, sort_keys=True, indent=1).encode() + b"\n")
    print(json.dumps({m: {"open": v["open_ranges"], "count": v["open_count"]} for m, v in res["per_m"].items()}))
    print("graded zone last cell", res["graded_zone"]["last_graded_cell"], "sha256", sha256_bytes(Path(a.out).read_bytes()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
