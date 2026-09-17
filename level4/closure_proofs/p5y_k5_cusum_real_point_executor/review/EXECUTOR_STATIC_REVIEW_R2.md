# Independent static review of the r2 real point executor

**EXECUTOR_STATIC_REVIEW: FAIL**

One narrow, repairable family of defects — the in-process prelaunch obligation and the supervisor / ledger file
contract. The mathematics, certification, guard, separation, serialization, cost model, mutation coverage and trust
statement all pass.

## Scope and method

Read-only review in the clone `/Users/suzhe/ReBaseGuard-k5r`. No computation on python-flint, the operator, K1 records
or any host; no file modified. HEAD advanced during the review from the source freeze `52769488` to `57b51a6f`
("frozen qualification evidence"); `git diff --name-only 52769488 57b51a6f -- .../code .../config .../*.md` is
**empty**, so `57b51a6f` adds only the `evidence/qualification_r2/*.json` files and the reviewed source bytes are
exactly those of `52769488`. Worktree clean.

Independently recomputed, not taken on trust:
- all **276** entries of `config/EXECUTOR_PINS.json`: 0 missing, 0 mismatched at HEAD;
- `authorization_interface.executor_identity()` over the 10 `IDENTITY_FILES` =
  `2bd98fde6bba1e2252b31c28a108c76b112f9924bd1b94a6f8fd237cc53a50f3`, equal to the protocol's
  `executor_identity_sha256` and to the r2 result;
- `sha256(SCIENCE_PREREGISTRATION_R4.json)` = `9ace6896d70b7a17225c03cd6d8092e3d33089d001dd3e2736894dd866f3780a`,
  equal to the value in the executor spec, the authorization template and the qualification protocol;
- `sha256(QUALIFICATION_RESULT_EXECUTOR.json)` = `884bebe0b6836105df25d64ce1e7d5f9ce12a94fdcb42e801ff3805c9767ab2b`,
  equal to `RUN_COMPLETE.json:result_sha256`; all 14 `part_sha256` entries match their files.

## Q1. Faithful reuse of the frozen R2/R3/R4 mathematics — PASS

The executor composes frozen entry points and adds no mathematics of its own.

- **σ-odd point reduction.** `backends.py:294` builds the cell as `point_core.point_cell(k1_inputs.frozen_cell(0), F(0))`
  — degenerate `{0}`. `graded_dag.py:228` refuses any input that is not `x0_sigma_fixed`, and
  `executor_core.py:270-273` re-checks both `x0_sigma_fixed` and `eta_mid == 0` before the cascade.
  `graded_real.py:194` is what sets `eta_mid = |e0| = 0` for the point cell.
- **Certificates.** `backends.py:296-303` loads `C_o0`, `C_e0` only through `constants_r4.load_certificates()`, which
  re-hashes the registry (`a645a157…`) and each artifact and has no fallback (`constants_r4.py:31-47`).
  `C_o0 = 5.360144767926632` (R4 exact odd-block reduction), `C_e0 = 469.76966683433835` (R3), both exact rationals.
  `C_point = C_hull = C_upper` of frozen cell 0.
- **Graded wiring.** `executor_core.py:285` calls `G.certify_graded(stages["inputs"], parity=True)` unchanged; the
  inputs come from `graded_real.graded_inputs(cert, residuals, left=0, right=0, certificates={C_o0, C_e0})`
  (`backends.py:310-311`).
- **He6/j5.** `backends.py:329-332` uses `hermite6_ext.norm_table(0, x1)` (which extends the frozen orders 0–4 with
  `k5, k6, j5, j6`, `hermite6_ext.py:202-209`) and `sup_S0_on(n, 0, x1)` for n ≤ 6, with `eta = x1`. The `h1` omission
  on the real path (present only in the manufactured base, `backends.py:142`) is correct: the point run has no `h1`
  hull term.
- **Local exact-parity M5 tower.** `executor_core.py:286` calls
  `LR.local_tower(base, candidates, out0["mid"]["nodes"], x1=R1E.exact(x1))` with no `start_anchors` and default
  `iterations`; `local_r5.py:36` fixes `ITERATIONS = 12` (trace length 13) and `local_r5.py:78-79` refuses any anchor
  of order > 3. `M5 = r5_majorant.m5(tower, parity=True)` takes only the even component
  (`r5_majorant.py:103-111`), the R3 semantics at the σ-fixed `x0`.
- **Exact transport.** `executor_core.py:288, 294`: `tf = x1*x1/2`, `L1 = L0 - tf*M5`, `U1 = U0 + tf*M5`, all on
  `Fraction`. When `x1` is the preregistered one, `executor_core.py:337-339` additionally requires equality with
  `probe_rules.transport`, which itself refuses a non-preregistered `x1` (`probe_rules.py:59-70`).
- **Preregistered executor parameters** (`executor_binding.amendment.executor_parameters_bound_here`, which no
  amendment may change) are all honoured: Q06 via `constants_r4.load_certificates`; Q08 relative `2^-200`
  (`synthetic_real.scalar_equivalence:262` `tol = F(1, 2**200)`); Q09 12 `local_r5` iterations; 256 bits; CPU ceilings.

Informational, not a defect: `certify_graded` opens its **own** precision context at its default
`bits = rung3_engine.PRODUCTION_BITS` (`graded_dag.py:223-224`), and the executor calls it without passing `bits`
(`executor_core.py:285`, `backends.py:169-170`). `PRODUCTION_BITS = 256` (`rung3_engine.py:59`), the frozen ladder is
the single rung `[256]` with `escalation_allowed: false`, and `validate_context` refuses any other precision
(`executor_core.py:170-171`), so the coupling is currently exact. It is a latent trap only if a future protocol
re-opens the ladder.

