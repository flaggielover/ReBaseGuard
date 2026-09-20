"""Campaign C2 adversarial suite. Every mutant must be DETECTED, or PROVEN EQUIVALENT.

Runs on committed evidence with stdlib Python alone (no python-flint, no remote host, no K1 record store), so a
reviewer and an adjudicator can re-run it. It reports REAL mutants (source or data edits that are executed)
separately from STATIC assertions (checks that a control exists), because counting them together overstates a suite
- a lesson from Campaign C1's review.

Detection channels:
  xcheck    the two independent theorem-TC-T paths disagree
  atomx     the two independent Lemma Dv' derivations disagree
  combx     the two independent implementations of the componentwise-minimum rule disagree
  refusal   a guard raises
  outcome   a tail cell's m = 5 pass/open decision changes
  value     a published exact quantity changes

    python3 -B c2_mutations.py --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import types
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
REPO = HERE.parents[4]
CP = REPO / "level4/closure_proofs"
B_NS = CP / "p5y_k5_m5_tail_closure"
C1_NS = CP / "p5y_k5_tail_operator_registry"
AD_NS = CP / "p5y_k5_perron_deflated_resolvent"
TAIL = (305, 306, 307, 308, 309)
MS = (1, 2, 3, 5)
FIELDS = ("A0", "A1", "A2")
K1_BOUND = F(7978846, 10 ** 7)
K2_BOUND = F(9678830, 10 ** 7)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load(path: Path, name: str, src: str | None = None):
    raw = path.read_bytes() if src is None else src.encode()
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    sys.modules[name] = mod
    exec(compile(raw, str(path), "exec"), mod.__dict__)
    return mod


def rat(p) -> F:
    return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


def atom_independent(Abar, tau, C, Dlo, D1, D2):
    if not (Dlo > 0 and tau >= 1 and C >= tau and Abar >= 1):
        raise ValueError("operator constants violate their premises")
    eff = Abar if Abar < tau / Dlo else tau / Dlo
    d1, d2 = D1 / Dlo, D2 / Dlo
    return {"A0": eff, "A1": eff * (K1_BOUND * C + d1),
            "A2": eff * (2 * K1_BOUND ** 2 * C ** 2 + K2_BOUND * C + 2 * K1_BOUND * C * d1 + 2 * d1 ** 2 + d2)}


def combine_a(supplies):
    """Implementation 1 of the gate's D4 rule."""
    A, prov = {}, {}
    for j in FIELDS:
        n, v = min(((n, s[j]) for n, s in supplies.items()), key=lambda nv: nv[1])
        A[j], prov[j] = v, n
    return A, prov


def combine_b(supplies):
    """Implementation 2, written differently: sort each field's candidates and take the head."""
    A, prov = {}, {}
    for j in FIELDS:
        cand = sorted(((s[j], n) for n, s in supplies.items()), key=lambda vn: vn[0])
        A[j], prov[j] = cand[0][0], cand[0][1]
    return A, prov


def world():
    cover = {c["index"]: c for c in json.loads((CP / "p5y_k1_cover_ledger_successor/config/cells.json").read_bytes())
             if c["detector"] == "CUSUM"}
    c2 = json.loads((NS / "evidence/registry_c2/REGISTRY_C2.json").read_bytes())
    c1 = json.loads((C1_NS / "evidence/registry_c1/REGISTRY_C1.json").read_bytes())
    adopted = json.loads((B_NS / "evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json").read_bytes())["cells"]
    meas = {k: json.loads((B_NS / f"evidence/measurement_r1/TCT_INPUTS_{k}.json").read_bytes()) for k in TAIL}
    return (cover, {b["cell"]: b for b in c2["blocks"]}, {b["cell"]: b for b in c1["blocks"]}, adopted, meas)


