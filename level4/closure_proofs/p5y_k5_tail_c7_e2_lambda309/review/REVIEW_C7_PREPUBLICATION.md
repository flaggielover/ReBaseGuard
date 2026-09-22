# C7 pre-publication review — hostile, fresh context

Reviewer scope: the committed tree at `/Users/suzhe/ReBaseGuard-k5c7`, branch `p5y-k5-tail-c7-e2`,
HEAD `511a3c92`. Namespace `level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309`, plus the predecessor
files it reads (C4 certificate, C5 forecast, the frozen CUSUM model).

Method: the three proofs were checked by hand against the docstrings; every rounding direction was
read line by line; every number in `README.md` was recomputed from the modules and compared against
`evidence/certificate/C7_CERTIFICATE.json`, `evidence/phase1/C7_LEDGER.json`,
`p5y_k5_tail_c4_exhaustion/evidence/certificate/C4_CERTIFICATE.json` and
`p5y_k5_tail_c5_exhaustion/evidence/forecast/C5_FORECAST.json`; and the U-provenance mechanism was
attacked with running code. Nothing in the repository was modified except this file; no remote host
was contacted, no ssh, no package installed, no `numpy/scipy/flint/mpmath/sympy/gmpy2` imported, no
state-changing git command run. All probes ran out of tree with `PYTHONINTMAXSTRDIGITS=0`; the
Gaussian primitives were memoised in the probe process only (identical values, no file touched).

`code/c7_certificate.py`, `code/c7_ledger.py`, `code/c7_mutations.py` and `code/c7_b0_audit.py` were
**not** executed as `__main__`, because each of them writes an evidence file.

---

## 1. CRITICAL — the U-provenance mechanism does not close the hole it claims to close

**Files/lines:** `code/c7_theorem.py:384-388` (`g_tail`), `:403-423` (`U_elementary`), `:459-490`
(`certified_U`), `:493-505` (`_resolve_U`, in particular line 499); claim asserted at
`code/c7_theorem.py:439-453` and `README.md:63-69`.

`README.md:61` titles the section "Two structural holes, found and closed before the final
evaluation", and `README.md:67-68` states that "`U` now arrives as a certificate that is re-derived
from its declared source" so that "a mutated or invented `U` cannot survive re-derivation". The hole
is not closed. I obtained a bound from an understated `U` without mutating a single line of the
campaign's code, using only its public API:

```
forged certificate: _tag='C7_CERTIFIED_U/1'  source='elementary'  dependencies=[]
                    a_grid=['-47/20']  derivation='Lemma C7-U at a = -47/20'
                    value = 3.549353697333...
  certified_U floor guard  H/E[V] = 3.297250281519544   -> PASSED
  lambda_lower_tier_k(e_lo, K, H, cert, part_64)  ->  L_lower = 3.619819605670872
  KG1 (> C4 floor 3.297250282)?  True      KG5 (<= A0 4.867216117 and <= ceiling 4.679910340)?  True
  inflation over the published PRIMARY (3.586306093865): +0.9345 %
```

The `U` used, 3.549353697, is **below C7's own certified lower bound on `E[τ′]`** (3.586306094), so
C7's own arithmetic proves it is not an upper bound on `E[τ′]`. The result is a
dependency-set-EMPTY, re-derivation-surviving, kill-gate-clean bound that is unsound. This is the
same species as the `U = 0.1` probe the campaign says it repaired.

Two independent root causes, both of which must be fixed:

1a. **Lemma C7-U's hypothesis `a > 0` is never enforced.** `g_tail` (`:384-388`) evaluates the closed
form `ρ(s−e) + ρ(s+e) + a·[Φ(−(s−e)) + Φ(−(s+e))]`, `s = K + a`, which equals `E[V 1{V>a}]` only for
`a ≥ 0` — the derivation needs `{V > a} = {|z| > K + a}`, and for `a < 0` the event is all of Ω and
`g(a) = E[V]`. Neither `g_tail`, nor `U_elementary` (whose only admissibility test is
`gh >= EV.lo` at `:411`), nor `certified_U` checks the sign of `a`. Negative `a` sweeps `U` smoothly
through the whole window: `a = −2.40 → U = 3.2757` (caught by the floor), `a = −2.35 → U = 3.5494`
(not caught), `a = −2.20 → U = 4.5648`, `a = −1.00 → U = 64.08`.

1b. **Re-derivation does not re-derive the grid.** `_resolve_U:499` reads
`grid = [F(x) for x in U_cert["a_grid"]]` **from the certificate under test**, and re-runs
`certified_U` against that same grid. The gate freezes
`a_grid_for_lemma_C7_U = "{j/4 : j = 8..24}"` (`config/FEASIBILITY_GATES_C7.json:34`) but no code
compares a presented grid with it. The provenance check therefore constrains `source` only — which is
exactly the field the mutation suite tests (M09, M10) and not the field that carries the payload.

**Not affected:** the published numbers. `code/c7_certificate.py:20` and `:54` pass the gate's grid
`[F(j,4) for j in range(8,25)]`, all positive, so the committed `L3_elementary = 3.586306093865...`
is not itself contaminated. The defect is in the mechanism and in the claims made for it.

