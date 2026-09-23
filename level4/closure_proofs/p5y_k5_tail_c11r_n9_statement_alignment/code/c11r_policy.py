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

REVISION 4 (review round 3, N-8; errata E24, E28). The configuration RULE is replaced. Revision 3
disclosed (E24) that lambda1 = h_D + step_P + W, a geometric surrogate, ranked the feasible
configurations differently from the non-target evidence. The third reviewer judged that replacing
the rule now, on NON-TARGET evidence only and before any target science, is a legitimate
prospective choice. The new rule, declared here and applied mechanically:
  1  the candidate family is the predeclared finite set CONFIG_CANDIDATES (depth 4-6 x panels
     32/64/128), unchanged since revision 2;
  2  a candidate whose committed-cost estimate x SAFETY_FACTOR exceeds the cap, or whose peak RSS
     exceeds its cap, is rejected (the cap is never raised);
  3  every remaining candidate is evaluated on the fixed NON-TARGET CALIBRATION WORKLOAD below:
     its metric is the WORST RELATIVE box-discretisation loss -- over eight fixed states spanning
     R, both supersolution kernels and the sub-solution -- of the rigorous box bound against the
     tightest rigorous pointwise bound at the box's corners and centre, each loss measured in units
     of the quantity its family certifies at the atom (A for w = A - B m, alpha for
     u = alpha + beta m) so that neither family's scale swamps the other's;
  4  the winner is the lexicographic minimum of (calibration loss, estimated seconds,
     boxes x (panels + 1), depth, panels);
  5  the rule and all its inputs are frozen in the policy; nothing is revisited after a target run.
The workload and metric were declared without reference to which candidate they would favour: they
measure the quantity every certificate pays for -- the margin a box bound gives up against the
states it covers -- on both certified families, at fixed states chosen as a regular pattern.

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
import c11r_procs as PR

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
    seq = cost["sequential"]
    if seq.get("detector") != PR.DETECTOR_LABEL or seq.get("campaign_workers_seen") \
            or not seq.get("samples"):
        raise SystemExit(f"REFUSE: the cost artifact is not certified sequential by the current "
                         f"detector ({PR.DETECTOR_LABEL})")
    der = cost["derived"]
    per = {int(k): F(v["per_box_panel_seconds_max"]) for k, v in der["per_panels"].items()}
    rss = {int(k): v["peak_rss_mb"] for k, v in der["per_panels"].items()}
    return {"per_box_panel": per, "rss_mb": rss, "screen_seconds": F(der["screen_total_seconds"]),
            "cost_artifact_sha256": cost["sha256"], "host": cost["host"],
            "producer_sha256": prov["producer_sha256"]}


def estimate(model: dict, depth: int, panels: int, boxes: int) -> F:
    return boxes * (panels + 1) * model["per_box_panel"][panels] + model["screen_seconds"]


def feasibility(model: dict, boxes_at: dict) -> list[dict]:
    """Steps 1-2: the predeclared family, each with its committed-cost estimate and cap test."""
    table = []
    for (d, p) in CONFIG_CANDIDATES:
        est = estimate(model, d, p, boxes_at[d])
        fits = est * SAFETY_FACTOR <= CAP_SECONDS and model["rss_mb"][p] <= CAP_RSS_MB
        table.append({"depth": d, "panels": p, "boxes": boxes_at[d],
                      "complexity_boxes_x_panels": boxes_at[d] * (p + 1),
                      "lambda1": str(lambda1(d, p)), "lambda1_float": float(lambda1(d, p)),
                      "estimated_seconds": round(float(est), 1),
                      "estimated_seconds_exact": str(est),
                      "estimated_seconds_with_safety_factor": round(float(est * SAFETY_FACTOR), 1),
                      "cap_fraction_with_safety_factor": round(float(est * SAFETY_FACTOR
                                                                     / CAP_SECONDS), 4),
                      "within_cap": fits})
    return table


