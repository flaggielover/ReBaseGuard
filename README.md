# ReBaseGuard Certified Lemma Proof

This repository contains a computer-assisted continuum proof for the two-sided
Gaussian CUSUM with `k=0.5`, `h=5`:

```text
Gamma = E[Z_tau T_tau] > 2.
```

The audited enclosure is

```text
Gamma in [3.924348200582897128..., 27.849382127546703281...].
```

The finite spectral solve is only a candidate constructor. The proof consists
of Arb-certified continuum residual bounds, a continuum block contraction, an
explicit resolvent error bound, and a full replay audit.

## Pinned environment

- CPython 3.14.5
- python-flint 0.9.0
- FLINT 3.6.0 with Arb real-ball arithmetic
- NumPy 2.5.2
- SciPy 1.18.0
- pytest 9.1.1

Create the local environment:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
```

## Reproduce

```bash
make test
make diagnostic
make proof
make audit
```

`make proof` reconstructs the exact dyadic candidate, continuum residual,
contraction, enclosure, independent finite Bellman cross-check, certificate,
and full audit. It exits nonzero unless the audited lower endpoint is greater
than two. `make audit` independently replays the existing certificate without
running the ordinary candidate solver.

On the reference Apple-silicon machine, tests take about 4 seconds, proof
generation plus its full replay takes approximately 4–10 minutes, and a
standalone full audit takes approximately 2–7 minutes. The proof artifacts are
small (under 100 KiB); peak working memory is recorded in
`results/reproducibility.json`.

## Proof artifacts

- `proofs/derivation.md`: exact equations and error propagation.
- `proofs/certificate.json`: machine-readable certificate.
- `proofs/audit_report.md`: full replay result.
- `proofs/ReBaseGuard_Certified_Lemma_Proof_Report.md`: final mathematical report.
- `diagnostics/reference.json`: explicitly non-rigorous Monte Carlo checks.

The ordinary diagnostic and finite Bellman result are cross-checks only. They
do not contribute to the certified lower endpoint.

## Phase-4 feasibility pre-gate

The finite-Bellman/Monte-Carlo discrepancy and detector-dependence of the score
identity are audited separately from the protected certificate:

```bash
make pregate
make pregate-audit
```

This preserves the historical finite Arb implementation, runs the pathwise and
Monte Carlo diagnostics plus the independent refined Bellman solver, and writes
`diagnostics/phase4_pregate.json`. The findings and stopped-score proof are in
`proofs/ReBaseGuard_Phase4_Feasibility_PreGate_Report.md`. These diagnostics are
not part of the continuum proof trusted base.