## Q2. Genuinely certified sealed objects; refuses rather than degrades — PASS

- **Exact rationals, radius-zero exports.** `L0, U0` come from `graded_dag.py:241-243` as `(lo - rm, hi + rm)` where
  `lo, hi = R1E.ball_fractions(centre)` (exact dyadic endpoints, explicitly precision-independent,
  `rung3_engine.py:102-111`) and `rm = R1E.fraction_of(rad_mid[m])`. `M5 = R1E.fraction_of(loc["M5"][m].abs_upper())`
  (`executor_core.py:293`). `rung3_engine.fraction_of:114-118` **raises**
  `ProducerRefusal("export of a non-exact endpoint")` on any ball with non-zero radius. Every intermediate goes
  through `up() = q(R1E.upper_fraction(v))` (`executor_core.py:65-66`). No float reaches a scientific leaf; the
  consumer re-validates with `_frac`, which rejects any string containing `.` or `e`
  (`qualification_gates.py:27-30`).
- **Certificate chain.** `executor_core.py:467-479` requires `C_point, C_e0, C_o0, C_hull`; the exact leaf key set per
  m; `F:r:3` point nodes for r ∈ 0..4; `F:r:5` tower nodes for r ∈ 0..4; non-empty anchors; and the four addresses —
  otherwise `INCOMPLETE_CERTIFICATE_CHAIN`. `validate_stage_outputs` (`executor_core.py:268-281`) additionally
  requires the 11 graded-input keys, all five `("G", r)` origin values, `k0..k6`, and refuses any candidate of order
  > 3. The r1 finding that the chain check is "presence-only" is now materially answered downstream:
  `qualification_gates.QE11` (`:96-106`) **re-derives** `M5` per m from the sealed `tower_nodes` even components with
  `R1E.coefficients(m)` and requires agreement to `2^-100`, and `QE10` re-checks `e ≤ t, o ≤ t` on every point, anchor
  and tower node.
- **Refusals, not rounding.** The refusal set is complete and fail-closed: `UNBOUND_OR_MALFORMED_INPUT`,
  `K1_IDENTITY_MISMATCH`, `CELL_ENDPOINT_MISMATCH`, `CELL_IDENTITY_MISMATCH`, `M_SET_MISMATCH`, `POINT_MISMATCH`,
  `THEOREM_CELL_MISMATCH`, `UNSUPPORTED_PRECISION`, `PRODUCER_IDENTITY_MISMATCH`, `PROTOCOL_IDENTITY_MISMATCH`,
  `RUNTIME_IDENTITY_MISMATCH`, `RUNTIME_MISMATCH`, `STALE_OUTPUT_NAMESPACE`, `FINALIZED_ADDRESS_EXISTS`,
  `UNAUTHORIZED_REAL_ARITHMETIC`, `INCOMPLETE_CERTIFICATE_CHAIN`, `PRECISION_PROBE_MISMATCH`,
  `TRANSPORT_DISAGREES_WITH_FROZEN_RULE`, `AUX5_GATE_REFUSED`, `PINS_UNAVAILABLE`, `CPU_RLIMIT`, `WALL_TIMEOUT`.
  `refuse_finalized_addresses` (`executor_core.py:204-217`) treats an *unreadable* sealed record as a blocking one.
  17/17 refusal tests pass (`part_refusals.json`).
- **Residual (carried from r1, unchanged).** The precision probe reads back the context it just set
  (`executor_core.py:323-325`). It detects a wrong *requested* precision — mutation E15 (`R1E.precision(128)`) is
  detected — but not a transient nested change inside a stage. The pins and identity cover source mutation, so this is
  acceptable; it is a read-back, not an independent measurement, and no more should be claimed.

## Q3. Preregistration preserved; the executor never interprets a sign — PASS_WITH_NOTES

- **Byte preservation.** `git show --stat 52769488` touches only files under `p5y_k5_cusum_real_point_executor/`.
  `SCIENCE_PREREGISTRATION_R4.json` and `probe_rules.py` were last modified at `852b2d65` (the r4 protocol freeze) and
  are unchanged; `part_fence.json:science_preregistration_unchanged` PASS, and both files are pinned.
- **Separation is structural, not merely stated.** `consumer.py:31-35` computes `PR.producer_qualification(q)` and
  `PR.science_usable(q)` over the sealed `Q01..Q16` and returns `PR.VOID` unless both the frozen rules and the
  structural checks hold (`:36-41`). `qualification_gates.py` may touch only `PR.scientific_address` and
  `PR.load_prereg`, and `qualify_executor.qualification_structure()` (`:269-294`) enforces this by **AST**: it rejects
  any other `PR.*` attribute in `qualification_gates.py`, rejects `import consumer` / `import qualification_gates` in
  `executor_core.py` / `backends.py` / `input_adapters.py`, rejects any verdict-function call in them, and rejects the
  five enclosure/verdict names in `smoke.py`. `part_separation.json:structural` PASS with zero problems. Sign
  invariance is demonstrated on all three verdict classes (`gates_sign_invariant: true` for
  SUPPORTS/INCONCLUSIVE/CONTRADICTS) against the negation map of `qualification_gates.negated`.
