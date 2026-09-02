# P5X defect register

Additive. **No frozen document is edited.** Each entry states the frozen text,
what is wrong or incomplete, the evidence, the correction, the blast radius, and
what may proceed before adjudication. Entries created during Phase 1
(human proofs), before any certified computation.

---

## `D1` — the frozen SR pre-alarm state square is too small

| field | content |
|---|---|
| frozen text | `FROZEN_THEOREM.md` §2: "the pre-alarm detector state, living in the compact square `E_D = [0, b_D)^2` with … `b_SR = log A`" |
| status | **FALSE for SR.** CUSUM (`b = h = 5`) is correct |
| why | the SR alarm test is on the *pre-update* quantity `v = y + z - 1/2`, while the *stored* state is `y' = log(1 + exp(v))`. A live step has `v < log A`, hence `y' < log(1 + A)`, and `y' >= log A` whenever `v >= log(A-1)` — an event of positive probability |
| evidence | `feasibility/results/sr_domain_check.json` (fresh seed `20260902`, 400 000 paths): maximum live stored state `6.25744933`, against `log A = 6.25553146` and `log(1+A) = 6.25744943`; `1535` live states at or above `log A` |
| correction | `b_SR := log(1 + A)`. Nothing else changes: `l(x) = x^- - c_SR`, `u(x) = c_SR - x^+`, `q_SR` and `c_SR = log A + 1/2` are all stated for a general `x` and never used `x < log A`; `L1` is proved on the corrected square |
| blast radius | **SR only.** Every CUSUM statement, and the entire single-cell stop-gate (which is CUSUM), is unaffected. Had this reached an SR certificate unnoticed, a positive-probability part of the state space would have been outside the certified cover — a silent error, not a conservative one |
| gate impact | `G5` is per-detector, so an SR-only correction cannot change a CUSUM verdict |
| may proceed before adjudication | all CUSUM work, including the stop-gate |
| must NOT proceed before adjudication | any SR certified solve or SR cover |

## `D2` — the frozen operator enumeration for second moments is incomplete

| field | content |
|---|---|
| frozen text | `FROZEN_THEOREM.md` §3: the pair functions are "built from `h` and `K_{z,e}` by the same first-step conditioning" |
| status | **INCOMPLETE, conclusion unaffected** |
| why | the diagonal terms `E[Z_{tau-r}^2 ; tau >= m]` require the `z^2`-weighted operator `K_{z2,e} f (x) = int_l^u z^2 f(q(x,z)) phi(z+e) dz`, which is not a composition of `K_e` and `K_{z,e}`. `PROOF.md` `L2.5` derives them |
| correction | add `K_{z2,e}` to the operator list. Its absorbing reward `rho_{2,e}` is already frozen in `P5X-T1` |
| blast radius | the frozen *conclusion* ("determined by the same square through `O(m^2)` backward functions") is proved as stated; only the enumeration of operators was short by one. No certified quantity changes |
| gate impact | none |
| may proceed | everything; `PROOF.md` `L2` is the discharge |

## `D3` — `L4`'s monotonicity clause is not proved, and is not needed

| field | content |
|---|---|
| frozen text | `PROOF_OBLIGATIONS.md` `L4`: "the monotone Bellman minorant … extends to interval-valued `e`, with the worst case at the endpoint of the interval nearest `0`" |
| status | **NOT PROVED here.** `L4` was not in the Phase-1 mandate and is not discharged |
| why it is delicate | the clause is essentially "`sup_x E_{x,e}[tau]` is decreasing in `|e|`". Pathwise coupling gives monotonicity of each *arm* separately (`tau^-` decreases and `tau^+` increases in `e`), not of `tau = min(tau^+, tau^-)`. The closely related statement `sup_e E[tau|e] = E[tau|0]` is recorded as **open** in `p5_nonlinear_dynamics/LIMITATIONS.md` §3 |
| how the campaign avoids it | the resolvent constant is obtained **per `e`-cell** by a drift-explicit block-forcing bound proved from scratch (`STOP_GATE.md` §3), which needs no monotonicity in `e` and no imported constant. A one-sided monotone minorant, if wanted later, can also be re-run at the cell's drift rather than transported from `e = 0` |
| blast radius | none, given the replacement. The frozen `L4` remains an open obligation and must not be cited as discharged |
| gate impact | none; no gate references `L4` |

