# P5Y K1 cover and ledger governance successor

P5Y_K1_COVER_LEDGER_SUCCESSOR = FROZEN_WITH_IMPLEMENTATION_DEPENDENCIES

This status becomes binding at the single commit anchoring manifests/freeze.json.
This is governance/specification plus small pre-freeze diagnostics, not K1
production. PRODUCTION_ENABLED = false. K1 is NOT_RUN, not CLOSED. No historical
verdict, protected checkpoint, numerical threshold, budget amount, detector/m
scope or LEVEL4_GLOBAL_CLOSURE is changed.

## Authority, ancestry and reason for succession

START_HEAD = 8929bbede755933b7a2f1570f42756d17b227e44; starting worktree CLEAN.
Parent namespace: ../p5y_k1_successor_optimized/.
PARENT_SUCCESSOR_HASH = a5d09f83078bf02ae5d015bfb08eb35429190f646cc51260f6ca72fce6e325ec.
Parent binding checkpoint hash = ababbef4d42ad5a7a61e87279eb895c1b2d0ecfe67454f18c85acf6d57cd5c1d.
Task1R checkpoint hash = 20e664dec414b427e2b714531f3121224774f20f46cfe43e5c84300ec9de3aea.

Post-freeze implementation and diagnostics exposed ambiguities in cover
realization, Taylor expansion geometry, complete derivative dependencies and
ledger ownership. The prior conversational governance adjudication selected
FROZEN_SPEC_AMBIGUOUS_BUT_REPAIR_INTERPRETATION_SUPPORTED. It did NOT authorize
repair in place. The user's present explicit request authorizes this independent
successor and its prospective semantic decisions; it does not recolor old results.
There is no standalone ledger-adjudication file in START_HEAD. Its conversational
provenance is disclosed in manifests/authority.json, not invented as a prior
repository artifact.

Authoritative chain, read at START_HEAD and hash-listed in manifests/authority.json:

| Source | Load-bearing content |
|---|---|
| [P5 THEOREM](../p5_nonlinear_dynamics/THEOREM.md), [PROOF](../p5_nonlinear_dynamics/PROOF.md), [adjudication](../p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md) | Raw mean, stopped denominator, R'(0)=1-GammaTilde, oddness; historical P5 PARTIAL |
| [P5X frozen theorem](../p5x_global_nonlinear_dynamics/FROZEN_THEOREM.md), [scope](../p5x_global_nonlinear_dynamics/FROZEN_SCOPE.md), [proof](../p5x_global_nonlinear_dynamics/PROOF.md) | Fredholm reduction, exact short-stop coefficients, two detectors/four m; inherited SR coordinate erratum as resolved by parent K1 |
| [Gate-2E preregistration §6](../p5y_gate2e_sr_metric/GATE2E_PREREGISTRATION.md) | .050 cover, .040 candidate/kernel/other, .010 rounding/interval, nondrawable reserve; derivative-equation overlap |
| [Binding K1 checkpoint §§3,6,8,11,27](../p5y_k1_binding_campaign/CHECKPOINT.md), its JSON and budget ledger | Raw all-m assembly, explicit F0 budget, cover descriptions, no post-freeze amendment |
| [Task1 adjudication](../p5y_k1_binding_campaign/adjudication/TASK1_ADJUDICATION.json), [Task1R checkpoint](../p5y_k1_task1r_budget_harness/CHECKPOINT_T1R.md), harness and adjudication | Task1 FAIL/IMPLEMENTATION_DEFECT; Task1R PASS; nested .040 partition and endpoint gate |
| [Optimized checkpoint](../p5y_k1_successor_optimized/CHECKPOINT_S.md), config/checkpoint_s.json and manifest | Frozen parent, inherited ledger, 1126 CPU-h, 64 workers, 256 bits, complexity 60000 |
| [R1 cost reprojection](../p5x_global_nonlinear_dynamics/compute_optimization_r1/R1_COST_REPROJECTION.md), [R1 frozen spec](../p5x_global_nonlinear_dynamics/compute_optimization_r1/R1_FROZEN_SPEC.md) | Cost count versus half-step density; exact-rational benchmark geometry |
| [Historical R1 Taylor code](../p5x_global_nonlinear_dynamics/compute_optimization_r1/r1_stop_gate.py), [minorant proof](../p5x_global_nonlinear_dynamics/compute_optimization_r1/PROOF.md) | Midpoint Taylor construction; M1/M2 and valid whole-cell upper C; old g system is not today's raw certificate |
| [SR cover code](../p5y_gate2b_sr_cover/sr_cover.py) and its stored result | Direct SR Bellman bound exists; old 322 uses coarse drift-envelope walk |
| [Production driver](../p5y_k1_production_driver/k1prod/driver.py), [kernel adapter](../p5y_k1_production_driver/k1prod/kernel.py), [raw kernel](../p5y_k1_cusum_kernel/code/cusum_raw.py) | Float assembly under enclosure field names, missing complete dependencies/curvature and old work universe; unchanged |
| [Near-zero diagnosis](../p5y_k1_cusum_kernel/diagnostics/DF0_NEAR_ZERO_DIAGNOSIS.md), decomposition JSON, [cover finding](../p5y_k1_cusum_kernel/COVER_WALK_FINDING.md) | 244% historical dF0 charge, representative defects, actual CUSUM walk discrepancy |
| [Historical budget-stop adjudication](../p5y_k1_production/adjudication/K1_PRODUCTION_ADJUDICATION.json) | K1_INCOMPLETE_BUDGET under 1848 CPU-h; no mathematical contradiction |

