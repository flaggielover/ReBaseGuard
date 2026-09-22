# Final independent adjudication — C11 (N9 independent second-certifier closure)

Adjudicator: fresh context, no prior involvement in C2–C11.
Worktree `/Users/suzhe/ReBaseGuard-k5c11`, branch `p5y-k5-tail-c11-n9-independent-certifier`,
HEAD `832e27aa` ("N9 VERDICT: AGREEMENT_INSUFFICIENT, N9 remains OPEN").

**Method.** I read `README.md`, `config/N9_GATE_C11.json`, all three evidence artifacts and all five
`code/*.py` modules. I then read the sources C11 depends on but does not quote in full: the original
certifier `p5y_k5_perron_deflated_resolvent/code/taboo_certify.py`, the frozen model
`p5y_k1_cover_ledger_implementation/code/cusum_layer1.py`, the reused primitive
`p5y_k5_tail_c7_e2_lambda309/code/c7_gaussian.py`, `REGISTRY_C2.json`, the reachable-set
parameterisation in `p5x_global_nonlinear_dynamics/compute_optimization_r2/fast_range.py`, and the
N9 wording in `OPEN_NOTES_DISPOSITION_C2.md`.

I did not take any numeric claim on trust. In a scratchpad I (i) wrote my own float
re-implementation of the kernel from `cusum_layer1.py` and cross-checked it against
`c11_certifier.kernel_apply`; (ii) solved the true value function `v = 1 + K_e v` by value iteration
to 4.5e-11; (iii) computed the exact pointwise supersolution condition for C11's candidate families
on a 161×161 grid over R; (iv) re-ran C11's own unmodified `supersolution_margin` on eight
candidate/depth combinations, including reproducing its published figures and testing a candidate it
did not try.

**No file in the tree was modified except this report.** I ran no producer that writes evidence
(`c11_b0_n9.py`, `c11_mutations.py` and `c11_result.py` all write into `evidence/`; I did not run
them). No git state was changed. No AWS, no Vultr, no SSH, no installs, no numpy/scipy/flint.
`PYTHONINTMAXSTRDIGITS=0` throughout.

I judge the committed artifacts and code, not the commit messages.

---

## Executive finding

C11's second certifier is **genuinely independent** and **sound**. I verified both myself, against
the frozen model rather than against C11's description of it, and I reproduce its two published
certification figures to the last recorded digit.

But the campaign's scientific conclusion is **wrong**, and wrong in the exact way the brief warns
about. C11 declared the route dead on a blocker it manufactured. Three separate defects compound:

1. **It compared against the wrong constant.** C11's certifier certifies `w ≥ 1 + K_e w`, whose
   conclusion — in its own words — is `E_x[τ] ≤ w(x)`. In the original certifier that is *exactly*
   the `Abar` field (7.5556132), not the `tau` field (4.9520562), which is the **atom-removed**
   taboo quantity against `Khat_e`. `c11_result.py` loads both and divides by `tau`.
2. **Its diagnosis of the failure is false.** The drift-aware family `w = A − B(p+m)` fails
   **pointwise**, with an exact kernel and no box bound at all, for every candidate C11 tried and
   for every `(A,B)` in the family below `A = 8070`. The box-uniform kernel bound is not the binding
   looseness. "More compute" and "a sharper uniform bound" would never have certified that family.
3. **Closure was reachable in this campaign, with C11's own unmodified code.** Deleting the `p` term
   — `w = A − B·m`, which is what the true solution actually looks like — is pointwise feasible at
   `A = 4.885`. Running C11's certifier, unchanged, at its own drift, `w = 9.9 − 1.5m` **certifies
   at depth 4 in 190 seconds** — a ratio of **1.310** against the correct comparator
   `Abar = 7.5556132`, and of **1.9992** against the `tau` C11 actually used. That is inside C11's
   own frozen factor-of-2 criterion **against either comparator**. **N6 was reachable**, and not
   merely as a consequence of defect 1.

