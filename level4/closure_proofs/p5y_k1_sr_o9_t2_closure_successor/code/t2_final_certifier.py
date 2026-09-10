"""T2 closure successor -- final per-patch certifier (composition of committed pieces only).

For one cell drift e0 and one live patch it certifies the FULL frozen SR DAG
(sr_o9_equations: 45 residual nodes + 18 operator-image nodes = 63) with
  * the task1r-span-p1-v1 core panelisation and the O9 contraction (T2, 29ee382),
  * contracted endpoint strips, repeated-multiplication raw-shift powers (b48973d6),
  * the authorized P1 Lagrange factor (014879b, implementation 0f52b77).
No new scientific method: this module only runs the endpoint-strip assembly over every
DAG node instead of the five F_r:k0 nodes, and records identities.  Patch-level only:
no whole-cell delta_cell, refinement, B_cover, 28-obligation or production claim.
"""
from __future__ import annotations

import hashlib
import resource
import time
from fractions import Fraction as Fr

import sr_o9_candidates as T
import sr_o9_equations as EQ
import sr_o9_patch_certifier as PC
import sr_o9_endpoint_strips as ES          # installs FixedRawShiftDrift / fixed_raw_moments
import sr_o9_bint_p1 as BP
from flint import arb

NODES = list(EQ.RESIDUAL_NODES) + list(EQ.IMAGE_NODES)
F_LOCAL = [n for n in EQ.RESIDUAL_NODES if EQ.local_gate(n)]
ARCH = "task1r-span-p1-v1 core (O9) + strip-contract-v3 + P1 Lagrange factor"
AUTHORIZATIONS = ["P1_DERIVATIVE_BOUND_REUSE_FOR_SOFTPLUS_LAGRANGE_FACTOR"]
_MAP_SHA = None
# Governance-canonical identities (PRE_T2_GOVERNANCE.issue_2_panel_universe.canonical_panel_id).  The frozen
# T2 engine labels panels "SRpanel:v2:task1r-span-p1-v1:..." (rule name leaked into the ID); that label defect
# is repaired HERE by emitting the canonical form.  Labels only: they key the PanelShared cache and the
# evidence; no scientific quantity depends on them.  Predecessor evidence is not rewritten.
PANEL_ID_FMT = "SRpanel:v2:task1r-span-p1:64:{i}:{j}:{k}/{n}"


def canonical_panel_ids(i, j, n):
    return [PANEL_ID_FMT.format(i=i, j=j, k=k, n=n) for k in range(n)]


def _h(o) -> str:
    return hashlib.sha256(T.canonical(o)).hexdigest()


def equation_map_sha() -> str:
    global _MAP_SHA
    if _MAP_SHA is None:
        _MAP_SHA = EQ.build_map()["equation_map_sha256"]
    return _MAP_SHA


def settings() -> dict:
    return {"D": T.FROZEN_D, "Z": T.FROZEN_Z, "bits": T.FROZEN_BITS, "cand_degree": T.CAND_DEGREE,
            "bidegree": list(T.FROZEN_BIDEGREE), "softplus_degree": PC.H.SOFTPLUS_DEGREE,
            "nested_lines": {k: str(v) for k, v in sorted(T.spec.NESTED_CANDIDATE.items())},
            "endpoint_gate": "C*delta_end <= 1/250", "panel_rule": PC.RULE, "strip_arch": ES.ARCH,
            "weight_series_degree": ES.M_W, "KMAX": PC.KMAX}


def _ball(x: arb):
    return {"mid": PC.enc(arb(x.mid())), "rad": PC.enc(arb(x.rad()))}


