# P5Y K1 CUSUM Aux5 production checkpoint: result

**Classification: governance and readiness only.** No production cell was launched and no result-bearing compute ran. This record closes nothing scientific. The CUSUM successor moves from **QUALIFIED** to **READY_TO_LAUNCH_PRODUCTION**.

## Freeze

| Object | Value |
|---|---|
| Checkpoint candidate commit | `54b77949` |
| Freeze commit | `532c880e` |
| `config/PRODUCTION_CHECKPOINT.json` sha256 | `4026f296bd7b32bea24a0f73422f4fc8df1f0c1d04aea952ee7ed0f5313c3c5c` (36 bound sources) |
| `evidence/acceptance_r1/ACCEPTANCE_RESULT.json` sha256 | `3d5b6eb8d0ef8427677225cfd3ca0d0b73f15b80336b845424e4194f06b10eaf` |
| Producer identity / runtime contract | `3692d0fe…` / `bc75c9ea…` (Aux5 manifest v3, unchanged) |
| Certifier | Aux5 `qualify5.py`, unmodified, run as its own `env -i` interpreter |
| Host | rebaseguard-vultr-02 (machine-id sha `e9144212…`, kernel 6.12.107+deb13-amd64, glibc 2.41-12+deb13u3, libc sha `fa430b8f…`) |

## What the checkpoint binds

Every item below is hash-bound in `PRODUCTION_CHECKPOINT.json`.

- **Producer and runtime:**
  - producer: manifest v3 file sha, the three identity hashes, the certifier bytes;
  - runtime: the full runtime contract, the venv python, and the worker argv (identical to the qualification command);
  - workers: cores 0, 2, 4, 6 (one per physical core), with `PR_SET_PDEATHSIG`.
- **Science:**
  - universe: 17,978 obligations, 326 CUSUM cells;
  - geometry: `cells.json` sha `341eb5e9…` and geometry digest `cd48d716…`, a contiguous cover [0, 11/2] with e0 ± rho = left/right, m ∈ {1,2,3,5};
  - K4 domain: cells 0..309;
  - precision: 256 bits, no escalation.
- **Record and hash:**
  - result schema: required top-level fields, the exact per-m key set, and the record-flag semantics;
  - scientific hash: Aux4 `schema.py` and `hash_v2.py` bytes, and the incidental and provenance patterns.
- **Ledger and lifecycle:**
  - ledger, journal, reaper and export schemas;
  - states: PENDING, RESERVED, RUNNING, SEALED, RELEASED, TORN, FAILED;
  - the reservation, sealed-cell, torn-attempt, failure, duplicate-cell, skip/resume, drain, restart and crash-reconciliation rules;
  - halt rules, the 3-tear retry limit, and the CPU evidence hierarchy.
- **Cost cap:**
  - the formula file and `cap_formula.py` bytes;
  - c_max `2041.449429377` CPU-s, re-derived from the four qualification records;
  - exact derivation P = 3660318826872961/18000000000000, R = 1, CAP = **300 CPU-h**;
  - invariant `115·(committed + in-flight + R) ≤ 100·CAP`.
  - The cap is bound into the ledger at genesis and can never be raised (`CAP_CHANGE_FORBIDDEN`).
- **Qualification:** result sha `c52cffa4…`, protocol sha `81e28577…`, the four record shas.
  - Cells 318 and 323 are **not imported** as production cells.
  - The seal refuses qualification bytes (`QUALIFICATION_RECORD_REUSE`), and any record claiming more CPU or wall time than its attempt used (`CPU_EVIDENCE_INCONSISTENT`).
- **Qualification CPU:** 8153.456 CPU-s is excluded from the cap accounting. The formula's N is 326 production cells, and the exclusion is disclosed in the ledger's genesis.

## Checks

**Ledger and lifecycle (`prod_ledger.py`, `prod_supervisor.py`):**
- Every state is validated before it is written and after it is read.
- A cell can hold at most one SEALED attempt.
- Each accounting bucket must equal the sum of its recorded charges.
- The ledger must continue the hash-chained journal, or be exactly one crash-step past it (repaired). Anything else is refused.

**K4 structural attestation (`config/K4_INPUT_SCHEMA_ATTESTATION.json`): `K4_CUSUM_INPUT_SCHEMA_ATTESTED = YES`.**
- The frozen K4 checkpoint (`95b1fd16ac420d6f545cbb2619a6086ced31c6d748a9c801ca7f7c114e77a1e1`, equal to its hash file) is intact, and its bound sources are unchanged.
- Its CUSUM input schema, integrity clause and the reads in `k4_assembly.py` match the consumed paths exactly.
- On the four qualification records, every consumed field is present as an exact rational: R, R′ (`D_interval`), the R″ interval and `M_R2`, e0/rho/C_upper, precision, and producer identity.
  - These cells lie outside the K4 domain, and no value was compared.
- No consumed path is INCIDENTAL, and mutating each one moves the recomputed scientific hash.
- The seal enforces the same checks on every production record.
- K4 assembly was not run.

**Real-format check:** on an incidental-field-edited scratch copy of qualification record 318A, the production seal accepts the frozen producer's genuine record structure. The scientific hash is unchanged (`01ff4f7a…`). No ledger was involved and nothing was sealed.

## Synthetic acceptance on rebaseguard-vultr-02 (clean checkout `54b77949`)

**26/26 PASS** (`evidence/acceptance_r1/ACCEPTANCE_RESULT.json`). All workers were synthetic, the frozen certifier was never started, and the production runtime root did not exist before or after.

