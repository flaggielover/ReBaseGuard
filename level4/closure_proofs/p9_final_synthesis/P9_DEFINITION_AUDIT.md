# P9 definition audit — what Priority 9 is, from repository authority alone

**Namespace:** `level4/closure_proofs/p9_final_synthesis/`
**Worktree:** `/Users/suzhe/ReBaseGuard-p9`, branch `p9-research`
**Anchor commit:** `ffe23a63181e2ff11380768d3c73980de80f94fb` (P6R2b result
checkpoint; `main` HEAD at campaign start, `HEAD == origin/main`).
**Protected-tree manifest:** `results/protected_tree_manifest_pre.json`
(2217 files).

This file was written **before** any P9 synthesis, theory or computation.
Where the campaign prompt and the repository disagree, the repository wins and
the disagreement is recorded in §6.

---

## 1. Search procedure (reproducible)

Run at the anchor commit over the whole tree:

```bash
grep -rIn --exclude-dir=.git --exclude-dir=.pytest_cache -E "\bP9\b|Priority 9|PRIORITY 9|priority_9|priority9" .
grep -rIn --exclude-dir=.git -E "\bP1[01]\b|Priority 10" .
grep -rIn --exclude-dir=.git -iE "final synthesis|synthesis priority|priority map|priority roadmap|remaining priorities|next priority" --include="*.md" .
grep -rIn --exclude-dir=.git -E "after P8|beyond P8|post-P8|P8\+" .
```

Counts at the anchor commit:

| query | total hits | hits that refer to **Priority 9** |
|---|---:|---:|
| `\bP9\b` | 11 | **0** |
| `Priority 9` / `PRIORITY 9` / `priority_9` / `priority9` | 0 | 0 |
| `after P8` / `beyond P8` / `post-P8` | 0 | 0 |
| `\bP10\b`, `\bP11\b` | 5 | 0 |

---

## 2. THE CENTRAL FINDING — there is no frozen P9

> **At the anchor commit, the repository contained zero statements that define,
> scope, name, schedule, or assign deliverables to a Level-4 Priority 9.**

> **UPDATE (post-P8 adjudication).** This remained true throughout P9's
> P8-independent work. It is now *partly* superseded: the authoritative
> `p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md` §16, delivered during
> this campaign, is titled **"Exact P9 handoff boundary"** and constrains what
> P9 may use from P8. It is a genuine repository statement addressed to P9 and
> is honoured in full (`P8_TO_P9_RECONCILIATION.md` §5). It still does **not**
> define P9's scientific question, its gates, or its deliverables — it bounds
> one input. The classification below therefore stands, with §16 added as an
> `AUTHORITATIVE_DEPENDENCY`, not a `FROZEN_REQUIREMENT`.

There is no `p9_*` directory, no P9 protocol, no P9 gate file, no P9 config, no
P9 row in `README.md`'s Level-4 status table, and no forward handoff from any
`CLOSED` priority that names a ninth priority. P7 — the priority that
*did* create Priority 8 by explicit handoff (`p7/CLOSURE_REPORT.md:102`,
`p7/README.md:56`, `p7/EXPERIMENT_DESIGN.md:21`) — names **no** successor to
P8. P8's own `CODEX_HANDOFF.md` and `LIMITATIONS.md` list owed work but assign
it to no priority number.

This is a **stronger negative than P8 faced.** P8's definition audit found four
frozen statements (F1–F4) that literally defined Priority 8. P9 has none. The
contrast is the single most important fact in this document.

### 2.1 Consequence for authority

Because no repository statement defines P9, the instruction "if this prompt's
expectations conflict with repository-frozen P9 definitions, repository
authority wins" **cannot fire**: there is nothing to conflict with. The prompt's
own fallback therefore governs the scope:

> §3: "Unless repository authority specifies otherwise, treat P9 as the final
> Level-4 synthesis/closure priority."

