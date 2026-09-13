# CUSUM Aux5 production-provenance successor: result

**Classification: governance only.** No production cell was launched, no result-bearing compute ran, and the frozen Aux5 certifier was not started. The scientific producer, its record bytes and the scientific-hash definition are unchanged.

## Trigger and predecessor

The predecessor checkpoint `4026f296…` (namespace `p5y_k1_cusum_aux5_production_checkpoint`, freeze `532c880e`, readiness record `264e9d37`) was **BLOCKED** by independent countersignature. The block rests solely on record-level production-authority semantics.

- It is preserved unmodified.
- It is **fenced** on rebaseguard-vultr-02: `/root/work/postk1-runs/cusum-aux5-production` holds `DRAIN` plus a `BLOCKED_ON_PRODUCTION_STATUS_SEMANTICS` marker and no ledger, so its preflight is NOT_READY (C13).

## Governance findings

| Question | Answer | Where |
|---|---|---|
| Authoritative rule | Pre-result hash-bound run authorization (never flipping the frozen K1/certifier guard) → that authorization's production ledger → sealed record + hash-bound provenance object → integrity-audit admission | `GOVERNANCE_AUDIT.md` |
| Inline result-bearing flag required? | NO | PS1 science artifacts carry none; `result_bearing: false` appears only on governance objects, about themselves |
| External hash-bound provenance allowed? | YES | The PS1 sealed record binds its external T3/T4/T5 artifacts by sha256 |
| PS1 equivalence | PASS: no missing mandatory field | `PS1_PROVENANCE_EQUIVALENCE` in `PS1_PRECEDENT_MAPPING.md` |
| Downstream consumers | Every code path that can admit CUSUM Aux5 production requires a verified pair. Residuals: frozen K4 code trusts its attestation file (the adjudicator recomputes it), and the stale closure template names Aux4. | `DOWNSTREAM_CONSUMER_AUDIT.md` |

## Frozen objects

| Object | sha256 / id |
|---|---|
| `config/PROVENANCE_CHECKPOINT.json` | `dd4c89d773c411355d93d0d703e40c027f9913e11e116e4bfe35117f84b4baf2` (52 bound sources, including every predecessor module and frozen input) |
| `config/RUN_AUTHORIZATION.json` | `b8f11ec05efc2476f733dd989ae02b542dc9efa374f24fa0a27688d76ec2b329`; authorization commit `9719cba2`; `CUSUM-AUX5-PROD-AUTH-001`, run `CUSUM-AUX5-PROD-R1`, ledger id `61eb8565…` |
| `config/ENVELOPE_SCHEMA.json` | `decda981cb1b31ecbe461b4620c8a624b6fde89f92c7b2bfd2aa143629ded197` |
| `evidence/acceptance_r1/ACCEPTANCE_RESULT.json` | `e7139f2cc3d3924f7bc99576a5b8f210f669f5450821cb9d39a26e81a1ba1fb8` |
| `config/FREEZE_RECORD.json` (freeze commit `292e432e`) | `e61dcc15f8f6ab89752596109782d9108e8d25962271e3858b6c8b8a7af31ec1`. An independent countersignature must bind this value. |

The checkpoint's required statements:

```text
PREDECESSOR_CHECKPOINT     = BLOCKED_ON_PRODUCTION_STATUS_SEMANTICS
SCIENTIFIC_PRODUCER        = UNCHANGED_AUX5
NEW_SCIENTIFIC_COMPUTE     = NONE
PRODUCTION_AUTHORITY_LAYER = COMPOSITE_PROVENANCE: pre-result run authorization + independent countersignature
                             -> authorization-bound ledger genesis -> sealed attempt -> hash-bound production
                             provenance envelope (PROVENANCE_BOUND) -> pair-verifying integrity audit
```

## Synthetic adversarial acceptance

**Run:** rebaseguard-vultr-02, clean checkout `9719cba2`, 2026-09-13 10:22:40Z–10:24:03Z. **Result: 19/19 PASS.**

- The frozen certifier was never started.
- Both production runtime roots were untouched.
- No production countersignature exists.
- The checkpoint was unchanged during the run.
- Per-test refusals and coverage are in `REVIEW_PACKET.md` §5 and the result JSON.

## Entrypoint after the freeze

`prov_entry.py preflight` on the clean checkout `292e432e` (`evidence/preflight_postfreeze_r1/PREFLIGHT_POSTFREEZE.txt`) passes P01–P06 and P08–P10. It fails only:

```text
FAIL  P07_independent_countersignature   [COUNTERSIGNATURE_MISSING]
CUSUM_AUX5_PROVENANCE_ENTRYPOINT = NOT_READY   (fail closed)
```

This is the intended state: production is not self-authorized.

## Final report

```text
AUTHORITATIVE_PRODUCTION_AUTHORITY      = pre-result hash-bound run authorization (separate from the never-flipped K1/
                                          certifier guard) -> authorization-bound production ledger -> sealed record +
                                          hash-bound production provenance object -> integrity-audit admission;
                                          production result = (scientific record, valid provenance envelope)
INLINE_RESULT_BEARING_FLAG_REQUIRED     = NO
EXTERNAL_HASH_BOUND_PROVENANCE_ALLOWED  = YES
PS1_PROVENANCE_EQUIVALENCE              = PASS
AUX5_SCIENTIFIC_PRODUCER_CHANGED        = NO
NEW_RESULT_BEARING_COMPUTE              = NONE
PROVENANCE_SUCCESSOR_CHECKPOINT         = PASS
READY_FOR_INDEPENDENT_COUNTERSIGNATURE  = YES
CUSUM_PRODUCTION_LAUNCHED               = NO
LIVE_AWS_PS1_TOUCHED                    = NO
ORIGIN_MAIN                             = UNCHANGED
```

`CUSUM_READY_TO_LAUNCH_PRODUCTION` stays **NO** until the reviewer commits `config/COUNTERSIGNATURE.json` and preflight prints READY.

## Disclosures

1. **Host fence.** A fence directory was created on rebaseguard-vultr-02 at the predecessor runtime root. It holds only marker files, no ledger, and nothing was launched.
2. **Scratch runs.** Synthetic acceptance scratch (`/root/work/postk1-runs/aux5-provenance-acceptance-r1`) remains on Vultr outside the repository.
3. **Single-session authorship.** The rule derivation, design, tests and packet were written by one agent session; a second independent countersignature is required.
4. **Not touched.** The live AWS PS1/SR campaign, K2–K5 artifacts, the predecessor namespace files and origin/main.
