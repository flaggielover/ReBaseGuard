# Q6 new-glibc requalification: result

**Result: Q6 PASS. `CARRYOVER_ROUTE = ELIGIBLE_FOR_INDEPENDENT_REVIEW`.**

This is not an authorization. No countersignature exists, no successor checkpoint exists, and production was not launched. `glibc_successor.py launch-readiness --q6 Q6_RESULT.json` returns `NOT_READY` (`COUNTERSIGNATURE_ABSENT`, `SUCCESSOR_CHECKPOINT_ABSENT`).

The machine-readable result is `Q6_RESULT.json` (sha256 `894f2e8aae6eb38beb2d389a1447a0fce8e1d0d3189fb49ca683701604dc3d88`). `code/q6_result.py verify` rebuilds it deterministically from the committed evidence.

## Bindings

| Object | Value |
|---|---|
| Governance freeze commit | `3e26bb3016a45236a3ecb38236dc0ddd463e5650` |
| Proposal manifest | `964dc9691a4d5261d244c64426b6438a2ca7e6d2ef7329c26399345d60e34241` |
| Predecessor binding | `0676fc8267bac3fc6044ab4cb9f57c8769b2b9d62e0d2f0bb2a2d3b1d9db8ac3` (re-collected after the runs: identical) |
| Requalification protocol | `38a7f97884736e3e7cb1e35bcf7e6e2d7d82abbe263fc0cfcdb9feaad019d244` |
| Q6 reference | `124376c0f98a112ebc2404db72bec782646d1d14fd8a359b8dd6425df5548597` |
| Run metadata | `cf0b901b09ec3120dfde586dea256fd45cbcd8626f59fc4eb43e0d04877e7223` |
| Frozen analyzer output | `1376825ebbf0c1f2f04f6d7823ee05e99404b77b081e45d8835bf2c6f195ba8e` |

## 1. Host containment

Applied on 2026-09-14 at 08:29:49Z, exactly as `HOST_CONTAINMENT_PLAN.md` specifies.

| State | sha256 | Summary |
|---|---|---|
| `evidence/containment/PRE_STATE.json` | `7c1e6d24d5214428d82e44621acccd942a56e96dc733cbf15bae55337c923d20` | both apt timers enabled/active, both services static, periodic keys `"1"`, no holds, no drop-in |
| `evidence/containment/POST_STATE.json` | `5af4e10228278be2308cf0caf584328c2a320118f2e24d081f575fd3bcef5940` | both timers disabled/inactive, both services masked, drop-in `99-rebaseguard-cusum-freeze` sets both periodic keys `"0"`, exactly 8 holds; no package version, library hash, kernel or Debian apt file changed |
| `evidence/containment/POST_RUN_STATE.json` | `9cead60d02167a4f7e45d1e982ed5bd2511c63f04d01eb23083e3c9ef36bcf72` | identical containment after the runs |

- **No other install path is armed.** The `apt-compat` cron script exits on systemd hosts, `apt-listchanges.timer` was already disabled, packagekit and snapd are not installed, and no install-on-shutdown key is set.
- **Holds:** `libc6 libc-bin libgcc-s1 libstdc++6 zlib1g libcrypt1 linux-image-amd64 linux-image-6.12.107+deb13-amd64`.
- **Restore** by `HOST_CONTAINMENT_PLAN.md` §3.

## 2. Qualification worktree

- **Worktree:** `/root/work/postk1-q6-d31ea4ed`, a separate clone from the host's local bare repository, detached at `d31ea4edd5a96be5c9ac0a7d4acea2a5a3c5e563`. It had no tracked or untracked changes before launch or after the runs. The production checkout `/root/work/postk1-aux5` (`50cb25ae`) was not used.
- **Frozen files, byte-identical:**

| File | sha256 |
|---|---|
| `qualify5.py` | `7d917e51…` |
| `run_qualification.sh` | `9b38489d…` |
| `analyze_qualification.py` | `dc2d9fb5…` |
| `cap_formula.py` | `bf100884…` |
| `QUALIFICATION_PROTOCOL.json` | `81e28577…` |
| `producer_manifest_v3.json` | `611bd0a9…` |

