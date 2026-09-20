# Independent pre-freeze review — Campaign C1 (`p5y_k5_tail_operator_registry`), branch `p5y-k5-tail-operator-registry` @ `4ccee386`

**VERDICT: NOT_READY** — the science reproduces exactly, but the frozen gate's material-improvement test is
implemented with a different quantity than the gate states; under the gate as written C1's class is MARGINAL and the
frozen selection rule says STOP, not EXECUTE.

Reviewer context: fresh context, did not write this work. Everything decision-relevant was recomputed from the
committed evidence with an independently written exact-rational implementation
(`fractions.Fraction` only, stdlib only), built from `THEOREM_TC.md`, `THEOREM_TCT.md`, `THEOREM_AD.md`,
`C1_OPERATOR_EXTENSION.md` and `k5b_check.k5b_literal`, importing none of `c1_forecast.py`, `tct_rule.py`,
`tc_rule.py`, `tc_crosscheck.py` or `deflated_consume.py`. Those files were read only afterwards, to explain the one
disagreement. No file in the worktree was modified except this one; no remote host was contacted; no writing git
command was run.

The independent implementation was validated before use by reproducing Campaign B's Lemma-G baseline **exactly**
(magnitudes `4.257154729064679 / 4.151682079144239 / 4.040056656988599 / 4.005124051293261 / 3.964274326087183`,
Γ(305) = `-0.043751780433257684`) and by reproducing the gate's own `required` values
(4.891579 / 3.905056 / 3.076148 / 2.432398 / 1.969828) in closed form.

