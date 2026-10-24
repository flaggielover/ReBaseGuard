# Consolidated D-* recommendation package, revision r2 (Cell-308 Cloud route r1) — after formal review FR1

**Status: PROPOSED · ADVICE TO THE OWNER · NOTHING DECIDED.** `DECIDED` stays empty (`lx_platform.py` at `9db01504`),
and all 21 ids stay open until the owner records a decision.

This package supersedes the recommendations of `FORMAL_ROUTE_READINESS_PACKET_20261016.md` §4 (sha256 `078f2ab2…3a17b`,
preserved unchanged). Each row merges three sources:
* the packet's proposal;
* the F2 disposition of the formal route review FR1 (`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md`, sha256
  `af150ef4…b6df`);
* the coordinator's resolution of FR1's requested changes.

`new_target_evaluations = 0` · `cell309_activity = none`.

**Authority (FR1 F7).** Only the owner (**O**) can bring a rule into force. The formal reviewer's role was advice. **I**
= the implementation reviewer (conformance only). **S12** = the risk reviewer (rating advice).

**Label legend:**
* **AMENDS** an accepted text;
* **NEW RULE** (no accepted counterpart);
* **NEW HOST REQ** (a host-selection requirement);
* **NEW PIN** / **NEW PIN RULE**;
* **SUBST** (a measurement replaced by an owner statement, an evidentiary-class change, FR1 G20);
* **SETS ASIDE PREP:19** (needs the owner to set aside ROUTE_PREPARATION line 19 expressly, FR1 G36).

## 1. The 21 items

