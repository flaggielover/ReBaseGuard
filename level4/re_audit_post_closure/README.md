# Global Level-4 re-audit after scoped closure proofs

This isolated namespace derives the current Level-4 status without changing
Stage F. Historical Stage F remains `LEVEL-4-PARTIAL`;
this namespace answers the later question using the evidence boundary after
Tracks 1B, 2, and 3A/3B.

`requirements.json` is the sole status source. It contains exactly the 18
requirements reconstructed by Stage F. `src/generate_audit.py` derives the
current row statuses, counts, blocker lists, verdict JSON, and mirrored
reports. Do not edit generated status artifacts independently.

Current derived result:

```text
12 PASS
3 PARTIAL / NEGATIVE
2 FAIL
1 OPEN
LEVEL-4-PARTIAL
```

Mandatory fail/open blockers are the D4 phase map, semi-real external
validation, and novelty verification. The first two require scientific work;
the third is a documentation/provenance gap.

Reproduce with:

```bash
bash level4/re_audit_post_closure/reproduce.sh
```

The reproducer runs verification only. It launches no scientific campaign.
