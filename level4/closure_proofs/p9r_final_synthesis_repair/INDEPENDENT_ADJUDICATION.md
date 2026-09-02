# Independent adjudication of Priority 9 Repair (P9R)

**Verdict: `FINAL_P9R_VERDICT = CLOSED`.**

This is an independent, adversarial adjudication of the P9R candidate at
Checkpoint B, `eea2bfb43803e853a1bc84d10410fd9f3984d849`. It does not amend
the original P9 adjudication: `P9 = PARTIAL`. Closure here means that the
identified P9 repair obligations are closed. It does not mean that Level 4 is
globally closed, that `ASM-DOM` or global monotonicity has been proved, or that
novelty is established (`NOVELTY_STATUS = NOT_ESTABLISHED`).

Two reviewer corrections are binding on interpretation. First, the corrected
versus defective SR comparison supports a small observed aggregate difference,
not statistical or practical equivalence; the candidate word `IMMATERIAL` is
too strong without an equivalence margin. Second, the typed-graph validator is
a useful fail-closed consistency checker, not a semantic proof of every source
classification or edge type. Neither issue leaves the SR recurrence wrong,
restores an orphan result, or makes an unproved premise load-bearing in an exact
claim.

## 1. Repository forensics

The audit began from a clean worktree with `HEAD = main = origin/main =
eea2bfb43803e853a1bc84d10410fd9f3984d849`. A live `git ls-remote` confirmed
the same remote tip. The other registered worktree was
`/Users/suzhe/ReBaseGuard-p9` on `p9-research` at `5411e2c...`.

The relevant history is linear:

```text
a3e3cabc30c4508b866736aeede54db17e5e1fcc  original P9 adjudication (PARTIAL)
dc8516732c2c5672987a6a5a22c1ce023c77f68f  P8R adjudication (CLOSED)
c1e8f98bb908aff095814f3c45994ecc0f0846ed  P9R Checkpoint A
eea2bfb43803e853a1bc84d10410fd9f3984d849  P9R Checkpoint B
```

Checkpoint B has A as its direct parent; there was no squash or rewrite.
During the audit, another repository task advanced `main` through later P5X
and R-A commits. At the last pre-integration check its tip was
`e02b5ce04798668fc4d406d5b528887dccf66da6`. Those descendants add a separate
namespace and preserve the P9 and P9R trees byte-for-byte. The P9R scientific
adjudication below is therefore about the authentic A-to-B campaign, while the
final integration commit may descend from a later repository tip.

Path history confirms exactly one commit touches the original P9 namespace
(`a3e3cab...`), and only A and B touch P9R through Checkpoint B. No P1-P8 or
P8R closure artifact changed between the P8R adjudication and B as part of
P9R.

## 2. Temporal integrity

At A, `git ls-tree` returns exactly 34 P9R files. The only path below
`results/` is
`results/integrity/protected_tree_manifest_pre.json`. The frozen protocol,
gates, theorem and assumption statements, claim classes, ledger schema, edge
semantics, source manifests, generators, commands, estimands, thresholds and
verdict semantics are all present at A.

The A-to-B diff changes no source-manifest or protocol-digest member. The
20-file source aggregate remains
`c1d53e2cf66e0e18b9d4599cef8b07d3151c9cf27033e682355094a6bb16b46d`;
the 9-file protocol aggregate remains
`446f41a3815c4cc7c76daad89d125973aeaa1f72b318cf7919ea37c0139549e3`.
Only the deliberately excluded `TEMPORAL_ANCHOR.md` placeholders changed.

The local remote-tracking reflog records A on `origin/main` at
2026-09-02 15:24:41 +09:00. The first production result mtime is 15:25:16,
followed by the other generators; B was pushed at 15:39:53. Production
artifacts record A as `git_commit` and a dirty-at-write state, as expected for
post-anchor generated outputs. The object database, digest comparison, reflog,
and result timing agree. `TEMPORAL_ANCHOR = VALID`.

