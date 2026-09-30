# ENOSPC incident of 2026-09-30 and the integrity audit of step L (coordinator editorR3C1)

**What happened.** The data volume ran nearly full while builder3 (step L) and builder4 (brief 46) were running
sandbox-heavy suites and mutant matrices: 5.3 GiB free was observed; builder4 reported ENOSPC early in its build and
readings below 1 GiB at times. Cause: each MB-S mutant-matrix run leaves about 0.8 GB of sandbox per mutant (about 40
GB per full run), and two finished matrix runs (the editor's and reviewR3C1's) had not been cleaned.

**Cleanup (2026-09-30T08:59:48Z).** The coordinator deleted ONLY the `sbx` sandbox clones and bare `base_store.git`
stores in two FINISHED scratch areas (`scratchpad/editor`, `scratchpad/reviewR3C1`): 126 directories, listed in
`COORDINATOR_DELETED_SANDBOXES.txt`. Nothing under the repository, no JSON report, probe, review, ledger, ref or
active builder scratch was touched. About 105 GB were reclaimed (110 GiB free afterwards).

**Audit method.** `ENOSPC_AUDIT_TOOL.py.txt` (read-only) over builder3's reports and per-mutant result files: parse
every JSON; list failures with their error text; scan every report, log and result for disk-exhaustion signatures
(ENOSPC, "No space left", Errno 28, short write, truncated, unexpected EOF, JSON decode errors); flag zero-length or
unparseable files; classify every mutant as killed by assertion, killed by error, survived or missing. Output
`ENOSPC_AUDIT_STEP_L.json`. The real repository was checked with `git fsck --no-dangling` (clean) and every commit
made during the window resolves its tree.

**Findings.**
1. **One contaminated run:** builder3's first run of the six liveness mutants (report 07:15Z). Its unmutated phase
   failed on infrastructure ("fatal: unable to write new index file", an "invalid object" during a sandbox checkout,
   and a sandbox directory removed mid-run by builder3's own cleaner). Its "6/6 killed" is therefore meaningless. It is
   preserved unchanged as `CONTAMINATED_builder3_L2_mutants_new.json` (sha256 b79b821d… equals the original) and was
   superseded by (a) builder3's re-run at 07:22Z (6/6 killed by assertion, unmutated all pass) and (b) the full
   57-mutant matrix run after the cleanup (09:11-09:47Z: 57/57 killed by assertion, unmutated all pass, no error).
2. **Signature hits are all false positives:** every "truncated" match is the name of the planted test case
   `t_S06_truncated_result` or its "truncated" sub-case; no ENOSPC / Errno 28 / "No space left" text anywhere else.
3. **No bad JSON:** every report and per-mutant result file parses; none is zero-length (the two zero-length
   `MX2_alerts.*` files are builder3's empty disk-alert logs).
4. **Pre-cleanup suites** (static 10/10, launch 10/10, state 46/46, crash 50/50; 07:24-07:44Z) show no error, but ran
   inside the window. **Re-run on clean disk by the coordinator on the committed bytes of L (216c465f), 10:36-10:55Z,
   own fresh base store: static 10/10, launch 10/10, state 46/46, crash 50/50, identical; the deterministic S01 run
   8.1 s (bound 60 s).**
5. **Pre-cleanup matrix** (55/56, M15 survived) is structural, not disk-induced: M15's fragment (the boot check in
   `identity_alive`) left the classifier's path when the classifier moved to `identity_state`; a survivor is a PASS of
   the target test, which disk exhaustion cannot produce. M15 was re-targeted and its old fragment kept as M57; both
   killed in the post-cleanup run.
6. **Final bytes:** no code or test file of the namespace changed after 09:11Z (last test edit 08:36Z), so the
   post-cleanup matrix ran on the committed bytes of L.

**Conclusion.** The low-disk interval contaminated exactly one run, which was preserved and superseded; no
conclusion of step L rests on evidence produced under disk exhaustion. **New cell-308 target evaluations: 0.**
MB r1's marker still names afa93072; no ref under `refs/p5y-k5-cell308-mbs-r1/`.

**Lesson (prospective gate pending).** A target-free disk-space and scratch-lifecycle gate is to be designed and
reviewed before the freeze (user instruction of 2026-09-30).
