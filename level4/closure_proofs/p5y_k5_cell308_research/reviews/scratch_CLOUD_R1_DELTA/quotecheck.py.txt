"""Word-for-word check of the [ACCEPTED] / [PREPARATION] quotations of amendment r2 and the errata against their sources
(whitespace collapsed; '**' emphasis and markdown '> ' quote markers removed on both sides). Read-only."""
import json
import re
import sys
from pathlib import Path

NS = Path("/home/user/ReBaseGuard/level4/closure_proofs/p5y_k5_cell308_research")


def norm(s):
    s = s.replace("**", "")
    s = re.sub(r"^\s*>\s?", "", s, flags=re.M)
    s = re.sub(r"^\s*[*-]\s+", "", s, flags=re.M)
    return re.sub(r"\s+", " ", s).strip()


Q = [
    ("HOST row", "registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md",
     "moving the successor to another host | EXCLUDED unless RC2 is discharged there | the determinism argument binds the platform. A different host means the S4 changed branch, and its own exact reproduction of MB r1's r3 records would be required"),
    ("DR2 (amendment 2.1 part)", "registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E1.md",
     "The host's automatic OS and software updates must be disabled for that window. This is an operator action by the user; the campaign never changes system settings."),
    ("DR2 (erratum E1 full)", "registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E1.md",
     "The no-update rule covers the whole post-marker window, up to the 7-day resume deadline. The host's automatic OS and software updates must be disabled for that window. This is an operator action by the user; the campaign never changes system settings."),
    ("MBS-5(b)", "governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md",
     "any evaluation of cell 308 after the MB-S marker, of any route, starts at a risk rating not lower than HIGH"),
    ("route A1 1", "registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md",
     "Determinism is conditional on RC2. The value of MB-S equals the value the lost MB r1 run would have produced only on the same platform: interpreter, libpython, OS build and architecture. The A0 certifier review's N2 says the float proposals use libm. Off that platform the S4 \"changed\" branch applies."),
    ("route A1 3 MBR1_REPRO", "registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md",
     "The MBR1_REPRO qualification case. It re-runs MB r1's committed non-target r3 cases through the successor's code: QC02 (decoy 297), QC03 (decoy 316, blocks 0–2), and the QC04 validation-drift ladder pair. It requires exact equality of every certified leaf, timing stripped, with MB r1's committed r3 records. Any mismatch means STOP and the S4 changed branch. Qualification review E8 applies: these records are never placed next to a cell-308 quantity."),
    ("brief R2 9 not settled", "governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md",
     "Which of the two governs is not settled in the texts I read."),
    ("incident review line 129", "reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md",
     "If any of N1–N4 fails, the successor is on S4's changed branch. Its value is then a second, different draw, the decisive argument is lost, and this rating does not apply (trigger T1 in Q4)."),
    ("incident review T1", "reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md",
     "T1. Any of N1–N4 fails at qualification or at any resume (the science is then \"changed\" under S4)."),
    ("S5", "governance/SUCCESSOR_GOVERNANCE_308.md",
     "Liabilities carried forward verbatim. Incidents 01–03, H4.3b, I-a…I-e with E1′, the F2/F3 exposures, the quarantine breach, single-implementation inputs, and result-chasing MEDIUM–HIGH. The C4 conditions U1–U8 are the minimum for any new ruling."),
    ("S7", "governance/SUCCESSOR_GOVERNANCE_308.md",
     "Exactly-once, again. The successor has its own single marker and grant. A failure after its marker gives its own frozen INDETERMINATE-class outcome. Any further successor needs a further governance process and user ruling."),
    ("S10", "governance/SUCCESSOR_GOVERNANCE_308.md",
     "Isolation from cell 309. Cell 309 is EXTERNALLY_IN_PROGRESS in a separate session. No inspection for continuation, duplication, review, proxy, qualification, authorisation or evaluation of cell 309."),
    ("S13", "governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md",
     "S13 (GC-6). Exposure. A formal exposure addendum (E1″ in `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`) names, never values, the MB r1 target-run runtime and host observations, where they are recorded, and who holds them. No successor brief contains them or points to REVIEW_EXECUTION_INTERRUPTION §4b. The successor's route, implementation and caps agents have not seen them. The builder was instructed so on 2026-09-29 ~20:40Z, and must disclose any prior reading. The caps decision is justified from decoy and qualification evidence only."),
    ("E1 D2", "governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1_ERRATUM_E1.md",
     "The successor builder was instructed about GC-6 at 2026-09-29 18:39:04Z, not \"~20:40Z\". The same applies to A1 §4 S13 (\"2026-09-29 ~20:40Z\")."),
    ("E1 D3", "governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1_ERRATUM_E1.md",
     "The holder list is extended by: reviewGOV, the successor-governance reviewer, who read REVIEW_EXECUTION_INTERRUPTION §4b's per-coalition CPU figures; the step-8 adjudication reviewer (reviewADJ), who reads the recovery chain and the execution review. Neither may take a successor route, implementation or caps role (S13)."),
    ("PREPARATION", "governance/new_host_route_cloud_r1/ROUTE_PREPARATION.md",
     "The existing R-ALLOW path-class rules and R-FREE memory definition may not transfer to Linux. If unchanged semantics cannot be supported, stop and put the exact incompatibility to an independent route reviewer and the owner; do not substitute a Linux metric or path policy silently."),
    ("R-FREE fragment", "governance/CONSTANTS_RATIFICATION_MBS308.md", "measured as the driver's own `free_memory_bytes` (vm_stat"),
    ("R-MEM step 1 fragment", "governance/CONSTANTS_RATIFICATION_MBS308.md", "under the launchd launcher"),
    ("brief R2 9 launchd fragment", "governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md", "only under the launchd launcher"),
    ("S6 fragment (H2)", "governance/SUCCESSOR_GOVERNANCE_308.md",
     "a launcher that survives the hosting app's death and the launcher's parent's death"),
    ("S6 fragment (H2) in A1", "governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md",
     "a launcher that survives the hosting app's death and the launcher's parent's death"),
    ("brief R2 7.8 launched by the operator", "governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md", "launched by the operator"),
    ("brief R2 7.8 platform change", "governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md",
     "A platform change gives close-indeterminate"),
    ("S15 fragment", "governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md", "later-found MB r1 evidence is a permanent STOP"),
    ("R-ALLOW 39 names", "governance/CONSTANTS_RATIFICATION_MBS308.md", "the current 39 names"),
    ("route A1 1 'only on the same platform'", "registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md", "only on the same platform"),
]

res = []
for name, src, q in Q:
    text = (NS / src).read_text()
    hit = norm(q) in norm(text)
    res.append({"quote": name, "source": src, "verbatim": hit})
print(json.dumps(res, indent=1, ensure_ascii=False))
