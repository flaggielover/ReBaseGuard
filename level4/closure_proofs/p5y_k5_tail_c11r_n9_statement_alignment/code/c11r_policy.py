"""C11R Repair A -- the PROSPECTIVE candidate / depth policy, frozen before any target run.

WHAT THIS MODULE DOES AND DOES NOT TOUCH. It computes nothing on cell 306's drift block. Every
numerical probe here runs on the NON-TARGET block NT = [5/2, 5/2 + 108337/1250000], which lies
above cell 309's upper end (2.0922830) and so belongs to no m=5 cell at all, and which has exactly
cell 306's width, so box geometry transfers. It reads no original magnitude (the firewall scanner
checks this module like every other). It chooses NO candidate: candidates are chosen at execution
by the frozen optimiser in c11r_boxdata, which minimises the certified bound and nothing else.

THE THREE DECISIONS THIS MODULE FREEZES
  1. The families: w = A - B m for K_e and for Khat_e; u = alpha + beta m for the D_lo route.
  2. The selector: exact integer ternary search on frozen rational grids -- tightest certifiable
     member, ties to the smaller slope, A rounded UP and alpha rounded DOWN.
  3. The configuration (depth D, panels P): the member of a frozen candidate set that minimises the
     STRUCTURAL LOSS PER UNIT SLOPE, lambda1 = h_D + step_P + W, subject to a wall-clock cap
     measured on NT. lambda1 is the mechanism the pre-freeze review identified -- the box bound for
     w = A - B m pays about B * (box height + panel z-width) -- computed from geometry alone.

The rule makes ONE execution at ONE configuration and then stops. There is no escalation, so no
decision is ever conditioned on a target certification outcome.
"""
from __future__ import annotations

import json
import pathlib
import re
import resource
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
# A DETERMINISTIC cost model. The first draft chose the configuration by comparing live timings to
# the cap, and its choice sat at 92% of the cap -- from timings taken while the validation job ran
# concurrently. A re-run on an idle machine could measure faster and flip the choice, making the
# frozen configuration depend on machine load. These per-(box x (P+1)) costs are that first
# measurement (policy evidence 2bfbe5a304f35dc3), rounded UP to two decimals; because it was taken
# under load they are pessimistic. The live probe below no longer DECIDES anything: it re-checks
# that these constants remain conservative, and the policy REFUSES to freeze if the machine has
# become more than 25% slower than they assume. P = 256 is dropped: under these costs it fits the
# cap at no depth.
COST_PER_BOX_PANEL = {32: F(37, 100), 64: F(42, 100), 128: F(44, 100)}
SCREEN_SECONDS_PER_STATE = F(19, 10)
COST_TOLERANCE = F(5, 4)
REVIEW_BOXES = [(F(0), F(5, 16), F(0), F(5, 16)), (F(0), F(5, 16), F(15, 16), F(5, 4)),
                (F(5, 2), F(45, 16), F(0), F(5, 16))]


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


def _rss_mb() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / (1024 * 1024) if sys.platform == "darwin" else r / 1024


# ---------------------------------------------------------------------------------------------
# the cost probe, on NT only
# ---------------------------------------------------------------------------------------------
def cost_probe(panels_list=(32, 64, 128)) -> dict:
    """Per-box cost of every Phase 14 operation, measured on NT boxes at each panel count."""
    wK = {(0, 0): F(12), (0, 1): F(-3, 2)}                # manufactured weights, NT only
    uD = {(0, 0): F(1, 2), (0, 1): F(1, 20)}
    out = {}
    for P in panels_list:
        t_data, t_cert = 0.0, 0.0
        for bx in REVIEW_BOXES:
            with BD.PhiCache():
                t = time.time()
                BD.box_upper_coeffs(*bx, NT, P)
                BD.box_lower_coeffs(*bx, NT, P)
                t_data += time.time() - t
                t = time.time()
                I.kernel_box_upper_iv(wK, *bx, NT, P)
                I.kernel_box_upper_iv(wK, *bx, NT, P, atom_removed=True)
                BD.kernel_box_lower_iv(uD, *bx, NT, P)
                t_cert += time.time() - t
        n = len(REVIEW_BOXES)
        out[P] = {"data_pass_seconds_per_box": round(t_data / n, 3),
                  "cached_certification_seconds_per_box": round(t_cert / n, 3),
                  "peak_rss_mb": round(_rss_mb(), 1)}
    return out


