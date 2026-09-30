# Incident-independence review of the FOURTH rev. 2c delta (A37–A42; conditions C2, D8, delta-3 G8, G9), formal campaign p5y_k5_cell309_p309_r1
DELTA4_INDEPENDENCE_ACCEPTED

**Standard.** As before, temporal and parametric independence only. The conditions are H1–H8, in the section headed
"Conditions" below. H2–H4 must be met before the freeze.

**Reviewer.** I am the independent incident-independence reviewer. I wrote:
* `reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`;
* `reviews/REVIEW_U2_CHECK_P309.md`;
* `reviews/REVIEW_DELTA_INCIDENT_P309.md`;
* `reviews/REVIEW_DELTA2_INCIDENT_P309.md`, with its follow-up 1;
* `reviews/REVIEW_DELTA3_INCIDENT_P309.md`.

I did not produce or coordinate the campaign.

**Brief.** `reviews/BRIEF_DELTA4_INCIDENT_P309.md`, committed at bfa18252 before it was issued (C5 respected).

**Reviewed state.**
* The code and governance are at bfa18252. The brief's tip, 6f6c1e7c, adds only a checkpoint record.
* Two commits landed during the review: 49bf2e95 (ten execution-ledger lines) and 5781b6da (a checkpoint record). I
  cover the ledgers through 5781b6da.
* I read committed bytes only. The working tree carries further uncommitted ledger lines from the running dry run
  part 4, which I did not read (H5).

**Written.** 2026-09-30, 08:57–09:05Z.

**Ledger** (reads and runs):
`/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/delta4review/D4_LEDGER.jsonl`.

---

## 0. Verdict in brief

**ACCEPTED, on temporal and parametric independence.**

* **Sources.** Every row comes from R4 follow-up 2 (F3; R4F2-C1, -C2 and -C4), from my own delta-3 G4 question, or
  from a coordinator finding about the host's git configuration. None of these depends on a target quantity.
* **Scope.** The rows change only:
  * static code-path rules;
  * the pinning of already-reviewed code;
  * pre-grant validation;
  * `execute`'s git environment.

  They change no Stage 1a, 1b or 2 code, budget, gate, decoy, band or outcome rule. The driver diff is limited to
  `ENV`, `REPO_CONFIG_ALLOWED`, `check_host_git`, validate-grant's pre-checks and one call in `run_execute`.
* **A38** pins code that is unchanged since R4 recorded its hashes. I compared the ASTs at 7884122d and HEAD. It is
  fail-closed.
* **A40** cannot change the result of a correct run.
  * The record is fixed in memory, and persisted as a blob and pending ref, **before** the seal commit.
  * The only thing A40 changes after the marker is the seal commit's metadata: a fixed identity and no signature.
    Nothing checks either.
  * It removes a probable host-dependent seal failure.
  * Its pre-marker refusal depends only on the host's git version, repository config key names and hooks. It is
    outcome-neutral, and validate-grant surfaces it before the grant commit.
* **Exposures.** From 77991be1 to 5781b6da, 266 new execution-ledger rows and no new exposure rows. None records a
  target evaluation, a tail cell, or a drift in the band or its mirror. Nobody saw a 305–309 value.
* **Result-chasing component: LOW.**
* **What must happen before the freeze.**
  * The R4 follow-up-2 liability understates F3 (H2).
  * The fourth-delta rule choices need a liability entry (H3).
  * Two handoff texts need precision: the `host_git` key list, and the timing of `grant_validation` (H4).

**Delta-3 conditions.**
* G2–G5 are met:
  * the grant carries the delta-3, delta-4 and R4 follow-up 2 and 3 conditions;
  * the three G3 items are listed;
  * the `grant_validation` text is corrected;
  * FE-11 and its liability are recorded.
* G6 is met by §3, for committed rows up to 5781b6da.
* G8 is met by A38.
* G7 stands (H6).

---

## 1. Task 1: each row