## 3. Original P9 immutability

The P9 tree at `a3e3cab...`, at B, and at the later audited HEAD is
`3aec482ec1f87184848b4bb60a7ee7c6928e3127`; byte-level diffs are empty.
The original machine adjudication still says `PARTIAL`. P9R is a successor
repair namespace, not rewritten history. `ORIGINAL_P9_PRESERVED = YES`.

## 4. First-principles reconstruction of P9R-T2a

Under authoritative convention A,

\[
e_{j+1}=\rho(e_j+\bar Z_w)+(1-\rho)\bar Z_{\mathrm{fresh}},
\qquad \bar Z_{\mathrm{fresh}}\sim N(0,1/m),
\]

where the fresh reference sample is independent of the current state and of
the alarm-selected observations. At `rho = 0`, the selected term vanishes
exactly. Detector reset, stopping, and window bookkeeping cannot reintroduce
conditioning into the fresh term. Hence
`K(e, ·) = N(0,1/m)` for every current state `e`.

If a probability law `mu` is invariant, then `mu K = N(0,1/m)` because the
kernel is constant, while invariance says `mu K = mu`; therefore the Gaussian
law is the unique invariant probability law. For the frozen CUSUM and SR
stopping times, a uniform geometric stopping bound gives finite `A(e)` and
integrability. Thus the stationary ARL is exactly
`E_{e~N(0,1/m)}[A(e)]`. The local multiplier is the separate
conditional-mean derivative `rho(1-Gamma)`, which is exactly zero at `rho=0`.

All four subclaims survive without simulation or monotonicity:
`P9R_T2A = EXACT`.

## 5. P9R-T2b and ASM-DOM

Let `g(e)=A(0)-A(e)`. Under `ASM-DOM`, `g` is measurable, integrable and
nonnegative almost everywhere under the exact invariant Gaussian law, and is
positive on a set of positive measure. Therefore `E[g]>0` and
`E[A(e)]<A(0)`. No continuity or global monotonicity is required. The finite
stopping bound supplies integrability; the candidate's `A(0)>1` and
`A(e)->1` lemmas supply positive-measure strictness.

`ASM-DOM` itself is not discharged. All exact-looking uses were searched in
README, THEORY, RESULTS, ledger, graph, scope map, limitations, tests, handoff,
and JSON artifacts; no exact downstream theorem silently imports it.
Accordingly `P9R_T2B = CONDITIONAL_ON_ASM_DOM` and
`ASM_DOM = NOT_ESTABLISHED`.

## 6. Global monotonicity

The response experiment uses 321 nodes per detector on `[0,8]`, step 0.025,
20,000 paths per node, and 320 adjacent comparisons per detector. It reports
0 of 640 increases at the 3-SE rule and an empirical argmax at zero. Nodes use
independent seeds rather than common random numbers. The combined-SE rule has
no familywise multiplicity adjustment, and the recorded minimum detectable
increase shows low power near zero. This is useful descriptive evidence, not a
proof or certificate. `GLOBAL_MONOTONICITY = EMPIRICALLY_SUPPORTED`.

## 7. SR recurrence reconstructed independently

The authoritative symmetric two-chart SR recurrence is

\[
R_t^\pm=(1+R_{t-1}^\pm)\exp(\pm z_t-1/2),\quad R_0^\pm=0.
\]

P7 stores `y=log(1+R)`, initializes `y=0`, computes the alarm statistic
`ell=y_prev +/- z - 1/2 = log R_t`, alarms inclusively at
`ell >= log(A)`, stores `logaddexp(0,ell)` if the cycle continues, and resets
to `y=0`.

