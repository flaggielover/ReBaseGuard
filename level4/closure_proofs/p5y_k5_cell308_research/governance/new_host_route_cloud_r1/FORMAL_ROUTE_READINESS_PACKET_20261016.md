# Formal-route readiness packet — Cell-308 MB-S new-host route, Cloud r1 (2026-10-16)

**Status: PREPARATION · every recommendation PROPOSED · NOT ACCEPTED · NOT IN FORCE.** Prepared by the coordinator of
the Claude Cloud session. **It is not an independent review, accepts nothing and decides nothing.** All 21 D-* items
stay undecided, and `DECIDED` stays empty. No freeze, grant, qualification, designation, L-DET case, production execution
or scientific adoption is authorized. `new_target_evaluations = 0` · `cell309_activity = none`.

Companion files, same directory:
* `HOST_EVIDENCE_PLAN_H1_H8_20261016.md` (with `CLOUD_HOST_INVENTORY_R3_20261016.json`);
* `LDET_SPECIFICATION_PACKET_20261016.md`;
* `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_20261016.md`;
* `S12_RISK_REVIEW_BRIEF_DRAFT_20261016.md`.

## 1. Verified engineering state (2026-10-16, before this packet)

| fact | verified value | how |
|---|---|---|
| integration branch head | `b1010b14720aacb97fd049603370a2442562de90` = local HEAD, working tree clean | `git ls-remote`, `git status` |
| final tested source | `9db01504beabd5939b5ff65fe904a69647e17453` (tested inputs equal `d4b2e240`; `lx_platform.py` unchanged since `74badebc`) | ledger |
| native run | 38848711278 on `9db01504`: success; baseline 230 tests PASS; 207/207 KILLED; 208 suites; inputs unchanged; git 2.55.0; artifact 12025299365, GitHub digest `sha256:49c5f5b4…86aa2` | GitHub API, job-log SUMMARY |
| review 71 | REPAIR: REPAIRED; no remaining product-code defect; its harness findings U1–U6 pinned in `d4b2e240` and validated | ledger; `reviews/REVIEW_REVIEW70_REPAIR_DELTA.md` |
| PR3 | draft, open, unmerged; head `b1010b14`; base `claude/cell-308-github-state-skb1g0` | GitHub API |
| original base branch | `37c62102c0e2e22563760173fb04a1fcf66d5e2f`, unchanged | `git ls-remote` |
| PR2 | draft, open, unmerged; head `codex/cell308-review61-continuation` `3b244277…` | GitHub API |
| branch reconciliation | none needed: the remote head equals the expected head | — |

**Artifact audit (final run).** An external audit of the final native artifact was **reported** to the coordinator as
PASS, with report sha256 `da6adcbe1bd27680e1528986e53a321db924667b760c278673ed3afad9278174`. The report itself was
**not supplied** to this session, so its hash was **not verified** here and its content was **not inspected**. It is
recorded as externally reported evidence.

This session's environment could not download any run artifact: the network policy blocks the artifact host. The
earlier historical audit (R2, run 38683513462, report `4700d35a…1dd`) covers that one earlier run only. **Not every
historical artifact has been audited.**

## 2. Classes of source (so they are not mixed)

| class | documents (path, sha256 at `b1010b14`) | standing |
|---|---|---|
| **ACCEPTED** (binding today) | `governance/SUCCESSOR_GOVERNANCE_308.md` `4e9e6ad4…278e`; `…_ADDENDUM_A1.md` `c170c726…152c`; `…_ADDENDUM_A1_ERRATUM_E1.md` `a1972ad3…224c`; `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md` `84379c99…5162` with errata E1 `173bd4f9…77d8` and E2; `governance/CONSTANTS_RATIFICATION_MBS308.md` `caa74210…16ae`; `governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md` `cda3cf45…ad9c` (as quoted [ACCEPTED] by amendment r5) | never weakened here |
| **PREPARATION** | `ROUTE_PREPARATION.md` `80c9f5a0…be99` (coordinator instruction, not independently accepted; review 59 F18) | followed; not cited as accepted |
| **OWNER RECORDS** | `OWNER_SELECTION.md` `bffa0f1e…d8fd` ("走第二条吧", "claude的那个cloud吧"); `USER_AUTHORIZATION_20261014.md` `a202596d…50b9` | authorize target-free preparation only; not S1, S16(c), §14 / G2 or step 8 |
| **PROPOSED** | amendment `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md` `d0963b11…a933`; owner brief r5 `a0142eb0…fbee`; L-DET addendum r1 `4efcd152…5277`; Codex integration supplement `add5c4db…5675`; disposition supplements r63–r71 (r71 `ea88372d…9741`) and r64 erratum E1; this packet and its companions | not binding until a formal route / governance review accepts and the owner decides |
| **HISTORICAL** | amendment drafts r1–r4; owner briefs r1–r4; feasibility r1 / r2 with erratum E1; inventories r1, r2, r2b; the failed and interrupted runs recorded in the ledger | preserved unchanged; describes the past |
| **CURRENT EVIDENCE** | development source at `9db01504` (`lx_platform.py` `da32ce8c…6389`); native run 38848711278; reviews 59–71 recorded verbatim; inventory r3 (this session host only) | development and synthetic only; establishes no host, rule or acceptance |