| # | id | FR1 F2 | recommended ruling (r2, PROPOSED) | labels | evidence still needed | authority |
|---|---|---|---|---|---|---|
| 1 | D-RC2-SCOPE | ENDORSE_WITH_CHANGES | Read route A1 §1 and the HOST row cumulatively. An L-DET MATCH is **necessary**. RC2 counts as discharged on the named host only under the four **sufficient** conditions of amendment erratum E1.2: <ol><li>L-DET MATCH (a)∧(b);</li><li>the L-DET pins matched at every later computing step;</li><li>the platform window from the L-DET interpreter build;</li><li>MBR1_REPRO matching at qualification.</li></ol>The decisive argument is not restored, so the route stays on the changed branch at a rating **not lower than HIGH**. The S4 instrument is route-audit addendum A2, written after the owner's adoption | a reading; AMENDS nothing in accepted text; the HOST-row CONDITIONAL status is NEW RULE | S12 rating | O; S12 |
| 2 | D-INTERPRETER | CANNOT_ASSESS_WITHOUT_HOST | CPython 3.14.5 built from the official tarball on the named host, with the sha256, compiler and flags recorded. Built before any decoy or L-DET run and never changed after an L-DET outcome. L-PIN pins the build-provenance record and a prefix manifest (L-DET erratum E1 §4) | NEW PIN | whether it builds on the host's toolchain / glibc / libm (host fact) | O; I |
| 3 | D-PIN-POINT | ENDORSE_WITH_CHANGES | `PIN_POINT_MODULES` is the static AST import closure of the reviewed successor's evaluation entry point. It includes the S11 modules, their certifier imports, and the stdlib and C-extension modules reached (e.g. `fractions`, `decimal` / `_decimal`, `json`, `math`, `multiprocessing`). The pin is taken in **every worker** after its imports, and a post-job check refuses any later mapping (requirements doc P1–P4) | NEW PIN RULE | the successor build | O; I |
| 4 | D-LDET-REPEAT | ENDORSE_WITH_CHANGES | **No repeat.** A non-completion stops the route on that platform. Any later owner ruling to try again on the same platform is a **post-result decision**: it needs a fresh S12 re-rating and a fresh formal review with the failed attempt in view. MBR1_REPRO at qualification is not a repeat (erratum E1.3) | NEW RULE | — | O |
| 5 | D-MEM-FREE | ENDORSE_WITH_CHANGES | Free memory = `min( MemAvailable , MemFree + Inactive(file) , min over the chain of (limit − usage) )`. The chain is the campaign unit's cgroup and every ancestor, read from inside the unit. The value is numeric only with H6 attested (`root_attestation`). The earlier claim that (d) was "the most conservative" is withdrawn (G17). R-FREE's attainability rule is unchanged | AMENDS R-FREE; SETS ASIDE PREP:19 | prepared-state readings on the host; H6 | O; I |
| 6 | D-MEM-WIRED | ENDORSE_WITH_CHANGES | `W_idle` analogue = idle usage in the prepared state = `max( MemTotal − MemAvailable , memory.current (v2) or usage_in_bytes (v1) of every **limited** level of the unit's chain )`. `effective_limit = min( MemTotal , every chain limit )`. At the cgroup-v2 root, or with no limit anywhere in the chain, the first term alone applies (G18) | AMENDS R-MEM step 5; SETS ASIDE PREP:19 | prepared-state readings; H6 | O; I |
| 7 | D-MEM-PRESSURE | ENDORSE | PSI `memory some avg10` = `0.00` in N = 3 consecutive readings 30 s apart. Start gate only. A host without PSI (e.g. booted with `psi=0`) cannot pass. This is also a host criterion | AMENDS ratification row 24 and protocol-draft row; new parameters `avg10`, `0.00`, N = 3; SETS ASIDE PREP:19 | PSI on the host | O |
| 8 | D-THERMAL | ENDORSE_WITH_CHANGES | Pass only if every readable `thermal_zone*` is below the **lowest trip point of any type** (passive, active, hot, critical). A zone with **no** trip point fails, and a host with no readable zone fails (fail closed). hwmon sensors (e.g. `coretemp`) are recorded, not gated | **NEW RULE** (no accepted thermal text; replaces a protocol-draft gate, G13 / G19); SETS ASIDE PREP:19 | zone and trip inventory on the host | O |
| 9 | D-LPM | ENDORSE_WITH_CHANGES | Fail if `platform_profile` is `low-power` (or `quiet`). With `intel_pstate` / `amd-pstate` in active mode, fail if any `energy_performance_preference` is `power`; the governor `powersave` is normal there and does not fail. With other drivers (e.g. `acpi-cpufreq`), fail if any governor is `powersave`. If the host exposes none of these, an owner statement that no OS low-power mode exists is required (G16) | AMENDS ratification row 25 and protocol-draft row; **SUBST** for the no-interface case; SETS ASIDE PREP:19 | power-management inventory | O |
| 10 | D-POWER-ABSENT | ENDORSE_WITH_CHANGES | A host with no power-supply entries **and** a non-portable DMI chassis type passes the AC gate only with an owner statement of mains (or UPS-backed) supply. A boot-id change still gives CONSUMED_INTERRUPTED. Hosts with supplies keep the recognised-status rules | AMENDS the AC precondition; **SUBST** | inventory (supplies, chassis type) | O |
| 11 | D-LID | ENDORSE_WITH_CHANGES | Whether the host has a lid is derived from the inventory (DMI chassis type), never assumed. A host without a lid drops the check. A laptop requires a readable lid state `open` at start | AMENDS the readiness checklist (candidate code, not accepted text) | inventory | O |
| 12 | D-PAUSE | ENDORSE_WITH_CHANGES | <ol><li>EVAL_CAP awake time on `CLOCK_MONOTONIC`, which stops in system suspend.</li><li>**Bare metal only** (recommended). The attestation route (no pause or live migration) is retained only as a fallback the owner may choose, labelled SUBST.</li><li>Interval CLEAN stays impossible until a reviewed journal reader exists.</li></ol> | (1) AMENDS EVAL_CAP's basis; (2) NEW RULE (+ SUBST if fallback); NEW HOST REQ (bare metal) | DMI / `systemd-detect-virt` on the host | O |
| 13 | D-EXCL-WINDOW | ENDORSE_WITH_CHANGES | Windowed CPU share over 30 s, threshold 25 % of one CPU unchanged. Hosting app = none, so the exception is removed. A process that **exits** in the window is unknown, which means no reading, which refuses (as L-EXCL already reads; G8). Start-gate re-read: a NEW RULE, at most 3 re-reads before the marker, every reading recorded | AMENDS R-EXCL-PCT (measured quantity; exception removed); new number 30 s; NEW RULE (re-read); SETS ASIDE PREP:19 | prepared-state readings | O |
| 14 | D-ALLOW-PATHS | ENDORSE_WITH_CHANGES | **None**: no Linux path is auto-allowed. Stricter | **AMENDS R-ALLOW (b)** (its literal list includes `/usr/sbin/` and `/sbin/`, G14); SETS ASIDE PREP:19 | — | O |
| 15 | D-ALLOW-BASE39 | ENDORSE | Drop the 39 macOS base names on Linux. Stricter | AMENDS R-ALLOW; SETS ASIDE PREP:19 | — | O |
| 16 | D-WORKERS-CORES | ENDORSE_WITH_CHANGES | ≥ 6 **physical cores** in the campaign unit's effective cpuset (SMT siblings not counted). WORKERS 5 unchanged | **NEW HOST REQ** (derived from ratification item 15's rationale, G15) | `lscpu` core / socket topology and the unit cpuset | O |
| 17 | D-CAPS-CPU | OWNER_RESERVED | MBS-8 is the owner's choice. The coordinator's advice stays **(ii)**: re-derive the caps by the accepted §3.2 rule from official decoy runtimes on the named host (non-holder, decoys only). The owner needs: <ol type="i"><li>the brief R2 §8 sequencing answer;</li><li>those decoy runtimes;</li><li>Q12's result under option (i) on that host.</li></ol>L-DET runtimes stay excluded | owner decision | as listed | O |
| 18 | D-TEXT-LAUNCHD | ENDORSE_WITH_CHANGES | "under the launchd launcher" becomes "under the reviewed launcher (L-LAUNCH)" in R-MEM step 1, brief R2 §6 MBS-8 (ii) (brief R2 line 241), and ratification items 30–31 (the launchctl timeouts become the reviewed systemd launcher's timeouts, with the same numbers) | AMENDS R-MEM step 1, MBS-8 (ii) wording, ratification items 30–31 | L-LAUNCH implementation review | O; I |
| 19 | D-ID-ZOMBIE | ENDORSE | **No**: a zombie proves nothing; current fail-closed behaviour | amends nothing | — | O |
| 20 | D-S15-NEWHOST | ENDORSE_WITH_CHANGES | (a) The owner names the authoritative store of the MB r1 formal refs. It is presumed to be the owner's MB r1 repository on the Mac (the "Mac store" of the packet's mechanism (2)), but this is **an owner fact, not verified here**. The canonical GitHub remote advertises **no** ref under `refs/p5y-k5-cell308-mb-r1/` (FR1 G7, `git ls-remote` 2026-10-16). (b) At every official step, the owner supplies a value-free listing of `git for-each-ref refs/p5y-k5-cell308-mb-r1/` from that store (ref names and ids only), signed or recorded in the owner's record. (c) The check asserts that `refs/p5y-k5-cell308-mb-r1/target-consumed` = `afa930727d084a5b70e6b85d30ca8f34c0e8ae74` is the **only** ref under that prefix. (d) An absent or unreadable listing refuses. (e) The owner statement that the store holds no pending ref, emergency file or MB r1 `evidence/` is kept, labelled SUBST. The route never pushes formal refs | NEW assertion mechanism for an accepted condition (gov A1 S15); **SUBST** for (e) | the owner's listing | O; I |
| 21 | D-HOST-LIFETIME | ENDORSE_WITH_CHANGES | Adopt `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R2_20261016.md` after its fresh bounded review accepts it. It corrects G9 (C fixes the bytes, HEAD's history the veto), G10 (anchor check procedure), G11 (split acceptance) and G26 (reviewer-reported digest; no self-asserted acceptance; agent identity). The appointing authority is the owner | NEW RULE | the fresh review of r2; then an attestation and its accepted review | O; I |

## 2. Lists the owner needs in one place

**Measurements replaced by an owner statement (SUBST; FR1 G20)**, for the owner and the S12 reviewer:
* D-LPM (no interface);
* D-POWER-ABSENT (mains supply);
* D-PAUSE (2), only if the bare-metal requirement is not chosen;
* D-S15-NEWHOST (e);
* the H1 lifetime statement;
* H3's `ATTESTED_NO_IMAGE_OR_OS_CHANGE`;
* H6's `root_cgroup_is_real`;
* H7.

**Rules for which ROUTE_PREPARATION line 19 must be expressly set aside (FR1 G36):** D-MEM-FREE, D-MEM-WIRED,
D-MEM-PRESSURE, D-THERMAL, D-LPM, D-EXCL-WINDOW, D-ALLOW-PATHS, D-ALLOW-BASE39.

**New host requirements, once decided:**
* D-WORKERS-CORES (≥ 6 physical cores);
* D-PAUSE (bare metal);
* D-MEM-PRESSURE (PSI);
* D-THERMAL (readable zones with trip points).

## 3. Dependencies between the items

* D-RC2-SCOPE and D-LDET-REPEAT depend on the S12 rating, which is advice.
* D-INTERPRETER, D-PIN-POINT, D-MEM-*, D-THERMAL, D-LPM, D-POWER-ABSENT, D-LID and D-WORKERS-CORES need host facts
  before their evidence exists. They can be **decided** as rules before a host exists.
* D-HOST-LIFETIME needs the fresh review of procedure r2.
* D-CAPS-CPU needs the official decoy runtimes, after the successor build.
* D-S15-NEWHOST needs the owner's listing at each step.