| Scenario | Covers |
|---|---|
| s01 | clean start, reservation (RESERVED→RUNNING→SEALED), synthetic success, read-only seals, exact WAIT4 charges |
| s02, s03 | synthetic failure halts; malformed / overclaim / no-output / wrong-identity / wrong-runtime records FAILED at seal; a worker killed before writing is TORN and retried |
| s04, s05 | SIGTERM and DRAIN marker: admitted work finishes and seals; relaunch with DRAIN refused; resume completes |
| s06, s07 | worker SIGKILL / SIGTERM → TORN, charged, retried, tear counted |
| s08 | supervisor SIGKILL: no worker survives (PDEATHSIG); keeper rusage reconciles the orphans (REAPER_RUSAGE) |
| s09 | worker death after a durable record → recovered seal; a record from a self-killed worker is sealed once |
| s10, s11 | stale reservation (no pid) and unreaped orphan → TORN by tail bound; a live orphan is refused, never adopted |
| s12 | a second launch is refused (flock); a 3-way launch race produces one seal per cell; DUPLICATE_CELL / DUPLICATE_SEALED_CELL |
| s13 | sealed cells skipped, bytes untouched, deterministic ascending resume |
| s14 | corrupted sealed evidence refused at start and at export, without mutation |
| s15 | qualification bytes refused; the real record format is accepted by the production seal; CPU/age evidence refusals |
| s16 | export → corrupted/foreign/non-empty restore refused → restore → resume; scientific hashes identical to an uninterrupted run |
| s17 | exact integer admission boundary; in-flight CPU above R counted; frozen campaign at c_max fits with **72.6 CPU-h** headroom at its last admission |
| s18 | cap exhaustion → INCOMPLETE_BUDGET_EXHAUSTED (7 sealed, 5 pending), terminal; raising the cap refused |
| s19 | drain, supervisor crash and resume: accounting monotone, every keeper exit charged once, runs settled |
| s20 | naive edit, forged accounting, forged cap raise, negative charge, truncation, deleted ledger or journal, rollback, broken chain: all refused without writes; crash-gap and torn journal tail repaired |
| s21 | wrong runtime contract (OPENBLAS_CORETYPE=Sandybridge in a genuine probe) → C06 RUNTIME_CONTRACT |
| s22 | wrong producer identity (forged probe; tampered TCB file in a temporary worktree) → C06 refused |
| s23 | wrong host → C04 WRONG_HOST; admission-time host drift → HALTED before any admission |
| s24 | synthetic spec refused in the production root; synthetic record refused by the production seal; keeperless supervisor refused; launch with a wrong sha refused |
| s25 | pre-freeze preflight: only C01 and C12 fail |
| s26 | full 326-cell synthetic ledger → settle → integrity attestation accepted by the frozen `k4_assembly.check_cusum_attestation`; incomplete / foreign attestations rejected (assembly not run) |

## Entrypoint

On the clean checkout at `532c880e`, `prod_entry.py preflight` passed all 14 checks (C01–C14). Output is in `evidence/preflight_ready_r1/PREFLIGHT_READY.txt`:

```text
CUSUM_AUX5_PRODUCTION_ENTRYPOINT = READY   checkpoint 4026f296bd7b32bea24a0f73422f4fc8df1f0c1d04aea952ee7ed0f5313c3c5c
```

`launch` was not executed.

## Readiness adjudication

```text
CUSUM_PRODUCTION_CHECKPOINT        = PASS
CUSUM_LEDGER_READY                 = YES
CUSUM_LIFECYCLE_READY              = YES
CUSUM_COST_CAP_ENFORCED            = YES
K4_CUSUM_INPUT_SCHEMA_ATTESTED     = YES
CUSUM_PRODUCTION_ENTRYPOINT_READY  = YES
CUSUM_SYNTHETIC_ACCEPTANCE         = PASS
CUSUM_READY_TO_LAUNCH_PRODUCTION   = YES
CUSUM_FULL_CAMPAIGN_LAUNCHED       = NO
LIVE_AWS_PS1_TOUCHED               = NO
NEW_RESULT_BEARING_COMPUTE         = NONE
ORIGIN_MAIN                        = UNCHANGED
```

## Disclosures (for independent review)

1. **Record flags.** The frozen certifier stamps `production_run`, `result_bearing` and `scientific_certification_of_full_cover` as `false` inside the scientific hash. It also refuses to run if `spec.PRODUCTION_ENABLED` is true.
   - Changing either would change the qualified producer identity.
   - The checkpoint therefore declares these fields certifier constants. Production status is conferred **only** by a SEALED attempt in this checkpoint's ledger.
   - This follows the governance record: the qualification protocol requires a separate checkpoint for this producer, the Aux4 aggregate ledger precedent, and SR's separate production authorization.
   - It is an interpretation that an independent reviewer should confirm.
2. **Tail-bound charging.** If both supervisor and keeper die, open attempts are charged `last sample + elapsed wall time` up to reconciliation. This is sound, but it can overcharge by the unattended interval, so reconcile promptly after a double crash. The keeper's CPU after the final run is charged by `prod_entry.py settle`, which `attest` requires.
3. **Host upgrades.** Automatic upgrades stay enabled on the host and were not modified. A kernel, glibc or runtime change fails closed (C04, HOST_DRIFT) and requires requalification.
4. **Independence.** The checkpoint, the tooling, the acceptance tests and this adjudication were written by one agent session. The criteria were fixed in code before the official acceptance run, but independent review is recommended before launch.
5. **Leftover files.** Development scratch runs (`/root/work/postk1-runs/aux5-prodckpt-dev1`, `-dev2`) and the acceptance scratch (`aux5-prodckpt-acceptance-r1`) remain on Vultr, outside the repository, and are non-production. The temporary dev worktree was removed.
6. **Not touched.** The live AWS PS1/SR campaign, K2/K3/K4/K5 artifacts, frozen scientific definitions and origin/main were not touched.
