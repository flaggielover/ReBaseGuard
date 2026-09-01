# P8 definition audit — what Priority 8 is, from repository authority alone

**Namespace:** `level4/closure_proofs/p8_model_class_robustness/`
**Anchor commit:** `ffe23a63181e2ff11380768d3c73980de80f94fb` (P6 authoritative closure
checkpoint; `HEAD == origin/main`, worktree clean at record time).
**Protected-tree manifest:** `results/protected_tree_manifest_pre.json`.

This file was written **before** any P8 implementation, theory or computation.
Nothing here is inferred from the campaign prompt where the repository speaks;
where the two disagree, the repository wins and the disagreement is recorded in
§5.

---

## 1. Search procedure (reproducible)

```bash
grep -rIn --exclude-dir=.git -E "Priority 8|PRIORITY 8|\bP8\b|priority_8|priority8" .
grep -rIn --exclude-dir=.git -E "robustness matrix|distribution-family|drift-pattern|detector-family" .
```

Both were run at the anchor commit over the whole tree. Every hit is classified
below. There is **no** `P8_*` directory, no `P8` protocol, no `P8` gate file, no
`P8` config, and no `P8` entry in `README.md`'s Level-4 status table. The
searches are exhaustive over tracked text.

---

## 2. FROZEN REQUIREMENT — statements that define P8

These are the only repository statements that *define* Priority 8. All four are
in `CLOSED` P7 artifacts or in the P6 pre-design's frozen exclusion ledger.

| # | source (file:line) | literal statement |
|---|---|---|
| F1 | `p7_statistical_consequences/EXPERIMENT_DESIGN.md:21` | table row: `detector-family / distribution-family / drift-pattern robustness matrix` → owner **`P8`** |
| F2 | `p7_statistical_consequences/CLOSURE_REPORT.md:102` | handoff: "**P8** — everything outside the two frozen Gaussian specialisations." |
| F3 | `p7_statistical_consequences/README.md:56` | P7 "does **not** run the detector-family, distribution-family or drift-pattern robustness matrix (P8)" |
| F4 | `p6_safe_rebaselining_predesign/DEPENDENCY_LEDGER.md:155` (exclusion `X5`) | "Non-Gaussian innovations, contamination, other detectors, other reuse conventions — that is **P8**" |

Corroborating (same content, weaker phrasing, not independent):

| # | source | statement |
|---|---|---|
| F5 | `p7/THEORY_BRIDGE.md:224` | "Nothing outside the two frozen Gaussian specialisations and `m in {1,2,3,5}`. **P8 handoff.**" |
| F6 | `p7/P6_HANDOFF.md:106` | "No robustness beyond frozen Gaussian CUSUM/SR and `m in {1,2,3,5}` — that is P8's." |
| F7 | `p6_predesign/FAILURE_MODE_REGISTER.md:183` (`N1`) | "The frozen Gaussian core is itself unrepresentative of any real process … only P8 can address it" |
| F8 | `p6_predesign/P6_METHOD_CANDIDATES.md:124,219` | "Robustness to *non-Gaussian innovations* is **P8**"; "non-Gaussian robustness, contamination defence, alternative detectors → `X5` (P8)" |
| F9 | `p6/LIMITATIONS.md` L1 | "Non-Gaussian innovations, contamination, other detectors, other reuse conventions and other cost models are **P8** (`X5`)" |

### Synthesised frozen P8 question

> **Does the recursive re-baselining structure established for the two frozen
> Gaussian specialisations — the stopped-selection gain `GammaTilde`, the local
> stability boundary `rho_c` (P3), and the operational monitoring degradation
> (P7) — survive outside that specialisation, across innovation-distribution
> families, detector families, reuse windows `m`, reuse conventions, and drift
> patterns?**

Every axis in that sentence is named in F1–F4 verbatim. Nothing else is.

---

## 3. HISTORICAL EXPECTATION — what earlier priorities predicted about P8

None of the following are requirements. They are recorded so that P8's results
can be checked against what the campaign expected.

| # | source | expectation |
|---|---|---|
| H1 | `p7/EVIDENCE_BOUNDARY.md` | P7 carries no rank 1–3 evidence; a downstream robustness priority is not expected to supply one either |
| H2 | `p6_predesign/FAILURE_MODE_REGISTER.md` `N1` | the Gaussian core "is itself unrepresentative of any real process" — i.e. P8 is expected to be the priority that *tests external validity*, not one that *builds a method* |
| H3 | `location_family/FINAL_REPORT.md` §A | P4's own verdict already warns the location-family result "is not distribution-free, universal, detector-independent, or a class-wide instability certificate" — P8 must not close that gap by assertion |
| H4 | `stage_d/results/d3_nongaussian.json` | Stage D already calibrated **CUSUM** thresholds for six innovation families to `ARL_0 = 465.50394`; a P8 distribution matrix is expected to reuse those, not re-derive them |
| H5 | `p7/INDEPENDENT_ADJUDICATION.md:285` | P7's adjudicator lists "detector/distribution robustness matrix" among the things P7 does not deliver — an explicit statement that the matrix is still owed |

---

## 4. OPTIONAL EXTENSION — allowed but not required by any frozen statement

