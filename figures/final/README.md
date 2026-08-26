# Final publication figures

These eight figures are presentation-only derivatives of frozen ReBaseGuard evidence.
They do not run simulations, download data, or modify scientific artifacts.

Regenerate with:

```bash
level4/.venv/bin/python scripts/generate_final_figures.py
```

## Provenance

| ID | Title | Evidence | Paper | PNG SHA-256 | SVG SHA-256 |
|---|---|---|---|---|---|
| Figure 1 | Stopping-selected recursive re-baselining | INTERPRETATION / CONCEPTUAL DIAGRAM | Sections 1–3 | `6bcd26915f929be5f4208a6591345c7500c74c9d28d801dea93ec4c27916bddc` | `6e7562d4a1556b2f3e5a2f11764e85140f56a7d507c9c77b0bdd2d17bb6de47f` |
| Figure 2 | Stopped-selection derivative and local instability | LEAN-CHECKED + ARB-CERTIFIED + HUMAN THEOREM BRIDGE | Sections 4–5 | `7e4b119fdd214bdabae28be916f3ef820fc971846be1edc0cfc3d92f27274101` | `dc333a7e6508d3a5843cd812b1b60361201da7dc3326591ae391dba2aa8dc950` |
| Figure 3 | Certified period-two orbit of the deterministic skeleton | RIGOROUS NUMERICAL CERTIFICATE | Section 5 | `2de25a0d29cf74276032db8846bf43fc375f1837643343e9a9d9b213b84d9359` | `08dbef988ee232c64b02d1ce4705f4690a63e2de18ff0851c3688173e2c95f40` |
| Figure 4 | Finite-window local-stability map | HUMAN THEOREM CONSEQUENCE + CONFIRMATORY NUMERICAL | Section 6 | `3e96c3f0234f819738569f604d446be7557662cef40c7dbefd28a3d6fcda0b88` | `ddf0ba2dbe73e1ed452315d185db64334db65217500408d862c1fe3303e69e3b` |
| Figure 5 | Frozen stability-aware P3 reuse policy | METHOD DEFINITION + CONFIRMATORY NUMERICAL | Section 7 | `84065540a5c1a4376f3d5d0949c4d03d4871bf5cfa828d30d0964d7343a78065` | `e36be863a939dc0fbdb83658f5b72e9d349fa56a35622cf9f9c0f6c83c791dc9` |
| Figure 6 | Reference-state and monitoring consequences | CONFIRMATORY NUMERICAL | Section 7 | `b03ab97296f18c459073b375bee490c28ccf4af3f177a363e61c53a2f7aad2eb` | `c56df4807eca13f41c92a55676976b745685ddff665a61460b45e42a836dee6a` |
| Figure 7 | Semi-real external-validation synthesis | SEMI-REAL EMPIRICAL | Section 9 | `ec5144012f726b99a30f99fac78e7fbac2c60343006a3f91d66e63169a0b81e9` | `7fbbcdeaccf6d651e58d8732a8775eb0bbe2eac3c4d2fe5ba0bc271dea792ffe` |
| Figure 8 | Mathematical crossing without detected operational transition | NEGATIVE RESULT | Section 10 | `7365165e23fc0690cbbd8652baf4834416fddd7556d633889687bee4bc642185` | `1bc285d95d638628af582dc9201fb08c9eb195d4fb6135d9b170c716a418402e` |

## Figure details

### Figure 1 — Stopping-selected recursive re-baselining

- **Purpose:** Define the cross-cycle feedback mechanism.
- **Sources:** `docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md`, `docs/research_synthesis/DEFINITIONS_AND_NOTATION.md`
- **Source SHA-256:** `docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md` `f6390a4c225045686ad8049a943a6efb18492138b661bcccd9ff459942d3e3f4`, `docs/research_synthesis/DEFINITIONS_AND_NOTATION.md` `9447fee60fa90e96a1aab3c19f19ad1fc9379829b3739d2ef695dbf717c9c542`
- **Transformation:** Explanatory vector diagram from the frozen synthesis narrative; no quantitative values.
- **Evidence classification:** INTERPRETATION / CONCEPTUAL DIAGRAM
- **Paper section:** Sections 1–3
- **Limitation:** Diagram defines the mechanism; it is not empirical or proof evidence.

### Figure 2 — Stopped-selection derivative and local instability

- **Purpose:** Separate the Lean-checked derivative spine from the Arb-certified gain enclosure.
- **Sources:** `rebaseguard-proof/proofs/certificate.json`, `docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md`
- **Source SHA-256:** `rebaseguard-proof/proofs/certificate.json` `85e68c7dde306f2e6ce464203def22089e9b935d1cfca4b4944cef191d80545e`, `docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md` `f6390a4c225045686ad8049a943a6efb18492138b661bcccd9ff459942d3e3f4`
- **Transformation:** Exact interval transformation F'_1(0)=1-Gamma_CUSUM and evidence-flow diagram.
- **Evidence classification:** LEAN-CHECKED + ARB-CERTIFIED + HUMAN THEOREM BRIDGE
- **Paper section:** Sections 4–5
- **Limitation:** Local deterministic fixed-point conclusion only; Lean does not certify the Gamma value.

