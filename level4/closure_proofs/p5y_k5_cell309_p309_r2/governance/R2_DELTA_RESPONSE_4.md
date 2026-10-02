# P309-r2: response to the third follow-up review (repair round 4; advisories X1–X7)

**The review.** `governance/REVIEW_R2_DELTA_FOLLOWUP_3.md`: R2_DELTA_FOLLOWUP_3_ACCEPTED, read at `93ea669a`.
* Every condition in it is **advisory**. None is blocking before owner decisions, and none is before the freeze.
* It recommended folding X1, X2, X3 and X6 into any code change made before D.
* It is preserved verbatim in `cfd46740`. Its execution ledger is kept, byte-identical, in `evidence/reviews/`. That
  commit explains why the ledger sits outside `governance/`.

**Why a round for advisories.** X1 names a rare false Q-HOST failure at the stop, about 4.5 × 10⁻⁶ per stop, that
would consume r2's single attempt. X2 names a race in the abort's process-tree kill. Both are small and testable in
this session, so the coordinator repaired all seven before any worker step. The round is re-drilled and goes to a
fourth focused follow-up review.

**Development checks before commit.** They ran in a scratch clone of the branch with the changes copied in, so their
ledger rows stayed in that clone:
* QC12 T1–T14, the scanner and the pins;
* `tests/test_p309_host.py` 77/77;
* `tests/test_p309_host_controls.py` 41/41;
* `tests/test_p309_static_controls.py` 22/22;
* `tests/test_p309_scan_allowance.py` 19/19;
* `code/p309_placeholder_check.py`, with no unallowed hit.

No TEST process was left. NEW Γ309 TARGET EVALUATIONS = 0.

## Advisories

| id | what was done | where | shown by |
|---|---|---|---|
| X1 | The monitor's `m` times are no longer rounded. The runner takes its stop time only **after** the monitor has been reaped, so no event can be later than the stop. The monitor file is parsed by a pure function, `parse_monitor_rows`: a torn last line is set aside, and any other line that does not parse fails Q-HOST (`corrupt_lines`). The packet's list of what ends the attempt is completed: the order rule, "no completed sample", and a corrupt file | `code/p309_host.py`; `code/p309_qualify.py` `stop_qhost_monitor`; packet OD-R2-5; amendments §I1 | `tests/test_p309_host.py` MV06–MV09: a torn last line, a corrupt middle line, an event exactly at the stop (passes), an event after it (fails). R01 (below) runs the stop path for real |
| X2 | The reviewer's own variant. The rounds end only when a walk that **began after** an observation of every seen descendant as stopped or gone finds nothing new | `code/p309_host.py` `kill_own_descendants`; amendments §I2 | **Development check:** the reviewer's slow-fork harness (`kod_slowfork.py`: two 1 GB TEST forkers in a back-to-back `os.fork` loop; an outside TEST process), copied to the coordinator's scratchpad, 20 trials each. **Round-3 function:** survivors in 7 of 20 trials (the reviewer saw 8 of 20). **This round:** 0 of 20. The outside process was untouched in all 40. One measurement fix was made to the copy: its survivor scan now skips the driver's own ancestors. Without it, the token on the harness's command line made the harness and its `timeout` wrapper count as "survivors" in every trial, for both versions. **Committed:** K02, a slow-fork regression (two 512 MB TEST processes starting children with a real fork, three trials). It does **not** reproduce the race: that needs a back-to-back `os.fork` loop, which the namespace scanner forbids everywhere, test programs included, and the scanner was not weakened for it |
| X3 | R01, a cloud-tier control. It runs the runner's own `start_qhost_monitor` and `stop_qhost_monitor` with a real monitor child. The interval is 4 s, set through the runner's `QHOST["interval"]`: QC12 T7 forbids a test setting a module attribute, so the interval moved into the runner's existing state dict, still 60 s in production. Q-HOST must pass with three or more samples, the start-of-sample rows must be one interval apart, and nothing may be written in qualification/. The MV harness selects rows by their time, which equals the time they were written on the virtual clock | `tests/test_p309_host_controls.py` R01; `code/p309_qualify.py` (`QHOST["interval"]`) | R01a–c. Development: cadence `[4.0, 4.0, 4.003, 4.0]` s, largest gap 2.0 s |
| X4 | A01's TEST forkers stop forking after 20 s. `kill_token` repeats until no process carrying the token is left | `tests/test_p309_host_controls.py` | A01, K01 and K02 |
| X5 | U01's altered configuration file now holds TEST bytes only, with no host value: the refusal needs only bytes other than the bound file's. The U records sit in a mode-700 directory that is removed at the end of the case. The record copies are of the redacted launch record | `tests/test_p309_host_controls.py` `case_u` | worker tier only (U00 on the cloud tier) |
| X6 | T14's docstring states its reach: the names, an attribute, or a from-import alias. It names what it does not see: assignment aliases, getattr, exec*, pthread_kill and alarm | `code/p309_static_check.py` | the text |
| X7 | AWS §3: "no blocker" includes the gate, so the 8c check needs an agreed quiet moment, and a gate blocker there is not a host verdict. The record keeps 80 process rows, with counts by tag for all. Every `code/...` command runs from the r2 namespace directory. §4.1 step 2 shows each timer's account (`systemctl show -p User,DynamicUser`) and each cron job's account (the sixth field of `/etc/crontab` and `/etc/cron.d/*`) | `R2_AWS_SESSION_INSTRUCTIONS.md` | the text |

## Re-pins

`governance/R2_REPIN_LIST_SUPPLEMENT_4.json` has 8 rows against `93ea669a`:
* re-pinned: `kill_own_descendants`, `qhost_monitor`, `start_qhost_monitor`, `stop_qhost_monitor`, `case_u`,
  `kill_token`;
* new: `case_k02`, `case_r01`.

The exactly-once sites, the backstop pins, the T13 pins and the production tokens are unchanged.

## Changes to the code a reviewer should know

* `code/p309_host.py`: `parse_monitor_rows` (new, pure), the unrounded `m`, and the `kill_own_descendants` loop.
* `code/p309_qualify.py`: `QHOST["interval"]`, and in `stop_qhost_monitor` the stop time after the reap, the parser
  and `corrupt_lines`.
* `code/p309_static_check.py`: T14's docstring only.
* `code/p309_self_audit.py`: IMMUTABLE adds the third follow-up's brief, review and sha256 record, and its ledger at
  its `evidence/reviews/` path.

Nothing in the driver, guard, verifier, generators or scanner code changed in this round.