def certify_patch_final(i, j, e, cands, *, cand_hashes, C_gate: Fr, shared_cache=None):
    T.require_precision()
    if PC.RawShiftDrift is not ES.FixedRawShiftDrift or PC.raw_moments is not ES.fixed_raw_moments:
        raise T.T1Refusal("repeated-multiplication raw-shift path is not installed")
    if PC.L.softplus_local_enclosure is not BP.softplus_local_enclosure_p1:
        raise T.T1Refusal("authorized P1 Lagrange factor is not installed")
    g = PC.patch_geometry(i, j, e)
    pan = PC.panelisation(i, j, g)
    if not pan["P1_PASS"]:
        raise T.T1Refusal(f"P1 fails on ({i},{j}); executable universe violated")
    pan["panel_ids"] = canonical_panel_ids(i, j, pan["n_z"])
    ctxt = PC.context(g, pan["h"])
    exprs = {n: (EQ.image(n) if n in EQ.IMAGE_NODES else EQ.rhs(n)) for n in NODES}
    needed = sorted({k for ex_ in exprs.values() for k in ex_.terms},
                    key=lambda k: (T.BASIS_ORDER.index(k[0]), k[1]))
    stats = {"hits": 0, "misses": 0}
    core = PC.contract_all(g, pan, ctxt, cands, needed, shared_cache, stats)
    shifts = sorted({s for _, s in needed})
    sides = {"L": ES.StripSide(g, g["L_c"], "L", shifts), "U": ES.StripSide(g, g["U_c"], "U", shifts)}
    acc, end, parts = {}, {}, {}
    for key in needed:
        c, s = key
        pL, eL, dL = sides["L"].contract(cands[c], s)
        pU, eU, dU = sides["U"].contract(cands[c], s)
        acc[key] = ([[core[key][0][a][b] - pL[a][b] - pU[a][b] for b in range(ES.DP)] for a in range(ES.DP)],
                    core[key][1], core[key][2])
        end[key] = eL + eU
        parts[EQ.contract_id(c, s)] = {"L": dL, "U": dU}
    srcs = PC.source_tms(g, ctxt)
    pb = PC.PatchBasis(g, ctxt)
    out = {}
    for n in NODES:
        ex_ = exprs[n]
        if n in EQ.IMAGE_NODES:
            ch, dmid, _ = PC.assemble(ex_, g, acc, end, srcs)
            width = ch["trunc"] + ch["tail"] + ch["end"] + ch["int"]
            rec = {"class": "OPERATOR_IMAGE", "enclosure_width_upper": PC.enc(width), "enclosure_width": float(width),
                   "channels": {k: PC.enc(v) for k, v in ch.items() if k != "eq"},
                   "centre_coefficient": _ball(dmid[0][0])}
            chk = {k: v for k, v in ch.items() if k != "eq"}
        else:
            fh, ex_f = PC.candidate_on_patch(pb, cands[n])
            ch, dmid, _ = PC.assemble(ex_, g, acc, end, srcs, fh, ex_f)
            delta = ch["eq"] + ch["trunc"] + ch["tail"] + ch["end"] + ch["int"] + ch["round"]
            rec = {"class": EQ.node_class(n), "delta_patch_upper": PC.enc(delta), "delta_patch": float(delta),
                   "channels": {k: PC.enc(v) for k, v in ch.items()},
                   "channels_float": {k: float(v) for k, v in ch.items()},
                   "dominant_channel": max(ch, key=lambda k: PC.fr_upper(ch[k]) if ch[k].is_finite() else Fr(10 ** 99)),
                   "candidate_identity_hash": cand_hashes.get(n)}
            chk = ch
        finite = all(v.is_finite() for v in ch.values())
        rec["finite_nonnegative"] = finite and all(PC.fr_upper(v) >= 0 for v in chk.values())
        if EQ.local_gate(n):
            if finite:
                rec["local_gates"] = PC.gates(ch, C_gate)
                r_end = C_gate * PC.fr_upper(ch["end"]) / Fr(1, 250)
                rec["endpoint_gate"] = {"C_delta_end_over_gate": float(r_end), "PASS": r_end <= 1}
                rec["local_gates_all_pass"] = all(v["PASS"] for v in rec["local_gates"].values()) and r_end <= 1
            else:
                rec["local_gates_all_pass"] = False
        rec["contracts"] = sorted(EQ.contract_id(c, s) for c, s in ex_.terms)
        rec["dependency_identity_hashes"] = {c: cand_hashes.get(c) for c in sorted({c for c, _ in ex_.terms})}
        out[n] = rec
    sci = {"patch": [i, j], "architecture": ARCH, "n_z": pan["n_z"], "panel_ids": pan["panel_ids"],
           "panel_ids_sha256": _h(pan["panel_ids"]), "strip_ids": ES.strip_ids(i, j),
           "P1": {"E_d": pan["p1"]["E_d"], "HEADROOM_REL": pan["p1"]["HEADROOM_REL"], "PASS": pan["P1_PASS"]},
           "strip_P1": {s: {"E_d_upper": PC.enc(v.P1_E_d), "PASS": v.P1_PASS} for s, v in sides.items()},
           "contracts_evaluated": sorted(EQ.contract_id(c, s) for c, s in needed),
           "contract_evaluations": stats["contract_evaluations"],
           "strip_error_parts": parts, "nodes": out}
    return sci, {"hits": stats["hits"], "misses": stats["misses"]}


