# Campaign C2 — independent fresh-context adjudication

**VERDICT: PARTIALLY_ADOPTED**

**ADOPTED CELL SET: [305]**  — pair (m = 5, cell 305), and nothing else.

Cell 306 is **NOT adopted**. Cells 307, 308, 309 remain open (C2 does not close them and does not claim to).

The sealed result itself — `D_STAGE_CLASS = D_PARTIAL`, closed {305, 306}, still open {307, 308, 309} — is
**correct**. I reproduced every decision-relevant number of it bit-exactly from the theorem documents, with an
implementation that imports no module this campaign or its predecessors wrote. The reason cell 306 is not adopted
is not that its arithmetic is wrong; it is the margin-floor decision referred to me under K, and it is stated in
full in section K.

---

## Adjudicator context

I am an independent fresh-context adjudicator. I wrote no part of Campaign C2, took part in none of its sixteen
pre-freeze reviews, and am not bound by its conclusions. I reviewed `p5y-k5-tail-c2` at `2d626506` in the worktree
`/Users/suzhe/ReBaseGuard-k5c2`.

I modified no file in this repository except this one, ran no writing git command, did not touch AWS
(`mcp__rebaseguard-aws__*` was not called), did not contact `rebaseguard-vultr`, generated no coverage map r5, and
created no file inside the repository other than this document and its containing directory. All scratch work is
outside the repository. `git status` was clean before I started and is clean apart from this file now.

---

## What I re-derived independently, and what I accepted

### Re-derived from the theorem text, sharing no code with the campaign

I wrote a standalone implementation from `THEOREM_AD.md` §4 (Lemma Dv′ r2), `THEOREM_TCT.md` §§1–4 (Lemma G, the
(P2′) zero order-3 candidate, the (P3′) midpoint/cell towers, the (P3) envelope, the Taylor sums, the assembly
table) and the direct clause of `k5b_check.k5b_literal` (read, not imported). It loads only committed JSON —
`cells.json` (filtered on `detector == "CUSUM"`), `TCT_INPUTS_{305..309}.json`, `ADOPTED_TAIL_INPUTS.json`,
`REGISTRY_C1.json`, `REGISTRY_C2.json` — and imports no campaign module, not `tc_rule`, not `tct_rule`, not
`deflated_consume`, not `tail_forecast_r2`, not `c2_d5_forecast`.

It reproduces, **as exact rationals, string-for-string against the committed `Gamma_exact`, `A_exact`, `H_exact`
and `M_after_exact`**:

| cell | Γ | magnitude = M_after | required uniform A-reduction | gap above 1 | baseline gap | gap fall | pass |
|---|---|---|---|---|---|---|---|
| 305 | **−0.08802906884054082** | 3.615109875695682 | 1.0 | 0.0 | 0.0 | — | **yes** |
| 306 | **−0.030469257709306738** | 3.5119460127500672 | 1.0 | 0.0 | 0.0 | — | **yes** |
| 307 | +0.033132953404317905 | 3.451359412896 | 1.1407635748126312 | 0.1407635748126312 | 0.2620572570527464 | **0.46285183476411584** | no |
| 308 | +0.10270008356594545 | 3.4524564789357517 | 1.5002877825423833 | 0.5002877825423833 | 0.663450928753142 | **0.24593099374719365** | no |
| 309 | +0.16224941061997425 | 3.400934402274074 | 1.8990148694205993 | 0.8990148694205993 | 1.1015967636536343 | **0.18389841084966285** | no |

Applying the frozen gate's classes myself: closed = {305, 306} (≥ 1, < 5); 309's gap fall 0.18389841 < 0.20 so not
every still-open cell is materially tightened, so `D_USEFUL` fails; therefore **`D_PARTIAL`**. Identical to the
seal.

Also re-derived independently:

- **atom constants**, all three supplies, all five cells, exact (Lemma G `A0 = C, A1 = k₁C², A2 = k₂C² + 2k₁²C³`;
  Lemma Dv′ `A0 = Ā_eff, A1 = Ā_eff(κ₁C + δ₁), A2 = Ā_eff(2κ₁²C² + κ₂C + 2κ₁Cδ₁ + 2δ₁² + δ₂)`,
  `Ā_eff = min(Ā, τ/D_lo)`), and the componentwise-minimum selection and its per-field provenance (C2 on every
  field of every cell);
- **the derived identity gate** — rebuilding each cell's `R2_interval` for m = 1, 2, 3, 5 from the replayed
  `H_at_a`, `W2` and the extract's own `eps_cell_refined`: contained on **20/20** (cell, m) pairs, worst relative
  endpoint gap **3.6279 × 10⁻⁸** (the theorem claims 2.7–3.6 × 10⁻⁸);
- **the ×1.25 degradation**: Γ_deg(305) = −0.033733237 (closes), Γ_deg(306) = +0.029163293 (does not close), and
  the remaining three;
- **the margins** `M_needed / M_after`: 1.353093 / 1.111935 / 0.891286 / 0.704541 / 0.579202;
- **the D′ mixed-operator opportunity** (section J/N7): requirements 1.11196624 / 1.46065480 / 1.84787350 and gap
  falls 57.27 % / 30.57 % / 23.03 % — exactly as `D_PRIME_OPPORTUNITY.md` reports;
- **the sub-block tiling**, exactly, as rationals, for all five cells;
- **five Arb/FLINT certification artifacts**, re-certified with an independent python-flint venv on this host.

### Accepted without independent re-derivation

- The contents of the adopted K1 record store (`/root/work/.../k4_records`) — not present on this host. I used the
  committed `ADOPTED_TAIL_INPUTS.json` extract, which Campaign B's producer checks field-by-field against the
  records at run time. See "What I did not check".