- **Note (documentation).** `TRUST_MODEL.md:11` and the authorization template say the science content is "unchanged
  since `dbbd405a`". The file itself changed at `c4716a88`, `38234751` and `852b2d65`. Diffing r1 against r4: the
  hypothesis, scientific object, verdict thresholds, m set, precision ladder and transport rule are unchanged, but
  `scientific_address` went v1 → v2 (dropping `attempt_id`, adding `executor_binding_sha256`), the aggregate label was
  renamed `CUSUM_H3A_REFUTED_FOR_SOME_M` → `CUSUM_H3A_TARGET_REFUTED_FOR_SOME_M`, `consumption_keying` and
  `downstream_disclosure` were added, and the Q16 wording changed. All published pre-result; none loosens a verdict
  threshold. The claim is true in substance and overstated in form — say "science *rules* unchanged; the r4 file
  supersedes r1–r3 with governance and addressing amendments", not "unchanged since dbbd405a".

## Q4. REAL_INPUT_ARITHMETIC_GUARD — PASS

- **Policy DENY, only two recognized policies, everything else denies.** `config/REAL_INPUT_GUARD.json` holds
  `{"policy": "DENY"}`. `executor_core.guard_decision:70-76` treats an unreadable or malformed file as DENY;
  `decide:79-89` returns `real_arithmetic_permitted: False` for `DENY`, for any unrecognized value and for `None`.
  `enforce_guard:92-96` defaults `real_input` to `True` via `getattr(backend, "real_input", True)` — fail-closed for an
  unknown backend.
- **Checked before any backend method.** `executor_core.execute:311` is the first statement of `execute`, before
  `validate_context`, before the attempt log and before any backend call; `tests/test_executor.py:30-34` asserts this
  by AST on the first non-docstring statement.
- **Defence in depth.** `backends.CusumPointBackend.prepare_point:384` re-runs `EC.enforce_guard(self, ctx)` as its own
  first statement (`tests/test_executor.py:60-65` asserts this by AST). Both layers are exercised and both are
  load-bearing: `guard_deny_real_backend_real_binding` covers layer 1 through a `Tripwire` subclass that would raise a
  distinguishable error if reached, and `guard_deny_production_backend_direct` calls `prepare_point(None)` directly to
  cover layer 2 (`qualify_executor.py:187-195`). Mutation **E14** (replacing `enforce_guard` with a bare
  `guard_decision`) is detected.
- **Editing the guard file alone cannot enable it.** Flipping the policy to `EXTERNAL_AUTHORIZATION` moves the decision
  to `authorization_interface.validate`, which requires a countersigned object naming the running executor identity,
  the science sha256, the qualification result sha256, a `PASS*` static review, the K1 record and manifest, the cell,
  the m set, the precision, the CPU ceiling, the host runtime identity, the output namespace, a slot and a ≥32-hex
  nonce, plus a prelaunch report naming that authorization (`authorization_interface.py:63-103`).
  `part_authorization.json` shows the valid synthetic bundle accepted and **all 24 mutated bundles plus the no-bundle
  case refused (26/26)**, with `EC.decide` refusing `ALLOW` / `None` / `DENY` and accepting only
  `EXTERNAL_AUTHORIZATION` with a valid bundle.
- **The adapter leaks nothing.** `RealInputAdapter.bind` (`input_adapters.py:37-55`) runs `k1_inputs.validate`
  (V01–V10) and emits only `kind, detector, k1_cell_index, left, right, C_upper, C_evaluation` and three identity
  hashes, with `redacted: True`; every numeric record payload stays inside the adapter.

**Scope limitation accepted:** the guard is a consistency and accident-prevention mechanism, not a defence against the
host owner (`TRUST_MODEL.md:34-35`). No further on-host anti-tamper machinery is requested.

## Q5. Q01..Q16 evaluated inside the executor as preregistered — PASS_WITH_NOTES (one gate is defective: see D1)

`producer_gates` (`executor_core.py:378-444`) emits exactly the 16 preregistered ids
(`probe_rules.producer_qualification:192-196` refuses any other gate set), and each maps to a real computation:

| gate | where | verdict |
|---|---|---|
| Q01 | `executor_core.py:409-411` (real) / `:417-418` (harness) | **defective, see D1** |
| Q02 | `backends.py:416` — `RealInputAdapter().bind() == ctx.k1_binding`, i.e. V01–V10 re-run at seal | faithful |
| Q03 | `backends.py:414-417` — `left = right = e0 = rho = 0` on the frozen cell **and** `x1 ==` the preregistered `x1`, plus `shared_structure` | faithful |
| Q04 | `backends.py:212-244, 392-394, 411, 418-419` — `manifest_v3.verify()`, producer identity `3692d0fe`, `tcb5.verify_coverage(committed ∪ pins)`, `runtime_identity5.require`, `ScipyGuard.require_clean()`, at both `initial` and `final`; the initial gate *raises* rather than recording False | faithful |
| Q05/Q13 | `executor_core.py:126-136, 402-403` — 276 pinned files hashed at start and at seal, no `None`, live == pinned | faithful |
| Q06 | `backends.py:250-281` — `odd_block_certificate.verify_artifact` and `resolvent_certificate.verify_artifact` must reproduce the stored `certified` block **byte-identically**, with artifact sha256 and loader agreement | faithful |
| Q07 | `executor_core.py:388-395` — exact rationals, `L0 ≤ U0`, `M5 ≥ 0`, `L1 ≤ L0 ≤ U0 ≤ U1`, `tf == x1²/2`, and `(L1,U1)` equal to `PR.transport(..., x1)`; a **real** record must carry the preregistered `x1` | faithful |
| Q08 | `backends.py:334-347` — `synthetic_real.scalar_equivalence` at relative `2^-200` against the frozen midpoint DAG, plus graded radius ≤ scalar radius per m, on the **origin-free** cascade (`radius_only_cascade` strips `origin` and refuses if `out["m"]` is non-empty, `executor_core.py:298-306`), so no centre and no enclosure | faithful |
| Q09 | `executor_core.py:397-399` — trace length 13, `e ≤ t` and `o ≤ t` on all three node tables, anchors only at orders ≤ 3 | faithful |
| Q10 | `backends.py:175-202` — the frozen `aux_propagate.cell_dag` + `propagate.enclosures` + `assembly.assemble` path, compared against committed `RUNG_256` | faithful, intentionally weak (see D6b) |
| Q11 | `executor_core.py:436` | near-tautological (see D6a) |
| Q12 | `executor_core.py:437` + the separate `refuse_finalized_addresses` refusal | faithful, split (see note) |
| Q14 | `executor_core.py:415, 420` | faithful |
| Q15 | `executor_core.py:440` — CPU and wall at seal within the soft ceilings; Q06's 222 s replay is inside the measured window | faithful |
| Q16 | `executor_core.py:412-414` | partial (see D1) |

