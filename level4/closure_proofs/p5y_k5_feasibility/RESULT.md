# P5Y K5 feasibility — result

Status: **feasibility only. No R''' campaign, no oracle execution, no closure claim.**

| Field | Value |
|---|---|
| `K5_GLOBAL_BRIDGE_THEOREM` | **PASS** — Theorem K5-B (`K5_GLOBAL_BRIDGE.md`): K1 R, R', R'' enclosures plus a certified per-cell lower bound on R''' imply H3a on (0,2] whenever the exact recurrences certify a sign. The theorem is *sufficient, not complete*: a failed recurrence proves nothing against H3a. |
| `K5_FEASIBILITY_ORACLE_FROZEN` | **YES** — `config/K5_FEASIBILITY_ORACLE.json`, FROZEN_PRE_RESULT. Probes are SR {0,207,294} and CUSUM {0,221,309}, with m ∈ {1,2,3,5} at 256 bits. The predeclared PASS/FAIL rules are Q1 enclosable, Q2 near-zero SR sign (STOP on failure) and Q3 sign determinacy at cell 0; Q4 cost is report-only. Nothing expands. |
| `K5_ORACLE_EXECUTED` | **NO** — the frozen `execution_precondition` is not met. No *certified* order-3 producer exists: the SR aux3 line stopped at Phase 4, and CUSUM Aux4/Aux5 carry order-3 *auxiliary node bounds* only, with no certified `F_r:k3` obligation. Running the probes would first require a separately governed order-3 producer. |
| `K5_FULL_CAMPAIGN_AUTHORIZED` | **NO** |

`K4` stays locked (`WAITING_FOR_COMPLETE_K1_INPUTS`). Nothing here consumes, or is consumed by, the frozen K4 checkpoint.

Independence: the theorem and the oracle were written by the same agent session that wrote the K2/K3 packet. A countersignature from an independent reviewer is recommended before K5-B is cited as adjudicated.