## `D4` — `L5`'s "hence" clause overstates the reason (non-defect clarification)

| field | content |
|---|---|
| frozen text | `PROOF_OBLIGATIONS.md` `L5`: "real-analytic; **hence** interval-valued `e` is admissible and no separate modulus of continuity is required" |
| status | **TRUE but over-attributed** |
| why | admissibility of an interval-valued `e` follows from the weaker, purely order-theoretic fact that `phi(z+e)` has an outward-rounded enclosure for `e` in an interval. Analyticity is what licenses a low-degree polynomial candidate per cell; it is not what makes the enclosure valid |
| correction | none needed; recorded so that no reader concludes the certificate rests on analyticity |
| blast radius | none |

---

## Adjudication request

`D1` is the only entry that blocks work, and it blocks only SR. The
recommended disposition is a **pre-result erratum to `FROZEN_THEOREM.md` §2**
replacing `b_SR = log A` with `b_SR = log(1 + A)`, adjudicated by a reader other
than the campaign, recorded as an erratum rather than an edit, and applied
before any SR certified solve. Because it is discovered and recorded **before**
any P5X result exists, it is a pre-registration correction, not a post-hoc
change; `FROZEN_GATES.md` `G1` still holds because the frozen bytes are
unchanged.

## `D5` — a Checkpoint-A test asserts a transient worktree property

| field | content |
|---|---|
| frozen text | `tests/test_anchor_and_protection.py::test_no_production_results_at_checkpoint_a`, listed in `SOURCE_MANIFEST.json` |
| status | **STALE at Checkpoint B**, by construction |
| why | it asserts that `results/` holds nothing but the pre-campaign manifest. That is gate `G1`'s property, but `G1` is a statement about the **anchor commit**, whereas the test inspects the **working tree** — so it necessarily goes red as soon as Checkpoint B writes its first artifact |
| correction | the test file's bytes are frozen and are **not** edited. `tests/conftest.py` (which is not in `SOURCE_MANIFEST.json`) marks it `xfail(strict=True)` with this defect id as the reason, and `tests/test_checkpoint_b.py::test_gate_g1_anchor_holds` checks the intended property correctly, against `git ls-tree` on the anchor |
| blast radius | none. `G1` is checked, and more faithfully than before |
| lesson for the next anchor | freeze tests of *invariants*, not of *phases*; a phase assertion belongs in a gate script that names the commit it is about |

## `D6` — a Checkpoint-B test asserts a transient worktree property

| field | content |
|---|---|
| subject | `tests/test_ra_frozen.py::test_no_ra_production_result_at_the_anchor` |
| status | **STALE at the R-A result checkpoint**, by construction — the same defect class as `D5` |
| why | it asserts that no R-A result file exists in the working tree. That is a property of the **anchor commit** `e02b5ce`, not of the working tree, so it necessarily goes red as soon as the R-A′ gate writes its artifact |
| correction | the test is not edited. `tests/conftest.py` marks it `xfail(strict=True)` naming this defect, and `tests/test_checkpoint_c.py::test_no_ra_result_existed_in_the_anchor_commit` checks the intended property with `git ls-tree` on `e02b5ce` |
| blast radius | none; the property is checked, and more faithfully |
| lesson | repeated from `D5` and now demonstrated twice: freeze tests of *invariants*, never of *phases*. A phase assertion belongs in a gate script that names the commit it is about |

## `D7` — external repository change invalidates the protected-tree manifest comparison