**Honest mode labels.** `modes` is derived from the evidence dicts (`executor_core.py:443`). The manufactured run
records exactly `{"Q01": "HARNESS_ANALOGUE", "Q02": "MANUFACTURED", "Q03": "MANUFACTURED", "Q04": "HARNESS_ANALOGUE",
"Q06": "MANUFACTURED", "Q08": "MANUFACTURED", "Q10": "NOT_APPLICABLE_MANUFACTURED", "Q14": "HARNESS_ANALOGUE",
"Q16": "HARNESS_ANALOGUE"}` (`part_fixtures.json`). Q10 is set `true` under the `NOT_APPLICABLE_MANUFACTURED` label
(`backends.py:159`) rather than silently claiming a real check — the honest choice, provided the consumer refuses the
label on a real record.

**The consumer does refuse harness labels on a real-kind record.** `qualification_gates.py:60-66` (QE05) computes
`allowed = {"REAL"}` when `binding.kind == "real"` and requires `set(modes.values()) <= allowed`, together with the
full preregistered gate id set and boolean values. `part_separation.json` proves it operationally: a record whose
`binding.kind` is flipped to `"real"` **with the scientific hash recomputed** yields `science_usable: false`, and
flipping a single gate (`Q10`) to false also yields `science_usable: false`.

**Q05 confirmed load-bearing.** `pins_ok` compares the start and seal snapshots *and* both against the pinned values,
so `EXECUTOR_PINS.json` being absent from its own `files` map is covered: the pins file is bound through
`IDENTITY_FILES` and `executor_pins_sha256`.

**Note on Q12.** The gate itself only checks that the four addresses are distinct; "no finalized record exists for any
of them" is enforced as a *refusal* (`executor_core.py:314`) scanning the namespace root, and the git/packet/ledger
half is prelaunch `P09`. The division is coherent and matches `scientific_address.attempts`, but the gate boolean alone
does not attest it.

## Q6. Serialization, determinism, VOID sealing, supervision — PASS

- **Canonical JSON and exact rationals** throughout (`executor_core.py:56-62`); runtime fields (`cpu_seconds`,
  `wall_seconds`, `peak_rss_kib`) live in a `metadata` block excluded from the hash (`:359-362`).
- **Determinism.** Two independent fresh-process runs of all nine fixtures give the identical payload
  `cb28b9727470a6b4287aa412313284b433bd8c16c6c16bd39b948dfa56b1e7e0`, with `scientific_leaf_differences: []` and
  hash-by-hash equality on all nine records. The env is pinned (`PYTHONHASHSEED=0`, four thread variables) by both the
  supervisor (`supervisor.py:55-56`) and `executor_cli.py:20-24`, which additionally refuses to start if `numpy` was
  imported before the thread contract was pinned.
- **Gate evaluation cannot contaminate the leaves.** `scalar_equivalence` mutates `cert.residuals` / `cert.aux`;
  `backends.py:339-344` saves and restores them in a `finally`, and — more importantly — `producer_gate_evidence` is
  called at `executor_core.py:332`, *after* `enclosure_stages` and after `serialize_intermediates`, so every
  scientific value is already fixed.
- **VOID sealing after ARITHMETIC_STARTED.** `executor_core.py:366-375` catches `BaseException`, seals
  `VOID_RECORD_SEALED.json` / `MANUFACTURED_VOID_RECORD_SEALED.json` with the failure and everything computed so far,
  logs `VOID`, and re-raises. `_CpuLimit` (`:236-249`) turns SIGXCPU into `ExecutorRefusal("CPU_RLIMIT")` in the main
  thread; `executor_cli.py:37-38` turns the watchdog's SIGTERM into a refusal inside `execute`. A VOID record blocks
  re-use of its addresses (`void_address_refused` PASS).
- **Atomic sealing.** `seal` (`:482-492`) writes `name + ".tmp"`, `flush`, `fsync`, `os.replace`. `AttemptLog.emit`
  appends and fsyncs each event.
