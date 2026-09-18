# K5 CUSUM first real probe: countersigned external authorization, result

**`COUNTERSIGNED_EXTERNAL_AUTHORIZATION = READY_FOR_FINAL_LAUNCH_PREFLIGHT`.**

The governed packet is complete and published: amendment review, execution-binding amendment, E5 amended-packet
check, protocol authorization, independent countersignature, and slot-1 LAUNCH_NOTICE.
- **Frozen verifier.** The unmodified `prelaunch_verify.py` was run read-only on rebaseguard-vultr-02, from a fresh
  GitHub clone at `93a73313`. It returns **LAUNCH_PERMITTED**, and P01–P12 all pass. P11 reads "next slot slot-1 (0
  arithmetic attempts so far), launch notice committed and published".
- **Nothing was launched.** `REAL_INPUT_ARITHMETIC_GUARD = DENY` in the repository and on the host. The namespace
  `/root/work/k5-first-real-probe` does not exist. No slot was created, and no real R'''(0), R^(5), L0/U0 or L1/U1
  was computed or observed.

## Commits (branch `p5y-postk1-frontier`; each one published before the next)

| step | commit | object | sha256 |
|---|---|---|---|
| 1 | `585c9a01` | `p5y_k5_cusum_external_authorization/review/AMENDMENT_REVIEW.md`: independent review, PASS_WITH_SCOPE_LIMITATION | `9240e7b5…` |
| 2 | `842d3565` | `p5y_k5_cusum_first_real_probe_protocol/protocol/EXECUTION_BINDING_AMENDMENT.json` (BOUND_QUALIFIED) | `0c6809a2d56fc15603fc15a27bf79cc0e94977bf4370cacee9740295f1972bb4` |
| 3 | `e794f0a1` | E5 record: independent amended-packet review (PASS) plus verifier reports | — |
| 4 | `b2bc93d5` | `p5y_k5_cusum_first_real_probe_protocol/protocol/AUTHORIZATION_ACTIVE.json` | `17a45ffdbb34c9d96e6a3adde8d2eff125dc2018c397d87689fc70d7ad990255` |
| 5 | `dd750286` | `p5y_k5_cusum_real_point_executor/authorization/COUNTERSIGNATURE_ACTIVE.json` | `89a02599e568ed498070076f81fdb850b51a493a0765030b3c2036732769ff70` |
| 6 | `93a73313` | `p5y_k5_cusum_first_real_probe_protocol/ledger/ATTEMPT_LEDGER.jsonl`: one LAUNCH_NOTICE, `slot-1` | `88627b05d2c2c88d9f02aa2f182a87b31bb2182f796f5d67159a1fbe0cacb472` |

## What each object binds

**Amendment (`842d3565`)**
- It binds:
  - the r5 executor: freeze `a16d22b5`, identity `ef1c86e40bff0b13e40e924ba27d0841aff71f7344d114f71f517ab3adfdd41b`,
    `executor_entry` `p5y_k5_cusum_real_point_executor/code/executor_cli.py`;
  - the accepted E6 adapter as `consumption_adapter_entry`: `p5y_k5b_consumption_adapter/code/consumption_adapter.py`,
    sha256 `fbad7d33…`.
- `executor_sources_sha256` has 14 entries: the 11 identity files, frozen `k5_minimality.py` (`3a54f0fb…`), frozen
  `k5b_check.py` (`ddd54dc4…`) and the adapter. Its canonical sha256 is
  `b437adba64cd4098d6f8998f01af159e7092c14b6597c219cc9ab130da97c015`. That value was computed independently by the
  preparer and by the reviewer, and the review file names it.
- Evidence pins (5): the r5 qualification result and RUN_PROVENANCE, the r5 static review, and the E6 acceptance
  result and provenance.
- The science preregistration `9ace6896…` is unchanged.

**Authorization (`b2bc93d5`)**
- It is the frozen `AUTHORIZATION_TEMPLATE_R4.json`, with only the activation fields changed:
  - `EXECUTION_AUTHORIZED` true;
  - `PROTOCOL_FREEZE_COMMIT` `852b2d65c9332facd59771da7940ab429a7e2f2f`;
  - `executor_binding_sha256` `0c6809a2…`;
  - `AUTHORIZED_BY`;
  - `AUTHORIZATION_UTC` `2026-09-18T15:26:49+00:00`.
- The timing satisfies the frozen rule: the UTC is after the amendment commit (15:13:31Z) and equal to the
  authorization commit time.

**Countersignature (`dd750286`)**
- It was signed by an independent fresh-context countersigner session, from its own GitHub clone at `b2bc93d5`.
- It names the authorization bytes `17a45ffd…` and the amendment bytes `0c6809a2…`.
- `attempt_slot` is the integer 1, the nonce is 64 hex characters, and `countersigner.utc` is the numeric epoch
  `1789746837`.
- It is committed byte-for-byte as signed.

**LAUNCH_NOTICE (`93a73313`)**
- `{"authorization_sha256": "17a45ffd…", "event": "LAUNCH_NOTICE", "slot": "slot-1", "utc": "2026-09-18T15:58:05+00:00"}`.
- `utc` is ISO-8601 with an explicit offset and later than AUTHORIZATION_UTC.
- It is the only ledger entry. There is no OUTCOME and no seal.

## Final verification (read-only, fresh GitHub clones)

| file | where | result |
|---|---|---|
| `evidence/final/FROZEN_PRELAUNCH_VERIFIER_REPORT_READONLY.json` | vultr-02, frozen venv, `prelaunch_verify.py --authorization protocol/AUTHORIZATION_ACTIVE.json` | LAUNCH_PERMITTED, P01–P12 PASS |
| `evidence/final/FINAL_PKT_VERIFY_HOST.json` | vultr-02, `code/pkt_verify.py --stage full --frozen-verify` | every check PASS |
| `evidence/final/FINAL_PKT_VERIFY_MAC.json` | owner's Mac, `code/pkt_verify.py --stage full` | every check PASS (34/34) |

The checker covers all of the following:
- publication against the real GitHub `ls-remote`;
- commit ordering: freeze < review ≤ amendment < E5 < authorization < countersignature < notice;
- that every object was committed once;
- duplicate-key rejection on every JSON object;
- the frozen P01–P06 and P09–P12 in process;
- the countersignature rule of `authorization_interface.countersignature_problems`, mirrored;
- the r5 `supervisor.launch_state`, a pure read, which approves `slot-1` and refuses `slot-2`;
- that the namespace is absent.

The frozen verifier does not read the guard. Once the host guard is set to `EXTERNAL_AUTHORIZATION` as specified
below, the executor's own in-process checks are the same ones verified here:
- the verifier call;
- the amendment binding of the running executor bytes;
- the countersignature;
- the canonical-slot binding.

## Independence and scope

- The amendment review, the E5 review and the countersignature were each produced by a **fresh-context Claude
  session**. Each worked from its own GitHub clones and did not see the preparer's reasoning.
- None of these is a human, and all are the same model family as the preparer.
- `AUTHORIZED_BY` records the owner's explicit instruction, which was given in the preparing session.
- The r5 executor's scope limitations still apply: the host is not a trust root, and the real-mode path was
  qualified only statically and by unit rows.

## Host state (rebaseguard-vultr-02, 2026-09-18 16:15 UTC; re-check immediately before launch)

- **Runtime contract:** equals the frozen `host_runtime_contract` (P07 passes).
- **Packages and kernel:** kernel `6.12.107+deb13-amd64`, libc6 `2.41-12+deb13u4`, no reboot marker. The last
  package change was bind9 at 2026-09-18 06:23 UTC.
  - Unattended upgrades are **active**, and the next `apt-daily-upgrade` run is 2026-09-19 06:04 UTC. The final
    preflight must re-check P07, and should contain or avoid that window.
- **Disk:** `/` is 40% used.
- **K1 records:** all 326 match manifest `29ad1f9b…`.
- **Processes and outputs:** no conflicting producer (P08). No sealed record anywhere on the host. The activation
  objects exist only inside clean GitHub clones at published commits:
  - `/var/tmp/extauth-final/repo`;
  - `/var/tmp/extauth-pkt/e5`;
  - `/var/tmp/e5review-r1/repo`;
  - `/var/tmp/cs-indep-r1-154116`.
- **Hygiene:** see `HOST_HYGIENE.md`. The stale loop pid 182342 was stopped, and the tripwire debris was archived.
- **Mirror:** `/root/work/postk1.git` was fast-forwarded from `8ffcfaff` to the GitHub frontier. The fetch also
  auto-followed GitHub's 29 tags, all identical to GitHub. The mirror is updated again after this record is
  published.

## Runbook for the separate final preflight and launch task (not performed here)

1. **Checkout.** On vultr-02, make a fresh, clean checkout of `p5y-postk1-frontier` at the published tip. Its origin
   must be allow-listed (GitHub, or `/root/work/postk1.git` only after confirming it equals GitHub), and
   `origin/p5y-postk1-frontier` must equal `ls-remote`. `/root/work/ReBaseGuard` is on `main` and is not such a
   checkout.
2. **Host re-check.**
   - P07: the runtime contract, including libc and kernel after any unattended upgrade.
   - P08: no conflicting producer. Do not mistake the operator's own polling shells for producers.
   - No `/root/work/k5-first-real-probe`, disk space, and the K1 manifest.
3. **Frozen verifier.** Run `prelaunch_verify.py --authorization protocol/AUTHORIZATION_ACTIVE.json` with the
   contract venv. It must return LAUNCH_PERMITTED, with P11 approving `slot-1`.
4. **Guard.** Only then, and only on that host checkout, set `config/REAL_INPUT_GUARD.json` to
   `{"policy": "EXTERNAL_AUTHORIZATION"}`. The file is outside the identity and pins. Do not commit it.
5. **Launch.** The ONLY permitted command is
   `supervisor.py launch --namespace /root/work/k5-first-real-probe --slot 1 --mode real`, run with the contract venv
   interpreter and the default frozen ceilings (9000/10800 CPU-s, 14400 s wall).
   - `manufactured`, `governed_manufactured`, `burn`, `diskfull`, smoke, qualification and debug modes must never be
     run on this host while the authorization is active.
6. **Waiting and recording.** Wait via `RUN_COMPLETE.json` / `RUN_FAILED.json` in the slot and exact
   `/proc/<pid>/cmdline` equality (never `pgrep -f`). Then append the OUTCOME derived by `lifecycle.outcome_entry`,
   and publish everything, including a VOID or uninformative result.

## Unchanged by this packet

The following are all byte-unchanged:
- the science preregistration;
- the R1–R5 executor sources, pins and evidence;
- the E6 adapter and its evidence;
- `k5_minimality.py` and `k5b_check.py`;
- the K1 records and manifest;
- the K5-B theorem and countersignature;
- the CUSUM closure;
- AWS PS1.

No scientific rule, parameter or result-dependent consumption was introduced.

`EXECUTION_AUTHORIZED = true` (protocol authorization) · `REAL_INPUT_ARITHMETIC_GUARD = DENY` ·
`REAL_CELL_EXECUTED = NO` · `REAL_R3_VALUE_OBSERVED = NO` · `REAL_R5_VALUE_OBSERVED = NO` ·
`SCIENTIFIC_K5_PROBE_RUN = NO`

`NEXT_STEP = FINAL_REAL_PROBE_PREFLIGHT`