**To fix:** (i) refuse `a <= 0` in `g_tail`/`U_elementary` (the lemma's own hypothesis); (ii) make
`_resolve_U` re-derive from the **gate's** frozen grid, not from the certificate's, and refuse any
certificate whose `a_grid` differs from it; (iii) add a mutant that tampers with `a_grid` (not just
with `value` and `source`) to the required-detection set; (iv) regenerate the certificate.

## 2. CRITICAL — the gate's non-blindness argument is falsified as stated

**File/line:** `config/FEASIBILITY_GATES_C7.json:88`.

> "Every prospective choice -- the partition, the a-grid, the u0 ladder, the point e, the choice of U
> -- affects only the TIGHTNESS of a bound, never its VALIDITY. … There is no setting of any of them
> that can make an invalid result appear valid."

The handover (`review/HANDOVER_C7_REVIEW.md:22-23`) invites exactly this test. Two of the five
enumerated choices affect validity, not tightness:

- **the a-grid** — finding 1;
- **the point `e`** — validity requires `e` in the closed cell `[19839101/10000000, 2092283/1000000]`
  = `[1.983910, 2.092283]`. `psi_min_lower` only refuses `e <= K` (`code/c7_theorem.py:113`); neither
  `lambda_lower` nor `lambda_lower_tier_k` nor any kill gate tests cell membership. Measured tier-1
  bounds at out-of-cell `e`, with the kill gates applied:

```
  e = 1.90  (outside cell)  tier-1 = 3.642963840   KG5 fires? No
  e = 1.95  (outside cell)  tier-1 = 3.532754133   KG5 fires? No
  e = 1.50  (outside cell)  tier-1 = 4.780763678   KG5 fires? yes (exceeds the 4.679910 ceiling)
  e = 1.00  (outside cell)  tier-1 = 7.132848826   KG5 fires? yes
```

`e = 1.90` produces an invalid bound *larger than the published PRIMARY* and fires nothing. The
gate's parenthetical at `:30` ("ANY point in the closed cell is valid") states the validity condition
correctly; the code does not enforce it, and the non-blindness argument at `:88` asserts that no
setting can do damage, which is false.

**To fix:** either enforce `e_lo <= e <= e_hi` in the theorem entry points (reading `e_lo`/`e_hi`
from `C4_CERTIFICATE.json`, which `c7_common.c4_cell309()` already returns), or rewrite `:88` so that
it claims tightness-invariance only for the choices where it is true (partition, `u0` ladder) and
names the validity side-conditions for the others. The freeze-order disclosure itself is fine; it is
the sweeping "no setting of any of them" that has to go.

## 3. MAJOR — Lemma C7-U Step 0 (`E[τ′] < ∞`) is asserted as certified but is dead code

**Files/lines:** `code/c7_theorem.py:391-400` (`E_tau_prime_finite`), claim at
`code/c7_theorem.py:343-346` and `README.md:55-57`.

`code/c7_theorem.py:346` states: "Both `c` and `p` are chosen and evaluated rigorously below, so the
finiteness is certified, not assumed." `E_tau_prime_finite` has **no caller anywhere in the tree**
(`grep -rn E_tau_prime_finite code/ evidence/ config/ README.md` matches only its own definition and
docstring). No `c` is fixed by the gate; no `p_lower`, `geometric_stages` or
`E_tau_prime_upper_crude` value appears in any evidence file. `README.md:56` repeats the claim.

This matters. Step 3 of the lemma divides by `E[V] − g(a)` after substituting Wald; that
rearrangement is invalid if `E[R] = ∞`, and `E[R] < ∞` comes only from `E[τ′] < ∞`. So the PRIMARY
bound's advertised *empty* dependency set currently rests on a step that is proved in prose in a
docstring and executed nowhere. (The mathematics is correct and the computation is cheap — for any
`c > 0`, `E[τ′] <= (⌈H/c⌉+1)/P(V>c)`; the `⌈·⌉+1` pad correctly covers the `H/c ∈ ℤ` case, and
`n = -((-H) // c) + 1` is exact.)

**To fix:** fix a `c` in the gate, call `E_tau_prime_finite` from `certified_U`/`U_elementary`, refuse
if `p_lower <= 0`, and emit the resulting crude bound into the ledger and the certificate. Then the
sentence at `:346` becomes true.

## 4. MAJOR — four of the thirteen required-detection mutants survive, and the recorded reason is numerically false

**Files/lines:** `code/c7_mutations.py:126-135` (classification), `:128` (threshold);
`evidence/mutations/C7_MUTATIONS.json` `mutants[0..3]`.

M01 (`E[V]` from below), M02 (`r` from above), M03 (`f` from below), M04 (`q` from below) are the four
mutants that test the *rounding directions* — the stated organising principle of the suite
(`code/c7_mutations.py:6-9`). All four inflate the bound and none is detected. They are recorded as
`UNSOUND_BELOW_GRID` with the detail "formally the wrong rounding direction, but the effect is below
the 2^-320 grid resolution and cannot reach any reported digit". The first half of that sentence is
false:

| mutant | recorded `inflation_percent` | absolute change | in units of the 2^-320 grid (4.6817e-97) |
|---|---|---|---|
| M01 | 5.479219351529656e-94 | 1.966e-95 | **≈ 42** |
| M02 | 5.2835329461178825e-93 | 1.896e-94 | **≈ 405** |
| M03 | 1.3045760360784896e-95 | 4.682e-97 | ≈ 1 |
| M04 | 6.522880180392447e-95 | 2.341e-96 | ≈ 5 |

(The `E[V]` interval's own relative width is 5.557e-96, which is what M01 measures.) The threshold
used at `:128` is `F(1, 10) ** 60` — a relative `1e-60`, roughly `10^37` times coarser than the grid
it is named after. Any mutant inflating the bound by up to `1e-60` relative would be silently
declassified by this rule.

Consequence: `MUTATION_CLASS = "PASS"` and `undetected = []` are written to
`C7_MUTATIONS.json`, and `code/c7_certificate.py:77-78` (KG8) consumes exactly those two fields. A
kill gate therefore reads PASS while four required-direction mutants formally survived. The suite
supplies **no** evidence on item E.

Only the second half of the sentence is true — the effect cannot reach a reported decimal digit. That
is a much weaker statement and should be the one recorded, with the class renamed accordingly (e.g.
`UNSOUND_BELOW_REPORTED_PRECISION`), the threshold tied to something real, and the four mutants
listed in the outcome summary rather than folded into `undetected = []`.

I verified the rounding directions by hand instead; see the "what is correct" section — they are
right.

## 5. MAJOR — M11 tests a copy of the guard it claims to test

**Files/lines:** `code/c7_mutations.py:166-167`, `:218-227`.

`_force_low_U` never calls `certified_U`. It recomputes `floor = H/E[V]` inline, multiplies it by
`9/10`, and raises its own `TheoremRefusal` with a message paraphrasing the real guard. The suite then
records `M11 … DETECTED_BY_RULE` for a rule the mutant wrote for itself. The real guard
(`code/c7_theorem.py:483-487`) is never exercised by any mutant.

This is precisely the failure mode the module docstring at `:11-15` says the suite exists to avoid
("the error C5 made when it measured a mutation against manufactured cells"). Line 167 also carries
dead code: `lambda: T.certified_U("registry", E_LO, K, H) if False else _force_low_U(...)`.

**To fix:** drive the real path — e.g. present a certificate whose `source` is `"elementary"` with a
crafted `a_grid` (finding 1) and assert that `certified_U`/`_resolve_U` refuses it. As committed, that
mutant would pass, which is the point of finding 1.

## 6. MAJOR — the acknowledged `coverage_limitation` is narrower than reality

**File:** `evidence/mutations/C7_MUTATIONS.json` → `coverage_limitation` (written at
`code/c7_mutations.py:190-204`). Item I asks whether the admitted gap is stated accurately. It is
understated in three ways.

(a) It frames the gap as reachable only by "a mutation of a U DERIVATION ITSELF … because
re-derivation re-runs the mutated code". Finding 1 reaches the same place with **no mutation at
all**, through an input the API accepts and the gate does not bind. The residual gap is not a
code-integrity gap; it is an interface gap.

(b) The stated range, "`[3.297250281519544, 4.679910339516997]`", takes Lorden's `U` as the top. The
`registry` `U` is `4.867216116723177` (`C7_CERTIFICATE.json` → `bounds.L3_registry.U_used`), so a
mutation of the registry derivation spans a strictly wider range than admitted.

(c) "inflates the bound by a small amount" is never quantified. Measured, at the certificate's own
`N = 64` partition and `e = e_lo`, holding everything else fixed:

```
  U = 5.9372 (elementary, published)   L = 3.586306094    +0.0000 %
  U = 4.8672 (registry)                L = 3.597941639    +0.3244 %
  U = 4.6799 (lorden)                  L = 3.600337620    +0.3913 %
  U = 4.0000 (the JSON's own example)  L = 3.610955979    +0.6873 %
  U = 3.5494 (finding 1's forgery)     L = 3.619819606    +0.9345 %
  U = 3.2973 (at the floor guard)      L = 3.625700692    +1.0985 %
```

The maximum undetectable inflation, +1.0985 %, is **larger than C4's entire margin over the C5-T
critical `A0`** (0.9440 %) — i.e. larger than the quantity C7 exists to make robust. "Small" is the
wrong word for it. State the number.

## 7. MAJOR — the B0 compute-boundary walk covers 4 of the 7 modules and cannot be re-run

**Files/lines:** `code/c7_b0_audit.py:89-134`, `:28`, `:32`, `:153-157`;
`evidence/b0/C7_B0_AUDIT.json` → `checks[11].detail.imports_per_module`;
`code/c7_certificate.py:88` (KG9b). Claim at `config/FEASIBILITY_GATES_C7.json:26`: "asserted by
`code/c7_b0_audit.py` via an ast import walk, not merely declared".

The committed audit's import walk covers `c7_b0_audit.py`, `c7_common.py`, `c7_gaussian.py`,
`c7_theorem.py` — and nothing else. `c7_ledger.py`, `c7_mutations.py` and `c7_certificate.py` did not
exist when B0 ran, so the module that produces the certificate has never been walked. `KG9b`
nevertheless reads `B0_CLASS == "PASS"` out of that stale file.

The audit also cannot be regenerated to cover them: `chk(1)` pins the branch, `chk(2)` pins HEAD to
`f494416f` (HEAD is now `511a3c92`), and `chk(16)` asserts that
`config/FEASIBILITY_GATES_C7.json` and `evidence/certificate/C7_CERTIFICATE.json` do **not** exist —
both are now committed. So the handover's repair promise ("the certificate will be regenerated after
the fix") cannot extend to B0 without rewriting the audit's own checks. Three of sixteen B0 checks are
now structurally unreproducible.

Secondary, and smaller: the walk is evadable in principle. `__import__("numpy")` is an `ast.Call`,
not an `ast.Import`, and is invisible to `:104-109`; and `from subprocess import run` followed by
`run([...])` passes both check 12 (`subprocess` is in `STDLIB_ALLOWED`, `:91`) and check 13, because
the argv0 scan at `:111-112` only matches `subprocess.<attr>(...)` on an `ast.Name` receiver.

**Verified independently, by hand:** the compute-boundary counters are *true*. All seven modules
import only `__future__`, `fractions`, `json`, `pathlib`, `sys`, `hashlib`, `ast`, `subprocess` and
each other; no `__import__`/`importlib`/`exec`/`eval` appears anywhere; the only `subprocess` use is
`c7_common.git()` launching `git`; nothing reads an operator, a kernel or a K1 record. The finding is
that the *mechanism* is weaker than the gate advertises and is no longer re-runnable, not that the
boundary was breached.

## 8. MINOR — `README.md:26` overstates what survives if the Arb/FLINT surface is doubted

`README.md:20-26` says the PRIMARY bound clears the critical `A0` by 9.7933 % "without depending on
the Arb/FLINT certification surface at all … and that conclusion survives even if the operator
certification surface is doubted entirely." The **bound** is surface-free; the **conclusion** is not.
The margin is measured against `critical_A0_C5T = 3.266415728267196`, read from
`p5y_k5_tail_c5_exhaustion/evidence/forecast/C5_FORECAST.json` — an operator-level quantity. If that
surface is doubted entirely, the comparison target is gone and there is no exclusion margin to state.

**To fix:** narrow the sentence to the bound ("the *bound* survives; the margin statement still needs
C5-T's critical `A0`"). The gate's own `forbidden_conclusions` already includes "that the Arb/FLINT
surface is validated or invalidated by C7", so this is a wording repair, not a re-derivation.

## 9. MINOR — `baseline_C4.margin_percent` is silently re-based, and `README.md:23` inherits it

`C7_CERTIFICATE.json` → `baseline_C4.margin_percent = 0.9439874105892059` is C4's floor measured
against **C5-T's** critical `A0`. C4's own published figure is
`C4_CERTIFICATE.json#/cells/309/slack_over_critical_percent = 2.5827057582567217`, against its
frozen-clause critical `A0` 3.2142360226778806. The field name does not disclose the re-basing; a
reader diffing the two certificates will see a 2.58 vs 0.94 mismatch. (The README table header does
disclose it — "margin over the C5-T critical A0" — so the README table is fine.)

`README.md:23` then reads "C4's exclusion of cell 309 tolerated a 0.94 % adverse move in the critical
A0, and a single successor … had already consumed 63 % of C4's original margin". The 0.94 % *is* the
post-C5-T residue; C4 as published tolerated 2.58 %. The two clauses describe the same event in the
wrong order. Not false, but compressed to the point of misleading.

**To fix:** rename the certificate field (`margin_percent_over_C5T_critical_A0`) or carry both
numbers; reorder the README sentence.

## 10. OBSERVATION — `ψ` *is* decreasing; item G's "genuinely unclear" is too pessimistic

`README.md:75-77` says `psi_exact` is used only as a guard "because using it directly would require
`ψ` to be decreasing, which is *not* proved: the weights in its mixture shift toward the larger term
as `u` grows, so the monotonicity is genuinely unclear rather than merely unproved." The weight
observation is correct (`1−w = f/(1+f)` falls as `s` rises, shifting mass onto the larger `r(s−e)`),
but the conclusion is too weak on two counts.

**An exact scalar criterion exists.** With `a = Φ(−(s−e))`, `b = Φ(−(s+e))`, `A = ρ(s−e)`,
`B = ρ(s+e)`, `s = K + u`, differentiating `ψ = (A+B)/(a+b)` and using `ρ′(t) = −Φ(−t)` gives

```
    ψ′(u) = [ (A+B)(φ(s−e)+φ(s+e)) − (a+b)² ] / (a+b)²,
    so  ψ′ < 0  ⟺  ψ(u) · h_{|Y|}(s) < 1,   h_{|Y|}(s) = (φ(s−e)+φ(s+e)) / (a+b).
```

Evaluated in C7's own rigorous interval arithmetic at all 65 knots `u = j·H/64`, `j = 0..64`, the
criterion holds everywhere, with the upper endpoint of the interval:

```
   u = 0.0000  ψ = 1.617369585   ψ·h ≤ 0.260326
   u = 1.2500  ψ = 0.888986897   ψ·h ≤ 0.582916
   u = 2.5000  ψ = 0.521946222   ψ·h ≤ 0.802776
   u = 3.7500  ψ = 0.344790394   ψ·h ≤ 0.900206
   u = 5.0000  ψ = 0.250478251   ψ·h ≤ 0.943443      (worst case, at u = H)
```

**And most of the range is provable outright.** `|Y|` with `Y ~ N(e,1)` has density proportional to
`e^{−y²/2} cosh(ey)`, whose log second derivative is `−1 + e² sech²(ey)`, negative exactly when
`cosh(ey) > e`, i.e. for `y > arccosh(e)/e = 0.659128` at `e = 1.9839101`. A log-concave density
implies IFR implies DMRL, so `ψ` is decreasing for `s ≥ 0.659128`, i.e. for `u ≥ 0.159128` — 96.8 %
of `[0,H]`. Only `u ∈ [0, 0.159128)` needs a separate argument, and there the criterion has margin
`≥ 0.72`, comfortably closable by the interval arithmetic already in `c7_gaussian.py`.

**What it is worth:** little. Substituting `psi_exact(u_j).lo` for `psi_lo_at(u_j)` in the `N = 64` LP
raises `E[R]` from `0.4383285884695285` to `0.4413871947681776` and the PRIMARY bound from
`3.586306094` to `3.588323092`, i.e. **+0.0562 %**. No verdict changes. Report it as tightening that
is available and was declined for a stated reason, not as a defect — but the stated reason should not
be "genuinely unclear".

## 11. OBSERVATION — item F: the `ψ` guard is not circular, but it is not independent either

`code/c7_theorem.py:508-527` (`psi_exact`) claims it shares "no code path with `psi_lo_at` beyond the
Gaussian primitives". At the function level that is true (`psi_exact` goes through `rho1`,
`psi_lo_at` through `hazard`/`mrl`/`f_ratio`), and the guard demonstrably catches the endpoint class
of error — M06 refuses with `psi_lo[0] = 1.6151230064930002 exceeds psi(0.3125) <= 1.3966430082797825`.
But `r(t) ≡ ρ(t)/Φ(−t)` identically, so the two expressions are the same two primitives rearranged;
any systematic error in `G.Phi` or `G.phi` is invisible to both, and the committed tree contains **no
test of those primitives against known values** anywhere.

I checked them independently (not a finding against the tree, a gap in it):

```
   Φ(0)     = [0.5, 0.5]                                     expected 0.5
   Φ(1)     = 0.8413447460685429                             expected 0.8413447460685429
   Φ(−1.96) = 0.024997895148220435                           expected 0.024997895148220435
   φ(0)     = 0.3989422804014327                             expected 0.3989422804014327
   Φ(−7)    = [1.279812543885835e-12, 1.279812543885835e-12] expected 1.2798125438858352e-12
```

Correct. Adding four such assertions to the tree would cost nothing and would close the one class of
error neither `psi_exact` nor any mutant can see.

## 12. MINOR — M07 and M13 are detected by the wrong guard

`code/c7_mutations.py:158-159` (M07, "threshold confusion: H := C_CUSUM = 11/2") and `:170-171`
(M13, "partition not strictly increasing") both refuse with `"partition must end exactly at H"` —
the same message as M12 — because `pipeline` checks `us[-1] != H_` at `:44-45` before it reaches
either the `K_+H_ != 11/2` check (`:48`) or the strict-increase check (`:46`). Neither mutant
exercises the guard it is named for. They are recorded as `DETECTED_BY_RULE`, so the "13/13 required
detection" count overstates coverage by two. (`KG7`'s own `K + H == 11/2` test at
`code/c7_certificate.py:39` is genuine and does hold.)

## 13. OBSERVATION — dead code and cosmetics

- `code/c7_theorem.py:205-230` `lambda_lower_tier2` has no caller, although the gate documents a
  `u0_ladder_for_tier2` for it (`config/FEASIBILITY_GATES_C7.json:35`).
- `code/c7_certificate.py:115-116`: `"exclusion_test": c4["gate_sha256"] and "<string>"` — an
  accidental `and` that evaluates to the string only because the sha is non-empty. If it were ever
  empty the field would silently become `""`.
- `code/c7_mutations.py:109`: the analytic ceiling is hard-coded as
  `F("4679910339516997")/F(10)**15` rather than computed, so a change in the ceiling would not
  propagate into the suite's `caught` test.
- `code/c7_mutations.py:184`: `"mirror_equivalence_asserted": True` is a literal, which
  `code/c7_certificate.py:79` (KG8b) then checks. It is only reachable when the mirror did match
  (`:103-106` returns early otherwise), so it is sound but vacuous as a gate.
- `code/c7_theorem.py:241-242` asserts `Σ_j m_j = 1` over subintervals `(u_{j−1}, u_j]`, which cover
  `(0,H]` but not `{0}`. `μ({0}) = 0` because `D_n = 0` needs `W_{n−1} = H` exactly and `V` has a
  continuous part, so the claim holds; the text does not say why.

---

# Addendum — the tree moved during this review

Findings 1–13 were made against HEAD `511a3c92`. While I was writing, the worktree advanced to
`a6c2855b` ("p5y: K5 C7 phase 13 — governance fact verification, PASS with gate ordering disclosed")
and acquired uncommitted changes. I re-diffed: **nothing I reviewed changed**
(`git diff --stat 511a3c92 HEAD` over the namespace shows only two added files), so findings 1–13
stand verbatim. The new material introduces four more.

Current state as I finish: HEAD `a6c2855b`; `code/c7_factcheck.py` and
`evidence/governance/HANDOVER_FACT_VERIFICATION.json` **modified in the working tree** on top of that
commit; `OPEN_NOTES_DISPOSITION_C7.md` **untracked**. What I read may not be what is published.

## 14. MAJOR — Monte Carlo, which the frozen gate forbids outright, was run and its result is carried in the namespace

**Files/lines:** `OPEN_NOTES_DISPOSITION_C7.md` → N3, against
`config/FEASIBILITY_GATES_C7.json:23`.

The gate's `compute_boundary.forbidden` list contains `"Monte Carlo of any kind"` — unconditionally,
with no "as evidence" qualifier. N3 reports: "Monte Carlo puts `E[τ′]` at 3.98842 ± 0.00050", and
describes "an independently coded simulator". The note argues the simulation "is a cross-check and is
not evidence … no C7 conclusion rests on it", which I believe — the figure is consistent with the
bracket C7's own certified arithmetic gives (`E[τ′] ∈ [3.586306, 4.679910]`), and nothing in the
certificate depends on it. But a frozen gate's prohibition is not waivable after the fact by the
campaign that froze it, and the certificate simultaneously declares
`SCIENTIFIC_KERNEL_EVALUATIONS: 0` and `TOOLCHAIN_PROVISIONED: 0`. A reader has to reconcile those
declarations with a simulator that was written and run. `KG9` cannot see the discrepancy because it
reads the declared counters out of the B0 artifact, not the tree.

**To fix:** either drop N3 and the simulator entirely, or amend the gate before publication and
declare the activity in the compute boundary rather than in a note. Do not publish the current
combination of "0 kernel evaluations / Monte Carlo of any kind is forbidden" and "Monte Carlo puts
E[τ′] at 3.98842".

## 15. MAJOR — the new fact-verification artifact is already stale, and its PASS is much narrower than its stated purpose

**Files/lines:** `code/c7_factcheck.py:1-15` (docstring), `:27` (`NUM`), `:77-84` (check 1);
`evidence/governance/HANDOVER_FACT_VERIFICATION.json`.

(a) **Stale.** `prose_scanned` lists three files. The tree now also contains
`OPEN_NOTES_DISPOSITION_C7.md`, which `C.NS.rglob("*.md")` picks up. Re-running check 1 against the
present tree yields eleven `PROSE_FIGURE_UNBACKED` findings from that file alone — `0.0005`,
`0.078125`, `0.15625`, `0.159111601`, `0.159112`, `0.441387195`, `0.659111601`, `1.04797`,
`1.048343`, `3.588323092`, `3.98842` — so `FACT_CHECK_CLASS` would be `REFUSE`, not `PASS`. The
committed artifact's PASS describes a tree that no longer exists. (Same class as finding 7: an
artifact whose verdict cannot be reproduced at the publication HEAD.)

