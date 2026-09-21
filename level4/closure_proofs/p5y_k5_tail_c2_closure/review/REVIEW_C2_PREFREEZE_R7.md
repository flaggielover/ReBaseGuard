# Seventh independent pre-freeze review — K5 Campaign C2

**VERDICT: NOT_READY** — 41 rows, 33 PASS, 6 NOTE, **2 FAIL**. Both text only; neither touches a computed number.
The D-stage arithmetic is sound and I could not break any of it. What blocks the freeze is, for the fourth
consecutive round, the campaign's account of *itself*: the commit that claims to have abolished hand-maintained
counts left four of them standing in the same file, two already stale, and asserts in two places that none
survives. Separately, the cross-platform re-certification claim that answers the predecessor reviewer's condition 2
rests on a build-host column that no committed artifact records, and the erratum says that complaint "is answered".

## Reviewer context

Fresh context. I wrote none of this work and took no part in rounds one to six. Worktree
`/Users/suzhe/ReBaseGuard-k5c2`, branch `p5y-k5-tail-c2`, HEAD `5a098ec6`, reviewed 2026-09-21. Read-only
throughout: no file in this namespace or any other was modified except this review file, no writing git command was
run, AWS was not touched in any way, and no lifecycle artifact (freeze, qualification, seal, coverage map,
adjudication) was created or pre-empted.

**What I re-derived independently, from committed evidence, with my own code:**

- the three gap falls, from the frozen gate's own baseline gaps and the forecast's requirement values
  (0.46285183, 0.24593099, 0.18389841), and the material-tightening verdicts under `gap ≤ 0.80 × gap_baseline`;
- the `D_STAGE_CLASS` decision by applying the four frozen class definitions by hand, and separately by reading
  `classify()` against them line by line;
- the exact sign of Γ on all five cells from `Gamma_exact`;
- the blocker ranking on all five cells from `radius_grouped` (f_F > f_D > f_H everywhere, to the digit printed in
  the prose table), and the C_T admissibility clamp / `gain_per_unit_of_input_moved` / `per_unit_comparability`
  placement from the D1 evidence;
- the whole-cell soundness premise of the mixed-operator route: that each tail cell equals `[e₀−ρ, e₀+ρ]` and
  equals `[left, right]` in the frozen cover, that **C1's block is exactly that interval on all five cells**, and
  that C2's 9/9/10/11/11 sub-blocks tile it exactly with every width ≤ 1/100;
- the registry's own worst-over-cover composition (max on C_T/τ/D1/D2, min on D_lo) on all five cells;
- Lemma Dv′ applied to the componentwise-best operator tuple, reproducing the published `operator_mixed` A-vector
  on all five cells, and its gap falls 57.27 / 30.57 / 23.03 %;
