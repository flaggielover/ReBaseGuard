# Stream CLOUD_R1_LINUX_DEV — development-only Linux platform layer (Cloud route r1), revision 4

**Status: DEV_ONLY · NOT ACCEPTED BY ANY GOVERNANCE REVIEW · NOT FROZEN · NOT A CAMPAIGN NAMESPACE.**
Nothing here may be used for a designated series, a derivation, an apply, a freeze, an official qualification, a
grant or a target step. The historical candidate (`142d97a9`) neither imports nor is changed by anything here.

Authority: owner instruction of 2026-10-14 (`governance/new_host_route_cloud_r1/USER_AUTHORIZATION_20261014.md`).

**History.** Revision 1 (`19b4e8b8`) was reviewed by the fresh review 59 (`reviews/REVIEW_CLOUD_R1_FEASIBILITY_
AMENDMENT_DEV.md`): **DEV_CODE: NOT_FAIL_CLOSED** — failed or absent readings could yield AC, PASS, a numeric memory
allowance or a false DEAD (a zombie leader with a live thread), the pins missed libm, and 0 of the reviewer's 10
mutants were killed. Revision 2 attempted to repair the code findings (disposition: amendment r2 §10); review 60 found remaining defects. The claim of revision 1's
README that "every failed reading returns UNKNOWN; neither ever passes" was false for revision 1; for revision 2 it is
the property the tests and mutants target. The fresh delta review 60 (`reviews/REVIEW_CLOUD_R1_DELTA_R2.md`) found
it false again for revision 2 (**DEV_CODE_R2: NOT_FAIL_CLOSED**: an unrecognised battery status read as AC, a truthy
root attestation giving a numeric allowance, a self-asserted attestation passing two gates, a nested PID namespace read
as a complete /proc view, 9 of its 12 mutants surviving). Revision 3 repairs N1–N8 and N11–N13; per review 60's
condition C1 no amendment row may cite this code as its implementation until a fresh delta review of revision 3.

## Revision 4 continuation

The independent Codex takeover of brief 61 rejected revision 3 (`reviews/REVIEW_CLOUD_R1_DELTA_R3_CODEX.md`).
Revision 4 checks actual parent identity before a child exemption, validates process and interval record schemas,
refuses invalid CPU arithmetic and ambiguous /proc views, and corroborates the supplied launch record with a fresh
live supervisor observation. Explicit observer/checker/reading injection is for synthetic testing; an operational
wrapper must independently pin and restrict those seams. Raw memory helpers still accept a strict boolean and do
not prove its attestation provenance; the reviewed wrapper and fixed science-import list remain conditions.

Native Linux validation and fresh independent review of these repairs are pending. Historical evidence does not
establish the current code's behavior. Neither this continuation nor a successful test authorizes an official step.

## Contents

| file | what |
|---|---|
| `lx_platform.py` | Linux counterparts of the `mbs308_host` / driver host facilities (amendment r3 §3). Target property: a failed, absent or unrecognised reading is UNKNOWN; a rule quantity without a Linux identity, or a gate whose D-* decision is open, is `OPEN_DECISION`; neither passes. A zombie is never proof of death. Pins must contain libm, libc and the loader, plus package versions and livepatch. Attestation facts are read from a committed file accepted by a committed review line naming its sha256. |
| `lx_inventory.py` | Read-only host inventory; revision 2 compares with r1 after normalisation (`governance/new_host_route_cloud_r1/CLOUD_HOST_INVENTORY_R2B_20261014.json`). The earlier `CLOUD_HOST_INVENTORY_R2_20261014.json` was produced by revision 1 of both tools and is kept unchanged. |
| `lx_portmap.py` | Read-only scan of the candidate's macOS dependencies via `git show` (`results/PORT_MAP_142D97A9.json`). |
| `tests/test_lx_platform.py` | 103 isolated tests: synthetic `/proc` and `/sys` trees, child processes (incl. a zombie leader with a live thread, and a detached grandchild), temporary files and git repositories, SIGKILL crash injection, an fsync-order spy, and two constants pinned to the candidate's values via `git show`. |
| `tests/run_mutants.py` | 73 mutants (M01–M32 coordinator, R01–R10 from review 59, X01–X09 from review 60, N01–N14 weakening the revision-3 repairs; Y01–Y03 from review61 and P01–P05 for the takeover repairs); the passing unmodified suite must detect their intended weakening; full failure traces are preserved and execution errors are never automatic kills. |
| `results/TEST_RUN.json`, `results/MUTANTS_RUN.json` | historical revision-3 records, preserved unchanged. Revision-4 evidence is filed separately and must match current input hashes. |

## Run

```
cd level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV
python3 -B -m unittest discover -s tests -v
python3 -B tests/run_mutants.py /tmp/platform-mutants-current.json
```

## What the tests do NOT show

* Survival of the host's death or of a VM reclaim; disk durability across power loss (SIGKILL is not a power loss).
* That any proposed Linux reading has the macOS rule's meaning — the open decisions D-* of amendment r4 §4.
* Hidden cgroup ancestors (no reader can see above a cgroup-namespace root; H6 is an attestation).
* Anything about the science, a cell, a drift or a target value: none is touched.
