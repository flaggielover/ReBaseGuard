# Eligibility determination: the excluded-file searches disclosed by reviewerS12 and reviewerFR2 (Cell-308 Cloud route r1)

**Status: COORDINATOR'S PROPOSED DETERMINATION · VERIFIED FACTS STATED SEPARATELY · OWNER ADOPTION REQUIRED.**
A disclosure is not proof that a restriction held. This file states:
* what the briefs prohibited;
* what was done;
* what could be independently checked, and how;
* what the check cannot establish;
* the proposed determination.

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The restriction

Briefs S12 and FR2 (`ledger/briefs/S12_RISK_REVIEW_CLOUD_R1.txt` `d46c19f7…710d`;
`ledger/briefs/FR2_formalROUTE_CONDITIONS_CHECK_CLOUD_R1.txt` `77cf992d…9589`) said: "Do NOT open, grep into, hash or
otherwise read" the excluded files.

## 2. What was done (from the reviewers' own disclosures and their recorded tool calls)

| reviewer | command (as recorded in the transcript) | files whose bytes were scanned |
|---|---|---|
| reviewerS12 | `grep -rn "Complete the fresh S12" --include=*.md --include=*.txt governance reviews ledger/briefs` (in its pinned tree) | everything under `reviews/`, including the excluded `REVIEW_EXECUTION_INTERRUPTION*` and `INCIDENT_INDEPENDENCE_REVIEW_MBS308.md` |
| reviewerFR2 | (1) `grep -rn "first in effect" $N/governance/*.md`; (2) `grep -rn "Complete the fresh S12" $N --include=*.md --include=*.txt \| grep -v p5y_k5_cell308_mb_r1` ($N = the research namespace of its pinned tree) | (1) every governance `.md`, including the file named `K5_AUDIT_EXCL_309.md`; (2) every `.md` / `.txt` in the research namespace, including `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`, `audit/*`, `reviews/REVIEW_EXECUTION_INTERRUPTION*` and `INCIDENT_INDEPENDENCE_REVIEW_MBS308.md` |

**The restriction was breached.** "Grep into" was expressly prohibited. This is a procedural breach of the briefs,
whatever the search returned.

## 3. What was independently checked, and how (value-free)

The coordinator audited the three reviewers' recorded transcripts (FR1, S12, FR2) with two scripts. The scripts print
only:
* counts;
* path names;
* the command text the agents themselves wrote.

They print no file content and no command output. They are recorded in `reviews/scratch_SEARCH_ELIGIBILITY_AUDIT/`
(`path_audit.py.txt` `708619d1…14d2`, `cmd_audit.py.txt` `bcb8d4bc…e2b9`, output `path_audit_output.jsonl`
`3eae7330…d220`).

| check | FR1 | S12 | FR2 |
|---|---|---|---|
| transcript sha256 | `b68ae929…1523` | `2fe30c8d…5cd8` | `9234fd36…2ec2` |
| `Read` calls on an excluded or MB r1 path | 0 | 0 | 0 |
| tool-output lines in `path:line:` form | 16 | 66 | 3 |
| of these, lines from an excluded path | **0** | **0** | **0** |
| of these, lines from an MB r1 path | 0 | 0 | 0 |
| recursive greps over the repository tree | 0. Its "309" greps ran over its own saved ref listing and printed only counts and non-309 lines, as disclosed | 1 (above) | 2 (above) |

**Verified:**
* No line of any excluded file entered any of the three reviewers' context through a tool result.
* No excluded file was opened.

The search patterns were fixed literals written by the coordinator: a sentence of the owner's instruction, and the
phrase "first in effect". They are not target-related. So, for each scanned excluded file, the only information
obtained is the single fact that it contains no line matching those literals.

## 4. What this check cannot establish

* It relies on the recorded transcripts being complete and unaltered. They are stored by the coordinator's environment,
  so the coordinator could, in principle, have altered them. Their sha256 values are recorded now.
* It cannot show what a reviewer "knew" from other sources. Each reviewer's prior exposure rests on its own phase-1
  disclosure.
* The path match covers `grep -n`-style output lines. Output in any other form was not in scope. No other command of
  the three reads an excluded path (the command audit).

## 5. Proposed determination

1. **No E1″ exposure arose from the searches.** No excluded content entered the reviewers' context (§3). reviewerS12
   and reviewerFR2 are not E1″ holders by this event.
2. **The procedural breach is recorded, and it reduces the weight of their reviews.**
   * Both reviews stay valid advice.
   * Neither reviewer may take any later role on this route (procedure r3 §2 already excludes them).
   * Neither review may be cited as satisfying a requirement for an independent or owner-launched reviewer.
3. **Briefs from now on** prohibit recursive search over the research namespace outright, and require an explicit
   allowlist of readable paths (the external handoffs below do so).
4. **Owner adoption.** This determination is the coordinator's proposal. It takes effect only with the owner's
   decision, statement 1 of `OWNER_DECISION_PACKAGE_R3_20261016.md`. The owner may also ask the external conformance
   reviewer (handoff B1) to re-check §3 from the recorded transcripts. That reviewer would run the same value-free
   scripts on the transcripts, which the owner would need to supply. They live in this session's storage and cannot be
   published without reading them.