- the critical ratios and the +8.0 / +11.1 / +16.2 % improvement over the true C1 column;
- the `MEASURE_CHANGE_SELF_AUDIT` arithmetic (raw falls 9.61/9.81/9.64 %, gap-equivalents 48.16/25.07/19.08 %,
  and the 15.708 % fall that would have made C2 USEFUL under C1's gate verbatim);
- **every leaf of `C2_D1_BLOCKER.json` across all four commits that have ever touched it** — 487 leaves initially,
  exactly nine ever replaced, all C_T `magnitude`/`delta_vs_base`/`relative_gain` on 307/308/309, 525 at HEAD,
  nothing that existed at `ef58310c` removed;
- byte-for-byte reproduction of `c2_critical_ratio.py`, `c2_d1_blocker.py` and `c2_mutations.py`; and
  `c2_b0_verify.py` identical except the recorded `head`;
- **an independent Arb/FLINT re-certification of five registry artifacts** on the venv build (macOS 26.5.2 /
  arm64 / Python 3.14.5 / numpy 2.5.3 / python-flint 0.9.0), spanning three different cells and both artifact
  kinds, at both precisions;
- the additivity and in-namespace confinement of `5289b6ce..5a098ec6`, the gate sha at every commit that touches
  it, the immutability of the D5 producer and artifact, `main`, and coverage map r4.

**What I did not check** is in its own section below.

## Checklist

| # | check | verdict | evidence |
|---|---|---|---|
| **A. Integrity** |
| 1 | `5289b6ce..5a098ec6` is entirely additive and entirely inside the C2 namespace | **PASS** | 137 entries, **all `A`**; `git diff --name-status` filtered on the complement of `p5y_k5_tail_c2_closure/` is empty; no entry with status other than `A` |
| 2 | frozen gate sha `098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f`, one commit only | **PASS** | `git log -- config/FEASIBILITY_GATES_C2.json` → exactly `87309610`; sha256 identical at `87309610` and at `5a098ec6`; the D5 artifact records the same string |
| 3 | `c2_d5_forecast.py` and `C2_D5_FORECAST.json` unmoved since `5a94568a` | **PASS** | `git log` on both paths → `5a94568a`, `51f8844b`; nothing later |
| 4 | `main` untouched | **PASS** | `main` at `c123b9bb`; `git log main -- <namespace>` empty |
| 5 | coverage map r4 intact, no r5 | **PASS** | `K5_COVERAGE_MAP_R4.json` sha256 `a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35`; repo-wide `-iname '*COVERAGE_MAP_R5*'` → nothing |
| 6 | nothing pre-empts freeze, qualification, seal, adoption or adjudication | **PASS** | no freeze / qualification / seal / consumption / adjudication artifact anywhere in the namespace; `CELL_306_ADOPTION.md` is a proposal with both branches pre-committed; guard DENY, `NEW_REAL_ADDRESSES = 0` |
| 7 | producers reproduce byte-for-byte | **PASS** | `c2_critical_ratio.py` → `2995246193d4…` = committed; `c2_d1_blocker.py` → `1d7715a2b887…` = committed; `c2_mutations.py` → `512180f32a5c…` = committed. Note 1 for `c2_b0_verify.py` |
| 8 | adversarial suite current and honest | **PASS** | my re-run: `applied 43, real_mutants 35, static_assertions 8, detected 40, equivalent [M19, M20, M32], undetected [], pass true`; `OPEN_NOTES_DISPOSITION_C2.md:25`'s "35 real mutants and 8 static assertions" matches. No stale "33" survives outside r1's own frozen review file |
| 9 | the six review files are committed verbatim, one commit each | **PASS** | `git log -- review/` → one commit per file, never amended; r7 is the only file this review writes |
| **B. The four load-bearing repairs named for this round** |
| 10 | critical-ratio column relabelled; true C1 values substituted | **PASS** | `R_STAGE_DESIGN.md:2` table now reads "Lemma G (Campaign B) \| **C1 (true)** \| **C2**" with 32.03283 / **34.55795** / **37.32219** (307), …/20.93621/23.26035 (308), …/12.18694/14.15799 (309). `D_STAGE_DECISION.md:5` carries the same three C1 figures. Both match `C2_CRITICAL_RATIOS.json` to the digit: my re-run gives C1 34.557952668899276 / 20.936212876634386 / 12.186944853482373 |
| 11 | the +8.0 / +11.1 / +16.2 % improvement is the true C2-over-C1 figure | **PASS** | computed from the artifact: 37.32219/34.55795 − 1 = **+8.00 %**, 23.26035/20.93621 − 1 = **+11.10 %**, 14.15799/12.18694 − 1 = **+16.17 %**. The old "16–34 %" (C2 over Campaign B) appears nowhere except as a disclosed correction |
| 12 | the producer refuses unless it reproduces both anchors | **PASS** | `C2_CRITICAL_RATIOS.json` carries `anchors.campaign_B_lemma_G_critical_ratio: "reproduced bit-exactly"` and `anchors.campaign_C2_critical_ratio_Gamma_and_attribution: "reproduced bit-exactly"`; the script emits nothing otherwise, and it reproduced byte-for-byte here |
| 13 | D1 §1 blocker ranking corrected to f_F > f_D > f_H | **PASS** | from `radius_grouped` at every cell: 305 f_F 0.602 > f_D 0.320 > f_H 0.170; 306 0.545 / 0.340 / 0.179; 307 0.475 / 0.342 / 0.177; 308 0.378 / 0.322 / 0.161; 309 0.285 / 0.282 / 0.135 — identical to the prose table, column order and all. `DOMINANT_BLOCKER_3.term = order0_residual_fF` on every cell |
| 14 | the JSON was right from the start, as claimed | **PASS** | `git show 5a94568a:…/C2_D1_BLOCKER.json` → `DOMINANT_BLOCKER_3 = {'share': 0.006024755326775572, 'term': 'order0_residual_fF'}`. The prose was the wrong copy; the correction is disclosed at `D1_BLOCKER_DIAGNOSIS.md:19–25` |
| 15 | the registry verifier's nesting defect is fixed, and fixed structurally | **PASS** | `c2_refined_registry.py:201–203` reads `rec = got.get("recomputed", {})` then indexes `rec[fld]`, so a missing field raises rather than comparing against `None`; `:209` likewise indexes `["tau"]` directly. The cause is recorded in-source at `:197–200` |
| 16 | the verifier now demonstrably passes, with the artifact count reconciling | **PASS** | `C2_REGISTRY_VERIFY.json`: `artifacts_rechecked 105`, `cells_checked 5`, `pass true`, `problems []`, registry sha and host recorded. 105 = 50 `taboo_block` + 50 `taboo_cell` (9+9+10+11+11 sub-blocks) + 5 `arl_cell`, matching the committed file set exactly |
| 17 | C_T sensitivity admissibility guard present and enforced | **PASS** | `c2_d1_blocker.py:71–72` raises `PremiseRefusal` unless `Dlo > 0 and tau >= 1 and C >= tau and Abar >= 1`. The 309 C_T row carries `admissibility_clamp` naming C_T/1.1 = 4.277739 < τ = 4.418493, `relative_gain 0.009335012952053988` = the published +0.9335 % |
| 18 | the inadmissible figures are gone and the correction is disclosed, not silent | **PASS** | +1.3681 / +1.1502 / +0.9335 % published; +1.3823 / +1.3945 / +1.3887 % named as the inadmissible predecessors at `D1_BLOCKER_DIAGNOSIS.md:70–76`. My leaf diff confirms those are the only nine values ever replaced |
| 19 | `gain_per_unit_of_input_moved` is emitted on the C_T row only, with the comparability limit in the artifact | **PASS** | cell 309's sensitivity rows are `A0, A1, A2, A_all, C_T, C_upper_frozen, D1, D2, D_lo, rho_frozen, tau`; only `C_T` carries the field, and it carries `per_unit_comparability`. τ and D_lo carry `relative_gain` only, and the ordering holds there: D_lo 0.08718593 > τ 0.08168084 |
| 20 | the withdrawn "refuses exactly as `deflated_consume.atom_constants`" claim is gone from the source comment r3 named | **PASS** | `c2_d1_blocker.py:67–70` now states the guard "enforces the four premise inequalities ONLY. It is deliberately NOT a claim of equivalence", and records the withdrawal. `grep -rn 'refuses exactly'` over `code/` → nothing |
| **C. The structural de-counting repair (the subject of r6 FAIL 1)** |
| 21 | `README.md` prose carries no hand-maintained tally | **PASS** | `:69–78` says "Every independent pre-freeze review so far has returned NOT_READY" and "— **repeatedly** — an error introduced by a *repair*". "Four", "five" and "three separate times" are gone. `git diff ec5b08ca..5a098ec6` confirms removal, not update |
| 22 | the README review table's FAIL counts reconcile against each review's own verdict | **PASS** | 6 / 3 / 1 / 3 / 2 / 1 against r1 `\| **FAIL** \| **6** \|` (total 79), r2 `\| **FAIL** \| **3** \|` (total 71), r3 "1 FAIL", r4 "3 FAIL", r5 "2 FAIL", r6 "1 FAIL" |
| 23 | `ERRATUM_C2.md` prose carries no hand-maintained tally, as `:267–269` claims | **FAIL** | **Four survive, two already stale, and two sentences assert that none does.** FAIL 1 |
| 24 | the two tables are the only places a count appears, as `:268–269` claims | **FAIL** | the erratum's own round table at `:7–14` is a third, and `README.md:71` calls its own table "the only place in this namespace that counts them". FAIL 1 |
| 25 | the pattern table itself is accurate and complete | **PASS** | 11 rows, each traceable to a named review FAIL or a named self-audit commit; I checked each against the round it cites and found no misattribution. Only the *prose count of its rows* is wrong (FAIL 1) |
| **D. The D-stage result** |
| 26 | gap falls re-derive from the frozen baseline | **PASS** | 1 − 0.1407635748126312/0.2620572570527464 = **0.462852**; 1 − 0.5002877825423833/0.663450928753142 = **0.245931**; 1 − 0.8990148694205993/1.1015967636536343 = **0.183898**. Identical to `gap_fall_fraction` |
| 27 | material-tightening verdicts under the frozen 20 % rule | **PASS** | `gap ≤ 0.80 × gap_baseline`: 307 True, 308 True, 309 **False** (0.899015 > 0.881277). Matches `materially_tightened` |
| 28 | Γ signs and the closed subset | **PASS** | from `Gamma_exact`: 305 −0.088029 < 0, 306 −0.030469 < 0, 307/308/309 > 0. `closed [305, 306]`, `still_open [307, 308, 309]` |
| 29 | the class is mechanical under the frozen classes | **PASS** | not `D_STRONG` (2 ≠ 5); not `D_USEFUL` (309 not materially tightened); `D_PARTIAL` (≥ 1 closed). Applied by hand to the gate text, independently of the code |
| 30 | `c2_d5_forecast.classify()` is a faithful transcription | **PASS** | `n == 5 → D_STRONG`; `n >= 2 and all(materially_tightened[k] for k in still_open) → D_USEFUL`; `n >= 1 → D_PARTIAL`; else `D_INSUFFICIENT`. Word for word the gate. `mt` is `gap <= (1 - thresh) * base_gap` with `thresh` read from the gate, and closed cells are excluded from `still_open`. The one gate hole (no cell closed but some tightened) is resolved to `D_INSUFFICIENT` and **disclosed in the docstring** rather than by amending the gate; unreachable here. Note 2 |
| 31 | margins, degradation and the R-attribution figures are consistent across documents | **PASS** | margin = M_needed/M_after = 4.891579/3.615110 = 1.35309 and 3.905056/3.511946 = 1.11194; `Gamma_degraded_125pct` −0.033733 (closes) and +0.029163 (does not); perfect-order-3 magnitudes 1.1311/1.1744/1.1995 and Γ −0.1718/−0.1267/−0.0873 — all matching `D_STAGE_DECISION.md` §3 and §5 and `R_STAGE_DESIGN.md` §1 |
| 32 | 2.69 CPU-h and 0 new real addresses | **PASS** | `REGISTRY_C2.cpu_seconds_total 9687.63` = 2.691 h; registry is `operator_only: true`, `rule: r2`; no order-3 field anywhere; guard DENY |
| **E. The 306 re-certification and the 105-artifact verification** |
| 33 | `C2_RECERTIFY_306.json` is internally sound and correctly summarised | **PASS** | 18 artifacts; both passes `all_ok true`, `certified true` on all 18 at both precisions; verdict `BOTH_PASSES_OK`. The consumed fields are asserted 45 times in the safe-side pass (C_T 9, τ 9, D_lo 9, D1 9, D2 9), exactly the "45/45" claimed; `diagnostic_deviations {count 27, worst_relative 5.3188e-30}` matches the prose "5.19 × 10⁻³⁰" for the worst *violating* one and "27 that moved at all" |
| 34 | the Arb/FLINT machinery actually reproduces — my own spot-check | **PASS** | `taboo_certify.py` sha `ced9422c…` matches its pin. At **256 bits**, `taboo_block_306_00`, `taboo_cell_306_00`, `taboo_block_305_00`, `taboo_cell_309_10` and `arl_cell_306` each re-certify and every published field is **bit-identical**. At **384 bits** all five still certify, all consumed bounds hold safe-side (C_T, τ, D1, D2 ≤ published; D_lo ≥ published) while the three diagnostics move — exactly the published behaviour, extended to two cells the 306 artifact does not cover |
| 35 | the cross-platform claim's *re-certifying* half is recorded | **PASS** | both `C2_RECERTIFY_306.json` and `C2_REGISTRY_VERIFY.json` record `platform`, `machine`, `python`, `numpy`, `python_flint` |
| 36 | the cross-platform claim's *build* half is recorded, and the erratum's account of it is accurate | **FAIL** | `CELL_306_ADOPTION.md:33–38`'s left column is sourced nowhere; `ERRATUM_C2.md:100–101` says the complaint "is answered". FAIL 2 |
| 37 | the campaign does not overclaim a second *implementation* | **PASS** | `CELL_306_ADOPTION.md:77` "This is still one implementation, run twice. A second, independently written certifier is the real answer, and no campaign in this programme has built one"; carried as N9. That part is exactly right |
| **F. The 384-bit test treatment** |
| 38 | the consumed-constant comparisons were not weakened post hoc | **PASS** | `git diff 12585997..8aee1fc5` on `c2_recertify_306.py`: the branches change from `key in UPPER` / `key in LOWER` to `key in CONSUMED_UPPER` / `key in CONSUMED_LOWER`, with the inequalities `g_ <= p_` and `g_ >= p_` **character-identical**; C_T, τ, D1, D2, D_lo are in both sets, so they hit the same test before and after. Only the test *string* gained "ASSERTED:". Unchanged again at `55c4cf00` |
| 39 | the strict determinism branch was not weakened | **PASS** | `elif strict: good, test = p_ == g_, "equal"` is outside every hunk of both diffs — byte-identical across all three versions. The bool branch `(p_ == g_ and g_ is True)` is likewise unchanged and runs in both passes, and `main()` additionally raises on `not r["certified"]` |
| 40 | the separation is sound rather than a moved goalpost | **PASS** | judged, not taken on trust: see Note 3 |
| **G. Referring the 306 margin floor out** |
| 41 | the referral is compliant with the frozen `D_PARTIAL` rule | **PASS** | judged against the gate text and both pre-committed branches: see the answer to G. Note 4 |

## Notes

**Note 1 (NOTE) — `c2_b0_verify.py` reproduces except for the recorded HEAD.** My re-run gives
`85e4e4a6…` against the committed `646a2c21…`. The entire difference is one leaf: `head` is
`5289b6cee713…` in the artifact and `5a098ec6…` in my run. All seven checks still return true
(`ALL_PASS`). The artifact was produced at the start frontier and records the commit it ran at, so this is correct
behaviour, not drift — but the namespace nowhere says the B0 artifact is reproducible only modulo that field, and a
reviewer who runs `cmp` will see a mismatch and have to work out why. One sentence would fix it.

**Note 2 (NOTE) — the `classify()` gap resolution is right, and its scope statement is slightly generous.** The
frozen gate leaves "closes no cell, but some still-open cell is materially tightened" outside all four classes.
`classify()` resolves it to `D_INSUFFICIENT` and says so in the docstring, which is the correct handling: record the
resolution rather than amend a frozen pre-registration. The docstring calls the case "unreachable in C2 (which
closes two)", which is true of the run that happened; it is reachable in principle by the same code on other
inputs, which is why the resolution matters at all. Non-blocking.