| row | kind | source | direction for closure | basis target-free? |
|---|---|---|---|---|
| **A37** scanner schema 5 (closed-world imports, introspection, module stores, environments, per-verb git options, token and path folding, controls) | implementation / controls: static rejection of code paths | R4F2-C1 (a)–(f), (h), (i); the owner's D5 classes | none. It can fail qualification on code **shape** only. It needed no driver change | yes: R4's mutants N, K, T and R |
| **A38** backstop pinned by AST hash; T8 is an equality check; never refreshed | **binding** | R4F2-C1(g); my G8 | fail-closed | yes. ASTs of `_assert_execute_context`, `_site_backstop`, `_require_own_run_nonce` and the `_SITE_CODES` statement are identical at 7884122d and HEAD; the two sites are unchanged |
| **A39** validate-grant runs `execute`'s read-only pre-marker checks; T9 | implementation (as delta-3 G4 classed it) | R4F2-C2 | toward a conclusive outcome: host-specific refusal causes appear before the grant commit. Not toward any particular outcome | yes. Same functions and conditions as `run_execute`; `check_bindings` hashes the pinned inputs and parses no values |
| **A40** hermetic git (`GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_GLOBAL=/dev/null`, fixed identity); pre-marker `check_host_git` | **binding** (the git environment) and **rule** (a new pre-marker refusal) | R4F2 NF5; the coordinator's `commit.gpgSign` finding | after the marker: removes a host-dependent seal failure. Before the marker: fail-closed and outcome-neutral (§2) | yes: host configuration only |
| **A41** QC11 V10; QC13 `execution_ledger_append_only_since_the_freeze` | controls | R4F2 NF3, NF4 | none. It makes a hidden second attempt harder | yes |
| **A42** `--end-of-options` in the verifier author's sandbox helper | implementation | R4F2-C1(e); verifier-author follow-ups 3–5, each brief committed before issue | none. The same semantics for every operand that does not start with `-`. The variant file, tests and batch runner are unchanged | yes |

**Other code.** `p309_qualify.py` drops the unused `env_extra` and passes `--end-of-options` to `git archive`; the
mirror content is the same. `p309_self_audit.py` and `p309_scan_pins.py` extend lists. The tests add V10 and
controls. No QC command, parameter or threshold changes.

---

## 2. Task 2: A40

**The seal commit: no signing, fixed identity. Could a correct run's outcome change?** No.

**Why not.**
* In `after_marker`, the order is:
  1. the evaluation;
  2. the record's bytes are serialized in memory;
  3. `_persist_pending` writes them as a blob and a pending ref;
  4. then `seal_blob` makes the commit, whose tree entry must equal that blob.
* A40 changes only step 4's commit metadata: the author and committer `p309-execute`, and no signature.
* The record, `mechanical_outcome` and `target_evaluations` are fixed before step 4.
* I searched `code/` and `verify/` for any check on a commit's author, committer or signature, including in the
  postexec and review mode, and found none.

**What it removes.**
* On the development host, the global `commit.gpgSign` with an ssh signing program would have run inside `commit-tree`.
* `ENV` does not carry the ssh agent variables, so that signing would probably have failed. The result would then be
  UNSEALED (exit 4), with `seal-only` failing the same way.
* A40 therefore only removes a host-dependent post-marker failure.
* The A21 `committer_identity` check now always passes, because the identity is fixed. That is harmless.

**The Stage-1 jobs.** They receive `ENV`, so they now also get six git variables.
* The job code reads no environment variable. The only `os.environ` read in the driver is `ENV`'s `HOME`, in the
  parent.
* The jobs run under `-I`.
* So the computation is unaffected.

**Is the pre-marker refusal outcome-neutral?** Yes.
* `check_host_git` depends only on:
  * the host's git version (≥ 2.32);
  * the repository config key names by scope, against `REPO_CONFIG_ALLOWED`;
  * the presence of hooks.
* It runs before the marker, right after the flags check, and validate-grant runs the same function before the grant
  commit.
* No target quantity enters it.

