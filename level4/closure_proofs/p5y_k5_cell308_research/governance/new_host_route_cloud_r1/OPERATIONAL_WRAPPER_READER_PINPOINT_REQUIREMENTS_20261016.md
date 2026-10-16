# Requirements: operational wrapper (A1 / A2), journal reader (L′) and fixed pin point (A5) — Cell-308 Cloud route r1

**Status: PROPOSED REQUIREMENTS · NOT IMPLEMENTED · NOT ACCEPTED.** These are the requirements a reviewed successor build
must meet before the conditions A1, A2 and A5, and the journal-reader gap, can be discharged. Implementation waits for
the route acceptance and the design decisions named below (governing sequence: route acceptance and decisions,
actual-host evidence, reviewed implementation). `new_target_evaluations = 0` · `cell309_activity = none`.

Condition sources: the Codex amendment review `REVIEW_CLOUD_R1_DELTA_R3_CODEX_AMENDMENT.md` findings A1, A2 and A5 (PR2
line `3b244277`), carried by Codex r4 §12 and its erratum E1. They are traced in
`FORMAL_ROUTE_READINESS_PACKET_20261016.md` §5. Development reference: `streams/CLOUD_R1_LINUX_DEV/lx_platform.py` at
`9db01504` (sha256 `da32ce8c…6389`).

## 1. A1 — memory provenance: the operational memory wrapper

| # | requirement | development state at `9db01504` | test / review evidence required |
|---|---|---|---|
| A1.1 | The only production entry point for memory quantities takes **one** input: `attestation_ref` (a pointer to committed files). It never passes `mem_text`, `proc_cgroup_text` or `root`, which are test locations. | `memory_readings(mem_text=None, proc_cgroup_text=None, root="/sys/fs/cgroup", *, attestation_ref=None)` has these test parameters | a static check (AST) over the successor build: no production call site passes them |
| A1.2 | Root provenance is derived inside, never supplied. All of these must hold: the initial cgroup namespace; D-HOST-LIFETIME in `DECIDED`; `attestation_valid` accepts the reference; the record states `root_cgroup_is_real: true`. | implemented in `root_attestation()` | existing tests and mutants (RV-series, P2); the implementation review confirms the production path |
| A1.3 | A number labelled as an R-FREE or R-MEM quantity exists only after D-MEM-FREE and D-MEM-WIRED are decided. It is computed by the decided formula, by one function named after the rule, with the inputs recorded. | `memory_readings` gives raw quantities side by side; `lx_verified.observe` withholds `effective_limit` and headroom | unit tests of the decided formula on synthetic chains, plus a mutant per term |
| A1.4 | A partial chain, an unreadable level, or a non-initial namespace never yields a number. | implemented (`visible_limit_upper_bound` only) | existing tests |
| A1.5 | The wrapper records every raw reading next to the rule quantity, so the qualification can recompute it. | not implemented | a review of the record schema |

## 2. A2 — launcher corroboration: the operational launch wrapper

| # | requirement | development state | evidence required |
|---|---|---|---|
| A2.1 | `execute` and `resume` run only inside the campaign's systemd service `rebaseguard-mbs308-<mode>.service`, started by the reviewed launcher. The unit file is committed with its sha256. | `launched_by_systemd()` checks PID 1, the cgroup unit, `INVOCATION_ID`, `MainPID` and `InvocationID` | a committed unit file; a synthetic dry launch of a non-science service on the official host (H2) |
| A2.2 | `preflight` always takes a **fresh** `launched_by_systemd()` reading with default arguments (no `env`, `proc_cgroup_text`, `show` or `pid1`). A passed record must equal it. | implemented (P6) | a static check that no production call passes those seams |
| A2.3 | `other_job_running` comes from the reviewed launcher's pidfile check (as in the candidate), never a literal. | caller input | an implementation review of the launcher |
| A2.4 | The test seams (`env`, `show`, `pid1`, `proc_cgroup_text`, `power_root`, `suspend_text`, `apt_dump`, `unit_roots`, `maps_text`, `query`) may be passed only by files under `tests/`. | convention only | an AST lint in the harness that fails on any non-test call site passing a seam, with a mutant that adds one |