For `z1=0.25`, the first plus/minus log statistics are `-0.25` and `-0.75`.
For `z2=-0.75`, they are `-0.6740605801211564` and
`0.6368710061148999`. After reset, `z=0.1` again gives `-0.4` on the plus
chart. P9R implements these values and reset semantics. Original P9 instead
applied `logaddexp(0,state)` to an initial zero state before adding the
increment, giving `0.4431471805599453` rather than `-0.25`: an exact first-step
shift of `log(2)=0.6931471805599453`. A threshold witness also makes the alarm
decisions differ. `SR_RECURRENCE = CORRECTED` and
`ORIGINAL_LOG2_DEFECT = REPRODUCED_EXACTLY`.

## 8. Corrected reproduction

An isolated clone replayed the complete production generator. All 16 payload
rows were byte-identical to the stored payload. CUSUM is MC-consistent in 8/8
cells with maximum `|z|=2.3630617101`; corrected SR is MC-consistent in 8/8
with maximum `|z|=1.7282259220`. The generator reads P7's estimands,
replication counts and burn-in, resets each cycle, and uses the stated SE and
combined-z formulas.

The defective-versus-corrected SR aggregate is reported as
`+0.402 +/- 0.200` cycles (6/8 cell signs positive; `|z|=2.01`). This shows a
small observed aggregate effect under that experiment. It does **not** prove
immateriality or equivalence because no practical equivalence margin was
specified. Moreover, once alarm paths diverge, sequential random-number
allocation is not a strict per-path addressable CRN coupling, so the paired SE
should not be treated as a rigorous equivalence test. The recurrence defect is
scientifically real and is closed because the recurrence was corrected, not
because its observed aggregate effect was small.

## 9. A5/A6 reproducibility

Both retained artifacts name an existing manifest-covered generator, frozen
configuration, seed namespace/addressing, command, environment, schema and
canonical payload digest. Reduced A5 and A6 runs were each executed twice and
were byte/digest stable. The full reproduction was byte-identical. No retained
scientific result in the P9R result set is orphaned. The immutable original P9
orphans remain historical evidence but are not used without the P9R
replacement. `A5_A6_REPRODUCIBILITY = REPAIRED`.

## 10. Source-derived claim-ledger audit

The generated graph contains 75 nodes and 108 typed edges; the validator finds
zero violations, while the intentionally collapsed-edge diagnostic finds 36.
Manual samples across P1-P9/P8R agree with their authoritative sources and
adjudications. In particular, P4/P5 retain exact surviving claims alongside
their `PARTIAL` statuses; P8 retains surviving evidence alongside `FAIL`; P8R
and P9 remain distinct successor/original records.

One traceability limitation is recorded: the `ASM-P4-A1A7` citation names a
directory, and validator V8 checks only path existence, not that section text
entails the ledger wording. Manual source review supports the row, but the
validator alone does not. This does not alter an outgoing load-bearing exact
premise.

## 11. P3-X1

`P3-X1 = CERTIFIED_NUMERICAL` is the strongest accurate class. The witness
combines exact rational arithmetic with an outward-rounded 128-bit Arb
consistency enclosure; its own record says the Gaussian layers are not
certified. The Lean correspondence proves an abstract spine and makes no
numerical claim. It is not `FORMALLY_VERIFIED`.

## 12. P7-A / P7-D0 split

The candidate split is sound. `P7-A-ID` is the exact finite-cycle mixture
identity; `P7-A-MONO = NOT_ESTABLISHED`; `P7-A-OP` is empirical. `P7-D0-ID`
is the exact `rho=0` identity, while `P7-D0-DEF` is conditional on the named
dominance premise. Stationary uses carry existence/integrability. Outgoing
logical-premise edges use the identity nodes, not empirical monotonicity.

## 13. Dependency-graph adversarial mutations