**Note 3 (NOTE, and my judgement on F) — the CONSUMED/DIAGNOSTIC separation is sound, and the reason is stronger
than "these are only diagnostics".** Three things make it sound rather than a moved goalpost, and I checked each:

1. *Nothing that carries the soundness claim changed.* The five constants the registry composes and Lemma Dv′
   consumes are asserted safe-side in both versions with character-identical inequalities (row 38), and the strict
   determinism pass still demands bit-identity on **every** field including the three diagnostics (row 39). My own
   256-bit runs confirm that demand is met on artifacts from three different cells.
2. *The load-bearing content of the diagnostics is still asserted, unconditionally, at both precisions.*
   `certify_block` sets `ok = (margin > 0 and wmin >= 0)`, and `certified is True` is required in both passes —
   once by `main()`'s `raise SystemExit`, once by `compare()`'s bool branch. So the positivity of the margin and
   the non-negativity of w_min are re-established at 384 bits from scratch. What is no longer asserted is only
   whether their low-order digits land on the same side of a rounding boundary.
3. *The recomputation is self-certifying.* Even if a published `allowance_upper` is off by 5e-30 in the unsafe
   direction, the 384-bit pass does not rely on that published value: it recomputes the certification inequality at
   384 bits and requires it to pass. My spot-check reproduces exactly this pattern — at 384 bits
   `margin_lower_bound`, `w_min_lower_bound` and `allowance_upper` all move while `certified` stays true and every
   consumed bound holds.

