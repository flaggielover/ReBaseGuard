# ReBaseGuard Level 4 — Stage B

**Rigorous period-2 certificate for the frozen CUSUM at full reuse (`rho = 1`).**

Stage A established a `STRONG-CANDIDATE` nonzero root of `H_1(e) = F_1(e) + e`
near `e* ≈ 1.0367` by Monte Carlo, and Claude Science reproduced it with a
deterministic Bellman solver. Stage B upgrades that from
`CANDIDATE / NUMERICALLY-SUPPORTED` to `RIGOROUS-CERTIFIED`.

| Entry point | Contents |
|---|---|
| [`theorem.md`](theorem.md) | the exact theorem, and lemmas L0–L8 with proofs |
| [`proof_obligations.md`](proof_obligations.md) | every obligation, its status, and the full error budget |
| [`../reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md`](../reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md) | the report |
| [`certificate/period2_certificate.json`](certificate/period2_certificate.json) | machine-readable certificate |
| [`../reports/STAGE_B_LEDGER.md`](../reports/STAGE_B_LEDGER.md) | Stage B ledger (Stage A untouched) |
| [`lean/`](lean/) | optional, non-load-bearing Lean spine |

```bash
bash level4/stage_b/reproduce.sh          # full (~40 min)
bash level4/stage_b/reproduce.sh --quick  # reduced grid, all code paths
```

## What makes this rigorous rather than merely precise

The Stage B brief is emphatic that none of these are the same thing:
high-precision floating point; Monte Carlo evidence; numerical convergence;
interval arithmetic on an approximate discretization; and a genuine enclosure of
the true continuous-state map. Only the last one counts.

**The tempting shortcut is unsound and was rejected.** The Claude Science
Bellman solver could be re-run in Arb in an afternoon. It is midpoint
collocation — `grid.cell(p + z_c - k)` projects the continuum destination onto
a cell using the sub-interval midpoint — so interval arithmetic on it would
certify the discretization, not the map. It is used here only to place grid
cells (which cannot affect validity, only width) and as an independent check.

The scheme actually used has three approximation sources that are **exactly
zero** rather than bounded:

* **quadrature — zero.** The `z` axis is cut at breakpoints and each piece is
  integrated against the Gaussian in closed form. There is no quadrature rule.
* **domain truncation — zero.** The continuation set is contained in
  `(-(h+k), h+k)`, so `|z| > z_cut` is a pure-alarm region integrated to `±∞`
  analytically.
* **iterative solve error — zero.** The one-step map `T` is monotone, so *every*
  iterate of the interval iteration is already a valid bracket. The iteration
  can be stopped anywhere.

What remains — Arb ball radii, the cell partition, float rounding in the
iteration, and the `e`-dependence between mesh points — is enumerated with an
explicit bound in `proof_obligations.md` §4 and in the report's error budget.

## Layout

```text
level4/stage_b/
  theorem.md, proof_obligations.md
  src/
    domain.py            live-region partition (Lemma L1)
    transitions.py       certified one-step segment table
    backends.py          Float (sizing only) and Arb (certified) numerics
    enclosure.py         monotone interval iteration for G
    derivative.py        differentiated operator equation for G'
    killing.py           uniform resolvent bound (Lemma L2)
    mesh_certificate.py  root, uniqueness and multiplier from thin-e solves
    run_stage_b.py       main driver
    cross_check.py       B8 independent routes
    adversarial.py       B9 falsification attempts
    make_certificate.py  assembles certificate, ledger and report
    profile_grid.py      non-rigorous grid placement (validity-neutral)
  tests/                 44 tests
  results/  certificate/  reports/  lean/
  reproduce.sh
```

## Scope

Only `rho = 1`, `m = 1`, `k = 1/2`, `h = 5`, Gaussian innovations. The theorem
concerns the **deterministic** conditional-mean map `F_1`; the noisy recursion
`E_{j+1} = F_1(E_j) + noise`, its invariant law and bimodality are untouched and
remain `OPEN`. Uniqueness is asserted only inside the certified interval.