The actual typed graph passes and the core premise closure was also audited
manually. The validator rejects: empirical-only to exact as a logical premise;
conditional to exact without assumption propagation; certified numerical
relabelled formal without formal evidence; a P8 `FAIL` status node used as an
exact premise; empirical monotonicity relabelled exact; and `ASM-DOM` empirical
support changed to an exact logical premise. Removing `ASM-DOM` makes the
validator terminate with `KeyError`, which is fail-closed but not a graceful
structured violation. Changing the rank-neutral `P9R-E1 -> P9R-T3` edge from
`EMPIRICAL_SUPPORT` to `LOGICAL_PREMISE` is accepted, demonstrating that edge
semantics still require manual review. `DEPENDENCY_GRAPH =
PASS_WITH_REVIEWER_LIMITATIONS`.

## 14. Partial/fail premise propagation

The manual source audit finds no priority status used as a blanket theorem
license or blanket eraser. The P9R core preserves the surviving exact P4/P5
claims only within their scopes. Neither P8 nor P8R occurs in the computed
premise/assumption closure of P9R-T2a or T2b.

## 15. P8/P8R reconciliation

`P8 = FAIL` and `P8R = CLOSED` remain separate. P9R preserves the rejected
window law, measured absence of detector transfer, conditional P8R-T1,
statistically fragile S15 evidence (upper 95% value about 1.9425), and novelty
that is not established. No P9R statement converts P8R closure into universal
model-class robustness. `P8R_REQUIRED_FOR_P9R_CORE = NO`.

## 16. D-09, D-13 and D-15

- `D-09 = BLOCKS_GLOBAL_LEVEL4_CLOSURE; DOES_NOT_BLOCK_P9R`. The root
  governance/status contradiction remains real, but neither P9R theorem relies
  on a globally closed Level 4.
- `D-13 = SCOPE_LIMITING; DOES_NOT_BLOCK_P9R`. The approximately 16-chain-SE
  residual attacks the gridded/PCHIP plug-in reconstruction, not the exact
  P5-T11 realized-window identity, and is not a P9R core premise.
- `D-15 = PROVENANCE_LIMITATION; DOES_NOT_BLOCK_P9R`. It limits provenance of
  the frozen P3 grid, not the continuous analytic boundary theorem used here.

None of these discrepancies is closed by this adjudication.

## 17. Formal verification scope

Four ledger rows have Lean proof spines. Their source hashes match the frozen
manifests; source scans find no `sorry`, `admit`, declared `axiom`, `unsafe`,
or `native_decide`. All four source modules compiled independently. P1 and P2
axiom audits, and the stored P3/P4 audits, use only `propext`,
`Classical.choice`, and `Quot.sound`.

Lean does not prove `ASM-DOM`, global monotonicity of `A(e)`, any numerical
value, or the complete P9R-T2a probability model. The exact T2a result is a
human mathematical derivation from frozen definitions and scoped prior facts.

## 18. Certified numerical scope

The surviving frozen-Gaussian certificate is for the symmetric two-chart SR
model, `m=1`, threshold
`4581762885148045/8796093022208 = 520.886133602749`, at 192-bit Arb
precision:

```text
Gamma_SR in [5.80039179950844233566..., 28.78128580308149205927...]
```

All three independent certificate auditors passed (monotone block
contraction; 1,210-patch global-a residual; 1,210-patch global-b residual), as
did 28 focused certificate tests. This certification is not propagated to
P9R Monte Carlo, the response grid, ASM-DOM, or global monotonicity.

## 19. Exact/empirical language firewall

Contextual searches for `proves`, `establishes`, `exact`, `guarantees`,
`safe`, `universal`, `for all`, and `boundary` found no material promotion of
empirical monotonicity or operational degradation into an exact theorem. The
candidate explicitly rejects universal impossibility. The overstrong word
`IMMATERIAL` is corrected by this adjudication as described in section 8; it
does not support an exact or load-bearing claim.

## 20. Operational-safety conclusion

The strongest defensible conclusion is four-tiered:

1. Exact: the `rho=0` constant kernel, unique invariant Gaussian law,
   stationary mixture identity, and zero local multiplier.