## 3. Readiness matrix

Status values: **MET** (with evidence), **UNMET**, **OPEN_DECISION** (a decision, not evidence, is missing),
**BLOCKED** (waits on an earlier row).

| # | gate | status | evidence / source | what is missing | authority |
|---|---|---|---|---|---|
| 1 | ROUTE_PREPARATION step 1: inventory and source verification | MET for the session host only; UNMET for any official host | inventories r1, r2, r2b, r3; feasibility r2 + E1 | an official host (OD-1) and its inventory | owner (OD-1) |
| 2 | session host classification | HOST_UNSUITABLE (confirmed by review 59) | amendment r5 §2.1; inventory r3 (restarts, image change, no systemd PID 1, no DMI identity) | — | — |
| 3 | development implementation (DEV_ONLY precursor) | MET as development | `9db01504`; run 38848711278; review 71 REPAIRED | not an implementation review of a successor build | — |
| 4 | formal route / governance review of amendment r5 (+ L-DET addendum, this packet, the procedures) | UNMET | only bounded draft / development reviews exist (59–71) | commission (OD-2); an eligible reviewer | owner (OD-2); formal reviewer |
| 5 | 21 D-* decisions | OPEN_DECISION (all) | amendment r5 §4; `OPEN_DECISIONS` = 21 ids, `DECIDED` empty | §4 of this packet: recommended rulings for decision | formal reviewer + owner (per item) |
| 6 | A1 / A2 conditions (Codex amendment-review findings) | UNMET for operation | §5 | reviewed operational wrapper | implementation reviewer |
| 7 | A5: fixed science import list / pin point | UNMET | `PIN_POINT_MODULES = None`; §5 | D-PIN-POINT after a successor build exists | formal reviewer; implementation reviewer |
| 8 | reviewed journal reader (L′) | UNMET | `JOURNAL_READER_REVIEWED = False` | a reader, its tests, an independent review | implementation reviewer |
| 9 | fresh S12 risk rating | UNMET | draft brief prepared, not commissioned | commission; an eligible reviewer | owner |
| 10 | official host H1–H8 | UNMET (no host) | `HOST_EVIDENCE_PLAN_H1_H8_20261016.md` | OD-1, inventory, owner attestation, accepted review | owner; appointed acceptance reviewer |
| 11 | host-attestation acceptance mechanism (D-HOST-LIFETIME (i)–(iii)) | OPEN_DECISION | (iii) implemented in development; (i), (ii) specified in the acceptance procedure | formal acceptance of the procedure | formal reviewer + owner |
| 12 | L-DET reference addendum accepted (paths, commits, digests by a non-holder) | UNMET | addendum r1; pins re-verified 2026-10-16 (value-free) | full-clone confirmation; independent re-derivation by an eligible reviewer | formal reviewer |
| 13 | L-DET comparison semantics | UNMET | candidate `_compare` is structural only; specification in the L-DET packet §1 | acceptance of the comparison rule | formal reviewer |
| 14 | step 3: campaign namespace and reviewed successor build | BLOCKED (rows 4, 5, 10) | — | — | owner design approval |
| 15 | step 4: implementation and premeasurement review | BLOCKED (row 14) | — | — | fresh reviewer |
| 16 | OD-3 (L-DET authorization) | BLOCKED (rows 4, 5, 10, 12, 13, 15) | — | — | owner |
| 17 | S14: MB r1 §10 steps 6–8 accepted | MET (register: `a40211cc`, `9ad632c9`, `e451e634`) | conditions register | — | — |
| 18 | S16 (a)–(d) freeze gates | (a), (d) MET in the register; (b), (c) UNMET | register | route conditions as facts; the owner's §14 / G2 decision | owner |
| 19 | MBS-6, MBS-7, MBS-8 owner decisions | UNMET (open, user) | register; brief R2 §4–§6 | owner decisions before any freeze | owner |
| 20 | steps 5–9 (designated series … grant, target) | BLOCKED; not authorized | ROUTE_PREPARATION | everything above, then S1 | owner (S1) |

