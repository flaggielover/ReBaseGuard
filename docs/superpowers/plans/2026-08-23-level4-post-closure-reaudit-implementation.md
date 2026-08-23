# Level-4 post-closure re-audit implementation plan

1. Freeze the approved 18-row requirement source and historical hash manifest.
2. Implement one generator for the decision JSON and all mirrored reports.
3. Implement R1--R18 as a deterministic evaluator and 18 pytest cases.
4. Add a byte-stable reproduction entry point and Level-4 verifier integration.
5. Generate artifacts and confirm the approved 12/3/2/1 derivation.
6. Run the isolated suite, adversarial evaluator, both full verifiers, and the
   re-audit reproducer.
7. Recheck Stage F hashes, inspect the exact diff, commit once, confirm a clean
   tree, and fast-forward push `main`.
