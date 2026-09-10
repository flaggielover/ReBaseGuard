# Production result namespace — EMPTY AT FREEZE

`GENUINE_SR_PRODUCTION_CELLS = 0`.

This directory is the **only** place a genuine, result-bearing SR production
record may be written:

```
production/PRODUCTION_LEDGER.json    the global budget ledger for the real campaign
production/cells/NNNN.json           one sealed record per genuine cell
```

Nothing here has executed. At the freeze commit this directory contains this
README and nothing else, which is the checkable pre-result property: assert
against `git ls-tree <tag> -- production/`, never against the working tree.

Synthetic and control artifacts — including all Phase-8 evidence — live under
`evidence/`, `diagnostics/` and `phase8/` and are **structurally** refused here:
`production_launcher.gate_production_result_path` refuses any write outside this
directory, `gate_no_evidence_collision` refuses any write over `evidence/`, and
`production_provenance.verify` refuses any record that does not carry genuine
provenance bound to this campaign's production authorization.
