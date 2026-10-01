# P309-r2 amendments to the inherited protocol (append-only)

**What this is.** The r2 plan (R2-I1) puts every r2 change to the inherited frozen protocol in this one append-only
file. The inherited texts (`fc2/FC2_SPEC_R2.md`, `governance/P309_REV2C_AMENDMENTS.md` and the other r1 governance
copies) stay byte-identical to r1's. Where they name r1's campaign, this record says how r2 reads them.

**What this is not.**
* It decides none of OD-R2-0 … OD-R2-6.
* Section A carries the **provisional** OD-R2-1 (b) names (addendum 2 F7). If the owner answers OD-R2-1 otherwise,
  section A is superseded by an appended section, with the re-implementation, delta review and re-drill that F7 states.
* It grants nothing, freezes nothing and authorizes no run.

**Origin.** Written 2026-10-01 by the coordinator, in response to the r2 delta review (`governance/REVIEW_R2_DELTA.md`,
conditions C7, C12 and C13).

## A. r2's production names (provisional, OD-R2-1 (b); review C12)

| item | r2 (provisional) | r1 (closed; stays forbidden) |
|---|---|---|
| ref namespace | `refs/p5y-k5-cell309-p309-r2/` | `refs/p5y-k5-cell309-p309-r1/` |
| production marker | `refs/p5y-k5-cell309-p309-r2/target-consumed` | `refs/p5y-k5-cell309-p309-r1/target-consumed` |
| pending-result ref | `refs/p5y-k5-cell309-p309-r2/pending-result` | `refs/p5y-k5-cell309-p309-r1/pending-result` |
| grant path | `level4/closure_proofs/p5y_k5_cell309_p309_r2/authorization/P309_GRANT.json` | the same path under `p5y_k5_cell309_p309_r1` |
| campaign | `p5y_k5_cell309_p309_r2` | `p5y_k5_cell309_p309_r1` |
| sealed result path | `level4/closure_proofs/p5y_k5_cell309_p309_r2/evidence/execution/P309_RESULT.json` | the same path under `p5y_k5_cell309_p309_r1` |
| result schema | `rebaseguard.p5y.k5.cell309-p309-r2.result.v1` | `rebaseguard.p5y.k5.cell309-p309-r1.result.v1` |

The code carries these names in `code/p309_guard.py` (`PRODUCTION_MARKER`, `PENDING_REF`, `_PROD_NAMESPACE`,
`_PROD_GRANT_PATH`), `code/p309_driver.py` (`SCHEMA`, `RESULT_REL`) and the verifier variant. No ref and no file with
any of these names exists, and none is created by anything in r2's development work.

**How r2 reads `fc2/FC2_SPEC_R2.md`.** Its §2 table, its §6 rules and its §7 scanner allowance name r1's campaign. For
r2 they read with r2's names from the table above. The rules themselves are unchanged: the allowance conditions §7
(a)–(e), the TEST context and the test fixtures.

## B. Forbidden names: r2's namespace added, r1's kept (FC2_SPEC_R2 §6; addendum 2 F1 and F7; review C12)

FC2_SPEC_R2 §6 "Forbidden names" is amended **by addition**. For r2 it reads:

* **The production marker name of either campaign, and any ref under `refs/p5y-k5-cell309-p309-r2/` or under
  `refs/p5y-k5-cell309-p309-r1/`, is never created anywhere.** That includes sandboxes, temporary namespaces, mock
  repositories, drill clones and controls. A control that needs a "prior evaluation" ref uses a TEST-only prefix in
  neither namespace (the drill uses `refs/p5y-k5-cell309-TEST-ONLY-prior/x`).
* The production grant path of either campaign is never written anywhere.

Where the bytes enforce it:
* the guard: `_FORBIDDEN_NAMESPACES` and the refusal in `TestContext`;
* the verifier variant: `FORBIDDEN_REF_NAMESPACES`;
* the verifier author's sandbox helper: `_FORBIDDEN_REF_PREFIX`;
* QC13: `no_exactly_once_ref` over both namespaces;
* the scanner: both namespaces in `production_tokens`, and the planted `TOKEN_R1` control;
* QC12 T12, with its committed negative controls T12a–T12c in `tests/test_p309_static_controls.py`.

## C. The execute gating rule on a shared host (review C7)

As the r2 bytes stand:
* The qualification run and QC10's host re-run start only through `code/p309_launch.py`:
  * modes `official` and `host-rerun`;
  * the exclusion gate, isolation and the durability preflight at the launch;
  * Q-HOST before the attempt directory;
  * the in-run monitor, its liveness and a final same-host sample.
* `code/p309_driver.py execute` and `seal-only` are **not** under the launcher, the exclusion gate or Q-HOST.

**The rule.** If the execution host the owner names (OD-R2-6, then the grant) runs another campaign's work, execute
may run there only after these steps, in order:
1. a reviewed amendment, appended here, that defines all of:
   * an exclusion gate and isolation check before execute's marker;
   * the durability preflight;
   * how a Q-HOST failure is handled before the marker (a refusal that spends nothing) and after it (a recorded
     EXECUTION_INDETERMINATE path that the existing post-marker rules accept);
2. the code implementing it;
3. a delta review;
4. a re-drill.

These bytes contain no such amendment. They support execute only on a host that runs no other campaign's work.
Whether to name such a host, or to ask for the amendment, is part of OD-R2-6. Nothing here names a host.

The frozen parameter file states the same rule:
* `post_grant_derivations.execution_host`;
* `proposed_execution_host`, which names a host only from the owner's own OD-R2-6 answer
  (`governance/OWNER_OD_R2_6_ANSWER.json`) and otherwise says that no host is proposed (review C8).

## D. Tree binding at the freeze, stated mechanically (P13; review C13)