# ---------------------------------------------------------------------------------------------
# step 3: the fixed NON-TARGET calibration workload
# ---------------------------------------------------------------------------------------------
CALIBRATION_STATES = ((F(0), F(0)), (F(0), F(5, 4)), (F(0), F(5, 2)), (F(5, 4), F(0)),
                      (F(5, 4), F(5, 4)), (F(5, 2), F(0)), (F(5, 4), F(5, 2)),
                      (F(5, 2), F(5, 4)))            # a regular pattern: {0, 5/4, 5/2}^2 in R
CAL_W = {(0, 0): F(12), (0, 1): F(-3, 2)}            # supersolution family member, NT only
CAL_U = {(0, 0): F(1, 2), (0, 1): F(1, 20)}          # sub-solution family member, NT only
# each margin's loss in units of what its family certifies at the atom: A = 12, alpha = 1/2
CAL_SCALE = {"supersolution": CAL_W[(0, 0)], "subsolution": CAL_U[(0, 0)]}
_PW: dict = {}                                       # pointwise bounds do not depend on panels


def _pointwise_upper(x: F, y: F, ar: bool) -> F:
    k = ("w", ar, x, y)
    if k not in _PW:
        _PW[k] = (X.poly_eval_iv(CAL_W, G.Iv(x, x), G.Iv(y, y)).hi - 1
                  - I.kernel_apply_iv(CAL_W, x, y, NT, atom_removed=ar).lo)
    return _PW[k]


def _pointwise_lower(x: F, y: F) -> F:
    k = ("u", x, y)
    if k not in _PW:
        _PW[k] = BD.pointwise_lower_hi(BD.pointwise_coeffs(x, y, NT), CAL_U[(0, 0)],
                                       CAL_U[(0, 1)])
    return _PW[k]


def box_containing(depth: int, p: F, m: F) -> tuple:
    for bx in X.cover(depth):
        a, b, c, d = bx
        if a <= p <= b and c <= m <= d:
            return tuple(bx)
    raise ValueError(f"no depth-{depth} cover box contains ({p}, {m})")


def calibration(depth: int, panels: int) -> dict:
    """The worst RELATIVE box-discretisation loss on the calibration workload, on NT, rigorous
    throughout: for each state's cover box, min over its corners and centre of the pointwise UPPER
    bound of the margin, minus the box LOWER bound of the margin, divided by the family's atom
    value -- for K_e and Khat_e supersolution margins (w = 12 - 3/2 m) and the sub-solution
    margin (u = 1/2 + m/20)."""
    rows = []
    with BD.PhiCache():
        for (p, m) in CALIBRATION_STATES:
            a, b, c, d = box_containing(depth, p, m)
            pts = ((a, c), (a, d), (b, c), (b, d), ((a + b) / 2, (c + d) / 2))
            wbox = X.poly_eval_iv(CAL_W, G.Iv(a, b), G.Iv(c, d))
            for kern, ar in (("K_e", False), ("Khat_e", True)):
                kv = I.kernel_box_upper_iv(CAL_W, a, b, c, d, NT, panels, atom_removed=ar)
                box_lo = wbox.lo - 1 - kv.hi
                pt_hi = min(_pointwise_upper(x, y, ar) for (x, y) in pts)
                rows.append({"state": [str(p), str(m)], "box": [str(t) for t in (a, b, c, d)],
                             "margin": f"supersolution/{kern}", "gap": pt_hi - box_lo,
                             "relative": (pt_hi - box_lo) / CAL_SCALE["supersolution"]})
            ubox = X.poly_eval_iv(CAL_U, G.Iv(a, b), G.Iv(c, d))
            box_lo = (BD.h1_box_lower(a, b, c, d, NT)
                      + BD.kernel_box_lower_iv(CAL_U, a, b, c, d, NT, panels) - ubox.hi)
            pt_hi = min(_pointwise_lower(x, y) for (x, y) in pts)
            rows.append({"state": [str(p), str(m)], "box": [str(t) for t in (a, b, c, d)],
                         "margin": "subsolution/Khat_e", "gap": pt_hi - box_lo,
                         "relative": (pt_hi - box_lo) / CAL_SCALE["subsolution"]})
    worst = max(r["relative"] for r in rows)
    return {"depth": depth, "panels": panels, "metric": str(worst), "metric_float": float(worst),
            "rows": [dict(r, gap=str(r["gap"]), gap_float=float(r["gap"]),
                          relative=str(r["relative"]), relative_float=float(r["relative"]))
                     for r in rows]}


