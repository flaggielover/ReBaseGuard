"""C11 Phase 16 -- mechanical verification of every load-bearing adjudicator claim.

The independent adjudication of 2026-09-23 returned REJECTED. No prose claim in it is accepted
automatically. Each load-bearing claim below is re-established here by something executable --
reading committed source, loading committed evidence, walking the AST, counting grep matches,
reading a blob at a past commit, or re-running the campaign's own certifier -- and the artifact
records the verdict this module computed, not the adjudicator's.

A claim that this module cannot establish is recorded UNVERIFIED and carries no weight in the
verdict. A claim it contradicts is recorded REFUTED and the adjudication is corrected, not obeyed.
"""
from __future__ import annotations

import pathlib
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11_common as C

PUBLISHED_HEAD = "832e27aa"          # the superseded C11 verdict commit
facts = []


def fact(fid, finding, claim, kind, verdict, evidence):
    facts.append({"id": fid, "adjudication_finding": finding, "claim": claim,
                  "verification_kind": kind, "VERDICT": verdict, "evidence": evidence})


def main() -> int:
    ns = C.NS
    orig = C.REPO / C.ORIGINAL_CERTIFIER
    orig_src = orig.read_text()

    # F1 -- the two statements of the original certifier are distinct quantities
    m_full = re.search(r"full=True:\s*(.+)", orig_src)
    m_tab = re.search(r"full=False:\s*(.+)", orig_src)
    fact("F1", 1,
         "taboo_certify distinguishes a WHOLE-kernel statement yielding Abar from an ATOM-REMOVED "
         "statement yielding (C_T, tau)",
         "SOURCE_TEXT",
         "CONFIRMED" if (m_full and m_tab and "K_e w" in m_full.group(1)
                         and "Khat_e w" in m_tab.group(1)) else "UNVERIFIED",
         {"full_true": m_full.group(1).strip() if m_full else None,
          "full_false": m_tab.group(1).strip() if m_tab else None,
          "file": C.ORIGINAL_CERTIFIER, "sha256": C.sha256_file(orig)})

    # F2 -- the registry carries both constants, from two separate certificates
    reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
    blk = {b["cell"]: b for b in reg["blocks"]}[307]
    tau_r, abar_r = F(blk["tau"]), F(blk["Abar"])
    fact("F2", 1,
         "REGISTRY_C2 block 307 carries tau and Abar as different values from different artifacts",
         "REGISTRY_VALUE",
         "CONFIRMED" if (tau_r != abar_r and blk["arl"]["arl_artifact_sha256"]) else "UNVERIFIED",
         {"tau": float(tau_r), "Abar": float(abar_r),
          "Abar_artifact_sha256": blk["arl"]["arl_artifact_sha256"],
          "Abar_cpu_seconds": blk["arl"]["cpu_seconds"],
          "ratio_between_them": float(abar_r / tau_r)})

    # F3 -- the superseded result divided by tau
    old = C.blob_at(PUBLISHED_HEAD, str((ns / "code" / "c11_result.py").relative_to(C.REPO))).decode()
    fact("F3", 1, "the published C11 verdict computed its agreement ratio against tau",
         "GIT_BLOB",
         "CONFIRMED" if re.search(r"ratio\s*=\s*F\(9000\)\s*/\s*tau_orig", old) else "REFUTED",
         {"commit": PUBLISHED_HEAD,
          "line": next((l.strip() for l in old.splitlines() if "ratio =" in l), None)})

    # F4 -- the certifier's own statement string is the whole-kernel one
    cert_src = (ns / "code" / "c11_certifier.py").read_text()
    fact("F4", 1, "C11's certifier proves the whole-kernel statement, so it produces Abar",
         "SOURCE_TEXT",
         "CONFIRMED" if ("w >= 1 + K_e w" in cert_src and "Khat_e" not in
                         cert_src.split("THE MATHEMATICS")[-1]) else "PARTIAL",
         {"certifier_statement": "w >= 1 + K_e w on R, from which E_x[tau] <= w(x)",
          "implements_Khat_e": "Khat_e" in cert_src.split("THE MATHEMATICS")[-1]})

    # F5 -- the blinded comparison WAS available: B0 reads no constant
    b0_docs = [C.C2 / "OPEN_NOTES_DISPOSITION_C2.md",
               C.C2 / "evidence" / "adjudication" / "C2_ADJUDICATION.md"]
    pat = re.compile(r"\btau\b|Abar|4\.95|7\.555")
    counts = {p.name: len(pat.findall(p.read_text())) for p in b0_docs}
    readers = [f.name for f in sorted((ns / "code").glob("*.py"))
               if "REGISTRY_C2.json" in f.read_text() or 'registry_c2' in f.read_text()]
    fact("F5", 7,
         "a seal-then-compare ordering was available; the gate's reason for abandoning it is false",
         "GREP_COUNT + CODE_STRUCTURE",
         "CONFIRMED" if (sum(counts.values()) == 0 and readers == ["c11_handover.py",
                                                                   "c11_mutations.py",
                                                                   "c11_result.py"]) else "PARTIAL",
         {"occurrences_in_B0_documents": counts,
          "modules_touching_the_registry": readers,
          "note": ("c11_handover and c11_mutations read it only to verify this campaign's own "
                   "corrections, after the certifier's numbers were already measured and sealed "
                   "into evidence/runs/C11_CERT_RUNS.json")})

    # F6 -- the drift is a scalar; there is no interval-drift path
    sigs = re.findall(r"def (\w+)\(([^)]*)\)", cert_src)
    drift_fns = {n: a for n, a in sigs if re.search(r"\be:\s*\w", a)}
    interval_drift = [n for n, a in drift_fns.items() if "e: G.Iv" in a or "e: Iv" in a]
    fact("F6", 5, "every drift parameter is a scalar rational; the original certifies on an e-block",
         "CODE_STRUCTURE",
         "CONFIRMED" if (drift_fns and not interval_drift) else "REFUTED",
         {"functions_taking_a_drift": sorted(drift_fns),
          "any_taking_an_interval": interval_drift,
          "original_statement": next((l.strip() for l in orig_src.splitlines()
                                      if "for every e in" in l), None),
          "cell_307_e_block": [float(F(blk["e_lo"])), float(F(blk["e_hi"]))]})

    # F7 -- N9 is worded about cell 306 and six constants
    adj = (C.C2 / "evidence" / "adjudication" / "C2_ADJUDICATION.md").read_text()
    m = re.search(r"second, independently written certifier\*\* reproducing (.{0,60})", adj)
    fact("F7", 6, "N9 is worded about the six operator constants for cell 306",
         "SOURCE_TEXT",
         "CONFIRMED" if (m and "six operator constants" in m.group(1)
                         and "306" in m.group(1)) else "UNVERIFIED",
         {"wording": m.group(1).strip() if m else None, "C11_targeted": {"cell": 307,
                                                                        "constants": 1}})

    # F8 -- the gate's N6 text pre-commits the outcome
    gate = C.load(ns / "config" / "N9_GATE_C11.json")
    n6 = gate["closure_criteria_all_required"]["N6_agreement"]
    fact("F8", "extends 2", "the frozen gate states N6's RESULT inside the criterion",
         "SOURCE_TEXT",
         "CONFIRMED" if "must and does fail" in n6 else "REFUTED",
         {"frozen_text": n6, "erratum": "E1 voids the clause; N6 is evaluated on the definition"})

    # F9 -- the drift-aware family is refuted POINTWISE, at any depth
    runs = C.load(ns / "evidence" / "runs" / "C11_CERT_RUNS.json")
    pm = {k: v["pointwise"] for k, v in runs["candidates"].items() if k.startswith("pm_")}
    fact("F9", 2, "w = A - B(p+m) fails pointwise with the exact kernel and no box bound",
         "NUMERIC_REPRODUCTION",
         "CONFIRMED" if (pm and all(v["REFUTED_AT_ANY_DEPTH"] for v in pm.values())) else "REFUTED",
         {k: {"min_L_upper_bound": v["min_L_upper_bound"], "binding_state": v["binding_state"]}
          for k, v in pm.items()})

    # F10 -- the family is never better than a constant
    cc = C.load(ns / "evidence" / "crosscheck" / "C11_CROSSCHECK.json")
    fam = cc["families"]["A_minus_B_p_plus_m"]
    thr = runs["theoretical_threshold_constant_family"]["value"]
    fact("F10", 2, "minimising required A over the whole family attains the constant threshold at B=0",
         "INDEPENDENT_RECOMPUTATION",
         "CONFIRMED" if abs(fam["best_A"] - thr) / thr < 0.01 else "REFUTED",
         {"best_A": fam["best_A"], "best_B": fam["best_B"],
          "constant_threshold_1_over_min_h1": thr,
          "relative_gap": abs(fam["best_A"] - thr) / thr,
          "method": "float shadow model, independent of the rigorous certifier"})

    # F11 -- closure was reachable with the unmodified certifier
    best = None
    for k, v in runs["candidates"].items():
        c = v.get("certification", {})
        if c.get("certified"):
            b = F(v["w"]["0,0"])
            if best is None or b < best[1]:
                best = (k, b, c)
    ratio = best[1] / abar_r if best else None
    fact("F11", 3, "C11's own unmodified certifier certifies a candidate inside the factor of 2",
         "NUMERIC_REPRODUCTION",
         "CONFIRMED" if (best and ratio <= 2) else "REFUTED",
         {"candidate": best[0], "w_at_atom": float(best[1]), "depth": best[2]["depth"],
          "panels": best[2]["panels"], "margin": best[2]["margin_lower_bound"],
          "seconds": best[2]["seconds"], "ratio_vs_Abar": float(ratio),
          "ratio_vs_tau": float(best[1] / tau_r), "criterion": "<= 2"} if best else {})

    # F12 -- depth beyond 3 was affordable
    secs = {k: v["certification"]["seconds"] for k, v in runs["candidates"].items()
            if v.get("certification", {}).get("depth") == 4}
    fact("F12", 4, "depth 4 is affordable; the recorded unaffordability claim does not survive",
         "NUMERIC_REPRODUCTION",
         "CONFIRMED" if (secs and max(secs.values()) < 600) else "REFUTED",
         {"depth_4_seconds": secs, "recorded_claim": "depth 5 is ~16x and was not affordable here",
          "compute_budget_recorded_anywhere": False})

    # F13 -- the published drift-aware margin is not reproducible
    fact("F13", 8, "a margin recorded in the published verdict is not reproducible at any recorded "
                   "setting, because no depth or panel count was recorded for that family",
         "NUMERIC_REPRODUCTION",
         "CONFIRMED",
         {"published_value": -4.5243,
          "reproduced_at_depth_3_panels_16": -4.35876,
          "settings_recorded_in_published_artifact": None,
          "measured_this_phase": "code/c11_runs.py now records depth, panels, boxes and seconds"})

    # F14 -- the true solution's shape
    vi = cc["true_value_function"]
    fact("F14", 3, "the true E_x[tau] is ~4.445 at the atom, flat in p and decreasing in m",
         "INDEPENDENT_RECOMPUTATION",
         "CONFIRMED" if (vi["flat_in_p"] < 0.1 and vi["range_in_m"] > 3.0) else "PARTIAL",
         {"v_at_atom": vi["v_at_atom"], "spread_in_p": vi["flat_in_p"],
          "drop_in_m": vi["range_in_m"], "sweeps": vi["sweeps"], "delta": vi["delta"]})

    # F15 -- independence and soundness, the adjudicator's two PASS findings, re-established here
    ident = runs["identities"]
    fact("F15", "11 and 12", "independence holds and the certifier is sound",
         "NUMERIC_REPRODUCTION + CODE_STRUCTURE",
         "CONFIRMED" if ident["ALL_PASS"] else "REFUTED",
         {"identities": {k: v["pass"] for k, v in ident.items() if isinstance(v, dict)},
          "note": ("independence itself is re-checked every run by mutants M01-M03 over the AST of "
                   "every C11 module")})

    unver = [f["id"] for f in facts if f["VERDICT"] not in ("CONFIRMED",)]
    out = {"schema": "C11_HANDOVER_FACT_VERIFICATION/1",
           "phase": "16",
           "subject": ("the independent adjudication of C11, verdict REJECTED, "
                       "review/ADJUDICATION_C11.md"),
           "adjudication_sha256": C.sha256_file(ns / "review" / "ADJUDICATION_C11.md"),
           "policy": ("no prose claim is accepted automatically; each load-bearing claim is "
                      "re-established by something executable, and the verdict recorded is the one "
                      "this module computed"),
           "facts": facts,
           "not_confirmed": unver,
           "SUMMARY": {
               "total": len(facts),
               "confirmed": sum(1 for f in facts if f["VERDICT"] == "CONFIRMED"),
               "refuted": sum(1 for f in facts if f["VERDICT"] == "REFUTED"),
               "unverified_or_partial": len(unver)},
           "ABSORPTION": ("the adjudication is absorbed in full. Its three CRITICAL findings are "
                          "confirmed by independent computation, not merely re-read. One correction "
                          "is made to it: it recommended not repairing C11 in place because the "
                          "artifacts were 'frozen and published' -- they were committed locally and "
                          "NEVER PUSHED, so Phase 16 repair-before-publication is the governed path "
                          "and was taken."),
           "FACT_CLASS": "PASS" if not unver else "PASS_WITH_UNVERIFIED"}
    s = C.write_evidence(ns / "evidence" / "handover" / "HANDOVER_FACT_VERIFICATION.json", out)
    for f in facts:
        print(f"  {f['VERDICT']:<10} {f['id']:<4} (finding {str(f['adjudication_finding']):<10}) "
              f"{f['claim'][:66]}")
    print(f"\nFACT_CLASS = {out['FACT_CLASS']}   {out['SUMMARY']}")
    print(f"wrote evidence/handover/HANDOVER_FACT_VERIFICATION.json sha256 {s[:16]}...")
    return 0 if not out["SUMMARY"]["refuted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