2. Conditional: a strict stationary-ARL deficit under `ASM-DOM`.
3. Empirical: P7/P9R reject the specific P7 frozen nominal-ARL preservation
   rule for CUSUM and SR at `m in {1,2,3,5}`.
4. Unsupported: no universal claim that every conceivable rho-based
   operational boundary is impossible.

## 21. Novelty

The earlier 2,445-work search is prior-art evidence, not a novelty proof. P9R
does not conduct a novelty campaign or upgrade that search.
`NOVELTY_STATUS = NOT_ESTABLISHED`.

## 22. Protected tree and P9R-D04

The P9R pre/final manifests each cover 3,428 files in 32 trees and have the
same aggregate digest
`a52a8a...`; independent file-by-file comparison gives zero changed, added or
removed protected paths. Both original P9 and P8R are covered.

The single P8R regression failure was reproduced. Its test treats every later
tracked addition outside P8R as unauthorized, so the existence of P9R (and, at
later HEAD, subsequent namespaces) triggers it despite zero changes to P8R or
the frozen protected bytes. `P9R-D04 = HARMLESS_ADDITIVE_SET_VERIFIER_SCOPE`,
not a protected-tree defect. Later post-B campaigns are outside the P9R
snapshot and were separately checked not to alter the P9/P9R trees.

## 23. P9R-D05

The frozen discrepancy register was correctly preserved. The frozen protocol
also says new production discrepancies belong in that register and require a
new anchor if scientific sources/results must be rerun. Recording D04/D05 in
`LIMITATIONS.md` preserved the freeze but did not literally use the named
register. This is a transparent protocol-design tension, not evidence of
outcome-responsive science: neither row required a changed estimand, source,
threshold or rerun. `P9R-D05 = NONBLOCKING_PROTOCOL_DESIGN_CONTRADICTION`.

## 24. Focused tests and independent reproductions

The candidate focused suite passes `110/110`. In addition to the full
reproduction, reduced A5/A6 double runs, SR hand calculations, validator
mutations and source audits above, the certified-SR subset passes `28/28`.
These tests establish implementation consistency; they are not substituted
for the mathematical adjudication.

The reviewer JSON added by this adjudication is not a candidate-generated
scientific result. The frozen candidate orphan-artifact test enumerates the six
candidate result names, so it should be interpreted at Checkpoint B rather
than used to demand a generator for an independent adjudication record.

## 25. Repository-wide regression

The independently run matrix is:

```text
level4/tests                               290 passed, 0 failed
p7_statistical_consequences/tests          31 passed, 0 failed
novelty_verification/tests                 17 passed, 1 failed
external_validation_v2/tests               43 passed, 2 failed
final_global_reaudit/tests                  33 passed, 3 failed
final_level4_closure/tests                  32 passed, 4 failed
p8r_temporal_integrity_repair/tests         71 passed, 1 failed
p9_final_synthesis/tests                    44 passed, 0 failed (clean tree)
p9r_final_synthesis_repair/tests           110 passed, 0 failed (Checkpoint B)
SR certificate focused tests               28 passed, 0 failed
```

The historical failure counts match the candidate baseline. Their causes are
stale historical protected manifests/global status, plus P8R's additive-set
scope semantics; they are not P9R regressions. The 290-test core suite creates
untracked P4/P5 audit outputs and a P5X self-test result; those test side effects
were isolated before the clean-tree P9 rerun.

The unified Level 1-3 verifier also passed all checks with zero skips: the
8,717-job Lean build, bypass scan, nine-theorem axiom audit, direct final-module
elaboration, full Arb replay, 90-test proof regression suite, and independent
certificate arithmetic all passed.

## 26. Remaining limitations