def screen_cost_probe() -> float:
    """Seconds per state of the pointwise stage, on NT."""
    t = time.time()
    for (p, m) in ((F(0), F(0)), (F(5, 14), F(15, 14)), (F(5, 2), F(0))):
        BD.pointwise_coeffs(p, m, NT)
    return (time.time() - t) / 3


# ---------------------------------------------------------------------------------------------
# the demonstration on the reviewer's worst boxes, from DISCLOSED numbers and geometry only
# ---------------------------------------------------------------------------------------------
def disclosed_failures() -> dict:
    """Read, mechanically, what the preserved review and the revision-1 screen already disclosed.

    Nothing here is computed on the target block. The review's per-box table and the revision-1
    screen artifact are committed historical evidence; this reads them rather than transcribing
    them, so the numbers are traceable to their source (the M29 defect was a transcribed number).
    """
    review = (C.NS / "review" / "REVIEW_C11R_PREFREEZE.md").read_text()
    rows = re.findall(r"\|\s*`(K_e  w=12-3/2m|Khat w=8-1m)`\s*\|\s*`\(([^)]*)\)`\s*\|\s*"
                      r"([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*\*{0,2}([+\-−][\d.]+)", review)
    box_margin = {}
    for cand, box, _wlo, _kw, llo in rows:
        box_margin[(cand, box.replace(" ", ""))] = float(llo.replace("−", "-"))
    blob = C.blob_at("38f59993", str((C.NS / "evidence" / "screen" / "C11R_SCREEN.json")
                                     .relative_to(C.REPO)))
    scr = json.loads(blob)
    pw = {k: scr["candidates"][k]["min_L_upper_bound"] for k in
          ("K_e  w=12-3/2m", "Khat w=8-1m")}
    binding = {k: scr["candidates"][k]["binding_state"] for k in pw}
    return {"box_margins_from_review": {f"{c} @ {b}": v for (c, b), v in box_margin.items()},
            "rows_parsed": len(box_margin),
            "pointwise_min_from_revision_1_screen": pw,
            "binding_state_from_revision_1_screen": binding,
            "screen_blob_sha256": C.sha256_bytes(blob),
            "review_sha256": C.sha256_file(C.NS / "review" / "REVIEW_C11R_PREFREEZE.md")}


def demonstrate(disc: dict, chosen: tuple[int, int]) -> dict:
    """Would the geometric loss have predicted the disclosed failures? And what does it say now?"""
    box = (F(0), F(5, 16), F(15, 16), F(5, 4))            # contains the binding state (0, 15/14)
    contains = box[0] <= 0 <= box[1] and box[2] <= F(15, 14) <= box[3]
    rows = []
    for cand, B, key in (("K_e  w=12-3/2m", F(3, 2), "0,5/16,15/16,5/4"),
                         ("Khat w=8-1m", F(1), "0,5/16,15/16,5/4")):
        pw = disc["pointwise_min_from_revision_1_screen"][cand]
        bm = disc["box_margins_from_review"].get(f"{cand} @ {key}")
        lam_old = B * (F(5, 16) + step_of(box[0], box[2], 16) + W)
        dd, pp = chosen
        lam_new = B * (F(5, 2 ** dd) + step_of(box[0], box[2], pp) + W)
        rows.append({
            "candidate (discarded, E2/E9)": cand, "slope_B": str(B),
            "disclosed_pointwise_min": pw, "disclosed_box_margin_at_4_16": bm,
            "observed_loss_at_4_16": None if bm is None else round(pw - bm, 5),
            "geometric_loss_bound_at_4_16": round(float(lam_old), 5),
            "bound_covers_observed_loss": None if bm is None else float(lam_old) >= pw - bm,
            "geometry_predicts_failure_at_4_16": float(lam_old) > pw,
            "disclosed_outcome_at_4_16": None if bm is None else ("FAILED" if bm < 0 else "passed"),
            "geometric_loss_bound_at_chosen_config": round(float(lam_new), 5),
        })
    return {"box": "(0, 5/16, 15/16, 5/4)", "contains_binding_state_(0,15/14)": contains,
            "rows": rows,
            "reading": (
                "the pure-geometry loss bound B*(h + step + W) exceeds the observed loss on this "
                "box for both discarded candidates, and exceeds their disclosed pointwise margins, "
                "so geometry alone would have flagged depth 4 / 16 panels as unable to certify "
                "them -- which is what the review found. The bound at the chosen configuration is "
                "smaller. That is a statement about STRUCTURAL LOSS, not a prediction that anything "
                "will certify: a screen or loss figure is never evidence of certifiability "
                "(erratum E10). Under this policy a hand-picked candidate is never submitted at "
                "all; the selector enforces every box constraint, so an uncertifiable member "
                "cannot be selected.")}


