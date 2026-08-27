# ReBaseGuard

## Plain-language abstract

Drift monitoring is often repeated: a system raises an alarm, updates its
reference, and starts monitoring again. If that update reuses observations that
helped trigger the alarm, the reference data were selected through a
data-dependent stopping event rather than sampled afresh. ReBaseGuard studies
the recursive feedback created by this reuse. It develops mathematical
descriptions of the resulting reference dynamics, with rigorous local
instability results for frozen CUSUM and symmetric two-chart
Shiryaev-Roberts settings. It also evaluates a stability-aware reuse policy on
simulated and semi-real streams. The policy receives scoped support in the
tested regimes, while a pre-specified operational-transition hypothesis
produces a negative result. The project separates theorem, formal proof,
certified numerics, empirical evidence, and limitations throughout.

## Why this problem exists

A repeated monitoring system can feed its own stopping decision into its next
cycle:

![Reference, monitoring, alarm, reuse, and update form a recursive feedback loop.](figures/final/figure01_recursive_rebaselining.png)

The loop is **monitor -> alarm at a data-dependent stopping time -> reuse
alarm-participating observations -> update the next reference -> monitor
again**. The reused observations are not necessarily equivalent to fresh
reference data because their participation is connected to the event that
triggered the alarm. The updated reference then changes the distribution and
stopping behavior of the next cycle. ReBaseGuard isolates this
**stopping-selected recursive re-baselining** mechanism rather than treating it
as generic drift detection.

## Results at a glance

| Result | Evidence type | Current status |
|---|---|---|
| Stopping-selected reuse changes local reference dynamics | Analytic theorem + Lean-checked spine | Established for the frozen model |
| Frozen Gaussian CUSUM instability coefficient exceeds two | Arb rigorous certificate | Certified |
| Authoritative symmetric two-chart SR instability coefficient exceeds two | Arb rigorous certificate | `SR-GAMMA-CERTIFIED` |
| Deterministic conditional-mean skeleton admits period-two behavior | Rigorous deterministic certificate | Established within the certified interval |
| Finite-window reuse yields an \(m\)-\(\rho\) local-stability boundary | Theorem + deterministic analysis | Established for the frozen convention |
| Stability-aware P3 reuse policy | Frozen simulation + semi-real evidence | Supported within tested regimes |
| Operational crossing hypothesis | Frozen operational evaluation | Negative result under the tested protocol |

For a compact advisor/application overview, read the
[four-page Research Brief](docs/research_brief/ReBaseGuard_Research_Brief.pdf).
For the complete scientific narrative and evidence routing, use the
[research synthesis](docs/research_synthesis/README.md).

## Core mathematical result

Let \(e\) be the current reference error, \(m\) the reuse-window length,
\(\rho\) the reuse fraction, and \(F_{\rho,m}(e)\) the deterministic
conditional mean of the next reference error. Under the frozen Track-1B
random-window convention,

\[
F'_{\rho,m}(0)=\rho\left(1-\widetilde{\Gamma}_m\right).
\]

For the frozen Gaussian CUSUM with \(m=1\), Lean checks the
stopped-likelihood differentiation spine and outward-rounded Arb arithmetic
independently certifies
\(\Gamma_{\mathrm{CUSUM}}\in[3.9243482,27.8493821]\). The human theorem bridge
therefore makes zero locally linearly repelling at full reuse.

For the authoritative symmetric two-chart Shiryaev-Roberts detector, a later
post-closure optional rigor upgrade certifies
\(\Gamma_{\mathrm{SR}}\in[5.800391799508442,28.781285803081492]\), so its
rigorous lower endpoint exceeds two by \(3.800391799508442\). Both conclusions
are local results for deterministic conditional-mean maps; they are not claims
of global or operational instability of the stochastic monitoring process.

![Lean-checked derivative spine, human model bridge, and Arb-certified interval.](figures/final/figure02_derivative_instability.png)

## Research status and reproducibility

`LEVEL-4-CLOSED` is ReBaseGuard's **internal project-closure designation for a
pre-specified research checklist**. It is not an external academic standard,
third-party certification, publication decision, institutional endorsement, or
peer-review result.