`ASM-DOM` and global monotonicity remain unproved; the response grid is finite,
Monte Carlo, independently seeded and multiplicity-unadjusted; the SR defect
effect has no equivalence margin; one ledger citation is directory-level; the
validator is syntactic/rank-based and has one ungraceful missing-node path;
P4/P5 retain their adjudicated limitations; P8 remains failed; D-09/D-13/D-15
remain open; transfer beyond the frozen Gaussian detectors/windows is not
proved; and novelty is not established.

## 27. Closure standard applied

The authentic pre-result anchor is valid, original P9 is immutable, T2a is
exact within its frozen scope, T2b is honestly conditional, the SR recurrence
is corrected, A5/A6 are reproducible, P8 is quarantined without erasing its
evidence, and no material exact/empirical claim inflation remains. The open
items above are expressly allowed by the P9R closure standard or are
nonblocking reviewer corrections. The P9-specific repair lineage is therefore
closed.

## 28. Global status

`LEVEL4_GLOBAL_CLOSURE = NO`. This adjudication does not resolve D-09 or the
historical/global mandatory ledger, and it does not close P4, P5, or P8.

## 29. Required 44-item final report

| # | Required item | Independent finding |
|---:|---|---|
| 1 | FINAL_P9R_VERDICT | `CLOSED` |
| 2 | repository state | Began clean at B; later main advanced to preserved descendant(s), separated from the B audit |
| 3 | ancestry / A/B authenticity | Authentic; B is the direct unsquashed child of pushed pre-result A |
| 4 | temporal-integrity verdict | `VALID` |
| 5 | original P9 preservation | `YES`; tree `3aec482e...`; verdict remains `PARTIAL` |
| 6 | P9R-T2a verdict | `EXACT` in frozen scope |
| 7 | rho=0 kernel-law verdict | `EXACT_CONSTANT_GAUSSIAN_KERNEL` |
| 8 | invariant-law uniqueness verdict | `EXACT_UNIQUE` |
| 9 | stationary-mixture identity verdict | `EXACT`, with finiteness proved for frozen detectors |
| 10 | local-multiplier verdict | `EXACT_ZERO_AT_RHO0` |
| 11 | P9R-T2b verdict | `CONDITIONAL_ON_ASM_DOM` |
| 12 | ASM-DOM status | `NOT_ESTABLISHED` |
| 13 | global monotonicity status | `EMPIRICALLY_SUPPORTED`, not proved |
| 14 | operational-safety conclusion | Frozen P7 rule rejected empirically; universal impossibility unsupported |
| 15 | SR recurrence verdict | `CORRECTED` |
| 16 | original log(2) defect | `REPRODUCED_EXACTLY` |
| 17 | corrected CUSUM reproduction | `8/8 MC_CONSISTENT`, max `|z|=2.3631` |
| 18 | corrected SR reproduction | `8/8 MC_CONSISTENT`, max `|z|=1.7282` |
| 19 | A5/A6 reproducibility | `REPAIRED`; reduced double runs deterministic |
| 20 | claim-ledger audit | 75 nodes/108 edges; source samples sound; one directory-level citation limitation |
| 21 | P3-X1 classification | `CERTIFIED_NUMERICAL` |
| 22 | P7-A/P7-D0 classification | Identity exact; deficit conditional; monotonicity empirical/not established |
| 23 | dependency-graph audit | `PASS_WITH_REVIEWER_LIMITATIONS` |
| 24 | adversarial validator results | Six load-bearing inflations rejected; missing ASM fail-closed by exception; one rank-neutral edge mutation accepted |
| 25 | P4/P5 premise propagation | Scoped surviving claims only; no blanket status propagation |
| 26 | P8/P8R reconciliation | `P8=FAIL`; `P8R=CLOSED`; negative/scope limits preserved |
| 27 | P8R dependency of P9R core | `NO` |
| 28 | D-09 verdict | Blocks global closure, not P9R |
| 29 | D-13 verdict | Scope-limiting plug-in discrepancy, not P9R-blocking |
| 30 | D-15 verdict | Grid-provenance limitation, not P9R-blocking |
| 31 | formal verification scope | Four abstract Lean spines; no ASM-DOM/monotonicity/numerical/full-T2a formal proof |
| 32 | certified numerical scope | Frozen m=1 symmetric SR Gamma interval only |
| 33 | empirical evidence scope | Frozen Gaussian CUSUM/SR, m=1,2,3,5, stated grids and protocols |
| 34 | novelty status | `NOT_ESTABLISHED` |
| 35 | protected-tree verdict | `PASS`; 3,428 files, zero P9R-campaign differences |
| 36 | P9R-D04 verdict | Harmless additive-set verifier scope semantics |
| 37 | P9R-D05 verdict | Nonblocking frozen-register protocol-design contradiction |
| 38 | focused tests | Candidate 110/110; certificate 28/28 |
| 39 | repository-wide regression | Candidate baseline reproduced exactly; no P9R-caused failure |
| 40 | remaining limitations | Listed in section 26; none silently closed |
| 41 | LEVEL4_GLOBAL_CLOSURE status | `NO` |
| 42 | adjudication artifact paths | This report and `results/independent_adjudication.json` |
| 43 | final commit hash | Self-referential; authoritative hash is the commit containing this file and is reported after commit |
| 44 | push status | Reported after integration; no claim is made inside this pre-commit artifact |

