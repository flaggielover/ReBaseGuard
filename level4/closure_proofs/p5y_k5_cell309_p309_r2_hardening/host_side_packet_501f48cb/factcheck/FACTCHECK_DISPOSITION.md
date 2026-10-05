# Disposition of the independent fact-check (`FACTCHECK_REPORT.md`)

**The fact-check.** A separate agent checked the packet against the extracted bytes of r2 `501f48cb`. It was
read-only and executed no r2 code.

**Verdict.** DEFECTS_FOUND: no blocking defect, 6 should-fix and 15 minor. Every item was corrected in the commit that
adds this file, which follows the draft commit `fd754adc`.

## Should-fix

| # | finding | correction |
|---|---|---|
| 1 | the runner's per-gate lines never reach the journal: the drill captures the runner's output, and the drill root is deleted | 8D §3 and §4: monitoring uses the files and `systemctl`, and the journal limitation is stated. 8D §5, §8 and §10, PASS_FAIL §3–§4 and PRE_FREEZE I-6/Q8 no longer rely on journal lines. FAIL-PROBE is replaced by **FAIL-PRESTART** (rc 2, gates null; the kept evidence cannot name which pre-attempt refusal fired, and this is stated) |
| 2 | the filesystem type (R-FS-7, HP-only) had been made a blocker | 8B B-28 is now an advisory note, never a blocker. 8A S-01 and OD M2 present it as a recommendation |
| 3 | `ls-remote` dropped the credential helper | the pre-launch tool passes `GIT_ASKPASS` to `ls-remote` only; the docstring explains it. C07 is unchanged (the same rule as r2's isolation check) |
| 4 | `PACKET_MANIFEST.json` was missing | added (sha256 of every packet file except itself) |
| 5 | E-1 relied on the system journal, which the P309 user normally cannot read | E-1 now rests on the exclusive launch records, the launcher output, the `systemctl list-units` snapshots and the report's unit Id. An administrator's journal extract is optional |
| 6 | U01–U03 cannot be shown to have run | P-1, 8D §6/§11, PRE_FREEZE Q5 and PASS_FAIL §7 now say so. The validator records `host_controls_pass_lines` for the reviewer, who compares it with the committed cloud-tier count (41) |

## Minor

| finding | correction |
|---|---|
| the protected-ref regex was broader than r2's | both tools and the docs now use `^refs/p5y-k5-cell309` |
| the launcher's order was described as refusing on the first failure | 8D §3 now describes the actual behaviour: it collects every blocker, then writes the record |
| the per-gate timeout | corrected to 6 h by default, and 24 h for the decoy runs |
| the Q-HOST effects were conflated | split into a failure during the run (exit 3) and a judgement at the stop (exit 1, report continues) |
| the location of the decoy outputs | corrected: they lie directly in `attempt_1/` |
| the `launched` key | it is attributed to the launcher's output, not the record |
| a quote was misattributed | the OD packet now cites `R2_DELTA_FOLLOWUP_5_RECORD.md` and the OD-R2-4 heading |
| R-SD-9 was overclassified | split: `timedatectl` is REQUIRED (effective); `journalctl` and `systemd-detect-virt` are RECOMMENDED (R-SD-10) |
| the R-SD-4 citation | SI §3 is now cited for "reset if failed" |
| B-08 added a criterion r2 lacks | `spot_instance_action` is now recorded only |
| the IMDS request rate | corrected to about 6 requests per sample |
| the disk figure | it now uses HP §1's figures only |
| operator consent for X-5–X-7 | added to the form, Part B8 |
| 8A's git rule | `git version` and `git --version` are allowed explicitly |
| tool robustness | the validator classifies a corrupt report as FAIL (a new self-test case). The pre-launch tool loads `p309_host.py` only if C08 confirms its bytes |
| the reviewer's git verbs | `clone` and `checkout` are allowed inside the reviewer's workspace |
| 8D's scan-allowance wording | now "every line [PASS]" |

**Self-test after the corrections.** `tools/selftest/SELFTEST_RESULTS.json` shows all 9 cases as expected: 3
pre-launch cases and 6 drill cases (PASS, FAIL ×3, INCIDENT, INTERRUPTED). Neither tool changed the clone.