Every scope statement in §3–§28 of the prompt is accordingly classified
`PROMPT_DERIVED`, **not** `FROZEN_REQUIREMENT`. P9 is a
**prompt-constituted synthesis priority over a repository-constituted evidence
base.** That asymmetry is declared here, before results, and is restated in
`CODEX_HANDOFF.md`. An adjudicator who rejects the prompt's authority to
constitute a priority should read P9 as a *synthesis audit of P1–P8* rather
than as a Level-4 closure step; the artifacts are written so that reading
survives.

### 2.2 What P9 must therefore **not** do

Because P9's scope is prompt-derived, it carries no frozen mandate to change
anything. P9 therefore:

* declares **no** priority's status other than its own;
* edits **no** artifact outside `p9_final_synthesis/`;
* introduces **no** new scientific premise; every claim it carries is traced to
  an artifact that already existed at the anchor commit;
* creates no obligation on any future priority.

---

## 3. UNSUPPORTED — the `P9` label collision (the U1-analogue)

All 11 `\bP9\b` hits are the **same collision P8 recorded as its `U1`**, and it
must be recorded again because for P9 it is total: *every* occurrence is the
wrong object.

| # | assumption | why it is unsupported |
|---|---|---|
| **U1** | **"`P9` means the `m`-monotonicity result."** | All 11 hits (`p6_safe_rebaselining_predesign/DEPENDENCY_LEDGER.md:117,157,158`, `.../OBSERVABILITY_AUDIT.md:150`, `.../P6_METHOD_CANDIDATES.md:28`, `.../P5_ADJUDICATION_CONTINGENCIES.md:53`, `.../FAILURE_MODE_REGISTER.md:168,170`, `p6_safe_rebaselining/RESULTS.md:274`, `.../P5_TO_P6_DEPENDENCY_AUDIT.md:78,114`) use `P9` as a **premise label inside P5's numbered premise ledger** (`P1`…`P15` are *premises*, not priorities). That `P9` is the claim "increasing `m` lowers `sup|R|`, lowers `S(0)`, lowers stationary RMS, raises ARL, raises `rho_c`, lowers `rho*`; measured only for `m<=5`". It has nothing to do with Priority 9. Its own ledger rates it `NUMERICAL EVIDENCE` and flags cross-tension `X8` against premise `S14`. **Priority 9 must not inherit, re-litigate, or import it.** |
| U2 | "P9 inherits P8's `PARTIAL_CANDIDATE` gate list" | those gates are `P8_ORIGINAL` and scope-bound to the model-class matrix; they are not synthesis gates and are not authoritative until Codex adjudicates them |
| U3 | "P9 may repair, reopen or supersede P4, P5, P6 or P8" | forbidden by prompt §0 and by standing campaign policy (`p7/README.md`: the `PARTIAL` `p4_theory_generalization` "is read-write from here" — negated); P9 owns no repair mandate |
| U4 | "P9 may declare the Level-4 campaign closed" | `level4/final_level4_closure/FINAL_REPORT.md:164` already says `CURRENT LEVEL-4 CAMPAIGN: CLOSED` for the *frozen* Level-4 campaign, while `level4/reports/LEVEL_4_CURRENT_LEDGER.md:19` keeps `L4R-11` at **FAIL**. Both are historical and neither is P9's to move. |
| U5 | "absence of a P9 definition means P9 is unconstrained" | the opposite: with no frozen mandate, P9's only defensible output is one that is *checkable against artifacts that already exist*. Novel premises are the failure mode, not the goal. |

---

## 4. AUTHORITATIVE DEPENDENCY — the evidence base P9 synthesises

These are not P9 definitions; they are the inputs whose status P9 must carry
without inflation. Status is as recorded in the repository at the anchor commit.

