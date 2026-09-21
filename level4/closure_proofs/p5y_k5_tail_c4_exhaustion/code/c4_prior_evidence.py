"""Phase 2: the reuse-first search. Which committed certified quantity, if any, bounds E_a[tau] FROM BELOW?

The search is mechanical in both halves:

  (a) every numeric field of every committed operator-registry artifact for the tail cells is enumerated and
      classified by its DIRECTION with respect to E_a[tau] = tau_a / D -- upper bound, lower bound, two-sided
      enclosure, or unrelated. The classification is by field name against a table written out here in full, and
      any field the table does not name is reported as UNCLASSIFIED rather than silently dropped;

  (b) the whole closure_proofs tree is swept for artifacts whose schema or statement mentions a lower bound on an
      ARL, a stopping time, a subsolution or a minorant, so that a relevant artifact in another namespace cannot
      be missed by having looked only where C4 expected to find one.

    python3 -B c4_prior_evidence.py --out OUT.json
"""
import argparse
import json
import re
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c4_common import C2, CP, NS, OPEN_CELLS, sha  # noqa: E402

C1_NS = CP / "p5y_k5_tail_operator_registry"
AD_NS = CP / "p5y_k5_perron_deflated_resolvent"

# Direction of each certified registry field with respect to E_a[tau] = tau_a(e) / D_e.
# "UPPER"    the field upper-bounds E_a[tau] or one of its numerator ingredients
# "LOWER_D"  the field lower-bounds the DENOMINATOR, which upper-bounds the ratio -- still the wrong direction
# "ENCLOSE"  the field is a two-sided enclosure, so it carries usable information in both directions
# "OTHER"    the field constrains derivatives, geometry or provenance, not the level of E_a[tau]
DIRECTION = {
    "tau": ("UPPER", "w(a) >= tau_a(e) on the block (Lemma T). Bounds the numerator from ABOVE."),
    "C_T": ("UPPER", "sup_X w >= ||Ghat_e||. Bounds an operator norm from ABOVE."),
    "Abar": ("UPPER", "W(a) >= E_a[tau] directly (whole-kernel Lemma T). The wrong direction, by construction."),
    "D_lo": ("LOWER_D", "D_e >= D_lo. Lower-bounding the denominator upper-bounds tau_a/D."),
    "D_mid": ("ENCLOSE", "two-sided enclosure of D at e0. Its UPPER end is usable: it lower-bounds 1/D."),
    "D1": ("OTHER", "|D'| <= D1. Constrains the e-derivative, not the level."),
    "D2": ("OTHER", "|D''| <= D2."),
    "D1_mid_abs_upper": ("OTHER", "|D'(e0)| upper bound."),
    "margin_lower_bound": ("OTHER", "inf_X of the supersolution defect. A lower bound on the defect's INFIMUM; "
                                    "inverting Lemma T needs an upper bound on its SUPREMUM, which is not recorded."),
    "w_min_lower_bound": ("OTHER", "inf_X w >= 0, a validity condition of Lemma T."),
    "allowance_upper": ("OTHER", "truncation allowance of one operator application."),
    "sup_w_chebyshev": ("UPPER", "sup of the candidate polynomial."),
    "candidate_at_atom": ("OTHER", "candidate VALUES at the atom; a candidate is not a bound."),
    "lambda_mid": ("OTHER", "certification allowances at e0."),
    "lambda_cell": ("OTHER", "certification allowances on the cell."),
    "C_upper": ("UPPER", "frozen K1 block bound >= sup_cell ||(I-K_e)^-1|| = sup_cell sup_x E_x[tau] >= E_a[tau]."),
    "arl": ("OTHER", "the nested whole-kernel sub-artifact; its own fields are classified on their own rows."),
    "sub_blocks": ("OTHER", "the count of e-sub-blocks tiling the cell; geometry, not a bound."),
}
META = {"cell", "certified", "schema", "statement", "bits", "depth", "patches", "kind", "cpu_seconds",
        "kernel_calls", "e0", "e_lo", "e_hi", "ec", "delta", "rho", "payload", "payloads", "proposal",
        "arl_alpha", "taboo_alpha", "arl_artifact_sha256", "taboo_artifact_sha256",
        "taboo_cell_artifact_sha256", "sub_rows"}

