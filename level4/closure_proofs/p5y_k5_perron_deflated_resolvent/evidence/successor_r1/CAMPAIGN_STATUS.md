# K5_PERRON_DEFLATION_FEASIBILITY — campaign status (2026-09-19)

```text
START_FRONTIER                  = 5a8c194d
FREEZE_COMMIT                   = 730d6e83  (SUCCESSOR_PROTOCOL.json sha256 ef6c1d14…, 42 pins)
CERTIFIED_OPERATOR_REGISTRY     = evidence/registry_r1/REGISTRY.json sha256 1b7f5da7…  (operator only)
FEASIBILITY_GATE (frozen rule)  = USEFUL (certified constants dominated by the forecast model at scale 1.6 on every front cell)
INDEPENDENT_REVIEW              = r1 PASS_WITH_NOTES, r2 PASS_WITH_NOTES, r3 NOT_READY (B1), r4 READY_TO_FREEZE after one fix (applied)
PERRON_DEFLATION_GATE           = FEASIBLE_READY_FOR_SUCCESSOR   (end state PERRON_DEFLATED_SUCCESSOR_FROZEN)
K5_STATUS                       = PARTIAL (unchanged; no successor result sealed yet)
```

## Pending (blocked by a host outage caused by the producer)

On 2026-09-19 ≈ 08:50 UTC a stray `rm -v -f /dev/null` in one of the producer's remote commands deleted `/dev/null` on
rebaseguard-vultr-02; sshd now refuses every session. Nothing was running on the host. Restore from the Vultr console
(`rm -f /dev/null && mknod -m 666 /dev/null c 1 3`) or reboot. The K1 export tree (the records the successor reads) and the
pinned certifier runtime (python-flint 0.9.0) exist only there.

After restoration, in order (full-history clones only):
1. qualification S00–S12 on a clean clone at 730d6e83 (`code/qualify_successor.py run --protocol-sha256 ef6c1d14…`),
   commit `evidence/successor_r1/QUALIFICATION_RESULT.json` and its evidence;
2. two `consume` runs (byte-identical, outputs outside the namespace), then the seal commit copying the result and ledger into
   `evidence/successor_r1/`;
3. independent adjudication (`review/ADJUDICATION_BRIEF.md`), then the coverage map r3 (`code/coverage_map_r3.py`).

Guaranteed by the certified dominance (lower bound on what the sealed consumption will close): front cells 45–132 (m = 1),
53–144 (m = 2), 53–145 (m = 3), 55–148 (m = 5); expected (float-constant forecast at s ≈ 1.3): 39–132, 46–144, 47–145, 49–148.
The lower front (11 to ≈ 38–54) and the m = 5 tail 305–309 stay open under this successor.
