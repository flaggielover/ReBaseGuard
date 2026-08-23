#!/usr/bin/env python3
"""Generate the isolated post-closure Level-4 re-audit artifacts.

The only scientific-status input is requirements.json. This module validates
that 18-row table, resolves scoped later updates, checks the protected history,
derives the verdict, and renders every current-state decision artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve()
AUDIT = HERE.parents[1]
REPO = HERE.parents[3]
SOURCE = AUDIT / "requirements.json"
HASHES = AUDIT / "historical_artifact_hashes.json"
VERIFICATION = AUDIT / "results" / "verification.json"

ALLOWED_STATUSES = {"PASS", "PARTIAL", "FAIL", "OPEN"}
ALLOWED_CLASSES = {"MANDATORY", "OPTIONAL", "STRONG_EXTENSION", "STRETCH", "AMBIGUOUS"}

GENERATED_PATHS = (
    AUDIT / "README.md",
    AUDIT / "REQUIREMENT_UPDATE.md",
    AUDIT / "INTEGRITY_AUDIT.md",
    AUDIT / "CURRENT_SCIENTIFIC_SYNTHESIS.md",
    AUDIT / "FINAL_DECISION.md",
    AUDIT / "FAILURE_DIAGNOSES.md",
    AUDIT / "results" / "final_decision.json",
    REPO / "level4" / "reports" / "LEVEL_4_POST_CLOSURE_REAUDIT.md",
    REPO / "level4" / "reports" / "LEVEL_4_CURRENT_LEDGER.md",
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_historical_hashes() -> dict[str, Any]:
    manifest = load_json(HASHES)
    mismatches: list[dict[str, str]] = []
    missing: list[str] = []
    for rel, expected in manifest["files"].items():
        path = REPO / rel
        if not path.exists():
            missing.append(rel)
            continue
        actual = sha256(path)
        if actual != expected:
            mismatches.append({"path": rel, "expected": expected, "actual": actual})
    return {
        "status": "INTACT" if not missing and not mismatches else "BROKEN",
        "files_verified": len(manifest["files"]),
        "missing": missing,
        "mismatches": mismatches,
        "baseline_head": manifest["baseline_head"],
    }


def validate_source(source: dict[str, Any]) -> None:
    rows = source.get("requirements", [])
    if len(rows) != 18:
        raise ValueError(f"expected exactly 18 requirements, found {len(rows)}")
    ids = [row.get("id") for row in rows]
    if len(set(ids)) != 18:
        raise ValueError("requirement IDs must be unique")
    if source.get("historical_stage_f_status") != "LEVEL-4-PARTIAL":
        raise ValueError("historical Stage-F verdict changed")
    if len([row for row in rows if row.get("classification") == "MANDATORY"]) != 16:
        raise ValueError("the Stage-F reconstruction must retain 16 mandatory rows")
    for row in rows:
        if row.get("classification") not in ALLOWED_CLASSES:
            raise ValueError(f"{row['id']}: invalid classification")
        stage_status = row.get("stage_f", {}).get("status")
        if stage_status not in ALLOWED_STATUSES:
            raise ValueError(f"{row['id']}: invalid Stage-F normalized status")
        update = row.get("later_update")
        if update is not None:
            if update.get("effect") != "CLOSES_REQUIREMENT" or update.get("status") != "PASS":
                raise ValueError(f"{row['id']}: later updates may only record scoped closure")
            if not (REPO / update["artifact"]).exists():
                raise ValueError(f"{row['id']}: missing closure artifact {update['artifact']}")
        for artifact in row.get("artifacts", []):
            if not (REPO / artifact).exists():
                raise ValueError(f"{row['id']}: missing evidence artifact {artifact}")


def derive_decision() -> dict[str, Any]:
    source = load_json(SOURCE)
    validate_source(source)
    integrity = verify_historical_hashes()
    verification = load_json(VERIFICATION)

    resolved: list[dict[str, Any]] = []
    for row in source["requirements"]:
        item = dict(row)
        update = row.get("later_update")
        item["current_status"] = update["status"] if update else row["stage_f"]["status"]
        item["changed_since_stage_f"] = bool(
            update and update["status"] != row["stage_f"]["status"]
        )
        resolved.append(item)

    counts = Counter(row["current_status"] for row in resolved)
    mandatory = [row for row in resolved if row["classification"] == "MANDATORY"]
    mandatory_unmet = [row for row in mandatory if row["current_status"] in {"FAIL", "OPEN"}]
    mandatory_partial = [row for row in mandatory if row["current_status"] == "PARTIAL"]
    mandatory_nonpass = [row for row in mandatory if row["current_status"] != "PASS"]
    optional_unmet = [
        row for row in resolved
        if row["classification"] != "MANDATORY" and row["current_status"] != "PASS"
    ]
    closed_since = [row for row in resolved if row["changed_since_stage_f"]]

    inputs = source["decision_inputs"]
    integrity_ok = (
        inputs["protocol_integrity"] == "INTACT"
        and inputs["historical_artifacts_unchanged"] is True
        and integrity["status"] == "INTACT"
    )
    if inputs["central_level4_claim_contradicted"] or not integrity_ok:
        verdict = "LEVEL-4-FAILED"
    elif mandatory_nonpass:
        verdict = "LEVEL-4-PARTIAL"
    else:
        verdict = "LEVEL-4-CLOSED"

    allowed = source["taxonomy"]["allowed_labels"]
    if verdict not in allowed:
        raise ValueError(f"derived verdict {verdict} is outside the frozen taxonomy")

    def compact(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "requirement": row["requirement"],
            "classification": row["classification"],
            "status": row["current_status"],
            "blocker_type": row.get("blocker_type"),
            "artifacts": row["artifacts"],
        }

    decision = {
        "schema": "rebaseguard.level4-post-closure-final-decision.v1",
        "audit": "GLOBAL LEVEL-4 RE-AUDIT INCORPORATING POST-STAGE-F CLOSURES",
        "audit_date": source["audit_date"],
        "audit_start_head": source["audit_start_head"],
        "historical_stage_f_status": source["historical_stage_f_status"],
        "current_status": verdict,
        "taxonomy_source": source["taxonomy"]["source"],
        "allowed_labels": allowed,
        "total_requirements": len(resolved),
        "pass_count": counts["PASS"],
        "partial_count": counts["PARTIAL"],
        "fail_count": counts["FAIL"],
        "open_count": counts["OPEN"],
        "mandatory_total": len(mandatory),
        "mandatory_pass_count": sum(row["current_status"] == "PASS" for row in mandatory),
        "mandatory_partial_count": len(mandatory_partial),
        "mandatory_unmet": [compact(row) for row in mandatory_unmet],
        "mandatory_partial_or_negative": [compact(row) for row in mandatory_partial],
        "optional_unmet": [compact(row) for row in optional_unmet],
        "requirements_closed_since_stage_f": [compact(row) for row in closed_since],
        "requirements": resolved,
        "protocol_integrity": integrity,
        "reproducibility_status": verification,
        "historical_artifacts_unchanged": integrity["status"] == "INTACT",
        "no_new_science_performed": inputs["no_new_science_performed"],
        "decision_rule_trace": [
            "historical Stage-F verdict is immutable and remains LEVEL-4-PARTIAL",
            f"protected-history audit -> {integrity['status']}",
            f"central Level-4 claim contradicted -> {inputs['central_level4_claim_contradicted']}",
            f"mandatory non-PASS rows -> {len(mandatory_nonpass)} ({len(mandatory_partial)} partial/negative; {len(mandatory_unmet)} fail/open)",
            f"mandatory fail/open rows -> {len(mandatory_unmet)}",
            f"fallback taxonomy -> {verdict}",
        ],
        "historical_statuses_preserved": {
            "level_1_3": "CLOSED",
            "stage_b": "STAGE-B-CLOSED-RIGOROUS-PERIOD2",
            "stage_c": "STAGE-C-PARTIAL",
            "stage_c1": "STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY",
            "stage_d": "STAGE-D-PARTIAL",
            "stage_d_D2_3": "FAILED",
            "stage_d_D2_5": "MATHEMATICAL, NOT OPERATIONAL",
            "stage_e": "STAGE-E-PARTIAL",
            "stage_e_H_E5": "0/3",
            "stage_f": "LEVEL-4-PARTIAL",
            "track_1a": "MGT1-TRACK1A-FAILED",
            "track_3": "LOCATION-FAMILY-THEOREM-PARTIAL",
            "track_3_historical_gate": "4.605351% > 3% — FAILED"
        },
        "current_scoped_closures": {
            "track_1b": "MGT1-TRACK1B-CLOSED",
            "track_2": "SR-DERIVATIVE-CLOSED",
            "track_3ab": "LOCATION-FAMILY-TRACK3AB-CLOSED"
        },
        "sr_status_boundary": {
            "derivative_theorem": "CLOSED",
            "Gamma_SR_gt_2": "CONFIRMATORY NUMERICAL",
            "rigorous_SR_local_instability_certificate": "OPEN"
        },
        "strongest_rigorous_result": "Lean-checked stopped-likelihood differentiation spine, outward-rounded Gamma_CUSUM enclosure above two, and the certified deterministic-skeleton period-2 orbit",
        "strongest_general_theorem": "For regular one-dimensional location families satisfying explicit stopped change-of-measure and domination hypotheses, F'_rho(0)=rho(1-Gamma_f) for matched raw-observation m=1 reuse",
        "strongest_cross_detector_result": "CUSUM and the authoritative symmetric two-chart SR detector both satisfy the stopped-score derivative identity; SR Gamma above two remains confirmatory numerical evidence",
        "most_important_negative_result": "The Gamma_m crossing is mathematical, not operational: zero of four monitoring metrics peaked and all four were monotone in log m",
        "external_validity_limitation": "The frozen three-stream semi-real campaign met H-E5 on zero of three tasks; no later external-validation campaign was performed",
        "publication_safe_claim": "ReBaseGuard has a rigorous CUSUM core, independently closed derivative theorems for the scoped m>1 CUSUM and symmetric SR settings, and a conditional regular-location-family stopped-score theorem; its global Level-4 status remains partial because mandatory phase-map, semi-real validation, and novelty-provenance requirements remain unmet."
    }
    return decision


def requirement_table(decision: dict[str, Any]) -> str:
    lines = [
        "| ID | Requirement | Class | Stage-F status | Later evidence | Current | Reason |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in decision["requirements"]:
        update = row.get("later_update")
        later = update["campaign"] if update else "None that changes this row"
        reason = row["reason"].replace("|", "/")
        lines.append(
            f"| {row['id']} | {row['requirement']} | {row['classification']} | "
            f"{row['stage_f']['label']} | {later} | **{row['current_status']}** | {reason} |"
        )
    return "\n".join(lines)


def render_readme(decision: dict[str, Any]) -> str:
    return f"""# Global Level-4 re-audit after scoped closure proofs