- The replay gate (that the adopted post-Campaign-A state reproduces the sealed Campaign-A consumption pass
  ranges) and the full 310-cell `k5b_literal` composition, both of which need the record store.
- The frozen producer's 262-field identity gate on the replayed measurements.
- 100 of the 105 registry artifacts (I re-certified five).

---

## A. Temporal integrity / gate pre-registration — **PASS**

The gate `config/FEASIBILITY_GATES_C2.json` (sha `098dd7f5…`) has **exactly one commit in its entire history
across all refs**: `87309610`, 2026-09-20 19:24:21 +0900. Its content at that commit hashes to `098dd7f5…`; so does
its content at HEAD. It has never been amended.

`87309610` is the **first** commit of the C2 namespace — the child of the start frontier `5289b6ce`. Nothing in the
namespace can predate it because nothing in the namespace exists before it. The only other file in that commit that
carries numbers is `evidence/phase_b0/C2_B0_VERIFICATION.json`, and every constant in it is a **C1** constant
(`B6_c1_constants`, τ/C_T/D_lo/D1/D2/Ā transcribed from the already-published C1 registry) — no C2 operator
constant, no TC-T magnitude, no K5-B outcome, no class. The first file reporting a C2 constant is
`REGISTRY_C2.json`, added at `e71378a0`; the first reporting a magnitude/Γ/class is `C2_D5_FORECAST.json`, added at
`51f8844b`. Both are strictly after the gate.

The gate's `baseline` is not self-generated: it is transcribed from
`p5y_k5_tail_operator_registry/evidence/forecast_r1/C1_FORECAST.json`, `material_improvement.per_cell_uniform_reduction_still_needed`.
I read that file at the frontier commit and the five values match the gate's `requirement` block exactly
(1.0 / 1.0 / 1.2620572570527464 / 1.663450928753142 / 2.1015967636536343), so the baseline C2 measures itself
against is a predecessor's published number, not one C2 chose.

The gate's `README.md` was in the same commit and has been edited since; the campaign says so explicitly and tells
the reader to use `git show 87309610:…/README.md` rather than trust the description. I did; the pre-registered
version has no result rows.

## B. Freeze and protocol integrity — **PASS**

- Protocol at the freeze commit `637b59bc` hashes to `c1243194…` = `protocol_sha256_unbound_at_freeze`. Protocol at
  HEAD hashes to `523d2eb3…` = `protocol_sha256_bound`. Both as recorded.
- `git diff 637b59bc HEAD -- config/C2_PROTOCOL.json` is **exactly six lines**: `freeze.commit` null → the freeze
  sha, `freeze.note`, `freeze.state` UNBOUND → BOUND. Nothing else changed. The binding changed only the freeze
  block, verified directly rather than through the campaign's own checker.
- `git diff 637b59bc HEAD` over the whole namespace is: one `M` (the protocol, above) and eleven `A` rows, all of
  which are governance artifacts produced *after* the freeze (freeze record, qualification, authorization,
  execution, seal + manifest, consumption) plus the three non-frozen lifecycle scripts (`c2_qualify.py`,
  `c2_execute.py`, `c2_consume.py`). **No frozen producer, no config file, no evidence artifact under
  `evidence/registry_c2/`, `evidence/phase_d1/`, `evidence/phase_d5/` or `evidence/prefreeze/` changed after the
  freeze.** That is the property that matters and it holds absolutely.
- The protocol pins 152 files. Its `expected_verdicts` and `result` blocks are consistent with the evidence I
  re-derived.

**The superseded freeze attempt `1efb76ee`: leaving it in history and superseding it was correct.** `git diff
1efb76ee 637b59bc` is a single hunk of **+20 lines in `code/c2_protocol.py`** — the binding-integrity check that
re-reads the protocol as committed at the freeze commit and refuses if the bound copy differs anywhere outside the
freeze block. The first attempt pinned a `c2_protocol.py` that lacked it; adding it changed the producer the
protocol pinned, so the attempt's own checker refused. The two available repairs were (i) amend `1efb76ee`, which
destroys the record that a freeze was attempted and failed, or (ii) supersede it with a second freeze commit and
disclose it in the freeze record and in the pre-freeze refusal artifact. C2 did (ii). That is the right choice, and
it *strengthens* the packet: the added check is precisely what makes the later "binding changed only the freeze
block" claim mechanically enforceable rather than asserted. I verified the 20 added lines do what they claim.

## C. Qualification validity — **PASS, with two findings**

Seventeen checks, zero FAIL, zero load-bearing SKIPPED, verdict QUALIFIED. The qualifier is deliberately outside the
frozen set, committed after the freeze, and its own sha256 (`59a3c889…`) is recorded in the artifact and matches the
file on disk. The checks are real, not decorative — I read every one:

- the load-bearing set is explicit (`LOAD_BEARING`) and omitting the two toolchain-dependent rows yields
  INCOMPLETE, not a pass, so the 2.7 h registry re-certification and the 40 min cell-306 re-certification could not
  be skipped to obtain QUALIFIED;
- the refusal rows genuinely execute the refusals (unbound protocol; a protocol with one evidence pin overwritten
  by 64 zeros) and require non-zero exit plus the expected message;
- `producer_determinism` re-runs the three record-free producers inside the frozen tree and compares bytes. **I
  re-ran all three myself on a different host and all three are byte-identical to the committed artifacts**
  (`C2_MUTATIONS.json`, `C2_D1_BLOCKER.json`, `C2_CRITICAL_RATIOS.json`);
- `result_classification` re-reads the forecast and checks the class, the closed set, the open set, three gap falls
  and both Γ against constants hard-coded in the qualifier;
- `gate_identity` requires exactly one commit in the gate's history — which I confirmed independently.

