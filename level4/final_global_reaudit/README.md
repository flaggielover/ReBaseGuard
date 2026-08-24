# Final global Level-4 re-audit

This isolated terminal audit derives the current global Level-4 status from
the protected historical record and authorized later closure campaigns. It
performs no new science and rewrites no historical verdict.

The canonical source is `requirements.json`. Generated status artifacts must
not be edited independently. Reproduce offline with:

```bash
bash level4/final_global_reaudit/reproduce.sh
```

Temporal verdicts are separate facts:

- historical Stage F: `LEVEL-4-PARTIAL`;
- previous post-closure re-audit: `LEVEL-4-PARTIAL`;
- current final verdict: mechanically generated in
  `results/final_decision.json`.
