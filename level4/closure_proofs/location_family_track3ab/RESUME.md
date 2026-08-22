# Track 3A/3B resume state

## PROGRESS CAPSULE — #5

| Field | Value |
|---|---|
| Step | Track-3B Lean spine and axiom audit complete |
| Gate | `T3A-NUMERICAL-PASS` — `NUMERICAL GATE CLOSED — LEAN AUTHORIZED` |
| Protocol frozen? | YES — `0983fb483219a5eb593652fbb1596b73193dc12edf8aa7914c2e3e143750b9aa` |
| Historical Track 3 preserved? | YES |
| Variance diagnosis | COMPLETE — sampling variance amplified by heavy-tailed stopped gain |
| Pilot sizing | NOT USED — fixed historical-replay sizing selected |
| Replication 1 | PASS — relative `0.8620%`, `|z|=1.0114` |
| Replication 2 | PASS — relative `0.4894%`, `|z|=0.5876` |
| Numerical gate | PASS — pooled relative `0.1867%`, `|z|=0.3135` |
| Lean | COMPILED — conditional proof spine |
| Axiom audit | CLEAN — `propext`, `Classical.choice`, `Quot.sound` only |
| Tests | Focused post-Lean suite pending |
| Historical artifacts modified? | NO |
| Git | Numerical checkpoint `15fdd43` pushed; Lean checkpoint pending commit |
| Remaining | Run focused tests, preserve Lean checkpoint, then final reports/reproducer/full verification |

Exact next command:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTEST_ADDOPTS='-p no:cacheprovider' \
  level4/.venv/bin/python -m pytest \
  level4/closure_proofs/location_family_track3ab/tests -q
```

Do not edit `PROTOCOL.md` or any file listed in
`results/source_manifest.json`.