All parent manifests are rehashed including their aggregate path-NUL-digest-LF
rule. The new protected snapshot covers all 3780 START_HEAD tracked paths,
including modes and immutable Git object identities. Tests compare both index
and worktree against that anchor; new work is confined to this namespace.

Verification limits: the six-row diagnostic JSON reproduces the e=0 dF0 charge
2.440039489968827, the defect roles and amplification. The committed diagnosis
states 256/384/512-bit invariance; it does not archive the per-precision probe
records. This task does not claim an independent replay of those probes. Neither
that narrative nor a float R'(0) is a new scientific certificate or closure.

## Design choice and alternatives

Midpoint expansion is selected because it matches the historical certified
Taylor construction, fixes the actual expansion distance, and requires no
asymmetric Taylor bookkeeping. Left expansion with rho=full width is valid
mathematically but increases the first/second-order geometric factors and adds
avoidable convention divergence. Left expansion with rho=half width is invalid
and rejected. Selection precedes the new midpoint diagnostic results.

STYLE_1 is selected: D_interval contains all derivative uncertainty and the
Taylor charge uses its magnitude once. A center-plus-error representation could
be equivalent, but mixing it with interval magnitude would duplicate error.
These choices are prospective, not claims of unique old frozen semantics.

## Exact executable cover (both detectors)

The entire ordered table is config/cells.json. Ordered detectors are CUSUM then
SR; cells within a detector are ordered by increasing left endpoint. Domain
CUSUM is [0,11/2]. Domain SR is [0,c_SR] with the exact unchanged splice
c_SR=log(4581762885148045/8796093022208)+1/2. A=4581762885148045/8796093022208
is the inherited exact detector threshold. SR state is log(1+R), b=log(1+A).
Negative drift is covered by the inherited exact oddness. Far-field theorem
P5X-T3 and the parent splice obligations remain mandatory for both detectors.

1. Q=10^7. Start left=0. Every nonterminal right is an integer divided by Q.
2. Evaluate the inherited detector-specific Bellman upper bound at that EXACT
   left endpoint: CUSUM 100 state cells, SR 200; horizon 250, 192-bit Arb,
   python-flint 0.9.0. Require probability row mass balance. The module sources
   and their dependencies are protected by the start snapshot.
3. Quantize conservatively: C_new=ceil(upper(C_Arb)*2^32)/2^32. Take
   C_use=min(C_new,C_previous_use), omitting the second entry on the first cell.
   M2 proves any previous left bound remains valid at later drift, so this is
   safe and forces non-increasing stored C. This is NOT an assumption about
   monotonicity of two-sided E[tau].
4. a_up=ceil(upper(2*phi(0))*2^60)/2^60, computed at 192 bits once.
   Define nominal step parameter s=1/(4*a_up*C_use). It is never called the
   actual Taylor radius. Integer advance=floor(2*s*Q). STOP if advance<1;
   no forced one-grid-unit widening is permitted.
5. right=min(left+advance/Q,exact_splice). e0=(left+right)/2;
   rho=(right-left)/2=max(|left-e0|,|right-e0|). Thus rho<=s and
   rho<=1/(4*a_true*C_use); all cell points are within the declared radius.