(b) **Narrower than advertised.** The docstring at `:10` says "every number of >= 6 significant
digits asserted in a prose file", but the regex at `:27` requires **five or more decimal places**.
Every percentage in `README.md`'s headline table — 4.9748, 5.9658, 8.7666, 9.7933, 9.1195, 10.1495,
9.1921, 10.2229 — and C4's 0.9440 have four decimals and are never scanned. (I checked all of them
by hand against the certificate; they are correct. The gap is in coverage, not in the numbers.)

(c) **It cannot see the failure mode it names.** `code/c7_factcheck.py:3-5` says the module exists
because the programme has "repeatedly shipped statements its own tree contradicted: a repair recorded
as landed that had not". That is precisely finding 3 (`E_tau_prime_finite` is dead code while
`code/c7_theorem.py:346` says the finiteness "is certified, not assumed"), and finding 4 (a
numerically false justification in `C7_MUTATIONS.json`), and finding 6. No check in the module can
reach any of them: checks 1–5 compare numerals, predecessor baselines, commit order, self-shas and
byte-equality of inherited code — never a behavioural claim. `FACT_CHECK_CLASS: PASS` with
`findings: []` must not be read as clearing the prose.

Check 1's *rounding-based* backing test (`:71-75`, half-ULP at the quoted precision) is a genuine
improvement over prefix matching and is correctly implemented. Check 5 is the best thing in the
namespace — see the positives below.

