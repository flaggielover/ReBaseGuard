# C11RD-R1Q — qualification of the C11RD-R1 freeze

Scope: QUALIFICATION ONLY of freeze `ce5b85959a1693525f9e001e7c191516a4ee7d76`, whose pre-execution
review (preserved at `3c1eff11562638727156f09a9c58b8dc704548a5`) is READY_TO_QUALIFY. No
authorization, no grant, no target execution, no comparison. No cell-306 D1/D2 magnitude has been
computed. Nothing under `code/`, `protocol/`, `theory/` or the frozen documents was changed: every
frozen hash is still valid.

## 1. What was added (outside the frozen scientific object)

| path | role |
|---|---|
| `qualification_r1/code/c11rd_qualify.py` | the qualification checks Q01–Q10 and the artifact writer |
| `qualification_r1/code/c11rd_launch.py` | the qualified LAUNCHER: the only permitted entry for the one execution |
| `evidence/qualification_r1/C11RD_R1_QUALIFICATION_CHECKS.json` | every check with its evidence |
| `evidence/qualification_r1/validation/` | the frozen validation suite re-run (29/29) |
| `evidence/qualification_r1/C11RD_R1_QUALIFICATION.json` | the qualification artifact (binds everything below) |
| `evidence/qualification_r1/POST_WRITE_LEAK_SCAN.json` | leak scan of every namespace file after all evidence was written |
| this document | human reading, note dispositions, errata |

The launcher and the checks import the frozen modules read-only; the frozen runner's pre-import
barrier (exactly eight files in `code/`) is unaffected because the new code lives in
`qualification_r1/code/`.

## 2. Checks (all run with `python3 -I -S -B`; governance git is `/usr/bin/git --no-replace-objects -c core.commitGraph=false` with an explicit PATH=/usr/bin:/bin environment)

* **Q01 entry identity** — the freeze commit exists and is an ancestor of HEAD; the freeze JSON/MD on
  disk equal those at the freeze commit; the review file equals `3c1eff11`'s (sha256 `dd4ccbda…`)
  with exactly one verdict line, READY_TO_QUALIFY; since the review only qualification paths change.
* **Q02 historical cleanliness** — on every ref, reflog entry and full history (read by this tool AND
  by the frozen reader `c11rd_model.history_commits`): no run, lock, seal, comparison, grant or
  authorization/execution review path; none on disk; no `refs/c11rd/*`; not shallow; no grafts or
  shallow file; no replace refs; C11R byte-identical since `7375b9cd`; nothing outside the namespace
  changed; r5 unchanged; no r6; LOCAL_MAIN_REF `c123b9bb…` and cached origin/main `1cb45382…` (the
  live remote was also checked at entry).
* **Q03 scientific object** — target cell 306 only on `[680769/400000, 17885921/10000000]`; the
  four-sub-block exact tiling; 168 initial boxes; refinement (tolerances 1/100000, 1/20000, 1/2000;
  depth 2; splits); Taylor order 6; 34 moment terms; float proposal; recurrence and D1/D2 formula
  texts; the production `propagate` and `atom_values` equal the formulas on 50 random rational
  instances; maximum aggregation (AST); factor-2 rule; one-execution policy; caps 43,200 s / 2 GiB /
  5 workers; the upper-closed convention (freeze and production `owner_band`); cover completeness;
  the original-value quarantine (blob-bound; the comparator reads it only after U0, U1 and U3); V29
  identity with `71495747`.
* **Q04 hashes** — the eight frozen code files (and only those in `code/`), C7's `c7_gaussian.py`
  (sha256 and blob), all eight input blobs, the eight frozen document hashes.
* **Q05 validation** — the frozen suite, re-run: **29/29 PASS**.
* **Q06 host/runtime** — see section 3.
* **Q07 git/history hardening** — scratch repositories: an artifact committed then deleted is found;
  a CORRUPTED commit-graph is not consulted (plain git reports a chunk-offset error; the hardened
  reader is unaffected); a replace ref does not hide the commit; hostile `GIT_DIR`, `GIT_WORK_TREE`,
  `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`,
  `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_COUNT/KEY/VALUE`, `GIT_REPLACE_REF_BASE`,
  `GIT_CEILING_DIRECTORIES`, `GIT_CONFIG_GLOBAL/SYSTEM` and a poisoned PATH change nothing for the
  frozen history reader, the comparator's U0 or the launcher; grafts and shallow history fail
  closed; an artifact committed only in a DETACHED linked worktree is found; a path alias yields the
  same history and worktree identity; the real repository is clean under the hostile environment.