| priority | repository-authoritative status | source of that status |
|---|---|---|
| P1 | `CLOSED` | `m_gt_1_priority1/CLOSURE_REPORT.md` "Overall verdict: CLOSED" |
| P2 | `CLOSED` | `sr_derivative_priority2/CLOSURE_REPORT.md` "Level-4 Priority 2 -- CLOSED" |
| P3 | `CLOSED` | `m_rho_stability_priority3/CLOSURE_REPORT.md` "Level-4 Priority 3 -- CLOSED" (independent) |
| P4 | `PARTIAL` | `p4_theory_generalization/INDEPENDENT_ADJUDICATION.md` "Decision: PARTIAL" |
| P5 | `PARTIAL` | `p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md` `FINAL_P5_VERDICT = PARTIAL` |
| **P6** | **`CLOSED`** — *revised*, see §6 C1 | root `README.md` Level-4 status table (authoritative, updated by the adjudicator in the same pass as the P8 verdict). The intermediate record `p6r2_.../ADJUDICATION_RECORD_P6R2.md` still reads `FINAL_P6_VERDICT = PARTIAL`. |
| P7 | `CLOSED` | `p7_statistical_consequences/INDEPENDENT_ADJUDICATION.md` `FINAL_VERDICT = CLOSED` |
| P8 | **`FAIL`** — *authoritative* | `p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md`: 16 PASS / 5 FAIL; `G14` temporal integrity fails. Claude's `PARTIAL_CANDIDATE` did **not** survive. |

---

## 5. HISTORICAL EXPECTATION — what earlier priorities expected of a synthesis

Not requirements. Recorded so P9's output can be checked against what the
campaign anticipated.

| # | source | expectation |
|---|---|---|
| H1 | `docs/research_synthesis/EVIDENCE_HIERARCHY.md`, `CLAIM_CATALOG.md` | a synthesis layer already exists and is authoritative for wording; P9 must reconcile with it, not replace it |
| H2 | `p7/INDEPENDENT_ADJUDICATION.md` `RHO_C_STATUS = LOCAL_MATHEMATICAL_BOUNDARY_ONLY` | any synthesis must keep local stability and operational safety separate |
| H3 | `location_family/FINAL_REPORT.md` §A | the location-family result "is not distribution-free, universal, detector-independent, or a class-wide instability certificate" — a synthesis must not close that gap by aggregation |
| H4 | `p5/INDEPENDENT_ADJUDICATION.md` (G3/G7/G9 narrowing) | universal quantifiers over finite-grid Monte Carlo evidence were rejected once already; a synthesis repeating them repeats a known defect |
| H5 | `p6r_.../ADJUDICATION_RECORD.md` `NOVELTY_STATUS = NOT_ESTABLISHED` | P6 closure, if it comes, is not a novelty claim |
| H6 | `final_global_reaudit/CLAIM_FIREWALL.md` | a claim firewall already exists at project level; P9's `CLAIM_LANGUAGE_POLICY.md` must extend it, not fork it |

---

## 6. Conflicts between this prompt and repository authority

| # | item | prompt says | repository says | resolution |
|---|---|---|---|---|
| **C1** | **P6 status** — *resolved during the campaign* | §0: `P6 = CLOSED` | **At the anchor commit** the last independent verdict was `FINAL_P6_VERDICT = PARTIAL` with `G6`/`G9`/`G12` `PARTIAL`, and P6R2b was first-party only, stating verbatim "`P6 = CLOSED` is **not** declared here." P9 flagged the conflict and carried P6 at `PARTIAL`. **The authoritative status table has since been updated to `P6 = CLOSED`** in the same pass that produced the P8 verdict. | **Resolved in favour of the prompt, by the repository itself.** P9 now records `P6 = CLOSED`, scope-bound. It notes without dispute that no independent Gate-9 review is recorded *inside* the P6 namespace, so a reader tracing closure through `p6r2b_gate9_crn_identity/` alone will not find it. `P6-NOV` stays `NOT_ESTABLISHED`: closure is not novelty. |
| C2 | existence of P9 | §0 and §3 presuppose a defined Priority 9 | no such definition exists (§2) | prompt's own §3 fallback governs; all P9 scope is `PROMPT_DERIVED` and labelled as such |
| C3 | "preserve frozen P9 gates literally" (§18) | assumes frozen P9 gates may exist | none exist | P9 preregisters its own gates in `CLOSURE_GATES.md`, marked `P9_ORIGINAL`, and records that no historical gate was overwritten |
| C4 | P6 campaign existence | root `README.md:34` (at anchor): "P6 has a pre-design directory only; its full campaign has not started" | four P6 campaign trees exist | **Fixed during the campaign, not by P9.** The root `README.md` now carries both a P6 row and a P8 row. P9 recorded the staleness (`D-08`) and correctly declined to edit a frozen artifact; the owner fixed it. |
| C5 | P8 as an input | §5: use only as provisional | **now authoritative: `P8 = FAIL`** | P9's preregistered `FAIL` rule applied literally: P8 is quarantined from all P9 premises. §16 permits four tiers; **P9 declines the permission** and keeps its stricter pre-committed rule (`P8_TO_P9_RECONCILIATION.md` §4). |

