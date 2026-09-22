# C7 independent adjudication — did the 17 repairs land?

Adjudicator scope: the committed tree at `/Users/suzhe/ReBaseGuard-k5c7`, branch `p5y-k5-tail-c7-e2`.
Namespace `level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309`, plus the predecessor files it reads
(C4 certificate, C5 forecast, the frozen CUSUM model).

HEAD when I started: `ce018ffa`. HEAD when I finished: `b472ff0d`. The only change between them is the
addition of `review/HANDOVER_C7_ADJUDICATION.md`; `git diff --stat ce018ffa b472ff0d` over the
namespace shows one added file and nothing else, so everything below was verified against the
publication content. `git status` is clean apart from this report.

Method. I did **not** re-derive the mathematics from scratch — the pre-publication review did that and
its items A–E, J, K and L were checked. My charge was the claim in `OPEN_NOTES_DISPOSITION_C7.md` → N5
(*"ALL FINDINGS ADDRESSED"*) and in commit `ce018ffa`. I read `c7_theorem.py`, `c7_certificate.py`,
`c7_mutations.py`, `c7_b0_audit.py`, `c7_factcheck.py`, `c7_common.py`, `c7_ledger.py`,
`c7_primitives_test.py` and `c7_psi_monotonicity.py` line by line; re-ran both CRITICAL exploits and
eleven variants of them out of tree; instrumented the PRIMARY path to count calls; recomputed all four
bounds, all three `U`s, all three `E_R_lower`s, the ceiling, the PRIMARY/MAX selection, the verdict
class and KG1/KG4/KG5 from the repaired modules; re-implemented the fact-checker's checks 1 and 4
read-only over the publication tree; and verified the gate blob, the model sha, the inherited Gaussian
and every artifact self-sha.

Constraints observed: no AWS, no Vultr, no ssh, no package install, no
`numpy/scipy/flint/mpmath/sympy/gmpy2`, no state-changing git command, and **no producer was run** —
`c7_certificate.py`, `c7_ledger.py`, `c7_mutations.py`, `c7_b0_audit.py`, `c7_factcheck.py`,
`c7_primitives_test.py` and `c7_psi_monotonicity.py` were never executed as `__main__`, because each
writes an evidence file. Every probe ran from copies of `c7_theorem.py` and `c7_gaussian.py` in a
scratch directory outside the repository, with `PYTHONINTMAXSTRDIGITS=0` and `PYTHONDONTWRITEBYTECODE=1`.
No file in the repository was modified except this one.

---

## 1. The two CRITICAL exploits, re-run

### Exploit (a) — forged `a_grid`

I presented `lambda_lower_tier_k` with exactly the certificate the review used:
`_tag='C7_CERTIFIED_U/1'`, `source='elementary'`, `a_grid=['-47/20']`, `dependencies=[]`,
`value=Fraction(3549353697, 10**9)`, at `e = e_lo`, `K = 1/2`, `H = 5`, `N = 64`:

```
[a: forged a_grid -47/20]  TheoremRefusal: presented a_grid does not match the gate's frozen grid;
                           presented ['-47/20']..., frozen ['2', '9/4', '5/2', '11/4']...
```

**The refusal is from a real guard, and it is specific.** I separated the two repairs and probed the
neighbourhood to rule out an incidental refusal:

| probe | outcome |
|---|---|
| a_grid = `['-47/20']`, value forged | refused — **grid mismatch** (`_resolve_U`, `c7_theorem.py:549`) |
| a_grid = the gate's grid, value still forged | refused — **re-derivation mismatch** (`:557`), a *different* guard |
| a_grid = gate grid **+** `-47/20` appended | refused — grid mismatch (tuple equality, so no subset escape) |
| a_grid present, `source='lorden'` | refused — `source 'lorden' must not carry an a_grid` (`:555`) |
| `source='elementary'` with the `a_grid` key **absent** | refused — grid mismatch (`None != GATE_A_GRID`) |
| `source='elementary'`, `a_grid=[]` | refused — grid mismatch |
| `U_elementary(..., [-47/20])` direct | refused — `Lemma C7-U requires a > 0; got a = -47/20` (`g_tail`, `:397`) |
| `g_tail(a=0)` | refused — same guard, so the boundary `a = 0` is excluded too |
| honest path: `certified_U('elementary', e_lo, K, H, GATE_A_GRID)` → `lambda_lower_tier_k` | **accepted**, `U = 5.9372053907260245`, `L = 3.5863060938653875`, dependencies `[]` |