**The git-origin repointing was a legitimate environment fix, not a touch of the frozen tree.** `c2_b0_verify.py`
B1 compares `git ls-remote origin refs/heads/main` against the expected GitHub main `1cb45382`. In a clone whose
`origin` is a local worktree, `ls-remote origin` resolves against that local repository and returns `c123b9bb` — the
documented scratch-clone trap. Repointing the **clone's** `origin` at the campaign's real remote changes nothing
inside the frozen tree, leaves `git status` empty in the clone, and makes the check evaluate the quantity it was
written to evaluate. Had they instead relaxed the check, or edited `c2_b0_verify.py` (a pinned frozen producer),
that would have been impermissible. They did neither. I judge this **permissible and correct**.

**Finding C-1 (minor, but real).** The fix is disclosed only in the commit message of `b4bd007a`. It appears in no
artifact and in no document inside the namespace. A reader of the sealed packet cannot discover it. The campaign's
own standard elsewhere is that governance-relevant facts live in the namespace, not in commit messages; §"r9 FAIL 2"
of `ERRATUM_C2.md` makes exactly that criticism of itself ("existed only in a commit message, not in the
namespace"). This one repeats it.

**Finding C-2 (minor, but a breach of the packet's own reproducibility standard).** `c2_qualify.py` writes
`"tree": str(tree)`. The committed `C2_QUALIFICATION.json` carries
`"tree": "<clean clone at the freeze commit; path elided as incidental>"`. The recorded `qualifier_sha256` matches
the file on disk, so the artifact was **hand-edited after the qualifier produced it**, before its single commit.
The edited field is incidental (a local filesystem path) and no check, verdict or number is affected — but it means
the qualification artifact is *not* the byte output of the pinned qualifier and cannot be reproduced by re-running
it, which is the property every other artifact in this packet has. It is also undisclosed: it is not in the
replacement ledger and not in the erratum. Neither finding changes the verdict.

## D. Predecessor preservation — **PASS, unconditionally**

`git diff --name-status 5289b6ce HEAD`, filtered to paths outside
`level4/closure_proofs/p5y_k5_tail_c2_closure/`, is **empty**. Not "no modifications" — no rows at all. Every row in
the full diff is an `A` inside the C2 namespace except the single `M` on `config/C2_PROTOCOL.json` discussed in B.

- `main` is at `c123b9bb8f15d17650545b3fce4aca8a6b61093b`, exactly as the freeze record and the seal state, and no
  C2 commit is on it.
- `K5_COVERAGE_MAP_R4.json` hashes to `a3bddd83234f33983e07b005b4686a5f3971264bb6bdd64d2c639339de210a35` —
  byte-identical to the pin.
- No coverage map r5 exists anywhere under `level4/`. I did not create one and will not; that follows this verdict
  and is not mine to make.
- The order-3 producer's `REAL_CELL_AUTHORIZATION_REGISTRY.json` is still `FROZEN_EMPTY` with zero authorizations.

## E. Scientific correctness of the deterministic construction — **PASS**

This is the core and it is right. Bit-exact agreement on every number listed at the top of this document. Beyond
reproducing the values, I checked the constructions themselves:

**Lemma Dv′ (r2).** `A0 = Ā_eff`, `A1 = Ā_eff(κ₁C + δ₁)`, `A2 = Ā_eff(2κ₁²C² + κ₂C + 2κ₁Cδ₁ + 2δ₁² + δ₂)` with
`Ā_eff = min(Ā, τ/D_lo)`, `δ₁ = D1/D_lo`, `δ₂ = D2/D_lo` — matches `THEOREM_AD.md` §4 Lemma Dv′ term for term. The
rational κ bounds are valid: `κ₁ = √(2/π) = 0.79788456…< 7978846/10⁷` and `κ₂ = 4φ(1) = 0.96788276… < 9678830/10⁷`,
both upper bounds as required. The campaign's two implementations (`deflated_consume.atom_constants_r2`, frozen in
an *adopted predecessor* namespace, and `c2_d5_forecast._atom_independent`, written here) are compared for equality
on every supply and every cell before anything is emitted — a genuine cross-boundary check, and my third
implementation agrees with both.

**Lemma G.** `A0 = C, A1 = k₁C², A2 = k₂C² + 2k₁²C³` from the frozen K1 block bound `C_upper` and the frozen
drift-aware norms. I confirmed the CUSUM/SR `index` collision trap in `cells.json` is avoided (filtering on
`detector == "CUSUM"` reproduces `A0(305) = 7.732565297…`; using the SR row would not).

**The D4 componentwise minimum is sound and was genuinely pre-registered.** Each supply independently upper-bounds
the same three quantities, so the componentwise minimum is an upper bound of each, and each selected value carries
its own certificate. The rule is in the gate at `87309610`, before any C2 constant existed. In the event it does no
mixing: the C2 refined registry wins **every field of every cell**, so the selected tuple equals the C2 supply
throughout, and the provenance block says so.

**Theorem TC-T.** I re-derived `env4`, `p0/p1/p2`, `rad = A0p2 + 2A1p1 + A2p0`, `half = ρ|Ĝ(a)| + rad` with
`|Ĝ(a)| = 0`, and the assembly `Σ_{r<m}(1/m)[Ĥ_r(a) ∓ half_r] + Σ(1/t − 1/m)W_(r,t−r−1)`, from the theorem text.
The (P3′) r2 two-tower construction is sound as written: σ3 takes the midpoint tower (a (P2) premise at e₀, where a
midpoint bound is the right object); σ4 takes the cell tower whose order-3 slot carries the mean-value correction
`‖h_j‴(e)‖ ≤ ‖h_j‴(e₀)‖ + ρ·sup_C‖h_j⁗‖` with the order-4 bound from the *unrefined* tower, and re-derives order 4
from the corrected lower orders — valid because the Leibniz recursion is pointwise in e. The order-4 clamp is
defensive and never fires (the cell tower is componentwise ≤ the pure tower and the recursion is monotone). The
minimum of two valid upper bounds is a valid upper bound throughout.

**The K5-B direct test.** `Γ = (R.hi − e₀·D.lo) + ρ·x_hi·M` with pass iff `Γ < 0` is *verbatim* the direct clause of
the frozen `k5b_check.k5b_literal` (`ddd54dc4`), which I read rather than imported. C2 uses **only** the direct
clause, never the chain clause — which is strictly stricter than the theorem's own pass condition, so it can only
under-claim. The full composition (`tail_forecast_r2.compose`, which runs the real `k5b_literal` over all 310
cells) reports `newly_passing = [305, 306]` at m = 5 via `direct` and `regressed = []` at every m, so the adopted
set is exactly what the frozen theorem certifies and nothing previously passing is disturbed.

`M = min(M_R2, mag(H ∩ 𝓗))` is a valid tightening: R″ lies in both, hence in the intersection. The empty-intersection
fallback to `M_R2` is conservative. I verified the intersection is non-empty on all five cells — in fact
**𝓗 ⊆ R2_interval** on all five, with `mag(𝓗)/M_R2` = 0.6575 / 0.6471 / 0.6469 / 0.6519 / 0.6453, so the TC-T
enclosure, not the record, sets M everywhere.

**The class.** `classify()` resolves one hole the frozen gate leaves (closes no cell while tightening some) to
`D_INSUFFICIENT`, records the resolution rather than amending the gate, and the case is unreachable here. Correct
handling. Its redundant trailing branch — which had masked mutant M23 — was removed before the freeze, so every
branch is load-bearing.

## F. Registry / whole-cell premise validity — **PASS**

**Exact cover, verified as rationals, not asserted.** For each cell I recomputed `N_k = ceil((right − left)/(1/100))`
and the equal-width partition from the frozen cover's own endpoints, and compared to the committed `sub_rows`:

| cell | N_k | exact cover | widths ≤ 1/100 | contiguous, left edge to right edge | max/min composition re-derived | Dv′ premises on every sub-block and on the composed cell |
|---|---|---|---|---|---|---|
| 305 | 9 | yes | yes | yes | yes | yes |
| 306 | 9 | yes | yes | yes | yes | yes |
| 307 | 10 | yes | yes | yes | yes | yes |
| 308 | 11 | yes | yes | yes | yes | yes |
| 309 | 11 | yes | yes | yes | yes | yes |

The sub-blocks tile `[left, right]` exactly — first row starts at `left`, last ends at `right`, adjacent rows share
an endpoint, no gap, no overlap — so `sup_cell ≤ max_i sup_{B_i}` and `inf_cell ≥ min_i inf_{B_i}`, and
**worst-over-cover is a valid whole-cell bound**. The composition is max on C_T, τ, D1, D2 and min on D_lo, which
is the correct direction for each (upper bounds by maximum, the one lower bound by minimum). `Ā` is certified once
per cell over the whole cell, and is inert: `Ā > τ/D_lo` on all five cells, so `Ā_eff = τ/D_lo` and the ARL
supersolution never binds. `τ/D_lo` computed from composed `τ` (max) and composed `D_lo` (min) is ≥ the true
cell-wise supremum, i.e. conservative.

All four Lemma Dv′ admissibility premises (`τ ≥ 1`, `C ≥ τ`, `D_lo > 0`, `Ā ≥ 1`) hold on every one of the 50
sub-blocks and on all five composed cells, and separately on all five C1 blocks. C1's blocks are
endpoint-for-endpoint identical to the frozen cover's cells, so C1's constants are genuine whole-cell bounds too —
which is what makes the D4 minimum over C1 and C2 legitimate.

**FLINT spot-check.** Using the independent python-flint venv (macOS 26.5.2 arm64, Python 3.14.5, python-flint
0.9.0, numpy 2.5.3) I re-certified five artifacts through the pinned `taboo_certify`:

| artifact | re-certifies | recomputed constants vs registry row | artifact sha vs registry |
|---|---|---|---|
| `taboo_block_306_00.json` | yes | C_T, τ bit-identical | match |
| `taboo_cell_306_00.json` | yes | D_lo, D1, D2 bit-identical | match |
| `taboo_block_305_04.json` | yes | C_T, τ bit-identical | match |
| `taboo_cell_309_10.json` | yes | D_lo, D1, D2 bit-identical | match |
| `arl_cell_306.json` | yes | τ = published Ā bit-identical | match |

I did not re-certify the other 100; the campaign's own `C2_REGISTRY_VERIFY.json` records 105/105 pass with host and
toolchain, and the qualification re-ran it. A useful incidental observation from the spot-check: `taboo_block_305_04`
(the *centre* sub-block of cell 305) returns C_T = 6.028953464721635 and τ = 5.291155319465771, which are exactly
C1's whole-cell values for 305 — confirming from the outside that these constants are driven by the block **centre**
and the α rung, not by the block width, which is the mechanism behind C2's τ/C_T regression (see J).

## G. Mutation / falsification adequacy — **PASS, with a caveat about the headline number**

The suite is honest and it is real. I re-ran it and reproduced `C2_MUTATIONS.json` byte-for-byte.

The three undetected mutants are **genuinely equivalent, not hidden failures**:

- **M19 (single-supply selector)** and **M20 (min by A0 only)** return the same tuple as the pre-registered
  componentwise minimum here because the C2 supply dominates G and C1 on every field of every tail cell — which I
  verified independently. The campaign's response is the right one: it added **M34 / M35**, the same two selectors
  restricted to the {G, C1} pair, where C1 does *not* dominate componentwise (C1 beats G on A0 and A1, G beats C1 on
  A2), and **both are detected**, on value and on provenance. That converts an unfalsifiable row into a falsified
  one without weakening it.
- **M32 (intersection skipped)** is equivalent because 𝓗 ⊆ R2_interval on all five cells, which I verified
  (ratios 0.645–0.658 above). The row states the condition under which it would revert to an undetected miss and
  says it is verified per run, not assumed.

Load-bearing mechanisms and their probes: the two towers and the mean-value correction (M01, M02), the radius terms
and each A-constant (M04–M06), the source-node map (M07), W endpoints (M08), the order-3 injection point (M09), the
sub-block *selection* (M11–M14) **and the sub-block geometry** (M28 gap, M29 overlap, M30 short cover — the last
three added only after a review pointed out that nothing checked the cover was a cover, which was a genuine
soundness hole with no probe), the classifier's three branches (M21–M23), the material-tightening denominator and
baseline quantity (M24, M25), the crosscheck's own assembly coefficients (M26, M27), and the M/intersection logic
(M31, M33).

**Gaps I did find, and how I discharged them.** No mutant targets (i) the K5-B corner choice — substituting `D.hi`
for `D.lo` in Γ — or (ii) the Lemma Dv′ algebraic coefficients themselves. Both are instead defended by using
pinned predecessor code plus a second implementation inside `c2_d5_forecast`. I closed both by hand: I read
`k5b_literal` and confirmed the corner, and I checked the Dv′ coefficients against `THEOREM_AD.md` §4 and against a
third implementation of my own. Neither is a defect in the result; both are worth a mutant in a successor.

**Caveat on the headline.** "43 applied / 40 detected" counts **35 executed mutants plus 8 static assertions**, and
the static assertions are substring greps over source files (`'cells outside the frozen C2 universe' in rr`, a pin
literal `in d5`, and so on). They are controls that a guard *exists*, not tests that it *works*. The artifact
separates `real_mutants: 35` from `static_assertions: 8` so the reader can see this, and the code comments say
"controls that must EXIST (not executed mutants)" — so it is disclosed, not concealed. But the aggregate 43/40 is
quoted as a mutation score in the qualification, the protocol's `expected_verdicts` and the commit messages, and
that overstates the falsification by 8. Recorded; it changes nothing.

## H. Sealed-result and consumer reproducibility — **PASS**

- The seal's own file hashes to `abf463a85cb42003854926253adabb1088ab82c8d9b4d3359b9889cfdf85429e` (`abf463a8…`).
- `sha256(canonical(manifest)) == seal.namespace_manifest_sha256`: **yes**.
- The 156-entry manifest: **zero drift**, every file present and hashing to its recorded value.
- Chain: `qualification_sha256`, `authorization_sha256`, `execution_sha256` and `gate_sha256` all re-hash to what
  the seal records.
- The five namespace files not in the manifest are exactly the ones that could not be (the seal, the manifest, and
  the three post-seal consumption artifacts), plus one untracked `__pycache__` byte-file that is not in git.

**Consumer.** I ran `c2_consume.py` twice: both runs print
`sha256 = 4a89a719c8c97051cebf8c4fa94bf5bcaaf123c5a5d9ad2bac61362e225da393`, are byte-identical to each other and
**byte-identical to the committed `C2_CONSUMPTION.json`**. Determinism is by construction (no wall-clock or host
leaf is emitted at all), which is stronger than a tolerance.

**Tamper.** I exercised three tampers on a copy of the namespace outside the repository:

| tamper | consumer behaviour |
|---|---|
| alter a sealed evidence leaf (`C2_D5_FORECAST.json` Γ(309)) | exit 1, `manifest_drift` names the file |
| alter the execution record (one wall-clock leaf) | exit 2, hard `REFUSED: chain hash mismatch: evidence/execution/C2_EXECUTION.json` |
| alter the seal's own per-cell `pass` for 309 | exit 1, `agrees_with_seal: false`, the divergence surfaced |

The third case is worth naming precisely: the seal is not inside its own manifest, so tampering with the seal is
caught by the re-derivation (`agrees_with_seal` goes false and the exit code is non-zero) rather than by the hash
chain. The seal's hash is anchored in the committed `C2_CONSUMPTION.json` (`seal_sha256`), which I verified matches.
That is adequate; it is worth a successor making the anchoring explicit.

One structural observation, stated as a limitation and not a defect. The **executor** and the **consumer**
re-derive only the *classification* from the recorded per-cell values; neither recomputes Γ. Γ *is* re-derived
inside the lifecycle, by `c2_critical_ratio.py`, which refuses to emit anything unless it first reproduces C2's own
published Γ (and Campaign B's Lemma-G column) bit-exactly from committed evidence alone — and that producer is
re-run for determinism at qualification, at execution and by me. What is not re-derived anywhere inside the
lifecycle is the requirement/gap-fall bisection and the 310-cell composition, both of which need the off-host K1
record store. I re-derived the former myself; the latter I could not.

## I. Absence of unauthorized new-real evaluation — **PASS**

- `new_real_scientific_addresses_evaluated = 0`, `new_real_cpu_seconds = 0` in the execution record; the
  authorization authorizes 0 and names an explicit not-authorized list including any real order-3 address and any
  R-stage execution; `REAL_SCIENTIFIC_COMPUTE = DENY` before, during and after, in every artifact that mentions it.
- **Reachability**, checked rather than accepted: nothing C2 executes imports the order-3 real-producer namespace.
  `c2_b0_verify.py` only *hashes* `REAL_CELL_AUTHORIZATION_REGISTRY.json` and `ORDER3_PRODUCER_MANIFEST.json`;
  `c2_refined_registry.py` adds `p5y_k5_order3_readiness_audit/code` to `sys.path` solely to import the frozen
  `k5_minimality` cover loader (`load_cells`, `rat`) — that is the readiness-audit namespace, not the producer, and
  no gated entry point is touched.
- The order-3 authorization registry remains `FROZEN_EMPTY`, `authorizations: []`, byte-unchanged.
- The consumer refuses any measurement with `order3_fields_present`, and C2 passes `order3 = None` on every call
  (`Ĝ := 0`, so `sup_G = |Ĝ(a)| = 0` exactly). Mutant M09 confirms an order-3 field inserted at the wrong location
  is detected.
- The 2.69 CPU-h spent is operator certification — supersolutions for the kernel, its atom split and the one-step
  alarm probability — which touches no source, no candidate of F/D/H/G, no K1 record and no value of R. It is not
  new-real compute, and the gate classifies it that way in advance.
- AWS was not contacted by C2 (recorded in the seal) and was not contacted by me.

## J. Provenance limitations — **the disclosure is adequate and, on balance, against C2's own interest**

**The limitation is real and it bites.** `REGISTRY_C2.json` records no host, no toolchain and no precision. The
build worker's log records only the registry summary. So the *build* host is reported by the campaign and recorded
in no artifact. What the evidence establishes on its own is narrower than "reproduced across a host boundary": it is
"reproduced bit-identically on a host whose OS, architecture, Python and compiled Arb/FLINT build are fully
recorded". That is a materially weaker claim, and it is the claim the campaign now makes.

**The disclosure is not self-serving; it is unusually hard on itself.** `CELL_306_ADOPTION.md` prints the two
columns side by side and labels the left one "**reported, not recorded**"; it states that the stronger phrasing it
carried until review r7 "asserted a *difference* between two hosts, and only one of the two is recorded"; it records
that the point was raised as a note at round 2 and left undispositioned for five rounds before being failed at round
7; and it explicitly says the result "is short of the independent re-certification the C1 reviewer asked for". The
one piece of in-repo corroboration it offers (per-artifact `cpu_seconds` of 90.2 s and 88.3 s against 56.2 s and
66.1 s for the same certifications on the re-certifying host) is labelled "weak but real" and credited to the
reviewer who found it rather than to C2. N10 is carried forward with a concrete, nearly-free remedy for the
successor. I cannot improve on that disclosure.

**How much it limits the evidence.** Less than it first appears for the *existence* of the bounds, more than it
appears for their *independence*:

- It does **not** weaken the soundness of the constants as such. A supersolution certificate is one-sided and
  self-validating: if `w ≥ 1 + K̂_e w` holds in outward-rounded interval arithmetic, the bound holds, whoever ran it.
- It does **not** leave the numbers unchecked on *this* side of the boundary: 105/105 artifacts re-verified with
  host recorded, 18/18 for cell 306 bit-identical at 256 bits, 45/45 consumed constants still valid at 384 bits,
  and five artifacts re-certified by me on a third host.
- It **does** mean the programme has no evidence that the machinery was ever exercised on a *different* stack. The
  bit-identity result is therefore evidence about determinism, not about implementation independence — and
  implementation independence is the thing N9 says is missing. N10 removes the only cheap partial substitute for
  N9 that was available.

I also record a separate finding here rather than in C. **Finding J-1.** `CELL_306_ADOPTION.md` states that of the
27 diagnostic fields that moved under the precision change, "**nine** moved in the direction that would violate the
published bound, at a worst relative magnitude of **5.19 × 10⁻³⁰**". The committed artifact
`C2_RECERTIFY_306.json` records only `{"count": 27, "worst_relative": 5.3188387505108386e-30}`, in every one of its
three committed revisions. Neither "nine" nor 5.19 × 10⁻³⁰ appears in any evidence file. These are transcribed
numbers with no committed support — the failure mode this campaign named for itself and spent sixteen rounds
hunting — appearing in the one document it referred to me. The direction of the discrepancy is *against* C2 (the
artifact's own worst is larger and its count is larger), the quantities are internal diagnostics that are not
composed into the registry and not consumed by Lemma Dv′, and the consumed-constant test is 45/45 at both
precisions, which I confirmed from the artifact. So nothing decision-relevant rides on it. It should be corrected or
evidenced by a successor.

## K. THE CELL-306 MARGIN FLOOR — **decided here**

### The floor

I set the following floor. It is **prospective**: it governs future adoptions of K5 m = 5 tail cells from this
verdict onward. It does not reopen, impeach or revisit any cell already adopted in coverage map r4 or earlier.

> **K5 tail adoption floor (r1), set by this adjudication.**
>
> A pair (m, k) may be adopted only if the frozen K5-B certifies it (Γ < 0 under the campaign's own frozen closure
> rule) **and at least one of**:
>
> **F1 — supply independence.** Γ < 0 also holds under a certified atom-constant supply that does **not** depend on
> the Arb/FLINT supersolution operator registry — i.e. under Lemma G from the adopted K1 block bound `C_upper` and
> the frozen drift-aware norms. This limb is available for as long as **N9** (no second, independently written
> certifier of the operator constants) remains open, and lapses when N9 is closed.
>
> **F2 — degradation survival.** Γ < 0 still holds when every atom constant of the chosen supply is degraded
> uniformly in the unfavourable direction by the factor **×1.25**, i.e. the cell's uniform-A margin is ≥ 1.25.

### Why this floor, and why it is not a number fitted to the answer

I was asked to decide the question C2 correctly refused to decide, and I have seen 11.2 %. I cannot un-see it. What
I can do — and what I have done — is build the floor out of inputs that existed before this adjudication and that
were published by the campaign against its own interest, and state it as a rule over Γ and a fixed severity rather
than as a percentage threshold:

1. **The ×1.25 severity is C2's, not mine.** C2 invented it, applied it uniformly to all five cells, and published
   the result — including that cell 306 fails it — in committed evidence before any adjudicator existed. I am
   adopting the only degradation scenario on the table, not inventing one that happens to separate the cells.
2. **It is a disjunction, not a single bar.** A cell that is certified by a registry-free supply clears F1 even if
   it is thin, and a cell that is robust clears F2 even if it has no registry-free route. That is deliberate: the
   two limbs answer the two different things a margin could be protecting against.
3. **It does not mention 11.2 %, or any margin percentage.** It is a statement about supplies and about a fixed
   degradation factor.
4. **It is applied identically to both cells and to everything that follows.**

The substantive reason a floor is warranted here at all — when the programme's own precedent (Campaign A's
adjudication of cells 11–44) adopted on a valid enclosure plus a frozen K5-B pass, with no robustness requirement —
is this. The C1 reviewer attached three conditions specifically to cell 306. One was delivered. One was delivered
only in part, and the campaign says so: it is one implementation run twice, with the build host recorded nowhere
(**N9** and **N10**, both open, both acknowledged). The third *is* the floor. Discharging that condition by
declining to set any floor would be discharging it by ignoring it, and would leave the programme adopting a
permanent cell on the exact question — "is this margin enough?" — asked for the second campaign running after the
answer was already visible. A floor is the instrument the condition named, so I have named one.

The reason the floor is framed around *supply independence* rather than around a bigger margin number is that a
margin is the wrong instrument for the risk that is actually open. The open risk is N9: a possible systematic error
in a single implementation of the Arb supersolution machinery, of unknown magnitude. No percentage protects against
an unknown-magnitude logic error. What does protect against it is a second, structurally independent route to the
same conclusion. Cell 305 has one; cell 306 does not.

### Applying it

| | cell 305 | cell 306 |
|---|---|---|
| Γ (adopted supply) | **−0.088029069** | **−0.030469258** |
| margin `M_needed/M_after` | 1.353093 | 1.111935 |
| uniform-A margin | **1.4053** | 1.1277 |
| **F1** — Γ under Lemma G alone, no operator registry | **−0.043752 → closes. PASSES F1** | +0.019116 → does **not** close. **FAILS F1** |
| **F2** — Γ at every constant × 1.25 | **−0.033733 → closes. PASSES F2** | +0.029163 → does **not** close. **FAILS F2** |
| verdict | **ADOPT** | **DO NOT ADOPT** |

Cell 305 clears **both** limbs. Its closure has two structurally independent certifications of the atom constants:
one through the adopted K1 stack (Lemma G, `C_upper` and the frozen drift-aware norms — no Arb supersolution
anywhere in it), and one through the C2 refined registry. If the entire operator-registry surface were wrong, cell
305 would still close, with a 14.9 % margin. That is the property that makes a permanent adoption safe here, and it
is not a property of the margin size.

Cell 306 clears **neither**. Its closure exists only through the Arb supersolution registry — Lemma G leaves it
open by Γ = +0.019 — and it is the one cell of the five that the campaign's own degradation scenario turns over. It
is a *sound* closure; I reproduced it exactly and I have no doubt about its arithmetic. It is a sound closure whose
entire support is the one evidence surface the programme itself says has never been independently implemented, with
the build provenance of that surface recorded nowhere, and without the margin to absorb being wrong about it.

### What this costs, and why I judge the cost acceptable

Deferring 306 costs one campaign cycle, and it is a cycle the programme must run anyway: **N7 blocks any R-stage
authorization** until a successor freezes a D′ gate and runs the operator-level combination. That successor will
recompute all five cells. Under the mixed supply, cell 306 improves to Γ = −0.036198 with a uniform-A margin of
1.1555 — better, but still short of F2 — so I should be plain that a D′ campaign **alone will not discharge this
floor for cell 306**. What will:

- a **second, independently written certifier** reproducing the six operator constants for cell 306 (closing N9),
  at which point the registry-dependence objection is answered and a successor should freeze a replacement floor
  requiring agreement between two independent certifier implementations rather than F1; **or**
- further deterministic tightening bringing 306's uniform-A margin to **≥ 1.25**; **or**
- a real order-3 candidate — the headroom there is large (`Γ_perfect_order3(306) = −0.2175`) — under the R-stage's
  own separately frozen gate, and only after N1, N5 and N7 are discharged.

Against that cost stands the asymmetry of the error. An adopted cell is permanent, is removed from every future
campaign's universe, and is never revisited. A deferred cell is recomputed next cycle at no compute cost, with its
refined registry intact, under a floor frozen in advance — which is precisely the outcome the C1 reviewer asked
for and precisely the branch C2 itself pre-committed to.

### On the frozen `D_PARTIAL` rule

The gate says "a non-empty closed subset is always adopted when the adjudication chain completes", and argues that
declining to adopt "has twice already left a soundly closed cell 305 unadopted". **I am satisfying that rule, not
narrowing it.** The closed subset I adopt is non-empty, and it contains exactly the cell whose repeated
non-adoption the rule was written against. C2 pre-committed, before any adjudication existed, to "adopt 305 only"
in the branch where the adjudicator sets a floor cell 306 fails. That is the branch, and this is that outcome.

---

## ADOPTED CELL SET

    [305]

For the coverage map generator: the pair (m = 5, cell 305) moves from OPEN to CLOSED. Cells 306, 307, 308 and 309
remain OPEN at m = 5. K5 remains **PARTIAL**. m = 1, 2, 3 are unaffected and remain complete on 0–309.

I have **not** generated coverage map r5 and no r5 exists in this worktree.

---

## Conditions and notes attached to this verdict

1. **The floor above is now the standard** for K5 m = 5 tail adoptions, prospectively. A successor that wishes to
   replace it must freeze the replacement **before** recomputing any magnitude, as the D′ document itself insists.
2. **Cell 306 is carried forward with its refined registry intact.** Nothing about it is retracted or impeached.
   Its Γ, its margin and its eighteen re-certified artifacts stand as published, and I have confirmed them.
3. **N7 stands and must be discharged before any R-stage address is spent.** I independently confirmed the D′
   mixed-operator claim: the componentwise best of C1's and C2's six operator constants — min on τ, C_T, D1, D2,
   max on D_lo, min on Ā, each limb valid uniformly on the whole cell because C1's block is endpoint-identical to
   the cover cell and C2's sub-blocks tile it exactly — is a sound supply that satisfies all four Dv′ premises, and
   it yields requirements **1.11196624 / 1.46065480 / 1.84787350** and gap falls **57.27 % / 30.57 % / 23.03 %** on
   307/308/309. All three clear the gate's own 20 % bar, at zero CPU and zero new real addresses. The premise that
   the deterministic direction is exhausted is **not established**, and C2 is right to say so and right not to take
   the step itself. This finding is the reviewer's, C2 confirmed it from a committed producer, and I confirm it
   here a third time.
4. **N9 and N10 remain open and are now load-bearing for adoption**, by limb F1 of the floor. A successor should
   make the registry builder record its own host, toolchain and precision (N10) — it is nearly free — and should
   treat a second, independently written certifier (N9) as the item that unlocks the remaining tail cells rather
   than as a nice-to-have.
5. **Findings C-1, C-2, J-1 and the G caveat** should be dispositioned by the successor. None of them changes any
   number, any class or this verdict. C-2 in particular should be fixed by making the qualifier emit the elided
   field itself, so the artifact is again exactly what the pinned producer writes.
6. **Recommended mutants for the successor suite:** the K5-B corner (`D.hi` for `D.lo` in Γ) and a perturbation of
   each Lemma Dv′ coefficient. Both are load-bearing and neither currently has a probe.
7. The eight static assertions should stop being aggregated into the mutation score quoted upstream; report 35/35
   executed mutants and 8 static controls separately.

---

## What I did not check

Stated precisely, because the value of this adjudication depends on the boundary being honest.

- **The adopted K1 record store.** The 326 CUSUM records live off this host
  (`/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records`) and I did not contact any remote host. My
  re-derivation reads the committed `ADOPTED_TAIL_INPUTS.json` extract instead. Campaign B's producer checks that
  extract field-by-field against the records at run time (`R_interval`, `D_interval`, `R2_interval`, `M_R2` for
  every m, `C_upper`, every `candidate_suprema`, `midpoint_eps` and `eps_cell_refined` leaf) and refuses on any
  difference, and the extract is pinned in the protocol at `485fb125…`; but I verified that binding only by reading
  the code, not by executing it against the records.
- **The replay gate** — that the adopted post-Campaign-A state with no tail route reproduces the sealed Campaign-A
  consumption pass ranges for every m — needs the record store. Not re-run. The producer refuses if it fails.
- **The full 310-cell `k5b_literal` composition**, including the chain clause, the Perron deflation on [0, 148],
  the T-EXT channel on cells 0–40 and the sealed Campaign-A enclosures on 11–44, and therefore the
  `newly_passing = [305, 306]` / `regressed = []` results. Not re-run, same reason. I re-derived the tail cells'
  Γ directly instead, which is what the adoption turns on.
- **The frozen producer's 262-field identity gate** on the replayed measurements. I did re-derive the *derived*
  identity gate (20/20 contained, worst relative gap 3.6279 × 10⁻⁸), which covers `H_at_a` and `W2` — the fields
  the 262-field gate does not reach.
- **100 of the 105 registry artifacts.** I re-certified five with the FLINT venv (~5 minutes of the ~2.7 hours a
  full run needs) and relied on `C2_REGISTRY_VERIFY.json` and the qualification for the rest.
- **The cell-306 re-certification run itself** (18 artifacts × 2 precisions, ~40 min). I read the artifact, counted
  its rows (18/18 certified and 45/45 consumed constants valid at both 256 and 384 bits) and re-certified three of
  cell 306's own artifacts at 256 bits. I did not re-run the 384-bit pass.
- **The build host of the registry.** Not checkable — that is N10, and it is the point of N10.
- **Whether `c2_qualify.py` was in fact executed against a clean clone at the freeze commit.** The artifact says so
  and the commit message describes the run, but the artifact's `tree` field was hand-edited (Finding C-2) and I
  could not reproduce the run without cloning, which I judged to be outside "read-only git". I re-ran the three
  record-free producers and the consumer myself instead, and both reproduce byte-identically, which is the part of
  the qualification I can stand behind directly.
- **The sixteen pre-freeze reviews' own findings.** I read r16 in full and sampled the others. I did not audit
  whether each round's claims about the previous round are accurate; r16 reports it did, and the erratum's
  replacement ledger is independently rebuildable from the git object store by the command it gives.
- **Anything on AWS.** `mcp__rebaseguard-aws__*` was not called. SR/PS1 is an unrelated live campaign and I did not
  go near it.
- **C1's own published margin for cell 306 (1.0193×).** I reproduced it indirectly — `C2_CRITICAL_RATIOS.json`'s C1
  column gives Γ(306) = −0.005719468, which is bit-identical to `C1_FORECAST.json`'s own sealed
  `Gamma_exact`, and I reproduced that producer byte-for-byte. I did not re-derive C1's forecast from C1's own
  chain.

---

*Adjudicated at `2d626506` on branch `p5y-k5-tail-c2`. This document is the only file I wrote. No coverage map was
generated; that follows this verdict and belongs to whoever generates it, mechanically, from the adopted cell set
stated above.*