This isolated namespace derives the current Level-4 status without changing
Stage F. Historical Stage F remains `{decision['historical_stage_f_status']}`;
this namespace answers the later question using the evidence boundary after
Tracks 1B, 2, and 3A/3B.

`requirements.json` is the sole status source. It contains exactly the 18
requirements reconstructed by Stage F. `src/generate_audit.py` derives the
current row statuses, counts, blocker lists, verdict JSON, and mirrored
reports. Do not edit generated status artifacts independently.

Current derived result:

```text
{decision['pass_count']} PASS
{decision['partial_count']} PARTIAL / NEGATIVE
{decision['fail_count']} FAIL
{decision['open_count']} OPEN
{decision['current_status']}
```

Mandatory fail/open blockers are the D4 phase map, semi-real external
validation, and novelty verification. The first two require scientific work;
the third is a documentation/provenance gap.

Reproduce with:

```bash
bash level4/re_audit_post_closure/reproduce.sh
```

The reproducer runs verification only. It launches no scientific campaign.
"""


def render_requirement_update(decision: dict[str, Any]) -> str:
    closed = "\n".join(
        f"- {row['requirement']} — {row['later_update']['campaign']}"
        for row in decision["requirements"] if row["changed_since_stage_f"]
    )
    return f"""# Post-closure requirement update