N9 nevertheless remains open, for three reasons C11 did not identify: its statement is at a single
drift where the original's is uniform on the e-block; it targets cell 307 and one constant where N9
is worded about cell 306 and six; and its own stated reason for abandoning the blinded comparison is
contradicted by its own code. The recorded status (OPEN) is right; almost everything the record says
about *why* is wrong, and the forward guidance it hands the successor points away from the answer.

---

## Findings

### 1. CRITICAL — the N6 comparison is between two different quantities

`taboo_certify.py` lines 202–203 state the distinction verbatim:

    full=False: w >= 1 + Khat_e w (taboo: C_T = sup w, tau = w(a)).
    full=True:  w >= 1 + K_e w (whole kernel: E_x[tau] <= w(x); Abar = w(a) bounds the ARL at the atom).

and its module docstring (line 7) confirms the supersolution behind `(C_T, tau_a)` is taken against
`Khat_e`, the kernel with the origin/atom piece removed (`K_e = Khat_e + k_a ⊗ δ_a`; the removal is
the `continue` at line 99 skipping the z-window `[m−K, K−p]` where both arms land on the atom).

`REGISTRY_C2` block 307 carries **both** constants, from **two separate certificates**:

| field | value | statement |
|---|---|---|
| `tau` | 4.952056204691856 | `(Ghat_e 1)(a) ≤ tau`, **atom-removed** kernel `Khat_e` (Lemma T) |
| `Abar` | 7.5556132138736665 | `E_a[τ] ≤ Abar`, **whole** kernel `K_e` — own artifact `67122df3…`, 57.9 CPU-s |

C11's certifier implements the **whole** kernel. Its own certificate string
(`c11_certifier.py:45-46`, `c11_result.py:35`) is *"w ≥ 1 + K_e w on R, hence E_x[tau] ≤ w(x)"* —
which is the definition of `Abar`, word for word. `c11_result.py` loads `tau_orig` **and**
`abar_orig` (lines 22–23), records both, and then forms

    ratio = F(9000) / tau_orig                                  # line 56

The comparator is wrong. The headline "1817×" should be 9000 / 7.5556132 = **1191×**. More
importantly the framing built on it — *"there is NO scientific disagreement: the independent bound is
consistent with the original's, merely far weaker"* — is asserted of a comparison that is not
like-for-like. (The inequality direction is at least safe: `Khat_e ≤ K_e` pointwise for `w ≥ 0`, so a
`K_e`-supersolution is also a `Khat_e`-supersolution and 9000 does bound `tau`. It is *valid*; it is
not *the same quantity*.)

C11 never implemented `Khat_e` at all, so it cannot produce the constant it chose to compare
against. This is a two-line change to `kernel_apply`: the function already isolates the piece where
`pz_pos` and `mz_pos` are both false — that piece *is* the atom piece.

Aggravating: `c11_b0_n9.py` line ~203 does `p.read_text()` on `taboo_certify.py` to AST-walk it, so
the campaign had in hand the file that spells out the distinction in English.

### 2. CRITICAL — the recorded cause of failure is false; the drift-aware family fails pointwise

For `w = A − B(p+m)` the supersolution condition is exactly, with no box bound and no discretisation:

    A·h1(p,m) + B·( K_e[p'+m'](p,m) − (p+m) ) ≥ 1      for all (p,m) ∈ R

I evaluated this on a 161×161 grid over R at C11's own drift `e = 1.8355`, using an exact-kernel
float reimplementation (cross-checked against `kernel_apply`, finding 12):

| candidate | C11's recorded box margin | **exact pointwise margin** | binding state |
|---|---|---|---|
| A=9, B=1.3 | −4.5243 | **−2.2331** | (4.56, 0) |
| A=12, B=2.0 | −6.4251 | **−2.9036** | (4.72, 0) |
| A=20, B=3.0 | −9.1343 | **−3.8480** | (4.59, 0) |

All three are infeasible **at infinite subdivision depth with a perfect kernel**. Worse, minimising
the required `A` over the whole one-parameter family gives

    min over B of A_required = 8070.30, attained at B = 0

