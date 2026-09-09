# SR worker-count scaling study — runtime fingerprint and pre-run verification
Study run 2026-09-09 05:11:37Z – 06:58Z on the resized AWS host.

## Worktrees (verified before the study; re-verified after)
  /home/ubuntu/work/ReBaseGuard              p5y-gate1-micropilots  ea2ce6bd9d2aad9008f94e8ae304d69a623c5e2d  CLEAN (0 entries)
  /home/ubuntu/work/ReBaseGuard-sr-parallel  p5y-k1-sr-parallel     4f0c7d7f1ee0b7959d07b7340609bc03c1006966  CLEAN (0 entries)
Both match the expected HEADs. No study artifact was written into either worktree.

## CPU / topology
  Intel Xeon Platinum 8488C (Sapphire Rapids), family 6, model 143, stepping 8
  16 physical cores, 32 logical, SMT2, 1 socket, 1 NUMA node
  L1d 768 KiB (16 inst), L1i 512 KiB, L2 32 MiB (16x2 MiB), L3 105 MiB (1 instance, shared)
  KVM full virtualisation; AVX-512 + AMX present; aperfmperf/constant_tsc/nonstop_tsc
  SIBLING MAP: cpu i and cpu i+16 share physical core i (i = 0..15)
  No cgroup CPU limit (cpu.max: none). No cpufreq sysfs (virtualised).
  PMU NOT available: /proc/sys/kernel/perf_event_paranoid = 4, "No supported events found".
    -> effective per-core speed measured instead by an in-process rate probe using the
       SAME instruction mix as the workload (256-bit arb multiply-add).

## Machine state at study start
  uptime load average 0.00 / 0.13 / 1.21; 122 GiB of 123 GiB RAM free; swap 0
  No unrelated heavy process: top CPU consumer 0.3% (systemd). No leftover benchmark procs.

## Runtime
  CPython 3.12.3 (main, Jul 15 2026 23:46:41) GCC 13.3.0, glibc 2.39
  python-flint 0.9.0, FLINT 3.6.0 (Arb merged in: 910 arb_*, 913 acb_* symbols)
  numpy 2.5.2, scipy 1.18.1; flint.ctx.threads = 1; ctx.prec = 256

## BLAS
  libflint links NO BLAS (needed: libmpfr, libgmp, libm, libpthread, libc only).
  The certified interval arithmetic never enters OpenBLAS. OpenBLAS is reached only
  by numpy during the candidate collocation solve.
  RUNTIME-SELECTED kernel, read from the mapped library (not build config):
    numpy ILP64 scipy_openblas_get_corename64_ -> SkylakeX
      "OpenBLAS 0.3.34.0.0  USE64BITINT DYNAMIC_ARCH NO_AFFINITY SkylakeX MAX_THREADS=64"
    scipy LP64  scipy_openblas_get_corename    -> SkylakeX
      "OpenBLAS 0.3.31.dev DYNAMIC_ARCH NO_AFFINITY SkylakeX MAX_THREADS=64"

## Backend library sha256 (unchanged; match committed producer_manifest_v2.json)
  libscipy_openblas64_-61654e39.so  6cad8d2ad994ddc43d2ccdb0fb5d9458373ff1b87ef7ff420f2f94406eb8f082
  libflint-6839011d.so.24.0.0       871a4132fd1e9f3638391b2208e07088f8e3e72a10e41d45f58b150a60c2a1a9
  libgmp-e0c82b6b.so.10.5.0         33d24e675b10f8b1ab93a8ad3fa2ed5012e1b0d89dcdb97273877c6c6b9450d8
  libmpfr-be332c05.so.6.2.2         c4dfcfc7c5c7ab71d427e15f2f9fae4ace88592a81d4596a918dcc02eadfc6e3

## Threading contract — CONFIRMED IN EVERY BENCHMARK PROCESS
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
  NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
  Each worker records os.environ for all six and reports violations.
  Across all 15 runs / 219 worker processes: thread_env_violations = NONE.

## Frozen benchmark packet (identical for every worker count)
  patches      : (17,11) A_reference, (0,0) B_max_span, (63,63) C_sliver_heavy
                 -- the three FROZEN benchmark cells of frozen_audit.json
  panels       : 4 real panels per patch from the frozen p1 rule -> 11 real panels
  moment shifts: 0,1,2,3 (all relevant)  -> 44 frozen (patch,panel,shift) contexts
  candidate    : GENUINE production F_0 candidate, task1_f0.build_candidate --
                 collocation solve rounded to exact dyadic Chebyshev coefficients.
                 17x17, all 289 entries nonzero. NOT a random synthetic matrix.
  control      : the protocol's declared DENSE random candidate (seed 1)
  inner loop   : build Rbig once per panel (panel-only work), then 102 contracts
                 against it -- the real production amortisation
  packet       = 44 contexts x 102 contracts = 4488 contracts
  per worker   = 25 packets = 112,200 contracts   (~5 min at 1 worker)
  arithmetic   : accepted O9 contraction ordering, 256-bit certified interval arithmetic
  D=11, Z=20, cand_degree=16, e=1/4 -- all frozen, unchanged.

## Affinity (recorded per run)
  1/4/8/16 workers : one worker per DISTINCT physical core, cpus 0..N-1
  24 workers       : cpus 0-15 (all 16 physical cores) + cpus 16-23
                     -> 8 physical cores DOUBLY occupied, 8 singly occupied
  32 workers       : cpus 0-31 -> all 16 physical cores doubly occupied

## Scope discipline
  Nothing was changed: scope, precision, degrees, certificate semantics, thresholds,
  the governing CPU-hour cap, and all historical P5/P5X/P5Y artifacts are untouched.
  No approximate arithmetic path was used. Production was NOT started.