## 16. MAJOR — the new module would make the campaign's own B0 audit REFUSE

**Files/lines:** `code/c7_factcheck.py:20` (`import re`) against
`code/c7_b0_audit.py:91-93` (`STDLIB_ALLOWED`) and `:124-128` (check 12).

`c7_factcheck.py` imports `re`. `re` is not in `STDLIB_ALLOWED`, not in `NUMERICAL` and not in
`NETWORK`, so `unexpected = ['re']` and check 12 fails → `B0_CLASS = "REFUSE"` → `KG9b`
(`code/c7_certificate.py:88`) fires → `C7_CLASS = "REFUSED"`. The only reason this does not happen is
that the committed `C7_B0_AUDIT.json` is frozen from before the module existed (finding 7). The
campaign has added a module whose import, if its own audit were re-run, would refuse the campaign.

`code/` now holds eight modules and the committed walk covers four. Finding 7's remedy has to add
`re` to the allowlist deliberately (it is harmless) rather than by accident.

## 17. OBSERVATION — `ψ` monotonicity was reached independently, but the README still says otherwise

`OPEN_NOTES_DISPOSITION_C7.md` → N1 reaches finding 10 independently and with the same arithmetic:
`arccosh(e)/e = 0.659111601`, hence `u ≥ 0.159111601`, exactly two of the 64 knots unresolved; `E[R]`
0.438328588 → 0.441387195 (+0.6978 %); bound 3.586306094 → 3.588323092 (+0.0562 %). My own figures,
computed before I saw that file, agree to every digit, and my `ψ·h ≤ 0.943443` at `u = H` is the same
number as its `max ψ′ = −0.0566`. Good corroboration, and the "NOT TAKEN" disposition is a reasonable
call.

