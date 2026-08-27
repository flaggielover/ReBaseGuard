# Result dependency graph

## Logical graph

```text
Stopping-selected recursive re-baselining mechanism
│
├── Frozen Gaussian CUSUM, m=1
│   ├── human model/change-of-measure bridge
│   └── Lean-checked stopped-likelihood differentiation spine
│       └── F'_rho(0)=rho(1-Gamma_CUSUM)
│           ├── Arb Gamma_CUSUM>2
│           │   └── local repulsion of zero at full reuse
│           │       └── certified deterministic-skeleton period-2 orbit
│           └── no direct stochastic invariant-law conclusion
│
├── Random-window extension, m>1
│   ├── ordinary tau + A_m with denominator min(m,tau)
│   ├── exact nonnegative short-cycle correction C_m
│   └── F'_{rho,m}(0)=rho(1-GammaTilde_m)
│       └── rho_c(m) and D4 local-stability map
│           ├── stability-aware P3 policy
│           └── operational-crossing study
│               └── NEGATIVE: no detected transition under frozen protocol
│
├── Cross-detector extension
│   └── symmetric two-chart SR derivative theorem CLOSED
│       └── post-Level-4 Arb Gamma_SR>2 certificate
│           └── local repulsion at full reuse for authoritative SR mean map
│               └── no stochastic operational or detector-general conclusion
│
├── Distributional extension
│   └── regular location-family theorem
│       ├── conditional Lean spine
│       ├── concrete analytic obligations human-proved
│       └── non-Gaussian strong extension L4R-13 PARTIAL
│
└── External and novelty support
    ├── semi-real validation: Stage E 0/3, V2 1/3, V3 2/2; total 3 >= 2
    └── novelty audit: N2 partial overlap, claims narrowed
```

## Dependency table

| Result | Requires | Does not establish |
|---|---|---|
| `m=1` derivative | frozen model, stopped likelihood, domination, mixed-reference algebra | a numerical value of `Gamma_CUSUM` |
| CUSUM local instability | derivative identity + Arb lower bound above two | nonlinear orbit or stochastic long-run law |
| deterministic period two | conditional-mean operator, oddness, separate interval certificate | period two of the noisy chain |
| `m>1` derivative | ordinary alarm `tau`, random window, short-cycle correction, conditional differentiation | Stage-A minimum-dwell theorem |
| D4 boundary | `m>1` theorem + numerical `GammaTilde_m` map | abrupt operational transition |
| P3 | D4 lower 95% boundary + frozen 0.8 margin + monitoring campaign | universal safety or optimality |
| SR derivative | SR-specific stopping functional, tails, stopped score, reflection | a numerical value of `Gamma_SR` without the separate certificate |
| SR local instability | SR derivative theorem + post-Level-4 Arb lower bound above two | stochastic operational instability or arbitrary SR variants |
| location-family theorem | common-support regularity and explicit stopped analytic hypotheses | distribution-free validity |
| external validation | frozen task-level semi-real protocols | production deployment |
| negative crossing | resolved frozen grid and four preselected metrics | universal absence of operational effects |

Authoritative dependency sources are `closure/02_THEOREM_MAP.md`,
`level4/closure_proofs/d4_phase_map/THEOREM_BRIDGE.md`, and
`level4/final_level4_closure/EVIDENCE_MAP.md`.
