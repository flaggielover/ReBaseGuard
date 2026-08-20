# 04 — Arb Rigorous Numerical Certificate

**Subject:** the certification of `Γ_CUSUM > 2` for the frozen model of
`01_FROZEN_MODEL.md`.

**Reproduction status:**

```text
CERTIFICATE REPRODUCED
```

The certificate was **actually re-executed** on 2026-08-20 in this closure
session, not merely read from stored artifacts. Details in §11–§14.

---

## 1. Exact mathematical quantity certified

```text
Γ = E₀[ Z_τ · T_τ ]
```

for the frozen two-sided Gaussian CUSUM. The certificate's own machine-readable
fields state this without ambiguity:

```json
"target":       "E[Z_tau*T_tau]",
"target_state": "Gamma=b(0,0)",
"state_reduction": "E[Z_tau*T_tau|S_t=(p,m),T_t=x]=a(p,m)*x+b(p,m)",
"result":       "Gamma_lower > 2",
"proof_status": "CERTIFIED"
```

The auditor **enforces** the target string (`audit.py:40`,
`_require(certificate.get("target") == "E[Z_tau*T_tau]", "wrong target")`), so a
silently substituted functional would fail the replay.

The quantity is **not** `E[Z_τ²]` and **not** `E[Z_τ T_{τ−1}]`. The proof report
devotes §3 to explaining why the `E[Z_τ²] > 2 ⇒ Γ > 2` shortcut is invalid (the
cross term has no established sign) and states that the shortcut is never used.

## 2. Exact frozen model, as enforced by the auditor

```python
_require(
    certificate.get("model")
    == {"k": {"numerator": 1, "denominator": 2},
        "h": {"numerator": 5, "denominator": 1}},
    "wrong model",
)                                              # audit.py:36-39
```

`k` and `h` are carried as **exact rationals**, not floats, and a mismatch is a
hard audit failure. This matches §2 of `01_FROZEN_MODEL.md` and the Lean literals
in `hasDerivAt_rebaseguard_cusum`.

## 3. Numerical method

1. **State reduction.** Conditioning on the live state `s=(p,m)` and current sum
   `x=T_t`, the future is conditionally independent of `x`, giving the affine
   ansatz `E[Z_τT_τ|s,x] = a(s)x + b(s)` and `Γ = b(0,0)`.
2. **Fredholm system.** With `ℓ = m−h−k`, `u = h+k−p`,
   `q(s,z) = (max(0,p+z−k), max(0,m−z−k))`,
   `(Kf)(s) = ∫_ℓ^u f(q(s,z))φ(z)dz`, `(K_zf)(s) = ∫_ℓ^u z f(q(s,z))φ(z)dz`,
   and exact absorbing rewards `r_a = φ(u)−φ(ℓ)`,
   `r_b = uφ(u)+1−Φ(u)+Φ(ℓ)−ℓφ(ℓ)`, first-step conditioning gives
   `a = Ka + r_a`, `b = Kb + K_z a + r_b`.
3. **Candidate (non-proof).** A degree-12 tensor Chebyshev collocation solve
   produces `â, b̂`; coefficients are then rounded to **exact dyadic rationals**
   with common denominator `2^50`. At that point the floating-point solver leaves
   the proof path entirely — `"candidate_role": "exact dyadic candidate only; not proof evidence"`.
4. **Certified residual.** The exact rational candidate is converted to power
   polynomials, the kernel is split at every reset regime, `φ` is replaced by its
   degree-100 Maclaurin polynomial **with a rigorous uniform Lagrange remainder**,
   and each piece is integrated symbolically. The residual is a bivariate Arb
   polynomial on the regions `p+m ≤ 1` and `p+m ≥ 1`.
5. **Continuum range bound.** The reachable set is parameterized by `p = r·t`,
   `m = r·(1−t)`; tensor Bernstein conversion bounds the residual on `0≤r≤1`,
   `1≤r≤4` and the axis tails `4≤r≤5` (4 patches, `subdivision_depth = 0`). The
   Bernstein convex-hull property is a **continuum** bound, so
   `"sampled_grid_used": false` and `"reachable_continuum_complete": true`.
