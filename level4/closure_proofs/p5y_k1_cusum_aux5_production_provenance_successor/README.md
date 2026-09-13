# P5Y K1 CUSUM Aux5: production-provenance successor checkpoint

This namespace is the additive successor to the CUSUM Aux5 production checkpoint (`p5y_k1_cusum_aux5_production_checkpoint`, sha `4026f296…`). That checkpoint was **BLOCKED** by independent countersignature on record-level production-authority semantics. It is preserved unmodified and fenced on the host.

```text
PREDECESSOR_CHECKPOINT     = BLOCKED_ON_PRODUCTION_STATUS_SEMANTICS
SCIENTIFIC_PRODUCER        = UNCHANGED_AUX5
NEW_SCIENTIFIC_COMPUTE     = NONE
PRODUCTION_AUTHORITY_LAYER = COMPOSITE_PROVENANCE
```

**Nothing is launched.** Production also cannot become launchable from this namespace alone: it requires an independent countersignature (`config/COUNTERSIGNATURE.json`) that only the reviewer creates.

## Documents

| File | Content |
|---|---|
| `GOVERNANCE_AUDIT.md` | The authoritative production rule, re-derived from frozen sources (K1 checkpoint, PS1, SR-authorized, Lane C, K4); why the internal false flags do not decide the disposition |
| `PS1_PRECEDENT_MAPPING.md` | Field-by-field mapping against PS1 (sealed record, `production_provenance`, launch authorization, Lane C): no missing mandatory field |
| `DOWNSTREAM_CONSUMER_AUDIT.md` | Every consumer that could admit a CUSUM record, and the pair requirement for each |
| `REVIEW_PACKET.md` | The packet for the second independent countersignature |
| `RESULT.md` | Freeze, acceptance and readiness record |

## The production-authority layer

1. **Run authorization** (`config/RUN_AUTHORIZATION.json` + `_HASH`), committed before any result.
   - It binds the checkpoint, producer, runtime argv, host, the exact 326-cell universe and far-field obligation, the cap, the run id and ledger id, the envelope schema and the executor sources.
   - Its `result_bearing: false` is a property of the authorization object, exactly as in PS1.
2. **Independent countersignature.** It binds the authorization sha256 and the freeze record. No ledger genesis, and therefore no result, can exist without it.
3. **Authorized ledger.** The genesis state and journal entry 0 carry the authorization block, and a ledger without that block is never adopted.
4. **Seal.** The predecessor seal semantics are reused unchanged.
5. **Provenance envelope** (`provenance/<attempt>/CUSUM_<cell>.envelope.json`).
   - It is derived entirely from the sealed record bytes, the ledger's RESERVED → RUNNING → SEAL journal entries, the authorization and the frozen specification.
   - It is written read-only and verified as a pair, then bound once by a `PROVENANCE_BOUND` transition.
6. **Integrity audit** (`prov_integrity.audit`) is the only admission path to K1 adjudication and K4. A cell counts only as a verified (record, envelope) pair.

**Production result = scientific record + valid production provenance envelope. Neither alone is disposition-bearing.**

## Code

**Reused unchanged:** all predecessor modules (ledger, supervisor, keeper, sealer, spec, cells), imported by path and hash-bound in the checkpoint.

**New in this namespace:**

| Module | Role |
|---|---|
| `code/prov_schema.py` | Schema ids and the normative rule texts |
| `code/prov_authorization.py` | Run authorization and countersignature verification; synthetic countersignatures only |
| `code/prov_envelope.py` | `build_envelope`, `verify_pair`, `check_genesis`, ledger linkage |
| `code/prov_ledger.py` | `ProvenanceLedger` (authorized genesis), `bind_envelope`, `op_bind_provenance` |
| `code/prov_supervisor.py` | The predecessor supervisor plus authorization gate and envelope binding |
| `code/prov_integrity.py` | Pair-verifying audit, pair export, K4 attestation and its recomputation |
| `code/prov_entry.py` | Preflight P01–P10, launch (never run), status, settle, audit, export, attest |
| `code/make_provenance_checkpoint.py` | Envelope schema, checkpoint and authorization builder |
| `tests/prov_acceptance.py`, `tests/prov_synthetic_worker.py` | Synthetic adversarial acceptance |