| Internal research-management item | Status |
|---|---|
| Research-program status | Internal closure checklist complete (`LEVEL-4-CLOSED`) |
| Internal ledger | 17 PASS, 1 PARTIAL, 0 FAIL, 0 OPEN |
| Mandatory internal requirements | 16/16 satisfied |
| Remaining nonmandatory extension | L4R-13 non-Gaussian robustness remains `PARTIAL` |
| Post-closure rigor upgrade | `SR-GAMMA-CERTIFIED` |

At the original Level-4 closure, the SR derivative theorem was closed while
the rigorous SR Arb certificate remained open. That optional item was closed
later as `SR-GAMMA-CERTIFIED`; the historical ledger and tags were not
rewritten. See the [terminal closure report](level4/final_level4_closure/FINAL_REPORT.md),
[mechanical decision](level4/final_level4_closure/results/final_decision.json),
and [SR certificate](level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md).

## Evidence map

| Result | Evidence | Authoritative entry point |
|---|---|---|
| CUSUM derivative spine | Human theorem + Lean-checked | [Lean verification](closure/03_LEAN_VERIFICATION.md) |
| \(\Gamma_{\mathrm{CUSUM}}>2\) | Arb-certified | [Arb certificate report](closure/04_ARB_CERTIFICATE.md) |
| Period-two skeleton | Rigorous deterministic certificate | [Stage-B report](level4/reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md) |
| Random-window \(m>1\) derivative | Human theorem + conditional Lean-checked spine | [Track-1B theorem](level4/closure_proofs/m_gt_1_track1b/THEOREM.md) |
| D4 \(m\)-\(\rho\) boundary | Theorem consequence + confirmatory numerical | [D4 report](level4/closure_proofs/d4_phase_map/FINAL_REPORT.md) |
| SR derivative | Human theorem + conditional Lean-checked spine | [SR theorem report](level4/closure_proofs/sr_derivative/FINAL_REPORT.md) |
| \(\Gamma_{\mathrm{SR}}>2\) | Post-closure Arb-certified | [SR Gamma certificate](level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md) |
| Location-family derivative | Human theorem + conditional Lean-checked spine | [Location-family theorem](level4/closure_proofs/location_family_track3ab/THEOREM.md) |
| External validation | Semi-real empirical | [Cross-campaign aggregation](level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md) |
| Operational crossing | Negative result | [Operational-crossing report](level4/closure_proofs/l4r12_operational_crossing/FINAL_REPORT.md) |

Evidence labels are descriptive rather than cumulative. The
[evidence hierarchy](docs/research_synthesis/EVIDENCE_HIERARCHY.md) states
exactly what each layer does and does not establish.

## Stability-aware reuse policy

The frozen P3 method uses 80% of the simultaneous lower-95% D4 boundary,
clipped at one:

\[
\rho_{\mathrm{P3}}(m)=\min\left(1,\;0.8\,\rho_{c,L95}(m)\right).
\]

![P0, P1, P2, and P3 reuse fractions at the four frozen regimes.](figures/final/figure05_p3_policy.png)

At \(m=1,20,70,100\), P3 uses reuse fractions \(0.053642\), \(0.245418\),
\(0.781994\), and \(1\). In active regimes it improved the frozen
reference-MSE and false-alert-burden contrasts against P1. At \(m=100\), P3
saturates at P1; P2 retains descriptive advantages at \(m=70\) and \(m=100\),
and two secondary \(\epsilon=0.05\) conditions fail. The result is scoped to
the frozen policy protocol.

## Semi-real validation

The external-validation package retains every semi-real/public sequential task
without pooling samples: Stage E is **0/3**, V2 is **1/3**, and V3 is **2/2**.
That is three supporting tasks against two required by the internal protocol.
Unsuccessful tasks remain visible, and P2 safety is regime-dependent. These
results are not production deployment evidence.

![Eight external-validation tasks and their campaign-level support counts.](figures/final/figure07_external_validation.png)

## Negative result

