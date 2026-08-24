# D4 phase-map closure campaign

This isolated campaign addresses only Level-4 requirement `L4R-11`: the
Stage-D `m-rho` phase map. It uses the closed Track-1B derivative theorem for
the frozen symmetric two-sided Gaussian CUSUM (`k=1/2`, `h=5`) under the
Stage-D convention-A truncated stopped window.

The primary artifact is a theorem-supported map of **local deterministic
reference-map stability**. It is not an operational phase-transition map and
does not revise Stage D, Stage F, or the post-closure global re-audit.

Execution order:

1. `DEFINITION_AUDIT.md`
2. `THEOREM_BRIDGE.md`
3. frozen `PROTOCOL.md`
4. `results/gamma_grid_checkpoint.json`
5. `results/phase_map.json`
6. `results/direct_validation_checkpoint.json`
7. `results/operational_overlay_checkpoint.json`
8. reports, adversarial checks, repository verification, and scoped decision

The eventual one-command replay entry point is:

```bash
bash level4/closure_proofs/d4_phase_map/reproduce.sh
```

Historical decisions remain authoritative in their own namespaces. In
particular, historical D2.3 remains `FAILED`, D2.5 remains `MATHEMATICAL, NOT
OPERATIONAL`, Track 1A remains `MGT1-TRACK1A-FAILED`, Stage F remains
`LEVEL-4-PARTIAL`, and the current post-closure global verdict remains
`LEVEL-4-PARTIAL` unless a separate future global re-audit says otherwise.