But the disposition file is **untracked**, and `README.md:75-77` — which is what a reader sees —
still says the monotonicity is "genuinely unclear rather than merely unproved". Either commit the
disposition and amend the README, or leave neither.

---

## What I checked and found correct

These are positives, recorded so a later reviewer does not redo them.

**Item J — every published number reproduces exactly.** Recomputed from the modules at `e = e_lo`,
`K = 1/2`, `H = 5`, `N = 64`, gate grid:

| bound | recomputed | matches `C7_CERTIFICATE.json` | matches `C7_LEDGER.json` | README |
|---|---|---|---|---|
| L1_tier1 | 3.461283496693919 | exact rational identical | exact rational identical | 3.461283497 / +4.9748 % / 5.9658 % ✓ |
| L3_elementary | 3.5863060938653875 | identical | identical | 3.586306094 / +8.7666 % / 9.7933 % ✓ |
| L3_registry | 3.5979416389974226 | identical | identical | 3.597941639 / +9.1195 % / 10.1495 % ✓ |
| L3_lorden | 3.6003376198767163 | identical | identical | 3.600337620 / +9.1921 % / 10.2229 % ✓ |

The three `U_used` values and all three `E_R_lower` values match the certificate as exact rationals.
`C4`'s floor `3.297250281519544` and its exact rational match
`C4_CERTIFICATE.json#/cells/309/lower_bound_E_a_tau`; `critical_A0_C5T = 816603932066799/250000000000000
= 3.266415728267196` matches `C5_FORECAST.json`; the C4 margin 0.9440 %, the margin multiple
10.3744 (README "10.37×"), `C5T_consumed_of_C4_margin_percent = 63.4497` (README "63 %"), the ceiling
4.679910339516997 (README "4.679910340") and the headroom 30.4939 % (README "~30 %") all reproduce.
The certificate's self-sha256 verifies, `gate_sha256` matches the frozen gate file, and
`model_sha256` matches `cusum_layer1.py`. `README.md:69`'s "That floor evaluates to
3.297250281519544 — exactly C4's published bound" is exactly true: the `Fraction` returned by
`certified_U`'s floor is `==` C4's committed rational, not merely close. **No mis-transcribed number
was found anywhere.** This is the first thing I looked for and it is clean.

