# Proposed supplement: disposition of review 64 on the combined development source

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This supplement answers review 64
(`reviews/REVIEW_REVIEW63_REPAIR_DELTA.md`, recorded verbatim). Review 64 is a fresh bounded review of the review-63
repairs, `9b6347cb..5e8e3d9c`. This supplement accepts nothing and decides nothing.
* All 21 D-* decisions remain undecided, and `DECIDED` is empty.
* `JOURNAL_READER_REVIEWED = False` and `PIN_POINT_MODULES = None`.
* A1, A2 and A5 remain unmet.

It **corrects and extends** `PROPOSED_REVIEW63_DISPOSITION_SUPPLEMENT_20261015.md` §2, which stays unchanged. Where the
two differ, this text describes the new source. The new source is bound by the ledger line of the commit that carries
it, and by its own native synthetic run. Until that run passes, nothing here is validated.

## 1. Findings

| finding (review 64) | disposition on the new source |
|---|---|
| K1 MAJOR: the order rule depends on the reading repository's git configuration | Every git read runs as `git -C <repo> --no-replace-objects -c log.showRoot=true …`. The environment carries `GIT_CONFIG_NOSYSTEM=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_ATTR_NOSYSTEM=1` and `GIT_GRAFT_FILE=/dev/null`. The pickaxe and object searches add `--no-textconv --no-ext-diff`. In a shallow clone the boundary commit is shown as introducing every file it holds, so an order hidden by the cut refuses and is never accepted. A separate shallow check would have been an equivalent mutant, so it was dropped. Test `test_review64_order_ignores_reading_configuration`: a local `log.showRoot=false` with the acceptance in the root commit; a textconv driver on the accepting file through `.git/info/attributes`; a depth-1 clone. Mutants RV23, RV24. **Residual (stated):** repository-local configuration is still read for every other key, and a host review may require an allow-list. |
| K2 MINOR: Q04 extended instead of a test added | Q04 is back to its single site. The case "accepting verdict line twice" is added to `test_acceptance_is_found_not_named`, and RV21 (`set(verdicts)`) is registered. Ledger 485's root cause is corrected by a new ledger line: Q04 was a test gap. |
| K3 MAJOR: RW1–RW4 and RW6 survive | Registered as RV18 (`test_review64_missing_blob_commits_refuse`), RV19 (`test_review64_dangling_top_entry_shadows_lower_mask`), RV20 (`test_review64_non_utf8_historical_review_path_refuses`), RV21 (above) and RV22 (`test_review64_side_branch_acceptance_synced_and_merged_refuses`). |
| K4 MINOR regression: a full sha inside a longer hex run | `_names_sha` also tests `sha in line.lower()`. Test `test_review64_sha_inside_longer_hex_run_still_names_it`; RV25. |
| K5 MINOR: later merges refuse a valid acceptance | **Stated, not changed.** With `--diff-merges=separate`, a merge counts as introducing the blob or the line whenever any parent lacks it. A later `--no-ff` merge of a branch forked before the blob therefore refuses the acceptance permanently, which is fail-closed. Combined-diff semantics would remove this, but they change the mechanism. They are left to the formal review together with the ledger binding (D-HOST-LIFETIME item (i)), which would make commit order secondary. |
| K6 MINOR: caller-input enumeration incomplete | §2 below lists every public function's parameters. |
| K7 MINOR: a symlink accepted as a review | Accepting entries must be mode 100644 or 100755 blobs, read from an exact-path `ls-tree`. Test `test_review64_symlink_is_not_an_accepting_review`; RV26. |
| K8 NOTE: vocabulary residuals | Stated: the negative-word, reference and verdict rules are enumerations. They catch the listed forms, not every way of writing a refusal. The ledger binding (item (i)) is the intended remedy. |
| K9 NOTE: denial and crash paths | (a) Review blobs and the attestation are read with `git cat-file blob HEAD:<path>`, and blob ids and modes come from `ls-tree -z HEAD -- <paths>`. A name such as `x..HEAD` is therefore never parsed as a revision range. Probing showed `git show HEAD:<dir>/x..HEAD` prints a commit log, not the file. Test `test_review64_range_like_review_names_do_not_block`; RV27. The fault injectors in `test_sync_boundaries.py` now match either read form, with unchanged semantics. (b) An `OSError` from a unit root becomes an unknown unit in `auto_update_settings`. Test `test_review64_unreadable_unit_root_is_unknown_not_a_crash`; RV28. |
| K10 NOTE: records | A new ledger line binds a16d2d99's inputs and states the timing of the local full run correctly (it finished after the native success). It also names the two empty review-63 scratch directories that were not copied. |
| K11 NOTE: L-DET addendum gaps | Additions to the addendum's §3: `true`/`1`, `false`/`0` and `0`/`-0.0` also compare equal after `json.loads`. The candidate's `pinned_bytes` reads the **working tree** and HEAD, so it cannot be L-DET's loader on a branch where the paths are absent; L-DET must read by blob id. The `MBR1_RECORD_PINS` assignment spans lines 1823–1839. The comment line citing `21e99cf0` is 1822. |