Both root causes the review named are closed, independently of each other, and the honest path is
unaffected. `GATE_A_GRID` is bound at `c7_theorem.py:476` and `c7_certificate.py:20` now takes its
grid from it rather than re-literalling it.

### Exploit (b) — `e` outside the closed cell

```
[b:  lambda_lower(e=19/10)]          TheoremRefusal: e = 19/10 lies outside the closed cell
                                     [19839101/10000000, 2092283/1000000] for cell 309
[b2: lambda_lower_tier_k(e=19/10)]   same refusal — fires BEFORE _resolve_U (c7_theorem.py:274)
[b3: e = 198391/100000  (one ULP of the quoted decimal below e_lo)]   refused
[b4: e = 523071/250000  (just above e_hi)]                            refused
[b5: e = e_hi exactly]   accepted, 3.249221213828406   (closed cell, correctly inclusive)
[b6: e = e_lo exactly]   accepted, 3.461283496693919   (the published L1)
```

The guard is inclusive at both endpoints, as "closed cell" requires, and refuses immediately outside.
`GATE_E_LO`/`GATE_E_HI` (`c7_theorem.py:479`) are `19839101/10000000` and `2092283/1000000`; I
confirmed against `C4_CERTIFICATE.json#/cells/309` that these are C4's own `e_lo`/`e_hi` as exact
`Fraction`s.

Both CRITICALs are genuinely closed. **M16, M17 and M18 are in `required_detection_set` and all three
are `DETECTED_BY_RULE`**, with the refusal text in the artifact being the real guards' own messages.

---

## 2. Finding 3 — is `E_tau_prime_finite` on the published path?

I wrapped `T.E_tau_prime_finite` with a counter and ran the PRIMARY computation:

```
PRIMARY L3_elementary: 3.5863060938653875
E_tau_prime_finite call count on the PRIMARY path: 2
    [('19839101/10000000', '1'), ('19839101/10000000', '1')]
tier-1 path call count: 0
```