i.e. **the "drift-aware" family is provably never better than the constant**. No sharpening of
`kernel_box_upper`, no per-box window, no splitting at the kinks inside the box bound, and no amount
of compute can certify it below 8070.

C11 observed the diagnostic signature of this and misread it. Its own record says *"all fail, and the
margin **WORSENS** as the candidate grows"* — a margin that degrades monotonically as you spend more
of the budget is the signature of a **structurally infeasible ansatz**, not of a loose bound; a loose
bound gets *relatively* cheaper as the candidate grows. The pointwise margins above worsen in the
same monotone way (−2.23 → −2.90 → −3.85), which settles it.

Therefore `WHAT_BLOCKS_CLOSURE` —

> "tightness, not soundness. The box-uniform kernel bound is too loose at affordable subdivision
> depth. Closing N9 needs a sharper uniform bound … or enough compute to subdivide far deeper."

— is **false**, and it is the single most damaging sentence in the campaign, because it is the
instruction the successor inherits. The cost of refuting it was a few milliseconds of arithmetic on
the same laptop: evaluating the pointwise condition on a grid requires no interval arithmetic and no
subdivision at all. A negative-verdict campaign owes that check before blaming its own machinery.

This is the C9 failure mode named in my brief, reproduced.

### 3. CRITICAL — closure was reachable: C11's own certifier certifies a qualifying candidate

The true solution of `v = 1 + K_e v` (my value iteration, 41×41 grid, bilinear interpolation,
converged to 4.5e-11) is

    v(atom) = 4.44498,   sup over R = 4.44498 (at the atom)
    v along m = 0: 4.445, 4.445, … , 4.443, 4.434, 4.401   for p = 0 … 5
    v along p = 0: 4.445, 4.096, 3.732, 3.362, 2.990, 2.611, 2.225, 1.847, 1.516, 1.269, 1.117

`v` is, to three digits, **a function of m alone, decreasing in m, and flat in p**. C11's family
decreases in `p` as well, which is precisely backwards at the binding states (`p ≈ 4.6, m = 0`,
where `h1` is at its floor and `p+m` falls by ≈ 3 in one step). Dropping the `p` term:

    family w = A − B·m :   pointwise-feasible with A_min = 4.885 at B = 0.75

— below even the taboo `tau`. And with **C11's own `c11_certifier.supersolution_margin`, unmodified,
at its own drift `e = 18355/10000`, its own `panels = 16`, its own cover**:

| candidate | depth | boxes | margin | certified | wall clock |
|---|---|---|---|---|---|
| w = 12 − 1.5·m | 1 | 3 | −3.12672 | no | 4.6 s |
| w = 12 − 1.5·m | 2 | 10 | −1.28847 | no | 16.5 s |
| w = 12 − 1.5·m | 3 | 30 | −0.37832 | no | 53.0 s |
| **w = 12 − 1.5·m** | **4** | **97** | **+0.09043** | **YES** (w_min 4.5) | **297 s** |
| **w = 9.9 − 1.5·m** | **4** | **97** | **+0.08406** | **YES** (w_min 2.4) | **189.5 s** |

So an independent certified bound of **12** — or of **9.9** — on the quantity the original certifies
as `Abar = 7.5556132`, for three to five minutes of the same laptop C11 declared out of budget:

| independent bound | vs `Abar` = 7.5556132 | vs `tau` = 4.9520562 |
|---|---|---|
| 12 | **1.588 ≤ 2** ✓ | 2.423 ✗ |
| 9.9 | **1.310 ≤ 2** ✓ | **1.9992 ≤ 2** ✓ |

**C11's own frozen N6 criterion is satisfied against either comparator.** The 9.9 candidate clears
the factor of 2 even against the constant C11 wrongly compared to — so finding 1 is not what saved
the campaign from a negative verdict, and finding 2 is not excused by it. The candidate was one
deleted term away.

