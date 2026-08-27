# Main theorem architecture

## Research object

An alarm is not an ordinary sampling time. ReBaseGuard asks how a monitor
changes when observations selected through the alarm stopping time are reused
to form the next reference and the resulting reference error is fed into the
next cycle. The central mathematical object is the conditional-mean reference
map `F`; the scientific task is to connect its derivative and nonlinear
dynamics to explicitly bounded evidence without confusing the deterministic
map with the noisy monitoring recursion.

## Theorem 1 — stopped-selection derivative at `m=1`

For the frozen two-sided Gaussian CUSUM, let `e=R_j-mu`,
`Z_t=epsilon_t-e`, `tau` be the inclusive alarm time, and
`T_tau=sum_{t<=tau}Z_t`. With one reused terminal observation and reuse fraction
`rho`,

`F_rho(e)=rho(e+E_e[Z_tau])`

and

`F'_rho(0)=rho(1-Gamma_CUSUM)`,

`Gamma_CUSUM=E_0[Z_tau T_tau]`.

Assumptions include iid standard-Gaussian innovations, the frozen reset
CUSUM (`k=1/2`, `h=5`), terminal inclusion, and the stopped measurability,
moment, and domination conditions discharged in the formal/human chain.

- **Evidence:** HUMAN THEOREM + LEAN-CHECKED differentiation spine.
- **Lean:** the final frozen-detector derivative identity is
  `hasDerivAt_rebaseguard_cusum`; no `sorry`, `admit`, or custom scientific
  axiom occurs.
- **Arb:** not needed for the identity; Arb enters Theorem 2.
- **Implication:** local behavior is governed by one stopped-selection gain,
  not by the variance of an ordinary sample.
- **Sources:** `closure/02_THEOREM_MAP.md`,
  `closure/03_LEAN_VERIFICATION.md`, and
  `rebaseguard-lean/RebaseguardLean/ReBaseGuardIdentity.lean`.

## Theorem 2 — rigorous CUSUM local instability

Outward-rounded Arb arithmetic certifies

`Gamma_CUSUM in [3.924348200582897,27.849382127546703]`.

The lower endpoint is strictly greater than two. Combining this numerical
certificate with Theorem 1 gives `F'_1(0)=1-Gamma_CUSUM<-1`, so zero is a
locally linearly repelling fixed point of the full-reuse deterministic
conditional-mean map.

- **Evidence separation:** LEAN-CHECKED proves the differentiation spine;
  ARB-CERTIFIED proves the numerical enclosure; the HUMAN THEOREM/model bridge
  connects them.
- **Scope:** frozen CUSUM, `m=1`, `rho=1`, local deterministic behavior.
- **Sources:** `rebaseguard-proof/proofs/certificate.json`,
  `closure/04_ARB_CERTIFICATE.md`, and `closure/02_THEOREM_MAP.md`.

## Theorem 3 — deterministic-skeleton period two

At `m=1` and `rho=1`, the frozen CUSUM deterministic conditional-mean skeleton
has a unique nonzero root of `F_1(e)+e` within

`e_star in [1.0287242887,1.0447242887]`.

Odd symmetry produces the orbit `{e_star,-e_star}`. Its two-cycle multiplier
is certified in

`lambda_2 in [0.1081476358,0.8325317050] subset (0,1)`,

so the orbit is locally attracting for the deterministic skeleton.

- **Evidence:** HUMAN THEOREM + ARB-CERTIFIED rigorous numerical certificate.
- **Scope limitation:** no global uniqueness outside the stated interval and no
  theorem about the invariant law, bimodality, or period-two behavior of the
  noisy stochastic reference chain.
- **Sources:** `level4/stage_b/certificate/period2_certificate.json` and
  `level4/reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md`.

## Theorem 4 — random-window derivative for `m>1`

Track 1B retains the ordinary alarm time and defines

`A_m=(1/min(m,tau))*sum_{r=0}^{min(m,tau)-1}Z_{tau-r}`,

`GammaTilde_m=E_0[A_m T_tau]`.

Then, for finite fixed `m`,

`F'_{rho,m}(0)=rho(1-GammaTilde_m)`.

The exact identity

`GammaTilde_m=(1/m)sum_{r=0}^{m-1}gamma_r+C_m`,

`C_m=E_0[1{tau<m}(1/tau-1/m)T_tau^2]>=0`,

is the short-cycle correction. At `m=1`, `C_1=0` and Theorem 1 is recovered.

- **Evidence:** HUMAN THEOREM + compiled LEAN-CHECKED algebraic and conditional
  analytic spine + confirmatory numerical correspondence.
- **Lean boundary:** the concrete random stopped window, measurability,
  integrability, and uniform dominator are human-instantiated, not formalized
  end to end.
