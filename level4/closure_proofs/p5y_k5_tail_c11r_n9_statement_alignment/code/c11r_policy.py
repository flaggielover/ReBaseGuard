"""C11R -- the PROSPECTIVE candidate / depth policy, frozen before any target run. Revision 3.

WHAT THIS MODULE DOES AND DOES NOT TOUCH. It computes nothing on cell 306's drift block. Every
numerical probe here runs on the NON-TARGET block NT = [5/2, 5/2 + 108337/1250000], which lies
above cell 309's upper end (2.0922830) and so belongs to no m=5 cell at all, and which has exactly
cell 306's width, so box geometry transfers. It reads no original magnitude, no review report and
no historical target computation (the firewall proves it by load-path dataflow). It chooses NO
candidate: candidates are chosen at execution by the frozen optimiser in c11r_boxdata, which
minimises the certified bound and nothing else.

THE THREE DECISIONS THIS MODULE FREEZES
  1. The families: w = A - B m for K_e and for Khat_e; u = alpha + beta m for the D_lo route.
  2. The selector: exact integer ternary search on frozen rational grids -- tightest certifiable
     member, ties to the smaller slope, A rounded UP and alpha rounded DOWN. (Ruled legitimate by
     review round 2; unchanged.)
  3. The configuration (depth D, panels P): the member of a frozen candidate set that minimises the
     STRUCTURAL LOSS PER UNIT SLOPE, lambda1 = h_D + step_P + W, subject to the resource cap. This
     rule is unchanged from revision 2. What changed is the COST MODEL the cap is tested with.

REVISION 3 (review round 2; errata E12, E13, E18). Revision 2 froze cost constants it called
pessimistic, citing a measurement in no commit; the reviewer measured them optimistic, with the
chosen configuration at about 99.6% of the cap. The costs now come from ONE source only, the
committed NON-TARGET cost artifact evidence/cost/C11R_COST.json (c11r_cost.py: sequential, host-
bound, raw observations, constants derived mechanically), and the cap test carries a safety factor
declared here, prospectively: estimate x SAFETY_FACTOR <= CAP. The cap is NOT raised. If no
configuration passes, the policy REFUSES to freeze. This module performs no timing of its own, so
its choice is a deterministic function of the committed cost artifact and geometry.

Revision 2 also parsed the first review report (which quotes original values) and a git blob of
the revision-1 screen (a TARGET computation) to "demonstrate" its configuration. Both reads are
gone. The demonstration is now on NT only.

The rule makes ONE execution at ONE configuration and then stops. There is no escalation, so no
decision is ever conditioned on a target certification outcome.
"""
from __future__ import annotations

import pathlib
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_boxdata as BD
import c11r_common as C
import c11r_idrift as I

X, G = I.X, I.G

W = F(108337, 1250000)                                   # cell 306's block width, exact
NT = I.Blk(F(5, 2), F(5, 2) + W)                          # the non-target block
CAP_SECONDS = 10800                                       # 3 hours for the whole Phase 14 run
CAP_RSS_MB = 8192
GRID = 1000                                               # rational grid for A, B, alpha, beta
B_MAX, BETA_MAX = F(4), F(1)
MU = F(1, 2 ** 60)                                        # strictness, far above ~1e-95 rounding
SCREEN_N = 15
CONFIG_CANDIDATES = [(d, p) for d in (4, 5, 6) for p in (32, 64, 128)]
# THE PROSPECTIVE SAFETY FACTOR. Declared here, before any target execution, and applied to every
# candidate alike: the measured cost is a maximum over a sample of boxes on one host at one time;
# Phase 14 may run on a busier or slower machine, and the round-2 constants were 7% optimistic at
# 64 panels. A configuration is feasible only if estimate x SAFETY_FACTOR <= CAP_SECONDS.
SAFETY_FACTOR = F(3, 2)
COST_ARTIFACT = "evidence/cost/C11R_COST.json"
COST_PRODUCER = "c11r_cost.py"


def step_of(a: F, c: F, panels: int) -> F:
    """The u-panel width of the reviewed box bound on a box with lower corner (a, c)."""
    return (2 * I.CC - a - c + W) / panels