The D4 mathematical local-stability boundary brackets the full-reuse crossing
at \(m\in[70,72]\). Under the frozen operational protocol, **0/4** preselected
metrics peaked at the crossing and **4/4** were monotone in \(\log m\). The
study therefore detected no corresponding operational transition. This
conclusion is limited to the frozen Gaussian CUSUM protocol, grid, shifts, and
monitored metrics.

![Four operational metrics pass smoothly through the mathematical crossing.](figures/final/figure08_negative_crossing.png)

## Reproduce

From a normal Git clone on a Unix-like system with Bash, Python 3, Git, the
repository's Python environments, Lean/Lake, and FLINT/Arb available as
documented, reproduce the historical terminal closure with:

```bash
git checkout rebaseguard-level4-closed
bash level4/final_level4_closure/reproduce.sh
```

Reproduce the separate post-closure SR rigor upgrade with:

```bash
git checkout rebaseguard-sr-gamma-certified
bash level4/closure_proofs/sr_derivative/certificate/reproduce_closed_upgrade.sh
```

The commands are intentionally separate because the historical 52-file SR
freeze predates the additive certificate. Current presentation checks are run
with:

```bash
python3 scripts/verify_academic_presentation.py
python3 docs/research_synthesis/verify_synthesis.py --no-diff-check
```

## Repository navigation

| Reader question | Entry point |
|---|---|
| What is the complete scientific story? | [Research synthesis](docs/research_synthesis/README.md) |
| What are the principal theorem dependencies? | [Main theorem architecture](docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md) |
| What exactly is rigorous, formal, numerical, or empirical? | [Evidence hierarchy](docs/research_synthesis/EVIDENCE_HIERARCHY.md) |
| Where is every load-bearing artifact? | [Reviewer-first repository map](docs/research_synthesis/REPOSITORY_MAP.md) |
| What wording is safe? | [Claim catalog](docs/research_synthesis/CLAIM_CATALOG.md) |
| What remains limited or open? | [Limitations and open items](docs/research_synthesis/LIMITATIONS_AND_OPEN_ITEMS.md) |
| Where is the short academic overview? | [Research Brief](docs/research_brief/ReBaseGuard_Research_Brief.pdf) |
| Where are the final figures and provenance? | [Final figures](figures/final/README.md) |
| Where are the two frozen releases? | [Release records](docs/releases/) |

## Limitations

- L4R-13, the stronger non-Gaussian robustness requirement, remains `PARTIAL`
  and nonmandatory.
- CUSUM and one authoritative symmetric two-chart SR detector are treated; no
  detector-independent conclusion follows.
- The location-family theorem has explicit regularity assumptions and is not a
  distribution-free result.
- Local multipliers and the period-two certificate concern deterministic
  conditional-mean maps, not the noisy chain's invariant law.
- The D4 boundary is mathematical and local, not an operational
  phase-transition theorem.
- Empirical policy safety is regime-dependent, and semi-real tasks do not
  establish production readiness.
- The N2 novelty position is limited to the documented search scope; it is not
  a priority or exhaustive-search claim.

See the full [limitations register](docs/research_synthesis/LIMITATIONS_AND_OPEN_ITEMS.md).

## Author

**Jingzhe Su (苏靖哲)**<br>
School of Information and Software Engineering<br>
University of Electronic Science and Technology of China<br>
Email: [suzhea0226@gmail.com](mailto:suzhea0226@gmail.com)

The affiliation identifies the author's institution and does not imply
institutional endorsement of this project.

## Citation

Use the factual repository metadata in [CITATION.cff](CITATION.cff). No paper or
release DOI, journal, conference, acceptance, or peer-review status is claimed.
For a fixed snapshot, include the relevant tag and resolved commit:

- terminal research-program snapshot: `rebaseguard-level4-closed`;
- post-closure SR certificate snapshot: `rebaseguard-sr-gamma-certified`.

## License

**License: not yet specified.** Copyright defaults apply; do not assume
permission to reuse, modify, or redistribute beyond applicable law. The
[licensing-readiness audit](docs/releases/LICENSING_READINESS.md) separates
source code, prose, figures, proofs/certificates, and third-party data so a
future rights-holder decision can be made without fabricating permission.