## 4. The 21 D-* items in six packages

Every recommendation below is **PROPOSED**, for the formal route / governance reviewer and the owner. "Authority" names
who may decide:
* **R**: the formal route / governance reviewer;
* **O**: the owner;
* **S12**: the fresh risk reviewer;
* **I**: the implementation reviewer, who checks conformance.

### 4.1 Reproduction and bindings

| id | governing source | recommended ruling (PROPOSED) or precise unknown | required evidence | implementation dependency | authority |
|---|---|---|---|---|---|
| D-RC2-SCOPE | [ACCEPTED] route A1 §1 ("only on the same platform"); route A1 HOST row ("EXCLUDED unless RC2 is discharged there"); brief R2 §9 ("not settled") | Read both texts cumulatively. (1) An L-DET exact match is **necessary** to discharge the HOST row on that platform. (2) Under route A1 §1 the decisive argument is **not restored** off the old platform, so the successor's value is a second, different draw and the route is rated as S4's changed branch (HIGH unless S12 states otherwise). This is option (a) plus the HOST-row condition, and amends nothing | the two texts; an S12 rating | none | R + O; S12 for the rating |
| D-INTERPRETER | amendment r5 §5 item 3 (new pin); brief R2 §9 (3.14.5 on macOS) | **Precise unknown:** a named build. Recommendation: CPython 3.14.5 from the official source tarball (sha256 recorded), compiler and flags recorded, built and pinned on the official host before L-DET; executable and libpython sha256 fixed in the accepted amendment. An equal version is not an equal platform | build provenance record on the host; pins | OD-1; a build procedure (no install now) | R + O |
| D-PIN-POINT | amendment r5 L-PIN; Codex A5 | **Precise unknown until a successor build exists.** Recommendation: the list is the static transitive import closure of the reviewed successor's evaluation entry point (at least the S11 modules `mb308_stage1`, `mb308_supply`, `mb308_consumer`, `mb308_a0core`, `mb308_pinned` and their certifier imports), computed by static analysis, fixed in the accepted text. A reviewed wrapper reaches the pin point after those imports in every computing mode | the import closure, computed without executing science | successor build (step 3); wrapper | R; I |
| D-LDET-REPEAT | amendment r5 §5 item 5 | Keep **no repeat**: a non-completing attempt stops the route on that platform until a new owner ruling. No new rule | — | none | R + O |

### 4.2 Memory semantics

| id | governing source | recommended ruling (PROPOSED) or precise unknown | required evidence | implementation dependency | authority |
|---|---|---|---|---|---|
| D-MEM-FREE | [ACCEPTED] R-FREE ("measured as the driver's own `free_memory_bytes` (vm_stat free + inactive + speculative + purgeable)") | Option (d): `min(MemAvailable, min over the cgroup chain of (limit − usage))`. It is the most conservative of the Linux analogues and is numeric only with H6 attested. **Amends R-FREE** (label it). R-FREE's attainability rule (≥ 10 readings, 30 s apart, 3 consecutive ≥ FREE_MEM_MIN) is unchanged | official-host prepared-state readings; H6 attestation | L-FREE gate on `root_attestation`; reviewed caller | R + O |
| D-MEM-WIRED | [ACCEPTED] R-MEM step 5 (`hw.memsize − W_idle`) | `effective_limit − idle cgroup usage in the prepared state` (`memory.current`, or v1 `usage_in_bytes`), with `effective_limit = min(MemTotal, every chain limit)`. Stricter than the wired-only analogue (usage includes cache). **Amends R-MEM step 5** | prepared-state readings on the host; H6 | L-FREE / L-WIRED reader | R + O |
| D-MEM-PRESSURE | [ACCEPTED] ratification row 24 (`kern.memorystatus_vm_pressure_level` = 1); brief R2 §9 Memory row | PSI `memory some avg10 = 0.00` in N = 3 consecutive readings 30 s apart (the R-FREE cadence). Start gate only; a host without PSI cannot pass. **Amends row 24 and the brief row; new number N = 3** | PSI available on the host (present on the session host, inventory r3) | L-MEMP reader | R + O |

### 4.3 Host operating conditions