def nt_loss_validation(chosen: tuple[int, int]) -> dict:
    """On NT only: does the geometric slope loss upper-bound the ACTUAL box loss, and shrink?"""
    w = {(0, 0): F(10), (0, 1): F(-1)}                   # manufactured, B = 1, NT only
    rows = []
    for (D, P) in ((4, 16), chosen):
        h = F(5, 2 ** D)
        bx = (F(0), h, F(1), F(1) + h)                    # the box at m ~ 1, where screens bind
        with BD.PhiCache():
            wlo = X.poly_eval_iv(w, G.Iv(bx[0], bx[1]), G.Iv(bx[2], bx[3])).lo
            kv = I.kernel_box_upper_iv(w, *bx, NT, P)
            L_box = wlo - 1 - kv.hi
            worst = None
            for (p, m) in ((bx[0], bx[2]), (bx[1], bx[3]), ((bx[0] + bx[1]) / 2,
                                                            (bx[2] + bx[3]) / 2)):
                Lp = X.poly_eval_iv(w, G.Iv(p, p), G.Iv(m, m)).hi - 1 - \
                    I.kernel_apply_iv(w, p, m, NT).lo
                loss = Lp - L_box
                worst = loss if worst is None or loss > worst else worst
        lam = F(1) * (h + step_of(bx[0], bx[2], P) + W)
        rows.append({"config": [D, P], "box": [str(x) for x in bx],
                     "actual_worst_loss": round(float(worst), 5),
                     "geometric_slope_bound": round(float(lam), 5),
                     "bound_covers_actual": worst <= lam})
    return {"block": "NON-TARGET [5/2, 5/2 + 108337/1250000]", "weight": "w = 10 - m (B = 1)",
            "rows": rows,
            "note": ("the slope term ignores the window-end over-count and the drift-range width, "
                     "so it need not dominate everywhere; it is a figure of merit for ranking "
                     "configurations, not a certificate. Correctness never depends on it: the "
                     "selector and the reviewed certifier are rigorous whatever lambda1 says.")}


