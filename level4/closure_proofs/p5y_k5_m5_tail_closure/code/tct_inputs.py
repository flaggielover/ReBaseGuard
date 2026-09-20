"""Campaign B: REPLAY measurement of the theorem-TC input fields of a tail cell that are ADOPTED K1 quantities.

No order-3 candidate of F is proposed and no order-3 field of F is written, so this is not a new real scientific
evaluation: every field emitted here is a recomputation of an adopted K1 / Aux3 quantity, and the frozen identity gate
of the Campaign-A producer (`tc_producer.identity_gate`, imported by pin) compares the recomputation against the sealed
K1 record before anything is written. The guard stays DENY; this runs before any authorization.

Emitted (exact rational strings): rho, e0, left, right, norms.k[0..4], norms.j[0..4], sup_S0[0..4], and per r = 0..4
delta_F, delta_D, delta_H (adopted midpoint residuals), eps_src[0..3] (frozen midpoint DAG for k <= 2, adopted Aux3
`midpoint_order3_eps` for k = 3), sup.{F,D,H} (adopted candidate suprema), H_at_a (the adopted order-2 candidate at the
atom) and W2[r:j] (the adopted whole-cell W enclosures). NOT emitted: anything derived from a candidate of F''' .

    python -B tct_inputs.py --cell K --record REC.json --record-sha256 SHA --out OUT.json
"""
from __future__ import annotations

import os
import sys

_PINNED = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}
if "numpy" not in sys.modules:
    os.environ.update(_PINNED)
    os.environ["K1_THREADS_PINNED"] = "1"

import argparse                                                        # noqa: E402
import hashlib                                                         # noqa: E402
import json                                                            # noqa: E402
import resource                                                        # noqa: E402
import time                                                            # noqa: E402
from fractions import Fraction as F                                    # noqa: E402
from pathlib import Path                                               # noqa: E402

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CAMPAIGN_A_CODE = REPO / "level4/closure_proofs/p5y_k5_lower_front_order3/code"
SCHEMA = "rebaseguard.p5y.k5.m5-tail.tct-inputs.v1"
BITS = 256
TAIL_CELLS = (305, 306, 307, 308, 309)


class TCTInputRefusal(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _fstr(x: F) -> str:
    return f"{x.numerator}/{x.denominator}"


def _src(r: int, k: int) -> str:
    return f"Sclosed:{k}" if r == 0 else f"S:{r}:{k}"


def measure(cell_index: int, record: dict, record_sha256: str) -> dict:
    if cell_index not in TAIL_CELLS:
        raise TCTInputRefusal(f"cell {cell_index} is outside the m = 5 tail {TAIL_CELLS}")
    if str(CAMPAIGN_A_CODE) not in sys.path:
        sys.path.insert(0, str(CAMPAIGN_A_CODE))
    import tc_producer as TP                               # frozen Campaign-A producer: chain import + identity gate
    Z = TP._import_chain()
    if os.environ.get("K1_THREADS_PINNED") != "1":
        raise TCTInputRefusal("thread environment was not pinned before numpy import")
    if record.get("cell_index") != cell_index or record.get("detector") != "CUSUM":
        raise TCTInputRefusal("record does not identify itself as this CUSUM cell")
    cell = next(c for c in Z["spec"].CELLS if c["detector"] == "CUSUM" and c["index"] == cell_index)
    cls = type("ReplayAux3Certifier", (Z["AC"].Aux3Certifier,),
               {"vec": staticmethod(Z["O3"].Pair), "z_range": Z["O3"].Z_RANGE})
    mag, lo, hi = Z["mag"], Z["lo"], Z["hi"]
    t0 = time.process_time()
    guard = Z["SG"].ScipyGuard()
    with guard:
        with Z["workprec"](BITS):
            cert = cls(cell, bits=BITS).prepare()
            cert.all_residuals()
            cert.aux_residuals()
            mid = Z["AP"].cell_dag(cert, "delta_mid")
            aux_mid = Z["AC"].midpoint_order3_eps(cert, mid.nodes)
            node_ref = Z["AR"].AuxiliaryRefinement(cert, mid.nodes, aux_mid)
            cellwise = Z["AP"].RefinedCellValues(cert, Z["AP"].cell_dag(cert, "delta_cell"), node_ref)
            ident = TP.identity_gate(Z, cert, mid, aux_mid, cellwise, record)
            out = {"schema": SCHEMA, "mode": "replay_measurement", "cell": cell_index,
                   "k1_record_sha256": record_sha256, "identity_gate": ident,
                   "e0": _fstr(F(cert.e0)), "rho": _fstr(F(cert.rho)), "left": _fstr(F(cert.left)),
                   "right": _fstr(F(cert.right)),
                   "norms": {"k": [_fstr(mag(cert.norms["k"][i])) for i in range(5)],
                             "j": [_fstr(mag(cert.norms["j"][i])) for i in range(5)]},
                   "sup_S0": [_fstr(mag(Z["O2"].sup_source_derivative_on(n, cert.left, cert.right)))
                              for n in range(5)],
                   "r": {}, "W2": {},
                   "order3_fields_present": False}
            for r in range(5):
                Ha = cert.origin(("H", r, 0))
                out["r"][str(r)] = {
                    "delta_F": _fstr(mag(cert.residuals[f"F_{r}"]["delta_mid"])),
                    "delta_D": _fstr(mag(cert.residuals[f"dF_{r}"]["delta_mid"])),
                    "delta_H": _fstr(mag(cert.residuals[f"H_{r}"]["delta_mid"])),
                    "eps_src": [_fstr(mag(mid.nodes[_src(r, k)])) for k in range(3)]
                               + [_fstr(mag(aux_mid[_src(r, 3)]))],
                    "sup": {fam: _fstr(mag(cert.sup[fam, r, 0])) for fam in ("F", "D", "H")},
                    "H_at_a": [_fstr(lo(Ha)), _fstr(hi(Ha))],
                }
            for r in range(4):
                for j in range(0, 4 - r):
                    w = Z["assembly"].enclose(cert.origin(("W", (r, j), 2)), cellwise.get(f"W:{r}:{j}:2"))
                    out["W2"][f"{r}:{j}"] = [_fstr(lo(w)), _fstr(hi(w))]
    if hasattr(guard, "require_clean"):
        guard.require_clean()
    for r in range(5):
        if any(key.startswith("G") or key == "delta_G" or key == "abs_G_at_a" for key in out["r"][str(r)]):
            raise TCTInputRefusal("an order-3 field of F leaked into the replay measurement")
    out["metadata"] = {"cpu_seconds": time.process_time() - t0,
                       "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", type=int, required=True)
    ap.add_argument("--record", required=True)
    ap.add_argument("--record-sha256", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raw = Path(a.record).read_bytes()
    if sha(raw) != a.record_sha256:
        raise TCTInputRefusal("K1 record does not match the given sha256")
    res = measure(a.cell, json.loads(raw), a.record_sha256)
    meta = res.pop("metadata")
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({"cell": a.cell, "sha256": sha(data), **meta}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
