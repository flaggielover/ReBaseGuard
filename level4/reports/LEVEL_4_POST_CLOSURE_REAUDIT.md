# ReBaseGuard Level 4 — post-closure global re-audit

## A. Current global verdict

**`LEVEL-4-PARTIAL`**

## B. Historical Stage-F verdict

**`LEVEL-4-PARTIAL`**, preserved unchanged.

## C. Closed since Stage F

The scoped `m>1` derivative theorem, SR derivative theorem, and regular
location-family stopped-score theorem now pass their original requirement
rows through Tracks 1B, 2, and 3A/3B respectively.

## D–E. Remaining mandatory blockers

- m-rho phase map (D4) — SCIENTIFIC
- Semi-real external validation — SCIENTIFIC
- Prior-art and novelty verification — DOCUMENTATION_PROVENANCE

The first two are scientific blockers. Novelty verification is a
documentation/provenance blocker.

## F. Mechanical decision

The generator reads exactly 18 rows and derives **12 pass,
3 partial/negative, 2 fail,
and 1 open**. There are 3
mandatory fail/open rows and 2
mandatory partial/negative rows, so the fallback taxonomy returns
`LEVEL-4-PARTIAL`.

## G–J. Scientific extrema

- Strongest rigorous result: Lean-checked stopped-likelihood differentiation spine, outward-rounded Gamma_CUSUM enclosure above two, and the certified deterministic-skeleton period-2 orbit.
- Strongest general theorem: For regular one-dimensional location families satisfying explicit stopped change-of-measure and domination hypotheses, F'_rho(0)=rho(1-Gamma_f) for matched raw-observation m=1 reuse.
- Strongest cross-detector result: CUSUM and the authoritative symmetric two-chart SR detector both satisfy the stopped-score derivative identity; SR Gamma above two remains confirmatory numerical evidence.
- Most important negative result: The Gamma_m crossing is mathematical, not operational: zero of four monitoring metrics peaked and all four were monotone in log m.

## K–L. External validity and SR Arb

The frozen three-stream semi-real campaign met H-E5 on zero of three tasks; no later external-validation campaign was performed. The rigorous SR local-instability
certificate remains open; only the derivative theorem is closed.

## M. Claim boundary

The safe claim is scoped to the named CUSUM and SR constructions and to regular
location families satisfying the stated analytic hypotheses. The work does
not establish arbitrary-detector coverage, arbitrary-distribution coverage,
deployment readiness, optimality, or universal safety.

## N. Publication-safe summary

ReBaseGuard has a rigorous CUSUM core, independently closed derivative theorems for the scoped m>1 CUSUM and symmetric SR settings, and a conditional regular-location-family stopped-score theorem; its global Level-4 status remains partial because mandatory phase-map, semi-real validation, and novelty-provenance requirements remain unmet.

## O. Resume-safe summary

- Historical Stage F stays `LEVEL-4-PARTIAL`; the current derived verdict is also `LEVEL-4-PARTIAL`.
- Three theorem requirements closed later; D4, Stage E external validation, and novelty provenance remain mandatory fail/open blockers.
- No new science was run; exact protected hashes and 947 distinct checks support this re-audit.

## P–Q. Verification and reproduction

Current distinct check count: **947 / 947**.

```bash
bash scripts/verify_level_1_3.sh
bash scripts/verify_level_4.sh
bash level4/closure_proofs/m_gt_1_track1b/reproduce.sh
bash level4/closure_proofs/sr_derivative/reproduce.sh
bash level4/closure_proofs/location_family_track3ab/reproduce.sh
bash level4/re_audit_post_closure/reproduce.sh
```

## Historical confirmation

No historical result was rewritten. No new scientific campaign was performed.
All historical failures and partial decisions remain visible and unchanged.
