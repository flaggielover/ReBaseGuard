"""T3 per-patch producer.

Runs the T2-CLOSED final certifier path (t2_final_certifier: full 63-node DAG, O9 core, contracted endpoint
strips, repeated-multiplication raw shift, authorized P1 Lagrange factor) at the two drift modes the frozen
whole-cell algebra (ERROR_ALGEBRA sections 3-5) requires:

  mid  : e = e0, the exact cell midpoint              -> R_interval, D_interval, midpoint error chain
  cell : e = the whole cell [left, right] as one ball -> uniform-in-e residuals (H chain, W'' chain, crude seeds)

The certifier arithmetic is the committed T2 code path; this module only (a) evaluates it at a ball-valued e
(inclusion isotone, hence a bound for EVERY e in the cell), (b) on the reset patch evaluates every operator-image
node at x0 = (0,0), and (c) exports compact outward-safe records: every exported upper bound is the 256-bit
certified upper endpoint rounded UP to binary64 (never smaller).  No new scientific method.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import resource
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_equations as EQ
import sr_o9_patch_certifier as PC
import sr_o9_endpoint_strips as ES
import sr_o9_bint_p1 as BP
import t2_final_certifier as FC
from flint import arb

SCHEMA = "rebaseguard.p5y.k1.sr.o9.t3-patch.v1"


def fup(x) -> float:
    """Outward (upward) binary64 export of a nonnegative certified upper bound."""
    q = PC.fr_upper(x) if isinstance(x, arb) else Fr(x)
    if q <= 0:
        return 0.0
    f = float(q)
    if Fr(f) < q:
        f = math.nextafter(f, math.inf)
    return f


def _enc_exact(x: arb):
    m, e = x.man_exp()
    return [int(m), int(e)]


def cell_drifts(cell_index):
    """(e0, e_cell) as arb balls; e_cell = e0 +/- rho encloses [left, right] exactly."""
    g = T.cell_geometry(T.frozen_cell(cell_index))
    e_cell = g["e0"] + arb(0, g["rho"].abs_upper())
    if not (e_cell.contains(g["left"]) and e_cell.contains(g["right"])):
        raise T.T1Refusal("cell ball does not contain the cell endpoints")
    return g["e0"], e_cell, g


def core(i, j, e, cands, *, cand_hashes, C_gate: Fr, shared_cache, mode):
    """Mirror of t2_final_certifier.certify_patch_final (same calls, same order) with compact export."""
    T.require_precision()
    if PC.RawShiftDrift is not ES.FixedRawShiftDrift or PC.L.softplus_local_enclosure is not BP.softplus_local_enclosure_p1:
        raise T.T1Refusal("T2-closed machinery not installed")
    g = PC.patch_geometry(i, j, e)
    pan = PC.panelisation(i, j, g)
    if not pan["P1_PASS"]:
        raise T.T1Refusal(f"P1 fails on ({i},{j})")
    pan["panel_ids"] = FC.canonical_panel_ids(i, j, pan["n_z"])
    ctxt = PC.context(g, pan["h"])
    exprs = {n: (EQ.image(n) if n in EQ.IMAGE_NODES else EQ.rhs(n)) for n in FC.NODES}
    needed = sorted({k for ex_ in exprs.values() for k in ex_.terms}, key=lambda k: (T.BASIS_ORDER.index(k[0]), k[1]))
    stats = {"hits": 0, "misses": 0}
    core_acc = PC.contract_all(g, pan, ctxt, cands, needed, shared_cache, stats)
    shifts = sorted({s for _, s in needed})
    sides = {"L": ES.StripSide(g, g["L_c"], "L", shifts), "U": ES.StripSide(g, g["U_c"], "U", shifts)}
    acc, end = {}, {}
    for key in needed:
        c, s = key
        pL, eL, _dL = sides["L"].contract(cands[c], s)
        pU, eU, _dU = sides["U"].contract(cands[c], s)
        acc[key] = ([[core_acc[key][0][a][b] - pL[a][b] - pU[a][b] for b in range(ES.DP)] for a in range(ES.DP)],
                    core_acc[key][1], core_acc[key][2])
        end[key] = eL + eU
    srcs = PC.source_tms(g, ctxt)
    pb = PC.PatchBasis(g, ctxt)
    alpha, beta = -g["p_c"], -g["m_c"]
    # x0 = (0,0) is EXACTLY the lower-left corner of the reset patch (0,0): p_c = m_c = H = b/128, so
    # alpha = beta = -H lies on the boundary of the Taylor-model box |alpha|,|beta| <= H (remainders valid there).
    x0_here = bool((i, j) == (0, 0) and (g["p_c"] - g["H"]).contains(arb(0)) and (g["m_c"] - g["H"]).contains(arb(0)))
    out = {}
    for n in FC.NODES:
        ex_ = exprs[n]
        if n in EQ.IMAGE_NODES:
            ch, dmid, _ = PC.assemble(ex_, g, acc, end, srcs)
            width = ch["trunc"] + ch["tail"] + ch["end"] + ch["int"]
            fin = all(ch[k].is_finite() for k in ("trunc", "tail", "end", "int"))
            rec = {"w": fup(width) if fin else None, "fin": fin}
            if x0_here and fin:
                v = arb(0)
                for a in range(ES.DP):
                    for b in range(ES.DP):
                        v += dmid[a][b] * ES.ipow(alpha, a) * ES.ipow(beta, b)
                v = v + arb(0, (ch["trunc"] + ch["tail"] + ch["end"]).upper())
                rec["x0"] = {"mid": _enc_exact(arb(v.mid())), "rad": _enc_exact(arb(v.rad()))}
        else:
            fh, ex_f = PC.candidate_on_patch(pb, cands[n])
            ch, dmid, _ = PC.assemble(ex_, g, acc, end, srcs, fh, ex_f)
            delta = ch["eq"] + ch["trunc"] + ch["tail"] + ch["end"] + ch["int"] + ch["round"]
            fin = all(v.is_finite() for v in ch.values()) and delta.is_finite()
            rec = {"d": fup(delta) if fin else None, "fin": fin,
                   "dom": max(ch, key=lambda k: PC.fr_upper(ch[k])) if fin else None}
            if EQ.local_gate(n):
                rec["ch"] = {k: fup(v) for k, v in ch.items()} if fin else None
                if mode == "mid" and fin:
                    gts = PC.gates(ch, C_gate)
                    r_end = C_gate * PC.fr_upper(ch["end"]) / Fr(1, 250)
                    rec["lg"] = {k: v["PASS"] for k, v in gts.items()}
                    rec["eg"] = {"ratio": fup(r_end), "PASS": r_end <= 1}
                    rec["lgb"] = PC.fr_upper(delta) <= Fr(1, 10) / C_gate     # LOCAL_GATE_BUDGET delta_max
        out[n] = rec
    geo = {"n_z": pan["n_z"], "panel_ids_sha256": hashlib.sha256(T.canonical(pan["panel_ids"])).hexdigest(),
           "strip_ids": ES.strip_ids(i, j), "P1": {"E_d": pan["p1"]["E_d"], "PASS": pan["P1_PASS"]},
           "strip_P1_PASS": all(v.P1_PASS for v in sides.values()),
           "contracts": len(needed), "contract_evaluations": stats["contract_evaluations"], "x0_patch": x0_here}
    return out, geo, stats


def run_chunk(cells, patches, out_path):
    """patches x cells x {mid, cell}; PanelShared reused per patch across modes and cells (committed cache)."""
    done = set()
    p = Path(out_path)
    if p.exists():
        for line in p.read_text().splitlines():
            try:
                r = json.loads(line)
                done.add((r["cell"], tuple(r["patch"])))
            except json.JSONDecodeError:
                break
    inputs = {}
    with T.scientific_precision():
        for c in cells:
            built = T.build_cell_candidates(c)["scientific"]
            hashes = {x["node"]: x["identity_hash"] for x in built["candidates"]}
            cands = {x["node"]: T.to_arb_matrix(x["mantissas"]) for x in built["candidates"]}
            e0, ecell, g = cell_drifts(c)
            inputs[c] = (cands, hashes, Fr(T.frozen_cell(c)["C_upper"]), e0, ecell,
                         hashlib.sha256(T.canonical(sorted(hashes.items()))).hexdigest())
        with open(p, "a") as fh:
            for (i, j) in patches:
                cache = {}
                for c in cells:
                    if (c, (i, j)) in done:
                        continue
                    cands, hashes, C, e0, ecell, clsha = inputs[c]
                    t0 = time.process_time()
                    rec = {"schema": SCHEMA, "cell": c, "patch": [i, j], "candidate_identity_list_sha256": clsha, "modes": {}}
                    with BP.p1_lagrange_factor():
                        for mode, e in (("mid", e0), ("cell", ecell)):
                            nodes, geo, st = core(i, j, e, cands, cand_hashes=hashes, C_gate=C, shared_cache=cache, mode=mode)
                            rec["modes"][mode] = {"nodes": nodes, "geo": geo, "cache_hits": st["hits"], "cache_misses": st["misses"]}
                    rec["cpu_seconds"] = time.process_time() - t0
                    rec["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    fh.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
                    fh.flush()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--patches", required=True, help="file with 'i j' lines")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    T.check_threads()
    cells = [int(x) for x in a.cells.split(",")]
    patches = [tuple(map(int, l.split())) for l in Path(a.patches).read_text().splitlines() if l.strip()]
    run_chunk(cells, patches, a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
