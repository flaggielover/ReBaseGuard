"""P5Y-K4R1 near-zero successor certificate (anchored third-order Taylor certificate, route D3).

Authoritative specification: SPECIFICATION.md + config/GATE.json + config/RESIDUAL_UNIVERSE.json + config/PROVENANCE.json.
Exact rational arithmetic (fractions.Fraction) over recorded outward endpoints; floats are refused; strict inequalities.

For each residual m in {2, 3, 5} of CUSUM, with a = a_m the right end of the historical residual region:

  G_m = D0.hi - L1_m * e0^2 / 2                   upper bound of R'(0)
        D0 = K1 cell-0 D_interval (encloses R'(e0), e0 = 5083/20000000); L1_m = slot-1 lower bound of R''' on [0, x1]
        (R'(0) = R'(e0) - int_0^e0 R'', and R''(t) = int_0^t R''' >= t*L1 because R''(0) = 0 by oddness)
  T_m = min( M3_m(a) , U0_m + a^2/2 * M5_m(a) )  upper bound of R''' on [0, a]
        M_n(a) = T-EXT certified majorant of sup_[0,a] |R^(n)|; U0 = slot-1 upper end of the enclosure of R'''(0)
        (R'''(e) = R'''(0) + int_0^e R'''' and |R''''(s)| <= s*M5 because R''''(0) = 0 by oddness)
  B_m = G_m + a^2/6 * max(T_m, 0)
  PASS_m  iff  B_m < 0        (then for every e in (0, a]: R(e) = e*R'(0) + e^3/6*R'''(xi) <= e*B_m < 0)

Premises: P5-T3 (R odd, so R(0) = R''(0) = R''''(0) = 0), P5X L5 (R in C^inf; qualitative use only).

Subcommands:
  preflight   value-blind identity/geometry/type checks over the real sources; never computes G, T or B
  execute     requires config/FREEZE.json (hash-bound); computes the certificate and the successor assembly exactly
              once and refuses to overwrite its output
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CONFIG = NS / "config"
M_RESIDUAL = ("2", "3", "5")
DETECTORS = ("CUSUM", "SR")
M_SCOPE = ("1", "2", "3", "5")
E_CAP = F(2)


class K4R1Refusal(RuntimeError):
    """Input, identity or mode not admissible. Never a scientific outcome."""


# ------------------------------------------------------------------ primitives
def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha_file(p) -> str:
    return sha_bytes(Path(p).read_bytes())


def fr(x) -> F:
    if isinstance(x, float) or isinstance(x, bool):
        raise K4R1Refusal(f"non-exact value {x!r} in a certified field")
    if not isinstance(x, (str, int)):
        raise K4R1Refusal(f"unexpected type {type(x).__name__} in a certified field")
    return F(x)


def pair0(p) -> F:
    """[p, s] exact pair with s == 0 (non-symbolic)."""
    if fr(p[1]) != 0:
        raise K4R1Refusal("symbolic geometry where a numeric one is required")
    return fr(p[0])


def interval(d) -> tuple[F, F]:
    lo, hi = fr(d["lo"]), fr(d["hi"])
    if lo > hi:
        raise K4R1Refusal("malformed interval lo > hi")
    return lo, hi


# ------------------------------------------------------------------ the certificate (pure, exact)
def g_bound(D0_hi: F, L1: F, e0: F) -> F:
    return D0_hi - L1 * e0 * e0 / 2


def t_bound(M3: F, U0: F, M5: F, a: F) -> F:
    if M3 < 0 or M5 < 0:
        raise K4R1Refusal("negative majorant")
    return min(M3, U0 + a * a / 2 * M5)


def b_bound(G: F, T: F, a: F) -> F:
    return G + a * a / 6 * max(T, F(0))


def decide(G: F, T: F, a: F) -> dict:
    if a <= 0:
        raise K4R1Refusal("non-positive residual end")
    B = b_bound(G, T, a)
    return {"G": str(G), "T": str(T), "a": str(a), "B": str(B), "PASS": B < 0,
            "outcome": "K4R1_CERTIFIED" if B < 0 else "K4R1_CERTIFICATE_TOO_LOOSE"}


# ------------------------------------------------------------------ sources
def load_json_bound(entry: dict, repo: Path) -> dict:
    p = repo / entry["path"]
    if not p.exists():
        raise K4R1Refusal(f"source missing: {entry['path']}")
    if sha_file(p) != entry["sha256"]:
        raise K4R1Refusal(f"source hash drift: {entry['path']}")
    return json.loads(p.read_text())


def load_sources(prov: dict, repo: Path = REPO) -> dict:
    """Every bound source (data and premise documents) is hash-verified; only data sources are parsed."""
    out = {}
    for k, v in prov["sources"].items():
        if v.get("kind") == "json":
            out[k] = load_json_bound(v, repo)
        else:
            p = repo / v["path"]
            if not p.exists() or sha_file(p) != v["sha256"]:
                raise K4R1Refusal(f"premise document missing or drifted: {v['path']}")
    return out


def residual_from_report(report: dict) -> dict:
    """{m: [cells]} of CERTIFICATE_TOO_LOOSE cells in the historical K4 report, all (D,m)."""
    out = {}
    for key, v in report["per_Dm"].items():
        if v.get("too_loose_cells"):
            out[key] = sorted(v["too_loose_cells"])
    return out


def check_universe(universe: dict, report: dict) -> dict:
    """Refuse unless the frozen residual universe is exactly the historical residual. Returns {m: (cells, a)}."""
    hist = residual_from_report(report)
    declared = {f"{r['detector']}|m={r['m']}": sorted(r["cells"]) for r in universe["residuals"]}
    if hist != declared:
        raise K4R1Refusal(f"residual universe {declared} != historical residual {hist}")
    out = {}
    for r in universe["residuals"]:
        key = f"{r['detector']}|m={r['m']}"
        per = report["per_Dm"][key]
        if per["outcome"] != "K4_CERTIFICATE_TOO_LOOSE" or per.get("counterexample_cells"):
            raise K4R1Refusal(f"{key}: historical outcome is not a counterexample-free CERTIFICATE_TOO_LOOSE")
        cells = sorted(r["cells"])
        if cells != list(range(len(cells))):
            raise K4R1Refusal(f"{key}: residual cells are not a prefix from cell 0")
        by_idx = {c["index"]: c for c in per["per_cell"]}
        if F(by_idx[0]["left"]) != 0:
            raise K4R1Refusal(f"{key}: residual does not start at e = 0")
        a = F(by_idx[cells[-1]]["right"])
        if a != F(r["a"]):
            raise K4R1Refusal(f"{key}: declared a {r['a']} != historical right end {a}")
        out[str(r["m"])] = (cells, a)
    return out


def extract_inputs(src: dict, universe: dict, prov: dict) -> dict:
    """All identity and geometry checks; returns exact per-m inputs. Computes no G, T or B."""
    report, k1, slot1, text = src["historical_report"], src["k1_cell0_record"], src["slot1_record"], src["text_result"]
    res = check_universe(universe, report)
    if set(res) != set(M_RESIDUAL) or universe["detector_scope"] != ["CUSUM"]:
        raise K4R1Refusal(f"residual m-scope {sorted(res)} is not exactly CUSUM m in {M_RESIDUAL}")
    # K1 cell-0 record
    if k1.get("detector") != "CUSUM" or k1.get("cell_index") != 0:
        raise K4R1Refusal("K1 record is not CUSUM cell 0")
    if k1.get("producer_identity_hash") != prov["identities"]["k1_cusum_producer_identity_hash"]:
        raise K4R1Refusal("K1 record producer identity differs from the frozen CUSUM producer")
    e0, rho = pair0(k1["e0"]), pair0(k1["rho"])
    if e0 != rho or e0 - rho != 0:
        raise K4R1Refusal("K1 cell 0 is not the cell [0, 2*e0]")
    if e0 != F(prov["geometry"]["k1_cell0_e0"]):
        raise K4R1Refusal("K1 cell-0 e0 differs from the frozen geometry")
    # slot-1 record: bound to that K1 record, point e = 0, hull [0, x1] with e0 <= x1
    s1 = slot1["scientific"]
    b, ctx = s1["binding"], s1["context"]
    if not (b["k1_cell_index"] == 0 and b["detector"] == "CUSUM" and b["record_sha256"] == prov["sources"]["k1_cell0_record"]["sha256"]
            and fr(b["left"]) == 0 and fr(ctx["point_e"]) == 0):
        raise K4R1Refusal("slot-1 record is not bound to K1 CUSUM cell 0 at the point e = 0")
    x1 = fr(ctx["x1"])
    if x1 != fr(b["right"]) or not (e0 <= x1):
        raise K4R1Refusal("slot-1 hull [0, x1] does not contain [0, e0]")
    # T-EXT result: sealed transport of that slot-1 record
    if text.get("sealed_record_sha256") != prov["sources"]["slot1_record"]["sha256"]:
        raise K4R1Refusal("T-EXT result is not the transport of the bound slot-1 record")
    rows = text["rows"]
    out = {}
    for m in M_RESIDUAL:
        cells, a = res[m]
        hits = [r for r in rows if fr(r["x_hi"]) == a]
        if len(hits) != 1:
            raise K4R1Refusal(f"m={m}: no unique T-EXT hull with x_hi == a = {a}")
        row = hits[0]
        eta = fr(row["hull_norms"]["eta"])
        # eta is the outward (upward) 256-bit rounding of x_hi: the majorants hold on [0, eta] which contains [0, a]
        if not (a <= eta <= a * (1 + F(1, 2 ** 200))):
            raise K4R1Refusal(f"m={m}: T-EXT hull eta is not an outward rounding of x_hi")
        ent = k1["m"][m]
        if ent.get("detector") != "CUSUM":
            raise K4R1Refusal(f"m={m}: K1 entry detector")
        D0 = interval(ent["D_interval"])
        pm = s1["per_m"][m]
        L1, U0 = fr(pm["L1"]), fr(pm["U0"])
        M3, M5 = fr(row["M"]["3"][m]), fr(row["M"]["5"][m])
        out[m] = {"cells": cells, "a": a, "e0": e0, "x1": x1, "hull_cell": row["cell"],
                  "_D0_hi": D0[1], "_L1": L1, "_U0": U0, "_M3": M3, "_M5": M5}
    return out


# ------------------------------------------------------------------ successor assembly
def assemble(report: dict, universe_res: dict, certs: dict) -> dict:
    """Historical K4 per-(D,m) outcomes + K4R1 residual certificates -> coverage of (0, 2] for all 8 (D,m)."""
    per = {}
    for d in DETECTORS:
        for m in M_SCOPE:
            key = f"{d}|m={m}"
            h = report["per_Dm"][key]
            cells = sorted(h["per_cell"], key=lambda c: F(c["left"]))
            contiguous = (bool(cells) and F(cells[0]["left"]) == 0 and F(cells[-1]["right"]) >= E_CAP
                          and all(F(x["right"]) == F(y["left"]) for x, y in zip(cells, cells[1:])))
            if not contiguous:
                per[key] = {"status": "FAIL", "reason": "historical cover not contiguous from 0 to >= 2"}
                continue
            if h["outcome"] == "K4_CELLWISE_ALL_CERTIFIED":
                ok = all(c["how"] in ("CHAIN_RPRIME_NEGATIVE", "DIRECT_R_NEGATIVE") for c in cells)
                per[key] = {"status": "PASS" if ok else "FAIL", "source": "INHERITED_HISTORICAL_K4",
                            "covered_up_to": cells[-1]["right"]}
                continue
            if d != "CUSUM" or m not in universe_res:
                per[key] = {"status": "FAIL", "reason": f"historical {h['outcome']} outside the K4R1 universe"}
                continue
            rcells, a = universe_res[m]
            rest = [c for c in cells if c["index"] not in rcells]
            hist_ok = (all(c["how"] == "CERTIFICATE_TOO_LOOSE" for c in cells if c["index"] in rcells)
                       and all(c["how"] in ("CHAIN_RPRIME_NEGATIVE", "DIRECT_R_NEGATIVE") for c in rest)
                       and not h.get("counterexample_cells")
                       and bool(rest) and F(rest[0]["left"]) == a)
            cert = certs[m]
            status = "PASS" if (hist_ok and cert["PASS"]) else "FAIL"
            per[key] = {"status": status, "source": "K4R1_CERTIFICATE (0, a] + INHERITED_HISTORICAL_K4 [a, end]",
                        "a": str(a), "k4r1_outcome": cert["outcome"], "historical_rest_certified": hist_ok,
                        "covered_up_to": cells[-1]["right"]}
    return {"per_Dm": per, "complete": all(v["status"] == "PASS" for v in per.values())}


# ------------------------------------------------------------------ freeze gate
def verify_freeze(freeze_path: Path = CONFIG / "FREEZE.json", repo: Path = REPO) -> dict:
    if not freeze_path.exists():
        raise K4R1Refusal("EXECUTION_LOCKED: config/FREEZE.json absent")
    fz = json.loads(freeze_path.read_text())
    hp = freeze_path.with_name("FREEZE_HASH")
    if not hp.exists() or hp.read_text().strip() != sha_file(freeze_path):
        raise K4R1Refusal("EXECUTION_LOCKED: FREEZE_HASH missing or mismatched")
    if fz.get("qualification_verdict") != "QUALIFICATION_ACCEPTED":
        raise K4R1Refusal("EXECUTION_LOCKED: qualification not accepted")
    for rel, h in fz["bound_files"].items():
        p = repo / rel
        if not p.exists() or sha_file(p) != h:
            raise K4R1Refusal(f"EXECUTION_LOCKED: bound file drift {rel}")
    try:
        here = str(Path(__file__).resolve().relative_to(repo.resolve()))
    except ValueError:
        raise K4R1Refusal("EXECUTION_LOCKED: implementation lies outside the bound repository") from None
    if here not in fz["bound_files"]:
        raise K4R1Refusal("EXECUTION_LOCKED: this implementation is not bound by the freeze")
    return fz


def read_config():
    return (json.loads((CONFIG / "RESIDUAL_UNIVERSE.json").read_text()),
            json.loads((CONFIG / "PROVENANCE.json").read_text()))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("preflight")
    ex = sub.add_parser("execute")
    ex.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    universe, prov = read_config()
    if a.cmd == "preflight":
        src = load_sources(prov)
        inp = extract_inputs(src, universe, prov)
        print(json.dumps({"PREFLIGHT": "PASS", "values_computed": False,
                          "residual": {m: {"cells": v["cells"], "a": str(v["a"]), "hull_cell": v["hull_cell"]}
                                       for m, v in inp.items()}}, sort_keys=True))
        return 0
    fz = verify_freeze()
    out = Path(a.out)
    if out.exists():
        raise K4R1Refusal("EXACT_ONCE: output already exists")
    t0w, t0c = time.time(), time.process_time()
    src = load_sources(prov)
    inp = extract_inputs(src, universe, prov)
    certs = {}
    for m, v in inp.items():
        G = g_bound(v["_D0_hi"], v["_L1"], v["e0"])
        T = t_bound(v["_M3"], v["_U0"], v["_M5"], v["a"])
        certs[m] = {**decide(G, T, v["a"]), "cells": v["cells"], "hull_cell": v["hull_cell"],
                    "inputs": {"D0_hi": str(v["_D0_hi"]), "L1": str(v["_L1"]), "U0": str(v["_U0"]),
                               "M3": str(v["_M3"]), "M5": str(v["_M5"]), "e0": str(v["e0"]), "x1": str(v["x1"])},
                    "T_branch": "M3" if v["_M3"] <= v["_U0"] + v["a"] ** 2 / 2 * v["_M5"] else "U0+a^2/2*M5"}
    asm = assemble(src["historical_report"], {m: (v["cells"], v["a"]) for m, v in inp.items()}, certs)
    science = all(c["PASS"] for c in certs.values()) and asm["complete"]
    res = {"schema": "rebaseguard.p5y.k4r1.result.v1", "freeze_sha256": sha_file(CONFIG / "FREEZE.json"),
           "freeze_commit_declared": fz.get("freeze_commit"), "arithmetic": "exact rational",
           "certificates": {f"CUSUM|m={m}": c for m, c in sorted(certs.items())}, "assembly": asm,
           "K4R1_COMPACT_RESIDUAL_COVERAGE": "PASS" if all(c["PASS"] for c in certs.values()) else "FAIL",
           "K4R1_COMPLETE_K4_ASSEMBLY": "PASS" if asm["complete"] else "FAIL",
           "K4R1_SUCCESSOR_SCIENCE": "PASS" if science else "NOT_CLOSED",
           "residual_remaining": {f"CUSUM|m={m}": c["cells"] for m, c in sorted(certs.items()) if not c["PASS"]},
           "new_real_addresses": 0,
           "runtime": {"cpu_seconds": time.process_time() - t0c, "wall_seconds": time.time() - t0w,
                       "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0w))}}
    out.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in ("K4R1_COMPACT_RESIDUAL_COVERAGE", "K4R1_COMPLETE_K4_ASSEMBLY",
                                          "K4R1_SUCCESSOR_SCIENCE")}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except K4R1Refusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(3)
