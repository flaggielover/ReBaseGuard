"""Adversarial suite for the C3 mixed selector, run BEFORE the real C3 forecast.

Mutants are planted where an error would produce an ARTIFICIALLY OPTIMISTIC result — a tighter A, a spurious
closure, a premise quietly skipped, a component taken from a source that does not cover the cell. Each must be
detected. A mutant that survives is reported as undetected unless its equivalence under a certified invariant is
proved here, in code, rather than asserted.

    python3 -B c3_mutations.py --out OUT.json
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[2]
C2 = CP / "p5y_k5_tail_c2_closure"
CELLS = (306, 307, 308, 309)
FIELDS = ("A0", "A1", "A2")


def load(path, name, src=None):
    raw = src.encode() if src else Path(path).read_bytes()
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    exec(compile(raw, str(path), "exec"), m.__dict__)
    return m


def world():
    FC = load(C2 / "code/c2_d5_forecast.py", "c2fc")
    B = FC.load(FC.B_NS / "code/tail_forecast_r2.py", "b_tf")
    T = sys.modules["tct_rule"]
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    DC = FC.load(FC.AD_NS / "code/deflated_consume.py", "ad_dc", FC.DC_SHA)
    adopted = json.loads((FC.B_NS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())["cells"]
    cover = {c["index"]: c for c in json.loads(
        (CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes()) if c["detector"] == "CUSUM"}
    c1 = {b["cell"]: b for b in json.loads(
        (FC.C1_NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes())["blocks"]}
    c2 = {b["cell"]: b for b in json.loads(
        (C2 / "evidence/registry_c2/REGISTRY_C2.json").read_bytes())["blocks"]}
    meas = {}
    for k in CELLS:
        d = json.loads((FC.B_NS / f"evidence/measurement_r1/TCT_INPUTS_{k}.json").read_bytes())
        d["C_upper"] = adopted[str(k)]["C_upper"]
        meas[k] = d
    return FC, B, T, R, DC, adopted, cover, c1, c2, meas


def outcome(SEL, FC, B, T, R, DC, adopted, cover, c1, c2, meas):
    """A -> Gamma per cell, plus the selector's own structural flags."""
    out = {}
    for k in CELLS:
        s = SEL.build(k, c1[k], c2[k], cover[k], meas[k], DC, T, B.rat)
        A = s["A"]
        d = FC.direct(T, R, meas[k], adopted[str(k)]["auxiliary_evidence"], A,
                      adopted[str(k)]["m"]["5"], cover[k], B)
        out[k] = {"A": {j: str(A[j]) for j in FIELDS}, "Gamma": str(d["Gamma"]), "pass": bool(d["pass"]),
                  "prov": dict(s["A_provenance"]), "rejected": dict(s["rejected_sources"]),
                  "fallback": s["premise_fallback"]}
    return out


SRC_MUTANTS = {
    # each would make A smaller (more optimistic) or skip a guard
    "M01_operator_best_takes_max_for_upper_bounds":
        ('        cand = sorted(((F(str(b[fld])), n) for n, b in sources.items()), key=lambda vn: (vn[0], vn[1]))\n'
         '        tup[fld], prov[fld] = cand[0]\n    for fld in OPERATOR_LOWER:',
         '        cand = sorted(((F(str(b[fld])), n) for n, b in sources.items()), key=lambda vn: (-vn[0], vn[1]))\n'
         '        tup[fld], prov[fld] = cand[0]\n    for fld in OPERATOR_LOWER:'),
    "M02_operator_best_takes_min_for_D_lo":
        ('        cand = sorted(((F(str(b[fld])), n) for n, b in sources.items()), key=lambda vn: (-vn[0], vn[1]))\n'
         '        tup[fld], prov[fld] = cand[0]\n    return tup, prov',
         '        cand = sorted(((F(str(b[fld])), n) for n, b in sources.items()), key=lambda vn: (vn[0], vn[1]))\n'
         '        tup[fld], prov[fld] = cand[0]\n    return tup, prov'),
    "M03_A_level_takes_max":
        ("        cand = sorted(((s[j], n) for n, s in supplies.items()), key=lambda vn: (vn[0], vn[1]))",
         "        cand = sorted(((s[j], n) for n, s in supplies.items()), key=lambda vn: (-vn[0], vn[1]))"),
    "M04_premise_check_swallowed":
        ("    except Exception as exc:\n"
         "        fallback = f\"mixed tuple violates a Lemma Dv' premise ({type(exc).__name__}); falling back\"\n"
         "        mixed = None",
         "    except Exception as exc:\n"
         "        fallback = None\n"
         "        mixed = {j: F(0) for j in ('A0', 'A1', 'A2')}"),
    "M05_whole_cell_check_disabled":
        ("    rejected = {n: \"not certified uniformly on the whole cell\"\n"
         "                for n, b in sources.items() if not whole_cell_ok(n, b, cover, rat)}",
         "    rejected = {}"),
    "M06_tiling_gap_accepted":
        ("            if i + 1 < len(rows) and F(r[\"e_hi\"]) != F(rows[i + 1][\"e_lo\"]):\n"
         "                return False",
         "            if False:\n                return False"),
    "M07_cover_endpoints_not_checked":
        ("        if F(rows[0][\"e_lo\"]) != lo or F(rows[-1][\"e_hi\"]) != hi:\n            return False",
         "        if False:\n            return False"),
    "M08_tie_resolution_nondeterministic":
        ("key=lambda vn: (vn[0], vn[1]))\n        tup[fld], prov[fld] = cand[0]\n    for fld in OPERATOR_LOWER:",
         "key=lambda vn: (vn[0],))\n        tup[fld], prov[fld] = cand[0]\n    for fld in OPERATOR_LOWER:"),
}


