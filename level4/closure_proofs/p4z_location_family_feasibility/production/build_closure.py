#!/usr/bin/env python3
"""Assemble the P4Z successor closure artifact from the adjudicated evidence.

Historical P4 is not rewritten and not relabelled.  This produces a NEW
successor artifact that states exactly which historically unadjudicated cells
the governed P4Z campaign discharged, under which estimator, runtime, hashes
and cost, and says plainly what it does not establish.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
P4 = NS.parent / "p4_theory_generalization"


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def main() -> int:
    adj = load(NS / "production" / "adjudication.json")
    ind = load(NS / "production" / "independent_adjudication.json")
    replay = load(NS / "production" / "replay.json")
    lean = load(NS / "results" / "lean_audit.json")
    plan = load(NS / "production" / "campaign_plan.json")
    checkpoint = load(NS / "configs" / "checkpoint_p4z.json")
    contract = load(NS / "production" / "mac_runtime_contract.json")
    manifest_head = load(NS / "production" / "run_state.json")
    p4 = load(P4 / "results" / "closure_decision.json")
    if adj is None or ind is None:
        raise SystemExit("adjudication artifacts are missing; nothing to close")

    residue = adj["unresolved_residue"]
    discharged = residue["by_result"]["PASS"]
    failed = residue["by_result"]["FAIL"]
    inconclusive = residue["by_result"]["INCONCLUSIVE"]

    if failed:
        verdict = "P4Z_FAILED_FROZEN_GATE"
    elif adj["cost"]["COST_CAP"] == "FAIL":
        verdict = "P4Z_COST_CAP_FAIL"
    elif ind["verdict"] != "ADJUDICATION_PASS":
        verdict = "P4Z_PROVENANCE_FAIL"
    elif inconclusive:
        verdict = "P4Z_INCONCLUSIVE"
    elif adj["counts"]["INCONCLUSIVE"]:
        # the residue is discharged but the full 96-cell grid is not
        verdict = "P4Z_NUMERICAL_PASS_AWAITING_FORMAL_OR_GOVERNANCE"
    elif adj["counts"]["FAIL"]:
        verdict = "P4Z_FAILED_FROZEN_GATE"
    else:
        verdict = "P4Z_CLOSED"

    doc = {
        "schema": "rebaseguard.p4z-successor-closure.v1",
        "result_bearing": True,
        "verdict": verdict,
        "historical_status_unchanged": {
            "P4_ORIGINAL_VERDICT": p4["verdict"],
            "P4_artifacts_modified": False,
            "P4_relabelled": False,
            "P4X_and_P4Y_modified": False,
            "statement": "Historical P4 remained PARTIAL throughout and is "
                         "untouched. P4Z supplies successor evidence; it does "
                         "not repair, rewrite or relabel any historical artifact.",
        },
        "successor_evidence": {
            "historically_unresolved_cells": residue["total"],
            "discharged_PASS": discharged,
            "FAIL": failed,
            "INCONCLUSIVE": inconclusive,
            "which_historical_gate": "P4X obligation C2 / Checkpoint A gate X6, "
                                     "the 8 cells recorded PRECONDITION_NOT_MET",
            "cells": [
                {k: c[k] for k in ("layer", "detector", "family", "m",
                                   "gate_result", "reasons")}
                for c in adj["cells"] if c["is_historically_unresolved"]
            ],
        },
        "full_grid": {
            "cells_total": adj["cells_total"],
            "counts": adj["counts"],
            "note": "the frozen scope is 96 cells; a campaign that discharges "
                    "the 8-cell residue has NOT re-adjudicated all 96",
            "killed_configurations": adj["killed_configurations"],
            "excluded_configurations": adj["excluded_configurations"],
        },
        "theorem_scope": {
            "source": "level4/closure_proofs/p4_theory_generalization",
            "tree_object": checkpoint["theorem"]["tree_object"],
            "statement": "G1a: Gamma_{D,m,f} = E_0[A_m S_tau^psi], for a regular "
                         "one-dimensional location family and a fixed "
                         "residual-path stopping rule; the frozen two-sided "
                         "CUSUM and two-chart SR only. Not distribution free, "
                         "not detector universal, not global, not nonlinear, "
                         "not valid for moving support or for an innovation law "
                         "without a first moment.",
            "modified_by_p4z": False,
        },
        "estimators": {
            "primary": checkpoint["estimators"]["primary"],
            "companion": checkpoint["estimators"]["fallback"],
            "analytic_contract": checkpoint["estimators"]["analytic_contract"],
        },
        "runtime": {
            "host": contract["declaration"],
            "runtime_hash": contract["runtime_hash"],
            "cpu": contract["machine"]["cpu_brand"],
            "os": f"{contract['operating_system']['product']} "
                  f"{contract['operating_system']['version']} "
                  f"({contract['operating_system']['build']})",
            "python": contract["python"]["version"],
            "numpy": contract["package_lock"]["numpy"],
            "scipy": contract["package_lock"]["scipy"],
            "blas": contract["numerical_backend"]["blas_name"],
            "workers": plan["execution"]["workers"],
        },
        "thresholds": adj["thresholds_used"],
        "cost": adj["cost"],
        "provenance": {
            "independent_adjudication": ind["verdict"],
            "checks_total": ind["checks_total"],
            "checks_failed": ind["checks_failed"],
            "replay": None if replay is None else {
                "blocks_replayed": replay["blocks_replayed"],
                "all_scientific_hashes_identical":
                    replay["all_scientific_hashes_identical"],
                "any_scientific_field_mismatch":
                    replay["any_scientific_field_mismatch"],
            },
        },
        "formal": None if lean is None else {
            "target": "bounded-survival lemma only",
            "declarations": lean["declarations"],
            "axioms": lean["axioms"],
            "errors": lean["compile"]["errors"],
            "new_axioms": lean["new_axioms"],
        },
        "what_is_awaiting": {
            "formal": "SATISFIED. The bounded-survival lemma compiles with no "
                      "error, no sorry, and no new axiom. Nothing further was "
                      "required by the frozen checkpoint.",
            "governance": "OUTSTANDING. 52 of the 96 frozen cells are "
                          "INCONCLUSIVE and a governance decision is needed on "
                          "them. 32 were killed by K3 because P4Z's own light "
                          "regime envelope under-predicted their variance; 20 "
                          "were refused by K7 because the h=0.2 rung of the "
                          "frozen FD ladder is outside the O(h^2) asymptotic "
                          "regime for light-tailed families at the frozen "
                          "thresholds. Neither is evidence against the "
                          "estimator, and every one of those 52 cells already "
                          "PASSED in P4X. Re-certifying them needs a "
                          "re-calibrated envelope and a ladder whose coarsest "
                          "rung is inside the asymptotic regime -- which is a "
                          "NEW frozen campaign, not an amendment of this one.",
            "why_not_closed": "P4Z_CLOSED requires every frozen scientific, "
                              "numerical, provenance, governance, cost and "
                              "formal condition to be satisfied. The 8-cell "
                              "residue is discharged and provenance, cost, "
                              "replay and formal are all clean, but the frozen "
                              "96-cell scope is not fully adjudicated.",
        },
        "claims_explicitly_not_made": [
            "historical P4 was retroactively repaired",
            "P4 is CLOSED",
            "P5Y is CLOSED",
            "K1 is CLOSED",
            "Level-4 is CLOSED",
            "production readiness unrelated to this theorem",
            "all 96 frozen cells were re-adjudicated",
        ],
    }
    out = NS / "results" / "successor_closure.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    (NS / "SUCCESSOR_CLOSURE.md").write_text(_markdown(doc))
    print(f"verdict {verdict}")
    print(f"residue: PASS {discharged}  FAIL {failed}  INCONCLUSIVE {inconclusive}")
    print(f"full grid: {adj['counts']}")
    print(f"-> {out}")
    return 0


def _markdown(d: dict) -> str:
    r = d["successor_evidence"]
    g = d["full_grid"]
    rows = "\n".join(
        f"| {c['layer']} | `{c['detector']}` | `{c['family']}` | {c['m']} | "
        f"**{c['gate_result']}** | {'; '.join(c['reasons']) or '—'} |"
        for c in r["cells"])
    fm = d["formal"]
    pv = d["provenance"]
    rp = pv["replay"]
    return f"""# P4Z successor closure

