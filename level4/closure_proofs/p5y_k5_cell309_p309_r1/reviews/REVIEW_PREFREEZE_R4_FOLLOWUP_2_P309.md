# Independent pre-freeze review R4, follow-up 2 (R4F-C3 focused confirmation and the D5 exception), formal campaign p5y_k5_cell309_p309_r1
FREEZE_BLOCKED
D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO

**Reviewer.** R4, the author of `reviews/REVIEW_PREFREEZE_R4_P309.md` (preserved at 879e6908) and
`reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md` (preserved at 68019506). R4 wrote none of the reviewed code. R4 is not
R1–R3, the incident-independence reviewer, the delta reviewer or the verifier's author. Brief:
`reviews/BRIEF_PREFREEZE_R4_FOLLOWUP_2_P309.md` (committed before issue).

**State reviewed.**
* The code is as of **7884122d**, the commit that adds the brief.
* The coordinator's addendum put **046b63aa** in scope, with tip 575136d1. I checked its diff against 7884122d: it
  changes only texts (`make_proposed_authorization.py`, `make_freeze_params.py`), the evidence, the manifest, the
  errata, the ledgers and the reviews. The driver, guard, scanner, static check, tests and config are byte-identical.
* The later commits up to 6122544f touch ledgers only.
* My runs used the working tree at those commits. Its code equals 7884122d, plus the 046b63aa texts.
* I recomputed the two ratified site hashes: `_arm_marker` `1ee764b7…` and `_persist_pending` `13ee3ec3…`. Both are
  unchanged and equal the owner-ratified values.

---

## 1. Verdict in brief

**FREEZE_BLOCKED.** The fixes asked for last time are in, and they work as far as they go:
* **F2 is closed.** That covers the narrowed placeholder test, validate-grant, the required worktree and the handoff
  text (§4).
* **The runtime backstop is correct against the shapes it was built for.** A test or tool that calls a ratified site
  directly, M13 and M14 of last round, is refused at runtime and rejected statically (T7). At runtime the refusal comes
  from the missing execute mode (B11a/B11b) or the missing grant (B01). A call to the assertion from anywhere but a site
  is refused as NOT_A_SITE (B10).
* **Schema 4 classifies every registered runner's callers.** All 20 runners were probed from an unlisted function:
  with `update-ref`, or for the script runners with a non-literal script. All 20 are rejected (R01–R20).
* **Every allowlist entry is necessary.** That holds for every `reviewed_functions` permit, every runner and every
  `ref_mutation_functions` entry, by ablation (§3.2).

| suite | result at 7884122d (+046b63aa texts) |
|---|---|
| D5 controls `tests/test_p309_d5_exception.py`, including M01–M15 | **101/101** |
| my M-suite (`reviews/R4_FOLLOWUP_D5_MUTANTS.py.txt`, M01–M18), static only | **18/18 rejected**, genuine tree passes |
| QC11 `tests/test_p309_exactly_once.py` | **103/103** (includes A27, A28 and V01–V09) |
| backstop controls `tests/test_p309_site_backstop.py` | **27/27** |

**One finding blocks the freeze: F3.** The owner's seven D5 classes are still **not** all rejected. The brief asked
for new mutants. **28 of the 54 new mutants pass the formal scan and static checks T1–T8 cleanly.** Of those:
* **3 are complete test-path or QC-tool paths** that reach `_arm_marker` with a production context. They neutralize the
  new backstop in-process: they forge the mode, replace the guard's pre-marker check through an alias and plant the run
  nonce. Read from the code (never executed), they would create the production marker with **no grant and outside
  execute mode**.
* **16 more are complete ways** to run an arbitrary program or write a ref file from code that the scan accepts:
  * git environment variables on read verbs;
  * `git grep -O`;
  * `ctypes`, `runpy`, `builtins` exec, `pickle` or `code`;
  * a ref path built with `chr()`.
* **4 are building blocks**, and **3 neuter the backstop inside the driver** while T8 still passes.
* **2 are inert or information only** (N17, N18).

Hence `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: NO`. The committed code itself contains none of these. The genuine tree
passes, and I found no path other than the two sites that mutates a production-namespace ref. The NO is about the guarantee the owner's ratification
requires: that the scanner **rejects** the seven classes. It is not about a defect in the code as written.

**About my own earlier conditions.** R4F-C1 and R4F-C3, read literally, are met:
* backstop, hardened scan and T7 in place;
* M01–M15 rejected;
* D5, my suite and QC11 run.

Last time I also wrote that with those in place "I would expect to answer YES". I cannot, for two reasons:
* **The brief asks for new mutants**, and the D5 question is whether the seven classes are rejected.
* **The backstop was meant to make static evasions harmless**, and the composite mutants neutralize it with code the
  static checks accept. So F1's core, "the only protection is static, and it can be evaded", still holds.