### Figure 3 — Certified period-two orbit of the deterministic skeleton

- **Purpose:** Show the rigorously certified symmetric deterministic orbit and multiplier.
- **Sources:** `level4/stage_b/certificate/period2_certificate.json`
- **Source SHA-256:** `level4/stage_b/certificate/period2_certificate.json` `99095e4bc8eaf960c41ea9732a5a739eec8e7dc402188de552b8bc7e687e8a68`
- **Transformation:** Direct diagram of the certified root and multiplier intervals.
- **Evidence classification:** RIGOROUS NUMERICAL CERTIFICATE
- **Paper section:** Section 5
- **Limitation:** No stochastic-chain period-two or invariant-law claim.

### Figure 4 — Finite-window local-stability map

- **Purpose:** Show the D4 deterministic local boundary rho_c(m).
- **Sources:** `level4/closure_proofs/d4_phase_map/results/decision.json`
- **Source SHA-256:** `level4/closure_proofs/d4_phase_map/results/decision.json` `8b21f4dae37d0f59ba01b179573f55bb2b831bf526574691c4af3f4bc452f80a`
- **Transformation:** Log-m interpolation between frozen D4 grid values for display; plotted grid points remain visible.
- **Evidence classification:** HUMAN THEOREM CONSEQUENCE + CONFIRMATORY NUMERICAL
- **Paper section:** Section 6
- **Limitation:** Mathematical deterministic local-stability boundary, not an observed operational phase transition.

### Figure 5 — Frozen stability-aware P3 reuse policy

- **Purpose:** Compare P0, P1, fixed P2, and uncertainty-aware P3 at four frozen regimes.
- **Sources:** `level4/closure_proofs/l4r06_policy/results/scientific_findings.json`
- **Source SHA-256:** `level4/closure_proofs/l4r06_policy/results/scientific_findings.json` `994ca341606f9a40fe37b8968820d6aaca8292d60808203cfbce6664c3853c49`
- **Transformation:** Direct plot of frozen policy actions and lower-95%-boundary allowances.
- **Evidence classification:** METHOD DEFINITION + CONFIRMATORY NUMERICAL
- **Paper section:** Section 7
- **Limitation:** P3 is scoped and not universally optimal; m=100 saturates at P1.

### Figure 6 — Reference-state and monitoring consequences

- **Purpose:** Show frozen reference-MSE and false-alert-burden improvements in active regimes.
- **Sources:** `level4/closure_proofs/l4r06_policy/results/scientific_findings.json`
- **Source SHA-256:** `level4/closure_proofs/l4r06_policy/results/scientific_findings.json` `994ca341606f9a40fe37b8968820d6aaca8292d60808203cfbce6664c3853c49`
- **Transformation:** Direct point and simultaneous lower-95%-bound display for H6-2 and H6-3.
- **Evidence classification:** CONFIRMATORY NUMERICAL
- **Paper section:** Section 7
- **Limitation:** P2 has descriptive advantages at m=70 and m=100; P3=P1 at m=100; two secondary epsilon=0.05 conditions fail.

### Figure 7 — Semi-real external-validation synthesis

- **Purpose:** Retain every Stage E, V2, and V3 task while showing the non-pooled closure count.
- **Sources:** `level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md`, `level4/closure_proofs/external_validation_v3/results/decision.json`
- **Source SHA-256:** `level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md` `e7c45c1062d045e1f164fc0c921704eef23a93578631c4f6cde4f62ef4a46b76`, `level4/closure_proofs/external_validation_v3/results/decision.json` `b3939a091ac577bbc0605c27954e9ec95abf2d9f00ab65e1b7a9119bc2db3118`
- **Transformation:** Parse the frozen task table and render a task matrix plus campaign support counts.
- **Evidence classification:** SEMI-REAL EMPIRICAL
- **Paper section:** Section 9
- **Limitation:** No pooled samples, production deployment, universal safety, or detector-independence claim.

### Figure 8 — Mathematical crossing without detected operational transition

- **Purpose:** Place the frozen mathematical crossing beside all four preselected operational metrics.
- **Sources:** `level4/stage_d/results/d2_5_bridge.json`, `level4/closure_proofs/d4_phase_map/results/decision.json`
- **Source SHA-256:** `level4/stage_d/results/d2_5_bridge.json` `6186a3c27847431c10f9fdbf3f3a16b496f8a773877e74aa0815e62860a14cc6`, `level4/closure_proofs/d4_phase_map/results/decision.json` `8b21f4dae37d0f59ba01b179573f55bb2b831bf526574691c4af3f4bc452f80a`
- **Transformation:** Four small multiples of frozen tabulated means with Stage-D and D4 crossing bands.
- **Evidence classification:** NEGATIVE RESULT
- **Paper section:** Section 10
- **Limitation:** Negative answer is limited to the frozen Gaussian CUSUM protocol, grid, shifts, and metrics.

## Visual system

All figures use DejaVu Sans, charcoal text, restrained blue/gold/orange/pink/olive roots,
near-white backgrounds, quiet grids, shared line weights, and non-color encodings such as
hatching, marker shape, open fills, direct labels, and line style. SVG is the vector master;
PNG is exported at 220 dpi for GitHub rendering.

The machine-readable companion is `figures/final/manifest.json`.
