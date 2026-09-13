# CUSUM Aux4 full-rerun readiness: host binding and cost cap only (2026-09-13)

**Not a launch.** The 326-cell rerun was not started. The Vultr probe ran Aux4's own `runtime_identity.compare` against the committed manifest. The AWS probe was an equivalent inline read at `nice 19`, pinned to logical CPU 31 (outside the live workers' cores 0–15); it wrote nothing and did not touch the live campaign. No certified value was computed.

## Frozen requirement

- `p5y_k1_cusum_aux4_fullcover`: `CUSUM_COVER_INHERITANCE = REQUIRES_FULL_326_RERUN`. The ledger admits a cell only under the Aux4 producer identity `f85bd92c…`, runtime contract hash `d49f0437…` (`manifests/producer_manifest_v2.json`, schema `k1.cusum-aux4.runtime-contract.v2`).
- `runtime_identity.compare` fails on **any** key difference, except the diagnostic `openblas_coretype_env`. Bound keys:
  - CPython version, full version, build and compiler; glibc; numpy and python-flint versions;
  - **OpenBLAS runtime corename** and config;
  - the sha256 of each backend library (openblas, flint, gmp, mpfr);
  - thread environment, precision 256, Taylor order 120, collocation 12/400, subdivision depth 0.
- Committed identity: corename `SkylakeX`; CPython `3.12.3 (main, Jul 15 2026, 23:46:41) [GCC 13.3.0]`; glibc 2.39. Both existing cells (318, 323) carry exactly this contract.
- Rerun geometry (frozen `p5y_k1_cover_ledger_successor/config/cells.json`): 326 CUSUM cells; 310 of them meet `(0,2]` (also the K4 input), contiguous from 0.

## Host binding

| host | probe | mismatches vs committed runtime contract | eligible to reproduce the Aux4 identity |
|---|---|---|---|
| Vultr `rebaseguard-vultr-02` (AMD EPYC-Milan, no AVX-512) | `runtime_identity.compare` | **7**: backend_libraries (layout: the venv is outside the Aux4 tree root), `cpython_build`, `cpython_compiler` (Clang 17.0.6), `cpython_version_full`, `libc` (2.41), `openblas_config`, `openblas_runtime_corename` (**Haswell**) | **NO**. SkylakeX needs AVX-512, so the kernel cannot be selected or forced on this CPU. |
| AWS (Xeon 8488C, `level4/.venv`) | inline read of the same fields | **2**: `cpython_build` (`Aug 31 2026 10:18:26` vs committed `Jul 15 2026 23:46:41`) and `cpython_version_full`. Matching: corename SkylakeX, openblas config, all 4 bound library sha256s, glibc 2.39, numpy 2.5.2, flint 0.9.0, compiler GCC 13.3.0 | **NO as frozen.** The CPython binary was rebuilt after the Aux4 commit (consistent with the recorded unattended-upgrade history), and strict `compare` refuses. The host is also fully occupied by the live PS1 campaign on 16 physical cores. |

Interpretation, with no ruling made: the arithmetic-relevant bindings (BLAS kernel and backend library bytes) match on AWS, and only the interpreter build stamp differs. Whether a patched CPython rebuild of the same 3.12.3 invalidates the producer identity is a **governance decision**. The frozen rule says it does. Options are a successor runtime contract re-bound on a named host, or restoring the committed interpreter build. Either way the rerun must be homogeneous on **one** bound contract, and the 2 existing cells must be re-produced under it if the contract changes. Vultr is excluded by the kernel alone.

`CUSUM_HOST_BINDING_READY = NO`

## Cost cap

| record | cap | scope |
|---|---|---|
| `p5y_k1_successor_optimized/CHECKPOINT_S.md` §6 | `SUCCESSOR_K1_HARD_CAP = 1126` | the **complete** K1 campaign (SR 387 + CUSUM 126 CPU-h basis) |
| PS1 protocol `immutable_predecessors.historical_caps` | "1,126 and 4,500 CPU-h caps remain immutable history; superseded for PS1 only" | — |
| PS1 authorization | 6,600 CPU-h | **PS1 (SR) only** |
| Aux4 RESULTS / audit | `COST_CAP = NOT_ESTABLISHED`; projection 205.6 CPU-h (2,270 CPU-s/cell × 326, 4 workers on 4 physical cores, Aux4 host) | CUSUM contribution only |

There is no record that establishes a cap governing the CUSUM rerun. The 1,126 cap was scoped to a K1 campaign whose SR half now runs under its own 6,600 cap, so it cannot be applied to CUSUM without a ruling. The 205.6 CPU-h projection was measured on the Aux4 host, and its transfer to a re-bound host is unqualified.

`CUSUM_COST_CAP_READY = NO`: requires a pre-result CUSUM cap record, plus cost requalification on the bound host if the runtime contract changes.
