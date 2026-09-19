# evidence/dev — pre-freeze development artifacts (NOT evidence for the freeze)

- `MANUFACTURED_DEV.json`: manufactured suite dev run (48 fixtures, 20/20 mutants); the frozen qualification re-runs it.
- `QUALIFICATION_REHEARSAL.json`: full dress rehearsal S00–S09 (QUALIFIED) on the vultr dev clone at dev-only commit
  02d6a93a = code of de94e8b3 + a dev protocol (sha 30922c24…). Never published. Superseded by the frozen qualification.
- `TC_PROTOCOL_DRAFT.json`: an r1-era draft protocol (still lists `G_at_a`); SUPERSEDED, kept only for the record.
- `QUALIFICATION_REHEARSAL_R3.json` (if present): partial rehearsal after the r3 fixes (S00–S05, S07, S08; S06 unchanged).
No real TC value (no order-3 candidate of F at any address) was computed in any of these.