| field | content |
|---|---|
| subject | `test_protected_tree_intact` in `test_anchor_and_protection.py` and `test_checkpoint_b.py` |
| status | **FAILING at `HEAD`, for a cause outside P5X** |
| why | commit `31132e8` ("Independently close P9R repair adjudication") and an external working-tree clean landed between Checkpoint B and the R-A′ result. See `INCIDENT_EXTERNAL_TREE_CHANGE.md` |
| correction | the manifest is **not** re-baselined — that would destroy the gate. Both tests are marked `xfail(strict=True)` naming the incident, and `tests/test_checkpoint_c.py` checks against git the properties that actually matter (`P5` byte-identical to `bb03c0e`; the P5X tree at `HEAD` identical to the anchor; no P5X commit touching anything outside P5X) **and pins the external diff to exactly three files**, so any further outside change fails loudly |
| blast radius | the P4/P5 disposition-audit namespaces are lost as working-tree artifacts; their recorded digests survive. No P5X proof path depends on them (`DEPENDENCY_AUDIT.md` §2) |
| responsibility | not P5X's. Escalated to the repository owner in `INCIDENT_EXTERNAL_TREE_CHANGE.md` §5 |

## `D8` — a Checkpoint-C test asserts a transient worktree property (third occurrence)

| field | content |
|---|---|
| subject | `tests/test_r1_frozen.py::test_no_r1_result_at_the_anchor` |
| status | **STALE at the R1 result checkpoint**, by construction — identical in kind to `D5` and `D6` |
| why | it asserts that no R1 result file exists in the working tree; that is a property of the **anchor commit** `a5fdb17`, not of the working tree |
| correction | the test is not edited. `tests/conftest.py` marks it `xfail(strict=True)` naming this defect, and `tests/test_checkpoint_d.py::test_no_r1_result_in_the_checkpoint_c_anchor` checks the intended property with `git ls-tree` on `a5fdb17` |
| blast radius | none |
| **standing lesson, now demonstrated three times** | anchor-phase assertions must be written against `git ls-tree <anchor>` from the outset. Every future P5X checkpoint test that wants to say "no result existed at the anchor" must name the commit, never inspect the working tree. This is recorded as a process rule, not merely a defect |

## `D9` — anchor-phase worktree assertion (fourth occurrence, D8 pattern)

| field | content |
|---|---|
| subject | `tests/test_r2_frozen.py::test_no_r2_result_at_the_anchor` |
| status | **STALE at the R2 result checkpoint**, by construction |
| correction | not edited; `tests/conftest.py` marks it `xfail(strict=True)` citing the `D8` pattern, and `tests/test_checkpoint_e.py::test_no_r2_result_in_the_checkpoint_d_anchor` checks the property against `git ls-tree` on `afbfe18` |
| note | the `D8` standing rule was written after the third occurrence and was **not** followed when `test_r2_frozen.py` was authored. Recorded as a process failure, not just a defect: the rule needs to be enforced at authoring time, e.g. by a lint that rejects `results/*.exists()` assertions in anchor-phase tests |

## `D10` — the R4 two-chart exponential shorthand is wrong (NOT a `D8`/`D9` repeat)