## 3. Journal reader for channel L′ (L-SLEEP)

Today `JOURNAL_READER_REVIEWED = False`, so no interval can be CLEAN. The requirements for a reader:

| # | requirement |
|---|---|
| J1 | **Source.** The systemd journal of the **current boot**, read with `journalctl --boot=<boot_id> --since=<start> --until=<end> -o json --no-pager` under the same isolation discipline as the git reads (allow-listed environment, no pager, timeout). The kernel and `systemd-sleep` records only. |
| J2 | **Events.** A sleep event is any entry of: `systemd-sleep` (`Entering sleep state`, `System returned from sleep`); kernel `PM: suspend entry` / `PM: suspend exit` / `PM: hibernation entry`; `systemd-logind` suspend or hibernate requests. The patterns are fixed in the accepted text, and a reviewer checks them against the host's systemd and kernel versions. |
| J3 | **Completeness.** The journal must be persistent (`Storage=persistent` with `/var/log/journal` present), and the reader verifies the cursor sequence has no gap over the interval. Rotation or vacuuming inside the interval, rate-limit suppression messages (`Suppressed … messages`), or an unreadable journal ⇒ L′ unavailable ⇒ AMBIGUOUS. |
| J4 | **Fail closed.** Any parse error, an unknown event shape, a wrong boot id, or a timeout ⇒ AMBIGUOUS, never CLEAN. |
| J5 | **Tests.** Synthetic journals covering each event, each gap and rotation case, and malformed records, with a mutant per rule. The reader is independently reviewed, and the review is bound by a ledger line before `JOURNAL_READER_REVIEWED` may become `True`. |
| J6 | **Scope.** L′ covers OS suspend only. A hypervisor pause stays undetectable from the guest (D-PAUSE); the reader does not change that. |

Dependency: H2 (systemd on the official host) and the host's journal configuration (an owner setting, H3 / H5
procedure). The reader can be written and tested synthetically once the route text accepts J1–J6.

## 4. A5 — the fixed import list and pin point

| # | requirement |
|---|---|
| P1 | **The list (`PIN_POINT_MODULES`).** The static transitive import closure of the reviewed successor's evaluation entry point. It includes at least the S11 modules (`mb308_stage1`, `mb308_supply`, `mb308_consumer`, `mb308_a0core`, `mb308_pinned`), their certifier imports, and every standard-library and extension module they import. It is computed by **static analysis** (AST over the successor build at a named commit, never by importing or executing science). It is written into the accepted amendment with the successor commit and the tool's sha256. |
| P2 | **The wrapper.** Each computing mode (`decoy`, `execute`, `resume`, qualification cases) has one entry module that imports the whole list with top-level static `import` statements, then calls `pin_point()` before any evaluation, and again at every resume. No dynamic import anywhere on the path (the research quarantine scanner already refuses unresolvable dynamic imports). |
| P3 | **Late imports.** A module imported after the pin point is a pin defect. The pin is re-read at the end of each computing mode and compared. Any new mapped object ⇒ the run is invalid (before the marker) or close-indeterminate (after it), as the RC2 pin rule already says for a resume. |
| P4 | **Tests.** Synthetic: undefined list refuses (existing); a missing module refuses (existing); an entry module that omits one module refuses; a late import is detected. The implementation review confirms P1's closure on the actual build. |

Dependency: the successor build (ROUTE_PREPARATION step 3), D-PIN-POINT, D-INTERPRETER.

## 5. What can be done before the dependencies, and what cannot

* **Now (synthetic, isolated worktree, no science):** the AST seam lint (A1.1, A2.2, A2.4) could be added to the
  development harness, and a synthetic journal-reader prototype written against J1–J6.
* **Implementing now is not recommended.** Both are design choices the formal review should accept first, and A1.3 needs
  D-MEM-FREE / D-MEM-WIRED. Changing the tested development source would also invalidate the final validation
  binding (`9db01504`, run 38848711278) without a decided design to justify it.
* **Not now:** P1 (no successor build), A2.1 on a host (no host), J3 on a host.
