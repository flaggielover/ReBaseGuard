# ReBaseGuard — Level-4 Closed Research Release

## Release identity

- Tag: `rebaseguard-level4-closed`
- Terminal verdict: `LEVEL-4-CLOSED`
- Ledger: `17 PASS`, `1 PARTIAL`, `0 FAIL`, `0 OPEN`
- Mandatory requirements: `16/16 PASS`
- Closure checkpoint: `49cf742` (`Close the frozen Level-4 campaign mechanically`)
- Synthesis checkpoint: `37926db` (`Add final ReBaseGuard research synthesis`)
- Publication checkpoint: the commit resolved by this release tag

“Level 4” is the project’s internally frozen closure criterion, not an external
academic certification.

## Scientific scope

ReBaseGuard studies stopping-selected recursive re-baselining: observations
that participate in a sequential alarm are reused to update the next reference,
which recursively changes later monitoring cycles. This release changes
presentation and navigation only. It does not revise theorem statements,
certificates, data, experiments, requirement statuses, historical reports, or
the terminal decision.

## Principal results

1. For the frozen Gaussian CUSUM at \(m=1\), a human theorem and Lean-checked
   differentiation spine give the stopped-selection derivative structure
   \(F'_\rho(0)=\rho(1-\Gamma_{\mathrm{CUSUM}})\).
2. Outward-rounded Arb arithmetic certifies
   \(\Gamma_{\mathrm{CUSUM}}>2\), implying local repulsion at zero for the
   full-reuse deterministic conditional-mean map.
3. A rigorous numerical certificate establishes a locally attracting
   period-two orbit of the deterministic conditional-mean skeleton, not of the
   noisy stochastic chain.
4. The Track-1B random-window theorem extends the derivative to \(m>1\) with
   its exact short-cycle correction and yields the D4 protocol-specific
   \(m\)-\(\rho\) local-stability boundary.
5. The symmetric two-chart SR derivative theorem is closed, while
   \(\Gamma_{\mathrm{SR}}>2\) remains confirmatory numerical evidence and the
   rigorous SR Arb certificate remains open.
6. A regular common-support location-family theorem gives the corresponding
   derivative under explicit analytic hypotheses.
7. The frozen P3 policy uses
   \(\rho_{\mathrm{P3}}(m)=\min(1,0.8\rho_{c,L95}(m))\) and passed its scoped
   primary criteria. Historical failures and unfavorable comparisons remain
   visible.

The authoritative scientific spine is
`docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md`.

## Evidence types

Lean checks the formal differentiation spine; Arb certifies the CUSUM
enclosure; human theorems carry analytic assumptions not wholly discharged in
Lean; confirmatory numerical results remain non-rigorous; semi-real tasks do
not constitute deployment validation; and negative results answer only their
pre-specified scoped questions. See
`docs/research_synthesis/EVIDENCE_HIERARCHY.md`.

## Negative result

D4 identifies a mathematical deterministic local-stability crossing at full
reuse, bracketed by \(m\in[70,72]\). Under the frozen operational-crossing
protocol, 0/4 preselected metrics peaked there and 4/4 were monotone in
\(\log m\). No corresponding operational transition was detected under that
protocol. This is not a general no-effect result.

## External validation

The non-pooled semi-real task record is Stage E 0/3, V2 1/3, and V3 2/2:
three supporting tasks against two required. Failed tasks remain in the final
figure and evidence record; P2 safety is regime-dependent.

## Novelty position

Within the documented search scope, no identified work combines the same
alarm-stopped next-reference mechanism with the reported derivative and
stability results. This is the frozen N2 scoped position, not a priority or
exhaustiveness claim. The audit is at
`level4/closure_proofs/novelty_verification/`.

## Publication-facing additions

- Eight consistent, traceable figures in `figures/final/`
- Deterministic renderer at `scripts/generate_final_figures.py`
- Reviewer-first root `README.md`
- Final research synthesis in `docs/research_synthesis/`
- Mechanical release guard and checklist in `docs/releases/`

## Reproduce

The authoritative offline terminal command is:

```bash
bash level4/final_level4_closure/reproduce.sh
```

Regenerate the presentation figures with:

```bash
level4/.venv/bin/python scripts/generate_final_figures.py
```

Exact figure inputs, transformations, limitations, and SHA-256 values are in
`figures/final/README.md` and `figures/final/manifest.json`.

## Known limitations and optional upgrades

- L4R-13 non-Gaussian robustness remains `PARTIAL` and nonmandatory.
- A rigorous SR local-instability Arb certificate remains `OPEN`.
- D4 is a deterministic local boundary, not an operational phase-transition
  theorem.
- Policy and external-validation safety findings are regime-dependent.
- There is no production-readiness result.
- The N2 novelty statement is search-scope limited.
- Optional future work may strengthen the SR certificate, discharge additional
  location-family obligations, or study stochastic invariant behavior. None is
  required for the frozen `LEVEL-4-CLOSED` verdict.

## Authoritative closure locations

- `level4/final_level4_closure/FINAL_REPORT.md`
- `level4/final_level4_closure/REQUIREMENT_LEDGER.md`
- `level4/final_level4_closure/OPEN_ITEMS.md`
- `level4/final_level4_closure/STATUS_TRANSITIONS.md`
- `level4/final_level4_closure/results/final_decision.json`
- `level4/final_level4_closure/reproduce.sh`

No DOI is assigned, no explicit repository license is included, and no
speculative citation metadata has been added.
