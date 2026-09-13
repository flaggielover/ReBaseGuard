# Governance root-cause audit: what makes a CUSUM artifact production

**Scope.** This audit re-derives the project's production semantics from frozen historical sources only. It does not rely on the rejected interpretation in the predecessor checkpoint (`p5y_k1_cusum_aux5_production_checkpoint`, sha `4026f296…`), which held that "production status is conferred by the sealed ledger entry alone".

**Trigger.** The independent countersignature, relayed by the user on 2026-09-13, returned **BLOCKED** for CUSUM production, solely on record-level production-authority semantics.

## 1. Frozen sources and what each one establishes

| # | Frozen source | What it establishes |
|---|---|---|
| S1 | `p5y_k1_cover_ledger_successor/CHECKPOINT.md` (K1 checkpoint) | "An explicit **separate** production authorization is then necessary; it must **not flip the guard** inside this frozen checkpoint." `config/checkpoint.json` holds `production_enabled: false` and `no_production_authorization_from_this_checkpoint: true`. |
| S2 | Every K1 CUSUM certifier since repair1 (`repair_qualify.py`, `successor_qualify.py`, `qualify4.py`, `qualify5.py`) | Each raises if `spec.PRODUCTION_ENABLED` is true. The certifier guard is permanently closed, so authority can never come from inside the certifier. |
| S3 | `p5y_k1_sr_production_authorized_successor/README.md` and `driver/production_provenance.py` | A genuine record and a synthetic stand-in are structurally identical. What makes a record genuine is an **additive `production_provenance` block** with four layers: TEMPORAL (bound to the live production authorization, which did not exist when the synthetic records were made), CHECKPOINT, KIND (`SCIENCE`, `synthetic: false`) and BINDING (a canonical digest over the whole tuple). |
| S4 | `p5y_k1_ps1_production/config/LAUNCH_AUTHORIZATION.json` (+ `_HASH`) and `make_authorization.py` | A hash-bound run authorization that binds the producer commit, checkpoint, cell table, protocol, shard manifest, executor sources (`scientific_adapter_hash`), host, runtime and cap. The authorization object itself carries **`result_bearing: false`**, and the launcher refuses one that does not (`auth.get("result_bearing") is not False`). |
| S5 | `p5y_k1_ps1_production/driver/ps1_cellseq_launcher.py`: `_verified`, `_seal_one`, `production_preflight` | The **science artifacts** (T3/T4/T5 evidence files) carry **no** production or result-bearing field. A **sealed production cell record** (`production/cells/NNNN.json`) references them by sha256 in `evidence` and carries `production_provenance` (PP.seal + PP.verify). The preflight requires the authorized producer commit to be an ancestor of HEAD, with no executor change since. |
| S6 | `p5y_k1_ps1_production/production/README.md` and `config/protocol.json` `provenance_firewall` | `production/` is "the **only** place a genuine, result-bearing PS1 SR production record may be written". Genuine cells at protocol freeze: 0. Pre-result is proven against the pre-result git tag. `protocol.json` also declares `result_bearing: false` of itself. |
| S7 | `p5y_k1_ps1_production/driver/global_budget.py` `commit` | A cell is committed to the production ledger (`completed_cells[cell] = sealed record`) only after sealing. |
| S8 | `p5y_k1_ps1_postk1_adjudication_tooling/code/ps1_adjudication_audit.py` (Lane C) | Before adjudication it requires: sealed file == ledger entry (canonical), evidence sha256 re-verified, scientific hash recomputed, complete domain, no open reservations, and continuity chains valid → `INTEGRITY_READY_FOR_ADJUDICATION`. |
| S9 | `p5y_k2k5_postk1_audit/config/K4_ASSEMBLY_CHECKPOINT.json` `integrity` | SR K4 inputs are admitted **only via sealed PS1 production cell records** plus the Lane C audit. CUSUM inputs are admitted via an integrity attestation bound to the frozen CUSUM successor checkpoint. |
| S10 | `p5y_k2k5_postk1_audit/K4_K5_ADMISSIBILITY.md` | "Disposition-bearing" is about the governed record set entering adjudication. It is never an inline flag. |

## 2. Derived rule

The three properties are defined by governed objects outside the science artifact, in this order:

- **Production-authorized:** the artifact was produced under a hash-bound **run authorization** committed before any result (S1, S4, S5, S6).
- **Result-bearing:** in addition, the artifact is **sealed** in that authorization's production namespace and ledger, with a **provenance object** that binds the artifact bytes to the authorization, checkpoint, producer, cell and run (S3, S5, S6, S7).
- **Disposition-bearing:** in addition, the **integrity audit** admits the sealed set for adjudication (S8, S9, S10).

No inline boolean inside the scientific artifact is part of any of these definitions. In PS1 the science artifacts have no such field at all, and the only `result_bearing` booleans that exist sit on governance objects (authorization, protocol) and read `false` about those objects themselves.

The requirement is therefore **C combined with B**: a sealed ledger entry, plus a provenance/authorization object bound to the record. It is **not A** (literal booleans inside the scientific record).

```text
AUTHORITATIVE_PRODUCTION_AUTHORITY =
  pre-result hash-bound run authorization (separate from, and never flipping, the frozen K1/certifier guard)
  -> governed production ledger of that authorization
  -> sealed record + production provenance object binding {record bytes/scientific hash, authorization, checkpoint,
     producer, cell, run, kind, binding digest}
  -> integrity audit admission before adjudication

INLINE_RESULT_BEARING_FLAG_REQUIRED       = NO
EXTERNAL_HASH_BOUND_PROVENANCE_ALLOWED    = YES   (PS1 science artifacts are external files bound by sha256 from the
                                                   sealed provenance-carrying record)
```

## 3. Root cause of the BLOCKED verdict

Measured against the rule, the predecessor checkpoint was missing four objects:

1. **No pre-result run authorization object.** There was no LAUNCH_AUTHORIZATION analogue. The checkpoint freeze stood in for it, but it was not a separate, hash-bound authorization of a run.
2. **No per-record provenance object.** The ledger seal bound record bytes, but nothing that travels with the record bound it to an authorization, run and ledger. A sealed Aux5 record, whose own fields read `production_run=false` and `result_bearing=false`, was indistinguishable from a qualification record except by where it was stored.
3. **Raw records reached a consumer.** The predecessor `export` put raw records alone into `k4_records/`, and its attestation derived production status from the ledger alone.
4. **The authority layer was self-activating.** The authoring session could launch with nothing independent in between.

Items 1–3 are exactly what PS1 has and the predecessor lacked, and they are why the internal `false` fields could be read as the record's own disposition.

## 4. Why the internal false flags do not invalidate the composite artifact

- **They are certifier constants.** They are part of the frozen Aux5 scientific bytes, inside the scientific hash, and identical in qualification and production. Rewriting them would change the qualified producer identity and break the determinism qualification.
- **What they literally assert is true.** A scientific record by itself is not a production result, and the composite rule says the same.
- **They are the certifier-side image of guard S2.** The K1 checkpoint (S1) forbids flipping that guard and requires authority to come from a separate authorization. So a record that emitted `production_run=true` would itself contradict the frozen governance.
- **PS1 is the direct precedent.** Its governance objects state `result_bearing: false` of themselves, its science artifacts carry no production field, and production status lives entirely in the sealed provenance-bearing record.

The composite production artifact is **(scientific record, valid provenance envelope)**. The disposition is a property of the pair; no object inside it carries it.