The disclosure in `DIAGNOSTIC_NOTE` is honest about the order of events ("introduced AFTER seeing a result"), and
the earlier "not a bound anyone relies on" wording — which was wrong, because `allowance_upper` *is* an input to
the certification inequality — has been withdrawn in the module itself. The one claim I cannot verify from
committed evidence is "passed 45/45 as originally written", because the failing run was never committed; I verified
the structural equivalent, which is that the branch that would have produced those 45 comparisons is unchanged, and
that the current run passes all 45. That is enough.

**Note 4 (NOTE, and my judgement on G) — the referral is compliant, and the reason is in the rule's own wording.**
The frozen `D_PARTIAL` rule requires that "a non-empty closed subset is **always** adopted when the adjudication
chain completes". It does not specify *which* non-empty subset, and it gives its own reason for existing: that
"declining to adopt it preserves nothing and has twice already left a soundly closed cell 305 unadopted". Both
pre-committed branches adopt cell 305, so the rule is satisfied in either. The campaign is not narrowing the rule;
it is declining to supply a number — the margin floor — that the gate never asked it for and that it is
disqualified from setting, having seen 11.2 % first. The pre-commitment is committed before any adjudication
exists, is symmetric, and resolves the "declines to set one" case *against* C2's interest (adopt 305 alone). The
adverse facts are stated in the table an adjudicator reads: margin 1.112× against 305's 1.353×, and Γ under
×1.25 degradation +0.029163 — **306 does not survive it while 305 does** (−0.033733), which I confirmed from
`C2_ROBUSTNESS_AND_R_ATTRIBUTION.json`. This is the opposite of an evasion. Two smaller points: the ×1.25 scenario
is not a gate input and the document says so; and "independent derivations closing it — 4 / 3" counts reviewer
implementations alongside campaign derivations, which is defensible but is the kind of hand-maintained figure that
goes stale (see FAIL 1).

**Note 5 (NOTE) — `D1_BLOCKER_DIAGNOSIS.md` never states which supply it is computed under.** Every number in that
document comes from C1's registry: `c2_d1_blocker.py:82` reads `registry_c1/REGISTRY_C1.json`, and the evidence file
carries a field literally named `closes_under_C1_constants`. So §1's requirements (1.262057 / 1.663451 / 2.101597)
are the C1 baseline, §3's magnitudes (3.9476 … 3.7234) are C1's, and §2.3's "certified 4.42" is C1's τ. None of
that is wrong, and the phase ordering (D1 diagnoses, D2/D3 refine, D5 forecasts) makes it inferable. But the prose
never says it, and C2's own published magnitudes are 3.615110 … 3.400934 — a reader who lands on §3 first has no
label telling them the two sets are different supplies. Given that r1 FAIL 61/62 were *exactly* a column labelled
with the wrong campaign, one clause ("all figures in this document are under C1's certified constants") is cheap
insurance. Six reviewers including me reproduced this file bit-exactly and none was actually misled, which is why
this is a NOTE and not a FAIL.

**Note 6 (NOTE) — `compare()` silently skips a field present in the published artifact but absent from the
recomputation.** `for key, val in got.items(): if key not in pub: continue` iterates the *recomputed* dict, so a
consumed constant that `verify_block` stopped emitting would simply never be compared, and both passes would still
report `all_ok`. This is the mirror image of the defect r1's row 79 exposed in `c2_refined_registry.verify`, which
was fixed by indexing `rec[fld]` so a missing field raises. Nothing is wrong today — my spot-check confirms all
five consumed fields are emitted on the relevant artifact kinds — and the D5 producer and the registry verifier
both index directly. But the recertification module is the one place that would not notice. Worth one line for a
successor; not blocking.

## FAIL 1 — the de-counting repair is incomplete, and asserts twice that it is complete

This is the finding that blocks the freeze, and it is the fourth consecutive round in which the blocking defect is
the campaign's account of its own review history.