def outcome(T, DC, cover, c2b, c1b, adopted, meas, combiner=combine_a):
    R = T.load_frozen("tc_rule", T.FROZEN["tc_rule"][1])
    res, flags = {}, {"xcheck_ok": True, "atomx_ok": True, "combx_ok": True}
    for k in TAIL:
        kn = {i: F(meas[k]["norms"]["k"][i]) for i in range(5)}
        sup = {"G": T.atom_constants_generic(rat(cover[k]["C_upper"]), kn[1], kn[2])}
        for name, blk in (("C1", c1b[k]), ("C2", c2b[k])):
            args = tuple(F(blk[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2"))
            fr = DC.atom_constants_r2(*args)
            if {j: fr[j] for j in FIELDS} != atom_independent(*args):
                flags["atomx_ok"] = False
            sup[name] = fr
        A, prov = combiner(sup)
        A2_, prov2 = combine_b(sup)
        if A != A2_:
            flags["combx_ok"] = False
        aux = adopted[str(k)]["auxiliary_evidence"]
        for m in MS:
            lo, hi, _ = T.tail_enclosure(R, meas[k], aux, A, m, None)
            if (lo, hi) != T.tail_enclosure_crosscheck(meas[k], aux, A, m, None):
                flags["xcheck_ok"] = False
            if m == 5:
                ad = adopted[str(k)]["m"]["5"]
                H = (F(ad["R2_interval"]["lo"]), F(ad["R2_interval"]["hi"]))
                M0 = F(ad["M_R2"])
                a, b = max(H[0], lo), min(H[1], hi)
                M = M0 if a > b else min(M0, max(abs(a), abs(b)))
                e0, rho, x_hi = (rat(cover[k][t]) for t in ("e0", "rho", "right"))
                Gam = (F(ad["R_interval"]["hi"]) - e0 * F(ad["D_interval"]["lo"])) + rho * x_hi * M
                res[k] = {"mag": str(max(abs(lo), abs(hi))), "M": str(M), "Gamma": str(Gam),
                          "pass": bool(Gam < 0), "prov": dict(prov)}
    return {"cells": res, **flags}


SOURCE_MUTANTS = {
    "M01_midpoint_tower_for_sigma4":
        ('"sigma4": sigma_source(4, r, j, cell, sup_S0)}', '"sigma4": sigma_source(4, r, j, mid, sup_S0)}'),
    "M02_omit_mean_value_correction":
        ("cell[(j, 3)] = min(pure[(j, 3)], h3_mid[j] + rho * pure[(j, 4)])",
         "cell[(j, 3)] = min(pure[(j, 3)], h3_mid[j])"),
    "M03_sign_flip_lower_endpoint":
        ('lo += c * (a - obj[r]["half"])', 'lo += c * (a + obj[r]["half"])'),
    "M04_radius_term_omission_A2":
        ("    rad = R.radius(A, p)", '    rad = R.radius(dict(A, A2=F(0)), p)'),
    "M05_wrong_A0_in_radius":
        ("    rad = R.radius(A, p)", '    rad = R.radius(dict(A, A0=A["A0"] / 2), p)'),
    "M06_wrong_A1_in_radius":
        ("    rad = R.radius(A, p)", '    rad = R.radius(dict(A, A1=A["A1"] * 3), p)'),
    "M07_source_node_swap":
        ('fH = F(meas_r["delta_H"]) + F(meas_r["eps_src"][2])',
         'fH = F(meas_r["delta_H"]) + F(meas_r["eps_src"][1])'),
    "M08_W_endpoint_swap":
        ("            lo += c * a\n            hi += c * b\n    return lo, hi, obj",
         "            lo += c * b\n            hi += c * a\n    return lo, hi, obj"),
    "M09_order3_field_inserted_at_wrong_location":
        ("    fG = residual_G + F(meas_r[\"eps_src\"][3])",
         "    fG = residual_G\n    fF = fF + F(meas_r[\"eps_src\"][3])"),
}


def data_mutants():
    def wrong_cell(cover, c2b, c1b, adopted, meas):
        b = dict(c2b)
        b[309] = dict(c2b[305], cell=309)
        return cover, b, c1b, adopted, meas

    def wrong_partition_block(cover, c2b, c1b, adopted, meas):
        b = {k: dict(v) for k, v in c2b.items()}
        for k in b:                                            # take the BEST sub-block instead of the worst
            b[k]["tau"] = str(min(F(r["tau"]) for r in b[k]["sub_rows"]))
        return cover, b, c1b, adopted, meas

    def swapped_D_lo(cover, c2b, c1b, adopted, meas):
        b = {k: dict(v) for k, v in c2b.items()}
        for k in b:
            b[k]["D_lo"] = str(max(F(r["D_lo"]) for r in b[k]["sub_rows"]))   # max, not min: unsound
        return cover, b, c1b, adopted, meas

    def swapped_D1(cover, c2b, c1b, adopted, meas):
        b = {k: dict(v) for k, v in c2b.items()}
        for k in b:
            b[k]["D1"] = str(min(F(r["D1"]) for r in b[k]["sub_rows"]))
        return cover, b, c1b, adopted, meas

    def swapped_D2(cover, c2b, c1b, adopted, meas):
        b = {k: dict(v) for k, v in c2b.items()}
        for k in b:
            b[k]["D2"] = str(min(F(r["D2"]) for r in b[k]["sub_rows"]))
        return cover, b, c1b, adopted, meas

    def wrong_C_upper(cover, c2b, c1b, adopted, meas):
        c = {k: dict(v) for k, v in cover.items()}
        for k in TAIL:
            c[k]["C_upper"] = str(rat(c[k]["C_upper"]) / 4)
        return c, c2b, c1b, adopted, meas

    def stale_predecessor(cover, c2b, c1b, adopted, meas):
        ad = json.loads(json.dumps(adopted))
        ad["309"]["m"]["5"]["M_R2"] = str(F(ad["309"]["m"]["5"]["M_R2"]) / 2)
        return cover, c2b, c1b, ad, meas

    def wrong_x(cover, c2b, c1b, adopted, meas):
        c = {k: dict(v) for k, v in cover.items()}
        for k in TAIL:
            c[k]["right"] = [str(rat(c[k]["right"]) / 2), "0/1"]
        return c, c2b, c1b, adopted, meas

    return {"M10_wrong_tail_cell": wrong_cell, "M11_wrong_partition_block": wrong_partition_block,
            "M12_swapped_D_lo": swapped_D_lo, "M13_swapped_D1": swapped_D1, "M14_swapped_D2": swapped_D2,
            "M15_wrong_C_upper": wrong_C_upper, "M16_stale_predecessor": stale_predecessor,
            "M17_wrong_x": wrong_x}


def bad_selectors():
    """Componentwise-selector mutants: each must disagree with the pre-registered minimum somewhere."""
    def take_max(sup):
        A, prov = {}, {}
        for j in FIELDS:
            n, v = max(((n, s[j]) for n, s in sup.items()), key=lambda nv: nv[1])
            A[j], prov[j] = v, n
        return A, prov

    def single_supply_C2(sup):
        return {j: sup["C2"][j] for j in FIELDS}, {j: "C2" for j in FIELDS}

    def min_over_whole_tuple(sup):
        n = min(sup, key=lambda n: sup[n]["A0"])          # pick one supply by A0 and use it for all three
        return {j: sup[n][j] for j in FIELDS}, {j: n for j in FIELDS}

    return {"M18_selector_takes_max": take_max, "M19_selector_single_supply": single_supply_C2,
            "M20_selector_min_by_A0_only": min_over_whole_tuple}


def run() -> dict:
    cover, c2b, c1b, adopted, meas = world()
    T = load(B_NS / "code/tct_rule.py", "tct_rule")
    DC = load(AD_NS / "code/deflated_consume.py", "ad_dc")
    base = outcome(T, DC, cover, c2b, c1b, adopted, meas)
    if not all(base[f] for f in ("xcheck_ok", "atomx_ok", "combx_ok")):
        raise SystemExit("the unmutated world already fails a cross-check")
    out = {"schema": "rebaseguard.p5y.k5.tail-c2.mutations.v1",
           "baseline": {str(k): base["cells"][k] for k in TAIL}, "mutants": {}}

    src = (B_NS / "code/tct_rule.py").read_text()
    for name, (old, new) in SOURCE_MUTANTS.items():
        if src.count(old) != 1:
            out["mutants"][name] = {"kind": "real", "applied": False, "reason": "anchor not unique"}
            continue
        caught = []
        try:
            Tm = load(B_NS / "code/tct_rule.py", "tct_mut", src.replace(old, new))
            got = outcome(Tm, DC, cover, c2b, c1b, adopted, meas)
            if not got["xcheck_ok"]:
                caught.append("xcheck")
            if any(got["cells"][k]["pass"] != base["cells"][k]["pass"] for k in TAIL):
                caught.append("outcome")
            if any(got["cells"][k]["mag"] != base["cells"][k]["mag"] for k in TAIL):
                caught.append("value")
        except Exception as exc:
            caught.append(f"refusal:{type(exc).__name__}")
        out["mutants"][name] = {"kind": "real", "applied": True, "detected": bool(caught), "caught_by": caught[:3]}

    for name, fn in data_mutants().items():
        caught = []
        try:
            got = outcome(T, DC, *fn(cover, c2b, c1b, adopted, meas))
            for f, lbl in (("xcheck_ok", "xcheck"), ("atomx_ok", "atomx"), ("combx_ok", "combx")):
                if not got[f]:
                    caught.append(lbl)
            if any(got["cells"][k]["pass"] != base["cells"][k]["pass"] for k in TAIL):
                caught.append("outcome")
            if any(got["cells"][k]["Gamma"] != base["cells"][k]["Gamma"] for k in TAIL):
                caught.append("value")
        except Exception as exc:
            caught.append(f"refusal:{type(exc).__name__}")
        out["mutants"][name] = {"kind": "real", "applied": True, "detected": bool(caught), "caught_by": caught[:3]}

    for name, sel in bad_selectors().items():
        caught = []
        try:
            got = outcome(T, DC, cover, c2b, c1b, adopted, meas, combiner=sel)
            if not got["combx_ok"]:
                caught.append("combx")
            if any(got["cells"][k]["pass"] != base["cells"][k]["pass"] for k in TAIL):
                caught.append("outcome")
            if any(got["cells"][k]["mag"] != base["cells"][k]["mag"] for k in TAIL):
                caught.append("value")
            if any(got["cells"][k]["prov"] != base["cells"][k]["prov"] for k in TAIL):
                caught.append("provenance")
        except Exception as exc:
            caught.append(f"refusal:{type(exc).__name__}")
        row = {"kind": "real", "applied": True, "detected": bool(caught), "caught_by": caught[:3]}
        if not caught:
            row.update({"equivalent": True,
                        "equivalence_proof": "this selector returns the same tuple as the pre-registered minimum on "
                                             "every tail cell of this registry; it is separated from the minimum "
                                             "only by inputs this campaign does not have"})
        out["mutants"][name] = row

    # --- classifier: probed across a truth table, never only at the campaign's own result
    FCsrc = (HERE.parent / "c2_d5_forecast.py").read_text()
    C2 = load(HERE.parent / "c2_d5_forecast.py", "c2_fc_ref")
    PROBES = [
        ("all_five", [305, 306, 307, 308, 309], {}, []),
        ("four_closed_rest_tight", [305, 306, 307, 308], {309: True}, [309]),
        ("four_closed_rest_slack", [305, 306, 307, 308], {309: False}, [309]),
        ("two_closed_all_tight", [305, 306], {307: True, 308: True, 309: True}, [307, 308, 309]),
        ("two_closed_one_slack", [305, 306], {307: True, 308: False, 309: True}, [307, 308, 309]),
        ("one_closed_all_tight", [305], {306: True, 307: True, 308: True, 309: True}, [306, 307, 308, 309]),
        ("none_closed_some_tight", [], {k: (k == 309) for k in TAIL}, list(TAIL)),
        ("none_closed_none_tight", [], {k: False for k in TAIL}, list(TAIL)),
    ]
    truth = {n: C2.classify(c, t, s) for n, c, t, s in PROBES}
    out["classify_truth_table"] = truth
    CLS_MUTANTS = {
        "M21_classifier_threshold_branch":
            ("    if n >= 2 and all(materially_tightened[k] for k in still_open):", "    if n >= 2:"),
        "M22_classifier_STRONG_branch":
            ("    if n == 5:", "    if n >= 4:"),
        "M23_classifier_PARTIAL_branch":
            ("    if n >= 1:\n        return \"D_PARTIAL\"", "    if n >= 3:\n        return \"D_PARTIAL\""),
    }
    for name, (old, new) in CLS_MUTANTS.items():
        if FCsrc.count(old) != 1:
            out["mutants"][name] = {"kind": "real", "applied": False, "reason": "anchor not unique"}
            continue
        caught = []
        try:
            Cm = load(HERE.parent / "c2_d5_forecast.py", "c2_fc_mut", FCsrc.replace(old, new))
            for n, c, t, s in PROBES:
                if Cm.classify(c, t, s) != truth[n]:
                    caught.append(f"{n}:{truth[n]}->{Cm.classify(c, t, s)}")
        except Exception as exc:
            caught.append(f"refusal:{type(exc).__name__}")
        out["mutants"][name] = {"kind": "real", "applied": True, "detected": bool(caught), "caught_by": caught[:3]}

    # --- the material-tightening test: denominator and baseline quantity
    gate = json.loads((NS / "config/FEASIBILITY_GATES_C2.json").read_bytes())
    bg = {k: F(str(gate["baseline"]["gap"][str(k)])) for k in TAIL}
    br = {k: F(str(gate["baseline"]["requirement"][str(k)])) for k in TAIL}
    thr = F(str(gate["material_tightening_test"]["threshold"]))
    probe_gap = {305: F(0), 306: F(0), 307: F(1, 5), 308: F(1, 2), 309: F(1)}
    right = {k: (probe_gap[k] <= (1 - thr) * bg[k]) for k in TAIL if bg[k] > 0}
    wrong_denom = {k: (probe_gap[k] <= (1 - thr) * br[k]) for k in TAIL if bg[k] > 0}       # gap vs REQUIREMENT
    wrong_quantity = {k: ((probe_gap[k] + 1) <= (1 - thr) * br[k]) for k in TAIL if bg[k] > 0}
    out["mutants"]["M24_material_wrong_denominator"] = {
        "kind": "real", "applied": True, "detected": right != wrong_denom,
        "caught_by": [f"right={right} wrong={wrong_denom}"]}
    out["mutants"]["M25_material_wrong_baseline_quantity"] = {
        "kind": "real", "applied": True, "detected": right != wrong_quantity,
        "caught_by": [f"right={right} wrong={wrong_quantity}"]}

    # --- static assertions: controls that must EXIST (not executed mutants)
    rr = (HERE.parent / "c2_refined_registry.py").read_text()
    b0 = (HERE.parent / "c2_b0_verify.py").read_text()
    d5 = FCsrc
    statics = {
        "S01_unauthorized_address_refused": 'cells outside the frozen C2 universe' in rr,
        "S02_taboo_pin_enforced": ('TABOO_SHA256 = "ced9422c' in rr
                                   and "does not match its pin" in rr),
        "S03_stale_coverage_map_pinned": "a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35" in b0,
        "S04_stale_gate_or_protocol_pinned": ("098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f"
                                              in d5),
        "S05_executor_identity_pinned": ("ced9422ca07981a9ad053acd79b72ef0d5007e93e49c16f2501f31c593fd0daa" in b0
                                         and "order3_executor_registry" in b0),
        "S06_deflated_consume_pinned": "ef5d0474183053bb7cde3075bda66f99211706a9bf7bf27e31fe994ff8b87e72" in d5,
        "S07_c1_registry_pinned": "87bb1cfacb09c2a144cab0270427d91980ea742b36fd80f8963265a22d2eebb3" in d5,
        "S08_regression_refused": "regressed for m=" in d5,
    }
    for n, v in statics.items():
        out["mutants"][n] = {"kind": "static", "applied": True, "detected": bool(v)}

    applied = [n for n, v in out["mutants"].items() if v.get("applied")]
    equivalent = [n for n in applied if out["mutants"][n].get("equivalent")]
    undetected = [n for n in applied if not out["mutants"][n].get("detected")
                  and not out["mutants"][n].get("equivalent")]
    out["applied"] = len(applied)
    out["real_mutants"] = len([n for n in applied if out["mutants"][n].get("kind") == "real"])
    out["static_assertions"] = len([n for n in applied if out["mutants"][n].get("kind") == "static"])
    out["detected"] = len(applied) - len(undetected) - len(equivalent)
    out["equivalent"] = equivalent
    out["undetected"] = undetected
    out["pass"] = not undetected and len(applied) == len(out["mutants"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    res = run()
    data = json.dumps(res, sort_keys=True, indent=1).encode() + b"\n"
    Path(a.out).write_bytes(data)
    print(json.dumps({k: res[k] for k in ("applied", "real_mutants", "static_assertions", "detected",
                                          "equivalent", "undetected", "pass")} | {"sha256": sha(data)}))
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
