# PS1 production result namespace — EMPTY AT FREEZE

`GENUINE_PS1_SR_PRODUCTION_CELLS = 0`.

This directory is the **only** place a genuine, result-bearing PS1 SR production
record may be written:

```
production/PRODUCTION_LEDGER.json    the global budget ledger for the real campaign
production/cells/NNNN.json           one sealed record per genuine cell
```

Nothing here has executed. At the freeze commit this directory contains this
README and nothing else, which is the checkable pre-result property: assert
against `git ls-tree p5y-k1-sr-ps1-production-authorized-preresult -- production/`,
never against the working tree.

The historical SR production ledger of
`p5y_k1_sr_production_authorized_successor` is IMMUTABLE HISTORY, SUPERSEDED FOR
PS1 ONLY and **not inherited**: PS1 opens a fresh ledger here.

Synthetic and control artifacts are **structurally** refused here:
`production_launcher.gate_production_result_path` refuses any write outside this
directory, `gate_no_evidence_collision` refuses any write over `evidence/`, and
`production_provenance.verify` refuses any record that does not carry genuine
provenance bound to this campaign's production authorization.