- **Supervision and the frozen failure_class.** `supervisor.py:46-95` sets `RLIMIT_CPU (soft, hard)` in `preexec_fn`
  before exec, polls `os.wait4` for the child's own rusage, sends SIGTERM at the wall limit and SIGKILL 60 s later,
  records boot id before/after, and derives the class **only** via `PR.failure_class(evidence)`
  (`probe_rules.py:164-189`) — never self-declared. The evidence bears it out: `manufactured_success` → `None`, events
  `[VALIDATED, ARITHMETIC_STARTED, SEALED]`; `real_mode_refused_before_arithmetic` → `INTEGRITY_REFUSAL`, no events, no
  seal, and `retry_decision` → `NOT_AN_ATTEMPT_RELAUNCH_AFTER_VERIFIER`; `cpu_limit_seals_void` → `CPU_RLIMIT` with the
  VOID seal; `wall_timeout_seals_void` → `WALL_TIMEOUT` with the VOID seal; `external_kill_classified` →
  `PROCESS_KILLED_BY_EXTERNAL_SIGNAL` with **no** seal (matching `void_after_arithmetic.transient_kills`). Mutation
  **V01** (VOID seal dropped) is detected against a clean wrapper control.
- **Mutation honesty.** `part_mutations.json` runs an unmutated control first (`all_expected: true, failing: []`), and
  a crash counts as **not** detected (`qualify_executor.py:735-738, 84-85`); anchors must match exactly once
  (`:729-730`), also asserted statically in `tests/test_executor.py:53-58, 67-73`. **E 16/16, P 4/4, A 3/3, V 1/1,
  C 1/1.** The four production-stack mutants are detected by the *unmutated* shared checks with specific, non-vacuous
  problems (`constants differ from the R4 registry`; `hull base eta differs from the binding x1`; ten `origin W…`
  mismatches; ten candidate parity violations) — the r1 finding "no mutation touched the production `_CusumStack`
  methods" is closed.

## Q7. Cost credibility and the CRAMER contract — PASS

**Cost.** `projected = (2424.798 + 222.263 + 0.0155 + 0.0054 + 1501.7 + 120) × 1.5 = 6403.17` CPU-s ≤ soft **9000**;
campaign `19209.52` ≤ **32400**; the rlimit hard 10800 and wall 14400 are enforced by the supervisor. The decomposition
is sound, and, contrary to the r1 note, it is **not** double counting:

- `SyntheticGradedCert.prepare_synthetic` (`synthetic_real.py:70-110`) replaces the real candidate construction with
  synthetic Chebyshev payloads; it does the real Arb norm tables, Taylor remainders, closed forms and sharp norms but
  **not** the order-2/Aux3/rung-3 collocation. `Order3Certifier` extends `Aux3Certifier` extends `Order2Certifier`
  (`cusum_order3.py:116`, `aux_certifier.py:77`), so the real `GradedRealCertifier.prepare()` *does* pay that
  collocation. The `committed_collocation_cpu_seconds: 1501.7` term (1160.5 order-2 + 171.2 Aux3 + ~170 rung-3)
  therefore covers exactly what the measured 2424.8 s omits, and the qualification independently re-measured the
  order-2 part at **1155.75 CPU-s** (`part_order2_reference.json`) against the committed 1160.5 — 0.4 % agreement.
- The `enclosure_and_tower_allowance_cpu_seconds: 120` is the only unmeasured term. Q08 ran **two** full
  `certify_graded` passes on the *real* graded inputs in **0.0155 s** total, so the cascade is ~8 ms on real data; the
  12-iteration tower is the same algebraic scale. 120 s is four orders of magnitude of headroom, with `safety_factor:
  1.5` on top.
- Q15 is measured at seal on the real process (`executor_core.py:356`), after the 222 s Q06 replay, so the gate
  measures what the projection projects.

**CRAMER contract.** A sound, fail-closed treatment of a genuine import-time-precision dependency, diagnosed before
the repair (`DEV_CALIBRATION.md:58-73`): `ra_certifier` builds `CRAMER = arb(1086)/arb(1000)` at import time, so its
ball and every downstream remainder, allowance and certificate endpoint depend on the precision of the *first* import;
the frozen C_o0/C_e0 artifacts and the K1 records were generated at python-flint's default 53 bits.

- `backends.py:36-52` states the contract (including the exact ball `mid = 2445454597662179/2251799813685248`,
  `rad = 1/4503599627370496`, sha256 `b472beac…`) and initialises the certificate stack under an explicit
  `workprec(53)` at import.
- `check_cramer_contract()` (`:60-71`) requires `used == reference_53 == recorded contract` on **both** midpoint and
  radius, and is called in `production_gate` (`:219-221`) and at the start **and end** of `certificate_replay`
  (`:253-255, 279-280`). A violated contract makes Q04 fail (and the initial gate raises, `:392-394`) and makes Q06
  return `{"pass": false, "refused": "CRAMER_CONTRACT_VIOLATED"}` **without calling any verifier** — so no sealable
  result can be produced under a violated contract. The replay itself runs each verifier inside `workprec(53)`
  (`:268`), matching the artifacts' production context.
- Empirically fail-closed and precision-independent: a caller at 53 bits and a caller at 256 bits in **fresh
  processes** both give `contract.pass: true` and byte-identical, certified replays of both artifacts; a forced first
  import at 256 bits gives `contract.pass: false`, `replay.refused: CRAMER_CONTRACT_VIOLATED` and `gate.pass: false`;
  mutant **C01** (first import at 256) is detected (`part_cramer_contract.json`).

The residual assumption — that 53-bit construction is the correct inherited contract — is stated as inherited from the
artifact and K1 generation context, not proved. That is the right framing: a compatibility contract, not a theorem.

## Q8. Trust model honesty — PASS