def lambda1(depth: int, panels: int) -> F:
    """Structural loss per unit slope at the worst geometry (the origin box has the widest window)."""
    return F(5, 2 ** depth) + step_of(F(0), F(0), panels) + W


def atom_removal_fraction(depth: int, panels: int) -> F:
    """Share of the origin box's atom window that whole panels can remove in the Khat_e bound."""
    h = F(5, 2 ** depth)
    usable = (1 - 2 * h) - (step_of(F(0), F(0), panels) + W)
    return max(F(0), usable) / 1


# ---------------------------------------------------------------------------------------------
# the cost model: the committed NON-TARGET cost artifact is its only source
# ---------------------------------------------------------------------------------------------
def cost_model(cost: dict) -> dict:
    """Verify the cost artifact is current and derive the estimate function's constants from it."""
    prov = cost["provenance"]
    now = C.sha256_file(C.HERE / COST_PRODUCER)
    if prov["producer_sha256"] != now:
        raise SystemExit("REFUSE: the cost artifact was produced by other code than c11r_cost.py "
                         "as it stands; re-measure")
    if cost["block"] != "NON-TARGET [5/2, 5/2 + 108337/1250000] only":
        raise SystemExit("REFUSE: the cost artifact was not measured on the non-target block")
    if cost["sequential"]["campaign_workers_before"] or cost["sequential"]["campaign_workers_after"]:
        raise SystemExit("REFUSE: the cost artifact was not measured sequentially")
    der = cost["derived"]
    per = {int(k): F(v["per_box_panel_seconds_max"]) for k, v in der["per_panels"].items()}
    rss = {int(k): v["peak_rss_mb"] for k, v in der["per_panels"].items()}
    return {"per_box_panel": per, "rss_mb": rss, "screen_seconds": F(der["screen_total_seconds"]),
            "cost_artifact_sha256": cost["sha256"], "host": cost["host"],
            "producer_sha256": prov["producer_sha256"]}


def estimate(model: dict, depth: int, panels: int, boxes: int) -> F:
    return boxes * (panels + 1) * model["per_box_panel"][panels] + model["screen_seconds"]


def choose(model: dict, boxes_at: dict) -> tuple[list[dict], dict | None]:
    table = []
    for (d, p) in CONFIG_CANDIDATES:
        est = estimate(model, d, p, boxes_at[d])
        fits = est * SAFETY_FACTOR <= CAP_SECONDS and model["rss_mb"][p] <= CAP_RSS_MB
        table.append({"depth": d, "panels": p, "boxes": boxes_at[d],
                      "lambda1": str(lambda1(d, p)), "lambda1_float": float(lambda1(d, p)),
                      "atom_removal_fraction_origin_box": float(atom_removal_fraction(d, p)),
                      "estimated_seconds": round(float(est), 1),
                      "estimated_seconds_with_safety_factor": round(float(est * SAFETY_FACTOR),
                                                                    1),
                      "cap_fraction_with_safety_factor": round(float(est * SAFETY_FACTOR
                                                                     / CAP_SECONDS), 4),
                      "within_cap": fits})
    feasible = [r for r in table if r["within_cap"]]
    best = min(feasible, key=lambda r: (F(r["lambda1"]), r["estimated_seconds"])) \
        if feasible else None
    return table, best


