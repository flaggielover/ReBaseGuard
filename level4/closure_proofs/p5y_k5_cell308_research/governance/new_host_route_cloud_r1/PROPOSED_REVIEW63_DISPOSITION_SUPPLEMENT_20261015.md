# Proposed supplement: disposition of review 63 on the combined development source

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This supplement answers review 63
(`reviews/REVIEW_CLOUD_R1_DELTA_R5.md`, recorded verbatim) for the combined development source on
`codex/cell308-claude-r5-integration`. It accepts nothing and decides nothing. All 21 D-* decisions remain undecided,
`DECIDED` is empty, `JOURNAL_READER_REVIEWED = False` and `PIN_POINT_MODULES = None`. A1, A2 and A5 remain unmet. The
preserved amendment r5, owner brief r5 and the r5 integration technical supplement are not edited.

**Scope note.** Review 63 reviewed Claude revision 5 at `37c62102`, not the combined source. Each finding was checked
against the combined source (PR3 head `9b6347cb`, `lx_platform.py` `2f0489d3…`) before any repair. Some were already
repaired there, and they are marked so below. The repaired source is bound by the ledger line of the commit that
carries it and by its own native synthetic run. Until that run and an independent check of it pass, nothing here is
validated.

## 1. Findings against the combined source

| finding (review 63) | state at PR3 head `9b6347cb` | disposition on the new source |
|---|---|---|
| H1 MAJOR: order rule; tree entry; merges; side branch; oldest-by-date | tree entry already refused as unavailable evidence. **Open:** merges invisible, oldest-dated hit, side branch, acceptance before the blob. | `_ordered`: **every** commit that adds or removes the attested blob must be a strict ancestor of **every** commit that adds or removes the accepting line. Both searches run over HEAD's history with merges included (`--diff-merges=separate`), and no commit is chosen by date. `_first_commit` is removed. Tests: `test_review63_order_every_commit_merges_and_side_branches` (evil merge, acceptance before the blob, side branch forked before the blob, and a legitimate merge as the positive control). Mutants RV01, RV08; Z05 and Q06 re-anchored. |
| H2 MAJOR: W01–W07 survive | W01–W07 not in the combined harness. W03 is **equivalent** on the combined source, because `identity_state` re-validates the recorded boot id. | Tests: `test_review63_shape_rejects_uppercase_digest_and_boot_id`, `test_review63_not_found_unit_file_search_complete`, `test_review63_veto_words_and_references`. Harness group RV01–RV07 carries W01–W07. RV03 weakens both boot-id checks together, since W03 alone is equivalent here. |
| H3 MINOR: rejection not permanent; forms not seen | quoted paths and non-UTF-8 evidence already refuse. **Open:** HEAD-only scan; abbreviated or upper-case sha; other words; other verdicts. | `_historical_review_blobs`: every blob under the review directory in **any** commit of HEAD's full history (side branches included) is scanned. A rejection survives `git rm`, `git mv` out of the directory, and later edits. Unreadable history refuses. `_vetoing`: a sha reference counts in any case and as any prefix of at least 8 hex digits. Negative words now also include refus*, unaccept*, declin*, "needs revision" and veto. Any verdict-like line other than the accepting one also vetoes. Tests: `test_review63_rejection_is_permanent`, `test_review63_veto_words_and_references`. Mutants RV06, RV09–RV14; Z01 re-anchored. |
| H4 MINOR: failed is-active plus disabled | **already repaired**: "disabled" gives False only when activity reads inactive or failed (CDEX16). | none needed |
| H5 MINOR: caller-input enumeration | partly addressed by the r5 integration technical supplement (`repo_path`). | §2 below. The `attestation_valid` docstring now calls `repo_root` a test seam that a reviewed caller never passes. |
| H6 NOTE: update-unit residuals | systemd mode **already repaired**: an unrecognised activity such as deactivating or maintenance gives unknown. | File mode: `*.upholds` links now count. A mask counts only when it is the **highest-precedence** entry for the unit. Test `test_review63_upholds_and_mask_precedence`; mutants RV16, RV17; P11 and Z02 re-anchored. Still not covered: `Wants=` written inside another unit's file. |
| H7 NOTE: formatted verdicts | open | A verdict-like line is any line containing the word "verdict" (any case), or a bare capitalised `KEY: VALUE` line. The accepting file must hold exactly one, the accepting line. Test `test_review63_verdict_like_lines_refuse_acceptance`; mutant RV15. |
| H8 NOTE: records | `_strictly_after` timeout **already repaired**. | `acc_path` is now documented. The repository-wide search covers it, because a line enters the accepting file only by an addition or by a move of an earlier addition. The Z05/Z06 wording and the "permanent" statement are corrected by a ledger line (§3). |

## 2. Restated rows (proposed; for the formal route review)

**L-LIFE acceptance, as the new source implements it.**
* The acceptance set is the **blob** files that are direct children of `reviews/` and are named
  `REVIEW_HOST_ATTESTATION_*.md`. A tree entry with such a name refuses the check as unavailable evidence.