I stress what this does and does not show. It does **not** close N9 (see findings 5–7). It does show
that C11's stated ground for the negative verdict — that the independent route is 1817× too weak and
the gap is an engineering limit — is refuted by C11's own code, at C11's own settings, with a
candidate obtained by deleting one term from C11's own ansatz.

### 4. MAJOR — "depth 5 was not affordable" does not survive measurement

Measured on this machine with C11's code:

| depth | boxes | wall clock (panels 16) |
|---|---|---|
| 3 | 30 | 90.7 s (w=9000), 106.2 s (w=6000), 105.2 s (A=9,B=1.3) |
| 4 | 97 | 297 s |

I therefore reproduce the recorded "110–121 s per candidate" at depth 3 within machine noise, and the
claim is honest. But the growth factor is **≈ 3.3 per level, not 4** (the cover drops boxes that miss
R), and depth 5 extrapolates to **≈ 15–20 minutes for one candidate** — on a campaign that recorded
`AWS: 0`, `VULTR: 0` and `NEW_REAL: 0` and was under no clock. `N7_precision_escalation` is recorded
`PARTIAL` on an affordability claim that a single twenty-minute run would have settled, and `N7` is
one of the criteria C11 cites in its verdict. No compute budget is recorded anywhere in the campaign,
so "not affordable" is an assertion with no referent.

### 5. MAJOR — statement mismatch: a point drift is not the e-block

`taboo_certify.py` lines 236–239 state both certificates as *"for every e in [e_lo, e_hi]"*. For cell
307 that block is `[1.7885921, 1.882413]`. C11 certifies at the **single rational** `e = 18355/10000`
and its code takes `e: F` with no interval-`e` path anywhere; `kernel_apply`, `alarm_prob` and
`kernel_box_upper` all take a scalar drift.

C11 discloses that the drift is a development value, but records `N4_same_frozen_inputs: SATISFIED`
and evaluates `N6` as though the two statements were comparable. They are not: C11 solves a strictly
easier problem. A second certifier that cannot express block-uniformity cannot corroborate the
original's statement however close its number lands. This is a real gap in the artifact and it is not
recorded as one.

### 6. MAJOR — mis-scoped target: cell 307 and one constant, where N9 is worded about cell 306 and six

C11's own B0 dossier records the two governing wordings verbatim:

- replacement floor: *"a second, independently written certifier reproducing **the six operator
  constants for cell 306** (closing N9)"*
- adjudication: *"Cell 305 has one; **cell 306** does no[t]"*

`c11_result.py` sets `CELL = 307` with no recorded justification, and certifies one constant
(and, per finding 1, not one of the ones it compares against). Even perfect factor-of-2 agreement
here would not have closed N9 as worded. `N9_GATE_C11.json` never states which cell or how many
constants closure requires — a prospective gate for an N9 campaign is exactly where that belongs, and
B0 had already extracted the answer.

### 7. MAJOR — the sole stated reason for abandoning the blinded comparison is contradicted by the code

The gate's `DISCLOSURE_OF_ORDERING` says a blinded comparison *"was never available"* because
*"the first certifier's tau and Abar are committed in REGISTRY_C2 and **were read during phase B0**,
before any implementation began"*, and calls this *"sufficient reason not to claim N9 closure in this
campaign, independently of the numerical outcome"*.

`REGISTRY_C2.json` is read in exactly one place in the whole campaign:

    code/c11_result.py:20   reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")

`c11_b0_n9.py` reads only `OPEN_NOTES_DISPOSITION_C2.md` and `C2_ADJUDICATION.md` (lines 139–140),
and I grepped both: **neither contains `tau`, `Abar`, `4.95` or `7.555`**. C11's own mutation M03
asserts the same thing — *"the registry is read only by the RESULT module, at comparison time"*.

So either the disclosure is inaccurate about its own history, or the read happened in un-recorded
exploratory work outside the committed producers. Either way, a seal-then-compare ordering **was**
available and was simply not arranged: run the certifier, hash and commit the bound, then run
`c11_result.py`. `N10_seal_before_compare: FAILED — not available in this campaign` books a fixable
process omission as an inherent limitation, and then leans on it in the verdict.