| id | governing source | recommended ruling (PROPOSED) or precise unknown | required evidence | implementation dependency | authority |
|---|---|---|---|---|---|
| D-THERMAL | [ACCEPTED] brief R2 §9 "Thermal pressure level 0" | Pass only if every readable thermal zone is below its lowest passive trip point. **A host with no readable zone cannot pass** (fail closed; VMs such as the session host have none). **New rule; amends the brief row** | zone inventory on the host | L-THERMAL reader | R + O |
| D-LPM | [ACCEPTED] ratification row 25 (lowpowermode 0); brief R2 §9 | Fail if any readable `platform_profile` is `low-power` or any cpufreq governor is `powersave`. If the host exposes neither, the gate needs an owner attestation that no OS-level low-power mode exists. **Amends row 25 and the brief row** | power-management inventory; attestation field | L-LPM reader; schema field | R + O |
| D-POWER-ABSENT | [ACCEPTED] brief R2 §9 AC row; R-FREE prepared state | Server rule: a host with no power-supply entries passes the AC gate only with an owner attestation of mains (or UPS-backed) supply. A boot-id change still gives CONSUMED_INTERRUPTED. Recognised-status rules for hosts with supplies are unchanged. **Amends the AC precondition** | attestation; inventory r3 shows no supplies on the session host | schema field; L-POWER branch | R + O |
| D-LID | readiness checklist (`mbs308_qualify.py` lines 338–341) | Drop for hosts without a lid; on a laptop, require a readable lid state "open" at start. **Amends the readiness checklist** | host class | L-LID branch | R + O |
| D-PAUSE | [ACCEPTED] brief R2 ("EVAL_CAP applies per attempt, on awake time (CLOCK_UPTIME_RAW)") | (1) EVAL_CAP awake time on `CLOCK_MONOTONIC`. On Linux it stops in system suspend, as UPTIME_RAW does on macOS; **amends EVAL_CAP's measurement basis**. (2) Hypervisor pause is **not** detectable from the guest. Require bare metal, or an owner / provider attestation (H1) that no pause or live migration occurs; channel P stays AMBIGUOUS-only. **New rule.** (3) Interval CLEAN stays impossible until a reviewed journal reader exists | H1 attestation; journal reader | L-AWAKE; L-SLEEP; journal reader | R + O |

### 4.4 Exclusivity

| id | governing source | recommended ruling (PROPOSED) or precise unknown | required evidence | implementation dependency | authority |
|---|---|---|---|---|---|
| D-EXCL-WINDOW | [ACCEPTED] R-EXCL-PCT (25 %, one hosting-app exception); governance S17 | Windowed CPU share over **30 s** (the prepared-reading cadence), threshold 25 % of one CPU unchanged. **Hosting app = none** on a systemd host, so the exception is removed (nothing is raised). A process that exits in the window is charged its last observed ticks, and refuses if above the threshold. An unknown share is no reading, which refuses; the start gate may then be re-read before the marker (a start-gate re-read consumes nothing). **Changes R-EXCL-PCT's measured quantity; new number 30 s; removes the exception** | prepared-state readings on the host | L-EXCL reader | R + O |
| D-ALLOW-PATHS | [ACCEPTED] R-ALLOW (b) (SIP prefixes) | **None**: no Linux path is auto-allowed (current, strictest). A dedicated host should have no busy non-campaign daemon. If one exists, the owner stops it. Amends nothing | prepared-state readings | none | R + O |
| D-ALLOW-BASE39 | [ACCEPTED] R-ALLOW base "the current 39 names" | **Drop** the 39 macOS names on Linux (a Linux binary could reuse such a basename). Stricter. **Amends R-ALLOW** | — | constant | R + O |

### 4.5 CPU and caps

| id | governing source | recommended ruling (PROPOSED) or precise unknown | required evidence | implementation dependency | authority |
|---|---|---|---|---|---|
| D-WORKERS-CORES | [ACCEPTED] ratification item 15 ("WORKERS 5 on hw.ncpu 6 … leaves one spare core") | Reading: the accepted sizing assumes **online CPUs ≥ WORKERS + 1 = 6**; WORKERS unchanged. Make it a host requirement (the session host has 4, inventory r3). Reading only | affinity / online CPUs on the host | host requirement row | R |
| D-CAPS-CPU | [ACCEPTED] brief R2 §6 (MBS-8 options (i) / (ii)); amendment r5 notes thin Q12 margins on macOS arm64 | **Owner MBS-8 choice.** Recommended: **(ii)**, re-derive the caps by the accepted §3.2 rule from the new host's official decoy runtimes (non-holder, decoys only). On a changed CPU, the macOS-measured margins (about 6 % and 9 %) give no assurance. Requires the brief R2 §8 sequencing answer first | official decoy runtimes on the host | non-holder derivation; S16(c) | O (MBS-8); R |

