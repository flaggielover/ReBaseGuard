"""Theorem-TC producer: certified midpoint inputs of the Taylor-cell enclosure at one CUSUM K1 cell.

Runs on rebaseguard-vultr-02 in the frozen Aux5 venv. Imports the frozen chain in place (nothing assigned into any
imported module):

    frozen order-3 producer   cusum_order3.Order3Certifier (Aux3Certifier + degree-12 G_r candidates)   [mode real]
    frozen Aux3 certifier     aux_certifier.Aux3Certifier (no G_r)                                        [mode replay]
    frozen K1 science         all_residuals, aux_residuals, aux_propagate.cell_dag / RefinedCellValues,
                              aux_certifier.midpoint_order3_eps, aux_refine.AuxiliaryRefinement,
                              rung3_residual.g_residual (real only), order2.sup_source_derivative_on

Modes
  replay  qualification only: recomputes the adopted K1/Aux3 midpoint quantities of a cell and checks them against the
          sealed K1 record (identity gate). No order-3 candidate of F is proposed: the extraction code path is exercised
          with a SYNTHETIC G := Hhat (the real operator evaluates the order-3 right-hand side in memory; only a shape /
          finiteness summary is written, no scientific field).
  real    the governed run: refuses unless the frozen protocol is committed and pin-exact, a committed QUALIFIED result
          exists for it at the freeze commit, a committed AUTHORIZATION covers exactly the pre-registered addresses and
          the committed GUARD is ALLOW for exactly those addresses; then computes the cell, applies the identity gate,
          and writes the certified TC inputs (exact rational strings). Nothing precedes the gate.

    python -B tc_producer.py replay --cell K --record REC.json --out OUT.json
    python -B tc_producer.py real   --cell K --record REC.json --protocol-sha256 SHA --out OUT.json
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
import subprocess                                                      # noqa: E402
import time                                                            # noqa: E402
from fractions import Fraction as F                                    # noqa: E402
from pathlib import Path                                               # noqa: E402

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
NS_REL = "level4/closure_proofs/p5y_k5_lower_front_order3"
ORDER3_CODE = REPO / "level4/closure_proofs/p5y_k5_cusum_order3_real_producer/code"
PROTOCOL_REL = NS_REL + "/config/TC_PROTOCOL.json"
EVID_REL = NS_REL + "/evidence/tc_r1"
SCHEMA = "rebaseguard.p5y.k5.lower-front-order3.tc-cell.v1"
BITS = 256


class TCProducerRefusal(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(*args) -> str:
    return subprocess.run(["git", "-C", str(REPO), *args], check=True, capture_output=True, text=True).stdout


# ------------------------------------------------------------------ governance gate (runs FIRST in mode real)
def committed_json(rel: str) -> dict:
    try:
        _git("ls-files", "--error-unmatch", rel)
    except Exception:
        raise TCProducerRefusal(f"{rel} is not committed")
    disk = (REPO / rel).read_bytes()
    head = _git("show", f"HEAD:{rel}").encode()
    if disk != head:
        raise TCProducerRefusal(f"{rel} differs from its committed bytes")
    return json.loads(disk)


def frozen_guard(protocol_sha256: str) -> dict:
    raw = (REPO / PROTOCOL_REL).read_bytes()
    if sha(raw) != protocol_sha256:
        raise TCProducerRefusal("protocol does not match the given sha256")
    proto = committed_json(PROTOCOL_REL)
    if _git("status", "--porcelain", "--", NS_REL).strip():
        raise TCProducerRefusal("namespace has uncommitted changes")
    added = _git("log", "--diff-filter=A", "--format=%H", "--", PROTOCOL_REL).split()
    if not added:
        raise TCProducerRefusal("cannot find the freeze commit")
    freeze = added[-1]
    changed = _git("diff", "--name-only", freeze, "HEAD", "--", NS_REL).split()
    extra = [c for c in changed if not c.startswith(EVID_REL + "/")]
    if extra:
        raise TCProducerRefusal(f"namespace changed after the freeze outside {EVID_REL}: {extra[:5]}")
    bad = [rel for rel, h in proto["pins"].items() if sha((REPO / rel).read_bytes()) != h]
    if bad:
        raise TCProducerRefusal(f"pins do not match: {bad[:5]}")
    return {"proto": proto, "freeze": freeze, "head": _git("rev-parse", "HEAD").strip()}


def require_authorized(cell: int, protocol_sha256: str) -> dict:
    g = frozen_guard(protocol_sha256)
    proto = g["proto"]
    addresses = proto["addresses"]["cells"]
    qual = committed_json(EVID_REL + "/QUALIFICATION_RESULT.json")
    if qual.get("QUALIFIED") is not True or qual.get("protocol_sha256") != protocol_sha256:
        raise TCProducerRefusal("no committed QUALIFIED qualification for this protocol")
    if qual.get("S00", {}).get("head") != g["freeze"]:
        raise TCProducerRefusal("qualification did not run at the freeze commit")
    qual_sha = sha((REPO / (EVID_REL + "/QUALIFICATION_RESULT.json")).read_bytes())
    auth = committed_json(EVID_REL + "/AUTHORIZATION.json")
    if auth.get("verdict") != "AUTHORIZED" or auth.get("protocol_sha256") != protocol_sha256 \
            or auth.get("addresses") != addresses or auth.get("qualification_result_sha256") != qual_sha:
        raise TCProducerRefusal("no committed AUTHORIZATION for exactly the pre-registered addresses and this "
                                "qualification")
    auth_sha = sha((REPO / (EVID_REL + "/AUTHORIZATION.json")).read_bytes())
    guard = committed_json(EVID_REL + "/GUARD.json")
    if guard.get("state") != "ALLOW" or guard.get("addresses") != addresses \
            or guard.get("protocol_sha256") != protocol_sha256 or guard.get("authorization_sha256") != auth_sha:
        raise TCProducerRefusal("guard is not ALLOW for exactly the pre-registered addresses and this authorization")
    q_add = _git("log", "--diff-filter=A", "--format=%H", "--", EVID_REL + "/QUALIFICATION_RESULT.json").split()[-1]
    a_add = _git("log", "--diff-filter=A", "--format=%H", "--", EVID_REL + "/AUTHORIZATION.json").split()[-1]
    g_last = _git("log", "-1", "--format=%H", "--", EVID_REL + "/GUARD.json").strip()

    def ancestor(x, y):
        return subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", x, y]).returncode == 0
    if q_add == a_add or not ancestor(q_add, a_add) or not ancestor(a_add, g_last):
        raise TCProducerRefusal("commit order qualification -> authorization -> guard is violated")
    if cell not in addresses:
        raise TCProducerRefusal(f"cell {cell} is not a pre-registered address")
    return {"head": g["head"], "freeze_commit": g["freeze"], "authorization_sha256": auth_sha,
            "guard_sha256": sha((REPO / (EVID_REL + "/GUARD.json")).read_bytes()), "protocol_sha256": protocol_sha256,
            "protocol": proto}


# ------------------------------------------------------------------ frozen chain
def _import_chain():
    if str(ORDER3_CODE) not in sys.path:
        sys.path.insert(0, str(ORDER3_CODE))
    import cusum_order3                                                # noqa: F401  (inserts the Aux5 bootstrap)
    import aux_certifier
    import aux_propagate
    import aux_refine
    import order2
    import rung3_residual
    import scipy_guard
    import spec
    from intervals import lower_fraction, mag_fraction, upper_fraction, workprec
    import assembly
    return {"O3": cusum_order3, "AC": aux_certifier, "AP": aux_propagate, "AR": aux_refine, "O2": order2,
            "RR": rung3_residual, "SG": scipy_guard, "spec": spec, "lo": lower_fraction, "mag": mag_fraction,
            "hi": upper_fraction, "workprec": workprec, "assembly": assembly}


def _src(r: int, k: int) -> str:
    return f"Sclosed:{k}" if r == 0 else f"S:{r}:{k}"


def _fstr(x: F) -> str:
    return f"{x.numerator}/{x.denominator}"


def identity_gate(Z, cert, mid, aux_mid, cellwise, record: dict) -> dict:
    """Recomputed adopted quantities must equal the sealed K1 record exactly (exact rational comparison)."""
    mag = Z["mag"]
    diffs = []
    obj = record["objects"]
    for name, v in cert.residuals.items():
        if name not in obj:
            diffs.append(f"object {name} absent from the record")
        elif mag(v["delta_mid"]) != F(obj[name]["delta_mid"]):
            diffs.append(f"delta_mid {name}")
    if set(obj) != set(cert.residuals):
        diffs.append("object name sets differ")
    for key, val in record["eps_mid"].items():
        if key not in mid.nodes or mag(mid.nodes[key]) != F(val):
            diffs.append(f"eps_mid {key}")
    for key, val in record["eps_cell"].items():
        if key not in cellwise.nodes or mag(cellwise.nodes[key]) != F(val):
            diffs.append(f"eps_cell {key}")
    # The adopted Aux5 run serialised the Aux3 evidence (qualify5._aux_record) OUTSIDE its workprec(256) block, i.e.
    # at python-flint's default 53-bit context, where mag_fraction rounds abs_upper up to 53 bits. Reproduce that
    # rendering exactly, and require the 256-bit value to be no larger (same ball, finer rounding).
    from flint import ctx as _ctx
    aux = record["auxiliary_evidence"]
    pairs = [(f"aux midpoint_eps {k}", aux_mid.get(k), v) for k, v in aux["midpoint_eps"].items()]
    pairs += [(f"aux object {k}", (cert.aux.get(k) or {}).get("delta_mid"), v["delta_mid"])
              for k, v in aux["objects"].items()]
    pairs += [(f"aux candidate_sup {k}", cert.sup.get(tuple(int(x) if x.isdigit() else x for x in k.split(":")))
               if not k.startswith("W:") else None, v) for k, v in aux["candidate_suprema"].items()
              if not k.startswith("W:")]
    fine = {name: (mag(x) if x is not None else None) for name, x, _ in pairs}
    saved = _ctx.prec
    try:
        _ctx.prec = 53
        coarse = {name: (mag(x) if x is not None else None) for name, x, _ in pairs}
    finally:
        _ctx.prec = saved
    for name, _, val in pairs:
        if coarse[name] is None:
            diffs.append(f"{name} absent")
        elif coarse[name] != F(val) or fine[name] > F(val):
            diffs.append(f"{name} {float(coarse[name]):.17g} != {float(F(val)):.17g}")
    checked = len(cert.residuals) + len(record["eps_mid"]) + len(record["eps_cell"]) + len(pairs)
    if checked < 150:
        raise TCProducerRefusal(f"identity gate compared only {checked} fields")
    if diffs:
        raise TCProducerRefusal(f"recomputation differs from the sealed K1 record: {diffs[:8]}")
    return {"identical": True, "fields_compared": checked}


def extract(Z, cert, mid, aux_mid, cellwise, g) -> dict:
    """Every theorem-TC input field of one cell (exact rational strings)."""
    mag, lo, hi = Z["mag"], Z["lo"], Z["hi"]
    out = {"norms": {"k": [_fstr(mag(cert.norms["k"][i])) for i in range(5)],
                     "j": [_fstr(mag(cert.norms["j"][i])) for i in range(5)]},
           "sup_S0": [_fstr(mag(Z["O2"].sup_source_derivative_on(n, cert.left, cert.right))) for n in range(5)],
           "r": {}, "W2": {}}
    for r in range(5):
        Ha, Ga = cert.origin(("H", r, 0)), cert.origin(("G", r, 0))
        out["r"][str(r)] = {
            "delta_F": _fstr(mag(cert.residuals[f"F_{r}"]["delta_mid"])),
            "delta_D": _fstr(mag(cert.residuals[f"dF_{r}"]["delta_mid"])),
            "delta_H": _fstr(mag(cert.residuals[f"H_{r}"]["delta_mid"])),
            "delta_G": _fstr(mag(g[r]["delta_mid"])),
            "eps_src": [_fstr(mag(mid.nodes[_src(r, k)])) for k in range(3)] + [_fstr(mag(aux_mid[_src(r, 3)]))],
            "sup": {fam: _fstr(mag(cert.sup[fam, r, 0])) for fam in ("F", "D", "H", "G")},
            "H_at_a": [_fstr(lo(Ha)), _fstr(hi(Ha))], "abs_G_at_a": _fstr(mag(Ga)),
        }
    for r in range(4):
        for j in range(0, 4 - r):
            w = Z["assembly"].enclose(cert.origin(("W", (r, j), 2)), cellwise.get(f"W:{r}:{j}:2"))
            out["W2"][f"{r}:{j}"] = [_fstr(lo(w)), _fstr(hi(w))]
    return out


def _structure(fields: dict) -> dict:
    """Replay-mode summary: shape and finiteness only (the synthetic-G fields are never written)."""
    vals = []

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        else:
            vals.append(F(x))
    walk(fields)
    nonneg = all(F(v) >= 0 for r in fields["r"].values() for key in ("delta_F", "delta_D", "delta_H", "delta_G")
                 for v in [r[key]])
    return {"objects": len(fields["r"]), "W2": len(fields["W2"]), "rational_fields": len(vals),
            "residuals_nonnegative": nonneg, "complete": len(fields["r"]) == 5 and len(fields["W2"]) == 10}


def module_check(proto: dict) -> int:
    """Every repository module file loaded so far is frozen: pinned by this protocol, or listed in the Aux5 producer
    manifest or in the order-3 producer manifest, with a matching sha256 (review r2 N-R2-2: run before AND after the
    computation, so a lazily imported module is covered too)."""
    frozen = dict(proto["pins"])
    for rel in ("level4/closure_proofs/p5y_k1_cusum_aux5_successor/manifests/producer_manifest_v3.json",
                "level4/closure_proofs/p5y_k5_cusum_order3_real_producer/config/ORDER3_PRODUCER_MANIFEST.json"):
        for k, v in json.loads((REPO / rel).read_bytes())["files"].items():
            frozen.setdefault(k, v)
    loaded = set()
    for mod in list(sys.modules.values()):
        f = getattr(mod, "__file__", None)
        if f:
            try:
                loaded.add(str(Path(f).resolve().relative_to(REPO)))
            except ValueError:
                pass
    bad = sorted(rel for rel in loaded if rel not in frozen or sha((REPO / rel).read_bytes()) != frozen[rel])
    if bad:
        raise TCProducerRefusal(f"repository modules outside the frozen set (or changed): {bad[:5]}")
    return len(loaded)


def runtime_checks(Z, proto: dict, cell_index: int, record_sha256: str) -> dict:
    """Mode real: the frozen runtime, the frozen order-3 producer identity, the pre-registered K1 record and no
    repository module outside the frozen pin list."""
    import platform
    import socket
    import numpy
    import scipy
    import flint
    rt = {"host": socket.gethostname(), "python": platform.python_version(), "numpy": numpy.__version__,
          "scipy": scipy.__version__, "python_flint": flint.__version__, "venv": sys.prefix}
    if rt != proto["runtime"]:
        raise TCProducerRefusal(f"runtime differs from the protocol: {rt}")
    if Z["O3"].producer_manifest_problems():
        raise TCProducerRefusal("frozen order-3 producer manifest mismatch")
    import manifest_v3
    if not manifest_v3.verify()["ok"]:
        raise TCProducerRefusal("frozen Aux5 producer manifest does not verify")
    if proto["k1_record_sha256"].get(str(cell_index)) != record_sha256:
        raise TCProducerRefusal("K1 record sha differs from the pre-registered one")
    mods = module_check(proto)
    flint.ctx.threads = 1
    return {"runtime": rt, "loaded_repository_modules_before": mods}


def compute(cell_index: int, record: dict, mode: str, protocol_sha256: str | None = None,
            record_sha256: str = "") -> dict:
    binding, proto = None, None
    if mode == "real":                                 # FIRST: the governance gate lives inside compute (N-R2-9)
        if not protocol_sha256:
            raise TCProducerRefusal("mode real needs the protocol sha256")
        binding = require_authorized(cell_index, protocol_sha256)
        proto = binding.pop("protocol")
    elif protocol_sha256:                              # replay with the protocol: runtime checks only, no gate
        proto = json.loads((REPO / PROTOCOL_REL).read_bytes())
        if sha((REPO / PROTOCOL_REL).read_bytes()) != protocol_sha256:
            raise TCProducerRefusal("protocol does not match the given sha256")
    Z = _import_chain()
    if os.environ.get("K1_THREADS_PINNED") != "1":
        raise TCProducerRefusal("thread environment was not pinned before numpy import")
    checks = runtime_checks(Z, proto, cell_index, record_sha256) if proto is not None else None
    if record.get("cell_index") != cell_index or record.get("detector") != "CUSUM":
        raise TCProducerRefusal("record does not identify itself as this CUSUM cell")
    cell = next(c for c in Z["spec"].CELLS if c["detector"] == "CUSUM" and c["index"] == cell_index)
    if mode == "real":
        cls = Z["O3"].Order3Certifier
    else:                                   # no order-3 candidate of F is ever proposed in replay mode
        cls = type("ReplayAux3Certifier", (Z["AC"].Aux3Certifier,),
                   {"vec": staticmethod(Z["O3"].Pair), "z_range": Z["O3"].Z_RANGE})
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
            ident = identity_gate(Z, cert, mid, aux_mid, cellwise, record)
            out = {"schema": SCHEMA, "mode": mode, "cell": cell_index, "e0": _fstr(F(cert.e0)),
                   "rho": _fstr(F(cert.rho)), "left": _fstr(F(cert.left)),
                   "right": _fstr(F(cert.right)), "identity_gate": ident, "k1_record_sha256": None,
                   "runtime_checks": checks}
            if mode == "real":
                g = {r: Z["RR"].g_residual(cert, r) for r in range(5)}
                out.update(extract(Z, cert, mid, aux_mid, cellwise, g))
            else:
                for r in range(5):          # SYNTHETIC G := Hhat (real operator, meaningless residual; code path only)
                    cert.P["G", r, 0] = cert.P["H", r, 0]
                    cert.sup["G", r, 0] = cert.sup["H", r, 0]
                g = {r: Z["RR"].g_residual(cert, r) for r in range(5)}
                out["extraction_code_path"] = _structure(extract(Z, cert, mid, aux_mid, cellwise, g))
    if hasattr(guard, "require_clean"):
        guard.require_clean()
    if proto is not None:
        out["runtime_checks"]["loaded_repository_modules_after"] = module_check(proto)
    out["binding"] = binding
    out["metadata"] = {"cpu_seconds": time.process_time() - t0,
                       "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("replay", "real"))
    ap.add_argument("--cell", type=int, required=True)
    ap.add_argument("--record", required=True)
    ap.add_argument("--record-sha256", required=True)
    ap.add_argument("--protocol-sha256")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.mode == "real" and not a.protocol_sha256:
        raise TCProducerRefusal("mode real needs --protocol-sha256")
    raw = Path(a.record).read_bytes()
    if sha(raw) != a.record_sha256:
        raise TCProducerRefusal("K1 record does not match the given sha256")
    res = compute(a.cell, json.loads(raw), a.mode, a.protocol_sha256, a.record_sha256)   # gate first inside
    meta = res.pop("metadata")                         # non-deterministic: never part of the sealed payload
    res["k1_record_sha256"] = a.record_sha256
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({"cell": a.cell, "mode": a.mode, "sha256": sha(data), **meta}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
