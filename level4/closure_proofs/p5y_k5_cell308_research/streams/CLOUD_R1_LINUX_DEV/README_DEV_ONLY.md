# Stream CLOUD_R1_LINUX_DEV — development-only Linux platform layer (Cloud route r1)

**Status: DEV_ONLY · UNREVIEWED by any accepted process · NOT FROZEN · NOT A CAMPAIGN NAMESPACE.**
Nothing here may be used for a designated series, a derivation, an apply, a freeze, an official qualification, a
grant or a target step. The historical candidate (`142d97a9`) neither imports nor is changed by anything here.

Authority: owner instruction of 2026-10-14 (`governance/new_host_route_cloud_r1/USER_AUTHORIZATION_20261014.md`):
target-free feasibility investigation, development-only implementation and isolated testing.

## Contents

| file | what |
|---|---|
| `lx_platform.py` | Linux counterparts of the `mbs308_host` / driver host facilities: boot id, process identity (R2 / N-2 semantics), suspend / pause interval assessment, power and thermal readers, RAW memory and cgroup readers, windowed CPU exclusivity, update controls, `systemd` launch check, durable atomic write, Linux platform pins, and a PROPOSED preflight gate set. Every rule quantity without a Linux identity returns `OPEN_DECISION`; every failed reading returns `UNKNOWN`; neither ever passes. |
| `lx_inventory.py` | Read-only host inventory (produced `governance/new_host_route_cloud_r1/CLOUD_HOST_INVENTORY_R2_20261014.json`). |
| `lx_portmap.py` | Read-only scan of the candidate's macOS dependencies via `git show` (produced `results/PORT_MAP_142D97A9.json`). |
| `tests/test_lx_platform.py` | 44 isolated tests: synthetic `/proc` and `/sys` trees, `sleep` children, temporary files, crash injection by SIGKILL at each durable-write stage, real detachment of a new-session grandchild. |
| `tests/run_mutants.py` | 20 mutants, each weakening one fail-closed property; the unchanged suite must kill all of them. |
| `results/TEST_RUN.json`, `results/MUTANTS_RUN.json` | the recorded runs (44/44 OK; 20/20 killed). |

## Run

```
cd level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV
python3 -m unittest discover -s tests -v
python3 tests/run_mutants.py results/MUTANTS_RUN.json
```

Stdlib only; tested on CPython 3.11.17, 3.12.3 and 3.13.16 on the 2026-10-14 Cloud host.

## What the tests do NOT show

* Survival of the host's own death or of a VM reclaim (no in-guest test can).
* Disk durability across power loss or VM reclaim (SIGKILL is not a power loss).
* That any proposed Linux reading has the macOS rule's meaning — those are the open decisions D-* of
  `governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1.md` §4.
* Anything about the science, a cell, a drift or a target value: none is touched.