def rank_key(row: dict, cal: dict) -> tuple:
    """Step 4, lexicographic: calibration loss, estimated seconds, complexity, depth, panels."""
    k = f"D{row['depth']}/P{row['panels']}"
    return (F(cal[k]["metric"]), F(row["estimated_seconds_exact"]),
            row["complexity_boxes_x_panels"], row["depth"], row["panels"])


def choose(model: dict, boxes_at: dict, cal: dict) -> tuple[list[dict], dict | None]:
    """The whole rule, from the committed cost artifact and the recorded calibration."""
    table = feasibility(model, boxes_at)
    feasible = [r for r in table if r["within_cap"]]
    if not feasible or any(f"D{r['depth']}/P{r['panels']}" not in cal for r in feasible):
        return table, None
    return table, min(feasible, key=lambda r: rank_key(r, cal))


def old_lambda1_choice(table: list[dict]) -> dict | None:
    """The SUPERSEDED revision-2/3 rule, kept only as a record: minimise lambda1 over the feasible."""
    feasible = [r for r in table if r["within_cap"]]
    return min(feasible, key=lambda r: (F(r["lambda1"]), r["estimated_seconds"])) if feasible \
        else None


def main() -> int:
    t0 = time.time()
    stmt = C.load_allowlisted("evidence/table/C11R_N9_STATEMENTS.json")
    val = C.load_allowlisted("evidence/validation/C11R_VALIDATION.json")
    cost = C.load_allowlisted(COST_ARTIFACT)
    model = cost_model(cost)
    boxes_at = {d: len(X.cover(d)) for d in (4, 5, 6)}
    table = feasibility(model, boxes_at)
    feasible = [r for r in table if r["within_cap"]]
    if not feasible:
        raise SystemExit("REFUSE: no configuration fits the cap with the safety factor. The cap "
                         "is not raised; the policy does not freeze (NOT_READY).")
    print(f"calibrating {len(feasible)} cap-feasible configurations on the NON-TARGET workload ...",
          flush=True)
    cal = {}
    for r in feasible:
        t = time.time()
        k = f"D{r['depth']}/P{r['panels']}"
        cal[k] = calibration(r["depth"], r["panels"])
        cal[k]["seconds"] = round(time.time() - t, 1)
        print(f"  {k:9s} worst box loss {cal[k]['metric_float']:.6f}  ({cal[k]['seconds']}s)",
              flush=True)
    table, best = choose(model, boxes_at, cal)
    if best is None:
        raise SystemExit("REFUSE: the rule selected nothing")
    chosen = (best["depth"], best["panels"])
    old = old_lambda1_choice(table)
    ranking = sorted(feasible, key=lambda r: rank_key(r, cal))
    print(f"chosen configuration: depth {chosen[0]}, panels {chosen[1]}", flush=True)

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
    policy = {
        "schema": "C11R_POLICY/4",
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
            "ruling": "review round 2 ruled the selector legitimate; unchanged in revisions 3 and 4",
        },
        "configuration": {
            "rule": ("from the predeclared finite family CONFIG_CANDIDATES, reject every "
                     "candidate whose committed-cost estimate x SAFETY_FACTOR exceeds CAP or whose "
                     "peak RSS exceeds CAP_RSS; evaluate every remaining candidate on the fixed "
                     "NON-TARGET calibration workload; choose the lexicographic minimum of "
                     "(worst RELATIVE calibration box loss as defined in calibration_workload."
                     "metric, estimated seconds, boxes x (panels + 1), depth, panels). If no "
                     "candidate passes, the policy REFUSES; the cap is never raised."),
            "rule_revision": 4,
            "rule_history": {
                "superseded_rule": ("revisions 2-3: minimise lambda1 = h_D + step_P + W subject "
                                    "to the cap"),
                "superseded_rule_would_choose": ({"depth": old["depth"], "panels": old["panels"]}
                                                 if old else None),
                "why_superseded": ("lambda1 is a geometric surrogate; revision 3 disclosed "
                                   "(erratum E24) that it ranked the feasible configurations "
                                   "differently from the non-target loss evidence"),
                "authority": ("review round 3 (N-8) judged that replacing the rule now, on "
                              "NON-TARGET evidence only and before any target science, is a "
                              "legitimate prospective choice and not post-result tuning"),
                "errata": ["E24", "E28"]},
            "candidate_family": [list(c) for c in CONFIG_CANDIDATES],
            "candidates": table,
            "calibration_workload": {
                "block": "NON-TARGET [5/2, 5/2 + 108337/1250000]",
                "states": [[str(a), str(b)] for a, b in CALIBRATION_STATES],
                "supersolution_weight": "w = 12 - 3/2 m, kernels K_e and Khat_e",
                "subsolution_weight": "u = 1/2 + m/20, kernel Khat_e",
                "sample_points_per_box": "4 corners + centre",
                "metric": ("max over states and margins of ([min over sample points of the "
                           "rigorous pointwise UPPER bound of the margin] - [the rigorous box "
                           "LOWER bound of the margin]) / (the family's atom value: 12 for w, "
                           "1/2 for u)"),
                "normalisation_declared_when": ("before any cross-configuration comparison; "
                                                "the only calibration seen beforehand was one "
                                                "configuration's raw gaps, which showed the raw "
                                                "maximum was set by the supersolution scale "
                                                "alone (erratum E28)"),
                "evaluated_for": "every cap-feasible candidate, and only those"},
            "calibration": {k: {"metric": v["metric"], "metric_float": v["metric_float"]}
                            for k, v in sorted(cal.items())},
            "ranking": [f"D{r['depth']}/P{r['panels']}" for r in ranking],
            "chosen": {"depth": chosen[0], "panels": chosen[1]},
            "cap_seconds": CAP_SECONDS, "cap_rss_mb": CAP_RSS_MB,
            "safety_factor": str(SAFETY_FACTOR),
            "chosen_cap_fraction_with_safety_factor": best["cap_fraction_with_safety_factor"],
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
                                  "the committed cost artifact, geometry and the deterministic "
                                  "interval-arithmetic calibration")},
            "change_history": [
                {"revision": 2, "choice": {"depth": 5, "panels": 64},
                 "basis": "lambda1 with optimistic, uncommitted cost constants (E12)"},
                {"revision": 3, "choice": {"depth": 4, "panels": 128},
                 "basis": "lambda1 with the committed cost artifact and SF 3/2 (E24 disclosed)"},
                {"revision": 4, "choice": {"depth": chosen[0], "panels": chosen[1]},
                 "basis": "the replacement rule on committed non-target calibration (E28)"}],
            "if_the_estimate_exceeds_the_cap": [
                "AT FREEZE: no candidate passes -> this policy REFUSES to freeze (NOT_READY); the "
                "cap is never raised",
                "AT QUALIFICATION (Phase 12): the qualifier re-derives the configuration from the "
                "committed cost artifact and the recorded calibration by this same rule and "
                "requires the frozen choice, and requires the execution host to be the host the "
                "cost was measured on; any difference -> NO_TARGET_EXECUTION. A new "
                "configuration needs a new prospective policy revision and a fresh review, never "
                "an in-place edit",
                "AT EXECUTION (Phase 14): the runner checks the cap BEFORE each stage and each "
                "certification starts; a certification already running is not interrupted, so "
                "the wall clock can exceed the cap by at most the duration of the one "
                "certification in progress (review 4, N4-9); once the cap is exceeded nothing "
                "further starts: the run stops as RESOURCE_CAP, finished families are kept, "
                "unfinished ones are NOT_REACHED, and nothing is retried"],
            "known_risk": ("the calibration is a proxy measured on NON-TARGET geometry; it is not a "
                           "prediction that any family will certify on cell 306. The runs module "
                           "enforces the cap before every certification."),
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
            "after ONE execution at the chosen configuration. There is no escalation and no retry. "
            "What enforces it, exactly (review 4, N4-9): a second COMMITTED execution anywhere in "
            "HEAD's reachable history is refused by c11r_contract.protocol_history; an execution "
            "that is never committed, or committed only outside HEAD's history, cannot be seen by "
            "git and is excluded by the protocol, not proved absent",
            "if the wall clock exceeds the cap or RSS exceeds its cap when a stage or a "
            "certification is about to start: STOP; unfinished families are NOT_REACHED with "
            "reason RESOURCE_CAP. A certification already running is not interrupted: the overrun "
            "is bounded by that one certification's duration, not by the cap",
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
            "revision 3: the lambda1 rule, re-applied with the committed cost artifact and a "
            "prospective safety factor; no review prose or target history is read.",
            "revision 4 (this policy): the lambda1 surrogate is REPLACED by a rule on committed "
            "NON-TARGET calibration evidence (review 3, N-8; errata E24, E28); the configuration "
            "follows from that rule mechanically.",
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
                "an independent candidate for d' and d'' -- the D_lo sub-solution gives neither",
                "bounds on the drift derivatives of the alarm source (sup_source_derivative), "
                "which the original's derivative propagation also consumes (review 3, N-6)"],
            "N9": ("N9 concerns all six constants for cell 306. If D1 and D2 are not independently "
                   "certified, N9 remains OPEN, whatever the other four yield."),
        },
    }
    s = C.write_evidence(C.NS / "config" / "C11R_POLICY.json", policy, producer=__file__)

    evidence = {"schema": "C11R_POLICY_EVIDENCE/4",
                "block_used": "NON-TARGET [5/2, 5/2 + 108337/1250000] only",
                "cost_artifact_sha256": model["cost_artifact_sha256"],
                "calibration_raw": cal,
                "policy_sha256": s,
                "seconds": round(time.time() - t0, 1)}
    e = C.write_evidence(C.NS / "evidence" / "policy" / "C11R_POLICY_EVIDENCE.json", evidence,
                         producer=__file__)

    print(f"\ncandidate configurations (NON-TARGET cost, safety factor {SAFETY_FACTOR}):")
    for r in table:
        k = f"D{r['depth']}/P{r['panels']}"
        mark = "<- chosen" if (r["depth"], r["panels"]) == chosen else ""
        calv = f"{cal[k]['metric_float']:.6f}" if k in cal else "   (not evaluated)"
        print(f"  {k:9s} boxes {r['boxes']:5d}  est {r['estimated_seconds']:8.0f}s  x SF "
              f"{r['estimated_seconds_with_safety_factor']:8.0f}s "
              f"({100 * r['cap_fraction_with_safety_factor']:6.1f}% of cap)  "
              f"{'ok ' if r['within_cap'] else 'CAP'}  calibration {calv} {mark}")
    print(f"superseded lambda1 rule would choose: "
          f"{'D%d/P%d' % (old['depth'], old['panels']) if old else None}")
    print(f"\nwrote config/C11R_POLICY.json sha256 {s[:16]}...")
    print(f"wrote evidence/policy/C11R_POLICY_EVIDENCE.json sha256 {e[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