### 4.6 Launcher, identity and historical-state assertions

| id | governing source | recommended ruling (PROPOSED) or precise unknown | required evidence | implementation dependency | authority |
|---|---|---|---|---|---|
| D-TEXT-LAUNCHD | [ACCEPTED] R-MEM step 1 ("under the launchd launcher"); brief R2 §9 | Textual amendment to "under the reviewed launcher (L-LAUNCH)" | — | L-LAUNCH implementation review | R + O |
| D-ID-ZOMBIE | [ACCEPTED] O-4 outcome (unreadable argv ⇒ UNKNOWN) | **No**: a zombie or dead task proves nothing (current fail-closed). Amends nothing | — | none | R |
| D-S15-NEWHOST | [ACCEPTED] governance A1 S15 | **Both** mechanisms at every preflight: (1) read the MB r1 refs from the pushed repository and assert `refs/p5y-k5-cell308-mb-r1/target-consumed` → `afa93072` is the only ref under that prefix; (2) an owner attestation, refreshed at every official step, that the Mac store holds no pending ref, emergency file or MB r1 `evidence/`. **New assertion mechanism for an accepted condition** | repository refs; owner attestation | reviewed S15 check | R + O |
| D-HOST-LIFETIME | amendment r5 §4 (new rule; carried items (i)–(iii)) | Adopt `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_20261016.md`: git tree paths and blob contents only; ledger REVIEW binding; owner-appointed, non-coordinator, non-holder reviewer; external anchor; H1–H8 per the host plan | an attestation and its accepted review | (i), (ii) and the external anchor are not implemented; schema fields | R + O |

## 5. Conditions A1, A2, A5 (and two related items), traced

**These IDs are not the documents named "addendum A1".** "Addendum A1" names three unrelated accepted or proposed
texts: governance addendum A1, route audit addendum A1, and the proposed route amendment A1. The condition IDs come
from one review.

* **Source:** `reviews/REVIEW_CLOUD_R1_DELTA_R3_CODEX_AMENDMENT.md` (sha256 `ba578675…ed16`). It is a Codex
  amendment-fidelity review of a Codex amendment draft, preserved on the PR2 branch `codex/cell308-review61-continuation`
  at `3b244277`, not on this branch.
* **Carried as conditions by** the Codex amendment r4 (PR2 branch, same file name as this branch's Claude r4, different
  content: sha256 `0a9d720f…aa9b` vs `42114202…4f63`) §12, and its erratum E1 (`b73ecabf…7e84`). The combined
  integration on this branch keeps them as status labels in `streams/CLOUD_R1_LINUX_DEV/lx_verified.py`
  (`b78756eb…a9a9`):
  * A1 and A2 as `DEV_COMPOSITION_ONLY_OPERATIONAL_REVIEW_UNMET`;
  * A5 as `UNMET_FIXED_SCIENCE_IMPORT_LIST_AND_PIN_POINT`.

| id | original finding (Codex review, verbatim heading) | condition carried (Codex r4 §12 / E1) | state at `9db01504` | what discharges it |
|---|---|---|---|---|
| A1 | "L-FREE claims a binding to verified attestation that the API does not enforce" (MAJOR) | "verified current-host attestation provenance"; no operational allowance until an independently reviewed wrapper derives the field from the verified committed record and the current host | `root_attestation()` is derived inside `memory_readings`, not a caller flag; `lx_verified.observe` withholds `effective_limit` / headroom. Development composition only | implementation review of the operational wrapper; D-HOST-LIFETIME decided; H6 attested |
| A2 | "L-LAUNCH's record verification still accepts caller-asserted launch evidence" (MAJOR) | "live launcher corroboration and reviewed restrictions on injected seams / configuration" | `preflight` takes a fresh `launched_by_systemd()` reading; a caller record never passes on its own; reader seams remain for tests | implementation review confirming no production caller passes test seams; H2 on the host |
| A5 | "The fixed pin-point import list is a remaining formal-review requirement" (NOTE) | "fixed complete science import list and independently reviewed pin-point wrapper in every computing mode" | `PIN_POINT_MODULES = None`; `pin_point()` refuses | D-PIN-POINT; successor build; implementation review |
| journal reader | amendment r5 L-SLEEP | a reviewed journal reader for channel L′ | `JOURNAL_READER_REVIEWED = False`: no interval can be CLEAN | a reader, its tests, an independent review |
| fixed scientific import / pin-point list | amendment r5 L-PIN, D-PIN-POINT | as A5 | undefined | as A5 |

