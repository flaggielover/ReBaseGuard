# Disposition of pre-freeze review r3 (verdict PASS_WITH_NOTES; no BLOCKING finding)

The three load-bearing notes are resolved before the freeze; the resolution is demonstrated by the partial dress
rehearsal recorded in `evidence/dev/QUALIFICATION_REHEARSAL_R3.json` (the changed gates S00–S05, S07, S08 incl. the
extended lifecycle simulation; S06 is unaffected by the r3 changes and passed in the full rehearsal).

| id | disposition |
|---|---|
| N-R3-1 (load-bearing) | `tc_run.py` now runs `preflight` BEFORE any write: it refuses an evidence directory inside the checkout or already existing, a runtime (interpreter prefix, python/numpy/scipy/flint versions, host) different from the protocol, a K1 record whose sha differs from the pre-registered one, and runs the producer gate `require_authorized` for all 34 addresses without computing. On refusal it prints PREFLIGHT REFUSED and exits 2 with no directory, no ledger, no producer invocation. The protocol's `stopping_rule` states that a preflight refusal is not a run, and `governance_schema` fixes the exact AUTHORIZATION / GUARD schema, commit order, fast-forward-only full clones and LF line endings. S08(l) exercises the preflight positively after the ALLOW commit and negatively with the evidence directory inside the checkout. `tc_run` pins the thread environment like the producer. |
| N-R3-2 (load-bearing) | `checkpoint.py` writes under `evidence/tc_r1/checkpoints/` once `config/TC_PROTOCOL.json` exists. CP_000–CP_002 are committed before the freeze. |
| N-R3-3 | `tc_consume.py` refuses an `--out` inside the checkout; both consumption runs write outside and the verified output is copied in and committed afterwards. |
| N-R3-4 | The consumer now requires exactly one START and exactly one ok OUTPUT per address (index sha), exactly one RUN_START and one RUN_END (identical reproduction, `index_sha256` = sha of TC_INDEX), no RUN_VOID/CAP_STOP, one run head shared by every record binding, TC_INDEX and every ledger line, the record schema and the recorded runtime equal to the protocol's; it re-checks QUALIFICATION → AUTHORIZATION commit order and the GUARD's addresses and protocol sha at the run head. |
| N-R3-5 (load-bearing) | The pre-freeze commit contains `tc_prefreeze.py`, `ADJUDICATION_BRIEF.md`, `REVIEW_R3.md`, this disposition, CP_002 and `evidence/dev/README.md`; `make_tc_protocol.py` pins all review documents, `checkpoint.py` and the dev README. The authorization brief item 4 covers r3 and asks for explicit acceptance of the residual risks. The protocol is generated from a clean checkout of exactly the published pre-freeze commit; the freeze commit adds only the protocol and `PREFREEZE_REFUSAL.json`. |
| N-R3-6 | `tc_producer.committed_json` compares bytes with bytes. |
| N-R3-7 | Protocol cap raised from 24 to 30 CPU-h (CAP_STOP then binds at ≈ 3000 CPU-s per cell, 1.9× the forecast); worst case A + B = 30 + ≈ 3.6 < 40. Not measured with 4 concurrent processes; the residual risk is put to the authorization review. |
| N-R3-8 | Informational; accepted residual risk (put to the authorization review). |
| N-R3-9 | Runbook: fast-forward only, full clones (protocol `governance_schema.order`). |
| N-R3-10 | Checked read-only on vultr-02: `apt-daily-upgrade.timer` next fires 2026-09-20 06:41 UTC, `apt-daily.timer` (list refresh only) at 02:02 UTC. The run starts right after the preflight; forecast wall ≈ 4 h. No system setting is changed. |
| N-R3-11 | `evidence/dev/README.md` annotates every dev artifact (superseded draft; rehearsal = de94e8b3 code + dev protocol 30922c24, never published). |
