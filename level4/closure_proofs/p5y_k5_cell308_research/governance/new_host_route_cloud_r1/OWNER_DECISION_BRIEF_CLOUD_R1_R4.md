# Owner decision brief r4 — Cell-308 Cloud route after brief61 Codex review (2026-10-15)

Supersedes the r1, r2 and r3 briefs (kept unchanged). **PROPOSED · NOT ACCEPTED · NOT IN FORCE.** Target-free.
`new_target_evaluations = 0` · `cell309_activity = none`. Prepared after reviews 59 and 60 and the fresh brief-61
Codex review of immutable revision 3 (`reviews/REVIEW_CLOUD_R1_DELTA_R3_CODEX.md`), which returned DELTA_REJECTED /
AMENDMENT_DRAFT_R3 NEEDS_REVISION / DEV_CODE_R3 NOT_FAIL_CLOSED. This repair brief asserts no passed revision-4 tests,
accepted follow-up review, owner decision or operational authority.

## Where things stand

* MB-S r1 on the Mac stays at **NOT_DERIVED / R-FREE GATE_UNATTAINABLE** (nothing re-measured).
* The Anthropic-hosted Claude Cloud session is **HOST_UNSUITABLE for the official steps** — the coordinator's
  determination, **confirmed by the independent reviewer**. The decisive reason: the accepted rules require *you* to
  disable every automatic update from the qualification to the end of the execution window, and on a provider-managed
  image you cannot. The image did change between two sessions ten days apart (system library package, kernel build,
  OS point release, Python builds). Supporting reasons: an idle session's VM **pauses** after a few minutes (your next
  message restores the *same* VM), and a paused VM **can be reclaimed**, after which a *fresh* VM is provisioned without
  the running processes.
* The Cloud session remains useful for target-free development and review. The current proposal is amendment r4
  (`PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R4.md`), with a scoped revision-4 development repair. Exact-input Linux
  validation and independent follow-up review remain to be recorded; this brief does not claim they passed.
* The raw memory helpers accept a strict boolean caller contract and do not prove attestation provenance. They provide
  no operational allowance until a reviewed wrapper derives the field from the verified host attestation and the
  dependent decisions are resolved. The proposed default launch preflight corroborates its record against live
  systemd evidence; any launch-observer injection is for synthetic tests only. A complete fixed science import list
  and reviewed pin-point wrapper are also prerequisites (amendment §3 / §12).
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

### OD-2 — commission the formal route / governance review of amendment r4?

Reviews so far were of earlier drafts. Acceptance of **amendment r4** still requires a formal route / governance
review, a fresh S12 risk rating (presumed HIGH), the open rule decisions with the reviewer (§4 of amendment r4 — 20
of them, **all undecided**; each option is labeled as amending accepted text, adding a rule/number, or neither), and
your design approval. The r4 integration conditions in §3 / §12 must be accepted and met before operation; a synthetic
repair review cannot substitute for them. Decision options remain yes / no / after OD-1; this brief selects none.

### OD-3 — authorize the RC2 reproduction check (gate L-DET), once a host exists?

It re-runs MB r1's committed **non-target** qualification cases on the new platform and requires an **exact** match.
A mismatch stops the route on that platform (and a further host would need your new ruling with the failure
disclosed). An exact match shows only that the platform reproduces those non-target records; it does **not** restore
the argument that the successor's value equals the lost run's. The protocol is pre-registered (amendment §5): exact
match, no tolerance, **no repeat** of a failed or incomplete attempt, no switching hosts after a mismatch without your
new ruling. It needs OD-1, an accepted route review that includes the list of reference records and their checksums,
and fixed interpreter and comparison tooling first. The accepted text must also pin the complete science import list;
an independent implementation review must verify the wrapper that reaches that pin point and restricts test seams.
No failed or incomplete L-DET is repeated under this proposal; any different repeat rule remains undecided.

## Repair evidence and limits

Amendment r4 §12 maps P1–P6, A1–A5 and E1–E2 to the scoped repairs and remaining conditions. It does not claim that
revision-4 tests, mutation replay or independent review have passed. The cited independent evidence subreview
confirmed the historical ledger correction and all 13 immutable revision-3 bindings; it did not establish native
Linux runtime replay. The quoted V-A provider extract remains unstored and independently UNVERIFIED. A host choice,
review commission or L-DET authorization establishes no additional rule choice or target authority.

## What is not being asked

No target evaluation, freeze, grant, qualification, S1 ruling or scientific adoption. No threshold is changed. Cell 309
is untouched.