6. CUSUM terminal 11/2 is rational. SR terminal is not rational: retain it as
   the symbolic constant c_SR, not a decimal or its inward rounding. Only the
   last SR right endpoint, midpoint and radius contain c_SR. For exact ordering,
   192-bit outward evaluation must give the same floor(Q*c_SR) from both ends;
   otherwise STOP without precision adaptation. A proposed rational endpoint
   past that floor clips to c_SR. Each exact expression is encoded as [p,s],
   meaning p+s*c_SR, with reduced rational strings. Ordinary midpoint
   denominators divide 2Q. The final SR exception is explicit, not hidden.
7. Set left=right and repeat until the exact splice. Shared boundary equality
   is exact; interiors are disjoint; no gaps, overlaps, adaptive splitting or
   result-dependent cell changes. SR symbolic quantities must be outward
   evaluated at 256 production bits while preserving their exact identity.

Canonical encoding: ASCII JSON, sorted keys, comma/colon compact separators,
exact rational strings, no floats/timestamps, one final LF. config/cover_witnesses.json
stores every left-location bound, raw Arb ball, t_star, directed quantization
and transport witness. Independent integer and Fraction implementations replay
these bound witnesses to byte-identical cells. Recomputing minorants uses the
pinned implementation/runtime and exact quantization; no float-only C is binding.

NEW_EXECUTABLE_COVER_COUNT: CUSUM=326, SR=316, total=642.
CUSUM is the conservative walk, without forcing 323. For SR, this successor
explicitly chooses the existing DIRECT bound at every actual left endpoint.
The older 322-cell walk used the earlier point of a 200-drift grid as an envelope.
Both bounds are justified by M2; using the direct bound at the actual left is
conservative on that entire cell too. This prospectively specified replacement
is justified by the same proof and common exact rule, not by a target count or
observed production outcome. The 316 does not narrow drift or detector scope.
The exact new SR terminal avoids the prior floating-point endpoint ambiguity.

The s rule is a geometry bound, NOT a proof that B_cover will pass. In particular,
the old R1 bootstrap condition C(2 a rho+b2 rho^2)<=1/2 does not follow from
rho<=1/(4aC) alone. This successor does not invoke that bootstrap: its required
curvature certificate bounds the differentiated raw equations uniformly over
the cell. No unproved closure inequality is smuggled into the new ledger.

## Formal disposition of historical counts

FROZEN_323_MEANING = EXECUTABLE_COVER_COUNT in the old binding manifest: that
field and its 323*19 work invariant were binding, even though inconsistent
with the declared greedy rule. Its cited R1 COST PROVENANCE is a continuum cost
estimate (historical analysis gives integral 2aC approximately 322.49, ceil 323).
The approximation is not an executable cover or a certified exact integral.
We do not retroactively downgrade the binding field to an optional estimate.

OLD_12255_WORK_UNIVERSE_STATUS = SUPERSEDED_BY_SUCCESSOR.
The old 323/322/12255 facts remain byte-identical historical facts. For this
successor only, the canonical table defines the new work universe. No resume
record or prior PASS is silently carried across the checkpoint boundary.

## Binding enclosure, ledger and all-m mathematics

[ERROR_ALGEBRA.md](ERROR_ALGEBRA.md) is normative, hash-bound with this document
and config/checkpoint.json. It gives the complete residual identities, source
and finite-power recurrences through order two, the derivation of derivative
and curvature uncertainty, all-m correspondence, channel ownership and gates.

    epsF_r = C*(deltaF_r+epsS_r)
    epsD_r = C*(deltaD_r+k1*epsF_r+epsS1_r)
    R(cell) subset R_interval+(cell-e0)*D_interval
                   +[-rho^2*M_R2/2,+rho^2*M_R2/2]
    B_cover_usage = outward_upper(rho*mag(D_interval)+rho^2*M_R2/2).

D_interval includes the dF defect, K'F uncertainty, derivative sources, finite
kernel powers, all-m assembly and arithmetic. M_R2 is the uniform-cell
curvature bound, not S_2 and not K3's second moment. No separate rho*epsD is
charged. The explanatory nominal/uncertainty breakdown is not a second debit.
R_interval likewise includes its value uncertainty once.

Top-level caps stay B_cover=.050, B_candidate=.040, B_kernel=.040,
B_other=.040, B_rounding=.010, B_interval=.010; B_resolvent=0;
reserve=.010 is nondrawable. B_other has zero authorized usage under this exact
assembly; it is locked, not redistributed. LOCAL_GATE_BUDGET=.100 and its .100/C and .100/(C*n_panels) gates remain.
The nested B_candidate partition,
including B_end=.004 and unavailable .002 reserve, remains and has explicit
local and all-m gates. B_end is not an additional top-level budget.
The .050 covers nominal drift variation AND Taylor-model uncertainty as its
parent description states. Numerical sufficiency is NOT_ESTABLISHED.