**Item A — Theorem C7-E2 is correct.** `E[R] = Σ_n E[1{τ′≥n} g(D_n)] = Σ_n E[1{τ′≥n} ψ(D_n) p(D_n)]`,
and the total mass is `Σ_n E[1{τ′≥n} p(D_n)] = Σ_n P(τ′=n) = 1` because
`{τ′=n} = {τ′≥n} ∩ {V_n > D_n}` and `{τ′≥n} = {W_{n−1} ≤ H}` is `F_{n−1}`-measurable. `μ` is a
genuine probability measure on `[0,H]`; `D_n ∈ [0,H]` on `{τ′≥n}`. Setting `ψ_min = 0` recovers C4.
The decomposition `ψ(u) = w·r(s−e) + (1−w)·r(s+e)` and the drop to `r(s−e)/(1+f(s))` are both
correct for `V = (|z|−K)⁺`, `s = K+u`.

**Item B — both monotonicity facts hold on all of ℝ; the positivity-guard removal is sound.**
(M1) `r′ = h(h−t) − 1 < 0` ⟺ `h(t) < (t+√(t²+4))/2`, Sampford's Mills-ratio bound, valid for every
real `t`. (M2) `d log f/ds = h(s−e) − h(s+e) < 0` needs only `h` increasing, and
`h′ = h(h−t) > 0` everywhere because `h(t) > t` ⟺ `r(t) = E[Z−t | Z>t] > 0`. So `psi_lo_at`'s comment
at `:193-197` is right: no positivity hypothesis on `t = K+u−e` is needed, and the residual check
`r.lo > 0` is the correct one to keep.

