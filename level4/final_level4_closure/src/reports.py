#!/usr/bin/env python3
"""Generate all non-final terminal audit reports from canonical JSON."""
from __future__ import annotations

import argparse
from pathlib import Path

from config import BASE, RESULTS, ROOT, load


def requirement_ledger(canonical: dict, ledger: dict) -> str:
    counts = ledger["counts"]
    lines = [
        "# Terminal Level-4 requirement ledger", "",
        "Generated from the canonical `requirements.json`; no total is manually maintained.", "",
        f"Current tally: **{counts['PASS']} PASS · {counts['PARTIAL']} PARTIAL · "
        f"{counts['FAIL']} FAIL · {counts['OPEN']} OPEN**.", "",
        "| ID | Requirement | Class | Mandatory | Stage F | Previous final | Current | Blocks | Evidence | Limitations |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in canonical["requirements"]:
        evidence = "<br>".join(f"`{path}`" for path in row["evidence_paths"])
        limits = "<br>".join(row["surviving_limitations"]) or "—"
        lines.append(
            f"| {row['id']} | {row['requirement']} | {row['classification']} | "
            f"{'YES' if row['mandatory'] else 'NO'} | {row['stage_f_status']['label']} | "
            f"{row['previous_final_audit_status']} | **{row['current_status']}** | "
            f"{'YES' if row['current_blocking'] else 'NO'} | {evidence} | {limits} |"
        )
    return "\n".join(lines) + "\n"


def evidence_map(evidence: dict) -> str:
    lines = [
        "# Terminal evidence map", "",
        "Every status-changing campaign targets exactly one original row.", "",
        "| Campaign | Original row | Audit | Evidence | Surviving limitations |",
        "|---|---|---|---|---|",
    ]
    for campaign in evidence["campaigns"]:
        paths = "<br>".join(f"`{path}`" for path in campaign["evidence_paths"])
        limits = "<br>".join(campaign["surviving_limitations"])
        lines.append(
            f"| {campaign['campaign']} | {campaign['target_requirement']} | "
            f"**{campaign['status']}** | {paths} | {limits} |"
        )
    return "\n".join(lines) + "\n"


def status_transitions(canonical: dict) -> str:
    lines = [
        "# Final Level-4 status transitions", "",
        "Historical scientific results and current requirement status are separate fields.", "",
        "| ID | Stage-F status | Current status | Campaign | Reason |",
        "|---|---|---|---|---|",
    ]
    for row in canonical["requirements"]:
        if row["changed_since_stage_f"]:
            lines.append(
                f"| {row['id']} | {row['stage_f_status']['label']} | **{row['current_status']}** | "
                f"`{row['transition_campaign']}` | {row['transition_reason']} |"
            )
    lines += ["", (
        "For L4R-12, the scientific result remains negative (`MATHEMATICAL, NOT OPERATIONAL`) "
        "while the investigational requirement becomes PASS because the frozen research question is completed."
    ), ""]
    return "\n".join(lines)


def claim_firewall(canonical: dict) -> str:
    return """# Terminal Level-4 claim firewall

## Allowed

ReBaseGuard closes its internally frozen Level-4 research program only if the
final generator confirms that all 16 mandatory requirements and every
engineering gate pass. One nonmandatory strong extension may remain partial.

- Gamma_CUSUM is Arb-certified above two; Gamma_SR is not.
- The deterministic period-2 result concerns the conditional-mean skeleton.
- D4 is a protocol-specific deterministic local-stability map.
- Gamma_SR > 2 is confirmatory numerical evidence.
- The L4R-12 operational-crossing result is negative under the frozen protocol.
- External validation is semi-real and P2 safety remains regime-dependent.
- Novelty is the scoped N2 partial-overlap/claims-narrowed conclusion.

## Prohibited

- all research questions solved;
- universally valid, universally safe, distribution-free, detector-independent;
- production proven, production deployed, or peer reviewed;
- novel, first, first-ever, unprecedented, or absolute priority;
- SR rigorously certified or SR-GAMMA-CERTIFIED;
- an operational phase transition was proved;
- historical failures or partial campaigns were retrospectively successful.
"""


def open_items(canonical: dict) -> str:
    lines = ["# Remaining optional and open work", ""]
    for item in canonical["open_nonblockers"]:
        lines += [
            f"## {item['id']} — {item['status']}", "",
            item["reason"], "",
            *[f"- `{path}`" for path in item["evidence_paths"]], "",
        ]
    lines += [
        "A closed Level-4 verdict would not imply `SR-GAMMA-CERTIFIED`.", "",
        "L4R-13 remains a nonmandatory PARTIAL strong extension; it is a limitation, not an OPEN item or mandatory blocker.", "",
    ]
    return "\n".join(lines)


def readme(ledger: dict) -> str:
    return f"""# Final Level-4 closure audit

This isolated namespace mechanically recomputes the current global Level-4
status from the protected original 18-row ledger and all authorized later
same-requirement closures. It does not modify historical audits and runs no new
science.

Canonical ledger candidate: `{ledger['ledger_candidate_verdict']}`. The final
verdict remains gated on A1-A32, offline byte stability, protected history, and
both authoritative repository verifiers.

Reproduce with:

```bash
bash level4/final_level4_closure/reproduce.sh
```
"""


def outputs() -> dict[Path, str]:
    canonical = load(BASE / "requirements.json")
    evidence = load(RESULTS / "evidence_audit.json")
    ledger = load(RESULTS / "ledger_derivation.json")
    return {
        BASE / "README.md": readme(ledger),
        BASE / "REQUIREMENT_LEDGER.md": requirement_ledger(canonical, ledger),
        BASE / "EVIDENCE_MAP.md": evidence_map(evidence),
        BASE / "STATUS_TRANSITIONS.md": status_transitions(canonical),
        BASE / "CLAIM_FIREWALL.md": claim_firewall(canonical),
        BASE / "OPEN_ITEMS.md": open_items(canonical),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, content in outputs().items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(content)
    if stale:
        print("terminal reports stale: " + ", ".join(stale))
        return 1
    print("terminal core reports: byte-stable" if args.check else "terminal core reports generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
