# Proof Track 1B — correlation-aware decomposition and Lean completion

This isolated campaign audits the Track 1A uncertainty model, executes a
fresh batch-level paired and independent decomposition replication, and—only
if the frozen numerical gate closes—formalizes the stable `m>1` theorem spine
in Lean.

Historical status is immutable:

- Stage-D D2.3 remains `FAILED`;
- Proof Track 1 remains `MGT1-THEOREM-PARTIAL`;
- Proof Track 1A remains `MGT1-TRACK1A-FAILED`, including its
  `m=20` decomposition result `3.130 > 3`;
- Stage F remains `LEVEL-4-PARTIAL` unless a future global re-audit says
  otherwise.

The pre-data statistical reconstruction is in `COVARIANCE_AUDIT.md`. The
confirmatory design is frozen in `PROTOCOL.md` before any Track 1B outcome is
generated.

## Current evidence

- numerical gate: `PASS` — `NUMERICAL GATE CLOSED — LEAN AUTHORIZED`;
- paired pathwise and batch decomposition: `PASS`;
- independent-route Hotelling cross-check: `PASS`;
- `m=1` structural control: `PASS`;
- Lean stable spine: compiled;
- axiom audit: only `propext`, `Classical.choice`, and `Quot.sound`;
- concrete frozen-CUSUM analytic instantiation: human proof, not discharged
  end to end in Lean;
- final Track 1B verdict: pending the authoritative repository verifier.

Start with `REPLICATION_REPORT.md`, `THEOREM.md`, and
`LEAN_CORRESPONDENCE.md`. After the closure checkpoint is committed, run:

```bash
bash level4/closure_proofs/m_gt_1_track1b/reproduce.sh
```