`TRUST_MODEL.md` is the strongest document in the namespace. It separates five stages, names what each trusts and what
it does **not** establish, and states plainly that git commits are unsigned, that the on-host verifier and guard are
"consistency and fail-closed mechanisms against accidents, not trust roots", that an operator controlling the host can
bypass them, and that the principal residual risk — an operator running the real backend outside an authorized slot or
suppressing an output — "is stated, not engineered away" (`:14, 22-24, 30-35`). `authorization_interface.py:9-12`
repeats that `validate` "authenticates no one". `tests/test_executor.py:96-99` asserts the no-cryptographic-authority
language is present. Two claims verified independently:

- **`config/REAL_INPUT_GUARD.json` is outside the executor identity and the pins — HOLDS.** It is absent from
  `authorization_interface.IDENTITY_FILES` (`:26-28`) and from all 276 entries of `EXECUTOR_PINS.json` (checked
  programmatically: zero matches), whose `rule` string says so explicitly;
  `make_protocol_executor.executor_pins():132-145` never adds it; `tests/test_executor.py:75-80` and
  `qualify_executor.py:464-468` both assert it, and the latter PASSes in the frozen evidence. Activation therefore does
  not change `executor_identity_sha256 = 2bd98fde…`, which is what the countersigned authorization names and what
  `validate` re-computes live.
- **One nuance the countersigner must be told.** The guard file *is* listed in the frozen qualification protocol's
  `executor_sources_sha256` (via `make_protocol_executor.QUALIFICATION_SOURCES:16-18`), which `part_fence`
  (`qualify_executor.py:687-689`) and `cmd_check` (`:893-894`) check byte-for-byte. So after activation, re-running
  `qualify_executor.py check` will report that **one** file as drifted, while the identity and the pins are untouched.
  This is not a contradiction of the claim, but it should be documented so nobody reads that expected drift as
  tampering.

## Verification of the three specific claims

1. **`REAL_INPUT_GUARD.json` outside identity and pins → HOLDS** (recomputed; see Q8).
2. **The `require/check_cramer_contract` typo is non-functional and recorded → HOLDS.** The string occurs exactly once,
   in a comment at `backends.py:35`. No identifier `require_cramer_contract` exists anywhere in `code/`; the real
   function `check_cramer_contract()` is defined at `:60` and called at `:219`, `:253`, `:279` (and by the
   qualification at `qualify_executor.py:506, 511`), all exercised. `DEV_CALIBRATION.md:78-83` records it and explains
   that the file is pinned, so it is documented rather than edited. Zero effect on execution or certification.
3. **The r2 evidence → HOLDS in full.** `EG01..EG17` all PASS (**17/17**),
   `REAL_POINT_EXECUTOR = QUALIFIED_AWAITING_EXTERNAL_AUTHORIZATION`, `mutations 16/16`, `production_mutations 4/4`,
   `authorization_mutations 3/3`, `void_mutations 1/1`, `cramer C01 detected 1/1`, `replay_payload_sha256` identical
   twice (`cb28b972…`), `scientific_leaf_differences: []`, `runner_failures: []`,
   `REAL_INPUT_ARITHMETIC_GUARD: DENY`, `EXECUTION_AUTHORIZED: false`, `REAL_CELL_EXECUTED: NO`. Internally
   consistent: all 14 `part_sha256` match, `RUN_COMPLETE.result_sha256` matches the result bytes, every part's
   `runtime` matches the frozen host contract (`rebaseguard-vultr-02`, python 3.12.3, python-flint 0.9.0, glibc
   2.41-12+deb13u4, `libc_sha256 9792e3cb…`), and every part's `protocol_sha256` matches. Truth containment: 0
   violations across all nine fixtures; M5/truth ratios 4.76–1669.4 within the calibrated limits; the independent acb
   Cauchy cross-check passes on all four cross-check fixtures with no enclosure disagreements. No file anywhere in the
   repository is named `SCIENTIFIC_RECORD_SEALED.json` or `VOID_RECORD_SEALED.json`, satisfying that executor
   obligation.

## Defects, by severity

### D1 — Q01 and the in-process prelaunch obligation. LOAD-BEARING for a real run. This is the FAIL.

The frozen preregistration obliges, in `executor_binding.amendment.executor_obligations` (item 3):

> "the executor calls `prelaunch_verify.verify` with its defaults only and refuses in-process unless the result is
> LAUNCH_PERMITTED for the same HEAD and authorization"

and `trust_model` repeats "The executor must call the verifier with its defaults only."

The r2 executor never calls it. `executor_core.py:179-180` imports `prelaunch_verify` solely for `live_host_facts()`.
Instead, real-mode Q01 (`executor_core.py:409-411`) accepts an operator-supplied dict from the bundle and checks only
three things: `rep["verdict"] == "LAUNCH_PERMITTED"`, `rep["authorization_sha256"] == decision["authorization_sha256"]`,
and `rep["utc_epoch"] <= ARITHMETIC_STARTED`. Nothing checks the report's schema, its `head`, its `failing_checks`, or
its `science_sha256` — all of which a genuine report carries (`prelaunch_verify.py:515-540`).

Worse, **the hash Q01 demands cannot be produced by the frozen verifier**:
- `decision["authorization_sha256"] = _sha(canonical(bundle["authorization"]))` — the compact-canonical sha256 of the
  executor's own countersigned object (`authorization_interface.py:55`).
- A real `prelaunch-report.v4` carries `authorization_sha256 = sha(Path(auth_path).read_bytes())` — the **file bytes**
  of the *protocol's* authorization (default `protocol/AUTHORIZATION_TEMPLATE_R4.json`, `prelaunch_verify.py:63`), a
  different object with a different schema.
