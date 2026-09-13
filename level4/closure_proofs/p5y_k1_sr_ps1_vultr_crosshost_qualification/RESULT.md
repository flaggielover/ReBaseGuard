# Lane B: PS1 SR definition audit and Vultr cross-host qualification (NON-PRODUCTION)

**Classification.** `NON-PRODUCTION`, `NON-DISPOSITION-BEARING`. No cell obligation, T3/T4/T5 status,
B_cover ratio, ledger or production namespace was computed, read for disposition, or written.
Compute used: 3 × ~262 CPU-s of patch replays, plus two post-hoc diagnostics of a few CPU-minutes,
all on Vultr. Nothing ran on AWS.

## 0. Premise correction (audit finding)

The brief says "K1 has CUSUM machinery but SR remains unfinished / unqualified". The repository
records the opposite split:

- **SR is the qualified, authorized and currently running campaign.** PS1 has 369 successor cells;
  `PS1_PRODUCTION_AUTHORIZATION_CLOSED` was recorded at `29b3bffb`. The generation-2 run has been live
  on AWS since 2026-09-12T15:46Z.
- **CUSUM is the incomplete half.** Aux4 has 2/326 cells under its producer and requires a full
  326-cell rerun (`CUSUM_AUX4_INCOMPLETE_FULL_COVER`).

So this lane did not build a second SR producer, which would duplicate the frozen, authorized one.
It audited the existing definition. It then qualified the one SR question the records leave open:
whether a second host can run the PS1 producer (`VULTR = NOT_QUALIFIED_FOR_PS1`).

## 1. SR definition audit: PASS (each item located in a committed, hash-bound record)

| item | where it is fixed | finding |
|---|---|---|
| exact SR recurrence | `p5_nonlinear_dynamics/DEFINITION_AUDIT.md` §1 → `level4/stage_d/src/stopped.py::_sr_update` (two-chart log-domain, `A = 520.886133602749`) | defined; certified path uses the resolvent form of `R_{SR,m}` |
| stopping-time convention | DEFINITION_AUDIT §2.4–2.7: `tau = inf{t≥1: alarm after update}`, two-sided inclusive, window `w = min(m,tau)`, terminal increment included | defined |
| m / rho / domain mapping | target `sup_e \|R_{D,m}(e)\| < 2`, m ∈ {1,2,3,5}; drift domain `[0, c_SR]` with oddness; cell `e0=(L+R)/2`, `rho=(R−L)/2` exact affine `[p,s]=p+s·c_SR` (`succ_cells.py`, 256-bit checks). The reference-reuse `rho∈[0,1]` of T2 is a different quantity and enters only as `f_rho = rho·R`. | defined; the two meanings of "rho" must not be conflated in reports |
| RNG address semantics | none on the certified path: the PS1 producer is interval arithmetic (Arb, 256 bits) plus a deterministic float candidate construction. RNG appears only in the P5/P7 Monte-Carlo correspondence (`z = rng.standard_normal(...) − e`, frozen order) | N/A for the producer; recorded for the numerical-evidence tier |
| producer manifest | `LAUNCH_AUTHORIZATION.json` `executor_source_manifest` (39 files) → `scientific_adapter_hash 13ba2ecd…` | bound |
| runtime contract | `multihost.ROLES.AWS.runtime_contract_hash fb0dbe33…` (python, flint, numpy, BLAS name/version, 6 thread vars) | bound, **but see §3: it does not capture the BLAS kernel** |
| numerical backend binding | python-flint 0.9.0 at 256 bits; numpy 2.5.2 with scipy-openblas 0.3.34 DYNAMIC_ARCH | bound by version, not by kernel |
| scientific vs incidental hash classification | `succ_t3_aggregate.aggregate()` strips `cpu_seconds, peak_rss_kib, cache_hits, cache_misses` before `consumed_records_sha256`; `scientific_content_hash = H(t3_record, t4_record, t5 certificate hashes)`; T1 identity hash includes `runtime_binding.numpy_config_sha256` (incidental host metadata inside a scientific identity) | classified; one host-metadata leak into identity noted |
| deterministic certificate / replay | protocol `determinism_contract`: bit-identical records across processes, batch sizes, worker counts and runs; the recorded replay is 6/6 on AWS | defined; **same-host scope only** |
| representative-cell launcher, resumability | `ps1_cellseq_launcher` + portable recovery (per-cell durable markers, checkpoint/export/resume) | exist (Lane A repairs their path binding) |
| cost measurement | Phase-4: 13 real cells, 11.94 CPU-h/cell mean; cells-outer 15.43 CPU-h/cell → 5,694 CPU-h | measured |

## 2. Vultr qualification set (predeclared: `config/PREDECLARATION.json`, sha256 `2db592d5…`, logged before start)