No float output is an interval certificate. Every source, state domain,
derivative order, propagation edge, norm and enclosure must be persisted in
config/record_schema.json's record contract. Raw-kernel `assemble()` and the
old driver's `R_prime_enclosure` float field do not meet it. The old driver is
not modified. There is no production driver in this namespace.

## Work universe, sharding, resumption and cost

The original 19 function objects are still required on every cell. Add explicit
work identities for the dependencies the old list did not discharge:

| work kind | per cell | scope |
|---|---:|---|
| object | 19 | h1..h4, S0..S4, F0..F4, dF0..dF4 |
| dependency_bundle | 1 | certified h/S derivatives and finite kernel powers, orders 0 and 1, union of all m |
| curvature | 4 | one per m: uniform-cell source/resolvent/power order-2 certificates and M_R2 |
| assembly | 4 | certified R, D, Taylor, top/nested ledgers, one per m |

Add two detector far-field certificates. Base object units=19*642=12198.
Total governed units=(19+1+4+4)*642+2=17978. A bundle is an exhaustive named
certificate obligation, NOT a claim of equal runtime to one old object. Its
internal work and CPU must be recorded; sharing requires hash-linked completed
dependencies. The curvature m=5 unit owns the shared uniform-cell jets for r=0..4 once;
curvature m=1,2,3 units only assemble their bounds from those hash-linked inputs.
The dependency graph in code/algebra.py fixes h-to-S-to-F edges, the source
derivative bundle before dF, shared curvature before its consumers and all
required certificates before assembly. Integer identity order is not a license
to execute before dependencies. Cross-shard dependencies wait for completed
records and do not trigger duplicate solves. Global adjudication/integrity work is mandatory and timed in the
CPU ledger even though it is not a detector-cell certificate unit.

Order and identity are generated by code/algebra.py::work_ids. For S workers,
shard k receives [floor(k*N/S),floor((k+1)*N/S)), never ceil boundaries. No
omission, duplication or implicit missing-record PASS. Worker ceiling stays 64;
new bundle memory must fit the inherited worker/cache limits before production.

Resume identity includes new checkpoint hash, exact cell-table hash, backend
hash, detector, cell index, unit kind, function/m, exact e0/rho and dependency
hashes. Old records are evidence only; they cannot satisfy new coverage.
Shared certificates must be included by explicit hash links, not repeated work
or unrecorded external caches. Cache construction remains inside the cost model.

Base-object cost reuses the parent measured primitives with actual counts and
recomputes cache amortization: t_panel=t_shared/(19*N_SR)+t_drift/19+t_perfn.
It does not scale away fixed shared-cache construction. Corrected base-only
CPU-h: central 612.810; conservative 740.462; worst plausible 887.135.
These EXCLUDE unmeasured additional dependency/curvature/interval assembly work.
The nominal remaining worst-band headroom is 238.865 CPU-h, not a budget grant
or proof that the missing work fits. config/cost_model.json contains full inputs.

HARD_CPU_CAP=1126 retained as an absolute, non-increasable ceiling.
CPU_CAP_ADEQUACY=NOT_ESTABLISHED. A full model including new kernels, interval-e
work, cache creation, memory constraints and verification must be measured and
qualified before production. If it cannot fit, a separate governed cap successor
is required. No full cost number is invented and no scientific failure follows
from a cost failure. Preserve 1848 as the historical older campaign cap only.

## Representative checks, tests and freeze discipline

[diagnostics/REPRESENTATIVES.md](diagnostics/REPRESENTATIVES.md) and its JSON
report actual cells containing 0,1/10,1/4,1,27/5,11/2, for every m. New float
collocation probes run only at those six cell midpoints. They report nominal
point estimates; R/D interval widths, derivative uncertainty, curvature,
complete B_cover utilization and other certified gates are NOT_COMPUTED /
IMPLEMENTATION_DEPENDENCY. No prior anchor-point defect is transplanted onto a
different midpoint. No full-cover function certification or production ran.

Focused tests independently replay geometry, verify exact tiling/radius and
conservative quantization, exercise exact all-m interval algebra and derivative
propagation, reject double counting, check floor sharding, preserve budget
ownership, verify checkpoint/parent hashes and protected files, and require the
production guard OFF. Test arithmetic is not a scientific qualification.