- The verifier cannot simply be pointed at the executor's object either: `check_P02` requires the authorization to
  equal the committed r4 template in every non-activation field with **no extra keys**, which
  `EXTERNAL_AUTHORIZATION_TEMPLATE.json` (own schema, `nonce`, `countersigner`, `attempt_slot`, `output_namespace`,
  `result_blind`) cannot satisfy.

So as frozen, Q01 is satisfiable only by a hand-assembled artifact that is not a `prelaunch_verify` output — which is
precisely what the obligation forbids. And that obligation cannot be amended away: `allowed_keys` governs the keys of
the *amendment file*, not the preregistration, so the obligation is frozen prereg text;
`executor_parameters_bound_here` states that infeasibility voids the preregistration in favour of a successor
**before** authorization.

This is a fidelity defect, not an anti-tamper request. The repair is small and local: have `executor_core` call
`PV.verify()` with its defaults in-process before `ARITHMETIC_STARTED`, require `verdict == "LAUNCH_PERMITTED"`,
`failing_checks == []`, `schema == "…prelaunch-report.v4"`, `head == <current HEAD>` and
`science_sha256 == ctx.protocol_sha256`, and bind the executor's own countersigned object as a **second**,
separately-hashed requirement rather than overloading the report's `authorization_sha256` field. Q16's git-ordering
half (`PROTOCOL_FREEZE_COMMIT < amendment < AUTHORIZATION_COMMIT`), which the executor currently reduces to a UTC
comparison, is covered for free once `P04` is actually run in-process.

### D2 — the `completion_semantics` file contract is not met. LOAD-BEARING for a real campaign.

The preregistration fixes the contents of the supervisor's marker files. Comparing with `supervisor.py:62-63, 91-94`:

| file | preregistered | actual | missing |
|---|---|---|---|
| `RUN_STATE.json` | pid, argv, boot id, start epoch, **authorization sha256** | `child_pid, supervisor_pid, boot_id, started_unix, cpu_soft, cpu_hard, wall` | `argv`, authorization sha256 |
| `RUN_COMPLETE.json` | pid, **sealed record sha256**, qualification gates | `evidence, sealed_files, events, arithmetic_started, failure_class, refusal` | pid, sealed record sha256, gates |
| `RUN_FAILED.json` | pid, arithmetic_started, supervisor_evidence, traceback without numbers | same object as above | pid, traceback |

This matters because the ledger **governs** the host files: prelaunch `P09` looks for a ledger `OUTCOME` with a
non-null `sealed_record_sha256`, and `P11` requires `RUN_FAILED.json`'s sha256 and its `arithmetic_started` / derived
class to agree with the `OUTCOME`. The pieces `P11` needs are present; the sealed-record sha256 that `P09` and the
`OUTCOME` need is not emitted, and the prereg `waiter` wants `argv` for exact `/proc/<pid>/cmdline` comparison. All
easily added; no science is affected.

### D3 — no supervisor reboot-recovery mode. LOAD-BEARING for a real campaign.

Obligation item 2: "after a host reboot the supervisor's recovery mode writes `RUN_FAILED.json` with `boot_id_changed`
evidence for the interrupted slot." `supervisor.py` compares boot ids within a single live run (`:33-37, 85`) and
`probe_rules.failure_class:172-173` routes `boot_id_changed` to `HOST_REBOOT_OR_BOOT_ID_CHANGE` (a *transient* class,
so a retry hinges on it), but there is no recovery entry point: if the host reboots, the supervisor process is gone and
no marker is ever written for that slot. The one transient class most likely to need a retry is the one with no
mechanism to record it.

### D4 — the r2 evidence has no `RUN_PROVENANCE.json`. MEDIUM; partly compensated.

`evidence/qualification/RUN_PROVENANCE.json` (r1) recorded
`{commit: 8ffcfaff…, porcelain_lines_before_run: 0, host, started_utc, venv}`. `evidence/qualification_r2/` has no
equivalent, so the run's commit and worktree cleanliness are not recorded in the evidence a countersigner reads — yet
`authorization_interface.py:72-74` obliges them to name a `qualification_commit` and a `qualification_result_sha256`.
Compensating: `part_fence` re-verified `pins_sha256`, `executor_sources_sha256` and all 276 pins at run time against
values that live in the freeze commit, so the run provably used the freeze-commit bytes for every identity and pinned
file. What is unrecorded is the state of *unpinned* files and the commit label itself. Add the provenance file before
authorization.

### D5 — `README.md:30` references a non-existent `RESULT.md`. LOW, not load-bearing.

### D6 — two weak gates, both honest about it. LOW, not load-bearing.

(a) Q11 as implemented is `canonical(s) == canonical(json.loads(canonical(s)))` (`executor_core.py:436`) — a JSON
round-trip that is true for essentially any serializable payload. The substantive content of the preregistered Q11
("per-m scientific hash recomputes") lives in the consumer's `QE12` (`qualification_gates.py:107`) and its replay half
is stage 5. The gate is not wrong, but it carries almost no information; say so rather than counting it as a check.

(b) Q10 requires only **intersection** with `RUNG_256`, not equality (`backends.py:191-202`), which is why a
relabelled-m mutant survives and the comparator mutant had to flip the sign of R′ instead
(`DEV_CALIBRATION.md:56-57`). That is exactly what the preregistration specifies, and the frozen evidence in fact
reports `identical_to_reference: true` — so the stronger property held on this run without being demanded. Recording
`identical_to_reference` alongside the pass is the right compromise.

### D7 — gate evidence sits outside the scientific hash. LOW, not load-bearing.

