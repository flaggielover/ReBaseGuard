# Official provider facts — Claude Cloud route, second check (2026-10-14)

Date checked: 2026-10-14 (18:50–18:55Z). Coordinator infrastructure note. **Not independent review, not designated
evidence.** Supplements, and does not replace, `OFFICIAL_PROVIDER_FACTS_20261004.md`.

## Sources (fetched live, `maxAge: 0`)

- S-A. Claude Code Docs, *Claude Code on the web* — <https://code.claude.com/docs/en/claude-code-on-the-web>
  (sections "Environment expired", "Limitations").
- S-B. Claude Code Docs, *Configure cloud environments* — <https://code.claude.com/docs/en/cloud-environments>
  (section "Time limits", "Idle sessions").
- S-C. Claude Code Docs, *Self-hosted environments* — <https://code.claude.com/docs/en/self-hosted-environments>.
- S-D. The in-session environment documentation tool, topic `session.resources` (no lifetime figure given).

## Verbatim statements (quoted exactly as fetched)

| id | source | statement |
|---|---|---|
| P1 | S-A | "Cloud sessions stop after a period of inactivity and the session’s VM is reclaimed." |
| P2 | S-A | "Reopen the session from claude.ai/code to provision a fresh VM: … **Not restored**: background work that was still running when the VM was reclaimed, such as subagents and shell commands" |
| P3 | S-B | "Idle sessions: after a few minutes without activity, a session’s VM pauses with its files saved, and a paused VM can later be reclaimed." |
| P4 | S-B | "Claude waits 2 minutes for a foreground command by default and can ask for up to 10 minutes. … A command moved this way can keep running for up to 30 more minutes before Claude Code stops it at its background time limit" |
| P5 | S-B | "To raise the command timeouts for an environment’s sessions, add BASH_DEFAULT_TIMEOUT_MS and BASH_MAX_TIMEOUT_MS … to its environment variables." |
| P6 | S-A | "The session keeps running after you close your laptop" |
| P7 | S-C | "Self-hosted environments are in public beta on Team and Enterprise plans and are off by default." |
| P8 | S-C | "A self-hosted environment executes Claude Code cloud sessions on infrastructure your organization operates." … "Repository checkouts, build artifacts, secrets, and any files a session creates or modifies stay on the machines you provision." |
| P9 | S-C | "If you want to run Claude Code on your own always-on machine and drive it from other devices, use Remote Control, which is also available on Pro and Max plans." |

## What these settle, and what they do not

Settled by provider text (Anthropic-hosted environment):

1. A session VM is **paused after a few minutes without activity** and a paused VM **can be reclaimed** (P1, P3).
2. After a reclaim, **running processes are not restored**; a fresh VM is provisioned (P2).
3. Agent-launched commands have documented time limits (≤ 10 min foreground, ≤ 30 min further in background,
   P4); P5 says the *command timeouts* can be raised per environment, and does not say that the background time limit
   or the idle pause can be.
4. An owner-operated host can be used for cloud sessions only through a self-hosted environment (Team / Enterprise,
   beta) or, outside the cloud-session product, Remote Control on the owner's own machine (P7–P9).

Still not stated anywhere found: a maximum VM lifetime while active, the exact idle interval, whether a process that
is not an agent command (e.g. a `setsid` daemon) keeps a VM "active", whether the guest clocks observe a pause, disk
durability after a reclaim, cross-session host identity, or exclusivity of compute. These remain **UNKNOWN** and are
never treated as passing.

`new_target_evaluations = 0` · `cell309_activity = none` · no measurement, designation, qualification, freeze, grant,
apply or target step.
