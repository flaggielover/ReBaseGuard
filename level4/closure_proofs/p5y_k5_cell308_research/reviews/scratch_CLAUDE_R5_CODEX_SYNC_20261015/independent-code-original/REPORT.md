# Independent bounded code review — immutable selective integration snapshot

Review status: **changes required for the retained defects below**. This is a code correctness/regression review of four supplied byte snapshots. It grants no governance, route, host, campaign, scientific, or execution acceptance. I authored none of the reviewed inputs. I made no product/test-source changes, commits, or pushes.

## Immutable input binding

These SHA-256 hashes were independently calculated before execution and rechecked after all original-snapshot probes. Each matches the supplied `code-review-input/SOURCE_BINDINGS.json`.

| Snapshot relative to `code-review-input/` | SHA-256 |
| --- | --- |
| `lx_platform.py` | `864e47ee93f2a2972e51f76c0c4d4a9f727e9be2ffd0a421016df90e72917263` |
| `lx_verified.py` | `b78756eb377e91c4877b5bf0f96557257da64d4ac464ae339080e9f9e0ca29a9` |
| `tests/test_sync_boundaries.py` | `aebecf1e4cce000c78e3ed07d7d785f6bfe9ab06dcf99a8d9327b182dd8fff5f` |
| `tests/test_lx_verified.py` | `041b8dcf15fe5c998f140f9a9126676f301ea52401fc08eeb77069a738a4c781` |

The snapshot root is `/tmp/cell308-claude-sync-20261015/code-review-input` (macOS resolves `/tmp` to `/private/tmp`). Repository-relative production paths are recorded in this review's `SOURCE_BINDINGS.json`. The coordinator must separately establish equality with any final committed bytes; this review does not do so.

## Findings

### F1 — P2: Git-quoted review pathnames silently bypass a committed veto

`lx_platform.py:1171–1177` runs `git ls-tree -r --name-only` without NUL output, splits its output by newlines, and passes each resulting string directly to `git show HEAD:<path>`. Git's default pathname quoting escapes non-ASCII and control characters. The string passed to `show` therefore includes Git's quoting rather than the real pathname. `show` fails, and `or b""` suppresses the unreadable review.

Fresh temporary-repository controls first committed a host JSON blob and then a valid direct acceptance review in a later commit. Adding a rejection review containing that exact SHA under `reviews/scratch/negative.txt` made `attestation_valid` return `None` with a rejection reason, as expected. The same committed content at `reviews/scratch/拒否.txt`, a tab-containing filename, or a newline-containing filename left `attestation_valid` returning the record with `reasons == []`.

For the Unicode case, the raw listing contained `".../reviews/scratch/\\346\\213\\222\\345\\220\\246.txt"`. No fault injection was needed. The fixed recursive veto rule promises to consider every committed file under the review directory; this implementation omits valid Git pathnames. Use unambiguous NUL-delimited path transport and preserve raw pathname bytes (including surrogate handling) through blob reads.

Evidence: `probe_acceptance.py`, cases `committed_veto_*` in `acceptance_probes.json`. `_acceptances` is AST-identical to the Claude original; this is a retained Claude defect, not a newly introduced selective-integration regression. The old Codex baseline had a different acceptance mechanism and no `_acceptances` function.

### F2 — P2: unavailable veto evidence becomes evidence of no veto

`lx_platform.py:1173–1177` coerces both an unavailable recursive review listing and an unavailable review blob into empty data. `attestation_valid` at `1238–1244` receives only `(acceptances, rejections)` and cannot distinguish a complete clean scan from an incomplete scan. A known accepting review may therefore verify the attestation while the veto channel is unreadable.

In a temporary repository containing a readable valid acceptance and a committed ASCII rejection, the unmodified boundary rejected the record. Selectively returning `None` from `_git` for only the recursive `ls-tree` call changed the result to `verified=True, reasons=[]`. Selectively returning `None` for only the rejection's `git show` did the same. These values are the real `_git` failure contract for subprocess unavailability/timeouts and other Git failures. Preserve an explicit completeness/error result and make any incomplete required veto scan invalidate the attestation.