SWEEP = re.compile(r"subsolution|minorant|lower bound on .*(arl|tau|stopping)|arl_lower|tau_lower|E_a\[tau\] *>=",
                   re.I)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    # ---- (a) direction table over every committed registry field --------------------------------------
    fields, unclassified = {}, set()
    sources = {"C1_registry": C1_NS / "evidence/registry_c1/REGISTRY_C1.json",
               "C2_registry": C2 / "evidence/registry_c2/REGISTRY_C2.json"}
    for name, p in sources.items():
        blocks = {b["cell"]: b for b in json.loads(p.read_bytes())["blocks"]}
        for k in OPEN_CELLS:
            for fld in blocks[k]:
                if fld in META:
                    continue
                if fld not in DIRECTION:
                    unclassified.add(fld)
                fields.setdefault(fld, {"direction": DIRECTION.get(fld, ("UNCLASSIFIED", ""))[0],
                                        "why": DIRECTION.get(fld, ("", "not named in the direction table"))[1],
                                        "seen_in": []})["seen_in"].append(name)
    for k in OPEN_CELLS:
        for tag, p in (("C1_taboo_cell", C1_NS / f"evidence/registry_c1/taboo_cell_{k}.json"),
                       ("C1_arl_cell", C1_NS / f"evidence/registry_c1/arl_cell_{k}.json"),
                       ("C2_taboo_cell", C2 / f"evidence/registry_c2/taboo_cell_{k}.json")):
            if not p.exists():
                continue
            for fld in json.loads(p.read_bytes()):
                if fld in META:
                    continue
                if fld not in DIRECTION:
                    unclassified.add(fld)
                fields.setdefault(fld, {"direction": DIRECTION.get(fld, ("UNCLASSIFIED", ""))[0],
                                        "why": DIRECTION.get(fld, ("", "not named in the direction table"))[1],
                                        "seen_in": []})["seen_in"].append(tag)
    for v in fields.values():
        v["seen_in"] = sorted(set(v["seen_in"]))

    # ---- (b) tree sweep for any lower-bound artifact anywhere -----------------------------------------
    hits = []
    for p in sorted(list(CP.rglob("*.json")) + list(CP.rglob("*.py"))):
        if p.is_relative_to(NS):
            continue                                   # C4's own output is not prior evidence
        try:
            txt = p.read_text()
        except Exception:
            continue
        m = SWEEP.search(txt)
        if m:
            hits.append({"path": p.relative_to(CP).as_posix(),
                         "matched": m.group(0),
                         "context": " ".join(txt[max(0, m.start() - 90):m.end() + 70].split())[:220],
                         "mentions_CUSUM_tail_cell": any(str(c) in txt for c in OPEN_CELLS) and "CUSUM" in txt})

    # ---- the one usable two-sided quantity, extracted ------------------------------------------------
    d_enclosure = {}
    for k in OPEN_CELLS:
        row = {}
        for tag, p in (("C1", C1_NS / f"evidence/registry_c1/taboo_cell_{k}.json"),
                       ("C2", C2 / f"evidence/registry_c2/taboo_cell_{k}.json")):
            if p.exists():
                d = json.loads(p.read_bytes())
                if "D_mid" in d:
                    lo, hi = (F(x) for x in d["D_mid"])
                    row[tag] = {"lo": str(lo), "hi": str(hi), "lo_float": float(lo), "hi_float": float(hi),
                                "sha256": sha(p)}
        d_enclosure[str(k)] = row

    by_dir = {}
    for f, v in fields.items():
        by_dir.setdefault(v["direction"], []).append(f)
    out = {"schema": "rebaseguard.p5y.k5.tail-c4.prior-evidence.v1",
           "question": "does any committed certified quantity bound E_a[tau] from BELOW?",
           "fields": dict(sorted(fields.items())),
           "fields_by_direction": {k: sorted(v) for k, v in sorted(by_dir.items())},
           "unclassified_fields": sorted(unclassified),
           "tree_sweep_regex": SWEEP.pattern,
           "tree_sweep_hits": hits,
           "tree_sweep_adjudicated": {
               "p5y_gate2e_sr_metric/results/sr_metric.json":
                   "SR detector, not CUSUM; binding=false; e=1/4, not a tail cell; its own direction_audit records "
                   "type=UPPER (a LOWER envelope of the hit probability yields an UPPER bound on sup_x E_x[tau]). "
                   "Wrong detector, wrong drift, wrong direction.",
               "p5x_global_nonlinear_dynamics/compute_optimization_r1/drift_minorant.py":
                   "its own docstring states it changes 'the rigorous upper bound used for ||(I - K_e)^{-1}||_inf'. "
                   "A minorant of the hit probability; an UPPER bound on the resolvent. Wrong direction.",
               "manifests_and_checkpoints":
                   "the remaining hits match only inside file listings or an unrelated algorithm name "
                   "('direct-left-minorant-integer-floor-v1'); no quantity is asserted by them.",
           },
           "D_enclosure_at_e0": d_enclosure,
           "ANSWER": ("NO committed certified quantity lower-bounds E_a[tau]. Every field that constrains its LEVEL "
                      "is an upper bound on the numerator or a lower bound on the denominator; the single two-sided "
                      "object, D_mid, constrains only the denominator. A lower bound on E_a[tau] must therefore be "
                      "produced, not reused."),
           "new_real_scientific_addresses_evaluated": 0,
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"fields_by_direction": out["fields_by_direction"],
                      "unclassified_fields": out["unclassified_fields"],
                      "tree_sweep_hits": [h["path"] for h in hits],
                      "sweep_hits_touching_a_CUSUM_tail_cell":
                          [h["path"] for h in hits if h["mentions_CUSUM_tail_cell"]]}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