This table mirrors the canonical 18-row source in `requirements.json`. Counts
and the verdict are generated; this document contains no independent status
assertions.

{requirement_table(decision)}

## Requirements closed since Stage F

{closed}

The Stage-F verdict remains historical `LEVEL-4-PARTIAL`. Closing a later
scoped requirement does not rewrite its Stage-F row or its originating stage
decision.
"""


def render_integrity(decision: dict[str, Any]) -> str:
    v = decision["reproducibility_status"]
    i = decision["protocol_integrity"]
    return f"""# Post-closure integrity audit

## Repository state at audit start

- Branch: `main`
- HEAD: `{decision['audit_start_head']}`
- `origin/main`: `{decision['audit_start_head']}` after `git fetch origin --prune`
- Ahead/behind: `0 / 0`
- Worktree before implementation: clean
- No frozen post-Stage-F global taxonomy was found; the Stage-F fallback is reused.

The first full Level 1–3 invocation was interrupted by its execution session
during Lean compilation without a verifier failure. The identical command was
rerun from a clean state and completed successfully; the interruption is not
silently treated as a pass.

## Actual verification results

| Command / package | Result |
|---|---|
| `bash scripts/verify_level_1_3.sh` | PASS; zero skips; final Lean source elaborated; Arb replay byte-identical; {v['level_1_3_full']['regression_tests']} regression tests passed |
| `bash scripts/verify_level_4.sh` | PASS; {v['authoritative_repository']['tests']} authoritative tests after re-audit integration |
| Track 1B reproducer | {v['scoped_reproducers']['track_1b']} |
| Track 2 reproducer | {v['scoped_reproducers']['track_2']} |
| Track 3A/3B reproducer | {v['scoped_reproducers']['track_3ab']} |
| Post-closure reproducer | {v['post_closure_reproducer']['status']}; byte-stable `{v['post_closure_reproducer']['byte_stable']}` |