**Side effects of ignoring the global config.** A host that needs `safe.directory` or a global excludes file now
refuses before the marker (HOST_GIT or CLEAN). That is fail-closed. validate-grant shows it before the grant commit,
provided it runs as the same user in the same worktree, as the procedure says.

**On this host.**
* git 2.43.
* The repository's own config keys are all inside the allowlist. The only keys outside it were command-scope keys from
  my session's environment, which `execute`'s fixed `ENV` does not inherit.
* There are no hooks.

So no spurious refusal is expected here. The execution host remains the owner's choice.

**Note for R4 follow-up 3, not a condition.** `run_seal_only` does not call `check_host_git`. A hook added between
`execute` and `seal-only` would run at seal-only's `update-ref`. This is recovery mechanics, not independence.

---

## 3. Task 3: new exposures (from 77991be1 on)

**Exposure ledger.** There are no new rows. The last row is still the delta-2 E4 retrospective row.

**Execution ledger, 77991be1 to 5781b6da.**
* 266 rows, appended only, with no line removed.
* Dated 06:53:35Z to 08:57:30Z.
* By class: 183 NONTARGET_DECOY, 57 SYNTHETIC, 26 GOVERNANCE.

**Sources.**
* **The coordinator's pre-freeze dry runs, parts 2–4.**
  * Opening lines.
  * Research tests: part 2's last line still reads "qualification:"; later lines read "dry run (pre-freeze,
    development)", per FE-11.
  * Decoy Stage 1a on the declared a2_h5.
  * QC09 decoy Stage 1b on cover cells 297 and 316. These stay latent-proxy class; I did not read their outputs.
  * 102 SRK certification lines on the declared a2_h5 decoy.
* **R4 follow-up 2.** 14 rows, matching its disclosure table.
* **The verifier author's follow-ups 3–5.** 6 run and result lines, plus 111 per-test lines of
  `tests/test_verify_scoped.py`.
  * The `D1_real_band_production_context_dry` and `N09` lines are SYNTHETIC, with no drift, and record a refusal.
  * The `TestKernelClosedForm` lines carry one drift each, out of band.
* **The coordinator's development runs.** QC12, the D5 controls, QC11, the backstop, guard and allowance controls.

**Checks, done mechanically; I printed no interval.**
* `new_target_evaluations`, `target_informed_optimisation` and `target_equivalent_proxies` are 0 on every row.
* No `drifts` entry meets the band or its mirror.
* Of the 164 interval pairs in purpose or notes text, none meets the band or its mirror.
* No row touches a cell 305–309.
* No row names `cells.json` or THEOREM_TCT. The only "cell309" strings are campaign path names.
* No production validate-grant, proposal, `execute` or `seal-only` ran.

**Answer.** On the ledgers' evidence, nobody saw a 305–309 value in this window.

---

## 4. Task 4: liabilities and texts

**The R4 follow-up-2 item understates F3.** It says "28 of 54 … passed …, three of which neutralize the backstop
in-process". R4's own breakdown is:
* 3 complete test-path or QC-tool paths to the production marker with no grant and outside execute mode;
* **16 complete ways to run an arbitrary program or write a ref file**;
* 4 building blocks;
* 3 in-driver neuterings that T8 did not catch;
* 2 inert.

The committed code contained none of them. The liability should say so (H2).

**The A40 finding item is accurate:** the host's global config, the signing program in the seal, removed, and the
direction. It should add that the seal commit now carries the fixed identity and no signature, so the record's
provenance rests on the marker, the pending ref and the chain (H3).

**`host_git`.**
* The freeze-parameter text is accurate.
* The proposal's text lists the allowed keys as "core format and file-mode keys, remote url/fetch, branch remote/merge,
  gc.auto, user name/email". That is a strict subset of `REPO_CONFIG_ALLOWED`: it omits, for example, `core.bare`,
  `core.logallrefupdates`, `remote.*.pushurl`, `branch.*.rebase` and the two `extensions.*` keys.
* That errs on the safe side, but it is not exact (H4).

