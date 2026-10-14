# OFFICIAL_PROVIDER_FACTS_20261014 — erratum E1 (coordinator; review 59 finding F17)

`OFFICIAL_PROVIDER_FACTS_20261014.md` stays byte-unchanged; this erratum prevails where they differ.

## Added statements (verbatim, from the review-59 fetched copy of `cloud-environments`, 2026-10-14 ~19:18Z,
## `reviews/scratch_CLOUD_R1/fetched/cloud-environments.md`)

| id | statement |
|---|---|
| P4 (completed) | "A command moved this way can keep running for up to 30 more minutes before Claude Code stops it at its background time limit. Setting `BASH_DEFAULT_TIMEOUT_MS` above `1800000` milliseconds lengthens that limit as well as the foreground default." |
| P10 | "**The VM is restored after being idle**: after a few minutes without activity, a session’s VM pauses with its files saved. Your next message restores the same VM and starts Claude Code again." |

## Withdrawn

"Settled" item 3's clause that P5 "does not say that the background time limit or the idle pause can be" raised is
**withdrawn for the background time limit**: the completed P4 says it can be lengthened. Nothing found says the idle
pause can be disabled. Whether the sentence was already on the page at 18:55Z, when the coordinator's extract was
taken, is **UNVERIFIED** (the coordinator's query extract did not contain it).

## Reconciliation with r1

The r1 inventory recorded a 2-hour cap (`background_task_limit_of_agent_tool`) from the agent tool's own definition.
That, the documented 30-minute default and the configurable lengthening are all limits of **agent-launched
commands**. None is a statement about a process detached from the agent, and none is a lifetime guarantee for the VM.

## Effect

The classification is unchanged (`CLOUD_FEASIBILITY_R2_ERRATUM_E1.md` §4–§5): there is still no documented basis for
an 8-hour unattended computation, and the primary basis is now DR2's user-performed no-update requirement, which a
provider-managed image cannot meet.
