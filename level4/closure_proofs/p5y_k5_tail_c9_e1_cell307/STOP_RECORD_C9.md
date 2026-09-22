# C9 stop record

**Classification: `EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION`.**

> **Superseded in part.** This record's original claim that the route itself was dead is
> WITHDRAWN. A fresh-context review returned STOP_PREMATURE and was correct: C9 had
> manufactured its scientific blocker by misdefining E1. See README and
> `evidence/phase4/C9_ALPHA_LEVER.json`. What survives is that C9 must not EXECUTE —
> no host authorization exists and the pinned runtime cannot be built here.

Reached at Phase 5 (toolchain qualification). Phases 6–16 — manufactured qualification, pre-execution
review of an execution, freeze, frozen qualification, authorization, target execution, seal,
consumption, result classification, coverage r6 — were **not** performed, because the charter
forbids authorization when qualification fails.

## The charter hard-stops that fired

> "STOP scientific execution if: … qualification fails … "

and the toolchain precondition:

> "C9 may provision/use a certification environment ONLY AFTER: … runtime/toolchain is qualified;
> qualification passes; execution authorization is committed; guard is explicitly ALLOW …"

Neither could be satisfied. A third consideration is independent of both: executing the committed
producer would reproduce the committed result, so authorization would have purchased a guaranteed
null.

## What was deliberately NOT done

- **No producer source was modified and no certification was run.** The first pass justified this by
  calling an α change "improvising around the blocker". That justification is **withdrawn**: varying
  α is what E1 means, and `taboo_certify.py` exposes it as a first-class argument. The correct reason
  for not running is narrower and still holds — no authorized host, and the pinned runtime cannot be
  built on this machine.
- **No host was provisioned.** Not AWS (forbidden), not Vultr (unauthorized; the charter forbids
  inferring authorization from historical use), not the local machine (a Homebrew install is shared
  system state, not a dedicated certification environment, and cannot pin FLINT 3.6.0).
- **No guard was set to ALLOW.** It never left DENY.
- **No neighbouring cell was touched.** 306, 308 and 309 were never evaluated. In particular C9 was
  not used as a disguised governance repair for 306, which C8 showed is cheaper (1.067071×) but which
  C8's frozen rule 1 placed out of scope.
- **No r6 was created.** r5 remains authoritative and the open set remains {306, 307, 308, 309}.

## Non-target diagnostic

C8's finding that cell 306 needs only **1.067071×** — cheaper than 307's 1.096007× — is reported here
as `NON_TARGET_DIAGNOSTIC` only. C9 evaluated no 306 address, consumed nothing from it, and draws no
conclusion from it. A separate prospective governance successor may address 306.

## Why this is a useful negative

The valuable part is blocker 1, and it required no compute at all: **the route C8 selected cannot
deliver its target using the producer as committed**, and that is provable from the producer's own
frozen constants and recorded configuration. Had C9 waited on host provisioning first, it would have
provisioned a host, run a certification, and obtained a guaranteed 1.0000×.

The cost of learning this was zero CPU-hours of science.