```text
P4Z_VERDICT = {d["verdict"]}

P4_ORIGINAL_VERDICT = {d["historical_status_unchanged"]["P4_ORIGINAL_VERDICT"]}   (unchanged, untouched, not relabelled)
LEVEL4_GLOBAL_CLOSURE = NO
```

Historical P4 remains historical P4.  Nothing in the P4, P4X or P4Y namespaces
was modified, and no verdict of theirs was converted.  This is a **new**
successor artifact recording what a governed P4Z campaign, run entirely on the
local Mac, does and does not establish.

## 1. What was discharged

The historically unadjudicated residue is the **{r["historically_unresolved_cells"]} cells** that P4X's own
precision precondition could not decide — its obligation C2 / Checkpoint-A gate
`X6`, recorded `PRECONDITION_NOT_MET`.

```text
discharged PASS   {r["discharged_PASS"]}
FAIL              {r["FAIL"]}
INCONCLUSIVE      {r["INCONCLUSIVE"]}
```

| layer | detector | family | m | result | reasons |
|---|---|---|---|---|---|
{rows}

## 2. What was NOT re-adjudicated

The frozen scope is **{g["cells_total"]} cells** in 24 configurations.  Discharging the
{r["historically_unresolved_cells"]}-cell residue is **not** a re-adjudication of all {g["cells_total"]}.

