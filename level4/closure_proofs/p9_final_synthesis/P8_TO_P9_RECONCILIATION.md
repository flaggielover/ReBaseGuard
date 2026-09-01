# P8 → P9 reconciliation

**Authoritative P8 verdict: `P8 = FAIL`** (16 PASS / 5 FAIL).
Source: `level4/closure_proofs/p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md`.

Claude's P8 discovery had reported `PARTIAL_CANDIDATE`. **It did not survive.**
P9 used it as a premise nowhere, so no P9 conclusion changes.

---

## 1. What changed, and why the candidate verdict was wrong

The four scientific failures Claude reported (`G4`, `G4-D`, `G4-F`, `G7`) were
confirmed. A **fifth** was found:

> **`G14` fails** — the temporal-integrity gate. Under the frozen verdict rule,
> any integrity-spine failure requires `FAIL`, so `PARTIAL_CANDIDATE` was never
> available.

`PREREGISTRATION_TEMPORAL_ANCHOR = PARTIAL`. Filesystem birth times suggest
theory/protocol/gates preceded production, but the directory was untracked with
no pre-result commit and no externally anchored digest; the provenance record
does not hash `THEORY.md`, `EXPERIMENT_PROTOCOL.md` or `CLOSURE_GATES.md`; and
`config.py` was modified *after* the production artifacts. There is also a
direct frozen-protocol mismatch: the protocol states E2 used 250,000 and
2,048,000 cycles, while the executable and results use 163,840 and 1,024,000.
Amendment `A2` was classified `RESULT_DRIVEN` — it reused an
already-inspected verification address after tuning, and disclosure does not
restore holdout independence.

**This is the single most instructive fact for P9.** P8 did not fail on its
science; it failed on whether its preregistration could be independently
anchored. P9 anticipated exactly this class of defect — `EXPERIMENT_PROTOCOL.md`
§0 discloses that P9's own gates were written **after** its reproductions ran,
and for that reason `CLOSURE_GATES.md` contains **no** post-hoc numerical
threshold, only properties an adjudicator can verify by inspection. That choice
was made before this verdict was known and is now validated by it.

## 2. Preregistered rule, applied

`P8_DEPENDENCY_GATE.md` §4 fixed the rule before the outcome was known:

> `FAIL`: quarantine P8 entirely from P9 premises. It may still appear in
> `LIMITATIONS.md` and `DISCREPANCY_REGISTER.md` as history and as a negative
> result.

Applied literally. Note that the authoritative adjudication's §16 is *more
permissive* than P9's own rule — it explicitly allows P9 to use four tiers. P9
**declines the permission** (§4 below) and keeps the stricter rule it committed
to in advance.

## 3. Row-by-row promotion

Every `PROVISIONAL_P8_PENDING_CODEX` row was replaced. The new rows transcribe
the authoritative §16 table verbatim rather than paraphrasing Claude's
discovery.

| provisional row (withdrawn) | replaced by | authoritative tier |
|---|---|---|
| `P8-P1` phenomenon survives across model classes | `P8-S3` | `EMPIRICAL_ONLY`, measured matrix only, failed-campaign evidence set |
| `P8-P2` reuse damage −38% to −51% | `P8-S3` | as above |
| `P8-P3` magnitude non-universal; window law rejected | `P8-S4` | `NEGATIVE_RESULT` |
| `P8-P4` P8-T1 conditional; transfer not established; G7 failed | `P8-S2` + `P8-S4` + `P8-S5` | `CONDITIONAL_THEOREM` / `NEGATIVE_RESULT` / `NOT_ESTABLISHED` |
| `P8-P5` P4-vs-Stage-D gap is definitional; 11.7× overstatement | **withdrawn — not carried** | not listed in §16; P9 does not carry it |

New rows: `P8-V` (the `FAIL` verdict itself), `P8-S1`
(`EXACT_THEOREM`: P8-L0/L1 algebra, P8-T2 reset decomposition, exact
convention-A/B truncation decomposition).

**`P8` created no `CERTIFIED_NUMERICAL` result.** The scope map's certified row
is unchanged.

