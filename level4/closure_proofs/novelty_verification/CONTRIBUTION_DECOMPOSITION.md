# Frozen contribution decomposition

This decomposition precedes external search and prevents monolithic novelty
reasoning. Types describe the strongest current repository status; they do not
claim literature novelty.

| ID | Atomic component | Type | Repository evidence and boundary |
|---|---|---|---|
| C1 | Alarm-participating observations are reused to estimate/update the next reference state | ENGINEERING / PROTOCOL CONTRIBUTION | Frozen model definition throughout Levels 1–4; a studied mechanism, not a theorem |
| C2 | Repeated alarm-selected reuse creates cycle-to-cycle reference dynamics that feed the next stopping input | ENGINEERING / PROTOCOL CONTRIBUTION | Multi-cycle oracle and deterministic reference map; no claim of detector-statistic novelty |
| C3 | Local reference-map derivative is expressed by a stopped-score / stopped sufficient-statistic covariance-like gain | THEOREM | Level 1–3 proof and Track 3A/3B; only under explicit stopped-process hypotheses |
| C4 | Frozen Gaussian two-sided CUSUM has `Gamma_CUSUM` and a rigorous local-instability certificate | CERTIFICATE | Lean identity plus Arb enclosure; detector/protocol-specific |
| C5 | Convention-A `m>1` random-window derivative includes the `tau<m` short-cycle correction | THEOREM | Track 1B closure; historical Stage-D formula remains failed |
| C6 | `F'_{rho,m}(0)=rho(1-GammaTilde_m)` induces `rho_c(m)=1/(GammaTilde_m-1)` where `GammaTilde_m>1` | THEOREM | D4 consequence of C5 plus confirmatory map; the crossing near `m=71.419386` is not operational |
| C7 | Authoritative symmetric two-chart Shiryaev–Roberts detector satisfies the corresponding stopped-score derivative identity | THEOREM | Track 2; `Gamma_SR>2` is confirmatory numerical and rigorous SR instability remains open |
| C8 | A regular location-family extension uses `Gamma_f=E_0[Z_tau sum_{t<=tau}psi(Z_t)]` | THEOREM | Track 3A/3B under explicit analytic hypotheses; not distribution-free |
| C9 | A nonzero locally attracting period-2 orbit exists for the deterministic conditional-mean skeleton at full reuse | CERTIFICATE | Stage B rigorous certificate; does not imply noisy-chain period-2 behavior or bimodality |
| C10 | The local mathematical stability boundary has no established operational monitoring phase transition | NEGATIVE RESULT | Stage-D D2.5 and D4 preserve `MATHEMATICAL, NOT OPERATIONAL` |
| C11 | The findings motivate selection-aware/safe re-baselining constraints | INTERPRETATION | Limited engineering implication; no validated production benefit, policy optimality, or external validity claim |

Numerical results that support a theorem input or illustrate a boundary remain
numerical. In particular, `Gamma_SR>2`, the D4 grid/crossing location, and
non-Gaussian estimates are not promoted to general theoretical contributions.