Let **D** be the commit that the last passing worker-tier drill cloned: its report's `clone_base`. The last accepted
review of the r2 delta must cover D's code. Let **F** be r2's freeze commit, and `FNS2` be
`level4/closure_proofs/p5y_k5_cell309_p309_r2`.

At F, all of these must hold, each checked by the command shown:
1. **The code trees are those drilled and reviewed.** For each of `code`, `config`, `fc2`, `tests` and `verify`, the
   tree id at F equals the one at D:
   * `git rev-parse F:FNS2/<dir>` equals `git rev-parse D:FNS2/<dir>`.
2. **governance/ differs only by listed, reviewed additions.**
   * `git diff --name-status --diff-filter=MDRTCUX D F -- FNS2/governance` prints nothing.
   * Every path printed by `git diff --name-only --diff-filter=A D F -- FNS2/governance` is listed in section E, with
     its sha256 and the review that read it.
3. **freeze/ holds only the generated freeze files.** `git diff --name-only D F -- FNS2/freeze` lists only
   `freeze/P309_FREEZE_MANIFEST.json` and `freeze/P309_FREEZE.json`, as written by the unmodified generators at F.
4. **Nothing is added to a frozen directory after F.** For every later commit C on the branch,
   `git diff --name-only F C -- FNS2/code FNS2/config FNS2/fc2 FNS2/freeze FNS2/tests FNS2/verify FNS2/governance`
   prints nothing. After F, new material goes only to:
   * `qualification/`;
   * `ledger/`;
   * `reviews/`, under the driver's `QREVIEW_PREFIX`, for post-freeze reviews.

The review noted that the reviewed tree (`447e0713`) already differed from the drilled tree (`61731123`) in
governance/ only. Rule 2 is the general form of that case: such additions are allowed, but only when listed in
section E and reviewed.

## E. Reviewed governance additions after D

This list is empty in this first version of the record. Entries are appended at the freeze step, each with:
* its path;
* its sha256;
* the review that read it.

## F. Other r2 changes that this record points to (implemented; review C2–C11, C14)

These are implemented in the code. They are listed here so that the inherited texts are read with them.

**Q-HOST and the launcher** (plan §7; P10; C3–C5, C7, C9):
* the launcher has modes `drill`, `official` and `host-rerun`, each with a fixed unit name;
* the unit properties add `KillSignal=SIGKILL` and `TimeoutStopSec=10s`;
* the launch record is redacted, and binds the host configuration file by its sha256;
* the runner's Q-HOST preflight checks the unit's effective properties and the instance-id rule;
* the attempt keeps its start evidence;
* the abort kills its own process tree at once;
* the monitor's liveness and a final sample are checked at the stop;
* the host re-run runs under Q-HOST.

**Visibility under a separate user** (P9; C2):
* `foreign_uids` must be configured;
* another non-root user's process whose working directory cannot be read is `unattributable`, and counts as foreign
  at the gate and in the monitor;
* an aggregate foreign-CPU limit is enforced in the monitor (A8).

**Runtime binding** (P15; C14): the freeze manifest's runtime pins glibc and the sha256 of the interpreter binary,
and the driver's `check_bindings` compares both.

**QC12:**
* T13 also pins the module constants on the production read path (A10);
* the new T14 checks the runner's Q-HOST order (C6);
* negative controls for T11–T14 are in `tests/test_p309_static_controls.py` (C10).

**The scanner** (A7): sending a signal is a finding outside a reviewed function with the permit `signal`. The planted
control fires both new kinds.

**Committed host controls** (C11): `tests/test_p309_host_controls.py`.

## G. Corrections after the follow-up review (appended 2026-10-01; `REVIEW_R2_DELTA_FOLLOWUP_1.md` FU1, FU3)

**G1. §D and §E: where the list of governance additions lives (FU3).** As first written, §D rule 2 forbade any
modification of a governance file between D and F, while §E was to be appended to at the freeze step. Those two
rules contradicted each other. They are made consistent as follows, and this section supersedes §E:
1. **The list is a separate file.** The list of reviewed governance additions after D is kept in a separate file,
   `governance/R2_GOVERNANCE_ADDITIONS_AFTER_D.json`, added at the freeze step. Because it is added, rule 2 allows
   it. It is the one added path that rule 2 does not require to list itself.
   * Every other path printed by `git diff --name-only --diff-filter=A D F -- FNS2/governance` must be in it, with
     its sha256 and the review that read it.
   * It names D and F by their commit ids.
2. **This file is not changed between D and F.** §E stays as written: an empty list, superseded by G1.1.
3. **No governance file is modified between D and F.** Anything that must be recorded in that interval goes into a
   new file and is listed under G1.1. `git diff --name-status --diff-filter=MDRTCUX D F -- FNS2/governance` must print
   nothing (rule 2 unchanged).

**G2. §F: what the runner checks of its unit (FU1 (a)).** §F's phrase "the runner's Q-HOST preflight checks the
unit's effective properties" means exactly this: it refuses unless `Restart`, `KillMode`, `KillSignal`,
`NoNewPrivileges`, `PrivateTmp` and `ProtectSystem` have the launcher's values. `MemoryMax`, `OOMScoreAdjust`,
`CPUWeight`, `IOWeight`, `SendSIGKILL`, `TimeoutStopSec` and `InaccessiblePaths` are set by the launcher's command and
recorded in the attempt's `UNIT_PROPERTIES.json`, but not checked.

**G3. §F: whom "unattributable" covers (FU1 (b)).** It covers every non-root uid other than the P309 user's whose
working directory P309 cannot read, not only cell 308's: service accounts, other login sessions, and any access user
other than the P309 user. The operating procedure is in `R2_AWS_SESSION_INSTRUCTIONS.md` §4.1.