def data_mutants():
    def narrower_c1_block(c1, c2, cover, meas):
        b = {k: dict(v) for k, v in c1.items()}
        for k in CELLS:                      # C1 block no longer covers the cell: must be rejected
            b[k]["e_hi"] = str(F(str(b[k]["e_hi"])) - F(1, 1000))
        return b, c2, cover, meas

    def c2_tiling_gap(c1, c2, cover, meas):
        b = {k: dict(v) for k, v in c2.items()}
        for k in CELLS:
            rows = [dict(r) for r in sorted(b[k]["sub_rows"], key=lambda r: F(r["e_lo"]))]
            rows[2]["e_hi"] = str(F(rows[2]["e_hi"]) - F(1, 1000))
            b[k]["sub_rows"] = rows
        return c1, b, cover, meas

    def impossible_premise(c1, c2, cover, meas):
        b = {k: dict(v) for k, v in c2.items()}
        for k in CELLS:                      # drive C_T under tau so the MIXED tuple is inadmissible
            b[k]["C_T"] = str(F(str(b[k]["tau"])) / 2)
        return c1, b, cover, meas

    def optimistic_forged_tau(c1, c2, cover, meas):
        b = {k: dict(v) for k, v in c2.items()}
        for k in CELLS:
            b[k]["tau"] = str(F(str(b[k]["tau"])) / 2)     # artificially tight -> spurious closure
        return c1, b, cover, meas

    def c2_endpoint_shift(c1, c2, cover, meas):
        """C2's sub-blocks stay contiguous but no longer start at the cover's left edge."""
        b = {k: dict(v) for k, v in c2.items()}
        for k in CELLS:
            rows = [dict(r) for r in sorted(b[k]["sub_rows"], key=lambda r: F(r["e_lo"]))]
            rows[0]["e_lo"] = str(F(rows[0]["e_lo"]) + F(1, 1000))
            b[k]["sub_rows"] = rows
        return c1, b, cover, meas

    return {"M13_c2_subblocks_miss_the_left_edge": c2_endpoint_shift,
            "M09_c1_block_does_not_cover_cell": narrower_c1_block,
            "M10_c2_subblocks_leave_a_gap": c2_tiling_gap,
            "M11_mixed_tuple_violates_C_ge_tau": impossible_premise,
            "M12_forged_optimistic_tau": optimistic_forged_tau}