---

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| 1 | `config/FEASIBILITY_GATES_C1.json` added at `36d8e39b`, exactly once (`git log -- <gate>` returns one commit, `A` only) | PASS | `git log --follow` → single commit `36d8e39b`; `--name-status` shows `A` and no `M` anywhere |
| 2 | gate sha256 = `927ecfc7597c…2ceb98`; blob identical at `36d8e39b` and at HEAD (`a1ee8bf1ff4a…`) | PASS | `shasum -a 256`; `git rev-parse 36d8e39b:<gate>` == `git rev-parse HEAD:<gate>` |
| 3 | `36d8e39b` is an ancestor of HEAD | PASS | `git merge-base --is-ancestor 36d8e39b HEAD` → 0 |
| 4 | no file reporting a tail operator constant, a TC-T magnitude or a K5-B outcome predates the gate | PASS | namespace commit graph: `36d8e39b` (gate + README) → `09524c0a` (Phase A) → `ee1e4385` (registry builder) → `492fdbea` (forecast evaluator) → `4ccee386` (all registry/forecast/mutation **evidence**). Every evidence file is added at `4ccee386`, four commits after the gate |
| 5 | gate `start_frontier` `76c37de1` is Campaign B's last commit, and the gate is the first C1 commit after it | PASS | `git log` — `76c37de1` at 17:41:51, gate at 17:50:25 |
| 6 | gate's classes, scenarios, baseline, closure rule and selection rule are stated precisely enough to follow mechanically | PASS | Note 6 lists what the gate deliberately leaves free (block geometry, alpha ladders, κ choice); none of those is a class input |
| 7 | `c1_forecast.classify()` is a faithful transcription of STRONG / USEFUL / MARGINAL / INFEASIBLE | PASS | line-by-line against `gate["classes"]`; `beyond_305 = [k for k in closed if k != 305]` is exactly `∩ {306,307,308,309}` since `closed ⊆ {305..309}` |
| 8 | USEFUL's "at least one closed cell in {306..309}" is a fair reading, not an advantage to C1 | PASS | Note 7 — it is **stricter** than "closes ≥ 2 currently-open cells" (all five are open in r4, so {305,306} would satisfy the looser phrasing) |
| 9 | gate baseline value `2.252903` verified against Campaign B's committed evidence | PASS | `ATOM_CONSTANT_REQUIREMENT.json` / `TAIL_FORECAST_R2.json` `uniform_A_reduction_needed[309] = 2.2529025166407797`; independently re-bisected here to `2.2529025166399…` |
| 10 | gate baseline `magnitudes` and `required` verified | PASS | reproduced exactly from the committed inputs (see header) |
| 11 | **the material-improvement test is implemented as the gate states it** | **FAIL** | **Note 1** — the recorded "now" value `1.890224226409337` is `1/margin = M_after/M_needed`, a *magnitude* ratio; the baseline `2.252903` is an *atom-constant* reduction factor. The two are different quantities |
| 12 | **C1's class under the gate as written** | **FAIL** | **Note 2** — MARGINAL, not USEFUL; `selection_rule` ⇒ stop before freeze |
| 13 | Lemma Dv′ atom constants reproduced independently, exactly, on all five cells | PASS | A0/A1/A2 identical to `C1_FORECAST.json` `constants[*].c1_LemmaDv_prime` to full printed precision; e.g. 305 → `6.884064161921174 / 47.612938182348756 / 814.6298812805493` |
| 14 | C3: A0 better by 1.104×–1.128×, A1 ≈ unchanged, A2 worse | PASS | A0 reductions `1.1044 / 1.1156 / 1.1098 / 1.1233 / 1.1277`; A1 `0.9609–1.0090`; A2 `0.7376–0.7985` ⇒ **worse by 1.2523×–1.3557×**, matching the claimed "1.25×–1.36×" |
| 15 | C4: the five TC-T magnitudes, `H_tail_exact`, `M_after_exact`, `Gamma_exact` (CERTIFIED) | PASS | exact-rational string equality on all 15 recorded exact fields; Γ = `-0.065100279 / -0.005719468 / +0.061683080 / +0.136194543 / +0.198810311` |
| 16 | C4: per-r radii of cell 305 | PASS | `2.264870745938 / 2.870960247987 / 3.473271755996 / 4.147880894664 / 4.651800219621` — identical to `detail.305.per_r_rad` |
| 17 | DEGRADED scenario (constants × 5/4) reproduced exactly; closes only 305 | PASS | Γ = `-0.005072250 / +0.060100529 / +0.135948892 / +0.221563682 / +0.293631556`; all `Gamma_exact` strings match |
| 18 | no empty intersection at any (cell, m); m = 1, 2, 3 stay complete on 0–309; nothing regresses | PASS | intersections non-empty for all 5 cells × m ∈ {1,2,3,5} in both scenarios; Note 8 gives the monotonicity argument that regression is structurally impossible |
| 19 | reported margins are exact | INFO | Note 9 — margins use the gate's 6-dp-rounded `required`, so they are right only to ≈ 1e-7 relative. Display-only here |
| 20 | my implementation is capable of failing (perturbation sweep) | PASS | Note 10 — 31 perturbations at 1e-4; every load-bearing input moves Γ; the three that do not are explained and expected |
| 21 | C1 uses the adopted certification machinery unchanged | PASS | `TC.block_artifact(lo,hi,α,0,2,20,False)`, `TC.block_artifact(lo,hi,α,2,2,12,True)`, `TC.cell_artifact(e0,ρ,τ,C,degree=20)` — argument-for-argument identical to `build_registry._block` / `._cell` except the α ladder |
| 22 | block geometry: one block per cell = the cell's own interval; `block_for` (r2) resolves each cell to exactly one block, exact coverage, no gap | PASS | verified by hand against `deflated_consume.block_for`: for each cell the open-overlap test hits exactly `[cell]`; `e_hi(305) == e_lo(306) == 680769/400000` etc., `lo_cov == x_lo`, `hi_cov == x_hi` |
| 23 | a wider block is a **stronger** certification obligation, and C1 says so | INFO | Note 11 — true (Lemma T with E = the whole cell), but the spec states the geometry change without stating its direction, and the accuracy it costs is not mentioned |
| 24 | alpha ladders are deterministic, in the source before the evidence, and **every cell certified at the first alpha** | PASS | `REGISTRY_C1.json`: `taboo_alpha = 6/5` (first of `TABOO_ALPHAS`) and `arl_alpha = 5/4` (first of `ARL_ALPHAS`) on all five cells; ladders committed at `ee1e4385`, evidence at `4ccee386` |
| 25 | the ARL ladder is "the frozen `build_registry` ladder extended upward", as the source comment says | INFO | Note 12 — the frozen ARL ladder is ρ-dependent (`full_alphas(ρ)`); C1's is a fixed 6-rung list. The taboo ladder *is* the frozen one extended |
| 26 | `taboo_certify.py` is "executed from its pinned bytes", as the spec's table claims | **FAIL** | Note 13 — `c1_tail_registry.py` sets `TABOO_SHA256 = None  # … record, do not enforce`; `c1_inputs_verify` also pins it with `None`. The bytes do match (`ced9422c…`), so no result is wrong — the *control* is claimed and not implemented |
| 27 | `NEW_REAL_ADDRESSES = 0` is actually true | PASS | Note 14 — the registry builder forms only kernel/supersolution objects and reads only `cells.json`; `c1_forecast` reads K1 records, but only to consume adopted values (C_upper, aux evidence, R/D/R2/M_R2), which is consumption, not a new real evaluation |
| 28 | registry internal consistency: τ ≥ 1, C_T ≥ τ, D_lo > 0, Ā ≥ 1, and Lemma Dv′ never exceeds Lemma Dv (r2 ≤ r1) | PASS | all five cells; r1 constants recomputed here and `A_j(r2) ≤ A_j(r1)` holds for every j |
| 29 | the Arb-precision operator certification itself (`certify_block`, `certify_cell`, the supersolution inequalities, the Bernstein ranges) | NOT_CHECKABLE_LOCALLY | `import flint` → ModuleNotFoundError; `import numpy` → ModuleNotFoundError |
| 30 | `c1_tail_registry verify` (recompute every artifact from its own payload) | NOT_CHECKABLE_LOCALLY | same reason — it calls `TC.verify_block` / `TC.verify_cell` |
| 31 | `block_for` is exercised by C1 | INFO | Note 15 — `c1_forecast` passes `blocks[k]` straight to `atom_constants_r2`; the adopted resolution function is never called. The property it would check holds (row 22), verified by hand |
| 32 | Ā is load-bearing | INFO | Note 16 — `Ā_eff = min(Ā, τ/D_lo) = τ/D_lo` on **all five** cells, so the whole-kernel ARL certification (half the 1232 s build) never touches a result |
| 33 | D: Γ(306) = −0.005719468 and the margin is 1.9 % | PASS | Γ exact; margin `1.0192604…` ⇒ 1.926 %; |Γ| is 1.89 % of the drift term `R.hi − e0·D.lo = −0.302674156` |
| 34 | D: the DEGRADED scenario loses cell 306 | PASS | DEGRADED Γ(306) = `+0.060100529` |
| 35 | D: the spec reports the thinness prominently and honestly | PASS | `C1_OPERATOR_EXTENSION.md` §2 gives it a bolded paragraph of its own and ties it to the class. Note 3 gives my opinion on adopting 306, and Note 17 flags one unreproducible number in that paragraph |
| 36 | E: A2 degradation and the d₂ = D2/D_lo = 22.8–37.1 explanation | PASS | d₂ = `37.088 / 32.606 / 29.067 / 25.902 / 22.801`; it enters A2 additively in Lemma Dv′ and is the dominant new term |
| 37 | E: `C1_DIAGNOSTIC_MIN.json` reproduces and "changes nothing" | PASS | every A, mag, Γ, margin and pass flag in the file reproduced exactly; same two cells close |
| 38 | E: the componentwise minimum would not rescue the gate either | INFO | Note 4 — under the min, the still-required atom-constant reduction at 309 is `2.0748782`, a 7.90 % fall: still short of 10 % |
| 39 | F: `c1_mutations.py` re-runs locally and reports 19/19 | PASS | re-ran to `/tmp/your_mutations.json`; **byte-identical** to the committed `C1_MUTATIONS.json` (sha `2033824d…`) |
| 40 | F: the M03 retarget is honest and the original miss correctly diagnosed | PASS | Note 18 — confirmed independently: Lemma G's constants enter no C1 result (my perturbation sweep shows Γ is invariant to them) |
| 41 | F: "19 of 19 **mutants**" and "the frozen gate's section 8 list" | **FAIL** | Note 5 — M15–M18 are not mutants (two are `substring in source_text` assertions); the real mutant count is 15. Neither the C1 gate nor gate B has a "section 8" — the suite is self-selected, not gate-mandated |
| 42 | F: the computation that decides the campaign is covered by a mutant | **FAIL** | Note 5 — no mutant touches `classify()` or the material-improvement block. That is exactly where the defect of Note 1 sits |
| 43 | F: other coverage gaps | INFO | Note 5 — no individual mutant for Ā (undetectable anyway, row 32), C_T, D1, D2; the DEGRADED 5/4 factor; the frozen `k5b_literal` chain (the suite re-implements the direct test inline) |
| 44 | G: N1 — no order-3 entry point is reached | PASS | no C1 module imports the order-3 producer; `order3 = None` on every `tail_enclosure` call; `c1_forecast` refuses a measurement with `order3_fields_present` |
| 45 | G: (P3′) preserved — no midpoint quantity where TC-T needs a whole-cell bound | PASS | my independent tower implementation uses the midpoint tower for σ₃ and the mean-value-corrected cell tower for σ₄ and reproduces Campaign B exactly; `h:1:3` confirmed non-binding (perturbing it moves nothing), as `THEOREM_TCT.md` §3 states |
| 46 | G: C1's own six constants are whole-cell by construction | PASS | each is `block_artifact`/`cell_artifact` on `[left, right]`, never at e₀ |
| 47 | G/C8: adopted namespaces byte-unchanged; the diff `76c37de1..HEAD` is purely additive inside the C1 namespace | PASS | `git diff --name-status 76c37de1 HEAD` — 28 files, all `A`, all under `p5y_k5_tail_operator_registry`; nothing outside |
| 48 | G/C8: coverage map r4 untouched, no r5 exists, `main` untouched, Campaign B reviews untouched | PASS | r4 sha still `a3bddd83…`, last touched at `f2ac1eb3` (pre-frontier); `find -name '*COVERAGE_MAP_R5*'` → 0; no C1 commit on any main branch; `review/` last touched at `f2674899` |
| 49 | G: nothing in the namespace pre-empts the freeze, qualification or adjudication | PASS | no artifact asserts adoption, sealing, qualification or a coverage-map change; the README states r4 "remains authoritative until an adopted C1 result says otherwise" |
| 50 | G: README phase table still shows phases B and C as "—" | INFO | Note 19 — stale (it was frozen with the gate and never updated); harmless, but a reader of the README alone cannot tell the campaign ran |
| 51 | H: the spec's §1 table of certified constants | **FAIL** | Note 20 — cell 305's Ā, D_lo and D1 are wrong (8.221 / 0.7692 / 1.5875 vs the registry's 8.290719 / 0.768609 / 1.618684). The other 27 entries are right and the computation uses the JSON, not the table |
| 52 | H: Phase A input verification 7/7 | PASS | re-ran `c1_inputs_verify.py` locally: `A1..A7 all true`; identical to the committed evidence except `head` (expected) |
| 53 | H: compute gate respected | PASS | `cpu_seconds_total = 1232.19` s = 0.342 CPU-h, against a forecast cap of 8 and a hard cap of 12 |
| 54 | H: `C1_FORECAST.gate_frozen_before_forecast` | INFO | Note 21 — a hard-coded `True` in the output dict, not a computed check. The fact is true (rows 1–4); the field is an assertion |
| 55 | H: `MAIN` pin in `c1_inputs_verify.py` | INFO | declared at line 22 and never used — a dead pin |
| 56 | H: κ₁, κ₂ choice in Lemma Dv′ | INFO | Note 22 — C1 uses the literal `0.7978846 / 0.9678830` (valid, conservative) rather than the tighter drift-aware `cert.norms["k"]`. This is the adopted `deflated_consume` default, so it is the right call, but it is another unused tightening |
| 57 | H: full end-to-end replay of `c1_forecast.py` (310 K1 records, the 262-field identity gate, `derived_identity_gate`, the `k5b_literal` chain over cells 0–309) | NOT_CHECKABLE_LOCALLY | the sealed K1 record store is not in the repo; `--records DIR` cannot be supplied. The tail arithmetic, which is what the claims rest on, *was* reproduced exactly from the committed extracts |

---

## Notes

### Note 1 (FAIL, decisive) — the material-improvement test compares two different quantities

The frozen gate states:

> `material_improvement_test`: "the **uniform atom-constant reduction factor** still required by the WORST still-open
> tail cell falls by at least 10 per cent relative to the baseline above (2.252903 at cell 309)."

and its `baseline.uniform_atom_constant_reduction_still_needed` is `{305: 1.0, 306: 1.071062, 307: 1.361618,
308: 1.771344, 309: 2.252903}`. That dictionary is Campaign B's `uniform_A_reduction_needed`, which
`tail_forecast_r2.atom_constant_requirement` computes by **bisecting a uniform scale factor on (A0, A1, A2)** — the
namespace's own Phase A verifier (`A6_baseline`) binds the gate's baseline to exactly that field.

`c1_forecast.py` computes the "now" value as

```python
worst_now = max(F(str(1)) / F(cert["_margins_exact"][str(k)]) for k in still_open)
```

with `margins[k] = need[k] / M_after`. So `worst_now = M_after / M_needed` — a **magnitude** reduction factor. It is
not the atom-constant reduction factor, and the two differ materially because the enclosure has a part that does not
scale with A (the centre Ĥ_r(a) and the W terms).

Recomputed independently (my own bisection, validated by reproducing Campaign B's baseline to 1e-12):

| measure (worst still-open cell = 309 in every case) | baseline | C1 | fall | 10 % test |
|---|---|---|---|---|
| uniform **atom-constant** reduction (what the gate says) | 2.252903 | **2.1015968** | **6.716 %** | **FAIL** |
| **magnitude** reduction, applied consistently to both ends | 2.0124980 | 1.8902242 | 6.076 % | **FAIL** |
| as recorded: magnitude "now" vs atom-constant baseline | 2.252903 | 1.8902242 | 16.098 % | PASS |

Only the mixed comparison passes, and the mismatch is worth ≈ 10 percentage points of "fall" — the whole distance
between failing and passing. The same conclusion holds under every variant I tried: no still-open cell reaches a 10 %
fall on the atom-constant measure (307: 7.31 %, 308: 6.09 %, 309: 6.72 %), and the componentwise-minimum variant does
not reach it either (Note 4).

Cross-checks that this is a real defect and not a definitional quibble:
- The baseline's own *magnitude* ratios are `1.0632 / 1.3133 / 1.6466 / 2.0125` on cells 306–309 — demonstrably not
  the `1.071062 / 1.361618 / 1.771344 / 2.252903` the gate records, so the gate's baseline is unambiguously the
  atom-constant measure.
- `atom_constant_requirement`'s docstring is explicit: "the factor by which A0,A1,A2 (uniformly) … must fall".
- The comment above the block in `c1_forecast.py` reads "material-improvement test, **exactly as the gate states
  it**". It is not.

This is not a rounding or presentation problem. It is the single arithmetic test the gate created so that
"materially improves the remaining blocker" would be "decided by arithmetic and not by narrative", and it decides the
campaign.

### Note 2 (FAIL) — the class and the selection verdict change

Feeding `material = False` through `c1_forecast.classify()` unchanged:

- not STRONG (`n_c = 2 ≠ 5`);
- not USEFUL (`n_c ≥ 2` ✓ and `beyond_305 = [306]` ✓, but `material` ✗);
- MARGINAL (`n_c ≥ 1`).

The gate's `selection_rule`: "C1 is executed through freeze, qualification, seal, consumption and adjudication only
if its class is USEFUL or STRONG. Below USEFUL is never executed; MARGINAL and INFEASIBLE both stop before freeze."
And the gate's `stop_rule` then requires a costed C2 continuation plan.

So the recorded `"C1_CLASS": "USEFUL"` and `"selection_verdict": "EXECUTE"` do not follow from the frozen gate.

Note also the `no_redefinition` clause: the classes, the baseline and the material-improvement test "are not changed
after any C1 forecast or result is seen. If they are found to be wrong, the campaign stops and a successor owns the
replacement gate." A repair that redefines the test to the magnitude measure at both ends is therefore *also* not
available to C1 — and it would fail anyway (6.076 %). The honest paths are: (a) fix the implementation to the gate's
own quantity, accept MARGINAL, stop before freeze and write the C2 plan; or (b) stop and hand a corrected gate to a
successor. Either way C1 does not freeze on this evidence.

### Note 3 (opinion) — cell 306 at a 1.9 % margin

Verified: Γ(306) = −0.005719468 against a drift term of −0.302674156, i.e. |Γ| is 1.89 % of the term it has to
overcome, and the K5-B margin `M_needed/M_after` is 1.0192604 (1.93 %). The DEGRADED scenario loses it.

The margin is not statistical, and that is the right defence as far as it goes: every quantity in the chain is a
certified upper bound, so 1.9 % of headroom is 1.9 % of *real* headroom, not a confidence interval. But the same
observation cuts the other way, and harder:

1. Every input is an upper bound produced by a *different* piece of machinery — the frozen K1 δ/ε stack, the Aux3
   order-3 evidence, the J/h tower, the W enclosures, and now six Arb-certified operator constants on a domain where
   **no prior certified evidence exists at all** (the disposition document says so plainly, and I agree that is the
   honest statement of C1's trust boundary). A single sign, index or premise error anywhere in that chain eats 1.9 %
   without a trace.
2. The one genuinely new trust surface — the tail operator registry — is the one I could not check locally
   (rows 29–30), and its own re-verification path needs the same absent toolchain.
3. Cell 306 is not a bonus. Under the gate, USEFUL requires a closed cell beyond 305; 306 is the only one. If 306
   falls, C1 closes {305} alone, `n_c = 1`, and the class is MARGINAL regardless of Note 1. The entire campaign
   outcome rests on 1.9 %.
4. C1's own frozen robustness probe — the scenario the gate created precisely so that "a knife-edge closure cannot
   be reported as a clear one" — says 306 does not survive a 25 % degradation.

What I would require before adopting 306, in order of value:
- **an independent re-certification of the six operator constants on cell 306** by a second implementation (or at
  minimum a second execution on a second host) — this is the un-gated surface and it is where the margin lives;
- **a finer taboo block partition on 306** (the adopted r1 geometry is 1/100-wide blocks; C1 uses one block of width
  2ρ ≈ 0.0867). Finer blocks give a tighter sup over each block and hence smaller C_T and τ, which is where A0 comes
  from. This is the cheapest available real margin and C1 leaves it unused (Note 11);
- **a stated, frozen margin floor** for adoption. If the programme is willing to adopt at 1.9 %, it should say so
  before it sees the number, not after;
- adoption of 305 alone in the meantime, which is uncontested (margin 1.239×, survives DEGRADED) and is a legitimate
  `partial_adoption` outcome under the gate.

On the presentation: the spec is honest here. §2 gives the thinness its own bolded paragraph, states the 1.9 %,
states that DEGRADED loses it, and explicitly attributes the USEFUL-not-STRONG class to it. That is the right
behaviour and I want to say so. (One number inside that paragraph is not reproducible — Note 17.)

### Note 4 (INFO) — the componentwise minimum, and whether refusing it was right

`C1_DIAGNOSTIC_MIN.json` reproduces exactly under my implementation: A-constants, magnitudes
(3.9265382 / 3.8116662 / 3.7411484 / 3.7331190 / 3.6808843), Γ, margins and pass flags all identical. The claim that
it "changes nothing" is correct for the closed set and the class.

On the decision itself: I think C1's reasoning is right, for a reason C1 does not give. The gate says the CERTIFIED
scenario is "the atom constants the frozen operator machinery actually certifies over the tail domain, used **exactly
as theorem AD Lemma Dv′ prescribes**". A componentwise min of Lemma G and Lemma Dv′ is not "exactly as Lemma Dv′
prescribes", and `no_redefinition` forbids changing the scenario after seeing the result. That is a literal reading,
but it is the reading the gate exists to enforce, and the alternative — reaching for a sharper composition precisely
because the specified one degraded — is the failure mode the clause names. Refusing it while recording the
diagnostic anyway is the right handling of a decision-relevant number, and I would have criticised the opposite.

It is also moot for the outcome, which is worth stating: under the min, the required uniform atom-constant reduction
at 309 is `2.0748782`, a 7.90 % fall — still short of the gate's 10 %. Taking the min would not have rescued USEFUL.

### Note 5 (FAIL) — the adversarial suite is smaller and less gate-bound than claimed

The suite re-runs locally and is byte-identical to the committed evidence; that part is exactly what a reviewer wants
and Campaign B could not offer. Three problems with how it is described and scoped:

1. **"19 of 19 mutants" overcounts.** Ten source mutants (M01–M09, M03b) and five data mutants (M10–M14) are real:
   they change code or inputs and the run detects the change. M15 is a property assertion (the four assembly tables
   differ). **M16, M17 and M18 are `substring in source_text` checks** — e.g. M16 is
   `'raise SystemExit(f"cells outside the frozen C1 universe' in src`. They never execute the guard they claim to
   test and would pass against dead or wrong code. The honest count is 15 mutants plus 4 static assertions.
2. **"the frozen gate's section 8 list" does not exist.** `FEASIBILITY_GATES_C1.json` has no section 8, and neither
   does `FEASIBILITY_GATES_B.json` (I checked both; the C1 gate contains no occurrence of "adversarial" or
   "section 8"). If the intended referent is `THEOREM_AD.md` §8 — the six registry obligations — then the suite
   mutates two of the six (τ via M12, D_lo via M11) and leaves Ā, C_T, D1 and D2 without an individual mutant. Either
   way the suite is self-selected, and describing it as discharging a frozen list overstates it.
3. **The gap that mattered.** No mutant touches `classify()` or the material-improvement block of `c1_forecast.py`.
   A suite of 15 mutants aimed almost entirely at the enclosure arithmetic passed 15/15 while the one computation
   that flips the campaign's verdict (Note 1) went unexercised. A mutant that perturbs `base_worst` or swaps
   `worst_now` for the atom-constant bisection would have caught it immediately.

Other uncovered items, for the record: the DEGRADED factor 5/4; the α ladders and block geometry; the frozen
`k5b_literal` chain (the suite re-implements the direct test inline rather than calling it); and Ā — which no mutant
could detect anyway, since it never binds (Note 16).

### Note 6 (INFO) — what the gate does and does not fix

The gate fixes the universe, the scenarios, the closure rule, the predicate, the baseline, the classes, the
material-improvement test and the selection and stop rules, all in terms that follow mechanically from numbers. That
is a good gate and it is genuinely frozen (rows 1–5).

What it leaves free, and which C1 therefore chose *after* the freeze: the block geometry, the α ladders, the
supersolution degrees, and the κ₁/κ₂ bounds. None of these is a class input and all of them are deterministic and
committed before the evidence, so I do not treat any of them as post-hoc tuning. But they are the levers that set the
constants, and a successor gate should pre-register them — especially the block width, which is the one lever with
real margin left in it (Note 11).

### Note 7 (INFO) — USEFUL's extra conjunct is stricter, not laxer

All five tail cells are open in coverage map r4, so "closes at least two currently-open tail cells" would be
satisfied by {305, 306} without any further condition. The gate additionally demands that one closed cell lie in
{306,307,308,309}, and its own baseline note explains why: "cell 305 is already closable by TC-T alone, so closing it
is NOT by itself material progress for C1". That is a self-imposed handicap, and `classify()` transcribes it
faithfully. No advantage to C1 here.

### Note 8 (INFO) — why no previously passing cell can regress

Independent of the forecast's own report (which shows `regressed: []` for every m in both scenarios): the TC-T
composition can only intersect, so `M_after ≤ M_R2` and `H_after ⊆ H_record`. In `k5b_literal`, Γ is increasing in M,
so Γ can only fall; `mu` and `ell` are increasing in `H.lo`, which can only rise; and `U = max(γ, γ − μ·Δx²/2)` is
decreasing in μ. Every channel therefore moves toward passing. Cells 0–304 are untouched. Regression is structurally
impossible, not merely unobserved.

### Note 9 (INFO) — margins carry a 1e-7 rounding

`c1_forecast` takes `M_needed` from `gate["baseline"]["required"]`, which is rounded to 6 decimal places, so the
reported margins differ from the exact values in the 8th significant figure (e.g. 305: recorded `1.23913050721774`,
exact `1.239130616…`). Harmless for display and for the STRONG test (≥ 11/10), but note that `1/margin` is precisely
what Note 1's defective test consumes, so the same rounding propagates there.

### Note 10 (INFO) — my implementation is capable of failing

31 single-input perturbations at +1e-4 on cell 306. Γ moved for: τ, C_T, D_lo, D1, D2; A0, A1, A2 separately; ρ, x_hi
and e0; `sup.F/D/H`; `norms.k[1]`, `k[4]`, `j[2]`; `sup_S0[4]`; `H_at_a`; the `W2` lower endpoints; `delta_H`;
`eps_src[3]`; the Aux3 `S:4:3` and `h:3:3` suprema; and the record's `R.hi` and `D.lo`. Three did not move, all
correctly: Ā (never binds, Note 16), `W2['0:0'].hi` (the magnitude comes from the lower endpoint), `h:1:3` and
`M_R2` (both documented as non-binding in `THEOREM_TCT.md` §3 and by `M_after = mag < M_R2`).

### Note 11 (INFO) — the block geometry is sound, and is stated without its direction

Lemma T is quantified over the drift set E, so certifying `w ≥ 1 + K̂_e w` uniformly on a block of width 2ρ ≈ 0.081–0.108
is a **stronger** obligation than on the adopted r1's 1/100-wide blocks, and the resulting C_T and τ are whole-cell
sup bounds by construction. So C1's choice is conservative and the constants are valid — the claim is fine.

Two things the spec does not say. First, it never states that direction; §1 presents the geometry as a neutral
change ("one block per tail cell … so `block_for` resolves each cell to exactly one block"). Second, the conservatism
costs accuracy: under the adopted rule a cell takes the worst over the sub-blocks meeting it, and nine 1/100-wide
sub-blocks would each admit a tighter supersolution than one block nine times as wide. A0 = τ/D_lo is where C1's
whole gain lives, so this is the cheapest untaken tightening in the campaign — and it bears directly on the 1.9 %
margin at cell 306 (Note 3).

### Note 12 (INFO) — the ARL ladder is not the frozen one

`c1_tail_registry.py` comments the ladders as "the frozen `build_registry` ladders, extended upward for the tail".
That is exact for the taboo ladder: frozen `(6/5, 13/10, 7/5)` → C1 `(6/5, 13/10, 7/5, 3/2, 2, 3)`. It is not true of
the ARL ladder: the frozen one is ρ-dependent, `full_alphas(ρ) = (1 + 200ρ + 1/50, 1 + 400ρ + 1/20, 5/4, 7/5)`, whereas
C1's is a fixed `(5/4, 7/5, 3/2, 2, 3, 5)`.

Substantively this is fine — at tail ρ ≈ 0.04–0.054 the two ρ-dependent rungs evaluate to ≈ 9.1 and ≈ 18, which are not
sensible starting proposals — and α only steers the *float proposal* for the candidate; certification is a verified
inequality on the resulting exact payload, so a badly chosen α costs CPU, not soundness. But the provenance sentence
should say what was actually done.

### Note 13 (FAIL) — a pin that is claimed but not enforced

`C1_OPERATOR_EXTENSION.md`'s table says the certification machinery is "adopted, **executed from its pinned bytes**".
`c1_tail_registry.py` disables that: `TABOO_SHA256 = None  # filled from the C1 protocol when one exists; None =
record, do not enforce`. `c1_inputs_verify.PINS` also carries `taboo_certify` with a `None` hash. So nothing in C1
would refuse a modified `taboo_certify.py`; the registry merely records whatever it ran.

Mitigation, stated fairly: the recorded hash `ced9422c…` does match the committed file today, the file is byte-unchanged
since the start frontier (`A4_immutability` passes and my own `git diff 76c37de1..HEAD` is empty outside the C1
namespace), and `c1_forecast` *does* enforce the pin on `deflated_consume` (`ef5d0474…`). So no result here is in
doubt. The defect is that a provenance control is asserted in the theorem document and not implemented — the kind of
gap that matters precisely when someone later re-runs the build on a host where the file is not byte-checked.

### Note 14 (INFO) — `NEW_REAL_ADDRESSES = 0` holds, with the boundary stated precisely

The registry builder reads `cells.json` (sha-pinned) for the cell intervals and nothing else; `taboo_certify` forms
the kernel K_e, its atom split, h₁ = 1 − K_e1 and polynomial supersolutions. No source S_r, no candidate of F/D/H/G,
no K1 record, no value of R.

`c1_forecast` *does* read the sealed K1 records — via `tail_forecast_r2.adopted_state` — for `C_upper`, the Aux3
auxiliary evidence, the recorded R/D/R2 intervals and `M_R2`, and it runs the 262-field identity gate and the derived
identity gate against them. That is consumption of adopted values, which is exactly what the gate permits
("Deterministic operator certification and registry construction are permitted"), not a new real evaluation. The
guard stays DENY and I found no path that would form a new scientific address.

`c1_tail_registry` does put `p5y_k5_order3_readiness_audit/code` on `sys.path`, but only to import `k5_minimality`
for the cover loader. No gated order-3 entry point (`certify_real_cell`, `rung3_engine.certify_order3`,
`rung3_residual.g_residual`) is imported or reached anywhere in the namespace.

### Note 15 (INFO) — `block_for` is asserted, not exercised

`c1_forecast` passes `blocks[k]` directly into `atom_constants_r2`; the adopted `deflated_consume.block_for` is never
called, so the spec's "`block_for` resolves each cell to exactly one block with exact coverage" is a claim about a
function C1 does not run. I verified the property by hand against `block_for`'s r2 branch (row 22) and it holds
exactly, including the open-interval rule that keeps the abutting neighbour out. Calling `block_for` and asserting a
single hit would turn a documentation claim into a check, for free.

### Note 16 (INFO) — one of the six certified constants is inert

`Ā_eff = min(Ā, τ/D_lo)`, and on all five cells `τ/D_lo` is the smaller: 6.884 / 6.411 / 5.987 / 5.590 / 5.210 against
Ā = 8.291 / 7.912 / 7.556 / 7.218 / 6.901. So the whole-kernel ARL supersolution — one of the two `block_artifact`
certifications per cell, and roughly half the 1232 CPU-s — contributes nothing to any C1 number, and a wrong Ā would
be undetectable by any check in the namespace. The e = 0 precedent where Ā binds (the adopted R3 C_e0 = 469.8 against
a float 466) does not transfer to the tail. Worth recording so that a successor does not pay for it again, or pays
for it knowing it is a redundancy check rather than an input.

### Note 17 (INFO) — one number in the thin-cell paragraph does not reproduce

§2 says "Γ = −0.005719 against a penalty term of ≈ 0.43". I cannot reproduce 0.43. The two natural readings are
ρ·x_hi·M_after = 0.296955 and |R.hi − e0·D.lo| = 0.302674; the closest candidate I found is ρ·x_hi·M_R2 = 0.420639, the
penalty *before* C1's tightening, which rounds to 0.42. The error is in the conservative direction (it makes the
margin look like 1.33 % rather than the true 1.89 %), and the accompanying "the margin is 1.9 %" is correct
(1.926 %). Still, this is the one paragraph whose whole job is to convey the thinness accurately.

### Note 18 (INFO) — the M03 retarget is honest

The comment says an earlier M03 edited `atom_constants_generic` (Lemma G), went undetected, and was correctly
diagnosed as testing code no C1 result depends on. I confirmed this independently before reading the comment: in my
perturbation sweep, Lemma G's constants do not enter Γ at all — C1 consumes the Lemma Dv′ constants and uses Lemma G
only to report the comparison table, and the gate's baseline numbers come from the frozen gate, not from
`atom_constants_generic`. The retarget to the A0 contribution inside `radius()` puts the mutant where C1 actually
spends A0. Disclosing an undetected mutant and its diagnosis rather than quietly deleting it is the right behaviour.

### Note 19 (INFO) — the README is stale

The phase table still shows "B. tail operator certification and forecast" and "C. execution decision under the frozen
gate" as "—". It was committed with the gate and never updated. Harmless, but if C1 is re-scoped after this review the
README is the natural place to record what actually happened.

### Note 20 (FAIL) — the spec's §1 constants table is wrong for cell 305

| cell 305 | spec §1 | `REGISTRY_C1.json` |
|---|---|---|
| Ā | 8.221 | **8.290719** |
| D_lo | 0.7692 | **0.768609** |
| D1 | 1.5875 | **1.618684** |

The other 27 entries of the table (C_T and τ on 305, and all six constants on 306–309) are correct to the precision
printed. The computation reads the JSON, and `C1_FORECAST.json`'s `constants.305.operator` block carries the correct
values, so no result is affected. But this is the document's headline presentation of what was certified, on the
cell with the largest margin, and three of its six numbers are not the certified ones. It needs correcting before
freeze, and it makes me wonder what else in the prose was transcribed rather than generated — which is the same
failure mode Campaign B's own commit `76c37de1` had to repair.

### Note 21 (INFO) — `gate_frozen_before_forecast` is an assertion

`C1_FORECAST.json` carries `"gate_frozen_before_forecast": true`, written as a literal into the output dict. The real
check is `c1_inputs_verify.A2_gate` (gate sha, added exactly once, `len(gate_commits) == 1`), which passes. Since this
is the campaign's headline governance claim, the forecast should recompute it rather than assert it — or drop the
field and point at A2.

### Note 22 (INFO) — the κ bounds are the conservative ones

Lemma Dv′ needs bounds on ‖∂ⁿK̂‖. C1 uses `K1_BOUND = 0.7978846`, `K2_BOUND = 0.9678830` — the whole-line κ₁ = √(2/π),
κ₂ = 4φ(1) of Lemma K, and valid upper bounds (√(2/π) = 0.79788456…, 4φ(1) = 0.96788276…). The frozen drift-aware
`cert.norms["k"]` are tighter on the tail cells (k₁ = 0.7976691, k₂ = 0.9670471) and are also valid, since
‖∂ⁿK̂_e‖ ≤ ‖∂ⁿK_e‖ ≤ k_n on the cell. Using them would improve A1 by ≈ 0.02 % and A2 by ≈ 0.03 % — negligible, and
using the adopted `deflated_consume` default is the right call. Recorded only so that the choice is visible: C1's
constants are conservative in this respect too.

---

## What I did not check

- **The operator certification itself.** `taboo_certify.certify_block` / `certify_cell` require `python-flint` (Arb at
  256 bits) and `numpy`; neither is installed here. I could not verify a single supersolution inequality, Bernstein
  range, truncation allowance or the degree-20/degree-12 candidate payloads. This is the campaign's one genuinely new
  trust surface and it is entirely unverified by this review. `c1_tail_registry verify` is unavailable for the same
  reason.
- **The end-to-end forecast replay.** `c1_forecast.py` needs the sealed 310-record K1 store (`--records DIR`), which
  is not in the repository. The 262-field producer identity gate, `tct_rule.derived_identity_gate`, and the
  `k5b_literal` chain across cells 0–309 were therefore not executed by me. I reproduced the decisive tail arithmetic
  from the committed extracts (`TCT_INPUTS_305..309.json`, `ADOPTED_TAIL_INPUTS.json`, `REGISTRY_C1.json`,
  `cells.json`) and matched every exact field the forecast records.
- **The two "independent second paths" inside C1** (`_atom_constants_independent` and
  `tct_rule.tail_enclosure_crosscheck`) as *independence* claims. I confirmed the Lemma Dv′ formula by writing a third
  implementation from `THEOREM_AD.md` that agrees exactly, and the mutation suite exercises the enclosure crosscheck.
  I did not audit `tail_enclosure_crosscheck` for hidden shared helpers — that was Campaign B's review scope.
- **CPU and cost claims.** `cpu_seconds_total = 1232.19` and the per-cell ≈ 246 s are not reproducible locally; I
  checked only that they are consistent with each other and inside the gate's caps.
- **Whether the α ladders were chosen before the build rather than after a failed attempt.** The only evidence is the
  commit order (`ee1e4385` before `4ccee386`), which is sufficient for the record but is not independent timestamping.
  Mitigating: α steers only the float proposal, not the certification.
- **The wider programme state** (adoption status of the predecessor namespaces, the remote hosts, the export tree).
  Out of scope and no remote contact was made.

---

## Verdict counts

| verdict | count |
|---|---|
| PASS | 37 |
| INFO | 11 |
| NOT_CHECKABLE_LOCALLY | 3 |
| **FAIL** | **6** |
| total | 57 |

(PASS: rows 1–10, 13–18, 20–22, 24, 27–28, 33–37, 39–40, 44–49, 52–53. INFO: 19, 23, 25, 31, 32, 38, 43, 50, 54, 55,
56. NOT_CHECKABLE_LOCALLY: 29, 30, 57. FAIL: 11, 12, 26, 41, 42, 51.)

FAILs: #11 and #12 (Note 1, Note 2 — the material-improvement test and the resulting class/verdict), #26 (Note 13 —
the unenforced `taboo_certify` pin), #41 and #42 (Note 5 — the suite's size and gate-binding are overstated, and the
deciding computation has no mutant), #51 (Note 20 — the spec's §1 table is wrong for cell 305).

