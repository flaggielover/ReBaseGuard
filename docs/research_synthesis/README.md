# ReBaseGuard research synthesis

## Synthesis verdict

ReBaseGuard is `LEVEL-4-CLOSED`: the terminal ledger contains **17 PASS, 1
PARTIAL, 0 FAIL, and 0 OPEN**, with **16/16 mandatory requirements passing**.
The one nonmandatory partial is L4R-13, non-Gaussian robustness. At that
terminal closure checkpoint, the separate rigorous SR local-instability Arb
certificate was an optional open rigor upgrade. These historical facts are
mechanically recorded in
`level4/final_level4_closure/results/final_decision.json` and summarized in
`level4/final_level4_closure/FINAL_REPORT.md`.

The later, additive post-Level-4 upgrade is now **`SR-GAMMA-CERTIFIED`** for the
authoritative symmetric two-chart SR detector. It does not change the terminal
Level-4 ledger or make a detector-independent claim.

## Central research question

What happens in repeated sequential monitoring when an alarm is selected by a
stopping time, observations that participated in that alarm are reused to
update the next reference, and the changed reference recursively alters the
distribution and stopping behavior of the next monitoring cycle?

The project isolates this **stopping-selected recursive re-baselining**
mechanism. It is not a generic drift-detection study.

## One-paragraph summary

ReBaseGuard studies feedback created when alarm-participating observations are
reused as the next monitoring baseline. For a frozen two-sided Gaussian CUSUM,
the local reference map satisfies a stopped-score derivative identity; a
Lean-checked differentiation spine and an outward-rounded Arb enclosure of
`Gamma_CUSUM` above two imply local repulsion at full reuse. A separate rigorous
numerical certificate establishes an attracting period-2 orbit of the
deterministic conditional-mean skeleton, not of the noisy stochastic chain.
The derivative theory extends to random finite reuse windows, symmetric
two-chart SR, and regular one-dimensional location families under explicit
hypotheses. The finite-window theorem yields an `m`-`rho` local-stability map and
a frozen uncertainty-aware P3 reuse rule. Semi-real tasks support the scoped
mechanism in three tasks against two required, while the pre-specified
operational-crossing study returns a first-class negative result: the
mathematical boundary had no detected operational transition under the frozen
protocol. Novelty remains the scoped N2 partial-overlap position.

## One-page version

The object of study is a repeated monitor whose reference is updated after each
alarm. If the update reuses observations from the alarmed path, the new
reference is not based on an ordinary sample: both the path length and the
terminal sample are selected by the stopping rule. Let `e` be the current
reference error, `tau` the alarm time, and `F` the conditional mean of the next
reference error. Repeating the procedure iterates this map with stochastic
noise.

For one reused observation, the frozen Gaussian CUSUM has
`F'_rho(0)=rho(1-Gamma_CUSUM)`, where
`Gamma_CUSUM=E_0[Z_tau T_tau]`. Lean checks the stopped-likelihood
differentiation spine, while Arb independently certifies
`Gamma_CUSUM in [3.9243482,27.8493821]`; together with the human model bridge,
this makes the zero fixed point locally repelling at full reuse. A later
interval certificate proves a unique nonzero root in
`[1.0287243,1.0447243]` and a period-2 multiplier in
`[0.10815,0.83253]` for the deterministic conditional-mean skeleton. These
numbers come from `rebaseguard-proof/proofs/certificate.json` and
`level4/stage_b/certificate/period2_certificate.json`.

For a reuse window of size `m`, the authoritative Stage-D/Track-1B convention
retains the ordinary alarm time and averages the last `min(m,tau)` residuals.
The corresponding theorem is
`F'_{rho,m}(0)=rho(1-GammaTilde_m)`. Its exact short-cycle correction prevents
this quantity from being silently identified with the earlier Stage-A
minimum-dwell convention. The derived boundary
`rho_c(m)=1/(GammaTilde_m-1)` when `GammaTilde_m>1` produces the D4
protocol-specific local-stability map. D4 brackets the full-reuse crossing at
`m in [70,72]`, with secondary interpolation `71.419386`; this is mathematical,
not operational (`level4/closure_proofs/d4_phase_map/results/decision.json`).