- **Historical boundary:** Stage A uses a minimum-dwell stopping time and fixed
  denominator; it is a different `m>1` object. Historical D2.3 and Track 1A
  remain failed.
- **Sources:** `level4/closure_proofs/m_gt_1_track1b/THEOREM.md`,
  `level4/closure_proofs/m_gt_1_track1b/LEAN_CORRESPONDENCE.md`, and
  `level4/closure_proofs/m_gt_1_track1b/results/decision.json`.

## Theorem 5 — the `m`-`rho` local-stability boundary

Theorem 4 gives the local multiplier

`lambda(m,rho)=rho(1-GammaTilde_m)`.

When `GammaTilde_m>1`, the sign-reversing unit-magnitude boundary is

`rho_c(m)=1/(GammaTilde_m-1)`.

The D4 map classifies `|lambda|<1` as locally stable and `|lambda|>1` as locally
unstable. The full-reuse crossing `GammaTilde_m=2`, equivalently `rho_c=1`, is
bracketed at `m in [70,72]`; its frozen secondary log-linear interpolation is
`71.419386`. Direct-map correspondence passes 6/6 frozen cells.

- **Evidence:** HUMAN THEOREM consequence + CONFIRMATORY NUMERICAL D4 map.
- **Interpretation:** **MATHEMATICAL, NOT OPERATIONAL.** It is a local boundary
  of a deterministic conditional-mean map under one frozen protocol.
- **Sources:** `level4/closure_proofs/d4_phase_map/FINAL_REPORT.md`,
  `level4/closure_proofs/d4_phase_map/THEOREM_BRIDGE.md`, and
  `level4/closure_proofs/d4_phase_map/results/decision.json`.

## Theorem 6 — symmetric two-chart SR derivative

For the authoritative symmetric SR detector with reset charts

`R_t^+=(1+R_{t-1}^+)exp(Z_t-1/2)`,

`R_t^-=(1+R_{t-1}^-)exp(-Z_t-1/2)`,

inclusive alarm threshold `A=520.886133602749`, and `m=1`, define
`Gamma_SR=E_0[Z_tau T_tau]`. Then

`F'_rho(0)=rho(1-Gamma_SR)`.

Reflection swaps charts, preserves `tau`, and establishes oddness. A forcing
event gives the geometric-tail and moment control used by the human stopped
change-of-measure proof.

- **Derivative theorem:** CLOSED; HUMAN THEOREM + conditional LEAN-CHECKED
  proof spine.
- **At terminal Level-4 closure:** `Gamma_SR>2` had CONFIRMATORY NUMERICAL
  support; the rigorous Arb certificate remained `OPEN`.
- **Current post-Level-4 status:** ARB-CERTIFIED. The later optional upgrade
  gives `Gamma_SR in [5.800391799508442,28.781285803081492]`, with rigorous
  lower-endpoint margin `3.800391799508442` above two. Combined with the closed
  derivative theorem, this makes zero locally linearly repelling at full reuse
  for the authoritative symmetric two-chart SR deterministic mean map.
- **Boundary:** the certificate is SR-model-specific and local/deterministic;
  it does not establish stochastic operational instability or a result for
  arbitrary SR variants.
- **Sources:** `level4/closure_proofs/sr_derivative/THEOREM.md`,
  `level4/closure_proofs/sr_derivative/FINAL_REPORT.md`,
  `level4/closure_proofs/sr_derivative/results/decision.json`,
  `level4/closure_proofs/sr_derivative/ARBITRARY_PRECISION_ATTEMPT.md`, and
  `level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md`.

## Theorem 7 — regular location-family derivative

Let `f_e(z)=f(z+e)` be a regular one-dimensional location family on locally
common support, with conventional location score
`psi(z)=-f'(z)/f(z)`. For a fixed residual-path stopping functional and actual
raw-observation `m=1` reuse, define

`Gamma_f=E_0[Z_tau sum_{t<=tau}psi(Z_t)]`.

Under explicit stopped change-of-measure, measurability, almost-sure
finiteness, event-slice summability, integrability, and domination hypotheses,

`F'_rho(0)=rho(1-Gamma_f)`.

For the standard Gaussian, `psi(z)=z`, so this reduces to Theorem 1. Rho scaling
does not require symmetry; symmetry supplies oddness and the zero fixed point.

- **Evidence:** HUMAN THEOREM + conditional LEAN-CHECKED algebraic/stopped-score
  spine + variance-aware t3 confirmatory correspondence.
- **Human-only concrete obligations:** infinite-process measurability and
  parameter independence, geometric stopping tail, stopped likelihood/change
  of measure, integrability, event-slice summability, and domination.