| field | content |
|---|---|
| subject | `compute_optimization_r4_xi_reformulation/XI_DERIVATION_AND_INVARIANCE.md` §7 and §14, as committed at Checkpoint F `209a6fd9a5ca2824688062ac855a7abcefae9697` |
| class | **algebra defect in a frozen derivation.** Explicitly *not* the anchor-phase transient-worktree pattern of `D5`/`D6`/`D8`/`D9`; the `D8` standing rule was followed in R4 |
| statement | §7 writes the minus-chart factor as `E^{-b}` and §14 as `(1/A+zeta^-)/E`, with `E = e^{z-1/2}`. That is false. The frozen minus-chart update is `v^- = y^- - z - 1/2`, so the correct factor is `E^- = e^{-z-1/2}`, and `E^- = e^{-1}/E^+`, **not** `1/E^+`. The two charts are *not* reciprocal; they satisfy `E^+ E^- = e^{-1}` |
| consequence | as written, §7/§14 overstate every minus-chart contribution by `e^{j}`. Measured error before correction: relative `5.3e-3` to `2.9e-1` against an independent brute-force simulation of the frozen `y`-space recurrence |
| what is **not** affected | §1 (`xi^- ' = 1 + xi^- exp(-z-1/2)`) is correct as written. The live-region limits `l`, `u` are correct (re-derived and re-checked). The closed-form integral identity of §7 is correct. `L-R4.1`..`L-R4.10` are unaffected: they are pathwise statements about `exp`/`log`, not about the shorthand |
| correction | `(E^+)^i (E^-)^j = e^{(i-j)z} e^{-(i+j)/2}`. The `z`-exponent is still `k = i-j`, so the closed-form structure, the `2(2n+1)` `Phi` count and the zero-panel property all survive **unchanged**; only the constant prefactor moves inside the `G_k` accumulation: `G_k = sum_{i-j=k} c_ij (1/A+zeta^+)^i (1/A+zeta^-)^j e^{-(i+j)/2}`, and `(K_e f) = sum_k G_k e^{k^2/2-ke}[Phi(u+e-k)-Phi(l+e-k)]` |
| frozen bytes | **not edited.** `XI_DERIVATION_AND_INVARIANCE.md` keeps its Checkpoint-F content; this erratum and `errata/D10_XI_CHART_ASYMMETRY_ERRATUM.md` carry the correction, exactly as `D1` was handled |
| how found | a pre-gate independent equivalence check against a brute-force simulation of the frozen recurrence, run **before** the gate — the same discipline that caught the R2 `C2` substitution-order bug. It was not found by reading the algebra |
| gate impact | none on any criterion, threshold, class or the recorded prediction. The bug was in the implementation and the shorthand, and was fixed before the gate ran |

## `D11` — the frozen `P2` criterion is ill-typed and unsatisfiable

| field | content |
|---|---|
| subject | `compute_optimization_r4_xi_reformulation/R4_FROZEN_SPEC.md` §3, criterion `P2`, frozen at Checkpoint F |
| statement | `P2` requires the closed-form **ball to CONTAIN** a composite-Simpson reference. The closed form's radius at 192 bits is `~1e-50` relative; composite Simpson at `40000` points has a truncation error of `~1e-15` relative that its ball arithmetic does **not** account for. So the reference's midpoint sits outside the closed-form ball whenever the closed form is *correct*, and the criterion cannot be met by any correct implementation |
| consequence | `P2` as literally frozen is a **FAIL for a correct method**. It does not discriminate correct from incorrect implementations, which is what a correctness criterion is for |
| correction | frozen bytes **not edited**. The gate reports `P2` twice: `pass` is the literal frozen verdict, and `pass_corrected` uses the test that was intended — overlap against a reference **widened by a Richardson estimate of its own truncation error**, together with the frozen `<= 1e-12` relative-half-width requirement. The gate reports `gate` (frozen conjunction, binding) and `gate_corrected` separately, both labelled |
| honesty note | the correction is **post-hoc**: it was written after observing that the literal criterion could not pass. It is disclosed as post-hoc wherever it is reported, and the frozen verdict is the one carried in the headline. `P4`, the decisive criterion, is untouched by this and was not re-budgeted |
| lesson | a criterion comparing a rigorous enclosure against a non-rigorous numerical reference must be stated as *overlap with a widened reference*, never as *containment*. Direction matters, and "high-order quadrature" is not an enclosure |

## `D12` — the frozen R5 `erfcx` branch is numerically inferior in Arb