To make the next confirmation a finite target, the fix I ask for now is **closed-world**: allowlists, not further shape
rules. With it, **every mutant listed here becomes a control** (R4F2-C1).

G4 (the delta-3 reviewer's question): **yes**. `validate-grant` should also run `execute`'s read-only pre-marker checks
that do not depend on the grant commit, including the bindings and the governance state. I make this a condition
(R4F2-C2, §4.3).

---

## 2. Blocking finding

### F3. The seven D5 classes are still not all rejected: closed-world gaps in schema 4 and T7, and a backstop that can be neutralized in-process

All mutants were planted into temporary copies of `code/`, `config/`, `tests/`, `verify/` and `start_state/`. The
copies were **only parsed**, by `p309_scan.scan` and `p309_static_check.run`. Nothing was executed, and each copy was
deleted. The scripts are:
* `scratchpad/r4/d5_mutants2.py` (N);
* `scratchpad/r4/d5_mutants3.py` (K);
* `scratchpad/r4/d5_mutants4.py` (T);
* `scratchpad/r4/d5_mutants5.py` (R).

Their outputs are in `scratchpad/r4/run3_*.log`. The genuine copy (N00, K00, T00, R00) passes every check in every
suite.

**F3a. The composite test path defeats the backstop (classes 5, 6 and 7).** This is K01, planted as a new test file.
Names are assembled from pieces, as an evader would.

```python
import inspect, os, types
import p309_driver as D
import p309_guard as GG

def evil(head):
    dm = dict(inspect.getmembers(D)); gm = dict(inspect.getmembers(GG))
    h = GG
    h.premarker_check = lambda c: (True, "")                 # alias store: not seen by T7
    dm["_MO" + "DE"]["mode"] = "execute"                      # mode forged
    ctx = types.SimpleNamespace(kind="PRODUC" + "TION", guard_ctx=gm["PRODUC" + "TION"], ... repo=dm["RE" + "PO"])
    (dm["RE" + "PO"] / (chr(46) + "git") / ("p309-run-" + "nonce.json")).write_text('{"pid": %d, ...}' % os.getpid())
    dm["_arm" + "_marker"](ctx, head)
```

Each defence and why it fails:
* **The context shape.** `_assert_execute_context` compares `ctx.guard_ctx is G.PRODUCTION`, the names and `REPO`. All
  are satisfied by the real objects.
* **The caller check.** The caller is the real `_arm_marker`, so `_SITE_CODES` accepts it.
* **The grant check.** `_site_backstop` calls `G.premarker_check` through the module attribute, which the alias store
  replaced.
* **The nonce.** `_require_own_run_nonce` accepts any file naming the current pid.
* **The static checks.** T7 tracks only `import … as` aliases:
  * a local alias (`h = GG`) is invisible;
  * `inspect.getmembers` is not an introspection primitive T7 knows;
  * strings are checked only as whole constants;
  * the `chr()`-built git-dir path escapes GITDIR_WRITE.

**T7c needs no `inspect` at all.** It reaches the driver through another module:

```python
import p309_postexec as P
d = P.D                                   # T7 recognizes only `import p309_driver as X` and `X.G`
d.G.premarker_check = lambda c: (True, "")
getattr(d, "_MO" + "DE")["mode"] = "execute"
ctx = getattr(d, "production" + "_context")()
getattr(d, "_arm" + "_marker")(ctx, head)             # after planting the nonce as above
```

K04 is K01 as a QC tool in `code/`, and it passes too.

**The genuine tree contains a live instance of the alias gap.** `tests/test_p309_site_backstop.py:37` has `G = D.G`,
and lines 140 and 142 use `G.PRODUCTION`. T7 does not see this. The ablation (§3.2) shows that the file's
`PRODUCTION_REFERENCE` exemption rule is **unnecessary**: removing it produces no T7 finding. The use is benign
(SANDBOX-kind shape controls). The point is that T7 cannot see it.

**F3b. Git runs programs named by the environment or by read-verb options (classes 1–4).** The driver's
`git(..., env_extra=…)`, the tests' `sh(..., env=…)` and `p309_qualify.run(..., env_extra=…)` take any mapping, and
schema 4 does not look at it. None of the following is rejected:
* `git status` with `GIT_CONFIG_COUNT`/`KEY`/`VALUE` setting `core.fsmonitor` (a hook command): N04, and the same
  through the test runner (R21) and the QC runner (R23);
* `git diff` with `GIT_EXTERNAL_DIFF`: N05;
* `git ls-remote ssh://…` with `GIT_SSH_COMMAND`: N06;
* `GIT_CONFIG_GLOBAL` pointing to another config: N19;
* the same through a raw `subprocess.run([... 'git', 'status'], env={...})`: N20;
* `git grep --open-files-in-pager=<cmd>` and `git grep -O<cmd>`: N12 and N13. `grep` is an allowlisted read verb that
  no file uses.

The program named this way can run `git update-ref` on any ref. The genuine tree's only environment key on these calls
is `GIT_INDEX_FILE`.

**F3c. Exec primitives outside the process allowlist (classes 1–4).** None of these is rejected:
* `ctypes.CDLL(None).system(b"…")` with the marker name in a **bytes** literal: N01. The token rules check only `str`
  constants.
* `runpy.run_path` of a `.txt` file: N02. `.txt` is an allowed suffix, and its content is not parsed as Python.
* `__builtins__["ex" + "ec"]`: N07.
* `builtins.__dict__["ex" + "ec"]`: N08.
* `pickle.loads`: N09.
* `code.InteractiveInterpreter().runsource`: N10.
* A ref file written through `os.path.join(REPO, chr(46) + "git", chr(114) + "efs", …)`: N11.

Only `importlib.machinery.SourceFileLoader` (N03) is caught, as PROCESS_ALIAS.

**F3d. T8 checks shape, not behaviour.** T8 accepts a backstop whose checks are all disabled, as long as the required
substrings remain. Examples:
* `if _MODE.get("mode") != "execute" and not ctx:` and `if not ok and not ctx:` (T8a);
* a nonce reader that substitutes `{"pid": os.getpid()}` when the file is missing (T8b);
* a nonce reader whose mismatch branch is `pass` (T8c).

All three pass the scan and T1–T8. They are edits to the reviewed driver, so the risk is lower. But the backstop is the
one runtime layer, so its AST should be pinned like the sites'.

**The mutants and their results** (scan = formal scan verdict; T = static checks failed):

| id | shape | where | D5 class | scan | T |
|---|---|---|---|---|---|
| K01 | inspect + alias store + forged mode and nonce + site call | tests/ | 5, 6, 7 | PASS | none |
| K04 | the same | code/ (QC tool) | 5, 6, 7 | PASS | none |
| T7c | driver reached as `P.D` through `p309_postexec`; getattr with computed names | tests/ | 5, 6, 7 | PASS | none |
| K02 / K03 / N16 / T7b | building blocks: `inspect.getmembers(D)`; guard alias store; `sys.modules['p309_' + 'driver'].__dict__` | tests/ | 4 | PASS | none |
| N04 N05 N06 N19 N20 R21 R23 | git environment runs a program | driver, rehearse, tests, qualify | 1–4 | PASS | none |
| N12 N13 | `git grep -O` / `--open-files-in-pager` | driver | 1–4 | PASS | none |
| N01 N02 N07 N08 N09 N10 | ctypes / runpy .txt / builtins exec ×2 / pickle / code | rehearse | 1–4 | PASS | none |
| N11 | ref file path built with `chr()` | driver | 3, 4 | PASS | none |
| T8a T8b T8c | backstop or nonce neutered, same shape | driver | 5, 6 | PASS | none |
| N18 | `GIT_PAGER`/`PAGER` on `git log` (probably inert: no terminal) | driver | — | PASS | none |
| N17 | `multiprocessing.Process` (information only; the target is scanned) | rehearse | — | PASS | none |
| N03 | `SourceFileLoader(...).load_module()` of a `.json` file | rehearse | 4 | FAIL (PROCESS_ALIAS) | T5 |
| N14 N15 | direct store on the driver alias / `D.G.x = …` | tests/ | 5–7 | PASS | T7 |
| T7a | `importlib.import_module('p309_' + 'driver')` | tests/ | 4 | FAIL (DYNAMIC_IMPORT_UNRESOLVED) | T5 |
| T7d | the composite written plainly in the T7-exempt `p309_postexec.py` | code/ | 5–7 | FAIL (GITDIR_WRITE, PROCESS_ALIAS) | T5 |
| R01–R20 | every registered runner called with `update-ref` / an opaque script from an unlisted function | each runner's file | 1–3 | FAIL | T5 |
| R22 | as R21, in `tests/test_p309_guard.py` | tests/ | 1–4 | PASS | T7, only incidentally: the edit voids the file's hash-bound exemption |

**What I would accept as the fix.** It is R4F2-C1, stated in full under Conditions. The idea is to replace shape rules
with allowlists that the genuine tree already satisfies:
* **Imports.** Allowlist the imports per directory. The genuine tree imports none of ctypes, runpy, pickle, inspect,
  builtins or code.
* **Introspection.** Forbid the introspection primitives outside AST-pinned reviewed functions. The genuine tree uses
  none of `__builtins__`, `builtins`, `setattr` or `delattr`. Its few existing uses can each get an AST-pinned permit:
  * `getattr` with a non-literal name once, in the guard's context proxy (`p309_guard.py:433`);
  * `vars` only on a SimpleNamespace in the backstop test;
  * `globals()` only in the guard;
  * `sys.modules`, `__dict__` and `_getframe` only in the driver, the static check, the scanner and the D5 test.
* **Module attribute stores.** Forbid stores on any module object, however it was obtained.
* **Environment keys.** Allowlist the environment keys on every runner and subprocess call: `GIT_INDEX_FILE` only.
* **Git options.** Give each verb its own option allowlist, and remove the 17 verbs no file uses.
* **Bytes constants** fall under the token rules.
* **Unresolved paths.** A write through an unresolved path piece directly under the repository root, or anywhere under
  its git dir, is a finding.
* **AST pins** for the backstop functions, and for `p309_postexec.py`'s T7 exemption.
* **Controls.** Every mutant above becomes a control.

A runtime process-origin check at the arm site is useful as defence in depth, but it is not required. In-process code
can forge that too, so the closed-world static rules are the real fix.

---

## 3. Task 1: R4F-C1 (F1)

### 3.1 (a) The runtime backstop

This is `_assert_execute_context`, `_site_backstop` and `_require_own_run_nonce` (driver lines 168–221), together with
`_SITE_CODES` (line 1171).
* **It is the fix I described, for the scenarios I described.** The caller must be one of the two sites' code objects.
  The arm site requires execute mode, `G.premarker_check` passing now, and a run nonce naming this process. The pending
  site requires the marker, the marker's commit carrying the grant path, and, in execute mode, the nonce. The site ASTs
  are unchanged.
* **It is correctly fail-closed.** In the edge case the delta-3 review noted (§2.1 there), a grant that expires between
  admission and arming leads to a refusal before the marker. Nothing is consumed.
* **The controls exercise it.** B01–B11, with 27 controls, cover:
  * no grant, no nonce, another pid's nonce, seal-only and no mode for arm;
  * no marker, an ungranted marker, no nonce and a mode outside execute/seal-only for pending;
  * the allowed cases, including a second arm refused;
  * a direct call and a wrapper refused as NOT_A_SITE;
  * `_SITE_CODES` read-only;
  * every context-shape refusal;
  * no production-namespace ref in any sandbox or in this repository.

  All pass at this tree.
* **Limit (F3a, F3d).** Every input the backstop trusts can be replaced by in-process code: the guard module attribute,
  `_MODE`, and the nonce file. So it is a real barrier against a *mistaken* call, and no barrier against *deliberately
  evasive* code the static checks accept. It is sound only together with closed-world static rules.

### 3.2 (b) Scanner schema 4

**Runner classification.** R01–R20 plant, in each registered runner's own file, an unlisted function that calls the
runner with `update-ref refs/heads/r4probe HEAD`. For the script runners the function passes a non-literal script
name. **All 20 are rejected**, as REF_MUTATION_UNLISTED, or as PROCESS_UNLISTED plus RUNNER_UNREGISTERED. For the git
runners the finding is REF_MUTATION_UNLISTED, not an opaque-call finding. So the verb was identified, which it would
not be with a wrong `leading` or `list` field.

**Necessity and minimality, by in-memory ablation** (`scratchpad/r4/perm_ablation.py`, 609 s). I removed each item
from the scanner's loaded allowance, one at a time, and re-scanned the genuine tree read-only:

| allowlist | items | necessary (removal makes the scan FAIL) | unnecessary |
|---|---|---|---|
| `reviewed_functions` permits | 43 entries, 49 permits | **all** | none |
| `git_runners` | 20 | **all** (RUNNER_UNREGISTERED) | none |
| `ref_mutation_functions` | 17 | **all** | none |
| `git_read_verbs` | 26 | 14 | **12**: archive, check-ignore, cherry, count-objects, describe, diff-index, grep, name-rev, shortlog, show-ref, verify-pack, version |
| `git_object_verbs` | 11 | 6 | **5**: add, index-pack, mktree, pack-objects, unpack-objects |
| `t7_exemptions` rules | 4 | 3 | **1**: `tests/test_p309_site_backstop.py` PRODUCTION_REFERENCE. It is unnecessary only because of the T7 alias gap (F3a) |

**Reasons.** I read the reasons of the new and changed entries against the code:
* the `ref_mutation_functions` removals: `production_context`, `sandbox_context`, `_check_official`,
  `TestFC2Scoped.fresh`, `_admission`, and the D5 test's `run`;
* the additions: `test_p309_site_backstop.run` and `validate_flows`;
* the rehashes;
* the three `forwards_operands` permits: `p309_qualify.mirror`, `Sandbox.commit` and `_changed_paths`.

The reasons are true:
* The removed functions use only `symbolic-ref -q HEAD`, or no longer move a ref. This is consistent with the genuine
  scan passing: an unlisted ref mover would fail it as REF_MUTATION_UNLISTED.
* The added functions move TEST refs in sandboxes only.
* The three `forwards_operands` functions fix the verb and forward operands only.

The permits are minimal. The verb lists are not: the 17 unused verbs should go. `grep` is among them, and it is the
one that enables N12 and N13.

**Forwarding into program or verb position.** No registered runner forwards a parameter into program or verb position
without being registered. `_forwards_params` enforces this, and R18–R20 confirm it for the script runners. One gap
remains: operand forwarding can carry an option, for example `mirror("--output=…")` into `git archive`. The callers
pass git-produced commit ids, so today it is inert. Putting `--end-of-options` before forwarded operands would close
it (note in R4F2-C1(e)).

**Gaps.** The allowlist is not closed over the environment, exec primitives, bytes tokens, computed paths and
per-verb options (F3b, F3c).

### 3.3 (c) T7 and T8

**What T7 now catches.**
* It covers every `*.py` file whatever its name (M01).
* Its exemptions are rule-specific and bound to the file's AST hash. R22 shows that an edit voids them.
* It catches direct and `from`-imports of the forbidden names, `__dict__` and `__getattribute__` on the aliases, stores
  on the driver and guard aliases, `getattr` and similar calls on the aliases, `sys.modules["p309_driver"]` with a
  constant name, and the forbidden names inside `python -c` strings. My M13 and M14 are rejected.

**What T7 misses.**
* local aliases, and modules reached through another module (`P.D`, `G = D.G`);
* computed names;
* `inspect` and similar;
* `sys.modules` with a computed key;
* the blanket name exemption of `code/p309_postexec.py`, which is not AST-bound (F3a).

**T8** verifies the backstop's structure by string shape only (F3d).

**The seven D5 classes at this tree:**

| class | rejected for the shapes of last round (M01–M18) and all registered runners (R01–R20) | not rejected |
|---|---|---|
| 1 additional marker site | yes | N01, N02, N07–N10 (exec primitives); N04–N06, N12, N13, N19, N20, R21, R23 (git runs a program) |
| 2 additional pending site | yes | the same |
| 3 unreviewed ref mutation path | yes | the same, plus N11 (`chr()` ref path) |
| 4 dynamically constructed equivalent | yes (M04, M05, M10) | N07, N08, N11, T7b, K01 (computed names) |
| 5 reachable without execute mode | yes for a direct call (B04, B11a/b, T7) | K01, K04, T7c; T8a–T8c in the driver |
| 6 reachable without a valid grant | yes for a direct call (B01, T7) | K01, K04, T7c; T8a–T8c |
| 7 test/QC path mutating production refs | yes for M13, M14, N14, N15 | K01, T7c (tests), K04 (QC tool) |

---

## 4. Task 2: R4F-C2 (F2)

### 4.1 Closed

* **`PLACEHOLDER_MARKS`.** It is now exactly the proposal's two placeholder openings: `("<THE OWNER'S GRANT
  INSTRUCTION", "<SET BY THE OWNER")` (driver line 97). A27, an authority quoting the owner with `->` and `<…>`, is
  admitted. V02, the placeholder, is refused. This removes the trap.
* **`validate_grant`** (lines 603–647). It reads the candidate file, HEAD, status, the branch, the manifest, the
  recorded freeze and the target cell's pinned `cells.json` interval. That last read is ledgered as an exposure line,
  and G3 discloses it as a liability. It walks the chain with `walk_chain`, the same function as `check_grant`. It runs
  `grant_content_checks`, the same function as `premarker_admission`, and `G.candidate_check` (guard checks 2, 3 and
  5–9, plus the field parser). Its only writes are one `E.log` and one `E.exposure` line, in the PRODUCTION context
  only. It creates no commit and no ref, and runs nothing of Stage 1 or 2. `clean_tree_before` is computed before its
  own ledger writes. The CLI entry is T1-checked: MODE_ENTRIES `validate-grant` reaches no target function.
* **Agreement with `execute`.** V01 (a valid candidate passes) and V09 (the same candidate committed alone is admitted
  by `execute`) both pass. V02–V08 each fail on the intended check and leave the sandbox unchanged ("same"). A28 and V03
  refuse a missing worktree.
* **Handoff text** (046b63aa, `grant_rules.grant_validation`).
  * It now says what validate-grant checks and what only `execute` checks.
  * It says that a PASS does not guarantee admission.
  * It gives the order: ledger-only commit, then the grant alone.
  * It says that a refused grant commit is terminal without a new owner decision.

  This is correct for the code at 7884122d. Once R4F2-C2 is applied, it must move the added checks to the "checks"
  list.

### 4.2 Note (non-blocking)

* **NF3.** V09 commits the grant **directly** on the validated HEAD, because a sandbox validate-grant writes no ledger
  lines. The production handoff inserts **one ledger-only window commit** between validation and the grant.
  * Window commits are admitted elsewhere in QC11.
  * But no V-flow exercises this exact production sequence: validate, then a window commit touching
    `ZERO_TARGET_LEDGER` and `EXPOSURE_LEDGER`, then the grant, then `execute` admits.

  Add it as V10.

### 4.3 G4: should validate-grant also run the read-only bindings and governance-state checks?

**My call: yes, as a condition (R4F2-C2).** It is an implementation change, not a new delta, as the delta-3 reviewer
says.

**Why.** Any refusal after the grant commit is terminal. So every avoidable refusal cause that can be checked before
the grant commit should be. The strongest remaining causes are host-specific, and only a run on the execution host can
see them:
* **`check_bindings`** hashes the worktree bytes of every pin, and also checks the interpreter implementation. A clean
  `git status` does not imply byte equality. On a host with `core.autocrlf`, a smudge filter or a sparse or partial
  checkout, git can report clean while the bytes differ from the pinned sha256. `execute` would then refuse with
  PIN_MISMATCH, after the grant.
* **`check_governance_state`** runs `git log --all` for the R6 name. `--all` sees every ref of the host clone, including
  branches the chain walk never looks at.

**Why it is safe.**
* Both checks are read-only, and hash-only on the pinned inputs: no values are parsed.
* Both already run in `preflight` mode, which T1 checks.
* Their result at the would-be parent equals their result at G, because check 4 lets G change only the grant path.

**The same reasoning covers the other read-only pre-marker checks that do not depend on G:** `check_flags`,
`check_not_evaluated` and `check_result_paths`. What legitimately stays execute-only:
* guard check 4, the grant commit itself;
* the consumer-cover agreement, which loads the consumer;
* the historical control, which is a computation. Its failure is exit 3, not consumed.

---

## 5. Task 3: R4F-C3 runs

All runs used `python3 -I -S -B` and `P309_EVIDENCE_DIR=scratchpad/r4/evidence2`. The test modules ran unchanged
through my wrapper `scratchpad/r4/r4c2_run.py`, which only redirects their `SCRATCH` into `scratchpad/r4`. That kept
the coordinator's concurrent dry run undisturbed. Sandboxes were light repositories with TEST names only, and all were
deleted.

| run | ledger UTC | result |
|---|---|---|
| QC11 without `validate_flows` (my wrapper's list was incomplete; superseded) | 07:03:46 | 94/94 |
| backstop controls | 07:03:49 | **27/27** |
| D5 controls (M01–M15 included) | 07:03:52 | **101/101** |
| QC11 with all six flow groups, as the module's `__main__` | 07:14:14 | **103/103**: A27, A28, V01–V09 and Z (no production-namespace ref anywhere) pass |
| my M-suite, M01–M18 (the committed `.py.txt`, identical to my scratch copy except for the ledger purpose text) | 07:16:26 | **18/18 rejected**; M00 genuine passes |
| new mutants T (T7, T8) | 07:22:49 | 2/7 rejected |
| new mutants N (schema 4) | 07:24:17 | 3/20 rejected |
| new mutants K (composite) | 07:28:11 | 0/4 rejected (a re-run of 07:00:31 and 07:01:33 with output captured) |
| allowlist ablation | 07:30:52 | §3.2 |
| runner probes R | 07:33:08 | 21/23 rejected (R22 only incidentally) |
| site and backstop AST hashes | 07:40:17 | sites unchanged; backstop hashes `c8a2fb51…`, `80d206ad…`, `23f3021d…` |

The counts match the coordinator's dev results: D5 101/101, backstop 27/27, QC11 103/103.

---

## 6. Task 4: R4F-C4

* **NF1: accepted.**
  * `grant_content_checks` requires `execution_host.worktree` to be a non-empty string that resolves to the context
    repository (line 569).
  * A34 records this.
  * QC11 A28 (missing worktree refused) and V03 (validate-grant refuses it) pass.
* **NF2: accepted.** Addendum 2 of the qualification-review brief tells the reviewer to check the attempt tree and the
  committed execution ledger together: exactly one `QUALIFICATION RUN START` line after the freeze record, and exactly
  one `attempt_1`.
* **NF4 (non-blocking addition).** The same check should confirm that the execution ledger is append-only over F..Q:
  each committed version is a byte prefix of the next. Otherwise a deleted attempt directory **and** its deleted
  ledger line would leave no trace.

---

## 7. Task 5: readiness

Apart from F3 (R4F2-C1) and G4 (R4F2-C2), nothing else blocks the freeze from my side:
* B1–B8 and F2 are closed.
* The whitelists are necessary and their reasons are true. The one exception is the 17 unused verbs, which belong in
  R4F2-C1.
* The site hashes are the ratified ones.
* The runs pass.

The delta-3 conditions G1–G9 are the coordinator's. I checked only G4's text.

**Non-blocking.**
* **NF3** (§4.2) and **NF4** (§6).
* **NF5.** The git runners pass `HOME` through, so the execution host's system, global and repository git config apply
  to `execute`'s git calls. A host config with `core.fsmonitor` or `core.hooksPath`, or a `reference-transaction` hook
  in the git dir, runs a program during those calls, including the marker's `update-ref`. The owner controls the host.
  Still, validate-grant could refuse if any of these is set, and so could `execute`'s pre-marker checks. That is
  cheap, and it turns a silent host dependency into a checked one.

---

## Conditions

* **R4F2-C1 (F3; before the freeze).** The formal scan and T7 reject the owner's seven D5 classes by closed-world
  allowlists, not by call shape:
  * **(a) Imports.** Every Python file under `code/`, `tests/`, `verify/` and `start_state/` imports only modules on a
    per-directory allowlist in `SCANNER_ALLOWANCE_P309.json`. The following are never allowlisted except inside an
    AST-pinned `reviewed_functions` entry with a true reason:
    * ctypes, cffi, runpy, pickle, marshal, shelve, code, codeop, inspect, gc, multiprocessing, concurrent, pty and
      builtins;
    * `importlib.machinery`, `importlib.util` and `importlib.abc`.
  * **(b) Introspection.** Outside AST-pinned reviewed functions, each of the following is a finding:
    * `getattr`, `setattr`, `delattr` and `hasattr` with a non-literal name or on a module;
    * `vars`, `globals`, `locals` and `dir`;
    * `__dict__`, `__getattribute__`, `__builtins__`, `__globals__`, `__code__`, `f_globals` and `f_locals`;
    * any `sys.modules` access and `sys._getframe`;
    * `__import__`;
    * `object.__setattr__` and `type.__setattr__`;
    * `exec`, `eval` and `compile` under any spelling.
  * **(c) Module attribute stores.** In tests and QC tools, a store or delete on an attribute of a module object is a
    finding however the module was obtained. That includes an import alias, a local alias, an attribute of another
    project module (`P.D`, `P.D.G`, `G = D.G`) and a `sys.modules` lookup. It is allowed only by a rule-specific,
    AST-hash-bound `t7_exemptions` entry. T7's alias tracking follows the same bindings.
  * **(d) Environment.** `env` / `env_extra` on every runner and subprocess call is one of:
    * `None`;
    * a module-level fixed environment, or one built inside an AST-pinned reviewed runner;
    * such an environment extended by literal keys from an allowlist. The allowlist is `GIT_INDEX_FILE` for the
      genuine tree.

    `p309_qualify.run`'s unused `env_extra` parameter is removed.
  * **(e) Git verbs and options.**
    * Each allowlisted verb has its own option allowlist. At least `-O` and `--open-files-in-pager` are forbidden.
    * The 17 verbs that no file uses are removed. They are: archive, check-ignore, cherry, count-objects, describe,
      diff-index, grep, name-rev, shortlog, show-ref, verify-pack, version, add, index-pack, mktree, pack-objects,
      unpack-objects.
    * Forwarded operands are preceded by `--end-of-options` or validated.
  * **(f) Tokens and paths.**
    * `bytes` constants are subject to the token rules.
    * A file suffix that is allowed but not parsed (`.txt`, `.md`, `.json`, …) is never opened as code. N02 becomes
      rejected, and N03 stays rejected.
    * A write whose target has an unresolved path piece directly under the repository root, where it could be `.git`,
      or anywhere under the git dir is a finding (REF_FILE_WRITE / GITDIR_WRITE) unless reviewed. Examples of
      unresolved pieces: `chr()`, or a join of non-literals. The same applies when the base itself is unresolved.
  * **(g) Backstop pins.** T8 is an equality check. The AST sha256 of `_assert_execute_context` (`c8a2fb51…`),
    `_site_backstop` (`80d206ad…`) and `_require_own_run_nonce` (`23f3021d…`), and the `_SITE_CODES` statement, are
    pinned in the allowance like the two sites. They are reported to the owner with the D5 record.
  * **(h) `p309_postexec.py`.** Its blanket `T7_EXEMPT` entry becomes a rule-specific, AST-hash-bound `t7_exemptions`
    entry.
  * **(i) Controls.** My mutants are added as D5 controls, each rejected, and the genuine tree passes:
    * N01–N16 and N19–N20;
    * K01–K04;
    * T7a–T7d and T8a–T8c;
    * R01–R23.

    The sources are `scratchpad/r4/d5_mutants2.py` to `d5_mutants5.py`, or equivalent committed copies. N17 and N18
    are optional.
* **R4F2-C2 (G4; before the freeze).**
  * `validate-grant` also runs, in the PRODUCTION context exactly as `run_execute` does:
    * `check_flags`, `check_not_evaluated` and `check_result_paths`;
    * `check_bindings` and `check_governance_state`.
  * It reports each in `checks`, and PASS requires all of them.
  * T1's `validate-grant` entry set lists them, and T1 still passes.
  * A static control checks that `validate_grant` calls them under the same condition as `run_execute`.
  * `grant_rules.grant_validation` moves them to the list of what validate-grant checks.
  * This is an implementation change, not a new delta.
* **R4F2-C3.** A focused confirmation by R4 or another independent reviewer, at the tree containing R4F2-C1 and
  R4F2-C2:
  * the D5 controls, including every mutant of R4F2-C1(i) and M01–M15;
  * the backstop controls;
  * one QC11 run under `-I -S -B`.

  Only then `D5_EXCEPTION_LIMITED_TO_RATIFIED_SITES: YES` and FREEZE_APPROVED.
* **R4F2-C4.** R4F-C4 is satisfied: NF1 is applied, and NF2 is accepted as addendum 2 of the qualification-review
  brief. NF3 (V10), NF4 (the ledger append-only check) and NF5 (the host git-config check) are applied or recorded as
  accepted residuals.

---

## 8. Disclosures

**Reads.**
* FNS and RNS files, and git metadata.
* The code at 7884122d.
* The 046b63aa diff.
* `governance/P309_REV2C_AMENDMENTS.md` (Third delta, A31–A36 and the A32 addendum).
* `governance/D5_SITE_BACKSTOP_REPORT_P309.md`.
* `reviews/REVIEW_DELTA3_INCIDENT_P309.md` (G4).
* The qualification-review brief (addenda 2 and 3).
* The execution ledger: my own lines, and the other lines in my run window, to separate my runs from the
  coordinator's.
* No consumer code, no target input and no 305–309 value. No `code_skeleton.py` call was needed this round.
* I did not open THEOREM_TCT.md.

**Indirect reads by the test code I ran.** QC11's integration flows verify the committed TEST-band h3 decoy
certificates in review mode. I03 composes the committed a2_h5 decoy certificates with manufactured Stage-1b records.
No cover-cell entry and no campaign results file is read, and nothing was displayed.

**Executions.** All carry notes prefixed "R4 reviewer:" and `new_target_evaluations` 0. Times are ledger UTC on
2026-09-30:

| UTC | what | class |
|---|---|---|
| 06:56:12 | N mutants, first run (static) | GOVERNANCE |
| 07:00:31 | K mutants, first run (static) | GOVERNANCE |
| 07:01:33 | K mutants, `os` imported plainly (static) | GOVERNANCE |
| 07:03:46 | QC11 without `validate_flows`, 94/94 (superseded) | NONTARGET_DECOY |
| 07:03:49 | backstop controls, 27/27 | SYNTHETIC |
| 07:03:52 | D5 controls, 101/101 | GOVERNANCE |
| 07:14:14 | QC11, 103/103 | NONTARGET_DECOY |
| 07:16:26 | my M-suite (static) | GOVERNANCE |
| 07:22:49 | T mutants (static) | GOVERNANCE |
| 07:24:17 | N mutants, re-run with output captured (static) | GOVERNANCE |
| 07:28:11 | K mutants, re-run with output captured (static) | GOVERNANCE |
| 07:30:52 | allowlist ablation (in memory, read-only scans) | GOVERNANCE |
| 07:33:08 | R runner probes (static) | GOVERNANCE |
| 07:40:17 | site and backstop AST hashes (read-only) | GOVERNANCE |

Scratch copy of these 14 ledger lines: `scratchpad/r4/evidence2/R4_FOLLOWUP2_EXEC_LEDGER.jsonl`. Results:
`scratchpad/r4/evidence2/R4C3_*.json` and `scratchpad/r4/run3_*.log`, where `scratchpad/r4` is
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/r4`.

**How the executions were contained.**
* Sandboxes were light repositories (alternates) under `scratchpad/r4`, with TEST names only, never pushed, and
  deleted.
* Mutant copies were parsed only, never imported or executed, and deleted. The directories `mut`–`mut5` are removed.
* The ablation changed only the in-memory allowance of my own process.

**What was never done.**
* `execute`, `seal-only` and `validate-grant` were never run against this repository.
* **K01, K04, T7c, N01–N20, T8a–T8c and R01–R23 were never executed.** Their runtime effect in §2 is read from the
  code.
* No ref was created, armed or consumed under `refs/p5y-k5-cell309-p309-r1/` anywhere. There are 0 such refs here and
  0 `refs/p309-test/` refs here, checked after all runs.
* The production grant path was never written.
* No git write was made.
* No kernel ran in [6/5, 13/5] or its mirror.
* Nothing was evaluated for cells 305–309.

**Writes.** This file only, plus my ledger lines through `p309_env`, and scratch files under `scratchpad/r4`.

NEW Γ309 TARGET EVALUATIONS = 0.