### 8. MAJOR — the load-bearing numbers are hard-coded literals, not produced evidence

`c11_result.py` lines 32–53 embed every certifier result as a Python literal. No committed module
runs the certifier and emits an artifact; `evidence/` contains only `b0/`, `mutations/` and `n9/`.

I re-ran them:

| claim | recorded | reproduced |
|---|---|---|
| w=9000, depth 3, panels 16 | +0.1152, certified | **+0.1152, certified** ✓ |
| w=6000, depth 3, panels 16 | −0.2565, not certified | **−0.2565, not certified** ✓ |
| A=9, B=13/10 | −4.5243 | **−4.3588** at depth 3, panels 16 ✗ |

The first two are honest and exactly reproducible. The drift-aware margins are **not** reproducible
from the artifact, because the artifact records no depth and no panel count for that family — the
`cost` field says "panels 12/16", so the three drift-aware rows were evidently taken at settings that
are nowhere recorded. Separately, the soundness claim *"standard-normal moments exact 1, 0, 1, 0, 3"*
(README table; `WHAT_C11_DID_ESTABLISH`) has **no producer anywhere in `code/`** — `M08` only checks
that the moments are `Fraction` intervals. I verified the claim myself
(`moments(−12, 12, 4) = [1, ±1.0e-76, 1, ±1.5e-74, 3]`), so it is true; it is an assertion, not
evidence.

### 9. MODERATE — the mutation suite cannot catch any of the findings above

The twelve mutants are: three AST/import checks (M01–M03), two shallow numerical invariants (M04
domination, checked only at box **corners**, only for `w ≡ 1`, on **three** boxes; M05 an ordering
check at depth 2/panels 8), two constants checks (M06, M07), two arithmetic-hygiene checks (M08,
M09), and three self-referential governance reads (M10–M12) of the JSON `c11_result.py` had just
written from literals.

Not one mutant plants a wrong comparator, a wrong target quantity, a wrong cell, a wrong candidate
family, a mis-transcribed margin, or a point-drift-for-block-drift substitution. The suite is by
construction incapable of detecting findings 1, 3, 5, 6 or 8 — the ones that decide the campaign.
`MUTATION_CLASS = PASS` is therefore much weaker evidence than it reads as. For a campaign whose
entire product is a cross-check, the mutation suite should have contained at least one mutant of the
form "swap the comparator" and one of the form "report a margin the certifier does not produce".

### 10. MODERATE — the gate's criterion names collide with the programme's open-note identifiers