* **Q08 execution lifecycle** — (a) the frozen runner's real mode calls, in this order: grant check,
  clean-tree check, loaded-module check, exclusive lock, the certifier, the atomic artifact write;
  the cover/accounting guard precedes any mode; nothing removes the lock; NOT_CERTIFIED writes no
  value; the comparator turns NOT_CERTIFIED into INSUFFICIENT. (b) The predecessor matrix on a
  scratch lineage through the frozen `grant_problems`: the complete lineage is accepted; a missing
  freeze commit, qualification commit, qualification review (commit or file), authorization review,
  an out-of-order lineage, platform-only, input-bindings, git-common-dir-only deviations, a
  QUALIFICATION_REJECTED or duplicated qualification verdict, an AUTHORIZATION_REJECTED verdict, a
  grant absent at the authorization review, and an ancestor freeze commit carrying a different
  freeze file are all refused. (c) Attempt semantics of the PRODUCTION runner on the non-target
  block: an unreadable process table gives NOT_CERTIFIED / RESOURCE_ACCOUNTING_FAILED before any box,
  a memory cap gives RESOURCE_CAP_MEMORY, a wall cap RESOURCE_CAP_WALL. (d) The launcher end to end
  with a STUB runner in scratch repositories (see section 4).
* **Q09 reviewer-note checks** — N-1, N-2, N-3, N-13 (section 5).
* **Q10 broad leak scan** — every namespace file, every decimal (plain, bare-point, scientific),
  integer-mantissa scientific and rational token against both disclosed original values (supplied on
  stdin, never stored): no token within 1e-4 relative.

## 3. Host and runtime (bound in the artifact)

Hostname, hardware UUID (IOPlatformUUID), platform `darwin`, Python 3.14.5 — the runner's
`grant_host`; interpreter realpath `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14`
with its sha256 and `-I -S -B`; canonical worktree `/Users/suzhe/ReBaseGuard-k5c11rd`, git common
dir `/Users/suzhe/ReBaseGuard/.git`; macOS 26.5.2 (25F84), arm64, 6 cores; 8 GiB RAM; free disk;
five spawn workers with the isolated flags; `/bin/ps` read 500 times without a failure; the runner's
cap clock is `time.time()` (a wall clock that keeps running while the machine sleeps); `/usr/bin/caffeinate -i`
assertion verified in `pmset -g assertions`; git 2.50.1; sha256 of every standard-library module the
runner loads.