---

## 7. Scope P9 adopts (declared before any result)

**In scope** (from prompt §3, as the only available scope source):

1. Recovery and normalisation of the status of every scientifically important
   claim in P1–P8 into a single ledger with non-flattened evidence classes.
2. Cross-priority **definition** crosswalk for the objects that recur under the
   same name with possibly different finite-sample estimands.
3. Cross-priority **discrepancy** register, including discrepancies P9 cannot
   resolve.
4. A logical dependency DAG whose edges are real implications.
5. A claim-language firewall extending the existing project firewall.
6. Independent reproduction of a small set of anchor results spanning the
   dependency chain.
7. A model-scope map with explicit `UNKNOWN` cells.
8. Operational-safety and safe-re-baselining synthesis that keeps local,
   stochastic, and operational layers separate.
9. Project-level novelty position, conservative.
10. Adversarial review of the synthesis itself.

**Out of scope, declared:**

* Any repair, reopening, or status change of P4, P5, P6, P7 or P8.
* Any new production experiment whose purpose is to *establish* a new
  scientific claim about the model. P9's computation is **reproduction and
  consistency checking**, not discovery. (Prompt §12 explicitly permits
  declining a theorem target; §7.1 below records the decision.)
* Any edit to a frozen historical artifact, including the stale root
  `README.md`.
* Real data, new detectors, new distribution families, novelty adjudication of
  any single priority.

### 7.1 Theorem-target decision, declared before analysis

Prompt §12 asks whether P9 has a legitimate theorem target and forbids
inventing one. P9's provisional position, to be confirmed or withdrawn in
`THEORY.md` after the definition and dependency audits:

> The defensible P9 theorem target is **not** a new statement about the
> monitoring model. It is a **statement about the evidence graph**: a
> *no-inflation* / claim-class propagation result — that the strongest claim
> derivable from the ledger along any path in the dependency DAG is bounded
> above by the weakest evidence class on that path, and identification of which
> published narrative sentences currently violate that bound.

That target is checkable, is about objects P9 owns, requires no new premise,
and cannot be satisfied by concatenating earlier READMEs. If the audit shows it
is vacuous, `THEORY.md` will record P9 as having **no** theorem and say so.

---

## 8. Classification summary

| class | count | items |
|---|---:|---|
| `FROZEN_REQUIREMENT` | **0** | none defines P9's question. P8 §16 constrains one input and is filed as `AUTHORITATIVE_DEPENDENCY` (§2) |
| `AUTHORITATIVE_DEPENDENCY` | 9 | P1–P8 statuses (§4) + the P8 §16 "Exact P9 handoff boundary" |
| `HISTORICAL_EXPECTATION` | 6 | H1–H6 (§5) |
| `OPTIONAL_EXTENSION` | — | see `CLOSURE_GATES.md`; none mandatory |
| `UNSUPPORTED` | 5 | U1–U5 (§3) |
| `PROMPT_DERIVED` | 10 | §7 in-scope items |

The zero in the first row is the finding that governs how this campaign must be
read.