A3 and A4 of the same review were textual and are resolved in the Codex r4 text. They are not open conditions.

## 6. Ordered dependency list

1. **OD-2**: the owner commissions the formal route / governance review. Its scope: amendment r5, the L-DET addendum and
   packet, this packet, the acceptance procedure.
2. **OD-1**: the owner decides V-A / V-B (names one persistent machine) or V-C (close the route). V-C ends here.
3. The formal reviewer:
   * decides or carries each D-* item (§4);
   * accepts or corrects the acceptance procedure;
   * re-derives the L-DET reference list on a full clone;
   * fixes the comparison rule.
4. The fresh **S12** review rates the route (draft brief prepared).
5. Phase-1 read-only inventory on the named machine. The owner then performs the H3 actions, writes and commits the
   attestation, and appoints the acceptance reviewer, who accepts or rejects. The ledger binding and the external
   anchor follow.
6. Owner design approval; campaign namespace; the reviewed successor build. This fixes D-PIN-POINT, the journal reader,
   the A1 / A2 wrapper and D-INTERPRETER's build on the host.
7. Implementation and premeasurement review (step 4).
8. **OD-3**, then exactly one L-DET attempt. A mismatch or an incomplete attempt stops the route on that platform.
9. Only after a match: MBS-6 / MBS-7 / MBS-8, S16(c), the prospective designation policy, then steps 5–9 of
   ROUTE_PREPARATION up to S1. None of this is authorized now.

## 7. Narrow external decisions and evidence still required (with recommended resolutions)

| # | what | who | recommended resolution |
|---|---|---|---|
| 1 | OD-2: commission the formal route / governance review | owner | **Yes**, now. Scope as §6 item 1; reviewer eligibility as the S12 brief §2 |
| 2 | OD-1: official host | owner | **V-B** (or V-A with the campaign as a systemd service), naming one persistent bare-metal or dedicated machine with ≥ 6 online CPUs, readable thermal zones, systemd PID 1, local persistent disk and DMI identity. Otherwise **V-C**. The session host is excluded |
| 3 | appoint the acceptance and S12 reviewers | owner | appoint by name; non-coordinator, non-holder, not reviews 59–71 |
| 4 | the 21 D-* items | formal reviewer + owner | as §4 (PROPOSED) |
| 5 | the attestation and H3 actions | owner, after OD-1 | per the host plan §2 |
| 6 | MBS-8 under a changed CPU | owner | (ii), after the brief R2 §8 sequencing answer |
| 7 | the final-artifact audit report | whoever holds it | supply the report file (sha256 `da6adcbe…8174`) to the repository or the session so its hash can be verified. Alternatively allow `productionresultssa1.blob.core.windows.net` in the environment's network policy so artifacts can be downloaded |

## 8. Trust assumptions that remain

* In-repository checks are defence in depth only (review 67 N7). An actor who controls the repository can construct a
  consistent false history. Closing this needs the ledger binding plus an external anchor, and an independent,
  appointed reviewer.
* The owner's attestations are statements, not measurements. Provider lifetime terms are quoted, not verified.
* Development tests are synthetic. They establish no host lifetime, power-loss durability, cgroup-ancestor visibility,
  Linux / macOS rule equivalence or reviewer authority.
* The coordinator's preparation, including this packet and reviews 59–71, is not formal independent acceptance.

## 9. Exposure disclosure for this packet

* Opened: the governance, registry and route documents named above. Also `streams/CLOUD_R1_LINUX_DEV/` sources and the
  ledger.
* From the PR2 branch, by `git show`: the Codex r4 §12, its errata E1 / E2 and the Codex amendment review.
* Hashed by git object reads only, no content printed: the five MB r1 r3 qualification records and the two candidate
  code files.
* Hashed only, not opened: `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`.
* **Name-level contact:** a `git ls-remote` of the repository listed branch names, including names containing "309".
  No such branch was fetched, listed further or opened.
* Not opened: any interruption-assessment, incident-audit, execution-interruption review or exposure-disclosure record;
  MB r1 postexec or target-run material; Cell-309 content.
* No scientific, candidate, decoy, qualification or L-DET code was run. The only host action was the read-only inventory
  r3.