Launch limits (governance, not science): 1-min load ≤ 2.0, free disk ≥ 2 GiB, available memory
≥ 1 GiB (about 5× the ~210 MB peak process-tree RSS of the frozen runner's rehearsals). At
qualification time the load was about 2.7 (the qualification jobs themselves); the launcher enforces
the limits at launch.

**Review N-7 (accepted limitation) — binding requirement for any future authorization:** the
execution runs on an otherwise idle host, on mains power with the lid open, with idle sleep prevented
by the launcher's `caffeinate -i -w <launcher pid>` assertion, which the launcher verifies before
consuming the authorization.

## 4. The qualified launcher and the execution lifecycle

freeze → qualification → qualification review (QUALIFICATION_ACCEPTED) → grant at
`config/C11RD_GRANT.json` + authorization review (AUTHORIZATION_ACCEPTED) → exactly one execution
THROUGH THE LAUNCHER → immediate seal → execution review → comparison → adjudication.

The launcher (`qualification_r1/code/c11rd_launch.py`) is the only permitted entry. It:
L1 re-executes itself with only PATH, HOME, LANG and GIT_NO_REPLACE_OBJECTS (PEP 538 and macOS add
LC_CTYPE and __CF_USER_TEXT_ENCODING; anything else refuses) and replaces `os.environ` before any
frozen call; L2 runs a preflight that creates nothing (qualified host, interpreter, worktree; the
frozen `grant_problems` empty; the grant's freeze commit exactly `ce5b8595` and its qualification
paths exactly the canonical ones; the frozen runner's hash; idle host, disk, memory, process table;
no other runner; no consumed ref; clean namespace); L3 starts and verifies the caffeinate assertion;
L4 creates the create-only ref `refs/c11rd/r1-execution-consumed` in the common git dir; L5 runs the
frozen runner once, logging outside the worktree and forwarding SIGINT/SIGTERM/SIGHUP; L6 seals
IMMEDIATELY: one commit of `evidence/runs/` only (artifact, `.partial`, lock, log — whatever exists)
on top of the start HEAD, without reading any value.

Attempt semantics (verified with a stub runner, Q08):

| attempt | outcome class | sealed | consumed |
|---|---|---|---|
| success (exit 0) | COMPLETED_CERTIFIED | artifact + lock + log | yes |
| cap or accounting failure (exit 3) | COMPLETED_NOT_CERTIFIED | artifact + lock + log | yes |
| process failure | CONSUMED_NO_RESULT | lock + log | yes |
| interruption (signal forwarded) | CONSUMED_NO_RESULT | lock + log | yes |
| runner refusal before its lock | REFUSED_BEFORE_LOCK | log | yes (launcher rule) |
| a second launch | refused in preflight | nothing | — |

Fail-closed behaviour is not weakened for retryability: any launch that passes preflight consumes
the authorization; a new execution needs a new, independently reviewed authorization.

## 5. Disposition of the R1 review's notes

| note | class | how |
|---|---|---|
| N-1 `point_box` lower-closed | QUALIFIED | every call uses a globally continuous candidate or none and no interior `s >= 4` point (Q09; 151 calls instrumented); frozen file not edited |
| N-2 V24 exclusion via state value | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q09: kernel-level exclusion for Khat orders 0, 1, 2 at s = 2, 3, 4, interior and axes (36 rows) |
| N-3 V25 weak containment | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q09: tiny state boxes, order 6, frozen proposal; width < 1e-3 of the residual at both endpoints |
| N-4 nontarget mode trusts the on-disk freeze | ACCEPTED_LIMITATION | rule: no rehearsal after this qualification except on explicit instruction, from a clean tree with the committed freeze; the target path is bound by R2 |
| N-5 governance git inherits the environment | HARDENED_OUTSIDE_FROZEN_SCIENCE | the launcher's sanitized environment (Q07, Q08); residual: deliberate forgery by a trusted operator |
| N-6 worktree-local lock | HARDENED_OUTSIDE_FROZEN_SCIENCE | consumed ref in the common git dir; automatic immediate seal |
| N-7 reachable history only | ACCEPTED_LIMITATION | inherent |
| N-8 qualification paths from the grant | HARDENED_OUTSIDE_FROZEN_SCIENCE | canonical paths and the exact freeze commit fixed here and enforced by the launcher |
| N-9 stale docs / FORBIDDEN list | ACCEPTED_LIMITATION | errata below; the convention is immutable through the frozen hashes and guard R6 |
| N-10 U7 needs a decimal point | QUALIFIED | Q10 broad scan clean |
| N-11 one failed `ps` consumes the execution | QUALIFIED | fail-closed kept; 500/500 reads; launcher pre-check; idle host required |
| N-12 missing V26 deviations | HARDENED_OUTSIDE_FROZEN_SCIENCE | Q08 matrix |
| N-13 R6 whole-block list | QUALIFIED | Q09: each per-sub-block list complete and geometrically identical |

No note requires a new freeze.

## 6. Qualification run history (defects of the qualification tool, found and fixed before the recorded run)

1. The first full run hung in Q10: its scientific-notation pattern also matched inside hex digests
   (e.g. `...0e87612345...` read as 0 x 10^87612345) and Python began building a huge power of ten.
   Stopped; tokens must now stand alone (no letter or digit around them) and exponents have at most
   three digits. The frozen comparator's tokenizer requires a decimal point and is not affected
   (V18 scans every file in well under a second).
2. The second full run failed Q06 `five_isolated_workers`: the probe's tasks were trivial, so the
   first spawned worker finished all twenty before the others started (1 distinct worker). Each probe
   task now lasts one second; five workers are seen. This was a probe defect, not a host limitation
   (the rehearsals used five workers).

The recorded evidence is the third full run, made after both fixes; nothing under `code/` changed.

## 7. Errata (hash-bound documents are not edited; these entries supersede their wording)

* `docs/C11RD_ARCHITECTURE.md` (module table and the one-execution paragraph) and the freeze JSON's
  `K_success_failure` say "R0–R6": the runner also checks R7 (memory accountability) before the
  lock; the freeze records it in `runner_guards.R7` and `K_r1_additional_not_certified_reason`.
* The freeze JSON's `FORBIDDEN` list does not repeat the band-convention clause stated in
  `protocol/C11RD_FREEZE_R1.md` ("any change of the band-ownership convention"). The convention is
  bound by `E_state_domain_partition.band_ownership`, the frozen `c11rd_certify.py` hash
  (`owner_band`, `verify_cover`), the frozen theory hash and runner guard R6; changing it changes a
  frozen hash and guard R1 refuses.
* `code/c11rd_validate.py` `point_box`: its docstring says "the band that owns (p, m)" but it
  selects bands lower-closed; it is a validation helper only (N-1).
* The freeze JSON's `entry_head` is the campaign entry `7375b9cd`; the R1 round's entry was
  `663f8fe7` (bound in `successor_of`).
