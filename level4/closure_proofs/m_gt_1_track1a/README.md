# Proof Track 1A — Stage-A / Stage-D distinction and Lean completion

This isolated campaign tested whether the previously human-proved Stage-D
`m>1` derivative theorem can close after an independently seeded distinction
replication and a Lean proof-spine formalization.

**Final decision:** `MGT1-TRACK1A-FAILED`.

The Stage-A/Stage-D distinction replicated, but the independently routed
decomposition comparison reached `3.130` combined SE at `m=20`, outside the
frozen three-SE pooled bound. The pathwise decomposition remained exact and
all per-replication comparisons were below four SE. The protocol required a
stop on any decomposition-gate failure, so Lean was not started.

The campaign does not modify the prior proof track or any historical Stage A,
Stage D, or Stage F result. In particular:

- historical Stage-D D2.3 remains `FAILED`;
- the previous proof-track decision remains `MGT1-THEOREM-PARTIAL`;
- the historical global result remains `LEVEL-4-PARTIAL`.

The protocol is frozen in `PROTOCOL.md` before Track 1A confirmatory data are
generated. The audit trail is in `AUDIT.md`, and live checkpoint state is in
`PROGRESS_CAPSULE.md`.

Final entry points are `REPLICATION_REPORT.md`, `THEOREM.md`,
`LEAN_CORRESPONDENCE.md`, and `../../reports/MGT1_TRACK1A_REPORT.md`.
