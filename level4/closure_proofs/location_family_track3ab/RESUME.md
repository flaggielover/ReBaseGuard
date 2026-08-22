# Track 3A/3B resume state

## PROGRESS CAPSULE — #4

| Field | Value |
|---|---|
| Step | Track-3A numerical gate passed; preserve checkpoint before Lean |
| Gate | `T3A-NUMERICAL-PASS` — `NUMERICAL GATE CLOSED — LEAN AUTHORIZED` |
| Protocol frozen? | YES — `0983fb483219a5eb593652fbb1596b73193dc12edf8aa7914c2e3e143750b9aa` |
| Historical Track 3 preserved? | YES |
| Variance diagnosis | COMPLETE — sampling variance amplified by heavy-tailed stopped gain |
| Pilot sizing | NOT USED — fixed historical-replay sizing selected |
| Replication 1 | PASS — relative `0.8620%`, `|z|=1.0114` |
| Replication 2 | PASS — relative `0.4894%`, `|z|=0.5876` |
| Numerical gate | PASS — pooled relative `0.1867%`, `|z|=0.3135` |
| Lean | AUTHORIZED; NOT STARTED |
| Axiom audit | NOT STARTED |
| Tests | Numerical audit pending, then focused suite |
| Historical artifacts modified? | NO |
| Git | Frozen protocol commit `96bc371` pushed; numerical checkpoint pending commit |
| Remaining | Audit/push numerical PASS, then implement conditional Lean spine |

Exact next command:

```bash
PYTHONDONTWRITEBYTECODE=1 level4/.venv/bin/python \
  level4/closure_proofs/location_family_track3ab/numerics/audit_numerical.py
```

Do not edit `PROTOCOL.md` or any file listed in
`results/source_manifest.json`.