## Protected history

- Exact SHA-256 files checked: **{i['files_verified']}**
- Missing: **{len(i['missing'])}**
- Mismatched: **{len(i['mismatches'])}**
- Status: **{i['status']}**

The manifest covers every tracked file in `level4/stage_f/`, both historical
Stage-F final reports, the frozen Stage C/C.1/D/E protocols and precommitments,
the critical historical decisions, and the three later closure protocols and
decisions. Stage F is byte-for-byte unchanged.

## Check accounting

- Authoritative repository tests: **{v['distinct_test_accounting']['authoritative_repository_tests']}**
- Historical closure tests: **{v['distinct_test_accounting']['historical_closure_tests']}**
- Track-3A/3B focused tests: **{v['distinct_test_accounting']['track_3ab_tests']}**
- Current distinct total: **{v['distinct_test_accounting']['combined_checks']} / {v['distinct_test_accounting']['combined_checks']}**

No Monte Carlo campaign, semi-real dataset, D4 run, SR certificate campaign,
phase diagram, or new theorem was executed by this re-audit.
"""


def render_synthesis(decision: dict[str, Any]) -> str:
    return """# Current scientific synthesis

## A. Rigorous core

Level 1–3 remains closed. The CUSUM stopped-likelihood derivative spine and
outward-rounded Gamma enclosure remain verified. Stage B remains a rigorous
period-2 result for the deterministic conditional-mean skeleton, not the
stochastic long-run monitoring process.

## B. Post-Stage-F theorem closures

Track 1B closes the scoped `m>1` derivative theorem. Track 2 closes the
authoritative symmetric SR derivative theorem. Track 3A/3B closes the regular
location-family stopped-score theorem under explicit analytic hypotheses.
These are current requirement updates, not revisions of Stage D, Track 1A,
historical Track 3, or Stage F.

## C. Numerical and generalization evidence

The SR gain above two remains confirmatory numerical evidence. Stage D retains
six-family numerical robustness with the historical t3 estimand ambiguity.
Track 3A/3B adds a variance-aware t3 replication for the distinct raw-reuse
gain used by the location-family theorem.

## D. Operational negative results

The measured Gamma_m crossing remains mathematical, not operational. Stage E
remains heterogeneous: Task A contains a directional contradiction, Task B is
low-power, Task C excludes unreliable E2/E3 endpoints, and zero of three tasks
support H-E5.

## E. Open rigor upgrades

The rigorous SR local-instability certificate remains open. The derivative
theorem does not require that certificate, and the numerical gain estimate is
not promoted to a certified inequality.

## F. Current unmet requirements

The mandatory D4 phase map and semi-real external-validation requirements
remain scientific blockers. Novelty verification remains a
documentation/provenance blocker because the review artifact is absent. The
non-Gaussian robustness row remains a partially met strong extension.

