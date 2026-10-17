# Owner decision brief r5 — Cell-308 Cloud route after reviews 59, 60, 61 and 62 (2026-10-15)

Supersedes the r1–r4 briefs, which are kept unchanged:
* r3's OD-2 named the wrong amendment revision (review 61 P12);
* r4 said revision 4's own delta review was recorded before it was (review 62 G10 / E4).

Target-free. `new_target_evaluations = 0` · `cell309_activity = none`.

Prepared by the coordinator after these reviews, and the repairs they required:
* the fresh independent review 59 (`reviews/REVIEW_CLOUD_R1_FEASIBILITY_AMENDMENT_DEV.md`);
* the fresh delta reviews 60 (`reviews/REVIEW_CLOUD_R1_DELTA_R2.md`), 61 (`reviews/REVIEW_CLOUD_R1_DELTA_R3.md`) and
  62 (`reviews/REVIEW_CLOUD_R1_DELTA_R4.md`).

## Where things stand

* MB-S r1 on the Mac stays at **NOT_DERIVED / R-FREE GATE_UNATTAINABLE** (nothing re-measured).
* The Anthropic-hosted Claude Cloud session is **HOST_UNSUITABLE for the official steps** — the coordinator's
  determination, **confirmed by the independent reviewer**. The decisive reason: the accepted rules require *you* to
  disable every automatic update from the qualification to the end of the execution window, and on a provider-managed
  image you cannot. The image did change between two sessions ten days apart (system library package, kernel build,
  OS point release, Python builds). Supporting reasons: an idle session's VM **pauses** after a few minutes (your next
  message restores the *same* VM), and a paused VM **can be reclaimed**, after which a *fresh* VM is provisioned without
  the running processes.
* The Cloud session remains useful for target-free development and review, which is what was done: a revised proposed
  Linux platform contract (`PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md`) and a repaired, tested development layer
  (revision 5).
  * The delta reviews recorded so far go up to review 62, which is of revision 4 and amendment r4.
  * Revision 5 and r5 answer review 62.
  * Their own fresh delta review was **not yet recorded** when this brief was written. It is recorded in the ledger only
    after it is made.
* An important limit, now stated plainly: on a *different* platform, the accepted route texts say the successor's
  value equals the lost MB r1 value **only on the same platform**. So a Linux route is treated as a **second, different
  draw** with risk rating **HIGH**, unless reviewers and you decide otherwise (D-RC2-SCOPE).

## Decisions that only you can make

### OD-1 — which machine, if any, should be the official host?

| option | what it means | what it needs | consequence |
|---|---|---|---|
| **V-A** | Claude **self-hosted environment**: sessions run on a runner on a Linux machine your organization operates; the campaign runs there as a systemd service | Team / Enterprise plan with self-hosted environments enabled (public beta); a persistent Linux machine you control | the service, not the session, carries the run. **V-A itself gives no host-identity guarantee** beyond your own machine. The provider's page on self-hosted environments says that when a runner reaches its retire time or releases an idle session, "the session resumes on a fresh runner when the user sends their next message" (code.claude.com/docs/en/self-hosted-environments, read 2026-10-14 ~18:52Z; the coordinator's extract is not stored verbatim in the repository). So the machine must be one persistent host you pin and attest (H1, H8), and the campaign must run as a service on it, not inside a session |
| **V-B** | any persistent Linux machine you own or rent, optionally driven via Remote Control | the machine and access | same H1–H8 requirements |
| **V-C** | **close the Cloud route**; MB-S r1 stays at its NOT_DERIVED stop | nothing | no further Cell-308 work under MB-S unless a later ruling opens another route |
| other | e.g. a Mac with more memory | your ruling | its own S4 route preparation (it would still be a different host) |

For V-A or V-B you would also be the one to disable every update vector (H3) and to attest the machine's identity and
lifetime (H1, H5, H6, H8).

### OD-2 — commission the formal route / governance review of amendment r5?

Reviews so far were of drafts. Acceptance needs a formal route / governance review, a fresh S12 risk rating (presumed
HIGH), the open rule decisions with the reviewer (§4 of the amendment — 21 of them; for each option it states whether
it would amend an accepted text, add a new rule or number, or neither), and your design approval.

The formal review also has to fix how a host attestation is accepted (D-HOST-LIFETIME). Review 62 requires that the
independence of that acceptance be decided there. Today's code checks only the commit order. The review must still add:
* a ledger line that binds the accepting review;
* a reviewer who is not the coordinator.

Yes / no / after OD-1.

### OD-3 — authorize the RC2 reproduction check (gate L-DET), once a host exists?

It re-runs MB r1's committed **non-target** qualification cases on the new platform and requires an **exact** match.
A mismatch stops the route on that platform (and a further host would need your new ruling with the failure
disclosed). An exact match shows only that the platform reproduces those non-target records; it does **not** restore
the argument that the successor's value equals the lost run's. The protocol is pre-registered (amendment §5): exact
match, no tolerance, **no repeat** of a failed or incomplete attempt, no switching hosts after a mismatch without your
new ruling. It needs OD-1, an accepted route review that includes the list of reference records and their checksums,
and fixed interpreter and comparison tooling first.

## What is not being asked

No target evaluation, freeze, grant, qualification, S1 ruling or scientific adoption. No threshold is changed. Cell 309
is untouched.
