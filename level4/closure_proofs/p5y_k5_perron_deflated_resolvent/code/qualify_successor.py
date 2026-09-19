"""Successor qualification S00-S09 (K5_PERRON_DEFLATED_SUCCESSOR_SPEC section 5). Sign-blind: no K5 pass/fail is read,
except the replay of the ADOPTED T-EXT consumption (S05).

    python -B code/qualify_successor.py run --protocol-sha256 SHA --outdir DIR --workers 7      (vultr venv)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
sys.path.insert(0, str(HERE.parent))
import deflated_consume as DC  # noqa: E402

RECORDS = Path("/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")


def sha(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def s09_assembly_semantics(reg: dict) -> dict:
    """For every covered record and m: recorded half-width >= sum (1/m) recorded radii (R, R' midpoint; R'' whole
    cell); for m = 1 the excess over the radius must be tiny (origin radius + outward rounding)."""
    A = DC._load_pinned(REPO, DC.ADAPTER, DC.ADAPTER_SHA256, "e6_adapter_q")
    comp = A.frozen_components(REPO)
    KM = comp["loader"]
    manifest = json.loads(A.bound_file(REPO / A.MANIFEST, A.MANIFEST_SHA256, "record manifest"))
    cover = KM.load_cells(REPO / A.CELLS_JSON, A.DETECTOR)
    recs, _ = A.read_records(KM, RECORDS, cover, manifest)
    cells = sorted({b["cell"] for b in reg["blocks"]})
    bad, worst_excess = [], F(0)
    for k in cells:
        r = recs[k]
        for m in DC.MS:
            mi = int(m)
            for field, key, src in (("R_interval", "F", "eps_mid"), ("D_interval", "D", "eps_mid"),
                                    ("R2_interval", "H", "eps_cell_refined")):
                lo, hi = F(r["m"][m][field]["lo"]), F(r["m"][m][field]["hi"])
                need = sum((F(1, mi) * F(r[src][f"{key}:{j}"]) for j in range(mi)), F(0))
                hw = (hi - lo) / 2
                if hw < need:
                    bad.append([k, m, field])
                if mi == 1:
                    ex = (hw - need) / hw
                    worst_excess = max(worst_excess, ex)
    return {"cells": len(cells), "violations": bad, "m1_max_relative_excess": float(worst_excess),
            "pass": not bad and worst_excess < F(1, 10 ** 6)}


def s11_kappa_bounds() -> dict:
    """Arb proof of the consumer's rational kappa bounds: sqrt(2/pi) < K1_BOUND and 4 phi(1) < K2_BOUND."""
    import taboo_certify  # noqa: F401  (frozen import bootstrap)
    from flint import arb
    from intervals import workprec
    with workprec(256):
        k1 = (arb(2) / arb.pi()).sqrt()
        k2 = arb(4) * (arb(-1) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()
        b1 = arb(DC.K1_BOUND.numerator) / arb(DC.K1_BOUND.denominator)
        b2 = arb(DC.K2_BOUND.numerator) / arb(DC.K2_BOUND.denominator)
        ok = bool(k1 < b1) and bool(k2 < b2)
    return {"kappa1": k1.str(20), "kappa2": k2.str(20), "pass": ok}


def run(protocol_sha256: str, outdir: Path, workers: int) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    res = {}
    g = DC.frozen_guard(REPO, protocol_sha256)
    proto = g["protocol"]
    res["S00"] = {"head": g["head"], "pins": len(proto["pins"]), "pass": True}
    regp = REPO / proto["registry"]
    reg = json.loads(regp.read_text())
    art_dir = REPO / proto["registry_artifacts_dir"]
    v = subprocess.run([py, "-B", str(HERE.parent / "build_registry.py"), "verify", "--outdir", str(art_dir),
                        "--workers", str(workers)], capture_output=True, text=True)
    vres = json.loads(v.stdout[v.stdout.index("{"):])
    same_reg = sha(art_dir / "REGISTRY.json") == sha(regp)
    res["S01"] = {**vres, "registry_file_identical_to_committed": same_reg, "pass": vres["pass"] and same_reg}
    x = subprocess.run([py, "-B", str(HERE.parent / "xcheck_registry.py"), "xcheck", "--registry", str(regp),
                        "--out", str(outdir / "XA.json")], capture_output=True, text=True)
    res["S02"] = {"pass": x.returncode == 0, "sha256": sha(outdir / "XA.json")}
    p = subprocess.run([py, "-B", str(HERE.parent / "xcheck_registry.py"), "probe", "--out", str(outdir / "PROBE.json")],
                       capture_output=True, text=True)
    res["S03"] = {"pass": p.returncode == 0, "sha256": sha(outdir / "PROBE.json")}
    q = subprocess.run([py, "-B", str(HERE.parent / "qualify_ad.py"), "run", "--out", str(outdir / "QUALIFICATION_AD.json")],
                       capture_output=True, text=True)
    res["S04"] = {"pass": q.returncode == 0, "sha256": sha(outdir / "QUALIFICATION_AD.json")}
    rep = DC.replay_text(RECORDS)
    (outdir / "REPLAY.json").write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    res["S05"] = {"pass": rep["pass"], "sha256": sha(outdir / "REPLAY.json")}
    ge = subprocess.run([py, "-B", str(HERE.parent / "gate_eval.py"), "--registry", str(regp),
                         "--out", str(outdir / "GATE_RESULT.json")], capture_output=True, text=True)
    gate = json.loads((outdir / "GATE_RESULT.json").read_text())
    res["S06"] = {"level": gate["level"], "smallest_dominating_scale": gate["smallest_dominating_scale"],
                  "pass": ge.returncode == 0 and gate["level"] == "USEFUL", "sha256": sha(outdir / "GATE_RESULT.json")}
    xbr = subprocess.run([py, "-B", str(HERE.parent / "xcheck_registry.py"), "xb", "--registry", str(regp),
                          "--out", str(outdir / "XB.json")], capture_output=True, text=True)
    res["S10"] = {"pass": xbr.returncode == 0, "sha256": sha(outdir / "XB.json")}
    res["S11"] = s11_kappa_bounds()
    s09 = s09_assembly_semantics(reg)
    (outdir / "S09.json").write_text(json.dumps(s09, indent=1, sort_keys=True) + "\n")
    res["S09"] = {"pass": s09["pass"], "m1_max_relative_excess": s09["m1_max_relative_excess"]}
    res["QUALIFIED"] = all(v.get("pass") for k, v in res.items() if k.startswith("S"))
    res["protocol_sha256"] = protocol_sha256
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run",))
    ap.add_argument("--protocol-sha256", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--workers", type=int, default=7)
    a = ap.parse_args()
    res = run(a.protocol_sha256, Path(a.outdir), a.workers)
    Path(a.outdir, "QUALIFICATION_RESULT.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps(res, indent=1))
    return 0 if res["QUALIFIED"] else 1


if __name__ == "__main__":
    sys.exit(main())
