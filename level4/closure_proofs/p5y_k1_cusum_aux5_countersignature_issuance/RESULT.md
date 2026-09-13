# CUSUM Aux5 countersignature issuance: result

## r2 (current): strict pre-genesis repair

**r2 is the current state. The r1 record below is historical.** Its countersignature `a58b1ad1…` is revoked.

**Trigger.** The first launch attempt, at 11:18:12Z, was refused fail-closed by the frozen in-supervisor P10: an operator-wrapper command line contained a launch marker. No ledger, cell or worker was created. The keeper left the runtime root holding only the frozen `PRE_GENESIS_FILES`. Issuance r1 wrongly read the root's existence as a production start.

| Step | Commit / time (UTC) | Outcome |
|---|---|---|
| Revoke stale r1 countersignature | `71314403` | `config/COUNTERSIGNATURE.json` removed; frozen P07 `COUNTERSIGNATURE_MISSING` (fail closed) |
| Issuance r2: runtime-root classifier, residue binding, tests A–J | `8778dd4f` | Host 24/24 PASS; J drives the frozen ledger |
| Phase A `review-preflight` r2 at `8778dd4f` | 11:37:53Z; evidence `35e425f5` (`b7b650c2…`) | `READY_FOR_COUNTERSIGNATURE`; root `PRE_GENESIS` |
| Pre-write temporal check | 11:41:11Z | Residue, hashes, lock, cells, processes and fence unchanged |
| Replacement countersignature (issuance v2) | `50cb25ae` (only `config/COUNTERSIGNATURE.json`) | `1ceb92d463d1332dfb26505143454b3c3fd87a611bc731372d9e227017682b07`; frozen verifier PASS; r2 bindings PASS |
| Frozen P01–P10 and `launch-preflight` at `50cb25ae` | 11:45:15–24Z | All PASS; `READY_TO_LAUNCH_PRODUCTION`; root still `PRE_GENESIS`, byte-identical |

The evidence is in `evidence/revocation_r1/`, `evidence/review_preflight_r2/` and `evidence/post_signature_r2/`.

```text
ROOT_EXISTENCE_ALONE_MEANS_STARTED         = NO
CURRENT_STATE                              = PRE_GENESIS
AUTHORITATIVE_PRODUCTION_STARTED_PREDICATE = ledger.json OR journal.jsonl exists (genesis has begun)
REAPER_ACCOUNTING_PRESERVED                = YES   (4441807 usec, charged once at the first RUN_OPENED)
DOUBLE_CHARGE_PATH                         = NONE
UNDERCHARGE_PATH                           = NONE
EXISTING_COUNTERSIGNATURE_REMAINS_VALID    = NO    (a58b1ad1 revoked)
PRE_SIGNATURE_REVIEW                       = PASS
INDEPENDENT_COUNTERSIGNATURE               = REPLACED (1ceb92d4…)
FROZEN_P01_P10                             = PASS
REPAIRED_LAUNCH_PREFLIGHT                  = PASS
CUSUM_READY_TO_RELAUNCH                    = YES
CUSUM_PRODUCTION_LAUNCHED                  = NO
CUSUM_PRODUCTION_CELLS                     = 0
LIVE_AWS_PS1_TOUCHED                       = NO
NEW_RESULT_BEARING_COMPUTE                 = NONE
ORIGIN_MAIN                                = UNCHANGED (1cb45382)
```

**Relaunch note.** A relaunch must be hosted so that no process holding a P10 marker string stays alive while the supervisor runs its preflight. For example, start the canonical command from a short-lived detached launcher whose own command line carries no marker. Run `issuance.py launch-preflight` immediately before.

## r1 (historical)

**Classification: governance only.** Nothing was launched: no launch command was invoked, no production runtime root was created, no scientific worker was started, AWS was not touched, and no result-bearing compute ran. The design and meaning of `PROTOCOL.md` are unchanged. It records how the countersignature role and the P07 classification were derived.

## Sequence

| Step | Commit / time (UTC) | Outcome |
|---|---|---|
| Issuance protocol and tests | `ae601630` | 12/12 adversarial tests PASS (Mac and rebaseguard-vultr-02) |
| Phase A `review-preflight`, bound host at `ae601630` | 10:51:38Z; evidence `292e8f6b`, sha `b8f47ec5e9f2421f4a1677c94ccf444fc8df45ae989d13765ddbf929556af78f` | `READY_FOR_COUNTERSIGNATURE`: P01–P06 and P08–P10 PASS, P07 `COUNTERSIGNATURE_MISSING`, launch not authorized |
| Pre-write temporal check | 11:02:13Z | Branch tip, clean tree, four full hashes, root absent, 0 cells, 0 processes, fence intact: unchanged since review |
| Countersignature, written after the operator's explicit authorization | `6b8aad68` (only `config/COUNTERSIGNATURE.json`) | sha `a58b1ad175567b232531ee4a65d131bbf48d6a72b9c7d1f71ac996e04734821f`; frozen `verify_countersignature` PASS; issuance bindings PASS |
| Frozen P01–P10 preflight, bound host at `6b8aad68` | 11:07:29Z | All PASS (P07 PASS); entrypoint READY |
| `launch-preflight` | 11:07:54Z | `READY_TO_LAUNCH_PRODUCTION`, no binding problems |

The post-signature evidence is in `evidence/post_signature_r1/`. `POST_SIGNATURE_RECORD.json` indexes the two host outputs by sha256.

## Final report

```text
COUNTERSIGNATURE_ROLE               = OUTPUT_OF_SUCCESSFUL_REVIEW
P07_CLASSIFICATION                  = POST_SIGNATURE_ONLY
PRE_SIGNATURE_SUBSTANTIVE_REVIEW    = PASS
COUNTERSIGNATURE_TEMPORAL_INTEGRITY = PASS
INDEPENDENT_COUNTERSIGNATURE        = CREATED
COUNTERSIGNATURE_SHA256             = a58b1ad175567b232531ee4a65d131bbf48d6a72b9c7d1f71ac996e04734821f
POST_SIGNATURE_P07                  = PASS
POST_SIGNATURE_P01_P10              = PASS
LAUNCH_PREFLIGHT                    = PASS
CUSUM_READY_TO_LAUNCH_PRODUCTION    = YES
CUSUM_PRODUCTION_LAUNCHED           = NO
CUSUM_PRODUCTION_CELLS              = 0
LIVE_AWS_PS1_TOUCHED                = NO
NEW_RESULT_BEARING_COMPUTE          = NONE
ORIGIN_MAIN                         = UNCHANGED (1cb45382)
```

## Disclosures

1. **Reviewed tip.** The committed Phase A evidence was produced on checkout `ae601630`. The countersignature therefore binds `reviewed_tip = ae601630…`, and binds the evidence commit `292e8f6b…` as `review_evidence.commit` and `branch_tip_at_signing`.
2. **Independence** is session-level. The reviewer session is distinct from the successor authoring session, but it is the same model family, and it also authored this issuance tooling. The tooling does not alter the reviewed production design.
3. **Launch-path residual.** The frozen `prov_entry.py launch` enforces P01–P10 only. The issuance bindings are an additional operator-side check. Run `issuance.py launch-preflight` immediately before any launch.
4. **Future launches.** A launch now needs only an explicit operator command: `prov_entry.py launch --confirm-checkpoint-sha256 dd4c89d7… --confirm-authorization-sha256 b8f11ec0…`. This session did not run it.
5. **Host scratch.** The host keeps `aux5-countersign-*` scratch outputs under `/root/work/postk1-runs/`, outside both production roots.