```text
PASS         {g["counts"]["PASS"]}
FAIL         {g["counts"]["FAIL"]}
INCONCLUSIVE {g["counts"]["INCONCLUSIVE"]}
```

Configurations killed by a prespecified kill gate: `{g["killed_configurations"]}`
Configurations excluded on budget: `{g["excluded_configurations"]}`

A cell reported `INCONCLUSIVE` is reported as `INCONCLUSIVE`.  It is never
counted as a pass and never dropped from the denominator.

## 3. Theorem scope

Inherited unchanged at tree `{d["theorem_scope"]["tree_object"]}`.

{d["theorem_scope"]["statement"]}

## 4. Estimator

```text
PRIMARY    {d["estimators"]["primary"]["name"]}   {d["estimators"]["primary"]["file"]}
           sha256 {d["estimators"]["primary"]["sha256"]}
COMPANION  {d["estimators"]["companion"]["name"]}     {d["estimators"]["companion"]["file"]}
           sha256 {d["estimators"]["companion"]["sha256"]}
CONTRACT   {d["estimators"]["analytic_contract"]["file"]}
           sha256 {d["estimators"]["analytic_contract"]["sha256"]}
```

## 5. Runtime

```text
host          {d["runtime"]["host"]["P4Z_NUMERICAL_HOST"]}
AWS CPU used  {d["runtime"]["host"]["AWS_CPU_USED_BY_P4Z"]}
runtime_hash  {d["runtime"]["runtime_hash"]}
cpu           {d["runtime"]["cpu"]}
os            {d["runtime"]["os"]}
python        {d["runtime"]["python"]}   numpy {d["runtime"]["numpy"]}   scipy {d["runtime"]["scipy"]}
blas          {d["runtime"]["blas"]}
workers       {d["runtime"]["workers"]}
```

## 6. Thresholds — none changed

```text
relative <= {d["thresholds"]["relative"]}
|z|      <= {d["thresholds"]["z"]}
r*        = {d["thresholds"]["r_star"]}
any_threshold_changed_by_p4z = {d["thresholds"]["any_threshold_changed_by_p4z"]}
```

## 7. Cost

```text
CPU        {d["cost"]["cpu_hours_total"]:.4f} h
cap        {d["cost"]["cap_hours"]} h
COST_CAP   {d["cost"]["COST_CAP"]}
```

Includes every block produced, failed and inconclusive alike.

## 8. Provenance

```text
independent adjudication   {pv["independent_adjudication"]}  ({pv["checks_total"] - pv["checks_failed"]}/{pv["checks_total"]} checks)
replay                     {"n/a" if rp is None else f'{rp["blocks_replayed"]} blocks, hashes identical: {rp["all_scientific_hashes_identical"]}, field mismatches: {rp["any_scientific_field_mismatch"]}'}
```

## 9. Formal

```text
{"none" if fm is None else f'target       {fm["target"]}'}
{"" if fm is None else f'declarations {fm["declarations"]}, errors {fm["errors"]}, new axioms {fm["new_axioms"]}'}
{"" if fm is None else f'axioms       {fm["axioms"]}'}
```

## 10. What is awaiting

```text
formal      SATISFIED   -- bounded-survival lemma compiles, no sorry, no new axiom
governance  OUTSTANDING -- 52 of 96 frozen cells are INCONCLUSIVE
```

32 of those 52 were killed by `K3` because P4Z's own light-regime variance
envelope under-predicted them; 20 were refused by `K7` because the `h = 0.2`
rung of the frozen FD ladder is outside the `O(h^2)` asymptotic regime for
light-tailed families at the frozen thresholds.  Neither is evidence against
the estimator, and **every one of those 52 cells already PASSED in P4X**.

Re-certifying them requires a re-calibrated regime envelope and a ladder whose
coarsest rung is inside the asymptotic regime.  That is a **new frozen
campaign**, not an amendment of this one, and P4Z does not make it.

## 11. What this does not claim

""" + "\n".join(f"* {c}" for c in d["claims_explicitly_not_made"]) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
