# ReBaseGuard Continuum Certificate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use the approved continuum-certificate specification and execute this plan task-by-task. This task is being executed inline because the user requested autonomous work and did not request subagents.

**Goal:** Build and independently audit an Arb-backed continuum certificate proving `E[Z_tau T_tau] > 2` for the two-sided Gaussian CUSUM with `k=0.5`, `h=5`.

**Architecture:** A non-rigorous simulator and collocation solver construct candidate functions. A separate Arb path certifies the exact block contraction, continuum residuals, resolvent error, and final interval. A separately implemented interval Bellman solver provides a fallback/cross-check, while the audit command replays proof-critical inequalities from exact certificate inputs.

**Tech Stack:** CPython 3.14, pinned `python-flint`/FLINT/Arb, NumPy and SciPy for non-proof candidates, pytest, JSON/SHA-256, Make.

---

## File map

- `pyproject.toml`: package metadata, exact direct dependency pins, CLI entry points, pytest configuration.
- `requirements.lock`: fully resolved installed environment from `pip freeze`.
- `Makefile`: deterministic `diagnostic`, `test`, `proof`, and `audit` commands.
- `src/rebaseguard_certify/model.py`: exact CUSUM updates and alarm thresholds.
- `src/rebaseguard_certify/geometry.py`: reachable simplicial complex and symmetry maps.
- `src/rebaseguard_certify/equations.py`: ordinary evaluation of `K`, `K_z`, `r_a`, and `r_b`.
- `src/rebaseguard_certify/diagnostics.py`: seeded Monte Carlo diagnostics only.
- `src/rebaseguard_certify/mesh.py`: dyadic axis/triangle mesh and exact nodal serialization.
- `src/rebaseguard_certify/candidate.py`: non-rigorous collocation/value-iteration candidate solver.
- `src/rebaseguard_certify/arb_backend.py`: minimal wrappers around Arb balls and endpoint serialization.
- `src/rebaseguard_certify/contraction.py`: analytic continuum block-contraction certificate.
- `src/rebaseguard_certify/residual.py`: adaptive continuum residual enclosure.
- `src/rebaseguard_certify/enclosure.py`: resolvent error propagation and Gamma enclosure.
- `src/rebaseguard_certify/bellman.py`: independent cellwise interval Bellman fallback.
- `src/rebaseguard_certify/certificate.py`: proof orchestration, JSON generation, and hashes.
- `src/rebaseguard_certify/audit.py`: small independent replay auditor.
- `src/rebaseguard_certify/cli.py`: command-line interface and nonzero failure exits.
- `tests/`: focused unit, property, regression, proof-smoke, and tamper tests.
- `proofs/derivation.md`: human-readable mathematical derivation.
- `proofs/certificate.json`: generated machine certificate.
- `proofs/audit_report.md`: generated independent audit report.
- `diagnostics/`: explicitly non-rigorous JSON results.
- `results/`: timing, memory, hashes, and refinement logs.

### Task 1: Reproducible package and pinned environment

**Files:** Create `pyproject.toml`, `Makefile`, `src/rebaseguard_certify/__init__.py`, `src/rebaseguard_certify/cli.py`, `tests/test_cli.py`; generate `requirements.lock`.

- [ ] Create a local `.venv`, install `python-flint`, NumPy, SciPy, and pytest, and record their exact resolved versions.
- [ ] Write a failing CLI test:

```python
def test_cli_reports_noncertified_before_certificate(capsys):
    from rebaseguard_certify.cli import main
    assert main(["audit", "missing.json"]) != 0
```

- [ ] Add package entry points `rebaseguard-certify` and `rebaseguard-audit`, plus Make targets that always use `.venv/bin/python`.
- [ ] Run `.venv/bin/pytest tests/test_cli.py -q`; expect one passing test.
- [ ] Freeze the environment, record Python/FLINT/Arb runtime versions, and commit `build: scaffold pinned proof environment`.

### Task 2: Exact model, geometry, and symmetry

**Files:** Create `src/rebaseguard_certify/model.py`, `src/rebaseguard_certify/geometry.py`, `tests/test_model.py`, `tests/test_geometry.py`.

- [ ] Write failing update/alarm tests, including the exact thresholds:

```python
def test_alarm_thresholds():
    from rebaseguard_certify.model import thresholds
    assert thresholds(0.0, 0.0, 0.5, 5.0) == (-5.5, 5.5)
```

