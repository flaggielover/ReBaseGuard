# Stream CLOUD_R1_LINUX_DEV — development-only Linux platform layer (Cloud route r1), revision 2

**Status: DEV_ONLY · NOT ACCEPTED BY ANY GOVERNANCE REVIEW · NOT FROZEN · NOT A CAMPAIGN NAMESPACE.**
Nothing here may be used for a designated series, a derivation, an apply, a freeze, an official qualification, a
grant or a target step. The historical candidate (`142d97a9`) neither imports nor is changed by anything here.

Authority: owner instruction of 2026-10-14 (`governance/new_host_route_cloud_r1/USER_AUTHORIZATION_20261014.md`).

**History.** Revision 1 (`19b4e8b8`) was reviewed by the fresh review 59 (`reviews/REVIEW_CLOUD_R1_FEASIBILITY_
AMENDMENT_DEV.md`): **DEV_CODE: NOT_FAIL_CLOSED** — failed or absent readings could yield AC, PASS, a numeric memory
allowance or a false DEAD (a zombie leader with a live thread), the pins missed libm, and 0 of the reviewer's 10
mutants were killed. Revision 2 repairs every code finding (disposition: amendment r2 §10). The claim of revision 1's
README that "every failed reading returns UNKNOWN; neither ever passes" was false for revision 1; for revision 2 it is
the property the tests and mutants target, and the fresh delta review (`reviews/` brief 60) checks it.

## Contents

| file | what |
|---|---|
| `lx_platform.py` | Linux counterparts of the `mbs308_host` / driver host facilities (amendment r2 §3). A failed, absent or unrecognised reading is UNKNOWN; a rule quantity without a Linux identity is `OPEN_DECISION`; neither passes. A zombie is never proof of death. Pins cover every mapped shared object (libm, libc, loader), package versions and livepatch. Attestations must be committed, sha-bound, accepted and hardware-bound. |
| `lx_inventory.py` | Read-only host inventory; revision 2 compares with r1 after normalisation (`governance/new_host_route_cloud_r1/CLOUD_HOST_INVENTORY_R2B_20261014.json`). The earlier `CLOUD_HOST_INVENTORY_R2_20261014.json` was produced by revision 1 of both tools and is kept unchanged. |
| `lx_portmap.py` | Read-only scan of the candidate's macOS dependencies via `git show` (`results/PORT_MAP_142D97A9.json`). |
| `tests/test_lx_platform.py` | 60 isolated tests: synthetic `/proc` and `/sys` trees, child processes (incl. a zombie leader with a live thread, and a detached grandchild), temporary files and git repositories, SIGKILL crash injection, an fsync-order spy, and two constants pinned to the candidate's values via `git show`. |
| `tests/run_mutants.py` | 42 mutants (M01–M32 coordinator, R01–R10 from review 59); the unchanged suite must kill all of them. |
| `results/TEST_RUN.json`, `results/MUTANTS_RUN.json` | 60/60 OK on CPython 3.11.17, 3.12.3, 3.13.16; 42/42 killed. |

## Run

```
cd level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV
python3 -B -m unittest discover -s tests -v
python3 -B tests/run_mutants.py results/MUTANTS_RUN.json
```

## What the tests do NOT show

* Survival of the host's death or of a VM reclaim; disk durability across power loss (SIGKILL is not a power loss).
* That any proposed Linux reading has the macOS rule's meaning — the open decisions D-* of amendment r2 §4.
* Hidden cgroup ancestors (no reader can see above a cgroup-namespace root; H6 is an attestation).
* Anything about the science, a cell, a drift or a target value: none is touched.