* An accepting file holds the exact line `HOST_ATTESTATION_ACCEPTED sha256=<sha>`. It also holds exactly one
  verdict-like line, `VERDICT: HOST_ATTESTATION_ACCEPTED`.
* **Order:** every commit of HEAD's history that adds or removes the attested blob is a strict ancestor of every commit
  that adds or removes the accepting line anywhere in the repository. Merges count on both sides.
* **Rejection:** a file vetoes when it names the sha (full, or a prefix of at least 8 hex digits, in any case) and
  carries a negative word or any other verdict-like line. It vetoes whether it is at HEAD or in **any** commit of HEAD's
  full history. A rejection is therefore permanent within that history. Rewriting history is outside the check, and
  the ledger binding (carried item (i)) is what would make it detectable.
* **Stated side effects (fail-closed):**
  * a quote of the accepting line before or beside the blob refuses forever;
  * a later re-introduction of the blob refuses;
  * any negative word or extra verdict-like line in a file naming the sha refuses;
  * any git failure, unreadable listing, or non-UTF-8 review blob, current or historical, refuses;
  * in a shallow clone the history is cut, so acceptance depends on clone depth.
* **Not established:** independence. D-HOST-LIFETIME items (i), a ledger REVIEW binding, and (ii), a non-coordinator
  reviewer, stay carried. Item (iii), blob-level order, is implemented as stated above, and no stronger claim is made.
* **Exposure note (new, for the formal review).** The veto scan reads every file under `reviews/` programmatically,
  whether current or historical. In this repository that directory also holds exposure-restricted reviews (S13). The
  scan prints nothing, but on an actual host the formal review should decide whether host-attestation reviews belong in
  a dedicated directory. Synthetic tests use synthetic repositories only, and no live call reached the real review
  directory with a valid reference.

**L-UPD failed-query clause.** With systemd as PID 1:
* True if activity is active, activating or reloading, or the enablement state is an enabling one.
* False only when activity reads inactive or failed **and** the state is disabled, masked or masked-runtime, or the
  state is not-found with no unit file or link in any root.
* Any failed or unrecognised reading gives unknown.
* If systemd's PID-1 status is unknown, the result is unknown.

**Caller inputs (complete for the public functions of `lx_platform.py`).**
* *Caller inputs with a required source:*
  * `preflight(repo_path, …)`: `repo_path` is the campaign store, and it decides `free_disk_ge_2GiB`;
  * `mode`;
  * `other_job_running`, from the reviewed launcher's pidfile check;
  * `launched`, which is only compared with a fresh reading;
  * `attestation_ref`, a pointer to committed files;
  * `busy_processes(t0, t1, dt_s, threshold_pct, own)`: `t0` and `t1` from `cpu_ticks()` at the default `/proc`;
    `dt_s` from CLOCK_MONOTONIC between the two snapshots; `threshold_pct` the decided R-EXCL-PCT value (D-EXCL-WINDOW
    is open); `own` the campaign's (pid, starttime) keys.
* *Test seams that a reviewed caller never passes:*
  * `attestation_valid(repo_root=)`;
  * `identity_state(current_boot=, exists=, stat=, cmd=, current_ns=)`;
  * `busy_processes(hz=)`;
  * `cpu_ticks(proc_root=)`;
  * `proc_view_complete(status_text=, mountinfo_text=, pidns=)`;
  * `memory_readings(mem_text=, proc_cgroup_text=, root=)`;
  * `power_source(root=)`;
  * `unit_enabled(unit_roots=)`;
  * `auto_update_settings(apt_dump=, unit_roots=, uu_binary=, snapd_paths=, cloud_dir=, livepatch_dir=,
    use_live_apt=)`;
  * `systemd_is_pid1(comm_text=, run_dir=)`;
  * `launched_by_systemd(env=, proc_cgroup_text=, show=, pid1=, prefix=)`;
  * the `text=`, `root=` and `maps_text=` arguments of the other readers.
* `lx_verified.observe(attestation_ref=None, *, mode="execute")` passes none of these seams. `preflight` passes none.
  Checking callers is an implementation-review item.

## 3. Conditions C1–C4

* **C1:** no citation of the new source for L-LIFE or L-UPD until its native synthetic run, an independent check of
  that run, and a fresh review confirm the repairs. This supplement cites nothing as accepted.
* **C2:** §2 restates L-LIFE, L-UPD and the caller inputs. Independence items (i) and (ii) stay carried.
* **C3:** the ledger line recording review 63 corrects ledger 473 and amendment r5 §13. Neither "a rejection is
  permanent" (at 37c62102) nor "the same two weakenings" for Z05/Z06 was true. Lines 472 and 473 are not edited.
* **C4:** no new owner brief is issued here. Any later brief must state item (iii) with this qualification and must
  name only recorded reviews.
