BRIEF 63 — reviewCLOUD_R1_DELTA4: fresh independent DELTA review of revision 5 (dev layer) and amendment r5, made
after the delta review 62 (Cell 308, MB-S successor, S4 changed branch, Cloud route r1). Issued 2026-10-15 by the
coordinator of a Claude Cloud session. Pasted inline to the reviewer verbatim.

=== ROLE
You are a fresh, independent reviewer. You wrote none of the material and none of reviews 59, 60, 61 or 62. You review;
you do not repair, commit, push or edit any repository file. Write your review to the single output file named below.

=== REPOSITORY AND COMMITS
Checkout: /home/user/ReBaseGuard (git), branch claude/cell-308-github-state-skb1g0. Review the delta from cd86c326
(reviewed by review 62) to the branch HEAD (`git rev-parse HEAD`; it carries revision 5, its tests, its recorded
mutation run, amendment r5 and owner brief r5). Namespace NS = level4/closure_proofs/p5y_k5_cell308_research/. The
historical candidate 142d97a90a1c3fafff394044aa1448674f7a633c may be read only with `git show 142d97a9:<path>`.

=== INPUT: THE REVIEW BEING ANSWERED
NS/reviews/REVIEW_CLOUD_R1_DELTA_R4.md (review 62: DELTA_ACCEPTED_WITH_CONDITIONS; AMENDMENT_DRAFT_R4
FIT_WITH_CONDITIONS; DEV_CODE_R4 FAIL_CLOSED_WITH_DEFECTS; new findings G1-G11; conditions E1-E4 in its §6). Its
scratch: NS/reviews/scratch_CLOUD_R1_DELTA3/ (scripts stored as *.py.txt; copy them to your scratch dir and rename
before running). Reviews 59-61 and their scratch directories are background.

=== WHAT TO REVIEW (at HEAD)
D1. NS/streams/CLOUD_R1_LINUX_DEV/ revision 5: lx_platform.py, lx_inventory.py, tests/test_lx_platform.py,
    tests/run_mutants.py, results/TEST_RUN.json, results/MUTANTS_RUN.json, README_DEV_ONLY.md.
D2. NS/governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md (its §13 maps review 62's
    findings) and OWNER_DECISION_BRIEF_CLOUD_R1_R5.md.
D3. The ledger lines added after cd86c326 in NS/ledger/TARGET_INTEGRITY_LEDGER.jsonl and NS/ledger/briefs/ changes.

=== ACCEPTED SOURCES YOU MAY READ to check fidelity
NS/governance/SUCCESSOR_GOVERNANCE_308*.md, NS/governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md,
NS/governance/CONSTANTS_RATIFICATION_MBS308.md, NS/registry/SUCCESSOR_ROUTE_AUDIT_308*.md,
NS/reviews/REVIEW_SUCCESSOR_ROUTE_308.md, NS/reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md,
NS/governance/new_host_route_cloud_r1/ROUTE_PREPARATION.md, the candidate code / tests via git show.

=== EXPOSURE RESTRICTIONS (binding; governance S13, S10)
Do NOT open, grep into or otherwise read: NS/audit/EXECUTION_INTERRUPTION_ASSESSMENT*, NS/audit/INCIDENT_AUDIT*,
NS/reviews/REVIEW_EXECUTION_INTERRUPTION*, anything under level4/closure_proofs/p5y_k5_cell308_mb_r1/postexec/ or any MB
r1 target-run record, NS/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md. Do not read any Cell-309 branch, file or record
(branch names in `git branch -a` are the only permitted contact). Disclose any accidental contact.

=== WHAT YOU MAY RUN
Target-free, read-only or synthetic only: git read commands, file reads, and from NS/streams/CLOUD_R1_LINUX_DEV:
`python3 -B -m unittest discover -s tests -v` and `python3 -B tests/run_mutants.py` (NO output-file argument; do not
write results/). Scratch scripts and extra mutants ONLY under
/tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review63/, against a COPY of
lx_platform.py there (the suite honours LX_PLATFORM_DIR). You may re-run reviews 59-62's probes and mutants against a
copy of revision 5 (note: revision 5 removed the `readings`, `view_complete` and `pin_point(modules)` parameters; tests
change trust-relevant inputs only by patching module attributes, and your probes may do the same in your scratch
copy). Synthetic git repositories for acceptance-set probes go under your scratch dir. Never run candidate code, a science module, a decoy, a qualification case, quarantine
guards against cells, or anything that evaluates a cell, drift or certificate. No installs, no setting changes. Note:
`unshare` probes are permitted (target-free) if they need no installation.