Run from repository root:

    PYTHONDONTWRITEBYTECODE=1 rebaseguard-proof/.venv/bin/python -m unittest discover -s level4/closure_proofs/p5y_k1_cover_ledger_successor/tests -v
    PYTHONDONTWRITEBYTECODE=1 rebaseguard-proof/.venv/bin/python level4/closure_proofs/p5y_k1_cover_ledger_successor/code/audit.py

adjudication/REVIEW.json is produced by a separate read-only self-adjudication
program, not represented as an independent human or subagent review. The freeze
manifest hashes every namespace file except itself; the single adding commit
anchors the manifest. CHECKPOINT.md cannot contain its own hash; file hashes
below cover the machine configuration and normative dependencies without a
circular hash, and manifests/freeze.json covers this document as well.

After commit no frozen file may change. Implementations may consume these
immutable contracts in a NEW implementation namespace. Qualification must
establish the full derivative/source/curvature/assembly requirements, preserve
the exact table and ledger, and demonstrate full cost/memory feasibility.
An explicit separate production authorization is then necessary; it must not
flip the guard inside this frozen checkpoint. No implementation work is done
as part of this task beyond the governance reference algebra/tests.

## Self-adjudication and historical state

The specification is unambiguous and freezable with explicit implementation
dependencies. Governance can be complete while numerical qualification is not.
This is option C, not production-ready and not a promise of eventual PASS:

    P5Y_K1_COVER_LEDGER_SUCCESSOR = FROZEN_WITH_IMPLEMENTATION_DEPENDENCIES
    CURVATURE_CERTIFICATE_STATUS = NOT_COMPUTED / IMPLEMENTATION_DEPENDENCY
    ALL_M_ASSEMBLY_STATUS = exact reference algebra tested; scientific interval kernel missing
    REPRESENTATIVE_LEDGER_STATUS = NOT_COMPUTED / IMPLEMENTATION_DEPENDENCY
    CPU_CAP_STATUS = 1126 retained ceiling; complete adequacy NOT_ESTABLISHED
    PRODUCTION_DRIVER_STATUS = OFF; prior driver untouched
    P5_ORIGINAL_VERDICT = PARTIAL
    P5X_FINAL_VERDICT = PARTIAL
    HISTORICAL_K1_VERDICT = K1_INCOMPLETE_BUDGET
    TASK1 = FAIL; TASK1R = PASS
    OLD_OPTIMIZED_SUCCESSOR = FROZEN / NOT_RUN
    SCIENTIFIC_VERDICT_CHANGED = NO
    LEVEL4_GLOBAL_CLOSURE_CHANGED = NO
    LEVEL4_GLOBAL_CLOSURE = NO

EXACT_NEXT_ACTION = Implement and qualify the complete source/derivative,
whole-cell curvature and interval-assembly certificate bundle in a separate
implementation namespace against this immutable checkpoint, measuring full
cost/memory under the retained 1126 CPU-hour ceiling before requesting production.

## Binding artifact SHA-256 hashes

| File | SHA-256 |
|---|---|
| [config/checkpoint.json](config/checkpoint.json) | `1c2a6825f19e19de6fb588647ca3fc4618068087ef0976292ca7bbeca701f13f` |
| [config/cells.json](config/cells.json) | `341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f` |
| [config/cover_witnesses.json](config/cover_witnesses.json) | `dcb89ccc1a15729a0fb2469ce9c28b0891a81dffe112840b2325417cda31f446` |
| [config/cost_model.json](config/cost_model.json) | `2a3ec2171d1d639770b6cca8b131e7947677b7ec89e39da24e7c729f3a8e0d34` |
| [config/record_schema.json](config/record_schema.json) | `666dee60b9ab60203f7582d01e49416c23e75cbacd713655344ff459689038a0` |
| [ERROR_ALGEBRA.md](ERROR_ALGEBRA.md) | `4f32df0273d05b1b4e0136e2a901adec9979e158b5decd8c9bf3cce0e35b9ffa` |
| [manifests/authority.json](manifests/authority.json) | `4ffd0e47d301886646f45884c5c233bf8f42f3ed6dd785d778de3298ed2f523e` |
| [manifests/protected_start.json](manifests/protected_start.json) | `d30f011447df72315e568c279f53fdf8a0d7f152a9720321d26a4f1ae9f40873` |
