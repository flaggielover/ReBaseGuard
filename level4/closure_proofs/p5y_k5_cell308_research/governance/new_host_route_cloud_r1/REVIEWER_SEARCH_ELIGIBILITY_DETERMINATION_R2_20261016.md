# Eligibility determination, revision r2: the excluded-file searches disclosed by reviewerS12 and reviewerFR2 (Cell-308 Cloud route r1)

**Status: COORDINATOR'S PROPOSED DETERMINATION · REVISION r2 · CERTIFIES NO ABSENCE OF EXPOSURE · OWNER ADOPTION
REQUIRED.** This revision answers external B1 finding X1 (`reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`,
`cf1a4b18…8e41`, lines 134–146).

**Precedence.** This revision supersedes `REVIEWER_SEARCH_ELIGIBILITY_DETERMINATION_20261016.md` (r1, `b1b4cc10…91a6`)
in whole, except r1 §1 (the restriction), which r2 §1 repeats unchanged. r1 is preserved unchanged as a historical
record. Where r1 and r2 differ, r2 governs. In particular, r1's §3 "**Verified:**" block and its §5 items 1 and 4 are
**withdrawn**.

Nothing here is a new investigation. No excluded file was fetched, opened, grepped, hashed or listed to write it, and no
transcript was read. It restates what the existing evidence supports and attributes each statement to its source.
`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The restriction (unchanged from r1 §1)

Briefs S12 and FR2 (`ledger/briefs/S12_RISK_REVIEW_CLOUD_R1.txt` `d46c19f7…710d`;
`ledger/briefs/FR2_formalROUTE_CONDITIONS_CHECK_CLOUD_R1.txt` `77cf992d…9589`) said: "Do NOT open, grep into, hash or
otherwise read" the excluded files.

## 2. Two different events: a process scanning bytes, and content reaching a context

These are kept apart throughout this file.

| term | meaning here |
|---|---|
| **byte scan by a process** | A process the reviewer started (`grep`, `find`, `ls`, `git`) read the bytes, or the directory entries, of an excluded path. The process saw the content. What the reviewer can learn depends only on what the process emitted: its output lines, its exit status, error messages, and anything the harness saved. |
| **content in a reviewer's context** | Any part of an excluded file's content, or anything derived from it, reached the reviewer's context in any form: a printed line, a count, a file name list (`-l`), a "binary file matches" notice, an error text, a harness-saved tool result, or a later summary of any of these. |
| **opened** (r1's word) | r1 used "opened" for a direct read or display call on the path. A grep that scans a file is not "opening" in that sense, yet it is a byte scan. r2 does not use "not opened" as evidence about byte scans. |

A byte scan does not imply content in context. But the absence of content in context can be shown only from a complete
record of what the process emitted and of everything the reviewer then saw.

## 3. What is established, and on what

| statement | status | source |
|---|---|---|
| reviewerS12 ran one recursive `grep -rn "Complete the fresh S12"` over `governance`, `reviews` and `ledger/briefs` of its pinned tree. That scanned the bytes of the excluded `REVIEW_EXECUTION_INTERRUPTION*` and `INCIDENT_INDEPENDENCE_REVIEW_MBS308.md` | **ESTABLISHED** (the reviewer's own disclosure) | `reviews/REVIEW_S12_RISK_CLOUD_R1.md` lines 49–54 |
| reviewerFR2 ran one recursive `grep -rn "Complete the fresh S12"` over all of NS (`*.md`, `*.txt`). That scanned the bytes of `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`, `audit/*`, `reviews/REVIEW_EXECUTION_INTERRUPTION*`, `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md` and `governance/K5_AUDIT_EXCL_309.md` | **ESTABLISHED** (the reviewer's own disclosure) | `reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR2.md` lines 62–74 |
| reviewerFR2's `find` walked the directory entries of excluded directories; its listing of `governance/` showed the name `K5_AUDIT_EXCL_309.md`; reviewerS12's listing of `ledger/` showed excluded file names | **ESTABLISHED** (name-level contact, disclosed) | FR2 lines 71–74; S12 lines 55–56 |
| These searches breached the briefs, which prohibited "grep into" | **ESTABLISHED** | §1, and the rows above |
| reviewerS12 reports that no line of an excluded file matched and nothing from them was printed | **REPORTED by the reviewer**; not independently verified | S12 lines 53–54 |
| reviewerFR2 reports that the grep printed matches only from `FR1_DISPOSITION_20261016.md`, and that no line of any excluded file was printed or seen | **REPORTED by the reviewer**; not independently verified | FR2 line 70 |
| The search patterns were fixed literals: a sentence of the owner's instruction, and (FR2) the phrase "first in effect". They are not target-related. A scan for them, even with no output, still tells the process whether each scanned file contains the literal | **ESTABLISHED as to the patterns** (they are recorded); the information content stated is a property of grep | S12 line 54; FR2 lines 46, 63 |

**A further discrepancy (UNVERIFIED).** r1 §2 attributes to reviewerFR2 a command `grep -rn "first in effect"
$N/governance/*.md` "as recorded in the transcript", over every governance `.md`. FR2's own disclosure (line 46)
describes "a grep for "launchd", "first in effect" and section headings" against brief R2. The two descriptions differ in
scope. They cannot be reconciled without the transcript. Neither account is asserted to be false. The broader scope is
used where it matters, because it covers more excluded bytes.

## 4. What the coordinator's transcript audit adds, and its limits

The coordinator of the 2026-10-14 session ran two scripts over the three reviewers' recorded transcripts. They are
committed as text in `reviews/scratch_SEARCH_ELIGIBILITY_AUDIT/` (r1 §3 gives their sha256 values). As r1 reports them:
* 0 direct `Read` calls on an excluded or MB r1 path;
* among tool-output lines in `path:line:` form (FR1 16, S12 66, FR2 3), 0 from an excluded or MB r1 path.

**Status: COORDINATOR-REPORTED.** These results describe what the coordinator's scripts found in transcripts that the
coordinator's environment stores. They are not independent verification:
* **Completeness and integrity of the transcripts: UNVERIFIED.** They are held in the environment of the party whose
  process is being checked. No party outside that environment has examined them.
* **Output forms outside the scripts' scope: UNVERIFIED.** The path match covers `grep -n`-style lines only. Counts,
  `-l` file lists, `-c` output, "binary file matches" notices, error messages, harness-saved tool results and summaries
  were not in scope.
* **The scripts themselves** are committed as text. This file does not re-run them. B1 did not either (B1 lines 23–25).

So the supportable statement is: **in the output forms the scripts covered, the coordinator's audit found no excluded
output.** It is not: "no excluded content entered any reviewer's context".

## 5. UNVERIFIED propositions (stated, not resolved)

1. That the recorded transcripts are complete and unaltered.
2. That no content of any excluded file reached reviewerS12's or reviewerFR2's context **in any output form or
   channel**.
3. **The resulting E1″ holder status** of reviewerS12 and reviewerFR2. It is neither established nor excluded.
4. What either reviewer knew from other sources. Each one's prior exposure rests on its own self-declared phase-1
   statement.
5. The exact scope of reviewerFR2's "first in effect" search (§3).

## 6. Proposed determination r2 (replaces r1 §5)

1. **The breach is established and recorded.** Both reviewers ran prohibited recursive searches that scanned the bytes
   of excluded files (§3).
2. **No certification about exposure.** The available evidence does not establish that restricted content reached
   either reviewer's context. It does not establish that none did. Holder status stays **UNVERIFIED** (§5). No absence
   of E1″ exposure is certified, proposed for certification or presented for adoption.
3. **Consequences, which hold whatever the unresolved facts are:**
   * Both reviews stay **advice** only. Their weight is reduced by the breach.
   * Neither review may be cited as satisfying any requirement for an independent, external or owner-launched
     reviewer, or for a non-holder.
   * **Neither reviewer takes any later role on this route.** That covers acceptance, rating, reading, provenance,
     implementation, caps, qualification and review roles (procedure r3 §2 already excludes both).
   * For any rule that turns on non-holder status, each is treated as **holder status UNVERIFIED**, never as a
     verified non-holder.
4. **No gate on this route depends on resolving §5**, given the consequences in item 3. A stronger conclusion would
   need a separately authorized examination by an eligible examiner outside the coordinator's environment, with
   sufficient evidence (for example, transcripts the owner supplies directly), followed by a further revision of this
   determination. None is commissioned here, and none is needed for any gate.
5. **Briefs from now on** prohibit recursive search over the research namespace outright, and give an explicit
   allowlist of readable paths (as the external briefs B1–B3 already do).
6. **Owner adoption.** The determination takes effect only through the owner's statement 1 in
   `OWNER_DECISION_PACKAGE_R4_20261016.md` §2 item 6. That item records the breach, these limits, the advisory standing
   and the no-later-role restriction. It certifies nothing about holder status.

## 7. What was not done in writing r2

* No excluded file was fetched, opened, grepped, hashed or listed.
* No transcript was read, requested or audited, and the r1 scripts were not re-run.
* No evidence was sought to make a stronger conclusion possible. B1 X1 and the owner's release both bar that.