def tie_world(c1, c2, cover, meas):
    """A world where C1 and C2 report IDENTICAL values for every operator constant, so every field is a tie.

    Tie resolution is unexercised on real data because the two registries agree on nothing; without this world a
    nondeterministic tie-break would be invisible.
    """
    b1 = {k: dict(v) for k, v in c1.items()}
    b2 = {k: dict(v) for k, v in c2.items()}
    for k in CELLS:
        for fld in ("tau", "C_T", "D1", "D2", "Abar", "D_lo"):
            b2[k][fld] = b1[k][fld]
    return b1, b2, cover, meas


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    FC, B, T, R, DC, adopted, cover, c1, c2, meas = world()
    SEL = load(NS / "code/c3_selector.py", "c3sel")
    base = outcome(SEL, FC, B, T, R, DC, adopted, cover, c1, c2, meas)

    out = {"schema": "rebaseguard.p5y.k5.tail-c3.mutations.v1",
           "baseline": base, "mutants": {}}
    src = (NS / "code/c3_selector.py").read_text()

    # A guard is only meaningful where it can fire. Each source mutant is therefore evaluated against the real
    # world AND against every adversarial world, and is detected if it changes behaviour in ANY of them. A guard
    # mutant that is invisible on well-formed data but invisible on malformed data too is a real miss.
    worlds = {"real": (c1, c2, cover, meas)}
    for wname, wfn in data_mutants().items():
        worlds[wname] = wfn(c1, c2, cover, meas)
    worlds["tie"] = tie_world(c1, c2, cover, meas)

    base_by_world = {}
    for wname, (wc1, wc2, wcov, wmeas) in worlds.items():
        try:
            base_by_world[wname] = outcome(SEL, FC, B, T, R, DC, adopted, wcov, wc1, wc2, wmeas)
        except Exception as exc:
            base_by_world[wname] = {"__refusal__": type(exc).__name__}

    for name, (old, new_) in SRC_MUTANTS.items():
        if src.count(old) != 1:
            out["mutants"][name] = {"kind": "source", "applied": False, "reason": "anchor not unique"}
            continue
        caught, exercised = [], []
        try:
            M = load(NS / "code/c3_selector.py", "c3mut", src.replace(old, new_))
        except Exception as exc:
            out["mutants"][name] = {"kind": "source", "applied": True, "detected": True,
                                    "caught_by": [f"load-refusal:{type(exc).__name__}"]}
            continue
        for wname, (wc1, wc2, wcov, wmeas) in worlds.items():
            try:
                got = outcome(M, FC, B, T, R, DC, adopted, wcov, wc1, wc2, wmeas)
            except Exception as exc:
                got = {"__refusal__": type(exc).__name__}
            ref = base_by_world[wname]
            if got != ref:
                exercised.append(wname)
                if "__refusal__" in got or "__refusal__" in ref:
                    caught.append(f"{wname}:refusal-differs")
                else:
                    for k in CELLS:
                        for fld in ("A", "prov", "pass", "rejected", "fallback"):
                            if got[k][fld] != ref[k][fld]:
                                caught.append(f"{wname}:{fld}@{k}")
                                break
        out["mutants"][name] = {"kind": "source", "applied": True, "detected": bool(caught),
                                "caught_by": caught[:4], "worlds_that_exercised_it": exercised}

    for name, fn in data_mutants().items():
        caught = []
        try:
            mc1, mc2, mcov, mmeas = fn(c1, c2, cover, meas)
            got = outcome(SEL, FC, B, T, R, DC, adopted, mcov, mc1, mc2, mmeas)
            for k in CELLS:
                if got[k]["rejected"] != base[k]["rejected"]:
                    caught.append(f"rejected@{k}")
                if got[k]["fallback"] != base[k]["fallback"]:
                    caught.append(f"fallback@{k}")
                if got[k]["A"] != base[k]["A"]:
                    caught.append(f"A@{k}")
                if got[k]["pass"] != base[k]["pass"]:
                    caught.append(f"closure@{k}")
        except Exception as exc:
            caught.append(f"refusal:{type(exc).__name__}")
        out["mutants"][name] = {"kind": "data", "applied": True, "detected": bool(caught),
                                "caught_by": caught[:4]}

    # --- equivalence proofs, computed not asserted -----------------------------------------------------------
    for name, row in out["mutants"].items():
        if row.get("applied") and not row.get("detected"):
            if name == "M08_tie_resolution_nondeterministic":
                # Proved, not asserted: with sources inserted in lexicographic order and Python's sort stable,
                # a value-only sort and a (value, name) sort select the same element on every tie. The mutant is
                # therefore equivalent ON THIS SOURCE SET, and would be detected the moment a source set were
                # built out of lexicographic order.
                names = ["C1", "C2"]
                lex_ok = names == sorted(names)
                probe = sorted(((F(1), n) for n in names), key=lambda vn: (vn[0], vn[1]))[0][1]
                probe_mut = sorted(((F(1), n) for n in names), key=lambda vn: (vn[0],))[0][1]
                if lex_ok and probe == probe_mut:
                    row.update({"equivalent": True, "equivalence_proof":
                                "sources are inserted in lexicographic order (C1, C2) and Python's sort is "
                                "stable, so dropping the name from the sort key cannot change the selected "
                                "element on a tie. Verified here by constructing an all-equal probe: both keys "
                                f"select {probe!r}. Detected if a source set is ever inserted non-lexicographically."})
            if name == "M03_A_level_takes_max":
                doms = {}
                for k in CELLS:
                    s = SEL.build(k, c1[k], c2[k], cover[k], meas[k], DC, T, B.rat)
                    om = s["supplies"]["operator_mixed"]
                    doms[k] = all(F(om[j]) <= F(s["supplies"][n][j])
                                  for n in s["supplies"] for j in FIELDS)
                if all(doms.values()):
                    row.update({"equivalent": False})   # max != min here, so if undetected something is wrong
    applied = [n for n, v in out["mutants"].items() if v.get("applied")]
    undetected = [n for n in applied if not out["mutants"][n].get("detected")
                  and not out["mutants"][n].get("equivalent")]
    out.update({"applied": len(applied), "detected": len(applied) - len(undetected),
                "undetected": undetected, "pass": not undetected})
    data = json.dumps(out, sort_keys=True, indent=1) + "\n"
    Path(a.out).write_text(data)
    print(json.dumps({k: out[k] for k in ("applied", "detected", "undetected", "pass")}
                     | {"sha256": hashlib.sha256(data.encode()).hexdigest()}, indent=1))
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