| field | content |
|---|---|
| subject | `compute_optimization_r5_scaled_tail/R5_FROZEN_SPEC.md` §2, the `erfcx` branch rule, frozen at Checkpoint G `f19f8d13caae1d9d8d21a6237fe1b71ee06b8e63` |
| class | **frozen implementation-choice defect.** The *mathematics* is correct — `erfcx(t) = U(1/2,1/2,t^2)/sqrt(pi)` was verified to overlap `exp(t^2)erfc(t)` at eight arguments — but the *evaluator* chosen is the wrong one |
| statement | the rule freezes `t > 2 -> hypgeom_u(1/2,1/2,t^2)/sqrt(pi)`. That choice was made on evidence gathered at **point** arguments, where Arb's `U` gives relative radius `~5e-60`. On **ball** arguments Arb's `U` loses up to 26 decimal digits: at `t = 7.5708` (a ball of relative radius `5.3e-58`) it returns relative radius `1.772e-29`, while the true sensitivity is `7.3e-58` |
| consequence | `Q3` amplification `2.238e20` — **worse than R4's `2.136e17` by a factor of 1048**; and `Q7` runtime `2.2617 ms` against the `2.0 ms` budget, `COST_FAIL`. The frozen gate fails on both, plus `Q2` (the R5 interval is wider than R4's, so `R5 subset R4` cannot hold) |
| what is **not** affected | `Q1` passes: the scaled interval overlaps R4's at **every** `k` in `-16..16`. The algebra of `SCALED_TAIL_DERIVATION.md` §3-§5 is correct; `L-R5.1`..`L-R5.9` stand. The defect is confined to which routine evaluates `erfcx` |
| correction | frozen bytes **not edited**. Two post-hoc variants are reported, labelled: `expbranch` (`erfcx = exp(t^2)erfc(t)` throughout) and `minimal` (regime-split `erfc` difference, no exponent folding). Both give amplification `1.0027e2` |
| how found | the pre-gate smoke test showed the scaled path was *worse* than R4 (`1.77e-29` vs `1.68e-32`), which was traced to `hypgeom_u` on ball input. Found before the gate ran, but after the spec was frozen |
| residual classification | `ARB_SPECIAL_FUNCTION_LIMITATION` |

## `D13` — `Q4` encoded a mechanism that R5's own diagnostic had already refuted

| field | content |
|---|---|
| subject | `R5_FROZEN_SPEC.md` §4, criterion `Q4` (`huge_tiny_intermediate = NO`), frozen at Checkpoint G |
| statement | `Q4` forbids constructing any product of a `|log10| > 20` factor with a `|log10| < -20` factor. It encodes the R4 brief's hypothesis that the `2^58` came from forming `exp(k^2/2-ke) x [Phi(b)-Phi(a)]` as `~1e55 x ~1e-55`. **§1 of `SCALED_TAIL_DERIVATION.md` — written by me, in the same commit — measured that this is not the mechanism**: there is no cross-`k` cancellation (`max|G_k I_k|/|sum| = 0.9933`), and the entire radius is produced by the `1 + erf` branch inside a single `I_k` |
| consequence | `Q4` is the only criterion that forced the exponent-folding architecture and hence the `erfcx`/`hypgeom_u` choice of `D12`. `Q4` **passed** (`0` huge-tiny products) while `Q3`, the criterion that actually matters, failed. The two post-hoc variants violate `Q4` (26 and 4 products respectively) and achieve amplification `1.0027e2` — a factor `2.1e15` better than R4 |
| finding | a `huge x tiny` product is **harmless when both factors carry full relative accuracy**, because relative error is preserved under multiplication. `Q4` is a hygiene proxy, not a conditioning criterion, and it was allowed to override the measured diagnosis |
| correction | frozen bytes **not edited**; `Q4` remains part of the binding conjunction and is reported as passing. The variants that violate it are reported as **post-hoc**, and the gate verdict stays `FAIL` |
| lesson | this is the third mis-specified criterion in the campaign (`D11`, then `Q4`). Twice now a criterion was frozen from an inherited hypothesis rather than from the measurement already in hand. A frozen criterion must be checked against the campaign's own diagnostics **before** the anchor commit, not after |