## 2. Restated rows (proposed; supersede supplement r63 §2 where they differ)

**L-LIFE acceptance (new source).** As supplement r63 §2, with these changes:
* **Isolation:** the git isolation described under K1 above.
* **Set:** accepting entries are regular-file blobs (mode 100644 or 100755) only.
* **Reads:** review blobs and the attestation are read by `cat-file blob HEAD:<path>`.
* **References:** a sha reference also counts inside a longer hex run.
* **Additional stated side effects:**
  * any later merge of a branch that lacks the blob or the line refuses permanently (K5);
  * the rules for negative words, references and verdicts are enumerations (K8);
  * repository-local git configuration other than the forced keys is still honoured (K1 residual);
  * any review-file name that git cannot list as UTF-8, current or historical, refuses.

**Public functions of `lx_platform.py` and their parameters.**
* *Caller inputs, with the source a reviewed caller must use:*
  * `preflight(repo_path, *, mode, other_job_running, launched, attestation_ref)`:
    * `repo_path` is the campaign store;
    * `other_job_running` comes from the reviewed launcher's pidfile check;
    * `launched` is only compared with a fresh reading;
    * `attestation_ref` is a pointer to committed files.
  * `busy_processes(t0, t1, dt_s, threshold_pct, own)`:
    * `t0` and `t1` come from `cpu_ticks()`;
    * `dt_s` is measured on CLOCK_MONOTONIC;
    * `threshold_pct` is the decided R-EXCL-PCT value (D-EXCL-WINDOW is open);
    * `own` is the campaign's (pid, starttime) keys.
  * `identity(pid)`, `identity_state(ident)`: `ident` is a record produced by `identity()`.
  * `proc_stat(pid)`, `cmdline_sha256(pid)`, `ns_inode(kind, pid)`: the process and namespace being read.
  * `attestation_valid(ref)`, `root_attestation(attestation_ref)`, `memory_readings(attestation_ref=)`: a pointer to
    committed files.
  * `assess(start, end, samples, journal_suspend_events)`: readings from `snapshot()`. The journal channel stays
    AMBIGUOUS until a reviewed reader exists.
  * `pin_mismatches(pins, got)`: `pins` from the accepted pin record, `got` from `platform_readings()` at the pin point.
  * `launch_record_ok(rec)`: `rec` from `launched_by_systemd()`.
  * `unit_enabled(unit)`: a name from `UPDATE_UNITS`.
  * `dpkg_versions(packages)`: the interpreter's owning packages.
  * `durable_write(path, data)`: the campaign store's file and payload.
  * `free_disk_bytes(path)`: the campaign store.
  * `visible_limit_upper_bound(chain_rec, mem)`: the outputs of `memory_cgroup_chain()` and `meminfo()`.
* *Test seams that a reviewed caller never passes:*
  * `boot_id(text)`;
  * `machine_identity(machine_id_path, dmi_path)`: the F20 hardware binding;
  * `proc_stat(text)`, `cmdline_sha256(data)`, `suspend_success_count(text)`;
  * `snapshot(power_root, suspend_text)`, `power_source(root)`, `thermal_zones(root)`;
  * `meminfo(text)`, `memory_cgroup_chain(proc_cgroup_text, root)`, `cgroup_resources(proc_cgroup_text, root)`;
  * `memory_readings(mem_text, proc_cgroup_text, root)`, `psi_memory(text)`;
  * `proc_view_complete(status_text, mountinfo_text, pidns)`, `cpu_ticks(proc_root)`, `busy_processes(hz)`;
  * `unit_enabled(unit_roots)`;
  * `auto_update_settings(apt_dump, unit_roots, uu_binary, snapd_paths, cloud_dir, livepatch_dir, use_live_apt)`;
  * `systemd_is_pid1(comm_text, run_dir)`;
  * `launched_by_systemd(env, proc_cgroup_text, show, pid1, prefix)`;
  * `durable_write(fault)`, `os_release(text)`, `mapped_objects(maps_text)`, `dpkg_versions(query)`,
    `platform_readings(maps_text)`;
  * `identity_state(current_boot, exists, stat, cmd, current_ns)`;
  * `attestation_valid(repo_root)`.
* `lx_verified.observe(attestation_ref=None, *, mode="execute")` passes none of the test seams. Checking every caller
  is an implementation-review item.

## 3. Harness

Group RV grows to RV01–RV28, so the registry has 161 mutants. Q04 is back to its single site. R5SYNC02 is extended
once more: its emptied listing also empties the exact-path listing that the K7 mode check reads, so the faithful
weakening tolerates a missing entry there too. The reason is stated in the mutant's description. RV08 and RV12 are
re-anchored with the same weakening, because their lines changed. The workflow expects 161 mutants and 162 suites.