| # | item | why optional |
|---|---|---|
| O1 | Adding a **third** detector family (e.g. EWMA) | F4 says "other detectors" without naming any; only CUSUM and SR are closed (P1/P2), so a third family would have no closed derivative theorem behind it and could only be reported as `EMPIRICAL_ONLY`. **P8 declines this** (see §6). |
| O2 | Non-step drift patterns (ramp, drift-in, transient) | F1 names "drift-pattern" as an axis; no repository artifact specifies which patterns |
| O3 | A new theorem generalising the frozen derivative identity to convention-A windows for general `f` | not required anywhere; P4's abstract theorem is `m=1` raw-reuse only (`location_family/PROTOCOL.md` §1) |
| O4 | Formal (Lean/Arb) layer | no P8 statement requires it; P4's Lean was explicitly **NOT AUTHORIZED** after its numerical gate failed, so P8 starting a formal layer would be out of order |
| O5 | Cost models other than the step-shaped fresh-sample cost | named in `p6/LIMITATIONS.md` L1 but not in the P7 handoff triple; it is a P6-method axis, not a model-class axis |

---

## 5. UNSUPPORTED ASSUMPTION — things that look like P8 but are not

| # | assumption | why it is unsupported |
|---|---|---|
| U1 | **"`P8` means RMS/ARL co-optimality."** | `p6_predesign/DEPENDENCY_LEDGER.md:116`, `p6/P5_TO_P6_DEPENDENCY_AUDIT.md:77` and `p6/CODEX_HANDOFF.md:69` all use `P8` as a **premise label inside P5's numbered premise ledger** (`P1`…`P15` are *premises*, not priorities). That `P8` is the claim "`argmin_rho RMS` and `argmax_rho ARL_0` coincide". It has nothing to do with Priority 8. P6 already re-verified it and reported a reproduction failure (2 of 8 cells). **P8-the-priority must not inherit or re-litigate it.** This collision is the single most likely way a reader mis-scopes this campaign. |
| U2 | P8 is an algorithm priority | no statement asks P8 for a method. F1–F4 ask for a *matrix*. P6 owns the algorithm. |
| U3 | P8 must produce a certified/formal layer | see O4 |
| U4 | P8 may re-open, repair or supersede P4 or P5 | forbidden by campaign policy and by `p7/README.md` ("Nothing in … the `PARTIAL` `p4_theory_generalization` is read-write from here") |
| U5 | P8 may treat Stage-D `STAGE-D-PARTIAL` numbers as closed inputs | Stage D is `PARTIAL`; its calibrated thresholds are reusable as *frozen conventions*, but its `Gamma_psi` values are not closed premises |
| U6 | P8 establishes "universal detector transfer" | F4 says "other detectors" is P8's *territory*, not that P8 will find transfer. P6's limitation ledger and this prompt both forbid claiming transfer without evidence |

---

## 6. Scope P8 adopts (declared before any result)

**In scope (from F1–F4):**

1. **Distribution family.** The six frozen Stage-D D3 innovation families:
   `gaussian`, `t10`, `t5`, `t3`, `contam0.05`, `contam0.1`, at the frozen
   `ARL_0 = 465.50394` operating point.
2. **Detector family.** The two closed families only: frozen two-sided CUSUM
   (`k=1/2`) and frozen symmetric two-chart SR. Non-Gaussian SR thresholds do
   not exist in the repository and must be calibrated by P8 (§7 below).
3. **Window `m`.** `{1, 2, 3, 5}` (the windows P3 supports) extended to
   `{10, 20}` for the window law only, labelled as extrapolation beyond P3.
4. **Reuse convention.** Convention A (truncated window, `w = min(m, tau)`,
   denominator `w`) as primary; convention B (fixed-`m` denominator) as the
   declared alternative convention, reported side by side and never merged.
5. **Drift pattern.** Step shift (the P7 pattern) plus a linear ramp, in
   control and out of control.

**Out of scope, declared:**

* O1 (third detector family) — **declined**: no closed derivative theorem exists
  for any third family, so any result would be unanchored.
* Any P4/P5 repair, any P6 method change, any re-optimisation of `rho`.
* Any cost model, any policy design, any novelty claim about the *method*.
* Real data. P8 is a model-class study inside simulation.

---

## 7. The one new convention P8 must introduce, and why

`stage_d/results/d3_nongaussian.json` supplies **CUSUM** thresholds `h_f`
calibrated to `ARL_0 = 465.50394` for all six families. It supplies **no** SR
thresholds for non-Gaussian families: the frozen SR threshold
`A = 520.886133602749` is Gaussian-only
(`stage_d/results/calibration_d1.json`).

A detector-family × distribution-family matrix is meaningless if the two
detectors are compared at different false-alarm rates. P8 therefore calibrates
`A_f` per family to the **same** frozen target `ARL_0 = 465.50394`, using the
same bisection procedure Stage D used for CUSUM, with the P8 addressable
primitive field and a fully recorded trace. This is declared here, before any
result, as P8's only new calibration. It is reported as
`NEW_P8_CALIBRATION`, never as an inherited frozen constant.

---

## 8. Conflicts between this prompt and repository authority

| item | prompt | repository | resolution |
|---|---|---|---|
| meaning of "P8" | "the P8 research campaign" (Priority 8) | `P8` is *also* P5's premise label for RMS/ARL co-optimality | repository wins on both readings: they are different objects. P8-the-priority is defined by F1–F4; the premise label is out of scope (U1) |
| P6 status | `P6 = CLOSED` | `README.md:34` still says "P6 has a pre-design directory only" | the README is **stale** relative to `HEAD`; the P6 artifact tree and its repair reports are the authority. P8 does **not** edit `README.md` |
| expected P8 gates | "If historical P8 gates already exist, preserve them literally" | none exist | P8 preregisters its own gates in `CLOSURE_GATES.md`, marked `P8_ORIGINAL`, and states that no historical gate was overwritten |