6. **Resolvent.** A monotone one-sided Bellman minorant plus pathwise-coupling
   monotonicity gives a genuine left-endpoint step *envelope* (not grid sampling),
   yielding `‖K^250‖_∞ ≤ β = 0.81 < 1` and
   `‖(I−K)^{-1}‖_∞ ≤ n/q_safe = 250/0.19`.
7. **Error propagation.** `E_a = C·δ_a`, `E_b = C·(δ_b + μ·E_a)`,
   `Γ ∈ b̂(0,0) + [−E_b, E_b]`.

## 4. Arb / python-flint version

| Component | Version |
|---|---|
| Interval backend | `python-flint` / FLINT-Arb |
| `python_flint` | `0.9.0` |
| `flint` | `3.6.0` |
| Semantics | `"outward-rounded real balls"` |
| Precision | 256 bits (residual, propagation); 192 bits (stored contraction artifact) |
| CPython | 3.14.5 |
| NumPy / SciPy | 2.5.2 / 1.18.0 (candidate + diagnostics only — **outside** the trusted base) |
| Platform of record | `macOS-26.5.2-arm64-arm-64bit-Mach-O` |

Verified live in this session: `.venv/bin/python -c "import flint; print(flint.__version__)"` → `0.9.0`, Python `3.14.5`.

## 5. Outward-rounding strategy

Arb's native real-ball arithmetic is outward-rounded by construction: every
operation returns a ball provably containing the exact result. The project's
wrapper (`src/rebaseguard_certify/arb_backend.py`) adds:

* inputs built only from exact integers and rationals (`rational(num, den)`);
* Gaussian quantities from Arb `exp`, `erf`, `sqrt`, `pi` — never from floats;
* a minimum working precision guard (`workprec` raises below 64 bits);
* redundant serialization of every stored quantity as **three** enclosures —
  `ball`, `lower_enclosure`, `upper_enclosure` — so a stored endpoint can be
  re-checked independently of the ball's radius formatting.

The final inequality is evaluated on the **lower endpoint** of the enclosure,
which is the conservative direction.

## 6. Discretization and truncation

| Aspect | Value |
|---|---|
| Candidate degree | 12 (tensor Chebyshev), rounded to dyadics with denominator `2^50` |
| `φ` approximation | Maclaurin, `phi_taylor_order = 50` in `z²/2`, i.e. **degree 100 in `z`** (`residual.py:41-44` builds `2·order+1` coefficients) |
| `φ` uniform error | `ε_φ ≤ 3.7560344489596462e-7`, Lagrange remainder `max_y^(51)/(51!·√(2π))` |
| Gaussian tail truncation | **none** (`"gaussian_tail_truncation": "none"`, `"tail_cutoff": null`) |
| Continuation increments | always in the exact finite interval `[ℓ,u] ⊆ [−5.5, 5.5]` |
| Absorbing tails | exact complete Gaussian moment identities |
| Bernstein subdivision depth | 0 (4 patches suffice) |
| Contraction discretization | 100 cells at `n = 250` — used **only** as a monotone lower envelope, valid on the continuum |

## 7. Tail / error bounds

```text
δ_a ≤ 8.4634602268726275566e-6
δ_b ≤ 2.0616516000703808493e-4
C   = ‖(I−K)^{-1}‖_∞ ≤ 250/0.19 = 1315.789473684210526315789…
μ   = ‖K_z‖ ≤ E|Z| = √(2/π) = 0.797884560802865355879892…

E_a = C·δ_a          ≤ 0.011136131877463983627157…
E_b = C·(δ_b + μE_a) ≤ 11.962516910658127710605800…

b̂(0,0) = 15.8868651640648002043576525466050952672958374023437500…
```

## 8. The exact certified interval

```text
Γ_lower = 3.9243482005828971281857775466050952672958374023437500000000000000000000000000000
Γ_upper = 27.849382127546703280529527546605095267295837402343750000000000000000000000000000
```

(80 significant digits as stored; the trailing digits are exact because
`b̂(0,0)` is an exact dyadic rational and `E_b` is a dyadic-rational bound.)

**Endpoint arithmetic, checked independently in exact decimal (this session).**
The endpoints are *not* `b̂(0,0) ∓ E_b` exactly — the propagation rounds the
radius **outward** to the dyadic value `11.962516963481903076171875`, which
exceeds `E_b = 11.9625169106581277106058001493…` by `5.2823775365566e-8`:

```text
b̂(0,0) − E_b      = 3.9243482534066724937518523972…
Γ_lower (stored)   = 3.9243482005828971281857775466…      ≤  b̂ − E_b   ✓ (wider)

b̂(0,0) + E_b      = 27.8493820747229279149634526959…
Γ_upper (stored)   = 27.8493821275467032805295275466…     ≥  b̂ + E_b   ✓ (wider)

Γ_lower + Γ_upper  = 2·b̂(0,0)   exactly                                ✓ (symmetric)
```

That is the conservative direction — the stored interval strictly **contains**
`b̂ ± E_b` — so the certified statement is if anything slightly stronger than the
raw propagation formula suggests. Margin above 2:
`1.9243482005828971281857775466…`.

## 9. Why `Γ_lower > 2` implies `Γ_CUSUM > 2`

The chain is:

1. `Γ = b(0,0)` exactly, for the unique bounded solution `(a,b)` of the Fredholm
   system (`C-BELL`, `C-EXU` in `02_THEOREM_MAP.md`; existence and uniqueness
   follow from the convergent Neumann series, whose contraction constant
   `β = 0.81 < 1` is itself Arb-certified).
2. `‖b − b̂‖_∞ ≤ E_b` is a **proved** consequence of the residual bound and the
   resolvent bound: `b − b̂ = (I−K)^{-1}(residual)`, so
   `‖b−b̂‖ ≤ C(δ_b + μE_a)`.
3. Therefore `b(0,0) ∈ [b̂(0,0) − E_b, b̂(0,0) + E_b]`, and every quantity in that
   interval is computed with outward-rounded Arb balls, so the printed endpoints
   provably enclose the true ones.
4. `3.9243482… > 2`, and the comparison is performed *in Arb* on the lower
   endpoint (`_require(gamma_lower > 2, …)`, `audit.py:91`), where `>` on an
   `arb` is true only if the relation holds for **every** point of the ball.
5. Hence `Γ_CUSUM > 2`. The margin is `> 1.9243`.

The step that makes this *rigorous rather than heuristic* is (2)+(5): the
candidate `b̂` is never claimed to approximate `b`; only its **exact residual**
is bounded, and the resolvent converts that into a two-sided enclosure.

## 10. Source paths

| Item | Path (relative to project root) |
|---|---|
| Certificate | `rebaseguard-proof/proofs/certificate.json` |
| Audit verdict | `rebaseguard-proof/proofs/audit_report.md` |
| Residual bounds | `rebaseguard-proof/proofs/residual.json` |
| Contraction | `rebaseguard-proof/proofs/contraction_monotone.json` |
| Enclosure | `rebaseguard-proof/proofs/enclosure.json` |
| Candidate | `rebaseguard-proof/proofs/candidates.json` |
| Human derivation | `rebaseguard-proof/proofs/derivation.md` |
| Final report | `rebaseguard-proof/proofs/ReBaseGuard_Certified_Lemma_Proof_Report.md` |
| Auditor | `rebaseguard-proof/src/rebaseguard_certify/audit.py` |
| Arb wrappers | `rebaseguard-proof/src/rebaseguard_certify/arb_backend.py` |

## 11. Reproduction command

```bash
cd /Users/suzhe/ReBaseGuard/rebaseguard-proof
.venv/bin/python -m rebaseguard_certify.audit proofs/certificate.json
# equivalently:  make audit
```

For a full regeneration from the candidate solve onwards:

```bash
make proof     # rebuilds candidate, residual, contraction, enclosure, certificate, then audits
```

## 12. Expected output

```json
{
  "Gamma_lower": "3.9243482005828971281857775466050952672958374023437500000000000000000000000000000",
  "Gamma_lower_gt_2": true,
  "Gamma_upper": "27.849382127546703280529527546605095267295837402343750000000000000000000000000000",
  "artifact_hashes_verified": true,
  "bellman_crosscheck_consistent": true,
  "block_contraction_replayed": true,
  "continuum_residual_replayed": true,
  "mode": "full replay",
  "model_verified": true,
  "resolvent_propagation_replayed": true,
  "schema": "rebaseguard.audit-report.v1",
  "status": "PASS"
}
```

