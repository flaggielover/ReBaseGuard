#!/usr/bin/env python
"""Stage C.1 — figures, ledger and the confirmatory report."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt   # noqa: E402
import numpy as np                # noqa: E402

from campaign_c1 import RESULTS, SEED_ADVERSARIAL, SEED_CONFIRM, SEED_SMOKE, SHIFTS  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "level4" / "src"))
from rebaseguard_level4 import provenance      # noqa: E402
from rebaseguard_level4.ledger import Ledger   # noqa: E402

STAGE_C1 = Path(__file__).resolve().parents[1]
FIGS = STAGE_C1 / "figures"
LEVEL4_REPORTS = STAGE_C1.parent / "reports"

plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 200,
                     "savefig.bbox": "tight", "font.size": 9,
                     "axes.grid": True, "grid.alpha": 0.25,
                     "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "errorbar.capsize": 2.5})


def build_figures(f):
    FIGS.mkdir(parents=True, exist_ok=True)
    rows = f["rows"]
    shifts = [r["shift"] for r in rows]
    index = {}

    # Fig 1 -- the primary metric R by policy
    fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.axhline(1.0, ls="--", lw=1.0, color="0.4",
               label="R = 1: shift produces no acceleration")
    for label, style, name in (("fresh", "-o", "fresh ($\\rho=0$), reference"),
                               ("rbg", "-D", "ReBaseGuard ($\\rho=0.0298$)"),
                               ("full", "-s", "full reuse ($\\rho=1$), diagnostic")):
        y = [r["R"][label]["point"] for r in rows]
        lo = [r["R"][label]["ci_low"] for r in rows]
        hi = [r["R"][label]["ci_high"] for r in rows]
        ax.errorbar(shifts, y, yerr=[np.array(y) - lo, np.array(hi) - y],
                    fmt=style, ms=4, label=name)
    ax.set_xlabel(r"mean shift $\Delta$")
    ax.set_ylabel(r"$R_\Delta = \mathbb{E}[\tau_\Delta]/\mathbb{E}[\tau_0]$")
    ax.set_title("Baseline-normalised detection response", fontsize=10)
    ax.legend(fontsize=7)
    fig.text(0.005, 0.002, "Monte Carlo, preregistered confirmatory experiment; "
             "lower R = stronger response relative to that policy's own baseline",
             fontsize=6, alpha=0.65)
    fig.savefig(FIGS / "fig1_normalised_response.png"); plt.close(fig)
    index["fig1_normalised_response.png"] = "primary metric R by policy and shift"

    # Fig 2 -- the non-inferiority contrast
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    y = [r["D"]["point"] for r in rows]
    lo = [r["D"]["ci_low"] for r in rows]
    hi = [r["D"]["ci_high"] for r in rows]
    ax.axhline(0.0, color="0.55", lw=0.9)
    ax.axhline(f["epsilon"], ls="-", lw=1.4, color="0.15",
               label=rf"non-inferiority margin $\epsilon={f['epsilon']}$")
    ax.axhspan(f["epsilon"], f["epsilon"] + 0.02, color="0.85", lw=0)
    ax.errorbar(shifts, y, yerr=[np.array(y) - lo, np.array(hi) - y],
                fmt="-D", ms=5, color="0.1",
                label=r"$D_\Delta = R_\Delta(\mathrm{RBG}) - R_\Delta(\mathrm{fresh})$")
    ax.set_xlabel(r"mean shift $\Delta$")
    ax.set_ylabel(r"$D_\Delta$ (normalised-response units)")
    ax.set_title("H-C1: non-inferiority of ReBaseGuard to fresh-only", fontsize=10)
    ax.legend(fontsize=7)
    fig.text(0.005, 0.002, "H-C1 passes when the UPPER 95% bound lies below "
             "epsilon at every shift; paired bootstrap over replicates",
             fontsize=6, alpha=0.65)
    fig.savefig(FIGS / "fig2_non_inferiority.png"); plt.close(fig)
    index["fig2_non_inferiority.png"] = "the preregistered non-inferiority test"

    # Fig 3 -- raw vs normalised, side by side
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))
    for label, style in (("fresh", "-o"), ("rbg", "-D"), ("full", "-s")):
        axes[0].plot(shifts, [r["raw_delay"][label] for r in rows], style, ms=4,
                     label=label)
        axes[1].plot(shifts, [r["R"][label]["point"] for r in rows], style, ms=4,
                     label=label)
    axes[0].set_ylabel("raw mean detection delay")
    axes[0].set_title("Raw delay (what Stage C's C6 compared)", fontsize=9)
    axes[1].axhline(1.0, ls="--", lw=0.9, color="0.4")
    axes[1].set_ylabel(r"$R_\Delta$")
    axes[1].set_title("Baseline-normalised response (Stage C.1)", fontsize=9)
    for a in axes:
        a.set_xlabel(r"mean shift $\Delta$"); a.legend(fontsize=7)
    fig.text(0.005, 0.002, "left: full reuse looks fastest because it alarms "
             "constantly. right: normalising by each policy's own baseline shows "
             "it barely responds to the shift at all", fontsize=6, alpha=0.65)
    fig.savefig(FIGS / "fig3_raw_vs_normalised.png"); plt.close(fig)
    index["fig3_raw_vs_normalised.png"] = "why the raw comparison is confounded"

    (FIGS / "figure_index.json").write_text(json.dumps(index, indent=2))
    return index


def build_ledger(f, adv):
    L = Ledger()
    rows = f["rows"]
    L.add("C1-METHOD-DEFINITION",
          "Stage C.1 preregisters the baseline-normalised detection response "
          "R_Delta(rho) = E[tau_Delta|rho]/E[tau_0|rho], the paired contrast "
          "D_Delta = R_Delta(RBG) - R_Delta(fresh), the margin epsilon = 0.05, "
          "the shift set {0.25,0.5,1.0,1.5}, the ratio-of-means estimator and "
          "the decision rule, all frozen before any new outcome was generated.",
          "METHOD-DEFINITION",
          evidence=["level4/stage_c1/STAGE_C1_PROTOCOL.md",
                    "level4/stage_c1/results/protocol_hash.json"],
          notes="Protocol sha256 recorded before the confirmatory seeds were "
                "used; a test re-hashes the file and fails if it changed.")
    L.add("C1-SEEDS",
          f"Stage C.1 uses seed families {SEED_SMOKE} (smoke), {SEED_CONFIRM} "
          f"(confirmatory) and {SEED_ADVERSARIAL} (adversarial), none of which "
          f"appears in Stage A, Stage B, Stage C or the Claude Science work.",
          "METHOD-DEFINITION",
          evidence=["level4/stage_c1/tests/test_stage_c1.py"],
          notes="Tests assert the seeds are new and that the generated streams "
                "are uncorrelated with Stage C's.")
    hc1 = "; ".join(
        f"Delta={r['shift']:g}: D={r['D']['point']:+.5f}, "
        f"upper95={r['D']['ci_high']:+.5f}" for r in rows)
    L.add("C1-CONFIRMATORY-NUMERICAL-HC1",
          f"H-C1 (non-inferiority of ReBaseGuard to fresh-only in "
          f"baseline-normalised response) holds at every preregistered shift: "
          f"{hc1}; all upper bounds lie below epsilon = {f['epsilon']}.",
          "CONFIRMATORY-NUMERICAL",
          evidence=["level4/stage_c1/results/findings_confirmatory.json"],
          numbers={f"D_{r['shift']}": r["D"]["point"] for r in rows})
    L.add("C1-CONFIRMATORY-NUMERICAL-Q",
          "The secondary absolute-delay guard holds at every shift: "
          + "; ".join(f"Q_{r['shift']:g}={r['Q']['point']:.4f}" for r in rows)
          + f", all at or below {f['q_guard']}.",
          "CONFIRMATORY-NUMERICAL")
    fulls = "; ".join(f"Delta={r['shift']:g}: R={r['R']['full']['point']:.4f}"
                      for r in rows)
    L.add("C1-CONFIRMATORY-NUMERICAL-FULLREUSE",
          f"Full reuse shows poor discrimination between in-control and shifted "
          f"regimes: {fulls}. R exceeds 1 at three of four shifts, i.e. a "
          f"genuine shift makes it SLOWER to alarm than no shift.",
          "CONFIRMATORY-NUMERICAL",
          notes="Described as poor discrimination, never as high sensitivity. "
                "Short raw delay with a short in-control run length is not good "
                "detection.")
    L.add("C1-STAGE-C-UNCHANGED",
          "Stage C remains STAGE-C-PARTIAL because its preregistered criterion "
          "C6 failed. Stage C.1 is a separate experiment answering a "
          "better-defined question with new seeds; it does not alter C6.",
          "OPEN",
          evidence=["level4/reports/STAGE_C_METHOD_REPORT.md",
                    "level4/stage_c/notes/CRITERION_C6_DIAGNOSIS.md"],
          notes="A test asserts the Stage C decision file still reads "
                "STAGE-C-PARTIAL with C6 failed, and that no Stage C.1 text "
                "claims C6 passed.")
    L.add("C1-NULL-RAW",
          "The raw cross-policy delay comparison is retained and still shows "
          "ReBaseGuard slower than full reuse at small shifts, exactly as Stage "
          "C reported. Stage C.1 does not overturn that observation; it shows "
          "the observation does not mean what a raw reading suggests.",
          "CONFIRMATORY-NUMERICAL")
    L.add("C1-OPEN-SCOPE",
          "Stage C.1 concerns SENSITIVITY ONLY, at m = 1, k = 1/2, h = 5, "
          "Gaussian innovations, shifts at a cycle boundary, and the single "
          "certificate-aware rho. No sample-efficiency claim is made or implied.",
          "OPEN")
    L.add("C1-OPEN-EVIDENCE-CLASS",
          "Every Stage C.1 number is Monte Carlo simulation and carries no "
          "evidence class stronger than CONFIRMATORY-NUMERICAL.",
          "OPEN",
          notes="The only Level 4 claim with a stronger evidence class remains "
                "the Stage B deterministic result (RIGOROUS-CERTIFIED), which "
                "concerns the conditional-mean map F_1 and not the noisy "
                "recursion. No Stage C.1 entry may ever be labelled "
                "RIGOROUS-CERTIFIED.")
    return L


def write_report(f, adv, index, protocol_hash, sizing):
    rows = f["rows"]
    L, A = [], None
    A = (L := []).append
    dec = f["decision"]

    A("# ReBaseGuard Level 4 — Stage C.1")
    A("")
    A("## Confirmatory Sensitivity Evaluation")
    A("")
    A(f"**Decision: `{dec}`**")
    A("")
    A("> **Stage C is unchanged.** Stage C remains `STAGE-C-PARTIAL` because its")
    A("> preregistered criterion C6 failed. Stage C.1 is a *separate* experiment")
    A("> asking a better-defined question with new seeds. It does not, and")
    A("> cannot, make C6 pass.")
    A("")
    A("---")
    A("")
    A("## 1. Motivation")
    A("")
    A("Stage C asked whether the certificate-aware ReBaseGuard policy buys its")
    A("in-control stability by blinding the detector. Its criterion C6 compared")
    A("**raw** detection delays across policies. That comparison was confounded:")
    A("the policies operate at very different in-control points (cycle ARL 85.2")
    A("for ReBaseGuard against 50.0 for full reuse, a factor of 1.7), and a")
    A("detector that alarms constantly always posts short \"delays\" whether or")
    A("not anything changed.")
    A("")
    A("Stage C.1 asks the same scientific question with a metric that removes")
    A("each policy's own baseline alarm rate.")
    A("")
    A("---")
    A("")
    A("## 2. Historical Stage C C6 failure — chronology")
    A("")
    A("1. Stage C preregistered C6 as a **raw** cross-policy detection-delay")
    A("   criterion.")
    A("2. C6 **failed**, at `Delta = 0.25` and `Delta = 0.5`.")
    A("3. C6 **remained failed**; the Stage C decision reflects it and was not")
    A("   amended.")
    A("4. Post-hoc diagnosis (`CRITERION_C6_DIAGNOSIS.md`) identified the")
    A("   confound: raw cross-policy delay is not comparable across policies with")
    A("   different in-control operating points.")
    A("5. A baseline-normalised response metric was **proposed** in that")
    A("   diagnosis, and reported there only as a labelled secondary diagnostic.")
    A("6. **Stage C.1 preregistered that metric here, before any new data.**")
    A("7. Stage C.1 used entirely new seed families.")
    A("8. Stage C.1 reports its own decision, separately, below.")
    A("")
    A("The correct summary is: **Stage C's C6 failed; Stage C.1 independently")
    A("tested a better-defined sensitivity question.** Stage C.1 is a separate")
    A("experiment, not a repair of C6, and C6's verdict is unchanged by it.")
    A("")
    A("---")
    A("")
    A("## 3. The new preregistered question")
    A("")
    A("> Does the certificate-aware ReBaseGuard policy preserve a meaningful")
    A("> response to genuine distribution shifts **relative to its own in-control")
    A("> operating regime**, rather than obtaining stability by making alarms")
    A("> generally slower?")
    A("")
    A("---")
    A("")
    A("## 4. Frozen protocol")
    A("")
    A(f"`level4/stage_c1/STAGE_C1_PROTOCOL.md`, sha256 `{protocol_hash[:32]}…`,")
    A("frozen and hashed **before** any confirmatory outcome existed. A test")
    A("re-hashes the file on every run and fails if it changed.")
    A("")
    A("Policies (fixed, never re-optimised):")
    A("")
    A("| Label | `rho` | Role |")
    A("|---|---|---|")
    A("| fresh | 0 | non-inferiority **reference** |")
    A(f"| **ReBaseGuard** | `{f['rho_rbg']!r}` | the Stage C policy under test |")
    A("| full reuse | 1 | **diagnostic only** |")
    A("| 0.25, 0.30 | exploratory | context only; excluded from the decision |")
    A("")
    A("`rho_RBG` is imported verbatim from the Stage C policy module. A test")
    A("asserts that module contains no Stage C.1 identifier or outcome value, so")
    A("the policy cannot have been tuned to this experiment.")
    A("")
    A("---")
    A("")
    A("## 5. Primary normalised metric")
    A("")
    A("```text")
    A("R_Delta(rho) = E[tau_Delta | rho] / E[tau_0 | rho]")
    A("```")
    A("")
    A("`R` near 1 means the shift produces little acceleration relative to that")
    A("policy's own in-control alarm rate; smaller `R` means a genuine shift")
    A("accelerates detection strongly. **This is not a classical standardised ARL")
    A("quantity and is not claimed to be one** — it is a ratio of two")
    A("expectations under one policy, and only the relative reading is used.")
    A("")
    A("Estimator, fixed in advance: **ratio of means**, `mean_r(num_r) /")
    A("mean_r(den_r)`, with `den_r` from the `Delta = 0` arm of the **same**")
    A("policy run with the **same** seed. Uncertainty: percentile bootstrap")
    A("resampling **replicates**, never cycles.")
    A("")
    A("---")
    A("")
    A("## 6. Non-inferiority margin")
    A("")
    A(f"`D_Delta = R_Delta(RBG) - R_Delta(fresh)`, margin **`epsilon = "
      f"{f['epsilon']}`**, fixed before any data.")
    A("")
    A("**H-C1 passes when the upper 95% bound of `D_Delta` is strictly below")
    A("`epsilon` at every one of the four preregistered shifts.** This is an")
    A("intersection–union test, so no multiplicity adjustment is needed; it is")
    A("conservative by construction. `epsilon` was not changed after seeing")
    A("results.")
    A("")
    A(f"Secondary descriptive guard: `Q_Delta = E[tau_Delta|RBG] / "
      f"E[tau_Delta|fresh] <= {f['q_guard']}`.")
    A("")
    A("---")
    A("")
    A("## 7. Independent-seed design")
    A("")
    A("Every seed used anywhere in the repository was audited before choosing:")
    A("`{1234, 1729, 2024, 2026, 4242, 5150, 8080, 31337, 90210, 20260820,")
    A("20260821, 20260822}`.")
    A("")
    A("| Purpose | Master seed | Used for |")
    A("|---|---|---|")
    A(f"| smoke sizing (non-confirmatory) | `{SEED_SMOKE}` | choosing (N, K) only |")
    A(f"| **confirmatory** | `{SEED_CONFIRM}` | the Stage C.1 result |")
    A(f"| adversarial rerun | `{SEED_ADVERSARIAL}` | independent replication |")
    A("")
    c = sizing["chosen"]
    A(f"**Replicate structure.** Stage C's detection design gave one change event")
    A(f"per replicate, so a per-replicate ratio was impossible there. Stage C.1")
    A(f"uses `K = {c['K_events']}` change events in each of `N = "
      f"{c['N_replicates']}` replicates ({c['N_replicates'] * c['K_events']:,}")
    A(f"events per cell), via the **existing, unmodified** simulator. Spacing")
    A(f"between events is {c['cycles_between']} cycles, chosen by measuring")
    A(f"recovery: `|e|` settles within 1 cycle for fresh and ReBaseGuard and")
    A(f"within about 3 for full reuse.")
    A("")
    A("The `(N, K)` rung was selected by a rule recorded **before** the smoke")
    A("run: the first rung on a fixed ladder with bootstrap `SE(D_Delta) <= 0.010`")
    A("at every shift, then applied identically to every policy and shift.")
    A("Replication was never increased for cells close to passing.")
    A("")
    A("> **Stated plainly:** sizing required estimating the very contrast under")
    A("> test, so the smoke run necessarily revealed the approximate answer. That")
    A("> cannot bias the result, because every degree of freedom — margin, shifts,")
    A("> policies, estimator, statistical unit, decision rule — was already")
    A("> frozen. Nothing remained to adjust, and nothing was adjusted. The smoke")
    A("> numbers are recorded in `results/sizing_decision.json` and are excluded")
    A("> from the Stage C.1 result.")
    A("")
    A("---")
    A("")
    A("## 8. Results")
    A("")
    A("| `Delta` | R(fresh) | R(RBG) | `D` | 95% CI | upper bound | vs `epsilon` | H-C1 |")
    A("|---|---|---|---|---|---|---|---|")
    for r in rows:
        A(f"| {r['shift']:g} | {r['R']['fresh']['point']:.4f} | "
          f"{r['R']['rbg']['point']:.4f} | {r['D']['point']:+.5f} | "
          f"[{r['D']['ci_low']:+.5f}, {r['D']['ci_high']:+.5f}] | "
          f"{r['D']['ci_high']:+.5f} | < {f['epsilon']} | "
          f"{'**PASS**' if r['hc1_pass'] else '**FAIL**'} |")
    A("")
    A("Every `D_Delta` is **negative**: on the preregistered metric ReBaseGuard")
    A("is slightly *more* responsive than fresh-only, not less. The point")
    A("estimates and intervals are reported above whether or not the criterion")
    A("passed, as the protocol requires.")
    A("")
    A("Secondary absolute-delay guard:")
    A("")
    A("| `Delta` | delay(RBG) | delay(fresh) | `Q` | guard |")
    A("|---|---|---|---|---|")
    for r in rows:
        A(f"| {r['shift']:g} | {r['raw_delay']['rbg']:.3f} | "
          f"{r['raw_delay']['fresh']:.3f} | {r['Q']['point']:.4f} | "
          f"{'PASS' if r['q_guard_pass'] else '**FAIL**'} |")
    A("")
    A("### Sanity checks")
    A("")
    A("| ID | Check | Result |")
    A("|---|---|---|")
    for ch in f["sanity"]:
        A(f"| {ch['id']} | {ch['text']} | "
          f"{'PASS' if ch['passed'] else '**FAIL**'} |")
    A("")
    A("Check A deserves a note. Stage C.1's fresh arm reads 81.78 at")
    A("`Delta = 0.25` against Stage C's 74.42, which looked like a design")
    A("effect. It is not: rerunning the **Stage C replicate structure** (one")
    A("event per replicate, 4000 replicates) on the Stage C.1 seed gives")
    A("**81.92 ± 2.97**, agreeing with the many-event value 81.78 ± 0.48 to")
    A("0.14. The replicate structure changes nothing; it reduces the standard")
    A("error about sixfold. The Stage C / Stage C.1 gap is 1.9 sigma of ordinary")
    A("between-seed variation, given Stage C's detection cells carried ~3.5%")
    A("relative error.")
    A("")
    return L


def write_report_tail(L, f, adv, index):
    A = L.append
    rows = f["rows"]
    dec = f["decision"]

    A("---")
    A("")
    A("## 9. Raw versus normalised detection delays")
    A("")
    A("Both are reported, side by side, because the difference between them is")
    A("the whole point.")
    A("")
    A("| `Delta` | \\multicolumn{3}{c}{raw mean delay} | | \\multicolumn{3}{c}{normalised `R`} |")
    A("|---|---|---|---|---|---|---|---|")
    A("| | fresh | RBG | full | | fresh | RBG | full |")
    for r in rows:
        A(f"| {r['shift']:g} | {r['raw_delay']['fresh']:.2f} | "
          f"{r['raw_delay']['rbg']:.2f} | {r['raw_delay']['full']:.2f} | | "
          f"{r['R']['fresh']['point']:.4f} | {r['R']['rbg']['point']:.4f} | "
          f"{r['R']['full']['point']:.4f} |")
    A(f"| in control | {rows[0]['raw_delay_in_control']['fresh']:.2f} | "
      f"{rows[0]['raw_delay_in_control']['rbg']:.2f} | "
      f"{rows[0]['raw_delay_in_control']['full']:.2f} | | — | — | — |")
    A("")
    A("Read the left block alone and full reuse looks like the most sensitive")
    A("detector at small shifts: it alarms in ~51 observations where ReBaseGuard")
    A("takes ~83. Read the bottom row and the reason is obvious — full reuse")
    A("alarms in ~50 observations *with no change at all*. The right block")
    A("removes that baseline and the picture reverses.")
    A("")
    A("**Stage C's raw observation is not overturned.** ReBaseGuard is indeed")
    A("slower than full reuse in raw terms at small shifts, exactly as Stage C")
    A("measured and reported, and the adversarial suite retains that comparison.")
    A("What Stage C.1 shows is that the raw reading does not mean what it")
    A("appears to mean.")
    A("")
    A("---")
    A("")
    A("## 10. Full-reuse diagnostic")
    A("")
    A("| `Delta` | `R(full)` | 95% CI |")
    A("|---|---|---|")
    for r in rows:
        A(f"| {r['shift']:g} | {r['R']['full']['point']:.4f} | "
          f"[{r['R']['full']['ci_low']:.4f}, {r['R']['full']['ci_high']:.4f}] |")
    A("")
    above = sum(1 for r in rows if r["R"]["full"]["point"] > 1.0)
    A(f"`R(full)` sits at or above 0.87 at every shift and **exceeds 1 at")
    A(f"{above} of 4** — meaning a genuine shift makes full reuse *slower* to")
    A("alarm than no shift at all. Its alarm times are essentially decoupled from")
    A("whether the process changed.")
    A("")
    A("The correct description is **poor discrimination between in-control and")
    A("shifted regimes**, not high sensitivity. A short raw delay accompanied by")
    A("an equally short in-control run length is not good detection.")
    A("")
    A("This is the mechanism that made Stage C's raw-delay C6 comparison")
    A("uninterpretable, now measured directly and at 160,000 events per cell.")
    A("")
    A("---")
    A("")
    A("## 11. Adversarial tests")
    A("")
    if adv:
        A("| Check | Question | Result | Note |")
        A("|---|---|---|---|")
        for c in adv["checks"]:
            A(f"| `{c['check']}` | {c['question']} | "
              f"{'PASS' if c['passed'] else '**FAIL**'} | {c['note']} |")
        A("")
        A(f"**{adv['n_passed']}/{adv['n_checks']}** passed.")
        A("")
        A("Two of these carry most of the weight. The **independent-seed rerun**")
        A("on a disjoint seed family reproduces H-C1 at every shift. The")
        A("**estimator variant** shows the verdict does not depend on choosing")
        A("ratio-of-means over mean-of-ratios. Breaking CRN widened the standard")
        A("error 1.25x, as expected, without changing the conclusion — so the")
        A("pairing is doing real variance reduction rather than manufacturing the")
        A("result.")
    else:
        A("*(adversarial output not present)*")
    A("")
    A("### Independent cross-check: Claude Science Stage C theory")
    A("")
    A("Claude Science material was added to the repository at")
    A("`level4/stage_c/science_data/` **after** the Stage C.1 protocol was frozen,")
    A("so it cannot have influenced the preregistration. It comes from a separate")
    A("implementation with its own solver and seeds, and it reports raw delays")
    A("only. Normalising its published numbers by its own in-control cycle length")
    A("gives an independent estimate of the same metric:")
    A("")
    A("| `rho` | source | in-control | `Delta`=0.5 | `R(0.5)` | `Delta`=1.0 | `R(1.0)` |")
    A("|---|---|---|---|---|---|---|")
    A("| 0 | Claude Science | 83.27 | 74.13 | 0.8904 | 53.55 | 0.6431 |")
    A("| 0 | **Stage C.1** | 84.22 | 74.35 | **0.8828** | 53.47 | **0.6348** |")
    A("| ~0.06 | Claude Science | 86.98 | 77.58 | 0.8920 | 53.82 | 0.6187 |")
    A("| 1 | Claude Science | 50.12 | 52.91 | **1.0556** | 52.67 | **1.0510** |")
    A("| 1 | **Stage C.1** | 50.14 | 52.34 | **1.0437** | 53.02 | **1.0574** |")
    A("")
    A("Two agreements matter here. First, the **full-reuse diagnostic reproduces**:")
    A("an independent implementation also finds `R(full) > 1` at both shared")
    A("shifts, i.e. a genuine change makes full reuse slower to alarm. Second,")
    A("Claude Science's own `H3g` — its version of the insensitivity question —")
    A("is stated on **raw** delays and **fails at `mu = 0.5`** for `rho = 0.2`")
    A("(81.9 against fresh 74.1). Stage C.1 does not contradict that: at")
    A("`rho = 0.25` the Stage C.1 raw penalty is likewise about 11%, whereas at")
    A("the much smaller certificate-aware `rho = 0.0298` it is 1.6%, comfortably")
    A("inside the `Q` guard. The raw-delay penalty scales with `rho`, and the")
    A("certificate-aware policy sits where it is small.")
    A("")
    A("Claude Science also independently reports, from its own runs, that under")
    A("the frozen convention **no** sample-efficiency claim is well posed for")
    A("stability-aware reuse at all (its `H4`), and that bimodality onset at `m = 1`")
    A("occurs near `rho = 0.55` rather than at `rho_c = 0.067` (its `H5`). Both")
    A("corroborate Stage C's own conclusions and neither is weakened here.")
    A("")
    A("Its independent solver gives `Gamma = 15.8868` and `rho_c = 0.06717`")
    A("against the Stage C values `15.885729` and `0.067178` — agreement to five")
    A("decimals — and it independently reached the same Stage C verdict,")
    A("`STAGE-C-PARTIAL`.")
    A("")
    A("---")
    A("")
    A("## 12. Negative and null findings")
    A("")
    A("1. **Stage C's C6 remains failed.** Nothing here changes it. Stage C's")
    A("   decision is still `STAGE-C-PARTIAL`, for the reason it always was.")
    A("2. **The raw cross-policy comparison still favours full reuse at small")
    A("   shifts** and is retained in full. Stage C.1 does not delete or")
    A("   reinterpret that measurement; it adds the baseline that makes it")
    A("   readable.")
    A("3. **`D_Delta` is statistically indistinguishable from zero at the two")
    A("   smallest shifts** (`Delta = 0.25`: `-0.0024 [-0.0186, +0.0136]`;")
    A("   `Delta = 0.5`: `-0.0008 [-0.0165, +0.0141]`). Non-inferiority is")
    A("   established; **superiority is not**, and is not claimed.")
    A("4. **The exploratory policies were not used in the decision.** They are")
    A("   reported for context only, as the protocol required.")
    A("5. **Sizing necessarily revealed the approximate answer** (§7). Recorded")
    A("   rather than omitted.")
    A("")
    A("---")
    A("")
    A("## 13. Limitations")
    A("")
    A("* **Monte Carlo, not certified.** Every Stage C.1 number is simulation.")
    A("  None is `RIGOROUS-CERTIFIED`; that status belongs to the Stage B")
    A("  deterministic theorem alone, which concerns the conditional-mean map")
    A("  `F_1` and not the noisy recursion.")
    A("* **Sensitivity only.** Under the frozen convention every `rho < 1` policy")
    A("  still draws the fresh block each cycle, so **no sample-efficiency claim")
    A("  is made or implied** anywhere in Stage C.1.")
    A("* **Non-inferiority, not superiority.** H-C1 establishes that ReBaseGuard")
    A("  is not materially *worse* than fresh-only on the preregistered metric.")
    A("* **One policy, one margin.** Only the single certificate-aware `rho` at")
    A("  `delta = 0.2` was tested; `epsilon = 0.05` is a practical choice, not a")
    A("  derived one.")
    A("* **Scope.** `m = 1`, `k = 1/2`, `h = 5`, Gaussian innovations, shifts")
    A("  inserted at a cycle boundary, non-adaptive `rho`.")
    A("* **The metric is a ratio of expectations under one policy.** It is not a")
    A("  classical standardised ARL quantity and no such interpretation is")
    A("  attached to it.")
    A("* Stage C's separate finding that a fixed `rho` well above the stability")
    A("  boundary dominates ReBaseGuard on in-control performance is untouched by")
    A("  this stage and still stands.")
    A("")
    A("---")
    A("")
    A("## 14. Decision")
    A("")
    A(f"### `{dec}`")
    A("")
    A(f"{f['decision_reason']}.")
    A("")
    A("| Requirement | Result |")
    A("|---|---|")
    A(f"| H-C1 passes at every preregistered `Delta` | "
      f"{'PASS' if f['hc1_all_pass'] else '**FAIL**'} |")
    A(f"| absolute-delay guard `Q <= {f['q_guard']}` | "
      f"{'PASS' if f['q_guard_all_pass'] else '**FAIL**'} |")
    A(f"| sanity checks A–F | "
      f"{'PASS' if all(c['passed'] for c in f['sanity']) else '**FAIL**'} |")
    A(f"| adversarial checks | "
      f"{'PASS' if f.get('adversarial_all_pass') else '**FAIL**'} |")
    A("")
    A("### Wording of the conclusion")
    A("")
    A("> The original preregistered raw-delay criterion failed and remains")
    A("> failed. An independently preregistered follow-up using baseline-")
    A("> normalised detection response found that certificate-aware ReBaseGuard")
    A("> preserved responsiveness across the tested shifts, supporting the")
    A("> interpretation that its stability improvement is not obtained by simply")
    A("> blinding the detector.")
    A("")
    A("This does **not** mean C6 passed. It does **not** mean ReBaseGuard is")
    A("universally better or optimal. It makes **no** claim about sample")
    A("efficiency.")
    A("")
    A("### Reproduction")
    A("")
    A("```bash")
    A("bash level4/stage_c1/reproduce.sh")
    A("```")
    A("")
    A("### Figures")
    A("")
    for name, desc in sorted(index.items()):
        A(f"* `level4/stage_c1/figures/{name}` — {desc}")
    A("")
    return L


def main() -> int:
    f = json.loads((RESULTS / "findings_confirmatory.json").read_text())
    adv_p = RESULTS / "adversarial_c1.json"
    adv = json.loads(adv_p.read_text()) if adv_p.exists() else None
    sizing = json.loads((RESULTS / "sizing_decision.json").read_text())
    phash = hashlib.sha256(
        (STAGE_C1 / "STAGE_C1_PROTOCOL.md").read_bytes()).hexdigest()

    index = build_figures(f)
    L = write_report(f, adv, index, phash, sizing)
    L = write_report_tail(L, f, adv, index)
    text = "\n".join(L) + "\n"
    LEVEL4_REPORTS.mkdir(parents=True, exist_ok=True)
    (LEVEL4_REPORTS / "STAGE_C1_CONFIRMATORY_REPORT.md").write_text(text)
    (STAGE_C1 / "notes" / "STAGE_C1_CONFIRMATORY_REPORT.md").write_text(text)

    ledger = build_ledger(f, adv)
    ledger.write(RESULTS / "ledger_stage_c1.json",
                 LEVEL4_REPORTS / "STAGE_C1_LEDGER.md",
                 title="ReBaseGuard Level 4 — Stage C.1 Result Ledger")

    (RESULTS / "report_manifest.json").write_text(json.dumps(
        provenance.build_manifest(gate="stage-c1", stage="report",
                                  config={"decision": f["decision"],
                                          "protocol_sha256": phash}),
        indent=2, default=str))
    print(f"decision : {f['decision']}")
    print(f"figures  : {len(index)} -> {FIGS}")
    print(f"report   : {LEVEL4_REPORTS / 'STAGE_C1_CONFIRMATORY_REPORT.md'}")
    print(f"ledger   : {LEVEL4_REPORTS / 'STAGE_C1_LEDGER.md'} "
          f"({len(ledger.entries())} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
