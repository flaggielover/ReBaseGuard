# ReBaseGuard

**ReBaseGuard studies how repeated monitoring changes when observations selected
by an alarm stopping time are reused to update the next reference state.**

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
produces a negative result. The project keeps theorem, formal proof, certified
numerics, empirical evidence, and limitations distinct.

## Current Level-4 research status

At the current authoritative repository state, the campaign status is:

| Priority | Status | Current conclusion |
|---|---|---|
| P1 | `CLOSED` | The frozen \(m>1\) CUSUM derivative theorem is closed within its stated convention. |
| P2 | `CLOSED` | The frozen symmetric two-chart SR derivative/stability result is closed, with its supporting Lean and Arb evidence. |
| P3 | `CLOSED` | The reuse-fraction local stability map is closed; its conclusions are local deterministic results. |
| P4 | `PARTIAL` | The general location-family derivative theorem and supporting proof, numerical, Lean, and Arb evidence survived independent review. Three frozen preregistered numerical closure gates remain literally false; none was weakened or rewritten. Novelty remains `NOVELTY-NOT-ADJUDICATED`. |
| P5 | `PARTIAL` | The raw-mean identity and the fixed-policy invariant-law/ergodicity theorem survive independent adjudication. Global deterministic attraction, operational-invisibility, and universal finite-grid claims were narrowed; several literal closure gates fail. Novelty remains `NOVELTY-NOT-ADJUDICATED`. |
| P6 | `CLOSED` | The safe-rebaselining campaign and its literal closure repairs are complete at the repository's authoritative status; its scope and negative results remain as adjudicated. |
| P7 | `CLOSED` | Independent adjudication confirms material monitoring degradation under recursive re-baselining, while \(\rho_c\) is a local mathematical boundary, not an operational safety boundary under the frozen criterion. |
| P8 | `FAIL` | Broad tested local repulsion and operational degradation reproduce, but the cross-family window law and its sub-gates are rejected, G7 fails literally, and the temporal-integrity gate fails. The evidence is scope-bound and novelty is not independently adjudicated. |

## Why this problem exists

The cycle is **monitor -> alarm at a data-dependent stopping time -> reuse
alarm-participating observations -> update the next reference -> monitor
again**. Because the alarm selected the reused observations, they need not
behave like fresh reference data; the resulting update then changes later
monitoring cycles.

![Recursive reference, monitor, alarm, reuse, and update loop.](figures/final/figure01_recursive_rebaselining.png)

## Results at a glance

> **Strongest rigorous core.** For the frozen two-sided Gaussian CUSUM with
> \(m=1,\rho=1,k=1/2,h=5\), a human theorem connects the reference-map
> derivative to the stopped gain; Lean kernel-checks the differentiation and
> moment spine; and an independent outward-rounded Arb certificate proves
> \(\Gamma_{\mathrm{CUSUM}}>2\). Together—not Lean or Arb alone—these establish
> that zero is locally repelling for the deterministic conditional-mean map.

| Result | Evidence type | Current status |
|---|---|---|
| CUSUM stopped-selection derivative | Human bridge + Lean-checked spine | Proved for the frozen model |
| \(\Gamma_{\mathrm{CUSUM}}>2\) | Arb interval certificate | Certified |
| Symmetric two-chart SR local instability | Human/conditional Lean spine + separate Arb certificate | `SR-GAMMA-CERTIFIED` |
| Deterministic period-two skeleton | Human theorem + rigorous numerical certificate | Certified within the stated interval |
| Finite-window \(m>1\) derivative | Human theorem + conditional Lean spine | Closed for the Track-1B convention |
| Stability-aware P3 policy | Frozen numerical + semi-real evidence | Scoped empirical support |
| Operational crossing hypothesis | Frozen operational evaluation | Negative result under the tested protocol |

## Core mathematical result

For reuse fraction \(\rho\), reference error \(e\), and stopped gain
\(\Gamma\), the frozen \(m=1\) derivative is

\[
F'_\rho(0)=\rho(1-\Gamma).
\]

Arb certifies
\(\Gamma_{\mathrm{CUSUM}}\in[3.9243482,27.8493821]\). The later, separate
symmetric two-chart SR upgrade certifies
\(\Gamma_{\mathrm{SR}}\in[5.800391799508442,28.781285803081492]\), whose lower
endpoint exceeds two by \(3.800391799508442\). These are local deterministic
results, not global or operational instability theorems for noisy chains.

## Evidence and verification

| Evidence layer | What it checks | Status | Entry point |
|---|---|---|---|
| Human mathematics | Model bridge, assumptions, and theorem interpretation | Proved within stated scope | [Theorem map](closure/02_THEOREM_MAP.md) |
| Numerical correspondence | Frozen simulations and consistency checks | Confirmatory, not proof | [Evidence hierarchy](docs/research_synthesis/EVIDENCE_HIERARCHY.md) |
| Lean | Stopped-likelihood derivative and moment proof spine | Kernel-checked | [Lean audit guide](rebaseguard-lean/README.md) |
| Arb | Outward-rounded gain enclosures | Certified | [CUSUM certificate](closure/04_ARB_CERTIFICATE.md) |

Lean does not certify either numerical interval; Arb does not prove
differentiation under the expectation. The human theorem supplies the bridge.

## Quick reproduction