The method contribution is P3:
`rho_P3(m)=min(1,0.8*rho_c,L95(m))`. It uses the lower 95% boundary and a frozen
20% margin, producing reuse fractions `0.053642`, `0.245418`, `0.781994`, and
`1.000000` for `m=1,20,70,100`. Under its frozen Gaussian protocol it improved
reference MSE and false-alert burden in active regimes and was non-inferior to
fresh reference on the primary family. Historical C6 remains failed, P2 has
descriptive advantages at `m=70,100`, and P3 equals P1 at saturated `m=100`
(`level4/closure_proofs/l4r06_policy/results/scientific_findings.json`).

The extension stack is deliberately scoped. The symmetric two-chart SR
derivative theorem was closed and Lean-supported conditionally at Level 4. A
later optional Arb upgrade rigorously certified
`Gamma_SR in [5.800391799508442,28.781285803081492]`, with lower-endpoint margin
`3.800391799508442` above two, for that authoritative SR model. The
regular-location-family result gives
`F'_rho(0)=rho(1-Gamma_f)` under explicit stopped change-of-measure,
measurability, tail, integrability, and domination assumptions; concrete
infinite-process obligations remain human-proved. L4R-13 remains partial, so no
distribution-free or general non-Gaussian claim follows.

External validation is semi-real rather than production validation. Stage E
remains 0/3, V2 remains 1/3, and V3 is 2/2, giving three successful tasks
against two required; P2 safety is regime-dependent
(`level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md`).
The operational-crossing study used 20,000 replicates: 0/4 preselected metrics
peaked at the crossing and 4/4 were monotone in log `m`, so the positive
transition hypothesis was falsified under the frozen protocol
(`level4/closure_proofs/l4r12_operational_crossing/results/evidence_assessment.json`).

The novelty audit closes at N2, `PARTIAL-OVERLAP-FOUND-CLAIMS-NARROWED`: 36
frozen queries, 2,445 deduplicated candidate works inspected, 33 included, 0
DIRECT, and 9 HIGH-PARTIAL. Within the documented search scope, no work was
identified that combines the same alarm-stopped next-reference mechanism with
the reported derivative and stability results
(`level4/closure_proofs/novelty_verification/results/search_manifest.json` and
`level4/closure_proofs/novelty_verification/FINAL_REPORT.md`).

## Five-bullet version

- Alarm-selected observations can create recursive reference-state feedback
  when reused after a monitoring alarm.
- The frozen CUSUM core combines a Lean-checked derivative spine with an
  Arb-certified `Gamma_CUSUM>2` bound and a certified deterministic-skeleton
  period-2 orbit.
- The random-window theorem yields a protocol-specific `m`-`rho` local-stability
  boundary and the uncertainty-aware P3 reuse policy.
- SR and location-family results broaden the mechanism under explicit scope;
  the post-Level-4 SR Arb certificate is closed while L4R-13 remains partial.
- Semi-real evidence is supportive but regime-dependent, and the mathematical
  crossing produced no detected operational transition under the frozen
  protocol.

## Reviewer navigation

- Scientific spine: [MAIN_THEOREM_ARCHITECTURE.md](MAIN_THEOREM_ARCHITECTURE.md)
- Dependencies and scope: [RESULT_DEPENDENCY_GRAPH.md](RESULT_DEPENDENCY_GRAPH.md)
- Evidence labels: [EVIDENCE_HIERARCHY.md](EVIDENCE_HIERARCHY.md)
- Canonical notation: [DEFINITIONS_AND_NOTATION.md](DEFINITIONS_AND_NOTATION.md)
- Publication wording: [CLAIM_CATALOG.md](CLAIM_CATALOG.md)
- Limits and open work: [LIMITATIONS_AND_OPEN_ITEMS.md](LIMITATIONS_AND_OPEN_ITEMS.md)
- Paper plan: [PAPER_OUTLINE.md](PAPER_OUTLINE.md)
- Figure plan: [FIGURE_PLAN.md](FIGURE_PLAN.md)
- Evidence locations: [REPOSITORY_MAP.md](REPOSITORY_MAP.md)

Reproduce the terminal closure with
`bash level4/final_level4_closure/reproduce.sh`. Reproduce the separate SR
upgrade with
`bash level4/closure_proofs/sr_derivative/certificate/reproduce_closed_upgrade.sh`.
Run the synthesis guard with `python3 docs/research_synthesis/verify_synthesis.py`.

The terminal closure checkpoint is commit `49cf742` (`Close the frozen Level-4
campaign mechanically`). Its stored offline reproduction status is `PASS` with
`new_science_run=false` in
`level4/final_level4_closure/results/final_decision.json`.