- **Scope:** regular location families satisfying the stated hypotheses; not
  moving-support families without boundary terms. Historical Stage-D t3
  remains ambiguous and historical Track 3 remains partial/failed.
- **Sources:** `level4/closure_proofs/location_family_track3ab/THEOREM.md`,
  `level4/closure_proofs/location_family_track3ab/PROOF_OBLIGATIONS.md`,
  `level4/closure_proofs/location_family_track3ab/FINAL_REPORT.md`, and
  `level4/closure_proofs/location_family_track3ab/results/decision.json`.

## Method result — stability-aware P3 reuse

The frozen policy is

`rho_P3(m)=min(1,0.8*rho_c,L95(m))`.

The lower 95% endpoint makes the rule uncertainty-aware; multiplying by `0.8`
adds a precommitted 20% margin before clipping. For `m={1,20,70,100}`, the
actions are `{0.053642,0.245418,0.781994,1.000000}`. The evaluated shifts were
`Delta={0.25,0.5,1.0,1.5}` under the frozen Gaussian CUSUM protocol.

P3 improved reference MSE and false-alert burden in every active regime and
was non-inferior to fresh reference on all 16 primary normalized-response
conditions. It is not universally optimal: historical C6 remains failed, P2
has descriptive advantages at `m=70,100`, P3=P1 at saturated `m=100`, and two
secondary `epsilon=0.05` conditions remain unfavorable. The later
same-requirement campaign closes L4R-06 without rewriting Stage C.

Sources: `level4/closure_proofs/l4r06_policy/POLICY_DEFINITION.md`,
`level4/closure_proofs/l4r06_policy/results/scientific_findings.json`, and
`level4/closure_proofs/l4r06_policy/FINAL_REPORT.md`.

## First-class negative result — no detected operational crossing

The mathematical `GammaTilde_m=2` crossing is real and is located consistently
by Stage D and D4. Under the frozen operational protocol, however, 0/4
preselected metrics peaked at the crossing and 4/4 were monotone in log `m`
across 20,000 replicates. The pre-specified positive transition hypothesis is
therefore falsified for the monitored metrics and design.

The result is: **a mathematical local-stability boundary without detected
operational transition under the frozen protocol.** It is not a general
no-effect theorem.

Sources: `level4/closure_proofs/l4r12_operational_crossing/FINAL_REPORT.md` and
`level4/closure_proofs/l4r12_operational_crossing/results/evidence_assessment.json`.

## External-validation result

The external program uses semi-real/public sequential streams and a frozen
task-counting rule; task estimates are not pooled.

| Campaign | Task | Reference distortion | Operational consequence | P2 safety | Joint support |
|---|---|---|---|---|---|
| Stage E | Electricity / Elec2 | YES | NO | NO | NO |
| Stage E | UCI Air Quality | NO | NO | YES | NO |
| Stage E | UCI Bike Sharing | NA | YES | YES | NO |
| V2 | Beijing PM2.5 | YES | YES | NO | NO |
| V2 | Household power | YES | YES | YES | YES |
| V2 | Metro traffic | YES | NO | NO | NO |
| V3 | MetroPT-3 compressor | YES | YES | YES | YES |
| V3 | Online Retail II | YES | YES | YES | YES |

Stage E remains 0/3, V2 remains 1/3, and V3 contributes 2/2. The
cross-campaign count is therefore three successful tasks against two required.
P2 safety is regime-dependent: the two V3 tasks and V2 Household pass, while
V2 Beijing and Metro do not establish their frozen safety hypothesis. Both V3
Route-B medium-step response findings remain unfavorable. This closes the
scoped semi-real requirement, not production deployment.

Sources: `level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md`,
`level4/closure_proofs/external_validation_v3/FINAL_REPORT.md`, and
`level4/closure_proofs/external_validation_v3/results/decision.json`.

## Novelty-safe position

The closed position is **N2 — PARTIAL-OVERLAP-FOUND-CLAIMS-NARROWED**. The
frozen audit ran 36 primary queries, inspected 2,445 unique candidate works
after DOI/title deduplication, included 33, classified 0 as DIRECT and 9 as
HIGH-PARTIAL, and recorded unavailable primary indexes. Strong partial overlap
exists in adaptive/self-starting monitoring, post-alarm estimation, repeated
detection, reset/forgetting systems, and adaptive windows, so claims were
narrowed.

Publication-safe wording is: “Within the documented search scope, no work was
identified that combines the same alarm-stopped next-reference mechanism with
the reported derivative and stability results.” This is a scoped search result,
not an exhaustive priority finding.

Sources: `level4/closure_proofs/novelty_verification/results/search_manifest.json`,
`level4/closure_proofs/novelty_verification/results/decision.json`, and
`level4/closure_proofs/novelty_verification/FINAL_REPORT.md`.