```bash
(cd rebaseguard-lean && lake build)
(cd rebaseguard-proof && .venv/bin/python -m rebaseguard_certify.audit proofs/certificate.json)
```

The first command checks the primary Lean library. The second replays the CUSUM
certificate. For frozen release snapshots, use the separate
[`terminal closure snapshot`](docs/releases/LEVEL4_RELEASE_NOTES.md) and
[`SR-GAMMA-CERTIFIED`](docs/releases/SR_GAMMA_CERTIFIED_RELEASE_NOTES.md)
instructions. Current presentation checks are:

```bash
python3 scripts/verify_academic_presentation.py --no-diff-check
python3 docs/research_synthesis/verify_synthesis.py --no-diff-check
```

## Repository map

| Reader question | Entry point |
|---|---|
| What exactly does Lean verify? | [Lean audit guide](rebaseguard-lean/README.md) |
| What is the complete scientific narrative? | [Research synthesis](docs/research_synthesis/README.md) |
| Where are theorem dependencies and evidence boundaries? | [Theorem architecture](docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md) and [evidence hierarchy](docs/research_synthesis/EVIDENCE_HIERARCHY.md) |
| Where is the short academic overview? | [Four-page Research Brief](docs/research_brief/ReBaseGuard_Research_Brief.pdf) |
| Where are frozen artifacts by topic? | [Reviewer-first repository map](docs/research_synthesis/REPOSITORY_MAP.md) |
| What wording and limitations are authoritative? | [Claim catalog](docs/research_synthesis/CLAIM_CATALOG.md) and [limitations register](docs/research_synthesis/LIMITATIONS_AND_OPEN_ITEMS.md) |

## Limitations and negative results

- Historical Stage-D D2.3 and Track 1A remain failed. The later Track 1B
  theorem is a separate result under its own random-window convention.
- L4R-13 non-Gaussian robustness remains `PARTIAL` and nonmandatory.
- Results concern frozen CUSUM and one symmetric two-chart SR model; they are
  neither detector-independent nor distribution-free.
- Deterministic local multipliers do not establish stochastic invariant laws
  or an operational phase transition. Under the frozen crossing study, **0/4**
  metrics peaked at the crossing and **4/4** were monotone in \(\log m\).
- Policy and semi-real evidence are regime-scoped, not production validation;
  the novelty position is scoped to the documented search.

## Priority-7 operational consequence

P7's independent adjudication finds that recursive re-baselining materially
degrades monitoring performance. Nominal single-cycle ARL is about **465**;
fresh-reference recursive ARL is roughly **80–162**, and full-reuse ARL roughly
**48–80**, with substantial false-alarm inflation. Detection delay develops a
severe heavy tail. One-cycle calibration can look normal while cycle 2 collapses
to about **5.6–9.4** in mean run length.

The P3 critical reuse fraction \(\rho_c\) is a local mathematical boundary. Under
P7's frozen operational criterion it is **not** an operational safety boundary.
This is a monitoring consequence, not a global nonlinear-dynamics theorem.

### P7 theory-status boundaries

| Statement | Status |
|---|---|
| P7-A | Exact finite-cycle conditional theorem. |
| P7-B | Conditional-exact stationary identity. |
| P7-C | Conditional proposition with an empirically supported but unproved global sign condition. |
| P7-D | Monte Carlo plug-in diagnostic; not certified. |

P7 itself left stationary-law existence, uniqueness, ergodicity, and finite
fourth moment as simulation evidence. P5 now proves those properties for the
same frozen Gaussian constant-policy convention-A chain, with the explicit
cross-reference and limitations recorded in P5's independent adjudication. The
P7 artifacts remain unchanged. The repository distinguishes proved theorems,
conditional theorems, rigorous certificates, numerical evidence, exploratory
observations, and novelty status.

## Future research implications

- **P5:** retain the exact raw-mean and fixed-policy ergodicity results; treat
  attraction, global cycle uniqueness, bimodality onset, and the dispersion
  optimum at their adjudicated conditional or numerical tiers.
- **P6:** preserve its adjudicated safe-rebaselining scope and literal repairs;
  do not treat \(\rho < \rho_c\) as a universal safety rule or import P5's
  measured optimum as a design constant.
- **P8:** retain the tested robustness evidence only within its empirical and
  conditional-theorem tiers. Do not use the rejected window-separability law,
  assume detector or P7-boundary transfer, or claim novelty.

## Research status and reproducibility

The status labels above are internal, scope-bound research designations. They
are not an external academic standard, certification, endorsement, or
peer-review result. Frozen artifacts and campaign records remain authoritative;
this README summarizes them and does not replace their evidence boundaries.

## Author and citation

**Jingzhe Su (苏靖哲)** · School of Information and Software Engineering ·
University of Electronic Science and Technology of China ·
[suzhea0226@gmail.com](mailto:suzhea0226@gmail.com)

Use [CITATION.cff](CITATION.cff) and the relevant immutable release tag when
citing a snapshot. Citation is scholarly practice, not a condition of the
Apache License 2.0. No institutional endorsement is implied.

## License

Original ReBaseGuard software, formalizations, proof and certificate
implementations, documentation, and figures are licensed under the
[Apache License 2.0](LICENSE) only to the extent owned by the licensor.
Third-party dependencies, datasets, bibliographic records, and source-derived
portions retain their respective terms and are excluded from that grant. See
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the audited boundaries.
