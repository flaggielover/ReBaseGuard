# K1 successor production driver — pre-T2S

`P5Y_K1_SUCCESSOR_PRODUCTION_RUN = NO`. Nothing here has executed production.

```
k1prod/schema.py         work-unit identity, floor sharding, record schema, atomic writes
k1prod/kernel.py         per-unit scientific kernel + the honest coverage gap
k1prod/driver.py         phases A..F, resume, CPU cap, monitoring
k1prod/qualify.py        NON-result-bearing environment qualification
k1prod/smoke.py          synthetic scaling smoke (1/8/16/32/64)
k1prod/review_driver.py  independent review — the implementer does not self-certify
deploy/                  Debian 13 server package, 00..60
tests/test_driver.py     25 focused tests
```

## What is ready

Orchestration: 12,255 units, floor sharding exact at 1/8/16/32/64, atomic
per-record writes, resume that rejects corrupt lines and checkpoint/backend hash
mismatches, CPU cap read from the frozen checkpoint (1126 CPU-h) and checked
before each unit, worker ceiling 64 enforced, no scientific constant hard-coded.

**R and R' are persisted by design.** The frozen contract (parent
`CHECKPOINT.md` §23) says a record carries its fields *at minimum* — a floor,
not a ceiling — so this needs no amendment. Phase D emits them per cell.

## What is not ready

The per-unit scientific kernel covers **322 of 12,255 units (2.63%)** — only
`SR/F_0`, the object Task1R qualified. The other 18 object classes
(`h_j`, `S_r`, `F_r` for `r>=1`, `dF_r`, and all of CUSUM) have no production
implementation: the pre-existing `ra_certifier` certifies the *old g-variable*
system, which is a different formulation from the frozen raw-variable DAG.

The driver reports these as `NOT_IMPLEMENTED` — a state distinct from `FAILED`
and from `NOT_RUN` — and never counts them as coverage.

## Running it

```bash
# on the server, after provisioning
REPO_URL=... COMMIT=... bash deploy/10_checkout_and_verify.sh
bash deploy/20_python_env.sh
bash deploy/30_qualify.sh          # ENVIRONMENT_QUALIFICATION = PASS/FAIL
RUN_ID=k1-001 bash deploy/40_launch_production.sh
RUN_ID=k1-001 bash deploy/60_monitor.sh    # single-shot, no polling loop
```
