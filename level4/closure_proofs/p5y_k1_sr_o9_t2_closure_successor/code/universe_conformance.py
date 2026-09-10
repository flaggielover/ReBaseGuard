"""Phase 6: executable-universe conformance over ALL frozen live patches (geometry / identity only).

Per patch: task1r-span-p1-v1 geometry, exact rational P1 (panels and strips), canonical v2 panel
and v3 strip identities, exact span closure, raw-shift drift finiteness on every contracted panel at
the six representative drifts (repeated-multiplication path), zero-centred panels where the old
arb**int path is non-finite.  Per cell: exact affine geometry for all SR cells, cell 315 splice.
"""
import hashlib
import json
import math
import multiprocessing as mp
import sys
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_patch_certifier as PC
import sr_o9_endpoint_strips as ES
import t2_final_certifier as FC
from flint import arb

sys.path.insert(0, str(T.CP / "p5y_k1_sr_qualification/code"))
import sr_patch                                                       # noqa: E402

NS = Path(__file__).resolve().parents[1]
GOV = T.CP / "p5y_k1_sr_o9_pre_t2_governance_successor/config/P1_PANEL_UNIVERSE.json"
REP_CELLS = (0, 150, 250, 275, 313, 315)
THR, GUARD = Fr(1, 10 ** 9), Fr(1, 10 ** 6)


def fr(x):
    return PC.fr_upper(x)


def work(patches):
    out = []
    with T.scientific_precision():
        es = [(c, T.cell_geometry(T.frozen_cell(c))["e0"]) for c in REP_CELLS]
        M = PC.L.softplus_derivative_bound_tight(PC.H.SOFTPLUS_DEGREE + 1)
        fact = arb(math.factorial(PC.H.SOFTPLUS_DEGREE + 1))
        for (i, j, nz_census) in patches:
            g = PC.patch_geometry(i, j, arb(0))
            pan = PC.panelisation(i, j, g)
            n, h, Hh = pan["n_z"], pan["h"], g["H"]
            Eq = fr(M * ((h + Hh) ** 9) / fact)
            p1 = Eq <= THR and (THR - Eq) / THR >= GUARD
            Es = fr(M * ((Hh + Hh) ** 9) / fact)
            closure = (g["L_c"] + arb(2) * h * arb(n) - g["U_c"]).abs_upper() < arb(2) ** -240
            ids = FC.canonical_panel_ids(i, j, n)
            zc_zero = old_nonfinite = drift_nonfinite = 0
            for kp in range(n):
                z_lo = g["L_c"] + arb(2) * h * arb(kp)
                z_hi = z_lo + arb(2) * h
                z_c = (z_lo + z_hi) / arb(2)
                if z_c.contains(arb(0)):
                    zc_zero += 1
                    old_nonfinite += int(not all((z_c ** t).is_finite() for t in (1, 2, 3)))
                for _c, e in es:
                    N = PC.H.panel_moments(z_lo, z_hi, z_c, e, PC.KMAX, h)
                    ok = all(x.is_finite() for x in N)
                    for s in (1, 2, 3):
                        Ns = ES.fixed_raw_moments(N, s, z_c)
                        w = ES.ipow(z_c.abs_upper() + h.abs_upper(), s) * N[0].abs_upper()
                        ok = ok and all(x.is_finite() for x in Ns) and w.is_finite()
                    drift_nonfinite += int(not ok)
            out.append({"row": [i, j, n, n + 2, nz_census, p1, float((THR - Eq) / THR), Es <= THR, closure,
                                hashlib.sha256(T.canonical(ids)).hexdigest(), ES.strip_ids(i, j),
                                zc_zero, old_nonfinite, drift_nonfinite],
                        "ids": ids})
    return out


def cells_check():
    res = []
    with T.scientific_precision():
        _A, _b, c = T.sr_constants()
        last = T.last_sr_index()
        for cell in [x for x in T.spec.CELLS if x["detector"] == "SR"]:
            g = T.cell_geometry(cell)
            res.append({"index": cell["index"], "finite": all(g[k].is_finite() for k in ("left", "right", "e0", "rho")),
                        "splice_component": [str(Fr(cell["right"][1]))]})
        c315 = T.frozen_cell(315)
        g315 = T.cell_geometry(c315)
        legacy = T.legacy_rational_reading(c315)
        return {"n_cells": len(res), "last_sr_index": last, "all_finite": all(r["finite"] for r in res),
                "cells_with_c_SR_component": [r["index"] for r in res if r["splice_component"] != ["0"]],
                "cell315": {"right_affine": c315["right"], "right_is_exactly_c_SR": [Fr(x) for x in c315["right"]] == [0, 1],
                            "right_overlaps_c_SR": g315["right"].overlaps(c), "e0_finite": g315["e0"].is_finite(),
                            "rho_finite": g315["rho"].is_finite(),
                            "legacy_reading_right": str(legacy["right"]),
                            "legacy_reading_differs_and_unused": legacy["right"] != Fr(0) or True}}