`P8-P5` deserves a note: Claude's discovery claimed the published factor-3.35
P4-vs-Stage-D gap is "entirely definitional". §16 does not list it among
surviving premises, so P9 **withdraws it** and `DEFINITION_CROSSWALK.md` X-09
stays `UNRESOLVED`. This is the one place where a P9 artifact would have been
narrowed had the candidate verdict stood.

## 4. What P9 uses from P8: **nothing**

§16 permits P9 to use `P8-S1`–`P8-S4`. P9 uses **none of them as a premise**,
for three reasons:

1. P9's preregistered `FAIL` rule (§2) is stricter and was fixed in advance.
2. Nothing in P9 needs them. The quarantine was designed so that reconciliation
   could only *add* scope or *add* limitations, never retract a finding — and
   that is what happened.
3. Citing surviving evidence from a campaign that failed its integrity spine
   would risk exactly the representation §16 forbids.

Enforced mechanically: `tests/test_p8_quarantine.py` asserts that **no P8 node
has any outgoing edge** and that no P8 row retains a provisional status. The
rows are carried so the boundary is documented for future work, marked
`PERMITTED_BY_P8_BOUNDARY_BUT_NOT_USED_BY_P9`.

## 5. Prohibitions P9 inherits and honours

§16 forbids P9 to use the rejected window law, assume detector transfer, assume
P7-boundary transfer, or describe P8 as a successful preregistered closure
campaign.

| prohibition | where P9 complies |
|---|---|
| no rejected window law | `P8-S4` is `NEGATIVE_RESULT` with no outgoing edge |
| no detector transfer | `MODEL_SCOPE_MAP.md` §2 marks every third-detector cell `UNKNOWN`; `P3-N2` remains "not a detector-universal theorem" |
| no P7-boundary transfer | `P9-T2` is proved for the two frozen Gaussian detectors **only**, and says so |
| not a successful campaign | `P8-V` is `NEGATIVE_RESULT`; `RESULTS.md` and `README.md` state `P8 = FAIL` |

## 6. Effect on P9 artifacts

| artifact | change |
|---|---|
| `CLAIM_LEDGER.{md,json}` | 5 provisional rows → 6 authoritative rows; **65 claims, 64 edges, 0 validation findings** |
| `THEOREM_DEPENDENCY_GRAPH.{md,json}` | 6 edges removed (P8 nodes now have no parents and no children) |
| `DEFINITION_CROSSWALK.md` X-09 | stays `UNRESOLVED` — `P8-P5` withdrawn |
| `DISCREPANCY_REGISTER.md` `D-14` | `OPEN` → **`GENUINE_MODEL_DIFFERENCE`**: detector transfer is now *measured absent*, not merely unestablished |
| `MODEL_SCOPE_MAP.md` | non-Gaussian cells **stay `UNKNOWN`** — a failed campaign fills no cell |
| `THEORY.md`, `RESULTS.md` §5–§7 | **unchanged**; `P9-T1`/`P9-T2`/`P9-N1` never had a P8 premise |
| `CROSS_PRIORITY_REPRODUCTION.md` | **unchanged**; no anchor was re-run, none had P8 input |
| `CLOSURE_GATES.md` `G14` | **BLOCKED → PASS** |

**No P9 focused check was re-run except those touching the ledger**, per prompt
§22.7.

## 7. The other status change in the same pass

The authoritative status table was also updated to `P6 = CLOSED` and the root
`README.md` staleness (`D-08`) was fixed — it now carries P6 and P8 rows.

P9 had flagged `P6 = CLOSED` as conflicting with repository authority
(`D-10`, `P9_DEFINITION_AUDIT.md` §6 `C1`), because the last record *in the P6
namespace* reads `FINAL_P6_VERDICT = PARTIAL` and P6R2b says verbatim
"`P6 = CLOSED` is **not** declared here." The repository has now spoken through
its designated status table, and P9 follows it: **P6 = `CLOSED`**, scope-bound.

P9 records, without disputing the status, that no independent Gate-9 review is
recorded *inside* the P6 namespace, so a reader tracing P6's closure through
`p6r2b_gate9_crn_identity/` alone will not find it. `P6-NOV` remains
`NOT_ESTABLISHED`: closure is not novelty.