def cell_inputs(cell_index):
    built = T.build_cell_candidates(cell_index)["scientific"]
    return built


def run_case(cell_index, i, j, *, shared_cache=None, built=None):
    t0c, t0w = time.process_time(), time.perf_counter()
    built = built if built is not None else cell_inputs(cell_index)
    hashes = {x["node"]: x["identity_hash"] for x in built["candidates"]}
    cell = T.frozen_cell(cell_index)
    C = Fr(cell["C_upper"])
    with T.scientific_precision():
        cands = {x["node"]: T.to_arb_matrix(x["mantissas"]) for x in built["candidates"]}
        e = T.cell_geometry(cell)["e0"]
        tc = time.process_time()
        with BP.p1_lagrange_factor() as st:
            res, cache = certify_patch_final(i, j, e, cands, cand_hashes=hashes, C_gate=C, shared_cache=shared_cache)
        stats = dict(st)
        tcert = time.process_time() - tc
        e_ball = _ball(e)
    sci = {"schema": "rebaseguard.p5y.k1.sr.o9.t2-final-patch-record.v1",
           "case": {"cell": cell_index, "patch": [i, j]},
           "cell_identity_sha256": _h(T.cell_identity(cell)), "C_upper": f"{C.numerator}/{C.denominator}",
           "e0": e_ball, "candidate_identity_hashes": dict(sorted(hashes.items())),
           "candidate_identity_list_sha256": _h(sorted(hashes.items())),
           "equation_map_sha256": equation_map_sha(), "settings": settings(),
           "authorizations": AUTHORIZATIONS, **res}
    return {"scientific": sci, "scientific_hash": _h(sci),
            "run": {"cpu_seconds_certify": tcert, "cpu_seconds_total": time.process_time() - t0c,
                    "wall_seconds": time.perf_counter() - t0w,
                    "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    # flat single-segment keys: the frozen aux4 pattern "run.**" matches one segment below run
                    "cache_hits": cache["hits"], "cache_misses": cache["misses"],
                    "lagrange_calls": stats["calls"], "lagrange_old_ball_contains_new": stats["old_ball_contains_new"],
                    "lagrange_old_rad_min": stats["old_rad_min"], "lagrange_old_rad_max": stats["old_rad_max"]}}


def summary(rec) -> dict:
    s = rec["scientific"]
    nodes = s["nodes"]
    F = {n: nodes[n] for n in F_LOCAL}
    return {"case": s["case"], "n_nodes": len(nodes), "nodes_expected": sorted(nodes) == sorted(NODES),
            "contracts": len(s["contracts_evaluated"]),
            "all_finite_nonnegative": all(v["finite_nonnegative"] for v in nodes.values()),
            "endpoint_PASS": all(v.get("endpoint_gate", {}).get("PASS") for v in F.values()),
            "B_int_PASS": all(v["local_gates"]["int"]["PASS"] for v in F.values()),
            "all_F_local_gates_PASS": all(v["local_gates_all_pass"] for v in F.values()),
            "worst_endpoint_ratio": max(v["endpoint_gate"]["C_delta_end_over_gate"] for v in F.values()),
            "worst_int_over_allowance": max(float(Fr(*_frac(v["local_gates"]["int"]["value_upper"]))
                                                  / Fr(v["local_gates"]["int"]["allowance"])) for v in F.values()),
            "failing": sorted({f"{n}:{k}" for n, v in F.items() for k, g in v["local_gates"].items() if not g["PASS"]}),
            "scientific_hash": rec["scientific_hash"]}


def _frac(enc):
    m, ex = enc
    return (m * 2 ** ex, 1) if ex >= 0 else (m, 2 ** (-ex))