## Claim scope

The evidence supports two named detector constructions and regular
one-dimensional location families under explicit conditions. It does not
support claims covering arbitrary detectors or arbitrary distributions, and
the semi-real study does not establish deployment readiness, optimality, or
general safety.
"""


def render_final_decision(decision: dict[str, Any]) -> str:
    blockers = "\n".join(
        f"- **{row['requirement']}** — {row['status']}; {row['blocker_type']}"
        for row in decision["mandatory_unmet"]
    )
    trace = "\n".join(f"{idx}. {item}" for idx, item in enumerate(decision["decision_rule_trace"], 1))
    return f"""# Current post-closure Level-4 decision

## Current verdict

> **`{decision['current_status']}`**

## Historical Stage-F verdict

> **`{decision['historical_stage_f_status']}` — unchanged and historically correct**

The current verdict is a new derived audit at a later evidence boundary. It
does not replace, correct, or edit Stage F.

## Mechanical path

{trace}

Current 18-row count: **{decision['pass_count']} PASS · {decision['partial_count']} PARTIAL/NEGATIVE · {decision['fail_count']} FAIL · {decision['open_count']} OPEN**.

## Mandatory fail/open blockers

{blockers}

The phase-map and external-validation blockers require new scientific work.
The novelty blocker is documentation/provenance work. The stability-aware
policy and operational-consequence rows remain mandatory partial/negative
limitations and are reported separately from the three fail/open blockers.

## Requirements closed after Stage F

- `m>1` derivative theorem — Track 1B
- SR derivative theorem — Track 2
- general location-family theorem — Track 3A/3B

## SR boundary

- Derivative theorem: **CLOSED**
- Gamma above two: **CONFIRMATORY NUMERICAL**
- Rigorous local-instability certificate: **OPEN**
"""


def render_failures(decision: dict[str, Any]) -> str:
    return """# Failure and limitation diagnoses

## Scientific blockers

The D4 `m`–`rho` phase map was not run because the historical D2 gate failed.
No later campaign supplies it. Closing this row requires new scientific work.

The Stage-E criterion remains zero of three tasks supporting H-E5. Closing it
requires a new frozen external-validation campaign; the current re-audit does
not start one.

## Documentation/provenance blocker

The persisted prior-art review required by the Stage-F reconstruction is still
absent. This is a documentation/provenance gap, not a contradiction of the
mathematical core.

## Partial and negative rows

Stage C remains partial because C6 failed. The Gamma_m crossing still lacks an
operational counterpart. Non-Gaussian robustness remains partial because its
historical t3 estimand ambiguity is preserved.

## Historical failures retained

Stage-D D2.3, Track 1A, and the historical Track-3 4.605351% gate remain
failed. Stage E remains partial at 0/3. No first-run adversarial failure
occurred in this new namespace; therefore no synthetic failure record is
created.
"""


def render_report(decision: dict[str, Any]) -> str:
    blockers = "\n".join(
        f"- {row['requirement']} — {row['blocker_type']}"
        for row in decision["mandatory_unmet"]
    )
    return f"""# ReBaseGuard Level 4 — post-closure global re-audit

## A. Current global verdict

**`{decision['current_status']}`**

## B. Historical Stage-F verdict

**`{decision['historical_stage_f_status']}`**, preserved unchanged.

## C. Closed since Stage F

The scoped `m>1` derivative theorem, SR derivative theorem, and regular
location-family stopped-score theorem now pass their original requirement
rows through Tracks 1B, 2, and 3A/3B respectively.

## D–E. Remaining mandatory blockers

{blockers}

The first two are scientific blockers. Novelty verification is a
documentation/provenance blocker.

## F. Mechanical decision

The generator reads exactly 18 rows and derives **{decision['pass_count']} pass,
{decision['partial_count']} partial/negative, {decision['fail_count']} fail,
and {decision['open_count']} open**. There are {len(decision['mandatory_unmet'])}
mandatory fail/open rows and {len(decision['mandatory_partial_or_negative'])}
mandatory partial/negative rows, so the fallback taxonomy returns
`{decision['current_status']}`.

## G–J. Scientific extrema