- **`env -i` probe in the clone:** `manifest_v3.verify()` OK, 60 files, no problems. Manifest `b55a2da1…`, runtime contract `bc75c9ea…`, producer identity `3692d0fe…`. CPython `3.12.3 (main, Apr 15 2024, 18:25:56) [Clang 17.0.6 ]`, NumPy 2.5.2, SciPy 1.18.1 (metadata, not imported), python-flint 0.9.0, OpenBLAS `0.3.34.0.0 … Haswell`, runtime core `Haswell`.
- **Host at launch and at run end:** identical (`4db9e45d…`) and equal to the frozen protocol. Kernel `6.12.107+deb13-amd64`, glibc `2.41-12+deb13u4`, libc `9792e3cb…`, and all 11 library hashes and 8 package versions.

## 3. Runs

- **Launch:** the frozen `run_qualification.sh` from the clone, detached with `setsid nohup`, with 4 concurrent fresh `env -i` interpreters under the frozen thread contract.
- **Timing and control:** started 08:33:52Z, done 09:09:02Z. No retries, no production ledger, output outside the repository and both production roots.

| Run | CPU (observed) | rc | Record sha256 | run.log sha256 | CPU-s incl. dependencies |
|---|---|---|---|---|---|
| 318A | 0 | 0 | `1227ccfac08ae816d3fe71905aa34be836b2b38461e6b024e6b2b931980aedd3` | `9fe3882fcbab04103cb066f6b621188efc3575301ca70fa056ad6e2eb81a031d` | 2085.036 |
| 318B | 2 | 0 | `670c87edcfda4c0122c3b5490bb3cc44fbb67884188fe0707cb283e074aa1752` | `3e9b2928a5b31df5257a3221701ff1c57f9b35ad061e1d2cf49c6abb667ae73d` | 2109.124 |
| 323A | 4 | 0 | `1271938a317f96dfef3979c30f98493fe4b3ee5988af3842d04df712394645be` | `063d6764593193e8efdfc20ce1569c10e98c2c1ee180b7f37706b0e249d22a5b` | 2071.152 |
| 323B | 6 | 0 | `2671319a942b2306c61ec5964ffa6f87f29eddb432e5f9686a58629060913835` | `8fa7578b854f48bf86e0eb6bbafb54cdd7edb582a2c5e837c293f34265136ad3` | 2089.074 |

`run.log` is each run's combined stdout and stderr; the launcher log is empty. No new record is byte-identical to any predecessor qualification record.

## 4. Gates

| Gate | Result |
|---|---|
| P1 runs complete (rc 0, final gate `final`, provenance chain verified, SciPy-free) | PASS (4/4) |
| P2 scientific hash identical across repeats | PASS (318, 323) |
| P3 certificate hashes identical across repeats | PASS (318, 323) |
| P4 runtime contract and producer identity | PASS (4/4) |
| P5 backend libraries bound (4 families, absolute paths) | PASS (4/4) |
| Frozen shape (CPU pinning 0/2/4/6, `--bits 256`, cell index, certifier constant flags) | PASS (4/4) |
| Frozen analyzer (`analyze_qualification.py`) agrees with the independent re-derivation | YES (`QUALIFICATION: PASS`, `CUSUM_DETERMINISM: PASS`) |
| **Q6 scientific hash identity** | **PASS**: 318A/B = `01ff4f7a2632102475805537f439ccbe7932b68339eafa37d5ecdd03c13edda9`; 323A/B = `054a5ef0cd932ddcac3b4b2dc1a9b461e353ae6b51a2d726a5ccbc9607e57077` |
| **Q6 certificate hash identity** | **PASS**: all 28 certificate hashes per cell equal the predecessor reference, for every repeat; 0 differences |
| **Q6 final** | **PASS** |

The glibc change from 2.41-12+deb13u3 to deb13u4 is therefore bit-inert for the frozen Aux5 scientific content and certificates of the representative cells 318 and 323.

## 5. Qualification CPU and cap

- **Qualification CPU:** 8354.386 CPU-s total, c_max 2109.124 CPU-s. This is excluded from the campaign cap and disclosed here.
- **Cap:** the frozen formula still gives 300 CPU-h, since 2109.124 ≤ 2431.904. The absolute campaign cap is unchanged, and the successor residual cap stays 817,313,389,420 µs.

## 6. Not done

- No carry-over authorization, countersignature, successor checkpoint or production launch.
- No change to predecessor namespaces or runtime evidence.
- AWS, SR and PS1 were not touched, and `origin/main` was not modified.

**Remaining on the host:**
- the clean clone `/root/work/postk1-q6-d31ea4ed`;
- raw outputs under `/root/work/postk1-runs/glibc-successor-q6/`;
- the verifier copy under `/root/work/postk1-runs/glibc-successor-tools/`;
- containment stays applied until restored.

**Next step:** an independent carry-over governance review.
