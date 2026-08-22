# Track 3A/3B resume state

## PROGRESS CAPSULE — #3

| Field | Value |
|---|---|
| Step | Protocol/source freeze complete; confirmatory replication next |
| Gate | Fresh numerical work authorized by immutable protocol only |
| Protocol frozen? | YES — `0983fb483219a5eb593652fbb1596b73193dc12edf8aa7914c2e3e143750b9aa` |
| Historical Track 3 preserved? | YES |
| Variance diagnosis | COMPLETE — sampling variance amplified by heavy-tailed stopped gain |
| Pilot sizing | NOT USED — fixed historical-replay sizing selected |
| Replication 1 | NOT STARTED |
| Replication 2 | NOT STARTED |
| Numerical gate | NOT EVALUATED |
| Lean | NOT AUTHORIZED |
| Axiom audit | NOT STARTED |
| Tests | New pre-outcome 12/12; historical Track-3 37/37 |
| Historical artifacts modified? | NO |
| Git | Frozen checkpoint pending commit/push |
| Remaining | Run/resume two frozen confirmatory replications; evaluate one numerical gate |

Exact next command:

```bash
PYTHONDONTWRITEBYTECODE=1 level4/.venv/bin/python \
  level4/closure_proofs/location_family_track3ab/numerics/run_confirmatory.py
```

The runner validates existing checkpoints and skips them.  Do not edit
`PROTOCOL.md` or any file listed in `results/source_manifest.json`.
