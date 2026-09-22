"""C11 Phase 13 -- the N9 verdict, under the criterion frozen in N9_GATE_C11.json.

REVISED in Phase 16 after independent adjudication returned REJECTED. Every finding was verified
mechanically before absorption; see evidence/handover/HANDOVER_FACT_VERIFICATION.json and the ERRATA
block of the gate. The first draft of this module was wrong in three compounding ways:

  * it compared a K_e supersolution against the original's ATOM-REMOVED constant tau (erratum E2);
  * it blamed the box-uniform kernel bound for a candidate family that is infeasible POINTWISE, at
    any depth, for reasons the box bound has nothing to do with (erratum E9);
  * it therefore declared AGREEMENT_INSUFFICIENT when the frozen factor-of-2 criterion was in fact
    reachable -- and reachable with this campaign's own unmodified certifier (erratum E10).

No number below is a literal. Everything measured is read from evidence/runs/C11_CERT_RUNS.json,
which code/c11_runs.py produced. REGISTRY_C2 is still read only here, at comparison time.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11_common as C

GATE_FREEZE = "fed7f309"                 # the commit that froze the criteria
GATE_SHA_AT_FREEZE = "84e1128d1fca20bb"  # the gate FILE's sha256 prefix at that commit
CELL = 307
GATE_PATH = "config/N9_GATE_C11.json"


def _gate_checked() -> dict:
    """Load the gate and REFUSE if its frozen criteria have moved since GATE_FREEZE.

    The first draft recorded GATE_SHA as a bare literal that nothing compared to anything -- the
    defect C10 named as 'frozen values bound only in prose'. Phase 16 appended errata to this file,
    so its hash legitimately changed; what must NOT change is the criteria, and that is now checked
    rather than asserted.
    """
    import json as _json
    here = C.NS / GATE_PATH
    now = _json.loads(here.read_text())
    frozen = _json.loads(C.blob_at(GATE_FREEZE, str(here.relative_to(C.REPO))).decode())
    for key in ("closure_criteria_all_required", "N6_AGREEMENT_CRITERION",
                "permitted_verdicts", "forbidden_conclusions", "guard"):
        if now[key] != frozen[key]:
            raise SystemExit(f"REFUSE: frozen gate section {key!r} has changed since {GATE_FREEZE}")
    if C.sha256_bytes(C.blob_at(GATE_FREEZE, str(here.relative_to(C.REPO)))
                      )[:16] != GATE_SHA_AT_FREEZE:
        raise SystemExit("REFUSE: the gate blob at the freeze commit is not the one recorded")
    return {"gate": now,
            "freeze_commit": GATE_FREEZE,
            "sha256_prefix_at_freeze": GATE_SHA_AT_FREEZE,
            "sha256_prefix_now": C.sha256_file(here)[:16],
            "frozen_sections_verified_unchanged": True,
            "errata_appended_since_freeze": sorted(k for k in now.get("ERRATA", {})
                                                   if k.startswith("E"))}


def main() -> int:
    gate = _gate_checked()
    runs = C.load(C.NS / "evidence" / "runs" / "C11_CERT_RUNS.json")
    cand = runs["candidates"]

    # ---- what the independent certifier MEASURED (no literals) ------------------------------
    certified = {k: v for k, v in cand.items()
                 if v.get("certification", {}).get("certified")}
    refuted = {k: v for k, v in cand.items()
               if v["pointwise"]["REFUTED_AT_ANY_DEPTH"]}
    if not certified:
        raise SystemExit("no certified candidate in the runs artifact")
    best_name = min(certified, key=lambda k: F(certified[k]["w"]["0,0"]))
    best = certified[best_name]
    best_bound = F(best["w"]["0,0"])          # w(atom): the ARL bound at the atom

    # ---- the original's constants, read LAST -------------------------------------------------
    reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
    blk = {b["cell"]: b for b in reg["blocks"]}[CELL]
    tau_orig = F(blk["tau"])                  # Khat_e taboo quantity -- NOT what C11 proves
    abar_orig = F(blk["Abar"])                # K_e whole-kernel ARL bound -- what C11 proves
    e_lo, e_hi = F(blk["e_lo"]), F(blk["e_hi"])

    ratio = best_bound / abar_orig            # erratum E2: Abar-to-Abar
    n6_pass = ratio <= 2

    comparator = {
        "why_Abar_and_not_tau": (
            "taboo_certify.certify_block states the distinction verbatim at lines 202-203. "
            "full=False proves w >= 1 + Khat_e w against the ATOM-REMOVED kernel and yields "
            "(C_T, tau); full=True proves w >= 1 + K_e w against the WHOLE kernel and yields Abar. "
            "C11's certifier proves the full=True statement word for word, so the constant it "
            "produces is Abar. The registry carries both, from two separate certificates."),
        "Abar": {"value": str(abar_orig), "float": float(abar_orig),
                 "artifact_sha256": blk["arl"]["arl_artifact_sha256"],
                 "cpu_seconds": blk["arl"]["cpu_seconds"]},
        "tau": {"value": str(tau_orig), "float": float(tau_orig),
                "note": ("the first draft divided by this. The direction was safe -- Khat_e <= K_e "
                         "pointwise for w >= 0 -- but it is a different quantity, and C11 has never "
                         "implemented Khat_e, so it cannot produce it.")},
        "ratios_of_the_certified_bound": {
            "vs_Abar": float(ratio), "vs_tau": float(best_bound / tau_orig)},
    }

    scope = {
        "N9_as_worded": ("a second, independently written certifier reproducing THE SIX OPERATOR "
                         "CONSTANTS FOR CELL 306 (closing N9)"),
        "what_C11_targeted": {"cell": CELL, "constants": 1, "which": "Abar only"},
        "conforms": False,
        "consequence": ("even perfect agreement here would not close N9 as worded. The gate never "
                        "stated which cell or how many constants closure requires, although phase "
                        "B0 had already extracted the answer verbatim."),
    }

    statement = {
        "original": f"for every e in [{float(e_lo)}, {float(e_hi)}]  (block-uniform)",
        "independent": f"at the single rational e = {runs['drift']['value']}  (point)",
        "conforms": False,
        "consequence": ("C11 solves a strictly easier problem. A certifier that cannot express "
                        "block-uniformity cannot corroborate the original's statement however close "
                        "its number lands. This, not tightness, is the real remaining engineering "
                        "work."),
    }

    criteria = {
        "C11-N1_implementation_independence": "SATISFIED",
        "C11-N2_no_load_bearing_import": "SATISFIED",
        "C11-N3_no_use_of_original_outputs": "SATISFIED",
        "C11-N4_same_frozen_inputs": "PARTIAL -- point drift, not the e-block (erratum E4)",
        "C11-N5_both_sound": ("SATISFIED for the independent certifier; the original's soundness is "
                              "not re-litigated by C11"),
        "C11-N6_agreement": ("SATISFIED against Abar (erratum E2, E10)" if n6_pass else "FAILED"),
        "C11-N7_precision_escalation": ("SATISFIED -- depth 4 measured at "
                                        f"{best['certification']['seconds']} s (erratum E7)"),
        "C11-N8_manufactured_cases": "SATISFIED -- now with producers (erratum E8)",
        "C11-N9_mutation_suite": "SATISFIED",
        "C11-N10_seal_before_compare": "FAILED -- a fixable process omission (erratum E6)",
        "SCOPE_CONFORMANCE": "FAILED -- cell 307 and one constant, where N9 is worded about 306 and six",
    }

    reasons = [
        ("C11-N6 is SATISFIED once the comparator is corrected: the certified bound "
         f"{float(best_bound)} is {float(ratio):.4f}x Abar = {float(abar_orig):.7f}, inside the "
         "frozen factor-of-2 criterion. It is also inside it against the tau the first draft "
         f"wrongly used ({float(best_bound / tau_orig):.4f}x)."),
        ("N9 does NOT close, on grounds the first draft did not identify: the statement is at a "
         "single drift where the original's is uniform on the e-block (C11-N4), and the target is "
         "cell 307 and one constant where N9 is worded about cell 306 and six (SCOPE)."),
        ("The published verdict AGREEMENT_INSUFFICIENT asserted a scientific fact about achievable "
         "tightness. That fact is false, so the label is withdrawn rather than re-argued."),
        ("C11-N10 remains failed, but is booked as a process omission that was available and simply "
         "not arranged -- not as an inherent limitation, and the verdict does not lean on it."),
    ]

    out = {
        "schema": "C11_N9_RESULT/2",
        "supersedes": ("C11_N9_RESULT/1 at commit 832e27aa, whose verdict AGREEMENT_INSUFFICIENT "
                       "and whose WHAT_BLOCKS_CLOSURE are both withdrawn"),
        "gate": gate | {"gate": "<criteria verified unchanged; not duplicated here>"},
        "target_quantity": f"the K5 m=5 tail operator supply at cell {CELL}",
        "runs_artifact": {"path": "evidence/runs/C11_CERT_RUNS.json",
                          "sha256": C.sha256_file(C.NS / "evidence" / "runs" / "C11_CERT_RUNS.json")},
        "comparator": comparator,
        "independent_certified_bound": {
            "candidate": best_name,
            "w": best["w"], "w_at_atom": str(best_bound),
            "depth": best["certification"]["depth"], "panels": best["certification"]["panels"],
            "boxes": best["certification"]["boxes"],
            "margin_lower_bound": best["certification"]["margin_lower_bound"],
            "seconds": best["certification"]["seconds"],
            "statement": best["certification"]["statement"]},
        "comparison": {"independent_bound": float(best_bound), "original_Abar": float(abar_orig),
                       "ratio": float(ratio), "criterion": "ratio <= 2", "agrees": bool(n6_pass)},
        "statement_conformance": statement,
        "scope_conformance": scope,
        "criteria_status": criteria,
        "N9_VERDICT": "EXECUTION_INVALID",
        "N9_STATUS_AFTER_C11": "OPEN",
        "verdict_reasons": reasons,
        "WHAT_C11_DID_ESTABLISH": [
            "a second certifier for this problem EXISTS, is implementationally independent, and is "
            "arithmetic-backend independent as well -- exact rationals against numpy + flint.arb",
            "it is SOUND: standard-normal moments exact 1,0,1,0,3; (K_e 1) = 1 - h1 at six states; "
            "the box bound dominates the pointwise kernel at interior points for a non-constant w; "
            "the constant certificate straddles the theoretical threshold 1/min_R h1 ~ 8070 exactly",
            "it MEETS the frozen factor-of-2 agreement criterion against the correct comparator, at "
            f"{float(ratio):.4f}x Abar, in {best['certification']['seconds']} s of laptop time",
            "there is no scientific disagreement with the original"],
        "WHAT_BLOCKS_CLOSURE": (
            "NOT tightness and NOT compute -- that diagnosis is withdrawn as erratum E9. Two things "
            "block N9. (1) STATEMENT: this certifier takes a scalar drift and cannot express the "
            "block-uniform 'for every e in [e_lo, e_hi]' that the original proves; until it can, no "
            "number it produces corroborates the original's statement. (2) SCOPE: N9 is worded about "
            "six operator constants for cell 306; C11 produced one, for cell 307, and has never "
            "implemented the atom-removed kernel Khat_e that two of those six require."),
        "WHAT_THE_SUCCESSOR_MUST_NOT_INHERIT": [
            "that the box-uniform kernel bound is the binding looseness (false -- erratum E9)",
            "that the drift-aware family w = A - B(p+m) needs more compute (false -- it is "
            "pointwise infeasible below A = 8070 for every B, so it is never better than a constant)",
            "that depth beyond 3 is unaffordable (false -- depth 4 is ~190 s)",
            "that a blinded comparison was structurally unavailable (false -- it was simply not "
            "arranged)"],
        "SUCCESSOR_GUIDANCE": [
            "screen every candidate family POINTWISE first -- exact kernel, one state, ~0.4 s -- "
            "and only subdivide what survives; a negative verdict owes this check before it blames "
            "its own machinery",
            "shape the supersolution like the solution: the true E_x[tau] is ~4.445 at the atom, "
            "flat in p and decreasing in m, so w = A - B*m is the family (pointwise feasible at "
            "A = 4.885, B = 3/4)",
            "give the certifier an INTERVAL drift so it can state the block-uniform result",
            "implement Khat_e -- the atom piece is already isolated in kernel_apply -- which yields "
            "tau and, as sup_R w, C_T: two of the six constants from machinery already validated",
            "target cell 306 and all six constants, or amend N9 explicitly and say why",
            "seal the independent bound before reading REGISTRY_C2",
            "do not reuse the criterion names N1..N10 (erratum E3)"],
        "EXPLICITLY_NOT_CLAIMED": [
            "that N9 is closed", "that F1 has lapsed",
            "that the C2 adoption floor may be replaced",
            "that any cell is closed or adopted", "that r6 may be created"],
        "compute_boundary": {"NEW_REAL": 0, "OPERATOR_CERTIFICATIONS_OF_THE_ORIGINAL": 0,
                             "AWS": 0, "VULTR": 0, "TOOLCHAIN_PROVISIONED": 0, "guard": "DENY"},
    }
    s = C.write_evidence(C.NS / "evidence" / "n9" / "C11_N9_RESULT.json", out)
    print(f"comparator (corrected)       : Abar = {float(abar_orig):.7f}   [NOT tau = "
          f"{float(tau_orig):.9f}]")
    print(f"independent certified bound  : {float(best_bound)}  ({best_name}, depth "
          f"{best['certification']['depth']}, {best['certification']['seconds']}s)")
    print(f"ratio                        : {float(ratio):.4f}x   criterion: <= 2   -> "
          f"{'SATISFIED' if n6_pass else 'FAILED'}")
    print(f"pointwise-refuted candidates : {len(refuted)}  {sorted(refuted)}")
    print(f"\nN9_VERDICT = {out['N9_VERDICT']}   N9 remains {out['N9_STATUS_AFTER_C11']}")
    for r in reasons:
        print(f"  - {r}")
    print(f"\nwrote evidence/n9/C11_N9_RESULT.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
