# Host-drift forensic audit: CUSUM Aux5 provenance-successor production (halted)

**Classification: governance only.** Every observation below was made read-only on 2026-09-14. No runtime evidence was modified, and no certifier, supervisor or worker was started. The machine-readable form is `config/PREDECESSOR_BINDING.json` (sha256 `0676fc8267bac3fc6044ab4cb9f57c8769b2b9d62e0d2f0bb2a2d3b1d9db8ac3`). It was collected twice on rebaseguard-vultr-02, 07:50:44Z–07:51:55Z, and both runs were byte-identical.

## 1. Governing predecessor identities

| Object | Value |
|---|---|
| Branch / production checkout | `p5y-postk1-frontier`; `/root/work/postk1-aux5` at `50cb25ae5f2db2713201f80ef7065e575332051d`, clean |
| Provenance checkpoint | `dd4c89d773c411355d93d0d703e40c027f9913e11e116e4bfe35117f84b4baf2` |
| Freeze record | `e61dcc15f8f6ab89752596109782d9108e8d25962271e3858b6c8b8a7af31ec1` |
| Run authorization | `b8f11ec05efc2476f733dd989ae02b542dc9efa374f24fa0a27688d76ec2b329` (commit `9719cba2`); `CUSUM-AUX5-PROD-AUTH-001`; run `CUSUM-AUX5-PROD-R1` |
| Active countersignature | `1ceb92d463d1332dfb26505143454b3c3fd87a611bc731372d9e227017682b07` (issuance v2, commit `50cb25ae`). Revoked: `a58b1ad1…` |
| Ledger id / supervisor run | `61eb8565e382127620e85831673608d80e38364d0ee935888f30f0ee48034082` / `R20260913T115713Z-103963` (pid 103963, keeper 103960) |
| Producer | identity `3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19`; runtime contract `bc75c9ea7cd5f9406a0509bb0a161aa2c013f80427d1035197989e3d202c845a`; manifest file `611bd0a9f356b0e7f5e63da60567ac1afa9e69fc1f8c464c7e5b89aeedbd2b9f` |
| Runtime root | `/root/work/postk1-runs/cusum-aux5-production-prov-r1` |
| Boot | `eefa85dc-14db-4ba0-912f-f95eeece9c2b`, btime `1788930261`, CLK_TCK 100 (one boot for all 128 attempts) |

## 2. glibc identities

| | Bound (old) | Live (new) |
|---|---|---|
| Package `libc6` / `libc-bin` | `2.41-12+deb13u3` | `2.41-12+deb13u4` |
| `/usr/lib/x86_64-linux-gnu/libc.so.6` sha256 | `fa430b8f298f817a266046af84a77533185ad6fc4406c7d3787b5a0a0c207826` | `9792e3cbb541c8f44c7acf5f14f4022ea62998ecc787d326bed4d8b6547dfd92` |
| Replacement time | — | ctime `2026-09-14T06:10:59.784621549Z` (`libc_ctime_ns` 1789366259784621549); dpkg `upgrade libc6:amd64 2.41-12+deb13u3 2.41-12+deb13u4` at 06:10:59 |
| Cause | — | `apt-daily-upgrade.timer` → `unattended-upgrade`, started at 06:10:40Z (see `HOST_CONTAINMENT_PLAN.md`) |

The deb13u4 changelog lists `ungetwc` (CVE-2026-5928), `scanf %mc` (CVE-2026-5450), iconv `//TRANSLIT` errors, and a build fix against Linux 7.0 headers. It lists no libm change.

## 3. Timeline (journal, 1,611 hash-chained entries; ledger state == last entry)

| Seq | UTC | Event |
|---|---|---|
| 0 | 2026-09-13 11:57:17.835 | `GENESIS` (entry sha `eee65c7bf364e3bd6611ad8150178f3c04ab8faaf613ac9ae9a189c2c32272b8`), naming the authorization block above |
| 1565 | 2026-09-14 05:39:53.806 | **Last admission**: `RESERVED` cell 127, core 0 |
| 1566 | 05:39:53.823 | **Last worker start**: `RUNNING` A00127-C0127; process start from `pid_start_ticks` = 05:39:53.670 |
| — | 06:10:59.785 | **glibc replaced** (libc.so.6 ctime) |
| 1598, 1599 | 06:11:14.415, 06:12:14.432 | `HEARTBEAT` |
| 1600 | 06:12:29.651 | `SEALED` A00124-C0124 frees core 4, the first admission opportunity after the replacement |
| 1602 | 06:12:29.846 | **Drift detection**: the frozen `_admit` host guard writes the stop transition with reason `HOST_DRIFT`. No `RESERVED` follows. |
| 1603 / 1606 / 1608 | 06:12:59.998 / 06:13:55.337 / 06:14:05.660 | `SEALED` A00125, A00126, A00127, each followed by `PROVENANCE_BOUND` |
| 1608 | 06:14:05.660 | **Last seal** (cell 127) |
| 1610 | 06:14:05.841 | **Terminal disposition** (`DISPOSITION_` + terminal state); supervisor exit 20. Last entry sha `eed2a5558b7fcbaf5144f346b98e917cf462a462787c02ce6f25f259d8003eae` |

Detection latency was 90.06 s. The guard runs only before an admission, and all 4 cores were busy from 05:39:53.8Z until 06:12:29.65Z.

## 4. No post-drift admission and no post-drift worker start

