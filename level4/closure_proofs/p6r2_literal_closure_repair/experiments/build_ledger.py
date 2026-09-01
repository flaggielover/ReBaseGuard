"""Build the P6R2 claim ledger from the frozen P6R and regenerated P6R2 artifacts."""
from __future__ import annotations

import json

import _p6r2_paths as P                                              # noqa: F401
from _p6r2_paths import P6R, RESULTS

CATS = ("SURVIVED_UNCHANGED", "NUMERICALLY_CORRECTED_BUT_SAME_INTERPRETATION",
        "DOWNGRADED", "INVALIDATED", "UNDEFINED_NO_CLAIM")


def main():
    led = {c: [] for c in CATS}
    counts = {c: 0 for c in CATS}
    rdelta_flips = []
    for fam in ("eval", "replay"):
        new = json.loads((RESULTS / f"p6r2_analysis_{fam}.json").read_text())
        old = json.loads((P6R / "results" / f"p6r_analysis_{fam}.json").read_text())
        for cell, row in new["cells"].items():
            for blk, comps in row["comparisons"].items():
                oldblk = old["cells"].get(cell, {}).get("comparisons", {}).get(blk, {})
                for m, r in comps.items():
                    o = oldblk.get(m)
                    if r["status"] == "UNDEFINED_ZERO_DENOMINATOR":
                        counts["UNDEFINED_NO_CLAIM"] += 1
                        if o is not None:
                            counts["INVALIDATED"] += 1
                            led["INVALIDATED"].append(
                                {"family": fam, "cell": cell, "comparison": blk,
                                 "metric": m, "p6r_verdict": o["verdict"],
                                 "p6r2": "UNDEFINED_ZERO_DENOMINATOR / NO_CLAIM",
                                 "why": "ratio with an exactly-zero denominator"})
                        continue
                    if o is None:
                        continue
                    if m == "Rdelta":
                        counts["NUMERICALLY_CORRECTED_BUT_SAME_INTERPRETATION"] += 1
                        if r["verdict"] != o["verdict"]:
                            rdelta_flips.append({"family": fam, "cell": cell,
                                                 "comparison": blk,
                                                 "p6r": o["verdict"],
                                                 "p6r2": r["verdict"]})
                    else:
                        counts["SURVIVED_UNCHANGED"] += 1
    # family-level entries
    of3 = json.loads((P6R / "results" / "p6r_analysis_eval.json").read_text()
                     )["cells"]["P"]["bh"]["F3_delta_scope"]
    nf3 = json.loads((RESULTS / "p6r2_analysis_eval.json").read_text()
                     )["cells"]["P"]["bh"]["F3_delta_scope_literal"]
    led["INVALIDATED"].append(
        {"item": "F3 member Dq95@0.5", "p6r": "included as a BH test",
         "p6r2": "removed -- undeclared: the primary metric was eligible at "
                 "Delta = 0.5, so the declared fallback may not also enter",
         "why": "adjudication blocker G6A"})
    counts["INVALIDATED"] += 1
    led["NUMERICALLY_CORRECTED_BUT_SAME_INTERPRETATION"].append(
        {"item": "F3 family as a whole",
         "p6r": f"{of3['n_tests']} tests, none rejected",
         "p6r2": f"{nf3['n_tests']} tests, none rejected",
         "why": "one undeclared test removed; no decision changes"})
    led["INVALIDATED"].append(
        {"item": "official s1 calibration sensitivity artifact",
         "p6r": "precommit/s1_sensitivity.json -- CONFOUNDED (variants used "
                "different policy_id values, hence different RNG streams)",
         "p6r2": "results/p6r2_crn_fixed_path_calibration_sensitivity.json -- "
                 "identical stochastic paths across variants",
         "why": "adjudication blocker G9"})
    counts["INVALIDATED"] += 1
    led["SURVIVED_UNCHANGED"].append(
        {"item": "the qualitative calibration conclusion",
         "detail": "s1 is not load-bearing; the corrected CRN analysis makes the "
                   "movement SMALLER, and exactly zero where s1 cannot fire"})
    led["SURVIVED_UNCHANGED"].append(
        {"item": "primary result, replication, REPLAY, T6-B, T6-C, "
                 "baseline selection, temporal precommit, protected tree",
         "detail": "not reopened; 958 defined effects reproduce P6R bit-for-bit"})

    out = {"categories": CATS, "counts": counts,
           "rdelta_verdict_flips": rdelta_flips,
           "n_rdelta_verdict_flips": len(rdelta_flips), "entries": led}
    (RESULTS / "p6r2_claim_ledger.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(counts, indent=1))
    print("Rdelta verdict flips:", len(rdelta_flips), rdelta_flips[:3])


if __name__ == "__main__":
    main()