- [ ] Implement immutable state updates and explicit `UP`, `DOWN`, and `CONTINUE` outcomes.
- [ ] Write property tests showing every continuing state from the reachable complex remains on an axis or satisfies `p+m <= h-2*k`.
- [ ] Implement `reflect(p,m)=(m,p)` and tests showing path reflection swaps arms, negates terminal increments, and preserves `Z_tau*T_tau`.
- [ ] Run the focused tests and commit `feat: encode exact CUSUM geometry and symmetry`.

### Task 3: Non-rigorous diagnostic baseline

**Files:** Create `src/rebaseguard_certify/diagnostics.py`, `scripts/run_diagnostics.py`, `tests/test_diagnostics.py`; generate `diagnostics/reference.json`.

- [ ] Write tests for deterministic seeds, terminal arm/state recording, and agreement between scalar and vectorized paths on fixed innovations.
- [ ] Implement batched simulation that records `tau`, `Z_tau`, `T_tau`, `T_tau^2`, arm, and pre-terminal state.
- [ ] Run at least two independent seeded batches and require diagnostic checks for reflection, `E[T_tau^2] approximately E[tau]`, the known ARL scale, and `Gamma approximately 15.8`.
- [ ] Stamp every output with `proof_role: NON-RIGOROUS DIAGNOSTIC ONLY`.
- [ ] Commit `test: reproduce non-rigorous CUSUM target`.

### Task 4: Exact equations and independent checks

**Files:** Create `src/rebaseguard_certify/equations.py`, `tests/test_equations.py`; update `proofs/derivation.md`.

- [ ] Write tests for absorbing moments against high-accuracy ordinary quadrature:

```python
def test_absorbing_reward_at_origin():
    ra, rb = absorbing_rewards_float(0.0, 0.0, 0.5, 5.0)
    assert abs(ra) < 1e-15
    assert rb > 0.0
```

- [ ] Implement ordinary `phi`, `Phi`, `r_a`, `r_b`, `K`, and `K_z` exactly as specified.
- [ ] Independently compare one-step recursion with direct integration on fixed polynomial test functions.
- [ ] Test the affine decomposition by evaluating identical future paths from two different current cumulative sums.
- [ ] Document the derivation, reachable-domain proof, and symmetry proof; commit `docs: derive and test coupled Fredholm equations`.

### Task 5: Dyadic mesh and non-rigorous candidates

**Files:** Create `src/rebaseguard_certify/mesh.py`, `src/rebaseguard_certify/candidate.py`, `tests/test_mesh.py`, `tests/test_candidate.py`.

- [ ] Write tests that the triangle-plus-axis mesh covers the closed reachable complex without gaps and that shared nodes serialize identically.
- [ ] Implement dyadic coordinates using integer numerators and a common power-of-two denominator.
- [ ] Implement continuous piecewise-linear evaluation and exact dyadic nodal export.
- [ ] Implement deterministic ordinary fixed-point/collocation iteration for `a_hat,b_hat`, enforcing symmetry only after the symmetry tests pass.
- [ ] Compare `b_hat(0,0)` against both Monte Carlo and an unreduced ordinary discretization; commit `feat: construct deterministic candidate value functions`.

### Task 6: Arb primitives and exact serialization

**Files:** Create `src/rebaseguard_certify/arb_backend.py`, `tests/test_arb_backend.py`.

- [ ] Write containment tests for `phi`, `Phi`, Gaussian mass, first moment, and second tail moment at rational inputs over multiple precisions.
- [ ] Wrap `flint.arb` without converting proof-critical values through binary float; construct inputs from integers or decimal strings.
- [ ] Serialize every ball as exact decimal lower/upper endpoints produced with outward containment and enough digits for round-trip inclusion.
- [ ] Test that higher precision produces contained or narrower balls for representative operations.
- [ ] Commit `feat: add outward-rounded Arb proof primitives`.

### Task 7: Rigorous continuum block contraction

**Files:** Create `src/rebaseguard_certify/contraction.py`, `tests/test_contraction.py`; update `proofs/derivation.md`.

- [ ] Write tests that reject sampled-grid evidence and require an analytic `q_n` derivation record.
- [ ] Implement Arb evaluation of

```text
q_n = 2 Q((h+n*k)/sqrt(n)),
beta_n = 1-q_n,
C_n = n/(1-beta_n).
```

- [ ] Search candidate integers using ordinary arithmetic, then recompute the selected integer solely with Arb exact inputs.
- [ ] Assert with strict ball endpoints that `q_n>0`, `beta_n<1`, and `C_n >= n/(1-beta_n)`.
- [ ] Emit and independently reload the first block-contraction artifact; commit `proof: certify global killed-kernel contraction`.

### Task 8: Continuum residual certifier

**Files:** Create `src/rebaseguard_certify/residual.py`, `tests/test_residual.py`, `tests/test_coverage.py`.

