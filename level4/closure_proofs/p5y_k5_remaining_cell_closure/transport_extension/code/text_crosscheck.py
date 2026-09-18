"""Independent cross-check of T-EXT (written separately; shares no function with text_transport / text_consume).

X-A  transport: for every frozen hull 0..40 rebuild base(eta = right end of cell k) from cells.json directly (own
     contiguity and running-max C, own sealed-input parsing), call the frozen R4 local_r5.local_tower / R3
     r5_majorant.m5 / hermite6_ext / R2 graded_dag directly; M2..M5 and Lambda must equal TEXT_RESULT exactly; hull 0 must
     equal the sealed M5; modes graded; M_n nondecreasing in k.
X-B  consumption: records addressed through the manifest keys, geometry from cells.json, and an own implementation of
     the K5-B recurrences written from K5_GLOBAL_BRIDGE.md (never k5b_literal), for C1 and C2; pass sets and the fed
     channel / curvature must equal TEXT_CONSUMPTION.

    python -B code/text_crosscheck.py transport --text TEXT_RESULT.json --out XA.json
    python -B code/text_crosscheck.py consumption --text TEXT_RESULT.json --consumption TEXT_CONSUMPTION.json --out XB.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
CPD = ROOT / "level4" / "closure_proofs"
MVALS = ("1", "2", "3", "5")
SEALED_REC = CPD / "p5y_k5_cusum_first_real_probe_protocol" / "evidence" / "slot-1" / "SCIENTIFIC_RECORD_SEALED.json"


def _digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _need(cond: bool, msg: str, problems: list) -> None:
    if not cond:
        problems.append(msg)


def _cusum_table() -> dict:
    t = json.loads((CPD / "p5y_k1_cover_ledger_successor" / "config" / "cells.json").read_text())
    return {c["index"]: c for c in t if c["detector"] == "CUSUM"}


def _expected_lambda(tab: dict, L0: dict, m5: dict, m3: dict, k: int, m: str) -> Fraction:
    X = Fraction(tab[k]["right"][0])
    pen = Fraction(0)
    for j in range(k + 1):
        a, b = Fraction(tab[j]["left"][0]), Fraction(tab[j]["right"][0])
        pen += m5[j][m] * ((X - a) * (X - a) - (X - b) * (X - b)) / 2
    lo = L0[m] - pen
    return lo if lo > -m3[k][m] else -m3[k][m]


def _frozen_or_refuse() -> None:
    """Own pre-freeze guard (review F11): X-A evaluates wide hulls, so it refuses unless the T-EXT protocol is committed,
    unmodified against HEAD and FROZEN_PRE_RESULT."""
    import subprocess
    rel = "level4/closure_proofs/p5y_k5_remaining_cell_closure/transport_extension/config/TEXT_PROTOCOL.json"
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", rel], capture_output=True).returncode == 0
    clean = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--", rel], capture_output=True).returncode == 0
    if not (tracked and clean and json.loads((ROOT / rel).read_text()).get("status") == "FROZEN_PRE_RESULT"):
        raise SystemExit("X-A refused: the T-EXT protocol is not frozen at HEAD")


def transport(text_path: Path) -> dict:
    _frozen_or_refuse()
    sys.path.insert(0, str(CPD / "p5y_k5_cusum_real_point_executor" / "code"))
    import paths  # noqa: F401
    import backends  # noqa: F401  (53-bit certificate-stack initialisation)
    from flint import arb
    import constants_r4
    import graded_dag
    import hermite6_ext
    import local_r5
    import r5_majorant
    import rung3_engine

    problems: list = []
    text = json.loads(text_path.read_text())
    _need(_digest(SEALED_REC) == "cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae", "sealed hash", problems)
    sci = json.loads(SEALED_REC.read_text())["scientific"]
    tab = _cusum_table()
    certs = constants_r4.load_certificates()
    L0 = {m: Fraction(sci["per_m"][m]["L0"]) for m in MVALS}
    got = {}
    with rung3_engine.precision(256):
        def num(x):
            x = Fraction(x)
            return arb(x.numerator) / arb(x.denominator)
        cand = {node: (num(p[0]), num(p[1])) for node, p in sci["intermediates"]["candidate_graded_sups"].items()}
        errs = {node: graded_dag.V(num(t[0]), num(t[1]), num(t[2])) for node, t in sci["intermediates"]["point_nodes"].items()}
        running_C = Fraction(0)
        for k in range(0, 41):
            running_C = max(running_C, Fraction(tab[k]["C_upper"]))
            if k > 0:
                _need(Fraction(tab[k]["left"][0]) == Fraction(tab[k - 1]["right"][0]), f"gap before cell {k}", problems)
            eta = Fraction(tab[k]["right"][0])
            norms = hermite6_ext.norm_table(Fraction(0), eta)
            base = {"C": num(running_C), "C_e0": num(certs["C_e0"]), "C_o0": num(certs["C_o0"]),
                    "k": norms["k"], "j": norms["j"], "eta": num(eta),
                    "S0": {n: hermite6_ext.sup_S0_on(n, Fraction(0), eta) for n in range(7)}}
            blk = graded_dag.resolvent_block(base["C"], base["C_e0"], base["C_o0"], norms["k"][1], norms["k"][2],
                                             base["eta"], True)
            res = local_r5.local_tower(base, cand, errs, x1=num(eta))
            M = {n: {m: rung3_engine.fraction_of(r5_majorant.m5(res["towers"], parity=True, order=n)[int(m)].abs_upper())
                     for m in MVALS} for n in (2, 3, 4, 5)}
            got[k] = {"mode": blk["mode"], "M": M}
    for m in MVALS:
        _need(got[0]["M"][5][m] == Fraction(sci["per_m"][m]["M5"]), f"hull 0 M5 differs from sealed m {m}", problems)
    rows = {r["cell"]: r for r in text["rows"]}
    _need(sorted(rows) == list(range(0, 41)), "TEXT_RESULT hull cells", problems)
    m5 = {k: got[k]["M"][5] for k in got}
    m3 = {k: got[k]["M"][3] for k in got}
    for k, g in got.items():
        r = rows.get(k, {})
        _need(r.get("resolvent_mode") == g["mode"] == "graded", f"mode cell {k}", problems)
        for n in (2, 3, 4, 5):
            for m in MVALS:
                _need(Fraction(r["M"][str(n)][m]) == g["M"][n][m], f"M{n} cell {k} m {m}", problems)
                if k > 0:
                    _need(g["M"][n][m] >= got[k - 1]["M"][n][m], f"M{n} not monotone at cell {k} m {m}", problems)
        if k > 0:
            for m in MVALS:
                _need(Fraction(r["Lambda"][m]) == _expected_lambda(tab, L0, m5, m3, k, m), f"Lambda cell {k} m {m}", problems)
    return {"check": "X-A", "hulls": len(got), "problems": problems, "pass": not problems}


def _chain(cells: list) -> list:
    """K5-B from the theorem text: l_0 = 0; cell 1 special; gamma_1 = +inf when L_1 is absent."""
    out, ell, gam = [], Fraction(0), None
    for i, c in enumerate(cells):
        G = c["Rhi"] - c["e0"] * c["Dlo"] + c["rho"] * c["xhi"] * c["M"]
        L, h = c["L"], c["Hlo"]
        if i == 0:
            good = (L is not None and L > 0) or G < 0
            ell = h if L is None else max(h, 2 * c["rho"] * L)
            gam = None if L is None else -L * c["xhi"] ** 3 / 3
        else:
            if L is None:
                mu, ell_next = h, h
            else:
                mu = max(h, ell + min(Fraction(0), 2 * c["rho"] * L))
                ell_next = max(h, ell + 2 * c["rho"] * L)
            d = (c["xhi"] ** 2 - c["xlo"] ** 2) / 2
            if gam is None:
                U, gam_next = None, G
            else:
                U, gam_next = max(gam, gam - mu * d), min(gam - mu * d, G)
            good = (U is not None and U < 0) or G < 0
            ell, gam = ell_next, gam_next
        out.append(good)
    return out


def _spans(xs):
    out = []
    for x in xs:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def consumption(text_path: Path, cons_path: Path, records_dir: Path) -> dict:
    problems: list = []
    text = json.loads(text_path.read_text())
    cons = json.loads(cons_path.read_text())
    _need(cons["text_result_sha256"] == _digest(text_path), "consumption not bound to this TEXT_RESULT", problems)
    man_path = CPD / "p5y_k1_cusum_aux5_composite_closure" / "evidence" / "closure_r1" / "COMPOSITE_EXPORT_MANIFEST.json"
    _need(_digest(man_path) == "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334", "manifest pin", problems)
    files = json.loads(man_path.read_text())["files"]
    sci = json.loads(SEALED_REC.read_text())["scientific"]
    tab = _cusum_table()
    rows = {r["cell"]: r for r in text["rows"]}
    recs = {}
    for k in range(310):
        b = (Path(records_dir) / f"aux5_CUSUM_{k}_256.json").read_bytes()
        _need(hashlib.sha256(b).hexdigest() == files.get(f"k4_records/aux5_CUSUM_{k}_256.json"), f"record {k}", problems)
        recs[k] = json.loads(b)
    out = {}
    for variant in ("C1", "C2"):
        out[variant] = {}
        for m in MVALS:
            Lmap = {0: Fraction(sci["per_m"][m]["L1"])}
            for k in range(1, 41):
                Lmap[k] = Fraction(rows[k]["Lambda"][m])
            cells = []
            for k in range(310):
                t, r = tab[k], recs[k]["m"][m]
                Hlo, Hhi, M = Fraction(r["R2_interval"]["lo"]), Fraction(r["R2_interval"]["hi"]), Fraction(r["M_R2"])
                if variant == "C2" and k <= 40:
                    b2 = Fraction(rows[k]["M"]["2"][m])
                    Hlo, M = max(Hlo, -b2), min(M, b2)
                cells.append({"xlo": Fraction(t["left"][0]), "xhi": Fraction(t["right"][0]), "rho": Fraction(t["rho"][0]),
                              "e0": Fraction(t["e0"][0]), "Rhi": Fraction(r["R_interval"]["hi"]),
                              "Dlo": Fraction(r["D_interval"]["lo"]), "Hlo": Hlo, "M": M, "L": Lmap.get(k)})
            spans = _spans([k for k, v in enumerate(_chain(cells)) if v])
            out[variant][m] = spans
            got = cons["consumptions"][variant][m]
            _need(spans == got["pass_ranges"], f"{variant} pass set m {m}", problems)
            _need(got.get("L_used") == {str(k): (None if cells[k]["L"] is None else str(cells[k]["L"])) for k in range(42)},
                  f"{variant} channel fed m {m}", problems)
            _need(got.get("H_lo_used") == {str(k): str(cells[k]["Hlo"]) for k in range(42)}, f"{variant} H.lo fed m {m}", problems)
            _need(got.get("M_used") == {str(k): str(cells[k]["M"]) for k in range(42)}, f"{variant} M fed m {m}", problems)
    return {"check": "X-B", "pass_ranges": out, "problems": problems, "pass": not problems}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("which", choices=("transport", "consumption"))
    ap.add_argument("--text", required=True)
    ap.add_argument("--consumption")
    ap.add_argument("--records", default="/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = transport(Path(a.text)) if a.which == "transport" else consumption(Path(a.text), Path(a.consumption),
                                                                             Path(a.records))
    Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1, default=str) + "\n")
    print(res["check"], "PASS" if res["pass"] else "FAIL", res["problems"][:5])
    return 0 if res["pass"] else 5


if __name__ == "__main__":
    sys.exit(main())
