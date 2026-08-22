# Track 3A/3B resume state

## PROGRESS CAPSULE — #6

| Field | Value |
|---|---|
| Step | Final packaging complete; full reproduction next |
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
| Tests | Final focused suite pending, target 29 |
| Historical artifacts modified? | NO |
| Git | Lean checkpoint `cace80b` pushed; final checkpoint pending |
| Remaining | Run complete reproducer, confirm 929/929 and clean tree, commit/push closure |

Exact next command:

```bash
bash level4/closure_proofs/location_family_track3ab/reproduce.sh
```

Do not edit `PROTOCOL.md` or any file listed in
`results/source_manifest.json`.
