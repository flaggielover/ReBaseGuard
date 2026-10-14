# Owner decision brief — Cell-308 Cloud route r1 after the r2 feasibility check (2026-10-14)

Target-free. `new_target_evaluations = 0` · `cell309_activity = none`. Prepared by the coordinator; the fresh
independent review of the underlying documents is under `reviews/REVIEW_CLOUD_R1_FEASIBILITY_AMENDMENT_DEV.md`.

## Where things stand

* MB-S r1 on the Mac stopped at **NOT_DERIVED / R-FREE GATE_UNATTAINABLE** (unchanged; nothing re-measured).
* You chose the new-host route on Claude Cloud ("走第二条吧", "claude的那个cloud吧").
* The Anthropic-hosted Cloud session is now classified **HOST_UNSUITABLE for the official steps** (coordinator;
  pending review; fallback HOST_UNVERIFIED), because (`CLOUD_FEASIBILITY_R2.md`):
  1. the provider documents that an idle session VM pauses within minutes and can be reclaimed, and a fresh VM is
     provisioned afterwards, without the running processes;
  2. two Cloud sessions ten days apart ran on visibly different platforms (CPU model, kernel build, OS point release,
     Python versions), while the accepted rules need one unchanged platform from qualification to the end of the
     execution window, across your decisions and the reviews in between;
  3. a resume after a reclaim would find changed platform pins, which the frozen rules turn into INDETERMINATE.
* It remains useful for target-free development and review, which is what was done today: a proposed Linux platform
  contract (`PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md`) and a tested, development-only Linux layer.

## Decisions that only you can make

### OD-1 — which machine, if any, should be the official host?

| option | what it means | what it needs from you | consequence |
|---|---|---|---|
| **V-A** | Claude Cloud **self-hosted environment**: Claude sessions are routed to a runner on a Linux machine that your organization operates; the campaign runs there as a systemd service | a Team or Enterprise plan with self-hosted environments enabled (public beta); a persistent Linux machine you control | keeps "Claude Cloud" as the session surface; the machine must meet H1–H8 of the amendment |
| **V-B** | any **persistent Linux machine** you own or rent (server, workstation), optionally driven from the Claude app via Remote Control | the machine and its access | same H1–H8 requirements; not a "cloud session" host |
| **V-C** | **close the Cloud route** without a host, recording the r2 classification; MB-S r1 stays at its NOT_DERIVED stop | nothing | no further Cell-308 work under MB-S unless a later ruling opens another route |
| other | e.g. a different Mac with more memory (that is not the Cloud route; it would be its own S4 changed-branch route, same platform family) | your ruling | its own route preparation |

Whatever you choose, nothing official happens next: the chosen machine first gets its own read-only inventory
(ROUTE_PREPARATION step 1), then the amendment goes to an independent route / governance review.

### OD-2 — commission the formal independent route / governance review of amendment A1?

The review done today is a fresh, independent review of the *draft* and the *dev code*. The governance sequence also
requires a route / governance review that can ACCEPT or REJECT the amendment, a fresh S12 incident-independence rating
(the accepted texts presume **HIGH** for a changed platform), and your design approval. Yes / no / after OD-1.

### OD-3 — authorize the RC2 determinism check (gate L-DET) once a host exists?

The accepted route audit excludes a host move "unless RC2 is discharged there": MB r1's committed non-target decoy
records must reproduce **exactly** on the new platform. The science uses floating-point proposals (libm), so this is
not guaranteed; it is the single most decisive target-free test of the whole route. The protocol is pre-registered in
amendment §5 (exact equality, no tolerance, no re-run selection, stop on any mismatch). It needs OD-1 and a route-review
acceptance first.

### Later, with the route reviewer (not now)

The rule-semantics questions D-MEM-FREE, D-MEM-WIRED, D-MEM-PRESSURE, D-THERMAL, D-LPM, D-POWER-ABSENT,
D-ALLOW-PATHS, D-EXCL-WINDOW, D-PAUSE, D-HOST-LIFETIME and D-WORKERS-CORES (amendment §4). Each currently blocks its
gate. None is decided by the coordinator, and the dev code never substitutes a Linux metric for a macOS one.

## What is not being asked

No target evaluation, freeze, grant, qualification, S1 ruling or scientific adoption. Nothing here changes a
threshold. Cell 309 is untouched.
