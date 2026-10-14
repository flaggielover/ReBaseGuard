# Cell-308 new-host route (Claude Cloud, r1) — feasibility, second assessment (r2)

Date: 2026-10-14 (host inventory 18:58:38Z). Class: INFRASTRUCTURE. **Not designated evidence. Coordinator
determination, not an independent review** (the fresh review of this document is recorded separately under
`reviews/`).

`new_target_evaluations: 0` · `proxy_evaluations: 0` · `cell309_activity: none` · no benchmark, decoy,
designation, qualification, freeze, grant, apply or target step · nothing installed, no setting changed · historical
candidate `142d97a9`, MB-S r1 designated evidence `86d3f8cb…` and its `NOT_DERIVED` / R-FREE `GATE_UNATTAINABLE`
stop untouched.

Authority: the owner's 2026-10-14 instruction (`USER_AUTHORIZATION_20261014.md`), which authorizes target-free Cloud
feasibility investigation and states that "unresolved host facts must block dependent official steps, but must not
prevent useful target-free analysis and development."

## 1. Verified starting state (unchanged since 2026-10-04)

| item | value on 2026-10-14 | changed? |
|---|---|---|
| `p5y-k5-cell308-mbs-r1-candidate` | `142d97a90a1c3fafff394044aa1448674f7a633c` | no |
| `p5y-k5-cell308-mbs-r1-research` | `88a16f74f3dc98c526f47a768be6f3b3b0f96f99` | no |
| MB-S r1 status | NOT_DERIVED / R-FREE GATE_UNATTAINABLE; ALREADY_DESIGNATED | no |
| Cloud route status | HOST_UNVERIFIED (CLOUD_FEASIBILITY.md, OFFICIAL_PROVIDER_FACTS_20261004.md) | see §4 |
| other Cell-308 branches or refs | none besides the two above | no |

## 2. New evidence

**E1. Provider documentation** (`OFFICIAL_PROVIDER_FACTS_20261014.md`, verbatim P1–P9). For the Anthropic-hosted
environment: an idle session's VM *pauses after a few minutes* and *can later be reclaimed*; after a reclaim a
*fresh VM* is provisioned and running *background work … shell commands* is *not restored*; agent commands are
limited to ≤ 10 min foreground plus ≤ 30 min background. An owner-operated host is reachable only through a
self-hosted environment (Team / Enterprise beta) or Remote Control.

**E2. A second Cloud host, observed directly** (`CLOUD_HOST_INVENTORY_R2_20261014.json`, collected with
`streams/CLOUD_R1_LINUX_DEV/lx_inventory.py`, read-only). Same provider and environment type, a different session:

| property | 2026-10-04 host | 2026-10-14 host |
|---|---|---|
| CPU model (guest-visible) | Intel Xeon @ 2.80 GHz | Intel Xeon @ 2.10 GHz |
| vCPUs | 4 | 4 |
| kernel | 6.18.44-fc-v64 | 6.18.44-fc-v114 |
| OS | Ubuntu 24.04.4 LTS | Ubuntu 24.04.5 LTS |
| MemTotal | 16 876 515 328 B | 16 874 930 176 B |
| leaf cgroup memory limit | 14 345 035 776 B | 14 343 688 192 B |
| default `python3` | 3.11.15 | 3.13.16 |
| interpreters under /usr/bin | 3.10.20, 3.11.15, 3.12.3, 3.13.14 | 3.11.17, 3.12.3, 3.13.16 (3.10 absent) |
| systemd as PID 1 | no | no |
| power supplies / thermal zones exposed | none / none | none / none |

Every platform-pin-relevant property except architecture and vCPU count differs between the two sessions.

**E3. Port map of the historical candidate** (`streams/CLOUD_R1_LINUX_DEV/results/PORT_MAP_142D97A9.json`,
read-only `git show` scan): 457 lines in 28 files use macOS-only facilities (launchd 134, macOS paths 80, pmset 47,
`ps` semantics 44, caffeinate 44, platform pins 36, macOS clocks 29, vm_stat 27, thermal 21, sysctl 14, software
update 9, F_FULLFSYNC 6). `time.CLOCK_UPTIME_RAW`, on which `AwakeCap` (EVAL_CAP) is counted, does not exist on Linux.

**E4. Frozen-constant context (constants, not target-run observations):** `EVAL_CAP_S = 8 h` per attempt on awake
time, `DECOY_CAP_S = 12 h`, rung CPU caps up to 8 700 s, at most 3 resumes inside a 7-day window, platform pins
re-verified at every resume (mismatch at a resume ⇒ close-indeterminate) — `mbs308_driver.py` lines 208–211 and
USER_DECISION_BRIEF_308_SUCCESSOR_R2 §8 item 8 and §9. The excluded MB r1 target-run observations were not
consulted.

## 3. Assessment against the accepted texts