Exit code `0`. Exit code `2` with `AUDIT FAIL: …` on any failure, including
`Gamma lower endpoint is not greater than two`.

## 13. Actual reproduction record (this session)

| Field | Value |
|---|---|
| Date | 2026-08-20 |
| Command | `.venv/bin/python -m rebaseguard_certify.audit proofs/certificate.json` |
| Cwd | `/Users/suzhe/ReBaseGuard/rebaseguard-proof` |
| **Exit code** | **0** |
| Wall time | **129 s** (within the documented 100–420 s window) |
| Mode | `full replay` — `continuum_residual_replayed: true` |
| Result | `status: PASS`, `Gamma_lower_gt_2: true` |
| Interval | **bit-identical to the stored interval** (all 80 digits, both endpoints) |
| `audit_report.md` regenerated | **byte-for-byte identical**, SHA-256 `034ccb1b…2238d7b`, matching the value recorded inside `certificate.json` under `independent_audit.sha256` |
| Pinned artifact hashes | all 5 re-verified OK (`bellman_crosscheck`, `candidates`, `contraction_monotone`, `enclosure`, `residual`) |

What the full replay actually recomputes (from `audit.py`):

* model constants (exact rationals) and target string — enforced;
* SHA-256 of all five pinned artifacts — enforced;
* `certify_monotone_block_contraction(n=250, cells=100, q_safe=19/100, bits=192)`
  re-run from scratch, and `H_250(0) > q_safe` re-checked, `β < 1` re-checked;
* `certify_continuum_residuals(candidates, phi_order=50, subdivision_depth=0, bits=256)`
  re-run from scratch; complete continuum coverage re-checked; the replayed
  `δ_a`, `δ_b` must be **contained in** the stored balls;
* `propagate_residual_enclosure(...)` re-run at 256 bits;
* `gamma_lower > 2` and `gamma_upper > gamma_lower` — enforced;
* the independent finite Bellman value re-checked to lie strictly inside the
  certified interval.

## 14. Determinism

Fully deterministic. Two independent confirmations from this session:

* the replayed 80-digit endpoints are bit-identical to the stored ones;
* the regenerated `audit_report.md` is byte-identical to the stored file.

There is no randomness anywhere on the proof path: no Monte Carlo, no
adaptive tolerance, no wall-clock or hash-seed dependence. (The Monte Carlo
diagnostics of `05_NUMERICAL_VALIDATION.md` are seeded and also reproduce
exactly, but they are outside the trusted base.)

## 15. Known limitations

1. **The certified interval is deliberately wide** (`[3.92, 27.85]`, width ≈ 23.9,
   around a true value near `15.89`). The target was a strict lower bound above 2,
   and the resolvent bound `C = 1315.8` is known to be conservative — the Phase-4D
   audit notes the exact identity `‖(I−K)^{-1}‖_∞ = sup_y E_y[τ] ≈ 465`, i.e. the
   block bound is ~2.7× lossy. This is *free margin left on the table*, not a
   defect, and tightening it is not required for `Γ > 2`.
2. **Not formally verified.** Arb, FLINT, python-flint and CPython are trusted.
   This certificate is `CERTIFIED`, never `MACHINE-CHECKED`. Nothing in the Lean
   development verifies Arb.
3. **The trusted computing base is broader than the Lean kernel**:
   CPython exact integer serialization, python-flint bindings, FLINT/Arb
   arithmetic and transcendental functions, and the project's own symbolic
   polynomial / Bernstein / monotone-contraction / audit-orchestration code.
4. **Parameter-specific.** Valid only for `k = 0.5`, `h = 5`, Gaussian
   innovations, `m = 1`. No closed form for `Γ` and no result for other
   parameters is produced.
5. **The candidate solver is not re-run by `make audit`.** The audit replays from
   `candidates.json`. This is sound — the candidate carries no proof weight, and
   any candidate with a certified residual would do — but a reader wanting to
   regenerate the candidate itself must run `make proof` (≈4–10 min), which
   additionally depends on NumPy/SciPy.
6. **`make audit` rewrites `proofs/audit_report.md` in place.** In this session
   the rewrite was byte-identical, but a reader should be aware the command is
   not read-only.