The set is 24 (cell, patch) pairs. The cells are the cold-cache group leaders 0, 148, 360 (the old-313 region) and 368 (terminal), with 6 patches each, stratified by AWS CPU rank.
The producer is the bound `opt_core.core` at tree `082526be`, run in fresh interpreters on distinct physical cores.

| measure | result |
|---|---|
| runtime fingerprint sha256 | `fb0dbe33…` = the AWS runtime contract hash |
| **determinism across fresh processes** (R1 vs R2, 24/24 pairs) | **PASS**: byte-identical |
| **cross-host bit identity vs committed AWS records** | **FAIL**: 0/24 identical (R1, R2); the diagnostic R3 `OPENBLAS_CORETYPE=Haswell` is also 0/24 |
| wall time per replicate process | 262–263 s |
| CPU-seconds per replicate process | 261.7–263.2 s |
| peak RSS | 132 MiB (max 135,148 KiB) |
| Vultr / AWS per-patch CPU (same pairs) | 0.852 overall; per-pair p50 0.873, p90 0.900 |

## 3. Why cross-host identity fails (post-hoc diagnostics, labelled as such; they do not alter §2)

1. The candidate identity list hash differs for all 4 cells: `diag_clsha.txt`.
2. Frozen cell 150's T1 candidate set was rebuilt on Vultr and compared with the committed AWS set
   `p5y_k1_sr_o9_executor_t1_successor/evidence/cell150_candidate_set.json`:
   - **22 of 46 nodes have identical mantissas; 24 differ, by up to 776 units of 2⁻⁵⁰.**
   - identity hashes differ on 46/46 nodes; the only differing runtime-binding key is `numpy_config_sha256`.
   - the producer hash and the construction spec are identical.
3. On Vultr, candidates are identical under the default, Haswell and Zen kernels.
   The difference is therefore AWS-vs-Vultr (AVX-512 Sapphire Rapids vs AVX2 Zen) in the float
   Nyström/LAPACK construction. The prior predeclared multihost check (`p5y_k1_sr_multihost_successor`,
   random candidates, Arb contract stage only) showed `CROSS_HOST_BYTE_IDENTITY_HOLDS`.
   This localizes the sensitivity to T1 float construction, consistent with CUSUM Aux4's
   `blas_kernel_sensitivity.json` (62/240 candidates differ between two kernels on one host).

Scientific meaning: a different dyadic candidate still gives a rigorous enclosure. It is a
**different certificate**, though, so under the frozen determinism contract a Vultr-produced cell is not
a replay of an AWS cell. The runtime contract hash does not detect this, because it binds the BLAS
version and not the kernel.

## 4. Projection (full SR on Vultr-class cores; predeclared rule; not an authorization)

| AWS basis | Vultr-equivalent CPU-h (ratio 0.852) | p90 band |
|---|---:|---:|
| cells-outer production shape 5,694 | 4,850 | 5,127 |
| patch-outer qualified mean 4,413 | 3,759 | 3,974 |
| patch-outer worst group 4,642 | 3,954 | 4,180 |

On 4 physical cores that is about 50 days of wall time, so Vultr is not a practical PS1 host even if identity held.

## 5. Verdicts

```
SR_DEFINITION_AUDIT                  = PASS
SR_PRODUCER_QUALIFIED                = YES_ON_AWS_ONLY   (pre-existing PS1 qualification; not this session)
SR_DETERMINISM_FRESH_PROCESS         = PASS              (same host, 24/24 pairs R1 == R2)
SR_CROSS_HOST_BIT_IDENTITY           = FAIL              (0/24 pairs vs committed AWS records)
SR_VULTR_RESULT_BEARING_ELIGIBILITY  = NO
SR_PROJECTED_CPU_HOURS               = 4,413–5,694 CPU-h AWS basis (live cells-outer shape 5,694);
                                       3,759–5,127 Vultr-equivalent (not an authorization)
SR_FULL_RUN                          = the live 369-cell PS1 campaign on AWS (generation 2, under drain)
NEW_RESULT_BEARING_COMPUTE           = NONE
```

Adverse findings retained without softening:
- Vultr/AWS cross-host divergence in T1 candidate construction.
- 0/24 bit-identical cross-host replay pairs.
- Cell-150 candidate mantissas differ on 24 of 46 nodes, by up to 776 units of 2⁻⁵⁰.
- The runtime contract hash (`fb0dbe33…`) is identical on both hosts, so it fails to distinguish the host arithmetic behaviour that changes the certificate.

Making Vultr admissible would need a governed successor that transports AWS-built candidate sets as
authenticated inputs, or binds the kernel into the runtime contract. Topology A (AWS only) does not need that successor.
