"""QC09 (in-process part): the formal guard, DECOY mode and the reproduction context, through the pinned code paths.

Every check is a boolean that can fail; nothing is certified, evaluated or computed in the band: each refusal must
fire BEFORE any certifier work (the time of each refused call is bounded). The sandbox part (arming with the marker at
HEAD = grant) is in test_mb308_flows.py (QC09_arming).
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
CODE = HERE.parents[1] / "code"
REPO = HERE.parents[4]
sys.path.insert(0, str(CODE))
import mb308_guard as G  # noqa: E402

FAST_S = 5.0


def refused(fn, *a, **k) -> bool:
    t0 = time.time()
    try:
        fn(*a, **k)
        return False
    except G.QuarantineRefusal:
        return time.time() - t0 < FAST_S


def cover_cells(read_pinned) -> dict:
    return {c["index"]: c for c in json.loads(read_pinned(REPO, "cells_json")) if c["detector"] == "CUSUM"}


def run(read_pinned, mods: dict | None = None) -> dict:
    """mods (optional): {"c1b", "c2b", "S1", "A0C", "vd", "TPT", "indep"} pinned modules for the code-path checks."""
    if G.mode() != "DECOY" or G.in_reproduction():
        return {"pass": False, "reason": "the guard is not in DECOY mode"}
    cells = cover_cells(read_pinned)
    geo = G.geometry(*G.CELL308)
    r = {}
    r["band_points_and_mirror_refused"] = all(refused(G.guard_drift, x) for x in (F(6, 5), F(13, 5), F(19, 10),
                                                                                 F(-2), F(-6, 5)))
    r["straddling_intervals_refused"] = all(refused(G.guard_drift, a, b) for a, b in ((F(1), F(3)), (F(-3), F(-1)),
                                                                                    (F(1, 2), F(6, 5))))
    r["cell308_tiles_hulls_points_refused"] = len(geo) > 1 and all(
        refused(G.guard_drift, *g["tile"]) and refused(G.guard_drift, *g["hull"]) and refused(G.guard_drift, g["b"])
        for g in geo)
    r["tail_cover_cells_refused"] = all(refused(G.guard_drift, F(cells[k]["left"][0]), F(cells[k]["right"][0]))
                                        for k in (305, 306, 307, 308, 309))
    r["cell308_cover_is_guard_constant"] = (F(cells[308]["left"][0]), F(cells[308]["right"][0])) == G.CELL308
    r["decoys_accepted"] = not any(refused(G.guard_drift, a, b) for a, b in (
        (F(1, 2), F(17, 32)), (F(3), F(31, 10)), (F(-1, 2), F(-1, 4)),
        *[g["hull"] for g in G.geometry(F(cells[297]["left"][0]), F(cells[297]["right"][0]))]))
    r["quarantined_labels_refused"] = all(refused(G.guard_cell, "CUSUM", 5, k) for k in (305, 306, 307, 308, 309))
    try:
        for lab in (("DECOY", 5, 9000), ("SR", 5, 308), ("CUSUM", 3, 308), ("CUSUM", 5, 297)):
            G.guard_cell(*lab)
        r["other_labels_accepted"] = True
    except G.QuarantineRefusal:
        r["other_labels_accepted"] = False
    r["log_execution_refuses"] = refused(G.log_execution, "x")
    G.install_import_guard()
    try:
        __import__("numpy")
        r["numpy_import_refused"] = False
    except G.QuarantineRefusal:
        r["numpy_import_refused"] = True
    except ImportError:
        r["numpy_import_refused"] = False
    r["arm_without_marker_refused"] = refused(G.arm_target, str(REPO), "HEAD", G.target_admitted_set())
    # reproduction context: exactly the declared cell's cover and points, nothing else
    c305 = (F(cells[305]["left"][0]), F(cells[305]["right"][0]))
    e305 = F(cells[305]["e0"][0])
    with G.reproduction(305, c305, e305):
        inside_ok = not refused(G.guard_drift, *c305) and not refused(G.guard_drift, e305) and \
            not refused(G.guard_cell, "CUSUM", 5, 305)
        inside_refusals = refused(G.guard_drift, *geo[0]["tile"]) and refused(G.guard_cell, "CUSUM", 5, 308) and \
            refused(G.guard_cell, "CUSUM", 5, 306) and refused(G.guard_drift, c305[0], c305[1] + F(1, 10 ** 9))
        nested = refused(lambda: G.reproduction(308, G.CELL308, sum(G.CELL308) / 2).__enter__())
    r["reproduction_admits_exactly_the_cell"] = inside_ok and inside_refusals and nested
    r["reproduction_closed_after_exit"] = refused(G.guard_drift, *c305) and refused(G.guard_cell, "CUSUM", 5, 305)
    r["reproduction_refuses_other_cells"] = refused(lambda: G.reproduction(306, (F(cells[306]["left"][0]),
                                                                                F(cells[306]["right"][0])),
                                                                          F(cells[306]["e0"][0])).__enter__())
    r["reproduction_308_needs_guard_cover"] = refused(lambda: G.reproduction(308, c305, e305).__enter__())
    if mods:
        r.update(code_paths(mods))
    r["mode_still_decoy"] = G.mode() == "DECOY" and not G.in_reproduction()
    r["pass"] = all(v is True for v in r.values())
    return r


def code_paths(m: dict) -> dict:
    """The band is refused through each pinned module's own guard call (unarmed), before any work."""
    b = G.geometry(*G.CELL308)[0]
    out = {}
    m["set_flags"](m["c1b"], True, True)
    out["c1b_block_rung_refused"] = refused(m["S1"].certify_rung, m["c1b"], b["hull"][0], b["hull"][1], 4)
    m["set_flags"](m["c1b"], True, False)
    out["c1b_pointwise_rung_refused"] = refused(m["A0C"].c1b_w_rung, m["c1b"], G, b["b"], 8)
    out["c1b_Ctx_direct_refused"] = refused(m["c1b"]["c1b_certpw"].Ctx, b["b"], m["c1b"]["c1b_pw"].BW_PW)
    out["c2b_rung_refused"] = refused(m["A0C"].c2bx_rung, m["c2b"], G, b["b"], 20)
    out["c2b_Setup_direct_refused"] = refused(m["c2b"]["c2b_exact"].Setup, 20, b["b"])
    out["verifier_refused"] = refused(m["vd"].Prep, m["vd"].StripPW([F(0), F(5)], [{(0, 0): F(1)}]), b["b"])
    TPT = m["TPT"]
    cp = TPT.CellProfile(detector="DECOY", m=1, cell=9999, e0=sum(G.CELL308) / 2, rho=(G.CELL308[1] - G.CELL308[0]) / 2,
                         g_hi=F(-1), A0=F(1), A1=F(1), A2=F(1),
                         terms=[TPT.SourceTerm(H_at_a=(F(0), F(0)), abs_G_at_a=F(0), fF=F(0), fD=F(0), fH=F(0),
                                               fG=F(0), Env4=F(0))])
    out["tpt_geometry_refused_whatever_label"] = refused(TPT.lo_hi_polys, cp)
    if m.get("indep") is not None:
        IND = m["indep"]
        prof = {"e0": cp.e0, "rho": cp.rho, "x_lo": G.CELL308[0], "x_hi": G.CELL308[1], "m": 1,
                "sources": [{"f_F": 0, "f_D": 0, "f_H": 0, "f_G": 0, "Env4": 0, "Hhat": [0, 0]}], "W": [0, 0],
                "H_final": [0, 0]}
        try:
            IND.tptb(prof, [{"lo": G.CELL308[0], "hi": G.CELL308[1], "A0": 1, "A1": 1, "A2": 1}])
            out["f2_research_band_guard_on_by_default"] = False
        except IND.Refusal as exc:
            out["f2_research_band_guard_on_by_default"] = "RESEARCH_BAND_GUARD" in str(exc)
    return out
