# Figure plan

No figure is regenerated in this synthesis phase. The main text should use
approximately eight nonredundant figures; campaign-debug and estimator-audit
figures belong in appendices.

| # | Proposed figure | Source artifact | Purpose and paper section | Placement | Required cleanup / notation | Caption thesis |
|---:|---|---|---|---|---|---|
| 1 | Repeated monitoring and feedback mechanism | New schematic derived from `closure/01_FROZEN_MODEL.md` and `level4/closure_proofs/l4r06_policy/THEORY_BRIDGE.md` | Make the stopping-time selection and cross-cycle reference feedback visually explicit; Sections 1--3 | Main | Use `e,Z_t,tau,T_tau,m,rho`; separate stochastic cycle from mean map | Alarm-participating observations are selected by `tau`, reused in the next reference, and recursively alter later cycles. |
| 2 | Local derivative and rigorous instability | `level4/figures/fig11_conditional_map_near_zero.png`, plus values from `rebaseguard-proof/proofs/certificate.json` | Connect derivative slope, Arb enclosure, and stable/unstable local behavior; Sections 4--5 | Main | Replace legacy Gamma labels with `Gamma_CUSUM`; visually separate Lean identity from Arb value | The stopped-selection gain makes the full-reuse zero fixed point locally repelling for the frozen CUSUM. |
| 3 | Certified deterministic period-two skeleton | `level4/figures/fig06_conditional_map.png` and `level4/stage_b/certificate/period2_certificate.json` | Show `F_1(e)` against `-e`, root interval, and attracting two-cycle; Section 5 | Main | Put “deterministic conditional-mean skeleton” in panel title; add certified bands from the certificate | The nonlinear mean map has a certified attracting two-cycle, without asserting period two for the noisy chain. |
| 4 | `m`-`rho` local-stability map | `level4/closure_proofs/d4_phase_map/figures/d4_local_stability_map.png` | Present the finite-window boundary and crossing; Section 6 | Main | Use `GammaTilde_m`, `rho_c(m)`, and “local deterministic”; mark `[70,72]` | Larger windows weaken the stopping-selected gain and move the local boundary through full reuse near `m=71`. |
| 5 | Gain and boundary diagnostics | `level4/closure_proofs/d4_phase_map/figures/d4_gamma_and_boundary.png` | Show `GammaTilde_m`, short-cycle-aware boundary, intervals, and accessible region; Section 6 | Main or appendix if Figure 4 absorbs it | Add the `GammaTilde_m=2` reference and avoid calling it an operational threshold | The Track-1B gain declines with window length, creating a mathematical full-reuse crossing. |
| 6 | Stability-aware P3 policy performance | `level4/closure_proofs/l4r06_policy/figures/figure_a_policy.png`, `figure_b_reference_distortion.png`, `figure_c_operational_consequence.png`, `figure_d_noninferiority.png` | Combine policy action, reference MSE, false-alert burden, and primary non-inferiority; Section 7 | Main, multi-panel | Use P0/P1/P2/P3 definitions consistently; visibly mark P3=P1 at `m=100`; retain unfavorable annotations | An uncertainty-aware reuse allowance improves reference state and false-alert burden in active regimes while preserving the frozen primary response criterion. |
| 7 | Cross-campaign external validation | `level4/closure_proofs/external_validation_v3/figures/figure_a_cross_campaign_reference_distortion.png`, `figure_b_operational_consequences.png`, `figure_c_p2_noninferiority.png`, `figure_d_joint_support_matrix.png` | Show task-level support and regime dependence; Section 9 | Main, multi-panel | Label Stage E/V2/V3 separately; show 0/3, 1/3, 2/2 and non-pooled total 3 | Semi-real support crosses the frozen task-count requirement, while negative tasks and P2 regime dependence remain visible. |
| 8 | Negative operational-crossing result | `level4/stage_d/figures/fig_D_bridge.png` and `level4/closure_proofs/d4_phase_map/figures/d4_operational_overlay.png` | Put the mathematical crossing beside four smooth operational metrics; Section 10 | Main | Mark both Stage-D `[50,75]` and D4 `[70,72]` brackets; annotate 0/4 peaks and 4/4 monotone | The mathematical local-stability crossing has no detected operational transition under the frozen protocol. |

## Appendix figures

Use SR raw/log correspondence, location-family variance diagnosis, D4 direct
map cells, protocol/adversarial diagrams, sensitivity ladders, and additional
semi-real task diagnostics only where they document methods or robustness.
Avoid redundant campaign-progress figures in the main text.

Before publication, verify every listed image path and replace any legacy title
that says merely `Gamma_m` with the convention-specific notation.
