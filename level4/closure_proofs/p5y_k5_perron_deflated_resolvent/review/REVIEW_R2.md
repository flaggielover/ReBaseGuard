# Independent review r2 (disposition review of 849e3a91; same fresh-context reviewer)

**Verdict: PASS_WITH_NOTES, not ready to freeze.** Nothing in 849e3a91 makes the theorem, the consumer rule or the
consumption unsound. `qualify_ad.py` re-run: Q_PASS, MUTATION_PASS, 17/17 mutants, all checks true, 0 violations.

| round-1 item | r2 disposition |
|---|---|
| M1 certifier not qualified | PARTIALLY_RESOLVED — X-B adequate for arithmetic/wiring (re-applies the same formulas, so a wrong formula would be copied); X-A cannot catch a too-lenient Arb step (C_T, τ, Ā are read off w; the float model shares the proposal kernel); the probe shows only that the e-dependence terms are not empty (δ = 0.15 is refused possibly by the κ₂ term alone). Untested: the Arb inequality claims at e ≠ 0, origin removal with derivative weights, the two-end check, κ₂ term, hallow, w ≥ 0, whether env/prop are the right formulas, no certifier mutants. Close by a falsification gate with quadrature independent of `_kernel_polynomials`/Pair on thousands of (x, e) samples, itself qualified by planted certifier bugs. |
| M2 verify ignores REGISTRY.json | RESOLVED (note: `build()` writes a two-entry code_sha256, `assemble` one; re-run `assemble`) |
| citations | RESOLVED |
| qualification padding | RESOLVED (M18 crude; realistic misreads are caught by the `need` refusal; one property filed under refusals) |
| κ docstring | RESOLVED |
| Borel | RESOLVED |
| stale qualification file | PARTIALLY_RESOLVED — regenerate or mark superseded |

New findings: **N1 (MAJOR)** certifier dependencies not pinned (residual.py, polynomial.py, arb_backend.py, fast_range.py,
ra_certifier.py, opnorms.py, intervals.py, cusum_layer1/2, ancestry bootstrap), flint version unrecorded. **N2** consume
checks only the self-declared `certified` flag. **N3** S07/S08 in the spec but not in the runner. **N4** outputs inside the
namespace would trip the guard. **N5** run/forecast/replay execute without the guard. **N6** K_UP[3] = 1.5100130 is 1.3e-10
below κ₃. **N7** S01 compared a file with itself. **N8** spec §7 wording ("cannot fail unless the consumption refuses").
New consumer code (frozen_guard, replay_text, consume) and the spec: sound, fail closed, apart from N1–N3 and N8.