=== QUESTIONS
Q1. For EACH of review 62's findings G1-G11 and conditions E1-E4 (its §6): RESOLVED / PARTIALLY RESOLVED / NOT
    RESOLVED / CARRIED-AS-CONDITION (explicitly carried into the formal review, and acceptable to carry)? Evidence.
Q2. Fail-closed audit of revision 5, adversarially: any path where a failed, absent, unrecognised, rejected or
    caller-asserted input yields PASS, ALIVE, AC, a numeric allowance, a complete /proc view, CLEAN, an accepted
    attestation, or an update unit "not enabled". Re-run review 62's probes (incl. G1-G15 of its Q2 table and the
    unshare probes). Try in particular to get an attestation accepted by a file outside the fixed set, by text written
    before or together with the attested blob, or past a negative verdict anywhere under reviews/. Write at least three
    NEW mutants of your own against revision 5; report killed / survived.
Q3. Regression: did any revision-5 change break a property that was correct in revision 4 (e.g. the zombie rule, the
    pins, durable_write, the R01-R10 / X01-X09 / Y01-Y09 kills)? Did anything become stricter in a way that makes a gate unattainable on a
    legitimate host without saying so (state it as a NOTE, not a defect, if it is a deliberate fail-closed choice)?
Q4. Amendment r5: are the §3 rows (esp. L-UPD, L-EXCL, L-PIN, L-LIFE, H6 and the "Caller inputs" paragraph) now
    exactly what the code does? Are the §4 labels complete (21 rows) and equal to the code's OPEN_DECISIONS? Is the
    acceptance mechanism's independence carried as an explicit D-HOST-LIFETIME item (E2)? Any [ACCEPTED] quotation not
    verbatim? Does owner brief r5 state accurately which reviews are recorded (E4)?
Q5. Records: recompute the sha256 values bound in the new ledger lines; check TEST_RUN.json / MUTANTS_RUN.json against
    the committed files' hashes and against a fresh run; check that the r1-r4 drafts, the r1-r4 owner briefs, ledger lines
    1-472 and the reviewed files (reviews 59-62 and their scratch) stay byte-unchanged.

=== OUTPUT
ONE Markdown file: /tmp/claude-0/-home-user-ReBaseGuard/000d3115-48ec-594a-b3d0-49b4980206d0/scratchpad/review63/REVIEW_CLOUD_R1_DELTA_R5.md
  1. Header: reviewer = "reviewCLOUD_R1_DELTA4 (fresh agent, brief 63)", date, delta reviewed (with HEAD sha).
  2. Exposure disclosure.
  3. Verdict lines, exactly:
     DELTA: one of DELTA_ACCEPTED / DELTA_ACCEPTED_WITH_CONDITIONS / DELTA_REJECTED
     AMENDMENT_DRAFT_R5: one of FIT_FOR_FORMAL_ROUTE_REVIEW / FIT_WITH_CONDITIONS / NEEDS_REVISION
     DEV_CODE_R5: one of FAIL_CLOSED_CONFIRMED / FAIL_CLOSED_WITH_DEFECTS / NOT_FAIL_CLOSED
     State plainly that no verdict here accepts the amendment.
  4. Table G1-G11, E1-E4 with status and evidence.
  5. Answers Q2-Q5.
  6. New findings H1..Hn with severity BLOCKING / MAJOR / MINOR / NOTE, location, required correction.
  7. Your mutants: diff and killed/survived.
Be specific and adversarial; no praise; say UNVERIFIED where you cannot verify.
When finished, reply with only: the output path, the three verdict lines, and the count of new findings by severity.