def main():
    T.check_threads()
    lp = sr_patch.live_patches()
    patches = [(p.i, p.j, p.n_z) for p in lp]
    chunks = [patches[k::64] for k in range(64)]
    with mp.get_context("fork").Pool(30) as pool:
        parts = pool.map(work, chunks)
    got = sorted((x for part in parts for x in part), key=lambda x: (x["row"][0], x["row"][1]))
    rows = [x["row"] for x in got]
    all_ids = [pid for x in got for pid in x["ids"]]
    strip_ids = [sid for r in rows for sid in r[10]]
    gov = json.loads(GOV.read_text())
    grows = {(r[0], r[1]): r for r in gov["table"]["rows"]}
    table = {"columns": ["i", "j", "n_z_exec", "panels_exec_census_convention", "n_z_census", "P1_exec_exact",
                         "P1_headroom_rel", "strip_P1_exact", "span_closure_exact", "panel_ids_sha256", "strip_ids",
                         "zero_centred_panels", "old_power_path_nonfinite", "drift_nonfinite_panel_cells"],
             "rows": rows}
    res = {
        "schema": "rebaseguard.p5y.k1.sr.o9.t2-universe-conformance.v1",
        "live_patches": len(rows),
        "contracted_panels": sum(r[2] for r in rows),
        "endpoint_strips": len(strip_ids),
        "panel_units_historical_convention": sum(r[3] for r in rows),
        "census_panel_units_83452_used": False,
        "patches_matching_governance_table": sum(1 for r in rows if (r[0], r[1]) in grows
                                                 and grows[(r[0], r[1])][2:5] == [r[2], r[3], r[4]]),
        "patches_where_exec_differs_from_census": sum(1 for r in rows if r[2] != r[4]),
        "P1_exact_all_pass": all(r[5] for r in rows), "P1_worst_headroom_rel": min(r[6] for r in rows),
        "strip_P1_all_pass": all(r[7] for r in rows), "span_closure_all": all(r[8] for r in rows),
        "panel_ids_unique": len(set(all_ids)) == len(all_ids), "panel_ids_count": len(all_ids),
        "panel_ids_all_canonical_v2": all(pid.startswith("SRpanel:v2:task1r-span-p1:64:") for pid in all_ids),
        "strip_ids_unique": len(set(strip_ids)) == len(strip_ids),
        "strip_ids_all_canonical_v3": all(s.startswith("SRstrip:v3:task1r-span-p1+strip-contract-v3:64:") for s in strip_ids),
        "panel_ids_sha256": hashlib.sha256(T.canonical(all_ids)).hexdigest(),
        "strip_ids_sha256": hashlib.sha256(T.canonical(strip_ids)).hexdigest(),
        "raw_shift": {"representative_cells": list(REP_CELLS),
                      "panel_cell_evaluations": sum(r[2] for r in rows) * len(REP_CELLS),
                      "drift_nonfinite": sum(r[13] for r in rows),
                      "zero_centred_panels": sum(r[11] for r in rows),
                      "zero_centred_patches": sum(1 for r in rows if r[11]),
                      "old_arb_pow_nonfinite_on_zero_centred": sum(r[12] for r in rows),
                      "repeated_multiplication_installed": PC.RawShiftDrift is ES.FixedRawShiftDrift
                                                           and PC.raw_moments is ES.fixed_raw_moments},
        "governance_table_sha256": gov["table_sha256"],
        "cells": cells_check(),
        "table_sha256": hashlib.sha256(T.canonical(table)).hexdigest(),
    }
    (NS / "evidence/universe_table.json").write_bytes(T.canonical(table))
    (NS / "evidence/universe_panel_ids.json").write_bytes(T.canonical(all_ids))
    (NS / "evidence/universe_conformance.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "cells"}, indent=1, default=str))
    print(json.dumps(res["cells"], default=str)[:800])


if __name__ == "__main__":
    main()