def main() -> int:
    t0 = time.time()
    stmt = C.load(C.NS / "evidence" / "table" / "C11R_N9_STATEMENTS.json")
    val = C.load(C.NS / "evidence" / "validation" / "C11R_VALIDATION.json")
    v14 = next(c for c in val["checks"] if c["id"] == "V14")["detail"]
    refs = list(v14["float_d_at_atom_reference"].values())
    fd_tightness = {
        "source": "validation V14, NON-TARGET block, read mechanically (not transcribed)",
        "certified_alpha": v14["alpha"], "float_reference_d_at_atom": refs,
        "ratio_alpha_to_reference_min": min(float(F(v14["alpha"])) / r for r in refs),
        "reading": ("on the non-target block the linear sub-solution family is SOUND but LOOSE: it "
                    "certifies a lower bound near a third of an independent float solution. The "
                    "family is kept as frozen on structural grounds. Replacing it with a richer "
                    "one right after learning that it is loose -- by an author who knows the "
                    "original D_lo -- is the move erratum E2 records, so it is not made here. A "
                    "richer family is a candidate for a successor. This is a NON-TARGET fact, "
                    "not a prediction about cell 306."),
    }
    boxes_at = {d: len(X.cover(d)) for d in (4, 5, 6)}

    print("cost probe on the NON-TARGET block (validates the frozen cost model) ...", flush=True)
    cost = cost_probe()
    t_state = screen_cost_probe()
    n_states = len(BD.pointwise_grid(SCREEN_N))
    screen_seconds = float(SCREEN_SECONDS_PER_STATE) * n_states
    model_check = {}
    for P, c in cost.items():
        live = (c["data_pass_seconds_per_box"] + c["cached_certification_seconds_per_box"]) / (P + 1)
        model_check[f"P{P}"] = {"live_per_box_panel": round(live, 4),
                          "frozen_per_box_panel": float(COST_PER_BOX_PANEL[P]),
                          "within_tolerance": live <= float(COST_PER_BOX_PANEL[P] * COST_TOLERANCE)}
    model_check["screen"] = {"live_per_state": round(t_state, 3),
                             "frozen_per_state": float(SCREEN_SECONDS_PER_STATE),
                             "within_tolerance": t_state <= float(SCREEN_SECONDS_PER_STATE
                                                                  * COST_TOLERANCE)}
    if not all(v["within_tolerance"] for v in model_check.values()):
        raise SystemExit(f"REFUSE: the frozen cost model is no longer conservative: {model_check}")

    table = []
    for (d, p) in CONFIG_CANDIDATES:
        est = float(boxes_at[d] * (p + 1) * COST_PER_BOX_PANEL[p]) + screen_seconds
        table.append({"depth": d, "panels": p, "boxes": boxes_at[d],
                      "lambda1": str(lambda1(d, p)), "lambda1_float": float(lambda1(d, p)),
                      "atom_removal_fraction_origin_box": float(atom_removal_fraction(d, p)),
                      "estimated_seconds": round(est, 1),
                      "within_cap": est <= CAP_SECONDS
                      and cost[p]["peak_rss_mb"] <= CAP_RSS_MB})
    feasible = [r for r in table if r["within_cap"]]
    if not feasible:
        raise SystemExit("REFUSE: no configuration fits the resource cap")
    best = min(feasible, key=lambda r: (F(r["lambda1"]), r["estimated_seconds"]))
    chosen = (best["depth"], best["panels"])
    print(f"chosen configuration: depth {chosen[0]}, panels {chosen[1]} "
          f"(lambda1 {best['lambda1_float']:.4f}, est {best['estimated_seconds']:.0f}s)", flush=True)

    disc = disclosed_failures()
    demo = demonstrate(disc, chosen)
    ntv = nt_loss_validation(chosen)

    policy = {
        "schema": "C11R_POLICY/1",
        "status": "FROZEN at the commit that introduces it; applied only in Phase 14",
        "statements_sha256": stmt["sha256"],
        "references_original_magnitudes": False,
        "references_comparison_threshold": False,
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
        },
        "configuration": {
            "rule": ("minimise lambda1 = h_D + step_P + W over the candidate set, subject to the "
                     "estimated Phase 14 wall clock <= CAP and peak RSS <= CAP_RSS; ties to lower "
                     "cost. Geometry and NT cost only."),
            "candidates": table, "chosen": {"depth": chosen[0], "panels": chosen[1]},
            "cap_seconds": CAP_SECONDS, "cap_rss_mb": CAP_RSS_MB,
            "cost_model": {"per_box_panel_seconds": {str(k): str(v) for k, v in
                                                     COST_PER_BOX_PANEL.items()},
                           "screen_seconds_per_state": str(SCREEN_SECONDS_PER_STATE),
                           "source": ("first measurement, policy evidence 2bfbe5a304f35dc3, "
                                      "taken under concurrent load and rounded up"),
                           "deterministic": True,
                           "live_probe_validates_only": model_check},
            "known_risk": ("the chosen configuration's modelled cost is close to the cap. The "
                           "model is pessimistic (measured under load) and the runs module "
                           "enforces the cap before every certification, so an overrun stops "
                           "cleanly as RESOURCE_CAP with finished families kept -- but a slower "
                           "machine at Phase 14 could cost the later families."),
            "boxes_at_depth": boxes_at, "screen_grid": SCREEN_N,
        },
        "stages": [
            "1  pointwise coefficients on a 15x15 grid of R over the block (the cheap screen)",
            "2  one box-data pass at the chosen configuration: upper coefficients for K_e and "
            "Khat_e together, and lower coefficients for the sub-solution",
            "3  exact selection within each family",
            "4  each selected member is first screened pointwise (G10) -- a POINTWISE_REFUTED "
            "member is recorded and NOT sent on -- then certified",
            "5  every output written and hashed under the frozen run schema; then guard DENY",
        ],
        "stop_conditions": [
            "after ONE execution at the chosen configuration. There is no escalation and no retry.",
            "if the wall clock exceeds the cap or RSS exceeds its cap: STOP; unfinished families "
            "are NOT_CERTIFIED with reason RESOURCE_CAP",
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
            "revision 2 (this policy): no candidate is chosen by hand, now or later. The "
            "configuration is chosen here from geometry and NON-TARGET cost; the member of each "
            "family is chosen at Phase 14 by exact optimisation of the certified bound.",
            "no quantity on cell 306's drift block was computed in this repair turn.",
        ],
        "target_scope": {
            "implementable_under_this_policy": ["Abar", "tau", "C_T", "D_lo"],
            "D_lo": "INDEPENDENT_STATEMENT_IMPLEMENTED (sub-solution route; target run pending)",
            "F_D_non_target_tightness": fd_tightness,
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

    evidence = {"schema": "C11R_POLICY_EVIDENCE/1",
                "block_used": "NON-TARGET [5/2, 5/2 + 108337/1250000] only",
                "cost_probe_per_panel_count": {str(k): v for k, v in cost.items()},
                "screen_seconds_per_state": round(t_state, 3),
                "disclosed_failures": disc,
                "demonstration_on_worst_boxes": demo,
                "nt_loss_validation": ntv,
                "policy_sha256": s,
                "seconds": round(time.time() - t0, 1)}
    e = C.write_evidence(C.NS / "evidence" / "policy" / "C11R_POLICY_EVIDENCE.json", evidence,
                         producer=__file__)

    print("\ncandidate configurations (NON-TARGET cost):")
    for r in table:
        mark = "<- chosen" if (r["depth"], r["panels"]) == chosen else ""
        print(f"  D{r['depth']} P{r['panels']:<4d} boxes {r['boxes']:5d}  lambda1 "
              f"{r['lambda1_float']:.4f}  atom-removal {r['atom_removal_fraction_origin_box']:.3f}"
              f"  est {r['estimated_seconds']:8.0f}s  {'ok ' if r['within_cap'] else 'CAP'} {mark}")
    print(f"\ndisclosed rows parsed from the review: {disc['rows_parsed']}")
    for r in demo["rows"]:
        print(f"  {r['candidate (discarded, E2/E9)']:16s} pw {r['disclosed_pointwise_min']:+.4f}"
              f"  box@4/16 {r['disclosed_box_margin_at_4_16']:+.5f}  observed loss "
              f"{r['observed_loss_at_4_16']:.4f}  geometric bound {r['geometric_loss_bound_at_4_16']:.4f}"
              f"  covers={r['bound_covers_observed_loss']}  predicts-failure="
              f"{r['geometry_predicts_failure_at_4_16']}  -> at chosen "
              f"{r['geometric_loss_bound_at_chosen_config']:.4f}")
    print("\nNT loss validation (w = 10 - m on the non-target block):")
    for r in ntv["rows"]:
        print(f"  config {r['config']}  actual worst loss {r['actual_worst_loss']:.4f}  "
              f"slope bound {r['geometric_slope_bound']:.4f}  covers={r['bound_covers_actual']}")
    print(f"\nwrote config/C11R_POLICY.json sha256 {s[:16]}...")
    print(f"wrote evidence/policy/C11R_POLICY_EVIDENCE.json sha256 {e[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
