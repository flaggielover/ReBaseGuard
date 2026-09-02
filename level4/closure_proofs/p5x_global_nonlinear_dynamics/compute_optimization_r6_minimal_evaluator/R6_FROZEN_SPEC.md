# P5X R6 — Stable Minimal Tail Evaluator: specification repair

`CERTIFIED_NUMERICAL_REPRESENTATION_REPAIR`, successor to R5.
**Frozen before the R6 gate is implemented or run.**

R5 remains permanently `R5_LOCAL_GATE = FAIL`. R6 does not rewrite it, does not
reinterpret it, and does not reuse its verdict. R6 is a *specification* repair:
the R5 mathematics was correct (`Q1` passed at all 33 `k`) and the R5 *gate* was
mis-specified in two independent ways, registered as `D12` and `D13`.

---

## 1. What R6 changes, and what it must not

| item | R5 | R6 | why |
|---|---|---|---|
| production evaluator | `erfcx` folding via `hypgeom_u` for `t > 2` | **the R5 post-hoc `minimal` evaluator**: regime-split `erfc` difference, no exponent folding | `D12` — Arb's `U` loses up to 26 digits on ball arguments and is slow |
| `huge x tiny` | gate criterion `Q4` | **reporting diagnostic only** | `D13` — a `huge x tiny` product is harmless when both factors carry full relative accuracy; `Q4` encoded a mechanism R5 §1 had already measured to be false |
| amplification threshold | `<= 1e12` | **`<= 1e12`, unchanged** | never weakened |
| configuration | R4 `P3` hard case | **identical** | never made easier |

**Unchanged and re-frozen verbatim:** SR recurrence; the `xi`/`zeta`
reformulation; state patch `(17,11)`; `e = 1/4` exact rational; `k = -16..16`;
`bits = 192`; candidate degree `n = 16`; probe candidate `c_ij = 1/(1+i+2j)`;
amplification `= rad(sum_k G_k I_k) * 2^bits`; zero `z`-panels; zero softplus
approximations; the target/recurrence correspondence requirement;
`A = 4581762885148045/8796093022208`; the `D1`-corrected `b_SR = log(1+A)`;
convention A; `m in {1,2,3,5}`; `[0,12]`.

## 2. The frozen R6 production evaluator

```text
a = l + e - k ,  b = u + e - k ,  r2 = sqrt(2)
pref = exp(k^2/2 - k e)

regime B :  b.upper() <= 0   ->  d = [ erfc(-b/r2) - erfc(-a/r2) ] / 2
regime C :  a.lower() >= 0   ->  d = [ erfc( a/r2) - erfc( b/r2) ] / 2
regime D :  otherwise        ->  d = Phi(b) - Phi(a),
                                 Phi(w) = erfc(-w/r2)/2      if w.upper() <= 0
                                 Phi(w) = 1 - erfc(w/r2)/2   if w.lower() >= 0
                                 Phi(w) = (1 + erf(w/r2))/2  otherwise (|w| small)
I_k = pref * d
```

The regime split applies to the **difference**, not to each `Phi` separately:
computing `(1-x) - (1-y)` in the both-positive case re-creates the cancellation
the repair exists to remove. No `erfcx`, no `hypgeom_u`, no exponent folding.

The exponent identity, the regime partition, and the non-cancellation bounds
`W >= 0.99616407018867513833`, `Phi(b)/Phi(a) >= 3.13312` (B/C),
`Phi(b) - Phi(a) >= 0.19078688886760390794` (D) are inherited unchanged from
`SCALED_TAIL_DERIVATION.md` §3-§6 and its lemmas `L-R5.1` .. `L-R5.9`, all of
which apply verbatim to this evaluator (it is regimes B/C/D with the exponent
carried outside instead of folded in — algebraically the same `I_k`).

## 3. Frozen gate `G1`-`G10` (conjunctive; all must pass)

```text
G1  algebraic correspondence: for EVERY k in -16..16 the R6 interval must
    OVERLAP the R4 direct interval.  Rigorous vs rigorous.

G2  rigorous containment: the R6 summed interval must OVERLAP the R4 summed
    interval AND be a SUBSET of it (R6 is the refinement of the same enclosure).

G3  amplification <= 1e12          (unweakened R4/R5 threshold)

G4  z_panels = 0                    (instrumented)

G5  softplus_approximations = 0     (instrumented)

G6  runtime <= 2.0 ms per representative ball patch

G7  no empirical monotonicity

G8  e is an exact rational (ball radius exactly 0)

G9  the xi/zeta recurrence is unchanged: live_limits and the G_k assembly are
    imported from xi_kernel and verified identical to R4's kernel_apply

G10 precision-sweep stability: amplification <= 1e12 at EVERY one of
    192, 256, 320, 384, 512 bits, with the candidate rebuilt at each precision.
    This is what distinguishes a representation repair from a precision patch.

GATE = PASS iff G1 and ... and G10.
```

**Reporting diagnostics, not criteria** (`D13`): `huge_tiny_products`,
`max_abs_log10`, `max_raw_prefactor_log10`, `min_tail_factor`. These are
recorded in the result and may neither pass nor fail the gate.

**Diagnostic-only references** (`D11`): composite Simpson and the `y`-space
brute force are non-rigorous and may neither pass nor fail the gate. Widening
the R6 interval to contain a non-rigorous value remains forbidden.

## 4. Frozen classes

```text
amplification:  >1e12 R6_FAIL | 1e9-1e12 R6_PASS | 1e6-<1e9 R6_STRONG_PASS
                | <1e6 R6_BREAKTHROUGH
runtime:        <=0.75 ms EXCELLENT | <=2.0 ms ACCEPTABLE | >2.0 ms COST_FAIL
projected SR (835*1210*t_patch*2*43/3600):
                >100 R6_NOT_ENOUGH | 25-100 R6_USEFUL | 10-25 R6_STRONG
                | <=10 R6_BREAKTHROUGH
```

## 5. Frozen prediction — and an honest disclosure

The R5 result already **measured** this evaluator as a post-hoc variant:
amplification `1.0027e2`, `t_patch = 0.3885 ms`, flat `1.0027e2 .. 1.0028e2`
across 192-512 bits. R6 is therefore expected to pass, and the prediction is
not independent evidence.

What R6 supplies that R5 could not is **evidential status**: the same numbers
produced under a gate that was correctly specified *before* the run, rather
than as a diagnostic recorded after a failure. The frozen prediction is:

```text
G1..G10 all PASS ; amplification 1.00e2 .. 1.01e2 -> R6_BREAKTHROUGH
t_patch 0.35 .. 0.50 ms -> EXCELLENT ; projected SR 8 .. 12 CPU-h -> R6_BREAKTHROUGH
```

If any of these does not reproduce, that is itself the finding, and the gate
verdict stands as measured.

## 6. No retry ladder

If `G3` exceeds `1e12`, or any other criterion fails, the result is `R6_FAIL`.
The R6 lineage stops, the failure is preserved and diagnosed, and no further
repair is improvised without a new pre-result anchor.