Evidence: `probe_acceptance.py`, `fault_control_readable_veto`, `recursive_veto_listing_unavailable`, and `veto_blob_unavailable` in `acceptance_probes.json`. This finding is independent of pathname quoting: every pathname in this reproduction is ASCII. It is retained unchanged from the Claude original. Current development defaults still keep root authority and operational readiness blocked; that does not make an incorrect `verified` result correct.

### F3 — P2: unknown PID-1 status can be reported as disabled update units

`lx_platform.py:840` selects the systemd branch only for strict `True`; both `False` and `None` enter the filesystem fallback at `854–867`. An unreadable `/proc/1/comm` therefore becomes the same case as positive evidence that systemd is absent. With no dependency links, the function returns `False`, even though an active but disabled systemd service cannot be ruled out. The newly improved activity-query failure check at `845–850` is bypassed completely in this case.

The fresh synthetic matrix returned `None` for `systemd_is_pid1=True` with unavailable activity and `is-enabled=disabled`, but returned `False` for `systemd_is_pid1=None` with the same inputs and empty synthetic unit roots. Composing the real `auto_update_settings` with synthetic apt-off configuration and absent other update vectors then produced `guest_updates_shown_disabled=True`. Unknown supervisor status must remain unknown unless a separate complete observation establishes the runtime state.

Evidence: `probe_composition.py`, cases `unit_enabled missing activity pid1=*` and `auto_update_settings activity unavailable pid1=*` in `composition_probes.json`. This unknown-supervisor fallback was already present in the Claude original; the selective integration improves the `True` branch but retains this adjacent failure path. No actual PID 1, systemctl, or update configuration was queried.

### F4 — P3: malformed numeric reader text raises instead of yielding UNKNOWN

`lx_platform.py:299–302` and `457–461` use `str.isdigit()` followed by `int()`. Those predicates do not accept the same character set: superscript two (`"²"`) passes `isdigit()` and then raises `ValueError` in `int()`. A truthy non-string reading such as integer `7` or `True` raises `AttributeError` at `.strip()`. Bytes `b"7"` are accepted as a count rather than refused as the wrong reader type.

Both explicit `suspend_success_count("²")` and a mocked canonical `_read` returning `"²"` raised `ValueError`. The same canonical boundary probe for `_cg_val` raised `ValueError`. For `suspend_success_count`, this propagates through `snapshot`; `_cg_val` propagates through cgroup memory observation. Thus malformed-but-readable evidence escapes the advertised fail-closed reader boundary rather than becoming a missing/ambiguous observation. Require string input, use a bounded ASCII decimal grammar, and safely reject conversion failures.

Evidence: `composition_probes.json` and `numeric_order_probes.json`, generated by `probe_composition.py` and `probe_numeric_and_order.py`. Both functions are AST-identical in the snapshot, Claude original, and old Codex baseline; this is an inherited robustness defect, not an integration regression. These probes establish malformed-input behavior only, not that a conforming Linux kernel emits such strings.

## Integration properties checked

Apart from the defects above, I found no new regression in the bounded selective integration paths reviewed:

- Fixed direct acceptance-review membership, exact single verdict, case-insensitive recursive veto, and strict blob-before-acceptance-line commit ordering are present. Supplied same-commit and moved-review controls pass. F1/F2 limit the completeness of that veto guarantee.
- The canonical verifier reads committed bytes, refuses absence before hashing/JSON, binds the requested SHA, validates schema/strict accepted+reviewed booleans, reads the current machine internally, and does not trust a JSON-selected acceptance path. Malformed Git arguments/absence are refused by the supplied controls.
- Root provenance requires the initial cgroup namespace, `D-HOST-LIFETIME` in the validated fixed decision set, a verified record, and `root_cgroup_is_real is True`. Observer record claims remain distinct from the root contract. Under the actual empty `DECIDED`, a verified record grants no root contract. Synthetic all-decided controls also retain the observer's withheld quantities and readiness/condition limits.
- `preflight` performs fresh power, disk, boot, update, attestation, and required launch readings. The public signatures contain no old caller-selected trust/readings/decision/observer overrides. Launch records are corroborated against a fresh observation; malformed records and changed/extra fields fail comparison.
- `busy_processes` uses exact `(pid,starttime)` parent presence in the particular snapshot, rejects duplicate PID identities, checks counter regression before ownership exemption, refuses invalid duration/threshold/frequency types and nonfinite/overflow arithmetic, and performs a fresh strict `proc_view_complete` check. Fresh probes cover parent only at t0, reused parent, same-tick child, and owned negative/decreasing counters.
- Interval assessment checks all endpoint/sample clocks and counters, adjacent ordering, cumulative endpoint divergence, boot/power, and default journal refusal. Malformed and reordered controls do not produce CLEAN. `JOURNAL_READER_REVIEWED=False` remains fixed in the reviewed bytes.
- `DECIDED` is empty, all 21 decision IDs remain defined, `PIN_POINT_MODULES=None` has no caller list override, and static inspection shows pin-point refusal before platform readings. I did not invoke `pin_point`.
- `lx_verified.observe` exposes only the attestation reference and mode, uses the canonical repository/current-machine verifier, strips `effective_limit` and `cgroup_min_headroom`, labels remaining memory as raw, fixes the other-campaign detector to unknown, returns `development_only=True`, returns `operational_ready=False`, and keeps A1/A2/A5 explicitly unmet for every observed mode. It imports no science/candidate/evaluator.

## Execution and scope limits

Before importing either module I parsed and inspected all top-level AST nodes in all four inputs; `AST_IMPORT_PRECHECK.json` records them and their hashes. There are stdlib/module imports, constants/regex setup, definitions, and test-entry guards; no host/science reader runs at module top level. Controlled imports then loaded precisely the copied snapshot paths with bytecode writing disabled.

`run_supplied_tests.py` set `LX_PLATFORM_DIR` to the immutable snapshot and ran only the two supplied synthetic files: **71 tests, zero failures/errors/skips** (Python 3.14.5). `supplied_tests.log` and `supplied_tests.json` record the run. An initial runner path assertion stopped before any suite because macOS resolves `/tmp` as `/private/tmp`; the runner was corrected to compare canonical paths, then the full suite ran once.

Fresh independent scripts produced **13 acceptance/veto result cases, 56 composition result cases, and 32 numeric/order result cases**. These are probe-result counts, not a claim of 101 additional passing unit tests; several intentionally demonstrate the findings. Probe scripts use only planted records/parser strings, mocked module-reader boundaries, and Git inside controlled temporary repositories. Audit hooks forbid `/proc`, `/sys`, relevant host identity/OS/systemd reads and non-Git subprocesses; guarded stat/readlink and denied raw reader functions provide additional checks. All recorded unexpected host-access attempts are empty. No actual systemctl, host inventory reader, process signal/probe, science, pin point, evaluator, qualification, candidate, or campaign ran.

I read only the four immutable supplied inputs and the specifically authorized Claude/old-Codex platform/observer baselines. I did not inspect unfinished working tests/harness changes or mutant results. No prohibited interruption/incident/exposure records, target-run artifacts, Cell309 material, broad namespace inventory, or quarantine CLI were accessed. This review does not establish real-host facts, external authority, reviewer independence, persistent durability under device failure, or operational acceptance.

Supporting evidence remains under `/tmp/cell308-claude-sync-20261015/independent-code/`: source bindings, AST precheck, baseline byte bindings and exact diffs, baseline function comparison, runner/probe source, and raw JSON/log results. This original-snapshot report is to remain verbatim; review of later repaired bytes must be a separate delta report bound to their hashes.