**Item C — the multi-tier LP and its greedy minimiser are correct.** Writing `T_i = Σ_{j>i} m_j`, the
objective is `c_1 + Σ_{i=1}^{k−1} (c_{i+1} − c_i) T_i` with `c_j = psi_lo(u_j)` non-increasing, so
every coefficient `(c_{i+1} − c_i) ≤ 0` and the minimum takes each `T_i` as large as the constraints
allow, `T_i = q_i`; feasible because `q` is non-increasing (checked at `:296-297`) and clipped at 1
(`:295`), and `m` telescopes to 1 (checked exactly at `:314-316`). Using `q` from **above** enlarges
the feasible set and therefore lowers the LP value — the conservative direction, as the docstring
says. Constraint (i) is valid because `psi_lo(u_j)` bounds `ψ` below on all of `[0, u_j]`, which
contains `(u_{j−1}, u_j]`. Refinement can only raise the bound. The `k = 1` edge case at `:301-306` is
handled correctly and `KG4` does reproduce tier 1 exactly.

**Item D — the independence step and the rearrangement are correct.**
`{τ′ ≥ n} = {S_{n−1} ≤ H} ∈ σ(V_1,…,V_{n−1})`, independent of `V_n`, so
`Σ_n E[1{τ′≥n} V_n 1{V_n>a}] = E[τ′] g(a)`; `R ≤ V_{τ′} ≤ a + V_{τ′}1{V_{τ′}>a}`; substituting
Wald and dividing by `E[V] − g(a) > 0` gives `E[R] ≤ (aE[V] + Hg(a))/(E[V] − g(a))`. The only defect
is that `E[τ′] < ∞`, which the division needs, is never executed — finding 3.

**Item E — every rounding direction in the committed path is sound.** Read line by line:
`psi_lo_at` uses `r.lo` and `f.hi` and returns `.lo` (`:198-202`); `p_upper` returns `.hi` (`:187`);
`q = min(1, p_upper·U)` takes `q` from above, which is the direction the bound decreases in (`:295`);
`psi` from below (`:280`); `ER` is exact rational arithmetic on exact rationals, no rounding
(`:318`); `L = (Iv(H+ER)/Iv(EV.hi)).lo` needs `E[V]` from above and takes it (`:324`).
In `U_elementary`, `F(EV,g) = (aEV + Hg)/(EV − g)` is *decreasing* in `EV` (`∂F/∂EV = −(a+H)g/(EV−g)²`)
and *increasing* in `g`, so the code's use of `EV.hi` in the numerator, `EV.lo − gh` in the
denominator and `gh` from above all push `F` **up** — the safe side for an upper bound on `E[R]` —
and `.hi` is taken (`:414-416`); `U = ((H+ER)/EV.lo).hi` (`:416`); the admissibility test `gh >= EV.lo`
(`:411`) is the conservative form of `g(a) < E[V]`. `U_lorden` uses `EV2.hi/EV.lo` and `.hi`
(`:430-431`). `certified_U`'s floor uses `H/EV.hi` and `.lo` (`:483`), the correct direction for a
*lower* bound on `E[τ′]`. **I found no endpoint choice that inflates the final value.**

**The Gaussian layer is rigorous.** `_out` rounds correctly for both signs (`Fraction` denominators
are positive, so `divmod` floors); `Iv` rounds outward on every operation and refuses division by an
interval straddling zero; `_atan_small` and `_erf_integral` use first-omitted-term bounds with a
run-time check that the magnitudes really are decreasing over the tail relied on (and the ratio
`t²(2n+1)/(2(n+1)(2n+3))` is itself decreasing in `n`, so `nxt <= mags[-1]` does extend to the whole
omitted tail); `exp_neg`'s tail bound `y^{N+1}/(N+1)! · 1/(1−y/(N+2))` is correct and guarded;
`sqrt_iv` brackets correctly because `(r+1)² > ⌊x·2^{2S}⌋ ≥ x·2^{2S} − 1` forces `(r+1)² > x·2^{2S}`;
`E_excess`'s two-sided formula is right and disjointness needs only `K > 0`. Values verified against
textbook `Φ`/`φ` at five points (finding 11).

**`H = 5` is the correct alarm level, independently verified.** The gate's `KG7` inherits this from
C4 rather than re-deriving it, so I checked the frozen model: `cusum_layer1.py:115` sets the
continuation region to `z ∈ (m − C_CUSUM, C_CUSUM − p)`, which is exactly
`{max(0, p+z−K) ≤ H} ∩ {max(0, m−z−K) ≤ H}` with `H = C_CUSUM − K = 5`. So `C_CUSUM = 11/2` is the
innovation bound and `H = 5` is the threshold on the statistic; C7 uses the right one, and the
mis-taking `KG7` guards against would indeed inflate the bound unsoundly.

**Item K — the compute boundary was in fact respected.** 0 new-real, 0 kernel evaluations, 0 remote
hosts, guard DENY, `EXECUTION_AUTHORIZED` false. Hand-verified across all seven modules (finding 7
concerns the audit mechanism, not the boundary). The predecessors are tracked and unmodified; `git
status` is clean.

**The inherited Gaussian is genuinely C4's adjudicated code.** `code/c7_factcheck.py:141-148`
(check 5) asserts that `code/c7_gaussian.py` equals
`p5y_k5_tail_c4_exhaustion/code/c4_rigorous_gaussian.py` modulo the `c4_` → `c7_` rename. I verified
that independently: the byte-equality holds, and `sha256(c7_gaussian.py) =
bd73b5b46766ca4272cdf5db3c7258e45e81599e712f9984cd03a5455cea9815` matches
`inherited_gaussian_sha256` in the artifact. So the interval arithmetic every C7 bound rests on is
the arithmetic C4's adjudicator already accepted, unaltered. This is the strongest provenance fact in
the namespace and the one check in `c7_factcheck.py` that does real work.