**`grant_validation`.** Both texts are now accurate about what validate-grant runs and what only `execute` runs. One
point should be added. The time-dependent checks, the 14-day horizon and the expiry, are re-evaluated when `execute`
starts. A PASS followed by a delay can therefore turn into a terminal refusal. The `horizon_notice` covers this
implicitly; the handoff step should say it (H4).

**Missing.** The fourth-delta rule choices with direction, and "fourth delta result-chasing component LOW" (H3).

---

## Conditions

* **H1 (wording).** The fourth delta is accepted on **temporal and parametric independence only**. C1–C8, D1–D8,
  E1–E10 and G1–G9 continue. G6 is discharged for the committed rows up to 5781b6da.
* **H2 (R4 follow-up-2 liability; before the freeze).** State F3 as R4 classified it:
  * 28 of 54 static-only mutants passed schema 4 and T1–T8;
  * 3 were complete test-path or QC-tool paths to the production marker with no grant and outside execute mode;
  * 16 were complete ways to run an arbitrary program or write a ref file;
  * 4 were building blocks;
  * 3 were in-driver backstop neuterings that T8 passed;
  * 2 were inert;
  * the committed code contained none of them.
* **H3 (liabilities; before the freeze).** Add:
  * **(a) the fourth-delta rule choices, with direction:**
    * A38: a fail-closed binding.
    * A40 after the marker: toward a conclusive outcome, removing a host-dependent seal failure. The seal commit
      carries the fixed identity `p309-execute` and no signature.
    * A40 before the marker: the host-git refusal is fail-closed and outcome-neutral. It requires git ≥ 2.32 and an
      allowlisted repository config, with no hooks, on the execution host.
    * A39: toward a conclusive outcome.
  * **(b)** "fourth delta result-chasing component LOW".
* **H4 (handoff texts; before the freeze).**
  * The proposal's `host_git` key list either equals `REPO_CONFIG_ALLOWED` or is marked as examples.
  * The `grant_validation` handoff step states that `execute` re-evaluates the horizon and expiry checks when it
    starts, so the grant commit and `execute` should follow a PASS promptly.
* **H5 (later ledger lines).** The next independence or qualification review covers the execution-ledger rows after
  5781b6da, including the rest of dry run part 4 and R4 follow-up 3's runs.
* **H6 (standing).** At the freeze:
  * the third-delta item's "re-confirmed (R4F-C3)" and the R4 follow-up-2 item's "resolved before the freeze" are true,
    and cite R4 follow-up 3's verdict;
  * the two sites keep the owner-ratified AST hashes;
  * the backstop keeps the A38-pinned hashes.
* **H7 (the git environment is binding).** `ENV`, `REPO_CONFIG_ALLOWED` and `check_host_git` are frozen as R4 follow-up
  3 confirms them. Any change after that confirmation is a new delta under C2.
* **H8 (later changes).** Any further rule, parameter or binding change after this review is a new delta under C2.

---

## 5. Reviewer disclosures

**Exposures.** None to any 305–309 value. I saw:
* code and governance text of the formal namespace;
* R4's follow-up 2 review;
* ledger rows, summarised mechanically by class and flags, with purpose texts only in masked or grouped form;
* the key names of this repository's git config, with subsection names masked, and the hook count;
* top-level facts of the development evidence.

In the tail of the committed rows I also saw declared-decoy (a2_h5) drift intervals, out of band, which I do not
reproduce. I opened no cell-307 or cell-308 campaign file, and no THEOREM_TCT.

**Executions.**
* Read-only `git` and `grep`.
* `PYTHONDONTWRITEBYTECODE=1 python3 code/p309_scan_pins.py --list` (read-only).
* `git config --list --show-scope --name-only` and `git --version`.
* An in-memory `ast.dump` comparison of six driver definitions between two commits.
* Small read-only Python summaries, in scratch, of the ledger rows, printing flags and counts.

I ran no evaluation, no kernel run and no git write.

**Writes.** This file only.

---
