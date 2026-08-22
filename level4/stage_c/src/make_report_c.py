#!/usr/bin/env python
"""Stage C step 6 — figures, ledger and the Stage C method report."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np

import figures_c as F
import policy
from campaign import RESULTS, cell_path
from rebaseguard_level4 import provenance
from rebaseguard_level4.ledger import Ledger

STAGE_C = Path(__file__).resolve().parents[1]
FIGS = STAGE_C / "figures"
LEVEL4_REPORTS = STAGE_C.parent / "reports"
REPRESENTATIVE = (0.0, 0.03, 0.067, 0.10, 0.25, 1.0)


def fmt(v, d=4):
    return "—" if v is None else f"{v:.{d}f}"


def load(name):
    p = RESULTS / name
    return json.loads(p.read_text()) if p.exists() else None


def load_incontrol_cell(rho, args):
    key = {"rho": float(rho), "n_replicates": args["n_replicates"],
           "n_cycles": args["n_cycles"], "burn_in": args["burn_in"],
           "master_seed": args["master_seed"], "m": 1,
           "n_bootstrap": args["n_bootstrap"], "acurve": "arl_curve.json"}
    p = cell_path("incontrol", key)
    return json.loads(p.read_text()) if p.exists() else None


def build_figures(ic, det, findings, acurve):
    FIGS.mkdir(parents=True, exist_ok=True)
    rows = ic["rows"]
    rbg = findings["policy"]["conservative_rho"]
    label = rf"ReBaseGuard $\rho={rbg:.4f}$ ($\delta$=0.2, conservative)"
    oracle = findings["oracle"]["rho"]
    index = {}

    index["fig01_mse_vs_rho.png"] = F.fig_metric_vs_rho(
        rows, "reference_mse", r"stationary reference MSE  $\mathbb{E}_\pi[e^2]$",
        FIGS / "fig01_mse_vs_rho.png",
        title="Stationary reference MSE against reuse fraction",
        rbg_rho=rbg, rbg_label=label, ci_key="reference_mse_ci",
        oracle_rho=oracle, reference=1.0,
        reference_label=r"fresh baseline ($1/m$)").name

    index["fig02_arl_vs_rho.png"] = F.fig_metric_vs_rho(
        rows, "cycle_arl", "in-control cycle ARL",
        FIGS / "fig02_arl_vs_rho.png",
        title="In-control cycle ARL against reuse fraction",
        rbg_rho=rbg, rbg_label=label, ci_key="cycle_arl_ci",
        oracle_rho=oracle).name

    if det:
        shifts = sorted({r["shift"] for r in det["rows"]})
        index["fig03_detection_delay.png"] = F.fig_detection(
            det["rows"], shifts, FIGS / "fig03_detection_delay.png",
            rbg_rho=rbg, rbg_label=label).name

    eff = [{"rho": r["rho"],
            "reuse_weight": r["rho"],
            "fresh_per_observation": (0.0 if r["rho"] >= 1.0
                                      else 1.0 / r["cycle_arl"])}
           for r in rows]
    index["fig04_sample_efficiency.png"] = F.fig_metric_vs_rho(
        eff, "fresh_per_observation",
        "fresh observations per monitored observation",
        FIGS / "fig04_sample_efficiency.png",
        title="Fresh-sample consumption against reuse fraction",
        rbg_rho=rbg, rbg_label=label, oracle_rho=oracle).name

    if det:
        shift = 1.0
        front = findings["pareto"].get(str(shift), {}).get("front_rho", [])
        idx = [i for i, r in enumerate(sorted(rows, key=lambda z: z["rho"]))
               if r["rho"] in front]
        index["fig05_pareto.png"] = F.fig_pareto(
            rows, det["rows"], FIGS / "fig05_pareto.png", shift=shift,
            rbg_rho=rbg, oracle_rho=oracle, front=idx).name

    cells = {}
    for rho in REPRESENTATIVE:
        c = load_incontrol_cell(rho, ic["arguments"])
        if c:
            cells[rho] = c
    if cells:
        index["fig06_stationary_densities.png"] = F.fig_stationary_densities(
            cells, FIGS / "fig06_stationary_densities.png").name

    index["fig07_a_curve.png"] = F.fig_a_curve(
        acurve["records"], FIGS / "fig07_a_curve.png").name

    index["fig08_arl_decomposition.png"] = F.fig_decomposition(
        rows, FIGS / "fig08_arl_decomposition.png", rbg_rho=rbg,
        rbg_label=label).name

    index["fig09_stability_boundary.png"] = F.fig_stability_boundary(
        rows, FIGS / "fig09_stability_boundary.png",
        policy_rows=findings["policy"]["table"]).name

    (FIGS / "figure_index.json").write_text(json.dumps(index, indent=2))
    return index


def build_ledger(findings, ic, det, adv, acurve):
    L = Ledger()
    rbg = findings["policy"]["conservative_rho"]
    dom = findings["domination"]
    L.add("SC-F1", "Frozen Level 1-3, Stage A and Stage B are quoted unchanged; "
                   "Stage C adds no claim about them and modifies no frozen "
                   "artifact.", "FROZEN-CERTIFIED",
          evidence=["closure/04_ARB_CERTIFICATE.md",
                    "level4/stage_b/certificate/period2_certificate.json"])
    L.add("SC-F2", "F'_rho(0) = rho(1-Gamma) and F_rho = rho F_1 are Level 2C "
                   "results used here as given.", "FROZEN-PROVED",
          evidence=["rebaseguard_phase2c.md"])
    L.add("SC-M1", f"The ReBaseGuard policy is rho_safe(delta) = "
                   f"clip((1-delta)/(Gamma-1), 0, 1); at delta = 0.2, substituting the "
                   f"upper end of the frozen Gamma enclosure gives "
                   f"rho = {rbg:.6f}.",
          "METHOD-DEFINITION",
          evidence=["level4/stage_c/src/policy.py",
                    "level4/stage_c/STAGE_C_PROTOCOL.md"],
          notes="Defined before any Stage C evaluation and independent of every "
                "Stage B and Stage C outcome; enforced by a test that scans the "
                "module for outcome values and identifiers.")
    L.add("SC-M2", "The CONSERVATIVE variant keeps |F'_rho(0)| <= 1-delta for "
                   "every Gamma the frozen enclosure admits, because "
                   "|F'_rho(0)| = rho(Gamma-1) increases in Gamma.",
          "RIGOROUS-CERTIFIED",
          evidence=["level4/stage_c/tests/test_policy.py"],
          notes="Certified for LOCAL LINEAR stability of the DETERMINISTIC map "
                "only. It is not a statement about the noisy recursion.")
    L.add("SC-M3", "The POINT variant is heuristic: at the upper end of the "
                   "frozen Gamma enclosure its reuse fraction would exceed the "
                   "local stability boundary. It is reported only for contrast.",
          "NEW-NUMERICAL", evidence=["level4/stage_c/results/adversarial.json"])

    rows = {r["rho"]: r for r in ic["rows"]}
    L.add("SC-N1", f"Stationary reference MSE falls monotonically from "
                   f"{rows[0.0]['reference_mse']:.4f} at rho = 0 to a minimum of "
                   f"{min(r['reference_mse'] for r in ic['rows']):.4f}, then rises "
                   f"to {rows[1.0]['reference_mse']:.4f} at full reuse.",
          "NEW-NUMERICAL",
          evidence=["level4/stage_c/results/incontrol_main.json"])
    L.add("SC-N2", f"In-control cycle ARL is non-monotone in rho: "
                   f"{rows[0.0]['cycle_arl']:.2f} at rho = 0, peaking near "
                   f"rho = {max(ic['rows'], key=lambda r: r['cycle_arl'])['rho']:g}, "
                   f"falling to {rows[1.0]['cycle_arl']:.2f} at full reuse.",
          "NEW-NUMERICAL")
    L.add("SC-N3", "A(e) = E[tau | e] is symmetric within Monte Carlo error and "
                   "monotone decreasing in |e| across the whole tested grid; "
                   "monotonicity was TESTED, not assumed.",
          "NEW-NUMERICAL",
          evidence=["level4/stage_c/results/arl_curve.json"],
          numbers={"A_at_0": acurve["records"][len(acurve["records"]) // 2]["A"],
                   "symmetry_max_abs_z": acurve["symmetry"]["max_abs_z"]})
    L.add("SC-NULL1",
          "Crossing the local stability boundary rho_c leaves NO visible "
          "signature in stationary reference MSE or in cycle ARL: both vary "
          "smoothly through rho_c with no kink or discontinuity.",
          "NEW-NUMERICAL",
          notes="A null result, and an important one: the certified local "
                "boundary is not an observable transition in these endpoints. "
                "The nonlinearity of F_1 caps the instability well before it "
                "shows up in stationary summaries.")
    L.add("SC-NULL2",
          f"The ReBaseGuard policy is NOT performance-optimal: a fixed "
          f"rho = {dom['oracle_rho']:g} attains reference MSE "
          f"{dom['mse_oracle']:.4f} against {dom['mse_rbg']:.4f} for the policy.",
          "NEW-NUMERICAL",
          notes="Pre-registered in STAGE_C_PROTOCOL.md section 12 BEFORE the "
                "campaign, reported as a headline limitation. The policy buys "
                "a certified local-stability guarantee, not optimality.")
    c6 = [d for d in findings["detection"] if not d["c6_pass"]]
    L.add("SC-NULL3",
          f"Pre-specified criterion C6 FAILED at "
          f"{', '.join(f'Delta={d['shift']:g}' for d in c6)}: ReBaseGuard's raw "
          f"detection delay exceeds full reuse's by more than the 25% threshold. "
          f"The criterion was left unchanged and the Stage C decision reflects "
          f"the failure.",
          "FAILED-TO-REPRODUCE",
          evidence=["level4/stage_c/notes/CRITERION_C6_DIAGNOSIS.md",
                    "level4/stage_c/results/detection_main.json"],
          notes="The criterion compares raw delays across policies whose "
                "in-control ARLs differ by 1.7x. Full reuse's delay-to-baseline "
                "ratio is ~1.0 at every shift, i.e. it alarms at essentially the "
                "same rate with or without a change -- the ABSENCE of "
                "sensitivity. On that baseline-free measure ReBaseGuard "
                "preserves sensitivity (0.93 -> 0.41) and is absolutely faster "
                "than full reuse at Delta = 1.5. The criterion was badly "
                "formulated; it was not rewritten.")
    L.add("SC-NULL4",
          "The C7 decomposition check initially failed (max |z| = 3.70) because "
          "the implementation omitted the bias_interp term the protocol had "
          "already specified. With the specified formula it gives 2.12; with a "
          "sharper Richardson bias estimate 3.34, and 2 of 23 points would "
          "exceed 3.",
          "NEW-NUMERICAL",
          evidence=["level4/stage_c/notes/PROTOCOL_DEVIATIONS.md"],
          notes="Recorded because this is the one correction that turned a "
                "failure into a pass. Raw agreement between the two ARL routes "
                "is better than 0.6% at every rho, the discrepancy's sign and "
                "grid-scaling are fully explained by log-linear interpolation of "
                "a convex function, and the C7 verdict does not change the Stage "
                "C decision because C6 already fails.")
    L.add("SC-OPEN1",
          "Nothing here concerns the invariant law of the noisy recursion. "
          "Empirical stationary shapes are numerical descriptions only; no "
          "bimodality, ergodicity or stochastic period-2 claim is made.",
          "OPEN")
    L.add("SC-OPEN2",
          "Pre-allocated thinning and sample splitting are not implemented: "
          "both would change the frozen re-baselining rule.", "OPEN")
    L.add("SC-OPEN3",
          "Only m = 1, k = 1/2, h = 5, Gaussian innovations, and shifts applied "
          "at a cycle boundary. Adaptive reuse is untouched.", "OPEN")
    return L


def write_report(findings, ic, det, adv, acurve, index) -> str:
    rows = sorted(ic["rows"], key=lambda r: r["rho"])
    byrho = {r["rho"]: r for r in rows}
    rbg = findings["policy"]["conservative_rho"]
    rbg_p = findings["policy"]["point_rho"]
    dom = findings["domination"]
    decision = findings["decision"]
    L, A = [], None
    A = L.append

    A("# ReBaseGuard Level 4 — Stage C")
    A("")
    A("## Stability-Aware Reuse, Monitoring Consequences, and the "
      "Reuse–Performance Tradeoff")
    A("")
    A(f"**Decision: `{decision}`**")
    A("")
    A("> **Scope.** Stage B's rigorous theorem concerns the **deterministic**")
    A("> conditional-mean map `F_1`, *not* the noisy recursion")
    A("> `E_{j+1} = F_1(E_j) + noise`. Nothing in Stage C upgrades it. Every")
    A("> stationary shape below is an empirical, numerical description; no")
    A("> bimodality, ergodicity or stochastic period-2 claim is made anywhere.")
    A("")
    A("---")
    A("")
    A("## 1. Scientific question")
    A("")
    A("Not *does reuse cause instability* — Stage A and Stage B settled that.")
    A("The Stage C question is whether the **certified local stability**")
    A("boundary can be used to *control* reuse: keep some alarm-triggering data,")
    A("avoid recursive reference instability, and not wreck monitoring.")
    A("")
    A("---")
    A("")
    A("## 2. Frozen theoretical inputs")
    A("")
    A("| Input | Value | Status |")
    A("|---|---|---|")
    A("| `F_rho = rho F_1`, `F_1'(0) = 1 - Gamma` | exact | FROZEN-PROVED (Level 2C) |")
    A(f"| `Gamma` enclosure | `[{policy.GAMMA_CERT_LOW:.7f}, "
      f"{policy.GAMMA_CERT_HIGH:.7f}]` | FROZEN-CERTIFIED (Arb) |")
    A(f"| `Gamma` point estimate | `{policy.GAMMA_POINT:.6f} ± "
      f"{policy.GAMMA_POINT_SE:.6f}` | NEW-NUMERICAL (Stage A) |")
    A(f"| `rho_c = 1/(Gamma-1)` | point `{findings['policy']['rho_c_point']:.6f}`; "
      f"certified `[{findings['policy']['rho_c_certified'][0]:.6f}, "
      f"{findings['policy']['rho_c_certified'][1]:.6f}]` | derived |")
    A("| Stage B period-2 orbit at `rho=1` | `e* ∈ [1.028724, 1.044724]`, "
      "`lambda_2 ∈ [0.1081, 0.8325]` | RIGOROUS-CERTIFIED, deterministic map |")
    A("")
    A("---")
    A("")
    A("## 3. The ReBaseGuard policy")
    A("")
    A("Require `|F'_rho(0)| <= 1 - delta`. Since `|F'_rho(0)| = rho (Gamma - 1)`:")
    A("")
    A("```text")
    A("rho_safe(delta) = clip( (1 - delta) / (Gamma - 1), 0, 1 )")
    A("```")
    A("")
    A("| Variant | `Gamma` used | Guarantee | Evidence class |")
    A("|---|---|---|---|")
    A(f"| POINT | `{policy.GAMMA_POINT:.6f}` | holds *if* the Monte Carlo "
      f"estimate is exact | heuristic, **NOT certified** |")
    A(f"| **CONSERVATIVE** | `{policy.GAMMA_CERT_HIGH:.6f}` | holds for the "
      f"**true** `Gamma` | **certified**, local linear stability, deterministic "
      f"map only |")
    A("")
    A("| `delta` | POINT `rho` | CONSERVATIVE `rho` |")
    A("|---|---|---|")
    for d in (0.05, 0.1, 0.2, 0.5):
        p = policy.rho_safe(d, variant=policy.POINT).rho
        q = policy.rho_safe(d, variant=policy.CONSERVATIVE).rho
        star = "**" if d == 0.2 else ""
        A(f"| {star}{d}{star} | {star}{p:.6f}{star} | {star}{q:.6f}{star} |")
    A("")
    A(f"**Headline: `delta = 0.2`, CONSERVATIVE, `rho = {rbg:.6f}`.** Fixed in")
    A("the protocol before the campaign. `delta = 0.2` was chosen as a")
    A("conventional 20% margin, not for performance.")
    A("")
    A("The distinction between the two variants is not cosmetic. At the")
    A("certified upper end of `Gamma`, the POINT variant's reuse fraction gives")
    A(f"`|F'_rho(0)| = {rbg_p * (policy.GAMMA_CERT_HIGH - 1):.3f} > 1` — i.e. it")
    A("would sit on the *unstable* side of the boundary. That is why only the")
    A("conservative variant carries a guarantee.")
    A("")
    A("---")
    A("")
    A("## 4. Pre-specified protocol")
    A("")
    A("`level4/stage_c/STAGE_C_PROTOCOL.md`, frozen before the campaign, fixes")
    A("the endpoints, grids, sample sizes, tolerances, the policy and the")
    A("success criteria. Section 12 of that protocol pre-registers the")
    A("possibility that a fixed `rho` dominates the policy — see §12 below.")
    A("")
    A("---")
    A("")
    A("## 5. Experimental design")
    A("")
    a = ic["arguments"]
    A(f"* **In-control:** the FROZEN Stage A multi-cycle simulator, "
      f"{a['n_replicates']} replicates × {a['n_cycles']:,} retained cycles, "
      f"burn-in {a['burn_in']:,}, master seed `{a['master_seed']}`. "
      f"{len(rows)} `rho` cells.")
    if det:
        d = det["arguments"]
        A(f"* **Detection:** {d['n_replicates']:,} independent change events per "
          f"cell. `tau` is heavy-tailed (in control at `rho=0`: mean ≈ 78, "
          f"median 16, sd ≈ 173), so 100 events would give ~22% relative error — "
          f"far too coarse for criterion C6.")
    A("* **Statistical unit:** the replicate. All intervals are 95% percentile")
    A("  bootstrap over replicates, never over cycles.")
    A("* **CRN:** the same master seed across `rho`, so every between-`rho`")
    A("  comparison is a **paired** replicate contrast. Naive independent-point")
    A("  standard errors are never used for such comparisons.")
    A("* **Grid:** all 21 protocol points retained; 2 points added (the two")
    A("  policy values) and recorded as additions; 4 further points added near")
    A("  `rho_c` by the adversarial refinement check. Nothing was deleted.")
    A("")
    A("---")
    A("")
    A("## 6. Stability results")
    A("")
    A("| `rho` | regime | ref. MSE | 95% CI | cycle ARL | 95% CI | alternation | ACF₁ |")
    A("|---|---|---|---|---|---|---|---|")
    reg = {r["rho"]: r["regime"] for r in findings["regimes"]}
    for r in rows:
        tag = ""
        if abs(r["rho"] - rbg) < 1e-9:
            tag = " **←RBG**"
        elif abs(r["rho"] - rbg_p) < 1e-9:
            tag = " ←RBG-pt"
        elif abs(r["rho"] - dom["oracle_rho"]) < 1e-9:
            tag = " ←ORACLE"
        A(f"| {r['rho']:g}{tag} | {reg[r['rho']].split('/')[0]} | "
          f"{r['reference_mse']:.5f} | "
          f"[{r['reference_mse_ci'][0]:.5f}, {r['reference_mse_ci'][1]:.5f}] | "
          f"{r['cycle_arl']:.3f} | "
          f"[{r['cycle_arl_ci'][0]:.3f}, {r['cycle_arl_ci'][1]:.3f}] | "
          f"{r['alternation_rate']:.4f} | {r['acf_e_lag1']:+.4f} |")
    A("")
    c = findings["contrasts"]
    A("**Paired contrasts** (replicate-level, CRN-aware):")
    A("")
    A(f"* `MSE(rho=1) - MSE(RBG)` = **{c['mse_full_minus_rbg']['point']:.4f}** "
      f"[{c['mse_full_minus_rbg']['ci_low']:.4f}, "
      f"{c['mse_full_minus_rbg']['ci_high']:.4f}]")
    A(f"* `MSE(rho=1) / MSE(RBG)` = **{c['mse_full_over_rbg']['point']:.4f}** "
      f"[{c['mse_full_over_rbg']['ci_low']:.4f}, "
      f"{c['mse_full_over_rbg']['ci_high']:.4f}]")
    A(f"* `MSE(fresh) - MSE(RBG)` = {c['mse_fresh_minus_rbg']['point']:.4f} "
      f"[{c['mse_fresh_minus_rbg']['ci_low']:.4f}, "
      f"{c['mse_fresh_minus_rbg']['ci_high']:.4f}]")
    A("")
    A("### The `rho_c` null finding")
    A("")
    A("**Crossing the certified local stability boundary produces no visible")
    A("signature in either headline endpoint.** Reference MSE and cycle ARL both")
    A("vary smoothly through `rho_c ≈ 0.067` with no kink, no discontinuity and")
    A("no change of slope that the grid can resolve — the four extra points added")
    A("at `rho ∈ {0.055, 0.062, 0.068, 0.072}` confirm it.")
    A("")
    A("This is a genuine null result and it matters for interpretation: the")
    A("local boundary is a statement about the linearisation of `F_1` at `e = 0`,")
    A("and the strong nonlinearity of `F_1` caps the resulting instability long")
    A("before it reaches a stationary summary. A practitioner cannot find")
    A("`rho_c` by looking at MSE or ARL curves; it has to come from the theory.")
    A("")
    A("---")
    A("")
    A("## 7. ARL mechanism")
    A("")
    sym = acurve["symmetry"]
    mono = acurve["monotonicity"]
    mid = acurve["records"][len(acurve["records"]) // 2]
    A(f"`A(e) = E[tau | E_j = e]` was estimated on {len(acurve['records'])} grid")
    A(f"points spanning `|e| <= 5`, {acurve['n_paths']:,} paths each, with")
    A("**independent seeds per grid point** (no CRN): `A` is consumed by an")
    A("integral, so independent errors average down, whereas CRN would make them")
    A("systematic.")
    A("")
    A(f"* `A(0) = {mid['A']:.3f} ± {mid['A_se']:.3f}` against the frozen "
      f"in-control `ARL_0 ≈ 465.4`")
    A(f"* **symmetry:** {sym['n_pairs']} mirror pairs, max `|z| = "
      f"{sym['max_abs_z']:.2f}`, mean `z = {sym['mean_z']:.3f}` — consistent "
      f"with the proved arm-swap involution")
    A(f"* **monotonicity in `|e|`: TESTED, not assumed.** "
      f"{mono['n_increasing']}/{mono['n_intervals']} intervals increase, "
      f"{mono['n_significantly_increasing']} of them by more than 3σ. Verdict: "
      f"`{mono['monotone_decreasing_in_abs_e']}`")
    A("")
    A("So the mechanism is confirmed in the expected direction: **reference")
    A("displacement shortens the in-control stopping time**, i.e. raises the")
    A("false-alarm hazard.")
    A("")
    A("### Decomposition check")
    A("")
    A("`ARL_rho = E_pi[A(e)]` was evaluated by averaging an interpolated `A` over")
    A("the observed `e_prev` sample — no binning of `pi`. Because both routes use")
    A("the *same* cycles, the contrast is naturally **paired**:")
    A("")
    A("| `rho` | direct `mean(tau)` | decomposition `E_pi[A]` | paired gap | 95% CI |")
    A("|---|---|---|---|---|")
    for r in rows:
        A(f"| {r['rho']:g} | {r['cycle_arl']:.3f} | "
          f"{r['arl_decomposition']:.3f} | {r['arl_paired_gap']:+.3f} | "
          f"[{r['arl_paired_gap_ci'][0]:+.3f}, {r['arl_paired_gap_ci'][1]:+.3f}] |")
    A("")
    dec = next((x for x in (adv or {}).get("checks", [])
                if x["check"] == "arl_decomposition"), None)
    if dec:
        A(f"Pre-specified tolerance was 3σ combining the paired bootstrap SE with")
        A(f"`A`'s own Monte Carlo error. Result: **{dec['note']}** → "
          f"`{'PASS' if dec['passed'] else 'FAIL'}`.")
    A("")
    return L


def write_report_tail(L, findings, ic, det, adv, acurve, index):
    A = L.append
    rows = sorted(ic["rows"], key=lambda r: r["rho"])
    byrho = {r["rho"]: r for r in rows}
    rbg = findings["policy"]["conservative_rho"]
    dom = findings["domination"]
    decision = findings["decision"]

    A("---")
    A("")
    A("## 8. Detection-delay results")
    A("")
    if det:
        shifts = sorted({r["shift"] for r in det["rows"] if r["shift"] > 0})
        key_rho = [0.0, rbg, findings["policy"]["point_rho"], 0.25,
                   dom["oracle_rho"], 1.0]
        key_rho = sorted(set(round(x, 6) for x in key_rho))
        A("Mean detection delay (observations) for a mean shift applied at a")
        A("cycle boundary. `Delta = 0` is the in-control control arm.")
        A("")
        head = "| `rho` | " + " | ".join(
            (r"in control" if s == 0 else rf"$\Delta$={s:g}")
            for s in [0.0] + shifts) + " |"
        A(head)
        A("|" + "---|" * (len(shifts) + 2))
        for rho in key_rho:
            cells = []
            for s in [0.0] + shifts:
                m = [q for q in det["rows"]
                     if abs(q["rho"] - rho) < 1e-6 and abs(q["shift"] - s) < 1e-12]
                cells.append(f"{m[0]['delay_mean']:.2f}" if m else "—")
            tag = " **←RBG**" if abs(rho - rbg) < 1e-6 else ""
            A(f"| {rho:g}{tag} | " + " | ".join(cells) + " |")
        A("")
        A("**Paired contrasts against full reuse** (criterion C6):")
        A("")
        A("| `Delta` | delay(RBG) | delay(rho=1) | paired difference | 95% CI | C6 threshold | verdict |")
        A("|---|---|---|---|---|---|---|")
        for d in findings["detection"]:
            p = d["paired_rbg_minus_full"]
            A(f"| {d['shift']:g} | {d['delay_rbg']:.3f} | {d['delay_full']:.3f} | "
              f"{p['point']:+.3f} | [{p['ci_low']:+.3f}, {p['ci_high']:+.3f}] | "
              f"< {d['c6_threshold']:+.3f} | "
              f"{'PASS' if d['c6_pass'] else '**FAIL**'} |")
        A("")
        A("**C6 therefore FAILS**, and it is left failed: the criterion was not")
        A("rewritten, and the Stage C decision reflects the failure.")
        A("")
        A("### Why C6 failed, and what the data actually show")
        A("")
        A("C6 compares **raw** delays between two policies whose in-control cycle")
        A("ARLs differ by a factor of 1.7 (RBG 85.2, full reuse 50.0). A detector")
        A("that alarms constantly always posts short \"delays\", change or no")
        A("change. That is not like-for-like — a hazard flagged in §9 of the")
        A("protocol, which I then failed to build the criterion around.")
        A("")
        A("Normalising each policy by its own in-control delay removes the")
        A("baseline alarm rate and measures sensitivity as such:")
        A("")
        shift_list = [d["shift"] for d in findings["detection"]]
        A("| `rho` | " + " | ".join(rf"$\Delta$={s:g}" for s in shift_list) + " |")
        A("|" + "---|" * (len(shift_list) + 1))
        for label, key in (("0 (fresh)", "fresh"),
                           (f"**{rbg:.4f} (RBG)**", "rbg"),
                           ("**1.0 (full reuse)**", "full")):
            cells = []
            for d in findings["detection"]:
                v = d.get("delay_ratio_vs_own_baseline", {}).get(key)
                cells.append(f"{v:.3f}" if v is not None else "—")
            A(f"| {label} | " + " | ".join(cells) + " |")
        A("")
        A("Full reuse sits at **≈1.0 at every shift**: its detection delay is")
        A("almost identical whether or not a change occurred. Its alarms are")
        A("driven by its own reference instability, not by the data — that is the")
        A("*absence* of sensitivity, not its presence. ReBaseGuard's ratios fall")
        A("from 0.93 to 0.41, and at `Delta = 1.5` it is **absolutely faster**")
        A("than full reuse (33.7 vs 44.4) despite a 1.7x longer in-control run.")
        A("")
        A("So the scientific concern C6 was written to capture — *is the stability")
        A("gain bought by blinding the detector?* — is answered decisively **no**,")
        A("in the opposite direction from the criterion's verdict.")
        A("")
        A("The ratio is reported as a **secondary diagnostic only**. It is not a")
        A("gate, it was not pre-specified as one, and it does not rescue C6. Full")
        A("analysis: `level4/stage_c/notes/CRITERION_C6_DIAGNOSIS.md`.")
        A("")
        A("**Detection delay must never be read alone.** The honest object is the")
        A("pair (in-control ARL, delay), which §10 plots. Because `h` is frozen,")
        A("the baselines cannot be re-tuned to a common `ARL_0`, so no")
        A("single-number delay comparison is like-for-like.")
    else:
        A("*(detection campaign not present)*")
    A("")
    A("---")
    A("")
    A("## 9. Sample-efficiency results")
    A("")
    A("Definitions match the implemented protocol exactly:")
    A("")
    A("| ID | Quantity | At `rho = 0` | At RBG | At `rho = 1` |")
    A("|---|---|---|---|---|")
    a0, ar, a1 = byrho[0.0], byrho[rbg], byrho[1.0]
    A(f"| D1 | retained alarm-data weight = `rho` | 0 | **{rbg:.6f}** | 1 |")
    A(f"| D2 | fresh observations per cycle | 1 | 1 | 0 |")
    A(f"| D3 | fresh observations per monitored observation | "
      f"{1/a0['cycle_arl']:.5f} | {1/ar['cycle_arl']:.5f} | 0 |")
    A("")
    A("**Stated limitation, pre-registered in the protocol.** At `m = 1` the")
    A("fresh-sample *count* (D2) is a step function of `rho`: the protocol always")
    A("draws one fresh variate and weights it by `1-rho`. The continuous")
    A("efficiency story therefore lives in the weight D1 and in the amortised D3,")
    A("not in D2. No percentage is quoted here that is not one of D1–D3.")
    A("")
    A("The practical consequence is blunt: **at `m = 1`, ReBaseGuard does not")
    A("reduce the number of fresh observations collected.** It changes how much")
    A("weight the reference places on stopping-selected data. A protocol in which")
    A("the fresh draw could be *skipped* — pre-allocated thinning or sample")
    A("splitting — would make D2 continuous, but both change the frozen")
    A("re-baselining rule and are therefore out of scope (`SC-OPEN2`).")
    A("")
    A("---")
    A("")
    A("## 10. Pareto analysis")
    A("")
    if det and findings["pareto"]:
        for shift, info in sorted(findings["pareto"].items()):
            front = ", ".join(f"{x:g}" for x in info["front_rho"])
            A(f"* `Delta = {shift}`: Pareto front (high ARL, low delay) at "
              f"`rho ∈ {{{front}}}`; ReBaseGuard on front: "
              f"**{info['rbg_on_front']}**; oracle on front: "
              f"{info['oracle_on_front']}")
        A("")
    A("Regimes, using the certified `rho_c` enclosure rather than the point")
    A("estimate alone — the enclosure is wide, so a whole band of `rho` is")
    A("genuinely **undetermined by the certificate**:")
    A("")
    A("| Regime | `rho` range | interpretation |")
    A("|---|---|---|")
    A(f"| certified-stable | `rho < {findings['policy']['rho_c_certified'][0]:.4f}` | "
      f"local stability holds for every `Gamma` the certificate admits |")
    A(f"| undetermined | `{findings['policy']['rho_c_certified'][0]:.4f} <= rho "
      f"<= {findings['policy']['rho_c_certified'][1]:.4f}` | the certificate "
      f"cannot decide; the point estimate places `rho_c` at "
      f"{findings['policy']['rho_c_point']:.4f} |")
    A(f"| certified-unstable | `rho > {findings['policy']['rho_c_certified'][1]:.4f}` | "
      f"the fixed point is locally unstable for every admissible `Gamma` |")
    A("")
    A(f"ReBaseGuard sits at `rho = {rbg:.6f}`, inside **certified-stable**, which")
    A("is exactly what it was designed to guarantee.")
    A("")
    A("---")
    A("")
    A("## 11. Adversarial checks")
    A("")
    if adv:
        A("| Check | Question | Result | Note |")
        A("|---|---|---|---|")
        for c in adv["checks"]:
            A(f"| `{c['check']}` | {c['question']} | "
              f"{'PASS' if c['passed'] else '**FAIL**'} | {c['note']} |")
        A("")
        A(f"**{adv['n_passed']}/{adv['n_checks']}** passed.")
    else:
        A("*(adversarial output not present)*")
    A("")
    A("---")
    A("")
    A("## 12. Negative and null findings")
    A("")
    A("Kept prominent, not buried.")
    A("")
    A("1. **`rho_c` is invisible in the endpoints.** Reference MSE and ARL pass")
    A("   through the certified local stability boundary with no kink. The")
    A("   boundary is real and certified, but it is not an observable transition")
    A("   in stationary summaries (`SC-NULL1`).")
    A(f"2. **ReBaseGuard is not performance-optimal, as pre-registered.** A fixed")
    A(f"   `rho = {dom['oracle_rho']:g}` attains reference MSE "
      f"{dom['mse_oracle']:.5f} against **{dom['mse_rbg']:.5f}** for the policy;")
    p = dom["paired_rbg_minus_oracle"]
    A(f"   the paired difference is {p['point']:+.5f} "
      f"[{p['ci_low']:+.5f}, {p['ci_high']:+.5f}], so the domination is")
    A(f"   statistically clear. This was written into §12 of the protocol")
    A("   **before** the campaign, precisely so it could not later be presented")
    A("   as a discovery or quietly dropped. The policy buys a *certified local")
    A("   stability guarantee*, not optimality — and that is the price.")
    A("3. **At `m = 1` no fresh observations are saved** (§9). The efficiency")
    A("   gain is in reference weight, not in sample count.")
    A("4. **The POINT policy variant is not safe** at the certified upper end of")
    A("   `Gamma`; it is reported only for contrast (`SC-M3`).")
    A("")
    A("---")
    A("")
    A("## 13. Limitations")
    A("")
    A("* The certified guarantee is **local linear stability of the deterministic")
    A("  map at `e = 0`** — nothing more. It is not a statement about the noisy")
    A("  recursion, its invariant law, or its stationary dispersion.")
    A("* Stage B's period-2 theorem is about the deterministic map `F_1`. Stage C")
    A("  neither uses nor extends it; the policy provably cannot see it.")
    A("* Only `m = 1`, `k = 1/2`, `h = 5`, Gaussian innovations, shifts at a cycle")
    A("  boundary, non-adaptive `rho`.")
    A("* The certified `rho_c` enclosure `[0.0372, 0.3420]` is wide because the")
    A("  frozen `Gamma` enclosure is wide. A tighter `Gamma` certificate would")
    A("  immediately allow a less conservative certified policy — currently the")
    A(f"  conservative variant is {findings['policy']['point_rho']/rbg:.2f}x more")
    A("  restrictive than the point-estimate variant.")
    A("* Stationary shapes are empirical. No bimodality, ergodicity or stochastic")
    A("  period-2 claim is made.")
    A("")
    A("---")
    A("")
    A("## 14. Claim ledger")
    A("")
    A("Stage A and Stage B ledgers are untouched. Stage C entries are in")
    A("`level4/reports/STAGE_C_LEDGER.md`.")
    A("")
    A("---")
    A("")
    A("## 15. Final Stage C decision")
    A("")
    A(f"### `{decision}`")
    A("")
    A("| # | Criterion | Result | Detail |")
    A("|---|---|---|---|")
    for c in findings["criteria"]:
        mark = {True: "PASS", False: "**FAIL**", None: "n/a"}[c["passed"]]
        detail = str(c["detail"]).replace("|", r"\|")
        A(f"| {c['id']} | {c['text']} | {mark} | {detail} |")
    A("")
    basis = findings["decision_basis"]
    if basis["failed"]:
        A(f"Failed criteria: {', '.join(basis['failed'])}.")
    if basis["unresolved"]:
        A(f"Evaluated outside this script: {', '.join(basis['unresolved'])} "
          f"(see `reproduce.sh`).")
    A("")
    A("### Reproduction")
    A("")
    A("```bash")
    A("bash level4/stage_c/reproduce.sh")
    A("```")
    A("")
    A("Every campaign cell is checkpointed by config hash, so a rerun reuses")
    A("completed cells and an interrupted run resumes.")
    A("")
    A("### Figures")
    A("")
    for name in sorted(index):
        A(f"* `level4/stage_c/figures/{name}`")
    A("")
    return L


def main() -> int:
    ic = load("incontrol_main.json")
    if ic is None:
        print("missing results/incontrol_main.json", file=sys.stderr)
        return 2
    det = load("detection_main.json")
    adv = load("adversarial.json")
    findings = load("findings.json")
    acurve = load("arl_curve.json")
    if findings is None:
        print("missing results/findings.json -- run run_analysis.py first",
              file=sys.stderr)
        return 2

    index = build_figures(ic, det, findings, acurve)
    L = write_report(findings, ic, det, adv, acurve, index)
    L = write_report_tail(L, findings, ic, det, adv, acurve, index)
    text = "\n".join(L) + "\n"
    LEVEL4_REPORTS.mkdir(parents=True, exist_ok=True)
    (LEVEL4_REPORTS / "STAGE_C_METHOD_REPORT.md").write_text(text)
    (STAGE_C / "reports" / "STAGE_C_METHOD_REPORT.md").write_text(text)

    ledger = build_ledger(findings, ic, det, adv, acurve)
    ledger.write(RESULTS / "ledger_stage_c.json",
                 LEVEL4_REPORTS / "STAGE_C_LEDGER.md",
                 title="ReBaseGuard Level 4 — Stage C Result Ledger")

    manifest = provenance.build_manifest(
        gate="stage-c", stage="report",
        config={"decision": findings["decision"],
                "n_figures": len(index)})
    (RESULTS / "report_manifest.json").write_text(
        json.dumps(manifest, indent=2, default=str))

    print(f"decision : {findings['decision']}")
    print(f"figures  : {len(index)} -> {FIGS}")
    print(f"report   : {LEVEL4_REPORTS / 'STAGE_C_METHOD_REPORT.md'}")
    print(f"ledger   : {LEVEL4_REPORTS / 'STAGE_C_LEDGER.md'} "
          f"({len(ledger.entries())} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
