# Real point executor: specification (written before implementation)

**Objective.** BUILD_AND_QUALIFY_REAL_POINT_EXECUTOR repairs blocker E of the first real-probe protocol: no executor
implemented the frozen scientific computation.

**Non-scientific, additive.**
- No real K1 cell is executed, and no real `R'''`, `R⁽⁵⁾`, `L1` or `U1` is formed or observed.
- `EXECUTION_AUTHORIZED` stays `false`.
- Blocker G (a local verifier cannot authenticate authorization against the host owner) is **not** addressed by local
  anti-tamper code. See `TRUST_MODEL.md`.

**Frozen inputs this executor must implement, unchanged:**
- **Science preregistration:** `p5y_k5_cusum_first_real_probe_protocol/protocol/SCIENCE_PREREGISTRATION_R4.json`
  (sha256 `9ace6896…`; science content frozen since `dbbd405a`).
- **R4 producer:** freeze `0a7ce2fd`, qualification `dcca5c46`, QUALIFIED_FOR_GOVERNED_REAL_CELL_QUALIFICATION.

## 1. Interface

`executor_core.execute(backend, context) -> SealedRecord`.

### Context (all mandatory, validated before anything else)

| field | rule |
|---|---|
| `k1_binding` | produced only by an input adapter: record sha256, export manifest sha256, cells.json entry, detector CUSUM, k1 cell index 0, left `0/1`, right `5083/10000000`, `C_upper` (exact), `C_evaluation` 0 |
| `m_set` | exactly `[1, 2, 3, 5]` |
| `point_e` | exactly `0/1` |
| `theorem_cell` | `C_1` with `x1 = right` |
| `precision_bits` | exactly `256` |
| `producer_identity_sha256` | equals the preregistration's `producer_identity_sha256` (R4) |
| `protocol_sha256` | equals sha256 of `SCIENCE_PREREGISTRATION_R4.json` |
| `runtime_identity_sha256` | equals the preregistration's `host_runtime_identity_sha256`; the live host must match when `backend.real_input` |
| `output_dir` | must not exist, or be empty |

### Output per m (exact rationals as strings; no floats in scientific leaves)

| leaf | definition |
|---|---|
| `I0 = [L0, U0]` | certified enclosure of `R'''_m(0)`: graded point cascade (R2 `graded_dag.certify_graded`, parity mode) at the degenerate cell {0} |
| `M5` | certified absolute majorant `≥ sup_[0,x1] |R_m⁽⁵⁾|`: R4 `local_r5.local_tower` on the hull `[0, x1]`, anchored by the point candidates' graded suprema and graded point errors, 12 iterations |
| `transport_factor` | `x1²/2`, exact |
| `L1` | `L0 − transport_factor · M5` |
| `U1` | `U0 + transport_factor · M5` |

**Load-bearing intermediates** (also sealed):
- the certified constants used: `C` (`C_upper`), `C_e0`, `C_o0`, with the certificate artifact sha256;
- the hull norm uppers `k0..k6` and `j0..j6`;
- `sup|S_0⁽ⁿ⁾|`, n ≤ 6;
- every graded point node `(e, o, t)` upper;
- every local anchor and tower node `(e, o, t)` upper;
- the M5 iteration trace;
- the resolvent mode;
- the observed working precision.

**Scientific payload and hash.**
- The payload is canonical JSON (`sort_keys`, separators `(',', ':')`, `ensure_ascii`) of `{binding identities, per-m
  leaves, intermediates}`. Its hash is sha256.
- A per-m scientific address is computed with the frozen `probe_rules.scientific_address`.
- Runtime fields (CPU, wall, RSS, timestamps) live in a separate `metadata` block, excluded from every hash.

**The executor never interprets signs.** Verdicts are computed only by the separate frozen consumer
(`consumer.py` → protocol `probe_rules`). Qualification gates live in `qualification_gates.py`, which must not import
any verdict function and must be invariant under negating every endpoint.

## 2. Pipeline (reuse of R2/R3/R4, no new mathematics)

| step | production backend `CusumPointBackend` (real, guarded) | qualification backend `ManufacturedPointBackend` |
|---|---|---|
| **cell** | frozen `point_core.point_cell(cells.json[CUSUM 0], 0)`: degenerate {0}, `C_upper` of cell 0 | σ-system `GradedRig(sysm, 0, 0)` |
| **prepare** | R3 `GradedRealCertifier(point_cell, 256).prepare()`: Aux3 prepare + R1 rung-3 candidates | exact manufactured candidates plus noise |
| **residuals** | R3 `all_residuals_for_graded` (frozen residuals + Repair1 + Aux3 + R1 G) | rig residuals (R2) |
| **graded inputs** | R3 `graded_inputs(cert, residuals, left=0, right=0, certificates=constants_r4)` | `GradedRig.engine_inputs()` |
| **constants** | `constants_r4.load_certificates()` (C_o0 5.3601 R4, C_e0 469.7697 R3) | exact σ-block resolvents of the system |
| **point cascade** | `graded_dag.certify_graded(inputs, parity=True)` | same call |
| **candidate graded sups** | `graded_real.graded_sup(cert, key)` for nodes of order ≤ 3 | `sigma_systems.gnorm` of the candidates |
| **hull base** | `hermite6_ext.norm_table(0, x1)`, `sup_S0_on(n, 0, x1)`, `C_upper`, `C_e0`, `C_o0`, `eta = x1` | rig hull norms, S0 and h1 sups |
| **local M5** | `local_r5.local_tower(base, cands, point_nodes, x1)` | same call |
| **transport** | exact `x1²/2`; the equality with protocol `probe_rules.transport` is checked when x1 is the preregistered one | same formula |
| **seal** | atomic write (tmp + fsync + rename) of `SCIENTIFIC_RECORD_SEALED.json` | same writer |