- **Journal entries after the replacement:** only `HEARTBEAT` (1598, 1599, 1605), `SEALED`/`PROVENANCE_BOUND` (1600–1601, 1603–1604, 1606–1607, 1608–1609), the stop (1602) and the disposition (1610). There is no `RESERVED` and no `RUNNING`.
- **Admissions:** every `RESERVED` is at or before seq 1565 (05:39:53.806Z), 31 min 6 s before the replacement.
- **Worker starts:** every worker process start (`btime + pid_start_ticks/100`) is ≤ 05:39:53.670Z, and each lies between its reservation and its `RUNNING` entry.
- **Machine-checked:** `verify_binding` (codes `POST_DRIFT_ADMISSION`, `POST_DRIFT_WORKER_START`, `DRIFT_DETECTION_NOT_FAIL_CLOSED`) passes on the committed binding.

## 5. Cells 124–127

| Cell | Reserved | Process start | Sealed |
|---|---|---|---|
| 124 | 05:37:52.636 | 05:37:52.500 | 06:12:29.651 |
| 125 | 05:38:38.059 | 05:38:37.930 | 06:12:59.998 |
| 126 | 05:39:38.446 | 05:39:38.310 | 06:13:55.337 |
| 127 | 05:39:53.806 | 05:39:53.670 | 06:14:05.660 |

**Runtime-semantics analysis:**
1. **dpkg replaces files by rename.** It installs a new file and renames it over the path, giving it a new inode. A running process keeps the old file mapped and its contents never change.
2. **CPython loads the whole glibc family at process start.** The uv CPython 3.12.3 binary depends on `libpthread`, `libdl`, `libutil`, `libm`, `librt`, `libc` and `ld-linux`, all from package `libc6`. All were mapped at process start (05:37:52–05:39:54Z). A later load of the same library returns the already-loaded object.
3. **No other upgraded library can be loaded.** Across the 178 shared objects in the interpreter and the venv, the only system libraries reachable are glibc-family plus `libgcc-s1`, `libstdc++6`, `zlib1g` and `libcrypt1`. Of the 51 packages upgraded at 06:10–06:11, only glibc is among them.
4. **The frozen runtime check could not see the change, and all its checks passed.** The runtime contract compares the glibc version string only (`["glibc","2.41"]`, unchanged) and the venv backend-library bytes (unchanged). Every record passed the seal's runtime-contract equality check. Cells 124 and 127 show final gate `final`, `provenance_chain.all_verified`, and are SciPy-free.
5. **Residual, not traced:** lazily loaded glibc plugins (iconv gconv, NSS). They could affect only incidental host fields, never the scientific hash. Q6 is the empirical guard for the new runtime.

```text
CELLS_124_127_OLD_RUNTIME_SEMANTICS_PRESERVED = YES
```

## 6. Integrity

| Check | Result |
|---|---|
| Frozen `prov_integrity.audit` (read-only, against checkpoint `dd4c89d7`) | domain 326, sealed 128, **verified pairs 128**. Issue keys only the stop record and `D_unsettled_supervisor_runs`. Pairs digest `07e6adb37efd624d182df6d50c396b4f1d4da26aeec374a18a9e1f7a66a70067` |
| Frozen `verify_sealed_evidence(full=True)` | 128/128, including scientific-hash recomputation |
| Record / envelope hashes | every file hash equals its seal and its bound envelope hash; every envelope names its record and cell |
| Duplicates | no duplicate record, envelope or scientific hash; exactly one attempt per cell; no torn, failed, released or orphan attempt |
| Authorization linkage | every envelope names authorization `b8f11ec0…` and countersignature `1ceb92d4…`; the genesis state and entry 0 carry the same block |
| Qualification firewall | no record equals any of the four qualification record hashes; every envelope has `is_qualification_record: false` |
| Cells digest | `2a93585ced70138afc3f3ca1175fbf34280bcc99d1087b630cafc36cd02dba3f` |

## 7. Terminal state and settled CPU

| Object | sha256 |
|---|---|
| `ledger.json` | `eebc21e7801888b31e892f9e81aa7c4954758cb55031afbcfac6be27f6e4d712` |
| `journal.jsonl` | `02170cae2cb25559e24d802e827d19c3c07fd5ee104aa246778f9e5034edc00c` |
| `reaper.jsonl` | `84d09fd47f794246a1820d873dd4ac398e132bfad446372e86b1e05ad5278f9f` |
| Ledger state (canonical) | `b3cee6fff848d55aaba7ae143b43e77563663b929c8f5483d8eeec47875b60cb` |

The disposition is terminal on the host-drift stop, with cells 0–127 SEALED and 198 PENDING. The frozen preflight's run-state check (P09) refuses any relaunch of this ledger, and it is never written again.

| Component | µs |
|---|---|
| Committed in ledger (science 262,623,734,174 + supervisor 62,733,953) | 262,686,468,127 |
| Unsettled supervisor run, frozen REAPER_RUSAGE rule (262,682,097,826 − 262,623,904,846 − 58,121,474) | 71,506 |
| Unmatched keeper exit (pid 103960) | 70,947 |
| **Predecessor settled CPU** | **262,686,610,580** (72.968503 CPU-h) |

The settlement was computed in memory only; the predecessor ledger was not settled.

```text
HOST_DRIFT_FORENSICS                  = PASS
OLD_128_SCIENTIFIC_INTEGRITY          = PASS
OLD_128_PROVENANCE_INTEGRITY          = PASS
POST_DRIFT_ADMISSION_OCCURRED         = NO
POST_DRIFT_WORKER_START_OCCURRED      = NO
HALT_WAS_FAIL_CLOSED                  = YES
OLD_128_ELIGIBLE_FOR_CARRYOVER_REVIEW = YES
```