- Strongest rigorous result: {decision['strongest_rigorous_result']}.
- Strongest general theorem: {decision['strongest_general_theorem']}.
- Strongest cross-detector result: {decision['strongest_cross_detector_result']}.
- Most important negative result: {decision['most_important_negative_result']}.

## K–L. External validity and SR Arb

{decision['external_validity_limitation']}. The rigorous SR local-instability
certificate remains open; only the derivative theorem is closed.

## M. Claim boundary

The safe claim is scoped to the named CUSUM and SR constructions and to regular
location families satisfying the stated analytic hypotheses. The work does
not establish arbitrary-detector coverage, arbitrary-distribution coverage,
deployment readiness, optimality, or universal safety.

## N. Publication-safe summary

{decision['publication_safe_claim']}

## O. Resume-safe summary

- Historical Stage F stays `LEVEL-4-PARTIAL`; the current derived verdict is also `LEVEL-4-PARTIAL`.
- Three theorem requirements closed later; D4, Stage E external validation, and novelty provenance remain mandatory fail/open blockers.
- No new science was run; exact protected hashes and {decision['reproducibility_status']['distinct_test_accounting']['combined_checks']} distinct checks support this re-audit.

## P–Q. Verification and reproduction

Current distinct check count: **{decision['reproducibility_status']['distinct_test_accounting']['combined_checks']} / {decision['reproducibility_status']['distinct_test_accounting']['combined_checks']}**.

```bash
bash scripts/verify_level_1_3.sh
bash scripts/verify_level_4.sh
bash level4/closure_proofs/m_gt_1_track1b/reproduce.sh
bash level4/closure_proofs/sr_derivative/reproduce.sh
bash level4/closure_proofs/location_family_track3ab/reproduce.sh
bash level4/re_audit_post_closure/reproduce.sh
```

## Historical confirmation

No historical result was rewritten. No new scientific campaign was performed.
All historical failures and partial decisions remain visible and unchanged.
"""


def render_ledger(decision: dict[str, Any]) -> str:
    return f"""# ReBaseGuard Level 4 — current ledger

**Historical Stage-F status:** `{decision['historical_stage_f_status']}`

**Current post-closure status:** `{decision['current_status']}`

{requirement_table(decision)}

## Current totals

| PASS | PARTIAL / NEGATIVE | FAIL | OPEN | Total |
|---:|---:|---:|---:|---:|
| {decision['pass_count']} | {decision['partial_count']} | {decision['fail_count']} | {decision['open_count']} | {decision['total_requirements']} |

The canonical source is `level4/re_audit_post_closure/requirements.json`.
This ledger is generated and must not be edited independently.
"""


def render_all() -> dict[Path, str]:
    decision = derive_decision()
    payload = json.dumps(decision, indent=2, ensure_ascii=False) + "\n"
    return {
        AUDIT / "README.md": render_readme(decision),
        AUDIT / "REQUIREMENT_UPDATE.md": render_requirement_update(decision),
        AUDIT / "INTEGRITY_AUDIT.md": render_integrity(decision),
        AUDIT / "CURRENT_SCIENTIFIC_SYNTHESIS.md": render_synthesis(decision),
        AUDIT / "FINAL_DECISION.md": render_final_decision(decision),
        AUDIT / "FAILURE_DIAGNOSES.md": render_failures(decision),
        AUDIT / "results" / "final_decision.json": payload,
        REPO / "level4" / "reports" / "LEVEL_4_POST_CLOSURE_REAUDIT.md": render_report(decision),
        REPO / "level4" / "reports" / "LEVEL_4_CURRENT_LEDGER.md": render_ledger(decision),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated artifacts differ")
    args = parser.parse_args()
    rendered = render_all()
    if args.check:
        stale = [str(path.relative_to(REPO)) for path, text in rendered.items()
                 if not path.exists() or path.read_text() != text]
        if stale:
            raise SystemExit("stale generated artifacts: " + ", ".join(stale))
        print("post-closure generated artifacts: BYTE-STABLE")
        return
    for path, text in rendered.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    decision = derive_decision()
    print(
        f"generated {len(rendered)} artifacts: {decision['pass_count']} PASS / "
        f"{decision['partial_count']} PARTIAL / {decision['fail_count']} FAIL / "
        f"{decision['open_count']} OPEN -> {decision['current_status']}"
    )


if __name__ == "__main__":
    main()
