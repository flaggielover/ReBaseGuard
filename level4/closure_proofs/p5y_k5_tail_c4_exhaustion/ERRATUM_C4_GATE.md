# Erratum to the frozen C4 gate

`config/FEASIBILITY_GATES_C4.json` is frozen at commit `376950be`, sha256
`d5b5b385d5c123ccd5993116901797f1ef2b75054a56617dfd07e860d526a647`. It is **not amended**. Defects found after
the freeze are recorded here, as Campaign C3 recorded its own.

## E1 — the disclosed diagnostic is not the decision-relevant one

`prior_evidence_known_at_freeze.diagnostic_true_E_a_tau_at_midpoints` discloses `E_a[tau]` at each cell's
**midpoint**: 4.17430 at cell 308. Against the 4.375229 an exclusion needs, that reads as about 4.8 % of
headroom.

The quantity that actually decides whether cell 308 can ever be excluded is not the midpoint value but

    Lambda_308 = sup_{e in cell 308} E_a[tau](e) = E_a[tau](e_lo) ,

because `E_a[tau]` decreases in `e`. Interpolating the two committed midpoint diagnostics across the shared
endpoint gives `Lambda_308 ≈ 4.315`, i.e. about **1.5 %** below the threshold, not 4.8 %. The pre-result
reviewer's own independent Monte-Carlo (2,000,000 paths of the chain as identified in `c4_model_identity.py`) puts
it at **4.31108 ± 0.00102**, a gap of 0.0641 to the threshold — about 63 standard errors.

`phase_1/C4_TARGET_RECONSTRUCTION.md` §5 already used the endpoint figure ("about 4.315"). The **gate**, which is
the frozen document a later reader will consult first, discloses only the midpoints. Anyone repeating the cell-308
claim should repeat it with the endpoint number.

Nothing computational changes: no gate class, test, threshold or permitted conclusion consumes the diagnostics,
and the certificate does not read them. Found by the pre-result review, OTHER FINDINGS 8.

## E2 — how the freeze should be described

The gate was frozen **after** `c9b06abf`, which already contained `evidence/phase3/C4_ROUTES.json` with every
cell's bound, every `Gamma` at the bound and every `excludes_cell` flag. The campaign instruction required Phase 3
to report each route's resulting bound and slack, so this ordering was mandated, not chosen — but the consequence
must be stated plainly rather than left for a reader to infer:

**the freeze has essentially no prospective evidential value.** With 306 and 307 outside the count, 308 already
known to be out of reach and `Gamma = +0.004661` at 309 already computed, `PASS` was unattainable and
`FAIL_INCONCLUSIVE` was already ruled out. `PARTIAL` was the only reachable class, and the gate names `PARTIAL` as
the expected class.

What the freeze *does* do, and what it should be described as doing, is **bind what the result is allowed to
mean** before the result is written down: the exclusion test, the domain requirement, the admissible family, the
permitted conclusions and the refusals are all fixed and mechanically enforceable, and `c4_certificate.py` refuses
to run against any other gate. No report of C4 may describe the freeze as a pre-registration of what the result
would be. Raised by the pre-result review, item H and note (j).

## E3 — the carve-out for cells whose blocker is not A0

`classification.cells_whose_blocker_is_not_A0` removes exactly cells 306 and 307 from the PASS/PARTIAL count, and
those are exactly the cells that would otherwise have counted against the campaign. The reviewer examined this as
a candidate for gate-fitting and concluded it is **logically forced rather than fitted**: if
`Gamma(A0_certified, 0, 0) < 0` then `A0` is not what keeps the cell open, so no floor under `A0` can bear on it,
and a gate that counted such a cell as a failure would be measuring the wrong thing. It is recorded here because
the coincidence is real and a later reader is entitled to see it flagged rather than discover it.