`5a098ec6`'s commit message is "delete every hand-maintained count from prose, rather than update one more". In
`README.md` it did exactly that, thoroughly, and I could not find a surviving count there (row 21). In
`ERRATUM_C2.md` it did not, and it added two sentences claiming it had.

**The two claims:**

> `:4–5` — "The table below is the count; **no sentence in this namespace states one**, for the reason given in
> §'The pattern, named'."

> `:278–279` — "The table below is the campaign's only tally of them; **no other sentence in this namespace states a
> count**, because hand-maintained counts in prose are themselves one of the recurring defects…"

> `:267–269` — "So **every hand-maintained tally has been deleted from prose in both `README.md` and this
> section**, and **the two tables** — the review list at the top of the README, and the instance table below — **are
> now the only places a count appears**."

**What actually survives in prose, in the same file:**

1. **`:16` — "Across all **five** rounds no Γ, magnitude, margin, requirement, gap fall, class or adopted-subset
   value has changed".** Six rounds are dispositioned, in the table **two lines above this sentence**. `5a098ec6`
   added the r6 row to that table and left this sentence untouched: `git diff ec5b08ca..5a098ec6` shows the r6 row
   added at `@@ -10,6 +11,7 @@` and this line in the immediately following unchanged context. This is the
   campaign's single most important reliability claim, and it is stale by one in the file's opening paragraph.
2. **`:331` — "Across **five** rounds, **no Γ, magnitude, margin … has changed**".** The same claim, the same
   staleness, in §"The pattern, named" — the section whose subject is stale counts left by repairs.
3. **`:280` — "**three separate instances** below are a number left stale by a later edit"**, which is the
   *second clause of the same sentence* that says no other sentence states a count. It is also contradicted by
   `:266–267`: "**Three** of the instances in the table below are a count left stale by a later edit; **this was
   the fourth**." The instance referred to as "the fourth" is r6 FAIL 1, which **is** the last row of that very
   table. So the table now holds four of them and `:280` says three.
4. **`:246–247` — "Independently recounted here: r1 60/10/3/6, r2 62/4/2/3, r3 31/7/1, r4 28/4/3."** A prose tally
   that (a) stops at r4 although r5 and r6 are dispositioned in the same document, and (b) gives r4 four NOTEs
   while `:207` of the same file transcribes r4's header as "28 PASS, **5 NOTE**, 3 FAIL", with no sentence
   reconciling the two. Both are defensible individually — r4's checklist does contain exactly four cells reading
   `NOTE`, which I counted — but the file states both numbers for the same quantity and explains neither.
5. **`:335` — "reproducing bit-exactly under **four** independent implementations".** Another prose count, now an
   undercount: six rounds have reproduced the result, and r6 re-derived the gap falls itself.

And the "two tables" claim is wrong on its own terms: the erratum's round table at **`:7–14` is a third table that
counts** — it is where the 6/3/1/3/2/1 FAIL figures live. Meanwhile `README.md:71` says the README's table "is the
only place in this namespace that counts them", which the erratum's table contradicts, and which the erratum's own
"two tables" sentence contradicts by naming a different pair.

**Why this blocks rather than being a NOTE.** It is not prose quality. It is a false claim about the campaign's own
reliability, made twice, in the document the erratum itself calls "the document an adjudicator reads first" — and
the specific falsehood is that the recurring defect has been structurally eliminated. Two of the survivors are
already stale by exactly that defect, and one of them is the headline "the result has never moved" sentence. r6
blocked on "a wrong count of how many independent reviews the campaign had survived, in the front-door document",
and C2 accepted that framing at `:271–274`. The same defect is now in the second front-door document, introduced by
the commit that announced its abolition. That is the twelfth instance of the pattern, and it is of the sub-type the
pattern table already names twice: a neighbouring sentence the fix failed to carry along.

