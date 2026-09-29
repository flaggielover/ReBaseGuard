# User ruling on incident-review condition C4 (cell-308 MB r1)

Received in chat on 2026-09-29, about 02:25Z. The r2 official qualification at freeze `29b68d5e` was still running
and no qualification review existed yet. It is recorded here word for word, below the rule. It is the ruling that the
incident-independence review (`reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308.md`, condition C4) requires before any grant.
It does not replace or satisfy any other gate.

---

My ruling on reviewer condition C4 is:

C4 = ACCEPTED FOR CLOSURE-ONLY EVALUATION, WITH THE DOCUMENTED
RESULT-CHASING / INCIDENT-INDEPENDENCE LIMITATION PRESERVED.

I authorize proceeding toward a single exactly-once cell-308 target
evaluation only if all remaining frozen qualification and independent
review gates pass.

This ruling does NOT assert that route selection was fully independent
of prior cell-308 information.

The final record must preserve that:

1. incidents 01–03 remain disclosed and are not erased or downgraded;

2. the route-selection / result-chasing risk remains an explicit
   limitation;

3. the pre-existing provenance for TPT and sub-segment
   re-certification must remain part of the justification;

4. any resulting CELL308_CLOSED verdict is scientific closure only;

5. this ruling does NOT authorize adoption, floor-r2 modification,
   creation of r6, K5 closure, P5Y closure, or any publication-status
   rewrite;

6. there must be exactly one authorized target evaluation under the
   frozen protocol, and no tuning or successor variant may be selected
   from its result;

7. qualification failure or independent-review rejection still stops
   the campaign before the target;

8. this ruling itself must not be interpreted as a substitute for any
   frozen qualification, independent review, grant, execution review,
   adjudication, or adjudication review.

Do not touch the target now.

Continue the currently running r2 qualification unchanged.

If qualification passes, complete the independent qualification review
first. Only if that review is accepted and every frozen prerequisite is
satisfied may this C4 ruling be incorporated into the explicit grant.

---

## How the campaign binds it (coordinator)

* **Order.** Nothing changes until the r2 qualification finishes. If it passes, the qualification evidence is committed
  on its own. The fresh independent reviewer (brief 20) runs, and its verdict file is committed on its own. The ruling
  enters `authorization/MB308_GRANT.json` only if that verdict is QUALIFICATION_ACCEPTED and every frozen
  prerequisite of `check_grant` holds.
* **The grant records:**
  * the C4 value as given;
  * this file's path, git blob and research commit;
  * points 1–8 as grant conditions;
  * the incident-review conditions C1–C9;
  * the reviewer's G*/E* conditions.
* **Stop rule.** Qualification FAIL or QUALIFICATION_REJECTED stops the campaign before the target (point 7). The
  ruling does not override that.
* **The final record.** Incidents 01–03, H4.3b, I-a … I-e, E1′ and the MEDIUM–HIGH result-chasing rating stay in the
  record at full strength (points 1–2). So does the pre-existing provenance of TPT and of sub-segment
  re-certification: TPT's committed incident-01 disclosure in the overnight campaign, and Lemma M-U / the block
  re-certification in Theorem MB r1 (point 3). A CELL308_CLOSED verdict would be scientific closure only. It would
  not bring adoption, a floor-r2 change, r6, K5 or P5Y closure, or any publication-status change (points 4–5).