# ---------------------------------------------------------------------------------------------
# the demonstration, on NT only: does the geometric slope loss bound the ACTUAL box loss?
# ---------------------------------------------------------------------------------------------
def nt_loss_validation(configs: list[tuple[int, int]]) -> dict:
    rows = []
    for name, w, B in (("w = 10 - m", {(0, 0): F(10), (0, 1): F(-1)}, F(1)),
                       ("w = 12 - 3/2 m", {(0, 0): F(12), (0, 1): F(-3, 2)}, F(3, 2))):
        for (D, P) in configs:
            h = F(5, 2 ** D)
            bx = (F(0), h, F(1), F(1) + h)                # the box at m ~ 1, where screens bind
            with BD.PhiCache():
                wlo = X.poly_eval_iv(w, G.Iv(bx[0], bx[1]), G.Iv(bx[2], bx[3])).lo
                kv = I.kernel_box_upper_iv(w, *bx, NT, P)
                L_box = wlo - 1 - kv.hi
                worst = None
                for (pp, mm) in ((bx[0], bx[2]), (bx[1], bx[3]),
                                 ((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2)):
                    Lp = X.poly_eval_iv(w, G.Iv(pp, pp), G.Iv(mm, mm)).hi - 1 - \
                        I.kernel_apply_iv(w, pp, mm, NT).lo
                    loss = Lp - L_box
                    worst = loss if worst is None or loss > worst else worst
            lam = B * (h + step_of(bx[0], bx[2], P) + W)
            rows.append({"weight": name, "config": [D, P], "box": [str(x) for x in bx],
                         "actual_worst_loss": round(float(worst), 5),
                         "geometric_slope_bound": round(float(lam), 5),
                         "bound_covers_actual": worst <= lam})
    return {"block": "NON-TARGET [5/2, 5/2 + 108337/1250000]", "rows": rows,
            "reading": ("lambda1 is a figure of merit for RANKING configurations, from geometry "
                        "alone; it is not a certificate and not a prediction that anything will "
                        "certify. Correctness never depends on it: the selector and the reviewed "
                        "certifier are rigorous whatever lambda1 says.")}


def main() -> int:
    t0 = time.time()
    stmt = C.load_allowlisted("evidence/table/C11R_N9_STATEMENTS.json")
    val = C.load_allowlisted("evidence/validation/C11R_VALIDATION.json")
    cost = C.load_allowlisted(COST_ARTIFACT)
    model = cost_model(cost)
    boxes_at = {d: len(X.cover(d)) for d in (4, 5, 6)}
    table, best = choose(model, boxes_at)
    if best is None:
        raise SystemExit("REFUSE: no configuration fits the cap with the safety factor. The cap "
                         "is not raised; the policy does not freeze (NOT_READY).")
    chosen = (best["depth"], best["panels"])
    rev2 = next(r for r in table if (r["depth"], r["panels"]) == (5, 64))
    print(f"chosen configuration: depth {chosen[0]}, panels {chosen[1]} (lambda1 "
          f"{best['lambda1_float']:.4f}, est {best['estimated_seconds']:.0f}s, x{SAFETY_FACTOR} = "
          f"{best['estimated_seconds_with_safety_factor']:.0f}s of {CAP_SECONDS}s)", flush=True)

    checks = {c["id"]: c for c in val["checks"]}
    v14, v17 = checks["V14"]["detail"], checks["V17"]["detail"]
    fd_record = {
        "source": "validation V14 and V17, NON-TARGET block, read mechanically (not transcribed)",
        "family_pointwise_ceiling_alpha": v17["ceiling_alpha"],
        "float_reference_d_at_atom": v17["float_reference_d_at_atom"],
        "ceiling_to_reference_min": v17["ceiling_to_reference_min"],
        "coarse_config_certified_alpha": v14["alpha"], "coarse_config": v14["config"],
        "reading": ("the linear sub-solution family u = alpha + beta m is NOT intrinsically loose "
                    "on the non-target block: its own pointwise ceiling is close to the float "
                    "reference (V17). The much lower alpha certified in V14 is box and panel loss "
                    "at the COARSE validation configuration, not a property of the family "
                    "(erratum E13, correcting round 2). The family is unchanged: it was neither "
                    "refined when it looked loose nor is it changed now. These are NON-TARGET "
                    "facts, not predictions about cell 306."),
    }

    feasible_cfgs = [(r["depth"], r["panels"]) for r in table if r["within_cap"]]
    ntv = nt_loss_validation(sorted({(4, 16), (5, 64)} | set(feasible_cfgs)))
    # DISCLOSURE, not a decision: does the declared lambda1 ranking agree with the ACTUAL
    # non-target loss among the feasible configurations? The rule is not changed either way.
    worst_by_cfg = {}
    for r in ntv["rows"]:
        k = tuple(r["config"])
        worst_by_cfg[k] = max(worst_by_cfg.get(k, 0), r["actual_worst_loss"])
    nt_best = min(feasible_cfgs, key=lambda c: worst_by_cfg[c])
    ntv["ranking_check"] = {
        "feasible_configurations": [list(c) for c in feasible_cfgs],
        "worst_actual_nt_loss_by_configuration": {f"D{c[0]}/P{c[1]}": worst_by_cfg[c]
                                                   for c in feasible_cfgs},
        "chosen_by_the_declared_rule": list(chosen),
        "lowest_actual_nt_loss": list(nt_best),
        "agree": nt_best == chosen,
        "disposition": ("recorded for review; the declared rule (minimise lambda1) is applied "
                        "unchanged whatever this shows, because changing the rule after "
                        "seeing its outcome would be the move the prospective policy exists to "
                        "prevent. Non-target evidence only.")}

    policy = {
        "schema": "C11R_POLICY/3",
        "status": "FROZEN at the commit that introduces it; applied only in Phase 14",
        "statements_sha256": stmt["sha256"],
        "references_original_magnitudes": False,
        "references_comparison_threshold": False,
        "reads_review_prose_or_target_history": False,
        "chooses_a_candidate_now": False,
        "families": {
            "F_K": {"kernel": "K_e", "form": "w = A - B*m", "constraints": "A, B >= 0; A >= 5B",
                    "targets": ["Abar"], "read_out": {"Abar": "w(atom) = A"}},
            "F_H": {"kernel": "Khat_e", "form": "w = A - B*m", "constraints": "A, B >= 0; A >= 5B",
                    "targets": ["tau", "C_T"],
                    "read_out": {"tau": "w(atom) = A", "C_T": "sup over the cover of w = A"}},
            "F_D": {"kernel": "Khat_e", "form": "u = alpha + beta*m",
                    "constraints": "alpha > 0, beta >= 0", "route": "sub-solution",
                    "targets": ["D_lo"], "read_out": {"D_lo": "u(atom) = alpha"}},
            "why_these_families": (
                "C11 found the true E_x[tau] flat in p and decreasing in m, and d is driven by the "
                "m-arm under positive drift; linear-in-m families are the simplest that respect "
                "those shapes, and they keep every box constraint linear so the selection is exact. "
                "They were fixed on structural grounds, before and without any target computation."),
        },
        "selector": {
            "upper": "minimise A over B in {0, 1/1000, ..., 4}; A_req(B) is convex; A rounded UP",
            "lower": "maximise alpha over beta in {0, 1/1000, ..., 1}; alpha_max concave; DOWN",
            "tie_break": "the smaller slope",
            "grid": GRID, "b_max": str(B_MAX), "beta_max": str(BETA_MAX),
            "mu": "2^-60 -- strictness far above the ~1e-95 outward rounding",
            "objective": ("the tightest certifiable bound. This objective is the certifier's own; "
                          "it references neither an original value nor the factor-2 comparator."),
            "certificate": ("the selected upper members are certified by the REVIEWED "
                            "c11r_idrift.supersolution_margin_iv; the lower member by "
                            "c11r_boxdata.subsolution_margin_iv. The selector only chooses."),
            "ruling": "review round 2 ruled the selector legitimate; unchanged in revision 3",
        },
        "configuration": {
            "rule": ("minimise lambda1 = h_D + step_P + W over the candidate set, subject to "
                     "estimated Phase 14 wall clock x SAFETY_FACTOR <= CAP and peak RSS <= "
                     "CAP_RSS; ties to lower cost. Geometry and NON-TARGET cost only. If no "
                     "candidate passes, the policy REFUSES; the cap is never raised."),
            "rule_unchanged_since": "revision 2 (the safety factor is new in revision 3)",
            "candidates": table, "chosen": {"depth": chosen[0], "panels": chosen[1]},
            "cap_seconds": CAP_SECONDS, "cap_rss_mb": CAP_RSS_MB,
            "safety_factor": str(SAFETY_FACTOR),
            "cost_model": {
                "source_artifact": COST_ARTIFACT,
                "source_artifact_sha256": model["cost_artifact_sha256"],
                "source_producer_sha256": model["producer_sha256"],
                "host": model["host"],
                "per_box_panel_seconds": {str(k): str(v) for k, v in
                                          sorted(model["per_box_panel"].items())},
                "screen_seconds": str(model["screen_seconds"]),
                "estimate": "boxes(D) x (P + 1) x per_box_panel(P) + screen_seconds",
                "deterministic": ("the policy performs no timing; its choice is a function of "
                                  "the committed cost artifact and geometry"),
            },
            "change_from_revision_2": {
                "revision_2_choice": {"depth": 5, "panels": 64},
                "revision_2_under_the_corrected_model": {
                    "estimated_seconds": rev2["estimated_seconds"],
                    "with_safety_factor": rev2["estimated_seconds_with_safety_factor"],
                    "within_cap": rev2["within_cap"]},
                "revision_3_choice": {"depth": chosen[0], "panels": chosen[1]},
                "why": ("the corrected, committed cost model and the prospective safety factor, "
                        "applied by the unchanged rule. No target quantity, original magnitude or "
                        "review value informed it; the cap was not raised."),
                "consequence": ("lambda1 at the chosen configuration is "
                                f"{best['lambda1_float']:.4f} against {rev2['lambda1_float']:.4f} "
                                "at depth 5 / 64 panels: a larger structural loss per unit slope. "
                                "Whether that matters for cell 306 is unknown and is NOT "
                                "estimated here."),
            },
            "if_the_estimate_exceeds_the_cap": [
                "AT FREEZE: no candidate passes -> this policy REFUSES to freeze (NOT_READY); the "
                "cap is never raised",
                "AT QUALIFICATION (Phase 12): the qualifier re-derives the configuration from the "
                "committed cost artifact by this same rule and requires the frozen choice, and "
                "requires the execution host to be the host the cost was measured on; any "
                "difference -> NO_TARGET_EXECUTION. A new configuration needs a new prospective "
                "policy revision and a fresh review, never an in-place edit",
                "AT EXECUTION (Phase 14): the runner checks the cap before every certification; "
                "an overrun stops the run as RESOURCE_CAP, finished families are kept, unfinished "
                "ones are NOT_REACHED, and nothing is retried"],
            "known_risk_ranking": (
                "the declared lambda1 ranking and the non-target loss evidence DISAGREE on the "
                "best feasible configuration (policy evidence nt_loss_validation.ranking_check; "
                "erratum E24). The rule is applied unchanged; revising it is a prospective "
                "decision for the user and a review." if not ntv["ranking_check"]["agree"] else
                "the declared lambda1 ranking and the non-target loss evidence agree"),
            "known_risk": ("the runs module enforces the cap before every certification, so an "
                           "overrun stops cleanly as RESOURCE_CAP with finished families kept; "
                           "the qualifier refuses if the execution host differs from the cost "
                           "artifact's host."),
            "boxes_at_depth": boxes_at, "screen_grid": SCREEN_N,
        },
        "stages": [
            "1  pointwise coefficients on a 15x15 grid of R over the block (the cheap screen)",
            "2  one box-data pass at the chosen configuration: upper coefficients for K_e and "
            "Khat_e together, and lower coefficients for the sub-solution",
            "3  exact selection within each family",
            "4  each selected member is first screened pointwise (G10) -- a POINTWISE_INFEASIBLE "
            "member is recorded and NOT sent on -- then certified",
            "5  every output written and hashed under the frozen run schema; then guard DENY",
        ],
        "stop_conditions": [
            "after ONE execution at the chosen configuration. There is no escalation and no retry.",
            "if the wall clock exceeds the cap or RSS exceeds its cap: STOP; unfinished families "
            "are NOT_REACHED with reason RESOURCE_CAP",
            "if a family's selection is infeasible, or its certificate fails: that family is "
            "NOT_CERTIFIED, with the reason recorded; nothing is re-run",
            "a selected member that the reviewed certifier REJECTS although the selector accepted "
            "it would indicate an inconsistency between the two; it is recorded as "
            "SELECTOR_CERTIFIER_MISMATCH and stops that family",
        ],
        "consistency_checks_at_execution": [
            "certified A >= the pointwise lower bound A_pw_min for the same family",
            "certified alpha <= the pointwise upper bound alpha_pw_max",
            "Abar certified value >= tau certified value (Khat_e <= K_e)",
        ],
        "selection_chronology": [
            "38f59993: w = 12 - 3/2 m (K_e) and w = 8 - m (Khat_e) -- the second chosen after the "
            "screen with the original values in view. DISCARDED (erratum E2).",
            "revision 1: the seven screened candidates, all written after the original values "
            "were in the table. SUPERSEDED, not re-ranked (erratum E9).",
            "revision 2: no candidate is chosen by hand, now or later; the configuration from "
            "geometry and NON-TARGET cost; the member of each family at Phase 14 by exact "
            "optimisation of the certified bound.",
            "revision 3 (this policy): the same rule, re-applied with the committed cost artifact "
            "and a prospective safety factor; no review prose or target history is read.",
            "no quantity on cell 306's drift block was computed in any repair turn.",
        ],
        "target_scope": {
            "implementable_under_this_policy": ["Abar", "tau", "C_T", "D_lo"],
            "D_lo": "INDEPENDENT_STATEMENT_IMPLEMENTED (sub-solution route; target run pending)",
            "F_D_non_target_record": fd_record,
            "D1": "PROSPECTIVELY_REACHABLE_BUT_NOT_IMPLEMENTED",
            "D2": "PROSPECTIVELY_REACHABLE_BUT_NOT_IMPLEMENTED",
            "D1_D2_require": [
                "the drift-derivative kernels Khat' and Khat'' (Hermite-weighted densities)",
                "h_1' and h_1''",
                "operator norm bounds kernel_norm(0..3) over the block",
                "a residual-to-error propagation argument consuming THIS campaign's own C_T and "
                "tau, never the original's",
                "an independent candidate for d' and d'' -- the D_lo sub-solution gives neither"],
            "N9": ("N9 concerns all six constants for cell 306. If D1 and D2 are not independently "
                   "certified, N9 remains OPEN, whatever the other four yield."),
        },
    }
    s = C.write_evidence(C.NS / "config" / "C11R_POLICY.json", policy, producer=__file__)

    evidence = {"schema": "C11R_POLICY_EVIDENCE/3",
                "block_used": "NON-TARGET [5/2, 5/2 + 108337/1250000] only",
                "cost_artifact_sha256": model["cost_artifact_sha256"],
                "nt_loss_validation": ntv,
                "policy_sha256": s,
                "seconds": round(time.time() - t0, 1)}
    e = C.write_evidence(C.NS / "evidence" / "policy" / "C11R_POLICY_EVIDENCE.json", evidence,
                         producer=__file__)

    print(f"\ncandidate configurations (NON-TARGET cost, safety factor {SAFETY_FACTOR}):")
    for r in table:
        mark = "<- chosen" if (r["depth"], r["panels"]) == chosen else ""
        print(f"  D{r['depth']} P{r['panels']:<4d} boxes {r['boxes']:5d}  lambda1 "
              f"{r['lambda1_float']:.4f}  est {r['estimated_seconds']:8.0f}s  x SF "
              f"{r['estimated_seconds_with_safety_factor']:8.0f}s "
              f"({100 * r['cap_fraction_with_safety_factor']:5.1f}% of cap)  "
              f"{'ok ' if r['within_cap'] else 'CAP'} {mark}")
    print("\nNT loss validation:")
    for r in ntv["rows"]:
        print(f"  {r['weight']:15s} config {r['config']}  actual worst loss "
              f"{r['actual_worst_loss']:.4f}  slope bound {r['geometric_slope_bound']:.4f}  "
              f"covers={r['bound_covers_actual']}")
    print(f"\nwrote config/C11R_POLICY.json sha256 {s[:16]}...")
    print(f"wrote evidence/policy/C11R_POLICY_EVIDENCE.json sha256 {e[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