**Minimal change required.** Delete the count from each of `:16`, `:280`, `:331` and `:335` (e.g. "Across every
round", "several of the instances below", "under every independent implementation that has reproduced it"); delete
or complete `:246–247` and, if it is kept, say in one clause why it differs from `:207`; and correct `:268–269` and
`README.md:71` so that each describes the tables that actually exist. Per the campaign's own operational lesson —
make the change and stop — nothing else in either file needs to move, and no computed number is involved.

## FAIL 2 — the build-host half of the cross-platform claim is unattested, and the erratum says the provenance complaint is answered

Condition 2 of cell 306's adoption was "an independent re-certification … or at minimum a second execution on a
second host". r1's row 51 refused it partly because "`REGISTRY_C2.json` records **no host, no toolchain, no
precision**, so it cannot even be established that a second host was used."

`CELL_306_ADOPTION.md:28–31` restates that correctly. Then `:33–38` presents this:

> | | the worker that built the registry | the host that re-certified |
> | OS / arch | Linux x86_64 (`rebaseguard-vultr-02`) | macOS 26.5.2 arm64 |
> | Python | 3.12.3 | 3.14.5 |
> | numpy | 2.5.2 | 2.5.3 |
> | python-flint | 0.9.0 (Linux x86_64 build) | 0.9.0 (macOS arm64 build) |

The right column is recorded, in two artifacts (row 35). **The left column is recorded nowhere.** I checked
directly: `REGISTRY_C2.json`'s keys are `schema, rule, certified, operator_only, code_sha256, cells_json_sha256,
degree_taboo, degree_arl, taboo_alphas, arl_alphas, sub_block_max_width, cpu_seconds_total, blocks` — no host, no
platform, no toolchain; and no per-artifact file under `evidence/registry_c2/` carries a platform field either.
`grep -rn 'vultr\|x86_64\|3\.12\.3\|2\.5\.2'` over the namespace returns those four table cells and r2's note about
them, and nothing else.

On that unsourced half rests the document's bolded conclusion at `:56–58`:

> "**The Arb supersolution machinery reproduces exactly across the OS, architecture and FLINT build boundary**, and
> its published bounds survive a 50 % increase in working precision. That is the strongest statement available
> without a second implementation, **and it is the one the C1 reviewer asked for.**"

If the registry had in fact been built on this same macOS/arm64 host, every word of the safe-side and determinism
evidence would still hold, but "across the OS, architecture and FLINT build boundary" would be empty — and nothing
committed distinguishes those two worlds. `OPEN_NOTES_DISPOSITION_C2.md`'s N9 restates the claim a third time ("on
a genuinely independent host and toolchain build").

Two further things make this a FAIL rather than a NOTE:

- **`ERRATUM_C2.md:100–101` states that the provenance complaint is discharged:** "separately the C1 reviewer's
  complaint that `REGISTRY_C2.json` records no host or toolchain **is answered by the two artifacts that do**." The
  two artifacts record the *re-certifying* host. The complaint was that you cannot establish where the registry was
  built, and you still cannot. That sentence is not true.
- **r2 asked for the exact minimal repair and it was never made or dispositioned.** r2's Note 4 concluded: "a
  successor should record the build host in the registry, and in the meantime **the table's left column should be
  marked as reported rather than recorded**." Four rounds later the column is unmarked, the erratum's r2 section
  lists only that round's three FAILs, and no document in the namespace discloses that half of the comparison is
  unattested.

I want to be clear about how strong the underlying claim probably is. r2 found timing corroboration, and my own
runs add to it: `taboo_block_305_00` carries `cpu_seconds` ≈ 88 in the artifact and took 62.2 s here;
`taboo_block_306_00` re-certified in 55.5 s. The machines are almost certainly different. But "almost certainly,
by inference from a timing field" is not what the table's four precise version strings look like, and the campaign
is about to freeze a document that answers a predecessor reviewer's blocking condition with it.

**Minimal change required.** Mark the table's left column as reported-not-recorded, as r2 asked — one footnote is
enough, and the timing corroboration is worth including in it — and correct `ERRATUM_C2.md:100–101` to say what the
two artifacts do establish (the re-certifying host) and what they do not. Nothing else needs to change: the
determinism and safe-side results stand on their own, and I re-verified them independently.

## What I did not check

- **`c2_d5_forecast.py` end-to-end.** It needs the adopted K1 record store, which is not in this repository; my
  attempt refused cleanly with `AdapterRefusal: record 0 missing or not a regular file in the records directory`
  (a structured refusal, which is itself the right behaviour). I therefore did **not** confirm that
  `C2_D5_FORECAST.json` reproduces byte-for-byte. What I did instead: re-derived the classification, the gap falls
  and the material-tightening verdicts arithmetically from its committed outputs and the frozen gate, checked Γ
  signs from the exact rationals, and read `direct()`, `requirement()`, `combine()` and `classify()` against the
  gate clause by clause. I also did not exercise the TC-T enclosure, the K5-B literal, `tail_enclosure_crosscheck`,
  the replay gate or the regression check on m = 1, 2, 3; earlier rounds report these and I relied on that.
- **The full 105-artifact registry verification** (≈ 2.7 h). I spot-checked five artifacts at both precisions
  instead, deliberately spanning cells 305, 306 and 309 and both artifact kinds plus an `arl_cell`.
- **The 16 cell-306 artifacts I did not spot-check**, and the 384-bit behaviour of any artifact beyond those five.
- **Whether the registry was in fact built on `rebaseguard-vultr-02`.** I did not contact Vultr or AWS and did not
  try; see FAIL 2. This is the one factual claim in the namespace I could neither confirm nor refute.
- **Anything inside predecessor namespaces beyond what C2 pins**: I verified the C1 registry's block endpoints, the
  frozen cover cells, Campaign B's Lemma-G anchor as reproduced by C2's own producer, and the `taboo_certify.py`
  pin, but I did not re-audit Campaign B, Campaign C1, `deflated_consume.py` or the K5-B literal themselves.
- **The theorem content of TC-T, Lemma Dv′ and Lemma G.** I checked that `_atom_independent` and `atom_dv_prime`
  implement the same formula as `deflated_consume.atom_constants_r2` is asserted to, and that the crosscheck in the
  producer would raise on disagreement; I did not verify the lemmas are true.
- **The six prior review files' own internal arithmetic**, except where the erratum makes a specific claim about
  one (r1's `NOT_CHECKABLE_LOCALLY` rows, r2's non-reconciling header, r4's NOTE count) — those three I recounted.
- **Anything about AWS/SR/PS1.** Untouched, as instructed.

## Verdict counts

**NOT_READY** — 41 rows: **33 PASS, 6 NOTE, 2 FAIL.**

| verdict | count |
|---|---|
| PASS | 33 |
| NOTE | 6 |
| **FAIL** | **2** |
| **total** | **41** |

| FAIL | one line |
|---|---|
| **FAIL 1** (rows 23, 24) | `ERRATUM_C2.md` asserts twice that no sentence in the namespace states a count, while four prose counts survive in that file — two of them (`:16`, `:331`, "Across all five rounds") already stale after the sixth review, one (`:280`) contradicting `:266–267` in the same document — and the "two tables are the only places a count appears" claim is contradicted by the erratum's own round table and by `README.md:71` |
| **FAIL 2** (row 36) | `CELL_306_ADOPTION.md:33–38`'s build-host column (Linux x86_64 vultr-02, Python 3.12.3, numpy 2.5.2, Linux FLINT build) is recorded in no committed artifact, the bolded "reproduces across the OS, architecture and FLINT build boundary" conclusion rests entirely on it, `ERRATUM_C2.md:100–101` says the provenance complaint "is answered by the two artifacts that do", and r2's Note 4 asked specifically that the column be "marked as reported rather than recorded" — never done, never dispositioned |

## Answers to A–I

**A. Are the previously load-bearing failures actually repaired in the tree?** Yes — all four named ones, and every
other one I sampled. The critical-ratio column is relabelled "Lemma G (Campaign B) / C1 (true) / C2" in **both**
`R_STAGE_DESIGN.md` §2 and `D_STAGE_DECISION.md` §5, carrying 34.55795 / 20.93621 / 12.18694, which my re-run of
`c2_critical_ratio.py` reproduces to the digit, with the improvement restated as +8.00 / +11.10 / +16.17 % over C1
and the old "16–34 %" surviving only as a disclosed correction. The D1 blocker ranking is f_F > f_D > f_H on all
five cells in the prose, matching `radius_grouped` exactly, with `DOMINANT_BLOCKER_3 = order0_residual_fF` — and I
confirmed from `git show 5a94568a:` that the JSON always said so, as the erratum claims. The registry verifier's
nesting defect is fixed structurally: it indexes `rec[fld]` so a missing field raises, and a 105-artifact run is
committed with `pass: true`. The C_T admissibility guard is present and enforced, the inadmissible figures are
replaced by the clamped +1.3681 / +1.1502 / +0.9335 %, `gain_per_unit_of_input_moved` is confined to the C_T row
with a comparability string, and the withdrawn "refuses exactly as `deflated_consume.atom_constants`" claim is gone
from the source comment r4 caught. My own leaf-by-leaf diff across all four commits touching
`C2_D1_BLOCKER.json` confirms exactly nine values have ever been replaced, all C_T sensitivity on 307–309, with
487 → 525 leaves and nothing removed that existed at `ef58310c`. Three producers reproduce byte-for-byte; the
fourth differs only in the commit it records (Note 1). **The repairs are in the tree, not just described.**

**B. Did the structural de-counting repair eliminate the recurring defect?** **No — it changed the number in one
file and left the defect in the other, then claimed twice to have ended it.** `README.md` is genuinely clean: I
swept it and found no hand-maintained tally, and the diff shows deletion rather than update. `ERRATUM_C2.md` is
not. Four prose counts survive there: "Across all **five** rounds" at `:16` and again at `:331`, both stale after
the sixth review and the first one sitting two lines below the table that lists six rounds; "**three** separate
instances below are a number left stale by a later edit" at `:280`, which contradicts `:266–267`'s "Three … this
was the fourth" because the instance called "the fourth" is itself the table's last row; and the "Independently
recounted here: r1 60/10/3/6 … r4 28/4/3" tally at `:246–247`, which stops at r4 and gives r4 a NOTE count the same
file contradicts 40 lines earlier. Plus "four independent implementations" at `:335`. The completeness claims —
"no sentence in this namespace states one" (`:5`), "no other sentence in this namespace states a count" (`:279`,
whose own next clause states one), and "the two tables … are now the only places a count appears" (`:268–269`,
while the erratum's own round table at `:7–14` is a third and `README.md:71` names a different sole place) — are all
false as written. I swept code comments, docstrings and committed JSON strings as well: those are clean. Every
count in `code/*.py` is a specific reference ("pre-freeze review r4", "note 14"), not a tally, and the mutant
figures are current (43/35/8/40/3/0, which I reproduced). So the defect is confined to one file, but it is the
erratum, it is the twelfth instance of the named pattern, and it was introduced by the commit that announced the
pattern's structural end. **The number changed; the defect did not.**

**C. Does any remaining prose materially misstate?** Two things, both already stated as FAILs. On reliability:
the count claims in B. On evidence provenance: the unattested build-host column and the erratum's "is answered"
sentence in FAIL 2. Everything else I checked is accurate and often notably candid — the τ and C_T regressions are
reported rather than buried, the measure change is audited in both directions (including the finding that C2 would
have been USEFUL under C1's gate verbatim, which I re-derived at 15.708 %), the "It is adopted" declarative is gone
and replaced with an explicit statement that adoption requires a chain none of which has happened, the ×1.25
failure at cell 306 is put in a table against C2's own interest, and the governance state (guard DENY, zero new
real addresses, K5 PARTIAL, coverage map r4 authoritative, no r5) is stated correctly everywhere I looked. The one
non-blocking labelling gap is Note 5: `D1_BLOCKER_DIAGNOSIS.md` is computed entirely under C1's constants and never
says so.

**D. Does the D-stage result mechanically remain `D_PARTIAL`, closed = {305, 306}, open = {307, 308, 309}?**
**Yes.** Gap falls re-derived from the frozen baseline gaps: 0.462852 / 0.245931 / 0.183898, matching the published
figures exactly. Under `gap ≤ 0.80 × gap_baseline`, 307 and 308 are materially tightened and 309 is not
(0.899015 against the 0.881277 it would need). Γ is negative on 305 and 306 and positive on 307–309 from the exact
rationals. Applying the four frozen class definitions by hand: not `D_STRONG` (2 of 5), not `D_USEFUL` (309 fails
the every-open-cell requirement), so `D_PARTIAL`. `classify()` is a faithful transcription — the three guarded
branches are word-for-word the gate's classes, `mt` reads the 0.20 threshold from the gate rather than hard-coding
it, and closed cells are excluded from the `still_open` set the `all()` quantifies over. The one place it goes
beyond the gate is the uncovered case "no cell closed but some tightened", which it resolves to `D_INSUFFICIENT`
and discloses in its docstring instead of amending a frozen artifact — the right call (Note 2). The 1.6-percentage-point
miss at cell 309 is real and the threshold was frozen at `87309610`, sha verified identical at that commit and at
HEAD, before any C2 number existed.

**E. Are the 306 re-certification and the 105-artifact verification sound and correctly represented?** The
computational content is sound and I verified it independently rather than reading it. Using the FLINT venv I
re-certified five registry artifacts spanning cells 305, 306 and 309 and all three artifact kinds: at **256 bits**
every published field on all five came back **bit-identical**; at **384 bits** all five still certify and every
consumed bound holds safe-side (C_T, τ, D1, D2 ≤ published, D_lo ≥ published) while the three internal diagnostics
move — precisely the published behaviour, and on two cells the 306 artifact does not cover. The artifact's own
accounting reconciles: 18 artifacts, 45 consumed-constant assertions (5 fields × 9 sub-blocks), 27 diagnostic
fields that moved, worst relative deviation 5.3188e-30, `BOTH_PASSES_OK`. The 105 figure reconciles exactly against
the committed file set (50 + 50 + 5). **The cross-platform claim is where it fails.** Its re-certifying half is
recorded in two artifacts; its build half — Linux x86_64 `rebaseguard-vultr-02`, Python 3.12.3, numpy 2.5.2, Linux
FLINT build — appears in exactly one place, that table, and in no committed artifact at all, in a document that two
paragraphs earlier says `REGISTRY_C2.json` records no host or toolchain. The bolded "reproduces exactly across the
OS, architecture and FLINT build boundary" therefore rests on an assertion, the erratum says the provenance
complaint "is answered by the two artifacts that do", and r2's specific request to mark the column as reported
rather than recorded was never carried out. That is overclaiming, and it is FAIL 2. The campaign does *not*
overclaim a second implementation — "still one implementation, run twice", carried as N9 — and that part is
exactly right.

**F. Is the 384-bit test treatment legitimate?** **Yes, and I verified the non-weakening from git history rather
than accepting it.** Across `12585997 → 8aee1fc5 → 55c4cf00`, the consumed-constant branches change only their set
membership (`UPPER`/`LOWER` → `CONSUMED_UPPER`/`CONSUMED_LOWER`) and their test strings; the inequalities `g_ <= p_`
and `g_ >= p_` are character-identical, and C_T, τ, D1, D2 and D_lo are in both the old and the new sets, so they
hit the same test before and after. The strict determinism branch, `elif strict: good, test = p_ == g_, "equal"`,
lies outside every hunk of both diffs and is byte-identical in all three versions — it still demands bit-identity
on **every** field, diagnostics included, and my own 256-bit runs confirm that demand is met. Nothing was
weakened. On whether the separation is sound: it is, and for a stronger reason than the module's first attempt gave.
`certify_block` sets `ok = (margin > 0 and wmin >= 0)` and `certified is True` is asserted unconditionally in both
passes, so the load-bearing content of all three diagnostics is re-established from scratch at 384 bits; and
because the safe-side pass recomputes the certification inequality rather than trusting the published diagnostic, a
5e-30 wrong-side drift in `allowance_upper` cannot smuggle anything through. The disclosure is honest about the
order of events, and the earlier "not a bound anyone relies on" wording — which was simply wrong, since
`allowance_upper` *is* an input to the inequality — has been withdrawn in the module itself. **Not a moved
goalpost.** The single claim I could not verify is "passed 45/45 as originally written", because the failing run
was never committed; I verified its structural equivalent instead.

**G. Is referring the cell-306 margin floor to the adjudicator compliant, or an evasion?** **Compliant.** The
frozen rule requires that "a non-empty closed subset is **always** adopted when the adjudication chain completes"
and does not name which subset; both pre-committed branches adopt cell 305, so the rule holds either way. The
campaign is declining to supply a number the gate never required and that it is structurally disqualified from
setting, having seen 11.2 % before any floor existed — and the document says exactly that, including the sharp
observation that "writing one would be worse than having none, because it would look like a pre-registration".
The pre-commitment is symmetric, committed before any adjudication exists, and resolves the awkward case ("declines
to set one") *against* C2 by adopting 305 alone. The adverse facts are put in front of the adjudicator rather than
buried: margin 1.112× against 305's 1.353×, and Γ under ×1.25 degradation +0.029163 — **cell 306 does not survive
the degradation while cell 305 does** at −0.033733, which I confirmed from the robustness artifact. An evasion
would look like a floor quietly chosen at 10 %, or like adopting {305, 306} while calling the floor question open.
Neither is what this is. My only reservation is the "independent derivations closing it — 4 / 3" row, which mixes
reviewer implementations with campaign derivations and is the kind of hand-maintained figure FAIL 1 is about.

**H. Is the deterministic mixed/operator-level alternative sound enough to block "deterministic routes are
exhausted"?** **Yes, and I verified both the numbers and the premise from scratch.** The premise is the load-bearing
part, and it holds: each tail cell's interval satisfies `[e₀−ρ, e₀+ρ] = [left, right]` in the frozen cover, **C1's
single block is exactly that interval on all five cells**, and C2's 9/9/10/11/11 sub-blocks tile it exactly with
every width ≤ 1/100 — so both registries' constants are genuinely whole-cell bounds and the componentwise best (min
on the five upper bounds, max on D_lo) is a valid whole-cell supply satisfying all six Lemma Dv′ hypotheses. I
recomputed Lemma Dv′ on the mixed tuple myself and reproduced the published `operator_mixed` A-vector on all five
cells, and the gap falls come out **57.27 / 30.57 / 23.03 %**, exactly as reported, all three clearing the gate's
own frozen 20 % bar — including the 309 that cost C2 `D_USEFUL` by 1.6 points. The mixed critical ratios 38.07 /
23.90 / 14.72 check out too. **C2 does not consume this route**, which I confirmed: `operator_mixed` appears only in
`C2_CRITICAL_RATIOS.json` and its producer, the D5 forecast's supplies are exactly `{G, C1, C2}` with provenance C2
on all fifteen fields, and the gate's D4 rule ranges over whole supplies rather than the six operator constants —
so taking the mixed route now, after seeing 309 land at 18.39 %, would be the post-hoc rule change the gate exists
to forbid. The campaign says so plainly and makes the point block the R stage (`R_STAGE_DESIGN.md`'s opening
precondition, `D_PRIME_OPPORTUNITY.md` §4, N7). **The "deterministic exhaustion" premise is unestablished, and a
real order-3 address must not be spent on it.** This is the most valuable thing in the namespace and the campaign
handles it correctly: it neither takes the forbidden step nor pretends the step does not exist.

**I. Is the namespace coherent enough for a cold adjudicator?** Mostly yes, with the count defect as the
exception. Read as a set, `README.md` → `ERRATUM_C2.md` → `phase_d/` → `phase_r/` → `OPEN_NOTES_DISPOSITION_C2.md`
tells one consistent story: what was frozen and when, what the result is, what every review found, what changed as
a result, what is referred out, and what blocks the next step. The cross-references resolve, the numbers agree
across documents wherever I checked them, N6–N9 map cleanly onto the four open governance questions, and the
R-stage document opens by arguing against its own recommendation — which is the right shape for this evidence. The
navigation is good: an adjudicator who reads only the README's result table, `D_STAGE_DECISION.md` §4 and
`CELL_306_ADOPTION.md` has what they need to decide, and the erratum tells them what not to trust. What a cold
reader would stumble on: the erratum's count claims, which contradict themselves within a few lines and undermine
confidence in exactly the document meant to restore it (FAIL 1); the unattested build-host table in the one
document that decides an adoption (FAIL 2); and `D1_BLOCKER_DIAGNOSIS.md`'s unlabelled supply, whose magnitudes
differ from C2's published ones with no explanation (Note 5). None of the three requires a new computation. Fix the
two FAILs by deletion and one footnote respectively — the campaign's own lesson, "when a review asks for one
change, make that change and stop" — and I would expect this to freeze.