**U1 — one host across the official sequence.** The accepted texts bind designation, qualification and execution to
one host and configuration: brief R2 §9 host-identity row ("this host only: another host means S4's changed
branch"), PLATFORM_PINS "taken from the qualification host at the freeze" and "re-verified at `execute`, at every
resume", ROUTE_PREPARATION step 7 ("Official qualification on the actual frozen host/configuration"). Between those
steps the accepted sequence places owner decisions and independent reviews (S16(c), the qualification review, the S1
ruling), i.e. periods without session activity. E1 documents that an idle VM pauses within minutes and may then be
reclaimed and replaced by a fresh VM; E2 shows that a fresh VM can differ in every pinned property. Keeping the
session artificially active across those periods is excluded by ROUTE_PREPARATION ("Do not keep a cloud session
idle or repeatedly measure in order to appear active") and would still not be a provider guarantee.

**U2 — run length versus the documented lifetime model.** A single attempt may legitimately last up to EVAL_CAP
(8 h of awake time); a decoy up to 12 h. The documented agent-command limits are 10 + 30 minutes. A campaign process
detached from the agent (`setsid`) is not covered by any provider statement: whether it keeps the VM "active" is
UNKNOWN. Nothing documented supports an 8-hour unattended computation in this environment.

**U3 — the resume path cannot rescue a reclaim here.** MB-S answers a host interruption with an operator-launched
resume, but a resume re-verifies the platform pins and a mismatch gives close-indeterminate (brief R2 §8 item 8). After
a reclaim the resume would run on a fresh VM; by E2 the pins are expected to differ. A reclaim during the one consumed
evaluation would therefore most likely end it INDETERMINATE — the outcome S6 exists to prevent ("so the one
evaluation is not lost again", governance §4 item 7).

**U4 — missing sources (decisions, not unsuitability by themselves).** No service manager as PID 1, no power supply,
no thermal zone, no suspend statistics, no journal (both hosts). Each maps to an open rule-semantics decision in the
proposed amendment; none is treated as passing.

## 4. Classification

For the **Anthropic-hosted Claude Cloud session environment** as the host of the official stages (designated series,
official qualification, execution): **`HOST_UNSUITABLE` — coordinator determination, pending the independent review
recorded under `reviews/`.** Basis: U1 and U3 are contradictions between documented provider behaviour plus direct
observation and accepted requirements (one host and stable pins across the sequence; a resumable single evaluation),
not merely missing facts; U2 adds that no documented basis exists for an 8-hour unattended run.

If the independent reviewer does not accept U1/U3 as contradictions, the conservative fallback is the previous
`HOST_UNVERIFIED`. **Either classification blocks every dependent official step**; neither is treated as a pass.

The same environment **is suitable for target-free work** — development, synthetic tests, static analysis and
reviews — and is used for exactly that in this session.

Not classified here (each needs an owner decision and its own Phase-1 inventory on the actual machine):
* **V-A** a self-hosted Claude environment whose runner is an owner-operated, persistent Linux host (P7, P8; Team /
  Enterprise beta; plan availability unknown to the coordinator);
* **V-B** any other owner-provided persistent Linux host (optionally driven through Remote Control, P9);
* **V-C** closing the Cloud route without a host (the R-FREE stop brief's option (a) analogue).

## 5. What remains blocked, and why

Blocked (dependent official steps): new campaign namespace and refs, designated series, derivation/apply, freeze,
official qualification, S1 ruling, grant, execution. They wait on, in order: an owner host decision (OWNER_DECISION
_BRIEF_CLOUD_R1.md, OD-1), a Phase-1 inventory of that host, an accepted route amendment (independent route and
governance review), a fresh S12 incident-independence rating, and operator design approval.

Not blocked, and done in this session (target-free): this assessment, the proposed amendment and Linux platform
contract (`PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md`), the development-only platform layer with isolated tests
(`streams/CLOUD_R1_LINUX_DEV/`), and a fresh independent review.

## 6. Exposure disclosure (coordinator of this session)

Read in this session: governance SUCCESSOR_GOVERNANCE_308, its ADDENDUM_A1 and ERRATUM_E1; USER_DECISION_BRIEF_308
_MBS_R1_RFREE_STOP; excerpts of USER_DECISION_BRIEF_308_SUCCESSOR_R2 (§8 item 8, §9 table and lines quoted above);
the "Written rules" section of CONSTANTS_RATIFICATION_MBS308; every file of `governance/new_host_route_cloud_r1/`; the
research README; the last ledger lines; candidate code `mbs308_host.py` (lines 1–50, 161–300, 356–604),
`mbs308_rrules.py` (lines 1–90), `mbs308_driver.py` (lines 495–612 and grep hits for constants),
`mbs308_state.py` (lines 490–506, 973–1010, 1160–1180 and grep hits); two grep hits (`float(` lines) and the
docstring of the MB r1 science glue `mb308_pinned.py`; commit subject lines of the two Cell-308 branches; branch names
of all branches. Not opened: any MB r1 target-run record, `audit/EXECUTION_INTERRUPTION_ASSESSMENT*`,
`audit/INCIDENT_AUDIT*`, `reviews/REVIEW_EXECUTION_INTERRUPTION*`, the designated evidence file itself (its ten
non-target free-memory readings were seen only as quoted in the R-FREE stop brief), or any Cell-309 content. The coordinator holds no MB r1 target-run runtime observation.