The C2 open notes contain notes **N9** ("the Arb/FLINT supersolutions remain the residual trust
surface") and **N10** ("the registry does not record the host that built it"). `N9_GATE_C11.json`
reuses `N1…N10` for its own internal criteria, including a criterion literally named
`N9_mutation_suite` **inside the campaign whose subject is note N9**, and an `N10_seal_before_compare`
that has nothing to do with note N10. `C11_N9_RESULT.json` then reports `"N10 … FAILED"`, which a
reader will bind to the open note. Rename before anyone builds on this.

### 11. PASS — the independence claim is TRUE

AST walk over all five C11 modules. Union of imported roots:

    {__future__, ast, c11_certifier, c11_common, c7_gaussian, fractions,
     hashlib, importlib, json, math, os, pathlib, re, subprocess, sys}

Intersection with the forbidden set `{taboo_certify, resolvent_certificate, opnorms, ra_certifier,
fast_range, intervals, rebaseguard_certify, rung3_engine, spec}`: **empty**. Intersection with
`{numpy, flint, scipy, mpmath, sympy, gmpy2}`: **empty**. Every textual occurrence of a forbidden
name in `code/` is a docstring, a path constant, or the B0 dossier's own record of the list — I
checked each occurrence. There is no dynamic import, no `exec`, and no read of an artifact the
forbidden modules produced anywhere in the certifier.

**The reuse of `c7_gaussian.py` is legitimate, not a hidden dependency on the first certifier.** C7
is a sibling tail campaign, not the first certifier; it does not appear in `taboo_certify.py`'s
transitive graph (I re-derived the graph); and it is itself a from-scratch rational Φ/φ whose only
import is `fractions`, with proved remainder bounds on every series — the opposite of an Arb
dependency. The declaration in the certifier docstring is appropriate.

One qualification, which belongs in the record and is not there. What is established is independence
**from the first certifier**, on implementation and on arithmetic backend. It is not independence of
**authorship**: the same agent wrote C7 and C11, and N9's risk is *"a possible systematic error in a
single implementation … of unknown magnitude"*. Finding 1 is a live demonstration that a same-author
second implementation does not catch a same-author misconception — here, about which of two
published constants the machinery computes.

### 12. PASS — the certifier is SOUND

I checked every link against the frozen model rather than against C11's description of it.

- **Kernel.** `cusum_layer1.collocation` (lines 112–128) uses `ell = m − C_CUSUM`,
  `upper = C_CUSUM − p`, weight `φ(z + drift)`, next state `(max(0, p+z−K), max(0, m−z−K))`, and
  `h1 = 1 − Φ(upper+e) + Φ(ell+e)`. `c11_certifier.kernel_apply` and `alarm_prob` transcribe this
  exactly, including the kink set `{K−p, m−K}` and both sign conventions
  (`p' = (p−K) + z` via `_pow_lin(p−K, +1, i)`, `m' = (m−K) − z` via `_pow_lin(m−K, −1, j)`), and the
  suppression of a monomial when its arm is clamped to zero on that piece. The midpoint sign test is
  legitimate because the kinks are exactly the sign changes. With my independent float
  reimplementation, `(K_e 1)(p,m) − (1 − h1(p,m)) = 0.0` to the last bit at six states covering all
  three window regimes.
- **Moments.** `M_0 = Φ(B) − Φ(A)`, `M_1 = φ(A) − φ(B)`,
  `M_j = (j−1)M_{j−2} + A^{j−1}φ(A) − B^{j−1}φ(B)` is the standard recursion; the shift
  `∫_a^b z^j φ(z+e) dz = Σ_i C(j,i)(−e)^{j−i} M_i` is correct. Verified numerically (finding 8).
- **Box bound.** A genuine upper bound. The union window `[c−C, C−a]` contains `[m−C, C−p]` for every
  state in `[a,b]×[c,d]`; each panel contributes `Iv(0, max(0, w.hi)) · Iv(0, mass.hi) ≥ 0`, so
  widening and any negative excursions of `w` can only push the bound up; and the image-box endpoints
  are right because both arms are monotone in the state and in `z`. I tested domination
  independently on 5 boxes × 16 interior points with a **non-constant** `w` (stronger than M04's
  corners-only, `w ≡ 1` test): dominates on all, slack 0.08–0.46.
- **Cover.** `box_meets_R` keeps every box that can meet `R = {p+m ≤ 4} ∪ {p=0} ∪ {m=0}` (`a+c` is
  the box minimum of `p+m`; `a==0`/`c==0` are exactly the axis-touching tests), so the cover is a
  superset of R — sound, and it matches the original's reachable parameterisation in `fast_range`
  (triangle `0 ≤ r ≤ 4` plus axis tails `4 ≤ r ≤ 5`). R is forward-invariant (`p'+m' = p+m−1` when
  both arms are positive, otherwise one arm is 0), so the supersolution conclusion on R is legitimate
  for a chain started at the atom.
- **Margin.** `min over boxes of (w.lo − 1 − Kw.hi)` is a valid lower bound on `L` over R, and
  `w.lo ≥ 0` is checked separately. Correct.
- **Straddle.** I independently compute `min_R h1 = 1.23911e-4` at the atom, so `1/min_R h1 =
  8070.30`; 9000 certifies with +0.1152 and 6000 fails with −0.2565, both reproduced exactly. This is
  a real, independently derivable correctness signal and C11 is right to claim it.

Soundness is not what failed here.

### 13. MINOR — the reused Φ/Φ degrades silently outside the operating range

`c7_gaussian._erf_integral(t)` passes its own monotonicity guard for `t ≈ 20` (it needs
`n ≳ t²/2 = 200 < ERF_TERMS = 240`) but returns an enclosure of width ~1e82:
`moments(−20, 20, 4)` gives `[−2.2e82, 6.5e82]` for `M_0` instead of refusing. The enclosure is
**sound** — it contains the true value — but vacuous. `exp_neg` does refuse above `|t| ≈ 21`.

Nothing load-bearing is affected: inside C11's operating range the moment arguments lie in
`[−3.67, 7.34]` (`t²/2 ≤ 27 ≪ 240`), which I checked from `kernel_box_upper`'s window construction.
Flagged only because `c11_certifier` adds no range guard of its own, so a successor that widens the
state space or the drift block gets silence rather than a refusal.

### 14. PASS — scope is clean

- `git diff ec969db1..HEAD` touches **only** the C11 namespace (10 files). Verified.
- No `COVERAGE_MAP_R6` anywhere in `HEAD` (the one `R6` hit is `C2/review/REVIEW_C2_PREFREEZE_R6.md`,
  a pre-existing review round, not a coverage map).
- No `guard: ALLOW` anywhere; C11 records `DENY` in B0, the gate and the result.
- C2–C10 namespace trees unchanged.
- No cell closed or adopted, no r6, no coverage change. `EXPLICITLY_NOT_CLAIMED` is accurate and
  complete.
- No AWS, no Vultr, no SSH, no installs in C11's code. The only network call is
  `git ls-remote origin refs/heads/main` in B0 check 14, recorded and explicitly not synchronised;
  it returns `1cb45382` against local main `c123b9bb`, consistent with the known divergence, and it
  is run from the primary checkout so the scratch-clone `ls-remote` trap does not apply.
- My own review contacted no host and installed nothing.

### 15. MODERATE — the honesty question, answered both ways

C11 is right to disclose the ordering defect rather than paper over it, and right that "both bounds
are valid" is too weak a rule to close N9 — the gate's `explicitly_not_adopted` clause is good
governance and M11 enforces it. On N7 and N10 it is **not** being over-scrupulous in the sense of
holding itself to an unreasonable standard; it is doing something subtler and worse. Both criteria
are recorded as structurally unavailable when both were in fact simply not arranged: N10 by an
ordering that its own code shows was available (finding 7), N7 by a twenty-minute run it never
attempted (finding 4). Scrupulous-sounding self-denial on two criteria sits directly alongside an
unexamined comparator error on the criterion that decided the verdict. The scepticism was pointed at
the campaign's process and not at its mathematics.

---

## Answers

**(a) Is the second certifier genuinely independent?**
**Yes**, from the first certifier, on both axes claimed. Zero imports from the forbidden set, zero
from `numpy`/`flint`/`scipy`, no dynamic import, no replay of any artifact the forbidden modules
produced; exact rational arithmetic throughout. The `c7_gaussian.py` reuse is **legitimate** — C7 is
not the first certifier, is not in its transitive graph, and is itself a standard-library-only
rational Φ/φ — and it is properly declared. The claim that this is "strictly stronger than N9 asks"
is fair. The unrecorded qualification: this is independence of *implementation and backend*, not of
*authorship*, and finding 1 shows what that distinction costs.

**(b) Is it sound?**
**Yes.** I verified the kernel against `cusum_layer1.py` line by line and numerically, the moment
recursion and the shift, the box bound's domination (with a stronger test than C11's own), the
cover's superset property and R's forward-invariance, the margin's direction, and the `1/min_R h1 =
8070.30` straddle. One non-load-bearing robustness defect in the reused Φ (finding 13). The
certificate `9000` is a valid upper bound on `E_a[τ]`, and *a fortiori* on the original's `tau`.

**(c) Is AGREEMENT_INSUFFICIENT the correct verdict, or was closure reachable?**
**The verdict is wrong as reasoned, and N6 closure was reachable.** C11's own unmodified certifier
certifies `w = 9.9 − 1.5m` at depth 4 in 190 seconds: ratio **1.310** against the correct comparator
`Abar = 7.5556132` and **1.9992** against the `tau` C11 used — the frozen criterion **satisfied
either way**, so the negative verdict does not even survive on C11's own terms. The grounds C11 gives for the
negative verdict do not hold: `N6` was evaluated against the wrong constant (finding 1) with a
family that is pointwise infeasible for reasons unrelated to the box bound (finding 2), and `N7` was
abandoned on an affordability claim that measurement refutes (finding 4). The honest label for this
campaign is not `AGREEMENT_INSUFFICIENT` — which asserts a scientific fact about the achievable
tightness that is false — but an execution-invalid outcome: the N6 evaluation is void.

**(d) Should N9 be recorded OPEN or CLOSED after C11?**
**OPEN** — the status is right, the stated reasons are not, and the record must be corrected before
anyone builds on it. N9 stays open because: the second certifier's statement is at a single drift
where the original's is uniform on the e-block (finding 5); it addresses cell 307 and one constant
where N9 is worded about cell 306 and six (finding 6); it has never implemented the atom-removed
kernel and so cannot produce `tau` at all (finding 1); and no sealed, blinded comparison was arranged
although one was available (finding 7). None of these is what `C11_N9_RESULT.json` says. In
particular `WHAT_BLOCKS_CLOSURE` must not stand as written: the blocker is not tightness and not
compute.

**(e) What exactly should the next campaign do?**

1. **Fix the comparator first, in the gate.** State which constant each certifier's statement
   produces — `w ≥ 1 + K_e w ⟹ Abar` versus `w ≥ 1 + Khat_e w ⟹ (C_T, tau)` — and require the
   comparison to be constant-for-constant. Do not reuse `N1…N10` as criterion names (finding 10).
2. **Implement `Khat_e`.** Two lines in `kernel_apply`: drop the piece where `pz_pos` and `mz_pos`
   are both false. That yields `tau` and, as `sup_R w`, `C_T` — two of the six constants — from
   machinery that already exists and is already validated.
3. **Use a supersolution shaped like the solution.** The true `E_x[τ]` is ≈ 4.445 at the atom,
   decreasing in `m`, essentially flat in `p`. `w = A − B·m` is pointwise feasible at `A = 4.885`,
   `B = 0.75`, and `w = 12 − 1.5m` certifies at depth 4 today. Before spending any compute on a
   candidate family, screen it with the **pointwise** condition on a grid — milliseconds, no interval
   arithmetic — and only then subdivide. Had C11 done this, the campaign would have turned within the
   first hour.
4. **Make the certifier take an interval drift** so it can state the original's block-uniform result
   over `[e_lo, e_hi]`. Until it can, no number it produces corroborates the original's statement.
   This, not tightness, is the real remaining engineering work.
5. **Target cell 306 and all six constants**, as N9 is worded, or amend N9 explicitly and say why.
6. **Seal before comparing.** Run the certifier, commit the hash of its output, and only then read
   `REGISTRY_C2`. Nothing prevents this; C11's own module layout already isolates the registry read
   in the last module.
7. **Run depth 5.** At ≈ 3.3× per level it is ≈ 15–20 minutes per candidate on this laptop. Record a
   compute budget so "affordable" has a referent, and settle `N7` by measurement.
8. **Give the mutation suite at least one comparator mutant and one "recorded margin ≠ produced
   margin" mutant**, and emit the certifier's runs as evidence artifacts rather than as literals in
   `c11_result.py` (finding 8).
9. **Do not repair C11 in place.** Its artifacts are frozen and published; the corrections belong in
   the successor, with C11's record superseded, not edited.

Scope for the successor is unchanged and unconditional: no cell closed or adopted, no r6, no
coverage change, guard **DENY**, C2–C10 untouched, no AWS, no Vultr.

---

REJECTED
