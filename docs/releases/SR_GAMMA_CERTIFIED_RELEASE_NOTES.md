# ReBaseGuard — SR Gamma Certified

## Release identity

This is a **post-Level-4 optional rigor upgrade**, not a new Level-4 closure.
The historical `rebaseguard-level4-closed` tag, `LEVEL-4-CLOSED` verdict,
18-row ledger, and original release record remain unchanged.

- Upgrade verdict: `SR-GAMMA-CERTIFIED`
- Intended tag: `rebaseguard-sr-gamma-certified`
- Principal certificate commits: `414ec47`, `14984e2`
- Scope: authoritative symmetric two-chart SR detector, `m=1`, full-reuse local
  deterministic mean map

## Certified result

At 192-bit Arb precision, the post-Level-4 certificate gives

```text
Gamma_SR in [5.800391799508442, 28.781285803081492]
lower-endpoint margin above 2 = 3.800391799508442
epsilon_a = 4.504390937831506e-6
epsilon_b = 4.003813425152367e-3
||(I-K)^(-1)||_infinity <= 25000/19
||K_z|| <= sqrt(2/pi)
```

The candidate has degree 16 and exact dyadic coefficients. Both global covers
certify all 1,210 symmetry-reduced patches. The `a` cover uses 96,295
innovation intervals (62–94 per patch, maximum depth 2; worst patch
`p17_m11`). The `b` cover uses 50,947 intervals (37–48 per patch, maximum
depth 1; worst patch `p45_m04`). No sampled-state inference, artificial
Gaussian truncation, or omitted Gaussian tail is used.

Together with the already closed SR derivative theorem, the strict lower bound
establishes local linear repulsion at zero under full reuse for the specified
deterministic conditional-mean map. It does not establish stochastic
operational instability, detector independence, arbitrary-SR validity,
distribution-free validity, production readiness, or a universal transition.

## Independent verification

The independent resolvent auditor, global-`a` auditor, and global-`b`/
propagation auditor pass. The focused certificate tests pass 28/28, the full SR
suite passes 94/94, and the closed-upgrade reproduction is byte-stable.

Run the post-Level-4 certificate independently with:

```bash
bash level4/closure_proofs/sr_derivative/certificate/reproduce_closed_upgrade.sh
```

The distinct historical terminal Level-4 reproducer remains:

```bash
bash level4/final_level4_closure/reproduce.sh
```

## Historical 52-file freeze

The original Level-4 tag contains 52 protected files under
`level4/closure_proofs/sr_derivative/`. The optional certificate adds 40 files,
so the current tracked tree contains 92. The historical verifier correctly
rejects the expanded tree when asked to treat it as the old frozen snapshot.
That is an **expected historical freeze rejection**, not a scientific failure:
all original 52 paths remain byte-identical, the historical guard was not
weakened, and the additive certificate has its own verifier.

See `docs/releases/SR_GAMMA_CERTIFIED_ARCHIVE_MANIFEST.md` and run:

```bash
python3 scripts/verify_post_level4_archive.py
```

## No-new-science boundary

This release integrates and archives an already completed optional rigor
upgrade. It does not change a detector definition, theorem statement, frozen
protocol, dataset, experiment, historical verdict, requirement status,
negative result, or novelty position.