**The gate ordering is reported truthfully.** `HANDOVER_FACT_VERIFICATION.json` → `gate_ordering`
states B0 `BEFORE_GATE`, ledger `SAME_COMMIT_AS_GATE` (and produced before it in wall-clock order),
mutations and certificate `AFTER_GATE`. That matches the commit history (`166224bb` carries the gate
and the ledger, `83299d66` the mutations, `511a3c92` the certificate). The freeze-order deviation is
disclosed in three places and nowhere dressed up.

**Item L — no forbidden conclusion is drawn.** `README.md:28-32` explicitly states cell 309 is not
closed, that the exclusion is about the deterministic operator-level route, that K5 remains PARTIAL
with m = 5 open on `[305,309]`, that no other cell's status changes, that the guard stays DENY and the
R-stage is not authorised. The certificate carries the gate's `forbidden_conclusions` verbatim and
scopes phase 10 `FEASIBILITY_ONLY`. The only scoping overreach is the surface-independence sentence in
finding 8, and the family-exhaustion statement is correctly framed as a statement about the E2 family,
not about the cell.

## Unverifiable from the committed tree (stated, not upgraded by inference)

- The re-run timings in `config/FEASIBILITY_GATES_C7.json:33` and the S6 ledger note ("~17s against
  ~75s") are environment claims; my own N=64 evaluation of four bounds took 114 s uncached on this
  host. Not a defect, just not a verifiable property of the tree.
- The provenance of `critical_A0_C5T = 3.266415728267196` and of `A0_certified_float =
  4.867216116723177` lies outside this namespace; C7 reads them as committed facts and labels their
  dependency sets correctly. I did not re-derive either, and the Arb/FLINT surface is out of scope.
- The claim that `E[τ] ≥ E[τ′]` pathwise (C4's clipping majorant) is inherited from C4 and was
  adjudicated there. I verified the induction `max(s⁺_t, s⁻_t) ≤ Σ_{i≤t} (|x_i|−K)⁺` by hand and it
  holds, but C4's adjudication itself is out of scope.
- Three B0 checks (`chk(1)`, `chk(2)`, `chk(16)`) can no longer be reproduced at this HEAD, so the
  B0 artifact's PASS is a historical record rather than a re-checkable fact (finding 7).

## Conditions that would change the verdict

1. Findings 1 and 2 repaired in code and in the gate text, with a new mutant that tampers with
   `a_grid` (not only with `value`/`source`) in the required-detection set.
2. Finding 3: Step 0 executed, with `c` frozen in the gate and its output emitted.
3. Finding 4: the `UNSOUND_BELOW_GRID` class renamed and its justification corrected; the four
   surviving rounding mutants surfaced in the summary rather than folded into `undetected = []`.
4. Finding 5: M11 rewritten to drive the real `certified_U` guard.
5. Finding 6: `coverage_limitation` restated with the measured `+1.0985 %` span and the correct upper
   `U` (4.867216116723177), and with the interface (not merely code-mutation) reachability admitted.
6. Finding 7: a walk that covers all seven modules, in an artifact that can be regenerated at the
   publication HEAD.
7. Findings 8 and 9: the two wording/field repairs.
8. Finding 14: the Monte Carlo either removed or declared against an amended gate — not both as they
   currently stand.
9. Finding 15: `HANDOVER_FACT_VERIFICATION.json` regenerated at the publication HEAD (it would
   currently REFUSE), its regex widened to cover four-decimal percentages, and its PASS not presented
   as clearing prose claims it cannot see.
10. Finding 16: `re` added to `STDLIB_ALLOWED` deliberately, and the walk re-run over all eight
    modules.
11. The working tree committed and clean, and `OPEN_NOTES_DISPOSITION_C7.md` either committed (with
    `README.md:75-77` amended to match) or dropped.
12. The certificate regenerated after all of the above, since the gate text, the mutation artifact and
    the B0 artifact all feed it.

Findings 10–13 and 17 do not need to block publication on their own, but 10/17 should be reflected in
`README.md:75-77`, which currently makes a claim about the mathematics ("genuinely unclear") that the
campaign's own untracked note already contradicts.

## Verdict

The arithmetic is clean and the three theorems are correct; the published PRIMARY bound
3.586306093865… is, as far as I can tell, a valid certified lower bound on `Λ_309`, and every number
in `README.md` reproduces exactly from the committed code — which is the failure mode this programme
has shipped five times and did not ship here. But the README's headline claim that two structural
holes were "found and closed" is false of the committed tree for one of the two: I obtained an
inflated bound from an understated `U`, with an empty dependency set, surviving re-derivation and
every kill gate. And the gate's non-blindness argument, which the handover asked me to test, is
falsified by two of the five choices it enumerates. Neither of those can be shipped as written.

The addendum only hardens that: the frozen gate's flat prohibition on "Monte Carlo of any kind" was
crossed and the result is sitting in the namespace; the new governance artifact that is supposed to
stop exactly this class of error is already stale, cannot see any of findings 3, 4 or 6, and its
companion module would make the campaign's own B0 audit refuse.

Distinguish clearly, because it matters for the repair: **the numbers are right, the mechanisms are
not.** Nothing I found impugns 3.586306093865… as a lower bound on `Λ_309`. Everything I found
impugns the machinery that is supposed to guarantee it — the U provenance, the gate's validity
argument, the mutation classification, the import walk, the fact-check. This programme's recorded
history is of mechanisms that passed while the thing they guarded was wrong; here the thing guarded
happens to be right and four of the guards do not hold. That is not a safer position, it is the same
position with better luck.

NOT_READY
