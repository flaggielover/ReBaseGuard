# Independent review r1 of theorem AD — disposition

Reviewer: fresh-context agent (independent by session, not by agent family or human), reviewing commit `b67cb900`.
Verdict: **PASS_WITH_NOTES** — no BLOCKING finding; points 1–12 SOUND or SOUND_WITH_NOTE (spectral/rank-one identity,
no hidden projection, nonnormality, normalization and Lemma Dv', eigenvalue simplicity not load-bearing, uniformity,
derivative terms, source errors, interval certification, tightening, consumption and monotonicity of K5-B, slot-1 reuse).
The full report is `REVIEW_R1.md`.

| finding | severity | disposition |
|---|---|---|
| M1 certifier (`taboo_certify.py`) not qualified | MAJOR | new successor gates S02 (float X-A: every certified bound dominates the float operator value at 5 drifts per cell), S03 (Arb probe: a wide block is refused; a point certificate used as a block certificate is accepted, so the e-linear term is load-bearing), S10 (X-B: independent Fraction recomputation of every registry field from the artifacts — payload sup norms from the dyadic numerators, whole-cell envelopes, tame taboo propagation, D_lo/D1/D2 composition, worst-block selection, ARL binding) |
| M2 `verify` does not check REGISTRY.json | MAJOR | `build_registry.py verify` re-assembles the registry from the artifacts in memory and requires byte identity, `certified` and `rule = r2` |
| premise citations name cusum_layer2/refine, not the Aux5 producer chain | MINOR | THEOREM_AD §5 "producer binding" and SPEC §1 cite `aux_propagate.cell_obligations`, `refine2`, `order2`; meaning unchanged; S09 checks the assembly semantics on every record (m = 1 excess ≤ 7.2e-9 relative in the dev run) |
| qualification padding (M07, M16 not mutants; Q2 range implied; closed_class is a harness check; Sclosed = S:0 in record_like; no wrong-radius / wrong-block mutants) | MINOR | M07/M16 moved to refusal/property checks; Q2 note; closed_class relabelled; record_like now distinguishes Sclosed (true r = 0 source) from S:0 (unused) with new mutant M17; new mutants M18 (over-shrink with a too-large recorded radius) and M19 (midpoint constants used for the whole cell); 17/17 detected |
| docstring claims an Arb proof of κ₁, κ₂ that did not exist | MINOR | S11 proves both rational bounds in Arb; docstring points to S11 |
| B(X) should be bounded Borel functions | MINOR | fixed in THEOREM_AD and OPERATOR_AUDIT; audit §4 table marked INFORMATIONAL |
| committed qualification bound to an older consumer sha | MINOR | the frozen version is re-qualified by S04 at the freeze head |
