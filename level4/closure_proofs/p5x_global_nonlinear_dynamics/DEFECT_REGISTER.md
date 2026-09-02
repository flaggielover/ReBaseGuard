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