The production path also enforces the R1 production requirements:
- thread pinning before numpy;
- the Aux5 `manifest_v3` initial and final gates;
- the SciPy guard.

## 3. REAL_INPUT_ARITHMETIC_GUARD

- **Policy file.** `config/REAL_INPUT_GUARD.json` holds `{"policy": "DENY"}` and is pinned in the qualification
  evidence.
- **The only recognized policy is `DENY`.** Any other value, or a missing or unreadable file, is also a denial.
- **Where it is checked.** `executor_core.execute` checks it before calling any backend method whenever
  `backend.real_input is True`. `CusumPointBackend.prepare_point` checks it again, independently.
- **Future activation** needs a successor that adds an externally authorized path and gets it independently reviewed.
  This executor cannot run real arithmetic.

**Input adapters.**
- **`RealInputAdapter`** (metadata only) validates the frozen K1 cell-0 record with R1 `k1_inputs.validate`
  (V01–V10). It emits only identities, geometry and `C_upper`; every other record field is redacted.
- **`ManufacturedInputAdapter`** emits the same binding schema for manufactured fixtures, with fixture identities.

**Real-stage smoke (qualification only), `SyntheticCusumSmokeBackend`.**
- **What runs.** The R3 `SyntheticGradedCert` (real Arb kernels, synthetic parity-pure candidates that are NOT
  approximations of any DAG object, no collocation) at the degenerate cell {0} runs `prepare`, `residuals`, graded
  inputs, candidate graded sups and hull base.
- **Where it stops.** It stops before `certify_graded`, so no `R'''` or `R⁽⁵⁾` enclosure is formed.
- **What it checks.** Schema checks, float-quadrature residual containment at e = 0, and the cost of the real Arb
  stages.

## 4. Refusals (`ExecutorRefusal`, fail closed)

- **Binding and identity:** unbound input; producer, protocol or runtime hash mismatch; malformed K1 binding schema;
  wrong m set; wrong point; wrong cell endpoint.
- **Precision and output:** unsupported precision; non-empty output directory; an existing sealed record or address
  in the output directory.
- **Real arithmetic:** real backend under a DENY guard.
- **Certificate chain:** incomplete (missing constant, node, anchor or m).
- **Precision probe:** the observed working precision differs from 256.

## 5. Qualification (all manufactured or synthetic)

**Manufactured fixtures** (exact truth from the Taylor recurrence, independently confirmed by acb Cauchy integrals):
1. positive L1;
2. inconclusive transport;
3. negative U1;
4. point-negative U0;
5. tight M5;
6. loose valid M5;
7. parity-pure;
8. parity contamination;
9. near-zero boundary;
10. malformed certificate (refused);
11. wrong K1 identity (refused);
12. wrong m identity (refused).

**Gate groups:**
- truth containment (`I0 ∋ R'''(0)`, `L1 ≤ min R'''`, `U1 ≥ max R'''` on 17 grid points, `M5 ≥ max|R⁽⁵⁾|`);
- expected verdict class per fixture (frozen from DEV);
- qualification/science separation (PASS with SUPPORTS, INCONCLUSIVE and CONTRADICTS);
- sign invariance of the qualification gates;
- mutations E01–E16;
- inherited R4 gates (local R⁽⁵⁾ soundness, R⁽⁵⁾ and local mutations, M5 cross-check, certificate replay, fail-closed);
- deterministic replay in two fresh processes (zero scientific-leaf differences);
- real-stage smoke;
- guard DENY with a tripwire backend;
- cost projection against the frozen ceilings (soft 9000, hard 10800, wall 14400, campaign 32400 CPU-s);
- runtime identity.

## 6. External authorization

The authorization object (`config/EXTERNAL_AUTHORIZATION_TEMPLATE.json`, inactive) binds:
- science preregistration commit and hash;
- executor freeze commit and identity hash;
- executor qualification result hash;
- K1 input manifest hash;
- cell, m set, precision and CPU ceiling;
- host runtime identity;
- output namespace and slot;
- a nonce;
- a result-blindness statement.

It is prepared for countersigning by an independent reviewer. It is not activated, and it is not a cryptographic
anchor (see `TRUST_MODEL.md`).
