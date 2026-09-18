"""Independent cross-check of the E6 consumption adapter (E6_SPEC.md S9).

Written separately from consumption_adapter.py and sharing no function with it. Two paths, both frozen
implementations of the same frozen theorem; no new rule:

  X-A  the frozen readiness scan k5_minimality.verify(CUSUM_MINIMALITY_R1, records, cells) must reproduce the committed
       evidence exactly (it never calls k5b_literal);
  X-B  records addressed through the manifest keys (not record_path), cover built here from cells.json (not
       load_cells), cells fed to the frozen k5b_check.k5b_readiness_variant; pass sets must equal EXPECTED, every
       per-cell Gamma must equal the Gamma string of the same cell in the R1 boundary rows, and every H.lo <= 0.
"""
from __future__ import annotations

import hashlib
import json
import types
from fractions import Fraction
from pathlib import Path

CP = "level4/closure_proofs/"
PIN = {"k5_minimality": (CP + "p5y_k5_order3_readiness_audit/code/k5_minimality.py",
                         "3a54f0fb290a9b8a07c861653d4399e6c588afdaef77ee51473f778c6c988885"),
       "k5b_check": (CP + "p5y_k5b_independent_countersignature/code/k5b_check.py",
                     "ddd54dc469375a2d64352782add8573231be07b94f7246dad83c4e55a2bf35a6")}
EVIDENCE = (CP + "p5y_k5_order3_readiness_audit/evidence/CUSUM_MINIMALITY_R1.json",
            "7feb576b84508c91a79e605fc190ac5da5083662ad9640aea4976c566a0c2a30")
COVER = (CP + "p5y_k1_cover_ledger_successor/config/cells.json",
         "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f")
EXPORT_MANIFEST = (CP + "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
                   "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334")
MS = ("1", "2", "3", "5")


def _pinned_bytes(path: Path, pin: str) -> bytes:
    b = path.read_bytes()
    if hashlib.sha256(b).hexdigest() != pin:
        raise RuntimeError(f"pin mismatch: {path}")
    return b


def _module(repo: Path, name: str):
    rel, pin = PIN[name]
    mod = types.ModuleType(name + "_crosscheck")
    mod.__file__ = str(repo / rel)
    exec(compile(_pinned_bytes(repo / rel, pin), str(repo / rel), "exec"), mod.__dict__)
    return mod


def _q(v) -> Fraction:
    """An exact rational: 'p/q' or an exact [value, correction] pair."""
    return Fraction(v) if isinstance(v, str) else Fraction(v[0]) + Fraction(v[1])


def _spans(xs):
    out = []
    for x in xs:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def path_a(repo: Path, records_dir: Path) -> dict:
    KM = _module(repo, "k5_minimality")
    _pinned_bytes(repo / EVIDENCE[0], EVIDENCE[1])
    _pinned_bytes(repo / COVER[0], COVER[1])
    problems = KM.verify(repo / EVIDENCE[0], records_dir, repo / COVER[0])
    return {"frozen_scan_reproduces_evidence": problems == [], "problems": problems}


def path_b(repo: Path, records_dir: Path) -> dict:
    KB = _module(repo, "k5b_check")
    evidence = json.loads(_pinned_bytes(repo / EVIDENCE[0], EVIDENCE[1]))
    manifest = json.loads(_pinned_bytes(repo / EXPORT_MANIFEST[0], EXPORT_MANIFEST[1]))["files"]
    table = json.loads(_pinned_bytes(repo / COVER[0], COVER[1]))
    cover = sorted((c for c in table if c["detector"] == "CUSUM" and _q(c["left"]) < 2), key=lambda c: c["index"])
    idx = [c["index"] for c in cover]
    export_root = Path(records_dir).parent
    records = {}
    for i in idx:
        key = f"k4_records/aux5_CUSUM_{i}_256.json"
        data = (export_root / key).read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest[key]:
            raise RuntimeError(f"manifest mismatch for {key}")
        records[i] = json.loads(data)
        if records[i]["cell_index"] != i:
            raise RuntimeError(f"{key} names cell {records[i]['cell_index']}")
    out = {"universe": [idx[0], idx[-1]], "cell_count": len(idx), "per_m": {}}
    for m in MS:
        cells = []
        for c in cover:
            e = records[c["index"]]["m"][m]
            iv = lambda f: (Fraction(e[f]["lo"]), Fraction(e[f]["hi"]))
            cells.append({"x_lo": _q(c["left"]), "x_hi": _q(c["right"]), "rho": _q(c["rho"]), "e0": _q(c["e0"]),
                          "R": iv("R_interval"), "D": iv("D_interval"), "H": iv("R2_interval"),
                          "M": Fraction(e["M_R2"]), "L": None})
        rows = KB.k5b_readiness_variant(cells)
        passing = [idx[j] for j, r in enumerate(rows) if r["pass"]]
        gamma = {idx[j]: str(r["Gamma"]) for j, r in enumerate(rows)}
        boundary = evidence["per_m"][m]["boundary_rows"]
        gamma_mismatch = [b["cell"] for b in boundary if gamma.get(b["cell"]) != b["Gamma"]]
        pass_mismatch = [b["cell"] for b in boundary if (b["cell"] in set(passing)) != b["pass"]]
        out["per_m"][m] = {"pass": passing, "pass_ranges": _spans(passing),
                           "expected_ranges": evidence["per_m"][m]["closed_by_k1"],
                           "boundary_rows_checked": len(boundary), "gamma_mismatches": gamma_mismatch,
                           "boundary_pass_mismatches": pass_mismatch,
                           "all_H_lo_le_0": all(c["H"][0] <= 0 for c in cells)}
    return out


def run(repo: Path, records_dir: Path, adapter_result: dict) -> dict:
    a = path_a(repo, records_dir)
    b = path_b(repo, records_dir)
    per_m = {}
    for m in MS:
        v = b["per_m"][m]
        expected = [x for lo, hi in v["expected_ranges"] for x in range(lo, hi + 1)]
        per_m[m] = {"variant_equals_expected": v["pass"] == expected,
                    "variant_equals_adapter": v["pass"] == adapter_result["per_m"][m]["pass"],
                    "gamma_addresses_ok": not v["gamma_mismatches"] and v["boundary_rows_checked"] > 0,
                    "boundary_pass_ok": not v["boundary_pass_mismatches"],
                    "premise_all_H_lo_le_0": v["all_H_lo_le_0"]}
    ok = (a["frozen_scan_reproduces_evidence"] and b["universe"] == [0, 309] and b["cell_count"] == 310
          and all(all(x.values()) for x in per_m.values()))
    return {"X_A": a, "X_B": b, "checks": per_m, "status": "PASS" if ok else "FAIL"}
