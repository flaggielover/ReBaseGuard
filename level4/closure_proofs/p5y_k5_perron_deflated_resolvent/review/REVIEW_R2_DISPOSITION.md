# Review r2 — disposition

| item | disposition |
|---|---|
| M1 remainder | new gate **S12** `code/falsify_registry.py`: independent composite Gauss–Legendre quadrature on the exact z-pieces (no `_kernel_polynomials`, no Pair, no φ series, no Bernstein), Chebyshev evaluation by numpy, closed forms by scipy `ndtr`; every certified supersolution inequality (taboo blocks, whole-kernel ARL cells) and every residual bound (λ_mid, λ_cell of d, d', d'') evaluated on ~1.5k states (axes to 5, dense near p+m = 1 and 4, the triangle, the origin) at the ends and centre of each drift set; the gate must flag four planted certifier bugs (no margin, lenient operator, one block end only / point certificate on a wide block, residual bounds ÷10) |
| M2 note | the committed REGISTRY.json is produced by `assemble` (single code_sha256) |
| stale qualification file | regenerated with the current code (qualify 6021643d, consumer 57a67d17); S04 re-runs at the freeze head |
| N1 | `make_protocol.py` pins every repository module the certifier loads on the build host (13 files, listed from `sys.modules` on rebaseguard-vultr-02) and records the runtime (host, Python 3.12.3, python-flint 0.9.0, numpy 2.5.2, venv); S00 checks the runtime against the protocol |
| N2 | `consume` refuses unless the committed QUALIFICATION_RESULT (path in the protocol) has QUALIFIED = true for the same protocol sha256 |
| N3 | S08 reads the committed pre-freeze refusal log; S07 is checked at the evaluation (two runs, byte-identical); runner docstring corrected |
| N4 | all evaluation outputs and ledgers are written outside the namespace and copied in by the seal commit |
| N5 | `run()` refuses a certified, non-empty registry unless called by `consume`; the replay uses an uncertified empty registry |
| N6 | K_UP[3] = 1.5100131 |
| N7 | S01 compares the registry with its committed blob (`git show HEAD:…`) |
| N8 | spec §7 reworded |