Two calls: once inside `certified_U` when the certificate is issued (`c7_theorem.py:519`), once again
inside `_resolve_U`'s re-derivation (`:556` → `certified_U`). So the step executes on the path that
produces the published PRIMARY bound, and the `p_lower > 0` refusal at `:520` is live. Its output
rides in every `U` certificate (`finiteness`) and is emitted in the certificate as
`lemma_C7_U_step0_finiteness` (`c = 1`, `p_lower = 0.686022237…`, `geometric_stages = 6`,
`E_tau_prime_upper_crude = 8.74607218165499`). The claim at `c7_theorem.py:348` ("the finiteness is
certified, not assumed") is now true of the tree.

Zero calls on the tier-1 path is correct and not a gap: tier 1 does not divide by `E[V] − g(a)` and
its Wald step is an identity in `[0, ∞]` by Tonelli, so it needs no finiteness.

Two caveats, neither fatal. (i) `c = 1` is fixed by `ERRATUM_C7_GATE.md` E3 and bound in code, **not**
in the frozen gate — which is the right instrument, since the gate cannot be amended, but it means a
prospective choice was made after the review with the answer already known. It does not affect
validity: any `c > 0` with `P(V > c) > 0` proves the same thing. (ii) `evidence/phase1/C7_LEDGER.json`
was **not** regenerated in `ce018ffa` and carries no step-0 figure, although the review's condition 2
asked for the crude bound in the ledger as well as the certificate. The crude bound `8.746072` is
also inert — nothing consumes it as a constraint; the load-bearing guard is the independent floor
`H/E[V]`.

---

## 3. Finding 4 — is `MUTATION_CLASS = PASS` laundering the four survivors?

**Partly yes, and this is my most serious adverse finding.**

What improved, and genuinely: the class `UNSOUND_BELOW_GRID` is gone; its justification ("below the
`2^-320` grid resolution") was numerically false by up to 405× and has been replaced by a statement
that is true and measured — the artifact now records "the effect is 42x / 405x / 1x / 5x the 2^-320
grid unit -- **NOT** below the grid". The `F(1,10)**60` threshold, ~10³⁷ coarser than the grid it was
named after, is gone; the anchor is now `float(v) == float(baseline)`, which is a real, checkable
property. M01–M04 are surfaced in `unsound_below_reported_precision`, in
`surviving_required_mutants_note` ("These mutants are **NOT** detected … the suite supplies no
positive evidence on rounding direction"), and in the certificate's
`supporting_artifacts.mutations.surviving_below_reported_precision`. The record is honest.

What did not change, and was not disclosed anywhere:

> `config/FEASIBILITY_GATES_C7.json:68` — **"KG8": "any mutant in the required-detection set survives
> -> REFUSE"**

`required_detection_set` contains M01–M04. The artifact's own prose says they survive and are not
detected. `MUTATION_CLASS` is nevertheless `"PASS"`, because `c7_mutations.py:234` computes it as
`"PASS" if not undetected else "REFUSE"` and the four were moved out of `undetected` into a sibling
list. `c7_certificate.py:88` reads exactly `MUTATION_CLASS == "PASS"`. Under the frozen gate's own
text, KG8 fires and `C7_CLASS` is `REFUSED`.

I grepped the whole namespace for any acknowledgement of this: `KG8` appears in the gate, in
`c7_certificate.py` and nowhere else. `ERRATUM_C7_GATE.md` has five entries (E1–E5) and none is about
KG8. **The campaign narrowed a frozen kill gate from "survives" to "survives and alters a reported
digit", in its own favour, without an erratum** — in a campaign whose erratum instrument exists for
precisely this act. The review's condition 3 asked only that the four be "surfaced in the summary
rather than folded into `undetected = []`", which was done; the gate-conformance question is one the
review did not ask and the campaign did not raise.

A second, smaller overstatement: the anchor is IEEE-double equality, while the certificate's
authoritative field is `bounds[*].value`, an exact rational with a 97-digit numerator. "Does not alter
any digit of the reported value" is true of the float and false of the rational. (It is mitigated by
the fact that the mutants run against the `N = 16` mirror and never touch the certificate's path.)

Materiality: nil for the number. The four mutants move the bound by ~1e-94 relative; no verdict, band
or conclusion depends on them. This is a governance defect, not an arithmetic one.

---

## 4. The 17 findings

| # | severity | repair claimed | verdict | evidence I checked |
|---|---|---|---|---|
| 1 | CRITICAL | `a > 0` enforced; frozen grid bound in code; M16/M17 | **LANDED** | Re-ran the exploit and 8 variants out of tree (§1). `g_tail` refuses `a ≤ 0` (`c7_theorem.py:397`), including `a = 0`. `_resolve_U` compares the presented grid against `GATE_A_GRID` (`:549`) and re-derives from the gate's grid (`:556`), never the certificate's. Non-elementary sources may not carry a grid (`:555`). M16/M17 in `required_detection_set`, both `DETECTED_BY_RULE` with the real guards' messages. Honest path unchanged: `U = 5.9372053907260245`, `L3_elementary` identical to the certificate as an exact rational. |
| 2 | CRITICAL | cell membership enforced; M18 | **LANDED** | `_require_in_cell` (`:485`) called from `lambda_lower` (`:134`) and `lambda_lower_tier_k` (`:274`), before `_resolve_U`. `e = 1.90` refused; `e_lo`/`e_hi` accepted; one-step-outside on either side refused. Endpoints from C4's certificate, verified as exact `Fraction`s. M18 `DETECTED_BY_RULE`. `ERRATUM_C7_GATE.md` E1 corrects the gate's non-blindness claim and names the side-conditions instead of the sweeping "no setting of any of them". |
| 3 | MAJOR | step 0 executes and rides in every `U` certificate | **LANDED** | Instrumented call counter: 2 calls on the PRIMARY path, 0 on tier-1 (§2). `p_lower > 0` refusal live. `lemma_C7_U_step0_finiteness` in the certificate. Caveats: `c` fixed by erratum + code, not by the gate (unavoidable); the ledger was not regenerated and carries no step-0 figure; the crude bound is inert. |
| 4 | MAJOR | false class replaced; M01–M04 reported as surviving | **PARTIAL** | Class renamed, justification now true and measured, threshold replaced by a real anchor, survivors surfaced in three places (§3). But `MUTATION_CLASS = "PASS"` and `undetected = []` are unchanged, KG8 consumes exactly those, and the frozen gate's KG8 text — "any mutant in the required-detection set survives → REFUSE" — is not satisfied. No erratum entry covers it; `KG8` appears nowhere in the erratum, README or disposition. |
| 5 | MAJOR | M11 drives the real floor guard | **LANDED** | `_mutated_lorden_derivation` (`c7_mutations.py:286`) monkeypatches `T.U_lorden` and calls the real `T.certified_U`. The recorded detail is `c7_theorem.certified_U`'s own text: *"U = 3 from source 'lorden' is below the certified floor H/E[V] = 7042883855512317…"*. The `if False` dead code at the old `:167` is gone. |
| 6 | MAJOR | coverage gap quantified at +1.0985 %, range widened | **LANDED** | `residual_gap_MEASURED` carries `max_undetectable_inflation_percent: 1.0985` and `U_range_undetectable: [3.297250281519544, 4.867216116723177]` with a `range_note` correcting the previous Lorden top. I reproduced both out of tree at `N = 64`, `e = e_lo`: `U` at the floor `3.297250282` → `L = 3.625700692` → **+1.0985 %**; registry `U` → **+0.3244 %**. `interface_gap_CLOSED` admits the reachability was an interface gap, not only a code-mutation gap. `why_this_matters` states the comparison against C4's 0.9440 % margin. |
| 7 | MAJOR | B0 re-runnable by ancestry; all modules walked | **LANDED** (with a new defect, see N4 below) | `chk(2)` now tests `merge-base --is-ancestor f494416f HEAD` instead of pinning a HEAD; `chk(16)` tests the gate sha instead of asserting the gate does not exist; new `chk(17)` asserts every module in `code/` was walked. The committed artifact walks **10** modules (`imports_per_module` includes `c7_certificate.py`, `c7_mutations.py`, `c7_ledger.py`, `c7_factcheck.py`), `unexpected: []`, `numerical_imported: []`, `B0_CLASS = PASS`, 17/17. `__import__`/`eval`/`exec`/`compile` and `from subprocess import run` are now detected (`:128`, `:121`). The artifact records `current_head: a6c2855b`, i.e. it was produced from the working tree before the publication commit; re-running at the publication HEAD would still PASS because the invariants are ancestry- and sha-based. |
| 8 | MINOR | README's surface-independence claim narrowed | **LANDED** | `README.md:27-32` now states explicitly that the *bound* is surface-free but the *margin statement* is not, because `critical_A0_C5T` is operator-level. |
| 9 | MINOR | C4 margin re-basing disclosed; README reordered | **LANDED** | `baseline_C4` now carries `margin_percent_over_C5T_critical_A0` (0.9439874105892059), `margin_percent_as_C4_published` (2.5827057582567217), `C4_frozen_clause_critical_A0` (3.2142360226778806) and a `rebasing_note`. `README.md:19-22` puts C4's published 2.5827 % first and the post-C5-T 0.9440 % second. |
| 10 | OBSERVATION | ψ wording corrected, backed by a producer | **LANDED** | New `code/c7_psi_monotonicity.py` + `evidence/psi_monotonicity/C7_PSI_MONOTONICITY.json`: criterion holds at all 65 knots, worst `ψ·h = 0.9434434039746084` at `u = H` (the review's 0.943443 to every digit), `u_star`, unresolved knots `[0.078125, 0.15625]`, gain `+0.05624166044571126 %`. `README.md:81-91` replaces "genuinely unclear" with the quantified declination. I checked the identity the bisection uses, `cosh(ey) = (φ(y−e)+φ(y+e))·φ(0)/(2φ(y)φ(e))`, algebraically — it is correct — and the bisection's use of the interval's *lower* endpoint for the predicate is the conservative direction. |
| 11 | OBSERVATION | primitives test committed | **LANDED** | `code/c7_primitives_test.py` + artifact: 12 known-value cases (Φ at 0, ±1, ±1.96, −7, 2.5; φ at 0, ±1, 2, 3.5) and 8 identities (Φ(t)+Φ(−t)=1 at four points, φ symmetry at three, an 81-point monotonicity sweep), `PRIMITIVES_CLASS = PASS`. Consumed by new gates KG10 and KG10b, the latter pinning `gaussian_sha256` to the committed `c7_gaussian.py` (I verified the sha `bd73b5b4…` matches). |
| 12 | MINOR | M07 and M13 reordered to reach their own guards | **LANDED** | `pipeline` now tests `K + H != 11/2` and strict increase **before** the ends-at-H test (`c7_mutations.py:47-52`). Artifact: M07 → `"K + H = 6 != 11/2, the frozen CUSUM threshold"`, M13 → `"partition must be strictly increasing and positive"`, M12 → `"partition must end exactly at H"`. Three distinct guards. |
| 13 | OBSERVATION | "dead code removed" | **PARTIAL — 2 of 5** | Fixed: the accidental `and` in the certificate (now `"exclusion_test"` and `"C4_gate_sha256"` as separate keys); M11's `if False` clause. **Not fixed:** `lambda_lower_tier2` still has **no caller anywhere** (`grep` over `code/ config/ evidence/ *.md` matches only its own definition) and is worse than inert — see N2 below; the analytic ceiling is still a hard-coded literal at `c7_mutations.py:112`; `mirror_equivalence_asserted: True` is still a literal (`:222`) consumed by KG8b; `c7_theorem.py:242` still does not say why `μ({0}) = 0`. N5's table entry "13 | dead code removed" is **false as stated**. |
| 14 | MAJOR | Monte Carlo breach disclosed and declared | **LANDED** (as disclosure; the breach itself is not repairable) | `ERRATUM_C7_GATE.md` E4 records it as "a breach of the gate's TEXT" and explicitly refuses to waive it; E5 scopes the counters. The certificate carries `external_non_evidence_activity` with `MONTE_CARLO_RUNS: 4`, `wrote_into_namespace: false`, `any_C7_conclusion_depends_on_it: false`, and `compute_boundary_scope`. I verified the gate blob is byte-identical at `166224bb` and at HEAD (`ed9220350557b1784fa78a434ef5abb4839ad95c` both), and that its sha `9f7083b9…` still gates the certificate (`c7_certificate.py:21`, `:40`) and B0 (`c7_b0_audit.py:180`). See §5 for my ruling. |
| 15 | MAJOR | fact-check regenerated, widened, blind spots stated | **LANDED** | I re-implemented checks 1 and 4 read-only over the publication tree: **0 unbacked prose figures** across all four scanned files (`ERRATUM_C7_GATE.md`, `OPEN_NOTES_DISPOSITION_C7.md`, `README.md`, `phase_3/C7_ROUTE_SEARCH.md`), and **all 7 evidence self-shas verify**. The regex is now `\d+\.\d{4,}` (`:30`), so the four-decimal headline percentages are scanned. Five Monte Carlo figures are exempted by an enumerated, declared `EXTERNAL_FIGURES` table rather than silently. The artifact carries `WHAT_THIS_CANNOT_VERIFY`, which names findings 3, 4 and 6 as classes it returned PASS on. The erratum/README figures the review computed are now backed by `pre_repair_exploit_values` in `C7_MUTATIONS.json` — emitted rather than exempted, as the commit claims. |
| 16 | MAJOR | `re` allowlisted deliberately | **LANDED** | `re` is in `STDLIB_ALLOWED` at `c7_b0_audit.py:101`, in the same literal as the other additions, and the committed walk shows `c7_factcheck.py` importing `re` with `unexpected: []`. |
| 17 | OBSERVATION | disposition committed, README amended | **LANDED** | `OPEN_NOTES_DISPOSITION_C7.md` is tracked as of `ce018ffa`; `README.md:81-91` no longer says "genuinely unclear". (But see N1: the README's own layout block was not updated to match the file it now describes.) |

**Tally: 15 LANDED, 2 PARTIAL (4, 13), 0 NOT_LANDED.**

On the good side, and it deserves saying plainly: I recomputed **every published number** from the
repaired modules, out of tree, and they are identical as exact rationals —

```
L1_tier1       cert 3.461283496693919   mine 3.461283496693919   exact match
L3_elementary  cert 3.586306093865387   mine 3.586306093865387   exact match   (U, E_R also exact)
L3_registry    cert 3.597941638997423   mine 3.597941638997423   exact match   (U, E_R also exact)
L3_lorden      cert 3.600337619876716   mine 3.600337619876716   exact match   (U, E_R also exact)
ceiling        cert 4.679910339516997   mine 4.679910339516997   exact match
PRIMARY key L3_elementary; MAX key L3_lorden; C7_CLASS STRENGTHENED
C4 margin 0.9439874105892059 %   PRIMARY margin 9.79331451382309 %
KG1 all > C4 floor: True    KG5 all ≤ A0 and ≤ ceiling: True    KG4 tier-k(k=1) == tier-1: True
```

Model sha `efcc0f36…` matches the pin; predecessors are tracked and clean; `c7_gaussian.py` is
byte-identical to C4's `c4_rigorous_gaussian.py` modulo the `c4_`→`c7_` rename (I diffed it directly).
**The repairs did not move the bound and did not damage the arithmetic.** That is the thing this
programme has failed five times, and it is clean here for the second review in a row.

---

## 5. New defects introduced by, or surviving, the repairs

**N1 — the README's layout block is stale in three places, introduced by this commit.**
`README.md:133` says "16-check state audit"; the audit now has 17 checks. `:135` says "15 mutants";
there are now 18. `:142` says "`OPEN_NOTES_DISPOSITION_C7.md` N1–N4"; the file has N1–N6, and N5 is the
section this adjudication was convened to test. `:129` says "9 kill gates" while the certificate now
enforces thirteen. The fact-checker cannot see any of these, because they are integers and its regex
requires four decimal places — an instance of its own declared blind spot, arriving in the same commit
that declared it.

**N2 — `lambda_lower_tier2` is dead, public, and unguarded.** It takes a **bare** `U` (no certificate,
no `_resolve_U`) and never calls `_require_in_cell`. Measured:

```
lambda_lower_tier2(e=1.90,  K=1/2, H=5, U=0.1, gate ladder)  ->  4.21903818040167   no refusal
lambda_lower_tier2(e=e_lo,  K=1/2, H=5, U=0.1, gate ladder)  ->  4.034025125455948  no refusal
```

That is the `U = 0.1` probe the README says was repaired (`:69-72`) and the out-of-cell `e` the erratum
says is now enforced (E1), both still reachable through a documented public entry point that the gate
itself references (`u0_ladder_for_tier2`). It has no caller, so nothing published depends on it — but
`ERRATUM_C7_GATE.md` E1's sentence "the side-conditions must be enforced in code, **which they now
are**" is not true of this function, and N5's "dead code removed" is not true of it either.

**N3 — `K` and `H` are not side-condition-checked at any theorem entry point.** This is the same
species as both CRITICALs and the review did not find it. `K` and `H` are free parameters of
`lambda_lower`, `lambda_lower_tier_k` and `certified_U`; nothing in `c7_theorem.py` enforces
`K = 1/2`, `H = 5` or `K + H = 11/2`. KG7 lives only in `c7_certificate.py:39`, where it tests that
module's own constants, and in the mutation suite's *mirror* pipeline (M07). Driving the **real** entry
point with a self-consistent certificate:

```
K=1/2 H=5    -> 3.600337620   (the published L3_lorden)
K=1/2 H=11/2 -> 3.925355098   NO REFUSAL    <- C4's documented threshold-confusion failure mode
K=1/2 H=6    -> 4.250984509   NO REFUSAL
tier-1 at H=11/2 -> 3.774230652 ;  at H=6 -> 4.090097516     NO REFUSAL
```

Both inflated values exceed the published PRIMARY, both are below the certified `A0` 4.867216117 and
below the E2-family ceiling 4.679910340, so **KG5 would not fire either**. This is a larger inflation
(+18.5 % at `H = 6`) than either exploit the review found, obtained through the public API with no
mutation, and it is exactly the error KG7 exists to catch. In fairness: `K` and `H` are frozen model
constants rather than gate "prospective choices", and the campaign's own producers hardcode them, so
no published number is affected — as with findings 1 and 2, the defect is in the mechanism.

**N4 — `c7_b0_audit.py:186` names a property it does not test.** The check is registered as *"gate
matches its frozen sha256 **and precedes the certificate**"* but its boolean is `gsha == GATE_SHA`
alone; the ordering half is never evaluated. (It is tested elsewhere, by `c7_factcheck.py` check 3, so
the fact is true — the check's name is what is false.) Separately, `chk(15)` is
`chk(15, "guard state discoverable…", True, …)` — a check whose condition is the literal `True` and
which counts toward "17/17". In a namespace whose entire theme is claims outrunning the code, both of
these are the wrong shape.

**N5 — three kill gates were added that the frozen gate does not contain.** The gate enumerates
KG1–KG9. The certificate now also enforces KG8b, KG9b, KG10, KG10b and KG11. Adding gates is
conservative in direction and I do not object to KG10/KG10b. KG11 is different in kind: it makes the
verdict depend on `criterion_holds_at_every_knot` in the ψ-monotonicity artifact — an analysis the
theorem explicitly **does not use** and the disposition records as NOT TAKEN. A failure there would
refuse an otherwise valid campaign. Not disclosed in the erratum.

**N6 — self-declared literals that no producer measures.** `MONTE_CARLO_RUNS: 4` is a hand-written
constant in `c7_certificate.py:228`; nothing in the tree can corroborate the count, or that there were
not more. `mirror_equivalence_asserted: True` is likewise a literal (`c7_mutations.py:222`) that KG8b
then checks — sound only because `main()` returns early when the mirror disagrees, so the gate is
vacuous as written. The review flagged the second at finding 13 and it was not repaired.

**N7 — within-commit ordering is unverifiable.** The certificate reads the mutation, primitives, ψ and
B0 artifacts and gates on them. All five files were committed together in `ce018ffa`, so
`c7_factcheck.py`'s commit-granular ordering check cannot establish that the certificate was produced
*after* the artifacts it consumes. I state this rather than infer it either way.

**N8 — a latent binding error in the certificate.** `c7_certificate.py:56` assigns `finiteness` inside
the `for src in (...)` loop; the published `step0` block at `:62` therefore reports the **last**
iteration's certificate (`lorden`), not the PRIMARY's. The values are source-independent today
(`E_tau_prime_finite` depends only on `e, K, H, c`), so the published figures are correct — but the
binding is accidental and would silently mis-attribute if the step ever became source-dependent.

**N9 — the ledger was not regenerated.** `evidence/phase1/C7_LEDGER.json` predates the repairs, was
not touched by `ce018ffa`, and carries no step-0 figure. Its numbers reproduce (I recomputed `E_R` and
the ceiling), so this is staleness, not error.

---

## 6. The questions I was asked to rule on

**Is `C7_CLASS = STRENGTHENED` right under the gate's frozen verdict rule?** *On the numbers, yes; on
the premise, contestable.* The rule requires the PRIMARY bound to strictly exceed C4's floor **and**
its margin over the C5-T critical `A0` to strictly exceed C4's. I reproduced both independently:
`3.5863060938653875 > 3.297250281519544` and `9.79331451382309 % > 0.9439874105892059 %`. The
`MARGINAL` and `NO_IMPROVEMENT` branches are correctly not taken. But the fourth class, `REFUSED`, is
defined as "any kill gate fires", and under KG8's literal text (§3) it does. The verdict is correct
given `kill_gates_fired: []`; whether that list is correct is finding 4.

**Is the PRIMARY selection correct?** *Yes.* The rule is "the largest bound whose dependency set is
EMPTY". The dependency-free set is `{L1_tier1 = 3.4613, L3_elementary = 3.5863}`; the max is
`L3_elementary`. I recomputed the selection from the modules and got the same key, and the same
`MAX_OVER_ALL = L3_lorden`. The dependency sets themselves are right: `elementary` returns `[]`,
`lorden` cites Lorden (1970), `registry` cites the Arb/FLINT surface. Importantly, the EMPTY claim for
`L3_elementary` no longer rests on an unexecuted step — that was finding 3, and it is repaired.

**Are the gate's `forbidden_conclusions` respected?** *Yes.* `README.md:36-38` states in terms that
cell 309 is not closed, that the exclusion concerns the deterministic operator-level route, that K5
remains PARTIAL with m = 5 open on [305, 309], that no other cell's status changes, and that the guard
stays DENY and the R-stage is not authorised. The certificate carries the list verbatim, scopes phase
10 `FEASIBILITY_ONLY` and frames phase 11 as a statement about the E2 family. I grepped the whole
namespace for closure/authorisation language and the only matches are the forbidden list itself. The
surface-independence overreach the review found at finding 8 is repaired.

**Is the Monte Carlo disclosure adequate, or should it block publication?** *Adequate; it should not
block.* The prohibition's purpose is to keep uncertified numerics out of the evidence chain, and
nothing entered it: I recomputed every certificate number from the modules with no reference to any
simulated quantity, and the only Monte Carlo figures anywhere in the tree are the five enumerated
prose exemptions and the certificate's explicitly-labelled `external_non_evidence_activity.result`.
The erratum records it as a breach rather than arguing it away, which is the right posture, and E4's
recommendation for the successor gate ("no Monte Carlo **in the evidence chain**") is the correct
lesson. Two residual weaknesses: `MONTE_CARLO_RUNS: 4` is uncorroborable (N6), and the campaign took
the "disclose" branch of the review's either/or while keeping the result, which is the weaker of the
two options it was offered. I would not withhold publication for it.

**Did the campaign effectively amend a frozen gate while claiming not to?** *The file, no. Its
enforcement, yes — in one place, undisclosed.* The gate blob is provably unchanged
(`ed9220350557b1784fa78a434ef5abb4839ad95c` at both `166224bb` and HEAD) and its sha still gates both
the certificate and B0. E1–E5 are corrections recorded outside it, which is the correct instrument for
a frozen artifact that turns out to be wrong, and E3's post-hoc choice of `c` is disclosed. But **KG8
was narrowed in the campaign's favour with no erratum entry** (§3), and three kill gates were added
with no erratum entry (N5). The first is the one that matters, because it is the only change that
makes a REFUSE into a PASS.

---

## 7. What I could not verify from the committed tree

- That `MONTE_CARLO_RUNS` is 4 and not more, or that the simulator was what E4 describes. Nothing in
  the tree can establish it; it is a declaration.
- That the certificate was produced after the artifacts it gates on, since they share a commit (N7).
- That `GATE_A_GRID`, `GATE_E_LO/HI` and `GATE_C_FINITENESS` in `c7_theorem.py` match their sources.
  They **do** — I checked the cell endpoints against `C4_CERTIFICATE.json#/cells/309` and the grid
  against the gate's prose — but *no code does*. The gate's sha covers the JSON, not the module, so a
  frozen constant has been moved from prose that bound nothing into code that nothing cross-checks.
  This is a strictly better place for it, and it is the next iteration of N6 in the disposition's own
  "what a successor should inherit" list.
- The re-run timings in the gate and the S6 ledger note; environment claims, as the review said.
- The provenance of `critical_A0_C5T` and `A0_certified_float`; outside this namespace, read as
  committed facts with their dependency sets correctly labelled.

---

## 8. Conclusion

The claim under test was `OPEN_NOTES_DISPOSITION_C7.md` → N5: *"ALL FINDINGS ADDRESSED."* That claim
is **substantially but not entirely true**, and it contains at least one entry that is false as
written ("13 | dead code removed"), which is the precise failure mode the programme convened this
adjudication to catch. It is a much smaller instance than the five that preceded it — a cosmetic item
mis-recorded, not a soundness repair mis-recorded — but it is the same shape, in the same document,
one commit after the campaign wrote that it had learned to stop doing this.

What is genuinely good, and I want it on the record because it is the first time: both CRITICAL
exploits are closed by **real, specific guards** that I drove myself from outside the tree, with the
honest path left intact and every published rational reproducing exactly. Step 0 executes. M11 drives
the real guard. The false 405× justification is gone and replaced by a true one. The coverage gap is
measured and its number is right. B0 walks everything and can be re-run. The primitives are tested.
Thirteen of the seventeen are clean repairs with nothing left over.

What blocks an unqualified acceptance is not arithmetic and not the mathematics. It is that the
certificate's `kill_gates_fired: []` is defended by a reading of KG8 that the frozen gate's text does
not support and that no erratum records; that a public entry point still accepts a bare `U` and an
out-of-cell `e`; that the frozen threshold `H` is enforced nowhere the theorem can be called; and that
the repair record again overstates itself in a small way. Every one of those is closable by a
bounded, mechanical change that cannot move a single digit of the result.

### Conditions

1. **KG8.** Either set `MUTATION_CLASS = "REFUSE"` and accept the consequence, or record an erratum
   entry (E6) that narrows KG8 explicitly — in the same form E1–E5 use — stating that a survivor whose
   effect does not alter a reported digit is not treated as a survival for gating purposes, and
   naming M01–M04. Do not leave the gate's text and the artifact's verdict in contradiction with
   nothing in the tree acknowledging it. If the erratum route is taken, tie the anchor to the exact
   rational the certificate publishes, not to IEEE-double equality.
2. **`lambda_lower_tier2`.** Delete it, or give it `_require_in_cell` and a `U` certificate. As
   committed it falsifies E1's "which they now are" and N5's "dead code removed".
3. **`K`/`H`.** Enforce `K = 1/2`, `H = 5`, `K + H = 11/2` at the theorem entry points, as `e` and `a`
   now are, and add a mutant that drives the **real** `lambda_lower_tier_k` with `H = 11/2` rather
   than only the mirror. This is C4's own failure mode and it is currently reachable for +18.5 %.
4. **Record corrections.** Fix N5's finding-13 row to say what was and was not done; update
   `README.md:129,133,135,142` to 13 gates / 17 checks / 18 mutants / N1–N6; fix `chk(16)`'s name or
   make it test what it says; replace `chk(15)`'s literal `True`.
5. **Disclose the added gates.** KG8b, KG9b, KG10, KG10b and KG11 are not in the frozen gate's
   `kill_gates` block. Record them in the erratum, with a note on why the verdict is now coupled to an
   analysis (KG11) the theorem does not use.
6. **Regenerate the ledger** so that the whole evidence chain postdates the repairs, and re-run the
   certificate last so the ordering it gates on is real; or state in the certificate that within-commit
   ordering is not establishable.

None of these conditions bears on the validity of `3.586306093865…` as a certified lower bound on
`Λ_309`, on the PRIMARY selection, on `STRENGTHENED`, or on the scope statements. I verified all four
independently and they hold.

ACCEPTED_WITH_CONDITIONS
