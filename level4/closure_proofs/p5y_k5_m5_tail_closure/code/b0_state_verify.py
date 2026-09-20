"""Campaign B, Phase B0: read-only verification of the authoritative starting state and of the Campaign-B audit's
internal consistency. Stdlib only, no remote host, no model quantity.

Checks
  G1  git: HEAD, branch, origin/p5y-postk1-frontier, origin/main, clean worktree, linear ancestry
  G2  the adopted coverage map r4 (sha256 a3bddd83...) and the bindings it declares
  G3  the sealed Campaign-A consumption (1fa8d8de...) and its open set: m1/m2/m3 complete, m5 open exactly 305-309
  G4  the Campaign-A final adjudication: ADOPTED, 27 PASS / 7 INFO / 3 NOT_CHECKABLE_LOCALLY / 0 FAIL,
      the sequencing-defect disclosure present, and the r4 regeneration claim (byte-identical) re-checked by
      regenerating r4 from the sealed consumption with the committed generator
  G5  the Campaign-A namespace is untouched since the freeze outside its evidence prefix, and the adopted
      predecessor namespaces are untouched since the Campaign-A start frontier
  G6  the frozen Campaign-B feasibility gates and the tail blocker map: schema, universe, row arithmetic
      (Gamma = hi(g) + rho*x_hi*M, M_needed, reduction factor, passes_direct) and geometry against the frozen cover
  G7  the Campaign-B audit prose table agrees with the machine-readable map
  G8  route selection: T2, gate USEFUL, execution not started (no protocol, no evidence, no coverage map r5)

    python3 -B b0_state_verify.py --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = REPO / "level4/closure_proofs"
A_NS = CP / "p5y_k5_lower_front_order3"
A_EV = A_NS / "evidence/tc_r1"

FRONTIER = "3c1c6b9cae59ba09d96d1d90baa3ea9074822bca"
MAIN = "1cb453826313c189f0bdafd5b84120c1edb74da9"
R4_SHA = "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35"
R3_SHA = "6d598dc53293f91cdffb99f8fb3a0080542d8d0ca75c3110cc5fcc4db97a544d"
CONS_SHA = "1fa8d8dee78483c83d54bd90dba86a9316fb5c67c4acd43781a05103ab111f51"
IDX_SHA = "51c5ca9342afad54975f9f7d97e4d3ff006933fe60a231366b17c1c00b830cfd"
A_FREEZE = "3f540a33cf10ce5ea3fe0a35a2576a7368ad5f04"
A_PROTO_SHA = "10ff7e37e9b6e9ad1c39be4f32cceeeb7c413e50319efea4d0c7aa12ca76924f"
A_START = "7cb01e38e2831983ba8f29b3d8c14c189678e4ac"
TAIL = (305, 306, 307, 308, 309)
ADOPTED_NS = ("p5y_k5_perron_deflated_resolvent", "p5y_k5b_independent_countersignature",
              "p5y_k1_cusum_aux5_composite_closure", "p5y_k5_remaining_cell_closure",
              "p5y_k5_cusum_order3_real_producer", "p5y_k1_cover_ledger_successor",
              "p5y_k5b_consumption_adapter", "p5y_k5_cusum_first_real_probe_protocol")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*a, check=True) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True, check=check).stdout


def rat(p) -> F:
    return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


def g1() -> dict:
    head = git("rev-parse", "HEAD").strip()
    branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
    ls = {ln.split()[1]: ln.split()[0] for ln in git("ls-remote", "origin", "refs/heads/main",
                                                     "refs/heads/p5y-postk1-frontier").splitlines() if ln.strip()}
    dirty = git("status", "--porcelain", "--untracked-files=all").strip().splitlines()
    ancestry = subprocess.run(["git", "-C", str(REPO), "merge-base", "--is-ancestor", FRONTIER, head]).returncode == 0
    out = {"head": head, "branch": branch, "origin_frontier": ls.get("refs/heads/p5y-postk1-frontier"),
           "origin_main": ls.get("refs/heads/main"), "dirty_paths": len(dirty),
           "frontier_is_ancestor_of_head": ancestry,
           "merges_since_frontier": len([x for x in git("log", "--merges", "--format=%H",
                                                        f"{FRONTIER}..{head}").split() if x])}
    out["pass"] = (out["origin_frontier"] == FRONTIER and out["origin_main"] == MAIN and ancestry
                   and out["merges_since_frontier"] == 0
                   and all(p.split()[-1].startswith("level4/closure_proofs/p5y_k5_m5_tail_closure/")
                           for p in dirty))
    return out


def g2() -> dict:
    raw = (A_EV / "K5_COVERAGE_MAP_R4.json").read_bytes()
    d = json.loads(raw)
    inp = d["inputs"]
    per = d["per_m"]
    out = {"r4_sha256": sha(raw), "K5_COVERAGE_COMPLETE": d["K5_COVERAGE_COMPLETE"],
           "union_open_ranges": d["union_open_ranges"], "inputs": inp,
           "open_per_m": {m: per[m]["open_ranges"] for m in per}}
    out["pass"] = (out["r4_sha256"] == R4_SHA and d["K5_COVERAGE_COMPLETE"] is False
                   and d["union_open_ranges"] == [[305, 309]] and d["union_open_count"] == 5
                   and inp["coverage_map_r3_sha256"] == R3_SHA and inp["tc_consumption_sha256"] == CONS_SHA
                   and inp["tc_index_sha256"] == IDX_SHA and inp["protocol_sha256"] == A_PROTO_SHA
                   and inp["freeze_commit"] == A_FREEZE
                   and per["1"]["open_ranges"] == [] and per["2"]["open_ranges"] == []
                   and per["3"]["open_ranges"] == [] and per["5"]["open_ranges"] == [[305, 309]]
                   and sha((CP / "p5y_k5_perron_deflated_resolvent/evidence/successor_r1/"
                                 "K5_COVERAGE_MAP_R3.json").read_bytes()) == R3_SHA)
    return out


def g3() -> dict:
    raw = (A_EV / "TC_CONSUMPTION.json").read_bytes()
    d = json.loads(raw)
    c = d["consumptions"]
    out = {"consumption_sha256": sha(raw), "tc_cells": [d["tc_cells"][0], d["tc_cells"][-1]],
           "tc_cell_count": len(d["tc_cells"]), "crosscheck_comparisons": d["crosscheck_comparisons"],
           "replay_gate": d["replay_gate"], "open": {m: c[m]["open_ranges"] for m in c},
           "pass_counts": {m: c[m]["pass_count"] for m in c}}
    out["pass"] = (out["consumption_sha256"] == CONS_SHA and d["tc_cells"] == list(range(11, 45))
                   and d["crosscheck_comparisons"] == 136 and d["replay_gate"].startswith("PASS")
                   and c["1"]["open_ranges"] == [] and c["2"]["open_ranges"] == [] and c["3"]["open_ranges"] == []
                   and c["5"]["open_ranges"] == [[305, 309]] and c["5"]["pass_count"] == 305)
    return out


def g4() -> dict:
    md = (A_EV / "adjudication_r1/ADJUDICATION_R1.md").read_text()
    js = json.loads((A_EV / "adjudication_r1/ADJUDICATION_R1.json").read_bytes())
    note = (A_EV / "adjudication_r1/SEQUENCING_DEFECT_NOTE.md").read_text()
    counts = re.search(r"PASS\s+(\d+)\s+.\s+INFO\s+(\d+)\s+.\s+NOT_CHECKABLE_LOCALLY\s+(\d+)\s+.\s+FAIL\s+\*?\*?(\d+)",
                       md)
    out = {"verdict_md": "ADJUDICATION = ADOPTED" in md, "verdict_json": js.get("verdict") or js.get("ADJUDICATION"),
           "counts_md": [int(x) for x in counts.groups()] if counts else None,
           "counts_json": {k: js.get(k) for k in ("PASS", "INFO", "NOT_CHECKABLE_LOCALLY", "FAIL") if k in js},
           "sequencing_note_present": bool(note.strip()),
           "sequencing_note_names_defect": "before final adjudicator handover" in note
                                           or "published before handover" in note or "in-progress copy" in note,
           "notes_present": {n: (n in md) for n in ("N1", "N3", "N5", "N7")}}
    regen = None
    with tempfile.TemporaryDirectory() as td:
        p = subprocess.run([sys.executable, "-B", str(A_EV / "code/coverage_map_r4.py"),
                            "--result", str(A_EV / "TC_CONSUMPTION.json"), "--result-sha256", CONS_SHA,
                            "--out", str(Path(td) / "R4.json")], capture_output=True, text=True)
        if p.returncode == 0:
            regen = sha((Path(td) / "R4.json").read_bytes())
    out["r4_regenerated_sha256"] = regen
    out["r4_regeneration_byte_identical"] = regen == R4_SHA
    out["pass"] = (out["verdict_md"] and out["counts_md"] == [27, 7, 3, 0] and out["sequencing_note_present"]
                   and out["sequencing_note_names_defect"] and all(out["notes_present"].values())
                   and out["r4_regeneration_byte_identical"])
    return out


def g5() -> dict:
    changed = git("diff", "--name-only", A_FREEZE, FRONTIER, "--",
                  "level4/closure_proofs/p5y_k5_lower_front_order3").split()
    outside = [c for c in changed if not c.startswith("level4/closure_proofs/p5y_k5_lower_front_order3/"
                                                     "evidence/tc_r1/")]
    moved = {}
    for ns in ADOPTED_NS:
        d = git("diff", "--name-only", A_START, FRONTIER, "--", f"level4/closure_proofs/{ns}").split()
        moved[ns] = len(d)
    out = {"campaign_A_changed_outside_evidence": outside, "adopted_namespace_changes": moved,
           "campaign_A_changed_files_since_freeze": len(changed)}
    out["pass"] = not outside and all(v == 0 for v in moved.values())
    return out


def g6() -> dict:
    gates_raw = (NS / "config/FEASIBILITY_GATES_B.json").read_bytes()
    gates = json.loads(gates_raw)
    map_raw = (NS / "phase_a/TAIL_BLOCKER_MAP.json").read_bytes()
    bm = json.loads(map_raw)
    cover = {c["index"]: c for c in json.loads((CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes())
             if c["detector"] == "CUSUM"}
    cells_sha = sha((CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes())
    bad, rows = [], {}
    for row in bm["rows"]:
        k, m = row["cell"], row["m"]
        g = cover[k]
        x_lo, x_hi, rho, e0 = (rat(g[t]) for t in ("left", "right", "rho", "e0"))
        for name, want, got in (("e_lo", x_lo, row["e_lo"]), ("e_hi", x_hi, row["e_hi"]),
                                ("rho", rho, row["rho"]), ("e0", e0, row["e0"])):
            if abs(float(want) - got) > 1e-12 * max(1.0, abs(got)):
                bad.append(f"{k}:{m}:{name}")
        if abs(x_lo + rho - e0) > 0 or abs(x_hi - rho - e0) > 0:
            bad.append(f"{k}:geometry")
        M, g_hi = row["M_R2"], row["g_e0_interval"][1]
        pen = float(rho) * float(x_hi) * M
        if abs(pen - row["penalty_rho_xhi_M"]) > 1e-12 * abs(pen):
            bad.append(f"{k}:{m}:penalty")
        if abs((g_hi + pen) - row["Gamma"]) > 1e-12 * max(1.0, abs(row["Gamma"])):
            bad.append(f"{k}:{m}:Gamma")
        if row["passes_direct"] != (row["Gamma"] < 0):
            bad.append(f"{k}:{m}:passes_direct")
        if g_hi < 0:
            need = -g_hi / (float(rho) * float(x_hi))
            if abs(need - row["M_needed_for_direct_pass"]) > 1e-9 * need:
                bad.append(f"{k}:{m}:M_needed")
            if abs(M / need - row["M_reduction_factor_needed"]) > 1e-9:
                bad.append(f"{k}:{m}:reduction")
        if row["m"] == 5 and k in TAIL:
            rows[k] = row
    open_pairs = sorted((r["cell"], r["m"]) for r in bm["rows"] if not r["passes_direct"])
    out = {"gates_sha256": sha(gates_raw), "blocker_map_sha256": sha(map_raw), "rows": len(bm["rows"]),
           "cells_json_sha256": cells_sha, "cells_json_matches_map": bm["cells_json_sha256"] == cells_sha,
           "arithmetic_mismatches": bad[:10], "direct_fail_pairs": open_pairs,
           "gates_universe": gates["universe"], "gates_frozen_before": gates["frozen_before"],
           "tail_rows": {str(k): {t: rows[k][t] for t in ("M_R2", "M_needed_for_direct_pass",
                                                          "M_reduction_factor_needed", "C_upper", "rho",
                                                          "penalty_rho_xhi_M", "Gamma", "target_gate_status")}
                         for k in sorted(rows)}}
    out["pass"] = (not bad and out["cells_json_matches_map"] and len(bm["rows"]) == 40
                   and open_pairs == [(k, 5) for k in TAIL]
                   and gates["universe"]["cells"] == list(TAIL) and gates["universe"]["m"] == [5]
                   and gates["universe"]["pairs"] == 5
                   and all(rows[k]["target_gate_status"] == "PASS" for k in rows))
    return out


def g7() -> dict:
    md = (NS / "phase_a/TAIL_BLOCKER_AUDIT.md").read_text()
    bm = {r["cell"]: r for r in json.loads((NS / "phase_a/TAIL_BLOCKER_MAP.json").read_bytes())["rows"]
          if r["m"] == 5}
    bad = []
    for line in md.splitlines():
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) != 9 or not cols[0].isdigit():
            continue
        k = int(cols[0])
        row = bm[k]
        pen = float(cols[3])
        gam = float(cols[4].replace("+", ""))
        M = float(cols[5])
        need = float(cols[6])
        red = float(cols[7].strip("*").rstrip("x").rstrip("×"))
        C = float(cols[8])
        for name, want, got, tol in (("penalty", row["penalty_rho_xhi_M"], pen, 1e-2),
                                     ("Gamma", row["Gamma"], gam, 1e-2), ("M", row["M_R2"], M, 1e-2),
                                     ("need", row["M_needed_for_direct_pass"], need, 1e-2),
                                     ("reduction", row["M_reduction_factor_needed"], red, 1e-2),
                                     ("C_upper", row["C_upper"], C, 1e-2)):
            if abs(want - got) > tol * max(1.0, abs(want)):
                bad.append(f"{k}:{name}:{want}!={got}")
    out = {"prose_rows_checked": len(bm), "mismatches": bad}
    out["pass"] = not bad
    return out


def g8() -> dict:
    rc = (NS / "phase_b/TAIL_ROUTE_COMPARISON.md").read_text()
    out = {"selected": "TAIL_ROUTE_SELECTED = T2" in rc, "gate": "TAIL_FEASIBILITY_GATE = USEFUL" in rc,
           "not_started": "TAIL_EXECUTION = NOT_STARTED" in rc,
           "protocol_present": (NS / "config/TCT_PROTOCOL.json").exists(),
           "coverage_map_r5_anywhere": [str(p.relative_to(REPO)) for p in REPO.rglob("K5_COVERAGE_MAP_R5.json")],
           "T1_infeasible": "**INFEASIBLE**" in rc, "T4_infeasible": "INFEASIBLE** (governance)" in rc}
    out["pass"] = (out["selected"] and out["gate"] and out["not_started"] and not out["protocol_present"]
                   and not out["coverage_map_r5_anywhere"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = {"schema": "rebaseguard.p5y.k5.m5-tail.b0-state-verification.v1",
           "G1_git": g1(), "G2_coverage_map_r4": g2(), "G3_sealed_consumption": g3(),
           "G4_campaign_A_adjudication": g4(), "G5_immutability": g5(), "G6_gates_and_blocker_map": g6(),
           "G7_audit_prose": g7(), "G8_route_selection": g8()}
    res["ALL_PASS"] = all(v["pass"] for k, v in res.items() if k.startswith("G"))
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({k: v["pass"] for k, v in res.items() if k.startswith("G")}
                     | {"ALL_PASS": res["ALL_PASS"], "sha256": sha(data)}))
    return 0 if res["ALL_PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