The gate **booleans** and **modes** are inside `scientific` and therefore hashed (`executor_core.py:358-359`), but
`producer_qualification_evidence` — including the Q04 manifest/identity/TCB detail and the Q06 replay detail — lives in
the unhashed `metadata` block (`:362`). Runtime fields must be excluded, but the non-runtime gate evidence arguably
belongs under the hash. Relatedly, `QE05` constrains mode *values* but not that each real-mode gate carries a mode
label, so a record with a single `"REAL"` mode entry and the rest stripped would pass that predicate. Both matter only
against a tampering operator, who is explicitly outside the trust boundary, and stage-5 adjudication re-derives from
the published record.

### D8 — `seal()` and `AttemptLog.emit` fsync the file but not the containing directory. LOW, not load-bearing.

`executor_core.py:483-491, 229-233`. Content is durable and the rename is atomic within the filesystem, but the
directory entry is not durability-fenced against a power loss between `os.replace` and the next directory sync.
`completion_semantics` asks for "tmp + fsync + rename", which is literally satisfied.

### D9 — refusal strings are not mechanically guaranteed number-free. LOW, not load-bearing.

`retry_policy.rules` says "The executor must not print, log or persist any endpoint, sign or majorant outside the
sealed record", and `ATTEMPT_LOG.jsonl` is specified as "gate events only (no endpoint, sign or majorant)". Every
refusal path traced emits identifiers only (node names, hashes, key names, `observed 128`), but
`executor_cli.py:81` prints `str(exc)[:400]` to stderr, the supervisor persists it in `RUN_FAILED.refusal` and
`child_stderr.log`, and `executor_core.py:374` logs `failure[:120]` to the attempt log. An unexpected exception from a
lower layer could in principle carry a value. A whitelist of refusal codes, or stripping digits from the logged string,
would close it cheaply.

### D10 / D11 / D12 — informational, recorded above.

D10: `certify_graded` runs at `PRODUCTION_BITS`, not `ctx.precision_bits` (harmless while the ladder is the single
frozen rung 256). D11: `TRUST_MODEL.md:11` "science content unchanged since `dbbd405a`" overstates byte-level
constancy, and the guard file's presence in `executor_sources_sha256` means an expected post-activation fence drift on
exactly one file. D12: `DEV_CALIBRATION.md:85-89` reports 6413.9 / 19241.7 / 2433.0 / 221.2 from a DEV run, while the
committed evidence reports 6403.17 / 19209.52 / 2424.80 / 222.26; label these as two different runs so no reader
mistakes the DEV numbers for the evidence.

## Scope limitations accepted

1. **The local host is not an independent trust root.** Stated in `TRUST_MODEL.md:14, 30-35` and in the guard file's
   own `rule` string. Accepted as-is, with **no** recommendation for further on-host anti-tamper machinery, verifier
   hardening against the host owner, or another local patch loop. The residual risk — an operator who runs the real
   backend outside an authorized slot or suppresses an output — is correctly declared rather than engineered away.
2. **The real Q01/Q14/Q16 real-mode branch and `CusumPointBackend.producer_gate_evidence` as an assembly are never
   executed end-to-end.** They cannot be, under a DENY guard. The components are exercised on the real stack by the
   smoke (Q04 both stages with ScipyGuard, Q06 replay, Q08 origin-free scalar/radius equivalence, Q10 path, the
   shared-method checks and P01–P04), and the assembly is reviewed statically only. That is the strongest available
   evidence short of authorization, and `EG13` should be read as exactly that rather than as a real-mode
   demonstration.
3. **Reviews are not proofs** (`TRUST_MODEL.md:27-28`). This review read code and evidence; it re-hashed files and
   re-derived identities, but it ran no certifier, no operator and no host check.
4. **Arb correctness** and the inherited 53-bit CRAMER construction are assumptions, both explicitly stated.
5. **The order-2 re-derivation in `smoke.order2_reference()` touches real inputs.** It builds a fresh
   `Order2Certifier` on the frozen cell 0 and recomputes R(0), R′(0) at a cost of 1155.75 CPU-s, outside `execute` and
   therefore outside the guard (`smoke.py:143-167`). Accepted: those two quantities are exactly the ones already
   published by the 84aaa6a5 point certificate, the run reproduced them **identically**
   (`identical_to_reference: true`), and no order-3 or order-5 object is formed. It is worth stating explicitly in
   `EXECUTOR_SPEC_R2.md` R2-4 that this path performs real order-2 arithmetic on already-published values without
   passing through the guard, so that a later reader does not discover it as a surprise.

## Disposition

The science is right and the engineering around it is, with the exceptions above, careful and honestly documented. All
six r1 required repairs are genuinely delivered: the Aux5 final gate and SciPy guard are real and exercised; Q01–Q16
are evaluated inside the executor and sealed with honest mode labels; the consumer applies
`probe_rules.producer_qualification` / `science_usable` and the old QE05 is gone; ARITHMETIC_STARTED, in-process
authorization validation, VOID sealing and SIGXCPU handling all work and are mutation-tested; activation changes only
the guard policy file plus a published countersigned object, with the identity provably unchanged; and the production
`_CusumStack` methods now carry four load-bearing mutants.

What blocks a PASS is D1: a frozen executor obligation that is not implemented, expressed through a gate (Q01) that as
written cannot be satisfied by the frozen verifier's own report — and, per `executor_parameters_bound_here`, an
obligation that may not be amended away. D2 and D3 are in the same governance family and are needed before any real
campaign can be run against the ledger discipline the preregistration assumes. None of these touch the mathematics,
the certification, the guard or the trust statement, and all are small, local repairs. An r3 addressing D1–D4 should be
reviewable quickly and, on the evidence here, should pass.
