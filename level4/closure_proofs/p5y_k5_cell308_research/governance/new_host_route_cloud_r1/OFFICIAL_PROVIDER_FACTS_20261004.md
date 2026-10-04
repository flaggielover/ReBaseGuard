# Official provider facts — Claude Cloud route

Date checked: 2026-10-04 UTC. This is a coordinator infrastructure note, not independent review and not designated evidence.

## Sources

- Claude Help Center, [Claude Cowork architecture overview](https://support.claude.com/en/articles/14479288-claude-cowork-architecture-overview).
- Claude Help Center, [Use Claude Cowork on web, desktop, and mobile](https://support.claude.com/en/articles/15520349-use-claude-cowork-on-web-desktop-and-mobile).

## Facts supported by the provider documentation

- Cloud work runs in an isolated, temporary sandbox on Anthropic-managed infrastructure.
- A cloud session's sandbox is created when the session starts and destroyed when the session ends.
- Work can continue in the background while the user's laptop is closed.
- Sessions and files are saved to the user's Claude account, while files fetched into a session are deleted when that session is deleted.
- A later cloud session starts on a fresh machine; the documentation does not promise the same VM, boot identity, CPU allocation or memory limit.

## What remains unresolved

The documentation does not establish a maximum execution window, an inactivity timeout, whether a running VM can be reclaimed, whether resources remain stable for one execution, or whether compute is exclusive. Account-level session/file retention is not the same as a durable exactly-once result on the execution host. The observed restart and the inventory's `HOST_UNVERIFIED` classification therefore remain unchanged.

This note narrows the unknowns but does not authorize Linux adaptation, designation, qualification, freeze, grant, apply or target evaluation. `new_target_evaluations=0`; `cell309_activity=none`.