## 30. Machine-readable summary

```text
FINAL_P9R_VERDICT = CLOSED
P9_ORIGINAL_VERDICT = PARTIAL
TEMPORAL_REPAIR_ANCHOR = VALID
ORIGINAL_P9_PRESERVED = YES
P9R_T2A = EXACT
RHO0_KERNEL = EXACT_CONSTANT_GAUSSIAN
INVARIANT_LAW = EXACT_UNIQUE_GAUSSIAN
STATIONARY_MIXTURE_IDENTITY = EXACT
LOCAL_MULTIPLIER = EXACT_ZERO_AT_RHO0
P9R_T2B = CONDITIONAL_ON_ASM_DOM
ASM_DOM = NOT_ESTABLISHED
GLOBAL_MONOTONICITY = EMPIRICALLY_SUPPORTED
OPERATIONAL_SAFETY = FROZEN_P7_RULE_REJECTED_EMPIRICALLY; UNIVERSAL_IMPOSSIBILITY_UNSUPPORTED
SR_RECURRENCE = CORRECTED
ORIGINAL_LOG2_DEFECT = REPRODUCED_EXACTLY
A5_A6_REPRODUCIBILITY = REPAIRED
CLAIM_INFLATION = NO_MATERIAL_INFLATION; REVIEWER_CORRECTIONS_RECORDED
DEPENDENCY_GRAPH = PASS_WITH_REVIEWER_LIMITATIONS
P3_X1_CLASS = CERTIFIED_NUMERICAL
P7_MONOTONICITY_CLASS = EMPIRICALLY_SUPPORTED_NOT_PROVED
P8_ORIGINAL_VERDICT = FAIL
P8R_VERDICT = CLOSED
P8R_REQUIRED_FOR_P9R_CORE = NO
D09 = BLOCKS_GLOBAL_LEVEL4_CLOSURE; DOES_NOT_BLOCK_P9R
D13 = SCOPE_LIMITING; DOES_NOT_BLOCK_P9R
D15 = PROVENANCE_LIMITATION; DOES_NOT_BLOCK_P9R
PROTECTED_TREE = PASS_AT_CHECKPOINT_B
NOVELTY_STATUS = NOT_ESTABLISHED
SCIENTIFIC_CORE = SURVIVES_IN_FROZEN_SCOPE
LEVEL4_GLOBAL_CLOSURE = NO
AUTHORITATIVE_STATUS_RECOMMENDATION = RECORD_P9R_CLOSED; RETAIN_P9_PARTIAL_AND_LEVEL4_GLOBAL_NO
```
