# P5Y K1 -- SR qualification lane (`p5y_k1_sr_qualification`)

Isolated SR implementation/qualification namespace, developed in PARALLEL with
the running CUSUM Aux4 326-cell full-cover certification campaign and designed
so that it cannot touch it.

```text
branch     p5y-k1-sr-parallel
worktree   /home/ubuntu/work/ReBaseGuard-sr-parallel   (separate from the running one)
based on   f0954a9db09d22ad44151afdb557f823fe6eb393
status     SR_REFINEMENT_ARCHITECTURE_PARTIAL -- heavy numerics deferred
```

## Contents

| path | what |
|---|---|
| `SR_DERIVATION.md` | the raw-variable derivation, before any code |
| `SR_NSTEP_RESOLVENT.md` | n-step resolvent: positivity, survival, geometric decomposition |
| `SR_RESOLVENT_GOVERNANCE.md` | global vs local C, decided from frozen artifacts |
| `SR_REFINEMENT_DESIGN.md` | why refinement is mandatory, and the order-3 assessment |
| `SR_MIDPOINT_REFINEMENT.md` | midpoint derivation, contraction proof, order-3 adjudication |
| `config/excluded_routes.json` | machine-readable historical route exclusions (Phase 2) |
| `config/sr_dag.json` | the complete SR object DAG, audited (Phase 3) |
| `code/sr_dag.py` | DAG builder + structural audit |
| `code/sr_sources.py` | closed-form `rho_1`, `rho_2` and e-derivatives |
| `code/sr_operators.py` | exact operator norms and the `K'`, `K''`, `K_z'` identities |
| `code/sr_propagate.py` | h/S/W chains, F/D/H resolvent, all-m assembly, `M_R2` |
| `code/sr_nstep.py` | `ResolventCertificate`, frozen `C_upper`, interval-DP certifier |
| `code/sr_survival_explore.py` | EXPLORATORY float survival DP (not a certificate) |
| `code/sr_universe.py` | the exact 8,849-obligation SR universe, sharding, resume |
| `code/sr_refine.py` | `SRRefinedCellValues`, the monotone whole-cell refinement |
| `code/sr_patch.py` | live-patch identity, work mapping, candidate determinism |
| `code/sr_width.py` | exact additive attribution of whole-cell width |
| `code/sr_provenance.py` | execution-derived TCB, runtime binding, scientific hash, final gate |
| `code/sr_cost.py` | honest cost instrumentation (no cap claim) |
| `code/sr_pilot.py` | representative pilot runner -- PREPARED, NOT RUN |
| `SR_INTEGRATION_PLAN.md` | how SR later joins the CUSUM Aux4 ledger |
| `RESULTS.md` | current status and the exact remaining blockers |

## Running the tests (safe while CUSUM runs)

```bash
OMP_NUM_THREADS=1 nice -n 19 python -m pytest tests/ -q     # 126 tests, ~1.6 s
```

## The CPU resource gate

`code/sr_pilot.py` refuses to start any numerical pilot while the CUSUM
`qualify_batch.sh` process group is alive. There is no `--force`.

```bash
python code/sr_pilot.py --pilot central --check-gate-only
```