- [ ] Write failing coverage tests that inject a missing source simplex, reset-boundary sliver, or `z` subinterval and require rejection.
- [ ] Implement exact enumeration of source cells and conservative destination-cell intersection for `q(s,z)`.
- [ ] Implement adaptive Arb enclosure of `K a_hat`, `K b_hat`, and `K_z a_hat`, retaining ambiguous slivers and explicit Gaussian mass totals.
- [ ] Prove cellwise residual intervals cover `rho_a` and `rho_b` for every continuum source point; take outward maxima `delta_a,delta_b`.
- [ ] Add precision/subdivision regression tests and commit `proof: enclose continuum Fredholm residuals`.

### Task 9: Resolvent propagation and first Gamma interval

**Files:** Create `src/rebaseguard_certify/enclosure.py`, `tests/test_enclosure.py`.

- [ ] Write exact synthetic tests where known residual bounds produce known error bounds.
- [ ] Compute with Arb

```text
mu = sqrt(2/pi),
E_a = C*delta_a,
E_b = C*(delta_b + mu*E_a),
Gamma = b_hat(0,0) + [-E_b,E_b].
```

- [ ] Reject any non-Arb proof input, non-finite ball, inconsistent endpoint, or lower endpoint not strictly greater than two.
- [ ] Run adaptive refinement driven by the largest residual contributors until the first rigorous interval is obtained or the residual route reaches its resource ceiling.
- [ ] Commit `proof: propagate residuals to a Gamma enclosure`.

### Task 10: Independent interval Bellman fallback

**Files:** Create `src/rebaseguard_certify/bellman.py`, `tests/test_bellman.py`.

- [ ] Write tests for lower/upper ordering, continuing-plus-absorbing mass enclosing one, signed reward handling, and width improvement under refinement.
- [ ] Implement a separate cellwise range representation that does not import candidate or residual modules.
- [ ] Implement interval Bellman lower/upper iterations with the certified resolvent tail bound.
- [ ] Compare its enclosure with the residual result; if the primary route fails, refine this route automatically.
- [ ] Commit `proof: add independent interval Bellman fallback`.

### Task 11: Certificate generation and independent audit

**Files:** Create `src/rebaseguard_certify/certificate.py`, `src/rebaseguard_certify/audit.py`, `tests/test_certificate.py`, `tests/test_audit.py`; generate `proofs/certificate.json`, `proofs/audit_report.md`.

- [ ] Write tamper tests for model parameters, mesh hash, contraction endpoints, residual coverage, Gamma endpoints, and missing artifacts.
- [ ] Generate JSON containing exact inputs, environment versions, artifact hashes, contraction proof, residual coverage, propagation bounds, and final interval.
- [ ] Implement the auditor without importing the candidate solver or diagnostic code.
- [ ] Replay Arb contraction, coverage/hashes, residual maxima, resolvent propagation, and strict `Gamma_L>2`; exit nonzero on any discrepancy.
- [ ] Commit `proof: generate and independently audit certificate`.

### Task 12: Reproducibility, full verification, and final report

**Files:** Finalize `README.md`, `Makefile`, `requirements.lock`, `proofs/derivation.md`, `proofs/audit_report.md`, `results/reproducibility.json`; create the final proof report in `proofs/ReBaseGuard_Certified_Lemma_Proof_Report.md`.

- [ ] Run `make clean-proof-state`, `make test`, `make proof`, and `make audit` from documented prerequisites.
- [ ] Record wall time, peak memory, platform, Python, python-flint, FLINT/Arb versions, certificate SHA-256, and exact commands.
- [ ] Verify a fresh audit uses no diagnostic or candidate-solving imports and rejects a deliberately corrupted certificate.
- [ ] Write all twenty requested report sections, explicitly correcting the invalid `E[Z_tau^2]` shortcut and stating limitations.
- [ ] End the report with exactly the verdict justified by the audited interval; commit `docs: publish certified lemma proof report`.

## Plan self-review

- Spec coverage: state reduction, reachable geometry, exact equations, Arb backend, global block contraction, continuum residuals, resolvent propagation, Bellman fallback, diagnostics, tests, certificate, auditor, reproducibility, and final report are each assigned to a task.
- Placeholder scan: no deferred implementation markers are present.
- Type consistency: `a_hat`, `b_hat`, `delta_a`, `delta_b`, `C`, `mu`, `E_a`, `E_b`, and `Gamma` use the same names and meanings from candidate construction through audit.
- Trust boundary: only Arb-backed certification, exact serialized inputs, and auditor logic determine the final interval.