**FINAL VERDICT: NOT_READY.**

The mathematics is in good shape and I want to be clear about that: every atom constant, every per-r radius, every
enclosure endpoint, every M and every Γ in `C1_FORECAST.json` and `C1_DIAGNOSTIC_MIN.json` reproduced **exactly**
against an independent exact-rational implementation, in both scenarios; the registry is internally consistent; the
block geometry is sound and conservative; the (P3′) repair is preserved and re-tested; `NEW_REAL_ADDRESSES = 0` holds;
the adversarial suite re-runs byte-identically; and the immutability and gate-timing claims (C1 and C8) are true as
stated and verified against the commit graph rather than the prose.

C1 fails at governance, not at science, and it fails on the one test the gate was written to make unarguable. Under
the gate as frozen, the still-required uniform atom-constant reduction at the worst still-open cell falls from
2.252903 to 2.1015968 — 6.7 %, against a 10 % threshold — so the material-improvement test does not pass, the class is
MARGINAL, and the frozen selection rule says stop before freeze and write a costed C2 continuation plan. Because
`no_redefinition` forecloses repairing the test after the result is known, and because the test fails under the
magnitude measure too (6.1 %), I do not see a path to freeze on this evidence.

Recommended disposition: do not freeze. Correct `c1_forecast`'s material-improvement computation to the gate's own
quantity, re-emit the forecast, record the MARGINAL class, and proceed under the gate's `stop_rule`. Cell 305 remains
a legitimate `partial_adoption` candidate on its own merits (margin 1.239×, survives DEGRADED) if the programme wants
to bank it separately; cell 306 should not be adopted at 1.9 % without the independent operator re-certification and
the finer block partition described in Note 3. The other five FAILs are all repairable in place and none of them
changes a number.
